# [BLUEPRINT] MOD-AU-009 | docs/03_modules/_domain_autonomy_core/signal_analyst_agent/blueprint.md
# [MODULE] zephyr.autonomy_core.agents.signal_analyst_agent
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 运行时装配批（C-028 输出批量装配 / 漏斗权重真实调整 / SIGQC 指标对接）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] assess 纯函数无IO; snapshot/配置非法 Fail-Closed; 输出仅到漏斗建议层（FORWARD/DOWNWEIGHT/HOLD_BACK）绝无下单语义; 非 PROMOTE 必落降级建议审计; sink 异常不阻断判定
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_core/signal_analyst_agent/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] InvalidSignalSnapshotError; InvalidSignalAnalystConfigError
# [TESTS] tests/autonomy/test_signal_analyst_agent.py
# [A_module] module_id=MOD-AU-009 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""SignalAnalystAgent — 信号 Agent (MOD-AU-009)

B1-00241（AUD-DRAFT-001-DIGEST P1 波 W-P1-11）：SignalAnalyst 角色卡
（14号文 §3.0 role façade 族卡模式，与 MOD-AU-007/008 同族）。汇总 C-028
信号工厂输出（``SignalSnapshot`` 调用方装配注入）→ IC 衰减与拥挤度质量
评估（确定性阶梯）→ **漏斗处置建议**（FORWARD/DOWNWEIGHT/HOLD_BACK——
输出入漏斗，**绝不直接下单**），异常信号降级建议经 ``degrade_sink`` 外发。

查重分工：信号生产归 MOD-SIG-087 signal_factory；质量基础设施归 D_SIGQC
族；本角色只做职责化编排判定（评估输入注入、不复制 QC 计算件、不辩论）。
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
    "FunnelAction",
    "InvalidSignalAnalystConfigError",
    "InvalidSignalSnapshotError",
    "QualityAssessment",
    "SignalAnalystAction",
    "SignalAnalystAgent",
    "SignalAnalystThresholds",
    "SignalQualityVerdict",
    "SignalSnapshot",
]

ROLE: Final[str] = "signal_analyst"

AGENT_CARD: Final[dict[str, Any]] = {
    "role": ROLE,
    "capabilities": [
        {
            "id": "signal_quality_assessment",
            "name": "IC 衰减与拥挤度质量评估（确定性阶梯）",
            "inputs": "SignalSnapshot（C-028 信号工厂输出装配注入）",
            "outputs": "QualityAssessment（漏斗处置建议 FORWARD/DOWNWEIGHT/HOLD_BACK）",
            "autonomyLevel": "L1_suggest",
        },
        {
            "id": "degrade_advice",
            "name": "异常信号降级建议",
            "inputs": "verdict ≠ PROMOTE",
            "outputs": "degrade_sink 回调（漏斗权重调整执行委托装配层）",
            "autonomyLevel": "L1_suggest",
        },
    ],
    "autonomyBoundaries": {
        "ai_modifiable": ["降级建议文本", "评估理由"],
        "human_gated": ["QUARANTINE 隔离的恢复放行"],
        "immutable": ["下单/交易执行（执行域职责，本角色无下单语义）", "信号生产本体（MOD-SIG-087）", "判定阈值真源（配置）"],
    },
    "healthCheck": {"heartbeat": "on_demand_assess"},
}


class InvalidSignalSnapshotError(ZephyrBaseError):
    """信号快照非法（Fail-Closed：不评估脏输入）。"""


class InvalidSignalAnalystConfigError(ZephyrBaseError):
    """SignalAnalyst 阈值配置非法。"""


class SignalQualityVerdict(str, Enum):
    """信号质量裁决。"""

    PROMOTE = "PROMOTE"
    DEGRADE = "DEGRADE"
    QUARANTINE = "QUARANTINE"


class FunnelAction(str, Enum):
    """漏斗处置建议（建议语义，绝不直接下单）。"""

    FORWARD = "FORWARD"  # 正常入漏斗
    DOWNWEIGHT = "DOWNWEIGHT"  # 降权入漏斗
    HOLD_BACK = "HOLD_BACK"  # 拦下不入漏斗


_VERDICT_TO_FUNNEL: Final[dict[SignalQualityVerdict, FunnelAction]] = {
    SignalQualityVerdict.PROMOTE: FunnelAction.FORWARD,
    SignalQualityVerdict.DEGRADE: FunnelAction.DOWNWEIGHT,
    SignalQualityVerdict.QUARANTINE: FunnelAction.HOLD_BACK,
}


@dataclass(frozen=True)
class SignalSnapshot:
    """信号质量快照（由调用方从 C-028 输出与质量指标装配注入）。"""

    signal_id: str
    ic_current: float  # 近期 IC ∈ [-1,1]
    ic_baseline: float  # 基线 IC（正；衰减比 = current/baseline）
    crowding_score: float  # 拥挤度 ∈ [0,1]

    def __post_init__(self) -> None:
        if not self.signal_id or not self.signal_id.strip():
            raise InvalidSignalSnapshotError("signal_id 不能为空")
        if not (-1.0 <= self.ic_current <= 1.0):
            raise InvalidSignalSnapshotError(f"ic_current 必须 ∈ [-1,1]: {self.ic_current}")
        if self.ic_baseline <= 0:
            raise InvalidSignalSnapshotError(f"ic_baseline 必须为正（衰减比不可计算）: {self.ic_baseline}")
        if not (0.0 <= self.crowding_score <= 1.0):
            raise InvalidSignalSnapshotError(f"crowding_score 必须 ∈ [0,1]: {self.crowding_score}")


@dataclass(frozen=True)
class SignalAnalystThresholds:
    """判定阈值配置（C 类可调参数）。"""

    decay_warn_ratio: float = 0.5  # 衰减比 ≤ 该值 → DEGRADE
    decay_crit_ratio: float = 0.25  # 衰减比 ≤ 该值 → QUARANTINE
    crowding_warn: float = 0.7  # 拥挤度 ≥ 该值 → DEGRADE
    crowding_crit: float = 0.9  # 拥挤度 ≥ 该值 → QUARANTINE

    def __post_init__(self) -> None:
        if not (0.0 < self.decay_warn_ratio <= 1.0):
            raise InvalidSignalAnalystConfigError(f"decay_warn_ratio 必须 ∈ (0,1]: {self.decay_warn_ratio}")
        if not (0.0 < self.decay_crit_ratio < self.decay_warn_ratio):
            raise InvalidSignalAnalystConfigError(
                f"decay_crit_ratio 必须 ∈ (0, warn): {self.decay_crit_ratio}"
            )
        if not (0.0 < self.crowding_warn < 1.0):
            raise InvalidSignalAnalystConfigError(f"crowding_warn 必须 ∈ (0,1): {self.crowding_warn}")
        if not (self.crowding_warn < self.crowding_crit <= 1.0):
            raise InvalidSignalAnalystConfigError(
                f"crowding_crit 必须 ∈ (warn, 1]: {self.crowding_crit}"
            )


@dataclass(frozen=True)
class QualityAssessment:
    """质量评估结论（不可变；仅漏斗建议语义）。"""

    verdict: SignalQualityVerdict
    funnel_action: FunnelAction
    reasons: tuple[str, ...]
    ic_decay_ratio: float


@dataclass(frozen=True)
class SignalAnalystAction:
    """act 编排结果：评估 + 降级建议 + 双审计记录。"""

    assessment: QualityAssessment
    degrade_adviced: bool
    audit_records: tuple[dict[str, Any], ...]


class SignalAnalystAgent:
    """信号 Agent：IC 衰减×拥挤度 → 漏斗处置建议（判定核心纯函数）。

    Args:
        thresholds: 判定阈值配置。
        degrade_sink: 降级建议回调；异常不阻断判定，degrade_adviced 如实记 False。
        audit_sink: 审计记录回调；异常不阻断（记录仍内嵌 action.audit_records）。
    """

    ROLE: Final[str] = ROLE
    AGENT_CARD: Final[dict[str, Any]] = AGENT_CARD

    def __init__(
        self,
        thresholds: SignalAnalystThresholds | None = None,
        degrade_sink: Callable[[dict[str, Any]], None] | None = None,
        audit_sink: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self._thresholds = thresholds or SignalAnalystThresholds()
        self._degrade_sink = degrade_sink
        self._audit_sink = audit_sink

    # ── 判定阶梯（纯函数） ──────────────────────────────────────────────────

    def assess(self, snapshot: SignalSnapshot) -> QualityAssessment:
        """确定性阶梯：硬降级 QUARANTINE > 预警带 DEGRADE > 健康 PROMOTE。"""
        t = self._thresholds
        decay = snapshot.ic_current / snapshot.ic_baseline
        crit_reasons: list[str] = []
        if decay <= t.decay_crit_ratio:
            crit_reasons.append(f"IC 衰减比 {decay:.4f} ≤ 硬降级线 {t.decay_crit_ratio:.4f}（异常信号）")
        if snapshot.crowding_score >= t.crowding_crit:
            crit_reasons.append(f"拥挤度 {snapshot.crowding_score:.4f} ≥ 硬降级线 {t.crowding_crit:.4f}")
        if crit_reasons:
            return QualityAssessment(
                verdict=SignalQualityVerdict.QUARANTINE,
                funnel_action=_VERDICT_TO_FUNNEL[SignalQualityVerdict.QUARANTINE],
                reasons=tuple(crit_reasons),
                ic_decay_ratio=decay,
            )
        warn_reasons: list[str] = []
        if decay <= t.decay_warn_ratio:
            warn_reasons.append(f"IC 衰减比 {decay:.4f} ≤ 预警线 {t.decay_warn_ratio:.4f}")
        if snapshot.crowding_score >= t.crowding_warn:
            warn_reasons.append(f"拥挤度 {snapshot.crowding_score:.4f} ≥ 预警线 {t.crowding_warn:.4f}")
        if warn_reasons:
            return QualityAssessment(
                verdict=SignalQualityVerdict.DEGRADE,
                funnel_action=_VERDICT_TO_FUNNEL[SignalQualityVerdict.DEGRADE],
                reasons=tuple(warn_reasons),
                ic_decay_ratio=decay,
            )
        return QualityAssessment(
            verdict=SignalQualityVerdict.PROMOTE,
            funnel_action=_VERDICT_TO_FUNNEL[SignalQualityVerdict.PROMOTE],
            reasons=(f"IC 衰减比 {decay:.4f} 与拥挤度 {snapshot.crowding_score:.4f} 均在安全区",),
            ic_decay_ratio=decay,
        )

    # ── 编排：评估→（非 PROMOTE）降级建议，双审计 ───────────────────────────

    def act(self, snapshot: SignalSnapshot) -> SignalAnalystAction:
        """assess → 评估审计 → 非 PROMOTE 时降级建议 + 处置审计。"""
        assessment = self.assess(snapshot)
        records: list[dict[str, Any]] = [
            {
                "record_type": "SIGNAL_QUALITY_ASSESSMENT",
                "role": ROLE,
                "signal_id": snapshot.signal_id,
                "verdict": assessment.verdict.value,
                "funnel_action": assessment.funnel_action.value,
                "ic_decay_ratio": assessment.ic_decay_ratio,
                "reasons": list(assessment.reasons),
            }
        ]
        self._emit_audit(records[-1])
        degrade_adviced = False
        if assessment.verdict is not SignalQualityVerdict.PROMOTE:
            advice: dict[str, Any] = {
                "record_type": "SIGNAL_DEGRADE_ADVICE",
                "role": ROLE,
                "signal_id": snapshot.signal_id,
                "verdict": assessment.verdict.value,
                "suggested_funnel_action": assessment.funnel_action.value,
                "note": "输出仅漏斗处置建议，绝不直接下单；权重调整执行委托装配层",
            }
            if self._degrade_sink is not None:
                try:
                    self._degrade_sink(advice)
                    degrade_adviced = True
                except Exception:  # noqa: BLE001 — sink 异常不阻断，如实标记
                    _logger.exception("degrade_sink 异常（已降级，degrade_adviced=False）")
            records.append(advice)
            self._emit_audit(advice)
        return SignalAnalystAction(
            assessment=assessment,
            degrade_adviced=degrade_adviced,
            audit_records=tuple(records),
        )

    def _emit_audit(self, record: dict[str, Any]) -> None:
        if self._audit_sink is not None:
            try:
                self._audit_sink(record)
            except Exception:  # noqa: BLE001 — sink 异常不阻断（记录仍内嵌返回值）
                _logger.exception("audit_sink 异常（已降级，判定不受影响）")
