# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | CT-SCRIPT-KB-001
# [MODULE] zephyr.infrastructure.script_system.kb_bridge
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.__init__
# [CONSUMERS] zephyr.trading.orchestrator.script_runner; AutoRuntime Core post-scan phase
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] findings→KB entry 1:1映射; KB不可用时仅日志不阻塞; timestamp带时区
# [MODIFY-GUARD] CT-SCRIPT-KB-001 schema变更必须同步KB indexing规则
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] KB不可用返回degraded不阻塞; 空findings返回0
# [TESTS] scripts/connect/script_kb.py --trigger
# [A_module] module_id=MOD-INF_kb_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Script→KB 审计入库桥接器 — publish_to_kb() 生产者

CT-SCRIPT-KB-001: 审计脚本执行完成后将 findings 写入 Knowledge Base。
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "KBBridge",
    "KBPublishResult",
    "publish_to_kb",
]


@dataclass
class KBPublishResult:
    published: int = 0
    total: int = 0
    status: str = "complete"
    error: str | None = None


class KBBridge:
    def publish(
        self,
        findings: list[dict[str, Any]],
        task_id: str = "",
        session_id: str = "",
    ) -> KBPublishResult:
        if not findings:
            return KBPublishResult()

        try:
            from zephyr.shared.protocols.registry import ServiceRegistry

            conn = ServiceRegistry.get("db_connection")
            now = datetime.now(UTC).isoformat()
            published = 0

            for finding in findings:
                try:
                    dim = finding.get("dimension", "unknown")
                    conn.execute(
                        """INSERT INTO knowledge
                           (ke_id, title, category, source_file, tags, summary, created_at, updated_at, status)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            f"finding:{task_id}:{dim}",
                            finding.get("message", "Audit finding")[:200],
                            "audit_finding",
                            f"script_system/task/{task_id}",
                            dim,
                            json.dumps(finding, ensure_ascii=False, default=str)[:2000],
                            now,
                            now,
                            "INDEXED",
                        ),
                    )
                    published += 1
                except Exception as exc:
                    logger.debug("[SCRIPT-KB] write finding failed: %s", exc, exc_info=True)

            conn.commit()
            conn.close()

            logger.info("[SCRIPT-KB] published: task=%s published=%d/%d", task_id, published, len(findings))
            return KBPublishResult(published=published, total=len(findings))
        except Exception as exc:
            logger.warning("[SCRIPT-KB] KB unavailable, degraded: %s", exc, exc_info=True)
            return KBPublishResult(published=0, total=len(findings), status="degraded", error=str(exc))


def publish_to_kb(
    findings: list[dict[str, Any]],
    task_id: str = "",
    session_id: str = "",
) -> KBPublishResult:
    return KBBridge().publish(findings, task_id, session_id)