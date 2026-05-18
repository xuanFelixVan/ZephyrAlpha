---
module_id: PS-STD-005
title: ZephyrAlpha 蓝图体系架构标准 — 三级金字塔与目录归属
doc_type: standard
status: active
version: "1.1.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-06"
valid_from: "2026-05-06"
summary: "ZephyrAlpha 蓝图体系的元标准——定义蓝图的**三级金字塔**（System 级总蓝图 / Domain 级域集成蓝图 / Module 级模块蓝图）、每级蓝图的**目录存放位置**、**蓝图 ID 命名约定**、**归属与引用关系**（每份蓝图 MUST 声明 belongs_to 上级蓝图）、**AI Agent 的蓝图定位规则**（新 session 冷启动如何逐级定位）。v1.1.0：§10 禁止行为新增 #7（禁止创建平行蓝图覆盖已有功能域）+ §3.3 升级为"创建条件+前置闸门"双列表——Level 2 创建前 MUST 通过 GOV-MOD-001 §7 #5 功能域重叠检查。对标 Codified Context (arXiv 2602.20478) 三层记忆模型 + Microsoft Edge AI master-blueprint 体系 + HP Inc specification.md 与 blueprint.md 双层分离 + TOGAF Architecture Repository Structure + ITIL SACM CI Hierarchy。"
ttl: permanent
tags: [blueprint-architecture, meta-standard, three-tier-pyramid, master-blueprint, domain-integration, module-blueprint, belongs-to, ssot, codified-context, three-tier-memory]
rule_form: structural
scope: global
stability: evolving
verifiability: manual
depends_on:
  - {target: PS-STD-000, at: "全篇", why: "宪法——本标准属于登记表层，不违反宪法不可逆性原则"}
  - {target: PS-STD-001, at: "§2~§7", why: "frontmatter 字段合法值"}
  - {target: PS-STD-002, at: "§3.1~§3.2", why: "L1 标准子类型格式定义型——本标准属于格式定义型，选择对应章节集"}
ai_autonomy: immutable_core
---
# ZephyrAlpha 蓝图体系架构标准

> **module_id**: PS-STD-005 | **version**: 1.0.0 | **status**: active | **layer**: cross_layer

> 本标准是 ZephyrAlpha 蓝图体系的**元标准**——定义蓝图的三级金字塔结构。
>
> **根因**：现有 19 份蓝图全部平铺在 `03_modules/l01_infrastructure/` 下，没有任何层级归属声明。
> 新 AI session 打开项目后，不知道"哪份蓝图是总蓝图、哪份是子蓝图、子蓝图归属于哪个总蓝图"。
> 当项目从 19 份蓝图扩展到 100+ 份蓝图（14 层 × 多域）时，扁平化将不可持续——新蓝图不知道在哪个目录创建、与谁建立引用关系。
>
> **对标**：
> - **Codified Context** (arXiv 2602.20478, 2026-02)：三层记忆模型——Tier 1 热记忆宪法（~660 行每 session 自动加载）→ Tier 2 领域专家 Agent（19 个按触发条件加载）→ Tier 3 冷记忆知识库（34 份 MCP 按需检索）
> - **Microsoft Edge AI**：`master-blueprint/`（总蓝图）→ `blueprints/{domain}/`（领域蓝图）→ `src/{component}/`（组件库）。总蓝图只定义组件如何组合。
> - **HP Inc AI Blueprints**：`specification.md`（蓝图总设计——"放哪、怎么命名"）+ `blueprint.md`（具体架构）。两层分离。
> - **TOGAF**：Architecture Repository 按层存放（Architecture Landscape / Reference Library / Standards Information Base / Governance Log）
> - **ITIL SACM**：CI Hierarchy（Logical CI → Physical CI，逐级细化）
>
> **本标准与 PS-STD-002 的关系**：
> - PS-STD-002（标准文档模板）管"**单个标准怎么写**"——章节清单、治理章、消费者注册表
> - PS-STD-005（本标准）管"**整个蓝图体系怎么建**"——层级结构、目录归属、ID 命名、引用链
> - 两者互补，不重复。蓝图编写者需要同时查 PS-STD-002（章节模板）+ PS-STD-005（放在哪个层级目录下）

---

## 1. 目的与范围

### 1.1 目的

确保 ZephyrAlpha 项目的每一份蓝图都具备：

- **可追溯**：从总蓝图 → 域蓝图 → 模块蓝图的完整引用链可逐级回溯
- **可定位**：AI Agent 新 session 冷启动时，能从总蓝图逐级下钻到需要的模块蓝图
- **可归属**：每份模块蓝图明确声明自己归属于哪个域集成蓝图
- **可扩展**：新增领域时，有明确的目录创建规则和 ID 命名空间

### 1.2 责任范围（本标准管什么）

本标准管理以下内容：
- 蓝图的三级金字塔模型（System / Domain / Module）——级定义、级级关系
- **每级蓝图的目录存放位置**——在 `docs/03_modules/` 目录树中的精确路径约定
- **蓝图 ID 命名体系**——不同层级的蓝图前缀约定（MOD-MASTER / MOD-DOMAIN / MOD-{LAYER}）
- **蓝图归属声明**——每份蓝图的 `frontmatter` 字段 `belongs_to`（上级蓝图引用）
- **AI Agent 蓝图定位规则**——新 session 冷启动时按什么顺序读蓝图
- **注册表联动规则**——`blueprint-registry.yaml` 和 `module-registry.yaml` 需要增加的字段

### 1.3 责任边界（本标准不管什么）

本标准**不**覆盖以下内容：
- 单个蓝图的章节结构 → 以 `blueprint-construction-template.md` 为准（蓝图模板已在本标准 §5 中作为规范性引用）
- 蓝图内的技术决策内容 → 各蓝图独立定义
- 蓝图审批流程 → 以 MOD-INF-006 任务系统蓝图和 gate-engine 门禁规则为准
- 模块生命周期（planned → in_design → in_dev → testing → active → suspended → deprecated → archived） → 以 GOV-MOD-003（module-lifecycle-policy.md）为准
- frontmatter 字段定义 → 以 PS-STD-001（metadata-registry.md）为准

---

## 2. SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 蓝图三级金字塔结构定义（System/Domain/Module）| **本标准 §3** | —（本次新建） |
| 蓝图目录存放位置约定 | **本标准 §4** | `03_modules/index.md`（目录说明）——仅作为补充参考，不替代本标准的层级规则 |
| 蓝图 ID 命名命名体系 | **本标准 §5** | — |
| 蓝图归属字段 `belongs_to` 合法值 | **本标准 §6** | — |
| AI Agent 蓝图定位顺序 | **本标准 §7** | AGENTS.md（项目入口）——仅作为补充参考 |
| 蓝图注册表字段扩展 `blueprint_level` | **本标准 §8** | — |

**任何与本文档冲突的定义，以本文档为准。**

---

## 3. 构建的第

### 3.1 三级金字塔模型

```
                                    ┌──────────────────────────────┐
                                    │  Level 0: SYSTEM-MASTER       │
                                    │  全系统总蓝图                    │
                                    │  定义 L00-L13 全部层间数据契约    │
                                    │  ID: MOD-MASTER-001            │
                                    └────────────┬─────────────────┘
                                                 │ 引用
                         ┌───────────────────────┼───────────────────────┐
                         │                       │                       │
              ┌──────────▼──────────┐ ┌──────────▼──────────┐ ┌──────────▼──────────┐
              │ Level 1: L01 Master │ │ Level 1: L02-L03    │ │ Level 1: L11-L13     │
              │ 基础设施层集成蓝        │ │ 因子+信号域集成蓝图 │ │ ML+实验域集成蓝图      │
              │ MOD-MASTER-001      │ │ MOD-DOMAIN-SIG-001  │ │ MOD-DOMAIN-ML-001    │
              └──────────┬──────────┘ └──────────┬──────────┘ └──────────┬──────────┘
                         │                       │                       │
              ┌──────────┼──────────┐     ┌──────┼──────┐       ┌──────┼──────┐
              │          │          │     │      │      │       │      │      │
         ┌────▼───┐ ┌───▼───┐ ┌───▼────┐ ...┐ ...┐ │  ┌──▼──┐ ┌──▼──┐ ┌──▼──┐
         │MOD-INF │ │MOD-INF│ │MOD-INF  │        │  │ MOD- │ │ MOD-│ │ MOD-│
         │  -006  │ │ -005  │ │  -010  │ │ .... │ │  │ L11  │ │ L13 │ │ L12 │
         │任务系统 │ │脚本系统│ │自进化   │ │      │ │  │ ML平台│ │实验 │ │可观测│
         └───────┘ └──────┘ └───────┘┘ └─────┘┘ └──┘ └─────┘ └─────┘ └─────┘
         Module 级 Module 级 Module 级 Module 级 Module 级 Module 级 Module 级
```

### 3.2 三级定义

#### Level 0：全系统总蓝图（System Master Blueprint）

| 属性 | 值 |
|------|-----|
| **蓝图层** | SYSTEM |
| **ID 前缀** | `MOD-MASTER` |
| **职责** | 定义 **14 层架构之间的跨层数据契约**（CTR-001~006 等 L00-L07 层间的标准化数据结构）和 **13 个基础设施系统之间的集成契约**（CT-* 合同）|
| **包含内容** | 跨层数据契约（CTR）、透视拓扑图、分层架构全局约束 |
| **引用关系** | 总蓝图引用所有域蓝图，但不重复定义域内细节 |
| **关键约束** | 总蓝图可以定义"层间传什么"，不定义"单个模块内部怎么干" |
| **对标** | TOGAF Architecture Vision + K8s Cluster Architecture + OpenAPI Root Spec |
| **加载策略** | AI 新 session **MUST** 首先定位总蓝图，按需下钻到域蓝图 |

**当前已完成**：`MOD-MASTER-001`（L01 基础设施层 12 系统集成总蓝图，[blueprint.md](03_modules/_master-blueprint/blueprint.md)）

**未来需要新建**：`SYS-MASTER-001`（真正的全系统 14 层总蓝图——承载 AGENTS.md 中定义的 6 个 CTR-001~006 跨层契约的全系统叙事）

#### Level 1：功能域集成蓝图（Domain Integration Blueprint）

| 属性 | 值 |
|------|-----|
| 蓝图层 | DOMAIN |
| ID 前缀 | `MOD-DOMAIN-{DOMAIN_CODE}` |
| 职责 | 定义**一个功能域内的多个系统/层之间的集成关系**，是该域内模块蓝图的上级 |
| 包含内容 | 域内系统间的 CT-* 合同、域特有的拓扑图、域级 SLA/SLO |
| 引用关系 | 域蓝图 MUST 声明 `belongs_to: SYS-MASTER-001`（或 MOD-MASTER-001 非系统级覆盖）|
| 关键约束 | 域蓝图只定义域内集成，不重复模块蓝图的内部架构 |
| 对标 | TOGAF Domain Architecture + K8s Node-level Architecture |

**当前已有（针对 L01 的域蓝图变体）**：`MOD-MASTER-001`（实质上承担了 L01 Domain 的职责）

**未来需要新建的域蓝图**：
- `MOD-DOMAIN-SIG-001`：L02 因子 + L03 信号 域集成蓝图
- `MOD-DOMAIN-RISK-001`：L04 风控 + L05 组合 + L06 执行 + L07 归因 域集成蓝图
- `MOD-DOMAIN-ML-001`：L11 ML + L13 实验 域集成蓝图
- `MOD-DOMAIN-GOV-001`：L00 数据 + L10 合规 + L12 可观测性 + L01 基础设施 域集成蓝图（横向治理层）

> ⚠️ **重要说明**：`MOD-MASTER-001` 当前同时承担了"12 个 L01 系统集成总蓝图"的角色。
> 这在 1 阶段是可接受的——因为目前所有蓝图都在 L01 基础设施层。
> 当 L02-L13 模块开始创建蓝图时，需要做**重命名/升级**：`MOD-MASTER-001` → `MOD-DOMAIN-L01-001`，并新建真正的 `SYS-MASTER-001`。
> 这个升级动作的触发条件见 §3.3。

#### Level 2：单模块蓝图（Module Blueprint）

| 属性 | 值 |
|------|-----|
| 蓝图层 | MODULE |
| ID 前缀 | `MOD-{LAYER}-{NNN}` 或 `MOD-{DOMAIN}-{NNN}` |
| 职责 | 定义**单个系统/模块**的完整设计——边界、状态机、Schema、API、存储、门禁 |
| 包含内容 | (§1-§11 架构设计) + (§12 施工指引) + 消费者注册表 + 依赖声明 |
| 引用关系 | 模块蓝图 MUST 声明 `belongs_to: {上级域蓝图或总蓝图 ID}` |
| 关键约束 | 模块蓝图引用集成合同（CT-*），但集成合同的定义在上级蓝图（域蓝图或总蓝图）|
| 对标 | TOGAF Capability Architecture + K8s Component-level Architecture |
| 加载策略 | AI 仅在需要该模块时阅读完整蓝图 |

**当前已有**：19 份模块蓝图（INF-001~017 + KB-001 + MASTER-001）

### 3.3 三级蓝图的存在条件与创建规则（Creation Triggers + Pre-Creation Gates）

> 不是任何时候都需要立即创建所有三级蓝图。以下条件触发对应级别的蓝图创建。
> **v1.1.0 新增**：Level 2 创建前必须执行功能域重叠检查（GOV-MOD-001 §7 #5）——禁止为已被覆盖的功能域创建平行蓝图。

| 蓝图层级 | 创建条件 | 前置闸门（MUST） | 示例场景 | 1 当前 |
|:----|---------|---------|---------|:---:|
| **Level 0** | 系统 ≥ 3 个功能域且出现跨域数据契约需求 | —（Level 0 有且仅有一份，无重叠风险）| L02 因子开始产出 → L04 风控消费，需要 CTR 合同 | ⚠️ 仅有 MOD-MASTER-001（L01 域级），缺真正的全系统总蓝图 |
| **Level 1** | 某一域内模块 ≥ 5 且出现 ≥ 3 组跨模块交互 | 域蓝图声明的 `responsibility_domain` 必须不与任何已有域蓝图重叠 | L02/L03 域内模块超过 5 个后，因子和信号的集成需要独立域蓝图 | ⚠️ 仅有 L01 域级（MOD-MASTER-001），缺 L02-L03、L04-L07、L11-L13 域蓝图 |
| **Level 2** | 每创建一个新的功能模块 | **GOV-MOD-001 §7 #5 功能域重叠检查通过**——新模块责任不被任何已有蓝图覆盖 | 当前已满足——各模块蓝图均已创建 | ✅ 已完成 |

> **1 约束**：当前阶段，只创建 Level 0 `MOD-MASTER-001` + 已有的 19 个 Level 2 模块蓝图。
> `SYS-MASTER-001`（真正的全系统总蓝图）留待 beta 创建——触发条件为任一 L02+ 模块蓝图开始创建时。

---

## 4. 目录结构约定

### 4.1 整体目录树

```
docs/03_modules/
├── index.md                                    ← 本目录说明（已有）
├── module-registry.yaml                        ← 模块生命周期登记表（已有）
├── blueprint-registry.yaml                     ← 蓝图深度评估登记表（已有）
│
├── _system-master/                             ← Level 0: 全系统总蓝图目录
│   └── system-master-blueprint.md             ← SYS-MASTER-001（待创建，beta）
│
├── _master-blueprint/                          ← Level 1(Domain): L01 基础设施层集成蓝图
│   └── blueprint.md                            ← MOD-MASTER-001（已有）
│      （beta 升级：→ _domain-l01/ → MOD-DOMAIN-L01-001）
│
├── _cross_layer/                                ← Level 2: cross_layer 模块蓝图（跨越多个业务层的基础设施模块）
│   ├── index.md                                 ← cross_layer 索引
│   ├── gate-engine/blueprint.md                 ← MOD-INF-007 Gate Engine
│   ├── context-engine/blueprint.md              ← MOD-INF-008 Context Engine
│   ├── pipeline/blueprint.md                    ← MOD-INF-009 Pipeline
│   ├── feedback-loop/blueprint.md               ← MOD-INF-010 Feedback Loop
│   ├── database/blueprint.md                    ← MOD-INF-012 Database（layer: cross_layer in frontmatter）
│   ├── mcp-servers/blueprint.md                 ← MOD-INF-013 MCP Servers
│   ├── llm-security/blueprint.md                ← MOD-INF-014 LLM Security Gateway
│   └── shared-core/blueprint.md                 ← MOD-INF-016 Shared + Core Infrastructure
│
├── _domain-l02-l03/                            ← Level 1: L02+L03 信号域集成蓝图（待创建）
│   └── domain-integration-blueprint.md        ← MOD-DOMAIN-SIG-001
│
├── _domain-l04-l07/                            ← Level 1: L04-L07 执行域集成蓝图（待创建）
│   └── domain-integration-blueprint.md        ← MOD-DOMAIN-RISK-001
│
├── _domain-l11-l13/                            ← Level 1: L11+L13 ML域集成蓝图（待创建）
│   └── domain-integration-blueprint.md        ← MOD-DOMAIN-ML-001
│
├── l00_data_source/                            ← Level 2: L00 数据源层的模块蓝图
│   └── <module>/blueprint.md                  ← MOD-DS-NNN
│
├── l01_infrastructure/                         ← Level 2: L01 基础设施层的模块蓝图
│   ├── index.md                                ← 层级索引（已有）
│   ├── <module-name>/                         ← 每个模块一个子目录（全小写 kebab-case）
│   │   ├── index.md
│   │   ├── blueprint.md                        ← MOD-INF-NNN（已有 1 份）
│   │   │   §1-§11 架构设计 + §12 施工指引     ← L2 设计模板
│   │   └── delivery/                           ← 交付记录
│   └── ...
│
├── l02_alpha_factor/                           ← Level 2: L02 因子层蓝图（待创建）
├── l03_signal_generation/                      ← Level 2: L03 信号层蓝图（待创建）
├── l04_risk_management/                        ← Level 2: L04 风控层蓝图（待创建）
├── l05_portfolio_construction/                 ← Level 2: L05 组合层蓝图（待创建）
├── l06_trade_execution/                        ← Level 2: L06 执行层蓝图（待创建）
├── l07_post_trade_analytics/                   ← Level 2: L07 归因层蓝图（待创建）
├── l08_human_ai_interface/                     ← Level 2: L08 人机层蓝图（已有骨架）
├── l09_research_innovation/                    ← Level 2: L09 研创层蓝图（待创建）
├── l10_compliance/                             ← Level 2: L10 合规层蓝图（待创建）
├── l11_ml_platform/                            ← Level 2: L11 ML平台层蓝图（待创建）
├── l12_system_telemetry/                       ← Level 2: L12 可观测层蓝图（待创建）
├── l13_experimentation/                        ← Level 2: L13 实验层蓝图（待创建）
│
└── 99_catalogs/                               ← 组件目录（如 M1-M11 模块清单等）
    └── ...
```

### 4.2 目录命名规则（MUST）

| 目录类型 | 命名约定 | 示例 |
|------|---------|------|
| Level 0 总蓝图 | `_system-master/`（下划线前缀，表顶层）| `_system-master/` |
| Level 1 域蓝图 | `_domain-{layer-range}/`（下划线前缀 + domain + 层级范围，表跨层）| `_domain-l02-l03/` |
| Level 2 模块蓝图 | `l{NN}_{name}/`（层级编号 + 下划线 + 全小写 kebab-case 名称）| `l01_infrastructure/` |
| 模块子目录 | `{module-name}/`（全小写 kebab-case，与 module_id 中 name 字段一致）| `task-system/` |
| 交付记录子目录 | `delivery/` | `delivery/` |

**规则**：
- Level 0 和 Level 1 的蓝图目录**以 `_` 下划线前缀**，与 Level 2 模块目录区分——方便 AI Agent 和人类快速定位金字塔高层
- Level 2 的模块目录**以层级编号 `l{NN}` 开头**，对齐 `module-registry.yaml` 的 `layer` 字段
- **所有目录名全小写、kebab-case**——禁止大写、中文、空格

### 4.3 蓝图文件名约定（MUST）

| 蓝图类型 | 文件名 | 示例 |
|------|------|------|
| Level 0 总蓝图 | `system-master-blueprint.md` | `MOD-MASTER-001` |
| Level 1 域蓝图 | `domain-integration-blueprint.md` | `MOD-DOMAIN-SIG-001` |
| Level 2 模块蓝图 | `blueprint.md`（简洁——目录名已承载模块信息）| `MOD-INF-006/blueprint.md` |

**规则**：
- Level 2 模块蓝图：文件名**统一是 `blueprint.md`**——模块名在目录名中，文件承载蓝图内容
- Level 0/1 蓝图：文件名**描述性命名**——因为这些目录下只有这一份独立蓝图文件，命名要一目了然

---

## 5. 蓝图 ID 命名体系

### 5.1 ID 前缀约定

| 蓝图层级 | ID 前缀 | 格式 | 示例 |
|:-----|------|------|------|
| Level 0 总蓝图 | `SYS-MASTER` | `SYS-MASTER-NNN` | `SYS-MASTER-001`（全系统 14 层总蓝图）|
| Level 1 域蓝图 | `MOD-DOMAIN` | `MOD-DOMAIN-{CODE}-NNN` | `MOD-DOMAIN-L01-001`（基础设施域集成蓝图）|
| Level 2 模块蓝图 | `MOD-{LAYER/DOMAIN}` | `MOD-{LAYER}-NNN` 或 `MOD-{DOMAIN}-NNN` | `MOD-INF-006`（任务系统模块蓝图）|
| Level 2 基础设施模块 | `MOD-INF` | `MOD-INF-NNN` | `MOD-INF-005`（脚本系统）|
| Level 2 知识库模块 | `MOD-KB` | `MOD-KB-NNN` | `MOD-KB-001`（知识库）|
| Level 2 数据源模块 | `MOD-DS` | `MOD-DS-NNN` | `MOD-DS-001`（数据源接入）|
| Level 2 因子模块 | `MOD-AF` | `MOD-AF-NNN` | `MOD-AF-001`（Alpha 因子计算）|
| Level 2 信号模块 | `MOD-SIG` | `MOD-SIG-NNN` | `MOD-SIG-001`（信号生成）|
| Level 2 风控模块 | `MOD-RISK` | `MOD-RISK-NNN` | `MOD-RISK-001`（风控引擎）|
| Level 2 组合模块 | `MOD-PC` | `MOD-PC-NNN` | `MOD-PC-001`（组合优化器）|
| Level 2 执行模块 | `MOD-EXE` | `MOD-EXE-NNN` | `MOD-EXE-001`（订单管理系统）|
| Level 2 归因模块 | `MOD-PTA` | `MOD-PTA-NNN` | `MOD-PTA-001`（绩效归因）|
| Level 2 人机模块 | `MOD-UI` | `MOD-UI-NNN` | `MOD-UI-001`（Dashboard）|
| Level 2 研创模块 | `MOD-RES` | `MOD-RES-NNN` | `MOD-RES-001`（回测引擎）|
| Level 2 合规模块 | `MOD-CMP` | `MOD-CMP-NNN` | `MOD-CMP-001`（合规引擎）|
| Level 2 ML 模块 | `MOD-ML` | `MOD-ML-NNN` | `MOD-ML-001`（ML Pipeline）|
| Level 2 实验模块 | `MOD-EXP` | `MOD-EXP-NNN` | `MOD-EXP-001`（A/B 实验平台）|

### 5.2 既存蓝图 ID 兼容性

现有 19 份蓝图（创建于 PS-STD-005 发布之前）的 module_id **保持不动**——这是一个相容性规则：

| 既存 ID | 蓝图层级（新分类）| 兼容性说明 |
|------|:---:|------|
| `MOD-MASTER-001` | Level 1（当前）→ Level 0（beta 升级后）| 当前它承担 L01 域集成蓝图职责。beta 后升级为全系统总蓝图或降级为 DOMAIN-L01。兼容期内 ID 不动 |
| `MOD-INF-001~017` | Level 2 MODULE | ✅ 不涉及不兼容 |
| `MOD-KB-001` | Level 2 MODULE | ✅ 不涉及不兼容 |
| `MOD-INF-003`（deprecated）| Level 2 MODULE | ✅ 已废弃，兼容性不适用 |
| `MOD-INF-004`（deprecated）| Level 2 MODULE | ✅ 已废弃，兼容性不适用 |

> **既存蓝图不强制改名**——新标准只要求新增蓝图遵循 ID 体系。
> 既存蓝图在第一份该层的 experimental 升级**蓝图时，自然迁移**。

---

## 6. 蓝图归属与引用链

### 6.1 `belongs_to` 字段（MUST）

每份 Level 2 模块蓝图 MUST 在 frontmatter 中声明 `belongs_to` 字段，指向其上级蓝图：

```yaml
# 模块蓝图 frontmatter（示例）
module_id: "MOD-INF-006"
belongs_to: "MOD-MASTER-001"     #  ← 关联域蓝图 ID（必填）
```

| 如果... | `belongs_to` 值 | 何时 |
|------|------|------|
| 在 1 期创建的模块蓝图 | `MOD-MASTER-001` | 因为当前只有这个域蓝图 |
| 在 beta+ 创建的 L02 因子蓝图 | `MOD-DOMAIN-SIG-001` | 信号域集成蓝图（待创建）|
| 在 beta+ 创建的 L06 执行蓝图 | `MOD-DOMAIN-RISK-001` | 执行域集成蓝图（待创建）|
| 跨层基础设施模块（如 Telemetry）| `SYS-MASTER-001` | 全系统总蓝图|

### 6.2 域蓝图的 `belongs_to`（MUST）

Level 1 域蓝图 MUST 声明 `belongs_to` 指向 Level 0 总蓝图：

```yaml
# 域蓝图 frontmatter（示例——beta 创建时）
module_id: "MOD-DOMAIN-SIG-001"
belongs_to: "SYS-MASTER-001"     #  ← 全系统总蓝图
```

### 6.3 `references` 字段（SHOULD）

Level 2 模块蓝图**可以**在 frontmatter 中声明 `references` 字段——列出其**直接依赖的其他模块蓝图**（同级 Level 2）：

```yaml
# 任务系统蓝图引用脚本系统蓝图
references:
  - {id: "MOD-INF-005", at: "§3~§5", why: "Finding Schema 和脚本 system exit code 约定"}
  - {id: "MOD-INF-007", at: "§1", why: "G0-G7 门禁判决逻辑"}
```

**根因**：当前模块蓝图的依赖关系平铺在 `depends_on` 或 body 文本中，无法机器读取。
`references` 字段提供字段级引用追踪——改了某一蓝图时，能机器扫描"哪些其他蓝图引用了我"。

### 6.4 引用链可追踪性

```
SYS-MASTER-001（Level 0）
  │
  ├── MOD-DOMAIN-L01-001（Level 1，L01 基础设施域）
  │     │ belongs_to: SYS-MASTER-001
  │     │
  │     └── MOD-INF-006（Level 2，任务系统）
  │            belongs_to: MOD-DOMAIN-L01-001
  │            references: [MOD-INF-005, MOD-INF-007]
  │
  ├── MOD-DOMAIN-SIG-001（Level 1，L02+L03 信号域——待创建）
  │
  └── MOD-DOMAIN-RISK-001（Level 1，L04-L07 执行域——待创建）
```

---

## 7. AI Agent 蓝图定位规则

> 对标 Codified Context (arXiv 2602.20478)：三层记忆模型——热记忆宪法 → 领域触发 Agent → 冷记忆按需文档。
> 本标准的三级蓝图体系等效实现此模型。

### 7.1 新 Session 冷启动定位路径

```
Step 1: AI 读 AGENTS.md（项目入口）
  ↓
Step 2: AGENTS.md → 跳转 PS-STD-005（本标准，蓝图体系总设计）
  ↓
Step 3: PS-STD-005 → 定位 Level 0 总蓝图路径
  ↓
Step 4: Level 0 总蓝图 → 分派到 Level 1 域蓝图
  ↓
Step 5: Level 1 域蓝图 → 定位到 Level 2 模块蓝图
  ↓
Step 6: Level 2 模块蓝图 → 实现任务开发
```

### 7.2 Token 加载策略（SHOULD）

对标 Codified Context 的三层内存消耗模型（热记忆/领域触发/冷记忆），本体系推荐以下加载策略：

| 蓝图层级 | 加载策略 | 包含内容 | Token 预算 | 怎么加载 |
|:---|:------|------|:---:|------|
| **热内存** | 自动加载 (每次会话) | PS-STD-005 §3 + §4 + §7 + Level 0 总蓝图 §1（系统清单+拓扑图）| ~800 | AGENTS.md 自动注入 |
| **领域触发** | 领域触发 (按任务) | 对应 Level 1 域集成蓝图 + 该域内 ≥ 3 个 Module 蓝图 §1 | ~2000 | Gate Engine 或 Pipeline Router 自动加载 |
| **冷内存** | 按需检索 (Index→full) | Level 2 模块蓝图全文 §1-§12 | ~8000/模块 | MCP 检索 + CE build→compress→inject |

**三层内存对应关系**：

| Codified Context | ZephyrAlpha PS-STD-005 |
|------|------|
| Tier 1 Constitution（热记忆 660 行） | = Level 0 总蓝图 §0 + Level 1 域蓝图 §1 |
| Tier 2 Domain Experts（19 Agent 按触发）| = Level 1 域蓝图 + 本域内的 Level 2 模块蓝图 |
| Tier 3 Knowledge Base（34 按需检索）| = Level 2 模块蓝图 §1-§12 全文 + 02_enterprise_architecture/ 架构视图 |

**冷启动检查清单**：新 AI session 打开项目后，**MUST** 先读 §2 SSoT 声明的真源（§3 蓝图金字塔 + §4 目录结构），再按 §7.1 逐级下钻。
**禁止**：跳过 Level 0/1 直接读 Level 2——没有跨系统上下文。

---

## 8. 注册表联动规则

### 8.1 `blueprint-registry.yaml` 扩展（MUST）

在每条 blueprints[] 记录中**新增** `blueprint_level` 字段：

```yaml
blueprints:
  - module_id: "MOD-MASTER-001"
    name: "master-blueprint"
    blueprint_level: "domain"     # ← 新增：SYSTEM / DOMAIN / MODULE
```

| `blueprint_level` | 含义 | 对应 ID 前缀 |
|:--|------|------|
| `system` | Level 0 全系统总蓝图 | `SYS-MASTER` 或 `MOD-MASTER`（1 变体）|
| `domain` | Level 1 功能域集成蓝图 | `MOD-DOMAIN` 或 `MOD-MASTER`（1 变体）|
| `module` | Level 2 单模块蓝图 | `MOD-{LAYER/DOMAIN}` |

### 8.2 `module-registry.yaml` 扩展（SHOULD）

在每条 modules[] 记录的 `blueprint:` 下**新增** `parent_blueprint` 字段：

```yaml
modules:
  - module_id: "MOD-INF-006"
    blueprint:
      status: approved
      file: "blueprint.md"
      parent_blueprint: "MOD-MASTER-001"   # ← 新增
```

---

## 9. 既存蓝图的归属映射

> 本章是过渡性声明——1 既存的 19 份蓝图的归属（按 §6.1 规则声明 `belongs_to`）。

| module_id | title | `belongs_to` | blueprint_level |
|------|------|------|:---:|
| MOD-MASTER-001 | 集成闭环总蓝图 | —（域蓝图层）| domain |
| MOD-INF-001 | 容量保障体系 | MOD-MASTER-001 | module |
| MOD-INF-002 | 运行时集成 | MOD-MASTER-001 | module |
| MOD-INF-003 | 任务卡+KMS（deprecated）| MOD-MASTER-001 | module |
| MOD-INF-004 | Vibe Coding双管线（deprecated）| MOD-MASTER-001 | module |
| MOD-INF-005 | 脚本系统 | MOD-MASTER-001 | module |
| MOD-INF-006 | 任务系统 | MOD-MASTER-001 | module |
| MOD-KB-001 | 知识库 | MOD-MASTER-001 | module |
| MOD-INF-007 | Gate Engine | MOD-MASTER-001 | module |
| MOD-INF-008 | Context Engine | MOD-MASTER-001 | module |
| MOD-INF-009 | Pipeline | MOD-MASTER-001 | module |
| MOD-INF-010 | Feedback Loop | MOD-MASTER-001 | module |
| MOD-INF-011 | Vector Memory | MOD-MASTER-001 | module |
| MOD-INF-012 | Database | MOD-MASTER-001 | module |
| MOD-INF-013 | MCP Servers | MOD-MASTER-001 | module |
| MOD-INF-014 | LLM Security | MOD-MASTER-001 | module |
| MOD-INF-015 | System Telemetry | MOD-MASTER-001 | module |
| MOD-INF-016 | Shared+Core | MOD-MASTER-001 | module |
| MOD-INF-017 | Code Dedup Engine | MOD-MASTER-001 | module |

> **说明**：1 阶段，所有 Level 2 模块蓝图的上级都是 `MOD-MASTER-001`（即 L01 基础设施域集成蓝图）。
> beta+ 时，L02+ 的模块蓝图将归属到新建的对应 Level 1 域蓝图。

---

## 10. 禁止行为

| 禁止行为 | 原因 | 替代方案 |
|------|------|------|
| 创建蓝图时不声明 `belongs_to` 字段 | AI 无法判断蓝图在金字塔中的位置 | 按 §6.1 声明 `belongs_to` |
| 将 Level 2 模块蓝图混放在 Level 0/1 的 `_` 前缀目录下 | ID 命名空间混乱，层次关系不可恢复 | Level 2 放入 `l{NN}_{name}/{module}/` |
| Level 2 模块蓝图文件名用 `{module}-blueprint.md` | 目录名已经承载模块名，重复 | 统一用 `blueprint.md` |
| 在 Level 2 模块蓝图中定义跨系统的 CT-* 合同 | 合同应该在上级（域蓝图/总蓝图）——跨系统合同如果写在具体蓝图里，改一个模块会漏更新合同影响所有系统 | CT-* 合同的定义放 Level 1 域蓝图或 Level 0 总蓝图。Level 2 只引用 CT-* 编号 |
| AI 新 session 跳过 Level 0 直接读 Level 2 | 缺跨系统上下文——"这个模块的上游是谁"不知道 | 按 §7.1 逐级下钻 |
| 在既存蓝图 frontmatter 中加入 `belongs_to` 时，改 module_id 或 status | 仅新增 frontmatter 字段即可 | 不改其他 frontmatter 字段 |
| 为已被覆盖的功能域创建平行蓝图——需要新范围时应升级原蓝图（版本号 + changelog），而非创建同级新蓝图 | MOD-INF-003/004→006 的反模式：创建"任务卡KMS"和"双管线"两个子域蓝图，后发现它们都属于"任务系统"更大的功能域，又创建 006 来合并——根源是跳过功能域重叠检查（GOV-MOD-001 §7 #5） | 升级优先级：① 升级原蓝图（version bump + changelog 在既存蓝图中新增节）→ ② 拆分原蓝图为父蓝图 + 子蓝图（须声明 `responsibility_domain` + `covers[]`）→ ❌ 禁止创建平行蓝图后"合并" |

---

## 11. 与已有标准的关系（PS-STD 系列）

| PS-STD | 职责 | 与本标准的关系 |
|------|------|------|
| PS-STD-000 宪法 | 规则怎么分类 | 本标准是登记表层标准——后果可逆（重组目录归属是可逆操作）|
| PS-STD-001 字段 | frontmatter 字段定义 | `belongs_to` 字段的定义以本标准为准，**不与其他字段冲突** |
| PS-STD-002 模板 | 单个标准怎么写 | 本标准（格式定义型子类型）遵循 PS-STD-002 的 Common Core（6 章）+ 该子类型的条件章节。§12/§13/§14 不适用（本标准不定义字段、不定义行为约束。行为约束在本 §5 禁止行为中表达）|
| PS-STD-003 行为边界 | ABS/COND/REC | 本标准的禁止行为在本 §5。因果关系可逆——违反即重组目录归属，不需要纳入宪法 |

---

## 12. 标准间引用规范

### 规范性引用（MUST）

| 文档 | 引用内容 | 冲突时以谁为准 |
|------|------|------|
| `01_policies_and_standards/templates/blueprint-construction-template.md` | 蓝图模板——单份蓝图的章节结构 | 蓝图模板 |
| `PS-STD-000` (meta-standard-constitution.md) | 元标准宪法——规则分类（标准 vs 宪法）| PS-STD-000 |
| `PS-STD-001` (metadata-registry.md) | frontmatter 字段定义 | PS-STD-001 |
| `PS-STD-002` (document-structure-standard.md) | L1 标准模板——格式定义型子类型适用的章节集 | PS-STD-002 |
| `03_modules/module-registry.yaml` | 模块生命周期登记 | module-registry.yaml |
| `03_modules/blueprint-registry.yaml` | 蓝图深度评估 | 本标准 + blueprint-registry.yaml（§8.1 扩展字段以本标准为准）|

### 资料性引用（仅供参考）

| 文档 | 引用内容 |
|------|------|
| Codified Context (arXiv 2602.20478) | 三层记忆模型（设计参考）|
| Microsoft Edge AI Blueprint Architecture | master-blueprint → domain-blueprint → component 层级（设计参考）|
| HP Inc AI-Blueprints specification.md | specification.md vs blueprint.md 双层分离（设计参考）|
| TOGAF Architecture Repository | COBIT 对齐——架构仓库分级存放 |

---

## 13. 异常豁免机制

本标准的异常豁免机制适用于**临时性违反**——如 1 过渡期内暂时无法升级既存蓝图 frontmatter 的情况。

| 豁免级别 | 定义 | 触发条件 | 审批 |
|------|------|------|------|
| 瞬态豁免 | 1 既有蓝图**不强制**立即声明 `belongs_to` | 现有蓝图 > 20 份且 Owner 判断立即声明成本过高 | 本声明即可——Owner 已知 |
| 建设豁免 | 目录迁移中**允许暂时**存在双目录（旧目录 + 新目录）| 目录迁移过程中必须不能一次切换 | Owner 口头批准 |

**瞬态豁免的失效条件**：本标准发布后，experimental 结束时（任务系统 v0.3.0 升级完成 + GateEngine G7 完整度门禁激活），所有既存蓝图 MUST 已声明 `belongs_to`。届时瞬态豁免自动失它。

---

## 14. AI 可消费性声明

| 维度 | 状态 | 说明 |
|------|:--:|------|
| 语义无歧义 | ✅ | MUST/SHOULD/MAY 精确使用，所有约定有对照表 |
| 上下文自足 | ✅ | 不需要读外部文档即可执行目录创建和ID生成 |
| 示例充分 | ✅ | 每项规则 COVR 目录创建和 ID 生成 |
| Token 估算 | ~3000 tokens | 最小必读：§3 + §4 + §5（ID 命名）+ §7（定位）+ §9（归属映射）——约 1200 tokens |
| AI 工具兼容性 | ✅ | 全文 Markdown + YAML 对照表——AI 可直接消费，无需额外推理 |

---

## 15. 完整性自检清单

> ⚠️ **免责声明**：本标准由 AI Agent 生成。以下自检清单为 SHOULD（可选）——不具备独立验证力（对比 PS-STD-002 §18）。

- [x] §1  目的与范围：目的、责任范围（管什么）、责任边界（不管什么）
- [x] §2  SSoT 声明：真源/非真源表格 + "以本标准为准"
- [x] §3  主体内容：三级金字塔完整定义（Level 0/1/2 属性+职责+条件）
- [x] §4  目录结构约定：整体目录树 + 命名规则表
- [x] §5  蓝图 ID 命名体系：ID 前缀表 + 两层 ID 前缀完整覆盖 14 层
- [x] §6  蓝图归属与引用链：`belongs_to` 字段定义 + `references` + 引用链图
- [x] §7  AI Agent 蓝图定位规则：冷启动路径 + Token 预算 + Codified Context 对照
- [x] §8  注册板联动：`blueprint-registry.yaml` + `module-registry.yaml` 新增字段
- [x] §9  既存蓝图归属映射：19 份既存蓝图 → `belongs_to` 映射
- [x] §5  禁止行为：6 条 MUST NOT
- [x] §6  AI 可消费性声明：可理解性+Token预算
- [x] §9  标准间引用：normative/informative 分离
- [x] §7  既存蓝图相容性（ID 不变）
- [x] frontmatter 完整：所有 PS-STD-001 定义的必填字段

---

## 16. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|------|
| 1.1.0 | 2026-05-06 | **SSoT 操作化——§10 新增禁止行为 #7 + §3.3 升级为创建条件+前置闸门双列表**。根源：MOD-INF-003/004→006 的"平行蓝图后合并"反模式——003 和 004 分别覆盖了 006 功能域的子范围，而现有规则只禁止结构性违规（缺 belongs_to、错目录、错命名），不禁止功能性重叠。修复：(1) §10 #7 明确禁止为已被覆盖的功能域创建平行蓝图，需要新范围时必须升级原蓝图；(2) §3.3 表新增"前置闸门"列——Level 2 创建前 MUST 通过 GOV-MOD-001 §7 #5 功能域重叠检查；(3) 定义替代方案优先级：① 升级原蓝图 → ② 拆分 + responsibility_domain → ❌ 禁止平行蓝图。对标：唯一真源原则的操作化落地。版本号 minor +1。 |
| 1.0.0 | 2026-05-04 | 初始版本。建立蓝图三级金字塔体系：(1) Level 0 ⇒ 全系统总蓝图 `_system-master/`，(2) Level 1 ⇒ 域集成蓝图 `_domain-{layers}/`，(3) Level 2 ⇒ 模块蓝图 `l{NN}_{name}/{module}/blueprint.md`。定义 `belongs_to` frontmatter 字段、14 层 ID 前缀表、既有 19 份蓝图归属清单。AI 冷启动 6 步定位路径。对标 Codified Context 三层内存模型。禁止行为 6 条。1 瞬态豁免——既存蓝图不强制立即声明 `belongs_to`，experimental 结束时触发。关联决策线：`R85`（本决策在 architecture-rationale-log.md 中的记录）|
