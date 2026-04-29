import re
import numpy as np
import joblib
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

# ============================================================================
# MODEL LOADING
# ============================================================================
MODEL_DIR = Path(__file__).parent.parent / "ai_engine" / "models"

# Load all 4 models at module startup — once only
scaler                = joblib.load(MODEL_DIR / "expert_scaler.pkl")
isolation_forest      = joblib.load(MODEL_DIR / "expert_if_watchdog.pkl")
tfidf_vectorizer      = joblib.load(MODEL_DIR / "tfidf_vectorizer.pkl")
tfidf_baseline_matrix = joblib.load(MODEL_DIR / "tfidf_baseline_matrix.pkl")

# Calibrated threshold from notebook (BEST_TFIDF_THRESHOLD = 0.9455)
# DO NOT load from pkl — it was saved with wrong value 0.25 in some versions
TFIDF_THRESHOLD = 0.9455

# Feature names in exact training order — DO NOT CHANGE THIS ORDER
FEATURES = [
    'cpu_smoothed',
    'mem_smoothed',
    'db_smoothed',
    'error_smoothed',
    'cpu_diff',
    'mem_diff',
    'db_diff'
]

# ── Startup verification ──────────────────────────────────────────────────────
_test_vec = tfidf_vectorizer.transform(['info health check passed'])
_test_sim = float(cosine_similarity(_test_vec, tfidf_baseline_matrix).max())
print(f"[STARTUP] TF-IDF verification: 'info health check passed' → sim={_test_sim:.4f}")
if _test_sim < 0.5:
    print("[WARNING] TF-IDF models may be wrong — expected sim > 0.9 for normal log")
else:
    print("[OK] Models loaded and verified correctly")

# Backwards-compatible initializer for main.py imports
def initialize_models():
    """Models are loaded at module import; keep this for compatibility."""
    return True


# ============================================================================
# LOG TEXT NORMALIZATION
# MUST match exactly what was used during TF-IDF training in the notebook
# ============================================================================
def _normalize_log(text: str) -> str:
    """
    Normalize log text before TF-IDF transform.
    This MUST match the clean_log_text() function used during training.
    Steps: lowercase → digits to NUM → hex IDs to ID → remove punctuation → collapse spaces
    """
    text = str(text).lower()
    text = re.sub(r'\b\d+\b', ' NUM ', text)        # digits → NUM
    text = re.sub(r'[a-f0-9]{8,}', ' ID ', text)    # hex UUIDs → ID
    text = re.sub(r'[^\w\s]', ' ', text)             # remove punctuation
    return re.sub(r'\s+', ' ', text).strip()


# ============================================================================
# LAYER 3 — RULE ENGINE
# Handles Scenario 5 (Disk) and Scenario 6 (SSL) — no ML needed
# Thresholds from log-dataset.md:
#   Disk WARNING=90%  Disk CRITICAL=95%
#   SSL  WARNING=7d   SSL  CRITICAL=1d
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
# MAIN DETECTION FUNCTION
# ============================================================================
def detect_log_anomaly(log_message: str) -> dict:
    """
    TF-IDF layer only — for the /api/ml/log-anomaly endpoint.
    Normalizes the log text, computes max cosine similarity against
    the normal baseline, and compares to the calibrated threshold.

    similarity >= 0.9455 → normal (looks like training normal logs)
    similarity <  0.9455 → anomaly (unseen pattern)
    """
    try:
        log_norm   = _normalize_log(log_message)
        log_vector = tfidf_vectorizer.transform([log_norm])
        # Use .max() not .mean() — max finds the most similar normal log
        sim        = float(cosine_similarity(log_vector, tfidf_baseline_matrix).max())
        is_anomaly = sim < TFIDF_THRESHOLD

        return {
            'anomaly':          bool(is_anomaly),
            'similarity_score': round(sim, 4),
            'threshold':        TFIDF_THRESHOLD,
            'message':          'Anomalous log detected' if is_anomaly else 'Normal log'
        }
    except Exception as e:
        return {'error': str(e), 'anomaly': None}


def detect_metric_anomaly(cpu: float = 0, memory: float = 0,
                           db_errors: float = 0) -> dict:
    """
    Isolation Forest layer only — for the /api/ml/metric-anomaly endpoint.
    The scaler expects exactly 7 features in the FEATURES order.
    cpu_diff, mem_diff, db_diff are 0 for single-window calls (no history).
    """
    try:
        feature_vector = np.array([
            cpu, memory, db_errors, 0.0,   # cpu_smoothed, mem_smoothed, db_smoothed, error_smoothed
            0.0, 0.0, 0.0                   # cpu_diff, mem_diff, db_diff
        ]).reshape(1, -1)

        scaled     = scaler.transform(feature_vector)
        prediction = isolation_forest.predict(scaled)[0]       # -1=anomaly, 1=normal
        score      = float(isolation_forest.decision_function(scaled)[0])
        is_anomaly = (prediction == -1)

        return {
            'anomaly':                bool(is_anomaly),
            'isolation_forest_score': round(score, 4),
            'raw_scores':             {'cpu': cpu, 'memory': memory, 'db_errors': db_errors},
            'message':                'Metric anomaly detected' if is_anomaly else 'Metrics normal'
        }
    except Exception as e:
        return {'error': str(e), 'anomaly': None}


def score_window(metrics: dict, raw_log: str,
                 disk_percent: float, cert_days_left: int) -> dict:
    """
    Full 3-layer pipeline — called by the monitoring loop every 30 seconds.

    Parameters
    ----------
    metrics : dict with exactly the 7 FEATURES keys
    raw_log : most recent log line from Elasticsearch
    disk_percent : current disk usage (0-100)
    cert_days_left : days until SSL certificate expires

    Returns
    -------
    dict with triggered, layer breakdown, and action
    """
    # ── Layer 1: Isolation Forest (metric anomaly) ─────────────────────────
    feature_vector = np.array(
        [metrics[f] for f in FEATURES], dtype=float
    ).reshape(1, -1)

    scaled     = scaler.transform(feature_vector)
    if_score   = float(isolation_forest.decision_function(scaled)[0])
    if_anomaly = isolation_forest.predict(scaled)[0] == -1

    # ── Layer 2: TF-IDF (log text anomaly) ────────────────────────────────
    log_norm    = _normalize_log(raw_log)
    log_vector  = tfidf_vectorizer.transform([log_norm])
    sim         = float(cosine_similarity(log_vector, tfidf_baseline_matrix).max())
    tfidf_anom  = sim < TFIDF_THRESHOLD

    # Keyword guard — catches ERROR/FATAL/CRITICAL even if TF-IDF misses
    kw_anom = bool(re.search(
        r'\bERROR\b|\bFATAL\b|\bCRITICAL\b|OOMKill|EXHAUSTED',
        raw_log, re.IGNORECASE
    ))

    # ── Layer 3: Rule engine (disk + SSL) ─────────────────────────────────
    rule_alerts = _run_rules(disk_percent, cert_days_left)

    # ── Final decision: ANY layer triggers = anomaly ───────────────────────
    triggered = if_anomaly or tfidf_anom or kw_anom or len(rule_alerts) > 0

    return {
        'triggered':     triggered,
        'if_score':      round(if_score, 4),
        'if_anomaly':    if_anomaly,
        'tfidf_sim':     round(sim, 4),
        'tfidf_anomaly': tfidf_anom,
        'kw_anomaly':    kw_anom,
        'rule_alerts':   rule_alerts,
        'action':        'TRIGGER_LLM' if triggered else 'HEALTHY',
    }


def full_system_analysis(log_message: str, cpu: float = 0,
                          memory: float = 0, db_errors: float = 0) -> dict:
    """
    Combined analysis — for the /api/ml/full-analysis endpoint.
    Runs both TF-IDF and Isolation Forest separately and combines results.
    """
    log_result    = detect_log_anomaly(log_message)
    metric_result = detect_metric_anomaly(cpu, memory, db_errors)

    anomaly_count = sum([
        log_result.get('anomaly', False),
        metric_result.get('anomaly', False)
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
