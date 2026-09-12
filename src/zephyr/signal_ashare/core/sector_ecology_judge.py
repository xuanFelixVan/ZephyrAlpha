# [BLUEPRINT] MOD-SIG-143 | docs/03_modules/_domain_signal/sector_ecology_judge/blueprint.md
# [MODULE] zephyr.signal_ashare.core.sector_ecology_judge
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（纯函数判定核，零 IO；主线梯队连击/成交集中度/高潮分由调用方注入——lead_streak=mainline_candidates（MOD-SIG-061 已锚定件）产出，高潮分口径=sector_rotation_state 高潮≥90（L2-04-1 已锚定件））
# [CONSUMERS] TDM-E-L2-04（板块级市场状态）；TDM-E-L3-06 环境开关（六段状态归并上游，待接线）；TDM-E-L2 板块候选池排序（生态系数，待接线）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 三态封闭枚举 MAINLINE_CLEAR/CLIMAX/CHAOS; 判定优先级 CLIMAX > MAINLINE_CLEAR > CHAOS（风险方向优先）; 主线清晰=梯队连击≥2 且 Top2 成交集中度≥30%（节点真源"1-2 个板块吸走 30%+成交额"）; 高潮=高潮分≥90（sector_rotation_state 既有文档阈值）; 阈值全部取自已锚定模块文档值非自创; 输入越界/非有限 → SectorEcologyInputError（fail-closed）; 同输入必同输出（frozen+纯函数）; 阈值 proposed 待实盘标定
# [MODIFY-GUARD] 地图节点 TDM-E-L2-04
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 状态字符串非封闭集/集中度或分数越界/非有限 → SectorEcologyInputError（fail-closed）
# [TESTS] tests/signal_ashare/sector/test_sector_ecology_judge.py
# [TTL] permanent
"""SectorEcologyJudge — 板块级市场状态三态判定（MOD-SIG-143，TDM-E-L2-04）。

节点语义（TDM-E-L2-04 algo_note 逐条对码）：
    看全市场板块分布结构定当日生态：主线清晰（1-2 个板块吸走 30%+成交额）=聚焦做；
    高潮（涨停潮遍地）=第二天大概率分歧；混沌（无主线）=降仓等待。

判定优先级（风险方向优先）：CLIMAX > MAINLINE_CLEAR > CHAOS。
输入三维：主线梯队连击 lead_streak（mainline_candidates/MOD-SIG-061 口径）、
Top2 板块成交集中度（0-1）、高潮分（0-100，sector_rotation_state 高潮≥90 口径）。

晨审定性（st-tdm-review-20260911 前批）：三态判据需阈值裁定——本件的裁定
（night-gw-2300 架构师自裁，Owner 授权"自行裁定"令）：全部阈值取自已锚定模块的
既有文档口径（lead_streak≥2=MOD-SIG-064 无主线判据的反向、集中度 30%=节点真源、
高潮 90=sector_rotation_state 既有文档阈值），零自创数字。
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

#: 主线清晰：梯队连击下限（真源=mainline_probability MOD-SIG-064 "lead_streak<2=无主线混沌"反向）
LEAD_STREAK_MIN: Final = 2
#: 主线清晰：Top2 板块成交集中度下限（节点真源"1-2 个板块吸走 30%+成交额"）
TURNOVER_CONCENTRATION_MIN: Final = 0.30
#: 高潮：高潮分下限（真源=sector_rotation_state 高潮≥90 既有文档阈值）
CLIMAX_SCORE_MIN: Final = 90.0

#: 三态封闭枚举
ECOLOGY_MAINLINE_CLEAR: Final = "MAINLINE_CLEAR"  # 主线清晰=聚焦做
ECOLOGY_CLIMAX: Final = "CLIMAX"  # 极端高潮=第二天大概率分歧
ECOLOGY_CHAOS: Final = "CHAOS"  # 混沌=降仓等待


class SectorEcologyInputError(ValueError):
    """输入非法（集中度/分数越界、连击为负）——fail-closed。"""


@dataclass(frozen=True)
class SectorEcology:
    """三态生态判定输出（frozen，JSON 可序列化经 to_dict）。"""

    ecology: str  # MAINLINE_CLEAR / CLIMAX / CHAOS
    lead_streak: int  # 主线梯队连击（回显）
    turnover_concentration: float  # Top2 成交集中度（回显）
    climax_score: float  # 高潮分（回显）
    reason: str  # 大白话判定理由

    def to_dict(self) -> dict:
        return {
            "ecology": self.ecology,
            "lead_streak": self.lead_streak,
            "turnover_concentration": self.turnover_concentration,
            "climax_score": self.climax_score,
            "reason": self.reason,
        }


def _validate_ratio(v: float, what: str) -> float:
    fv = float(v)
    if not math.isfinite(fv):
        raise SectorEcologyInputError(f"{what} 非有限: {v!r}")
    if fv < 0.0 or fv > 1.0:
        raise SectorEcologyInputError(f"{what} 越界 [0,1]: {v!r}")
    return fv


def judge_sector_ecology(
    lead_streak: int,
    turnover_concentration: float,
    climax_score: float,
) -> SectorEcology:
    """三态判定主入口（优先级 CLIMAX > MAINLINE_CLEAR > CHAOS）。

    Args:
        lead_streak: 主线梯队连击天数（≥0，MOD-SIG-061 口径）。
        turnover_concentration: Top2 板块成交额占比（0-1）。
        climax_score: 高潮分（0-100，sector_rotation_state 口径）。

    Returns:
        SectorEcology（frozen）。

    Raises:
        SectorEcologyInputError: 连击为负/集中度或分数越界/非有限。
    """
    streak = int(lead_streak)
    if streak < 0:
        raise SectorEcologyInputError(f"梯队连击为负: {lead_streak!r}")
    conc = _validate_ratio(turnover_concentration, "成交集中度")
    climax = float(climax_score)
    if not math.isfinite(climax):
        raise SectorEcologyInputError(f"高潮分非有限: {climax_score!r}")
    if climax < 0.0 or climax > 100.0:
        raise SectorEcologyInputError(f"高潮分越界 [0,100]: {climax_score!r}")

    # ① 高潮（风险方向最优先——次日分歧警示）
    if climax >= CLIMAX_SCORE_MIN:
        return SectorEcology(
            ecology=ECOLOGY_CLIMAX,
            lead_streak=streak,
            turnover_concentration=conc,
            climax_score=climax,
            reason=f"高潮分 {climax:.0f} ≥ {CLIMAX_SCORE_MIN:.0f} → 极端高潮，次日大概率分歧",
        )
    # ② 主线清晰（梯队连击 + 成交集中）
    if streak >= LEAD_STREAK_MIN and conc >= TURNOVER_CONCENTRATION_MIN:
        return SectorEcology(
            ecology=ECOLOGY_MAINLINE_CLEAR,
            lead_streak=streak,
            turnover_concentration=conc,
            climax_score=climax,
            reason=f"梯队连击 {streak} ≥ {LEAD_STREAK_MIN} 且 Top2 集中度 {conc:.0%} ≥ "
            f"{TURNOVER_CONCENTRATION_MIN:.0%} → 主线清晰，聚焦做",
        )
    # ③ 其余 → 混沌
    return SectorEcology(
        ecology=ECOLOGY_CHAOS,
        lead_streak=streak,
        turnover_concentration=conc,
        climax_score=climax,
        reason=f"无主线（连击 {streak} < {LEAD_STREAK_MIN} 或集中度 {conc:.0%} < "
        f"{TURNOVER_CONCENTRATION_MIN:.0%}）且非高潮 → 混沌，降仓等待",
    )
