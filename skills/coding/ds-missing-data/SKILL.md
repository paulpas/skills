---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Handles missing data using imputation strategies, deletion methods, and techniques for dealing with incomplete
  datasets while preserving information"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-data-quality, ds-eda, ds-feature-engineering
  role: implementation
  scope: implementation
  triggers: missing data, imputation, NaN handling, missing values, how do i handle missing data, data gaps
  version: 1.0.0
name: missing-data
---
# Missing Data Handling

Comprehensive guide to missing data handling in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world exploratory data analysis problems
- Building machine learning pipelines with missing data handling
- Implementing best practices for missing data handling
- Optimizing model performance using missing data handling techniques
- Learning industry-standard approaches to missing data handling

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require missing data handling rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Missing Data Handling is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Missing Data Handling

```python
import pandas as pd
import numpy as np
from typing import Dict, Any, Literal

def apply_basic_imputation(df: pd.DataFrame, strategy: Literal["drop", "mean", "median", "mode"] = "mean") -> pd.DataFrame:
    """Apply basic missing data handling strategies to a DataFrame."""
    if df.empty:
        raise ValueError("Input DataFrame cannot be empty")
        
    df_clean = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns
    
    if strategy == "drop":
        df_clean = df_clean.dropna()
    elif strategy == "mean":
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].mean())
    elif strategy == "median":
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())
    elif strategy == "mode":
        for col in categorical_cols:
            mode_val = df_clean[col].mode()
            fill_val = mode_val.iloc[0] if not mode_val.empty else "Unknown"
            df_clean[col] = df_clean[col].fillna(fill_val)
    else:
        raise ValueError(f"Unsupported strategy: {strategy}")
        
    return df_clean
```

### Pattern 2: Production-Ready Missing Data Handling

```python
import logging
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer

logger = logging.getLogger(__name__)

class MissingDataHandler:
    """Production-grade missing data handler with configurable strategies."""
    
    def __init__(self, numeric_strategy: str = "median", categorical_strategy: str = "most_frequent", 
                 drop_threshold: float = 0.5, verbose: bool = False):
        self.numeric_strategy = numeric_strategy
        self.categorical_strategy = categorical_strategy
        self.drop_threshold = drop_threshold
        self.verbose = verbose
        self.numeric_imputer: Optional[SimpleImputer] = None
        self.categorical_imputer: Optional[SimpleImputer] = None
        self.preprocessor: Optional[ColumnTransformer] = None
        
    def _validate_input(self, data: pd.DataFrame) -> None:
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
        if data.empty:
            raise ValueError("Input DataFrame cannot be empty")
            
    def fit_transform(self, data: pd.DataFrame) -> Dict[str, Any]:
        self._validate_input(data)
        logger.info("Starting missing data handling pipeline")
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = data.select_dtypes(include=["object", "category"]).columns.tolist()
        
        missing_ratio = data.isnull().mean()
        cols_to_drop = missing_ratio[missing_ratio > self.drop_threshold].index.tolist()
        if cols_to_drop:
            logger.warning(f"Dropping columns with >{self.drop_threshold*100}% missing: {cols_to_drop}")
            data = data.drop(columns=cols_to_drop)
            
        numeric_transformer = SimpleImputer(strategy=self.numeric_strategy)
        categorical_transformer = SimpleImputer(strategy=self.categorical_strategy)
        
        self.preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_transformer, numeric_cols),
                ("cat", categorical_transformer, categorical_cols)
            ], remainder="passthrough"
        )
        
        transformed_data = self.preprocessor.fit_transform(data)
        result_df = pd.DataFrame(transformed_data, columns=data.columns.drop(cols_to_drop), index=data.index)
        
        return {
            "status": "success",
            "data": result_df,
            "metadata": {
                "original_shape": data.shape,
                "final_shape": result_df.shape,
                "dropped_columns": cols_to_drop,
                "strategies_used": {"numeric": self.numeric_strategy, "categorical": self.categorical_strategy}
            }
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
# BAD: Blindly dropping rows without assessing missingness pattern or data type
df_clean = df.dropna()  # May discard 80% of data if missingness is non-random or structured

# GOOD: Assess missingness mechanism and data types before choosing strategy
MISSING_THRESHOLD = 0.5
numeric_cols = df.select_dtypes(include=[np.number]).columns
missing_pct = df.isnull().mean()

if missing_pct.max() > MISSING_THRESHOLD:
    df_clean = df.drop(columns=missing_pct[missing_pct > MISSING_THRESHOLD].index)
else:
    df_clean = df.copy()
    df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())
    df_clean = df_clean.dropna()  # Safe to drop remaining rows after targeted imputation
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
import pandas as pd
import numpy as np
from typing import Dict, Any
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

def handle_missing_data_pipeline(data: pd.DataFrame, target_col: str) -> Dict[str, Any]:
    """
    Complete pipeline for handling missing data and evaluating impact.
    """
    if data.empty or target_col not in data.columns:
        raise ValueError("Invalid input data or target column")
        
    X = data.drop(columns=[target_col])
    y = data[target_col]
    
    np.random.seed(42)
    missing_mask = np.random.random(X.shape) < 0.2
    X_missing = X.copy()
    X_missing.values[missing_mask] = np.nan
    
    X_dropped = X_missing.dropna()
    y_dropped = y.loc[X_dropped.index]
    
    imputer = SimpleImputer(strategy="median")
    X_imputed = pd.DataFrame(imputer.fit_transform(X_missing), columns=X_missing.columns, index=X_missing.index)
    
    X_train_d, X_test_d, y_train_d, y_test_d = train_test_split(X_dropped, y_dropped, test_size=0.2, random_state=42)
    X_train_i, X_test_i, y_train_i, y_test_i = train_test_split(X_imputed, y, test_size=0.2, random_state=42)
    
    clf_d = RandomForestClassifier(n_estimators=10, random_state=42)
    clf_d.fit(X_train_d, y_train_d)
    pred_d = clf_d.predict(X_test_d)
    
    clf_i = RandomForestClassifier(n_estimators=10, random_state=42)
    clf_i.fit(X_train_i, y_train_i)
    pred_i = clf_i.predict(X_test_i)
    
    return {
        "dropped_data_shape": X_dropped.shape,
        "imputed_data_shape": X_imputed.shape,
        "dropped_model_report": classification_report(y_test_d, pred_d, output_dict=True),
        "imputed_model_report": classification_report(y_test_i, pred_i, output_dict=True),
        "status": "success"
    }

if __name__ == "__main__":
    X, y = make_classification(n_samples=500, n_features=10, n_informative=5, random_state=42)
    df = pd.DataFrame(X, columns=[f"feat_{i}" for i in range(10)])
    df["target"] = y
    results = handle_missing_data_pipeline(df, "target")
    print(f"Status: {results['status']}")
    print(f"Dropped shape: {results['dropped_data_shape']}")
    print(f"Imputed shape: {results['imputed_data_shape']}")
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-data-quality` | Data Quality techniques | Complementary to this skill |
| `coding-ds-eda` | Eda techniques | Complementary to this skill |
| `coding-ds-feature-engineering` | Feature Engineering techniques | Complementary to this skill |

## References

- Official documentation and papers on Missing Data Handling
- Industry best practices and standards
- Implementation examples from the scikit-learn, TensorFlow, and PyTorch libraries
- ISO 8000 (Data Quality) standard for handling incomplete datasets
- DRY and KISS principles for maintainable data pipelines

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
