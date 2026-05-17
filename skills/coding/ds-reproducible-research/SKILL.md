---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Implements reproducible research practices including code organization, environment management, documentation,
  and experiment tracking"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-data-versioning, ds-explainability, ds-model-robustness, ds-privacy-ml
  role: implementation
  scope: implementation
  triggers: reproducible research, reproducibility, code organization, environment, notebooks, how do I reproduce
  version: 1.0.0
name: reproducible-research
---
# Reproducible Research

Comprehensive guide to reproducible research in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world reproducibility & responsible ai problems
- Building machine learning pipelines with reproducible research
- Implementing best practices for reproducible research
- Optimizing model performance using reproducible research techniques
- Learning industry-standard approaches to reproducible research

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require reproducible research rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Reproducible Research is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Reproducible Research

```python
import os
import random
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any

logger = logging.getLogger(__name__)

def setup_reproducible_environment(seed: int = 42) -> Dict[str, Any]:
    """
    Configures deterministic behavior for Python, NumPy, and random modules.
    Follows DRY principles by centralizing seed configuration.
    Returns configuration dictionary for tracking and audit trails.
    """
    os.environ['PYTHONHASHSEED'] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    
    config = {
        'seed': seed,
        'environment': 'reproducible',
        'timestamp': 'setup_complete',
        'libraries': {'numpy': np.__version__, 'pandas': pd.__version__}
    }
    logger.info(f"Reproducible environment configured with seed: {seed}")
    return config
```

### Pattern 2: Production-Ready Reproducible Research

```python
import os
import json
import logging
import pandas as pd
import numpy as np
from typing import Any, Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)

class ExperimentManager:
    """Manages reproducible experiment workflows with artifact tracking."""
    
    def __init__(self, project_root: str = "./experiments", seed: int = 42):
        self.project_root = Path(project_root)
        self.project_root.mkdir(parents=True, exist_ok=True)
        self.seed = seed
        self.runs: List[Dict[str, Any]] = []
        self._setup_environment()
        
    def _setup_environment(self) -> None:
        os.environ['PYTHONHASHSEED'] = str(self.seed)
        np.random.seed(self.seed)
        
    def execute(self, data: pd.DataFrame, model_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a reproducible experiment run with validation and logging."""
        if data.empty:
            raise ValueError("Input data cannot be empty")
            
        run_id = f"run_{len(self.runs) + 1:03d}"
        run_dir = self.project_root / run_id
        run_dir.mkdir(exist_ok=True)
        
        # Simulate model training & evaluation
        np.random.shuffle(data.values)
        metrics = {'accuracy': 0.85, 'f1': 0.82, 'seed': self.seed}
        
        # Save artifacts
        metadata = {
            'run_id': run_id,
            'params': model_params,
            'metrics': metrics,
            'data_shape': list(data.shape)
        }
        with open(run_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
            
        self.runs.append(metadata)
        logger.info(f"Experiment {run_id} completed successfully.")
        return metadata
```

## Best Practices

- ✅ Always validate your implementation on test data
- ✅ Document your assumptions and methodology
- ✅ Use version control for reproducibility
- ✅ Monitor performance metrics in production
- ✅ Periodically review and update your approach
- ✅ Test with edge cases and outliers
- ✅ Log all significant operations for debugging

### BAD vs GOOD Practices

```python
# BAD: Hardcoded seeds, no validation, missing logging
def bad_pipeline(data):
    np.random.seed(123)
    return data.mean()

# GOOD: Configurable seeds, input validation, structured logging
def good_pipeline(data: pd.DataFrame, seed: int = 42) -> float:
    if data.empty:
        raise ValueError("Data cannot be empty")
    np.random.seed(seed)
    logger.info(f"Processing {len(data)} rows with seed {seed}")
    return float(data.mean().mean())
```

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
import os
import json
import logging
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from typing import Dict, Any, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

def run_reproducible_pipeline(
    data: pd.DataFrame, 
    target_col: str, 
    output_dir: str = "./results"
) -> Dict[str, Any]:
    """
    Executes a fully reproducible ML pipeline with data splitting, training, 
    evaluation, and artifact persistence. Follows KISS and DRY principles.
    """
    os.makedirs(output_dir, exist_ok=True)
    seed = 42
    np.random.seed(seed)
    
    if target_col not in data.columns:
        raise ValueError(f"Target column '{target_col}' not found in data")
        
    X = data.drop(columns=[target_col])
    y = data[target_col]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed, stratify=y
    )
    
    model = RandomForestClassifier(n_estimators=100, random_state=seed)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    
    results = {
        'accuracy': acc,
        'classification_report': report,
        'train_size': len(X_train),
        'test_size': len(X_test),
        'seed': seed
    }
    
    with open(os.path.join(output_dir, "results.json"), "w") as f:
        json.dump(results, f, indent=2)
        
    logger.info(f"Pipeline completed. Accuracy: {acc:.4f}")
    return results

if __name__ == "__main__":
    X, y = make_classification(n_samples=1000, n_features=10, random_state=42)
    df = pd.DataFrame(X, columns=[f"feat_{i}" for i in range(10)])
    df['target'] = y
    res = run_reproducible_pipeline(df, 'target')
    print(f"Final Accuracy: {res['accuracy']:.4f}")
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-data-versioning` | Data Versioning techniques | Complementary to this skill |
| `coding-ds-explainability` | Explainability techniques | Complementary to this skill |
| `coding-ds-model-robustness` | Model Robustness techniques | Complementary to this skill |

## References

- Official documentation and papers on Reproducible Research
- Industry best practices and standards
- Implementation examples from the scikit-learn, TensorFlow, and PyTorch libraries
- DRY (Don't Repeat Yourself) and KISS (Keep It Simple, Stupid) software engineering principles

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
