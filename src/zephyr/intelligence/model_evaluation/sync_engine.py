# [BLUEPRINT] MOD-INF-036 | docs/03_modules/_cross_layer/model-capability-exam/blueprint.md
# [MODULE] zephyr.intelligence.model_evaluation.sync_engine
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema; zephyr.governance.__init__; zephyr.autonomy_core.__init__
# [CONSUMERS] zephyr.knowledge.kb.scheduler; AutoRuntime Core sync phase
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 增量按created_at > since检测; 全量since=None; VMS不可用降级不阻塞
# [MODIFY-GUARD] CT-KB-VMS-001 集合映射变更同步更新collection_manager
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] VMS不可用返回degraded; 空增量返回0
# [TESTS] scripts/connect/kb_vms.py --trigger
# [A_module] module_id=MOD-INF-036-sync_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""KB->VMS 同步引擎 — sync_to_vms() 生产者"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

__all__ = ["SyncEngine", "SyncResult", "sync_to_vms"]


@dataclass
class SyncResult:
    synced: int = 0
    total: int = 0
    status: str = "complete"
    error: str | None = None


class SyncEngine:
    def sync_to_vms(self, since: datetime | None = None) -> SyncResult:
        try:
            from zephyr.autonomy_core.context.vector_bridge import VectorBridge
            from zephyr.governance.persistence.sqlite_schema import get_db_connection
            from zephyr.integration.vector_memory.in_memory_fake_vms import InMemoryFakeVMS

            conn = get_db_connection()
            try:
                since_str = since.isoformat() if since else "1970-01-01"
                rows = conn.execute(
                    "SELECT ke_id,title,summary,category,tags FROM knowledge WHERE status='INDEXED' AND created_at > ? LIMIT 50",
                    (since_str,),
                ).fetchall()
            finally:
                # 5.144.5 修复: conn.close() 移入 finally, 防止 execute 抛异常跳过 close
                conn.close()

            if not rows:
                return SyncResult(synced=0, total=0)

            vms = InMemoryFakeVMS()
            bridge = VectorBridge(vms)
            stored = 0
            for row in rows:
                ke_id, title, summary, category, tags = row
                text = f"{title}: {summary or ''}"[:2000]
                meta = {"ke_id": ke_id, "category": category or "", "tags": tags or ""}
                try:
                    bridge._vms.write("knowledge", text, metadata=meta, doc_id=f"ke::{ke_id}")
                    stored += 1
                except Exception as exc:
                    logger.debug("[KB-VMS] write failed for %s: %s", ke_id, exc, exc_info=True)

            logger.info("[KB-VMS] synced: %d/%d", stored, len(rows))
            return SyncResult(synced=stored, total=len(rows))
        except Exception as exc:
            logger.warning("[KB-VMS] degraded: %s", exc, exc_info=True)
            return SyncResult(status="degraded", error=str(exc))


def sync_to_vms(since: datetime | None = None) -> SyncResult:
    return SyncEngine().sync_to_vms(since)