# [BLUEPRINT] MOD-REGIME-005 | docs/03_modules/_domain_regime/chip_distribution_engine/blueprint.md
# [MODULE] tests.regime.test_chip_winner_profile
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; pytest
# [CONSUMERS] MOD-REGIME-005 winner 剖面（获利盘，IND-CHIPS-001 供给面）回归证尺
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] winner 剖面全场景不抛错（fail-open）；解析构造例 winner 手算值精确命中
# [A_module] module_id=TST-REGIME-008 | layer=test | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""MOD-REGIME-005 winner（获利盘）剖面 单元测试（SW14 处方①，D21 第一步）。

证尺面：
1. 解析构造例：两日一字板 + 半衰换手，winner 手算值 1/3 精确命中（直调
   chips.py::compute_chip_metrics 单一真源，禁第二套分布实现）。
2. float_share 派生腿：缺 turnover_rate 列时由流通股本（万股，tushare
   stock_daily_basic 口径）派生换手率，与显式换手率入参逐位一致。
3. fail-open 语义：空/缺列/缺换手源/全零成交量 全部降级不抛错，
   degrade_reason 可读，与引擎邻居剖面的降级契约（ZA-REGIME-0050 族）对齐。
4. 引擎集成：compute() 输出含 winner 键且与独立调用同构；均匀降级路径
   winner 键恒在（消费者零 KeyError 面）。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.features.chip_distribution_engine import (
    ChipDistributionEngine,
    compute_winner_profile,
)


def _two_bar_df(close_day2: float, volumes: tuple[float, float] = (100.0, 100.0)) -> pd.DataFrame:
    """两日一字板 fixture：day1 价格 10，day2 价格 12、收盘由调用方定。"""
    return pd.DataFrame(
        {
            "date": pd.date_range("2026-09-28", periods=2, freq="B"),
            "open": [10.0, 12.0],
            "high": [10.0, 12.0],
            "low": [10.0, 12.0],
            "close": [10.0, close_day2],
            "volume": list(volumes),
            "amount": [1000.0, 1200.0],
        }
    )


class TestWinnerProfileAnalytic:
    """解析构造例：获利比例手算值精确命中。"""

    def test_winner_one_third_analytic(self):
        """day1 全部质量@10；day2 换手 50% 衰减后旧质量 50@10 + 新增 100@12；
        close=11 → winner = 50/150 = 1/3（精确）。"""
        df = _two_bar_df(close_day2=11.0)
        out = compute_winner_profile(df, turnover_rate=pd.Series([0.0, 50.0]))
        assert out["available"] is True
        assert out["chips_winner"] == pytest.approx(1.0 / 3.0, abs=1e-9)
        # day1：全部成本 10 ≤ close 10 → 获利盘 1.0
        assert out["winner_series"][0] == pytest.approx(1.0, abs=1e-9)

    def test_winner_zero_when_close_below_all_cost(self):
        """close=8 低于全部筹码成本（10/12）→ 获利盘 0。"""
        df = _two_bar_df(close_day2=8.0, volumes=(100.0, 0.0))
        out = compute_winner_profile(df, turnover_rate=pd.Series([0.0, 0.0]))
        assert out["available"] is True
        assert out["chips_winner"] == pytest.approx(0.0, abs=1e-12)

    def test_avg_cost_analytic(self):
        """同 day1/day2 半衰例末日：avg_cost=(50×10+100×12)/150=1700/150≈11.333。"""
        df = _two_bar_df(close_day2=12.0)
        out = compute_winner_profile(df, turnover_rate=pd.Series([0.0, 50.0]))
        assert out["chips_avg_cost"] == pytest.approx(1700.0 / 150.0, rel=1e-9)

    def test_deterministic_rerun(self):
        """同输入两次调用输出逐位一致（幂等）。"""
        df = _two_bar_df(close_day2=11.0)
        a = compute_winner_profile(df, turnover_rate=pd.Series([0.0, 50.0]))
        b = compute_winner_profile(df, turnover_rate=pd.Series([0.0, 50.0]))
        assert a["chips_winner"] == b["chips_winner"]
        assert a["winner_series"] == b["winner_series"]


class TestWinnerProfileTurnoverSources:
    """换手率三源解析：显式入参 > df 列 > float_share 派生。"""

    def test_turnover_from_column(self):
        df = _two_bar_df(close_day2=11.0)
        df["turnover_rate"] = [0.0, 50.0]
        explicit = compute_winner_profile(df, turnover_rate=pd.Series([0.0, 50.0]))
        via_column = compute_winner_profile(df)
        assert via_column["available"] is True
        assert via_column["chips_winner"] == explicit["chips_winner"]

    def test_turnover_derived_from_float_share(self):
        """float_share=10000 万股=1e8 股；volume=1e6 股/日 → 换手 1.0%/日；
        派生腿与显式同值换手率入参输出逐位一致。"""
        df = _two_bar_df(close_day2=11.0, volumes=(1e6, 1e6))
        derived = compute_winner_profile(df, float_share=10000.0)
        explicit = compute_winner_profile(df, turnover_rate=pd.Series([1.0, 1.0]))
        assert derived["available"] is True
        assert derived["chips_winner"] == pytest.approx(explicit["chips_winner"], abs=1e-12)
        assert derived["winner_series"] == pytest.approx(explicit["winner_series"], abs=1e-12)

    def test_explicit_series_overrides_column(self):
        df = _two_bar_df(close_day2=11.0)
        df["turnover_rate"] = [0.0, 50.0]
        via_arg = compute_winner_profile(df, turnover_rate=pd.Series([0.0, 100.0]))
        assert via_arg["available"] is True
        # 换手 100%：旧质量全衰尽，末日质量全部 @12 → close=11 → winner=0
        assert via_arg["chips_winner"] == pytest.approx(0.0, abs=1e-12)


class TestWinnerProfileFailOpen:
    """fail-open 语义：一切缺数据场景降级不抛错（对齐 ZA-REGIME-0050 族契约）。"""

    def test_none_df(self):
        out = compute_winner_profile(None)
        assert out["available"] is False
        assert out["chips_winner"] is None
        assert out["degrade_reason"]

    def test_empty_df(self):
        out = compute_winner_profile(pd.DataFrame())
        assert out["available"] is False
        assert out["chips_winner"] is None

    def test_missing_hard_column(self):
        df = _two_bar_df(close_day2=11.0).drop(columns=["close"])
        out = compute_winner_profile(df, turnover_rate=pd.Series([0.0, 50.0]))
        assert out["available"] is False
        assert "close" in out["degrade_reason"]

    def test_no_turnover_source(self):
        df = _two_bar_df(close_day2=11.0)
        out = compute_winner_profile(df)
        assert out["available"] is False
        assert "turnover" in out["degrade_reason"].lower() or "换手" in out["degrade_reason"]

    def test_all_nan_turnover_column_degrades(self):
        """换手率列存在但全 NaN（对齐 CYQ 类软降级：非 daily 周期=设计内降级）。"""
        df = _two_bar_df(close_day2=11.0)
        df["turnover_rate"] = [np.nan, np.nan]
        out = compute_winner_profile(df)
        assert out["available"] is False

    def test_bad_float_share_degrades(self):
        df = _two_bar_df(close_day2=11.0)
        for bad in (0.0, -5.0, float("nan")):
            out = compute_winner_profile(df, float_share=bad)
            assert out["available"] is False

    def test_all_zero_volume_degrades(self):
        """全历史零成交量 → CYQ 无筹码可用 → 末日 winner NaN → 降级。"""
        df = _two_bar_df(close_day2=11.0, volumes=(0.0, 0.0))
        out = compute_winner_profile(df, turnover_rate=pd.Series([0.0, 50.0]))
        assert out["available"] is False


class TestEngineWinnerIntegration:
    """引擎集成：winner 键恒在、与独立剖面同构、均匀降级路径 fail-open。"""

    def test_compute_attaches_winner_profile(self):
        df = _two_bar_df(close_day2=11.0)
        df["turnover_rate"] = [0.0, 50.0]
        result = ChipDistributionEngine().compute(df, symbol="000852")
        assert "winner" in result
        standalone = compute_winner_profile(df)
        assert result["winner"]["chips_winner"] == standalone["chips_winner"]
        assert result["winner"]["available"] is True

    def test_compute_float_share_passthrough(self):
        df = _two_bar_df(close_day2=11.0, volumes=(1e6, 1e6))
        result = ChipDistributionEngine().compute(df, symbol="000852", float_share=10000.0)
        assert result["winner"]["available"] is True
        assert result["winner"]["chips_winner"] == pytest.approx(
            compute_winner_profile(df, float_share=10000.0)["chips_winner"], abs=1e-12
        )

    def test_empty_df_uniform_result_has_winner_key(self):
        result = ChipDistributionEngine().compute(pd.DataFrame(), symbol="000852")
        assert result["total_distribution"]  # 既有均匀剖面不回归
        assert result["winner"]["available"] is False
        assert result["winner"]["chips_winner"] is None

    def test_existing_profile_keys_unchanged(self):
        """同构断言：既有键一个不少（消费者兼容面）。"""
        df = _two_bar_df(close_day2=11.0)
        df["turnover_rate"] = [0.0, 50.0]
        result = ChipDistributionEngine().compute(df, symbol="000852")
        for key in (
            "symbol",
            "date",
            "grid_prices",
            "total_distribution",
            "age_layers",
            "metrics",
            "schema_version",
            "window_days",
        ):
            assert key in result
