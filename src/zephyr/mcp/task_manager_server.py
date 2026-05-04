"""
ZephyrAlpha MCP Task Manager Server
===================================
依据：MOD-INF-006 v0.3.0 §5.3 MCP 接口契约
注册：task_repo（SQLite） + BlueprintDecomposer（蓝图拆解）
暴露：5 个 MCP Tool（create / get / update_status / decompose / register_from_triage）
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server

from zephyr.core.blueprint_decomposer import BlueprintDecomposer
from zephyr.core.models import (
    DecompositionResult,
    GateLevel,
    TaskCard,
    TaskStatus,
)
from zephyr.shared.schemas import Priority, SafetyLevel, TaskNamespace

logger = logging.getLogger(__name__)


class TaskManagerMCP:
    """
    MCP Server for Task System.

    5 Tools：
      create_task          — 创建 TaskCard
      get_task             — 查询 TaskCard
      update_task_status   — 更新状态
      decompose_blueprint  — 拆解蓝图
      register_from_triage — 从审阅池注册任务
    """

    def __init__(
        self,
        task_repo: Optional[object] = None,
        docs_dir: Optional[str] = None,
    ):
        self.task_repo = task_repo
        self.decomposer = BlueprintDecomposer(
            task_repo=task_repo,
            docs_dir=docs_dir,
        )
        self.docs_dir = Path(docs_dir) if docs_dir else None
        self.server = Server("task-manager")

        self._register_tools()

    def _register_tools(self) -> None:
        server = self.server

        @server.call_tool()
        async def create_task(
            task_id: str,
            title: str,
            source_blueprint: str,
            source_section: str,
            description: str,
            namespace: str = "CP",
            priority: str = "P2",
            phase: int = 1,
            execution_model: str = "deepseek",
            safety_level: str = "L",
        ) -> dict:
            """创建 TaskCard——蓝图 MOD-INF-006 §5.3 Tool 1"""
            from zephyr.shared.schemas import Priority

            ns = getattr(TaskNamespace, namespace.upper(), TaskNamespace.CP)
            seq = self._next_seq(ns) if self.task_repo else self._global_seq

            if self.task_repo:
                task_id = f"{ns.value}-{seq}"

            tc = TaskCard(
                task_id=task_id,
                namespace=ns,
                seq=seq,
                title=title,
                status=TaskStatus.PENDING,
                priority=getattr(Priority, priority, Priority.P2),
                phase=phase,
                execution_model=execution_model,
                safety_level=getattr(
                    __import__("zephyr.shared.schemas", fromlist=["SafetyLevel"]).SafetyLevel,
                    safety_level,
                    __import__("zephyr.shared.schemas", fromlist=["SafetyLevel"]).SafetyLevel.L,
                ),
                source_blueprint=source_blueprint,
                source_section=source_section,
                description=description,
                upstream_files=[],
                downstream_outputs=[],
                allowed_touch=[],
                forbidden_touch=[],
                applicable_rules=[],
                context_assembly_manifest=[],
                rollback_instructions="",
                estimated_tokens=8000,
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
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
            )

            self._persist(tc)
            return self._to_response(tc)

        @server.call_tool()
        async def get_task(task_id: str) -> dict:
            """查询 TaskCard——蓝图 MOD-INF-006 §5.3 Tool 2"""
            tc = self._load(task_id)
            if tc is None:
                raise ValueError(f"Task 不存在: {task_id}")
            return self._to_response(tc)

        @server.call_tool()
        async def update_task_status(task_id: str, new_status: str) -> dict:
            """更新任务状态——蓝图 MOD-INF-006 §5.3 Tool 3"""
            tc = self._load(task_id)
            if tc is None:
                raise ValueError(f"Task 不存在: {task_id}")

            new_st = getattr(TaskStatus, new_status.upper(), None)
            if new_st is None:
                raise ValueError(f"无效状态: {new_status}，合法值: {[s.name for s in TaskStatus]}")

            tc.status = new_st
            tc.updated_at = datetime.now().isoformat()

            if new_st == TaskStatus.COMPLETED:
                tc.completed_at = datetime.now().isoformat()

            self._persist(tc)
            return self._to_response(tc)

        @server.call_tool()
        async def decompose_blueprint(blueprint_path: str, namespace: str = "CP", phase: int = 1) -> dict:
            """拆解蓝图→生成 TaskCard 列表——蓝图 MOD-INF-006 §5.3 Tool 4"""
            result: DecompositionResult = self.decomposer.decompose_blueprint(
                blueprint_path=blueprint_path,
                namespace=namespace,
                phase=phase,
            )
            return {
                "total_tasks": result.total_tasks,
                "task_ids": [t.task_id for t in result.tasks],
                "dependency_graph": result.dependency_graph,
                "unassigned_items": result.unassigned_items,
                "warnings": result.warnings,
            }

        @server.call_tool()
        async def register_from_triage(triage_path: str, namespace: str = "ADR", phase: int = 1) -> dict:
            """从审阅池注册任务——蓝图 MOD-INF-006 §5.3 Tool 5"""
            path = Path(triage_path)
            if not path.exists():
                raise FileNotFoundError(f"审阅文件不存在: {triage_path}")

            content = path.read_text(encoding="utf-8")
            ns = getattr(TaskNamespace, namespace.upper(), TaskNamespace.ADR)
            seq = self._next_seq(ns) if self.task_repo else self._global_seq
            task_id = f"{ns.value}-{seq}"

            profile = _extract_triage_profile(content, task_id)

            tc = TaskCard(
                task_id=task_id,
                namespace=ns,
                seq=seq,
                title=profile.get("title", f"审阅导入: {path.stem}"),
                status=TaskStatus.PENDING,
                phase=phase,
                execution_model="deepseek",
                safety_level="L",
                source_blueprint=path.stem,
                source_section="triage",
                description=profile.get("description", content[:800]),
                upstream_files=[str(path.resolve())],
                downstream_outputs=[],
                allowed_touch=[],
                forbidden_touch=[],
                applicable_rules=[{
                    "module_id": "MOD-INF-006",
                    "section": "§5.3",
                    "reason": "审阅池注册",
                }],
                context_assembly_manifest=[{
                    "file_path": str(path.resolve()),
                    "reason": "审阅源文件",
                }],
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
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
            )

            self._persist(tc)
            return self._to_response(tc)

        self._global_seq = 0

    def _next_seq(self, namespace: TaskNamespace) -> int:
        if self.task_repo:
            return self.task_repo.next_seq(namespace)
        self._global_seq += 1
        return self._global_seq

    def _persist(self, tc: TaskCard) -> None:
        if self.task_repo:
            try:
                existing = self.task_repo.get(tc.task_id)
                if existing:
                    existing.status = tc.status
                    existing.updated_at = tc.updated_at
                    self.task_repo.update(existing)
                else:
                    self.task_repo.create(tc)
            except Exception:
                pass

    def _load(self, task_id: str) -> Optional[TaskCard]:
        if self.task_repo:
            try:
                task = self.task_repo.get(task_id)
                if task:
                    return task
            except Exception:
                pass

        return None

    @staticmethod
    def _to_response(tc: TaskCard) -> dict:
        return {
            "task_id": tc.task_id,
            "title": tc.title,
            "status": tc.status.name,
            "priority": tc.priority.name,
            "phase": tc.phase,
            "source_blueprint": tc.source_blueprint,
            "source_section": tc.source_section,
            "description": tc.description[:200],
            "upstream_files": tc.upstream_files,
            "execution_model": tc.execution_model,
            "estimated_tokens": tc.estimated_tokens,
            "completed_gates": [g.value for g in tc.completed_gates],
            "created_at": tc.created_at.isoformat() if hasattr(tc.created_at, "isoformat") else str(tc.created_at),
            "updated_at": tc.updated_at.isoformat() if hasattr(tc.updated_at, "isoformat") else str(tc.updated_at),
        }

    def run(self) -> None:
        async def _run():
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options(),
                )

        asyncio.run(_run())


_TRIAGE_TITLE_PATTERN = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def _extract_triage_profile(content: str, task_id: str) -> dict:
    profile: dict = {"title": task_id, "description": content[:800]}
    title_match = _TRIAGE_TITLE_PATTERN.search(content)
    if title_match:
        profile["title"] = title_match.group(1).strip()
        body = content[title_match.end():].strip()
        if body:
            profile["description"] = body[:800]
    return profile


def _parse_md_status(content: str) -> Optional[str]:
    for line in content.split("\n"):
        if line.startswith("**状态**："):
            return line.split("：", 1)[1].strip()
    return None


_MD_KV_PATTERN = re.compile(r"^\*\*(.+?)\*\*[：:]\s*(.+)$")
_MD_LIST_ITEM = re.compile(r"^-\s+(.+)$")
_MD_GATE_PASSED = re.compile(r"已通过:\s*\[(.*?)\]")
_MD_GATE_BLOCKED = re.compile(r"阻塞:\s*(.+)$")
_MD_TIME_ITEM = re.compile(r"^-\s*(创建|更新)[：:]\s*(.+)$")


def _parse_md_to_taskcard(content: str) -> Optional[TaskCard]:
    lines = content.split("\n")
    title = ""
    kv: dict[str, str] = {}
    description_lines: list[str] = []
    upstream_files: list[str] = []
    downstream_outputs: list[dict] = []
    completed_gates: list[str] = []
    blocked_gates: dict[str, str] = {}
    created_at_str = ""
    updated_at_str = ""

    section: str = ""
    for line in lines:
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            continue

        if line.startswith("## "):
            section = line[3:].strip()
            continue

        if section == "描述":
            stripped = line.strip()
            if stripped and not stripped.startswith("**"):
                description_lines.append(stripped)
            continue

        if section == "上游文件":
            m = _MD_LIST_ITEM.match(line)
            if m:
                upstream_files.append(m.group(1).strip())
            continue

        if section == "下游产出":
            m = _MD_LIST_ITEM.match(line)
            if m:
                item = m.group(1).strip()
                if " — " in item:
                    path_part, desc_part = item.split(" — ", 1)
                    downstream_outputs.append({"path": path_part.strip(), "description": desc_part.strip()})
                else:
                    downstream_outputs.append({"path": item, "description": ""})
            continue

        if section == "门禁状态":
            gm = _MD_GATE_PASSED.search(line)
            if gm:
                gates_str = gm.group(1).strip()
                if gates_str:
                    completed_gates = [g.strip().strip("'\"") for g in gates_str.split(",") if g.strip()]
            bm = _MD_GATE_BLOCKED.search(line)
            if bm:
                try:
                    blocked_gates = json.loads(bm.group(1).strip().replace("'", '"'))
                except (json.JSONDecodeError, TypeError):
                    pass
            continue

        if section == "时间":
            tm = _MD_TIME_ITEM.match(line)
            if tm:
                key = tm.group(1).strip()
                val = tm.group(2).strip()
                if key == "创建":
                    created_at_str = val
                elif key == "更新":
                    updated_at_str = val
            continue

        if not section or section == "描述":
            m = _MD_KV_PATTERN.match(line)
            if m:
                kv[m.group(1).strip()] = m.group(2).strip()

    description = "\n".join(description_lines).strip()
    if not description:
        description = kv.get("描述", title or "无描述")

    if len(description) < 3:
        description = title + " — 自动恢复"

    task_id = kv.get("task_id", "")

    ns_str = kv.get("命名空间", "CP")
    ns = getattr(TaskNamespace, ns_str, TaskNamespace.CP) if ns_str else TaskNamespace.CP

    status_str = kv.get("状态", "PENDING")
    status = getattr(TaskStatus, status_str, TaskStatus.PENDING) if status_str else TaskStatus.PENDING

    priority_str = kv.get("优先级", "P2")
    priority = getattr(Priority, priority_str, Priority.P2) if priority_str else Priority.P2

    phase = int(kv.get("Phase", "1"))
    execution_model = kv.get("执行模型", "deepseek")
    estimated_tokens = int(kv.get("预估 Token", "8000"))

    source_parts = kv.get("源蓝图", "MOD-UNKNOWN §unknown").split(" §", 1)
    source_blueprint = source_parts[0].strip()
    source_section = source_parts[1].strip() if len(source_parts) > 1 else "unknown"

    created_at = _parse_time(created_at_str)
    updated_at = _parse_time(updated_at_str)

    gates_list = [GateLevel(g) for g in completed_gates if g in GateLevel.__members__]

    return TaskCard(
        task_id=task_id,
        namespace=ns,
        seq=int(kv.get("seq", "0") or "0") or 1,
        title=title,
        status=status,
        priority=priority,
        phase=phase,
        execution_model=execution_model,
        safety_level=SafetyLevel.L,
        source_blueprint=source_blueprint,
        source_section=source_section,
        description=description,
        upstream_files=upstream_files,
        downstream_outputs=downstream_outputs,
        estimated_tokens=estimated_tokens,
        completed_gates=gates_list,
        blocked_gates=blocked_gates,
        created_at=created_at,
        updated_at=updated_at,
    )


def _parse_time(s: str) -> datetime:
    if not s:
        return datetime.now()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except ValueError:
            continue
    return datetime.now()


def _taskcard_to_md(tc: TaskCard) -> str:
    dt_fmt = "%Y-%m-%d %H:%M"
    created = (
        tc.created_at.strftime(dt_fmt)
        if hasattr(tc.created_at, "strftime")
        else str(tc.created_at)[:16]
    )
    updated = (
        tc.updated_at.strftime(dt_fmt)
        if hasattr(tc.updated_at, "strftime")
        else str(tc.updated_at)[:16]
    )

    lines = [
        f"# {tc.title}",
        "",
        f"**task_id**：{tc.task_id}",
        f"**命名空间**：{tc.namespace.value}",
        f"**状态**：{tc.status.name}",
        f"**优先级**：{tc.priority.name}",
        f"**Phase**：{tc.phase}",
        f"**源蓝图**：{tc.source_blueprint} §{tc.source_section}",
        f"**执行模型**：{tc.execution_model}",
        f"**预估 Token**：{tc.estimated_tokens}",
        "",
        "## 描述",
        "",
        tc.description,
        "",
        "## 上游文件",
        "",
    ]

    for f in tc.upstream_files:
        lines.append(f"- {f}")

    lines.extend([
        "",
        "## 下游产出",
        "",
    ])

    for d in tc.downstream_outputs:
        if isinstance(d, dict):
            lines.append(f"- {d.get('path', '?')} — {d.get('description', '')}")
        else:
            lines.append(f"- {d}")

    lines.extend([
        "",
        "## 门禁状态",
        "",
        f"已通过: {[g.value for g in tc.completed_gates]}",
    ])

    if tc.blocked_gates:
        lines.append(f"阻塞: {tc.blocked_gates}")

    lines.extend([
        "",
        "## 时间",
        "",
        f"- 创建：{created}",
        f"- 更新：{updated}",
        "",
        "> 本文件由 MOD-INF-006 task_manager_server 自动同步生成。",
    ])

    return "\n".join(lines)
