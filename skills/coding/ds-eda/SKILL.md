---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Provides Performs exploratory data analysis using summary statistics, distributions, correlations, and descriptive
  methods to understand dataset characteristic"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-correlation-analysis, ds-data-profiling, ds-data-visualization, ds-dimensionality-reduction ds-missing-data
  role: implementation
  scope: implementation
  triggers: exploratory data analysis, EDA, summary statistics, distributions, data exploration, how do i explore data
  version: 1.0.0
name: eda
---
# Exploratory Data Analysis

Comprehensive guide to exploratory data analysis in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world exploratory data analysis problems
- Building machine learning pipelines with exploratory data analysis
- Implementing best practices for exploratory data analysis
- Optimizing model performance using exploratory data analysis techniques
- Learning industry-standard approaches to exploratory data analysis

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require exploratory data analysis rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Exploratory Data Analysis is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Exploratory Data Analysis

```python
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

def perform_basic_eda(df: pd.DataFrame) -> dict:
    """Perform basic exploratory data analysis on a DataFrame."""
    if df.empty:
        raise ValueError("DataFrame cannot be empty")
    
    # Summary statistics
    summary = df.describe().to_dict()
    
    # Correlation matrix for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number])
    corr_matrix = numeric_cols.corr().to_dict() if not numeric_cols.empty else {}
    
    # Missing values count
    missing = df.isnull().sum().to_dict()
    
    # Distribution skewness for numeric columns
    skewness = {col: float(stats.skew(df[col].dropna())) for col in numeric_cols.columns}
    
    return {
        'summary': summary,
        'correlations': corr_matrix,
        'missing_values': missing,
        'skewness': skewness
    }

# BAD vs GOOD Example
# BAD: Ignoring data types and missing values
# bad_results = df.describe().to_dict()
# GOOD: Explicit type filtering, missing value tracking, and statistical validation
# good_results = perform_basic_eda(df)
```

### Pattern 2: Production-Ready Exploratory Data Analysis

```python
import logging
import pandas as pd
import numpy as np
from typing import Any, Dict, List
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class ExploratoryDataAnalysis:
    """Production implementation of Exploratory Data Analysis"""
    
    def __init__(self, log_level: int = logging.INFO):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        self.scaler = StandardScaler()
        
    def execute(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Execute Exploratory Data Analysis on data"""
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
        if data.empty:
            raise ValueError("Input DataFrame is empty")
            
        results = {
            'shape': data.shape,
            'dtypes': data.dtypes.astype(str).to_dict(),
            'missing_counts': data.isnull().sum().to_dict(),
            'missing_pct': (data.isnull().sum() / len(data) * 100).to_dict(),
            'numeric_summary': data.describe().to_dict(),
            'categorical_counts': {}
        }
        
        for col in data.select_dtypes(include=['object', 'category']).columns:
            results['categorical_counts'][col] = data[col].value_counts().to_dict()
            
        numeric_data = data.select_dtypes(include=[np.number])
        if not numeric_data.empty:
            results['correlation_matrix'] = numeric_data.corr().to_dict()
            
        self.logger.info(f"EDA completed on {data.shape[0]} rows and {data.shape[1]} columns")
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
import seaborn as sns
from sklearn.datasets import load_wine
from typing import Dict, Any

def run_comprehensive_eda(dataset_name: str = "wine") -> Dict[str, Any]:
    """
    Run comprehensive EDA on a sample dataset.
    Demonstrates data loading, cleaning, statistical analysis, and visualization.
    """
    # Load real dataset
    if dataset_name == "wine":
        data = load_wine()
        df = pd.DataFrame(data.data, columns=data.feature_names)
        df['target'] = data.target
    else:
        df = pd.DataFrame(np.random.randn(100, 5), columns=['A', 'B', 'C', 'D', 'E'])
        df['target'] = np.random.choice([0, 1], 100)
        
    # Basic profiling
    profile = {
        'shape': df.shape,
        'memory_usage': df.memory_usage(deep=True).sum(),
        'missing_values': int(df.isnull().sum().sum()),
        'numeric_stats': df.describe().to_dict(),
        'correlation_matrix': df.corr().to_dict()
    }
    
    # Visualization setup
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Distribution plot
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    sns.histplot(df[numeric_cols[0]], kde=True, ax=axes[0, 0])
    axes[0, 0].set_title(f'Distribution of {numeric_cols[0]}')
    
    # Correlation heatmap
    sns.heatmap(df.corr(), annot=True, cmap='coolwarm', ax=axes[0, 1])
    axes[0, 1].set_title('Feature Correlation Matrix')
    
    # Boxplot for target groups
    if 'target' in df.columns:
        df_melted = df.melt(id_vars=['target'], value_vars=numeric_cols[:3])
        sns.boxplot(x='target', y='value', hue='variable', data=df_melted, ax=axes[1, 0])
        axes[1, 0].set_title('Feature Distribution by Target')
        
    # Pairplot subset
    sns.pairplot(df[numeric_cols[:4]], diag_kind='kde', ax=axes[1, 1])
    axes[1, 1].set_title('Pairwise Relationships')
    
    plt.tight_layout()
    plt.show()
    
    profile['plots_generated'] = True
    return profile

if __name__ == "__main__":
    results = run_comprehensive_eda()
    print(f"EDA Complete. Processed {results['shape'][0]} samples.")
    print(f"Missing values: {results['missing_values']}")
    print(f"Correlation matrix keys: {list(results['correlation_matrix'].keys())[:3]}...")
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-data-visualization` | Data Visualization techniques | Complementary to this skill |
| `coding-ds-correlation-analysis` | Correlation Analysis techniques | Complementary to this skill |
| `coding-ds-data-profiling` | Data Profiling techniques | Complementary to this skill |

## References

- Official documentation and papers on Exploratory Data Analysis
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
