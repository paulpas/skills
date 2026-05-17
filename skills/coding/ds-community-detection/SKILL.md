---
compatibility: opencode
completeness: 95
content-types:
- code
- guidance
- do-dont
- examples
description: '"Detects communities and clusters in graphs using modularity optimization, spectral methods, and graph partitioning
  algorithms"'
license: MIT
maturity: stable
metadata:
  domain: coding
  output-format: code
  related-skills: ds-association-rules, ds-clustering, ds-dimensionality-reduction
  role: implementation
  scope: implementation
  triggers: community detection, graph clustering, modularity, spectral clustering, graph partitioning
  version: 1.0.0
name: community-detection
---
# Community Detection

Comprehensive guide to community detection in machine learning and data science workflows.

## When to Use This Skill

- Solving real-world unsupervised learning problems
- Building machine learning pipelines with community detection
- Implementing best practices for community detection
- Optimizing model performance using community detection techniques
- Learning industry-standard approaches to community detection

## When NOT to Use This Skill

- When using pre-built libraries without understanding underlying concepts
- For toy problems that don't require community detection rigor
- When domain expertise in specific problem requires different approach
- If your problem doesn't require the complexity this skill provides

## Purpose and Key Concepts

Community Detection is a critical component of the machine learning workflow. This skill covers:

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

### Pattern 1: Basic Community Detection

```python
import networkx as nx
import numpy as np
from typing import Dict, Any

def basic_community_detection(graph: nx.Graph) -> Dict[str, Any]:
    """Basic community detection using greedy modularity optimization."""
    communities = nx.community.greedy_modularity_communities(graph)
    community_labels = {node: idx for idx, comm in enumerate(communities) for node in comm}
    modularity = nx.community.modularity(graph, communities)
    return {
        'communities': communities,
        'labels': community_labels,
        'modularity': float(modularity)
    }

# Create a sample graph with known community structure
G = nx.gnm_random_graph(50, 150, seed=42)
for i in range(0, 25):
    for j in range(i+1, 25):
        if np.random.rand() < 0.3:
            G.add_edge(i, j)
    for i in range(25, 50):
        for j in range(i+1, 50):
            if np.random.rand() < 0.3:
                G.add_edge(i, j)

results = basic_community_detection(G)
print(f"Detected {len(results['communities'])} communities with modularity Q={results['modularity']:.4f}")
```

### Pattern 2: Production-Ready Community Detection

```python
import logging
import networkx as nx
import numpy as np
from typing import Any, Dict, Union
from sklearn.cluster import SpectralClustering

logger = logging.getLogger(__name__)

class CommunityDetection:
    """Production implementation of Community Detection using spectral methods"""
    
    def __init__(self, n_communities: int = 4, method: str = "spectral"):
        self.n_communities = n_communities
        self.method = method
        
    def execute(self, graph: Union[nx.Graph, np.ndarray]) -> Dict[str, Any]:
        """Execute Community Detection on graph data"""
        try:
            if isinstance(graph, np.ndarray):
                G = nx.from_numpy_array(graph)
            elif isinstance(graph, nx.Graph):
                G = graph.copy()
            else:
                raise TypeError("Input must be a NetworkX graph or adjacency matrix")
                
            if self.method == "spectral":
                adj_matrix = nx.to_numpy_array(G)
                sc = SpectralClustering(n_clusters=self.n_communities, affinity='precomputed')
                labels = sc.fit_predict(adj_matrix)
                communities = {int(i): list(np.where(labels == i)[0]) for i in range(self.n_communities)}
                modularity = nx.community.modularity(G, communities.values())
            else:
                communities = list(nx.community.greedy_modularity_communities(G))
                labels = np.array([community_labels[node] for node in G.nodes()])
                modularity = nx.community.modularity(G, communities)
                
            return {
                'status': 'success',
                'communities': communities,
                'labels': labels.tolist(),
                'modularity': float(modularity),
                'node_count': G.number_of_nodes(),
                'edge_count': G.number_of_edges()
            }
        except Exception as e:
            logger.error(f"Community detection failed: {e}")
            return {'status': 'error', 'message': str(e)}
```

### Pattern 3: BAD vs GOOD Implementation

```python
# BAD: Hardcoded values, no error handling, violates DRY principle
def bad_detection(G):
    labels = [0] * G.number_of_nodes()
    for i in range(10):
        labels[i] = 1
    return labels

# GOOD: Type hints, validation, modular design, follows SOLID principles
def good_detection(graph: nx.Graph, n_clusters: int = 4) -> list[int]:
    if not isinstance(graph, nx.Graph):
        raise TypeError("Expected NetworkX graph")
    if graph.number_of_nodes() == 0:
        raise ValueError("Graph is empty")
    adj = nx.to_numpy_array(graph)
    sc = SpectralClustering(n_clusters=n_clusters, affinity='precomputed')
    return sc.fit_predict(adj).tolist()
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
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any
from sklearn.cluster import SpectralClustering

def implement_detection(data: nx.Graph) -> Dict[str, Any]:
    """
    Complete implementation of Community Detection.
    
    This example demonstrates:
    - Proper input validation
    - Core algorithm implementation (Spectral Clustering)
    - Error handling
    - Result formatting and visualization
    
    Args:
        data: Input NetworkX graph with nodes and edges
        
    Returns:
        Dictionary with results and metadata
        
    Raises:
        ValueError: If input data is invalid
    """
    if data is None or not isinstance(data, nx.Graph):
        raise ValueError("Input data must be a NetworkX graph")
    if data.number_of_nodes() == 0:
        raise ValueError("Graph cannot be empty")
        
    n_communities = 4
    adj_matrix = nx.to_numpy_array(data)
    
    # Run spectral clustering
    sc = SpectralClustering(n_clusters=n_communities, affinity='precomputed', random_state=42)
    labels = sc.fit_predict(adj_matrix)
    
    # Organize results
    communities = {int(i): list(np.where(labels == i)[0]) for i in range(n_communities)}
    modularity = nx.community.modularity(data, communities.values())
    
    # Visualization
    pos = nx.spring_layout(data, seed=42)
    plt.figure(figsize=(10, 8))
    colors = plt.cm.tab10(labels)
    nx.draw_networkx_nodes(data, pos, node_color=colors, node_size=500, alpha=0.8)
    nx.draw_networkx_edges(data, pos, alpha=0.5)
    nx.draw_networkx_labels(data, pos, font_size=8)
    plt.title(f"Community Detection (Q={modularity:.3f})")
    plt.axis('off')
    plt.tight_layout()
    plt.show()
    
    return {
        'status': 'success',
        'communities': communities,
        'labels': labels.tolist(),
        'modularity': float(modularity),
        'metadata': {'nodes': data.number_of_nodes(), 'edges': data.number_of_edges()}
    }

# Usage and testing
if __name__ == "__main__":
    # Create sample graph with community structure
    sample_graph = nx.karate_club_graph()
    
    # Run implementation
    results = implement_detection(sample_graph)
    print(f"Status: {results['status']}")
    print(f"Detected {len(results['communities'])} communities")
    print(f"Modularity Score: {results['modularity']:.4f}")
```

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `coding-ds-clustering` | Clustering techniques | Complementary to this skill |
| `coding-ds-association-rules` | Association Rules techniques | Complementary to this skill |
| `coding-ds-dimensionality-reduction` | Dimensionality Reduction techniques | Complementary to this skill |

## References

- Official documentation and papers on Community Detection
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
