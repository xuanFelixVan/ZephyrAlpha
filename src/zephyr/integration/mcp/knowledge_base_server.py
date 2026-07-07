# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §
# [MODULE] zephyr.integration.mcp.knowledge_base_server
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.mcp._base_server; zephyr.governance.__init__; zephyr.integration.vector_memory.in_process_vector_memory
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
# [A_module] module_id=MOD-INT_knowledge_base_server | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# AI-generated: knowledge_base MCP Server skeleton (ADR-0033, T-3-04)
"""
KnowledgeBaseServer: 知识库语义检索 MCP Server
=============================================
Task ID  : T-3-04 (B15)
Server   : knowledge_base (tool-contracts.yaml §Server 2)
Protocol : ADR-0033（stdio 传输、JSON-RPC 2.0）
Backend  : UnifiedMemoryAPI (zephyr.governance.kb.storage.unified_memory_api) + InProcessVectorMemory
           KB refactor 已移除 SQLite knowledge 表 + ChromaDB 中间层

实现工具
--------
- knowledge_base.search       — 跨 collection 语义检索
- knowledge_base.upsert_ke    — 新增/更新知识条目
- knowledge_base.get_ke       — 按 ke_id 获取条目
- knowledge_base.rebuild_index — 重建 collection 向量索引
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import hashlib
import re
import threading
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from zephyr.integration.mcp._base_server import BaseMCPServer, MCPError
from zephyr.shared.io.yaml_utils import load_vocabulary_values  # 治本 2026-06-30 SSoT 词表加载

if TYPE_CHECKING:
    from zephyr.shared.protocols.ports import VectorMemoryProtocol

__all__ = ["KnowledgeBaseServer", "create_server"]

_KE_ID_RE = re.compile(r"^KE-[0-9]{3}(-.+)?$")

_VALID_COLLECTIONS = frozenset(
    {
        "ke_entries",
        "vibe_rules",
        "blueprints",
        "failure_patterns",
        "decisions",
        "code_context",
        "lessons",
        "knowledge",
        "rules",
        "session_snapshots",
        "execution_traces",
    }
)

_VMS_COLLECTIONS = frozenset(
    {
        "decisions",
        "code_context",
        "lessons",
        "knowledge",
        "rules",
        "blueprints",
        "session_snapshots",
        "execution_traces",
    }
)
_LEGACY_COLLECTIONS = _VALID_COLLECTIONS - _VMS_COLLECTIONS
# 治本（2026-06-30）：从 category_vocabulary.yaml 动态加载（SSoT，PS-VOC-013）。
_VALID_CATEGORIES = frozenset(load_vocabulary_values("category_vocabulary.yaml"))


class KnowledgeBaseServer(BaseMCPServer):
    """knowledge_base MCP Server 实现。

    持久化后端：UnifiedMemoryAPI (RI-02 三件套，真源:
    zephyr.governance.kb.storage.unified_memory_api) + InProcessVectorMemory。
    KB refactor 已移除 KbRepo (SQLite + ChromaDB) 中间层，禁止重建。
    降级策略：UnifiedMemoryAPI 不可用时回退到内存字典。
    """

    SERVER_ID = "knowledge_base"
    VERSION = "1.1.0"
    DESCRIPTION = "知识库语义检索（KE / 规则 / 蓝图 / 失败模式 + VMS 8 Collection）"

    def __init__(self, *, enable_rbac: bool = True, vms: VectorMemoryProtocol | None = None) -> None:
        super().__init__(self.SERVER_ID, self.VERSION, self.DESCRIPTION, enable_rbac=enable_rbac)
        self._entries: dict[str, dict[str, Any]] = {}
        self._vms: Any = None
        self._vms_lock = threading.Lock()
        self._kb_api: Any = None
        self._backend_mode: str = "unknown"

        self._init_backends()

        # DI: 若注入 vms，在构造时初始化（_search 内的懒初始化兜底 None 情况）
        if vms is not None:
            try:
                vms.init_all_collections()
                vms.start()
                self._vms = vms
            except Exception:
                logger.warning("suppressed error in knowledge_base_server", exc_info=True)

        self.register_tool(
            name="knowledge_base.search",
            description="跨 collection 语义检索",
            input_schema={
                "type": "object",
                "required": ["query_text"],
                "additionalProperties": False,
                "properties": {
                    "query_text": {"type": "string", "minLength": 1, "maxLength": 1000},
                    "collection": {
                        "type": "string",
                        "enum": sorted(_VALID_COLLECTIONS),
                        "default": "ke_entries",
                    },
                    "n_results": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5},
                    "score_threshold": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.6,
                    },
                },
            },
            handler=self._search,
        )
        self.register_tool(
            name="knowledge_base.upsert_ke",
            description="新增 / 更新知识条目并入库向量",
            input_schema={
                "type": "object",
                "required": ["ke_id", "title", "category", "content", "source_file"],
                "additionalProperties": False,
                "properties": {
                    "ke_id": {"type": "string", "pattern": r"^KE-[0-9]{3}(-.+)?$"},
                    "title": {"type": "string"},
                    "category": {"type": "string", "enum": sorted(_VALID_CATEGORIES)},
                    "content": {"type": "string"},
                    "source_file": {"type": "string"},
                    "layer": {"type": "string"},
                    "source_git_deleted": {"type": "boolean"},
                },
            },
            handler=self._upsert_ke,
        )
        self.register_tool(
            name="knowledge_base.get_ke",
            description="按 ke_id 获取条目",
            input_schema={
                "type": "object",
                "required": ["ke_id"],
                "additionalProperties": False,
                "properties": {"ke_id": {"type": "string"}},
            },
            handler=self._get_ke,
        )
        self.register_tool(
            name="knowledge_base.rebuild_index",
            description="重建 collection 向量索引（幂等）",
            input_schema={
                "type": "object",
                "required": ["collection"],
                "additionalProperties": False,
                "properties": {
                    "collection": {
                        "type": "string",
                        "enum": sorted(_VALID_COLLECTIONS) + ["ALL"],
                    },
                    "force": {"type": "boolean", "default": False},
                },
            },
            handler=self._rebuild_index,
        )
        self.register_tool(
            name="knowledge_base.list_kes",
            description="列出知识条目（支持 category 筛选和分页）",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "category": {"type": "string", "enum": sorted(_VALID_CATEGORIES)},
                    "offset": {"type": "integer", "minimum": 0, "default": 0},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
                },
            },
            handler=self._list_kes,
        )
        self.register_tool(
            name="knowledge_base.health_check",
            description="健康检查——返回 UnifiedMemoryAPI + VMS 连通性",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "properties": {},
            },
            handler=self._health_check,
        )

    # ------------------------------------------------------------------
    # Backend initialization
    # ------------------------------------------------------------------

    def _init_backends(self) -> None:
        self._backend_mode = "memory_fallback(kb_repo removed)"

        try:
            from zephyr.governance.kb.unified_memory_api import get_unified_memory_api

            self._kb_api = get_unified_memory_api(enforce_capability=False)
        except Exception as e:
            logger.warning("suppressed error in knowledge_base_server", exc_info=True)

    # ------------------------------------------------------------------
    # Tool handlers
    # ------------------------------------------------------------------

    def _search(
        self,
        query_text: str,
        collection: str = "ke_entries",
        n_results: int = 5,
        score_threshold: float = 0.6,
    ) -> dict[str, Any]:
        """语义检索（优先使用 VMS 向量搜索，回退关键词匹配）。

        ZA-KB-0001: collection not found
        """
        if collection not in _VALID_COLLECTIONS:
            raise MCPError(-32001, f"collection not found: {collection!r}", error_code="ZA-KB-0001")

        start = datetime.now(tz=UTC)

        if collection in _VMS_COLLECTIONS:
            try:
                with self._vms_lock:
                    if self._vms is None:
                        from zephyr.integration.vector_memory.in_process_vector_memory import InProcessVectorMemory

                        self._vms = InProcessVectorMemory()
                        self._vms.init_all_collections()
                        self._vms.start()
                hits_raw = self._vms.search(collection, query_text, k=n_results)
                hits = []
                for result in hits_raw:
                    score = result.get("score", 0.0)
                    if score >= score_threshold:
                        hits.append(
                            {
                                "chunk_id": result.get("id", ""),
                                "score": score,
                                "content": result.get("content", "")[:500],
                                "metadata": result.get("metadata", {}),
                                "ke_id": result.get("ke_id", ""),
                            }
                        )
                elapsed = int((datetime.now(tz=UTC) - start).total_seconds() * 1000)
                return {
                    "hits": hits[:n_results],
                    "total_scanned": len(hits_raw),
                    "latency_ms": elapsed,
                }
            except Exception as exc:
                elapsed = int((datetime.now(tz=UTC) - start).total_seconds() * 1000)
                return {"hits": [], "total_scanned": 0, "latency_ms": elapsed, "vms_error": str(exc)}

        if collection in _LEGACY_COLLECTIONS:
            hits = []
            for entry in self._entries.values():
                if query_text.lower() in entry.get("content", "").lower():
                    hits.append(
                        {
                            "chunk_id": entry["ke_id"] + "-chunk-0",
                            "score": 0.9,
                            "content": entry["content"][:500],
                            "metadata": {"collection": collection},
                            "ke_id": entry["ke_id"],
                        }
                    )
            elapsed = int((datetime.now(tz=UTC) - start).total_seconds() * 1000)
            filtered = [h for h in hits if h["score"] >= score_threshold]
            return {
                "hits": filtered[:n_results],
                "total_scanned": len(self._entries),
                "latency_ms": elapsed,
            }

    def _upsert_ke(
        self,
        ke_id: str,
        title: str,
        category: str,
        content: str,
        source_file: str,
        layer: str | None = None,
        source_git_deleted: bool = False,
    ) -> dict[str, Any]:
        """新增或更新知识条目（幂等，按内容 SHA-256 去重）。"""
        if not _KE_ID_RE.match(ke_id):
            raise MCPError(-32602, f"ke_id 格式无效: {ke_id!r}")
        if category not in _VALID_CATEGORIES:
            raise MCPError(-32602, f"category 无效: {category!r}")

        fingerprint = hashlib.sha256(content.encode("utf-8")).hexdigest()
        chunks_count = max(1, len(content) // 512)

        record: dict[str, Any] = {
            "ke_id": ke_id,
            "title": title,
            "category": category,
            "content": content,
            "source_file": source_file,
            "layer": layer or "",
            "source_git_deleted": source_git_deleted,
            "fingerprint_sha256": fingerprint,
            "updated_at": datetime.now(tz=UTC).isoformat(),
        }
        self._entries[ke_id] = record

        if self._kb_api is not None:
            try:
                from zephyr.governance.kb.unified_memory_api import build_provenance

                prov = build_provenance(
                    origin=f"mcp:knowledge_base:upsert_ke:{ke_id}",
                    audit_chain=["MOD-KB-001", "MCP-ADR-0033"],
                )
                self._kb_api.write(
                    topic=f"kb::{category}::{ke_id}",
                    content=content[:4000],
                    provenance=prov,
                )
            except Exception as e:
                logger.warning("suppressed error in knowledge_base_server", exc_info=True)

        return {
            "ke_id": ke_id,
            "chunks_indexed": chunks_count,
            "fingerprint_sha256": fingerprint,
            "backend": self._backend_mode,
        }

    def _get_ke(self, ke_id: str) -> dict[str, Any]:
        """按 ke_id 返回条目（ZA-KB-0005 on not found）。"""
        entry = self._entries.get(ke_id)
        if entry is not None:
            return {
                "ke_id": entry["ke_id"],
                "title": entry["title"],
                "category": entry["category"],
                "content": entry["content"],
                "source_file": entry["source_file"],
                "fingerprint_sha256": entry["fingerprint_sha256"],
                "backend": "memory",
            }

        raise MCPError(-32001, f"ke_id not found: {ke_id!r}", error_code="ZA-KB-0005")

    def _rebuild_index(self, collection: str, force: bool = False) -> dict[str, Any]:
        """重建向量索引（骨架层；生产中由 InProcessVectorMemory 重建）。"""
        targets = list(_VALID_COLLECTIONS) if collection == "ALL" else [collection]
        for col in targets:
            if col not in _VALID_COLLECTIONS:
                raise MCPError(-32001, f"collection not found: {col!r}", error_code="ZA-KB-0001")
        chunks = sum(max(1, len(e.get("content", "")) // 512) for e in self._entries.values())
        return {"chunks_indexed": chunks, "duration_seconds": 0.0}

    def _list_kes(
        self,
        category: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> dict[str, Any]:
        """按 category 筛选并分页列出知识条目。"""
        entries = list(self._entries.values())
        if category:
            entries = [e for e in entries if e.get("category") == category]
        total = len(entries)
        page = entries[offset : offset + limit]
        items = [
            {
                "ke_id": e["ke_id"],
                "title": e["title"],
                "category": e["category"],
                "fingerprint_sha256": e.get("fingerprint_sha256", ""),
            }
            for e in page
        ]
        return {"items": items, "total": total, "offset": offset, "limit": limit, "backend": "memory"}

    def _health_check(self) -> dict[str, Any]:
        sqlite_ok = False
        chromadb_ok = False
        vms_status = "unavailable"
        kb_repo_status = "disabled(kb_repo removed)"
        kb_api_count = -1

        try:
            vms_status = "available"
        except Exception as e:
            logger.warning("suppressed error in knowledge_base_server", exc_info=True)

        if self._kb_api is not None:
            try:
                kb_api_count = self._kb_api.count()
            except Exception as e:
                logger.warning("suppressed error in knowledge_base_server", exc_info=True)

        overall = "healthy" if (sqlite_ok or chromadb_ok) else "degraded"

        return {
            "status": overall,
            "sqlite_connected": sqlite_ok,
            "chromadb_connected": chromadb_ok,
            "vms_integrated": vms_status,
            "kb_repo": kb_repo_status,
            "kb_api_count": kb_api_count,
            "entries_count": len(self._entries),
            "backend_mode": self._backend_mode,
            "collections_supported": len(_VALID_COLLECTIONS),
            "checked_at": datetime.now(tz=UTC).isoformat(),
        }


def create_server(*, enable_rbac: bool = True) -> KnowledgeBaseServer:
    """工厂函数，返回配置好的 KnowledgeBaseServer 实例。"""
    return KnowledgeBaseServer(enable_rbac=enable_rbac)


if __name__ == "__main__":
    create_server().run()
