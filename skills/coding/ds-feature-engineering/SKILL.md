---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Creates and transforms features including polynomial features, interactions, domain-specific features, and
  feature transformations"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-categorical-encoding, ds-dimensionality-reduction, ds-feature-scaling-normalization, ds-feature-selection
    ds-missing-data
  role: implementation
  scope: implementation
  triggers: feature engineering, feature creation, feature transformation, how do I engineer features, feature design
  version: 1.0.0
name: feature-engineering
---
# Feature Engineering

Comprehensive guide to feature engineering in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world feature engineering problems
- Building machine learning pipelines with feature engineering
- Implementing best practices for feature engineering
- Optimizing model performance using feature engineering techniques
- Learning industry-standard approaches to feature engineering

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require feature engineering rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Feature Engineering is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Feature Engineering

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def basic_feature_engineering(df: pd.DataFrame, target_col: str, numeric_cols: list) -> tuple:
    """
    Apply basic feature engineering transformations to a DataFrame.
    Handles polynomial features, log transforms, and standard scaling.
    """
    if df.empty:
        raise ValueError("Input DataFrame cannot be empty")
    
    # Separate features and target
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    # Identify numeric columns for transformation
    numeric_features = [col for col in numeric_cols if col in X.columns]
    
    # Create transformation pipeline
    transformer = ColumnTransformer(
        transformers=[
            ('poly', PolynomialFeatures(degree=2, include_bias=False), numeric_features),
            ('scaler', StandardScaler(), numeric_features)
        ],
        remainder='passthrough'
    )
    
    # Fit and transform data
    X_transformed = transformer.fit_transform(X)
    
    # Create DataFrame with new feature names
    poly_names = transformer.named_transformers_['poly'].get_feature_names_out(numeric_features)
    new_df = pd.DataFrame(X_transformed, columns=poly_names, index=X.index)
    
    return new_df, transformer, y
```

### Pattern 2: Production-Ready Feature Engineering

```python
import logging
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import warnings

logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

class FeatureEngineering:
    """Production-grade feature engineering pipeline with validation and logging."""
    
    def __init__(self, numeric_cols: List[str], categorical_cols: List[str], 
                 target_col: str, degree: int = 2, handle_missing: bool = True):
        self.numeric_cols = numeric_cols
        self.categorical_cols = categorical_cols
        self.target_col = target_col
        self.degree = degree
        self.handle_missing = handle_missing
        self.pipeline = None
        self.feature_names = None
        
    def _validate_input(self, data: pd.DataFrame) -> None:
        missing_cols = set(self.numeric_cols + self.categorical_cols + [self.target_col]) - set(data.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        if data.isnull().sum().sum() > 0 and not self.handle_missing:
            logger.warning("Data contains missing values but handle_missing is False")
            
    def execute(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Execute feature engineering on data with full validation and logging."""
        self._validate_input(data)
        logger.info(f"Starting feature engineering on {len(data)} rows")
        
        X = data.drop(columns=[self.target_col])
        y = data[self.target_col]
        
        # Build preprocessing pipeline
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')) if self.handle_missing else None,
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')) if self.handle_missing else None,
            ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, self.numeric_cols),
                ('cat', categorical_transformer, self.categorical_cols)
            ],
            remainder='drop'
        )
        
        # Fit and transform
        X_transformed = preprocessor.fit_transform(X)
        self.pipeline = preprocessor
        
        # Get feature names
        num_names = preprocessor.named_transformers_['num'].named_steps['scaler'].get_feature_names_out(self.numeric_cols)
        cat_names = preprocessor.named_transformers_['cat'].named_steps['encoder'].get_feature_names_out(self.categorical_cols)
        self.feature_names = np.concatenate([num_names, cat_names])
        
        logger.info(f"Feature engineering complete. Output shape: {X_transformed.shape}")
        
        return {
            'X_transformed': X_transformed,
            'y': y.values,
            'feature_names': self.feature_names,
            'pipeline': self.pipeline,
            'metadata': {'original_shape': data.shape, 'transformed_shape': X_transformed.shape}
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
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
import warnings
warnings.filterwarnings('ignore')

def run_complete_feature_engineering_example():
    """
    Demonstrates a complete feature engineering workflow with real data,
    model training, evaluation, and visualization.
    """
    # 1. Generate synthetic regression data
    X, y = make_regression(n_samples=500, n_features=4, noise=0.1, random_state=42)
    df = pd.DataFrame(X, columns=['feat_1', 'feat_2', 'feat_3', 'feat_4'])
    df['target'] = y
    
    # 2. Split data
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    
    # 3. Define feature engineering pipeline
    fe_pipeline = Pipeline([
        ('poly', PolynomialFeatures(degree=2, include_bias=False, interaction_only=False)),
        ('scaler', StandardScaler())
    ])
    
    # 4. Apply transformations
    X_train_fe = fe_pipeline.fit_transform(train_df.drop(columns=['target']))
    X_test_fe = fe_pipeline.transform(test_df.drop(columns=['target']))
    
    # 5. Train model
    model = Ridge(alpha=1.0)
    model.fit(X_train_fe, train_df['target'].values)
    
    # 6. Evaluate
    y_pred = model.predict(X_test_fe)
    mse = mean_squared_error(test_df['target'].values, y_pred)
    r2 = r2_score(test_df['target'].values, y_pred)
    
    print(f"Mean Squared Error: {mse:.4f}")
    print(f"R² Score: {r2:.4f}")
    
    # 7. Visualization
    plt.figure(figsize=(8, 6))
    plt.scatter(test_df['target'].values, y_pred, alpha=0.6, color='steelblue')
    plt.plot([test_df['target'].min(), test_df['target'].max()], 
             [test_df['target'].min(), test_df['target'].max()], 'r--', lw=2)
    plt.xlabel('Actual Values')
    plt.ylabel('Predicted Values')
    plt.title(f'Feature Engineering Pipeline Performance (R²={r2:.2f})')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()
    
    return {'mse': mse, 'r2': r2, 'pipeline': fe_pipeline, 'model': model}

if __name__ == "__main__":
    results = run_complete_feature_engineering_example()
    print(f"Pipeline completed successfully. Metrics: {results}")
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-feature-selection` | Feature Selection techniques | Complementary to this skill |
| `coding-ds-categorical-encoding` | Categorical Encoding techniques | Complementary to this skill |
| `coding-ds-feature-scaling-normalization` | Feature Scaling Normalization techniques | Complementary to this skill |

## References

- Official documentation and papers on Feature Engineering
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
