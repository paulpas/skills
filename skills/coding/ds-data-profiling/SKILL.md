---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: Provides Extracts data profiles, schemas, metadata, and statistical summaries to understand data structure, quality,
  and characteristics at scale
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-data-quality, ds-data-visualization, ds-eda
  role: implementation
  scope: implementation
  triggers: data profiling, metadata extraction, schema analysis, data schema, how do i profile data, data structure, performance
    analysis, optimization
  version: 1.0.0
name: data-profiling
---
# Data Profiling

Comprehensive guide to data profiling in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world exploratory data analysis problems
- Building machine learning pipelines with data profiling
- Implementing best practices for data profiling
- Optimizing model performance using data profiling techniques
- Learning industry-standard approaches to data profiling

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require data profiling rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Data Profiling is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Data Profiling

```python
import pandas as pd
import numpy as np

def basic_data_profiling(df: pd.DataFrame) -> dict:
    """Generate a basic statistical and structural profile of a DataFrame."""
    if df.empty:
        raise ValueError("DataFrame cannot be empty")
    
    profile = {
        'shape': df.shape,
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'missing_percentages': (df.isnull().mean() * 100).round(2).to_dict(),
        'numeric_summary': df.describe().to_dict() if len(df.select_dtypes(include='number').columns) > 0 else {},
        'categorical_summary': {col: df[col].nunique() for col in df.select_dtypes(include='object').columns}
    }
    return profile

# Example usage
if __name__ == "__main__":
    sample_df = pd.DataFrame({
        'age': [25, 30, 35, 40, np.nan],
        'salary': [50000, 60000, 75000, 80000, 90000],
        'department': ['HR', 'IT', 'IT', 'HR', 'Finance']
    })
    results = basic_data_profiling(sample_df)
    print("Profile generated successfully")
    print(f"Missing values: {results['missing_values']}")
```

### Pattern 2: Production-Ready Data Profiling

```python
import logging
import pandas as pd
import numpy as np
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

class DataProfiling:
    """Production implementation of Data Profiling"""
    
    def __init__(self, include_correlations: bool = True, sample_size: int = 10000):
        self.include_correlations = include_correlations
        self.sample_size = sample_size
        logger.info("DataProfiling initialized")
    
    def execute(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Execute Data Profiling on data"""
        if data is None or data.empty:
            raise ValueError("Input data cannot be None or empty")
        
        logger.info(f"Starting profiling on {data.shape[0]} rows and {data.shape[1]} columns")
        
        profile = {
            'metadata': {
                'rows': len(data),
                'columns': len(data.columns),
                'memory_usage_mb': round(data.memory_usage(deep=True).sum() / 1024**2, 2)
            },
            'data_types': data.dtypes.to_dict(),
            'null_counts': data.isnull().sum().to_dict(),
            'null_percentages': (data.isnull().mean() * 100).round(2).to_dict(),
            'unique_counts': data.nunique().to_dict()
        }
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            profile['descriptive_stats'] = data[numeric_cols].describe().to_dict()
            if self.include_correlations:
                profile['correlation_matrix'] = data[numeric_cols].corr().round(3).to_dict()
        
        logger.info("Profiling completed successfully")
        return profile
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
import warnings
warnings.filterwarnings('ignore')

def implement_profiling(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Complete implementation of Data Profiling.
    
    This example demonstrates:
    - Proper input validation
    - Core algorithm implementation
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
        >>> results = implement_profiling(df)
        >>> print(results)
    """
    if data is None or data.empty:
        raise ValueError("Input data cannot be None or empty")
    
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
        
    profiling_results = {
        'status': 'success',
        'shape': data.shape,
        'column_names': list(data.columns),
        'data_types': data.dtypes.to_dict(),
        'missing_values': data.isnull().sum().to_dict(),
        'missing_percentages': (data.isnull().mean() * 100).round(2).to_dict(),
        'unique_values': data.nunique().to_dict(),
        'memory_usage_mb': round(data.memory_usage(deep=True).sum() / 1024**2, 3)
    }
    
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        profiling_results['descriptive_statistics'] = data[numeric_cols].describe().to_dict()
        profiling_results['correlation_matrix'] = data[numeric_cols].corr().round(4).to_dict()
        
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns
    if len(categorical_cols) > 0:
        profiling_results['top_categories'] = {
            col: data[col].value_counts().head(5).to_dict() for col in categorical_cols
        }
        
    return profiling_results

# Usage and testing
if __name__ == "__main__":
    np.random.seed(42)
    sample_data = pd.DataFrame({
        'id': range(100),
        'age': np.random.randint(18, 65, 100),
        'income': np.random.normal(50000, 15000, 100),
        'department': np.random.choice(['Engineering', 'Sales', 'HR', 'Marketing'], 100),
        'rating': np.random.uniform(1.0, 5.0, 100)
    })
    sample_data.loc[np.random.choice(100, 5), 'income'] = np.nan
    
    results = implement_profiling(sample_data)
    print(f"Status: {results['status']}")
    print(f"Processed {results['shape'][0]} rows and {results['shape'][1]} columns")
    print(f"Missing values found: {sum(results['missing_values'].values())}")
    print("Descriptive stats keys:", list(results['descriptive_statistics'].keys()))
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-eda` | Eda techniques | Complementary to this skill |
| `coding-ds-data-quality` | Data Quality techniques | Complementary to this skill |
| `coding-ds-data-visualization` | Data Visualization techniques | Complementary to this skill |

## References

- Official documentation and papers on Data Profiling
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
