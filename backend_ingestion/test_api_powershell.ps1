# PowerShell Testing Script for ML Integration API

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "ML Integration API Testing (PowerShell)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$BASE_URL = "http://localhost:8000"

# Test 1: Check Model Status
Write-Host "TEST 1: Checking Model Status" -ForegroundColor Yellow
Write-Host "==============================" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BASE_URL/api/models/status" -Method Get -ContentType "application/json"
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Models:" -ForegroundColor Green
    $content.models | ForEach-Object {
        $_.PSObject.Properties | ForEach-Object {
            Write-Host "  $($_.Name): $($_.Value)" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
}

Write-Host ""

# Test 2: Log Anomaly Detection - Normal Log
Write-Host "TEST 2: Log Anomaly Detection (Normal Log)" -ForegroundColor Yellow
Write-Host "===========================================" -ForegroundColor Yellow
try {
    $body = @{
        message = "INFO service started successfully"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$BASE_URL/api/predict/log-anomaly" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body
    
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Anomaly: $($content.anomaly)" -ForegroundColor Green
    Write-Host "Similarity Score: $($content.similarity_score)" -ForegroundColor Green
    Write-Host "Threshold: $($content.threshold)" -ForegroundColor Green
    Write-Host "Message: $($content.message)" -ForegroundColor Green
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
}

Write-Host ""

# Test 3: Log Anomaly Detection - Abnormal Log
Write-Host "TEST 3: Log Anomaly Detection (Abnormal Log)" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Yellow
try {
    $body = @{
        message = "ERROR database connection timeout critical failure"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$BASE_URL/api/predict/log-anomaly" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body
    
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Anomaly: $($content.anomaly)" -ForegroundColor Red
    Write-Host "Similarity Score: $($content.similarity_score)" -ForegroundColor Red
    Write-Host "Threshold: $($content.threshold)" -ForegroundColor Red
    Write-Host "Message: $($content.message)" -ForegroundColor Red
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
}

Write-Host ""

# Test 4: Metric Anomaly Detection - Normal
Write-Host "TEST 4: Metric Anomaly Detection (Normal)" -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Yellow
try {
    $body = @{
        cpu = 35
        memory = 45
        db_errors = 2
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$BASE_URL/api/predict/metric-anomaly" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body
    
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Anomaly: $($content.anomaly)" -ForegroundColor Green
    Write-Host "Isolation Forest Score: $($content.isolation_forest_score)" -ForegroundColor Green
    Write-Host "Message: $($content.message)" -ForegroundColor Green
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
}

Write-Host ""

# Test 5: Metric Anomaly Detection - High Stress
Write-Host "TEST 5: Metric Anomaly Detection (High Stress)" -ForegroundColor Yellow
Write-Host "==============================================" -ForegroundColor Yellow
try {
    $body = @{
        cpu = 98
        memory = 96
        db_errors = 127
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$BASE_URL/api/predict/metric-anomaly" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body
    
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Red
    Write-Host "Anomaly: $($content.anomaly)" -ForegroundColor Red
    Write-Host "Isolation Forest Score: $($content.isolation_forest_score)" -ForegroundColor Red
    Write-Host "Message: $($content.message)" -ForegroundColor Red
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
}

Write-Host ""

# Test 6: Full System Analysis - Healthy
Write-Host "TEST 6: Full System Analysis (Healthy)" -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Yellow
try {
    $body = @{
        log_message = "INFO request completed successfully"
        cpu = 40
        memory = 50
        db_errors = 1
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$BASE_URL/api/predict/system-analysis" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body
    
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Risk Level: $($content.risk_level)" -ForegroundColor Green
    Write-Host "Anomaly Count: $($content.anomaly_count)" -ForegroundColor Green
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
}

Write-Host ""

# Test 7: Full System Analysis - Critical
Write-Host "TEST 7: Full System Analysis (Critical)" -ForegroundColor Yellow
Write-Host "=======================================" -ForegroundColor Yellow
try {
    $body = @{
        log_message = "ERROR database connection timeout critical"
        cpu = 92
        memory = 86
        db_errors = 45
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$BASE_URL/api/predict/system-analysis" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body
    
    $content = $response.Content | ConvertFrom-Json
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Red
    Write-Host "Risk Level: $($content.risk_level)" -ForegroundColor Red
    Write-Host "Anomaly Count: $($content.anomaly_count)" -ForegroundColor Red
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "Testing Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
