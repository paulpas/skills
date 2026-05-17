---
completeness: 95
content-types:
- guidance
- examples
- do-dont
- config
maturity: stable
---
# jaeger Namespace
apiVersion: v1
kind: Namespace
metadata:
  name: jaeger
  labels:
    app.kubernetes.io/name: jaeger
    app.kubernetes.io/managed-by: helm

---
# jaeger Service Account
apiVersion: v1
kind: ServiceAccount
metadata:
  name: jaeger
  namespace: jaeger
  labels:
    app.kubernetes.io/name: jaeger
---
# jaeger ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: jaeger-config
  namespace: jaeger
  labels:
    app.kubernetes.io/name: jaeger
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
      - /etc/jaeger/rules/*.yaml

    scrape_configs:
      - job_name: 'jaeger'
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
# jaeger Service
apiVersion: v1
kind: Service
metadata:
  name: jaeger
  namespace: jaeger
  labels:
    app.kubernetes.io/name: jaeger
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
    app.kubernetes.io/name: jaeger

---
# jaeger StatefulSet
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: jaeger
  namespace: jaeger
  labels:
    app.kubernetes.io/name: jaeger
spec:
  serviceName: jaeger
  replicas: 3
  selector:
    matchLabels:
      app.kubernetes.io/name: jaeger
  template:
    metadata:
      labels:
        app.kubernetes.io/name: jaeger
    spec:
      serviceAccountName: jaeger
      securityContext:
        fsGroup: 65534
        runAsGroup: 65534
        runAsNonRoot: true
        runAsUser: 65534
      containers:
        - name: jaeger
          image: jaeger/jaeger:v2.45.0
          args:
            - "--config.file=/etc/jaeger/config.yaml"
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
              mountPath: /etc/jaeger
            - name: data
              mountPath: /data
            - name: rules
              mountPath: /etc/jaeger/rules
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
            name: jaeger-config
        - name: rules
          configMap:
            name: jaeger-rules
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

### Pattern 1: Creating a jaeger Custom Resource (GOOD)

```bash
# ✅ GOOD — Create jaeger resource using kubectl
# Create namespace
kubectl create namespace jaeger --dry-run=client -o yaml | kubectl apply -f -

# Create ConfigMap for jaeger configuration
cat << 'EOF' | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: jaeger-config
  namespace: jaeger
data:
  replicas: "1"
  cpu_request: "100m"
  memory_request: "64Mi"
EOF

# Create jaeger deployment using kubectl
kubectl apply -f - << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger-controller
  namespace: jaeger
  labels:
    app.kubernetes.io/name: jaeger
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jaeger-controller
  template:
    metadata:
      labels:
        app: jaeger-controller
    spec:
      containers:
      - name: jaeger
        image: jaeger/controller:v1.0.0
        resources:
          requests:
            cpu: "100m"
            memory: "64Mi"
          limits:
            cpu: "500m"
            memory: "256Mi"
EOF

# Verify deployment
kubectl get pods -n jaeger -l app=jaeger-controller
kubectl describe deployment jaeger-controller -n jaeger
```

### Pattern 2: Querying jaeger Metrics (BAD vs GOOD)

```bash
# ✅ GOOD — Query jaeger metrics using curl
# Query jaeger metrics with error handling
METRICS_URL="http://localhost:8080/metrics"
TIMEOUT=10

# Test connectivity and fetch metrics
HTTP_CODE=$(curl -s -o /tmp/jaeger-metrics.txt -w "%{http_code}" --max-time $TIMEOUT "$METRICS_URL")
if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 400 ]]; then
    echo "✅ jaeger metrics retrieved (HTTP $HTTP_CODE)"
    head -20 /tmp/jaeger-metrics.txt
else
    echo "❌ Failed to get jaeger metrics (HTTP $HTTP_CODE)"
    exit 1
fi

# Query specific metrics with curl and grep
curl -s --max-time $TIMEOUT "$METRICS_URL" | grep "jaeger_active" | head -10

# Query jaeger API via port-forward
kubectl port-forward -n jaeger svc/jaeger 8080:8080 &
curl -s http://localhost:8080/api/v1/services | jq .
```

### Pattern 3: Health Check Implementation

```bash
# ✅ GOOD — Comprehensive jaeger health check using curl
#!/bin/bash
# check_jaeger_health.sh — Health checks for jaeger service

HOST="${1:-localhost}"
PORT="${2:-8081}"
TIMEOUT=5

echo "=== jaeger Health Check ==="

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
# Use kubectl to check jaeger service health
kubectl get pods -n jaeger -o jsonpath=''.items[].status.conditions[?(@.type=="Ready")].status'
kubectl exec -n jaeger deployment/jaeger-controller -- curl -sf http://localhost:8080/healthz
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
- Never expose jaeger API endpoints without authentication
- Never disable resource quotas in shared namespaces
- Never skip security scanning in CI/CD pipelines

## Related Skills

| Skill | Purpose |
|---|---|
| `cncf-jaeger-operator` | jaeger operator for Kubernetes deployment automation |
| `cncf-jaeger-integration` | Integration patterns with other CNCF projects |
| `cncf-jaeger-troubleshooting` | Common issues and debugging procedures for jaeger |
| `coding-jaeger-api` | jaeger API usage patterns and examples |

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

- **Official Documentation:** [https://jaeger.io/docs/](https://jaeger.io/docs/)
- **GitHub Repository:** [https://github.com/jaeger/jaeger](https://github.com/jaeger/jaeger)
- **CNCF Project Page:** [https://www.cncf.io/projects/jaeger/](https://www.cncf.io/projects/jaeger/)
- **Community:** Check the GitHub repository for community channels
- **Versioning:** Refer to project's release notes for version-specific features

---

## Troubleshooting

### Common Issues

1. **Deployment Failures**
   - Check pod logs for errors: `kubectl logs -n jaeger <pod-name>`
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
# Check jaeger pod status
kubectl get pods -n jaeger

# View recent logs
kubectl logs -n jaeger <pod-name> --tail=100 -f

# Query jaeger API directly
kubectl port-forward -n jaeger <pod-name> 9090:9090 &
curl http://localhost:9090/api/v1/targets

# Check configuration
kubectl get configmap jaeger-config -n jaeger -o yaml
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
