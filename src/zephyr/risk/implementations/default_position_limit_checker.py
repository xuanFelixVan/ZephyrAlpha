# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain-risk/risk-management-core/blueprint.md
# [MODULE] zephyr.risk.implementations.default_position_limit_checker
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.risk_manager_base; zephyr.risk.risk_manager
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
# [A_module] module_id=MOD-UNK_default_position_limit_checker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: risk
# category: risk_implementation
# status: active
# created: "2026-05-05"
# ---

"""D_RISK — Default Position Limit Checker

仓位限额检查器具体实现。对齐 CTR-003 (RiskLimits)，输出 CTR-ERR-004 (RiskLimitViolationError)。

核心职责：
  - check_single_position: 单仓上限检查（max_single_position + symbol_overrides）
  - check_sector_concentration: 行业集中度检查（max_sector_concentration）
  - check_gross_leverage: 总杠杆检查（max_gross_leverage）

SSoT: cross_layer_contracts.yaml → CTR-003 + CTR-ERR-004
"""

from __future__ import annotations

from datetime import UTC, datetime

from zephyr.risk.risk_manager import RiskLimits
from zephyr.risk.risk_manager_base import (
    PositionLimitCheckerBase,
    RiskCheckResult,
)

__checker_id__ = "default-position-limit-checker"


class DefaultPositionLimitChecker(PositionLimitCheckerBase):
    """默认仓位限额检查器——单仓/行业/杠杆三项检查"""

    __checker_id__ = __checker_id__

    def check_single_position(self, symbol: str, weight: float, limit: float) -> RiskCheckResult:
        check_id = f"pos-{symbol}-{int(datetime.now(UTC).timestamp())}"
        override_limit = None
        if isinstance(limit, RiskLimits):
            override_limit = (limit.symbol_overrides or {}).get(symbol)
            effective_limit = override_limit if override_limit is not None else limit.max_single_position
        else:
            effective_limit = limit

        passed = weight <= effective_limit
        return RiskCheckResult(
            check_id=check_id,
            rule_name="single_position_limit",
            passed=passed,
            limit_value=effective_limit,
            actual_value=weight,
            message=f"symbol={symbol} weight={weight:.4f} limit={effective_limit:.4f} override={override_limit}",
            timestamp=datetime.now(UTC),
            severity="HALT" if not passed else "info",
        )

    def check_sector_concentration(self, sector: str, weight: float, limit: float) -> RiskCheckResult:
        check_id = f"sector-{sector}-{int(datetime.now(UTC).timestamp())}"
        effective_limit = limit.max_sector_concentration if isinstance(limit, RiskLimits) else limit
        passed = weight <= effective_limit
        return RiskCheckResult(
            check_id=check_id,
            rule_name="sector_concentration",
            passed=passed,
            limit_value=effective_limit,
            actual_value=weight,
            message=f"sector={sector} weight={weight:.4f} limit={effective_limit:.4f}",
            timestamp=datetime.now(UTC),
            severity="HALT" if not passed else "info",
        )

    def check_gross_leverage(self, current_leverage: float, limit: float) -> RiskCheckResult:
        check_id = f"lev-{int(datetime.now(UTC).timestamp())}"
        effective_limit = limit.max_gross_leverage if isinstance(limit, RiskLimits) else limit
        passed = current_leverage <= effective_limit
        return RiskCheckResult(
            check_id=check_id,
            rule_name="gross_leverage",
            passed=passed,
            limit_value=effective_limit,
            actual_value=current_leverage,
            message=f"leverage={current_leverage:.4f} limit={effective_limit:.4f}",
            timestamp=datetime.now(UTC),
            severity="HALT" if not passed else "info",
        )


__all__ = ["DefaultPositionLimitChecker"]
