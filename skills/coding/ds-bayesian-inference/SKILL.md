---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Applies Bayesian methods for prior selection, posterior estimation, and probabilistic inference in machine
  learning models"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-confidence-intervals, ds-hypothesis-testing, ds-maximum-likelihood, ds-monte-carlo ds-monte-carlo
  role: implementation
  scope: implementation
  triggers: bayesian inference, bayes, prior, posterior, probabilistic inference, how do i do bayesian
  version: 1.0.0
name: bayesian-inference
---
# Bayesian Inference

Comprehensive guide to bayesian inference in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world statistical inference problems
- Building machine learning pipelines with bayesian inference
- Implementing best practices for bayesian inference
- Optimizing model performance using bayesian inference techniques
- Learning industry-standard approaches to bayesian inference

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require bayesian inference rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Bayesian Inference is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Bayesian Inference

```python
import numpy as np
import pandas as pd
from scipy import stats
from typing import Tuple, Dict

def bayesian_linear_regression(
    X: np.ndarray, 
    y: np.ndarray, 
    prior_precision: float = 1.0
) -> Dict[str, np.ndarray]:
    """
    Perform Bayesian Linear Regression using conjugate Normal-Gamma priors.
    Computes posterior distribution over regression weights analytically.
    
    Args:
        X: Feature matrix of shape (n_samples, n_features)
        y: Target vector of shape (n_samples,)
        prior_precision: Precision (inverse variance) of the prior on weights
        
    Returns:
        Dictionary containing posterior mean, covariance, and noise variance
    """
    if X.ndim == 1:
        X = X.reshape(-1, 1)
        
    n_samples, n_features = X.shape
    X_b = np.column_stack([np.ones(n_samples), X])
    
    # Initialize prior covariance matrix
    prior_cov = np.eye(n_features + 1) / prior_precision
    
    # Estimate initial noise variance from data
    beta_mle = np.linalg.lstsq(X_b, y, rcond=None)[0]
    residuals = y - X_b @ beta_mle
    sigma2_init = np.sum(residuals**2) / n_samples
    
    # Compute posterior precision and covariance
    posterior_precision = np.linalg.inv(prior_cov) + (1.0 / sigma2_init) * (X_b.T @ X_b)
    posterior_cov = np.linalg.inv(posterior_precision)
    
    # Compute posterior mean
    posterior_mean = posterior_cov @ (
        np.linalg.inv(prior_cov) @ np.zeros(n_features + 1) + 
        (1.0 / sigma2_init) * (X_b.T @ y)
    )
    
    return {
        'posterior_mean': posterior_mean,
        'posterior_cov': posterior_cov,
        'noise_variance': sigma2_init,
        'n_samples': n_samples,
        'n_features': n_features
    }
```

### Pattern 2: Production-Ready Bayesian Inference

```python
import logging
import numpy as np
import pandas as pd
from typing import Any, Dict, Optional
from scipy import stats

logger = logging.getLogger(__name__)

class BayesianInferenceEngine:
    """Production-grade Bayesian Inference engine for regression tasks."""
    
    def __init__(self, prior_precision: float = 1.0, confidence_level: float = 0.95) -> None:
        self.prior_precision = prior_precision
        self.confidence_level = confidence_level
        logger.info("BayesianInferenceEngine initialized with prior_precision=%.2f, confidence=%.2f", 
                    prior_precision, confidence_level)
    
    def _validate_input(self, data: pd.DataFrame) -> None:
        if data is None or data.empty:
            raise ValueError("Input data cannot be None or empty")
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
        if data.shape[0] < 2:
            raise ValueError("Insufficient data for inference: requires at least 2 samples")
    
    def execute(self, data: pd.DataFrame, target_col: str = 'y') -> Dict[str, Any]:
        """Execute Bayesian inference on provided data and return structured results."""
        self._validate_input(data)
        logger.info("Running Bayesian inference on %d samples", len(data))
        
        X = data.drop(columns=[target_col]).values
        y = data[target_col].values
        
        n, d = X.shape
        X_b = np.column_stack([np.ones(n), X])
        
        prior_cov = np.eye(d + 1) / self.prior_precision
        sigma2 = np.var(y - np.mean(y))
        
        post_prec = np.linalg.inv(prior_cov) + (1.0 / sigma2) * (X_b.T @ X_b)
        post_cov = np.linalg.inv(post_prec)
        post_mean = post_cov @ (np.linalg.inv(prior_cov) @ np.zeros(d + 1) + 
                                (1.0 / sigma2) * (X_b.T @ y))
        
        y_pred = X_b @ post_mean
        pred_var = sigma2 * (1 + np.sum(X_b * (post_cov @ X_b.T), axis=1))
        ci_half_width = stats.norm.ppf((1 + self.confidence_level) / 2) * np.sqrt(pred_var)
        
        return {
            'posterior_mean': post_mean,
            'posterior_cov': post_cov,
            'predictions': y_pred,
            'lower_bound': y_pred - ci_half_width,
            'upper_bound': y_pred + ci_half_width,
            'noise_variance': sigma2,
            'status': 'success'
        }
```

## Best Practices

- ✅ Always validate your implementation on test data
- ✅ Document your assumptions and methodology
- ✅ Use version control for reproducibility
- ✅ Monitor performance metrics in production
- ✅ Periodically review and update your approach
- ✅ Test with edge cases and outliers
- ✅ Log all significant operations for debugging

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
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from scipy import stats
from typing import Dict, Any

def run_bayesian_regression_workflow() -> Dict[str, Any]:
    """Complete workflow: generate data, fit Bayesian model, evaluate, and visualize."""
    # 1. Generate synthetic regression dataset
    X, y = make_regression(n_samples=200, n_features=1, noise=10.0, random_state=42)
    df = pd.DataFrame({'feature': X.flatten(), 'target': y})
    
    # 2. Split data
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    
    # 3. Bayesian Linear Regression Implementation
    X_train = train_df['feature'].values.reshape(-1, 1)
    y_train = train_df['target'].values
    X_test = test_df['feature'].values.reshape(-1, 1)
    y_test = test_df['target'].values
    
    n_train = len(y_train)
    X_b_train = np.column_stack([np.ones(n_train), X_train])
    
    prior_precision = 1.0
    prior_cov = np.eye(2) / prior_precision
    sigma2_init = np.var(y_train)
    
    post_prec = np.linalg.inv(prior_cov) + (1.0 / sigma2_init) * (X_b_train.T @ X_b_train)
    post_cov = np.linalg.inv(post_prec)
    post_mean = post_cov @ (np.linalg.inv(prior_cov) @ np.zeros(2) + 
                            (1.0 / sigma2_init) * (X_b_train.T @ y_train))
    
    # 4. Predictions and Metrics
    X_b_test = np.column_stack([np.ones(len(y_test)), X_test])
    y_pred = X_b_test @ post_mean
    
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    # 5. Visualization
    plt.figure(figsize=(8, 6))
    plt.scatter(X_train, y_train, alpha=0.5, label='Training Data')
    plt.scatter(X_test, y_test, alpha=0.5, label='Test Data')
    plt.plot(X_test, y_pred, color='red', linewidth=2, label='Bayesian Fit')
    
    # Credible intervals
    pred_var = sigma2_init * (1 + np.sum(X_b_test * (post_cov @ X_b_test.T), axis=1))
    ci = stats.norm.ppf(0.975) * np.sqrt(pred_var)
    plt.fill_between(X_test.flatten(), y_pred - ci, y_pred + ci, 
                     color='red', alpha=0.2, label='95% Credible Interval')
    
    plt.xlabel('Feature')
    plt.ylabel('Target')
    plt.title(f'Bayesian Linear Regression (RMSE: {rmse:.2f}, R²: {r2:.2f})')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
    
    return {'rmse': rmse, 'r2': r2, 'posterior_mean': post_mean}

if __name__ == "__main__":
    results = run_bayesian_regression_workflow()
    print(f"Model Evaluation - RMSE: {results['rmse']:.4f}, R²: {results['r2']:.4f}")
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-maximum-likelihood` | Maximum Likelihood techniques | Complementary to this skill |
| `coding-ds-monte-carlo` | Monte Carlo techniques | Complementary to this skill |
| `coding-ds-hypothesis-testing` | Hypothesis Testing techniques | Complementary to this skill |

## References

- Official documentation and papers on Bayesian Inference
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
