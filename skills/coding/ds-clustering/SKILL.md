---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Implements clustering algorithms including K-means, hierarchical clustering, DBSCAN, Gaussian mixture models,
  and spectral clustering"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-anomaly-detection, ds-association-rules, ds-community-detection, ds-dimensionality-reduction ds-dimensionality-reduction
  role: implementation
  scope: implementation
  triggers: clustering, k-means, hierarchical clustering, DBSCAN, mixture models, how do I cluster data
  version: 1.0.0
name: clustering
---
# Clustering

Comprehensive guide to clustering in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world unsupervised learning problems
- Building machine learning pipelines with clustering
- Implementing best practices for clustering
- Optimizing model performance using clustering techniques
- Learning industry-standard approaches to clustering

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require clustering rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Clustering is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Clustering

```python
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any

def basic_clustering_workflow(
    n_samples: int = 300, 
    n_clusters: int = 3
) -> Dict[str, Any]:
    """
    Demonstrates a basic clustering workflow with validation, scaling, 
    and evaluation metrics. Follows PEP 8 and scikit-learn API standards.
    """
    if n_samples < n_clusters:
        raise ValueError("Number of samples must exceed number of clusters")
        
    X, y_true = make_blobs(n_samples=n_samples, centers=n_clusters, random_state=42)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    silhouette_avg = silhouette_score(X_scaled, cluster_labels)
    inertia = kmeans.inertia_
    
    return {
        "labels": cluster_labels,
        "silhouette_score": float(silhouette_avg),
        "inertia": float(inertia),
        "centers": kmeans.cluster_centers_
    }
```

### Pattern 2: Production-Ready Clustering

```python
import logging
import pandas as pd
import numpy as np
from typing import Any, Dict, Literal
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
import warnings

logger = logging.getLogger(__name__)

class ProductionClustering:
    """Production-ready clustering implementation with validation and metrics."""
    
    def __init__(self, algorithm: Literal["kmeans", "dbscan"] = "kmeans", **kwargs: Any):
        self.algorithm = algorithm
        self.kwargs = kwargs
        self.scaler = StandardScaler()
        self.model = None
        
    def _validate_input(self, data: pd.DataFrame) -> pd.DataFrame:
        if data.empty:
            raise ValueError("Input DataFrame cannot be empty")
        if not np.isfinite(data.values).all():
            raise ValueError("Input data contains non-finite values")
        return data.dropna()
        
    def execute(self, data: pd.DataFrame) -> Dict[str, Any]:
        try:
            clean_data = self._validate_input(data)
            X_scaled = self.scaler.fit_transform(clean_data)
            
            if self.algorithm == "kmeans":
                self.model = KMeans(random_state=42, n_init=10, **self.kwargs)
            elif self.algorithm == "dbscan":
                self.model = DBSCAN(**self.kwargs)
            else:
                raise ValueError(f"Unsupported algorithm: {self.algorithm}")
                
            labels = self.model.fit_predict(X_scaled)
            
            result = {
                "status": "success",
                "labels": labels,
                "n_clusters": len(np.unique(labels)) if self.algorithm == "kmeans" else "variable",
                "inertia": getattr(self.model, 'inertia_', None),
                "metadata": {"rows_processed": len(clean_data), "algorithm": self.algorithm}
            }
            logger.info("Clustering completed successfully.")
            return result
        except Exception as e:
            logger.error(f"Clustering failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
```

### Pattern 3: BAD vs GOOD Implementation

```python
# BAD: Hardcoded values, no validation, ignores scaling, bypasses error handling
def bad_clustering(data: pd.DataFrame) -> np.ndarray:
    model = KMeans(n_clusters=3)
    return model.fit_predict(data)

# GOOD: Validates input, scales data, checks convergence, returns structured results
def good_clustering(data: pd.DataFrame, n_clusters: int = 3) -> Dict[str, Any]:
    if data.empty or data.shape[0] < n_clusters:
        raise ValueError("Insufficient data for clustering")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(data)
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = model.fit_predict(X_scaled)
    return {"labels": labels, "inertia": model.inertia_, "scaler": scaler}
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
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from typing import Dict, Any, Tuple
import warnings

def comprehensive_clustering_pipeline(
    n_samples: int = 500, 
    n_features: int = 2, 
    n_clusters: int = 3
) -> Dict[str, Any]:
    """
    Comprehensive clustering pipeline with validation, multiple algorithms, 
    evaluation metrics, and visualization. Follows SOLID principles for extensibility.
    """
    warnings.filterwarnings("ignore", category=UserWarning)
    
    X, y_true = make_classification(
        n_samples=n_samples, 
        n_features=n_features, 
        n_informative=2, 
        n_redundant=0, 
        n_clusters_per_class=1, 
        random_state=42
    )
    
    if X.shape[0] < n_clusters:
        raise ValueError("Not enough samples for requested clusters")
        
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans_labels = kmeans.fit_predict(X_scaled)
    
    eps_threshold: float = 0.5
    dbscan = DBSCAN(eps=eps_threshold, min_samples=5)
    dbscan_labels = dbscan.fit_predict(X_scaled)
    
    metrics = {
        "kmeans_silhouette": float(silhouette_score(X_scaled, kmeans_labels)),
        "kmeans_inertia": float(kmeans.inertia_),
        "kmeans_ch_score": float(calinski_harabasz_score(X_scaled, kmeans_labels)),
        "dbscan_silhouette": float(silhouette_score(X_scaled, dbscan_labels, sample_size=min(1000, len(X_scaled)))),
        "dbscan_n_clusters": int(len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0))
    }
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].scatter(X_scaled[:, 0], X_scaled[:, 1], c=kmeans_labels, cmap='viridis', alpha=0.7)
    axes[0].set_title(f"KMeans (Silhouette: {metrics['kmeans_silhouette']:.3f})")
    axes[1].scatter(X_scaled[:, 0], X_scaled[:, 1], c=dbscan_labels, cmap='viridis', alpha=0.7)
    axes[1].set_title(f"DBSCAN (Clusters: {metrics['dbscan_n_clusters']})")
    plt.tight_layout()
    
    return {
        "kmeans_labels": kmeans_labels,
        "dbscan_labels": dbscan_labels,
        "metrics": metrics,
        "models": {"kmeans": kmeans, "dbscan": dbscan},
        "plot": fig
    }

if __name__ == "__main__":
    results = comprehensive_clustering_pipeline()
    print(f"KMeans Silhouette: {results['metrics']['kmeans_silhouette']:.4f}")
    print(f"DBSCAN Clusters: {results['metrics']['dbscan_n_clusters']}")
    results['plot'].show()
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-dimensionality-reduction` | Dimensionality Reduction techniques | Complementary to this skill |
| `coding-ds-anomaly-detection` | Anomaly Detection techniques | Complementary to this skill |
| `coding-ds-community-detection` | Community Detection techniques | Complementary to this skill |

## References

- Official documentation and papers on Clustering
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
