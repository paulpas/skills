---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Provides Fits statistical distributions to data using goodness-of-fit tests, parameter estimation, and distribution
  selection methods"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-kernel-density, ds-maximum-likelihood, ds-monte-carlo
  role: implementation
  scope: implementation
  triggers: distribution fitting, goodness-of-fit, fitting distributions, distribution selection, how do i fit
  version: 1.0.0
name: distribution-fitting
---
# Distribution Fitting

Comprehensive guide to distribution fitting in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world statistical inference problems
- Building machine learning pipelines with distribution fitting
- Implementing best practices for distribution fitting
- Optimizing model performance using distribution fitting techniques
- Learning industry-standard approaches to distribution fitting

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require distribution fitting rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Distribution Fitting is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Distribution Fitting

```python
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

def basic_distribution_fitting(data: pd.Series) -> dict:
    """Fit a normal distribution to the provided data and return parameters."""
    if data is None or data.empty:
        raise ValueError("Input data cannot be None or empty")

    # Fit a normal distribution using Maximum Likelihood Estimation
    mu, std = stats.norm.fit(data)

    # Perform Kolmogorov-Smirnov test to validate fit
    ks_stat, p_value = stats.kstest(data, 'norm', args=(mu, std))

    # Generate fitted PDF for visualization
    x = np.linspace(data.min(), data.max(), 100)
    pdf = stats.norm.pdf(x, mu, std)

    return {
        "distribution": "normal",
        "parameters": {"mu": mu, "sigma": std},
        "goodness_of_fit": {"ks_statistic": ks_stat, "p_value": p_value},
        "x_values": x,
        "pdf_values": pdf
    }

# Example usage with synthetic data
if __name__ == "__main__":
    np.random.seed(42)
    sample_data = pd.Series(np.random.normal(loc=5.0, scale=2.0, size=500))
    results = basic_distribution_fitting(sample_data)
    print(f"Fitted mu: {results['parameters']['mu']:.3f}, sigma: {results['parameters']['sigma']:.3f}")
    print(f"KS Test p-value: {results['goodness_of_fit']['p_value']:.4f}")
```

### Pattern 2: Production-Ready Distribution Fitting

```python
import logging
import numpy as np
import pandas as pd
from scipy import stats
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class DistributionFitting:
    """Production-grade implementation for fitting and selecting statistical distributions."""

    def __init__(self, distributions: Optional[List[str]] = None):
        self.distributions = distributions or ['norm', 'expon', 'weibull_min', 'gamma']
        self.results: Dict[str, Any] = {}

    def _fit_distribution(self, dist_name: str, data: np.ndarray) -> Dict[str, float]:
        try:
            dist = getattr(stats, dist_name)
            params = dist.fit(data)
            # Calculate AIC for model selection
            n = len(data)
            log_likelihood = np.sum(dist.logpdf(data, *params))
            k = len(params)
            aic = 2 * k - 2 * log_likelihood
            return {"params": params, "aic": aic, "log_likelihood": log_likelihood}
        except Exception as e:
            logger.warning(f"Failed to fit {dist_name}: {e}")
            return {"params": None, "aic": np.inf, "log_likelihood": -np.inf}

    def execute(self, data: pd.DataFrame, target_col: str = "values") -> Dict[str, Any]:
        """Execute distribution fitting on specified column and return best model."""
        if target_col not in data.columns:
            raise ValueError(f"Column '{target_col}' not found in DataFrame")

        series = data[target_col].dropna()
        if series.empty:
            raise ValueError("Target column contains no valid data")

        logger.info(f"Fitting {len(self.distributions)} distributions to {len(series)} samples")
        fit_results = []

        for dist_name in self.distributions:
            res = self._fit_distribution(dist_name, series.values)
            fit_results.append({"distribution": dist_name, **res})

        # Select best distribution based on lowest AIC
        best_fit = min(fit_results, key=lambda x: x["aic"])
        self.results = {
            "status": "success",
            "best_distribution": best_fit["distribution"],
            "best_params": best_fit["params"],
            "aic": best_fit["aic"],
            "all_fits": fit_results
        }
        return self.results
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
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any
import matplotlib.pyplot as plt

def implement_fitting(data: pd.DataFrame, target_col: str = "values") -> Dict[str, Any]:
    """
    Complete implementation of Distribution Fitting.
    Demonstrates input validation, MLE fitting, KS testing, and visualization.
    Follows DRY and KISS principles for maintainable statistical code.
    """
    if data is None or data.empty:
        raise ValueError("Input data cannot be None or empty")
    if target_col not in data.columns:
        raise ValueError(f"Column '{target_col}' not found in DataFrame")

    series = data[target_col].dropna()
    if series.empty:
        raise ValueError("Target column contains no valid data")

    # Fit Normal Distribution via MLE
    mu, std = stats.norm.fit(series)
    ks_stat, p_value = stats.kstest(series, 'norm', args=(mu, std))

    # Generate fitted curve for plotting
    x = np.linspace(series.min(), series.max(), 100)
    pdf = stats.norm.pdf(x, mu, std)

    # Create visualization
    fig, ax = plt.subplots()
    ax.hist(series, bins=30, density=True, alpha=0.6, color='g', label='Data Histogram')
    ax.plot(x, pdf, 'r-', linewidth=2, label=f'Fitted Normal (μ={mu:.2f}, σ={std:.2f})')
    ax.set_title(f'Distribution Fit: KS p-value = {p_value:.4f}')
    ax.legend()
    plt.tight_layout()
    plt.savefig("distribution_fit.png")
    plt.close()

    return {
        'status': 'success',
        'parameters': {'mu': mu, 'sigma': std},
        'goodness_of_fit': {'ks_statistic': ks_stat, 'p_value': p_value},
        'plot_saved': 'distribution_fit.png',
        'metadata': {'rows': len(series), 'columns': data.shape[1]}
    }

# BAD vs GOOD Example Pair
# BAD: Ignoring distribution assumptions and skipping validation
def bad_fitting_approach(data: pd.DataFrame) -> Dict[str, Any]:
    # Assumes data is always normal without testing
    # No error handling for missing values or empty columns
    mu = data.mean()
    std = data.std()
    return {"mu": mu, "std": std}  # Returns summary stats, not a fitted distribution

# GOOD: Validates data, tests assumptions, and returns comprehensive fit metrics
def good_fitting_approach(data: pd.DataFrame, col: str = "values") -> Dict[str, Any]:
    if col not in data.columns or data[col].isna().all():
        raise ValueError("Invalid or empty target column")
    series = data[col].dropna()
    mu, std = stats.norm.fit(series)
    _, p_val = stats.kstest(series, 'norm', args=(mu, std))
    if p_val < 0.05:
        raise RuntimeError("Normality assumption rejected by KS test")
    return {"mu": mu, "sigma": std, "ks_p_value": p_val, "assumption_valid": True}

# Usage and testing
if __name__ == "__main__":
    np.random.seed(42)
    sample_data = pd.DataFrame({
        'values': np.random.normal(loc=5.0, scale=2.0, size=500)
    })
    results = implement_fitting(sample_data)
    print(f"Status: {results['status']}")
    print(f"Fitted parameters: {results['parameters']}")
    print(f"KS Test p-value: {results['goodness_of_fit']['p_value']:.4f}")
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-kernel-density` | Kernel Density techniques | Complementary to this skill |
| `coding-ds-maximum-likelihood` | Maximum Likelihood techniques | Complementary to this skill |
| `coding-ds-monte-carlo` | Monte Carlo techniques | Complementary to this skill |

## References

- Official documentation and papers on Distribution Fitting
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
