---
module_id: KE-2931
status: active
title: src/zephyr/vector-memory/in_process.py (experimental 产出)
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# src/zephyr/vector-memory/in_process.py (experimental 产出)

src/zephyr/vector-memory/in_process.py (experimental 产出)

class InProcessVectorMemory:  # implements VectorMemoryProtocol
    """experimental 默认实现。所有方法均为 async，依赖 ChromaDB SDK。"""

    def __init__(self, config: VMConfig) -> None: ...

    async def __aenter__(self) -> "InProcessVectorMemory": ...
    async def __aexit__(self, *args) -> None: ...

    # ───── Ingestion（三个入口场景）─────
    async def ingest(
        self,
        doc: Document,
        idempotency_key: str | None = None,
    ) -> IngestResult:
        """单文档入库。content_hash 未变返回 unchanged。用于程序化写入。"""

    async def bulk_bootstrap(
        self,
        docs: list[Document],
        batch_size: int = 50,
        on_progress: callable | None = None,
        checkpoint_path: str | None = None,
    ) -> BootstrapResult:
        """
        首次部署批量导入（200+ 文档）。遗漏 #1 补充。
        - 游标分批 embedding 避免 OOM
        - checkpoint_path 持久化已完成 doc_ids，断点续传
        - on_progress(done, total) 回调给 CLI/Dashboard
        使用场景：首次部署 / 向量库重建 / 迁移。
        """

    async def sync_document(
        self,
        file_path: str,
        event: Literal["add", "modify", "delete"],
    ) -> SyncResult:
        """
        单文件增量同步。遗漏 #1 补充（调整）。
        使用场景：git post-commit hook 主调用入口 / 手动单文件操作。
        - event='add' / 'modify'：读取文件 → 构建 Document → ingest/update
        - event='delete'：按 file_path 查 doc_id → delete_document(mode='hard')
        与 bulk_bootstrap 共享底层 ingest/update/delete，是增量流量的主入口。
        """

    # ───── Update & Delete（4 种 cascade）─────
    async def update_document(
        self,
        doc_id: str,
        new_content: str,
        new_metadata: dict | None = None,
        cascade: CascadeStrategy = CascadeStrategy.SUPERSEDE,
    ) -> UpdateResult:
        """
        更新已入库文档。四种 cascade 策略见 §3.2 表：
          - supersede（默认，适合 ADR / 契约 / 规范变更，保留历史）
          - reorder（适合任务卡依赖变更，不动 chunks）
          - delete（触发物理删除）
          - merge（去重合并，旧 doc 指向新 doc）
        """

    async def delete_document(
        self,
        doc_id: str,
        mode: Literal["soft", "hard"] = "soft",
        cascade_to_derivatives: bool = False,
    ) -> DeleteResult:
        """删除文档。cascade_to_derivatives=True 按 metadata.derived_from 链级联。"""

    # ───── Retrieval ─────
    async def search(
        self,
        query_text: str,
        collection: CollectionName,
        top_k: int = 10,
        filters: SearchFilters | None = None,
        score_threshold: float = 0.0,
        include_superseded: bool = False,
    ) -> list[SearchResult]:
        """单 Collection 语义检索。"""

    async def multi_search(
        self,
        query_text: str,
        collections: list[CollectionName],
        top_k_per_collection: int = 5,
        merged_top_k: int = 15,
        filters_by_collection: dict[CollectionName, SearchFilters] | None = None,
        merge_strategy: Literal["rrf", "weighted"] = "rrf",
        collection_weights: dict[CollectionName, float] | None = None,
    ) -> MultiSearchResult:
        """
        跨 Collecti
