"""OWASP ASI06 Vector Memory投毒防护——RAG/Vector Memory写入源身份+来源审计+隔离."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class MemoryProvenance(BaseModel):
    provenance_id: str
    source_agent_id: str
    source_session_id: str
    content_hash: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    vector_db_name: str = ""
    collection_name: str = ""
    trust_score: float = 1.0
    flagged: bool = False


class ProvenanceAuditEntry(BaseModel):
    provenance_id: str
    action: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MemoryProvenanceGuard:
    def __init__(self) -> None:
        self._provenance: dict[str, MemoryProvenance] = {}
        self._audit: list[ProvenanceAuditEntry] = []
        self._quarantine: set[str] = set()

    def record_provenance(self, source_agent_id: str, source_session_id: str, content_hash: str, vector_db_name: str = "", collection_name: str = "") -> MemoryProvenance:
        pid = f"PROV-{source_agent_id}-{source_session_id[:8]}-{content_hash[:8]}"
        mp = MemoryProvenance(
            provenance_id=pid,
            source_agent_id=source_agent_id,
            source_session_id=source_session_id,
            content_hash=content_hash,
            vector_db_name=vector_db_name,
            collection_name=collection_name,
        )
        self._provenance[pid] = mp
        self._audit.append(ProvenanceAuditEntry(provenance_id=pid, action="RECORDED"))
        return mp

    def verify(self, provenance_id: str, consuming_agent_id: str) -> dict[str, Any]:
        mp = self._provenance.get(provenance_id)
        if not mp:
            return {"verified": False, "reason": "unknown_provenance", "provenance_id": provenance_id}

        if mp.flagged or provenance_id in self._quarantine:
            return {"verified": False, "reason": "quarantined_or_flagged", "provenance_id": provenance_id}

        if mp.source_agent_id != consuming_agent_id and mp.trust_score < 0.5:
            return {"verified": False, "reason": "low_trust_cross_agent", "provenance_id": provenance_id}

        self._audit.append(ProvenanceAuditEntry(provenance_id=provenance_id, action="VERIFIED"))
        return {"verified": True, "provenance_id": provenance_id, "source_agent_id": mp.source_agent_id}

    def flag(self, provenance_id: str) -> None:
        if provenance_id in self._provenance:
            self._provenance[provenance_id].flagged = True
        self._quarantine.add(provenance_id)
        self._audit.append(ProvenanceAuditEntry(provenance_id=provenance_id, action="FLAGGED"))
