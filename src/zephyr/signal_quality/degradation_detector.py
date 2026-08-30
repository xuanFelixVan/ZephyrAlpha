# [BLUEPRINT] MOD-SIGQC-001 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_quality.degradation_detector
# [DOMAIN] D_SIGQC
# [DEPENDENCIES] zephyr.signal_quality.degradation_monitor_base; zephyr.data.alerter; zephyr.signal_fundamental.audit.signal_audit_logger; zephyr.shared.contracts.synthesized_signal; zephyr.trading.trading_contracts.market.signal_degradation_warning; zephyr.shared.utils.time_utils
# [CONSUMERS] signal_fundamental; risk; pf_core
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 三级分级 worst-of 合成；SEVERE⇔block_dispatch=True；告警级别映射 MILD→WARN/MODERATE→ERROR/SEVERE→CRITICAL；同级去重升级再报；审计事件零密钥材料；滑窗 maxlen 有界
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] evaluate/assess/observe 不抛异常（检测器不得阻断信号主链路；SEVERE 经 block_dispatch 标记由下游阻断）
# [TESTS] tests/signal_quality/test_degradation_detector.py
# [A_module] module_id=MOD-SIGQC-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
信号质量降级检测器（B2-05120 / CAND-SIGQC-001 / D-SIGNAL-156 二元结论补充）。

多维检测 + 三级降级分级 + 重度阻断 + 告警路由 + 审计落 signal_audit：

- 检测维度（滑窗衰减/骤降/漂移，基线窗 vs 近窗对比）：
  ① IC 滑窗衰减——近窗 IC 均值 / 基线均值 < ic_decay_warn → MODERATE；≤ 0（符号翻转）→ SEVERE
  ② 覆盖率骤降——基线-近窗均值差 ≥ coverage_drop_warn → MODERATE；≥ severe → SEVERE
  ③ 方向一致性漂移——近窗多空比均值偏离基线 ≥ direction_drift_warn → MODERATE；≥ severe → SEVERE
- 三级分级：NONE / MILD / MODERATE / SEVERE，多维 worst-of 合成；
  下游信号自带 is_degraded 标记时地板级 MILD。
- 重度阻断：SEVERE → suggested_action="block_dispatch" 且 should_block()=True，
  由信号下发方据此阻断（本器不自行阻断流水线，对齐 DegradationMonitorBase 契约）。
- 告警路由：复用 D-DATA-112 zephyr.data.alerter.Alerter（注入实例），
  MILD→WARN / MODERATE→ERROR / SEVERE→CRITICAL；同级别去重、升级再报、恢复复位。
- 审计：检测事件写 signal_audit（SignalAuditEvent/DEGRADED，严重级别同步映射）。

契约对齐：CTR-ERR-003（SignalDegradationWarning 出站）-> D_RISK, D_PORTFOLIO_CORE。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: window_size 参数
#   fields: 参数 window_size（无注解）
#   code: degradation_detector.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: baseline_size 参数
#   fields: 参数 baseline_size（无注解）
#   code: degradation_detector.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: ic_decay_warn 参数
#   fields: 参数 ic_decay_warn（无注解）
#   code: degradation_detector.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: coverage_drop_warn 参数
#   fields: 参数 coverage_drop_warn（无注解）
#   code: degradation_detector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① DegradationDetector
#   name_en: DegradationDetector
#   intro: 信号质量降级检测器（OCP 扩展点 D_SIGQC-DEG 实现）。
#   desc: 信号质量降级检测器（OCP 扩展点 D_SIGQC-DEG 实现）。 Usage: detector = DegradationDetector(alerter=Alerter(…；公共方法（定义序）: observe…
#   inputs: window_size baseline_size ic_decay_warn coverage_drop_warn coverage_d…
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: DegradationDetector
#   downstream: signal_fundamental; risk; pf_core
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
import logging
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Final

from zephyr.data.alerter import LEVEL_CRITICAL, LEVEL_ERROR, LEVEL_WARN
from zephyr.shared.contracts.synthesized_signal import SynthesizedSignal
from zephyr.shared.utils.time_utils import now_utc
from zephyr.signal_fundamental.audit.signal_audit_logger import (
    AuditSeverity,
    SignalAuditEvent,
    SignalEventType,
)
from zephyr.signal_quality.degradation_monitor_base import DegradationMonitorBase
from zephyr.trading.trading_contracts.market.signal_degradation_warning import SignalDegradationWarning

logger = logging.getLogger(__name__)

__all__ = [
    "DegradationAssessment",
    "DegradationDetector",
    "DegradationGrade",
]

_SOURCE_MODULE: Final[str] = "signal_quality.degradation_detector"
_ALERT_TASK_ID: Final[str] = "signal_quality_degradation"


class DegradationGrade(str, Enum):
    """三级降级分级（+NONE 健康态）。"""

    NONE = "NONE"
    MILD = "MILD"
    MODERATE = "MODERATE"
    SEVERE = "SEVERE"


_GRADE_RANK: Final[dict[DegradationGrade, int]] = {
    DegradationGrade.NONE: 0,
    DegradationGrade.MILD: 1,
    DegradationGrade.MODERATE: 2,
    DegradationGrade.SEVERE: 3,
}

_ALERT_LEVEL: Final[dict[DegradationGrade, str]] = {
    DegradationGrade.MILD: LEVEL_WARN,
    DegradationGrade.MODERATE: LEVEL_ERROR,
    DegradationGrade.SEVERE: LEVEL_CRITICAL,
}

_AUDIT_SEVERITY: Final[dict[DegradationGrade, AuditSeverity]] = {
    DegradationGrade.MILD: AuditSeverity.WARNING,
    DegradationGrade.MODERATE: AuditSeverity.ERROR,
    DegradationGrade.SEVERE: AuditSeverity.CRITICAL,
}


@dataclass(frozen=True)
class DegradationAssessment:
    """一次多维检测结论。"""

    grade: DegradationGrade
    block_dispatch: bool
    dimensions: dict[str, str] = field(default_factory=dict)  # 维度名 → grade.value
    reason: str = ""


class DegradationDetector(DegradationMonitorBase):
    """信号质量降级检测器（OCP 扩展点 D_SIGQC-DEG 实现）。

    Usage:
        detector = DegradationDetector(alerter=Alerter(), audit_sink=signal_audit.write)
        detector.observe(ic=0.042, coverage=0.93, long_ratio=0.61)
        warnings = detector.evaluate(signals)
        if detector.should_block():
            ...  # 阻断信号下发
    """

    def __init__(
        self,
        *,
        window_size: int = 10,
        baseline_size: int = 60,
        ic_decay_warn: float = 0.5,
        coverage_drop_warn: float = 0.2,
        coverage_drop_severe: float = 0.5,
        direction_drift_warn: float = 0.25,
        direction_drift_severe: float = 0.4,
        alerter: Any = None,
        audit_sink: Callable[[SignalAuditEvent], None] | None = None,
        clock: Callable[[], datetime] = now_utc,
    ) -> None:
        self._window = window_size
        self._ic: deque[float] = deque(maxlen=baseline_size)
        self._coverage: deque[float] = deque(maxlen=baseline_size)
        self._long_ratio: deque[float] = deque(maxlen=baseline_size)
        self._ic_decay_warn = ic_decay_warn
        self._coverage_drop_warn = coverage_drop_warn
        self._coverage_drop_severe = coverage_drop_severe
        self._direction_drift_warn = direction_drift_warn
        self._direction_drift_severe = direction_drift_severe
        self._alerter = alerter
        self._audit_sink = audit_sink
        self._clock = clock
        self._last_alerted_grade = DegradationGrade.NONE
        self._last_audited_grade = DegradationGrade.NONE
        self._warning_seq = 0

    # ── 观测摄入 ──────────────────────────────────────────

    def observe(
        self,
        *,
        ic: float | None = None,
        coverage: float | None = None,
        long_ratio: float | None = None,
    ) -> None:
        """摄入一次质量观测（IC/覆盖率/多空比，缺省维度不记）。"""
        if ic is not None:
            self._ic.append(float(ic))
        if coverage is not None:
            self._coverage.append(float(coverage))
        if long_ratio is not None:
            self._long_ratio.append(float(long_ratio))

    # ── 多维检测 ──────────────────────────────────────────

    def assess(self) -> DegradationAssessment:
        """对滑窗做三维检测并 worst-of 合成三级降级结论。"""
        dimensions: dict[str, DegradationGrade] = {
            "ic_decay": self._assess_ic_decay(),
            "coverage_drop": self._assess_coverage_drop(),
            "direction_drift": self._assess_direction_drift(),
        }
        grade = max(dimensions.values(), key=lambda g: _GRADE_RANK[g])
        reasons = [f"{name}={g.value}" for name, g in dimensions.items() if g is not DegradationGrade.NONE]
        return DegradationAssessment(
            grade=grade,
            block_dispatch=grade is DegradationGrade.SEVERE,
            dimensions={k: v.value for k, v in dimensions.items()},
            reason="; ".join(reasons) if reasons else "质量指标平稳",
        )

    def should_block(self) -> bool:
        """重度降级（SEVERE）→ 阻断信号下发。"""
        return self.assess().block_dispatch

    def evaluate(self, signals: list[SynthesizedSignal]) -> list[SignalDegradationWarning]:
        """评估批量合成信号质量（DegradationMonitorBase 契约：不阻断流水线，仅发降级警告）。"""
        assessment = self.assess()
        signal_degraded = any(s.is_degraded for s in signals)
        if assessment.grade is DegradationGrade.NONE and signal_degraded:
            assessment = DegradationAssessment(
                grade=DegradationGrade.MILD,
                block_dispatch=False,
                dimensions=assessment.dimensions,
                reason="下游信号自带 is_degraded 降级标记",
            )
        if assessment.grade is DegradationGrade.NONE:
            self._last_alerted_grade = DegradationGrade.NONE  # 恢复复位，后续可重新告警
            self._last_audited_grade = DegradationGrade.NONE
            return []

        self._route_alert(assessment)
        self._write_audit(assessment, signals)
        return [self._build_warning(assessment, signals)]

    # ── 维度实现 ──────────────────────────────────────────

    def _split_windows(self, series: deque[float]) -> tuple[list[float], list[float]] | None:
        if len(series) < self._window * 2:
            return None
        values = list(series)
        return values[: -self._window], values[-self._window :]

    def _assess_ic_decay(self) -> DegradationGrade:
        split = self._split_windows(self._ic)
        if split is None:
            return DegradationGrade.NONE
        baseline, recent = split
        baseline_mean = sum(baseline) / len(baseline)
        if baseline_mean <= 0:
            return DegradationGrade.NONE  # 无正基线不做衰减判定
        recent_mean = sum(recent) / len(recent)
        ratio = recent_mean / baseline_mean
        if ratio <= 0:
            return DegradationGrade.SEVERE  # IC 符号翻转
        if ratio < self._ic_decay_warn:
            return DegradationGrade.MODERATE
        return DegradationGrade.NONE

    def _assess_coverage_drop(self) -> DegradationGrade:
        split = self._split_windows(self._coverage)
        if split is None:
            return DegradationGrade.NONE
        baseline, recent = split
        drop = (sum(baseline) / len(baseline)) - (sum(recent) / len(recent))
        if drop >= self._coverage_drop_severe:
            return DegradationGrade.SEVERE
        if drop >= self._coverage_drop_warn:
            return DegradationGrade.MODERATE
        if drop >= self._coverage_drop_warn / 2:
            return DegradationGrade.MILD
        return DegradationGrade.NONE

    def _assess_direction_drift(self) -> DegradationGrade:
        split = self._split_windows(self._long_ratio)
        if split is None:
            return DegradationGrade.NONE
        baseline, recent = split
        drift = abs((sum(recent) / len(recent)) - (sum(baseline) / len(baseline)))
        if drift >= self._direction_drift_severe:
            return DegradationGrade.SEVERE
        if drift >= self._direction_drift_warn:
            return DegradationGrade.MODERATE
        if drift >= self._direction_drift_warn * 0.6:
            return DegradationGrade.MILD
        return DegradationGrade.NONE

    # ── 告警 / 审计 / 契约 ────────────────────────────────

    def _route_alert(self, assessment: DegradationAssessment) -> None:
        """复用 D-DATA-112 alerter 路由：同级去重、升级再报。"""
        if self._alerter is None or assessment.grade is self._last_alerted_grade:
            return
        level = _ALERT_LEVEL[assessment.grade]
        try:
            self._alerter.notify(
                _ALERT_TASK_ID,
                f"信号质量{assessment.grade.value}降级: {assessment.reason}",
                level=level,
                source="signal_quality",
                extra={"grade": assessment.grade.value, "dimensions": assessment.dimensions},
            )
            self._last_alerted_grade = assessment.grade
        except Exception:  # noqa: BLE001 — 告警失败不阻断检测主链路（对齐 alerter ERROR_CONTRACT）
            logger.warning("degradation alert notify failed", exc_info=True)

    def _write_audit(self, assessment: DegradationAssessment, signals: list[SynthesizedSignal]) -> None:
        """检测日志入 signal_audit（级别变化时写一条，防同级刷量）。"""
        if self._audit_sink is None or assessment.grade is self._last_audited_grade:
            return
        event = SignalAuditEvent(
            event_type=SignalEventType.DEGRADED,
            signal_id=signals[0].signal_id if signals else "",
            symbol=signals[0].symbol if signals else "*",
            timestamp=self._clock(),
            severity=_AUDIT_SEVERITY[assessment.grade],
            description=f"信号质量{assessment.grade.value}降级（IC衰减/覆盖率骤降/方向漂移多维检测）: {assessment.reason}",
            metadata={"grade": assessment.grade.value, "dimensions": assessment.dimensions},
            source_module=_SOURCE_MODULE,
        )
        try:
            self._audit_sink(event)
            self._last_audited_grade = assessment.grade
        except Exception:  # noqa: BLE001 — 审计失败不阻断检测主链路
            logger.warning("degradation audit sink failed", exc_info=True)

    def _build_warning(
        self,
        assessment: DegradationAssessment,
        signals: list[SynthesizedSignal],
    ) -> SignalDegradationWarning:
        self._warning_seq += 1
        factor_ids = sorted({fid for s in signals for fid in s.contributing_factors})
        idem_seed = hashlib.sha256(
            f"{assessment.grade.value}|{assessment.reason}|{','.join(s.signal_id for s in signals)}".encode()
        ).hexdigest()[:16]
        return SignalDegradationWarning(
            degradation_level=assessment.grade.value,
            idempotency_key=f"sqd-{idem_seed}",
            reason=assessment.reason,
            suggested_action="block_dispatch" if assessment.block_dispatch else "downweight_position",
            warning_id=f"SQD-{self._clock().strftime('%Y%m%d%H%M%S')}-{self._warning_seq}",
            affected_factor_ids=factor_ids,
        )
