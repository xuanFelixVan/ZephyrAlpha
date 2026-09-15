# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.risk.risk_validator_protocol
# [DOMAIN] D_TRADING
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] ViolationDetail is SSoT for cross-layer risk violation data; l04 re-exports from here
# [MODIFY-GUARD] Changes to ViolationDetail fields MUST sync with risk.risk_validator
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError on negative limit_value
# [TESTS] tests/trading/pipeline/test_l06_trade_execution.py  # 2026-09-05 STEWARD B20 重锚：AI-00 修复脚本 src. 前缀 bug 漏网（AST/patch 直查 1 个测试）
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW] external: docs/03_modules/_domain_trading/algo_flow/risk_validator_protocol.yaml
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    # 5.145.12 修复：limits: Any -> RiskLimits（SSoT: cross_layer_contracts.yaml CTR-003）
    # TYPE_CHECKING 导入避免运行期循环依赖；from __future__ import annotations 使注解惰性求值
    from zephyr.shared.contracts.risk_limits import RiskLimits


@dataclass(frozen=True)
class ViolationDetail:
    constraint: str
    description: str
    limit_value: Decimal
    actual_value: Decimal
    severity: str = "HALT"


@runtime_checkable
class RiskValidatorProtocol(Protocol):
    def validate_order(
        self,
        symbol: str,
        target_weight: float,
        current_holdings: dict[str, float],
        limits: RiskLimits,
    ) -> list[ViolationDetail]: ...

    def validate_portfolio(
        self,
        holdings: dict[str, float],
        market_values: dict[str, float],
        total_nav: Decimal,
        limits: RiskLimits,
    ) -> list[ViolationDetail]: ...


__all__ = ["RiskValidatorProtocol", "ViolationDetail"]
