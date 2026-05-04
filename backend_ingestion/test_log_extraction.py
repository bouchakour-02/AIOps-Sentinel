#!/usr/bin/env python3
"""Test log extraction to diagnose why dashboard shows 'Waiting for logs'"""

import requests
import json

ES_URL = "http://192.168.159.136:30200"

def test_log_extraction():
    # Query Elasticsearch
    response = requests.post(
        f"{ES_URL}/vermeg-logs/_search",
        json={
            "query": {"match_all": {}},
            "sort": [{"@timestamp": {"order": "desc"}}],
            "size": 10
        },
        headers={"Content-Type": "application/json"}
    )
    
    payload = response.json()
    hits = payload.get("hits", {}).get("hits", [])
    
    print(f"✅ Found {len(hits)} logs in Elasticsearch\n")
    
    if not hits:
        print("❌ No logs found!")
        return
    
    # Test extraction on first 3 logs
    for i, hit in enumerate(hits[:3]):
        source = hit.get("_source", {})
        print(f"\n{'='*80}")
        print(f"LOG #{i+1}")
        print(f"{'='*80}")
        print(f"Raw _source keys: {list(source.keys())}")
        
        # Test message extraction
        body = source.get("Body")
        body_l = source.get("body")
        message = source.get("Message")
        
        print(f"\nBody (capital): {repr(body)}")
        print(f"body (lowercase): {repr(body_l)}")
        print(f"Message: {repr(message)}")
        
        # Simulate the extraction function
        extracted = ""
        if isinstance(body, str) and body:
            extracted = body
            print(f"✅ Extracted from Body (capital)")
        elif isinstance(body, dict):
            extracted = body.get("stringValue") or body.get("text") or ""
            print(f"✅ Extracted from Body dict")
        elif isinstance(body_l, str) and body_l:
            extracted = body_l
            print(f"✅ Extracted from body (lowercase)")
        elif isinstance(body_l, dict):
            extracted = body_l.get("stringValue") or body_l.get("text") or ""
            print(f"✅ Extracted from body dict")
        elif isinstance(message, str) and message:
            extracted = message
            print(f"✅ Extracted from Message")
        
        if not extracted:
            print(f"❌ FAILED TO EXTRACT MESSAGE - This log won't appear in dashboard!")
        else:
            print(f"\n📝 Final message: {extracted[:100]}...")
        
        # Test service extraction
        service = _extract_service(source)
        print(f"📦 Service: {service}")
        
        # Test timestamp extraction
        timestamp = _extract_timestamp(source)
        print(f"⏰ Timestamp: {timestamp}")


def _extract_service(source):
    """Extract service name from OTel/resource-style fields."""
    service = source.get("service")
    if isinstance(service, str) and service:
        return service
    if isinstance(service, dict):
        name = service.get("name")
        if isinstance(name, str) and name:
            return name

    resource = source.get("Resource") or source.get("resource")
    if isinstance(resource, dict):
        svc = resource.get("service")
        if isinstance(svc, dict):
            name = svc.get("name")
            if isinstance(name, str) and name:
                return name

    attrs = source.get("attributes")
    if isinstance(attrs, list):
        for attr in attrs:
            if attr.get("key") == "service.name":
                value = attr.get("value", {})
                return value.get("stringValue", "unknown")

    return "unknown"


def _extract_timestamp(source):
    return (
        source.get("@timestamp")
        or source.get("timestamp")
        or source.get("Timestamp")
        or source.get("time")
    )


if __name__ == "__main__":
    test_log_extraction()
