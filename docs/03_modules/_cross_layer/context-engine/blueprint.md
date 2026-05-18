---
module_id: "MOD-INF-008"
title: "Context Engine 蓝图 — build→compress→validate→inject 四阶段上下文注入"
doc_type: blueprint
template_for: blueprint
status: Draft
version: "0.9.3"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-07"
updated: "2026-05-14"
valid_from: "2026-05-07"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: src/zephyr/context_engine/
belongs_to: "MOD-MASTER-001"
parent_module: ""
generation: 1
functional_domain: intelligence
last_verified: "2026-05-13"
last_updated: "2026-05-14"
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
summary: "四阶段上下文注入引擎：build→compress→validate→inject，Token预算三级管控，LSG安全审查"
tags: [context-engine, ce, context-injection, rag, token-budget, build-compress-validate-inject, local-llm, infrastructure, capacity-planning]
priority: P0
depends_on:
  - {target: "MOD-MASTER-001", at: "§2.3", why: "CT-ORC-CE-001 集成契约——Orc→CE上下文构建请求时序"}
  - {target: "MOD-MASTER-001", at: "§2.6", why: "CT-CE-VMS-001 集成契约——CE→VMS向量检索"}
  - {target: "MOD-KB-001", at: "§1.5", why: "知识库——CE的上下文检索源"}
  - {target: "architecture-model/layers/b_context_engine.yaml", at: "全篇", why: "CE YAML SSoT——本蓝图真源"}
---

# Context Engine 蓝图 — build→compress→validate→inject 四阶段上下文注入

## 概述

本蓝图描述 Context Engine——ZephyrAlpha 的上下文注入引擎。它解决了 Agent 大脑获取最优上下文的问题：从 VMS 检索相关知识、压缩到 Token 预算内、安全检查后注入 Agent session。核心职责包括：四阶段流水线(build→compress→validate→inject)、Token 预算三级管控(L1 80%/L2 90%/L3 95%)、LSG 安全审查(CT-CE-LSG-001 fail-closed)、结构化分层注入(Layer1-4)。当前规模 51 模块/3 Agent，目标容量 1500 模块/100 Agent 并发。上游依赖 VMS(MOD-INF-011)和知识库(MOD-KB-001)，下游被 Orchestrator(MOD-INF-006)消费。canonical SSoT 为 [b_context_engine.yaml](file:///D:/ZephyrAlpha/architecture-model/layers/b_context_engine.yaml)，代码落位 `src/zephyr/context_engine/`（85 个 .py 文件）。

> module_id: MOD-INF-008 | version: 0.9.3 | status: Draft | layer: cross_layer
> actual_disk_path: src/zephyr/context_engine/ | generation: 1 | construction_progress: partially_implemented

> 蓝图+施工图模板：[TPL-BLUEPRINT-001](file:///D:/ZephyrAlpha/docs/03_modules/template-registry.yaml) | AI 压缩工作流标准：[GOV-DOC-011](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/governance/document/compression-workflow-standard.md)

## §0 对齐验证

### §0.1 代码文件清单

#### 源文件

| 文件 | 行数 | 说明 |
|------|:---:|------|
| `context_assembler.py` | 292 | Build 阶段——组装上下文 |
| `context_rule_registry.py` | — | 规则注册 API——动态注册上下文注入规则 |
| `context_budget_tracker.py` | 227 | Token 预算三级管理 |
| `context_injector.py` | — | Inject 阶段——加 provenance 溯源字段 |
| `context_rot_model.py` | — | beta a——n² attention 衰减数学模型 |
| `context_evictor.py` | — | beta a——三维排序上下文逐出器 |
| `doc_compressor.py` | 563 | 完整实现——Immutable Core+不变量校验+三级降级 |
| `intent_keyword_mapper.py` | — | intent→keyword 映射表 |
| `intent_parser.py` | — | 意图分类 NLP |
| `pattern_library.py` | — | pattern 模板库 |
| `prompt_registry.py` | — | prompt 注册表 |
| `system_snapshot.py` | — | 系统状态快照 |
| `pipeline_orchestrator.py` | ~6.2KB | 多阶段流水线编排 |
| `vector_bridge.py` | ~5.6KB | CE↔VMS 桥接 |
| `task_validator.py` | ❌ | beta 待实现 |

#### 测试文件

| 文件 | 磁盘 | 说明 |
|------|:---:|------|
| `test_context_assembler.py` | ✅ | ContextAssembler 单元测试 |
| `test_context_budget_tracker.py` | ❌ | 待实现 |
| `test_context_evaluator.py` | ✅ | ContextEvaluator 单元测试 |
| `test_context_evictor.py` | ✅ | beta a——ContextEvictor 18 测试 |
| `test_context_injector.py` | ✅ | ContextInjector 单元测试 |
| `test_context_pipeline.py` | ✅ | 流水线集成测试 |
| `test_context_rot_model.py` | ✅ | beta a——ContextRotModel 18 测试 |
| `test_curation_loop.py` | ✅ | CurationLoop 单元测试 |
| `test_doc_compressor.py` | ✅ | DocCompressor 单元测试 |
| `test_intent_accuracy.py` | ✅ | 意图分类精准度测试 |
| `test_intent_keyword_mapper.py` | ✅ | intent keyword 映射测试 |
| `test_intent_parser.py` | ✅ | intent 解析测试 |
| `test_memory_bank.py` | ✅ | MemoryBank 单元测试 |
| `test_pattern_library.py` | ❌ | 待实现 |
| `test_prompt_registry.py` | ✅ | prompt 注册表测试 |
| `test_system_snapshot.py` | ✅ | 系统快照测试 |
| `test_pipeline_orchestrator.py` | ⚠️ Ghost | 测试存在但源文件不存在 |

#### 配置文件

| 文件 | 说明 |
|------|------|
| `config/context_rules_v1.yaml` | 上下文规则配置 |
| `config/compression/policy.yaml` | DocCompressor 策略 |

#### 统计

| | 源文件 | 测试 | 配置 | 合计 |
|---|:---:|:---:|:---:|:---:|
| 已实现 | 85 | 15+ | 2 | 102+ |

### §0.2 对齐验证矩阵

| 蓝图章节 | 代码文件 | 对齐状态 |
|---------|---------|:---:|
| §3.1 Build | `context_assembler.py` | ✅ |
| §4.7 规则注册 | `context_rule_registry.py` | ✅ |
| §3.1 Compress | `doc_compressor.py` + `context_budget_tracker.py` | ✅ |
| §3.1 Validate | `prompt_registry.py` + `pattern_library.py` | ✅ |
| §3.1 Inject | `context_injector.py` | ✅ |
| §3.2 降级 | `context_assembler.py` (embedded_defaults) | ✅ |
| §3.3 流水线 | `pipeline_orchestrator.py` | ✅ |
| §3.1 VMS 桥接 | `vector_bridge.py` | ✅ |
| §3.1 意图解析 | `intent_parser.py` + `intent_keyword_mapper.py` | ✅ |
| beta a ContextRot | `context_rot_model.py` + `context_evictor.py` | ✅ |

### §0.3 版本-代码映射

| 版本 | 代码变更 |
|------|---------|
| v0.2.0 | 9 文件骨架 + context_assembler + injector |
| v0.3.0 | beta a: context_rot_model + context_evictor + context_injector(provenance) |
| v0.8.0 | pipeline_orchestrator + vector_bridge 落盘；214/214 测试全绿 |
| v0.9.0 | 容量升级 B49-B60/DD121-DD132/AP48-AP55 |
| v0.9.1 | 执行引擎并发 B61-B70/DD133-DD142/AP56-AP65 |

## §1 设计背景与目标

### §1.1 背景

ZephyrAlpha 从 51 模块/268 脚本/3 Agent 扩展到 1500 模块/10000 脚本/100 Agent。CE 是"知识库→Agent 大脑"的翻译桥梁——从 VMS 检索相关知识→压缩到 Token 预算内→安全检查→注入到 Agent session。

### §1.2 目标

| # | 目标 | 衡量标准 |
|---|------|---------|
| 1 | 四阶段流水线 build→compress→validate→inject | 端到端 P99 <3s |
| 2 | Token 预算三级管控 | L1(80%)预警/L2(90%)压缩/L3(95%)硬截断 |
| 3 | 安全合规：所有上下文必经 LSG 审查 | CT-CE-LSG-001 fail-closed |
| 4 | 100 Agent 并发支持 | M0-M4 五里程碑 |
| 5 | 增量注入减少 token 浪费 | ContextDiff 节约率 >60% |

### §1.3 不包含的目标

| 不包含 | 原因 |
|--------|------|
| VMS Collection 管理 | → VMS 蓝图 (MOD-INF-011) |
| Token 计算方式 | → LLM provider SDK |
| LSG 安全规则定义 | → LSG 蓝图 (MOD-INF-014) |
| Agent session 管理 | → Orchestrator (MOD-INF-006) |
| KE CRUD 操作 | → 知识库 (MOD-KB-001) |

### §1.4 运行场景约束

| 维度 | 当前基线 | 目标 | 膨胀倍率 |
|------|:---:|:---:|:---:|
| 模块 | 51 | 1,500 | ×29.4 |
| 治理脚本 | ~268 | ~10,000 | ×37.3 |
| 并发 AI Agent | 1~3 | 100 | ×33~100 |
| CE 并发 build 请求 | 单线程 | 100 并发 | ×100 |
| 硬件 | i7-12700KF + 64GB + RTX3090 24GB | 同一台 | — |

---

## §2 模块边界

### §2.1 职责范围

| 阶段 | 职责 | 入口文件 |
|------|------|---------|
| Build | 从 VMS 检索相关知识（4 Collection × top_K） | `context_assembler.py` |
| Compress | Token 预算内压缩（三级回退：LLM→规则→截断） | `doc_compressor.py` + `context_budget_tracker.py` |
| Validate | LSG 安全校验（prompt injection/敏感信息/危险工具） | `prompt_registry.py` + `pattern_library.py` |
| Inject | 结构化分层注入（Layer1-4） | `context_injector.py` |

### §2.2 不包含的职责

| 不包含 | → 去哪 |
|--------|--------|
| VMS 的 Collection 管理 | VMS 蓝图 (MOD-INF-011) |
| Token 的计算方式 | LLM provider SDK |
| LSG 的安全规则 | LSG 蓝图 (MOD-INF-014) |
| Agent session 的管理 | Orchestrator (MOD-INF-006) |
| KE 的增删改查 | 知识库 (MOD-KB-001) |

---

## §3 架构设计

### §3.1 组件架构

```
┌──────────┐    ┌───────────┐    ┌───────────┐    ┌──────────┐
│  BUILD   │ →  │ COMPRESS  │ →  │ VALIDATE  │ →  │ INJECT   │
│  检索    │    │   压缩    │    │  安全校验  │    │   注入   │
└──────────┘    └───────────┘    └───────────┘    └──────────┘
     ↑                                                  ↓
  VMS 4C                                           Agent Session
  (ke_entries×5,                                   (Orchestrator)
   vibe_rules×3,
   blueprints×2,
   failure_patterns×3)
```

| 组件 | 文件 | 职责 |
|------|------|------|
| ContextAssembler | `context_assembler.py` | Build 阶段——从 VMS 拉取原始上下文 |
| ContextBudgetTracker | `context_budget_tracker.py` | Compress 阶段——Token 预算管理 |
| DocCompressor | `doc_compressor.py` | Compress 阶段——三级压缩回退 |
| ContextInjector | `context_injector.py` | Inject 阶段——格式化+注入 session |
| IntentParser | `intent_parser.py` | 解析任务意图→决定检索策略 |
| IntentKeywordMapper | `intent_keyword_mapper.py` | 意图→关键词映射表 |
| PatternLibrary | `pattern_library.py` | Validate 阶段——已知危险模式库 |
| PromptRegistry | `prompt_registry.py` | Validate 阶段——注入模板注册 |
| SystemSnapshot | `system_snapshot.py` | 系统状态快照——供上下文参考 |
| PipelineOrchestrator | `pipeline_orchestrator.py` | 多阶段流水线编排 |
| VectorBridge | `vector_bridge.py` | CE↔VMS 检索桥接 |
| ContextRotModel | `context_rot_model.py` | n² attention 衰减数学模型 |
| ContextEvictor | `context_evictor.py` | 三维排序上下文逐出器 |

### §3.2 数据流

#### Build 阶段

| Collection | 检索条件 | top_k | 用途 |
|------|------|:---:|------|
| ke_entries | task_type + target_layer 语义相似 | 5 | 历史经验 |
| vibe_rules | task_type 相关治理规则 | 3 | 合规约束 |
| blueprints | target_layer 相关蓝图 | 2 | 架构参考 |
| failure_patterns | task_type 历史失败模式 | 3 | 避坑指南 |

#### Compress 阶段

| 类型 | Token 预算 | 优先级 |
|------|:---:|:---:|
| KE 条目 | 0-3000 | 最高 |
| 规则/策略 | 0-2000 | 高 |
| 蓝图 | 0-2000 | 中 |
| 运行时日志 | 0-1000 | 低 |
| **总计** | **8000** | — |

压缩策略（三级回退）：Level 1: Qwen2.5-3B 本地摘要→Level 2: 规则基摘要→Level 3: 截断

#### Validate 阶段

CE 通过 CT-CE-LSG-001 契约调用 LSG：检查 prompt injection / 敏感信息泄露 / 危险工具调用。LSG 拒绝的块→移除→重新 compress→再送 LSG→最多 3 次。

#### Inject 阶段

| 层 | 内容 | Token 策略 |
|----|------|-----------|
| Layer1 (system) | AGENTS.md core rules | always-on，不受 token 预算 |
| Layer2 (rules) | CT-\* 相关合同+blueprints | 按 task_type 注入 |
| Layer3 (knowledge) | KE+failure_patterns | priority 排序 |
| Layer4 (examples) | 类似任务成功案例 | 仅相似度>0.7 注入 |

### §3.3 状态生命周期

#### 三级降级策略

| 情况 | 降级行为 | 标记 |
|------|------|------|
| VMS 不可用 | 仅注入 AGENTS.md + 当前模块蓝图 | `session.degraded=true` |
| LSG 拒绝 ≥3 次 | 移除被拒绝块，注入剩余 | `injection_blocks_removed=N` |
| CE 10s 超时 | 降级注入—仅硬编码规则 | `CE_timeout_metric += 1` |

#### 四阶段流水线结构化规则

**Stage 1: Build**

```yaml
stage: build
entry_conditions:
  - id: BUILD-C00
    name: parse_user_intent
    type: nlp_classification
    check: "intent_parser.classify(user_prompt) → intent IN {CODE_GEN,CODE_REVIEW,ANALYSIS,OPS_FIX,DOC,REFACTOR,TEST,AUDIT,QUERY,DEBUG}"
    on_failure: flag
  - id: BUILD-C01
    name: map_intent_to_keywords
    type: lookup_table
    check: "intent_keyword_mapper.map(intent) → keywords[] AND keywords NOT EMPTY"
    on_failure: reject
  - id: BUILD-C02
    name: query_vector_memory
    type: vector_search
    check: "vector_bridge可用 → query 4C (ke_entries×5, failure_patterns×3, blueprints×2, architecture_model×1)"
    on_failure: auto_fix
```

**Stage 2: Compress**

```yaml
stage: compress
entry_conditions:
  - id: COMPRESS-C00
    name: check_token_budget
    type: budget
    check: "ContextBudgetTracker.check_budget(session_id) ≤ L1_WARNING"
    on_failure: auto_fix
  - id: COMPRESS-C01
    name: doc_compressor_invariants
    type: invariant
    check: "CompressionPolicy frozen 5不变量 ALL PASS: preserve_structure=true, preserve_provenance=true, min_chars≥100, max_chars≤10000, immutable_blocks preserved"
    on_failure: reject
```

**Stage 3: Validate**

```yaml
stage: validate
entry_conditions:
  - id: VALIDATE-C00
    name: lsg_safety_check
    type: security
    check: "context通过 CT-CE-LSG-001 → LSG三层审查全部PASS"
    on_failure: auto_fix
  - id: VALIDATE-C01
    name: no_hallucinated_sources
    type: integrity
    check: "ALL context.sources 路径在磁盘上存在"
    on_failure: auto_fix
```

**Stage 4: Inject**

```yaml
stage: inject
entry_conditions:
  - id: INJECT-C00
    name: structured_injection
    type: injection
    check: "context分层注入 Layer1-4"
    on_failure: flag
  - id: INJECT-C01
    name: verify_injected
    type: verification
    check: "session.system_prompt包含所有4层 AND 总tokens≤session_limit"
    on_failure: auto_fix
```

---

## §4 接口契约

### §4.1 CE 入口接口

| 接口 | 方向 | 说明 |
|------|------|------|
| `CE.build(task_card, session_id)` | Orc→CE | 任务启动时触发上下文构建 |
| `CE.fetch(keyword/domain/KE_ID/file)` | Agent→CE | Agentic Pull——Agent 按需拉取上下文 (DD113) |

### §4.2 跨模块契约

| CT-\* | 涉及系统 | 方向 | 说明 |
|------|---------|------|------|
| CT-ORC-CE-001 | Orc→CE | → | Orc 在任务启动时→CE.build(task_card, session_id) |
| CT-CE-VMS-001 | CE→VMS | → | CE.build()→VMS.search()→4C 检索 |
| CT-CE-LSG-001 | CE→LSG | → | CE.validate()→LSG 三层审查→PASS/FAIL |

### §4.3 契约容量条款 (DD127)

| CT-\* | max_qps | max_concurrent | degradation_strategy |
|-------|:---:|:---:|------|
| CT-ORC-CE-001 | — | 100 | BACKPRESSURE 信号 (DD132) |
| CT-CE-VMS-001 | — | 16 (连接池 DD136) | 排队 2s→DEGRADE |
| CT-CE-LSG-001 | — | — | LSG 不可用→拒绝注入 (fail-closed) |

### §4.4 输出契约

CE 输出为结构化 `RawContext`，包含分层上下文块 + provenance 溯源字段 (DD8)。CE context 优先级高于 Orc 系统提示 (DD96)——冲突时 CE 在 inject 阶段标记 `[CE_OVERRIDES_SYSTEM_PROMPT]`。

| 输出字段 | 类型 | 说明 |
|---------|------|------|
| `context_blocks` | List[ContextBlock] | 分层上下文块 (Layer1-4) |
| `provenance` | Provenance | 溯源信息 (DD8) |
| `token_usage` | TokenBudget | 实际 token 消耗 |
| `degraded` | bool | 是否降级注入 |

### §4.5 MCP接口

| 接口 | 方向 | 说明 |
|------|------|------|
| `/ce:fetch` | Agent→CE | Agentic Pull MCP tool (DD113) |
| `/ce:diagnose` | Owner→CE | 自诊断 API (B47) |
| `/ce:kill` / `/ce:revive` | Owner→CE | 紧急熔断/恢复 (DD110) |
| `/sc:dry-run <task>` | Owner→CE | 上下文沙箱 (DD79) |

CE Backpressure 信号 (DD132)：

| load | 行为 |
|------|------|
| >80% | 向 Orc 发送 BACKPRESSURE 信号→新 Agent 排队或降级 |
| >95% | 拒绝新 session (503) |

### §4.6 契约版本

| CT-\* | 版本 | 状态 | 变更说明 |
|-------|------|------|---------|
| CT-ORC-CE-001 | v1 | 活跃 | 初始版本 |
| CT-CE-VMS-001 | v1 | 活跃 | 初始版本 |
| CT-CE-LSG-001 | v1 | 活跃 | 初始版本 |

CE 启动就绪门控 (DD142)：CE 初始化完成→设置 `CE_READY` 标志→Orc 轮询 `GET /ce:health`→就绪前返回 `{"status": "starting", "ready_in_seconds": N}`。

### §4.7 规则注册 API（ContextRuleRegistry）

**职责**：允许外部模块动态注册上下文注入规则，按优先级分层注入 AI 上下文。

**消费者**：MOD-INF-017(去重引擎)、MOD-INF-018(RBAC)、MOD-INF-023(漂移检测器)、MOD-INF-033(行为审计器)

| 注入级别 | 定义 | Token 预算 | 示例 |
|---------|------|-----------|------|
| HOT | 始终注入 | ≤400 | @intentional-duplicate 标记规范 + 退出码映射 |
| DOMAIN | 关键词触发 | ≤800 | 影子 API 列表（触发词: dedup/去重/重复） |
| COLD | 按需加载 | 不限 | 完整策略树 policy_tree.yaml |

**API 签名**：

```python
@dataclass
class ContextRule:
    rule_id: str
    trigger_conditions: dict
    content: str
    priority: int = 50
    injection_level: str = "DOMAIN"  # HOT / DOMAIN / COLD
    max_tokens: int = 500
    source_module: str = ""

class ContextRuleRegistry:
    def register(self, rule: ContextRule) -> None: ...
    def lookup(self, task_type: str, tags: list[str], **kwargs) -> list[ContextRule]: ...
    def unregister(self, rule_id: str) -> None: ...
    def load_yaml(self, path: str) -> int: ...
    def list_rules(self) -> list[ContextRule]: ...
```

**SSoT 声明**：ContextRuleRegistry 是规则注册的唯一入口。

---

## §5 约束条件

### §5.1 技术约束

| # | 约束 | 来源 |
|---|------|------|
| 1 | 上下文不生成内容——只负责收集、压缩、校验、注入 | ai_role_instruction |
| 2 | 永远不给未经 LSG 审查的上下文给 LLM | CT-CE-LSG-001 |
| 3 | compress 阶段永不丢弃 raw_text——LSG 需要它做安全检测 | AP2 |
| 4 | 同一 session+同一 query→缓存 (TTL=5min) | AP4 |
| 5 | DocCompressor CompressionPolicy 为 Pydantic frozen 不可变 | DD3 |
| 6 | Token 预算三级：L1_WARNING(80%)/L2_THROTTLE(90%)/L3_HARD_STOP(95%) | DD2 |
| 7 | 默认 token_budget=8000 | DD6 |
| 8 | PipelineOrchestrator.run() 重构为 async + Semaphore 限流 | DD133 |
| 9 | ContextBudgetTracker check+consume 合并为原子 try_consume | DD134 |
| 10 | Qwen2.5-3B 推理有界并发池 max_concurrent=8 | DD135 |

### §5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:---:|:---:|:---:|:---:|------|
| 并发 build 请求 | 单线程 | 100 | RTX3090 24GB | ❌ | DD133 async+Semaphore |
| GPU 推理并发 | 1 | 8 (DD135) | 24GB VRAM, Qwen2.5-3B ~2GB | ⚠️ | DD135 LLMInferencePool |
| VMS 连接池 | 无 | 4-16 (DD136) | — | ❌ | DD136 VMSConnectionPool |
| Session 状态内存 | ~2-5MB/session | 100 session ~200-500MB | 64GB RAM | ✅ | DD129 SessionTTL |
| CE 自身内存 | ~3-3.5GB | — | 含 Qwen2.5-3B+Embedding+Python | ✅ | — |

### §5.3 迁移/废弃方案

> ⚠️ 临时时态：迁移方案执行完毕后从蓝图删除。

| 迁移/废弃项 | 触发条件 | 操作 | 废弃条件 |
|--------|---------|------|---------|
| 嵌入模型版本 (DD92) | embedding model 变更 | KE metadata 写入 embedding_model+version；全量 re-index 告警 | cosine similarity<0.85 |
| PipelineOrchestrator 同步→异步 (DD133) | asyncio overhead > 同步 20% | 保留 sync fast-path | sync path 6 个月后移除 |
| 全量扫描分片 (DD131) | 10,000 脚本 130h 不可行 | 按 D1-D12 分 12 shard 独立执行 | 单 shard <1h 时可合并 |

---

## §6 错误处理

| 错误场景 | 处理 | 关联 DD/AP |
|---------|------|-----------|
| VMS 不可用 | 三级降级：embedded_defaults | AP1 |
| LSG 拒绝 ≥3 次 | 移除被拒绝块，注入剩余 | CT-CE-LSG-001 |
| CE 10s 超时 | 仅硬编码规则 | — |
| Token 预算耗尽 | L3_HARD_STOP——不追加 context | DD2, AP7 |
| PipelineOrchestrator 竞态 | async + Semaphore 限流 | DD133, B61 |
| Budget TOCTOU 竞态 | 原子 try_consume | DD134, B62 |
| GPU 推理排队超时 | 降级 rule_based 压缩 | DD135, B63 |
| VMS 连接耗尽 | 排队 2s→DEGRADE | DD136, B64 |
| 上下文毒化 | 注入后 30min 监控 Agent action 成功率 | DD97, B23 |
| 注入中途失败 | shadow-then-swap 原子注入 | DD102, B29 |
| 降级震荡 | 全局 DegradationCoordinator+冷却期 30s | DD141, B69 |
| CE 启动中收到请求 | 返回 503 Service Unavailable | DD142, B70 |
| LSG 模式级拒绝 | rejection_reason_code→切换检索关键词重新 build | DD94, B20 |

---

## §8 安全考量

| # | 安全项 | 威胁模型 | 缓解措施 |
|---|--------|---------|---------|
| 1 | LSG 安全审查 | 恶意知识注入 Agent session | 三级审查（格式→语义→策略），拒绝率≥5%触发告警 |
| 2 | Token 预算硬限制 | 上下文爆炸导致 OOM | L3_HARD_STOP，不追加 context |
| 3 | shadow-then-swap 注入 | 注入中途失败导致 session 不一致 | 原子替换，失败回滚 |
| 4 | VMS 数据投毒 | 检索到被污染的知识 | VMS 侧 provenance 验证 + CE 侧 LSG 审查双重防护 |

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 工具/方法 |
|---|---------|---------|---------|
| 1 | 单元测试 | 各组件独立逻辑 | pytest + mock VMS/LSG |
| 2 | 集成测试 | 四阶段流水线端到端 | pytest + 真实 VMS |
| 3 | 容量测试 | Token 预算边界 | 压测脚本 + 10K token 注入 |
| 4 | 安全测试 | LSG 拒绝路径 | 投毒 payload 注入 |

## §10 依赖关系

### §10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-INF-011 VMS | 必须 | 知识检索 | — | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\vms\blueprint.md` |
| MOD-INF-006 Task System | 必须 | 任务状态 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\task-system\blueprint.md` |
| MOD-INF-035 AutoRuntime Core | 可选 | 运行时调度 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-runtime-core\blueprint.md` |

### §10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 每个依赖在 registry 中有对应条目 | 未对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-008` |

### §10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| 无内部脚本依赖 | — | — | — |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| VMS 检索结果 | Compressor | raw_context: list[str] | 函数调用 |
| Compressor 输出 | Validator | compressed_context: str | 函数调用 |
| Validator 输出 | Injector | validated_context: str | 函数调用 |

### §10.4 自动化规格

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 否 | 模块数≤5 |
| 2 | 依赖对齐自动验证 | 是 | 有外部依赖 |

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\context-engine\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\context_engine\` | CE 源码 |
| 测试代码 | `D:\ZephyrAlpha\tests\context_engine\` | CE 测试用例 |

## §12 集成目标

| # | 集成目标 | 对接模块 | 接口 | 状态 |
|---|---------|---------|------|:---:|
| 1 | Orchestrator 消费 CE 输出 | MOD-INF-006 | CE→Orc 优先级协议 | 已实现 |
| 2 | VMS 知识检索 | MOD-INF-011 | build 阶段查询 | 已实现 |
| 3 | LSG 安全审查 | MOD-INF-012 | validate 阶段审查 | 已实现 |

## §13 需要更新

| # | 更新对象 | 触发条件 | 更新内容 |
|---|---------|---------|---------|
| 1 | blueprint-registry.yaml | 版本变更 | 版本号同步 |
| 2 | __init__.py __all__ | 新增导出 | 导出列表同步 |

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|:---:|:---:|---------|------|
| 1 | VMS 不可用导致全降级 | 中 | 高 | 三级降级策略 | 风险 |
| 2 | LSG 误拒合法知识 | 低 | 中 | rejection_reason_code 诊断 | 风险 |
| 3 | Token 预算硬限制截断关键上下文 | 中 | 高 | 优先级排序+关键信息前置 | 风险 |

---

## §16 施工指引

### §16.1 添加新 intent 类型

1. `intent_parser.py` IntentType 枚举中添加
2. `intent_keyword_mapper.py` _MAP 中添加映射
3. 运行 `test_intent_parser.py` + `test_intent_keyword_mapper.py`

### §16.2 修改 DocCompressor

- CompressionPolicy 为 Immutable Core (Pydantic frozen)→修改需 Human-Gated
- compress() 实现可 AI-Modified→修改后运行 `test_doc_compressor.py`

### §16.3 容量升级施工里程碑

```
M0 — "不崩" (CE 执行引擎并发安全)
  交付: DD133-DD142 (PipelineOrchestrator async/BudgetTracker 原子化/LLMInferencePool/VMSConnectionPool/MetricsCollector ring buffer/CEStartupReadinessGate/Per-Session RWLock/GlobalDegradationCoordinator)
  验收: 100 并发 build() 压测→零竞态→零预算泄漏→零数据损坏

M1 — "能跑" (P0 阻塞项)
  交付: DD121/DD123/DD128/DD132 + B24/DD98/B30 补齐 + DD138 StageExecutor + DD139 DiffCPUBudget

M2 — "好用" (P1 基础设施)
  交付: DD124/DD125/DD127/DD118/DD122

M3 — "完善" (P2 运维与优化)
  交付: DD131/DD130/DD129/B47/DD113/DD126

M4 — "验证" (端到端压测)
  交付: M0-M3 全部集成 + 100 Agent 模拟并发→增量扫描 p99<3s + 全量扫描 12 shard 串行<24h
```

### §16.4 前施工期骨架文件→本次集成动作

| 文件 | 前状态 | 本次动作 | 里程碑 |
|------|:---:|------|:---:|
| diff_injector.py | 骨架落盘 | 接入 PipelineOrchestrator.run() | M1 |
| cache_invalidation.py | 骨架落盘 | 接入 VMS write event bus | M2 |
| self_diagnosis.py | 骨架落盘 | 补齐诊断指标，暴露 CLI | M3 |
| contextual_fetch_api.py | 骨架落盘 | 补齐 MCP tool 注册，写集成测试 | M3 |
| checkpoint_manager.py | 骨架落盘 | 接入 Orc session lifecycle | M3 |
| mode_manager.py | 骨架落盘 | 接入 PipelineOrchestrator 初始化 | M3 |
| stalleness_manager.py | 骨架落盘 | 接入 context_assembler.build() | M2 |
| cold_start_booster.py | 骨架落盘 | 接入 CE startup sequence | M2 |
| kill_switch.py | 骨架落盘 | 补齐 /ce:kill + /ce:revive | M3 |
| host_resource_governor.py | 骨架落盘 | 接入 CE init，监控 RAM 使用 | M2 |

---

## §17 容量升级附录

### §17.1 容量基线

| # | 盲点 | 严重度 | 关联 DD |
|---|------|:---:|---------|
| B49 | Trigger Router 精度衰减 | P0 | DD121 |
| B50 | 脚本依赖拓扑爆炸 | P0 | DD122 |
| B51 | Multi-Agent CE 请求合并缺失 | P0 | DD123 |
| B52 | Trigger Router 索引性能退化 | P1 | DD124 |
| B53 | 脚本 Manifest 全量加载开销 | P1 | DD124 |
| B54 | 100 Agent 同时冷启动 CE 雪崩 | P1 | DD125 |
| B55 | 治理脚本分类层级不足 | P2 | DD126 |
| B56 | 跨模块契约容量约束缺失 | P1 | DD127 |
| B57 | 增量扫描触发风暴节流缺失 | P1 | DD128 |
| B58 | Agent Session 上下文沙箱内存压力 | P2 | DD129 |
| B59 | 治理脚本优先级调度缺失 | P2 | DD130 |
| B60 | 全量扫描分片策略缺失 | P2 | DD131 |
| B61 | PipelineOrchestrator 单线程瓶颈 | P0 | DD133 |
| B62 | ContextBudgetTracker TOCTOU 竞态 | P0 | DD134 |
| B63 | Qwen2.5-3B 推理吞吐瓶颈 | P0 | DD135 |
| B64 | VMS 检索连接池缺失 | P1 | DD136 |
| B65 | Observer/Metrics 写入竞态 | P1 | DD137 |
| B66 | 四阶段流水线跨 Session 并行调度缺失 | P1 | DD138 |
| B67 | ContextDiff 计算 CPU 预算缺失 | P1 | DD139 |
| B68 | Session 上下文状态并发读写安全 | P1 | DD140 |
| B69 | CE 降级状态机并发协调 | P2 | DD141 |
| B70 | CE 启动就绪门控 | P2 | DD142 |

### §17.2 缺口分析

| 原盲点 | 原严重度 | 新严重度 | 升级理由 |
|--------|:---:|:---:|------|
| B24 (无差异注入) | P0 | P0+ | 100 Agent×全量 rebuild=不可承受 |
| B30 (多 Agent 预算仲裁) | P1 | P0 | 100 Agent 共享资源无仲裁=雪崩 |
| B37 (冷启动预热) | P2 | P0 | 无 readiness gate=首批全错 |
| B39 (无 Agentic Pull) | P0 | P0+ | Push 模型下 CE 成单点热点 |
| B44 (事件驱动缓存) | P1 | P0 | 5min TTL 在 100 Agent 高频修改下命中率≈0% |
| B47 (CE 自诊断 API) | P2 | P1 | 1 人运维+100 Agent→必须快速诊断 |

### §17.3 升级版本矩阵

| 维度 | 盲点数 | 状态 |
|------|:---:|:---:|
| CE 静态结构与安全 | 91 | ✅ 饱和 |
| CE 时间生命线 | 16 | ✅ 饱和 |
| CE 交互/认知/运维 | 10 | ✅ 饱和 |
| Trigger Router & 脚本系统容量 | 12 |
| 13 | **已实现代码不在蓝图中重复**——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4） | 代码文件是 SSoT，蓝图复制代码=双源漂移 | AI 改蓝图忘改代码，或改代码忘改蓝图 |
| 14 | **临时时态内容执行完毕后从蓝图删除**——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 | 蓝图是当前设计文档，不是历史记录 | 蓝图膨胀，关键信息被历史噪音淹没 |
| 15 | **蓝图内容拆分判定**——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | 职责不同的内容强行塞一个蓝图=职责不清 | AI 不知道该读哪个蓝图，跨模块影响无法追踪 |
| 12 | ✅ 饱和 |
| CE 执行引擎并发架构 | 10 | ✅ 饱和 |
| **合计** | **139** | ✅ 全维度饱和 |

---

## §18 决策记录

### 设计决策汇总 (DD1-DD142)

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | DD1 | 4 阶段 vs 3 或 5 | 3/4/5 阶段 | 4 阶段 | Build/Compress/Validate/Inject 各有独立失败域 | 2026-05-05 |
| 2 | DD2 | Token 预算三级 80%/90%/95% | 单阈值/双级/三级 | 三级 | 80%预警有余量做 compress | 2026-05-05 |
| 3 | DD3 | DocCompressor Pydantic frozen 不可变策略 | 可变/frozen | frozen | LSG 安全审查依赖不变量 | 2026-05-05 |
| 4 | DD4 | intent_parser 10 分类 | 10/30+ 分类 | 10 分类 | 覆盖 task_type 枚举+辅助模式 | 2026-05-05 |
| 5 | DD5 | DocCompressor 三级降级 | 单级/双级/三级 | 三级 | 渐进式：规则基→本地 LLM→截断 | 2026-05-05 |
| 6 | DD6 | token_budget=8000 默认 | 4000/8000/不设限 | 8000 | 主流模型 context window 的 10-15% | 2026-05-05 |
| 7 | DD7 | ContextRot 幂函数 n^{-k} | 线性/幂函数 | 幂函数 | n² 衰减是幂级数 | 2026-05-05 |
| 8 | DD8 | Provenance 全覆盖 | 部分/全覆盖 | 全覆盖 | 上下文致错时唯一追溯链 | 2026-05-05 |
| 9 | DD9 | Eviction 三维排序 | FIFO/LRU/三维 | 三维 | Token 超预算精准逐出 | 2026-05-05 |
| 10 | DD10 | Per-Turn 增量注入 | 全量/增量 | 增量 | Agent 5 轮全量 build=n×5 token 浪费 | 2026-05-05 |
| 11 | DD75 | CE Bootstrap 三层递进 | 单层/三层 | 三层 | 100% AI 施工离不开 CE | 2026-05-05 |
| 12 | DD76 | KE Value ROI 公式 | 无/ROI | ROI | token 零浪费 | 2026-05-05 |
| 13 | DD77 | Strategy Auto-Evolution | 固定/自动 | 自动 | MetaCE 选了策略但不知何时换挡 | 2026-05-05 |
| 14 | DD78 | Canary Promotion: Shadow+3sigma | A/B 双轨/Shadow | Shadow | 免 A/B 双轨资源消耗 | 2026-05-05 |
| 15 | DD79 | Context Playground: /sc:dry-run | 无/Playground | Playground | Owner vibe coding 直观验证 | 2026-05-05 |
| 16 | DD80 | Unified Health Score(0-100)=PCA | 网格/单一值 | PCA 单一值 | 1 人操作:单一数值取代网格 | 2026-05-05 |
| 17 | DD81 | Progressive Disclosure: 摘要先注 | 全量/渐进 | 渐进 | 大幅减少初始 inject token | 2026-05-05 |
| 18 | DD82 | Adversarial: Fuzz+Semantic Perturb | 无/Adversarial | Adversarial | 安全检测器自身不能 stop testing | 2026-05-05 |
| 19 | DD83 | Sensitivity 4-tier per KE auto-classify | 无/4-tier | 4-tier | Privacy Scrubber 拦截 PII 但无分类可见性 | 2026-05-05 |
| 20 | DD84 | Knowledge Distillation: DBSCAN 同类→1 代表 | 无/蒸馏 | 蒸馏 | KE 增长不可避免；信息密度必须维持 | 2026-05-05 |
| 21 | DD85 | Context Intent Alignment Score | 无/Alignment | Alignment | CEEval 测质量，Alignment 测对齐度 | 2026-05-05 |
| 22 | DD86 | OpenTelemetry Full Trace + SRE | 无/OTEL | OTEL | CE 是线上服务 | 2026-05-05 |
| 23 | DD87 | Fallback Freshness Gate: >90d→WARN | 无/Freshness | Freshness | 兜底层的错误是"无药可救"的错误 | 2026-05-05 |
| 24 | DD88 | Context-Outcome Causal Tracking | 无/Causal | Causal | 闭环：从上下文质量到决策质量 | 2026-05-05 |
| 25 | DD89 | P0 任务 Context Injection Confirmation Gate | 无/Confirmation | Confirmation | 1 人模式下唯一安全阀 | 2026-05-05 |
| 26 | DD90 | Config Safety Domain: [min,max,default] | 无/Domain | Domain | AI 自维护的安全底线 | 2026-05-05 |
| 27 | DD91 | Host Resource Budget: 模型加载<25% RAM | 无/Budget | Budget | 16GB 笔记本上的生存策略 | 2026-05-05 |
| 28 | DD92 | Embedding Model Version Lock | 无/Lock | Lock | 确定性建立在锁上 | 2026-05-05 |
| 29 | DD93 | Context Debt Score: per-KE deprecation_risk | 无/Debt | Debt | 分辨"不被用"vs"被用但有害" | 2026-05-05 |
| 30 | DD94 | LSG Rejection Pattern Tracking | 无/Pattern | Pattern | 块替换逃逸的结构性破解 | 2026-05-05 |
| 31 | DD95 | KE Authority Level: Human>Agent>Inferred | 无/Authority | Authority | 防止珍贵人工信号被 AI 噪声稀释 | 2026-05-05 |
| 32 | DD96 | CE-Orc Context Precedence: CE overrides | Orc 优先/CE 优先 | CE 优先 | 确定性>灵活性 | 2026-05-05 |
| 33 | DD97 | Context Poisoning Monitor | 无/Monitor | Monitor | CE 需要知道自己何时提供了坏上下文 | 2026-05-06 |
| 34 | DD98 | ContextDiff: 仅注入 delta | 全量/增量 | 增量 | 多轮对话 token 节约率>60% | 2026-05-06 |
| 35 | DD99 | ExplainableKE: per-KE inclusion_rationale | 无/Explainable | Explainable | Owner 调试上下文的核心工具 | 2026-05-06 |
| 36 | DD100 | SessionCheckpoint: session 结束→序列化 | 无/Checkpoint | Checkpoint | 跨天任务连续性 | 2026-05-06 |
| 37 | DD101 | HealthTriggeredReset: Score<50→reset | 无/Reset | Reset | Health Score 从壁纸升级为触发器 | 2026-05-06 |
| 38 | DD102 | AtomicInjection: shadow-then-swap | 非原子/原子 | 原子 | 半注入 Agent 不可恢复 | 2026-05-06 |
| 39 | DD103 | ComplexityBudget: complexity→budget | 固定/自适应 | 自适应 | 简单任务不该消耗等同复杂任务 | 2026-05-06 |
| 40 | DD104 | CEModeSwitch: vibe/strict profile | 单模式/双模式 | 双模式 | vibe 需宽松探索，strict 需合规精准 | 2026-05-06 |
| 41 | DD105 | DomainDecayConfig: per-domain TTL | 统一/per-domain | per-domain | 安全 KE 和架构 KE 生命周期完全不同 | 2026-05-06 |
| 42 | DD106 | KEIntegrityCheck: SHA-256 | 无/校验 | 校验 | 静默数据损坏在单机环境是真实风险 | 2026-05-06 |
| 43 | DD107 | InjectionPositionOptimizer: primacy/recency | 无/优化 | 优化 | 首尾信息记忆率>中间 2 倍 | 2026-05-06 |
| 44 | DD108 | ContextFragmentationIndex: CI>0.7 warn | 无/碎片化 | 碎片化 | 高度碎片化降低 LLM 推理质量 | 2026-05-06 |
| 45 | DD109 | ColdStartWarmUp: 异步 preload | 无/预热 | 预热 | 首批 build P99<200ms | 2026-05-06 |
| 46 | DD110 | EmergencyGlobalKillSwitch: /ce:kill | 无/KillSwitch | KillSwitch | 生产事故中止血是最高优先级 | 2026-05-06 |
| 47 | DD111 | MCPPerIDECapabilityAdapter | 无/MCP | MCP | ADR-0015 明确要求 MCP 能力协商 | 2026-05-06 |
| 48 | DD112 | ContextStalenessBetweenBuildAndInject | 无/Staleness | Staleness | 高频 vibe coding 中文件变化极快 | 2026-05-06 |
| 49 | DD113 | AgenticPullAPI: /ce:fetch MCP tool | Push-only/Push+Pull | Push+Pull | 行业 2026 标杆已切换 pull 模型 | 2026-05-07 |
| 50 | DD114 | IntegrationTestGoldens: Jaccard≥0.85 | 无/Goldens | Goldens | 打破测试保真度断层 | 2026-05-07 |
| 51 | DD115 | SessionPatternLearner: 离线聚类 | 无/Learner | Learner | 跨 session 学习 | 2026-05-07 |
| 52 | DD116 | ExternalDepTracker: KE deps snapshot | 无/Tracker | Tracker | 解决库版本过期 | 2026-05-07 |
| 53 | DD117 | CitationGraphWalker: 1-2 hop retrieve | 无/Walker | Walker | 引用图遍历 | 2026-05-07 |
| 54 | DD118 | EventDrivenInvalidation: VMS write events | TTL/事件驱动 | 事件驱动 | 缓存事件驱动失效 | 2026-05-07 |
| 55 | DD119 | ModelAwareBudget: per-model strategy | 统一/per-model | per-model | 模型无感知 | 2026-05-07 |
| 56 | DD120 | DiversityConstraint: max per source | 无/Diversity | Diversity | 同质化检索 | 2026-05-07 |
| 57 | DD121 | Trigger Blast Radius Budget: >100→分层 | 无/BlastRadius | BlastRadius | 防止增量扫描退化为半全量 | 2026-05-10 |
| 58 | DD122 | Script DAG 分层编译: D1-D12 分区 | 无/分层 | 分层 | 10,000 节点依赖图优化 | 2026-05-10 |
| 59 | DD123 | CE Request Coalescer: 200ms 窗口合并 | 无/Coalescer | Coalescer | 100 Agent 做相似任务 VMS 查询合并 | 2026-05-10 |
| 60 | DD124 | Trigger Router 二进制索引 | YAML/二进制 | 二进制 | YAML→pickle/sqlite .idx | 2026-05-10 |
| 61 | DD125 | CE Session Warm-Up Pool: 预创建 10 | 无/WarmUp | WarmUp | 100 Agent 同时冷启动雪崩 | 2026-05-10 |
| 62 | DD126 | Governance Script Sub-Category | 粗分类/子分类 | 子分类 | 10,000 脚本时粗分类精度不足 | 2026-05-10 |
| 63 | DD127 | CT-\* Contract Capacity Clause | 无/Capacity | Capacity | 跨模块调用方不知道容量上限 | 2026-05-10 |
| 64 | DD128 | Scan Throttle Coalescer: 500ms 窗口 | 无/Throttle | Throttle | 增量扫描触发风暴 | 2026-05-10 |
| 65 | DD129 | Session Context TTL Swapper: 30min→磁盘 | 无/Swapper | Swapper | 100 Agent session 内存压力 | 2026-05-10 |
| 66 | DD130 | Script Priority Scheduling: P0→P1→P2 | FIFO/优先级 | 优先级 | 安全脚本不应排在风格检查后面 | 2026-05-10 |
| 67 | DD131 | Full Scan Sharding: 12 shard | 单机/分片 | 分片 | 全量扫描 130h 无法执行 | 2026-05-10 |
| 68 | DD132 | CE Backpressure Signal: 80%→排队 | 无/Backpressure | Backpressure | CE 无"忙不过来"信号 | 2026-05-10 |
| 69 | DD133 | PipelineOrchestrator Async+Semaphore | 同步/异步 | 异步 | B61——100 并发调用正确性基础 | 2026-05-10 |
| 70 | DD134 | ContextBudgetTracker 原子化 try_consume | 非原子/原子 | 原子 | B62——TOCTOU 竞态根治 | 2026-05-10 |
| 71 | DD135 | LLMInferencePool: max_concurrent=8 | 无/池化 | 池化 | B63——GPU 推理吞吐瓶颈 | 2026-05-10 |
| 72 | DD136 | VMSConnectionPool: min4 max16 | 无/连接池 | 连接池 | B64——VMS 连接层防护 | 2026-05-10 |
| 73 | DD137 | MetricsCollector thread-safe ring buffer | 非安全/安全 | 安全 | B65——metrics 收集不可成为瓶颈 | 2026-05-10 |
| 74 | DD138 | StageExecutor 跨 Session 调度 | 无/调度器 | 调度器 | B66——跨 session 阶段并行 | 2026-05-10 |
| 75 | DD139 | ContextDiff CPU Budget: max_concurrent=20 | 无/预算 | 预算 | B67——diff 不能吃掉所有 CPU | 2026-05-10 |
| 76 | DD140 | Per-Session ReadWriteLock | 无/读写锁 | 读写锁 | B68——session 状态并发安全 | 2026-05-10 |
| 77 | DD141 | GlobalDegradationCoordinator+冷却期 30s | 无/协调器 | 协调器 | B69——降级震荡 | 2026-05-10 |
| 78 | DD142 | CEStartupReadinessGate: CE_READY flag | 无/就绪门 | 就绪门 | B70——启动时序契约 | 2026-05-10 |

### 盲点汇总 (B1-B70)

| 范围 | 盲点 | 严重度 | 关联 DD |
|------|------|:---:|---------|
| B1 | CE 自举架构 | P0 | DD75 |
| B2 | 上下文价值归因 | P0 | DD76 |
| B3 | 策略自动进化 | P1 | DD77 |
| B4 | 金丝雀部署 | P1→done | DD78 |
| B5 | 上下文沙箱 | P1 | DD79 |
| B6 | 统一上下文健康分 | P1 | DD80 |
| B7 | 渐进式信息披露 | P1 | DD81 |
| B8 | 对抗鲁棒性测试 | P1 | DD82 |
| B9 | 上下文数据分级 | P2 | DD83 |
| B10 | 知识蒸馏 | P2 | DD84 |
| B11 | 意图-上下文对齐评分 | P2 | DD85 |
| B12 | 全链路 OTEL & SRE | P2 | DD86 |
| B13 | 终极兜底层自腐 | P0 | DD87 |
| B14 | 上下文-决策因果链断裂 | P0 | DD88 |
| B15 | 单人无审查安全网缺失 | P0 | DD89 |
| B16 | AI 自维护配置自毁 | P1 | DD90 |
| B17 | CE 主机资源治理 | P1 | DD91 |
| B18 | 嵌入模型版本锁定 | P1 | DD92 |
| B19 | 上下文债务量化 | P1 | DD93 |
| B20 | LSG 模式级拒绝块替换逃逸 | P2 | DD94 |
| B21 | 知识权威链缺失 | P1 | DD95 |
| B22 | CE-Orc 上下文冲突无解 | P1 | DD96 |
| B23 | 上下文毒化无感知与无重置 | P0 | DD97 |
| B24 | 全量重复注入无差异计算 | P0 | DD98 |
| B25 | 构建决策不可解释 | P0 | DD99 |
| B26 | 跨 Session 上下文状态断裂 | P0 | DD100 |
| B27 | 健康分触发自动上下文重置 | P0 | DD101 |
| B28 | 领域差异化新鲜度衰减 | P1 | DD105 |
| B29 | 四层注入无原子性事务 | P1 | DD102 |
| B30 | 多 Agent 并发上下文预算仲裁 | P1 | DD103 |
| B31 | 静态上下文明文存储 | P1 | DD83 |
| B32 | KE 完整性无校验 | P1 | DD106 |
| B33 | CE 无运行模式感知 | P1 | DD104 |
| B34 | 上下文注入位置未优化 | P1 | DD107 |
| B35 | 任务复杂度不感知固定预算 | P1 | DD103 |
| B36 | 上下文碎片化度量 | P2 | DD108 |
| B37 | 冷启动预热策略 | P2 | DD109 |
| B38 | CE 全局紧急熔断 | P2 | DD110 |
| B39 | Push-Only 架构无 Agentic Pull | P0 | DD113 |
| B40 | 上下文测试保真度断层 | P0 | DD114 |
| B41 | 跨 Session 模式学习缺失 | P0 | DD115 |
| B42 | 外部依赖版本感知 KE 过期 | P1 | DD116 |
| B43 | 平面化检索无引用图遍历 | P1 | DD117 |
| B44 | 时间驱动缓存无事件驱动失效 | P1 | DD118 |
| B45 | 模型无感知上下文策略 | P1 | DD119 |
| B46 | 检索同质化无多样性约束 | P1 | DD120 |
| B47 | CE 自我诊断 API 缺失 | P2 | — |
| B48 | 上下文预算预测 | P2 | — |
| B49-B70 | 见 §17.1 | — | 见 §17.1 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 代码文件 MUST 标注 `[BLUEPRINT] MOD-INF-008 \| 本蓝图 §N` | 无标注 = 孤儿文件 |
| 2 | 代码文件 MUST 标注 `[INVARIANTS]` 不变量 | AI 修改时破坏关键约束 |
| 3 | 代码文件 MUST 标注 `[MODIFY-GUARD]` 同步更新清单 | 改一处忘其他，集成断裂 |
| 4 | 代码文件 MUST 标注 `[CONSUMERS]` 消费者 | 不知道修改影响范围 |
| 5 | 蓝图 §4 文件清单 ↔ 代码 `[BLUEPRINT]` 字段 MUST 双向对齐 | 蓝图与代码漂移 |
| 6 | 禁止占位符（TODO/.../pass/NotImplementedError） | 半成品伪装完成 |
| 7 | 编辑优先，最小变更 | 丢失 history + 引入无关 bug |

## ⚠️ 安全删除协议

| 步骤 | 操作 |
|------|------|
| 1 | 登记检查：文件是否在 manifest/registry/\_\_init\_\_.py 中被引用？在 git log 中存在？→ 有价值，只能 refactor/rehome |
| 2 | 重复检查：有另一个文件与它内容完全相同且已注册？→ 真正重复可删 |
| 3 | 逐行价值检查：每行内容是否在其他地方存在？删除后有无引用报错？→ 有唯一价值则重新安置 |

## 必备链接

| 资源 | 路径 |
|------|------|
| CE YAML SSoT | [b_context_engine.yaml](file:///D:/ZephyrAlpha/architecture-model/layers/b_context_engine.yaml) |
| 代码落位 | `src/zephyr/context_engine/` |
| 总蓝图 | [MASTER-001](file:///D:/ZephyrAlpha/docs/03_modules/_master-blueprint/blueprint.md) |
| VMS 蓝图 | MOD-INF-011 |
| LSG 蓝图 | MOD-INF-014 |
| Orchestrator 蓝图 | MOD-INF-006 |
| 知识库蓝图 | MOD-KB-001 |
| 蓝图注册表 | [blueprint-registry.yaml](file:///D:/ZephyrAlpha/docs/03_modules/blueprint-registry.yaml) |
| 模板注册表 | [template-registry.yaml](file:///D:/ZephyrAlpha/docs/03_modules/template-registry.yaml) |

## 项目中已有类似功能

| 模块 | 覆盖范围 | 与 CE 的区别 |
|------|---------|-------------|
| MOD-INF-006 (Orchestrator) | Agent session 管理 | Orc 管理 Agent 生命周期；CE 管理上下文内容 |
| MOD-INF-011 (VMS) | 向量存储与检索 | VMS 是存储层；CE 是消费层 |
| MOD-INF-014 (LSG) | 安全审查 | LSG 是安全门；CE 是上下文管道 |
| MOD-KB-001 (知识库) | KE CRUD | KB 是数据源；CE 是数据消费者 |

## 涉及的文件范围

| 目录 | 文件数 | 说明 |
|------|:---:|------|
| `src/zephyr/context_engine/` | 85 | 核心源码（含 support/assembly/parsing/management 子包） |
| `src/zephyr/context_engine/config/` | 2 | 配置文件 |
| `tests/` | 15+ | 测试文件 |

---

## 治理信息

### SSoT 声明

本蓝图为 MOD-INF-008 的唯一设计文档。canonical SSoT 为 `architecture-model/layers/b_context_engine.yaml`。代码落位 `src/zephyr/context_engine/`。

### 消费者注册表

| 消费者 | 消费方式 | 契约 |
|--------|---------|------|
| MOD-MASTER-001 (Orchestrator) | 调用 CE.build() | CT-ORC-CE-001 |
| MOD-INF-011 (VMS) | 被 CE 检索 | CT-CE-VMS-001 |
| MOD-INF-014 (LSG) | 被 CE 调用审查 | CT-CE-LSG-001 |
| AI Agent (via MCP) | 调用 /ce:fetch | DD113 |

### 变更同步规则

| 修改此文件 | MUST 同步更新 |
|-----------|-------------|
| §0 代码文件清单 | 代码文件 `[BLUEPRINT]` 字段 |
| §4 接口契约 | 对应 CT-\* 契约文件 |
| §18 DD 表 | PS-REG-012 对应字段 |
| frontmatter version | blueprint-registry.yaml |

### 修改条件

| 条件 | 要求 |
|------|------|
| 修改 DD1-DD6 (核心决策) | Human-Gated: 需 Owner 批准 |
| 修改 DD3 (CompressionPolicy) | Immutable Core: Pydantic frozen |
| 修改接口契约 | 双方模块 Owner 确认 |
| 修改容量 SLO | 运行压测验证 |
| 新增盲点/B/DD | 必须关联已有 DD 并声明重评触发条件 |

---

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 上下文引擎——9文件骨架+assembler+injector已实现

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/context_engine/adversarial_robustness.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/alignment_scorer.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/architecture_context.json` | ✅ 已实现 | |
| `src/zephyr/context_engine/architecture_context_loader.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/assembly/context_assembler.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/assembly/context_injector.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/assembly/context_pipeline.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/atomic_injector.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/budget_forecaster.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/cache_invalidation.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/ce_bootstrap.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/ce_explain_cli.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/ce_playground_v2.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/ce_vibe_shortcuts.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/checkpoint_manager.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/citation_walker.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/cold_start_booster.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/complexity_budget.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/config/compression/policy.yaml` | ✅ 已实现 | |
| `src/zephyr/context_engine/config/context_rules_v1.yaml` | ✅ 已实现 | |
| `src/zephyr/context_engine/config_safety_guard.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/context_assembler.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/context_budget.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/context_budget_tracker.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/context_debt_score.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/context_evaluator.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/context_evictor.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/context_injector.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/context_model_strategy.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/context_outcome_tracker.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/context_pipeline.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/context_playground.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/context_rot_model.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/context_value_attribution.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/ContextHealthScore.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/contextual_fetch_api.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/curation_loop.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/dependency_tracker.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/diff_injector.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/dispatch_table.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/diversity_constraint.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/doc_compressor.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/domain_decay_config.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/embedding_version_lock.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/fallback_staleness_gate.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/fragmentation_index.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/host_resource_governor.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/integrity_check.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/intent_keyword_mapper.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/intent_parser.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/kill_switch.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/knowledge_distiller.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/list_ce_files.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/lsg_pattern_tracker.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/management/context_budget_tracker.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/management/context_evictor.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/management/context_rot_model.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/mcp_adapter.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/memory_bank.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/mode_manager.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/otel_instrumentation.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/parsing/intent_keyword_mapper.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/parsing/intent_parser.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/pattern_library.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/pipeline_orchestrator.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/poisoning_monitor.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/position_optimizer.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/progressive_disclosure_injector.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/prompt_registry.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/rational.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/risk_register.yaml` | ✅ 已实现 | |
| `src/zephyr/context_engine/self_diagnosis.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/sensitivity_classifier.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/session_learner.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/shadow_canary.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/solo_dev_safety_net.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/staleness_manager.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/support/architecture_context_loader.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/support/doc_compressor.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/support/prompt_registry.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/support/system_snapshot.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/system_snapshot.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/token_budget.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/vector_bridge.py` | ✅ 已实现 | |
| `src/zephyr/context_engine/verify_paths.py` | ✅ 已实现 | |

### 1.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/unit/test_context_injector.py` | ✅ 已实现 | |
| `tests/unit/test_doc_compressor.py` | ✅ 已实现 | |
| `tests/unit/test_prompt_registry.py` | ✅ 已实现 | |
| `tests/unit/test_intent_parser.py` | ✅ 已实现 | |
| `tests/unit/test_intent_keyword_mapper.py` | ✅ 已实现 | |
| `tests/unit/test_pattern_library.py` | ✅ 已实现 | |
| `tests/unit/test_system_snapshot.py` | ✅ 已实现 | |

### 1.3 配置文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `config/context_rules.yaml` | ✅ 已实现 | |
| `config/compression/policy.yaml` | ✅ 已实现 | |

### 1.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---

## 变更记录

| 日期 | 版本 | 变更摘要 |
|------|------|---------|
| 2026-05-04 | 0.2.0 | 代码-蓝图对齐审计+黄金标准补齐：§5 Core Flow YAML/§6 DD1-DD6/§7 AP1-AP7/§8 集成契约/§9 风险/§11 施工指南/§12 基于磁盘真实 |
| 2026-05-05 | 0.3.0 | beta 全面升级：§13 深度对标/§14 10 项缺失/§15 beta 三期/§16 DD7-DD10 |
| 2026-05-05 | 0.5.0 | 第十二轮审计：B1-B12/AP10-AP21/DD75-DD86/beta v+w |
| 2026-05-05 | 0.5.1 | 第十三轮取证审计：B13-B20/AP22-AP29/DD87-DD94/beta x |
| 2026-05-05 | 0.5.2 | 第十四轮终审：B21-B22/DD95-DD96/AP30-AP31 |
| 2026-05-06 | 0.6.0 | 第十五轮生命线审计：B23-B38/AP32-AP39/DD97-DD112/beta y-ab |
| 2026-05-06 | 0.7.0 | 第十六轮交互审计：B39-B48/AP40-AP47/DD113-DD120/beta ac-af |
| 2026-05-07 | 0.8.0 | 第十七轮零债务对齐：214/214 测试全绿；蓝图与磁盘完全一致 |
| 2026-05-10 | 0.9.0 | 容量升级：B49-B60/DD121-DD132/AP48-AP55/M1-M3 里程碑 |
| 2026-05-10 | 0.9.1 | 执行引擎并发审计：B61-B70/DD133-DD142/AP56-AP65/M0-M4 五里程碑 |
| 2026-05-13 | L1 | 规格化：Layer 1 模板合规+Layer 2 砍冗余。砍掉§13深度对标分析、多轮审计过程叙述(§14-EXPANDED~§23)、💡散文、变更记录散文；合并 DD/B/AP 表为统一汇总；添加 pre-sections/§0 代码对齐验证/缺失模板章节/治理信息 |
| 2026-05-14 | v3.3 | 蓝图模板 v3.5 重构：新增概述段+标准锚点；章节重排(§1-§15 设计→§0 对齐验证→§16-§18 施工→规则参考段→治理信息)；合并双 H1 为单 H1；# §N→## §N 统一；frontmatter 更新(template_for/parent_module/rule_form/scope/stability/verifiability)；§4.4-4.6 重命名(输出契约/MCP接口/契约版本)；§5.2 容量估算6列；§5.3 迁移/废弃方案；§10 依赖5列；§11 产出物存放目录；§14 已知风险与缓解；§17 容量升级附录(基线/缺口/矩阵)；§18 决策记录7列 |

---
