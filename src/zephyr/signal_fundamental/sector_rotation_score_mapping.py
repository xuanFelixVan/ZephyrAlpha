# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.1 v1.1.16
# [MODULE] zephyr.signal_fundamental.sector_rotation_score_mapping
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.sector_rrg（只读 import RRGQuadrant，不改动）
# [CONSUMERS] (待 G06 板块轮动定型后 L2-C→sleeve SynthesizedSignal.score 接线)
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] score ∈ [0,1]；quadrant 四象限全覆盖
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非法 quadrant/quality → ValueError；quality=None → 加成 0（未评级中性）
# [TESTS] tests/signal_fundamental/test_sector_rotation_score_mapping.py
# [TTL] permanent
#
# [ALGO_FLOW]
# 层: 输入
# - id: I1  RRG 四象限（Leading/Improving/Weakening/Lagging）+ 板块强度分(0-100) + 回踩质量(A/B/C)
# 层: 算法
# - id: A1  score = clamp(QUADRANT_BASE[quadrant] + strength/100×0.2 + QUALITY_BONUS[quality], 0, 1)
# 层: 输出
# - id: O1  板块轮动综合评分 [0,1]（SynthesizedSignal.score 语义统一）
# [/ALGO_FLOW]
"""板块轮动 → SynthesizedSignal.score 映射（21 号 memo §3.1 v1.1.16，随 G06 批次落地）。

公式（memo 原文）：
    score = clamp(SECTOR_QUADRANT_BASE[quadrant] + strength_score/100 × 0.2
                  + PULLBACK_QUALITY_BONUS[quality], 0.0, 1.0)

语义：Leading 象限+高强度+优质回踩 → score 接近 1.0（强买入信号）；
Lagging 象限+低强度+差回踩 → score 接近 0.1（弱信号/回避）。
与打板 sleeve 双引擎融合 score、多因子 sleeve 因子打分 score 在 SynthesizedSignal
中统一为 [0,1] 语义。

**当前施工态**：板块轮动属 design（G06 待定型），参数（象限基准值/强度系数/回踩加成）
待 G06 回测校准后最终确定。sector_overlay_active=False 时本映射不参与选股打分
（行业偏离由 firm 层 ±10% 硬约束兜底）。

放置说明：RRG 象限枚举只读 import 自 signal_ashare.sector_rrg（22 号 G06 批次资产），
本模块只做映射公式，不改动 sector_* 任何模块。
"""
from __future__ import annotations

from zephyr.signal_ashare.sector_rrg import RRGQuadrant

# 象限基准分（memo §3.1，待 G06 回测校准）
SECTOR_QUADRANT_BASE: dict[RRGQuadrant, float] = {
    RRGQuadrant.LEADING: 0.8,  # 领先：相对强度上行+动量上行
    RRGQuadrant.IMPROVING: 0.6,  # 改善：相对强度下行+动量上行（触底回升）
    RRGQuadrant.WEAKENING: 0.3,  # 减弱：相对强度上行+动量下行（见顶回落）
    RRGQuadrant.LAGGING: 0.1,  # 滞后：相对强度下行+动量下行
}

# 回踩质量加成（memo §3.1，待 G06 回测校准）
PULLBACK_QUALITY_BONUS: dict[str, float] = {"A": 0.15, "B": 0.05, "C": -0.05}

# 强度系数：板块强度分 0-100 归一化 ×0.2，使强度在象限基准上微调（±0.1）
STRENGTH_SCORE_COEF = 0.2


def map_sector_rotation_score(
    quadrant: RRGQuadrant | str,
    strength_score: float,
    pullback_quality: str | None = None,
) -> float:
    """RRG 象限 + 板块强度 + 回踩质量 → SynthesizedSignal.score ∈ [0,1]。

    Args:
        quadrant: RRGQuadrant 枚举或其 name/value 字符串（大小写不敏感）。
        strength_score: 板块强度评分 0-100（越界 clip）。
        pullback_quality: 回踩质量 "A"/"B"/"C"；None=未评级（加成 0，中性）。

    Raises:
        ValueError: quadrant 或 pullback_quality 非法。
    """
    q = _normalize_quadrant(quadrant)
    strength = max(0.0, min(100.0, strength_score))
    bonus = 0.0
    if pullback_quality is not None:
        key = pullback_quality.upper()
        if key not in PULLBACK_QUALITY_BONUS:
            raise ValueError(f"非法回踩质量: {pullback_quality!r}（须 A/B/C 或 None）")
        bonus = PULLBACK_QUALITY_BONUS[key]
    raw = SECTOR_QUADRANT_BASE[q] + strength / 100.0 * STRENGTH_SCORE_COEF + bonus
    return max(0.0, min(1.0, raw))


def _normalize_quadrant(quadrant: RRGQuadrant | str) -> RRGQuadrant:
    if isinstance(quadrant, RRGQuadrant):
        return quadrant
    if isinstance(quadrant, str):
        key = quadrant.strip().upper()
        for q in RRGQuadrant:
            if key in (q.name, q.value):
                return q
    raise ValueError(f"非法 RRG 象限: {quadrant!r}")
