# [MODULE] zephyr.shared.utils.market_units
# [DOMAIN] D_SHARED
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] zephyr.factor.core.evaluation.backtest(load_history 消费端边界)；
#             zephyr.backtest.core.matching_engine(仅引用单位常量与判定tolerance)
# [STARTUP] imported
# [MATURITY] trial
# [INVARIANTS] 归一后 amount ≈ close × volume（中位比 ∈[0.9,1.1]）；
#              返回 close × adj_factor == 后复权真值（逐符号常数锚定）；
#              纯函数无 IO——探测结果只进 report，告警由调用方发
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入缺列->raise KeyError（调用方契约违例）；数据不可探测->标记
#                  suspect 并回退声明口径，永不静默算错
# [TTL] permanent
"""A 股日线行情「量纲 + 复权」消费端归一公共件（纯函数，零 IO）。

## 为什么需要本件（车道 K 两 P0 的源头口径实证）

CH 只读实证（`c1_market.kline_daily`，窗口 2025-09-16..2026-09-15，A_share，
n=1,326,613 有效行，探针 `.runtime/tmp/laneK_probe1.py` / `laneK_probe8.py`）：

1. **volume 列按 data_source 混存两种量纲**（判据 `amount/(close×volume)`）：

   | data_source | 行数 | 中位比 | 实际量纲 |
   |-------------|------|--------|----------|
   | `''`（主进料） | 1,254,478 (94.6%) | **100.04** | 手 |
   | `tushare` | 69,361 (5.2%) | **1.002** | 股（写入侧 `tushare_provider.py:927` 已 ×100） |
   | `Baostock` | 2,774 | **1.000** | 股 |

   表 schema 注释「成交量(股)」只对 5.4% 的行成立。**单一全局 ×100 会把 tushare/
   Baostock 的 5.2% 行错 100 倍** → 必须逐行自洽探测，而不是"补一个 ×100"。

2. **`kline_daily.adj_factor` 是死列**：全史 10,069,078 行中 `adj_factor != 1` 的行数
   = **0**（NULL 亦 0），tracker #197 的 `close×adj_factor` 恒等于 raw close → 复权修正
   件自出生即惰性，除权缺口无人纠正（现网窗口内除权幻影 44~63 次，见车道 K 报告）。

3. **真复权价在 `c1_market.kline_daily_hfq`**（后复权，源 `bdpan_hfq`）：窗口内逐日
   symbol 覆盖 93.7~94.2%（无低于 90% 的交易日），现网成交 619 票命中率 **99.996%**
   （149,774 日对仅 6 行缺）。

4. **`c1_market.adj_factor` 专表不可用作整窗乘子**：窗口后半段日行数从 ~7,000 塌到
   9~21（面板失维，仅剩零星事件行），且 2026-07 起多票因子被重定标到 ≈1
   （600036 6.4834→1.0274、000651 230.39→1.0505、600000 16.59→1.048、
   300750 1.9495→1.0036）——跨重定标日相乘会注入 −68%~−84% 的新幻影，比原病更重。
   这正是 #209②「adj_factor 混存两口径」的实证根源。

## 口径决策（第一性原理）

- **成交量**：探测到"手"的行 ×100 归一为**股**；探测不到的行按同标的主流量纲回填，
  仍不可判定时回退表声明口径（股）并把 `suspect=True` 交给调用方告警——绝不静默算错。
- **价格**：整窗用后复权真值，但**逐标的除以本窗末锚点**（等价"窗口内前复权"）——
  ① 收益序列与后复权逐位相同（常数在比值里抵消，除权幻影归零）；
  ② 价格量级贴近可交易真实价（后复权裸值 600036≈184 vs 真实≈41、格力≈13,000），
     保住整手取整/最低佣金/碎股等绝对价语义不失真；
  ③ 锚点是本窗已知的末值，不引入未来信息进入**收益**。
- **量价联合不变量**：`close_adj×volume_adj = (raw×k)×(shares/k) = raw×shares ≈ amount`
  → 归一后 `amount/(close×volume)` 恒应 ≈ 1，与 k 无关。这是本件的自洽绊线
  （`consistency_median`），偏离即 suspect。

先例：`zephyr.regime.features.chip_distribution_engine.compute_vwap`（commit 3dcfe9dd07）
用同族"量纲自洽探测 + 界外降级 + 不静默"手法（逐日 [low,high] 判据）。本件复用其判据
思想但升级为面板级分布统计 + 逐行双候选判决（因为本仓 volume 列是**混存**量纲，
单一因子选择在该列上必然错 5.2%）。regime/** 由并行车道持有，本件不改动该处——
收敛为公共件的消费端登记在车道 K 报告的"需主会话落"清单。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

__all__ = [
    "SHARES_PER_LOT",
    "VOLUME_MULTIPLIER_CANDIDATES",
    "CONSISTENCY_TOL",
    "REPORT_ATTR",
    "PRICE_FIELDS",
    "VolumeUnitProbe",
    "MarketPanelReport",
    "probe_volume_unit",
    "normalize_market_panel",
    "format_report",
    "iter_price_fields",
]

#: 源头口径：1 手 = 100 股（A 股交易/行情最小报单单位的 100 倍整手约定）
SHARES_PER_LOT = 100.0

#: 成交量量纲候选乘子：1=已是股（tushare/Baostock 写入腿）、100=手→股（主进料腿）
VOLUME_MULTIPLIER_CANDIDATES: tuple[float, ...] = (1.0, float(SHARES_PER_LOT))

#: 归一后的量价自洽判据容差：|amount/(close×volume) − 1| ≤ 0.1 视为自洽
CONSISTENCY_TOL = 0.10

#: VWAP 界内判据的放宽容差（分位取整/盘后大宗摊薄造成的贴边）
_BAND_TOL = 0.02

#: 归一报告挂在 DataFrame.attrs 上的键
REPORT_ATTR = "market_units_report"

#: 参与价格复权的字段
PRICE_FIELDS: tuple[str, ...] = ("open", "high", "low", "close")


@dataclass(frozen=True)
class VolumeUnitProbe:
    """成交量量纲逐行探测结果（面板级统计）。

    Attributes:
        n_resolved:        判据命中（唯一候选落入 [low,high] 价界）的行数
        n_unresolved:      两候选都不自洽的行数（缺 high/low、零量额、坏行）
        counts_by_multiplier: 各候选乘子被判定的行数（键=乘子，1.0=股 / 100.0=手）
        chosen_by_fill:    不可判定行按"同标的主流量纲→全场面流量纲"回填的行数
        default_applied:   完全无先验可用时回退声明口径（乘子 1.0）的行数
        consistency_median: 归一后 median(amount/(close×volume))（应 ≈ 1）
        suspect:           探测面不自洽（多数行不可判定 或 中位比越界）→ 调用方 MUST 告警
    """

    n_resolved: int = 0
    n_unresolved: int = 0
    counts_by_multiplier: Mapping[float, int] = field(default_factory=dict)
    chosen_by_fill: int = 0
    default_applied: int = 0
    consistency_median: float = float("nan")
    suspect: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "n_resolved": self.n_resolved,
            "n_unresolved": self.n_unresolved,
            "counts_by_multiplier": {str(k): v for k, v in self.counts_by_multiplier.items()},
            "chosen_by_fill": self.chosen_by_fill,
            "default_applied": self.default_applied,
            "consistency_median": self.consistency_median,
            "suspect": self.suspect,
        }


@dataclass(frozen=True)
class MarketPanelReport:
    """一次面板归一的完整披露件（回归测试与现网告警都读它，禁静默降级）。

    Attributes:
        volume:            量纲探测件
        adjustment_enabled: 是否提供了后复权真值并完成复权
        adjusted_rows:     完成复权（有因子锚点可用）的行数
        unadjusted_rows:   整标的无任何后复权因子 → 全窗退不复权（k=1）的行数
        carried_rows:      因子由同标的近邻行前向/后向携带补齐的行数（缺因子但不产生假跳变）
        unadjusted_symbols: 完全无复权因子的标的数（口径混用面，MUST 告警）
        max_price_scale_distortion: 逐行 |k−1| 最大值（本窗累计除权幅度）
        symbols:           面板内标的数
    """

    volume: VolumeUnitProbe
    adjustment_enabled: bool = False
    adjusted_rows: int = 0
    unadjusted_rows: int = 0
    carried_rows: int = 0
    unadjusted_symbols: int = 0
    max_price_scale_distortion: float = 0.0
    symbols: int = 0

    def as_dict(self) -> dict[str, object]:
        return {
            "volume": self.volume.as_dict(),
            "adjustment_enabled": self.adjustment_enabled,
            "adjusted_rows": self.adjusted_rows,
            "unadjusted_rows": self.unadjusted_rows,
            "carried_rows": self.carried_rows,
            "unadjusted_symbols": self.unadjusted_symbols,
            "max_price_scale_distortion": self.max_price_scale_distortion,
            "symbols": self.symbols,
        }


def _band_hit(vwap: np.ndarray, low: np.ndarray, high: np.ndarray) -> np.ndarray:
    """VWAP 是否落入当日价界 [low×(1−tol), high×(1+tol)]（NaN 恒 False）。"""
    lo = low * (1.0 - _BAND_TOL)
    hi = high * (1.0 + _BAND_TOL)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (vwap >= lo) & (vwap <= hi)


def probe_volume_unit(
    df: pd.DataFrame,
    *,
    volume_col: str = "volume",
    amount_col: str = "amount",
    close_col: str = "close",
    low_col: str = "low",
    high_col: str = "high",
    groups: pd.Series | None = None,
) -> tuple[pd.Series, VolumeUnitProbe]:
    """逐行自洽探测成交量量纲，返回 (乘子 Series, 探测件)。

    判据（与 chip 引擎 commit 3dcfe9dd07 同族，升级为双候选判决）：
      候选乘子 m ∈ {1（已是股）, 100（手→股）}，取使 `amount/(volume×m)` 落入当日
      [low, high] 价界者。两候选相差 100 倍，任何真实日振幅都不可能同时容纳 → 判决
      唯一；都命中（退化数据）时取 `amount/(close×volume×m)` 更接近 1 者。

    不可判定行（缺 high/low、零量额、NaN）：先按**同标的**已判定行的主流量纲回填
    （量纲是"生产腿"属性，标的内稳定），无同标的先验时按**全场**主流量纲回填，
    仍无可用先验才回退表声明口径（乘子 1）并计 `default_applied`。

    Args:
        groups: 与 df 同 index 的分组标签（通常是 symbol），用于不可判定行回填。
    """
    for col in (volume_col, amount_col, close_col):
        if col not in df.columns:
            raise KeyError(f"probe_volume_unit 缺列: {col}")

    vol = pd.to_numeric(df[volume_col], errors="coerce").to_numpy(dtype=float)
    amt = pd.to_numeric(df[amount_col], errors="coerce").to_numpy(dtype=float)
    cls = pd.to_numeric(df[close_col], errors="coerce").to_numpy(dtype=float)
    has_band = low_col in df.columns and high_col in df.columns
    low = pd.to_numeric(df[low_col], errors="coerce").to_numpy(dtype=float) if has_band else np.full(len(df), np.nan)
    high = pd.to_numeric(df[high_col], errors="coerce").to_numpy(dtype=float) if has_band else np.full(len(df), np.nan)

    usable = np.isfinite(vol) & np.isfinite(amt) & np.isfinite(cls) & (vol > 0) & (amt > 0) & (cls > 0)

    hits: dict[float, np.ndarray] = {}
    vwaps: dict[float, np.ndarray] = {}
    for m in VOLUME_MULTIPLIER_CANDIDATES:
        with np.errstate(invalid="ignore", divide="ignore"):
            vwap = amt / (vol * m)
        vwaps[m] = vwap
        if has_band:
            hits[m] = usable & _band_hit(vwap, low, high)
        else:
            # 无价界（缺 high/low）时退化为"量价自洽比值≈1"判据
            with np.errstate(invalid="ignore", divide="ignore"):
                ratio = amt / (cls * vol * m)
            hits[m] = usable & np.isfinite(ratio) & (np.abs(ratio - 1.0) <= CONSISTENCY_TOL)

    chosen = np.full(len(df), np.nan)
    uniq = usable & (np.add.reduce([hits[m].astype(int) for m in VOLUME_MULTIPLIER_CANDIDATES], axis=0) == 1)
    multi = usable & (np.add.reduce([hits[m].astype(int) for m in VOLUME_MULTIPLIER_CANDIDATES], axis=0) > 1)
    for m in VOLUME_MULTIPLIER_CANDIDATES:
        chosen = np.where(hits[m] & uniq, m, chosen)
    if multi.any():  # 退化双命中：取比值更接近 1 的候选
        near = {m: np.abs(vwaps[m] / cls - 1.0) for m in VOLUME_MULTIPLIER_CANDIDATES}
        best = np.argmin(np.stack([near[m] for m in VOLUME_MULTIPLIER_CANDIDATES]), axis=0)
        cand = np.asarray(VOLUME_MULTIPLIER_CANDIDATES, dtype=float)
        chosen = np.where(multi & np.isfinite(near[cand[0]]), cand[best], chosen)

    counts = {m: int(np.nansum(chosen == m)) for m in VOLUME_MULTIPLIER_CANDIDATES}
    n_resolved = int(np.isfinite(chosen).sum())
    n_unresolved = int(usable.sum()) - n_resolved + int((~usable).sum())

    filled = np.zeros(len(df), dtype=bool)
    defaulted = np.zeros(len(df), dtype=bool)
    pend = ~np.isfinite(chosen)
    if pend.any():
        modal = _modal_multiplier(chosen, counts)
        if groups is not None:
            grp = pd.Series(chosen, index=df.index).groupby(np.asarray(groups), observed=True)
            fallback = grp.transform(lambda s: _series_mode(s)).to_numpy(dtype=float)
        elif modal is not None:
            fallback = np.full(len(df), float(modal))
        else:
            fallback = np.full(len(df), np.nan)
        use_group = pend & np.isfinite(fallback)
        chosen[use_group] = fallback[use_group]
        filled[use_group] = True
        rest = ~np.isfinite(chosen)
        if rest.any() and modal is not None:
            chosen[rest] = modal
            filled[rest] = True
            rest = ~np.isfinite(chosen)
        defaulted[rest] = True
        chosen[rest] = VOLUME_MULTIPLIER_CANDIDATES[0]  # 表声明口径（股）——不猜，且计入告警

    with np.errstate(invalid="ignore", divide="ignore"):
        post = amt / (cls * vol * chosen)
    finite_post = post[np.isfinite(post)]
    median_post = float(np.median(finite_post)) if finite_post.size else float("nan")

    total = max(1, len(df))
    suspect = (n_resolved / total < 0.5) or not np.isfinite(median_post) or abs(median_post - 1.0) > CONSISTENCY_TOL
    probe = VolumeUnitProbe(
        n_resolved=n_resolved,
        n_unresolved=int(filled.sum()) + int(defaulted.sum()),
        counts_by_multiplier=counts,
        chosen_by_fill=int(filled.sum()),
        default_applied=int(defaulted.sum()),
        consistency_median=median_post,
        suspect=bool(suspect),
    )
    return pd.Series(chosen, index=df.index, name="volume_multiplier"), probe


def _series_mode(s: pd.Series) -> float:
    """组内主流乘子（无已判定行 → NaN 交给上层回退）。"""
    v = s.dropna().to_numpy(dtype=float)
    if v.size == 0:
        return float("nan")
    vals, cnts = np.unique(v, return_counts=True)
    return float(vals[int(np.argmax(cnts))])


def _modal_multiplier(chosen: np.ndarray, counts: Mapping[float, int]) -> float | None:
    """全场主流乘子（出现最多者）；无任何判定 → None。"""
    if not counts or sum(counts.values()) == 0:
        return None
    return float(max(counts.items(), key=lambda kv: kv[1])[0])


def normalize_market_panel(
    df: pd.DataFrame,
    *,
    adjusted: pd.DataFrame | None = None,
    groups: pd.Series | None = None,
    price_fields: Sequence[str] = PRICE_FIELDS,
) -> tuple[pd.DataFrame, MarketPanelReport]:
    """把 raw 日线面板一次性归一到「成交量=股 + 价格=复权连续」口径。

    Args:
        df:       raw 面板（列含 open/high/low/close/volume/amount，index 需按
                  (symbol, trade_date) 升序——末锚点取每标的最后一条）。
        adjusted: 后复权真值面板（列 open/high/low/close，与 df **同 index 同序**）；
                  None=不复权（仅归一量纲），逐行缺该 index → 该行退不复权并计数。
        groups:   分组标签（通常 symbol），用于量纲不可判定行回填与复权锚点分组。
                  None 时用 df.index 的 "symbol" level（无则整表一组）。

    Returns:
        (归一后面板, MarketPanelReport)——原 df 不被修改；新增披露列
        `close_raw/open_raw/high_raw/low_raw`（交易所原始价，涨跌停等真实价语义用）
        与 `volume_lots`（原始手/股混存原值），`adj_factor` 重写为
        "本表 close 还原为后复权价所需乘子"（逐标的常数锚点，恒 > 0 或 NaN→1）。

    Raises:
        KeyError: 必需列缺失（调用方契约违例）。
    """
    missing = [c for c in ("volume", "amount", *price_fields) if c not in df.columns]
    if missing:
        raise KeyError(f"normalize_market_panel 缺列: {missing}")

    out = df.copy()
    if groups is None:
        if isinstance(df.index, pd.MultiIndex) and "symbol" in (df.index.names or []):
            groups = pd.Series(df.index.get_level_values("symbol"), index=df.index)
        else:
            groups = pd.Series("_all_", index=df.index)
    groups = pd.Series(np.asarray(groups), index=df.index)

    # ── 1) 量纲：逐行自洽探测，一次性归一到「股」──
    mult, vprobe = probe_volume_unit(out, groups=groups)
    for f in price_fields:  # 探测/告警判据建立在原始价上，先留原值
        out[f"{f}_raw"] = pd.to_numeric(out[f], errors="coerce")
    out["volume_lots"] = pd.to_numeric(out["volume"], errors="coerce")
    out["volume"] = pd.to_numeric(out["volume"], errors="coerce") * mult

    # ── 2) 复权：后复权真值 → 窗口末锚定（等价窗口内前复权）──
    adj_enabled = bool(adjusted is not None and len(adjusted) > 0 and "close" in adjusted.columns)
    k = pd.Series(1.0, index=out.index, name="price_scale")
    n_missing = 0
    n_carried = 0
    no_adj_symbols = 0
    if adj_enabled:
        adj_close = pd.to_numeric(adjusted["close"], errors="coerce").reindex(out.index)
        raw_close = pd.to_numeric(out["close_raw"], errors="coerce")
        with np.errstate(invalid="ignore", divide="ignore"):
            s = (adj_close / raw_close).astype(float)  # 逐行后复权因子，缺行/0 价 → NaN
        s = s.where(np.isfinite(s) & (s > 0))
        grp = np.asarray(groups, dtype=object)
        # 缺因子行用**同标的近邻因子**前向+后向携带补齐——绝不回退 1.0：
        # 否则锚点 k≈0.5 的标的在缺因子上台阶处会被造出新幻影跳变（比原病更重）。
        s_filled = s.groupby(grp, observed=True).ffill().groupby(grp, observed=True).bfill()
        n_carried = int((s.isna() & s_filled.notna()).sum())
        # 锚点 = 同标的最后一个已知因子（面板须按 (symbol, trade_date) 升序）
        anchor_s = s_filled.groupby(grp, observed=True).transform("last")
        covered = anchor_s.notna() & (anchor_s > 0)
        n_missing = int((~covered).sum())
        no_adj_symbols = int(groups[~covered].nunique()) if n_missing else 0
        s_use = s_filled.where(covered, 1.0)  # 整标的无因子 → 全窗退不复权（组内一致无假跳变）
        anchor = anchor_s.where(covered, 1.0)
        with np.errstate(invalid="ignore", divide="ignore"):
            k_row = (s_use / anchor).to_numpy(dtype=float)
        ok = np.isfinite(k_row) & (k_row > 0)
        n_missing += int((covered & ~ok).sum())
        k = pd.Series(np.where(ok, k_row, 1.0), index=out.index)
        for f in price_fields:
            out[f] = pd.to_numeric(out[f"{f}_raw"], errors="coerce") * k
        # 复权空间股数 = 真实股数 / k（持仓单位与价格单位同步缩放，参与率才不失真）
        with np.errstate(invalid="ignore", divide="ignore"):
            out["volume"] = pd.to_numeric(out["volume"], errors="coerce") / k
        # adj_factor 语义重写为「本表 close 还原为后复权价所需乘子」（逐标的常数锚点）
        out["adj_factor"] = anchor
    # adj_enabled=False 时 **不动** adj_factor 列（#197 close×adj_factor 口径原样透传）

    out["volume"] = pd.to_numeric(out["volume"], errors="coerce").round(0)

    # ── 3) 归一后自洽绊线（量价联合不变量，与 k 无关）──
    with np.errstate(invalid="ignore", divide="ignore"):
        post = pd.to_numeric(out["amount"], errors="coerce") / (
            pd.to_numeric(out["close"], errors="coerce") * pd.to_numeric(out["volume"], errors="coerce")
        )
    finite = post[np.isfinite(post) & (post > 0)].to_numpy(dtype=float)
    median_post = float(np.median(finite)) if finite.size else float("nan")
    suspect = bool(vprobe.suspect or abs(median_post - 1.0) > CONSISTENCY_TOL)
    probe = VolumeUnitProbe(
        n_resolved=vprobe.n_resolved,
        n_unresolved=vprobe.n_unresolved,
        counts_by_multiplier=vprobe.counts_by_multiplier,
        chosen_by_fill=vprobe.chosen_by_fill,
        default_applied=vprobe.default_applied,
        consistency_median=median_post,
        suspect=suspect,
    )
    dist = (k - 1.0).abs()
    report = MarketPanelReport(
        volume=probe,
        adjustment_enabled=adj_enabled,
        adjusted_rows=int(len(out) - n_missing) if adj_enabled else 0,
        unadjusted_rows=n_missing if adj_enabled else int(len(out)),
        carried_rows=n_carried if adj_enabled else 0,
        unadjusted_symbols=no_adj_symbols if adj_enabled else 0,
        max_price_scale_distortion=float(dist.max()) if len(dist) else 0.0,
        symbols=int(groups.nunique()),
    )
    out.attrs[REPORT_ATTR] = report
    return out, report


def format_report(report: MarketPanelReport, context: str = "") -> str:
    """人读一行摘要（调用方 log 与车道复验都读它）。"""
    v = report.volume
    dist = ", ".join(f"×{m:g}→{n}行" for m, n in sorted(v.counts_by_multiplier.items())) or "无判定"
    adj = (
        f"复权[已启用 覆盖={report.adjusted_rows}行 携带补齐={report.carried_rows}行 "
        f"无因子={report.unadjusted_rows}行/{report.unadjusted_symbols}标的 "
        f"最大价缩放失真={report.max_price_scale_distortion:.4f}]"
        if report.adjustment_enabled
        else "复权[未启用/无因子源——价格为原始价]"
    )
    return (
        f"{context or 'market_panel'}: 标的={report.symbols} 量纲探测[{dist}] "
        f"不可判定={v.n_unresolved} 回填={v.chosen_by_fill} 兜底={v.default_applied} "
        f"归一后自洽中位 amount/(close×volume)={v.consistency_median:.4f} suspect={v.suspect} | {adj}"
    )


def iter_price_fields(fields: Iterable[str] | None = None) -> tuple[str, ...]:
    """暴露 PRICE_FIELDS 的只读副本（防调用方就地改元组）。"""
    return tuple(fields) if fields is not None else PRICE_FIELDS
