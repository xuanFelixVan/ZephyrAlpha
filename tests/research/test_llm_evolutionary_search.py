# [BLUEPRINT] MOD-FAC-006 | docs/03_modules/_domain_factor/llm_evolutionary_search/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FAC-006 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.research.test_llm_evolutionary_search
# [TESTS] src/zephyr/research/llm_evolutionary_search.py
"""MOD-FAC-006 单元测试：llm_evolutionary_search LLM 进化式策略搜索。

蓝图验收（B10-01877/CAND-FAC-021，A1 §29.32）：
LLM 变异三角色（Exploit/Explore/Crossover 回调注入）+ 种群≤20 + 精英保留 +
多样性注入 + 仅盘后运行语义 + 三重门禁 + p-hacking 评估（注入）+
人工裁决队列，严禁全自动上线硬约束。
LLM/门禁/评估器/盘后检查全注入内存替身，不触网。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.research.llm_evolutionary_search",
    reason="llm_evolutionary_search not importable",
)

from zephyr.research.llm_evolutionary_search import (  # noqa: E402
    LlmEvolutionarySearch,
    LlmEvolutionError,
    MutationRole,
)

_FITNESS = {"seed_a": 0.9, "seed_b": 0.4}
_P_HACK = {"seed_a": 0.01, "seed_b": 0.02}


def _fitness(expr: str) -> float:
    return _FITNESS.get(expr, 0.5)


def _p_hack(expr: str) -> float:
    return _P_HACK.get(expr, 0.01)


def _search(seeds=("seed_a", "seed_b"), **kw) -> LlmEvolutionarySearch:
    kw.setdefault("exploit_llm", lambda e: f"{e}_x")
    kw.setdefault("explore_llm", lambda: f"explore_{len(_FITNESS)}")
    kw.setdefault("crossover_llm", lambda a, b: f"cx({a}|{b})")
    kw.setdefault("fitness_evaluator", _fitness)
    kw.setdefault("purged_kfold_gate", lambda e: True)
    kw.setdefault("walkforward_gate", lambda e: True)
    kw.setdefault("permutation_gate", lambda e: True)
    kw.setdefault("p_hacking_assessor", _p_hack)
    kw.setdefault("is_after_hours", lambda: True)
    kw.setdefault("population_size", 6)
    kw.setdefault("elite_n", 2)
    kw.setdefault("generations", 2)
    return LlmEvolutionarySearch(**kw), seeds


# ──────────────────────────────────────────────────────────────────────────────
# 构造 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_missing_llm_roles(self) -> None:
        base = dict(
            exploit_llm=lambda e: e,
            explore_llm=lambda: "x",
            crossover_llm=lambda a, b: a,
            fitness_evaluator=_fitness,
        )
        for key in base:
            kw = dict(base)
            kw[key] = None
            with pytest.raises(LlmEvolutionError):
                LlmEvolutionarySearch(**kw)

    def test_population_hard_cap_20(self) -> None:
        with pytest.raises(LlmEvolutionError):
            _search(population_size=21)
        with pytest.raises(LlmEvolutionError):
            _search(population_size=1)

    def test_elite_guard(self) -> None:
        with pytest.raises(LlmEvolutionError):
            _search(population_size=6, elite_n=6)  # 精英须 < 种群
        with pytest.raises(LlmEvolutionError):
            _search(population_size=6, elite_n=0)

    def test_generations_guard(self) -> None:
        with pytest.raises(LlmEvolutionError):
            _search(generations=0)

    def test_max_p_hacking_range(self) -> None:
        with pytest.raises(LlmEvolutionError):
            _search(max_p_hacking=0.0)


# ──────────────────────────────────────────────────────────────────────────────
# 盘后语义 + 门禁/p-hacking 注入检查
# ──────────────────────────────────────────────────────────────────────────────


class TestRunGuards:
    def test_after_hours_checker_missing(self) -> None:
        s, seeds = _search(is_after_hours=None)
        with pytest.raises(LlmEvolutionError):
            s.run(seeds)

    def test_intraday_run_rejected(self) -> None:
        s, seeds = _search(is_after_hours=lambda: False)
        with pytest.raises(LlmEvolutionError):
            s.run(seeds)

    def test_gates_missing_fail_closed(self) -> None:
        for gate in ("purged_kfold_gate", "walkforward_gate", "permutation_gate"):
            s, seeds = _search(**{gate: None})
            with pytest.raises(LlmEvolutionError):
                s.run(seeds)

    def test_p_hacking_assessor_missing(self) -> None:
        s, seeds = _search(p_hacking_assessor=None)
        with pytest.raises(LlmEvolutionError):
            s.run(seeds)

    def test_empty_and_blank_seeds(self) -> None:
        s, _ = _search()
        with pytest.raises(LlmEvolutionError):
            s.run([])
        with pytest.raises(LlmEvolutionError):
            s.run(["seed_a", "  "])


# ──────────────────────────────────────────────────────────────────────────────
# 进化循环（三角色 + 精英保留 + 多样性）
# ──────────────────────────────────────────────────────────────────────────────


class TestEvolution:
    def test_elite_retention_exploit_called_on_elite(self) -> None:
        calls: list[str] = []
        s, seeds = _search(exploit_llm=lambda e: calls.append(e) or f"{e}_x")
        s.run(seeds)
        assert "seed_a" in calls  # 每代精英 seed_a（fitness 0.9 最高）被保守变异

    def test_explore_diversity_injection(self) -> None:
        counter = {"n": 0}

        def explore() -> str:
            counter["n"] += 1
            return f"explore_{counter['n']}"

        s, seeds = _search(explore_llm=explore, population_size=6, elite_n=1)
        result = s.run(seeds)
        assert counter["n"] >= 2  # 每代 Explore 注入补满种群（精英1+后代2<6）
        assert result.generations_run == 2

    def test_llm_bad_output_skipped_with_note(self) -> None:
        s, seeds = _search(exploit_llm=lambda e: "")
        result = s.run(seeds)
        assert any("非法剔除" in n for n in result.notes)

    def test_dedup_diversity_note(self) -> None:
        s, seeds = _search(exploit_llm=lambda e: e)  # 保守变异原样返回 → 触发去重
        result = s.run(seeds)
        assert any("多样性去重" in n for n in result.notes)

    def test_candidate_roles_recorded(self) -> None:
        s, seeds = _search()
        result = s.run(seeds)
        roles = {c.expression: c.role for c in result.candidates}
        assert roles["seed_a"] is MutationRole.SEED  # 种子角色留痕

    def test_deterministic(self) -> None:
        def run() -> tuple:
            s, seeds = _search()
            r = s.run(seeds)
            return tuple((c.candidate_id, c.expression, c.role.value) for c in r.candidates)

        assert run() == run()  # 同输入必同输出


# ──────────────────────────────────────────────────────────────────────────────
# 三重门禁 + p-hacking + 人工裁决（严禁全自动上线）
# ──────────────────────────────────────────────────────────────────────────────


class TestGatesAndAdjudication:
    def test_gate_rejection_blocks(self) -> None:
        s, seeds = _search(permutation_gate=lambda e: False)
        result = s.run(seeds)
        assert result.candidates == ()
        assert any("permutation" in n for n in result.notes)

    def test_p_hacking_filter(self) -> None:
        s, seeds = _search(p_hacking_assessor=lambda e: 0.5, max_p_hacking=0.05)
        result = s.run(seeds)
        assert result.candidates == ()
        assert any("p-hacking" in n for n in result.notes)

    def test_no_auto_admission(self) -> None:
        s, seeds = _search()
        result = s.run(seeds)
        assert len(result.candidates) >= 1
        assert s.admitted() == ()  # 全过检也严禁自动上线

    def test_approve_moves_to_admitted(self) -> None:
        s, seeds = _search()
        result = s.run(seeds)
        cand = s.approve(result.candidates[0].candidate_id)
        assert cand.candidate_id in [c.candidate_id for c in s.admitted()]
        assert len(s.adjudication_queue()) == len(result.candidates) - 1

    def test_approve_unknown_raises(self) -> None:
        s, seeds = _search()
        s.run(seeds)
        with pytest.raises(LlmEvolutionError):
            s.approve("LE-9999")

    def test_reject_removes(self) -> None:
        s, seeds = _search()
        result = s.run(seeds)
        s.reject(result.candidates[0].candidate_id)
        assert len(s.adjudication_queue()) == len(result.candidates) - 1
        assert s.admitted() == ()

    def test_candidate_ids_sequential(self) -> None:
        s, seeds = _search()
        result = s.run(seeds)
        ids = [c.candidate_id for c in result.candidates]
        assert ids == [f"LE-{i + 1:04d}" for i in range(len(ids))]

    def test_fitness_evaluator_exception_fail_closed(self) -> None:
        def boom(expr: str) -> float:
            raise RuntimeError("评估故障")

        s, seeds = _search(fitness_evaluator=boom)
        with pytest.raises(LlmEvolutionError):
            s.run(seeds)
