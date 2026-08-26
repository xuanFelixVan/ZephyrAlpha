# [BLUEPRINT] MOD-ORCH-003 | docs/03_modules/_domain_orchestrator/task_orchestration_skill/blueprint.md
# [MODULE] zephyr.orchestrator.task_orchestration_skill
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] 无（编排核心纯内存；work_dag 语义内建轻量 DAG；executor/dlq_sink/clock 全注入）
# [CONSUMERS] 运行时装配批（任务分解入口 / 真实执行器绑定 / DLQ 落库路由 / 人工确认闸门）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] DAG 节点 task_id 唯一且非空; 依赖须已登记(未知依赖拒绝); 自环/循环拒绝; 波次按 Kahn 拓扑分层且层内按 task_id 排序; 编排计划未经 human_gated 确认禁止执行(硬约束); executor 未注入 Fail-Closed 不旁路; 重试上限后失败入 DLQ; 依赖失败级联 SKIPPED; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_orchestrator/task_orchestration_skill/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] TaskOrchestrationError(占位 ZA-ORCH-UNREGISTERED-TASK-ORCHESTRATION)——空plan_id/重复plan/空任务集/未知依赖/循环/未确认执行/executor缺失/未知plan/重复契约时抛
# [TESTS] tests/orchestrator/test_task_orchestration_skill.py
# [A_module] module_id=MOD-ORCH-003 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""TaskOrchestrationSkill — 任务编排技能（MOD-ORCH-003）。

B11-02579（AUD-DRAFT-001-DIGEST P2 波 P2-W13，CAND-ORCH-003，A7）：
task-orchestration 技能封装——任务分解 → DAG 生成（work_dag 语义：拓扑分层 +
循环拒绝，仓库无独立 work_dag 件，本件内建轻量 DAG）→ 波次调度 → 失败重试 /
DLQ + 技能契约（输入输出 Schema 登记）+ 产出编排计划需 **human_gated 确认**
（未确认执行 Fail-Closed）。

查重分工（蓝图 §0）：agent_orchestrator=6角色×10域能力评分路由（本件不做能
力评分，只做任务图编排）；layered_command_chain=Agent 层级委托协议（本件=
任务 DAG 执行面，不建指挥链）；execution/dlq_manager=DLQ 持久化实现（本件经
注入 dlq_sink 回调，不实现持久化）。
"""

from __future__ import annotations

import datetime
import logging
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "ExecutionRecord",
    "ExecutionReport",
    "OrchestrationPlan",
    "SkillContract",
    "TaskNode",
    "TaskOrchestrationError",
    "TaskOrchestrationSkill",
    "TaskStatus",
    "WorkDAG",
]


class TaskOrchestrationError(Exception):
    """任务编排输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-ORCH-UNREGISTERED-TASK-ORCHESTRATION。
    """


class TaskStatus(str, Enum):
    """任务执行状态机。"""

    PENDING = "pending"
    SUCCEEDED = "succeeded"
    DLQ = "dlq"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class TaskNode:
    """任务节点 Schema（DAG 顶点，frozen）。"""

    task_id: str
    name: str
    payload: Mapping
    depends_on: tuple[str, ...] = ()
    max_retries: int = 0


@dataclass(frozen=True)
class SkillContract:
    """技能契约 Schema 登记（输入/输出 JSON-Schema 字典，frozen）。"""

    skill_name: str
    input_schema: Mapping
    output_schema: Mapping
    registered_at: datetime.datetime


@dataclass(frozen=True)
class OrchestrationPlan:
    """编排计划（分解产物；waves 为拓扑分层结果，frozen）。"""

    plan_id: str
    nodes: tuple[TaskNode, ...]
    waves: tuple[tuple[str, ...], ...]
    created_at: datetime.datetime


@dataclass(frozen=True)
class ExecutionRecord:
    """单任务执行记录（frozen）。"""

    task_id: str
    status: TaskStatus
    attempts: int
    error: str | None
    finished_at: datetime.datetime


@dataclass(frozen=True)
class ExecutionReport:
    """整计划执行报告（records 按波次/层内序确定性排列，frozen）。"""

    plan_id: str
    records: tuple[ExecutionRecord, ...]
    dlq_task_ids: tuple[str, ...]
    executed_at: datetime.datetime

    @property
    def succeeded(self) -> bool:
        """全部任务成功（无 DLQ/SKIPPED）。"""
        return all(r.status is TaskStatus.SUCCEEDED for r in self.records)

    def status_of(self, task_id: str) -> TaskStatus:
        """单任务状态查询（未知任务 → Fail-Closed）。"""
        for r in self.records:
            if r.task_id == task_id:
                return r.status
        raise TaskOrchestrationError(f"未知任务: {task_id!r}")


class WorkDAG:
    """轻量 DAG（work_dag 语义：拓扑分层 + 未知依赖/循环拒绝）。

    参照 agent_orchestrator 纯内存/DI 既有模式内建；边仅经 depends_on 声明，
    校验集中在 waves()（未知依赖 + 三色 DFS 循环检测）。
    """

    def __init__(self) -> None:
        self._deps: dict[str, tuple[str, ...]] = {}

    def add_node(self, task_id: str, depends_on: Iterable[str] = ()) -> None:
        """加顶点（空 id / 重复 / 自环 → Fail-Closed）。"""
        if not task_id:
            raise TaskOrchestrationError("task_id 为空")
        if task_id in self._deps:
            raise TaskOrchestrationError(f"task_id 重复: {task_id!r}")
        deps = tuple(depends_on)
        if task_id in deps:
            raise TaskOrchestrationError(f"自环非法: {task_id!r}")
        self._deps[task_id] = deps

    def nodes(self) -> tuple[str, ...]:
        """顶点视图（按登记序确定性排列）。"""
        return tuple(self._deps)

    def dependencies(self, task_id: str) -> tuple[str, ...]:
        """单顶点依赖查询（未知顶点 → Fail-Closed）。"""
        deps = self._deps.get(task_id)
        if deps is None:
            raise TaskOrchestrationError(f"未知任务: {task_id!r}")
        return deps

    def waves(self) -> tuple[tuple[str, ...], ...]:
        """Kahn 拓扑分层（未知依赖/循环 → Fail-Closed；层内按 task_id 排序）。"""
        for task_id, deps in self._deps.items():
            for dep in deps:
                if dep not in self._deps:
                    raise TaskOrchestrationError(
                        f"未知依赖: 任务 {task_id!r} 依赖未登记任务 {dep!r}"
                    )
        self._reject_cycle()
        indegree = {t: len(deps) for t, deps in self._deps.items()}
        dependents: dict[str, list[str]] = {t: [] for t in self._deps}
        for task_id, deps in self._deps.items():
            for dep in deps:
                dependents[dep].append(task_id)
        out: list[tuple[str, ...]] = []
        frontier = sorted(t for t, d in indegree.items() if d == 0)
        while frontier:
            out.append(tuple(frontier))
            nxt: list[str] = []
            for task_id in frontier:
                for child in dependents[task_id]:
                    indegree[child] -= 1
                    if indegree[child] == 0:
                        nxt.append(child)
            frontier = sorted(nxt)
        return tuple(out)

    def _reject_cycle(self) -> None:
        """三色 DFS 循环检测（白=0 灰=1 黑=2）。"""
        color = {t: 0 for t in self._deps}

        def _visit(node: str, stack: tuple[str, ...]) -> None:
            color[node] = 1
            for dep in self._deps[node]:
                if dep not in color:
                    continue  # 未知依赖由 waves() 先行拒绝
                if color[dep] == 1:
                    cycle = " -> ".join((*stack, node, dep))
                    raise TaskOrchestrationError(f"循环依赖拒绝: {cycle}")
                if color[dep] == 0:
                    _visit(dep, (*stack, node))
            color[node] = 2

        for task_id in self._deps:
            if color[task_id] == 0:
                _visit(task_id, ())


class TaskOrchestrationSkill:
    """任务编排技能（契约登记 + 分解成 DAG + 人工确认 + 波次执行 + 重试/DLQ）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        executor: Callable[[TaskNode], object] | None = None,
        dlq_sink: Callable[[TaskNode, str], None] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._executor = executor
        self._dlq_sink = dlq_sink
        self._contracts: dict[str, SkillContract] = {}
        self._plans: dict[str, OrchestrationPlan] = {}
        self._confirmed: dict[str, bool] = {}
        self._reports: dict[str, ExecutionReport] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _plan_of(self, plan_id: str) -> OrchestrationPlan:
        plan = self._plans.get(plan_id)
        if plan is None:
            raise TaskOrchestrationError(f"未知 plan: {plan_id!r}")
        return plan

    # ── 技能契约登记 ──────────────────────────────────────────────────────

    def register_contract(self, contract: SkillContract) -> None:
        """登记技能契约（空名/重复/非法 Schema → Fail-Closed）。"""
        if not contract.skill_name:
            raise TaskOrchestrationError("skill_name 为空")
        if not isinstance(contract.input_schema, Mapping) or not isinstance(
            contract.output_schema, Mapping
        ):
            raise TaskOrchestrationError(f"契约 Schema 非法: {contract.skill_name!r}")
        if contract.skill_name in self._contracts:
            raise TaskOrchestrationError(f"契约重复登记: {contract.skill_name!r}")
        self._contracts[contract.skill_name] = contract

    def contract_of(self, skill_name: str) -> SkillContract:
        """契约查询（未知技能 → Fail-Closed）。"""
        contract = self._contracts.get(skill_name)
        if contract is None:
            raise TaskOrchestrationError(f"未知技能契约: {skill_name!r}")
        return contract

    def contracts(self) -> tuple[str, ...]:
        """已登记技能名视图（字典序确定性排列）。"""
        return tuple(sorted(self._contracts))

    # ── 任务分解 → DAG → 计划 ────────────────────────────────────────────

    def decompose(self, plan_id: str, tasks: Iterable[TaskNode]) -> OrchestrationPlan:
        """任务分解：节点校验 → DAG 生成（循环/未知依赖拒绝）→ 计划（未确认）。"""
        if not plan_id:
            raise TaskOrchestrationError("plan_id 为空")
        if plan_id in self._plans:
            raise TaskOrchestrationError(f"plan_id 重复: {plan_id!r}")
        nodes = tuple(tasks)
        if not nodes:
            raise TaskOrchestrationError("任务集为空（无可编排节点）")
        dag = WorkDAG()
        for node in nodes:
            if not isinstance(node, TaskNode):
                raise TaskOrchestrationError(f"非法任务节点: {node!r}")
            if node.max_retries < 0:
                raise TaskOrchestrationError(f"max_retries 非法: {node.task_id!r}")
            dag.add_node(node.task_id, node.depends_on)
        waves = dag.waves()
        plan = OrchestrationPlan(
            plan_id=plan_id, nodes=nodes, waves=waves, created_at=self._clock()
        )
        self._plans[plan_id] = plan
        self._confirmed[plan_id] = False
        return plan

    # ── human_gated 确认（硬约束） ────────────────────────────────────────

    def confirm_plan(self, plan_id: str, approved: bool = True) -> None:
        """人工确认编排计划（未确认/否决的计划禁止执行）。"""
        self._plan_of(plan_id)
        self._confirmed[plan_id] = bool(approved)

    def is_confirmed(self, plan_id: str) -> bool:
        """确认状态查询（未知 plan → Fail-Closed）。"""
        self._plan_of(plan_id)
        return self._confirmed[plan_id]

    # ── 波次调度执行 ──────────────────────────────────────────────────────

    def execute(self, plan_id: str) -> ExecutionReport:
        """波次执行：未确认/executor 缺失 → Fail-Closed；失败重试上限后入 DLQ。"""
        plan = self._plan_of(plan_id)
        if not self._confirmed[plan_id]:
            raise TaskOrchestrationError(
                f"编排计划 {plan_id!r} 未经 human_gated 确认（硬约束，禁止执行）"
            )
        if self._executor is None:
            raise TaskOrchestrationError("executor 未注入（Fail-Closed 不旁路）")
        node_by_id = {n.task_id: n for n in plan.nodes}
        statuses: dict[str, TaskStatus] = {}
        records: list[ExecutionRecord] = []
        dlq_ids: list[str] = []
        for wave in plan.waves:
            for task_id in wave:
                node = node_by_id[task_id]
                if any(
                    statuses.get(dep) in (TaskStatus.DLQ, TaskStatus.SKIPPED)
                    for dep in node.depends_on
                ):
                    statuses[task_id] = TaskStatus.SKIPPED
                    records.append(ExecutionRecord(
                        task_id=task_id, status=TaskStatus.SKIPPED, attempts=0,
                        error="依赖任务失败级联跳过", finished_at=self._clock(),
                    ))
                    continue
                attempts, error = 0, None
                for _ in range(1 + node.max_retries):
                    attempts += 1
                    try:
                        self._executor(node)
                        error = None
                        break
                    except Exception as exc:  # noqa: BLE001 — 执行异常收敛为重试/DLQ
                        error = f"{type(exc).__name__}: {exc}"
                        _log.warning(
                            "任务执行失败(第%d次): %s (%s)", attempts, task_id, error
                        )
                if error is None:
                    statuses[task_id] = TaskStatus.SUCCEEDED
                else:
                    statuses[task_id] = TaskStatus.DLQ
                    dlq_ids.append(task_id)
                    if self._dlq_sink is not None:
                        try:
                            self._dlq_sink(node, error)
                        except Exception:  # noqa: BLE001 — DLQ 回调异常不阻断
                            _log.exception("dlq_sink 回调失败: %s", task_id)
                records.append(ExecutionRecord(
                    task_id=task_id, status=statuses[task_id], attempts=attempts,
                    error=error, finished_at=self._clock(),
                ))
        report = ExecutionReport(
            plan_id=plan_id,
            records=tuple(records),
            dlq_task_ids=tuple(dlq_ids),
            executed_at=self._clock(),
        )
        self._reports[plan_id] = report
        return report

    # ── 查询 ─────────────────────────────────────────────────────────────

    def plan_of(self, plan_id: str) -> OrchestrationPlan:
        """计划查询（未知 plan → Fail-Closed）。"""
        return self._plan_of(plan_id)

    def report_of(self, plan_id: str) -> ExecutionReport:
        """执行报告查询（未执行 → Fail-Closed）。"""
        report = self._reports.get(plan_id)
        if report is None:
            raise TaskOrchestrationError(f"plan 未执行（无报告）: {plan_id!r}")
        return report
