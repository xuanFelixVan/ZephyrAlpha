"""
ZephyrAlpha 蓝图拆解器
=====================
依据：MOD-INF-006 v0.3.0 §5 TaskCard 接口契约
输入：治理文档（ADR/TD/CS/CP 等 blueprint.yaml），可选 task_repo
输出：双向存储——SQLite（task_repo.create）+ .md（companion）

命名空间规则（§3.1）：
  ADR-* → Architecture Decision Record     TD-* → Technical Debt
  CS-*  → Coding Standard                  CP-* → Construction Plan
  INFRA-* → Infrastructure Blueprint       SCRIPT-* → Script Governance

task_id 格式（§3.2.1）：{NAMESPACE}-{SEQ}（SQLite auto-increment 保证唯一性）
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from zephyr.core.models import (
    DecompositionResult,
    GateLevel,
    TaskCard,
    TaskStatus,
)

logger = logging.getLogger(__name__)

_NAMESPACE_MAP: dict[str, str] = {
    "ADR": "ADR",
    "TD": "TD",
    "TECH-DEBT": "TD",
    "CS": "CS",
    "CODING-STANDARD": "CS",
    "CP": "CP",
    "CONSTRUCTION-PLAN": "CP",
    "INFRA": "INFRA",
    "SCRIPT": "SCRIPT",
}

_ITEM_PATTERN = re.compile(
    r"[-*]\s+(?P<marker>"
    r"\[ADR-\d+-\d+\]|"
    r"TD-\d+|"
    r"CS-\d+|"
    r"CP-\d+|"
    r"INFRA-\d+"
    r")\s+\*\*(?P<module>[^*]+)\*\*\s*—?\s*(?P<desc>.+?)(?:\s*$)",
)

class BlueprintDecomposer:
    """
    治理文档 → 逐条拆解 → 生成 TaskCard 列表。

    每个文档条目按优先级和命名空间分派：
    - ADR-* → ADR     - TD-* → TD       - CS-* → CS
    - CP-* → CP       - INFRA-* → INFRA  - SCRIPT-* → SCRIPT
    """

    def __init__(
        self,
        task_repo: object | None = None,
        docs_dir: str | None = None,
    ):
        self.task_repo = task_repo
        self.docs_dir = Path(docs_dir) if docs_dir else None
        self._global_seq = 0

    def decompose_blueprint(
        self,
        blueprint_path: str,
        namespace: str = "CP",
        phase: int = 1,
    ) -> DecompositionResult:
        """
        拆解单个蓝图文件 → 生成 DecompositionResult。

        Args:
            blueprint_path: 蓝图文件路径
            namespace: 命名空间前缀
            phase: Phase 编号
        """
        path = Path(blueprint_path)
        if not path.exists():
            raise FileNotFoundError(f"蓝图文件不存在: {blueprint_path}")

        content = path.read_text(encoding="utf-8")

        tasks, unassigned, warnings = self._extract_tasks(content, blueprint_path, namespace, phase)

        dep_graph = self._build_dependency_graph(tasks)

        result = DecompositionResult(
            total_tasks=len(tasks),
            tasks=tasks,
            dependency_graph=dep_graph,
            unassigned_items=unassigned,
            warnings=warnings,
        )

        self._write_tasks(result)

        return result

    def decompose_blueprints_batch(
        self,
        blueprint_paths: list[str],
        namespace: str = "INFRA",
        phase: int = 1,
    ) -> list[DecompositionResult]:
        """
        批量拆解多个蓝图文件。
        """
        results: list[DecompositionResult] = []
        for bp_path in blueprint_paths:
            result = self.decompose_blueprint(bp_path, namespace, phase)
            results.append(result)
        return results

    def _extract_tasks(
        self,
        content: str,
        blueprint_path: str,
        namespace: str,
        phase: int,
    ) -> tuple[list[TaskCard], list[str], list[str]]:
        tasks: list[TaskCard] = []
        unassigned: list[str] = []
        warnings: list[str] = []

        lines = content.split("\n")
        task_name_buf: list[str] = []
        task_desc_buf: list[str] = []
        in_task = False

        for line in lines:
            item_match = _ITEM_PATTERN.match(line)
            if item_match:
                if in_task and task_name_buf:
                    task = self._build_task_card(
                        name=" ".join(task_name_buf),
                        description=" ".join(task_desc_buf),
                        blueprint_path=blueprint_path,
                        namespace=namespace.upper(),
                        phase=phase,
                    )
                    if task:
                        tasks.append(task)
                    else:
                        warnings.append(f"无法解析任务: {task_name_buf}")

                in_task = True
                task_name_buf = [item_match.group("module").strip()]
                task_desc_buf = [item_match.group("desc").strip()]
            elif in_task and line.strip():
                task_desc_buf.append(line.strip())

        if in_task and task_name_buf:
            task = self._build_task_card(
                name=" ".join(task_name_buf),
                description=" ".join(task_desc_buf),
                blueprint_path=blueprint_path,
                namespace=namespace.upper(),
                phase=phase,
            )
            if task:
                tasks.append(task)
            else:
                unassigned.append(" ".join(task_name_buf))

        return tasks, unassigned, warnings

    def _build_task_card(
        self,
        name: str,
        description: str,
        blueprint_path: str,
        namespace: str,
        phase: int,
    ) -> TaskCard | None:
        try:
            from zephyr.shared.schemas import TaskNamespace

            ns = getattr(TaskNamespace, namespace, None)
            if ns is None:
                return None

            if self.task_repo:
                seq = self.task_repo.next_seq(ns)
            else:
                self._global_seq += 1
                seq = self._global_seq

            task_id = f"{ns.value}-{seq}"

            bp_module_id = Path(blueprint_path).stem

            return TaskCard(
                task_id=task_id,
                namespace=ns,
                seq=seq,
                title=name,
                status=TaskStatus.PENDING,
                phase=phase,
                execution_model="deepseek",
                safety_level="L",
                source_blueprint=bp_module_id,
                source_section="auto-extracted",
                description=description,
                upstream_files=[blueprint_path],
                downstream_outputs=[],
                allowed_touch=[],
                forbidden_touch=[],
                applicable_rules=[
                    {
                        "module_id": "MOD-INF-006",
                        "section": "§3.2.1",
                        "reason": "TaskCard Schema——任务格式合规",
                    }
                ],
                context_assembly_manifest=[
                    {
                        "file_path": blueprint_path,
                        "reason": "源蓝图",
                    }
                ],
                rollback_instructions="",
                estimated_tokens=4000,
                timeout_minutes=30,
                completed_gates=[],
                blocked_gates={},
                assigned_pipeline="A",
                pipeline_modules=[],
                blocked_by=[],
                artifact_paths=[],
                audit_findings=[],
                ke_entries=[],
                ai_autonomy_level="supervised",
                autonomy_checklist=[],
                construction_status="pending",
                verification_status="unverified",
                created_at="2026-05-02T00:00:00",
                updated_at="2026-05-02T00:00:00",
            )
        except Exception as e:
            logger.warning(f"TaskCard 构造失败: {name} — {e}")
            return None

    def _build_dependency_graph(self, tasks: list[TaskCard]) -> dict[str, list[str]]:
        graph: dict[str, list[str]] = {}
        for i, task in enumerate(tasks):
            if i > 0:
                graph[task.task_id] = [tasks[i - 1].task_id]
            else:
                graph[task.task_id] = []
        return graph

    def _write_tasks(self, result: DecompositionResult) -> None:
        if self.task_repo:
            for task in result.tasks:
                try:
                    self.task_repo.create(task)
                except Exception as e:
                    logger.error(f"task_repo.create 失败: {task.task_id} — {e}")

        if self.docs_dir:
            out_dir = self.docs_dir / "decomposition"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / "decomposition_result.json"
            out_path.write_text(
                result.model_dump_json(indent=2),
                encoding="utf-8",
            )

    def check_gate(self, gate_id: GateLevel, task: TaskCard) -> bool:
        if gate_id == GateLevel.G0:
            return bool(task.source_blueprint and task.description)
        if gate_id == GateLevel.G7:
            return task.verification_status == "verified" and all(f.resolved for f in task.audit_findings)
        return True
