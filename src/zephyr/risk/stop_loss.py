# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain-risk/risk-management-core/blueprint.md
# [MODULE] zephyr.risk.stop_loss
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.implementations.default_stop_loss_engine
# [CONSUMERS] tests/risk/test_l04_risk_management.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/risk/test_l04_risk_management.py
# [A_module] module_id=MOD-UNK_stop_loss | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: risk
# category: risk_interface
# status: active
# created: "2026-05-05"
# ---

"""D_RISK — Stop-Loss & Kill Switch 兼容层

止损评估逻辑已迁移至 zephyr.risk.implementations.default_stop_loss_engine（真源）。
本模块提供函数式兼容 API，委托给 DefaultStopLossEngine。

trigger_kill_switch / reset_kill_switch 为事件记录层（日志+返回事件 dict），
状态管理由 DefaultRiskValidator.trigger_kill_switch/reset_kill_switch 负责。

SSoT: zephyr.risk.implementations.default_stop_loss_engine
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from zephyr.risk.implementations.default_stop_loss_engine import DefaultStopLossEngine


@dataclass
class StopLossResult:
    triggered: bool
    reason: str = ""
    stop_price: Decimal = Decimal("0")
    method: str = ""
    kill_switch_activated: bool = False


_engine = DefaultStopLossEngine()


def evaluate_stop_loss(position: dict, current_price: float | Decimal, rules: dict) -> bool:
    """评估持仓是否触发止损条件（兼容函数，委托给 DefaultStopLossEngine）。

    支持 fixed_pct / trailing / time_based / volatility 四种模式。
    """
    if not isinstance(current_price, Decimal):
        current_price = Decimal(str(current_price))
    entry_price = Decimal(str(position.get("entry_price", 0)))
    position_qty = Decimal(str(position.get("qty", 1)))
    symbol = position.get("symbol", "UNKNOWN")

    if "entry_date" not in rules and "entry_date" in position:
        rules = {**rules, "entry_date": position["entry_date"]}
    if "highest_since_entry" not in rules and "highest_since_entry" in position:
        rules = {**rules, "highest_since_entry": position["highest_since_entry"]}

    result = _engine.evaluate(symbol, entry_price, current_price, position_qty, rules)
    return not result.passed


def trigger_kill_switch(reason: str, scope: str = "all") -> dict:
    """触发 Kill Switch 事件记录（日志+返回事件 dict）。

    注意：本函数仅记录事件，不管理状态。
    状态管理由 DefaultRiskValidator.trigger_kill_switch() 负责。
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
    """重置 Kill Switch 事件记录（需人工确认）。

    注意：本函数仅记录重置事件，不管理状态。
    状态管理由 DefaultRiskValidator.reset_kill_switch() 负责。
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
