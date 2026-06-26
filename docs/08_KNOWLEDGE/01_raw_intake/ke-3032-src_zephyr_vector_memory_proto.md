---
module_id: KE-2932
status: active
title: src/zephyr/vector-memory/protocol.py (experimental 产出)
category: module_blueprint
ttl: permanent
---

# src/zephyr/vector-memory/protocol.py (experimental 产出)

src/zephyr/vector-memory/protocol.py (experimental 产出)

from typing import Protocol, Literal

class VectorMemoryProtocol(Protocol):
    """两种实现必须共享的接口签名。"""

    async def ingest(self, doc: Document, idempotency_key: str | None = None) -> IngestResult: ...
    async def bulk_bootstrap(self, docs: list[Document], **kwargs) -> BootstrapResult: ...
    async def sync_document(self, file_path: str, event: Literal["add","modify","delete"]) -> SyncResult: ...
    async def update_document(self, doc_id: str, new_content: str, **kwargs) -> UpdateResult: ...
    async def delete_document(self, doc_id: str, **kwargs) -> DeleteResult: ...
    async def search(self, query_text: str, collection: CollectionName, **kwargs) -> list[SearchResult]: ...
    async def multi_search(self, query_text: str, collections: list[CollectionName], **kwargs) -> MultiSearchResult: ...
    async def get_by_id(self, doc_id: str) -> Document | None: ...
    async def stats(self) -> VMStats: ...
    async def reindex(self, **kwargs) -> ReindexResult: ...
    async def gc(self, **kwargs) -> GCResult: ...

class InProcessVectorMemory:
    """experimental（当前目标）：直接调 ChromaDB SDK，进程内异步协调。"""

class RemoteVectorMemory:
    """beta+（按需启用）：HTTP/gRPC Client，调独立 VMS 服务。"""
```

| Phase | 实施形态 | 运行方式 | 触发升级条件 |
|:-:|---------|---------|-------------|
| **experimental** | **`InProcessVectorMemory`（Python 库，当前目标）** | `from zephyr.vector_memory import get_vm` 进程内异步调用 | - |
| beta | `RemoteVectorMemory`（HTTP 服务） | `POST /v1/*` FastAPI 进程，业务层切依赖即可 | ≥1 个触发：<br>① 数据量 > 10GB 或 chunks > 500k<br>② 并发写入 ≥ 3 进程同时需要<br>③ embedding 模型 > 2GB 不宜多进程加载 |
| stable | `RemoteVectorMemory`（gRPC） | 同上但传输层换 gRPC | RPS > 500 |

**所有 API 均为 `async`**——项目用 asyncio 事件循环，进程内锁用 `asyncio.Lock()`（异步等待，不阻塞 loop），跨进程锁用 `filelock.FileLock()`（pytest 并发 / 多 Agent 共存）。**严禁使用 `threading.Lock`**（阻塞事件循环）。

---
