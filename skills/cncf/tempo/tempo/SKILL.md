---
completeness: 95
content-types:
- guidance
- examples
- do-dont
- config
maturity: stable
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

```bash
# ✅ GOOD — Create tempo resource using kubectl
# Create namespace
kubectl create namespace tempo --dry-run=client -o yaml | kubectl apply -f -

# Create ConfigMap for tempo configuration
cat << 'EOF' | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: tempo-config
  namespace: tempo
data:
  replicas: "1"
  cpu_request: "100m"
  memory_request: "64Mi"
EOF

# Create tempo deployment using kubectl
kubectl apply -f - << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tempo-controller
  namespace: tempo
  labels:
    app.kubernetes.io/name: tempo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: tempo-controller
  template:
    metadata:
      labels:
        app: tempo-controller
    spec:
      containers:
      - name: tempo
        image: tempo/controller:v1.0.0
        resources:
          requests:
            cpu: "100m"
            memory: "64Mi"
          limits:
            cpu: "500m"
            memory: "256Mi"
EOF

# Verify deployment
kubectl get pods -n tempo -l app=tempo-controller
kubectl describe deployment tempo-controller -n tempo
```

### Pattern 2: Querying tempo Metrics (BAD vs GOOD)

```bash
# ✅ GOOD — Query tempo metrics using curl
# Query tempo metrics with error handling
METRICS_URL="http://localhost:8080/metrics"
TIMEOUT=10

# Test connectivity and fetch metrics
HTTP_CODE=$(curl -s -o /tmp/tempo-metrics.txt -w "%{http_code}" --max-time $TIMEOUT "$METRICS_URL")
if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 400 ]]; then
    echo "✅ tempo metrics retrieved (HTTP $HTTP_CODE)"
    head -20 /tmp/tempo-metrics.txt
else
    echo "❌ Failed to get tempo metrics (HTTP $HTTP_CODE)"
    exit 1
fi

# Query specific metrics with curl and grep
curl -s --max-time $TIMEOUT "$METRICS_URL" | grep "tempo_active" | head -10

# Query tempo API via port-forward
kubectl port-forward -n tempo svc/tempo 8080:8080 &
curl -s http://localhost:8080/api/v1/services | jq .
```

### Pattern 3: Health Check Implementation

```bash
# ✅ GOOD — Comprehensive tempo health check using curl
#!/bin/bash
# check_tempo_health.sh — Health checks for tempo service

HOST="${1:-localhost}"
PORT="${2:-8081}"
TIMEOUT=5

echo "=== tempo Health Check ==="

# Check 1: Basic connectivity
echo -n "Connectivity: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "http://$HOST:$PORT/healthz" 2>/dev/null || echo "000")
if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 400 ]]; then
    echo "✅ OK (HTTP $HTTP_CODE)"
    STATUS="HEALTHY"
else
    echo "❌ FAILED (HTTP $HTTP_CODE)"
    STATUS="UNHEALTHY"
fi

# Check 2: Readiness
echo -n "Readiness: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "http://$HOST:$PORT/ready" 2>/dev/null || echo "000")
if [[ "$HTTP_CODE" -eq 200 ]]; then
    echo "✅ OK (HTTP $HTTP_CODE)"
else
    echo "❌ FAILED (HTTP $HTTP_CODE)"
    STATUS="UNHEALTHY"
fi

# Check 3: Metrics endpoint
echo -n "Metrics: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "http://$HOST:$PORT/metrics" 2>/dev/null || echo "000")
if [[ "$HTTP_CODE" -eq 200 ]]; then
    echo "✅ OK (HTTP $HTTP_CODE)"
else
    echo "⚠️ DEGRADED (HTTP $HTTP_CODE)"
    [[ "$STATUS" == "HEALTHY" ]] && STATUS="DEGRADED"
fi

echo ""
echo "=== Overall Status: $STATUS ==="
exit $([[ "$STATUS" == "HEALTHY" ]] && echo 0 || echo 1)
```

```bash
# ✅ GOOD — Kubernetes-native health check
# Use kubectl to check tempo service health
kubectl get pods -n tempo -o jsonpath=''.items[].status.conditions[?(@.type=="Ready")].status'
kubectl exec -n tempo deployment/tempo-controller -- curl -sf http://localhost:8080/healthz
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
---

## When to Use

Use this skill when:

- **Integrating a CNCF project into Kubernetes infrastructure** — You need to configure, deploy, or troubleshoot a cloud-native tool within a cluster
- **Designing cloud-native architecture** — You are selecting and integrating CNCF tools to solve specific infrastructure challenges
- **Resolving operational issues** — A CNCF component is misbehaving, underperforming, or needs configuration changes
---

## Core Workflow

1. **Assess Requirements** — Understand the use case, scale, integration needs, and existing infrastructure. **Checkpoint:** Document requirements, constraints, and success criteria.

2. **Design Architecture** — Plan component interactions, data flow, and deployment strategy using cloud-native best practices. **Checkpoint:** Verify the architecture addresses all requirements and follows CNCF conventions.

3. **Implement & Configure** — Create manifests, configurations, and deployment scripts. Include resource limits, health checks, and observability hooks. **Checkpoint:** Validate all YAML against schema and test in a staging environment.

4. **Deploy & Monitor** — Apply manifests to the cluster, verify component health, and confirm observability is working. **Checkpoint:** Confirm all pods/services are running, probes passing, and metrics/alerts configured.
