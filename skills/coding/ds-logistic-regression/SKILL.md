---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Implements logistic regression for binary and multinomial classification with probability estimation and odds
  ratio interpretation"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-classification-metrics, ds-feature-engineering, ds-linear-regression
  role: implementation
  scope: implementation
  triggers: logistic regression, classification, binary classification, multinomial, how do i classify
  version: 1.0.0
name: logistic-regression
---
# Logistic Regression

Comprehensive guide to logistic regression in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world supervised learning problems
- Building machine learning pipelines with logistic regression
- Implementing best practices for logistic regression
- Optimizing model performance using logistic regression techniques
- Learning industry-standard approaches to logistic regression

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require logistic regression rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Logistic Regression is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Logistic Regression

```python
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.datasets import make_classification
from typing import Tuple

def basic_logistic_regression() -> Tuple[pd.DataFrame, LogisticRegression]:
    """Generate synthetic data, train model, and return results."""
    X, y = make_classification(n_samples=500, n_features=10, n_informative=5, random_state=42)
    df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(X.shape[1])])
    df['target'] = y
    
    X_train, X_test, y_train, y_test = train_test_split(
        df.drop('target', axis=1), df['target'], test_size=0.2, random_state=42
    )
    
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(classification_report(y_test, y_pred))
    
    return df, model

if __name__ == "__main__":
    basic_logistic_regression()
```

### Pattern 2: Production-Ready Logistic Regression

```python
import logging
import pandas as pd
import numpy as np
from typing import Any, Dict, List
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)

class LogisticRegressionPipeline:
    """Production-ready logistic regression pipeline with validation and metrics."""
    
    def __init__(self, C: float = 1.0, penalty: str = 'l2', random_state: int = 42) -> None:
        self.C = C
        self.penalty = penalty
        self.random_state = random_state
        self.pipeline: Pipeline | None = None
        self.scaler: StandardScaler | None = None
        self.model: LogisticRegression | None = None

    def execute(self, data: pd.DataFrame, target_col: str = 'target') -> Dict[str, Any]:
        """Execute logistic regression pipeline on provided data."""
        if data is None or data.empty:
            raise ValueError("Input data cannot be None or empty")
        if target_col not in data.columns:
            raise ValueError(f"Target column '{target_col}' not found in data")
        
        X = data.drop(columns=[target_col])
        y = data[target_col]
        
        self.scaler = StandardScaler()
        self.model = LogisticRegression(C=self.C, penalty=self.penalty, random_state=self.random_state, max_iter=1000)
        self.pipeline = Pipeline([('scaler', self.scaler), ('classifier', self.model)])
        
        self.pipeline.fit(X, y)
        predictions = self.pipeline.predict(X)
        probabilities = self.pipeline.predict_proba(X)
        
        logger.info("Pipeline executed successfully")
        return {
            'status': 'success',
            'predictions': predictions.tolist(),
            'probabilities': probabilities.tolist(),
            'model_params': {'C': self.C, 'penalty': self.penalty},
            'feature_names': X.columns.tolist()
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
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, roc_curve, auc
from typing import Dict, Any

def train_and_evaluate_logistic_regression(
    n_samples: int = 1000, 
    n_features: int = 5, 
    test_size: float = 0.2
) -> Dict[str, Any]:
    """Train logistic regression on synthetic data and return evaluation metrics."""
    X, y = make_classification(n_samples=n_samples, n_features=n_features, random_state=42)
    df = pd.DataFrame(X, columns=[f'feat_{i}' for i in range(n_features)])
    df['label'] = y
    
    X_train, X_test, y_train, y_test = train_test_split(
        df.drop('label', axis=1), df['label'], test_size=test_size, random_state=42
    )
    
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(6, 4))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic')
    plt.legend(loc='lower right')
    plt.grid(True)
    plt.show()
    
    return {
        'accuracy': acc,
        'confusion_matrix': cm.tolist(),
        'roc_auc': roc_auc,
        'coefficients': model.coef_.tolist(),
        'intercept': model.intercept_.tolist()
    }

if __name__ == "__main__":
    results = train_and_evaluate_logistic_regression()
    print(f"Model Accuracy: {results['accuracy']:.4f}")
    print(f"ROC AUC: {results['roc_auc']:.4f}")
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-linear-regression` | Linear Regression techniques | Complementary to this skill |
| `coding-ds-classification-metrics` | Classification Metrics techniques | Complementary to this skill |
| `coding-ds-feature-engineering` | Feature Engineering techniques | Complementary to this skill |

## References

- Official documentation and papers on Logistic Regression
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

### BAD vs GOOD Example Pair
```python
# BAD: Hardcoded values, no type hints, bypasses validation, violates DRY
def train_model(data):
    m = LogisticRegression()
    m.fit(data.drop('y', axis=1), data['y'])
    return m.predict(data.drop('y', axis=1))

# GOOD: Type hints, validation, configurable parameters, follows DRY principle
def train_model(data: pd.DataFrame, test_size: float = 0.2) -> np.ndarray:
    if data.empty:
        raise ValueError("Data cannot be empty")
    X_train, X_test, y_train, y_test = train_test_split(
        data.drop('y', axis=1), data['y'], test_size=test_size, random_state=42
    )
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    return model.predict(X_test)
```

### Standard Reference
This implementation adheres to the **DRY (Don't Repeat Yourself)** and **KISS (Keep It Simple, Stupid)** principles, ensuring modular, maintainable code. It also follows scikit-learn's consistent estimator API design pattern for predictability and interoperability.
