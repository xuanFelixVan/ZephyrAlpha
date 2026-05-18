# [BLUEPRINT] MOD-KB-001 | 03_modules/l01_infrastructure/knowledge-base/blueprint.md | §

# [MODULE] zephyr.kb.chromadb_init

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
ChromaDB 向量层初始化（T-2-10 · KB-legacy）
=============================================
依据：ADR-0031（ChromaDB persistent client）

⚠️ 此模块为 KB 模块旧版独立 ChromaDB 层 — 已被 VMS (MOD-INF-011) 取代为全系统主向量后端。
⚠️ VMS: src/zephyr/vector_memory/ — 8 Collection (decisions/code_context/lessons/knowledge/rules/blueprints/session_snapshots/execution_traces)
⚠️ 本模块保留于 KB 包内保证向后兼容 — KB 可通过 vector_bridge.VectorBridge 同步数据到 VMS。

物理路径
--------
- .audit_cache/vector_index/  ChromaDB 持久化根 (KB module only)
- .audit_cache/models/        embedding backbone 缓存

4 Collection (KB-module scope)
--------------------------------
1. ke_entries       KE 知识条目 chunks
2. vibe_rules       42 条治理规则 chunks
3. blueprints       蓝图文档 chunks
4. failure_patterns 失败模式库

Safety  : M（初始化目录 + 创建 collection，幂等）

用法
----
    from zephyr.kb.chromadb_init import init_chromadb, get_chroma_client

    init_chromadb()                    # 幂等，可重复调用
    client = get_chroma_client()       # 返回 PersistentClient
    collection = client.get_collection("ke_entries")
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from zephyr.shared.io.paths import MODELS_CACHE_DIR, VECTOR_INDEX_DIR
from zephyr.shared.schema.schemas import BASE_CONFIG

COLLECTION_NAMES = ("ke_entries", "vibe_rules", "blueprints", "failure_patterns")

_COLLECTION_METADATA: dict[str, dict[str, Any]] = {
    "ke_entries": {
        "hnsw:space": "cosine",
        "description": "KE knowledge entry chunks (docs/08_knowledge/**/ke-*.md)",
    },
    "vibe_rules": {
        "hnsw:space": "cosine",
        "description": "42 governance rule chunks (vibe-coding rules)",
    },
    "blueprints": {
        "hnsw:space": "cosine",
        "description": "Blueprint document chunks (docs/03_blueprints/**)",
    },
    "failure_patterns": {
        "hnsw:space": "cosine",
        "description": "Failure pattern entries (F-NNN)",
    },
}


class CollectionInfo(BaseModel):
    model_config = BASE_CONFIG

    name: str
    count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


_chroma_client: Any | None = None


def get_chroma_client(persist_dir: Path | str | None = None) -> Any:
    global _chroma_client
    if _chroma_client is not None:
        return _chroma_client
    import chromadb

    resolved = Path(persist_dir) if persist_dir is not None else VECTOR_INDEX_DIR
    resolved.mkdir(parents=True, exist_ok=True)
    _chroma_client = chromadb.PersistentClient(path=str(resolved))
    return _chroma_client


def init_chromadb(persist_dir: Path | str | None = None) -> list[CollectionInfo]:
    resolved = Path(persist_dir) if persist_dir is not None else VECTOR_INDEX_DIR
    resolved.mkdir(parents=True, exist_ok=True)
    MODELS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    client = get_chroma_client(resolved)
    existing = {c.name for c in client.list_collections()}

    results: list[CollectionInfo] = []
    for name in COLLECTION_NAMES:
        meta = _COLLECTION_METADATA.get(name, {"hnsw:space": "cosine"})
        if name not in existing:
            client.create_collection(name=name, metadata=meta)
            results.append(CollectionInfo(name=name, count=0, metadata=meta))
        else:
            col = client.get_collection(name=name)
            results.append(CollectionInfo(name=name, count=col.count(), metadata=meta))

    return results


def reset_chromadb(persist_dir: Path | str | None = None) -> list[CollectionInfo]:
    global _chroma_client
    client = get_chroma_client(persist_dir)
    for name in COLLECTION_NAMES:
        existing = {c.name for c in client.list_collections()}
        if name in existing:
            client.delete_collection(name=name)

    _chroma_client = None
    return init_chromadb(persist_dir)


def collection_status(persist_dir: Path | str | None = None) -> list[CollectionInfo]:
    client = get_chroma_client(persist_dir)
    results: list[CollectionInfo] = []
    for name in COLLECTION_NAMES:
        existing = {c.name for c in client.list_collections()}
        if name in existing:
            col = client.get_collection(name=name)
            meta = _COLLECTION_METADATA.get(name, {"hnsw:space": "cosine"})
            results.append(CollectionInfo(name=name, count=col.count(), metadata=meta))
        else:
            results.append(CollectionInfo(name=name, count=-1))
    return results


if __name__ == "__main__":
    infos = init_chromadb()
    for info in infos:
        print(f"  {info.name}: {info.count} records")
