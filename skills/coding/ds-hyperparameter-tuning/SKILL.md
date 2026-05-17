---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Optimizes hyperparameters using grid search, random search, Bayesian optimization, and evolutionary methods
  for model improvement"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-bias-variance-tradeoff, ds-cross-validation, ds-model-selection, ds-support-vector-machines ds-tree-methods
  role: implementation
  scope: implementation
  triggers: hyperparameter tuning, grid search, random search, bayesian optimization, how do I tune parameters
  version: 1.0.0
name: hyperparameter-tuning
---
# Hyperparameter Tuning

Comprehensive guide to hyperparameter tuning in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world model evaluation & selection problems
- Building machine learning pipelines with hyperparameter tuning
- Implementing best practices for hyperparameter tuning
- Optimizing model performance using hyperparameter tuning techniques
- Learning industry-standard approaches to hyperparameter tuning

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require hyperparameter tuning rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Hyperparameter Tuning is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Hyperparameter Tuning

```python
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Generate reproducible sample dataset
X, y = make_classification(n_samples=500, n_features=10, random_state=42)

# Define base estimator and parameter search space
model = RandomForestClassifier(random_state=42)
param_grid: dict[str, list[int]] = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5, 10]
}

# Initialize GridSearchCV with stratified cross-validation
grid_search: GridSearchCV = GridSearchCV(
    estimator=model,
    param_grid=param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    verbose=1
)

# Fit the model to the data
grid_search.fit(X, y)

# Extract and display optimal configuration
best_params: dict[str, int | None] = grid_search.best_params_
best_score: float = grid_search.best_score_
print(f"Best Parameters: {best_params}")
print(f"Best CV Score: {best_score:.4f}")
```

### Pattern 2: Production-Ready Hyperparameter Tuning

```python
import logging
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Tuple
from sklearn.model_selection import RandomizedSearchCV
from sklearn.base import BaseEstimator
from sklearn.metrics import make_scorer, accuracy_score

logger = logging.getLogger(__name__)

class HyperparameterTuning:
    """Production implementation of Hyperparameter Tuning"""
    
    def __init__(self, model: BaseEstimator, param_distributions: Dict[str, List], cv: int = 5):
        self.model = model
        self.param_distributions = param_distributions
        self.cv = cv
        self.results: Dict[str, Any] = {}
        
    def execute(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Execute Hyperparameter Tuning on data"""
        try:
            logger.info("Starting hyperparameter tuning...")
            search = RandomizedSearchCV(
                estimator=self.model,
                param_distributions=self.param_distributions,
                n_iter=20,
                cv=self.cv,
                scoring=make_scorer(accuracy_score),
                random_state=42,
                n_jobs=-1
            )
            search.fit(X, y)
            
            self.results = {
                'best_params': search.best_params_,
                'best_score': float(search.best_score_),
                'cv_results_mean': search.cv_results_['mean_test_score'].tolist(),
                'status': 'success'
            }
            logger.info(f"Tuning completed. Best score: {self.results['best_score']:.4f}")
            return self.results
        except Exception as e:
            logger.error(f"Tuning failed: {str(e)}")
            return {'status': 'failed', 'error': str(e)}
```

## Best Practices

- ✅ Always validate your implementation on test data
- ✅ Document your assumptions and methodology
- ✅ Use version control for reproducibility
- ✅ Monitor performance metrics in production
- ✅ Periodically review and update your approach
- ✅ Test with edge cases and outliers
- ✅ Log all significant operations for debugging
- ✅ Follow SOLID principles to keep tuning logic modular and testable
- ✅ Adhere to DRY principles by abstracting repeated search configurations

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
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score

def prepare_data(X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Split data into training and testing sets."""
    if X.shape[0] != y.shape[0]:
        raise ValueError("Feature and target dimensions must match")
    return train_test_split(X, y, test_size=0.2, random_state=42)

def run_tuning(X_train: np.ndarray, y_train: np.ndarray) -> GridSearchCV:
    """Execute grid search with defined parameter space."""
    model = GradientBoostingRegressor(random_state=42)
    param_grid = {
        'n_estimators': [50, 100],
        'learning_rate': [0.01, 0.1],
        'max_depth': [3, 5]
    }
    return GridSearchCV(model, param_grid, cv=5, scoring='neg_mean_squared_error', n_jobs=-1)

def evaluate_model(model: GridSearchCV, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
    """Calculate performance metrics on held-out data."""
    y_pred = model.best_estimator_.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    return {'test_mse': float(mse), 'test_r2': float(r2)}

def implement_tuning(X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
    """
    Complete implementation of Hyperparameter Tuning.
    
    Args:
        X: Feature matrix
        y: Target vector
        
    Returns:
        Dictionary with results and metadata
        
    Raises:
        ValueError: If input data is invalid
    """
    if X is None or y is None or len(X) == 0 or len(y) == 0:
        raise ValueError("Input data cannot be None or empty")
        
    X_train, X_test, y_train, y_test = prepare_data(X, y)
    grid_search = run_tuning(X_train, y_train)
    grid_search.fit(X_train, y_train)
    metrics = evaluate_model(grid_search, X_test, y_test)
    
    return {
        'status': 'success',
        'best_params': grid_search.best_params_,
        **metrics,
        'metadata': {'train_samples': len(X_train), 'test_samples': len(X_test)}
    }

if __name__ == "__main__":
    X, y = make_regression(n_samples=1000, n_features=10, noise=0.1, random_state=42)
    results = implement_tuning(X, y)
    print(f"Status: {results['status']}")
    print(f"Test MSE: {results['test_mse']:.4f}")
    print(f"Test R2: {results['test_r2']:.4f}")
```

## BAD vs GOOD Examples

```python
# BAD: Tuning on test data leaks information and invalidates metrics
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
grid = GridSearchCV(model, param_grid, cv=5)
grid.fit(X_test, y_test)  # ❌ Never tune on test data
print(grid.best_score_)   # ❌ Overly optimistic, unrepresentative

# GOOD: Strict separation of train/validation/test sets
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)
grid = GridSearchCV(model, param_grid, cv=5)
grid.fit(X_train, y_train)  # ✅ Tune only on training data
val_score = grid.best_estimator_.score(X_val, y_val)  # ✅ Validate on held-out set
test_score = grid.best_estimator_.score(X_test, y_test)  # ✅ Final evaluation on test set
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-cross-validation` | Cross Validation techniques | Complementary to this skill |
| `coding-ds-model-selection` | Model Selection techniques | Complementary to this skill |
| `coding-ds-bias-variance-tradeoff` | Bias Variance Tradeoff techniques | Complementary to this skill |

## References

- Official documentation and papers on Hyperparameter Tuning
- Industry best practices and standards
- Implementation examples from the scikit-learn, TensorFlow, and PyTorch libraries
- SOLID principles for modular, maintainable ML codebases
- DRY (Don't Repeat Yourself) guidelines for parameter grid management

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
