---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Analyzes statistical power, sample size determination, effect size estimation, and Type I/Type II error control"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-ab-testing, ds-experimental-design, ds-hypothesis-testing
  role: implementation
  scope: implementation
  triggers: statistical power, power analysis, sample size, effect size, Type I error, Type II error
  version: 1.0.0
name: statistical-power
---
# Statistical Power

Comprehensive guide to statistical power in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world experimentation & a/b testing problems
- Building machine learning pipelines with statistical power
- Implementing best practices for statistical power
- Optimizing model performance using statistical power techniques
- Learning industry-standard approaches to statistical power

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require statistical power rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Statistical Power is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Statistical Power

```python
import numpy as np
from statsmodels.stats.power import TTestPower

def calculate_basic_power(effect_size: float, sample_size: int, alpha: float = 0.05) -> float:
    """Calculate statistical power for a two-sample t-test."""
    if sample_size <= 0 or alpha <= 0 or alpha >= 1:
        raise ValueError("Invalid parameters: sample_size must be > 0, alpha in (0, 1)")
    
    power_analysis = TTestPower()
    power = power_analysis.power(effect_size=effect_size, nobs=sample_size, alpha=alpha)
    return float(np.clip(power, 0.0, 1.0))

# Example usage
if __name__ == "__main__":
    es: float = 0.5  # Medium effect size (Cohen's d)
    n: int = 50      # Sample size per group
    alpha: float = 0.05
    calculated_power: float = calculate_basic_power(es, n, alpha)
    print(f"Statistical Power: {calculated_power:.4f}")
```

### Pattern 2: Production-Ready Statistical Power

```python
import logging
import numpy as np
import pandas as pd
from typing import Any, Dict, Literal
from statsmodels.stats.power import TTestPower

logger = logging.getLogger(__name__)

class StatisticalPowerAnalyzer:
    """Production-grade statistical power analysis tool."""
    
    def __init__(self, alpha: float = 0.05, alternative: Literal['two-sided', 'larger', 'smaller'] = 'two-sided') -> None:
        self.alpha: float = alpha
        self.alternative: str = alternative
        self.ttest: TTestPower = TTestPower()
        
    def calculate_power(self, effect_size: float, sample_size: int) -> float:
        """Calculate power given effect size and sample size."""
        if sample_size <= 0 or effect_size < 0:
            raise ValueError("Sample size must be positive and effect size non-negative")
        return float(self.ttest.power(effect_size=effect_size, nobs=sample_size, alpha=self.alpha))
        
    def calculate_sample_size(self, effect_size: float, target_power: float) -> int:
        """Calculate required sample size for target power."""
        if target_power <= 0 or target_power >= 1:
            raise ValueError("Target power must be between 0 and 1")
        nobs: float = self.ttest.solve_power(effect_size=effect_size, power=target_power, alpha=self.alpha)
        return int(np.ceil(nobs))
        
    def execute(self, data: pd.DataFrame, target_power: float = 0.8) -> Dict[str, Any]:
        """Execute power analysis on provided data."""
        if data.empty:
            raise ValueError("Input DataFrame cannot be empty")
            
        group_a: pd.Series = data['group_a'].dropna()
        group_b: pd.Series = data['group_b'].dropna()
        pooled_std: float = np.sqrt(((len(group_a) - 1) * group_a.var() + (len(group_b) - 1) * group_b.var()) / (len(group_a) + len(group_b) - 2))
        effect_size: float = abs(group_a.mean() - group_b.mean()) / pooled_std if pooled_std > 0 else 0.0
        
        current_power: float = self.calculate_power(effect_size, len(group_a))
        required_n: int = self.calculate_sample_size(effect_size, target_power)
        
        logger.info(f"Calculated effect size: {effect_size:.4f}, Current power: {current_power:.4f}")
        return {
            'effect_size': float(effect_size),
            'current_power': float(current_power),
            'required_sample_size': required_n,
            'target_power': target_power,
            'alpha': self.alpha
        }
```

### Pattern 3: BAD vs GOOD Implementation

```python
# BAD: Hardcoded values, no validation, ignores statistical assumptions
def bad_power_calc(data):
    return 0.8  # Magic number, no calculation

# GOOD: Parameterized, validated, uses established statistical library
def good_power_calc(effect_size: float, n: int, alpha: float = 0.05) -> float:
    if n <= 0 or not (0 < alpha < 1):
        raise ValueError("Invalid parameters")
    from statsmodels.stats.power import TTestPower
    return float(TTestPower().power(effect_size=effect_size, nobs=n, alpha=alpha))
```

## Best Practices

- ✅ Always validate your implementation on test data
- ✅ Document your assumptions and methodology
- ✅ Use version control for reproducibility
- ✅ Monitor performance metrics in production
- ✅ Periodically review and update your approach
- ✅ Test with edge cases and outliers
- ✅ Log all significant operations for debugging
- ✅ Follow the DRY (Don't Repeat Yourself) principle to avoid duplicating power calculation logic across projects

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
from sklearn.datasets import make_classification
from statsmodels.stats.power import TTestPower
import matplotlib.pyplot as plt

def perform_power_analysis(data: pd.DataFrame, target_power: float = 0.8, alpha: float = 0.05) -> Dict[str, Any]:
    """
    Complete implementation of Statistical Power analysis.
    
    Args:
        data: DataFrame with 'feature' and 'target' columns
        target_power: Desired statistical power (default 0.8)
        alpha: Significance level (default 0.05)
        
    Returns:
        Dictionary with power metrics and recommendations
    """
    if data is None or data.empty:
        raise ValueError("Input data cannot be None or empty")
    if 'feature' not in data.columns or 'target' not in data.columns:
        raise ValueError("DataFrame must contain 'feature' and 'target' columns")
        
    group_0: pd.Series = data.loc[data['target'] == 0, 'feature']
    group_1: pd.Series = data.loc[data['target'] == 1, 'feature']
    
    pooled_std: float = np.sqrt(((len(group_0) - 1) * group_0.var() + (len(group_1) - 1) * group_1.var()) / (len(group_0) + len(group_1) - 2))
    effect_size: float = abs(group_0.mean() - group_1.mean()) / pooled_std if pooled_std > 0 else 0.0
    
    power_calc: TTestPower = TTestPower()
    current_power: float = power_calc.power(effect_size=effect_size, nobs=len(group_0), alpha=alpha)
    required_n: int = int(np.ceil(power_calc.solve_power(effect_size=effect_size, power=target_power, alpha=alpha)))
    
    return {
        'effect_size': float(effect_size),
        'current_power': float(current_power),
        'required_sample_size': required_n,
        'current_sample_size': len(group_0),
        'alpha': alpha,
        'target_power': target_power
    }

if __name__ == "__main__":
    X, y = make_classification(n_samples=200, n_features=1, n_informative=1, 
                               n_redundant=0, n_classes=2, random_state=42, flip_y=0.1)
    df: pd.DataFrame = pd.DataFrame({'feature': X.flatten(), 'target': y})
    
    results: Dict[str, Any] = perform_power_analysis(df)
    print(f"Effect Size (Cohen's d): {results['effect_size']:.4f}")
    print(f"Current Power: {results['current_power']:.4f}")
    print(f"Required Sample Size for 80% Power: {results['required_sample_size']}")
    
    powers: list[float] = []
    sample_sizes: range = range(20, 200, 5)
    for n in sample_sizes:
        p: float = TTestPower().power(effect_size=results['effect_size'], nobs=n, alpha=results['alpha'])
        powers.append(p)
        
    plt.figure(figsize=(8, 5))
    plt.plot(sample_sizes, powers, marker='o', label='Power Curve')
    plt.axhline(y=0.8, color='r', linestyle='--', label='Target Power (0.8)')
    plt.axvline(x=results['required_sample_size'], color='g', linestyle='--', label=f'Required N ({results["required_sample_size"]})')
    plt.xlabel('Sample Size per Group')
    plt.ylabel('Statistical Power')
    plt.title('Statistical Power Analysis')
    plt.legend()
    plt.grid(True)
    plt.show()
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-ab-testing` | Ab Testing techniques | Complementary to this skill |
| `coding-ds-hypothesis-testing` | Hypothesis Testing techniques | Complementary to this skill |
| `coding-ds-experimental-design` | Experimental Design techniques | Complementary to this skill |

## References

- Official documentation and papers on Statistical Power
- Industry best practices and standards
- Implementation examples from the scikit-learn, TensorFlow, and PyTorch libraries
- Statistical Power Analysis for the Behavioral Sciences (Cohen, 1988)
- APA Publication Manual guidelines for reporting effect sizes and power

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
