---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Defines, selects, and monitors key performance indicators (KPIs), business metrics, and evaluation metrics
  for decision-making"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-ab-testing, ds-classification-metrics, ds-online-experiments, ds-regression-evaluation ds-regression-evaluation
  role: implementation
  scope: implementation
  triggers: metrics, KPI, key performance indicator, business metrics, metric definition, how do I choose metrics, cloudwatch,
    optimization
  version: 1.0.0
name: metrics-and-kpis
---
# Metrics and KPIs

Comprehensive guide to metrics and kpis in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world experimentation & a/b testing problems
- Building machine learning pipelines with metrics and kpis
- Implementing best practices for metrics and kpis
- Optimizing model performance using metrics and kpis techniques
- Learning industry-standard approaches to metrics and kpis

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require metrics and kpis rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Metrics and KPIs is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Metrics and KPIs

```python
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, r2_score

def compute_basic_metrics(y_true: pd.Series, y_pred: pd.Series, task_type: str = "classification") -> dict:
    """Compute basic evaluation metrics for classification or regression tasks."""
    if y_true is None or y_pred is None:
        raise ValueError("y_true and y_pred cannot be None")
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")

    metrics = {}
    if task_type == "classification":
        metrics["accuracy"] = accuracy_score(y_true, y_pred)
        metrics["precision"] = precision_score(y_true, y_pred, average="weighted", zero_division=0)
        metrics["recall"] = recall_score(y_true, y_pred, average="weighted", zero_division=0)
        metrics["f1"] = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    elif task_type == "regression":
        metrics["mse"] = mean_squared_error(y_true, y_pred)
        metrics["rmse"] = np.sqrt(metrics["mse"])
        metrics["mae"] = np.mean(np.abs(y_true - y_pred))
        metrics["r2"] = r2_score(y_true, y_pred)
    else:
        raise ValueError("task_type must be 'classification' or 'regression'")

    metrics["sample_size"] = len(y_true)
    return metrics

# Example usage
if __name__ == "__main__":
    y_true = pd.Series([0, 1, 1, 0, 1, 0, 1, 1, 0, 0])
    y_pred = pd.Series([0, 1, 0, 0, 1, 1, 1, 0, 0, 1])
    results = compute_basic_metrics(y_true, y_pred, task_type="classification")
    print("Classification Metrics:", results)
```

### Pattern 2: Production-Ready Metrics and KPIs

```python
import logging
import pandas as pd
import numpy as np
from typing import Any, Dict, List
from sklearn.metrics import classification_report, confusion_matrix

logger = logging.getLogger(__name__)

class MetricsAndKPIs:
    """Production-grade metrics and KPIs tracker and calculator."""
    
    def __init__(self, kpi_names: List[str] = None):
        self.kpi_names = kpi_names or ["accuracy", "precision", "recall", "f1", "business_roi"]
        self.history: List[Dict[str, Any]] = []
        logger.info("Initialized MetricsAndKPIs tracker")
    
    def _validate_inputs(self, y_true: pd.Series, y_pred: pd.Series) -> None:
        if not isinstance(y_true, pd.Series) or not isinstance(y_pred, pd.Series):
            raise TypeError("Inputs must be pandas Series")
        if y_true.empty or y_pred.empty:
            raise ValueError("Input Series cannot be empty")
        if len(y_true) != len(y_pred):
            raise ValueError("y_true and y_pred must have matching lengths")
    
    def execute(self, data: pd.DataFrame, target_col: str = "y_true", pred_col: str = "y_pred") -> Dict[str, Any]:
        """Execute metrics calculation on provided DataFrame."""
        try:
            self._validate_inputs(data[target_col], data[pred_col])
            y_true = data[target_col]
            y_pred = data[pred_col]

            report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
            cm = confusion_matrix(y_true, y_pred).tolist()

            f1 = report.get("macro avg", {}).get("f1-score", 0.0)
            business_roi = f1 * 1000

            result = {
                "metrics": {
                    "accuracy": report["accuracy"],
                    "precision_macro": report["macro avg"]["precision"],
                    "recall_macro": report["macro avg"]["recall"],
                    "f1_macro": report["macro avg"]["f1-score"],
                    "confusion_matrix": cm,
                    "business_roi": business_roi
                },
                "metadata": {
                    "rows_processed": len(data),
                    "kpi_names": self.kpi_names,
                    "timestamp": pd.Timestamp.now().isoformat()
                }
            }
            self.history.append(result)
            logger.info(f"Metrics computed successfully for {len(data)} rows")
            return result
        except Exception as e:
            logger.error(f"Metrics execution failed: {str(e)}")
            raise RuntimeError(f"Failed to compute metrics: {e}") from e
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
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, r2_score
import matplotlib.pyplot as plt

def implement_kpis(data: pd.DataFrame, target_col: str = "target", feature_cols: list = None) -> Dict[str, Any]:
    """
    Complete implementation of Metrics and KPIs.
    
    This example demonstrates:
    - Proper input validation
    - Core algorithm implementation
    - Error handling
    - Result formatting
    
    Args:
        data: Input DataFrame with required columns
        target_col: Name of the target column
        feature_cols: List of feature column names (auto-detected if None)
        
    Returns:
        Dictionary with results and metadata
        
    Raises:
        ValueError: If input data is invalid
        
    Example:
        >>> df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        >>> results = implement_kpis(df)
        >>> print(results)
    """
    if data is None or data.empty:
        raise ValueError("Input data cannot be None or empty")
    if target_col not in data.columns:
        raise ValueError(f"Target column '{target_col}' not found in data")
        
    feature_cols = feature_cols or [c for c in data.columns if c != target_col]
    X = data[feature_cols]
    y = data[target_col]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, average="weighted", zero_division=0),
        "recall": recall_score(y_test, y_pred, average="weighted", zero_division=0),
        "f1": f1_score(y_test, y_pred, average="weighted", zero_division=0)
    }
    
    business_kpis = {
        "estimated_conversion_lift": metrics["f1"] * 0.15,
        "cost_per_prediction": 0.002,
        "projected_roi": metrics["accuracy"] * 1200
    }
    
    results = {
        'status': 'success',
        'model_metrics': metrics,
        'business_kpis': business_kpis,
        'metadata': {
            'train_size': len(X_train),
            'test_size': len(X_test),
            'features': len(feature_cols),
            'timestamp': pd.Timestamp.now().isoformat()
        }
    }
    
    return results

# Usage and testing
if __name__ == "__main__":
    X, y = make_classification(n_samples=1000, n_features=10, n_informative=5, random_state=42)
    sample_data = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(10)])
    sample_data['target'] = y
    
    results = implement_kpis(sample_data, target_col='target')
    print(f"Status: {results['status']}")
    print(f"Model Metrics: {results['model_metrics']}")
    print(f"Business KPIs: {results['business_kpis']}")
    print(f"Processed {results['metadata']['train_size']} train, {results['metadata']['test_size']} test samples")
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-ab-testing` | Ab Testing techniques | Complementary to this skill |
| `coding-ds-classification-metrics` | Classification Metrics techniques | Complementary to this skill |
| `coding-ds-regression-evaluation` | Regression Evaluation techniques | Complementary to this skill |

## References

- Official documentation and papers on Metrics and KPIs
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
