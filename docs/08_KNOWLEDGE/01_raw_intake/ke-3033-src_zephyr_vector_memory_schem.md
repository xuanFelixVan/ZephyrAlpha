---
module_id: KE-2933
status: active
title: src/zephyr/vector-memory/schemas.py (experimental 产出)
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# src/zephyr/vector-memory/schemas.py (experimental 产出)

src/zephyr/vector-memory/schemas.py (experimental 产出)

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum

class DocumentSourceType(str, Enum):
    MARKDOWN_DOC = "markdown_doc"
    CODE = "code"
    TASK_CARD = "task_card"
    SESSION_LOG = "session_log"
    ARCHITECTURE_YAML = "architecture_yaml"
    AUDIT_REPORT = "audit_report"
    EXTERNAL = "external"

class CollectionName(str, Enum):
    DECISIONS = "decisions"
    CODE_CONTEXT = "code_context"
    TASK_HISTORY = "task_history"
    LESSONS = "lessons"

class Document(BaseModel):
    doc_id: str = Field(..., description="全局唯一，推荐 sha1(source_path)")
    collection: CollectionName
    source_path: str
    source_type: DocumentSourceType
    title: str
    content: str
    content_hash: str = Field(..., description="sha256(content)")
    language: Literal["zh", "en", "mixed", "code"] = "zh"
    tags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict,
        description="自由字段 + cascade 字段：superseded_by / merged_into / task_deps 等")
    created_at: datetime
    updated_at: datetime
    version: int = Field(default=1, description="同 doc_id 下版本号，update 时 +1")

class Chunk(BaseModel):
    chunk_id: str = Field(..., description="{doc_id}::v{version}::c{chunk_index}")
    doc_id: str
    doc_version: int
    chunk_index: int = Field(..., ge=0)
    text: str
    char_start: int
    char_end: int
    overlap_with_prev_chars: int = 0

class SearchResult(BaseModel):
    chunk_id: str
    doc_id: str
    collection: CollectionName
    source_path: str
    source_type: DocumentSourceType
    text: str
    score: float = Field(..., ge=0.0, le=1.0)
    rank_in_collection: int = Field(..., description="在所属 Collection 内的排名，RRF 融合用")
    metadata: dict = Field(default_factory=dict)
    doc_title: Optional[str] = None
    degraded: bool = Field(default=False, description="若为 True 表示此结果来自降级路径")

class MultiSearchResult(BaseModel):
    query_text: str
    results_by_collection: dict[CollectionName, list[SearchResult]]
    merged_top_k: list[SearchResult] = Field(..., description="按 merge_strategy 合并后的 top_k")
    merge_strategy: Literal["rrf", "weighted"]
    total_matched_by_collection: dict[CollectionName, int]
    elapsed_ms: int
    degraded: bool = Field(default=False)

class SyncResult(BaseModel):
    """git hook / 手动单文件同步结果"""
    file_path: str
    event: Literal["add", "modify", "delete"]
    doc_id: str
    action_taken: Literal["ingested", "unchanged", "updated", "deleted", "skipped"]
    chunks_affected: int
    elapsed_ms: int
```

---
