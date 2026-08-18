import json
import logging
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class StructuredLogger:
    def __init__(self, name: str = "newsletter_agent"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _log(self, level: str, event_type: str, message: str, **kwargs: Any) -> None:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "event_type": event_type,
            "message": message,
            **kwargs,
        }
        log_str = json.dumps(payload)
        if level == "DEBUG":
            self.logger.debug(log_str)
        elif level == "WARNING":
            self.logger.warning(log_str)
        elif level == "ERROR":
            self.logger.error(log_str)
        else:
            self.logger.info(log_str)

    def info(self, event_type: str, message: str, **kwargs: Any) -> None:
        self._log("INFO", event_type, message, **kwargs)

    def warning(self, event_type: str, message: str, **kwargs: Any) -> None:
        self._log("WARNING", event_type, message, **kwargs)

    def error(self, event_type: str, message: str, **kwargs: Any) -> None:
        self._log("ERROR", event_type, message, **kwargs)

    def debug(self, event_type: str, message: str, **kwargs: Any) -> None:
        self._log("DEBUG", event_type, message, **kwargs)

    @contextmanager
    def trace_span(self, span_name: str, attributes: Optional[Dict[str, Any]] = None):
        start_time = time.time()
        attrs = attributes or {}
        self.info("span_start", f"Starting span: {span_name}", span_name=span_name, **attrs)
        try:
            yield
            duration = round((time.time() - start_time) * 1000, 2)
            self.info(
                "span_end",
                f"Completed span: {span_name} in {duration}ms",
                span_name=span_name,
                duration_ms=duration,
                status="SUCCESS",
                **attrs,
            )
        except Exception as e:
            duration = round((time.time() - start_time) * 1000, 2)
            self.error(
                "span_error",
                f"Error in span {span_name}: {str(e)}",
                span_name=span_name,
                duration_ms=duration,
                status="ERROR",
                error=str(e),
                **attrs,
            )
            raise


tracer = StructuredLogger("newsletter_agent")
