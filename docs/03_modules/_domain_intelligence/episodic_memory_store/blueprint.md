---
blueprint_id: MOD-INT-EPISODIC-MEM
module_name: episodic_memory_store
domain: D_INTELLIGENCE
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_INTELLIGENCE
path: src/zephyr/intelligence/episodic_memory_store.py
granularity: file
---

# MOD-INT-EPISODIC-MEM episodic_memory_store 蓝图（情景记忆）

> **module_id**: MOD-INT-EPISODIC-MEM | **域**: D_INTELLIGENCE | **优先级**: P1
> **来源**: B11-02613（AUD-DRAFT-001-DIGEST P1 波 W-P1-10，§6.1）
> 代码：`src/zephyr/intelligence/episodic_memory_store.py`

## 0. 定位

情景记忆存储（自反 Agent 内，业界对标 Reflexion 轨迹记忆 + Generative
Agents 向量 Top-K 检索）：轨迹 Schema（输入-行动-结果-反思）落 Redis
Hash + 向量入 FAISS 双写；相似任务 Top-K 检索供新任务上下文注入；LRU 淘
汰保留 1000 条 + 90 天转 SQLite 归档；与四层记忆架构（B11-02457
agent_memory_architecture）接口对齐。

与既有族分工（查重裁定）：
- MOD-REFLEXION_AGENT reflexion/roles：三角色骨架与 Trajectory/
  ReflectionRecord 数据载体——有轨迹数据结构无存储流水线，本模块轨迹
  Schema 字段语义与之对齐（input/action/result/reflection），不复制角色
  逻辑。
- MOD-REFLEXION_AGENT preflect_store：失败模式库（提炼后 pattern+触发
  条件+规避建议，JSON 落盘+规则关键词检索）——是反思**提炼产物**库，非
  轨迹级情景记忆，互补不重复。
- MOD-INF-011 faiss_collection_manager：FAISS 8 Collection 生命周期管理
  ——本模块向量写入经注入 vector_sink 委托，不直连 FAISS。
- MOD-INF-036 unified_memory_api：ChromaDB 知识库三件套。
- 本模块判定核心纯内存：Schema 校验/LRU 次序/淘汰与归档判定/Top-K 排序；
  Redis Hash/FAISS/SQLite 真实存储全经注入 sink，装配期可内存态 fake。

## 1. 判定核心（纯内存，无 IO）

- `TrajectoryRecord`（frozen）：record_id/task_input/action/result/
  reflection/created_at/last_accessed_at——四要素任一为空（reflection 可
  空字符串=未反思）或时间非法 → `InvalidTrajectoryError`（Fail-Closed）。
- `store(record, embedding=None)`：Schema 校验 → 内嵌索引台账（tuple 追加
  不可变语义）+ 经 `hash_sink`（Redis Hash 语义）与 `vector_sink`（FAISS
  语义，embedding 非空才写）双写外发；sink 异常不阻断台账（sink_errors
  留痕）。
- `retrieve_similar(query_embedding, k)`：经注入 `search` callable 取向量
  候选 → 按相似度降序 Top-K（k 非正 → ValueError）→ 命中条目刷新
  last_accessed_at（LRU 语义）。
- LRU 淘汰：台账超 max_entries（默认 1000）→ 淘汰最久未访问条目，淘汰
  名单落 `EvictionRecord` 留痕。
- 归档：age > archive_after_days（默认 90）→ 转 `archive_sink`（SQLite
  语义）归档并从主台账移除，归档留痕；未注入 archive_sink → 仅产归档
  建议不删除（Fail-Closed 不丢数据）。
- 与四层记忆架构接口对齐：`store/retrieve/forget` 三方法即情景层 backend
  契约（供 agent_memory_architecture 注入消费）。

## 2. 接口

```python
@dataclass(frozen=True) TrajectoryRecord: record_id/task_input/action/result/reflection/created_at/last_accessed_at
@dataclass(frozen=True) RetrievalHit: record/score
@dataclass(frozen=True) EvictionRecord: evicted_ids/reason
@dataclass(frozen=True) EpisodicMemoryConfig: max_entries=1000/archive_after_days=90
class EpisodicMemoryStore(config=None, hash_sink=None, vector_sink=None, search=None, archive_sink=None, clock=None):
    store/retrieve_similar/forget/evict_if_needed/archive_expired/stats
class InvalidTrajectoryError/EpisodicConfigError(ZephyrBaseError)
```

## 3. 不变量

- 判定核心纯内存无 IO；hash_sink/vector_sink/search/archive_sink/clock
  全注入；零密钥字段。
- Schema Fail-Closed：非法轨迹不入库不双写。
- LRU 语义：检索命中即刷新访问时间；淘汰恒取最久未访问；同输入必同淘汰
  名单（确定性）。
- 归档不丢数据：archive_sink 缺失时仅产建议不删除；台账只增不改（归档/
  淘汰经显式 forget 路径留痕）。

## 4. 依赖

- MOD-REFLEXION_AGENT reflexion/roles（设计边：轨迹 Schema 语义对齐）
- MOD-INF-011 faiss_collection_manager（设计边：向量双写委托面）
- MOD-INT-AGENT-MEMORY agent_memory_architecture（设计边：情景层 backend
  契约对齐，B11-02457 同波）

## 5. MVP 边界

- 运行时接线（hash_sink 接 Redis、vector_sink/search 接 FAISS、
  archive_sink 接 SQLite、embedding 接本地 EmbeddingRouter）留运行时装配
  批；本模块交付轨迹 Schema + 双写契约 + Top-K 检索 + LRU 淘汰 + 归档
  判定核心。
