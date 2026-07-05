# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §
# [MODULE] zephyr.integration.vector_memory.collection_schemas
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.schema.schemas
# [CONSUMERS] collection_manager; design_principles; sqlite_metadata_store; in_process_vector_memory; faiss_collection_manager; bridge_layer; provenance_enforcer; index_health_monitor; migrate_chroma_to_faiss; mcp/vector_memory_server; tests
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 8 collections; 2 dimensions (512, 1024); hot/cold separation; COLLECTION_SCHEMAS keys match COLLECTION_NAMES
# [MODIFY-GUARD] collection_manager.py; design_principles.py; sqlite_metadata_store.py; in_process_vector_memory.py; faiss_collection_manager.py; bridge_layer.py; provenance_enforcer.py; index_health_monitor.py; migrate_chroma_to_faiss.py; mcp/vector_memory_server.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] COLLECTION_SCHEMAS keys match COLLECTION_NAMES; dimensions in ALLOWED_DIMENSIONS
# [TESTS] tests/memory/test_vector_memory.py; tests/kb/test_cross_layer_systems_red_team.py
# [A_module] module_id=MOD-INT_collection_schemas | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from zephyr.shared.schema.schemas import BASE_CONFIG
from zephyr.shared.io.paths import VMS_PERSIST_DIR

__all__: list[str] = [
    "ALLOWED_DIMENSIONS",
    "CHUNK_STRATEGIES_COLD",
    "CHUNK_STRATEGIES_HOT",
    "COLD_COLLECTIONS",
    "COLLECTION_NAMES",
    "COLLECTION_SCHEMAS",
    "HOT_COLLECTIONS",
    "TTL_MAP",
    "VMS_PERSIST_DIR",
    "CollectionInfo",
]

ALLOWED_DIMENSIONS: frozenset[int] = frozenset({512, 1024})

HOT_COLLECTIONS: frozenset[str] = frozenset({"decisions", "rules", "lessons", "knowledge"})
COLD_COLLECTIONS: frozenset[str] = frozenset({"blueprints", "session_snapshots", "execution_traces"})

CHUNK_STRATEGIES_HOT: frozenset[str] = frozenset({"semantic", "paragraph", "heading_aware", "rule_level", "ast_aware"})
CHUNK_STRATEGIES_COLD: frozenset[str] = frozenset({"section_aware", "session_level", "time_window"})

TTL_MAP: dict[str, int] = {
    "code_context": 90,
    "session_snapshots": 90,
    "execution_traces": 30,
}

COLLECTION_SCHEMAS: dict[str, dict[str, Any]] = {
    "decisions": {
        "dimension": 1024,
        "chunk_strategy": "semantic",
        "ttl_days": 0,
        "ai_autonomy_level": "supervised",
        "embedding_model": "BAAI/bge-m3",
        "hnsw:space": "cosine",
        "description": "任务决策记录——Orchestrator写入，CE/FLE消费，1024d BGE-M3",
        "writers": ["Orchestrator"],
        "readers": ["CE", "FLE"],
    },
    "code_context": {
        "dimension": 1024,
        "chunk_strategy": "ast_aware",
        "ttl_days": 90,
        "ai_autonomy_level": "autonomous",
        "embedding_model": "BAAI/bge-m3",
        "hnsw:space": "cosine",
        "description": "代码上下文片段——Script System+Orc写入，CE消费，AST-aware分块",
        "writers": ["ScriptSystem", "Orchestrator"],
        "readers": ["CE"],
    },
    "lessons": {
        "dimension": 1024,
        "chunk_strategy": "paragraph",
        "ttl_days": 0,
        "ai_autonomy_level": "autonomous",
        "embedding_model": "BAAI/bge-m3",
        "hnsw:space": "cosine",
        "description": "经验教训——FLE+Script System写入，CE+KB消费，继承自failure_patterns",
        "writers": ["FLE", "ScriptSystem"],
        "readers": ["CE", "KB"],
    },
    "knowledge": {
        "dimension": 1024,
        "chunk_strategy": "heading_aware",
        "ttl_days": 0,
        "ai_autonomy_level": "supervised",
        "embedding_model": "BAAI/bge-m3",
        "hnsw:space": "cosine",
        "description": "知识条目——KB写入，CE消费，继承自ke_entries",
        "writers": ["KB"],
        "readers": ["CE"],
    },
    "rules": {
        "dimension": 1024,
        "chunk_strategy": "rule_level",
        "ttl_days": 0,
        "ai_autonomy_level": "human-gated",
        "embedding_model": "BAAI/bge-m3",
        "hnsw:space": "cosine",
        "description": "治理规则——Governance写入，CE+Orc消费，继承自vibe_rules",
        "writers": ["Governance"],
        "readers": ["CE", "Orchestrator"],
    },
    "blueprints": {
        "dimension": 512,
        "chunk_strategy": "section_aware",
        "ttl_days": 0,
        "ai_autonomy_level": "supervised",
        "embedding_model": "BAAI/bge-small-zh-v1.5",
        "hnsw:space": "cosine",
        "description": "蓝图文档——Doc System写入，CE+Orc消费，512d bge-small",
        "writers": ["DocSystem"],
        "readers": ["CE", "Orchestrator"],
    },
    "session_snapshots": {
        "dimension": 512,
        "chunk_strategy": "session_level",
        "ttl_days": 90,
        "ai_autonomy_level": "autonomous",
        "embedding_model": "BAAI/bge-small-zh-v1.5",
        "hnsw:space": "cosine",
        "description": "会话压缩摘要——SessionManager写入，CE消费",
        "writers": ["SessionManager"],
        "readers": ["CE"],
    },
    "execution_traces": {
        "dimension": 512,
        "chunk_strategy": "time_window",
        "ttl_days": 30,
        "ai_autonomy_level": "autonomous",
        "embedding_model": "BAAI/bge-small-zh-v1.5",
        "hnsw:space": "cosine",
        "description": "运行时任务执行语义摘要——All systems写入，FLE+CE消费，替代runtime_logs",
        "writers": ["AllSystems"],
        "readers": ["FLE", "CE"],
    },
}

COLLECTION_NAMES: tuple[str, ...] = tuple(COLLECTION_SCHEMAS.keys())


class CollectionInfo(BaseModel):
    model_config = BASE_CONFIG

    name: str
    dimension: int = 0
    chunk_strategy: str = ""
    ttl_days: int = 0
    ai_autonomy_level: str = ""
    embedding_model: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    exists: bool = False
