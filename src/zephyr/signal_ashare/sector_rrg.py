# [BLUEPRINT] MOD-SIG-026 supplement | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/22_sector_rotation_spec.md §3.1④
# [MODULE] zephyr.signal_ashare.sector_rrg
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS] (待 G05 选股引擎 / sector_gate rrg_filter / 10 号 §6.2 主线识别)
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] RS 基准=100; 象限 ∈ 4 值; 纯函数无副作用; 最小数据量 long×2+short=62 日
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 收盘价序列长度 < long×2+short 或基准价 ≤0 → ValueError
# [TESTS] tests/signal_ashare/test_sector_rrg.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: p_sector(板块指数收盘价日频序列, market_kline_sector_880) + p_bench(基准收盘价, 880001.SH)
# A1: RS(t) = 100 × P_sector/P_bench（标准化到 100 基准）
# A2: RS-Ratio(t) = EMA(RS,10)/EMA(RS,26)×100（JdK DualEma, >100 相对走强）
# A3: RS-Momentum(t) = EMA(RS-Ratio,10)/EMA(RS-Ratio,26)×100（动量的动量, 引导转向）
# A4: classify_quadrant(领先>100,>100 / 疲软>100,<100 / 滞后<100,<100 / 改善<100,>100)
# A5: confirm_quadrant_series(whipsaw 连续 2 日确认, 单日跳变不采信; 容许强趋势半圆)
# A6: rrg_zscore(Z=(RS-Ratio−63日均值)/63日标准差) + zscore_signal_adjust(领先 Z>+2 降级持有 / 改善 Z<−2 升级提前布局)
# O1: RRGPoint(rs_ratio, rs_momentum, quadrant) 序列 + 已确认象限序列 + 信号/强度调整分
# [/ALGO_FLOW]
"""RRG 相对旋转图（22 号 spec §3.1④，轮动序列主算法，BM-SEL-08 缺失态补施工）。

JdK（Julius de Kempenaer）DualEma 标准公式（xkqg/quantifiedtrader 2026 依据）：
  RS          = 100 × P_sector / P_bench
  RS-Ratio    = EMA(RS, 10) / EMA(RS, 26) × 100
  RS-Momentum = EMA(RS-Ratio, 10) / EMA(RS-Ratio, 26) × 100

四象限 = 轮动序列四阶段：领先（接棒中可买）→ 疲软（见顶持有/减仓）
→ 滞后（回避）→ 改善（提前布局观察）→ 顺时针回领先。
强趋势半圆例外（领先→疲软→领先，State Street 2026-03）由确认规则天然容许。

与 10_regime_detector_spec §6.2 主线识别同源（Improving=苗头 / Leading=确认 /
Weakening=退潮 / 象限转换=切换）。与 ranking_engine 第 5 因子不重复：
ranking 是当日截面快照选推送池，RRG 是时序变化率追轮动序列。

收缩登记：transition matrix 概率门限、21d/63d/252d 三时间框架交叉、
θ/r 旋转角度追踪本轮未施工（§3.1④ RRG 增强第 2 项与步骤 5 角度法，远期增强）。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# ------------------------------------------------------------------
# 常量（22 号 spec §3.1④ 参数）
# ------------------------------------------------------------------

DEFAULT_SHORT_PERIOD = 10  # DualEma 短窗
DEFAULT_LONG_PERIOD = 26  # DualEma 长窗
DEFAULT_CONFIRM_DAYS = 2  # whipsaw 连续确认天数（2-3 日，取 2）
DEFAULT_ZSCORE_WINDOW = 63  # Z-score 滚动窗口（63 日）
ZSCORE_STRETCH = 2.0  # |Z|>2 = 统计拉伸/异常压缩

#: 象限 → 板块强度综合层调整分（§3.1④ 象限→交易信号映射表）
QUADRANT_STRENGTH_ADJUST: dict[str, float] = {
    "LEADING": 0.05,
    "IMPROVING": 0.02,
    "WEAKENING": -0.03,
    "LAGGING": -0.08,
}

#: 象限 → 基础交易信号
QUADRANT_BASE_SIGNAL: dict[str, str] = {
    "LEADING": "BUY_CANDIDATE",  # 买入候选（接棒中）
    "IMPROVING": "WATCH_EARLY",  # 提前布局候选（观察）
    "WEAKENING": "HOLD_REDUCE",  # 持有/减仓（见顶）
    "LAGGING": "AVOID",  # 回避/拦截
}


class RRGQuadrant(str, Enum):
    """RRG 四象限"""

    LEADING = "LEADING"  # 领先：RS-Ratio>100 且 RS-Momentum>100
    WEAKENING = "WEAKENING"  # 疲软：RS-Ratio>100 且 RS-Momentum<100
    LAGGING = "LAGGING"  # 滞后：RS-Ratio<100 且 RS-Momentum<100
    IMPROVING = "IMPROVING"  # 改善：RS-Ratio<100 且 RS-Momentum>100


@dataclass(frozen=True)
class RRGPoint:
    """RRG 单日落点"""

    rs_ratio: float
    rs_momentum: float
    quadrant: RRGQuadrant


# ------------------------------------------------------------------
# EMA（通达信口径：种子=首值，adjust=False 等价递推）
# ------------------------------------------------------------------


def ema_series(values: list[float], span: int) -> list[float]:
    """指数移动平均序列（alpha=2/(span+1)，种子=首值，无预热 NaN）。"""
    if not values:
        return []
    alpha = 2.0 / (span + 1)
    out = [values[0]]
    for v in values[1:]:
        out.append(alpha * v + (1.0 - alpha) * out[-1])
    return out


# ------------------------------------------------------------------
# RRG 计算（JdK DualEma）
# ------------------------------------------------------------------


def compute_rrg_series(
    p_sector: list[float],
    p_bench: list[float],
    *,
    short: int = DEFAULT_SHORT_PERIOD,
    long: int = DEFAULT_LONG_PERIOD,
) -> list[RRGPoint]:
    """计算 RRG 序列（RS-Ratio / RS-Momentum / 四象限落点）。

    Args:
        p_sector: 板块指数收盘价日频序列（时间升序，market_kline_sector_880）。
        p_bench: 基准收盘价序列（880001.SH；缺失基准由调用方以全板块均值替代）。
        short: DualEma 短窗（默认 10）。
        long: DualEma 长窗（默认 26）。

    Returns:
        RRGPoint 列表（与输入等长，时间升序）。

    Raises:
        ValueError: 序列长度不一致、长度 < long×2+short（最小 62 日）或基准价 ≤0。
    """
    if len(p_sector) != len(p_bench):
        raise ValueError("板块与基准收盘价序列长度必须一致")
    min_len = long * 2 + short
    if len(p_sector) < min_len:
        raise ValueError(f"RRG 最小数据量 {min_len} 日（long×2+short），当前 {len(p_sector)} 日")
    if any(b <= 0 for b in p_bench):
        raise ValueError("基准收盘价必须为正")

    rs = [100.0 * s / b for s, b in zip(p_sector, p_bench, strict=True)]
    rs_ema_s = ema_series(rs, short)
    rs_ema_l = ema_series(rs, long)
    rs_ratio = [100.0 * e_s / e_l for e_s, e_l in zip(rs_ema_s, rs_ema_l, strict=True)]

    mom_ema_s = ema_series(rs_ratio, short)
    mom_ema_l = ema_series(rs_ratio, long)
    rs_momentum = [100.0 * e_s / e_l for e_s, e_l in zip(mom_ema_s, mom_ema_l, strict=True)]

    return [
        RRGPoint(rs_ratio=r, rs_momentum=m, quadrant=classify_quadrant(r, m))
        for r, m in zip(rs_ratio, rs_momentum, strict=True)
    ]


def classify_quadrant(rs_ratio: float, rs_momentum: float) -> RRGQuadrant:
    """(RS-Ratio, RS-Momentum) 二维坐标 → 四象限（100 为中性分界线）。"""
    if rs_ratio > 100.0:
        return RRGQuadrant.LEADING if rs_momentum > 100.0 else RRGQuadrant.WEAKENING
    return RRGQuadrant.IMPROVING if rs_momentum > 100.0 else RRGQuadrant.LAGGING


# ------------------------------------------------------------------
# whipsaw 确认（连续 2 日保持新象限才采信，单日跳变=假信号）
# ------------------------------------------------------------------


def confirm_quadrant_series(
    quadrants: list[RRGQuadrant],
    *,
    confirm_days: int = DEFAULT_CONFIRM_DAYS,
) -> list[RRGQuadrant]:
    """象限序列 whipsaw 确认平滑（已确认状态须连续 confirm_days 日才切换）。

    强趋势半圆（领先→疲软→领先）天然容许：疲软连续 2 日即确认，
    再回领先连续 2 日亦确认，不做路径禁则。
    """
    if not quadrants:
        return []
    confirmed = quadrants[0]
    candidate = quadrants[0]
    streak = 0
    out = [confirmed]
    for q in quadrants[1:]:
        if q == confirmed:
            candidate = confirmed
            streak = 0
        elif q == candidate:
            streak += 1
            if streak >= confirm_days:
                confirmed = q
                streak = 0
        else:
            candidate = q
            streak = 1
            if streak >= confirm_days:
                confirmed = q
                streak = 0
        out.append(confirmed)
    return out


# ------------------------------------------------------------------
# Z-score 跨象限修正（closelook 2026-08-07）
# ------------------------------------------------------------------


def rrg_zscore(rs_ratio_series: list[float], *, window: int = DEFAULT_ZSCORE_WINDOW) -> float:
    """最新 RS-Ratio 的滚动 z-score：Z = (当前 − 63日均值) / 63日标准差。

    序列不足 window 时用全序列；样本 <2 或标准差为 0 返回 0.0（无修正）。
    """
    hist = rs_ratio_series[-window:] if len(rs_ratio_series) >= 2 else rs_ratio_series
    if len(hist) < 2:
        return 0.0
    mean = sum(hist) / len(hist)
    var = sum((x - mean) ** 2 for x in hist) / (len(hist) - 1)
    std = var**0.5
    if std == 0.0:
        return 0.0
    return (hist[-1] - mean) / std


def zscore_signal_adjust(quadrant: RRGQuadrant, z: float) -> str:
    """Z-score 跨象限修正后的交易信号。

    领先象限 Z>+2 = 透支，买入信号降级为持有；
    改善象限 Z<−2 = 异常压缩，升级为提前布局；其余返回基础信号。
    """
    if quadrant == RRGQuadrant.LEADING and z > ZSCORE_STRETCH:
        return "HOLD_REDUCE"
    if quadrant == RRGQuadrant.IMPROVING and z < -ZSCORE_STRETCH:
        return "EARLY_LAYOUT"
    return QUADRANT_BASE_SIGNAL[quadrant.value]


def quadrant_strength_adjust(quadrant: RRGQuadrant) -> float:
    """象限 → 板块强度综合层调整分（+0.05/+0.02/−0.03/−0.08）。"""
    return QUADRANT_STRENGTH_ADJUST[quadrant.value]
