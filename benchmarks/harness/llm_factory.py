#!/usr/bin/env python3
"""LLM Factory: Create and manage real LLM API clients.

Provides:
- Factory pattern for creating LLM clients
- Unified interface across all providers
- Real API calls (not simulated)
- Token counting and cost tracking
- Error handling and retries
"""

import json
import os
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

from model_registry import ModelRegistry, Provider, ModelInfo


@dataclass
class LLMResponse:
    """Response from an LLM API call."""

    text: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    execution_time_ms: float
    cost_usd: float
    timestamp: datetime


class LLMClient(ABC):
    """Abstract base class for LLM API clients."""

    def __init__(self, model_info: ModelInfo):
        """Initialize client with model info."""
        self.model_info = model_info
        self.model_name = model_info.name
        self.provider = model_info.provider
        self._api_key: Optional[str] = None
        self._call_count = 0
        self._total_tokens = 0
        self._total_cost = 0.0

    @abstractmethod
    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate response from LLM."""
        pass

    @abstractmethod
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text (provider-specific)."""
        pass

    @property
    def call_count(self) -> int:
        """Total API calls made."""
        return self._call_count

    @property
    def total_tokens(self) -> int:
        """Total tokens used across all calls."""
        return self._total_tokens

    @property
    def total_cost(self) -> float:
        """Total cost of all API calls in USD."""
        return self._total_cost

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "model": self.model_name,
            "provider": self.provider.value,
            "calls": self._call_count,
            "total_tokens": self._total_tokens,
            "total_cost_usd": round(self._total_cost, 4),
            "avg_tokens_per_call": (
                self._total_tokens // self._call_count if self._call_count > 0 else 0
            ),
        }


class OpenAIClient(LLMClient):
    """OpenAI GPT models (gpt-4, gpt-3.5-turbo, etc.)."""

    def __init__(self, model_info: ModelInfo):
        """Initialize OpenAI client."""
        super().__init__(model_info)

        try:
            import openai
        except ImportError:
            raise ImportError(
                "openai package required. Install with: pip install openai"
            )

        self._api_key = model_info.get_api_key()
        if not self._api_key:
            raise ValueError(f"OPENAI_API_KEY environment variable not set")

        self.client = openai.OpenAI(api_key=self._api_key)

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate response using OpenAI API."""
        if max_tokens is None:
            max_tokens = self.model_info.max_output_tokens

        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            text = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            execution_time_ms = (time.time() - start_time) * 1000

            # Calculate cost
            cost = ModelRegistry.get_cost_estimate(
                self.model_name,
                input_tokens,
                output_tokens,
            )
            if cost is None:
                cost = 0.0

            # Update stats
            self._call_count += 1
            self._total_tokens += input_tokens + output_tokens
            self._total_cost += cost

            return LLMResponse(
                text=text,
                model=self.model_name,
                provider=self.provider.value,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                execution_time_ms=execution_time_ms,
                cost_usd=cost,
                timestamp=datetime.now(),
            )

        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")

    def _count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken."""
        try:
            import tiktoken

            encoding = tiktoken.encoding_for_model(self.model_name)
            return len(encoding.encode(text))
        except ImportError:
            # Fallback: estimate tokens (4 chars ≈ 1 token)
            return max(1, len(text) // 4)


class AnthropicClient(LLMClient):
    """Anthropic Claude models."""

    def __init__(self, model_info: ModelInfo):
        """Initialize Anthropic client."""
        super().__init__(model_info)

        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package required. Install with: pip install anthropic"
            )

        self._api_key = model_info.get_api_key()
        if not self._api_key:
            raise ValueError(f"ANTHROPIC_API_KEY environment variable not set")

        self.client = anthropic.Anthropic(api_key=self._api_key)

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate response using Anthropic API."""
        if max_tokens is None:
            max_tokens = self.model_info.max_output_tokens

        start_time = time.time()

        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=temperature,
            )

            text = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            execution_time_ms = (time.time() - start_time) * 1000

            # Calculate cost
            cost = ModelRegistry.get_cost_estimate(
                self.model_name,
                input_tokens,
                output_tokens,
            )
            if cost is None:
                cost = 0.0

            # Update stats
            self._call_count += 1
            self._total_tokens += input_tokens + output_tokens
            self._total_cost += cost

            return LLMResponse(
                text=text,
                model=self.model_name,
                provider=self.provider.value,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                execution_time_ms=execution_time_ms,
                cost_usd=cost,
                timestamp=datetime.now(),
            )

        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}")

    def _count_tokens(self, text: str) -> int:
        """Count tokens for Anthropic models.

        Anthropic tokens are roughly similar to OpenAI (4 chars ≈ 1 token).
        """
        return max(1, len(text) // 4)


class GroqClient(LLMClient):
    """Groq fast inference models (Mixtral, Llama, etc.)."""

    def __init__(self, model_info: ModelInfo):
        """Initialize Groq client."""
        super().__init__(model_info)

        try:
            from groq import Groq
        except ImportError:
            raise ImportError("groq package required. Install with: pip install groq")

        self._api_key = model_info.get_api_key()
        if not self._api_key:
            raise ValueError(f"GROQ_API_KEY environment variable not set")

        self.client = Groq(api_key=self._api_key)

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate response using Groq API."""
        if max_tokens is None:
            max_tokens = self.model_info.max_output_tokens

        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            text = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            execution_time_ms = (time.time() - start_time) * 1000

            # Calculate cost
            cost = ModelRegistry.get_cost_estimate(
                self.model_name,
                input_tokens,
                output_tokens,
            )
            if cost is None:
                cost = 0.0

            # Update stats
            self._call_count += 1
            self._total_tokens += input_tokens + output_tokens
            self._total_cost += cost

            return LLMResponse(
                text=text,
                model=self.model_name,
                provider=self.provider.value,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                execution_time_ms=execution_time_ms,
                cost_usd=cost,
                timestamp=datetime.now(),
            )

        except Exception as e:
            raise RuntimeError(f"Groq API error: {e}")

    def _count_tokens(self, text: str) -> int:
        """Count tokens for Groq models."""
        return max(1, len(text) // 4)


class OllamaClient(LLMClient):
    """Local Ollama models (free, no API key)."""

    def __init__(self, model_info: ModelInfo, base_url: str = "http://localhost:11434"):
        """Initialize Ollama client."""
        super().__init__(model_info)
        self.base_url = base_url

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate response using local Ollama."""
        if max_tokens is None:
            max_tokens = self.model_info.max_output_tokens

        try:
            import requests
        except ImportError:
            raise ImportError(
                "requests package required. Install with: pip install requests"
            )

        start_time = time.time()

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
                timeout=120,  # Longer timeout for local inference
            )
            response.raise_for_status()

            data = response.json()
            text = data.get("response", "")

            # Ollama includes token counts in response
            input_tokens = data.get("prompt_eval_count", 0)
            output_tokens = data.get("eval_count", 0)

            # If not provided, estimate
            if input_tokens == 0:
                input_tokens = self._count_tokens(prompt)
            if output_tokens == 0:
                output_tokens = self._count_tokens(text)

            execution_time_ms = (time.time() - start_time) * 1000

            # Update stats (local = free)
            self._call_count += 1
            self._total_tokens += input_tokens + output_tokens

            return LLMResponse(
                text=text,
                model=self.model_name,
                provider=self.provider.value,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                execution_time_ms=execution_time_ms,
                cost_usd=0.0,  # Local = free
                timestamp=datetime.now(),
            )

        except Exception as e:
            raise RuntimeError(f"Ollama error (is it running on {self.base_url}?): {e}")

    def _count_tokens(self, text: str) -> int:
        """Estimate tokens for Ollama models."""
        return max(1, len(text) // 4)


class LlamaCppClient(LLMClient):
    """Local llama.cpp server via OpenAI-compatible API (no API key needed)."""

    def __init__(
        self, model_info: ModelInfo, base_url: str = "http://localhost:8080/v1"
    ):
        """Initialize LlamaCppClient.

        Args:
            model_info: Model metadata from the registry.
            base_url:   Base URL of the llama.cpp server (OpenAI-compatible /v1 endpoint).
        """
        super().__init__(model_info)
        self.base_url = base_url

        try:
            import openai  # noqa: F401 — validate import at construction time
        except ImportError:
            raise ImportError(
                "openai package required for LlamaCppClient. "
                "Install with: pip install openai"
            )

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate a response from the locally-running llama.cpp server.

        The server is OpenAI-API-compatible, so we use the openai client
        pointed at the local base URL.  The model name sent in the request
        is the short registry alias (e.g. 'qwen3-coder-next-8_0') — llama.cpp
        ignores the model field and serves whatever model is currently loaded.

        Args:
            prompt:      User-facing prompt text.
            temperature: Sampling temperature (0.0 = deterministic).
            max_tokens:  Maximum tokens to generate; defaults to model max.

        Returns:
            LLMResponse with token counts and timing.

        Raises:
            RuntimeError: If the llama.cpp server is unreachable or returns an error.
        """
        import openai

        if max_tokens is None:
            max_tokens = self.model_info.max_output_tokens

        start_time = time.time()

        try:
            client = openai.OpenAI(api_key="not-needed", base_url=self.base_url)
            response = client.chat.completions.create(
                model=self.model_name,  # Short alias — llama.cpp ignores it
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            text = response.choices[0].message.content
            input_tokens = (
                response.usage.prompt_tokens
                if response.usage
                else self._count_tokens(prompt)
            )
            output_tokens = (
                response.usage.completion_tokens
                if response.usage
                else self._count_tokens(text)
            )
            execution_time_ms = (time.time() - start_time) * 1000

            # Update running stats (local = free)
            self._call_count += 1
            self._total_tokens += input_tokens + output_tokens

            return LLMResponse(
                text=text,
                model=self.model_name,
                provider=self.provider.value,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                execution_time_ms=execution_time_ms,
                cost_usd=0.0,  # Local = free
                timestamp=datetime.now(),
            )

        except Exception as e:
            raise RuntimeError(
                f"LlamaCpp API error (is the server running at {self.base_url}?): {e}"
            )

    def _count_tokens(self, text: str) -> int:
        """Estimate token count (4 chars ≈ 1 token)."""
        return max(1, len(text) // 4)


class GoogleClient(LLMClient):
    """Google Gemini models via the OpenAI-compatible Generative Language API."""

    def __init__(
        self,
        model_info: ModelInfo,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/",
    ):
        """Initialize GoogleClient.

        Args:
            model_info: Model metadata from the registry.
            base_url:   Google's OpenAI-compatible endpoint base URL.
        """
        super().__init__(model_info)
        self.base_url = base_url

        self._api_key = model_info.get_api_key()
        if not self._api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable not set. "
                "Export it before running Google model benchmarks."
            )

        try:
            import openai  # noqa: F401
        except ImportError:
            raise ImportError(
                "openai package required for GoogleClient. "
                "Install with: pip install openai"
            )

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate a response from Google Gemini via the OpenAI-compatible endpoint.

        Args:
            prompt:      User-facing prompt text.
            temperature: Sampling temperature.
            max_tokens:  Maximum tokens to generate.

        Returns:
            LLMResponse with token counts, timing, and cost estimate.

        Raises:
            RuntimeError: If the Google API returns an error.
        """
        import openai

        if max_tokens is None:
            max_tokens = self.model_info.max_output_tokens

        # Re-read API key at call time in case env var was updated after init
        api_key = os.environ.get("GEMINI_API_KEY", self._api_key)

        start_time = time.time()

        try:
            client = openai.OpenAI(api_key=api_key, base_url=self.base_url)
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            text = response.choices[0].message.content
            input_tokens = (
                response.usage.prompt_tokens
                if response.usage
                else self._count_tokens(prompt)
            )
            output_tokens = (
                response.usage.completion_tokens
                if response.usage
                else self._count_tokens(text)
            )
            execution_time_ms = (time.time() - start_time) * 1000

            cost = ModelRegistry.get_cost_estimate(
                self.model_name, input_tokens, output_tokens
            )
            if cost is None:
                cost = 0.0

            self._call_count += 1
            self._total_tokens += input_tokens + output_tokens
            self._total_cost += cost

            return LLMResponse(
                text=text,
                model=self.model_name,
                provider=self.provider.value,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                execution_time_ms=execution_time_ms,
                cost_usd=cost,
                timestamp=datetime.now(),
            )

        except Exception as e:
            raise RuntimeError(f"Google API error: {e}")

    def _count_tokens(self, text: str) -> int:
        """Estimate token count (4 chars ≈ 1 token)."""
        return max(1, len(text) // 4)


class LLMFactory:
    """Factory for creating LLM clients."""

    @classmethod
    def get_provider_base_url(cls, provider_name: str, default: str) -> str:
        """Look up the baseURL for a provider from openconfig.json.

        Reads ``provider.<provider_name>.options.baseURL`` from the config file.
        Falls back to *default* if the provider or key is absent.  No
        environment-variable substitution is performed on URL values — only
        API key strings use the ``{env:…}`` pattern.

        Args:
            provider_name: Provider key as in openconfig.json (e.g. 'llamacpp').
            default:       Fallback URL returned when config entry is missing.

        Returns:
            The configured baseURL string, or *default*.
        """
        provider_cfg = ModelRegistry.get_provider_config(provider_name)

        # Guard: empty provider config → use default
        if not provider_cfg:
            return default

        options = provider_cfg.get("options", {})
        base_url = options.get("baseURL", "")

        # Guard: missing or empty URL → use default
        if not base_url:
            return default

        return base_url

    @staticmethod
    def create(model_name: str) -> LLMClient:
        """Create an LLM client for the specified model.

        Args:
            model_name: Name of the model (e.g., 'gpt-4', 'claude-3-opus')

        Returns:
            Initialized LLMClient instance

        Raises:
            ValueError: If model is unknown or not configured
            ImportError: If required package is not installed
        """
        # Early exit: validate model exists
        model_info = ModelRegistry.get_model(model_name)
        if model_info is None:
            available = ", ".join(sorted(ModelRegistry.MODELS.keys()))
            raise ValueError(f"Unknown model '{model_name}'. Available: {available}")

        # Early exit: validate API key is configured
        is_valid, error = ModelRegistry.validate_model(model_name)
        if not is_valid:
            raise ValueError(error)

        # Dispatch to appropriate client by provider
        if model_info.provider == Provider.OPENAI:
            return OpenAIClient(model_info)
        elif model_info.provider == Provider.ANTHROPIC:
            return AnthropicClient(model_info)
        elif model_info.provider == Provider.GROQ:
            return GroqClient(model_info)
        elif model_info.provider == Provider.OLLAMA:
            base_url = LLMFactory.get_provider_base_url(
                "ollama", "http://localhost:11434"
            )
            return OllamaClient(model_info, base_url=base_url)
        elif model_info.provider == Provider.LLAMACPP:
            base_url = LLMFactory.get_provider_base_url(
                "llamacpp", "http://localhost:8080/v1"
            )
            return LlamaCppClient(model_info, base_url=base_url)
        elif model_info.provider == Provider.GOOGLE:
            base_url = LLMFactory.get_provider_base_url(
                "google",
                "https://generativelanguage.googleapis.com/v1beta/openai/",
            )
            return GoogleClient(model_info, base_url=base_url)
        else:
            raise ValueError(f"Unsupported provider: {model_info.provider}")

    @staticmethod
    def list_available_models() -> list[str]:
        """List all available model names."""
        return sorted(ModelRegistry.MODELS.keys())

    @staticmethod
    def list_configured_models() -> list[str]:
        """List only configured models (with API keys)."""
        return sorted(ModelRegistry.list_configured_models().keys())


if __name__ == "__main__":
    # Demo: Try creating clients
    print("LLM Factory Demo\n")
    print("Available models:", LLMFactory.list_available_models()[:5], "...")
    print("Configured models:", LLMFactory.list_configured_models() or "(none)")
