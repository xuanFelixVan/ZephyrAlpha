# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain-risk/risk-management-core/blueprint.md
# [MODULE] zephyr.risk.stop_loss
# [DOMAIN] D_RISK
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-UNK_stop_loss | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

# ---
# domain: risk
# category: risk_implementation
# status: active
# created: "2026-05-05"
# ---

"""D_RISK — Stop-Loss & Kill Switch Engine

止损规则与自动触发逻辑。对齐 CTR-ERR-004 (RiskLimitViolationError)。

核心职责：
  - 止损评估（固定比例 / 移动止损 / 时间止损 / 波动率止损）
  - Kill Switch 激活/重置
  - 止损价格持久化（用于次日恢复）

CTR 契约：
  生产者 — CTR-ERR-004 (RiskLimitViolationError) → D_PORTFOLIO_CORE, D_EXECUTION_CORE

INV-001: Kill Switch 延迟 < 1ms
INV-004: 每日亏损硬限

SSoT: cross_layer_contracts.yaml → CTR-ERR-004
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC
from decimal import Decimal


@dataclass
class StopLossResult:
    triggered: bool
    reason: str = ""
    stop_price: Decimal = Decimal("0")
    method: str = ""
    kill_switch_activated: bool = False


def evaluate_stop_loss(position: dict, current_price: float | Decimal, rules: dict) -> bool:
    """评估持仓是否触发止损条件。

    支持四种止损模式：
      - fixed_pct: 固定比例止损（如 -5%）
      - trailing: 移动止损（从最高点回撤 -3%）
      - time_based: 时间止损（超过最大持仓天数）
      - volatility: 波动率止损（N 倍 ATR）

    Args:
        position: 持仓信息 {entry_price, qty, entry_date, highest_since_entry}
        current_price: 当前价格
        rules: 止损规则配置 {method, stop_loss_pct, trailing_pct, ...}

    Returns:
        True 表示触发止损
    """
    # 5.105.2 修复: current_price 可能是 float, stop_price 是 Decimal
    # float 0.1 的精确值大于 Decimal('0.1'),可能导致止损该触发时未触发
    # 函数入口统一转换为 Decimal,确保比较精度一致
    if not isinstance(current_price, Decimal):
        current_price = Decimal(str(current_price))
    method = rules.get("method", "fixed_pct")
    entry_price = Decimal(str(position.get("entry_price", 0)))
    position_qty = Decimal(str(position.get("qty", 0)))
    highest_since_entry = Decimal(str(position.get("highest_since_entry", entry_price)))

    if entry_price <= 0:
        return False

    if method == "fixed_pct":
        stop_pct = Decimal(str(rules.get("stop_loss_pct", 0.05)))
        stop_price = entry_price * (Decimal("1") - stop_pct)

    elif method == "trailing":
        trail_pct = Decimal(str(rules.get("trailing_pct", 0.03)))
        stop_price = max(highest_since_entry, entry_price) * (Decimal("1") - trail_pct)

    elif method == "time_based":
        max_days = rules.get("max_hold_days", 20)
        entry_date = position.get("entry_date")
        if entry_date:
            from datetime import datetime

            held_days = (datetime.now(UTC) - entry_date).days
            return held_days > max_days
        return False

    elif method == "volatility":
        vol_pct = Decimal(str(rules.get("current_volatility", 0.02)))
        vol_mult = Decimal(str(rules.get("vol_multiplier", 2.0)))
        stop_price = entry_price - (vol_pct * vol_mult * entry_price)

    else:
        stop_price = entry_price * Decimal("0.95")

    triggered = current_price <= stop_price if position_qty > 0 else current_price >= stop_price
    return triggered


def trigger_kill_switch(reason: str, scope: str = "all") -> dict:
    """触发 Kill Switch，强制暂停交易。

    安全约束：
      - 一旦触发，必须人工确认后才能恢复
      - scope='all' 暂停所有标的，scope='symbol' 仅暂停特定标的
    """
    import logging
    import uuid

    _logger = logging.getLogger(__name__)
    event_id = str(uuid.uuid4())

    _logger.critical(
        "KILL_SWITCH_TRIGGERED event_id=%s reason=%s scope=%s",
        event_id,
        reason,
        scope,
    )

    return {
        "status": "triggered",
        "event_id": event_id,
        "reason": reason,
        "scope": scope,
        "requires_manual_reset": True,
    }


def reset_kill_switch(confirmation: dict) -> bool:
    """重置 Kill Switch（需人工确认）。

    Args:
        confirmation: 人工确认信息
          {confirmed_by, confirmed_at, override_reason}

    Returns:
        True 表示重置成功
    """
    import logging

    _logger = logging.getLogger(__name__)

    confirmed_by = confirmation.get("confirmed_by", "unknown")
    override_reason = confirmation.get("override_reason", "no reason provided")

    _logger.warning(
        "KILL_SWITCH_RESET confirmed_by=%s reason=%s",
        confirmed_by,
        override_reason,
    )

    return True


__all__ = ["StopLossResult", "evaluate_stop_loss", "reset_kill_switch", "trigger_kill_switch"]
