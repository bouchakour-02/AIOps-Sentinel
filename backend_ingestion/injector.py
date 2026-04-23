import requests
import time
import json
import re

# Config
OTEL_HTTP_URL = "http://192.168.159.136:30318/v1/logs"
DATASET_PATH = "../log-dataset.md"


def send_to_otel(body, severity="INFO", service="unknown"):
    payload = {
        "resourceLogs": [{
            "resource": {
                "attributes": [
                    {"key": "service.name", "value": {"stringValue": service}}
                ]
            },
            "scopeLogs": [{
                "logRecords": [{
                    "timeUnixNano": str(int(time.time() * 1e9)),
                    "severityText": severity,
                    "body": {"stringValue": body}
                }]
            }]
        }]
    }

    try:
        res = requests.post(OTEL_HTTP_URL, json=payload, timeout=2)
        return res.status_code
    except Exception as e:
        print("⚠️ OTel unreachable → skipping log", e)
        return None


def extract_logs_from_md(content):
    pattern = r"```(?:log|json)?\n(.*?)```"
    matches = re.findall(pattern, content, re.DOTALL)

    logs = []
    for block in matches:
        for line in block.split("\n"):
            line = line.strip()
            # ❌ skip empty
            if not line:
                continue
            # ❌ skip markdown / fake content
            if line.startswith("#"):
                continue
            # ❌ skip templates
            if "<Timestamp>" in line:
                continue
            # ❌ skip separators (====, ----, ────)
            if re.match(r"^[=\-─_]{5,}$", line):
                continue
            # ❌ skip system banners
            if "User UID" in line or "User GID" in line:
                continue
            # ❌ skip setup / install logs (noise)
            if any(x in line.lower() for x in [
                "creating template directory",
                "installing capture script",
                "configuring git globally",
                "global setup complete",
                "executing setup.ps1",
                "no custom files found",
                "change in ownership"
            ]):
                continue
            logs.append(line)
    return logs


def detect_severity(log):
    log_upper = log.upper()
    if "ERROR" in log_upper or "CRITICAL" in log_upper or "FATAL" in log_upper or "EXCEPTION" in log_upper or "FAILURE" in log_upper or "FAILED" in log_upper or "UNABLE" in log_upper :
        return "ERROR"
    elif "WARN" in log_upper:
        return "WARN"
    else:
        return "INFO"


def detect_service(log):
    log_lower = log.lower()

    if "organisationvalue" in log_lower:
        return "veggo-spring"

    elif "ssl_do_handshake" in log_lower or "nginx" in log_lower or "upstream" in log_lower:
        return "nginx-proxy"

    elif log.startswith("{") and '"level"' in log_lower:
        return "node-api"

    elif "cert-manager" in log_lower:
        return "k8s-cert-manager"

    elif "envoy" in log_lower or "istio" in log_lower:
        return "istio-mesh"

    elif "tomcat" in log_lower:
        return "tomcat"

    elif "jboss" in log_lower or "wildfly" in log_lower:
        return "wildfly"

    else:
        return "generic-service"


def run_injector():
    print("🚀 Starting clean log injection...")

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    logs = extract_logs_from_md(content)

    print(f"✅ Extracted {len(logs)} logs\n")

    for log in logs:
        severity = detect_severity(log)
        service = detect_service(log)

        print(f"📤 {service} | {severity} → {log[:80]}")

        send_to_otel(log, severity, service)

        time.sleep(0.2)  # smoother streaming


if __name__ == "__main__":
    run_injector()