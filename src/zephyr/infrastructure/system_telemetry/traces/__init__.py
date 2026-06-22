# [A_module] module_id=MOD-INF_traces | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain-infra_ops/system-telemetry/blueprint.md | 蓝图特有§A
# [MODULE] zephyr.infrastructure.system_telemetry.traces
# [STABILITY] evolving
# [SAFETY] M
# [INVARIANTS] Span命名MUST遵循gen_ai.component.operation风格;跨进程MUST携带traceparent(W3C)
# [MODIFY-GUARD] span_stub.py; facade.py
# [CONSUMERS] facade.py; logs/structured_sink.py
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 采样决策由TraceSampler控制;span结束自动flush到logs
# [TESTS] tests/unit/telemetry/
"""L12 · traces — 分布式链路追踪（W3C TraceContext）"""

from zephyr.infrastructure.system_telemetry.traces.span_stub import (
    Span,
    SpanEvent,
    TraceContext,
    TraceSampler,
    _current_span,
    get_trace_tree,
    list_active_spans,
    noop_span,
)

__all__ = [
    "Span",
    "SpanEvent",
    "TraceContext",
    "TraceSampler",
    "_current_span",
    "get_trace_tree",
    "list_active_spans",
    "noop_span",
    "span_stub",
]
