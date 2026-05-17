---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Implements topic modeling using Latent Dirichlet Allocation (LDA), Non-negative Matrix Factorization (NMF),
  and other topic extraction methods"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-association-rules, ds-clustering, ds-dimensionality-reduction
  role: implementation
  scope: implementation
  triggers: topic modeling, LDA, NMF, topic extraction, latent dirichlet allocation, text analysis
  version: 1.0.0
name: topic-modeling
---
# Topic Modeling

Comprehensive guide to topic modeling in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world unsupervised learning problems
- Building machine learning pipelines with topic modeling
- Implementing best practices for topic modeling
- Optimizing model performance using topic modeling techniques
- Learning industry-standard approaches to topic modeling

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require topic modeling rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Topic Modeling is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Topic Modeling

```python
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from typing import List, Dict, Any

def basic_topic_modeling(texts: List[str], n_topics: int = 5) -> Dict[str, Any]:
    """
    Perform basic topic modeling using Latent Dirichlet Allocation (LDA).
    
    Args:
        texts: List of raw text documents
        n_topics: Number of topics to extract
        
    Returns:
        Dictionary containing fitted model, vectorizer, and topic-word distributions
    """
    if not texts:
        raise ValueError("Input texts list cannot be empty")
        
    # Vectorize text documents
    vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
    doc_term_matrix = vectorizer.fit_transform(texts)
    
    # Initialize and fit LDA model
    lda_model = LatentDirichletAllocation(
        n_components=n_topics,
        max_iter=10,
        learning_method='online',
        random_state=42
    )
    lda_model.fit(doc_term_matrix)
    
    # Extract top words per topic
    feature_names = vectorizer.get_feature_names_out()
    topics = {}
    for idx, topic in enumerate(lda_model.components_):
        top_words_idx = topic.argsort()[:-10:-1]
        topics[f'topic_{idx}'] = [feature_names[i] for i in top_words_idx]
        
    return {
        'model': lda_model,
        'vectorizer': vectorizer,
        'topics': topics,
        'doc_term_matrix': doc_term_matrix
    }
```

### Pattern 2: Production-Ready Topic Modeling

```python
import logging
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from sklearn.pipeline import Pipeline
from typing import Any, Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class TopicModeling:
    """Production-grade implementation of Topic Modeling using NMF"""
    
    def __init__(self, n_topics: int = 5, max_features: int = 1000, random_state: int = 42):
        self.n_topics = n_topics
        self.max_features = max_features
        self.random_state = random_state
        self.pipeline: Optional[Pipeline] = None
        self.feature_names: List[str] = []
        
    def _validate_input(self, data: pd.DataFrame, text_column: str) -> None:
        if text_column not in data.columns:
            raise ValueError(f"Column '{text_column}' not found in DataFrame")
        if data[text_column].isnull().any():
            logger.warning("Dropping rows with missing text data")
            data = data.dropna(subset=[text_column])
        if len(data) < self.n_topics:
            raise ValueError("Dataset size must be greater than n_topics")
            
    def _build_pipeline(self) -> Pipeline:
        vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            stop_words='english',
            ngram_range=(1, 2)
        )
        nmf_model = NMF(
            n_components=self.n_topics,
            init='nndsvd',
            random_state=self.random_state,
            max_iter=200
        )
        return Pipeline([('tfidf', vectorizer), ('nmf', nmf_model)])
        
    def execute(self, data: pd.DataFrame, text_column: str = 'text') -> Dict[str, Any]:
        """Execute Topic Modeling on data"""
        self._validate_input(data, text_column)
        
        self.pipeline = self._build_pipeline()
        tfidf_matrix = self.pipeline.named_steps['tfidf'].fit_transform(data[text_column])
        self.pipeline.fit(tfidf_matrix)
        
        feature_names = self.pipeline.named_steps['tfidf'].get_feature_names_out()
        topic_words = {}
        for i, topic in enumerate(self.pipeline.named_steps['nmf'].components_):
            top_indices = topic.argsort()[:-10:-1]
            topic_words[f'topic_{i}'] = [feature_names[idx] for idx in top_indices]
            
        reconstructed = self.pipeline.named_steps['nmf'].transform(tfidf_matrix) @ \
                        self.pipeline.named_steps['nmf'].components_
        inertia = float(np.linalg.norm(tfidf_matrix.toarray() - reconstructed))
        
        return {
            'topics': topic_words,
            'inertia': inertia,
            'pipeline': self.pipeline,
            'document_topics': self.pipeline.named_steps['nmf'].transform(tfidf_matrix)
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
- Follow DRY (Don't Repeat Yourself) and KISS (Keep It Simple, Stupid) principles for maintainable code

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
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from typing import Dict, Any, List

def _preprocess_texts(data: pd.DataFrame, text_col: str) -> List[str]:
    if text_col not in data.columns:
        raise ValueError(f"Column '{text_col}' not found")
    return data[text_col].dropna().astype(str).tolist()

def _build_vectorizer() -> CountVectorizer:
    return CountVectorizer(max_df=0.95, min_df=2, stop_words='english')

def _train_lda(doc_term_matrix: np.ndarray, n_topics: int) -> LatentDirichletAllocation:
    return LatentDirichletAllocation(
        n_components=n_topics, max_iter=10, random_state=42, evaluate_every=-1
    ).fit(doc_term_matrix)

def implement_modeling(data: pd.DataFrame, text_col: str = 'text', n_topics: int = 5) -> Dict[str, Any]:
    """
    Complete implementation of Topic Modeling with validation and evaluation.
    
    Args:
        data: Input DataFrame containing text documents
        text_col: Column name containing raw text
        n_topics: Number of latent topics to discover
        
    Returns:
        Dictionary with model artifacts, topic distributions, and evaluation metrics
    """
    if data is None or data.empty:
        raise ValueError("Input data cannot be None or empty")
        
    texts = _preprocess_texts(data, text_col)
    if len(texts) < n_topics:
        raise ValueError("Dataset must contain more documents than requested topics")
        
    vectorizer = _build_vectorizer()
    doc_term_matrix = vectorizer.fit_transform(texts)
    
    lda = _train_lda(doc_term_matrix, n_topics)
    
    feature_names = vectorizer.get_feature_names_out()
    topics = {
        f'topic_{idx}': [feature_names[i] for i in topic.argsort()[:-10:-1]]
        for idx, topic in enumerate(lda.components_)
    }
    
    doc_topic_dist = lda.transform(doc_term_matrix)
    perplexity = float(np.exp(-lda.score(doc_term_matrix) / doc_term_matrix.shape[0]))
    
    return {
        'status': 'success', 'topics': topics, 'perplexity': perplexity,
        'doc_topic_distribution': doc_topic_dist, 'vectorizer': vectorizer,
        'model': lda, 'metadata': {'documents_processed': len(texts), 'topics_found': n_topics}
    }

if __name__ == "__main__":
    sample_data = fetch_20newsgroups(subset='all', remove=('headers', 'footers', 'quotes'))
    df = pd.DataFrame({'text': sample_data.data, 'category': sample_data.target})
    
    results = implement_modeling(df, text_col='text', n_topics=5)
    print(f"Status: {results['status']}")
    print(f"
