# [BLUEPRINT] MOD-FBL-004 | docs/03_modules/_domain_feedback_loop/meta_harness_optimizer/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FBL-004 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.feedback_loop.test_meta_harness_optimizer
# [TESTS] src/zephyr/feedback_loop/meta_harness_optimizer.py
"""MOD-FBL-004 单元测试：meta_harness_optimizer Meta-Harness 元优化器。

蓝图验收（B12-03617/CAND-FBL-006，B12）：
学习超参词表白名单（变异率/匹配阈值/审核策略）A/B 实验台（两组配置→注入
evaluator→显著性判定）+ 优胜配置保留 + 递归护栏（策略参数不动硬约束+深度上限）。
evaluator/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.feedback_loop.meta_harness_optimizer",
    reason="meta_harness_optimizer not importable",
)

from zephyr.feedback_loop.meta_harness_optimizer import (  # noqa: E402
    ABExperimentResult,
    ArmWinner,
    LearningConfig,
    MetaHarnessError,
    MetaHarnessOptimizer,
    ReviewPolicy,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)

_BASE = LearningConfig(
    mutation_rate=0.1, match_threshold=0.5, review_policy=ReviewPolicy.STANDARD
)
_BETTER = LearningConfig(
    mutation_rate=0.2, match_threshold=0.6, review_policy=ReviewPolicy.STRICT
)


def _score_by_mutation(config: LearningConfig) -> float:
    """确定性 evaluator（内存替身）：mutation_rate×100 为得分。"""
    return config.mutation_rate * 100.0


def _optimizer(
    evaluator=_score_by_mutation, **kw
) -> MetaHarnessOptimizer:
    kw.setdefault("initial_config", _BASE)
    kw.setdefault("clock", lambda: _T0)
    return MetaHarnessOptimizer(evaluator=evaluator, **kw)


# ──────────────────────────────────────────────────────────────────────────────
# LearningConfig 白名单校验（词表闭合 + 取值域）
# ──────────────────────────────────────────────────────────────────────────────


class TestLearningConfig:
    def test_valid_config_ok(self) -> None:
        cfg = LearningConfig(
            mutation_rate=0.3,
            match_threshold=0.85,
            review_policy=ReviewPolicy.LENIENT,
        )
        assert cfg.mutation_rate == 0.3
        assert cfg.review_policy is ReviewPolicy.LENIENT

    def test_mutation_rate_out_of_range_rejected(self) -> None:
        for bad in (0.0, -0.1, 1.01, float("nan"), float("inf"), "0.1", True):
            with pytest.raises(MetaHarnessError):
                LearningConfig(
                    mutation_rate=bad,
                    match_threshold=0.5,
                    review_policy=ReviewPolicy.STANDARD,
                )

    def test_match_threshold_out_of_range_rejected(self) -> None:
        for bad in (-0.01, 1.01, float("nan"), "0.5", False):
            with pytest.raises(MetaHarnessError):
                LearningConfig(
                    mutation_rate=0.1,
                    match_threshold=bad,
                    review_policy=ReviewPolicy.STANDARD,
                )

    def test_review_policy_out_of_vocab_rejected(self) -> None:
        for bad in ("strict", "whatever", 0, None):
            with pytest.raises(MetaHarnessError):
                LearningConfig(
                    mutation_rate=0.1,
                    match_threshold=0.5,
                    review_policy=bad,
                )


# ──────────────────────────────────────────────────────────────────────────────
# 构造（注入校验）
# ──────────────────────────────────────────────────────────────────────────────


class TestConstructor:
    def test_evaluator_not_injected_fail_closed(self) -> None:
        with pytest.raises(MetaHarnessError):
            MetaHarnessOptimizer(
                initial_config=_BASE, evaluator=None, clock=lambda: _T0
            )

    def test_initial_config_not_learning_config_rejected(self) -> None:
        with pytest.raises(MetaHarnessError):
            MetaHarnessOptimizer(
                initial_config={"mutation_rate": 0.1},  # 策略参数载体禁入
                evaluator=_score_by_mutation,
                clock=lambda: _T0,
            )

    def test_invalid_margin_rejected(self) -> None:
        for bad in (-0.1, float("nan"), "0.01", True):
            with pytest.raises(MetaHarnessError):
                _optimizer(significance_margin=bad)

    def test_invalid_max_depth_rejected(self) -> None:
        for bad in (-1, 0.5, "1", True):
            with pytest.raises(MetaHarnessError):
                _optimizer(max_depth=bad)

    def test_current_config_initial(self) -> None:
        opt = _optimizer()
        assert opt.current_config is _BASE
        assert opt.max_depth == 1
        assert opt.history() == ()


# ──────────────────────────────────────────────────────────────────────────────
# A/B 实验台（显著性判定 + 优胜保留）
# ──────────────────────────────────────────────────────────────────────────────


class TestABExperiment:
    def test_a_wins_significant_retained(self) -> None:
        opt = _optimizer(significance_margin=1.0)
        result = opt.run_ab_experiment(_BETTER, _BASE)  # 20 vs 10
        assert isinstance(result, ABExperimentResult)
        assert result.experiment_id == "exp-0001"
        assert result.winner is ArmWinner.A
        assert result.significant is True
        assert result.score_a == 20.0
        assert result.score_b == 10.0
        assert result.depth == 0
        assert result.completed_at == _T0
        assert opt.current_config is _BETTER  # 优胜保留

    def test_b_wins_significant_retained(self) -> None:
        opt = _optimizer(significance_margin=1.0)
        result = opt.run_ab_experiment(_BASE, _BETTER)  # 10 vs 20
        assert result.winner is ArmWinner.B
        assert result.significant is True
        assert opt.current_config is _BETTER

    def test_tie_within_margin_keeps_current(self) -> None:
        near = LearningConfig(
            mutation_rate=0.105,
            match_threshold=0.5,
            review_policy=ReviewPolicy.STANDARD,
        )
        opt = _optimizer(significance_margin=1.0)  # 10.5 vs 10.0，Δ<1
        result = opt.run_ab_experiment(near, _BASE)
        assert result.winner is ArmWinner.TIE
        assert result.significant is False
        assert opt.current_config is _BASE  # 平局保留原配置

    def test_margin_boundary_equal_is_significant(self) -> None:
        opt = _optimizer(significance_margin=10.0)  # Δ=10 恰等 → 显著
        result = opt.run_ab_experiment(_BETTER, _BASE)
        assert result.significant is True
        assert result.winner is ArmWinner.A

    def test_exact_same_score_tie(self) -> None:
        opt = _optimizer(significance_margin=0.0)
        result = opt.run_ab_experiment(_BASE, _BASE)
        assert result.winner is ArmWinner.TIE
        assert opt.current_config is _BASE

    def test_experiment_id_deterministic_increment(self) -> None:
        opt = _optimizer()
        r1 = opt.run_ab_experiment(_BASE, _BETTER)
        r2 = opt.run_ab_experiment(_BETTER, _BASE)
        assert (r1.experiment_id, r2.experiment_id) == ("exp-0001", "exp-0002")
        assert [r.experiment_id for r in opt.history()] == ["exp-0001", "exp-0002"]

    def test_history_returns_tuple_snapshot(self) -> None:
        opt = _optimizer()
        opt.run_ab_experiment(_BASE, _BETTER)
        hist = opt.history()
        assert isinstance(hist, tuple)
        assert len(hist) == 1

    def test_determinism_same_input_same_output(self) -> None:
        def run() -> tuple:
            opt = _optimizer()
            r = opt.run_ab_experiment(_BASE, _BETTER)
            return (r.winner, r.significant, r.score_a, r.score_b,
                    opt.current_config.mutation_rate)

        assert run() == run()


# ──────────────────────────────────────────────────────────────────────────────
# 递归护栏（策略参数不动硬约束 + 深度上限）
# ──────────────────────────────────────────────────────────────────────────────


class TestRecursionGuard:
    def test_arm_not_learning_config_rejected(self) -> None:
        opt = _optimizer()
        strategy_payload = {"mutation_rate": 0.2, "position_size": 100}  # 策略参数混入
        with pytest.raises(MetaHarnessError):
            opt.run_ab_experiment(strategy_payload, _BASE)
        with pytest.raises(MetaHarnessError):
            opt.run_ab_experiment(_BASE, strategy_payload)

    def test_depth_over_max_fail_closed(self) -> None:
        opt = _optimizer(max_depth=1)
        opt.run_ab_experiment(_BASE, _BETTER, depth=1)  # 达上限仍允许
        with pytest.raises(MetaHarnessError):
            opt.run_ab_experiment(_BASE, _BETTER, depth=2)
        strict = _optimizer(max_depth=0)  # 零深度上限：仅顶层
        strict.run_ab_experiment(_BASE, _BETTER, depth=0)
        with pytest.raises(MetaHarnessError):
            strict.run_ab_experiment(_BASE, _BETTER, depth=1)

    def test_invalid_depth_rejected(self) -> None:
        opt = _optimizer()
        for bad in (-1, 0.5, "1", True):
            with pytest.raises(MetaHarnessError):
                opt.run_ab_experiment(_BASE, _BETTER, depth=bad)

    def test_recursive_evaluator_blocked_by_depth(self) -> None:
        holder: dict[str, MetaHarnessOptimizer] = {}

        def recursive_evaluator(config: LearningConfig) -> float:
            # 模拟元优化器递归调自身：depth+1 超限 → Fail-Closed 透传
            holder["opt"].run_ab_experiment(_BASE, _BETTER, depth=2)
            return 0.0

        opt = _optimizer(evaluator=recursive_evaluator, max_depth=1)
        holder["opt"] = opt
        with pytest.raises(MetaHarnessError):
            opt.run_ab_experiment(_BASE, _BETTER, depth=1)

    def test_evaluator_exception_wrapped_fail_closed(self) -> None:
        def boom(config: LearningConfig) -> float:
            raise RuntimeError("evaluator 炸了")

        opt = _optimizer(evaluator=boom)
        with pytest.raises(MetaHarnessError):
            opt.run_ab_experiment(_BASE, _BETTER)

    def test_evaluator_illegal_return_rejected(self) -> None:
        for bad in (None, "高分", float("nan"), float("inf"), True):
            opt = _optimizer(evaluator=lambda c, _bad=bad: _bad)
            with pytest.raises(MetaHarnessError):
                opt.run_ab_experiment(_BASE, _BETTER)

    def test_failed_experiment_keeps_current_unchanged(self) -> None:
        opt = _optimizer(evaluator=lambda c: float("nan"))
        with pytest.raises(MetaHarnessError):
            opt.run_ab_experiment(_BETTER, _BASE)
        assert opt.current_config is _BASE  # 失败不污染优胜配置
        assert opt.history() == ()
