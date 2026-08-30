# [BLUEPRINT] MOD-KNW-001 | docs/03_modules/_domain_knowledge/kb_engine/blueprint.md
# [MODULE] zephyr.knowledge.kb_engine
# [DOMAIN] D_KNOWLEDGE
# [DEPENDENCIES] 无（协议核心纯内存；sqlite连接/clock/audit_sink 全注入）
# [CONSUMERS] 运行时装配批（八Collection统一KB门面 / 质量分写回语义挂接点）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] collection词表闭合(注入校验); 条目版本号每次写递增且历史全留存; 回滚=以旧版本内容追加新版本(历史不可改); 删除仅标记(历史留存); FTS5索引与当前版本同步; 审计回调逐变更触发; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_knowledge/kb_engine/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] KbEngineError(占位 ZA-KNW-UNREGISTERED-KB-ENGINE)——未知collection/未知条目/重复创建/空标识/未知版本时抛
# [TESTS] tests/knowledge/test_kb_engine.py
# [A_module] module_id=MOD-KNW-001 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
KbEngine — 统一知识库引擎（MOD-KNW-001）。

B1-00128（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-002，C2 D-KNOW-06）：
LlamaIndex 式知识库单机版——八 Collection 通用 CRUD（collection 词表注入
校验）+ 条目版本号（每次写 version 递增 + 历史留存）+ 变更审计（注入
audit 回调）+ 按版本回滚 + FTS5 全文搜索（注入 sqlite 连接，测试用真
:memory: FTS5 表）。canonical 承接 KNW-019（B6 重登稿）归并。

查重分工：vector_memory/sqlite_metadata_store=向量集合元数据底座（本件为其
上层通用门面，不复用实现）；knowledge_quality_assessor=质量分计算（本件仅
提供质量分写回的元数据语义挂载点，不算分）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: conn 参数
#   fields: 参数 conn（无注解）
#   code: kb_engine.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: collections 参数
#   fields: 参数 collections（无注解）
#   code: kb_engine.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: kb_engine.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: audit_sink 参数
#   fields: 参数 audit_sink（无注解）
#   code: kb_engine.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① KbEngine
#   name_en: KbEngine
#   intro: 八 Collection 统一 KB 门面（CRUD + 版本 + 回滚 + FTS5 + 审计）。
#   desc: 八 Collection 统一 KB 门面（CRUD + 版本 + 回滚 + FTS5 + 审计）。；公共方法（定义序）: create, get, update, delete, history, rollback,…
#   inputs: conn collections clock audit_sink
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: KbEngine
#   downstream: 运行时装配批（八Collection统一KB门面 / 质量分写回语义挂接点）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
import sqlite3
from dataclasses import dataclass
from typing import Callable, Final, Iterable, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "AuditAction",
    "KbAuditRecord",
    "KbEngine",
    "KbEngineError",
    "KbEntry",
]

#: 默认八 Collection 词表（未注入时兜底；注入则全量校验）
_DEFAULT_COLLECTIONS: Final = (
    "knowledge",
    "decisions",
    "research",
    "factors",
    "strategies",
    "experiments",
    "events",
    "governance",
)

_FTS_TABLE: Final = "kb_fts"


class KbEngineError(Exception):
    """知识库引擎输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-KNW-UNREGISTERED-KB-ENGINE。
    """


class AuditAction:
    """变更审计动作词表（闭合）。"""

    CREATE: Final = "create"
    UPDATE: Final = "update"
    DELETE: Final = "delete"
    ROLLBACK: Final = "rollback"


@dataclass(frozen=True)
class KbEntry:
    """知识条目单版本视图（frozen；历史以 KbEntry 序列留存）。"""

    collection: str
    entry_id: str
    version: int
    content: str
    metadata: dict
    updated_at: datetime.datetime
    deleted: bool


@dataclass(frozen=True)
class KbAuditRecord:
    """变更审计载荷（注入 audit_sink 回调）。"""

    collection: str
    entry_id: str
    action: str
    version: int
    at: datetime.datetime


class KbEngine:
    """八 Collection 统一 KB 门面（CRUD + 版本 + 回滚 + FTS5 + 审计）。"""

    def __init__(
        self,
        *,
        conn: sqlite3.Connection,
        collections: Iterable[str] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
        audit_sink: Callable[[KbAuditRecord], None] | None = None,
    ) -> None:
        if conn is None:
            raise KbEngineError("sqlite 连接未注入（FTS5 索引强制依赖）")
        vocab = tuple(collections) if collections is not None else _DEFAULT_COLLECTIONS
        if not vocab:
            raise KbEngineError("collection 词表为空")
        seen: set[str] = set()
        for name in vocab:
            if not name or not isinstance(name, str):
                raise KbEngineError(f"非法 collection 名: {name!r}")
            if name in seen:
                raise KbEngineError(f"collection 词表重复: {name!r}")
            seen.add(name)
        self._collections: frozenset[str] = frozenset(vocab)
        self._conn = conn
        self._clock = clock or datetime.datetime.now
        self._audit_sink = audit_sink
        # 存储结构：{collection: {entry_id: [KbEntry, ...按版本递增...]}}
        self._store: dict[str, dict[str, list[KbEntry]]] = {c: {} for c in vocab}
        self._conn.execute(
            f"CREATE VIRTUAL TABLE IF NOT EXISTS {_FTS_TABLE} "
            "USING fts5(collection UNINDEXED, entry_id UNINDEXED, content)"
        )

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _require_collection(self, collection: str) -> None:
        if collection not in self._collections:
            raise KbEngineError(f"未知 collection: {collection!r}（词表闭合）")

    def _require_entry_id(self, entry_id: str) -> None:
        if not entry_id:
            raise KbEngineError("entry_id 为空")

    def _versions(self, collection: str, entry_id: str) -> list[KbEntry]:
        versions = self._store[collection].get(entry_id)
        if not versions:
            raise KbEngineError(f"未知条目: {collection}/{entry_id!r}")
        return versions

    def _current(self, collection: str, entry_id: str) -> KbEntry:
        return self._versions(collection, entry_id)[-1]

    def _live(self, collection: str, entry_id: str) -> KbEntry:
        entry = self._current(collection, entry_id)
        if entry.deleted:
            raise KbEngineError(f"条目已删除: {collection}/{entry_id!r}")
        return entry

    def _audit(self, collection: str, entry_id: str, action: str, version: int) -> None:
        record = KbAuditRecord(
            collection=collection,
            entry_id=entry_id,
            action=action,
            version=version,
            at=self._clock(),
        )
        _log.info("KB变更: %s %s/%s v%d", action, collection, entry_id, version)
        if self._audit_sink is not None:
            self._audit_sink(record)

    def _index(self, collection: str, entry_id: str, content: str) -> None:
        self._conn.execute(
            f"DELETE FROM {_FTS_TABLE} WHERE collection = ? AND entry_id = ?",
            (collection, entry_id),
        )
        self._conn.execute(
            f"INSERT INTO {_FTS_TABLE} (collection, entry_id, content) VALUES (?, ?, ?)",
            (collection, entry_id, content),
        )

    def _append(
        self,
        collection: str,
        entry_id: str,
        content: str,
        metadata: Mapping | None,
        *,
        deleted: bool = False,
    ) -> KbEntry:
        versions = self._store[collection].setdefault(entry_id, [])
        entry = KbEntry(
            collection=collection,
            entry_id=entry_id,
            version=len(versions) + 1,
            content=content,
            metadata=dict(metadata or {}),
            updated_at=self._clock(),
            deleted=deleted,
        )
        versions.append(entry)
        return entry

    # ── CRUD ─────────────────────────────────────────────────────────────

    def create(
        self,
        collection: str,
        entry_id: str,
        content: str,
        *,
        metadata: Mapping | None = None,
    ) -> KbEntry:
        """创建条目（version=1；重复创建 Fail-Closed）。"""
        self._require_collection(collection)
        self._require_entry_id(entry_id)
        if entry_id in self._store[collection]:
            raise KbEngineError(f"条目已存在: {collection}/{entry_id!r}（重复创建拒绝）")
        entry = self._append(collection, entry_id, content, metadata)
        self._index(collection, entry_id, content)
        self._audit(collection, entry_id, AuditAction.CREATE, entry.version)
        return entry

    def get(self, collection: str, entry_id: str) -> KbEntry:
        """读当前版本（未知/已删除 → Fail-Closed）。"""
        self._require_collection(collection)
        self._require_entry_id(entry_id)
        return self._live(collection, entry_id)

    def update(
        self,
        collection: str,
        entry_id: str,
        content: str,
        *,
        metadata: Mapping | None = None,
    ) -> KbEntry:
        """更新条目（version+1，历史留存，FTS 同步）。"""
        self._require_collection(collection)
        self._require_entry_id(entry_id)
        self._live(collection, entry_id)
        entry = self._append(collection, entry_id, content, metadata)
        self._index(collection, entry_id, content)
        self._audit(collection, entry_id, AuditAction.UPDATE, entry.version)
        return entry

    def delete(self, collection: str, entry_id: str) -> None:
        """删除条目（仅标记，历史留存，FTS 去索引）。"""
        self._require_collection(collection)
        self._require_entry_id(entry_id)
        current = self._live(collection, entry_id)
        entry = self._append(collection, entry_id, current.content, current.metadata, deleted=True)
        self._conn.execute(
            f"DELETE FROM {_FTS_TABLE} WHERE collection = ? AND entry_id = ?",
            (collection, entry_id),
        )
        self._audit(collection, entry_id, AuditAction.DELETE, entry.version)

    # ── 版本 / 回滚 ───────────────────────────────────────────────────────

    def history(self, collection: str, entry_id: str) -> list[KbEntry]:
        """全版本历史（含删除标记版本；按 version 递增）。"""
        self._require_collection(collection)
        self._require_entry_id(entry_id)
        return list(self._versions(collection, entry_id))

    def rollback(self, collection: str, entry_id: str, version: int) -> KbEntry:
        """按版本回滚：以目标版本内容追加新版本（历史不可改）。"""
        self._require_collection(collection)
        self._require_entry_id(entry_id)
        self._live(collection, entry_id)
        versions = self._versions(collection, entry_id)
        if version < 1 or version > len(versions):
            raise KbEngineError(f"未知版本: {collection}/{entry_id!r} v{version}（现存 1..{len(versions)}）")
        target = versions[version - 1]
        entry = self._append(collection, entry_id, target.content, target.metadata)
        self._index(collection, entry_id, target.content)
        self._audit(collection, entry_id, AuditAction.ROLLBACK, entry.version)
        return entry

    # ── 检索 ─────────────────────────────────────────────────────────────

    def list_entries(self, collection: str) -> list[KbEntry]:
        """Collection 内存活条目（按 entry_id 确定性排序）。"""
        self._require_collection(collection)
        out = [versions[-1] for entry_id, versions in self._store[collection].items() if not versions[-1].deleted]
        out.sort(key=lambda e: e.entry_id)
        return out

    def search(
        self,
        query: str,
        *,
        collection: str | None = None,
        limit: int = 10,
    ) -> list[KbEntry]:
        """FTS5 全文搜索（仅命中存活当前版本；按 (bm25, entry_id) 确定性排序）。"""
        if not query or not query.strip():
            raise KbEngineError("搜索串为空")
        if limit < 1:
            raise KbEngineError(f"非法 limit: {limit}")
        if collection is not None:
            self._require_collection(collection)
            rows = self._conn.execute(
                f"SELECT collection, entry_id, bm25({_FTS_TABLE}) AS rank FROM {_FTS_TABLE} "
                f"WHERE {_FTS_TABLE} MATCH ? AND collection = ? "
                "ORDER BY rank, entry_id LIMIT ?",
                (query, collection, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                f"SELECT collection, entry_id, bm25({_FTS_TABLE}) AS rank FROM {_FTS_TABLE} "
                f"WHERE {_FTS_TABLE} MATCH ? "
                "ORDER BY rank, entry_id, collection LIMIT ?",
                (query, limit),
            ).fetchall()
        out: list[KbEntry] = []
        for coll, entry_id, _rank in rows:
            versions = self._store[coll].get(entry_id)
            if versions and not versions[-1].deleted:
                out.append(versions[-1])
        return out
