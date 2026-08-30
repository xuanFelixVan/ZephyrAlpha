# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] zephyr.infrastructure.system_telemetry._trace_bridge
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.system_telemetry.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-015 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: fn 参数
#   fields: 参数 fn，类型注解 Callable[[], Any]
#   code: _trace_bridge.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: data 参数
#   fields: 参数 data，类型注解 dict[str, Any]
#   code: _trace_bridge.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: labels 参数
#   fields: 参数 labels，类型注解 dict[str, Any] | None
#   code: _trace_bridge.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① set_span_context_getter
#   name_en: set_span_context_getter
#   intro: set_span_context_getter(fn) 源码 L97-L99
#   desc: 源码 L97-L99
#   inputs: fn
#   outputs: 返回值
# - id: A2
#   name_zh: ② set_record_writer
#   name_en: set_record_writer
#   intro: set_record_writer(fn) 源码 L102-L104
#   desc: 源码 L102-L104
#   inputs: fn
#   outputs: 返回值
# - id: A3
#   name_zh: ③ get_current_span
#   name_en: get_current_span
#   intro: get_current_span() 源码 L107-L110
#   desc: 源码 L107-L110
#   inputs: 无参数
#   outputs: object
# - id: A4
#   name_zh: ④ write_record
#   name_en: write_record
#   intro: write_record(data, labels) 源码 L113-L116
#   desc: 源码 L113-L116
#   inputs: data labels
#   outputs: bool
# 层: 输出
# - id: O1
#   name_zh: object
#   name_en: object
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

from typing import Any, Callable

_span_context_getter: Callable[[], Any] | None = None
span_context_getter = _span_context_getter  # public alias（Stage 4 公共化）

_record_writer: Callable[[dict[str, Any], dict[str, Any] | None], bool] | None = None
record_writer = _record_writer  # public alias（Stage 4 公共化）


def set_span_context_getter(fn: Callable[[], Any]) -> None:
    global _span_context_getter
    _span_context_getter = fn


def set_record_writer(fn: Callable[[dict[str, Any], dict[str, Any] | None], bool]) -> None:
    global _record_writer
    _record_writer = fn


def get_current_span() -> object:
    if _span_context_getter is not None:
        return _span_context_getter()
    return None


def write_record(data: dict[str, Any], labels: dict[str, Any] | None = None) -> bool:
    if _record_writer is not None:
        return _record_writer(data, labels)
    return False
