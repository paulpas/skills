---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Provides Scales and normalizes features using standardization, normalization, robust scaling, and other scaling
  methods for model compatibility"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-categorical-encoding, ds-feature-engineering, ds-linear-regression
  role: implementation
  scope: implementation
  triggers: feature scaling, normalization, standardization, robust scaling, scaling features, how do I scale
  version: 1.0.0
name: feature-scaling-normalization
---
# Feature Scaling

Comprehensive guide to feature scaling in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world feature engineering problems
- Building machine learning pipelines with feature scaling
- Implementing best practices for feature scaling
- Optimizing model performance using feature scaling techniques
- Learning industry-standard approaches to feature scaling

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require feature scaling rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Feature Scaling is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Feature Scaling

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# Generate sample data with different scales and distributions
np.random.seed(42)
data = pd.DataFrame({
    'feature_A': np.random.normal(loc=100, scale=10, size=100),
    'feature_B': np.random.uniform(low=0, high=1, size=100),
    'feature_C': np.random.exponential(scale=5, size=100)
})

# Standardization (Z-score normalization)
scaler_std = StandardScaler()
data_scaled_std = scaler_std.fit_transform(data)

# Min-Max Normalization
scaler_minmax = MinMaxScaler(feature_range=(0, 1))
data_scaled_minmax = scaler_minmax.fit_transform(data)

print("Original Data Shape:", data.shape)
print("Standardized Mean:", np.mean(data_scaled_std, axis=0))
print("Standardized Std:", np.std(data_scaled_std, axis=0))
print("Min-Max Range:", np.min(data_scaled_minmax, axis=0), np.max(data_scaled_minmax, axis=0))
```

### Pattern 2: Production-Ready Feature Scaling

```python
import logging
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, RobustScaler
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class FeatureScaling:
    """Production implementation of Feature Scaling following scikit-learn API conventions."""
    
    def __init__(self, method: str = "standard", columns: List[str] = None):
        self.method = method
        self.columns = columns
        self.scaler = None
        
    def _validate_input(self, data: pd.DataFrame) -> None:
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input data must be a pandas DataFrame")
        if data.empty:
            raise ValueError("Input DataFrame cannot be empty")
        if self.columns:
            missing = set(self.columns) - set(data.columns)
            if missing:
                raise ValueError(f"Missing columns: {missing}")
                
    def execute(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Execute Feature Scaling on data with proper error handling and logging."""
        self._validate_input(data)
        target_cols = self.columns if self.columns else data.select_dtypes(include=[np.number]).columns.tolist()
        
        if not target_cols:
            raise ValueError("No numeric columns found for scaling")
            
        try:
            if self.method == "standard":
                self.scaler = StandardScaler()
            elif self.method == "robust":
                self.scaler = RobustScaler()
            else:
                raise ValueError(f"Unsupported scaling method: {self.method}")
                
            scaled_data = self.scaler.fit_transform(data[target_cols])
            result_df = data.copy()
            result_df[target_cols] = scaled_data
            
            logger.info(f"Successfully scaled {len(target_cols)} columns using {self.method}")
            
            return {
                'status': 'success',
                'scaled_data': result_df,
                'metadata': {
                    'method': self.method,
                    'columns_scaled': target_cols,
                    'original_shape': data.shape,
                    'scaled_shape': result_df.shape
                }
            }
        except Exception as e:
            logger.error(f"Scaling failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
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
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from typing import Dict, Any, List, Tuple
import warnings

# BAD PRACTICE: Manual scaling without validation or vectorization
def bad_scaling_approach(df: pd.DataFrame) -> pd.DataFrame:
    """Inefficient and error-prone manual scaling."""
    result = df.copy()
    for col in result.columns:
        mean = sum(result[col]) / len(result[col])
        std = (sum((x - mean)**2 for x in result[col]) / len(result[col]))**0.5
        result[col] = (result[col] - mean) / std
    return result

# GOOD PRACTICE: Vectorized, validated, and using established libraries
def good_scaling_approach(df: pd.DataFrame, method: str = "standard") -> pd.DataFrame:
    """Efficient scaling following scikit-learn API design principles (DRY & KISS)."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if method == "standard":
        scaler = StandardScaler()
    elif method == "minmax":
        scaler = MinMaxScaler()
    elif method == "robust":
        scaler = RobustScaler()
    else:
        raise ValueError("Method must be 'standard', 'minmax', or 'robust'")
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    return df

def _validate_and_select_scaler(method: str) -> object:
    """Helper to validate method and instantiate appropriate scaler."""
    scaler_map = {
        "standard": StandardScaler,
        "minmax": MinMaxScaler,
        "robust": RobustScaler
    }
    if method not in scaler_map:
        raise ValueError(f"Unsupported scaling method: {method}")
    return scaler_map[method]()

def implement_feature_scaling(data: pd.DataFrame, scaling_method: str = "standard", 
                              exclude_columns: List[str] = None) -> Dict[str, Any]:
    """
    Complete implementation of Feature Scaling.
    
    This example demonstrates:
    - Proper input validation and type checking
    - Vectorized algorithm implementation using scikit-learn
    - Comprehensive error handling and logging
    - Result formatting with metadata
    
    Args:
        data: Input DataFrame with numeric and categorical columns
        scaling_method: One of 'standard', 'minmax', or 'robust'
        exclude_columns: List of column names to exclude from scaling
        
    Returns:
        Dictionary with scaled data, scaler objects, and metadata
        
    Raises:
        ValueError: If input data is invalid or method is unsupported
        TypeError: If input is not a DataFrame
        
    Example:
        >>> df = pd.DataFrame({'x': [1, 2, 3, 4, 5], 'y': [10, 20, 30, 40, 50], 'cat': ['a', 'b', 'c', 'd', 'e']})
        >>> results = implement_feature_scaling(df)
        >>> print(results['status'])
    """
    if data is None or data.empty:
        raise ValueError("Input data cannot be None or empty")
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Input data must be a pandas DataFrame")
        
    exclude_columns = exclude_columns or []
    numeric_cols = [col for col in data.select_dtypes(include=[np.number]).columns if col not in exclude_columns]
    
    if not numeric_cols:
        raise ValueError("No numeric columns available for scaling after exclusions")
        
    try:
        scaler = _validate_and_select_scaler(scaling_method)
        scaled_numeric = scaler.fit_transform(data[numeric_cols])
        result_df = data.copy()
        result_df[numeric_cols] = scaled_numeric
        
        stats = {col: {'mean': float(np.mean(result_df[col])), 'std': float(np.std(result_df[col]))} 
                 for col in numeric_cols}
                 
        return {
            'status': 'success',
            'scaled_data': result_df,
            'scaler': scaler,
            'metadata': {
                'method': scaling_method,
                'columns_scaled': numeric_cols,
                'original_shape': data.shape,
                'scaled_shape': result_df.shape,
                'post_scaling_stats': stats
            }
        }
    except Exception as e:
        warnings.warn(f"Scaling operation encountered an issue: {str(e)}")
        return {'status': 'error', 'message': str(e)}

# Usage and testing
if __name__ == "__main__":
    # Create realistic sample data with mixed types and scales
    np.random.seed(42)
    sample_data = pd.DataFrame({
        'age': np.random.normal(loc=35, scale=10, size=100),
        'income': np.random.exponential(scale=50000, size=100),
        'score': np.random.uniform(0, 100, size=100),
        'category': np.random.choice(['A', 'B', 'C'], size=100)
    })
    
    print("=== BAD APPROACH (Manual) ===")
    try:
        bad_result = bad_scaling_approach(sample_data[['age', 'income', 'score']])
        print("Bad approach completed (note: non-vectorized and lacks validation)")
    except Exception as e:
        print(f"Bad approach failed: {e}")
        
    print("\n=== GOOD APPROACH (Vectorized) ===")
    good_result = good_scaling_approach(sample_data[['age', 'income', 'score']], method="standard")
    print("Good approach completed successfully")
    
    print("\n=== FULL IMPLEMENTATION ===")
    results = implement_feature_scaling(sample_data, scaling_method="robust", exclude_columns=['category'])
    print(f"Status: {results['status']}")
    print(f"Processed {results['metadata']['original_shape'][0]} rows, {results['metadata']['original_shape'][1]} columns")
    print(f"Scaled columns: {results['metadata']['columns_scaled']}")
    print(f"Post-scaling stats for 'income': {results['metadata']['post_scaling_stats']['income']}")
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-feature-engineering` | Feature Engineering techniques | Complementary to this skill |
| `coding-ds-categorical-encoding` | Categorical Encoding techniques | Complementary to this skill |
| `coding-ds-linear-regression` | Linear Regression techniques | Complementary to this skill |

## References

- Official documentation and papers on Feature Scaling
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
