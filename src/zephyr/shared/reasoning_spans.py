"""
Reasoning Spans — OTel GenAI Semantic Conventions 对齐 (M-25)
特性：
  - agent.reasoning span + steps events（OTel GenAI 语义规范）
  - W3C TraceContext 传播：ContractBus 调用自动注入 traceparent + tracestate
  - 与 behavior_audit_logger.py 集成：审计日志关联 Trace ID
"""
import functools
import time
from contextlib import contextmanager
from typing import Any, Callable, Optional


class ReasoningSpan:
    """
    Agent 推理步骤追踪（M-25）
    对齐 OpenTelemetry GenAI Semantic Conventions
    """

    def __init__(self, enable_otel: bool = True):
        self.enable_otel = enable_otel
        self._tracer = None
        if enable_otel:
            try:
                from opentelemetry import trace
                self._tracer = trace.get_tracer("zephyr.capacity-assurance")
            except ImportError:
                self._tracer = None

    def trace_reasoning(self, agent_name: str, task: str):
        if self._tracer:
            return self._otel_trace_reasoning(agent_name, task)
        return self._fallback_trace_reasoning(agent_name, task)

    def _otel_trace_reasoning(self, agent_name: str, task: str):
        from opentelemetry import trace
        span = self._tracer.start_span("agent.reasoning")
        span.set_attribute("gen_ai.system", "zephyr")
        span.set_attribute("gen_ai.request.model", agent_name)
        span.set_attribute("agent.task", task)
        return span

    @contextmanager
    def _fallback_trace_reasoning(self, agent_name: str, task: str):
        start = time.time()
        span_ctx = {
            "span_name": "agent.reasoning",
            "agent_name": agent_name,
            "task": task,
            "start_time": start,
            "steps": [],
        }
        try:
            yield span_ctx
        finally:
            elapsed = time.time() - start
            span_ctx["elapsed_ms"] = elapsed * 1000
            span_ctx["steps_count"] = len(span_ctx["steps"])

    def add_step(self, span_ctx: dict, step_name: str, detail: str = ""):
        step = {"name": step_name, "detail": detail, "timestamp": time.time()}
        if self._tracer and hasattr(span_ctx, 'add_event'):
            span_ctx.add_event(step_name, {"detail": detail})
        elif isinstance(span_ctx, dict):
            span_ctx.setdefault("steps", []).append(step)

    def get_trace_context(self) -> dict:
        try:
            from opentelemetry import trace
            from opentelemetry.trace import propagation
            span = trace.get_current_span()
            ctx = span.get_span_context()
            if ctx.is_valid:
                return {
                    "traceparent": f"00-{ctx.trace_id:032x}-{ctx.span_id:016x}-01",
                    "tracestate": f"zephyr=capacity-assurance",
                }
        except Exception:
            pass
        return {"traceparent": "", "tracestate": ""}


_spans: Optional[ReasoningSpan] = None


def get_reasoning_spans() -> ReasoningSpan:
    global _spans
    if _spans is None:
        _spans = ReasoningSpan()
    return _spans
