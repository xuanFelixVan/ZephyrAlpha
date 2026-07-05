# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.resilience_governance.broker_resilience
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] MOD-INF-027;MOD-INF-020;MOD-INF-018
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 升级裁决;四级约束;Kill Switch
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md;src/zephyr/escalation-engine/__init__.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] EscalationError;TimeoutError
# [TESTS] tests/test_escalation_engine/
# [A_module] module_id=MOD-RES_broker_resilience | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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
