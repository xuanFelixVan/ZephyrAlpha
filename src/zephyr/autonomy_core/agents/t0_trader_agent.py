# [BLUEPRINT] MOD-AU-011 | docs/03_modules/_domain_autonomy_core/t0_trader_agent/blueprint.md
# [MODULE] zephyr.autonomy_core.agents.t0_trader_agent
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 运行时装配批（做T 信号实时接入 / t1_sellable 可卖装配 / 风控校验链 / C-012 管线）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] decide 纯函数无IO; ctx/配置非法 Fail-Closed; 底仓不变硬约束（卖出腿≤可卖，截断留痕）; 建议永远 requires_risk_check=True 且无下单语义（执行委托 C-012 管线）; EXECUTE 必发风控前置+执行外发并双审计; 回调/sink 异常不阻断判定
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_core/t0_trader_agent/blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] InvalidT0ContextError; InvalidT0ConstraintsError
# [TESTS] tests/autonomy/test_t0_trader_agent.py
# [A_module] module_id=MOD-AU-011 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""T0TraderAgent — 做T Agent (MOD-AU-011)

B1-00244（AUD-DRAFT-001-DIGEST P1 波 W-P1-11）：T0Trader 角色卡（14号文
§3.0 role façade 族卡模式，与 MOD-AU-007~010 同族）。做T 信号即时裁决
编排：**底仓不变硬约束** + **T+1 可卖校验**（t1_sellable 口径：卖出腿量
≤ 可卖底仓，当日买入不可卖）+ 单笔价差（min_edge_bp）与当日次数限额 →
EXECUTE/SKIP/REJECT 建议；建议**经风控校验后生效**
（risk_check_trigger），执行委托 C-012 管线（execution_sink，本 Agent
不产生任何生效指令、无下单语义）。

查重分工：信号源归 MOD-SIG-068；做T 计划生成归 MOD-SELL-018；底仓/T+1
可卖真源归 MOD-POS-018/t1_sellable；本角色只做即时裁决编排。
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "AGENT_CARD",
    "ROLE",
    "InvalidT0ConstraintsError",
    "InvalidT0ContextError",
    "T0Advice",
    "T0Constraints",
    "T0Context",
    "T0Decision",
    "T0TraderAction",
    "T0TraderAgent",
]

ROLE: Final[str] = "t0_trader"

_VALID_T0: Final[frozenset[str]] = frozenset({"T买", "T卖"})

AGENT_CARD: Final[dict[str, Any]] = {
    "role": ROLE,
    "capabilities": [
        {
            "id": "t0_decision",
            "name": "做T 信号即时裁决（底仓硬约束 + T+1 可卖 + 价差/次数限额）",
            "inputs": "T0Context（信号 + 底仓/可卖 + 价差 + 当日次数装配注入）",
            "outputs": "T0Advice（EXECUTE/SKIP/REJECT，requires_risk_check 恒真）",
            "autonomyLevel": "L1_suggest",
        },
        {
            "id": "execution_handoff",
            "name": "执行外发（风控前置信号 + C-012 管线委托）",
            "inputs": "T0Advice.decision = EXECUTE",
            "outputs": "risk_check_trigger + execution_sink 回调（执行委托 C-012 管线）",
            "autonomyLevel": "L2_approval",
        },
    ],
    "autonomyBoundaries": {
        "ai_modifiable": ["裁决理由文本", "建议量截断说明"],
        "human_gated": ["EXECUTE 建议经风控校验后生效（风控前置信号）"],
        "immutable": ["底仓不变硬约束（买回=卖出，日终仓位复原）", "T+1 可卖校验本体（t1_sellable/MOD-POS-018）", "下单/交易执行（C-012 管线职责，本角色无下单语义）"],
    },
    "healthCheck": {"heartbeat": "on_demand_decide"},
}


class InvalidT0ContextError(ZephyrBaseError):
    """做T 上下文非法（Fail-Closed：不评估脏输入）。"""


class InvalidT0ConstraintsError(ZephyrBaseError):
    """T0Trader 约束配置非法。"""


class T0Decision(str, Enum):
    """做T 裁决。"""

    EXECUTE = "EXECUTE"
    SKIP = "SKIP"
    REJECT = "REJECT"


@dataclass(frozen=True)
class T0Context:
    """做T 上下文（由调用方从信号/底仓/可卖/价差/次数真源装配注入）。"""

    symbol: str
    base_position: int  # 底仓股数（非负）
    sellable_qty: int  # T+1 可卖股数（非负）
    t0_signal: str | None  # 做T 信号：T买/T卖/None
    expected_edge_bp: float  # 预期净价差（基点，非负）
    trades_done_today: int  # 当日已做T 次数（非负）
    proposed_qty: int  # 申请腿量（正）

    def __post_init__(self) -> None:
        if not self.symbol or not self.symbol.strip():
            raise InvalidT0ContextError("symbol 不能为空")
        if self.base_position < 0:
            raise InvalidT0ContextError(f"base_position 不能为负: {self.base_position}")
        if self.sellable_qty < 0:
            raise InvalidT0ContextError(f"sellable_qty 不能为负: {self.sellable_qty}")
        if self.t0_signal is not None and self.t0_signal not in _VALID_T0:
            raise InvalidT0ContextError(f"t0_signal 必须 ∈ {{T买, T卖, None}}: {self.t0_signal!r}")
        if self.expected_edge_bp < 0:
            raise InvalidT0ContextError(f"expected_edge_bp 不能为负: {self.expected_edge_bp}")
        if self.trades_done_today < 0:
            raise InvalidT0ContextError(f"trades_done_today 不能为负: {self.trades_done_today}")
        if self.proposed_qty <= 0:
            raise InvalidT0ContextError(f"proposed_qty 必须为正: {self.proposed_qty}")


@dataclass(frozen=True)
class T0Constraints:
    """做T 约束配置（C 类可调参数）。"""

    min_edge_bp: float = 30.0  # 单笔最小净价差（基点，低于不做）
    max_trades_per_day: int = 3  # 当日次数限额
    max_qty_per_leg: int = 10000  # 单笔腿量上限

    def __post_init__(self) -> None:
        if self.min_edge_bp <= 0:
            raise InvalidT0ConstraintsError(f"min_edge_bp 必须为正: {self.min_edge_bp}")
        if self.max_trades_per_day <= 0:
            raise InvalidT0ConstraintsError(f"max_trades_per_day 必须为正: {self.max_trades_per_day}")
        if self.max_qty_per_leg <= 0:
            raise InvalidT0ConstraintsError(f"max_qty_per_leg 必须为正: {self.max_qty_per_leg}")


@dataclass(frozen=True)
class T0Advice:
    """做T 建议（不可变；经风控校验后生效）。"""

    decision: T0Decision
    direction: str | None  # EXECUTE 时 = t0_signal
    suggested_qty: int | None  # EXECUTE 时 = 截断后腿量
    reasons: tuple[str, ...]
    requires_risk_check: bool = True


@dataclass(frozen=True)
class T0TraderAction:
    """act 编排结果：裁决 + 风控前置 + 执行外发 + 双审计记录。"""

    advice: T0Advice
    risk_check_signaled: bool
    execution_handed_off: bool
    audit_records: tuple[dict[str, Any], ...]


class T0TraderAgent:
    """做T Agent：信号×底仓×可卖×限额 → 即时裁决（判定核心纯函数）。

    Args:
        constraints: 做T 约束配置。
        risk_check_trigger: 风控前置信号回调；异常不阻断，如实记 False。
        execution_sink: 执行外发回调（委托 C-012 管线）；异常不阻断，如实记 False。
        audit_sink: 审计记录回调；异常不阻断（记录仍内嵌 action.audit_records）。
    """

    ROLE: Final[str] = ROLE
    AGENT_CARD: Final[dict[str, Any]] = AGENT_CARD

    def __init__(
        self,
        constraints: T0Constraints | None = None,
        risk_check_trigger: Callable[[dict[str, Any]], None] | None = None,
        execution_sink: Callable[[dict[str, Any]], None] | None = None,
        audit_sink: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self._constraints = constraints or T0Constraints()
        self._risk_check_trigger = risk_check_trigger
        self._execution_sink = execution_sink
        self._audit_sink = audit_sink

    # ── 判定阶梯（纯函数） ──────────────────────────────────────────────────

    def decide(self, ctx: T0Context) -> T0Advice:
        """确定性阶梯：无信号 → 次数限额 → 价差不足 → 无可卖 REJECT → EXECUTE（截断留痕）。"""
        c = self._constraints
        if ctx.t0_signal is None:
            return T0Advice(
                decision=T0Decision.SKIP,
                direction=None,
                suggested_qty=None,
                reasons=("无做T 信号，不做",),
            )
        if ctx.trades_done_today >= c.max_trades_per_day:
            return T0Advice(
                decision=T0Decision.SKIP,
                direction=None,
                suggested_qty=None,
                reasons=(f"当日已做T {ctx.trades_done_today} 次 ≥ 次数限额 {c.max_trades_per_day}（次数限额，不做）",),
            )
        if ctx.expected_edge_bp < c.min_edge_bp:
            return T0Advice(
                decision=T0Decision.SKIP,
                direction=None,
                suggested_qty=None,
                reasons=(
                    f"预期净价差 {ctx.expected_edge_bp:.1f}bp < 最小价差 {c.min_edge_bp:.1f}bp（不值得做的T不做）",
                ),
            )
        if ctx.t0_signal == "T卖" and ctx.sellable_qty <= 0:
            return T0Advice(
                decision=T0Decision.REJECT,
                direction="T卖",
                suggested_qty=None,
                reasons=("T+1 硬约束：无可卖底仓（当日买入不可卖），卖出腿不可执行",),
            )
        # EXECUTE：卖出腿吃 T+1 可卖约束，双腿吃腿量上限；截断留痕
        cap = c.max_qty_per_leg if ctx.t0_signal == "T买" else min(c.max_qty_per_leg, ctx.sellable_qty)
        qty = min(ctx.proposed_qty, cap)
        reasons: list[str] = [
            f"信号 {ctx.t0_signal} 且净价差 {ctx.expected_edge_bp:.1f}bp 达标（≥{c.min_edge_bp:.1f}bp）",
            "底仓不变硬约束：买回=卖出，日终仓位复原",
        ]
        if qty < ctx.proposed_qty:
            reasons.append(f"申请腿量 {ctx.proposed_qty} 截断为 {qty}（T+1 可卖/腿量上限约束，留痕）")
        return T0Advice(
            decision=T0Decision.EXECUTE,
            direction=ctx.t0_signal,
            suggested_qty=qty,
            reasons=tuple(reasons),
        )

    # ── 编排：裁决→（EXECUTE）风控前置+执行外发，双审计 ─────────────────────

    def act(self, ctx: T0Context) -> T0TraderAction:
        """decide → 裁决审计 → EXECUTE 时风控前置 + 执行外发（委托 C-012）。"""
        advice = self.decide(ctx)
        records: list[dict[str, Any]] = [
            {
                "record_type": "T0_DECISION",
                "role": ROLE,
                "symbol": ctx.symbol,
                "decision": advice.decision.value,
                "direction": advice.direction,
                "suggested_qty": advice.suggested_qty,
                "reasons": list(advice.reasons),
                "requires_risk_check": advice.requires_risk_check,
            }
        ]
        self._emit_audit(records[-1])
        risk_check_signaled = False
        execution_handed_off = False
        if advice.decision is T0Decision.EXECUTE:
            exec_record: dict[str, Any] = {
                "record_type": "T0_EXECUTION",
                "role": ROLE,
                "symbol": ctx.symbol,
                "direction": advice.direction,
                "suggested_qty": advice.suggested_qty,
                "risk_check_signaled": False,
                "execution_handed_off": False,
                "note": "执行委托 C-012 做T 日内套利管线；本 Agent 不产生任何生效指令",
            }
            payload: dict[str, Any] = {
                "role": ROLE,
                "symbol": ctx.symbol,
                "direction": advice.direction,
                "suggested_qty": advice.suggested_qty,
                "expected_edge_bp": ctx.expected_edge_bp,
                "trades_done_today": ctx.trades_done_today,
            }
            if self._risk_check_trigger is not None:
                try:
                    self._risk_check_trigger(payload)
                    risk_check_signaled = True
                except Exception:  # noqa: BLE001 — 回调异常不阻断，如实标记
                    _logger.exception("risk_check_trigger 异常（已降级，risk_check_signaled=False）")
            if self._execution_sink is not None:
                try:
                    self._execution_sink(payload)
                    execution_handed_off = True
                except Exception:  # noqa: BLE001 — 回调异常不阻断，如实标记
                    _logger.exception("execution_sink 异常（已降级，execution_handed_off=False）")
            exec_record["risk_check_signaled"] = risk_check_signaled
            exec_record["execution_handed_off"] = execution_handed_off
            records.append(exec_record)
            self._emit_audit(exec_record)
        return T0TraderAction(
            advice=advice,
            risk_check_signaled=risk_check_signaled,
            execution_handed_off=execution_handed_off,
            audit_records=tuple(records),
        )

    def _emit_audit(self, record: dict[str, Any]) -> None:
        if self._audit_sink is not None:
            try:
                self._audit_sink(record)
            except Exception:  # noqa: BLE001 — sink 异常不阻断（记录仍内嵌返回值）
                _logger.exception("audit_sink 异常（已降级，判定不受影响）")
