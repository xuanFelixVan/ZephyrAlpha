# [BLUEPRINT] MOD-FAC-003 | docs/03_modules/_domain_factor/gp_strategy_discovery/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FAC-003 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.research.test_gp_strategy_discovery
# [TESTS] src/zephyr/research/gp_strategy_discovery.py
"""MOD-FAC-003 单元测试：gp_strategy_discovery 遗传规划策略发现器。

蓝图验收（B10-01844/CAND-FAC-019，A1 §29.14）：
算子集词表闭合表达式树（生成/交叉/变异，随机源注入）+ 适应度注入 +
进化循环护栏 + 强制三重门禁（注入验证器，未齐 Fail-Closed）+
人工审批后方可入库（审批队列硬约束，严禁自动入库）。
随机源/适应度/门禁全注入内存替身，不触网。
"""

from __future__ import annotations

import random

import pytest

pytest.importorskip(
    "zephyr.research.gp_strategy_discovery",
    reason="gp_strategy_discovery not importable",
)

from zephyr.research.gp_strategy_discovery import (  # noqa: E402
    ExprNode,
    GpDiscoveryError,
    GpStrategyDiscovery,
    serialize,
)

_FITNESS = {
    "add(close, volume)": 0.9,
    "sub(close, open)": 0.5,
    "mul(high, low)": 0.1,
}


def _fitness(expr: str) -> float:
    return _FITNESS.get(expr, 0.3)


def _gp(seed: int = 42, **kw) -> GpStrategyDiscovery:
    kw.setdefault("rng", random.Random(seed).random)
    kw.setdefault("fitness_evaluator", _fitness)
    return GpStrategyDiscovery(**kw)


def _gated(seed: int = 42, **kw) -> GpStrategyDiscovery:
    kw.setdefault("purged_kfold_gate", lambda e: True)
    kw.setdefault("walkforward_gate", lambda e: True)
    kw.setdefault("permutation_gate", lambda e: True)
    return _gp(seed=seed, **kw)


# ──────────────────────────────────────────────────────────────────────────────
# 构造 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_missing_rng_raises(self) -> None:
        with pytest.raises(GpDiscoveryError):
            GpStrategyDiscovery(rng=None, fitness_evaluator=_fitness)

    def test_missing_fitness_raises(self) -> None:
        with pytest.raises(GpDiscoveryError):
            GpStrategyDiscovery(rng=random.Random(0).random, fitness_evaluator=None)

    def test_population_guard(self) -> None:
        with pytest.raises(GpDiscoveryError):
            _gp(population_size=1)
        with pytest.raises(GpDiscoveryError):
            _gp(population_size=101)

    def test_loop_guards(self) -> None:
        with pytest.raises(GpDiscoveryError):
            _gp(generations=0)
        with pytest.raises(GpDiscoveryError):
            _gp(generations=51)
        with pytest.raises(GpDiscoveryError):
            _gp(max_depth=1)
        with pytest.raises(GpDiscoveryError):
            _gp(max_depth=7)

    def test_rng_out_of_range_fail_closed(self) -> None:
        gp = _gp(rng=lambda: 1.5)  # 越出 [0,1)
        with pytest.raises(GpDiscoveryError):
            gp.random_tree()


# ──────────────────────────────────────────────────────────────────────────────
# 表达式树（生成/交叉/变异，随机源注入）
# ──────────────────────────────────────────────────────────────────────────────


class TestTreeOps:
    def test_random_tree_valid_and_serializable(self) -> None:
        gp = _gp(max_depth=3)
        tree = gp.random_tree()
        assert gp._is_valid(tree)
        expr = serialize(tree)
        assert expr and isinstance(expr, str)

    def test_random_tree_deterministic_same_seed(self) -> None:
        t1 = _gp(seed=7).random_tree()
        t2 = _gp(seed=7).random_tree()
        assert serialize(t1) == serialize(t2)  # 同种子必同树

    def test_random_tree_depth_guard(self) -> None:
        gp = _gp(max_depth=2)
        for _ in range(20):
            assert gp._is_valid(gp.random_tree())

    def test_serialize_format(self) -> None:
        tree = ExprNode("add", (ExprNode("var", (), "close"), ExprNode("var", (), "volume")))
        assert serialize(tree) == "add(close, volume)"

    def test_crossover_swaps_subtree(self) -> None:
        a = ExprNode("var", (), "close")
        b = ExprNode("var", (), "volume")
        gp = _gp(rng=lambda: 0.0)  # 切点恒取首个
        child = gp.crossover(a, b)
        assert serialize(child) == "volume"  # a 的根被 b 的子树替换

    def test_crossover_invalid_falls_back_to_parent(self) -> None:
        # b 的子树为 var（非常数）→ 换入 rolling 第二子树位即非法 → 回退亲本
        a = ExprNode(
            "ts_mean",
            (ExprNode("var", (), "close"), ExprNode("const", (), 5)),
        )
        b = ExprNode("var", (), "volume")
        gp = _gp(rng=lambda: 0.9)  # 切点取 a 的末节点（常数位）
        child = gp.crossover(a, b)
        assert serialize(child) == serialize(a)

    def test_mutate_changes_tree(self) -> None:
        tree = ExprNode("var", (), "close")
        gp = _gp(rng=lambda: 0.0)  # 切点=根；重生时 u<0.4 → 终端 var（词表首项 open）
        child = gp.mutate(tree)
        assert serialize(child) == "open"

    def test_mutate_deterministic(self) -> None:
        tree = ExprNode("add", (ExprNode("var", (), "close"), ExprNode("var", (), "open")))
        c1 = _gp(seed=11).mutate(tree)
        c2 = _gp(seed=11).mutate(tree)
        assert serialize(c1) == serialize(c2)


# ──────────────────────────────────────────────────────────────────────────────
# 三重门禁（未注入齐全 Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestGates:
    def test_evolve_without_gates_fail_closed(self) -> None:
        with pytest.raises(GpDiscoveryError):
            _gp().evolve()

    def test_evolve_partial_gates_fail_closed(self) -> None:
        gp = _gp(purged_kfold_gate=lambda e: True)  # 缺二重
        with pytest.raises(GpDiscoveryError):
            gp.evolve()

    def test_gate_rejection_blocks_candidate(self) -> None:
        gp = _gated(permutation_gate=lambda e: False)  # Permutation 全拒
        result = gp.evolve()
        assert result.candidates == ()
        assert any("permutation" in n for n in result.notes)

    def test_gate_exception_counts_as_reject(self) -> None:
        def boom(expr: str) -> bool:
            raise RuntimeError("验证器故障")

        gp = _gated(walkforward_gate=boom)
        result = gp.evolve()
        assert result.candidates == ()
        assert any("walkforward" in n for n in result.notes)


# ──────────────────────────────────────────────────────────────────────────────
# 进化循环 + 人工审批队列
# ──────────────────────────────────────────────────────────────────────────────


class TestEvolveAndApprove:
    def test_evolve_populates_approval_queue(self) -> None:
        gp = _gated(population_size=6, generations=2)
        result = gp.evolve()
        assert result.generations_run == 2
        assert len(result.candidates) >= 1
        assert gp.approval_queue() == result.candidates
        ids = [c.candidate_id for c in result.candidates]
        assert ids == [f"GP-{i + 1:04d}" for i in range(len(ids))]  # 顺序枚举

    def test_min_fitness_filter(self) -> None:
        gp = _gated(population_size=6, generations=1, min_fitness=999.0)
        result = gp.evolve()
        assert result.candidates == ()
        assert any("适应度不足" in n for n in result.notes)

    def test_no_auto_admission(self) -> None:
        gp = _gated(population_size=6, generations=1)
        gp.evolve()
        assert gp.admitted() == ()  # 过门禁≠入库，严禁自动入库

    def test_approve_moves_to_admitted(self) -> None:
        gp = _gated(population_size=6, generations=1)
        result = gp.evolve()
        cand = gp.approve(result.candidates[0].candidate_id)
        assert cand.candidate_id in [c.candidate_id for c in gp.admitted()]
        assert len(gp.approval_queue()) == len(result.candidates) - 1

    def test_unknown_decision_raises(self) -> None:
        gp = _gated(population_size=4, generations=1)
        gp.evolve()
        with pytest.raises(GpDiscoveryError):
            gp.approve("GP-9999")
        with pytest.raises(GpDiscoveryError):
            gp.reject("GP-9999")

    def test_reject_removes_from_queue(self) -> None:
        gp = _gated(population_size=6, generations=1)
        result = gp.evolve()
        gp.reject(result.candidates[0].candidate_id)
        assert len(gp.approval_queue()) == len(result.candidates) - 1
        assert gp.admitted() == ()

    def test_fitness_evaluator_exception_fail_closed(self) -> None:
        def boom(expr: str) -> float:
            raise RuntimeError("评估故障")

        gp = _gated(fitness_evaluator=boom)
        with pytest.raises(GpDiscoveryError):
            gp.evolve()

    def test_evolve_deterministic(self) -> None:
        def run() -> tuple:
            gp = _gated(seed=99, population_size=6, generations=2)
            r = gp.evolve()
            return tuple((c.candidate_id, c.expression, c.fitness) for c in r.candidates)

        assert run() == run()  # 同输入必同输出
