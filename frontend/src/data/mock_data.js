// ============================================================
// AIOps Sentinel — Mock Data
// ============================================================

export const SERVICES = [
    { id: 'payment-api', name: 'Payment-API', team: 'Payments', language: 'Java' },
    { id: 'auth-service', name: 'Auth-Service', team: 'Identity', language: 'Go' },
    { id: 'order-service', name: 'Order-Service', team: 'Commerce', language: 'Node.js' },
    { id: 'notification-svc', name: 'Notification-Svc', team: 'Messaging', language: 'Python' },
    { id: 'api-gateway', name: 'API-Gateway', team: 'Platform', language: 'Nginx/Lua' },
];

// 20-point time series (last 20 minutes, 1-min intervals)
const now = Date.now();
export const METRICS_SERIES = Array.from({ length: 20 }, (_, i) => {
    const t = new Date(now - (19 - i) * 60_000);
    const label = t.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
    // Spike at index 14-16 to simulate the Payment-API incident
    const spike = i >= 14 && i <= 16;
    return {
        time: label,
        cpu: spike ? 80 + Math.round(Math.random() * 14) : 35 + Math.round(Math.random() * 20),
        memory: spike ? 72 + Math.round(Math.random() * 10) : 48 + Math.round(Math.random() * 15),
        errors: spike ? 18 + Math.round(Math.random() * 12) : Math.round(Math.random() * 4),
    };
});

export const INCIDENTS = [
    {
        id: 'INC-001',
        timestamp: new Date(now - 8 * 60_000).toISOString(),
        service: 'Payment-API',
        serviceId: 'payment-api',
        severity: 'critical',
        anomalyScore: 0.88,
        metric: 'CPU',
        metricValue: 94,
        metricUnit: '%',
        title: 'CPU Spike — OutOfMemoryError',
        logSnippet: 'java.lang.OutOfMemoryError: Java heap space\n  at com.vermeg.payment.processor.TransactionBatch.process(TransactionBatch.java:247)',
        aiDiagnosis:
            'Ministral-3B detected a heap exhaustion pattern correlated with a 340% surge in concurrent transaction batches. The JVM heap limit (2 GB) was breached after 14 minutes of sustained load. Root cause: unbounded `TransactionBatch` queue accumulation due to a missing back-pressure mechanism in the upstream API-Gateway routing rule.',
        recommendation: `# Immediate mitigation — increase heap & add GC flags
kubectl set env deployment/payment-api \\
  JAVA_OPTS="-Xms1g -Xmx4g -XX:+UseG1GC -XX:MaxGCPauseMillis=200" \\
  -n production

# Long-term fix — apply back-pressure config patch
kubectl patch configmap payment-api-config -n production --patch '
data:
  MAX_CONCURRENT_BATCHES: "50"
  QUEUE_OVERFLOW_STRATEGY: "DROP_OLDEST"
'`,
        metricSpike: METRICS_SERIES.slice(12),
    },
    {
        id: 'INC-002',
        timestamp: new Date(now - 22 * 60_000).toISOString(),
        service: 'Auth-Service',
        serviceId: 'auth-service',
        severity: 'warning',
        anomalyScore: 0.61,
        metric: 'Latency',
        metricValue: 1240,
        metricUnit: 'ms',
        title: 'P99 Latency Degradation',
        logSnippet: 'WARN  [auth-service] Token validation timeout after 1200ms — Redis connection pool exhausted (pool=32/32)',
        aiDiagnosis:
            'Elevated P99 latency traced to Redis connection pool saturation. 32/32 connections held by long-running token introspection calls. Likely caused by a downstream LDAP query taking >800ms per request.',
        recommendation: `# Scale Redis connection pool
kubectl patch deployment auth-service -n production \\
  --patch '{"spec":{"template":{"spec":{"containers":[{"name":"auth-service","env":[{"name":"REDIS_POOL_SIZE","value":"64"}]}]}}}}'`,
        metricSpike: METRICS_SERIES.slice(10).map(d => ({ ...d, cpu: d.cpu - 10, errors: d.errors + 5 })),
    },
    {
        id: 'INC-003',
        timestamp: new Date(now - 45 * 60_000).toISOString(),
        service: 'Order-Service',
        serviceId: 'order-service',
        severity: 'critical',
        anomalyScore: 0.79,
        metric: 'Error Rate',
        metricValue: 12.4,
        metricUnit: '%',
        title: 'Error Rate Spike — DB Deadlock',
        logSnippet: 'ERROR [order-service] Deadlock found when trying to get lock; try restarting transaction — query: UPDATE orders SET status=\'PROCESSING\'',
        aiDiagnosis:
            'Database deadlock cycle detected between `orders` and `inventory` tables. Two concurrent transactions acquiring locks in opposite order. Anomaly score 0.79 — high confidence. Pattern matches a known anti-pattern in distributed saga implementations.',
        recommendation: `# Restart affected pods immediately
kubectl rollout restart deployment/order-service -n production

# Apply index hint to break deadlock cycle
kubectl exec -it $(kubectl get pod -l app=order-service -o jsonpath='{.items[0].metadata.name}') \\
  -n production -- mysql -e "ALTER TABLE orders ADD INDEX idx_status_updated (status, updated_at);"`,
        metricSpike: METRICS_SERIES.slice(8).map(d => ({ ...d, errors: d.errors + 10 })),
    },
    {
        id: 'INC-004',
        timestamp: new Date(now - 90 * 60_000).toISOString(),
        service: 'Notification-Svc',
        serviceId: 'notification-svc',
        severity: 'warning',
        anomalyScore: 0.44,
        metric: 'Memory',
        metricValue: 78,
        metricUnit: '%',
        title: 'Memory Creep — Possible Leak',
        logSnippet: 'WARNING  [notification-svc] RSS memory grew from 312MB to 1.1GB over 90 minutes without GC relief',
        aiDiagnosis:
            'Gradual memory growth pattern consistent with an event listener leak. Each WebSocket reconnect registers a new listener without removing the previous one. Anomaly score 0.44 — medium confidence, monitor for escalation.',
        recommendation: `# Trigger rolling restart to reclaim memory
kubectl rollout restart deployment/notification-svc -n production

# Add memory limit to prevent OOM kill cascade
kubectl patch deployment notification-svc -n production \\
  --patch '{"spec":{"template":{"spec":{"containers":[{"name":"notification-svc","resources":{"limits":{"memory":"1.5Gi"}}}]}}}}'`,
        metricSpike: METRICS_SERIES.slice(5).map(d => ({ ...d, memory: d.memory + 15 })),
    },
    {
        id: 'INC-005',
        timestamp: new Date(now - 3 * 60 * 60_000).toISOString(),
        service: 'API-Gateway',
        serviceId: 'api-gateway',
        severity: 'info',
        anomalyScore: 0.22,
        metric: 'Throughput',
        metricValue: 8400,
        metricUnit: 'req/s',
        title: 'Throughput Anomaly — Traffic Surge',
        logSnippet: 'INFO  [api-gateway] Upstream throughput 8400 req/s — 2.1x above baseline (p95 baseline: 4000 req/s)',
        aiDiagnosis:
            'Unusual traffic surge detected — 2.1x above P95 baseline. Pattern does not match known DDoS signatures. Likely a legitimate marketing campaign or batch job. No downstream degradation observed. Anomaly score 0.22 — low severity.',
        recommendation: `# Pre-emptively scale gateway replicas
kubectl scale deployment api-gateway --replicas=6 -n production

# Enable rate limiting for non-authenticated routes
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: rate-limit-public
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api-gateway
EOF`,
        metricSpike: METRICS_SERIES.slice(0).map(d => ({ ...d, cpu: d.cpu + 5 })),
    },
];

export const SUMMARY_STATS = {
    globalHealth: 98.2,
    activeAnomalies: 3,
    mttd: '4m 32s',
    systemLoad: 67,
    trend: {
        anomalies: +1,
        mttd: -12,
        load: +4,
    },
};

export const CHAT_SEED = [
    {
        id: 1,
        role: 'assistant',
        text: 'Hello! I\'m the AIOps Sentinel AI. Ask me anything about your incidents, metrics, or services.',
        ts: new Date(now - 5 * 60_000).toISOString(),
    },
    {
        id: 2,
        role: 'user',
        text: 'What caused the Payment-API incident?',
        ts: new Date(now - 4 * 60_000).toISOString(),
    },
    {
        id: 3,
        role: 'assistant',
        text: 'The Payment-API incident (INC-001) was caused by JVM heap exhaustion. A 340% surge in concurrent transaction batches overwhelmed the 2 GB heap limit. The root cause is a missing back-pressure mechanism — the upstream API-Gateway is not throttling requests to Payment-API. I recommend applying the kubectl config patch shown in the analysis panel.',
        ts: new Date(now - 3 * 60_000).toISOString(),
    },
];
