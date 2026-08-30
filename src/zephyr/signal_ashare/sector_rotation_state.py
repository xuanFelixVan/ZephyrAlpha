# [BLUEPRINT] MOD-SIG-026 supplement | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/22_sector_rotation_spec.md §3.1⑨
# [MODULE] zephyr.signal_ashare.sector_rotation_state
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS] (待 G05 选股引擎 / 板块强度综合层市场级调节项 / sector_gate 水温联动)
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 5 状态枚举单值输出; watch_score ∈ {-0.10,-0.08,0.00,+0.01,+0.03}; 纯函数
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入比率超界由调用方保证; hhi 辅助函数空列表 → 0.0
# [TESTS] tests/signal_ashare/test_sector_rotation_state.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: up_ratio(上涨板块数/全板块数) + hhi_top5(头部5板块成交额份额平方和)
# I2: lead_streak(当前领涨板块连续领涨天数) + disp_signal(领涨板块放量滞涨 0/1)
# I3: fast_rotation(轮转速度 >P90 标志, rotation_speed=0.5×Σ|今日占比−昨日占比|)
# A1: 规则映射优先级: DISTRIBUTION_RISK(disp=1 且 hhi>0.25) → CONSENSUS_CLIMAX(hhi>0.30 且 up>0.70,
#     快轮动放宽 0.35) → HEALTHY_MAINLINE(streak≥3 且 hhi<0.20) → DISAGREEMENT_PULLBACK(up<0.40
#     且 hhi>0.20) → NEUTRAL_MIXED(默认)
# A2: watch_score 映射(-0.10/-0.08/+0.03/+0.01/0.00 注入板块强度综合层统一加减)
# O1: RotationState 5 选 1 + watch_score
# [/ALGO_FLOW]
"""
板块轮动状态 5 分类（22 号 spec §3.1⑨，每日盘后市场级快照）。

4 维输入规则映射 → 5 选 1 状态 + watch_score 加减分注入板块强度综合层
（全板块强度分统一加减，不进仓位分配层，与 regime 边界一致）。

与虹吸态（sector_siphon）关系：5 状态用绝对阈值判市场级大类，虹吸态用
z-score 相对阈值精判极端分化，可串联。与 regime 12 态正交：regime 是指数级
市场状态，5 状态专攻板块间分布结构。

阈值（hhi 0.20/0.25/0.30、up_ratio 0.40/0.70、streak 3）为初拟
（legulegu/rebuildingsociety 2026 依据），待 2026 实盘标定（spec §6 待裁定）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: turnovers 参数
#   fields: 参数 turnovers，类型注解 list[float]
#   code: sector_rotation_state.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: n 参数
#   fields: 参数 n，类型注解 int
#   code: sector_rotation_state.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: up_ratio 参数
#   fields: 参数 up_ratio，类型注解 float
#   code: sector_rotation_state.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: hhi_top5 参数
#   fields: 参数 hhi_top5，类型注解 float
#   code: sector_rotation_state.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① top_n_hhi
#   name_en: top_n_hhi
#   intro: 头部 N 成交额份额平方和 HHI（5 状态用 N=5；空列表/总额 ≤0 → 0.0）。
#   desc: 头部 N 成交额份额平方和 HHI（5 状态用 N=5；空列表/总额 ≤0 → 0.0）。；源码 L143-L149
#   inputs: turnovers n
#   outputs: float
# - id: A2
#   name_zh: ② classify_rotation_state
#   name_en: classify_rotation_state
#   intro: 4 维输入 → 规则映射 5 状态（优先级从高到低，命中即定）。
#   desc: 4 维输入 → 规则映射 5 状态（优先级从高到低，命中即定）。 Args: up_ratio: 上涨板块数 / 全板块数。 hhi_top5: 头部 5 板块成交额份额平方和（…；源码 L152-L179
#   inputs: up_ratio hhi_top5 lead_streak disp_signal fast_rotation
#   outputs: RotationState
# - id: A3
#   name_zh: ③ watch_score
#   name_en: watch_score
#   intro: 状态 → watch_score 加减分（CONSENSUS_CLIMAX −0.08 / DISTRIBUTION_…
#   desc: 状态 → watch_score 加减分（CONSENSUS_CLIMAX −0.08 / DISTRIBUTION_RISK −0.10 等）。；源码 L182-L184
#   inputs: state
#   outputs: float
#   （注：A3 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: (待 G05 选股引擎 / 板块强度综合层市场级调节项 / sector_gate 水温联动)
# - id: O2
#   name_zh: RotationState
#   name_en: RotationState
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: (待 G05 选股引擎 / 板块强度综合层市场级调节项 / sector_gate 水温联动)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

from enum import Enum

# ------------------------------------------------------------------
# 常量（初拟，22 号 spec §6 待实盘标定）
# ------------------------------------------------------------------

HHI_DISTRIBUTION_MIN = 0.25  # 派发风险：放量滞涨 + 集中 >0.25
HHI_CLIMAX_MIN = 0.30  # 共识高潮：高集中 >0.30（快轮动期放宽 0.35）
HHI_CLIMAX_FAST_ROTATION = 0.35
HHI_MAINLINE_MAX = 0.20  # 健康主线：未过度集中 <0.20
HHI_PULLBACK_MIN = 0.20  # 分歧回调：头部集中 >0.20

UP_RATIO_CLIMAX_MIN = 0.70  # 共识高潮：普涨 >0.70
UP_RATIO_PULLBACK_MAX = 0.40  # 分歧回调：涨跌严重分化 <0.40

LEAD_STREAK_MAINLINE = 3  # 健康主线：连续领涨 3+ 日


class RotationState(str, Enum):
    """板块轮动 5 状态"""

    CONSENSUS_CLIMAX = "CONSENSUS_CLIMAX"  # 共识高潮：多板块同时暴涨，市场亢奋
    DISAGREEMENT_PULLBACK = "DISAGREEMENT_PULLBACK"  # 分歧回调：涨跌严重分化，领涨回调
    HEALTHY_MAINLINE = "HEALTHY_MAINLINE"  # 健康主线：一条明确主线持续领涨
    DISTRIBUTION_RISK = "DISTRIBUTION_RISK"  # 派发风险：领涨高位放量滞涨（最危险）
    NEUTRAL_MIXED = "NEUTRAL_MIXED"  # 中性混沌：涨跌互现无序（默认态）


#: 状态 → watch_score（注入板块强度综合层市场级调节项）
WATCH_SCORES: dict[RotationState, float] = {
    RotationState.CONSENSUS_CLIMAX: -0.08,
    RotationState.DISAGREEMENT_PULLBACK: 0.01,
    RotationState.HEALTHY_MAINLINE: 0.03,
    RotationState.DISTRIBUTION_RISK: -0.10,
    RotationState.NEUTRAL_MIXED: 0.00,
}


def top_n_hhi(turnovers: list[float], n: int = 5) -> float:
    """头部 N 成交额份额平方和 HHI（5 状态用 N=5；空列表/总额 ≤0 → 0.0）。"""
    total = sum(turnovers)
    if total <= 0 or not turnovers:
        return 0.0
    top = sorted(turnovers, reverse=True)[:n]
    return sum((t / total) ** 2 for t in top)


def classify_rotation_state(
    up_ratio: float,
    hhi_top5: float,
    lead_streak: int,
    disp_signal: int,
    *,
    fast_rotation: bool = False,
) -> RotationState:
    """4 维输入 → 规则映射 5 状态（优先级从高到低，命中即定）。

    Args:
        up_ratio: 上涨板块数 / 全板块数。
        hhi_top5: 头部 5 板块成交额份额平方和（top_n_hhi 输出）。
        lead_streak: 当前领涨板块连续领涨天数。
        disp_signal: 领涨板块放量滞涨标志（1=成交额>5日均量×1.2 且涨幅<前日×0.5）。
        fast_rotation: 快轮动期标志（rotation_speed >P90 时 CONSENSUS_CLIMAX
            集中度阈值放宽 0.30→0.35，避免快轮动期集中度天然偏高误判）。
    """
    if disp_signal == 1 and hhi_top5 > HHI_DISTRIBUTION_MIN:
        return RotationState.DISTRIBUTION_RISK
    climax_hhi = HHI_CLIMAX_FAST_ROTATION if fast_rotation else HHI_CLIMAX_MIN
    if hhi_top5 > climax_hhi and up_ratio > UP_RATIO_CLIMAX_MIN:
        return RotationState.CONSENSUS_CLIMAX
    if lead_streak >= LEAD_STREAK_MAINLINE and hhi_top5 < HHI_MAINLINE_MAX:
        return RotationState.HEALTHY_MAINLINE
    if up_ratio < UP_RATIO_PULLBACK_MAX and hhi_top5 > HHI_PULLBACK_MIN:
        return RotationState.DISAGREEMENT_PULLBACK
    return RotationState.NEUTRAL_MIXED


def watch_score(state: RotationState) -> float:
    """状态 → watch_score 加减分（CONSENSUS_CLIMAX −0.08 / DISTRIBUTION_RISK −0.10 等）。"""
    return WATCH_SCORES[state]
