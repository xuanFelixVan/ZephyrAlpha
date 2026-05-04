# AI-generated: T-3-21 Pattern Library
"""
PatternLibrary · 成功模式库（被 kb_repo 索引为 patterns Collection）
=====================================================================

Task ID     : T-3-21
Depends     : T-2-11-A（kb_repo.py）、T-2-10（chromadb_init.py）
safety_level: M

核心职责
--------
1. **模式类型**：success_pattern / failure_pattern / anti_pattern
2. **与 kb_repo.py 集成**：模式自动索引到 ChromaDB patterns Collection
3. **模式检索**：按 domain / layer / pattern_type 查询
4. **CRUD 操作**：创建、读取、查询、删除模式

零外部依赖：仅 pydantic + 标准库。
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

from zephyr.shared.schemas import BASE_CONFIG
from zephyr.shared.time_utils import now_iso

__all__ = [
    "PatternType",
    "PatternEntry",
    "PatternQuery",
    "PatternLibrary",
]

class PatternType(str, Enum):
    SUCCESS_PATTERN = "success_pattern"
    FAILURE_PATTERN = "failure_pattern"
    ANTI_PATTERN = "anti_pattern"

class PatternEntry(BaseModel):
    model_config = BASE_CONFIG

    pattern_id: str = Field(pattern=r"^PAT-\d{3,}$", description="模式 ID，如 PAT-001")
    title: str = Field(min_length=1, max_length=300)
    pattern_type: PatternType = Field(description="模式类型")
    domain: str = Field(min_length=1, max_length=50, description="所属域 D0-D9")
    layer: str = Field(min_length=1, max_length=20, description="所属层 L00-L11")
    description: str = Field(min_length=1, max_length=2000)
    context: str = Field(default="", max_length=2000, description="适用上下文")
    solution: str = Field(default="", max_length=2000, description="解决方案（success）/ 避免方式（anti）")
    consequences: list[str] = Field(default_factory=list, description="后果/影响")
    tags: list[str] = Field(default_factory=list)
    source_ke_id: str | None = Field(default=None, description="来源 KE 编号")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="置信度")
    occurrence_count: int = Field(default=1, ge=1, description="观测次数")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")

    @field_validator("tags")
    @classmethod
    def tags_no_duplicates(cls, v: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for tag in v:
            if tag not in seen:
                seen.add(tag)
                result.append(tag)
        return result

class PatternQuery(BaseModel):
    model_config = BASE_CONFIG

    domain: str | None = None
    layer: str | None = None
    pattern_type: PatternType | None = None
    tags: list[str] | None = None
    keyword: str | None = None

def _compute_fingerprint(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

class PatternLibrary:
    """成功模式库，支持 CRUD + 向量检索。

    Parameters
    ----------
    persist_dir : Path | str | None
        持久化目录（用于 JSON 存储）。
    chroma_client : Any | None
        ChromaDB 客户端（用于向量索引）。
    """

    PATTERNS_COLLECTION = "patterns"

    def __init__(
        self,
        persist_dir: Any | None = None,
        chroma_client: Any | None = None,
    ) -> None:
        self._persist_dir = persist_dir
        self._chroma_client = chroma_client
        self._patterns: dict[str, PatternEntry] = {}
        self._next_id: int = 1

    def create(
        self,
        title: str,
        pattern_type: PatternType,
        domain: str,
        layer: str,
        description: str,
        context: str = "",
        solution: str = "",
        consequences: list[str] | None = None,
        tags: list[str] | None = None,
        source_ke_id: str | None = None,
        confidence: float = 1.0,
    ) -> PatternEntry:
        now_iso_val = now_iso()
        now_dt = datetime.fromisoformat(now_iso_val)
        pattern_id = f"PAT-{self._next_id:03d}"
        self._next_id += 1
        entry = PatternEntry(
            pattern_id=pattern_id,
            title=title,
            pattern_type=pattern_type,
            domain=domain,
            layer=layer,
            description=description,
            context=context,
            solution=solution,
            consequences=consequences or [],
            tags=tags or [],
            source_ke_id=source_ke_id,
            confidence=confidence,
            created_at=now_dt,
            updated_at=now_dt,
        )
        self._patterns[pattern_id] = entry
        self._index_to_chroma(entry)
        return entry

    def get(self, pattern_id: str) -> PatternEntry | None:
        return self._patterns.get(pattern_id)

    def query(self, query: PatternQuery) -> list[PatternEntry]:
        results = list(self._patterns.values())
        if query.domain is not None:
            results = [p for p in results if p.domain == query.domain]
        if query.layer is not None:
            results = [p for p in results if p.layer == query.layer]
        if query.pattern_type is not None:
            results = [p for p in results if p.pattern_type == query.pattern_type]
        if query.tags is not None and query.tags:
            tag_set = {t.lower() for t in query.tags}
            results = [p for p in results if tag_set & {t.lower() for t in p.tags}]
        if query.keyword is not None:
            kw = query.keyword.lower()
            results = [
                p for p in results if kw in p.title.lower() or kw in p.description.lower() or kw in p.context.lower()
            ]
        return results

    def delete(self, pattern_id: str) -> bool:
        entry = self._patterns.pop(pattern_id, None)
        if entry is None:
            return False
        self._delete_from_chroma(pattern_id)
        return True

    def update(
        self,
        pattern_id: str,
        **fields: Any,
    ) -> PatternEntry | None:
        entry = self._patterns.get(pattern_id)
        if entry is None:
            return None
        for key, value in fields.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        entry.updated_at = datetime.fromisoformat(now_iso())
        self._index_to_chroma(entry)
        return entry

    def list_all(self) -> list[PatternEntry]:
        return list(self._patterns.values())

    def count(self) -> int:
        return len(self._patterns)

    def _index_to_chroma(self, entry: PatternEntry) -> None:
        if self._chroma_client is None:
            return
        try:
            col = self._chroma_client.get_collection(name=self.PATTERNS_COLLECTION)
        except Exception:
            try:
                col = self._chroma_client.create_collection(
                    name=self.PATTERNS_COLLECTION,
                    metadata={"hnsw:space": "cosine"},
                )
            except Exception:
                return
        content = f"{entry.title}\n{entry.description}\n{entry.context}\n{entry.solution}"
        meta = {
            "pattern_id": entry.pattern_id,
            "pattern_type": entry.pattern_type.value,
            "domain": entry.domain,
            "layer": entry.layer,
            "tags": json.dumps(entry.tags),
            "confidence": entry.confidence,
        }
        chunk_id = f"{entry.pattern_id}-chunk-0"
        col.upsert(ids=[chunk_id], documents=[content], metadatas=[meta])

    def _delete_from_chroma(self, pattern_id: str) -> None:
        if self._chroma_client is None:
            return
        try:
            col = self._chroma_client.get_collection(name=self.PATTERNS_COLLECTION)
            chunk_id = f"{pattern_id}-chunk-0"
            col.delete(ids=[chunk_id])
        except Exception:
            pass

    def search(
        self,
        query_text: str,
        n_results: int = 5,
        pattern_type: PatternType | None = None,
        domain: str | None = None,
    ) -> list[dict[str, Any]]:
        if self._chroma_client is None:
            return []
        try:
            col = self._chroma_client.get_collection(name=self.PATTERNS_COLLECTION)
        except Exception:
            return []
        where_conditions: list[dict[str, Any]] = []
        if pattern_type is not None:
            where_conditions.append({"pattern_type": pattern_type.value})
        if domain is not None:
            where_conditions.append({"domain": domain})
        chroma_where: dict[str, Any] | None = None
        if len(where_conditions) == 1:
            chroma_where = where_conditions[0]
        elif len(where_conditions) > 1:
            chroma_where = {"$and": where_conditions}
        try:
            kwargs: dict[str, Any] = {
                "query_texts": [query_text],
                "n_results": n_results,
            }
            if chroma_where is not None:
                kwargs["where"] = chroma_where
            results = col.query(**kwargs)
        except Exception:
            return []
        hits: list[dict[str, Any]] = []
        if not results["ids"] or not results["ids"][0]:
            return hits
        ids = results["ids"][0]
        distances = results["distances"][0] if results.get("distances") else [0.0] * len(ids)
        docs = results["documents"][0] if results.get("documents") else [""] * len(ids)
        metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(ids)
        for chunk_id, dist, doc, meta in zip(ids, distances, docs, metas, strict=False):
            hits.append(
                {
                    "chunk_id": chunk_id,
                    "score": round(1.0 - dist, 4),
                    "content": doc,
                    "metadata": meta,
                }
            )
        return hits
