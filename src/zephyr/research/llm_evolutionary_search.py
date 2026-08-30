# [BLUEPRINT] MOD-FAC-006 | docs/03_modules/_domain_factor/llm_evolutionary_search/blueprint.md
# [MODULE] zephyr.research.llm_evolutionary_search
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] 无（协议核心纯内存；LLM 三角色回调/fitness/三重门禁/p_hacking_assessor/is_after_hours 全注入）
# [CONSUMERS] 运行时装配批（盘后 LLM 进化策略搜索批 / 人工裁决后入因子库草稿治理串行合并）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] LLM 变异三角色词表闭合（exploit 保守/explore 激进/crossover 合并或从零生成，回调全注入，非法输出剔除留痕）；种群≤20 硬护栏、精英保留（elite_n<population）、Explore 每代注入多样性（表达式去重）；仅盘后运行（is_after_hours 注入检查，未注入或非盘后 run Fail-Closed）；进化输出必经三重门禁（Purged K-Fold/Walk-Forward/Permutation 注入，未齐 Fail-Closed）+ p-hacking 概率≤阈值（注入评估器）；过检仅入人工裁决队列，approve 方可入库，严禁全自动上线；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_factor/llm_evolutionary_search/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] LlmEvolutionError(占位 ZA-FAC-UNREGISTERED-LLM-EVOLUTION)——LLM 角色/评估器缺失/种群护栏越界/非盘后运行/三重门禁或 p-hacking 评估器未注入/种子非法/未知 candidate_id 裁决时抛
# [TESTS] tests/research/test_llm_evolutionary_search.py
# [A_module] module_id=MOD-FAC-006 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
LlmEvolutionarySearch — LLM 进化式策略搜索（MOD-FAC-006）。

B10-01877（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-FAC-021，A1 §29.32）：LLM
变异**三角色**（Exploit 保守 / Explore 激进 / Crossover-Genesis 合并或从零
生成，LLM 回调注入）+ 种群 ≤20 + 精英保留 + 多样性注入 + **仅盘后运行**语义
+ 进化输出必经**三重门禁** + **p-hacking 概率评估**（注入评估器）+ **人工裁
决队列，严禁全自动上线**硬约束。

查重分工（蓝图 §0）：gp_strategy_discovery=符号表达式树 GP（随机源驱动，无
LLM）；本件=LLM 三角色**语义变异**进化（LLM 回调驱动），共享"三重门禁+人工
队列"治理骨架但变异算子与驱动源正交。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: exploit_llm 参数
#   fields: 参数 exploit_llm（无注解）
#   code: llm_evolutionary_search.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: explore_llm 参数
#   fields: 参数 explore_llm（无注解）
#   code: llm_evolutionary_search.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: crossover_llm 参数
#   fields: 参数 crossover_llm（无注解）
#   code: llm_evolutionary_search.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: fitness_evaluator 参数
#   fields: 参数 fitness_evaluator（无注解）
#   code: llm_evolutionary_search.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① LlmEvolutionarySearch
#   name_en: LlmEvolutionarySearch
#   intro: LLM 进化式策略搜索器（三角色变异 + 精英保留 + 盘后语义 + 人工裁决）。
#   desc: LLM 进化式策略搜索器（三角色变异 + 精英保留 + 盘后语义 + 人工裁决）。 Args: exploit_llm: Exploit 保守变异，``elite_express…；公共方法（定义序）: run, ad…
#   inputs: exploit_llm explore_llm crossover_llm fitness_evaluator purged_kfold_…
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: LlmEvolutionarySearch
#   downstream: 运行时装配批（盘后 LLM 进化策略搜索批 / 人工裁决后入因子库草稿治理串行合并）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "MAX_POPULATION",
    "LlmCandidate",
    "LlmEvolutionError",
    "LlmEvolutionResult",
    "LlmEvolutionarySearch",
    "MutationRole",
]

#: 种群硬护栏（≤20）
MAX_POPULATION: Final = 20

_GEN_MIN, _GEN_MAX = 1, 50


class LlmEvolutionError(Exception):
    """LLM 进化搜索输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FAC-UNREGISTERED-LLM-EVOLUTION。
    """


class MutationRole(str, Enum):
    """LLM 变异角色词表（闭合）。"""

    EXPLOIT = "exploit"
    EXPLORE = "explore"
    CROSSOVER = "crossover"
    SEED = "seed"


@dataclass(frozen=True)
class LlmCandidate:
    """过门禁+p-hacking 候选（人工裁决队列条目，frozen）。"""

    candidate_id: str
    expression: str
    role: MutationRole
    fitness: float
    p_hacking: float
    generation: int


@dataclass(frozen=True)
class LlmEvolutionResult:
    """进化搜索产出（frozen）。"""

    generations_run: int
    best_fitness: float
    candidates: tuple[LlmCandidate, ...]
    notes: tuple[str, ...]


class LlmEvolutionarySearch:
    """LLM 进化式策略搜索器（三角色变异 + 精英保留 + 盘后语义 + 人工裁决）。

    Args:
        exploit_llm: Exploit 保守变异，``elite_expression -> new_expression``。
        explore_llm: Explore 激进/从零生成，``() -> new_expression``（多样性注入）。
        crossover_llm: Crossover-Genesis 合并，``(expr_a, expr_b) -> new_expression``。
        fitness_evaluator: 注入适应度评估器，``expression -> float``。
        purged_kfold_gate / walkforward_gate / permutation_gate: 三重门禁注入。
        p_hacking_assessor: 注入 p-hacking 概率评估器，``expression -> float``。
        is_after_hours: 注入盘后检查，``() -> bool``（仅盘后运行语义）。
        population_size: 种群（≤20 硬护栏）。
        elite_n: 精英保留数（< population_size）。
        generations: 进化代数护栏。
        max_p_hacking: p-hacking 概率上限（∈ (0,1]）。
    """

    def __init__(
        self,
        *,
        exploit_llm: Callable[[str], str] | None,
        explore_llm: Callable[[], str] | None,
        crossover_llm: Callable[[str, str], str] | None,
        fitness_evaluator: Callable[[str], float] | None,
        purged_kfold_gate: Callable[[str], bool] | None = None,
        walkforward_gate: Callable[[str], bool] | None = None,
        permutation_gate: Callable[[str], bool] | None = None,
        p_hacking_assessor: Callable[[str], float] | None = None,
        is_after_hours: Callable[[], bool] | None = None,
        population_size: int = 10,
        elite_n: int = 2,
        generations: int = 3,
        max_p_hacking: float = 0.05,
    ) -> None:
        for name, dep in (
            ("exploit_llm", exploit_llm),
            ("explore_llm", explore_llm),
            ("crossover_llm", crossover_llm),
            ("fitness_evaluator", fitness_evaluator),
        ):
            if dep is None:
                raise LlmEvolutionError(f"{name} 未注入（LLM 角色/适应度强制注入，Fail-Closed）")
        if (
            isinstance(population_size, bool)
            or not isinstance(population_size, int)
            or not (2 <= population_size <= MAX_POPULATION)
        ):
            raise LlmEvolutionError(f"population_size 越出硬护栏 [2,{MAX_POPULATION}]: {population_size!r}")
        if isinstance(elite_n, bool) or not isinstance(elite_n, int) or not (1 <= elite_n < population_size):
            raise LlmEvolutionError(f"elite_n 非法（须 1≤elite_n<population_size）: {elite_n!r}")
        if isinstance(generations, bool) or not (_GEN_MIN <= int(generations) <= _GEN_MAX):
            raise LlmEvolutionError(f"generations 越出护栏 [{_GEN_MIN},{_GEN_MAX}]: {generations!r}")
        if not (0.0 < float(max_p_hacking) <= 1.0):
            raise LlmEvolutionError(f"max_p_hacking 非法（须 ∈ (0,1]）: {max_p_hacking!r}")
        self._exploit = exploit_llm
        self._explore = explore_llm
        self._crossover = crossover_llm
        self._fitness = fitness_evaluator
        self._gates = {
            "purged_kfold": purged_kfold_gate,
            "walkforward": walkforward_gate,
            "permutation": permutation_gate,
        }
        self._p_hacking = p_hacking_assessor
        self._after_hours = is_after_hours
        self._pop = population_size
        self._elite_n = elite_n
        self._gens = int(generations)
        self._max_p = float(max_p_hacking)
        self._queue: dict[str, LlmCandidate] = {}
        self._admitted: dict[str, LlmCandidate] = {}
        self._counter = 0

    # ── 注入件封装 ─────────────────────────────────────────────────────────

    def _score(self, expr: str) -> float:
        try:
            v = self._fitness(expr)
        except LlmEvolutionError:
            raise
        except Exception as exc:  # noqa: BLE001 — 注入件异常 Fail-Closed
            raise LlmEvolutionError(f"fitness_evaluator 异常: {expr!r}（{type(exc).__name__}）") from exc
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise LlmEvolutionError(f"fitness_evaluator 返回非法: {v!r}（expression={expr!r}）")
        return float(v)

    @staticmethod
    def _llm_output(raw: object, role: MutationRole, notes: list[str]) -> str | None:
        """LLM 输出契约：非空字符串；非法输出剔除留痕（单样本 fail-open）。"""
        if not isinstance(raw, str) or not raw.strip():
            notes.append(f"LLM {role.value} 角色输出非法剔除: {str(raw)[:60]!r}")
            return None
        return raw.strip()

    # ── 主流程 ────────────────────────────────────────────────────────────

    def run(self, seed_expressions: Sequence[str]) -> LlmEvolutionResult:
        """进化主循环（仅盘后；三重门禁 + p-hacking → 人工裁决队列）。"""
        if self._after_hours is None:
            raise LlmEvolutionError("is_after_hours 未注入（仅盘后运行语义，Fail-Closed）")
        if not bool(self._after_hours()):
            raise LlmEvolutionError("非盘后时段拒绝运行（仅盘后运行语义，Fail-Closed）")
        missing = [name for name, gate in self._gates.items() if gate is None]
        if missing:
            raise LlmEvolutionError(f"三重门禁未注入齐全: {missing}（Fail-Closed）")
        if self._p_hacking is None:
            raise LlmEvolutionError("p_hacking_assessor 未注入（p-hacking 评估强制注入，Fail-Closed）")
        if not seed_expressions:
            raise LlmEvolutionError("seed_expressions 为空（无初始种群）")
        seeds: list[str] = []
        for expr in seed_expressions:
            if not isinstance(expr, str) or not expr.strip():
                raise LlmEvolutionError(f"种子表达式非法（须非空字符串）: {expr!r}")
            if expr.strip() not in seeds:
                seeds.append(expr.strip())

        notes: list[str] = []
        # 种群成员: (expression, role)
        pop: list[tuple[str, MutationRole]] = [(e, MutationRole.SEED) for e in seeds]
        best = float("-inf")
        for _gen in range(self._gens):
            scored = sorted(
                ((self._score(e), e, role) for e, role in pop),
                key=lambda t: (-t[0], t[1]),
            )
            best = max(best, scored[0][0])
            elites = scored[: self._elite_n]  # 精英保留
            offspring: list[tuple[str, MutationRole]] = []
            for i, (_f, expr, _r) in enumerate(elites):
                out = self._llm_output(self._exploit(expr), MutationRole.EXPLOIT, notes)
                if out is not None:
                    offspring.append((out, MutationRole.EXPLOIT))
                mate = elites[(i + 1) % len(elites)][1]
                out = self._llm_output(self._crossover(expr, mate), MutationRole.CROSSOVER, notes)
                if out is not None:
                    offspring.append((out, MutationRole.CROSSOVER))
            while len(elites) + len(offspring) < self._pop:  # Explore 多样性注入
                out = self._llm_output(self._explore(), MutationRole.EXPLORE, notes)
                if out is None:
                    notes.append("Explore 连续非法输出，停止补充（防死循环）")
                    break
                offspring.append((out, MutationRole.EXPLORE))
            combined = [(e, r) for _f, e, r in elites] + offspring
            dedup: list[tuple[str, MutationRole]] = []
            seen: set[str] = set()
            for expr, role in combined:
                if expr in seen:
                    notes.append(f"多样性去重: {expr}")
                    continue
                seen.add(expr)
                dedup.append((expr, role))
            pop = dedup[: self._pop]

        final = sorted(
            ((self._score(e), e, role) for e, role in pop),
            key=lambda t: (-t[0], t[1]),
        )
        best = max(best, final[0][0])
        admitted: list[LlmCandidate] = []
        for fitness, expr, role in final:
            if not self._pass_gates(expr, notes):
                continue
            p = self._assess_p_hacking(expr)
            if p > self._max_p:
                notes.append(f"p-hacking 概率超限剔除: {expr}（{p:.4f}>{self._max_p}）")
                continue
            self._counter += 1
            cand = LlmCandidate(
                candidate_id=f"LE-{self._counter:04d}",
                expression=expr,
                role=role,
                fitness=fitness,
                p_hacking=p,
                generation=self._gens,
            )
            self._queue.setdefault(cand.candidate_id, cand)
            admitted.append(cand)
        _log.info("LLM 进化完成: %d 代，过检候选 %d（待人工裁决）", self._gens, len(admitted))
        return LlmEvolutionResult(
            generations_run=self._gens,
            best_fitness=best,
            candidates=tuple(admitted),
            notes=tuple(notes),
        )

    def _pass_gates(self, expr: str, notes: list[str]) -> bool:
        for name, gate in self._gates.items():
            assert gate is not None  # run 入口已校验齐全
            try:
                ok = bool(gate(expr))
            except Exception as exc:  # noqa: BLE001 — 门禁异常按不过处理（Fail-Closed 语义）
                _log.warning("门禁 %s 异常: %s %s", name, expr, type(exc).__name__)
                notes.append(f"门禁 {name} 异常剔除: {expr}")
                return False
            if not ok:
                notes.append(f"门禁 {name} 未过剔除: {expr}")
                return False
        return True

    def _assess_p_hacking(self, expr: str) -> float:
        try:
            p = self._p_hacking(expr)  # type: ignore[misc]
        except LlmEvolutionError:
            raise
        except Exception as exc:  # noqa: BLE001 — 注入件异常 Fail-Closed
            raise LlmEvolutionError(f"p_hacking_assessor 异常: {expr!r}（{type(exc).__name__}）") from exc
        if isinstance(p, bool) or not isinstance(p, (int, float)):
            raise LlmEvolutionError(f"p_hacking_assessor 返回非法: {p!r}（expression={expr!r}）")
        return float(p)

    # ── 人工裁决（严禁全自动上线硬约束） ─────────────────────────────────────

    def adjudication_queue(self) -> tuple[LlmCandidate, ...]:
        """待人工裁决队列（入队顺序，确定性）。"""
        return tuple(self._queue.values())

    def approve(self, candidate_id: str) -> LlmCandidate:
        """人工裁决通过：队列 → 已入库（未知/已处理 id Fail-Closed）。"""
        cand = self._queue.pop(candidate_id, None)
        if cand is None:
            raise LlmEvolutionError(f"未知或已处理 candidate_id: {candidate_id!r}（仅待裁决条目可通过）")
        self._admitted[candidate_id] = cand
        _log.info("LLM 进化候选人工裁决入库: %s %s", candidate_id, cand.expression)
        return cand

    def reject(self, candidate_id: str) -> LlmCandidate:
        """人工裁决拒绝：移出队列（未知/已处理 id Fail-Closed）。"""
        cand = self._queue.pop(candidate_id, None)
        if cand is None:
            raise LlmEvolutionError(f"未知或已处理 candidate_id: {candidate_id!r}（仅待裁决条目可拒绝）")
        _log.info("LLM 进化候选人工裁决拒绝: %s %s", candidate_id, cand.expression)
        return cand

    def admitted(self) -> tuple[LlmCandidate, ...]:
        """已裁决入库视图（按 candidate_id 确定性排序）。"""
        return tuple(self._admitted[k] for k in sorted(self._admitted))
