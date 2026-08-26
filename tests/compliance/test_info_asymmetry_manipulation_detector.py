# [BLUEPRINT] MOD-CMP-014 | docs/03_modules/_domain_compliance/info_asymmetry_manipulation_detector/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-CMP-014 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.compliance.test_info_asymmetry_manipulation_detector
# [TESTS] src/zephyr/compliance/info_asymmetry_manipulation_detector.py
"""MOD-CMP-014 单元测试：info_asymmetry_manipulation_detector 信息不对称期与操纵检测器。

蓝图验收（B10-01426/CAND-CMP-005，§0定位/§1规则）：
空窗期判定（披露间隔>90天/11月-次年4月30日窗口）+ z>2 异常波动扫描 +
幌骗/对敲/尾盘三模式操纵评分（数据注入）+ 回避名单输出。时钟/数据全注入，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.compliance.info_asymmetry_manipulation_detector",
    reason="info_asymmetry_manipulation_detector not importable",
)

from zephyr.compliance.info_asymmetry_manipulation_detector import (  # noqa: E402
    DetectorConfig,
    InfoAsymmetryError,
    InfoAsymmetryManipulationDetector,
    ManipulationFeatures,
    ManipulationMode,
)

_T0 = datetime.datetime(2026, 8, 25, 15, 0, 0)


def _detector(config: DetectorConfig | None = None) -> InfoAsymmetryManipulationDetector:
    return InfoAsymmetryManipulationDetector(clock=lambda: _T0, config=config)


def _features(**kw) -> ManipulationFeatures:
    base = dict(
        deviation=0.0,
        cancel_rate=0.0,
        order_intervals=(1.0, 2.0),
        volume_concentration=0.0,
        tail_volume_ratio=0.0,
        tail_deviation=0.0,
        self_trade_ratio=0.0,
    )
    base.update(kw)
    return ManipulationFeatures(**base)


# ──────────────────────────────────────────────────────────────────────────────
# 空窗期判定
# ──────────────────────────────────────────────────────────────────────────────


class TestAsymmetryWindow:
    def test_gap_over_90_days(self) -> None:
        d = _detector()
        d.register_disclosure("600519", datetime.date(2026, 1, 1))
        assert d.is_asymmetry_window("600519", datetime.date(2026, 5, 1)) is True  # 间隔120天

    def test_gap_within_90_outside_statutory_window(self) -> None:
        d = _detector()
        d.register_disclosure("600519", datetime.date(2026, 6, 1))
        assert d.is_asymmetry_window("600519", datetime.date(2026, 8, 1)) is False  # 间隔61天且8月

    def test_statutory_window_november(self) -> None:
        d = _detector()
        d.register_disclosure("600519", datetime.date(2026, 10, 20))
        assert d.is_asymmetry_window("600519", datetime.date(2026, 11, 15)) is True  # 11月窗口

    def test_statutory_window_april_30(self) -> None:
        d = _detector()
        d.register_disclosure("600519", datetime.date(2026, 3, 1))
        assert d.is_asymmetry_window("600519", datetime.date(2026, 4, 30)) is True

    def test_unknown_symbol_raises(self) -> None:
        d = _detector()
        with pytest.raises(InfoAsymmetryError):
            d.is_asymmetry_window("ghost", datetime.date(2026, 8, 1))

    def test_empty_symbol_raises(self) -> None:
        d = _detector()
        with pytest.raises(InfoAsymmetryError):
            d.register_disclosure("", datetime.date(2026, 1, 1))


# ──────────────────────────────────────────────────────────────────────────────
# z 扫描
# ──────────────────────────────────────────────────────────────────────────────


class TestZScan:
    def test_z_over_threshold(self) -> None:
        d = _detector()
        # 基准 [0.01, -0.01, 0.01, -0.01] 均值0 方差0.0001；末日 0.05 → z=5
        z = d.z_scan([0.01, -0.01, 0.01, -0.01, 0.05])
        assert z == pytest.approx(5.0)
        assert abs(z) > 2.0

    def test_z_normal(self) -> None:
        d = _detector()
        z = d.z_scan([0.01, -0.01, 0.01, -0.01, 0.005])
        assert abs(z) <= 2.0

    def test_insufficient_samples_raises(self) -> None:
        d = _detector()
        with pytest.raises(InfoAsymmetryError):
            d.z_scan([0.01])

    def test_zero_variance_raises(self) -> None:
        d = _detector()
        with pytest.raises(InfoAsymmetryError):
            d.z_scan([0.01, 0.01, 0.01, 0.05])

    def test_non_finite_raises(self) -> None:
        d = _detector()
        with pytest.raises(InfoAsymmetryError):
            d.z_scan([0.01, float("nan"), 0.02])


# ──────────────────────────────────────────────────────────────────────────────
# 三模式操纵评分
# ──────────────────────────────────────────────────────────────────────────────


class TestManipulationScore:
    def test_spoofing_high(self) -> None:
        d = _detector()
        scores = d.score_manipulation(_features(cancel_rate=0.8, deviation=0.05))
        assert scores[ManipulationMode.SPOOFING] == pytest.approx(0.7 * 0.8 + 0.3 * 0.5)
        assert scores[ManipulationMode.SPOOFING] >= 0.6

    def test_wash_trade_high(self) -> None:
        d = _detector()
        scores = d.score_manipulation(_features(self_trade_ratio=0.9, volume_concentration=0.8))
        assert scores[ManipulationMode.WASH_TRADE] == pytest.approx(0.6 * 0.9 + 0.4 * 0.8)

    def test_tail_high(self) -> None:
        d = _detector()
        scores = d.score_manipulation(_features(tail_volume_ratio=0.7, tail_deviation=0.04))
        assert scores[ManipulationMode.TAIL] == pytest.approx(0.5 * 0.7 + 0.5 * 0.4)

    def test_all_zero_clean(self) -> None:
        d = _detector()
        scores = d.score_manipulation(_features())
        assert all(v == 0.0 for v in scores.values())

    def test_score_clamped_to_one(self) -> None:
        d = _detector()
        scores = d.score_manipulation(_features(cancel_rate=1.0, deviation=1.0))
        assert scores[ManipulationMode.SPOOFING] <= 1.0

    def test_ratio_out_of_range_raises(self) -> None:
        d = _detector()
        with pytest.raises(InfoAsymmetryError):
            d.score_manipulation(_features(cancel_rate=1.5))

    def test_negative_deviation_raises(self) -> None:
        d = _detector()
        with pytest.raises(InfoAsymmetryError):
            d.score_manipulation(_features(deviation=-0.01))

    def test_negative_interval_raises(self) -> None:
        d = _detector()
        with pytest.raises(InfoAsymmetryError):
            d.score_manipulation(_features(order_intervals=(-1.0,)))


# ──────────────────────────────────────────────────────────────────────────────
# 综合扫描 + 回避名单
# ──────────────────────────────────────────────────────────────────────────────


class TestScanAndAvoidList:
    def _seeded_detector(self) -> InfoAsymmetryManipulationDetector:
        d = _detector()
        d.register_disclosure("600519", datetime.date(2026, 6, 1))   # 非空窗
        d.register_disclosure("000001", datetime.date(2026, 1, 1))   # 空窗（>90天）
        return d

    def test_scan_suspected_adds_avoidance(self) -> None:
        d = self._seeded_detector()
        report = d.scan(
            "600519", datetime.date(2026, 8, 25),
            [0.01, -0.01, 0.01, -0.01, 0.005],
            _features(cancel_rate=0.9, deviation=0.08),
        )
        assert report.suspected is True
        assert report.asymmetry_window is False
        assert d.avoid_symbols() == ("600519",)
        entry = d.avoid_list()[0]
        assert "spoofing" in entry.reasons

    def test_scan_asymmetry_and_anomaly_reasons(self) -> None:
        d = self._seeded_detector()
        report = d.scan(
            "000001", datetime.date(2026, 8, 25),
            [0.01, -0.01, 0.01, -0.01, 0.05],
            _features(),
        )
        assert report.asymmetry_window is True
        assert report.volatility_anomaly is True
        assert report.suspected is False  # 无操纵模式命中
        entry = d.avoid_list()[0]
        assert "info_asymmetry_window" in entry.reasons
        assert any(r.startswith("volatility_z") for r in entry.reasons)

    def test_scan_clean_no_avoidance(self) -> None:
        d = self._seeded_detector()
        report = d.scan(
            "600519", datetime.date(2026, 8, 25),
            [0.01, -0.01, 0.01, -0.01, 0.005],
            _features(),
        )
        assert report.suspected is False
        assert d.avoid_list() == ()

    def test_avoidance_keeps_higher_score(self) -> None:
        d = self._seeded_detector()
        d.scan("600519", datetime.date(2026, 8, 25),
               [0.01, -0.01, 0.01, -0.01, 0.005], _features(cancel_rate=0.9, deviation=0.08))
        first_score = d.avoid_list()[0].score
        d.scan("600519", datetime.date(2026, 8, 25),
               [0.01, -0.01, 0.01, -0.01, 0.005], _features(cancel_rate=0.65))
        assert len(d.avoid_list()) == 1
        assert d.avoid_list()[0].score == first_score  # 低分不覆盖

    def test_avoid_list_sorted(self) -> None:
        d = self._seeded_detector()
        d.register_disclosure("000002", datetime.date(2026, 1, 1))
        d.scan("000002", datetime.date(2026, 8, 25),
               [0.01, -0.01, 0.01, -0.01, 0.005], _features())
        d.scan("000001", datetime.date(2026, 8, 25),
               [0.01, -0.01, 0.01, -0.01, 0.005], _features())
        assert d.avoid_symbols() == ("000001", "000002")

    def test_deterministic_same_input(self) -> None:
        d1 = self._seeded_detector()
        d2 = self._seeded_detector()
        r1 = d1.scan("600519", datetime.date(2026, 8, 25),
                     [0.01, -0.01, 0.01, -0.01, 0.05], _features(cancel_rate=0.8))
        r2 = d2.scan("600519", datetime.date(2026, 8, 25),
                     [0.01, -0.01, 0.01, -0.01, 0.05], _features(cancel_rate=0.8))
        assert r1 == r2

    def test_invalid_config_raises(self) -> None:
        with pytest.raises(InfoAsymmetryError):
            _detector(DetectorConfig(z_threshold=0.0))
        with pytest.raises(InfoAsymmetryError):
            _detector(DetectorConfig(score_threshold=1.5))
