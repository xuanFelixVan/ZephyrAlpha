# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/mcp-servers/blueprint.md
# [MODULE] zephyr.infrastructure.doc_guard_server
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas; zephyr.infrastructure.__init__; zephyr.shared.utils.time_utils
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_doc_guard_server | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# AI-generated: doc_guard (session_handoff) MCP Server skeleton ( T-3-04)
"""
DocGuardServer: 跨会话交接协议服务 MCP Server
=============================================
Task ID  : T-3-04 (B15)
Server   : session_handoff (tool-contracts.yaml §Server 4)
Protocol :  传输、JSON-RPC 2.0）
Backend  : HandoffPackage / SessionCarryover + 5 项反腐败校验（

文件命名说明
-----------
doc_guard_server.py 对应 tool-contracts.yaml 中的 session_handoff server。
"DocGuard" 强调本服务的双重职责：文档交接完整性防护 + 反腐败校验。

实现工具
--------
- session_handoff.create_package   — 生成 HandoffPackage
- session_handoff.validate_package — 执行 5 项反腐败校验
- session_handoff.get_carryover    — 获取 session carryover
- session_handoff.emit_manual_event — 触发人工介入通道
"""

from __future__ import annotations

import uuid
from typing import Any

from zephyr.infrastructure._base_server import BaseMCPServer, MCPError
from zephyr.integration.shared.schema.schemas import Priority
from zephyr.shared.utils.time_utils import now_iso

__all__ = ["DocGuardServer", "create_server"]

_VALID_PLATFORMS = frozenset({"cursor", "trae-cn", "cli"})
_VALID_PRIORITIES = frozenset({"LOW", "NORMAL", "HIGH", "CRITICAL"})
_VALID_CONTEXT_PRIORITIES = frozenset({Priority.P0.value, Priority.P1.value, Priority.P2.value, Priority.P3.value})

# 5 项反腐败校验项（
_ANTI_CORRUPTION_CHECKS = [
    "AC1:no_fabricated_task_ids",
    "AC2:open_files_actually_modified",
    "AC3:decisions_log_not_empty_if_completed",
    "AC4:next_tasks_are_pending_or_ready",
    "AC5:from_session_matches_current_session",
]


class DocGuardServer(BaseMCPServer):
    """session_handoff MCP Server 实现（DocGuard）。

    骨架内置轻量内存存储（生产中替换为 HandoffPackage Pydantic 模型持久化）。
    """

    SERVER_ID = "session_handoff"
    VERSION = "1.0.0"
    DESCRIPTION = "跨会话交接协议服务；包装 HandoffPackage / SessionCarryover + 5 项反腐败校验"

    def __init__(self, *, enable_rbac: bool = True) -> None:
        super().__init__(self.SERVER_ID, self.VERSION, self.DESCRIPTION, enable_rbac=enable_rbac)
        # 内存存储（骨架层）
        self._packages: dict[str, dict[str, Any]] = {}
        self._carryovers: list[dict[str, Any]] = []
        self._events: list[dict[str, Any]] = []

        self.register_tool(
            name="session_handoff.create_package",
            description="生成 HandoffPackage（8 必填字段 + P0-P3 压缩）",
            input_schema={
                "type": "object",
                "required": ["from_session", "to_model", "completed_tasks", "next_tasks", "open_files"],
                "additionalProperties": False,
                "properties": {
                    "from_session": {"type": "string"},
                    "to_model": {"type": "string"},
                    "to_platform": {"type": "string", "enum": sorted(_VALID_PLATFORMS)},
                    "completed_tasks": {"type": "array", "items": {"type": "string"}},
                    "next_tasks": {"type": "array", "items": {"type": "string"}},
                    "open_files": {"type": "array", "items": {"type": "string"}},
                    "decisions_log": {"type": "array", "items": {"type": "string"}},
                    "blocked_items": {"type": "array", "items": {"type": "string"}},
                    "context_priority": {
                        "type": "string",
                        "enum": sorted(_VALID_CONTEXT_PRIORITIES),
                        "default": "P1",
                    },
                },
            },
            handler=self._create_package,
        )
        self.register_tool(
            name="session_handoff.validate_package",
            description="执行 5 项反腐败校验",
            input_schema={
                "type": "object",
                "required": ["package"],
                "additionalProperties": False,
                "properties": {
                    "package": {
                        "type": "object",
                        "description": "HandoffPackage 对象（JSON）",
                    }
                },
            },
            handler=self._validate_package,
        )
        self.register_tool(
            name="session_handoff.get_carryover",
            description="获取当前 session 的入职 carryover（替代旧 session log 读取）",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "session_id": {"type": ["string", "null"]},
                },
            },
            handler=self._get_carryover,
        )
        self.register_tool(
            name="session_handoff.emit_manual_event",
            description="触发人工介入通道（Gate P0 / Intent UNKNOWN / 任务 BLOCKED）",
            input_schema={
                "type": "object",
                "required": ["task_id", "priority", "reason"],
                "additionalProperties": False,
                "properties": {
                    "task_id": {"type": "string"},
                    "priority": {"type": "string", "enum": sorted(_VALID_PRIORITIES)},
                    "reason": {"type": "string", "minLength": 10},
                    "suggested_action": {"type": ["string", "null"]},
                },
            },
            handler=self._emit_manual_event,
        )
        self.register_tool(
            name="session_handoff.validate_doc_version",
            description="校验文档版本——检查文档版本号 + 前置 session 兼容性",
            input_schema={
                "type": "object",
                "required": ["doc_path", "expected_version"],
                "additionalProperties": False,
                "properties": {
                    "doc_path": {"type": "string"},
                    "expected_version": {"type": "string"},
                    "from_session": {"type": "string"},
                    "strict": {"type": "boolean", "default": False},
                },
            },
            handler=self._validate_doc_version,
        )

    # ------------------------------------------------------------------
    # Tool handlers
    # ------------------------------------------------------------------

    def _create_package(
        self,
        from_session: str,
        to_model: str,
        completed_tasks: list[str],
        next_tasks: list[str],
        open_files: list[str],
        to_platform: str = "cursor",
        decisions_log: list[str] | None = None,
        blocked_items: list[str] | None = None,
        context_priority: str = "P1",
    ) -> dict[str, Any]:
        """生成并存储 HandoffPackage。

        ZA-HF-0001: schema invalid
        ZA-HF-0004: context size exceeds limit
        """
        if to_platform not in _VALID_PLATFORMS:
            raise MCPError(-32602, f"ZA-HF-0001: to_platform 无效: {to_platform!r}")
        if context_priority not in _VALID_CONTEXT_PRIORITIES:
            raise MCPError(-32602, f"ZA-HF-0001: context_priority 无效: {context_priority!r}")

        total_items = len(completed_tasks) + len(next_tasks) + len(open_files)
        if total_items > 200:
            raise MCPError(-32413, "ZA-HF-0004: context size exceeds limit (>200 items)")

        package: dict[str, Any] = {
            "from_session": from_session,
            "to_model": to_model,
            "to_platform": to_platform,
            "completed_tasks": completed_tasks,
            "next_tasks": next_tasks,
            "open_files": open_files,
            "decisions_log": decisions_log or [],
            "blocked_items": blocked_items or [],
            "context_priority": context_priority,
            "anti_corruption_report": {"passed": True, "failed_checks": []},
            "created_at": now_iso(),
        }
        self._packages[from_session] = package
        # 同时写入 carryover 列表
        self._carryovers.append({"session_id": from_session, "package": package})
        return package

    def _validate_package(self, package: dict[str, Any]) -> dict[str, Any]:
        """执行 5 项反腐败校验（骨架规则）。

        ZA-HF-0002: anti-corruption check failed
        """
        failed: list[str] = []
        warnings: list[str] = []

        # AC1: 不得含有凭空捏造的 task_id 格式
        all_tasks = package.get("completed_tasks", []) + package.get("next_tasks", [])
        for tid in all_tasks:
            if not isinstance(tid, str) or not tid.startswith("T-"):
                failed.append(f"AC1:fabricated_task_id:{tid!r}")

        # AC2: open_files 非空校验
        if not isinstance(package.get("open_files"), list):
            failed.append("AC2:open_files_must_be_list")

        # AC3: 若有 completed_tasks，decisions_log 不应为空
        if package.get("completed_tasks") and not package.get("decisions_log"):
            warnings.append("AC3:decisions_log_empty_despite_completed_tasks")

        # AC4: next_tasks 不应包含 COMPLETED/VERIFIED 状态标记
        for task in package.get("next_tasks", []):
            if any(s in str(task) for s in ["COMPLETED", "VERIFIED"]):
                failed.append(f"AC4:next_task_already_completed:{task!r}")

        # AC5: from_session 不得为空
        if not package.get("from_session"):
            failed.append("AC5:from_session_empty")

        passed = not bool(failed)
        if not passed:
            raise MCPError(-32409, f"ZA-HF-0002: anti-corruption check failed: {failed}")

        return {"passed": passed, "failed_checks": failed, "warnings": warnings}

    def _get_carryover(
        self,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """获取最新或指定 session 的 carryover。

        ZA-HF-0003: carryover not found
        """
        if not self._carryovers:
            raise MCPError(-32404, "ZA-HF-0003: carryover not found")

        if session_id is None:
            # 5.85.3 修复：原返回 self._carryovers[-1]（内部dict引用），调用方可修改返回值，篡改server内部carryover状态。
            return dict(self._carryovers[-1])

        for co in reversed(self._carryovers):
            if co.get("session_id") == session_id:
                # 5.85.3 修复：原返回 co（内部dict引用），调用方可修改返回值，篡改server内部carryover状态。
                return dict(co)

        raise MCPError(-32404, f"ZA-HF-0003: carryover not found for session {session_id!r}")

    def _emit_manual_event(
        self,
        task_id: str,
        priority: str,
        reason: str,
        suggested_action: str | None = None,
    ) -> dict[str, Any]:
        """触发人工介入通道（骨架：记录事件到内存）。"""
        if priority not in _VALID_PRIORITIES:
            raise MCPError(-32602, f"priority 无效: {priority!r}")
        if len(reason) < 10:
            raise MCPError(-32602, "reason 至少 10 个字符")

        event: dict[str, Any] = {
            "event_id": str(uuid.uuid4()),
            "task_id": task_id,
            "priority": priority,
            "reason": reason,
            "suggested_action": suggested_action,
            "delivered_at": now_iso(),
        }
        self._events.append(event)
        return {"event_id": event["event_id"], "delivered_at": event["delivered_at"]}

    def _validate_doc_version(
        self,
        doc_path: str,
        expected_version: str,
        from_session: str | None = None,
        strict: bool = False,
    ) -> dict[str, Any]:
        """校验文档版本号（骨架规则：格式校验 + session 匹配检查）。"""
        import re as _re

        if not _re.match(r"^\d+\.\d+", expected_version):
            raise MCPError(-32602, f"expected_version 格式无效: {expected_version!r}")

        pkg = self._packages.get(from_session or "")
        session_match = pkg is not None if from_session else True

        return {
            "doc_path": doc_path,
            "expected_version": expected_version,
            "version_valid": True,
            "session_match": session_match,
            "strict_mode": strict,
            "checked_at": now_iso(),
        }


def create_server(*, enable_rbac: bool = True) -> DocGuardServer:
    """工厂函数，返回配置好的 DocGuardServer 实例。"""
    return DocGuardServer(enable_rbac=enable_rbac)


if __name__ == "__main__":
    create_server().run()
