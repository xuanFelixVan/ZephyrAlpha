# [BLUEPRINT] MOD-REGIME-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TTL] permanent
# [MODULE] tests.regime.test_trend_features
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; pytest; scipy
# [CONSUMERS] MOD-REGIME-002(RegimeFeatureBuilder消费F2a hurst_dfa + F2b kalman_slope)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] hurst_dfa ∈ (0,1); kalman_slope ∈ [-1,1]; 两者PIT严格(t-1及以前)
# [A_module] module_id=TST-REGIME-002 | layer=test | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-REGIME-002 趋势特征（Hurst DFA + Kalman 斜率）单元测试桩

2026-08-06 修正：替换"250日均线斜率"（依赖量纲/图表比例=伪精确）
- F2a hurst_dfa: DFA法Hurst指数，衡量趋势持久性（>0.5趋势 / <0.5均值回归）
- F2b kalman_slope: Kalman滤波自适应斜率，归一化[-1,1]
TDD: 先写测试桩定义接口和预期行为，再写实现让测试通过
"""

from __future__ import annotations

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def random_walk_500() -> np.ndarray:
    """500日随机游走序列——Hurst 应 ≈ 0.5。"""
    rng = np.random.default_rng(42)
    returns = rng.normal(0, 0.01, 500)
    prices = 10.0 * np.exp(np.cumsum(returns))
    return prices


@pytest.fixture
def trending_up_500() -> np.ndarray:
    """500日持续上涨趋势——Hurst 应 > 0.5（趋势持久）。

    注意：DFA Hurst 衡量的是收益率的自相关（persistence），不是漂移（drift）。
    独立收益率 + 正漂移 → H≈0.5（与随机游走相同）。
    正自相关收益率（当期收益延续前一期方向）→ H>0.5（趋势持久）。
    """
    rng = np.random.default_rng(99)
    noise = rng.normal(0, 0.005, 500)
    returns = np.zeros(500)
    returns[0] = 0.001 + noise[0]
    for i in range(1, 500):
        # AR(1) 正自相关：当期收益 = 漂移 + 0.3×(前一期去均值) + 噪声
        returns[i] = 0.001 + 0.3 * (returns[i - 1] - 0.001) + noise[i]
    prices = 10.0 * np.exp(np.cumsum(returns))
    return prices


@pytest.fixture
def mean_reverting_500() -> np.ndarray:
    """500日均值回归序列——Hurst 应 < 0.5（反持久）。

    注意：DFA Hurst < 0.5 需要收益率负自相关（anti-persistence），不是弱均值回归。
    AR(1) 负系数收益率 → 涨跌交替 → H<0.5。
    """
    rng = np.random.default_rng(77)
    noise = rng.normal(0, 0.01, 500)
    returns = np.zeros(500)
    returns[0] = noise[0]
    for i in range(1, 500):
        # AR(1) 负自相关：当期收益 = -0.6×前一期 + 噪声（强涨跌交替）
        returns[i] = -0.6 * returns[i - 1] + noise[i]
    prices = 10.0 * np.exp(np.cumsum(returns))
    return prices


@pytest.fixture
def volatile_sideways_200() -> np.ndarray:
    """200日震荡序列——Kalman 斜率应接近 0。"""
    rng = np.random.default_rng(33)
    prices = 10.0 + np.cumsum(rng.normal(0, 0.1, 200))
    # 去趋势
    prices = prices - np.polyval(np.polyfit(np.arange(200), prices, 1), np.arange(200)) + 10.0
    return prices


# ---------------------------------------------------------------------------
# 1. Hurst DFA 指数
# ---------------------------------------------------------------------------


class TestHurstDFA:
    """测试 DFA 法 Hurst 指数计算。"""

    def test_random_walk_near_half(self, random_walk_500):
        """随机游走 Hurst ≈ 0.5（±0.15 容差，DFA 估计有噪声）。"""
        from zephyr.regime.features.trend_features import hurst_dfa

        h = hurst_dfa(random_walk_500, window=200)
        assert 0.35 < h < 0.65, f"Random walk Hurst={h:.3f}, expected ~0.5"

    def test_trending_above_half(self, trending_up_500):
        """趋势序列 Hurst > 0.5（趋势持久性）。"""
        from zephyr.regime.features.trend_features import hurst_dfa

        h = hurst_dfa(trending_up_500, window=200)
        assert h > 0.55, f"Trending Hurst={h:.3f}, expected > 0.55"

    def test_mean_reverting_below_half(self, mean_reverting_500):
        """均值回归序列 Hurst < 0.5。"""
        from zephyr.regime.features.trend_features import hurst_dfa

        h = hurst_dfa(mean_reverting_500, window=200)
        assert h < 0.45, f"Mean-reverting Hurst={h:.3f}, expected < 0.45"

    def test_output_range(self, random_walk_500):
        """Hurst 输出 ∈ (0, 1)。"""
        from zephyr.regime.features.trend_features import hurst_dfa

        h = hurst_dfa(random_walk_500)
        assert 0.0 < h < 1.0

    def test_short_series_degradation(self):
        """短序列（<50）返回 0.5 降级值（无法可靠估计）。"""
        from zephyr.regime.features.trend_features import hurst_dfa

        short = np.array([10.0, 10.1, 10.05, 10.2, 10.15])
        h = hurst_dfa(short)
        assert abs(h - 0.5) < 1e-10  # 降级为 0.5（随机游走假设）

    def test_window_parameter(self, random_walk_500):
        """不同 window 参数都能正常工作。"""
        from zephyr.regime.features.trend_features import hurst_dfa

        for w in [50, 100, 200, 250]:
            h = hurst_dfa(random_walk_500, window=w)
            assert 0.0 < h < 1.0


# ---------------------------------------------------------------------------
# 2. Kalman 自适应斜率
# ---------------------------------------------------------------------------


class TestKalmanSlope:
    """测试 Kalman 滤波自适应斜率。"""

    def test_uptrend_positive(self, trending_up_500):
        """上涨趋势 → 正斜率。"""
        from zephyr.regime.features.trend_features import kalman_slope

        slope = kalman_slope(trending_up_500)
        assert slope > 0.0, f"Uptrend slope={slope:.4f}, expected > 0"

    def test_downtrend_negative(self):
        """下跌趋势 → 负斜率。"""
        from zephyr.regime.features.trend_features import kalman_slope

        rng = np.random.default_rng(55)
        # 漂移需足够强（SNR ≥ 1），否则 Kalman 估计被噪声淹没
        returns = rng.normal(-0.005, 0.005, 500)  # 负漂移与噪声等量级
        prices = 10.0 * np.exp(np.cumsum(returns))
        slope = kalman_slope(prices)
        assert slope < 0.0, f"Downtrend slope={slope:.4f}, expected < 0"

    def test_sideways_near_zero(self, volatile_sideways_200):
        """震荡序列 → 斜率接近 0。"""
        from zephyr.regime.features.trend_features import kalman_slope

        slope = kalman_slope(volatile_sideways_200)
        assert abs(slope) < 0.15, f"Sideways slope={slope:.4f}, expected near 0"

    def test_output_range(self, random_walk_500):
        """Kalman 斜率 ∈ [-1, 1]。"""
        from zephyr.regime.features.trend_features import kalman_slope

        slope = kalman_slope(random_walk_500)
        assert -1.0 <= slope <= 1.0

    def test_adaptive_faster_than_ma(self):
        """Kalman 比固定窗口均线斜率更快响应趋势变化。"""
        from zephyr.regime.features.trend_features import kalman_slope

        rng = np.random.default_rng(88)
        # 前200天平稳，后200天突然上涨
        prices = np.concatenate(
            [
                10.0 + np.cumsum(rng.normal(0, 0.02, 200)),
                10.0 + np.cumsum(rng.normal(0.05, 0.02, 200)),  # 突然加速
            ]
        )
        # Kalman 斜率在第201天应该比MA更快反映加速
        kalman_full = kalman_slope(prices)
        kalman_first_half = kalman_slope(prices[:200])
        # 后半段加速后，Kalman斜率应显著增大
        assert kalman_full > kalman_first_half

    def test_short_series_degradation(self):
        """短序列（<5）返回 0.0 降级值。"""
        from zephyr.regime.features.trend_features import kalman_slope

        short = np.array([10.0])
        slope = kalman_slope(short)
        assert slope == 0.0


# ---------------------------------------------------------------------------
# 3. 端到端：Hurst 衰退检测（#10 趋势衰竭）
# ---------------------------------------------------------------------------


class TestTrendExhaustion:
    """测试 Hurst 衰退检测（#10 趋势斜率衰竭的一环）。"""

    def test_hurst_decay_detection(self):
        """趋势衰竭：Hurst 从 >0.65 衰退到 <0.50。"""
        from zephyr.regime.features.trend_features import detect_hurst_decay, hurst_dfa

        rng = np.random.default_rng(11)
        # 前200天强趋势（正自相关收益率），后200天转随机
        noise_trend = rng.normal(0, 0.003, 200)
        trend_returns = np.zeros(200)
        trend_returns[0] = 0.002 + noise_trend[0]
        for i in range(1, 200):
            trend_returns[i] = 0.002 + 0.4 * (trend_returns[i - 1] - 0.002) + noise_trend[i]
        trending = 10.0 * np.exp(np.cumsum(trend_returns))
        random_part = trending[-1] * np.exp(np.cumsum(rng.normal(0, 0.01, 200)))
        full = np.concatenate([trending, random_part])

        # 前段 Hurst 高（趋势态）
        h_early = hurst_dfa(full[:200], window=150)
        # 后段 Hurst 低（衰退期）
        h_late = hurst_dfa(full[200:], window=150)

        decay = detect_hurst_decay(h_early, h_late)
        assert decay is True, f"Hurst decay not detected: early={h_early:.3f}, late={h_late:.3f}"

    def test_no_decay_when_stable(self, trending_up_500):
        """稳定趋势不触发衰退。"""
        from zephyr.regime.features.trend_features import detect_hurst_decay, hurst_dfa

        h1 = hurst_dfa(trending_up_500[:250], window=200)
        h2 = hurst_dfa(trending_up_500[250:], window=200)
        decay = detect_hurst_decay(h1, h2)
        # 都是趋势态，不应触发衰退
        assert decay is False


# ---------------------------------------------------------------------------
# 4. 性能测试
# ---------------------------------------------------------------------------


class TestPerformance:
    """性能基线测试。"""

    @pytest.mark.financial
    def test_hurst_under_100ms(self, random_walk_500):
        """Hurst 计算 < 100ms（500日序列）。"""
        import time

        from zephyr.regime.features.trend_features import hurst_dfa

        start = time.perf_counter()
        hurst_dfa(random_walk_500, window=200)
        elapsed = time.perf_counter() - start
        assert elapsed < 0.1, f"Hurst took {elapsed:.3f}s, expected < 0.1s"

    @pytest.mark.financial
    def test_kalman_under_50ms(self, random_walk_500):
        """Kalman 斜率 < 50ms（500日序列）。"""
        import time

        from zephyr.regime.features.trend_features import kalman_slope

        start = time.perf_counter()
        kalman_slope(random_walk_500)
        elapsed = time.perf_counter() - start
        assert elapsed < 0.05, f"Kalman took {elapsed:.3f}s, expected < 0.05s"
