import re
import numpy as np
import joblib
from pathlib import Path

# ============================================================================
# MODEL LOADING
# ============================================================================
MODEL_DIR = Path(__file__).parent.parent / "ai_engine" / "models"

# Load models saved by the notebook
tfidf_vectorizer = joblib.load(MODEL_DIR / "tfidf_vectorizer.pkl")
best_model       = joblib.load(MODEL_DIR / "best_model.pkl")       # LogisticRegression
scaler           = joblib.load(MODEL_DIR / "scaler.pkl")           # StandardScaler for LR features
metric_features  = joblib.load(MODEL_DIR / "metric_features.pkl")  # list of metric feature names

# ── Startup verification ──────────────────────────────────────────────────────
try:
    _test_text_vec = tfidf_vectorizer.transform(['info health check passed']).toarray()
    _test_metric_vec = scaler.transform(np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]).reshape(1, -1))
    _test_combined = np.hstack([_test_metric_vec, _test_text_vec])
    _test_pred = best_model.predict(_test_combined)
    print(f"[STARTUP] Model verification: 'info health check passed' → pred={_test_pred[0]}")
    print("[OK] All models loaded and verified correctly")
except Exception as e:
    print(f"[WARNING] Startup verification failed: {e}")


# Backwards-compatible initializer for main.py imports
def initialize_models():
    """Models are loaded at module import; keep this for compatibility."""
    return True


# Convenience alias so main.py's load_model() check still works
def load_model(name: str):
    """Return the requested model object (raises if unknown key)."""
    _registry = {
        "tfidf_vectorizer": tfidf_vectorizer,
        "best_model":       best_model,
        "scaler":           scaler,
        "metric_features":  metric_features,
    }
    if name not in _registry:
        raise KeyError(f"Unknown model key: {name}")
    return _registry[name]


# ============================================================================
# LOG TEXT NORMALIZATION
# MUST match exactly what was used during TF-IDF training in the notebook
# ============================================================================
def _normalize_log(text: str) -> str:
    """
    Normalize log text before TF-IDF transform.
    Matches clean_log_text() used during training:
      lowercase → digits→NUM → hex IDs→ID → remove punctuation → collapse spaces
    """
    text = str(text).lower()
    text = re.sub(r'\b\d+\b', ' NUM ', text)        # digits → NUM
    text = re.sub(r'[a-f0-9]{8,}', ' ID ', text)    # hex UUIDs → ID
    text = re.sub(r'[^\w\s]', ' ', text)             # remove punctuation
    return re.sub(r'\s+', ' ', text).strip()


# ============================================================================
# LAYER 3 — RULE ENGINE
# Handles Disk and SSL scenarios — no ML needed
# ============================================================================
def _run_rules(disk_percent: float, cert_days_left: int) -> list:
    alerts = []
    if disk_percent >= 95:
        alerts.append({
            'severity': 'CRITICAL',
            'msg': f'Disk at {disk_percent}% — pod eviction imminent (DiskPressure)'
        })
    elif disk_percent >= 90:
        alerts.append({
            'severity': 'WARNING',
            'msg': f'Disk at {disk_percent}% — FreeDiskSpaceLow threshold crossed'
        })
    if cert_days_left <= 1:
        alerts.append({
            'severity': 'CRITICAL',
            'msg': f'SSL expires in {cert_days_left}d — TLS handshakes will fail'
        })
    elif cert_days_left <= 7:
        alerts.append({
            'severity': 'WARNING',
            'msg': f'SSL expires in {cert_days_left}d — schedule renewal now'
        })
    return alerts


# ============================================================================
# LOG ANOMALY DETECTION — TF-IDF + Logistic Regression
# ============================================================================
def detect_log_anomaly(log_message: str, cpu: float = 0.0, memory: float = 0.0, db_errors: float = 0.0) -> dict:
    """
    Detect anomaly in a log message using Logistic Regression on combined features.
    
    The model was trained on 507 features (7 metrics + 500 TF-IDF features).
    If metrics are 0 (e.g. standalone log testing), we neutralize the metric vector
    by setting it to 0s to prevent them from negatively skewing the prediction towards 'Normal'.
    """
    try:
        # A. Process Text
        log_norm   = _normalize_log(log_message)
        text_vec   = tfidf_vectorizer.transform([log_norm]).toarray()
        
        # B. Process Metrics
        # If all core metrics are precisely 0.0, we assume this is a standalone text test
        # Setting metric_vec to np.zeros((1, 7)) simulates "average" metrics because
        # StandardScaler was fit with mean=True.
        if cpu == 0.0 and memory == 0.0 and db_errors == 0.0:
            metric_vec = np.zeros((1, 7))
        else:
            metric_arr = np.array([cpu, memory, db_errors, 0.0, 0.0, 0.0, 0.0]).reshape(1, -1)
            metric_vec = scaler.transform(metric_arr)
        
        # C. Combine
        combined = np.hstack([metric_vec, text_vec])

        # D. Predict
        prediction = int(best_model.predict(combined)[0])
        is_anomaly = (prediction == 1)

        # Confidence score
        if hasattr(best_model, 'predict_proba'):
            proba      = best_model.predict_proba(combined)[0]
            confidence = float(proba[prediction])
        else:
            # decision_function fallback
            score      = float(best_model.decision_function(combined)[0])
            confidence = round(abs(score), 4)

        return {
            'anomaly':    bool(is_anomaly),
            'confidence': round(confidence, 4),
            'prediction': prediction,
            'message':    'Anomalous log detected' if is_anomaly else 'Normal log'
        }
    except Exception as e:
        return {'error': str(e), 'anomaly': None}


# ============================================================================
# METRIC ANOMALY DETECTION — rule-based thresholds (no IsolationForest)
# The notebook removed the IsolationForest; we use simple threshold rules.
# ============================================================================
def detect_metric_anomaly(cpu: float = 0, memory: float = 0,
                           db_errors: float = 0) -> dict:
    """
    Detect metric anomalies using threshold rules.
    cpu / memory in percent (0-100), db_errors as count.
    """
    try:
        alerts = []
        if cpu >= 90:
            alerts.append(f"CPU critical: {cpu}%")
        elif cpu >= 75:
            alerts.append(f"CPU high: {cpu}%")

        if memory >= 90:
            alerts.append(f"Memory critical: {memory}%")
        elif memory >= 80:
            alerts.append(f"Memory high: {memory}%")

        if db_errors >= 10:
            alerts.append(f"DB errors critical: {db_errors}")
        elif db_errors >= 5:
            alerts.append(f"DB errors elevated: {db_errors}")

        is_anomaly = len(alerts) > 0

        return {
            'anomaly':   bool(is_anomaly),
            'alerts':    alerts,
            'raw_scores': {'cpu': cpu, 'memory': memory, 'db_errors': db_errors},
            'message':   'Metric anomaly detected' if is_anomaly else 'Metrics normal'
        }
    except Exception as e:
        return {'error': str(e), 'anomaly': None}


# ============================================================================
# FULL PIPELINE — score_window (called by monitoring loop)
# ============================================================================
def score_window(metrics: dict, raw_log: str,
                 disk_percent: float = 0, cert_days_left: int = 365) -> dict:
    """
    Full 3-layer pipeline — called by the monitoring loop every 30 seconds.

    Parameters
    ----------
    metrics : dict with cpu, memory, db_errors (and optionally diff fields)
    raw_log : most recent log line from Elasticsearch
    disk_percent : current disk usage (0-100)
    cert_days_left : days until SSL certificate expires
    """
    # ── Layer 1: Metric thresholds ─────────────────────────────────────────
    cpu      = metrics.get('cpu_smoothed', metrics.get('cpu', 0))
    memory   = metrics.get('mem_smoothed', metrics.get('memory', 0))
    db_err   = metrics.get('db_smoothed',  metrics.get('db_errors', 0))
    metric_r = detect_metric_anomaly(cpu, memory, db_err)
    metric_anomaly = metric_r.get('anomaly', False)

    # ── Layer 2: TF-IDF + LR (log text anomaly) ───────────────────────────
    log_r      = detect_log_anomaly(raw_log, cpu=cpu, memory=memory, db_errors=db_err)
    tfidf_anom = log_r.get('anomaly', False)

    # Keyword guard — catches ERROR/FATAL/CRITICAL even if LR misses
    kw_anom = bool(re.search(
        r'\bERROR\b|\bFATAL\b|\bCRITICAL\b|OOMKill|EXHAUSTED',
        raw_log, re.IGNORECASE
    ))

    # ── Layer 3: Rule engine (disk + SSL) ─────────────────────────────────
    rule_alerts = _run_rules(disk_percent, cert_days_left)

    # ── Final decision: ANY layer triggers = anomaly ───────────────────────
    triggered = metric_anomaly or tfidf_anom or kw_anom or len(rule_alerts) > 0

    return {
        'triggered':       triggered,
        'metric_anomaly':  metric_anomaly,
        'metric_alerts':   metric_r.get('alerts', []),
        'tfidf_anomaly':   tfidf_anom,
        'log_confidence':  log_r.get('confidence', 0),
        'kw_anomaly':      kw_anom,
        'rule_alerts':     rule_alerts,
        'action':          'TRIGGER_LLM' if triggered else 'HEALTHY',
    }


# ============================================================================
# COMBINED ANALYSIS
# ============================================================================
def full_system_analysis(log_message: str, cpu: float = 0,
                          memory: float = 0, db_errors: float = 0) -> dict:
    """
    Combined analysis — for the /api/predict/system-analysis endpoint.
    Runs both log anomaly and metric anomaly and combines results.
    """
    log_result    = detect_log_anomaly(log_message, cpu=cpu, memory=memory, db_errors=db_errors)
    metric_result = detect_metric_anomaly(cpu, memory, db_errors)

    anomaly_count = sum([
        bool(log_result.get('anomaly', False)),
        bool(metric_result.get('anomaly', False))
    ])

    if anomaly_count >= 2:
        risk_level = 'CRITICAL'
    elif anomaly_count == 1:
        risk_level = 'WARNING'
    else:
        risk_level = 'HEALTHY'

    return {
        'risk_level':      risk_level,
        'log_analysis':    log_result,
        'metric_analysis': metric_result,
        'anomaly_count':   anomaly_count
    }


def batch_predict_logs(log_messages: list) -> list:
    """Score multiple log messages at once."""
    return [detect_log_anomaly(msg) for msg in log_messages]


def batch_predict_metrics(metrics_list: list) -> list:
    """Score multiple metric windows at once."""
    return [
        detect_metric_anomaly(
            cpu=m.get('cpu', 0),
            memory=m.get('memory', 0),
            db_errors=m.get('db_errors', 0)
        )
        for m in metrics_list
    ]
