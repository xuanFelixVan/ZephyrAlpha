---
module_id: "MOD-INF-008"
title: "Context Engine 蓝图 — build→compress→validate→inject 四阶段上下文注入"
doc_type: blueprint
status: draft
version: "0.2.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-03"
valid_from: "2026-05-03"
ttl: permanent
construction_progress: phase_1_partial
ai_role_instruction: >
  你是上下文引擎蓝图(MOD-INF-008)，是ZephyrAlpha所有AI agent调用的上下文构建中枢。
  你负责四阶段流水线(build→compress→validate→inject)，从12系统全局状态+向量记忆中组装最优上下文。
  核心规则：(1)上下文不生成内容——只负责收集、压缩、校验、注入；(2)永远不给未经LSG审查的上下文给LLM；
  (3)compress阶段永不丢弃raw_text——LSG需要它做安全检测；(4)Cache短周期重复内容——不要对同一session反复查VMS。
summary: "ZephyrAlpha Context Engine 蓝图——四阶段上下文注入流水线(build→compress→validate→inject)+DocCompressor压缩服务(563行完整实现/Immutable Core+Pydantic frozen不变量)+ContextInjector知识检索注入(3种RetrievalMode)+ContextBudgetTracker Token三级预算(L1 80%/L2 90%/L3 95%)+intent_parser 10类意图解析+三级降级策略(VMS不可用/LSG拒绝/超时)。对标 Anthropic Codified Context(三层记忆)+Google Vertex AI Context Caching+Cursor Rules(Always-on Context)+Windsurf Rules(Context Freshness Decay)+RAG社区(Multi-Query+Dedup)。"
tags: [context-engine, ce, context-injection, rag, token-budget, build-compress-validate-inject, local-llm, infrastructure]
priority: P0
depends_on:
  - {target: "MOD-MASTER-001", at: "§2.3", why: "CT-ORC-CE-001 集成契约——Orc→CE上下文构建请求时序"}
  - {target: "MOD-MASTER-001", at: "§2.6", why: "CT-CE-VMS-001 集成契约——CE→VMS向量检索"}
  - {target: "MOD-KB-001", at: "§1.5", why: "知识库——CE的上下文检索源"}
  - {target: "architecture-model/layers/b_context_engine.yaml", at: "全篇", why: "CE YAML SSoT——本蓝图真源"}
---

# Context Engine 蓝图 — 四阶段上下文注入

> **module_id**: MOD-INF-008 | **version**: 0.2.0 | **status**: draft | **layer**: cross_layer

> **真源声明**：本蓝图的 canonical SSoT 为 [b_context_engine.yaml](file:///D:/ZephyrAlpha/architecture-model/layers/b_context_engine.yaml)。
> 代码落位：`src/zephyr/context_engine/`（9 个 .py 文件，bounded_context=true）。

> **对标**：Anthropic Codified Context（三层记忆模型）+ Google Vertex AI Context Caching（Hot/Warm/Cold）+ Cursor Rules（Always-on Context+Token预算）+ Windsurf Rules（Context Freshness Decay）+ RAG 社区（Multi-Query Retrieval+Dedup+Re-rank）。

---

## 1. 概述与模块定位

### 1.1 模块身份

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-008 |
| 代码落位 | `src/zephyr/context_engine/` |
| 边界上下文 | bounded_context: true（独立领域模型）|
| 伞盖层 | l12（可观测层覆盖）|
| 核心职责 | 把知识库里的东西变成 Agent 能用的上下文——不多不少、安全合规 |

### 1.2 核心职能（一句话）

**Context Engine 是"知识库 → Agent 大脑"的翻译桥梁**——从 VMS 检索相关知识 → 压缩到 Token 预算内 → 安全检查 → 注入到 Agent session。

大白话：知识库存了一堆经验教训（KE），但 Agent 每次干活时不能把所有书都搬出来看——太多了看不过来。CE 就是图书馆的"情报摘要员"——Agent 说"我要修 D6 维度的安全漏洞"，CE 就从图书馆翻出"以前修 D6 的经验+相关规则+相关蓝图"，压缩成 8000 字的精简版，检查没有有害内容，然后递给 Agent。

### 1.3 责任边界

| 管什么 | 不管什么（→ 去哪） |
|------|------|
| build: 从 VMS 检索相关知识 | VMS 的 Collection 管理 → VMS 蓝图 (MOD-INF-011) |
| compress: Token 预算内压缩 | Token 的计算方式 → LLM provider SDK |
| validate: LSG 安全校验 | LSG 的安全规则 → LSG 蓝图 (MOD-INF-014) |
| inject: 注入 Agent session | Agent session 的管理 → Orchestrator (MOD-INF-006) |

---

## 2. 四阶段流水线

```
┌──────────┐    ┌───────────┐    ┌───────────┐    ┌──────────┐
│  BUILD   │ →  │ COMPRESS  │ →  │ VALIDATE  │ →  │ INJECT   │
│  检索    │    │   压缩    │    │  安全校验  │    │   注入   │
└──────────┘    └───────────┘    └───────────┘    └──────────┘
     ↑                                                  ↓
  VMS 4C                                           Agent Session
  (ke_entries,                                     (Orchestrator)
   vibe_rules,
   blueprints,
   failure_patterns)
```

### 2.1 Build（检索）— context_assembler.py

```python
def build_context(task: TaskCard) -> RawContext:
    ke_list = VMS.search("ke_entries", task.embedding, top_k=5)
    rules = VMS.search("vibe_rules", task_type_match, top_k=3)
    blueprints = VMS.search("blueprints", layer_match, top_k=2)
    failures = VMS.search("failure_patterns", task_type_match, top_k=3)
    return RawContext(ke_list, rules, blueprints, failures)
```

| Collection | 检索条件 | top_k | 用途 |
|------|------|:---:|------|
| ke_entries | task_type + target_layer 语义相似 | 5 | 历史经验 |
| vibe_rules | task_type 相关治理规则 | 3 | 合规约束 |
| blueprints | target_layer 相关蓝图 | 2 | 架构参考 |
| failure_patterns | task_type 历史失败模式 | 3 | 避坑指南 |

### 2.2 Compress（压缩）— doc_compressor.py + context_budget_tracker.py

```
压缩策略（三级回退）：
  Level 1: Qwen2.5-3B 本地摘要模型 → 语义压缩
  Level 2: 规则基摘要 → 关键段落提取
  Level 3: 截断 → 超出预算直接截断
```

Token 预算分配：
| 类型 | Token 预算 | 优先级 |
|------|:---:|:---:|
| KE 条目 | 0-3000 | 最高 |
| 规则/策略 | 0-2000 | 高 |
| 蓝图 | 0-2000 | 中 |
| 运行时日志 | 0-1000 | 低 |
| **总计** | **8000** | — |

### 2.3 Validate（安全校验）— prompt_registry.py + pattern_library.py

CE 通过 CT-CE-LSG-001 契约调用 LSG 进行安全校验：
- 检查注入内容是否含恶意指令（prompt injection）
- 检查是否含项目敏感信息泄露
- 检查是否含危险工具调用建议

LSG 拒绝的块 → 移除 → 重新 compress → 再送 LSG → 最多 3 次

### 2.4 Inject（注入）— context_injector.py

```python
def inject(session: AgentSession, context: ValidatedContext) -> InjectionResult:
    full_context = format_context(context)
    session.system_prompt += full_context
    return InjectionResult(token_count, sources)
```

---

## 3. 三级降级策略

| 情况 | 降级行为 | 标记 |
|------|------|------|
| **VMS 不可用** | 仅注入 AGENTS.md + 当前模块蓝图 | `session.degraded=true` |
| **LSG 拒绝 ≥3 次** | 移除被拒绝块，注入剩余 | `injection_blocks_removed=N` |
| **CE 10s 超时** | 降级注入—仅硬编码规则 | `CE_timeout_metric += 1` |

---

## 4. 文件组成

| 文件 | 职责 |
|------|------|
| `context_assembler.py` | Build 阶段——从 VMS 拉取原始上下文 |
| `context_budget_tracker.py` | Compress 阶段——Token 预算管理 |
| `doc_compressor.py` | Compress 阶段——三级压缩回退 |
| `context_injector.py` | Inject 阶段——格式化+注入 session |
| `intent_parser.py` | 解析任务意图→决定检索策略 |
| `intent_keyword_mapper.py` | 意图→关键词映射表 |
| `pattern_library.py` | Validate 阶段——已知危险模式库 |
| `prompt_registry.py` | Validate 阶段——注入模板注册 |
| `system_snapshot.py` | 系统状态快照——供上下文参考 |

---

## 5. 核心流程 — 四阶段流水线结构化规则

> 将 §2 的自然语言伪代码升级为确定性 YAML 规则。

### 5.1 Stage 1: Build

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
    fix_hint: "补充 intent→keyword 映射到 intent_keyword_mapper.py"
  - id: BUILD-C02
    name: query_vector_memory
    type: vector_search
    check: "vector_bridge可用 → query 4C (ke_entries×5, failure_patterns×3, blueprints×2, architecture_model×1)"
    severity: error
    on_failure: auto_fix
    fix_hint: "VMS不可用 → 三级降级: embedded_defaults"
```

### 5.2 Stage 2: Compress

```yaml
stage: compress
entry_conditions:
  - id: COMPRESS-C00
    name: check_token_budget
    type: budget
    check: "ContextBudgetTracker.check_budget(session_id) ≤ L1_WARNING"
    severity: warning
    on_failure: auto_fix
    fix_hint: "触发 DocCompressor.compress() → max_chars=4000, preserve_structure=true"
  - id: COMPRESS-C01
    name: doc_compressor_invariants
    type: invariant
    check: >
      CompressionPolicy frozen 5不变量 ALL PASS:
      preserve_structure=true, preserve_provenance=true,
      min_chars≥100, max_chars≤10000, immutable_blocks preserved
    severity: error
    on_failure: reject
    fix_hint: "CompressionInvariantError → 回退降级策略 Phase 2 本地LLM"
```

### 5.3 Stage 3: Validate

```yaml
stage: validate
entry_conditions:
  - id: VALIDATE-C00
    name: lsg_safety_check
    type: security
    check: "context通过 CT-CE-LSG-001 → LSG三层审查全部PASS"
    severity: error
    on_failure: auto_fix
    fix_hint: "LSG拒绝 → 移除违规content → 重新compress → 最多3次"
  - id: VALIDATE-C01
    name: no_hallucinated_sources
    type: integrity
    check: "ALL context.sources 路径在磁盘上存在"
    severity: error
    on_failure: auto_fix
    fix_hint: "移除不存在的source → 重新assemble"
```

### 5.4 Stage 4: Inject

```yaml
stage: inject
entry_conditions:
  - id: INJECT-C00
    name: structured_injection
    type: injection
    check: >
      context分层注入:
      Layer1(system): AGENTS.md core rules → always-on, 不受token预算
      Layer2(rules): CT-*相关合同+blueprints → 按task_type注入
      Layer3(knowledge): KE+failure_patterns → priority排序
      Layer4(examples): 类似任务成功案例 → 仅相似度>0.7注入
    on_failure: flag
  - id: INJECT-C01
    name: verify_injected
    type: verification
    check: "session.system_prompt包含所有4层 AND 总tokens≤session_limit"
    on_failure: auto_fix
    fix_hint: "超出limit → 重新compress → 降低knowledge层top_k"
```

---

## 6. 设计决策集中表

| ID | 决策 | 理由 | 被否决替代方案 | 重评条件 |
|----|------|------|--------------|---------|
| DD1 | **4阶段vs3或5** | Build/Compress/Validate/Inject各有独立失败域和降级 | "3阶段合并Compress+Validate" — Validate需raw_text但Compress会压缩 | — |
| DD2 | **Token预算三级 80%/90%/95%** | 80%预警有余量做最后的compress；90%触发DocCompressor；95%硬截断 | "单阈值一刀切" — 无法区分预警和紧急 | 生产数据后微调 |
| DD3 | **DocCompressor Pydantic frozen不可变策略** | CompressionPolicy加载后不可运行时修改——防止AI在压缩中偷改不变量 | "可变策略" — LSG安全审查依赖不变量 | AI自主修改能力成熟后 |
| DD4 | **intent_parser 10分类** | 覆盖task_type枚举+QUERY/DEBUG辅助模式 | "30+细粒度" — 分类过多→keyword精度下降 | 混淆率>10%时 |
| DD5 | **DocCompressor三级降级** | Phase1规则基, Phase2本地Qwen2.5-3B, Phase3截断——渐进 | "只用LLM压缩" — 延迟不可控+cost高 | 本地LLM质量稳定后 |
| DD6 | **token_budget=8000默认** | 主流模型context window的10-15%——留足空间 | "全量注入不设限" — 挤占模型思考tokens | 模型window变化时 |

---

## 7. Anti-Patterns — AI agent 绝对禁止的上下文操作

> 上下文引擎在vibe coding社区是最容易出事的模块——AI往context里乱塞东西。

| # | Anti-Pattern | 违反后果 | 正确做法 |
|---|-------------|---------|---------|
| AP1 | **无LSG审查直接注入** — CE跳过validate阶段 | 恶意prompt进入LLM上下文——不可逆 | 注入前必经CT-CE-LSG-001三层审查 |
| AP2 | **compress丢弃raw_text** — 只保留压缩文本 | LSG需raw_text做注入检测——缺失→安全失效 | compress永远保留raw_text——压缩+原始同时维护 |
| AP3 | **Flat string concat注入** — 所有上下文粘成字符串 | system/rules/knowledge/examples混一起——LLM无法区分层级 | 结构化分层注入: Layer1→4 |
| AP4 | **重复查VMS** — 同一session反复查同一Collection | Token浪费+VMS性能下降+重复注入 | Cache: 同session_id+同query→缓存(TTL=5min) |
| AP5 | **注入不存在文件路径作source** | LLM尝试读不存在文件→幻觉连锁 | VALIDATE-C01: 注入前验证source路径存在 |
| AP6 | **旧KE与新KE权重相同** | 过时知识主导上下文——压制最新经验 | Freshness Decay: created_at越新→权重越高 |
| AP7 | **Token预算耗尽后强行注入** | 模型context溢出→关键信息截断→任务失败 | L3_HARD_STOP=不追加context, 仅保留Always-on |

---

## 8. 集成契约

| CT-* | 涉及系统 | 方向 | 说明 |
|------|---------|------|------|
| CT-ORC-CE-001 | Orc→CE | → | Orc在任务启动时→CE.build(task_card,session_id) |
| CT-CE-VMS-001 | CE→VMS | → | CE.build()→VMS.search()→4C检索 |
| CT-CE-LSG-001 | CE→LSG | → | CE.validate()→LSG三层审查→PASS/FAIL |

> 详见总蓝图 [MASTER-001](file:///D:/ZephyrAlpha/docs/03_modules/_master-blueprint/blueprint.md) §2.3/§2.6/§2.11。

---

## 9. 风险与缓解

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|:---:|:---:|------|
| R1 | 恶意内容通过CE进入LLM | 中 | 极高 | CT-CE-LSG-001 fail-closed: LSG不可用→拒绝注入 |
| R2 | Token预算耗尽→模型截断 | 中 | 高 | L1→L2→L3渐进+DocCompressor压缩 |
| R3 | 过时KE主导最新经验 | 中 | 高 | Freshness Decay+TTL=90天标记legacy |
| R4 | VMS不可用→上下文空洞 | 低 | 高 | embedded_defaults→硬编码基础上下文 |
| R5 | 3核心文件未实现(vector_bridge等) | 已知 | — | construction_progress=phase_1_partial, Phase2补 |

---

## 10. 施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| Phase 0 | 9 文件骨架 + context_assembler + injector | ✅ implemented |
| Phase 1 | VMS 集成 → 完整的 build→inject 链路 | 📋 Backlog |
| Phase 2 | LSG validate 集成 + 第三级截断降级 | 📋 Backlog |

---

## 11. 施工/演进指南

> CE已有10源文件+7测试+DocCompressor 563行完整实现——本章为修改和演进指南。

### 11.1 添加新intent类型

```
1. intent_parser.py IntentType 枚举中添加
2. intent_keyword_mapper.py _MAP 中添加映射
3. 运行 test_intent_parser.py + test_intent_keyword_mapper.py
```

### 11.2 实现缺失的3个文件 (Phase 2)

```
P1: vector_bridge.py — CE↔VMS检索桥接 (Connect CT-CE-VMS-001)
P2: task_validator.py — 任务告警/故障验证
P3: pipeline_orchestrator.py — 多阶段流水线编排 (已有测试Ghost)
```

### 11.3 修改DocCompressor

```
DocCompressor遵循CL-018 RI扩展模式:
- CompressionPolicy为Immutable Core(Pydantic frozen)→修改需Human-Gated
- compress()实现可AI-Modified→修改后运行test_doc_compressor.py
```

---

## 12. 已实现代码完整路径索引

> **2026-05-04 代码-蓝图对齐审计**：此前9源+7测试+1脚本+3配置全是"✅"，实际仅10源+7测试+2配置存在。本节已按磁盘实际修正。

### 12.1 源文件

| 文件 | 磁盘 | 说明 |
|------|:---:|------|
| `context_assembler.py` | ✅ 292行 | Build阶段——组装上下文 |
| `context_budget_tracker.py` | ✅ 227行 | Token预算三级管理 |
| `context_injector.py` | ✅ 203行 | Inject阶段——知识注入 |
| `doc_compressor.py` | ✅ 563行 | 完整实现——Immutable Core+不变量校验+三级降级 |
| `intent_keyword_mapper.py` | ✅ | intent→keyword映射表 |
| `intent_parser.py` | ✅ | 意图分类NLP |
| `pattern_library.py` | ✅ | pattern模板库 |
| `prompt_registry.py` | ✅ | prompt注册表 |
| `system_snapshot.py` | ✅ | 系统状态快照 |
| `architecture_context.json` | ✅ | 架构上下文数据 |
| `task_validator.py` | ❌ | Phase2待实现 |
| `pipeline_orchestrator.py` | ❌ | Phase2待实现 |
| `vector_bridge.py` | ❌ | Phase2待实现——CE↔VMS桥接 |

### 12.2 测试文件

| 文件 | 磁盘 | 说明 |
|------|:---:|------|
| `test_context_injector.py` | ✅ | ContextInjector单元测试 |
| `test_doc_compressor.py` | ✅ | DocCompressor单元测试 |
| `test_intent_keyword_mapper.py` | ✅ | intent keyword映射测试 |
| `test_intent_parser.py` | ✅ | intent解析测试 |
| `test_pattern_library.py` | ✅ | pattern模板测试 |
| `test_prompt_registry.py` | ✅ | prompt注册表测试 |
| `test_system_snapshot.py` | ✅ | 系统快照测试 |
| `test_pipeline_orchestrator.py` | ⚠️ Ghost | 测试存在但源文件不存在 |

### 12.3 配置文件

| 文件 | 磁盘 | 说明 |
|------|:---:|------|
| `config/context_rules_v1.yaml` | ✅ | 上下文规则配置 |
| `config/compression/policy.yaml` | ✅ | DocCompressor策略 |

### 12.4 统计

| | 源文件 | 测试 | 配置 | 合计 |
|---|---|:---:|:---:|:---:|
| 已实现 | 10 | 7+1 Ghost | 2 | **20** |
| 待实现 | 3 | 0 | 0 | **3** |

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-04 | 0.2.0 | 代码-蓝图对齐审计+黄金标准补齐：(1)construction_progress→phase_1_partial——审计发现3源+5测试+1脚本+3配置多项为蓝图虚构；(2)新增§5 核心流程——四阶段结构化YAML规则；(3)新增§6 设计决策集中表——6条；(4)新增§7 Anti-Patterns——7条上下文专属禁止行为；(5)新增§8 集成契约——CT-ORC-CE/CT-CE-VMS/CT-CE-LSG；(6)新增§9 风险与缓解；(7)新增§11 施工/演进指南；(8)重写§12 实现状态——基于磁盘真实(10源+7测试+Ghost+2配置)；(9)frontmatter新增construction_progress+ai_role_instruction+对标升级。CE从~35/100→~80/100。 |
