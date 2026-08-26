# [BLUEPRINT] MOD-PLAN-022 | docs/03_modules/_domain_plan_engine/plan_deviation_monitor/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-PLAN-022 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.plan_engine.test_plan_deviation_monitor
# [TESTS] src/zephyr/plan_engine/plan_deviation_monitor.py
"""MOD-PLAN-022 单元测试：plan_deviation_monitor 计划偏差检测与机会评估。

蓝图验收（B10-01479/CAND-PLAN-016，A1 模块38）：
盘中计划偏差实时监控（实际vs计划偏离>2σ判定，有利持有/不利纠错分类）
+ 计划外强信号三重闸（z>3σ且E>0.5%且计划外仓位≤20%）+ 评估记录留痕。
留痕/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime
from decimal import Decimal

import pytest

pytest.importorskip(
    "zephyr.plan_engine.plan_deviation_monitor",
    reason="plan_deviation_monitor not importable",
)

from zephyr.plan_engine.plan_deviation_monitor import (  # noqa: E402
    ACTION_CORRECT,
    ACTION_HOLD,
    ACTION_NONE,
    DeviationAssessment,
    DeviationKind,
    OffplanSignalAssessment,
    PlanDeviationError,
    PlanDeviationMonitor,
)

_T0 = datetime.datetime(2026, 8, 26, 10, 30, 0)


def _monitor(records: list | None = None, **kwargs) -> PlanDeviationMonitor:
    kwargs.setdefault("clock", lambda: _T0)
    if records is not None:
        kwargs["record_sink"] = lambda r: records.append(r)
    return PlanDeviationMonitor(**kwargs)


def _deviation(monitor: PlanDeviationMonitor, actual: str = "0.04", **kwargs):
    kwargs.setdefault("symbol", "600000.SH")
    kwargs.setdefault("planned_return", Decimal("0.01"))
    kwargs.setdefault("actual_return", Decimal(actual))
    kwargs.setdefault("sigma", Decimal("0.01"))
    return monitor.assess_deviation(**kwargs)


def _offplan(monitor: PlanDeviationMonitor, **kwargs):
    kwargs.setdefault("signal_id", "sig-1")
    kwargs.setdefault("z_score", Decimal("3.5"))
    kwargs.setdefault("expected_return", Decimal("0.006"))
    kwargs.setdefault("offplan_position_ratio", Decimal("0.1"))
    return monitor.assess_offplan_signal(**kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# 初始化
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_default_ok(self) -> None:
        assert _monitor() is not None

    def test_deviation_z_invalid_raises(self) -> None:
        with pytest.raises(PlanDeviationError):
            _monitor(deviation_z_threshold=Decimal("0"))
        with pytest.raises(PlanDeviationError):
            _monitor(deviation_z_threshold=2.0)  # 拒绝 float

    def test_strong_signal_z_invalid_raises(self) -> None:
        with pytest.raises(PlanDeviationError):
            _monitor(strong_signal_z=Decimal("-3"))

    def test_ratio_threshold_invalid_raises(self) -> None:
        with pytest.raises(PlanDeviationError):
            _monitor(min_expected_return=Decimal("-0.005"))
        with pytest.raises(PlanDeviationError):
            _monitor(max_offplan_position_ratio=Decimal("0"))
        with pytest.raises(PlanDeviationError):
            _monitor(max_offplan_position_ratio=Decimal("1.5"))


# ──────────────────────────────────────────────────────────────────────────────
# 计划偏差实时监控
# ──────────────────────────────────────────────────────────────────────────────


class TestDeviation:
    def test_within_2sigma_not_breached(self) -> None:
        a = _deviation(_monitor(), actual="0.015")  # z=1.5
        assert a.breached is False
        assert a.kind is DeviationKind.NONE
        assert a.action == ACTION_NONE

    def test_exactly_2sigma_not_breached(self) -> None:
        a = _deviation(_monitor(), actual="0.03")  # z=2 恰边界，严格>才判偏离
        assert a.breached is False
        assert a.z_score == Decimal("2")

    def test_favorable_deviation_hold(self) -> None:
        a = _deviation(_monitor(), actual="0.04")  # z=+3
        assert a.breached is True
        assert a.kind is DeviationKind.FAVORABLE
        assert a.action == ACTION_HOLD
        assert a.z_score == Decimal("3")
        assert a.deviation == Decimal("0.03")

    def test_adverse_deviation_correct(self) -> None:
        a = _deviation(_monitor(), actual="-0.02")  # z=-3
        assert a.breached is True
        assert a.kind is DeviationKind.ADVERSE
        assert a.action == ACTION_CORRECT
        assert a.z_score == Decimal("-3")

    def test_sigma_non_positive_raises(self) -> None:
        with pytest.raises(PlanDeviationError):
            _deviation(_monitor(), sigma=Decimal("0"))
        with pytest.raises(PlanDeviationError):
            _deviation(_monitor(), sigma=Decimal("-0.01"))

    def test_invalid_inputs_raise(self) -> None:
        with pytest.raises(PlanDeviationError):  # 空标的
            _deviation(_monitor(), symbol="")
        with pytest.raises(PlanDeviationError):  # 非 Decimal
            _deviation(_monitor(), sigma=0.01)


# ──────────────────────────────────────────────────────────────────────────────
# 计划外强信号三重闸
# ──────────────────────────────────────────────────────────────────────────────


class TestOffplanSignal:
    def test_all_gates_pass(self) -> None:
        a = _offplan(_monitor())
        assert a.gate_z is True
        assert a.gate_expected is True
        assert a.gate_position is True
        assert a.passed is True

    def test_z_exactly_3_blocked(self) -> None:
        a = _offplan(_monitor(), z_score=Decimal("3"))  # 严格>3σ
        assert a.gate_z is False
        assert a.passed is False

    def test_expected_exactly_half_percent_blocked(self) -> None:
        a = _offplan(_monitor(), expected_return=Decimal("0.005"))  # 严格>0.5%
        assert a.gate_expected is False
        assert a.passed is False

    def test_position_exactly_20pct_allowed(self) -> None:
        a = _offplan(_monitor(), offplan_position_ratio=Decimal("0.2"))  # ≤20% 含等号
        assert a.gate_position is True
        assert a.passed is True

    def test_position_over_20pct_blocked(self) -> None:
        a = _offplan(_monitor(), offplan_position_ratio=Decimal("0.25"))
        assert a.gate_position is False
        assert a.passed is False

    def test_ratio_out_of_range_raises(self) -> None:
        with pytest.raises(PlanDeviationError):
            _offplan(_monitor(), offplan_position_ratio=Decimal("1.2"))
        with pytest.raises(PlanDeviationError):
            _offplan(_monitor(), offplan_position_ratio=Decimal("-0.1"))

    def test_invalid_inputs_raise(self) -> None:
        with pytest.raises(PlanDeviationError):  # 空信号
            _offplan(_monitor(), signal_id="")
        with pytest.raises(PlanDeviationError):  # 非 Decimal
            _offplan(_monitor(), z_score=3.5)


# ──────────────────────────────────────────────────────────────────────────────
# 留痕
# ──────────────────────────────────────────────────────────────────────────────


class TestRecords:
    def test_sink_receives_both_types(self) -> None:
        records: list = []
        m = _monitor(records)
        _deviation(m)
        _offplan(m)
        assert len(records) == 2
        assert isinstance(records[0], DeviationAssessment)
        assert isinstance(records[1], OffplanSignalAssessment)

    def test_in_memory_records_accumulate(self) -> None:
        m = _monitor()
        _deviation(m)
        _offplan(m)
        _offplan(m)
        assert len(m.records()) == 3
        assert isinstance(m.records()[0], DeviationAssessment)

    def test_sink_exception_not_blocking(self) -> None:
        def _boom(_r) -> None:
            raise RuntimeError("sink down")

        m = PlanDeviationMonitor(clock=lambda: _T0, record_sink=_boom)
        a = _deviation(m)
        assert a.symbol == "600000.SH"  # 留痕失败不阻断评估
        assert len(m.records()) == 1

    def test_clock_injected(self) -> None:
        m = _monitor()
        assert _deviation(m).assessed_at == _T0
        assert _offplan(m).assessed_at == _T0


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_input_same_output(self) -> None:
        assert _deviation(_monitor()) == _deviation(_monitor())
        assert _offplan(_monitor()) == _offplan(_monitor())
