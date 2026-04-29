#!/usr/bin/env python3
"""
Test script for ML model integration
Tests model loading, log anomaly detection, and metric anomaly detection
"""

import sys
sys.path.insert(0, ".")

from aggregator import (
    initialize_models,
    detect_log_anomaly,
    detect_metric_anomaly,
    full_system_analysis
)

def test_models_loading():
    """Test if all models load correctly"""
    print("\n" + "="*70)
    print("TEST 1: Model Loading")
    print("="*70)
    result = initialize_models()
    if result:
        print("✅ All models loaded successfully!")
    else:
        print("❌ Failed to load models")
    return result

def test_log_anomaly():
    """Test log anomaly detection"""
    print("\n" + "="*70)
    print("TEST 2: Log Anomaly Detection")
    print("="*70)
    
    test_logs = [
        "INFO service started successfully",
        "ERROR database connection failed timeout",
        "INFO request processed in 45ms",
        "CRITICAL system memory exhausted fatal error",
        "INFO health check passed all systems normal",
    ]
    
    for log in test_logs:
        result = detect_log_anomaly(log)
        status = "🔴 ANOMALY" if result.get("anomaly") else "🟢 NORMAL"
        score = result.get("similarity_score", "N/A")
        print(f"{status} | Score: {score:.4f} | {log[:50]}")
    
    return True

def test_metric_anomaly():
    """Test metric anomaly detection"""
    print("\n" + "="*70)
    print("TEST 3: Metric Anomaly Detection (CPU/Memory/DB Errors)")
    print("="*70)
    
    test_metrics = [
        {"cpu": 30, "memory": 45, "db_errors": 2, "label": "Normal metrics"},
        {"cpu": 95, "memory": 88, "db_errors": 50, "label": "High load"},
        {"cpu": 5, "memory": 10, "db_errors": 0, "label": "Low load"},
        {"cpu": 99, "memory": 99, "db_errors": 100, "label": "Critical state"},
    ]
    
    for metrics in test_metrics:
        label = metrics.pop("label")
        result = detect_metric_anomaly(**metrics)
        status = "🔴 ANOMALY" if result.get("anomaly") else "🟢 NORMAL"
        if_score = result.get("isolation_forest_score", "N/A")
        print(f"{status} | IF Score: {if_score:.4f} | {label} | {metrics}")
    
    return True

def test_full_analysis():
    """Test full system analysis"""
    print("\n" + "="*70)
    print("TEST 4: Full System Analysis (Logs + Metrics)")
    print("="*70)
    
    scenarios = [
        {
            "log": "INFO request completed successfully",
            "cpu": 40,
            "memory": 50,
            "db_errors": 1,
            "label": "Healthy system"
        },
        {
            "log": "ERROR database connection timeout critical",
            "cpu": 90,
            "memory": 85,
            "db_errors": 45,
            "label": "System under stress"
        },
    ]
    
    for scenario in scenarios:
        label = scenario.pop("label")
        log = scenario.pop("log")
        result = full_system_analysis(log, **scenario)
        risk = result.get("risk_level", "Unknown")
        print(f"\n{label}:")
        print(f"  Risk Level: {risk}")
        print(f"  Log Anomaly: {result.get('log_analysis', {}).get('anomaly')}")
        print(f"  Metric Anomaly: {result.get('metric_analysis', {}).get('anomaly')}")
    
    return True

if __name__ == "__main__":
    print("\n🚀 Starting ML Integration Tests...\n")
    
    try:
        test_models_loading()
        test_log_anomaly()
        test_metric_anomaly()
        test_full_analysis()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\n📡 Ready to use ML endpoints in FastAPI:")
        print("  POST /api/predict/log-anomaly")
        print("  POST /api/predict/metric-anomaly")
        print("  POST /api/predict/system-analysis")
        print("  GET  /api/models/status")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
