# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain-risk/risk-management-core/blueprint.md
# [MODULE] zephyr.risk.implementations.default_risk_validator
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.risk_manager; zephyr.risk.risk_validator
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_default_risk_validator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

# ---
# domain: risk
# category: risk_implementation
# status: active
# created: "2026-05-05"
# ---

"""D_RISK — Default Risk Validator

风险校验器具体实现。Pre-trade 订单校验 + 全组合风控状态校验。

CTR 契约：
  消费者 — CTR-003 (RiskLimits) ← 本层
  消费者 — CTR-006 (PositionSnapshot) ← D_EXECUTION_CORE
  生产者 — CTR-ERR-004 (RiskLimitViolationError) → D_PORTFOLIO_CORE, D_EXECUTION_CORE

SSoT: cross_layer_contracts.yaml → CTR-ERR-004 + CTR-003
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from zephyr.risk.risk_manager import (
    RiskLimits,
)
from zephyr.risk.risk_validator import (
    RiskValidator,
    ViolatedConstraint,
    ViolationDetail,
)

__validator_id__ = "default-risk-validator"


class DefaultRiskValidator(RiskValidator):
    """默认风险校验器——Pre-trade + Portfolio 校验"""

    __validator_id__ = __validator_id__

    def __init__(self, kill_switch_active: bool = False):
        self._kill_switch_active = kill_switch_active
        self._violation_history: list[ViolationDetail] = []

    def validate_order(
        self,
        symbol: str,
        target_weight: float,
        current_holdings: dict[str, float],
        limits: Any,
    ) -> list[ViolationDetail]:
        violations: list[ViolationDetail] = []

        if self._kill_switch_active:
            violations.append(
                ViolationDetail(
                    constraint=ViolatedConstraint.DRAWDOWN_TRIGGER,
                    description="Kill switch 已激活，拒绝所有新订单",
                    limit_value=0.0,
                    actual_value=target_weight,
                    severity="HALT",
                )
            )
            self._violation_history.extend(violations)
            return violations

        if isinstance(limits, RiskLimits):
            override_limit = (limits.symbol_overrides or {}).get(symbol)
            effective_single = override_limit if override_limit is not None else limits.max_single_position
        else:
            effective_single = float(limits.get("max_single_position", 0.10))

        if abs(target_weight) > effective_single:
            violations.append(
                ViolationDetail(
                    constraint=ViolatedConstraint.POSITION_LIMIT,
                    description=f"单仓权重超限: {symbol} target={target_weight:.4f} limit={effective_single:.4f}",
                    limit_value=effective_single,
                    actual_value=abs(target_weight),
                    severity="HALT",
                )
            )

        post_trade_weight = Decimal(str(current_holdings.get(symbol, 0.0))) + Decimal(str(target_weight))
        if abs(post_trade_weight) > effective_single * 1.05:
            violations.append(
                ViolationDetail(
                    constraint=ViolatedConstraint.POSITION_LIMIT,
                    description=f"下单后总权重超限: {symbol} post_trade={post_trade_weight:.4f}",
                    limit_value=effective_single,
                    actual_value=abs(post_trade_weight),
                    severity="HALT",
                )
            )

        self._violation_history.extend(violations)
        return violations

    def validate_portfolio(
        self,
        holdings: dict[str, float],
        market_values: dict[str, float],
        total_nav: Decimal,
        limits: Any,
    ) -> list[ViolationDetail]:
        violations: list[ViolationDetail] = []

        if isinstance(limits, RiskLimits):
            max_single = limits.max_single_position
            max_leverage = limits.max_gross_leverage
            max_sector = limits.max_sector_concentration
            drawdown_limit = limits.max_drawdown_limit
        else:
            max_single = limits.get("max_single_position", 0.10)
            max_leverage = limits.get("max_gross_leverage", 1.0)
            max_sector = limits.get("max_sector_concentration", 0.30)
            drawdown_limit = limits.get("max_drawdown_limit", 0.20)

        for symbol, weight in holdings.items():
            if abs(weight) > max_single:
                violations.append(
                    ViolationDetail(
                        constraint=ViolatedConstraint.POSITION_LIMIT,
                        description=f"持仓超限: {symbol} weight={weight:.4f} limit={max_single:.4f}",
                        limit_value=max_single,
                        actual_value=abs(weight),
                        severity="HALT",
                    )
                )

        gross_leverage = sum(abs(w) for w in holdings.values())
        if gross_leverage > max_leverage:
            violations.append(
                ViolationDetail(
                    constraint=ViolatedConstraint.LEVERAGE_LIMIT,
                    description=f"总杠杆超限: {gross_leverage:.4f} > {max_leverage:.4f}",
                    limit_value=max_leverage,
                    actual_value=gross_leverage,
                    severity="HALT",
                )
            )

        if drawdown_limit and drawdown_limit > 0:
            total_mv = sum(market_values.values())
            if total_nav > 0:
                total_mv_dec = Decimal(str(total_mv))
                nav_dec = Decimal(str(total_nav)) if isinstance(total_nav, float) else total_nav
                dd_from_peak = Decimal("1") - total_mv_dec / nav_dec
                # 5.105.1 修复: drawdown_limit 可能是 float, Decimal > float 在 Python 3 抛 TypeError
                # 或精度差异(float 0.2 的精确 Decimal 表示略大于 0.2)导致回撤达阈值时违规未触发
                dd_limit_dec = Decimal(str(drawdown_limit)) if not isinstance(drawdown_limit, Decimal) else drawdown_limit
                if dd_from_peak > dd_limit_dec:
                    violations.append(
                        ViolationDetail(
                            constraint=ViolatedConstraint.DRAWDOWN_TRIGGER,
                            description=f"回撤触发: {float(dd_from_peak):.4%} > {drawdown_limit:.4%}",
                            limit_value=drawdown_limit,
                            actual_value=float(dd_from_peak),
                            severity="HALT",
                        )
                    )

        self._violation_history.extend(violations)
        return violations

    def trigger_kill_switch(self) -> None:
        """手动触发 kill switch"""
        self._kill_switch_active = True

    def reset_kill_switch(self) -> None:
        """重置 kill switch（需人工确认后调用）"""
        self._kill_switch_active = False

    @property
    def kill_switch_active(self) -> bool:
        return self._kill_switch_active


__all__ = ["DefaultRiskValidator"]
