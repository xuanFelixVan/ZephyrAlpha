# [BLUEPRINT] MOD-SELL-010 | docs/03_modules/MOD-SELL-010/
# [MODULE] zephyr.sell_decision.core.sell_signal_accuracy_monitor
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/sell_decision/test_sell_signal_accuracy_monitor.py
# [TTL] permanent
"""sell_signal_accuracy_monitor（卖出信号准确度监控）单元测试。

覆盖：
- 按信号类型聚合命中率（产出供 MOD-SELL-002 的 AccuracyStat）
- 衰退检测：样本充足且命中率低于基线−容差 → degraded + 预警
- 小样本不误报（min_samples 门槛）
- 非法输入 → InvalidAccuracyRecordError
"""

from __future__ import annotations

import pytest

from zephyr.sell_decision.core.sell_signal_collector import SellSignalType
from zephyr.sell_decision.core.sell_signal_accuracy_monitor import (
    InvalidAccuracyRecordError,
    SignalOutcomeRecord,
    evaluate_accuracy,
)


def _rec(stype: SellSignalType, hit: bool) -> SignalOutcomeRecord:
    return SignalOutcomeRecord(signal_type=stype, hit=hit)


def _records(stype: SellSignalType, hits: int, total: int) -> list[SignalOutcomeRecord]:
    return [_rec(stype, True)] * hits + [_rec(stype, False)] * (total - hits)


class TestAggregation:
    def test_accuracy_stat_per_type(self) -> None:
        """TECHNICAL 18/20 → hits=18,total=20。"""
        report = evaluate_accuracy(_records(SellSignalType.TECHNICAL, 18, 20))
        stat = report.by_type[SellSignalType.TECHNICAL]
        assert stat.hits == 18
        assert stat.total == 20

    def test_overall_accuracy(self) -> None:
        """总体命中率=总命中/总样本。"""
        records = _records(SellSignalType.TECHNICAL, 8, 10) + _records(SellSignalType.FUNDAMENTAL, 4, 10)
        report = evaluate_accuracy(records)
        assert report.overall_hits == 12
        assert report.overall_total == 20
        assert report.overall_rate == pytest.approx(0.6)

    def test_multiple_types_tracked_independently(self) -> None:
        records = _records(SellSignalType.TECHNICAL, 9, 10) + _records(SellSignalType.TIME_STOP, 2, 10)
        report = evaluate_accuracy(records)
        assert report.by_type[SellSignalType.TECHNICAL].hits == 9
        assert report.by_type[SellSignalType.TIME_STOP].hits == 2

    def test_empty_records(self) -> None:
        report = evaluate_accuracy([])
        assert report.overall_total == 0
        assert report.by_type == {}


class TestDegradation:
    def test_degraded_when_below_baseline(self) -> None:
        """命中率 0.40，基线 0.60，容差 0.10 → 衰退。"""
        report = evaluate_accuracy(
            _records(SellSignalType.TECHNICAL, 8, 20),
            baseline_rate=0.60,
            degradation_tolerance=0.10,
            min_samples=10,
        )
        assert SellSignalType.TECHNICAL in report.degraded_types
        assert any("TECHNICAL" in w for w in report.warnings)

    def test_not_degraded_when_within_tolerance(self) -> None:
        """命中率 0.55，基线 0.60，容差 0.10 → 不衰退。"""
        report = evaluate_accuracy(
            _records(SellSignalType.TECHNICAL, 11, 20),
            baseline_rate=0.60,
            degradation_tolerance=0.10,
            min_samples=10,
        )
        assert report.degraded_types == ()

    def test_small_sample_not_flagged(self) -> None:
        """样本 < min_samples → 不判衰退（防小样本误报）。"""
        report = evaluate_accuracy(
            _records(SellSignalType.TECHNICAL, 0, 5),
            baseline_rate=0.60,
            degradation_tolerance=0.10,
            min_samples=10,
        )
        assert report.degraded_types == ()


class TestInvalidInput:
    def test_baseline_out_of_range(self) -> None:
        with pytest.raises(InvalidAccuracyRecordError):
            evaluate_accuracy([_rec(SellSignalType.TECHNICAL, True)], baseline_rate=1.5)

    def test_tolerance_out_of_range(self) -> None:
        with pytest.raises(InvalidAccuracyRecordError):
            evaluate_accuracy([_rec(SellSignalType.TECHNICAL, True)], degradation_tolerance=-0.1)

    def test_min_samples_below_one(self) -> None:
        with pytest.raises(InvalidAccuracyRecordError):
            evaluate_accuracy([_rec(SellSignalType.TECHNICAL, True)], min_samples=0)

    def test_wrong_signal_type(self) -> None:
        """signal_type 非 SellSignalType → 拒绝。"""
        bad = SignalOutcomeRecord(signal_type="TECHNICAL", hit=True)  # type: ignore[arg-type]
        with pytest.raises(InvalidAccuracyRecordError):
            evaluate_accuracy([bad])
