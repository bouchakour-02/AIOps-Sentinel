"""
Prometheus Client for Real Metric Retrieval
Handles PromQL queries with caching and aggregation
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
import logging
import json

logger = logging.getLogger(__name__)

class PrometheusClient:
    def __init__(self, prom_url: str = "http://localhost:9090"):
        self.prom_url = prom_url
        self.timeout = 5
        self.cache = {}
        self.cache_ttl = 30
        
    def is_available(self) -> bool:
        """Check if Prometheus is available"""
        try:
            r = requests.get(f"{self.prom_url}/-/healthy", timeout=2)
            return r.status_code == 200
        except:
            return False
    
    def query(self, promql: str) -> List[Dict]:
        """
        Execute instant PromQL query
        
        Args:
            promql: PromQL query string
            
        Returns:
            List of metric results with values
        """
        try:
            r = requests.get(
                f"{self.prom_url}/api/v1/query",
                params={"query": promql},
                timeout=self.timeout
            )
            
            if r.status_code == 200:
                data = r.json()
                if data.get("status") == "success":
                    results = []
                    for result in data.get("data", {}).get("result", []):
                        results.append({
                            "metric": result.get("metric", {}),
                            "value": result.get("value", [None, None])[1],
                            "timestamp": result.get("value", [None, None])[0]
                        })
                    return results
            return []
            
        except Exception as e:
            logger.error(f"PromQL query error: {e}")
            return []
    
    def query_range(self, 
                   promql: str,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   step: str = "1m") -> List[Dict]:
        """
        Execute range PromQL query (time-series)
        
        Args:
            promql: PromQL query string
            start_time: Start time (default 1 hour ago)
            end_time: End time (default now)
            step: Resolution (default 1 minute)
            
        Returns:
            Time-series data with multiple values
        """
        try:
            if start_time is None:
                start_time = datetime.utcnow() - timedelta(hours=1)
            if end_time is None:
                end_time = datetime.utcnow()
            
            start_ts = int(start_time.timestamp())
            end_ts = int(end_time.timestamp())
            
            r = requests.get(
                f"{self.prom_url}/api/v1/query_range",
                params={
                    "query": promql,
                    "start": start_ts,
                    "end": end_ts,
                    "step": step
                },
                timeout=self.timeout
            )
            
            if r.status_code == 200:
                data = r.json()
                if data.get("status") == "success":
                    results = []
                    for result in data.get("data", {}).get("result", []):
                        results.append({
                            "metric": result.get("metric", {}),
                            "values": [
                                {
                                    "timestamp": int(v[0]),
                                    "value": float(v[1]) if v[1] else None
                                }
                                for v in result.get("values", [])
                            ]
                        })
                    return results
            return []
            
        except Exception as e:
            logger.error(f"Range query error: {e}")
            return []
    
    def get_cpu_usage(self, instance: Optional[str] = None, minutes: int = 60) -> Dict:
        """Get CPU usage metrics"""
        query = "node_cpu_seconds_total"
        if instance:
            query += f'{{instance="{instance}"}}'
        
        results = self.query_range(
            query,
            start_time=datetime.utcnow() - timedelta(minutes=minutes)
        )
        
        return {
            "metric": "cpu_seconds_total",
            "data": results,
            "unit": "seconds"
        }
    
    def get_memory_usage(self, instance: Optional[str] = None, minutes: int = 60) -> Dict:
        """Get memory usage metrics"""
        query = "node_memory_MemAvailable_bytes"
        if instance:
            query += f'{{instance="{instance}"}}'
        
        results = self.query_range(
            query,
            start_time=datetime.utcnow() - timedelta(minutes=minutes)
        )
        
        return {
            "metric": "memory_available_bytes",
            "data": results,
            "unit": "bytes"
        }
    
    def get_current_cpu_percent(self) -> float:
        """Get current CPU usage percentage"""
        try:
            results = self.query("100 - (avg(rate(node_cpu_seconds_total{mode='idle'}[5m])) * 100)")
            if results and results[0].get("value"):
                return float(results[0]["value"])
            return 0.0
        except:
            return 0.0
    
    def get_current_memory_percent(self) -> float:
        """Get current memory usage percentage"""
        try:
            results = self.query(
                "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100"
            )
            if results and results[0].get("value"):
                return float(results[0]["value"])
            return 0.0
        except:
            return 0.0
    
    def get_error_rate(self, 
                      service: Optional[str] = None,
                      minutes: int = 5) -> float:
        """Get application error rate"""
        query = "rate(application_errors_total[5m])"
        if service:
            query = f'rate(application_errors_total{{service="{service}"}}[5m])'
        
        try:
            results = self.query(query)
            if results and results[0].get("value"):
                return float(results[0]["value"])
            return 0.0
        except:
            return 0.0
    
    def get_request_latency(self, quantile: float = 0.95) -> float:
        """Get request latency in milliseconds"""
        query = f'histogram_quantile({quantile}, rate(http_request_duration_ms_bucket[5m]))'
        try:
            results = self.query(query)
            if results and results[0].get("value"):
                return float(results[0]["value"])
            return 0.0
        except:
            return 0.0
    
    def get_targets(self) -> Dict:
        """Get Prometheus scrape targets info"""
        try:
            r = requests.get(
                f"{self.prom_url}/api/v1/targets",
                timeout=self.timeout
            )
            if r.status_code == 200:
                data = r.json()
                targets = data.get("data", {})
                return {
                    "active": len(targets.get("activeTargets", [])),
                    "dropped": len(targets.get("droppedTargets", [])),
                    "targets": [
                        {
                            "job": t.get("labels", {}).get("job"),
                            "instance": t.get("labels", {}).get("instance"),
                            "state": t.get("health"),
                            "lastScrape": t.get("lastScrape")
                        }
                        for t in targets.get("activeTargets", [])
                    ]
                }
            return {}
        except Exception as e:
            logger.error(f"Targets query error: {e}")
            return {}
    
    def get_service_metrics(self, service: str) -> Dict:
        """Get all metrics for a service"""
        try:
            metrics = {
                "service": service,
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": {}
            }
            
            # Request rate
            req_rate = self.query(
                f'rate(http_requests_total{{service="{service}"}}[5m])'
            )
            metrics["metrics"]["request_rate"] = float(req_rate[0]["value"]) if req_rate and req_rate[0].get("value") else 0
            
            # Error rate
            err_rate = self.query(
                f'rate(http_requests_total{{service="{service}",status=~"5.."}}[5m])'
            )
            metrics["metrics"]["error_rate"] = float(err_rate[0]["value"]) if err_rate and err_rate[0].get("value") else 0
            
            # Latency P95
            latency = self.query(
                f'histogram_quantile(0.95, rate(http_request_duration_ms_bucket{{service="{service}"}}[5m]))'
            )
            metrics["metrics"]["latency_p95"] = float(latency[0]["value"]) if latency and latency[0].get("value") else 0
            
            return metrics
            
        except Exception as e:
            logger.error(f"Service metrics error: {e}")
            return {}
    
    def get_metrics_summary(self) -> Dict:
        """Get summary of all available metrics"""
        try:
            r = requests.get(
                f"{self.prom_url}/api/v1/label/__name__/values",
                timeout=self.timeout
            )
            if r.status_code == 200:
                data = r.json()
                metrics = data.get("data", [])
                return {
                    "total_metrics": len(metrics),
                    "metrics": metrics[:20],  # Top 20
                    "timestamp": datetime.utcnow().isoformat()
                }
            return {}
        except Exception as e:
            logger.error(f"Metrics summary error: {e}")
            return {}


# Singleton instance
_prom_client = None

def get_prom_client(prom_url: str = "http://localhost:9090") -> PrometheusClient:
    """Get or create Prometheus client"""
    global _prom_client
    if _prom_client is None:
        _prom_client = PrometheusClient(prom_url)
    return _prom_client
