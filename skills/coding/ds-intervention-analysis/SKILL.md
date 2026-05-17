---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Provides Estimates treatment effects, conditional average treatment effects (CATE), heterogeneous effects,
  and individual treatment responses"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-causal-inference, ds-observational-studies, ds-randomized-experiments, ds-synthetic-control ds-synthetic-control
  role: implementation
  scope: implementation
  triggers: treatment effects, intervention analysis, CATE, heterogeneous effects, treatment response
  version: 1.0.0
name: intervention-analysis
---
# Intervention Analysis

Comprehensive guide to intervention analysis in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world causal inference problems
- Building machine learning pipelines with intervention analysis
- Implementing best practices for intervention analysis
- Optimizing model performance using intervention analysis techniques
- Learning industry-standard approaches to intervention analysis

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require intervention analysis rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Intervention Analysis is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Intervention Analysis

```python
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from typing import Dict, Any

def estimate_ate_propensity_score(data: pd.DataFrame, treatment_col: str, outcome_col: str) -> Dict[str, Any]:
    """Estimate Average Treatment Effect using Propensity Score Weighting (IPTW)."""
    if treatment_col not in data.columns or outcome_col not in data.columns:
        raise ValueError(f"Columns '{treatment_col}' and '{outcome_col}' must exist in data.")
    
    X = data.drop(columns=[treatment_col, outcome_col])
    y_treatment = data[treatment_col]
    y_outcome = data[outcome_col]
    
    # Step 1: Estimate propensity scores (probability of treatment)
    propensity_model = LogisticRegression(max_iter=1000, random_state=42)
    propensity_model.fit(X, y_treatment)
    propensity_scores = propensity_model.predict_proba(X)[:, 1]
    
    # Step 2: Calculate Inverse Probability of Treatment Weight (IPTW)
    weights = np.where(y_treatment == 1, 1.0 / propensity_scores, 1.0 / (1.0 - propensity_scores))
    
    # Step 3: Weighted outcome estimation for ATE
    treated_mask = y_treatment == 1
    weighted_treated = np.sum(weights[treated_mask] * y_outcome[treated_mask]) / np.sum(weights[treated_mask])
    weighted_control = np.sum(weights[~treated_mask] * y_outcome[~treated_mask]) / np.sum(weights[~treated_mask])
    ate = weighted_treated - weighted_control
    
    return {
        'ate': float(ate),
        'propensity_scores': propensity_scores,
        'weights': weights,
        'treated_mean': float(weighted_treated),
        'control_mean': float(weighted_control)
    }
```

### Pattern 2: Production-Ready Intervention Analysis

```python
import logging
import pandas as pd
import numpy as np
from typing import Any, Dict, List
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score

logger = logging.getLogger(__name__)

class InterventionAnalysis:
    """Production implementation of Intervention Analysis using T-Learner CATE estimation."""
    
    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.treatment_model = None
        self.outcome_model = None
        
    def _validate_input(self, data: pd.DataFrame) -> None:
        required_cols = ['treatment', 'outcome', 'features']
        missing = [col for col in required_cols if col not in data.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        if data['treatment'].nunique() != 2:
            raise ValueError("Treatment column must be binary (0 or 1).")
            
    def fit(self, data: pd.DataFrame) -> 'InterventionAnalysis':
        self._validate_input(data)
        X = data['features']
        y_treatment = data['treatment']
        y_outcome = data['outcome']
        
        # T-Learner: Train separate models for treated and control groups
        self.treatment_model = RandomForestRegressor(n_estimators=self.n_estimators, random_state=self.random_state)
        self.outcome_model = RandomForestRegressor(n_estimators=self.n_estimators, random_state=self.random_state)
        
        treated_idx = y_treatment == 1
        control_idx = y_treatment == 0
        
        self.treatment_model.fit(X[treated_idx], y_outcome[treated_idx])
        self.outcome_model.fit(X[control_idx], y_outcome[control_idx])
        
        logger.info("T-Learner models fitted successfully.")
        return self
        
    def predict_cate(self, X: pd.DataFrame) -> np.ndarray:
        if self.treatment_model is None or self.outcome_model is None:
            raise RuntimeError("Model must be fitted before prediction.")
        cate_treated = self.treatment_model.predict(X)
        cate_control = self.outcome_model.predict(X)
        return cate_treated - cate_control
        
    def evaluate(self, data: pd.DataFrame) -> Dict[str, Any]:
        X = data['features']
        cate = self.predict_cate(X)
        mse = np.mean((self.treatment_model.predict(X) - self.outcome_model.predict(X)) ** 2)
        return {'cate_mean': float(np.mean(cate)), 'cate_std': float(np.std(cate)), 'baseline_mse': float(mse)}
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
import matplotlib.pyplot as plt
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import GradientBoostingRegressor
from typing import Dict, Any

def implement_analysis(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Complete implementation of Intervention Analysis.
    
    This example demonstrates:
    - Proper input validation
    - Core algorithm implementation (S-Learner CATE)
    - Error handling
    - Result formatting
    
    Args:
        data: Input DataFrame with required columns
        
    Returns:
        Dictionary with results and metadata
        
    Raises:
        ValueError: If input data is invalid
        
    Example:
        >>> df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        >>> results = implement_analysis(df)
        >>> print(results)
    """
    # Validate inputs
    if data is None or data.empty:
        raise ValueError("Input data cannot be None or empty")
    
    # Generate synthetic data with known heterogeneous treatment effects if not provided
    if 'treatment' not in data.columns or 'outcome' not in data.columns:
        X, y_true = make_regression(n_samples=500, n_features=4, noise=0.5, random_state=42)
        treatment_prob = 1 / (1 + np.exp(-X[:, 0]))
        treatment = np.random.binomial(1, treatment_prob)
        true_effect = 2.0 * X[:, 1]
        outcome = y_true + treatment * true_effect + np.random.normal(0, 0.5, 500)
        data = pd.DataFrame(X, columns=['feat_0', 'feat_1', 'feat_2', 'feat_3'])
        data['treatment'] = treatment
        data['outcome'] = outcome
    
    # Split data
    train_df, test_df = train_test_split(data, test_size=0.2, random_state=42)
    
    # S-Learner: Train one model with treatment as a feature
    feature_cols = [c for c in data.columns if c not in ['treatment', 'outcome']]
    s_learner = GradientBoostingRegressor(n_estimators=100, random_state=42)
    s_learner.fit(train_df[feature_cols], train_df['outcome'])
    
    # Predict outcomes under treatment=1 and treatment=0
    test_features = test_df[feature_cols].copy()
    test_features['treatment'] = 1
    y_pred_treated = s_learner.predict(test_features)
    
    test_features['treatment'] = 0
    y_pred_control = s_learner.predict(test_features)
    
    # Calculate CATE and metrics
    cate_estimated = y_pred_treated - y_pred_control
    mse = mean_squared_error(test_df['outcome'], (y_pred_treated + y_pred_control) / 2)
    r2 = r2_score(test_df['outcome'], (y_pred_treated + y_pred_control) / 2)
    
    # Visualization
    plt.figure(figsize=(10, 6))
    plt.scatter(cate_estimated, np.zeros_like(cate_estimated), alpha=0.6, color='steelblue')
    plt.xlabel('Estimated CATE')
    plt.title('Intervention Analysis: CATE Distribution')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('cate_distribution.png', dpi=150)
    plt.close()
    
    results = {
        'status': 'success',
        'mse': float(mse),
        'r2': float(r2),
        'mean_ate': float(np.mean(cate_estimated)),
        'plot_path': 'cate_distribution.png',
        'sample_predictions': pd.DataFrame({
            'treated_pred': y_pred_treated[:5],
            'control_pred': y_pred_control[:5],
            'cate': cate_estimated[:5]
        }).to_dict(orient='records')
    }
    
    return results

# Usage and testing
if __name__ == "__main__":
    # Create sample data
    sample_data = pd.DataFrame({
        'feat_0': np.random.randn(100),
        'feat_1': np.random.randn(100),
        'feat_2': np.random.randn(100),
        'feat_3': np.random.randn(100),
        'treatment': np.random.binomial(1, 0.5, 100),
        'outcome': np.random.randn(100)
    })
    
    # Run implementation
    results = implement_analysis(sample_data)
    print(f"Status: {results['status']}")
    print(f"MSE: {results['mse']:.4f}, R²: {results['r2']:.4f}")
    print(f"Mean ATE: {results['mean_ate']:.4f}")
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-causal-inference` | Causal Inference techniques | Complementary to this skill |
| `coding-ds-observational-studies` | Observational Studies techniques | Complementary to this skill |
| `coding-ds-randomized-experiments` | Randomized Experiments techniques | Complementary to this skill |

## References

- Official documentation and papers on Intervention Analysis
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
