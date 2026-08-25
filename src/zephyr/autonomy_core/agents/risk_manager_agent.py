# [BLUEPRINT] MOD-AU-007 | docs/03_modules/_domain_autonomy_core/risk_manager_agent/blueprint.md
# [MODULE] zephyr.autonomy_core.agents.risk_manager_agent
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-INF-016(trading_kill_switch 确定性执行体) ; 运行时装配批（状态轮询/审计持久化）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] assess/review 纯函数无IO; 触发仅当硬越限且kill_switch未激活(确定性校验路径); 建议与执行双审计记录; 回调/sink异常不阻断判定; 状态非法→InvalidRiskEngineStateError(Fail-Closed)
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_core/risk_manager_agent/blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] InvalidRiskManagerConfigError; InvalidRiskEngineStateError
# [TESTS] tests/autonomy/test_risk_manager_agent.py
# [A_module] module_id=MOD-AU-007 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""RiskManagerAgent — 风控 Agent (MOD-AU-007)

CAND-AUTONOMYCORE-003（B1-00240）：RiskManager 角色（14号文 §3.0 role façade
族卡模式）。实时读 risk 引擎限额 / 回撤 / VaR 状态（``RiskEngineState`` 由
调用方装配注入），生成**熔断建议**（``CircuitBreakerAdvice``）与**复盘说明**
（``review``）；触发 trading_kill_switch **仅经确定性校验路径**——硬熔断仍由
确定性代码执行（MOD-INF-016），本 Agent 只在状态确证硬越限且总停开关未激活时
发出触发信号（``kill_switch_trigger`` 回调）；建议与执行**双记录**入审计
（``audit_sink`` / ``RiskManagerAction.audit_records``）。

与 MOD-RK-22 agent_risk_monitor 分工：RK-22 管 agent 交易行为活动窗指标，
本角色管 risk 引擎状态（限额/回撤/VaR）的解释与熔断编排建议，互补不重复实现。
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
    "CircuitBreakerAdvice",
    "CircuitBreakerLevel",
    "InvalidRiskEngineStateError",
    "InvalidRiskManagerConfigError",
    "RiskEngineState",
    "RiskManagerAction",
    "RiskManagerAgent",
    "RiskManagerThresholds",
]

ROLE: Final[str] = "risk_manager"

AGENT_CARD: Final[dict[str, Any]] = {
    "role": ROLE,
    "capabilities": [
        {
            "id": "risk_state_assessment",
            "name": "risk 引擎限额/回撤/VaR 状态评估",
            "inputs": "RiskEngineState（调用方装配注入）",
            "outputs": "CircuitBreakerAdvice（熔断建议）+ 复盘说明",
            "autonomyLevel": "L1_suggest",
        },
        {
            "id": "circuit_breaker_signal",
            "name": "硬越限熔断触发信号（仅确定性校验路径）",
            "inputs": "CircuitBreakerAdvice=KILL_SWITCH 且 kill_switch 未激活",
            "outputs": "kill_switch_trigger 回调（执行委托确定性代码）",
            "autonomyLevel": "L2_approval",
        },
    ],
    "autonomyBoundaries": {
        "ai_modifiable": ["复盘说明文本", "预警带 REDUCE 建议"],
        "human_gated": ["kill_switch_trigger 触发信号发出"],
        "immutable": ["硬熔断执行本体（确定性代码，MOD-INF-016）", "限额/VaR 阈值真源（risk 引擎 SSoT）"],
    },
    "healthCheck": {"heartbeat": "on_demand_assess"},
}


class InvalidRiskManagerConfigError(ZephyrBaseError):
    """RiskManager 配置非法（warn_ratio 越界）。"""


class InvalidRiskEngineStateError(ZephyrBaseError):
    """risk 引擎状态输入非法（Fail-Closed：不评估脏输入）。"""


class CircuitBreakerLevel(str, Enum):
    """熔断建议级别。"""

    NONE = "NONE"
    REDUCE = "REDUCE"
    KILL_SWITCH = "KILL_SWITCH"


@dataclass(frozen=True)
class RiskManagerThresholds:
    """判定阈值配置（C 类可调参数）。"""

    warn_ratio: float = 0.8  # 预警带：占上限比例 ≥ 该值 → REDUCE

    def __post_init__(self) -> None:
        if not (0.0 < self.warn_ratio < 1.0):
            raise InvalidRiskManagerConfigError(f"warn_ratio 必须 ∈ (0,1): {self.warn_ratio}")


@dataclass(frozen=True)
class RiskEngineState:
    """risk 引擎实时状态快照（由调用方从限额/回撤/VaR 真源装配注入）。"""

    limits_breached: tuple[str, ...]  # 已破限额项
    current_drawdown: float  # 当前回撤（非负，0.05=5%）
    max_drawdown_limit: float  # 回撤上限（正）
    var_95: float | None  # VaR95 状态（None=未启用 VaR 判定）
    var_limit: float | None  # VaR 上限
    kill_switch_active: bool  # 确定性熔断是否已激活

    def __post_init__(self) -> None:
        if self.current_drawdown < 0:
            raise InvalidRiskEngineStateError(f"current_drawdown 不能为负: {self.current_drawdown}")
        if self.max_drawdown_limit <= 0:
            raise InvalidRiskEngineStateError(f"max_drawdown_limit 必须为正: {self.max_drawdown_limit}")
        if self.var_95 is not None and self.var_95 < 0:
            raise InvalidRiskEngineStateError(f"var_95 不能为负: {self.var_95}")
        if self.var_limit is not None and self.var_limit <= 0:
            raise InvalidRiskEngineStateError(f"var_limit 必须为正: {self.var_limit}")


@dataclass(frozen=True)
class CircuitBreakerAdvice:
    """熔断建议（不可变）。"""

    level: CircuitBreakerLevel
    reasons: tuple[str, ...]
    recommended_kill_switch_level: str | None = None  # DAILY_LOSS/POSITION_LIMIT/CIRCUIT_BREAKER


@dataclass(frozen=True)
class RiskManagerAction:
    """act 编排结果：建议 + 是否真触发 + 双审计记录。"""

    advice: CircuitBreakerAdvice
    triggered: bool
    audit_records: tuple[dict[str, Any], ...]


class RiskManagerAgent:
    """风控 Agent：限额/回撤/VaR 状态 → 熔断建议与复盘说明（判定核心纯函数）。

    Args:
        thresholds: 判定阈值配置。
        kill_switch_trigger: 熔断触发回调（level, payload）；异常不阻断判定，
            triggered 如实记 False。
        audit_sink: 审计记录回调；异常不阻断判定（记录仍内嵌 action.audit_records）。
    """

    ROLE: Final[str] = ROLE
    AGENT_CARD: Final[dict[str, Any]] = AGENT_CARD

    def __init__(
        self,
        thresholds: RiskManagerThresholds | None = None,
        kill_switch_trigger: Callable[[str, dict[str, Any]], None] | None = None,
        audit_sink: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self._thresholds = thresholds or RiskManagerThresholds()
        self._kill_switch_trigger = kill_switch_trigger
        self._audit_sink = audit_sink

    # ── 判定阶梯（纯函数） ──────────────────────────────────────────────────

    def assess(self, state: RiskEngineState) -> CircuitBreakerAdvice:
        """确定性判定阶梯：已熔断→NONE；硬越限→KILL_SWITCH（主因映射）；预警带→REDUCE。"""
        if state.kill_switch_active:
            return CircuitBreakerAdvice(
                level=CircuitBreakerLevel.NONE,
                reasons=("kill_switch 已熔断，不重复触发（确定性执行体已在位）",),
            )
        reasons: list[str] = []
        level_by_cause = ""
        if state.limits_breached:
            reasons.append(f"限额已破: {list(state.limits_breached)}")
            level_by_cause = "POSITION_LIMIT"
        if state.current_drawdown > state.max_drawdown_limit:
            reasons.append(f"回撤 {state.current_drawdown:.4f} 破上限 {state.max_drawdown_limit:.4f}")
            level_by_cause = level_by_cause or "DAILY_LOSS"
        if state.var_95 is not None and state.var_limit is not None and state.var_95 > state.var_limit:
            reasons.append(f"VaR95 {state.var_95:.4f} 破上限 {state.var_limit:.4f}")
            level_by_cause = level_by_cause or "CIRCUIT_BREAKER"
        if reasons:
            # 主因优先级：回撤(DAILY_LOSS) > 限额(POSITION_LIMIT) > VaR(CIRCUIT_BREAKER)
            if state.current_drawdown > state.max_drawdown_limit:
                level_by_cause = "DAILY_LOSS"
            elif state.limits_breached:
                level_by_cause = "POSITION_LIMIT"
            return CircuitBreakerAdvice(
                level=CircuitBreakerLevel.KILL_SWITCH,
                reasons=tuple(reasons),
                recommended_kill_switch_level=level_by_cause,
            )
        warn = self._thresholds.warn_ratio
        warn_reasons: list[str] = []
        if state.current_drawdown >= warn * state.max_drawdown_limit:
            warn_reasons.append(f"回撤 {state.current_drawdown:.4f} 入预警带（≥{warn:.0%}×上限）")
        if (
            state.var_95 is not None
            and state.var_limit is not None
            and state.var_95 >= warn * state.var_limit
        ):
            warn_reasons.append(f"VaR95 {state.var_95:.4f} 入预警带（≥{warn:.0%}×上限）")
        if warn_reasons:
            return CircuitBreakerAdvice(level=CircuitBreakerLevel.REDUCE, reasons=tuple(warn_reasons))
        return CircuitBreakerAdvice(level=CircuitBreakerLevel.NONE, reasons=("限额/回撤/VaR 均在安全区",))

    def review(self, state: RiskEngineState, advice: CircuitBreakerAdvice) -> str:
        """复盘说明（纯函数）：人可读的状态-判定-依据摘要。"""
        parts = [
            f"风控复盘：回撤={state.current_drawdown:.4f}/上限={state.max_drawdown_limit:.4f}",
            f"VaR95={state.var_95}/上限={state.var_limit}",
            f"限额破={list(state.limits_breached) or '无'}",
            f"kill_switch_active={state.kill_switch_active}",
            f"判定={advice.level.value}",
            f"依据={'; '.join(advice.reasons)}",
        ]
        if advice.recommended_kill_switch_level:
            parts.append(f"建议熔断档={advice.recommended_kill_switch_level}")
        return " | ".join(parts)

    # ── 编排：建议→双记录→（硬越限且未激活）触发信号 ─────────────────────────

    def act(self, state: RiskEngineState) -> RiskManagerAction:
        """assess → 建议审计 → 触发（仅确定性校验路径）→ 执行审计。"""
        advice = self.assess(state)
        records: list[dict[str, Any]] = [
            {
                "record_type": "RISK_MANAGER_ADVICE",
                "role": ROLE,
                "level": advice.level.value,
                "reasons": list(advice.reasons),
                "recommended_kill_switch_level": advice.recommended_kill_switch_level,
                "review": self.review(state, advice),
            }
        ]
        self._emit_audit(records[-1])
        triggered = False
        if advice.level is CircuitBreakerLevel.KILL_SWITCH and not state.kill_switch_active:
            payload: dict[str, Any] = {
                "role": ROLE,
                "reasons": list(advice.reasons),
                "drawdown": state.current_drawdown,
                "var_95": state.var_95,
                "limits_breached": list(state.limits_breached),
            }
            if self._kill_switch_trigger is not None:
                try:
                    self._kill_switch_trigger(advice.recommended_kill_switch_level or "CIRCUIT_BREAKER", payload)
                    triggered = True
                except Exception:  # noqa: BLE001 — 触发回调异常不阻断判定，如实标记
                    _logger.exception("kill_switch_trigger 异常（已降级，triggered=False）")
            records.append(
                {
                    "record_type": "RISK_MANAGER_EXECUTION",
                    "role": ROLE,
                    "kill_switch_level": advice.recommended_kill_switch_level,
                    "triggered": triggered,
                    "note": "触发仅经确定性校验路径；硬熔断执行委托确定性代码（MOD-INF-016）",
                }
            )
            self._emit_audit(records[-1])
        return RiskManagerAction(advice=advice, triggered=triggered, audit_records=tuple(records))

    def _emit_audit(self, record: dict[str, Any]) -> None:
        if self._audit_sink is not None:
            try:
                self._audit_sink(record)
            except Exception:  # noqa: BLE001 — sink 异常不阻断（记录仍内嵌返回值）
                _logger.exception("audit_sink 异常（已降级，判定不受影响）")
