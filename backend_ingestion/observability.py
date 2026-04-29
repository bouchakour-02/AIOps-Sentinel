"""
OTEL Observability Configuration
Distributed tracing, metrics, and logging
"""

import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor
from opentelemetry.instrumentation.elasticsearch import ElasticsearchInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.api.trace import set_span_in_context

logger = logging.getLogger(__name__)

class ObservabilityManager:
    """Manages all observability components"""
    
    def __init__(self, 
                 service_name: str = "aiops-sentinel",
                 jaeger_agent_host: str = "localhost",
                 jaeger_agent_port: int = 6831,
                 otel_collector_host: str = "localhost",
                 otel_collector_port: int = 4317):
        
        self.service_name = service_name
        self.jaeger_agent_host = jaeger_agent_host
        self.jaeger_agent_port = jaeger_agent_port
        self.otel_collector_host = otel_collector_host
        self.otel_collector_port = otel_collector_port
        
        self.tracer_provider = None
        self.meter_provider = None
        self.tracer = None
        self.meter = None
        
        self._init_logging()
        self._init_tracing()
        self._init_metrics()
        self._init_instrumentation()
    
    def _init_logging(self):
        """Initialize structured logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger.info(f"Observability initialized for {self.service_name}")
    
    def _init_tracing(self):
        """Initialize distributed tracing with Jaeger"""
        try:
            resource = Resource.create({SERVICE_NAME: self.service_name})
            
            # Jaeger exporter (for legacy Jaeger)
            jaeger_exporter = JaegerExporter(
                agent_host_name=self.jaeger_agent_host,
                agent_port=self.jaeger_agent_port,
            )
            
            # OTEL Collector exporter (recommended)
            otel_exporter = OTLPSpanExporter(
                endpoint=f"grpc://{self.otel_collector_host}:{self.otel_collector_port}"
            )
            
            self.tracer_provider = TracerProvider(resource=resource)
            
            # Use OTEL collector if available, fallback to Jaeger
            try:
                self.tracer_provider.add_span_processor(
                    BatchSpanProcessor(otel_exporter)
                )
                logger.info("OTEL Collector exporter configured")
            except:
                self.tracer_provider.add_span_processor(
                    BatchSpanProcessor(jaeger_exporter)
                )
                logger.info("Jaeger exporter configured (OTEL unavailable)")
            
            trace.set_tracer_provider(self.tracer_provider)
            self.tracer = trace.get_tracer(__name__)
            logger.info("Distributed tracing initialized")
            
        except Exception as e:
            logger.error(f"Tracing initialization failed: {e}")
            self.tracer_provider = TracerProvider()
            self.tracer = trace.get_tracer(__name__)
    
    def _init_metrics(self):
        """Initialize metrics collection"""
        try:
            resource = Resource.create({SERVICE_NAME: self.service_name})
            
            # OTEL metrics exporter
            metric_exporter = OTLPMetricExporter(
                endpoint=f"grpc://{self.otel_collector_host}:{self.otel_collector_port}"
            )
            
            metric_reader = PeriodicExportingMetricReader(metric_exporter)
            
            self.meter_provider = MeterProvider(
                resource=resource,
                metric_readers=[metric_reader]
            )
            
            metrics.set_meter_provider(self.meter_provider)
            self.meter = metrics.get_meter(__name__)
            
            # Create instruments
            self.request_counter = self.meter.create_counter(
                "http_requests_total",
                description="Total HTTP requests",
                unit="1"
            )
            
            self.error_counter = self.meter.create_counter(
                "http_errors_total",
                description="Total HTTP errors",
                unit="1"
            )
            
            self.ml_prediction_counter = self.meter.create_counter(
                "ml_predictions_total",
                description="Total ML predictions",
                unit="1"
            )
            
            self.ml_anomaly_counter = self.meter.create_counter(
                "ml_anomalies_detected",
                description="Total anomalies detected",
                unit="1"
            )
            
            self.prediction_latency = self.meter.create_histogram(
                "ml_prediction_latency_ms",
                description="ML prediction latency",
                unit="ms"
            )
            
            logger.info("Metrics initialized")
            
        except Exception as e:
            logger.error(f"Metrics initialization failed: {e}")
            self.meter = None
    
    def _init_instrumentation(self):
        """Initialize auto-instrumentation for libraries"""
        try:
            # FastAPI auto-instrumentation
            FastAPIInstrumentor().instrument()
            
            # HTTP client instrumentation
            RequestsInstrumentor().instrument()
            URLLib3Instrumentor().instrument()
            
            # Database instrumentation
            ElasticsearchInstrumentor().instrument()
            
            logger.info("Auto-instrumentation initialized")
        except Exception as e:
            logger.error(f"Instrumentation initialization failed: {e}")
    
    @contextmanager
    def trace_operation(self, 
                       operation_name: str,
                       attributes: Optional[Dict[str, Any]] = None):
        """Context manager for tracing operations"""
        with self.tracer.start_as_current_span(operation_name) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, str(value))
            yield span
    
    def record_request(self, 
                      path: str,
                      method: str,
                      status_code: int,
                      duration_ms: float):
        """Record HTTP request metrics"""
        if self.meter:
            self.request_counter.add(1, {
                "path": path,
                "method": method,
                "status": status_code
            })
            
            if status_code >= 400:
                self.error_counter.add(1, {
                    "path": path,
                    "status": status_code
                })
    
    def record_ml_prediction(self,
                            model_name: str,
                            anomaly_detected: bool,
                            confidence: float,
                            latency_ms: float):
        """Record ML prediction metrics"""
        if self.meter:
            self.ml_prediction_counter.add(1, {
                "model": model_name,
                "status": "success"
            })
            
            if anomaly_detected:
                self.ml_anomaly_counter.add(1, {
                    "model": model_name
                })
            
            self.prediction_latency.record(latency_ms, {
                "model": model_name
            })
    
    def create_trace_id(self) -> str:
        """Generate a trace ID for correlation"""
        return str(uuid.uuid4())
    
    def shutdown(self):
        """Gracefully shutdown observability"""
        try:
            if self.tracer_provider:
                self.tracer_provider.force_flush(timeout_millis=5000)
            if self.meter_provider:
                self.meter_provider.force_flush(timeout_millis=5000)
            logger.info("Observability shutdown complete")
        except Exception as e:
            logger.error(f"Shutdown error: {e}")


# Singleton instance
_obs_manager = None

def get_observability_manager() -> ObservabilityManager:
    """Get or create observability manager"""
    global _obs_manager
    if _obs_manager is None:
        _obs_manager = ObservabilityManager()
    return _obs_manager

def init_observability(service_name: str = "aiops-sentinel") -> ObservabilityManager:
    """Initialize observability"""
    global _obs_manager
    _obs_manager = ObservabilityManager(service_name=service_name)
    return _obs_manager
