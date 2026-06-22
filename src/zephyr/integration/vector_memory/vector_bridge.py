# [A_module] module_id=MOD-INT_vector_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain-knowledge/vector-memory/blueprint.md | §

# [MODULE] zephyr.integration.vector_memory.vector_bridge

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
VectorBridge — MOD-INF-011 CE/KB 外部集成适配器
==================================================
蓝图 §8 · §6 · 6 系统集成目标

接口
----
- search_for_ce(query, k) → CE 检索专用接口
- sync_knowledge(ke_id, content) → KB 同步写入 knowledge Collection
- sync_rules(rule_id, content) → Governance 同步写入 rules Collection
- write_decision(task_id, decision_text) → Orchestrator 写入 decisions Collection
- write_session_summary(session_id, summary) → SessionMgr 写入 session_snapshots
- audit_operation(operation, details) → 写入审计日志
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

_logger = logging.getLogger(__name__)


class VectorBridge:
    def __init__(self, vms: Any) -> None:
        self._vms = vms

    def search_for_ce(self, query: str, collections: list[str] | None = None, k: int = 5) -> list[dict[str, Any]]:
        target_collections = collections or ["rules", "knowledge", "decisions", "lessons"]
        all_results: list[dict[str, Any]] = []
        for col_name in target_collections:
            try:
                results = self._vms.search(col_name, query, k=k)
                for r in results:
                    r["source_collection"] = col_name
                all_results.extend(results)
            except Exception as e:
                _logger.warning("VectorBridge: CE 检索 %s 失败: %s", col_name, e)
        all_results.sort(key=lambda x: x.get("distance", 1.0))
        return all_results[:k]

    def sync_knowledge(self, ke_id: str, content: str, metadata: dict[str, Any] | None = None) -> str:
        meta = dict(metadata or {})
        meta.setdefault("origin", f"kb/ke/{ke_id}")
        meta.setdefault("audit_chain", ["kb"])
        meta.setdefault("arbitration", "supervised")
        return self._vms.write("knowledge", content, metadata=meta)

    def sync_rules(self, rule_id: str, content: str) -> str:
        return self._vms.write(
            "rules",
            content,
            metadata={
                "origin": f"governance/rule/{rule_id}",
                "audit_chain": ["governance"],
                "arbitration": "human-gated",
            },
        )

    def write_decision(self, task_id: str, decision_text: str) -> str:
        return self._vms.write(
            "decisions",
            decision_text,
            metadata={
                "origin": f"orchestrator/task/{task_id}",
                "audit_chain": ["orchestrator"],
                "arbitration": "supervised",
                "task_id": task_id,
            },
        )

    def write_session_summary(self, session_id: str, summary: str) -> str:
        return self._vms.write(
            "session_snapshots",
            summary,
            metadata={
                "origin": f"session_manager/{session_id}",
                "audit_chain": ["session_manager"],
                "arbitration": "autonomous",
                "session_id": session_id,
            },
        )

    def audit_operation(self, operation: str, details: dict[str, Any]) -> str:
        import json

        return self._vms.write(
            "execution_traces",
            json.dumps(details, ensure_ascii=False, default=str),
            metadata={
                "origin": f"audit-trail/{operation}",
                "audit_chain": ["audit-trail"],
                "arbitration": "supervised",
                "operation": operation,
                "details": details,
                "audited_at": datetime.now(UTC).isoformat(),
            },
        )

    def write_failure_pattern(self, pattern_text: str) -> str:
        return self._vms.write(
            "lessons",
            pattern_text,
            metadata={
                "origin": "fle/failure_pattern",
                "audit_chain": ["fle"],
                "arbitration": "autonomous",
            },
        )
