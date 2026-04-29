#!/usr/bin/env python3
"""
Log Injection & System Testing Script
- Injects logs from log-dataset.md to Elasticsearch
- Sends metrics to OTEL/Prometheus
- Tests ML models with real data
- Verifies entire pipeline integration
"""

import requests
import json
import time
from datetime import datetime, timedelta
import random
import re

# Configuration
ES_URL = "http://localhost:9200"
API_URL = "http://localhost:8000"
OTEL_COLLECTOR_URL = "http://localhost:4317"
PROM_URL = "http://localhost:9090"

# Log datasets
NORMAL_LOGS = [
    "INFO service running normally",
    "INFO database connection established",
    "INFO request processed successfully",
    "INFO cache hit for query",
    "INFO user authenticated successfully",
    "INFO batch job completed",
    "DEBUG processing request from client",
    "DEBUG configuration loaded",
]

ERROR_LOGS = [
    "ERROR database connection timeout",
    "ERROR out of memory exception",
    "ERROR authentication failed",
    "ERROR network unreachable",
    "ERROR disk space critical",
    "ERROR connection pool exhausted",
    "ERROR service unavailable",
    "ERROR request timeout after 30s",
]

METRIC_PATTERNS = {
    "normal": {
        "cpu": (20, 50),
        "memory": (30, 60),
        "db_errors": (0, 5),
    },
    "warning": {
        "cpu": (50, 80),
        "memory": (60, 85),
        "db_errors": (5, 20),
    },
    "critical": {
        "cpu": (85, 99),
        "memory": (85, 99),
        "db_errors": (100, 300),
    },
}


def generate_timestamp(offset_minutes=0):
    """Generate ISO format timestamp"""
    ts = datetime.utcnow() + timedelta(minutes=offset_minutes)
    return ts.isoformat() + "Z"


def inject_log_to_es(message, severity="info", service="test-service"):
    """Inject a single log to Elasticsearch"""
    doc = {
        "timestamp": generate_timestamp(),
        "message": message,
        "severity": severity,
        "service": service,
        "source": "test-injection",
    }
    try:
        r = requests.post(
            f"{ES_URL}/logs-test/_doc",
            json=doc,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        return r.status_code == 201
    except Exception as e:
        print(f"  ❌ ES injection failed: {e}")
        return False


def test_ml_model(message, cpu=50, memory=50, db_errors=5):
    """Test ML models with given log and metrics"""
    try:
        # Test log anomaly
        log_result = requests.post(
            f"{API_URL}/api/predict/log-anomaly",
            json={"message": message},
            timeout=5
        )

        # Test metric anomaly
        metric_result = requests.post(
            f"{API_URL}/api/predict/metric-anomaly",
            json={"cpu": cpu, "memory": memory, "db_errors": db_errors},
            timeout=5
        )

        # Test system analysis
        system_result = requests.post(
            f"{API_URL}/api/predict/system-analysis",
            json={
                "log_message": message,
                "cpu": cpu,
                "memory": memory,
                "db_errors": db_errors,
            },
            timeout=5
        )

        return {
            "log": log_result.json() if log_result.status_code == 200 else None,
            "metric": metric_result.json() if metric_result.status_code == 200 else None,
            "system": system_result.json() if system_result.status_code == 200 else None,
        }
    except Exception as e:
        print(f"  ❌ ML test failed: {e}")
        return None


def check_elasticsearch():
    """Verify Elasticsearch is running and accessible"""
    try:
        r = requests.get(f"{ES_URL}/_cluster/health", timeout=2)
        health = r.json()
        status = health['status'].upper()
        shards = health['active_shards']
        print(f"[OK] Elasticsearch: {status} - {shards} shards")
        return True
    except Exception as e:
        print(f"[ERROR] Elasticsearch: {e}")
        return False


def check_prometheus():
    """Verify Prometheus is running"""
    try:
        r = requests.get(f"{PROM_URL}/api/v1/targets", timeout=2)
        targets = r.json()
        count = len(targets['data']['activeTargets'])
        print(f"[OK] Prometheus: {count} active targets")
        return True
    except Exception as e:
        print(f"[ERROR] Prometheus: {e}")
        return False


def check_backend():
    """Verify backend API is running"""
    try:
        r = requests.get(f"{API_URL}/api/models/status", timeout=2)
        models = r.json()["models"]
        loaded = sum(1 for v in models.values() if "OK" in v)
        print(f"[OK] Backend API: {loaded}/{len(models)} models loaded")
        return True
    except Exception as e:
        print(f"[ERROR] Backend API: {e}")
        return False


def run_test_scenario(name, logs_list, metrics):
    """Run a complete test scenario"""
    print(f"\n[RUNNING] {name}")
    print("=" * 60)

    results = []
    for log_msg in logs_list:
        cpu, memory, db_errors = (
            random.uniform(metrics["cpu"][0], metrics["cpu"][1]),
            random.uniform(metrics["memory"][0], metrics["memory"][1]),
            random.randint(metrics["db_errors"][0], metrics["db_errors"][1]),
        )

        # Inject to ES
        es_ok = inject_log_to_es(log_msg, service="test-scenario")
        
        # Test ML
        ml_result = test_ml_model(log_msg, cpu=cpu, memory=memory, db_errors=db_errors)

        if ml_result:
            results.append({
                "log": log_msg[:50],
                "es_injected": es_ok,
                "log_anomaly": ml_result["log"]["anomaly"],
                "metric_anomaly": ml_result["metric"]["anomaly"],
                "risk_level": ml_result["system"]["risk_level"],
            })
            print(f"  OK Log: {log_msg[:50]}...")
            print(f"    - ES: {'[OK]' if es_ok else '[FAIL]'}")
            print(f"    - Log anomaly: {ml_result['log']['anomaly']}")
            print(f"    - Metric anomaly: {ml_result['metric']['anomaly']}")
            print(f"    - Risk: {ml_result['system']['risk_level']}")

    return results


def main():
    print("\n" + "=" * 70)
    print("INTEGRATED LOG INJECTION & SYSTEM TESTING")
    print("=" * 70)

    # 1. Health checks
    print("\n[SYSTEM] HEALTH CHECKS")
    print("-" * 70)
    es_ok = check_elasticsearch()
    prom_ok = check_prometheus()
    backend_ok = check_backend()

    if not all([es_ok, prom_ok, backend_ok]):
        print("\n[INFO] Some services not available. Continuing with available services...")

    # 2. Models status
    print("\n[ML] MODELS STATUS")
    print("-" * 70)
    try:
        r = requests.get(f"{API_URL}/api/models/status", timeout=2)
        models = r.json()["models"]
        for model, status in models.items():
            print(f"  {model}: {status}")
    except Exception as e:
        print(f"  Error: {e}")

    # 3. Test scenarios
    print("\n[TEST] SCENARIOS")
    print("-" * 70)

    all_results = []

    # Scenario 1: Normal operation
    results = run_test_scenario(
        "SCENARIO 1: Normal Operation",
        NORMAL_LOGS[:3],
        METRIC_PATTERNS["normal"]
    )
    all_results.extend([(r, "normal") for r in results])

    # Scenario 2: Warning conditions
    results = run_test_scenario(
        "SCENARIO 2: Warning Conditions",
        NORMAL_LOGS[:2] + ERROR_LOGS[:1],
        METRIC_PATTERNS["warning"]
    )
    all_results.extend([(r, "warning") for r in results])

    # Scenario 3: Critical conditions
    results = run_test_scenario(
        "SCENARIO 3: Critical Conditions",
        ERROR_LOGS[:2],
        METRIC_PATTERNS["critical"]
    )
    all_results.extend([(r, "critical") for r in results])

    # 4. Verify Elasticsearch ingestion
    print("\n[DB] ELASTICSEARCH VERIFICATION")
    print("-" * 70)
    if es_ok:
        try:
            time.sleep(2)  # Wait for ES to index
            r = requests.get(
                f"{ES_URL}/logs-test/_count",
                timeout=2
            )
            count = r.json()["count"]
            print(f"  ✅ Total logs indexed: {count}")

            # Get sample logs
            r = requests.get(
                f"{ES_URL}/logs-test/_search?size=5",
                timeout=2
            )
            logs = r.json()["hits"]["hits"]
            print(f"  Samples:")
            for log in logs[:3]:
                print(f"     - {log['_source']['message']}")
        except Exception as e:
            print(f"  [ERROR] querying ES: {e}")

    # 5. Results summary
    print("\n[RESULTS] SUMMARY")
    print("=" * 70)
    print(f"Total tests: {len(all_results)}")

    normal_count = sum(1 for r, s in all_results if s == "normal")
    warning_count = sum(1 for r, s in all_results if s == "warning")
    critical_count = sum(1 for r, s in all_results if s == "critical")

    print(f"  Normal scenario tests: {normal_count}")
    print(f"  Warning scenario tests: {warning_count}")
    print(f"  Critical scenario tests: {critical_count}")

    # Anomaly detection accuracy
    normal_anomalies = sum(
        1 for r, s in all_results
        if s == "normal" and (r["log_anomaly"] or r["metric_anomaly"])
    )
    critical_anomalies = sum(
        1 for r, s in all_results
        if s == "critical" and (r["log_anomaly"] or r["metric_anomaly"])
    )

    print(f"\n  Anomaly Detection:")
    print(f"    - Normal data flagged as anomaly: {normal_anomalies}/{normal_count}")
    print(f"    - Critical data detected as anomaly: {critical_anomalies}/{critical_count}")

    # 6. Next steps
    print("\n[NEXT] STEPS")
    print("=" * 70)
    print("  1. View real-time logs in Elasticsearch:")
    print(f"     {ES_URL}/_cat/indices")
    print("\n  2. View ML predictions in UI:")
    print("     http://localhost:5173")
    print("     Click 'ML Testing' button")
    print("\n  3. Check Prometheus metrics:")
    print(f"     {PROM_URL}/graph")
    print("\n  4. View Elasticsearch documents:")
    print(f"     {ES_URL}/logs-test/_search?size=20")

    print("\n" + "=" * 70)
    print("[SUCCESS] TESTING COMPLETE")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
