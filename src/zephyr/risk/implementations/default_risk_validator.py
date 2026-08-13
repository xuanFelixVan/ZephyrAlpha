# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain_risk/risk-management-core/blueprint.md
# [MODULE] zephyr.risk.implementations.default_risk_validator
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.risk_manager; zephyr.risk.risk_validator
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
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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
  生产者 — CTR-ERR-004 (RiskLimitViolationError) -> D_PORTFOLIO_CORE, D_EXECUTION_CORE

SSoT: cross_layer_contracts.yaml -> CTR-ERR-004 + CTR-003
"""

from __future__ import annotations

from decimal import Decimal

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
        limits: RiskLimits,
    ) -> list[ViolationDetail]:
        """对单笔订单做 pre-trade 风控校验。

        校验项：
        1. Kill Switch 激活时拒绝全部新订单（HALT）
        2. 单仓权重是否超限（HALT）
        3. 下单后总权重是否超限（HALT）

        Args:
            symbol: 标的代码
            target_weight: 目标权重（正=买入，负=卖出）
            current_holdings: 当前持仓权重字典
            limits: 风险限额配置

        Returns:
            违规列表，空列表表示通过
        """
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

        # 5.145 审查修复：limits: Any -> RiskLimits，消除 dict 双模式（死代码）
        override_limit = (limits.symbol_overrides or {}).get(symbol)
        effective_single = override_limit if override_limit is not None else limits.max_single_position

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
        limits: RiskLimits,
    ) -> list[ViolationDetail]:
        """对全组合做风控状态校验。

        校验项：
        1. 各标的持仓是否超单仓限额（HALT）
        2. 总杠杆是否超限（HALT）
        3. 组合回撤是否超限额（HALT）

        Args:
            holdings: symbol → weight 字典
            market_values: symbol → market_value 字典
            total_nav: 组合总净值
            limits: 风险限额配置

        Returns:
            违规列表，空列表表示通过
        """
        violations: list[ViolationDetail] = []

        # 5.145 审查修复：limits: Any -> RiskLimits，消除 dict 双模式（死代码）
        max_single = limits.max_single_position
        max_leverage = limits.max_gross_leverage
        max_sector = limits.max_sector_concentration
        drawdown_limit = limits.max_drawdown_limit

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
        """手动触发 kill switch（资金级熔断事件）。"""
        import logging

        _logger = logging.getLogger(__name__)
        _logger.critical("KILL_SWITCH_ACTIVATED validator=%s", self.__validator_id__)
        self._kill_switch_active = True

    def reset_kill_switch(self, confirmation: dict | None = None) -> None:
        """重置 kill switch（需人工确认后调用）。

        Args:
            confirmation: 确认信息字典，必须包含：
                - confirmed_by: 确认人
                - holdings_verified_zero: 持仓已清零确认（True/False）
        """
        import logging

        _logger = logging.getLogger(__name__)

        if confirmation is not None:
            confirmed_by = confirmation.get("confirmed_by", "unknown")
            holdings_verified_zero = confirmation.get("holdings_verified_zero", False)
            if not holdings_verified_zero:
                _logger.warning(
                    "KILL_SWITCH_RESET_GHOST_RISK confirmed_by=%s holdings_not_verified_zero",
                    confirmed_by,
                )
            _logger.warning(
                "KILL_SWITCH_RESET confirmed_by=%s holdings_verified_zero=%s",
                confirmed_by,
                holdings_verified_zero,
            )
        else:
            _logger.warning("KILL_SWITCH_RESET no confirmation provided")

        self._kill_switch_active = False

    def detect_ghost_positions(
        self,
        broker_holdings: dict[str, dict],
        strategy_state: dict[str, str],
    ) -> list[tuple[str, dict, str]]:
        """检测 Ghost Position（策略认为已平仓但 broker 仍持有的幽灵持仓）。

        两种 Ghost 情况：
        1. 策略侧某标的 CLOSED 但 broker 仍有该标的持仓
        2. Kill Switch 已激活但 broker 仍有任意持仓

        Args:
            broker_holdings: symbol → position_info 字典，broker 端实际持仓
                position_info 需包含 "qty" 字段
            strategy_state: symbol → "OPEN"/"CLOSED" 字典，策略侧持仓状态

        Returns:
            ghost_positions 列表，每项为 (symbol, position_info, ghost_type) 元组
        """
        ghosts: list[tuple[str, dict, str]] = []

        # 情况 1：策略侧 CLOSED 但 broker 有持仓
        for sym, pos in broker_holdings.items():
            qty = pos.get("qty", 0)
            if qty != 0 and strategy_state.get(sym) == "CLOSED":
                ghosts.append((sym, pos, "strategy_closed_but_broker_holds"))

        # 情况 2：Kill Switch 已激活但 broker 仍有任意持仓
        if self._kill_switch_active:
            for sym, pos in broker_holdings.items():
                qty = pos.get("qty", 0)
                if qty != 0:
                    # 避免重复（情况 1 已记录的标的不重复添加）
                    if not any(g[0] == sym for g in ghosts):
                        ghosts.append((sym, pos, "kill_switch_active_but_position_remains"))

        return ghosts

    @property
    def kill_switch_active(self) -> bool:
        return self._kill_switch_active


__all__ = ["DefaultRiskValidator"]
