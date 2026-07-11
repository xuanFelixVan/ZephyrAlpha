# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] zephyr.governance.kb.storage._backend_protocol
# [DOMAIN] D_GOV_KB
# [DEPENDENCIES] zephyr.governance.kb.storage.__init__
# [CONSUMERS] zephyr.knowledge.kb.storage.unified_memory_api; zephyr.knowledge.kb.vms_memory_backend
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] MemoryBackend Protocol signature must not change without updating all implementors
# [MODIFY-GUARD] changes here affect unified_memory_api.py + vms_memory_backend.py + all backend implementors
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] MemoryBackendError on backend failure; WriteTraceMissing on missing provenance
# [TESTS] tests/test_unified_memory_api.py; tests/test_vms_memory_backend.py
# [A_module] module_id=MOD-DAT__backend_protocol | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Backend protocol & shared data classes for the unified memory layer.
=====================================================
Extracted from unified_memory_api.py to break the circular dependency:

    unified_memory_api.py -> vms_memory_backend.py -> unified_memory_api.py

This module defines the *contract* (Protocol + data classes + exceptions +
InMemoryMemoryBackend fallback) that both unified_memory_api.py and
vms_memory_backend.py depend on, with no import cycle.

This module must NOT import from unified_memory_api.py or vms_memory_backend.py.
"""

from __future__ import annotations

import threading
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "InMemoryMemoryBackend",
    "MemoryBackend",
    "MemoryBackendError",
    "MemoryRecord",
]


class MemoryBackendError(RuntimeError):
    """Raised when a memory backend is unavailable or an operation fails."""
    error_code = "ZA-GV-0038"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class MemoryRecord(BaseModel):
    """Unified return type for kb.recall / kb.search."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    chunk_id: str = Field(min_length=1, description="Backend-unique ID")
    topic: str = Field(min_length=1, description="Owning topic")
    content: str = Field(description="Raw content")
    score: float = Field(default=1.0, ge=0.0, le=1.0, description="Similarity score (recall defaults to 1.0)")
    written_at: str = Field(default="", description="UTC ISO 8601 write timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extra metadata (incl. provenance)")


@runtime_checkable
class MemoryBackend(Protocol):
    """Memory backend protocol; InMemoryMemoryBackend / VMSMemoryBackend implement this."""

    def write(self, record: MemoryRecord) -> str: ...  # pragma: no cover - Protocol

    def list_by_topic(self, topic: str, k: int) -> list[MemoryRecord]: ...  # pragma: no cover

    def query(self, query_text: str, k: int, topic: str | None = None) -> list[MemoryRecord]: ...  # pragma: no cover

    def count(self) -> int: ...  # pragma: no cover


class InMemoryMemoryBackend:
    """Pure-Python dict fallback backend (no ChromaDB dependency).

    Used for:
    1. Unit tests — avoids ChromaDB startup cost and persistence side-effects
    2. Degradation path when embedding model download fails
    3. Offline CI runs
    """

    def __init__(self) -> None:
        self._records: dict[str, MemoryRecord] = {}
        self._order: dict[str, int] = {}
        self._counter: int = 0
        self._lock = threading.RLock()

    def write(self, record: MemoryRecord) -> str:
        with self._lock:
            self._counter += 1
            self._records[record.chunk_id] = record
            self._order[record.chunk_id] = self._counter
        return record.chunk_id

    def list_by_topic(self, topic: str, k: int) -> list[MemoryRecord]:
        with self._lock:
            matched = [(self._order.get(r.chunk_id, 0), r) for r in self._records.values() if r.topic == topic]
        matched.sort(key=lambda item: (item[1].written_at, item[0]), reverse=True)
        return [r for _, r in matched[: max(0, k)]]

    def query(self, query_text: str, k: int, topic: str | None = None) -> list[MemoryRecord]:
        if not query_text:
            return []
        q_tokens = set(_simple_tokens(query_text))
        if not q_tokens:
            return []

        with self._lock:
            candidates = list(self._records.values())
        if topic is not None:
            candidates = [r for r in candidates if r.topic == topic]

        scored: list[tuple[float, MemoryRecord]] = []
        for rec in candidates:
            r_tokens = set(_simple_tokens(rec.content))
            if not r_tokens:
                continue
            overlap = len(q_tokens & r_tokens)
            score = overlap / max(len(q_tokens), 1)
            if score <= 0.0:
                continue
            scored.append((min(score, 1.0), rec))

        scored.sort(key=lambda item: item[0], reverse=True)
        results: list[MemoryRecord] = []
        for score, rec in scored[: max(0, k)]:
            results.append(
                MemoryRecord(
                    chunk_id=rec.chunk_id,
                    topic=rec.topic,
                    content=rec.content,
                    score=round(score, 4),
                    written_at=rec.written_at,
                    metadata=dict(rec.metadata),
                )
            )
        return results

    def count(self) -> int:
        with self._lock:
            return len(self._records)

    def clear(self) -> None:
        """Test-only: wipe in-memory store."""
        with self._lock:
            self._records.clear()
            self._order.clear()
            self._counter = 0


def _simple_tokens(text: str) -> list[str]:
    """Minimal tokenizer: split on non-alnum + per-char CJK."""
    if not text:
        return []
    tokens: list[str] = []
    buf: list[str] = []
    for ch in text.lower():
        if ch.isascii() and (ch.isalnum() or ch == "_"):
            buf.append(ch)
        else:
            if buf:
                tokens.append("".join(buf))
                buf = []
            if "\u4e00" <= ch <= "\u9fff":
                tokens.append(ch)
    if buf:
        tokens.append("".join(buf))
    return [t for t in tokens if t]
