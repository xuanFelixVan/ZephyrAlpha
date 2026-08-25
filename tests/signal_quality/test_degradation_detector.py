# [BLUEPRINT] MOD-SIGQC-001 | docs/03_modules/_domain_signal/blueprint.md
# [TTL] permanent
"""信号质量降级检测器测试（B2-05120 / CAND-SIGQC-001 / D-SIGNAL-156 二元结论补充）。

测试内容（注入假告警器与内存审计 sink，不触达真实告警通道）：
- 无观测数据 → NONE 不告警；指标平稳 → NONE
- IC 滑窗衰减：比值 < 阈值 → MODERATE；符号翻转 → SEVERE
- 覆盖率骤降：小跌 MILD / 大跌 MODERATE / 崩塌 SEVERE
- 方向一致性漂移：漂移超阈 → MODERATE/SEVERE
- 三级分级 worst-of 合成；SEVERE 阻断信号下发（block_dispatch/should_block）
- 告警复用 D-DATA-112 alerter 路由：MILD→WARN / MODERATE→ERROR / SEVERE→CRITICAL；同级去重、升级再报
- 检测日志入 signal_audit：SignalEventType.DEGRADED + 严重级别映射
- 下游信号自带 is_degraded 标记 → 至少 MILD
- 滑窗滑动后恢复 → NONE 且告警状态复位
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from zephyr.data.alerter import LEVEL_CRITICAL, LEVEL_ERROR, LEVEL_WARN
from zephyr.shared.contracts.synthesized_signal import SynthesizedSignal
from zephyr.signal_fundamental.audit.signal_audit_logger import AuditSeverity, SignalEventType
from zephyr.signal_quality.degradation_detector import DegradationDetector, DegradationGrade
from zephyr.trading.trading_contracts.market.signal_degradation_warning import SignalDegradationWarning


class _FakeAlerter:
    """替代 D-DATA-112 Alerter 的内存告警器（记录触达级别）。"""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def notify(self, task_id, error, level=LEVEL_ERROR, source=None, extra=None):
        self.calls.append({"task_id": task_id, "error": error, "level": level, "source": source, "extra": extra})
        return True


@pytest.fixture
def alerter():
    return _FakeAlerter()


@pytest.fixture
def audit_events():
    return []


@pytest.fixture
def detector(alerter, audit_events):
    return DegradationDetector(
        window_size=10,
        alerter=alerter,
        audit_sink=audit_events.append,
    )


def _signal(signal_id: str = "SIG-1", *, is_degraded: bool = False, factors: dict[str, float] | None = None):
    return SynthesizedSignal(
        as_of_timestamp=datetime(2026, 8, 25, tzinfo=UTC),
        confidence=0.8,
        generation_latency_ms=5,
        idempotency_key=f"idem-{signal_id}",
        signal_direction="long",
        signal_id=signal_id,
        signal_value=1.5,
        symbol="600519.SH",
        contributing_factors=factors or {"FAC-001": 0.6},
        is_degraded=is_degraded,
    )


def _feed_ic(detector, values):
    for v in values:
        detector.observe(ic=v)


def _feed_coverage(detector, values):
    for v in values:
        detector.observe(coverage=v)


def _feed_direction(detector, values):
    for v in values:
        detector.observe(long_ratio=v)


# ── 基线：无数据 / 指标平稳 ────────────────────────────────


def test_no_observation_no_warning(detector, alerter):
    warnings = detector.evaluate([_signal()])
    assert warnings == []
    assert detector.should_block() is False
    assert alerter.calls == []


def test_stable_metrics_no_warning(detector):
    _feed_ic(detector, [0.05] * 30)
    _feed_coverage(detector, [0.95] * 30)
    _feed_direction(detector, [0.55] * 30)
    assert detector.assess().grade is DegradationGrade.NONE
    assert detector.evaluate([_signal()]) == []


# ── IC 滑窗衰减 ───────────────────────────────────────────


def test_ic_decay_moderate(detector, alerter):
    _feed_ic(detector, [0.05] * 20 + [0.01] * 10)  # 近窗仅为基线 20%
    warnings = detector.evaluate([_signal()])
    assert len(warnings) == 1
    assert warnings[0].degradation_level == DegradationGrade.MODERATE.value
    assert detector.should_block() is False
    assert alerter.calls[-1]["level"] == LEVEL_ERROR


def test_ic_sign_flip_severe_blocks_dispatch(detector, alerter):
    _feed_ic(detector, [0.05] * 20 + [-0.02] * 10)  # IC 符号翻转
    warnings = detector.evaluate([_signal()])
    assert warnings[0].degradation_level == DegradationGrade.SEVERE.value
    assert warnings[0].suggested_action == "block_dispatch"
    assert detector.should_block() is True
    assert alerter.calls[-1]["level"] == LEVEL_CRITICAL


# ── 覆盖率骤降 ────────────────────────────────────────────


def test_coverage_small_drop_mild(detector, alerter):
    _feed_coverage(detector, [0.95] * 20 + [0.82] * 10)  # 跌 0.13
    warnings = detector.evaluate([_signal()])
    assert warnings[0].degradation_level == DegradationGrade.MILD.value
    assert alerter.calls[-1]["level"] == LEVEL_WARN


def test_coverage_crash_severe(detector):
    _feed_coverage(detector, [0.95] * 20 + [0.30] * 10)  # 跌 0.65
    warnings = detector.evaluate([_signal()])
    assert warnings[0].degradation_level == DegradationGrade.SEVERE.value
    assert detector.should_block() is True


# ── 方向一致性漂移 ────────────────────────────────────────


def test_direction_drift_moderate(detector):
    _feed_direction(detector, [0.70] * 20 + [0.40] * 10)  # 多空比漂移 0.30
    warnings = detector.evaluate([_signal()])
    assert warnings[0].degradation_level == DegradationGrade.MODERATE.value


def test_direction_drift_severe(detector):
    _feed_direction(detector, [0.80] * 20 + [0.20] * 10)  # 漂移 0.60
    warnings = detector.evaluate([_signal()])
    assert warnings[0].degradation_level == DegradationGrade.SEVERE.value


# ── 多维合成 worst-of ─────────────────────────────────────


def test_multi_dimension_worst_of_wins(detector):
    _feed_ic(detector, [0.05] * 20 + [0.04] * 10)  # 平稳
    _feed_coverage(detector, [0.95] * 20 + [0.80] * 10)  # MILD
    _feed_direction(detector, [0.80] * 20 + [0.25] * 10)  # SEVERE
    assessment = detector.assess()
    assert assessment.grade is DegradationGrade.SEVERE
    assert assessment.dimensions["coverage_drop"] == DegradationGrade.MILD.value
    assert assessment.dimensions["direction_drift"] == DegradationGrade.SEVERE.value


# ── 告警路由与去重 ────────────────────────────────────────


def test_alert_dedup_same_grade_and_escalation(detector, alerter):
    _feed_ic(detector, [0.05] * 20 + [0.01] * 10)
    detector.evaluate([_signal()])
    detector.evaluate([_signal()])  # 同级不重复触达
    assert len(alerter.calls) == 1
    _feed_ic(detector, [-0.03] * 10)  # 升级为 SEVERE
    detector.evaluate([_signal()])
    assert len(alerter.calls) == 2
    assert alerter.calls[0]["level"] == LEVEL_ERROR
    assert alerter.calls[1]["level"] == LEVEL_CRITICAL


# ── 审计入 signal_audit ───────────────────────────────────


def test_audit_event_written_on_degradation(detector, audit_events):
    _feed_coverage(detector, [0.95] * 20 + [0.30] * 10)
    detector.evaluate([_signal(factors={"FAC-001": 0.6, "FAC-002": -0.4})])
    assert len(audit_events) == 1
    event = audit_events[0]
    assert event.event_type is SignalEventType.DEGRADED
    assert event.severity is AuditSeverity.CRITICAL
    assert event.source_module == "signal_quality.degradation_detector"
    assert "coverage" in event.description or "覆盖率" in event.description


# ── 下游信号自带降级标记 ───────────────────────────────────


def test_signal_level_degraded_flag_floor_mild(detector):
    warnings = detector.evaluate([_signal(is_degraded=True)])
    assert len(warnings) == 1
    assert warnings[0].degradation_level == DegradationGrade.MILD.value


# ── 契约字段与滑窗恢复 ─────────────────────────────────────


def test_warning_contract_fields(detector):
    _feed_ic(detector, [0.05] * 20 + [0.01] * 10)
    warnings = detector.evaluate([_signal("SIG-9", factors={"FAC-001": 0.6})])
    w = warnings[0]
    assert isinstance(w, SignalDegradationWarning)
    assert w.warning_id
    assert w.idempotency_key
    assert w.reason
    assert "FAC-001" in w.affected_factor_ids


def test_window_slide_recovery_resets_alert(detector, alerter):
    _feed_ic(detector, [0.05] * 20 + [0.01] * 10)
    detector.evaluate([_signal()])
    assert len(alerter.calls) == 1
    _feed_ic(detector, [0.05] * 30)  # 滑窗推出坏样本，恢复平稳
    assert detector.assess().grade is DegradationGrade.NONE
    assert detector.evaluate([_signal()]) == []
    _feed_ic(detector, [0.01] * 10)  # 再次衰减 → 恢复后可重新告警
    detector.evaluate([_signal()])
    assert len(alerter.calls) == 2
