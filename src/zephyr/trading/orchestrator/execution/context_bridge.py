# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | CT-ORC-CE-001
# [MODULE] zephyr.trading.orchestrator.execution.context_bridge
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS] zephyr.trading.orchestrator.agent_orchestrator; zephyr.trading.orchestrator.work_orchestrator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] request_context 幂等; 异步模式: 发送后立即返回pending; CE不可用时降级不阻塞任务
# [MODIFY-GUARD] CT-ORC-CE-001 协议变更必须同步更新context_engine/task_context_builder
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError CE不可用返回degraded; 空task返回None
# [TESTS] scripts/connect/orc_ce.py --trigger
# [A_module] module_id=MOD-ORC_context_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Orc→CE 上下文桥接 — request_context() 生产者

CT-ORC-CE-001: 任务启动时向 Context Engine 请求构建执行上下文。
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "ContextBridge",
    "ContextResponse",
    "request_context",
]


class ContextResponse:
    def __init__(
        self,
        task_id: str,
        blocks: list[dict[str, Any]] | None = None,
        total_tokens: int = 0,
        status: str = "pending",
        build_stages: dict[str, float] | None = None,
        error: str | None = None,
    ):
        self.task_id = task_id
        self.blocks = blocks or []
        self.total_tokens = total_tokens
        self.status = status
        self.build_stages = build_stages or {}
        self.error = error

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "blocks": self.blocks,
            "total_tokens": self.total_tokens,
            "status": self.status,
            "build_stages": self.build_stages,
            "error": self.error,
        }


class ContextBridge:
    def request_context(self, task: Any, *, task_type: str | None = None, session_id: str = "") -> ContextResponse:
        task_id = getattr(task, "task_id", "unknown")
        t_type = task_type or _infer_type(task)
        t_blueprint = getattr(task, "source_blueprint", "")
        t_files = getattr(task, "files_in_scope", [])
        if isinstance(t_files, str):
            import json

            try:
                t_files = json.loads(t_files)
            except Exception:
                t_files = []

        try:
            from zephyr.trading.orchestrator.execution.task_context_builder import TaskContextBuilder

            builder = TaskContextBuilder()
            response = builder.build_from_task(
                task_id=task_id,
                task_type=t_type,
                blueprint_refs=[t_blueprint] if t_blueprint else [],
                file_context=t_files if isinstance(t_files, list) else [],
                max_tokens=8000,
                session_id=session_id,
            )

            self._vectorize_context(response)

            return response
        except Exception as exc:
            logger.warning("[ORC-CE] CE unavailable, degraded: %s", exc)
            return ContextResponse(
                task_id=task_id,
                status="degraded",
                error=str(exc),
            )

    def _vectorize_context(self, response: ContextResponse) -> None:
        try:
            from zephyr.integration.vector_memory.vector_writer import vectorize_context

            vectorize_context(response.task_id, response.blocks)
        except Exception:
            logger.debug("[CE-VMS] context vectorize skipped")


def _infer_type(task: Any) -> str:
    tags = getattr(task, "tags", "")
    if isinstance(tags, str):
        import json

        try:
            tags_list = json.loads(tags)
        except Exception:
            tags_list = []
    else:
        tags_list = tags if isinstance(tags, list) else []

    tag_str = " ".join(tags_list).lower()
    if "code" in tag_str or "construction" in tag_str:
        return "code_construction"
    if "audit" in tag_str:
        return "audit_execution"
    if "knowledge" in tag_str or "ke" in tag_str:
        return "knowledge_query"
    if "governance" in tag_str:
        return "governance_check"
    if "infra" in tag_str or "connect" in tag_str:
        return "infra_connect"
    return "code_construction"


def request_context(task: Any, *, task_type: str | None = None, session_id: str = "") -> ContextResponse:
    return ContextBridge().request_context(task, task_type=task_type, session_id=session_id)
