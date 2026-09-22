# [BLUEPRINT] MOD-L02-031 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.technical_indicators.chips
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.technical_indicators.indicator_base; pandas(pip); numpy(pip)
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider（包级 autodiscover 动态接线：延迟导入本包+注册表消费）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 筹码族 3 指标（CYQ 分布/SCR 集中度/CYC 成本均线），纯自实现 pandas/numpy；指标输入首次引入换手率（批10 契约扩张，输入仍为纯 DataFrame 无副方向数据依赖）；缺 turnover_rate 软降级为空输出（禁抛异常——provider 逐指标异常会跳过整标的）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] compute 输入空 DataFrame→返回空 DataFrame 不抛；缺 OHLCV 硬列→ValueError；缺 turnover_rate→返回空 DataFrame 不抛（非 daily 周期/基础表缺数=按设计输出 NULL）
# [TESTS] tests/zephyr/factor/technical_indicators/test_chips.py
# [A_module] module_id=MOD-L02-031 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""筹码族技术指标（3 个，批10 施工 2026-09-21）。

指标清单：CYQ（筹码分布 6 列：获利盘/平均成本/成本分位 5/15/85/95）/ SCR（筹码集中度 1 列，=集中度(90) 通达信同义）/ CHIP_CONC_90、CHIP_CONC_70（通达信集中度族 1 列各，批10 扩项）/ CYC（成本均线 4 列）。

批10 契约扩张（16 号 memo §2/§6.10）：技术指标输入首次引入换手率 turnover_rate——
CYQ/SCR/CYC.inf 需要日频换手率（c1_market.stock_daily_basic，批9 数据批）。
provider 仅在 daily 周期并入该列；其余周期/缺数据时筹码指标软降级：
  - CYQ/SCR：返回空 DataFrame（provider 跳过 → 表列 NULL，不前填不前视）
  - CYC：cyc_5/13/34 照算（仅需 OHLCV+amount），cyc_inf 全 NaN

CYQ 迭代衰减算法（标准全市场通用模型，逐日递推，PIT 安全——只用过去+当日数据）：
  1. 衰减：整个筹码分布 × (1 − clip(换手率%, 0, 100)/100)。换手率 NaN（停牌/缺口）→ 不衰减。
  2. 换手新增：当日成交量按 [low, high] 均匀铺入价格网格；一字板（high==low）全部质量
     落最近网格点。成交量 0 → 无新增。
  3. 价格网格：400 bins，初始=首日 [low, high]；当日高低价越界时按旧分布 CDF 线性插值
     质量守恒重建（仅扩张，不收缩；确定性）。
  4. 输出（每日）：
     - chips_winner  获利盘比例 = cost <= close 的筹码质量占比（[0,1]）
     - chips_avg_cost 平均成本 = Σ(price×mass)/Σmass
     - chips_cost_5/95 成本 5%/95% 分位 = CDF 首次越过 q 的网格价
  预热期：首日即有输出（首日换手形成初始分布）；全历史成交量为 0 → NaN 不前填。

SCR 筹码集中度：SCR = 100×(cost_95 − cost_5)/(cost_95 + cost_5)，[0,100]，越小越集中
（与 chips_cost_5/95 同源同口径，90/10 与 95/5 分位之争取 95/5——与自家输出列自洽）。

CYC 成本均线（通达信口径）：
  - cyc_N = Σ(amount, N) / Σ(volume, N)，N∈{5,13,34}——kline_daily volume 已统一为"股"
    （2026-09-22 量纲治本：miniqmt 写入端 手→股 ×100 + 存量 data_source='' 行 ×100 更正，
    对齐 DDL 注释/tushare/baostock/BJ 路径既有口径；病根实证留痕 16 号 memo §6.10）。
  - cyc_inf（无穷成本均线）= DMA(close, 换手率/100)：
    c[i] = c[i-1] + (close[i] − c[i-1]) × clip(tr[i],0,100)/100，种子=首日收盘。
    tr NaN → 该日不修正（c[i]=c[i-1]）。缺 turnover_rate → 全 NaN。
  预热期：cyc_N 前 N−1 根 NaN（rolling 满窗）；cyc_inf 首日即有值。

设计文档：docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/16_technical_indicator_catalog.md §6.10

# [ALGO_FLOW] external: docs/03_modules/_domain_factor/algo_flow/chips.yaml
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

import numpy as np
import pandas as pd

from zephyr.factor.technical_indicators.indicator_base import (
    TechnicalIndicatorBase,
    TechnicalIndicatorMeta,
    TechnicalIndicatorRegistry,
)

_N_BINS_DEFAULT = 400


def _bin_edges(centers: np.ndarray) -> np.ndarray:
    """网格中心点 → n+1 个等距边界（供 CDF 插值/质量重铺）。"""
    step = centers[1] - centers[0]
    return np.concatenate([centers - step / 2.0, [centers[-1] + step / 2.0]])


def _redistribute_mass(old_centers: np.ndarray, old_dist: np.ndarray, new_centers: np.ndarray) -> np.ndarray:
    """网格扩张时按旧分布 CDF 线性插值把质量重铺到新网格（质量守恒、确定性）。

    CDF 是分布的唯一不变量：旧网格上的阶梯 CDF 线性化后，在新网格边界上取样作差
    即得新各 bin 质量；浮点误差的负值截 0，总量最后精确归一。
    """
    old_edges = _bin_edges(old_centers)
    new_edges = _bin_edges(new_centers)
    cdf = np.concatenate([[0.0], np.cumsum(old_dist)])
    upper = np.interp(new_edges[1:], old_edges, cdf, left=0.0, right=cdf[-1])
    lower = np.interp(new_edges[:-1], old_edges, cdf, left=0.0, right=cdf[-1])
    new_mass = np.clip(upper - lower, 0.0, None)
    total_old = float(old_dist.sum())
    total_new = float(new_mass.sum())
    if total_new > 0.0 and total_old > 0.0:
        new_mass *= total_old / total_new
    return new_mass


def _quantile_price(cum_ratio: np.ndarray, grid: np.ndarray, q: float) -> float:
    """CDF 分位价：首个 cum_ratio >= q 的网格价（cum_ratio 单调不减，总质量已归一）。"""
    idx = int(np.searchsorted(cum_ratio, q, side="left"))
    if idx >= grid.size:
        idx = grid.size - 1
    return float(grid[idx])


def _initial_grid(lo0: float, hi0: float, n_bins: int) -> tuple[np.ndarray, float, float]:
    """首日网格：一字首日退化为极窄带；异常高低互换。"""
    if hi0 < lo0:
        lo0, hi0 = hi0, lo0
    if hi0 - lo0 < 1e-12:
        hi0 = lo0 + 1e-12
    return np.linspace(lo0, hi0, n_bins), lo0, hi0


def _decay_distribution(dist: np.ndarray, turnover_pct: float) -> np.ndarray:
    """换手率衰减一步：×(1−clip(tr,0,100)/100)；NaN（停牌/缺数）不衰减。"""
    if np.isfinite(turnover_pct):
        alpha = min(max(turnover_pct, 0.0), 100.0) / 100.0
        if alpha > 0.0:
            return dist * (1.0 - alpha)
    return dist


@dataclass
class _ChipGrid:
    """价格网格 + 筹码质量分布的演进状态（封装越界扩张/当日铺量/日指标）。"""

    centers: np.ndarray
    lo: float
    hi: float
    dist: np.ndarray
    n_bins: int

    def expand_if_needed(self, lo_i: float, hi_i: float) -> None:
        """当日高低价越界时按旧分布 CDF 质量守恒重铺到扩张网格（PIT 只用过去+当日）。"""
        if lo_i >= self.lo and hi_i <= self.hi:
            return
        new_lo = min(self.lo, lo_i)
        new_hi = max(self.hi, hi_i)
        new_grid = np.linspace(new_lo, new_hi, self.n_bins)
        self.dist = _redistribute_mass(self.centers, self.dist, new_grid)
        self.centers, self.lo, self.hi = new_grid, new_lo, new_hi

    def add_day_volume(self, lo_i: float, hi_i: float, vol_i: float) -> None:
        """当日换手新增筹码：均匀铺 [low, high]；一字板全部质量落最近网格点。"""
        if not (np.isfinite(vol_i) and vol_i > 0.0):
            return
        self.expand_if_needed(lo_i, hi_i)
        add = np.zeros_like(self.dist)
        if hi_i - lo_i < 1e-12:
            add[int(np.argmin(np.abs(self.centers - lo_i)))] += vol_i
        else:
            mask = (self.centers >= lo_i) & (self.centers <= hi_i)
            if not mask.any():
                mask[int(np.argmin(np.abs(self.centers - (lo_i + hi_i) / 2.0)))] = True
            add[mask] = vol_i / float(mask.sum())
        self.dist = self.dist + add

    def decay(self, turnover_pct: float) -> None:
        """换手率衰减一步：×(1−clip(tr,0,100)/100)；NaN（停牌/缺数）不衰减。"""
        self.dist = _decay_distribution(self.dist, turnover_pct)

    def day_metrics(self, close_i: float) -> tuple[float, float, float, float, float, float] | None:
        """单日输出六元组（winner, avg_cost, q05, q15, q85, q95）；无筹码（总量 0）返回 None → NaN。"""
        total = float(self.dist.sum())
        if not np.isfinite(total) or total <= 0.0:
            return None
        cum = np.cumsum(self.dist) / total
        winner = float(self.dist[self.centers <= close_i].sum()) / total if np.isfinite(close_i) else np.nan
        avg = float(np.dot(self.centers, self.dist)) / total
        return (
            winner,
            avg,
            _quantile_price(cum, self.centers, 0.05),
            _quantile_price(cum, self.centers, 0.15),
            _quantile_price(cum, self.centers, 0.85),
            _quantile_price(cum, self.centers, 0.95),
        )


def compute_chip_metrics(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    volume: pd.Series,
    turnover_rate_pct: pd.Series,
    n_bins: int = _N_BINS_DEFAULT,
) -> pd.DataFrame:
    """CYQ 迭代衰减筹码分布逐日指标（engine 单一真源，CYQ/SCR/CHIP_CONC 共用）。

    Returns:
        DataFrame(index=close.index, columns=[chips_winner, chips_avg_cost,
        chips_cost_5, chips_cost_15, chips_cost_85, chips_cost_95])。
        无筹码可用（全历史成交量为 0/NaN）或高低价缺失的行输出 NaN。
    """
    n = len(close)
    empty = pd.DataFrame(
        {
            "chips_winner": pd.Series(np.nan, index=close.index),
            "chips_avg_cost": pd.Series(np.nan, index=close.index),
            "chips_cost_5": pd.Series(np.nan, index=close.index),
            "chips_cost_15": pd.Series(np.nan, index=close.index),
            "chips_cost_85": pd.Series(np.nan, index=close.index),
            "chips_cost_95": pd.Series(np.nan, index=close.index),
        }
    )
    if n == 0:
        return empty

    h = high.to_numpy(dtype=float)
    l = low.to_numpy(dtype=float)
    c = close.to_numpy(dtype=float)
    v = volume.to_numpy(dtype=float)
    tr = turnover_rate_pct.to_numpy(dtype=float)
    if not (np.isfinite(l[0]) and np.isfinite(h[0])):
        return empty  # 首日高低缺失 → 无法定初始网格（输入已 validate 但防御）

    grid_arr, grid_lo, grid_hi = _initial_grid(l[0], h[0], n_bins)
    state = _ChipGrid(centers=grid_arr, lo=grid_lo, hi=grid_hi, dist=np.zeros(n_bins, dtype=float), n_bins=n_bins)

    out_winner = np.full(n, np.nan)
    out_avg = np.full(n, np.nan)
    out_q05 = np.full(n, np.nan)
    out_q15 = np.full(n, np.nan)
    out_q85 = np.full(n, np.nan)
    out_q95 = np.full(n, np.nan)

    for i in range(n):
        if not (np.isfinite(l[i]) and np.isfinite(h[i])):
            continue  # 该 bar 高低价缺失 → 整行 NaN（不前视不后视）
        state.decay(tr[i])
        state.add_day_volume(l[i], h[i], v[i])
        metrics = state.day_metrics(c[i])
        if metrics is None:
            continue
        out_winner[i], out_avg[i], out_q05[i], out_q15[i], out_q85[i], out_q95[i] = metrics

    return pd.DataFrame(
        {
            "chips_winner": pd.Series(out_winner, index=close.index),
            "chips_avg_cost": pd.Series(out_avg, index=close.index),
            "chips_cost_5": pd.Series(out_q05, index=close.index),
            "chips_cost_15": pd.Series(out_q15, index=close.index),
            "chips_cost_85": pd.Series(out_q85, index=close.index),
            "chips_cost_95": pd.Series(out_q95, index=close.index),
        },
        index=close.index,
    )


def _concentration_pct(cost_hi: float, cost_lo: float) -> float:
    """通达信集中度公式：100×(cost_hi−cost_lo)/(cost_hi+cost_lo)；分母退化 → NaN。

    集中度(N)=(cost_(50+N/2)−cost_(50−N/2))/(cost_(50+N/2)+cost_(50−N/2))×100：
    N=90 → (cost_95, cost_5)；N=70 → (cost_85, cost_15)。
    """
    denom = cost_hi + cost_lo
    if not (np.isfinite(denom) and abs(denom) > 1e-12):
        return np.nan
    return float(100.0 * (cost_hi - cost_lo) / denom)


def _soft_turnover(data: pd.DataFrame) -> pd.Series | None:
    """软取换手率列：列不存在或全 NaN → None（调用方按设计降级）；部分 NaN → 原样（逐日不衰减）。"""
    if data is None or "turnover_rate" not in data.columns:
        return None
    tr = data["turnover_rate"]
    if tr.notna().sum() == 0:
        return None
    return tr


class _ChipsValidateMixin(TechnicalIndicatorBase):
    """筹码族 validate 覆盖：turnover_rate 是软输入（非 daily 周期/缺基础数据=设计内降级），
    只硬校验其余列——否则缺列 ValueError 会经 provider 逐标的 except 跳过整标的全部指标。"""

    def validate(self, data: pd.DataFrame) -> bool:
        if data is None or data.empty:
            return False
        required = set(self.meta.input_columns) - {"turnover_rate"}
        missing = required - set(data.columns)
        if missing:
            raise ValueError(
                f"指标 '{self.meta.indicator_id}' 输入数据缺少列: {missing}。 需要: {required}，实际: {set(data.columns)}"
            )
        return True


@TechnicalIndicatorRegistry.register
class CYQ(_ChipsValidateMixin):
    """筹码分布（ChiP distribution CYQ 族：获利盘/平均成本/成本分位 5/15/85/95）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="cyq",
        name="筹码分布",
        category="chips",
        output_columns=[
            "chips_winner",
            "chips_avg_cost",
            "chips_cost_5",
            "chips_cost_15",
            "chips_cost_85",
            "chips_cost_95",
        ],
        input_columns=["high", "low", "close", "volume", "turnover_rate"],
        params={"bins": _N_BINS_DEFAULT},
        version="1.1.0",
        description="CYQ 迭代衰减筹码分布：获利盘比例/平均成本/5%15%85%95%成本分位（换手率衰减模型，批10 扩项+15/+85）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        tr = _soft_turnover(data)
        if tr is None:
            # 换手率不可用（非 daily 周期/基础表缺数）→ 按设计降级为空输出（列 NULL）
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        return compute_chip_metrics(
            high=data["high"],
            low=data["low"],
            close=data["close"],
            volume=data["volume"],
            turnover_rate_pct=tr,
            n_bins=int(params.get("bins", _N_BINS_DEFAULT)),
        )


@TechnicalIndicatorRegistry.register
class SCR(_ChipsValidateMixin):
    """筹码集中度（Chip concentration，通达信集中度(90) 同义；与 CYQ 成本分位同源）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="scr",
        name="筹码集中度",
        category="chips",
        output_columns=["scr"],
        input_columns=["high", "low", "close", "volume", "turnover_rate"],
        params={"bins": _N_BINS_DEFAULT},
        version="1.1.0",
        description="SCR=100×(cost95−cost5)/(cost95+cost5)=集中度(90) 通达信同义，[0,100] 越小越集中（与 chips_cost_5/95 同源）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        scr = _compute_concentration(data, params, 0.95, 0.05)
        return pd.DataFrame({"scr": pd.Series(scr, index=data.index)}, index=data.index)


def _compute_concentration(data: pd.DataFrame, params: dict, q_hi: float, q_lo: float) -> np.ndarray:
    """集中度公共内核：算 CYQ 分布 → 取两分位价 → 通达信集中度公式（向量化 NaN 透传）。

    q_hi/q_lo 为分布质量分位（如 0.95/0.05 对应集中度(90)，0.85/0.15 对应集中度(70)）。
    """
    tr = _soft_turnover(data)
    if tr is None:
        return np.full(len(data), np.nan)
    metrics = compute_chip_metrics(
        high=data["high"],
        low=data["low"],
        close=data["close"],
        volume=data["volume"],
        turnover_rate_pct=tr,
        n_bins=int(params.get("bins", _N_BINS_DEFAULT)),
    )
    lo_price = metrics[f"chips_cost_{int(round(q_lo * 100))}"].to_numpy(dtype=float)
    hi_price = metrics[f"chips_cost_{int(round(q_hi * 100))}"].to_numpy(dtype=float)
    return np.vectorize(_concentration_pct, otypes=[float])(hi_price, lo_price)


class _ChipConcBase(_ChipsValidateMixin):
    """CHIP_CONC_90/70 公共基类：通达信集中度(N) 条目族。

    集中度(N)=(cost_(50+N/2)−cost_(50−N/2))/(cost_(50+N/2)+cost_(50−N/2))×100。
    CHIP_CONC_90 与 SCR 同公式（SCR=集中度(90) 通达信同义异名，双条目系扩项工单
    明令+命名族一致性保留，memo §6.10 已记 overlap 说明）；CHIP_CONC_70 用新增
    cost_85/cost_15 分位列。
    """

    _n: ClassVar[int]
    _q_hi: ClassVar[float]
    _q_lo: ClassVar[float]
    _col: ClassVar[str]

    meta: ClassVar[TechnicalIndicatorMeta]

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        conc = _compute_concentration(data, params, self._q_hi, self._q_lo)
        return pd.DataFrame({self._col: pd.Series(conc, index=data.index)}, index=data.index)


@TechnicalIndicatorRegistry.register
class CHIP_CONC_90(_ChipConcBase):
    """集中度(90)：cost_95/cost_5（与 SCR 同公式，通达信命名族口径）。"""

    _n = 90
    _q_hi = 0.95
    _q_lo = 0.05
    _col = "conc_90"

    meta = TechnicalIndicatorMeta(
        indicator_id="chip_conc_90",
        name="筹码集中度90",
        category="chips",
        output_columns=["conc_90"],
        input_columns=["high", "low", "close", "volume", "turnover_rate"],
        params={"bins": _N_BINS_DEFAULT},
        version="1.0.0",
        description="集中度(90)=100×(cost_95−cost_5)/(cost_95+cost_5)（与 SCR 同公式，批10 扩项工单明令独立条目）",
    )


@TechnicalIndicatorRegistry.register
class CHIP_CONC_70(_ChipConcBase):
    """集中度(70)：cost_85/cost_15（批10 扩项新增分位对）。"""

    _n = 70
    _q_hi = 0.85
    _q_lo = 0.15
    _col = "conc_70"

    meta = TechnicalIndicatorMeta(
        indicator_id="chip_conc_70",
        name="筹码集中度70",
        category="chips",
        output_columns=["conc_70"],
        input_columns=["high", "low", "close", "volume", "turnover_rate"],
        params={"bins": _N_BINS_DEFAULT},
        version="1.0.0",
        description="集中度(70)=100×(cost_85−cost_15)/(cost_85+cost_15)（使用批10 扩项新增 cost_85/15 分位列）",
    )


@TechnicalIndicatorRegistry.register
class CYC(_ChipsValidateMixin):
    """成本均线（Cost moving averages，通达信 CYC1/2/3/∞ 口径）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="cyc",
        name="成本均线",
        category="chips",
        output_columns=["cyc_5", "cyc_13", "cyc_34", "cyc_inf"],
        input_columns=["close", "volume", "amount", "turnover_rate"],
        params={"periods": [5, 13, 34]},
        version="1.0.0",
        description="cyc_N=Σamount/Σvolume（kline_daily volume 已统一为股，2026-09-22 量纲治本）；cyc_inf=DMA(close,换手率/100)",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        periods = list(params.get("periods", [5, 13, 34]))
        close = data["close"].astype(float)
        volume = data["volume"].astype(float)
        amount = data["amount"].astype(float)

        out: dict[str, pd.Series] = {}
        for n in periods:
            amt_sum = amount.rolling(window=int(n), min_periods=int(n)).sum()
            vol_sum = volume.rolling(window=int(n), min_periods=int(n)).sum()  # volume 已统一为股（2026-09-22 量纲治本）
            cyc_n = amt_sum / vol_sum.replace(0.0, np.nan)  # 全停牌窗 → NaN
            out[f"cyc_{int(n)}"] = cyc_n

        tr = _soft_turnover(data)
        if tr is None:
            out["cyc_inf"] = pd.Series(np.nan, index=data.index)
        else:
            trv = tr.to_numpy(dtype=float)
            cv = close.to_numpy(dtype=float)
            inf_arr = np.full(cv.size, np.nan)
            prev_inf = np.nan
            for i in range(cv.size):
                if not np.isfinite(cv[i]):
                    continue  # 收盘缺失 → 该日 NaN，prev_inf 保持（不前视不硬补）
                if not np.isfinite(prev_inf):
                    prev_inf = cv[i]  # 种子=首个有效收盘
                else:
                    alpha = min(max(trv[i], 0.0), 100.0) / 100.0 if i < trv.size and np.isfinite(trv[i]) else 0.0
                    prev_inf = prev_inf + (cv[i] - prev_inf) * alpha
                inf_arr[i] = prev_inf
            out["cyc_inf"] = pd.Series(inf_arr, index=data.index)

        return pd.DataFrame(out, index=data.index)
