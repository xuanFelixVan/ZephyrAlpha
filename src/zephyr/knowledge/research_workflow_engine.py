# [BLUEPRINT] MOD-KNW-014 | docs/03_modules/_domain_knowledge/research_workflow_engine/blueprint.md
# [MODULE] zephyr.knowledge.research_workflow_engine
# [DOMAIN] D_KNOWLEDGE
# [DEPENDENCIES] 无（协议核心纯内存；clock/sleeper/gate/audit_sink 全注入，task 随模板节点注入）
# [CONSUMERS] 运行时装配批（研究模板注册 / 上线门禁绑定 / 审计路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 模板注册表唯一(template_id/node_id); DAG 依赖引用闭合且循环检测 Fail-Closed; 拓扑执行顺序确定性(Kahn+node_id 排序); 重试指数退避经注入 sleeper 不真睡; 上线门禁未注入/拒绝/异常即 BLOCKED 阻断该节点并标记; 审计留痕 seq 单调递增; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_knowledge/research_workflow_engine/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ResearchWorkflowError(占位 ZA-KNW-UNREGISTERED-RESEARCH-WORKFLOW)——空模板/重复节点/未知依赖/自环/循环DAG/未知模板/重复run_id/非法退避参数时抛
# [TESTS] tests/knowledge/test_research_workflow_engine.py
# [A_module] module_id=MOD-KNW-014 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""ResearchWorkflowEngine — 研究工作流引擎轻量版（MOD-KNW-014）。

B6-08551（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-017，B6 D-RESEARCH-09）：
复用 task_scheduler 语义的研究 pipeline——DAG 节点依赖拓扑执行 +
研究模板注册表（因子挖掘→IC验证→注册→灰度）+ 重试指数退避
（注入时钟/sleeper 不真睡）+ 审计留痕 + 上线门禁挂接（注入 gate 回调，
拒绝即阻断该节点并标记 BLOCKED）。

查重分工（蓝图 §0）：task_scheduler=通用任务调度（本件=研究 DAG 语义层，
不重建调度原语）；research_project_aggregate=项目聚合根状态机（本件=单
次运行执行引擎，不管项目生命周期）；layered_command_chain=Agent 层级委
托（零交集）。上线门禁实体归 gov_audit kb_gate 族（本件仅注入回调）。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Callable, Final, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "AuditEvent",
    "NodeContext",
    "NodeResult",
    "NodeStatus",
    "ResearchTemplate",
    "ResearchWorkflowEngine",
    "ResearchWorkflowError",
    "RunResult",
    "RunStatus",
    "WorkflowNode",
]

#: 因子研究标准模板阶段（词表闭合，逐阶段依赖，灰度阶段挂上线门禁）
_FACTOR_STAGES: Final[tuple[str, ...]] = (
    "factor_mining",
    "ic_validation",
    "registration",
    "canary_release",
)


class ResearchWorkflowError(Exception):
    """研究工作流输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-KNW-UNREGISTERED-RESEARCH-WORKFLOW。
    """


class NodeStatus(str, Enum):
    """节点执行状态。"""

    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class RunStatus(str, Enum):
    """工作流运行状态。"""

    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class NodeContext:
    """节点执行上下文（run 元信息 + 上游产出只读视图，frozen）。"""

    run_id: str
    template_id: str
    node_id: str
    context: Mapping[str, object]
    outputs: Mapping[str, object]


@dataclass(frozen=True)
class WorkflowNode:
    """DAG 节点（task 注入；depends_on 引用闭合；frozen）。"""

    node_id: str
    task: Callable[[NodeContext], object]
    depends_on: tuple[str, ...] = ()
    max_retries: int = 0
    requires_gate: bool = False


@dataclass(frozen=True)
class ResearchTemplate:
    """研究模板（DAG 定义载体，frozen）。"""

    template_id: str
    description: str
    nodes: tuple[WorkflowNode, ...]

    @classmethod
    def factor_research(
        cls,
        tasks: Mapping[str, Callable[[NodeContext], object]],
        *,
        template_id: str = "factor_research",
        description: str = "因子挖掘→IC验证→注册→灰度标准研究模板",
    ) -> "ResearchTemplate":
        """标准因子研究模板：四阶段逐依赖链，灰度阶段强制上线门禁。"""
        missing = [stage for stage in _FACTOR_STAGES if stage not in tasks]
        if missing:
            raise ResearchWorkflowError(f"因子研究模板缺任务: {missing}")
        nodes: list[WorkflowNode] = []
        prev: str | None = None
        for stage in _FACTOR_STAGES:
            nodes.append(WorkflowNode(
                node_id=stage,
                task=tasks[stage],
                depends_on=(prev,) if prev is not None else (),
                requires_gate=(stage == "canary_release"),
            ))
            prev = stage
        return cls(template_id=template_id, description=description, nodes=tuple(nodes))


@dataclass(frozen=True)
class AuditEvent:
    """审计事件（seq 单调递增留痕，frozen）。"""

    seq: int
    run_id: str
    node_id: str | None
    event: str
    detail: str
    at: datetime.datetime


@dataclass(frozen=True)
class NodeResult:
    """单节点执行结果（frozen）。"""

    node_id: str
    status: NodeStatus
    attempts: int
    output: object
    error: str | None


@dataclass(frozen=True)
class RunResult:
    """单次运行结果（节点结果按拓扑执行序，frozen）。"""

    run_id: str
    template_id: str
    status: RunStatus
    node_results: tuple[NodeResult, ...]
    started_at: datetime.datetime
    finished_at: datetime.datetime


class ResearchWorkflowEngine:
    """研究工作流引擎（模板注册表 + DAG 拓扑执行 + 退避重试 + 门禁 + 审计）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        sleeper: Callable[[float], None] | None = None,
        gate: Callable[[str, str], bool] | None = None,
        audit_sink: Callable[[AuditEvent], None] | None = None,
        base_backoff_seconds: float = 1.0,
        max_backoff_seconds: float = 60.0,
    ) -> None:
        if base_backoff_seconds <= 0:
            raise ResearchWorkflowError(
                f"base_backoff_seconds 非法: {base_backoff_seconds}（须 > 0）"
            )
        if max_backoff_seconds <= 0:
            raise ResearchWorkflowError(
                f"max_backoff_seconds 非法: {max_backoff_seconds}（须 > 0）"
            )
        self._clock = clock or datetime.datetime.now
        self._sleeper = sleeper or (lambda seconds: None)  # 默认空操作，绝不真睡
        self._gate = gate
        self._audit_sink = audit_sink
        self._base_backoff = float(base_backoff_seconds)
        self._max_backoff = float(max_backoff_seconds)
        self._templates: dict[str, ResearchTemplate] = {}
        self._topo: dict[str, tuple[str, ...]] = {}
        self._runs: dict[str, RunResult] = {}
        self._audit_log: list[AuditEvent] = []
        self._audit_seq = 0
        self._run_seq = 0

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _audit(self, run_id: str, node_id: str | None, event: str, detail: str) -> None:
        self._audit_seq += 1
        entry = AuditEvent(
            seq=self._audit_seq,
            run_id=run_id,
            node_id=node_id,
            event=event,
            detail=detail,
            at=self._clock(),
        )
        self._audit_log.append(entry)
        if self._audit_sink is not None:
            try:
                self._audit_sink(entry)
            except Exception:  # noqa: BLE001 — 审计路由异常不阻断执行
                _log.exception("audit_sink 失败: %s/%s", run_id, event)

    @staticmethod
    def _topo_order(nodes: Sequence[WorkflowNode]) -> tuple[str, ...]:
        """Kahn 拓扑排序（ready 按 node_id 排序保证确定性）；循环 → Fail-Closed。"""
        indegree = {n.node_id: 0 for n in nodes}
        children: dict[str, list[str]] = {n.node_id: [] for n in nodes}
        for node in nodes:
            for dep in node.depends_on:
                indegree[node.node_id] += 1
                children[dep].append(node.node_id)
        ready = sorted(nid for nid, degree in indegree.items() if degree == 0)
        order: list[str] = []
        while ready:
            nid = ready.pop(0)
            order.append(nid)
            for child in children[nid]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    ready.append(child)
            ready.sort()
        if len(order) != len(nodes):
            raise ResearchWorkflowError("DAG 存在循环依赖（Fail-Closed 拒绝注册）")
        return tuple(order)

    def _gate_allowed(self, run_id: str, node_id: str) -> tuple[bool, str]:
        """上线门禁判定：未注入/拒绝/异常均按拒绝处理（Fail-Closed）。"""
        if self._gate is None:
            return False, "上线门禁未注入（Fail-Closed 默认拒绝）"
        try:
            allowed = bool(self._gate(run_id, node_id))
        except Exception:  # noqa: BLE001 — 门禁异常按拒绝处理
            _log.exception("gate 回调异常: %s/%s", run_id, node_id)
            return False, "上线门禁异常（按拒绝处理）"
        if not allowed:
            return False, "上线门禁拒绝"
        return True, ""

    # ── 模板注册表 ────────────────────────────────────────────────────────

    def register_template(self, template: ResearchTemplate) -> None:
        """登记研究模板：结构校验 + 依赖闭合 + 循环检测，全部 Fail-Closed。"""
        if not template.template_id:
            raise ResearchWorkflowError("template_id 为空")
        if template.template_id in self._templates:
            raise ResearchWorkflowError(f"重复模板: {template.template_id!r}")
        if not template.nodes:
            raise ResearchWorkflowError(f"模板无节点: {template.template_id!r}")
        seen: set[str] = set()
        for node in template.nodes:
            if not node.node_id:
                raise ResearchWorkflowError("node_id 为空")
            if node.node_id in seen:
                raise ResearchWorkflowError(f"重复节点: {node.node_id!r}")
            seen.add(node.node_id)
            if not callable(node.task):
                raise ResearchWorkflowError(f"节点 task 不可调用: {node.node_id!r}")
            if node.max_retries < 0:
                raise ResearchWorkflowError(
                    f"max_retries 非法: {node.max_retries}（须 >= 0）"
                )
            for dep in node.depends_on:
                if dep == node.node_id:
                    raise ResearchWorkflowError(f"节点自环: {node.node_id!r}")
                if dep not in {n.node_id for n in template.nodes}:
                    raise ResearchWorkflowError(
                        f"未知依赖: {node.node_id!r} -> {dep!r}（依赖引用须闭合）"
                    )
        order = self._topo_order(template.nodes)
        self._templates[template.template_id] = template
        self._topo[template.template_id] = order

    def get_template(self, template_id: str) -> ResearchTemplate:
        """模板查询（未知 → Fail-Closed）。"""
        template = self._templates.get(template_id)
        if template is None:
            raise ResearchWorkflowError(f"未知模板: {template_id!r}")
        return template

    def list_templates(self) -> tuple[ResearchTemplate, ...]:
        """模板列表（按 template_id 确定性排序）。"""
        return tuple(self._templates[tid] for tid in sorted(self._templates))

    # ── 执行 ─────────────────────────────────────────────────────────────

    def _execute_node(
        self,
        run_id: str,
        template: ResearchTemplate,
        node: WorkflowNode,
        node_context: NodeContext,
    ) -> NodeResult:
        """单节点执行：失败按指数退避重试（注入 sleeper），穷尽 → FAILED。"""
        attempts = 0
        while True:
            attempts += 1
            try:
                output = node.task(node_context)
            except Exception as exc:  # noqa: BLE001 — 任务异常按失败重试处理
                error = str(exc) or type(exc).__name__
                _log.warning("节点失败: %s/%s 第%d次: %s", run_id, node.node_id, attempts, error)
                if attempts <= node.max_retries:
                    delay = min(
                        self._base_backoff * (2 ** (attempts - 1)),
                        self._max_backoff,
                    )
                    self._audit(
                        run_id, node.node_id, "node_retry",
                        f"{error}；退避 {delay}s 后进行第 {attempts + 1} 次尝试",
                    )
                    self._sleeper(delay)
                    continue
                self._audit(
                    run_id, node.node_id, "node_failed",
                    f"共 {attempts} 次尝试均失败: {error}",
                )
                return NodeResult(node.node_id, NodeStatus.FAILED, attempts, None, error)
            self._audit(
                run_id, node.node_id, "node_succeeded", f"第 {attempts} 次尝试成功"
            )
            return NodeResult(node.node_id, NodeStatus.SUCCEEDED, attempts, output, None)

    def run(
        self,
        template_id: str,
        *,
        run_id: str | None = None,
        context: Mapping[str, object] | None = None,
    ) -> RunResult:
        """执行工作流：拓扑序逐节点；上游未成功→SKIPPED；门禁拒绝→BLOCKED。"""
        template = self._templates.get(template_id)
        if template is None:
            raise ResearchWorkflowError(f"未知模板: {template_id!r}")
        if run_id is None:
            self._run_seq += 1
            run_id = f"{template_id}-run-{self._run_seq:04d}"
        if not run_id:
            raise ResearchWorkflowError("run_id 为空")
        if run_id in self._runs:
            raise ResearchWorkflowError(f"重复 run_id: {run_id!r}")
        nodes_by_id = {n.node_id: n for n in template.nodes}
        started_at = self._clock()
        self._audit(run_id, None, "run_started", f"模板 {template_id!r} 启动，节点 {len(template.nodes)} 个")
        statuses: dict[str, NodeStatus] = {}
        outputs: dict[str, object] = {}
        results: list[NodeResult] = []
        for node_id in self._topo[template_id]:
            node = nodes_by_id[node_id]
            bad_upstream = sorted(
                dep for dep in node.depends_on
                if statuses[dep] is not NodeStatus.SUCCEEDED
            )
            if bad_upstream:
                detail = f"上游未成功: {bad_upstream}"
                self._audit(run_id, node_id, "node_skipped", detail)
                statuses[node_id] = NodeStatus.SKIPPED
                results.append(NodeResult(node_id, NodeStatus.SKIPPED, 0, None, detail))
                continue
            if node.requires_gate:
                allowed, reason = self._gate_allowed(run_id, node_id)
                if not allowed:
                    self._audit(run_id, node_id, "node_blocked", reason)
                    statuses[node_id] = NodeStatus.BLOCKED
                    results.append(NodeResult(node_id, NodeStatus.BLOCKED, 0, None, reason))
                    continue
                self._audit(run_id, node_id, "node_gate_passed", "上线门禁放行")
            node_context = NodeContext(
                run_id=run_id,
                template_id=template_id,
                node_id=node_id,
                context=MappingProxyType(dict(context or {})),
                outputs=MappingProxyType(dict(outputs)),
            )
            result = self._execute_node(run_id, template, node, node_context)
            statuses[node_id] = result.status
            if result.status is NodeStatus.SUCCEEDED:
                outputs[node_id] = result.output
            results.append(result)
        if any(s is NodeStatus.FAILED for s in statuses.values()):
            run_status = RunStatus.FAILED
        elif any(s is NodeStatus.BLOCKED for s in statuses.values()):
            run_status = RunStatus.BLOCKED
        else:
            run_status = RunStatus.SUCCEEDED
        finished_at = self._clock()
        self._audit(run_id, None, "run_finished", f"状态 {run_status.value}")
        run_result = RunResult(
            run_id=run_id,
            template_id=template_id,
            status=run_status,
            node_results=tuple(results),
            started_at=started_at,
            finished_at=finished_at,
        )
        self._runs[run_id] = run_result
        return run_result

    # ── 查询 ─────────────────────────────────────────────────────────────

    def get_run(self, run_id: str) -> RunResult:
        """运行查询（未知 → Fail-Closed）。"""
        result = self._runs.get(run_id)
        if result is None:
            raise ResearchWorkflowError(f"未知 run: {run_id!r}")
        return result

    def list_runs(self) -> tuple[RunResult, ...]:
        """运行列表（按 run_id 确定性排序）。"""
        return tuple(self._runs[rid] for rid in sorted(self._runs))

    def audit_trail(self, run_id: str | None = None) -> tuple[AuditEvent, ...]:
        """审计留痕（可按 run 过滤；按 seq 单调序）。"""
        return tuple(
            e for e in self._audit_log
            if run_id is None or e.run_id == run_id
        )
