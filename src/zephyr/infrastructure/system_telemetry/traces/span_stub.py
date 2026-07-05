# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | 蓝图特有§A
# [MODULE] zephyr.infrastructure.system_telemetry.traces.span_stub
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] src/zephyr/system-telemetry/facade.py;src/zephyr/system-telemetry/logs/structured_sink.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Span命名MUST遵循gen_ai.component.operation风格;跨进程MUST携带traceparent(W3C);禁止手动传递trace_id
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/system-telemetry/blueprint.md;src/zephyr/system-telemetry/facade.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 采样决策由TraceSampler控制;span结束自动flush到logs
# [TESTS] tests/infrastructure/
# [A_module] module_id=MOD-INF_span_stub | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""遥测 · traces/span_stub — W3C TraceContext 分布式追踪管道。

蓝图 §6: Span 数据结构 + W3C TraceContext 传播 + span/log 关联 + 采样。
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import contextvars
import threading
import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

_NS_PER_MS: int = 1_000_000

_SPAN_REGISTRY: dict[str, Span] = {}
_SPAN_REGISTRY_LOCK: threading.Lock = threading.Lock()


@dataclass
class TraceContext:
    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    trace_flags: int = 1
    tracestate: str | None = None

    @classmethod
    def new_root(cls) -> TraceContext:
        return cls(
            trace_id=_gen_hex_id(32),
            span_id=_gen_hex_id(16),
        )

    @classmethod
    def new_child(cls, parent: TraceContext) -> TraceContext:
        return cls(
            trace_id=parent.trace_id,
            span_id=_gen_hex_id(16),
            parent_span_id=parent.span_id,
            trace_flags=parent.trace_flags,
            tracestate=parent.tracestate,
        )

    def to_w3c_header(self) -> str:
        return f"00-{self.trace_id}-{self.span_id}-{self.trace_flags:02x}"

    def to_log_context(self) -> dict[str, str]:
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
        }


@dataclass
class Span:
    name: str
    context: TraceContext
    start_time_ns: int = field(default_factory=lambda: int(time.time() * 1e9))
    end_time_ns: int | None = None
    status: str = "UNSET"
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[SpanEvent] = field(default_factory=list)
    _sample: bool = True

    @property
    def duration_ms(self) -> float | None:
        if self.end_time_ns is None:
            return None
        return (self.end_time_ns - self.start_time_ns) / _NS_PER_MS

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def add_event(self, name: str, attrs: dict[str, Any] | None = None) -> None:
        self.events.append(
            SpanEvent(
                name=name,
                timestamp_ns=int(time.time() * 1e9),
                attributes=attrs or {},
            )
        )

    def finish(self, status: str = "OK") -> None:
        self.end_time_ns = int(time.time() * 1e9)
        self.status = status

    def snapshot(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "trace_id": self.context.trace_id,
            "span_id": self.context.span_id,
            "parent_span_id": self.context.parent_span_id,
            "start_time_ns": self.start_time_ns,
            "end_time_ns": self.end_time_ns,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "attributes": dict(self.attributes),
            "event_count": len(self.events),
        }


@dataclass
class SpanEvent:
    name: str
    timestamp_ns: int
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class TraceSampler:
    base_rate: float = 0.1
    error_always: bool = True
    min_duration_ms_for_keep: float = 50.0

    def should_sample(self, span: Span) -> bool:
        if self.error_always and span.status not in ("UNSET", "OK"):
            return True
        if span.duration_ms is not None and span.duration_ms >= self.min_duration_ms_for_keep:
            return True
        import hashlib
        import struct

        h = hashlib.sha256(span.context.trace_id.encode()).digest()
        threshold = int(0xFFFFFFFF * self.base_rate) & 0xFFFFFFFF
        return struct.unpack(">I", h[:4])[0] <= threshold


def _register_span(span: Span) -> None:
    with _SPAN_REGISTRY_LOCK:
        _SPAN_REGISTRY[span.context.span_id] = span


def _deregister_span(span: Span) -> None:
    with _SPAN_REGISTRY_LOCK:
        _SPAN_REGISTRY.pop(span.context.span_id, None)


def list_active_spans() -> list[dict[str, Any]]:
    with _SPAN_REGISTRY_LOCK:
        return [s.snapshot() for s in _SPAN_REGISTRY.values() if s.end_time_ns is None]


def get_trace_tree(trace_id: str) -> list[dict[str, Any]]:
    with _SPAN_REGISTRY_LOCK:
        return [s.snapshot() for s in _SPAN_REGISTRY.values() if s.context.trace_id == trace_id]


# 5.132.3 修复: threading.local → contextvars,消除跨请求span栈泄漏
# 原 _THREAD_LOCAL._span_stack 在线程池复用线程时残留上个请求的span栈,
# 新请求误将stale span作为parent,破坏trace树结构。contextvars在asyncio和
# 经_wrap_ctx包装的线程池中正确传播且请求边界自动隔离。
_span_stack_var: contextvars.ContextVar[list[Span]] = contextvars.ContextVar(
    "_span_stack", default=[]
)


def _current_span() -> Span | None:
    stack = _span_stack_var.get()
    return stack[-1] if stack else None


def _push_span(span: Span) -> None:
    # 5.132.3 修复: 创建新列表而非原地修改,遵循contextvars不可变语义最佳实践
    stack = _span_stack_var.get()
    _span_stack_var.set(stack + [span])


def _pop_span() -> Span | None:
    stack = _span_stack_var.get()
    if not stack:
        return None
    _span_stack_var.set(stack[:-1])
    return stack[-1]


@contextmanager
def noop_span(
    name: str,
    parent: TraceContext | None = None,
    attributes: dict[str, Any] | None = None,
    sampler: TraceSampler | None = None,
) -> Iterator[Span]:
    parent_span = _current_span()
    if parent is None and parent_span is not None:
        parent = parent_span.context

    ctx = TraceContext.new_child(parent) if parent is not None else TraceContext.new_root()
    span = Span(name=name, context=ctx, attributes=dict(attributes or {}))
    span.set_attribute("thread", threading.current_thread().name)

    _register_span(span)
    _push_span(span)

    try:
        yield span
        span.finish("OK")
    except BaseException:
        # 5.163.5 修复: except Exception → BaseException,确保 Ctrl+C/SystemExit 时
        # span 也调用 finish("ERROR"),避免 span 状态停留在 UNSET。
        span.finish("ERROR")
        raise
    finally:
        _pop_span()
        _deregister_span(span)

        _sampler = sampler or TraceSampler()
        if _sampler.should_sample(span):
            _flush_span(span)


def _flush_span(span: Span) -> None:
    try:
        from zephyr.infrastructure.system_telemetry._trace_bridge import write_record

        write_record(span.snapshot(), labels={"__type": "trace_span"})
    except Exception as e:
        logger.debug("suppressed error in span_stub", exc_info=True)


def _gen_hex_id(hex_len: int) -> str:
    return uuid.uuid4().hex[:hex_len]


from zephyr.infrastructure.system_telemetry._trace_bridge import set_span_context_getter

set_span_context_getter(lambda: _current_span())
