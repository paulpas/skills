---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Implements data versioning, lineage tracking, provenance management, and reproducible data pipelines for experiment
  tracking and governance"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-data-collection, ds-data-ingestion, ds-data-privacy, ds-reproducible-research
  role: implementation
  scope: implementation
  triggers: data versioning, data lineage, provenance, reproducibility, data governance, how do i track data
  version: 1.0.0
name: data-versioning
---
# Data Versioning

Comprehensive guide to data versioning in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world data collection & ingestion problems
- Building machine learning pipelines with data versioning
- Implementing best practices for data versioning
- Optimizing model performance using data versioning techniques
- Learning industry-standard approaches to data versioning

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require data versioning rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Data Versioning is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Data Versioning

```python
import pandas as pd
import numpy as np
import hashlib
from typing import Dict, Any

def compute_data_version(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute a deterministic version ID and metadata for a DataFrame.
    Follows DRY principle by centralizing hashing logic.
    """
    if data is None or data.empty:
        raise ValueError("Input DataFrame cannot be None or empty")
        
    # Convert DataFrame to deterministic byte representation
    data_bytes = data.to_csv(index=False).encode('utf-8')
    version_hash = hashlib.sha256(data_bytes).hexdigest()
    
    metadata = {
        'version_id': version_hash,
        'rows': len(data),
        'columns': list(data.columns),
        'dtypes': {col: str(dtype) for col, dtype in data.dtypes.items()},
        'checksum': hashlib.md5(data_bytes).hexdigest(),
        'created_at': pd.Timestamp.now().isoformat()
    }
    return metadata

# Example usage
if __name__ == "__main__":
    sample_df = pd.DataFrame({
        'feature_a': np.random.randn(50),
        'feature_b': np.random.randint(0, 10, 50),
        'target': np.random.choice([0, 1], 50)
    })
    version_info = compute_data_version(sample_df)
    print(f"Version ID: {version_info['version_id'][:16]}...")
    print(f"Rows: {version_info['rows']}, Columns: {version_info['columns']}")
```

### Pattern 2: Production-Ready Data Versioning

```python
import logging
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd
import hashlib

logger = logging.getLogger(__name__)

class DataVersionManager:
    """
    Production-grade data versioning with lineage tracking and reproducibility checks.
    Implements core concepts from DVC and LakeFS specifications.
    """
    
    def __init__(self, storage_path: str = "./data_versions"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.version_log: List[Dict[str, Any]] = []
        self._load_existing_versions()
        
    def _load_existing_versions(self) -> None:
        """Load existing version records from storage."""
        log_file = os.path.join(self.storage_path, "version_log.json")
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    self.version_log = json.load(f)
                logger.info(f"Loaded {len(self.version_log)} existing versions")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load version log: {e}")
                self.version_log = []
                
    def create_version(self, data: pd.DataFrame, name: str = "default") -> Dict[str, Any]:
        """Create a new version of the dataset with lineage tracking."""
        if data.empty:
            raise ValueError("Input data cannot be empty")
            
        data_bytes = data.to_csv(index=False).encode('utf-8')
        version_id = hashlib.sha256(data_bytes).hexdigest()
        
        version_record = {
            'version_id': version_id,
            'name': name,
            'timestamp': datetime.now().isoformat(),
            'rows': len(data),
            'columns': list(data.columns),
            'checksum': hashlib.md5(data_bytes).hexdigest(),
            'lineage': []
        }
        
        # Track lineage: link to previous version if exists
        if self.version_log:
            version_record['lineage'].append(self.version_log[-1]['version_id'])
            
        self.version_log.append(version_record)
        self._save_log()
        logger.info(f"Created version {version_id[:8]}... for dataset '{name}'")
        return version_record
        
    def validate_reproducibility(self, data: pd.DataFrame, target_version_id: str) -> bool:
        """Check if current data matches a stored version for reproducibility."""
        if data.empty:
            return False
            
        data_bytes = data.to_csv(index=False).encode('utf-8')
        current_hash = hashlib.sha256(data_bytes).hexdigest()
        matches = current_hash == target_version_id
        logger.info(f"Reproducibility check: {'PASSED' if matches else 'FAILED'}")
        return matches
        
    def get_version_history(self) -> List[Dict[str, Any]]:
        """Return full version history."""
        return self.version_log.copy()
        
    def _save_log(self) -> None:
        """Persist version log to disk."""
        log_file = os.path.join(self.storage_path, "version_log.json")
        try:
            with open(log_file, 'w') as f:
                json.dump(self.version_log, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save version log: {e}")
```

### BAD vs GOOD Implementation

```python
# BAD: Fragile, no error handling, hardcoded paths, ignores lineage
def bad_versioning(df):
    path = "/tmp/data.csv"
    df.to_csv(path)
    return {"status": "ok"}

# GOOD: Robust, type-hinted, validates input, tracks lineage, follows DRY
def good_versioning(df: pd.DataFrame, manager: DataVersionManager) -> Dict[str, Any]:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Expected pandas DataFrame")
    if df.empty:
        raise ValueError("DataFrame cannot be empty")
    return manager.create_version(df, name="validated_dataset")
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
import logging
from typing import Dict, Any
from data_versioning_manager import DataVersionManager  # Assumes Pattern 2 is saved as data_versioning_manager.py

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def run_data_versioning_workflow() -> Dict[str, Any]:
    """
    End-to-end data versioning workflow demonstrating lineage tracking,
    reproducibility validation, and metadata management.
    """
    # Initialize manager
    manager = DataVersionManager(storage_path="./experiment_versions")
    
    # Generate reproducible sample dataset
    np.random.seed(42)
    raw_data = pd.DataFrame({
        'user_id': np.arange(1000),
        'age': np.random.randint(18, 70, 1000),
        'income': np.random.normal(50000, 15000, 1000),
        'purchase_flag': np.random.choice([0, 1], 1000, p=[0.7, 0.3])
    })
    
    # Step 1: Create initial version
    v1 = manager.create_version(raw_data, name="raw_data_v1")
    print(f"Version 1 created: {v1['version_id'][:16]}...")
    
    # Step 2: Simulate data transformation
    transformed_data = raw_data.copy()
    transformed_data['age_group'] = pd.cut(transformed_data['age'], bins=[0, 25, 40, 60, 100], labels=['young', 'mid', 'senior', 'elder'])
    transformed_data['income_log'] = np.log1p(transformed_data['income'])
    
    # Step 3: Create transformed version (lineage automatically links to v1)
    v2 = manager.create_version(transformed_data, name="transformed_data_v1")
    print(f"Version 2 created: {v2['version_id'][:16]}...")
    print(f"Lineage: {v2['lineage']}")
    
    # Step 4: Validate reproducibility
    is_reproducible = manager.validate_reproducibility(transformed_data, v2['version_id'])
    print(f"Reproducibility check: {'PASSED' if is_reproducible else 'FAILED'}")
    
    # Step 5: Verify failure case
    corrupted_data = transformed_data.copy()
    corrupted_data.loc[0, 'income_log'] = 999.0
    is_corrupted = manager.validate_reproducibility(corrupted_data, v2['version_id'])
    print(f"Corruption detection: {'PASSED' if not is_corrupted else 'FAILED'}")
    
    return {
        'v1_id': v1['version_id'],
        'v2_id': v2['version_id'],
        'lineage': v2['lineage'],
        'reproducible': is_reproducible,
        'corruption_detected': not is_corrupted
    }

if __name__ == "__main__":
    results = run_data_versioning_workflow()
    print("\nWorkflow Results:", results)
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-reproducible-research` | Reproducible Research techniques | Complementary to this skill |
| `coding-ds-data-collection` | Data Collection techniques | Complementary to this skill |
| `coding-ds-data-ingestion` | Data Ingestion techniques | Complementary to this skill |

## References

- Official documentation and papers on Data Versioning
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
