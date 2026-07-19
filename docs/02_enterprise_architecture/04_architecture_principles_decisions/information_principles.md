---
module_id: VIEW-04PRINC-INFORMATION
title: Architecture Principles — Information / 架构原则：信息
doc_type: architecture_view
status: Active
version: 1.0.1
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-07-19
superseded_by: null
supersedes: VIEW-02-INFORMATION-ARCH
related_rationale: []
related_open_questions: []
tags:
- information-principles
- togaf
- ia
- docs-structure
- document-lifecycle
- drawer-taxonomy
summary: 信息架构永恒原则文档。timeless 方法论——docs/ 抽屉四种性质分类（治理与标准层/架构层/模块蓝图层/知识层/过程区/历史区）、文档生命周期状态机、frontmatter 元数据标准（schema v2.0.0 + 9 类 doc_type 词表 + module_id 命名规则）、TTL 治理。派生数据（具体目录清单、成熟度状态、当前工作区入口）不在本文档，由 directory_registry.yaml + 自动化系统维护。
date: '2026-07-19'
ttl: permanent
---

# Architecture Principles — Information
# 架构原则：信息（Information Principles）

---

## §1 定位 / Position

本文档是**信息架构的永恒指导原则**。

**保留内容**：方法论、设计原则、不变约束——抽屉分类依据、文档生命周期、元数据标准。

**不保留内容**（派生/动态数据，由各自自动化系统维护）：
- docs/ 具体目录清单 → `directory_registry.yaml`（项目目录登记表 SSoT）
- 目录成熟度状态（active/partial/planned/deferred）→ 由 directory_registry 派生
- 当前工作区关键入口 → 自动从 directory_registry 派生
- 全域清单 → `generated/domains/index.md`（depgraph 派生，待生成）

**与其他原则文档关系**：
- [capability_maturity_principles.md](capability_maturity_principles.md)：能力成熟度方法论
- [data_principles.md](data_principles.md)：数据架构原则
- [security_principles.md](security_principles.md)：安全架构原则
- [integration_principles.md](integration_principles.md)：集成架构原则
- [business_principles.md](business_principles.md)：业务架构原则
- 本文：信息架构原则（抽屉分类/文档生命周期/元数据标准）

---

## §2 Drawer Classification / docs/ 抽屉分类方法论

### 2.1 四种性质分类原则（永恒框架）

docs/ 顶级目录按**四种性质**分类：

| 类别 | 性质 |
|------|------|
| **治理与标准层** | 定义合格产物标准、规则、注册表、词表（跨业务域，管所有东西） |
| **架构层（中枢）** | 企业架构设计、域架构文档、治理报告、架构原则、派生视图、TOGAF 视图 |
| **模块蓝图层** | 域模块蓝图（`_domain_*/` 平级 + `_cross_layer/` 跨层模块） |
| **知识层** | 长期知识资产、AI 驱动采集流水线、可复用认知 |
| **过程区** | 讨论中、未定稿、任务卡、session log（TTL=task_bound） |
| **历史区** | 归档、退役资产 |

### 2.2 抽屉关系图（永恒拓扑）

```
         ┌────────── 治理与标准层 ──────────┐
         │ 01_policies_and_standards       │
         │ (rules / policies / registry)   │
         └───────────┬─────────────────────┘
                     │ 规则 / 标准 / 词表约束
                     ↓
         ┌────────── 架构层（中枢）─────────┐
         │ 02_enterprise_architecture      │
         │  (域文档 / 治理报告 / TOGAF视图)│
         └───────────┬─────────────────────┘
                     │ 蓝图 / 施工指引
                     ↓
         ┌────────── 模块蓝图层 ────────────┐
         │ 03_modules                      │
         │  (_domain_* 域 + _cross_layer)  │
         └───────────┬─────────────────────┘
                     │ 沉淀 / 反馈
                     ↓
         ┌────────── 知识层 ────────────────┐
         │ 08_knowledge                    │
         └─────────────────────────────────┘
                     ↑ 过程产物               ↓ 失效归档
              _working/                  _archive/
              (task_bound)               (retired)
```

### 2.3 抽屉精简原则（永恒——避免目录爆炸）

**原则**：同一职责不在两处定义。

- 业务域文档归 `02_enterprise_architecture/02_domain_architecture_docs/`
- 业务域蓝图归 `03_modules/_domain_*/`
- 避免双真源

**精简触发条件**：当顶级目录数量超过 **10 个**时，必须评估是否有可合并项（按职责相似性合并）。

### 2.4 具体目录清单（派生数据）

> **注**：docs/ 当前具体目录清单不在本文档硬编码。真源在 `directory_registry.yaml`（项目目录登记表 SSoT），结构变更必须先改 SSoT。

---

## §3 Document Lifecycle / 文档生命周期

### 3.1 生命周期状态机（永恒）

```
┌────────────────────┐     ┌───────────────────┐     ┌──────────────────┐
│ _working/          │ ──→ │ _working/         │ ──→ │ 02_enterprise    │
│ research_notes/    │Stabilize│ decomposition/│Promote│ /03_modules       │
│ decomposition/     │     │                   │     │ etc.（canonical）│
└────────────────────┘     └───────────────────┘     └─────────┬────────┘
                                                               │
                                                               │ Superseded / 失效替代
                                                               ↓
                                                     ┌──────────────────┐
                                                     │ _archive/        │
                                                     │ (retired assets) │
                                                     └──────────────────┘
```

### 3.2 Status 状态机（永恒枚举）

文档 status 必须遵循以下状态机：

```
draft → in_discussion → review_ready → active/accepted → superseded/deprecated
```

**永恒约束**：
- 已 accepted 的文档**只能被 supersede，不可删改**（KBG-0002）
- 禁用删除线标记（用 superseded_by 字段显式标注替代关系）

### 3.3 过程区 TTL 治理（永恒）

`_working/` 下过程产物 TTL=task_bound：

- 任务完成或文档升格后，`_working/` 下过程产物应清理
- TTL-METADATA gate 在 commit 时强制校验
- 由 `ttl_vocabulary.yaml` 受控

---

## §4 Metadata Standard / 元数据标准

### 4.1 frontmatter schema（永恒约束）

所有 `docs/` 下文档必须遵守 frontmatter schema v2.0.0：

- **Single frontmatter schema** — 真源：`frontmatter_schema.json`
- **Phased required fields** — status 决定哪些字段必填
- **Controlled `doc_type` vocabulary** — 真源：`doc_type_vocabulary.yaml`（9 个合法值）
- **Unified `module_id` naming** — `<DOMAIN>-[<SUBDOMAIN>-]<TYPE>-<NNN>`
- **Append-only supersedes rule** — 已接受决策只能被 supersede，不可删改（禁用删除线）

### 4.2 TTL 治理（永恒）

`ttl` 字段受控于 `ttl_vocabulary.yaml`：

- `permanent` — 永久文档（架构原则、契约、规则）
- `task_bound` — 过程产物（任务完成即清理）
- `phase_bound` — 阶段产物（阶段结束清理）
- `review_bound` — 评审产物（评审结束清理）

**永恒约束**：commit 时 TTL-METADATA gate 强制校验 ttl 字段合法性。

### 4.3 module_id 命名规则（永恒）

格式：`<DOMAIN>-[<SUBDOMAIN>-]<TYPE>-<NNN>`

- `<DOMAIN>` — 大写域代码（如 `VIEW`、`MOD`、`SH`）
- `<SUBDOMAIN>` — 可选子域
- `<TYPE>` — 类型代码（如 `PRINC`、`ARCH`、`INF`）
- `<NNN>` — 序号

**永恒约束**：所有 `src/zephyr/**/*.py` 文件的 `[BLUEPRINT]` 头部 module_id 必须符合裁定#208三轨制。

---

## §5 Architecture Runway / 架构预留通道

> 以下预留通道为未来 P3 能力激活后的挂载点。

| ID | 能力描述 | 挂载点 | 激活触发条件 |
|---|---|---|---|
| RW-IA-01 | 多模态因子信息对象 — 将文本/图像/数字融合因子纳入知识体系，扩展抽屉定义与文档生命周期规则 | `08_knowledge/` 子目录扩展 + 文档生命周期新增多模态类型 | NLP 因子生产验证充分 + 图像/另类数据供应商接入完成 |
| RW-IA-02 | ESG 因子信息对象 — 在 `_domain_factor/` 下建立 ESG 因子专属蓝图，定义数据质量与血缘标准 | `_domain_factor/` 子目录扩展 | ESG 数据供应商接入评估完成 |
| RW-IA-03 | 知识图谱自动构建 — 在 `08_knowledge/` 建立知识图谱子层，定义实体/关系信息架构与跨抽屉引用规则扩展 | `08_knowledge/` 新增子目录 + 元数据标准扩展 | KMS 条目 > 500 条 + 知识图谱基础设施完成 |

---

## §6 视图边界 / Boundaries

### 6.1 本文档覆盖

- docs/ 抽屉四种性质分类方法论（§2）
- 抽屉关系拓扑图（§2.2）
- 抽屉精简原则（§2.3）
- 文档生命周期状态机（§3）
- frontmatter 元数据标准（§4）
- TTL 治理（§4.2）
- module_id 命名规则（§4.3）
- Architecture Runway（§5）

### 6.2 本文档不覆盖（由其他系统维护）

| 内容 | 真源 |
|------|------|
| docs/ 具体目录清单 | `directory_registry.yaml`（SSoT）|
| 目录成熟度状态（active/partial/planned/deferred）| `directory_registry.yaml` 派生 |
| 当前工作区关键入口 | 自动从 directory_registry 派生 |
| 全域清单 | `generated/domains/index.md`（depgraph 派生，待生成）|
| frontmatter schema 完整规格 | `frontmatter_schema.json` |
| doc_type 合法值清单 | `doc_type_vocabulary.yaml` |
| TTL 合法值清单 | `ttl_vocabulary.yaml` |
| 业务能力地图（哪些能力需要哪些文档）| `business_principles.md` |
| 应用模块边界（代码模块如何划分）| `application_principles.md` |
| 架构原则（R1-R4 安全红线 + 准入铁律）| `architecture_principles.md` |

### 6.3 与其他原则文档关系

- [capability_maturity_principles.md](capability_maturity_principles.md)：能力成熟度方法论
- [data_principles.md](data_principles.md)：数据架构原则
- [security_principles.md](security_principles.md)：安全架构原则
- [integration_principles.md](integration_principles.md)：集成架构原则
- [business_principles.md](business_principles.md)：业务架构原则
- 本文：信息架构原则（抽屉分类/文档生命周期/元数据标准）

---

> **文档维护原则**：本文档只包含永恒指导原则。任何随目录结构演进、frontmatter schema 升级、TTL 词表扩展的内容，均不应写入本文档——它们由各自自动化系统维护。
