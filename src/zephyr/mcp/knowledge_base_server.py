# AI-generated: knowledge_base MCP Server skeleton (ADR-0033, T-3-04)
"""
KnowledgeBaseServer: 知识库语义检索 MCP Server
=============================================
Task ID  : T-3-04 (B15)
Server   : knowledge_base (tool_contracts.yaml §Server 2)
Protocol : ADR-0033（stdio 传输、JSON-RPC 2.0）
Backend  : knowledge_indexer.py (ADR-0031 ChromaDB) + SQLite knowledge 表

实现工具
--------
- knowledge_base.search       — 跨 collection 语义检索
- knowledge_base.upsert_ke    — 新增/更新知识条目
- knowledge_base.get_ke       — 按 ke_id 获取条目
- knowledge_base.rebuild_index — 重建 collection 向量索引
"""

from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from typing import Any

from zephyr.mcp._base_server import BaseMCPServer, MCPError

__all__ = ["KnowledgeBaseServer", "create_server"]

_KE_ID_RE = re.compile(r"^KE-[0-9]{3}(-.+)?$")

_VALID_COLLECTIONS = frozenset({"ke_entries", "vibe_rules", "blueprints", "failure_patterns"})
_VALID_CATEGORIES = frozenset(
    {
        "blueprint_decision",
        "strategy",
        "factor",
        "best_practice",
        "lesson_learned",
        "architecture",
        "risk_control",
        "data_governance",
        "operations",
        "compliance",
    }
)


class KnowledgeBaseServer(BaseMCPServer):
    """knowledge_base MCP Server 实现。

    骨架内置轻量内存存储（生产中替换为 KnowledgeIndexer + KbRepo 适配器）。
    """

    SERVER_ID = "knowledge_base"
    VERSION = "1.0.0"
    DESCRIPTION = "知识库语义检索（KE / 规则 / 蓝图 / 失败模式 4 个 collection）"

    def __init__(self) -> None:
        super().__init__(self.SERVER_ID, self.VERSION, self.DESCRIPTION)
        # 轻量内存存储（骨架层）
        self._entries: dict[str, dict[str, Any]] = {}

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
        """关键词模糊匹配（骨架层；生产中替换为 ChromaDB 向量检索）。

        ZA-KB-0001: collection not found
        """
        if collection not in _VALID_COLLECTIONS:
            raise MCPError(-32001, f"ZA-KB-0001: collection not found: {collection!r}")

        start = datetime.now(tz=UTC)
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
        return {"ke_id": ke_id, "chunks_indexed": chunks_count, "fingerprint_sha256": fingerprint}

    def _get_ke(self, ke_id: str) -> dict[str, Any]:
        """按 ke_id 返回条目（ZA-KB-0005 on not found）。"""
        entry = self._entries.get(ke_id)
        if entry is None:
            raise MCPError(-32001, f"ZA-KB-0005: ke_id not found: {ke_id!r}")
        return {
            "ke_id": entry["ke_id"],
            "title": entry["title"],
            "category": entry["category"],
            "content": entry["content"],
            "source_file": entry["source_file"],
            "fingerprint_sha256": entry["fingerprint_sha256"],
        }

    def _rebuild_index(self, collection: str, force: bool = False) -> dict[str, Any]:
        """重建向量索引（骨架层；生产中替换为 ChromaDB 重建调用）。"""
        targets = list(_VALID_COLLECTIONS) if collection == "ALL" else [collection]
        for col in targets:
            if col not in _VALID_COLLECTIONS:
                raise MCPError(-32001, f"ZA-KB-0001: collection not found: {col!r}")
        chunks = sum(max(1, len(e.get("content", "")) // 512) for e in self._entries.values())
        return {"chunks_indexed": chunks, "duration_seconds": 0.0}


def create_server() -> KnowledgeBaseServer:
    """工厂函数，返回配置好的 KnowledgeBaseServer 实例。"""
    return KnowledgeBaseServer()


if __name__ == "__main__":
    create_server().run()
