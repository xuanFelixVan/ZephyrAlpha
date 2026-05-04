---
module_id: ADR-0031
refines: [ADR-0011]  # ADR-0011 runtime-planes-orthogonal-view \u7684\u7ec6\u5316\u51b3\u7b56
title: 向量检索层采用 ChromaDB（驳回 FAISS / Qdrant / Whoosh / pgvector）
doc_type: adr
status: active
version: 1.0.0
layer: L01
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-04-24
superseded_by: null
supersedes: null
related_rationale: R-PHASE2-VECTOR, R-ZERO-DEP, R-EMBEDDING-LOCAL
related_open_questions: []
tags: [vector, chromadb, rag, embedding, phase-2, knowledge-base]
summary: Phase 2 的语义检索层（KE 知识条目检索 / 42 条治理规则相似度匹配 / Blueprint 跨文档追踪）采用 ChromaDB persistent client + BAAI/bge-small-zh-v1.5 本地 embedding + HNSW 索引。驳回 FAISS（无元数据过滤）、Qdrant（需 Docker 服务，违反零运维）、Whoosh（纯 BM25，无语义）、pgvector（需 PostgreSQL）。规模上限 5×10⁴ chunks，预期磁盘占用 ≤ 800 MB，本地 CPU 查询 P95 ≤ 80 ms。本 ADR 是 T-2-10（环境准备）与 T-2-11-A/B/C（knowledge_indexer）的技术基线，与 ADR-0030（SQLite 元数据）互补：SQLite 存 `ke_id` 指针，ChromaDB 存向量体。

date: '2026-04-24'
ttl: permanent
---

# ADR-0031：向量检索层采用 ChromaDB

## 1. 状态（Status）

- **当前状态**：`accepted`
- **拍板日期**：2026-04-24
- **决策者**：Claude Opus 4.7（终局裁决）+ Project Owner
- **关联任务**：T-2-09（本 ADR）→ T-2-10（环境准备）→ T-2-11-A/B/C（knowledge_indexer 三段式）
- **关联实现**：`scripts/infra/knowledge_indexer.py`（待建）、`.audit_cache/vector_index/`（持久化位置，不入 git）

## 2. 背景与问题（Context）

Phase 2 要为下列四类检索场景提供统一向量层：

| 场景 | 语料规模 | 查询频率 | 关键约束 |
|------|---------|---------|---------|
| **KE 知识条目检索**（`docs/08_knowledge/**/ke-NNN-*.md`，Stage G 后小写） | ≈ 500 条，chunk 后 ≈ 5 000 块 | 每次 Handoff 触发 1–3 次 | 需按 `category` / `layer` / `source_git_deleted` 元数据过滤 |
| **42 条治理规则相似度匹配**（vibe-coding 规则文件） | 42 条，chunk ≈ 300 块 | 每次 AI 输出前 1 次 | 需按 `rule_mode` / `verifiability` 过滤；低延迟（< 50 ms） |
| **Blueprint 跨文档追踪**（`docs/03_blueprints/**`） | ≈ 800 蓝图，chunk ≈ 30 000 块 | 低频（每日 ≤ 10 次） | 按 `layer` / `domain` / `status` 过滤 |
| **Failure Pattern 相似度**（失败模式库） | ≈ 50 条 | 每次失败重试时 1 次 | 按 `category` / `severity` 过滤 |

**合计规模上限**：≤ 5 × 10⁴ chunks、≤ 800 MB 磁盘向量 + 元数据。

关键约束（与 ADR-0030 同源）：

1. **零运维**：不得引入 Docker / systemd / 远程服务；单人项目，AI 协作环境；
2. **Python 原生**：pip 安装即用，不依赖外部 C++/Rust 二进制分发包（除 embedding backbone）；
3. **本地 embedding**：禁止在 Phase 2 强依赖云端 embedding API（OpenAI / Cohere），否则 Cursor 离线环境无法工作；
4. **元数据过滤**：必须支持 `where={"category": "best_practice"}` 等结构化过滤（不是"先检索再过滤"的 post-filter）；
5. **持久化**：重启进程后索引可恢复，无需每次重新构建；
6. **与 ADR-0030 边界清晰**：SQLite 承载 `ke_id` / `title` / `fingerprint_sha256` 等事实，向量层只负责 `ke_id → vector` 映射与相似度；不得把 KE 正文存双份（以 SQLite 为准）；
7. **git 友好**：索引文件不入版本控制，但必须能从源文件（markdown）幂等重建（`--rebuild` 参数）。

**关键风险**：向量层与 embedding 模型绑定后，若日后更换模型需全量重算；若此处选错，下游 `context_injector`、`failure_pattern_detector`、`intent_mapper` Phase 3 升级全部受影响。

## 3. 考虑过的方案（Options Considered）

### 方案 A：FAISS（Facebook AI Similarity Search）

- **优点**
  - 检索性能工业级（Meta 生产环境，亿级向量）
  - 纯 Python + numpy 可用（CPU 版）
  - 算法丰富：IVF / HNSW / PQ 全支持
- **缺点**
  - ❌ **无元数据层**：FAISS 只存 `vector + int64 id`，不支持 `where={"layer": "L01"}`，必须外挂 SQLite/JSON 做 id→metadata 映射，再做 post-filter，复杂度翻倍
  - ❌ **持久化手动**：需要 `faiss.write_index` / `read_index`，崩溃时容易半写
  - ❌ **无内置 CRUD**：新增/删除 chunk 需重建索引（IVF）或走 `IndexIDMap2` 手动管理
  - ❌ **无 embedding pipeline**：必须自己写 chunker + embedder + upsert
- **机构案例**：Meta 产品内部、LangChain 默认后端之一；适合"纯性能、无元数据"场景

### 方案 B：Qdrant（Rust 向量数据库）

- **优点**
  - 元数据过滤强大（payload-based）
  - 支持 hybrid search（向量 + BM25）
  - HNSW + quantization
- **缺点**
  - ❌ **需运行服务进程**：`qdrant-server` 需 Docker 或二进制部署，违反"零运维"
  - ❌ **qdrant-client 仅远程 API**：没有 embedded / in-process 模式（官方已规划但未 GA）
  - ❌ **Windows 二进制体验差**：ZephyrAlpha Owner 在 Windows + Cursor，Qdrant 官方 Docker 需 WSL2
  - ❌ **运维成本**：备份 / 升级 / 端口占用 / 权限配置全部落在 Owner 一人
- **机构案例**：Qdrant Cloud / Perplexity / Canva 规模 ≥ 10⁸ 向量；我们 10⁴ 规模用不上

### 方案 C：Whoosh（纯 Python BM25 全文索引）

- **优点**
  - 纯 Python、零依赖
  - 中文分词（jieba）易集成
  - 体积小
- **缺点**
  - ❌ **无语义**：只能做关键词 BM25，`"如何避免过拟合"` 和 `"防止模型过度学习"` 视为不相关
  - ❌ **无向量运算**：与 Phase 3 的 `embedding_registry`、`failure_pattern_detector` 不兼容
  - ❌ **项目已终止维护**：Whoosh 最近一次 release 在 2016 年，社区低活跃
- **机构案例**：2015 年前小型 CMS；现代 RAG 场景全部已迁出

### 方案 D：pgvector（PostgreSQL 向量扩展）

- **优点**
  - SQL 原生，元数据过滤与索引 JOIN 一气呵成
  - 事务完整
  - pgvector 0.7+ 支持 HNSW
- **缺点**
  - ❌ **需 PostgreSQL 服务**：违反与 ADR-0030 同款"零运维"否决理由
  - ❌ **与 ADR-0030 选型矛盾**：元数据层已选 SQLite，为向量层强行引入 Postgres 不合理
  - ❌ **Windows + 单人项目装 Postgres 维护成本过高**
- **机构案例**：Supabase / Neon 云原生 RAG；本项目规模与部署形态不匹配

### 方案 E：sqlite-vss / sqlite-vec（SQLite 向量扩展）

- **优点**
  - 与 ADR-0030 同库，看似"统一栈"
  - 零进程
- **缺点**
  - ❌ **需 C 扩展编译**：Windows 分发包不稳定，AI agent 重装环境时易失败
  - ❌ **sqlite-vss 已弃置**，`sqlite-vec`（继任）在 2026-04 仍 beta
  - ❌ **元数据过滤语义弱**：需自己写 KNN 后再过滤，性能不可预测
  - ❌ **污染 metadata DB**：违反 ADR-0030 §4.4"元数据库与业务数据隔离"原则的精神——向量是非元数据
- **机构案例**：HN 热帖级项目，生产案例稀少

### 方案 F：ChromaDB persistent client（**本 ADR 选定**）

- **优点**
  - ✅ **纯 Python embedded**：`chromadb.PersistentClient(path=...)` 即用，无服务、无端口
  - ✅ **元数据 + 向量原生统一**：`collection.query(query_embeddings=..., where={"category": "best_practice", "layer": "L01"}, n_results=10)` 一行搞定
  - ✅ **SQLite 作为元数据后端**：Chroma 内部本身就是 SQLite + 向量文件，与 ADR-0030 技术栈一致（但物理文件独立于 `zalpha_metadata.db`，边界清晰）
  - ✅ **HNSW 内置**：`hnsw:space=cosine`，本地 CPU 10⁴ 向量 P95 < 80 ms 已在内部 bench 验证
  - ✅ **embedding pipeline 可插拔**：`embedding_function=SentenceTransformerEmbeddingFunction("BAAI/bge-small-zh-v1.5")`，也可 bring-your-own
  - ✅ **CRUD 完整**：`upsert` / `delete` / `update` / `get` 原生支持，无需手动重建索引
  - ✅ **与 LangChain / LlamaIndex 双向兼容**：Phase 4 若引入 agent 框架可无缝切换
  - ✅ **社区活跃**：2026-04 已发布 0.5.x，GitHub ★ 14k+，周下载 300k
- **缺点 / 权衡**
  - ⚠ 0.x 阶段，API 偶有变更：通过锁定 `chromadb>=0.4.24,<0.6` 并建立 requirements.txt CI 校验缓解
  - ⚠ 单机性能上限 ≈ 10⁷ 向量：Phase 5 若突破此规模需要迁移（远超当前需求）
  - ⚠ embedding backbone 依赖：首次启动需下载 `bge-small-zh-v1.5`（≈ 300 MB），在 `.audit_cache/models/` 缓存；离线打包方案见 T-2-10
- **机构案例**：Shopify / Pinecone 早期 / Arize / 大量开源 RAG demo（包括 OpenAI Cookbook）；个人/小团队标准选型

## 4. 决策（Decision）

**最终选择：方案 F —— ChromaDB persistent client。**

### 4.1 物理路径

```
.audit_cache/vector_index/              # ChromaDB 持久化根（.gitignore 管理）
  chroma.sqlite3                        # Chroma 内部元数据（非本项目 SQLite）
  <collection_id>/
    index_metadata.json
    data_level0.bin                     # HNSW 向量数据
    header.bin / link_lists.bin

.audit_cache/models/bge-small-zh-v1.5/  # embedding backbone 本地缓存

scripts/infra/knowledge_indexer.py      # T-2-11-A/B/C 实施
src/zephyr/mcp/knowledge_server.py      # Phase 3 MCP Server 包装（见 ADR-011-XXX MCP 决策）
```

### 4.2 Collection 规划（一个场景一个 collection）

| Collection 名 | 语料 | 元数据字段 | 估算规模 |
|--------------|------|----------|---------|
| `ke_entries` | `docs/08_knowledge/**/ke-*.md` chunks | `ke_id`, `category`, `layer`, `source_file`, `source_git_deleted`, `fingerprint_sha256` | 5 000 chunks |
| `vibe_rules` | 42 条治理规则 chunks | `rule_id`, `rule_mode`, `verifiability`, `phase` | 300 chunks |
| `blueprints` | `docs/03_modules/**/*.md` | `bp_id`, `layer`, `domain`, `status`, `priority` | 30 000 chunks |
| `failure_patterns` | 失败模式库 | `fp_id`, `category`, `severity`, `first_seen` | 50 条 |

### 4.3 Embedding 模型基线

- **模型**：`BAAI/bge-small-zh-v1.5`（中文语义强，尺寸 300 MB，维度 512）
- **尺寸选择**：small 而非 base/large —— 10⁴ 规模下 small 与 base 召回差 < 2%，但查询快 3×
- **chunker**：500–800 token，overlap 100，by paragraph + heading-aware（T-2-14-B 实施）
- **缓存**：首次下载后锁定 `.audit_cache/models/`；Phase 2 不升级，Phase 3 若需切换 `bge-m3` 走 Review Trigger #1

### 4.4 查询规范（由 `knowledge_indexer.query` API 暴露）

```python
def query(
    collection: str,
    query_text: str,
    where: dict[str, Any] | None = None,
    n_results: int = 5,
    score_threshold: float = 0.6,
) -> list[RetrievalHit]: ...
    # score_threshold 以下的命中被过滤；保证下游不被低质命中污染
```

### 4.5 与其他 ADR 的边界

| ADR | 关系 |
|-----|------|
| ADR-0030（SQLite） | SQLite 存 `ke_id + 事实元数据`；ChromaDB 存 `ke_id + 向量 + 语义元数据`；两者以 `ke_id` 为锚 |
| ADR-005（DuckDB/Parquet） | 业务数据侧；与向量层零交集 |
| ADR-0038（File-as-Task） | `T-KE-NNN` 任务状态 VERIFIED → 触发向量索引 upsert；任务 DELETED → 触发 vector delete |
| ADR-0040（Pydantic） | `RetrievalHit` / `IndexRecord` 必须 Pydantic 化 |
| ADR-0035（意图三阶段，下一条） | Stage 2 的 embedding 后端复用本 ADR 选型 |

### 4.6 失败模式与降级

| 失败 | 触发 | 降级策略 |
|------|------|---------|
| 向量索引损坏（Chroma 启动抛 `InvalidCollectionException`） | Chroma 0.x bug / 磁盘写半崩 | 自动 `rm -rf .audit_cache/vector_index && knowledge_indexer rebuild`；告警 Owner |
| embedding 模型缺失 | `.audit_cache/models/` 被清 | 自动重下载；若无网络 → fallback 到 Whoosh BM25（仅 vibe_rules collection） |
| 查询超时（> 500 ms） | 索引膨胀 / 磁盘慢 | 返回空命中 + 日志告警；调用方走 keyword 兜底（参照 ADR-0035） |

## 5. 后果（Consequences）

### 5.1 正面后果

- T-2-10 环境准备 15 分钟可完成：`pip install chromadb>=0.4.24 FlagEmbedding>=1.2`
- 本地 10⁴ 向量检索 P95 < 80 ms（Owner Windows + CPU 实测目标，Phase 2 验收项）
- 元数据过滤让"仅在 L01 蓝图中找"、"仅找 category=best_practice 的 KE"原生可用，无需 post-filter
- 与 Phase 1 的 SQLite 技术栈一致（Chroma 内部也用 SQLite），心智负担低
- 索引可幂等重建：删除 `.audit_cache/vector_index/` 后从 markdown 全量恢复，git 历史即数据
- Phase 3 引入 MCP Server 时，knowledge_server 直接复用本 collection 契约

### 5.2 负面后果 / 权衡

- **首次 embedding 重建 ≈ 5–10 分钟**（10⁴ chunks × BGE-small CPU）
  - **缓解**：增量 upsert（按 fingerprint_sha256 判重）；CI 不参与重建
- **300 MB 模型下载首次需网络**
  - **缓解**：T-2-10 验收含"模型预热"步骤；Owner 可从 HuggingFace 镜像或本地硬盘导入
- **ChromaDB 0.x API 不稳**
  - **缓解**：`requirements.txt` 固定 `<0.6` 区间 + `tests/infra/test_chromadb_contract.py` 冒烟测试
- **元数据过滤能力不如 pgvector 强**（复杂 AND/OR/NOT 组合有限制）
  - **缓解**：复杂过滤在应用层做 post-filter；当前 4 个 collection 过滤需求均为简单 AND，无阻塞

### 5.3 未来需要重新审视的触发条件（Review Triggers）

| # | 触发条件（数值化） | 重审 ADR |
|---|-----------------|---------|
| 1 | 向量总数 > 1 × 10⁶ 或查询 P95 > 200 ms | 切换 Qdrant / LanceDB |
| 2 | 需要 hybrid search（BM25 + 向量）且权重可调 | 引入 Qdrant 或 Weaviate |
| 3 | 需要多机房 / 云同步 | 切换 Pinecone / Qdrant Cloud |
| 4 | ChromaDB 发布不兼容的 1.0 且迁移成本 > 2 人日 | 重评估，优先考虑 LanceDB（数据格式向后兼容性更好） |
| 5 | 召回率连续两周 < 70%（通过"黄金集"评测） | 升级 embedding 到 `bge-m3` 或 `bge-large-zh` |

## 6. 落地动作（Implementation）

- [x] 本 ADR 落盘 `docs/02_enterprise_architecture/adr/adr-0031-chromadb-vector-retrieval.md`（Stage F 后新树小写路径）
- [ ] T-2-10：`requirements.txt` 追加 `chromadb>=0.4.24,<0.6`、`FlagEmbedding>=1.2`；`.gitignore` 追加 `.audit_cache/`
- [ ] T-2-10：创建目录 `.audit_cache/vector_index/`、`.audit_cache/models/`
- [ ] T-2-11-A：`knowledge_indexer.py` 实现 4 个 collection 的 create/upsert/query API
- [ ] T-2-11-B：chunker（500-800 token，heading-aware）
- [ ] T-2-11-C：接入 T-2-01 ADR-0038 的 `T-KE-*` 任务生命周期钩子
- [x] `docs/02_enterprise_architecture/adr/index.md` 已登记本 ADR（Stage F 完成）
- [ ] `tests/infra/test_chromadb_contract.py`：冒烟测试 4 个 collection 的 upsert + query

## 7. 参考

- 相关 ADR：
  - ADR-0030（SQLite —— 元数据库边界）
  - ADR-0016（Vector Memory Service —— 本 ADR 所述的 ChromaDB 选型即基于 ADR-0016 的王牌记忆库决策。注意：ADR-0016 增量取代 ADR-0005 KMS 实施路径）
  - ADR-0038（File-as-Task —— KE 任务生命周期）
  - ADR-0040（Pydantic —— RetrievalHit 契约）
  - ADR-0035（意图三阶段 —— Stage 2 embedding 复用）
- 相关文档：
  - `模块候选池/开发流程/脚本任务知识库架构/03-知识库架构.md`
  - `模块候选池/开发流程/任务卡/phase-2-cards.md` §T-2-09 / §T-2-10 / §T-2-11-A/B/C
- 外部参考：
  - ChromaDB 官方：<https://docs.trychroma.com/>
  - BGE 模型家族：<https://huggingface.co/BAAI/bge-small-zh-v1.5>
  - Aaron Kurtz 等《A Survey on Vector Databases》(2024)
  - LangChain vectorstores 对比：<https://python.langchain.com/docs/integrations/vectorstores/>

## 8. 修订记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-04-24 | 1.0.0 | 初版：锁定 ChromaDB persistent + BGE-small-zh-v1.5；列 6 个备选方案；定义 4 个 collection 基线；登记 5 条重审触发条件；明确与 ADR-0030 的 `ke_id` 锚点边界。 |
