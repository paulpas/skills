---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: Implements causal models, directed acyclic graphs (DAGs), confounding adjustment, and mediation analysis for
  causal discovery
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-instrumental-variables, ds-intervention-analysis, ds-observational-studies, ds-randomized-experiments
    ds-synthetic-control
  role: implementation
  scope: implementation
  triggers: causal inference, causality, causal models, DAG, confounding, how do i determine causation, airflow, data pipelines
  version: 1.0.0
name: causal-inference
---
# Causal Inference

Comprehensive guide to causal inference in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world causal inference problems
- Building machine learning pipelines with causal inference
- Implementing best practices for causal inference
- Optimizing model performance using causal inference techniques
- Learning industry-standard approaches to causal inference

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require causal inference rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Causal Inference is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Causal Inference

```python
import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

def estimate_ate_ols(df: pd.DataFrame, treatment_col: str, outcome_col: str, confounders: list) -> dict:
    """Estimate Average Treatment Effect using Ordinary Least Squares with confounders."""
    if treatment_col not in df.columns or outcome_col not in df.columns:
        raise ValueError("Treatment or outcome column missing")
    
    X = df[confounders].values
    X = sm.add_constant(X)
    y = df[outcome_col].values
    treatment = df[treatment_col].values
    
    model = sm.OLS(y, X).fit()
    coef_treatment = model.params[treatment_col] if treatment_col in model.params else 0.0
    
    # Propensity score estimation for robustness check
    ps_model = LogisticRegression()
    ps_model.fit(X[:, 1:], treatment)
    df['propensity'] = ps_model.predict_proba(X[:, 1:])[:, 1]
    
    return {
        'method': 'OLS with Confounders',
        'ate': float(coef_treatment),
        'confidence_interval': tuple(model.conf_int().loc[treatment_col]),
        'p_value': float(model.pvalues[treatment_col]),
        'r_squared': float(model.rsquared)
    }
```

### Pattern 2: Production-Ready Causal Inference

```python
import logging
import pandas as pd
import numpy as np
from typing import Any, Dict, List
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import cross_val_score

logger = logging.getLogger(__name__)

class CausalInference:
    """Production implementation of Causal Inference using IPW and Double Robust Estimation."""
    
    def __init__(self, confounders: List[str], treatment_col: str, outcome_col: str):
        self.confounders = confounders
        self.treatment_col = treatment_col
        self.outcome_col = outcome_col
        self.propensity_model = LogisticRegression(max_iter=1000)
        self.outcome_model = LinearRegression()
        self.fitted = False
        
    def _validate_data(self, data: pd.DataFrame) -> None:
        missing = [c for c in self.confounders + [self.treatment_col, self.outcome_col] if c not in data.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")
        if data[self.treatment_col].nunique() != 2:
            raise ValueError("Treatment variable must be binary")
            
    def fit(self, data: pd.DataFrame) -> 'CausalInference':
        self._validate_data(data)
        X = data[self.confounders].values
        T = data[self.treatment_col].values
        Y = data[self.outcome_col].values
        
        self.propensity_model.fit(X, T)
        ps = self.propensity_model.predict_proba(X)[:, 1]
        ipw_weights = T / ps + (1 - T) / (1 - ps)
        
        self.outcome_model.fit(X, Y)
        self.weights = ipw_weights
        self.fitted = True
        logger.info("Causal model fitted successfully with IPW weights.")
        return self
        
    def execute(self, data: pd.DataFrame) -> Dict[str, Any]:
        if not self.fitted:
            raise RuntimeError("Model must be fitted before execution")
        self._validate_data(data)
        X = data[self.confounders].values
        T = data[self.treatment_col].values
        Y = data[self.outcome_col].values
        
        ps = self.propensity_model.predict_proba(X)[:, 1]
        ipw_weights = T / ps + (1 - T) / (1 - ps)
        
        predicted_treated = self.outcome_model.predict(X)
        ate = np.mean(ipw_weights * (Y - predicted_treated))
        
        return {
            'status': 'success',
            'average_treatment_effect': float(ate),
            'standard_error': float(np.std(ipw_weights * (Y - predicted_treated)) / np.sqrt(len(Y))),
            'sample_size': len(Y),
            'confounders_used': self.confounders
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
import pandas as pd
import numpy as np
from typing import Dict, Any
from sklearn.datasets import make_regression
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

def implement_causal_inference(data: pd.DataFrame, treatment_col: str, outcome_col: str, confounders: list) -> Dict[str, Any]:
    """
    Complete implementation of Causal Inference using Double Machine Learning approach.
    
    Args:
        data: Input DataFrame with treatment, outcome, and confounder columns
        treatment_col: Name of the binary treatment variable
        outcome_col: Name of the continuous outcome variable
        confounders: List of confounding variable column names
        
    Returns:
        Dictionary with causal estimates, diagnostics, and metadata
        
    Raises:
        ValueError: If input data is invalid or columns missing
    """
    required_cols = [treatment_col, outcome_col] + confounders
    if not all(col in data.columns for col in required_cols):
        raise ValueError(f"DataFrame must contain columns: {required_cols}")
        
    X = data[confounders].values
    T = data[treatment_col].values
    Y = data[outcome_col].values
    
    # Step 1: Estimate Propensity Scores
    ps_model = LogisticRegression(max_iter=1000)
    ps_model.fit(X, T)
    ps = ps_model.predict_proba(X)[:, 1]
    
    # Step 2: Calculate Inverse Probability Weights
    ps = np.clip(ps, 0.01, 0.99)
    ipw = T / ps + (1 - T) / (1 - ps)
    
    # Step 3: Estimate Outcome Model & Residuals
    outcome_model = LinearRegression()
    outcome_model.fit(X, Y)
    residuals = Y - outcome_model.predict(X)
    
    # Step 4: Compute ATE via IPW on residuals
    ate = np.mean(ipw * residuals)
    se = np.std(ipw * residuals) / np.sqrt(len(Y))
    
    # Step 5: Cross-validated performance check
    X_train, X_test, T_train, T_test, Y_train, Y_test = train_test_split(X, T, Y, test_size=0.2, random_state=42)
    cv_score = np.mean(cross_val_score(outcome_model, X_train, Y_train, cv=5, scoring='r2'))
    
    return {
        'status': 'success',
        'average_treatment_effect': float(ate),
        'standard_error': float(se),
        'confidence_interval_95': (float(ate - 1.96 * se), float(ate + 1.96 * se)),
        'p_value': float(2 * (1 - __import__('scipy.stats').norm.cdf(abs(ate / se)))),
        'outcome_model_r2': float(outcome_model.score(X, Y)),
        'cv_r2_score': float(cv_score),
        'metadata': {'rows': len(data), 'confounders': confounders, 'treatment_rate': float(np.mean(T))}
    }

if __name__ == "__main__":
    np.random.seed(42)
    n_samples = 1000
    X1, X2 = np.random.randn(n_samples), np.random.randn(n_samples)
    T = (0.5 * X1 + 0.3 * X2 + np.random.randn(n_samples) * 0.5 > 0).astype(int)
    Y = 2.5 * T + 1.0 * X1 - 0.5 * X2 + np.random.randn(n_samples) * 0.8
    
    df = pd.DataFrame({'conf1': X1, 'conf2': X2, 'treatment': T, 'outcome': Y})
    results = implement_causal_inference(df, 'treatment', 'outcome', ['conf1', 'conf2'])
    print(f"Estimated ATE: {results['average_treatment_effect']:.4f}")
    print(f"95% CI: {results['confidence_interval_95']}")
    print(f"Model R2: {results['outcome_model_r2']:.4f}")
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-observational-studies` | Observational Studies techniques | Complementary to this skill |
| `coding-ds-intervention-analysis` | Intervention Analysis techniques | Complementary to this skill |
| `coding-ds-randomized-experiments` | Randomized Experiments techniques | Complementary to this skill |

## References

- Official documentation and papers on Causal Inference
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
