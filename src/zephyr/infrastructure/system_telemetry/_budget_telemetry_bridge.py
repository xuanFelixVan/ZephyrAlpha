# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] zephyr.infrastructure.system_telemetry._budget_telemetry_bridge
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.system_telemetry.__init__
# [CONSUMERS] zephyr.infrastructure.budget_enforcement.budget_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] callback must be set before first use; getter returns None if unset
# [MODIFY-GUARD] auto_bootstrap.py; budget_engine.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None return when unset
# [TESTS] tests/system-telemetry/test_budget_telemetry_bridge.py
# [A_module] module_id=MOD-INF-015 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: getter 参数
#   fields: 参数 getter，类型注解 Callable[[], Any]
#   code: _budget_telemetry_bridge.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① set_telemetry_getter
#   name_en: set_telemetry_getter
#   intro: set_telemetry_getter(getter) 源码 L65-L67
#   desc: 源码 L65-L67
#   inputs: getter
#   outputs: 返回值
# - id: A2
#   name_zh: ② get_telemetry
#   name_en: get_telemetry
#   intro: get_telemetry() 源码 L70-L73
#   desc: 源码 L70-L73
#   inputs: 无参数
#   outputs: object
# 层: 输出
# - id: O1
#   name_zh: object
#   name_en: object
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.infrastructure.budget_enforcement.budget_engine
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

_telemetry_getter: Callable[[], Any] | None = None
telemetry_getter = _telemetry_getter  # public alias（Stage 4 公共化）


def set_telemetry_getter(getter: Callable[[], Any]) -> None:
    global _telemetry_getter
    _telemetry_getter = getter


def get_telemetry() -> object:
    if _telemetry_getter is not None:
        return _telemetry_getter()
    return None
