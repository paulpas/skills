---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Evaluates classification models using precision, recall, F1-score, ROC-AUC, confusion matrix, and other classification
  metrics"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-ab-testing, ds-cross-validation, ds-metrics-and-kpis, ds-model-selection
  role: implementation
  scope: implementation
  triggers: classification metrics, precision, recall, F1-score, ROC-AUC, confusion matrix
  version: 1.0.0
name: classification-metrics
---
# Classification Metrics

Comprehensive guide to classification metrics in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world model evaluation & selection problems
- Building machine learning pipelines with classification metrics
- Implementing best practices for classification metrics
- Optimizing model performance using classification metrics techniques
- Learning industry-standard approaches to classification metrics

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require classification metrics rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Classification Metrics is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Classification Metrics

```python
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)

# Generate synthetic binary classification dataset
X, y = make_classification(n_samples=1000, n_features=10, n_informative=5, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a baseline classifier
model = LogisticRegression(random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

# Calculate core classification metrics
metrics = {
    'precision': precision_score(y_test, y_pred),
    'recall': recall_score(y_test, y_pred),
    'f1_score': f1_score(y_test, y_pred),
    'roc_auc': roc_auc_score(y_test, y_prob),
    'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
}

# Output results
print(classification_report(y_test, y_pred))
print(f"ROC-AUC: {metrics['roc_auc']:.4f}")
```

### Pattern 2: Production-Ready Classification Metrics

```python
import logging
from typing import Any, Dict, List, Optional
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score

logger = logging.getLogger(__name__)

class ClassificationMetrics:
    """Production implementation of Classification Metrics"""
    
    def __init__(self, threshold: float = 0.5, metrics_list: Optional[List[str]] = None):
        self.threshold = threshold
        self.metrics_list = metrics_list or ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
        
    def execute(self, y_true: np.ndarray, y_pred: np.ndarray, y_prob: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Execute Classification Metrics on predictions"""
        if y_true.shape != y_pred.shape:
            raise ValueError("y_true and y_pred must have the same shape")
            
        results: Dict[str, Any] = {'status': 'success', 'metrics': {}}
        
        for metric_name in self.metrics_list:
            if metric_name == 'accuracy':
                results['metrics']['accuracy'] = float(accuracy_score(y_true, y_pred))
            elif metric_name == 'precision':
                results['metrics']['precision'] = float(precision_recall_fscore_support(y_true, y_pred, average='weighted')[0])
            elif metric_name == 'recall':
                results['metrics']['recall'] = float(precision_recall_fscore_support(y_true, y_pred, average='weighted')[1])
            elif metric_name == 'f1':
                results['metrics']['f1'] = float(precision_recall_fscore_support(y_true, y_pred, average='weighted')[2])
            elif metric_name == 'roc_auc' and y_prob is not None:
                results['metrics']['roc_auc'] = float(roc_auc_score(y_true, y_prob))
            else:
                logger.warning(f"Metric {metric_name} not implemented or skipped")
                
        return results
```

### BAD vs GOOD: Metric Calculation

```python
# BAD: Hardcoded thresholds, duplicated logic, and no type safety
def bad_metrics(y_true, y_pred):
    p = sum((y_pred == 1) & (y_true == 1)) / sum(y_pred == 1)
    r = sum((y_pred == 1) & (y_true == 1)) / sum(y_true == 1)
    f1 = 2 * p * r / (p + r)
    return {'precision': p, 'recall': r, 'f1': f1}

# GOOD: Vectorized operations, reusable components, and proper error handling
def good_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Calculate precision, recall, and F1 using vectorized numpy operations."""
    if not isinstance(y_true, np.ndarray) or not isinstance(y_pred, np.ndarray):
        raise TypeError("Inputs must be numpy arrays")
        
    tp = np.sum((y_pred == 1) & (y_true == 1))
    fp = np.sum((y_pred == 1) & (y_true == 0))
    fn = np.sum((y_pred == 0) & (y_true == 1))
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {'precision': float(precision), 'recall': float(recall), 'f1': float(f1)}
```

## Best Practices

- ✅ Always validate your implementation on test data
- ✅ Document your assumptions and methodology
- ✅ Use version control for reproducibility
- ✅ Monitor performance metrics in production
- ✅ Periodically review and update your approach
- ✅ Test with edge cases and outliers
- ✅ Log all significant operations for debugging
- ✅ Follow DRY and SOLID principles to keep metric calculations modular and maintainable
- ✅ Reference the scikit-learn API design standard for consistent estimator interfaces

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
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_curve, auc, confusion_matrix, ConfusionMatrixDisplay
)
from typing import Dict, Tuple, Any

def evaluate_classification_model(
    X: np.ndarray, 
    y: np.ndarray, 
    model: Any, 
    test_size: float = 0.2, 
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Comprehensive evaluation of a classification model.
    
    Args:
        X: Feature matrix
        y: Target vector
        model: Trained sklearn-compatible classifier
        test_size: Proportion of data for testing
        random_state: Random seed for reproducibility
        
    Returns:
        Dictionary containing metrics, predictions, and visualization data
    """
    if X.shape[0] != y.shape[0]:
        raise ValueError("Feature matrix and target vector must have matching row counts")
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred),
        'roc_auc': auc(*roc_curve(y_test, y_prob)[:2]),
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
    }
    
    return {
        'metrics': metrics,
        'y_test': y_test,
        'y_pred': y_pred,
        'y_prob': y_prob
    }

if __name__ == "__main__":
    # Generate dataset
    X, y = make_classification(n_samples=2000, n_features=8, n_classes=2, random_state=123)
    
    # Initialize and evaluate
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    results = evaluate_classification_model(X, y, clf)
    
    # Print metrics
    for k, v in results['metrics'].items():
        print(f"{k}: {v:.4f}")
        
    # Visualize confusion matrix
    cm = confusion_matrix(results['y_test'], results['y_pred'])
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Class 0', 'Class 1'])
    disp.plot(cmap='Blues')
    plt.title('Confusion Matrix')
    plt.show()
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-cross-validation` | Cross Validation techniques | Complementary to this skill |
| `coding-ds-model-selection` | Model Selection techniques | Complementary to this skill |
| `coding-ds-ab-testing` | Ab Testing techniques | Complementary to this skill |

## References

- Official documentation and papers on Classification Metrics
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
