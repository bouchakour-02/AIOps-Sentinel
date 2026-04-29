#!/usr/bin/env python3
"""
Quick ML Model Testing with Log Dataset
- Test TF-IDF log anomaly detection
- Test Isolation Forest metric anomaly detection
- Test system analysis
- Focus on ML pipeline only (ES/Prom optional)
"""

import requests
import json
import random

API_URL = "http://localhost:8000"

NORMAL_LOGS = [
    "INFO service running normally",
    "INFO database connection established",
    "INFO request processed successfully",
    "INFO cache hit",
    "INFO user authenticated",
]

ERROR_LOGS = [
    "ERROR database connection timeout",
    "ERROR out of memory exception",
    "ERROR authentication failed",
    "ERROR network unreachable",
    "ERROR disk space critical",
]

def test_scenario(name, logs, metrics_range):
    """Test a scenario with given logs and metrics"""
    print(f"\n{name}")
    print("=" * 60)

    for i, log_msg in enumerate(logs):
        cpu = random.uniform(metrics_range["cpu"][0], metrics_range["cpu"][1])
        memory = random.uniform(metrics_range["memory"][0], metrics_range["memory"][1])
        db_errors = random.randint(metrics_range["db_errors"][0], metrics_range["db_errors"][1])

        try:
            # Test system analysis (combines log + metric)
            r = requests.post(
                f"{API_URL}/api/predict/system-analysis",
                json={
                    "log_message": log_msg,
                    "cpu": cpu,
                    "memory": memory,
                    "db_errors": db_errors,
                },
                timeout=5
            )

            if r.status_code == 200:
                result = r.json()
                print(f"\n[{i+1}] Log: '{log_msg}'")
                print(f"    Metrics: CPU={cpu:.1f}%, MEM={memory:.1f}%, DB_ERRORS={db_errors}")
                print(f"    Log Anomaly: {result['log_analysis']['anomaly']}")
                print(f"    Metric Anomaly: {result['metric_analysis']['anomaly']}")
                print(f"    Risk Level: {result['risk_level']}")
                print(f"    Anomaly Count: {result['anomaly_count']}")
            else:
                print(f"[ERROR] HTTP {r.status_code}: {r.text}")
        except Exception as e:
            print(f"[ERROR] {e}")

def main():
    print("\n" + "=" * 70)
    print("ML MODEL TESTING WITH LOG DATASET")
    print("=" * 70)

    # Check backend
    try:
        r = requests.get(f"{API_URL}/api/models/status", timeout=2)
        models = r.json()["models"]
        print("\n[MODELS]")
        for model, status in models.items():
            print(f"  {model}: {status}")
    except Exception as e:
        print(f"[ERROR] Backend not available: {e}")
        return

    # Scenario 1: Normal operation
    test_scenario(
        "[SCENARIO 1] Normal Operation",
        NORMAL_LOGS,
        {
            "cpu": (20, 50),
            "memory": (30, 60),
            "db_errors": (0, 5),
        }
    )

    # Scenario 2: Warning conditions
    test_scenario(
        "[SCENARIO 2] Warning Conditions",
        NORMAL_LOGS[:2] + ERROR_LOGS[:1],
        {
            "cpu": (50, 80),
            "memory": (60, 85),
            "db_errors": (5, 20),
        }
    )

    # Scenario 3: Critical conditions
    test_scenario(
        "[SCENARIO 3] Critical Conditions",
        ERROR_LOGS,
        {
            "cpu": (85, 99),
            "memory": (85, 99),
            "db_errors": (100, 300),
        }
    )

    print("\n" + "=" * 70)
    print("[SUCCESS] ALL TESTS COMPLETED")
    print("=" * 70)
    print("\nNext: View results in UI at http://localhost:5173")
    print("      Click 'ML Testing' button to test interactively\n")


if __name__ == "__main__":
    main()
