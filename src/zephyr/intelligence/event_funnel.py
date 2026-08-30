# [BLUEPRINT] MOD-INT_EVENT_FUNNEL | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md | §2.5
# [MODULE] zephyr.intelligence.event_funnel
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.event_score（MOD-INT-EVENT-SCORE 评分全族，不重复造评分）
# [CONSUMERS] 事件驱动 sleeve（event_driven_sleeve_strategy 选股收敛上游，BM-SEL-19 第四层事件侧编排，待接线——本包 strategies 装配层接线前经 TYPE_CHECKING 声明可发现性）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 无事件数据源 → skipped 直通不筛（第三层直接进第五层，降级不阻塞）；利空（score≤-0.2）仅剔除不做空（A股不能做空）；极端反应（|day0_reaction|>3%）不进入买入候选（PEAD Inversion）；kept ⊆ 候选池；kept ≤ capacity_target；排序按评分降序、同分保持输入序；单标的契约违反剔除不整批抛；纯函数无副作用
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md §2.5 + battle_map_05 BM-SEL-19 六件套
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EventFunnelError(ZA-IT-0023)——capacity_target≤0 等配置契约违反时抛；单标的 EventScoreError 契约违反剔除+记 excluded 不整批抛；数据缺失（条件PDF/传导链未就绪 None）走降级路径不抛
# [TESTS] tests/intelligence/test_event_funnel.py
# [A_module] module_id=MOD-INT_EVENT_FUNNEL | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] 26_event_driven_strategy_detail §2.5 事件信号→选股映射 / battle_map_05_stock_selection BM-SEL-19 事件驱动分布筛选
# [ALGO_FLOW]
# I1: EventFunnelCandidate（symbol + EventRecord? + EarningsFactorData? + conditional_prob_shift? + conduction_risk?）
# I2: 精筛输出 ~50 标的（BM-SEL-18 下游）+ 事件触发标的（26 号 §2.5：事件触发标的即候选，非固定池）
# F1: build_candidate_pool 候选池生成（精筛 ∪ 事件触发合并去重，精筛序优先稳定）
# F2: 事件评分批处理（compute_event_score 调度族——业绩三/双因子、其余五类单因子，契约违反剔除不整批抛）
# F3: 三重门控过滤（利空 score≤-0.2 剔除 / 极端反应 |>3%| 剔除 / 条件PDF 上涨概率下降>15% 淘汰 / 传导链风险 >0.7 剔除；|score|<0.2 噪声不动作=保留但不加权）
# F4: 排序输出（评分降序+输入序 tie-break，容量截断 ~50→~30）
# O1: EventFunnelResult(kept/excluded{symbol:reason}/scores{symbol:score}/skipped/degraded/truncated)
# [/ALGO_FLOW]
"""
MOD-INT_EVENT_FUNNEL — 事件驱动选股漏斗（BM-SEL-19 第四层事件侧编排，~50→~30）。

26 号 §2.5「事件信号→选股映射」施工化：事件源 → 事件分类（六类）+ 情绪分数 →
**事件影响评分** → 注入选股漏斗第四层。本模块承载漏斗编排（候选池生成→过滤→
排序→输出），**评分全部委托** ``zephyr.intelligence.event_score`` 全族
（``compute_event_score`` 调度：业绩类三/双因子、其余五类单因子降级链）——
不重复造评分公式（SIGNAL-ARCH 反重复裁定同源）。

四段语义（battle_map_05 BM-SEL-19 六件套 + 26 号 §2.5）：

1. **候选池生成**（``build_candidate_pool``）：精筛输出 ~50（BM-SEL-18 下游）
   ∪ 事件触发标的（「事件触发标的即候选，非固定池」），合并去重、精筛序优先。
2. **过滤**（``run_event_funnel`` 门控链）：
   - 利空剔除——``score ≤ -0.2``（A 股不能做空，利空只能剔除/回避）；
   - 极端反应剔除——``|day0_reaction| > 3%``（PEAD Inversion：不追涨不杀跌，
     均不进入买入候选）；
   - 条件 PDF 修正——``conditional_prob_shift < -0.15`` 淘汰
     （上涨概率下降 >15%，BM-SEL-13/MOD-SIG-123 输出，``None``=未就绪不判定）；
   - 传导链风险——``conduction_risk > 0.7`` 剔除
     （BM-SEL-11/MOD-SIG-042 输出，``None``=未就绪不判定）；
   - 噪声不动作——``|score| < 0.2`` 保留但评分记 0（不据此剔除也不加权）。
3. **排序**：有效评分降序，同分保持输入序（稳定排序）；score 已含
   ``decay_stage_factor × extreme_reaction_modifier`` 乘法，即 21 号 §3.6
   ``event_impact_score × decay_phase_factor`` 裁定式，不二次加衰减。
4. **输出**：容量截断 ~50→~30（``capacity_target``），
   ``EventFunnelResult(kept/excluded/scores/skipped/degraded/truncated)``。

降级链（memo 契约「没事件数据源就跳过」）：
- ``event_source_ready=False`` → ``skipped=True`` 直通不筛（第三层直接进第五层）；
- ``degraded=True`` → 仅剔除利空，极端反应/条件PDF/传导链不判定。

与既有件边界：``signal_ashare/event_driven_screener.py``（MOD-SIG-049）是 21 号
§3.6 侧 A 股域骨架（EventImpactRecord 方向/强度/年龄契约）；本模块是 26 号 §2.5
事件 sleeve 侧实现（EventRecord + compute_event_score 族契约），两者平行承载
BM-SEL-19，评分真源唯一在 event_score。

依据: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md §2.5
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: prescreened 参数
#   fields: 参数 prescreened，类型注解 Sequence[str]
#   code: event_funnel.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: events 参数
#   fields: 参数 events，类型注解 Mapping[str, EventRecord]
#   code: event_funnel.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: earnings_map 参数
#   fields: 参数 earnings_map（无注解）
#   code: event_funnel.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: prob_shift_map 参数
#   fields: 参数 prob_shift_map（无注解）
#   code: event_funnel.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① build_candidate_pool
#   name_en: build_candidate_pool
#   intro: 候选池生成（26 号 §2.5：事件触发标的即候选，非固定池）。
#   desc: 候选池生成（26 号 §2.5：事件触发标的即候选，非固定池）。 精筛输出（BM-SEL-18 下游 ~50）∪ 事件触发标的，合并去重——精筛序优先、 事件触发追加在后（稳定序…；源码 L203-L245
#   inputs: prescreened events earnings_map prob_shift_map conduction_risk_map
#   outputs: list[EventFunnelCandidate]
# - id: A2
#   name_zh: ② run_event_funnel
#   name_en: run_event_funnel
#   intro: 事件驱动分布筛选主入口（BM-SEL-19，~50→~30）。
#   desc: 事件驱动分布筛选主入口（BM-SEL-19，~50→~30）。 ``event_source_ready=False`` → skipped 直通（开通条件=事件数据源+知识图谱…；源码 L266-L329
#   inputs: candidates config event_source_ready degraded
#   outputs: EventFunnelResult
#   （注：A2 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: list[EventFunnelCandidate]
#   name_en: list[EventFunnelCandidate]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 事件驱动 sleeve（event_driven_sleeve_strategy 选股收敛上游，BM-SEL-19 第四层事件侧编排，待接线——本包 stra…
# - id: O2
#   name_zh: EventFunnelResult
#   name_en: EventFunnelResult
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 事件驱动 sleeve（event_driven_sleeve_strategy 选股收敛上游，BM-SEL-19 第四层事件侧编排，待接线——本包 stra…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Final, Mapping, Sequence

from zephyr.intelligence.event_score import (
    EXTREME_REACTION_THRESHOLD,
    SIGNAL_NOISE_THRESHOLD,
    EarningsFactorData,
    EventRecord,
    EventScoreError,
    compute_event_score,
)

try:
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # noqa: BLE001  # pragma: no cover
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_log = logging.getLogger(__name__)


class EventFunnelError(ZephyrBaseError):
    """ZA-IT-0023: 事件漏斗配置/输入契约违反（capacity_target≤0 等）。"""

    error_code = "ZA-IT-0023"


# ── BM-SEL-19 六件套③参数 + 26 号 §2.5 裁定值 ──
DEFAULT_CAPACITY_TARGET: Final[int] = 30  # 漏斗容量目标（~50→~30）
PROB_SHIFT_REJECT: Final[float] = -0.15  # 条件PDF：上涨概率下降 >15% 淘汰
CONDUCTION_RISK_MAX: Final[float] = 0.7  # 传导链风险剔除阈值（初拟，G10 校准）


@dataclass(frozen=True, slots=True)
class EventFunnelCandidate:
    """漏斗候选标的记录（精筛输出 ~50 + 事件触发标的装配）。

    event : 事件记录（``None``=无事件中性标的，保留且评分记 0）。
    earnings : 业绩类外部因子数据（一致预期/EAR/ORJ，调用方从数据层注入）。
    conditional_prob_shift : 事件驱动条件 PDF 修正后上涨概率变化
        （BM-SEL-13/MOD-SIG-123 输出；``None``=未就绪不判定）。
    conduction_risk : 传导链风险 [0,1]（BM-SEL-11/MOD-SIG-042 输出；
        ``None``=未就绪不判定）。
    """

    symbol: str
    event: EventRecord | None = None
    earnings: EarningsFactorData | None = None
    conditional_prob_shift: float | None = None
    conduction_risk: float | None = None


@dataclass(frozen=True, slots=True)
class EventFunnelConfig:
    """第四层事件漏斗参数（memo 契约值 + 初拟阈值，G10 校准）。

    capacity_target : 漏斗容量目标（~30）；通过数超容量按评分降序截断。
    prob_shift_reject : 条件 PDF 淘汰门槛（上涨概率下降超过该幅度淘汰，负值）。
    conduction_risk_max : 传导链风险剔除阈值（0-1，越高越宽容）。
    """

    capacity_target: int = DEFAULT_CAPACITY_TARGET
    prob_shift_reject: float = PROB_SHIFT_REJECT
    conduction_risk_max: float = CONDUCTION_RISK_MAX


@dataclass(frozen=True)
class EventFunnelResult:
    """事件漏斗输出（BM-SEL-19 → BM-SEL-20 多策略投票上游）。"""

    kept: tuple[str, ...]  # 保留标的（评分降序）
    excluded: dict[str, str] = field(default_factory=dict)  # {symbol: 排除原因}
    scores: dict[str, float] = field(default_factory=dict)  # {symbol: 有效评分（kept 内，噪声/无事件=0.0）}
    skipped: bool = False  # True=无事件数据源，直通不筛
    degraded: bool = False  # True=降级路径（仅剔除利空）
    truncated: bool = False  # True=超容量按评分截断


def build_candidate_pool(
    prescreened: Sequence[str],
    events: Mapping[str, EventRecord],
    *,
    earnings_map: Mapping[str, EarningsFactorData] | None = None,
    prob_shift_map: Mapping[str, float] | None = None,
    conduction_risk_map: Mapping[str, float] | None = None,
) -> list[EventFunnelCandidate]:
    """候选池生成（26 号 §2.5：事件触发标的即候选，非固定池）。

    精筛输出（BM-SEL-18 下游 ~50）∪ 事件触发标的，合并去重——精筛序优先、
    事件触发追加在后（稳定序）。``events`` 键集合外的精筛标的按无事件装配；
    仅在事件集合出现而精筛外的标的亦入池（事件触发型候选）。
    """
    pool: list[EventFunnelCandidate] = []
    seen: set[str] = set()
    for symbol in prescreened:
        if symbol in seen:
            continue
        seen.add(symbol)
        pool.append(
            EventFunnelCandidate(
                symbol=symbol,
                event=events.get(symbol),
                earnings=(earnings_map or {}).get(symbol),
                conditional_prob_shift=(prob_shift_map or {}).get(symbol),
                conduction_risk=(conduction_risk_map or {}).get(symbol),
            )
        )
    for symbol, event in events.items():
        if symbol in seen:
            continue
        seen.add(symbol)
        pool.append(
            EventFunnelCandidate(
                symbol=symbol,
                event=event,
                earnings=(earnings_map or {}).get(symbol),
                conditional_prob_shift=(prob_shift_map or {}).get(symbol),
                conduction_risk=(conduction_risk_map or {}).get(symbol),
            )
        )
    return pool


def _score_candidate(cand: EventFunnelCandidate) -> float | None:
    """单标的评分（委托 compute_event_score 族）。

    无事件 → 0.0（中性）；EventScoreError 契约违反 → ``None``（剔除信号）；
    噪声（|score|<0.2）→ 0.0（不动作=不加权，由调用方保留）。
    """
    if cand.event is None:
        return 0.0
    try:
        score = compute_event_score(cand.event, cand.earnings)
    except EventScoreError:
        _log.warning("run_event_funnel: 事件评分契约违反剔除 symbol=%s", cand.symbol)
        return None
    if abs(score) < SIGNAL_NOISE_THRESHOLD:
        return 0.0
    return score


def run_event_funnel(
    candidates: Sequence[EventFunnelCandidate],
    *,
    config: EventFunnelConfig | None = None,
    event_source_ready: bool = True,
    degraded: bool = False,
) -> EventFunnelResult:
    """事件驱动分布筛选主入口（BM-SEL-19，~50→~30）。

    ``event_source_ready=False`` → skipped 直通（开通条件=事件数据源+知识图谱
    +NLP，未就绪跳过本层）；``degraded=True`` → 仅剔除利空，极端反应/条件PDF/
    传导链不判定。
    """
    cfg = config or EventFunnelConfig()
    if cfg.capacity_target <= 0:
        raise EventFunnelError(
            "run_event_funnel: capacity_target 必须为正",
            details={"capacity_target": cfg.capacity_target},
        )
    if not event_source_ready:
        return EventFunnelResult(
            kept=tuple(c.symbol for c in candidates),
            scores={c.symbol: 0.0 for c in candidates},
            skipped=True,
        )

    kept_records: list[tuple[EventFunnelCandidate, float]] = []  # (候选, 有效评分) 保输入序
    excluded: dict[str, str] = {}
    for cand in candidates:
        score = _score_candidate(cand)
        if score is None:
            excluded[cand.symbol] = "event:score_contract"
            continue
        if score <= -SIGNAL_NOISE_THRESHOLD:
            excluded[cand.symbol] = "event:negative_score"  # 利空回避（不能做空）
            continue
        if degraded:
            kept_records.append((cand, score))
            continue
        if cand.event is not None and abs(cand.event.day0_reaction) > EXTREME_REACTION_THRESHOLD:
            excluded[cand.symbol] = "event:extreme_reaction"  # PEAD Inversion 不进入买入候选
            continue
        if cand.conditional_prob_shift is not None and cand.conditional_prob_shift < cfg.prob_shift_reject:
            excluded[cand.symbol] = "event:prob_shift_down"  # 上涨概率下降 >15% 淘汰
            continue
        if cand.conduction_risk is not None and cand.conduction_risk > cfg.conduction_risk_max:
            excluded[cand.symbol] = "event:conduction_risk"
            continue
        kept_records.append((cand, score))

    # 排序：有效评分降序 + 输入序 tie-break（sorted 稳定保证）
    kept_records = sorted(kept_records, key=lambda item: item[1], reverse=True)
    truncated = False
    if len(kept_records) > cfg.capacity_target:
        kept_records = kept_records[: cfg.capacity_target]
        truncated = True
    return EventFunnelResult(
        kept=tuple(c.symbol for c, _ in kept_records),
        excluded=excluded,
        scores={c.symbol: s for c, s in kept_records},
        skipped=False,
        degraded=degraded,
        truncated=truncated,
    )


__all__: Final = [
    "CONDUCTION_RISK_MAX",
    "DEFAULT_CAPACITY_TARGET",
    "PROB_SHIFT_REJECT",
    "EventFunnelCandidate",
    "EventFunnelConfig",
    "EventFunnelError",
    "EventFunnelResult",
    "build_candidate_pool",
    "run_event_funnel",
]
