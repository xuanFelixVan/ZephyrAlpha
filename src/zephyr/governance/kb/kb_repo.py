# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] zephyr.data.knowledge_management.kb.kb_repo
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.schema.schemas; zephyr.shared.utils.time_utils; zephyr.shared.utils.db_utils; zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_kb_repo | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
知识库仓库层（T-2-11-A）
========================
依据：ADR-0031（ChromaDB）、ADR-0030（SQLite knowledge 表）

10 状态机
---------
DRAFT → SUBMITTED → REVIEWED → ACCEPTED → INDEXED → VERIFIED
  ↑                                              ↓
  └── REJECTED ←─────────────────────────────────┘
  └── DEPRECATED → ARCHIVED
  └── SUPERSEDED

合法转换（有向图）：
  DRAFT      → SUBMITTED
  SUBMITTED  → REVIEWED, REJECTED
  REVIEWED   → ACCEPTED, REJECTED
  ACCEPTED   → INDEXED, REJECTED
  INDEXED    → VERIFIED, REJECTED
  VERIFIED   → DEPRECATED, SUPERSEDED, REJECTED
  REJECTED   → DRAFT（重新提交）
  DEPRECATED → ARCHIVED
  SUPERSEDED → ARCHIVED

Safety  : M（写入 knowledge 表 + ChromaDB upsert/delete）

用法
----
    from zephyr.governance.kb.kb_repo import KbRepo, KeStatus

    repo = KbRepo()
    repo.create(ke_id="KE-001", title="...", category="best_practice",
                source_file="docs/...", content="markdown...")
    repo.transition("KE-001", KeStatus.SUBMITTED)
    repo.search("如何避免过拟合", collection="ke_entries", n_results=5)
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator

from zephyr.shared.schema.schemas import BASE_CONFIG
from zephyr.shared.utils.time_utils import now_iso


class KeStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    REVIEWED = "REVIEWED"
    ACCEPTED = "ACCEPTED"
    INDEXED = "INDEXED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"
    SUPERSEDED = "SUPERSEDED"


_VALID_TRANSITIONS: dict[KeStatus, set[KeStatus]] = {
    KeStatus.DRAFT: {KeStatus.SUBMITTED},
    KeStatus.SUBMITTED: {KeStatus.REVIEWED, KeStatus.REJECTED},
    KeStatus.REVIEWED: {KeStatus.ACCEPTED, KeStatus.REJECTED},
    KeStatus.ACCEPTED: {KeStatus.INDEXED, KeStatus.REJECTED},
    KeStatus.INDEXED: {KeStatus.VERIFIED, KeStatus.REJECTED},
    KeStatus.VERIFIED: {KeStatus.DEPRECATED, KeStatus.SUPERSEDED, KeStatus.REJECTED},
    KeStatus.REJECTED: {KeStatus.DRAFT},
    KeStatus.DEPRECATED: {KeStatus.ARCHIVED},
    KeStatus.SUPERSEDED: {KeStatus.ARCHIVED},
    KeStatus.ARCHIVED: set(),
}

_VECTOR_VISIBLE_STATUSES = {
    KeStatus.INDEXED,
    KeStatus.VERIFIED,
    KeStatus.DEPRECATED,
    KeStatus.SUPERSEDED,
}


class RetrievalHit(BaseModel):
    model_config = BASE_CONFIG

    chunk_id: str
    score: float = Field(ge=0.0, le=1.0)
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    ke_id: str | None = None


class KeRecord(BaseModel):
    model_config = BASE_CONFIG

    ke_id: str = Field(pattern=r"^(KE-\d{3,}|ADR-\d{4,})$")
    title: str = Field(min_length=1, max_length=300)
    category: str = Field(min_length=1, max_length=100, default="general")
    source_file: str = Field(min_length=1)
    source_git_deleted: bool = False
    fingerprint_sha256: str | None = None
    tags: list[str] = Field(default_factory=list)
    summary: str = Field(default="", max_length=2000)
    status: KeStatus = KeStatus.DRAFT
    created_at: datetime
    updated_at: datetime

    @field_validator("fingerprint_sha256")
    @classmethod
    def validate_sha256(cls, v: str | None) -> str | None:
        if v is not None and len(v) != 64:
            raise ValueError("fingerprint_sha256 must be 64 hex chars")
        return v


class TransitionResult(BaseModel):
    model_config = BASE_CONFIG

    ke_id: str
    from_status: KeStatus
    to_status: KeStatus
    event_id: str
    vector_action: str = ""


def _compute_fingerprint(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class KbRepo:
    def __init__(
        self,
        db_path: Path | str | None = None,
        vector_dir: Path | str | None = None,
    ) -> None:
        from zephyr.shared.utils.db_utils import get_db_connection

        self._conn = get_db_connection(db_path)
        self._vector_dir = vector_dir

    def validate_state_transition(self, from_status: KeStatus, to_status: KeStatus) -> bool:
        allowed = _VALID_TRANSITIONS.get(from_status, set())
        return to_status in allowed

    def create(
        self,
        ke_id: str,
        title: str,
        category: str,
        source_file: str,
        content: str,
        source_git_deleted: bool = False,
        tags: list[str] | None = None,
        summary: str = "",
    ) -> KeRecord:
        now = now_iso()
        fp = _compute_fingerprint(content)
        rec = KeRecord(
            ke_id=ke_id,
            title=title,
            category=category,
            source_file=source_file,
            source_git_deleted=source_git_deleted,
            fingerprint_sha256=fp,
            tags=tags or [],
            summary=summary,
            status=KeStatus.DRAFT,
            created_at=datetime.fromisoformat(now),
            updated_at=datetime.fromisoformat(now),
        )
        self._conn.execute("BEGIN")
        try:
            self._conn.execute(
                "INSERT INTO knowledge "
                "(ke_id, title, category, source_file, source_git_deleted, "
                "fingerprint_sha256, tags, summary, status, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    rec.ke_id,
                    rec.title,
                    rec.category,
                    rec.source_file,
                    int(rec.source_git_deleted),
                    rec.fingerprint_sha256,
                    json.dumps(rec.tags),
                    rec.summary,
                    rec.status.value,
                    now,
                    now,
                ),
            )
            self._conn.execute("COMMIT")
        except Exception:
            self._conn.execute("ROLLBACK")
            raise
        return rec

    def get(self, ke_id: str) -> KeRecord | None:
        cursor = self._conn.execute(
            "SELECT ke_id, title, category, source_file, source_git_deleted, "
            "fingerprint_sha256, tags, summary, status, created_at, updated_at "
            "FROM knowledge WHERE ke_id = ?",
            (ke_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return KeRecord(
            ke_id=row["ke_id"],
            title=row["title"],
            category=row["category"],
            source_file=row["source_file"],
            source_git_deleted=bool(row["source_git_deleted"]),
            fingerprint_sha256=row["fingerprint_sha256"],
            tags=json.loads(row["tags"]),
            summary=row["summary"],
            status=KeStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def transition(self, ke_id: str, to_status: KeStatus, content: str | None = None) -> TransitionResult:
        rec = self.get(ke_id)
        if rec is None:
            raise ValueError(f"KE not found: {ke_id}")
        from_status = rec.status
        if to_status not in _VALID_TRANSITIONS.get(from_status, set()):
            raise ValueError(f"Invalid transition: {from_status.value} → {to_status.value} for {ke_id}")
        now = now_iso()
        event_id = f"KE-{uuid.uuid4().hex[:12]}"
        vector_action = self._determine_vector_action(from_status, to_status)

        self._conn.execute("BEGIN")
        try:
            self._conn.execute(
                "UPDATE knowledge SET status = ?, updated_at = ? WHERE ke_id = ?",
                (to_status.value, now, ke_id),
            )
            self._conn.execute(
                "INSERT INTO events (event_id, event_type, payload, task_id, session_id, created_at) "
                "VALUES (?, 'state_transition', ?, NULL, NULL, ?)",
                (
                    event_id,
                    json.dumps(
                        {
                            "ke_id": ke_id,
                            "from_status": from_status.value,
                            "to_status": to_status.value,
                            "vector_action": vector_action,
                        }
                    ),
                    now,
                ),
            )
            self._conn.execute("COMMIT")
        except Exception:
            self._conn.execute("ROLLBACK")
            raise

        if vector_action == "upsert" and content is not None:
            self._upsert_vector(ke_id, content, rec)
        elif vector_action == "delete":
            self._delete_vector(ke_id)

        return TransitionResult(
            ke_id=ke_id,
            from_status=from_status,
            to_status=to_status,
            event_id=event_id,
            vector_action=vector_action,
        )

    def search(
        self,
        query_text: str,
        collection: str = "ke_entries",
        where: dict[str, Any] | None = None,
        n_results: int = 5,
        score_threshold: float = 0.6,
    ) -> list[RetrievalHit]:
        from zephyr.governance.kb.chromadb_init import get_chroma_client

        client = get_chroma_client(self._vector_dir)
        try:
            col = client.get_collection(name=collection)
        except Exception:
            return []

        chroma_where: dict[str, Any] = {"status": {"$in": [s.value for s in _VECTOR_VISIBLE_STATUSES]}}
        if where:
            chroma_where = {"$and": [chroma_where, where]}

        try:
            results = col.query(
                query_texts=[query_text],
                where=chroma_where,
                n_results=n_results,
            )
        except Exception:
            return []

        hits: list[RetrievalHit] = []
        if not results["ids"] or not results["ids"][0]:
            return hits
        ids = results["ids"][0]
        distances = results["distances"][0] if results.get("distances") else [0.0] * len(ids)
        docs = results["documents"][0] if results.get("documents") else [""] * len(ids)
        metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(ids)

        for chunk_id, dist, doc, meta in zip(ids, distances, docs, metas, strict=False):
            score = 1.0 - dist
            if score < score_threshold:
                continue
            hits.append(
                RetrievalHit(
                    chunk_id=chunk_id,
                    score=round(score, 4),
                    content=doc,
                    metadata=meta,
                    ke_id=meta.get("ke_id"),
                )
            )
        return hits

    def list_by_status(self, status: KeStatus | None = None) -> list[KeRecord]:
        if status is not None:
            cursor = self._conn.execute(
                "SELECT ke_id, title, category, source_file, source_git_deleted, "
                "fingerprint_sha256, tags, summary, status, created_at, updated_at "
                "FROM knowledge WHERE status = ? ORDER BY created_at",
                (status.value,),
            )
        else:
            cursor = self._conn.execute(
                "SELECT ke_id, title, category, source_file, source_git_deleted, "
                "fingerprint_sha256, tags, summary, status, created_at, updated_at "
                "FROM knowledge ORDER BY created_at"
            )
        records: list[KeRecord] = []
        for row in cursor.fetchall():
            records.append(
                KeRecord(
                    ke_id=row["ke_id"],
                    title=row["title"],
                    category=row["category"],
                    source_file=row["source_file"],
                    source_git_deleted=bool(row["source_git_deleted"]),
                    fingerprint_sha256=row["fingerprint_sha256"],
                    tags=json.loads(row["tags"]),
                    summary=row["summary"],
                    status=KeStatus(row["status"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                )
            )
        return records

    def delete(self, ke_id: str) -> bool:
        existing = self.get(ke_id)
        if existing is None:
            return False
        self._delete_vector(ke_id)
        self._conn.execute("BEGIN")
        try:
            self._conn.execute("DELETE FROM knowledge WHERE ke_id = ?", (ke_id,))
            self._conn.execute("COMMIT")
            return True
        except Exception:
            self._conn.execute("ROLLBACK")
            return False

    def _determine_vector_action(self, from_status: KeStatus, to_status: KeStatus) -> str:
        if to_status in _VECTOR_VISIBLE_STATUSES and from_status not in _VECTOR_VISIBLE_STATUSES:
            return "upsert"
        if to_status in (KeStatus.ARCHIVED, KeStatus.REJECTED) and from_status in _VECTOR_VISIBLE_STATUSES:
            return "delete"
        if to_status in _VECTOR_VISIBLE_STATUSES and from_status in _VECTOR_VISIBLE_STATUSES:
            return "upsert"
        return ""

    def _upsert_vector(self, ke_id: str, content: str, rec: KeRecord) -> None:
        from zephyr.governance.kb.chromadb_init import get_chroma_client

        client = get_chroma_client(self._vector_dir)
        try:
            col = client.get_collection(name="ke_entries")
        except Exception:
            return

        chunk_id = f"{ke_id}-chunk-0"
        meta = {
            "ke_id": ke_id,
            "category": rec.category,
            "source_file": rec.source_file,
            "source_git_deleted": rec.source_git_deleted,
            "status": rec.status.value,
        }
        col.upsert(
            ids=[chunk_id],
            documents=[content],
            metadatas=[meta],
        )

    def _delete_vector(self, ke_id: str) -> None:
        from zephyr.governance.kb.chromadb_init import get_chroma_client

        client = get_chroma_client(self._vector_dir)
        try:
            col = client.get_collection(name="ke_entries")
        except Exception:
            return

        try:
            existing = col.get(where={"ke_id": ke_id})
            if existing["ids"]:
                col.delete(ids=existing["ids"])
        except Exception:
            pass
