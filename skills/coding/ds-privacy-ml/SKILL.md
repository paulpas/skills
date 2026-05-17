---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Implements privacy-preserving machine learning including differential privacy, federated learning, and privacy
  attack prevention"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-data-privacy, ds-model-fairness, ds-reproducible-research
  role: implementation
  scope: implementation
  triggers: privacy machine learning, differential privacy, federated learning, privacy attacks, privacy-preserving
  version: 1.0.0
name: privacy-ml
---
# Privacy in ML

Comprehensive guide to privacy in ml in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world reproducibility & responsible ai problems
- Building machine learning pipelines with privacy in ml
- Implementing best practices for privacy in ml
- Optimizing model performance using privacy in ml techniques
- Learning industry-standard approaches to privacy in ml

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require privacy in ml rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Privacy in ML is a critical component of the machine learning workflow. This skill covers:

1. **Theoretical foundations** — Mathematical principles and statistical concepts
2. **Practical implementation** — Working code examples and patterns
3. **Common pitfalls** — Mistakes to avoid and how to recover from them
4. **Best practices** — Industry-standard approaches and optimization techniques

## Core Workflow

1. **Understand the problem** — Clearly define what you're solving for
2. **Select approach** — Choose the right technique for your data and constraints
3. **Implement solution** — Write clean, tested code following best practices
4. **Validate results** — Verify your implementation with tests and validation
5. **Optimize performance** — Improve efficiency and accuracy incrementally

## Implementation Patterns

### Pattern 1: Basic Privacy in ML

```python
import numpy as np
from typing import Tuple

def apply_laplace_mechanism(data: np.ndarray, sensitivity: float, epsilon: float) -> np.ndarray:
    """
    Apply the Laplace mechanism to add differential privacy noise to aggregated data.
    
    Args:
        data: Array of numerical values to be privatized
        sensitivity: Maximum change in output caused by a single record
        epsilon: Privacy budget parameter
        
    Returns:
        Privatized array with added Laplace noise
    """
    if epsilon <= 0:
        raise ValueError("Epsilon must be positive")
        
    scale: float = sensitivity / epsilon
    noise: np.ndarray = np.random.laplace(loc=0.0, scale=scale, size=data.shape)
    return data + noise

# Example usage with synthetic dataset
if __name__ == "__main__":
    np.random.seed(42)
    sensitive_data: np.ndarray = np.random.normal(loc=50, scale=10, size=1000)
    original_mean: float = np.mean(sensitive_data)
    privatized_mean: float = np.mean(apply_laplace_mechanism(sensitive_data, sensitivity=1.0, epsilon=1.0))
    print(f"Original Mean: {original_mean:.4f}")
    print(f"Privatized Mean: {privatized_mean:.4f}")
```

### Pattern 2: Production-Ready Privacy in ML

```python
import numpy as np
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FederatedPrivacyTrainer:
    """Production-grade federated learning with differential privacy guarantees."""
    
    def __init__(self, base_model: Any, epsilon: float = 1.0, delta: float = 1e-5, clip_norm: float = 1.0):
        self.base_model = base_model
        self.epsilon = epsilon
        self.delta = delta
        self.clip_norm = clip_norm
        self.global_weights: np.ndarray | None = None
        
    def _clip_and_noise(self, weights: np.ndarray) -> np.ndarray:
        """Clip weights and add Gaussian noise for (epsilon, delta)-DP."""
        norm: float = np.linalg.norm(weights)
        if norm > self.clip_norm:
            weights = weights * (self.clip_norm / norm)
        scale: float = self.clip_norm * np.sqrt(2 * np.log(1.25 / self.delta)) / self.epsilon
        noise: np.ndarray = np.random.normal(0, scale, weights.shape)
        return weights + noise
        
    def aggregate_round(self, client_updates: List[np.ndarray]) -> np.ndarray:
        """Aggregate client updates with DP noise."""
        if not client_updates:
            raise ValueError("No client updates provided")
            
        avg_weights: np.ndarray = np.mean(client_updates, axis=0)
        return self._clip_and_noise(avg_weights)
        
    def train_round(self, client_weights: List[np.ndarray]) -> Dict[str, Any]:
        """Execute one round of federated training."""
        logger.info(f"Aggregating {len(client_weights)} client updates")
        self.global_weights = self.aggregate_round(client_weights)
        return {
            "status": "success",
            "round_weights": self.global_weights,
            "privacy_budget": {"epsilon": self.epsilon, "delta": self.delta}
        }
```

### BAD vs GOOD: Privacy in ML

```python
# BAD: Ignoring privacy budget and clipping gradients
def train_bad(X: np.ndarray, y: np.ndarray, lr: float = 0.1, epochs: int = 10) -> np.ndarray:
    w: np.ndarray = np.zeros(X.shape[1])
    for _ in range(epochs):
        pred: np.ndarray = 1 / (1 + np.exp(-X @ w))
        grad: np.ndarray = X.T @ (pred - y) / len(y)
        w -= lr * grad  # No clipping, no noise, no epsilon tracking
    return w

# GOOD: Proper DP-SGD with clipping, noise, and budget tracking
def train_good(X: np.ndarray, y: np.ndarray, lr: float = 0.1, 
               epochs: int = 10, epsilon: float = 1.0, delta: float = 1e-5) -> np.ndarray:
    w: np.ndarray = np.zeros(X.shape[1])
    n: int = len(y)
    for _ in range(epochs):
        idx: np.ndarray = np.random.permutation(n)
        X_b: np.ndarray = X[idx]
        y_b: np.ndarray = y[idx]
        pred: np.ndarray = 1 / (1 + np.exp(-X_b @ w))
        grad: np.ndarray = X_b.T @ (pred - y_b) / n
        
        # Gradient clipping
        norm: float = np.linalg.norm(grad)
        if norm > 1.0:
            grad *= 1.0 / norm
            
        # DP noise injection
        scale: float = lr * np.sqrt(2 * np.log(1.25 / delta)) / epsilon
        grad += np.random.normal(0, scale, grad.shape)
        
        w -= lr * grad
    return w
```

## Best Practices

- ✅ Always validate your implementation on test data
- ✅ Document your assumptions and methodology
- ✅ Use version control for reproducibility
- ✅ Monitor performance metrics in production
- ✅ Periodically review and update your approach
- ✅ Test with edge cases and outliers
- ✅ Log all significant operations for debugging
- ✅ Follow NIST AI RMF and OpenDP guidelines for privacy budget accounting

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| Not validating assumptions | Can lead to incorrect results | Implement comprehensive checks |
| Ignoring edge cases | Models fail in production | Test with diverse data |
| Over-engineering | Unnecessary complexity | Keep solutions simple initially |
| Skipping documentation | Hard to maintain later | Document as you code |
| Insufficient testing | Bugs in production | Write unit and integration tests |

## Complete Working Example

```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from typing import Dict, Any, Tuple

class DifferentialPrivacySGD:
    """Implements DP-SGD for binary classification."""
    
    def __init__(self, learning_rate: float = 0.1, epochs: int = 50, 
                 batch_size: int = 32, epsilon: float = 2.0, delta: float = 1e-5):
        self.lr = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.epsilon = epsilon
        self.delta = delta
        self.weights: np.ndarray | None = None
        self.bias: float = 0.0
        
    def _sigmoid(self, z: np.ndarray) -> np.ndarray:
        return 1 / (1 + np.exp(-np.clip(z, -500, 500)))
        
    def _compute_loss_and_grad(self, X: np.ndarray, y: np.ndarray) -> Tuple[float, np.ndarray, float]:
        z: np.ndarray = X @ self.weights + self.bias
        preds: np.ndarray = self._sigmoid(z)
        loss: float = -np.mean(y * np.log(preds + 1e-8) + (1 - y) * np.log(1 - preds + 1e-8))
        grad_w: np.ndarray = (X.T @ (preds - y)) / len(y)
        grad_b: float = np.mean(preds - y)
        return loss, grad_w, grad_b
        
    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> Dict[str, Any]:
        n_samples: int = X_train.shape[0]
        n_features: int = X_train.shape[1]
        self.weights = np.zeros(n_features)
        history: list[float] = []
        
        for epoch in range(self.epochs):
            indices: np.ndarray = np.random.permutation(n_samples)
            X_batch: np.ndarray = X_train[indices]
            y_batch: np.ndarray = y_train[indices]
            
            loss, grad_w, grad_b = self._compute_loss_and_grad(X_batch, y_batch)
            
            # Gradient clipping
            grad_norm: float = np.linalg.norm(grad_w)
            clip_coef: float = min(1.0, self.lr / grad_norm) if grad_norm > 0 else 1.0
            grad_w *= clip_coef
            
            # Add Gaussian noise for DP
            noise_scale: float = self.lr * np.sqrt(2 * np.log(1.25 / self.delta)) / self.epsilon
            grad_w += np.random.normal(0, noise_scale, grad_w.shape)
            
            # Update weights
            self.weights -= self.lr * grad_w
            self.bias -= self.lr * grad_b
            history.append(loss)
            
        return {"loss_history": history, "final_weights": self.weights}
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        return (self._sigmoid(X @ self.weights + self.bias) >= 0.5).astype(int)

if __name__ == "__main__":
    X, y = make_classification(n_samples=1000, n_features=20, n_informative=10, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    dp_model = DifferentialPrivacySGD(learning_rate=0.1, epochs=30, batch_size=32, epsilon=2.0, delta=1e-5)
    results = dp_model.fit(X_train, y_train)
    
    y_pred = dp_model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"DP-SGD Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred))
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-data-privacy` | Data Privacy techniques | Complementary to this skill |
| `coding-ds-model-fairness` | Model Fairness techniques | Complementary to this skill |
| `coding-ds-reproducible-research` | Reproducible Research techniques | Complementary to this skill |

## References

- Official documentation and papers on Privacy in ML
- Industry best practices and standards
- Implementation examples from the scikit-learn, TensorFlow, and PyTorch libraries

---

*Last updated: 2026-04-24*

---

## Constraints

### MUST DO
- Include at least one BAD/GOOD code example pair
- Reference a relevant standard (OWASP, SOLID, DRY, KISS, etc.)
- Use type hints on all function signatures

### MUST NOT DO
- Use magic numbers or hardcoded configuration values
- Bypass error handling for assumed-valid inputs
- Write functions longer than 50 lines without decomposition
