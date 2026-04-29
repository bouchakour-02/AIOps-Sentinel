from fastapi import FastAPI, Header, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import time
import logging
import os
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

# Import ML models
from aggregator import initialize_models, detect_log_anomaly, detect_metric_anomaly, full_system_analysis

# Import observability stack (optional)
from elasticsearch_client import get_es_client
from prometheus_client import get_prom_client

# Try to import OTEL (optional)
try:
    from observability import init_observability, get_observability_manager
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    class DummyObservabilityManager:
        def trace_operation(self, name, attrs):
            from contextlib import contextmanager
            @contextmanager
            def dummy():
                yield None
            return dummy()
        def record_ml_prediction(self, **kwargs):
            pass
        def record_request(self, **kwargs):
            pass
        def create_trace_id(self):
            return str(uuid.uuid4())
    def get_observability_manager():
        return DummyObservabilityManager()
    def init_observability(name):
        return DummyObservabilityManager()

# Initialize FastAPI
app = FastAPI(title="AIOps Sentinel", version="2.0")

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize ML models
logger.info("Loading ML models...")
initialize_models()

# Initialize observability
logger.info("Initializing observability stack...")
obs_manager = init_observability("aiops-sentinel")

# Get clients
def _resolve_observability_url(
    env_var: str,
    localhost_url: str,
    vm_url: str,
    health_path: str
) -> str:
    """Pick observability endpoint URL from env or first healthy candidate."""
    explicit = os.getenv(env_var)
    candidates = [explicit] if explicit else [localhost_url, vm_url]

    for candidate in candidates:
        if not candidate:
            continue
        try:
            r = requests.get(f"{candidate}{health_path}", timeout=2)
            if r.status_code == 200:
                logger.info(f"{env_var} resolved to {candidate}")
                return candidate
        except Exception:
            continue

    fallback = explicit or localhost_url
    logger.warning(f"{env_var} using fallback {fallback}")
    return fallback


ES_URL = _resolve_observability_url(
    env_var="ELASTICSEARCH_URL",
    localhost_url="http://localhost:9200",
    vm_url=f"http://{os.getenv('OBS_VM_HOST', '192.168.159.136')}:9200",
    health_path="/_cluster/health"
)
PROM_URL = _resolve_observability_url(
    env_var="PROMETHEUS_URL",
    localhost_url="http://localhost:9090",
    vm_url=f"http://{os.getenv('OBS_VM_HOST', '192.168.159.136')}:9090",
    health_path="/-/healthy"
)

es_client = get_es_client(ES_URL)
prom_client = get_prom_client(PROM_URL)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for correlation IDs
@app.middleware("http")
async def add_trace_id(request, call_next):
    """Add trace ID to all requests"""
    trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())
    request.state.trace_id = trace_id
    
    response = await call_next(request)
    response.headers["X-Trace-ID"] = trace_id
    return response

@app.get("/")
def home():
    return {"status": "Backend Active"}

@app.get("/logs")
def get_logs():
    """Récupère les logs stockés dans Elasticsearch"""
    try:
        if not es_client.is_available():
            return {"error": "Elasticsearch unavailable", "logs": []}
        return get_api_logs()
    except Exception as e:
        return {"error": str(e), "logs": []}


def _extract_message(source: Dict[str, Any]) -> str:
    """Extract log message from different ES/OTel document shapes."""
    body = source.get("Body")
    if isinstance(body, str) and body:
        return body
    if isinstance(body, dict):
        return body.get("stringValue") or body.get("text") or ""

    msg = source.get("message")
    if isinstance(msg, str) and msg:
        return msg
    if isinstance(msg, dict):
        return msg.get("stringValue") or msg.get("text") or ""

    body_l = source.get("body")
    if isinstance(body_l, str) and body_l:
        return body_l
    if isinstance(body_l, dict):
        return body_l.get("stringValue") or body_l.get("text") or ""

    return ""


def _extract_service(source: Dict[str, Any]) -> str:
    """Extract service name from OTel/resource-style fields."""
    service = source.get("service")
    if isinstance(service, str) and service:
        return service
    if isinstance(service, dict):
        name = service.get("name")
        if isinstance(name, str) and name:
            return name

    resource = source.get("Resource") or source.get("resource")
    if isinstance(resource, dict):
        svc = resource.get("service")
        if isinstance(svc, dict):
            name = svc.get("name")
            if isinstance(name, str) and name:
                return name

    attrs = source.get("attributes")
    if isinstance(attrs, list):
        for attr in attrs:
            if attr.get("key") == "service.name":
                value = attr.get("value", {})
                return value.get("stringValue", "unknown")

    return "unknown"


def _extract_timestamp(source: Dict[str, Any]) -> Optional[str]:
    return (
        source.get("@timestamp")
        or source.get("timestamp")
        or source.get("Timestamp")
        or source.get("time")
    )

@app.get("/api/logs")
def get_api_logs():
    """Logs endpoint for the dashboard frontend — includes severity extraction."""
    try:
        if not es_client.is_available():
            return {"error": "Elasticsearch unavailable", "logs": []}

        response = requests.post(
            f"{es_client.es_url}/vermeg-logs/_search",
            json={
                "query": {"match_all": {}},
                "sort": [{"@timestamp": {"order": "desc"}}],
                "size": 50
            },
            timeout=5,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        payload = response.json()
        logs = []
        for hit in payload.get("hits", {}).get("hits", []):
            source = hit.get("_source", {})
            message = _extract_message(source)
            # Extract severity from the message content
            msg_upper = message.upper()
            if 'CRITICAL' in msg_upper or 'FATAL' in msg_upper:
                severity = 'critical'
            elif 'ERROR' in msg_upper or 'EXCEPTION' in msg_upper:
                severity = 'error'
            elif 'WARN' in msg_upper:
                severity = 'warning'
            else:
                severity = 'info'
            logs.append({
                "timestamp": _extract_timestamp(source),
                "message": message,
                "service": _extract_service(source),
                "severity": severity,
                "severity_text": source.get('SeverityText') or source.get("severityText") or severity.upper(),
            })
        total = payload.get("hits", {}).get("total", {}).get("value", len(logs))
        return {"total": total, "logs": logs}
    except Exception as e:
        return {"error": str(e), "logs": []}

# --- 2. RÉCUPÉRATION DU CPU (PROMETHEUS) ---
@app.get("/api/metrics/cpu")
def get_cpu_usage():
    try:
        if not prom_client.is_available():
            return {"metric": "cpu_usage", "value": 0, "unit": "%", "status": "prometheus_unavailable"}

        # Try common Prometheus/OTel metric shapes
        cpu_queries = [
            ("100 - (avg(rate(node_cpu_seconds_total{mode='idle'}[5m])) * 100)", 1.0),
            ("100 * (1 - avg(rate(system_cpu_time_seconds_total{state='idle'}[1m])))", 1.0),
            ("100 * avg(system_cpu_utilization)", 1.0),
            ("100 * (1 - avg(rate(system_cpu_time{state='idle'}[1m])))", 1.0),
        ]

        for query, multiplier in cpu_queries:
            results = prom_client.query(query)
            if results and results[0].get("value") is not None:
                cpu_value = float(results[0]["value"]) * multiplier
                return {"metric": "cpu_usage", "value": round(cpu_value, 2), "unit": "%"}

        return {"metric": "cpu_usage", "value": 0, "unit": "%", "status": "no_data"}
    except Exception as e:
        return {"metric": "cpu_usage", "value": 0, "unit": "%", "error": str(e)}


# ============================================================================
# PYDANTIC MODELS FOR REQUEST VALIDATION
# ============================================================================
class LogPredictionRequest(BaseModel):
    message: str

class MetricPredictionRequest(BaseModel):
    cpu: float = None
    memory: float = None
    db_errors: float = None

class SystemAnalysisRequest(BaseModel):
    log_message: str
    cpu: float = None
    memory: float = None
    db_errors: float = None

# ============================================================================
# ML PREDICTION ENDPOINTS
# ============================================================================

@app.post("/api/predict/log-anomaly")
def predict_log_anomaly(request: LogPredictionRequest):
    """Detect anomaly in a single log message using TF-IDF + baseline"""
    return detect_log_anomaly(request.message)

@app.post("/api/predict/metric-anomaly")
def predict_metric_anomaly(request: MetricPredictionRequest):
    """Detect anomalies in system metrics (CPU, memory, DB errors) using Isolation Forest"""
    return detect_metric_anomaly(
        cpu=request.cpu,
        memory=request.memory,
        db_errors=request.db_errors
    )

@app.post("/api/predict/system-analysis")
def system_analysis(request: SystemAnalysisRequest):
    """Full system health analysis combining logs + metrics"""
    return full_system_analysis(
        log_message=request.log_message,
        cpu=request.cpu,
        memory=request.memory,
        db_errors=request.db_errors
    )

@app.get("/api/models/status")
def models_status():
    """Check if all ML models are loaded"""
    try:
        from aggregator import load_model
        models = ["expert_scaler", "expert_if_watchdog", "tfidf_vectorizer", 
                  "tfidf_baseline_matrix", "tfidf_threshold"]
        status = {}
        for model in models:
            try:
                load_model(model)
                status[model] = "[OK] Loaded"
            except:
                status[model] = "[ERROR] Missing"
        return {"models": status}
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# ELASTICSEARCH ENDPOINTS - REAL LOGS
# ============================================================================

@app.get("/api/logs/recent")
def get_recent_logs(limit: int = 100, minutes: int = 60):
    """Get recent logs from Elasticsearch"""
    if not es_client.is_available():
        return {"error": "Elasticsearch unavailable", "logs": []}
    
    logs = es_client.get_recent_logs(limit=limit, minutes=minutes)
    
    with obs_manager.trace_operation("get_recent_logs", {
        "count": len(logs),
        "minutes": minutes
    }) as span:
        pass
    
    return {
        "count": len(logs),
        "logs": logs,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/logs/errors")
def get_error_logs(minutes: int = 60, limit: int = 50):
    """Get error and critical logs"""
    if not es_client.is_available():
        return {"error": "Elasticsearch unavailable", "logs": []}
    
    logs = es_client.get_error_logs(minutes=minutes, limit=limit)
    return {
        "count": len(logs),
        "logs": logs,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/logs/search")
def search_logs(query: str, minutes: int = 60, limit: int = 50):
    """Search logs"""
    if not es_client.is_available():
        return {"error": "Elasticsearch unavailable", "results": []}
    
    results = es_client.search_logs(
        query,
        filters={"minutes": minutes},
        limit=limit
    )
    return {
        "count": len(results),
        "results": results,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/logs/stats")
def get_log_stats(minutes: int = 60):
    """Get log statistics"""
    if not es_client.is_available():
        return {"error": "Elasticsearch unavailable"}
    
    stats = es_client.get_log_stats(minutes=minutes)
    return stats


@app.post("/api/logs/batch-predict")
def batch_predict_logs(limit: int = 50):
    """Batch predict anomalies on recent logs"""
    if not es_client.is_available():
        return {"error": "Elasticsearch unavailable", "predictions": []}
    
    logs = es_client.get_recent_logs(limit=limit)
    predictions = []
    
    for log in logs:
        pred = detect_log_anomaly(log["message"])
        predictions.append({
            "log_id": log["id"],
            "message": log["message"],
            "anomaly": pred["anomaly"],
            "score": pred.get("similarity_score"),
            "timestamp": log["timestamp"]
        })
    
    obs_manager.record_ml_prediction(
        model_name="tfidf_batch",
        anomaly_detected=any(p["anomaly"] for p in predictions),
        confidence=sum(p["score"] for p in predictions if p["score"]) / len(predictions) if predictions else 0,
        latency_ms=0
    )
    
    return {
        "count": len(predictions),
        "anomalies": sum(1 for p in predictions if p["anomaly"]),
        "predictions": predictions
    }


# ============================================================================
# PROMETHEUS ENDPOINTS - REAL METRICS
# ============================================================================

@app.get("/api/metrics/current")
def get_current_metrics():
    """Get current system metrics"""
    if not prom_client.is_available():
        return {"error": "Prometheus unavailable"}
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu_percent": prom_client.get_current_cpu_percent(),
        "memory_percent": prom_client.get_current_memory_percent(),
        "error_rate": prom_client.get_error_rate(),
        "request_latency_p95": prom_client.get_request_latency(0.95)
    }


@app.get("/api/metrics/history")
def get_metrics_history(minutes: int = 60, step: str = "1m"):
    """Get historical metrics"""
    if not prom_client.is_available():
        return {"error": "Prometheus unavailable"}
    
    from datetime import timedelta
    start_time = datetime.utcnow() - timedelta(minutes=minutes)
    
    cpu_data = prom_client.query_range(
        "rate(node_cpu_seconds_total{mode='user'}[1m])",
        start_time=start_time,
        step=step
    )
    
    memory_data = prom_client.query_range(
        "node_memory_MemAvailable_bytes",
        start_time=start_time,
        step=step
    )
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "period_minutes": minutes,
        "cpu": cpu_data,
        "memory": memory_data
    }


@app.get("/api/metrics/services")
def get_service_metrics(service: str):
    """Get metrics for specific service"""
    if not prom_client.is_available():
        return {"error": "Prometheus unavailable"}
    
    return prom_client.get_service_metrics(service)


@app.post("/api/metrics/query")
def query_prometheus(promql: str):
    """Execute custom PromQL query"""
    if not prom_client.is_available():
        return {"error": "Prometheus unavailable"}
    
    results = prom_client.query(promql)
    return {
        "query": promql,
        "results": results,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/metrics/targets")
def get_prometheus_targets():
    """Get Prometheus scrape targets"""
    if not prom_client.is_available():
        return {"error": "Prometheus unavailable"}
    
    return prom_client.get_targets()


# ============================================================================
# OBSERVABILITY & TRACING ENDPOINTS
# ============================================================================

@app.get("/api/health")
def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "elasticsearch": es_client.is_available(),
        "prometheus": prom_client.is_available(),
        "ml_models": True
    }


@app.get("/api/observability/status")
def observability_status():
    """Get observability stack status"""
    return {
        "elasticsearch": {
            "available": es_client.is_available(),
            "logs": es_client.get_log_stats() if es_client.is_available() else {}
        },
        "prometheus": {
            "available": prom_client.is_available(),
            "targets": prom_client.get_targets() if prom_client.is_available() else {}
        },
        "tracing": {
            "available": True,
            "service_name": "aiops-sentinel"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# COMPLETE SYSTEM ANALYSIS WITH REAL DATA
# ============================================================================

@app.get("/api/analysis/system")
def complete_system_analysis():
    """Full system analysis combining ML + real logs + real metrics"""
    
    analysis = {
        "timestamp": datetime.utcnow().isoformat(),
        "logs": {},
        "metrics": {},
        "predictions": {}
    }
    
    # Get real logs
    if es_client.is_available():
        logs = es_client.get_recent_logs(limit=10)
        analysis["logs"] = {
            "count": len(logs),
            "errors": sum(1 for l in logs if "error" in l["message"].lower()),
            "samples": logs[:3]
        }
    
    # Get real metrics
    if prom_client.is_available():
        metrics = {
            "cpu": prom_client.get_current_cpu_percent(),
            "memory": prom_client.get_current_memory_percent(),
            "errors": prom_client.get_error_rate()
        }
        analysis["metrics"] = metrics
    
    # Run ML prediction
    log_msg = logs[0]["message"] if logs else "system running"
    cpu = analysis["metrics"].get("cpu", 50) if analysis["metrics"] else 50
    memory = analysis["metrics"].get("memory", 50) if analysis["metrics"] else 50
    
    prediction = full_system_analysis(log_msg, cpu, memory, 10)
    analysis["predictions"] = prediction
    
    obs_manager.record_ml_prediction(
        model_name="system_analysis",
        anomaly_detected=prediction.get("anomaly_count", 0) > 0,
        confidence=0.85,
        latency_ms=100
    )
    
    return analysis


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
