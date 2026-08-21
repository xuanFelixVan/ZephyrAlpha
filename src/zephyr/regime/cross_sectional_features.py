# [BLUEPRINT] MOD-REGIME-007 | 待统筹登记
# [MODULE] zephyr.regime.cross_sectional_features
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] regime_feature_builder（可选开关，默认关）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] PIT严格(T日特征只用≤T数据;滚动窗口walk-forward,禁全样本归一);输出4列列序钉死(cross_dispersion/avg_pairwise_corr/vol_dispersion/momentum_breadth);截面样本<min_cs_names只该日4列全NaN;个股缺数据该日剔除不填补;抽样确定性(seed固定,同一面板同一输出)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CrossSectionalFeatureError(输入面板缺列/空面板/非法配置)
# [TESTS] tests/regime/test_cross_sectional_features.py
# [A_module] module_id=MOD-REGIME-007 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""横截面结构特征（MOD-REGIME-007，ALG-01）——regime 特征集的横截面维度补强。

背景（2026-08 架构审查 P1）：regime_feature_builder 既有 6 特征全部是
市场代理指数（沪深300）时序维度 + 广度派生量，缺乏**个股横截面结构**维度
（离散度/相关性/波动率结构/动量宽度）。本模块补齐 4 个横截面结构特征，
全部由日频 OHLCV 面板可算，PIT 安全：

  C1 cross_dispersion    — 截面收益离散度：全市场个股日收益的截面 std
                           （或 IQR/1.35 稳健版），20 日滚动均值平滑。
                           离散度飙升 = 市场分化极端（结构性行情/股灾前兆）。
  C2 avg_pairwise_corr   — 平均成对相关：个股日收益两两 Pearson 相关均值
                           （60 日窗）。恐慌期"一切相关趋于 1"，是 CRISIS 信号。
                           全市场两两组合 O(N²) 太大 → 分层抽样 ~200 只代表性
                           样本股（抽样纪律见下文）。
  C3 vol_dispersion      — 波动率离散：个股 20 日已实现波动率（年化）的截面 std。
                           波动率结构分化 = 风险定价不一致。
  C4 momentum_breadth    — 动量宽度：收盘价强于 MA20 的股票占比（%）。
                           宽度崩塌 = 指数靠少数权重股支撑的脆弱上涨。

PIT 铁律（与 MOD-REGIME-002 blueprint §6.1 一致）：
  - T 日特征只用 ≤ T 数据（rolling 窗口全部 trailing，无 center/未来项）；
  - 滚动窗口 walk-forward 归一化（分位/std 均为 trailing 窗口内计算），
    禁止全样本归一（全样本统计量含未来信息）；
  - 抽样选股在 t 日只用 ≤ t 的流动性排名（再平衡日冻结样本，前向填充）。

NaN 处理纪律：
  - 个股某日缺数据 → 该日把该股剔除出截面，**不填补**（pct_change 用
    fill_method=None，禁止前向填充制造假收益）；
  - 截面有效样本 < min_cs_names（默认 30）只 → 该日 4 列全部输出 NaN；
  - 平滑/相关窗口内数据不足 → NaN（warmup 期由下游 dropna 处理）。

avg_pairwise_corr 抽样纪律（配置项均可调）：
  - 每 corr_rebalance_days（默认 20）个交易日在再平衡日 t_reb 重选样本：
    以 ≤ t_reb 的 20 日平均成交额（liquidity，缺 amount 回退 volume）排名，
    按排名均分 corr_strata（默认 10）层，每层等量抽样
    corr_sample_size // corr_strata 只（确定性种子 = (random_state, t_reb)），
    低流动性层也能入选 → 全谱系代表性；
  - 再平衡日之间样本冻结（as-of 前向填充），同一面板同一输出（确定性）；
  - 入选门槛：t_reb 日回看 corr_window 内有效收益 ≥ corr_min_pair_obs；
  - 两两相关用 60 日窗 nan-aware 计算：列内标准化（自身有效值 ddof=0），
    协有效观测 < corr_min_pair_obs 的 pair 置 NaN 后取上三角均值；
    常数列（std=0）视为无效列剔除。

输入面板（compute_cross_sectional_features 的 panel 参数）支持两种形态：
  1. 长表 DataFrame：含 trade_date / symbol / close（必需）+ volume /
     amount（可选，作流动性分层依据）列；
  2. MultiIndex(trade_date, symbol) 或 MultiIndex(symbol, trade_date) 长表。

输出：pd.DataFrame，index=trade_date（升序），列序钉死为
CROSS_SECTIONAL_FEATURE_NAMES = [cross_dispersion, avg_pairwise_corr,
vol_dispersion, momentum_breadth]。

依据: 2026-08 架构审查报告 P1（92号清单 §5.1）/ 工单 ALG-01
Version: 0.1.0
"""

from __future__ import annotations

import logging
from typing import Final

import numpy as np
import pandas as pd

__all__: Final = [
    "CROSS_SECTIONAL_FEATURE_NAMES",
    "CrossSectionalFeatureError",
    "compute_cross_sectional_features",
]

_logger = logging.getLogger(__name__)

# 输出 4 列列序钉死（消费方按此序读，禁止插入/重排）
CROSS_SECTIONAL_FEATURE_NAMES: Final = [
    "cross_dispersion",
    "avg_pairwise_corr",
    "vol_dispersion",
    "momentum_breadth",
]

# IQR→std 稳健换算系数（正态假设下 std ≈ IQR / 1.35）
_IQR_TO_STD: Final = 1.35
# 年化因子（日频 → 年化波动率）
_ANNUALIZE: Final = 252


class CrossSectionalFeatureError(ValueError):
    """横截面结构特征输入错误（面板缺列/空面板/非法配置）。"""


# ---------------------------------------------------------------------------
# 公共入口
# ---------------------------------------------------------------------------


def compute_cross_sectional_features(
    panel: pd.DataFrame,
    *,
    date_col: str = "trade_date",
    symbol_col: str = "symbol",
    close_col: str = "close",
    volume_col: str = "volume",
    liquidity_col: str | None = "amount",
    dispersion_method: str = "iqr",
    dispersion_smooth_window: int = 20,
    corr_window: int = 60,
    corr_sample_size: int = 200,
    corr_strata: int = 10,
    corr_rebalance_days: int = 20,
    corr_min_pair_obs: int = 30,
    vol_window: int = 20,
    ma_window: int = 20,
    min_cs_names: int = 30,
    random_state: int = 42,
) -> pd.DataFrame:
    """计算 4 个横截面结构特征（纯函数，PIT 安全）。

    Args:
        panel: 个股日 K 面板。长表（含 trade_date/symbol/close 列）或
            MultiIndex(trade_date, symbol)/(symbol, trade_date) DataFrame。
            volume/amount 可选（amount 优先作流动性分层依据，缺失回退 volume，
            再缺失退化为随机抽样）。
        date_col: 日期列/索引层名。
        symbol_col: 代码列/索引层名。
        close_col: 收盘价列名。
        volume_col: 成交量列名。
        liquidity_col: 流动性分层列名（None 或缺列时回退 volume_col）。
        dispersion_method: 截面离散度口径，"iqr"（IQR/1.35 稳健版，默认）或 "std"。
        dispersion_smooth_window: 离散度平滑窗口（默认 20 日，需窗内全有效否则 NaN）。
        corr_window: 成对相关回看窗口（默认 60 日）。
        corr_sample_size: 相关抽样目标只数（默认 ~200，分层等量）。
        corr_strata: 流动性分层数（默认 10 层）。
        corr_rebalance_days: 样本再平衡间隔（默认 20 个交易日）。
        corr_min_pair_obs: pair 协有效观测下限（默认 30，不足置 NaN）。
        vol_window: 已实现波动率窗口（默认 20 日，年化 ×√252）。
        ma_window: 动量宽度均线窗口（默认 MA20）。
        min_cs_names: 截面有效样本下限（默认 30，不足该日 4 列全 NaN）。
        random_state: 抽样种子基（确定性：同一面板同一输出）。

    Returns:
        pd.DataFrame，index=trade_date（升序），列序 = CROSS_SECTIONAL_FEATURE_NAMES。
        warmup 期含 NaN，由下游 dropna 处理。

    Raises:
        CrossSectionalFeatureError: 面板为空、缺必需列、索引形态无法识别、
            dispersion_method 非法、窗口/样本数配置非法。
    """
    close_wide, liquidity_wide = _normalize_panel(
        panel,
        date_col=date_col,
        symbol_col=symbol_col,
        close_col=close_col,
        volume_col=volume_col,
        liquidity_col=liquidity_col,
    )
    if min_cs_names < 2:
        raise CrossSectionalFeatureError(f"min_cs_names 需 ≥2: {min_cs_names}")
    if dispersion_method not in ("iqr", "std"):
        raise CrossSectionalFeatureError(f"dispersion_method 仅支持 'iqr'/'std': {dispersion_method}")
    if dispersion_smooth_window < 1:
        raise CrossSectionalFeatureError(
            f"dispersion_smooth_window 需 ≥1（1=不平滑）: {dispersion_smooth_window}"
        )
    for name, w in (
        ("corr_window", corr_window),
        ("vol_window", vol_window),
        ("ma_window", ma_window),
    ):
        if w < 2:
            raise CrossSectionalFeatureError(f"{name} 需 ≥2: {w}")
    if corr_sample_size < min_cs_names:
        raise CrossSectionalFeatureError(
            f"corr_sample_size({corr_sample_size}) 需 ≥ min_cs_names({min_cs_names})"
        )

    # 个股日收益（fill_method=None：缺数据不填补，NaN 收益该日剔除出截面）
    returns = close_wide.pct_change(fill_method=None)

    # C1 截面收益离散度（20 日滚动均值平滑）
    cross_dispersion = _cross_dispersion(
        returns,
        method=dispersion_method,
        smooth_window=dispersion_smooth_window,
        min_cs_names=min_cs_names,
    )
    # C2 平均成对相关（60 日窗，分层抽样 ~200 只）
    avg_corr = _avg_pairwise_corr(
        returns,
        liquidity_wide,
        window=corr_window,
        sample_size=corr_sample_size,
        strata=corr_strata,
        rebalance_days=corr_rebalance_days,
        min_pair_obs=corr_min_pair_obs,
        min_cs_names=min_cs_names,
        random_state=random_state,
    )
    # C3 波动率离散（个股 20 日已实现波动率的截面 std）
    vol_dispersion = _vol_dispersion(returns, vol_window=vol_window, min_cs_names=min_cs_names)
    # C4 动量宽度（收盘价 > MA20 占比 %）
    momentum_breadth = _momentum_breadth(close_wide, ma_window=ma_window, min_cs_names=min_cs_names)

    out = pd.DataFrame(
        {
            "cross_dispersion": cross_dispersion,
            "avg_pairwise_corr": avg_corr,
            "vol_dispersion": vol_dispersion,
            "momentum_breadth": momentum_breadth,
        }
    )
    out = out.sort_index()
    _logger.info(
        "compute_cross_sectional_features: %d 日 × %d 列，有效行占比 %.1f%%",
        len(out),
        len(CROSS_SECTIONAL_FEATURE_NAMES),
        100.0 * float(out.notna().all(axis=1).mean()) if len(out) else 0.0,
    )
    return out


# ---------------------------------------------------------------------------
# 面板规范化
# ---------------------------------------------------------------------------


def _normalize_panel(
    panel: pd.DataFrame,
    *,
    date_col: str,
    symbol_col: str,
    close_col: str,
    volume_col: str,
    liquidity_col: str | None,
) -> tuple[pd.DataFrame, pd.DataFrame | None]:
    """把输入面板规范化为 date × symbol 宽表（close + liquidity）。

    Returns:
        (close_wide, liquidity_wide)。liquidity_wide 为 amount 优先、volume 回退；
        两者皆缺时为 None（调用方退化为随机抽样）。
    """
    if panel is None or len(panel) == 0:
        raise CrossSectionalFeatureError("输入面板为空")

    df = panel
    if isinstance(df.index, pd.MultiIndex):
        names = list(df.index.names)
        if date_col not in names or symbol_col not in names:
            raise CrossSectionalFeatureError(
                f"MultiIndex 层名需含 {date_col}/{symbol_col}: {names}"
            )
        df = df.reset_index()
    missing = [c for c in (date_col, symbol_col, close_col) if c not in df.columns]
    if missing:
        raise CrossSectionalFeatureError(f"面板缺必需列: {missing}")

    keep = [date_col, symbol_col, close_col, volume_col]
    if liquidity_col:
        keep.append(liquidity_col)
    df = df[[c for c in dict.fromkeys(keep) if c in df.columns]]
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df[close_col] = pd.to_numeric(df[close_col], errors="coerce")
    # 重复 (date, symbol) 保留最后一条（与 regime_data_loader 纪律一致）
    df = df.drop_duplicates(subset=[date_col, symbol_col], keep="last")
    df = df.sort_values([date_col, symbol_col])

    close_wide = df.pivot(index=date_col, columns=symbol_col, values=close_col)

    liq_col: str | None = None
    if liquidity_col and liquidity_col in df.columns:
        liq_col = liquidity_col
    elif volume_col in df.columns:
        liq_col = volume_col
    liquidity_wide = None
    if liq_col is not None:
        df[liq_col] = pd.to_numeric(df[liq_col], errors="coerce")
        liquidity_wide = df.pivot(index=date_col, columns=symbol_col, values=liq_col)
        # 列序对齐 close_wide（同源 pivot 天然一致，reindex 防御显式化）
        liquidity_wide = liquidity_wide.reindex(columns=close_wide.columns)

    return close_wide, liquidity_wide


# ---------------------------------------------------------------------------
# C1 截面收益离散度
# ---------------------------------------------------------------------------


def _cross_dispersion(
    returns: pd.DataFrame,
    *,
    method: str,
    smooth_window: int,
    min_cs_names: int,
) -> pd.Series:
    """全市场个股日收益的截面离散度（std 或 IQR/1.35），20 日滚动均值平滑。

    逐日截面：有效收益 < min_cs_names 只 → 该日 NaN（剔除缺数据个股，不填补）。
    平滑：trailing smooth_window 均值，min_periods=smooth_window（窗内有 NaN 则 NaN，
    保守纪律——不用残缺窗凑数）。
    """
    valid_cnt = returns.notna().sum(axis=1)
    if method == "std":
        daily = returns.std(axis=1, ddof=1)
    else:  # iqr 稳健版：IQR / 1.35（≈正态 std，对厚尾/离群稳健）
        q75 = returns.quantile(0.75, axis=1)
        q25 = returns.quantile(0.25, axis=1)
        daily = (q75 - q25) / _IQR_TO_STD
    daily = daily.where(valid_cnt >= min_cs_names)
    return daily.rolling(smooth_window, min_periods=smooth_window).mean()


# ---------------------------------------------------------------------------
# C2 平均成对相关（分层抽样）
# ---------------------------------------------------------------------------


def _select_stratified_sample(
    liquidity_rank: pd.Series,
    eligible: np.ndarray,
    *,
    sample_size: int,
    strata: int,
    seed: tuple[int, int],
) -> list[str]:
    """按流动性排名分层等量抽样（确定性）。

    eligible 只数按流动性降序均分 strata 层，每层等量抽 sample_size//strata 只
    （余数补给前几层），层内不足则全取。种子 = (random_state, 再平衡日位置) →
    同一面板同一输出。
    """
    elig_set = set(eligible.tolist())
    ranked = [s for s in liquidity_rank.index if s in elig_set]
    n = len(ranked)
    if n == 0:
        return []
    n_strata = min(strata, n)
    per = sample_size // n_strata
    rem = sample_size - per * n_strata
    rng = np.random.default_rng(list(seed))
    # 按排名均分层（contiguous blocks：第 0 层流动性最高）
    bounds = np.linspace(0, n, n_strata + 1).astype(int)
    picked: list[str] = []
    for k in range(n_strata):
        block = ranked[bounds[k] : bounds[k + 1]]
        take = min(per + (1 if k < rem else 0), len(block))
        if take <= 0:
            continue
        idx = rng.choice(len(block), size=take, replace=False)
        picked.extend(block[i] for i in sorted(idx))
    return picked


def _avg_pairwise_corr(
    returns: pd.DataFrame,
    liquidity: pd.DataFrame | None,
    *,
    window: int,
    sample_size: int,
    strata: int,
    rebalance_days: int,
    min_pair_obs: int,
    min_cs_names: int,
    random_state: int,
) -> pd.Series:
    """个股日收益两两 Pearson 相关的截面均值（60 日窗，分层抽样 ~200 只）。

    抽样纪律（PIT 安全）：
      - 每 rebalance_days 个交易日在 t_reb 重选样本：≤ t_reb 的 20 日平均流动性
        排名分层等量抽样；t_reb 日回看 window 内有效收益 < min_pair_obs 的
        个股无入选资格；
      - 再平衡日之间样本冻结；
      - liquidity 为 None 时退化为固定种子随机抽样（分层纪律不生效，记 warning）。

    相关计算（nan-aware）：窗内列内标准化（自身有效值，ddof=0）→
    corr_ij = Σ(z_i·z_j) / √(P_ii·P_jj)（P=协有效计数），协有效 < min_pair_obs
    的 pair 置 NaN；常数列（std=0）剔除。取上三角 nan 均值。
    """
    dates = returns.index
    t_total = len(dates)
    out = np.full(t_total, np.nan)
    symbols = list(returns.columns)
    sym_idx = {s: i for i, s in enumerate(symbols)}
    r_vals = returns.to_numpy(dtype=float)
    liq_vals = liquidity.to_numpy(dtype=float) if liquidity is not None else None
    if liquidity is None:
        _logger.warning("面板无 volume/amount 列，avg_pairwise_corr 抽样退化为随机抽样")

    if t_total < window:
        return pd.Series(out, index=dates)

    # 再平衡日序列：首个再平衡日 = 第 window-1 个（0 基，需满窗才算相关）
    reb_points = list(range(window - 1, t_total, rebalance_days))
    # 每日 → 生效样本（col 索引数组）；首个再平衡日前为 None（NaN）
    active: list[np.ndarray | None] = [None] * t_total
    current: np.ndarray | None = None
    reb_iter = iter(reb_points)
    next_reb = next(reb_iter, None)
    for t in range(t_total):
        if next_reb is not None and t == next_reb:
            current = _rebalance_sample(
                t,
                returns,
                r_vals,
                liq_vals,
                symbols,
                sym_idx,
                window=window,
                sample_size=sample_size,
                strata=strata,
                rebalance_days=rebalance_days,
                min_pair_obs=min_pair_obs,
                random_state=random_state,
            )
            next_reb = next(reb_iter, None)
        active[t] = current

    for t in range(window - 1, t_total):
        cols = active[t]
        if cols is None or len(cols) < min_cs_names:
            continue
        w = r_vals[t - window + 1 : t + 1][:, cols]
        out[t] = _mean_pairwise_corr_window(w, min_pair_obs=min_pair_obs, min_cs_names=min_cs_names)

    return pd.Series(out, index=dates)


def _rebalance_sample(
    t: int,
    returns: pd.DataFrame,
    r_vals: np.ndarray,
    liq_vals: np.ndarray | None,
    symbols: list[str],
    sym_idx: dict[str, int],
    *,
    window: int,
    sample_size: int,
    strata: int,
    rebalance_days: int,
    min_pair_obs: int,
    random_state: int,
) -> np.ndarray:
    """再平衡日 t 的样本重选（PIT：只用 ≤ t 数据）。"""
    # 入选资格：回看 window 内有效收益 ≥ min_pair_obs
    w = r_vals[t - window + 1 : t + 1]
    valid_cnt = np.isfinite(w).sum(axis=0)
    eligible = np.array([symbols[i] for i in np.nonzero(valid_cnt >= min_pair_obs)[0]])
    if len(eligible) == 0:
        return np.array([], dtype=int)

    if liq_vals is not None:
        # ≤ t 的 20 日平均流动性排名（缺数据日剔除，nan-aware，全 NaN 列 → NaN）
        lb = max(0, t - rebalance_days + 1)
        liq_slice = liq_vals[lb : t + 1]
        finite = np.isfinite(liq_slice)
        cnt = finite.sum(axis=0)
        sums = np.where(finite, liq_slice, 0.0).sum(axis=0)
        liq_mean = np.divide(sums, cnt, out=np.full(sums.shape, np.nan), where=cnt > 0)
        liq_s = pd.Series(liq_mean, index=symbols).dropna().sort_values(ascending=False)
        picked = _select_stratified_sample(
            liq_s,
            eligible,
            sample_size=sample_size,
            strata=strata,
            seed=(random_state, t),
        )
    else:
        rng = np.random.default_rng([random_state, t])
        take = min(sample_size, len(eligible))
        picked = list(eligible[rng.choice(len(eligible), size=take, replace=False)])

    return np.array([sym_idx[s] for s in picked], dtype=int)


def _mean_pairwise_corr_window(w: np.ndarray, *, min_pair_obs: int, min_cs_names: int) -> float:
    """单个 60×N 收益窗的平均成对相关（nan-aware）。

    常数列（std=0）与有效观测 < min_pair_obs 的列剔除；有效列 < min_cs_names
    → NaN；pair 协有效 < min_pair_obs → 该 pair NaN；上三角 nan 均值。
    """
    mask = np.isfinite(w)
    cnt = mask.sum(axis=0)
    # 列内标准化（自身有效值，ddof=0）；std=0 常数列剔除
    w_f = np.where(mask, w, 0.0)
    sums = w_f.sum(axis=0)
    means = np.divide(sums, cnt, out=np.full_like(sums, np.nan), where=cnt > 0)
    dev = np.where(mask, w - means, 0.0)
    var = np.divide((dev**2).sum(axis=0), cnt, out=np.full_like(sums, np.nan), where=cnt > 0)
    std = np.sqrt(var)
    col_ok = (cnt >= min_pair_obs) & np.isfinite(std) & (std > 0.0)
    if col_ok.sum() < min_cs_names:
        return np.nan
    z = np.divide(dev, std, out=np.zeros_like(dev), where=mask & (std > 0.0))
    z = np.where(mask & col_ok, z, 0.0)
    m = (mask & col_ok).astype(float)
    # 协有效计数矩阵 + 协方差和矩阵
    p = m.T @ m
    c = z.T @ z
    with np.errstate(invalid="ignore", divide="ignore"):
        denom = np.sqrt(np.diag(p))[:, None] * np.sqrt(np.diag(p))[None, :]
        corr = np.where(p >= min_pair_obs, c / np.where(denom > 0, denom, np.nan), np.nan)
    n = corr.shape[0]
    iu = np.triu_indices(n, k=1)
    pair_vals = corr[iu]
    pair_vals = pair_vals[np.isfinite(pair_vals)]
    if len(pair_vals) == 0:
        return np.nan
    return float(np.mean(pair_vals))


# ---------------------------------------------------------------------------
# C3 波动率离散
# ---------------------------------------------------------------------------


def _vol_dispersion(returns: pd.DataFrame, *, vol_window: int, min_cs_names: int) -> pd.Series:
    """个股 vol_window 日已实现波动率（年化）的截面 std。

    个股 HV = trailing vol_window 收益 std × √252（PIT：只用 ≤ t 收益）；
    截面 std（ddof=1）逐日计算，有效 HV < min_cs_names 只 → 该日 NaN。
    """
    hv = returns.rolling(vol_window).std(ddof=1) * np.sqrt(_ANNUALIZE)
    valid_cnt = hv.notna().sum(axis=1)
    return hv.std(axis=1, ddof=1).where(valid_cnt >= min_cs_names)


# ---------------------------------------------------------------------------
# C4 动量宽度
# ---------------------------------------------------------------------------


def _momentum_breadth(close_wide: pd.DataFrame, *, ma_window: int, min_cs_names: int) -> pd.Series:
    """收盘价强于 MA(ma_window) 的股票占比（%）。

    MA 为 trailing 窗口（含当日，PIT 安全）；判定分母 = 当日 close 与 MA 均有效
    的股票数（缺数据剔除，不填补）；分母 < min_cs_names → 该日 NaN。
    """
    ma = close_wide.rolling(ma_window).mean()
    valid = close_wide.notna() & ma.notna()
    above = (close_wide > ma) & valid
    denom = valid.sum(axis=1)
    pct = above.sum(axis=1) / denom.replace(0, np.nan) * 100.0
    return pct.where(denom >= min_cs_names)
