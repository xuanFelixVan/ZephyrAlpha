# [BLUEPRINT] MOD-SIG-136 | docs/03_modules/_domain_signal/sector_conduction/blueprint.md
# [MODULE] zephyr.signal_ashare.core.sector_conduction
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（纯函数核，零 IO；板块强度由调用方从 DS-059 算好注入）
# [CONSUMERS] TDM-E-L2-06-3（强度加权传导）；G05 选股引擎打分池（待接线）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 锚点系数封闭：10 分=+15%、6 分=+5%、<6 分=-10%（节点真源）；6→10 分区间线性插值(每分+2.5%)；<6 分按平段 -10%（不随深度扩大）；乘数恒 ∈[0.90,1.15]；个股 score 越界 fail-closed；板块强度越界 fail-closed；同输入必同输出；先传导后归一语义=返回调整后分值不重排名
# [MODIFY-GUARD] 地图节点 TDM-E-L2-06-3
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 板块强度 ∉[0,10] 或个股 score <0 → SectorConductionError（fail-closed）
# [TESTS] tests/signal_ashare/sector/test_sector_conduction.py
# [TTL] permanent
"""SectorConduction — 板块强度加权传导（MOD-SIG-136）。

节点语义逐条吸收（真源=TDM-E-L2-06-3 algo_note）：
强度传导系数——板块强度 10 分制映射个股加成：10 分板块=个股 score+15%，
6 分=+5%，<6 分=反而 -10%。**强板块的弱票也加分，弱板块的强票打折。**

系数模型（三锚点，6→10 线性插值每分 +2.5%，<6 平段 -10%）：
  strength=10 → ×1.15；strength=8 → ×1.10；strength=6 → ×1.05；
  strength<6  → ×0.90（平段，禁越弱越砸的深坑设计——节点口径）
应用方式：adjusted = stock_score × multiplier（乘法传导，保序不重排名）。

查重分工（蓝图 §1）：sector_attribute_rules（MOD-SIG-077）=板块攻防属性标注
（offensive/defensive 标签语义）；本件=板块强度→个股 score 的**数值传导系数**；
sector_gate.admission_gate=先 gate 后 weight 的**准入闸**（放行/拦截二元判定）。
三者正交：先过 gate，属性标注给语境，本件给数值加成。
"""

from __future__ import annotations

from dataclasses import dataclass

_STRENGTH_MAX = 10.0
_ANCHOR_FULL = 10.0  # 锚点一：10 分
_ANCHOR_MID = 6.0  # 锚点二：6 分
_BONUS_FULL = 0.15  # 10 分 → +15%
_BONUS_MID = 0.05  # 6 分 → +5%
_BONUS_WEAK = -0.10  # <6 分 → -10%（平段）
_MULT_MIN = 0.90
_MULT_MAX = 1.15


class SectorConductionError(ValueError):
    """非法输入（fail-closed）：强度/score 越界。"""


@dataclass(frozen=True)
class ConductionResult:
    """传导结果（frozen，可审计）。"""

    multiplier: float  # ∈ [0.90, 1.15]
    bonus_pct: float  # ∈ [-0.10, +0.15]
    adjusted_score: float


def strength_conduction_bonus(sector_strength: float) -> float:
    """板块强度（10 分制）→ 加成比例（三锚点模型，纯函数）。

    Args:
        sector_strength: 板块强度 ∈ [0, 10]。

    Returns:
        加成比例 ∈ [-0.10, +0.15]（6→10 线性插值；<6 平段 -0.10）。
    """
    if sector_strength != sector_strength or sector_strength < 0.0 or sector_strength > _STRENGTH_MAX:
        raise SectorConductionError(f"板块强度越界 [0,10]: {sector_strength!r}")
    if sector_strength >= _ANCHOR_FULL:
        return _BONUS_FULL
    if sector_strength >= _ANCHOR_MID:
        span = _ANCHOR_FULL - _ANCHOR_MID  # 4 分
        frac = (sector_strength - _ANCHOR_MID) / span
        return _BONUS_MID + frac * (_BONUS_FULL - _BONUS_MID)
    return _BONUS_WEAK


def apply_strength_conduction(stock_score: float, sector_strength: float) -> ConductionResult:
    """板块强度传导到个股 score（乘法加成/打折，纯函数）。

    Args:
        stock_score: 个股打分池 score ≥0（G05 多因子综合分）。
        sector_strength: 所属板块强度 ∈ [0,10]。

    Returns:
        ConductionResult：multiplier + bonus_pct + adjusted_score。
    """
    if stock_score != stock_score or stock_score < 0.0:
        raise SectorConductionError(f"个股 score 非法（NaN/负数）: {stock_score!r}")
    bonus = strength_conduction_bonus(sector_strength)
    multiplier = 1.0 + bonus
    multiplier = max(_MULT_MIN, min(_MULT_MAX, multiplier))
    return ConductionResult(
        multiplier=multiplier,
        bonus_pct=bonus,
        adjusted_score=stock_score * multiplier,
    )
