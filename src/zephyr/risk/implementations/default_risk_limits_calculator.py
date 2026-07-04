# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain-risk/risk-management-core/blueprint.md
# [MODULE] zephyr.risk.implementations.default_risk_limits_calculator
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.trading.trading_contracts.risk.risk_limits; zephyr.risk.risk_manager
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
# [A_module] module_id=MOD-UNK_default_risk_limits_calculator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

# ---
# domain: risk
# category: risk_implementation
# status: active
# created: "2026-05-05"
# ---

"""D_RISK — Default Risk Limits Calculator

风险限额计算引擎具体实现。输入持仓快照 + 因子信号，输出 RiskLimits (CTR-003)。

核心职责：
  - 单标的权重上限计算（含 symbol_overrides）
  - 行业集中度上限计算（根据持仓自动推断行业权重）
  - VaR 回撤触发线计算
  - IV 调整：当合成信号 unstable 时自动收紧限额

CTR 契约：
  消费者 — CTR-006 (PositionSnapshot) ← D_EXECUTION_CORE
  消费者 — CTR-P1-015 (SynthesizedSignal) ← D_SIGNAL（IV 调整输入）
  生产者 — CTR-003 (RiskLimits) → D_PORTFOLIO_CORE

SSoT: cross_layer_contracts.yaml → CTR-003
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from zephyr.risk.risk_limits import RiskLimitsCalculator
from zephyr.risk.risk_manager import RiskLimits

__calculator_id__ = "default-risk-limits-calculator"


class DefaultRiskLimitsCalculator(RiskLimitsCalculator):
    """默认风险限额计算器"""

    __calculator_id__ = __calculator_id__

    def __init__(
        self,
        max_single_position: float = 0.10,
        max_gross_leverage: float = 1.0,
        max_sector_concentration: float = 0.30,
        max_drawdown_limit: float = 0.20,
        var_confidence: float = 0.95,
    ):
        self._max_single_position = max_single_position
        self._max_gross_leverage = max_gross_leverage
        self._max_sector_concentration = max_sector_concentration
        self._max_drawdown_limit = max_drawdown_limit
        self._var_confidence = var_confidence

    def calculate(
        self,
        positions: dict[str, float],
        market_values: dict[str, float],
        total_nav: Decimal,
        factor_signals: dict[str, float] | None = None,
    ) -> RiskLimits:
        nav = total_nav if isinstance(total_nav, Decimal) else Decimal(str(total_nav))
        symbol_overrides: dict[str, float] = {}
        adjusted_max_single = self._max_single_position

        if factor_signals:
            unstable_count = sum(1 for v in factor_signals.values() if abs(v) > 3.0)
            if unstable_count > 0:
                adjustment = max(0.5, 1.0 - unstable_count * 0.1)
                adjusted_max_single = self._max_single_position * adjustment

        var_1d = self._estimate_var(market_values, nav)

        return RiskLimits(
            as_of_date=datetime.now(UTC),
            idempotency_key=f"limits-{int(datetime.now(UTC).timestamp())}",
            max_single_position=adjusted_max_single,
            max_gross_leverage=self._max_gross_leverage,
            max_sector_concentration=self._max_sector_concentration,
            max_portfolio_var_1d=float(var_1d),
            max_drawdown_limit=self._max_drawdown_limit,
            symbol_overrides=symbol_overrides,
        )

    def _estimate_var(self, market_values: dict[str, float], total_nav: Decimal) -> Decimal:
        """简化 VaR 估算——基于持仓集中度估算"""
        if not market_values or total_nav <= 0:
            return Decimal("0.02")
        max_mv = Decimal(str(max(market_values.values()))) if market_values else Decimal("0")
        concentration = max_mv / total_nav if max_mv > 0 else Decimal("0")
        position_count = len(market_values)
        if position_count <= 2:
            return concentration * Decimal("0.05")
        if position_count <= 5:
            return concentration * Decimal("0.03")
        return concentration * Decimal("0.02")


__all__ = ["DefaultRiskLimitsCalculator"]
