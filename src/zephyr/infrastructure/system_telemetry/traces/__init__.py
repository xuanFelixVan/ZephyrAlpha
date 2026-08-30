# [A_module] module_id=MOD-INF-traces | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | 蓝图特有§A
# [MODULE] zephyr.infrastructure.system_telemetry.traces
# [STABILITY] evolving
# [SAFETY] M
# [INVARIANTS] Span命名MUST遵循gen_ai.component.operation风格;跨进程MUST携带traceparent(W3C)
# [MODIFY-GUARD] span_stub.py; facade.py
# [CONSUMERS] facade.py
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 采样决策由TraceSampler控制;span结束自动flush到logs
# [TESTS] tests/infrastructure/
# [TTL] permanent
"""
遥测 · traces — 分布式链路追踪（W3C TraceContext）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: Span, SpanEvent, TraceContext, TraceSampler, _current_span, get_trace…
#   code: __init__.py import L43
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 Span, SpanEvent, TraceContext, TraceSampler, _current_span, get_trace_tree,…
#   desc: __init__ import L43；__all__ 9 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（9 符号）
#   name_en: __all__
#   intro: Span, SpanEvent, TraceContext, TraceSampler, _current_span, get_trace_tree, lis…
#   downstream: facade.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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
