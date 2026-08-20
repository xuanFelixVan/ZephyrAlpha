# [BLUEPRINT] MOD-SIG-026 supplement | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/22_sector_rotation_spec.md §3.1②
# [MODULE] zephyr.signal_ashare.sector_pullback
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS] (待 G05 选股引擎 / BM-BUY-04 买入优先级)
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] fib_retrace_ratio ≥ 0; grade ∈ {A,B,C,None}; 纯函数无副作用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] swing_high ≤ swing_low → ValueError; 时间窗 <2 或 >15 交易日 → None(不评级)
# [TESTS] tests/signal_ashare/test_sector_pullback.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: swing_high/swing_low/current_price(回踩形态, 复用 intraday_buy_sell_point_analyzer PULLBACK 买点输出)
# I2: volume_ratios(最近 N 日成交量/50日均量 比率序列, 时间升序)
# I3: sector_strength(§3.1① 板块强度 0-100) + pullback_days + rotation_warning(warn_rotation)
# A1: fib_retrace_ratio = (high-current)/(high-low), Fib 回撤位
# A2: classify_volume_pattern(缩量递减至 35-50%→SHRINKING / 放量→EXPANDING / 其余→MIXED)
# A3: grade_pullback(Fib 档 × 量能档 × 强度档 三维取最弱档定级; 时间窗 <2/>15 不评级)
# O1: grade A(优先建仓)/B(分批建仓)/C(观望或突破失败降级)/None + pullback_action 映射
# [/ALGO_FLOW]
"""回踩质量 A/B/C 判定（22 号 spec §3.1②，BM-SEL-08 缺失态补施工）。

量化三维 + 时间窗：
  - Fib 回撤位：A=≤50%（浅/中）/ B=50%-61.8%（深）/ C=>61.8%（>78.6% 结构破坏）
  - 量能衰减：A=缩量序列（逐日递减至 50 日均量 35-50%）/ B=混合 / C=回踩放量（派发）
  - 板块强度：A=≥70 / B=40-70 / C=<40 或轮动预警
  - 时间窗：3-10 交易日健康；<2 非真回踩（盘中洗盘）；>15 转横盘失效——均不评级

三维错位时取最弱档定级（保守降级，服务突破失败降级用途）。
阈值待 G05/G08 校准（spec §6 待裁定）。
"""

from __future__ import annotations

# ------------------------------------------------------------------
# 常量（22 号 spec §3.1② 阈值）
# ------------------------------------------------------------------

FIB_SHALLOW_MAX = 0.50  # A 档回撤上限（38.2%-50% 浅/中）
FIB_DEEP_MAX = 0.618  # B 档回撤上限（61.8% 分水岭，健康趋势应守住）
FIB_STRUCTURE_BREAK = 0.786  # >78.6% 趋势结构破坏，回踩转反转

VOLUME_SHRINK_MAX = 0.50  # 缩量序列末段 ≤50 日均量 50%
VOLUME_EXPAND_MIN = 1.00  # 最新量 >50 日均量 = 放量

PULLBACK_MIN_DAYS = 2  # <2 交易日属盘中洗盘非真回踩
PULLBACK_HEALTHY_MAX_DAYS = 10  # 3-10 交易日健康窗
PULLBACK_STALE_DAYS = 15  # >15 交易日转横盘整理，回踩失效

STRENGTH_STRONG = 70.0
STRENGTH_MEDIUM = 40.0

#: 量能模式
VOLUME_SHRINKING = "SHRINKING"
VOLUME_MIXED = "MIXED"
VOLUME_EXPANDING = "EXPANDING"

#: 等级 → 买入优先级动作（BM-BUY-04）
PULLBACK_ACTIONS: dict[str, str] = {
    "A": "FULL_POSITION_PRIORITY",  # 优先建仓（满仓风险预算）
    "B": "HALF_POSITION_STAGED",  # 分批建仓（半仓风险预算）
    "C": "WATCH_OR_DOWNGRADE",  # 观望 / 突破失败降级
}

_GRADE_ORDER = {"A": 0, "B": 1, "C": 2}
_ORDER_GRADE = {0: "A", 1: "B", 2: "C"}


def fib_retrace_ratio(swing_high: float, swing_low: float, current_price: float) -> float:
    """Fibonacci 回撤比例 = (swing_high - current) / (swing_high - swing_low)。

    0 = 未回踩（创新高）；0.382-0.50 浅/中；0.618 深；>0.786 结构破坏。
    当前价高于 swing_high 时返回 0.0（未回踩）。

    Raises:
        ValueError: swing_high ≤ swing_low（形态无效）。
    """
    if swing_high <= swing_low:
        raise ValueError(f"swing_high({swing_high}) 必须大于 swing_low({swing_low})")
    return max(0.0, (swing_high - current_price) / (swing_high - swing_low))


def classify_volume_pattern(volume_ratios: list[float]) -> str:
    """量能衰减模式分类（输入：最近 N 日成交量/50日均量 比率序列，时间升序）。

    - SHRINKING：逐日递减且最新 ≤0.50（健康缩量，35-50% 区间达标）
    - EXPANDING：最新 >1.00 或逐日递增（回踩放量=机构派发）
    - MIXED：其余（部分日放量但不破支撑）
    """
    if not volume_ratios:
        return VOLUME_MIXED
    latest = volume_ratios[-1]
    if latest > VOLUME_EXPAND_MIN:
        return VOLUME_EXPANDING
    if len(volume_ratios) >= 2:
        decreasing = all(volume_ratios[i] < volume_ratios[i - 1] for i in range(1, len(volume_ratios)))
        increasing = all(volume_ratios[i] > volume_ratios[i - 1] for i in range(1, len(volume_ratios)))
        if decreasing and latest <= VOLUME_SHRINK_MAX:
            return VOLUME_SHRINKING
        if increasing:
            return VOLUME_EXPANDING
    elif latest <= VOLUME_SHRINK_MAX:
        # 单日数据量不足判序列，仅满足缩量阈值 → 按混合处理（保守）
        return VOLUME_MIXED
    return VOLUME_MIXED


def grade_pullback(
    fib_ratio: float,
    volume_pattern: str,
    sector_strength: float,
    pullback_days: int,
    *,
    rotation_warning: bool = False,
) -> str | None:
    """回踩质量 A/B/C 定级（三维取最弱档，时间窗外不评级）。

    Args:
        fib_ratio: Fib 回撤比例（fib_retrace_ratio 输出）。
        volume_pattern: classify_volume_pattern 输出。
        sector_strength: §3.1① 板块强度分 0-100。
        pullback_days: 回踩已持续交易日数。
        rotation_warning: §3.1① warn_rotation 预警（触发即 C 档强度）。

    Returns:
        "A"/"B"/"C"；时间窗 <2 或 >15 交易日返回 None（不评级）。
    """
    if pullback_days < PULLBACK_MIN_DAYS or pullback_days > PULLBACK_STALE_DAYS:
        return None

    # 维度 1：Fib 回撤位
    if fib_ratio <= FIB_SHALLOW_MAX:
        fib_grade = "A"
    elif fib_ratio <= FIB_DEEP_MAX:
        fib_grade = "B"
    else:
        fib_grade = "C"

    # 维度 2：量能衰减
    vol_grade = {VOLUME_SHRINKING: "A", VOLUME_EXPANDING: "C"}.get(volume_pattern, "B")

    # 维度 3：板块强度 / 轮动预警
    if rotation_warning or sector_strength < STRENGTH_MEDIUM:
        strength_grade = "C"
    elif sector_strength >= STRENGTH_STRONG:
        strength_grade = "A"
    else:
        strength_grade = "B"

    worst = max(_GRADE_ORDER[fib_grade], _GRADE_ORDER[vol_grade], _GRADE_ORDER[strength_grade])
    return _ORDER_GRADE[worst]


def pullback_action(grade: str | None) -> str:
    """等级 → BM-BUY-04 买入优先级动作；None（不评级）按观望处理。"""
    if grade is None:
        return PULLBACK_ACTIONS["C"]
    return PULLBACK_ACTIONS[grade]
