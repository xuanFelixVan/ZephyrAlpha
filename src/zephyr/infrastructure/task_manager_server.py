# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §4.2
# [MODULE] zephyr.infrastructure.task_manager_server
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.blueprint_decomposer; zephyr.shared.models; zephyr.integration.shared.schema.severity_types; zephyr.integration.shared.schema.schemas
# [CONSUMERS] zephyr.infrastructure.mcp_server; AI sessions via MCP protocol
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] claim_task uses SQLite UPDATE RETURNING for atomic claim; status transitions follow 10-state machine
# [MODIFY-GUARD] claim_task/mark_task_done/mark_task_failed/batch_progress/list_dependents/write_draft/commit_draft/list_drafts/discard_draft — new tools must preserve atomic claim semantics
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError when task_repo is None; GateViolationError on invalid transitions
# [TESTS] tests/test_mcp_task_claim.py
# [A_module] module_id=MOD-INF_task_manager_server | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ZephyrAlpha MCP Task Manager Server
===================================
依据：MOD-TASK_SYSTEM v0.3.0 §5.3 MCP 接口契约
注册：task_repo（SQLite） + BlueprintDecomposer（蓝图拆解）
暴露：6 个 MCP Tool（create / get / list / update_status / decompose / register_from_triage；工具 ID 为 task_manager.*）
"""

from __future__ import annotations

import importlib
import json
import logging
import re
from datetime import UTC, datetime
from pathlib import Path

from mcp.server import FastMCP

from zephyr.shared.io.paths import REPO_ROOT

from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
from zephyr.shared.blueprint_tools.blueprint_decomposer import BlueprintDecomposer
from zephyr.shared.foundation.models import (
    DecompositionResult,
    GateLevel,
    TaskCard,
    TaskStatus,
)

logger = logging.getLogger(__name__)


class TaskManagerMCP:
    """
    MCP Server for Task System.

    6 Tools（MCP 注册名含 ``task_manager.`` 前缀，与 MOD-INF-013 / tool-contracts.yaml 一致）：
      create_task          — 创建 TaskCard
      get_task             — 查询 TaskCard
      update_task_status   — 更新状态
      decompose_blueprint  — 拆解蓝图
      list_tasks           — 条件筛选任务列表
      claim_task           — 原子认领下一个可施工任务（多AI并发安全）
      mark_task_done       — 标记任务完成
      mark_task_failed     — 标记任务失败
      batch_progress       — 查询批量进度
      list_dependents      — 查询依赖指定任务的下游任务
    """

    def __init__(
        self,
        task_repo: object | None = None,
        docs_dir: str | None = None,
        auth_check: callable | None = None,
    ):
        """
        Parameters
        ----------
        task_repo : TaskRepository | None
            SQLite 任务仓库
        docs_dir : str | None
            .md 双轨同步目标目录
        auth_check : callable | None
            权限检查钩子。签名为 ``auth_check(action: str, task_id: str) -> bool``。
            返回 False 表示拒绝操作，抛出异常同理。
            为 None 时跳过所有权限检查（默认——兼容旧版无 RBAC）。
        """
        self.task_repo = task_repo
        self.decomposer = BlueprintDecomposer(
            task_repo=task_repo,
            docs_dir=docs_dir,
        )
        self.docs_dir = Path(docs_dir) if docs_dir else None
        self._auth_check = auth_check
        self.mcp = FastMCP("task-manager")
        self._register_tools()
        self._global_seq = 0
        self._idempotency_cache: dict[str, dict] = {}

    @property
    def server(self) -> object:
        """向后兼容：指向 FastMCP 内部 lowlevel ``Server``（tests/ 与红队脚本读 ``.name``）。"""
        return self.mcp._mcp_server  # type: ignore[attr-defined]

    @property
    def tool_names(self) -> list[str]:
        """已注册工具名称列表（与 BaseMCPServer API 保持一致）。"""
        try:
            return list(self.mcp._tool_manager._tools.keys())
        except Exception:
            return [
                "task_manager.create_task",
                "task_manager.get_task",
                "task_manager.list_tasks",
                "task_manager.update_task_status",
                "task_manager.decompose_blueprint",
                "task_manager.register_from_triage",
            ]

    def _rbac_guard(self, action: str, task_id: str = "") -> None:
        """权限守卫——调用注入的 auth_check 钩子。

        若 auth_check 未注入（None），静默通过。
        若 auth_check 返回 False 或抛异常，以 PermissionError 阻断。
        """
        if self._auth_check is None:
            return
        try:
            if not self._auth_check(action, task_id):
                raise PermissionError(f"RBAC 拒绝: action={action}, task_id={task_id}")
        except PermissionError:
            raise
        except Exception as exc:
            raise PermissionError(
                f"RBAC 检查异常: action={action}, task_id={task_id} — {type(exc).__name__}: {exc}"
            ) from exc

    def _register_tools(self) -> None:
        mgr = self
        mcp = self.mcp

        @mcp.tool(name="task_manager.create_task")
        async def create_task(
            title: str,
            source_blueprint: str,
            source_section: str,
            description: str,
            files_in_scope: list[str] | None = None,
            deliverables: list[str] | None = None,
            allowed_touch: list[str] | None = None,
            task_id: str = "",
            namespace: str = "CP",
            priority: str = "P2",
            phase: int = 1,
            execution_model: str = "deepseek",
            safety_level: str = "L",
            downstream_outputs: list | None = None,
            pipeline_task_type: str = "",
            target_layer: str = "",
        ) -> dict:
            """创建 TaskCard——蓝图 MOD-TASK_SYSTEM §3.5 Tool 1（idempotent）"""
            # 5.51.1 修复：原可变默认参数 = [] 在函数定义时创建一次，所有调用共享同一 list 对象，
            # 若函数体内对列表做原地修改会跨调用污染。改为 None + 函数内初始化。
            if files_in_scope is None:
                files_in_scope = []
            if deliverables is None:
                deliverables = []
            if allowed_touch is None:
                allowed_touch = []
            if downstream_outputs is None:
                downstream_outputs = []

            import hashlib

            _mod = importlib.import_module("zephyr.governance.rule_enforcement.task_types")
            TaskNamespace = _mod.TaskNamespace
            normalize_execution_model = _mod.normalize_execution_model

            mgr._rbac_guard("create_task")
            from zephyr.integration.shared.schema.schemas import Priority

            raw = json.dumps(
                {
                    "title": title,
                    "source_blueprint": source_blueprint,
                    "source_section": source_section,
                    "description": description,
                    "namespace": namespace,
                    "priority": priority,
                    "phase": phase,
                },
                sort_keys=True,
                ensure_ascii=False,
            )
            arg_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            cached = mgr._idempotency_cache.get(arg_hash)
            if cached is not None:
                return cached

            ns = getattr(TaskNamespace, namespace.upper(), TaskNamespace.CP)
            seq = mgr._next_seq(ns)
            if mgr.task_repo or not task_id.strip():
                task_id = f"{ns.value}-{seq}"

            now = datetime.now(UTC)
            tc = TaskCard(
                task_id=task_id,
                namespace=ns,
                seq=seq,
                title=title,
                status=TaskStatus.PENDING,
                priority=getattr(Priority, priority, Priority.P2),
                phase=phase,
                execution_model=normalize_execution_model(execution_model),
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
                files_in_scope=files_in_scope,
                deliverables=deliverables,
                allowed_touch=allowed_touch,
                forbidden_touch=[],
                applicable_rules=[
                    {"module_id": source_blueprint, "section": source_section, "reason": "MCP create_task"}
                ],
                context_assembly_manifest=[],
                rollback_instructions="git checkout",
                post_sync_standard=["echo ok"],
                acceptance=["task passes G7 gate"],
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
                pipeline_task_type=pipeline_task_type or None,
                target_layer=target_layer or None,
                created_at=now,
                updated_at=now,
            )

            mgr._persist(tc)
            resp = mgr._to_response(tc)

            if downstream_outputs:
                try:
                    _mod = importlib.import_module("zephyr.governance.architecture_governance.path_resolver")
                    PathResolver = _mod.PathResolver
                    resolver = PathResolver(str(REPO_ROOT))
                    warnings = []
                    for item in downstream_outputs:
                        if isinstance(item, dict) and "path" in item:
                            resolution = resolver.validate_path(item["path"])
                            if resolution.status != "OK" and resolution.suggested_path:
                                warnings.append(
                                    {
                                        "expected": item["path"],
                                        "suggested": resolution.suggested_path,
                                        "status": resolution.status,
                                    }
                                )
                    if warnings:
                        resp["g8_warnings"] = warnings
                except ImportError:
                    pass

            mgr._idempotency_cache[arg_hash] = resp
            return resp

        @mcp.tool(name="task_manager.get_task")
        async def get_task(task_id: str) -> dict:
            """查询 TaskCard——蓝图 MOD-TASK_SYSTEM §3.5 Tool 2"""
            mgr._rbac_guard("get_task", task_id)
            tc = mgr._load(task_id)
            if tc is None:
                raise ValueError(f"Task 不存在: {task_id}")
            return mgr._to_response(tc)

        @mcp.tool(name="task_manager.list_tasks")
        async def list_tasks(
            phase: int | None = None,
            status: str | None = None,
            session_id: str | None = None,
            file_path_glob: str | None = None,
            limit: int = 50,
        ) -> dict:
            """按条件列出任务（需 task_repo）。"""
            mgr._rbac_guard("list_tasks")
            if mgr.task_repo is None:
                return {"items": [], "total": 0}
            tasks = mgr.task_repo.query_tasks(
                phase=phase,
                status=status,
                session_id=session_id,
                file_path_glob=file_path_glob,
                limit=limit,
            )
            items = [mgr._to_response(t) for t in tasks]
            return {"items": items, "total": len(items)}

        @mcp.tool(name="task_manager.update_task_status")
        async def update_task_status(task_id: str, new_status: str) -> dict:
            """更新任务状态——蓝图 MOD-TASK_SYSTEM §3.5 Tool 3（使用状态机 transition）"""
            mgr._rbac_guard("update_task_status", task_id)
            if mgr.task_repo is None:
                raise RuntimeError("update_task_status 需要注入 task_repo，当前为 None")

            new_st = getattr(TaskStatus, new_status.upper(), None)
            if new_st is None:
                raise ValueError(f"无效状态: {new_status}，合法值: {[s.name for s in TaskStatus]}")

            updated = mgr.task_repo.transition(task_id, new_st)
            if mgr.docs_dir:
                mgr._sync_md(updated)
            return mgr._to_response(updated)

        @mcp.tool(name="task_manager.decompose_blueprint")
        async def decompose_blueprint(blueprint_path: str, namespace: str = "CP", phase: int = 1) -> dict:
            """拆解蓝图→生成 TaskCard 列表——蓝图 MOD-TASK_SYSTEM §3.5 Tool 4"""
            mgr._rbac_guard("decompose_blueprint")
            result: DecompositionResult = mgr.decomposer.decompose_blueprint(
                blueprint_path=blueprint_path,
                namespace=namespace,
                phase=phase,
            )
            return {
                "total_tasks": result.total_tasks,
                "task_ids": [t.task_id for t in result.tasks],
                "dependency-graph": result.dependency_graph,
                "unassigned_items": result.unassigned_items,
                "warnings": result.warnings,
            }

        @mcp.tool(name="task_manager.register_from_triage")
        async def register_from_triage(
            triage_path: str = "",
            namespace: str = "KE",
            phase: int = 1,
            yaml_path: str = "",
        ) -> dict:
            """从审阅池注册任务——蓝图 MOD-TASK_SYSTEM §3.5 Tool 5（yaml_path 为契约兼容别名）。"""
            _mod = importlib.import_module("zephyr.governance.rule_enforcement.task_types")
            TaskNamespace = _mod.TaskNamespace
            normalize_execution_model = _mod.normalize_execution_model

            mgr._rbac_guard("register_from_triage")
            src = (triage_path or yaml_path).strip()
            if not src:
                raise ValueError("必须提供 triage_path（或兼容别名 yaml_path）")
            path = Path(src)
            if not path.exists():
                raise FileNotFoundError(f"审阅文件不存在: {src}")

            content = path.read_text(encoding="utf-8")
            ns = getattr(TaskNamespace, namespace.upper(), TaskNamespace.KBG)
            seq = mgr._next_seq(ns) if mgr.task_repo else mgr._global_seq
            task_id = f"{ns.value}-{seq}"

            profile = _extract_triage_profile(content, task_id)

            now = datetime.now(UTC)
            tc = TaskCard(
                task_id=task_id,
                namespace=ns,
                seq=seq,
                title=profile.get("title", f"审阅导入: {path.stem}"),
                status=TaskStatus.PENDING,
                phase=phase,
                execution_model=normalize_execution_model("deepseek"),
                safety_level=SafetyLevel.L,
                source_blueprint=path.stem,
                source_section="triage",
                description=profile.get("description", content[:50000]),
                upstream_files=[str(path.resolve())],
                downstream_outputs=[],
                allowed_touch=[],
                forbidden_touch=[],
                applicable_rules=[
                    {
                        "module_id": "MOD-TASK_SYSTEM",
                        "section": "§5.3",
                        "reason": "审阅池注册",
                    }
                ],
                context_assembly_manifest=[
                    {
                        "file_path": str(path.resolve()),
                        "reason": "审阅源文件",
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
                created_at=now,
                updated_at=now,
            )

            mgr._persist(tc)
            return mgr._to_response(tc)

        @mcp.tool(name="task_manager.claim_task")
        async def claim_task(batch_id: str, worker_id: str) -> dict:
            """原子认领下一个依赖已满足的 READY 任务——多AI并发安全（MOD-TASK_SYSTEM §16.7）"""
            mgr._rbac_guard("claim_task")
            if mgr.task_repo is None:
                raise RuntimeError("claim_task 需要注入 task_repo，当前为 None")
            card = mgr.task_repo.claim_next(batch_id, worker_id)
            if card is None:
                return {"claimed": False, "task": None, "reason": "no_ready_tasks"}
            return {"claimed": True, "task": mgr._to_response(card)}

        @mcp.tool(name="task_manager.mark_task_done")
        async def mark_task_done(task_id: str, worker_id: str = "") -> dict:
            """标记任务完成——调用状态机 transition(task_id, COMPLETED)"""
            mgr._rbac_guard("mark_task_done", task_id)
            if mgr.task_repo is None:
                raise RuntimeError("mark_task_done 需要注入 task_repo，当前为 None")
            updated = mgr.task_repo.transition(task_id, TaskStatus.COMPLETED, session_id=worker_id or None)
            if mgr.docs_dir:
                mgr._sync_md(updated)
            return mgr._to_response(updated)

        @mcp.tool(name="task_manager.mark_task_failed")
        async def mark_task_failed(task_id: str, reason: str = "", worker_id: str = "") -> dict:
            """标记任务失败——调用状态机 transition(task_id, FAILED)，reason 须包含"根因"关键词"""
            mgr._rbac_guard("mark_task_failed", task_id)
            if mgr.task_repo is None:
                raise RuntimeError("mark_task_failed 需要注入 task_repo，当前为 None")
            updated = mgr.task_repo.transition(task_id, TaskStatus.FAILED, note=reason, session_id=worker_id or None)
            if mgr.docs_dir:
                mgr._sync_md(updated)
            return mgr._to_response(updated)

        @mcp.tool(name="task_manager.batch_progress")
        async def batch_progress_tool(batch_id: str) -> dict:
            """查询批量进度——READY/IN_PROGRESS/COMPLETED/FAILED 各多少"""
            mgr._rbac_guard("batch_progress")
            if mgr.task_repo is None:
                raise RuntimeError("batch_progress 需要注入 task_repo，当前为 None")
            return mgr.task_repo.batch_progress(batch_id)

        @mcp.tool(name="task_manager.list_dependents")
        async def list_dependents(task_id: str) -> dict:
            """查询所有依赖指定 task_id 的下游任务（MOD-TASK_SYSTEM §16.7 依赖感知）"""
            mgr._rbac_guard("list_dependents", task_id)
            if mgr.task_repo is None:
                raise RuntimeError("list_dependents 需要注入 task_repo，当前为 None")
            downstream = mgr.task_repo.list_by_dependency(task_id)
            items = [mgr._to_response(t) for t in downstream]
            return {"task_id": task_id, "dependents": items, "count": len(items)}

        @mcp.tool(name="task_manager.auto_split")
        async def auto_split_task(
            task_id: str,
            split_strategy: str = "auto",
            session_id: str = "",
        ) -> dict:
            """将超粒度任务卡自动拆分为多张原子卡（GOV-TASK-001 §6 一卡一任务）。

            拆分策略：auto（按违规维度自动选择）/ by_deliverable / by_file / by_acceptance / by_target。
            拆分后原卡 CANCELLED，子卡自动建立依赖链。
            """
            mgr._rbac_guard("auto_split", task_id)
            if mgr.task_repo is None:
                raise RuntimeError("auto_split 需要注入 task_repo，当前为 None")
            sub_cards = mgr.task_repo.auto_split_task(
                task_id,
                session_id=session_id or None,
                split_strategy=split_strategy,
            )
            if not sub_cards:
                original = mgr.task_repo.get(task_id)
                if original:
                    violations = mgr.task_repo._validate_granularity(original)
                    if not violations:
                        return {"task_id": task_id, "action": "no_split_needed", "reason": "任务卡粒度合规，无需拆分"}
                    return {"task_id": task_id, "action": "split_failed", "reason": f"违规但拆分失败: {violations}"}
                return {"task_id": task_id, "action": "not_found", "reason": "任务不存在"}
            items = [mgr._to_response(c) for c in sub_cards]
            return {
                "task_id": task_id,
                "action": "split",
                "sub_task_ids": [c.task_id for c in sub_cards],
                "sub_tasks": items,
                "count": len(sub_cards),
                "strategy": split_strategy,
            }

        @mcp.tool(name="task_manager.write_draft")
        async def write_draft(session_id: str, file_path: str, content: str) -> dict:
            """写草稿到 .aidrafts/{session_id}/{file_path}——不获取排他锁"""
            mgr._rbac_guard("write_draft")
            _mod = importlib.import_module("zephyr.trading.staging_area")
            StagingArea = _mod.StagingArea
            sa = StagingArea(project_root=str(REPO_ROOT))
            draft_path = sa.write_draft(session_id, file_path, content)
            return {"status": "draft_written", "draft_path": str(draft_path), "file_path": file_path}

        @mcp.tool(name="task_manager.commit_draft")
        async def commit_draft(session_id: str, file_path: str, auto_merge: bool = True) -> dict:
            """提交草稿到最终位置——提交时获取排他锁+冲突检测"""
            mgr._rbac_guard("commit_draft")
            _mod = importlib.import_module("zephyr.trading.staging_area")
            StagingArea = _mod.StagingArea
            sa = StagingArea(project_root=str(REPO_ROOT))
            if auto_merge:
                result = sa.try_auto_merge(session_id, file_path)
            else:
                result = sa.commit(session_id, file_path)
            resp: dict = {"status": result.status.value, "file_path": result.file_path, "message": result.message}
            if result.conflict:
                resp["conflict"] = {
                    "draft_mtime": result.conflict.draft_mtime,
                    "current_mtime": result.conflict.current_mtime,
                    "diff_lines": result.conflict.diff_lines[:20],
                }
            return resp

        @mcp.tool(name="task_manager.list_drafts")
        async def list_drafts(session_id: str) -> dict:
            """列出当前会话的所有草稿"""
            mgr._rbac_guard("list_drafts")
            _mod = importlib.import_module("zephyr.trading.staging_area")
            StagingArea = _mod.StagingArea
            sa = StagingArea(project_root=str(REPO_ROOT))
            drafts = sa.list_drafts(session_id)
            return {"session_id": session_id, "drafts": drafts, "count": len(drafts)}

        @mcp.tool(name="task_manager.discard_draft")
        async def discard_draft(session_id: str, file_path: str) -> dict:
            """丢弃草稿"""
            mgr._rbac_guard("discard_draft")
            _mod = importlib.import_module("zephyr.trading.staging_area")
            StagingArea = _mod.StagingArea
            sa = StagingArea(project_root=str(REPO_ROOT))
            ok = sa.discard(session_id, file_path)
            return {"status": "discarded" if ok else "not_found", "file_path": file_path}

    def _next_seq(self, namespace: TaskNamespace) -> int:
        _mod = importlib.import_module("zephyr.governance.rule_enforcement.task_types")
        TaskNamespace = _mod.TaskNamespace

        if self.task_repo:
            return self.task_repo.next_seq(namespace)
        self._global_seq += 1
        return self._global_seq

    def _persist(self, tc: TaskCard) -> None:
        if self.task_repo is None:
            raise RuntimeError(
                f"MCP _persist 失败: task_id={tc.task_id} — task_repo 未注入，"
                f"数据将丢失。请确保 TaskManagerMCP(task_repo=...) 正确初始化。"
            )
        try:
            existing = self.task_repo.get(tc.task_id)
            if existing:
                existing.status = tc.status
                existing.updated_at = tc.updated_at
                self.task_repo.update(existing)
            else:
                self.task_repo.create(tc)
        except Exception as exc:
            raise RuntimeError(f"MCP _persist 失败: task_id={tc.task_id} — {type(exc).__name__}: {exc}") from exc

        if self.docs_dir:
            self._sync_md(tc)

    def _sync_md(self, tc: TaskCard) -> None:
        md_dir = self.docs_dir / "tasks"
        md_dir.mkdir(parents=True, exist_ok=True)
        md_path = md_dir / f"{tc.task_id}.md"
        md_content = _taskcard_to_md(tc)
        md_path.write_text(md_content, encoding="utf-8")

    def _load(self, task_id: str) -> TaskCard | None:
        if self.task_repo is None:
            raise RuntimeError(
                f"MCP _load 失败: task_id={task_id} — task_repo 未注入，"
                f"无法查询任务。请确保 TaskManagerMCP(task_repo=...) 正确初始化。"
            )
        try:
            return self.task_repo.get(task_id)
        except Exception as exc:
            raise RuntimeError(f"MCP _load 失败: task_id={task_id} — {type(exc).__name__}: {exc}") from exc

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
        self.mcp.run(transport="stdio")


_TRIAGE_TITLE_PATTERN = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def _extract_triage_profile(content: str, task_id: str) -> dict:
    profile: dict = {"title": task_id, "description": content[:50000]}
    title_match = _TRIAGE_TITLE_PATTERN.search(content)
    if title_match:
        profile["title"] = title_match.group(1).strip()
        body = content[title_match.end() :].strip()
        if body:
            profile["description"] = body[:50000]
    return profile


_MD_KV_PATTERN = re.compile(r"^\*\*(.+?)\*\*[：:]\s*(.+)$")
_MD_LIST_ITEM = re.compile(r"^-\s+(.+)$")


def _parse_md_to_taskcard(content: str) -> TaskCard | None:
    yaml_fm = _extract_yaml_frontmatter(content)
    if yaml_fm:
        return _parse_yaml_frontmatter_to_taskcard(yaml_fm)

    return _parse_legacy_md_to_taskcard(content)


_YAML_FM_PATTERN = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def _extract_yaml_frontmatter(content: str) -> dict | None:
    m = _YAML_FM_PATTERN.match(content)
    if not m:
        return None
    raw_yaml = m.group(1).strip()
    if not raw_yaml:
        return None
    try:
        import yaml as _yaml

        fm = _yaml.safe_load(raw_yaml)
        if isinstance(fm, dict):
            return fm
    except Exception:
        pass
    return None


def _parse_yaml_frontmatter_to_taskcard(fm: dict) -> TaskCard:
    _mod = importlib.import_module("zephyr.governance.rule_enforcement.task_types")
    TaskNamespace = _mod.TaskNamespace
    normalize_execution_model = _mod.normalize_execution_model

    now = datetime.now(UTC)
    task_id = str(fm.get("task_id", ""))
    ns_str = str(fm.get("namespace", "CP"))
    ns = getattr(TaskNamespace, ns_str, TaskNamespace.CP) if ns_str else TaskNamespace.CP

    status_str = str(fm.get("status", "PENDING"))
    status = getattr(TaskStatus, status_str.upper(), TaskStatus.PENDING)

    priority_str = str(fm.get("priority", "P2"))
    priority = getattr(Priority, priority_str, Priority.P2)

    safety_str = str(fm.get("safety_level", "L"))
    safety_level = getattr(SafetyLevel, safety_str, SafetyLevel.L)

    classification_str = str(fm.get("classification", "internal"))
    classification = getattr(
        __import__("zephyr.shared.schemas", fromlist=["Classification"]).Classification,
        classification_str.upper(),
        __import__("zephyr.shared.schemas", fromlist=["Classification"]).Classification.INTERNAL,
    )

    evolution_str = str(fm.get("evolution_policy", "extendable"))
    evolution_policy = getattr(
        __import__("zephyr.shared.schemas", fromlist=["EvolutionPolicy"]).EvolutionPolicy,
        evolution_str.upper(),
        __import__("zephyr.shared.schemas", fromlist=["EvolutionPolicy"]).EvolutionPolicy.EXTENDABLE,
    )

    upstream_files = _normalize_str_list(fm.get("upstream_files", []))
    downstream_outputs = _normalize_downstream_outputs(fm.get("downstream_outputs", []))
    allowed_touch = _normalize_str_list(fm.get("allowed_touch", []))
    forbidden_touch = _normalize_str_list(fm.get("forbidden_touch", []))
    applicable_rules = _normalize_dict_list(fm.get("applicable_rules", []), {"module_id", "section", "reason"})
    context_assembly = _normalize_dict_list(fm.get("context_assembly_manifest", []), {"file_path", "reason"})

    execution_model_raw = fm.get("execution_model") or fm.get("assigned_model", "deepseek")

    phase = int(fm.get("phase", 1))
    estimated_tokens = int(fm.get("estimated_tokens", 8000))
    timeout_minutes = int(fm.get("timeout_minutes", 30))
    estimate_hours = float(fm.get("estimate_hours", 0.0))
    seq = int(fm.get("seq", 0) or 0) or 1

    acceptance = _normalize_str_list(fm.get("acceptance_criteria") or fm.get("acceptance", []))
    depends_on = _normalize_str_list(fm.get("depends_on", []))
    blocked_by = _normalize_str_list(fm.get("blocked_by", []))
    deliverables = [
        item.get("path", item.get("description", str(item))) if isinstance(item, dict) else str(item)
        for item in downstream_outputs
    ]
    files_in_scope = _normalize_str_list(fm.get("files_in_scope", []))

    tags = _merge_tags(
        fn=_normalize_str_list(fm.get("tags_fn", [])),
        ly=fm.get("tags_ly", ""),
        md=fm.get("tags_md", ""),
        st=fm.get("tags_st", ""),
        mo=_normalize_str_list(fm.get("tags_mo", [])),
        extra=_normalize_str_list(fm.get("tags", [])),
    )

    source_blueprint = str(fm.get("source_blueprint", "unknown"))
    source_section = str(fm.get("source_section", "unknown"))
    title_text = str(fm.get("title", task_id or "Untitled"))
    description = str(fm.get("description", title_text))

    created_at_str = fm.get("created_at")
    created_at = _parse_time(str(created_at_str)) if created_at_str else now
    updated_at_str = fm.get("updated_at")
    updated_at = _parse_time(str(updated_at_str)) if updated_at_str else now

    completed_gates_raw = fm.get("completed_gates", [])
    gates_list = [GateLevel(g) for g in completed_gates_raw if isinstance(g, str) and g in GateLevel.__members__]
    blocked_gates_raw = fm.get("blocked_gates", {})
    blocked_gates = blocked_gates_raw if isinstance(blocked_gates_raw, dict) else {}

    return TaskCard(
        task_id=task_id,
        namespace=ns,
        seq=seq,
        title=title_text,
        status=status,
        priority=priority,
        phase=phase,
        execution_model=normalize_execution_model(str(execution_model_raw)),
        safety_level=safety_level,
        classification=classification,
        evolution_policy=evolution_policy,
        estimate_hours=estimate_hours,
        source_blueprint=source_blueprint,
        source_section=source_section,
        description=description,
        files_in_scope=files_in_scope,
        deliverables=deliverables,
        acceptance=acceptance,
        depends_on=depends_on,
        tags=tags,
        upstream_files=upstream_files,
        downstream_outputs=downstream_outputs,
        allowed_touch=allowed_touch,
        forbidden_touch=forbidden_touch,
        applicable_rules=applicable_rules,
        context_assembly_manifest=context_assembly,
        rollback_instructions=str(fm.get("rollback_instructions", "")),
        estimated_tokens=estimated_tokens,
        timeout_minutes=timeout_minutes,
        completed_gates=gates_list,
        blocked_gates=blocked_gates,
        assigned_pipeline=str(fm.get("assigned_pipeline", "A")),
        pipeline_modules=_normalize_str_list(fm.get("pipeline_modules", [])),
        blocked_by=blocked_by,
        artifact_paths=_normalize_str_list(fm.get("artifact_paths", [])),
        ai_autonomy_level=str(fm.get("ai_autonomy_level", "supervised")),
        pipeline_task_type=fm.get("pipeline_task_type"),
        target_layer=fm.get("target_layer"),
        created_at=created_at,
        updated_at=updated_at,
    )


def _normalize_str_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _normalize_dict_list(value: object, known_keys: set[str]) -> list[dict]:
    if not isinstance(value, list):
        return []
    result: list[dict] = []
    for item in value:
        if isinstance(item, dict):
            result.append(item)
        elif isinstance(item, str) and item.strip():
            result.append({"source": item.strip()})
    return result


def _normalize_downstream_outputs(value: object) -> list[dict]:
    if not isinstance(value, list):
        return []
    result: list[dict] = []
    for item in value:
        if isinstance(item, dict):
            result.append(item)
        elif isinstance(item, str):
            if " — " in item:
                path_part, desc_part = item.split(" — ", 1)
                result.append({"path": path_part.strip(), "description": desc_part.strip()})
            else:
                result.append({"path": item.strip(), "description": ""})
    return result


def _merge_tags(*, fn: list[str], ly: str, md: str, st: str, mo: list[str], extra: list[str]) -> list[str]:
    merged: list[str] = list(extra)
    merged.extend(f"fn:{t}" for t in fn if t)
    if ly:
        merged.append(f"ly:{ly}")
    if md:
        merged.append(f"md:{md}")
    if st:
        merged.append(f"st:{st}")
    merged.extend(f"mo:{t}" for t in mo if t)
    return merged


def _split_tags(tags: list[str]) -> dict[str, object]:
    fn: list[str] = []
    ly = ""
    md_tag = ""
    st = ""
    mo: list[str] = []
    extra: list[str] = []
    for tag in tags:
        tag_str = str(tag)
        if tag_str.startswith("fn:"):
            fn.append(tag_str[3:])
        elif tag_str.startswith("ly:"):
            ly = tag_str[3:]
        elif tag_str.startswith("md:"):
            md_tag = tag_str[3:]
        elif tag_str.startswith("st:"):
            st = tag_str[3:]
        elif tag_str.startswith("mo:"):
            mo.append(tag_str[3:])
        elif tag_str.startswith("orig:") or tag_str.startswith("module:"):
            extra.append(tag_str)
        else:
            extra.append(tag_str)
    return {"tags_fn": fn, "tags_ly": ly, "tags_md": md_tag, "tags_st": st, "tags_mo": mo, "tags": extra}


def _parse_legacy_md_to_taskcard(content: str) -> TaskCard | None:
    _mod = importlib.import_module("zephyr.governance.rule_enforcement.task_types")
    TaskNamespace = _mod.TaskNamespace
    normalize_execution_model = _mod.normalize_execution_model

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

        if section in ("描述", "目标"):
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

        if section in ("门禁", "门禁状态"):
            gm = re.search(r"已通过:\s*\[(.*?)\]", line)
            if gm:
                gates_str = gm.group(1).strip()
                if gates_str:
                    completed_gates = [g.strip().strip("'\"") for g in gates_str.split(",") if g.strip()]
            bm = re.search(r"阻塞:\s*(.+)$", line)
            if bm:
                try:
                    # 5.147.7 修复: 原 json.loads(text.replace("'", '"')) 启发式解析 Python-repr 为 JSON,
                    # 若门禁名称含撇号会破坏字符串边界。改用 ast.literal_eval 安全解析 Python 字面量
                    import ast

                    blocked_gates = ast.literal_eval(bm.group(1).strip())
                except (ValueError, SyntaxError):
                    pass
            continue

        if section == "时间":
            tm = re.match(r"^-\s*(创建|更新)[：:]\s*(.+)$", line)
            if tm:
                key = tm.group(1).strip()
                val = tm.group(2).strip()
                if key == "创建":
                    created_at_str = val
                elif key == "更新":
                    updated_at_str = val
            continue

        if not section or section in ("描述", "目标"):
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

    priority_str = kv.get("优先级", Priority.P2.value)
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
        execution_model=normalize_execution_model(str(execution_model)),
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
    created = (
        tc.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(tc.created_at, "strftime") else str(tc.created_at)[:16]
    )
    updated = (
        tc.updated_at.strftime("%Y-%m-%d %H:%M") if hasattr(tc.updated_at, "strftime") else str(tc.updated_at)[:16]
    )

    tag_parts = _split_tags(tc.tags)

    def _yaml_list(items: list, indent: int = 2) -> str:
        if not items:
            return " []"
        prefix = " " * indent
        lines = []
        for item in items:
            if isinstance(item, dict):
                lines.append(f'{prefix}- path: "{item.get("path", "")}"')
                if item.get("description"):
                    lines.append(f'{prefix}  description: "{item.get("description", "")}"')
            else:
                lines.append(f'{prefix}- "{item}"')
        return "\n" + "\n".join(lines)

    def _yaml_rule_list(items: list[dict], indent: int = 2) -> str:
        if not items:
            return " []"
        prefix = " " * indent
        lines = []
        for item in items:
            if isinstance(item, dict):
                lines.append(f'{prefix}- module_id: "{item.get("module_id", "")}"')
                lines.append(f'{prefix}  section: "{item.get("section", "")}"')
                lines.append(f'{prefix}  reason: "{item.get("reason", "")}"')
        return "\n" + "\n".join(lines)

    def _yaml_context_list(items: list[dict], indent: int = 2) -> str:
        if not items:
            return " []"
        prefix = " " * indent
        lines = []
        for item in items:
            if isinstance(item, dict):
                lines.append(f'{prefix}- file_path: "{item.get("file_path", "")}"')
                lines.append(f'{prefix}  reason: "{item.get("reason", "")}"')
        return "\n" + "\n".join(lines)

    gates_str = ", ".join(f"'{g.value}'" for g in tc.completed_gates) if tc.completed_gates else ""

    yaml_block = f"""---
task_id: "{tc.task_id}"
source_blueprint: "{tc.source_blueprint}"
source_section: "{tc.source_section}"
title: "{tc.title}"
description: "{tc.description[:50000]}"
priority: "{tc.priority.value}"
upstream_files:{_yaml_list(tc.upstream_files)}
downstream_outputs:{_yaml_list(tc.downstream_outputs)}
allowed_touch:{_yaml_list(tc.allowed_touch)}
forbidden_touch:{_yaml_list(tc.forbidden_touch)}
applicable_rules:{_yaml_rule_list(tc.applicable_rules)}
context_assembly_manifest:{_yaml_context_list(tc.context_assembly_manifest)}
assigned_model: "{tc.execution_model.value if hasattr(tc.execution_model, "value") else tc.execution_model}"
assigned_pipeline: "{tc.assigned_pipeline}"
pipeline_modules:{_yaml_list(tc.pipeline_modules)}
pipeline_task_type: "{tc.pipeline_task_type or ''}"
target_layer: "{tc.target_layer or ''}"
estimated_tokens: {tc.estimated_tokens}
timeout_minutes: {tc.timeout_minutes}
acceptance_criteria:{_yaml_list(tc.acceptance)}
rollback_instructions: "{tc.rollback_instructions}"
depends_on:{_yaml_list(tc.depends_on)}
blocked_by:{_yaml_list(tc.blocked_by)}
status: "{tc.status.value if hasattr(tc.status, "value") else tc.status}"
tags_fn:{_yaml_list(tag_parts.get("tags_fn", []))}
tags_ly: "{tag_parts.get("tags_ly", "")}"
tags_md: "{tag_parts.get("tags_md", "")}"
tags_st: "{tag_parts.get("tags_st", "")}"
tags_mo:{_yaml_list(tag_parts.get("tags_mo", []))}
completed_gates: [{gates_str}]
blocked_gates: {json.dumps(tc.blocked_gates, ensure_ascii=False)}
artifact_paths:{_yaml_list(tc.artifact_paths)}
audit_findings:{
        _yaml_list(
            [
                {
                    "finding_id": f.finding_id,
                    "dimension": f.dimension,
                    "severity": f.severity,
                    "description": f.description,
                }
                for f in tc.audit_findings
            ]
            if tc.audit_findings
            else []
        )
    }
ke_entries:{_yaml_list(tc.ke_entries)}
ai_autonomy_level: "{tc.ai_autonomy_level}"
autonomy_checklist:{_yaml_list(tc.autonomy_checklist)}
---

# {tc.title}

## 目标
{tc.description}

## 触发条件
{chr(10).join(f"- {dep}" for dep in tc.depends_on) if tc.depends_on else "- 无前置依赖"}

## 执行步骤

### 读
{chr(10).join(f"- {f}" for f in tc.upstream_files) if tc.upstream_files else "-（见 upstream_files）"}

### 做
{chr(10).join(f"- {m}" for m in tc.pipeline_modules) if tc.pipeline_modules else "- 按管线模块执行"}

### 产
{
        chr(10).join(
            f"- {d.get('path', str(d))} — {d.get('description', '')}" if isinstance(d, dict) else f"- {d}"
            for d in tc.downstream_outputs
        )
        if tc.downstream_outputs
        else "-（见 downstream_outputs）"
    }

### 检
- 运行对应测试套件
- 门禁 G5 完成验证

## 验收标准
{chr(10).join(f"- {a}" for a in tc.acceptance) if tc.acceptance else "- 见 acceptance_criteria"}

## 风险与缓解
| 风险 | 缓解 |
|------|------|
| 回滚 | {tc.rollback_instructions if tc.rollback_instructions else "无特定回滚方案"} |

---
*创建: {created} | 更新: {updated}*
*本文件由 MOD-TASK_SYSTEM task_manager_server 自动同步生成。*"""

    return yaml_block
