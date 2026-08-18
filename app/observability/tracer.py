import json
import logging
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Generator, Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter, SpanExporter, SpanExportResult
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Status, StatusCode, Span

from app.observability.pii_redactor import redactor


class InMemorySpanCollector(SpanExporter):
    """In-memory span exporter for testing and runtime telemetry tracking."""
    def __init__(self):
        self.spans = []

    def export(self, spans) -> SpanExportResult:
        self.spans.extend(spans)
        return SpanExportResult.SUCCESS

    def shutdown(self):
        pass


class OpenTelemetryAgentTracer:
    """Enterprise OpenTelemetry distributed tracer and structured JSON logging framework.
    
    Provides authentic OpenTelemetry TracerProvider initialization, span hierarchies,
    contextual span linking, and automatic PII sanitization across logs and spans.
    """

    def __init__(self, service_name: str = "personalized-cloud-newsletter-agent"):
        self.service_name = service_name
        self.logger = logging.getLogger("newsletter_agent")
        
        # Configure JSON logging handler
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter("%(message)s"))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
            self.logger.propagate = False

        # Configure real OpenTelemetry TracerProvider
        resource = Resource.create({"service.name": self.service_name, "environment": "production"})
        self.provider = TracerProvider(resource=resource)
        
        # Add exporters for in-memory tracking and verification
        self.memory_exporter = InMemorySpanCollector()
        self.provider.add_span_processor(SimpleSpanProcessor(self.memory_exporter))
        
        trace.set_tracer_provider(self.provider)
        self.otel_tracer = trace.get_tracer(self.service_name, "1.0.0")

    @property
    def tracer_provider(self) -> TracerProvider:
        return self.provider

    def _log_event(self, level: str, event_type: str, message: str, **kwargs: Any) -> None:
        """Emits an immutable, structured JSON log event with PII redaction."""
        sanitized_kwargs = redactor.redact_dict(kwargs)
        sanitized_message = redactor.redact_text(message)
        
        # Get active span ID if available
        current_span = trace.get_current_span()
        span_ctx = current_span.get_span_context() if current_span else None
        
        payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "event_type": event_type,
            "message": sanitized_message,
            "service": self.service_name,
        }
        
        if span_ctx and span_ctx.is_valid:
            payload["trace_id"] = f"{span_ctx.trace_id:032x}"
            payload["span_id"] = f"{span_ctx.span_id:016x}"
            
        payload.update(sanitized_kwargs)
        
        log_line = json.dumps(payload)
        if level == "INFO":
            self.logger.info(log_line)
        elif level == "WARNING":
            self.logger.warning(log_line)
        elif level == "ERROR":
            self.logger.error(log_line)
        else:
            self.logger.debug(log_line)

    def info(self, event_type: str, message: str, **kwargs: Any) -> None:
        self._log_event("INFO", event_type, message, **kwargs)

    def warning(self, event_type: str, message: str, **kwargs: Any) -> None:
        self._log_event("WARNING", event_type, message, **kwargs)

    def error(self, event_type: str, message: str, **kwargs: Any) -> None:
        self._log_event("ERROR", event_type, message, **kwargs)

    @contextmanager
    def trace_span(self, span_name: str, attributes: Optional[Dict[str, Any]] = None) -> Generator[Span, None, None]:
        """Context manager creating a real OpenTelemetry span with structured lifecycle logs."""
        start_time = time.perf_counter()
        sanitized_attrs = redactor.redact_dict(attributes or {})
        
        with self.otel_tracer.start_as_current_span(span_name) as span:
            # Set OpenTelemetry span attributes
            for k, v in sanitized_attrs.items():
                if isinstance(v, (str, bool, int, float)):
                    span.set_attribute(k, v)
                else:
                    span.set_attribute(k, json.dumps(v))
            
            self.info("span_start", f"Starting span: {span_name}", span_name=span_name, **sanitized_attrs)
            try:
                yield span
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                span.set_status(Status(StatusCode.OK))
                self.info("span_end", f"Completed span: {span_name} in {duration_ms}ms", span_name=span_name, duration_ms=duration_ms, status="SUCCESS", **sanitized_attrs)
            except Exception as e:
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                self.error("span_error", f"Error in span: {span_name}: {str(e)}", span_name=span_name, duration_ms=duration_ms, status="ERROR", error=str(e), **sanitized_attrs)
                raise


OpenTelemetryTracer = OpenTelemetryAgentTracer
tracer = OpenTelemetryAgentTracer()
