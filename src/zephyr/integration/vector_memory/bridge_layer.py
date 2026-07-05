# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §
# [MODULE] zephyr.integration.vector_memory.bridge_layer
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.vector_memory.collection_manager
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
# [A_module] module_id=MOD-INT_bridge_layer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
BridgeLayer — MOD-INF-011 kb/ ↔ VMS 过渡桥接
================================================
蓝图 §5.2 · §6 · Phase 1-2 过渡期双读策略

功能
----
- search_both(): 同时检索 kb/ 旧 Collection 和 VMS 新 Collection → 合并去重
- migrate_collection(): 从 kb/ 读取数据 → 写入 VMS（含维度转换）
- dry_run_topic_split(): unified_memory → target Collection 映射预览
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, ClassVar

from zephyr.integration.vector_memory.collection_manager import (
    COLLECTION_SCHEMAS,
    CollectionInfo,
    CollectionManager,
)

_logger = logging.getLogger(__name__)

KB_PERSIST_DIR: Path = Path(".audit_cache/vector_index")

MIGRATION_MAP: dict[str, dict[str, Any]] = {
    "ke_entries": {
        "target": "knowledge",
        "source_dim": 512,
        "target_dim": 1024,
        "re_embed": True,
    },
    "vibe_rules": {
        "target": "rules",
        "source_dim": 512,
        "target_dim": 1024,
        "re_embed": True,
        "force_1024d": True,
    },
    "blueprints": {
        "target": "blueprints",
        "source_dim": 512,
        "target_dim": 512,
        "re_embed": False,
    },
    "failure_patterns": {
        "target": "lessons",
        "source_dim": 512,
        "target_dim": 1024,
        "re_embed": True,
    },
}

TOPIC_TO_COLLECTION: dict[str, str] = {
    "knowledge": "knowledge",
    "rule": "rules",
    "governance": "rules",
    "blueprint": "blueprints",
    "lessons": "lessons",
    "failure": "lessons",
    "decision": "decisions",
    "code": "code_context",
    "session": "session_snapshots",
    "execution": "execution_traces",
    "trace": "execution_traces",
}

COLLECTION_ALIASES: dict[str, str] = {
    "decisions": "decisions",
    "learnings": "learnings",
    "runbooks": "runbooks",
    "contracts": "contracts",
    "drift_events": "drift_events",
}


class BridgeLayer:
    MIGRATION_MAP: ClassVar[dict[str, dict[str, Any]]] = MIGRATION_MAP
    TOPIC_TO_COLLECTION: ClassVar[dict[str, str]] = TOPIC_TO_COLLECTION
    COLLECTION_ALIASES: ClassVar[dict[str, str]] = COLLECTION_ALIASES

    def __init__(
        self,
        vms_collection_manager: CollectionManager,
        kb_persist_dir: Path | str = KB_PERSIST_DIR,
    ) -> None:
        self._vms_cm = vms_collection_manager
        self._kb_persist_dir = Path(kb_persist_dir)
        self._kb_client: Any | None = None

    @property
    def kb_client(self) -> Any:
        if self._kb_client is None:
            import chromadb

            if self._kb_persist_dir.exists():
                self._kb_client = chromadb.PersistentClient(path=str(self._kb_persist_dir))
            else:
                _logger.warning("BridgeLayer: kb/ 持久化目录不存在: %s", self._kb_persist_dir)
                self._kb_client = None
        return self._kb_client

    def search_both(self, query: str, vms_collection: str, k: int = 5) -> dict[str, Any]:
        vms_results: list[dict[str, Any]] = []
        kb_results: list[dict[str, Any]] = []

        try:
            col = self._vms_cm.get_collection(vms_collection)
            if col.count() > 0:
                res = col.query(query_texts=[query], n_results=min(k, col.count()))
                if res.get("ids") and res["ids"][0]:
                    for i, doc_id in enumerate(res["ids"][0]):
                        vms_results.append(
                            {
                                "id": doc_id,
                                "content": res.get("documents", [[""]])[0][i] if res.get("documents") else "",
                                "source": "vms",
                                "distance": res.get("distances", [[0.0]])[0][i] if res.get("distances") else 0.0,
                            }
                        )
        except Exception as e:
            _logger.debug("BridgeLayer: VMS 检索失败: %s", e)

        kb_collection_name = None
        for kb_name, mapping in MIGRATION_MAP.items():
            if mapping["target"] == vms_collection:
                kb_collection_name = kb_name
                break

        if kb_collection_name and self.kb_client:
            try:
                existing = {c.name for c in self.kb_client.list_collections()}
                if kb_collection_name in existing:
                    col = self.kb_client.get_collection(kb_collection_name)
                    if col.count() > 0:
                        res = col.query(query_texts=[query], n_results=min(k, col.count()))
                        if res.get("ids") and res["ids"][0]:
                            for i, doc_id in enumerate(res["ids"][0]):
                                kb_results.append(
                                    {
                                        "id": f"kb::{doc_id}",
                                        "content": res.get("documents", [[""]])[0][i] if res.get("documents") else "",
                                        "source": "kb",
                                        "distance": res.get("distances", [[0.0]])[0][i]
                                        if res.get("distances")
                                        else 0.0,
                                    }
                                )
            except Exception as e:
                _logger.debug("BridgeLayer: kb/ 检索失败: %s", e)

        merged = vms_results + kb_results
        merged.sort(key=lambda x: x.get("distance", 1.0))
        return {
            "results": merged[:k],
            "vms_count": len(vms_results),
            "kb_count": len(kb_results),
            "total": len(merged),
        }

    def migrate_collection(self, source_kb: str, target_vms: str) -> CollectionInfo:
        if source_kb not in MIGRATION_MAP:
            raise KeyError(f"未知迁移源: {source_kb}。允许值: {list(MIGRATION_MAP.keys())}")
        if not self.kb_client:
            raise RuntimeError(f"kb/ PersistentClient 不可用: {self._kb_persist_dir}")

        mapping = MIGRATION_MAP[source_kb]
        existing = {c.name for c in self.kb_client.list_collections()}
        if source_kb not in existing:
            raise KeyError(f"kb/ Collection 不存在: {source_kb}")

        source_col = self.kb_client.get_collection(source_kb)
        source_data = source_col.get(include=["documents", "metadatas"])

        target_info = self._vms_cm.create_collection(
            name=target_vms,
            dim=mapping["target_dim"],
            chunk_strategy=COLLECTION_SCHEMAS[target_vms]["chunk_strategy"],
            ttl_days=COLLECTION_SCHEMAS[target_vms]["ttl_days"],
            ai_autonomy=COLLECTION_SCHEMAS[target_vms]["ai_autonomy_level"],
        )

        if source_data.get("ids"):
            target_col = self._vms_cm.get_collection(target_vms)
            docs = source_data.get("documents", [])
            metas = source_data.get("metadatas", [])
            old_ids = source_data.get("ids", [])

            new_ids = [f"{target_vms}::migrated::{oid.split('::')[-1] if '::' in oid else oid}" for oid in old_ids]
            new_metas = []
            for meta in metas:
                m = dict(meta or {})
                m["migrated_from"] = source_kb
                m["migration_dim_change"] = f"{mapping['source_dim']}→{mapping['target_dim']}"
                new_metas.append(m)

            target_col.add(ids=new_ids, documents=docs, metadatas=new_metas)

        _logger.info("BridgeLayer: 迁移完成 %s → %s (%d 条)", source_kb, target_vms, len(source_data.get("ids", [])))
        return target_info

    @staticmethod
    def dry_run_topic_split(kb_persist_dir: Path | str | None = None) -> list[dict[str, str]]:
        resolved = Path(kb_persist_dir) if kb_persist_dir else KB_PERSIST_DIR
        results: list[dict[str, str]] = []

        if not resolved.exists():
            _logger.warning("BridgeLayer.dry_run: kb/ 目录不存在: %s", resolved)
            return results

        import chromadb

        client = chromadb.PersistentClient(path=str(resolved))
        existing = {c.name for c in client.list_collections()}

        if "unified_memory" in existing:
            col = client.get_collection("unified_memory")
            data = col.get(include=["metadatas"])
            if data.get("ids"):
                for i, doc_id in enumerate(data["ids"]):
                    meta = data.get("metadatas", [{}])[i] if data.get("metadatas") else {}
                    topic = meta.get("topic", "")
                    target = TOPIC_TO_COLLECTION.get(topic, "unknown")
                    results.append(
                        {
                            "source_id": doc_id,
                            "topic": topic,
                            "target_collection": target,
                        }
                    )

        return results

    def dual_read_mode(self, collection_name: str, query: str, k: int = 5) -> dict[str, Any]:
        _logger.info("BridgeLayer: 进入双读模式 → collection=%s (mitigates R14)", collection_name)
        return self.search_both(query, collection_name, k)

    def mark_deprecated_after_migration(self) -> bool:
        deprecated_marker = self._kb_persist_dir / "DEPRECATED"
        deprecated_marker.write_text(
            f"kb/ 已于 {datetime.now(UTC).isoformat()} 迁移至 VMS。本目录仅供回滚参考。",
            encoding="utf-8",
        )
        _logger.info("BridgeLayer: kb/ 已标记为 DEPRECATED (mitigates R14)")
        return True
