# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.scope_creep_monitor
# [DOMAIN] D_FBL_VERIFICATION
# [DEPENDENCIES] zephyr.feedback_loop.gates.__init__
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
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Scope Creep Monitor — v0.15.0 R220

Blindspot: Autonomous repairs grow in scope over time; permission boundaries drift.
Risk: R220 — L2 repair slowly grows to L4 scope; autonomy level silently escalates.

Mitigation: Permission boundary tracking; alert when repair scope exceeds authorized level.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: scope_creep_monitor.py
# 层: 算法
# - id: A1
#   name_zh: ① ScopeCreepMonitor
#   name_en: ScopeCreepMonitor
#   intro: class ScopeCreepMonitor 源码 L68-L78
#   desc: 公共方法（定义序）: audit, violation_count；源码 L68-L78
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ScopeCreepMonitor
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ScopeEvent:
    action_id: str
    authorized_level: int
    actual_scope: int
    timestamp: str = ""


@dataclass
class ScopeCreepMonitor:
    events: list[ScopeEvent] = field(default_factory=list)
    max_tolerance: int = 1

    def audit(self, action_id: str, authorized_level: int, actual_scope: int) -> bool:
        event = ScopeEvent(action_id=action_id, authorized_level=authorized_level, actual_scope=actual_scope)
        self.events.append(event)
        return actual_scope <= authorized_level + self.max_tolerance

    def violation_count(self) -> int:
        return sum(1 for e in self.events if e.actual_scope > e.authorized_level + self.max_tolerance)
