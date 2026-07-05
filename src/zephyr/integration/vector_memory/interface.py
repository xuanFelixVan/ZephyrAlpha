# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §
# [MODULE] zephyr.integration.vector_memory.interface
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INT_interface | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
VMS — Vector Memory Service 接口基类

向量化记忆服务。负责语义向量存储、检索与记忆管理。

核心职责：
  - 向量存储与检索（ChromaDB 0.6 后端）
  - 嵌入生成（BGE-M3 ONNX 模型）
  - 8 大 Collection 管理：decisions / code_context / lessons / knowledge
    rules / blueprints / session_snapshots / execution_traces
  - 递归分块 + 上下文窗口管理

扩展点：
  - VectorMemoryBase    : OCP VMS-MEM — 向量存储与检索
  - EmbeddingEngineBase : OCP VMS-EMB — 嵌入生成

过渡期说明（2026-05-05）：
  当前业务能力由 zephyr.knowledge.kb.unified_memory_api 承接（参见 vector-memory/__init__.py）。
  本文件定义 VMS 独立进程/Chroma 后端的规划接口——Phase B 骨架就位，Phase D 落地实现。
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar


@dataclass(frozen=True)
class MemoryEntry:
    """单条记忆条目"""

    entry_id: str
    collection: str
    content: str
    embedding: list[float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    ttl_seconds: int | None = None

    COLLECTIONS: ClassVar[tuple[str, ...]] = (
        "decisions",
        "code_context",
        "lessons",
        "knowledge",
        "rules",
        "blueprints",
        "session_snapshots",
        "execution_traces",
    )


class EmbeddingEngineBase(abc.ABC):
    """
    嵌入引擎抽象基类（OCP 扩展点 VMS-EMB）

    实现者要求：
      - encode(): 文本 → 向量
      - 默认模型：BGE-M3 ONNX
      - 维度：1024（BGE-M3）
    """

    @abc.abstractmethod
    def encode(self, text: str) -> list[float]:
        """单文本转为向量"""
        ...

    @abc.abstractmethod
    def encode_batch(self, texts: list[str]) -> list[list[float]]:
        """批量文本转为向量"""
        ...


class VectorMemoryBase(abc.ABC):
    """
    向量记忆基类（OCP 扩展点 VMS-MEM）

    实现者要求：
      - store(): 文本 → embed → ChromaDB insert
      - search(): query → embed → ChromaDB query（返回 top_k）
      - 默认使用 per-collection ChromaDB collections
      - 递归分块策略：默认 chunk_size=512 / overlap=64
    """

    @abc.abstractmethod
    def store(self, entry: MemoryEntry) -> str:
        """存储单条记忆条目，返回 entry_id"""
        ...

    @abc.abstractmethod
    def search(self, query: str, collection: str, top_k: int = 10) -> list[MemoryEntry]:
        """语义搜索：query → embed → top_k 结果"""
        ...

    @abc.abstractmethod
    def delete(self, entry_id: str, collection: str) -> bool:
        """删除指定记忆条目"""
        ...

    @abc.abstractmethod
    def get_collection_stats(self, collection: str) -> dict[str, int]:
        """返回 Collection 统计（条目数、总 token 数等）"""
        ...

    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
        """递归分块器——默认实现，可按需覆盖"""
        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap
        return chunks


__all__ = [
    "EmbeddingEngineBase",
    "MemoryEntry",
    "VectorMemoryBase",
]
