# [MODULE] zephyr.ex_core.daban_signal_decision
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib
# [CONSUMERS] zephyr.ex_core.daban_pit_safety（PIT 回测框架主循环）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] pre_validate 门控三档(≥70放行/50-70降仓/<50否决); 冰点/反核+跌停反抽→REFLUSH_DIVE 反核路径; 主升/疯狂→BOARD 打板路径; 退潮阈值85事实禁 BOARD
# [MODIFY-GUARD] 24_daban_strategy_detail.md §3.14 缺失#8（v1.9.3）/ §3.13 缺失#3（v1.9.2）
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/ex_core/test_daban_signal_decision.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: echelon_health/height/sector_resonance/follow_count（前置质量评估四输入）
# I2: emotion_score/tech_score/phase/is_limit_down_rebound（7类决策四输入）
# F1: pre_validate_daban_signal——健康40+高度20+共振20+跟风20 百分制门控
# F2: classify_decision_v192——冰点/反核门控反核路径；否则 PHASE_THRESHOLDS 打板路径六类
# O1: {pass, score, reason} / 决策类标签（BOARD/CONTINUE/INVERSE_BOARD/REFLUSH_DIVE/WATCH/REJECT/WAIT）
# [/ALGO_FLOW]
"""打板信号前置门控 + 7 类交易动作决策（24_daban_strategy_detail §3.14#8 + §3.13#3 施工）。

缺失#8 pre_validate_daban_signal（首批实盘前必做）：§3.1 连板梯队识别
与 §3.2 情绪周期定位之间的前置质量门控——低质量梯队（孤板/断层）即使
主升期也不应打板。理论背书：arXiv:2607.27063 羊群 agent-based 模型——
无梯队跟风的孤板属"信息扩散不充分"，超调反转概率高。

缺失#3 classify_decision_v192（Phase 5）：双引擎融合 7 类决策——v1.9.2
补第 7 类 REFLUSH_DIVE + 情绪周期门控切换（主升/疯狂→打板路径，
冰点/反核→反核路径）。§3.5 第二层"标的角色→打板 sleeve 买卖动作"映射层。

PHASE_THRESHOLDS 取值说明（spec 伪代码引用未定义，按 §3.2 阶段评分区间
下界落定）：冰点 20 / 反核 40 / 主升 40 / 疯狂 65 / 退潮 85（退潮期阈值
拉满，事实禁止 BOARD——与 §3.2 退潮"≤1 成（清仓）"仓位裁定一致）。
"""

from __future__ import annotations

from typing import Final

__all__ = [
    "PHASE_THRESHOLDS",
    "pre_validate_daban_signal",
    "classify_decision_v192",
]

#: 情绪周期阶段→BOARD 决策游资分阈值（§3.2 阶段评分区间下界；退潮拉满事实禁板）
PHASE_THRESHOLDS: Final = {"冰点": 20, "反核": 40, "主升": 40, "疯狂": 65, "退潮": 85}


def pre_validate_daban_signal(
    echelon_health: str, echelon_height: int, sector_resonance: float, follow_count: int
) -> dict:
    """打板信号前置质量评估（v1.9.3 补，梯队质量→yes/no门控），在 §3.2 情绪周期定位器之前调用。

    理论背书：arXiv:2607.27063 羊群 agent-based 模型——信息扩散+社会强化分离机制下，
    无梯队跟风的孤板属于"信息扩散不充分"，超调反转概率高。
    """
    score = 0
    reasons = []
    health_scores = {"PERFECT": 40, "FRACTURE": 15, "LONE_DRAGON": 5, "COLLAPSE": 0}  # 梯队健康度权重 40
    score += health_scores.get(echelon_health, 0)
    if echelon_health in ("LONE_DRAGON", "COLLAPSE"):
        reasons.append(f"梯队{echelon_health}→质量极低")
    # 连板高度权重 20（2板最优，>5板风险递增）
    if echelon_height == 2:
        score += 20
    elif echelon_height == 1:
        score += 10
    elif 3 <= echelon_height <= 4:
        score += 15
    else:
        score += 5
        reasons.append(f"{echelon_height}板高度风险")
    score += int(sector_resonance * 20)  # 板块共振权重 20（板块跟风度）
    if sector_resonance < 0.3:
        reasons.append("板块共振不足→孤板风险")
    score += min(follow_count * 4, 20)  # 跟风股数量权重 20
    if follow_count < 3:
        reasons.append(f"跟风股{follow_count}只<3→梯队单薄")
    # 门控决策
    if score >= 70:
        return {"pass": True, "score": score, "reason": "梯队质量合格→进入情绪周期定位"}
    elif score >= 50:
        return {"pass": "CONDITIONAL", "score": score, "reason": f"梯队质量中等({';'.join(reasons)})→降仓50%"}
    else:
        return {"pass": False, "score": score, "reason": f"梯队质量不合格({';'.join(reasons)})→否决打板"}


def classify_decision_v192(
    emotion_score: float, tech_score: float, phase: str, is_limit_down_rebound: bool = False
) -> str:
    """双引擎融合 7 类决策（v1.9.2 补第7类 REFLUSH_DIVE + 情绪周期门控切换）。

    §3.5 INVERSE_BOARD 是"地天反包"非"反核"，§3.12 反核无显式切换逻辑，本函数补全。
    """
    if phase in ("冰点", "反核") and is_limit_down_rebound:  # 情绪周期门控：冰点/反核→反核路径
        if emotion_score >= 40 and tech_score >= 60:
            return "REFLUSH_DIVE"  # 反核入场
        return "WAIT"
    # 打板路径（主升/疯狂期，原6类不变）
    threshold = PHASE_THRESHOLDS[phase]
    if emotion_score >= threshold and tech_score >= 60:
        return "BOARD" if phase in ("主升", "疯狂") else "WATCH"
    elif emotion_score >= threshold * 0.8 and tech_score >= 70:
        return "CONTINUE"
    elif emotion_score >= 60 and tech_score >= 75:
        return "INVERSE_BOARD"
    elif emotion_score >= 40 and tech_score >= 50:
        return "WATCH"
    elif emotion_score < 20:
        return "WAIT"
    else:
        return "REJECT"
