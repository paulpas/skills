---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: Implements hypothesis testing including t-tests, chi-square tests, p-values, and statistical significance evaluation
  for data-driven decisions
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-ab-testing, ds-bayesian-inference, ds-confidence-intervals, ds-maximum-likelihood
  role: implementation
  scope: implementation
  triggers: hypothesis testing, t-test, chi-square, p-value, statistical significance, how do i test hypotheses, unit tests,
    testing
  version: 1.0.0
name: hypothesis-testing
---
# Hypothesis Testing

Comprehensive guide to hypothesis testing in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world statistical inference problems
- Building machine learning pipelines with hypothesis testing
- Implementing best practices for hypothesis testing
- Optimizing model performance using hypothesis testing techniques
- Learning industry-standard approaches to hypothesis testing

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require hypothesis testing rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Hypothesis Testing is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Hypothesis Testing

```python
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any, Tuple

def perform_independent_t_test(
    group_a: np.ndarray, 
    group_b: np.ndarray, 
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    Perform an independent two-sample t-test to compare means.
    
    Args:
        group_a: Array of values for the first group
        group_b: Array of values for the second group
        alpha: Significance level for the test
        
    Returns:
        Dictionary containing t-statistic, p-value, and conclusion
    """
    if len(group_a) < 2 or len(group_b) < 2:
        raise ValueError("Each group must contain at least two observations")
        
    t_stat, p_value = stats.ttest_ind(group_a, group_b, equal_var=False)
    is_significant = p_value < alpha
    
    return {
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "significant": bool(is_significant),
        "alpha": alpha,
        "conclusion": "Reject null hypothesis" if is_significant else "Fail to reject null hypothesis"
    }
```

### Pattern 2: Production-Ready Hypothesis Testing

```python
import logging
import numpy as np
import pandas as pd
from scipy import stats
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class HypothesisTestingEngine:
    """Production-grade engine for statistical hypothesis testing."""
    
    def __init__(self, alpha: float = 0.05, verbose: bool = False):
        self.alpha = alpha
        self.verbose = verbose
        self.results_log: List[Dict[str, Any]] = []
        
    def run_chi_square(self, observed: List[int], expected: List[int]) -> Dict[str, Any]:
        """Execute chi-square goodness of fit test."""
        if len(observed) != len(expected):
            raise ValueError("Observed and expected arrays must have the same length")
        if any(x < 0 for x in observed) or any(x < 0 for x in expected):
            raise ValueError("Counts cannot be negative")
            
        chi2_stat, p_value = stats.chisquare(f_obs=observed, f_exp=expected)
        result = {
            "test": "chi_square",
            "statistic": float(chi2_stat),
            "p_value": float(p_value),
            "significant": bool(p_value < self.alpha),
            "timestamp": pd.Timestamp.now().isoformat()
        }
        self.results_log.append(result)
        if self.verbose:
            logger.info(f"Chi-square test completed: p={p_value:.4f}")
        return result
        
    def run_all_tests(self, data: pd.DataFrame, target_col: str, feature_col: str) -> Dict[str, Any]:
        """Run appropriate tests based on data types."""
        if target_col not in data.columns or feature_col not in data.columns:
            raise KeyError(f"Columns '{target_col}' and '{feature_col}' must exist in data")
            
        results = {}
        if data[feature_col].dtype in ['float64', 'int64']:
            groups = data.groupby(feature_col)[target_col].apply(list)
            if len(groups) >= 2:
                results['anova'] = stats.f_oneway(*groups.values())._asdict()
        else:
            contingency = pd.crosstab(data[target_col], data[feature_col])
            results['chi2'] = stats.chi2_contingency(contingency)._asdict()
            
        return results
```

## Best Practices

- ✅ Always validate your implementation on test data
- ✅ Document your assumptions and methodology
- ✅ Use version control for reproducibility
- ✅ Monitor performance metrics in production
- ✅ Periodically review and update your approach
- ✅ Test with edge cases and outliers
- ✅ Log all significant operations for debugging

### BAD vs GOOD Example

```python
# BAD: Bypassing error handling, using magic numbers, and missing type hints
def bad_test(data):
    t, p = stats.ttest_ind(data['a'], data['b'])
    return p < 0.05  # Hardcoded threshold, no validation

# GOOD: Proper validation, type hints, configurable alpha, and clear return structure
def good_test(group_a: np.ndarray, group_b: np.ndarray, alpha: float = 0.05) -> Dict[str, Any]:
    if len(group_a) < 2 or len(group_b) < 2:
        raise ValueError("Insufficient samples for statistical testing")
    _, p_value = stats.ttest_ind(group_a, group_b, equal_var=False)
    return {
        "p_value": float(p_value),
        "significant": bool(p_value < alpha),
        "alpha_used": alpha
    }
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
from scipy import stats
from typing import Dict, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

def generate_sample_data(n_samples: int = 200, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic dataset for hypothesis testing demonstration."""
    np.random.seed(seed)
    df = pd.DataFrame({
        'control_group': np.random.normal(loc=50, scale=10, size=n_samples),
        'treatment_group': np.random.normal(loc=55, scale=10, size=n_samples),
        'category': np.random.choice(['A', 'B', 'C'], size=n_samples)
    })
    return df

def run_comprehensive_tests(df: pd.DataFrame) -> Dict[str, Any]:
    """Execute multiple hypothesis tests and return structured results."""
    results: Dict[str, Any] = {}
    
    # 1. Independent t-test
    t_stat, t_pval = stats.ttest_ind(df['control_group'], df['treatment_group'], equal_var=False)
    results['t_test'] = {
        'statistic': float(t_stat),
        'p_value': float(t_pval),
        'significant': bool(t_pval < 0.05),
        'interpretation': 'Significant difference in means' if t_pval < 0.05 else 'No significant difference'
    }
    
    # 2. Chi-square test for categorical independence
    contingency_table = pd.crosstab(df['category'], df['treatment_group'] > 52)
    chi2, chi_p, dof, expected = stats.chi2_contingency(contingency_table)
    results['chi_square'] = {
        'statistic': float(chi2),
        'p_value': float(chi_p),
        'degrees_of_freedom': int(dof),
        'significant': bool(chi_p < 0.05)
    }
    
    return results

def visualize_results(df: pd.DataFrame, results: Dict[str, Any]) -> None:
    """Plot distributions and test outcomes."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    axes[0].hist(df['control_group'], bins=20, alpha=0.5, label='Control', color='blue')
    axes[0].hist(df['treatment_group'], bins=20, alpha=0.5, label='Treatment', color='red')
    axes[0].set_title('Group Distributions')
    axes[0].set_xlabel('Value')
    axes[0].set_ylabel('Frequency')
    axes[0].legend()
    
    axes[1].bar(['Control', 'Treatment'], 
                [df['control_group'].mean(), df['treatment_group'].mean()],
                color=['blue', 'red'], alpha=0.7)
    axes[1].set_title('Mean Comparison')
    axes[1].set_ylabel('Mean Value')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    sample_df = generate_sample_data()
    test_results = run_comprehensive_tests(sample_df)
    visualize_results(sample_df, test_results)
    print("Test Results:", test_results)
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-confidence-intervals` | Confidence Intervals techniques | Complementary to this skill |
| `coding-ds-maximum-likelihood` | Maximum Likelihood techniques | Complementary to this skill |
| `coding-ds-ab-testing` | Ab Testing techniques | Complementary to this skill |

## References

- Official documentation and papers on Hypothesis Testing
- Industry best practices and standards
- Implementation examples from the scikit-learn, TensorFlow, and PyTorch libraries
- American Statistical Association (ASA) Statement on p-Values and Statistical Significance
- DRY (Don't Repeat Yourself) principle for test automation and result reporting

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
