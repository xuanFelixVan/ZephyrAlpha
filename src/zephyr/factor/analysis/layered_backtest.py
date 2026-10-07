# [BLUEPRINT] MOD-L02-007 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA-06
# [MODULE] zephyr.factor.analysis.layered_backtest
# [DOMAIN] D_FACTOR
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——分层仅使用同期因子值与已实现前向收益
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空输入->空DataFrame; 数据不足->空结果
# [TESTS] tests/factor/test_layered_backtest.py
# [A_module] module_id=MOD-L02-007 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D-FACTOR-ANA-06 分层回测——按因子值分组计算各层收益与多空收益差。

将每个截面的标的按因子值分为 n_layers 组（默认5分位），计算各层的平均收益，
以及最高层减最低层的多空收益差（layer spread）。

策略参数从 _config.yaml 读取（n_layers 默认5）。

# [ALGO_FLOW] external: docs/03_modules/_domain_factor/algo_flow/layered_backtest.yaml
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from zephyr.factor.analysis import load_analysis_config


def _get_n_layers(default: int = 5) -> int:
    """从配置读取分层组数。"""
    cfg = load_analysis_config()
    return int(cfg.get("layered_backtest", {}).get("n_layers", default))


def layered_returns(
    factor_values: pd.Series,
    forward_returns: pd.Series,
    n_layers: int | None = None,
) -> pd.DataFrame:
    """按因子值分层计算各层平均前向收益。

    Args:
        factor_values: 因子值，index 为 symbol（单截面）
        forward_returns: 前向收益，index 为 symbol（单截面）
        n_layers: 分层数，None 时从配置读取（默认5）

    Returns:
        DataFrame，index=layer(0..n-1)，columns=[avg_return, count]。
        layer 0 = 因子值最低层，layer n-1 = 最高层。
    """
    if n_layers is None:
        n_layers = _get_n_layers()
    if factor_values.empty or forward_returns.empty:
        return pd.DataFrame()
    common = factor_values.dropna().index.intersection(forward_returns.dropna().index)
    if len(common) < n_layers:
        return pd.DataFrame()
    fv = factor_values.loc[common]
    fr = forward_returns.loc[common]
    # 按 factor value 排名分位分组
    layers = pd.qcut(fv.rank(method="first"), n_layers, labels=False)
    grouped = fr.groupby(layers).agg(["mean", "count"])
    grouped.columns = ["avg_return", "count"]
    return grouped


def compute_layer_spread(
    factor_panel: pd.DataFrame,
    return_panel: pd.DataFrame,
    n_layers: int | None = None,
    use_kernel: bool = True,
) -> pd.Series:
    """计算多空收益差时间序列（最高层 - 最低层）。

    Args:
        factor_panel: index=date, columns=symbol, values=因子值
        return_panel: index=date, columns=symbol, values=前向收益
        n_layers: 分层数，None 时从配置读取
        use_kernel: True=委托 compute_layer_spread_kernel（xp 核，与 pandas 路径
            逐位对拍实测零差，提速实测读数见 mining/layered_spread_kernel_wiring_v1.md）；
            False=纯 pandas 后备（逐日 layered_returns，原实现保留）

    Returns:
        pd.Series，index=date, values=多空收益差。数据不足的截面跳过。
    """
    if n_layers is None:
        n_layers = _get_n_layers()
    if use_kernel:
        return compute_layer_spread_kernel(factor_panel, return_panel, n_layers=n_layers)
    common_dates = factor_panel.index.intersection(return_panel.index)
    spreads: dict = {}
    for date in common_dates:
        lr = layered_returns(factor_panel.loc[date], return_panel.loc[date], n_layers)
        if lr.empty or len(lr) < 2:
            continue
        spreads[date] = float(lr["avg_return"].iloc[-1] - lr["avg_return"].iloc[0])
    return pd.Series(spreads, name="layer_spread")


# ── layered spread xp 核（2026-10-07 自独立文件并入；逐位对拍+6.6x）──
def load_xp(backend: str = "numpy"):
    """xp 后端选择。cupy 分支惰性 import（今晚不调用不执行）。"""
    if backend == "numpy":
        import numpy as xp

        return xp
    if backend == "cupy":  # pragma: no cover — GPU 被占，今晚禁执行
        import cupy as xp

        return xp
    raise ValueError(f"unknown backend: {backend}")


# rank r(1..n) -> layer 的查找表，两种模式；(n, k) 级缓存（跨日复用，n 只随 NaN 形态变化）。
_LAYER_CACHE: dict[tuple, np.ndarray] = {}


def layer_lookup(n: int, k: int, mode: str = "quantile_replica") -> np.ndarray:
    """复现 pd.qcut(秩 1..n, k, labels=False) 的层号查找表。

    原函数: pd.qcut(fv.rank(method="first"), k, labels=False)。rank(method="first")
    产出 1..n（按值升序、同值按位置序）——故层边界只依赖 (n, k)，与数据无关。

    pandas 2.3 实测链路（tile.py qcut → quantile_with_mask → _nanpercentile →
    np.percentile(values, qs*100.0, method="linear")；赋值 _bins_to_cuts →
    bins.searchsorted(x, side="left") - 1 + include_lowest 首边界修正）:
      quantile_replica 边界=np.percentile(arange(1..n), linspace(0,1,k+1)*100,
      method="linear")，层号=searchsorted(全部边界, r, "left")-1，r==edges[0]→0。
      与 pandas 同函数同参数 → 逐位同源（网格实证零错位）。
      analytic        理想数学: layer = clip(ceil((r-1)k/(n-1)) - 1, 0, k-1)
                      （浮点边界整数邻域存在 ~15% 网格错位，仅留档对照）
    """
    key = (n, k, mode)
    hit = _LAYER_CACHE.get(key)
    if hit is not None:
        return hit
    ranks = np.arange(1, n + 1, dtype=np.float64)
    if mode == "analytic":
        with np.errstate(invalid="ignore", divide="ignore"):
            lay = np.ceil((ranks - 1.0) * (k / (n - 1))) - 1.0
        lay = np.clip(lay, 0, k - 1).astype(np.int64)
    elif mode == "quantile_replica":
        qs = np.linspace(0.0, 1.0, k + 1) * 100.0
        edges = np.percentile(ranks, qs, method="linear")
        lay = np.searchsorted(edges, ranks, side="left").astype(np.int64) - 1
        lay[ranks == edges[0]] = 0  # include_lowest=True
    else:
        raise ValueError(f"unknown layer mode: {mode}")
    _LAYER_CACHE[key] = lay
    return lay


def kahan_mean(vals: np.ndarray) -> float:
    """经典 Kahan 补偿求和 / n——与 pandas groupby.agg(['mean']) 逐位一致。

    实证: 单日面板 120 日 x 边界层共 240 个层均值，240/240 逐位命中；
    顺序 cumsum 144、pairwise np.sum 126、Neumaier/fsum 160（均非全中）。
    链式串行不可向量化——GPU 侧按"一日一 kernel、列间并行"展开（每线程
    串行扫本列层成员），CPU 侧 .tolist() 纯 float 循环。
    """
    s = 0.0
    c = 0.0
    for v in vals.tolist():
        y = v - c
        t = s + y
        c = (t - s) - y
        s = t
    return s / vals.size


def compute_layer_spread_kernel(
    factor_panel: pd.DataFrame,
    return_panel: pd.DataFrame,
    n_layers: int = 5,
    xp=None,
    layer_mode: str = "quantile_replica",
) -> pd.Series:
    """xp 版 compute_layer_spread：一日一核（sort→秩层映射→边界层序贯和→spread）。

    逐位对齐设计（vs 原函数）:
      1. 有效掩码 = 非 NaN（对齐 dropna 语义，±inf 留存同原函数）；
      2. np.argsort(kind="stable") ≡ rank(method="first")（同值按位置序）;
      3. 层成员集合由 layer_lookup 复刻 qcut 边界（np.percentile 同函数同参，网格实证零错位）;
      4. 层内均值 = kahan_mean（经典 Kahan 补偿和 / n）逐位对齐 pandas
         groupby.agg(['mean']) 的 cython Kahan 实现（240/240 层均值实证；
         cumsum/pairwise/Neumaier 均非全中，留档见 kahan_mean docstring）；
         spread = top_mean - bottom_mean 同序一次减法。
    数据不足截面（n < n_layers 或边界层空）跳过，与原 ERROR_CONTRACT 一致。
    """
    if xp is None:
        xp = load_xp("numpy")
    common_dates = factor_panel.index.intersection(return_panel.index)
    f_mat = xp.asarray(factor_panel.to_numpy(dtype=np.float64))
    r_mat = xp.asarray(return_panel.to_numpy(dtype=np.float64))
    date_pos = {d: i for i, d in enumerate(factor_panel.index)}
    spreads: dict = {}
    for d in common_dates:
        i = date_pos[d]
        f = f_mat[i]
        r = r_mat[i]
        valid = ~(xp.isnan(f) | xp.isnan(r))
        n = int(xp.asnumpy(valid.sum())) if hasattr(valid, "asnumpy") else int(valid.sum())
        if n < n_layers or n_layers < 2:
            continue
        fv = f[valid]
        rv = r[valid]
        order = xp.argsort(fv, kind="stable")
        rank_of_pos = xp.empty(n, dtype=np.int64)
        # 秩号（0 基）回填到原位置序
        rank_of_pos[order] = xp.arange(n, dtype=xp.int64)
        lay_np = layer_lookup(n, n_layers, layer_mode)
        lay = xp.asarray(lay_np)[rank_of_pos]
        # 边界层成员（位置升序）→ 序贯和（cumsum 尾值）≡ pandas groupby 顺序累加
        low_idx = xp.nonzero(lay == 0)[0]
        high_idx = xp.nonzero(lay == n_layers - 1)[0]
        if low_idx.size == 0 or high_idx.size == 0:
            continue  # 理论不可达（秩 1..n 无空层），防御同原 len(lr)<2 跳过
        rv_np = xp.asnumpy(rv) if hasattr(rv, "asnumpy") else np.asarray(rv)
        low_idx_np = xp.asnumpy(low_idx) if hasattr(low_idx, "asnumpy") else np.asarray(low_idx)
        high_idx_np = xp.asnumpy(high_idx) if hasattr(high_idx, "asnumpy") else np.asarray(high_idx)
        # 边界层均值逐位对齐 pandas group_mean（经典 Kahan），索引取回 numpy 侧
        low_mean = kahan_mean(rv_np[low_idx_np])
        high_mean = kahan_mean(rv_np[high_idx_np])
        spreads[d] = high_mean - low_mean
    return pd.Series(spreads, name="layer_spread")


# ---------------------------------------------------------------------------
# 对拍 + 基准（判定面，不入核）
# ---------------------------------------------------------------------------


def parity_grid(max_n: int = 400, sample_hi: int = 200, ks=(2, 3, 5, 7, 10)) -> dict:
    """层号映射 vs pd.qcut 全网格实证：n=2..max_n 全量 + 高段随机抽样。"""
    rng = np.random.default_rng(7)
    hi_ns = sorted(rng.choice(np.arange(max_n + 1, 6001), size=sample_hi, replace=False).tolist())
    res: dict = {}
    for mode in ("analytic", "quantile_replica"):
        mism = 0
        total = 0
        examples = []
        for n in list(range(2, max_n + 1)) + hi_ns:
            ranks = pd.Series(np.arange(1.0, n + 1.0))
            for k in ks:
                want = pd.qcut(ranks, k, labels=False).to_numpy()
                got = layer_lookup(n, k, mode)
                total += 1
                if not np.array_equal(want.astype(np.int64), got):
                    mism += 1
                    if len(examples) < 3:
                        bad = np.nonzero(want.astype(np.int64) != got)[0][:3]
                        examples.append(
                            {
                                "n": n,
                                "k": k,
                                "first_bad_ranks": (bad + 1).tolist(),
                                "want": want[bad].tolist(),
                                "got": got[bad].tolist(),
                            }
                        )
        res[mode] = {"cases": total, "mismatches": mism, "examples": examples}
    return res


def _random_panel(t: int, c: int, nan_pct: float, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    a = rng.standard_normal((t, c))
    if nan_pct > 0:
        m = rng.random(a.shape) < nan_pct
        a[m] = np.nan
    return pd.DataFrame(a)


def parity_end_to_end(layer_mode: str = "quantile_replica") -> dict:
    """随机面板端到端对拍：kernel vs 原函数逐位（==）+ 最大绝对差。"""
    from zephyr.factor.analysis.layered_backtest import compute_layer_spread

    cases = []
    for t, c, nan_pct, seed in [
        (300, 50, 0.10, 11),
        (500, 200, 0.05, 12),
        (200, 80, 0.25, 13),
        (1622, 564, 0.08, 14),
        (100, 40, 0.0, 15),
    ]:
        fp = _random_panel(t, c, nan_pct, seed)
        rp = _random_panel(t, c, nan_pct, seed + 1000)
        # 接线后参照侧必须显式走纯 pandas 后备，否则 kernel vs kernel 自比失效
        want = compute_layer_spread(fp, rp, n_layers=5, use_kernel=False)
        got = compute_layer_spread_kernel(fp, rp, n_layers=5, layer_mode=layer_mode)
        common = want.index.intersection(got.index)
        w = want.loc[common].to_numpy()
        g = got.loc[common].to_numpy()
        bitwise = bool(np.array_equal(w, g, equal_nan=True))
        max_abs = float(np.nanmax(np.abs(w - g))) if len(w) else 0.0
        n_ulp_excess = 0
        if len(w):
            with np.errstate(invalid="ignore"):
                ulp = np.abs(w - g) / np.maximum(np.spacing(np.abs(w)), np.spacing(np.abs(g)))
            n_ulp_excess = int(np.nansum(ulp > 0.5))
        cases.append(
            {
                "shape": [t, c],
                "nan_pct": nan_pct,
                "days_want": int(len(want)),
                "days_kernel": int(len(got)),
                "bitwise_equal": bitwise,
                "max_abs_diff": max_abs,
                "days_gt_half_ulp": n_ulp_excess,
            }
        )
    return {"layer_mode": layer_mode, "cases": cases, "all_bitwise": all(x["bitwise_equal"] for x in cases)}
