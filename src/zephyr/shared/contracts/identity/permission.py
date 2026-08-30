# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.identity.permission
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.security.access_control.guards.permission_guard;zephyr.infrastructure.escalation;zephyr.governance;zephyr.integration.mcp
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 权限判定枚举不可扩展
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT]
# [TESTS] tests/test_agent_rbac.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: permission.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: GuardDecision, GuardResult
#   desc: 数据契约/异常/枚举声明共 2 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（2 类）
#   name_en: data classes
#   intro: GuardDecision, GuardResult
#   downstream: zephyr.security.access_control.guards.permission_guard;zephyr.infrastructure.es…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field
from enum import Enum


class GuardDecision(str, Enum):
    ALLOW = "ALLOW"
    AUTO_GUARD = "AUTO_GUARD"
    BLOCKED = "BLOCKED"


@dataclass
class GuardResult:
    # P1-3: 合并 security 版 permission_guard.py 的 target 字段（原 security 版独有）
    decision: GuardDecision = GuardDecision.ALLOW
    layer: str = ""
    reason: str = ""
    rule_id: str = ""
    target: str = ""
    audit_context: dict = field(default_factory=dict)
    timing_ns: int = 0
