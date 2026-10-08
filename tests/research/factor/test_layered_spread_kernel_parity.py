# [BLUEPRINT] MOD-L02-007 | tests/research/factor/test_layered_spread_kernel_parity.py | layered spread xp 核对拍随行回归
# [TTL] permanent
"""layered spread xp 核 parity 随行（st-govfix-g1-20261007 重建）。

历史：原独立对拍测试曾并入 test_layered_backtest.py 后删除（遗留陈旧 pyc，
见 docs/_working/matrix_campaign/mining/layered_spread_kernel_wiring_v1.md §3 遗留），
kernel 的逐位对拍与提速实测（39-87x，历史口径 6.6x）自此无可执行随行——本册重建，
使 wiring 基准册的对拍结论有可重复验证面：

- layer_lookup vs pd.qcut 全网格零错位（quantile_replica 模式）；
- kahan_mean vs pandas groupby.agg(['mean']) 逐位（层均值面）；
- compute_layer_spread_kernel vs 纯 pandas 后备端到端逐位（随机面板+NaN+同值并列秩）；
- compute_layer_spread 默认 use_kernel=True 接线委托恒等；
- 提速随行（kernel vs pandas 比值下限，防"优化"回退成慢路径）；
- ERROR_CONTRACT：数据不足截面跳过/空面板返回空，两路径一致。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

lb = pytest.importorskip("zephyr.factor.analysis.layered_backtest")

layer_lookup = lb.layer_lookup
kahan_mean = lb.compute_layer_spread_kernel.__globals__["kahan_mean"]
compute_layer_spread = lb.compute_layer_spread
compute_layer_spread_kernel = lb.compute_layer_spread_kernel
parity_end_to_end = lb.parity_end_to_end


def _panel(t: int, c: int, nan_pct: float, seed: int, integer_vals: int | None = None) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    if integer_vals is not None:
        a = rng.integers(0, integer_vals, size=(t, c)).astype(np.float64)
    else:
        a = rng.standard_normal((t, c))
    if nan_pct > 0:
        a[rng.random(a.shape) < nan_pct] = np.nan
    return pd.DataFrame(a)


# ── 1. 层号映射网格零错位 ────────────────────────────────────────────────────


def test_layer_lookup_matches_qcut_grid():
    """layer_lookup(quantile_replica) vs pd.qcut：n=2..120 全量 + 高段抽样，k∈{2,3,5,7,10} 零错位。"""
    rng = np.random.default_rng(7)
    hi_ns = sorted(rng.choice(np.arange(121, 3001), size=40, replace=False).tolist())
    ks = (2, 3, 5, 7, 10)
    for n in list(range(2, 121)) + hi_ns:
        ranks = pd.Series(np.arange(1.0, n + 1.0))
        for k in ks:
            want = pd.qcut(ranks, k, labels=False).to_numpy().astype(np.int64)
            got = layer_lookup(n, k, "quantile_replica")
            assert np.array_equal(want, got), f"n={n} k={k} 错位 {np.nonzero(want != got)[0][:3]}"


def test_layer_lookup_cache_consistent():
    """(n,k) 级缓存命中后与首算逐位一致（防缓存态漂移）。"""
    a = layer_lookup(97, 5, "quantile_replica").copy()
    b = layer_lookup(97, 5, "quantile_replica")
    np.testing.assert_array_equal(a, b)


# ── 2. Kahan 层均值逐位 ─────────────────────────────────────────────────────


def test_kahan_mean_bitwise_matches_pandas_groupby():
    """kahan_mean vs pandas groupby.agg(['mean'])：多日多边界层全部逐位命中。"""
    rng = np.random.default_rng(11)
    mism = 0
    total = 0
    for day in range(30):
        n = int(rng.integers(10, 120))
        vals = rng.standard_normal(n)
        for lo in {0, 1, n // 2, max(n - int(rng.integers(1, 4)), 0)}:
            seg = vals[lo : lo + max(n // 10, 2)]
            if seg.size == 0:
                continue
            s = pd.Series(vals)
            layers = pd.Series(0, index=s.index)
            layers.iloc[lo : lo + max(n // 10, 2)] = 1
            want = float(s.groupby(layers).agg(["mean"]).loc[1, "mean"])
            got = kahan_mean(np.asarray(seg, dtype=np.float64))
            total += 1
            if want != got:  # 有限浮点 == 即逐位相等（无 -0/NaN 边角）
                mism += 1
    assert mism == 0, f"kahan_mean 逐位失配 {mism}/{total}"


# ── 3. 端到端逐位对拍 ───────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "t,c,nan_pct,seed,integer_vals",
    [
        (300, 50, 0.10, 11, None),
        (200, 80, 0.25, 12, None),
        (150, 60, 0.0, 13, None),
        (120, 40, 0.15, 14, 4),  # 同值并列秩：stress rank(method='first') 位置序对齐
        (100, 40, 0.0, 15, None),
    ],
)
def test_kernel_bitwise_vs_pandas_fallback(t, c, nan_pct, seed, integer_vals):
    """kernel vs use_kernel=False 纯 pandas 后备：值逐位相等+日期索引一致。"""
    fp = _panel(t, c, nan_pct, seed, integer_vals)
    rp = _panel(t, c, nan_pct, seed + 1000, integer_vals)
    want = compute_layer_spread(fp, rp, n_layers=5, use_kernel=False)
    got = compute_layer_spread_kernel(fp, rp, n_layers=5)
    assert want.index.equals(got.index), "日期索引不一致（跳过截面集合不同）"
    assert np.array_equal(want.to_numpy(), got.to_numpy()), (
        f"逐位失配 max|d|={np.max(np.abs(want.to_numpy() - got.to_numpy())) if len(want) else 0.0}"
    )


def test_module_parity_harness_all_bitwise():
    """模块自带 parity_end_to_end（wiring 基准册 §1 同源判据）：5/5 逐位零差。"""
    res = parity_end_to_end("quantile_replica")
    assert res["all_bitwise"] is True
    for case in res["cases"]:
        assert case["bitwise_equal"] is True, case
        assert case["max_abs_diff"] == 0.0, case
        assert case["days_gt_half_ulp"] == 0, case


def test_wiring_default_delegates_to_kernel():
    """接线契约：compute_layer_spread 默认 use_kernel=True 与直调 kernel 逐位恒等。"""
    fp = _panel(150, 40, 0.08, 21)
    rp = _panel(150, 40, 0.08, 1021)
    via_api = compute_layer_spread(fp, rp, n_layers=5)
    via_kernel = compute_layer_spread_kernel(fp, rp, n_layers=5)
    assert via_api.index.equals(via_kernel.index)
    assert np.array_equal(via_api.to_numpy(), via_kernel.to_numpy())


# ── 4. 提速随行（防优化回退成慢路径）────────────────────────────────────────


def test_kernel_speedup_companion():
    """kernel vs pandas 提速下限（实测 39-87x；阈值 3x 留 CI 负载余量，读数随测试输出留档）。"""
    fp = _panel(300, 50, 0.10, 31)
    rp = _panel(300, 50, 0.10, 1031)
    best_kernel = min(_timed(lambda: compute_layer_spread_kernel(fp, rp, n_layers=5)) for _ in range(3))
    best_pandas = min(_timed(lambda: compute_layer_spread(fp, rp, n_layers=5, use_kernel=False)) for _ in range(3))
    ratio = best_pandas / max(best_kernel, 1e-9)
    print(f"\n[speedup] kernel={best_kernel:.4f}s pandas={best_pandas:.4f}s ratio={ratio:.1f}x")
    assert ratio >= 3.0, f"kernel 提速回退：仅 {ratio:.2f}x（<3x 下限）"


def _timed(fn) -> float:
    import time as _t

    t0 = _t.perf_counter()
    fn()
    return _t.perf_counter() - t0


# ── 5. ERROR_CONTRACT 一致 ──────────────────────────────────────────────────


def test_insufficient_and_empty_contract():
    """空面板→空；数据不足截面跳过——两路径返回形状一致（契约对齐）。"""
    empty_f = pd.DataFrame()
    empty_r = pd.DataFrame()
    assert compute_layer_spread(empty_f, empty_r, n_layers=5, use_kernel=False).empty
    assert compute_layer_spread_kernel(empty_f, empty_r, n_layers=5).empty

    dates = pd.date_range("2025-01-01", periods=10, freq="D")
    fp = pd.DataFrame(np.random.default_rng(5).standard_normal((10, 2)), index=dates)
    rp = pd.DataFrame(np.random.default_rng(6).standard_normal((10, 2)), index=dates)
    # n_layers=8 > 截面有效数 2 → 全部跳过=空
    assert compute_layer_spread(fp, rp, n_layers=8, use_kernel=False).empty
    assert compute_layer_spread_kernel(fp, rp, n_layers=8).empty
