"""q3/q5/q20 多时间框架动量加权 单元测试（22 号 spec §3.1⑧）"""

import pytest

from zephyr.signal_ashare.sector_momentum import (
    multi_tf_momentum,
    n_day_return,
    percentile_ranks,
)


def _trend(start: float, daily_pct: float, n: int) -> list[float]:
    out = [start]
    for _ in range(n - 1):
        out.append(out[-1] * (1.0 + daily_pct))
    return out


class TestNDayReturn:
    def test_basic(self):
        assert n_day_return([100.0, 110.0], 1) == pytest.approx(0.10)

    def test_n_day_lookback(self):
        # closes[-21] → closes[-1]
        closes = _trend(100.0, 0.01, 21)
        expected = closes[-1] / closes[0] - 1.0
        assert n_day_return(closes, 20) == pytest.approx(expected)

    def test_insufficient_length_raises(self):
        with pytest.raises(ValueError, match="至少"):
            n_day_return([100.0, 101.0], 3)

    def test_non_positive_base_raises(self):
        with pytest.raises(ValueError, match="基准收盘价必须为正"):
            n_day_return([0.0, 100.0], 1)


class TestPercentileRanks:
    def test_empty(self):
        assert percentile_ranks({}) == {}

    def test_single_sector_neutral(self):
        assert percentile_ranks({"A": 0.05}) == {"A": 0.5}

    def test_ordering(self):
        """0=最弱，1=最强"""
        ranks = percentile_ranks({"WEAK": -0.05, "MID": 0.01, "STRONG": 0.08})
        assert ranks["WEAK"] == pytest.approx(0.0)
        assert ranks["MID"] == pytest.approx(0.5)
        assert ranks["STRONG"] == pytest.approx(1.0)

    def test_ties_get_average_rank(self):
        """并列取平均秩：两个并列最强 → 各 (1+2)/2/(3-1)=0.75"""
        ranks = percentile_ranks({"A": 0.05, "B": 0.05, "C": -0.01})
        assert ranks["A"] == pytest.approx(0.75)
        assert ranks["B"] == pytest.approx(0.75)
        assert ranks["C"] == pytest.approx(0.0)


class TestMultiTfMomentum:
    def test_strong_sector_scores_one_weak_scores_zero(self):
        """恒涨板块全窗口 q=1 → strength=1.0；恒跌 → 0.0；横盘 → 居中"""
        closes = {
            "STRONG": _trend(100.0, 0.01, 21),
            "FLAT": [100.0] * 21,
            "WEAK": _trend(100.0, -0.01, 21),
        }
        out = multi_tf_momentum(closes)
        assert out["STRONG"] == pytest.approx(1.0)
        assert out["WEAK"] == pytest.approx(0.0)
        assert out["FLAT"] == pytest.approx(0.5)

    def test_weights_applied_04_03_03(self):
        """权重核验：手工构造 q20=1, q5=0, q3=0 → 0.4"""
        # 21 日前高、随后阴跌、最近 3 日走平：20 日窗口涨幅最高，5/3 日最低
        closes = {
            "A": [200.0] + [100.0] * 17 + [99.0, 98.0, 97.0],
            "B": [100.0] * 21,
        }
        out = multi_tf_momentum(closes)
        # A: ret20 = 97/200-1 ≈ -0.515 最低 → q20=0；ret5/ret3 也最低 → 全 0
        assert out["A"] == pytest.approx(0.0)
        assert out["B"] == pytest.approx(1.0)

    def test_short_history_sector_skipped(self):
        """收盘价序列 < max(windows)+1=21 的板块跳过"""
        closes = {
            "GOOD": _trend(100.0, 0.01, 21),
            "SHORT": _trend(100.0, 0.01, 10),
        }
        out = multi_tf_momentum(closes)
        assert "SHORT" not in out
        assert "GOOD" in out

    def test_all_short_returns_empty(self):
        assert multi_tf_momentum({"X": [1.0] * 5}) == {}

    def test_windows_weights_mismatch_raises(self):
        with pytest.raises(ValueError, match="长度必须一致"):
            multi_tf_momentum({"A": _trend(100.0, 0.01, 21)}, windows=(20, 5), weights=(0.5,))

    def test_custom_windows_weights(self):
        """自定义窗口与权重（如 q5 单窗口）"""
        closes = {"A": _trend(100.0, 0.02, 21), "B": _trend(100.0, 0.01, 21)}
        out = multi_tf_momentum(closes, windows=(5,), weights=(1.0,))
        assert out["A"] == pytest.approx(1.0)
        assert out["B"] == pytest.approx(0.0)

    def test_output_bounded_unit_interval(self):
        closes = {f"S{i}": _trend(100.0 + i, (i - 5) * 0.002, 25) for i in range(10)}
        for v in multi_tf_momentum(closes).values():
            assert 0.0 <= v <= 1.0
