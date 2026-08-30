# [BLUEPRINT] MOD-RPT-038 | 待统筹登记（54号 BM-REC-03-D 元级迭代：归因反哺生命周期治理，评审建议编排）
# [MODULE] zephyr.reporting.attribution_meta_iteration
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.governance.lifecycle_governance.msprt_promotion_channel(A10 mSPRT 晋升通道，仅消费不改); zephyr.shared.contracts.performance_attribution_report(CTR-P1-009)
# [CONSUMERS] 调用方(盘后/周度元级迭代评审调度，battle_map_11 BM-REC-03-D); 人工评审裁定方(建议唯一消费出口)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 评审制铁律=只产评审建议永不自动改策略/因子状态(requires_human_decision恒True，对齐55号§3.5评审制); 通道预注册纪律直通(SR 26-02，注册/投喂非法由 PromotionChannelError fail-loud 不包装); 每期 delta 只投喂一次(序贯实验语义，重复投喂同窗口污染 e-process，调度幂等由调用方保证); 纯编排零IO零DB(归因数据由调用方注入，本模块不查库); 非法输入 fail-closed(ValueError)
# [MODIFY-GUARD] 54_reconciliation_attribution.md §3.1/§5.1 + battle_map_11_reconciliation BM-REC-03-D
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ValueError(输入非法 fail-closed); PromotionChannelError(通道契约原样上抛)
# [TESTS] tests/reporting/test_attribution_meta_iteration.py
# [A_module] module_id=MOD-RPT-038 | layer=module | stability=evolving | safety=L | ai_autonomy=human_gated
# [TTL] permanent
"""
D_REPORTING — 归因反哺元级迭代评审建议编排（54 号 BM-REC-03-D 元级迭代，A9 残余清偿）。

环节语义（battle_map_11 BM-REC-03-D 元级迭代与二阶优化 + 54 号 §3.1 闭环反馈）：
归因结果（MOD-RPT-036 计算的 Brinson 超额来源分解 / MOD-RPT-037 落库查询）
反哺生命周期治理——某策略归因持续负贡献（相对基准逐期超额收益为负）→ 经
A10 mSPRT 晋升通道（PromotionChannelManager，61 号 §3.3 纪律 1）序贯检验：
  - 通道终局 ELIMINATED（持续负贡献证据显著）→ 降级评审建议（DEMOTE_REVIEW）
  - 通道终局 PROMOTED（持续正超额证据显著）→ 晋升评审建议（PROMOTE_REVIEW）
  - 留观（PENDING/OBSERVING，证据不足默认保留现状）→ 无建议（NONE）

champion/challenger 取向：champion=基准（benchmark），challenger=策略；
逐期 delta = 策略该期超额收益（CTR-P1-009 total_return = 几何超额 −
transaction_cost_drag，MOD-RPT-036 守恒口径）。

评审制铁律（human_gated）：本模块只产出 MetaIterationRecommendation 建议，
永不自动改策略/因子状态——落地执行（30 号 budget 调整 / 55 号 §3.5 退役评审 /
61 号晋升载体切换）由人工裁定后经各自通道执行，不在本模块职责。

降级路径（环节⑥：元级迭代失效→保持现有优化策略，仅一阶反馈）：通道终局前
一律 NONE（不动现状）；样本不足由内核满窗最小样本门（window_size）兜底。

数据投喂纪律：每期归因 delta 只应投喂一次（序贯实验语义）——调度侧按
"上期评审以来新增期数"切片投喂，重复投喂同一窗口会污染 e-process（
重复累积证据），本模块不做窗口去重。

依据: 54_reconciliation_attribution §3.1/§5.1 + battle_map_11 BM-REC-03-D + 61 号 §3.3
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: strategy_id 参数
#   fields: 参数 strategy_id，类型注解 str
#   code: attribution_meta_iteration.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: benchmark_id 参数
#   fields: 参数 benchmark_id，类型注解 str
#   code: attribution_meta_iteration.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: reports 参数
#   fields: 参数 reports，类型注解 Sequence[PerformanceAttributionReport]
#   code: attribution_meta_iteration.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① window_from_reports
#   name_en: window_from_reports
#   intro: 从 CTR-P1-009 归因报告序列构建窗口（MOD-RPT-036/037 产物的消费桥）。
#   desc: 从 CTR-P1-009 归因报告序列构建窗口（MOD-RPT-036/037 产物的消费桥）。 delta = report.total_return（几何超额 − trans…；源码 L206-L237
#   inputs: strategy_id benchmark_id reports
#   outputs: StrategyAttributionWindow
# - id: A2
#   name_zh: ② AttributionMetaIterationEngine
#   name_en: AttributionMetaIterationEngine
#   intro: 归因反哺元级迭代评审建议引擎（BM-REC-03-D；只产建议，human_gated）。
#   desc: 归因反哺元级迭代评审建议引擎（BM-REC-03-D；只产建议，human_gated）。 用法：调度方按策略逐期归因结果构建窗口（window_from_reports 或手工…；公共方法（定义序）: channel…
#   inputs: channel_manager
#   outputs: 返回值
#   （注：A2 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: StrategyAttributionWindow
#   name_en: StrategyAttributionWindow
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 调用方(盘后/周度元级迭代评审调度，battle_map_11 BM-REC-03-D); 人工评审裁定方(建议唯一消费出口)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Final, Sequence

from zephyr.governance.lifecycle_governance.msprt_promotion_channel import (
    PromotionChannelManager,
    PromotionState,
)
from zephyr.shared.contracts.performance_attribution_report import (
    PerformanceAttributionReport,
)

_logger = logging.getLogger(__name__)

__all__: Final = [
    "AttributionMetaIterationEngine",
    "MetaIterationRecommendation",
    "MetaReviewAction",
    "StrategyAttributionWindow",
    "window_from_reports",
]

#: Brinson 三效应名称（dominant_negative_effect 取值域）
_EFFECT_NAMES: Final = ("allocation", "selection", "interaction")


class MetaReviewAction(str, Enum):
    """元级迭代评审建议三态（human_gated，终局才产建议）。"""

    PROMOTE_REVIEW = "PROMOTE_REVIEW"  # 晋升评审建议（mSPRT PROMOTED 终局）
    DEMOTE_REVIEW = "DEMOTE_REVIEW"  # 降级评审建议（mSPRT ELIMINATED 终局，持续负贡献）
    NONE = "NONE"  # 无建议（留观/样本不足，保持现状仅一阶反馈）


@dataclass(frozen=True)
class StrategyAttributionWindow:
    """单策略归因窗口输入（参数对象；逐期序列等长，按时间升序）。

    period_active_returns: 逐期超额收益序列（= mSPRT delta 序列，
        CTR-P1-009 total_return 口径：几何超额 − transaction_cost_drag）。
    period_allocation/selection/interaction_effects: 逐期 Brinson 三效应
        （证据分解用——告诉评审人负贡献来自配置/选股/交互哪一层）。
    """

    strategy_id: str
    benchmark_id: str
    period_active_returns: tuple[float, ...]
    period_allocation_effects: tuple[float, ...]
    period_selection_effects: tuple[float, ...]
    period_interaction_effects: tuple[float, ...]


@dataclass(frozen=True)
class MetaIterationRecommendation:
    """元级迭代评审建议输出（不可变；human_gated 铁律载体）。

    requires_human_decision 恒 True——建议永不自动执行（55 号 §3.5 评审制）。
    channel_state/n/m_value 为 mSPRT 终局或当前快照（审计追溯用）。
    negative_period_share/cumulative_* 为窗口归因证据分解。
    """

    strategy_id: str
    benchmark_id: str
    action: MetaReviewAction
    channel_state: PromotionState
    n: int
    m_value: float
    negative_period_share: float
    cumulative_active_return: float
    cumulative_allocation_effect: float
    cumulative_selection_effect: float
    cumulative_interaction_effect: float
    dominant_negative_effect: str | None
    reason: str
    requires_human_decision: bool = True


def _validate_non_empty_id(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} 非法（须非空字符串）: {value!r}")
    return value.strip()


def _validate_window(window: StrategyAttributionWindow) -> StrategyAttributionWindow:
    """窗口 fail-closed 校验：ID 非空 / 四序列等长非空 / 数值全有限。"""
    _validate_non_empty_id(window.strategy_id, "strategy_id")
    _validate_non_empty_id(window.benchmark_id, "benchmark_id")
    n = len(window.period_active_returns)
    lengths = {
        "period_active_returns": n,
        "period_allocation_effects": len(window.period_allocation_effects),
        "period_selection_effects": len(window.period_selection_effects),
        "period_interaction_effects": len(window.period_interaction_effects),
    }
    if n == 0:
        raise ValueError("period_active_returns 不能为空（窗口至少一期）")
    if len(set(lengths.values())) != 1:
        raise ValueError(f"四序列长度不一致: {lengths}")
    for field, seq in (
        ("period_active_returns", window.period_active_returns),
        ("period_allocation_effects", window.period_allocation_effects),
        ("period_selection_effects", window.period_selection_effects),
        ("period_interaction_effects", window.period_interaction_effects),
    ):
        for v in seq:
            if not isinstance(v, (int, float)) or isinstance(v, bool) or math.isnan(v) or math.isinf(v):
                raise ValueError(f"{field} 含非有限数值: {v!r}")
    return window


def window_from_reports(
    strategy_id: str,
    benchmark_id: str,
    reports: Sequence[PerformanceAttributionReport],
) -> StrategyAttributionWindow:
    """从 CTR-P1-009 归因报告序列构建窗口（MOD-RPT-036/037 产物的消费桥）。

    delta = report.total_return（几何超额 − transaction_cost_drag，守恒口径）；
    报告按时间升序传入（调用方保证，query_attribution_results 为倒序须先反转）。

    Raises:
        ValueError: reports 为空 / report.portfolio_id 与 strategy_id 不一致
            （策略层报告归属校验，fail-closed）。
    """
    v_sid = _validate_non_empty_id(strategy_id, "strategy_id")
    _validate_non_empty_id(benchmark_id, "benchmark_id")
    if not reports:
        raise ValueError("reports 不能为空（窗口至少一期归因报告）")
    for r in reports:
        if r.portfolio_id != v_sid:
            raise ValueError(
                f"报告归属与 strategy_id 不一致（策略层报告 portfolio_id 须等于策略 ID）: "
                f"report.portfolio_id={r.portfolio_id!r} strategy_id={v_sid!r}"
            )
    return StrategyAttributionWindow(
        strategy_id=v_sid,
        benchmark_id=benchmark_id.strip(),
        period_active_returns=tuple(float(r.total_return) for r in reports),
        period_allocation_effects=tuple(float(r.allocation_effect) for r in reports),
        period_selection_effects=tuple(float(r.selection_effect) for r in reports),
        period_interaction_effects=tuple(float(r.interaction_effect) for r in reports),
    )


class AttributionMetaIterationEngine:
    """归因反哺元级迭代评审建议引擎（BM-REC-03-D；只产建议，human_gated）。

    用法：调度方按策略逐期归因结果构建窗口（window_from_reports 或手工），
    每期/每批评审周期调 evaluate——引擎幂等确保 champion=基准 / challenger=
    策略的 mSPRT 通道已注册（首次评估即该监控通道的预注册文档化点），随后把
    窗口 delta 序贯投喂通道，终局裁决映射为评审建议 + Brinson 证据分解。

    注意：同一期 delta 不可重复投喂（序贯实验语义）；跨评审周期调用方须只传
    增量期窗口。
    """

    def __init__(self, *, channel_manager: PromotionChannelManager | None = None) -> None:
        """channel_manager: A10 mSPRT 通道 DI（None=内部自建默认内核参数实例）。"""
        self._channels = channel_manager if channel_manager is not None else PromotionChannelManager()

    @property
    def channel_manager(self) -> PromotionChannelManager:
        """底层 mSPRT 通道管理器（裁决快照查询入口）。"""
        return self._channels

    def ensure_channel(self, benchmark_id: str, strategy_id: str) -> None:
        """幂等预注册监控通道（champion=基准 / challenger=策略；已注册跳过）。"""
        if (benchmark_id, strategy_id) not in self._channels.pairs():
            self._channels.register(benchmark_id, strategy_id)
            _logger.info("元级迭代监控通道预注册: champion=%s challenger=%s", benchmark_id, strategy_id)

    def evaluate(self, window: StrategyAttributionWindow) -> MetaIterationRecommendation:
        """评估单策略归因窗口 → 评审建议（只产建议，零副作用到策略/因子状态）。

        流程：①窗口 fail-closed 校验 → ②幂等确保通道注册 → ③窗口 delta 序贯
        投喂（终局早停语义由通道承载）→ ④终局裁决映射建议 + Brinson 证据分解。

        Returns:
            MetaIterationRecommendation——requires_human_decision 恒 True；
            通道未达终局（PENDING/OBSERVING）→ action=NONE（保持现状）。

        Raises:
            ValueError: 窗口非法（fail-closed，非法期不投喂不污染通道）。
        """
        w = _validate_window(window)
        self.ensure_channel(w.benchmark_id, w.strategy_id)
        verdict = self._channels.feed_batch(w.benchmark_id, w.strategy_id, list(w.period_active_returns))

        n_periods = len(w.period_active_returns)
        negative_period_share = sum(1 for v in w.period_active_returns if v < 0.0) / n_periods
        cum_active = math.fsum(w.period_active_returns)
        cum_alloc = math.fsum(w.period_allocation_effects)
        cum_selec = math.fsum(w.period_selection_effects)
        cum_inter = math.fsum(w.period_interaction_effects)
        cum_effects = {"allocation": cum_alloc, "selection": cum_selec, "interaction": cum_inter}
        dominant_negative = min(cum_effects, key=lambda k: cum_effects[k])
        if cum_effects[dominant_negative] >= 0.0:
            dominant_negative = None  # 三效应累计均非负 → 无拖累层

        if verdict.state is PromotionState.PROMOTED:
            action = MetaReviewAction.PROMOTE_REVIEW
            reason = (
                f"mSPRT 终局 PROMOTED：策略相对基准持续正超额（窗口累计 {cum_active:+.4f}，"
                f"负贡献期占比 {negative_period_share:.0%}，n={verdict.n}，M={verdict.m_value:.3f}）"
                f"——建议晋升评审（人工裁定；30 号 RegimeMetaAllocator budget 上调评审入口）"
            )
        elif verdict.state is PromotionState.ELIMINATED:
            action = MetaReviewAction.DEMOTE_REVIEW
            reason = (
                f"mSPRT 终局 ELIMINATED：策略相对基准持续负贡献（窗口累计 {cum_active:+.4f}，"
                f"负贡献期占比 {negative_period_share:.0%}，主拖累层={dominant_negative}，"
                f"n={verdict.n}，M={verdict.m_value:.3f}）"
                f"——建议降级评审（人工裁定；55 号 §3.5 退役/降级评审入口）"
            )
        else:
            action = MetaReviewAction.NONE
            reason = (
                f"mSPRT 留观中（{verdict.state.value}，证据不足默认保留现状；"
                f"窗口累计 {cum_active:+.4f}，n={verdict.n}）——无建议，仅一阶反馈"
            )

        if action is not MetaReviewAction.NONE:
            _logger.warning(
                "元级迭代评审建议 %s: strategy=%s benchmark=%s n=%d M=%.3f",
                action.value,
                w.strategy_id,
                w.benchmark_id,
                verdict.n,
                verdict.m_value,
            )
        return MetaIterationRecommendation(
            strategy_id=w.strategy_id,
            benchmark_id=w.benchmark_id,
            action=action,
            channel_state=verdict.state,
            n=verdict.n,
            m_value=verdict.m_value,
            negative_period_share=negative_period_share,
            cumulative_active_return=cum_active,
            cumulative_allocation_effect=cum_alloc,
            cumulative_selection_effect=cum_selec,
            cumulative_interaction_effect=cum_inter,
            dominant_negative_effect=dominant_negative,
            reason=reason,
        )
