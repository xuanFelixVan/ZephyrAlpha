# [BLUEPRINT] MOD-BT-090 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_three_high_screen
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; pandas; numpy
# [CONSUMERS] MOD-BT-090 three_high_screen 循环验收（tests 同批）
# [STARTUP] manual
# [INVARIANTS] 纯函数测试零 IO（禁触生产 data/ 路径）；构造 stats 走聚合函数与手工行双路
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-090 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FAC-E1D 三高筛选纯函数核单测——评分/假说文本/候选 id/出生证/环节聚合，零 IO。"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts.backtest.three_high_screen import (
    aggregate_sector_stats,
    attach_birth_certificate,
    build_hypothesis,
    make_candidate_id,
    score_three_high,
    winsor_z,
)


def _fake_stats(n: int = 12, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "sector": [f"环节{i}" for i in range(n)],
        "members": rng.integers(5, 40, n),
        "fin_coverage": rng.uniform(0.6, 1.0, n),
        "rev_yoy_med": rng.normal(10, 15, n),
        "profit_yoy_med": rng.normal(5, 20, n),
        "gross_margin_med": rng.uniform(5, 60, n),
        "net_margin_med": rng.uniform(0, 30, n),
        "cust_top5_med": rng.uniform(10, 80, n),
        "hhi_med": rng.uniform(100, 4000, n),
        "downstream_breadth": rng.uniform(0, 20, n),
        "supply_pressure": rng.uniform(0, 20, n),
    })


class TestWinsorZ:
    def test_zero_variance_returns_zeros(self):
        s = pd.Series([5.0, 5.0, 5.0, 5.0])
        assert (winsor_z(s) == 0.0).all()

    def test_monotonic_and_bounded(self):
        s = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 100.0])  # 100 是极值
        z = winsor_z(s)
        assert z.is_monotonic_increasing
        assert np.isfinite(z).all() and z.abs().max() < 5.0  # winsorize 后 z 有界

    def test_nan_filled_as_zero(self):
        s = pd.Series([1.0, 2.0, np.nan, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        assert winsor_z(s).isna().sum() == 0


class TestScoreThreeHigh:
    def test_ranking_matches_total_z_desc(self):
        out = score_three_high(_fake_stats())
        assert out["total_z"].is_monotonic_decreasing
        assert list(out["rank"]) == list(range(1, len(out) + 1))

    def test_weights_override_changes_order(self):
        base = score_three_high(_fake_stats())
        tilted = score_three_high(_fake_stats(), weights={"chokepoint": 1.0, "growth": 0.0,
                                                          "margin": 0.0, "barrier": 0.0})
        assert not base["sector"].tolist() == tilted["sector"].tolist() or (
            base["total_z"].tolist() != tilted["total_z"].tolist())

    def test_flags_are_tag_union_or_none(self):
        out = score_three_high(_fake_stats(seed=3))
        valid = {"高增长", "高利润", "高壁垒", "咽喉", "none"}
        for tags in out["three_high_flags"]:
            assert set(tags.split("+")) <= valid

    def test_deterministic(self):
        a = score_three_high(_fake_stats(seed=11))
        b = score_three_high(_fake_stats(seed=11))
        pd.testing.assert_frame_equal(a, b)


class TestCandidateIdAndHypothesis:
    def test_candidate_id_stable_md5_12(self):
        assert make_candidate_id("光模块") == make_candidate_id("光模块")
        assert make_candidate_id("光模块") != make_candidate_id("光模块 ")
        assert len(make_candidate_id("x")) == len("CAND-") + 12
        assert make_candidate_id("x").startswith("CAND-")

    def test_hypothesis_deterministic_and_informative(self):
        row = score_three_high(_fake_stats(n=6, seed=5)).iloc[0]
        h1, h2 = build_hypothesis(row), build_hypothesis(row)
        assert h1 == h2
        assert row["sector"] in h1
        for token in ("高增长", "高壁垒", "高利润", "毛利率", "成员"):
            assert token in h1


class TestBirthCertificate:
    def test_machine_written_fields(self):
        df = score_three_high(_fake_stats(n=4)).head(2)
        out = attach_birth_certificate(df, batch_id="E1D-20260914-000000")
        assert (out["birth_channel"] == "D").all()
        assert (out["birth_batch"] == "E1D-20260914-000000").all()
        assert out["birth_source"].str.contains("ig_fact").all()

    def test_no_mutation_of_input(self):
        df = score_three_high(_fake_stats(n=4))
        before = list(df.columns)
        attach_birth_certificate(df, batch_id="E1D-x")
        assert list(df.columns) == before


class TestAggregateSectorStats:
    def _inputs(self):
        member = pd.DataFrame({
            "sector": ["甲"] * 3 + ["乙"] * 2,
            "symbol": ["600000.SH", "000001.SZ", "600519.SH", "300750.SZ", "002594.SZ"],
            "n": [1] * 5,
        })
        fin = pd.DataFrame({
            "symbol": ["600000.SH", "000001.SZ", "600519.SH", "300750.SZ"],
            "rev_yoy": [10.0, 20.0, -5.0, 30.0],
            "profit_yoy": [5.0, 12.0, -8.0, 25.0],
            "gross_margin": [30.0, 25.0, 91.0, 20.0],
            "net_margin": [10.0, 8.0, 50.0, 5.0],
        })
        choke = pd.DataFrame({
            "symbol": ["600000.SH", "600519.SH"],
            "downstream_breadth": [7.0, 3.0],
            "supply_pressure": [2.0, 9.0],
        })
        return member, fin, choke

    def test_min_members_filters_small_sectors(self):
        member, fin, choke = self._inputs()
        stats = aggregate_sector_stats(member, fin, choke, min_members=3)
        assert stats["sector"].tolist() == ["甲"]

    def test_coverage_fillna_and_counts(self):
        member, fin, choke = self._inputs()
        stats = aggregate_sector_stats(member, fin, choke, min_members=2, min_coverage=0.0)
        row = stats.set_index("sector").loc["甲"]
        assert row["members"] == 3
        assert abs(row["fin_coverage"] - 1.0) < 1e-9
        row2 = stats.set_index("sector").loc["乙"]
        assert row2["members"] == 2
        assert 0 < row2["fin_coverage"] < 1
        assert row2["cust_top5_med"] == 0.0  # 壁垒缺失补 0（fillna 口径）

    def test_coverage_gate_excludes(self):
        member, fin, choke = self._inputs()
        stats = aggregate_sector_stats(member, fin, choke, min_members=2, min_coverage=0.99)
        assert stats["sector"].tolist() == ["甲"]


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
