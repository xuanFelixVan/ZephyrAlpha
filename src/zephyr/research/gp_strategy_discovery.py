# [BLUEPRINT] MOD-FAC-003 | docs/03_modules/_domain_factor/gp_strategy_discovery/blueprint.md
# [MODULE] zephyr.research.gp_strategy_discovery
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] 无（协议核心纯内存；rng/fitness_evaluator/三重门禁验证器全注入）
# [CONSUMERS] 运行时装配批（GP 策略发现批 / 审批后入因子库草稿治理串行合并）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 算子集词表闭合（算术 add|sub|mul|div / 条件 gt|lt / 滚动 ts_mean|ts_std|ts_max|ts_min|ts_sum；终端=价量变量+窗口常数）；表达式树生成/交叉/变异仅经注入随机源（越界随机数 Fail-Closed）；树结构合法性校验（滚动第二子树须常数、深度护栏），交叉/变异产物非法→回退亲本；进化循环种群/代数护栏；候选强制三重门禁（Purged K-Fold/Walk-Forward/Permutation 注入验证器，未注入齐全 evolve Fail-Closed）；过门禁仅入人工审批队列，approve 方可入库，严禁自动入库；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_factor/gp_strategy_discovery/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] GpDiscoveryError(占位 ZA-FAC-UNREGISTERED-GP-DISCOVERY)——随机源/适应度评估器缺失/护栏参数越界/随机数越出 [0,1)/三重门禁未注入齐全/未知 candidate_id 审批时抛
# [TESTS] tests/research/test_gp_strategy_discovery.py
# [A_module] module_id=MOD-FAC-003 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""GpStrategyDiscovery — 遗传规划策略发现器（MOD-FAC-003）。

B10-01844（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-FAC-019，A1 §29.14）：GP/SR
进化信号公式——算子集（算术/条件/滚动词表闭合）+ 表达式树（生成/交叉/变异，
注入随机源）+ 适应度 IC/Sharpe 注入评估器 + 进化循环（种群/代数护栏）+ 强制
**三重门禁**（Purged K-Fold / Walk-Forward / Permutation 注入验证器）+ **人工
审批后方可入库**（审批队列硬约束）。

查重分工（蓝图 §0）：factor_mining_pipeline=论文→LLM 假说链（外部知识驱动）；
auto_feature_discoverer=算子模板笛卡尔枚举（无进化）；本件=表达式树**进化搜
索**（生成/交叉/变异+三重门禁），三者驱动源正交。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Final, Iterator, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "ARITH_OPS",
    "COND_OPS",
    "ROLLING_OPS",
    "TERMINAL_VARS",
    "WINDOW_CONSTS",
    "EvolutionResult",
    "ExprNode",
    "GpCandidate",
    "GpDiscoveryError",
    "GpStrategyDiscovery",
    "serialize",
]

#: 算术算子词表（闭合，二元）
ARITH_OPS: Final = ("add", "sub", "mul", "div")
#: 条件算子词表（闭合，二元）
COND_OPS: Final = ("gt", "lt")
#: 滚动算子词表（闭合，二元；第二子树须窗口常数）
ROLLING_OPS: Final = ("ts_mean", "ts_std", "ts_max", "ts_min", "ts_sum")
#: 终端价量变量词表（闭合）
TERMINAL_VARS: Final = ("open", "high", "low", "close", "volume")
#: 窗口常数词表（闭合）
WINDOW_CONSTS: Final = (3, 5, 10, 20)

_BINARY_OPS: Final = ARITH_OPS + COND_OPS
_OP_POOL: Final = _BINARY_OPS + ROLLING_OPS

#: 进化循环护栏
_POP_MIN, _POP_MAX = 2, 100
_GEN_MIN, _GEN_MAX = 1, 50
_DEPTH_MIN, _DEPTH_MAX = 2, 6


class GpDiscoveryError(Exception):
    """GP 策略发现输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FAC-UNREGISTERED-GP-DISCOVERY。
    """


@dataclass(frozen=True)
class ExprNode:
    """表达式树节点（frozen；op ∈ {var,const} ∪ 算子词表）。"""

    op: str
    children: tuple["ExprNode", ...] = ()
    value: str | int | None = None


def serialize(node: ExprNode) -> str:
    """表达式树 → 确定性前缀字符串（如 ``add(close, ts_mean(volume, 5))``）。"""
    if node.op == "var":
        return str(node.value)
    if node.op == "const":
        return str(node.value)
    return f"{node.op}(" + ", ".join(serialize(c) for c in node.children) + ")"


def _flatten(node: ExprNode, path: tuple[int, ...] = ()) -> Iterator[tuple[tuple[int, ...], ExprNode]]:
    """先序枚举 (路径, 节点)（确定性遍历序）。"""
    yield path, node
    for i, child in enumerate(node.children):
        yield from _flatten(child, path + (i,))


def _replace(node: ExprNode, path: tuple[int, ...], sub: ExprNode) -> ExprNode:
    """按路径替换子树（返回新树，原树不可变）。"""
    if not path:
        return sub
    head, rest = path[0], path[1:]
    children = list(node.children)
    children[head] = _replace(children[head], rest, sub)
    return ExprNode(node.op, tuple(children), node.value)


@dataclass(frozen=True)
class GpCandidate:
    """过三重门禁候选（人工审批队列条目，frozen）。"""

    candidate_id: str
    expression: str
    fitness: float
    generation: int


@dataclass(frozen=True)
class EvolutionResult:
    """进化循环产出（frozen）。"""

    generations_run: int
    best_fitness: float
    candidates: tuple[GpCandidate, ...]
    notes: tuple[str, ...]


class GpStrategyDiscovery:
    """GP/SR 进化信号公式发现器（进化循环 + 三重门禁 + 人工审批队列）。

    Args:
        rng: 注入随机源，``() -> [0,1)`` 均匀随机数。
        fitness_evaluator: 注入适应度评估器，``expression -> float``（IC/Sharpe）。
        purged_kfold_gate / walkforward_gate / permutation_gate: 三重门禁注入
            验证器，``expression -> bool``（evolve 前须注入齐全，Fail-Closed）。
        population_size / generations / max_depth: 进化循环护栏。
        min_fitness: 候选适应度下限。
    """

    def __init__(
        self,
        *,
        rng: Callable[[], float] | None,
        fitness_evaluator: Callable[[str], float] | None,
        purged_kfold_gate: Callable[[str], bool] | None = None,
        walkforward_gate: Callable[[str], bool] | None = None,
        permutation_gate: Callable[[str], bool] | None = None,
        population_size: int = 10,
        generations: int = 3,
        max_depth: int = 3,
        min_fitness: float = 0.0,
    ) -> None:
        if rng is None:
            raise GpDiscoveryError("rng 未注入（随机源强制注入，Fail-Closed）")
        if fitness_evaluator is None:
            raise GpDiscoveryError("fitness_evaluator 未注入（适应度评估强制注入，Fail-Closed）")
        for name, val, lo, hi in (
            ("population_size", population_size, _POP_MIN, _POP_MAX),
            ("generations", generations, _GEN_MIN, _GEN_MAX),
            ("max_depth", max_depth, _DEPTH_MIN, _DEPTH_MAX),
        ):
            if isinstance(val, bool) or not isinstance(val, int) or not (lo <= val <= hi):
                raise GpDiscoveryError(f"{name} 越出护栏 [{lo},{hi}]: {val!r}")
        self._rng = rng
        self._fitness = fitness_evaluator
        self._gates = {
            "purged_kfold": purged_kfold_gate,
            "walkforward": walkforward_gate,
            "permutation": permutation_gate,
        }
        self._pop = population_size
        self._gens = generations
        self._max_depth = max_depth
        self._min_fitness = float(min_fitness)
        self._approval: dict[str, GpCandidate] = {}
        self._admitted: dict[str, GpCandidate] = {}
        self._counter = 0

    # ── 随机源封装（越界 Fail-Closed） ─────────────────────────────────────

    def _u(self) -> float:
        u = float(self._rng())
        if not (0.0 <= u < 1.0):
            raise GpDiscoveryError(f"rng 返回越出 [0,1): {u!r}（随机源契约违反，Fail-Closed）")
        return u

    def _below(self, n: int) -> int:
        return min(int(self._u() * n), n - 1)

    # ── 树合法性（词表闭合 + 滚动常数约束 + 深度护栏） ──────────────────────

    def _is_valid(self, node: ExprNode, depth: int = 1) -> bool:
        if depth > self._max_depth:
            return False
        if node.op == "var":
            return not node.children and node.value in TERMINAL_VARS
        if node.op == "const":
            return not node.children and node.value in WINDOW_CONSTS
        if node.op in _BINARY_OPS:
            return len(node.children) == 2 and all(
                self._is_valid(c, depth + 1) for c in node.children
            )
        if node.op in ROLLING_OPS:
            if len(node.children) != 2:
                return False
            series, window = node.children
            return (
                self._is_valid(series, depth + 1)
                and window.op == "const"
                and window.value in WINDOW_CONSTS
            )
        return False

    # ── 生成 / 交叉 / 变异（随机源注入） ────────────────────────────────────

    def _gen(self, depth: int) -> ExprNode:
        if depth >= self._max_depth or self._u() < 0.4:
            return ExprNode("var", (), TERMINAL_VARS[self._below(len(TERMINAL_VARS))])
        op = _OP_POOL[self._below(len(_OP_POOL))]
        left = self._gen(depth + 1)
        if op in ROLLING_OPS:
            right: ExprNode = ExprNode("const", (), WINDOW_CONSTS[self._below(len(WINDOW_CONSTS))])
        else:
            right = self._gen(depth + 1)
        return ExprNode(op, (left, right))

    def random_tree(self) -> ExprNode:
        """ramped 生成合法表达式树（深度护栏内）。"""
        return self._gen(1)

    def crossover(self, a: ExprNode, b: ExprNode) -> ExprNode:
        """交叉：各选一切点互换子树；产物非法 → 确定性回退亲本 a。"""
        flat_a = list(_flatten(a))
        path_a, _node_a = flat_a[self._below(len(flat_a))]
        flat_b = list(_flatten(b))
        _path_b, sub_b = flat_b[self._below(len(flat_b))]
        child = _replace(a, path_a, sub_b)
        return child if self._is_valid(child) else a

    def mutate(self, tree: ExprNode) -> ExprNode:
        """变异：随机节点重生子树；产物非法 → 确定性回退原树。"""
        flat = list(_flatten(tree))
        path, _old = flat[self._below(len(flat))]
        sub = self._gen(len(path) + 1)
        child = _replace(tree, path, sub)
        return child if self._is_valid(child) else tree

    # ── 进化循环（种群/代数护栏 + 三重门禁 + 人工审批队列） ─────────────────

    def evolve(self) -> EvolutionResult:
        """进化主循环：生成→适应度→选择→交叉/变异→三重门禁→人工审批队列。"""
        missing = [name for name, gate in self._gates.items() if gate is None]
        if missing:
            raise GpDiscoveryError(
                f"三重门禁未注入齐全: {missing}（强制 Purged K-Fold/Walk-Forward/Permutation，Fail-Closed）"
            )
        notes: list[str] = []
        pop = [self.random_tree() for _ in range(self._pop)]
        best = float("-inf")
        for gen in range(self._gens):
            scored = sorted(
                ((self._score(serialize(t)), serialize(t), t) for t in pop),
                key=lambda t: (-t[0], t[1]),
            )
            best = max(best, scored[0][0])
            survivors = scored[: max(2, self._pop // 2)]
            nxt = [t for _, _, t in survivors]
            while len(nxt) < self._pop:
                p1 = survivors[self._below(len(survivors))][2]
                p2 = survivors[self._below(len(survivors))][2]
                child = self.crossover(p1, p2) if self._u() < 0.7 else self.mutate(p1)
                nxt.append(child)
            pop = nxt
        final = sorted(
            ((self._score(serialize(t)), serialize(t)) for t in pop),
            key=lambda t: (-t[0], t[1]),
        )
        best = max(best, final[0][0])
        admitted: list[GpCandidate] = []
        seen: set[str] = set()
        for fitness, expr in final:
            if expr in seen:
                continue
            seen.add(expr)
            if fitness < self._min_fitness:
                notes.append(f"适应度不足剔除: {expr}（{fitness:.4f}<{self._min_fitness}）")
                continue
            if not self._pass_gates(expr, notes):
                continue
            self._counter += 1
            cand = GpCandidate(
                candidate_id=f"GP-{self._counter:04d}",
                expression=expr,
                fitness=fitness,
                generation=self._gens,
            )
            self._approval.setdefault(cand.candidate_id, cand)
            admitted.append(cand)
        _log.info("GP 进化完成: %d 代，过门禁候选 %d", self._gens, len(admitted))
        return EvolutionResult(
            generations_run=self._gens,
            best_fitness=best,
            candidates=tuple(admitted),
            notes=tuple(notes),
        )

    def _score(self, expr: str) -> float:
        try:
            score = self._fitness(expr)
        except GpDiscoveryError:
            raise
        except Exception as exc:  # noqa: BLE001 — 注入件异常 Fail-Closed
            raise GpDiscoveryError(f"fitness_evaluator 异常: {expr!r}（{type(exc).__name__}）") from exc
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise GpDiscoveryError(f"fitness_evaluator 返回非法: {score!r}（expression={expr!r}）")
        return float(score)

    def _pass_gates(self, expr: str, notes: list[str]) -> bool:
        for name, gate in self._gates.items():
            assert gate is not None  # evolve 入口已校验齐全
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

    # ── 人工审批（严禁自动入库硬约束） ──────────────────────────────────────

    def approval_queue(self) -> tuple[GpCandidate, ...]:
        """待审批队列（入队顺序，确定性）。"""
        return tuple(self._approval.values())

    def approve(self, candidate_id: str) -> GpCandidate:
        """人工审批通过：队列 → 已入库（未知/已处理 id Fail-Closed）。"""
        cand = self._approval.pop(candidate_id, None)
        if cand is None:
            raise GpDiscoveryError(f"未知或已处理 candidate_id: {candidate_id!r}（仅待审批条目可通过）")
        self._admitted[candidate_id] = cand
        _log.info("GP 候选人工审批入库: %s %s", candidate_id, cand.expression)
        return cand

    def reject(self, candidate_id: str) -> GpCandidate:
        """人工审批拒绝：移出队列（未知/已处理 id Fail-Closed）。"""
        cand = self._approval.pop(candidate_id, None)
        if cand is None:
            raise GpDiscoveryError(f"未知或已处理 candidate_id: {candidate_id!r}（仅待审批条目可拒绝）")
        _log.info("GP 候选人工审批拒绝: %s %s", candidate_id, cand.expression)
        return cand

    def admitted(self) -> tuple[GpCandidate, ...]:
        """已审批入库视图（按 candidate_id 确定性排序）。"""
        return tuple(self._admitted[k] for k in sorted(self._admitted))
