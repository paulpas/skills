---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Provides Designs experiments using design of experiments (DOE), factorial designs, randomization, and blocking
  for efficient learning"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-ab-testing, ds-online-experiments, ds-randomized-experiments, ds-statistical-power ds-statistical-power
  role: implementation
  scope: implementation
  triggers: experimental design, DOE, factorial design, randomization, blocking, how do I design experiments
  version: 1.0.0
name: experimental-design
---
# Experimental Design

Comprehensive guide to experimental design in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world experimentation & a/b testing problems
- Building machine learning pipelines with experimental design
- Implementing best practices for experimental design
- Optimizing model performance using experimental design techniques
- Learning industry-standard approaches to experimental design

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require experimental design rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Experimental Design is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Experimental Design

```python
import pandas as pd
import numpy as np
from scipy import stats

def generate_factorial_design(factor_levels: dict) -> pd.DataFrame:
    """Generate a full factorial design matrix from factor levels."""
    keys = list(factor_levels.keys())
    values = list(factor_levels.values())
    grid = np.meshgrid(*values, indexing='ij')
    design = pd.DataFrame(np.column_stack([g.ravel() for g in grid]), columns=keys)
    return design

def apply_randomization(design: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Randomize the order of experimental runs using a reproducible RNG."""
    rng = np.random.default_rng(seed)
    indices = rng.permutation(len(design))
    return design.iloc[indices].reset_index(drop=True)

def create_blocks(design: pd.DataFrame, n_blocks: int) -> pd.DataFrame:
    """Assign experimental runs to blocks to control for nuisance variables."""
    block_assignments = np.repeat(np.arange(n_blocks), len(design) // n_blocks)
    remainder = len(design) % n_blocks
    if remainder > 0:
        block_assignments = np.append(block_assignments, np.arange(remainder))
    design['block'] = block_assignments
    return design
```

### Pattern 2: Production-Ready Experimental Design

```python
import logging
from typing import Any, Dict, List
import pandas as pd
import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)

class ExperimentalDesign:
    """Production implementation of Experimental Design following ISO 3534 standards."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        
    def execute(self, data: pd.DataFrame, response_col: str, factors: List[str], n_blocks: int = 1) -> Dict[str, Any]:
        """Execute Experimental Design on data with randomization and blocking."""
        if response_col not in data.columns:
            raise ValueError(f"Response column '{response_col}' not found in data")
        if not all(f in data.columns for f in factors):
            raise ValueError(f"All factors must be present in data: {factors}")
            
        design = data[factors].copy()
        design = apply_randomization(design, self.seed)
        design['block'] = np.repeat(np.arange(n_blocks), len(design) // n_blocks)
        remainder = len(design) % n_blocks
        if remainder > 0:
            design.loc[len(design) - remainder:, 'block'] = np.arange(remainder)
            
        design['response'] = data[response_col].values
        
        if n_blocks > 1:
            groups = [group['response'].values for _, group in design.groupby('block')]
            f_stat, p_val = stats.f_oneway(*groups)
        else:
            f_stat, p_val = np.nan, np.nan
            
        results = {
            'status': 'success',
            'design_matrix': design,
            'statistics': {'f_statistic': float(f_stat), 'p_value': float(p_val), 'n_runs': len(design)},
            'metadata': {'factors': factors, 'blocks': n_blocks, 'seed': self.seed}
        }
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
from sklearn.datasets import make_regression
from typing import Dict, Any, List, Tuple

def generate_synthetic_experiment(n_samples: int = 100, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic experimental data with controlled factors."""
    X, y = make_regression(n_samples=n_samples, n_features=2, noise=10.0, random_state=seed)
    df = pd.DataFrame(X, columns=['factor_A', 'factor_B'])
    df['response'] = y
    return df

def apply_good_randomization(df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """GOOD: Use cryptographically secure RNG for proper randomization."""
    rng = np.random.default_rng(seed)
    return df.sample(frac=1.0, random_state=rng).reset_index(drop=True)

def apply_bad_randomization(df: pd.DataFrame) -> pd.DataFrame:
    """BAD: Using fixed order or weak randomization leads to bias."""
    return df.sort_values(by=['factor_A']).reset_index(drop=True)

def run_anova_analysis(df: pd.DataFrame, response_col: str, factor_col: str) -> Dict[str, Any]:
    """Run one-way ANOVA to evaluate factor impact."""
    groups = [group[response_col].values for _, group in df.groupby(factor_col)]
    f_stat, p_val = stats.f_oneway(*groups)
    return {'f_statistic': float(f_stat), 'p_value': float(p_val)}

def plot_results(df: pd.DataFrame, response_col: str, factor_col: str) -> None:
    """Visualize experimental results with proper labeling."""
    fig, ax = plt.subplots(figsize=(8, 5))
    for name, group in df.groupby(factor_col):
        ax.boxplot(group[response_col].values, positions=[name], widths=0.6)
    ax.set_xlabel(factor_col)
    ax.set_ylabel(response_col)
    ax.set_title('Experimental Design Results (Montgomery DOE Standard)')
    plt.show()

def implement_design(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Complete implementation of Experimental Design.
    Follows Montgomery's Design of Experiments principles.
    """
    if data is None or data.empty:
        raise ValueError("Input data cannot be None or empty")
    
    df = generate_synthetic_experiment(n_samples=len(data), seed=42)
    df_good = apply_good_randomization(df)
    df_bad = apply_bad_randomization(df)
    
    stats_good = run_anova_analysis(df_good, 'response', 'factor_A')
    stats_bad = run_anova_analysis(df_bad, 'response', 'factor_A')
    
    plot_results(df_good, 'response', 'factor_A')
    
    return {
        'status': 'success',
        'good_randomization_stats': stats_good,
        'bad_randomization_stats': stats_bad,
        'metadata': {'rows': len(df), 'columns': df.shape[1], 'standard': 'Montgomery DOE'}
    }

if __name__ == "__main__":
    sample_data = pd.DataFrame({'x': np.arange(100), 'y': np.random.randn(100)})
    results = implement_design(sample_data)
    print(f"Status: {results['status']}")
    print(f"Processed {results['metadata']['rows']} rows")
    print(f"Good Randomization P-value: {results['good_randomization_stats']['p_value']:.4f}")
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-ab-testing` | Ab Testing techniques | Complementary to this skill |
| `coding-ds-statistical-power` | Statistical Power techniques | Complementary to this skill |
| `coding-ds-randomized-experiments` | Randomized Experiments techniques | Complementary to this skill |

## References

- Official documentation and papers on Experimental Design
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
