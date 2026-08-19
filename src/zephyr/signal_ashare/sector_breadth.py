# [BLUEPRINT] MOD-SIG-026 supplement | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/22_sector_rotation_spec.md §3.1①
# [MODULE] zephyr.signal_ashare.sector_breadth
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS] (待 G05 选股引擎 / evaluate_strength 修正层)
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] sector_limit_up_ratio in [0,1]; sector_capital_score in [-1,1]; 纯函数无副作用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 成分股数为 0 → ratio=0.0; 成交额权重和为 0 → 退化为等权
# [TESTS] tests/signal_ashare/test_sector_breadth.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: limit_up_count(板块涨停数) + constituent_count(成分股数, sector_constituent SCD-2 当日有效清单)
# I2: constituents(成分股代码) + nature_scores(个股资金性质因子值 dict) + turnovers(个股成交额 dict)
# A1: sector_limit_up_ratio = 涨停数/成分股数(归一化宽度, 替换 evaluate_strength 涨停数维度, 40% 权重不变)
# A2: classify_limit_up_breadth(>10% 极强 / >5% 强 / <2% 弱 / 其余中) + breadth_score(0-40 映射)
# A3: aggregate_capital_nature_to_sector(成交额加权聚合个股资金性质→板块级得分+4 级标签)
# A4: capital_nature_multiplier(主力流入×1.1 / 中性×1.0 / 对倒主导×0.8 / 主力流出×0.6, 输出层乘法修正)
# O1: (ratio, breadth_label, breadth_score) + (capital_score, capital_label, multiplier)
# [/ALGO_FLOW]
"""板块宽度归一化与资金性质板块级聚合（22 号 spec §3.1① v1.8.0 补全算法）。

两项 evaluate_strength 修正层纯函数：
  1. 板块涨停比归一化——涨停绝对数不可跨板块比较（电力设备 19/200≈9.5%
     vs 油气 3/30≈10%），归一化后公平比较板块间情绪宽度，保持 40% 权重不变。
  2. aggregate_capital_nature_to_sector——25 号个股级资金性质 5 类分类
     （拉升+1/吸筹+0.5/弱托底0/对倒嫌疑-0.5/出货-1）按成交额加权上溯板块级，
     作为 evaluate_strength 输出层乘法修正因子（非新增第 4 维度）。
"""

from __future__ import annotations

# ------------------------------------------------------------------
# 常量（22 号 spec §3.1① 阈值）
# ------------------------------------------------------------------

#: 涨停比阈值：>10% 极强 / >5% 强情绪宽度 / <2% 弱
BREADTH_EXTREME_RATIO = 0.10
BREADTH_STRONG_RATIO = 0.05
BREADTH_WEAK_RATIO = 0.02

#: 个股资金性质 5 类 → 因子值（25 号 spec §647-656）
CAPITAL_NATURE_SCORES: dict[str, float] = {
    "拉升": 1.0,
    "吸筹": 0.5,
    "弱托底": 0.0,
    "对倒嫌疑": -0.5,
    "出货": -1.0,
}

#: 板块级资金性质标签阈值与强度修正乘数
CAPITAL_LABEL_MAIN_INFLOW = "主力流入"
CAPITAL_LABEL_NEUTRAL = "中性"
CAPITAL_LABEL_CHURN_DOMINANT = "对倒主导"
CAPITAL_LABEL_MAIN_OUTFLOW = "主力流出"

_CAPITAL_MULTIPLIERS: dict[str, float] = {
    CAPITAL_LABEL_MAIN_INFLOW: 1.1,
    CAPITAL_LABEL_NEUTRAL: 1.0,
    CAPITAL_LABEL_CHURN_DOMINANT: 0.8,
    CAPITAL_LABEL_MAIN_OUTFLOW: 0.6,
}


# ------------------------------------------------------------------
# 1. 板块涨停比归一化
# ------------------------------------------------------------------


def sector_limit_up_ratio(limit_up_count: int, constituent_count: int) -> float:
    """板块涨停比 = 板块涨停数 / 板块成分股数（归一化宽度指标）。

    Args:
        limit_up_count: 板块内涨停数量。
        constituent_count: 板块成分股数（sector_constituent 当日有效清单长度）。

    Returns:
        涨停比 ∈ [0, 1]；成分股数为 0 时返回 0.0（空板块无宽度可言）。
    """
    if constituent_count <= 0:
        return 0.0
    return max(0.0, min(1.0, limit_up_count / constituent_count))


def classify_limit_up_breadth(ratio: float) -> str:
    """涨停比 → 情绪宽度分档（>10% 极强 / >5% 强 / <2% 弱 / 其余中）。"""
    if ratio > BREADTH_EXTREME_RATIO:
        return "极强"
    if ratio > BREADTH_STRONG_RATIO:
        return "强"
    if ratio < BREADTH_WEAK_RATIO:
        return "弱"
    return "中"


def limit_up_breadth_score(ratio: float) -> float:
    """涨停比 → 0-40 分（替换 evaluate_strength 涨停数维度，40% 权重不变）。

    映射对齐原绝对数档位（涨停≥5→40 / ≥1→20 / else 5）的相对强度语义。
    """
    if ratio > BREADTH_EXTREME_RATIO:
        return 40.0
    if ratio > BREADTH_STRONG_RATIO:
        return 32.0
    if ratio >= BREADTH_WEAK_RATIO:
        return 20.0
    if ratio > 0.0:
        return 10.0
    return 5.0


# ------------------------------------------------------------------
# 2. 资金性质板块级聚合
# ------------------------------------------------------------------


def aggregate_capital_nature_to_sector(
    sector_constituents: list[str],
    capital_nature_scores: dict[str, float],
    turnovers: dict[str, float],
) -> tuple[float, str]:
    """将个股级资金性质聚合到板块级（成交额加权，大票权重高）。

    Args:
        sector_constituents: 板块成分股代码列表。
        capital_nature_scores: 个股资金性质因子值 dict（缺失按 0=弱托底）。
        turnovers: 个股成交额 dict（缺失按 0；权重和为 0 时退化等权）。

    Returns:
        (sector_capital_score ∈ [-1, +1], sector_capital_label)。
        空成分列表返回 (0.0, "中性")。
    """
    if not sector_constituents:
        return 0.0, CAPITAL_LABEL_NEUTRAL

    scores = [capital_nature_scores.get(s, 0.0) for s in sector_constituents]
    weights = [max(0.0, turnovers.get(s, 0.0)) for s in sector_constituents]
    total_weight = sum(weights)
    if total_weight <= 0.0:
        weights = [1.0] * len(sector_constituents)
        total_weight = float(len(sector_constituents))

    sector_capital_score = sum(s * w for s, w in zip(scores, weights, strict=True)) / total_weight
    sector_capital_score = max(-1.0, min(1.0, sector_capital_score))

    if sector_capital_score > 0.3:
        label = CAPITAL_LABEL_MAIN_INFLOW
    elif sector_capital_score > -0.1:
        label = CAPITAL_LABEL_NEUTRAL
    elif sector_capital_score > -0.5:
        label = CAPITAL_LABEL_CHURN_DOMINANT
    else:
        label = CAPITAL_LABEL_MAIN_OUTFLOW
    return sector_capital_score, label


def capital_nature_multiplier(sector_capital_label: str) -> float:
    """板块级资金性质标签 → evaluate_strength 输出层乘法修正因子。

    主力流入×1.1（资金面确认结构强度）/ 对倒主导×0.8（虚假流入风险）/
    主力流出×0.6（资金面否定结构强度）/ 中性×1.0。未知标签按中性处理。
    """
    return _CAPITAL_MULTIPLIERS.get(sector_capital_label, 1.0)
