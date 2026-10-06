# [BLUEPRINT] MOD-E2E-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""盘中横截面因子单元测试——验证 IntradayClose / IntradayVwap 计算。

测试范围：
    - IntradayClose.compute：返回 close 列（恒等）
    - IntradayVwap.compute：volume>0 → amount/volume；volume=0 → 回退 close
    - 注册表覆盖：两因子在 FactorRegistry 中可查
    - 元数据完整性：factor_id / domain / tags 符合预期
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

# 导入模块触发 @FactorRegistry.register 注册副作用
import zephyr.factor.intraday_snapshot_factors  # noqa: F401
from zephyr.factor.factor_base import FactorRegistry
from zephyr.factor.intraday_snapshot_factors import IntradayClose, IntradayVwap


def _make_df(rows: dict[str, dict[str, float]]) -> pd.DataFrame:
    """构造 tick 快照 DataFrame（index=symbol, columns=close/volume/amount）。"""
    df = pd.DataFrame.from_dict(rows, orient="index")
    df.index.name = "symbol"
    return df


class TestIntradayClose:
    """盘中最新价因子。"""

    def test_returns_close_column(self):
        """compute 直接返回 close 列（恒等映射）。"""
        df = _make_df(
            {
                "000001.SZ": {"close": 12.50, "volume": 1000, "amount": 12500.0},
                "600000.SH": {"close": 8.32, "volume": 500, "amount": 4160.0},
            }
        )
        result = IntradayClose().compute(df)
        assert result["000001.SZ"] == pytest.approx(12.50)
        assert result["600000.SH"] == pytest.approx(8.32)

    def test_single_row(self):
        """单行 DataFrame 也能计算。"""
        df = _make_df({"000001.SZ": {"close": 10.0, "volume": 1, "amount": 10.0}})
        result = IntradayClose().compute(df)
        assert len(result) == 1
        assert result["000001.SZ"] == pytest.approx(10.0)


class TestIntradayVwap:
    """盘中累计均价因子。"""

    def test_vwap_normal(self):
        """volume>0 → amount/volume。"""
        df = _make_df(
            {
                "000001.SZ": {"close": 12.50, "volume": 1000, "amount": 12500.0},
                # amount=8320 / volume=1000 = 8.32（与 close 不同，验证实际计算）
                "600000.SH": {"close": 9.00, "volume": 1000, "amount": 8320.0},
            }
        )
        result = IntradayVwap().compute(df)
        assert result["000001.SZ"] == pytest.approx(12.50)
        assert result["600000.SH"] == pytest.approx(8.32)

    def test_vwap_zero_volume_falls_back_to_close(self):
        """volume=0 → 回退 close，避免除零。"""
        df = _make_df(
            {
                "000001.SZ": {"close": 12.50, "volume": 0, "amount": 0.0},
            }
        )
        result = IntradayVwap().compute(df)
        assert result["000001.SZ"] == pytest.approx(12.50)

    def test_vwap_mixed(self):
        """混合：一只 volume>0，一只 volume=0。"""
        df = _make_df(
            {
                "000001.SZ": {"close": 12.50, "volume": 1000, "amount": 12500.0},  # vwap=12.50
                "600000.SH": {"close": 8.32, "volume": 0, "amount": 0.0},  # 回退 8.32
            }
        )
        result = IntradayVwap().compute(df)
        assert result["000001.SZ"] == pytest.approx(12.50)
        assert result["600000.SH"] == pytest.approx(8.32)

    def test_vwap_does_not_mutate_input(self):
        """compute 不修改输入 DataFrame 的 close 列。"""
        df = _make_df(
            {
                "000001.SZ": {"close": 12.50, "volume": 1000, "amount": 9999.0},
            }
        )
        original_close = df["close"].copy()
        IntradayVwap().compute(df)
        pd.testing.assert_series_equal(df["close"], original_close)

    def test_vwap_handles_nan_amount(self):
        """amount=NaN 时 vwap=NaN（不抛异常），由下游 NaN 过滤处理。"""
        df = _make_df(
            {
                "000001.SZ": {"close": 12.50, "volume": 1000, "amount": float("nan")},
            }
        )
        result = IntradayVwap().compute(df)
        assert np.isnan(result["000001.SZ"])


class TestRegistryCoverage:
    """因子注册表覆盖——确保两因子已注册可被 IntradayFactorLoop 发现。"""

    @pytest.fixture(autouse=True)
    def _ensure_registered(self):
        """xdist 同 worker 内其他测试文件会 FactorRegistry.clear()（全局单例污染），
        本类断言注册表内容前须幂等恢复注册（直接 register 既有类对象，保身份断言）。"""
        if "intraday_close" not in FactorRegistry.registry:
            FactorRegistry.register(IntradayClose)
        if "intraday_vwap" not in FactorRegistry.registry:
            FactorRegistry.register(IntradayVwap)

    def test_intraday_close_registered(self):
        assert "intraday_close" in FactorRegistry.registry

    def test_intraday_vwap_registered(self):
        assert "intraday_vwap" in FactorRegistry.registry

    def test_both_factors_gettable(self):
        cls_close = FactorRegistry.get("intraday_close")
        cls_vwap = FactorRegistry.get("intraday_vwap")
        assert cls_close is IntradayClose
        assert cls_vwap is IntradayVwap

    def test_meta_domain_technical(self):
        assert IntradayClose.meta.domain == "technical"
        assert IntradayVwap.meta.domain == "technical"

    def test_meta_has_tags(self):
        assert "intraday" in IntradayClose.meta.tags
        assert "cross-sectional" in IntradayClose.meta.tags
        assert "intraday" in IntradayVwap.meta.tags
        assert "cross-sectional" in IntradayVwap.meta.tags

    def test_factor_ids_distinct(self):
        """两因子 factor_id 必须不同（防重复注册）。"""
        assert IntradayClose.meta.factor_id != IntradayVwap.meta.factor_id
