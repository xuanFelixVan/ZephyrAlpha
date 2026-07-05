# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.auto_dispatcher
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.__init__; zephyr.shared.contracts.task_repository_protocol; zephyr.governance.persistence.task_repo
# [CONSUMERS] zephyr.trading.ide_health_service
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_auto_dispatcher | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
AutoDispatcher — 守护进程内的轻量 PipelineDispatcher
=====================================================
实现 PipelineDispatcher Protocol，供 TaskQueue 在守护进程中自动调度 READY 任务。

流程:
    TaskQueue._tick() → transition(READY→IN_PROGRESS) → dispatch(task_card)
        ├── ContextBridge.request_context()     → CE→LSG + CE→VMS 自动触发
        ├── ScriptRunner.run_audit()            → Script→Gate + Script→KB 自动触发
        └── transition(IN_PROGRESS→COMPLETED)   → Orc→VMS + KB→VMS hook 自动触发
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zephyr.trading.orchestrator.core.task_queue import TaskCard

logger = logging.getLogger("zephyr.auto_dispatcher")


class AutoDispatcher:
    """轻量 PipelineDispatcher — 执行 TaskCard 并触发整条基础设施管道。"""

    def dispatch(self, task_card: TaskCard) -> dict:
        task_id = getattr(task_card, "task_id", str(task_card))
        logger.info("[AUTO-DISPATCH] dispatching task=%s", task_id)

        files_in_scope = getattr(task_card, "files_in_scope", []) or []
        if isinstance(files_in_scope, str):
            import json

            try:
                files_in_scope = json.loads(files_in_scope)
            except (json.JSONDecodeError, TypeError):
                files_in_scope = [files_in_scope]

        session_id = getattr(task_card, "session_id", None) or "auto"

        result = {
            "task_id": task_id,
            "step_context": "skipped",
            "step_scripts": "skipped",
            "step_gate": "skipped",
            "step_kb": "skipped",
        }

        try:
            from zephyr.trading.orchestrator.execution.context_bridge import ContextBridge

            bridge = ContextBridge()
            bridge.request_context(task_id=task_id, session_id=session_id)
            result["step_context"] = "ok"
            logger.info("[AUTO-DISPATCH] context built for %s", task_id)
        except Exception as exc:
            logger.warning("[AUTO-DISPATCH] context failed for %s: %s", task_id, exc)
            result["step_context"] = f"failed: {exc}"

        if files_in_scope:
            try:
                from zephyr.trading.orchestrator.execution.script_runner import ScriptRunner

                runner = ScriptRunner()
                audit_result = runner.run_audit(task_id, files_in_scope)
                result["step_scripts"] = f"ok (passed={audit_result.passed} failed={audit_result.failed})"
                result["step_gate"] = "embedded"
                result["step_kb"] = "embedded"
                logger.info(
                    "[AUTO-DISPATCH] audit done for %s: passed=%d failed=%d",
                    task_id,
                    audit_result.passed,
                    audit_result.failed,
                )
            except Exception as exc:
                logger.warning("[AUTO-DISPATCH] audit failed for %s: %s", task_id, exc)
                result["step_scripts"] = f"failed: {exc}"
        else:
            logger.info("[AUTO-DISPATCH] no files_in_scope for %s, skipping audit", task_id)

        try:
            from zephyr.governance.persistence.task_repo import TaskRepository

            repo = TaskRepository()
            repo.transition(task_id, "COMPLETED", note="auto-dispatched by daemon")
            result["step_transition"] = "ok (→COMPLETED)"
        except Exception as exc:
            logger.warning("[AUTO-DISPATCH] transition failed for %s: %s", task_id, exc)
            result["step_transition"] = f"failed: {exc}"

        return result
