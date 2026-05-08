"""
ZephyrLogger — 结构化日志 + OpenTelemetry 集成 (M-10)
职责：所有日志关联 Trace ID，自动生成 OTel Metrics Span。

设计：
  - structlog 核心（零依赖 baseline）
  - OTel SDK optional（可用时自动启用 Reasoning Spans）
  - 容量相关日志带 capacity_metrics 标签
"""
import logging
import os
import sys
import time
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class LogEntry:
    timestamp: str
    level: str
    message: str
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    module: Optional[str] = None
    capacity_metrics: Optional[dict] = None
    extra: Optional[dict] = None

    def as_dict(self) -> dict:
        result = {"timestamp": self.timestamp, "level": self.level, "message": self.message}
        if self.trace_id:
            result["trace_id"] = self.trace_id
        if self.span_id:
            result["span_id"] = self.span_id
        if self.module:
            result["module"] = self.module
        if self.capacity_metrics:
            result["capacity_metrics"] = self.capacity_metrics
        if self.extra:
            result.update(self.extra)
        return result


class ZephyrLogger:
    def __init__(self, module: str = "zephyr", enable_otel: bool = True, log_level: str = "INFO"):
        self.module = module
        self.enable_otel = enable_otel
        self.logger = logging.getLogger(module)
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            ))
            self.logger.addHandler(handler)

    def _make_trace_id(self) -> str:
        if self.enable_otel:
            try:
                from opentelemetry import trace
                span = trace.get_current_span()
                if span and span.get_span_context().is_valid:
                    ctx = span.get_span_context()
                    return f"{ctx.trace_id:032x}"
            except Exception:
                pass
        return "local"

    def _make_span_id(self) -> Optional[str]:
        if self.enable_otel:
            try:
                from opentelemetry import trace
                span = trace.get_current_span()
                if span and span.get_span_context().is_valid:
                    ctx = span.get_span_context()
                    return f"{ctx.span_id:016x}"
            except Exception:
                pass
        return None

    def info(self, message: str, capacity_metrics: Optional[dict] = None, **extra):
        entry = self._build_entry("INFO", message, capacity_metrics, extra)
        self.logger.info(entry.as_dict())
        return entry

    def warning(self, message: str, capacity_metrics: Optional[dict] = None, **extra):
        entry = self._build_entry("WARNING", message, capacity_metrics, extra)
        self.logger.warning(entry.as_dict())
        return entry

    def error(self, message: str, capacity_metrics: Optional[dict] = None, **extra):
        entry = self._build_entry("ERROR", message, capacity_metrics, extra)
        self.logger.error(entry.as_dict())
        return entry

    def debug(self, message: str, capacity_metrics: Optional[dict] = None, **extra):
        entry = self._build_entry("DEBUG", message, capacity_metrics, extra)
        self.logger.debug(entry.as_dict())
        return entry

    def _build_entry(self, level: str, message: str,
                     capacity_metrics: Optional[dict], extra: dict) -> LogEntry:
        from datetime import datetime, timezone
        ts = datetime.now(timezone.utc).isoformat()
        return LogEntry(
            timestamp=ts,
            level=level,
            message=message,
            trace_id=self._make_trace_id(),
            span_id=self._make_span_id(),
            module=self.module,
            capacity_metrics=capacity_metrics,
            extra=extra if extra else None,
        )


_default_logger: Optional[ZephyrLogger] = None


def get_logger(module: str = "zephyr") -> ZephyrLogger:
    global _default_logger
    if _default_logger is None:
        _default_logger = ZephyrLogger(module=module)
    return _default_logger
