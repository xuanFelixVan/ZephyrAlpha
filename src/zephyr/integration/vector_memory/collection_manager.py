# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §
# [MODULE] zephyr.integration.vector_memory.collection_manager
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.schema.schemas
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
# [A_module] module_id=MOD-INT_collection_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CollectionManager — MOD-INF-011 八大 Collection 全生命周期管理
================================================================
真源: blueprint.md §2

八大 Collection Schema
-----------------------
┌──────────────────┬──────────┬─────────────────────┬───────────┬────────────┐
│ name             │ dim      │ chunk_strategy       │ ttl_days  │ autonomy   │
├──────────────────┼──────────┼─────────────────────┼───────────┼────────────┤
│ decisions        │ 1024     │ semantic             │ permanent │ supervised │
│ code_context     │ 1024     │ ast_aware             │ 90        │ autonomous │
│ lessons          │ 1024     │ paragraph             │ permanent │ autonomous │
│ knowledge        │ 1024     │ heading_aware         │ permanent │ supervised │
│ rules            │ 1024     │ rule_level            │ permanent │ human-gated│
│ blueprints       │  512     │ section_aware         │ permanent │ supervised │
│ session_snapshots│  512     │ session_level         │ 90        │ autonomous │
│ execution_traces │  512     │ time_window           │ 30        │ autonomous │
└──────────────────┴──────────┴─────────────────────┴───────────┴────────────┘
"""

from __future__ import annotations

from typing import Final
import json
import logging
from pathlib import Path
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from zephyr.shared.io.paths import VMS_PERSIST_DIR
from zephyr.shared.schema.schemas import BASE_CONFIG

_logger = logging.getLogger(__name__)

ALLOWED_DIMENSIONS: Final[frozenset[int]] = frozenset({512, 1024})

HOT_COLLECTIONS: Final[frozenset[str]] = frozenset({"decisions", "rules", "lessons", "knowledge"})
COLD_COLLECTIONS: Final[frozenset[str]] = frozenset({"blueprints", "session_snapshots", "execution_traces"})

CHUNK_STRATEGIES_HOT: Final[frozenset[str]] = frozenset({"semantic", "paragraph", "heading_aware", "rule_level", "ast_aware"})
CHUNK_STRATEGIES_COLD: Final[frozenset[str]] = frozenset({"section_aware", "session_level", "time_window"})

TTL_MAP: Final[dict[str, int]] = {
    "code_context": 90,
    "session_snapshots": 90,
    "execution_traces": 30,
}


class VMSError(Exception):
    pass


class DesignPrincipleError(VMSError):
    pass


class ProvenanceMissingError(VMSError):
    pass


class DimensionError(DesignPrincipleError):
    pass


class ChunkStrategyError(DesignPrincipleError):
    pass


class TTLError(DesignPrincipleError):
    pass


class HotColdSeparationError(DesignPrincipleError):
    pass


class DesignPrinciplesEnforcer:
    ALLOWED_DIMENSIONS: ClassVar[frozenset[int]] = ALLOWED_DIMENSIONS
    HOT_COLLECTIONS: ClassVar[frozenset[str]] = HOT_COLLECTIONS
    COLD_COLLECTIONS: ClassVar[frozenset[str]] = COLD_COLLECTIONS

    @staticmethod
    def validate_dimension(dim: int) -> None:
        if dim not in ALLOWED_DIMENSIONS:
            raise DimensionError(f"嵌入维度 {dim} 不在白名单中。允许: {sorted(ALLOWED_DIMENSIONS)}")

    @staticmethod
    def validate_chunk_strategy(name: str, chunk_strategy: str) -> None:
        if name in HOT_COLLECTIONS and chunk_strategy in CHUNK_STRATEGIES_COLD:
            raise HotColdSeparationError(
                f"热数据 Collection '{name}' 不可使用冷数据分块策略 '{chunk_strategy}'。"
                f"允许: {sorted(CHUNK_STRATEGIES_HOT)}"
            )
        if name in COLD_COLLECTIONS and chunk_strategy in CHUNK_STRATEGIES_HOT:
            _logger.warning(
                "冷数据 Collection '%s' 使用了热数据分块策略 '%s'——可能不适合",
                name,
                chunk_strategy,
            )
        schema = COLLECTION_SCHEMAS.get(name, {})
        expected = schema.get("chunk_strategy", "")
        if expected and chunk_strategy != expected:
            _logger.warning(
                "Collection '%s' 的分块策略 '%s' 与蓝图预期 '%s' 不一致",
                name,
                chunk_strategy,
                expected,
            )

    @staticmethod
    def validate_ttl(name: str, ttl_days: int) -> None:
        expected_ttl = TTL_MAP.get(name)
        if expected_ttl is not None and ttl_days != expected_ttl:
            raise TTLError(f"Collection '{name}' 的 TTL 应为 {expected_ttl}d，实际 {ttl_days}d")

    @staticmethod
    def validate_provenance(metadata: dict[str, Any] | None) -> None:
        if metadata is None:
            raise ProvenanceMissingError("写入操作必须提供 provenance metadata")
        if "provenance" not in metadata and "origin" not in metadata:
            raise ProvenanceMissingError("provenance 缺失: metadata 必须包含 'origin' 或 'provenance' 字段")

    @staticmethod
    def validate_all(
        name: str,
        dim: int,
        chunk_strategy: str,
        ttl_days: int,
        strict: bool = True,
    ) -> None:
        DesignPrinciplesEnforcer.validate_dimension(dim)
        if strict:
            DesignPrinciplesEnforcer.validate_chunk_strategy(name, chunk_strategy)
            DesignPrinciplesEnforcer.validate_ttl(name, ttl_days)
        else:
            DesignPrinciplesEnforcer.validate_chunk_strategy(name, chunk_strategy)


COLLECTION_SCHEMAS: Final[dict[str, dict[str, Any]]] = {
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

COLLECTION_NAMES: Final[tuple[str, ...]] = tuple(COLLECTION_SCHEMAS.keys())


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


class CollectionManager:
    VMS_COLLECTION_NAMES: ClassVar[tuple[str, ...]] = COLLECTION_NAMES
    VMS_SCHEMAS: ClassVar[dict[str, dict[str, Any]]] = COLLECTION_SCHEMAS

    def __init__(self, persist_dir: Path | str | None = None, embedding_router: Any | None = None) -> None:
        self._persist_dir = Path(persist_dir) if persist_dir is not None else VMS_PERSIST_DIR
        self._persist_dir.mkdir(parents=True, exist_ok=True)
        self._client: Any | None = None
        self._embedding_router = embedding_router

    @property
    def client(self) -> Any:
        if self._client is None:
            import chromadb

            self._client = chromadb.PersistentClient(path=str(self._persist_dir))
        return self._client

    @property
    def persist_dir(self) -> Path:
        return self._persist_dir

    def create_collection(
        self,
        name: str,
        dim: int = 1024,
        chunk_strategy: str = "semantic",
        ttl_days: int = 0,
        ai_autonomy: str = "supervised",
        strict: bool = True,
    ) -> CollectionInfo:
        if name not in COLLECTION_SCHEMAS:
            raise KeyError(f"未知 Collection: {name}。允许值: {', '.join(COLLECTION_NAMES)}")

        DesignPrinciplesEnforcer.validate_all(name, dim, chunk_strategy, ttl_days, strict=strict)

        schema = COLLECTION_SCHEMAS[name]
        metadata = {
            "dimension": dim,
            "chunk_strategy": chunk_strategy,
            "ttl_days": ttl_days if ttl_days > 0 else 0,
            "ai_autonomy_level": ai_autonomy,
            "embedding_model": schema["embedding_model"],
            "hnsw:space": schema["hnsw:space"],
        }

        existing_names = {c.name for c in self.client.list_collections()}
        if name in existing_names:
            col = self.client.get_collection(name=name)
            return CollectionInfo(
                name=name,
                dimension=dim,
                chunk_strategy=chunk_strategy,
                ttl_days=ttl_days,
                ai_autonomy_level=ai_autonomy,
                embedding_model=schema["embedding_model"],
                metadata=metadata,
                exists=True,
            )

        self.client.create_collection(name=name, metadata=metadata)
        _logger.info("CollectionManager: 创建 Collection '%s' (%dd, %s, %s)", name, dim, chunk_strategy, ai_autonomy)
        return CollectionInfo(
            name=name,
            dimension=dim,
            chunk_strategy=chunk_strategy,
            ttl_days=ttl_days,
            ai_autonomy_level=ai_autonomy,
            embedding_model=schema["embedding_model"],
            metadata=metadata,
            exists=True,
        )

    def get_collection(self, name: str) -> Any:
        if name not in COLLECTION_SCHEMAS:
            raise KeyError(f"未知 Collection: {name}")
        return self.client.get_collection(name=name)

    def list_collections(self) -> list[CollectionInfo]:
        existing_names = {c.name for c in self.client.list_collections()}
        results: list[CollectionInfo] = []
        for name in COLLECTION_NAMES:
            schema = COLLECTION_SCHEMAS[name]
            exists = name in existing_names
            results.append(
                CollectionInfo(
                    name=name,
                    dimension=schema["dimension"],
                    chunk_strategy=schema["chunk_strategy"],
                    ttl_days=schema["ttl_days"],
                    ai_autonomy_level=schema["ai_autonomy_level"],
                    embedding_model=schema["embedding_model"],
                    metadata={
                        "dimension": schema["dimension"],
                        "chunk_strategy": schema["chunk_strategy"],
                        "ttl_days": schema["ttl_days"],
                        "ai_autonomy_level": schema["ai_autonomy_level"],
                        "embedding_model": schema["embedding_model"],
                        "hnsw:space": schema["hnsw:space"],
                    },
                    exists=exists,
                )
            )
        return results

    def migrate_collection(self, from_name: str, to_name: str) -> CollectionInfo:
        if from_name not in COLLECTION_SCHEMAS and to_name not in COLLECTION_SCHEMAS:
            raise KeyError(f"迁移需要至少一个目标在 COLLECTION_SCHEMAS 中: {from_name} → {to_name}")

        existing_names = {c.name for c in self.client.list_collections()}
        if from_name not in existing_names:
            raise KeyError(f"源 Collection 不存在: {from_name}")

        if to_name in existing_names:
            existing_col = self.client.get_collection(name=to_name)
            return CollectionInfo(
                name=to_name,
                dimension=int(existing_col.metadata.get("dimension", 0)),
                chunk_strategy=existing_col.metadata.get("chunk_strategy", ""),
                ttl_days=int(existing_col.metadata.get("ttl_days", 0)),
                ai_autonomy_level=existing_col.metadata.get("ai_autonomy_level", ""),
                embedding_model=existing_col.metadata.get("embedding_model", ""),
                metadata=dict(existing_col.metadata),
                exists=True,
            )

        schema = COLLECTION_SCHEMAS.get(to_name) or COLLECTION_SCHEMAS.get(from_name, {})
        source_col = self.client.get_collection(name=from_name)
        source_data = source_col.get(include=["documents", "metadatas", "embeddings"])

        metadata = {
            "dimension": schema.get("dimension", 1024),
            "chunk_strategy": schema.get("chunk_strategy", "semantic"),
            "ttl_days": schema.get("ttl_days", 0),
            "ai_autonomy_level": schema.get("ai_autonomy_level", "supervised"),
            "embedding_model": schema.get("embedding_model", "BAAI/bge-m3"),
            "hnsw:space": schema.get("hnsw:space", "cosine"),
            "migrated_from": from_name,
        }

        self.client.create_collection(name=to_name, metadata=metadata)

        if source_data["ids"]:
            target_col = self.client.get_collection(name=to_name)
            target_col.add(
                ids=source_data.get("ids", []),
                documents=source_data.get("documents", []),
                metadatas=source_data.get("metadatas", []),
                embeddings=source_data.get("embeddings"),
            )

        _logger.info(
            "CollectionManager: 迁移 Collection '%s' → '%s' (%d 条记录)",
            from_name,
            to_name,
            len(source_data.get("ids", [])),
        )
        return CollectionInfo(
            name=to_name,
            dimension=schema.get("dimension", 1024),
            chunk_strategy=schema.get("chunk_strategy", "semantic"),
            ttl_days=schema.get("ttl_days", 0),
            ai_autonomy_level=schema.get("ai_autonomy_level", "supervised"),
            embedding_model=schema.get("embedding_model", "BAAI/bge-m3"),
            metadata=metadata,
            exists=True,
        )

    def archive_collection(self, name: str) -> None:
        if name not in COLLECTION_SCHEMAS:
            raise KeyError(f"未知 Collection: {name}")

        existing_names = {c.name for c in self.client.list_collections()}
        if name not in existing_names:
            _logger.warning("CollectionManager: Collection '%s' 不存在，跳过归档", name)
            return

        self.client.delete_collection(name=name)
        _logger.info("CollectionManager: 已归档 Collection '%s'", name)

    def write_with_provenance(
        self,
        collection_name: str,
        content: str,
        metadata: dict[str, Any],
        doc_id: str | None = None,
    ) -> str:
        DesignPrinciplesEnforcer.validate_provenance(metadata)
        col = self.get_collection(collection_name)
        import uuid
        from datetime import UTC, datetime

        # 确定性业务 id 优先（治本幂等缺陷，向量 upsert 范式）；
        # 无 id 时回退 uuid+timestamp（向后兼容，旧调用方不 break）
        if doc_id is None:
            doc_id = f"{collection_name}::{datetime.now(UTC).strftime('%Y%m%dT%H%M%S')}::{uuid.uuid4().hex[:12]}"
        meta = self._flatten_metadata(metadata)
        meta["written_at"] = datetime.now(UTC).isoformat()

        # col.add → col.upsert（治本：同 doc_id 覆盖，消除重复垃圾堆叠）
        if self._embedding_router is not None:
            embedding = self._embedding_router.embed(content, collection_name)
            col.upsert(ids=[doc_id], documents=[content], metadatas=[meta], embeddings=[embedding])
        else:
            col.upsert(ids=[doc_id], documents=[content], metadatas=[meta])

        _logger.debug("CollectionManager: 写入 '%s' → %s (provenance validated)", content[:40], collection_name)
        return doc_id

    @staticmethod
    def _flatten_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
        flat: dict[str, Any] = {}
        for key, value in metadata.items():
            if isinstance(value, dict):
                flat[key] = json.dumps(value, ensure_ascii=False, sort_keys=True)
            else:
                flat[key] = value
        return flat

    def init_all_collections(self) -> list[CollectionInfo]:
        results: list[CollectionInfo] = []
        for name in COLLECTION_NAMES:
            schema = COLLECTION_SCHEMAS[name]
            info = self.create_collection(
                name=name,
                dim=schema["dimension"],
                chunk_strategy=schema["chunk_strategy"],
                ttl_days=schema["ttl_days"],
                ai_autonomy=schema["ai_autonomy_level"],
            )
            results.append(info)
        return results

    def purge_expired(self) -> dict[str, int]:
        from datetime import UTC, datetime

        now = datetime.now(UTC)
        purged: dict[str, int] = {}
        for name, ttl_days in TTL_MAP.items():
            if ttl_days <= 0:
                continue
            try:
                col = self.get_collection(name)
            except Exception:
                continue
            try:
                all_data = col.get(include=["metadatas"])
            except Exception:
                continue
            if not all_data or not all_data.get("ids"):
                continue
            expired_ids = []
            for doc_id, meta in zip(all_data["ids"], all_data.get("metadatas", []) or [], strict=False):
                written_at = meta.get("written_at", "") if meta else ""
                if not written_at:
                    continue
                try:
                    written_dt = datetime.fromisoformat(written_at)
                    if (now - written_dt).days > ttl_days:
                        expired_ids.append(doc_id)
                except (ValueError, TypeError):
                    continue
            if expired_ids:
                col.delete(ids=expired_ids)
                purged[name] = len(expired_ids)
                _logger.info(
                    "CollectionManager: purged %d expired docs from '%s' (ttl=%dd)", len(expired_ids), name, ttl_days
                )
        return purged
