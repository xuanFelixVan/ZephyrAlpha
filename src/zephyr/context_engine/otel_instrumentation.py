"""otel_instrumentation.py — 全链路 OTel (B12, DD86, TASK-015 beta v)"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from typing import Any


@dataclass
class PipelineTraceSpan:
    name: str
    start_time: float
    end_time: float = 0.0
    attributes: dict[str, Any] = field(default_factory=dict)
    status: str = "OK"


class OTelInstrumentation:
    """OTEL trace Orc→CE.build→compress→validate→inject→Agent Action (DD86)."""
    def __init__(self) -> None:
        self._spans: list[PipelineTraceSpan] = []

    def start_span(self, name: str, attrs: dict[str, Any] | None = None) -> PipelineTraceSpan:
        span = PipelineTraceSpan(name=name, start_time=time.time(), attributes=attrs or {})
        self._spans.append(span)
        return span

    def end_span(self, span: PipelineTraceSpan) -> None:
        span.end_time = time.time()
