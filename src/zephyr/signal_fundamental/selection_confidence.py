# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.5/§3.6
# [MODULE] zephyr.signal_fundamental.selection_confidence
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS] (待 G08/G09/G10 sleeve SelectionResult 接线)
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] confidence ∈ [0,1]；事件阈值 ∈ (0,1]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知事件类型→回退默认阈值；阈值表非法→validate 返回问题清单
# [TESTS] tests/signal_fundamental/test_selection_confidence.py
# [TTL] permanent
#
# [ALGO_FLOW]
# 层: 输入
# - id: I1  打板=情绪周期阶段置信度+融合评分 / 多因子=因子 IC 集 / 事件=LLM 置信度+事件日反应
# 层: 算法
# - id: A1  compute_daban_confidence：路径② 阶段置信度×信号强度（memo §3.5 v1.0.1）
# - id: A2  compute_multifactor_confidence：路径① surrogate variance 代理（收缩：IC 均值×离散度折扣）
# - id: A3  compute_event_confidence：路径②+④ LLM gate × PEAD Inversion gate（|reaction|>3% → ×0.1）
# - id: A4  事件过滤阈值表 + validate_event_confidence_thresholds（配置级，G10 校准）
# 层: 输出
# - id: O1  sleeve 自评置信度 ∈[0,1]（喂 firm 层 PerformanceScore）+ 事件过滤判定
# [/ALGO_FLOW]
"""SelectionResult.confidence sleeve 差异化算法 + 事件过滤阈值（21 号 memo §3.5/§3.6）。

只做函数级 confidence 计算器——SelectionResult 统一接口是大型项（G08/G09/G10），不在本模块。

sleeve 差异化选型（memo §3.5 四候选汇总）：
- 打板 sleeve：路径② 情绪周期阶段 confidence（phase_confidence × 融合信号强度）
- 多因子 sleeve：路径① surrogate variance——**收缩登记**：surrogate 模型未建，
  以"因子 IC 均值 × (1-离散度折扣)"代理（因子共识越强越集中 → confidence 越高）；
  待 G09 接入真 surrogate 后替换，签名不变
- 事件 sleeve：路径②+④ 双重门控——LLM 事件标签 confidence gate（防误读）
  × PEAD Inversion gate（|reaction|>3% 极端反应 confidence 衰减至 0.1，防追涨）

事件过滤阈值（memo §3.6 v1.0.1）：初拟 0.7，按事件类型差异化，**待 G10 校准**。
"""

from __future__ import annotations

import math

# ------------------------------------------------------------------
# 事件 sleeve 过滤置信度阈值（配置级，memo §3.6 待裁定-6）
# ------------------------------------------------------------------
EVENT_CONFIDENCE_FILTER_THRESHOLD = 0.7  # 默认阈值（memo 初拟）

# 按事件类型差异化初拟（误读成本不同：并购 > 业绩 > 突发 > 政策）——**待 G10 校准**
EVENT_TYPE_CONFIDENCE_THRESHOLDS: dict[str, float] = {
    "earnings": 0.70,  # 业绩
    "ma": 0.75,  # 并购（误读成本最高，"否认收购"误读为利好是主要亏损源）
    "policy": 0.65,  # 政策（官方文本误读率低）
    "breaking": 0.70,  # 突发
}

# PEAD Inversion gate（memo §3.5 v1.1.0 第四候选）
PEAD_EXTREME_REACTION_THRESHOLD = 0.03  # 事件日 |reaction|>3% 为极端反应
PEAD_EXTREME_CONFIDENCE_DECAY = 0.1  # 极端反应 confidence 衰减系数

# 多因子 confidence 代理参数（路径① 收缩代理，G09 校准）
_MF_IC_FULL_CONFIDENCE = 0.05  # 因子均值 RankIC ≥0.05 → 满分置信
_MF_DISPERSION_MAX_PENALTY = 0.5  # 离散度最大折扣 50%


def validate_event_confidence_thresholds(
    thresholds: dict[str, float] | None = None,
) -> list[str]:
    """校验事件阈值表合法性。返回问题清单（空=通过）。

    规则：每值 ∈ (0,1]；键非空字符串；默认阈值常量 ∈ (0,1]。
    """
    table = EVENT_TYPE_CONFIDENCE_THRESHOLDS if thresholds is None else thresholds
    problems: list[str] = []
    if not (0.0 < EVENT_CONFIDENCE_FILTER_THRESHOLD <= 1.0):
        problems.append(f"默认阈值越界: {EVENT_CONFIDENCE_FILTER_THRESHOLD}")
    if not table:
        problems.append("阈值表为空")
    for key, value in table.items():
        if not isinstance(key, str) or not key:
            problems.append(f"非法事件类型键: {key!r}")
        if not (0.0 < value <= 1.0):
            problems.append(f"阈值越界 [{key}]={value}（须 ∈(0,1]）")
    return problems


def event_passes_confidence_filter(
    event_type: str,
    llm_confidence: float,
    *,
    thresholds: dict[str, float] | None = None,
) -> bool:
    """漏斗②过滤：LLM 事件标签 confidence 低于阈值 → 过滤（False=过滤掉）。

    未知事件类型回退默认阈值（保守：宁严勿宽由 G10 校准修正）。
    """
    table = EVENT_TYPE_CONFIDENCE_THRESHOLDS if thresholds is None else thresholds
    threshold = table.get(event_type, EVENT_CONFIDENCE_FILTER_THRESHOLD)
    return llm_confidence >= threshold


def compute_event_confidence(
    llm_confidence: float,
    event_day_reaction: float,
) -> float:
    """事件 sleeve confidence = LLM gate × PEAD Inversion gate（memo §3.5 v1.1.0）。

    |reaction|≤3% → confidence = llm_confidence（温和反应，PEAD 延续有效）；
    |reaction|>3% → confidence = llm_confidence × 0.1（极端反应，20 日中位反转）。
    """
    base = max(0.0, min(1.0, llm_confidence))
    if abs(event_day_reaction) <= PEAD_EXTREME_REACTION_THRESHOLD:
        return base
    return base * PEAD_EXTREME_CONFIDENCE_DECAY


def compute_daban_confidence(
    phase_confidence: float,
    signal_strength: float = 1.0,
) -> float:
    """打板 sleeve confidence（路径② 情绪周期阶段 confidence × 信号强度）。

    phase_confidence：情绪周期定位器阶段置信度（BM-SEL-23-B，∈[0,1]）；
    signal_strength：双引擎融合信号强度（∈[0,1]，默认 1.0=不折扣）。
    """
    pc = max(0.0, min(1.0, phase_confidence))
    ss = max(0.0, min(1.0, signal_strength))
    return pc * ss


def compute_multifactor_confidence(
    factor_ics: list[float],
    *,
    min_factors: int = 3,
) -> float:
    """多因子 sleeve confidence（路径① surrogate variance **代理**，收缩实现）。

    真 surrogate 模型（AlphaSchema 路线）未建——以因子 IC 共识代理：
    confidence = clip(mean_ic / 0.05, 0, 1) × (1 - 离散度折扣)。
    因子数 < min_factors → 0.0（共识不足不自评）；空序列 → 0.0。
    待 G09 接入真 surrogate 后替换实现（签名不变）。
    """
    n = len(factor_ics)
    if n < min_factors:
        return 0.0
    mean_ic = sum(factor_ics) / n
    var = sum((v - mean_ic) ** 2 for v in factor_ics) / n
    std = math.sqrt(var)
    strength = max(0.0, min(1.0, mean_ic / _MF_IC_FULL_CONFIDENCE))
    # 相对离散度（std/|mean|）越大共识越弱；mean≈0 时离散度惩罚拉满
    rel_dispersion = 1.0 if abs(mean_ic) < 1e-9 else min(1.0, std / abs(mean_ic))
    return strength * (1.0 - _MF_DISPERSION_MAX_PENALTY * rel_dispersion)
