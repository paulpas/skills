# Self-Hosted LLM Provider Configuration (vLLM, LiteLLM)

This guide explains how to configure the Skill Router to use self-hosted LLM providers like vLLM and LiteLLM, including the embedding emulation workaround for providers without native embedding support.

## Overview

Self-hosted LLM providers offer:
- **Privacy and data control** - Keep your data on-premises
- **Cost savings** - No per-request billing for high-volume usage
- **Custom models** - Run fine-tuned or proprietary models
- **Offline capability** - No internet dependency

## Supported Providers

### vLLM
- High-performance LLM inference server
- Compatible with OpenAI API format
- Great for local or on-prem deployments

### LiteLLM
- Unified API for multiple LLM providers
- Supports OpenAI, Anthropic, Cohere, and more
- Can route to multiple backends

### Local LLMs
- llama.cpp, Ollama, Text Generation WebUI
- Run models locally on your machine
- No external API calls needed

## Configuration for Self-Hosted Endpoints

### Basic Configuration

```bash
# Self-Hosted LLM Configuration
LLM_ENDPOINT_URL=http://localhost:8000/v1
LLM_ENDPOINT_API_KEY=dummy

# Provider selection
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai
```

### Complete Configuration Example

```bash
# ─────────────────────────────────────────────────────────────────────────────
# Self-Hosted LLM Provider Configuration
# ─────────────────────────────────────────────────────────────────────────────

# Your custom LLM endpoint URL
LLM_ENDPOINT_URL=http://localhost:8000/v1
LLM_ENDPOINT_API_KEY=dummy

# LLM Provider Selection (use 'openai' for OpenAI-compatible endpoints)
LLM_PROVIDER=openai
LLM_MODEL=your-model-name

# Embedding Provider Configuration
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=your-embedding-model

# ─────────────────────────────────────────────────────────────────────────────
# Networking Configuration
# ─────────────────────────────────────────────────────────────────────────────

PORT=3000

# ─────────────────────────────────────────────────────────────────────────────
# Optional: GitHub Integration
# ─────────────────────────────────────────────────────────────────────────────

GITHUB_ENABLED=true
GITHUB_TOKEN=

# ─────────────────────────────────────────────────────────────────────────────
# Optional: Auto-Skill Generation
# ─────────────────────────────────────────────────────────────────────────────

AUTO_SKILL_ENABLED=true
AUTO_SKILL_MODEL=your-model-name
```

## Embedding Configuration Challenges

### The Problem

Most self-hosted LLM providers (vLLM, Ollama, local models) **do not include embedding models**. Embeddings are a separate specialized model type optimized for semantic similarity, not general LLMs.

### The Solution: Embedding Emulation

Since dedicated embedding models may not be available, the Skill Router supports **embedding emulation** - using the LLM itself to generate embeddings through a prompt-based approach.

### How Embedding Emulation Works

The process uses a specialized prompt that asks the LLM to output a fixed-size vector representation:

```
Represent the following text as a JSON array of 64 floats capturing its semantic meaning.
Output only the array.

Text: "Your text here"
```

The LLM responds with:
```json
[0.12, -0.45, 0.78, -0.23, 0.56, ...]
```

### Why 64 Dimensions?

- **Low dimensionality** (64 floats = 256 bytes) minimizes token usage
- **Reasonable semantic capture** for skill routing tasks
- **Compatibility** with vector search algorithms
- **Speed** - smaller vectors are faster to compute and compare

### Configuration for Emulation

When using embedding emulation:

```bash
# Self-Hosted LLM Configuration
LLM_ENDPOINT_URL=http://localhost:8000/v1
LLM_ENDPOINT_API_KEY=dummy
LLM_MODEL=your-model-name

# For self-hosted providers without native embeddings
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=emulated-64

# Optional: Specify the LLM model to use for embedding emulation
EMBEDDING_LLM_MODEL=your-model-name
```

### Customizing the Emulation Prompt

The default emulation prompt is:
```
Represent the following text as a JSON array of 64 floats capturing its semantic meaning.
Output only the array.
```

If you want to customize this for your specific model, you can modify the Skill Router configuration (requires code modification or environment variable override).

## Provider-Specific Configuration

### vLLM Configuration

vLLM is an OpenAI-compatible server, so configure it like this:

```bash
# vLLM Configuration
LLM_ENDPOINT_URL=http://localhost:8000/v1
LLM_ENDPOINT_API_KEY=dummy
LLM_MODEL=meta-llama/Meta-Llama-3-8B-Instruct

# Embeddings (emulated)
EMBEDDING_MODEL=emulated-64
```

### LiteLLM Configuration

LiteLLM provides a unified API for multiple providers:

```bash
# LiteLLM Configuration
LLM_ENDPOINT_URL=https://api.litellm.com/v1
LLM_ENDPOINT_API_KEY=your-litellm-key
LLM_MODEL=claude-4-sonnet

# Embeddings (use native if available, otherwise emulated)
EMBEDDING_MODEL=emulated-64
```

### Ollama Configuration

Ollama runs local LLMs with simple configuration:

```bash
# Ollama Configuration
LLM_ENDPOINT_URL=http://localhost:11434/v1
LLM_ENDPOINT_API_KEY=dummy
LLM_MODEL=llama3:8b

# Embeddings (emulated - Ollama doesn't include embeddings)
EMBEDDING_MODEL=emulated-64
```

### Text Generation WebUI Configuration

For the popular Text Generation WebUI:

```bash
# Text Generation WebUI Configuration
LLM_ENDPOINT_URL=http://localhost:5000/v1
LLM_ENDPOINT_API_KEY=dummy
LLM_MODEL=your-model-name

# Embeddings (emulated)
EMBEDDING_MODEL=emulated-64
```

## Performance Considerations

### Speed Comparison

| Approach | Speed | Quality | Resource Usage |
|----------|-------|---------|----------------|
| Native Embeddings (OpenAI) | Fast | High | Low (offloaded) |
| Emulated Embeddings | Slow | Medium | High (uses LLM) |
| Local Embedding Model | Fast | High | High (GPU memory) |

### Recommendations

1. **For development/testing**: Use emulated embeddings (no extra setup needed)
2. **For production with high volume**: Consider running a dedicated embedding model
3. **For privacy-critical applications**: Run embedding model on-premises

### Optimization Tips

1. **Use smaller models** for emulation (7B-13B parameters)
2. **Batch requests** when possible to improve throughput
3. **Cache embeddings** for repeated text queries
4. **Monitor GPU usage** during embedding generation

## Security Considerations

### API Key Handling

For self-hosted endpoints:

```bash
# If your endpoint requires authentication
LLM_ENDPOINT_API_KEY=your-api-key-here

# If no authentication (like Ollama)
LLM_ENDPOINT_API_KEY=dummy
```

**Important**: If your self-hosted endpoint is exposed to the internet:
- Use HTTPS with valid certificates
- Implement authentication (API keys, OAuth)
- Restrict access via firewall rules
- Consider using a reverse proxy (like NGINX) for SSL termination

### Data Privacy

Self-hosted solutions provide better data privacy:

- ✅ No data leaves your infrastructure
- ✅ No third-party API calls
- ✅ Compliance with strict data residency requirements
- ⚠️ Still need to secure your local infrastructure

## Troubleshooting

### Error: "Connection refused"

**Solution**: Verify your endpoint is running:
```bash
curl http://localhost:8000/v1/models
```

### Error: "Model not found"

**Solution**: Check available models:
```bash
curl http://localhost:8000/v1/models
```

### Error: "Embedding generation failed"

**Solution**: Try a smaller model for emulation or verify the LLM can generate JSON output correctly.

### Error: "Slow embedding generation"

**Solution**: 
- Use a smaller model for emulation
- Increase the LLM endpoint timeout
- Consider caching embeddings

### Error: "Invalid JSON in response"

**Solution**: Some models struggle with JSON output. Try:
- Using a model known for JSON generation (e.g., `gpt-4o-mini`)
- Adding "Output valid JSON only" to the prompt
- Using a larger, more capable model

## Testing Your Configuration

After configuring, test your setup:

```bash
# Test the Skill Router with self-hosted LLM
docker run --rm \
  -e LLM_ENDPOINT_URL="http://host.docker.internal:8000/v1" \
  -e LLM_ENDPOINT_API_KEY="dummy" \
  -e LLM_MODEL="llama3:8b" \
  -e EMBEDDING_MODEL="emulated-64" \
  -p 3000:3000 \
  skill-router:latest
```

Then test the endpoints:

```bash
# Test LLM endpoint
curl http://localhost:3000/v1/chat/completions \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dummy" \
  -d '{
    "model": "llama3:8b",
    "messages": [{"role": "user", "content": "test"}]
  }'

# Test embeddings endpoint
curl http://localhost:3000/embeddings \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"input": "test query", "model": "emulated-64"}'
```

## Comparison: Native vs Emulated Embeddings

| Aspect | Native Embeddings | Emulated Embeddings |
|--------|------------------|---------------------|
| **Quality** | Optimized for semantic similarity | General LLM output |
| **Speed** | Fast (dedicated model) | Slow (uses LLM) |
| **Cost** | Low per request | High (uses LLM tokens) |
| **Setup** | Requires embedding model | Works with any LLM |
| **Dimensions** | Fixed (e.g., 1536 for OpenAI) | Variable (64 in our case) |
| **Best For** | Production, high volume | Development, low volume |

## Related Documentation

- [Full Installation Guide](../README.md#installation)
- [OpenAI Provider Configuration](config-openai.md)
- [Anthropic Provider Configuration](config-anthropic.md)
- [API Documentation](../API.md)

## Support

For vLLM:
- [vLLM Documentation](https://docs.vllm.ai/)
- [vLLM GitHub](https://github.com/vllm-project/vllm)

For LiteLLM:
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [LiteLLM GitHub](https://github.com/BerriAI/litellm)

For Ollama:
- [Ollama Documentation](https://ollama.com/docs)
- [Ollama GitHub](https://github.com/ollama/ollama)
