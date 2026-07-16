---
module_id: MOD-INF-011
title: Vector Memory Service Interface / 向量记忆服务接口规范
doc_type: architecture_view
status: Active
version: "1.2.0"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: Claude-Opus-4.7
created_date: "2026-04-24"
last_updated: "2026-05-06"
ttl: permanent
truth_source:
  - "03_modules/infra_ops/vector_memory/blueprint.md（MOD-INF-011 — 详细设计与 Collection 契约；蓝图真源）"
  - "architecture_model/layers/b_vector_memory.yaml（Vector Memory YAML SSoT）"
supersedes:
  - "archive/reorg-2026-04-24/08_ai_engineering/memory-interface-contract.md (archived 2026-04-24)"
related_kb:
  - "KBG-0016 Vector Memory Service 选型与渐进实施（pending B-e）"
integration_points:
  - "Context Engine (downstream, 主消费者)"
  - "Agent Orchestrator (upstream writer)"
  - "MCP Server knowledge_base_server.py (MCP 适配层)"
  - "git post-commit hook (upstream writer)"
tags:
  - vector_memory
  - chromadb
  - bge-m3
  - service-interface
  - vibe-coding-infrastructure
mod_master_blueprint: "MOD-MASTER_BLUEPRINT"
mod_master_contracts:
  - "CT-ORC-VMS-001"
  - "CT-CE-VMS-001"
  - "CT-KB-VMS-001"
responsibility_domain: 
build_status: planned
design_maturity: design
---

# Vector Memory Service Interface / 向量记忆服务接口规范

> **定位**：Vibe Coding 2.0 基础设施五大核心服务之一。替代老 `memory-interface-contract.md` 的 KMS 六层文件流水线方案。
>

---

## 0. 读者指南

### 0.1 本文档是什么

| 章节 | 内容 | 主要读者 |
|:-:|------|---------|
| §1 | 服务定位与实施策略（含 Protocol 抽象基类） | 架构师 |
| §2 | 技术选型表 | 架构师、运维 |
| §3 | 核心数据模型（Collection / Document / Chunk / Cascade） | 开发者 |
| §4 | API 设计（Python 库 experimental + HTTP 预留骨架） | 所有集成方 |
| §5 | 前置条件与依赖 | 开发者 |
| §6 | 文件清单与落位 | 开发者 |
| §7 | 集成点 | 架构师、开发者 |
| §8 | 渐进路线 | 所有人 |
| §9 | 错误码与降级策略（含 DEGRADE-* P0 降级） | 所有集成方 |
| §10 | 性能 SLO（含冷启动） | 运维 |
| §11 | 测试用例（P0） | 开发者、QA |
| §12 | 修订记录 | 所有人 |

### 0.2 本文档**不是**

> 防止"接口文档被当成实现文档"的常见误读。

- ❌ **ChromaDB 使用教程**——见 ChromaDB 官方文档（https://docs.trychroma.com）
- ❌ **BGE-M3 模型训练指南**——本方案仅使用预训练量化模型，不涉及微调
- ❌ **生产部署运维手册**——beta+ 服务化时另出 SRE 文档
- ❌ **Context Engine 设计文档**——见 `context_engine-interface.md`（B-a-2 产出）
- ❌ **MCP 协议适配细则**——VMS 不碰 MCP，相关内容见 `context_engine-interface.md`
- ❌ **具体施工计划**——见 experimental `construction-plan-vms-*.md`（B 阶段后由 E 阶段任务卡覆盖）

---

## 1. 服务定位与实施策略

### 1.1 缺口 → 原因 → 解法

**缺口**：AI Agent 编写代码时需要跨会话检索项目积累的知识（KB 决策记录 / 代码 / 任务卡 / 教训），老方案要求人工分拣到六层 KMS，上线后 0 人分拣，知识库空转。

**原因**：
1. 老方案把"知识价值评审"与"知识检索"耦合——分拣门（G1-G5）成为入库前置阻塞
2. Markdown 文件 + frontmatter 索引无法支撑语义检索，Agent 只能精确查询
3. 没有独立 embedding 层，每次查询都要重新全文扫描

**解法**：
- 解耦"入库"与"评审"——知识就地入库，查询时用相似度过滤低质内容
- 引入 ChromaDB 0.6 + BGE-M3 ONNX 做向量检索
- 首份是 Python 库（进程内调用），数据量 > 10k docs 时按需升级为独立服务

### 1.2 职责边界

| Yes | No |
|-----|----|
| ✅ Document 入库、chunking、embedding、持久化 | ❌ 决定"查什么问题"（Context Engine 职责） |
| ✅ 语义检索、元数据过滤、top-k、跨 Collection 联合检索 | ❌ 上下文组装与压缩（Context Engine 职责） |
| ✅ Collection 级 CRUD、增量同步、批量 bootstrap | ❌ 权限控制（MCP Server 前置 Gateway 职责） |
| ✅ 向量库容量、性能、一致性保障 | ❌ 触发写入（git hook / Orchestrator 职责） |
| ✅ 软删除、硬删除、四种 cascade 策略 | ❌ 人工分拣 / 价值评级（老方案废弃） |

### 1.3 实施策略：Protocol + 双实现（库化优先，按需服务化）

**关键决策**：定义 `VectorMemoryProtocol` 抽象基类，两种实现共享同一签名，业务层永远依赖 Protocol 而非具体实现，升级时零重写。

```python
# src/zephyr/security/llm_defense/llm_security/protocol.py (experimental 产出)

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

## 2. 技术选型表（真源锁定）

| 组件 | 首选 | 备选 | 不推荐 | 选型理由 | 升级触发 | 相关 KB 决策记录 |
|------|----------------|------|-------|---------|---------|----------|
| 向量数据库 | **ChromaDB 0.6** | Qdrant 本地模式 | Weaviate / Pinecone（网络依赖） | 纯 Python、零外部依赖、Windows 原生支持 | 数据 > 10GB 或 chunks > 500k | KBG-0016 |
| Embedding 模型 | **BAAI/bge-m3 ONNX 量化** | text-embedding-3-small（OpenAI） | Ada-002（已淘汰） | 本地推理、多语言、1024 维、MIT License | 本地质量 < API 质量 20% | KBG-0016 |
| 分块策略 | **递归字符分块** | 语义分块（spaCy） | 固定长度分块 | 自动保留语义单元；spaCy 重量级 | 召回率 < 80% 或长文 > 50KB 频繁出现 | KBG-0016 |
| multi_search 合并策略 | **RRF 倒数排名融合**（Cormack 2009） | 加权分数融合（需配权重） | 级联串行检索（延迟高） | 不同 Collection 向量距离尺度不同，RRF 只看排名不看分数 | - | KBG-0016 |
| 进程内并发 | **`asyncio.Lock`** | - | `threading.Lock`（阻塞事件循环）| 项目全异步栈 | 服务化后废除 | - |
| 跨进程并发 | **`filelock.FileLock`** | `msvcrt.locking`（Windows Only） | 全局单例 | pytest 并发 + 多 Agent 场景 | 服务化后废除 | - |
| 服务运行时（beta 启用） | FastAPI | gRPC | Flask | FastAPI 原生 async + OpenAPI | RPS > 500 → gRPC | - |

---

## 3. 核心数据模型

### 3.1 Collection 概念（4 个预定义）

VMS 管理 **4 个预定义 Collection**，按检索用途分区，支持跨 Collection 联合检索（允许动态创建自定义，但 4 个预定义不可删除）：

| Collection | 用途 | 典型 Document 来源 |
|-----------|------|-------------------|
| `decisions` | 架构决策与合约 | **KB:decisions**（SQLite `knowledge`，`category=architecture_decision`，`ke_id=ADR-*`）、`03_modules/_cross_layer/_b_track_interfaces/*interface*.md` |
| `code_context` | 代码与配置 | `src/**/*.py`、`src/**/*.yaml`、`docs/03_modules/**/*.md` |
| `task_history` | 任务卡与执行历史 | `docs/03_modules/_domain_infrastructure_runtime/task_system/changes/**/*.md`（拆卡/任务卡样例）、`src/zephyr/data/persistence/task_repo.py` 持久化任务元数据（见 MOD-TASK_SYSTEM） |
| `lessons` | 经验教训与审计 | `docs/_working/audit/reports/`、`docs/_working/audit/findings/` |

### 3.2 Cascade 语义表（4 种场景）

update / delete 动作的级联策略，每种对应不同的业务触发：

```python
# src/zephyr/data/knowledge_management/vector_memory/cascade.py (experimental 产出)

from enum import Enum

class CascadeStrategy(str, Enum):
    SUPERSEDE = "supersede"   # KB 决策记录 替代 / 规范版本迭代
    REORDER   = "reorder"     # 任务依赖调整
    DELETE    = "delete"      # 源文件删除
    MERGE     = "merge"       # 重复条目合并

CASCADE_SCENARIOS = {
    "supersede": {
        "trigger":        "新 KB 决策记录/契约明确替代旧版",
        "action":         "旧条目 metadata.superseded_by = 新条目ID，旧 chunks 保留",
        "search_weight":  0.1,   # 检索权重降级到 10%，除非 include_superseded=True
        "gc_eligible":    False, # gc() 不清理（历史留档）
    },
    "reorder": {
        "trigger":        "任务依赖关系变更（task_deps 字段）",
        "action":         "相关条目 metadata.task_deps 更新，chunks 保持不变",
        "search_weight":  1.0,   # 正常检索
        "gc_eligible":    False,
    },
    "delete": {
        "trigger":        "git rm 源文件 / 明确声明删除",
        "action":         "所有 Collection 中该 doc_id 的 chunks 物理删除（硬删除）",
        "search_weight":  0.0,
        "gc_eligible":    True,  # 立即清理
    },
    "merge": {
        "trigger":        "去重检测（MinHash LSH / content_hash 完全相同）发现重复",
        "action":         "被合并条目 metadata.merged_into = 保留条目ID，chunks 软删除",
        "search_weight":  0.0,
        "gc_eligible":    True,  # gc() 清理被合并方
    },
}
```

### 3.3 Pydantic Schemas

```python
# src/zephyr/integration/shared/schema/schemas.py (experimental 产出)

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum

class DocumentSourceType(str, Enum):
    MARKDOWN_DOC = "markdown_doc"
    CODE = "code"
    TASK_CARD = "task_card"
    SESSION_LOG = "session_log"
    ARCHITECTURE_YAML = "architecture_yaml"
    AUDIT_REPORT = "audit_report"
    EXTERNAL = "external"

class CollectionName(str, Enum):
    DECISIONS = "decisions"
    CODE_CONTEXT = "code_context"
    TASK_HISTORY = "task_history"
    LESSONS = "lessons"

class Document(BaseModel):
    doc_id: str = Field(..., description="全局唯一，推荐 sha1(source_path)")
    collection: CollectionName
    source_path: str
    source_type: DocumentSourceType
    title: str
    content: str
    content_hash: str = Field(..., description="sha256(content)")
    language: Literal["zh", "en", "mixed", "code"] = "zh"
    tags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict,
        description="自由字段 + cascade 字段：superseded_by / merged_into / task_deps 等")
    created_at: datetime
    updated_at: datetime
    version: int = Field(default=1, description="同 doc_id 下版本号，update 时 +1")

class Chunk(BaseModel):
    chunk_id: str = Field(..., description="{doc_id}::v{version}::c{chunk_index}")
    doc_id: str
    doc_version: int
    chunk_index: int = Field(..., ge=0)
    text: str
    char_start: int
    char_end: int
    overlap_with_prev_chars: int = 0

class SearchResult(BaseModel):
    chunk_id: str
    doc_id: str
    collection: CollectionName
    source_path: str
    source_type: DocumentSourceType
    text: str
    score: float = Field(..., ge=0.0, le=1.0)
    rank_in_collection: int = Field(..., description="在所属 Collection 内的排名，RRF 融合用")
    metadata: dict = Field(default_factory=dict)
    doc_title: Optional[str] = None
    degraded: bool = Field(default=False, description="若为 True 表示此结果来自降级路径")

class MultiSearchResult(BaseModel):
    query_text: str
    results_by_collection: dict[CollectionName, list[SearchResult]]
    merged_top_k: list[SearchResult] = Field(..., description="按 merge_strategy 合并后的 top_k")
    merge_strategy: Literal["rrf", "weighted"]
    total_matched_by_collection: dict[CollectionName, int]
    elapsed_ms: int
    degraded: bool = Field(default=False)

class SyncResult(BaseModel):
    """git hook / 手动单文件同步结果"""
    file_path: str
    event: Literal["add", "modify", "delete"]
    doc_id: str
    action_taken: Literal["ingested", "unchanged", "updated", "deleted", "skipped"]
    chunks_affected: int
    elapsed_ms: int
```

---

## 4. API 设计

### 4.1 Python 库 API（experimental 主用，`InProcessVectorMemory` 实现）

```python
# src/zephyr/data/knowledge_management/vector_memory/in_process.py (experimental 产出)

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
          - supersede（默认，适合 KB 决策记录 / 契约 / 规范变更，保留历史）
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
        跨 Collection 联合检索。遗漏 #3 补充。
        典型场景：AI 编写 D_FACTOR 因子代码时需要 decisions(KB 决策记录) + code_context(接口) + lessons(教训)

        merge_strategy（experimental 默认 rrf）：
          - "rrf"（推荐）：倒数排名融合 score = Σ 1/(k + rank_i)，k=60。
            理由：不同 Collection 向量距离尺度不同（维度/分布不同），RRF 只看排名规避尺度问题。
            参考：Cormack et al. 2009 "Reciprocal Rank Fusion outperforms Condorcet..."
          - "weighted"：加权分数融合 score = Σ w_i * score_i。需 collection_weights。
            仅用于各 Collection 向量空间一致的高级场景。
        """

    async def get_by_id(self, doc_id: str, version: int | None = None) -> Document | None: ...
    async def get_chunks_by_doc(self, doc_id: str, version: int | None = None) -> list[Chunk]: ...

    # ───── Management ─────
    async def stats(self) -> VMStats: ...

    async def reindex(
        self,
        new_embedding_version: str,
        collection: CollectionName | None = None,
        mode: Literal["blue_green", "in_place"] = "blue_green",
        dry_run: bool = False,
    ) -> ReindexResult: ...

    async def gc(self, older_than_days: int = 30) -> GCResult: ...
```

### 4.2 HTTP API（beta 按需启用，预留骨架）

**现在不实现**，但固化 URL 与 schema，`RemoteVectorMemory` 将严格对齐：

| Method + Path | 对应库方法 |
|---------------|-----------|
| `POST /v1/ingest` | `ingest()` |
| `POST /v1/ingest/bootstrap` | `bulk_bootstrap()` |
| `POST /v1/sync` | `sync_document()` |
| `PATCH /v1/documents/{doc_id}` | `update_document()` |
| `DELETE /v1/documents/{doc_id}?mode=&cascade=` | `delete_document()` |
| `POST /v1/search` | `search()` |
| `POST /v1/search/multi` | `multi_search()` |
| `GET /v1/documents/{doc_id}` | `get_by_id()` |
| `GET /v1/stats` | `stats()` |
| `POST /v1/reindex` | `reindex()` |
| `POST /v1/gc` | `gc()` |

HTTP 请求 / 响应 schema = 库方法入参 / 出参的 Pydantic JSON 序列化形式。

---

## 5. 前置条件与依赖

### 5.1 前置组件（必须先完成）

| 前置项 | 状态 | 所在任务 |
|-------|:----:|---------|
| `src/zephyr/config/embedding_model_registry.yaml` | ✅ 已存在 | - |
| `src/zephyr/vector_memory/` 包创建 | ⏳ 待建 | experimental T-1-XX |
| BGE-M3 ONNX 模型下载到 `.models/bge-m3/` | ⏳ 待建 | experimental T-1-XX |
| `.runtime/` 目录规范写入 `trae_028_doc_structure_naming.yaml` | ⏳ 待修订 | B-d 阶段（B3/B4） |
| `.gitignore` 追加 `.runtime/` + `.models/` | ⏳ 待追加 | experimental T-1-XX 首步 |
| `vibe_config.yaml::runtime_root` 字段定义 | ⏳ 待修订 | B-d 阶段（B3） |
| KBG-0016 批准 | ⏳ pending | B-e 阶段 |

### 5.2 Python 依赖（锁定版本写入 pyproject.toml）

```toml
[project.optional-dependencies]
vector_memory = [
    "chromadb==0.6.*",
    "onnxruntime>=1.17,<2.0",
    "transformers>=4.40,<5.0",  # BGE-M3 tokenizer
    "filelock>=3.13",
    "pydantic>=2.5,<3.0",       # 已有
]
```

### 5.3 运行时依赖（可选的消费者）

- Context Engine（主消费者，见 `context_engine-interface.md`）
- MCP `knowledge_base_server.py`（已存在，experimental 重构接入 `get_vm()`）

---

## 6. 文件清单与落位（不留 placeholder）

```

├── src/zephyr/
│   ├── vector_memory/                              # ⏳ experimental 新建
│   │   ├── __init__.py                             # 导出 get_vm() 工厂（按配置返回 InProcess 或 Remote 实现）
│   │   ├── protocol.py                             # VectorMemoryProtocol 抽象基类（§1.3）
│   │   ├── in_process.py                           # experimental 实现（ChromaDB SDK）
│   │   ├── remote.py                               # beta 实现占位（当前不开发）
│   │   ├── schemas.py                              # Pydantic schemas（§3.3）
│   │   ├── cascade.py                              # CascadeStrategy + CASCADE_SCENARIOS（§3.2）
│   │   ├── chunker.py                              # 递归字符分块
│   │   ├── embedder.py                             # BGE-M3 ONNX 封装
│   │   ├── chroma_adapter.py                       # ChromaDB 0.6 适配层
│   │   ├── collections.py                          # 4 个预定义 Collection 初始化
│   │   ├── routing.py                              # 路径 → Collection 路由规则（§7.3）
│   │   ├── bulk_bootstrap.py                       # bulk_bootstrap 断点续传
│   │   ├── sync.py                                 # sync_document git hook 入口
│   │   ├── rrf.py                                  # RRF 融合算法
│   │   └── config.py                               # VMConfig 加载
│   ├── config/
│   │   ├── embedding_model_registry.yaml           # ✅ 已存在
│   │   └── vector_memory.yaml                      # ⏳ 新建：runtime_root 引用 + ChromaDB 配置
│   └── clients/                                    # beta 启用时才建
│
├── vibe_config.yaml                                # ⏳ B-d 修订新增字段
│   # 新增字段：
│   #   runtime_root: ${ZEPHYR_RUNTIME_ROOT:-.runtime}   # 支持环境变量覆盖
│   #   models_root:  ${ZEPHYR_MODELS_ROOT:-.models}
│
├── .runtime/                                       # ⏳ 运行时数据根目录（加 .gitignore）
│   ├── chromadb/                                   # ← ChromaDB 持久化（按 Collection 分 persist_directory）
│   │   ├── decisions/
│   │   ├── code_context/
│   │   ├── task_history/
│   │   └── lessons/
│   ├── sqlite/                                     # 预留（Orchestrator 任务队列 / Session Log）
│   ├── logs/                                       # 预留（运行时日志）
│   ├── cache/                                      # 预留（TTL 缓存）
│   └── vector_memory_bootstrap.ckpt                # bulk_bootstrap 断点
│
├── .models/                                        # ⏳ 本地模型（加 .gitignore）
│   └── bge-m3/                                     # ONNX 模型文件 (~1.2GB)
│
├── tests/                       # ⏳ experimental 新建
│   ├── test_chunker.py
│   ├── test_embedder.py
│   ├── test_chroma_adapter.py
│   ├── test_api_ingest.py
│   ├── test_api_sync.py
│   ├── test_api_search.py
│   ├── test_api_multi_search.py                    # 含 RRF 融合测试
│   ├── test_cascade.py                             # 4 种场景全覆盖
│   ├── test_bulk_bootstrap_resume.py
│   ├── test_cold_start.py                          # §10 冷启动 SLO 验证
│   └── test_degrade_paths.py                       # §9 DEGRADE-* 降级路径
│
└── .gitignore                                      # ⏳ 追加：
                                                    #   .runtime/
                                                    #   .models/
```

**关键约定**（本接口就地锁定）：
1. **`.runtime/`** = 所有服务运行时数据根目录（B-d 阶段 `trae_028_doc_structure_naming.yaml` 新增一节）
2. **`.models/`** = 本地模型文件根目录，不入 git
3. ChromaDB **每个 Collection 独立 persist_directory**（便于单独备份/重建）
4. **路径可配置**：`vibe_config.yaml::runtime_root` 支持环境变量覆盖（测试环境可用 `/tmp/zephyr-runtime/`）

---

## 7. 集成点

### 7.1 上游 Writers

| 写入方 | 触发 | 目标 Collection | 调用方式 |
|--------|------|----------------|---------|
| git post-commit hook | 每次 commit 的 `.md`/`.py`/`.yaml` | 按 §7.3 路由 | `await vm.sync_document(path, event)` |
| Agent Orchestrator | 任务完成时 | `task_history` | `await vm.ingest(doc)` |
| Session Log writer | 会话结束时 | `lessons` | `await vm.ingest(doc)` |
| Manual CLI（`scripts/vm_ingest.py`） | 首次 bootstrap / 手动导入 | 按 CLI 参数 | `await vm.bulk_bootstrap(docs)` |

### 7.2 下游 Readers

| 读取方 | 用途 | 调用方式 |
|--------|------|---------|
| **Context Engine**（主消费者） | 组装 Agent 上下文 | `await vm.multi_search(query, collections, merge_strategy="rrf")` |
| MCP `knowledge_base_server.py` | Cursor/Claude 的 MCP 工具 | `await vm.search(...)` / `multi_search(...)` |
| Dashboard `knowledge_overview.py` | 可视化统计 | `await vm.stats()` |
| 4 验收脚本 | 合规检查（是否全量入库） | `await vm.stats()` vs 源文件数 |

### 7.3 Collection 路由规则（git hook 默认）

| 源路径模式 | 目标 Collection |
|-----------|----------------|
| **KB:decisions**（SQLite ingest / MCP KB） | `decisions` |
| `docs/03_modules/_cross_layer/_b_track_interfaces/*interface*.md` | `decisions` |
| `src/**/*.py`, `src/**/*.yaml`, `docs/03_modules/**` | `code_context` |
| `docs/03_modules/_domain_infrastructure_runtime/task_system/changes/**` | `task_history` |
| `docs/_working/audit/reports/**`, `docs/_working/audit/findings/**` | `lessons` |
| 其他 | `code_context`（保守默认） |

---

## 8. 渐进路线

| Phase | 范围 | 验收标准 |
|:-:|------|---------|
| **scaffold**（当前） | 接口规范定稿（本文档） | KBG-0016 Active + 接口规范 Active |
| **experimental** | `InProcessVectorMemory` 实现 + `bulk_bootstrap` 200+ 文档首次导入 | ① §11 P0 用例全通过<br>② 导入 `docs/**/*.md` 全量成功<br>③ Context Engine `multi_search` p50 < 200ms |
| **beta** | git post-commit hook 接 `sync_document` + MCP Server 重构 | ① commit 后 5s 内增量入库<br>② MCP `knowledge_base_server.py` 调用转发到 `get_vm()` |
| **beta** | `RemoteVectorMemory` 独立服务（按需触发才启动） | 触发条件满足时启动；业务层切 factory 即可，零重写 |
| **stable** | gRPC 升级（按需） | RPS > 500 时 |

---

## 9. 错误码与降级策略

### 9.1 异常层级（Python 库）

```python
class VMError(Exception): ...                        # 基类
class VMConfigError(VMError): ...                    # 配置错误（启动即失败）
class VMEmbeddingError(VMError): ...                 # embedding 失败（模型加载 / OOM）
class VMStorageError(VMError): ...                   # ChromaDB 操作失败
class VMConflictError(VMError): ...                  # 幂等冲突 / update cascade 拒绝
class VMNotFoundError(VMError): ...                  # doc_id 不存在
class VMValidationError(VMError): ...                # schema 校验失败
class VMDegradedError(VMError): ...                  # 可降级但记录用（通常被 catch 后返回空结果）
```

HTTP 映射：`VMConfigError`→503 / `VMEmbeddingError`→422 / `VMStorageError`→500 / `VMConflictError`→409 / `VMNotFoundError`→404 / `VMValidationError`→400

### 9.2 P0 级降级条款

> **核心原则**：VMS 是"增强层"，不是核心依赖。挂了不能拖垮 AI Session，宁可上下文不完整，也不能卡死。

**DEGRADE-001：向量检索不可用时的降级路径**

触发场景：
- ChromaDB 持久化文件损坏
- 磁盘满 / 权限错误
- 首次启动未 bootstrap（collection 为空）
- BGE-M3 模型加载失败（运行时被删除）

降级动作：

```python
try:
    results = await vm.multi_search(query, collections)
    if results.degraded:                       # 上游必须检查此标记
        context_engine.fallback_to_filesystem_grep(query)
except VMStorageError:
    # search/multi_search 内部捕获并返回 degraded=True 空结果，通常不抛到调用方
    # 若抛到这里说明基础设施已彻底失效
    log.critical("VMS completely down, fallback to rg/grep")
    results = filesystem_grep_fallback(query)
```

**调用方强制契约**：
- `search()` / `multi_search()` / `sync_document()` 失败时**必须返回**空结果 + `degraded=True` 标记，**不抛异常**阻塞 AI Session
- 调用方（Context Engine / MCP Server）**必须**检查 `degraded` 标记，选择性降级到文件系统检索（`rg`/`grep`）
- 本次降级必须写入 `logs/vms_degrade.log`（结构化日志：触发原因 / 时间戳 / 调用方 / 查询文本 sha256）

### 9.3 降级条件速查表

| 触发条件 | 降级动作 | 上游感知 |
|---------|---------|---------|
| BGE-M3 加载失败 | 启动即抛 `VMConfigError` | 启动失败，需人工排查 |
| ChromaDB 读失败 | `search()` 返回 `[]` + `degraded=True` | **DEGRADE-001** 生效 |
| ChromaDB 写失败 | `ingest()/sync_document()` 抛 `VMStorageError` | 上游指数退避重试 |
| 单次查询 > 2s | 超时返回已有结果 + `partial=True` | 日志告警 |
| 首次启动未 bootstrap | 任何 search 返回 `[]` + `degraded=True` + reason="empty_collection" | **DEGRADE-001** 生效 |
| 数据量 > 10GB | 告警触发 beta 升级评估 | 运维 |

---

## 10. 性能 SLO

### 10.1 稳态 SLO（experimental，ChromaDB 已加载完毕后）

| 指标 | 目标 | 测试条件 |
|------|------|---------|
| `search()` p50 延迟 | ≤ 80 ms | top_k=10，数据量 < 50k chunks |
| `search()` p95 延迟 | ≤ 250 ms | 同上 |
| `multi_search()` p50 延迟 | ≤ 200 ms | 4 个 Collection，top_k_per=5，RRF 融合 |
| `multi_search()` p95 延迟 | ≤ 500 ms | 同上 |
| `sync_document()` 单文件 | ≤ 300 ms | 含 embedding |
| `bulk_bootstrap()` 稳态吞吐 | ≥ 50 docs/s | batch_size=50 |
| 内存占用（稳态） | ≤ 700 MB | 含模型 + 元数据索引 |

### 10.2 冷启动 SLO（首次启动 / 重启后首次调用，补充）

> **为什么必须量化**：个人量化系统高频场景——每天开电脑第一次启动。不快就是用户体验灾难。

| 指标 | 目标 | 说明 |
|------|------|------|
| 进程冷启动（不含 BGE-M3 加载） | ≤ 3 s | import + 配置解析 |
| BGE-M3 模型首次加载 | ≤ 5 s | ONNX Runtime 加载 + warmup 1 条 embedding |
| 首次 `search()` 延迟（冷缓存） | ≤ 2 s | 含 ChromaDB 打开持久化文件 |
| 首次 `multi_search()` 延迟（冷缓存） | ≤ 3 s | 4 个 Collection 首次打开 |
| **总冷启动到首次可用** | **≤ 10 s** | 进程启动 + 模型加载 + ChromaDB 打开 + warmup 查询 |
| `bulk_bootstrap(200 docs)` 端到端 | ≤ 60 s | 首次部署场景 |

**冷启动优化要求**：
- BGE-M3 懒加载（首次调用时才加载，而非 import 时）
- ChromaDB collection 懒打开（首次检索对应 collection 时才 open）
- 启动完成后记录 `logs/vms_startup.log`，供运维比对

---

## 11. 测试用例（P0，experimental 必须通过）

### 11.1 Ingestion & Sync P0

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-I1 | 单文档首次入库 | 空 Collection | `await vm.ingest(doc)` | 返回 `ingested`，search 能命中 |
| P0-I2 | content_hash 未变幂等 | 已 ingest | 再次 ingest 同 doc | 返回 `unchanged`，chunks_created=0 |
| P0-I3 | 内容变更 version 递增 | 已 ingest v1 | 修改 content 再 ingest | version=2，旧 chunks 被替换 |
| P0-I4 | bulk_bootstrap 断点续传 | 导 200 docs 中途 kill | 重启再调用 | checkpoint 续跑，不重入库，总耗时 < 1.5× 无中断 |
| P0-I5 | sync_document add 事件 | 新文件 | `sync_document(path, "add")` | 等价 ingest，Collection 按 §7.3 自动路由 |
| P0-I6 | sync_document delete 事件 | 已入库 | `sync_document(path, "delete")` | 等价 `delete_document(mode="hard")` |

### 11.2 Retrieval P0

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-R1 | 单 Collection 语义检索 | decisions 含 KBG-0016 | `search("ChromaDB 选型", decisions)` | top_1 为 KBG-0016，score > 0.5 |
| P0-R2 | multi_search RRF 融合 | 4 Collection 均有数据 | `multi_search(query, [4 个], "rrf")` | 返回各 Collection top_k + 全局 merged_top_k，按 RRF 分数降序 |
| P0-R3 | RRF vs weighted 一致性 | 同上 | 同 query 分别用 rrf 和 weighted | 两者 top-3 overlap ≥ 2（高相关 query 应稳定） |
| P0-R4 | 过滤器语义正确 | 含 `tags=[archived]` | `search(..., filters=tags_exclude=["archived"])` | 不返回含 archived chunks |

### 11.3 Cascade & Delete P0

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-C1 | cascade=supersede 默认 | KB 决策记录 v1 已入库 | `update_document(..., cascade=SUPERSEDE)` | 旧 chunks 保留，metadata.superseded_by 指向新；默认 search 权重降至 0.1 |
| P0-C2 | cascade=delete 物理删除 | doc 已入库 | `update_document(..., cascade=DELETE)` | 所有 chunks 物理删除，search 无命中 |
| P0-C3 | cascade=merge 合并语义 | 两 doc content_hash 相同 | `update_document(old_id, ..., cascade=MERGE)` | old_id 标记 merged_into=new_id，gc 后物理删除 |
| P0-C4 | cascade=reorder 元数据更新 | 任务卡 doc | `update_document(..., cascade=REORDER, new_metadata={"task_deps":...})` | chunks 不动，仅 metadata 更新 |
| P0-C5 | soft delete 默认不返回 | doc 已入库 | `delete_document(id, mode="soft")` → search | search 不返回；`gc()` 后硬删除 |

### 11.4 并发与持久化 P0

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-P1 | 多进程并发 sync 不冲突 | 空库 | 3 进程各 100 docs sync | filelock 正常，无重复 chunk，总量正确 |
| P0-P2 | 重启后持久化正常 | ingest 10 docs 后杀进程 | 重启 search | 查询结果与重启前一致 |
| P0-P3 | reindex blue_green 不阻塞查询 | 持续 search QPS=5 + 触发 reindex | 检查期间错误率 | < 0.1% |

### 11.5 冷启动 P0（§10.2 SLO 对应）

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-B1 | 冷启动端到端 ≤ 10s | 清空进程，ChromaDB 已持久化 50k chunks | 启动进程 + 首次 search | 端到端 ≤ 10s |
| P0-B2 | bulk_bootstrap 200 docs ≤ 60s | 空库 | `bulk_bootstrap(200 docs)` | ≤ 60s |
| P0-B3 | BGE-M3 懒加载 | 启动进程 | 仅 import 不调用 | 不触发模型加载（内存 < 200MB） |

### 11.6 降级路径 P0（§9.2 DEGRADE-001 对应）

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-D1 | ChromaDB 读失败降级 | mock chroma 抛异常 | `await vm.search(...)` | 返回 `[]` + `degraded=True`，不抛异常 |
| P0-D2 | 空 Collection 首次 search | 未 bootstrap | `await vm.search(...)` | 返回 `[]` + `degraded=True` + reason="empty_collection" |
| P0-D3 | 降级日志落盘 | 触发 DEGRADE-001 | 检查 `logs/vms_degrade.log` | 含触发原因 + 时间戳 + 调用方 + query sha256 |

---

## 12. 修订记录

| 日期 | 版本 | 说明 |
|------|:-:|------|
| 2026-04-24 | 1.0.0 | 初版（B-a-1 首稿）。基于 Kimi §7.5.2 + Qwen 选型 #4-6。 |
| 2026-04-24 | 1.1.0 | 用户反馈吸收一轮：库化优先 + `.runtime/chromadb/` 锁定 + Collection + multi_search + bulk_bootstrap + update cascade 三场景 + 前置条件/文件清单/P0 测试章节 + 瘦身 "缺口→原因→解法" 三段式。 |
| 2026-04-24 | 1.2.0 | 用户反馈吸收二轮（定稿为 5 份接口的共享模板）：① §1.3 引入 `VectorMemoryProtocol` 抽象基类 + `InProcessVectorMemory` / `RemoteVectorMemory` 双实现；② 所有 API 改为 `async`，锁用 `asyncio.Lock` + `filelock`（严禁 `threading.Lock`）；③ 新增 `sync_document(file_path, event)` 增量同步 API（git hook 主入口）；④ CASCADE 新增 merge 场景（第 4 种）+ `CASCADE_SCENARIOS` 完整表；⑤ multi_search 默认 `merge_strategy="rrf"`（Cormack 2009），weighted 降为高级选项；⑥ §0 新增"本文档不是"；⑦ §9 补 **DEGRADE-001** P0 级降级条款 + 调用方强制契约 + 降级日志；⑧ §10 新增冷启动 SLO（总冷启动 ≤ 10s）；⑨ §11 补 merge / 冷启动 / 降级路径 P0 测试；⑩ `vibe_config.yaml::runtime_root` 支持环境变量覆盖。 |

### §0.6 四图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从四图真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-INF-011`

#### 四图位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-INF-011` 的 37 个 file 节点 | design | `extract_depgraph.py --modules MOD-INF-011` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-INF-011 | MOD-INF-011 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | planned | planned | ✅ |
| file_count | 37 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
