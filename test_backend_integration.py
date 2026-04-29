#!/usr/bin/env python3
"""
Test complete backend integration without external dependencies
Tests: ML models, ES client, Prometheus client, API endpoints structure
"""

import sys
import json
sys.path.insert(0, 'backend_ingestion')

print("[TEST] Complete Backend Integration")
print("=" * 70)

# Test 1: ML Models
print("\n[1] Testing ML Models...")
try:
    from aggregator import initialize_models, detect_log_anomaly, detect_metric_anomaly
    initialize_models()
    
    # Test log anomaly
    result = detect_log_anomaly("ERROR database connection timeout")
    print(f"  [OK] Log anomaly detection: {result.get('anomaly')}")
    print(f"      Similarity: {result.get('similarity_score', 'N/A')}")
    
    # Test metric anomaly
    result = detect_metric_anomaly(85, 75, 100)
    print(f"  [OK] Metric anomaly detection: {result.get('anomaly')}")
    print(f"      Isolation Forest score: {result.get('if_score')}")
    
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 2: Elasticsearch Client
print("\n[2] Testing Elasticsearch Client...")
try:
    from elasticsearch_client import ElasticsearchClient
    es = ElasticsearchClient()
    print(f"  [OK] ES client instantiated")
    print(f"      Available: {es.is_available()}")
    
    # Try to get stats even if not available
    try:
        stats = es.get_log_stats()
        print(f"      Stats: {json.dumps(stats, indent=6)[:100]}...")
    except:
        print(f"      (Stats unavailable - ES not running on localhost:9200)")
    
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 3: Prometheus Client
print("\n[3] Testing Prometheus Client...")
try:
    from prometheus_client import PrometheusClient
    prom = PrometheusClient()
    print(f"  [OK] Prometheus client instantiated")
    print(f"      Available: {prom.is_available()}")
    
    # Try to get metrics even if not available
    try:
        cpu = prom.get_current_cpu_percent()
        print(f"      Current CPU: {cpu}%")
    except:
        print(f"      (Metrics unavailable - Prometheus not running on localhost:9090)")
    
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 4: FastAPI App Structure
print("\n[4] Testing FastAPI App Structure...")
try:
    from main import app, OTEL_AVAILABLE
    
    routes = [r.path for r in app.routes]
    print(f"  [OK] FastAPI app loaded")
    print(f"      OTEL Support: {OTEL_AVAILABLE}")
    print(f"      Routes: {len(routes)}")
    
    # Check for our new endpoints
    expected = [
        '/api/health',
        '/api/logs/recent',
        '/api/logs/errors',
        '/api/logs/search',
        '/api/logs/stats',
        '/api/logs/batch-predict',
        '/api/metrics/current',
        '/api/metrics/history',
        '/api/metrics/query',
        '/api/observability/status',
        '/api/analysis/system'
    ]
    
    found_count = 0
    for endpoint in expected:
        if any(endpoint in route for route in routes):
            print(f"      [OK] {endpoint}")
            found_count += 1
        else:
            print(f"      [?] {endpoint}")
    
    print(f"      Found: {found_count}/{len(expected)} expected endpoints")
    
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 5: Middleware
print("\n[5] Testing Middleware...")
try:
    from main import app
    middlewares = [m.__class__.__name__ for m in app.user_middleware]
    print(f"  [OK] {len(middlewares)} middleware installed")
    for m in middlewares:
        print(f"      - {m}")
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 6: Pydantic Models
print("\n[6] Testing Request Models...")
try:
    from main import LogPredictionRequest, MetricPredictionRequest, SystemAnalysisRequest
    
    # Test LogPredictionRequest
    log_req = LogPredictionRequest(message="Test error message")
    print(f"  [OK] LogPredictionRequest model: message={log_req.message}")
    
    # Test MetricPredictionRequest
    metric_req = MetricPredictionRequest(cpu=50, memory=60, db_errors=5)
    print(f"  [OK] MetricPredictionRequest model: cpu={metric_req.cpu}, memory={metric_req.memory}")
    
except Exception as e:
    print(f"  [ERROR] {e}")

print("\n" + "=" * 70)
print("[RESULT] Backend Integration Test Complete")
print("\nNext Steps:")
print("  1. Start backend: python backend_ingestion/main.py")
print("  2. Test endpoints: curl http://localhost:8000/api/health")
print("  3. VM integration: Run from K3s VM for full observability")
print("  4. Frontend: npm start in frontend/ directory")

