---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Provides Reduces data dimensionality using PCA, t-SNE, UMAP, autoencoders, and other feature extraction methods
  for visualization and efficiency"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-clustering, ds-community-detection, ds-eda, ds-feature-engineering
  role: implementation
  scope: implementation
  triggers: dimensionality reduction, PCA, t-SNE, UMAP, feature extraction, how do i reduce dimensions
  version: 1.0.0
name: dimensionality-reduction
---
# Dimensionality Reduction

Comprehensive guide to dimensionality reduction in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world unsupervised learning problems
- Building machine learning pipelines with dimensionality reduction
- Implementing best practices for dimensionality reduction
- Optimizing model performance using dimensionality reduction techniques
- Learning industry-standard approaches to dimensionality reduction

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require dimensionality reduction rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Dimensionality Reduction is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Dimensionality Reduction

```python
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_iris

def basic_dimensionality_reduction(data: pd.DataFrame, n_components: int = 2) -> pd.DataFrame:
    """Apply PCA for basic dimensionality reduction with proper scaling."""
    if data.empty:
        raise ValueError("Input DataFrame cannot be empty")
    
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data)
    
    pca = PCA(n_components=n_components)
    reduced_data = pca.fit_transform(scaled_data)
    
    component_names = [f"PC{i+1}" for i in range(n_components)]
    reduced_df = pd.DataFrame(reduced_data, columns=component_names, index=data.index)
    
    explained_variance = pca.explained_variance_ratio_
    print(f"Explained variance ratio: {explained_variance}")
    print(f"Total variance explained: {sum(explained_variance):.2%}")
    
    return reduced_df

# Example usage
if __name__ == "__main__":
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    result = basic_dimensionality_reduction(df, n_components=2)
    print(result.head())
```

### Pattern 2: Production-Ready Dimensionality Reduction

```python
import logging
import numpy as np
import pandas as pd
from typing import Any, Dict, Optional
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import umap

logger = logging.getLogger(__name__)

class ProductionDimensionalityReduction:
    """Production-grade dimensionality reduction pipeline with method switching."""
    
    def __init__(self, method: str = "pca", n_components: int = 2, random_state: int = 42):
        self.method = method
        self.n_components = n_components
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.reducer = None
        self.is_fitted = False

    def _initialize_reducer(self) -> None:
        if self.method == "pca":
            self.reducer = PCA(n_components=self.n_components, random_state=self.random_state)
        elif self.method == "umap":
            self.reducer = umap.UMAP(n_components=self.n_components, random_state=self.random_state)
        else:
            raise ValueError(f"Unsupported method: {self.method}")

    def execute(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Execute dimensionality reduction on input data with full validation."""
        if data.empty:
            raise ValueError("Input data cannot be empty")
        
        self._initialize_reducer()
        scaled_data = self.scaler.fit_transform(data)
        reduced_data = self.reducer.fit_transform(scaled_data)
        self.is_fitted = True
        
        result = {
            "reduced_data": reduced_data,
            "method": self.method,
            "n_components": self.n_components,
            "explained_variance": getattr(self.reducer, "explained_variance_ratio_", None),
            "shape": reduced_data.shape
        }
        logger.info(f"Successfully reduced {data.shape[1]} dimensions to {self.n_components}")
        return result

# Example usage
if __name__ == "__main__":
    df = pd.DataFrame(np.random.randn(100, 10), columns=[f"feat_{i}" for i in range(10)])
    pipeline = ProductionDimensionalityReduction(method="pca", n_components=2)
    output = pipeline.execute(df)
    print(f"Reduced shape: {output['shape']}")
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
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
from typing import Dict, Any

def complete_dimensionality_reduction_workflow(data: pd.DataFrame, target: pd.Series = None, n_components: int = 2) -> Dict[str, Any]:
    """
    Complete workflow for dimensionality reduction with validation and visualization.
    """
    if data.empty or (target is not None and len(target) != len(data)):
        raise ValueError("Data and target must be aligned and non-empty")
    
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data)
    
    pca = PCA(n_components=n_components)
    pca_result = pca.fit_transform(scaled_data)
    
    tsne = TSNE(n_components=n_components, random_state=42, perplexity=min(30, len(data)-1))
    tsne_result = tsne.fit_transform(scaled_data)
    
    explained_var = pca.explained_variance_ratio_.sum()
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    if target is not None:
        for label in target.unique():
            mask = target == label
            axes[0].scatter(pca_result[mask, 0], pca_result[mask, 1], label=str(label))
            axes[1].scatter(tsne_result[mask, 0], tsne_result[mask, 1], label=str(label))
        axes[0].legend()
        axes[1].legend()
    
    axes[0].set_title(f"PCA (Explained Var: {explained_var:.2%})")
    axes[1].set_title("t-SNE")
    plt.tight_layout()
    plt.show()
    
    return {
        "pca_transform": pca_result,
        "tsne_transform": tsne_result,
        "explained_variance_ratio": explained_var,
        "scaler": scaler,
        "pca_model": pca,
        "tsne_model": tsne
    }

if __name__ == "__main__":
    X, y = make_classification(n_samples=500, n_features=20, n_informative=10, random_state=42)
    df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(20)])
    results = complete_dimensionality_reduction_workflow(df, y, n_components=2)
    print(f"PCA Explained Variance: {results['explained_variance_ratio']:.4f}")
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-clustering` | Clustering techniques | Complementary to this skill |
| `coding-ds-eda` | Eda techniques | Complementary to this skill |
| `coding-ds-feature-engineering` | Feature Engineering techniques | Complementary to this skill |

## References

- Official documentation and papers on Dimensionality Reduction
- Industry best practices and standards
- Implementation examples from the scikit-learn, TensorFlow, and PyTorch libraries

## BAD vs GOOD Examples

### BAD: Ignoring Data Scaling and Validation
```python
import pandas as pd
from sklearn.decomposition import PCA

def bad_reduction(df: pd.DataFrame) -> pd.DataFrame:
    """Naive implementation that fails on unscaled or empty data."""
    pca = PCA(n_components=2)
    # Ignores feature scaling; high-magnitude features dominate variance
    # No validation for empty DataFrames or non-numeric columns
    # Violates DRY principle by duplicating scaling logic in downstream code
    return pca.fit_transform(df)

# This will produce misleading results if features have different scales
# and will crash if the input DataFrame is empty or contains strings
```

### GOOD: Proper Scaling, Validation, and Modular Design
```python
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any

def good_reduction(df: pd.DataFrame, n_components: int = 2) -> Dict[str, Any]:
    """Robust implementation following DRY and KISS principles."""
    if df.empty:
        raise ValueError("DataFrame cannot be empty")
    
    numeric_cols = df.select_dtypes(include=[np.number])
    if numeric_cols.empty:
        raise ValueError("No numeric columns found for dimensionality reduction")
    
    scaler = StandardScaler()
    scaled = scaler.fit_transform(numeric_cols)
    
    pca = PCA(n_components=n_components)
    reduced = pca.fit_transform(scaled)
    
    return {
        "reduced_data": reduced,
        "explained_variance": pca.explained_variance_ratio_.sum(),
        "scaler": scaler,
        "pca_model": pca,
        "original_columns": numeric_cols.columns.tolist()
    }

# Usage demonstrates proper error handling and modular component reuse
if __name__ == "__main__":
    sample = pd.DataFrame({"a": [1, 2, 3], "b": [100, 200, 300], "c": ["x", "y", "z"]})
    output = good_reduction(sample, n_components=2)
    print(f"Explained variance: {output['explained_variance']:.4f}")
```

## Constraints

### MUST DO
- Include at least one BAD/GOOD code example pair
- Reference a relevant standard (OWASP, SOLID, DRY, KISS, etc.)
- Use type hints on all function signatures

### MUST NOT DO
- Use magic numbers or hardcoded configuration values
- Bypass error handling for assumed-valid inputs
- Write functions longer than 50 lines without decomposition

---

*Last updated: 2026-04-24*

---
