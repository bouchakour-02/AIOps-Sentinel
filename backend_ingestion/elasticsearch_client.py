"""
Elasticsearch Client for Real Log Retrieval
Handles all ES queries with caching and error handling
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ElasticsearchClient:
    def __init__(self, es_url: str = "http://localhost:9200"):
        self.es_url = es_url
        self.timeout = 5
        self.default_index = "logs-*"
        self.cache = {}
        self.cache_ttl = 30  # seconds
        
    def is_available(self) -> bool:
        """Check if Elasticsearch is available"""
        try:
            r = requests.get(f"{self.es_url}/_cluster/health", timeout=2)
            return r.status_code == 200
        except:
            return False
    
    def get_recent_logs(self, limit: int = 100, minutes: int = 60) -> List[Dict]:
        """
        Get recent logs from Elasticsearch
        
        Args:
            limit: Max number of logs to return
            minutes: How far back to query (default 60 minutes)
            
        Returns:
            List of log documents with source data
        """
        try:
            # Build time range query
            start_time = (datetime.utcnow() - timedelta(minutes=minutes)).isoformat() + "Z"
            
            query = {
                "query": {
                    "range": {
                        "timestamp": {
                            "gte": start_time,
                            "lte": "now"
                        }
                    }
                },
                "sort": [{"timestamp": {"order": "desc"}}],
                "size": limit
            }
            
            r = requests.post(
                f"{self.es_url}/{self.default_index}/_search",
                json=query,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if r.status_code == 200:
                hits = r.json().get("hits", {}).get("hits", [])
                return [
                    {
                        "id": hit["_id"],
                        "index": hit["_index"],
                        "timestamp": hit["_source"].get("timestamp"),
                        "message": hit["_source"].get("message"),
                        "severity": hit["_source"].get("severity", "unknown"),
                        "service": hit["_source"].get("service", "unknown"),
                        "source": hit["_source"].get("source"),
                    }
                    for hit in hits
                ]
            else:
                logger.error(f"ES query failed: {r.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Elasticsearch query error: {e}")
            return []
    
    def search_logs(self, 
                   query_string: str,
                   filters: Optional[Dict] = None,
                   limit: int = 50) -> List[Dict]:
        """
        Search logs with KQL/Lucene query
        
        Args:
            query_string: Search query (e.g., "ERROR database")
            filters: Additional filters (severity, service, time range)
            limit: Result limit
            
        Returns:
            Search results
        """
        try:
            must_clauses = [
                {"multi_match": {
                    "query": query_string,
                    "fields": ["message", "service"]
                }}
            ]
            
            # Add filters
            if filters:
                if "severity" in filters:
                    must_clauses.append({
                        "term": {"severity.keyword": filters["severity"]}
                    })
                if "service" in filters:
                    must_clauses.append({
                        "term": {"service.keyword": filters["service"]}
                    })
                if "minutes" in filters:
                    start_time = (datetime.utcnow() - timedelta(minutes=filters["minutes"])).isoformat() + "Z"
                    must_clauses.append({
                        "range": {"timestamp": {"gte": start_time}}
                    })
            
            query = {
                "query": {"bool": {"must": must_clauses}},
                "sort": [{"timestamp": {"order": "desc"}}],
                "size": limit
            }
            
            r = requests.post(
                f"{self.es_url}/{self.default_index}/_search",
                json=query,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if r.status_code == 200:
                hits = r.json().get("hits", {}).get("hits", [])
                return [hit["_source"] for hit in hits]
            return []
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def get_logs_by_severity(self, severity: str, limit: int = 100) -> List[Dict]:
        """Get logs filtered by severity (info, warn, error, critical)"""
        return self.search_logs(
            "*",  # Match all
            filters={"severity": severity.lower()},
            limit=limit
        )
    
    def get_logs_by_service(self, service: str, limit: int = 100) -> List[Dict]:
        """Get logs from specific service"""
        return self.search_logs(
            "*",
            filters={"service": service},
            limit=limit
        )
    
    def get_error_logs(self, minutes: int = 60, limit: int = 50) -> List[Dict]:
        """Get error and critical logs from recent time range"""
        try:
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    "timestamp": {
                                        "gte": f"now-{minutes}m"
                                    }
                                }
                            }
                        ],
                        "should": [
                            {"term": {"severity.keyword": "ERROR"}},
                            {"term": {"severity.keyword": "error"}},
                            {"term": {"severity.keyword": "CRITICAL"}},
                            {"term": {"severity.keyword": "critical"}}
                        ],
                        "minimum_should_match": 1
                    }
                },
                "sort": [{"timestamp": {"order": "desc"}}],
                "size": limit
            }
            
            r = requests.post(
                f"{self.es_url}/{self.default_index}/_search",
                json=query,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if r.status_code == 200:
                hits = r.json().get("hits", {}).get("hits", [])
                return [hit["_source"] for hit in hits]
            return []
            
        except Exception as e:
            logger.error(f"Error logs query failed: {e}")
            return []
    
    def get_log_stats(self, minutes: int = 60) -> Dict[str, Any]:
        """Get log statistics (count by severity, service, etc)"""
        try:
            query = {
                "query": {
                    "range": {
                        "timestamp": {
                            "gte": f"now-{minutes}m"
                        }
                    }
                },
                "aggs": {
                    "by_severity": {
                        "terms": {"field": "severity.keyword", "size": 10}
                    },
                    "by_service": {
                        "terms": {"field": "service.keyword", "size": 20}
                    },
                    "total_count": {
                        "value_count": {"field": "_id"}
                    }
                }
            }
            
            r = requests.post(
                f"{self.es_url}/{self.default_index}/_search",
                json=query,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if r.status_code == 200:
                data = r.json()
                aggs = data.get("aggregations", {})
                return {
                    "total": aggs.get("total_count", {}).get("value", 0),
                    "by_severity": {
                        bucket["key"]: bucket["doc_count"]
                        for bucket in aggs.get("by_severity", {}).get("buckets", [])
                    },
                    "by_service": {
                        bucket["key"]: bucket["doc_count"]
                        for bucket in aggs.get("by_service", {}).get("buckets", [])
                    }
                }
            return {}
            
        except Exception as e:
            logger.error(f"Stats query error: {e}")
            return {}
    
    def index_log(self, message: str, severity: str = "info", 
                  service: str = "test", **kwargs) -> bool:
        """Index a new log document"""
        try:
            doc = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "message": message,
                "severity": severity,
                "service": service,
                **kwargs
            }
            
            r = requests.post(
                f"{self.es_url}/logs-test/_doc",
                json=doc,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            return r.status_code in [201, 200]
            
        except Exception as e:
            logger.error(f"Index error: {e}")
            return False


# Singleton instance
_es_client = None

def get_es_client(es_url: str = "http://localhost:9200") -> ElasticsearchClient:
    """Get or create ES client"""
    global _es_client
    if _es_client is None:
        _es_client = ElasticsearchClient(es_url)
    return _es_client
