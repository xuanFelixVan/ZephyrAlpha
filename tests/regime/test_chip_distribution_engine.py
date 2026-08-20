# [BLUEPRINT] MOD-REGIME-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TTL] permanent
# [MODULE] tests.regime.test_chip_distribution_engine
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; pytest
# [CONSUMERS] MOD-REGIME-002(RegimeFeatureBuilder消费#12筹码结构/#5空间位置/S2底部筹码)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] total_distribution Σ=1.0; age_layers各层Σ=1.0; 32网格网格0=最低价网格31=最高价
# [A_module] module_id=TST-REGIME-005 | layer=test | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-REGIME-005 筹码分布引擎 单元测试桩

华泰2026前沿算法：VWAP中心三角分布换手递推 + 筹码龄分层 + 32相对网格映射
TDD: 先写测试桩定义接口和预期行为，再写实现让测试通过
"""

from __future__ import annotations

import time
from datetime import datetime

import numpy as np
import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Fixtures: 构造 mock OHLCV 数据（不依赖 ClickHouse）
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_ohlcv_10d() -> pd.DataFrame:
    """10日 mock OHLCV 数据，用于递推测试。"""
    dates = pd.date_range("2026-07-20", periods=10, freq="B")
    rng = np.random.default_rng(42)
    base = 10.0
    return pd.DataFrame(
        {
            "date": dates,
            "open": base + rng.uniform(-0.2, 0.2, 10),
            "high": base + rng.uniform(0.1, 0.5, 10),
            "low": base + rng.uniform(-0.5, -0.1, 10),
            "close": base + rng.uniform(-0.3, 0.3, 10),
            "volume": rng.uniform(1e6, 5e6, 10),
            "amount": rng.uniform(1e7, 5e7, 10),
        }
    )


@pytest.fixture
def sample_ohlcv_250d() -> pd.DataFrame:
    """250日 mock OHLCV 数据，用于完整递推+网格映射测试。"""
    dates = pd.date_range("2025-08-01", periods=250, freq="B")
    rng = np.random.default_rng(123)
    # 模拟一个先跌后涨的走势，底部有堆积
    close = 10.0 + np.cumsum(rng.normal(-0.01, 0.15, 250))
    close[150:] += np.cumsum(rng.normal(0.02, 0.12, 100))  # 后100天反弹
    high = close + rng.uniform(0.05, 0.3, 250)
    low = close - rng.uniform(0.05, 0.3, 250)
    open_ = close + rng.uniform(-0.1, 0.1, 250)
    volume = rng.uniform(1e6, 5e6, 250)
    amount = volume * close
    return pd.DataFrame(
        {"date": dates, "open": open_, "high": high, "low": low, "close": close, "volume": volume, "amount": amount}
    )


# ---------------------------------------------------------------------------
# 1. 三角分布密度函数
# ---------------------------------------------------------------------------


class TestTriangularDistribution:
    """测试 VWAP 中心三角分布密度函数 D_t(p)。"""

    def test_vwap_is_peak(self):
        """VWAP 处密度最大（三角分布峰值在中心）。"""
        from zephyr.regime.features.chip_distribution_engine import (
            triangular_pdf,
        )

        vwap, low, high = 10.0, 9.0, 11.0
        # VWAP 处密度应该最大
        density_at_vwap = triangular_pdf(vwap, vwap, low, high)
        density_off_center = triangular_pdf(9.5, vwap, low, high)
        assert density_at_vwap > density_off_center

    def test_zero_outside_range(self):
        """[low, high] 之外密度为 0，边界内（严格大于 low/小于 high）> 0。"""
        from zephyr.regime.features.chip_distribution_engine import (
            triangular_pdf,
        )

        vwap, low, high = 10.0, 9.0, 11.0
        assert triangular_pdf(8.0, vwap, low, high) == 0.0
        assert triangular_pdf(12.0, vwap, low, high) == 0.0
        # 三角分布在端点处密度为0，严格在区间内才 > 0
        assert triangular_pdf(9.1, vwap, low, high) > 0.0
        assert triangular_pdf(10.9, vwap, low, high) > 0.0

    def test_normalizes_to_one(self):
        """离散化到价格网格后 Σ=1.0。"""
        from zephyr.regime.features.chip_distribution_engine import (
            compute_daily_distribution,
        )

        vwap, low, high = 10.0, 9.0, 11.0
        prices = np.linspace(9.0, 11.0, 32)
        dist = compute_daily_distribution(vwap, low, high, prices)
        assert abs(sum(dist) - 1.0) < 1e-10


# ---------------------------------------------------------------------------
# 2. 换手递推
# ---------------------------------------------------------------------------


class TestTurnoverRecursion:
    """测试换手递推公式 C_t = (1-τ)×C_{t-1} + τ×D_t。"""

    def test_zero_turnover_preserves(self):
        """τ=0 时 C_t = C_{t-1}（完全保留旧筹码）。"""
        from zephyr.regime.features.chip_distribution_engine import (
            turnover_recurse,
        )

        old = np.array([0.1] * 32)
        new = np.array([0.0] * 16 + [0.0625] * 16)
        result = turnover_recurse(old, new, tau=0.0)
        np.testing.assert_array_almost_equal(result, old)

    def test_full_turnover_replaces(self):
        """τ=1 时 C_t = D_t（完全替换为新筹码）。"""
        from zephyr.regime.features.chip_distribution_engine import (
            turnover_recurse,
        )

        old = np.array([0.1] * 32)
        new = np.array([0.0] * 16 + [0.0625] * 16)
        result = turnover_recurse(old, new, tau=1.0)
        np.testing.assert_array_almost_equal(result, new)

    def test_half_turnover_blends(self):
        """τ=0.5 时 C_t = 0.5×C_{t-1} + 0.5×D_t（混合）。"""
        from zephyr.regime.features.chip_distribution_engine import (
            turnover_recurse,
        )

        old = np.array([0.1] * 32)  # 均匀
        new = np.array([0.0] * 16 + [0.0625] * 16)  # 上半
        result = turnover_recurse(old, new, tau=0.5)
        expected = 0.5 * old + 0.5 * new
        np.testing.assert_array_almost_equal(result, expected)

    def test_result_always_normalizes(self):
        """递推后结果始终归一化（Σ=1.0）。"""
        from zephyr.regime.features.chip_distribution_engine import (
            turnover_recurse,
        )

        old = np.random.dirichlet(np.ones(32))
        new = np.random.dirichlet(np.ones(32))
        for tau in [0.1, 0.3, 0.5, 0.7, 0.9]:
            result = turnover_recurse(old, new, tau=tau)
            assert abs(sum(result) - 1.0) < 1e-10


# ---------------------------------------------------------------------------
# 3. 32 相对网格映射
# ---------------------------------------------------------------------------


class TestGridMapping:
    """测试 32 相对网格映射（跨股比较）。"""

    def test_grid_boundaries(self):
        """网格 0 = 最低价，网格 31 = 最高价。"""
        from zephyr.regime.features.chip_distribution_engine import (
            build_grid_prices,
        )

        low, high = 5.0, 15.0
        grid = build_grid_prices(low, high, n_grids=32)
        assert len(grid) == 32
        assert abs(grid[0] - 5.0) < 1e-10
        assert abs(grid[31] - 15.0) < 1e-10

    def test_grid_spacing_uniform(self):
        """网格等间距。"""
        from zephyr.regime.features.chip_distribution_engine import (
            build_grid_prices,
        )

        # linspace(0, 31, 32) → 步长 = 31/31 = 1.0
        grid = build_grid_prices(0.0, 31.0, n_grids=32)
        diffs = np.diff(grid)
        np.testing.assert_array_almost_equal(diffs, np.full(31, 1.0))


# ---------------------------------------------------------------------------
# 4. 筹码分布引擎端到端
# ---------------------------------------------------------------------------


class TestChipDistributionEngine:
    """测试 ChipDistributionEngine 端到端计算。"""

    def test_output_structure(self, sample_ohlcv_250d):
        """输出包含所有必需字段。"""
        from zephyr.regime.features.chip_distribution_engine import (
            ChipDistributionEngine,
        )

        engine = ChipDistributionEngine()
        result = engine.compute(sample_ohlcv_250d, symbol="000300.SH")
        required_keys = [
            "symbol",
            "date",
            "grid_prices",
            "total_distribution",
            "age_layers",
            "metrics",
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_total_distribution_normalizes(self, sample_ohlcv_250d):
        """total_distribution Σ=1.0。"""
        from zephyr.regime.features.chip_distribution_engine import (
            ChipDistributionEngine,
        )

        engine = ChipDistributionEngine()
        result = engine.compute(sample_ohlcv_250d, symbol="000300.SH")
        assert abs(sum(result["total_distribution"]) - 1.0) < 1e-10

    def test_age_layers_each_normalizes(self, sample_ohlcv_250d):
        """age_layers 各层 Σ=1.0。"""
        from zephyr.regime.features.chip_distribution_engine import (
            ChipDistributionEngine,
        )

        engine = ChipDistributionEngine()
        result = engine.compute(sample_ohlcv_250d, symbol="000300.SH")
        for layer_name, layer_dist in result["age_layers"].items():
            assert abs(sum(layer_dist) - 1.0) < 1e-10, f"{layer_name} not normalized"

    def test_grid_length_32(self, sample_ohlcv_250d):
        """所有分布长度=32。"""
        from zephyr.regime.features.chip_distribution_engine import (
            ChipDistributionEngine,
        )

        engine = ChipDistributionEngine()
        result = engine.compute(sample_ohlcv_250d, symbol="000300.SH")
        assert len(result["total_distribution"]) == 32
        assert len(result["grid_prices"]) == 32
        for layer_dist in result["age_layers"].values():
            assert len(layer_dist) == 32

    def test_metrics_present(self, sample_ohlcv_250d):
        """衍生指标全部存在且在合理范围。"""
        from zephyr.regime.features.chip_distribution_engine import (
            ChipDistributionEngine,
        )

        engine = ChipDistributionEngine()
        result = engine.compute(sample_ohlcv_250d, symbol="000300.SH")
        m = result["metrics"]
        assert "long_term_bottom_ratio" in m
        assert "upper_trap_peak" in m
        assert "bottom_accumulation" in m
        assert "distribution_migration" in m
        # long_term_bottom_ratio ∈ [0, 1]
        assert 0.0 <= m["long_term_bottom_ratio"] <= 1.0
        assert 0.0 <= m["bottom_accumulation"] <= 1.0


# ---------------------------------------------------------------------------
# 5. 衍生指标语义正确性
# ---------------------------------------------------------------------------


class TestDerivedMetrics:
    """测试衍生指标的语义正确性。"""

    def test_bottom_accumulation_high_when_bottom_heavy(self):
        """底部堆积时 bottom_accumulation 高。"""
        from zephyr.regime.features.chip_distribution_engine import (
            compute_metrics,
        )

        # 底部8格占80%
        dist = np.array([0.1] * 8 + [0.005] * 24)
        metrics = compute_metrics(dist, age_layers=None)
        assert metrics["bottom_accumulation"] > 0.7

    def test_migration_negative_when_bottom_heavy(self):
        """底部堆积时 migration 为负（筹码下移）。"""
        from zephyr.regime.features.chip_distribution_engine import (
            compute_metrics,
        )

        long_layer = np.array([0.1] * 8 + [0.005] * 24)
        age_layers = {"long": long_layer, "ultra_short": long_layer, "short": long_layer, "medium": long_layer}
        metrics = compute_metrics(long_layer, age_layers=age_layers)
        assert metrics["distribution_migration"] < 0

    def test_migration_positive_when_top_heavy(self):
        """高位堆积时 migration 为正（筹码上移=派发）。"""
        from zephyr.regime.features.chip_distribution_engine import (
            compute_metrics,
        )

        long_layer = np.array([0.005] * 24 + [0.1] * 8)
        age_layers = {"long": long_layer, "ultra_short": long_layer, "short": long_layer, "medium": long_layer}
        metrics = compute_metrics(long_layer, age_layers=age_layers)
        assert metrics["distribution_migration"] > 0


# ---------------------------------------------------------------------------
# 6. 降级处理
# ---------------------------------------------------------------------------


class TestDegradation:
    """测试降级处理。"""

    def test_empty_ohlcv_returns_uniform(self):
        """空 OHLCV 返回均匀分布。"""
        from zephyr.regime.features.chip_distribution_engine import (
            ChipDistributionEngine,
        )

        engine = ChipDistributionEngine()
        empty_df = pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume", "amount"])
        result = engine.compute(empty_df, symbol="000300.SH")
        assert abs(sum(result["total_distribution"]) - 1.0) < 1e-10
        # 均匀分布：每格 1/32
        expected = 1.0 / 32
        for v in result["total_distribution"]:
            assert abs(v - expected) < 1e-10

    def test_zero_volume_uses_typical_price(self):
        """成交量为 0 时用典型价格 (O+H+L+C)/4 代替 VWAP。"""
        from zephyr.regime.features.chip_distribution_engine import (
            compute_vwap,
        )

        row = {"open": 10.0, "high": 11.0, "low": 9.0, "close": 10.5, "volume": 0.0, "amount": 0.0}
        vwap = compute_vwap(row)
        expected = (10.0 + 11.0 + 9.0 + 10.5) / 4
        assert abs(vwap - expected) < 1e-10


# ---------------------------------------------------------------------------
# 7. 性能测试
# ---------------------------------------------------------------------------


class TestPerformance:
    """性能测试——不做过早优化，但设定合理基线。"""

    @pytest.mark.financial
    def test_single_compute_under_50ms(self, sample_ohlcv_250d):
        """单次计算 < 50ms（250日递推+32网格）。"""
        from zephyr.regime.features.chip_distribution_engine import (
            ChipDistributionEngine,
        )

        engine = ChipDistributionEngine()
        start = time.perf_counter()
        engine.compute(sample_ohlcv_250d, symbol="000300.SH")
        elapsed = time.perf_counter() - start
        # 基线 50ms，不是 200ms——先实现再测量，慢了再优化
        assert elapsed < 0.05, f"Chip distribution took {elapsed:.3f}s, expected < 0.05s"
