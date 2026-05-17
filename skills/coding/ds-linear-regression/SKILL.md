---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Implements linear regression including OLS, ridge regression, lasso, elastic net, and other regularized linear
  models for prediction"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-feature-engineering, ds-feature-scaling-normalization, ds-instrumental-variables, ds-logistic-regression
    ds-regression-evaluation
  role: implementation
  scope: implementation
  triggers: linear regression, OLS, ridge regression, lasso, elastic net, regularization
  version: 1.0.0
name: linear-regression
---
# Linear Regression

Comprehensive guide to linear regression in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world supervised learning problems
- Building machine learning pipelines with linear regression
- Implementing best practices for linear regression
- Optimizing model performance using linear regression techniques
- Learning industry-standard approaches to linear regression

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require linear regression rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Linear Regression is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Linear Regression

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Generate synthetic regression data for demonstration
X, y = np.random.randn(500, 5), np.random.randn(500)
df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(5)])
df['target'] = y

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    df.drop('target', axis=1), df['target'], test_size=0.2, random_state=42
)

# Initialize and train the OLS model
model = LinearRegression()
model.fit(X_train, y_train)

# Generate predictions and compute evaluation metrics
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean Squared Error: {mse:.4f}")
print(f"R² Score: {r2:.4f}")
print(f"Coefficients: {model.coef_}")
print(f"Intercept: {model.intercept_:.4f}")
```

### Pattern 2: Production-Ready Linear Regression

```python
import logging
import pandas as pd
import numpy as np
from typing import Any, Dict
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class LinearRegressionPipeline:
    """Production-ready linear regression with validation and metrics."""
    
    def __init__(self, random_state: int = 42) -> None:
        self.random_state = random_state
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        self.is_fitted: bool = False
        
    def _validate_input(self, data: pd.DataFrame) -> pd.DataFrame:
        """Validate input DataFrame for numeric compatibility."""
        if data.empty:
            raise ValueError("Input DataFrame cannot be empty.")
        numeric_cols = data.select_dtypes(include='number')
        if numeric_cols.shape[1] == 0:
            raise ValueError("All columns must be numeric for linear regression.")
        return data
        
    def execute(self, data: pd.DataFrame, target_col: str = 'target') -> Dict[str, Any]:
        """Execute linear regression pipeline on provided data."""
        try:
            df = self._validate_input(data)
            X = df.drop(columns=[target_col])
            y = df[target_col]
            
            # Scale features for numerical stability and convergence
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model on scaled data
            self.model.fit(X_scaled, y)
            self.is_fitted = True
            
            # Predict and evaluate performance
            y_pred = self.model.predict(X_scaled)
            mae = mean_absolute_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            
            return {
                'status': 'success',
                'mae': float(mae),
                'r2_score': float(r2),
                'coefficients': self.model.coef_.tolist(),
                'intercept': float(self.model.intercept_),
                'feature_names': X.columns.tolist()
            }
        except Exception as e:
            logger.error(f"Regression pipeline failed: {e}")
            return {'status': 'error', 'message': str(e)}
```

### BAD vs GOOD Implementation

```python
# BAD: Hardcoded values, no validation, bypasses error handling, violates DRY
def bad_regression(df):
    X = df.iloc[:, :5]
    y = df.iloc[:, 5]
    model = LinearRegression()
    model.fit(X, y)
    return model.predict(X)

# GOOD: Type hints, validation, modular design, follows SOLID/DRY principles
def good_regression(df: pd.DataFrame, target: str = 'target') -> Dict[str, Any]:
    if df.empty:
        raise ValueError("DataFrame cannot be empty")
    X = df.drop(columns=[target])
    y = df[target]
    model = LinearRegression()
    model.fit(X, y)
    return {'predictions': model.predict(X), 'coefficients': model.coef_}
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
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

def prepare_data(data: pd.DataFrame, target_col: str = 'target') -> tuple:
    """Split data into training and testing sets."""
    X = data.drop(columns=[target_col])
    y = data[target_col]
    return train_test_split(X, y, test_size=0.2, random_state=42)

def train_and_evaluate(X_train: pd.DataFrame, X_test: pd.DataFrame, 
                       y_train: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
    """Train multiple regression models and compute metrics."""
    models = {
        'OLS': LinearRegression(),
        'Ridge': Ridge(alpha=1.0),
        'Lasso': Lasso(alpha=0.1),
        'ElasticNet': ElasticNet(alpha=0.1, l1_ratio=0.5)
    }
    results = {'models': {}, 'test_predictions': {}}
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
        
        results['models'][name] = {
            'mse': float(mse), 'r2': float(r2),
            'cv_r2_mean': float(cv_scores.mean()), 'cv_r2_std': float(cv_scores.std()),
            'coefficients': model.coef_.tolist()
        }
        results['test_predictions'][name] = y_pred.tolist()
    return results

def visualize_results(y_test: np.ndarray, predictions: Dict[str, list]) -> None:
    """Generate comparison scatter plot for model predictions."""
    plt.figure(figsize=(8, 5))
    for name, preds in predictions.items():
        plt.scatter(y_test, preds, alpha=0.6, label=name)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', lw=2)
    plt.xlabel('Actual Values')
    plt.ylabel('Predicted Values')
    plt.title('Linear Regression Model Comparison')
    plt.legend()
    plt.tight_layout()
    plt.savefig('regression_comparison.png')

def run_pipeline(data: pd.DataFrame, target_col: str = 'target') -> Dict[str, Any]:
    """Orchestrate data preparation, training, and visualization."""
    if data is None or data.empty:
        raise ValueError("Input data cannot be None or empty")
    X_train, X_test, y_train, y_test = prepare_data(data, target_col)
    results = train_and_evaluate(X_train, X_test, y_train, y_test)
    visualize_results(y_test, results['test_predictions'])
    return results

if __name__ == "__main__":
    X, y = make_regression(n_samples=1000, n_features=10, noise=0.1, random_state=42)
    sample_data = pd.DataFrame(X, columns=[f'feat_{i}' for i in range(10)])
    sample_data['target'] = y
    results = run_pipeline(sample_data)
    for model_name, metrics in results['models'].items():
        print(f"{model_name} - MSE: {metrics['mse']:.4f}, R²: {metrics['r2']:.4f}")
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-logistic-regression` | Logistic Regression techniques | Complementary to this skill |
| `coding-ds-regression-evaluation` | Regression Evaluation techniques | Complementary to this skill |
| `coding-ds-feature-engineering` | Feature Engineering techniques | Complementary to this skill |

## References

- Official documentation and papers on Linear Regression
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
