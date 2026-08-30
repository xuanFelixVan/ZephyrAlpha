# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] zephyr.infrastructure.a2a_protocol.phase_hold
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.__init__
# [CONSUMERS] zephyr.infrastructure.a2a_protocol
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Phase4Hold 状态转换必须合法; hold 释放必须通过验证门禁
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 agent_id 和 protocol_layer
# [TESTS] tests/test_a2a_protocol.py
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
[BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3

Phase 4 Hold — A2A Phase 4 锁定标记模块 与其他 Phase 3 模块不可并发施工.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: phase_hold.py
# 层: 算法
# - id: A1
#   name_zh: ① Phase4Hold
#   name_en: Phase4Hold
#   intro: A2A Phase 4 施工锁定.
#   desc: A2A Phase 4 施工锁定.；公共方法（定义序）: check, can_proceed；源码 L61-L77
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: Phase4Hold
#   downstream: zephyr.infrastructure.a2a_protocol
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

PHASE_HOLD_ACTIVE = True


PHASE_HOLD_REASON = "A2A module locked to Phase 4 — cannot be built concurrently with Phase 3 modules (Drift, Budget, Rollback, Escalation)"


class Phase4Hold:
    """A2A Phase 4 施工锁定."""

    def __init__(self) -> None:
        self.hold_active = PHASE_HOLD_ACTIVE

        self.hold_since = datetime.now(UTC).isoformat()

    def check(self) -> dict[str, Any]:
        return {
            "hold_active": self.hold_active,
            "reason": PHASE_HOLD_REASON,
            "hold_since": self.hold_since,
        }

    def can_proceed(self, current_phase: str) -> bool:
        return current_phase in ("Phase4", "phase4", "4") and self.hold_active
