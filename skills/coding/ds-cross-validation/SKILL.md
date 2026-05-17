---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Implements k-fold cross-validation, stratified cross-validation, time-series cross-validation, and model validation
  strategies"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-bias-variance-tradeoff, ds-classification-metrics, ds-hyperparameter-tuning, ds-model-selection ds-regression-evaluation
  role: implementation
  scope: implementation
  triggers: cross-validation, k-fold, stratified cross-validation, time-series cross-validation, validation
  version: 1.0.0
name: cross-validation
---
# Cross-Validation

Comprehensive guide to cross-validation in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world model evaluation & selection problems
- Building machine learning pipelines with cross-validation
- Implementing best practices for cross-validation
- Optimizing model performance using cross-validation techniques
- Learning industry-standard approaches to cross-validation

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require cross-validation rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Cross-Validation is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Cross-Validation

```python
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.metrics import accuracy_score, classification_report

def basic_kfold_cv(X: np.ndarray, y: np.ndarray, n_splits: int = 5) -> dict:
    """Perform basic k-fold cross-validation and return metrics."""
    if X.shape[0] != y.shape[0]:
        raise ValueError("X and y must have the same number of samples.")
    
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    scores = cross_val_score(model, X, y, cv=kf, scoring='accuracy')
    
    # Generate predictions for the first fold to demonstrate usage
    train_idx, test_idx = next(kf.split(X))
    model.fit(X[train_idx], y[train_idx])
    y_pred = model.predict(X[test_idx])
    
    return {
        'mean_accuracy': float(np.mean(scores)),
        'std_accuracy': float(np.std(scores)),
        'fold_scores': scores.tolist(),
        'first_fold_report': classification_report(y[test_idx], y_pred, output_dict=True)
    }

# Example usage with synthetic data
if __name__ == "__main__":
    X, y = make_classification(n_samples=500, n_features=10, n_classes=2, random_state=42)
    results = basic_kfold_cv(X, y, n_splits=5)
    print(f"Mean CV Accuracy: {results['mean_accuracy']:.4f} (+/- {results['std_accuracy']:.4f})")
```

### Pattern 2: Production-Ready Cross-Validation

```python
import logging
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional
from sklearn.model_selection import StratifiedKFold, TimeSeriesSplit, cross_validate
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.datasets import load_breast_cancer

logger = logging.getLogger(__name__)

class ProductionCrossValidator:
    """Production-grade cross-validation wrapper with logging and error handling."""
    
    def __init__(self, cv_strategy: str = 'stratified', n_splits: int = 5, random_state: int = 42):
        self.cv_strategy = cv_strategy
        self.n_splits = n_splits
        self.random_state = random_state
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def _get_cv_splitter(self, y: np.ndarray) -> Any:
        if self.cv_strategy == 'stratified':
            return StratifiedKFold(n_splits=self.n_splits, shuffle=True, random_state=self.random_state)
        elif self.cv_strategy == 'timeseries':
            return TimeSeriesSplit(n_splits=self.n_splits)
        else:
            raise ValueError(f"Unsupported CV strategy: {self.cv_strategy}")
            
    def execute(self, X: pd.DataFrame, y: pd.Series, model: Any = None) -> Dict[str, Any]:
        """Execute cross-validation on provided data and model."""
        try:
            if X is None or y is None:
                raise ValueError("Input data cannot be None")
            if X.shape[0] != y.shape[0]:
                raise ValueError("X and y must have matching sample counts")
                
            if model is None:
                model = Pipeline([
                    ('scaler', StandardScaler()),
                    ('classifier', GradientBoostingClassifier(n_estimators=100, random_state=self.random_state))
                ])
                
            cv_splitter = self._get_cv_splitter(y.values)
            scoring_metrics = ['accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted']
            
            cv_results = cross_validate(
                model, X, y, cv=cv_splitter, 
                scoring=scoring_metrics, return_train_score=True, n_jobs=-1
            )
            
            self.logger.info(f"CV completed with strategy: {self.cv_strategy}")
            return {
                'status': 'success',
                'cv_strategy': self.cv_strategy,
                'n_splits': self.n_splits,
                'test_scores': {k: float(np.mean(v)) for k, v in cv_results.items() if k.startswith('test_')},
                'train_scores': {k: float(np.mean(v)) for k, v in cv_results.items() if k.startswith('train_')},
                'fit_times': float(np.mean(cv_results['fit_time'])),
                'score_times': float(np.mean(cv_results['score_time']))
            }
        except Exception as e:
            self.logger.error(f"Cross-validation failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = load_breast_cancer()
    X, y = pd.DataFrame(data.data, columns=data.feature_names), pd.Series(data.target)
    validator = ProductionCrossValidator(cv_strategy='stratified', n_splits=5)
    results = validator.execute(X, y)
    print(f"Test F1 Score: {results['test_scores']['f1_weighted']:.4f}")
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
from sklearn.model_selection import cross_val_score, StratifiedKFold, learning_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

def run_comprehensive_cv_analysis(X: pd.DataFrame, y: pd.Series) -> dict:
    """
    Run comprehensive cross-validation analysis including metrics and learning curves.
    """
    if X.shape[0] != y.shape[0]:
        raise ValueError("X and y must have the same number of samples.")
        
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scoring = ['accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted']
    
    # 1. Cross-validation scores
    cv_scores = cross_val_score(pipeline, X, y, cv=cv, scoring=scoring, n_jobs=-1)
    
    # 2. Final model training on full data for visualization
    pipeline.fit(X, y)
    y_pred = pipeline.predict(X)
    
    # 3. Learning curve for bias-variance analysis
    train_sizes, train_scores, val_scores = learning_curve(
        pipeline, X, y, cv=cv, scoring='accuracy', n_jobs=-1, train_sizes=np.linspace(0.1, 1.0, 10)
    )
    mean_train = np.mean(train_scores, axis=1)
    std_train = np.std(train_scores, axis=1)
    mean_val = np.mean(val_scores, axis=1)
    std_val = np.std(val_scores, axis=1)
    
    return {
        'cv_mean_scores': {k: float(np.mean(cv_scores[:, i])) for i, k in enumerate(scoring)},
        'cv_std_scores': {k: float(np.std(cv_scores[:, i])) for i, k in enumerate(scoring)},
        'final_accuracy': float(accuracy_score(y, y_pred)),
        'learning_curve': {
            'train_sizes': train_sizes.tolist(),
            'mean_train_scores': mean_train.tolist(),
            'mean_val_scores': mean_val.tolist()
        }
    }

def plot_cv_results(results: dict, save_path: str = 'cv_analysis.png'):
    """Plot learning curve and CV metrics."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot Learning Curve
    lc = results['learning_curve']
    axes[0].fill_between(lc['train_sizes'], 
                         np.array(lc['mean_train_scores']) - np.array(lc['mean_val_scores']),
                         np.array(lc['mean_train_scores']) + np.array(lc['mean_val_scores']),
                         alpha=0.1, color='blue')
    axes[0].plot(lc['train_sizes'], lc['mean_train_scores'], 'o-', color='blue', label='Training Score')
    axes[0].plot(lc['train_sizes'], lc['mean_val_scores'], 'o-', color='red', label='Validation Score')
    axes[0].set_xlabel('Training Examples')
    axes[0].set_ylabel('Accuracy')
    axes[0].set_title('Learning Curve')
    axes[0].legend()
    
    # Plot CV Metrics
    metrics = list(results['cv_mean_scores'].keys())
    means = list(results['cv_mean_scores'].values())
    stds = list(results['cv_std_scores'].values())
    axes[1].bar(metrics, means, yerr=stds, capsize=5, color='green', alpha=0.7)
    axes[1].set_ylabel('Score')
    axes[1].set_title('Cross-Validation Metrics')
    axes[1].set_ylim(0, 1.1)
    
    plt.tight_layout()
    plt.savefig(save_path)
    plt.show()
    print(f"Results saved to {save_path}")

if __name__ == "__main__":
    X, y = make_classification(n_samples=1000, n_features=20, n_informative=10, n_classes=2, random_state=42)
    X_df = pd.DataFrame(X, columns=[f'feat_{i}' for i in range(X.shape[1])])
    y_series = pd.Series(y)
    
    results = run_comprehensive_cv_analysis(X_df, y_series)
    print("CV Mean Scores:", results['cv_mean_scores'])
    plot_cv_results(results)
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-hyperparameter-tuning` | Hyperparameter Tuning techniques | Complementary to this skill |
| `coding-ds-model-selection` | Model Selection techniques | Complementary to this skill |
| `coding-ds-classification-metrics` | Classification Metrics techniques | Complementary to this skill |

## References

- Official documentation and papers on Cross-Validation
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
