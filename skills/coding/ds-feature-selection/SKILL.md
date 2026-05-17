---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Selects relevant features using univariate selection, recursive elimination, stability selection, and importance-based
  methods"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-feature-engineering, ds-feature-interaction, ds-hyperparameter-tuning, ds-model-interpretation ds-model-interpretation
  role: implementation
  scope: implementation
  triggers: feature selection, feature importance, recursive elimination, univariate selection, feature selection methods
  version: 1.0.0
name: feature-selection
---
# Feature Selection

Comprehensive guide to feature selection in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world feature engineering problems
- Building machine learning pipelines with feature selection
- Implementing best practices for feature selection
- Optimizing model performance using feature selection techniques
- Learning industry-standard approaches to feature selection

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require feature selection rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Feature Selection is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Feature Selection

```python
# BAD: Fitting selector on full dataset before splitting causes data leakage
import pandas as pd
import numpy as np
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.model_selection import train_test_split

X = pd.DataFrame(np.random.randn(100, 10), columns=[f"feat_{i}" for i in range(10)])
y = np.random.randint(0, 2, 100)
selector = SelectKBest(f_classif, k=5)
X_selected = selector.fit_transform(X, y)  # Data leakage: information from test set leaks into training
X_train, X_test, y_train, y_test = train_test_split(X_selected, y, random_state=42)

# GOOD: Using Pipeline ensures proper train/test separation and prevents leakage
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

pipeline = Pipeline([
    ('selector', SelectKBest(f_classif, k=5)),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
])
scores = cross_val_score(pipeline, X, y, cv=5, scoring='accuracy')
print(f"Cross-validated accuracy: {scores.mean():.3f} (+/- {scores.std() * 2:.3f})")
```

### Pattern 2: Production-Ready Feature Selection

```python
import logging
import pandas as pd
import numpy as np
from typing import Any, Dict, List
from sklearn.feature_selection import SelectFromModel
from sklearn.ensemble import RandomForestClassifier
from sklearn.exceptions import ConvergenceWarning
import warnings

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=ConvergenceWarning)

class FeatureSelectionPipeline:
    """Production-grade feature selection with importance-based filtering.
    Follows SOLID principles for maintainability and testability."""
    
    def __init__(self, threshold: float = 0.01, max_features: int = None) -> None:
        self.threshold = threshold
        self.max_features = max_features
        self.selector = SelectFromModel(
            RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
            threshold=threshold
        )
        self.selected_features: List[str] = []
        
    def execute(self, data: pd.DataFrame, target_col: str) -> Dict[str, Any]:
        """Execute feature selection and return structured results."""
        if target_col not in data.columns:
            raise ValueError(f"Target column '{target_col}' not found in data.")
            
        X = data.drop(columns=[target_col])
        y = data[target_col]
        
        if X.shape[1] == 0:
            raise ValueError("No features available for selection.")
            
        self.selector.fit(X, y)
        self.selected_features = X.columns[self.selector.get_support()].tolist()
        
        X_selected = self.selector.transform(X)
        
        result = {
            'status': 'success',
            'original_features': X.shape[1],
            'selected_features': len(self.selected_features),
            'feature_names': self.selected_features,
            'transformed_data': X_selected,
            'importance_scores': dict(zip(X.columns, self.selector.estimator_.feature_importances_))
        }
        logger.info(f"Selected {len(self.selected_features)} features from {X.shape[1]}")
        return result
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
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_selection import SelectKBest, f_classif, RFECV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline

def run_comprehensive_feature_selection() -> Dict[str, Any]:
    """Demonstrates multiple feature selection strategies on a synthetic dataset."""
    # Generate realistic classification dataset
    X, y = make_classification(
        n_samples=500, n_features=20, n_informative=5, 
        n_redundant=3, n_classes=2, random_state=42
    )
    feature_names = [f"feature_{i}" for i in range(X.shape[1])]
    df = pd.DataFrame(X, columns=feature_names)
    df['target'] = y
    
    X_train, X_test, y_train, y_test = train_test_split(
        df.drop('target', axis=1), df['target'], test_size=0.2, random_state=42
    )
    
    # Method 1: Univariate Selection (SelectKBest)
    selector_kbest = SelectKBest(score_func=f_classif, k=5)
    X_train_kbest = selector_kbest.fit_transform(X_train, y_train)
    X_test_kbest = selector_kbest.transform(X_test)
    
    clf_kbest = RandomForestClassifier(n_estimators=100, random_state=42)
    clf_kbest.fit(X_train_kbest, y_train)
    y_pred_kbest = clf_kbest.predict(X_test_kbest)
    acc_kbest = accuracy_score(y_test, y_pred_kbest)
    print(f"SelectKBest Accuracy: {acc_kbest:.4f}")
    
    # Method 2: Recursive Feature Elimination with Cross-Validation
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rfecv = RFECV(estimator=rf, step=1, cv=5, scoring='accuracy')
    rfecv.fit(X_train, y_train)
    X_train_rfecv = rfecv.transform(X_train)
    X_test_rfecv = rfecv.transform(X_test)
    
    clf_rfecv = RandomForestClassifier(n_estimators=100, random_state=42)
    clf_rfecv.fit(X_train_rfecv, y_train)
    y_pred_rfecv = clf_rfecv.predict(X_test_rfecv)
    acc_rfecv = accuracy_score(y_test, y_pred_rfecv)
    print(f"RFECV Accuracy: {acc_rfecv:.4f} (Selected {rfecv.n_features_} features)")
    
    # Method 3: Importance-Based Selection via Pipeline
    pipeline = Pipeline([
        ('selector', SelectKBest(f_classif, k=8)),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    pipeline.fit(X_train, y_train)
    y_pred_pipe = pipeline.predict(X_test)
    acc_pipe = accuracy_score(y_test, y_pred_pipe)
    print(f"Pipeline Accuracy: {acc_pipe:.4f}")
    
    return {
        'kbest_acc': acc_kbest,
        'rfecv_acc': acc_rfecv,
        'pipeline_acc': acc_pipe,
        'rfecv_selected_features': rfecv.support_
    }

if __name__ == "__main__":
    results = run_comprehensive_feature_selection()
    print("\nFinal Results:", results)
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-feature-engineering` | Feature Engineering techniques | Complementary to this skill |
| `coding-ds-model-interpretation` | Model Interpretation techniques | Complementary to this skill |
| `coding-ds-hyperparameter-tuning` | Hyperparameter Tuning techniques | Complementary to this skill |

## References

- Official documentation and papers on Feature Selection
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
