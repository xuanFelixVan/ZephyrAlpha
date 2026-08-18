# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.governance.phase_hold
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.phase_hold
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 常量与基础逻辑单真源在 a2a_protocol.phase_hold；本模块仅派生扩展 is_hold_active
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Phase 4 Hold — governance 子包派生扩展（真源收敛）。

治本（AI-14 审计 R1-06）：本模块原与 ``a2a_protocol.phase_hold`` 全量重复定义
``PHASE_HOLD_ACTIVE``/``PHASE_HOLD_REASON``/``Phase4Hold``（双胞胎双真源，漂移温床）。
现收敛：常量与基础类唯一真源 = ``zephyr.infrastructure.a2a_protocol.phase_hold``，
本模块仅保留 governance 子包派生扩展（``is_hold_active`` 便捷判定），保持
``zephyr.infrastructure.a2a_protocol.governance.phase_hold`` 导入路径不变（向后兼容）。
"""

from __future__ import annotations

from typing import Final

from zephyr.infrastructure.a2a_protocol.phase_hold import (
    PHASE_HOLD_ACTIVE,
    PHASE_HOLD_REASON,
)
from zephyr.infrastructure.a2a_protocol.phase_hold import (
    Phase4Hold as _Phase4HoldBase,
)

__all__: Final = [
    "PHASE_HOLD_ACTIVE",
    "PHASE_HOLD_REASON",
    "Phase4Hold",
]


class Phase4Hold(_Phase4HoldBase):
    """A2A Phase 4 施工锁定（governance 子包派生扩展）。

    继承真源全部行为（check/can_proceed），新增 is_hold_active 便捷判定。
    """

    def is_hold_active(self) -> bool:
        return self.hold_active
