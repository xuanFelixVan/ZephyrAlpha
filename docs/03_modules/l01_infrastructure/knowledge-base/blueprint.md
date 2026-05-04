---
module_id: "MOD-KB-001"
title: "知识库系统蓝图"
doc_type: blueprint
status: draft
version: "0.6.5"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: AI-Claude
date: "2026-05-02"
valid_from: "2026-05-02"
ttl: permanent
construction_progress: phase_1_partial
summary: "ZephyrAlpha 知识库系统完整蓝图——覆盖知识全生命周期：入库(G1-G5五门禁+§3.9.1 8条来源矩阵) → 存储(§7三层存储+§7.8灾备) → 出库(§9检索质量度量+混合检索BM25+RRF+查询改写HyDE+上下文动态分配) → 演化(§9 KE版本semver+依赖级联+去重聚类HDBSCAN+效果A/B测试+Self-RAG自反思) → 运维(§9.10 Token预算背压+§9.12三级记忆HotWarmCold+§9.6知识溯源PROV)。ChromaDB 4 Collection向量架构 + SQLite元数据层 + 10状态KE状态机 + 三轨18类知识分类（A1-A8+B1-B7+C1-C3）+ Track D AI-AI协作预留（D1-D3，beta实现）+ KO→KE→KB三级漏斗 + KE Schema字段稳定性三级分级(frozen/extendable/runtime_only) + Human-Gated三层权限模型(§7.7) + KB规则执行引擎(§9.5)。全自动零Owner触发（月均≤12min LLM费用≤¥0.40）。experimental代码已实现(12模块/3600行)，4持续建设。"
tags: [knowledge-base, ke, embedding, vector-db, semantic-search, chromadb, mcp, state-machine, g1-g5, triage, audit-pipeline]
priority: P0
depends_on:
  - {target: "MOD-INF-006", at: "§3.2", why: "TaskCard模型 + task_id格式——知识库施工任务追踪"}
  - {target: "MOD-INF-006", at: "§5.1", why: "context_assembler——知识注入接口"}
  - {target: "MOD-INF-006", at: "§4.2", why: "10状态任务状态机——KB施工任务状态管理"}
  - {target: "MOD-INF-005", at: "§6.3", why: "脚本系统 MEDIUM Finding → KB 入库——知识库的审计数据来源"}
  - {target: "MOD-INF-005", at: "§3.6", why: "标签分类体系——KB 的 tags 字段对齐脚本系统标签"}
  - {target: "PS-STD-001", at: "§3", why: "doc_type受控词表——知识条目doc_type注册"}
  - {target: "PS-STD-004", at: "§5", why: "domain枚举——知识domain分类与仲裁"}
---

# 知识库系统蓝图（MOD-KB-001）

> **module_id**: MOD-KB-001 | **version**: 0.6.5 | **status**: draft
>
> **真源声明**：本蓝图是 ZephyrAlpha 知识库（KB/KMS）系统的唯一真源蓝图。
> 取代了退役的 `task-card-kms/blueprint.md`（MOD-INF-003，retired，内容已并入 MOD-INF-006 任务系统）。
> 候选池中所有知识库相关设计（`03-知识库架构.md`、`知识库升级方案.md`、`vibe-coding-task-card-and-knowledge-base-design.md`、
> `知识库专题讨论文档.md`、D0-knowledge 四轮 prompt 指令等）已全部提取并经质量对比后择优纳入本蓝图。
>
> **对标**：ITIL Knowledge Management（DIKW 金字塔：Data→Information→Knowledge→Wisdom）、
> ChromaDB 嵌入式向量数据库官方最佳实践、MCP（Model Context Protocol）2024-11-05 规范、
> Anthropic CLAUDE.md AI 可消费文档标准、Validator-N 四模型审计流水线。

---

## §1 概述与模块定位

### 1.1 模块标识

| 属性 | 值 |
|------|-----|
| module_id | MOD-KB-001 |
| 架构层 | cross_layer（跨层基础设施——B-Track） |
| 代码落位 | `src/zephyr/kb/` |
| 知识数据落位 | `docs/08_knowledge/` |
| 运行时平面对标 | Warm memory（温记忆——任务触发时加载 ≤8000 tokens） |

### 1.2 核心职能（一句话）

**让 AI Agent 能"记住做过什么、自动检索相关知识、在合适时机注入上下文"**——把每次 Vibe Coding session 从"零记忆新员工"升级为"带着项目全量经验上岗的老员工"。

大白话：AI 每次干活都是从头开始，不知道这个项目以前做过什么决策、踩过什么坑。知识库就是 AI 的"外置大脑"——干活前先查一下"以前这事怎么干的"，干完后把经验存起来"下次别踩同一个坑"。

### 1.3 责任范围（管什么）

| 职责 | 内容 |
|------|------|
| **知识全生命周期** | 采集(G1)→分拣(G2)→分析(G3)→激活(G4)→提取(G5) 五门禁流水线 |
| **知识条目管理** | KE 的创建、状态流转（10状态机）、版本管理、过期检测 |
| **向量语义检索** | ChromaDB 4 Collection：ke_entries / vibe_rules / blueprints / failure_patterns |
| **跨Agent知识互通** | MCP 协议：4 Resource + 4 Tool，多模型（Claude/Kimi/Qwen/GLM）共享知识 |
| **审计与质量保障** | 四模型审计流水线（GLM扫描→Kimi根因→Qwen落地→Opus终审）+ 知识衰减/新鲜度管理 |
| **上下文注入** | 与 MOD-INF-006 `context_assembler` 对接，AI session 启动时自动注入相关KE |

### 1.4 责任边界（不管什么——去哪找）

| 不管的内容 | 正确位置 |
|-----------|---------|
| 任务系统的 TaskCard 状态机和任务生命周期 | MOD-INF-006（任务系统蓝图） |
| 上下文引擎的 Token 预算追踪和注入策略 | `context_engine/` 模块（ADR-0015） |
| VMS（Vector Memory Service）的 `InProcessVectorMemory` | `src/zephyr/vector_memory/`（beta 目标，当前空包） |
| Session Log 的结构和交接协议 | `_registry/schemas/session-log-schema.yaml` |
| 蓝图的结构注册和治理 | 各模块 `blueprint.md`（本蓝图只管理知识库自身的蓝图） |
| **脚本系统的 12 维度审计结果**（MEDIUM Finding → KB 入库） | **MOD-INF-005 §6.3 + §6.6**（脚本系统蓝图——C4→G1 数据流） |
| **脚本系统的审计执行**（C1-C5 流水线运行逻辑） | **MOD-INF-005**（脚本系统蓝图——KB 只消费审计结果，不执行审计） |

### 1.5 与兄弟模块的关系

```
[上下文引擎 (CE)]          [任务系统 (MOD-INF-006)]       [脚本系统 (MOD-INF-005)]
       │                           │                           │
       │ context_assembler          │ TaskCard 追踪KB施工        │ C4: MEDIUM Finding→KB
       │ 拉取KE注入上下文            │ task_id: KB-INF-NNNN       │ C5: 知识沉淀→G3
       ▼                           ▼                           ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │                      知识库 (MOD-KB-001)                          │
  │                                                                   │
  │  G1 Ingest → G2 Triage → G3 Analyze                              │
  │  → G4 Activate → G5 Extract                                       │
  │                                                                   │
  │  ChromaDB 4C + SQLite + MCP                                      │
  └──────────────┬──────────────────┬────────────────────────────────┘
                 │                  │
    ┌────────────┼──────────────────┼────────────┐
    ▼            ▼                  ▼            ▼
[VMS Phase3] [MCP Server] [Audit Pipeline] [→C1 扫描规则升级]
```

大白话：知识库夹在"上下文引擎"和"任务系统"之间。上下文引擎干活前找知识库要"相关资料"注入给 AI；任务系统追踪"知识库本身还有哪些施工任务没完成"。知识库自己的施工也用任务系统的 TaskCard 来追踪。

---

## §2 必备链接 + 依赖声明

### 2.1 必读文档（新 AI session 接手 KB 模块时按此顺序）

| # | 文件 | 说明 |
|---|------|------|
| 1 | 本文件 `knowledge-base/blueprint.md` | KB 系统唯一真源蓝图 |
| 2 | `src/zephyr/kb/kb_repo.py` | 核心仓储——10状态机 + SQLite + ChromaDB |
| 3 | `src/zephyr/kb/unified_memory_api.py` | RI-02 统一内存 API——remember/learn/forget/recall |
| 4 | `src/zephyr/kb/chromadb_init.py` | ChromaDB 4 Collection 初始化 |
| 5 | `architecture-model/layers/b_kb.yaml` | 架构 YAML SSoT——KB 模块登记 |
| 6 | MOD-INF-006 `task-system/blueprint.md` | 任务系统——KB 施工任务追踪格式 |

### 2.2 关键路径速查

| 内容 | 绝对路径 |
|------|---------|
| KB 代码 | `D:\ZephyrAlpha\src\zephyr\kb\` |
| 知识数据 | `D:\ZephyrAlpha\docs\08_knowledge\` |
| 架构 YAML SSoT | `D:\ZephyrAlpha\architecture-model\layers\b_kb.yaml` |
| 任务系统蓝图 | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md` |
| 上下文引擎 ADR | `D:\ZephyrAlpha\docs\02_enterprise_architecture\adr\adr-0015-context-engine-architecture.md` |
| VMS ADR | `D:\ZephyrAlpha\docs\02_enterprise_architecture\adr\adr-0016-vector-memory-chromadb-bge-m3.md` |
| ChromaDB ADR | `D:\ZephyrAlpha\docs\02_enterprise_architecture\adr\adr-0031-chromadb-vector-retrieval.md` |
| Session Log | `D:\ZephyrAlpha\docs\19_development_workspace\session-logs\` |

### 2.3 depends_on 声明

本蓝图（MOD-KB-001）作为知识库模块的蓝图，**直接依赖**以下模块/标准的设计契约：

| 依赖目标 | 引用位置 | 为什么依赖 | 耦合程度 |
|---------|---------|-----------|:---:|
| MOD-INF-006 | §3.2 + §4.2 | TaskCard 模型 + task_id 格式（`{NAMESPACE}-{SEQ}`）——KB 自己的施工任务用 TaskCard 追踪 | 强 |
| MOD-INF-006 | §5.1 | `context_assembler` 的 KE 知识注入接口——上下文引擎通过此接口拉取 KB 知识 | 强 |
| MOD-INF-006 | §4.2 | 10 状态任务状态机——KB 施工任务状态管理引用此状态机 | 中 |
| MOD-INF-005 | §6.3 + §6.6 | 脚本系统 MEDIUM Finding → KB 入库（C4→G1）——Finding→KE 数据格式转换 | 强 |
| MOD-INF-005 | §3.6 | 脚本系统标签体系（`[Quick]`/`[Security]` 等）——KB 的 tags 字段对齐脚本系统标签 | 中 |
| PS-STD-001 | §3 | doc_type 受控词表——知识条目的 doc_type 注册 | 中 |
| PS-STD-004 | §5 | domain 枚举——知识 domain 分类与冲突仲裁 | 弱 |
| ADR-0016 | 全文 | ChromaDB + BGE-M3 向量存储技术选型 | 中 |
| ADR-0031 | 全文 | ChromaDB 向量检索方案细节 | 中 |

> **耦合说明**：KB 系统是一个"基础设施模块"——它**服务**于任务系统（追踪施工）、上下文引擎（注入知识）、审计系统（记录决策）。
> KB 出问题会**连锁影响**这三个上游消费者。因此 depends_on 强耦合 = KB 变更时必须通知对方。
> 大白话：知识库不是孤岛——任务系统靠它追踪进度，上下文引擎靠它喂资料给 AI，审计系统靠它留证据。改了知识库的结构，这三个兄弟都得知道。

---

## §3 数据模型

### 3.1 概述

知识库的数据模型分三层：

```
┌──────────────────────────────────────────────┐
│  应用层（KnowledgeChunk Schema）              │
│  - KE ID、标题、正文、分类、标签、来源         │
│  - 状态（10状态机）、质量评分、TTL             │
├──────────────────────────────────────────────┤
│  索引层（ChromaDB + SQLite）                  │
│  - 4 Collection：ke_entries/vibe_rules/       │
│    blueprints/failure_patterns                │
│  - SQLite metadata：kb_state/kb_state_log/    │
│    knowledge_entries                          │
├──────────────────────────────────────────────┤
│  存储层（File System）                        │
│  - docs/08_knowledge/ 下的 Markdown KE 文件   │
│  - ChromaDB 持久化目录                         │
└──────────────────────────────────────────────┘
```

### 3.2 知识条目（KE — Knowledge Entry）Schema

每个知识条目对应一条可被语义检索的知识。核心字段：

| 字段 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| `ke_id` | str | ✅ | 全局唯一标识，格式 `KE-{NNN}`（3位递增编号），代码真源在 `kb_repo.py` |
| `title` | str (≤100) | ✅ | 知识标题 |
| `body` | str | ✅ | 知识正文（Markdown 格式） |
| `category` | enum | ✅ | 知识分类：15 类双轨体系（§3.8）。**beta 迁移**（KB-INF-0022）：当前仍沿用旧 10 类枚举→逐步迁移至 Track A（8类）+ Track B（7类） |
| `domain` | enum | ✅ | 业务域：10域枚举（对齐 PS-STD-004 §5） |
| `layer` | enum | ✅ | 架构层：14层枚举（对齐 `triage.py` VALID_LAYERS） |
| `source_type` | enum | ✅ | 来源类型：`adr` / `blueprint` / `session_log` / `candidate_pool` / `external_paper` / `github_repo` |
| `source_path` | str | ✅ | 来源文件绝对路径 |
| `status` | enum | ✅ | KE 状态：10状态机（§3.3） |
| `quality_score` | float [0.0-1.0] | ✅ | 质量评分（G2 Triage 产出） |
| `priority` | enum | ✅ | 优先级：`P0`~`P3` |
| `tags` | list[str] | ✅ | 标签列表（对齐 MOD-INF-006 5轴标签：fn/ly/md/st/mo） |
| `audit_chain` | list[str] | ✅ | 审计链：记录经过的审计模型和结论 |
| `ttl` | str | ✅ | 有效期：`permanent` / `30d` / `7d` / `session` |
| `half_life_days` | int | SHOULD | 知识半衰期（天），用于衰减计算。0=永不过期 |
| `created_at` | datetime | ✅ | 创建时间 |
| `updated_at` | datetime | ✅ | 最后更新时间 |
| `last_verified_at` | datetime | SHOULD | 最后验证时间 |
| `usage_count` | int | ✅ | 被 `recall()` 检索到的次数。默认 0 |
| `adoption_count` | int | ✅ | 被检索后 AI 实际采纳的次数。由 `learn(event_type="ke_adopted")` 递增。默认 0 |
| `helpfulness_score` | float [0.0-1.0] | ✅ | 采纳后任务成功率（滑动窗口最近 10 次）。默认 0.5 |
| `last_used_at` | datetime | SHOULD | AI 最后一次检索/使用此 KE 的时间 |
| `depends_on_ke` | list[str] | SHOULD | 依赖的其他 KE-ID |
| `supersedes_ke` | list[str] | SHOULD | 取代的旧 KE-ID |
| `_locked` | bool | ✅ | 锁定状态（true=不可修改，需走决策记录解锁） |
| `valid_from` | date | OPTIONAL | 知识生效起始日期（Track B 金融KE专用——如"Q1 财报季策略"仅在 01-01~03-31 有效） |
| `valid_until` | date | OPTIONAL | 知识失效日期（到期后自动 DEPRECATED，检索时过滤掉已过期的 KE） |

**字段稳定性分级**（对标 CTR-001~CTR-006 `stability: locked-5yr`）：

KE Schema 的 28 个字段同样需要稳定性承诺——beta/3 代码会依赖这些字段名和类型，随意变更会破坏下游消费者。

| 分级 | 字段 | 含义 | 变更规则 |
|:---:|------|------|---------|
| **frozen** | `ke_id` `category` `domain` `layer` `source_type` `status` `priority` `quality_score` `ttl` `created_at` `_locked` | 核心契约字段——代码强依赖其类型和枚举值 | 3年内不删不改类型。允许追加新枚举值但禁止删除旧值 |
| **extendable** | `title` `body` `source_path` `tags` `audit_chain` `depends_on_ke` `supersedes_ke` `updated_at` `last_verified_at` | 可扩展字段——内容可迭代但结构稳定 | 可追加子字段，不可删除已有子字段，类型变更需3个版本过渡期 |
| **runtime_only** | `usage_count` `adoption_count` `helpfulness_score` `last_used_at` `half_life_days` | 运行时统计字段——仅存在于 SQLite，不写入 MD frontmatter | 自由变更——仅影响 SQLite schema migration，不影响 MD 格式 |

> **对标**：CTR-001~CTR-006 `frozen: true` + `stability: locked-5yr` / PostgreSQL pg_catalog 字段稳定性——`pg_class.relname` 自从 1996 年未改类型 / Kubernetes API versioning——`v1` 字段 deprecated 但不删除，至少保留 3 个 minor 版本。
> **大白话**：以前 KE Schema 的字段可以随便改——蓝图版本升级的时候想删哪个字段就删哪个。现在分三级：frozen 字段是承重墙——动了代码就塌；extendable 字段是隔断墙——可以改但得走流程；runtime_only 是家具——随便摆。

#### 3.2.1 KE ID 格式裁决

> **历史冲突**：代码 `kb_repo.py` 使用 `KE-{NNN}`（3位数字），早期 schema 草案用 `KMS-{YYYYMMDD}-{SEQ}`。经 `知识库专题讨论文档.md` §KB-024 裁定：

- **最终格式**：`KE-{NNN}`（NNN = 3位递增编号，如 KE-001、KE-042）
- **裁决理由**：简短+机器可消费+与 `KMS-` 前缀冲突时已代码实现的事实为准（代码 = 最终仲裁者）
- **与 task_id 格式的关系**：KE ID ≠ task_id。KE 有独立的 `KE-{NNN}` 格式；KB 施工任务用 MOD-INF-006 的 `{NAMESPACE}-{SEQ}` 格式（如 `KB-INF-0001`）。

#### 3.2.2 KE 物理存储格式（Markdown）

每条 KE 的 canonical 物理形态是一个独立的 `.md` 文件，存储在 `docs/08_knowledge/` 下。格式包含两个区：

1. **YAML frontmatter**（机器可消费元数据 + 人类随手可看）——从 §3.2 的 28 字段 Schema 中选取"文件级必读"字段
2. **Markdown body**（知识正文）——结构化段落模板

##### 两区字段分工

| 字段 | 落位 | 理由 |
|------|:---:|------|
| `ke_id` | frontmatter | 文件级标识——AI 扫一眼 frontmatter 就知道这是哪条 KE |
| `title` | frontmatter | 标题——人类/AI 快速判断"这条知识讲什么" |
| `body` | **body** | 知识正文——Markdown 正文区，结构化段落 |
| `category` | frontmatter | 15 类双轨分类（§3.8） |
| `domain` | frontmatter | 业务域（对齐 PS-STD-004 §5） |
| `layer` | frontmatter | 架构层（对齐 `triage.py` VALID_LAYERS） |
| `source_type` | frontmatter | 来源类型——可追溯 |
| `source_path` | frontmatter | 来源文件绝对路径——可审计 |
| `status` | frontmatter | 10 状态机当前状态（§3.3） |
| `quality_score` | frontmatter | G2 Triage 质量评分 |
| `priority` | frontmatter | P0~P3 优先级 |
| `tags` | frontmatter | 标签列表（YAML list） |
| `ttl` | frontmatter | 有效期 |
| `half_life_days` | frontmatter | 半衰期（天）——0=永不过期 |
| `created_at` | frontmatter | 创建时间（ISO 8601） |
| `updated_at` | frontmatter | 最后更新时间 |
| `last_verified_at` | frontmatter | 最后验证时间 |
| `depends_on_ke` | frontmatter | 依赖的其他 KE-ID |
| `supersedes_ke` | frontmatter | 取代的旧 KE-ID |
| `usage_count` | **SQLite only** | 运行时计数器——由 `recall()` 实时更新，不在文件中 |
| `adoption_count` | **SQLite only** | 运行时计数器——由 `learn()` 实时更新，不在文件中 |
| `helpfulness_score` | **SQLite only** | 运行时滑动窗口（最近 10 次）——不在文件中 |
| `last_used_at` | **SQLite only** | 运行时时间戳 |
| `_locked` | **SQLite only** | 内部锁标记——禁止暴露给文件层 |

> **设计原则（对标 §6.12 AI-First Audience Principle）**：frontmatter 选择的边界是"这条字段离开这个文件之后还有没有独立价值？"——有 → 放 frontmatter（如 category、source_path）；没有（如 usage_count 是运行时计数器）→ 放 SQLite only。禁止把运行时字段写进文件——下次 `parse_frontmatter` 会读到过期数据。

##### 完整文件模板

```yaml
---
# ═══════════════════════════════════════
# ZephyrAlpha Knowledge Entry (KE)
# 格式版本：v1.0.0 | 编码：UTF-8 LF
# ═══════════════════════════════════════

ke_id: "KE-042"
title: "ruff 选 pylint：快 10-100x + pyproject.toml 原生集成"

category: "tool_configuration"
domain: "infra"
layer: "L01"

source_type: "session_log"
source_path: "docs/19_development_workspace/session-logs/session-047.md"

status: "VERIFIED"
quality_score: 0.92
priority: "P1"

tags:
  - "fn:tool-chain"
  - "ly:L01"
  - "md:design"
  - "st:build-ready"
  - "mo:active"

ttl: "permanent"
half_life_days: 180

created_at: "2026-05-02T14:30:00+08:00"
updated_at: "2026-05-03T09:15:00+08:00"
last_verified_at: "2026-05-03T09:15:00+08:00"

depends_on_ke: ["KE-041"]
supersedes_ke: []

# ═══════════════════════════════════════
# 运行时字段（不在文件中，SQLite only）：
#   usage_count, adoption_count,
#   helpfulness_score, last_used_at, _locked

---

# KE-042：ruff 选 pylint——快 10-100x + pyproject.toml 原生集成

> **状态**：VERIFIED | **分类**：tool_configuration (A5) | **优先级**：P1

## 1. 核心结论（一句话）

ZephyrAlpha 项目选择 **ruff** 而非 pylint 作为 Python linter，基于三大理由：
ruff 快 10-100x、pyproject.toml 原生集成、同时覆盖 pylint + flake8 + isort 职责。

## 2. 决策背景

| 维度 | ruff | pylint | 裁决 |
|------|:---:|:---:|------|
| 速度 | ~5ms/文件（Rust） | ~500ms/文件（Python） | ruff ✅ |
| 配置格式 | pyproject.toml（原生） | .pylintrc（独立文件） | ruff ✅ |
| 功能覆盖 | linter + formatter + import sort | linter only | ruff ✅ |

## 3. 实施方式

```toml
# pyproject.toml
[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]
```

## 4. 反模式（不要做的事）

- ❌ 不要同时启用 ruff 和 pylint——冲突诊断成本 > 收益
- ❌ 不要在 ruff 规则中手动复刻 pylint 的 R 系列（refactor）

## 5. 关联知识

- 依赖 [KE-041](KE-041.md)：pre-commit hooks 选型
- 驱动决策：ADR-0020 编码工具链标准化

---
*格式 v1.0.0 | 由 G5 extract.py 自动生成 | via Session Log handoff-047*
```

##### 格式规则（G1 Ingest 校验项）

| # | 规则 | 校验方式 | 失败后果 |
|:--:|------|---------|---------|
| F-01 | 文件以 `---\n` 开头（frontmatter 起止符） | G1 Ingest 逐行校验 | REJECTED |
| F-02 | 所有 frontmatter 必填字段存在且非空 | `parse_frontmatter()` → 比对必填清单 | SUBMITTED |
| F-03 | `ke_id` 格式 = `KE-\d{3}`（3位数字） | 正则匹配 | 阻断 |
| F-04 | body 首行 = `# KE-{NNN}：{title}` | 正则匹配 | 阻断 |
| F-05 | body 含 `## 1. 核心结论（一句话）` | 字符串包含 | 警告 |
| F-06 | frontmatter 不含运行时字段（usage_count/adoption_count/helpfulness_score/last_used_at/_locked） | AST 逐字段检查 | 阻断 |

> **格式为什么是 YAML frontmatter + Markdown body 而非纯 JSON/YAML/纯 prose**：
> - frontmatter = 机器可精确解析（结构化字段）→ 对应 §6.12 AI-First 原则维度 1（机器可解析 > 自然阅读）
> - Markdown body = AI 零歧义消费 + 人类随手可读 → 一源双态：对 AI 是向量源数据，对 Owner 是可读知识卡片
> - 对标：GitHub Flavored Markdown（YAML frontmatter 事实标准）+ Obsidian（Markdown-first PKM）+ Anthropic CLAUDE.md（YAML frontmatter 元数据）

> **大白话**：每条 KE 就是一个 `.md` 文件——顶上用 YAML 格式写"身份证信息"（编号、分类、分数、谁生成的），下面用 Markdown 写"正文"（结论、论证、反模式）。这样 AI 读到文件时，frontmatter 告诉它"这个文件的基本信息是什么"（机器快读），body 告诉它"这条知识具体讲了什么"（语义消费）。只有运行时 counter（被用了多少次、采纳率多少）存在 SQLite 里不在文件中——那些数字每秒都在变，写进文件反而会过期。

### 3.3 KE 状态机（10 状态）

> **来源**：`03-知识库架构.md` §4 + `kb_repo.py` 代码实现。
> **对标**：ITIL Knowledge Management — 知识从 Draft 到 Verified 的正式流转需要审批门控。

```
DRAFT → SUBMITTED → REVIEWED → ACCEPTED → INDEXED → VERIFIED
  │        │           │          │          │          │
  │        │           │          │          │          ├─→ REJECTED (终态)
  │        │           │          │          │          │
  │        │           │          │          │          ├─→ DEPRECATED
  │        │           │          │          │          │      │
  │        │           │          │          │          │      └─→ ARCHIVED (终态)
  │        │           │          │          │          │
  │        │           │          │          │          └─→ SUPERSEDED
  └────────┴───────────┴──────────┘          │                 │
      (任意非终态可直接取消)                   │            (终态，被新版取代)
                                              │
```

**10 状态定义与流转规则**：

| # | 状态 | 英文 | 含义 | 进入条件 | 可流转至 |
|:--:|------|------|------|---------|---------|
| 0 | 草稿 | DRAFT | KE 刚创建，内容待完善 | 创建时默认 | SUBMITTED, REJECTED |
| 1 | 已提交 | SUBMITTED | KE 已提交，等待审核 | G1 Ingest 通过 | REVIEWED, REJECTED |
| 2 | 已审核 | REVIEWED | KE 经人类/AI 审核，内容准确 | G2 Triage 通过 | ACCEPTED, REJECTED |
| 3 | 已接受 | ACCEPTED | KE 被接受，等待入库 | 人工/AI 确认 | INDEXED, REJECTED |
| 4 | 已索引 | INDEXED | KE 已写入 ChromaDB + SQLite 索引 | G3 Analyze 通过 | VERIFIED, REJECTED |
| 5 | 已验证 | VERIFIED | KE 经四轮审计确认无误 | G4 Activate 通过 | DEPRECATED, SUPERSEDED |
| 6 | 已拒绝 | REJECTED | KE 被拒绝入库 | 任意审核门禁失败 | —（终态） |
| 7 | 已废弃 | DEPRECATED | KE 内容过时/不再适用 | half_life 到期 or 人工标记 | ARCHIVED |
| 8 | 已归档 | ARCHIVED | KE 物理归档 | DEPRECATED 确认后 30d | —（终态） |
| 9 | 已取代 | SUPERSEDED | KE 被新版 KE 取代 | `supersedes_ke` 引用 | —（终态） |

**终态**：REJECTED（拒绝）、ARCHIVED（归档）、SUPERSEDED（被取代）

> **大白话**：一条知识从"有人提了个想法"（DRAFT）→"整理好提交审核"（SUBMITTED）→"检查过没问题"（REVIEWED）→"批准入库"（ACCEPTED）→"写入数据库可检索"（INDEXED）→"经过四轮 AI 交叉审计确认无误"（VERIFIED）。中间任何一步被发现问题就进入 REJECTED（拒绝）。知识过时了就 DEPRECATED→ARCHIVED（归档）。

### 3.4 KE 索引结构

KE 支持三种检索方式：

| 检索方式 | 存储层 | 适用场景 |
|---------|--------|---------|
| **向量语义检索**（主） | ChromaDB `ke_entries` Collection | "找一个关于任务分解最佳实践的知识" |
| **标签精确匹配** | SQLite `knowledge_entries.tags` JSON | "所有 domain=infra AND layer=L01 的知识" |
| **全文关键词搜索** | SQLite FTS5 全文索引 | "正文中包含 'ChromaDB' 的知识" |

检索优先级：向量语义（Top-K） → 标签过滤（缩小范围） → 全文搜索（兜底）

### 3.5 知识衰减模型

每个 KE 有一个 `half_life_days`（半衰期），用于计算知识"新鲜度"：

```
freshness = 0.5 ^ (days_since_verified / half_life_days)
```

| 分类 | 默认半衰期 | 说明 |
|------|-----------|------|
| `blueprint_decision` | 180d | 蓝图决策相对稳定 |
| `best_practice` | 90d | 最佳实践随工具链演进 |
| `factor` | 365d | 量化因子知识长期有效 |
| `failure_pattern` | 永久 | 失败模式不会过时（只会被覆盖） |
| `guardrail` | 60d | 护栏规则需跟随代码变更 |

> **大白话**：知识不是"存进去就永远正确"的。一条"用 ruff 而不用 pylint"的最佳实践，等半年后可能就不对了（如果 ruff 出现重大问题）。半衰期机制让 AI 知道"这条知识已经老了，引用时需要标注'请验证当前是否仍然适用'"。

### 3.6 KO→KE→KB 三级知识漏斗

**问题**：Session Log 里 AI 说"我今天发现 ruff check 报 E501..."——这是一条原始观察（KO）。不该直接进入知识库——需要先结构化，再提炼，最终形成可复用的规则。

**对标 ITIL DIKW 金字塔的量化投射**：

```
DIKW 金字塔                ZephyrAlpha 三级漏斗           数量约束
──────────                ──────────────────           ────────
Wisdom  (智慧)           →  KB  (Knowledge Base)       ≤ 10 条
                            系统级规则——跨模块生效、
                            写入 JUSTFILE / AGENTS.md
                              "本项目永远用 ruff 不用 pylint，用 mypy 不用 pyright"

Knowledge (知识)         →  KE  (Knowledge Entry)      ≤ 30 条
                            结构化知识条目——标注了
                            分类/领域/层/标签/半衰期
                              "ruff 选型理由：比 pylint 快 10-100x + pyproject.toml 原生集成"

Information (信息)       →  KO  (Knowledge Observation) ≤ 50 条
                            从 Session Log / ADR 提取的
                            原始观察——未经结构化的第一手记录
                              "Session 2026-05-02：ruff E501 错误手动 fix 耗时 2 分钟"
```

**漏斗流转规则**：

```
KO (50条上限)                     KE (30条上限)                  KB (10条上限)
───────────                      ───────────                    ──────────
创建条件：G5 Extract              升格条件：≥3个 KO              升格条件：≥5个 KE
         从SessionLog/ADR/BP               指向同一主题的                或者Owner主动
         中自动识别知识块                    KO被人工/AI聚合              声明升格
         │                                │                           │
         │ 同类KO聚合                     │ 提炼为可复用规则            │
         ├────────────────→               ├──────────────→            │
         │   ≥3条 → 升格                  │    ≥5条 → 升格             │
         │                                │                           │
         ▼                                ▼                           ▼
    标记 KO-{NNN}                     标记 KE-{NNN}               标记 KB-{NNN}
    状态：DRAFT→REVIEWED              状态：INDEXED→VERIFIED      状态：ACTIVE
    存储：08_knowledge/drafts/         存储：08_knowledge/分类      存储：AGENTS.md /
    TTL：30d（过期自动清理）             + ChromaDB + SQLite            justfile /
                                        TTL：permanent                .cursor/rules/
                                                                      TTL：permanent
```

**升格阀值**：
- KO→KE：≥3 条 KO 指向同一主题（由向量聚类检测）→ 触发 D0 四轮知识管理流水线（011 GLM→022 Kimi→033 Qwen→044 Opus）自动聚合为 KE
- KE→KB：≥5 条 KE 在同一领域（`category` + `domain` + `layer` 交叉匹配）→ 触发 KB 升格评审（Owner 审批）

**淘汰规则**：
- KO：30 天内未升格为 KE → 自动清理（不是所有观察都值得保留）
- KE：升格为 KB 后 → SUPERSEDED（终态）
- KB：永不过期，但可被新版 KB 取代（SUPERSEDED）

> **对标**：ITIL Knowledge Management — DIKW 金字塔（Data→Information→Knowledge→Wisdom）要求每一层的升格有明确的阀值和流程。KO→KE→KB 是对 DIKW 的量化投射——从"模糊观察"到"可执行规则"的渐进化。
> 大白话：一条知识从"AI 随口说了一句"到"写入项目强制规则"要过三道门槛。第一道（KO）：记下来，"我在 Session #12 发现 ruff 很快"。第二道（KE）：整理好，"ruff 比 pylint 快 10-100 倍，所以选 ruff"。第三道（KB）：写入铁律，"本项目只用 ruff，不准用 pylint"。大多数 KO 熬不到 KE，大多数 KE 熬不到 KB——漏斗的作用就是筛掉噪音，只留下最有价值的东西。

### 3.7 KE 运行时反馈字段

**问题**：当前 `quality_score` 只在入库时计算一次（G2 Triage），之后永远不变。但实际上——一条 KE 被 AI 检索了 100 次但从未采纳 = 质量可能有问题；一条 KE 被检索 3 次但 3 次都采纳了 = 高质量。

**新增 Schema 字段**（追加到 §3.2 KE Schema）：

| 字段 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| `usage_count` | int | ✅ | 被 `recall()` 检索到的次数。默认 0 |
| `adoption_count` | int | ✅ | 被检索后 AI 实际采纳的次数。由 `learn(event_type="ke_used", adopted=True)` 递增。默认 0 |
| `helpfulness_score` | float [0.0-1.0] | ✅ | 采纳后任务成功率（滑动窗口最近 10 次）。由 `learn(event_type="task_outcome")` 更新。默认 0.5 |
| `last_used_at` | datetime | SHOULD | AI 最后一次检索/使用此 KE 的时间 |

**动态质量评分**（取代纯静态评分）：

```python
quality_score = (
    quality_score_static * 0.4    # 入库时 G2 Triage 评分
    + adoption_rate     * 0.3    # 采纳次数 / usage_count（usage_count=0 → 此项=0）
    + helpfulness_score * 0.2   # 任务成功率
    + freshness         * 0.1    # 半衰期的新鲜度
)
```

**反馈事件类型**（通过 `unified_memory_api.learn()` 记录）：

| event_type | 触发时机 | 记录内容 |
|-----------|---------|---------|
| `ke_retrieved` | `recall()` 返回 KE 列表时 | `ke_id` + `query` |
| `ke_adopted` | AI 明确说"根据 KE-042 的建议..." | `ke_id` + `adopted=True` |
| `ke_ignored` | KE 被检索到但 AI 未引用 | `ke_id` + `adopted=False` |
| `task_outcome` | 任务完成时 | `ke_id`（哪些 KE 被采纳） + `success`（bool） + `session_id` |
| `ke_contradiction` | 矛盾检测发现冲突 | `ke_id_a` + `ke_id_b` + `conflict_description` |

> **对标**：Horthy Harness Engineering——反馈闭环是四大支柱之一（"每次注入的知识必须追踪采纳率和效果"）+ Google Vertex AI——RAG 评估有 `answer_relevance` + `faithfulness` + `context_recall` 三维指标。
> 大白话：现在知识存进去后跟石沉大海一样——不知道 AI 到底用没用、用了有没有用。加了这四个字段，知识从"入库时猜质量"变成"运行时验证质量"。就像餐厅——不仅做出菜（G2），还要看客人吃没吃（`adoption_count`）、好不好吃（`helpfulness_score`）。

### 3.8 三轨 18 类知识分类体系

**问题**：当前 `KeCategory` 枚举（`schemas.py` L130-142）定义了 10 个 category——其中 6 个是金融域（`strategy` / `factor` / `risk_control` / `data_governance` / `compliance` / `operations`），为量化金融系统设计的。但当前 KB 实际存储的全是**项目施工知识**（ruff 选型、AGENTS.md 规则、Session Log 教训）——分类体系和实际内容严重不匹配。

**对标**：

| 来源 | 知识分类维度 | 关键发现 |
|------|-------------|---------|
| **Vasilopoulos Codified Context**（283 sessions 实证数据） | 65% 领域知识 / 35% 行为指令 | `codebase_facts`(35%) / `domain_formulas`(20%) / `failure_modes`(15%) / `coding_conventions`(15%) / `tool_config`(10%) / `behavioral_instructions`(5%) |
| **vibe-init (Vishal)** | 10 大类 59 条治理策略 | 按"责任域"分类——每个 AI 施工动作对应一个责任域：`architecture_decisions` / `coding_standards` / `context_engineering` / `dependency_management` / `error_handling` / `git_workflow` / `project_structure` / `security` / `testing` / `tooling` |
| **n1n.ai 3-Tier Memory** | 知识优先级三分法 | HIGH（不可变核心身份）→ 直接 LTM；MID（可变偏好）→ MTM 晋升队列；LOW（瞬时上下文）→ 丢弃 |

**三轨 18 类设计**：

#### Track A：Vibe Coding 施工知识（8 类）

> 来源：Session Log / AGENTS.md / ADR / 门禁阻断 / pre-commit hooks。提取优先级：自动（无需 Owner 触发）。

| # | `category` | 含义 | 优先级 | `halflife_h` | 典型来源 | 示例 |
|:--:|-----------|------|:---:|:---:|---------|------|
| A1 | `coding_convention` | 编码约定 | HIGH | 2160h(90d) | AGENTS.md / pre-commit 规则 | "ruff 不用 pylint：快 10-100x + pyproject.toml 原生集成" |
| A2 | `architecture_decision` | 架构决策 | HIGH | 4320h(180d) | ADR / 蓝图 | "L01 层选 SQLite 而非 PostgreSQL：< 10万 KE 规模时 SQLite 足够，零运维成本" |
| A3 | `governance_rule` | 治理规则 | HIGH | 2160h(90d) | AGENTS.md / PS 标准 | "新 .py 文件必须在 scripts/governance/ 注册（§6.5 入库强制约定）" |
| A4 | `failure_pattern` | 失败模式 | HIGH | ∞(permanent) | Session Log 教训 / 门禁阻断 | "KE-001: 3587 个误报源于一个多余的反斜杠——扫描器先自检" |
| A5 | `tool_configuration` | 工具配置 | MID | 4320h(180d) | justfile / pyproject.toml / CI 配置 | "pytest 必须用 --strict-markers：所有 @pytest.mark.* 装饰器必须注册到 pyproject.toml" |
| A6 | `dependency_knowledge` | 依赖知识 | MID | 2160h(90d) | 踩坑 / 升级记录 | "pydantic v2 BaseSettings → model_config SettingsConfigDict 迁移注意事项" |
| A7 | `workflow_pattern` | 工作流模式 | MID | 2160h(90d) | Session Log / AGENTS.md | "Session 启动顺序：AGENTS.md → 最新 Session Log → 按 §8.2 加载领域规则" |
| A8 | `context_engineering` | 上下文工程 | MID | 4320h(180d) | 实践经验 | "Hot ≤ 400 行 / Warm 按域触发 / Cold 按需检索——context utilization ≤ 40% 性能最优" |

#### Track B：金融领域知识（7 类）

> 来源：arXiv 论文 / GitHub 开源项目 / 券商研报 / 监管文件。提取优先级：Owner 触发或定期批量注入。

| # | `category` | 含义 | 优先级 | `halflife_h` | 典型来源 | 示例 |
|:--:|-----------|------|:---:|:---:|---------|------|
| B1 | `strategy_logic` | 策略逻辑 | HIGH | 2160h(90d) | 论文 / 开源 / 内部研发 | "Turtle Trading：20 日突破入场 + 10 日反向出场 + ATR(20) 止损" |
| B2 | `factor_design` | 因子设计 | HIGH | 4320h(180d) | 论文 / 研究 | "Momentum 因子：过去 12-1 月累计收益，截面标准化" |
| B3 | `risk_management` | 风险管理 | HIGH | 2160h(90d) | 论文 / 监管 / 内部实践 | "VaR 99% 置信度 20 日回望窗口——巴塞尔 III 推荐" |
| B4 | `data_quality` | 数据质量 | MID | 4320h(180d) | 治理经验 / 踩坑 | "东方财富 API 复权因子：需和通达信交叉校验后使用" |
| B5 | `market_microstructure` | 市场微观结构 | MID | 8640h(360d) | 论文 / 交易经验 | "A 股 T+1 制度：当日买入次日才能卖出；涨停板 ±10%" |
| B6 | `compliance` | 合规知识 | MID | 2160h(90d) | 监管文件 / 法律 | "私募基金信息披露：季度报告应在季后 15 个工作日内提交" |
| B7 | `backtest_methodology` | 回测方法论 | MID | 4320h(180d) | 论文 / 专业实践 | "样本外测试最小周期 ≥ 样本内的 1/3——De Prado 建议" |

**优先级驱动的提取与存储策略**（对标 n1n.ai priority-based classification）：

| 优先级 | 条件 | 存储策略 | 对应类别 |
|:---:|------|---------|---------|
| **HIGH** | 不可变核心知识 + 错误必可避免类 | 提取后直接写入 KE（跳级），不入 KO 等待队列 | A1-A4, B1-B3 |
| **MID** | 可变偏好/配置/方法论类 | 先入 KO（Knowledge Observation）→ MTM 晋升队列 → 达升格阀值后变为 KE | A5-A8, B4-B7 |
| **LOW** | 瞬时/会话级/不可复用 | 保留在 Session Log 原位置，不入知识库。G2 Triage 阶段过滤 | 天气、临时报错、单次手动修法 |

#### Track C：Owner 决策画像（3 类）

> 来源：聊天记录中 Owner 覆盖 AI 建议的决策 / 反复表达的偏好 / 隐性审美判断。优先级：**全部 LOW**（仅参考，不自动执行）。对标 Anthropic Claude implicit preference signals + GitHub Copilot user style learning。

| # | `category` | 含义 | 优先级 | `halflife_h` | 典型来源 | 示例 |
|:--:|-----------|------|:---:|:---:|---------|------|
| C1 | `decision_rule` | Owner 的决策启发式 | LOW | 720h(30d) | Owner 覆盖 AI 建议时自动提取 | "Owner 在 ruff vs pylint 中选 ruff——偏好 Rust 工具链" |
| C2 | `taste_signal` | Owner 的审美/偏好信号 | LOW | 720h(30d) | Owner 反复表达的偏好 | "Owner 偏好短函数 ≤30 行 + 避免过度抽象" |
| C3 | `override_log` | Owner 覆盖了 AI 的建议 | LOW | 720h(30d) | AI 建议被拒绝时记录 | "AI 建议 PostgreSQL → Owner 选 SQLite：零运维" |

**Track C 的特殊规则**：

| 维度 | Track A/B | Track C |
|------|:---:|:---:|
| 强制执行 | ✅ 是（如 A4 会阻断 CI） | ❌ 否——仅作为 context 注入，参考但不自动决策 |
| 过期策略 | 90d-360d | **30d**——偏好会漂移，短期有效 |
| 衰减机制 | usage_count↑ → 越用越强 | 30d 未再确认 → 自动 DISCARDED |
| 冲突处理 | 报错——知识冲突必须裁决 | 静默提示——"您上次说 X，但当前是 Y，要更新偏好吗？" |
| 入库条件 | G2 Triage ≥ 0.6 | Owner 重复 ≥2 次即可（不要求质量分数） |

> **为什么 Track C 存在但不强制执行**：偏好是弱信号——Owner 会说"我偏好小迭代"，但紧急修复可能做一个大迭代。把偏好变硬规则会让 Owner 被自己过去的决策锁死。但完全不记录浪费可复用信息（下次 AI 就知道"这个老板喜欢短函数"）。对标 Anthropic Claude——"preference signals are suggestions, not rules"。

> **对标**：n1n.ai (2026) 三优先级分类——HIGH 直接 LTM、MID 走 MTM 晋升队列（"≥2 references → consolidate to LTM"）、LOW 丢弃。Vasilopoulos trigger table——"automatically routes tasks to appropriate specialized agents based on observable signals"。
> 大白话：三轨各有分工——Track A（施工知识）是"怎么盖房子"，强制执行；Track B（金融知识）是"盖什么房子"，强制执行；Track C（Owner 画像）是"老板喜欢什么风格"，仅参考不强制——30 天没人提就自动过期，因为人的偏好会变。

#### Track D：AI-AI 协作知识（beta+ 预留接口）

> **状态**：`planned`——分类桩已就位，接口契约已定义，beta 之前不实现提取/入库逻辑。
> **为什么现在就要定义**：§6.3 埋雷判定——如果等 1000+ KE 入库后再补 AI-AI 协作分类，全量重新打标的工量 = 埋雷。现在定义空壳 = 零成本的"接口预留位"。

**场景**（beta 未来状态）：

| 场景 | 描述 | 产生什么知识 |
|------|------|------------|
| 双 Agent 对等讨论 | Agent A 提出方案 → Agent B 挑战/改进 → 收敛 | 协作决策日志（哪个 Agent 的方案赢了、为什么） |
| Agent 分工协作 | Agent A 负责代码 → Agent B 负责测试 → 结果合并 | 分工模式（并行/串行/接力）、Agent 专长画像 |
| Agent 交叉审查 | Agent A 写的 ADR → Agent B 审查 → 发现问题 | 审查发现（Agent B 发现了 Agent A 的什么盲区） |
| 多 Agent 投票 | 3 个 Agent 对同一问题给出不同答案 → 投票裁决 | 投票模式（哪个 Agent 的方案更正确/更高效） |

**Track D 分类桩（3 类，beta 实现）**：

| # | `category` | 含义 | 优先级 | `halflife_h` | 典型来源 | 示例（beta 才产生） |
|:--:|-----------|------|:---:|:---:|---------|------|
| D1 | `agent_collab_pattern` | Agent 协作模式 | — | — | 双 Agent 讨论日志 | "Agent B 挑战了 Agent A 的 SQLite 选型，最终 Agent A 引用 ChromaDB 官方文档胜出" |
| D2 | `agent_expertise_profile` | Agent 能力画像 | — | — | 交叉审查记录 | "Agent Qwen 在编码约定类偏差最大（20% 违反 A1 规则），建议加强 A1 上下文注入" |
| D3 | `multi_agent_decision` | 多 Agent 联合决策 | — | — | 投票日志 | "3/3 Agent 一致选择 ruff；2/3 Agent 建议 pytest -x 而非 pytest --lf" |

**接口契约（现在定义，beta 实现）**：

```python
# beta 新建：src/zephyr/kb/agent_collab.py

def extract_agent_discussion(
    agent_a_id: str,
    agent_b_id: str,
    discussion_log: str,
    winner: str | None
) -> list[KnowledgeEntry]:
    """双 Agent 讨论 → D1 agent_collab_pattern KE"""
    ...

def profile_agent_expertise(
    agent_id: str,
    review_history: list[ReviewResult]
) -> KnowledgeEntry:
    """交叉审查历史 → D2 agent_expertise_profile KE"""
    ...

def record_multi_agent_vote(
    topic: str,
    votes: dict[str, str],
    outcome: str
) -> KnowledgeEntry:
    """投票记录 → D3 multi_agent_decision KE"""
    ...
```

> **预留原则**：分类桩已在蓝图中注册（= "这个地方以后会有内容"），`KeCategory` 枚举先不加 D1-D3（避免 `schemas.py` 出现未实现的枚举值导致运行时 KeyError），待 beta 统一启用。蓝图 = 设计图，代码 = 施工成果——设计图可以先画，施工可以分批。
> **对标**：Terraform provider contract —— 接口先定义、实现可分批 / K8s API versioning —— `planned` 状态的 API 不进 `v1` 但已在设计文档中注册

> **大白话**：未来会有多个 AI 互相讨论、互相审查、互相投票——它们之间的互动也会产生知识（哪个 Agent 更擅长什么、两个 Agent 讨论后谁的方案更好）。但现在没到那个阶段——现在只有 Owner+AI 两个人，不需要多个 AI 之间的协作知识。所以我们先在蓝图里画好"预留停车位"（Track D + 接口），等真需要的时候再盖车库——不用回头拆墙重建。

### 3.9 知识来源矩阵与全自动获取决策模型

**核心理念**：Owner 不应该被要求"记得提取知识"——所有提取触发必须是**自动的**。Owner 的角色是**审批**（面对自动生成的草稿说 yes/no），而非**启动**。

#### 3.9.1 来源矩阵（7 条全自动管线）

| # | 来源 | 触发方式 | 自动率 | 输出 | 频率 | Owner 角色 |
|:--:|------|---------|:---:|------|:---:|---------|
| 1 | **AGENTS.md / 治理标准变更** | git hook + L3 哨兵自动检测 | 100% | KO→KE（A3） | 每次 commit 含规则文件 | 无需介入 |
| 2 | **跨层契约（CTR）版本升级** | CTR-001~CTR-006 YAML version bump → `schema_version` 变更事件 | 100% | KE（A2） | CTR version bump 时 | 无需介入 |
| 3 | **蓝图版本升级** | bp version bump 事件 | 100% | KE（A2/A3/A5） | version bump 时 | 无需介入 |
| 4 | **Pre-commit / CI 阻断** | pre-commit hook 捕获 | 100% | KO→KE（A4） | 每次阻断 | 无需介入 |
| 5 | **Session Log 生成** | auto-handoff-log.py 完成 | 100% | KO→KE（A1-A8）| 每次 session 结束 | 无需介入 |
| 6 | **外部论文 / 开源项目** | Session Log 中出现了 arXiv/GitHub 链接 → 自动触发 D0 流水线 | 80% | KO→KE（B1-B7） | 按需（自动检测+自动触发） | **仅审批**：系统自动生成 KO 草稿 → 推送提醒 Owner "3 条新知识待审批，回复 yes/no" |
| 7 | **知识差距巡检** | APScheduler 每周 cron | 100% | KO（GAP）→ 推送 Owner 查看 | 每周一次 | **仅查看**：系统自动生成差距报告 → 推送 Owner "本周发现 2 个知识空白" |
| 8 | **CTR 运行时质量信号** | CTR-001 `quality_score` / CTR-002 `confidence` / CTR-005 `slippage` 连续 N 次超阈值（如 quality_score<0.3 连续10天）→ 自动触发 | 100% | KO→KE（B1/B3） | 异常事件驱动 | 无需介入 |

**关键设计**：来源 6（外部知识）和来源 7（差距巡检）是仅有的需要 Owner 参与的管线——但不是"Owner 记得启动"，而是系统自动检测→自动生成草稿→自动推送提醒→Owner 只需回复 yes/no（一个词）。来源 8（CTR运行时质量信号）是 100% 自动的——异常事件驱动，零Owner触发。

#### 3.9.4 聊天记录→KE 自动化决策树

```
原始对话记录（IDE 聊天窗口）
       │
       ▼ session 结束时自动触发（zero Owner action）
auto-handoff-log.py 生成 Session Log（§3.9.3 格式）
       │
       ▼ 自动触发（zero Owner action）
§5.10 五级切片 → 识别知识块边界
       │
       ▼ 自动触发（zero Owner action）
G1 Ingest → 格式校验
       │
       ▼ 按以下规则自动分流（zero Owner action）
  ┌──────────────────┬──────────────────┬──────────────────┐
  │ 场景              │ 判定逻辑          │ 动作              │
  ├──────────────────┼──────────────────┼──────────────────┤
  │ AI 发现了新事实/模式│ §3.8 15类模式匹配 │ 自动 KO→HIGH→KE   │
  │ "ruff 比 pylint 快  │ ke_body 含对比  │ （直达，不等 3 条）│
  │  10-100x"          │  + conclusion    │                  │
  ├──────────────────┼──────────────────┼──────────────────┤
  │ AI 踩坑/翻车       │ 含 error/fail/   │ 自动 KO→HIGH→KE   │
  │ "花了2小时修这个    │ fix/time_cost    │ （轨道2 门禁阻断）  │
  │  ruff 错误..."     │                  │                  │
  ├──────────────────┼──────────────────┼──────────────────┤
  │ Owner 主动指令     │ Owner 说的是      │ 自动 KO→MID→      │
  │ "我觉得应该加..."   │ 观察/偏好         │ KO 晋升队列        │
  ├──────────────────┼──────────────────┼──────────────────┤
  │ AI 和 Owner 讨论   │ 双边多轮 +        │ 自动 KO→MID→      │
  │ 决策过程           │ 结论明确          │ KO 晋升队列        │
  ├──────────────────┼──────────────────┼──────────────────┤
  │ AI 纯流程操作      │ "好的，我现在开始   │ ❌ 自动丢弃        │
  │                   │  写..." / "编译通过"│（G2 Triage 过滤）  │
  └──────────────────┴──────────────────┴──────────────────┘
```

#### 3.9.2 Session Log 最小格式约定（自动提取的基础）

**为什么需要格式约定**：format→regularity→机械提取→零人力。如果 Session Log 格式不统一，后续 G1-G5 就不可靠。

```yaml
# 每次 session 结束时由 auto-handoff-log.py 自动生成（zero Owner action）
session_id: "2026-05-02_session-047"
timestamp_start: "2026-05-02T14:00:00+08:00"
timestamp_end: "2026-05-02T16:23:17+08:00"
context_loaded:
  - "AGENTS.md v5.0.0"
  - "Session Log 046"
  - "KB MOD-KB-001 blueprint"
action_blocks:                    # ← G1 Ingest 从这里提取知识块
  - action: "重构 KeCategory 枚举"
    why: "15类双轨体系覆盖施工+金融知识"
    result: "schemas.py KeCategory 从10类→15类"
    failures: []                  # 无失败 → 自动归类 A1/A2
  - action: "发现 ruff E501 误报"
    why: "多了一个反斜杠导致 3587 个误报"
    result: "修正正则 → 误报清零"
    failures:                     # 有失败 → 自动归类 A4
      - type: "scanner_bug"
        root_cause: "regex 多余反斜杠"
        fix_method: "删除一个 `\\`"
        time_cost_minutes: 15
tags: ["kb", "schema-refactor", "scanner-bug"]
next_session_hint: "继续补 §3.9 知识来源清单"
handoff_package_path: "docs/19_development_workspace/session-logs/handoff-047.md"
```

---

> **对标**：Vasilopoulos session tracing ("each session perpetually captured in session tracing") + Horthy Harness auto-handoff-log ("session handoff package auto-generated via git hook") + vibe-init 治理引擎（"every governance strategy maps to a KE auto-check"）。
> 大白话：知识从七个不同的"水龙头"流进来——AGENTS.md 改了、ADR 定了、蓝图升级了、提交失败了、session 跑完了、论文链接出现了、每周巡检发现空白了。七个水龙头**全部自动打开**——Owner 不需要记得去拧任何一个。唯一需要你的地方是：面对系统自动推送的审批提醒时回一句 "yes" 或 "no"。

---

#### 3.9.3 聊天记录→知识提取器（Chat-to-KE Extractor）

**问题**：聊天（如本 session 的对话）是最大量、最高频的知识入口——一条 2000 行的聊天记录包含 15-30 个可提取的知识片段，但也混有大量上下文垃圾（"嗯""好的""继续"）。需要**自动拆分 + 自动分类 + 噪音过滤**。

**对标**：[vibe-coding-mcp](https://github.com/MUSE-CODE-SPACE/vibe-coding-mcp)（MUSE-CODE-SPACE，2025-12，v2.12.1）——提供 `muse_collect_code_context`（对话收集）+ `muse_summarize_design_decisions`（决策提取）+ `muse_auto_tag`（自动分类）+ `muse_create_session_log`（归档 Markdown）。Vasilopoulos session tracing："every session perpetually captured + auto-extracted"。

**三段式提取器架构**：

```
聊天记录（原始 Markdown）
    │
    ▼
┌──────────────────────────────────────────────────────┐
│ S1：语义分段器（Semantic Chunker）                      │
│ ───────────────────────────────────────────          │
│ 按话题转换切分——不按固定行数、不按固定时间               │
│                                                      │
│ 信号1：Markdown H2/H3 标题 ──→ 自然段落边界             │
│ 信号2：相邻段向量余弦相似度 < 0.3 ──→ 话题转换点         │
│ 信号3：总结/决策关键词 ("结论""所以""决定了""最终")       │
│                                                      │
│ 单条 2000 行 chat → 15-30 个"对话片段"（segment）       │
└──────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────┐
│ S2：三元判定器（Tri-Categorizer）                       │
│ ───────────────────────────────────────────          │
│ 每个 segment 判定为三类之一                             │
│                                                      │
│ 🟢 知识信号（declaration / decision / rule）           │
│    · 含 "决定了" / "CSS原则" / "规则" / "数据"           │
│    · 含对比表 / 专业参考 / 5 Whys 根因                   │
│    · Owner 明确说 "把这个加进去" / "按这个来"             │
│                                                      │
│ 🟡 上下文垃圾（banter / 重复 / 死路）                   │
│    · ≤50 tokens 的短响应                                │
│    · 和上一条向量余弦相似度 > 0.9（重复）                 │
│    · 纯提问（还没得到答案）→ 等答案出来再判定             │
│                                                      │
│ 🔵 半信号（refinement / 追问 / 澄清）                    │
│    · "还有一个问题" "继续说" "细化一下"                   │
│    · 合并到关联的 🟢 片段（作为补充 material）            │
│    · 如果 3 轮后还没关联到 🟢 → 丢弃                     │
└──────────────────────────────────────────────────────┘
    │
    ▼
🟢 知识信号 → G1 Ingest → G2 Triage → HIGH→KE / MID→KO
🟡 上下文垃圾 → 丢弃（不入库，留在 Session Log 原位置）
🔵 半信号 → 合并（追加到关联 🟢 片段的 body 末尾）
```

**噪音控制的四道硬门槛**：

| # | 机制 | 门槛值 | 作用 |
|:--:|------|--------|------|
| N-01 | 单片段最低长度 | ≥ 100 tokens | 过滤"好的""继续"等空响应 |
| N-02 | 知识信号评分 | G2 Triage ≥ 0.6 | 半信号自动过滤 |
| N-03 | 同 session 内去重 | 向量余弦相似度 > 0.9 → 合并 | 同一结论重复说只产 1 条 KE |
| N-04 | 日入库上限 | ≤ 30 条新 KO/天 | 防止密集讨论淹没知识库 |

**自动触发时机**：

| 触发事件 | 触发方式 | 提取范围 |
|---------|---------|---------|
| Session 结束（IDE 关闭 / 显式 `end session`） | post-commit hook → `auto-handoff-log.py` | 本 session 全部聊天 → 提取 🟢 片段 → G1 |
| 聊天中 Owner 说"把这个记下来" | 实时触发器 → 当前上下文 5 轮对话 → 直接 KE | Owner 手动标定片段 → 跳 KO → 直达 KE |
| 日终 22:00（如当天有聊天但未提取） | APScheduler cron → `extract_daily_chat.py` | 当天全部未提取片段 → 批量 G1 |

> **核心原则**：聊天是原料——不能全存（噪音太多）、不能全删（知识会丢）。必须拆→判→存。对标 vibe-coding-mcp：`collect` → `summarize` → `tag` → `log`。
> **大白话**：你和我的这场对话——你提三个问题、我回答、你决策——这些全是知识原料。系统要做的：①切成小段 ②判断哪些有用哪些是废话 ③有用的入库、没用的丢掉。每天最多 30 条，多了说明全是重复废话。

---

#### 3.9.5 决策记录的三层模型（取代旧 ADR 体系）

**背景**：ADR 体系已于 2026-04-27 裁定废弃（R72）。传统 ADR 假设"有人写 8 节模板 → 团队 Review → 永不过期"，但在 100% AI 开发的氛围编程下，这个假设不成立——决策在聊天中发生，不需要"有人写"。

**对标氛围编程社区**（8 个社区调研，2026-05）：

| 社区 | 做法 | 一行代码承载量 |
|------|------|:---:|
| Claude Code 官方 | CLAUDE.md `## Previous Decisions` — 每决策一行 | ≤1 行 |
| Steve Yegge (CHOP) | AI 在聊天中当场记录决策 → 追加到 CLAUDE.md | ≤1 行 |
| vertu.com (2026) | `decisions.log` — AI 自己写："I chose X over Y because..." | ≤1 行 |
| Cursor Rule Framework | `architecture.mdc` 自动更新内置决策 | ≤3 行 |
| 7/8 社区结论 | **不用传统 ADR。一句话决策贴进上下文文件。** | ≤200 字 |

**ZephyrAlpha 的三层决策记录模型**：

```
决策发生（聊天中）
      │
      ▼ AI 自动检测决策信号（关键字："决定了""选择一个""最终方案"）
      │
      ▼ 自动提取一句结论（≤200 字）
"选 ruff 不用 pylint：快 10-100x（Rust vs Python）+ pyproject.toml 原生集成"
      │
      ▼ 分流判定
 ┌──────────────────┬──────────────────────────┐
 │ L2：一行决策       │ L3：深度决策（KE）         │
 │ （绝大多数场景）     │ （需要对比表/冲突检测时）    │
 │                  │                          │
 │ 条件：            │ 条件：                    │
 │ · 无对比表需求      │ · 需要对比表/数据支撑       │
 │ · 未来不会反复争论   │ · 可能被后续 AI 重新论证     │
 │ · ≤200 字说得清    │ · 涉及架构不变核心          │
 │                  │                          │
 │ → AGENTS.md       │ → KE（A2）G1-G5 完整流程   │
 │   §10 历史决策      │   含对比表 + 结论 + 反模式   │
 │   每次决策追加一行   │   recall() 可语义检索      │
 └──────────────────┴──────────────────────────┘
```

**三层完整视图**：

| 层 | 载体 | 内容 | 粒度 | 示例 |
|:---:|------|------|------|------|
| L1 | AGENTS.md §5 Owner 画像（Track C） | Owner 反复表达的偏好/审美/决策启发式 | 30d TTL，弱信号 | "Owner 偏好短函数 ≤30 行" |
| L2 | AGENTS.md §10 历史决策 | 技术选型/工具对比的最终结论 | ≤200 字，一句话 | "选 SQLite 不用 PostgreSQL：零运维成本 > 并发需求" |
| L3 | KE（A2 architecture_decision） | 需要对比表/数据支撑的重大决策 | 5 段落 + 对比表 | ADR-0031 → KE-042（ChromaDB 选型） |

**旧 ADR 迁移方案**：

```
36 份旧 ADR (docs/02_enterprise_architecture/adr/)
      │
      ▼ 首次运行 adr_migrate.py（beta 单次执行）
      │
每份 ADR → 提取一句结论 + category + priority
      │
      ▼ 分流
 ┌──────────────────┬──────────────────────┐
 │ ≤200 字结论        │ 含对比表/多方案论证       │
 │ （大部分 ADR）      │ （如 ADR-0031 ChromaDB）│
 │                  │                      │
 │ → AGENTS.md §10   │ → KE（A2）            │
 │   原文件归档        │   G1-G5 完整流程        │
 │   docs/_archive/   │                       │
 │   old_adr/         │                       │
 └──────────────────┴──────────────────────┘
```

> **专业参考**：Claude Code 官方 CLAUDE.md 规范 §3 Historical Context——"每次重要决策后 AI 自动追加一行" / vertu.com 2026——"decisions.log：'I chose Library X because smaller bundle size'" / Cursor Rule Framework——"architecture.mdc auto-updated with decision logs"
> **大白话**：旧 ADR 体系太重了——每条决策要写 8 节、要编号、要审批、要永不过期。氛围编程社区 8 家调研，0 家在用传统 ADR。他们的做法很简单：聊天中产生了决策 → AI 自动提取一句话（"选了 X 因为 Y"）→ 贴到 AGENTS.md 里 → 下次 AI 启动自动读到 → 不用任何人维护。特别重要的决策（比如 ChromaDB 选型——需要多个方案对比那种）才走完整的 KE 流程。36 份旧 ADR 也是一样处理：一句话结论进 AGENTS.md，含对比表的深度决策进 KE（A2），原文件归档。

---

### 3.10 KO（Knowledge Observation）存储格式

**定位**：KO 是"知识碎片"——尚未通过完整 G1→G5 流水线的轻量级知识观察。对标 ITIL DIKW 金字塔的 Data→Information 层：KO = 原始观察（Data），KE = 结构化知识（Information），KB = 聚合规则（Knowledge）。

**KO 与 KE 的核心差异**：

| 维度 | KO | KE |
|------|:---:|:---:|
| 状态 | OBSERVED / PROMOTING / PROMOTED / DISCARDED（4 状态） | DRAFT→VERIFIED（10 状态机，§3.3） |
| 质量要求 | 低——仅需来源可追溯 | 高——需经过 G2 Triage 评分 ≥ 0.6 |
| 向量化 | ❌ 不入 ChromaDB | ✅ 入 ke_entries Collection |
| 被检索 | ❌ 不被 `recall()` 返回 | ✅ 语义检索+标签过滤+全文搜索 |
| 晋升条件 | 同 category 累计 3 条 + 人工确认 | — |
| 文件命名 | `KO-{NNN}-{slug}.md` | `KE-{NNN}-{slug}.md`（§3.2.1） |

**KO 4 状态机**：

```
OBSERVED → PROMOTING → PROMOTED（→ 转为 KE，原 KO 归档）
    │          │
    └──────────┴──→ DISCARDED（不晋升，直接丢弃）
```

| 状态 | 含义 | 条件 |
|------|------|------|
| OBSERVED | 系统自动生成，等待积累 | G2 Triage 将 LOW→MID 的知识放入 KO 等待队列 |
| PROMOTING | 满足晋升条件（同 category ≥ 3 条），等待 Owner 确认 | L2 哨兵触发："3 条同类 KO 待审批" |
| PROMOTED | Owner 确认晋升，已转为 KE | `batch_ingest.py` 将 KO 批量转为 KE |
| DISCARDED | Owner 拒绝晋升，或 90d 未达晋升条件 | 自动过期清理（APScheduler 月度 cron） |

**KO 文件模板**（`docs/08_knowledge/ko/KO-015-ruff-vs-pylint-speed-comparison.md`）：

```yaml
---
ko_id: "KO-015"
title: "ruff 比 pylint 快 50x 的实测数据"

category: "tool_configuration"
domain: "infra"
layer: "L01"

source_type: "session_log"
source_path: "docs/19_development_workspace/session-logs/session-047.md"

status: "OBSERVED"
priority: "MID"
quality_score: 0.45

created_at: "2026-05-02T14:35:00+08:00"

# ═══════════════════════════════
# KO 不包含的字段（KE 专有）：
#   tags, ttl, half_life_days, last_verified_at,
#   depends_on_ke, supersedes_ke, _locked
# 运行时字段同样不在文件中
---

# KO-015：ruff 比 pylint 快 50x 的实测数据

## 原始观察

在本次 session 中，对 ruff v0.11.x 和 pylint v3.x 进行了速度对比：
- ruff 检查全项目 120 个 .py 文件：0.3s
- pylint 检查同一批文件：15.2s
- 差距约 50x

## 来源上下文

```
Session Log handoff-047 §工具链选型讨论
Owner: "ruff 和 pylint 哪个快？"
AI: "ruff 快 10-100x，实测全项目 0.3s vs 15.2s"
```

---
*KO v1.0.0 | 晋升需同 category(tool_configuration) 累计 3 条*
```

> **大白话**：KO 是"草稿纸"——AI 在干活过程中产生的零散观察先记在这里。质量要求低（不需要满分），不入向量库（没资格被检索），等攒够 3 条同类的才由系统提醒 Owner"这几条草稿够格了吗？够的话我帮你转正成 KE"。这样做的好处：不会每个小观察都占据向量库空间，也不会丢弃可能有用的信息——先进草稿纸，攒够了再转正。

### 3.11 KB（Knowledge Base Rule）存储格式

**定位**：KB 是"系统级规则"——从多条 KE 聚合提炼出的硬约束/自动化检查项。对标 ITIL DIKW 的 Knowledge→Wisdom 层：KB = 可执行的 Wisdom（不是"建议"，是"规则"）。

**KB 与 KE 的核心差异**：

| 维度 | KB | KE |
|------|:---:|:---:|
| 消费者 | pre-commit hooks / CI 门禁 / APScheduler cron | AI context assembler / `recall()` |
| 格式 | YAML rule 定义（可机器执行） | Markdown 知识卡片（可人类阅读） |
| 来源 | 多条 KE 聚合 + MINOR 自动合并 | 单条知识提取 |
| 状态 | ACTIVE / SUPERSEDED / RETIRED（3 状态） | 10 状态机 |
| 向量化 | ❌ 不入 ChromaDB（规则精确匹配，不需语义检索） | ✅ |
| 文件命名 | `KB-{NNN}-{rule_name}.yaml` | `KE-{NNN}-{slug}.md` |

**KB 3 状态机**：

```
ACTIVE → SUPERSEDED（被新版规则取代）
  │
  └──→ RETIRED（规则不再适用）
```

**KB 文件模板**（`docs/08_knowledge/kb/KB-001-python-linter-must-be-ruff.yaml`）：

```yaml
---
kb_id: "KB-001"
title: "Python Linter 必须是 ruff"

category: "tool_configuration"
domain: "infra"
layer: "L01"

status: "ACTIVE"
priority: "P0"

derived_from:
  - "KE-041"     # pre-commit hooks 选型
  - "KE-042"     # ruff 选 pylint
  - "ADR-0020"   # 编码工具链标准化

rule:
  check: "file_exists"
  path: "pyproject.toml"
  required_section: "tool.ruff.lint"
  on_violation: "BLOCK"           # BLOCK / WARN / AUTO_FIX

merged_at: "2026-05-03T10:00:00+08:00"
created_at: "2026-05-02T14:30:00+08:00"
updated_at: "2026-05-03T10:00:00+08:00"

supersedes: []
superseded_by: []
---
```

**KB 的自动聚合策略（MINOR 自动合并）**：

| 条件 | 操作 | 触发 |
|------|------|------|
| 2+ 条 ACTIVE KB 字段完全相同（仅 derived_from 不同） | MINOR 自动合并 derived_from 列表，保留一条 | CI weekly cron |
| 2+ 条 ACTIVE KB 规则有交叉但不完全相同 | 推送 Owner："2 条规则有冲突，建议合并？" | L3 哨兵 |
| 1 条 ACTIVE KB 90d 未被触发 | 自动 RETIRED（冷却机制） | APScheduler monthly cron |

> **对标**：K8s Admission Controller（KB = 准入规则——不符合规则的操作被硬件阻断）+ OPA/Rego（声明式策略语言——"期望状态"而非"执行步骤"，对应 §6.4 声明式优于命令式）
> **大白话**：KB 不是"建议"——是"规则"。KE-042 说"ruff 比 pylint 好"（知识），KB-001 说"pyproject.toml 里必须有 `[tool.ruff.lint]` 否则提交直接挡住"（规则）。KB 从多条 KE 自动聚合，同类型规则自动合并，90 天不用自动废弃——这样规则体系永远不会膨胀到没人管。

---

### 4.0 数据引擎物理布局（`data/`）——数据库文件独立于 Markdown 文档

**设计原则（对标 12-Factor App §3 + ChromaDB 官方 + SQLite 最佳实践）**：

> 代码和数据的生命周期不同——代码通过 Git 版本控制、数据通过迁移脚本演化。Markdown KE 文件（人类可读知识卡片）属于 `docs/` 图书馆，SQLite/ChromaDB 二进制文件（机器运行时数据）属于 `data/` 机房。

**物理路径（环境变量驱动）**：

```yaml
# config/db_config.yaml
kb:
  data_root: ${KB_DATA_DIR:-data/}             # 根目录——环境变量覆盖，默认 data/
  sqlite:
    db_path: ${KB_SQLITE_PATH:-data/sqlite/kb_state.db}
  chroma:
    persist_dir: ${KB_CHROMA_DIR:-data/chroma/}
  cache:
    reranker_model: ${KB_RERANKER_DIR:-data/cache/bge-reranker-v2-m3/}
```

**磁盘布局**：

```

├── data/                          # 所有运行时数据根目录（不入 Git 的生产数据）
│   ├── .gitkeep                   # 空目录占位——确保 Git 追踪 data/ 的存在
│   ├── sqlite/                    # SQLite 数据库引擎文件
│   │   └── kb_state.db            #   knowledge_entries + kb_rules + state_log
│   ├── chroma/                    # ChromaDB 持久化目录（向量 + 全文本索引）
│   │   ├── chroma.sqlite3         #   Chroma 自动生成——元数据 (Sysdb + WAL + Metadata)
│   │   ├── index/                 #   Chroma 自动生成——HNSW 向量索引 binary
│   │   └── {collection_uuids}/    #   Chroma 自动生成——每 Collection 独立 Segment
│   └── cache/                     # 推理缓存（模型权重）
│       └── bge-reranker-v2-m3/    #   Reranker 模型 (~1.2GB, beta 下载)
│
├── docs/
│   └── 08_knowledge/              # Markdown KE 文件（图书馆——§4.2）
│
├── .gitignore                     # 数据库文件的 Git 策略 ↓
└── config/
    └── db_config.yaml             # 数据库路径配置（环境变量 + 默认值）
```

**`.gitignore` 三级策略**：

| 级别 | 内容 | Git 追踪？ | 理由 |
|:---:|------|:---:|------|
| L1 | `data/.gitkeep`、SQL migration schema 文件 | ✅ | 保证目录结构一致 + 数据库版本可重建 |
| L2 | `data/sqlite/kb_state.db`（开发环境种子数据） | ⚠️ 可选 | 方便新 AI session 快速启动——需 Owner 显式 `git add -f` |
| L3 | `data/chroma/**`、生产 `*.db`、`data/cache/**` | ❌ | 二进制大文件 + 可从 Markdown KE 重建（`embedding_migrate.py reindex`） |

```gitignore
# .gitignore 追加：
# --- Database files (12-Factor App: code ≠ data) ---
data/sqlite/*.db
!data/sqlite/.gitkeep
data/chroma/**
!data/chroma/.gitkeep
data/cache/**
!data/cache/.gitkeep
```

**环境变量 vs 代码的边界（对标 12-Factor App Config 第三条）**：

| 环境 | `KB_DATA_DIR` | 理由 |
|------|--------------|------|
| 开发（Windows 本地） | 未设置 → fallback `data/`（项目根下） | 零配置即用 |
| CI（GitHub Actions） | `${{ github.workspace }}/ci_data/` | 与源码隔离，每次 CI run 清空重建 |
| 生产（Linux 服务器） | `/mnt/ssd/zephyr_data/` | 放在 SSD 上——ChromaDB HNSW 索引需要快速随机读 |

> **为什么不在 `docs/08_knowledge/` 下放数据库文件**：`docs/` = 人类可读文档（Markdown KE 卡片），`data/` = 机器运行时数据（SQLite .db + Chroma 二进制索引）。两者的消费者不同——前者被 context_assembler 读，后者被 kb_repo.py 读。放在同一个目录会让 AI 困惑："这个 200MB 的 .bin 文件我应该读吗？"
> **对标**：12-Factor App §三——Config via environment variables / ChromaDB 官方——`PersistentClient(path=...)` ≠ source code directory / SQLite 最佳实践——`data/` for WAL-mode databases

> **大白话**：Markdown 知识卡片是"书"——放 `docs/` 图书馆书架上。SQLite 数据库和 ChromaDB 向量索引是"服务器"——放 `data/` 机房里。书架和机房分开，互不干扰。路径全用环境变量控制——开发时在项目目录下（`data/`），生产时可以指向 SSD 高速盘（`/mnt/ssd/zephyr_data/`），改一行环境变量就行，不用改代码。

---

## §4 目录结构/物理布局

### 4.1 代码层（`src/zephyr/kb/`）

```
src/zephyr/kb/
├── __init__.py                # 包初始化
├── chromadb_init.py           # ChromaDB 4 Collection 初始化（140行）✅
├── kb_repo.py                 # 核心仓储：10状态机 + SQLite + ChromaDB（422行）✅
├── unified_memory_api.py      # RI-02 统一内存 API：remember/learn/forget/recall（714行）✅
│
├── [G1] ingest.py             # G1 摄取门禁：格式校验 + 输入消毒（266行）✅
├── [G2] triage.py             # G2 分拣门禁：分类 + 评分 + 优先级（372行）✅
├── [G3] analyze.py            # G3 分析门禁：深度评估 + 矛盾检测（314行）✅
├── [G4] activate.py           # G4 激活门禁：INDEXED→VERIFIED + 审计触发（263行）✅
├── [G5] extract.py            # G5 提取门禁：知识提取 + 外部注入（361行）✅
│
├── batch_ingest.py            # 批量入库：Session Log→KE 自动提取（227行）✅
├── reranker.py                # 两阶段检索重排序：Cross-Encoder BGE-reranker-v2-m3（beta 新增）📋
├── graph_validator.py         # 图谱完整性校验：depends_on→DAG→深度≤3（275行）✅
├── embedding_migrate.py       # Embedding 模型迁移管线：升级/降级/回滚（313行）✅
│
└── _future/                   # 4 未来模块（规划中）
    ├── mcp_server_kb.py       # KB MCP Server 独立部署
    ├── query_understanding.py # Query expansion + 查询分解 + jieba分词优化
    ├── memory_consolidation.py# KE聚类 + 知识摘要 + 冗余检测
    └── decay_engine.py        # 知识衰减自动化引擎
    ├── knowledge_decay_engine.py  # 知识衰减自动检测
    └── cross_agent_consistency.py # 跨Agent知识一致性校验
```

> **✅ 表示 experimental 已实现**（12 个 Python 模块，约 3600 行代码）。

### 4.2 知识数据层（`docs/08_knowledge/`）——KE 物理文件

```
docs/08_knowledge/
├── index.md                        # 知识库总索引（由 validate_ke_index.py 自动维护）
│
├── track_a_vibe_coding/            # Track A：Vibe Coding 施工知识（8 类，§3.8）
│   ├── coding_convention/          # A1：编码约定
│   │   └── KE-{NNN}-{slug}.md
│   ├── architecture_decision/      # A2：架构决策
│   │   └── KE-{NNN}-{slug}.md
│   ├── governance_rule/            # A3：治理规则
│   │   └── KE-{NNN}-{slug}.md
│   ├── failure_pattern/            # A4：失败模式
│   │   └── KE-{NNN}-{slug}.md
│   ├── tool_configuration/         # A5：工具配置
│   │   └── KE-{NNN}-{slug}.md
│   ├── dependency_knowledge/       # A6：依赖知识
│   │   └── KE-{NNN}-{slug}.md
│   ├── workflow_pattern/           # A7：工作流模式
│   │   └── KE-{NNN}-{slug}.md
│   └── context_engineering/        # A8：上下文工程
│       └── KE-{NNN}-{slug}.md
│
├── track_b_finance/                # Track B：金融领域知识（7 类，§3.8）
│   ├── strategy_logic/             # B1：策略逻辑
│   │   └── KE-{NNN}-{slug}.md
│   ├── factor_design/              # B2：因子设计
│   │   └── KE-{NNN}-{slug}.md
│   ├── risk_management/            # B3：风险管理
│   │   └── KE-{NNN}-{slug}.md
│   ├── data_quality/               # B4：数据质量
│   │   └── KE-{NNN}-{slug}.md
│   ├── market_microstructure/      # B5：市场微观结构
│   │   └── KE-{NNN}-{slug}.md
│   ├── compliance/                 # B6：合规知识
│   │   └── KE-{NNN}-{slug}.md
│   └── backtest_methodology/       # B7：回测方法论
│       └── KE-{NNN}-{slug}.md
│
├── ko/                             # KO（Knowledge Observation）碎片层（§3.10）
│   ├── observed/                   # OBSERVED 状态——等待积累
│   │   └── KO-{NNN}-{slug}.md
│   ├── promoting/                  # PROMOTING 状态——等待 Owner 确认
│   │   └── KO-{NNN}-{slug}.md
│   └── discarded/                  # DISCARDED 状态——90d 后自动清理
│       └── KO-{NNN}-{slug}.md
│
├── kb/                             # KB（Knowledge Base Rule）规则层（§3.11）
│   ├── active/                     # ACTIVE 状态——当前生效规则
│   │   └── KB-{NNN}-{rule_name}.yaml
│   ├── superseded/                 # SUPERSEDED 状态——已被取代
│   │   └── KB-{NNN}-{rule_name}.yaml
│   └── retired/                    # RETIRED 状态——已废弃
│       └── KB-{NNN}-{rule_name}.yaml
│
└── _archive/                       # 归档层——REJECTED / ARCHIVED / SUPERSEDED 终态 KE
    └── KE-{NNN}-{slug}.md
```

> **为什么目录结构不是按 status 分层而是按 category 分层**：
> - category 是**静态属性**（一条 KE 的 category 不会变）→ 目录天然稳定
> - status 是**动态属性**（一条 KE 会从 DRAFT→VERIFIED→DEPRECATED）→ 会导致文件在不同目录间频繁移动
> - 对标：K8s CRD 按 kind 分组而非按 phase 分组 / Git 按内容类型分目录而非按"是否 merge"分目录
> - 例外：KO 和 KB 按 status 分目录——因为它们的状态变化频率低（OBSERVED→PROMOTING 是批量操作，非逐条移动）

##### 文件命名规范

| 实体 | 命名模式 | 示例 | 编号规则 |
|------|---------|------|---------|
| KE | `KE-{NNN}-{slug}.md` | `KE-042-ruff-over-pylint.md` | NNN = 3位全局递增编号（§3.2.1），`slug` = 标题的 kebab-case 缩写（≤40字符） |
| KO | `KO-{NNN}-{slug}.md` | `KO-015-ruff-vs-pylint-speed.md` | NNN = 3位独立递增编号（KE 和 KO 编号池独立，不共享） |
| KB | `KB-{NNN}-{rule_name}.yaml` | `KB-001-python-linter-must-be-ruff.yaml` | NNN = 3位独立递增编号，`rule_name` = snake_case（≤50字符） |

> **slug 生成规则**：取 title 的前 5 个有意义的英文/拼音词 → 转小写 → 用 `-` 连接 → 截断至 40 字符。中文标题先提取关键词拼音。目的：文件名人类可猜、AI 可解析、不会出现 `KE-042-%E4%B8%AD%E6%96%87.md` 的 URL 编码乱码。

### 4.3 ChromaDB 持久化层

```
src/zephyr/db/chroma/
├── chroma.sqlite3             # ChromaDB 元数据
└── {collection_id}/           # 每个 Collection 的向量持久化
    ├── data_level0.bin
    ├── header.bin
    ├── length.bin
    └── link_lists.bin
```

### 4.4 4 Collection 体系

| Collection | 存储内容 | 向量维度（当前） | 用途 |
|-----------|---------|:---:|------|
| `ke_entries` | 所有 KE 的向量 | 384d (all-MiniLM-L6-v2) | 知识语义检索 |
| `vibe_rules` | Vibe Coding 规则/护栏 | 384d | 规则语义匹配 |
| `blueprints` | 蓝图文档向量 | 384d | 蓝图检索 |
| `failure_patterns` | 失败模式/反模式 | 384d | 历史教训检索 |

> **Embedding 模型版本**：当前 2 默认 `all-MiniLM-L6-v2`（384d，ChromaDB 默认），中文场景降级到 `BGE-small-zh-v1.5`（512d），beta 目标 `BGE-M3`（1024d）。详见 [embedding_model_registry.yaml](file:///d:/ZephyrAlpha/src/zephyr/config/embedding_model_registry.yaml)。

---

## §5 核心流程：知识采集→分块→向量化→索引→检索→注入

### 5.1 总览：G1→G5 五门禁流水线

```
输入源                         门禁（Gate）                    产出
───────                        ──────────                    ────
Session Log
ADR            ──→ [G1 INGEST]  ──→ [G2 TRIAGE]  ──→ [G3 ANALYZE]
Blueprint          格式校验         分类+评分         深度评估
Candidate Pool     输入消毒         domain+layer     矛盾检测
外部论文            KE-ID分配       priority+tags    新鲜度计算
GitHub Repo         source追踪      质量评分          half_life

        ──→ [G4 ACTIVATE]  ──→ [G5 EXTRACT]
            激活+审计           知识提取
            INDEXED→            外部注入
            VERIFIED            批量处理
              │                     │
              ▼                     ▼
          上下文引擎              外部知识
          context_assembler       MCP Server
```

### 5.2 G1：摄取门禁（Ingest Gate — `ingest.py`）

**触发**：任何新知识进入系统时。

**检查内容**：

| 检查项 | 规则 | 失败后果 |
|--------|------|---------|
| 输入消毒 | SQL注入/命令注入/XSS模式检测 | REJECTED — 不安全输入不得进入系统 |
| 格式校验 | KE Schema 必填字段完整性 | SUBMITTED → 进入 G2 前先补字段 |
| KE-ID 分配 | `KE-{NNN}` 连续递增，不得跳号 | 阻断 — KE-ID 断裂会导致索引空洞 |
| 来源追踪 | `source_path` 必须指向真实存在的文件 | 阻断 — 虚构来源不得入库 |
| 编码合规 | UTF-8，无BOM，LF换行（AGENTS.md §4） | 阻断 — 编码不合规增加协作风险 |

> **对标**：ITIL SACM §4.5 — Configuration Audit（配置项格式合规性检查，入库前强制校验）。

### 5.3 G2：分拣门禁（Triage Gate — `triage.py`）

**触发**：G1 通过后。

**检查内容**：

| 检查项 | 规则 | 产出 |
|--------|------|------|
| 知识分类 | 六分类枚举：`blueprint_decision` / `best_practice` / `factor` / `failure_pattern` / `guardrail` / `architecture_decision` | `category` |
| domain分配 | 10域枚举（对齐 PS-STD-004 §5） | `domain` |
| layer分配 | 14层枚举（对齐 `VALID_LAYERS`：L00~L13） | `layer` |
| 优先级分配 | P0~P3 四级 | `priority` |
| 质量评分 | 0.0~1.0（基于来源权威性+内容完整性+时效性加权） | `quality_score` |
| 标签生成 | 5轴标签：fn/ly/md/st/mo（对齐 MOD-INF-006） | `tags` |
| 去重检测 | 与已有 KE 的向量相似度比较（>80% → 可能重复） | 去重建议 |
| 知识有效期 | TTL 设定 + `half_life_days` | TTL |

> **对标**：ISO 11179 §6.2 — Metadata Stewardship（元数据的领域归属和分类必须在入库前确定）。

### 5.4 G3：分析门禁（Analyze Gate — `analyze.py`）

**触发**：G2 通过后。

**检查内容**：

| 检查项 | 规则 | 产出 |
|--------|------|------|
| 深度评估 | 知识内容是否充分？是否有遗漏的上下文？ | 内容完整性评分 |
| 矛盾检测 | 与已有 KE 的语义矛盾检测（e.g. "用 ruff" vs "用 pylint"） | 矛盾报告 |
| 依赖分析 | `depends_on_ke` 引用的 KE 是否存在且状态≥INDEXED？ | 依赖链验证 |
| 新鲜度计算 | `freshness = 0.5 ^ (days_since_verified / half_life_days)` | 新鲜度评分 |
| 图谱连接性 | 入库后知识图谱是否产生孤立节点？ | 连通性报告 |
| CBAC 评估 | 知识是否涉及核心业务变更？需更高审批？ | 安全评级 |

### 5.5 G4：激活门禁（Activate Gate — `activate.py`）

**触发**：G3 通过后。

**检查内容**：

| 检查项 | 规则 | 产出 |
|--------|------|------|
| 状态流转 | REVIEWED→ACCEPTED→INDEXED（写入 ChromaDB + SQLite） | KE 状态更新 |
| 向量化 | 知识正文 → Embedding 模型 → 向量 → ChromaDB insert | 向量索引 |
| 审计触发 | 触发四模型审计流水线（§5.8） | 审计记录 |
| 索引更新 | 更新总索引 + 分类索引 + 标签索引 | 索引文件 |
| 通知消费者 | Tier 1 消费者通知（如有） | 通知记录 |

### 5.6 G5：提取门禁（Extract Gate — `extract.py`）

**触发**：外部知识提取需求 or Session Log 自动提取。

**检查内容**：

| 检查项 | 规则 | 产出 |
|--------|------|------|
| 知识提取 | 从 Session Log / ADR / Blueprint 中自动识别知识块 | 提取清单 |
| 外部注入 | MCP Resource 查询外部论文/代码仓库 → 提取知识 | 外部KE候选 |
| 批量处理 | `batch_ingest.py` 批量管道 | 批量入库报告 |
| 质量门控 | 自动提取的 KE 质量评分 < 0.6 → 标记 HUMAN_REVIEW | 人工审核标记 |

### 5.7 检索与注入流程

```
AI Session 启动
       │
       ▼
[context_assembler]  (MOD-INF-006 §5.1)
       │
       │  1. 解析当前任务（domain + layer + tags）
       │  2. 构建检索查询
       ▼
[unified_memory_api.recall()]
       │
       │  experimental 粗筛：向量语义检索 (ChromaDB ke_entries) → Top 50
       │  + 标签过滤 (SQLite)
       │
       ▼
[reranker.py]
       │
       │  beta 精排：Cross-Encoder (BGE-reranker-v2-m3)
       │  逐一打分 (query, each KE) → Top 10
       │  + 新鲜度排序
       │
       ▼
  Top-10 KE 列表（总 token ≤ 2000）
       │
       ▼
[context_injector]  注入到 AI 上下文
       │
       │  标注格式：
       │  > 📚 知识库提醒（KE-042）：[标题]
       │  > [正文摘要]
       │  > 来源：docs/08_knowledge/... | 新鲜度：87% | TTL：30d
       │
       ▼
  AI 开始执行任务（已携带相关历史知识）
```

**检索约束**：

- Top-K ≤ 10（避免上下文膨胀）
- 总注入 token ≤ 2000（约 5-8% 上下文预算）
- 新鲜度 < 50% 的 KE 标注 `⚠️ 此知识已超过半衰期，请验证当前是否仍然适用`
- 仅注入状态 ≥ INDEXED 的 KE

### 5.8 四模型审计流水线

**触发**：G4 Activate 时自动触发（或手动 `python kb_repo.py --audit KE-XXX`）。

```
[GLM-5.1 全景扫描]          识别缺口、分类正确性、KE-ID 连续性
       │
       ▼
[Kimi K2.6 根因深挖]        验证准确性、矛盾检测、关联图谱检查
       │
       ▼
[Qwen 3.6 Plus 落地执行]    去重、格式化、索引构建、图谱更新
       │
       ▼
[Opus 4.7 终局裁决]         元评审（评审前三轮本身）、质量评估、矛盾裁决、最终收口
       │
       ▼
  VERIFIED（四轮审计通过）
```

> **对标**：Validator-N（N=4）多模型交叉验证——单一模型的判断不可信，需要4个不同架构/训练数据的模型各自独立审计后投票。
> 大白话：一条知识入库前，让四个AI"评委"各自检查一遍。GLM负责"扫一眼看有没有大问题"，Kimi负责"深挖看有没有矛盾"，Qwen负责"实际操作写入"，Opus负责"终审——不仅审知识，还审前三个评委有没有审对"。四条独立的"防线"全部通过才算合格。
>
> **与脚本系统 12 维度审计的分工**：
> - **KB 四模型审计**：审计的是"知识条目本身是否准确、无矛盾、可检索"——关注知识的质量
> - **脚本系统 12 维度审计**：审计的是"项目文件是否合规、链接是否完整、代码是否安全"——关注项目的质量
> - **交叉点**：脚本系统 C5 知识沉淀产出的 KE 候选 → 进入 KB 的 G1→G5 门禁 → 经过四模型审计确认后成为 VERIFIED KE → KB 提取的知识（G5）反馈给脚本系统 C1 扫描规则升级（MOD-INF-005 §6.6）
> - **不重叠保证**：KB 审计不检查文件格式/链接/编码（那是脚本系统的事）；脚本系统不检查知识的准确性/矛盾/语义（那是 KB 四模型的事）

### 5.9 两阶段检索与重排序（Reranker）

**现状**：`recall()` 使用 ChromaDB 纯向量相似度排序——粗筛即终排。500 KE 时噪音显著。

**专业对标**：

| 机构 | 实践 | 核心洞察 |
|------|------|---------|
| **Meta FAIR** | Atlas / Fusion-in-Decoder | RAG 标准两阶段：bi-encoder（粗筛）+ cross-encoder（精排） |
| **Cohere** | Rerank API v3 | 逐一打分 `(query, doc)` pair，比纯向量相似度精确 15-30% |
| **Google Vertex AI** | Search→Ranking→Augmentation→Generation | Ranking 是四步中独立的一环，不可省略 |

**设计**：

```
recall() 升级为两阶段检索

experimental（粗筛）：ChromaDB 向量语义检索 → Top 50
       │
       ▼
beta（精排）：本地 Cross-Encoder 重排序 → Top 10
       │  模型：BGE-reranker-v2-m3（~200MB，支持中英双语）
       │  延迟：50条 × ~4ms/条 ≈ 200ms
       │        总召回+重排 < 500ms ✅ 可接受
       ▼
  Top 10 KE → 注入上下文
```

**与 ChromaDB 的集成方式**：
- experimental 保持现有 `kb_repo.query()` chrome 查询不变
- beta 在 `unified_memory_api.recall()` 中新增 `rerank()` 步骤
- 新模块：`src/zephyr/kb/reranker.py`——CrossEncoder 包装层

**降级策略**：
- 若 `BGE-reranker-v2-m3` 加载失败（首次运行需下载）→ 降级为纯 ChromaDB Top-10（当前行为）
- 若重排延迟 > 1s → 跳过重排，日志警告

> **对标**：Cohere Rerank API 是行业标准——"不重排的 RAG 就像不校对的书"。beta 500 KE 时不做重排，AI 拿到的 10 条 KE 中平均有 3-4 条不相关。
> 大白话：现在检索是"从书架拿前 10 本书"。升级后是"先拿 50 本，再仔细挑出真正有用的 10 本"。多花 0.2 秒，给 AI 的资料质量升一个档次。

### 5.10 知识切片机制（Knowledge Slicing）

**问题**：Session Log 可能 2000+ 行，但一条 KE 应该只包含一个独立的知识点。如何从长文档中自动切分出 KE 级别的知识块？

**对标**：

| 来源 | 机制 | 启发 |
|------|------|------|
| **LangChain Text Splitters** | `RecursiveCharacterTextSplitter`——按 `\n\n`→`\n`→`。`→` ` 优先级递归切分 | 段落边界优先于句子边界 |
| **Anthropic Contextual Retrieval** | 每个 chunk 前面拼接文档级上下文摘要 | chunk 独立可理解 |
| **Unstructured.io** | 按 title（标题层级）自动检测文档结构边界 | H2/H3 标题 = 天然知识边界 |

**切片策略**（五级边界信号，按优先级从高到低）：

| 优先级 | 边界信号 | 检测方式 | 示例 |
|:---:|---------|---------|------|
| 1 | **Markdown 标题** | `^#{1,3}\s+.+$` — H1/H2/H3 视为天然知识块边界 | `## 为什么选择 ChromaDB` → 新 KE 开始 |
| 2 | **显式分隔符** | `---` / `***` / `___` — 水平分隔线 | Session Log 中 `---` 切分不同话题 |
| 3 | **话题转换** | 相邻两段的向量余弦相似度 < 0.3 → 话题切换 | 一段在讲"ruff 配置"，下一段讲"SQLite Schema" |
| 4 | **时间跳变** | 时间戳间隔 > 30 分钟（仅 Session Log） | AI session 中途休息后换话题 |
| 5 | **字符硬上限** | KE body > 2000 字符 → 无论内容如何，强制切分 | 防止单条 KE 过大无法有效检索 |

**切片规则**：

| 规则 | 值 | 说明 |
|------|:---:|------|
| KE body 最小长度 | 200 字符 | 短于 200 字符的知识不够独立——合并到相邻 KE |
| KE body 最大长度 | 2000 字符 | 长于 2000 字符的 KE 检索精度下降——切分 |
| KE body 理想长度 | 500-800 字符 | 对应 ~200-300 tokens——检索精度和可读性的最佳平衡点 |
| Session Log→KE 提取比 | 2000 行 Log → ~15-25 KE | 不是每行都有知识——需要去噪 |

> **对标**：Anthropic Contextual Retrieval——每个 chunk 前面拼文档级摘要。我们的切片输出不仅是 `(ke_body, ke_id)`，还会自动附上来源文档的 `source_path` + 章节上下文，让 KE 脱离原文后仍可独立理解。
> 大白话：一篇文章扔进去，AI 自动按"标题 → 分隔线 → 话题转向 → 时间跳 → 字数上限"五种信号把它切成一片片"知识牛排"——每片刚好一口吃掉（500-800 字）。太小的合并，太大的再切。

### 5.11 五轨并行知识提取管道

**问题**：当前 `extract.py` 的 `EXTRACTION_TEMPLATES` 只覆盖 5 种 source_type（`blueprint` / `strategy` / `factor` / `best_practice` / `lesson_learned`）——和 §3.9 定义的 15 类 category 完全不匹配。提取不是"一个脚本跑一遍"，而是多轨并行、各有触发时机。

**对标**：

| 来源 | 提取机制 | 关键设计 |
|------|---------|---------|
| **Vasilopoulos Trigger Table** | 修改特定文件 → 自动路由到对应专家 agent → 该 agent 内置对应领域知识 | "constitution embeds trigger tables that route tasks to the appropriate specialized agent based on observable signals—primarily which files are being modified" |
| **OpenAI Harness** | AGENTS.md 作为动态反馈闭环——agent 每次失败后更新 AGENTS.md，下次自动加载 | "AGENTS.md as dynamic feedback loop — updated iteratively whenever agents encounter failures" |
| **n1n.ai Priority Classification** | 三级优先级决定提取后走向：HIGH→LTM / MID→MTM晋升 / LOW→丢弃 | `process_memory()`: 分类 → 按优先级写入不同层 |

**五轨设计**：

```
轨道1：Session Log 自动提取（session 结束时触发）
  ┌─────────────────────────────────────────────────────────┐
  │ auto-handoff-log.py 生成交接日志                         │
  │     │                                                    │
  │     ├─→ §5.10 五级切片 → 识别知识块边界                  │
  │     ├─→ 每块 → G1 Ingest（KE 格式校验）                  │
  │     ├─→ G2 Triage（分类）→ 分配 §3.9 category（A1-A8）   │
  │     │                                                    │
  │     │  优先级 HIGH（A1-A4）→ 直接创建 KE                  │
  │     │  优先级 MID（A5-A8）→ 创建 KO-{NNN}                  │
  │     │  优先级 LOW → 丢弃                                  │
  │     │                                                    │
  │     └─→ HIGH: KE-{NNN} 直接入库 ChromaDB+SQLite           │
  │         MID:  KO-{NNN} → 等待同类聚合≥3条 → D0流水线→KE   │
  └─────────────────────────────────────────────────────────┘

轨道2：门禁阻断自动记录（pre-commit/CI 失败时触发）
  ┌─────────────────────────────────────────────────────────┐
  │ ruff check FAIL / mypy error / pytest FAILED             │
  │     │                                                    │
  │     ├─→ G1 Ingest：提取 错误类型+修复方法+耗时           │
  │     ├─→ G2 Triage → category: A4（failure_pattern）      │
  │     │    priority: HIGH → 直接 KE                         │
  │     ├─→ 同类 KE ≥ 3 条（向量聚类检测）→ D0 四轮流水线     │
  │     │    → 聚合为一条"该错误类型完整知识"                  │
  │     │    → old KE: SUPERSEDED                             │
  │     └─→ KE-{NNN} 入库                                    │
  └─────────────────────────────────────────────────────────┘

轨道3：决策记录 + 蓝图变更提取（聊天中检测到决策信号 / 蓝图 version bump 时触发）
  ┌─────────────────────────────────────────────────────────┐
  │ 决策信号检测 / bp version changed                          │
  │     │                                                    │
  │     ├─→ G1 Ingest：用 per-source-type templates 提取      │
  │     ├─→ G2 Triage → category:                            │
  │     │    ADR            → A2（architecture_decision）     │
  │     │    蓝图/治理标准   → A3（governance_rule）          │
  │     │    工具配置        → A5（tool_configuration）       │
  │     ├─→ priority: HIGH → 直接 KE                          │
  │     └─→ KE-{NNN} 入库                                    │
  └─────────────────────────────────────────────────────────┘

轨道4：外部知识注入（Track B 主入口，Owner 手动触发或定时批量）
  ┌─────────────────────────────────────────────────────────┐
  │ arXiv 论文 / GitHub 开源 / 券商报告 / 监管文件            │
  │     │                                                    │
  │     ├─→ D0 四轮知识管理流水线（011 GLM→022 Kimi→033 Qwen→044 Opus）│
  │     │                                                      │
  │     │   experimental（011 GLM）：  从原文提取知识块 → KO 草稿  │
  │     │   beta（022 Kimi）： 结构化——补全 category/tags  │
  │     │   beta（033 Qwen）： 索引——写入 ChromaDB+SQLite  │
  │     │   stable（044 Opus）： 终审——检查与前3轮的一致性   │
  │     │                                                      │
  │     ├─→ G2 Triage → category: B1-B7                       │
  │     ├─→ priority: HIGH(B1-B3) → 直接 KE / MID(B4-B7) → KO 队列│
  │     └─→ KE-{NNN} 或 KO-{NNN} 入库                         │
  └─────────────────────────────────────────────────────────┘

轨道5：知识差距自动巡检（每周 cron / APScheduler 定时触发）
  ┌─────────────────────────────────────────────────────────┐
  │ 每周触发一次 detect_knowledge_gaps.py：                   │
  │                                                          │
  │   检查1：search_log → query 返回 0 结果的 query 是什么？  │
  │          → 创建 KO：KB-GAP-{date}-{query_hash}            │
  │                                                          │
  │   检查2：failure_feedback → 哪种错误类型反复出现？        │
  │          → 若该错误无对应 KE → KO 待补                    │
  │                                                          │
  │   检查3：AGENTS.md rule 交叉比对 → 每条规则是否已有 KE？  │
  │          → 比对 AGENTS.md frontmatter section ↔ KE SQLite │
  │          → 缺 KE 的规则 → KO 待补                          │
  │                                                          │
  │   检查4：new files in src/zephyr/ → 是否有对应蓝图？      │
  │          → 有蓝图但无 KE → KO 待补                        │
  │                                                          │
  │   输出：gap_report_{date}.md → Owner 审阅                 │
  └─────────────────────────────────────────────────────────┘
```

**EXTRACTION_TEMPLATES 扩展**（15 类 → 15 模板）：

```python
# extract.py EXTRACTION_TEMPLATES（beta 更新为 15 模板）
EXTRACTION_TEMPLATES: dict[str, dict[str, list[str]]] = {
    # Track A — Vibe Coding 施工知识提取模板
    "session_log": {
        "fields": [
            "failure_patterns",     # → A4: 从 Session Log 末段提取 AI 纠结/翻车事件
            "tool_insights",        # → A5: "我今天发现 ruff vs pylint..."
            "workflow_changes",     # → A7: "Session 启动顺序应该调整为..."
            "context_decisions",    # → A8: "我把 hot memory 上限设为 400 行"
        ],
    },
    "adr": {
        "fields": [
            "decision_rationale",   # → A2: "为什么选 X 不选 Y"
            "alternatives",         # → A2: "考虑过哪些其他方案"
            "consequences",         # → A2: "这个决策带来了什么后果"
        ],
    },
    "governance_document": {
        "fields": [
            "governance_rule",      # → A3: 从 AGENTS.md / PS-* 提取新规则
            "rule_scope",           # → A3: 规则适用范围
            "trigger_condition",    # → A3: 触发条件（何时强制执行）
        ],
    },
    "precommit_failure": {
        "fields": [
            "error_signature",       # → A4: 错误签名（标准化后用于聚类）
            "error_type",           # → A4: ruff/mypy/pytest/import
            "fix_method",           # → A4: 怎么修好的
            "time_cost_minutes",    # → A4: 修它花了多久
        ],
    },
    "dependency_migration": {
        "fields": [
            "package_name",         # → A6
            "from_version",         # → A6
            "to_version",           # → A6
            "breaking_changes",     # → A6
            "migration_steps",      # → A6
        ],
    },
    # Track B — 金融领域知识提取模板
    "academic_paper": {
        "fields": [
            "strategy_description", # → B1: 策略核心逻辑
            "factor_definition",    # → B2: 因子计算公式
            "risk_framework",       # → B3: 风控框架
            "backtest_results",     # → B7: 作者回测数据
        ],
    },
    "market_data_experience": {
        "fields": [
            "data_source",          # → B4: 数据来源
            "quality_issue",        # → B4: 发现的数据质量问题
            "cross_validation",     # → B4: 交叉验证结果
        ],
    },
    "regulatory_document": {
        "fields": [
            "compliance_requirement",# → B6
            "regulator",            # → B6
            "deadline",             # → B6
            "penalty",              # → B6
        ],
    },
    "trading_experience": {
        "fields": [
            "market_rule",          # → B5: 市场规则发现
            "market",               # → B5
            "impact_on_strategy",   # → B5
        ],
    },
}
```

### 5.12 四层防遗漏哨兵体系

> 对标：Vasilopoulos Trigger Table —— "automatic routing removes the burden of the developer remembering which agent to invoke" + vibe-init 治理引擎 —— "每条治理策略自动对应 KE"

| 层 | 哨兵 | 实现位置 | 检查频率 | 对标 |
|:--:|------|---------|:---:|------|
| **L1** | **Trigger Table**（触发式推送） | `context_assembler.py` → `unified_memory_api.recall()` 新增参数 `trigger_context` | 每次 AI 施工任务启动 | Vasilopoulos: "trigger tables that route tasks based on observable signals—primarily which files are being modified" |
| **L2** | **Coverage Gap Analyzer**（搜索日志分析） | `detect_knowledge_gaps.py`（beta 新增脚本） | 每周一次 | Google Vertex AI: "context_recall — whether all relevant KEs were retrieved" |
| **L3** | **Rule-to-KE Sync Check**（规则对齐） | `detect_knowledge_gaps.py` L3 检查 | 每周一次 + AGENTS.md 变更时立即触发 | vibe-init: "every governance strategy maps to a KE" |
| **L4** | **Quarterly Audit**（人工季度抽检） | 人工流程（非自动化脚本）| 每季度 | ITIL SACM: "Configuration Items must be periodically audited" |

**L1 Trigger Table 工程细节**（对标 Vasilopoulos）：

```yaml
# trigger_table.yaml — beta 新增
# 定义"修改哪些文件 → 加载哪些 KE"的映射关系
triggers:
  - file_pattern: "src/zephyr/kb/**/*.py"
    force_recall_categories: [A1, A2, A4]
    context_hint: "你正在修改知识库模块的代码——以下是 3 条相关 KE"

  - file_pattern: "src/zephyr/shared/schemas.py"
    force_recall_categories: [A2, A6]
    context_hint: "你正在修改 Schema 定义——注意 dependencies 和 version 约束"

  - file_pattern: "justfile"
    force_recall_categories: [A5, A7]
    context_hint: "你正在修改构建配置——确保和 pyproject.toml 中定义的 CI 规则一致"

  - file_pattern: "docs/01_policies_and_standards/**/*.md"
    force_recall_categories: [A3, A8]
    context_hint: "你正在修改治理标准——所有联动文件必须在同一 atomic batch 更新"

  - file_pattern: "src/zephyr/l09/**/*.py"
    force_recall_categories: [B1, B2, B3, B7]
    context_hint: "你正在修改研究/策略模块——以下是相关因子和回测方法论 KE"
```

**L2 Coverage Gap 工程细节**：

```python
# detect_knowledge_gaps.py — beta 新增（伪代码骨架）
def analyze_coverage_gaps(search_log: SearchLog, ke_index: KEIndex) -> GapReport:
    gaps = []

    # 检查1：搜索日志 → 零结果 query
    zero_result_queries = [
        entry.query for entry in search_log.entries
        if entry.result_count == 0
    ]
    for query in set(zero_result_queries):  # 去重
        gaps.append(Gap(
            type="zero_result_query",
            query=query,
            severity="HIGH" if query in zero_result_queries[-7:] else "MEDIUM",  # 最近一周的 HIGH
            suggestion=f"创建 KO 待补：{query[:80]}"
        ))

    # 检查2：AGENTS.md rules ↔ KE 覆盖
    agentsmd_rules = extract_rules_from_agentsmd()  # 正则提取 §N.N 规则
    ke_catalog = set(ke_index.list_all_ke_ids())
    for rule in agentsmd_rules:
        if not any(rule.ref in ke.depends_on for ke in ke_index.find_by_rule_ref(rule)):
            gaps.append(Gap(
                type="rule_not_in_ke",
                rule_ref=rule.ref,
                severity="MEDIUM",
                suggestion=f"AGENTS.md {rule.ref} 无对应 KE——创建 KO 待补"
            ))

    # 检查3：蓝图 ↔ KE 覆盖
    for bp in list_all_blueprints():
        related_kes = ke_index.find_by_source_doc(bp.file_path)
        if len(related_kes) == 0 and bp.status == "active":
            gaps.append(Gap(
                type="active_blueprint_without_ke",
                blueprint_id=bp.module_id,
                severity="LOW",
                suggestion=f"蓝图 {bp.module_id} 活跃但无对应 KE——可选补充"
            ))

    return GapReport(gaps=gaps, generated_at=datetime.now())
```

**L4 季度抽检 SOP**：

| 步骤 | 操作 | 输出 |
|:---:|------|------|
| 1 | 随机抽取最近 10 条 Session Log | Session Log 样本列表 |
| 2 | 逐条读取 → 人工标记"哪些应该被提取为 KE" | Expected KE 清单 |
| 3 | SQLite 查询实际提取结果：`SELECT ke_id, category FROM knowledge_entries WHERE source_session_id IN (...)` | Actual KE 清单 |
| 4 | Expected vs Actual 对比 → 计算 Recall（提取率）| Recall = Actual KE / Expected KE |
| 5 | Recall < 80% → 检查 extract.py 模板是否需要调整 → 更新蓝图 §5.11 | 治理改进工单 |

> **对标**：五轨并行提取是 Vasilopoulos "trigger-based routing" + OpenAI "AGENTS.md as dynamic feedback loop" + n1n.ai "priority-based classification" + Google Vertex AI "context_recall gap analysis" + ITIL SACM "quarterly configuration audit" 的融合投射。
> 大白话：知识不是"等着被提取"——五条轨道像五条传送带，各自在不同时机自动启动。Session 跑完→轨道1自动运转；提交失败→轨道2自动记录；决策信号→轨道3自动触发；外部资料→轨道4自动触发（零 Owner 手动）；每周一次→轨道5自动巡检"还缺什么"。四层哨兵确保——哪怕一条知识该被提取但五轨全漏了，季度抽检也能兜底抓到。

### 5.13 全自动提取策略：零 Owner 手动触发

**核心理念**：Owner 不应该"记得触发提取"——所有提取由事件驱动，100% 自动。Owner 的唯一动作是：面对系统自动推送的审批提醒，回复 yes/no。

#### 5.13.1 自动触发链全景

```
事件源                       检测方式                      提取链              Owner
───────                     ─────────                    ──────              ─────
Session 结束        →  auto-handoff-log.py             → G1-G5 → KO/KE      零
                       (git post-commit hook)

git commit 成功     →  L3 Rule-KE Sync                 → KO                 零
                       (git post-commit hook)

git commit 失败     →  pre-commit failure capture       → G1-G2 → KE(A4)     零
                       (pre-commit hook stderr)

ADR.status          →  ADR status watcher              → G1-G5 → KE(A2)     零
→ ACCEPTED              (git hook + YAML parse)

bp version bump    →  bp version watcher               → G1-G5 → KE(A2/A3)  零
                       (git hook + frontmatter diff)

arXiv/GitHub 出现   →  regex detect in session         → D0 → KO(B1-B7)     审批
                       body: arxiv.org/abs/*           → 推送 "3条待审批"     (yes/no)
                       github.com/*/*

每周一 09:00        →  APScheduler cron                → detect_knowledge_   仅查看
                       detect_knowledge_gaps.py        → gaps 生成+推送
```

#### 5.13.2 关键触发器工程细节

**触发器A：auto-handoff-log.py → 轨道1（session 结束，git post-commit hook 驱动）**

```python
# .git/hooks/post-commit（install-hooks.py 自动安装，零 Owner 操作）
def post_commit_hook():
    marker = "docs/19_development_workspace/session-logs/handoff-current.md"
    if not os.path.exists(marker):
        return  # 不是 session 结束 commit → 跳过

    # 1. 自动生成 Session Log（§3.9.3 YAML 格式）
    handoff = auto_handoff_log.generate()

    # 2. 自动 §5.10 五级切片
    chunks = knowledge_slicer.slice(handoff)

    # 3. 自动 G1-G5 五门禁管道
    ke_count, ko_count = 0, 0
    for chunk in chunks:
        result = ingest_pipeline.run(chunk)  # §5.1-5.6: Ingest→Triage→Analyze→Activate→Extract
        if result.entity_type == "KE":
            ke_count += 1
        else:
            ko_count += 1

    # 4. 自动归档
    archive_handoff(handoff)
    logger.info(f"[轨道1] 完成: {len(chunks)} slices → {ke_count} KE + {ko_count} KO")
```

**触发器B：pre-commit failure → 轨道2（门禁阻断自动吸收）**

```python
# .git/hooks/pre-commit 追加（阻断后 stderr 自动解析）
# ruff error / mypy error / pytest FAIL → 自动生成 failure_pattern KO

def on_precommit_failure(exit_code: int, stderr: str) -> None:
    if exit_code == 0:
        return
    failure = FailureSignature.from_stderr(stderr)
    # failure.error_type: "ruff_E501" / "mypy_attr_error" / "pytest_import_error"
    # failure.root_cause: "line too long" / "module not found"
    # failure.fix_method: "truncate line" / "add __init__.py"
    ko = KnowledgeObservation(
        category="A4_failure_pattern",
        body=f"### {failure.error_type}\n\n"
             f"- **根因**：{failure.root_cause}\n"
             f"- **修复**：{failure.fix_method}\n"
             f"- **耗时**：{failure.time_cost_minutes} min\n"
             f"- **来源**：pre-commit hook stderr",
        priority="HIGH",
        source="precommit_failure",
    )
    kb_repo.save_ko(ko)
    logger.info(f"[轨道2] {failure.error_type} → KO-{ko.id}")
```

**触发器C：arXiv/GitHub 链接自动检测 → 轨道4（外部知识自动注入）**

```python
# batch_ingest.py §5.11 轨道4 扩展：扫描 session 日志 body 中的学术/GitHub 链接
ARXIV_PATTERN = r'https?://arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})'
GITHUB_PATTERN = r'https?://github\.com/([^/\s]+)/([^/\s]+)'

def detect_external_sources(session_log_body: str) -> list[ExternalSource]:
    sources = []
    for m in re.finditer(ARXIV_PATTERN, session_log_body):
        sources.append(ExternalSource(type="arxiv", paper_id=m.group(1)))
    for m in re.finditer(GITHUB_PATTERN, session_log_body):
        sources.append(ExternalSource(type="github", owner=m.group(1), repo=m.group(2)))
    return sources

def auto_ingest_external(source: ExternalSource) -> None:
    # 1. 自动抓取
    paper_text = fetch_arxiv(source.paper_id) if source.type == "arxiv" else fetch_github_readme(source.owner, source.repo)
    if not paper_text:
        return  # 网络失败 → 静默跳过，不打扰 Owner

    # 2. D0 四轮流水线自动运转（011 GLM→022 Kimi→033 Qwen→044 Opus）
    ko_drafts = d0_pipeline.run(paper_text)  # output: list[KnowledgeObservation]

    # 3. 自动推送审批提醒（仅当 ko_drafts 非空）
    if ko_drafts:
        notify_owner(
            title=f"[KB] {source.type} {source.identifier} — {len(ko_drafts)} 条新知识待审批",
            body=format_ko_summary(ko_drafts),
            actions=["yes（入库）", "no（全部丢弃）"]
        )
    # Owner 回复 "yes" → ko_drafts 每条自动走 G1-G5 → KE 入库
    # Owner 回复 "no"  → 全部丢弃
    # Owner 7d 无回复 → 自动过期清理（KOTTL=30d override 外部来源: 7d）
```

#### 5.13.3 自动调度表（APScheduler cron）

```python
# scheduler.py — beta 新增
# BackgroundScheduler 随 app 进程启动

jobs = {
    "weekly_gap_scan": {
        "trigger": "cron", "day_of_week": "mon", "hour": 9, "minute": 0,
        "func": "detect_knowledge_gaps.run_full_scan",
        "desc": "每周一早9点自动跑四维覆盖率检查(§5.12 L2)",
    },
    "monthly_ko_cleanup": {
        "trigger": "cron", "day": 1, "hour": 3, "minute": 0,
        "func": "ko_cleanup.expire_stale_kos",
        "desc": "每月1日3:00清理30天未晋升的KO",
    },
    "daily_decay_update": {
        "trigger": "cron", "hour": 2, "minute": 0,
        "func": "freshness_engine.update_all",
        "desc": "每日2:00跑全量KE新鲜度衰减",
    },
}
```

#### 5.13.4 Owner 月耗时预算

| 事项 | 触发 | Owner 动作 | 月耗时 |
|------|------|----------|:---:|
| 外部知识审批 | 自动检测→自动 D0→推送提醒 | yes/no | ≤ 5 min |
| 周度差距查看 | 每周一早9点自动推送 | 扫一眼报告 | ≤ 10 min |
| 季度抽检（L4）| 每季度日历提醒 | 10条Sample→人工标→对比 | 10 min/月均 |
| **月度总计** | | | **~25 min** |

---

> **对标**：Horthy Harness→"session handoff auto-generated via git hook"（Session Log 由 git hook 零人驱动）+ vibe-init→"every governance strategy auto-maps to KE"（规则→KE 全自动）+ n1n.ai→"priority-based auto-routing"（优先级自动路由，无需人工分类）+ Vasilopoulos→"trigger tables route tasks automatically, removing the burden of the developer remembering which agent to invoke"。
> 大白话：Owner，你唯一要做的事——看到系统推送"3 条新知识待审批"时，回个 "yes" 或 "no"。每月总共花你 25 分钟。其他一切：session 跑完了→自动记录（git hook）；提交失败了→自动吸收教训（pre-commit hook）；论文链接出现了→自动跑 D0 流水线（regex detect）；周一到 9 点→自动巡检"还缺什么"（APScheduler cron）。

---

### 6.1 context_assembler 集成

**接口定义**（KB → 上下文引擎）：

| 接口 | 调用方 | 方法 | 输入 | 输出 |
|------|--------|------|------|------|
| `recall()` | `context_assembler` | `unified_memory_api.recall()` | `query: str, domain: str, layer: str, max_results: int = 10` | `List[KE]`（按新鲜度+相关性排序） |
| `remember()` | AI session结束 | `unified_memory_api.remember()` | `KE Schema dict` | `bool`（成功/失败） |
| `learn()` | 反馈闭环 | `unified_memory_api.learn()` | `feedback: dict` | `bool` |

**调用时机**：

1. **AI Session 开始时**：`context_assembler` 调用 `recall()`，传入当前任务描述 + domain + layer
2. **AI 执行中发现知识缺口**：调用 `recall()` 补充
3. **AI Session 结束时**：调用 `remember()` 保存本次学到的新知识
4. **门禁阻断/验证失败**：调用 `learn()` 记录失败模式

### 6.2 KB 施工任务追踪

KB 系统自己的施工任务使用 MOD-INF-006 的 TaskCard 格式追踪：

```yaml
task_id: "KB-INF-0001"
namespace: "KB"
title: "实现 ChromaDB 4 Collection 初始化"
blueprint_ref: "MOD-KB-001 §7.2"
status: verified
priority: P0
tags:
  - fn:infra
  - ly:cross_layer
  - md:chromadb
  - st:initialization
  - mo:kb-construction
```

**task_id 格式对齐**：

- KB 施工任务 = `KB-INF-{NNNN}`（4位序号）
- 对齐 MOD-INF-006 的 `{NAMESPACE}-{SEQ}` 格式
- NAMESPACE = `KB`（知识库），SEQ = 4位数字

### 6.3 状态机区分

| 关注点 | 知识条目（KE）状态机 | 任务（TaskCard）状态机 | 说明 |
|--------|-------------------|---------------------|------|
| 定义位置 | 本蓝图 §3.3 | MOD-INF-006 §4.2 | KE有独立的状态机 |
| 状态数 | 10 | 10 | 数量相同，语义不同 |
| 终态 | REJECTED / ARCHIVED / SUPERSEDED | VERIFIED / CANCELLED | 知识终态≠任务终态 |
| 关系 | KE 是"知识资产" | TaskCard 是"施工单元" | KE管理知识，TaskCard管理施工 |

**规则**：KE 有自己的一致性状态机（KNOWLEDGE 域）；但 KB 施工任务（建设 KB 系统本身的工作）使用 MOD-INF-006 的 TaskCard 状态机。两者不混淆。

### 6.4 从脚本系统接收 MEDIUM Finding（C4→G1 数据流）

> 对标 MOD-INF-005 §6.3 + §6.6——脚本系统的 C4 跟踪阶段将 MEDIUM Finding 路由至知识库。

**接收接口**（脚本系统 → KB）：

| 触发方 | 触发条件 | KB 入口 | 处理流程 |
|--------|---------|---------|---------|
| 脚本系统 `run_all.py` C4 阶段 | Finding severity = MEDIUM | `G1 INGEST`（`ingest.py`） | MEDIUM Finding → KE Schema 转换 → ingress → G2 Triage |
| 脚本系统 C5 知识沉淀 | 失败模式 / 经验教训 | `G3 ANALYZE`（`analyze.py`） | 失败模式 → 矛盾检测 + 关联已有 KE |
| 脚本系统 C5 知识沉淀 | 蓝图决策 / 最佳实践 | `G2 TRIAGE`（`triage.py`） | 知识块 → 六分类 + domain/layer 分配 |

**数据格式转换**（Finding → KE Schema）：

```python
# Finding (MOD-INF-005) → KE (MOD-KB-001) 映射
finding_to_ke = {
    "ke_id": auto_assign(),              # KE-{NNN} 自动分配
    "title": finding.get("check_name"),
    "body": f"## 问题\n{finding.message}\n\n## 来源\n- 脚本：{finding.script}\n- 维度：{finding.dimension}",
    "category": severity_to_category(finding.severity),  # MEDIUM→best_practice, HIGH→failure_pattern
    "source_type": "script_finding",
    "source_path": finding.get("file"),
    "quality_score": 0.7,                # 脚本产出默认质量评分
    "priority": severity_to_priority(finding.severity),  # MEDIUM→P2
}
```

> **大白话**：脚本系统找到的 MEDIUM 问题，不走"创建任务卡阻断施工"那条路，而是存进知识库变成一条可检索的 KE。下次 AI 施工前查知识库就能看到"以前这里有过这个问题"。

---

## §7 存储方案

### 7.1 三层存储架构

| 层 | 存储 | 消费者 | 查询方式 |
|:--:|------|--------|---------|
| L3 知识层 | `docs/08_knowledge/` Markdown 文件 | 人类阅读 + AI 全文消费 | 文件读取 / grep |
| L2 向量层 | ChromaDB 嵌入式（4 Collection） | AI 语义检索 | 向量相似度 |
| L1 元数据层 | SQLite（`kb_state` + `kb_state_log` + `knowledge_entries`） | 状态机 + CI/pre-commit | SQL 查询 |

### 7.2 ChromaDB 选型与配置

**选型决策**（来自 ADR-0031 + `01-脚本系统架构.md` §三十二）：

| 维度 | 选择 | 理由 |
|------|------|------|
| **向量数据库** | **ChromaDB 嵌入式** | pip install 即可，零运维，Windows 完美支持，10万级向量足够 |
| **Python Client** | `chromadb==0.5.x`（官方） | 原生 API，无需额外依赖 |
| **持久化** | 本地文件（`src/zephyr/db/chroma/`） | 零配置，单人项目足够 |
| **距离度量** | cosine（余弦相似度） | 标准语义相似度计算 |
| **备选方案** | Qdrant（Docker/WSL） | 仅在向量 > 10万 or 检索延迟 > 500ms 时评估 |

**ChromaDB vs Qdrant 对比**：

| 维度 | ChromaDB 嵌入式 | Qdrant 自托管 |
|------|:---:|:---:|
| 部署复杂度 | pip install 即可 | 需 Docker 或二进制部署 |
| 运维成本 | 零 | 需监控、备份、升级 |
| 10万级向量 | ✅ 足够 | ✅ 更优 |
| Windows 支持 | ✅ 完美 | ⚠️ 需 WSL/Docker |
| Python 集成 | 原生 API | 官方 Python client |

> **2 决策**：ChromaDB 嵌入式。触发迁移到 Qdrant 的条件：向量数量 > 10万 or 检索延迟 > 500ms。

### 7.3 Embedding 模型选型

| 阶段 | Embedding 模型 | 向量维度 | 模型大小 | 适用场景 | MTEB中文 |
|------|--------------|:---:|------|---------|:---:|
| **beta 当前** | all-MiniLM-L6-v2（ChromaDB 默认） | 384 | ~80MB | 英文为主、快速原型 | N/A |
| **beta 中文** | BGE-small-zh-v1.5（降级启用） | 512 | ~100MB | 中文语义检索 | 62.3 |
| **beta 目标** | BGE-M3（多语言+稠密+稀疏混合） | 1024 | ~2GB | 生产级多语言、高精度 | 67.8 |

**升级触发条件**：
- all-MiniLM → BGE-small：中文语义检索召回率 < 70%
- BGE-small → BGE-M3：检索准确率 < 80%（人工评估）

> **历史冲突**（`知识库专题讨论文档.md` §KB-005）：ADR-0005 说用 `all-MiniLM`，ADR-0016 说用 `BGE-M3`。**裁决**：beta 以代码实现为准（`chromadb_init.py` 用 `all-MiniLM-L6-v2`），beta 升级到 BGE-M3。
> **多语言支持**：BGE-M3 原生支持中英混合检索，无需额外语言检测或翻译层。beta 中文场景降级启用 `BGE-small-zh-v1.5`，beta 统一升级 BGE-M3 后自动获得多语言能力——当前无需额外设计。

### 7.4 Reranker 模型选型

| 维度 | 选择 | 理由 |
|------|------|------|
| **模型** | **BGE-reranker-v2-m3**（BAAI，Hugging Face 开源） | 支持中英双语，MTEB reranking 排名 top-3 |
| **模型大小** | ~200MB（下载后本地缓存） | 首次运行需下载，之后本地零延迟 |
| **Cross-Encoder** | 是（`query + each KE` 逐对打分） | 精度远超 bi-encoder 的向量相似度 |
| **延迟** | ~4ms/pair × 50 pairs ≈ 200ms | 总检索+重排 < 500ms |
| **Python Client** | `sentence-transformers==2.2.x`（已有依赖） | 与现有技术栈一致，无需新依赖 |

**降级策略**：若首次下载失败 → `recall()` 降级为纯 ChromaDB Top-10（当前行为），日志警告。

### 7.5 SQLite 元数据 Schema

```sql
-- kb_state：当前KE状态
CREATE TABLE kb_state (
    ke_id       TEXT PRIMARY KEY,
    status      TEXT NOT NULL CHECK(status IN (
        'DRAFT','SUBMITTED','REVIEWED','ACCEPTED',
        'INDEXED','VERIFIED','REJECTED',
        'DEPRECATED','ARCHIVED','SUPERSEDED'
    )),
    quality_score REAL DEFAULT 0.0,
    freshness    REAL DEFAULT 1.0,
    half_life_days INTEGER DEFAULT 0,
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL,
    last_verified_at TEXT
);

-- kb_state_log：状态流转审计日志
CREATE TABLE kb_state_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ke_id       TEXT NOT NULL,
    from_status TEXT,
    to_status   TEXT NOT NULL,
    triggered_by TEXT,
    reason      TEXT,
    recorded_at TEXT DEFAULT (datetime('now'))
);

-- knowledge_entries：完整KE元数据
CREATE TABLE knowledge_entries (
    ke_id        TEXT PRIMARY KEY,
    title        TEXT NOT NULL,
    body         TEXT NOT NULL,
    category     TEXT NOT NULL,
    domain       TEXT NOT NULL,
    layer        TEXT NOT NULL,
    source_type  TEXT NOT NULL,
    source_path  TEXT NOT NULL,
    status       TEXT NOT NULL,
    quality_score REAL DEFAULT 0.0,
    priority     TEXT DEFAULT 'P2',
    tags         TEXT DEFAULT '[]',
    ttl          TEXT DEFAULT 'permanent',
    half_life_days INTEGER DEFAULT 0,
    freshness   REAL DEFAULT 1.0,
    supersedes_ke TEXT DEFAULT '[]',
    audit_chain  TEXT DEFAULT '[]',
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL,
    last_verified_at TEXT,
    usage_count  INTEGER DEFAULT 0,
    adoption_count INTEGER DEFAULT 0,
    helpfulness_score REAL DEFAULT 0.5,
    last_used_at TEXT
);
```

### 7.6 三层存储同步机制（MD ↔ SQLite ↔ ChromaDB）

**核心理念**：三层存储不是各自独立的——它们之间存在明确的**派生关系**和**同步闸门**。Markdown 文件是 canonical 真源，SQLite 是一级缓存（结构化查询），ChromaDB 是二级缓存（语义检索）。

**派生链**：

```
Markdown 文件          SQLite              ChromaDB
(canonical 真源)  →   (一级缓存)     →    (二级缓存)
docs/08_knowledge/    kb_state +          ke_entries
KE-{NNN}.md           knowledge_entries   Collection

     ↑ 最高权威            ↑ 中间层            ↑ 最远派生
     冲突时以此为准
```

##### 7.6.1 同步闸门矩阵

| 操作 | MD→SQLite | SQLite→MD | SQLite→ChromaDB | ChromaDB→SQLite |
|------|:---:|:---:|:---:|:---:|
| KE 文件新建 | ✅ G1 Ingest 自动写入 | — | — | — |
| KE frontmatter 字段修改 | ✅ G1 Ingest 自动更新 | — | — | — |
| KE.status→INDEXED | — | — | ✅ `activate.py` 自动 upsert 向量 | — |
| KE.status→DEPRECATED | — | — | ✅ `activate.py` 自动 delete 向量 | — |
| KE body 修改（如质量升级） | ✅ 自动同步 | — | ✅ 自动 re-embedding | — |
| KE status 由 CI 变更 | — | ✅ 自动回写文件 frontmatter | — | — |
| 运行时字段变更（usage_count 等） | — | — | ❌ 仅 SQLite 内部更新 | — |

##### 7.6.2 一致性校验闸门（CI 自动执行）

| 闸门 | 检查内容 | 频率 | 失败后果 |
|:---:|------|:---:|------|
| **GATE-MD-SQL** | 扫描所有 `docs/08_knowledge/track_*/**/*.md` → 逐文件解析 frontmatter → 比对 SQLite `knowledge_entries` 中对应记录 | 每周 CI cron | 🔴 不一致 → CI 失败：列出所有漂移项 + 自动修复方案（以 MD 为准覆盖 SQLite） |
| **GATE-SQL-CHROMA** | 扫描 SQLite 中所有 `status=INDEXED\|VERIFIED` 的 KE → 逐条查询 ChromaDB `ke_entries` 是否存在 | 每周 CI cron | 🔴 缺失 → 自动 re-embedding（`embedding_migrate.py` reindex 模式） |
| **GATE-ORPHAN-CHROMA** | 扫描 ChromaDB `ke_entries` 中所有向量 → 反向查询 SQLite 中是否存在且 status 仍为 INDEXED\|VERIFIED | 每周 CI cron | 🟡 孤向量 → 自动清理（状态已变但 ChromaDB 未删除的遗留向量） |
| **GATE-FILE-COUNT** | 统计 `docs/08_knowledge/` 下各 category 的文件数 → 比对 SQLite 中各 category 的记录数 | 每周 CI cron | 🔴 不一致 → 列出差异清单 |
| **GATE-FRONTMATTER** | 扫描所有 .md 文件 frontmatter 是否符合 §3.2.2 格式规则 F-01~F-06 | 每次 pre-commit | 🔴 违规 → 阻断提交 |

##### 7.6.3 冲突裁决规则

当三层之间对同一 KE 的同一字段存在不同值时的裁决优先级：

| 优先级 | 来源 | 理由 |
|:---:|------|------|
| **1（最高）** | **Markdown 文件 frontmatter** | 物理真源——人类可直接编辑、Git 可追踪 diff、永远是"最后写入"的那个 |
| 2 | SQLite `knowledge_entries` | 一级缓存——由 MD 派生，信任度低于 MD |
| 3（最低） | ChromaDB metadata | 二级缓存——由 SQLite 派生，信任度最低 |

> **为什么 MD 是最高权威而非 SQLite**：
> - MD 文件在 Git 中有完整 diff 历史——谁改了什么、什么时候改的 → 可审计
> - SQLite 二进制文件 Git diff 是乱码 → 不可审计
> - 对标：Terraform → `.tf` 文件是 canonical，`.tfstate` 是派生缓存 / K8s → YAML manifest 是 canonical，etcd 是运行时缓存
> - 例外：运行时字段（usage_count/adoption_count/helpfulness_score/last_used_at/_locked）**只存在于 SQLite**——MD 中完全没有。这些字段的权威来源就是 SQLite。

##### 7.6.4 KO/KB 的同步策略差异

| 实体 | 存储层 | 同步策略 |
|------|--------|---------|
| **KO** | 仅 Markdown 文件（`docs/08_knowledge/ko/`） | 无需同步——KO 不入 SQLite、不入 ChromaDB。晋升为 KE 后走 KE 的三层同步 |
| **KB** | YAML 文件（`docs/08_knowledge/kb/`） + 可选的 SQLite `kb_rules` 表 | KB 的 `rule` 字段需要被 pre-commit/CI 直接读取（YAML 文件），SQLite 仅用于追踪 `derived_from` 反向索引和 `last_triggered_at` |

**KB SQLite 辅助表**（beta 可选，非强制）：

```sql
CREATE TABLE IF NOT EXISTS kb_rules (
    kb_id        TEXT PRIMARY KEY,
    status       TEXT NOT NULL DEFAULT 'ACTIVE',
    check_type   TEXT NOT NULL,
    on_violation TEXT NOT NULL DEFAULT 'BLOCK',
    derived_from TEXT DEFAULT '[]',
    last_triggered_at TEXT,
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL
);
```

> **为什么 KB 的 canonical 是 YAML 文件而非 SQLite**：KB 的消费者是 pre-commit hooks 和 CI 脚本——它们直接读 YAML 文件最快（不需要 SQL 连接）。SQLite 只是辅助追踪"这条规则上次是什么时候触发的"。

> **大白话**：MD（Markdown）= 房产证（物理真源），SQLite = 物业登记册（从房产证抄过来的，方便快速查），ChromaDB = 搜索引擎索引（从物业登记册再抄一遍，方便语义搜）。三个层次有严格的派生顺序——MD 生成 SQLite，SQLite 生成 ChromaDB。每周自动对账：房产证和物业登记册对不上？以房产证为准自动修复。登记册里有但搜索引擎里没有？自动补索引。就像一个自动化的三方会计对账系统——不需要人介入。

##### 7.6.5 决策一致性检查（Decision Consistency Check）

> **触发缺口**：ISSUE-006——当前 A2（架构决策）KE 创建时没有自动检测与已有决策记录的语义冲突。假如 KE-042 写入"本项目选用 ChromaDB 为唯一向量数据库"，半年后 KE-128 写入"迁移到 Milvus"——两条决策记录之间存在事实冲突，但系统不会自动检测，只能在 AI 冷启动时读到两条矛盾的 KE 后人工发现。

**设计**：

```
新决策 KE（A2 architecture_decision）提交 REVIEWED 状态时
       │
       ▼
┌──────────────────────────────────────────┐
│ S1：决策语义检索（Decision Semantic Scan） │
│  → ChromaDB query: new_ke.body 一起用    │
│     Cross-Encoder 对 category=A2 的       │
│     所有 ACTIVE/VERIFIED KE 做 pair 打分   │
│  → 取 top_k=5 相似度 > 0.75 的历史决策    │
└──────────────────┬───────────────────────┘
                   ▼
┌──────────────────────────────────────────┐
│ S2：矛盾断言判定（Contradiction Assertion）│
│  → Kimi K2.6 逐 pair 对比：              │
│     新决策 vs 旧决策是否构成互斥/矛盾？    │
│  → 输出：NO_CONFLICT / AMBIGUOUS /        │
│           CONTRADICTION                   │
└──────────────────┬───────────────────────┘
                   ▼
       ┌───────────┴───────────┐
       │                       │
  NO_CONFLICT            AMBIGUOUS /
  → 正常入库              CONTRADICTION
                         → 推送 Owner 裁决
                         → ke_contradiction 事件写入 learn()
                         → Owner 裁定后：
                           新 KE 入库 + 旧 KE SUPERSEDED
                           或 新 KE REJECTED
```

| 判定结果 | 自动动作 | Owner 参与 |
|---------|---------|:---:|
| NO_CONFLICT | KE 正常进入 INDEXED→VERIFIED 流程 | ❌ |
| AMBIGUOUS | KE 暂停在 REVIEWED 状态，生成对比报告推送 Owner | ✅ 需裁定 |
| CONTRADICTION | KE 阻止入库，生成冲突报告推送 Owner，同时触发 `ke_contradiction` 事件 | ✅ 必须裁定 |

**与 `ke_contradiction` 字段的联系**：
- §3.7 已定义 `ke_contradiction` 作为 feedback event type（`ke_id_a` + `ke_id_b` + `conflict_description`）
- 本检查是 `ke_contradiction` 的**自动触发源**——不需要等到 AI 运行时才发现
- 裁决结果永远记录在案：哪个决策保留、哪个被废弃、Owner 的裁定理由

**Semver 联动**：
- 矛盾 → 旧 KE 被 SUPERSEDED → `superseded_by` 字段填新 `ke_id`
- 新 KE 的 `version` 字段写入旧 KE 的 version + 1（如 1.0 → 2.0）
- 保留完整决策演化链路：KE-042(v1.0)→KE-128(v2.0,supersedes KE-042)

> **对标**：Anthropic Constitutional AI — 模型输出通过另一模型做"harmlessness check" / ChromaDB cross-encoder pair scoring 用于去重 / ITIL SACM — CI relationship mapping（配置项之间的影响分析）。三重对标都说明：决策之间必须建立关系图谱，新决策上线前必须扫一遍已有决策。
> **大白话**：你现在做决定时，系统会自动翻一遍"历史决定册"，看看跟以前说的有没有矛盾。有矛盾先暂停——拿新旧两条决定的对比报告推给 Owner："你以前说用 A，现在又说用 B——到底哪个？" Owner 点一下头，旧的决定自动标记为"被取代"，新的生效。这样知识库里的决策永远自洽——不会出现"KE-042 说用 ChromaDB、KE-128 说用 Milvus"这种 AI 读完了不知道听谁的尴尬。

### 7.7 Human-Gated 写入权限模型

> **触发缺口**：ISSUE-008——当前 KE/KB 的写入权限未明确定义。KB 规则写入（如"本项目只用 ruff"）会直接影响 CI/pre-commit 行为——写入前必须有人类确认。但 A4 失败模式（"3587 个误报源于一个多余的反斜杠"）是自动发现的事实——不需要人类确认。当前的权限模型不区分二者，所有 KE 走同一流程，导致：①高影响规则无人类确认就生效；②低影响事实被不必要的确认卡住。

**三层权限矩阵**：

| 层级 | 权限等级 | 适用范围 | 触发条件 | Owner 参与 | 示例 |
|:---:|---------|---------|---------|:---:|------|
| **L1** | AUTO | A1/A4/A5/A6/A7/B3——纯事实/自动阻断发现 | 系统自动生成→直接入库 | ❌ 零参与 | "3587 个误报源于一个多余的反斜杠" |
| **L2** | HUMAN_GATED | A2/A3/A8/B1/B2——决策/策略/推断 | 系统生成草稿→推送 Owner→Owner 确认后入库 | ✅ yes/no | "选 SQLite 而非 PostgreSQL：<10万KE 规模时足够" |
| **L3** | OWNER_ONLY | Track C（C1/C2/C3）——Owner 画像 | 仅 Owner 可以创建/修改，系统可建议 | ✅ 完全参与 | "Owner 在 ruff vs pylint 中选 ruff" |

**HUMAN_GATED 流程**：

```
系统检测到 L2 级 KE/KB 候选（如 A2 架构决策 / B1 策略规则）
       │
       ▼
┌──────────────────────────────────────────────┐
│ S1：系统自动生成 KE/KB 草稿                    │
│  → 格式符合 §3.2.2（KE）或 §3.11（KB）模板     │
│  → 附带对比表/数据支撑（如有）                  │
│  → 标记 status: DRAFT                        │
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│ S2：推送 Owner 通知                            │
│  → 渠道：Feishu MCP / Webhook（可配置）         │
│  → 格式：                                    │
│     📋 [KB] 新决策待确认                       │
│     KE-XXX: 选 SQLite 而非 PostgreSQL         │
│        对比：SQLite(零运维,<100GB) vs PG       │
│              (需运维,>100GB场景)               │
│     回复 Y 确认 / N 驳回                        │
└──────────────────┬───────────────────────────┘
                   ▼
       ┌───────────┴───────────┐
       │                       │
    Owner: Y               Owner: N
    → KE status:            → KE status:
      SUBMITTED               REJECTED
    → 进入 REVIEWED         → 记录驳回理由
    → 走 Auditor-N          → 系统学习偏好
      四模型审计            → 更新 Track C
```

**Owner 时间预算**：

| 场景 | 频率 | 每次耗时 | 月总耗时 |
|------|:---:|:---:|:---:|
| 架构决策（A2）确认 | ~2 次/月 | 30s | 1min |
| 策略规则（B1/B2）确认 | ~3 次/月 | 30s | 1.5min |
| 施工规范（A3）确认 | ~5 次/月 | 30s | 2.5min |
| Track C 偏好更新 | ~2 次/月 | 60s | 2min |
| 冲突裁决（§7.6.5） | ~1 次/月 | 120s | 2min |
| **总计** | **~13 次/月** | — | **≤12 min/月** |

**拒绝冷却机制**：
- 同类型建议被 Owner 拒绝 ≥3 次 → 该类型进入 30d 冷却期
- 冷却期内系统不再推送同类建议（避免重复骚扰）
- 冷却期结束后重置计数
- 对标：macOS notifications "Snooze for 1 hour" / Slack "Pause notifications"

**pending_approval 字段**（新增到 KE Schema）：

```yaml
# KE frontmatter 追加字段
pending_approval: true          # 是否等待 Owner 确认
approval_deadline: "2026-05-11" # 超过 7 天未响应 → 自动 REJECTED + 归档
approval_channel: "feishu"      # 推送渠道
rejection_reason: null          # Owner 驳回时记录理由
```

> **对标**：GitHub Pull Request Review — 人类审查者 APPROVE/REQUEST_CHANGES / Terraform Cloud — run triggers require human approval for apply / Anthropic HHH principle — Helpful + Honest + Harmless（知识写入必须有 Harmlessness 保障）。三重对标都说明：AI 自动生成的知识在写入执行层之前需要人类守门——但仅限于有执行后果的知识，事实类不需要。
> **大白话**：不是所有知识都需要 Owner 点头。系统自己发现的事实（"上次 CI 挂了是因为多打了一个反斜杠"）——直接入库，不打扰 Owner。系统推断的决策（"我们选 SQLite 不选 PostgreSQL"）——生成草稿，推给 Owner："确认吗？Y/N"。Owner 一个月最多花 12 分钟，大部分时候喝口水扫一眼打个 Y 就行。Track C 的知识（Owner 自己的偏好）——只能 Owner 自己创建，系统最多建议"要不要加一条偏好？"但绝不替 Owner 做决定。

### 7.8 灾难恢复：从 Markdown 全量重建（Disaster Recovery）

> **触发缺口**：当前 SQLite 和 ChromaDB 没有显式的备份策略。如果 `data/sqlite/kb_state.db` 损坏或 `data/chroma/` 被误删，知识库将退化为纯文件系统——语义检索不可用、状态机不可用、KE 关系图谱丢失。但所有 KE 的 canonical 真源（Markdown 文件）仍然在 `docs/08_knowledge/` 下完好无损——只需从 MD 全量重建。

**设计**：

```
灾难事件（SQLite 损坏 / ChromaDB 丢失 / 人工误删 data/ 目录）
       │
       ▼
┌──────────────────────────────────────────────┐
│ S1：触发重建                                  │
│  → 手动：python -m zephyr.kb.rebuild --all   │
│  → 自动：GATE-FILE-COUNT 检测到 SQLite 不可达 │
│           → 告警 → 自动触发重建                │
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│ S2：扫描 MD 真源（Source of Truth）            │
│  → 遍历 docs/08_knowledge/ 所有 KE-*.md       │
│  → 解析 YAML frontmatter → 提取 28 字段       │
│  → 验证 G1 格式规则 F-01~F-06                 │
│  → 跳过损坏的 MD 文件（记录到 recovery_log）    │
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│ S3：重建 SQLite                               │
│  → CREATE TABLE IF NOT EXISTS（全新库）       │
│  → 批量 INSERT 所有有效 KE 元数据              │
│  → 恢复 kb_state_log（从 KE status 历史重建）  │
│  → 恢复 KB 规则表（从 docs/08_knowledge/kb/）  │
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│ S4：重建 ChromaDB                             │
│  → 删除旧 Collection → 重新创建               │
│  → 逐 KE 调用 embedding_model.encode(body)   │
│  → 批量 upsert 向量 + metadata                │
│  →  BGE-M3（rebuilt with better │
│     model than the original one）             │
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│ S5：一致性校验                                │
│  → 运行 §7.6.2 五道一致性闸门（全量）          │
│  → 运行 GATE-FILE-COUNT（MD 数 vs SQLite 数） │
│  → 通过 → 生成 recovery_report.md             │
└──────────────────────────────────────────────┘
```

**恢复时间估算（RTO）**：

| 规模 | KE 数量 | SQLite 重建 | ChromaDB 重建 | 总 RTO |
|------|:---:|:---:|:---:|:---:|
| experimental（当前） | ~32 | <1s | ~30s | **<1min** |
| beta | ~200 | <2s | ~3min | **<5min** |
| beta（满规模） | ~1,500 | <10s | ~20min | **<25min** |

**恢复点目标（RPO）**：

| 数据层 | RPO | 依据 |
|--------|:---:|------|
| KE Markdown 文件 | **0（零丢失）** | Git 版本控制——`docs/08_knowledge/` 全量在 Git 中，可 `git checkout` 恢复至任意历史版本 |
| SQLite 运行时字段 | **<7天** | `usage_count` / `adoption_count` / `helpfulness_score` / `last_used_at` 会在重建时丢失最近 7 天的运行时统计（除非另做 SQLite 备份） |
| ChromaDB 向量 | **0（零丢失）** | 向量由 MD body 重新 embedding 生成——确定性输出（同模型同输入→同向量），无信息丢失 |

**SQLite 备份策略（可选增强）**：

```bash
# 每日 cron：备份 SQLite 到 Git 追踪目录
# 路径：data/sqlite/backups/kb_state_$(date +%Y%m%d).db
# Git 策略：保留最近 7 天（.gitignore 规则：data/sqlite/backups/*.db 不入库——仅本地保留）
cp data/sqlite/kb_state.db data/sqlite/backups/kb_state_$(date +%Y%m%d).db

# 每周 cron：备份 ChromaDB
# 路径：data/chroma/backups/chroma_$(date +%Y%m%d).tar.gz
tar -czf data/chroma/backups/chroma_$(date +%Y%m%d).tar.gz data/chroma/*/
```

> **对标**：PostgreSQL pg_dump/pg_restore 全量恢复 / ChromaDB 官方 "reindex from source documents" 策略 / Kubernetes etcd snapshot restore / ITIL IT Service Continuity Management——RTO+RPO 双指标。四重对标都说明：只要 canonical source（MD文件+Git历史）完好，向量和元数据都是派生数据——丢了可以重建，时间成本可控。
> **大白话**：最坏情况下——`data/sqlite/` 和 `data/chroma/` 全被删了——不要慌。运行 `python -m zephyr.kb.rebuild --all`，系统会扫一遍 `docs/08_knowledge/` 下所有 KE Markdown 文件，自动重建 SQLite 和 ChromaDB。experimental 不到 1 分钟就回来了。唯一丢的是最近 7 天的运行时统计（"这条 KE 被用了多少次"这类计数）——核心知识一文不少。因为 Markdown 文件在 Git 里，永远丢不了。

---

## §8 容量预估

### 8.1 知识条目（KE）数量预估

| 阶段 | KE 数量 | 来源 |
|------|:---:|------|
| experimental（当前） | ~32 KE | 手动录入的蓝图决策 + 最佳实践 |
| beta 末 | ~500 KE | Session Log 自动提取 + 候选池迁移 + GitHub 抓取 |
| beta 末 | ~2000 KE | arXiv 论文 + MCP 外部知识 + 多Agent交叉贡献 |
| stable+ | ~10000 KE | 长期积累 |

### 8.2 存储容量估算

| 数据层 | beta (~500 KE) | beta (~2000 KE) | stable+ (~10000 KE) |
|--------|:---:|:---:|:---:|
| Markdown KE 文件 | ~50 MB | ~200 MB | ~1 GB |
| ChromaDB 向量 (384d) | ~3 MB | ~12 MB | ~60 MB |
| BGE-M3 模型文件 | — | ~2000 MB | ~2000 MB |
| BGE-reranker-v2-m3 模型 | — | ~200 MB | ~200 MB |
| SQLite 元数据 | ~1 MB | ~5 MB | ~25 MB |
| ChromaDB 向量 (1024d BGE-M3) | — | ~35 MB | ~175 MB |
| **总计（当前）** | **~54 MB** | **~452 MB** | **~1.46 GB** |

### 8.3 ChromaDB 性能边界

| 向量数量 | 检索延迟（预期） | 是否需要升级 |
|---------|:---:|:---:|
| < 1000 | < 50ms | ❌ |
| 1000-10000 | < 200ms | ❌ |
| 10000-100000 | < 500ms | ⚠️ 评估 Qdrant |
| > 100000 | > 1s | ✅ 迁移 Qdrant/LanceDB |

---

## §9 知识检索与演化回路（Retrieval & Evolution Loop）

> **触发缺口**：蓝图 v0.6.3 及之前版本完整定义了"知识怎么进来"（G1-G5 五门禁 + §3.9.1 8条来源矩阵）和"知识怎么存"（§7 三层存储 + §7.8 灾难恢复），但**"知识怎么出去"和"知识怎么演化"两块完全空白**。这导致：①检索质量无法度量——AI冷启动时拿到了错误的KE但没人知道；②KE内容更新后旧版本无迹可寻——只能翻Git log；③上下文注入一刀切——修bug和写新模块用同等预算；④KB规则定义了但pre-commit不会执行——形同虚设。

### 9.1 检索质量度量（RAG Evaluation Metrics）

当前唯一的质量指标是 KE `quality_score`——衡量的是**KE内容本身的可靠度**，不是**检索结果的相关性**。两者完全不同：一条 excellent 的 KE 在错误的检索结果中 = 没用。

**四维质量指标**（对标 RAGAS / DeepEval / TruLens）：

| 指标 | 定义 | 计算方式 | 目标值 |
|------|------|---------|:---:|
| **Answer Relevance** | 生成的回答中有多少来自检索到的 KE | Kimi K2.6 逐句对比：每句话是否可追溯到某条 KE | > 0.80 |
| **Faithfulness** | 生成的回答中有多少与 KE 一致（不虚构） | Kimi K2.6 判断：回答中的断言是否与 KE body 矛盾 | > 0.90 |
| **Context Precision** | 返回的 Top-K 中真正相关的比例 | 人工标注金标准测试集（10个典型问题→答案→相关KE编号） | > 0.75 |
| **Context Recall** | 所有相关知识中，检索到了多少 | 同上——金标准测试集中"应返回但未返回"的KE比例 | > 0.70 |

**实现**：扩展 `eval_harness.py` 新增 `RAGMetricEvaluator` 类：

```python
class RAGMetricEvaluator:
    def evaluate(self, query: str, retrieved_kes: list[KeEntry],
                 generated_answer: str) -> RAGMetrics:
        """返回 answer_relevance / faithfulness / context_precision / context_recall"""
```

**触发**：每周 APScheduler cron + 每次 KE Schema 大版本升级后自动跑全量。

> **对标**：RAGAS (Exploding Gradients) — 被 LangChain/LlamaIndex 官方推荐 / DeepEval (Confident AI) — 企业级 RAG 评估 / TruLens (TruEra) — RAG 三合一反馈函数。三套框架都认同一件事：**无评估 = 盲飞**。没有检索质量度量，你连"知识库有没有用"都不知道。
> **大白话**：现在的问题是——库里有 200 条 KE，AI 问"ruff 怎么配置？"系统返回了 Top-10。但这 10 条 KE 里真正相关的有几条？AI 基于这些 KE 生成的回答是不是在瞎编？没人知道。引入四维指标后：每周自动跑一次——"这个月 context_precision 从 0.72 跌到了 0.53 → 别着急加新知识，先修检索管道"。

### 9.2 混合检索（Hybrid Search: BM25 + Vector）

当前 ChromaDB 纯稠密向量检索。问题：工程术语（"E501"、"VaR_95"、"ISIN"）在向量空间里容易被"语义相近但完全不同的事"淹没。

**设计**：

```
用户 query（或 AI 自动构造的 query）
       │
       ├──────────────────┬──────────────────┐
       ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Dense Ret.    │  │ Sparse Ret.  │  │ Query Exp.   │
│ ChromaDB      │  │ BM25(BGE-M3  │  │ HyDE (§9.3)  │
│ cosine > 768d │  │ tokenized)   │  │              │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       │    top_k=50     │    top_k=50     │
       └────────┬────────┘                 │
                ▼                          │
       ┌────────────────┐                  │
       │ RRF Fusion     │ ◄────────────────┘
       │ (Reciprocal    │
       │  Rank Fusion)  │
       │ k=60 constant  │
       └───────┬────────┘
               ▼
       ┌────────────────┐
       │ Merged Top-20   │
       │ → Cross-Encoder │
       │   Rerank (§5.9) │
       └────────────────┘
```

**BM25 实现**：使用 `rank_bm25` 库（纯Python，零外部依赖，与 ChromaDB 同级轻量）：

```python
from rank_bm25 import BM25Okapi
# beta 只需对 18 类每类建一个 BM25 索引（<500 KE，内存 <10MB）
```

**RRF 融合公式**：

```
RRF(d) = Σ 1/(k + rank_i(d))   # k=60, rank_i 是文档 d 在检索器 i 中的排名
```

**降级策略**：BM25 索引损坏 → 退化为纯向量检索 + WARN 日志。

> **对标**：Weaviate hybrid search (BM25 + vector + fusion) / Qdrant sparse vector / Elasticsearch v8.0+ Learn to Rank。三大向量引擎都在 2023-2024 年加入混合检索——说明纯向量不够，BM25 在精确术语匹配上不可替代。
> **大白话**：你搜"E501 错误怎么修"——向量可能给你返回"ruff 配置指南"（语义接近"错误"和"修"但根本不讲 E501），BM25 直接匹配"E501"这个精确 token → 给你"ruff line-too-long E501 诊断与修复"。两个结果融合后重排——既有语义深度又有词法精度。

### 9.3 查询改写与扩展（Query Rewriting & HyDE）

AI 的原始查询往往很口语化/碎片化："ruff报错了"、"VaR怎么算"。直接用这些 query 搜向量 = 低召回。

**三阶段管线**：

```
原始 query: "ruff报错了"
       │
       ▼
┌──────────────────────────────────────────┐
│ S1：Multi-Query 生成（LangChain 对标）    │
│  Kimi K2.6 prompt:                        │
│  "生成 3 个同义改写：                      │
│   1. ruff linter 故障排查流程              │
│   2. ruff 常见错误码 E501 E402 W291 修复   │
│   3. Python ruff 代码检查工具排错指南       │
│   → 3 个 query 各自检索 → 合并去重         │
└──────────────────┬───────────────────────┘
                   ▼
┌──────────────────────────────────────────┐
│ S2：HyDE（Hypothetical Doc Embedding）    │
│  Kimi K2.6 prompt:                        │
│  "假装你是一个 ruff 专家回答以下问题：     │
│   ruff报错了怎么办？"                      │
│  → 把生成的"假答案"做 embedding             │
│  → 用假答案的向量去搜真实 KE               │
│  → 假答案的向量比问题的向量更接近真实 KE    │
└──────────────────┬───────────────────────┘
                   ▼
┌──────────────────────────────────────────┐
│ S3：去重 + 合并                           │
│  → 3 个 Multi-Query 结果 + 1 个 HyDE 结果 │
│  → 按 ke_id 去重                          │
│  → 取并集 Top-20 → 送入 §9.2 RRF          │
└──────────────────────────────────────────┘
```

**触发条件**：仅当向量检索返回的 Top-1 相似度 < 0.60 时启用（正常情况不额外消耗 token）。

> **对标**：Stanford HyDE paper (Gao et al., 2023) — 在 TREC DL19/20 上 Recall@100 提升 10-15% / LangChain MultiQueryRetriever / LlamaIndex QueryFusionRetriever。三组实验都证明：**改写 query 的 ROI 远超扩大检索数量**。
> **大白话**：你问"ruff报错了"——系统不会直接拿这三个字去搜，而是先让 Kimi 写一篇"如果 ruff 报错了应该怎么办"的范文（HyDE），然后把这篇范文的向量拿去搜。为什么？因为"ruff报错了"的向量可能更接近"error handling"的通用文档，而范文里包含了"pyproject.toml"、"select"、"ignore"、"E501"等 ruff 特有词汇——这些词汇的向量会命中真正的 ruff KE。

### 9.4 上下文预算动态分配（Dynamic Context Budget）

当前 `context_assembler.recall()` 统一 Top-10 ≤ 2000 tokens——但任务需求差异极大。

**任务自适应注入策略**：

| 任务类型 | 判定方式 | Top-K | Token 预算 | 注入焦点 |
|---------|---------|:---:|:---:|------|
| 新模块创建（greenfield） | Session log task_type: `create_module` | ≤ 8 | ≤ 1500 | A3（施工规范）+ A2（架构决策）+ B2（设计模式） |
| Bug 修复（debug） | Session log task_type: `fix_bug` 或 pre-commit 阻断 | ≤ 5 | ≤ 800 | A4（失败模式）+ A7（具体修复步骤） |
| 重构（refactor） | Session log task_type: `refactor` | ≤ 6 | ≤ 1200 | A3（施工规范）+ A5（重构备忘）+ A6（性能优化） |
| 代码审查（review） | Session log task_type: `code_review` | ≤ 10 | ≤ 2000 | 全 A1-A8 + B2（设计模式） |
| 研究/学习（research） | Session log task_type: `research` | ≤ 12 | ≤ 2500 | B1-B7（金融知识）+ A8（工具评价） |
| 对话/日常（chat） | 默认 | ≤ 5 | ≤ 600 | 仅 Track C（Owner 偏好）+ 最近 3 条活跃 KE |

**实现**：

```python
context_assembler.recall(
    query=...,
    task_type=session_log.get("task_type", "chat"),
    trigger_context=...,
    # 内部自动查表分配 top_k 和 max_tokens
)
```

> **对标**：Claude Code context engineering — 根据 task_type 动态裁剪 context / Cursor .cursorrules — 不同项目不同注入策略 / MemGPT — Working Memory 预算自适应。三者都认同一件事：**context 是稀缺资源，预算必须按任务类型差异化分配**。
> **大白话**：修一个小 bug 的时候不需要把 2000 tokens 全灌给 AI——给 800 tokens 聚焦失败模式就够。写新模块的时候反而需要更多上下文——施工规范、架构决策、设计模式，一个不能少。就像工具箱——修自行车拿小扳手，修卡车拿大套筒，不是每次都把整个工具箱倒出来。

### 9.5 KB 规则执行引擎（KB Rule Enforcement）

§3.11 定义了 KB 规则 YAML 格式，但当前没有任何机制读取并执行这些规则。"本项目只用 ruff"是一条躺在 YAML 里的声明——pre-commit 不会读它，CI 不会读它，AI 也不会自动遵守它。

**设计**：

```
pre-commit hook 触发
       │
       ▼
┌──────────────────────────────────────────┐
│ S1：读取 KB 规则                           │
│  → 扫描 docs/08_knowledge/kb/*.yaml      │
│  → 过滤 status=ACTIVE                     │
│  → 提取 rule_type=CONSTRAINT 的规则       │
└──────────────────┬───────────────────────┘
                   ▼
┌──────────────────────────────────────────┐
│ S2：动态生成检查项                          │
│  KB-001: "unified_linter: ruff"           │
│  → 生成 check:                            │
│    - repo: local                           │
│    - hook: system                          │
│    - name: ruff (KB-enforced)              │
│    - entry: ruff check --fix               │
│    - language: system                      │
│    - KB source: docs/08_knowledge/kb/...  │
│                                            │
│  KB-002: "type_checker: mypy --strict"     │
│  → 同理                                    │
└──────────────────┬───────────────────────┘
                   ▼
┌──────────────────────────────────────────┐
│ S3：执行 + 结果溯源                         │
│  → 失败日志写入: ZK-KB-001 阻断            │
│  → 阻断来源=KB 规则而非手动配置             │
│  → Rule-KE Sync（§5.12.3）验证规则一致性   │
└──────────────────────────────────────────┘
```

**与现有 pre-commit 的关系**：KB 规则不替换 `.pre-commit-config.yaml`，而是作为**动态追加层**。`.pre-commit-config.yaml` 仍手工维护静态通用规则（trailing-whitespace, end-of-file-fixer），KB 规则追加项目特定的、会演化的约束。

> **对标**：ESLint `extends` 机制——规则 YAML 被 pre-commit hook 读取并转换为动态检查 / Terraform Sentinel — policy as code / OPA (Open Policy Agent) — Rego rules enforced at runtime。三者都说明：**规则定义了不执行 = 没有规则**。
> **大白话**：以前你在 KB 里写"本项目只用 ruff"，但 pre-commit 里还是 `pylint` + `flake8` + `ruff` 三件套全开着。现在 pre-commit 每次运行前先读 KB——发现有 CONSTRAINT 级别规则，自动加上对应的检查。KB 说用什么工具，pre-commit 就用什么工具——规则的唯一真源是 KB，不是 `.pre-commit-config.yaml`。

### 9.6 知识溯源与追踪（Knowledge Provenance & Tracing）

当前无法回答：AI 这次生成中使用了哪条 KE？KE-042 在哪些 session 中被引用了？RAG pipeline 每一步的决策是什么？

**三级溯源**：

| 层级 | 记录内容 | 存储 | 对标 |
|:---:|------|------|------|
| L1：KE 溯源 | `derived_from` 字段扩展为 PROV 标准：`wasDerivedFrom(session_log_#47)` + `wasGeneratedBy(g5_extract)` + `wasAttributedTo(kimi_k2.6)` | KE frontmatter | W3C PROV-O |
| L2：引用追踪 | 每次 `unified_memory_api.recall()` 在 SQLite 记录：`(session_id, ke_id, rank, similarity, used_in_generation: bool)` | SQLite `ke_usage_log` 表 | LangSmith trace |
| L3：RAG Trace | 端到端管线可视化：query → 召回 → 重排 → 注入 → 生成答案 → 答案中哪些片段来自哪条 KE | `data/sqlite/rag_traces.db` | LangFuse / MLflow |

**KE 引用热力图**：

```sql
-- 过去30天哪些KE被使用最多（引用热度）
SELECT ke_id, category, COUNT(*) AS usage_count
FROM ke_usage_log
WHERE created_at > DATE('now', '-30 days')
GROUP BY ke_id
ORDER BY usage_count DESC
LIMIT 10;
```

> **对标**：LangSmith (LangChain) — RAG pipeline 全链路 trace + feedback / LangFuse — 开源 LLM observability / W3C PROV — 知识溯源国际标准。三者都强调：**没有 trace，就无法优化**。
> **大白话**：现在你完全不知道 AI 用了哪些 KE、哪些 KE 从来没人看过。加上溯源后：每周自动出报告——"本周 KE-042 被引用了 47 次，KE-087 0 次 → KE-087 可能该降级或删了"。RAG 出问题也知道是哪一环崩了——"这次检索召回 10 条但重排后只剩 2 条相关，问题在重排模型没 calibrated"。

### 9.7 KE 版本历史（KE Semantic Versioning）

KE body 被更新时旧版本丢失（仅在 Git 中可追溯）。AI 读取 KE-042 看到的是最新版，不知道以前版本的存在。

**设计**：

```
docs/08_knowledge/
└── a2_architecture_decision/
    ├── KE-042-chromadb-as-vector-store/
    │   ├── v1.0.md          # 初始版本
    │   ├── v1.1.md          # 追加 Milvus 对比
    │   ├── v2.0.md          # 改为 superseeded(SQLite 够用了)
    │   ├── current.md       # → 始终指向最新版（软链/复制）
    │   ├── versions.yaml    # 版本清单 + diff 摘要
    │   └── CHANGELOG.md     # 人类可读变更日志
```

**versions.yaml**：

```yaml
versions:
  - version: "1.0"
    date: "2026-04-15"
    author: "g5_extract + kimi_k2.6"
    summary: "初始化——选定 ChromaDB 作为向量引擎"
  - version: "1.1"
    date: "2026-05-01"
    author: "g5_extract + qwen3_max"
    summary: "追加 ChromaDB vs Milvus 对比表"
    breaking: false
  - version: "2.0"
    date: "2026-05-03"
    author: "owner_override"
    summary: "裁决：当前规模 SQLite 就够了，ChromaDB 暂挂"
    breaking: true
    supersedes: "KE-042"
```

**Semver 规则**：

| 变更 | 版本号 | 示例 |
|------|:---:|------|
| 修正错别字、格式调整、补充示例 | MINOR (1.0→1.1) | 追加对比表 |
| 修改结论、变更推荐方案、追加新事实 | MAJOR (1.1→2.0) | 选型结论反转 |
| 原 KE 完全被新知识推翻 | SUPERSEDED | KE-042→KE-128 |

> **对标**：CRATE (Rust) versioning — 每个 crate 独立 semver / NPM semver — MAJOR.MINOR 双版本号 / Semantic Versioning 2.0.0 规范。三条标准都是：**变更不可怕，不记录变更才可怕**。
> **大白话**：你改完 KE-042 后，AI 下次读到的是新版——不知道以前你推荐过 ChromaDB，现在改为 SQLite。版本历史保留后：AI 读 current.md 知道最新结论是 SQLite，同时能翻 v1.0-v2.0 历史知道"为什么选 ChromaDB 后来又被否决了"——这个决策演化过程本身也是知识。

### 9.8 知识依赖级联（Dependency Cascade on Deprecation）

KE-128 `depends_on: [KE-042]`，KE-042 被标记 DEPRECATED → KE-128 当前仍然是 ACTIVE——AI 不知道它的底层依赖已经过期。

**设计**：

```
KE-042 status → DEPRECATED
       │
       ▼
┌──────────────────────────────────────────┐
│ S1：依赖反向索引查询                        │
│  → SQLite: SELECT ke_id FROM ke_metadata  │
│    WHERE depends_on_ke LIKE '%KE-042%'    │
│  → 返回：[KE-128, KE-215, KE-301]          │
└──────────────────┬───────────────────────┘
                   ▼
┌──────────────────────────────────────────┐
│ S2：级联影响评估                            │
│  → 对每条依赖 KE 逐条检查:                 │
│    是否仍然成立？（depends_on 中的其他 KE   │
│    是否也过期？）                           │
│  → 评级：GREEN（不受影响）/ YELLOW（需审查） │
│          / RED（依赖断裂——KE本身可能无效）   │
└──────────────────┬───────────────────────┘
                   ▼
┌──────────────────────────────────────────┐
│ S3：通知 + 批量标记                         │
│  → RED: 自动标记 NEEDS_REVIEW             │
│  → YELLOW: 推送 Owner "3条KE依赖的KE-042  │
│            已废弃，需要你审查"               │
│  → GREEN: 静默                            │
│  → 事件：ke_deprecation_cascade → learn() │
└──────────────────────────────────────────┘
```

> **对标**：npm deprecation warnings — `npm WARN deprecated` + 让消费者知道 / Rust cargo `--warn-deprecated` / Gradle dependency resolution — 冲突时自动 resolution strategy。三者都说明：**依赖图是活的——上游废弃了必须通知下游**。
> **大白话**：假设 KE-042 是一根柱子（"选 ChromaDB 做向量存储"），KE-128 和 KE-215 是建在这根柱子上的墙（"ChromaDB 的检索优化"、"向量索引升级方案"）。柱子拆了——墙怎么还立着？现在系统会自动检测：柱子被标记废弃→所有压在这根柱子上的墙自动标记"需要检查"→推给 Owner 决定是拆墙还是换柱子。

### 9.9 知识去重聚类（Cluster-based De-duplication）

G2 Triage 做单条 vs 单条相似度 > 0.80 去重。规模效应下不行：到 500+ KE 时，可能 8 条 KE 都在讲"ruff 配置"的不同侧面，逐对比较 O(n²) 且容易漏。

**HDBSCAN 聚类策略**：

```
每 30 天自动触发（APScheduler cron）
       │
       ▼
┌──────────────────────────────────────────┐
│ S1：构建 KE 向量矩阵                       │
│  → 从 ChromaDB 批量读出所有 ACTIVE KE     │
│     embedding vector                      │
│  → 构建 (N × 768d) 矩阵                   │
└──────────────────┬───────────────────────┘
                   ▼
┌──────────────────────────────────────────┐
│ S2：UMAP 降维 + HDBSCAN 聚类              │
│  → UMAP: 768d → 50d（保留局部结构）       │
│  → HDBSCAN(min_cluster_size=2,            │
│             min_samples=1)                │
│  → 输出：聚类标签 + 离群点(-1)             │
└──────────────────┬───────────────────────┘
                   ▼
┌──────────────────────────────────────────┐
│ S3：聚类内去重建议生成                      │
│  → 每个 cluster 中 ≥ 3 条 KE              │
│  → Kimi K2.6 cluster summary:            │
│     "这 5 条 KE 都在讲 ruff 配置：         │
│      KE-011 讲 pyproject.toml 配置        │
│      KE-023 讲 pre-commit 集成            │
│      KE-045 讲常见错误码                   │
│      KE-078 讲 ruff vs pylint 对比        │
│      KE-092 讲 ruff 格式化配置             │
│      建议：合并为 1 条 parent KE + 4 条    │
│      child KE（subtopic 形式）"            │
│  → 推送 Owner 审批                         │
└──────────────────────────────────────────┘
```

> **对标**：arXiv paper deduplication (HDBSCAN + UMAP) / Semantic Scholar — clustering academic papers / BERTopic — transformer-based topic modeling with HDBSCAN。三组工具都宣示：**逐对比较不可扩展，聚类是规模级去重的唯一路径**。
> **大白话**：50 条 KE 时，逐条对比没问题。500 条 KE 时，可能有 8 条都在讲 ruff——系统不会让你手动对着 500 条一个个挑。每月自动 HDBSCAN 聚类一次，把"扎堆"的 KE 揪出来——"这 5 条都在讲 ruff，要不要合并成一篇总纲+四篇分章？"Owner 点个头就行。

### 9.10 Token 预算与节流（Token Budget & Throttling）

五轨提取 + RAG 注入 + 四模型审计 + 查询改写 + HyDE + re-rank——全在今天消耗 LLM token。无预算上限 = 无底洞。

**月度 Token 预算**（以 Kimi K2.6 计价，约 ¥1.20/百万 token）：

| 管道 | 月度调用次数 | 平均 token/次 | 月 token | 月费用 |
|------|:---:|:---:|:---:|:---:|
| 轨道1：Session→KE提取 | ~30 | 2000 | 60,000 | ¥0.07 |
| 轨道2：CI阻断→KE | ~10 | 1500 | 15,000 | ¥0.02 |
| 轨道3：决策信号→KE | ~3 | 3000 | 9,000 | ¥0.01 |
| 轨道4：外部注入→KE | ~5 | 2000 | 10,000 | ¥0.01 |
| 轨道5：周巡检 | ~4 | 8000 | 32,000 | ¥0.04 |
| Multi-Query (§9.3) | ~15 | 1500 | 22,500 | ¥0.03 |
| HyDE (§9.3) | ~15 | 2000 | 30,000 | ¥0.04 |
| HDBSCAN 聚类 (§9.9) | ~1 | 5000 | 5,000 | ¥0.01 |
| 四模型审计 | ~12 | 12000 | 144,000 | ¥0.17 |
| **月度总计** | **~95** | — | **~327,500** | **¥0.40** |

**硬预算上限**：¥5.00/月。超 80% 时 WARN 日志 + 降级：HyDE → 关闭 / Multi-Query → 关闭 / 审计 → 仅 V-12 快速通道。

**背压机制**：

```
LLM API 429 (Rate Limit) / 月预算超 80%
       │
       ▼
┌──────────────────────────────────────────┐
│ 优先级队列降级                              │
│  P0 (永不降级): 轨道1 Session提取 + 轨道2   │
│                 CI阻断                      │
│  P1 (80%时降级): 轨道5 周巡检 + Multi-Query │
│                   + HyDE (§9.3)             │
│  P2 (>100%时降级): 四模型审计 → 仅V-12      │
│                    快速通道                 │
│  P3 (>120%时降级): 轨道4外部注入→暂停       │
└──────────────────────────────────────────┘
```

> **对标**：OpenAI rate limits tier system — 按额度分配优先级 / AWS Budget Alerts — 超预算自动告警+限流 / GCP Quotas — 硬上限 + 配额申请流程。三者都强调：**自动系统必须自带断路器**。
> **大白话**：这套系统的 LLM 开销极低——月均不到 5 毛钱。但如果没有预算上限，未来轨道 4 接到一个 GitHub trending 大项目自动灌入 200 条 KE 提案→审计器×4 模型全部跑一遍 = 一次就吃掉 ¥15。必须设硬上限——超了就降级，先把最重要的管道保住，不太重要的暂停到月底再说。

### 9.11 多模态知识（Multi-modal Knowledge）

所有 KE 目前纯文本。但 Vibe Coding 的 session 经常产出**截图**（UI 对比、架构白板、错误弹窗截图）和**代码 diff 截图**——这些视觉信息当前全部丢弃。

**beta 设计（预留，非当前施工）**：

| 模态 | 提取方式 | Embedding | 检索 |
|------|---------|---------|------|
| 截图/图表 | Session log `attachments[]` → CLIP image encoder | `ViT-B/32` (512d) | Image→Text Cross-modal search |
| 代码 diff 截图 | Git diff screenshot → OCR → text KE + screenshot 作为 attach | 文字部分走文本embedding，图片部分走 CLIP | 文字+图片双通道 |
| 架构白板 | 手绘架构图 → CogVLM 描述生成 → text KE | 描述文字的 embedding | 纯文本检索（图片作为可视化附件） |

**存储**：图片 base64 嵌入 KE frontmatter 的 `attachments` 字段，或外部路径引用到 `data/multimodal/`。

> **对标**：CLIP (OpenAI, 2021) — 图文跨模态检索 / CogVLM (THU/Zhipu, 2023) — 中文多模态理解 / GPT-4V — 截图直接喂给模型分析。但**2 不实现**——当前知识库主要处理结构化文本，多模态 ROI 在 beta+ 才显现。
> **大白话**：暂时先不搞——文本知识本身就够用。未来某个 session 里你贴了一张"为什么选 ChromaDB 而不是 Milvus"的白板照片——系统会把它 OCR 成文字描述+原始图作为附件一起入库。AI 以后搜"向量数据库选型"时，能在文字结果里看到那张图。

### 9.12 三级记忆模型（Three-Tier Memory: Hot/Warm/Cold）

KO→KE→KB 是**知识内容漏斗**，但 AI 运行时还需要**记忆温度分层**。一条 KE 不管多重要，都走同一条慢速检索通道 = 浪费。

**对标 MemGPT/Letta 的三级设计**：

| 温度 | 类比 | 存储 | 容量 | 访问延迟 | 存放内容 |
|:---:|------|------|:---:|:---:|------|
| Hot | L1 Cache | 进程内存（dict） | ≤ 20 条 KE | <1ms | Track C（Owner 人格）+ 当前 session 的活跃 KE + §9.4 任务相关 Top-K |
| Warm | L2 Cache | SQLite + 定时 refresh | 全量 ACTIVE KE 元数据 | <10ms | 所有 A1-B7 ACTIVE KE 的 metadata（不含 body 全文） |
| Cold | Disk | ChromaDB 语义检索 | 全量 KE | <200ms | 完整 KE body + embedding |

**Warm→Hot 预热规则**：

```
每个 AI session 开始时：
   S1：load Hot Cache = Track C (3 KE) + 上次 session 的活跃 KE (≤5)
   S2：根据 task_type 从 Warm 预取 → Hot (§9.4)
   S3：session 结束时：
       - 本次引用次数 ≥ 3 的 KE → 保留在 Hot（跨 session 暂留）
       - 其余 → 退回到 Warm
       - Track C → 永远留在 Hot（不 evict）
```

**与 unified_memory_api 的关系**：

```python
# 现有 API
unified_memory_api.recall(query, top_k=10)

# beta 增强
unified_memory_api.recall_with_tier(
    query=query,
    task_type="fix_bug",
    hot_cache=memory_tier.hot,      # → 优先从 Hot Cache 命中
    warm_cache=memory_tier.warm,    # → 未命中查 Warm
    cold_fallback=True              # → Warm 未命中走 ChromaDB
)
```

> **对标**：MemGPT (Packer et al., 2023) — OS-inspired tiered memory for LLMs / Letta — MemGPT 商业化版本 / Operating System memory hierarchy — L1/L2/L3 cache 原理。三者都说明：**访问频率 ≠ 知识重要性，Hot/Cold 分层可以同时给高频知识即时访问和低频知识全量保留**。
> **大白话**：你的知识库里 500 条 KE，AI 没法每 session 读 500 条。Hot 层就像浏览器的常驻标签页——Owner 的偏好、当前项目的核心规范永远开着。Warm 层是书签栏——能快速点击。Cold 层是全量搜索——不常用但需要时能找到。AI 先翻 Hot → 没找到翻 Warm → 实在不行搜 Cold——三层递进，不让 AI 在 500 条里大海捞针。

### 9.13 检索自反思（Self-RAG for Retrieval）

当前检索结果直接灌给 AI、直接信任。但检索可能返回不相关的 KE——AI 无脑采用导致幻觉或错误决策。

**Self-RAG 判定层**（在 RAG 生成前插入）：

```
检索返回 Top-K KE 列表
       │
       ▼
┌──────────────────────────────────────────┐
│ Self-Reflection Gate (Kimi K2.6)          │
│                                            │
│ Prompt:                                    │
│ "你收到了以下知识条目用于辅助回答。          │
│  逐一判定每条 KE 与当前问题的相关性：       │
│                                            │
│  KE-042: {body}                            │
│  → is_relevant: YES / NO                   │
│  → relevance_reason: ...                   │
│                                            │
│  KE-087: {body}                            │
│  → is_relevant: YES / NO                   │
│  → relevance_reason: ...                   │
│                                            │
│  仅使用 is_relevant=YES 的 KE 进行回答。"   │
└──────────────────┬───────────────────────┘
                   ▼
       ┌───────────┴───────────┐
       │                       │
   ≥ 3 条 relevant         < 3 条 relevant
   → 正常生成              → 降级：触发 §9.3 HyDE 重试
                              或 标记 answer_unsupported
```

**反馈闭环**：self-reflection 结果写入 `ke_usage_log.reflection_result`——后续用于校准检索参数。

> **对标**：Self-RAG (Asai et al., 2023) — 在 generation 前做 self-reflection 判定检索质量 / Anthropic Constitutional AI — 生成前过 harmlessness check / LangChain Self-Query Retriever — LLM 判定 query 与 doc 的关系。三者都说明：**不该盲目信任检索结果——AI 应该先审视再使用**。
> **大白话**：系统搜回来 10 条 KE，不会全喂给 AI。先让 Kimi 自己看一遍："这 10 条里哪些真的跟当前问题有关？"3 条——够用了继续。2 条——先别急着回答，改用 HyDE 重新搜。0 条——如实告诉 Owner"知识库里没有相关信息"而不是瞎编。

### 9.14 知识效果 A/B 测试（KE Effectiveness Validation）

所有 KE 只在入库时被审计——入库后就再没人验证"这条 KE 对 AI 的质量到底有没有提升"。

**设计**：

```
每周采样 5 个典型 task（覆盖不同 task_type）
       │
       ▼
┌──────────────────────────────────────────┐
│ A/B Split                                  │
│  → Group A: 注入全部 Top-K KE              │
│  → Group B: 注入 Top-K KE - 随机移除 1 条  │
│  → 两个 Group 各自生成答案                  │
└──────────────────┬───────────────────────┘
                   ▼
┌──────────────────────────────────────────┐
│ Delta 分析                                 │
│  → 对比 A 和 B 的输出质量：                │
│    - 答案完整性（是否缺少关键步骤）          │
│    - 答案正确性（是否引入错误）              │
│    - Token 效率（KE 注入是否节省了思考时间） │
│  → Δ < 0.05 = KE 对输出质量无显著贡献        │
│    → 标记 low_effectiveness → 降级或删      │
│  → Δ > 0.15 = KE 显著提升输出质量            │
│    → helpness_score +0.1                    │
└──────────────────────────────────────────┘
```

**月度报告**：

```
KE Effectiveness Report (2026-05)
─────────────────────────────────
Top 3 最有用的KE：
  1. KE-042 (Chromadb 配置) — Δ=0.23, 引用47次
  2. KE-078 (ruff error codes) — Δ=0.19, 引用38次
  3. KE-015 (pyproject.toml 模板) — Δ=0.17, 引用34次

Bottom 3 最没用的KE：
  1. KE-203 (old pylint config) — Δ=0.01, 引用1次 → 建议 DEPRECATED
  2. KE-187 (legacy setup.py) — Δ=0.02, 引用0次 → 建议 DEPRECATED
  3. KE-156 (python3.8 patterns) — Δ=0.03, 引用2次 → 建议降级
```

> **对标**：Feature flag A/B testing — 功能上线前验证效果 / Google Search ranking experiments — 每次算法变更都 A/B 对比 / Netflix A/B testing culture — 所有变更必须验证。三者都说明：**发布不是终点——效果验证才是闭环的最后一环**。
> **大白话**：现在的情况：KE-042 入库了，审计过了，质量分 0.95——完美。但没人验证过"把这 KE-042 喂给 AI 后，AI 的输出真的变好了吗？"A/B 测试每周跑一次：反着两个 AI——一个有 KE-042 一个没有——让你客观看到每条 KE 到底贡献了多少。没贡献的 KE 自动标记"没效果"降级清退——知识库不是收藏夹，只为能提升 AI 质量的知识留空间。

### 9.15 知识合并冲突（Knowledge Merge Conflict）

> **触发缺口**：五轨并行——Track 1（Session Log 提取）和 Track 5（周巡检）在同一周分别产出了 2 条候选 KE，都关于"ruff pyproject.toml 配置最佳实践"。当前 G2 Triage 只做 >0.80 向量相似度去重，但内容*部分*重叠的 KE（各讲 ruff 的不同侧面）不会被合并——最终产生 3 条独立 KE 零散地描述同一主题的不同侧面，AI 检索时需要看 3 条才能拼出完整答案。

**三级合并策略**：

```
新 KE 候选进入 G2 Triage
       │
       ▼
┌──────────────────────────────────────────┐
│ L1：向量相似度判定（已有）                  │
│  → cosine > 0.80 → DUPLICATE（直接拒绝）  │
│  → 0.60 < cosine ≤ 0.80 → 进入 L2          │
│  → cosine ≤ 0.60 → 非重复，正常入库         │
└──────────────────┬───────────────────────┘
                   ▼
┌──────────────────────────────────────────┐
│ L2：主题聚类判定（新增）                    │
│  → Kimi K2.6 prompt:                      │
│    "新候选 KE 讲的是 {新KE.title}           │
│     已有 KE [{旧1.title}, {旧2.title}]      │
│     也讲类似内容。                          │
│     判定关系：                              │
│     - SAME_TOPIC：和旧 KE 完全同一主题 →    │
│       合并到已有 KE（追加为新版本/补充段）   │
│     - SUBSET：新 KE 是已有 KE 的子主题 →    │
│       新 KE 变成已有 KE 的 depends_on 子项   │
│     - OVERLAP：部分重叠但角度不同 →          │
│       建议合并方案（如：KE-011 作为 parent，  │
│       KE-023 和 新KE 作为 child subtopics）  │
│     - DISTINCT：虽相似但确实独立主题 →       │
│       允许独立入库"                          │
└──────────────────┬───────────────────────┘
                   ▼
┌──────────────────────────────────────────┐
│ L3：合并执行                               │
│  → SAME_TOPIC → 旧 KE version bump（§9.7）│
│     + 新内容作为版本 diff 的增量部分        │
│  → SUBSET → 新 KE depends_on 指向旧 KE     │
│     + 旧 KE 追加 child_kes 字段            │
│  → OVERLAP → 生成 MERGE_PROPOSAL YAML      │
│     → 推送 Owner 审批（§7.7 L2）            │
│  → DISTINCT → 正常入库                     │
└──────────────────────────────────────────┘
```

**合并事件**：`ke_merge` → learn() → 记录哪个 KE 被合并到哪个 KE。

> **对标**：Git merge conflict resolution — 两个分支改同一文件 / Wikipedia article merging — 两篇文章讲同一主题时管理员发起合并 / arXiv deduplication — Semantic Scholar 检测多版本论文并建立 version chain。三者都说明：**多条独立记录描述同一事物 → 必须合并，否则检索碎片化**。
> **大白话**：五个轨道同时跑——就像五个工人同时在往一个知识库塞纸条。Track 1 塞了"ruff 配置"，Track 5 也塞了"ruff 配置检查"——两个讲的都是 ruff 但角度不同。系统不会让它们变成两条独立记录，而是检测到"这俩说的是一回事"→自动评估是合并到原有记录（追加版本）、变成子主题、还是需要 Owner 来决定怎么合并。

### 9.16 知识安全分级（Knowledge Safety Classification）

> **触发缺口**：KE body 可能包含内部 URL（`http://192.168.1.x:8080`）、服务端口、测试用 API key、内部路径结构等。当前 G4 Activate 在注入 AI 上下文时不做安全过滤——这些信息直接进入 LLM 上下文，存在信息泄露风险。尤其在 beta MCP Server 对外开放知识查询时，安全风险指数级放大。

**安全分级标准**：

| 等级 | 标签 | 含义 | 自动检测规则 | 注入策略 |
|:---:|------|------|------|------|
| S0 | PUBLIC | 无敏感信息，可自由分享 | 默认级别 | 正常注入 |
| S1 | INTERNAL | 项目内部信息（路径结构、服务名、端口） | 正则匹配：IP地址、`:端口号`、`/home/` 路径模式 | 仅内部 AI session 注入，MCP对外接口隐藏 body |
| S2 | RESTRICTED | 含可追溯的配置信息（API endpoint、数据库连接串结构、token格式说明） | 正则匹配：`https?://.*api`、敏感的 config key 模式 | 仅 Hot Cache 可用，不写入 ChromaDB 可检索向量（仅 SQLite 存储 metadata） |
| S3 | SECRET | 绝对禁止注入上下文的敏感凭证（任何形式的密钥、密码、token） | 正则匹配：`sk-`/`api_key`/`password`/`secret`/`token` 关键词 + 长度>20字母数字串 | **拒绝生成 KE 或自动 REDACT**——入库前强制脱敏替换为 `[REDACTED]` |

**S2 降级策略**：RESTRICTED KE 不进入 ChromaDB 向量索引 → 语义检索不会返回 → AI 不会在冷启动时"偶然读到"。仅在 hot_cache 中当 Owner 主动关联时可用。

**S3 自动脱敏示例**：

```
原始：`export OPENAI_API_KEY=sk-proj-abc123def456...`
脱敏后：`export $LLM_API_KEY=[REDACTED-S3-OPENAI]`
```

> **对标**：GitHub Secret Scanning — push 时自动检测+拦截 / AWS IAM — S3 bucket policy 限制访问 / OWASP Top 10 — A01:2021 Broken Access Control。三者都说明：**知识库不是保险柜——秘密不该出现在可检索的文本里**。
> **大白话**：你在一次 session 里写了 `http://192.168.1.100:8080/internal-api`——这是一个内部地址。现在这条信息可能变成 KE 被写进 ChromaDB，未来任何 AI session 都能搜到。安全分级后：系统自动检测到 IP+端口 → 标记 S1 → 你的内部 AI 能用，但未来如果有公共 MCP 接口，这条 KE 的 body 不会暴露。如果检测到 API key → 直接 REDACT——"不管你写了什么密钥，入库前全给你涂黑"。

### 9.17 Track C Owner 偏好 vs Track A/B 证据冲突裁决

> **触发缺口**：Owner 在 Track C 说"用 pylint"（C2/decision_preference，LOW priority，仅参考），但 Track A 积累了 23 条 A4 failure_pattern 和 5 条 A8 tool_evaluation，全部指向"ruff 在 lint 正确率、速度、误报率三个维度碾压 pylint"。当前 Track C 的 LOW priority 虽不会覆盖 Track A 证据，但系统不会显式告诉 Owner："你的偏好和累积证据矛盾了——你是坚持 pylint 还是更新偏好？"Owner 永远不知道他的偏好已经过时。

**裁决流程**：

```
每周 APScheduler cron 触发
       │
       ▼
┌──────────────────────────────────────────┐
│ S1：Track C ↔ Track A/B 冲突扫描           │
│  → 逐条 Track C KE(C2/C3)检索相关的 A/B   │
│    KE（ChromaDB cosine > 0.60）            │
│  → 对每对 C-vs-A/B 做 Kimi K2.6 判定：    │
│    "Owner 偏好'用 pylint'(C2-001)，        │
│     但 KE-A4-023 和 KE-A8-005 的证据       │
│     是否与这条偏好矛盾？"                   │
│  → 输出：ALIGNED / MISALIGNED              │
└──────────────────┬───────────────────────┘
                   ▼
       ┌───────────┴───────────┐
       │                       │
   ALIGNED                 MISALIGNED
   → 静默                  → 生成冲突简报：
                             📋 偏好冲突提醒
                             Owner 偏好：用 pylint (C2-001)
                             冲突证据：
                              - A4-023: pylint 漏报率 34% vs ruff 5%
                              - A8-005: ruff 快 47x
                              - A4-047: pylint 误报 3587 次源于一个多余反斜杠
                             动作建议：更新偏好 或 坚持原偏好+说明理由
                             → 推送 Owner（§7.7 L2 HUMAN_GATED）
```

**冲突冷却**：同一条 Track C 冲突已通知过 → 90d 内不再重复提醒。

**裁决结果**：
- Owner 选择更新偏好 → Track C KE status: SUPERSEDED，新内容写入
- Owner 选择坚持 → Track C KE 追加 `override_reason`："我知道 ruff 更好但我团队熟悉 pylint"——这个理由本身也变成知识（C3/decision_rationale 更新）

> **对标**：GitHub CODEOWNERS — repo owner 设定审批规则但 PR 被 evidence 压倒时 owner 重新评估 / Google "data beats opinion" culture — 无论谁说的，数据说了算 / Decision intelligence (Google) — 决策应基于证据而非权威。三者都说明：**偏好可以被保留，但不能在证据面前不被提醒**。
> **大白话**：你说你喜欢 pylint——没问题，这是你的个人偏好，Track C 记下来了。但系统每个月会自动跑一次冲突扫描：如果累积证据显示"pylint 漏报了 34% 的 bug、ruff 比它快 47 倍"——系统会推一条消息给你："你的偏好和证据矛盾了，要更新吗？"你点"坚持"→系统记下你的理由（"团队用惯了"），偏好照旧。你点"更新"→偏好自动改为 ruff。你不是被系统碾压，而是被自己的数据提醒——最终决定权永远在你手上。

---

## §10 迁移/废弃方案

### 10.1 退役蓝图迁移路径

| 退役内容 | 退役日期 | 迁移目标 | 状态 |
|---------|---------|---------|:---:|
| `task-card-kms/blueprint.md`（MOD-INF-003） | 2026-05-02 | KMS部分→本蓝图；任务卡部分→MOD-INF-006 | ✅ 已完成 |
| `construction-plan-task-card-and-kms.md` | 2026-05-02 | 并入 MOD-INF-003→本蓝图 | ✅ 已完成 |
| 候选池11个KB相关文件 | 本 session | 提取全部KB内容→本蓝图，源处留痕删除 | 🔄 本 session |

### 10.2 候选池KB内容提取记录（留痕）

> 以下文件的知识库内容已全量提取至本蓝图。提取后源文件中KB专属内容已删除，
> 仅保留非KB内容（如任务系统、脚本架构、基础设施等其他模块的设计）。
> 删除处标注了本蓝图的完整链接。

| # | 候选池源文件 | 提取的KB内容 | 质量对比结论 |
|:--:|------------|------------|------------|
| 1 | `03-知识库架构.md` | G1-G5门禁、10状态机、MCP协议、上下文预算、多Agent记忆、Embedding管理、知识衰减、安全架构、4轮审计结果、CLI命令、Phase计划（全文件唯一主题=知识库） | 候选池远优于退役蓝图 |
| 2 | `知识库升级方案.md` | 5并行分类系统诊断、3阶段升级计划、419+ KE现状分析、10阶段学术对标 | 退役蓝图无此内容 |
| 3 | `vibe-coding-task-card-and-knowledge-base-design.md` | 混合聚类架构（layer为主+domain为辅）、3阶段持续摄取策略、KB-Agent Harness集成、formal invariants、TagSchemaRegistry需求、Provenance Chain需求 | 候选池设计更系统化 |
| 4 | `知识库专题讨论文档.md` | 30 KB问题（KB-001~030）、ADR矛盾裁决（ADR-0005 vs ADR-0016）、KE ID格式冲突裁决（KE-{NNN} vs KMS-{YYYYMMDD}-{SEQ}）、3并行分类系统文档、知识库空洞化诊断 | 退役蓝图无此类深度诊断 |
| 5 | `01-脚本系统架构.md` §32~§40 | 14组件技术选型（#2 ChromaDB、#3 Embedding）、beta KMS交付物+验收标准、beta KB组件清单（triage/kb_repo/batch_ingest/chromadb_init）、Qwen务实修正（6条：向量DB/Embedding模型版本选择） | KB相关部分已提取，脚本系统部分保留 |
| 6 | `vibe-coding-infrastructure-7-modules-design.md` §M3 | M3记忆系统（短期/中期/长期三层）、kb/代码状态、vector_memory差距、统一API(remember/learn/forget/recall)、知识归属决策（蓝图→KE系统）、知识库存放架构参考 | KB部分已提取，其余7模块设计保留 |
| 7 | D0-knowledge四指令（011/022/033/044） | 四模型审计分工方法论（GLM扫描→Kimi结构→Qwen索引→Opus裁决）、知识提取六维矩阵（K1-K6）、知识去重策略、知识入库4步法 | 方法论已参考纳入，源文件保留作为施工执行指令 |

### 10.3 kb/→VMS 整合路径

```
2（当前）：kb/ 独立运行
  src/zephyr/kb/  →  12模块 ✅
  vector_memory/  →  空包（__init__.py only）

beta（计划）：kb/ 能力纳入 VMS
  src/zephyr/kb/  →  DEPRECATED（不删，保留退役标记）
  src/zephyr/vector_memory/  →  InProcessVectorMemory 完整实现
  unified_memory_api.py  →  作为 VMS 的统一入口保留

迁移契约：P1-KB-VMS-TRANSITION（定义在 b_kb.yaml interfaces）
```

### 10.4 KE 退役与清理

- **过期检测**：`freshness < 0.3` → Session Log 标注 `⚠️ 知识过期警告`
- **退役流程**：VERIFIED → DEPRECATED →（30d冷却期）→ ARCHIVED
- **物理删除**：ARCHIVED 30d 后 → 确认无引用 → `git rm`
- **禁止**：跳过 DEPRECATED 直接物理删除（必须留30天窗口让消费者迁移）

---

## §11 施工 Phase 规划

### experimental（已完成 ✅）：核心门禁 + ChromaDB 初始化

**目标**：知识库核心引擎——让 AI 能"存知识"和"查知识"。

**交付物**：

| # | 组件 | 路径 | 状态 |
|:--:|------|------|:---:|
| 1 | ChromaDB 4C 初始化 | `src/zephyr/kb/chromadb_init.py` | ✅ |
| 2 | G1 Ingest 门禁 | `src/zephyr/kb/ingest.py` | ✅ |
| 3 | G2 Triage 门禁 | `src/zephyr/kb/triage.py` | ✅ |
| 4 | G3 Analyze 门禁 | `src/zephyr/kb/analyze.py` | ✅ |
| 5 | G4 Activate 门禁 | `src/zephyr/kb/activate.py` | ✅ |
| 6 | G5 Extract 门禁 | `src/zephyr/kb/extract.py` | ✅ |
| 7 | 核心仓储(10状态机+SQLite+ChromaDB) | `src/zephyr/kb/kb_repo.py` | ✅ |
| 8 | 批量入库管道 | `src/zephyr/kb/batch_ingest.py` | ✅ |
| 9 | 图谱完整性校验 | `src/zephyr/kb/graph_validator.py` | ✅ |
| 10 | Embedding 迁移管线 | `src/zephyr/kb/embedding_migrate.py` | ✅ |
| 11 | RI-02 统一内存 API | `src/zephyr/kb/unified_memory_api.py` | ✅ |
| 12 | 单元测试（8个测试文件） | `tests/unit/test_*.py` | ✅ 8/8 |

**验收结果**：
- 代码：3600+ 行 Python，12 模块 ✅
- 测试：8/8 通过 ✅
- 知识数据：**⚠️ 引擎已建，知识库仍为空**——仅 `docs/08_knowledge/index.md` 骨架存在，32条 KE 未经过 G1-G5 管道正式处理

---

### beta（当前 🔄）：知识填充 + 检索升级 + 反馈闭环 + 漏斗机制

**目标**：把空知识库填满 + 两阶段重排序上线 + 反馈数据闭环启动 + KO→KE→KB 三级漏斗自动化。

**触发条件**：experimental 验收全部通过 + 本蓝图定稿（本 session）。

**交付物**：

| # | 任务 ID | 内容 | 优先级 |
|:--:|---------|------|:---:|
| 1 | KB-INF-0001~0010 | 候选池KE批量迁移——第3.1节的7个候选池文件中的全部KB设计内容通过G1-G5管道正式入库 | P0 |
| 2 | KB-INF-0011 | `batch_ingest.py` ↔ Session Log 自动提取管线打通——含 §5.10 五级切片边界信号实现 | P0 |
| 3 | KB-INF-0012 | `context_assembler` ↔ `unified_memory_api.recall()` 集成——AI session 开始时自动注入相关KE（含 §5.9 两阶段重排序） | P0 |
| 4 | KB-INF-0013 | `feedback_collector.py` 实现——门禁阻断/验证失败/幻觉事件自动收集 | P0 |
| 5 | KB-INF-0014 | **新增**：`reranker.py` 实现——BGE-reranker-v2-m3 Cross-Encoder 重排序层，含降级策略 | P0 |
| 6 | KB-INF-0015 | **新增**：KE 反馈字段落地——§3.2 四个新字段写入 SQLite Schema + `learn()` 五种事件类型扩展 + 动态 `quality_score` 公式 | P0 |
| 7 | KB-INF-0016 | `docs/08_knowledge/index.md` 更新——从手动维护迁移到自动生成 | P1 |
| 8 | KB-INF-0017 | three-layer memory (Hot/Warm/Cold) 与 KB 的映射关系文档化 + 代码层实现 warm-memory 触发逻辑 | P1 |
| 9 | KB-INF-0018 | KO→KE→KB 漏斗升格阀值自动化——≥3 KO 同主题 → 触发 D0 四轮流水线聚合为 KE；≥5 KE 同领域 → 触发 KB 升格评审提示 | P1 |
| 10 | KB-INF-0019 | **新增**：`detect_knowledge_gaps.py` 实现——§5.12 L2/3 四维覆盖率检查（零结果query + failure_feedback + AGENTS.md rule ↔ KE + 蓝图↔KE）| P1 |
| 11 | KB-INF-0020 | **新增**：`trigger_table.yaml` 落地——§5.12 L1 文件修改模式→KE category 自动推送，集成到 `context_assembler.recall(trigger_context=...)` | P1 |
| 12 | KB-INF-0021 | **新增**：`extract.py` EXTRACTION_TEMPLATES 扩展——5→10 templates（覆盖 §5.11 Track A 全部 5 类 + Track B 全部 5 类 source_type）| P1 |
| 13 | KB-INF-0022 | **新增**：`schemas.py` KeCategory 枚举重构——废弃原有金融域 6 类 + 新增 §3.8 施工域 15 类 + 向后兼容迁移逻辑 | P0 |
| 14 | KB-INF-0023 | **新增**：`install-hooks.py` 实现——自动安装 post-commit hook（触发轨道1）+ pre-commit failure capture（触发轨道2）| P0 |
| 15 | KB-INF-0024 | **新增**：`scheduler.py` + 通知系统——APScheduler cron 三任务（周巡检+月清理+日衰减）+ Owner 审批提醒推送（轨道4 yes/no）| P1 |

**验收标准**：

| 维度 | 指标 | 目标值 |
|------|------|:---:|
| 知识数量 | KE 条目数 | ≥ 50（含候选池迁移32+条 + Session提取） |
| 检索精度 | 两阶段检索 Top-3 准确率（§5.9） | > 80%（含reranker后） |
| 自动提取 | Session Log→KE 自动化率（轨道1） | ≥ 70% |
| 分类覆盖 | 15类 category 中已覆盖类别数 | ≥ 8（A1-A8 全部 + B1-B3 至少2个） |
| 防遗漏 | L2 Coverage Gap 周检启动 | ✅ detect_knowledge_gaps.py 成功运行 1 次 |
| 上下文节省 | 知识注入后 Token 重复消耗降低 | > 20% |

---

### beta（中期 🔮）：MCP 集成 + 四模型审计自动化 + BGE-M3 升级

**目标**：跨Agent知识互通 + 全自动审计 + 生产级向量检索

**触发条件**：beta 验收全部通过 + 向量库条目 > 100。

**交付物**：

| # | 任务 ID | 内容 | 优先级 |
|:--:|---------|------|:---:|
| 1 | KB-INF-0020 | MCP Server KB——4 Resource(ke_query/bp_search/rule_lookup/audit_trail) + 4 Tool(ingest_ke/audit_ke/deprecate_ke/export_ke) | P0 |
| 2 | KB-INF-0021 | 四模型审计流水线自动化——G4 Activate→GLM→Kimi→Qwen→Opus 全自动触发 | P0 |
| 3 | KB-INF-0022 | Embedding 升级——all-MiniLM(384d)→BGE-M3(1024d) | P1 |
| 4 | KB-INF-0023 | kb/→VMS 迁移——`vector_memory/` InProcessVectorMemory 实现，kb/设为 DEPRECATED | P1 |
| 5 | KB-INF-0024 | 多Agent交叉一致性校验——Claude/Kimi/Qwen/GLM 四者知识库同步一致性检查 | P1 |
| 6 | KB-INF-0025 | Context压缩机 L0-L3 策略——长KE自动摘要压缩 | P2 |

---

### stable（远期 🔮）：知识生态 + 自进化 + 外部抓取

**目标**：知识库成为 AI 的"长期外置大脑"——自动从外部学习、自动进化、自动清理。

**触发条件**：beta 验收全部通过 + 累计 session > 50。

**交付物**：

| # | 任务 ID | 内容 | 优先级 |
|:--:|---------|------|:---:|
| 1 | KB-INF-0030 | GitHub 开源项目知识抓取管道——自动扫描 vibe-coding/quant-finance 相关 repo → 提取KE | P0 |
| 2 | KB-INF-0031 | arXiv 论文自动提取——quant-finance/q-fin 分类论文 → KE | P1 |
| 3 | KB-INF-0032 | `knowledge_decay_engine.py`——自动检测过期KE、触发DEPRECATED流转 | P1 |
| 4 | KB-INF-0033 | `hallucination_loop_detector.py`——多Agent幻觉传播循环检测(NetworkX图遍历) | P1 |
| 5 | KB-INF-0034 | `evolution_engine.py`——知识自动进化规则引擎（基于反馈信号自动调整KE内容） | P2 |
| 6 | KB-INF-0035 | 知识质量仪表盘(Streamlit)——KE总量/分类分布/新鲜度趋势/审计通过率可视化 | P2 |

---

## §12 施工指引

### 11.1 本蓝图定稿后的立即行动

1. **更新架构 YAML SSoT**：修改 `b_kb.yaml`，将 status 从 `implemented` 更新为 `implemented`（不变），更新 `note` 和 `modules.description` 引用本蓝图
2. **更新 `_index.yaml`**：确认 `b_kb.yaml` 在 b_track 中正确注册
3. **候选池KB内容清理**：逐文件删除已提取的KB专属内容，留痕（§9.2）
4. **创建 `knowledge-base/index.md`**：模块入口索引文件

### 11.2 施工顺序依赖

```
experimental (✅ 已完成)
    │
beta (🔄 当前)
    ├── KB-INF-0001~0010 (候选池KE迁移)
    │       └── 依赖：本蓝图定稿
    ├── KB-INF-0011 (Session Log 自动提取)
    │       └── 依赖：batch_ingest.py ✅
    ├── KB-INF-0012 (context_assembler 集成)
    │       └── 依赖：unified_memory_api.py ✅ + MOD-INF-006 §5.1
    └── KB-INF-0013~0015 (反馈+索引+三记忆层)
            └── 依赖：KB-INF-0001~0010 完成后
    │
beta (🔮 计划)
    └── 依赖：beta 全部验收通过 + 向量库 > 100 KE
```

### 11.3 文件创建约束

- 每次 session 新建文件 ≤ 5 个（AGENTS.md §5.1 认知约束）
- 所有路径使用绝对路径
- 所有 Python 文件必须通过 ruff + mypy + pytest 三阶段质检
- 知识文件（KE .md）必须标注 UTF-8 编码、无BOM、LF换行

### 11.4 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|:---:|:---:|------|
| 知识库空洞化持续（引擎建了但没知识） | 高 | 🔴 高 | beta 优先填充候选池KE+Session提取 |
| 重排序模型下载失败（BGE-reranker首次需联网） | 中 | 🟡 中 | 降级策略：跳过重排→纯ChromaDB Top-10，日志警告 |
| 反馈数据污染（自动化标记的adoption/helpfulness不准） | 低 | 🟡 中 | `quality_score` 公式中静态评分权重40%兜底；异常反馈率超50%时触发人工审计 |
| KE漏斗堵死——KO大量创建但无人升格KE→KB | 中 | 🟡 中 | KB-INF-0018 自动化阀值触发 + 月度审计KO→KE→KB转化率 |
| Embedding 模型升级导致向量不兼容 | 中 | 🟡 中 | `embedding_migrate.py` 已实现迁移管线 |
| 多Agent知识冲突无法自动裁决 | 中 | 🟡 中 | Opus 4.7 终审裁决 + 冲突升级到人工 |
| kb/→VMS 迁移破坏现有功能 | 低 | 🔴 高 | beta 迁移期间 kb/ 保留运行，新写入双写，确认稳定后再 DEPRECATE |
| 上下文注入过多导致 Token 超预算 | 低 | 🟡 中 | Top-K ≤ 10, token ≤ 2000 硬约束 |
| KeCategory 枚举重构破坏现有 KE 分类查询 | 中 | 🟡 中 | 向后兼容迁移逻辑：`old_category → new_category` 映射表 + SQLite ALTER 而非 DROP |
| 五轨提取某条轨道阻塞导致知识持续遗漏 | 中 | 🔴 高 | 每条轨道有独立日志+错误计数；轨道5定期巡检兜底发现异常 |
| Trigger Table 配置错误推错 KE 给 AI | 低 | 🟡 中 | L4 季度抽检可发现——实际用的 KE 和预期不符 |
| 15 类 category 中某些类别长期空白（无人关注） | 中 | 🟡 中 | L2 Coverage Gap 周检按 category 维度输出空白度报告 |
| Git hook 安装失败导致轨道1/2全静默停摆 | 高 | 🔴 高 | `install-hooks.py` 运行后自动验证 hook 文件存在+可执行；每次 session 开始 context_assembler 自检 hook 健康 |
| 审批提醒推送失败 Owner 不知有知识待审 | 中 | 🟡 中 | KO 7d 无响应自动丢弃，不阻塞；推送失败日志报警 |
| 自动 D0 流水线消耗大量 LLM token | 中 | 🟡 中 | 仅当 session 日志中出现新链接时触发（非每 session）；月度 Token 预算上限 |
| 知识漂移（KE 渐近失真而非 binary 过期） | 高 | 🟡 中 | 当前 TTL 只处理"有效/过期"二元态。渐变失真（"ChromaDB 从最佳→还行→过时"）无法检测。beta `knowledge_decay_engine.py` 引入连续 `freshness` 评分+交叉验证触发降级 |
| 时间窗口 KE（B1-B7）在非活跃期仍被检索 | 中 | 🟡 中 | 新增 `valid_from`/`valid_until` 字段（§3.2），context_assembler 检索时自动过滤 `valid_until < today()` 的 KE |
| KE 安全信息泄露（S1-S3 分级失效） | 低 | 🟡 中 | §9.16 S0-S3 安全分级 + G4 Activate 注入前过滤 + S3 REDACT 脱敏 |

---

## §16 容量与性能约束

> **module_id**: MOD-KB-001 §16 | **对标**: capacity-assurance (MOD-INF-001) §5 全局容量预算

### 16.1 KE 总数硬约束

| 约束 | 值 |
|------|----|
| 单 domain 上限 | ≤ 500 KE |
| 全库上限 | ≤ 2000 KE |
| 超限处理 | 触发 KE_SATURATION WARNING 事件 → Feedback Loop Engine 消费 |
| 告警阈值 | KE 总数 > 80% 上限 → FLE 告警 → Script System D1 扫描 |

### 16.2 ChromaDB Collection 约束

| 约束 | 值 |
|------|----|
| 单 Collection 向量上限 | ≤ 10,000 vectors（BGE-M3 1024d ≈ 40MB） |
| 超限处理 | 自动归档最旧 20% 的 KE（按 `created_at` 排序）→ `_archive/` 目录 |
| 归档保留 | 向量删除，MD 文件保留——可随时从 MD 重建向量 |
| 恢复上游 | 归档触发 ARCHIVE_BUDGET_EXCEEDED 事件 → Telemetry 记录 |

### 16.3 检索性能 SLO

| 指标 | 目标 | 测量方式 |
|------|:---:|------|
| `ke_entries` 检索 P99 | ≤ 200ms | ChromaDB 内建 query latency |
| 混合检索（BM25 + 向量）P99 | ≤ 500ms | `hybrid_search()` 全链路耗时 |
| 重排序阶段 P99 | ≤ 300ms | BGE-reranker-v2-m3 Cross-Encoder |
| 全链路 Top-10 召回 P99 | ≤ 1000ms | RAGAS 评估采样 |
| 降级策略 | P99 > 2000ms → 跳过重排 → 纯 ChromaDB Top-10 | 日志告警 |

### 16.4 衰减与容量联动

| 触发条件 | 操作 | 联动 |
|------|------|------|
| `half_life_days` 到期 | KE status → DEPRECATED | `knowledge_decay_engine.py`  |
| DEPRECATED 30 天后 | KE status → ARCHIVED | 向量删除，MD 保留 |
| ARCHIVED KE 占库 > 20% | 触发 `_archive/` 清理审批 | Owner 人工裁决物理删除 |

### 16.5 容量告警矩阵

| 告警事件 | 阈值 | 消费者 | 响应 |
|------|:---:|------|------|
| KE_SATURATION | > 80% 总上限 | Feedback Loop Engine | Script System D1 全量扫描 |
| COLLECTION_NEAR_LIMIT | > 80% 单Collection上限 | Feedback Loop Engine | 预归档建议 |
| RETRIEVAL_SLO_VIOLATION | P99 > 2000ms（连续3次采样） | Telemetry + FLE | Hybrid → Pure ChromaDB 降级 |
| ARCHIVE_BLOAT | 归档 KE > 20% 全库 | Task System | 创建 Owner 审批任务 |

### 16.6 容量预测

对齐 `capacity-assurance` (MOD-INF-001) §17 容量预测模型：

- **新增 KE 速率**：beta 预计 ~50 KE/month（候选池迁移 + Session 提取）
- **衰减速率**：约 30% KE 的 `half_life_days` < 90d → 月衰减 ~15 KE
- **净增长**：~35 KE/month → 2000 上限 / 35 = **57 个月**缓冲区
- **审查频率**：每月 1 日在 Feedback Loop Engine 输出容量趋势报告

---

## §13 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 0.6.5 | 2026-05-04 | 第二轮盲点清零五合一：①**§9.15 知识合并冲突**——五轨并行同主题KE合并的三级策略（L1向量相似度>0.80拒绝/L2 Kimi主题聚类SAME_TOPIC|SUBSET|OVERLAP|DISTINCT/L3合并执行+ke_merge事件）；②**§9.16 知识安全分级**——S0-S3四级分类（PUBLIC/INTERNAL/RESTRICTED/SECRET）+正则自动检测+S3 REDACT脱敏+ChromDB索引降级策略；③**§9.17 Track C vs A/B冲突裁决**——每周Owner偏好vs累积证据矛盾扫描+ALIGNED/MISALIGNED判定+冲突冷却90d+Owner最终裁决权保留；④**§3.2 KE Schema 新增 valid_from/valid_until**——时间窗口有效性字段，Track B金融KE专用，检索时自动过滤过期KE；⑤**§7.3 多语言标注+BGE-M3原生中英混合** + **§11.4 风险表 +3条目**（知识漂移渐进失真+时间窗口检索污染+安全信息泄露）。联动：b_kb.yaml partition note同步更新 |
| 0.6.4 | 2026-05-04 | 知识检索与演化回路（14子节补齐"出库+演化"空白）：①**§9.1 检索质量度量**——RAGAS四维指标(answer_relevance/faithfulness/context_precision/context_recall)+RAGMetricEvaluator实现+每周APScheduler cron全量评估；②**§9.2 混合检索**——BM25稀疏向量+ChromaDB稠密向量+RRF融合+Cross-Encoder重排；③**§9.3 查询改写**——Multi-Query生成+HyDE假答案embedding+去重合并（仅Top-1<0.60时启用）；④**§9.4 上下文预算动态分配**——6类task_type自适应Top-K+Token预算+注入焦点矩阵；⑤**§9.5 KB规则执行引擎**——pre-commit动态读取KB YAML→生成临时检查项→阻断溯源；⑥**§9.6 知识溯源**——W3C PROV三级(L1 KE溯源+L2引用追踪+L3 RAG Trace)+ke_usage_log表；⑦**§9.7 KE版本历史**——v1.0/v1.1/v2.0目录+versions.yaml+MAJOR.MINOR semver规则；⑧**§9.8 依赖级联**——deprecated→反向索引查询→GREEN/YELLOW/RED三级评估→自动标记NEEDS_REVIEW；⑨**§9.9 去重聚类**——UMAP降维+HDBSCAN聚类+Kimi cluster summary合并建议；⑩**§9.10 Token预算**——月度14管道预算明细(¥0.40/月)+¥5.00硬上限+P0-P3四级背压降级；⑪**§9.11 多模态知识**——beta预留CLIP/CogVLM截图embedding；⑫**§9.12 三级记忆**——MemGPT对标Hot/Warm/Cold温度分层+unified_memory_api.recall_with_tier()；⑬**§9.13 检索自反思**——Self-RAG判定层(≥3条relevant→继续/<3条→HyDE重试/0条→answer_unsupported)；⑭**§9.14 效果A/B测试**——每周5task采样+Group A/B split+Delta分析+月度effectiveness报告。文档重编号：§9→§10～§12→§13。联动：b_kb.yaml partition note同步更新 |
| 0.6.3 | 2026-05-04 | CTR跨层契约对齐+Schema稳定性+灾难恢复：①**§3.9.1 来源矩阵**——ADR定稿行→跨层契约(CTR)版本升级 + 新增第8条CTR运行时质量信号管线（CTR-001 quality_score/CTR-002 confidence/CTR-005 slippage连续超阈值→KE B1/B3）；②**§3.2 KE Schema字段稳定性分级**——对标CTR locked-5yr，28字段分frozen(11)/extendable(9)/runtime_only(5)三级，frozen字段3年不删不改类型；③**§7.8 灾难恢复**——从MD全量重建SQLite+ChromaDB的5步流程+RTO<25min/RPO=0（MD在Git零丢失）+每日SQLite备份cron。联动：b_kb.yaml partition note同步更新 |
| 0.6.2 | 2026-05-04 | 技术债清零四合一：①**ISSUE-003**——5份治理规则旧ADR引用全量替换（registry-master-index.yaml REG-ADR-001 status→deprecated + session-log-schema.yaml update_adr→update_decision_record + doc_type-vocabulary.yaml adr doc_type标记废弃 + _registry/catalogs/index.md adr-status-registry标记冻结 + PS-IDX-001 index.md ADR行标注已冻结）；②**ISSUE-006**——§7.6.5 决策一致性检查（新A2 KE创建时Cross-Encoder扫描历史决策→Kimi K2.6矛盾断言→NO_CONFLICT/AMBIGUOUS/CONTRADICTION三级判定→Owner裁决+SUPERSEDED联动+semver版本链）；③**ISSUE-008**——§7.7 Human-Gated写入权限模型（AUTO/HUMAN_GATED/OWNER_ONLY三层权限矩阵+L2推送Owner yes/no流程+Owner月耗时≤12min预算+拒绝冷却机制+pending_approval字段）；④**ISSUE-009**——AGENTS.md §8.3新增知识库蓝图冷记忆引用（MOD-KB-001 §3.9.5 §3.9.1）。联动：b_kb.yaml partition note 同步更新 |
| 0.6.1 | 2026-05-03 | ADR 体系废弃执行+决策记录模型修正：①新增 §3.9.5 三层决策记录模型（L1=Owner画像/Track C、L2=AGENTS.md §10 历史决策、L3=KE A2 深度决策），基于 8 个氛围编程社区调研（Claude Code/Cursor/vertu.com/CHOP——7/8 不用传统 ADR，一句话决策贴进上下文文件）；②§3.9.1 来源矩阵 ADR 行→决策记录分流（L2 AGENTS.md / L3 KE A2）；③§5.11 轨道3 ADR→决策信号检测；④旧 ADR 迁移方案（adr_migrate.py：36 份→一句结论→AGENTS.md §10 / 深度→KE A2 + 原文件归档）。联动：b_kb.yaml partition note 同步更新 |
| 0.6.0 | 2026-05-03 | 分类体系升级 + 聊天知识自动化 + 数据库物理布局 + AI自治预留：①§3.8 双轨15类→三轨18类（+Track C：Owner决策画像 C1/C2/C3——全LOW priority、30d TTL、仅参考不强制执行，对标 Anthropic Claude implicit preference + GitHub Copilot user style learning）；②§3.8 Track D AI-AI协作知识预留桩（D1/D2/D3 + 接口契约，beta实现，对标 Terraform provider contract / K8s planned API）；③§3.9.4 聊天记录→知识提取器（S1语义分段器+S2三元判定器+N-01~N-04噪音四门槛+三触发时机，对标 vibe-coding-mcp）；④§4.0 数据引擎物理布局（data/sqlite/+chroma/+cache/ 与 Markdown KE 物理分离 + 环境变量驱动 + .gitignore 三级策略，对标 12-Factor App §3 + ChromaDB 官方 + SQLite 最佳实践）。联动：b_kb.yaml partition note 同步更新 |
| 0.5.0 | 2026-05-03 | KE/KO/KB 物理存储格式全部定稿：①§3.2.2 KE Markdown 物理格式（YAML frontmatter 18字段 + body 5段模板 + 6条 G1 格式校验规则 + 运行时字段 SQLite only 隔离）；②§3.10 KO 存储格式（4 状态机 + 轻量模板 + OBSERVED→PROMOTING→PROMOTED 晋升链路）；③§3.11 KB 存储格式（3 状态机 + YAML rule 定义 + MINOR 自动合并 + 90d 冷却机制）；④§4.2 目录结构重写——旧 5 分类目录（blueprint_decision/best_practice/factor/failure_pattern/guardrail）→§3.8 双轨 15 类体系（track_a_vibe_coding 8 类 + track_b_finance 7 类 + ko/ + kb/ + _archive/）；⑤文件命名规范（KE/KO/KB 三套独立编号池 + slug 生成规则）；⑥§7.6 三层存储同步机制（MD→SQLite→ChromaDB 派生链 + 5 道一致性校验闸门 + 冲突裁决规则 + KO/KB 同步策略差异）。联动：b_kb.yaml partition note 同步更新 |
| 0.4.0 | 2026-05-02 | 知识来源与全自动化补入：①§3.9 七来源全自动获取决策矩阵（含聊天记录→KE决策树 + Session Log最小YAML格式约定，对标 Vasilopoulos/Horthy auto-handoff-log）；②§5.13 零Owner手动触发全自动提取策略（git hook驱动3触发器工程伪代码 + APScheduler cron三任务 + Owner月耗时≤25min预算）。同步更新 §10 Phase2（+2新任务）、§11.4（+3新风险）|
| 0.3.0 | 2026-05-02 | 专业机构+氛围编程社区对标后补入：①§3.8 双轨15类知识分类体系（Track A 8类施工知识 + Track B 7类金融知识，对标 Vasilopoulos 65/35实证比例 + vibe-init 10类59策略 + n1n.ai 优先级三分法）；②§5.11 五轨并行知识提取管道（Session自动→门禁阻断→ADR变更→外部注入→差距巡检，对标 Vasilopoulos Trigger Table + OpenAI AGENTS.md动态反馈 + n1n.ai priority classification）；③§5.12 四层防遗漏哨兵体系（Trigger Table + Coverage Gap Analyzer + Rule-KE Sync + Quarterly Audit，含trigger_table.yaml和detect_knowledge_gaps.py工程细节）。同步更新 §10 Phase2（+4新任务）、§11.4（+4新风险）、EXTRACTION_TEMPLATES扩展 |
| 0.2.0 | 2026-05-02 | 专业对标审查后补入三大缺口：①§5.9 两阶段重排序（BGE-reranker-v2-m3 Cross-Encoder，对标 Meta/Cohere/Google RAG 标准）；②§3.6 KO→KE→KB 三级知识漏斗（对标 ITIL DIKW 金字塔 + Archerob Chunk 策略）+ §5.10 五级切片边界信号；③§3.7 KE 运行时反馈字段（usage_count/adoption_count/helpfulness_score/last_used_at）+ 动态 quality_score 公式 + learn() 五种事件类型扩展。同步更新 §3.2/Schema/§4.1/§7.4/§8.2/§10 Phase2/§11.4 |
| 0.1.0 | 2026-05-02 | 初始创建——从候选池7个KB相关文件提取全部知识库设计内容，经质量对比（远优于退役MOD-INF-003蓝图）后择优纳入。覆盖§1~§12全部章节，对齐 MOD-INF-006 结构和 task_id 格式 |

---

## 6. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 知识库——API骨架已实现，G1-G5门禁待beta

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/kb/activate.py` | ✅ 已实现 | |
| `src/zephyr/kb/analyze.py` | ✅ 已实现 | |
| `src/zephyr/kb/batch_ingest.py` | ✅ 已实现 | |
| `src/zephyr/kb/chromadb_init.py` | ✅ 已实现 | |
| `src/zephyr/kb/embedding_migrate.py` | ✅ 已实现 | |
| `src/zephyr/kb/extract.py` | ✅ 已实现 | |
| `src/zephyr/kb/graph_validator.py` | ✅ 已实现 | |
| `src/zephyr/kb/ingest.py` | ✅ 已实现 | |
| `src/zephyr/kb/kb_repo.py` | ✅ 已实现 | |
| `src/zephyr/kb/triage.py` | ✅ 已实现 | |
| `src/zephyr/kb/unified_memory_api.py` | ✅ 已实现 | |

### 6.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/unit/test_ingest.py` | ✅ 已实现 | |
| `tests/unit/test_triage.py` | ✅ 已实现 | |
| `tests/unit/test_analyze.py` | ✅ 已实现 | |
| `tests/unit/test_activate.py` | ✅ 已实现 | |
| `tests/unit/test_extract.py` | ✅ 已实现 | |
| `tests/unit/test_batch_ingest.py` | ✅ 已实现 | |
| `tests/unit/test_kb_repo.py` | ✅ 已实现 | |
| `tests/unit/test_graph_validator.py` | ✅ 已实现 | |
| `tests/unit/test_unified_memory_api.py` | ✅ 已实现 | |
| `tests/unit/test_embedding_migrate.py` | ✅ 已实现 | |
| `tests/unit/test_knowledge_activation_rate.py` | ✅ 已实现 | |

### 6.3 配置文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `config/embedding_model_registry.yaml` | ✅ 已实现 | |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
