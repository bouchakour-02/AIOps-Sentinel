#!/usr/bin/env python3
"""Quick test of models and endpoints"""

import sys
sys.path.insert(0, r'e:\Vermeg_AIOps_Debugger\backend_ingestion')

print("\n" + "="*70)
print("TEST 1: Loading Models")
print("="*70)

try:
    from aggregator import initialize_models, detect_log_anomaly, detect_metric_anomaly, full_system_analysis
    result = initialize_models()
    print(f"Models initialized: {result}")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("TEST 2: Log Anomaly Detection")
print("="*70)

test_logs = [
    ("INFO service running normally", False),
    ("ERROR database connection timeout critical", True),
    ("INFO request completed successfully", False),
]

for log_msg, expected_anomaly in test_logs:
    result = detect_log_anomaly(log_msg)
    anomaly = result.get("anomaly")
    score = result.get("similarity_score")
    status = "✓" if anomaly == expected_anomaly else "✗"
    print(f"{status} '{log_msg[:40]}...' | Anomaly: {anomaly} | Score: {score:.2f}")

print("\n" + "="*70)
print("TEST 3: Metric Anomaly Detection")
print("="*70)

test_metrics = [
    ({"cpu": 35, "memory": 45, "db_errors": 2}, False),
    ({"cpu": 98, "memory": 96, "db_errors": 127}, True),
    ({"cpu": 50, "memory": 60, "db_errors": 5}, False),
]

for metrics, expected_anomaly in test_metrics:
    result = detect_metric_anomaly(**metrics)
    anomaly = result.get("anomaly")
    score = result.get("isolation_forest_score")
    status = "✓" if anomaly == expected_anomaly else "✗"
    print(f"{status} CPU={metrics['cpu']} Mem={metrics['memory']} DBErr={metrics['db_errors']} | Anomaly: {anomaly} | IF Score: {score:.2f}")

print("\n" + "="*70)
print("TEST 4: Full System Analysis")
print("="*70)

scenarios = [
    ({"log_message": "INFO service running", "cpu": 40, "memory": 50, "db_errors": 1}, "🟢 HEALTHY"),
    ({"log_message": "ERROR database timeout", "cpu": 92, "memory": 86, "db_errors": 45}, "🔴 CRITICAL"),
    ({"log_message": "ERROR connection issue", "cpu": 45, "memory": 55, "db_errors": 3}, "🟠 WARNING"),
]

for params, expected_risk in scenarios:
    result = full_system_analysis(**params)
    risk = result.get("risk_level")
    count = result.get("anomaly_count")
    status = "✓" if risk == expected_risk else "✗"
    print(f"{status} Risk: {risk} | Anomalies: {count}")

print("\n" + "="*70)
print("✅ ALL TESTS COMPLETED")
print("="*70 + "\n")
