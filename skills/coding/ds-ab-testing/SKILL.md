---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: Provides Designs and analyzes A/B tests including hypothesis testing, power analysis, sample size calculation,
  and statistical significance evaluation
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-classification-metrics, ds-experimental-design, ds-hypothesis-testing, ds-metrics-and-kpis ds-statistical-power
  role: implementation
  scope: implementation
  triggers: A/B testing, A/B test, statistical test, power analysis, sample size, how do I design tests, unit tests, testing
  version: 1.0.0
name: ab-testing
---
# A/B Testing

Comprehensive guide to a/b testing in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world experimentation & a/b testing problems
- Building machine learning pipelines with a/b testing
- Implementing best practices for a/b testing
- Optimizing model performance using a/b testing techniques
- Learning industry-standard approaches to a/b testing

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require a/b testing rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

A/B Testing is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic A/B Testing

```python
import pandas as pd
import numpy as np
from scipy import stats

def run_basic_ab_test(group_a: pd.Series, group_b: pd.Series, alpha: float = 0.05) -> dict:
    """
    Perform a two-sample t-test to compare means between two groups.
    Returns p-value, confidence interval, and effect size.
    """
    if len(group_a) < 2 or len(group_b) < 2:
        raise ValueError("Each group must contain at least 2 observations.")

    t_stat, p_value = stats.ttest_ind(group_a, group_b, equal_var=False)
    mean_diff = group_b.mean() - group_a.mean()
    pooled_std = np.sqrt(((len(group_a) - 1) * group_a.var() + (len(group_b) - 1) * group_b.var()) / (len(group_a) + len(group_b) - 2))
    cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0.0

    se_diff = np.sqrt(group_a.var()/len(group_a) + group_b.var()/len(group_b))
    ci_lower = mean_diff - stats.t.ppf(1 - alpha / 2, df=len(group_a) + len(group_b) - 2) * se_diff
    ci_upper = mean_diff + stats.t.ppf(1 - alpha / 2, df=len(group_a) + len(group_b) - 2) * se_diff

    return {
        "p_value": float(p_value),
        "significant": bool(p_value < alpha),
        "mean_difference": float(mean_diff),
        "confidence_interval": (float(ci_lower), float(ci_upper)),
        "cohens_d": float(cohens_d),
        "group_a_mean": float(group_a.mean()),
        "group_b_mean": float(group_b.mean())
    }
```

### Pattern 2: Production-Ready A/B Testing

```python
import logging
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.power import TTestIndPower
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class ABTestAnalyzer:
    """Production-grade A/B test analyzer with power analysis and validation."""
    
    def __init__(self, alpha: float = 0.05, min_effect_size: float = 0.2):
        self.alpha = alpha
        self.min_effect_size = min_effect_size
        
    def validate_data(self, df: pd.DataFrame, group_col: str, metric_col: str) -> None:
        if df.empty:
            raise ValueError("Input DataFrame is empty.")
        if group_col not in df.columns or metric_col not in df.columns:
            raise ValueError(f"Missing required columns: {group_col}, {metric_col}")
        if df[metric_col].dtype not in [np.float64, np.int64]:
            raise ValueError("Metric column must be numeric.")
            
    def analyze(self, df: pd.DataFrame, group_col: str, metric_col: str) -> Dict[str, Any]:
        self.validate_data(df, group_col, metric_col)
        group_a = df.loc[df[group_col] == 0, metric_col].dropna()
        group_b = df.loc[df[group_col] == 1, metric_col].dropna()
        
        if len(group_a) < 30 or len(group_b) < 30:
            logger.warning("Sample sizes below 30. Results may be unreliable.")
            
        t_stat, p_value = stats.ttest_ind(group_a, group_b, equal_var=False)
        mean_diff = group_b.mean() - group_a.mean()
        pooled_std = np.sqrt(((len(group_a) - 1) * group_a.var() + (len(group_b) - 1) * group_b.var()) / (len(group_a) + len(group_b) - 2))
        cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0.0
        
        power_analysis = TTestIndPower()
        required_n = power_analysis.solve_power(effect_size=abs(cohens_d), alpha=self.alpha, power=0.8, ratio=1.0)
        
        return {
            "p_value": float(p_value),
            "significant": bool(p_value < self.alpha),
            "mean_difference": float(mean_diff),
            "effect_size_cohens_d": float(cohens_d),
            "required_sample_size_per_group": int(np.ceil(required_n)),
            "actual_sample_sizes": {"group_a": len(group_a), "group_b": len(group_b)},
            "status": "pass" if p_value < self.alpha and abs(cohens_d) >= self.min_effect_size else "inconclusive"
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
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.power import TTestIndPower
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def generate_synthetic_ab_data(n_per_group: int = 500, 
                               mean_a: float = 100.0, 
                               mean_b: float = 105.0, 
                               std: float = 25.0) -> pd.DataFrame:
    """Generate synthetic A/B test data with known parameters."""
    np.random.seed(42)
    group_a = np.random.normal(mean_a, std, n_per_group)
    group_b = np.random.normal(mean_b, std, n_per_group)
    df = pd.DataFrame({
        'group': [0] * n_per_group + [1] * n_per_group,
        'metric': np.concatenate([group_a, group_b])
    })
    return df

def run_ab_test(df: pd.DataFrame, group_col: str = 'group', metric_col: str = 'metric', alpha: float = 0.05) -> dict:
    """Execute A/B test analysis and return comprehensive results."""
    group_a = df.loc[df[group_col] == 0, metric_col].dropna()
    group_b = df.loc[df[group_col] == 1, metric_col].dropna()
    
    t_stat, p_value = stats.ttest_ind(group_a, group_b, equal_var=False)
    mean_diff = group_b.mean() - group_a.mean()
    pooled_std = np.sqrt(((len(group_a) - 1) * group_a.var() + (len(group_b) - 1) * group_b.var()) / (len(group_a) + len(group_b) - 2))
    cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0.0
    
    power = TTestIndPower()
    required_n = power.solve_power(effect_size=abs(cohens_d), alpha=alpha, power=0.8, ratio=1.0)
    
    return {
        "p_value": float(p_value),
        "significant": bool(p_value < alpha),
        "mean_difference": float(mean_diff),
        "effect_size": float(cohens_d),
        "required_n_per_group": int(np.ceil(required_n)),
        "actual_n": {"a": len(group_a), "b": len(group_b)}
    }

def visualize_results(df: pd.DataFrame, results: dict, save_path: str = "ab_test_results.png"):
    """Plot distribution of both groups and highlight significance."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    axes[0].hist(df.loc[df['group'] == 0, 'metric'], bins=30, alpha=0.5, label='Control (A)', color='blue')
    axes[0].hist(df.loc[df['group'] == 1, 'metric'], bins=30, alpha=0.5, label='Variant (B)', color='orange')
    axes[0].set_title('Metric Distribution by Group')
    axes[0].set_xlabel('Metric Value')
    axes[0].set_ylabel('Frequency')
    axes[0].legend()
    
    axes[1].bar(['Control Mean', 'Variant Mean', 'Difference'], 
                [df.loc[df['group']==0, 'metric'].mean(), 
                 df.loc[df['group']==1, 'metric'].mean(), 
                 results['mean_difference']], 
                color=['blue', 'orange', 'green'])
    axes[1].set_title('Group Means & Difference')
    axes[1].set_ylabel('Metric Value')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()
    logging.info(f"Visualization saved to {save_path}")

if __name__ == "__main__":
    # 1. Generate data
    df = generate_synthetic_ab_data(n_per_group=500, mean_a=100.0, mean_b=105.0, std=25.0)
    logging.info(f"Generated {len(df)} samples")
    
    # 2. Run analysis
    results = run_ab_test(df)
    logging.info(f"P-value: {results['p_value']:.4f} | Significant: {results['significant']}")
    logging.info(f"Effect Size (Cohen's d): {results['effect_size']:.3f}")
    logging.info(f"Required sample size per group for 80% power: {results['required_n_per_group']}")
    
    # 3. Visualize
    visualize_results(df, results)
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-hypothesis-testing` | Hypothesis Testing techniques | Complementary to this skill |
| `coding-ds-experimental-design` | Experimental Design techniques | Complementary to this skill |
| `coding-ds-statistical-power` | Statistical Power techniques | Complementary to this skill |

## References

- Official documentation and papers on A/B Testing
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
