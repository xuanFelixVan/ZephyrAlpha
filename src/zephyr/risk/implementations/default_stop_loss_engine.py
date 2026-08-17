# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain_risk/risk-management-core/blueprint.md
# [MODULE] zephyr.risk.implementations.default_stop_loss_engine
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.risk_manager_base
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 多头-only契约(position_qty<=0抛ValueError); trailing高水位按symbol隔离
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(position_qty<=0——A股通道禁做空,拒绝静默误触发)
# [TESTS]
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: risk
# category: risk_implementation
# status: active
# created: "2026-05-05"
# ---

"""D_RISK — Default Stop-Loss Engine

止损策略引擎具体实现。支持四种止损模式（多头-only：A 股通道禁做空
——43_compliance_discipline §6 硬边界 FORBIDDEN，position_qty<=0 fail-closed
抛 ValueError，杜绝空头分支静默误触发；trailing 高水位按 symbol 隔离）。

CTR 契约：
  - 消费者：CTR-006 (PositionSnapshot) ← D_EXECUTION_CORE
  - 生产者：CTR-ERR-004 (RiskLimitViolationError) -> D_PORTFOLIO_CORE, D_EXECUTION_CORE

SSoT: cross_layer_contracts.yaml -> CTR-ERR-004 + CTR-006
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from zephyr.risk.risk_manager_base import (
    RiskCheckResult,
    StopLossEngineBase,
)


@dataclass
class StopLossRules:
    """止损规则配置"""

    method: str = "fixed_pct"  # fixed_pct | trailing | time_based | volatility
    stop_loss_pct: float = 0.05  # 固定比例止损线（如 0.05 = 5%）
    trailing_pct: float = 0.03  # 移动止损回撤比例
    max_hold_days: int = 20  # 时间止损最大持仓天数
    vol_multiplier: float = 2.0  # 波动率止损的倍数（如 2x ATR）
    lookback_days: int = 14  # 波动率计算回溯窗口
    entry_date: datetime | None = None
    highest_price_since_entry: Decimal | None = None


__checker_id__ = "default-stop-loss-engine"


class DefaultStopLossEngine(StopLossEngineBase):
    """默认止损策略引擎——支持固定比例/移动/时间/波动率四种止损"""

    __checker_id__ = __checker_id__

    def __init__(self, rules: StopLossRules | None = None):
        self._rules = rules or StopLossRules()
        self._stop_prices: dict[str, Decimal] = {}
        # trailing 高水位按 symbol 隔离（引擎级共享会跨标的串扰止损价）
        self._highest_since_entry: dict[str, Decimal] = {}

    def evaluate(
        self,
        symbol: str,
        entry_price: Decimal,
        current_price: Decimal,
        position_qty: Decimal,
        rules: dict[str, Any],
    ) -> RiskCheckResult:
        # Fail-Closed 多头-only 契约：A 股通道禁做空（43 号 §6 硬边界 FORBIDDEN），
        # 空头/零仓求值属上游契约错误——显式拒绝，杜绝"看似支持空头实则方向算反"
        # 的静默误触发（stop 价在 entry 下方配 current>=stop → 入场即熔断）。
        if position_qty <= 0:
            raise ValueError(
                f"position_qty 必须 > 0（多头-only 契约，A 股通道禁做空），当前值: {position_qty}"
            )
        check_id = f"sl-{symbol}-{int(datetime.now(UTC).timestamp())}"
        method = rules.get("method", self._rules.method)

        if method == "time_based":
            triggered = self._check_time_based(rules)
            stop_price = Decimal("0")
        else:
            stop_price = self._compute_stop_price(symbol, entry_price, current_price, method, rules)
            triggered = current_price <= stop_price
        self._stop_prices[symbol] = stop_price

        if entry_price > 0:
            pnl_pct = float((current_price - entry_price) / entry_price)
        else:
            pnl_pct = 0.0

        return RiskCheckResult(
            check_id=check_id,
            rule_name=f"stop_loss_{method}",
            passed=not triggered,
            limit_value=float(stop_price),
            actual_value=float(current_price),
            message=f"symbol={symbol} entry={entry_price} current={current_price} stop={stop_price} pnl={pnl_pct:.4%} method={method}",
            timestamp=datetime.now(UTC),
            severity="HALT" if triggered else "info",
        )

    def get_stop_price(self, symbol: str) -> Decimal | None:
        return self._stop_prices.get(symbol)

    def _check_time_based(self, rules: dict[str, Any]) -> bool:
        """时间止损：持仓超过 max_hold_days 即触发.

        entry_date 优先从 rules 取，其次取 StopLossRules.entry_date。
        """
        max_days = rules.get("max_hold_days", self._rules.max_hold_days)
        entry_date = rules.get("entry_date", self._rules.entry_date)
        if entry_date is None:
            return False
        if isinstance(entry_date, str):
            entry_date = datetime.fromisoformat(entry_date)
        if entry_date.tzinfo is None:
            # naive ISO 字符串按 UTC 解释（避免 aware-naive 相减 TypeError）
            entry_date = entry_date.replace(tzinfo=UTC)
        held_days = (datetime.now(UTC) - entry_date).days
        return held_days > max_days

    def _compute_stop_price(
        self,
        symbol: str,
        entry_price: Decimal,
        current_price: Decimal,
        method: str,
        rules: dict[str, Any],
    ) -> Decimal:
        if method == "fixed_pct":
            stop_pct = Decimal(str(rules.get("stop_loss_pct", self._rules.stop_loss_pct)))
            return entry_price * (Decimal("1") - stop_pct)

        if method == "trailing":
            trail_pct = Decimal(str(rules.get("trailing_pct", self._rules.trailing_pct)))
            highest_from_rules = rules.get("highest_since_entry")
            if highest_from_rules is not None:
                highest = Decimal(str(highest_from_rules))
            else:
                # 按 symbol 隔离高水位（多标的共用引擎时互不串扰）
                highest = max(
                    self._highest_since_entry.get(symbol, current_price),
                    current_price,
                )
            self._highest_since_entry[symbol] = highest
            return highest * (Decimal("1") - trail_pct)

        if method == "volatility":
            vol = Decimal(str(rules.get("current_volatility", 0.02)))
            mult = Decimal(str(rules.get("vol_multiplier", self._rules.vol_multiplier)))
            return entry_price - (vol * mult * entry_price)

        return entry_price * Decimal("0.95")  # fallback 5% fixed


__all__ = ["DefaultStopLossEngine", "StopLossRules"]
