# [A_test] module_id: MOD-GOV_test_correlation_neff | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.factor.test_correlation_neff
# [TESTS] src/zephyr/factor/analysis/correlation_neff.py
# [TTL] task_bound
"""23 号 memo §3.1⑤ 组合层 Neff 引擎测试（Ledoit-Wolf 收缩前置）。

裁定真源：23_strategy_correlation_validation.md §3.1⑤——
  Neff=(Σλ)²/Σλ²；LW 闭式收缩保证正定稳定特征值；α∈[0,1] 双重用途；
  等相关近似仅辅助。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.analysis.correlation_neff import (
    effective_bets,
    equicorrelation_neff,
    ledoit_wolf_shrinkage,
)


class TestLedoitWolfShrinkage:
    def test_shrunk_matrix_symmetric_psd(self):
        """对称半正定校验：收缩矩阵必须对称且特征值 ≥ −ε。"""
        rng = np.random.default_rng(41)
        factor = rng.normal(0, 1, 300)
        x = np.column_stack(
            [0.8 * factor + 0.6 * rng.normal(0, 1, 300) for _ in range(4)]
        )
        res = ledoit_wolf_shrinkage(pd.DataFrame(x))
        assert np.allclose(res.shrunk_corr, res.shrunk_corr.T, atol=1e-12)  # 对称
        assert np.linalg.eigvalsh(res.shrunk_corr).min() >= -1e-12  # 半正定
        assert 0.0 <= res.alpha <= 1.0
        assert np.allclose(np.diag(res.shrunk_corr), 1.0)  # 相关矩阵对角恒 1

    def test_alpha_signal_for_correlated_structure(self):
        """α 双重用途：高相关面板 α 应非负且有界；恒等相关时收缩后矩阵仍合法。"""
        rng = np.random.default_rng(43)
        factor = rng.normal(0, 1, 200)
        x = np.column_stack([factor + 0.01 * rng.normal(0, 1, 200) for _ in range(3)])
        res = ledoit_wolf_shrinkage(x)
        assert 0.0 <= res.alpha <= 1.0

    def test_identity_sample_shrinks_to_identity(self):
        """构造正交列（样本相关≈I）→ d²≈0，LW 语义下 α→1 全收缩即恒等，矩阵不变。"""
        t = 256
        z1 = np.sin(np.arange(t) * 2 * np.pi / t)
        z2 = np.cos(np.arange(t) * 2 * np.pi / t)
        x = np.column_stack([z1, z2]) + 1e-9 * np.random.default_rng(1).normal(0, 1, (t, 2))
        res = ledoit_wolf_shrinkage(x)
        assert np.allclose(res.shrunk_corr, np.eye(2), atol=1e-6)

    def test_weak_correlation_long_sample_small_alpha(self):
        """弱相关（ρ=0.1）大样本 → d² 显著>0 且噪声小 → 轻收缩 α<0.5。"""
        rng = np.random.default_rng(45)
        t = 4000
        factor = rng.normal(0, 1, t)
        x = np.column_stack(
            [np.sqrt(0.1) * factor + np.sqrt(0.9) * rng.normal(0, 1, t) for _ in range(4)]
        )
        res = ledoit_wolf_shrinkage(x)
        assert 0.0 <= res.alpha < 0.5

    def test_constant_column_and_nan_rejected(self):
        with pytest.raises(ValueError):
            ledoit_wolf_shrinkage(np.column_stack([np.ones(50), np.arange(50.0)]))
        with pytest.raises(ValueError):
            ledoit_wolf_shrinkage(np.array([[0.1, np.nan], [0.2, 0.3]]))


class TestEffectiveBets:
    def test_uncorrelated_neff_near_n(self):
        rng = np.random.default_rng(47)
        x = rng.normal(0, 1, (2000, 4))
        res = effective_bets(x)
        assert res.neff == pytest.approx(4.0, abs=0.6)  # 独立策略 Neff≈N
        assert res.n_assets == 4
        assert len(res.eigenvalues) == 4

    def test_perfectly_correlated_neff_near_one(self):
        """同一序列复制 3 份 → 实际只有 1 个独立下注。"""
        rng = np.random.default_rng(53)
        base = rng.normal(0, 1, 300)
        x = np.column_stack([base, base, base])
        res = effective_bets(x)
        assert res.neff < 1.5  # 收缩偏乐观仍应 <<3
        assert res.eigenvalues[0] >= -1e-12  # 数值负零已裁剪

    def test_single_strategy_neff_one(self):
        res = effective_bets(np.random.default_rng(1).normal(0, 1, (100, 1)))
        assert res.neff == 1.0
        assert res.alpha == 0.0

    def test_no_shrink_path(self):
        rng = np.random.default_rng(59)
        res = effective_bets(rng.normal(0, 1, (500, 3)), shrink=False)
        assert res.alpha == 0.0
        assert 1.0 <= res.neff <= 3.0

    def test_equicorrelation_auxiliary(self):
        """等相关近似：恒等相关 ρ̄=0.5、N=4 → 4/(1+3×0.5)=1.6。"""
        corr = np.full((4, 4), 0.5)
        np.fill_diagonal(corr, 1.0)
        assert equicorrelation_neff(corr) == pytest.approx(1.6)
        assert equicorrelation_neff(np.eye(3)) == pytest.approx(3.0)
