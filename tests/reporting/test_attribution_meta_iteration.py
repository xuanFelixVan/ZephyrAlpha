# [BLUEPRINT] MOD-RPT-038 | 待统筹登记（54号 BM-REC-03-D 元级迭代：归因反哺生命周期治理，评审建议编排） | §test
# [MODULE] tests.reporting.test_attribution_meta_iteration
# [DOMAIN] D_REPORTING
# [INVARIANTS] 评审制铁律（requires_human_decision 恒 True，只产建议零状态副作用）; 通道终局映射（PROMOTED→PROMOTE_REVIEW / ELIMINATED→DEMOTE_REVIEW / 留观→NONE）; 窗口非法 fail-closed(ValueError，非法期不投喂不污染通道); 通道预注册幂等; 序贯累积（跨调用 n 累加）
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError
# [TESTS] self
# [A_test] module_id: MOD-RPT-038 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""归因反哺元级迭代评审建议编排单元测试（54 号 BM-REC-03-D，A10 mSPRT 通道消费方）。

覆盖：
- 窗口校验：空 ID / 空窗口 / 四序列长度不齐 / NaN·inf·非数值 fail-closed（ValueError）；
- window_from_reports：CTR-P1-009 报告序列 → 窗口（total_return=delta + 三效应提取）/
  空报告 / portfolio_id 归属不一致拒收；
- 终局映射（注入 window_size=3 小窗通道）：持续负贡献 → DEMOTE_REVIEW(ELIMINATED)；
  持续正超额 → PROMOTE_REVIEW(PROMOTED)；窗未满留观 → NONE(OBSERVING)；
- human_gated 铁律：三态建议 requires_human_decision 恒 True；
- 证据分解：negative_period_share / 三效应累计 / dominant_negative_effect
  （最负层 / 无非负层 → None）；
- 通道注册幂等（重复 evaluate / 显式 ensure_channel 不抛）；序贯累积（两批投喂 n 累加）；
- 终局幂等：ELIMINATED 后再评估仍 DEMOTE_REVIEW 且 n 冻结不推进。
全内存，零 DB 零网络（mSPRT 通道为 A10 production 真实件，非 mock）。
"""

from __future__ import annotations

import pytest

from zephyr.governance.lifecycle_governance.msprt_promotion_channel import (
    PromotionChannelManager,
    PromotionState,
)
from zephyr.reporting.attribution_meta_iteration import (
    AttributionMetaIterationEngine,
    MetaIterationRecommendation,
    MetaReviewAction,
    StrategyAttributionWindow,
    window_from_reports,
)
from zephyr.shared.contracts.performance_attribution_report import (
    PerformanceAttributionReport,
)

_BENCHMARK = "csi300"
_STRATEGY = "strategy_alpha_v1"
_WINDOW = 3  # 测试小窗（内核满窗最小样本门直通，窗口越小越早允许终局）


def _engine() -> AttributionMetaIterationEngine:
    return AttributionMetaIterationEngine(
        channel_manager=PromotionChannelManager(window_size=_WINDOW)
    )


def _window(
    active: tuple[float, ...],
    *,
    alloc: tuple[float, ...] | None = None,
    selec: tuple[float, ...] | None = None,
    inter: tuple[float, ...] | None = None,
) -> StrategyAttributionWindow:
    n = len(active)
    return StrategyAttributionWindow(
        strategy_id=_STRATEGY,
        benchmark_id=_BENCHMARK,
        period_active_returns=active,
        period_allocation_effects=alloc if alloc is not None else (0.0,) * n,
        period_selection_effects=selec if selec is not None else (0.0,) * n,
        period_interaction_effects=inter if inter is not None else (0.0,) * n,
    )


def _report(total_return: float, *, portfolio_id: str = _STRATEGY, key: str) -> PerformanceAttributionReport:
    return PerformanceAttributionReport(
        portfolio_id=portfolio_id,
        period_start="2026-08-01",
        period_end="2026-08-01",
        total_return=total_return,
        allocation_effect=0.001,
        selection_effect=total_return - 0.002,
        interaction_effect=0.001,
        transaction_cost_drag=0.0,
        idempotency_key=key,
    )


# ---------------------------------------------------------------------------
# 窗口校验（fail-closed）
# ---------------------------------------------------------------------------


class TestWindowValidation:
    def test_empty_strategy_id_rejected(self):
        w = _window((0.01,) * _WINDOW)
        with pytest.raises(ValueError):
            _engine().evaluate(
                StrategyAttributionWindow(
                    strategy_id=" ",
                    benchmark_id=w.benchmark_id,
                    period_active_returns=w.period_active_returns,
                    period_allocation_effects=w.period_allocation_effects,
                    period_selection_effects=w.period_selection_effects,
                    period_interaction_effects=w.period_interaction_effects,
                )
            )

    def test_empty_benchmark_id_rejected(self):
        w = _window((0.01,) * _WINDOW)
        with pytest.raises(ValueError):
            _engine().evaluate(
                StrategyAttributionWindow(
                    strategy_id=w.strategy_id,
                    benchmark_id="",
                    period_active_returns=w.period_active_returns,
                    period_allocation_effects=w.period_allocation_effects,
                    period_selection_effects=w.period_selection_effects,
                    period_interaction_effects=w.period_interaction_effects,
                )
            )

    def test_empty_active_returns_rejected(self):
        with pytest.raises(ValueError):
            _engine().evaluate(_window(()))

    def test_length_mismatch_rejected(self):
        with pytest.raises(ValueError):
            _engine().evaluate(_window((0.01,) * _WINDOW, selec=(0.0,)))

    @pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
    def test_non_finite_rejected_and_channel_untainted(self, bad):
        """非法期 fail-closed 且不投喂——通道 n 保持 0（不污染 e-process）。"""
        engine = _engine()
        engine.ensure_channel(_BENCHMARK, _STRATEGY)  # 先注册，隔离"校验先于投喂"语义
        with pytest.raises(ValueError):
            engine.evaluate(_window((0.01, bad, 0.01)))
        assert engine.channel_manager.verdict(_BENCHMARK, _STRATEGY).n == 0

    def test_bool_value_rejected(self):
        with pytest.raises(ValueError):
            _engine().evaluate(_window((0.01, True, 0.01)))


# ---------------------------------------------------------------------------
# window_from_reports（CTR-P1-009 消费桥）
# ---------------------------------------------------------------------------


class TestWindowFromReports:
    def test_builds_window_from_reports(self):
        reports = [_report(0.01, key=f"k{i}") for i in range(3)]
        w = window_from_reports(_STRATEGY, _BENCHMARK, reports)
        assert w.strategy_id == _STRATEGY
        assert w.benchmark_id == _BENCHMARK
        assert w.period_active_returns == (0.01, 0.01, 0.01)
        assert w.period_allocation_effects == (0.001, 0.001, 0.001)
        assert w.period_selection_effects == tuple(0.01 - 0.002 for _ in range(3))
        assert w.period_interaction_effects == (0.001, 0.001, 0.001)

    def test_empty_reports_rejected(self):
        with pytest.raises(ValueError):
            window_from_reports(_STRATEGY, _BENCHMARK, [])

    def test_portfolio_id_mismatch_rejected(self):
        reports = [_report(0.01, portfolio_id="other_strategy", key="k0")]
        with pytest.raises(ValueError):
            window_from_reports(_STRATEGY, _BENCHMARK, reports)

    def test_empty_ids_rejected(self):
        with pytest.raises(ValueError):
            window_from_reports("", _BENCHMARK, [_report(0.01, key="k0")])
        with pytest.raises(ValueError):
            window_from_reports(_STRATEGY, " ", [_report(0.01, key="k0")])


# ---------------------------------------------------------------------------
# 终局裁决 → 评审建议映射
# ---------------------------------------------------------------------------


class TestVerdictMapping:
    def test_persistent_negative_triggers_demote_review(self):
        """持续负贡献 → mSPRT ELIMINATED → 降级评审建议。"""
        rec = _engine().evaluate(_window((-1.0,) * _WINDOW))
        assert rec.action is MetaReviewAction.DEMOTE_REVIEW
        assert rec.channel_state is PromotionState.ELIMINATED
        assert rec.n == _WINDOW
        assert rec.negative_period_share == 1.0
        assert rec.cumulative_active_return == pytest.approx(-3.0)

    def test_persistent_positive_triggers_promote_review(self):
        """持续正超额 → mSPRT PROMOTED → 晋升评审建议。"""
        rec = _engine().evaluate(_window((1.0,) * _WINDOW))
        assert rec.action is MetaReviewAction.PROMOTE_REVIEW
        assert rec.channel_state is PromotionState.PROMOTED
        assert rec.negative_period_share == 0.0
        assert rec.cumulative_active_return == pytest.approx(3.0)

    def test_observing_yields_none(self):
        """窗未满（证据不足）→ 留观 → 无建议（保持现状，仅一阶反馈）。"""
        rec = _engine().evaluate(_window((1.0,) * (_WINDOW - 1)))
        assert rec.action is MetaReviewAction.NONE
        assert rec.channel_state is PromotionState.OBSERVING
        assert rec.n == _WINDOW - 1

    def test_human_gated_invariant_all_actions(self):
        """评审制铁律：三态建议 requires_human_decision 恒 True（永不自动执行）。"""
        engine_a = _engine()
        recs = [
            engine_a.evaluate(_window((-1.0,) * _WINDOW)),  # DEMOTE_REVIEW
            _engine().evaluate(_window((1.0,) * _WINDOW)),  # PROMOTE_REVIEW
            _engine().evaluate(_window((0.01,))),  # NONE
        ]
        assert all(r.requires_human_decision is True for r in recs)
        assert all(isinstance(r, MetaIterationRecommendation) for r in recs)


# ---------------------------------------------------------------------------
# 证据分解
# ---------------------------------------------------------------------------


class TestEvidence:
    def test_dominant_negative_effect_is_most_negative(self):
        rec = _engine().evaluate(
            _window(
                (-1.0,) * _WINDOW,
                alloc=(-0.1,) * _WINDOW,
                selec=(-0.8,) * _WINDOW,  # 选股层累计最负 → 主拖累
                inter=(-0.1,) * _WINDOW,
            )
        )
        assert rec.action is MetaReviewAction.DEMOTE_REVIEW
        assert rec.dominant_negative_effect == "selection"
        assert rec.cumulative_selection_effect == pytest.approx(-2.4)
        assert rec.cumulative_allocation_effect == pytest.approx(-0.3)
        assert rec.cumulative_interaction_effect == pytest.approx(-0.3)
        assert "selection" in rec.reason

    def test_no_negative_effect_yields_none_dominant(self):
        rec = _engine().evaluate(
            _window(
                (1.0,) * _WINDOW,
                alloc=(0.1,) * _WINDOW,
                selec=(0.2,) * _WINDOW,
                inter=(0.05,) * _WINDOW,
            )
        )
        assert rec.dominant_negative_effect is None

    def test_partial_negative_share(self):
        rec = _engine().evaluate(_window((-0.01, 0.02)))  # 留观档，仅查证据
        assert rec.negative_period_share == 0.5
        assert rec.cumulative_active_return == pytest.approx(0.01)


# ---------------------------------------------------------------------------
# 通道注册幂等 / 序贯累积 / 终局幂等
# ---------------------------------------------------------------------------


class TestChannelLifecycle:
    def test_registration_idempotent_across_evaluations(self):
        engine = _engine()
        engine.evaluate(_window((0.01,)))
        rec = engine.evaluate(_window((0.01,)))  # 二次评估不抛重复注册
        assert rec.channel_state is PromotionState.OBSERVING

    def test_explicit_ensure_channel_idempotent(self):
        engine = _engine()
        engine.ensure_channel(_BENCHMARK, _STRATEGY)
        engine.ensure_channel(_BENCHMARK, _STRATEGY)  # 幂等跳过
        assert (_BENCHMARK, _STRATEGY) in engine.channel_manager.pairs()

    def test_sequential_batches_accumulate(self):
        """序贯语义：跨评审周期增量窗口投喂，n 累加、终局可跨批达成。"""
        engine = _engine()
        r1 = engine.evaluate(_window((-1.0,) * (_WINDOW - 1)))
        assert r1.action is MetaReviewAction.NONE  # 窗未满
        r2 = engine.evaluate(_window((-1.0,)))  # 增量第 3 期
        assert r2.action is MetaReviewAction.DEMOTE_REVIEW
        assert r2.n == _WINDOW

    def test_terminal_idempotent_replay(self):
        """终局幂等：ELIMINATED 后再评估仍 DEMOTE_REVIEW 且 n 冻结。"""
        engine = _engine()
        r1 = engine.evaluate(_window((-1.0,) * _WINDOW))
        r2 = engine.evaluate(_window((1.0,) * 5))  # 反向数据不翻盘
        assert r2.action is MetaReviewAction.DEMOTE_REVIEW
        assert r2.channel_state is PromotionState.ELIMINATED
        assert r2.n == r1.n == _WINDOW

    def test_default_engine_builds_internal_channel(self):
        engine = AttributionMetaIterationEngine()
        rec = engine.evaluate(_window((0.01,)))
        assert rec.action is MetaReviewAction.NONE  # 默认窗 30，1 期必留观
        assert rec.channel_state is PromotionState.OBSERVING
