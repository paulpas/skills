---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Detects anomalies and outliers using isolation forests, local outlier factor (LOF), one-class SVM, and isolation-based
  methods"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-clustering, ds-data-quality, ds-model-robustness
  role: implementation
  scope: implementation
  triggers: anomaly detection, outlier detection, isolation forest, LOF, one-class SVM, how do I detect anomalies
  version: 1.0.0
name: anomaly-detection
---
# Anomaly Detection

Comprehensive guide to anomaly detection in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world unsupervised learning problems
- Building machine learning pipelines with anomaly detection
- Implementing best practices for anomaly detection
- Optimizing model performance using anomaly detection techniques
- Learning industry-standard approaches to anomaly detection

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require anomaly detection rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Anomaly Detection is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Anomaly Detection

```python
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

def basic_anomaly_detection(data: pd.DataFrame, contamination: float = 0.1) -> dict:
    """Perform basic anomaly detection using Isolation Forest."""
    if data.empty:
        raise ValueError("Input DataFrame cannot be empty")

    X = data.values
    X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)

    model = IsolationForest(contamination=contamination, random_state=42, n_estimators=100)
    model.fit(X_train)

    train_scores = model.decision_function(X_train)
    test_scores = model.decision_function(X_test)
    test_labels = model.predict(X_test)

    return {
        "train_scores": train_scores,
        "test_scores": test_scores,
        "test_labels": test_labels,
        "model": model
    }
```

### Pattern 2: Production-Ready Anomaly Detection

```python
import logging
import pandas as pd
import numpy as np
from typing import Any, Dict, List
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class AnomalyDetection:
    """Production implementation of Anomaly Detection supporting multiple algorithms.
    Adheres to SOLID principles for maintainability and testability."""
    
    def __init__(self, algorithm: str = "isolation_forest", contamination: float = 0.1):
        if algorithm not in ["isolation_forest", "lof"]:
            raise ValueError("Algorithm must be 'isolation_forest' or 'lof'")
        self.algorithm = algorithm
        self.contamination = contamination
        self.scaler = StandardScaler()
        self.model = None
    
    def execute(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Execute Anomaly Detection on data"""
        if data.empty:
            raise ValueError("Input data cannot be empty")

        X = data.values
        X_scaled = self.scaler.fit_transform(X)

        if self.algorithm == "isolation_forest":
            self.model = IsolationForest(
                contamination=self.contamination,
                random_state=42,
                n_estimators=200
            )
        else:
            self.model = LocalOutlierFactor(
                n_neighbors=20,
                contamination=self.contamination,
                novelty=True
            )

        self.model.fit(X_scaled)
        scores = self.model.decision_function(X_scaled)
        labels = self.model.predict(X_scaled)

        logger.info(f"Anomaly detection completed. Found {np.sum(labels == -1)} anomalies.")
        return {
            "scores": scores,
            "labels": labels,
            "anomaly_count": int(np.sum(labels == -1)),
            "anomaly_ratio": float(np.mean(labels == -1)),
            "model_type": self.algorithm
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
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any

# BAD: Ignoring data scaling and contamination tuning leads to poor detection
def bad_anomaly_detection(data: pd.DataFrame) -> Dict[str, Any]:
    model = IsolationForest()
    model.fit(data)
    return {"labels": model.predict(data)}

# GOOD: Proper scaling, contamination tuning, and evaluation
def good_anomaly_detection(data: pd.DataFrame, contamination: float = 0.1) -> Dict[str, Any]:
    if data.empty:
        raise ValueError("Input data cannot be empty")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(data)

    model = IsolationForest(contamination=contamination, random_state=42, n_estimators=150)
    model.fit(X_scaled)

    scores = model.decision_function(X_scaled)
    labels = model.predict(X_scaled)

    return {
        "scores": scores,
        "labels": labels,
        "anomaly_count": int(np.sum(labels == -1)),
        "scaler": scaler,
        "model": model
    }

def run_full_workflow() -> None:
    """Demonstrate complete anomaly detection workflow with evaluation and visualization."""
    # Generate synthetic dataset with known anomalies
    X, y = make_classification(n_samples=500, n_features=5, n_informative=3,
                               n_redundant=1, n_clusters_per_class=1,
                               weights=[0.9, 0.1], flip_y=0.0, random_state=42)
    df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(5)])

    # Run good implementation
    results = good_anomaly_detection(df, contamination=0.1)

    # Evaluate against synthetic labels
    precision = precision_score(y, results["labels"], pos_label=-1, zero_division=0)
    recall = recall_score(y, results["labels"], pos_label=-1, zero_division=0)
    f1 = f1_score(y, results["labels"], pos_label=-1, zero_division=0)

    print(f"Precision: {precision:.3f} | Recall: {recall:.3f} | F1: {f1:.3f}")

    # Visualization
    plt.figure(figsize=(10, 6))
    plt.scatter(df.iloc[:, 0], df.iloc[:, 1], c=results["labels"], cmap="coolwarm", alpha=0.7)
    plt.title("Anomaly Detection Results (Isolation Forest)")
    plt.xlabel("Feature 0")
    plt.ylabel("Feature 1")
    plt.colorbar(label="Label (-1: Anomaly, 1: Normal)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.show()

if __name__ == "__main__":
    run_full_workflow()
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-clustering` | Clustering techniques | Complementary to this skill |
| `coding-ds-model-robustness` | Model Robustness techniques | Complementary to this skill |
| `coding-ds-data-quality` | Data Quality techniques | Complementary to this skill |

## References

- Official documentation and papers on Anomaly Detection
- Industry best practices and standards
- Implementation examples from the scikit-learn, TensorFlow, and PyTorch libraries
- SOLID principles for object
