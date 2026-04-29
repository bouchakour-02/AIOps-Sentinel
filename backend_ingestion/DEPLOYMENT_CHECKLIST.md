# Deployment Checklist

## Pre-Deployment Verification

### ✅ Model Files
- [ ] `ai_engine/models/expert_scaler.pkl` exists
- [ ] `ai_engine/models/expert_if_watchdog.pkl` exists
- [ ] `ai_engine/models/tfidf_vectorizer.pkl` exists
- [ ] `ai_engine/models/tfidf_baseline_matrix.pkl` exists
- [ ] `ai_engine/models/tfidf_threshold.pkl` exists

Verify:
```bash
ls -la ai_engine/models/
```

### ✅ Code Files
- [ ] `backend_ingestion/aggregator.py` - ML module (220 lines)
- [ ] `backend_ingestion/main.py` - FastAPI app with endpoints (175 lines)
- [ ] `backend_ingestion/requirements.txt` - Dependencies updated
- [ ] `backend_ingestion/test_ml_integration.py` - Test suite

Verify:
```bash
cd backend_ingestion
wc -l *.py
```

### ✅ Dependencies
- [ ] scikit-learn installed
- [ ] joblib installed
- [ ] numpy installed
- [ ] pandas installed
- [ ] fastapi installed
- [ ] uvicorn installed

Install:
```bash
cd backend_ingestion
pip install -r requirements.txt
```

Verify:
```bash
pip list | grep -E "scikit|joblib|numpy|pandas|fastapi|uvicorn"
```

---

## Pre-Production Testing

### 1. Model Loading Test
```bash
cd backend_ingestion
python -c "from aggregator import initialize_models; initialize_models()"
```
Expected output:
```
✅ All ML models loaded successfully
```

### 2. Import Test
```bash
python -c "from aggregator import detect_log_anomaly, detect_metric_anomaly; print('✓ Imports OK')"
```

### 3. Full Test Suite
```bash
python test_ml_integration.py
```
Expected: All 4 tests pass ✅

### 4. FastAPI Startup
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Expected:
```
✅ All ML models loaded successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 5. API Endpoints Test
```bash
# In another terminal
curl http://localhost:8000/api/models/status
```
Expected: All models show ✅ Loaded

---

## Production Deployment Steps

### Step 1: Verify Environment
```bash
python --version  # Python 3.8+
pip --version
```

### Step 2: Install Dependencies
```bash
cd backend_ingestion
pip install --no-cache-dir -r requirements.txt
```

### Step 3: Run Pre-Deployment Tests
```bash
# Test 1: Models load
python test_ml_integration.py

# Test 2: Start server (5 seconds)
timeout 5 python -m uvicorn main:app --host 0.0.0.0 --port 8000 || true
```

### Step 4: Start the Server
```bash
# Development
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production (with workers)
python -m uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Step 5: Verify APIs Work
```bash
# Test models loaded
curl http://localhost:8000/api/models/status

# Test log prediction
curl -X POST http://localhost:8000/api/predict/log-anomaly \
  -H "Content-Type: application/json" \
  -d '{"message": "INFO service running"}'

# Test metric prediction
curl -X POST http://localhost:8000/api/predict/metric-anomaly \
  -H "Content-Type: application/json" \
  -d '{"cpu": 50, "memory": 50, "db_errors": 2}'
```

### Step 6: Check Health Endpoints
```bash
# Existing endpoints should still work
curl http://localhost:8000/
curl http://localhost:8000/api/logs
curl http://localhost:8000/api/logs/
curl http://localhost:8000/api/metrics/cpu
```

---

## System Requirements

### Minimum
- Python 3.8+
- 200MB disk space
- 100MB RAM

### Recommended
- Python 3.10+
- 500MB disk space
- 500MB+ RAM (for multiple workers)

---

## Configuration

### Model Path
Models must be in: `../ai_engine/models/`
(Relative to `backend_ingestion/aggregator.py`)

### API Port
Default: 8000
Change in `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)
```

### CORS Configuration
Currently allows all origins:
```python
allow_origins=["*"]
```
For production, restrict to specific domains.

---

## Monitoring & Health Checks

### Health Check Endpoint
```bash
curl http://localhost:8000/api/models/status
```

### Log Prediction Health
```bash
curl -X POST http://localhost:8000/api/predict/log-anomaly \
  -H "Content-Type: application/json" \
  -d '{"message": "INFO test"}'
```

### Metric Prediction Health
```bash
curl -X POST http://localhost:8000/api/predict/metric-anomaly \
  -H "Content-Type: application/json" \
  -d '{"cpu": 50, "memory": 50, "db_errors": 0}'
```

---

## Troubleshooting

### Issue: ModuleNotFoundError: sklearn
```bash
pip install scikit-learn
```

### Issue: Models not loading
```bash
# Check file exists
ls -la ai_engine/models/expert_scaler.pkl

# Check permission
chmod 644 ai_engine/models/*.pkl
```

### Issue: High latency on first request
**Normal** - Models load on first request (~1-2 seconds)
Subsequent requests are fast (~10-30ms)

### Issue: Port already in use
```bash
# Use different port
python -m uvicorn main:app --port 8001
```

### Issue: Memory usage high
Models take ~100MB in RAM
This is normal and expected

---

## Rollback Plan

If issues occur:

1. Stop the server
```bash
# Ctrl+C (if running foreground)
# or
pkill -f "uvicorn main:app"
```

2. Verify previous version working
```bash
git status
git log --oneline
```

3. Revert if needed
```bash
git checkout main
```

---

## Performance Baseline

After deployment, monitor these metrics:

| Metric | Target | Notes |
|--------|--------|-------|
| Model Load Time | <1s | One-time on startup |
| Log Prediction | 10-20ms | Per message |
| Metric Prediction | 5-10ms | Per sample |
| Full Analysis | 20-30ms | Combined |
| Memory Usage | ~100MB | Models in RAM |
| CPU (idle) | <1% | Between requests |

---

## Backup & Recovery

### Backup Models
```bash
tar -czf ai_engine_models_backup.tar.gz ai_engine/models/
```

### Restore Models
```bash
tar -xzf ai_engine_models_backup.tar.gz
```

### Code Version
Always tag releases:
```bash
git tag -a v1.0-ml-integration -m "ML models integrated"
git push origin v1.0-ml-integration
```

---

## Documentation References

1. **ML_INTEGRATION_GUIDE.md** - Full technical guide
2. **API_EXAMPLES.md** - API usage and examples
3. **IMPLEMENTATION_SUMMARY.md** - What was built
4. **This file** - Deployment steps

---

## Post-Deployment Checklist

- [ ] All 4 API endpoints responding
- [ ] Models status endpoint shows all ✅
- [ ] Log anomaly detection working
- [ ] Metric anomaly detection working
- [ ] Full system analysis working
- [ ] Performance baseline met
- [ ] No errors in logs
- [ ] CORS working if needed
- [ ] Database/Elasticsearch connections OK
- [ ] Monitoring/alerts configured

---

## Sign-Off

**Deployed by:** ________________  
**Date:** ________________  
**Version:** v1.0-ml-integration  
**Status:** ✅ Production Ready

---

## Support

For issues or questions:
1. Check **IMPLEMENTATION_SUMMARY.md** for overview
2. Check **ML_INTEGRATION_GUIDE.md** for details
3. Check **API_EXAMPLES.md** for usage
4. Review logs for errors
5. Run test suite to verify: `python test_ml_integration.py`
