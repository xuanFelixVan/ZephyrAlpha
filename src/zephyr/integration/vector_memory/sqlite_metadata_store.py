# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §
# [MODULE] zephyr.integration.vector_memory.sqlite_metadata_store
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
# [A_module] module_id=MOD-INT_sqlite_metadata_store | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
SQLiteMetadataStore — VMS 元数据存储 (SQLite WAL + FTS5 BM25)
==============================================================
真源: VMS 蓝图 §12.3 · 迁自 BridgeLayer / ChromaDB 内嵌 SQLite

职责
----
  • 文档内容、metadata、provenance 持久化
  • FTS5 BM25 全文检索
  • Vector ID ↔ FAISS 索引 ID 双向映射
  • 写操作（add/delete）与读操作（search）并发安全 (WAL 模式)

表结构
------
  vms_documents:
    rowid          INTEGER PRIMARY KEY AUTOINCREMENT  -- 即 FAISS index ID
    vector_id      TEXT NOT NULL UNIQUE                -- 形如 "decisions::20260101T120000::abcdef123456"
    collection     TEXT NOT NULL
    content        TEXT NOT NULL
    metadata_json  TEXT
    provenance_json TEXT
    written_at     TEXT NOT NULL
"""

from __future__ import annotations

import atexit
import json
import logging
import sqlite3
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from zephyr.integration.vector_memory.collection_manager import (
    COLLECTION_NAMES,
    VMS_PERSIST_DIR,
)

_logger = logging.getLogger(__name__)


class ScoredHit:
    __slots__ = ("collection", "content", "id", "metadata", "provenance", "score", "score_breakdown")

    def __init__(
        self,
        id: str = "",
        content: str = "",
        score: float = 0.0,
        score_breakdown: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        provenance: dict[str, Any] | None = None,
        collection: str = "",
    ):
        self.id = id
        self.content = content
        self.score = score
        self.score_breakdown = score_breakdown or {}
        self.metadata = metadata or {}
        self.provenance = provenance or {}
        self.collection = collection

    def model_dump(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "score": self.score,
            "score_breakdown": self.score_breakdown,
            "metadata": self.metadata,
            "provenance": self.provenance,
            "collection": self.collection,
        }


class SearchTrace:
    __slots__ = ("collection", "hits", "latency_ms", "method", "query")

    def __init__(self, query: str, collection: str, hits: list[ScoredHit], latency_ms: float, method: str):
        self.query = query
        self.collection = collection
        self.hits = hits
        self.latency_ms = latency_ms
        self.method = method

    def model_dump(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "collection": self.collection,
            "hits": [h.model_dump() for h in self.hits],
            "latency_ms": self.latency_ms,
            "method": self.method,
        }


class SQLiteMetadataStore:
    def __init__(self, db_path: Path | str | None = None) -> None:
        if db_path is None:
            db_path = VMS_PERSIST_DIR / "vms_metadata.db"
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        # 5.12.7 修复：跨线程连接注册，防止线程池场景下其他线程连接泄漏
        self._all_conns: dict[int, sqlite3.Connection] = {}
        self._all_conns_lock = threading.Lock()
        atexit.register(self.close_all)

    @property
    def _conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.row_factory = sqlite3.Row
            self._local.conn = conn
            # 5.12.7 修复：注册到全局连接表，close_all 可关闭所有线程的连接
            tid = threading.get_ident()
            with self._all_conns_lock:
                self._all_conns[tid] = conn
        return self._local.conn

    def __enter__(self) -> "SQLiteMetadataStore":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.close_all()
        return False

    def close_all(self) -> None:
        """5.12.7 修复：关闭所有线程的连接（线程池场景下 close() 只关闭当前线程连接是不够的）。"""
        with self._all_conns_lock:
            for tid, conn in list(self._all_conns.items()):
                try:
                    conn.close()
                except Exception:
                    _logger.debug("close_all: failed to close conn for thread %s", tid, exc_info=True)
            self._all_conns.clear()
        # 清理当前线程 local 引用
        if hasattr(self._local, "conn"):
            self._local.conn = None

    def _ensure_tables(self) -> None:
        conn = self._conn
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vms_documents (
                rowid          INTEGER PRIMARY KEY AUTOINCREMENT,
                vector_id      TEXT NOT NULL UNIQUE,
                collection     TEXT NOT NULL,
                content        TEXT NOT NULL,
                metadata_json  TEXT DEFAULT '{}',
                provenance_json TEXT DEFAULT '{}',
                written_at     TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS vms_documents_fts
            USING fts5(content, collection)
        """)
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS vms_docs_ai AFTER INSERT ON vms_documents BEGIN
                INSERT INTO vms_documents_fts(rowid, content, collection)
                VALUES (new.rowid, new.content, new.collection);
            END
        """)
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS vms_docs_ad AFTER DELETE ON vms_documents BEGIN
                INSERT INTO vms_documents_fts(vms_documents_fts, rowid, content, collection)
                VALUES ('delete', old.rowid, old.content, old.collection);
            END
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS vms_id_map (
                vector_id TEXT NOT NULL UNIQUE,
                faiss_index_id INTEGER NOT NULL,
                collection TEXT NOT NULL
            )
        """)
        conn.commit()

    def add_document(
        self,
        vector_id: str,
        collection: str,
        content: str,
        metadata: dict[str, Any] | None = None,
        provenance: dict[str, Any] | None = None,
    ) -> int:
        self._ensure_tables()
        now = datetime.now(UTC).isoformat()
        conn = self._conn
        cursor = conn.execute(
            """INSERT INTO vms_documents (vector_id, collection, content, metadata_json, provenance_json, written_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                vector_id,
                collection,
                content,
                json.dumps(metadata or {}, ensure_ascii=False),
                json.dumps(provenance or {}, ensure_ascii=False),
                now,
            ),
        )
        conn.commit()
        return cursor.lastrowid or 0

    def map_id(self, vector_id: str, faiss_index_id: int, collection: str) -> None:
        self._ensure_tables()
        self._conn.execute(
            "INSERT OR REPLACE INTO vms_id_map (vector_id, faiss_index_id, collection) VALUES (?, ?, ?)",
            (vector_id, faiss_index_id, collection),
        )
        self._conn.commit()

    def get_faiss_id(self, collection: str) -> int:
        self._ensure_tables()
        cursor = self._conn.execute(
            "SELECT COUNT(*) AS cnt FROM vms_id_map WHERE collection = ?",
            (collection,),
        )
        row = cursor.fetchone()
        return row["cnt"]

    def get_vector_id_by_faiss_id(self, faiss_index_id: int, collection: str) -> str | None:
        self._ensure_tables()
        cursor = self._conn.execute(
            "SELECT vector_id FROM vms_id_map WHERE faiss_index_id = ? AND collection = ?",
            (faiss_index_id, collection),
        )
        row = cursor.fetchone()
        return row["vector_id"] if row else None

    def get_vector_ids_by_faiss_ids(self, faiss_index_ids: list[int], collection: str) -> dict[int, str]:
        self._ensure_tables()
        if not faiss_index_ids:
            return {}
        placeholders = ",".join("?" for _ in faiss_index_ids)
        cursor = self._conn.execute(
            f"SELECT vector_id, faiss_index_id FROM vms_id_map WHERE faiss_index_id IN ({placeholders}) AND collection = ?",
            [*faiss_index_ids, collection],
        )
        return {row["faiss_index_id"]: row["vector_id"] for row in cursor.fetchall()}

    def search_fts(
        self,
        query: str,
        collection: str,
        k: int = 5,
    ) -> list[ScoredHit]:
        self._ensure_tables()
        conn = self._conn
        query_fts = " OR ".join(f'"{w}"' for w in query.split() if len(w) >= 2)
        if not query_fts:
            query_fts = query

        cursor = conn.execute(
            """SELECT d.rowid, d.vector_id, d.collection, d.content, d.metadata_json, d.provenance_json,
                      fts.rank AS rank
               FROM vms_documents_fts fts
               JOIN vms_documents d ON d.rowid = fts.rowid
               WHERE vms_documents_fts MATCH ? AND d.collection = ?
               ORDER BY rank
               LIMIT ?""",
            (query_fts, collection, k),
        )
        rows = cursor.fetchall()
        hits: list[ScoredHit] = []
        max_rank = max((r["rank"] or 1.0 for r in rows), default=1.0)
        for row in rows:
            rank = row["rank"] or 1.0
            normalized = min(rank / max_rank, 1.0) if max_rank > 0 else 0.0
            hits.append(
                ScoredHit(
                    id=row["vector_id"],
                    content=row["content"],
                    score=normalized,
                    score_breakdown={"bm25_raw": rank, "bm25_norm": normalized},
                    metadata=json.loads(row["metadata_json"] or "{}"),
                    provenance=json.loads(row["provenance_json"] or "{}"),
                    collection=row["collection"],
                )
            )
        return hits

    def get_documents_by_ids(self, vector_ids: list[str]) -> dict[str, ScoredHit]:
        self._ensure_tables()
        if not vector_ids:
            return {}
        placeholders = ",".join("?" for _ in vector_ids)
        cursor = self._conn.execute(
            f"""SELECT rowid, vector_id, collection, content, metadata_json, provenance_json
                FROM vms_documents
                WHERE vector_id IN ({placeholders})""",
            vector_ids,
        )
        result: dict[str, ScoredHit] = {}
        for row in cursor.fetchall():
            result[row["vector_id"]] = ScoredHit(
                id=row["vector_id"],
                content=row["content"],
                score=0.0,
                metadata=json.loads(row["metadata_json"] or "{}"),
                provenance=json.loads(row["provenance_json"] or "{}"),
                collection=row["collection"],
            )
        return result

    def delete_by_collection(self, collection: str) -> int:
        self._ensure_tables()
        conn = self._conn
        cursor = conn.execute("DELETE FROM vms_documents WHERE collection = ?", (collection,))
        conn.execute("DELETE FROM vms_id_map WHERE collection = ?", (collection,))
        conn.commit()
        return cursor.rowcount

    def count_by_collection(self, collection: str) -> int:
        self._ensure_tables()
        cursor = self._conn.execute("SELECT COUNT(*) AS cnt FROM vms_documents WHERE collection = ?", (collection,))
        row = cursor.fetchone()
        return row["cnt"] if row else 0

    def health_check(self) -> dict[str, Any]:
        self._ensure_tables()
        result: dict[str, Any] = {"collections": {}, "total_docs": 0}
        for name in COLLECTION_NAMES:
            cnt = self.count_by_collection(name)
            result["collections"][name] = {"docs": cnt}
            result["total_docs"] += cnt
        return result

    def close(self) -> None:
        # 5.12.7 修复：原 close() 只关闭当前线程连接，线程池中其他线程连接泄漏；
        # 现委托 close_all() 关闭所有线程连接
        self.close_all()
