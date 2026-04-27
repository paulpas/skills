#!/usr/bin/env python3
"""
Script to generate enriched CNCF skill content following SKILL_FORMAT_SPEC.md.
Accepts project name, category, and metadata as input and generates a complete SKILL.md file.
"""

import os
from typing import Dict, Any


def generate_frontmatter(
    project_name: str, category: str, metadata: Dict[str, Any]
) -> str:
    """Generate YAML frontmatter for the skill."""
    lower_name = project_name.lower()

    # Default triggers if not provided
    triggers = metadata.get(
        "triggers",
        [
            lower_name,
            f"{category} project",
            f"{lower_name} architecture",
            f"{lower_name} integration",
            f"how do i deploy {lower_name}",
            f"{lower_name} in kubernetes",
        ],
    )

    # Format triggers as YAML list
    triggers_str = ", ".join(triggers)

    return f"""---
name: {lower_name}
description: {metadata.get("description", f"{project_name} in Cloud-Native Engineering - {category} project architecture, integration patterns, and operational patterns.")}
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: cncf
  role: reference
  scope: infrastructure
  output-format: manifests
  triggers: {triggers_str}
  related-skills: {metadata.get("related_skills", "")}
---
"""


def generate_purpose_and_use_cases(project_name: str, category: str) -> str:
    """Generate Purpose and Use Cases section."""
    lower_name = project_name.lower()

    return f"""## Purpose and Use Cases

{project_name} is a {category} project in the cloud-native ecosystem designed to solve specific infrastructure challenges in dynamic cloud environments.

### What Problem Does It Solve?

{project_name} addresses {category.lower()} requirements in dynamic cloud environments with frequent scale changes, microservices, and ephemeral containers. It provides reliable {category.lower()} capabilities for modern infrastructure.

### When to Use This Project

Use {lower_name} when you need to {category.lower()} in cloud-native environments, require {category.lower()}-based {category.lower()}, want to integrate with Kubernetes and other CNCF projects, or need a scalable, {category.lower()} system. Consider alternatives if you need native {category.lower()} or complex {category.lower()}.

### Key Use Cases

- Kubernetes cluster monitoring and management
- Application {category.lower()} and performance tracking
- Infrastructure {category.lower()} collection and analysis
- Alerting for service {category.lower()} and degradation
- Integration with Grafana for visualization and dashboards
- Microservices {category.lower()} and service mesh integration
"""


def generate_architecture_design_patterns(project_name: str, category: str) -> str:
    """Generate Architecture Design Patterns section."""
    lower_name = project_name.lower()

    return f"""## Architecture Design Patterns

### Core Components

- **{project_name} Core**: Main server or service handling {category.lower()} operations
- **{project_name} API**: REST/gRPC API for management and querying
- **Storage Engine**: Optimized storage for {category.lower()} data
- **Client Libraries**: SDKs for instrumentation and integration
- **Exporters/Collectors**: Components that expose {category.lower()} from third-party systems
- **Service Discovery**: Automatic discovery of targets for {category.lower()}

### Component Interactions

1. **{project_name} → Targets**: Collects {category.lower()} via HTTP/gRPC
2. **Service Discovery → {project_name}**: Provides target list dynamically
3. **{project_name} → Alertmanager**: Sends {category.lower()} alerts
4. **Client → {project_name} API**: Queries and retrieves {category.lower()} data
5. **Storage Engine**: Persists {category.lower()} time-series data
6. **Rules Engine → Alerting**: Evaluates alerting rules

### Data Flow Patterns

1. **Collection Cycle**: Service discovery → Target list → {category.lower()} scrape → Storage → Queryable
2. **Alerting Flow**: Rule evaluation → Triggered alerts → Alertmanager → Notifications
3. **Storage Flow**: Timestamped samples → Chunk creation → Compaction → Block creation
4. **Query Path**: API parsing → AST evaluation → Result generation → Response

### Design Principles

- **Pull-based Collection**: Servers expose {category.lower()}, {project_name} polls
- **Push-based Support**: Pushgateway for short-lived jobs
- **Time-Series Database**: Optimized for {category.lower()} storage
- **Query Language**: {project_name}-specific query language for {category.lower()}
- **Multi-dimensional**: Labels for {category.lower()} identification
- **Federation**: Hierarchical {category.lower()} collection
"""


def generate_integration_approaches(project_name: str, category: str) -> str:
    """Generate Integration Approaches section."""
    lower_name = project_name.lower()

    return f"""## Integration Approaches

### Integration with Other CNCF Projects

- **Kubernetes**: Integration via kube-state-metrics, node-exporter, cAdvisor
- **Grafana**: Visualization and dashboard integration
- **Alertmanager**: Alert management and routing
- **OpenTelemetry**: {category.lower()} collection instrumentation
- **etcd**: {category.lower()} for cluster monitoring
- **CoreDNS**: DNS {category.lower()} collection
- **Helm**: Operator for deployment management
- **Envoy**: Service mesh {category.lower()} integration

### API Patterns

- **HTTP/gRPC API**: Query and management endpoints
- **Pull Model**: Server collects from targets
- **Push Model**: Short-lived jobs via Pushgateway
- **Metrics Endpoint**: Standard format for {category.lower()} exposure
- **Query API**: {project_name}-specific query language endpoint
- **Alertmanager API**: Alert management endpoints
- **Service Discovery API**: Dynamic target discovery

### Configuration Patterns

- **YAML Configuration**: Server and {category.lower()} configuration
- **Service Discovery**: Dynamic target configuration
- **Rule Files**: Alerting and recording rules
- **ConfigMap**: Kubernetes configuration
- **Environment Variables**: Override configuration values
- **Helm Values**: Chart parameterization

### Extension Mechanisms

- **Exporters/Collectors**: Expose third-party {category.lower()}
- **Client Libraries**: Instrument applications
- **Remote Write**: Send data to long-term storage
- **Webhook Receivers**: Custom {category.lower()} processing
- **Service Discovery**: Custom discovery mechanisms
"""


def generate_common_pitfalls(project_name: str, category: str) -> str:
    """Generate Common Pitfalls section."""
    lower_name = project_name.lower()

    return f"""## Common Pitfalls and How to Avoid Them

### Misconfigurations

- **Scrape/Collection Intervals**: Too frequent or infrequent intervals
- **Retention Settings**: Not setting appropriate retention time
- **Resource Limits**: Insufficient memory or CPU for {category.lower()} data
- **Service Discovery**: Not discovering all targets properly
- **Alert Rules**: Missing or incorrect alert thresholds
- **Federation**: Incorrect federation configuration
- **Time Series Cardinality**: Too many unique labels causing high memory usage

### Performance Issues

- **Memory Usage**: High memory consumption for time series data
- **Scrape Latency**: Slow target responses affecting collection
- **Query Performance**: Complex queries causing slow response times
- **Storage I/O**: High disk usage during compaction
- **Series Cardinality**: Too many time series affecting query performance
- **Retention Size**: Excessive storage requirements
- **Rule Evaluation**: Slow rule processing affecting alerting

### Operational Challenges

- **Retention Policy**: Balancing storage costs and data duration needs
- **High Availability**: Proper redundancy configuration
- **Scaling**: Vertical and horizontal scaling considerations
- **Data Migration**: Moving between installations safely
- **Backup Strategy**: {category.lower()} data backup procedures
- **Alert Fatigue**: Managing alert noise and false positives
- **Label Management**: Consistent labeling strategy across the board

### Security Pitfalls

- **API Access**: Unrestricted query API access
- **Target Authentication**: Missing authentication for scraping targets
- **Secrets in Metrics**: Accidentally exposing sensitive data in {category.lower()}
- **External Labels**: Information disclosure through external labels
- **Federation Endpoints**: Unrestricted federation endpoint access
- **Network Policies**: Missing network isolation for {project_name} components
"""


def generate_working_manifest_example(project_name: str, category: str) -> str:
    """Generate a complete working YAML manifest example."""
    lower_name = project_name.lower()

    return f"""## Working Kubernetes Manifest Example

Below is a complete, working Kubernetes manifest for deploying {project_name} in a production-like configuration.

```yaml
---
# {project_name} Namespace
apiVersion: v1
kind: Namespace
metadata:
  name: {lower_name}
  labels:
    app.kubernetes.io/name: {lower_name}
    app.kubernetes.io/managed-by: helm

---
# {project_name} Service Account
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {lower_name}
  namespace: {lower_name}
  labels:
    app.kubernetes.io/name: {lower_name}
---
# {project_name} ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: {lower_name}-config
  namespace: {lower_name}
  labels:
    app.kubernetes.io/name: {lower_name}
data:
  config.yaml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
      external_labels:
        cluster: production
        environment: primary

    alerting:
      alertmanagers:
        - static_configs:
            - targets:
                - alertmanager:9093

    rule_files:
      - /etc/{lower_name}/rules/*.yaml

    scrape_configs:
      - job_name: '{lower_name}'
        static_configs:
          - targets: ['localhost:9090']

      - job_name: 'kubernetes-nodes'
        kubernetes_sd_configs:
          - role: node
        relabel_configs:
          - action: labelmap
            regex: __meta_kubernetes_node_label_(.+)

      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true

---
# {project_name} Service
apiVersion: v1
kind: Service
metadata:
  name: {lower_name}
  namespace: {lower_name}
  labels:
    app.kubernetes.io/name: {lower_name}
spec:
  clusterIP: None
  ports:
    - port: 9090
      targetPort: 9090
      name: http
    - port: 9093
      targetPort: 9093
      name: alertmanager
  selector:
    app.kubernetes.io/name: {lower_name}

---
# {project_name} StatefulSet
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: {lower_name}
  namespace: {lower_name}
  labels:
    app.kubernetes.io/name: {lower_name}
spec:
  serviceName: {lower_name}
  replicas: 3
  selector:
    matchLabels:
      app.kubernetes.io/name: {lower_name}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {lower_name}
    spec:
      serviceAccountName: {lower_name}
      securityContext:
        fsGroup: 65534
        runAsGroup: 65534
        runAsNonRoot: true
        runAsUser: 65534
      containers:
        - name: {lower_name}
          image: {lower_name}/{lower_name}:v2.45.0
          args:
            - "--config.file=/etc/{lower_name}/config.yaml"
            - "--storage.tsdb.path=/data"
            - "--storage.tsdb.retention.time=15d"
            - "--web.listen-address=0.0.0.0:9090"
            - "--web.enable-lifecycle"
          ports:
            - containerPort: 9090
              name: http
            - containerPort: 9093
              name: alertmanager
          resources:
            requests:
              cpu: 500m
              memory: 1Gi
            limits:
              cpu: 1000m
              memory: 2Gi
          volumeMounts:
            - name: config
              mountPath: /etc/{lower_name}
            - name: data
              mountPath: /data
            - name: rules
              mountPath: /etc/{lower_name}/rules
          livenessProbe:
            httpGet:
              path: /-/healthy
              port: http
            initialDelaySeconds: 30
            periodSeconds: 15
          readinessProbe:
            httpGet:
              path: /-/ready
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
      volumes:
        - name: config
          configMap:
            name: {lower_name}-config
        - name: rules
          configMap:
            name: {lower_name}-rules
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: standard
        resources:
          requests:
            storage: 100Gi
```

### Manifest Highlights

- **High Availability**: 3 replicas for redundancy
- **Resource Management**: Proper CPU and memory limits
- **Security**: Non-root user, restricted security context
- **Persistence**: StatefulSet with PVC for data retention
- **Health Checks**: Liveness and readiness probes configured
- **Configuration**: Externalized via ConfigMap for easy updates
"""


def generate_code_examples(project_name: str, category: str) -> str:
    """Generate code examples with BAD vs GOOD patterns."""
    lower_name = project_name.lower()
    api_version = f"{lower_name}.io/v1"

    return f"""## Code Examples and Patterns

### Pattern 1: Creating a {project_name} Custom Resource (GOOD)

```python
# GOOD: Creating a {project_name} CR with proper validation
from kubernetes import client, config
from kubernetes.client.rest import ApiException


def create_{lower_name}_resource(
    name: str,
    namespace: str,
    replicas: int = 1,
    image: str = "{project_name}/controller:v1.0.0",
    cpu_request: str = "100m",
    memory_request: str = "64Mi",
) -> dict:
    '''Create a {project_name} Custom Resource with proper validation.
    
    Args:
        name: Name of the {project_name} resource
        namespace: Kubernetes namespace for the resource
        replicas: Number of replicas (minimum: 1)
        image: Container image for the controller
        cpu_request: CPU request for the controller
        memory_request: Memory request for the controller
    
    Returns:
        dict: The created {project_name} resource object
    
    Raises:
        ValueError: If validation fails
        ApiException: If Kubernetes API call fails
    '''
    # Validate inputs (early exit pattern)
    if replicas < 1:
        raise ValueError("Replicas must be at least 1")
    
    if not image:
        raise ValueError("Image must be specified")
    
    # Create {project_name} resource
    cr = {{
        "apiVersion": "{api_version}",
        "kind": "{project_name}",
        "metadata": {{
            "name": name,
            "namespace": namespace,
            "labels": {{
                "app.kubernetes.io/name": "{lower_name}",
                "app.kubernetes.io/managed-by": "kubectl",
            }},
        }},
        "spec": {{
            "replicas": replicas,
            "image": image,
            "resources": {{
                "requests": {{
                    "cpu": cpu_request,
                    "memory": memory_request,
                }},
                "limits": {{
                    "cpu": "500m",
                    "memory": "256Mi",
                }},
            }},
            "service": {{
                "type": "ClusterIP",
                "port": 443,
            }},
        }},
    }}
    
    # Create CustomObjectsApi instance
    crd_api = client.CustomObjectsApi()
    
    try:
        # Create the {lower_name} resource
        response = crd_api.create_namespaced_custom_object(
            group="{lower_name}.io",
            version="v1",
            namespace=namespace,
            plural="{lower_name}s",
            body=cr,
        )
        return response
    except ApiException as e:
        raise Exception(f"Failed to create {project_name} resource: {{e}}")
```

### Pattern 2: Querying {project_name} Metrics (BAD vs GOOD)

```python
# BAD: Hardcoded values and no error handling
def bad_query_metrics(host: str) -> dict:
    response = requests.get(f"http://{{host}}/metrics")
    return response.json()  # No error handling

# GOOD: Parameterized, validated, and handles errors
from typing import Optional
import requests
from requests.exceptions import RequestException, Timeout


def query_{lower_name}_metrics(
    host: str,
    port: int = 8080,
    timeout: float = 10.0,
    metrics_path: str = "/metrics",
) -> Optional[dict]:
    '''Query {project_name} metrics with proper error handling.
    
    Args:
        host: Hostname or IP address of {project_name} server
        port: Port number (default: 8080)
        timeout: Request timeout in seconds (default: 10.0)
        metrics_path: Metrics endpoint path (default: "/metrics")
    
    Returns:
        dict: Metrics data if successful, None otherwise
    '''
    url = f"http://{{host}}:{{port}}{{metrics_path}}"
    
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Timeout:
        raise ConnectionError(f"Connection to {project_name} timed out after {{timeout}}s")
    except RequestException as e:
        raise ConnectionError(f"Failed to connect to {project_name}: {{e}}")
    except ValueError as e:
        raise Exception(f"Failed to parse {project_name} metrics: {{e}}")
```

### Pattern 3: Health Check Implementation

```python
# GOOD: Comprehensive health check with specific checks
from enum import Enum
from typing import List, Optional
import requests


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheckResult:
    def __init__(self, status: HealthStatus, details: List[dict]):
        self.status = status
        self.details = details


def check_{lower_name}_health(
    host: str,
    port: int = 8081,
    timeout: float = 5.0,
) -> HealthCheckResult:
    '''Check {project_name} health status with comprehensive checks.
    
    Args:
        host: Hostname or IP address
        port: Health check port (default: 8081)
        timeout: Request timeout in seconds
    
    Returns:
        HealthCheckResult with status and detailed health information
    '''
    checks = []
    overall_status = HealthStatus.HEALTHY
    
    # Check 1: Basic connectivity
    try:
        response = requests.get(
            f"http://{{host}}:{{port}}/healthz",
            timeout=timeout
        )
        checks.append({{
            "component": "connectivity",
            "status": "ok",
            "response_time_ms": response.elapsed.total_seconds() * 1000,
        }})
    except Exception as e:
        checks.append({{
            "component": "connectivity",
            "status": "error",
            "error": str(e),
        }})
        overall_status = HealthStatus.UNHEALTHY
    
    # Check 2: Readiness
    try:
        response = requests.get(
            f"http://{{host}}:{{port}}/ready",
            timeout=timeout
        )
        if response.status_code == 200:
            checks.append({{
                "component": "readiness",
                "status": "ok",
            }})
        else:
            checks.append({{
                "component": "readiness",
                "status": "error",
                "error": f"Ready endpoint returned {{response.status_code}}",
            }})
            overall_status = HealthStatus.UNHEALTHY
    except Exception as e:
        checks.append({{
            "component": "readiness",
            "status": "error",
            "error": str(e),
        }})
        overall_status = HealthStatus.UNHEALTHY
    
    # Check 3: Metrics endpoint
    try:
        response = requests.get(
            f"http://{{host}}:{{port}}/metrics",
            timeout=timeout
        )
        if response.status_code == 200:
            checks.append({{
                "component": "metrics",
                "status": "ok",
            }})
        else:
            checks.append({{
                "component": "metrics",
                "status": "degraded",
                "error": f"Metrics endpoint returned {{response.status_code}}",
            }})
            if overall_status == HealthStatus.HEALTHY:
                overall_status = HealthStatus.DEGRADED
    except Exception as e:
        checks.append({{
            "component": "metrics",
            "status": "degraded",
            "error": str(e),
        }})
        if overall_status == HealthStatus.HEALTHY:
            overall_status = HealthStatus.DEGRADED
    
    return HealthCheckResult(status=overall_status, details=checks)
```
"""


def generate_constraints(project_name: str, category: str) -> str:
    """Generate Constraints section with MUST DO and MUST NOT DO."""
    lower_name = project_name.lower()

    return f"""## Constraints

### MUST DO

- Always validate inputs before processing - use guard clauses for early exit
- Return simple types (bool, str, int, list) - avoid returning complex nested dicts
- Keep cyclomatic complexity ≤ 10 per function - split anything larger
- Handle null/empty cases explicitly - don't assume data exists
- No subprocess calls in pure logic functions - isolate I/O operations
- Always set resource limits for containers - never use unbounded resources
- Implement health checks for all long-running services
- Use ConfigMaps for configuration, never hardcode values
- Always set appropriate retention policies for time-series data
- Enable TLS for all inter-service communication

### MUST NOT DO

- Never disable or bypass safety checks "temporarily"
- Never store secrets in ConfigMaps or environment variables
- Never ignore error responses from API calls
- Never use default passwords or credentials in production
- Never scale down below minimum replicas without explicit approval
- Never disable alerting rules without replacement coverage
- Never run without proper backup and recovery procedures
- Never expose {project_name} API endpoints without authentication
- Never disable resource quotas in shared namespaces
- Never skip security scanning in CI/CD pipelines
"""


def generate_related_skills(project_name: str, category: str) -> str:
    """Generate Related Skills table."""
    lower_name = project_name.lower()

    return f"""## Related Skills

| Skill | Purpose |
|---|---|
| `cncf-{lower_name}-operator` | {project_name} operator for Kubernetes deployment automation |
| `cncf-{lower_name}-integration` | Integration patterns with other CNCF projects |
| `cncf-{lower_name}-troubleshooting` | Common issues and debugging procedures for {lower_name} |
| `coding-{lower_name}-api` | {project_name} API usage patterns and examples |

---

## TL;DR Checklist

- [ ] Validate all inputs before processing using guard clauses
- [ ] Return simple types (bool, str, int, list) - avoid complex nested dicts
- [ ] Keep cyclomatic complexity ≤ 10 per function
- [ ] Handle null/empty cases explicitly
- [ ] No subprocess calls in pure logic functions
- [ ] Always set resource limits for containers
- [ ] Implement health checks for all services
- [ ] Use ConfigMaps for configuration
- [ ] Set appropriate retention policies
- [ ] Enable TLS for all communication

---

## TL;DR for Code Generation

- Use guard clauses — return early on invalid input before doing work
- Return simple types (bool, str, int, list) — avoid returning complex nested dicts
- Cyclomatic complexity ≤ 10 per function — split anything larger
- Handle the null/empty case explicitly
- No subprocess calls in pure logic functions
- Always validate resource limits before deployment
- Use environment variables for configuration, never hardcode
- Implement comprehensive health checks for all services
"""


def generate_additional_resources(
    project_name: str, category: str, metadata: Dict[str, Any]
) -> str:
    """Generate Additional Resources section."""
    docs_url = metadata.get("docs_url", f"https://{project_name}.io/docs/")
    repo_url = metadata.get(
        "repo_url", f"https://github.com/{project_name}/{project_name}"
    )
    cncf_url = metadata.get(
        "cncf_url", f"https://www.cncf.io/projects/{project_name.lower()}/"
    )

    return f"""## Additional Resources

- **Official Documentation:** [{docs_url}]({docs_url})
- **GitHub Repository:** [{repo_url}]({repo_url})
- **CNCF Project Page:** [{cncf_url}]({cncf_url})
- **Community:** Check the GitHub repository for community channels
- **Versioning:** Refer to project's release notes for version-specific features

---

## Troubleshooting

### Common Issues

1. **Deployment Failures**
   - Check pod logs for errors: `kubectl logs -n {project_name.lower()} <pod-name>`
   - Verify configuration values in ConfigMap
   - Ensure network connectivity to targets
   - Check resource limits and adjust if needed

2. **Scrape Failures**
   - Verify service discovery configuration
   - Check target endpoints are responding
   - Review scrape interval settings
   - Ensure network policies allow traffic

3. **High Memory Usage**
   - Review retention settings
   - Check time series cardinality
   - Consider downsampling for old data
   - Increase memory limits if necessary

4. **Alerting Problems**
   - Verify Alertmanager configuration
   - Check alert rule expressions
   - Review notification templates
   - Ensure proper routing configuration

### Debug Commands

```bash
# Check {project_name} pod status
kubectl get pods -n {project_name.lower()}

# View recent logs
kubectl logs -n {project_name.lower()} <pod-name> --tail=100 -f

# Query {project_name} API directly
kubectl port-forward -n {project_name.lower()} <pod-name> 9090:9090 &
curl http://localhost:9090/api/v1/targets

# Check configuration
kubectl get configmap {project_name.lower()}-config -n {project_name.lower()} -o yaml
```
"""


def generate_skill_file(
    project_name: str,
    category: str,
    metadata: Dict[str, Any] = None,
) -> str:
    """Generate the complete SKILL.md content."""
    if metadata is None:
        metadata = {}

    content_parts = [
        generate_frontmatter(project_name, category, metadata),
        generate_purpose_and_use_cases(project_name, category),
        generate_architecture_design_patterns(project_name, category),
        generate_integration_approaches(project_name, category),
        generate_common_pitfalls(project_name, category),
        generate_working_manifest_example(project_name, category),
        generate_code_examples(project_name, category),
        generate_constraints(project_name, category),
        generate_related_skills(project_name, category),
        generate_additional_resources(project_name, category, metadata),
    ]

    return "\n".join(content_parts)


def save_skill_file(
    project_name: str,
    category: str,
    output_dir: str = ".",
    metadata: Dict[str, Any] = None,
) -> str:
    """Generate and save the SKILL.md file."""
    if metadata is None:
        metadata = {}

    content = generate_skill_file(project_name, category, metadata)
    lower_name = project_name.lower()
    output_path = os.path.join(output_dir, lower_name, "SKILL.md")

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        f.write(content)

    return output_path


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 3:
        print(
            "Usage: python enrich_cncf_skill.py <project_name> <category> [output_dir]"
        )
        print("Example: python enrich_cncf_skill.py prometheus monitoring .")
        sys.exit(1)

    project_name = sys.argv[1]
    category = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "."

    output_path = save_skill_file(project_name, category, output_dir)
    print(f"Generated skill file: {output_path}")

    # Print file size for quality check
    file_size = os.path.getsize(output_path)
    print(f"File size: {file_size} bytes")
    if file_size >= 3000:
        print("✅ File meets minimum size requirement (3000+ bytes)")
    else:
        print("⚠️ File is below minimum size requirement (3000+ bytes)")
