# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | CT-CE-VMS-001
# [MODULE] zephyr.integration.vector_memory.context_ingest
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.vector_memory.in_memory_fake_vms
# [CONSUMERS] zephyr.autonomy_core.vector_writer
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 批量写入ContextBlock records; VMS不可用时使用in-memory fallback; 写入计数精确
# [MODIFY-GUARD] CT-CE-VMS-001 协议变更必须同步更新context_engine/vector_writer
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] VMS不可用回退in-memory; 空records返回0
# [TESTS] scripts/connect/ce_vms.py --trigger
# [A_module] module_id=MOD-INT_context_ingest | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""VMS 上下文注入器 — ingest_context() 消费者

CT-CE-VMS-001: 接收 CE 投递的上下文块, 向量化存储到 ChromaDB（Current: in-memory fallback）。
"""

from __future__ import annotations

import importlib
import logging
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "ContextIngest",
    "ingest_context",
]

_in_memory_collections: dict[str, list[dict[str, Any]]] = {}


class ContextIngest:
    def ingest(
        self,
        records: list[dict[str, Any]],
        collection: str = "session_context",
        task_id: str = "",
        session_id: str = "",
    ) -> int:
        if not records:
            return 0

        try:
            _vb_mod = importlib.import_module("zephyr.autonomy_core.vector_bridge")
            _VectorBridge = _vb_mod.VectorBridge
            from zephyr.integration.vector_memory.in_memory_fake_vms import InMemoryFakeVMS

            vms = InMemoryFakeVMS()
            bridge = _VectorBridge(vms)

            mapped_collection = _map_collection(collection)
            stored = 0
            for rec in records:
                content = rec.get("content", "")
                block_id = rec.get("block_id", "unknown")
                meta = {
                    "type": rec.get("type", "unknown"),
                    "tokens": rec.get("tokens", 0),
                    "source": rec.get("source", ""),
                    "task_id": task_id,
                    "session_id": session_id,
                }
                try:
                    bridge._vms.write(mapped_collection, content, metadata=meta, doc_id=f"{mapped_collection}::{block_id}")
                    stored += 1
                except Exception as exc:
                    logger.debug("[VMS-INGEST] write failed for %s: %s", block_id, exc, exc_info=True)

            logger.info(
                "[CE-VMS] ingested: task=%s collection=%s stored=%d/%d",
                task_id,
                collection,
                stored,
                len(records),
            )
            return stored
        except Exception as exc:
            logger.warning("[VMS-INGEST] VMS unavailable, in-memory fallback: %s", exc, exc_info=True)
            return self._ingest_memory(records, collection, task_id)

    def _ingest_memory(self, records: list[dict[str, Any]], collection: str, task_id: str) -> int:
        global _in_memory_collections
        if collection not in _in_memory_collections:
            _in_memory_collections[collection] = []
        ts = __import__("time").time()
        for rec in records:
            rec["_stored_at"] = ts
            _in_memory_collections[collection].append(rec)
        logger.info(
            "[VMS-INGEST] in-memory fallback: collection=%s count=%d total=%d",
            collection,
            len(records),
            len(_in_memory_collections[collection]),
        )
        return len(records)

    def query(self, collection: str = "session_context", text: str = "", limit: int = 10) -> list[dict[str, Any]]:
        global _in_memory_collections
        if collection not in _in_memory_collections:
            return []
        results = _in_memory_collections[collection]
        if text:
            results = [r for r in results if text.lower() in str(r.get("content", "")).lower()]
        return results[-limit:]


def ingest_context(
    records: list[dict[str, Any]],
    collection: str = "session_context",
    task_id: str = "",
    session_id: str = "",
) -> int:
    return ContextIngest().ingest(records, collection, task_id, session_id)


def _map_collection(preferred: str) -> str:
    valid = {
        "decisions",
        "code_context",
        "lessons",
        "knowledge",
        "rules",
        "blueprints",
        "session_snapshots",
        "execution_traces",
    }
    if preferred in valid:
        return preferred
    if "session" in preferred:
        return "session_snapshots"
    if "context" in preferred or "task" in preferred:
        return "code_context"
    return "execution_traces"