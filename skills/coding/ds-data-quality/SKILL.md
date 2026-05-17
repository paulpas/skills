---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Implements data validation, cleaning, outlier detection, and quality assurance techniques to ensure reliable
  datasets for model training"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-anomaly-detection, ds-data-collection, ds-data-profiling, ds-missing-data
  role: implementation
  scope: implementation
  triggers: data validation, data cleaning, outlier detection, data quality, how do i clean data, missing values
  version: 1.0.0
name: data-quality
---
# Data Quality

Comprehensive guide to data quality in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world data collection & ingestion problems
- Building machine learning pipelines with data quality
- Implementing best practices for data quality
- Optimizing model performance using data quality techniques
- Learning industry-standard approaches to data quality

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require data quality rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Data Quality is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Data Quality

```python
import pandas as pd
import numpy as np
from typing import Dict, Any

def basic_data_quality_check(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform basic data quality checks on a DataFrame.
    Checks for missing values, duplicates, data types, and basic statistics.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    quality_report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "data_types": df.dtypes.astype(str).to_dict(),
        "numeric_summary": {}
    }

    for col in df.select_dtypes(include=[np.number]).columns:
        quality_report["numeric_summary"][col] = {
            "mean": float(df[col].mean()),
            "std": float(df[col].std()),
            "min": float(df[col].min()),
            "max": float(df[col].max()),
            "null_count": int(df[col].isnull().sum())
        }

    return quality_report
```

### Pattern 2: Production-Ready Data Quality

```python
import logging
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class ProductionDataQuality:
    """
    Production-grade data quality handler following DRY principles.
    Handles validation, imputation, scaling, and outlier detection.
    """
    def __init__(self, missing_threshold: float = 0.5, outlier_std: float = 3.0):
        self.missing_threshold = missing_threshold
        self.outlier_std = outlier_std
        self.imputer = SimpleImputer(strategy="median")
        self.scaler = StandardScaler()
        self.quality_issues: List[str] = []

    def execute(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Execute comprehensive data quality pipeline."""
        if data.empty:
            raise ValueError("Input DataFrame cannot be empty")

        issues = []
        clean_data = data.copy()

        missing_cols = clean_data.columns[clean_data.isnull().mean() > self.missing_threshold]
        if len(missing_cols) > 0:
            issues.append(f"Dropping columns with >{self.missing_threshold*100}% missing: {list(missing_cols)}")
            clean_data.drop(columns=missing_cols, inplace=True)

        numeric_cols = clean_data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            clean_data[numeric_cols] = self.imputer.fit_transform(clean_data[numeric_cols])

        for col in numeric_cols:
            z_scores = np.abs((clean_data[col] - clean_data[col].mean()) / clean_data[col].std())
            outlier_mask = z_scores > self.outlier_std
            if outlier_mask.any():
                issues.append(f"Detected {outlier_mask.sum()} outliers in column '{col}'")
                clean_data.loc[outlier_mask, col] = clean_data[col].median()

        if len(numeric_cols) > 0:
            clean_data[numeric_cols] = self.scaler.fit_transform(clean_data[numeric_cols])

        self.quality_issues = issues
        return {
            "cleaned_data": clean_data,
            "issues_found": issues,
            "rows_processed": len(data),
            "columns_retained": len(clean_data.columns)
        }
```

### BAD vs GOOD Example

```python
# BAD: Bypasses error handling, uses magic numbers, and mutates input silently
def bad_quality_check(df):
    df.dropna()
    df = df[(df['val'] > -999) & (df['val'] < 999)]
    return df

# GOOD: Explicit validation, configurable thresholds, and proper return structure
def good_quality_check(df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a DataFrame")
    if df.empty:
        raise ValueError("DataFrame cannot be empty")
    clean_df = df.dropna()
    numeric_cols = clean_df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        q1, q3 = clean_df[col].quantile(0.25), clean_df[col].quantile(0.75)
        iqr = q3 - q1
        clean_df = clean_df[(clean_df[col] >= q1 - 1.5 * iqr) & (clean_df[col] <= q3 + 1.5 * iqr)]
    return clean_df
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
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

def run_data_quality_pipeline(raw_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Complete data quality pipeline with validation, cleaning, and reporting.
    Follows KISS principle by keeping steps explicit and modular.
    """
    if raw_data is None or raw_data.empty:
        raise ValueError("Raw data cannot be None or empty")

    report = {
        "original_shape": raw_data.shape,
        "missing_counts": {},
        "duplicate_count": 0,
        "outlier_count": 0,
        "cleaned_shape": (0, 0),
        "status": "success"
    }

    if not isinstance(raw_data, pd.DataFrame):
        raise TypeError("Expected pandas DataFrame")

    missing = raw_data.isnull().sum()
    report["missing_counts"] = missing[missing > 0].to_dict()

    report["duplicate_count"] = int(raw_data.duplicated().sum())

    cleaned = raw_data.dropna().drop_duplicates()

    numeric_cols = cleaned.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        q1, q3 = cleaned[col].quantile(0.25), cleaned[col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outliers = ((cleaned[col] < lower) | (cleaned[col] > upper)).sum()
        report["outlier_count"] += int(outliers)
        cleaned[col] = cleaned[col].clip(lower=lower, upper=upper)

    report["cleaned_shape"] = cleaned.shape
    return report

if __name__ == "__main__":
    X, y = make_classification(n_samples=500, n_features=5, n_informative=3, random_state=42)
    df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(5)])
    df["target"] = y

    df.loc[:10, "feature_0"] = np.nan
    df.loc[:5] = df.loc[0]

    results = run_data_quality_pipeline(df)
    print("Data Quality Report:")
    for key, value in results.items():
        print(f"  {key}: {value}")
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-data-collection` | Data Collection techniques | Complementary to this skill |
| `coding-ds-missing-data` | Missing Data techniques | Complementary to this skill |
| `coding-ds-data-profiling` | Data Profiling techniques | Complementary to this skill |

## References

- Official documentation and papers on Data Quality
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
