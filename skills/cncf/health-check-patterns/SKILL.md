---
name: health-check-patterns
description: Implements comprehensive health check patterns for cloud-native applications including Kubernetes probes, HTTP health endpoints, database checks, and circuit breaker patterns
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: cncf
  role: implementation
  scope: implementation
  output-format: code
  triggers: health checks, liveness probes, readiness probes, health monitoring, health endpoint, service health, health check implementation, health check testing
  related-skills: cncf-kubernetes-debugging, agent-docker-debugging, coding-fastapi-patterns
---

# Health Check Patterns

Comprehensive health check patterns for cloud-native applications, implementing Kubernetes probes (liveness, readiness, startup), HTTP health endpoints, database connectivity checks, external service monitoring, and circuit breaker patterns to ensure application reliability and service availability.

## TL;DR Checklist

- [ ] Implement separate liveness and readiness probes with distinct purposes
- [ ] Configure appropriate probe timeouts and thresholds for slow-starting applications
- [ ] Add database connection health checks with connection pool metrics
- [ ] Implement HTTP health endpoint with structured JSON response
- [ ] Monitor external service dependencies with timeout and retry logic
- [ ] Add circuit breaker patterns for failing external dependencies
- [ ] Test health checks in isolation before deployment
- [ ] Set up alerting based on health check failures with appropriate thresholds

---

## When to Use

Use health check patterns when:

- Deploying applications to Kubernetes or other container orchestration platforms
- Building microservices that need to expose health status for load balancers
- Implementing distributed systems with multiple external dependencies
- Creating resilient applications that must fail gracefully when dependencies fail
- Setting up CI/CD pipelines with automated health verification
- Designing service mesh configurations that depend on health status

---

## When NOT to Use

Avoid these patterns for:

- **Simple standalone scripts** — Use basic exit codes instead of complex health endpoints
- **Single-process applications without dependencies** — Health checks may add unnecessary overhead
- **Real-time systems with strict timing requirements** — Health check overhead may impact performance
- **Local development without orchestration** — Use simpler logging and error handling

---

## Core Workflow

1. **Design Health Strategy** — Define what "healthy" means for your application (database, cache, external services). **Checkpoint:** Document all dependencies and their health impact on service availability.

2. **Implement Kubernetes Probes** — Create separate liveness, readiness, and startup probes with appropriate configurations. **Checkpoint:** Verify probe endpoints respond correctly with correct HTTP status codes.

3. **Build HTTP Health Endpoint** — Create a standardized health endpoint that aggregates all dependency checks. **Checkpoint:** Test endpoint returns 200 OK when healthy and 503 Service Unavailable when degraded.

4. **Add Database Health Checks** — Implement connection pool monitoring with configurable timeout thresholds. **Checkpoint:** Verify health check fails gracefully when database is unreachable.

5. **Monitor External Services** — Create health checks for all external service dependencies with circuit breaker patterns. **Checkpoint:** Confirm circuit breaker opens when external service fails repeatedly.

6. **Set Up Testing and Validation** — Implement automated health check testing in CI/CD pipeline. **Checkpoint:** Run health check tests in staging environment matching production configuration.

---

## Implementation Patterns

### Pattern 1: Kubernetes Liveness Probes

Liveness probes determine if a container should be restarted. They should check internal application state, not external dependencies.

```yaml
# ❌ BAD — liveness probe checking external dependency (should not depend on database)
livenessProbe:
  httpGet:
    path: /health/live
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 2
  failureThreshold: 3

# ✅ GOOD — simple liveness probe checking application is still running
livenessProbe:
  exec:
    command:
      - /bin/sh
      - -c
      - "python -c 'import socket; s=socket.socket(); s.connect((\"localhost\", 8080)); s.close()'"
  initialDelaySeconds: 15
  periodSeconds: 20
  timeoutSeconds: 5
  failureThreshold: 3
```

**Best Practice:** Liveness probes should only check if the application process is responding, not if it's fully functional. Use external dependencies only for readiness probes.

### Pattern 2: Kubernetes Readiness Probes

Readiness probes determine if a pod should receive traffic. They should check all critical dependencies.

```yaml
# ✅ GOOD — readiness probe checking all dependencies
readinessProbe:
  httpGet:
    path: /health/ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  successThreshold: 1
  failureThreshold: 3

# ❌ BAD — readiness probe with incorrect thresholds
readinessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 0  # Too aggressive, starts receiving traffic before ready
  periodSeconds: 1  # Too frequent, creates overhead
  timeoutSeconds: 1  # Too short, may timeout on slow dependencies
```

### Pattern 3: Kubernetes Startup Probes

Startup probes are for slow-starting applications that need more time to initialize.

```yaml
# ✅ GOOD — startup probe for application with slow initialization
startupProbe:
  httpGet:
    path: /health/started
    port: 8080
  failureThreshold: 30
  periodSeconds: 10
  timeoutSeconds: 5

# ❌ BAD — startup probe missing, relying only on initialDelaySeconds
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 300  # Long delay but no startup probe
```

**Configuration Example:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: slow-start-app
spec:
  containers:
  - name: app
    image: my-app:latest
    ports:
    - containerPort: 8080
    startupProbe:
      httpGet:
        path: /health/started
        port: 8080
      failureThreshold: 60
      periodSeconds: 5
    livenessProbe:
      httpGet:
        path: /health/live
        port: 8080
      initialDelaySeconds: 60
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /health/ready
        port: 8080
      initialDelaySeconds: 10
      periodSeconds: 5
```

### Pattern 4: HTTP Health Endpoint with Structured Response

Create a standardized health endpoint that returns comprehensive status information.

```python
# ❌ BAD — simple health check without structured response
@app.get("/health")
def health():
    return {"status": "ok"}

# ✅ GOOD — comprehensive health endpoint with dependency checks
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import asyncio
import psycopg2
import redis

app = FastAPI()

class HealthStatus(BaseModel):
    status: str
    checks: dict
    timestamp: str

async def check_database():
    """Check database connectivity."""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="app",
            user="app",
            password="secret",
            connect_timeout=3
        )
        conn.close()
        return {"status": "healthy", "latency_ms": 15}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_redis():
    """Check Redis connectivity."""
    try:
        r = redis.Redis(host="localhost", port=6379, db=0, socket_timeout=3)
        r.ping()
        return {"status": "healthy", "latency_ms": 5}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Comprehensive health check with all dependencies."""
    import json
    from datetime import datetime
    
    checks = {}
    
    # Run all checks concurrently
    database_result = await check_database()
    redis_result = await check_redis()
    
    checks["database"] = database_result
    checks["redis"] = redis_result
    
    overall_status = "healthy" if all(
        check["status"] == "healthy" for check in checks.values()
    ) else "degraded"
    
    if any(check["status"] == "unhealthy" for check in checks.values()):
        raise HTTPException(
            status_code=503,
            detail={
                "status": overall_status,
                "checks": checks,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    return {
        "status": overall_status,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Pattern 5: Database Health Checks with Connection Pool Metrics

Monitor database health with connection pool statistics for proactive issue detection.

```python
# ❌ BAD — basic database health check without metrics
def check_database_health():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.close()
        return True
    except:
        return False

# ✅ GOOD — database health check with connection pool metrics
from contextlib import contextmanager
from typing import Dict, Any
import time

@contextmanager
def get_db_connection():
    """Context manager for database connections with proper cleanup."""
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

def get_connection_pool_metrics() -> Dict[str, Any]:
    """Get database connection pool metrics."""
    import psycopg2.pool
    
    pool = psycopg2.pool.SimpleConnectionPool(
        minconn=5,
        maxconn=20,
        **DB_CONFIG
    )
    
    metrics = {
        "total_connections": pool._pool.qsize() + len(pool._used),
        "available_connections": pool._pool.qsize(),
        "used_connections": len(pool._used),
        "max_connections": pool._maxconn,
    }
    
    return metrics

async def check_database_health() -> Dict[str, Any]:
    """Comprehensive database health check with metrics."""
    start_time = time.time()
    
    try:
        with get_db_connection() as conn:
            # Test connection with a simple query
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
        
        latency_ms = (time.time() - start_time) * 1000
        pool_metrics = get_connection_pool_metrics()
        
        return {
            "status": "healthy",
            "latency_ms": round(latency_ms, 2),
            "pool": pool_metrics,
            "last_check": time.time()
        }
    except psycopg2.OperationalError as e:
        return {
            "status": "unhealthy",
            "error": "Connection failed",
            "error_code": "DB_CONNECTION_FAILED",
            "details": str(e)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": "Database error",
            "error_code": "DB_ERROR",
            "details": str(e)
        }
```

### Pattern 6: External Service Health Checks with Circuit Breaker

Implement circuit breaker patterns for external service dependencies to prevent cascading failures.

```python
# ❌ BAD — no circuit breaker, repeated failures overwhelm external service
async def call_external_service():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.example.com/data") as response:
            return await response.json()

# ✅ GOOD — circuit breaker pattern for external service
import asyncio
from dataclasses import dataclass
from enum import Enum
import time
from typing import Optional

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    half_open_max_calls: int = 3
    failure_rate_threshold: float = 0.5
    min_request_threshold: int = 10

class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_calls = 0
    
    def is_allowed(self) -> bool:
        """Check if request is allowed based on circuit state."""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.config.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                return True
            return False
        
        if self.state == CircuitState.HALF_OPEN:
            return self.half_open_calls < self.config.half_open_max_calls
        
        return False
    
    def record_success(self):
        """Record successful call."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            self.half_open_calls += 1
            if self.half_open_calls >= self.config.half_open_max_calls:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
        elif self.state == CircuitState.CLOSED:
            self.success_count += 1
            self.failure_count = 0
    
    def record_failure(self):
        """Record failed call."""
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.last_failure_time = time.time()
            self.half_open_calls = 0
        
        if self.state == CircuitState.CLOSED:
            self.failure_count += 1
            self.success_count = 0
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                self.last_failure_time = time.time()

# Usage example
circuit_breaker = CircuitBreaker(CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=30.0
))

async def call_external_service_with_circuit_breaker(url: str) -> Optional[dict]:
    """Call external service with circuit breaker protection."""
    if not circuit_breaker.is_allowed():
        raise Exception("Circuit breaker is OPEN, request rejected")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status >= 500:
                    circuit_breaker.record_failure()
                    raise Exception(f"External service returned {response.status}")
                
                data = await response.json()
                circuit_breaker.record_success()
                return data
    except asyncio.TimeoutError:
        circuit_breaker.record_failure()
        raise
    except Exception as e:
        circuit_breaker.record_failure()
        raise
```

### Pattern 7: Health Check Testing with Docker Compose

Create comprehensive health check tests that validate all endpoints and dependencies.

```bash
# ❌ BAD — basic health check test without dependency validation
curl -f http://localhost:8080/health || exit 1

# ✅ GOOD — comprehensive health check test suite
#!/bin/bash
set -e

HEALTH_ENDPOINT="http://localhost:8080"
EXPECTED_RESPONSE_CODE=200

echo "=== Health Check Test Suite ==="

# Test 1: Basic health endpoint responds
echo "Test 1: Basic health endpoint"
RESPONSE=$(curl -s -w "\n%{http_code}" "$HEALTH_ENDPOINT/health")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
    echo "FAIL: Expected HTTP 200, got $HTTP_CODE"
    echo "Body: $BODY"
    exit 1
fi
echo "PASS: Health endpoint returns 200"

# Test 2: Liveness endpoint responds
echo "Test 2: Liveness endpoint"
LIVENESS_RESPONSE=$(curl -s -w "\n%{http_code}" "$HEALTH_ENDPOINT/health/live")
LIVENESS_CODE=$(echo "$LIVENESS_RESPONSE" | tail -1)

if [ "$LIVENESS_CODE" != "200" ]; then
    echo "FAIL: Liveness endpoint returned $LIVENESS_CODE"
    exit 1
fi
echo "PASS: Liveness endpoint returns 200"

# Test 3: Readiness endpoint responds
echo "Test 3: Readiness endpoint"
READINESS_RESPONSE=$(curl -s -w "\n%{http_code}" "$HEALTH_ENDPOINT/health/ready")
READINESS_CODE=$(echo "$READINESS_RESPONSE" | tail -1)

if [ "$READINESS_CODE" != "200" ]; then
    echo "FAIL: Readiness endpoint returned $READINESS_CODE"
    exit 1
fi
echo "PASS: Readiness endpoint returns 200"

# Test 4: JSON response structure validation
echo "Test 4: JSON response structure"
if ! echo "$BODY" | python3 -c "import json,sys; d=json.load(sys.stdin); assert 'status' in d" 2>/dev/null; then
    echo "FAIL: Missing 'status' field in response"
    exit 1
fi
echo "PASS: JSON structure valid"

# Test 5: Health endpoint with database dependency
echo "Test 5: Database dependency check"
if ! echo "$BODY" | python3 -c "import json,sys; d=json.load(sys.stdin); assert 'checks' in d and 'database' in d['checks']" 2>/dev/null; then
    echo "FAIL: Database check not included in response"
    exit 1
fi
echo "PASS: Database check included"

echo "=== All Tests Passed ==="
```

### Pattern 8: Kubernetes Health Check Debugging Commands

Debugging health check issues with kubectl commands and log analysis.

### Pattern 9: Python Health Check with Health Checks Library

Using the `health-checks` library for robust health monitoring.

```python
# ✅ GOOD — Using health-checks library for comprehensive monitoring
from health_checks import HealthCheck, HealthCheckMiddleware
from fastapi import FastAPI
import asyncio
import psycopg2
import redis
import time

app = FastAPI()

# Create health check instance
health = HealthCheck()

# Database health check
def database_check():
    """Check database connectivity."""
    try:
        start = time.time()
        conn = psycopg2.connect(
            host="localhost",
            database="app",
            user="app",
            password="secret",
            connect_timeout=3
        )
        conn.close()
        return True, {"latency_ms": int((time.time() - start) * 1000)}
    except Exception as e:
        return False, {"error": str(e)}

# Redis health check
def redis_check():
    """Check Redis connectivity."""
    try:
        start = time.time()
        r = redis.Redis(host="localhost", port=6379, db=0, socket_timeout=3)
        r.ping()
        return True, {"latency_ms": int((time.time() - start) * 1000)}
    except Exception as e:
        return False, {"error": str(e)}

# Add checks to health instance
health.add_check(database_check, "database")
health.add_check(redis_check, "redis")

# Add health endpoint middleware
app.add_middleware(HealthCheckMiddleware, health=health)

@app.get("/health")
async def health_endpoint():
    """Health endpoint using health-checks library."""
    results = await health.run_checks()
    return {
        "status": "healthy" if results["success"] else "unhealthy",
        "checks": results["results"],
        "total_time_ms": results["total_time_ms"]
    }
```

### Pattern 10: Go Health Check with net/http

Go implementation of health checks using standard library.

```go
// ✅ GOOD — Go health check implementation
package main

import (
    "context"
    "encoding/json"
    "log"
    "net/http"
    "os"
    "time"
    
    "github.com/go-redis/redis/v8"
)

type HealthStatus struct {
    Status     string            `json:"status"`
    Checks     map[string]Check  `json:"checks"`
    Timestamp  string            `json:"timestamp"`
}

type Check struct {
    Status  string `json:"status"`
    Error   string `json:"error,omitempty"`
    Latency string `json:"latency,omitempty"`
}

func checkDatabase(ctx context.Context) Check {
    start := time.Now()
    // Database connection logic here
    duration := time.Since(start)
    
    return Check{
        Status:  "healthy",
        Latency: duration.String(),
    }
}

func checkRedis(ctx context.Context, client *redis.Client) Check {
    start := time.Now()
    err := client.Ping(ctx).Err()
    duration := time.Since(start)
    
    if err != nil {
        return Check{
            Status: "unhealthy",
            Error:  err.Error(),
        }
    }
    
    return Check{
        Status:  "healthy",
        Latency: duration.String(),
    }
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
    ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
    defer cancel()
    
    checks := make(map[string]Check)
    
    // Run checks
    checks["database"] = checkDatabase(ctx)
    
    redisClient := redis.NewClient(&redis.Options{
        Addr: "localhost:6379",
    })
    checks["redis"] = checkRedis(ctx, redisClient)
    
    // Determine overall status
    status := "healthy"
    for _, check := range checks {
        if check.Status != "healthy" {
            status = "unhealthy"
            break
        }
    }
    
    if status != "healthy" {
        w.WriteHeader(http.StatusServiceUnavailable)
    }
    
    response := HealthStatus{
        Status:    status,
        Checks:    checks,
        Timestamp: time.Now().UTC().Format(time.RFC3339),
    }
    
    json.NewEncoder(w).Encode(response)
}

func main() {
    http.HandleFunc("/health", healthHandler)
    log.Fatal(http.ListenAndServe(":8080", nil))
}
```

### Pattern 11: Node.js Health Check with Express

Node.js implementation with Express framework.

```javascript
// ✅ GOOD — Node.js Express health check
const express = require('express');
const { Pool } = require('pg');
const redis = require('redis');
const app = express();

const pool = new Pool({
    host: process.env.DB_HOST || 'localhost',
    database: process.env.DB_NAME || 'app',
    user: process.env.DB_USER || 'app',
    password: process.env.DB_PASSWORD || 'secret',
    connectionTimeoutMillis: 3000
});

const redisClient = redis.createClient({
    url: process.env.REDIS_URL || 'redis://localhost:6379',
    socket: { timeout: 3000 }
});

async function checkDatabase() {
    try {
        const start = Date.now();
        const client = await pool.connect();
        await client.query('SELECT 1');
        client.release();
        const latency = Date.now() - start;
        
        return { status: 'healthy', latency_ms: latency };
    } catch (error) {
        return { status: 'unhealthy', error: error.message };
    }
}

async function checkRedis() {
    try {
        const start = Date.now();
        await redisClient.ping();
        const latency = Date.now() - start;
        
        return { status: 'healthy', latency_ms: latency };
    } catch (error) {
        return { status: 'unhealthy', error: error.message };
    }
}

app.get('/health', async (req, res) => {
    const checks = {};
    
    try {
        const [dbResult, redisResult] = await Promise.all([
            checkDatabase(),
            checkRedis()
        ]);
        
        checks.database = dbResult;
        checks.redis = redisResult;
        
        const allHealthy = Object.values(checks).every(c => c.status === 'healthy');
        
        res.status(allHealthy ? 200 : 503).json({
            status: allHealthy ? 'healthy' : 'degraded',
            checks,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(503).json({
            status: 'unhealthy',
            checks,
            error: error.message
        });
    }
});

// Separate liveness endpoint
app.get('/health/live', (req, res) => {
    res.status(200).json({ status: 'ok' });
});

// Separate readiness endpoint
app.get('/health/ready', async (req, res) => {
    try {
        const results = await Promise.all([
            checkDatabase(),
            checkRedis()
        ]);
        
        const allHealthy = results.every(r => r.status === 'healthy');
        res.status(allHealthy ? 200 : 503).json({
            status: allHealthy ? 'healthy' : 'unhealthy',
            checks: { database: results[0], redis: results[1] }
        });
    } catch (error) {
        res.status(503).json({ status: 'unhealthy', error: error.message });
    }
});

app.listen(8080, () => {
    console.log('Health check server running on port 8080');
});
```

### Pattern 12: Java Spring Boot Health Check

Spring Boot implementation with Actuator.

```java
// ✅ GOOD — Spring Boot Actuator health check
package com.example.health;

import org.springframework.boot.actuate.health.*;
import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.Map;

@Component
public class CustomHealthIndicator implements HealthIndicator {
    
    @Autowired
    private DataSource dataSource;
    
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;
    
    @Override
    public Health health() {
        Map<String, Object> details = new HashMap<>();
        
        Health databaseHealth = checkDatabase(details);
        Health redisHealth = checkRedis(details);
        
        Health.Builder builder = Health.status(databaseHealth.getStatus().getCode());
        if (databaseHealth.getStatus() != Status.UP || redisHealth.getStatus() != Status.UP) {
            builder = Health.down();
        }
        
        return builder
            .withDetails(details)
            .withDetail("timestamp", System.currentTimeMillis())
            .build();
    }
    
    private Health checkDatabase(Map<String, Object> details) {
        try {
            long start = System.currentTimeMillis();
            try (Connection conn = dataSource.getConnection()) {
                if (conn.isValid(3)) {
                    long latency = System.currentTimeMillis() - start;
                    details.put("database", Map.of(
                        "status", "healthy",
                        "latency_ms", latency
                    ));
                    return Health.up().build();
                }
            }
        } catch (SQLException e) {
            details.put("database", Map.of(
                "status", "unhealthy",
                "error", e.getMessage()
            ));
            return Health.down(e).build();
        }
        
        details.put("database", Map.of("status", "unhealthy", "error", "Connection invalid"));
        return Health.down().withDetail("error", "Database connection invalid").build();
    }
    
    private Health checkRedis(Map<String, Object> details) {
        try {
            long start = System.currentTimeMillis();
            String ping = redisTemplate.execute(RedisConnection::ping);
            long latency = System.currentTimeMillis() - start;
            
            if ("PONG".equals(ping)) {
                details.put("redis", Map.of(
                    "status", "healthy",
                    "latency_ms", latency
                ));
                return Health.up().build();
            }
        } catch (Exception e) {
            details.put("redis", Map.of(
                "status", "unhealthy",
                "error", e.getMessage()
            ));
            return Health.down(e).build();
        }
        
        details.put("redis", Map.of("status", "unhealthy", "error", "Redis ping failed"));
        return Health.down().withDetail("error", "Redis ping failed").build();
    }
}
```

### Pattern 13: Health Check Metrics with Prometheus

Exporting health check metrics for monitoring.

```python
# ✅ GOOD — Prometheus metrics for health checks
from prometheus_client import Counter, Gauge, Histogram, start_http_server
import time

# Metrics definitions
HEALTH_CHECK_TOTAL = Counter(
    'health_check_total',
    'Total number of health checks',
    ['check_name', 'status']
)

HEALTH_CHECK_DURATION = Histogram(
    'health_check_duration_seconds',
    'Duration of health checks',
    ['check_name']
)

HEALTH_CHECK_LIVE = Gauge(
    'health_check_live',
    'Live health status (1 = healthy, 0 = unhealthy)',
    []
)

HEALTH_CHECK_READY = Gauge(
    'health_check_ready',
    'Ready health status (1 = healthy, 0 = unhealthy)',
    []
)

# Start metrics server
start_http_server(9090)

async def check_database_with_metrics():
    """Database health check with Prometheus metrics."""
    start = time.time()
    
    try:
        # Database connection logic
        conn = psycopg2.connect(**DB_CONFIG)
        conn.close()
        
        duration = time.time() - start
        
        HEALTH_CHECK_TOTAL.labels(check_name='database', status='healthy').inc()
        HEALTH_CHECK_DURATION.labels(check_name='database').observe(duration)
        
        return {
            "status": "healthy",
            "latency_ms": int(duration * 1000)
        }
    except Exception as e:
        duration = time.time() - start
        
        HEALTH_CHECK_TOTAL.labels(check_name='database', status='unhealthy').inc()
        HEALTH_CHECK_DURATION.labels(check_name='database').observe(duration)
        
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Query example for Prometheus
# Query: health_check_duration_seconds{check_name="database"} > 1
# Alert: health_check_total{status="unhealthy"} > 0 for 5m
```

### Pattern 14: Health Check with Retry Logic

Implementing retry logic for transient failures.

```python
# ✅ GOOD — Health check with exponential backoff retry
import asyncio
import random
from typing import Optional
from functools import wraps

class HealthCheckError(Exception):
    """Custom exception for health check failures."""
    pass

def retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=10.0):
    """Decorator for retrying health checks with exponential backoff."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except HealthCheckError as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        # Exponential backoff with jitter
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        jitter = random.uniform(0, delay * 0.1)
                        await asyncio.sleep(delay + jitter)
            
            raise last_error
        
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3, base_delay=0.5)
async def check_database_with_retry():
    """Database health check with retry logic."""
    import psycopg2
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        
        return {"status": "healthy"}
    except psycopg2.OperationalError as e:
        raise HealthCheckError(f"Database connection failed: {e}")

@retry_with_backoff(max_retries=3, base_delay=0.5)
async def check_redis_with_retry():
    """Redis health check with retry logic."""
    import redis
    
    try:
        r = redis.Redis(host="localhost", port=6379, db=0, socket_timeout=3)
        r.ping()
        return {"status": "healthy"}
    except redis.ConnectionError as e:
        raise HealthCheckError(f"Redis connection failed: {e}")

# Usage example
async def comprehensive_health_check():
    """Comprehensive health check with all retries."""
    checks = {}
    
    try:
        checks["database"] = await check_database_with_retry()
    except HealthCheckError as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}
    
    try:
        checks["redis"] = await check_redis_with_retry()
    except HealthCheckError as e:
        checks["redis"] = {"status": "unhealthy", "error": str(e)}
    
    return checks
```

### Pattern 15: Health Check in Docker Container

Docker container health check configuration.

```dockerfile
# ✅ GOOD — Docker health check configuration
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .

# Health check with curl
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health/live || exit 1

EXPOSE 8080

CMD ["python", "app.py"]
```

```yaml
# Alternative: Docker Compose health check
version: '3.8'

services:
  app:
    image: my-app:latest
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health/live"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    ports:
      - "8080:8080"
  
  db:
    image: postgres:15
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    environment:
      POSTGRES_PASSWORD: secret
```

### Pattern 16: Health Check with Graceful Degradation

Implementing graceful degradation for non-critical dependencies.

```python
# ✅ GOOD — Health check with graceful degradation
from enum import Enum
from typing import Dict, Any, List

class DependencyType(Enum):
    CRITICAL = "critical"
    OPTIONAL = "optional"
    NON_CRITICAL = "non_critical"

class HealthCheckResult:
    def __init__(self):
        self.checks: Dict[str, Dict[str, Any]] = {}
    
    def add_check(self, name: str, status: str, 
                  dependency_type: DependencyType, 
                  details: Dict[str, Any] = None):
        """Add a health check result with dependency type."""
        self.checks[name] = {
            "status": status,
            "dependency_type": dependency_type.value,
            "details": details or {}
        }
    
    def get_overall_status(self) -> str:
        """Determine overall health status based on dependency types."""
        has_critical_failure = False
        has_optional_failure = False
        
        for check in self.checks.values():
            if check["status"] == "unhealthy":
                if check["dependency_type"] == DependencyType.CRITICAL.value:
                    has_critical_failure = True
                elif check["dependency_type"] == DependencyType.OPTIONAL.value:
                    has_optional_failure = True
        
        if has_critical_failure:
            return "unhealthy"
        elif has_optional_failure:
            return "degraded"
        return "healthy"
    
    def get_http_status(self) -> int:
        """Get appropriate HTTP status code."""
        status = self.get_overall_status()
        if status == "healthy":
            return 200
        elif status == "degraded":
            return 200  # Still serving traffic
        else:
            return 503

async def check_all_services() -> HealthCheckResult:
    """Check all services with appropriate dependency types."""
    result = HealthCheckResult()
    
    # Critical dependencies
    db_result = await check_database()
    if db_result["status"] == "healthy":
        result.add_check("database", "healthy", DependencyType.CRITICAL)
    else:
        result.add_check("database", "unhealthy", DependencyType.CRITICAL, 
                        {"error": db_result.get("error")})
    
    # Optional dependencies
    cache_result = await check_cache()
    if cache_result["status"] == "healthy":
        result.add_check("cache", "healthy", DependencyType.OPTIONAL)
    else:
        result.add_check("cache", "unhealthy", DependencyType.OPTIONAL,
                        {"error": cache_result.get("error")})
    
    # Non-critical dependencies
    metrics_result = await check_metrics()
    if metrics_result["status"] == "healthy":
        result.add_check("metrics", "healthy", DependencyType.NON_CRITICAL)
    else:
        result.add_check("metrics", "unhealthy", DependencyType.NON_CRITICAL,
                        {"error": metrics_result.get("error")})
    
    return result

@app.get("/health")
async def health():
    """Health endpoint with graceful degradation."""
    result = await check_all_services()
    
    return {
        "status": result.get_overall_status(),
        "http_status": result.get_http_status(),
        "checks": result.checks
    }
```

### Pattern 17: Health Check with Rate Limiting

Implementing rate limiting on health check endpoints.

```python
# ✅ GOOD — Health check with rate limiting
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

app = FastAPI()
limiter = Limiter(key_func=get_remote_address)

# Health check endpoint with rate limiting
@app.get("/health")
@limiter.limit("10/minute")
async def health_check(request: Request):
    """Health check endpoint with rate limiting (10 requests per minute)."""
    checks = await run_all_health_checks()
    return {
        "status": "healthy" if all(c["status"] == "healthy" for c in checks.values()) else "unhealthy",
        "checks": checks
    }

@app.get("/health/live")
@limiter.limit("100/minute")
async def liveness(request: Request):
    """Liveness endpoint with higher rate limit."""
    return {"status": "ok"}

# Custom rate limit exceeded handler
@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc):
    """Handle rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded for health check endpoint"}
    )

# Rate limit configuration
rate_limits = {
    "/health": "10/minute",
    "/health/live": "100/minute",
    "/health/ready": "30/minute",
    "/health/metrics": "5/minute"  # Lower limit for metrics endpoint
}
```

### Pattern 18: Health Check with Cache

Caching health check results to reduce load on dependencies.

```python
# ✅ GOOD — Health check with result caching
import time
from functools import wraps
from typing import Dict, Any, Optional

# Cache configuration
HEALTH_CHECK_CACHE_TTL = 5  # seconds
_health_cache: Dict[str, Dict[str, Any]] = {}
_cache_timestamps: Dict[str, float] = {}

def cached_health_check(ttl: int = HEALTH_CHECK_CACHE_TTL):
    """Decorator for caching health check results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            check_name = func.__name__
            now = time.time()
            
            # Check if cached result is still valid
            if check_name in _health_cache:
                if now - _cache_timestamps.get(check_name, 0) < ttl:
                    return _health_cache[check_name]
            
            # Execute check and cache result
            result = await func(*args, **kwargs)
            _health_cache[check_name] = result
            _cache_timestamps[check_name] = now
            
            return result
        
        return wrapper
    return decorator

@cached_health_check(ttl=5)
async def check_database():
    """Database health check with caching."""
    import psycopg2
    
    start = time.time()
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.close()
        latency = (time.time() - start) * 1000
        
        return {"status": "healthy", "latency_ms": round(latency, 2)}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@cached_health_check(ttl=5)
async def check_redis():
    """Redis health check with caching."""
    import redis
    
    start = time.time()
    try:
        r = redis.Redis(host="localhost", port=6379, db=0, socket_timeout=3)
        r.ping()
        latency = (time.time() - start) * 1000
        
        return {"status": "healthy", "latency_ms": round(latency, 2)}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def health_check_with_cache():
    """Health check using cached results."""
    checks = {
        "database": await check_database(),
        "redis": await check_redis()
    }
    
    return {
        "status": "healthy" if all(c["status"] == "healthy" for c in checks.values()) else "unhealthy",
        "checks": checks,
        "cached": True  # Indicate results were cached
    }
```

### Pattern 19: Health Check with Circuit Breaker States

Visualizing circuit breaker states in health check response.

```python
# ✅ GOOD — Health check with circuit breaker state visualization
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any
import time

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation, requests pass through
    OPEN = "open"          # Circuit tripped, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service recovered

@dataclass
class CircuitBreaker:
    name: str
    state: CircuitState
    failure_count: int = 0
    last_failure_time: Optional[float] = None
    recovery_timeout: float = 30.0
    failure_threshold: int = 5
    
    def should_allow_request(self) -> bool:
        """Check if request should be allowed."""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        
        return True  # Half-open allows limited requests
    
    def record_success(self):
        """Record successful request."""
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0
    
    def record_failure(self):
        """Record failed request."""
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.last_failure_time = time.time()
        elif self.state == CircuitState.CLOSED:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.last_failure_time = time.time()

class HealthCheckManager:
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.last_health_time = time.time()
    
    def add_circuit_breaker(self, name: str, **kwargs):
        """Add a circuit breaker for a dependency."""
        self.circuit_breakers[name] = CircuitBreaker(name=name, **kwargs)
    
    def get_health_with_circuit_breakers(self) -> Dict[str, Any]:
        """Get health status including circuit breaker states."""
        checks = {}
        all_healthy = True
        
        for name, cb in self.circuit_breakers.items():
            allowed = cb.should_allow_request()
            
            check_status = {
                "status": "healthy" if allowed else "circuit_open",
                "circuit_state": cb.state.value,
                "failure_count": cb.failure_count,
                "allowing_requests": allowed
            }
            
            if not allowed:
                all_healthy = False
            
            if cb.last_failure_time:
                seconds_since_failure = time.time() - cb.last_failure_time
                check_status["seconds_since_last_failure"] = round(seconds_since_failure, 1)
            
            checks[name] = check_status
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "checks": checks,
            "timestamp": time.time()
        }

# Initialize manager
health_manager = HealthCheckManager()
health_manager.add_circuit_breaker("database", failure_threshold=5, recovery_timeout=30)
health_manager.add_circuit_breaker("redis", failure_threshold=3, recovery_timeout=10)

@app.get("/health")
async def health():
    """Health check with circuit breaker state visualization."""
    return health_manager.get_health_with_circuit_breakers()
```

### Pattern 20: Health Check with Dependency Graph

Visualizing dependency relationships in health check response.

```python
# ✅ GOOD — Health check with dependency graph visualization
from typing import Dict, Any, List, Set
from dataclasses import dataclass
from enum import Enum

class DependencyStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class DependencyNode:
    name: str
    status: DependencyStatus
    dependencies: List[str] = None  # List of dependencies this node relies on
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class HealthDependencyGraph:
    def __init__(self):
        self.nodes: Dict[str, DependencyNode] = {}
    
    def add_dependency(self, name: str, status: DependencyStatus, 
                      depends_on: List[str] = None):
        """Add a dependency node to the graph."""
        self.nodes[name] = DependencyNode(
            name=name,
            status=status,
            dependencies=depends_on or []
        )
    
    def get_dependency_graph(self) -> Dict[str, Any]:
        """Get the dependency graph structure."""
        graph = {}
        for name, node in self.nodes.items():
            graph[name] = {
                "status": node.status.value,
                "depends_on": node.dependencies
            }
        return graph
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status with dependency information."""
        overall_status = DependencyStatus.HEALTHY
        
        for node in self.nodes.values():
            if node.status == DependencyStatus.UNHEALTHY:
                overall_status = DependencyStatus.UNHEALTHY
            elif node.status == DependencyStatus.DEGRADED:
                if overall_status != DependencyStatus.UNHEALTHY:
                    overall_status = DependencyStatus.DEGRADED
        
        return {
            "status": overall_status.value,
            "dependencies": {
                name: {
                    "status": node.status.value,
                    "depends_on": node.dependencies
                }
                for name, node in self.nodes.items()
            },
            "graph": self.get_dependency_graph()
        }

# Example dependency graph
# API Service depends on Database and Redis
# Redis depends on Memory Cache
# Database depends on PostgreSQL

health_graph = HealthDependencyGraph()
health_graph.add_dependency("postgresql", DependencyStatus.HEALTHY)
health_graph.add_dependency("database", DependencyStatus.HEALTHY, 
                           depends_on=["postgresql"])
health_graph.add_dependency("memory_cache", DependencyStatus.HEALTHY)
health_graph.add_dependency("redis", DependencyStatus.HEALTHY, 
                           depends_on=["memory_cache"])
health_graph.add_dependency("api_service", DependencyStatus.HEALTHY,
                           depends_on=["database", "redis"])

@app.get("/health/dependencies")
async def health_with_dependencies():
    """Health check with dependency graph visualization."""
    return health_graph.get_health_status()

# Example response:
# {
#   "status": "healthy",
#   "dependencies": {
#     "postgresql": {"status": "healthy", "depends_on": []},
#     "database": {"status": "healthy", "depends_on": ["postgresql"]},
#     "memory_cache": {"status": "healthy", "depends_on": []},
#     "redis": {"status": "healthy", "depends_on": ["memory_cache"]},
#     "api_service": {"status": "healthy", "depends_on": ["database", "redis"]}
#   }
# }
```

### Pattern 21: Health Check with SLA Metrics

Tracking health check SLA compliance.

```python
# ✅ GOOD — Health check with SLA metrics tracking
from dataclasses import dataclass
from typing import Dict, List
import time
from collections import deque
from datetime import datetime, timedelta

@dataclass
class SLAMetrics:
    window_seconds: int = 300  # 5 minutes
    max_p95_latency_ms: int = 100
    max_failure_rate: float = 0.01  # 1%
    
    def __post_init__(self):
        self.latency_samples: deque = deque(maxlen=1000)
        self.check_results: deque = deque(maxlen=1000)
    
    def record_check(self, latency_ms: float, successful: bool):
        """Record a health check result."""
        self.latency_samples.append(latency_ms)
        self.check_results.append({
            "timestamp": time.time(),
            "latency_ms": latency_ms,
            "successful": successful
        })
    
    def get_sla_compliance(self) -> Dict[str, Any]:
        """Get current SLA compliance status."""
        if not self.latency_samples:
            return {"compliant": True, "reason": "No samples yet"}
        
        # Calculate p95 latency
        sorted_latencies = sorted(self.latency_samples)
        p95_index = int(len(sorted_latencies) * 0.95)
        p95_latency = sorted_latencies[min(p95_index, len(sorted_latencies) - 1)]
        
        # Calculate failure rate
        recent_checks = list(self.check_results)[-100:]  # Last 100 checks
        failure_count = sum(1 for c in recent_checks if not c["successful"])
        failure_rate = failure_count / len(recent_checks) if recent_checks else 0
        
        compliant = (
            p95_latency <= self.max_p95_latency_ms and
            failure_rate <= self.max_failure_rate
        )
        
        return {
            "compliant": compliant,
            "p95_latency_ms": round(p95_latency, 2),
            "max_allowed_p95_latency_ms": self.max_p95_latency_ms,
            "failure_rate": round(failure_rate, 4),
            "max_allowed_failure_rate": self.max_failure_rate,
            "sample_count": len(self.latency_samples),
            "window_seconds": self.window_seconds
        }

class SLAHealthChecker:
    def __init__(self, sla_config: SLAMetrics = None):
        self.sla_config = sla_config or SLAMetrics()
        self.check_history: Dict[str, deque] = {}
    
    def check_database(self) -> Dict[str, Any]:
        """Database health check with SLA tracking."""
        start = time.time()
        
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            latency_ms = (time.time() - start) * 1000
            
            self.sla_config.record_check(latency_ms, True)
            
            return {
                "status": "healthy",
                "latency_ms": round(latency_ms, 2),
                "sla": self.sla_config.get_sla_compliance()
            }
        except Exception as e:
            latency_ms = (time.time() - start) * 1000
            self.sla_config.record_check(latency_ms, False)
            
            return {
                "status": "unhealthy",
                "error": str(e),
                "sla": self.sla_config.get_sla_compliance()
            }

# SLA alerting configuration
SLA_ALERTS = {
    "warning": {
        "p95_latency_ms": 80,
        "failure_rate": 0.005
    },
    "critical": {
        "p95_latency_ms": 100,
        "failure_rate": 0.01
    }
}
```

### Pattern 22: Health Check with Tracing Integration

Integrating health checks with distributed tracing.

```python
# ✅ GOOD — Health check with OpenTelemetry tracing
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import time
import random

# Configure OpenTelemetry
trace.set_tracer_provider(TracerProvider())
jaeger_exporter = JaegerExporter(
    agent_host_name='localhost',
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

def health_check_with_tracing(name: str, check_func):
    """Wrapper for health checks with distributed tracing."""
    async def wrapper(*args, **kwargs):
        with tracer.start_as_current_span(f"health.check.{name}") as span:
            span.set_attribute("component", "health-check")
            span.set_attribute("check.name", name)
            
            start = time.time()
            try:
                result = await check_func(*args, **kwargs)
                latency_ms = (time.time() - start) * 1000
                
                span.set_attribute("health.status", "healthy")
                span.set_attribute("health.latency_ms", latency_ms)
                
                return result
            except Exception as e:
                latency_ms = (time.time() - start) * 1000
                
                span.set_attribute("health.status", "unhealthy")
                span.set_attribute("health.error", str(e))
                span.record_exception(e)
                
                raise
    
    return wrapper

@health_check_with_tracing("database")
async def check_database_with_tracing():
    """Database health check with OpenTelemetry tracing."""
    import psycopg2
    
    conn = psycopg2.connect(**DB_CONFIG)
    conn.close()
    
    return {"status": "healthy"}

@health_check_with_tracing("redis")
async def check_redis_with_tracing():
    """Redis health check with OpenTelemetry tracing."""
    import redis
    
    r = redis.Redis(host="localhost", port=6379, db=0, socket_timeout=3)
    r.ping()
    
    return {"status": "healthy"}

@app.get("/health")
async def health_with_tracing():
    """Health check endpoint with distributed tracing."""
    import asyncio
    
    with tracer.start_as_current_span("health.check.composite") as span:
        span.set_attribute("check.type", "composite")
        
        # Run all checks concurrently
        results = await asyncio.gather(
            check_database_with_tracing(),
            check_redis_with_tracing()
        )
        
        all_healthy = all(r["status"] == "healthy" for r in results)
        
        span.set_attribute("health.overall", "healthy" if all_healthy else "unhealthy")
        
        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "checks": results
        }

# Example span attributes in Jaeger/Zipkin:
# - health.check.database
#   - health.status: healthy
#   - health.latency_ms: 15.2
#   - check.name: database
#   - component: health-check
```

### Pattern 23: Health Check with Fallback Strategy

Implementing fallback responses for critical health checks.

```python
# ✅ GOOD — Health check with fallback strategy
from typing import Optional, Callable, Any
import asyncio

class HealthCheckWithFallback:
    def __init__(self):
        self.primary_checks: dict = {}
        self.fallback_checks: dict = {}
    
    def register_primary(self, name: str, check_func: Callable):
        """Register a primary health check."""
        self.primary_checks[name] = check_func
    
    def register_fallback(self, name: str, check_func: Callable):
        """Register a fallback health check."""
        self.fallback_checks[name] = check_func
    
    async def check_with_fallback(self, name: str) -> dict:
        """Check health with fallback strategy."""
        # Primary check
        if name in self.primary_checks:
            try:
                result = await self.primary_checks[name]()
                if result.get("status") == "healthy":
                    return {
                        "status": "healthy",
                        "source": "primary",
                        **result
                    }
            except Exception:
                pass  # Fall through to fallback
        
        # Fallback check
        if name in self.fallback_checks:
            try:
                result = await self.fallback_checks[name]()
                if result.get("status") == "healthy":
                    return {
                        "status": "healthy",
                        "source": "fallback",
                        **result,
                        "warning": "Using fallback health check"
                    }
            except Exception:
                pass
        
        return {
            "status": "unhealthy",
            "error": "All health checks failed",
            "checked_sources": ["primary", "fallback"]
        }

# Example usage
health_fallback = HealthCheckWithFallback()

# Primary: Check database directly
async def primary_db_check():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.close()
    return {"status": "healthy", "latency_ms": 15}

# Fallback: Check if database pod is running (Kubernetes)
async def fallback_db_check():
    import subprocess
    try:
        result = subprocess.run(
            ["kubectl", "get", "pod", "postgres-0", "-o", "name"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            return {"status": "healthy", "source": "kubernetes"}
    except:
        pass
    return {"status": "unhealthy"}

# Register checks
health_fallback.register_primary("database", primary_db_check)
health_fallback.register_fallback("database", fallback_db_check)

# Usage
async def health_endpoint():
    db_result = await health_fallback.check_with_fallback("database")
    
    return {
        "status": db_result["status"],
        "checks": {"database": db_result}
    }

@app.get("/health")
async def health():
    return await health_endpoint()
```

### Pattern 24: Health Check with Dependency Priority

Weighting health checks by dependency priority.

```python
# ✅ GOOD — Health check with dependency priority
from enum import Enum
from typing import Dict, Any, List
import time

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class PrioritizedHealthCheck:
    def __init__(self):
        self.checks: Dict[str, Dict[str, Any]] = {}
    
    def add_check(self, name: str, check_func, priority: Priority = Priority.MEDIUM):
        """Add a health check with priority."""
        self.checks[name] = {
            "func": check_func,
            "priority": priority,
            "last_run": None,
            "last_status": None
        }
    
    async def run_check(self, name: str) -> dict:
        """Run a single health check."""
        if name not in self.checks:
            return {"status": "unknown", "error": "Check not found"}
        
        check = self.checks[name]
        start = time.time()
        
        try:
            result = await check["func"]()
            duration = time.time() - start
            
            check["last_run"] = time.time()
            check["last_status"] = result.get("status", "unknown")
            
            return {
                **result,
                "priority": check["priority"].value,
                "duration_ms": round(duration * 1000, 2),
                "last_run": check["last_run"]
            }
        except Exception as e:
            duration = time.time() - start
            
            check["last_run"] = time.time()
            check["last_status"] = "unhealthy"
            
            return {
                "status": "unhealthy",
                "error": str(e),
                "priority": check["priority"].value,
                "duration_ms": round(duration * 1000, 2)
            }
    
    async def get_health_with_priority(self) -> dict:
        """Get health status weighted by priority."""
        results = {}
        weighted_status = "healthy"
        weighted_score = 0
        
        # Calculate weights
        total_priority = sum(c["priority"].value for c in self.checks.values())
        
        for name, check in self.checks.items():
            result = await self.run_check(name)
            results[name] = result
            
            # Weight by priority
            priority_weight = check["priority"].value / total_priority
            
            if result["status"] == "healthy":
                weighted_score += priority_weight
            else:
                if check["priority"] == Priority.CRITICAL:
                    weighted_status = "unhealthy"
                elif check["priority"] == Priority.HIGH and weighted_status != "unhealthy":
                    weighted_status = "degraded"
        
        return {
            "status": weighted_status,
            "score": round(weighted_score, 4),
            "checks": results,
            "timestamp": time.time()
        }

# Example setup
health_priority = PrioritizedHealthCheck()

async def database_check():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.close()
    return {"status": "healthy"}

async def redis_check():
    r = redis.Redis(host="localhost", port=6379, socket_timeout=3)
    r.ping()
    return {"status": "healthy"}

async def external_api_check():
    # External API - lower priority
    return {"status": "healthy"}

# Register checks with priorities
health_priority.add_check("database", database_check, Priority.CRITICAL)
health_priority.add_check("redis", redis_check, Priority.HIGH)
health_priority.add_check("external_api", external_api_check, Priority.LOW)

@app.get("/health/prioritized")
async def prioritized_health():
    return await health_priority.get_health_with_priority()
```

### Pattern 25: Health Check with Dependency Health Thresholds

Configurable thresholds for health check acceptance.

```python
# ✅ GOOD — Health check with configurable thresholds
from dataclasses import dataclass
from typing import Dict, Any, Optional
import time

@dataclass
class HealthThresholds:
    max_latency_ms: float = 100.0
    max_error_rate: float = 0.01
    min_success_rate: float = 0.99
    max_consecutive_failures: int = 3

class ThresholdBasedHealthCheck:
    def __init__(self):
        self.results: Dict[str, list] = {}
        self.thresholds: Dict[str, HealthThresholds] = {}
        self.consecutive_failures: Dict[str, int] = {}
    
    def set_thresholds(self, name: str, thresholds: HealthThresholds):
        """Set thresholds for a specific health check."""
        self.thresholds[name] = thresholds
    
    def record_result(self, name: str, latency_ms: float, success: bool):
        """Record a health check result."""
        if name not in self.results:
            self.results[name] = []
            self.consecutive_failures[name] = 0
        
        self.results[name].append({
            "timestamp": time.time(),
            "latency_ms": latency_ms,
            "success": success
        })
        
        # Keep only recent results (last 100)
        self.results[name] = self.results[name][-100:]
        
        if success:
            self.consecutive_failures[name] = 0
        else:
            self.consecutive_failures[name] += 1
    
    def get_health_with_thresholds(self, name: str) -> dict:
        """Get health status based on thresholds."""
        results = self.results.get(name, [])
        thresholds = self.thresholds.get(name, HealthThresholds())
        
        if not results:
            return {
                "status": "healthy",
                "reason": "No samples yet",
                "samples": 0
            }
        
        # Calculate metrics
        latencies = [r["latency_ms"] for r in results]
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        error_rate = sum(1 for r in results if not r["success"]) / len(results)
        
        # Check thresholds
        issues = []
        
        if max_latency > thresholds.max_latency_ms:
            issues.append(f"Max latency {max_latency:.1f}ms exceeds threshold {thresholds.max_latency_ms}ms")
        
        if error_rate > thresholds.max_error_rate:
            issues.append(f"Error rate {error_rate:.2%} exceeds threshold {thresholds.max_error_rate:.2%}")
        
        if self.consecutive_failures.get(name, 0) >= thresholds.max_consecutive_failures:
            issues.append(f"{self.consecutive_failures[name]} consecutive failures")
        
        # Determine status
        if issues:
            status = "degraded" if len(issues) < 3 else "unhealthy"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "latency": {
                "avg_ms": round(avg_latency, 2),
                "max_ms": round(max_latency, 2),
                "threshold_ms": round(thresholds.max_latency_ms, 2)
            },
            "error_rate": round(error_rate, 4),
            "consecutive_failures": self.consecutive_failures.get(name, 0),
            "thresholds": {
                "max_latency_ms": round(thresholds.max_latency_ms, 2),
                "max_error_rate": round(thresholds.max_error_rate, 4)
            },
            "samples": len(results),
            "issues": issues
        }

# Example usage
threshold_health = ThresholdBasedHealthCheck()

# Set thresholds for database
threshold_health.set_thresholds("database", HealthThresholds(
    max_latency_ms=50.0,
    max_error_rate=0.001
))

# Simulate health checks
import random

async def database_check_with_thresholds():
    latency = random.uniform(5, 80)
    success = random.random() > 0.01
    
    threshold_health.record_result("database", latency, success)
    
    return {
        **threshold_health.get_health_with_thresholds("database"),
        "latency_ms": round(latency, 2)
    }

@app.get("/health/thresholds")
async def threshold_health_check():
    db_health = await database_check_with_thresholds()
    
    return {
        "status": db_health["status"],
        "checks": {"database": db_health}
    }

# Example output for degraded database:
# {
#   "status": "degraded",
#   "checks": {
#     "database": {
#       "status": "degraded",
#       "latency": {"avg_ms": 35.2, "max_ms": 78.5, "threshold_ms": 50.0},
#       "error_rate": 0.005,
#       "consecutive_failures": 1,
#       "samples": 100,
#       "issues": [
#         "Max latency 78.5ms exceeds threshold 50.0ms"
#       ]
#     }
#   }
# }
```

### Pattern 26: Health Check with Dependency Health Scoring

Calculating an overall health score from multiple dependencies.

```python
# ✅ GOOD — Health check with dependency health scoring
from dataclasses import dataclass
from typing import Dict, Any, List, Callable, Awaitable
import time
import math

@dataclass
class HealthScoreConfig:
    max_score: float = 100.0
    weight_critical: float = 0.4
    weight_high: float = 0.3
    weight_medium: float = 0.2
    weight_low: float = 0.1
    latency_penalty_threshold_ms: float = 50.0
    latency_penalty_factor: float = 2.0

class HealthScoreCalculator:
    def __init__(self, config: HealthScoreConfig = None):
        self.config = config or HealthScoreConfig()
        self.dependency_scores: Dict[str, Dict[str, Any]] = {}
    
    def calculate_dependency_score(self, name: str, status: str, 
                                   latency_ms: float = 0) -> float:
        """Calculate score for a single dependency."""
        base_score = self.config.max_score
        
        if status == "healthy":
            # Apply latency penalty
            if latency_ms > self.config.latency_penalty_threshold_ms:
                penalty = (latency_ms - self.config.latency_penalty_threshold_ms) / 100
                base_score -= penalty * self.config.latency_penalty_factor
        elif status == "degraded":
            base_score *= 0.5  # 50% score for degraded
        else:  # unhealthy
            base_score = 0
        
        return max(0, base_score)
    
    def add_dependency(self, name: str, priority: str = "medium"):
        """Add a dependency for scoring."""
        self.dependency_scores[name] = {
            "priority": priority,
            "score": self.config.max_score,
            "last_update": 0
        }
    
    def update_dependency(self, name: str, status: str, latency_ms: float = 0):
        """Update dependency score."""
        if name not in self.dependency_scores:
            self.add_dependency(name)
        
        self.dependency_scores[name]["score"] = self.calculate_dependency_score(
            name, status, latency_ms
        )
        self.dependency_scores[name]["last_update"] = time.time()
    
    def calculate_overall_score(self) -> Dict[str, Any]:
        """Calculate overall health score from all dependencies."""
        if not self.dependency_scores:
            return {
                "score": self.config.max_score,
                "rating": "excellent",
                "dependencies": {}
            }
        
        weighted_score = 0
        total_weight = 0
        dependency_details = {}
        
        for name, info in self.dependency_scores.items():
            priority = info["priority"]
            
            # Get weight based on priority
            weight_map = {
                "critical": self.config.weight_critical,
                "high": self.config.weight_high,
                "medium": self.config.weight_medium,
                "low": self.config.weight_low
            }
            weight = weight_map.get(priority, self.config.weight_medium)
            
            weighted_score += info["score"] * weight
            total_weight += weight
            
            dependency_details[name] = {
                "score": round(info["score"], 2),
                "priority": priority,
                "status": "healthy" if info["score"] > 80 else ("degraded" if info["score"] > 50 else "unhealthy")
            }
        
        # Normalize score
        overall_score = weighted_score / total_weight if total_weight > 0 else self.config.max_score
        
        # Determine rating
        if overall_score >= 95:
            rating = "excellent"
        elif overall_score >= 85:
            rating = "good"
        elif overall_score >= 70:
            rating = "fair"
        elif overall_score >= 50:
            rating = "poor"
        else:
            rating = "critical"
        
        return {
            "score": round(overall_score, 2),
            "max_score": self.config.max_score,
            "rating": rating,
            "dependencies": dependency_details,
            "timestamp": time.time()
        }

# Example usage
health_scoring = HealthScoreCalculator()

# Add dependencies
health_scoring.add_dependency("database", priority="critical")
health_scoring.add_dependency("redis", priority="high")
health_scoring.add_dependency("cache", priority="medium")
health_scoring.add_dependency("metrics", priority="low")

# Simulate health checks
async def database_check():
    latency = 25  # ms
    status = "healthy"
    
    health_scoring.update_dependency("database", status, latency)
    return {"status": status, "latency_ms": latency}

async def redis_check():
    latency = 10  # ms
    status = "healthy"
    
    health_scoring.update_dependency("redis", status, latency)
    return {"status": status, "latency_ms": latency}

@app.get("/health/score")
async def health_score():
    """Health endpoint with scoring."""
    await database_check()
    await redis_check()
    
    return health_scoring.calculate_overall_score()

# Example output:
# {
#   "score": 98.5,
#   "max_score": 100,
#   "rating": "excellent",
#   "dependencies": {
#     "database": {"score": 100, "priority": "critical", "status": "healthy"},
#     "redis": {"score": 100, "priority": "high", "status": "healthy"},
#     "cache": {"score": 100, "priority": "medium", "status": "healthy"},
#     "metrics": {"score": 100, "priority": "low", "status": "healthy"}
#   }
# }
```

### Pattern 27: Health Check with Dependency Health Trends

Tracking health check trends over time for predictive monitoring.

```python
# ✅ GOOD — Health check with trend analysis
from dataclasses import dataclass
from typing import Dict, Any, List
import time
from collections import deque

@dataclass
class TrendConfig:
    window_seconds: int = 300  # 5 minutes
    trend_threshold: float = 0.1  # 10% change is significant

class TrendingHealthCheck:
    def __init__(self, config: TrendConfig = None):
        self.config = config or TrendConfig()
        self.health_history: Dict[str, deque] = {}
    
    def add_sample(self, name: str, latency_ms: float, success: bool):
        """Add a health check sample."""
        if name not in self.health_history:
            self.health_history[name] = deque(maxlen=1000)
        
        self.health_history[name].append({
            "timestamp": time.time(),
            "latency_ms": latency_ms,
            "success": success
        })
    
    def get_trend(self, name: str) -> Dict[str, Any]:
        """Calculate health trend for a dependency."""
        samples = self.health_history.get(name, [])
        
        if len(samples) < 2:
            return {
                "trend": "stable",
                "samples": len(samples),
                "change": 0
            }
        
        # Calculate average latency for first half vs second half
        mid = len(samples) // 2
        first_half = samples[:mid]
        second_half = samples[mid:]
        
        first_avg = sum(s["latency_ms"] for s in first_half) / len(first_half)
        second_avg = sum(s["latency_ms"] for s in second_half) / len(second_half)
        
        if first_avg > 0:
            change = (second_avg - first_avg) / first_avg
        else:
            change = 0
        
        # Determine trend
        if change > self.config.trend_threshold:
            trend = "increasing"
        elif change < -self.config.trend_threshold:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "change": round(change * 100, 2),  # percentage
            "first_half_avg_ms": round(first_avg, 2),
            "second_half_avg_ms": round(second_avg, 2),
            "samples": len(samples),
            "window_seconds": self.config.window_seconds
        }
    
    def get_health_with_trends(self, name: str, current_status: str) -> dict:
        """Get health status with trend analysis."""
        trend = self.get_trend(name)
        
        # Determine overall status
        if current_status == "healthy":
            if trend["trend"] == "increasing":
                overall_status = "degraded"
                warning = "Latency increasing - monitor closely"
            else:
                overall_status = "healthy"
                warning = None
        else:
            overall_status = current_status
            warning = None
        
        return {
            "status": overall_status,
            "warning": warning,
            "trend": trend,
            **self.get_trend(name)
        }

# Example usage
trending_health = TrendingHealthCheck()

async def database_check_with_trends():
    latency = 25  # Simulated latency
    
    # Record sample
    trending_health.add_sample("database", latency, True)
    
    return {
        "status": "healthy",
        "latency_ms": latency,
        "trend_analysis": trending_health.get_health_with_trends("database", "healthy")
    }

@app.get("/health/trends")
async def health_with_trends():
    return await database_check_with_trends()

# Example output:
# {
#   "status": "healthy",
#   "trend": {
#     "trend": "stable",
#     "change": 2.5,
#     "first_half_avg_ms": 22.3,
#     "second_half_avg_ms": 23.1,
#     "samples": 100,
#     "window_seconds": 300
#   }
# }
```

### Pattern 28: Health Check with Dependency Health History

Maintaining health check history for debugging and analysis.

```python
# ✅ GOOD — Health check with history tracking
from dataclasses import dataclass
from typing import Dict, Any, List
import time
from collections import deque
from datetime import datetime, timedelta

@dataclass
class HistoryConfig:
    max_history_items: int = 1000
    retention_seconds: int = 3600  # 1 hour

class HealthHistoryTracker:
    def __init__(self, config: HistoryConfig = None):
        self.config = config or HistoryConfig()
        self.check_history: Dict[str, deque] = {}
        self.failure_history: Dict[str, deque] = {}
    
    def record_check(self, name: str, status: str, latency_ms: float = 0, 
                    error: str = None):
        """Record a health check result."""
        if name not in self.check_history:
            self.check_history[name] = deque(maxlen=self.config.max_history_items)
        
        self.check_history[name].append({
            "timestamp": time.time(),
            "status": status,
            "latency_ms": latency_ms,
            "error": error,
            "datetime": datetime.utcnow().isoformat()
        })
        
        # Track failures separately
        if status == "unhealthy":
            if name not in self.failure_history:
                self.failure_history[name] = deque(maxlen=100)
            
            self.failure_history[name].append({
                "timestamp": time.time(),
                "error": error,
                "datetime": datetime.utcnow().isoformat()
            })
    
    def get_history(self, name: str, minutes: int = 5) -> List[Dict[str, Any]]:
        """Get recent health check history."""
        if name not in self.check_history:
            return []
        
        cutoff = time.time() - (minutes * 60)
        history = []
        
        for item in self.check_history[name]:
            if item["timestamp"] >= cutoff:
                history.append(item)
        
        return history
    
    def get_failure_history(self, name: str, minutes: int = 5) -> List[Dict[str, Any]]:
        """Get failure history for a dependency."""
        if name not in self.failure_history:
            return []
        
        cutoff = time.time() - (minutes * 60)
        history = []
        
        for item in self.failure_history[name]:
            if item["timestamp"] >= cutoff:
                history.append(item)
        
        return history
    
    def get_health_with_history(self, name: str, current_status: str) -> dict:
        """Get health status with history context."""
        recent_history = self.get_history(name, minutes=5)
        failure_history = self.get_failure_history(name, minutes=5)
        
        # Calculate statistics
        if recent_history:
            latencies = [h["latency_ms"] for h in recent_history if h["latency_ms"] > 0]
            avg_latency = sum(latencies) / len(latencies) if latencies else 0
            max_latency = max(latencies) if latencies else 0
        else:
            avg_latency = 0
            max_latency = 0
        
        return {
            "status": current_status,
            "history": {
                "total_checks": len(recent_history),
                "failure_count": len(failure_history),
                "latency": {
                    "avg_ms": round(avg_latency, 2),
                    "max_ms": round(max_latency, 2)
                },
                "recent": recent_history[-10:]  # Last 10 checks
            },
            "timestamp": time.time()
        }

# Example usage
history_tracker = HealthHistoryTracker()

async def database_check_with_history():
    latency = 25
    
    # Simulate occasional failures
    import random
    if random.random() > 0.95:
        status = "unhealthy"
        error = "Connection timeout"
    else:
        status = "healthy"
        error = None
    
    history_tracker.record_check("database", status, latency, error)
    
    return {
        "status": status,
        "latency_ms": latency,
        "history": history_tracker.get_health_with_history("database", status)
    }

@app.get("/health/history")
async def health_with_history():
    return await database_check_with_history()

# Example output:
# {
#   "status": "healthy",
#   "history": {
#     "total_checks": 50,
#     "failure_count": 2,
#     "latency": {"avg_ms": 23.5, "max_ms": 45.2},
#     "recent": [
#       {"timestamp": 1234567890.123, "status": "healthy", "latency_ms": 25, ...},
#       ...
#     ]
#   }
# }
```

### Pattern 29: Health Check with Dependency Health Aggregation

Aggregating health checks for complex dependency graphs.

```python
# ✅ GOOD — Health check with dependency aggregation
from dataclasses import dataclass
from typing import Dict, Any, List, Set
import time
from enum import Enum

class AggregateType(Enum):
    AND = "and"  # All must be healthy
    OR = "or"    # At least one must be healthy
    MAJORITY = "majority"  # More than half must be healthy

@dataclass
class AggregateConfig:
    aggregate_type: AggregateType = AggregateType.AND
    required_count: int = 1  # For OR, MAJORITY
    weight_map: Dict[str, float] = None  # Weight for weighted average

class HealthAggregator:
    def __init__(self, config: AggregateConfig = None):
        self.config = config or AggregateConfig()
        self.dependencies: Dict[str, Dict[str, Any]] = {}
    
    def add_dependency(self, name: str, dependencies: List[str] = None):
        """Add a dependency that may have sub-dependencies."""
        self.dependencies[name] = {
            "dependencies": dependencies or [],
            "last_check": None,
            "last_status": None
        }
    
    def get_dependency_status(self, name: str) -> str:
        """Get status for a dependency, aggregating sub-dependencies."""
        if name not in self.dependencies:
            return "unknown"
        
        deps = self.dependencies[name]["dependencies"]
        
        if not deps:
            # Leaf dependency - return stored status
            return self.dependencies[name].get("last_status", "unknown")
        
        # Aggregate sub-dependencies
        sub_statuses = [
            self.get_dependency_status(dep) for dep in deps
        ]
        
        return self.aggregate_statuses(sub_statuses)
    
    def aggregate_statuses(self, statuses: List[str]) -> str:
        """Aggregate multiple statuses based on config."""
        healthy_count = sum(1 for s in statuses if s == "healthy")
        total_count = len(statuses)
        
        if total_count == 0:
            return "unknown"
        
        if self.config.aggregate_type == AggregateType.AND:
            return "healthy" if all(s == "healthy" for s in statuses) else "unhealthy"
        
        elif self.config.aggregate_type == AggregateType.OR:
            return "healthy" if any(s == "healthy" for s in statuses) else "unhealthy"
        
        elif self.config.aggregate_type == AggregateType.MAJORITY:
            return "healthy" if healthy_count > total_count / 2 else "unhealthy"
        
        return "unknown"
    
    def update_dependency(self, name: str, status: str):
        """Update dependency status."""
        if name in self.dependencies:
            self.dependencies[name]["last_status"] = status
            self.dependencies[name]["last_check"] = time.time()
    
    def get_aggregated_health(self) -> dict:
        """Get overall health from aggregated dependencies."""
        overall_status = "healthy"
        dependency_details = {}
        
        for name, info in self.dependencies.items():
            status = self.get_dependency_status(name)
            dependency_details[name] = {
                "status": status,
                "depends_on": info["dependencies"],
                "last_check": info["last_check"]
            }
            
            if status != "healthy":
                overall_status = "degraded" if overall_status != "unhealthy" else "unhealthy"
        
        return {
            "status": overall_status,
            "dependencies": dependency_details,
            "aggregation": {
                "type": self.config.aggregate_type.value,
                "total_dependencies": len(self.dependencies)
            },
            "timestamp": time.time()
        }

# Example: API service with multiple database shards
aggregator = HealthAggregator(AggregateConfig(
    aggregate_type=AggregateType.MAJORITY
))

# Register dependencies
aggregator.add_dependency("shard_1", dependencies=["database_1"])
aggregator.add_dependency("shard_2", dependencies=["database_2"])
aggregator.add_dependency("shard_3", dependencies=["database_3"])
aggregator.add_dependency("api_service", dependencies=["shard_1", "shard_2", "shard_3"])

@app.get("/health/aggregated")
async def aggregated_health():
    """Health endpoint with dependency aggregation."""
    # Simulate some shards being unhealthy
    aggregator.update_dependency("database_1", "healthy")
    aggregator.update_dependency("database_2", "healthy")
    aggregator.update_dependency("database_3", "unhealthy")  # One shard down
    
    return aggregator.get_aggregated_health()

# Example output:
# {
#   "status": "degraded",
#   "dependencies": {
#     "shard_1": {"status": "healthy", "depends_on": ["database_1"], ...},
#     "shard_2": {"status": "healthy", "depends_on": ["database_2"], ...},
#     "shard_3": {"status": "unhealthy", "depends_on": ["database_3"], ...},
#     "api_service": {"status": "degraded", "depends_on": ["shard_1", "shard_2", "shard_3"], ...}
#   },
#   "aggregation": {
#     "type": "majority",
#     "total_dependencies": 4
#   }
# }
```

### Pattern 30: Health Check with Dependency Health Threshold Busting

Detecting and alerting on threshold breaches.

```python
# ✅ GOOD — Health check with threshold breach detection
from dataclasses import dataclass
from typing import Dict, Any, List
import time

@dataclass
class Threshold:
    name: str
    warning: float
    critical: float
    type: str = "latency"  # latency, error_rate, etc.

class ThresholdBreachDetector:
    def __init__(self):
        self.thresholds: Dict[str, List[Threshold]] = {}
        self.breaches: Dict[str, List[Dict[str, Any]]] = {}
    
    def add_threshold(self, name: str, threshold: Threshold):
        """Add a threshold for a health check."""
        if name not in self.thresholds:
            self.thresholds[name] = []
        self.thresholds[name].append(threshold)
        
        if name not in self.breaches:
            self.breaches[name] = []
    
    def check_threshold(self, name: str, value: float) -> Dict[str, Any]:
        """Check if value breaches any thresholds."""
        breaches = []
        
        if name not in self.thresholds:
            return {"breached": False, "breaches": []}
        
        for threshold in self.thresholds[name]:
            breached = False
            breach_level = None
            
            if threshold.type == "latency":
                if value >= threshold.critical:
                    breached = True
                    breach_level = "critical"
                elif value >= threshold.warning:
                    breached = True
                    breach_level = "warning"
            
            elif threshold.type == "error_rate":
                if value >= threshold.critical:
                    breached = True
                    breach_level = "critical"
                elif value >= threshold.warning:
                    breached = True
                    breach_level = "warning"
            
            if breached:
                breaches.append({
                    "threshold": threshold.name,
                    "breach_level": breach_level,
                    "value": value,
                    "threshold_value": threshold.critical if breach_level == "critical" else threshold.warning
                })
        
        if breaches:
            self.breaches[name].append({
                "timestamp": time.time(),
                "value": value,
                "breaches": breaches
            })
        
        return {"breached": len(breaches) > 0, "breaches": breaches}
    
    def get_breach_history(self, name: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get breach history for a dependency."""
        if name not in self.breaches:
            return []
        
        cutoff = time.time() - (hours * 3600)
        return [b for b in self.breaches[name] if b["timestamp"] >= cutoff]

# Example thresholds
breach_detector = ThresholdBreachDetector()
breach_detector.add_threshold("database", Threshold("database_latency", warning=50, critical=100, type="latency"))
breach_detector.add_threshold("database", Threshold("database_error_rate", warning=0.01, critical=0.05, type="error_rate"))
breach_detector.add_threshold("redis", Threshold("redis_latency", warning=10, critical=30, type="latency"))

async def database_check_with_breaches():
    latency = 75  # Simulated latency (between warning and critical)
    
    breach_result = breach_detector.check_threshold("database", latency)
    
    return {
        "status": "healthy",
        "latency_ms": latency,
        "breach_check": breach_result
    }

@app.get("/health/breaches")
async def health_with_breaches():
    return await database_check_with_breaches()

# Example output:
# {
#   "status": "healthy",
#   "latency_ms": 75,
#   "breach_check": {
#     "breached": true,
#     "breaches": [
#       {
#         "threshold": "database_latency",
#         "breach_level": "warning",
#         "value": 75,
#         "threshold_value": 50
#       }
#     ]
#   }
# }
```

### Pattern 31: Health Check with Dependency Health Escalation

Implementing escalation based on health status.

```python
# ✅ GOOD — Health check with escalation logic
from dataclasses import dataclass
from typing import Dict, Any, List
import time
from enum import Enum

class EscalationLevel(Enum):
    NONE = "none"
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class EscalationConfig:
    info_threshold: float = 0.95  # 95% healthy
    warning_threshold: float = 0.80  # 80% healthy
    critical_threshold: float = 0.50  # 50% healthy
    critical_delay_seconds: int = 60  # Delay before escalating to critical

class EscalationManager:
    def __init__(self, config: EscalationConfig = None):
        self.config = config or EscalationConfig()
        self.escalation_state: Dict[str, Dict[str, Any]] = {}
        self.first_warning_time: Dict[str, float] = {}
    
    def calculate_health_percentage(self, health_status: str, 
                                   total_checks: int,
                                   healthy_checks: int) -> float:
        """Calculate health percentage."""
        if total_checks == 0:
            return 100.0
        return (healthy_checks / total_checks) * 100
    
    def determine_escalation_level(self, name: str, health_percentage: float) -> EscalationLevel:
        """Determine escalation level based on health."""
        if health_percentage >= self.config.info_threshold:
            return EscalationLevel.NONE
        elif health_percentage >= self.config.warning_threshold:
            return EscalationLevel.WARNING
        elif health_percentage >= self.config.critical_threshold:
            # Check if we should escalate to critical
            if name not in self.first_warning_time:
                self.first_warning_time[name] = time.time()
            
            elapsed = time.time() - self.first_warning_time[name]
            
            if elapsed >= self.config.critical_delay_seconds:
                return EscalationLevel.CRITICAL
            
            return EscalationLevel.WARNING
        else:
            return EscalationLevel.CRITICAL
    
    def get_escalation_info(self, name: str, health_percentage: float) -> Dict[str, Any]:
        """Get escalation information."""
        level = self.determine_escalation_level(name, health_percentage)
        
        info = {
            "level": level.value,
            "percentage": round(health_percentage, 2),
            "message": self._get_escalation_message(level, health_percentage)
        }
        
        if level in [EscalationLevel.WARNING, EscalationLevel.CRITICAL]:
            info["first_warning_time"] = self.first_warning_time.get(name)
            
            if name in self.first_warning_time:
                elapsed = time.time() - self.first_warning_time[name]
                info["warning_duration_seconds"] = round(elapsed, 2)
        
        return info
    
    def _get_escalation_message(self, level: EscalationLevel, percentage: float) -> str:
        """Get escalation message."""
        messages = {
            EscalationLevel.NONE: f"System healthy ({percentage:.1f}%)",
            EscalationLevel.INFO: f"System healthy ({percentage:.1f}%)",
            EscalationLevel.WARNING: f"System degraded ({percentage:.1f}% healthy) - monitor closely",
            EscalationLevel.CRITICAL: f"System critical ({percentage:.1f}% healthy) - immediate action required"
        }
        return messages.get(level, "Unknown status")

# Example escalation manager
escalation = EscalationManager(
    EscalationConfig(critical_delay_seconds=120)  # 2 minute delay to critical
)

@app.get("/health/escalation")
async def health_with_escalation():
    """Health endpoint with escalation."""
    # Simulate checks
    total_checks = 4
    healthy_checks = 3  # 75% healthy
    
    health_percentage = escalation.calculate_health_percentage(
        "degraded", total_checks, healthy_checks
    )
    
    escalation_info = escalation.get_escalation_info("main_service", health_percentage)
    
    return {
        "status": "degraded",
        "checks": {
            "total": total_checks,
            "healthy": healthy_checks,
            "unhealthy": total_checks - healthy_checks
        },
        "escalation": escalation_info
    }

# Example output:
# {
#   "status": "degraded",
#   "checks": {"total": 4, "healthy": 3, "unhealthy": 1},
#   "escalation": {
#     "level": "warning",
#     "percentage": 75.0,
#     "message": "System degraded (75.0% healthy) - monitor closely",
#     "first_warning_time": 1234567890.123,
#     "warning_duration_seconds": 45.5
#   }
# }
```

### Pattern 32: Health Check with Dependency Health Retries

Implementing intelligent retry logic for health checks.

```python
# ✅ GOOD — Health check with intelligent retries
from dataclasses import dataclass
from typing import Dict, Any, Callable, Awaitable
import asyncio
import time
import random
from enum import Enum

class RetryStrategy(Enum):
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    RANDOM = "random"

@dataclass
class RetryConfig:
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 10.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL

class RetryableHealthCheck:
    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
        self.retry_state: Dict[str, Dict[str, Any]] = {}
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay based on retry strategy."""
        if attempt >= self.config.max_retries:
            return 0
        
        if self.config.strategy == RetryStrategy.FIXED:
            return self.config.base_delay
        
        elif self.config.strategy == RetryStrategy.LINEAR:
            return min(self.config.base_delay * (attempt + 1), self.config.max_delay)
        
        elif self.config.strategy == RetryStrategy.EXPONENTIAL:
            return min(self.config.base_delay * (2 ** attempt), self.config.max_delay)
        
        elif self.config.strategy == RetryStrategy.RANDOM:
            base = self.config.base_delay * (2 ** attempt)
            return min(base * random.uniform(0.5, 1.5), self.config.max_delay)
        
        return self.config.base_delay
    
    async def execute_with_retry(self, name: str, check_func: Callable[[], Awaitable[Dict[str, Any]]]) -> Dict[str, Any]:
        """Execute health check with retry logic."""
        if name not in self.retry_state:
            self.retry_state[name] = {"success": False, "last_failure": None}
        
        last_error = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                result = await check_func()
                
                # Success - reset state
                self.retry_state[name] = {"success": True, "last_failure": None}
                
                return result
            
            except Exception as e:
                last_error = e
                
                if attempt < self.config.max_retries:
                    delay = self.calculate_delay(attempt)
                    jitter = random.uniform(0, delay * 0.1)
                    await asyncio.sleep(delay + jitter)
        
        # All retries failed
        self.retry_state[name]["success"] = False
        self.retry_state[name]["last_failure"] = time.time()
        
        raise last_error
    
    def get_retry_info(self, name: str) -> Dict[str, Any]:
        """Get retry information for a health check."""
        state = self.retry_state.get(name, {"success": False, "last_failure": None})
        
        info = {
            "success": state.get("success", False),
            "last_failure": state.get("last_failure")
        }
        
        if state.get("last_failure"):
            info["seconds_since_last_failure"] = round(
                time.time() - state["last_failure"], 2
            )
        
        return info

# Example usage
retry_health = RetryableHealthCheck(
    RetryConfig(
        max_retries=3,
        base_delay=0.5,
        strategy=RetryStrategy.EXPONENTIAL
    )
)

async def database_check():
    """Simulated database check that might fail."""
    import random
    if random.random() > 0.3:  # 70% success rate
        return {"status": "healthy", "latency_ms": random.uniform(10, 50)}
    raise Exception("Database connection failed")

@app.get("/health/retry")
async def health_with_retry():
    """Health endpoint with retry logic."""
    try:
        result = await retry_health.execute_with_retry("database", database_check)
        
        return {
            "status": result["status"],
            "latency_ms": result["latency_ms"],
            "retry_info": retry_health.get_retry_info("database")
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "retry_info": retry_health.get_retry_info("database")
        }

# Example output on success:
# {
#   "status": "healthy",
#   "latency_ms": 25.5,
#   "retry_info": {
#     "success": true,
#     "last_failure": null
#   }
# }

# Example output after failures:
# {
#   "status": "unhealthy",
#   "error": "Database connection failed",
#   "retry_info": {
#     "success": false,
#     "last_failure": 1234567890.123,
#     "seconds_since_last_failure": 45.5
#   }
# }
```

---

## Constraints

### MUST DO

- Implement separate liveness and readiness probes with distinct purposes
- Configure probe timeouts longer than expected response times (include slow dependencies)
- Use exec-based liveness probes when possible to avoid HTTP overhead
- Return HTTP 503 for readiness probe failures, HTTP 200 for liveness probe failures
- Include database and external service dependency checks in readiness probes
- Set appropriate initialDelaySeconds for slow-starting applications using startup probes
- Log health check failures with context for debugging
- Implement circuit breaker patterns for external service dependencies
- Test health checks in staging environment matching production configuration
- Configure alerting on health check failure counts with appropriate thresholds
- Add retry logic for transient failures with exponential backoff
- Implement graceful degradation for non-critical dependencies
- Track health check trends over time for predictive monitoring
- Use structured JSON responses with dependency health details
- Export health check metrics to Prometheus for monitoring

### MUST NOT DO

- Use external dependencies (database, cache, APIs) in liveness probes — only for readiness
- Set probe timeouts too short — they may fail during normal network latency
- Disable health checks in production — they're critical for reliability
- Use generic health check paths like `/health` without versioning or structured response
- Ignore probe failure logs — they indicate real issues needing attention
- Use the same endpoint for liveness and readiness without clear separation
- Set failureThreshold too low — may cause unnecessary restarts during transient issues
- Forget to configure startup probes for applications with slow initialization
- Hardcode database passwords in health check code
- Use blocking I/O in health check endpoints — use async/await
- Return different status codes for liveness vs readiness failures
- Forget to test health checks in the target environment before deployment
- Ignore circuit breaker state in health check response
- Not implement health check history tracking for debugging

---

## Output Template

When implementing health check patterns, your output must contain:

1. **Probe Configuration** — Complete Kubernetes probe YAML with all parameters (liveness, readiness, startup)

2. **Health Endpoint Implementation** — Full HTTP endpoint code with dependency checks and structured response

3. **Dependency Health Check Functions** — Individual functions for each dependency (database, cache, external services)

4. **Circuit Breaker Configuration** — Circuit breaker implementation with threshold settings

5. **Testing Scripts** — Health check test scripts for CI/CD and manual validation

6. **Debugging Commands** — kubectl commands for troubleshooting health check issues

7. **Metrics Export** — Prometheus metrics for health check monitoring

8. **Retry Logic** — Exponential backoff retry implementation

9. **Graceful Degradation** — Non-critical dependency handling

10. **Circuit Breaker States** — Visualization of circuit breaker states in health response

---

## Related Skills

| Skill | Purpose |
|---|---|
| `cncf-kubernetes-debugging` | General Kubernetes debugging patterns and troubleshooting techniques |
| `agent-docker-debugging` | Docker container debugging including health check verification |
| `coding-fastapi-patterns` | FastAPI-specific health check patterns and response formatting |
| `cncf-prometheus` | Monitoring and alerting based on health check metrics |
| `trading-risk-kill-switches` | Emergency shutdown patterns for trading systems |
| `cncf-service-mesh` | Service mesh health check integration (Istio, Linkerd) |

---

## References

- [Kubernetes Probes Documentation](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#container-probes)
- [Kubernetes Best Practices: Pod Disruption](https://cloud.google.com/blog/products/containers-kubernetes/kubernetes-best-practices-pod-disruption)
- [Circuit Breaker Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)
- [Health Check Response Format](https://tools.ietf.org/html/draft-inadarei-api-health-check-05)
- [Kubernetes Signal Handling](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/)
- [CNCF Health Check Guidelines](https://github.com/cncf/tag-app-delivery/blob/main/health-checks/health-checks-overview.md)
- [OpenTelemetry Health Checks](https://opentelemetry.io/docs/instrumentation/python/automatic/)
- [FastAPI Health Checks](https://fastapi.tiangolo.com/advanced/health-checks/)

---

*This skill provides comprehensive health check patterns for cloud-native applications. All code examples follow Python typing conventions and include proper error handling.*


```bash
# ❌ BAD — basic pod status without health check details
kubectl get pods

# ✅ GOOD — comprehensive health check debugging commands

# 1. Check pod status and events
kubectl get pods -o wide
kubectl describe pod <pod-name>

# 2. Get detailed probe configuration
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[0].livenessProbe}' && echo
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[0].readinessProbe}' && echo

# 3. Check container logs for health check failures
kubectl logs <pod-name> --tail=100

# 4. Execute inside container to test health endpoint
kubectl exec -it <pod-name> -- curl -v http://localhost:8080/health

# 5. Check if probe endpoint is accessible from inside pod
kubectl exec <pod-name> -- wget -q -O- http://localhost:8080/health/live

# 6. Monitor pod restarts (indicates liveness probe failures)
kubectl get pods -w

# 7. Check resource constraints affecting probe timing
kubectl top pods

# 8. Validate probe configuration in deployment
kubectl get deployment <deployment-name> -o yaml | grep -A 10 "livenessProbe"

# 9. Check service mesh integration (for Istio/Linkerd)
kubectl exec <pod-name> -- curl -v http://localhost:15000/ready

# 10. View all events in namespace
kubectl get events --sort-by=.metadata.creationTimestamp

# Health Check Troubleshooting Script
#!/bin/bash
# debug-health-checks.sh

POD_NAME=$1

if [ -z "$POD_NAME" ]; then
    echo "Usage: $0 <pod-name>"
    exit 1
fi

echo "=== Health Check Debug for $POD_NAME ==="

echo -e "\n1. Pod Status:"
kubectl get pod $POD_NAME -o wide

echo -e "\n2. Pod Events:"
kubectl describe pod $POD_NAME | grep -A 20 "Events:"

echo -e "\n3. Liveness Probe Config:"
kubectl get pod $POD_NAME -o jsonpath='{.spec.containers[0].livenessProbe}' | python3 -m json.tool

echo -e "\n4. Readiness Probe Config:"
kubectl get pod $POD_NAME -o jsonpath='{.spec.containers[0].readinessProbe}' | python3 -m json.tool

echo -e "\n5. Recent Logs:"
kubectl logs $POD_NAME --tail=50

echo -e "\n6. Test Health Endpoint:"
kubectl exec $POD_NAME -- curl -s http://localhost:8080/health/live
echo

echo -e "\n7. Container Resource Usage:"
kubectl top pod $POD_NAME
```

---

## Constraints

### MUST DO

- Implement separate liveness, readiness, and startup probes with distinct purposes
- Configure probe timeouts longer than expected response times (include slow dependencies)
- Use exec-based liveness probes when possible to avoid HTTP overhead
- Return HTTP 503 for readiness probe failures, HTTP 200 for liveness probe failures
- Include database and external service dependency checks in readiness probes
- Set appropriate initialDelaySeconds for slow-starting applications using startup probes
- Log health check failures with context for debugging
- Implement circuit breaker patterns for external service dependencies
- Test health checks in staging environment matching production configuration
- Configure alerting on health check failure counts with appropriate thresholds

### MUST NOT DO

- Use external dependencies (database, cache, APIs) in liveness probes — only for readiness
- Set probe timeouts too short — they may fail during normal network latency
- Disable health checks in production — they're critical for reliability
- Use generic health check paths like `/health` without versioning or structured response
- Ignore probe failure logs — they indicate real issues needing attention
- Use the same endpoint for liveness and readiness without clear separation
- Set failureThreshold too low — may cause unnecessary restarts during transient issues
- Forget to configure startup probes for applications with slow initialization

---

## Output Template

When implementing health check patterns, your output must contain:

1. **Probe Configuration** — Complete Kubernetes probe YAML with all parameters (liveness, readiness, startup)

2. **Health Endpoint Implementation** — Full HTTP endpoint code with dependency checks and structured response

3. **Dependency Health Check Functions** — Individual functions for each dependency (database, cache, external services)

4. **Circuit Breaker Configuration** — Circuit breaker implementation with threshold settings

5. **Testing Scripts** — Health check test scripts for CI/CD and manual validation

6. **Debugging Commands** — kubectl commands for troubleshooting health check issues

---

## Related Skills

| Skill | Purpose |
|---|---|
| `cncf-kubernetes-debugging` | General Kubernetes debugging patterns and troubleshooting techniques |
| `agent-docker-debugging` | Docker container debugging including health check verification |
| `coding-fastapi-patterns` | FastAPI-specific health check patterns and response formatting |
| `cncf-prometheus` | Monitoring and alerting based on health check metrics |
| `trading-risk-kill-switches` | Emergency shutdown patterns for trading systems |

---

## References

- [Kubernetes Probes Documentation](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#container-probes)
- [Kubernetes Best Practices: Pod Disruption](https://cloud.google.com/blog/products/containers-kubernetes/kubernetes-best-practices-pod-disruption)
- [Circuit Breaker Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)
- [Health Check Response Format](https://tools.ietf.org/html/draft-inadarei-api-health-check-05)
- [Kubernetes Signal Handling](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/)
- [CNCF Health Check Guidelines](https://github.com/cncf/tag-app-delivery/blob/main/health-checks/health-checks-overview.md)

---

*This skill provides comprehensive health check patterns for cloud-native applications. All code examples follow Python typing conventions and include proper error handling.*
