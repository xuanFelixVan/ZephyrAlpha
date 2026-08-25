# [BLUEPRINT] MOD-AU-010 | docs/03_modules/_domain_autonomy_core/timing_analyst_agent/blueprint.md
# [MODULE] zephyr.autonomy_core.agents.timing_analyst_agent
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 运行时装配批（C-021/C-014 实时输入装配 / 风控校验链 / MOD-EX-062 执行策略选择）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] advise 纯函数无IO; ctx/配置非法 Fail-Closed; 建议永远 requires_risk_check=True 且无下单语义; 非 HOLD 必发风控前置信号并双审计; 回调/sink 异常不阻断判定
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_core/timing_analyst_agent/blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] InvalidTimingContextError; InvalidTimingAnalystConfigError
# [TESTS] tests/autonomy/test_timing_analyst_agent.py
# [A_module] module_id=MOD-AU-010 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""TimingAnalystAgent — 择时 Agent (MOD-AU-010)

B1-00242（AUD-DRAFT-001-DIGEST P1 波 W-P1-11）：TimingAnalyst 角色卡
（14号文 §3.0 role façade 族卡模式，与 MOD-AU-007/008/009 同族）。综合
C-021 大盘状态 + C-014 大盘预测 + 做T 点位（MOD-SIG-068 口径）→
开/加/减仓时机（OPEN/ADD/REDUCE/HOLD）与执行策略（市价/限价/拆单）建议；
建议**经风控校验后才生效**（risk_check_trigger 回调，本 Agent 不产生任何
生效指令、无下单语义）。

查重分工：regime 判定归 MOD-REGIME-001；做T 点位归 MOD-SIG-068；执行策略
选择本体归 MOD-EX-062；本角色只做融合裁决与风控前置信号。
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
    "ExecutionStyle",
    "InvalidTimingAnalystConfigError",
    "InvalidTimingContextError",
    "TimingAction",
    "TimingAdvice",
    "TimingAnalystAction",
    "TimingAnalystAgent",
    "TimingAnalystThresholds",
    "TimingContext",
]

ROLE: Final[str] = "timing_analyst"

_VALID_REGIMES: Final[frozenset[str]] = frozenset({"trending", "range", "volatile"})
_VALID_T0: Final[frozenset[str]] = frozenset({"T买", "T卖"})

AGENT_CARD: Final[dict[str, Any]] = {
    "role": ROLE,
    "capabilities": [
        {
            "id": "timing_advice",
            "name": "开/加/减仓时机与执行策略（市价/限价/拆单）融合裁决",
            "inputs": "TimingContext（C-021 状态 + C-014 预测 + 做T 点位装配注入）",
            "outputs": "TimingAdvice（requires_risk_check 恒真）",
            "autonomyLevel": "L1_suggest",
        },
        {
            "id": "risk_check_signal",
            "name": "风控前置校验信号（非 HOLD 建议生效前必经）",
            "inputs": "TimingAdvice.action ≠ HOLD",
            "outputs": "risk_check_trigger 回调（校验执行委托风控链）",
            "autonomyLevel": "L2_approval",
        },
    ],
    "autonomyBoundaries": {
        "ai_modifiable": ["建议理由文本", "执行策略建议"],
        "human_gated": ["建议经风控校验后生效（风控前置信号）"],
        "immutable": ["下单/交易执行（执行域职责，本角色无下单语义）", "regime/预测/点位真源（C-021/C-014/MOD-SIG-068）", "判定阈值真源（配置）"],
    },
    "healthCheck": {"heartbeat": "on_demand_advise"},
}


class InvalidTimingContextError(ZephyrBaseError):
    """择时上下文非法（Fail-Closed：不评估脏输入）。"""


class InvalidTimingAnalystConfigError(ZephyrBaseError):
    """TimingAnalyst 阈值配置非法。"""


class TimingAction(str, Enum):
    """时机动作建议。"""

    OPEN = "OPEN"
    ADD = "ADD"
    REDUCE = "REDUCE"
    HOLD = "HOLD"


class ExecutionStyle(str, Enum):
    """执行策略建议。"""

    MARKET = "MARKET"  # 市价
    LIMIT = "LIMIT"  # 限价
    SLICED = "SLICED"  # 拆单


@dataclass(frozen=True)
class TimingContext:
    """择时上下文（由调用方从 C-021/C-014/做T 点位装配注入）。"""

    regime_state: str  # C-021 大盘状态：trending/range/volatile
    forecast_score: float  # C-014 大盘预测分 ∈ [-1,1]
    t0_signal: str | None  # 做T 点位：T买/T卖/None

    def __post_init__(self) -> None:
        if self.regime_state not in _VALID_REGIMES:
            raise InvalidTimingContextError(
                f"regime_state 必须 ∈ {sorted(_VALID_REGIMES)}: {self.regime_state!r}"
            )
        if not (-1.0 <= self.forecast_score <= 1.0):
            raise InvalidTimingContextError(f"forecast_score 必须 ∈ [-1,1]: {self.forecast_score}")
        if self.t0_signal is not None and self.t0_signal not in _VALID_T0:
            raise InvalidTimingContextError(f"t0_signal 必须 ∈ {{T买, T卖, None}}: {self.t0_signal!r}")


@dataclass(frozen=True)
class TimingAnalystThresholds:
    """判定阈值配置（C 类可调参数）。"""

    open_threshold: float = 0.3  # 开仓线：forecast ≥ 该值才考虑开/加
    strong_open_threshold: float = 0.6  # 强开线：强共振市价
    reduce_threshold: float = -0.3  # 减仓线：forecast ≤ 该值减仓

    def __post_init__(self) -> None:
        if not (0.0 < self.open_threshold <= 1.0):
            raise InvalidTimingAnalystConfigError(f"open_threshold 必须 ∈ (0,1]: {self.open_threshold}")
        if not (self.open_threshold < self.strong_open_threshold <= 1.0):
            raise InvalidTimingAnalystConfigError(
                f"strong_open_threshold 必须 ∈ (open, 1]: {self.strong_open_threshold}"
            )
        if not (-1.0 <= self.reduce_threshold < 0.0):
            raise InvalidTimingAnalystConfigError(f"reduce_threshold 必须 ∈ [-1,0): {self.reduce_threshold}")


@dataclass(frozen=True)
class TimingAdvice:
    """择时建议（不可变；经风控校验后才生效）。"""

    action: TimingAction
    execution_style: ExecutionStyle | None
    reasons: tuple[str, ...]
    requires_risk_check: bool = True


@dataclass(frozen=True)
class TimingAnalystAction:
    """act 编排结果：建议 + 风控前置信号 + 双审计记录。"""

    advice: TimingAdvice
    risk_check_signaled: bool
    audit_records: tuple[dict[str, Any], ...]


class TimingAnalystAgent:
    """择时 Agent：状态×预测×做T 点 → 时机与执行策略建议（判定核心纯函数）。

    Args:
        thresholds: 判定阈值配置。
        risk_check_trigger: 风控前置信号回调（payload dict）；异常不阻断，
            risk_check_signaled 如实记 False。
        audit_sink: 审计记录回调；异常不阻断（记录仍内嵌 action.audit_records）。
    """

    ROLE: Final[str] = ROLE
    AGENT_CARD: Final[dict[str, Any]] = AGENT_CARD

    def __init__(
        self,
        thresholds: TimingAnalystThresholds | None = None,
        risk_check_trigger: Callable[[dict[str, Any]], None] | None = None,
        audit_sink: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self._thresholds = thresholds or TimingAnalystThresholds()
        self._risk_check_trigger = risk_check_trigger
        self._audit_sink = audit_sink

    # ── 判定阶梯（纯函数） ──────────────────────────────────────────────────

    def advise(self, ctx: TimingContext) -> TimingAdvice:
        """确定性阶梯：volatile → 减仓线 → T卖联动 → 强共振 → 共振 → 无共振加 → HOLD。"""
        t = self._thresholds
        f = ctx.forecast_score
        if ctx.regime_state == "volatile":
            if f <= t.reduce_threshold:
                return TimingAdvice(
                    action=TimingAction.REDUCE,
                    execution_style=ExecutionStyle.SLICED,
                    reasons=(f"波动市且预测 {f:.4f} ≤ 减仓线 {t.reduce_threshold:.4f}（拆单减）",),
                )
            return TimingAdvice(
                action=TimingAction.HOLD,
                execution_style=None,
                reasons=(f"波动市（regime=volatile）预测 {f:.4f} 未破减仓线，不追单",),
            )
        if f <= t.reduce_threshold:
            return TimingAdvice(
                action=TimingAction.REDUCE,
                execution_style=ExecutionStyle.SLICED,
                reasons=(f"预测 {f:.4f} ≤ 减仓线 {t.reduce_threshold:.4f}（拆单减）",),
            )
        if ctx.t0_signal == "T卖" and f < t.open_threshold:
            return TimingAdvice(
                action=TimingAction.REDUCE,
                execution_style=ExecutionStyle.LIMIT,
                reasons=(f"做T 卖点（T卖）联动且预测 {f:.4f} 未达开仓线（限价减）",),
            )
        if f >= t.strong_open_threshold and ctx.t0_signal == "T买":
            return TimingAdvice(
                action=TimingAction.OPEN,
                execution_style=ExecutionStyle.MARKET,
                reasons=(f"预测 {f:.4f} ≥ 强开线 {t.strong_open_threshold:.4f} 且做T 买点共振（市价开）",),
            )
        if f >= t.open_threshold and ctx.t0_signal == "T买":
            return TimingAdvice(
                action=TimingAction.OPEN,
                execution_style=ExecutionStyle.LIMIT,
                reasons=(f"预测 {f:.4f} ≥ 开仓线 {t.open_threshold:.4f} 且做T 买点共振（限价开）",),
            )
        if f >= t.open_threshold:
            return TimingAdvice(
                action=TimingAction.ADD,
                execution_style=ExecutionStyle.SLICED,
                reasons=(f"预测 {f:.4f} ≥ 开仓线但无做T 点共振（拆单加）",),
            )
        return TimingAdvice(
            action=TimingAction.HOLD,
            execution_style=None,
            reasons=(f"预测 {f:.4f} 介于减仓/开仓线之间（{t.reduce_threshold:.4f} ~ {t.open_threshold:.4f}），观望",),
        )

    # ── 编排：建议→（非 HOLD）风控前置信号，双审计 ───────────────────────────

    def act(self, ctx: TimingContext) -> TimingAnalystAction:
        """advise → 建议审计 → 非 HOLD 时风控前置信号 + 校验审计。"""
        advice = self.advise(ctx)
        records: list[dict[str, Any]] = [
            {
                "record_type": "TIMING_ADVICE",
                "role": ROLE,
                "action": advice.action.value,
                "execution_style": advice.execution_style.value if advice.execution_style else None,
                "reasons": list(advice.reasons),
                "requires_risk_check": advice.requires_risk_check,
                "context": {
                    "regime_state": ctx.regime_state,
                    "forecast_score": ctx.forecast_score,
                    "t0_signal": ctx.t0_signal,
                },
            }
        ]
        self._emit_audit(records[-1])
        risk_check_signaled = False
        if advice.action is not TimingAction.HOLD:
            check_record: dict[str, Any] = {
                "record_type": "TIMING_RISK_CHECK",
                "role": ROLE,
                "action": advice.action.value,
                "risk_check_signaled": False,
                "note": "建议经风控校验后生效；本 Agent 不产生任何生效指令",
            }
            if self._risk_check_trigger is not None:
                try:
                    self._risk_check_trigger(
                        {
                            "role": ROLE,
                            "action": advice.action.value,
                            "execution_style": advice.execution_style.value if advice.execution_style else None,
                            "regime_state": ctx.regime_state,
                            "forecast_score": ctx.forecast_score,
                            "t0_signal": ctx.t0_signal,
                        }
                    )
                    risk_check_signaled = True
                except Exception:  # noqa: BLE001 — 回调异常不阻断，如实标记
                    _logger.exception("risk_check_trigger 异常（已降级，risk_check_signaled=False）")
            check_record["risk_check_signaled"] = risk_check_signaled
            records.append(check_record)
            self._emit_audit(check_record)
        return TimingAnalystAction(
            advice=advice,
            risk_check_signaled=risk_check_signaled,
            audit_records=tuple(records),
        )

    def _emit_audit(self, record: dict[str, Any]) -> None:
        if self._audit_sink is not None:
            try:
                self._audit_sink(record)
            except Exception:  # noqa: BLE001 — sink 异常不阻断（记录仍内嵌返回值）
                _logger.exception("audit_sink 异常（已降级，判定不受影响）")
