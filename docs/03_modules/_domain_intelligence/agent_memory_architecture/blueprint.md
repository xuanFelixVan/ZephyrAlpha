---
blueprint_id: MOD-INT-AGENT-MEMORY
module_name: agent_memory_architecture
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
path: src/zephyr/intelligence/agent_memory_architecture.py
granularity: file
---

# MOD-INT-AGENT-MEMORY agent_memory_architecture 蓝图（Agent 记忆架构）

> **module_id**: MOD-INT-AGENT-MEMORY | **域**: D_INTELLIGENCE | **优先级**: P1
> **来源**: B11-02457（AUD-DRAFT-001-DIGEST P1 波 W-P1-10，§0边界声明/§7）
> 代码：`src/zephyr/intelligence/agent_memory_architecture.py`

## 0. 定位

四层记忆统一模型（业界对标 MemGPT/Letta 认知架构）：工作记忆（会话/上下
文窗口）→ 情景记忆（轨迹+反思，施工面归 B11-02613 episodic_memory_store）
→ 语义记忆（知识/规则，入 D_KNOWLEDGE）→ 程序记忆（SKILL.md+scripts 版本
化）；五阶段流水线（编码/存储/检索/巩固/遗忘）接口统一；各层 TTL/淘汰策
略声明式配置。

与既有族分工（查重裁定）：
- MOD-CONTEXT_ENGINE memory_bank：6 个结构化 .md 跨 session 持久上下文
  （AI 读写分节），是存储件非四层统一模型——本模块程序/语义层后端可经
  注入委托，不复制其读写逻辑。
- MOD-INF-036 unified_memory_api：ChromaDB 三件套（recall/write/search+
  provenance 强制），知识库式记忆层。
- MOD-INF-011 in_process_vector_memory：VMS 统一入口（8 Collection FAISS）。
- MOD-REFLEXION_AGENT reflexion 族：三角色骨架+反思记录数据载体。
- B11-02613 episodic_memory_store（本波 W-P1-10 同波施工）：情景记忆流水
  线（轨迹存储/Top-K/LRU/归档）——本模块情景层接口与之对齐（层后端注入
  契约），不重复建存储。
- 本模块是四层模型+五阶段流水线的**统一接口层**：层路由/策略校验/巩固与
  遗忘判定纯内存，各层真实存储经注入 backend 消费。

## 1. 判定核心（纯内存，无 IO）

- 四层枚举 `MemoryLayer`（working/episodic/semantic/procedural）+ 五阶段
  枚举 `PipelineStage`（encode/store/retrieve/consolidate/forget）。
- `MemoryPolicy`（声明式）：ttl_seconds/max_entries/eviction（lru/fifo）
  ——ttl 非正/max_entries 非正/未知淘汰策略 → `InvalidMemoryPolicyError`
  （Fail-Closed）。
- `encode(item, layer)`：条目校验（空 content/未知层 → ValueError）产
  `MemoryItem`（layer/content/metadata/created_at）。
- `store(item)`：按层路由到注入 backend（未注入 → `MemoryBackendMissingError`）；
  超 max_entries 产淘汰判定（LRU 淘汰最久未访问 / FIFO 淘汰最旧），淘汰
  名单留痕。
- `retrieve(query, layer, k)`：经注入 backend 检索返回 Top-K。
- `consolidate(item, from_layer, to_layer)`：巩固判定——仅允许沿
  working→episodic→semantic 方向巩固（逆向/跳层非法 → ValueError），
  程序记忆只接受人工登记源（source=manual）。
- `forget(layer)`：按策略产遗忘清单（TTL 过期+淘汰溢出），经 backend
  执行删除委托。

## 2. 接口

```python
class MemoryLayer(Enum): WORKING/EPISODIC/SEMANTIC/PROCEDURAL
class PipelineStage(Enum): ENCODE/STORE/RETRIEVE/CONSOLIDATE/FORGET
@dataclass(frozen=True) MemoryPolicy: ttl_seconds/max_entries/eviction
@dataclass(frozen=True) MemoryItem: item_id/layer/content/metadata/created_at/last_accessed_at
@dataclass(frozen=True) EvictionDecision: layer/evicted_ids/reasons
class AgentMemoryArchitecture(policies, backends=None):
    encode/store/retrieve/consolidate/forget/policy_of
class InvalidMemoryPolicyError/MemoryBackendMissingError(ZephyrBaseError)
```

## 3. 不变量

- 判定核心纯内存无 IO；各层真实存储全经注入 backend（缺 backend 操作
  Fail-Closed）。
- 策略声明式：TTL/淘汰策略只经 `MemoryPolicy` 配置，非法即拒。
- 巩固方向恒 working→episodic→semantic；程序记忆恒人工登记源。
- 淘汰/遗忘判定确定性：同输入必同淘汰名单；判定留痕可审计。

## 4. 依赖

- MOD-CONTEXT_ENGINE memory_bank（设计边：程序/语义层持久上下文后端对齐）
- MOD-INF-036 unified_memory_api（设计边：语义层知识库接口对齐）
- MOD-INT-EPISODIC-MEM episodic_memory_store（设计边：情景层接口契约对齐，
  B11-02613 同波）

## 5. MVP 边界

- 运行时接线（四层 backend 真实装配：working=会话上下文、episodic=
  episodic_memory_store、semantic=D_KNOWLEDGE/VMS、procedural=SKILL.md
  版本库）留运行时装配批；本模块交付四层模型 + 五阶段流水线判定核心 +
  声明式策略契约。
