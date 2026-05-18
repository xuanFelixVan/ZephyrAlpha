# [BLUEPRINT] MOD-INF-022 | docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md
# [MODULE] zephyr.escalation_engine
# [INVARIANTS] 升级裁决;四级约束;Kill Switch
# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md;src/zephyr/escalation_engine/__init__.py
# [CONSUMERS] MOD-INF-027;MOD-INF-020;MOD-INF-018
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] EscalationError;TimeoutError
# [TESTS] tests/test_escalation_engine/

from __future__ import annotations
from enum import Enum

class BrokerLevel(str, Enum):
    P0_PRIMARY = "P0"
    P1_FALLBACK = "P1"
    P2_EMERGENCY = "P2"

class BrokerFailure(str, Enum):
    API_LOST = "API_LOST"
    REJECT_ERROR = "REJECT_ERROR"
    GAP_FILL = "GAP_FILL"
    EXCHANGE_HALT = "EXCHANGE_HALT"

BROKER_FAILOVER: dict[BrokerLevel, str] = {
    BrokerLevel.P0_PRIMARY: "主API Primary",
    BrokerLevel.P1_FALLBACK: "自动故障转移 P1",
    BrokerLevel.P2_EMERGENCY: "应急平仓 only",
}

EMERGENCY_LIQUIDATION_STEPS: list[str] = [
    "检测P0故障>容忍(90sP0/120sP1)",
    "简报Owner(new pending L0+unique brief)",
    "P2 20% Exposure→每15min再降20%",
    "P0恢复→5min转P0 / 未恢复→Owner 3×Go/No-go",
]
