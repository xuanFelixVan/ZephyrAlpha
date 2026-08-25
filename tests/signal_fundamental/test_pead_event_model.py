# [BLUEPRINT] MOD-SIG-110 | docs/03_modules/_domain_fundamental_signal/pead_event_model/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIG-110 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.signal_fundamental.test_pead_event_model
# [TESTS] src/zephyr/signal_fundamental/pead_event_model.py
"""MOD-SIG-110 单元测试：pead_event_model 财报季事件驱动与PEAD模型。

蓝图验收（B10-01417/CAND-FUNDAMEN-001，A1 §4模块49）：
SUE=(实际EPS-一致预期)/|一致预期| 已知答案 + 五档分档边界 + 20日漂移收益
统计 + 财报季持仓标记（披露截止窗口相交判定）。全部内存构造，不触网不触库。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.signal_fundamental.pead_event_model",
    reason="pead_event_model not importable",
)

from zephyr.signal_fundamental.pead_event_model import (  # noqa: E402
    EarningsEvent,
    PeadEventError,
    PeadEventModel,
    SueThresholds,
    classify_sue,
    compute_drift_return,
    compute_sue,
    earnings_season_windows,
    SueBand,
)


# ──────────────────────────────────────────────────────────────────────────────
# SUE 计算（已知答案）
# ──────────────────────────────────────────────────────────────────────────────


class TestComputeSue:
    def test_positive_surprise(self) -> None:
        assert compute_sue(1.2, 1.0) == pytest.approx(0.2)

    def test_negative_surprise(self) -> None:
        assert compute_sue(0.8, 1.0) == pytest.approx(-0.2)

    def test_negative_consensus_uses_abs(self) -> None:
        # 一致预期为负：分母取绝对值，符号由分子决定
        assert compute_sue(-0.5, -1.0) == pytest.approx(0.5)

    def test_near_zero_consensus_not_computable(self) -> None:
        assert compute_sue(1.0, 1e-9) is None

    def test_non_finite_raises(self) -> None:
        with pytest.raises(PeadEventError):
            compute_sue(float("nan"), 1.0)
        with pytest.raises(PeadEventError):
            compute_sue(1.0, float("inf"))

    def test_custom_eps_floor(self) -> None:
        assert compute_sue(1.0, 0.005, eps_floor=0.01) is None
        assert compute_sue(1.0, 0.005, eps_floor=0.001) == pytest.approx(199.0)


# ──────────────────────────────────────────────────────────────────────────────
# SUE 分档（边界含语义：sue < 阈值 严格小于）
# ──────────────────────────────────────────────────────────────────────────────


class TestClassifySue:
    @pytest.mark.parametrize(
        ("sue", "expected"),
        [
            (-3.0, SueBand.STRONG_NEGATIVE),
            (-2.0, SueBand.NEGATIVE),  # 边界：不小于 -2.0 → NEGATIVE
            (-1.0, SueBand.NEGATIVE),
            (-0.5, SueBand.NEUTRAL),  # 边界
            (0.0, SueBand.NEUTRAL),
            (0.5, SueBand.POSITIVE),  # 边界
            (1.5, SueBand.POSITIVE),
            (2.0, SueBand.STRONG_POSITIVE),  # 边界
            (3.5, SueBand.STRONG_POSITIVE),
        ],
    )
    def test_bands(self, sue: float, expected: SueBand) -> None:
        assert classify_sue(sue) is expected

    def test_threshold_validation(self) -> None:
        with pytest.raises(PeadEventError):
            SueThresholds(strong_neg=-0.5, neg=-2.0)  # 非递增
        with pytest.raises(PeadEventError):
            classify_sue(float("nan"))


# ──────────────────────────────────────────────────────────────────────────────
# 漂移收益统计（20 日）
# ──────────────────────────────────────────────────────────────────────────────


class TestDriftReturn:
    def test_known_answer_20d(self) -> None:
        closes = [100.0] + [100.0] * 19 + [110.0]
        assert compute_drift_return(closes, 0, days=20) == pytest.approx(0.10)

    def test_insufficient_series_returns_none(self) -> None:
        closes = [100.0] * 10
        assert compute_drift_return(closes, 0, days=20) is None

    def test_negative_drift(self) -> None:
        closes = [100.0] + [100.0] * 19 + [95.0]
        assert compute_drift_return(closes, 0, days=20) == pytest.approx(-0.05)

    def test_invalid_inputs_raise(self) -> None:
        with pytest.raises(PeadEventError):
            compute_drift_return([], 0)
        with pytest.raises(PeadEventError):
            compute_drift_return([100.0, float("nan")], 0)
        with pytest.raises(PeadEventError):
            compute_drift_return([100.0] * 25, 0, days=0)
        with pytest.raises(PeadEventError):
            compute_drift_return([0.0] * 25, 0, days=20)  # 基准价为 0
        with pytest.raises(PeadEventError):
            compute_drift_return([100.0] * 25, -1, days=20)


# ──────────────────────────────────────────────────────────────────────────────
# 事件评估（SUE+分档+漂移收益 聚合）
# ──────────────────────────────────────────────────────────────────────────────


class TestEvaluateEvent:
    def test_computable_full(self) -> None:
        model = PeadEventModel()
        event = EarningsEvent(
            symbol="600000.SH",
            announce_date=datetime.date(2026, 4, 25),
            actual_eps=1.3,
            consensus_eps=1.0,
        )
        closes = [100.0] + [100.0] * 19 + [112.0]
        result = model.evaluate(event, closes, 0)
        assert result.computable is True
        assert result.sue == pytest.approx(0.3)
        assert result.band is SueBand.NEUTRAL
        assert result.drift_return == pytest.approx(0.12)
        assert result.drift_days == 20

    def test_near_zero_consensus_not_computable_keeps_trace(self) -> None:
        model = PeadEventModel()
        event = EarningsEvent(
            symbol="600000.SH",
            announce_date=datetime.date(2026, 4, 25),
            actual_eps=1.3,
            consensus_eps=0.0,
        )
        result = model.evaluate(event, [100.0] * 25, 0)
        assert result.computable is False
        assert result.sue is None
        assert result.band is None
        assert "consensus" in result.detail  # 留痕不静默丢弃

    def test_strong_positive_band_with_drift(self) -> None:
        model = PeadEventModel()
        event = EarningsEvent(
            symbol="000001.SZ",
            announce_date=datetime.date(2026, 8, 20),
            actual_eps=3.5,
            consensus_eps=1.0,
        )
        result = model.evaluate(event, [100.0] * 25, 0)
        assert result.band is SueBand.STRONG_POSITIVE

    def test_invalid_event_raises(self) -> None:
        model = PeadEventModel()
        with pytest.raises(PeadEventError):
            model.evaluate(
                EarningsEvent(
                    symbol="",
                    announce_date=datetime.date(2026, 4, 25),
                    actual_eps=1.0,
                    consensus_eps=1.0,
                ),
                [100.0] * 25,
                0,
            )


# ──────────────────────────────────────────────────────────────────────────────
# 财报季窗口与持仓标记
# ──────────────────────────────────────────────────────────────────────────────


class TestEarningsSeason:
    def test_three_deadline_windows(self) -> None:
        windows = earnings_season_windows(2026)
        assert len(windows) == 3
        deadlines = [w.deadline for w in windows]
        assert deadlines == [
            datetime.date(2026, 4, 30),
            datetime.date(2026, 8, 31),
            datetime.date(2026, 10, 31),
        ]

    def test_pre_window_start(self) -> None:
        windows = earnings_season_windows(2026, pre_window=10)
        assert windows[0].window_start == datetime.date(2026, 4, 20)
        assert windows[0].window_end == datetime.date(2026, 4, 30)

    def test_exposure_on_intersect(self) -> None:
        model = PeadEventModel()
        mark = model.earnings_season_mark(
            "600000.SH",
            datetime.date(2026, 4, 15),
            datetime.date(2026, 5, 5),
            year=2026,
        )
        assert mark.in_season is True
        assert mark.exposure is True
        assert mark.window_start == datetime.date(2026, 4, 20)
        assert mark.window_end == datetime.date(2026, 4, 30)

    def test_no_exposure_outside_windows(self) -> None:
        model = PeadEventModel()
        mark = model.earnings_season_mark(
            "600000.SH",
            datetime.date(2026, 6, 1),
            datetime.date(2026, 6, 30),
            year=2026,
        )
        assert mark.in_season is False
        assert mark.exposure is False
        assert mark.window_start is None

    def test_hold_range_validation(self) -> None:
        model = PeadEventModel()
        with pytest.raises(PeadEventError):
            model.earnings_season_mark(
                "600000.SH",
                datetime.date(2026, 5, 5),
                datetime.date(2026, 4, 15),  # 起止倒置
                year=2026,
            )

    def test_determinism(self) -> None:
        model = PeadEventModel()
        event = EarningsEvent(
            symbol="600000.SH",
            announce_date=datetime.date(2026, 4, 25),
            actual_eps=1.3,
            consensus_eps=1.0,
        )
        closes = [100.0] + [100.0] * 19 + [112.0]
        assert model.evaluate(event, closes, 0) == model.evaluate(event, closes, 0)
