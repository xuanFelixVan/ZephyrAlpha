# [BLUEPRINT] MOD-INF-035 | 03_modules/_cross_layer/auto-runtime-core/blueprint.md | §

# [MODULE] zephyr.runtime.boot_hooks

# [INVARIANTS] register_boot_hooks is idempotent; hook_registry deduplicates by name

# [MODIFY-GUARD] none

# [CONSUMERS] zephyr.runtime.auto_runtime_core

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] returns None; logs warning on failure; never raises

# [TESTS]

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def register_boot_hooks() -> None:
    try:
        from zephyr.hooks.event_hook import hook_registry

        def _on_task_completed(event: object) -> None:
            try:
                from zephyr.db.task_repo import TaskRepository
                tr = TaskRepository()
                task = tr.get(getattr(event, "task_id", ""))
                if task and task.get("depends_on"):
                    for dep_id in task["depends_on"]:
                        dep = tr.get(dep_id)
                        if dep and dep.get("status") == "BLOCKED":
                            tr.transition(dep_id, "PENDING", note=f"unblocked by {task['task_id']}")
            except Exception:
                pass

        def _on_task_failed(event: object) -> None:
            try:
                from zephyr.db.task_repo import TaskRepository
                tr = TaskRepository()
                task = tr.get(getattr(event, "task_id", ""))
                if task and task.get("retry_count", 0) < 3:
                    tr.transition(
                        getattr(event, "task_id", ""),
                        "RETRY",
                        note=f"auto-retry from hook (attempt {task.get('retry_count', 0) + 1})",
                    )
            except Exception:
                pass

        def _on_task_verified_triple_align(event: object) -> None:
            try:
                from zephyr.gates.triple_alignment import check_triple_alignment
                task_id = getattr(event, "task_id", "")
                source_bp = ""
                try:
                    from zephyr.db.task_repo import TaskRepository
                    tr = TaskRepository()
                    task = tr.get(task_id)
                    source_bp = task.get("source_blueprint", "") if task else ""
                except Exception:
                    pass
                if not source_bp:
                    return
                result = check_triple_alignment(specific_module=source_bp, warn_only=False)
                if not result.passed:
                    logger.error(
                        "G-TRIPLE-ALIGN FAILED after task %s verified: module %s has %d violations",
                        task_id, source_bp,
                        len([v for v in result.violations if v.severity.value == "ERROR"]),
                    )
            except Exception:
                pass

        hook_registry.register(_on_task_completed, priority=50, name="auto_unblock_dependents")
        hook_registry.register(_on_task_failed, priority=60, name="auto_retry_on_failure")
        hook_registry.register(_on_task_verified_triple_align, priority=70, name="triple_alignment_on_verified")
        logger.info("Task system hooks registered: auto_unblock_dependents / auto_retry_on_failure / triple_alignment_on_verified")
    except Exception as e:
        logger.warning("Failed to register task system hooks: %s", e)
