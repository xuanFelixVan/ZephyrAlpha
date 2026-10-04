# [BLUEPRINT] MOD-REGIME-005 | docs/03_modules/_domain_regime/chip_distribution_engine/blueprint.md
# [MODULE] zephyr.regime.features.chip_distribution_engine
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; zephyr.factor.technical_indicators.chips(compute_chip_metrics)
# [CONSUMERS] MOD-REGIME-002(RegimeFeatureBuilder消费#12筹码结构/#5空间位置/S2底部筹码)——
#             声明面：实际零 import（2026-09-15 转正审计 CHIP-2），stub 在 risk_signal_builder 常量
# [CONSUMERS] TDM-E-L3-12-3 筹码分布分析节点（config/trading_decision_map.yaml）——winner 剖面
#             供给 IND-CHIPS-001 获利盘占比（2026-10-04 SW14 处方①接线，D21 第一步；
#             trial 期信号不进决策=裁定#257④ 纪律维持）
# [STARTUP] imported
# [MATURITY] trial  # 2026-09-16 裁定#257④：production 系虚标（零消费端+真实数据伪分布），打回 trial；量纲修复后以指数级试点身份再评估转正
# [INVARIANTS] total_distribution Σ=1.0; age_layers各层Σ=1.0; 32网格网格0=最低价网格31=最高价
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/chip_distribution_engine/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 降级场景码 ZA-REGIME-0050/0051/0052（blueprint §8）——全部降级不抛错，无异常类
# [TESTS] tests/regime/test_chip_distribution_engine.py
# [A_module] module_id=MOD-REGIME-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

筹码分布引擎（MOD-REGIME-005）— 华泰2026前沿算法。

从 OHLCV 自建筹码分布（非换手率代理），供 regime 特征管道判断：
- #12 筹码结构（健康/套牢/底部未堆积/高位派发）
- #5 空间位置
- S2 底部筹码堆积

核心算法：
1. VWAP 中心三角分布（当日增量 D_t）
2. 换手递推 C_t = (1-τ)×C_{t-1} + τ×D_t
3. 筹码龄分层（ultra_short/short/medium/long，衰减系数近似迁移）
4. 32 相对网格映射（跨股比较）

2026-09-16 量纲与 warmup 修复（裁定#257④，CHIP-1/CHIP-3）：
- VWAP 量纲自洽探测：个股 kline_daily.volume 实测为"手"（600519 全窗
  amount/close/volume 中位 100.04、全市场抽查 8 票中位 97.8~101.9，CH 只读实证；
  schema 注释"成交量(股)"失真），裸 amount/volume=100×价格伪 VWAP。现依次尝试
  raw、raw/100（手→股）、raw×100，取唯一落入当日 [low,high] 价格界者；全界外
  （指数表 volume 无 vwap 语义）降级典型价。
- 递推窗口与网格同窗：递推只跑末 lookback 日（与网格构建窗一致），消除
  "84% 历史日网格外均匀注水"（000300 实测 3406/4057 日）；同末日跨数据起点
  输出确定（窗口相同→逐字节一致）。
- τ 帧内 PIT：avg_vol 改窗口内 expanding（只用 ≤t 正量），消除"τ 含帧内未来量"。

2026-10-04 winner（获利盘）剖面（SW14 处方①，D21 第一步，Owner 批）：
- 新增 compute_winner_profile：直调 zephyr.factor.technical_indicators.chips::
  compute_chip_metrics（CYQ 迭代衰减分布内核，IND-CHIPS-001 供给
  chips_winner 获利盘占比）——禁在 regime 域第二套分布实现（nb1_b6 处方①）。
- 输入=OHLCV 序列 + 换手率三源解析（显式入参 > df turnover_rate 列 >
  float_share 派生：换手%=volume(股)/(流通股本万股×1e4)×100，tushare
  stock_daily_basic.float_share 万股原值口径，CH c1_market 在产 710 万行）；
  三源皆缺 → fail-open 降级（对齐 CYQ 类软降级语义）。
- 输出与既有剖面同构（available/chips_winner/…/degrade_reason），键恒在；
  空/缺列/全零成交量全场景不抛错（ZA-REGIME-0050 族降级契约）。
- D21 后续：流通股本工程到位后升级"单峰密集度"全语义（nb1_b6 处方③）。

# [ALGO_FLOW] external: docs/03_modules/_domain_regime/algo_flow/chip_distribution_engine.yaml
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from zephyr.factor.technical_indicators.chips import compute_chip_metrics

__all__ = [
    "triangular_pdf",
    "compute_vwap",
    "compute_daily_distribution",
    "turnover_recurse",
    "build_grid_prices",
    "compute_metrics",
    "compute_winner_profile",
    "ChipDistributionEngine",
]

# 筹码龄分层迁移率（衰减系数近似，蓝图 §3.3 L1）
# 每日各层有 migration_rate 比例的筹码迁移到下一层
# ultra_short(1-2天): avg 2天 → rate=0.5
# short(3-10天): avg 8天 → rate=0.125
# medium(11-100天): avg 50天 → rate=0.02
_MIGRATION_RATES = {"ultra_short": 0.5, "short": 0.125, "medium": 0.02}

# VWAP 量纲探测候选因子（raw、raw/100=手→股、raw×100=反向失真）
_VOLUME_UNIT_FACTORS = (1.0, 0.01, 100.0)


# ---------------------------------------------------------------------------
# 3.1 VWAP 中心三角分布
# ---------------------------------------------------------------------------


def triangular_pdf(p: float, center: float, low: float, high: float) -> float:
    """三角分布概率密度函数（VWAP 为中心）。

    Parameters
    ----------
    p      : 待求密度的价格点
    center : 三角分布中心（VWAP），峰值所在
    low    : 分布下界（当日最低价）
    high   : 分布上界（当日最高价）

    Returns
    -------
    概率密度值（[low, high] 之外为 0，center 处最大）
    """
    if p < low or p > high:
        return 0.0
    if high <= low:
        return 1.0  # 退化为单点分布
    rng = high - low
    if p <= center:
        if center <= low:
            # 中心在下界，左半退化
            return 2.0 / rng if p == center else 0.0
        return 2.0 * (p - low) / (rng * (center - low))
    else:
        if center >= high:
            # 中心在上界，右半退化
            return 2.0 / rng if p == center else 0.0
        return 2.0 * (high - p) / (rng * (high - center))


def compute_vwap(row: dict | pd.Series) -> float:
    """计算 VWAP（带量纲自洽探测）；无有效量额时用典型价格 (O+H+L+C)/4 降级。

    蓝图 §8 ZA-REGIME-0051：amount/volume 为 0/负/NaN 时降级。

    量纲探测（2026-09-16 CHIP-1 修复，裁定#257④）：依次尝试 raw、raw/100
    （volume 为"手"——个股 kline_daily 实测口径）、raw×100（反向失真），取唯一
    落入当日 [low, high] 价格界的候选；全部界外（如指数表 volume 无 vwap 语义）
    降级典型价。自洽数据（amount=volume×价格，含单测 fixture）raw 直接命中，
    行为不变。
    """
    o = float(row["open"])
    h = float(row["high"])
    low = float(row["low"])
    c = float(row["close"])
    typical = (o + h + low + c) / 4.0

    volume = float(row["volume"])
    amount = float(row["amount"])
    if not (volume > 0 and amount > 0):
        # NaN 参与比较恒 False，同走此路——防 NaN 伪 VWAP 下游毒化
        return typical

    lo, hi = (low, h) if low <= h else (h, low)
    raw = amount / volume
    for factor in _VOLUME_UNIT_FACTORS:
        candidate = raw * factor
        if lo <= candidate <= hi:
            return candidate
    return typical


def compute_daily_distribution(vwap: float, low: float, high: float, prices: np.ndarray) -> np.ndarray:
    """计算当日三角分布密度并离散化到价格网格，归一化 Σ=1.0。

    Parameters
    ----------
    vwap   : VWAP（三角分布中心）
    low    : 当日最低价
    high   : 当日最高价
    prices : 网格价格点（32个）

    Returns
    -------
    归一化的当日增量分布 D_t（长度=len(prices)，Σ=1.0）
    """
    prices = np.asarray(prices, dtype=float)
    n = len(prices)
    dist = np.zeros(n, dtype=float)

    if high <= low:
        return np.ones(n) / n

    rng = high - low
    # 向量化三角 PDF
    in_range = (prices >= low) & (prices <= high)
    left = in_range & (prices <= vwap)
    right = in_range & (prices > vwap)

    if vwap > low:
        dist[left] = 2.0 * (prices[left] - low) / (rng * (vwap - low))
    elif vwap == low:
        # 中心在下界：左半退化，只在 vwap 处有值
        dist[left & (prices == vwap)] = 2.0 / rng

    if vwap < high:
        dist[right] = 2.0 * (high - prices[right]) / (rng * (high - vwap))
    elif vwap == high:
        dist[right & (prices == vwap)] = 2.0 / rng

    total = dist.sum()
    if total > 0:
        dist /= total
    else:
        dist = np.ones(n) / n
    return dist


# ---------------------------------------------------------------------------
# 3.2 换手递推
# ---------------------------------------------------------------------------


def turnover_recurse(old: np.ndarray, new: np.ndarray, tau: float) -> np.ndarray:
    """换手递推公式 C_t = (1-τ)×C_{t-1} + τ×D_t。

    纯公式实现，不做额外归一化——当 old 和 new 均归一化（Σ=1）时，
    结果自然 Σ=(1-τ)×1+τ×1=1.0。调用方负责保证输入归一化。

    Parameters
    ----------
    old : 前一日筹码分布 C_{t-1}
    new : 当日增量分布 D_t
    tau : 换手率 ∈ [0, 1]

    Returns
    -------
    递推后分布 C_t = (1-τ)×old + τ×new
    """
    old = np.asarray(old, dtype=float)
    new = np.asarray(new, dtype=float)
    tau = float(np.clip(tau, 0.0, 1.0))
    return (1.0 - tau) * old + tau * new


# ---------------------------------------------------------------------------
# 3.5 32 相对网格映射
# ---------------------------------------------------------------------------


def build_grid_prices(low: float, high: float, n_grids: int = 32) -> np.ndarray:
    """构建 n 个等间距网格价格，grid[0]=low, grid[n-1]=high。

    跨股统一网格定义：网格 0 = 最低价，网格 31 = 最高价。
    """
    return np.linspace(low, high, n_grids)


# ---------------------------------------------------------------------------
# 3.6 衍生指标计算
# ---------------------------------------------------------------------------


def compute_metrics(dist: np.ndarray, age_layers: dict[str, np.ndarray] | None = None) -> dict[str, float]:
    """计算衍生指标（供 RegimeFeatureBuilder 直接消费）。

    Parameters
    ----------
    dist        : 总筹码分布（32网格归一化）
    age_layers  : 筹码龄分层分布（可选）

    Returns
    -------
    dict containing:
        long_term_bottom_ratio : 长期筹码底部网格占比（#12健康度，>0.6健康）
        upper_trap_peak        : 上方套牢峰强度
        bottom_accumulation    : 底部堆积度
        distribution_migration : 筹码迁移方向（正=上移派发，负=下移吸筹）
    """
    dist = np.asarray(dist, dtype=float)
    n = len(dist)
    bottom_n = max(1, n // 4)  # 底部 1/4
    top_n = max(1, n // 4)  # 顶部 1/4

    dist_sum = dist.sum()

    # 底部堆积度
    bottom_accumulation = float(dist[:bottom_n].sum() / dist_sum) if dist_sum > 0 else 0.0

    # 上方套牢峰强度（高位异常堆积的峰值超出均值的部分）
    top_section = dist[n - top_n :]
    upper_trap_peak = float(top_section.max() - top_section.mean()) if len(top_section) > 0 else 0.0

    # 长期筹码底部占比 & 筹码迁移方向
    long_term_bottom_ratio = 0.0
    distribution_migration = 0.0
    if age_layers is not None and "long" in age_layers:
        long_layer = np.asarray(age_layers["long"], dtype=float)
        long_sum = long_layer.sum()
        if long_sum > 0:
            long_term_bottom_ratio = float(long_layer[:bottom_n].sum() / long_sum)
            distribution_migration = float((long_layer[n - top_n :].sum() - long_layer[:bottom_n].sum()) / long_sum)

    return {
        "long_term_bottom_ratio": long_term_bottom_ratio,
        "upper_trap_peak": upper_trap_peak,
        "bottom_accumulation": bottom_accumulation,
        "distribution_migration": distribution_migration,
    }


# ---------------------------------------------------------------------------
# winner（获利盘）剖面 —— 直调 chips.py::CYQ 内核（IND-CHIPS-001 供给面）
# ---------------------------------------------------------------------------

_WINNER_SCHEMA_VERSION = "1.0"
_WINNER_SOURCE = "zephyr.factor.technical_indicators.chips.compute_chip_metrics (IND-CHIPS-001)"


def _winner_unavailable(reason: str, window_days: int = 0) -> dict[str, Any]:
    """winner 剖面降级形态（fail-open）：键恒在、值置空、原因可读，绝不抛错。"""
    return {
        "available": False,
        "chips_winner": None,
        "chips_avg_cost": None,
        "chips_cost_5": None,
        "chips_cost_15": None,
        "chips_cost_85": None,
        "chips_cost_95": None,
        "winner_series": None,
        "window_days": int(window_days),
        "degrade_reason": reason,
        "schema_version": _WINNER_SCHEMA_VERSION,
        "source": _WINNER_SOURCE,
    }


def _resolve_turnover_rate(
    df: pd.DataFrame,
    turnover_rate: pd.Series | None,
    float_share: float | None,
) -> tuple[pd.Series | None, str | None]:
    """换手率三源解析：显式入参 > df turnover_rate 列 > float_share 派生。

    返回 (turnover_rate_pct 序列或 None, 降级原因或 None)。全 NaN 列对齐 CYQ
    类 _soft_turnover 语义按"无源"降级（非 daily 周期=设计内 NULL 输出）。
    """
    if turnover_rate is not None:
        tr = pd.Series(turnover_rate)
        if tr.notna().any():
            return tr, None
    if "turnover_rate" in df.columns:
        tr = df["turnover_rate"]
        if tr.notna().any():
            return tr, None
    share = float(float_share) if float_share is not None else float("nan")
    if np.isfinite(share) and share > 0:
        # volume 统一为股（2026-09-22 量纲治本）；float_share=tushare 万股原值 → ×1e4 成股
        tr = df["volume"].astype(float) / (share * 1e4) * 100.0
        return tr, None
    return None, "no_turnover_source(缺换手率列/入参且 float_share 不可用)"


def compute_winner_profile(
    ohlcv_df: pd.DataFrame | None,
    *,
    turnover_rate: pd.Series | None = None,
    float_share: float | None = None,
    n_bins: int = 400,
) -> dict[str, Any]:
    """获利盘（winner）剖面——直调 zephyr.factor.technical_indicators.chips::CYQ 内核。

    IND-CHIPS-001（Chip Distribution CYQ）chips_winner 获利盘占比由本剖面供给消费：
    禁在 regime 域第二套分布实现（SW14 处方①/nb1_b6 三审"真源唯一"）。D21 第一步；
    "单峰密集度"全语义待流通股本工程（处方③）。trial 期信号不进决策（裁定#257④）。

    Parameters
    ----------
    ohlcv_df      : OHLCV DataFrame（columns: high/low/close/volume 必须；
                    turnover_rate 列可选）
    turnover_rate : 显式换手率%（优先级最高，可选）
    float_share   : 流通股本（万股，tushare stock_daily_basic.float_share 口径）；
                    仅当无换手率源时派生：换手%=volume(股)/(万股×1e4)×100
    n_bins        : CYQ 价格网格数（默认 400，与指标库 IND-CHIPS-001 params 同源）

    Returns
    -------
    dict（与引擎既有剖面同构，键恒在）：
        available     : 是否产出有效获利盘
        chips_winner  : 末日获利盘比例 [0,1]（成本≤close 的筹码质量占比）
        chips_avg_cost/cost_5/15/85/95 : 末日平均成本/成本分位
        winner_series : 逐日获利盘序列
        degrade_reason: 降级原因（available=False 时可读）
    全场景不抛错：None/空 df、缺硬列、缺换手源、全零成交量 → fail-open 降级
    （ZA-REGIME-0050 族降级契约对齐）。
    """
    if ohlcv_df is None or len(ohlcv_df) == 0:
        return _winner_unavailable("empty_data(空数据)")
    df = ohlcv_df
    missing = [c for c in ("high", "low", "close", "volume") if c not in df.columns]
    if missing:
        return _winner_unavailable(f"missing_columns(缺硬列:{','.join(missing)})")
    tr, degrade = _resolve_turnover_rate(df, turnover_rate, float_share)
    if tr is None:
        return _winner_unavailable(degrade or "no_turnover_source")
    if len(tr) != len(df):
        return _winner_unavailable("turnover_length_mismatch(换手率与K线行数不齐)")

    metrics = compute_chip_metrics(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        volume=df["volume"],
        turnover_rate_pct=tr,
        n_bins=int(n_bins),
    )
    winner = metrics["chips_winner"].to_numpy(dtype=float)
    last = winner[-1] if winner.size else float("nan")
    if not np.isfinite(last):
        return _winner_unavailable("no_chips_mass(全历史零成交量或末日无筹码)", window_days=len(df))

    def _last(col: str) -> float:
        v = float(metrics[col].to_numpy(dtype=float)[-1])
        return v if np.isfinite(v) else None

    return {
        "available": True,
        "chips_winner": float(last),
        "chips_avg_cost": _last("chips_avg_cost"),
        "chips_cost_5": _last("chips_cost_5"),
        "chips_cost_15": _last("chips_cost_15"),
        "chips_cost_85": _last("chips_cost_85"),
        "chips_cost_95": _last("chips_cost_95"),
        "winner_series": [float(x) if np.isfinite(x) else None for x in winner],
        "window_days": int(len(df)),
        "degrade_reason": None,
        "schema_version": _WINNER_SCHEMA_VERSION,
        "source": _WINNER_SOURCE,
    }


# ---------------------------------------------------------------------------
# 筹码分布引擎（端到端）
# ---------------------------------------------------------------------------


class ChipDistributionEngine:
    """筹码分布引擎——从 OHLCV 计算筹码分布（华泰2026前沿算法）。

    Usage::
        engine = ChipDistributionEngine()
        result = engine.compute(ohlcv_df, symbol="000300.SH")
        # result["total_distribution"]  → 32网格总分布（Σ=1.0）
        # result["age_layers"]["long"]  → 长期筹码分布
        # result["metrics"]             → 衍生指标
    """

    def __init__(self, n_grids: int = 32, lookback: int = 250, avg_turnover: float = 0.02):
        """
        Parameters
        ----------
        n_grids      : 网格数（默认32，跨股标准）
        lookback     : 参考区间长度（默认250交易日）；网格与递推均只使用末
                       lookback 日——窗口起点均匀先验即 warmup 语义（2026-09-16
                       CHIP-1.2/CHIP-3 修复，裁定#257④）
        avg_turnover : 平均换手率假设（默认2%，用于从volume估算tau）
        """
        self.n_grids = n_grids
        self.lookback = lookback
        self.avg_turnover = avg_turnover

    def compute(self, ohlcv_df: pd.DataFrame, symbol: str = "", float_share: float | None = None) -> dict[str, Any]:
        """端到端计算筹码分布。

        Parameters
        ----------
        ohlcv_df    : OHLCV DataFrame（columns: date/open/high/low/close/volume/amount）
        symbol      : 标的代码
        float_share : 流通股本（万股，可选）——透传 winner 剖面作换手率派生源

        Returns
        -------
        筹码分布结果 dict（见蓝图 §2.2）；winner 剖面键恒在（SW14 处方①，
        IND-CHIPS-001 供给面，缺数据 fail-open）
        """
        # 降级：空数据返回均匀分布
        if ohlcv_df is None or len(ohlcv_df) == 0:
            return self._uniform_result(symbol)

        df = ohlcv_df
        n = len(df)

        # 构建 32 相对网格（基于 lookback 区间的最低/最高价）
        lookback = min(self.lookback, n)
        recent = df.iloc[-lookback:]
        price_min = float(recent["low"].min())
        price_max = float(recent["high"].max())
        if price_max <= price_min:
            # 停牌或单一价格，降级为均匀分布
            date = self._get_date(df)
            return self._uniform_result(symbol, date, winner=compute_winner_profile(df, float_share=float_share))

        grid_prices = build_grid_prices(price_min, price_max, self.n_grids)

        # 估算换手率 tau（无流通股本数据时，用平均换手率假设）
        # CHIP-3 修复（2026-09-16）：avg_vol 只用窗口内 ≤t 的正量 expanding 均值，
        # 消除"τ 依赖帧内未来量"（旧实现取整帧均值，历史日 τ 含未来量，中间态不可
        # PIT 抽取）；窗口前 min_obs 日 tau=0（warmup 相位，只注入不换手）
        vol = recent["volume"].values.astype(float)
        tau_w = self._estimate_tau(vol)

        # 初始化分布（均匀）——窗口起点均匀先验 = warmup 语义
        uniform = np.ones(self.n_grids) / self.n_grids
        total_dist = uniform.copy()
        age_layers = {
            "ultra_short": uniform.copy(),
            "short": uniform.copy(),
            "medium": uniform.copy(),
            "long": uniform.copy(),
        }

        # 逐日递推——与网格同窗（CHIP-1.2 修复：旧实现递推全史 n 日而网格只按末
        # lookback 日构建，000300 实测 3406/4057 日（84.0%）当日高低区间完全在
        # 网格外→fallback 均匀注水；现递推只跑末 lookback 日，同末日跨数据起点
        # 输出确定）
        for t in range(lookback):
            row = recent.iloc[t]
            vwap = compute_vwap(row)
            daily_dist = compute_daily_distribution(vwap, float(row["low"]), float(row["high"]), grid_prices)
            t_now = float(tau_w[t])

            # 总分布换手递推
            total_dist = turnover_recurse(total_dist, daily_dist, t_now)

            # 筹码龄分层递推（turnover + migration）
            self._recurse_age_layers(age_layers, daily_dist, t_now)

        # 衍生指标
        metrics = compute_metrics(total_dist, age_layers)
        date = self._get_date(df)

        return {
            "symbol": symbol,
            "date": date,
            "grid_prices": grid_prices.tolist(),
            "total_distribution": total_dist.tolist(),
            "age_layers": {k: v.tolist() for k, v in age_layers.items()},
            "metrics": metrics,
            "winner": compute_winner_profile(df, float_share=float_share),
            "schema_version": "1.2",
            "window_days": int(lookback),
        }

    # expanding 均值最小观测数：窗口前若干日正量样本不足时 tau=0（warmup 相位）
    _TAU_MIN_OBS = 5

    def _estimate_tau(self, vol: np.ndarray) -> np.ndarray:
        """从成交量序列估算逐日 tau（窗口内 expanding 正量均值，PIT 清洁）。

        tau_t = clip(vol_t / (avg_vol_t / avg_turnover), 0, 1)；avg_vol_t 只依赖
        ≤t 的正量观测。volume<=0/NaN 日 tau=0（不换手，当日增量仍注入）。
        """
        vol = np.asarray(vol, dtype=float)
        vol_pos = np.where(vol > 0, vol, np.nan)
        avg_vol_t = pd.Series(vol_pos).expanding(min_periods=self._TAU_MIN_OBS).mean().to_numpy()
        with np.errstate(invalid="ignore", divide="ignore", over="ignore"):
            circ = avg_vol_t / self.avg_turnover
            tau = np.where(avg_vol_t > 0, vol / circ, 0.0)
        tau = np.nan_to_num(tau, nan=0.0, posinf=0.0, neginf=0.0)
        return np.clip(tau, 0.0, 1.0)

    def _recurse_age_layers(
        self,
        age_layers: dict[str, np.ndarray],
        daily_dist: np.ndarray,
        tau: float,
    ) -> None:
        """筹码龄分层递推（蓝图 §3.3，衰减系数近似迁移）。

        每日两步：
        1. Turnover：各层旧筹码按 (1-τ) 衰减，新筹码(τ×D_t)注入 ultra_short
        2. Migration：各层按迁移率将筹码转移到下一层
        3. 各层独立归一化（保证 Σ=1.0 不变量）
        """
        # Step 1: Turnover
        for layer in age_layers:
            age_layers[layer] = (1.0 - tau) * age_layers[layer]
        age_layers["ultra_short"] += tau * daily_dist

        # Step 2: Migration（各层按迁移率转移到下一层）
        mig_us = _MIGRATION_RATES["ultra_short"] * age_layers["ultra_short"]
        mig_s = _MIGRATION_RATES["short"] * age_layers["short"]
        mig_m = _MIGRATION_RATES["medium"] * age_layers["medium"]

        age_layers["ultra_short"] -= mig_us
        age_layers["short"] += mig_us - mig_s
        age_layers["medium"] += mig_s - mig_m
        age_layers["long"] += mig_m

        # Step 3: 各层归一化
        for layer in age_layers:
            s = age_layers[layer].sum()
            if s > 0:
                age_layers[layer] = age_layers[layer] / s

    def _uniform_result(
        self,
        symbol: str,
        date: str | pd.Timestamp | None = None,
        winner: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """降级：均匀分布（32网格各 1/32）；winner 剖面键恒在（缺省 fail-open）。"""
        uniform = np.ones(self.n_grids) / self.n_grids
        age = {k: uniform.copy() for k in ["ultra_short", "short", "medium", "long"]}
        return {
            "symbol": symbol,
            "date": date,
            "grid_prices": [0.0] * self.n_grids,
            "total_distribution": uniform.tolist(),
            "age_layers": {k: v.tolist() for k, v in age.items()},
            "metrics": compute_metrics(uniform, age),
            "winner": winner if winner is not None else _winner_unavailable("uniform_degrade(均匀降级)"),
            "schema_version": "1.0",
        }

    @staticmethod
    def _get_date(df: pd.DataFrame) -> str | pd.Timestamp | None:
        """安全获取最后一行日期。"""
        if "date" in df.columns and len(df) > 0:
            return df.iloc[-1]["date"]
        return None
