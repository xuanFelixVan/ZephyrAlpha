# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | CT-ORC-CE-001
# [MODULE] zephyr.orchestrator.execution.context_bridge
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS] zephyr.orchestrator.agent_orchestrator; zephyr.orchestrator.work_orchestrator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] request_context 幂等; 异步模式: 发送后立即返回pending; CE不可用时降级不阻塞任务
# [MODIFY-GUARD] CT-ORC-CE-001 协议变更必须同步更新context_engine/task_context_builder
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError CE不可用返回degraded; 空task返回None
# [TESTS] scripts/connect/orc_ce.py --trigger
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Orc->CE 上下文桥接 — request_context() 生产者

CT-ORC-CE-001: 任务启动时向 Context Engine 请求构建执行上下文。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: task 参数
#   fields: 参数 task，类型注解 object
#   code: context_bridge.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: task_type 参数
#   fields: 参数 task_type（无注解）
#   code: context_bridge.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: session_id 参数
#   fields: 参数 session_id（无注解）
#   code: context_bridge.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ContextResponse
#   name_en: ContextResponse
#   intro: class ContextResponse 源码 L89-L114
#   desc: 公共方法（定义序）: to_dict；源码 L89-L114
#   inputs: task_id blocks total_tokens status build_stages error
#   outputs: 返回值
# - id: A2
#   name_zh: ② ContextBridge
#   name_en: ContextBridge
#   intro: class ContextBridge 源码 L117-L161
#   desc: 公共方法（定义序）: request_context；源码 L117-L161
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ request_context
#   name_en: request_context
#   intro: request_context(task, task_type, session_id) 源码 L190-L191
#   desc: 源码 L190-L191
#   inputs: task task_type session_id
#   outputs: ContextResponse
# 层: 输出
# - id: O1
#   name_zh: ContextResponse
#   name_en: ContextResponse
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.orchestrator.agent_orchestrator; zephyr.orchestrator.work_orchestrator
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
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
    def request_context(self, task: object, *, task_type: str | None = None, session_id: str = "") -> ContextResponse:
        task_id = getattr(task, "task_id", "unknown")
        t_type = task_type or _infer_type(task)
        t_blueprint = getattr(task, "source_blueprint", "")
        t_files = getattr(task, "files_in_scope", [])
        if isinstance(t_files, str):
            import json

            try:
                t_files = json.loads(t_files)
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                t_files = []

        try:
            from zephyr.orchestrator.execution.task_context_builder import TaskContextBuilder

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
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("[ORC-CE] CE unavailable, degraded: %s", exc, exc_info=True)
            return ContextResponse(
                task_id=task_id,
                status="degraded",
                error=str(exc),
            )

    def _vectorize_context(self, response: ContextResponse) -> None:
        try:
            from zephyr.integration.vector_memory.vector_writer import vectorize_context

            vectorize_context(response.task_id, response.blocks)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.debug("[CE-VMS] context vectorize skipped", exc_info=True)


def _infer_type(task: object) -> str:
    tags = getattr(task, "tags", "")
    if isinstance(tags, str):
        import json

        try:
            tags_list = json.loads(tags)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
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


def request_context(task: object, *, task_type: str | None = None, session_id: str = "") -> ContextResponse:
    return ContextBridge().request_context(task, task_type=task_type, session_id=session_id)
