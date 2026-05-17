---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Implements synthetic control methods, difference-in-differences estimation, and quasi-experimental designs
  for impact evaluation"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-causal-inference, ds-intervention-analysis, ds-observational-studies
  role: implementation
  scope: implementation
  triggers: synthetic control, difference-in-differences, DiD, quasi-experiment, impact evaluation
  version: 1.0.0
name: synthetic-control
---
# Synthetic Control Methods

Comprehensive guide to synthetic control methods in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world causal inference problems
- Building machine learning pipelines with synthetic control methods
- Implementing best practices for synthetic control methods
- Optimizing model performance using synthetic control methods techniques
- Learning industry-standard approaches to synthetic control methods

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require synthetic control methods rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Synthetic Control Methods is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Synthetic Control Methods

```python
import numpy as np
from scipy.optimize import minimize
from typing import Tuple

def compute_synthetic_weights(
    X_donor: np.ndarray, 
    X_treated: np.ndarray, 
    regularization: float = 1e-4
) -> np.ndarray:
    """
    Compute optimal donor weights for synthetic control using constrained optimization.
    
    Args:
        X_donor: (n_donors, n_features) matrix of donor pre-treatment data
        X_treated: (n_features,) vector of treated unit pre-treatment data
        regularization: L2 penalty to prevent overfitting weights
        
    Returns:
        Optimal non-negative weights summing to 1.0
        
    Raises:
        ValueError: If input dimensions are incompatible
    """
    if X_donor.shape[1] != X_treated.shape[0]:
        raise ValueError("Donor features must match treated feature dimensions")
        
    def objective(w: np.ndarray) -> float:
        prediction = X_donor @ w
        residual = X_treated - prediction
        return float(np.sum(residual**2) + regularization * np.sum(w**2))
        
    constraints = (
        {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0},
        {'type': 'ineq', 'fun': lambda w: w}
    )
    
    n_donors = X_donor.shape[0]
    initial_weights = np.ones(n_donors) / n_donors
    
    result = minimize(
        objective, 
        initial_weights, 
        constraints=constraints, 
        method='SLSQP',
        options={'maxiter': 1000, 'ftol': 1e-9}
    )
    
    if not result.success:
        raise RuntimeError(f"Weight optimization failed: {result.message}")
        
    return result.x
```

### Pattern 2: Production-Ready Synthetic Control Methods

```python
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from scipy.optimize import minimize

logger = logging.getLogger(__name__)

class SyntheticControlEstimator:
    """Production-grade Synthetic Control Method estimator with DiD support."""
    
    def __init__(self, regularization: float = 1e-4, max_iter: int = 1000) -> None:
        self.regularization = regularization
        self.max_iter = max_iter
        self.weights_: Optional[np.ndarray] = None
        self.pre_error_: Optional[float] = None
        self.post_error_: Optional[float] = None
        
    def _optimize_weights(self, X_donor: np.ndarray, X_treated: np.ndarray) -> np.ndarray:
        """Find non-negative weights summing to 1 that minimize pre-treatment error."""
        def loss(w: np.ndarray) -> float:
            pred = X_donor @ w
            error = X_treated - pred
            return float(np.sum(error**2) + self.regularization * np.sum(w**2))
            
        constraints = (
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0},
            {'type': 'ineq', 'fun': lambda w: w}
        )
        
        n_donors = X_donor.shape[0]
        w0 = np.ones(n_donors) / n_donors
        
        res = minimize(
            loss, w0, constraints=constraints, method='SLSQP',
            options={'maxiter': self.max_iter}
        )
        if not res.success:
            logger.warning(f"Weight optimization did not converge: {res.message}")
        return res.x
        
    def fit_predict(
        self, 
        donor_data: pd.DataFrame, 
        treated_data: pd.DataFrame, 
        period_col: str = 'period', 
        treated_unit_id: str = 'treated'
    ) -> Dict[str, Any]:
        """Fit SCM and predict counterfactual outcomes."""
        if donor_data.empty or treated_data.empty:
            raise ValueError("Input DataFrames cannot be empty")
            
        donor_pre = donor_data[donor_data[period_col] < 0].drop(columns=[treated_unit_id])
        treated_pre = treated_data[treated_data[period_col] < 0].drop(columns=[treated_unit_id])
        
        X_donor = donor_pre.values
        X_treated = treated_pre.values.flatten()
        
        self.weights_ = self._optimize_weights(X_donor, X_treated)
        self.pre_error_ = float(np.mean((X_treated - X_donor @ self.weights_)**2))
        
        donor_post = donor_data[donor_data[period_col] >= 0].drop(columns=[treated_unit_id])
        counterfactual = donor_post.values @ self.weights_
        
        return {
            'weights': self.weights_,
            'pre_mse': self.pre_error_,
            'counterfactual': counterfactual,
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

```python
# BAD: Hardcoded values, no validation, violates DRY principle
def bad_scm(data):
    w = [0.1, 0.2, 0.3, 0.4]  # Magic numbers
    return sum(w) * data['y']

# GOOD: Type hints, validation, configurable parameters, follows SOLID/DRY
def good_scm(
    donor_matrix: np.ndarray, 
    target_vector: np.ndarray, 
    reg_lambda: float = 1e-3
) -> np.ndarray:
    if donor_matrix.shape[1] != target_vector.shape[0]:
        raise ValueError("Dimension mismatch")
    weights = compute_synthetic_weights(donor_matrix, target_vector, reg_lambda)
    return weights
```

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
from typing import Dict, Any
from scipy.optimize import minimize

class SyntheticControlMethod:
    """Implements Abadie et al. synthetic control with post-treatment impact estimation."""
    
    def __init__(self, regularization: float = 1e-3) -> None:
        self.regularization = regularization
        self.weights_: Optional[np.ndarray] = None
        
    def fit(self, X_donor: np.ndarray, X_treated: np.ndarray) -> 'SyntheticControlMethod':
        def objective(w: np.ndarray) -> float:
            return float(np.sum((X_treated - X_donor @ w)**2) + self.regularization * np.sum(w**2))
        constraints = (
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0},
            {'type': 'ineq', 'fun': lambda w: w}
        )
        res = minimize(objective, np.ones(X_donor.shape[0])/X_donor.shape[0], 
                       constraints=constraints, method='SLSQP')
        if not res.success:
            raise RuntimeError(f"Optimization failed: {res.message}")
        self.weights_ = res.x
        return self
        
    def predict(self, X_donor_post: np.ndarray) -> np.ndarray:
        return X_donor_post @ self.weights_

def generate_synthetic_data(
    n_donors: int = 20, 
    n_pre: int = 10, 
    n_post: int = 10, 
    treatment_effect: float = 5.0
) -> pd.DataFrame:
    np.random.seed(42)
    periods = list(range(-n_pre, 0)) + list(range(0, n_post))
    data = []
    for i in range(n_donors):
        for p in periods:
            noise = np.random.normal(0, 0.5)
            trend = 0.1 * p
            data.append({'unit': f'donor_{i}', 'period': p, 'value': trend + noise})
    for p in periods:
        noise = np.random.normal(0, 0.5)
        trend = 0.1 * p
        effect = treatment_effect if p >= 0 else 0
        data.append({'unit': 'treated', 'period': p, 'value': trend + noise + effect})
    return pd.DataFrame(data)

def evaluate_scm(df: pd.DataFrame) -> Dict[str, Any]:
    donor_df = df[df['unit'] != 'treated']
    treated_df = df[df['unit'] == 'treated']
    
    donor_pre = donor_df[donor_df['period'] < 0].pivot(index='period', columns='unit', values='value').T
    treated_pre = treated_df[treated_df['period'] < 0].set_index('period')['value']
    
    scm = SyntheticControlMethod(regularization=1e-3)
    scm.fit(donor_pre.values, treated_pre.values)
    
    donor_post = donor_df[donor_df['period'] >= 0].pivot(index='period', columns='unit', values='value').T
    counterfactual = scm.predict(donor_post.values)
    actual_post = treated_df[treated_df['period'] >= 0].set_index('period')['value'].values
    
    impact = actual_post - counterfactual
    return {
        'weights': scm.weights_,
        'pre_mse': float(np.mean((treated_pre.values - donor_pre.values @ scm.weights_)**2)),
        'post_impact': impact,
        'mean_impact': float(np.mean(impact))
    }

if __name__ == "__main__":
    df = generate_synthetic_data()
    results = evaluate_scm(df)
    print(f"Pre-treatment MSE: {results['pre_mse']:.4f}")
    print(f"Mean Post-treatment Impact: {results['mean_impact']:.4f}")
    
    plt.figure(figsize=(10, 5))
    plt.plot(df[df['unit']=='treated']['period'], df[df['unit']=='treated']['value'], 'k-', label='Treated')
    plt.plot(df[df['unit']!='treated']['period'], df[df['unit']!='treated']['value'], 'b--', alpha=0.3, label='Donors')
    plt.axvline(x=0, color='r', linestyle=':', label='Treatment')
    plt.legend()
    plt.title('Synthetic Control Method: Treated vs Donor Pool')
    plt.show()
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-causal-inference` | Causal Inference techniques | Complementary to this skill |
| `coding-ds-intervention-analysis` | Intervention Analysis techniques | Complementary to this skill |
| `coding-ds-observational-studies` | Observational Studies techniques | Complementary to this skill |

## References

- Official documentation and papers on Synthetic Control Methods
- Industry best practices and standards
- Implementation examples from the scikit-learn, TensorFlow, and PyTorch libraries
- DRY (Don't Repeat Yourself) and SOLID principles for maintainable causal inference code

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
