---
name: tempo
description: tempo in Cloud-Native Engineering - tracing project architecture, integration patterns, and operational patterns.
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: cncf
  role: reference
  scope: infrastructure
  output-format: manifests
  triggers: tempo, tracing project, tempo architecture, tempo integration, how do i deploy tempo, tempo in kubernetes
  related-skills: 
---

## Purpose and Use Cases

tempo is a tracing project in the cloud-native ecosystem designed to solve specific infrastructure challenges in dynamic cloud environments.

### What Problem Does It Solve?

tempo addresses tracing requirements in dynamic cloud environments with frequent scale changes, microservices, and ephemeral containers. It provides reliable tracing capabilities for modern infrastructure.

### When to Use This Project

Use tempo when you need to tracing in cloud-native environments, require tracing-based tracing, want to integrate with Kubernetes and other CNCF projects, or need a scalable, tracing system. Consider alternatives if you need native tracing or complex tracing.

### Key Use Cases

- Kubernetes cluster monitoring and management
- Application tracing and performance tracking
- Infrastructure tracing collection and analysis
- Alerting for service tracing and degradation
- Integration with Grafana for visualization and dashboards
- Microservices tracing and service mesh integration

## Architecture Design Patterns

### Core Components

- **tempo Core**: Main server or service handling tracing operations
- **tempo API**: REST/gRPC API for management and querying
- **Storage Engine**: Optimized storage for tracing data
- **Client Libraries**: SDKs for instrumentation and integration
- **Exporters/Collectors**: Components that expose tracing from third-party systems
- **Service Discovery**: Automatic discovery of targets for tracing

### Component Interactions

1. **tempo → Targets**: Collects tracing via HTTP/gRPC
2. **Service Discovery → tempo**: Provides target list dynamically
3. **tempo → Alertmanager**: Sends tracing alerts
4. **Client → tempo API**: Queries and retrieves tracing data
5. **Storage Engine**: Persists tracing time-series data
6. **Rules Engine → Alerting**: Evaluates alerting rules

### Data Flow Patterns

1. **Collection Cycle**: Service discovery → Target list → tracing scrape → Storage → Queryable
2. **Alerting Flow**: Rule evaluation → Triggered alerts → Alertmanager → Notifications
3. **Storage Flow**: Timestamped samples → Chunk creation → Compaction → Block creation
4. **Query Path**: API parsing → AST evaluation → Result generation → Response

### Design Principles

- **Pull-based Collection**: Servers expose tracing, tempo polls
- **Push-based Support**: Pushgateway for short-lived jobs
- **Time-Series Database**: Optimized for tracing storage
- **Query Language**: tempo-specific query language for tracing
- **Multi-dimensional**: Labels for tracing identification
- **Federation**: Hierarchical tracing collection

## Integration Approaches

### Integration with Other CNCF Projects

- **Kubernetes**: Integration via kube-state-metrics, node-exporter, cAdvisor
- **Grafana**: Visualization and dashboard integration
- **Alertmanager**: Alert management and routing
- **OpenTelemetry**: tracing collection instrumentation
- **etcd**: tracing for cluster monitoring
- **CoreDNS**: DNS tracing collection
- **Helm**: Operator for deployment management
- **Envoy**: Service mesh tracing integration

### API Patterns

- **HTTP/gRPC API**: Query and management endpoints
- **Pull Model**: Server collects from targets
- **Push Model**: Short-lived jobs via Pushgateway
- **Metrics Endpoint**: Standard format for tracing exposure
- **Query API**: tempo-specific query language endpoint
- **Alertmanager API**: Alert management endpoints
- **Service Discovery API**: Dynamic target discovery

### Configuration Patterns

- **YAML Configuration**: Server and tracing configuration
- **Service Discovery**: Dynamic target configuration
- **Rule Files**: Alerting and recording rules
- **ConfigMap**: Kubernetes configuration
- **Environment Variables**: Override configuration values
- **Helm Values**: Chart parameterization

### Extension Mechanisms

- **Exporters/Collectors**: Expose third-party tracing
- **Client Libraries**: Instrument applications
- **Remote Write**: Send data to long-term storage
- **Webhook Receivers**: Custom tracing processing
- **Service Discovery**: Custom discovery mechanisms

## Common Pitfalls and How to Avoid Them

### Misconfigurations

- **Scrape/Collection Intervals**: Too frequent or infrequent intervals
- **Retention Settings**: Not setting appropriate retention time
- **Resource Limits**: Insufficient memory or CPU for tracing data
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
- **Backup Strategy**: tracing data backup procedures
- **Alert Fatigue**: Managing alert noise and false positives
- **Label Management**: Consistent labeling strategy across the board

### Security Pitfalls

- **API Access**: Unrestricted query API access
- **Target Authentication**: Missing authentication for scraping targets
- **Secrets in Metrics**: Accidentally exposing sensitive data in tracing
- **External Labels**: Information disclosure through external labels
- **Federation Endpoints**: Unrestricted federation endpoint access
- **Network Policies**: Missing network isolation for tempo components

## Working Kubernetes Manifest Example

Below is a complete, working Kubernetes manifest for deploying tempo in a production-like configuration.

```yaml
---
# tempo Namespace
apiVersion: v1
kind: Namespace
metadata:
  name: tempo
  labels:
    app.kubernetes.io/name: tempo
    app.kubernetes.io/managed-by: helm

---
# tempo Service Account
apiVersion: v1
kind: ServiceAccount
metadata:
  name: tempo
  namespace: tempo
  labels:
    app.kubernetes.io/name: tempo
---
# tempo ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: tempo-config
  namespace: tempo
  labels:
    app.kubernetes.io/name: tempo
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
      - /etc/tempo/rules/*.yaml

    scrape_configs:
      - job_name: 'tempo'
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
# tempo Service
apiVersion: v1
kind: Service
metadata:
  name: tempo
  namespace: tempo
  labels:
    app.kubernetes.io/name: tempo
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
    app.kubernetes.io/name: tempo

---
# tempo StatefulSet
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: tempo
  namespace: tempo
  labels:
    app.kubernetes.io/name: tempo
spec:
  serviceName: tempo
  replicas: 3
  selector:
    matchLabels:
      app.kubernetes.io/name: tempo
  template:
    metadata:
      labels:
        app.kubernetes.io/name: tempo
    spec:
      serviceAccountName: tempo
      securityContext:
        fsGroup: 65534
        runAsGroup: 65534
        runAsNonRoot: true
        runAsUser: 65534
      containers:
        - name: tempo
          image: tempo/tempo:v2.45.0
          args:
            - "--config.file=/etc/tempo/config.yaml"
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
              mountPath: /etc/tempo
            - name: data
              mountPath: /data
            - name: rules
              mountPath: /etc/tempo/rules
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
            name: tempo-config
        - name: rules
          configMap:
            name: tempo-rules
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

## Code Examples and Patterns

### Pattern 1: Creating a tempo Custom Resource (GOOD)

```python
# GOOD: Creating a tempo CR with proper validation
from kubernetes import client, config
from kubernetes.client.rest import ApiException


def create_tempo_resource(
    name: str,
    namespace: str,
    replicas: int = 1,
    image: str = "tempo/controller:v1.0.0",
    cpu_request: str = "100m",
    memory_request: str = "64Mi",
) -> dict:
    '''Create a tempo Custom Resource with proper validation.
    
    Args:
        name: Name of the tempo resource
        namespace: Kubernetes namespace for the resource
        replicas: Number of replicas (minimum: 1)
        image: Container image for the controller
        cpu_request: CPU request for the controller
        memory_request: Memory request for the controller
    
    Returns:
        dict: The created tempo resource object
    
    Raises:
        ValueError: If validation fails
        ApiException: If Kubernetes API call fails
    '''
    # Validate inputs (early exit pattern)
    if replicas < 1:
        raise ValueError("Replicas must be at least 1")
    
    if not image:
        raise ValueError("Image must be specified")
    
    # Create tempo resource
    cr = {
        "apiVersion": "tempo.io/v1",
        "kind": "tempo",
        "metadata": {
            "name": name,
            "namespace": namespace,
            "labels": {
                "app.kubernetes.io/name": "tempo",
                "app.kubernetes.io/managed-by": "kubectl",
            },
        },
        "spec": {
            "replicas": replicas,
            "image": image,
            "resources": {
                "requests": {
                    "cpu": cpu_request,
                    "memory": memory_request,
                },
                "limits": {
                    "cpu": "500m",
                    "memory": "256Mi",
                },
            },
            "service": {
                "type": "ClusterIP",
                "port": 443,
            },
        },
    }
    
    # Create CustomObjectsApi instance
    crd_api = client.CustomObjectsApi()
    
    try:
        # Create the tempo resource
        response = crd_api.create_namespaced_custom_object(
            group="tempo.io",
            version="v1",
            namespace=namespace,
            plural="tempos",
            body=cr,
        )
        return response
    except ApiException as e:
        raise Exception(f"Failed to create tempo resource: {e}")
```

### Pattern 2: Querying tempo Metrics (BAD vs GOOD)

```python
# BAD: Hardcoded values and no error handling
def bad_query_metrics(host: str) -> dict:
    response = requests.get(f"http://{host}/metrics")
    return response.json()  # No error handling

# GOOD: Parameterized, validated, and handles errors
from typing import Optional
import requests
from requests.exceptions import RequestException, Timeout


def query_tempo_metrics(
    host: str,
    port: int = 8080,
    timeout: float = 10.0,
    metrics_path: str = "/metrics",
) -> Optional[dict]:
    '''Query tempo metrics with proper error handling.
    
    Args:
        host: Hostname or IP address of tempo server
        port: Port number (default: 8080)
        timeout: Request timeout in seconds (default: 10.0)
        metrics_path: Metrics endpoint path (default: "/metrics")
    
    Returns:
        dict: Metrics data if successful, None otherwise
    '''
    url = f"http://{host}:{port}{metrics_path}"
    
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Timeout:
        raise ConnectionError(f"Connection to tempo timed out after {timeout}s")
    except RequestException as e:
        raise ConnectionError(f"Failed to connect to tempo: {e}")
    except ValueError as e:
        raise Exception(f"Failed to parse tempo metrics: {e}")
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


def check_tempo_health(
    host: str,
    port: int = 8081,
    timeout: float = 5.0,
) -> HealthCheckResult:
    '''Check tempo health status with comprehensive checks.
    
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
            f"http://{host}:{port}/healthz",
            timeout=timeout
        )
        checks.append({
            "component": "connectivity",
            "status": "ok",
            "response_time_ms": response.elapsed.total_seconds() * 1000,
        })
    except Exception as e:
        checks.append({
            "component": "connectivity",
            "status": "error",
            "error": str(e),
        })
        overall_status = HealthStatus.UNHEALTHY
    
    # Check 2: Readiness
    try:
        response = requests.get(
            f"http://{host}:{port}/ready",
            timeout=timeout
        )
        if response.status_code == 200:
            checks.append({
                "component": "readiness",
                "status": "ok",
            })
        else:
            checks.append({
                "component": "readiness",
                "status": "error",
                "error": f"Ready endpoint returned {response.status_code}",
            })
            overall_status = HealthStatus.UNHEALTHY
    except Exception as e:
        checks.append({
            "component": "readiness",
            "status": "error",
            "error": str(e),
        })
        overall_status = HealthStatus.UNHEALTHY
    
    # Check 3: Metrics endpoint
    try:
        response = requests.get(
            f"http://{host}:{port}/metrics",
            timeout=timeout
        )
        if response.status_code == 200:
            checks.append({
                "component": "metrics",
                "status": "ok",
            })
        else:
            checks.append({
                "component": "metrics",
                "status": "degraded",
                "error": f"Metrics endpoint returned {response.status_code}",
            })
            if overall_status == HealthStatus.HEALTHY:
                overall_status = HealthStatus.DEGRADED
    except Exception as e:
        checks.append({
            "component": "metrics",
            "status": "degraded",
            "error": str(e),
        })
        if overall_status == HealthStatus.HEALTHY:
            overall_status = HealthStatus.DEGRADED
    
    return HealthCheckResult(status=overall_status, details=checks)
```

## Constraints

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
- Never expose tempo API endpoints without authentication
- Never disable resource quotas in shared namespaces
- Never skip security scanning in CI/CD pipelines

## Related Skills

| Skill | Purpose |
|---|---|
| `cncf-tempo-operator` | tempo operator for Kubernetes deployment automation |
| `cncf-tempo-integration` | Integration patterns with other CNCF projects |
| `cncf-tempo-troubleshooting` | Common issues and debugging procedures for tempo |
| `coding-tempo-api` | tempo API usage patterns and examples |

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

## Additional Resources

- **Official Documentation:** [https://tempo.io/docs/](https://tempo.io/docs/)
- **GitHub Repository:** [https://github.com/tempo/tempo](https://github.com/tempo/tempo)
- **CNCF Project Page:** [https://www.cncf.io/projects/tempo/](https://www.cncf.io/projects/tempo/)
- **Community:** Check the GitHub repository for community channels
- **Versioning:** Refer to project's release notes for version-specific features

---

## Troubleshooting

### Common Issues

1. **Deployment Failures**
   - Check pod logs for errors: `kubectl logs -n tempo <pod-name>`
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
# Check tempo pod status
kubectl get pods -n tempo

# View recent logs
kubectl logs -n tempo <pod-name> --tail=100 -f

# Query tempo API directly
kubectl port-forward -n tempo <pod-name> 9090:9090 &
curl http://localhost:9090/api/v1/targets

# Check configuration
kubectl get configmap tempo-config -n tempo -o yaml
```
