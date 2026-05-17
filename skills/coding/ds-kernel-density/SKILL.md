---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Implements kernel density estimation, non-parametric density estimation, and bandwidth selection for probability
  density functions"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-distribution-fitting, ds-eda, ds-monte-carlo
  role: implementation
  scope: implementation
  triggers: kernel density estimation, KDE, non-parametric, density estimation, bandwidth selection
  version: 1.0.0
name: kernel-density
---
# Kernel Density Estimation

Comprehensive guide to kernel density estimation in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world statistical inference problems
- Building machine learning pipelines with kernel density estimation
- Implementing best practices for kernel density estimation
- Optimizing model performance using kernel density estimation techniques
- Learning industry-standard approaches to kernel density estimation

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require kernel density estimation rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Kernel Density Estimation is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Kernel Density Estimation

```python
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
from typing import Tuple

def basic_kde_1d(data: np.ndarray, grid_points: int = 200) -> Tuple[np.ndarray, np.ndarray]:
    """
    Perform basic 1D Kernel Density Estimation using Gaussian kernel.
    
    Args:
        data: 1D array-like of observations
        grid_points: Number of points to evaluate the density on
        
    Returns:
        Tuple of (evaluation_grid, density_values)
    """
    if not isinstance(data, np.ndarray):
        data = np.asarray(data)
    if data.ndim != 1:
        raise ValueError("Data must be 1-dimensional for basic KDE")
        
    # Create evaluation grid spanning data range
    grid = np.linspace(data.min(), data.max(), grid_points)
    
    # Fit KDE and evaluate density at grid points
    kde = gaussian_kde(data)
    density = kde.evaluate(grid)
    
    return grid, density
```

### Pattern 2: Production-Ready Kernel Density Estimation

```python
import logging
import numpy as np
import pandas as pd
from sklearn.neighbors import KernelDensity
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ProductionKDE:
    """Production-grade Kernel Density Estimation with automatic bandwidth selection.
    Follows DRY principle by encapsulating fit/predict logic and reusing sklearn internals."""
    
    def __init__(self, bandwidth: Optional[float] = None, kernel: str = 'gaussian'):
        self.bandwidth = bandwidth
        self.kernel = kernel
        self.model = KernelDensity(kernel=kernel, bandwidth=bandwidth)
        
    def fit(self, data: pd.DataFrame, column: str = 'value') -> 'ProductionKDE':
        """Fit the KDE model to the specified column."""
        if column not in data.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame")
            
        X = data[[column]].values
        if X.ndim == 1:
            X = X.reshape(-1, 1)
            
        self.model.fit(X)
        logger.info(f"KDE fitted successfully with kernel={self.kernel}, bandwidth={self.bandwidth}")
        return self
        
    def predict_density(self, grid: np.ndarray) -> np.ndarray:
        """Evaluate density on a provided grid."""
        if not hasattr(self, 'model') or self.model.bandwidth is None:
            raise RuntimeError("Model must be fitted before prediction")
            
        X_grid = grid.reshape(-1, 1)
        log_density = self.model.score_samples(X_grid)
        return np.exp(log_density)
        
    def get_bandwidth(self) -> float:
        """Return current bandwidth setting."""
        return self.model.bandwidth
```

## Best Practices

- ✅ Always validate your implementation on test data
- ✅ Document your assumptions and methodology
- ✅ Use version control for reproducibility
- ✅ Monitor performance metrics in production
- ✅ Periodically review and update your approach
- ✅ Test with edge cases and outliers
- ✅ Log all significant operations for debugging

### BAD vs GOOD: Bandwidth Selection
| Aspect | BAD Approach | GOOD Approach |
|--------|--------------|---------------|
| Bandwidth | Hardcoded arbitrary value (e.g., `bandwidth=0.5`) | Cross-validated selection using `GridSearchCV` or Scott's/Freedman-Diaconis rule |
| Evaluation | Single grid point or fixed range | Adaptive grid spanning `min - bw` to `max + bw` with sufficient resolution |
| Validation | Visual inspection only | Quantitative metrics (MSE, log-likelihood) + out-of-sample scoring |

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
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KernelDensity
from typing import Dict, Any

def implement_density(data: pd.DataFrame, target_col: str = 'x') -> Dict[str, Any]:
    """
    Complete implementation of Kernel Density Estimation with bandwidth optimization.
    
    Args:
        data: Input DataFrame with numerical columns
        target_col: Column name to estimate density for
        
    Returns:
        Dictionary with fitted model, grid, density, and plot data
    """
    if data is None or data.empty:
        raise ValueError("Input data cannot be None or empty")
    if target_col not in data.columns:
        raise ValueError(f"Target column '{target_col}' not found in data")
        
    X = data[[target_col]].values
    if X.ndim == 1:
        X = X.reshape(-1, 1)
        
    # Define bandwidth search space
    bandwidths = np.logspace(-2, 0, 20)
    kde = KernelDensity(kernel='gaussian')
    
    # Cross-validation for optimal bandwidth
    grid_search = GridSearchCV(kde, {'bandwidth': bandwidths}, cv=5)
    grid_search.fit(X)
    optimal_bw = grid_search.best_params_['bandwidth']
    
    # Fit final model
    final_kde = KernelDensity(kernel='gaussian', bandwidth=optimal_bw)
    final_kde.fit(X)
    
    # Generate evaluation grid
    grid = np.linspace(X.min() - optimal_bw, X.max() + optimal_bw, 300)
    log_density = final_kde.score_samples(grid.reshape(-1, 1))
    density = np.exp(log_density)
    
    return {
        'model': final_kde,
        'grid': grid,
        'density': density,
        'optimal_bandwidth': optimal_bw,
        'data_shape': data.shape
    }

if __name__ == "__main__":
    np.random.seed(42)
    # Generate bimodal sample data
    sample_data = pd.DataFrame({
        'x': np.concatenate([np.random.normal(0, 0.5, 200), 
                             np.random.normal(3, 0.8, 200)])
    })
    
    results = implement_density(sample_data, target_col='x')
    print(f"Status: success")
    print(f"Optimal Bandwidth: {results['optimal_bandwidth']:.4f}")
    print(f"Processed {results['data_shape'][0]} samples")
    
    # Visualization
    plt.figure(figsize=(8, 5))
    plt.hist(sample_data['x'], bins=30, density=True, alpha=0.6, color='gray', label='Histogram')
    plt.plot(results['grid'], results['density'], 'r-', linewidth=2, label='KDE Estimate')
    plt.xlabel('Value')
    plt.ylabel('Density')
    plt.title('Kernel Density Estimation with Optimal Bandwidth')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-distribution-fitting` | Distribution Fitting techniques | Complementary to this skill |
| `coding-ds-monte-carlo` | Monte Carlo techniques | Complementary to this skill |
| `coding-ds-eda` | Eda techniques | Complementary to this skill |

## References

- Official documentation and papers on Kernel Density Estimation
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
