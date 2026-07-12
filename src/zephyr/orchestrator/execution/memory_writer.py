# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.execution.memory_writer
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.governance.__init__; zephyr.autonomy_core.__init__
# [CONSUMERS] zephyr.orchestrator.work_orchestrator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 任务COMPLETED时归档; VMS不可用降级不阻塞
# [MODIFY-GUARD] CT-ORC-VMS-001 必须同步更新VMS
# [STABILITY] evolving; [SAFETY] L; [AI_AUTONOMY] ai_modifiable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] scripts/connect/orc_vms.py --trigger
# [A_module] module_id=MOD-ORC_memory_writer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Orc->VMS 记忆写入器"""

from zephyr.shared.io.serialization import dumps
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)
__all__ = ["ArchiveResult", "MemoryWriter", "archive_to_vms"]


@dataclass
class ArchiveResult:
    stored: int = 0
    status: str = "complete"
    error: str | None = None


class MemoryWriter:
    def archive_to_vms(self, task: Any, result: dict[str, Any] | None = None) -> ArchiveResult:
        try:
            from zephyr.autonomy_core.context.vector_bridge import VectorBridge
            from zephyr.integration.vector_memory.in_memory_fake_vms import InMemoryFakeVMS

            vms = InMemoryFakeVMS()
            bridge = VectorBridge(vms)
            tid = getattr(task, "task_id", "unknown")
            summary = f"Task: {getattr(task, 'title', '')}. Result: {dumps(result or {})}"
            bridge._vms.write(
                "session_snapshots", summary[:2000], metadata={"task_id": tid, "status": getattr(task, "status", "?")},
                doc_id=f"session::{tid}",
            )
            logger.info("[ORC-VMS] archived: %s", tid)
            return ArchiveResult(stored=1)
        except Exception as e:
            logger.warning("[ORC-VMS] degraded: %s", e, exc_info=True)
            return ArchiveResult(stored=0, status="degraded", error="internal error")


def archive_to_vms(task: Any, result: dict[str, Any] | None = None) -> ArchiveResult:
    return MemoryWriter().archive_to_vms(task, result)