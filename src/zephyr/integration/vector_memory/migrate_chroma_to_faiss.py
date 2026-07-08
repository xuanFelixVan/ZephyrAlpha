# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §
# [MODULE] zephyr.integration.vector_memory.migrate_chroma_to_faiss
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.io.paths; zephyr.integration.vector_memory.faiss_collection_manager; zephyr.integration.vector_memory.sqlite_metadata_store; zephyr.integration.vector_memory.collection_manager
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT_migrate_chroma_to_faiss | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ChromDB -> FAISS + SQLite WAL 数据迁移脚本
==========================================
VMS Blueprint §12 Step 5

入口: ChromaDB PersistentClient (data/vector_db/ + .audit_cache/vector_index/)
出口: FAISS IndexHNSW (.index) + SQLite WAL (vms_metadata.db)

使用方式:
    python src/zephyr/vector-memory/migrate_chroma_to_faiss.py [--dry-run]
"""

from __future__ import annotations

from typing import Final
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path

# Bootstrap: 基于 .git marker 定位仓库根（文件移动不 break，替代 parents[N] 硬编码）
_repo_root = Path(__file__).resolve()
while not (_repo_root / ".git").exists() and _repo_root != _repo_root.parent:
    _repo_root = _repo_root.parent
sys.path.insert(0, str(_repo_root / "src"))

from zephyr.shared.io.paths import VMS_PERSIST_DIR

# 5.129.3 修复: logging.basicConfig 移入 main() 避免模块级全局 root logger 副作用
_logger = logging.getLogger("chroma2faiss")

VMS_CHROMA_PATH: Final[Path] = VMS_PERSIST_DIR
FAISS_PATH: Final[Path] = VMS_PERSIST_DIR

KB_COLLECTION_TO_VMS: Final[dict[str, str]] = {
    "ke_entries": "knowledge",
}

COLLECTION_NAMES: Final[tuple[str, ...]] = (
    "decisions",
    "code_context",
    "lessons",
    "knowledge",
    "rules",
    "blueprints",
    "session_snapshots",
    "execution_traces",
)


def _init_faiss_backend():
    from zephyr.integration.vector_memory.faiss_collection_manager import FAISSCollectionManager
    from zephyr.integration.vector_memory.sqlite_metadata_store import SQLiteMetadataStore

    Path(FAISS_PATH).mkdir(parents=True, exist_ok=True)
    faiss_cm = FAISSCollectionManager(persist_dir=str(FAISS_PATH))
    meta_store = SQLiteMetadataStore(Path(FAISS_PATH) / "vms_metadata.db")
    return faiss_cm, meta_store


def _init_chroma_client(path: Path):
    import chromadb

    return chromadb.PersistentClient(path=str(path))


def migrate_vms_collection(
    faiss_cm,
    meta_store,
    chroma_client,
    collection_name: str,
    dry_run: bool = False,
) -> dict[str, int]:
    existing_names = {c.name for c in chroma_client.list_collections()}
    if collection_name not in existing_names:
        _logger.info("ChromaDB 无 Collection '%s'，跳过", collection_name)
        return {"total": 0, "migrated": 0, "skipped": 0}

    chroma_col = chroma_client.get_collection(collection_name)
    total = chroma_col.count()
    if total == 0:
        _logger.info("Collection '%s' 为空，跳过", collection_name)
        return {"total": 0, "migrated": 0, "skipped": 0}

    from zephyr.integration.vector_memory.collection_manager import COLLECTION_SCHEMAS

    schema = COLLECTION_SCHEMAS.get(collection_name, {})
    target_dim = schema.get("dimension", 1024)

    batch_size = 100
    migrated = 0
    skipped = 0

    for offset in range(0, total, batch_size):
        limit = min(batch_size, total - offset)
        data = chroma_col.get(
            include=["documents", "metadatas", "embeddings"],
            offset=offset,
            limit=limit,
        )

        ids = data.get("ids", [])
        documents = data.get("documents", [])
        metadatas = data.get("metadatas", []) or []
        embeddings = data.get("embeddings")

        for i in range(len(ids)):
            doc_id = ids[i]
            content = documents[i]
            meta = metadatas[i] if i < len(metadatas) else {}
            emb = embeddings[i] if embeddings is not None else None

            vector_id = doc_id

            if emb is not None and dry_run:
                migrated += 1
                continue

            if dry_run:
                migrated += 1
                continue

            try:
                import numpy as np

                vec = np.asarray(emb, dtype=np.float32)

                if vec.shape[0] != target_dim:
                    _logger.warning(
                        "维度不匹配: %s/%s 期望 %dd 实际 %dd -> 仅存储元数据",
                        collection_name,
                        doc_id,
                        target_dim,
                        vec.shape[0],
                    )
                    meta_copy = dict(meta)
                    meta_copy["migrated_from_chromadb"] = True
                    meta_copy["migrated_at"] = datetime.now(UTC).isoformat()
                    meta_copy["_migration_dim_mismatch"] = f"expected_{target_dim}d_got_{vec.shape[0]}d"
                    provenance = {"origin": "chroma2faiss_migration", "source": "ChromaDB"}
                    meta_copy.setdefault("provenance", provenance)
                    meta_store.add_document(
                        vector_id=vector_id,
                        collection=collection_name,
                        content=content,
                        metadata=meta_copy,
                        provenance=provenance,
                    )
                    skipped += 1
                    continue

                faiss_cm.add_vector(collection_name, vec)

                faiss_id = meta_store.get_faiss_id(collection_name)

                meta_copy = dict(meta)
                meta_copy["migrated_from_chromadb"] = True
                meta_copy["migrated_at"] = datetime.now(UTC).isoformat()

                provenance = {"origin": "chroma2faiss_migration", "source": "ChromaDB"}
                meta_copy.setdefault("provenance", provenance)

                meta_store.add_document(
                    vector_id=vector_id,
                    collection=collection_name,
                    content=content,
                    metadata=meta_copy,
                    provenance=provenance,
                )

                meta_store.map_id(vector_id, faiss_id, collection_name)
                migrated += 1

            except Exception as e:
                _logger.error("迁移失败 %s/%s: %s", collection_name, doc_id, e, exc_info=True)
                skipped += 1

        _logger.info(
            "  %s: offset=%d/%d, migrated=%d, skipped=%d",
            collection_name,
            offset + limit,
            total,
            migrated,
            skipped,
        )

    return {"total": total, "migrated": migrated, "skipped": skipped}


def migrate_kb_collection(
    faiss_cm,
    meta_store,
    kb_client,
    kb_collection: str,
    vms_collection: str,
    dry_run: bool = False,
) -> dict[str, int]:
    existing_names = {c.name for c in kb_client.list_collections()}
    if kb_collection not in existing_names:
        _logger.info("KB ChromaDB 无 Collection '%s'，跳过", kb_collection)
        return {"total": 0, "migrated": 0, "skipped": 0}

    chroma_col = kb_client.get_collection(kb_collection)
    total = chroma_col.count()
    if total == 0:
        _logger.info("KB Collection '%s' 为空，跳过", kb_collection)
        return {"total": 0, "migrated": 0, "skipped": 0}

    from zephyr.integration.vector_memory.collection_manager import COLLECTION_SCHEMAS

    schema = COLLECTION_SCHEMAS.get(vms_collection, {})
    target_dim = schema.get("dimension", 1024)

    migrated = 0
    skipped = 0

    data = chroma_col.get(
        include=["documents", "metadatas", "embeddings"],
    )

    ids = data.get("ids", [])
    documents = data.get("documents", [])
    metadatas = data.get("metadatas", []) or []
    embeddings = data.get("embeddings")

    for i in range(len(ids)):
        doc_id = ids[i]
        content = documents[i]
        meta = metadatas[i] if i < len(metadatas) else {}
        emb = embeddings[i] if embeddings is not None else None

        vector_id = f"kb::{vms_collection}::{doc_id}"

        if dry_run:
            migrated += 1
            continue

        try:
            import numpy as np

            vec = np.asarray(emb, dtype=np.float32)

            if vec.shape[0] != target_dim:
                _logger.warning(
                    "维度不匹配: KB %s/%s 期望 %dd 实际 %dd -> 仅存储元数据",
                    kb_collection,
                    doc_id,
                    target_dim,
                    vec.shape[0],
                )
                meta_copy = dict(meta)
                meta_copy["migrated_from_chromadb"] = True
                meta_copy["migrated_from_kb_collection"] = kb_collection
                meta_copy["migrated_at"] = datetime.now(UTC).isoformat()
                meta_copy["_migration_dim_mismatch"] = f"expected_{target_dim}d_got_{vec.shape[0]}d"
                provenance = {"origin": "chroma2faiss_migration", "source": f"KB::{kb_collection}"}
                meta_copy.setdefault("provenance", provenance)
                meta_store.add_document(
                    vector_id=vector_id,
                    collection=vms_collection,
                    content=content,
                    metadata=meta_copy,
                    provenance=provenance,
                )
                skipped += 1
                continue

            faiss_cm.add_vector(vms_collection, vec)
            faiss_id = meta_store.get_faiss_id(vms_collection)

            meta_copy = dict(meta)
            meta_copy["migrated_from_chromadb"] = True
            meta_copy["migrated_from_kb_collection"] = kb_collection
            meta_copy["migrated_at"] = datetime.now(UTC).isoformat()

            provenance = {"origin": "chroma2faiss_migration", "source": f"KB::{kb_collection}"}
            meta_copy.setdefault("provenance", provenance)

            meta_store.add_document(
                vector_id=vector_id,
                collection=vms_collection,
                content=content,
                metadata=meta_copy,
                provenance=provenance,
            )

            meta_store.map_id(vector_id, faiss_id, vms_collection)
            migrated += 1

        except Exception as e:
            _logger.error("迁移失败 KB %s/%s: %s", kb_collection, doc_id, e, exc_info=True)
            skipped += 1

    return {"total": total, "migrated": migrated, "skipped": skipped}


def main() -> None:
    # 5.129.3 修复: basicConfig 移入 main(), 仅脚本直接执行时配置 root logger
    logging.basicConfig(level=logging.INFO, format="%(name)s [%(levelname)s] %(message)s")
    dry_run = "--dry-run" in sys.argv

    _logger.info("=" * 60)
    _logger.info("ChromaDB -> FAISS 迁移脚本 (VMS Blueprint §12 Step 5)")
    _logger.info("模式: %s", "DRY-RUN" if dry_run else "EXECUTE")
    _logger.info("=" * 60)

    _logger.info("初始化 FAISS 后端...")
    faiss_cm, meta_store = _init_faiss_backend()

    _logger.info("确保 8 个 FAISS Collection 已创建...")
    from zephyr.integration.vector_memory.collection_manager import COLLECTION_SCHEMAS

    for name in COLLECTION_NAMES:
        schema = COLLECTION_SCHEMAS[name]
        faiss_cm.create_collection(
            name,
            dim=schema["dimension"],
            chunk_strategy=schema["chunk_strategy"],
            ttl_days=schema["ttl_days"],
            ai_autonomy=schema["ai_autonomy_level"],
        )

    _logger.info("连接 VMS ChromaDB (data/vector_db/)...")
    vms_client = _init_chroma_client(VMS_CHROMA_PATH)

    stats: dict[str, dict[str, int]] = {}

    _logger.info("\n[Phase 1] VMS ChromaDB Collection -> FAISS...")
    for name in COLLECTION_NAMES:
        stat = migrate_vms_collection(faiss_cm, meta_store, vms_client, name, dry_run=dry_run)
        stats[name] = stat

    _logger.info("\n[Phase 2] KB ChromaDB -> VMS Knowledge...")
    try:
        from zephyr.shared.io.paths import VECTOR_INDEX_DIR

        kb_client = _init_chroma_client(VECTOR_INDEX_DIR)
        for kb_col, vms_col in KB_COLLECTION_TO_VMS.items():
            stat = migrate_kb_collection(faiss_cm, meta_store, kb_client, kb_col, vms_col, dry_run=dry_run)
            stats[f"KB::{kb_col}"] = stat
    except ImportError:
        _logger.warning("无法导入 VECTOR_INDEX_DIR，跳过 KB ChromaDB 迁移")

    _logger.info("\n" + "=" * 60)
    _logger.info("迁移统计:")
    total_all = 0
    migrated_all = 0
    for name, stat in stats.items():
        if stat["total"] > 0:
            _logger.info(
                "  %-30s total=%4d  migrated=%4d  skipped=%d",
                name,
                stat["total"],
                stat["migrated"],
                stat["skipped"],
            )
            total_all += stat["total"]
            migrated_all += stat["migrated"]

    _logger.info("  %-30s total=%4d  migrated=%4d", "(合计)", total_all, migrated_all)

    if dry_run:
        _logger.info("\nDRY-RUN 完成。使用 --no-dry-run 执行实际迁移。")
    else:
        _logger.info("\n迁移完成。")

    meta_store.close()
    _logger.info("SQLite 连接已关闭。")


if __name__ == "__main__":
    main()
