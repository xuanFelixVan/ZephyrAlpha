---
module_id: PS-STD-001
title: ZephyrAlpha 元数据登记表
doc_type: standard
status: active
version: "5.9.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-02"
valid_from: "2026-04-28"
summary: "ZephyrAlpha 全项目元数据的唯一真源注册表。定义三域字段（文档 frontmatter / 任务卡 / AI 治理）、doc_type 受控词表（27 种，canonical SSoT = vocabulary YAML，本文件仅保留速查引用）、审计字段、字段改名记录、与专业机构对照表。v5.12.0：§3.2.1 子集 12→13 值（补 schema），总数 26→27 对齐 vocabulary YAML；§2.2 Active 14→18 对齐 architecture-contract.yaml。"
ttl: permanent
tags: [metadata, frontmatter, doc_type, schema, ssot, ai-governance, metadata-registry]
rule_form: declarative
scope: global
stability: stable
verifiability: automated
supersedes:
  - path: docs/01_policies_and_standards/meta/metadata-registry.md
    version: 1.0.0
    reason: "v3.0.0 合并吸收，doc_type 从13种扩展为17种，新增 AI 员工字段、分阶段必填闸门、module_id 规范"
  - path: docs/19_development_workspace/structure-and-mapping/discussion-document-standard.md
    version: 2.0.0
    reason: "v3.0.0 合并吸收，管辖范围从工作区扩展为全局"
  - path: schemas/frontmatter-schema.json
    version: R4
    reason: "v3.0.0 生效后，JSON Schema 改为本注册表的自动生成产物，不再手写"
  - path: docs/01_policies_and_standards/governance/document/document-metadata-standard.md
    version: 3.6.0
    reason: "v4.0.0 重命名为元数据注册表，扩展为全项目三域字段真源，字段改名对标 IETF AAT"
ai_autonomy: immutable_core
depends_on: []
---

# ZephyrAlpha 元数据登记表

> **module_id**: PS-STD-001 | **version**: 5.7.0 | **status**: active
>
> 本注册表是 ZephyrAlpha **元数据标准**的唯一真源（Single Source of Truth）——
> 定义字段应该有什么属性、校验规则、分类体系。
> 覆盖三个域：文档 frontmatter（域 A）、任务卡（域 B）、AI 治理（域 C）。
> **字段的具体定义（字段名/类型/必填性/枚举值）以 PS-REG-012 [frontmatter-field-registry.yaml](../_registry/catalogs/frontmatter-field-registry.yaml) 为 canonical SSoT**
> （YAML 格式、字段级粒度、机器可校验——符合 AGENTS.md §6.9 YAML 优先原则）。
> 本文件管"规则"（字段应满足什么规范），PS-REG-012 管"数据"（每个字段具体是什么）。
> 所有工具、AI 员工、pre-commit 钩子、CI 流水线：**读字段定义 → 查 PS-REG-012；读字段规范/校验逻辑 → 查本文件**。
>
> 对标标准：ISO 11179（元数据登记表）、IETF Agent Audit Trail（AAT）、OpenLineage。

---

> ## ⚠️ 待解决问题（2 个）
>
> **任何修改本文件或使用 doc_type 的人/AI 必须知晓**：
>
> | # | 问题 | 严重度 | 状态 | 影响范围 |
> |---|------|:------:|------|---------|
> | 1 | ~~**旧 doc_type 长名未迁移**~~ | ~~🔴~~ | 📋 迁移方案已定 | 迁移方案见 §3.7，施工 beta 批量执行 |
> | 2 | **`internal` classification 值待迁移**：100 个文件标 `classification: internal`，已裁定删除 `internal` 改为 `confidential`，但尚未批量执行 | 🟡 | 待迁移 | 100 个 .md 文件 + 2 个 Python 文件 + 数据库 DDL |
>
> **处理原则**：问题 1 迁移方案已定义（§3.7），施工 beta 批量执行。问题 2 在后续 session 批量执行迁移。**在问题解决之前，不得新增使用旧长名或 `internal` 的文件。**
>
> > 拆分预判条件见 §6（文件末尾）👉 `metadata-registry.md#split-conditions`

---

## 1. 目的与范围

### 1.0 最小必读路径（~1000 Token）

新 AI session 按此路径最快上手：§1（三域架构）→ §2.1（必填字段）→ §4（status词表）→ §3.1（doc_type词表）→ §14（违规检测规则）。其余章节按需查阅。

### 1.1 目的

为 ZephyrAlpha 项目（1500+ 模块 AI 自治量化交易系统）建立统一的元数据登记表，确保：

- **AI 员工**可以在无人类指导的情况下，正确理解、创建、分类、检索项目文档
- **人类 Owner**可以快速定位任何文档的归属、状态、生命周期
- **工具链**（pre-commit、CI、校验脚本）基于同一套规则自动执行，无字段漂移
- **知识传承**不依赖特定 AI 模型的记忆，而是编码在文档元数据中
- **审计合规**出事后可追溯到人/模型/决策过程，对标 EU AI Act / SR 11-7 / IETF AAT

> **理论基础**：本注册表的设计哲学——字段优先级排序、`summary` 高于 `tags`、领域触发优于全量加载——遵循 Codified Context 论文（arXiv 2602.20478）在 108KLOC 分布式系统实验中验证的"距离衰减效应"和"领域触发策略"原则。详见 PS-STD-000 §3。

### 1.2 三域架构

本注册表覆盖三个域，每个域有各自的字段集合：

| 域 | 名称 | 适用范围 | 字段数 |
|---|------|---------|--------|
| **A** | 文档 frontmatter | 所有 `.md` / `.yaml` 文件 | 40 |
| **B** | 任务卡 | `doc_type: plan` 或 `doc_type: roadmap` 的文件 | 18 |
| **C** | AI 治理 | AI 决策日志 + AI 员工档案 | 28+2 + 30+ |

**域 A 是全局的**，所有文档都要遵守。域 B 和域 C 是专用的，只在特定场景下使用。

### 1.3 范围

本标准覆盖 ZephyrAlpha 项目**所有目录**下的 `.md` 和 `.yaml` 文件。

#### 1.3.1 YAML 文件子类型

项目中的 `.yaml` 文件按**消费者不同**分为两种子类型，遵循不同的 frontmatter 契约：

| 属性 | `document_yaml` | `registry_yaml` |
|------|----------------|-----------------|
| **消费者** | 人类 + AI（阅读+理解+执行） | CI 脚本 / pre-commit（机器解析+校验） |
| **典型文件** | `session-log-schema.yaml`、`model-capability-contract.yaml` | `_registry/` 下所有 .yaml（catalogs/ / contracts/ / vocabularies/） |
| **最小必填字段** | module_id, title, doc_type, status, version, date, owner（7 项——同 .md 文件） | schema_version, doc_type, title, status（4 项） |
| **不要求的字段** | — | module_id, rule_form, scope, stability, verifiability, layer（registry_yaml 不参与规则推导链） |
| **depends_on 要求** | 必须声明——glossary #19 规定引用链 ≤ 1 层 | 必须声明——声明依赖的元标准文件（如 PS-STD-001） |

> **裁定依据**：`_registry/` 下的文件是**机器消费的数据结构**（词表清单、索引注册表、校验契约），不是人类阅读的 prose 规则文档。强行套用 document_yaml 的 14 个必填字段（Active 阶段）会导致"词表文件被迫填 rule_form: data 假装自己是规则"的形式主义。承认其 `registry_yaml` 身份后，每个子类型只要求其消费者真正需要的字段。

> **文件扩展名区分**：`.yaml` 统一走 `registry_yaml` 契约；`.md` 统一走 `document_yaml` 契约。`_registry/schemas/` 下的 `.json` 文件（如 frontmatter-schema.json）不受本标准 frontmatter 约束——JSON 文件自带 `$schema` 自描述。

#### 1.3.2 覆盖目录清单

| 目录 | 说明 |
|------|------|
| `01_policies_and_standards/` | 治理策略与标准 |
| `02_enterprise_architecture/` | 企业架构 |
| `03_modules/` | 模块生命周期文档（蓝图含施工指引+交付） |
| `08_knowledge/` | 知识库 |
| `09_audit/` | 审计 |
| `10_compliance/` | 合规 |
| `03_modules/_b_track_interfaces/` | AI 工程 |
| `19_development_workspace/` | ~~开发工作区~~ 已删除（2026-05-02，迁至外部独立目录） |
| `archive/` | 归档 |
| 其他所有目录 | 无例外 |

### 1.4 SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| doc_type 受控词表 | **doc_type-vocabulary.yaml**（canonical SSoT） | 本文件 §3（速查引用）、frontmatter-standard.md v1.0.0（已废弃） |
| 域 A 字段定义（文档 frontmatter） | **frontmatter-field-registry.yaml**（canonical SSoT） | 本文件 §2（字段规范/校验逻辑，非字段数据定义）、frontmatter-schema.json（自动生成产物） |
| 域 B 字段定义（任务卡） | **本文件 §7** | task-card-standard.md（字段定义以本注册表为准，该文件保留业务规则） |
| 域 C 字段定义（AI 治理） | **本文件 §8** | ai-autonomous-company-endgame-design.md（设计文档，字段定义以本注册表为准） |
| 受控枚举定义（category / domain / namespace / AgentRole） | **本文件 §9.1~§9.4** | — |
| 受控枚举定义（layer / source_type / priority） | **本文件 §9.5~§9.7** | triage.py VALID_LAYERS（需对齐）、kms-entry-schema.md source_type（需对齐）、schemas.py AuditSeverity（需扩展重命名） |
| module_id 命名规范 | **本文件 §5** | unified-numbering-standard.md（层编号部分仍有效，模块 ID 格式以本文件为准） |
| 状态语义 | **status-vocabulary.yaml**（canonical SSoT） | 本文件 §4（规范解释） |
| rule_form 映射 | **rule_form-vocabulary.yaml**（canonical SSoT） | 本文件 §2.6（一致性约束） |
| ttl 枚举 | **ttl-vocabulary.yaml**（canonical SSoT） | 本文件 §6（规范解释） |

**任何与本文件冲突的定义，以本文件为准。** 发现冲突时，应提决策记录（参见 MOD-KB-001 §3.9.5 三层决策记录模型）并修正冲突方。

### 1.5 消费者注册表

> **交叉索引**：消费者注册的 authoritative tracking 在 [registry-master-index.yaml](../_registry/catalogs/registry-master-index.yaml) §2（health_check_coverage）+ §3（quick_lookup）
> 和 [frontmatter-field-registry.yaml](../_registry/catalogs/frontmatter-field-registry.yaml)（字段级定义）。
> 以下为 human-readable 速查，不替代 canonical YAML。

#### 1.5.1 Tier 1：硬编码枚举值（变更必须同步）

以下文件**硬编码了本注册表的枚举值**，注册表任何枚举变更都必须同步更新：

| 文件 | 依赖内容 | 同步要求 |
|------|---------|---------|
| `scripts/governance/check_frontmatter_metadata.py` | 全部枚举（doc_type 27值、status 3值、ttl 5值、safety_level 3值、evolution_policy 3值、governance_family 4值、ai_capability_slot 4值、category 10值、domain 10值、review_status 4值）+ 分阶段必填闸门 + 路径映射规则 | **最高优先级**：枚举变更必须同 commit 更新 |
| `src/zephyr/schemas.py` | TaskStatus 10值、SafetyLevel 3值、Classification 3值、EvolutionPolicy 3值、TaskNamespace 7值、AuditSeverity 3值 | **高优先级**：域 B 枚举变更必须同 commit 更新 |
| `src/zephyr/db/sqlite_schema.py` | DDL CHECK 约束硬编码了 status 10值、namespace 7值、safety_level 3值、classification 3值、evolution_policy 3值 | **高优先级**：DDL 变更需要数据库迁移脚本 |
| `src/zephyr/mcp/knowledge_base_server.py` | `_VALID_CATEGORIES` 10值 | **中优先级**：category 枚举变更必须同步 |
| `src/zephyr/mcp/tool_contracts.yaml` | category enum 10值、task_id 格式引用 §7.2 | **中优先级**：category 枚举变更必须同步 |
| `src/zephyr/kb/kb_repo.py` | KeStatus 10值 + 状态转换表 | **高优先级**：域 C 知识条目状态变更必须同步 |
| `schemas/frontmatter-schema.json` | 全部字段的 JSON Schema 定义（本注册表的自动生成产物） | **自动**：本注册表变更后重新生成 |

#### 1.5.2 Tier 2：引用本注册表作为权威依据

以下文件**引用本注册表作为权威依据**，但不硬编码枚举值：

| 文件 | 引用方式 |
|------|---------|
| `.pre-commit-config.yaml` | GATE-15 配置段注释声明"权威依据：metadata-registry.md" |
| `scripts/governance/validate_ssot.py` | 使用注册表定义的字段名做校验 |
| `scripts/governance/validate_blueprint_provenance.py` | 校验 doc_type 和 provenance 字段 |
| `scripts/governance/validate_truth_source_cascade.py` | 使用 doc_type 等字段做真源级联校验 |
| `scripts/governance/check_naming_convention.py` | 使用 doc_type 命名规则 |
| `scripts/governance/drafts_zone_archiver.py` | 使用 doc_type 和 status 字段 |
| `src/zephyr/hooks/ssot_guard.py` | 检查治理文件与注册表的一致性 |

#### 1.5.3 Tier 3：字段定义对齐（以本注册表为准）

以下文件**定义了与注册表对齐的字段**，字段定义以本注册表为准：

| 文件 | 对齐内容 |
|------|---------|
| `docs/01_policies_and_standards/governance/task/task-card-standard.md` | 域 B 任务卡字段（execution_model、safety_level 等） |
| `docs/01_policies_and_standards/_registry/schemas/session-log-schema.yaml` | author_agent 字段 |
| `docs/01_policies_and_standards/_registry/catalogs/task-card-meta-registry.yaml` | 任务卡元数据 |
| `docs/08_knowledge/kms-entry-schema.md` | domain 10值、knowledge_type 6值 |
| `docs/01_policies_and_standards/templates/blueprint-template.md` | frontmatter 模板字段 |
| `docs/01_policies_and_standards/templates/blueprint-template.md` | 蓝图 + 施工指引统一模板（设计和实施合并） |
| `docs/01_policies_and_standards/meta/document-structure-standard.md`（PS-STD-002） | 元标准模板，§2.3 引用本注册表作为 frontmatter 字段定义的权威来源 |

#### 1.5.4 Tier 4：已废弃但仍有引用

| 文件 | 状态 | 说明 |
|------|------|------|
| `docs/01_policies_and_standards/meta/metadata-registry.md` | Deprecated | `superseded_by: metadata-registry.md`，旧 13 种 doc_type 长名 |
| `docs/19_development_workspace/structure-and-mapping/discussion-document-standard.md` | 已合并 | v2.0.0 被 metadata-registry.md v3.0.0 吸收 |

#### 1.5.5 ADR 设计决策源头

| ADR | 与本注册表的关系 |
|-----|----------------|
| `adr-0002-single-schema-with-phased-required-fields.md` | 本注册表分阶段必填闸门的设计依据 |
| `adr-0030-sqlite-task-metadata-store.md` | SQLite 元数据层与文档 frontmatter 的互补关系 |
| `adr-0040-pydantic-v2-structured-contracts.md` | Pydantic 模型与 frontmatter-schema.json 互为补充 |

#### 1.5.6 变更同步规则

| 变更类型 | Tier 1 同步要求 | Tier 2 同步要求 | Tier 3 同步要求 |
|---------|----------------|----------------|----------------|
| 新增枚举值 | 同 commit 更新硬编码 | 无需操作 | 无需操作 |
| 删除枚举值 | 同 commit 更新 + 迁移脚本 | 检查引用 | 检查引用 |
| 新增字段 | 同 commit 更新校验逻辑 | 无需操作 | 按需对齐 |
| 字段改名 | 同 commit 更新所有引用 | 同 commit 更新引用 | 同 commit 更新引用 |
| 修改必填阶段 | 同 commit 更新分阶段闸门 | 无需操作 | 无需操作 |

---

## 2. 域 A：文档 frontmatter 字段（40 个固定字段 + 1 个 custom_* 扩展）

### 2.1 全局字段总表

> **Canonical SSoT**：`_registry/catalogs/frontmatter-field-registry.yaml`（PS-REG-012）
>
> 以下仅列出字段名和必填阶段速查。完整的字段定义（类型、枚举值、描述、对标机构）请查阅 **PS-REG-012**，本文件不再重复。

| 字段 | 必填阶段 | 字段 | 必填阶段 |
|------|---------|------|---------|
| `module_id` | Draft+ | `title` | Draft+ |
| `doc_type` | Draft+ | `status` | Draft+ |
| `version` | Draft+ | `date` | Draft+ |
| `owner` | Draft+ | `layer` | Active+ |
| `classification` | Active+ | `language` | Active+ |
| `created_by` | Active+ | `ttl` | Active+ |
| `summary` | Active+ | `tags` | Active+ |
| `valid_from` | Active+ | `rule_form` | Active+ |
| `depends_on` | Active+ | `supersedes` | Active+ |
| `superseded_by` | Deprecated | `derived_from` | optional |
| `related_adr` | optional | `safety_level` | optional |
| `evolution_policy` | optional | `ai_autonomy` | optional |
| `provenance` | optional | `author_agent` | optional |
| `governance_family` | optional | `ai_capability_slot` | optional |
| `ai_autonomy_level_planned` | optional | `ai_employee_count_planned` | optional |
| `blueprint_refs` | optional | `compliance_tags` | optional |
| `human_override` | optional | `last_reviewed_by` | optional |
| `review_status` | optional | `category` | optional |
| `domain` | optional | `verifiability` | optional |
| `scope` | optional | `stability` | optional |
| `custom_*` | optional | | |

### 2.2 分阶段必填闸门

| 阶段 | 必填字段数 | 必填字段 |
|------|:---------:|---------|
| **Draft** | 7 | `module_id` `title` `doc_type` `status` `version` `date` `owner` |
| **Active** | 18 | Draft 全部 + `layer` `classification` `language` `created_by` `ttl` `summary` `tags` `rule_form` `scope` `stability` `verifiability` |
| **Deprecated** | 19 | Active 全部 + `superseded_by`（必填，有替代品填路径，无替代品填 `"N/A"`） |

**升格只改 `status` 值，不改 schema，不做字段迁移。**

### 2.3 字段排序约定

Frontmatter 中字段按以下顺序排列，便于 AI 和人类快速定位：

```
module_id → title → doc_type → status → version → layer →
owner → classification → language → created_by →
date → valid_from → ttl → summary → tags →
rule_form → scope → stability → verifiability → depends_on →
supersedes → superseded_by → derived_from → related_adr →
safety_level → evolution_policy →
ai_autonomy → provenance → author_agent →
governance_family → ai_capability_slot → ai_autonomy_level_planned → ai_employee_count_planned →
blueprint_refs → compliance_tags → human_override →
last_reviewed_by → review_status → category → domain → custom_*
```

### 2.4 YAML 文件特殊规则

- `status` 使用小写：`active` / `draft` / `deprecated`（仅 3 值，`superseded` 已废弃——见 status-vocabulary.yaml deprecated_values）
- 必须包含 `schema_version` 字段
- 日期字段使用 ISO 8601 格式

### 2.5 按 doc_type 分类的必填字段清单

> 以下清单仅适用于 `01_policies_and_standards/` 目录下的文件。
> 其他目录的文件仍按 §2.2 分阶段闸门执行。

| 字段 | policy | standard | operational_rule | register | protocol | template | adr | blueprint | construction_plan | roadmap |
|------|:------:|:-------:|:---------------:|:-------:|:-------:|:-------:|:---:|:-------:|:-----------------:|:------:|
| `module_id` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `title` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `doc_type` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `status` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `version` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `date` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `owner` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `layer` | 🔴 | 🔴 | 🔴 | 🟡 | 🔴 | 🔴 | 🟡 | 🔴 | 🔴 | 🔴 |
| `classification` | 🔴 | 🔴 | 🔴 | 🟡 | 🔴 | 🔴 | 🟡 | 🔴 | 🔴 | 🔴 |
| `language` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `created_by` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `ttl` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `summary` | 🔴 | 🔴 | 🔴 | 🟡 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `tags` | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | ⬜ | 🟡 | 🟡 | 🟡 | 🟡 |
| `rule_form` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `scope` | 🔴 | 🔴 | 🟡 | ⬜ | 🔴 | ⬜ | 🟡 | 🔴 | 🟡 | 🟡 |
| `stability` | 🔴 | 🔴 | 🟡 | ⬜ | 🔴 | ⬜ | 🟡 | 🔴 | 🔴 | 🟡 |
| `verifiability` | 🟡 | 🟡 | 🔴 | ⬜ | 🟡 | ⬜ | ⬜ | ⬜ | 🟡 | ⬜ |
| `depends_on` | 🟡 | 🟡 | 🟡 | ⬜ | 🟡 | ⬜ | 🟡 | 🟡 | 🟡 | ⬜ |
| `valid_from` | 🟡 | 🟡 | ⬜ | ⬜ | 🟡 | ⬜ | 🟡 | 🟡 | 🟡 | 🟡 |
| `supersedes` | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| `superseded_by` | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| `derived_from` | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| `evolution_policy` | 🟡 | 🟡 | ⬜ | ⬜ | 🟡 | ⬜ | ⬜ | 🟡 | ⬜ | 🟡 |
| `ai_autonomy` | 🟡 | 🟡 | 🟡 | ⬜ | 🟡 | ⬜ | 🟡 | 🟡 | 🟡 | 🟡 |

> 🔴 = 必填 | 🟡 = 条件必填 | ⬜ = 可选

**条件必填说明**：

| 字段 | 条件 |
|------|------|
| `tags` | 当 `scope: layer` 时必填，需标注所属层 |
| `layer` | register/ADR 如为全局型则填 `cross_layer`，层域型填对应层 |
| `classification` | register/ADR 如含敏感信息则必填 `confidential` |
| `verifiability` | operational_rule 必填（操作规程必须可验证）; construction_plan 有可验证产出物时必填 |
| `depends_on` | 当文件依赖其他文件才能执行时必填 |
| `valid_from` | policy/standard/protocol/ADR/blueprint/construction_plan/roadmap 有生效日期时必填 |
| `evolution_policy` | policy/standard/protocol/blueprint/roadmap 有演进策略时必填 |
| `ai_autonomy` | 涉及 AI 操作权限时必填 |

**受控词表速查**：

| 字段 | 合法值 |
|------|--------|
| `rule_form` | `declarative` / `procedural` / `data` / `structural` |
| `scope` | `global` / `domain` / `layer` / `module` |
| `stability` | `frozen` / `stable` / `evolving` / `volatile` |
| `verifiability` | `automated` / `manual` / `inspection` |

### 2.6 一致性约束

> 以下约束确保 frontmatter 各字段之间不矛盾。AI 写 frontmatter 时必须逐项检查。

| # | 约束 | 说明 |
|---|------|------|
| 1 | `stability: frozen` → `ai_autonomy: immutable_core` | 冻结文件 AI 不可修改 |
| 2 | `stability: volatile` → `ai_autonomy` ≠ `immutable_core` | 易变文件不可能是不可修改的 |
| 3 | `doc_type: policy` → `rule_form: declarative` | policy 必须是声明式 |
| 4 | `doc_type: standard` → `rule_form: declarative` | standard 必须是声明式 |
| 5 | `doc_type: operational_rule` → `rule_form: procedural` | operational_rule 必须是过程式 |
| 6 | `doc_type: register` → `rule_form: data` | register 必须是数据形式 |
| 7 | `doc_type: template` → `rule_form: structural` | template 必须是结构形式 |
| 8 | `doc_type: adr` → `rule_form: declarative` | ADR 是声明式决策记录（对标 Nygard ADR 原始定义） |
| 9 | `doc_type: blueprint` → `rule_form: structural` | blueprint 是结构化设计规范（对标 TOGAF Architecture Definition Document） |
| 10 | `doc_type: construction_plan` → `rule_form: structural` | construction_plan 是结构化执行计划（对标 ITIL Change Enablement Plan） |
| 11 | `doc_type: roadmap` → `rule_form: declarative` | roadmap 是声明式方向规划，AI 不执行 roadmap 本身 |

> **架构公民原则（避免误判）**：
> - 约束 #1 是单向的（`frozen` → `immutable_core`），其**逆面不成立**：`stability: stable` + `ai_autonomy: immutable_core` 是合法组合（如 PS-STD-003——稳定但 AI 不可修改的核心规则）
> - `stability` 描述文件的"内容变更频率"，`ai_autonomy` 描述"谁有权改"——两者正交不耦合
> - 合法映射光谱：
>   - `frozen` → `immutable_core`（强制）
>   - `stable` → `immutable_core` 或 `human_gated`（均合法）
>   - `evolving` → `human_gated` 或 `ai_modifiable`（均合法）
>   - `volatile` → 不能是 `immutable_core`（约束 #2）

### 2.7 frontmatter 模板

> **SSoT：frontmatter 模板的唯一真源是 `templates/` 目录下的骨架文件。**
> AI 创建新文件时，从 `templates/` 目录下对应的骨架文件复制 frontmatter，填入具体值。
>
> 本注册表不再重复定义模板内容。模板文件清单和格式见 [templates/](01_policies_and_standards/templates/) 目录。

### 2.8 frontmatter 禁止行为

| # | 禁止 | 原因 |
|---|------|------|
| 1 | 禁止 `doc_type` 与 `rule_form` 矛盾（如 policy 配 procedural、operational_rule 配 declarative） | 全部约束见 §3.6 #5（跨域禁止 §2.8 与领域专属禁止 §3.6 互补不重叠） |
| 2 | 禁止 `stability: frozen` 配 `ai_autonomy: ai_modifiable` | 冻结文件 AI 不可修改 |
| 3 | 禁止省略 `rule_form` 字段（Active 状态以上） | rule_form 是 Active+ 必填字段 |
| 4 | 禁止使用未在 §2.1 注册的字段名 | 所有字段必须先注册再使用 |
| 5 | 禁止 `scope` 与 `layer` 矛盾 | `scope: layer` 时 `layer` 不能是 `cross_layer` |
| 6 | 禁止 `verifiability: inspection` 配 `doc_type: operational_rule` | 操作规程必须可自动或手动验证，不能只靠目视检查 |

---

## 3. doc_type 受控词表

### 3.1 设计原则

1. **自下而上归纳**：词表从项目 230+ 文件的实际使用中归纳，不是拍脑袋定的
2. **短名优先**：用 `standard` 而非 `governance_standard`，靠 `layer` 字段区分领域
3. **AI 可记忆**：每种类型有明确的 AI 查询关键词，AI 无需查表即可判断
4. **可扩展**：新增 doc_type 需提决策记录（MOD-KB-001 §3.9.5），审批后更新本文件

### 3.2 完整受控词表

> **Canonical SSoT**：[`_registry/vocabularies/doc_type-vocabulary.yaml`](../_registry/vocabularies/doc_type-vocabulary.yaml)
>
> 全项目 27 种 doc_type。以下为快速速查——完整定义（definition、allowed_directories、forbidden_directories、required_fields、ai_keywords、deprecated_values 等）请查阅词汇表 YAML。
>
> **`01_policies_and_standards/` 子集（13 种）**：
> `policy` `standard` `operational_rule` `register` `index` `protocol` `template` `terminology` `vocabulary` `contract` `reference` `gate` `schema`
>
> **其他目录（14 种）**：
> `adr` `blueprint` `construction_plan` `design` `plan` `roadmap` `readme` `log` `knowledge_entry` `audit_report` `service_spec` `architecture_view` `declaration` `config`
>
> **SSoT 铁律**：vocabulary YAML = 唯一真源，本 Markdown = 指路牌。冲突时以 YAML 为准。新增/废弃 doc_type 一律先在 YAML 操作——本表不需要手动同步。

#### 3.2.1 `01_policies_and_standards/` 子集（13 值）

> 全项目有 27 种 doc_type，但 `01_policies_and_standards/` 目录下**只使用以下 13 种**。
> 其他 doc_type（如 `blueprint`、`construction_plan`、`roadmap`、`knowledge_entry`）属于其他目录，不在此处使用。
> **例外**：`templates/` 下的模板文件不受此 13 值子集约束——模板 doc_type 取目标文档类型。
> 例如 `blueprint-template.md` 的 `doc_type: blueprint` 合法（它为蓝图提供模板，其 doc_type 表达的是目标，不是文件本身的分类）。

| # | doc_type | 含义 | 对应目录 | rule_form |
|---|----------|------|---------|-----------|
| 1 | `policy` | 强制约束 | `governance/` | 声明式 |
| 2 | `standard` | 推荐做法 | `governance/` | 声明式 |
| 3 | `operational_rule` | 操作规程 | `operational/` | 过程式 |
| 4 | `register` | 登记表 | `_registry/` | 数据 |
| 5 | `index` | 目录索引 | 所有目录 | 声明式 |
| 6 | `protocol` | 协议 | `governance/` | 声明式 |
| 7 | `terminology` | 术语表 | `meta/` | 数据 |
| 8 | `template` | 模板 | `templates/` | 结构 |
| 9 | `vocabulary` | 受控词表 | `_registry/vocabularies/` | 数据 |
| 10 | `contract` | 验证契约 | `_registry/contracts/` | 数据 |
| 11 | `reference` | 参考文档 | `_registry/catalogs/` | 数据 |
| 12 | `gate` | 质量门禁 | `_registry/` | 声明式 |
| 13 | `schema` | Schema 定义 | `_registry/schemas/` | 数据 |

#### 3.2.2 policy vs standard vs operational_rule 判据

> **问一个问题就能区分**：这个文件是在"定规矩"还是在"教操作"？

| 文件在做什么 | doc_type | 归属 | 例子 |
|------------|----------|------|------|
| 定义"什么是对的/错的"——必须、禁止、不得 | `policy` | `governance/` | "所有 API 密钥必须存储在环境变量中" |
| 定义"推荐怎么做"——应该、建议、最佳实践 | `standard` | `governance/` | "建议使用 Pydantic v2 做数据验证" |
| 定义"按步骤执行"——步骤 1→2→3 | `operational_rule` | `operational/` | "Step 1: 检查 .env → Step 2: 验证密钥格式" |

**3 个测试**：

| 测试 | policy | standard | operational_rule |
|------|--------|----------|-----------------|
| 删掉步骤描述，规则还成立吗？ | ✅ 成立 | ✅ 成立 | ❌ 不成立（没有步骤就没法执行） |
| 违反了会怎样？ | 🔴 严重（红线） | 🟡 不推荐（但不是红线） | 🔴 操作出错（按步骤才能避免） |
| 换一个人/AI 执行，结果一样吗？ | ✅ 一样（规则不变） | ⚠️ 可能不同（推荐做法有弹性） | ✅ 一样（步骤固定） |

#### 3.2.3 protocol vs policy 的区别

| 维度 | policy | protocol |
|------|--------|----------|
| 主体 | 单方约束 | 多方交互 |
| 核心问题 | "必须/禁止什么" | "谁先做什么，然后谁做什么" |
| 例子 | "密钥必须加密存储" | "交接协议：发出方 → 审核方 → 接收方" |
| 判断标准 | 只涉及一方 | 涉及两方以上的交互时序 |

**简单判断**：如果文件描述的是"谁→谁→谁"的交互流程，用 `protocol`；如果只是"必须/禁止 X"，用 `policy`。

### 3.3 doc_type 与 layer 的联动

`doc_type` 回答"这是什么品种"，`layer` 回答"属于哪个领域"。两者组合定位文档。

> 完整映射表见 vocabulary YAML 各条目的 `allowed_directories` 字段。
> 以下为典型示例（非完整枚举）：

| 组合示例 | 含义 |
|---------|------|
| `doc_type: policy` + `layer: cross_layer` | 全局强制规则 |
| `doc_type: standard` + `layer: cross_layer` | 全局推荐做法 |
| `doc_type: standard` + `layer: l04_ml_platform` | 机器学习层推荐做法 |
| `doc_type: blueprint` + `layer: l00_data_source` | 数据源层蓝图 |
| `doc_type: construction_plan` + `layer: l00_data_source` | 数据源层施工图 |
| `doc_type: architecture_view` + `layer: cross_layer` | 跨层正式架构视图 |
| `doc_type: plan` + `layer: cross_layer` | 跨层任务书 |
| `doc_type: roadmap` + `layer: cross_layer` | 跨层路线图 |

### 3.4 doc_type 与存放路径的映射

> Canonical SSoT 见 vocabulary YAML 各条目的 `allowed_directories` 和 `forbidden_directories` 字段。
> 以下为关键规则速查——不含已废弃类型。

| doc_type | 应存放的目录 | 禁止存放的目录 |
|----------|------------|--------------|
| `policy` | `01_policies_and_standards/governance/` | `03_modules/` `08_knowledge/` |
| `standard` | `01_policies_and_standards/governance/` `08_knowledge/` | `03_modules/` |
| `adr` | `02_enterprise_architecture/adr/` | 其他所有目录 |
| `blueprint` | `03_modules/l<NN>_<layer>/<module>/` | `01_policies_and_standards/` |
| `construction_plan` | `03_modules/l<NN>_<layer>/<module>/` | `01_policies_and_standards/` |
| `architecture_view` | `02_enterprise_architecture/target-architecture/` | `01_policies_and_standards/` `03_modules/` |
| `design` | `02_enterprise_architecture/` | | `01_policies_and_standards/` `03_modules/` |
| `operational_rule` | `01_policies_and_standards/operational/` | `governance/` `03_modules/` |
| `protocol` | `01_policies_and_standards/governance/` | `03_modules/` |
| `register` | `01_policies_and_standards/_registry/` | `03_modules/` |
| `vocabulary` | `01_policies_and_standards/_registry/vocabularies/` | `governance/` `operational/` |
| `contract` | `01_policies_and_standards/_registry/contracts/` | `governance/` `operational/` |
| `template` | `01_policies_and_standards/templates/` | — |
| `terminology` | `01_policies_and_standards/meta/` | — |
| `index` | 各目录根 | — |
| `readme` | 各目录根 | — |
| `log` | `09_audit/` | | `03_modules/` |
| `knowledge_entry` | `08_knowledge/` | `01_policies_and_standards/` |
| `audit_report` | `09_audit/` | — |
| `service_spec` | `03_modules/_b_track_interfaces/` | — |
| `plan` | `01_policies_and_standards/` | | — |
| `roadmap` | `01_policies_and_standards/` | | — |
| `declaration` | `docs/`（项目根） | `01_policies_and_standards/` |

#### 3.4.1 防幻觉三向映射（doc_type → directory → rule_form）

> AI 判断"这个文件该放哪、该是什么格式"时，查这张表。三个维度**一一对应**，不允许交叉。

| doc_type | 唯一目录 | rule_form | 反向验证 |
|----------|---------|-----------|---------|
| `policy` | `governance/` | 声明式 | governance/ 下只能是 policy / standard / protocol |
| `standard` | `governance/` | 声明式 | 同上 |
| `protocol` | `governance/` | 声明式 | 同上 |
| `operational_rule` | `operational/` | 过程式 | operational/ 下只能是 operational_rule |
| `register` | `_registry/` | 数据 | _registry/ 下只能是 register |
| `template` | `templates/` | 结构 | templates/ 下模板文件的 doc_type 取目标文档类型。"template"作为 doc_type 仅用于"模板的模板"（如本目录结构模板本身）；cookbook template（用于生成目标文档的预填骨架）其 doc_type = 目标类型（如 blueprint-template.md 的 doc_type: blueprint）。对标：K8s Helm template 不改 kind 为 Template，ITIL 模板不改标题加 "Template" 前缀。 |

### 3.5 新增 doc_type 的流程

1. 在实际使用中发现现有 27 种无法覆盖的文档类型
2. 提交决策记录（MOD-KB-001 §3.9.5），说明：新类型名称、与现有类型的区别、为什么不能归入现有类型
3. 决策记录审批通过后，**仅更新 `_registry/vocabularies/doc_type-vocabulary.yaml`**（canonical SSoT）——本文件 §3.2 为速查引用、§3.4 为派生表，不需要手动同步
4. 校验器 `check_frontmatter_metadata.py` 从 YAML 动态加载合法值——无需修改校验代码
5. 同步更新 `frontmatter-schema.json`（自动生成）
5. 在下一个 pre-commit 版本中纳入新值的校验

### 3.6 doc_type 禁止行为

| # | 禁止 | 原因 |
|---|------|------|
| 1 | 禁止在 `governance/` 下使用 `operational_rule` | governance/ 只放声明式，operational_rule 是过程式 |
| 2 | 禁止在 `operational/` 下使用 `policy` 或 `standard` | operational/ 只放过程式，policy/standard 是声明式 |
| 3 | 禁止使用旧长名（`governance_standard`、`governance_registry` 等） | 已迁移到短名，旧长名不再合法 |
| 4 | 禁止使用未在本文件 §3.2 注册的 doc_type | 所有 doc_type 必须先注册再使用 |
| 5 | 禁止 `doc_type` 与 `rule_form` 矛盾 | 声明式 doc_type 不能配过程式 rule_form，反之亦然 |

---

## 4. status 受控词表（三域分离）

> **核心原则**：文档、任务、知识条目的生命周期不同，状态机不同，枚举值不同。
> 三个 status 各管各的，不混用、不别名、不合并。

### 4.1 DocStatus（域 A：文档 frontmatter）

> **真元规则（Owner 裁定，2026-04-29）**：DocStatus 从 7 种精简为 3 种。

| status | 含义 | AI 行为 | superseded_by |
|--------|------|--------|:------------:|
| `draft` | 草稿，内容未稳定 | 可参考但不作为权威 | 不需要 |
| `active` | 生效中，当前有效 | 作为权威参考，修改需走变更流程 | 不需要 |
| `deprecated` | 已废弃，不应再使用 | 不再参考 | **必填**（有替代品填路径，无替代品填 `"N/A"`） |

**选择理由（为什么从 7 种精简为 3 种）**：

1. **Vibe Coding 语境**：AI 只需要知道"能不能用"——draft（还没好）、active（可以用）、deprecated（不能用了）。7 种状态中 `in_discussion` 跟 `draft` 的区别、`review_ready` 跟 `active` 的区别、`accepted` 跟 `active` 的区别，AI 经常搞混，最终退化成 3 种。

2. **行业参考**：MoAI Foundation Specs（AI Agent 开发框架）用 4 种（Draft/Active/Deprecated/Archived）；RAG 系统文档生命周期用 4 种（Active/Deprecated/Archived/Deleted）；OpenTelemetry 用 4 种（Development/Stable/Deprecated/Removed）。3 种是最精简的方案。

3. **废弃原因靠 `superseded_by` 字段区分**：不需要靠 status 值来区分"为什么废弃"。有 `superseded_by` 路径 = 被取代，`superseded_by: "N/A"` = 单纯过时。IETF RFC 也用 `Obsoleted-by` 字段而非单独的 status 值来区分。

4. **审阅由 `review_status` 字段单独管**：项目已有 `review_status` 字段（4 种：unreviewed/reviewed/approved/rejected），不需要在 DocStatus 里重复 `review_ready` 和 `accepted`。

5. **不按 doc_type 分状态**：真源文件已按域分三套状态机（文档/任务/知识），不需要再按文档类型细分。所有文档类型共用同一套 DocStatus，AI 不需要记"ADR 用这套、blueprint 用那套"。

**否决方案**：

| 方案 | 否决理由 |
|------|---------|
| 7 种（旧规则） | AI 经常搞混 `in_discussion`/`draft`、`accepted`/`active`；`review_ready`/`accepted` 跟 `review_status` 重复；自然退化成 3 种 |
| 5 种（+review_ready） | 跟 `review_status` 功能重叠；Confluence 有是因为组织需要经理签字，个人项目不需要 |
| 4 种（+archived） | `archived` 和 `deprecated` 对 AI 来说行为一样（都不再参考），区分无意义；归档是文件操作（移动到 archive 目录），不是文档状态 |

**状态流转**：

```
draft → active → deprecated
  ↑                  │
  └──────────────────┘（重新启用，需 Owner 审批）
```

**降格规则**：
- `active` → `deprecated`：需 Owner 审批 + 填写 `superseded_by`（必填）
- `deprecated` → `active`：需 Owner 审批（重新启用）
- 禁止跨级降格（`draft` 不能直接变 `deprecated`，必须先升格为 `active`）

#### 4.1.1 生命周期引用约束（Lifecycle Reference Constraint）——2026-05-02 新增

> **对标**：Kubernetes Admission Controller（准入控制器拒绝非法请求） + ITIL Change Enablement（变更前评估消费者影响）
>
> **动机**：2026-05-02 审计发现 GOV-MOD-002（draft，已升格 active v1.0.0）被 6 个 active 文件量产级引用、GOV-MOD-007（draft，已升格 active v2.1.0）被 registry-of-registries.yaml 引用。status 字段与 depends_on 之间没有互锁机制——"出生即公民"的默认假设覆盖了 draft 状态的"我还不是正式公民"的真实含义。

##### MUST 规则

| # | 规则 | 违反后果 |
|---|------|---------|
| **LRC-001** | `status: draft` 的文件 **不得** 被任何 `status: active` 的文件通过 `depends_on` 声明依赖 | 消费者获得的规则可能尚未稳定——AI session 行为漂移 |
| **LRC-002** | `status: draft` 的文件 **不得** 被任何 `status: active` 的文件在正文中作为权威引用（`see X §Y` 形式的规范性引用） | 同上 |
| **LRC-003** | 审批 `draft → active` 升格时，必须**先检查消费者清单**——所有已引用该文件的其他文件是否需要同步变更 | 升格后发现消费者与新版不兼容——返工成本 |

##### SHOULD 规则

| # | 规则 |
|---|------|
| **LRC-004** | `draft` 文件被 3 个以上活跃文件引用时，应评估是否已达 `active` 成熟度——实质活跃应升格 |
| **LRC-005** | 新 AI session 读到 `draft` 文件被多个活跃文件引用时，应标记为 MEDIUM Finding 提请 Owner 裁定 |

##### 设计意图：为什么 stage 比 status 更根本

当前 `status` 字段是**描述性**的——它描述文件当前状态，但不约束文件的交互行为。
对标 Kubernetes：alpha API 不能被 stable API 依赖——不是因为手动标了 `status: alpha`，而是因为它没通过 graduation gate。

**未来方向**（beta+）：引入 `lifecycle_stage` 字段，由门禁系统自动推进：

```
draft_stage  →  blueprint_review  →  construction_review  →  active_stage
  （出生）         （蓝图门通过）          （施工门通过）            （生产就绪）
```

`status` 由 `lifecycle_stage` 推导：
- `lifecycle_stage < active_stage` → `status: draft`（不可被 active 文件引用）
- `lifecycle_stage >= active_stage` → `status: active`（可被引用）

> **大白话**：现在的 status 是自己贴的标签——贴了跟没贴一样。将来的 stage 是门禁系统盖的章——没过蓝图门就是 draft，过了就是 active。这样就不会出现"明明还是个草稿却被到处引用"的尴尬了。

##### `lifecycle_stage` 字段定义（beta 落地）

| stage 值 | 含义 | 对应的门 | 等价 status |
|:---------|:-----|:--------|:-----------:|
| `draft` | 草稿阶段——内容未稳定，AI 自由编辑 | 无 | `draft` |
| `blueprint_reviewed` | 已通过蓝图评审——设计方向已确认 | GATE-BP-001（蓝图完整性门） | `draft`（不可被 active 引用） |
| `construction_reviewed` | 已通过施工评审——实现方案已验证 | GATE-CT-001（施工可执行性门） | `draft`（不可被 active 引用） |
| `active` | 生产就绪——可供全项目引用 | GATE-AD-001（active 准入门） | `active` |

**流转约束**：`lifecycle_stage` 只进不退（只能 forward，不能 rollback），对标 Kubernetes API version 的单向演进策略。

### 4.2 TaskStatus（域 B：任务系统）

> 代码真源：`src/zephyr/schemas.py` `TaskStatus` 枚举

| status | 含义 | 终态？ |
|--------|------|:------:|
| `PENDING` | 待执行 | ❌ |
| `IN_PROGRESS` | 执行中 | ❌ |
| `COMPLETED` | 已完成 | ❌ |
| `VERIFIED` | 已验证 | ✅ |
| `FAILED` | 执行失败 | ❌ |
| `BLOCKED` | 被阻塞 | ❌ |
| `WAITING` | 等待中 | ❌ |
| `READY` | 就绪待执行 | ❌ |
| `RETRY` | 重试中 | ❌ |
| `CANCELLED` | 已取消 | ✅ |

**状态流转**（代码真源：`task_repo.py`）：

```
PENDING → IN_PROGRESS → COMPLETED → VERIFIED
  ↓          ↓              ↓
BLOCKED    FAILED         CANCELLED
  ↓          ↓
 READY     RETRY → IN_PROGRESS
WAITING → READY
```

### 4.3 KeStatus（域 C：知识条目）

> 代码真源：`src/zephyr/kb/kb_repo.py` `KeStatus` 枚举

| status | 含义 | 终态？ | 向量可见？ |
|--------|------|:------:|:---------:|
| `DRAFT` | 草稿 | ❌ | ❌ |
| `SUBMITTED` | 已提交待审 | ❌ | ❌ |
| `REVIEWED` | 已审阅 | ❌ | ❌ |
| `ACCEPTED` | 已接受 | ❌ | ❌ |
| `INDEXED` | 已索引 | ❌ | ✅ |
| `VERIFIED` | 已验证 | ❌ | ✅ |
| `REJECTED` | 已否决 | ❌ | ❌ |
| `DEPRECATED` | 已废弃 | ❌ | ✅ |
| `SUPERSEDED` | 已取代 | ❌ | ✅ |
| `ARCHIVED` | 已归档 | ✅ | ❌ |

**状态流转**（代码真源：`kb_repo.py`）：

```
DRAFT → SUBMITTED → REVIEWED → ACCEPTED → INDEXED → VERIFIED
                     ↓          ↓          ↓         ↓
                  REJECTED   REJECTED   REJECTED   DEPRECATED → ARCHIVED
                     ↓                              SUPERSEDED → ARCHIVED
                   DRAFT
```

### 4.4 三域 status 对照表

| 维度 | DocStatus | TaskStatus | KeStatus |
|------|-----------|------------|----------|
| 域 | A（文档） | B（任务） | C（知识） |
| 值数量 | 3 | 10 | 10 |
| 大小写 | 枚举值小写 / 标识符大写 | 全大写 | 全大写 |
| 终态 | deprecated / superseded | VERIFIED / CANCELLED | ARCHIVED |
| 代码真源 | 本文件 §4.1 | schemas.py | kb_repo.py |
| 对标专业机构 | MLflow: status | IETF: task_status | OpenLineage: lifecycleState |

### 4.5 大小写约定：枚举值小写 + 标识符大写

> **真元规则（Owner 裁定，2026-04-29）**：frontmatter 字段值的大小写取决于字段类型——枚举值统一小写，标识符统一大写。

#### 4.5.1 两条核心规则

| 字段类型 | 大小写 | 例子 | 判断标准 |
|---------|:------:|------|---------|
| **枚举值** | **全小写** | `status: active`、`doc_type: standard`、`layer: l01_infrastructure`、`classification: confidential`、`ai_autonomy_level: immutable_core` | 从**有限选项**里选一个 |
| **标识符** | **全大写** | `module_id: L00-DS-001`、`module_id: ADR-0011`、`module_id: PS-STD-001` | 每个都**唯一**，不是从选项里选的 |

#### 4.5.2 为什么枚举值用小写？

1. **Vibe Coding 语境**：本项目的 frontmatter 主要由 AI 读取、AI 写入、AI 工作。AI 做字符串比较时严格区分大小写，`Active != active`，大小写不一致是最常见的 AI 识别错误来源。统一小写消除了这个出错点。

2. **零认知负担**：枚举值全小写，不需要记"哪个首字母大写、哪个不大写"。AI 和人类都不用想。

3. **与文件命名规则一致**：项目已裁定所有文件名和文件夹名全小写（kebab-case）。枚举值也全小写，跟文件命名规则保持一致。

4. **行业参考**：OpenSSF ADR-0013 讨论了 YAML 枚举值的 4 种大小写方案（Title Case / kebab-lower / camelCase / PascalCase），最终选择 Title Case 的理由是"为人类作者优化，视觉区分键和值"。但本项目的场景不同——AI 是主要消费者，"为 AI 优化"比"为人类视觉优化"更重要。Hugo/Jekyll 等工具也采用全小写方案。

5. **pre-commit 校验**：校验脚本只需匹配一种写法，不需要同时接受 `Active` 和 `active`，简化了门禁逻辑。

#### 4.5.3 为什么标识符用大写？

1. **可搜索性**：大写标识符在文本中**一眼就能认出来**。在一大段文字里看到 `L00-DS-001`，立刻知道这是一个模块编号；看到 `l00-ds-001`，可能以为是一段代码或路径。AI 用正则 `L\d{2}-[A-Z]+-\d{3}` 搜索，精准无歧义。

2. **与枚举值视觉区分**：枚举值小写、标识符大写，两种字段在 frontmatter 中天然区分。AI 读到 `status: active` 知道是枚举值，读到 `module_id: L00-DS-001` 知道是标识符，不需要额外判断。

3. **专业机构对标**：Linux Kernel（文件名小写 + 宏/常量大写）、Rust RFCs（文件名 `rfc-0001-*.md` 小写 + 标识符 `RFC-0001` 大写）、Google Engineering Practices（文件名小写 + 标识符大写）、HGNC 人类基因命名委员会（基因符号只允许大写字母+数字，如 `BRCA1`、`TP53`）。本项目 Stage F 已正式对标这三家机构（见 handoff-log §Stage F 工程级贡献）。

4. **正交性原则**：文件名是人类索引（小写），module_id 是机器索引（大写），两者规范独立不耦合。这是 Stage F 裁定的宪法条款（file-naming-standard.md §2.2.3），避免两套索引互相锁死。

5. **1500+ 模块规模**：在 1500 个模块的规模下，标识符必须能被快速定位。大写 + 连字符分隔的格式（`L00-DS-001`）比全小写（`l00-ds-001`）在 grep/ripgrep 中误匹配率更低。

#### 4.5.4 完整字段分类表

| 字段 | 类型 | 大小写 | 示例 |
|------|------|:------:|------|
| `status` | 枚举值 | 小写 | `draft` `active` `deprecated` |
| `doc_type` | 枚举值 | 小写 | `standard` `policy` `blueprint` |
| `classification` | 枚举值 | 小写 | `public` `confidential` |
| `layer` | 枚举值 | 小写 | `l01_infrastructure` `cross_layer` |
| `ai_autonomy_level` | 枚举值 | 小写 | `immutable_core` `ai_modifiable` `human_gated` |
| `ttl` | 枚举值 | 小写 | `permanent` `30d` `7d` `session` `periodic_review_90d` |
| `language` | 枚举值 | 小写 | `zh` `en` `zh_en` |
| `module_id` | **标识符** | **大写** | `L00-DS-001` `ADR-0011` `PS-STD-001` `KE-016` |
| `title` | 自由文本 | 自然语言 | `编码安全规范` |
| `version` | 语义版本 | 数字 | `1.0.0` |

#### 4.5.5 否决方案

| 方案 | 否决理由 |
|------|---------|
| `.md` 首字母大写 + `.yaml` 小写（旧规则） | 两套规则增加认知负担；AI 容易写错；宪法文件自身都写成了小写，说明规则不可执行 |
| Title Case（OpenSSF 方案） | 为人类视觉优化，不为 AI 优化；AI 严格区分大小写，Title Case 反而增加出错概率 |
| PascalCase（Open Data Fabric 方案） | 多词值可读性差（`NotApplicable`）；AI 需要额外映射逻辑 |
| 全部统一大写 | 枚举值大写（`STATUS: ACTIVE`）增加 AI 出错概率；跟文件名小写规则冲突；无专业机构先例 |
| 全部统一小写（包括标识符） | 标识符小写（`l00-ds-001`）跟文件路径混淆；AI 无法快速区分"这是编号还是路径"；跟 Stage F 正交性裁定矛盾 |

> TaskStatus 和 KeStatus 在代码中全大写（`PENDING` / `COMPLETED` / `DRAFT` / `INDEXED` 等），
> 这是 Python 枚举的惯例，与 frontmatter 枚举值无关——它们是域 B/C 专用，不在 frontmatter 中使用。
> pre-commit 校验时，域 A 枚举值只接受小写，标识符只接受大写。

### 4.6 classification 二分法：public / confidential

> **真元规则（Owner 裁定，2026-04-29）**：classification 只保留两种值。

| 值 | 含义 | AI 行为 |
|----|------|--------|
| `public` | 可以公开——泄露无影响 | 可自由分享 |
| `confidential` | 不能泄露——泄露会造成损害 | 禁止外传，需访问控制 |

> **两个维度各管各的**：`classification` 管"能不能公开"（二元），`ai_autonomy_level` 管"AI 能不能改"（三级）。
> 编码规范和交易策略都标 `confidential`（都不能公开），但编码规范是 `ai_modifiable`（AI 可以改），交易策略是 `immutable_core`（AI 不能碰）。
> 不要用 `classification` 来区分敏感程度——那是 `ai_autonomy_level` 的工作。

**选择理由（为什么只用两种）**：

1. **二分法最清晰**：一份文件要么可以公开，要么不能。没有中间地带。`internal`（内部使用）是一个模糊的灰色地带——"内部"到底能不能给合作方看？AI 无法判断，人类也经常拿不准。

2. **Vibe Coding 语境**：AI 需要明确的二元判断。`public` = 可以放出去，`confidential` = 不能放出去。不需要想"这个 internal 到底算不算敏感"。行业实践佐证：（a）OWASP Agentic AI 安全指南的核心原则是"最小权限"——AI 只能访问它完成任务所需的数据，判断是二元的（能访问/不能访问），不是三级的；（b）GitHub 爆火的 Vibe Coding 中文指南（阿里云专家）将数据只分"能给 AI 的"和"不能给 AI 的"两类，无中间层；（c）Airbyte / Azure AI Agent 安全实践均采用二元授权模型——AI 要么被授权访问，要么不被授权，`internal` 在 AI Agent 语境下无意义；（d）三分法在 Vibe Coding 下会自然退化成二分法——AI 用着用着就会把 `internal` 当 `confidential` 处理，与其让它自然退化，不如一开始就用二分法。

3. **商业标准对齐**：微软 Purview、AWS、CompTIA Security+ 商业分类体系的核心就是 public vs confidential 的二分。`internal` 是部分厂商添加的中间层，并非必需。

4. **与 `secret` 的区别**：`secret` 是军方/政府术语（US Executive Order 13526），在军方体系里 `secret` 比 `confidential` 高一级。本项目是商业量化交易系统，不使用军方分级，避免术语混淆。

5. **现有 `internal` 文件的处理**：当前 100 个标 `internal` 的文件，逻辑上都是"不能公开泄露"的，统一归入 `confidential`。批量迁移在后续 session 中执行。

**否决方案**：

| 方案 | 否决理由 |
|------|---------|
| 三分法 `public` / `internal` / `confidential`（旧规则） | `internal` 是灰色地带，AI 无法准确判断；100 个文件标了 internal 但语义模糊 |
| 军方三分法 `public` / `confidential` / `secret` | `secret` 在军方体系里比 `confidential` 高一级，本项目不需要这个区分；术语混淆风险 |
| 四分法 `public` / `internal` / `confidential` / `restricted` | 过度工程，个人项目不需要四级分类 |

> **迁移说明**：`internal` 值从本版本起废弃。现有 `classification: internal` 的文件需批量改为 `classification: confidential`。
> 代码真源 `schemas.py` `Classification` 枚举需删除 `INTERNAL`，默认值改为 `CONFIDENTIAL`。
> 数据库 DDL CHECK 约束需同步更新。此迁移在后续 session 中执行。

---

## 5. module_id 命名规范

### 5.1 格式

```
<DOMAIN>-<TYPE>-<NNN>
```

| 部分 | 规则 | 示例 |
|------|------|------|
| DOMAIN | 2-4 字符大写缩写 | `PS` `EA` `BP` `CP` `KE` `AR` `AG` `DW` |
| TYPE | 2-4 字符大写缩写 | `STD` `REG` `ADR` `DSG` `PLAN` `LOG` |
| NNN | 三位数字，零填充 | `001` `012` `123` |

### 5.2 DOMAIN 注册表

#### 5.2.1 已注册 DOMAIN（23 个）

| DOMAIN | 含义 | 对应目录 | 注册来源 |
|--------|------|---------|---------|
| `PS` | Policies & Standards | `01_policies_and_standards/` | v4.4.0 已注册 |
| `EA` | Enterprise Architecture | `02_enterprise_architecture/` | v4.4.0 已注册 |
| `MOD` | Module | `03_modules/` | v3.0.0 已注册 |
| `KE` | Knowledge Entries | `08_knowledge/` | v4.4.0 已注册 |
| `AR` | Audit Reports | `09_audit/` | v4.4.0 已注册 |
| `CM` | Compliance | `10_compliance/` | v4.4.0 已注册 |
| `AE` | AI Engineering | `03_modules/_b_track_interfaces/` | v4.4.0 已注册 |
| `AG` | AI Governance | `01_policies_and_standards/governance/ai/` | v4.4.0 已注册 |
| `DW` | ~~Development Workspace~~ 已删除 | `—` | `19_development_workspace/` 已于 2026-05-02 删除 |
| `L{XX}` | 业务层（L00-L13） | `src/zephyr/l{xx}_*/` | v4.4.0 已注册 |
| `GOV-DOC` | 文档治理 | `01_policies_and_standards/governance/document/` | v5.0.0 新增 |
| `GOV-AI` | AI 治理 | `01_policies_and_standards/governance/ai/` | v5.0.0 新增（替代原 `AG` 域） |
| `GOV-TASK` | 任务治理 | `01_policies_and_standards/governance/task/` | v5.0.0 新增 |
| `GOV-SEC` | 安全治理 | `01_policies_and_standards/governance/security/` | v5.0.0 新增 |
| `GOV-CMP` | 合规治理 | `01_policies_and_standards/governance/compliance/` | v5.0.0 新增 |
| `GOV-ARCH` | 架构治理 | `01_policies_and_standards/governance/architecture/` | v5.0.0 新增 |
| `GOV-DATA` | 数据治理 | `01_policies_and_standards/governance/data/` | v5.0.0 新增 |
| `GOV-MOD` | 模块治理 | `01_policies_and_standards/governance/module/` | v5.0.0 新增 |
| `OPS-VC` | Vibe Coding 操作 | `01_policies_and_standards/operational/vibe_coding/` | v5.0.0 新增 |
| `OPS-DEV` | DevOps 操作 | `01_policies_and_standards/operational/devops/` | v5.0.0 新增 |
| `OPS-MIG` | 迁移操作 | `01_policies_and_standards/operational/migration/` | v5.0.0 新增 |
| `DOM-L{XX}` | 层域治理 | `01_policies_and_standards/domains/L{XX}_*/` | v5.0.0 新增 |

#### 5.2.2 DOMAIN 命名规则

| 规则 | 说明 | 正确 | 错误 |
|------|------|------|------|
| 大写字母 + 连字符 | DOMAIN 部分用大写，层级用连字符分隔 | `GOV-SEC` | `gov-sec`, `GOV_SEC` |
| 层级编码 | 顶级域（PS/GOV/OPS/DOM）+ 子域缩写 | `GOV-SEC` | `SECURITY` |
| 子域缩写 2~4 字符 | 短到可读，长到无歧义 | `SEC`, `CMP`, `ARCH` | `SECURITY`, `COMPLIANCE` |
| 与物理目录一一对应 | 看到前缀就知道文件在哪 | `GOV-SEC` → `governance/security/` | 前缀和目录不对应 |

#### 5.2.3 顶级域层级关系

```
PS  ── meta/（元标准层，~10 文件，固定不增长）
 │
GOV ── governance/（全局治理层，~50 文件）
 │   ├── GOV-DOC  ── governance/document/
 │   ├── GOV-AI   ── governance/ai/
 │   ├── GOV-TASK ── governance/task/
 │   ├── GOV-SEC  ── governance/security/
 │   ├── GOV-CMP  ── governance/compliance/
 │   ├── GOV-ARCH ── governance/architecture/
 │   ├── GOV-DATA ── governance/data/
 │   └── GOV-MOD  ── governance/module/
 │
OPS ── operational/（全局操作层，~10 文件）
 │   ├── OPS-VC   ── operational/vibe_coding/
 │   ├── OPS-DEV  ── operational/devops/
 │   └── OPS-MIG  ── operational/migration/
 │
DOM ── domains/（层域治理，初始 4 层，按需扩展）
     ├── DOM-L00  ── domains/L00_data_source/
     ├── DOM-L02  ── domains/L02_alpha_factor/
     ├── DOM-L04  ── domains/L04_risk_management/
     └── DOM-L07  ── domains/L07_post_trade_analytics/
```

#### 5.2.4 新增 DOMAIN 的审批条件

| 条件 | 说明 |
|------|------|
| 对应目录已存在或即将创建 | 前缀不能凭空存在 |
| 缩写不与现有缩写冲突 | 检查 §5.2.1 DOMAIN 注册表 |
| 至少有 1 个文件需要该 DOMAIN | 不建空前缀 |
| 在本文件 §5.2.1 中注册 | DOMAIN 定义的唯一真源是本文件 |

#### 5.2.5 容量验证

| DOMAIN | 当前文件数 | experimental 目标 | 极限容量（NNN=999） | 够不够 |
|--------|:--------:|:----------:|:-----------------:|:-----:|
| PS-STD | 9 | 10 | 999 | ✅ |
| PS-REG | 1 | 2 | 999 | ✅ |
| GOV-DOC | 8 | 8 | 999 | ✅ |
| GOV-AI | 5 | 7 | 999 | ✅ |
| GOV-TASK | 3 | 3 | 999 | ✅ |
| GOV-SEC | 0 | 3 | 999 | ✅ |
| GOV-CMP | 0 | 2 | 999 | ✅ |
| GOV-ARCH | 2 | 3 | 999 | ✅ |
| GOV-DATA | 0 | 3 | 999 | ✅ |
| GOV-MOD | 7 | 7 | 999 | ✅ |
| OPS-VC | 3 | 5 | 999 | ✅ |
| OPS-DEV | 1 | 2 | 999 | ✅ |
| OPS-MIG | 1 | 1 | 999 | ✅ |
| DOM-L{XX}（每层） | 0~2 | 2~10 | 每层 999 | ✅ |

**总容量**：14 个 DOMAIN × 999 = 13986 个编号，远超峰值需求。如果某个 DOMAIN 超过 999，扩展为 NNNN（四位），格式不变。

### 5.3 TYPE 注册表

#### 5.3.1 已注册 TYPE（8 个）

| TYPE | 含义 | 示例 | 注册来源 |
|------|------|------|---------|
| `STD` | Standard（标准） | PS-STD-001 | v4.4.0 已注册 |
| `REG` | Registry（注册表） | PS-REG-001 | v4.4.0 已注册 |
| `ADR` | Architecture Decision Record | ADR-0010 | v4.4.0 已注册 |
| `DSG` | Design（设计） | EA-DSG-001 | v4.4.0 已注册 |
| `PLAN` | Plan（计划） | CP-PLAN-001 | v4.4.0 已注册 |
| `LOG` | Log（日志） | EA-LOG-001 | v4.4.0 已注册 |
| `POL` | Policy（策略/政策） | GOV-SEC-POL-001 | v5.0.0 新增 |
| `RBK` | Runbook（操作手册） | OPS-VC-RBK-001 | v5.0.0 新增 |

#### 5.3.2 TYPE 是否必填？

**不强制。** 当 DOMAIN 已经足够区分文件类型时，TYPE 可以省略。

| 场景 | 是否需要 TYPE | 示例 |
|------|:----------:|------|
| `meta/` 下的文件 | 需要（区分 STD 和 REG） | PS-STD-001, PS-REG-001 |
| `governance/` 下的文件 | **不需要**（GOV-SEC 已经足够定位） | GOV-SEC-001 |
| `operational/` 下的文件 | **不需要**（OPS-VC 已经足够定位） | OPS-VC-001 |
| `domains/` 下的文件 | **不需要**（DOM-L04 已经足够定位） | DOM-L04-001 |

**简化规则**：治理文件编号使用 `<DOMAIN>-<NNN>` 格式（省略 TYPE），只有 `meta/` 下的文件保留 `<DOMAIN>-<TYPE>-<NNN>` 格式。

### 5.4 编号分配铁律

| # | 铁律 | 说明 |
|---|------|------|
| 1 | **每个 DOMAIN 独立编号** | GOV-SEC-001 和 GOV-AI-001 是两个不同文件，互不冲突 |
| 2 | **连续分配** | 新文件取当前 DOMAIN 下最大编号 + 1 |
| 3 | **跳号保留，禁止回填** | 废弃编号标记为 skipped，永不回收 |
| 4 | **append-only** | 编号一旦分配，永不删除、不重编 |
| 5 | **迁移 = 重新编号** | 文件迁移到新目录时，module_id 必须按新 DOMAIN 重新分配 |
| 6 | **关联靠字段不靠编号** | 用 `superseded_by` / `refines` 表达关系，编号只承载唯一标识 |
| 7 | **禁止嵌套编号** | 不得创建 GOV-SEC-001-01 这种子编号 |
| 8 | **前缀长度 ≤12 字符** | 超长前缀可读性差 |

### 5.5 layer 字段格式

| 场景 | 格式 | 示例 |
|------|------|------|
| 业务层 | `l{xx}_{snake_case}` | `l00_data_source` `l04_ml_platform` |
| 跨层 | `cross_layer` | 治理标准、架构视图 |
| 基础设施 | `infra_{name}` | `infra_ci` `infra_precommit` |
| 前端 | `fe_l{n}` | `fe_l1` `fe_l2` |

### 5.6 module_id 与 L{XX} 层编号的关系

`unified-numbering-standard.md` 定义的 `L{XX}-{ABBR}-{NNN}` 格式用于**业务层模块**（L00-L13）。
本节定义的 `<DOMAIN>-<TYPE>-<NNN>` 格式用于**治理/标准/知识类文档**。

两者不冲突，通过 DOMAIN 区分：

| 场景 | 用哪个格式 | 示例 |
|------|----------|------|
| 业务层模块 | `L{XX}-{ABBR}-{NNN}` | `L00-DS-001` `L04-MLP-001` |
| 治理标准文档 | `PS-STD-{NNN}` | `PS-STD-001` |
| ADR | `ADR-{NNNN}` | `ADR-0002` `ADR-0010` |
| 知识条目 | `KE-{NNN}` | `KE-016` `KE-501` |
| 审计报告 | `AR-RPT-{NNN}` | `AR-RPT-001` |

### 5.7 废弃格式迁移说明

以下格式**全部废弃**，对应文件在施工 beta 统一改为新前缀：

| 废弃格式 | 文件 | 新 ID | 废弃原因 |
|---------|------|-------|---------|
| `STD-NUM-001` | unified-numbering-standard.md | GOV-DOC-001 | 不符合 `<DOMAIN>-<TYPE>-<NNN>` 格式；DOMAIN 应为 GOV-DOC |
| `STD-TASK-CARD-001` | task-card-standard.md | GOV-TASK-001 | 不符合格式；DOMAIN 应为 GOV-TASK |
| `PSP-DRAFTS-AUDITS-ARBITRATION-001` | drafts-audits-arbitration-protocol.md | GOV-DOC-011（2026-05-01 废除） | 超长前缀；不符合格式；文件已废除 |
| `PSP-AI-AUTONOMY-AUTHORITY-001` | ai-autonomy-authority-registry.md | GOV-AI-001 | 超长前缀；不符合格式 |
| `DW-HANDOFF-STD-001` | handoff-protocol.md | GOV-AI-008 | 不符合格式；DW 域用于开发工作区，不用于治理文件 |

**保留不动的格式**（已在项目中广泛引用）：

| 保留格式 | 文件 | 理由 |
|---------|------|------|
| `PS-STD-000` ~ `PS-STD-007` | meta/ 下 8 个文件 | 符合 `<DOMAIN>-<TYPE>-<NNN>` 格式；9 个文件广泛引用 |
| `PS-REG-001` | rule-registry.md | 符合格式 |
| `ADR-0001` ~ `ADR-0041` | ADR 文件 | ADR 已冻结，独立编号空间 |

### 5.8 完整编号分配表

> 以下为已分配的 module_id，按目录分组。"可用"槽位汇总在每段末尾。

| 目录 | 前缀 | 已分配编号 | 可用编号 |
|------|------|----------|---------|
| `meta/` | PS-STD | 000, 001, 002, 003, 004, 006, 009, 011, 012 | 005, 007, 008, 010 |
| `meta/` | META | GLS-001, IDX-001 | — |
| `meta/` | PS-REG | 001 | — |
| `governance/document/` | GOV-DOC | 001, 002, 003, 004, 005, 006, 007, 008, 009 | — |
| `governance/ai/` | GOV-AI | 001, 002, 003, 004, 005, 006, 007 | — |
| `governance/task/` | GOV-TASK | 001, 002, 003, 004, 005 | — |
| `governance/security/` | GOV-SEC | 001, 002, 003 | — |
| `governance/compliance/` | GOV-CMP | 001, 002 | — |
| `governance/architecture/` | GOV-ARCH | 001, 002, 003 | — |
| `governance/data/` | GOV-DATA | 001, 002, 003 | — |
| `governance/module/` | GOV-MOD | 001, 002, 003, 004, 005 | — |
| `operational/vibe_coding/` | OPS-VC | 001, 002, 003 | — |
| `operational/devops/` | OPS-DEV | 001 | — |
| `operational/migration/` | OPS-MIG | 001 | — |
| `domains/` | DOM-L## | L00-001~002, L02-001~002, L04-001~002, L07-001~002 | beta 扩展 |

> 详细文件对应用表见各目录的 `index.md`。

### 5.9 与 module-id-registry.yaml 的矛盾处理

`module-id-registry.yaml` 当前使用 `MOD-{LAYER_CODE}-{SEQ}` 格式，与本文件 §5.1 的 `<DOMAIN>-<TYPE>-<NNN>` 格式不一致。

**处理方案**：施工 stable 时将 module-id-registry.yaml 的格式对齐到本文件 §5.1，当前不处理（该注册表为空壳，无实际影响）。

---

## 6. ttl 受控词表

> **Canonical SSoT**：[`_registry/vocabularies/ttl-vocabulary.yaml`](../_registry/vocabularies/ttl-vocabulary.yaml)
>
> 以下仅列出速查。完整定义（definition、ai_behavior、retention_action 等）请查阅词汇表 YAML。

| ttl | 含义 |
|-----|------|
| `permanent` | 永久保留 |
| `30d` | 保留 30 天 |
| `7d` | 保留 7 天 |
| `session` | 仅当次会话有效 |
| `periodic_review_90d` | 定期审查（90 天周期） |

**AI 生成文件必须标注 ttl**。未标注 ttl 的 AI 生成文件，默认 `ttl: 7d`。

---

## 7. 域 B：任务卡字段（完整 SSoT）

> 任务卡是 AI 执行任务的最小单元。字段的**唯一真源**是本 §7，取代所有其他文件中的重复定义（包括原 `task-card-standard.md` §3 的字段定义——已于 2026-05-01 拆分，字段定义全部吸收至本节）。
>
> 代码真源：`src/zephyr/schemas.py` `TaskCard` 模型 + `src/zephyr/db/sqlite_schema.py` tasks 表
>
> 业务规则和操作指南（如何写任务卡正文、验收标准怎么写）见 `governance/task/task-card-standard.md`。

### 7.1 字段总表（快速索引）

> 以下为域 B 全部字段一览。各字段的详细格式规则、枚举约束、验真逻辑见 §§7.2~7.11。

| # | 字段 | 类型 | 必填 | 所属分组 | 说明 |
|---|------|------|:----:|---------|------|
| 1 | `task_id` | string | 是 | 标识 | 唯一标识，格式见 §7.10 |
| 2 | `namespace` | enum | 是 | 标识 | 7 命名空间之一，见 §9.3 |
| 3 | `seq` | int | 是 | 标识 | 命名空间内自增序号 |
| 4 | `title` | string | 是 | 标识 | 任务标题（1-200 字） |
| 5 | `status` | enum | 是 | 状态 | 10 状态机枚举值，见 §4.2 |
| 6 | `priority` | enum | 是 | 状态 | P0/P1/P2/P3/P4，见 §9.7 |
| 7 | `phase` | enum | 是 | 状态 | 施工阶段：`design` / `implement` / `verify` / `deploy` |
| 8 | `execution_model` | enum | 是 | 模型 | 主力模型，合法值见 §7.3 |
| 9 | `model_rationale` | string | 否 | 模型 | 选模型理由（1-3 句话） |
| 10 | `fallback_model` | enum | 否 | 模型 | 备选模型（主力不可用时） |
| 11 | `files_in_scope` | string[] | 否 | 路径 | 需读取的文件（绝对路径） |
| 12 | `deliverables` | string[] | 否 | 路径 | 产出的文件（绝对路径） |
| 13 | `depends_on` | string[] | 否 | 依赖 | 前置任务 task_id 列表 |
| 14 | `safety_level` | enum | 是 | 安全 | H/M/L，判定准则见 §10.10 |
| 15 | `classification` | enum | 是 | 安全 | public / confidential，见 §4.6 |
| 16 | `evolution_policy` | enum | 是 | 安全 | frozen / extendable / rewritable，见 §10.11 |
| 17 | `idempotent` | bool | 否 | 安全 | 任务是否可安全重试 |
| 18 | `directive` | string | 否 | 执行 | 执行指令编号（如 `313+325+999`） |
| 19 | `tags` | string[] | 否 | 执行 | 标签列表（kebab-case） |
| 20 | `acceptance` | string[] | 否 | 验收 | 量化验收指标列表 |
| 21 | `estimate_hours` | float | 否 | 工时 | 预估工时（小时） |
| 22 | `actual_hours` | float | 否 | 工时 | 实际工时（完成后填写） |
| 23 | `created_at` | datetime | 是 | 时间 | 创建时间 ISO 8601（系统自动） |
| 24 | `updated_at` | datetime | 是 | 时间 | 更新时间 ISO 8601（系统自动） |
| 25 | `completed_at` | datetime | 否 | 时间 | 完成时间 ISO 8601（系统自动） |
| 26 | `session_id` | string | 否 | 运行时 | 关联 session UUID（系统自动） |
| 27 | `waiting_for` | string | 否 | 运行时 | WAITING 时等待的条件 |
| 28 | `ready_at` | datetime | 否 | 运行时 | READY 触发时间 ISO 8601（系统自动） |

### 7.2 核心标识字段

| 字段 | 格式规则 | 说明 |
|------|---------|------|
| `task_id` | `{NAMESPACE}-{SEQ}` | 如 `ADR-001`、`SRC-042`。格式规则见 §7.10 |
| `namespace` | 7 命名空间枚举值之一（§9.3） | task_id 前缀，控制命名空间内自增 |
| `seq` | int ≥ 1 | 命名空间内自增序号，由 `task_repo.py` `next_seq(namespace)` 自动分配 |
| `title` | 1-200 字 | 一眼看懂干什么（对齐 Jira Summary / Linear Title） |
| `status` | TaskStatus 10 值之一（§4.2） | PENDING / IN_PROGRESS / COMPLETED / VERIFIED / FAILED / BLOCKED / WAITING / READY / RETRY / CANCELLED |
| `priority` | P0 / P1 / P2 / P3 / P4（§9.7） | P0=关键阻塞，P1=重要近期，P2=一般计划，P3=低优先，P4=可选 |
| `phase` | `design` / `implement` / `verify` / `deploy` | 任务所处的施工阶段，非项目 Phase 编号 |
| `directive` | 自由文本 | 执行指令编号，如 `313+325+999` |

### 7.3 模型执行字段

| 字段 | 格式规则 | 说明 |
|------|---------|------|
| `execution_model` | 模型枚举值之一（见下表） | 执行本任务的主力模型 |
| `model_rationale` | 1-3 句话 | 为什么选这个模型（**强建议填写，防止 AI 乱选贵模型**） |
| `fallback_model` | 模型枚举值之一 | 主力不可用时的备选。切换后必须在 execution_log 记录 |

**模型枚举值**：

| 值 | 擅长场景 | 费用 |
|---|---------|------|
| `claude-opus-4.7` | 复杂多文件联动、架构级决策 | 贵 |
| `claude-sonnet-4.6` | 核心代码编写、代码复查 | 便宜 |
| `glm-5.1` | 讨论、基础工作、批量化工作 | 免费 |
| `kimi` | 长文分析、知识提取 | 免费 |
| `any` | 不挑模型，谁空谁干 | — |

**model_rationale 质量判据**：

| 质量 | 示例 |
|:----:|------|
| ✅ Good | `Sonnet 擅长结构化代码编写且便宜，本任务涉及 3 个文件修改，无需 Opus 架构推理` |
| ❌ Bad | `Sonnet 够了`（无分析）、`因为便宜`（没说便宜够用）、`Owner 选的`（推责任） |

**默认规则**：优先使用免费/便宜模型，只有任务卡明确标注 `claude-opus-4.7` 时才使用贵模型。

> 对标 IETF AAT：`execution_model` = `model_id`，`author_agent`（域 A） = `agent_id`。两者不可合并——`author_agent` 回答"在哪个编辑器写的"，`execution_model` 回答"用哪个模型干的"，详见 §10.5。

### 7.4 路径字段（防漂移核心）

| 字段 | 格式规则 |
|------|---------|
| `files_in_scope` | **绝对路径**列表——本任务需读取的所有文件 |
| `deliverables` | **绝对路径**列表——本任务产出的所有文件 |

**路径铁律**：

| # | 规则 |
|---|------|
| 1 | 必须使用绝对路径（如 `D:\ZephyrAlpha\src\...`），禁止相对路径 |
| 2 | 必须列出所有相关文件——AI 不会猜，漏一个就可能找不到 |
| 3 | 路径必须以 `D:\ZephyrAlpha\` 开头 |
| 4 | deliverables 与 files_in_scope 不能完全重叠（除非原地修改） |

**AI 确定 files_in_scope 的规则**：

| 文件类型 | 是否放入 | 判据 |
|---------|:------:|------|
| 本任务需修改的文件 | ✅ | 直接读写 |
| 需理解接口/结构的只读文件 | ✅ | schemas.py / contracts/ |
| 同目录相邻但不需要改的 | ❌ | 除非联动修改 |
| 下游消费者的文件 | ❌ | 不修改就不放 |

> **N:N 映射**：任务与文件是多对多关系。`files_in_scope` 和 `deliverables` 是任务卡层面的快捷引用，完整 N:N 映射存储在 `task_files` 表中。

### 7.5 依赖字段

| 字段 | 格式规则 | 说明 |
|------|---------|------|
| `depends_on` | task_id 列表 | 前置任务，必须全部 VERIFIED 才能开始 |

**依赖验真规则**：

| 场景 | 行为 |
|------|------|
| depends_on 所有 task_id 均存在且终态 | ✅ 允许开始 |
| depends_on 中有 task_id 不存在 | ❌ G0 阻止创建 |
| depends_on 中有 task_id 非终态 | ⚠️ 可创建，状态自动 = PENDING |
| depends_on = `[]` 或字段缺失 | ✅ 无前置约束 |

> 对标 Jira Blocks / Azure DevOps Dependencies。

### 7.6 安全与演进字段

| 字段 | 类型 | 必填 | 合法值 | 说明 |
|------|------|:----:|--------|------|
| `safety_level` | enum | 是 | H / M / L | H=高风险（架构/风控），M=中风险（代码修改），L=低风险（文档/测试）。判定准则见 §10.10 |
| `classification` | enum | 是 | public / confidential | 访问分类，见 §4.6 |
| `evolution_policy` | enum | 是 | frozen / extendable / rewritable | 文件演进策略，见 §10.11 |
| `idempotent` | bool | 否 | true / false | true=重试不产生副作用；false 时必须解释原因 |

**safety_level 判定准则**：

| 条件 | → level |
|------|:------:|
| 涉及 `src/zephyr/db/` schema 变更 | H |
| 涉及 `docs/01_policies_and_standards/` 治理标准 | H |
| 涉及数据库文件读写（非 schema） | M |
| 涉及多个 `.py` 文件联动（非 DB 非治理） | M |
| 纯文档：README / ADR / 探索笔记 | L |
| 单文件修改、无跨文件副作用 | L |
| 不确定时 | M（默认保守） |

> **与 `ai_autonomy`（域 A）的关系**：`ai_autonomy` 管"AI 能不能动文件"，`safety_level` 管"动了之后有多危险"。两者独立判断，取更严。

### 7.7 工时与时间字段

| 字段 | 类型 | 必填 | 格式 | 说明 |
|------|------|:----:|------|------|
| `estimate_hours` | float | 否 | ≥ 0 | 预估工时（对齐 Jira Story Points） |
| `actual_hours` | float | 否 | ≥ 0 | 实际工时（完成后填写，对齐 Jira Time Spent） |
| `created_at` | datetime | 是 | ISO 8601 | 创建时间（系统自动填充） |
| `updated_at` | datetime | 是 | ISO 8601 | 最近更新时间（系统自动填充） |
| `completed_at` | datetime | 否 | ISO 8601 | 完成时间（系统自动填充，对齐 Jira Resolution Date） |

### 7.8 运行时字段（系统自动管理）

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `session_id` | string | 否 | 关联 session UUID（系统自动填充） |
| `waiting_for` | string | 否 | WAITING 状态时等待的资源/事件 |
| `ready_at` | datetime | 否 | READY 触发时间 ISO 8601（系统自动填充） |

### 7.9 标签与验收字段

| 字段 | 类型 | 必填 | 格式规则 | 说明 |
|------|------|:----:|---------|------|
| `tags` | string[] | 否 | kebab-case 全小写 | `{前缀}:{值}` 或裸标签。如 `wave0-arbitrated`、``、`origin:b5-s2.1` |
| `acceptance` | string[] | 否 | 量化验收指标 | 如 `CRUD 全覆盖`、`10 状态机转换全部实现`。建议用共享度量标签（coverage/build/lint/files/diff） |

### 7.10 task_id 格式与命名空间规则

```
{NAMESPACE}-{SEQ}
```

| 命名空间 | 含义 | 文件路径模式 | 示例 |
|---------|------|------------|------|
| `ADR` | 架构决策记录 | `docs/02_enterprise_architecture/adr/adr-*` | ADR-001 |
| `MOD` | 模块文档 | `docs/03_modules/l<NN>_<layer>/<module>/` | MOD-001 |
| `KE` | 知识条目 | `docs/08_knowledge/` | KE-003 |
| `STD` | 标准/规范 | `docs/01_policies_and_standards/` | STD-001 |
| `DW` | ~~开发工作区~~ 已删除 | `—` | `19_development_workspace/` 已于 2026-05-02 删除 |
| `SRC` | 源代码 | `src/zephyr/` | SRC-007 |
| `OPS` | 运维/其他 | 不属于以上分类的 | OPS-001 |

**自增规则**：每个命名空间内序号独立递增，由 `task_repo.py` `next_seq(namespace)` 自动分配。

**已废弃的旧 task_id 格式**：

| 旧前缀 | 替代 | 迁移方式 |
|--------|------|---------|
| `T-0-*` ~ `T-4-*` | 按 namespace 重新分配 | 迁移时自动分类 |
| `T-V2-*` | 按 namespace 重新分配 | 迁移时自动分类 |
| `T-KE-*` | `KE-{SEQ}` | 去 T- 前缀 |
| `T-ADR-*` | `ADR-{SEQ}` | 去 T- 前缀 |
| `T-CP-*` | `CP-{SEQ}` | 去 T- 前缀 |
| `T-SCRIPT-*` | `SRC-{SEQ}` | 归入 SRC |
| `T-UNCLASSIFIED-*` | `OPS-{SEQ}` | 归入 OPS |

### 7.11 已废弃字段（域 B 层面）

> 以下字段在任务卡层面已废弃。其替代方案和废弃原因记录于此，供迁移参考。

| 废弃字段 | 废弃原因 | 替代方案 |
|---------|---------|---------|
| `predecessor` | 与 `depends_on` 功能重复 | 使用 `depends_on` |
| `model_preference` | 与 `execution_model` 功能重复 | 直接按 `execution_model` 分组 |
| `ai_autonomy`（任务卡中） | 可由 `classification` + `safety_level` 组合推导 | H+confidential → Human-Gated，其余 → AI-Modifiable |
| `provenance.origin` / `provenance.rationale_log` | 结构化字段过重 | 放入 `tags`（如 `origin:b5-s2.1`） |
| `owner` | 固定值 `ZephyrAlpha-Owner`，无信息量 | 系统默认 |
| `version`（任务卡中） | 任务卡版本由 git 管理 | 不需要字段 |
| `layer`（任务卡中） | 可从 `namespace` 推导 | 不需要字段 |
| `est_hours` | 字段名不规范 | → `estimate_hours` |
| `created` | 字段名不规范 | → `created_at` |

### 7.12 与域 A frontmatter 的关系

任务卡字段**不是**文档 frontmatter 字段。它们存储在 SQLite `tasks` 表中，通过 `task_id` 关联。

域 A 中的同名字段（`execution_model`、`safety_level`、`classification`、`evolution_policy`）与域 B 是**同一概念的不同上下文**：
- 域 A 用于**文档溯源**——"这个文档是什么安全等级、用什么模型写的"
- 域 B 用于**任务执行**——"这个任务该用什么模型做、多危险"

两者通过 `task_id` 关联，字段值应保持一致（如有差异必须解释原因）。

---

## 8. 域 C：AI 治理字段

> AI 治理字段分散在三个位置：文档 frontmatter（域 A 子集）、AI 决策日志、AI 员工档案。
> 本节是域 C 字段的交叉引用索引，详细定义见对应章节。

### 8.1 域 C 字段分布

| 位置 | 字段数 | 存储方式 | 真源 |
|------|:------:|---------|------|
| 文档 frontmatter（域 A 子集） | 7 | YAML frontmatter | 本文件 §10 |
| AI 决策日志 | 28+2 | JSONL 文件 | `ai-autonomous-company-endgame-design.md` §2.6 |
| AI 员工档案 | 30+ | YAML 文件 | `ai-autonomous-company-endgame-design.md` §4 |

### 8.2 域 A 中的 AI 治理字段（7 个）

| 字段 | 说明 | 详见 |
|------|------|------|
| `ai_autonomy` | AI 自治权限等级 | §10.1 |
| `author_agent` | 创作代理（谁写的这个文档） | §10.5 |
| `governance_family` | 治理系统家族 A/B/C/D | §10.7 |
| `ai_capability_slot` | AI 员工接入点状态 | §10.7 |
| `ai_autonomy_level_planned` | 规划的 AI 自治等级 | §10.7 |
| `ai_employee_count_planned` | 规划的 AI 员工数量 | §10.7 |
| `provenance` | 溯源信息 | §10.3 |

### 8.3 provenance 双定义澄清

项目中 `provenance` 一词在两个上下文中使用，语义不同：

| 上下文 | 名称 | 语义 | 位置 | 格式 |
|--------|------|------|------|------|
| 文档溯源 | **`provenance`** | 文档的来源、审计链、裁决记录 | frontmatter YAML | 复杂对象（origin_drafts / audit_chain / arbitration） |
| 运行时写入溯源 | **`WriteTrace`** | 代码运行时每次写入操作的溯源 | Python 代码 `WriteTrace(BaseModel)` | 简单对象（writer_id / timestamp / operation / target） |

**为什么用两个词**：
- `provenance` 是行业术语（OpenLineage、W3C PROV 都用这个词），指文档/数据的来源和演变历史
- `WriteTrace` 是代码运行时的写入溯源，关注的是"谁在什么时候对什么做了什么操作"
- 两者粒度不同：provenance 是文档级（整个文件），WriteTrace 是操作级（单次写入）
- 代码中 `Provenance` 类已改名为 `WriteTrace`，避免与 frontmatter `provenance` 混淆

---

## 9. 受控枚举定义

> 本节定义跨域使用的枚举值。每个枚举有唯一的代码真源。

### 9.1 category 枚举（10 值）

> 语义：知识条目的内容类型——"这是什么类型的知识"。
> 与 `domain`（§9.2）是两个独立维度：category 管"是什么类型"，domain 管"属于哪个领域"。

| # | category | 含义 | 对标 KMS |
|---|----------|------|---------|
| 1 | `blueprint_decision` | 蓝图设计决策（模块级） | — |
| 2 | `strategy` | 交易策略（买卖信号、仓位管理） | domain:strategy |
| 3 | `factor` | 因子设计（alpha因子、风险因子） | domain:factor |
| 4 | `best_practice` | 最佳实践（验证过的做法） | knowledge_type:practice |
| 5 | `lesson_learned` | 教训记录（踩过的坑、故障复盘） | knowledge_type:lesson |
| 6 | `architecture` | 架构决策（系统级，区别于蓝图决策的模块级） | domain:infrastructure |
| 7 | `risk_control` | 风控知识（风控规则、风险度量、熔断机制） | domain:risk |
| 8 | `data_governance` | 数据治理（数据源、数据质量、数据血缘） | domain:data |
| 9 | `operations` | 运维知识（部署、监控、故障处理、CI/CD） | — |
| 10 | `compliance` | 合规知识（法规要求、审计标准、监管报告） | — |

**代码真源**：`src/zephyr/mcp/knowledge_base_server.py` `_VALID_CATEGORIES`（需同步扩展）

### 9.2 domain 枚举（10 值）

> 语义：知识条目所属的业务领域——"属于哪个领域"。
> 与 `category`（§9.1）是两个独立维度。

| # | domain | 含义 | 对应 layer |
|---|--------|------|-----------|
| D0 | `data` | 数据域 | l00 / l01 |
| D1 | `feature` | 特征域 | l02 |
| D2 | `model` | 模型域 | l03 / l04 |
| D3 | `signal` | 信号域 | l05 |
| D4 | `execution` | 执行域 | l06 |
| D5 | `risk` | 风控域 | l07 |
| D6 | `portfolio` | 组合域 | l08 |
| D7 | `reporting` | 报告域 | l09 |
| D8 | `infrastructure` | 基础设施域 | cross_layer |
| D9 | `other` | 其他 | — |

**代码真源**：`docs/08_knowledge/kms-entry-schema.md` `domain` 字段（需同步扩展）

### 9.3 namespace 枚举（7 值）

> 语义：任务卡的命名空间——任务属于哪个工作流。

| namespace | 含义 | 对应目录 |
|-----------|------|---------|
| `ADR` | 架构决策记录 | `02_enterprise_architecture/adr/` |
| `MOD` | 模块文档 | `03_modules/l<NN>_<layer>/<module>/` |
| `KE` | 知识条目 | `08_knowledge/` |
| `STD` | 标准 | `01_policies_and_standards/` |
| `DW` | ~~开发工作区~~ 已删除 | `—` |
| `SRC` | 源码 | `src/zephyr/` |
| `OPS` | 运维 | scripts/ |

**代码真源**：`src/zephyr/schemas.py` `TaskNamespace` 枚举

### 9.4 AgentRole 枚举（6 值）

> 语义：AI 员工的角色——负责什么类型的工作。

| role | 含义 | 典型任务 |
|------|------|---------|
| `architect` | 架构师 | 架构决策、模块边界、接口设计 |
| `implementer` | 实施者 | 代码编写、测试实现 |
| `reviewer` | 复核者 | 代码审查、文档审阅 |
| `governor` | 治理官 | 标准制定、合规检查 |
| `researcher` | 研究员 | 文献调研、竞品分析 |
| `operator` | 运营员 | 部署、监控、故障处理 |

**代码真源**：`src/zephyr/orchestrator/agent_orchestrator.py` `AgentRole` 枚举

### 9.5 layer 枚举（14 值）

> 语义：文档/模块所属的架构层——"属于系统的哪一层"。
> 与 `domain`（§9.2）是关联维度：domain 是业务领域（D0-D9），layer 是架构分层（l00-l13）。
> 一个 layer 可能对应多个 domain，一个 domain 也可能跨越多个 layer。

| # | layer | 含义 | 对应 domain |
|---|-------|------|------------|
| 1 | `l00_data_source` | 数据源层 | D0 data |
| 2 | `l01_data_processing` | 数据处理层 | D0 data |
| 3 | `l02_alpha_factor` | Alpha 因子层 | D1 feature |
| 4 | `l03_signal_generation` | 信号生成层 | D3 signal |
| 5 | `l04_ml_platform` | 机器学习平台层 | D2 model |
| 6 | `l05_portfolio_construction` | 组合构建层 | D6 portfolio |
| 7 | `l06_trade_execution` | 交易执行层 | D4 execution |
| 8 | `l07_risk_management` | 风险管理层 | D5 risk |
| 9 | `l08_post_trade_analytics` | 盘后分析层 | D7 reporting |
| 10 | `l09_research_innovation` | 研究创新层 | D9 other |
| 11 | `l10_compliance` | 合规层 | D9 other |
| 12 | `l11_human_ai_interface` | 人机交互层 | D8 infrastructure |
| 13 | `shared` | 共享组件 | D8 infrastructure |
| 14 | `cross_layer` | 跨层 | D8 infrastructure |

**代码真源**：`src/zephyr/kb/triage.py` `VALID_LAYERS`（需同步对齐）

### 9.6 source_type 枚举（7 值）

> 语义：知识条目的来源类型——"这条知识从哪里来"。
> 与 `category`（§9.1）是关联维度：category 管"是什么类型"，source_type 管"从哪来的"。

| # | source_type | 含义 | 典型场景 |
|---|------------|------|---------|
| 1 | `paper` | 学术论文 | 从 arXiv/期刊提取的策略/因子 |
| 2 | `opensource` | 开源项目 | 从 GitHub 项目提取的实现方案 |
| 3 | `blueprint` | 项目蓝图 | 从本项目的蓝图文档提取的设计决策 |
| 4 | `report` | 行业研究报告 | 从券商/咨询报告提取的行业洞察 |
| 5 | `practice` | 最佳实践文章 | 从博客/演讲/教程提取的实践方法 |
| 6 | `operation` | 运营经验 | 从实际运维中积累的经验 |
| 7 | `lesson` | 教训（失败案例） | 从故障/踩坑中提炼的教训 |

**代码真源**：`docs/08_knowledge/kms-entry-schema.md` `source_type` 字段

### 9.7 priority 枚举（5 值）

> 语义：优先级/严重度——"多重要/多紧急"。
> 统一了项目中原有的三套优先级定义：AuditSeverity（P0-P2）、模块 priority（P0-P3）、
> activation_priority（P0-P4）。统一为 5 级，覆盖所有场景。

| # | priority | 含义 | 适用场景 |
|---|----------|------|---------|
| 1 | `P0` | 关键/紧急——必须立即处理，阻塞其他工作 | 生产故障、安全漏洞、核心功能缺失 |
| 2 | `P1` | 重要——近期必须完成，影响核心功能 | 重要功能、关键设计决策 |
| 3 | `P2` | 一般——计划内工作，不影响核心功能 | 增强功能、优化改进 |
| 4 | `P3` | 低优先——有空再做 | 可选功能、锦上添花 |
| 5 | `P4` | 可选——不确定是否需要 | 探索性想法、远期规划 |

**代码真源**：`src/zephyr/schemas.py` `AuditSeverity` 枚举（需扩展为 P0-P4 并重命名为 `Priority`）

---

## 10. AI 员工与治理字段

### 10.1 ai_autonomy 字段

标注该文档的 AI 自治权限等级，与 `ai-autonomy-authority-registry.md` 三层模型对齐。

| 值 | 含义 | AI 员工行为 |
|----|------|-----------|
| `immutable_core` | 系统宪法层 | **禁止 AI 自主修改**，需 Owner 直接审批 + ADR 记录 |
| `human_gated` | 人控闸门层 | AI 可提修改提案，**Owner 审批后方可执行** |
| `ai_modifiable` | AI 可改层 | AI 可自主修改，**每次修改写入 Provenance Chain** |

**默认值**：治理标准文档 = `immutable_core`；蓝图/施工图 = `human_gated`；日志/标签 = `ai_modifiable`。

### 10.2 created_by 字段

| 值 | 含义 |
|----|------|
| `human` | 人类创建 |
| `agent` | AI 员工创建 |
| `human_plus_agent` | 人机协作创建 |

### 10.3 provenance 溯源块

```yaml
provenance:
  origin_drafts:          # 草稿来源
    - path: "原始草稿路径"
      model: "创建该草稿的 AI 模型"
  audit_chain:            # 审计链
    - auditor: "审计者"
      date: "YYYY-MM-DD"
      verdict: "pass|fail|conditional"
  arbitration:            # 裁决记录
    arbiter: "裁决者"
    date: "YYYY-MM-DD"
    decision: "裁决结论"
```

### 10.4 AI 员工在文档操作中的约束

1. **创建文档**：必须填写 Draft 阶段全部 7 个必填字段
2. **修改 `immutable_core` 文档**：必须先提 ADR，Owner 审批后方可修改
3. **修改 `human_gated` 文档**：必须走 `request_change()` → `approve_change()` 流程
4. **修改 `ai_modifiable` 文档**：可自主修改，但必须在 commit message 中包含 `agent_id` 和 `session_id`
5. **删除文档**：无论何种权限等级，AI 员工**禁止自主删除**文档，必须 Owner 审批
6. **AI 生成文件**：frontmatter 必须包含 `created_by: agent` 和 `ttl` 字段

### 10.5 模型选择字段（域 A + 域 B）

标注与该文档/任务相关的 AI 模型信息。`author_agent` 和 `execution_model` 是两个独立字段，语义不同，不可合并：

| 字段 | 域 | 语义 | 值的格式 | 适用场景 | 对标专业机构 |
|------|---|------|---------|---------|------------|
| `author_agent` | A | 创作代理——谁写的这个文档 | 编辑器/产品名：`Cursor-Premium` / `Trae-Free` / `Kimi-1M` / `Claude-API` | 所有文档 | **IETF: agent_id** |
| `execution_model` | B | 执行模型——计划用什么模型完成这个任务 | 底层模型名：`claude-opus-4.7` / `claude-sonnet-4.6` / `glm-5.1` / `kimi` / `any` | 任务卡 | **IETF: model_id** |
| `model_rationale` | B | 选模型理由 | 自由文本（1-3 句话） | 任务卡（建议填写） | — |
| `fallback_model` | B | 降级模型 | 同 `execution_model` | 任务卡（可选） | — |

**为什么不能合并**：
- `author_agent` 回答"谁写的"——关注**溯源审计**（这个文档是哪个编辑器/AI 产生的）
- `execution_model` 回答"谁干活"——关注**执行能力**（模型能不能完成这个任务）
- 两者维度不同：一个任务可能由 `claude-sonnet-4.6` 执行（execution_model），但在 `Trae-Free` 编辑器中完成（author_agent）
- 专业机构（IETF AAT、OpenLineage、MLflow）100% 拆开这两个维度，没有例外

**模型选择策略**（与 `model-capability-contract.yaml` 对齐）：

| 模型 | 适合的任务类型 | 不适合的任务类型 |
|------|-------------|---------------|
| `claude-opus-4.7` | 关键架构决策、终审裁决、复杂推理 | 机械批量操作 |
| `claude-sonnet-4.6` | 中等复杂度任务、代码实现、文档编写 | 关键架构决策 |
| `glm-5.1` | 机械任务、批量文件操作、流水线执行 | 复杂推理、长上下文 |
| `kimi` | 长文档阅读、历史挖掘、中文理解 | 代码实现 |
| `any` | 无模型偏好 | — |

### 10.6 Session Log 正文字段

Session log（`doc_type: log` 且用于 AI session 记录时）的正文包含以下字段。**这些是正文内容，不是 frontmatter 字段**——只有 session log 才需要写这些，其他文档不需要。

| 字段 | 类型 | 说明 |
|------|------|------|
| `context_budget_used` | string | 本次 session 消耗的上下文预算估计（如"约 50k tokens，读取了 8 个文件"） |
| `knowledge_extracted` | int | 本次 session 提取的知识条目数量（汇总计数） |
| `construction_deviations` | list_of_objects | 施工偏差明细列表（每条含 deviation_type / blueprint_ref / description / recommended_action） |
| `next_session_handover` | object | 交接给下一个 session 的信息，含 `next_task` / `blockers` / `context_needed` / `warnings` |

**大白话解释**：
- `context_budget_used`：这次干活花了多少"脑力"——AI 的上下文窗口是有限的，记录用了多少，方便下次估算
- `knowledge_extracted`：这次干活过程中，从旧文件里提炼出了几条知识（对应 `08_knowledge/` 下的 KE 条目数）。这是**汇总计数**，只记一个数字
- `construction_deviations`：施工中发现了哪些偏差，每条偏差怎么处理。这是**明细列表**，和 `knowledge_extracted` 互补而非替代。打个比方：`knowledge_extracted` 是"今天赚了 500 块"，`construction_deviations` 是"今天修了 3 个 bug，其中 2 个值得记录"
  - `deviation_type`（偏差类型）：`blueprint_defect`（蓝图设计有缺陷）/ `tech_choice_infeasible`（技术选型不可行）/ `interface_change`（接口变更）/ `scope_change`（范围变更）
  - `blueprint_ref`（来源蓝图路径）：必须写完整物理路径，不来自蓝图时写 N/A
  - `description`（具体描述）：发现了什么问题、为什么是偏差
  - `recommended_action`（建议动作）：`extract_ke`（提取 KE）/ `update_decision_record`（更新决策记录，参见 MOD-KB-001 §3.9.5）/ `modify_blueprint`（修改蓝图）/ `record_only`（仅记录）
- `next_session_handover`：交接班信息——下一个 AI 接手时需要知道：下一个任务是什么、有什么卡住的、需要先读哪些文件、有什么坑要注意

**字段间关系**：
- `knowledge_extracted` 与 `construction_deviations`：计数 vs 明细。`construction_deviations` 中 `recommended_action` 为 `extract_ke` 的条目数应 ≤ `knowledge_extracted` 的值（不是所有 KE 都来自施工偏差）
- `construction_deviations` 与施工图 §9.7：session 级 vs 文档级。一个 session 可能涉及多份施工图，两个层面各记各的，不冲突

来源：`session-log-schema.yaml`

### 10.7 治理系统 AI 预留字段（39 系统专用）

来自 AC-2 决议（`ai-autonomous-company-endgame-design.md` §4.2），为 39 个治理系统预留的 AI 员工规划字段：

| 字段 | 类型 | 合法值 | 说明 |
|------|------|--------|------|
| `governance_family` | string | `A` / `B` / `C` / `D` | 治理系统所属家族：A=机构标配，B=元治理，C=氛围独有，D=共享底座 |
| `ai_capability_slot` | enum | `planned` / `reserved` / `active` / `none` | AI 员工接入点状态：planned=已规划，reserved=已预留，active=已激活，none=无 |
| `ai_autonomy_level_planned` | enum | `l0` / `l1` / `l2` / `l3` | 规划的 AI 自治等级：L0=AI 自决，L1=自决+事后通知，L2=AI 提案+人批准，L3=人独占 |
| `ai_employee_count_planned` | int | 0-10 | 该系统计划接入的 AI 员工数量 |

**当前预填结果**（来自 ai-autonomous-company-endgame-design.md）：
- `ai_capability_slot`: 10 planned + 16 reserved + 13 none
- AI 员工规划总数：**31 个**

### 10.8 三层口子预留（代码/文档/前端各 3 项）

来自 OQ-063 决议（`ai-autonomous-company-endgame-design.md` §4.9），为 AI 员工在代码层/文档层/前端层预留接入点。**这些是路径/目录预留，不是 frontmatter 字段**——定义的是"哪里给 AI 员工留了位置"，不是"文档头部填什么"。

| 层 | 编号 | 预留路径 | 用途 |
|---|------|---------|------|
| 代码 | C-1 | `src/zephyr/layers/{L}/_ai_operator/` | 每层预留 AI Operator 命名空间 |
| 代码 | C-2 | `src/zephyr/shared/contracts/ai_operator_contract.py` | AI Operator 接口协议占位 |
| 代码 | C-3 | `src/zephyr/shared/immutable_core/` | 纳入 AI 决策日志 schema |
| 文档 | D-1 | `META_GOVERNANCE/ai_authored_docs/` | AI 生成文档归档 |
| 文档 | D-2 | `META_GOVERNANCE/ai_operators_registry.md` | 全公司 AI 员工花名册 |
| 文档 | D-3 | `META_GOVERNANCE/ai_operators/b01_operators/` | B01 元治理 Operator 归属 |
| 前端 | F-1 | `frontend/src/modules/ai_ops/` | AI 操作前端命名空间 |
| 前端 | F-2 | `frontend/src/routes/` | 路由前缀 `/ai-ops/*` |
| 前端 | F-3 | `frontend/src/api/ai_operator_client.ts` | AI Operator API 客户端契约 |

**合计**：AC-2 四列字段 + 三层口子 9 项 = **13 项 AI 预留**

### 10.9 AI 决策日志（独立 schema，非 frontmatter）

AI 决策日志（`logs/ai/{employee_id}/YYYY-MM-DD.jsonl`）有自己的独立 JSON schema，包含 28+ 字段（`decision_id` / `employee_id` / `trigger` / `context` / `reasoning` / `decision` / `outcome` / `audit` / `employee_state` 等）。

**这些字段不属于文档 frontmatter**，不纳入本标准 §2 字段表。AI 决策日志 schema 的真源是 `ai-autonomous-company-endgame-design.md` §2.6。

### 10.10 safety_level 字段

标注文档/任务的安全风险等级，决定 AI 操作的防护策略。与 `task-card-standard.md` §3.5 和 `schemas.py` `SafetyLevel` 枚举对齐。

| 值 | 含义 | AI 行为约束 |
|----|------|-----------|
| `H` | 高风险——架构决策、风控配置 | CoVe 幻觉检测强制触发；修改必须 Owner 审批；Gate 门禁一票否决 |
| `M` | 中风险——代码修改、业务逻辑 | CoVe 条件触发；修改需走 human_gated 流程 |
| `L` | 低风险——文档、测试、日志 | CoVe 仅黑名单触发；AI 可自主修改（ai_modifiable 范围内） |

**与 `ai_autonomy` 的关系**：`ai_autonomy` 管"AI 能不能动"，`safety_level` 管"动了之后有多危险"。两者独立判断，取更严格的结果。

### 10.11 evolution_policy 字段

标注文件本身的演进策略——允不允许被改、怎么改。与 `schemas.py` `EvolutionPolicy` 枚举和 ADR-0040 对齐。

| 值 | 含义 | AI 行为约束 |
|----|------|-----------|
| `frozen` | 冻结——任何修改都不允许 | AI 禁止修改；提议修改自动触发 CoVe 强制检测 |
| `extendable` | 可追加——可在末尾加新内容，不能改旧内容 | AI 可追加条目（如注册表新增行），但不可改写已有行 |
| `rewritable` | 可重写——可完全修改 | AI 可自主修改（在 ai_autonomy 和 safety_level 约束范围内） |

**默认值**：`extendable`。ADR 和已发布的标准默认 `frozen`。

**与 `ai_autonomy` 的关系**：`ai_autonomy` 管"AI 有没有权限"，`evolution_policy` 管"文件本身允不允许"。即使 AI 有 `ai_modifiable` 权限，`frozen` 文件也不可改。

### 10.12 blueprint_refs 字段

> **2026-05-02 更新**：`construction_plan` 作为独立 doc_type 已于 2026-05-02 合并入 `blueprint`（§12 施工指引）。新模块不再创建独立的施工图文件。以下规则仅对历史 `doc_type: construction_plan` 文档保留适用。

施工图（`doc_type: construction_plan`）必须标注引用的蓝图列表，确保施工图与蓝图的一致性可自动验证。

```yaml
blueprint_refs:
  - path: "docs/03_modules/l00_data_source/<module>/blueprint.md"
    status: active
    decisions_used: ["BD-001", "BD-003"]
  - path: "03_modules/l04_risk_management/<module>/blueprint.md"
    status: draft
    decisions_used: ["BD-012"]
```

| 子字段 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `path` | string | 是 | 蓝图文件路径 |
| `status` | string | 是 | 蓝图当前状态（`active` / `draft` / `deprecated`） |
| `decisions_used` | string[] | 否 | 本施工图使用了该蓝图的哪些决策编号 |

**pre-commit 校验规则**：
- `doc_type: construction_plan` 的文件必须包含 `blueprint_refs`
- `blueprint_refs` 中引用的蓝图路径必须存在
- 若引用的蓝图 `status` 不是 `active`，发出 P1 警告
- 若引用的蓝图 `status` 为 `deprecated`，发出 P0 阻断

### 10.13 compliance_tags 字段

标注文档涉及的合规要求。对标 EU AI Act Article 12 合规文档要求。

```yaml
compliance_tags:
  - SR-11-7
  - EU-AI-Act-Art12
  - GDPR-Art22
```

| 合法值 | 含义 | 适用场景 |
|--------|------|---------|
| `SR-11-7` | 美联储模型风险管理 | 涉及模型/算法的文档 |
| `EU-AI-Act-Art12` | EU AI 法案第 12 条日志要求 | 高风险 AI 系统文档 |
| `EU-AI-Act-Art14` | EU AI 法案第 14 条人工监督 | 需要人工监督的 AI 决策 |
| `GDPR-Art22` | GDPR 第 22 条自动化决策 | 涉及用户数据的文档 |
| `PCI-DSS` | 支付卡行业数据安全标准 | 涉及支付数据的文档 |
| `MiFID-II` | 欧盟金融工具市场指令 | 涉及交易执行的文档 |

**pre-commit 校验规则**：`safety_level: H` 的文件建议至少包含一个 `compliance_tags` 条目（P2 警告）。

### 10.14 human_override 字段

记录人工干预 AI 决策的情况。对标 IETF AAT `human_override` 字段。

```yaml
human_override:
  operator_id: "ZephyrAlpha-Owner"
  date: "2026-04-28"
  reason: "AI 提议删除风控参数，Owner 否决"
  original_action: "删除 risk_threshold 参数"
```

| 子字段 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `operator_id` | string | 是 | 干预人标识 |
| `date` | string | 是 | 干预日期 |
| `reason` | string | 是 | 干预原因 |
| `original_action` | string | 否 | AI 原本打算做的动作 |

**何时填写**：当 Owner 否决了 AI 的修改提议时，必须在本字段记录。

### 10.15 last_reviewed_by 字段

记录最后一次 review 的人和日期。对标 SR 11-7 模型验证要求。

```yaml
last_reviewed_by:
  reviewer: "ZephyrAlpha-Owner"
  date: "2026-04-28"
  model_used: "claude-opus-4.7"
```

| 子字段 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `reviewer` | string | 是 | review 人/模型标识 |
| `date` | string | 是 | review 日期 |
| `model_used` | string | 否 | 如果是 AI review，用的什么模型 |

**与 `review_status` 的关系**：`last_reviewed_by` 记录"谁 review 的"，`review_status` 记录"review 结果是什么"。

### 10.16 review_status 字段

标注文档的 review 状态。对标 SR 11-7 持续监控要求。

| 值 | 含义 | 说明 |
|----|------|------|
| `unreviewed` | 未 review | AI 创建后尚未被任何人 review |
| `reviewed` | 已 review | 已被 review 但未正式批准 |
| `approved` | 已批准 | Owner 正式批准，可作为依据使用 |
| `rejected` | 已否决 | review 后被否决，需要修改 |

**默认值**：`unreviewed`。

**pre-commit 校验规则**：
- `safety_level: H` 且 `review_status: unreviewed` → P1 警告
- `status: active` 且 `review_status: unreviewed` → P2 警告

### 10.17 derived_from 字段

记录本文档的**横向知识来源**——AI 在创建/修改本文档时，读了哪些文件、综合了哪些信息。

```yaml
derived_from:
  - path: "docs/03_modules/l02_alpha_factor/<module>/blueprint.md"
    relationship: synthesized
    sections: ["BD-003", "BD-007"]
  - path: "docs/08_knowledge/KE-042-factor-decay-pattern.md"
    relationship: referenced
```

| 子字段 | 类型 | 必填 | 说明 |
|--------|------|:----:|------|
| `path` | string | 是 | 来源文件路径 |
| `relationship` | enum | 是 | 推导关系：`synthesized`（综合多名来源后产出新结论）/ `referenced`（直接引用来源中的事实或决策）/ `transformed`（对来源内容做了实质性修改后使用） |
| `sections` | string[] | 否 | 具体引用了来源中的哪些决策编号或章节 |

**与 `supersedes` 和 `provenance` 的正交关系**：

| 字段 | 维度 | 回答的问题 | 对标 |
|------|------|-----------|------|
| `supersedes` | 纵向替代 | "这份文档取代了什么" | — |
| `derived_from` | 横向推导 | "这份文档的知识从哪里综合而来" | W3C PROV: wasDerivedFrom / Dublin Core: dcterms:isDerivedFrom / OpenLineage: inputs |
| `provenance` | 创作过程 | "谁在什么流程中创建了这份文档" | OpenLineage: producer / W3C PROV: wasGeneratedBy |

**典型使用场景**：
- AI 读了 3 篇 arXiv 论文 + 2 份项目蓝图，写了一篇 knowledge_entry → `derived_from` 列出 5 个来源
- AI 综合多个模块蓝图的设计决策，写了一份跨层架构视图 → 标注 `relationship: synthesized`
- AI 翻译/重构了一份外部参考文档 → 标注 `relationship: transformed`

**默认值**：不填。当文档由 AI 基于多个来源综合生成时，建议填写。

---

## 11. 正文结构要求

### 11.1 各 doc_type 的正文模板

#### standard（标准）

```
# 标题
> module_id | version | status

## 1. 目的与范围
## 2. 定义（术语表）
## 3. 规范正文（按条款编号）
## 4. 违规检测规则
## 5. 变更记录
```

#### adr（架构决策记录）

```
# ADR-{NNNN}: 标题
> status | date | deciders

## 上下文（Context）
## 决策（Decision）
## 理由（Rationale）
## 后果（Consequences）
## 否决方案（Alternatives Considered）
```

#### blueprint（模块蓝图）

> 📄 完整模板文件：`docs/01_policies_and_standards/templates/blueprint-template.md`

```
# 标题
> module_id | version | status | layer

## 1. 设计背景与目标
## 2. 架构决策
### 2.1 决策记录表
| 决策编号 | 问题 | 选项 | 结论 | 理由 | 关联 ADR |
## 3. 模块边界
### 3.1 职责范围
### 3.2 不包含的职责
## 4. 接口契约
### 4.1 公共 API（Python type hints）
### 4.2 数据模型
### 4.3 事件/消息格式
## 5. 约束条件
### 5.1 技术约束
### 5.2 业务约束
### 5.3 性能约束
## 6. 依赖关系
## 7. 已知风险与缓解
## 后果（Consequences）
## 否决方案（Alternatives Considered）
```

#### construction_plan（施工图纸）

> 📄 施工指引已合并至：`docs/01_policies_and_standards/templates/blueprint-template.md` §12

```
# 标题
> module_id | version | status | layer

## 1. 前置条件
### 1.1 依赖蓝图
| 蓝图路径 | 蓝图状态 | 本图涉及的决策编号 |
### 1.2 输入数据契约
### 1.3 运行环境
## 2. 模块分解
| 模块 ID | 名称 | 职责 | 优先级 |
## 3. 公共 API
### 3.1 函数签名（Python type hints）
### 3.2 异常类型
## 4. 数据流（Mermaid 图）
## 5. 实施步骤
| 步骤 | 内容 | 对应蓝图决策 | 验收标准 |
## 6. 来源追溯表（§8 自包含性）
| 蓝图决策编号 | 决策结论 | 本图实施位置 | 决策来源路径 |
## 7. 测试
### 7.1 P0 用例（每模块至少 3 条，含边界/异常）
### 7.2 测试数据准备
## 8. 技术选型与 TDR
## 9. 已知风险与缓解
## 10. 施工状态
| construction_status | verification_status |
```

#### design（架构视图）

```
# 标题
> module_id | version | status | layer

## 1. 视图概述
## 2. 架构元素
## 3. 关系与交互
## 4. 视图间映射
## 5. 约束与原则
```

#### plan（任务书）

```
# 标题
> module_id | version | status | layer

## 1. 任务目标
## 2. 任务分解
## 3. 依赖关系
## 4. 验收标准
## 5. 风险与缓解
```

#### roadmap（路线图）

```
# 标题
> module_id | version | status | layer | valid_from

## 1. 当前阶段目标
## 2. 未来 3 个月方向
## 3. 关键里程碑
## 4. 假设与约束
## 5. 与施工计划的对接
```

#### register（登记表）

```
# 标题
> module_id | version | status

## 1. 注册表说明
## 2. 条目表（Markdown 表格）
## 3. 变更记录
```

#### log（日志）

```
# 标题
> module_id | date | ai_model | context_budget_used

## 1. 任务列表
## 2. 变更文件
## 3. 知识提取
## 4. 关键决策
## 5. 未完成事项
```

#### knowledge_entry（知识条目）

```
# 标题
> module_id | category | source_file | extracted_date

## 1. 核心结论
## 2. 详细分析
## 3. 关联条目
```

### 11.2 Taskbook 状态符号

在任务书、施工图、检查清单中使用统一的状态符号：

| 符号 | 含义 |
|------|------|
| `[ ]` | 未开始 |
| `[/]` | 进行中 |
| `[x]` | 已完成 |
| `[~]` | 已取消/跳过 |

### 11.3 决策记忆分流规则

| 决策类型 | 记录位置 | doc_type |
|---------|---------|----------|
| 架构选型 | ADR | `adr` |
| 设计权衡 | rationale_log | `log` |
| 临时探索结论 | discussion_draft | `discussion_draft` |
| 经验证的最佳实践 | knowledge_entry | `knowledge_entry` |
| 流程/规则变更 | standard | `standard` |

---

## 12. 文件命名规范

文件命名遵循 [file-naming-standard.md](01_policies_and_standards/governance/document/file-naming-standard.md) v2.0.1（全小写 kebab-case，禁止大写/版本号/日期后缀）。

本节仅补充 meta 域特有的 doc_type 命名约定——其余均以 file-naming-standard.md 为准：

| doc_type | 命名格式 | 示例 |
|----------|---------|------|
| `standard` | `{topic}-standard.md` | `document-metadata-standard.md` |
| `adr` | `adr-{NNNN}-{title}.md` | `adr-0002-single-schema-with-phased-required-fields.md` |
| `blueprint` | `{module-name}-blueprint.md` | `data-source-blueprint.md` |
| `construction_plan` | `construction-plan-{layer}-{name}.md` | `construction-plan-l00-data-source.md` |
| `design` | `{topic}-design.md` | `capacity-assurance-design.md` |
| `plan` | `taskbook-{intent}.md` | `taskbook-backtest-engine-v2.md` |
| `roadmap` | `roadmap-{scope}-{YYYYMM}.md` | `roadmap-q2-202604.md` |
| `register` | `{topic}-registry.yaml` 或 `{topic}-register.md` | `governance-asset-registry.yaml` |
| `index` | `index.md` | `index.md` |
| `readme` | `README.md` | `README.md` |
| `log` | `session-{YYYYMMDD}-{NNN}.md` | `session-20260428-001.md` |
| `knowledge_entry` | `KE-{NNN}-{topic}.md` | `KE-016-data-version-control.md` |
| `audit_report` | `{scan-type}-report-{YYYYMMDD}.md` | `sentinel-l1-report-20260428.md` |

---

## 13. 升格规则（Workspace → Canonical）

### 13.1 升格路径

```
外部独立工作区（`19_development_workspace/` 已删除，2026-05-02 迁至外部）  ← Draft / in_discussion
    ↓ 内容稳定后
02_enterprise_architecture/ 或 governance/  ← review_ready
    ↓ Owner 审阅后
01_policies_and_standards/ 相应子目录 或 02_enterprise_architecture/  ← active / accepted
```

### 13.2 升格操作

1. **只改 `status` 值**，不改 schema，不做字段迁移
2. **只改文件位置**（`git mv`），不改文件名（除非违反命名规范）
3. 升格时必须补齐目标阶段的必填字段
4. 升格 commit message：`promote: {old_path} -> {new_path} | status: {old} -> {new}`

### 13.3 降格规则

- `active` → `deprecated`：需 Owner 审批 + 填写 `superseded_by`（必填，有替代品填路径，无替代品填 `"N/A"`）
- `deprecated` → `active`：需 Owner 审批（重新启用）
- 禁止跨级降格（`draft` 不能直接变 `deprecated`，必须先升格为 `active`）

---

## 14. 违规检测规则

### 14.1 自动检测项（pre-commit 执行）

| ID | 检测内容 | 严重性 | 阻断？ |
|----|---------|--------|:------:|
| META-V01 | 缺少 frontmatter | P0 | ✅ |
| META-V02 | 缺少当前阶段必填字段 | P0 | ✅ |
| META-V03 | doc_type 使用未定义值 | P0 | ✅ |
| META-V04 | status 使用未定义值 | P1 | ✅ |
| META-V05 | ttl 使用未定义值 | P1 | ✅ |
| META-V06 | module_id 格式不符合 §5 规范 | P1 | ✅ |
| META-V07 | date 格式非 YYYY-MM-DD | P2 | ❌ warn |
| META-V08 | doc_type 与存放路径不匹配（§3.4） | P2 | ❌ warn |
| META-V09 | AI 生成文件缺 `created_by: agent` | P1 | ✅ |
| META-V10 | AI 生成文件缺 `ttl` 字段 | P1 | ✅ |
| META-V11 | Deprecated 文件缺 `superseded_by` | P1 | ✅ |
| META-V12 | `layer` 字段值不在合法列表中 | P2 | ❌ warn |
| META-V13 | `safety_level` 使用未定义值 | P1 | ✅ |
| META-V14 | `evolution_policy` 使用未定义值 | P1 | ✅ |
| META-V15 | `construction_plan` 缺 `blueprint_refs` | P1 | ✅ |
| META-V16 | `blueprint_refs` 引用的蓝图路径不存在 | P0 | ✅ |
| META-V17 | `blueprint_refs` 引用的蓝图 status 为 deprecated | P0 | ✅ |
| META-V18 | `governance_family` 使用未定义值 | P2 | ❌ warn |
| META-V19 | `ai_capability_slot` 使用未定义值 | P2 | ❌ warn |
| META-V20 | 两个以上 `status: active` + `doc_type: standard` 文件对同一领域声明 `唯一真源`（SSoT） | P0 | ✅ |

### 14.2 人工审查项

| ID | 审查内容 | 频率 |
|----|---------|------|
| META-R01 | doc_type 语义是否准确（不是路径匹配就一定对） | 每月 |
| META-R02 | `summary` 是否能帮助 AI 理解文档大意 | 每月 |
| META-R03 | `tags` 是否覆盖了 AI 检索需要的关键词 | 每季度 |

---

## 15. Schema 漂移防护机制

### 15.1 核心原则

**一个项目，一套 schema，没有例外。** 所有工具、AI 员工、脚本读取 doc_type 合法值、字段定义时，只看本文件。

### 15.2 防护手段

| 手段 | 说明 |
|------|------|
| **单一真源** | 本文件是 doc_type 受控词表和字段定义的唯一权威来源 |
| **自动生成** | `frontmatter-schema.json` 从本文件自动生成，禁止手写 |
| **pre-commit 校验** | 提交时自动校验 frontmatter 合规性 |
| **新增值走 ADR** | 新增 doc_type 必须提 ADR，审批后更新本文件 |
| **定期扫描** | 每月运行全项目 frontmatter 合规扫描，发现漂移立即报告 |
| **版本化** | 本文件变更时更新 `version` 字段，`frontmatter-schema.json` 同步更新版本号 |

### 15.3 漂移修复流程

1. 发现漂移（扫描报告 / AI 自检 / 人工审查）
2. 判断漂移类型：
   - **字段名漂移**（如 `doc_type: standard` vs `doc_type: governance_standard`）→ 以本文件为准，修正文件
   - **新增值漂移**（如使用了 `doc_type: policy`）→ 判断是否需要新增合法值；如需要，走 ADR 流程；如不需要，修正为现有合法值
   - **缺失字段漂移**（如 Active 文件缺 `layer`）→ 补齐字段
3. 修正后运行全项目合规扫描确认

---

## 16. 与专业机构对照表

| 本项目字段 | IETF AAT | OpenLineage | MLflow | Databricks UC | ISO 11179 |
|-----------|----------|-------------|--------|---------------|-----------|
| `author_agent` | agent_id | producer.runId | — | created_by | — |
| `execution_model` | model_id | job.name | — | — | — |
| `derived_from` | — | inputs | — | — | — |
| `provenance` | — | producer | — | — | registration_authority |
| `compliance_tags` | — | — | — | — | — |
| `human_override` | human_override | — | — | — | — |
| `review_status` | — | — | status | — | — |
| `safety_level` | risk_score | — | — | — | — |
| `ai_autonomy` | trust_level | — | — | — | — |
| `evolution_policy` | — | — | lifecycle_stage | — | — |
| `doc_type` | — | — | artifact_type | — | data_element |
| `status` (DocStatus) | — | — | status | — | registration_status |
| `status` (TaskStatus) | task_status | job.status | — | — | — |
| `status` (KeStatus) | — | lifecycleState | — | — | — |
| `category` | — | — | — | — | — |
| `domain` | — | namespace | — | catalog | — |
| `namespace` | — | namespace | — | schema | — |
| `module_id` | — | — | name | — | identifier |
| `ttl` | — | — | — | — | — |
| `blueprint_refs` | — | inputs | — | — | — |

**关键发现**：
1. **identity vs execution 拆分**：5 家机构 100% 拆分身份（agent_id/producer）与执行（model_id/job），无例外
2. **status 三域分离**：文档/任务/知识各有独立状态机，专业机构同样分离（MLflow: status, IETF: task_status, OpenLineage: lifecycleState）
3. **audit 字段独立**：IETF AAT 有 `human_override`，SR 11-7 要求 `review_status`，EU AI Act 要求 `compliance_tags`
4. **provenance 是行业术语**：OpenLineage 和 W3C PROV 都用 `provenance`，运行时溯源用不同词（本项目用 `WriteTrace`）

---

## 17. 与其他标准的关系

| 标准 | 关系 | 交互点 |
|------|------|--------|
| `unified-numbering-standard.md` | 互补 | 本文件 §5 定义 module_id 的 DOMAIN 格式，该文件定义 L{XX} 层编号格式 |
| `document-lifecycle-standard.md` | 下游 | 本文件定义 status 语义，该文件定义 TTL 管理和快照规则 |
| `file-naming-standard.md` | 下游 | 本文件 §9 定义各 doc_type 的命名约定，该文件定义通用命名规则 |
| `encoding-safety-standard.md` | 独立 | 编码安全与本标准无冲突 |
| `ai-autonomy-authority-registry.md` | 上游 | 本文件 §7 的 `ai_autonomy` 字段值与该注册表三层模型对齐 |
| `task-card-standard.md` | 下游 | 任务卡的 `ai_autonomy` 字段遵循本文件 §7 定义 |
| `ssot-authority-map.md` | 上游 | 本文件 §1.3 的 SSoT 声明与该文件对齐 |

---

## 18. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 5.9.0 | 2026-05-02 | **SSoT 根治——单层真源**：§3.2 完整表（23 行）→速查引用（10+13 的速查列表 + vocabulary YAML 指针）。§3.3 移除 2 个已废弃类型行（ai_governance/reference），标注"完整映射见 YAML"。§3.4 移除 4 个已废弃类型行（ai_governance/candidate_pool/discussion_draft/reference），新增 operational_rule/protocol/vocabulary/contract/terminology/template/declaration/service_spec 行，标注 YAML 优先。§3.5 流程简化："改 YAML 即可，本表不需要手动同步"。根因：双层手动同步是结构性缺陷——对标 12 家专业机构（K8s/Terraform/OpenAPI/Google SRE/Anthropic/Cursor/AGENTS.md/ComfyUI 等），无一使用"人工同步双层真源"。方案选型详细论证见 Session Log。 |
| 5.8.0 | 2026-05-02 | **vocabulary YAML 对齐**：§3.2 完整词表从 25→23 种——移除 5 个已废弃 doc_type（checklist/ai_governance/candidate_pool/discussion_draft/reference，已在 vocabulary deprecated_values 中），新增 3 个 vocabulary 已注册但本表缺失的类型（vocabulary/contract/declaration）。§3.2.1 子集从 8→10 值（新增 vocabulary/contract）。§6 TTL 表新增 periodic_review_90d（ttl-vocabulary.yaml 已有）。新增 YAML 优先声明——本表从 vocabulary YAML 派生，冲突以 YAML 为准。根因：词汇表清理/新增后 metadata 手动同步遗漏了 5 个 deprecated 删除 + 3 个新增。 |
| 5.7.0 | 2026-05-02 | **生命周期引用约束（Lifecycle Reference Constraint）**：§4.1.1 新增 LRC-001~005 规则——draft 文件不可被 active 文件通过 depends_on 引用（对标 Kubernetes Admission Controller + ITIL Change Enablement）。定义 lifecycle_stage 字段（4 值：draft/blueprint_reviewed/construction_reviewed/active，beta 落地）。动机：审计发现 GOV-MOD-002（draft）被 6 个 active 文件量产级引用——status 与 depends_on 之间没有互锁机制。 |
| 5.6.0 | 2026-05-02 | §3.2 拆分 `design` 为 `architecture_view`（正式架构视图）+ `design`（工作级设计），消除"一个词两种文档"歧义。doc_type 25 种。(1) §3.2 #6 design 含义从"架构视图/设计文档"→"设计文档（工作级设计，非正式架构视图）"，路径从 `02_enterprise_architecture/`→`02_enterprise_architecture/designs/`。(2) §3.2 新增 #25 architecture_view（正式目标架构，TOGAF/ArchiMate 级），路径 `02_enterprise_architecture/target-architecture/`。(3) §3.3 组合示例 design+layer→architecture_view+layer。(4) §3.4 路径映射拆分为 architecture_view（target-architecture/）+ design（designs/），互禁对方目录。(5) §1.3 总种数、§2.5 表、§3.5、§14 各计数引用同步更新。(6) 相关 Python 脚本同步更新：check_frontmatter_metadata.py DOC_TYPE_LEGAL + architecture_view、doc_type-vocabulary.yaml + architecture_view |
| 5.5.0 | 2026-05-01 | §3.2 拆分 `plan` 为 `plan`（任务书）+ `roadmap`（路线图），消除"三合一"歧义。`plan` 的"执行计划"语义归入 `construction_plan`。doc_type 24 种。(1) §3.2 完整词表拆分 plan #7 → plan #7（任务书）+ roadmap #8（路线图），#8~#23 顺移为 #9~#24。(2) §3.3 组合示例拆分 plan+layer→roadmap+layer。(3) §3.4 路径映射 plan 移除 `04_construction_plans/`，新增 roadmap 行。(4) §2.5 表新增 roadmap 列。(5) §2.6 新增一致性约束 #11（roadmap → declarative）。(6) §12 命名 plan 从 `construction-plan` 改为 `taskbook`，新增 roadmap 命名。(7) §11 正文模板 plan 改为"任务书"，新增 roadmap 模板。(8) §1.3 总种数、§5 B 域范围、各枚举引用同步更新。(9) 相关 Python 脚本同步更新：check_frontmatter_metadata.py DOC_TYPE_LEGAL + roadmap、triage.py VALID_DOC_TYPES + roadmap、doc_type-vocabulary.yaml + roadmap |
| 5.4.0 | 2026-05-01 | §2.5 表扩展 +3 列（adr/blueprint/construction_plan）消除模板文件的 per-doc_type 字段约束盲区；§2.6 +3 条一致性约束（#8/#9/#10）对齐 rule_form-vocabulary.yaml 已有映射；条件说明表同步更新 5 行（补 layer/classification/verifiability/valid_from/evolution_policy 对新增 doc_type 的条件说明） |
| 5.3.0 | 2026-05-01 | §1.3 加入 YAML 子类型分类（document_yaml / registry_yaml），解决 _registry/ 下 6 个 .yaml 文件缺 depends_on 和 frontmatter 字段的根本问题 |
| 5.2.0 | 2026-05-01 | 门头精简 + 上下文压缩。(1) 删除已解决问题 1（doc_type边界模糊，v5.0.0已解决）。(2) 拆分预判条件后移至文件末尾。(3) §1.0 最小必读路径从表格压缩为单行声明（~300→~40 Token）。版本号 minor +1。 |
| 5.1.9 | 2026-05-01 | 回退编辑。(1) 删除 §3.7（doc_type 迁移方案拆分后的残桩）——迁移方案独立文件 doc_type-migration-plan.md 已被 Owner 指令删除（不属于 meta/ 目录责任范围）。(2) 删除 dead link。版本号 patch +1。 |
| 5.1.8 | 2026-05-01 | 编辑性压缩。(1) §3.7 迁移方案（45 行）拆分为独立文件 doc_type-migration-plan.md，降低注册表上下文开销。(2) §5.8 编号表从 13 个子表（131 行）压缩为单汇总表（18 行），去 60% 占位行。版本号 patch +1。 |
| 5.1.7 | 2026-05-01 | 新增 §1.0 最小必读路径（5 步，~1000 Token），解决 2038 行注册表对新 AI session 的上下文开销问题。新 AI 读完即可开始施工。版本号 patch +1。 |
| 5.1.6 | 2026-05-01 | 新增 META-V20 违规检测规则：扫描所有 `status: active` + `doc_type: standard` 文件的 SSoT 声明章节，检测两个以上文件对同一领域声称唯一真源的冲突（P0 阻断，pre-commit 自动执行）。杜绝"两个文件说自己管同一件事"的 SSoT 分裂。 |
| 5.1.5 | 2026-05-01 | 编辑性变更——frontmatter 字段排序对齐 PS-STD-001 §2.3（date 移至 created_by 之后，ai_autonomy 移至 verifiability 之后，supersedes 移至 verifiability 之后）。版本号 patch +1。 |
| 5.1.4 | 2026-05-01 | 编辑性压缩与跨文件对齐。§12 文件命名规范：删除与 file-naming-standard.md 重复的 §12.1（4 条通用规则），§12.2 前加入引用声明"以 file-naming-standard.md 为准"。版本号 patch +1（编辑性变更）。 |
| 5.1.3 | 2026-05-01 | PS-STD-009+010 合并收尾。(1) §5.8.1：PS-STD-010 从"🆕 新建"→"📋 可用（已合并至 PS-STD-009）"（生命周期内容合并至规则治理标准）。(2) PS-STD-011 文件名更新为 `governance-methodology-standard.md`（补齐 `-standard` 后缀以符合同目录命名约定）。(3) 更新 PS-STD-001 自身 `version` 为 5.1.3。 |
| 5.1.2 | 2026-05-01 | meta/ 系统性自审收尾。(1) §5.8.1 注册 META-GLS-001（glossary.md——术语表）和 PS-STD-006（governance-metrics-standard.md——治理度量标准）。(2) PS-STD-006 编号从 📋 可用→🆕 新建。 |
| 5.1.1 | 2026-05-01 | meta/ 系统性自审。(1) frontmatter 字段修正：`version` number→string（加引号，防 YAML 解析为浮点数）、`date` 更新为 2026-05-01（同步实际修改日期）、`valid_from` 更新为 2026-04-28（首次注册生效日）。(2) §5.8.1 幽灵条目清理：删除声称存在但实际不存在的 PS-STD-006/007（错误标记为"✅ 已有，保留"），标注 PS-STD-005~007 为"📋 可用（待分配）"，编号可回收复用。(3) §5.8.1 新增 PS-STD-012（rule-verification-standard.md）和 META-IDX-001（index.md），均为 meta/ 系统审查补齐。 |
| 5.1.0 | 2026-05-01 | B5 审查连带修复。(1) §2.1 字段表：修正 8 处过时节号引用（module_id §6→§5、status §7→§4、layer §6.3→§5.5、safety_level/evolution_policy/ai_autonomy/provenance/author_agent/governance_family 从 §8.x→§10.x）。(2) §2.8 禁止行为表与 §3.6 #5 去重：合并 #1+#2→跨域引用，互补不重叠。(3) §2.6 新增"架构公民原则"说明块：`stable + immutable_core` 合法（约束 #1 是单向的，逆面不成立），附合法映射光谱防误判。 |
| 4.4.0 | 2026-04-29 | 新增 §9.5 layer 枚举（14值）、§9.6 source_type 枚举（7值）、§9.7 priority 枚举（5值）；§9 从 4 个跨域枚举扩展为 7 个；更新 §1.4 SSoT 声明拆分 §9.1~§9.4 和 §9.5~§9.7 两行；标注代码真源需同步对齐（triage.py VALID_LAYERS、kms-entry-schema.md source_type、schemas.py AuditSeverity→Priority） |
| 4.4.0 | 2026-04-29 | 新增文件头部"⚠️ 待解决重大问题"区域，记录 3 个已识别但未解决的问题（doc_type词表边界模糊、旧长名未迁移、internal待迁移），确保每次打开本文件都能看到 |
| 4.3.0 | 2026-04-29 | **真元规则裁定**：§4.1 DocStatus 从 7 种精简为 3 种（draft/active/deprecated），删除 in_discussion/review_ready/accepted/superseded；理由：Vibe Coding语境下AI只需知道"能不能用"、废弃原因靠superseded_by字段区分、审阅由review_status单独管、不按doc_type分状态；§4.5 大小写约定从"统一小写"升级为"枚举值小写+标识符大写"二元规则（§4.5.1~§4.5.5）；§4.6 classification 二分法（public/confidential，删除internal）；§2.2 分阶段闸门删除Accepted行、Deprecated必填superseded_by；§13.3 降格规则同步更新 |
| 4.2.0 | 2026-04-29 | 新增 §1.5 消费者注册表（对标 ISO 11179 §6.2 Stewardship），4 层分级（Tier 1 硬编码枚举/Tier 2 引用权威/Tier 3 字段对齐/Tier 4 已废弃）+ 变更同步规则矩阵 |
| 4.1.0 | 2026-04-29 | 三域 status 分离（DocStatus 7值/TaskStatus 10值/KeStatus 10值）；新增 §7 域 B 任务卡字段（18字段）；新增 §8 域 C AI 治理字段交叉索引 + provenance 双定义澄清（frontmatter `provenance` vs 代码 `WriteTrace`）；新增 §9 受控枚举定义（category 10值/domain 10值/namespace 7值/AgentRole 6值）；layer 格式确认为全小写 `l00_data_source`；新增 §16 与专业机构对照表；章节重新编号（§7-§18） |
| 4.0.0 | 2026-04-28 | 重命名为元数据注册表（metadata-registry.md），扩展为全项目三域字段真源；`primary_model` → `execution_model`（对标 IETF model_id）；`ai_model` → `author_agent`（对标 IETF agent_id）；明确域 A（文档 frontmatter）+ 域 B（任务卡）+ 域 C（AI 治理）三层架构；新增 4 个审计字段：`compliance_tags`（§8.13）、`human_override`（§8.14）、`last_reviewed_by`（§8.15）、`review_status`（§8.16）；新增 §4 域 B 任务卡字段、§5 域 C AI 治理字段；新增 §12 与专业机构对照表；章节编号 §7→§8、§8→§9 |
| 3.6.0 | 2026-04-28 | 字段标准最终定版：新增 `safety_level`（§8.10）、`evolution_policy`（§8.11）、`blueprint_refs`（§8.12）三个字段；`governance_family` 合法值加 `D`（共享底座）；`ai_capability_slot` 合法值加 `active`（已激活）；`primary_model` 与 `ai_model` 明确语义分工、不可合并；新增 META-V13~V19 七项违规检测；字段排序约定更新（§2.3） |
| 3.5.0 | 2026-04-28 | 拆分 `design` 为三种独立 doc_type：`blueprint`（模块蓝图）、`construction_plan`（施工图纸）、`design`（架构视图）；蓝图和施工图各自拥有独立正文模板；蓝图模板侧重架构决策记录表+模块边界+接口契约+约束条件；施工图模板侧重依赖蓝图+来源追溯表（§8 自包含性）+实施步骤+施工状态双字段；doc_type 从 19 种扩展为 21 种 |
| 3.4.0 | 2026-04-28 | 撤回 primary_model+ai_model 合并：保留两个字段，标注"未来统一为 ai_model"但当前不执行（涉及 18 个代码文件+数据库迁移，直接合并会运行时崩溃）；补全三层口子 9 项预留（§7.8）；AI 治理字段完整覆盖 49 项 |
| 3.3.0 | 2026-04-28 | 修正 AI 员工字段：合并 primary_model 和 ai_model 为统一 ai_model 字段；Session Log 专用字段（context_budget_used/knowledge_extracted/next_session_handover）从 frontmatter 移出为正文字段；新增 §7.8 三层口子预留 9 项（C/D/F 各 3 项）；AC-2 四列字段 + 三层口子 9 项 = 13 项 AI 预留 |
| 3.2.0 | 2026-04-28 | 补全 AI 员工字段：新增 §7.5 模型选择字段（primary_model/model_rationale/fallback_model）、§7.6 Session Log 专用字段（ai_model/context_budget_used/knowledge_extracted/next_session_handover）、§7.7 治理系统 AI 预留字段（governance_family/ai_capability_slot/ai_autonomy_level_planned/ai_employee_count_planned）、§7.8 AI 决策日志说明（独立 schema，非 frontmatter） |
| 3.1.0 | 2026-04-28 | doc_type 从 17 种扩展为 19 种：新增 `policy`（强制规则，从 `standard` 拆出）、`reference`（参考文档）；`standard` 含义缩窄为"推荐做法"；`design` 扩展覆盖施工图；`plan` 缩窄为路线图/任务书；本文件自身 doc_type 从 `standard` 改为 `policy` |
| 3.0.0 | 2026-04-28 | 合并 frontmatter-standard.md v1.0.0 + discussion-document-standard.md v2.0.0 + frontmatter-schema.json R4；doc_type 从 13/15 种统一为 17 种短名；新增 AI 员工字段（§7）；新增分阶段必填闸门（§2.2）；新增 schema 漂移防护机制（§12）；管辖范围从工作区扩展为全局 |
| 2.0.0 | 2026-04-17 | discussion-document-standard.md：取消双 schema，改为单一 schema + 分阶段必填闸门（ADR-0002） |
| 1.0.0 | 2026-04-17 | discussion-document-standard.md：初始版本，沙盒档/正式档双 schema |
| 1.0.0 | 2026-04-22 | frontmatter-standard.md：从 discussion-document-standard.md 提取简化版（13 种 doc_type 长名） |
