# [BLUEPRINT] MOD-SIM-023 | docs/03_modules/_domain_simulation/sharpe_calculator_fixer/blueprint.md
# [MODULE] tests.simulation.test_sharpe_calculator_fixer
# [DOMAIN] D_SIMULATION
# [DEPENDENCIES] zephyr.simulation.sharpe_calculator_fixer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SIM-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-SIM-023 Sharpe Calculator Fixer 单元测试.

覆盖: 样本不足门禁、正态→Sharpe、非正态→Sortino、Jarque-Bera检测、
DSR集成、年化、滚动Sharpe、中国国债默认利率、配置/结果不可变、
边界值(空序列/零方差)、自定义无风险利率、num_trials透传.
"""

from __future__ import annotations

import math
import random

import pytest

from zephyr.simulation.sharpe_calculator_fixer import (
    SharpeCalculatorFixer,
    SharpeConfig,
    SharpeMethod,
    SharpeResult,
    SimulationError,
)

# ============== 辅助函数 ==============


def gen_normal(
    n: int, mean: float = 0.001, std: float = 0.02, seed: int = 42
) -> list[float]:
    """生成正态分布收益率序列。"""
    rng = random.Random(seed)
    return [rng.gauss(mean, std) for _ in range(n)]


def gen_non_normal(n: int = 200, seed: int = 7) -> list[float]:
    """生成显著非正态(重尾+偏斜)收益率序列。

    90% 小幅正收益 + 10% 大幅负跳 → 左偏 + 超额峰度, JB 远超 5.99。
    """
    rng = random.Random(seed)
    out: list[float] = []
    for _ in range(n):
        if rng.random() < 0.9:
            # 平常态: 小幅正收益
            out.append(rng.gauss(0.002, 0.005))
        else:
            # 尾部: 大幅负跳
            out.append(rng.gauss(-0.08, 0.02))
    return out


# ============== 配置 ==============


class TestSharpeConfig:
    def test_defaults(self):
        cfg = SharpeConfig()
        assert cfg.min_samples == 60
        assert cfg.periods_per_year == 252
        # 中国10年期国债 ~2.5% 年化
        assert cfg.risk_free_rate == pytest.approx(0.025 / 252, rel=1e-9)
        assert cfg.jb_critical == 5.99
        assert cfg.dsr_threshold == 0.95

    def test_frozen(self):
        cfg = SharpeConfig()
        with pytest.raises(Exception):
            cfg.min_samples = 100  # type: ignore[misc]

    def test_custom_config(self):
        cfg = SharpeConfig(
            min_samples=30,
            periods_per_year=365,
            risk_free_rate=0.03 / 365,
            jb_critical=4.6,
            dsr_threshold=0.99,
        )
        assert cfg.min_samples == 30
        assert cfg.periods_per_year == 365
        assert cfg.risk_free_rate == pytest.approx(0.03 / 365, rel=1e-9)


class TestSharpeResult:
    def test_frozen(self):
        r = SharpeResult(
            sharpe=1.0,
            sharpe_annualized=1.0 * math.sqrt(252),
            sortino=None,
            sortino_annualized=None,
            dsr=None,
            method=SharpeMethod.SHARPE,
            is_non_normal=False,
            skewness=0.0,
            kurtosis=0.0,
            jb_statistic=0.0,
            num_obs=100,
            risk_free_rate=0.025 / 252,
        )
        with pytest.raises(Exception):
            r.sharpe = 2.0  # type: ignore[misc]


# ============== 样本量门禁 ==============


class TestSampleInsufficient:
    def test_insufficient_returns_none(self):
        fixer = SharpeCalculatorFixer()
        result = fixer.calculate(gen_normal(59, seed=1))
        assert result.sharpe is None
        assert result.sortino is None
        assert result.dsr is None
        assert result.method == SharpeMethod.INSUFFICIENT
        assert result.is_non_normal is False

    def test_boundary_60_calculates(self):
        """恰好 60 个样本应计算(>= min_samples)。"""
        fixer = SharpeCalculatorFixer()
        result = fixer.calculate(gen_normal(60, seed=2))
        assert result.method != SharpeMethod.INSUFFICIENT
        assert result.sharpe is not None

    def test_insufficient_num_obs_recorded(self):
        fixer = SharpeCalculatorFixer()
        result = fixer.calculate(gen_normal(10, seed=3))
        assert result.num_obs == 10
        assert result.risk_free_rate == pytest.approx(0.025 / 252, rel=1e-9)

    def test_custom_min_samples(self):
        cfg = SharpeConfig(min_samples=30)
        fixer = SharpeCalculatorFixer(cfg)
        # 29 < 30 → 不足
        assert fixer.calculate(gen_normal(29, seed=4)).method == SharpeMethod.INSUFFICIENT
        # 30 >= 30 → 计算
        assert fixer.calculate(gen_normal(30, seed=5)).method != SharpeMethod.INSUFFICIENT


# ============== 正态 → Sharpe ==============


class TestNormalSharpe:
    def test_normal_uses_sharpe_method(self):
        fixer = SharpeCalculatorFixer()
        result = fixer.calculate(gen_normal(200, seed=10))
        assert result.method == SharpeMethod.SHARPE
        assert result.is_non_normal is False
        # 正态时不计算 Sortino
        assert result.sortino is None
        assert result.sortino_annualized is None

    def test_sharpe_value(self):
        fixer = SharpeCalculatorFixer()
        returns = gen_normal(200, mean=0.001, std=0.01, seed=11)
        result = fixer.calculate(returns)
        rf = 0.025 / 252
        mean_r = sum(returns) / len(returns)
        std_r = math.sqrt(
            sum((r - mean_r) ** 2 for r in returns) / (len(returns) - 1)
        )
        expected = (mean_r - rf) / std_r
        assert result.sharpe == pytest.approx(expected, rel=1e-9)

    def test_annualization(self):
        fixer = SharpeCalculatorFixer()
        result = fixer.calculate(gen_normal(200, seed=12))
        assert result.sharpe_annualized == pytest.approx(
            result.sharpe * math.sqrt(252), rel=1e-9
        )

    def test_positive_sharpe_for_positive_mean(self):
        fixer = SharpeCalculatorFixer()
        result = fixer.calculate(gen_normal(200, mean=0.002, std=0.01, seed=13))
        assert result.sharpe > 0

    def test_negative_sharpe_for_negative_mean(self):
        fixer = SharpeCalculatorFixer()
        result = fixer.calculate(gen_normal(200, mean=-0.002, std=0.01, seed=14))
        assert result.sharpe < 0


# ============== 非正态 → Sortino ==============


class TestNonNormalSortino:
    def test_non_normal_uses_sortino(self):
        fixer = SharpeCalculatorFixer()
        result = fixer.calculate(gen_non_normal(300, seed=20))
        assert result.is_non_normal is True
        assert result.method == SharpeMethod.SORTINO
        assert result.sortino is not None
        assert result.sortino_annualized is not None

    def test_jb_statistic_above_critical(self):
        fixer = SharpeCalculatorFixer()
        result = fixer.calculate(gen_non_normal(300, seed=21))
        assert result.jb_statistic > 5.99

    def test_sortino_value(self):
        fixer = SharpeCalculatorFixer()
        returns = gen_non_normal(300, seed=22)
        result = fixer.calculate(returns)
        rf = 0.025 / 252
        mean_r = sum(returns) / len(returns)
        # 下行标准差
        sq = sum(min(0.0, r - rf) ** 2 for r in returns) / len(returns)
        d_std = math.sqrt(sq)
        expected = (mean_r - rf) / d_std if d_std != 0 else 0.0
        assert result.sortino == pytest.approx(expected, rel=1e-9)

    def test_sortino_annualization(self):
        fixer = SharpeCalculatorFixer()
        result = fixer.calculate(gen_non_normal(300, seed=23))
        assert result.sortino_annualized == pytest.approx(
            result.sortino * math.sqrt(252), rel=1e-9
        )

    def test_skewness_kurtosis_populated(self):
        fixer = SharpeCalculatorFixer()
        result = fixer.calculate(gen_non_normal(300, seed=24))
        # 非正态序列偏度应显著非零
        assert result.skewness != pytest.approx(0.0, abs=0.01)
        assert result.kurtosis != pytest.approx(0.0, abs=0.01)


# ============== DSR 集成 ==============


class TestDSRIntegration:
    def test_dsr_populated_for_normal(self):
        fixer = SharpeCalculatorFixer()
        result = fixer.calculate(gen_normal(200, seed=30), num_trials=1)
        assert result.dsr is not None
        assert 0.0 < result.dsr < 1.0

    def test_dsr_decreases_with_more_trials(self):
        """试次数越多, DSR 越低(多重测试惩罚)。"""
        fixer = SharpeCalculatorFixer()
        returns = gen_normal(200, mean=0.001, std=0.01, seed=31)
        dsr_n1 = fixer.calculate(returns, num_trials=1).dsr
        dsr_n100 = fixer.calculate(returns, num_trials=100).dsr
        assert dsr_n1 is not None and dsr_n100 is not None
        assert dsr_n100 < dsr_n1

    def test_dsr_none_for_insufficient(self):
        fixer = SharpeCalculatorFixer()
        result = fixer.calculate(gen_normal(10, seed=32), num_trials=50)
        assert result.dsr is None


# ============== 滚动 Sharpe ==============


class TestRollingSharpe:
    def test_rolling_length(self):
        fixer = SharpeCalculatorFixer()
        returns = gen_normal(120, seed=40)
        rolling = fixer.rolling_sharpe(returns, window=60)
        assert len(rolling) == 120 - 60 + 1

    def test_rolling_each_is_result(self):
        fixer = SharpeCalculatorFixer()
        rolling = fixer.rolling_sharpe(gen_normal(120, seed=41), window=60)
        assert all(isinstance(r, SharpeResult) for r in rolling)
        # 样本足够时不应是 INSUFFICIENT
        assert all(r.method != SharpeMethod.INSUFFICIENT for r in rolling)

    def test_rolling_window_below_min_adjusted(self):
        """窗口 < min_samples 自动调整到 min_samples。"""
        fixer = SharpeCalculatorFixer()  # min_samples=60
        returns = gen_normal(120, seed=42)
        # 传 window=30 → 实际用 60
        rolling = fixer.rolling_sharpe(returns, window=30)
        assert len(rolling) == 120 - 60 + 1
        assert all(r.num_obs == 60 for r in rolling)

    def test_rolling_too_short_raises(self):
        fixer = SharpeCalculatorFixer()
        with pytest.raises(SimulationError):
            fixer.rolling_sharpe(gen_normal(50, seed=43), window=60)

    def test_rolling_num_trials_passthrough(self):
        fixer = SharpeCalculatorFixer()
        returns = gen_normal(120, seed=44)
        r_n1 = fixer.rolling_sharpe(returns, window=60, num_trials=1)
        r_n100 = fixer.rolling_sharpe(returns, window=60, num_trials=100)
        # 多试次 → DSR 更低
        assert r_n100[-1].dsr < r_n1[-1].dsr


# ============== 中国国债利率默认值 ==============


class TestChinaBondRate:
    def test_default_risk_free_rate(self):
        fixer = SharpeCalculatorFixer()
        result = fixer.calculate(gen_normal(100, seed=50))
        # 中国10年期国债 ~2.5% 年化, 每期 = 0.025/252
        assert result.risk_free_rate == pytest.approx(0.025 / 252, rel=1e-9)

    def test_custom_risk_free_rate(self):
        fixer = SharpeCalculatorFixer()
        custom_rf = 0.03 / 252
        result = fixer.calculate(gen_normal(100, seed=51), risk_free_rate=custom_rf)
        assert result.risk_free_rate == pytest.approx(custom_rf, rel=1e-9)

    def test_risk_free_rate_affects_sharpe(self):
        fixer = SharpeCalculatorFixer()
        returns = gen_normal(200, mean=0.001, std=0.01, seed=52)
        r_low = fixer.calculate(returns, risk_free_rate=0.0)
        r_high = fixer.calculate(returns, risk_free_rate=0.01)
        # rf 越高 → Sharpe 越低
        assert r_low.sharpe > r_high.sharpe


# ============== 边界值 ==============


class TestEdgeCases:
    def test_empty_raises(self):
        fixer = SharpeCalculatorFixer()
        with pytest.raises(SimulationError):
            fixer.calculate([])

    def test_zero_variance_sharpe_zero(self):
        """所有收益率相同 → 方差为 0 → Sharpe=0。"""
        fixer = SharpeCalculatorFixer()
        result = fixer.calculate([0.001] * 100)
        assert result.sharpe == 0.0

    def test_error_code(self):
        assert SimulationError.error_code == "ZA-SIM-0023"

    def test_result_num_obs(self):
        fixer = SharpeCalculatorFixer()
        result = fixer.calculate(gen_normal(150, seed=60))
        assert result.num_obs == 150


# ============== 方法枚举 ==============


class TestSharpeMethod:
    def test_method_values(self):
        assert SharpeMethod.SHARPE.value == "sharpe"
        assert SharpeMethod.SORTINO.value == "sortino"
        assert SharpeMethod.INSUFFICIENT.value == "insufficient"

    def test_method_is_str_enum(self):
        assert isinstance(SharpeMethod.SHARPE, str)


# ============== 配置只读 ==============


class TestConfigReadonly:
    def test_config_property(self):
        cfg = SharpeConfig(min_samples=50)
        fixer = SharpeCalculatorFixer(cfg)
        assert fixer.config.min_samples == 50
        assert fixer.config is cfg
