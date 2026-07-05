# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.guards.memory_provenance_guard
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_permissions.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] record_provenance returns MemoryProvenance with provenance_id; verify returns dict with verified key
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] record_provenance/verify never raise
# [TESTS] tests/agent_rbac/test_permissions.py
# [A_module] module_id=MOD-SEC_memory_provenance_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MemoryProvenanceGuard — 记忆来源溯源守卫.

依据蓝图 MOD-INF-018 §3:
- 记录 agent 记忆的来源（agent_id/session_id/content_hash）
- 验证记忆归属，防止跨 agent 记忆窃取
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class MemoryProvenance:
    """记忆来源记录.

    Attributes:
        provenance_id: 溯源 ID
        agent_id: 记忆归属 agent
        session_id: 会话 ID
        content_hash: 内容哈希
    """

    provenance_id: str
    agent_id: str
    session_id: str
    content_hash: str


@dataclass
class ProvenanceAuditEntry:
    """溯源审计条目."""

    provenance_id: str
    verifier_agent_id: str
    verified: bool


class MemoryProvenanceGuard:
    """记忆来源守卫 — 记录与验证记忆来源."""

    def __init__(self) -> None:
        self._records: dict[str, MemoryProvenance] = {}
        self._audit_trail: list[ProvenanceAuditEntry] = []

    def record_provenance(
        self,
        agent_id: str,
        session_id: str,
        content_hash: str,
    ) -> MemoryProvenance:
        """记录记忆来源.

        Args:
            agent_id: 记忆归属 agent
            session_id: 会话 ID
            content_hash: 内容哈希

        Returns:
            MemoryProvenance 包含 provenance_id
        """
        provenance_id = f"MP-{uuid.uuid4().hex[:12]}"
        mp = MemoryProvenance(
            provenance_id=provenance_id,
            agent_id=agent_id,
            session_id=session_id,
            content_hash=content_hash,
        )
        self._records[provenance_id] = mp
        return mp

    def verify(self, provenance_id: str, agent_id: str) -> dict[str, Any]:
        """验证记忆归属.

        Args:
            provenance_id: 溯源 ID
            agent_id: 验证者 agent ID

        Returns:
            dict 包含 verified 状态
        """
        mp = self._records.get(provenance_id)
        if mp is None:
            result = {"verified": False, "reason": "provenance_not_found"}
        else:
            verified = mp.agent_id == agent_id
            result = {
                "verified": verified,
                "provenance_id": provenance_id,
                "owner_agent_id": mp.agent_id,
                "verifier_agent_id": agent_id,
            }
        self._audit_trail.append(
            ProvenanceAuditEntry(
                provenance_id=provenance_id,
                verifier_agent_id=agent_id,
                verified=result.get("verified", False),
            )
        )
        return result


__all__ = [
    "MemoryProvenance",
    "MemoryProvenanceGuard",
    "ProvenanceAuditEntry",
]
