# [A_module] module_id=MOD-ORC_memory_writer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-MASTER-001 | docs/03_modules/_domain-knowledge/vector-memory/blueprint.md
# [MODULE] zephyr.trading.orchestrator.memory_writer
# [INVARIANTS] 任务COMPLETED时归档; VMS不可用降级不阻塞
# [MODIFY-GUARD] CT-ORC-VMS-001 必须同步更新VMS
# [CONSUMERS] zephyr.trading.orchestrator.work_orchestrator
# [STABILITY] evolving; [SAFETY] L; [AI_AUTONOMY] ai_modifiable
# [TESTS] scripts/connect/orc_vms.py --trigger
# [ERROR_CONTRACT]
"""Orc→VMS 记忆写入器"""

import json
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
            from zephyr.autonomy_core.vector_bridge import VectorBridge
            from zephyr.governance.vector_memory.in_memory_fake_vms import InMemoryFakeVMS

            vms = InMemoryFakeVMS()
            bridge = VectorBridge(vms)
            tid = getattr(task, "task_id", "unknown")
            summary = f"Task: {getattr(task, 'title', '')}. Result: {json.dumps(result or {}, default=str)}"
            bridge._vms.write(
                "session_snapshots", summary[:2000], metadata={"task_id": tid, "status": getattr(task, "status", "?")}
            )
            logger.info("[ORC-VMS] archived: %s", tid)
            return ArchiveResult(stored=1)
        except Exception as e:
            logger.warning("[ORC-VMS] degraded: %s", e)
            return ArchiveResult(stored=0, status="degraded", error=str(e))


def archive_to_vms(task: Any, result: dict[str, Any] | None = None) -> ArchiveResult:
    return MemoryWriter().archive_to_vms(task, result)
