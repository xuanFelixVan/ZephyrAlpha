# [BLUEPRINT] SRC-050 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.lifecycle_governance.post_live_verification
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.lifecycle_governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_post_live_verification | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class PLVCheck(str, Enum):
    ORDER_COUNT_DEVIATION = "order_count_deviation"
    FILL_RATE_COMPARISON = "fill_rate_comparison"
    RISK_CONFORMANCE = "risk_conformance"
    DATA_INTEGRITY = "data_integrity"
    PNL_RECONCILIATION = "pnl_reconciliation"


class PLVSpec(BaseModel):
    check: PLVCheck
    label: str
    threshold: str
    description: str


PLV_CHECKS: dict[PLVCheck, PLVSpec] = {
    PLVCheck.ORDER_COUNT_DEVIATION: PLVSpec(
        check=PLVCheck.ORDER_COUNT_DEVIATION,
        label="Paper vs Live 订单偏差",
        threshold="±1%",
        description="比较 paper 模拟与 live 实际订单量差异",
    ),
    PLVCheck.FILL_RATE_COMPARISON: PLVSpec(
        check=PLVCheck.FILL_RATE_COMPARISON,
        label="成交率 T+1 vs T-1",
        threshold="±0.5%",
        description="比较今天与昨天的 FillRate/Slippage",
    ),
    PLVCheck.RISK_CONFORMANCE: PLVSpec(
        check=PLVCheck.RISK_CONFORMANCE,
        label="风控合规",
        threshold="≥limits",
        description="是否所有风险限额均未超限",
    ),
    PLVCheck.DATA_INTEGRITY: PLVSpec(
        check=PLVCheck.DATA_INTEGRITY,
        label="数据完整性校验",
        threshold="checksum verified",
        description="核对 MD5/SHA256 checksum 消息完整性",
    ),
    PLVCheck.PNL_RECONCILIATION: PLVSpec(
        check=PLVCheck.PNL_RECONCILIATION,
        label="仓位与PnL对账",
        threshold="±$5/1000trades",
        description="position + PnL reconciliation 对账阈值",
    ),
}


def get_plv_spec(check: PLVCheck) -> PLVSpec | None:
    return PLV_CHECKS.get(check)


PLV_CHECK_COUNT: int = 5
