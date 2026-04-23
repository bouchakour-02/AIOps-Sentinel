from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch
import requests
import time 


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REMPLACE PAR L'IP QUE TU AS TROUVÉE À L'ÉTAPE 1
ELASTIC_IP = "192.168.159.136" 
ELASTIC_URL = f"http://{ELASTIC_IP}:30200"
PROMETHEUS_URL = f"http://{ELASTIC_IP}:30090/api/v1/query"


# Connexion à la base de données
es = Elasticsearch(ELASTIC_URL)

@app.get("/")
def home():
    return {"status": "Backend Active"}

@app.get("/logs")
def get_logs():
    """Récupère les logs stockés dans Elasticsearch"""
    try:
        # On cherche dans l'index défini dans otel-collector.yaml
        response = es.search(index="vermeg-logs", body={"query": {"match_all": {}}})
        
        # On nettoie le JSON pour ne garder que l'important
        logs = []
        for hit in response['hits']['hits']:
            source = hit['_source']
            logs.append({
                "timestamp": source.get('@timestamp'),
                "message": source.get('Body'),
                "service": source.get('Resource', {}).get('service', {}).get('name')
            })
        return {"total": response['hits']['total']['value'], "logs": logs}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/logs")
def get_api_logs():
    """Logs endpoint for the dashboard frontend — includes severity extraction."""
    try:
        response = es.search(
            index="vermeg-logs",
            body={"query": {"match_all": {}}, "sort": [{"@timestamp": {"order": "desc"}}]},
            size=50
        )
        logs = []
        for hit in response['hits']['hits']:
            source = hit['_source']
            message = source.get('Body', '') or ''
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
                "timestamp": source.get('@timestamp'),
                "message": message,
                "service": source.get('Resource', {}).get('service', {}).get('name', 'unknown'),
                "severity": severity,
                "severity_text": source.get('SeverityText', severity.upper()),
            })
        return {"total": response['hits']['total']['value'], "logs": logs}
    except Exception as e:
        return {"error": str(e), "logs": []}

# --- 2. RÉCUPÉRATION DU CPU (PROMETHEUS) ---
@app.get("/api/metrics/cpu")
def get_cpu_usage():
    # Formule PromQL : 1 - le temps idle (repos) sur la dernière minute
    query = '1 - rate(system_cpu_time_seconds_total{state="idle"}[30s])'
    
    try:
        response = requests.get(PROMETHEUS_URL, params={'query': query})
        data = response.json()
        
        if data['status'] == 'success' and data['data']['result']:
            # On récupère la valeur actuelle (multipliée par 100 pour avoir un %)
            cpu_value = float(data['data']['result'][0]['value'][1]) * 100
            return {"metric": "cpu_usage", "value": round(cpu_value, 2), "unit": "%"}
        return {"value": 0, "status": "no_data"}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)