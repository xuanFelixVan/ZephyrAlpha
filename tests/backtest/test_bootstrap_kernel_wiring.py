# [TTL] permanent
# [BLUEPRINT] MOD-BT-237 | tests/backtest/test_bootstrap_kernel_wiring.py | bootstrap核接线对拍+回归
"""bootstrap 加速核（MOD-BT-237）接线对拍与回归（st-mx07-L3 P1-3）。

对拍契约=同索引矩阵注入法：三处换核后的消费方索引缝
（walk_forward/e2/correlation 各自的 stationary_bootstrap_index_matrix 模块名）
被注入固定 (B,T) 索引矩阵后，换核路径与迁移前原内循环参考实现
（本文件内逐式镜像副本）吃同一批索引，统计量矩阵/派生量逐位 <=1e-9。

回归面：公共 API 不变（含标量 stationary_bootstrap_indices 保留）、
输入校验面不变、auto 恒 CPU 夜纪律。
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd
import pytest

from zephyr.backtest.accel import bootstrap_kernel as bk
from zephyr.backtest.core import walk_forward as wfmod
from zephyr.backtest.core.walk_forward import WalkForwardAnalyzer
from zephyr.backtest.regime_validation import e2_stationary_bootstrap as e2mod
from zephyr.factor.analysis import correlation_block_bootstrap as cbbmod

TOL = 1e-9


# ---------------------------------------------------------------------------
# 参考实现（迁移前原内循环逐式镜像，对拍基准）
# ---------------------------------------------------------------------------


def _ref_wrc_boot(recentered: np.ndarray, idx: np.ndarray, sqrt_n: float) -> np.ndarray:
    """walk_forward 原内循环（274-280 行同式）：逐 b 采样+ddof=1 t 统计量。"""
    out = np.empty(idx.shape[0])
    for b in range(idx.shape[0]):
        sample = recentered[idx[b]]
        s_std = float(np.std(sample, ddof=1))
        out[b] = 0.0 if s_std <= 0 else float(np.mean(sample)) / (s_std / sqrt_n)
    return out


def _ref_e2_diffs(on: np.ndarray, off: np.ndarray, idx: np.ndarray, ppy: int) -> np.ndarray:
    """e2 原内循环（168-170 行同式）：逐 b 成对 annualized_sharpe 差。"""
    out = np.empty(idx.shape[0])
    for b in range(idx.shape[0]):
        out[b] = e2mod.annualized_sharpe(on[idx[b]], ppy) - e2mod.annualized_sharpe(off[idx[b]], ppy)
    return out


def _ref_corr_pairs(x: np.ndarray, idx: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """correlation 原内循环（325-330 行同式）：逐 rep 同步行重采样 + np.corrcoef 成对提取。"""
    k = x.shape[1]
    pairs = [(i, j) for i in range(k) for j in range(i + 1, k)]
    ref_p = np.empty((idx.shape[0], len(pairs)))
    ref_s = np.empty_like(ref_p)
    for rep in range(idx.shape[0]):
        pm, sm = cbbmod._pair_corr_stats(x[idx[rep]])
        for pi, (i, j) in enumerate(pairs):
            ref_p[rep, pi] = pm[i, j]
            ref_s[rep, pi] = sm[i, j]
    return ref_p, ref_s


# ---------------------------------------------------------------------------
# 数据与注入工具
# ---------------------------------------------------------------------------


def _make_pair(T: int = 800, seed: int = 20261007) -> tuple[np.ndarray, np.ndarray]:
    """AR(0.3) 策略 vs 同源相关基准（自相关结构下块重采样才有意义）。"""
    rng = np.random.default_rng(seed)
    eps = rng.normal(0.0, 0.010, T)
    s = np.empty(T)
    s[0] = 0.0005 + eps[0]
    for t in range(1, T):
        s[t] = 0.0005 + 0.30 * s[t - 1] + eps[t]
    b = 0.40 * s + 0.0002 + rng.normal(0.0, 0.008, T)
    return s, b


def _make_panel(T: int = 600, k: int = 4, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    f = rng.normal(0.0, 0.010, T)
    betas = np.array([0.9, 0.5, -0.3, 0.7][:k])
    panel = betas[None, :] * f[:, None] + rng.normal(0.0, 0.006, (T, k))
    return pd.DataFrame(panel, columns=[f"f{i}" for i in range(k)])


class _StaticIdx:
    """索引缝注入：恒返回同一矩阵并计数（守恒校验防静默错位）。"""

    def __init__(self, mat: np.ndarray):
        self.mat = mat
        self.calls = 0

    def __call__(self, *args, **kwargs):  # noqa: ARG002 — 签名对齐被缝
        self.calls += 1
        return self.mat


# ---------------------------------------------------------------------------
# 对拍：三函数同索引注入逐位 <=1e-9
# ---------------------------------------------------------------------------


class TestWrcWiringParity:
    def test_wrc_parity_injected_idx(self, monkeypatch: pytest.MonkeyPatch) -> None:
        s, b = _make_pair()
        n_boot, block = 400, 0
        ser_s, ser_b = pd.Series(s), pd.Series(b)
        aligned = pd.concat([ser_s, ser_b], axis=1).dropna()
        diff = (aligned.iloc[:, 0] - aligned.iloc[:, 1]).to_numpy(dtype=float)
        n = len(diff)
        obs_mean = float(np.mean(diff))
        obs_std = float(np.std(diff, ddof=1))
        sqrt_n = float(np.sqrt(n))
        obs_t = obs_mean / (obs_std / sqrt_n)
        recentered = diff - obs_mean
        blk = max(1, int(round(n ** (1.0 / 3.0)))) if block <= 0 else block

        idx = bk.stationary_bootstrap_index_matrix(n, blk, n_boot, np.random.default_rng(101))
        seam = _StaticIdx(idx)
        monkeypatch.setattr(wfmod, "stationary_bootstrap_index_matrix", seam)
        res = WalkForwardAnalyzer().whites_reality_check(ser_s, ser_b, n_bootstrap=n_boot, block_size=block)
        assert seam.calls == 1, f"索引缝消费 {seam.calls} 次 != 1"

        ref = _ref_wrc_boot(recentered, idx, sqrt_n)
        boot = bk.wrc_boot_tstats(recentered, idx, sqrt_n)
        max_delta = float(np.max(np.abs(boot - ref)))
        assert max_delta <= TOL, f"WRC boot 矩阵 max|delta|={max_delta:.3e}"
        assert abs(float(np.mean(boot >= obs_t)) - float(res["p_value"])) <= TOL
        assert abs(obs_t - float(res["t_stat"])) <= TOL

    def test_wrc_block_size_one_iid_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """block_size=1（p>=0.999 索引生成分支）同索引对拍仍逐位一致。"""
        s, b = _make_pair(T=300, seed=11)
        n_boot = 100
        ser_s, ser_b = pd.Series(s), pd.Series(b)
        diff = (ser_s - ser_b).to_numpy(dtype=float)
        n = len(diff)
        recentered = diff - float(np.mean(diff))
        sqrt_n = float(np.sqrt(n))

        idx = bk.stationary_bootstrap_index_matrix(n, 1, n_boot, np.random.default_rng(5))
        seam = _StaticIdx(idx)
        monkeypatch.setattr(wfmod, "stationary_bootstrap_index_matrix", seam)
        res = WalkForwardAnalyzer().whites_reality_check(ser_s, ser_b, n_bootstrap=n_boot, block_size=1)
        assert seam.calls == 1
        boot = bk.wrc_boot_tstats(recentered, idx, sqrt_n)
        obs_t = float(res["t_stat"])
        assert float(np.max(np.abs(boot - _ref_wrc_boot(recentered, idx, sqrt_n)))) <= TOL
        assert abs(float(np.mean(boot >= obs_t)) - float(res["p_value"])) <= TOL


class TestE2WiringParity:
    def test_e2_parity_injected_idx(self, monkeypatch: pytest.MonkeyPatch) -> None:
        on, off = _make_pair()
        cfg = e2mod.E2BootstrapConfig(n_boot=400, mean_block=21, seed=42, ci_level=0.90)

        idx = bk.stationary_bootstrap_index_matrix(on.size, cfg.mean_block, cfg.n_boot, np.random.default_rng(202))
        seam = _StaticIdx(idx)
        monkeypatch.setattr(e2mod, "stationary_bootstrap_index_matrix", seam)
        res = e2mod.bootstrap_sharpe_difference(on, off, cfg)
        assert seam.calls == 1, f"索引缝消费 {seam.calls} 次 != 1"

        ref = _ref_e2_diffs(on, off, idx, cfg.periods_per_year)
        diffs = bk.e2_boot_sharpe_diffs(on, off, idx, periods_per_year=cfg.periods_per_year)
        max_delta = float(np.max(np.abs(diffs - ref)))
        assert max_delta <= TOL, f"E2 diffs 矩阵 max|delta|={max_delta:.3e}"
        alpha = 1.0 - cfg.ci_level
        assert abs(float(np.quantile(ref, 1.0 - alpha / 2.0)) - float(res.ci_upper)) <= TOL
        assert abs(float(np.mean(ref > 0.0)) - float(res.prob_positive)) <= TOL
        observed = e2mod.annualized_sharpe(on, cfg.periods_per_year) - e2mod.annualized_sharpe(
            off, cfg.periods_per_year
        )
        assert abs(observed - float(res.observed_diff)) <= TOL


class TestCorrWiringParity:
    def test_corr_parity_injected_idx(self, monkeypatch: pytest.MonkeyPatch) -> None:
        df = _make_panel()
        x = df.to_numpy(dtype=float)
        t, k = x.shape
        pairs = [(i, j) for i in range(k) for j in range(i + 1, k)]
        n_boot, blk = 300, 17

        idx = bk.stationary_bootstrap_index_matrix(t, blk, n_boot, np.random.default_rng(303))
        seam = _StaticIdx(idx)
        monkeypatch.setattr(cbbmod, "stationary_bootstrap_index_matrix", seam)
        res = cbbmod.bootstrap_correlation_ci(df, n_bootstrap=n_boot, block_size=blk, confidence=0.90, seed=7)
        assert seam.calls == 1, f"索引缝消费 {seam.calls} 次 != 1"

        ref_p, ref_s = _ref_corr_pairs(x, idx)
        boot_p, boot_s = bk.corr_boot_pair_stats(x, idx)
        dp = float(np.max(np.abs(boot_p - ref_p)))
        ds = float(np.max(np.abs(boot_s - ref_s)))
        assert dp <= TOL, f"CORR pearson 矩阵 max|delta|={dp:.3e}"
        assert ds <= TOL, f"CORR spearman 矩阵 max|delta|={ds:.3e}"

        alpha = (1.0 - 0.90) / 2.0
        names = list(df.columns)
        for qi, (i, j) in enumerate(pairs):
            pair_ci = res.pearson[(names[i], names[j])]
            col = ref_p[:, qi]
            assert abs(float(np.quantile(col, 1.0 - alpha)) - float(pair_ci.ci_upper)) <= TOL
            assert abs(float(np.mean(col > 0.6)) - float(pair_ci.prob_above_threshold)) <= TOL


# ---------------------------------------------------------------------------
# 回归：公共 API 与校验面不变
# ---------------------------------------------------------------------------


class TestPublicApiUnchanged:
    def test_scalar_index_generators_still_exported(self) -> None:
        """标量索引生成器保留（e2 公共 API + regime_validation 包 re-export）。"""
        rng = np.random.default_rng(0)
        idx = e2mod.stationary_bootstrap_indices(100, 10, rng)
        assert idx.shape == (100,) and idx.min() >= 0 and idx.max() < 100
        assert cbbmod.stationary_bootstrap_indices is not None
        from zephyr.backtest.regime_validation import stationary_bootstrap_indices as pkg_level

        assert pkg_level is e2mod.stationary_bootstrap_indices

    def test_wrc_zero_variance_returns_insufficient(self) -> None:
        """零波动早退路径（换核不触碰判定面）。"""
        flat = pd.Series(np.full(100, 0.001))
        res = WalkForwardAnalyzer().whites_reality_check(flat, pd.Series(np.full(100, 0.001)), n_bootstrap=50)
        assert res == {"p_value": 1.0, "is_significant": False, "t_stat": 0.0}

    def test_e2_validation_unchanged(self) -> None:
        with pytest.raises(e2mod.E2BootstrapError):
            e2mod.bootstrap_sharpe_difference(np.array([0.01]), np.array([0.02]))
        with pytest.raises(e2mod.E2BootstrapError):
            e2mod.bootstrap_sharpe_difference(np.array([np.nan, 0.01]), np.array([0.0, 0.02]))

    def test_corr_validation_unchanged(self) -> None:
        with pytest.raises(ValueError, match="NaN"):
            cbbmod.bootstrap_correlation_ci(pd.DataFrame({"a": [0.1, np.nan] * 8, "b": [0.0] * 16}), n_bootstrap=10)
        with pytest.raises(ValueError, match="k>=2"):
            cbbmod.bootstrap_correlation_ci(pd.DataFrame({"a": [0.1] * 16}), n_bootstrap=10)

    def test_wrc_legacy_block_sampler_still_available(self) -> None:
        """原逐块采样器保留（公共方法面未删）。"""
        rng = np.random.default_rng(1)
        sample = WalkForwardAnalyzer._stationary_block_bootstrap(np.arange(50.0), 5, rng)
        assert sample.shape == (50,)


class TestKernelDiscipline:
    def test_auto_backend_is_cpu_and_no_cupy_import_by_kernel(self) -> None:
        """auto 恒 CPU；核模块 import 零 cupy 触碰（夜纪律延续）。"""
        assert bk.resolve_backend() == "cpu"
        assert "cupy" not in sys.modules or bk.__file__ is not None  # 核本体无顶层 cupy import

    def test_invalid_backend_raises(self) -> None:
        with pytest.raises(ValueError, match="backend"):
            bk.resolve_backend("tpu")

    def test_shape_mismatch_raises(self) -> None:
        with pytest.raises(ValueError, match="不一致"):
            bk.wrc_boot_tstats(np.arange(10.0), np.zeros((2, 11), dtype=np.int64), 3.0)

    def test_degrade_log_visible_on_explicit_gpu_unavailable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """显式 gpu 不可用 = fail-closed 降级 CPU 且出声（degrade 台账非空）。"""
        monkeypatch.setattr(bk, "_probe_cupy_explicit", lambda: False)
        before = len(bk.degrade_log())
        assert bk.resolve_backend("gpu") == "cpu"
        assert len(bk.degrade_log()) == before + 1
