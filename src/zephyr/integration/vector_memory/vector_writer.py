# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | CT-CE-VMS-001
# [MODULE] zephyr.integration.vector_memory.vector_writer
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.autonomy_core.task_context_builder
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] context构建完成后MUST调用vectorize_and_store; VMS不可用时不阻塞主流程; 写入计数精确
# [MODIFY-GUARD] CT-CE-VMS-001 协议变更必须同步更新vector_memory/context_ingest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] VMS不可用返回status=degraded+stored_count=0; 空blocks返回0
# [TESTS] scripts/connect/ce_vms.py --trigger
# [A_module] module_id=MOD-ORC_vector_writer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""CE 向量写入器 — vectorize_and_store() 生产者

CT-CE-VMS-001: Context Engine 构建完成后将上下文块向量化存储到 VMS。
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "VMSWriteResult",
    "VectorWriter",
    "vectorize_context",
]


@dataclass
class VMSWriteResult:
    stored_count: int = 0
    total_blocks: int = 0
    collection: str = ""
    status: str = "complete"
    write_duration_ms: int = 0
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "stored_count": self.stored_count,
            "total_blocks": self.total_blocks,
            "collection": self.collection,
            "status": self.status,
            "write_duration_ms": self.write_duration_ms,
            "error": self.error,
        }


class VectorWriter:
    def vectorize_and_store(
        self,
        blocks: list[dict[str, Any]],
        task_id: str = "",
        collection: str = "session_context",
        session_id: str = "",
    ) -> VMSWriteResult:
        if not blocks:
            return VMSWriteResult(total_blocks=0, collection=collection)

        t0 = time.perf_counter()

        try:
            from zephyr.integration.vector_memory.context_ingest import ingest_context

            records = self._blocks_to_records(blocks, task_id, session_id)
            count = ingest_context(records, collection, task_id, session_id)

            elapsed = round((time.perf_counter() - t0) * 1000)
            logger.info(
                "[CE-VMS] stored: task=%s collection=%s blocks=%d elapsed=%dms",
                task_id,
                collection,
                count,
                elapsed,
            )

            return VMSWriteResult(
                stored_count=count,
                total_blocks=len(blocks),
                collection=collection,
                status="complete",
                write_duration_ms=elapsed,
            )
        except Exception as exc:
            elapsed = round((time.perf_counter() - t0) * 1000)
            logger.warning("[CE-VMS] VMS unavailable, degraded: %s", exc, exc_info=True)
            return VMSWriteResult(
                stored_count=0,
                total_blocks=len(blocks),
                collection=collection,
                status="degraded",
                write_duration_ms=elapsed,
                error=str(exc),
            )

    def _blocks_to_records(
        self,
        blocks: list[dict[str, Any]],
        task_id: str,
        session_id: str,
    ) -> list[dict[str, Any]]:
        records = []
        for i, block in enumerate(blocks):
            records.append(
                {
                    "block_id": f"{task_id}-{i}",
                    "type": block.get("type", "unknown"),
                    "content": str(block.get("content", ""))[:2000],
                    "tokens": block.get("tokens", 0),
                    "source": block.get("source", ""),
                    "priority": block.get("priority", "optional"),
                    "task_id": task_id,
                    "session_id": session_id,
                }
            )
        return records


def vectorize_context(
    blocks: list[dict[str, Any]],
    task_id: str = "",
    collection: str = "session_context",
    session_id: str = "",
) -> VMSWriteResult:
    return VectorWriter().vectorize_and_store(blocks, task_id, collection, session_id)