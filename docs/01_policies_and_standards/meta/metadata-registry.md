---
module_id: PS-STD-001
title: ZephyrAlpha 元数据登记表
doc_type: standard
status: active
version: "6.0.1"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-02"
valid_from: "2026-04-28"
summary: "ZephyrAlpha 全项目元数据的唯一真源注册表。定义三域字段（文档 frontmatter / 任务�?/ AI 治理）、doc_type 受控词表�?7 种，canonical SSoT = vocabulary YAML，本文件仅保留速查引用）、审计字段、字段改名记录、与专业机构对照表。v6.0.1：�?4.1 新增 META-V21（索�?entry vs frontmatter `status` 不一致）。v6.0.0：�?.6 classification 域A/域B 分层真源；�?.1 语义28 + §7.1.1 追踪3 = Task �?1；�?.7 Priority �?P4/SQLite 对齐；废弃「删�?INTERNAL」迁移叙述；`shared/schemas.py` 路径全库统一�?
ttl: permanent
tags: [metadata, frontmatter, doc_type, schema, ssot, ai-governance, metadata-registry]
rule_form: declarative
scope: global
stability: stable
verifiability: automated
supersedes:
  - path: docs/01_policies_and_standards/meta/metadata-registry.md
    version: 1.0.0
    reason: "v3.0.0 合并吸收，doc_type �?3种扩展为17种，新增 AI 员工字段、分阶段必填闸门、module_id 规范"
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
> 本注册表�?ZephyrAlpha **元数据标�?*的唯一真源（Single Source of Truth）—�?
> 定义字段应该有什么属性、校验规则、分类体系�?
> 覆盖三个域：文档 frontmatter（域 A）、任务卡（域 B）、AI 治理（域 C）�?
> **字段的具体定义（字段�?类型/必填�?枚举值）�?PS-REG-012 [frontmatter-field-registry.yaml](../_registry/catalogs/frontmatter-field-registry.yaml) �?canonical SSoT**
> （YAML 格式、字段级粒度、机器可校验——符�?AGENTS.md §6.9 YAML 优先原则）�?
> 本文件管"规则"（字段应满足什么规范），PS-REG-012 �?数据"（每个字段具体是什么）�?
> 所有工具、AI 员工、pre-commit 钩子、CI 流水线：**读字段定�?�?�?PS-REG-012；读字段规范/校验逻辑 �?查本文件**�?
>
> 对标标准：ISO 11179（元数据登记表）、IETF Agent Audit Trail（AAT）、OpenLineage�?

---

> ## ⚠️ 待解决问题（2 个）
>
> **任何修改本文件或使用 doc_type 的人/AI 必须知晓**�?
>
> | # | 问题 | 严重�?| 状�?| 影响范围 |
> |---|------|:------:|------|---------|
> | 1 | ~~**�?doc_type 长名未迁�?*~~ | ~~🔴~~ | 📋 迁移方案已定 | 迁移方案�?§3.7，施�?beta 批量执行 |
> | 2 | **`internal` classification 值待迁移**�?00 个文件标 `classification: internal`，已裁定删除 `internal` 改为 `confidential`，但尚未批量执行 | 🟡 | 待迁�?| 100 �?.md 文件 + 2 �?Python 文件 + 数据�?DDL |
>
> **处理原则**：问�?1 迁移方案已定义（§3.7），施工 beta 批量执行。问�?2 在后�?session 批量执行迁移�?*在问题解决之前，不得新增使用旧长名或 `internal` 的文件�?*
>
> > 拆分预判条件�?§6（文件末尾）👉 `metadata-registry.md#split-conditions`

---

## 1. 目的与范�?

### 1.0 最小必读路径（~1000 Token�?

�?AI session 按此路径最快上手：§1（三域架构）�?§2.1（必填字段）�?§4（status词表）→ §3.1（doc_type词表）→ §14（违规检测规则）。其余章节按需查阅�?

### 1.1 目的

�?ZephyrAlpha 项目�?500+ 模块 AI 自治量化交易系统）建立统一的元数据登记表，确保�?

- **AI 员工**可以在无人类指导的情况下，正确理解、创建、分类、检索项目文�?
- **人类 Owner**可以快速定位任何文档的归属、状态、生命周�?
- **工具�?*（pre-commit、CI、校验脚本）基于同一套规则自动执行，无字段漂�?
- **知识传承**不依赖特�?AI 模型的记忆，而是编码在文档元数据�?
- **审计合规**出事后可追溯到人/模型/决策过程，对�?EU AI Act / SR 11-7 / IETF AAT

> **理论基础**：本注册表的设计哲学——字段优先级排序、`summary` 高于 `tags`、领域触发优于全量加载——遵�?Codified Context 论文（arXiv 2602.20478）在 108KLOC 分布式系统实验中验证�?距离衰减效应"�?领域触发策略"原则。详�?PS-STD-000 §3�?

### 1.2 三域架构

本注册表覆盖三个域，每个域有各自的字段集合：

| �?| 名称 | 适用范围 | 字段�?|
|---|------|---------|--------|
| **A** | 文档 frontmatter | 所�?`.md` / `.yaml` 文件 | 40 |
| **B** | 任务�?| `doc_type: plan` �?`doc_type: roadmap` 的文�?| 18 |
| **C** | AI 治理 | AI 决策日志 + AI 员工档案 | 28+2 + 30+ |

**�?A 是全局�?*，所有文档都要遵守。域 B 和域 C 是专用的，只在特定场景下使用�?

### 1.3 范围

本标准覆�?ZephyrAlpha 项目**所有目�?*下的 `.md` �?`.yaml` 文件�?

#### 1.3.1 YAML 文件子类�?

项目中的 `.yaml` 文件�?*消费者不�?*分为两种子类型，遵循不同�?frontmatter 契约�?

| 属�?| `document_yaml` | `registry_yaml` |
|------|----------------|-----------------|
| **消费�?* | 人类 + AI（阅�?理解+执行�?| CI 脚本 / pre-commit（机器解�?校验�?|
| **典型文件** | `session-log-schema.yaml`、`model-capability-contract.yaml` | `_registry/` 下所�?.yaml（catalogs/ / contracts/ / vocabularies/�?|
| **最小必填字�?* | module_id, title, doc_type, status, version, date, owner�? 项——同 .md 文件�?| schema_version, doc_type, title, status�? 项） |
| **不要求的字段** | �?| module_id, rule_form, scope, stability, verifiability, layer（registry_yaml 不参与规则推导链�?|
| **depends_on 要求** | 必须声明——glossary #19 规定引用�?�?1 �?| 必须声明——声明依赖的元标准文件（�?PS-STD-001�?|

> **裁定依据**：`_registry/` 下的文件�?*机器消费的数据结�?*（词表清单、索引注册表、校验契约），不是人类阅读的 prose 规则文档。强行套�?document_yaml �?14 个必填字段（Active 阶段）会导致"词表文件被迫�?rule_form: data 假装自己是规�?的形式主义。承认其 `registry_yaml` 身份后，每个子类型只要求其消费者真正需要的字段�?

> **文件扩展名区�?*：`.yaml` 统一�?`registry_yaml` 契约；`.md` 统一�?`document_yaml` 契约。`_registry/schemas/` 下的 `.json` 文件（如 frontmatter-schema.json）不受本标准 frontmatter 约束——JSON 文件自带 `$schema` 自描述�?

#### 1.3.2 覆盖目录清单

| 目录 | 说明 |
|------|------|
| `01_policies_and_standards/` | 治理策略与标�?|
| `02_enterprise_architecture/` | 企业架构 |
| `03_modules/` | 模块生命周期文档（蓝图含施工指引+交付�?|
| `08_knowledge/` | 知识�?|
| `09_audit/` | 审计 |
| `10_compliance/` | 合规 |
| `03_modules/_b_track_interfaces/` | AI 工程 |
| `19_development_workspace/` | ~~开发工作区~~ 已删除（2026-05-02，迁至外部独立目录） |
| `archive/` | 归档 |
| 其他所有目�?| 无例�?|

### 1.4 SSoT 声明

| 内容 | 真源 | 非真�?|
|------|------|--------|
| doc_type 受控词表 | **doc_type-vocabulary.yaml**（canonical SSoT�?| 本文�?§3（速查引用）、frontmatter-standard.md v1.0.0（已废弃�?|
| �?A 字段定义（文�?frontmatter�?| **frontmatter-field-registry.yaml**（canonical SSoT�?| 本文�?§2（字段规�?校验逻辑，非字段数据定义）、frontmatter-schema.json（自动生成产物） |
| �?B 字段定义（任务卡�?| **本文�?§7** | task-card-standard.md（字段定义以本注册表为准，该文件保留业务规则�?|
| �?C 字段定义（AI 治理�?| **本文�?§8** | ai-autonomous-company-endgame-design.md（设计文档，字段定义以本注册表为准） |
| 受控枚举定义（category / domain / namespace / AgentRole�?| **本文�?§9.1~§9.4** | �?|
| 受控枚举定义（layer / source_type / priority�?| **本文�?§9.5~§9.7** | triage.py VALID_LAYERS（需对齐）、kms-entry-schema.md source_type（需对齐）�?*`src/zephyr/shared/schemas.py`** �?AuditSeverity→Priority 演进（需随版本对齐） |
| module_id 命名规范 | **本文�?§5** | unified-numbering-standard.md（层编号部分仍有效，模块 ID 格式以本文件为准�?|
| 状态语�?| **status-vocabulary.yaml**（canonical SSoT�?| 本文�?§4（规范解释） |
| rule_form 映射 | **rule_form-vocabulary.yaml**（canonical SSoT�?| 本文�?§2.6（一致性约束） |
| ttl 枚举 | **ttl-vocabulary.yaml**（canonical SSoT�?| 本文�?§6（规范解释） |

**任何与本文件冲突的定义，以本文件为准�?* 发现冲突时，应提决策记录（参�?MOD-KB-001 §3.9.5 三层决策记录模型）并修正冲突方�?

### 1.5 消费者注册表

> **交叉索引**：消费者注册的 authoritative tracking �?[registry-master-index.yaml](../_registry/catalogs/registry-master-index.yaml) §2（health_check_coverage�? §3（quick_lookup�?
> �?[frontmatter-field-registry.yaml](../_registry/catalogs/frontmatter-field-registry.yaml)（字段级定义）�?
> 以下�?human-readable 速查，不替代 canonical YAML�?

#### 1.5.1 Tier 1：硬编码枚举值（变更必须同步�?

以下文件**硬编码了本注册表的枚举�?*，注册表任何枚举变更都必须同步更新：

| 文件 | 依赖内容 | 同步要求 |
|------|---------|---------|
| `scripts/governance/check_frontmatter_metadata.py` | 全部枚举（doc_type 27值、status 3值、ttl 5值、safety_level 3值、evolution_policy 3值、governance_family 4值、ai_capability_slot 4值、category 10值、domain 10值、review_status 4值）+ 分阶段必填闸�?+ 路径映射规则 | **最高优先级**：枚举变更必须同 commit 更新 |
| `src/zephyr/shared/schemas.py` | TaskStatus 10 值、SafetyLevel 3 值、Classification 3 值、EvolutionPolicy 3 值、TaskNamespace 7 值、AuditSeverity 3 �?| **高优先级**：域 B 枚举变更必须�?commit 更新 |
| `src/zephyr/db/sqlite_schema.py` | DDL CHECK 约束硬编码了 status 10值、namespace 7值、safety_level 3值、classification 3值、evolution_policy 3�?| **高优先级**：DDL 变更需要数据库迁移脚本 |
| `src/zephyr/mcp/knowledge_base_server.py` | `_VALID_CATEGORIES` 10�?| **中优先级**：category 枚举变更必须同步 |
| `src/zephyr/mcp/tool_contracts.yaml` | category enum 10值、task_id 格式引用 §7.2 | **中优先级**：category 枚举变更必须同步 |
| `src/zephyr/kb/kb_repo.py` | KeStatus 10�?+ 状态转换表 | **高优先级**：域 C 知识条目状态变更必须同�?|
| `schemas/frontmatter-schema.json` | 全部字段�?JSON Schema 定义（本注册表的自动生成产物�?| **自动**：本注册表变更后重新生成 |

#### 1.5.2 Tier 2：引用本注册表作为权威依�?

以下文件**引用本注册表作为权威依据**，但不硬编码枚举值：

| 文件 | 引用方式 |
|------|---------|
| `.pre-commit-config.yaml` | GATE-15 配置段注释声�?权威依据：metadata-registry.md" |
| `scripts/governance/validate_ssot.py` | 使用注册表定义的字段名做校验 |
| `scripts/governance/validate_blueprint_provenance.py` | 校验 doc_type �?provenance 字段 |
| `scripts/governance/validate_truth_source_cascade.py` | 使用 doc_type 等字段做真源级联校验 |
| `scripts/governance/check_naming_convention.py` | 使用 doc_type 命名规则 |
| `scripts/governance/archive_drafts_zone.py` | 使用 doc_type �?status 字段 |
| `src/zephyr/hooks/ssot_guard.py` | 检查治理文件与注册表的一致�?|

#### 1.5.3 Tier 3：字段定义对齐（以本注册表为准）

以下文件**定义了与注册表对齐的字段**，字段定义以本注册表为准�?

| 文件 | 对齐内容 |
|------|---------|
| `docs/01_policies_and_standards/governance/task/task-card-standard.md` | �?B 任务卡字段（execution_model、safety_level 等） |
| `docs/01_policies_and_standards/_registry/schemas/session-log-schema.yaml` | author_agent 字段 |
| `docs/01_policies_and_standards/_registry/catalogs/task-card-meta-registry.yaml` | 任务卡元数据 |
| `docs/08_knowledge/kms-entry-schema.md` | domain 10值、knowledge_type 6�?|
| `docs/01_policies_and_standards/templates/blueprint-template.md` | frontmatter 模板字段 |
| `docs/01_policies_and_standards/templates/blueprint-template.md` | 蓝图 + 施工指引统一模板（设计和实施合并�?|
| `docs/01_policies_and_standards/meta/document-structure-standard.md`（PS-STD-002�?| 元标准模板，§2.3 引用本注册表作为 frontmatter 字段定义的权威来�?|

#### 1.5.4 Tier 4：已废弃但仍有引�?

| 文件 | 状�?| 说明 |
|------|------|------|
| `docs/01_policies_and_standards/meta/metadata-registry.md` | Deprecated | `superseded_by: metadata-registry.md`，旧 13 �?doc_type 长名 |
| `docs/19_development_workspace/structure-and-mapping/discussion-document-standard.md` | 已合�?| v2.0.0 �?metadata-registry.md v3.0.0 吸收 |

#### 1.5.5 ADR 设计决策源头

| ADR | 与本注册表的关系 |
|-----|----------------|
| `adr-0002-single-schema-with-phased-required-fields.md` | 本注册表分阶段必填闸门的设计依据 |
| `adr-0030-sqlite-task-metadata-store.md` | SQLite 元数据层与文�?frontmatter 的互补关�?|
| `adr-0040-pydantic-v2-structured-contracts.md` | Pydantic 模型�?frontmatter-schema.json 互为补充 |

#### 1.5.6 变更同步规则

| 变更类型 | Tier 1 同步要求 | Tier 2 同步要求 | Tier 3 同步要求 |
|---------|----------------|----------------|----------------|
| 新增枚举�?| �?commit 更新硬编�?| 无需操作 | 无需操作 |
| 删除枚举�?| �?commit 更新 + 迁移脚本 | 检查引�?| 检查引�?|
| 新增字段 | �?commit 更新校验逻辑 | 无需操作 | 按需对齐 |
| 字段改名 | �?commit 更新所有引�?| �?commit 更新引用 | �?commit 更新引用 |
| 修改必填阶段 | �?commit 更新分阶段闸�?| 无需操作 | 无需操作 |

---

## 2. �?A：文�?frontmatter 字段�?0 个固定字�?+ 1 �?custom_* 扩展�?

### 2.1 全局字段总表

> **Canonical SSoT**：`_registry/catalogs/frontmatter-field-registry.yaml`（PS-REG-012�?
>
> 以下仅列出字段名和必填阶段速查。完整的字段定义（类型、枚举值、描述、对标机构）请查�?**PS-REG-012**，本文件不再重复�?

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

### 2.2 分阶段必填闸�?

| 阶段 | 必填字段�?| 必填字段 |
|------|:---------:|---------|
| **Draft** | 7 | `module_id` `title` `doc_type` `status` `version` `date` `owner` |
| **Active** | 18 | Draft 全部 + `layer` `classification` `language` `created_by` `ttl` `summary` `tags` `rule_form` `scope` `stability` `verifiability` |
| **Deprecated** | 19 | Active 全部 + `superseded_by`（必填，有替代品填路径，无替代品�?`"N/A"`�?|

**升格只改 `status` 值，不改 schema，不做字段迁移�?*

### 2.3 字段排序约定

Frontmatter 中字段按以下顺序排列，便�?AI 和人类快速定位：

```
module_id �?title �?doc_type �?status �?version �?layer �?
owner �?classification �?language �?created_by �?
date �?valid_from �?ttl �?summary �?tags �?
rule_form �?scope �?stability �?verifiability �?depends_on �?
supersedes �?superseded_by �?derived_from �?related_adr �?
safety_level �?evolution_policy �?
ai_autonomy �?provenance �?author_agent �?
governance_family �?ai_capability_slot �?ai_autonomy_level_planned �?ai_employee_count_planned �?
blueprint_refs �?compliance_tags �?human_override �?
last_reviewed_by �?review_status �?category �?domain �?custom_*
```

### 2.4 YAML 文件特殊规则

- `status` 使用小写：`active` / `draft` / `deprecated`（仅 3 值，`superseded` 已废弃——见 status-vocabulary.yaml deprecated_values�?
- 必须包含 `schema_version` 字段
- 日期字段使用 ISO 8601 格式

### 2.5 �?doc_type 分类的必填字段清�?

> 以下清单仅适用�?`01_policies_and_standards/` 目录下的文件�?
> 其他目录的文件仍�?§2.2 分阶段闸门执行�?

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
| `tags` | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | �?| 🟡 | 🟡 | 🟡 | 🟡 |
| `rule_form` | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 |
| `scope` | 🔴 | 🔴 | 🟡 | �?| 🔴 | �?| 🟡 | 🔴 | 🟡 | 🟡 |
| `stability` | 🔴 | 🔴 | 🟡 | �?| 🔴 | �?| 🟡 | 🔴 | 🔴 | 🟡 |
| `verifiability` | 🟡 | 🟡 | 🔴 | �?| 🟡 | �?| �?| �?| 🟡 | �?|
| `depends_on` | 🟡 | 🟡 | 🟡 | �?| 🟡 | �?| 🟡 | 🟡 | 🟡 | �?|
| `valid_from` | 🟡 | 🟡 | �?| �?| 🟡 | �?| 🟡 | 🟡 | 🟡 | 🟡 |
| `supersedes` | �?| �?| �?| �?| �?| �?| �?| �?| �?| �?|
| `superseded_by` | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| `derived_from` | �?| �?| �?| �?| �?| �?| �?| �?| �?| �?|
| `evolution_policy` | 🟡 | 🟡 | �?| �?| 🟡 | �?| �?| 🟡 | �?| 🟡 |
| `ai_autonomy` | 🟡 | 🟡 | 🟡 | �?| 🟡 | �?| 🟡 | 🟡 | 🟡 | 🟡 |

> 🔴 = 必填 | 🟡 = 条件必填 | �?= 可�?

**条件必填说明**�?

| 字段 | 条件 |
|------|------|
| `tags` | �?`scope: layer` 时必填，需标注所属层 |
| `layer` | register/ADR 如为全局型则�?`cross_layer`，层域型填对应层 |
| `classification` | register/ADR 如含敏感信息则必�?`confidential` |
| `verifiability` | operational_rule 必填（操作规程必须可验证�? construction_plan 有可验证产出物时必填 |
| `depends_on` | 当文件依赖其他文件才能执行时必填 |
| `valid_from` | policy/standard/protocol/ADR/blueprint/construction_plan/roadmap 有生效日期时必填 |
| `evolution_policy` | policy/standard/protocol/blueprint/roadmap 有演进策略时必填 |
| `ai_autonomy` | 涉及 AI 操作权限时必�?|

**受控词表速查**�?

| 字段 | 合法�?|
|------|--------|
| `rule_form` | `declarative` / `procedural` / `data` / `structural` |
| `scope` | `global` / `domain` / `layer` / `module` |
| `stability` | `frozen` / `stable` / `evolving` / `volatile` |
| `verifiability` | `automated` / `manual` / `inspection` |

### 2.6 一致性约�?

> 以下约束确保 frontmatter 各字段之间不矛盾。AI �?frontmatter 时必须逐项检查�?

| # | 约束 | 说明 |
|---|------|------|
| 1 | `stability: frozen` �?`ai_autonomy: immutable_core` | 冻结文件 AI 不可修改 |
| 2 | `stability: volatile` �?`ai_autonomy` �?`immutable_core` | 易变文件不可能是不可修改�?|
| 3 | `doc_type: policy` �?`rule_form: declarative` | policy 必须是声明式 |
| 4 | `doc_type: standard` �?`rule_form: declarative` | standard 必须是声明式 |
| 5 | `doc_type: operational_rule` �?`rule_form: procedural` | operational_rule 必须是过程式 |
| 6 | `doc_type: register` �?`rule_form: data` | register 必须是数据形�?|
| 7 | `doc_type: template` �?`rule_form: structural` | template 必须是结构形�?|
| 8 | `doc_type: adr` �?`rule_form: declarative` | ADR 是声明式决策记录（对�?Nygard ADR 原始定义�?|
| 9 | `doc_type: blueprint` �?`rule_form: structural` | blueprint 是结构化设计规范（对�?TOGAF Architecture Definition Document�?|
| 10 | `doc_type: construction_plan` �?`rule_form: structural` | construction_plan 是结构化执行计划（对�?ITIL Change Enablement Plan�?|
| 11 | `doc_type: roadmap` �?`rule_form: declarative` | roadmap 是声明式方向规划，AI 不执�?roadmap 本身 |

> **架构公民原则（避免误判）**�?
> - 约束 #1 是单向的（`frozen` �?`immutable_core`），�?*逆面不成�?*：`stability: stable` + `ai_autonomy: immutable_core` 是合法组合（�?PS-STD-003——稳定但 AI 不可修改的核心规则）
> - `stability` 描述文件�?内容变更频率"，`ai_autonomy` 描述"谁有权改"——两者正交不耦合
> - 合法映射光谱�?
>   - `frozen` �?`immutable_core`（强制）
>   - `stable` �?`immutable_core` �?`human_gated`（均合法�?
>   - `evolving` �?`human_gated` �?`ai_modifiable`（均合法�?
>   - `volatile` �?不能�?`immutable_core`（约�?#2�?

### 2.7 frontmatter 模板

> **SSoT：frontmatter 模板的唯一真源�?`templates/` 目录下的骨架文件�?*
> AI 创建新文件时，从 `templates/` 目录下对应的骨架文件复制 frontmatter，填入具体值�?
>
> 本注册表不再重复定义模板内容。模板文件清单和格式�?[templates/](01_policies_and_standards/templates/) 目录�?

### 2.8 frontmatter 禁止行为

| # | 禁止 | 原因 |
|---|------|------|
| 1 | 禁止 `doc_type` �?`rule_form` 矛盾（如 policy �?procedural、operational_rule �?declarative�?| 全部约束�?§3.6 #5（跨域禁�?§2.8 与领域专属禁�?§3.6 互补不重叠） |
| 2 | 禁止 `stability: frozen` �?`ai_autonomy: ai_modifiable` | 冻结文件 AI 不可修改 |
| 3 | 禁止省略 `rule_form` 字段（Active 状态以上） | rule_form �?Active+ 必填字段 |
| 4 | 禁止使用未在 §2.1 注册的字段名 | 所有字段必须先注册再使�?|
| 5 | 禁止 `scope` �?`layer` 矛盾 | `scope: layer` �?`layer` 不能�?`cross_layer` |
| 6 | 禁止 `verifiability: inspection` �?`doc_type: operational_rule` | 操作规程必须可自动或手动验证，不能只靠目视检�?|

---

## 3. doc_type 受控词表

### 3.1 设计原则

1. **自下而上归纳**：词表从项目 230+ 文件的实际使用中归纳，不是拍脑袋定的
2. **短名优先**：用 `standard` 而非 `governance_standard`，靠 `layer` 字段区分领域
3. **AI 可记�?*：每种类型有明确�?AI 查询关键词，AI 无需查表即可判断
4. **可扩�?*：新�?doc_type 需提决策记录（MOD-KB-001 §3.9.5），审批后更新本文件

### 3.2 完整受控词表

> **Canonical SSoT**：[`_registry/vocabularies/doc_type-vocabulary.yaml`](../_registry/vocabularies/doc_type-vocabulary.yaml)
>
> 全项�?27 �?doc_type。以下为快速速查——完整定义（definition、allowed_directories、forbidden_directories、required_fields、ai_keywords、deprecated_values 等）请查阅词汇表 YAML�?
>
> **`01_policies_and_standards/` 子集�?3 种）**�?
> `policy` `standard` `operational_rule` `register` `index` `protocol` `template` `terminology` `vocabulary` `contract` `reference` `gate` `schema`
>
> **其他目录�?4 种）**�?
> `adr` `blueprint` `construction_plan` `design` `plan` `roadmap` `readme` `log` `knowledge_entry` `audit_report` `service_spec` `architecture_view` `declaration` `config`
>
> **SSoT 铁律**：vocabulary YAML = 唯一真源，本 Markdown = 指路牌。冲突时�?YAML 为准。新�?废弃 doc_type 一律先�?YAML 操作——本表不需要手动同步�?

#### 3.2.1 `01_policies_and_standards/` 子集�?3 值）

> 全项目有 27 �?doc_type，但 `01_policies_and_standards/` 目录�?*只使用以�?13 �?*�?
> 其他 doc_type（如 `blueprint`、`construction_plan`、`roadmap`、`knowledge_entry`）属于其他目录，不在此处使用�?
> **例外**：`templates/` 下的模板文件不受�?13 值子集约束——模�?doc_type 取目标文档类型�?
> 例如 `blueprint-template.md` �?`doc_type: blueprint` 合法（它为蓝图提供模板，�?doc_type 表达的是目标，不是文件本身的分类）�?

| # | doc_type | 含义 | 对应目录 | rule_form |
|---|----------|------|---------|-----------|
| 1 | `policy` | 强制约束 | `governance/` | 声明�?|
| 2 | `standard` | 推荐做法 | `governance/` | 声明�?|
| 3 | `operational_rule` | 操作规程 | `operational/` | 过程�?|
| 4 | `register` | 登记�?| `_registry/` | 数据 |
| 5 | `index` | 目录索引 | 所有目�?| 声明�?|
| 6 | `protocol` | 协议 | `governance/` | 声明�?|
| 7 | `terminology` | 术语�?| `meta/` | 数据 |
| 8 | `template` | 模板 | `templates/` | 结构 |
| 9 | `vocabulary` | 受控词表 | `_registry/vocabularies/` | 数据 |
| 10 | `contract` | 验证契约 | `_registry/contracts/` | 数据 |
| 11 | `reference` | 参考文�?| `_registry/catalogs/` | 数据 |
| 12 | `gate` | 质量门禁 | `_registry/` | 声明�?|
| 13 | `schema` | Schema 定义 | `_registry/schemas/` | 数据 |

#### 3.2.2 policy vs standard vs operational_rule 判据

> **问一个问题就能区�?*：这个文件是�?定规�?还是�?教操�?�?

| 文件在做什�?| doc_type | 归属 | 例子 |
|------------|----------|------|------|
| 定义"什么是对的/错的"——必须、禁止、不�?| `policy` | `governance/` | "所�?API 密钥必须存储在环境变量中" |
| 定义"推荐怎么�?——应该、建议、最佳实�?| `standard` | `governance/` | "建议使用 Pydantic v2 做数据验�? |
| 定义"按步骤执�?——步�?1�?�? | `operational_rule` | `operational/` | "Step 1: 检�?.env �?Step 2: 验证密钥格式" |

**3 个测�?*�?

| 测试 | policy | standard | operational_rule |
|------|--------|----------|-----------------|
| 删掉步骤描述，规则还成立吗？ | �?成立 | �?成立 | �?不成立（没有步骤就没法执行） |
| 违反了会怎样�?| 🔴 严重（红线） | 🟡 不推荐（但不是红线） | 🔴 操作出错（按步骤才能避免�?|
| 换一个人/AI 执行，结果一样吗�?| �?一样（规则不变�?| ⚠️ 可能不同（推荐做法有弹性） | �?一样（步骤固定�?|

#### 3.2.3 protocol vs policy 的区�?

| 维度 | policy | protocol |
|------|--------|----------|
| 主体 | 单方约束 | 多方交互 |
| 核心问题 | "必须/禁止什�? | "谁先做什么，然后谁做什�? |
| 例子 | "密钥必须加密存储" | "交接协议：发出方 �?审核�?�?接收�? |
| 判断标准 | 只涉及一�?| 涉及两方以上的交互时�?|

**简单判�?*：如果文件描述的�?谁→谁→�?的交互流程，�?`protocol`；如果只�?必须/禁止 X"，用 `policy`�?

### 3.3 doc_type �?layer 的联�?

`doc_type` 回答"这是什么品�?，`layer` 回答"属于哪个领域"。两者组合定位文档�?

> 完整映射表见 vocabulary YAML 各条目的 `allowed_directories` 字段�?
> 以下为典型示例（非完整枚举）�?

| 组合示例 | 含义 |
|---------|------|
| `doc_type: policy` + `layer: cross_layer` | 全局强制规则 |
| `doc_type: standard` + `layer: cross_layer` | 全局推荐做法 |
| `doc_type: standard` + `layer: l04_ml_platform` | 机器学习层推荐做�?|
| `doc_type: blueprint` + `layer: l00_data_source` | 数据源层蓝图 |
| `doc_type: construction_plan` + `layer: l00_data_source` | 数据源层施工�?|
| `doc_type: architecture_view` + `layer: cross_layer` | 跨层正式架构视图 |
| `doc_type: plan` + `layer: cross_layer` | 跨层任务�?|
| `doc_type: roadmap` + `layer: cross_layer` | 跨层路线�?|

### 3.4 doc_type 与存放路径的映射

> Canonical SSoT �?vocabulary YAML 各条目的 `allowed_directories` �?`forbidden_directories` 字段�?
> 以下为关键规则速查——不含已废弃类型�?

| doc_type | 应存放的目录 | 禁止存放的目�?|
|----------|------------|--------------|
| `policy` | `01_policies_and_standards/governance/` | `03_modules/` `08_knowledge/` |
| `standard` | `01_policies_and_standards/governance/` `08_knowledge/` | `03_modules/` |
| `adr` | `02_enterprise_architecture/adr/` | 其他所有目�?|
| `blueprint` | `03_modules/l<NN>_<layer>/<module>/` | `01_policies_and_standards/` |
| `construction_plan` | `03_modules/l<NN>_<layer>/<module>/` | `01_policies_and_standards/` |
| `architecture_view` | `02_enterprise_architecture/target-architecture/` | `01_policies_and_standards/` `03_modules/` |
| `design` | `02_enterprise_architecture/` | | `01_policies_and_standards/` `03_modules/` |
| `operational_rule` | `01_policies_and_standards/operational/` | `governance/` `03_modules/` |
| `protocol` | `01_policies_and_standards/governance/` | `03_modules/` |
| `register` | `01_policies_and_standards/_registry/` | `03_modules/` |
| `vocabulary` | `01_policies_and_standards/_registry/vocabularies/` | `governance/` `operational/` |
| `contract` | `01_policies_and_standards/_registry/contracts/` | `governance/` `operational/` |
| `template` | `01_policies_and_standards/templates/` | �?|
| `terminology` | `01_policies_and_standards/meta/` | �?|
| `index` | 各目录根 | �?|
| `readme` | 各目录根 | �?|
| `log` | `09_audit/` | | `03_modules/` |
| `knowledge_entry` | `08_knowledge/` | `01_policies_and_standards/` |
| `audit_report` | `09_audit/` | �?|
| `service_spec` | `03_modules/_b_track_interfaces/` | �?|
| `plan` | `01_policies_and_standards/` | | �?|
| `roadmap` | `01_policies_and_standards/` | | �?|
| `declaration` | `docs/`（项目根�?| `01_policies_and_standards/` |

#### 3.4.1 防幻觉三向映射（doc_type �?directory �?rule_form�?

> AI 判断"这个文件该放哪、该是什么格�?时，查这张表。三个维�?*一一对应**，不允许交叉�?

| doc_type | 唯一目录 | rule_form | 反向验证 |
|----------|---------|-----------|---------|
| `policy` | `governance/` | 声明�?| governance/ 下只能是 policy / standard / protocol |
| `standard` | `governance/` | 声明�?| 同上 |
| `protocol` | `governance/` | 声明�?| 同上 |
| `operational_rule` | `operational/` | 过程�?| operational/ 下只能是 operational_rule |
| `register` | `_registry/` | 数据 | _registry/ 下只能是 register |
| `template` | `templates/` | 结构 | templates/ 下模板文件的 doc_type 取目标文档类型�?template"作为 doc_type 仅用�?模板的模�?（如本目录结构模板本身）；cookbook template（用于生成目标文档的预填骨架）其 doc_type = 目标类型（如 blueprint-template.md �?doc_type: blueprint）。对标：K8s Helm template 不改 kind �?Template，ITIL 模板不改标题�?"Template" 前缀�?|

### 3.5 新增 doc_type 的流�?

1. 在实际使用中发现现有 27 种无法覆盖的文档类型
2. 提交决策记录（MOD-KB-001 §3.9.5），说明：新类型名称、与现有类型的区别、为什么不能归入现有类�?
3. 决策记录审批通过后，**仅更�?`_registry/vocabularies/doc_type-vocabulary.yaml`**（canonical SSoT）——本文件 §3.2 为速查引用、�?.4 为派生表，不需要手动同�?
4. 校验�?`check_frontmatter_metadata.py` �?YAML 动态加载合法值——无需修改校验代码
5. 同步更新 `frontmatter-schema.json`（自动生成）
5. 在下一�?pre-commit 版本中纳入新值的校验

### 3.6 doc_type 禁止行为

| # | 禁止 | 原因 |
|---|------|------|
| 1 | 禁止�?`governance/` 下使�?`operational_rule` | governance/ 只放声明式，operational_rule 是过程式 |
| 2 | 禁止�?`operational/` 下使�?`policy` �?`standard` | operational/ 只放过程式，policy/standard 是声明式 |
| 3 | 禁止使用旧长名（`governance_standard`、`governance_registry` 等） | 已迁移到短名，旧长名不再合法 |
| 4 | 禁止使用未在本文�?§3.2 注册�?doc_type | 所�?doc_type 必须先注册再使用 |
| 5 | 禁止 `doc_type` �?`rule_form` 矛盾 | 声明�?doc_type 不能配过程式 rule_form，反之亦�?|

---

## 4. status 受控词表（三域分离）

> **核心原则**：文档、任务、知识条目的生命周期不同，状态机不同，枚举值不同�?
> 三个 status 各管各的，不混用、不别名、不合并�?

### 4.1 DocStatus（域 A：文�?frontmatter�?

> **真元规则（Owner 裁定�?026-04-29�?*：DocStatus �?7 种精简�?3 种�?

| status | 含义 | AI 行为 | superseded_by |
|--------|------|--------|:------------:|
| `draft` | 草稿，内容未稳定 | 可参考但不作为权�?| 不需�?|
| `active` | 生效中，当前有效 | 作为权威参考，修改需走变更流�?| 不需�?|
| `deprecated` | 已废弃，不应再使�?| 不再参�?| **必填**（有替代品填路径，无替代品填 `"N/A"`�?|

**选择理由（为什么从 7 种精简�?3 种）**�?

1. **Vibe Coding 语境**：AI 只需要知�?能不能用"——draft（还没好）、active（可以用）、deprecated（不能用了）�? 种状态中 `in_discussion` �?`draft` 的区别、`review_ready` �?`active` 的区别、`accepted` �?`active` 的区别，AI 经常搞混，最终退化成 3 种�?

2. **行业参�?*：MoAI Foundation Specs（AI Agent 开发框架）�?4 种（Draft/Active/Deprecated/Archived）；RAG 系统文档生命周期�?4 种（Active/Deprecated/Archived/Deleted）；OpenTelemetry �?4 种（Development/Stable/Deprecated/Removed）�? 种是最精简的方案�?

3. **废弃原因�?`superseded_by` 字段区分**：不需要靠 status 值来区分"为什么废�?。有 `superseded_by` 路径 = 被取代，`superseded_by: "N/A"` = 单纯过时。IETF RFC 也用 `Obsoleted-by` 字段而非单独�?status 值来区分�?

4. **审阅�?`review_status` 字段单独�?*：项目已�?`review_status` 字段�? 种：unreviewed/reviewed/approved/rejected），不需要在 DocStatus 里重�?`review_ready` �?`accepted`�?

5. **不按 doc_type 分状�?*：真源文件已按域分三套状态机（文�?任务/知识），不需要再按文档类型细分。所有文档类型共用同一�?DocStatus，AI 不需要记"ADR 用这套、blueprint 用那�?�?

**否决方案**�?

| 方案 | 否决理由 |
|------|---------|
| 7 种（旧规则） | AI 经常搞混 `in_discussion`/`draft`、`accepted`/`active`；`review_ready`/`accepted` �?`review_status` 重复；自然退化成 3 �?|
| 5 种（+review_ready�?| �?`review_status` 功能重叠；Confluence 有是因为组织需要经理签字，个人项目不需�?|
| 4 种（+archived�?| `archived` �?`deprecated` �?AI 来说行为一样（都不再参考），区分无意义；归档是文件操作（移动到 archive 目录），不是文档状�?|

**状态流�?*�?

```
draft �?active �?deprecated
  �?                 �?
  └──────────────────┘（重新启用，需 Owner 审批�?
```

**降格规则**�?
- `active` �?`deprecated`：需 Owner 审批 + 填写 `superseded_by`（必填）
- `deprecated` �?`active`：需 Owner 审批（重新启用）
- 禁止跨级降格（`draft` 不能直接�?`deprecated`，必须先升格�?`active`�?

#### 4.1.1 生命周期引用约束（Lifecycle Reference Constraint）—�?026-05-02 新增

> **对标**：Kubernetes Admission Controller（准入控制器拒绝非法请求�?+ ITIL Change Enablement（变更前评估消费者影响）
>
> **动机**�?026-05-02 审计发现 GOV-MOD-002（draft，已升格 active v1.0.0）被 6 �?active 文件量产级引用、GOV-MOD-007（draft，已升格 active v2.1.0）被 registry-of-registries.yaml 引用。status 字段�?depends_on 之间没有互锁机制—�?出生即公�?的默认假设覆盖了 draft 状态的"我还不是正式公民"的真实含义�?

##### MUST 规则

| # | 规则 | 违反后果 |
|---|------|---------|
| **LRC-001** | `status: draft` 的文�?**不得** 被任�?`status: active` 的文件通过 `depends_on` 声明依赖 | 消费者获得的规则可能尚未稳定——AI session 行为漂移 |
| **LRC-002** | `status: draft` 的文�?**不得** 被任�?`status: active` 的文件在正文中作为权威引用（`see X §Y` 形式的规范性引用） | 同上 |
| **LRC-003** | 审批 `draft �?active` 升格时，必须**先检查消费者清�?*——所有已引用该文件的其他文件是否需要同步变�?| 升格后发现消费者与新版不兼容——返工成�?|

##### SHOULD 规则

| # | 规则 |
|---|------|
| **LRC-004** | `draft` 文件�?3 个以上活跃文件引用时，应评估是否已达 `active` 成熟度——实质活跃应升格 |
| **LRC-005** | �?AI session 读到 `draft` 文件被多个活跃文件引用时，应标记�?MEDIUM Finding 提请 Owner 裁定 |

##### 设计意图：为什�?stage �?status 更根�?

当前 `status` 字段�?*描述�?*的——它描述文件当前状态，但不约束文件的交互行为�?
对标 Kubernetes：alpha API 不能�?stable API 依赖——不是因为手动标�?`status: alpha`，而是因为它没通过 graduation gate�?

**未来方向**（beta+）：引入 `lifecycle_stage` 字段，由门禁系统自动推进�?

```
draft_stage  �? blueprint_review  �? construction_review  �? active_stage
  （出生）         （蓝图门通过�?         （施工门通过�?           （生产就绪）
```

`status` �?`lifecycle_stage` 推导�?
- `lifecycle_stage < active_stage` �?`status: draft`（不可被 active 文件引用�?
- `lifecycle_stage >= active_stage` �?`status: active`（可被引用）

> **大白�?*：现在的 status 是自己贴的标签——贴了跟没贴一样。将来的 stage 是门禁系统盖的章——没过蓝图门就是 draft，过了就�?active。这样就不会出现"明明还是个草稿却被到处引�?的尴尬了�?

##### `lifecycle_stage` 字段定义（beta 落地�?

| stage �?| 含义 | 对应的门 | 等价 status |
|:---------|:-----|:--------|:-----------:|
| `draft` | 草稿阶段——内容未稳定，AI 自由编辑 | �?| `draft` |
| `blueprint_reviewed` | 已通过蓝图评审——设计方向已确认 | GATE-BP-001（蓝图完整性门�?| `draft`（不可被 active 引用�?|
| `construction_reviewed` | 已通过施工评审——实现方案已验证 | GATE-CT-001（施工可执行性门�?| `draft`（不可被 active 引用�?|
| `active` | 生产就绪——可供全项目引用 | GATE-AD-001（active 准入门） | `active` |

**流转约束**：`lifecycle_stage` 只进不退（只�?forward，不�?rollback），对标 Kubernetes API version 的单向演进策略�?

### 4.2 TaskStatus（域 B：任务系统）

> 代码真源：`src/zephyr/shared/schemas.py` `TaskStatus` 枚举

| status | 含义 | 终态？ |
|--------|------|:------:|
| `PENDING` | 待执�?| �?|
| `IN_PROGRESS` | 执行�?| �?|
| `COMPLETED` | 已完�?| �?|
| `VERIFIED` | 已验�?| �?|
| `FAILED` | 执行失败 | �?|
| `BLOCKED` | 被阻�?| �?|
| `WAITING` | 等待�?| �?|
| `READY` | 就绪待执�?| �?|
| `RETRY` | 重试�?| �?|
| `CANCELLED` | 已取�?| �?|

**状态流�?*（代码真源：`task_repo.py`）：

```
PENDING �?IN_PROGRESS �?COMPLETED �?VERIFIED
  �?         �?             �?
BLOCKED    FAILED         CANCELLED
  �?         �?
 READY     RETRY �?IN_PROGRESS
WAITING �?READY
```

### 4.3 KeStatus（域 C：知识条目）

> 代码真源：`src/zephyr/kb/kb_repo.py` `KeStatus` 枚举

| status | 含义 | 终态？ | 向量可见�?|
|--------|------|:------:|:---------:|
| `DRAFT` | 草稿 | �?| �?|
| `SUBMITTED` | 已提交待�?| �?| �?|
| `REVIEWED` | 已审�?| �?| �?|
| `ACCEPTED` | 已接�?| �?| �?|
| `INDEXED` | 已索�?| �?| �?|
| `VERIFIED` | 已验�?| �?| �?|
| `REJECTED` | 已否�?| �?| �?|
| `DEPRECATED` | 已废�?| �?| �?|
| `SUPERSEDED` | 已取�?| �?| �?|
| `ARCHIVED` | 已归�?| �?| �?|

**状态流�?*（代码真源：`kb_repo.py`）：

```
DRAFT �?SUBMITTED �?REVIEWED �?ACCEPTED �?INDEXED �?VERIFIED
                     �?         �?         �?        �?
                  REJECTED   REJECTED   REJECTED   DEPRECATED �?ARCHIVED
                     �?                             SUPERSEDED �?ARCHIVED
                   DRAFT
```

### 4.4 三域 status 对照�?

| 维度 | DocStatus | TaskStatus | KeStatus |
|------|-----------|------------|----------|
| �?| A（文档） | B（任务） | C（知识） |
| 值数�?| 3 | 10 | 10 |
| 大小�?| 枚举值小�?/ 标识符大�?| 全大�?| 全大�?|
| 终�?| deprecated / superseded | VERIFIED / CANCELLED | ARCHIVED |
| 代码真源 | 本文�?§4.1 | `src/zephyr/shared/schemas.py` | kb_repo.py |
| 对标专业机构 | MLflow: status | IETF: task_status | OpenLineage: lifecycleState |

### 4.5 大小写约定：枚举值小�?+ 标识符大�?

> **真元规则（Owner 裁定�?026-04-29�?*：frontmatter 字段值的大小写取决于字段类型——枚举值统一小写，标识符统一大写�?

#### 4.5.1 两条核心规则

| 字段类型 | 大小�?| 例子 | 判断标准 |
|---------|:------:|------|---------|
| **枚举�?* | **全小�?* | `status: active`、`doc_type: standard`、`layer: l01_infrastructure`、`classification: confidential`、`ai_autonomy_level: immutable_core` | �?*有限选项**里选一�?|
| **标识�?* | **全大�?* | `module_id: L00-DS-001`、`module_id: ADR-0011`、`module_id: PS-STD-001` | 每个�?*唯一**，不是从选项里选的 |

#### 4.5.2 为什么枚举值用小写�?

1. **Vibe Coding 语境**：本项目�?frontmatter 主要�?AI 读取、AI 写入、AI 工作。AI 做字符串比较时严格区分大小写，`Active != active`，大小写不一致是最常见�?AI 识别错误来源。统一小写消除了这个出错点�?

2. **零认知负�?*：枚举值全小写，不需要记"哪个首字母大写、哪个不大写"。AI 和人类都不用想�?

3. **与文件命名规则一�?*：项目已裁定所有文件名和文件夹名全小写（kebab-case）。枚举值也全小写，跟文件命名规则保持一致�?

4. **行业参�?*：OpenSSF ADR-0013 讨论�?YAML 枚举值的 4 种大小写方案（Title Case / kebab-lower / camelCase / PascalCase），最终选择 Title Case 的理由是"为人类作者优化，视觉区分键和�?。但本项目的场景不同——AI 是主要消费者，"�?AI 优化"�?为人类视觉优�?更重要。Hugo/Jekyll 等工具也采用全小写方案�?

5. **pre-commit 校验**：校验脚本只需匹配一种写法，不需要同时接�?`Active` �?`active`，简化了门禁逻辑�?

#### 4.5.3 为什么标识符用大写？

1. **可搜索�?*：大写标识符在文本中**一眼就能认出来**。在一大段文字里看�?`L00-DS-001`，立刻知道这是一个模块编号；看到 `l00-ds-001`，可能以为是一段代码或路径。AI 用正�?`L\d{2}-[A-Z]+-\d{3}` 搜索，精准无歧义�?

2. **与枚举值视觉区�?*：枚举值小写、标识符大写，两种字段在 frontmatter 中天然区分。AI 读到 `status: active` 知道是枚举值，读到 `module_id: L00-DS-001` 知道是标识符，不需要额外判断�?

3. **专业机构对标**：Linux Kernel（文件名小写 + �?常量大写）、Rust RFCs（文件名 `rfc-0001-*.md` 小写 + 标识�?`RFC-0001` 大写）、Google Engineering Practices（文件名小写 + 标识符大写）、HGNC 人类基因命名委员会（基因符号只允许大写字�?数字，如 `BRCA1`、`TP53`）。本项目 Stage F 已正式对标这三家机构（见 handoff-log §Stage F 工程级贡献）�?

4. **正交性原�?*：文件名是人类索引（小写），module_id 是机器索引（大写），两者规范独立不耦合。这�?Stage F 裁定的宪法条款（file-naming-standard.md §2.2.3），避免两套索引互相锁死�?

5. **1500+ 模块规模**：在 1500 个模块的规模下，标识符必须能被快速定位。大�?+ 连字符分隔的格式（`L00-DS-001`）比全小写（`l00-ds-001`）在 grep/ripgrep 中误匹配率更低�?

#### 4.5.4 完整字段分类�?

| 字段 | 类型 | 大小�?| 示例 |
|------|------|:------:|------|
| `status` | 枚举�?| 小写 | `draft` `active` `deprecated` |
| `doc_type` | 枚举�?| 小写 | `standard` `policy` `blueprint` |
| `classification` | 枚举�?| 小写 | �?A：`public` `confidential`（推荐）；域 B 任务另见 §4.6 / §7.1 |
| `layer` | 枚举�?| 小写 | `l01_infrastructure` `cross_layer` |
| `ai_autonomy_level` | 枚举�?| 小写 | `immutable_core` `ai_modifiable` `human_gated` |
| `ttl` | 枚举�?| 小写 | `permanent` `30d` `7d` `session` `periodic_review_90d` |
| `language` | 枚举�?| 小写 | `zh` `en` `zh_en` |
| `module_id` | **标识�?* | **大写** | `L00-DS-001` `ADR-0011` `PS-STD-001` `KE-016` |
| `title` | 自由文本 | 自然语言 | `编码安全规范` |
| `version` | 语义版本 | 数字 | `1.0.0` |

#### 4.5.5 否决方案

| 方案 | 否决理由 |
|------|---------|
| `.md` 首字母大�?+ `.yaml` 小写（旧规则�?| 两套规则增加认知负担；AI 容易写错；宪法文件自身都写成了小写，说明规则不可执行 |
| Title Case（OpenSSF 方案�?| 为人类视觉优化，不为 AI 优化；AI 严格区分大小写，Title Case 反而增加出错概�?|
| PascalCase（Open Data Fabric 方案�?| 多词值可读性差（`NotApplicable`）；AI 需要额外映射逻辑 |
| 全部统一大写 | 枚举值大写（`STATUS: ACTIVE`）增�?AI 出错概率；跟文件名小写规则冲突；无专业机构先�?|
| 全部统一小写（包括标识符�?| 标识符小写（`l00-ds-001`）跟文件路径混淆；AI 无法快速区�?这是编号还是路径"；跟 Stage F 正交性裁定矛�?|

> TaskStatus �?KeStatus 在代码中全大写（`PENDING` / `COMPLETED` / `DRAFT` / `INDEXED` 等）�?
> 这是 Python 枚举的惯例，�?frontmatter 枚举值无关——它们是�?B/C 专用，不�?frontmatter 中使用�?
> pre-commit 校验时，�?A 枚举值只接受小写，标识符只接受大写�?

### 4.6 classification：域 A（文档）与域 B（任务）分层

> **2026-05-05 裁定（闭�?§4 �?§7 冲突�?*：不再执行「删�?`INTERNAL` / 强制枚举二分」的迁移。文档与任务对敏感度粒度需求不同—�?*分层真源**，禁止混读�?

| 上下�?| 合法�?| 真源 |
|--------|--------|------|
| **�?A** 文档 frontmatter | **`public` / `confidential`（推荐）**；历史文件可暂留 `internal` | 本表 + frontmatter 校验 |
| **�?B** `Task.classification` | **`public` / `internal` / `confidential`（三值）** | **`src/zephyr/shared/schemas.py`** `Classification` + `_registry/vocabularies/classification-vocabulary.yaml`；字段表�?**§7.1** |

**�?A 推荐二分**：降�?Vibe Coding �?AI 决策成本�? 
**�?B 使用三�?*：区分「项目内默认可见」（`internal`）与「明确机密」（`confidential`）；与代码枚举及 SQLite 对齐�? 
**�?`ai_autonomy_level` 正交**（不变）：`classification` 管外传边界，`ai_autonomy_level` 管「谁能改」�?

**以下�?2026-04-29 讨论的「仅文档域二分」论据摘�?*（仍适用�?*仅填 frontmatter 的文�?*，不推翻�?B 三值）�?

- 纯公开/不公开判断在部分商业合规语境中更简单�? 
- 军方 `secret` 分级本项目不使用�?

**已废止的叙述**：曾计划删除枚举 `INTERNAL`、批量把 `internal` 文件改为 `confidential`—�?*已撤销**；以本表分层为准�?

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

### 5.2 DOMAIN 注册�?

#### 5.2.1 已注�?DOMAIN�?3 个）

| DOMAIN | 含义 | 对应目录 | 注册来源 |
|--------|------|---------|---------|
| `PS` | Policies & Standards | `01_policies_and_standards/` | v4.4.0 已注�?|
| `EA` | Enterprise Architecture | `02_enterprise_architecture/` | v4.4.0 已注�?|
| `MOD` | Module | `03_modules/` | v3.0.0 已注�?|
| `KE` | Knowledge Entries | `08_knowledge/` | v4.4.0 已注�?|
| `AR` | Audit Reports | `09_audit/` | v4.4.0 已注�?|
| `CM` | Compliance | `10_compliance/` | v4.4.0 已注�?|
| `AE` | AI Engineering | `03_modules/_b_track_interfaces/` | v4.4.0 已注�?|
| `AG` | AI Governance | `01_policies_and_standards/governance/ai/` | v4.4.0 已注�?|
| `DW` | ~~Development Workspace~~ 已删�?| `—` | `19_development_workspace/` 已于 2026-05-02 删除 |
| `L{XX}` | 业务层（L00-L13�?| `src/zephyr/l{xx}_*/` | v4.4.0 已注�?|
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
| 大写字母 + 连字�?| DOMAIN 部分用大写，层级用连字符分隔 | `GOV-SEC` | `gov-sec`, `GOV_SEC` |
| 层级编码 | 顶级域（PS/GOV/OPS/DOM�? 子域缩写 | `GOV-SEC` | `SECURITY` |
| 子域缩写 2~4 字符 | 短到可读，长到无歧义 | `SEC`, `CMP`, `ARCH` | `SECURITY`, `COMPLIANCE` |
| 与物理目录一一对应 | 看到前缀就知道文件在�?| `GOV-SEC` �?`governance/security/` | 前缀和目录不对应 |

#### 5.2.3 顶级域层级关�?

```
PS  ── meta/（元标准层，~10 文件，固定不增长�?
 �?
GOV ── governance/（全局治理层，~50 文件�?
 �?  ├── GOV-DOC  ── governance/document/
 �?  ├── GOV-AI   ── governance/ai/
 �?  ├── GOV-TASK ── governance/task/
 �?  ├── GOV-SEC  ── governance/security/
 �?  ├── GOV-CMP  ── governance/compliance/
 �?  ├── GOV-ARCH ── governance/architecture/
 �?  ├── GOV-DATA ── governance/data/
 �?  └── GOV-MOD  ── governance/module/
 �?
OPS ── operational/（全局操作层，~10 文件�?
 �?  ├── OPS-VC   ── operational/vibe_coding/
 �?  ├── OPS-DEV  ── operational/devops/
 �?  └── OPS-MIG  ── operational/migration/
 �?
DOM ── domains/（层域治理，初始 4 层，按需扩展�?
     ├── DOM-L00  ── domains/L00_data_source/
     ├── DOM-L02  ── domains/L02_alpha_factor/
     ├── DOM-L04  ── domains/L04_risk_management/
     └── DOM-L07  ── domains/L07_post_trade_analytics/
```

#### 5.2.4 新增 DOMAIN 的审批条�?

| 条件 | 说明 |
|------|------|
| 对应目录已存在或即将创建 | 前缀不能凭空存在 |
| 缩写不与现有缩写冲突 | 检�?§5.2.1 DOMAIN 注册�?|
| 至少�?1 个文件需要该 DOMAIN | 不建空前缀 |
| 在本文件 §5.2.1 中注�?| DOMAIN 定义的唯一真源是本文件 |

#### 5.2.5 容量验证

| DOMAIN | 当前文件�?| experimental 目标 | 极限容量（NNN=999�?| 够不�?|
|--------|:--------:|:----------:|:-----------------:|:-----:|
| PS-STD | 9 | 10 | 999 | �?|
| PS-REG | 1 | 2 | 999 | �?|
| GOV-DOC | 8 | 8 | 999 | �?|
| GOV-AI | 5 | 7 | 999 | �?|
| GOV-TASK | 3 | 3 | 999 | �?|
| GOV-SEC | 0 | 3 | 999 | �?|
| GOV-CMP | 0 | 2 | 999 | �?|
| GOV-ARCH | 2 | 3 | 999 | �?|
| GOV-DATA | 0 | 3 | 999 | �?|
| GOV-MOD | 7 | 7 | 999 | �?|
| OPS-VC | 3 | 5 | 999 | �?|
| OPS-DEV | 1 | 2 | 999 | �?|
| OPS-MIG | 1 | 1 | 999 | �?|
| DOM-L{XX}（每层） | 0~2 | 2~10 | 每层 999 | �?|

**总容�?*�?4 �?DOMAIN × 999 = 13986 个编号，远超峰值需求。如果某�?DOMAIN 超过 999，扩展为 NNNN（四位），格式不变�?

### 5.3 TYPE 注册�?

#### 5.3.1 已注�?TYPE�? 个）

| TYPE | 含义 | 示例 | 注册来源 |
|------|------|------|---------|
| `STD` | Standard（标准） | PS-STD-001 | v4.4.0 已注�?|
| `REG` | Registry（注册表�?| PS-REG-001 | v4.4.0 已注�?|
| `ADR` | Architecture Decision Record | ADR-0010 | v4.4.0 已注�?|
| `DSG` | Design（设计） | EA-DSG-001 | v4.4.0 已注�?|
| `PLAN` | Plan（计划） | CP-PLAN-001 | v4.4.0 已注�?|
| `LOG` | Log（日志） | EA-LOG-001 | v4.4.0 已注�?|
| `POL` | Policy（策�?政策�?| GOV-SEC-POL-001 | v5.0.0 新增 |
| `RBK` | Runbook（操作手册） | OPS-VC-RBK-001 | v5.0.0 新增 |

#### 5.3.2 TYPE 是否必填�?

**不强制�?* �?DOMAIN 已经足够区分文件类型时，TYPE 可以省略�?

| 场景 | 是否需�?TYPE | 示例 |
|------|:----------:|------|
| `meta/` 下的文件 | 需要（区分 STD �?REG�?| PS-STD-001, PS-REG-001 |
| `governance/` 下的文件 | **不需�?*（GOV-SEC 已经足够定位�?| GOV-SEC-001 |
| `operational/` 下的文件 | **不需�?*（OPS-VC 已经足够定位�?| OPS-VC-001 |
| `domains/` 下的文件 | **不需�?*（DOM-L04 已经足够定位�?| DOM-L04-001 |

**简化规�?*：治理文件编号使�?`<DOMAIN>-<NNN>` 格式（省�?TYPE），只有 `meta/` 下的文件保留 `<DOMAIN>-<TYPE>-<NNN>` 格式�?

### 5.4 编号分配铁律

| # | 铁律 | 说明 |
|---|------|------|
| 1 | **每个 DOMAIN 独立编号** | GOV-SEC-001 �?GOV-AI-001 是两个不同文件，互不冲突 |
| 2 | **连续分配** | 新文件取当前 DOMAIN 下最大编�?+ 1 |
| 3 | **跳号保留，禁止回�?* | 废弃编号标记�?skipped，永不回�?|
| 4 | **append-only** | 编号一旦分配，永不删除、不重编 |
| 5 | **迁移 = 重新编号** | 文件迁移到新目录时，module_id 必须按新 DOMAIN 重新分配 |
| 6 | **关联靠字段不靠编�?* | �?`superseded_by` / `refines` 表达关系，编号只承载唯一标识 |
| 7 | **禁止嵌套编号** | 不得创建 GOV-SEC-001-01 这种子编�?|
| 8 | **前缀长度 �?2 字符** | 超长前缀可读性差 |

### 5.5 layer 字段格式

| 场景 | 格式 | 示例 |
|------|------|------|
| 业务�?| `l{xx}_{snake_case}` | `l00_data_source` `l04_ml_platform` |
| 跨层 | `cross_layer` | 治理标准、架构视�?|
| 基础设施 | `infra_{name}` | `infra_ci` `infra_precommit` |
| 前端 | `fe_l{n}` | `fe_l1` `fe_l2` |

### 5.6 module_id �?L{XX} 层编号的关系

`unified-numbering-standard.md` 定义�?`L{XX}-{ABBR}-{NNN}` 格式用于**业务层模�?*（L00-L13）�?
本节定义�?`<DOMAIN>-<TYPE>-<NNN>` 格式用于**治理/标准/知识类文�?*�?

两者不冲突，通过 DOMAIN 区分�?

| 场景 | 用哪个格�?| 示例 |
|------|----------|------|
| 业务层模�?| `L{XX}-{ABBR}-{NNN}` | `L00-DS-001` `L04-MLP-001` |
| 治理标准文档 | `PS-STD-{NNN}` | `PS-STD-001` |
| ADR | `ADR-{NNNN}` | `ADR-0002` `ADR-0010` |
| 知识条目 | `KE-{NNN}` | `KE-016` `KE-501` |
| 审计报告 | `AR-RPT-{NNN}` | `AR-RPT-001` |

### 5.7 废弃格式迁移说明

以下格式**全部废弃**，对应文件在施工 beta 统一改为新前缀�?

| 废弃格式 | 文件 | �?ID | 废弃原因 |
|---------|------|-------|---------|
| `STD-NUM-001` | unified-numbering-standard.md | GOV-DOC-001 | 不符�?`<DOMAIN>-<TYPE>-<NNN>` 格式；DOMAIN 应为 GOV-DOC |
| `STD-TASK-CARD-001` | task-card-standard.md | GOV-TASK-001 | 不符合格式；DOMAIN 应为 GOV-TASK |
| `PSP-DRAFTS-AUDITS-ARBITRATION-001` | drafts-audits-arbitration-protocol.md | GOV-DOC-011�?026-05-01 废除�?| 超长前缀；不符合格式；文件已废除 |
| `PSP-AI-AUTONOMY-AUTHORITY-001` | ai-autonomy-authority-registry.md | GOV-AI-001 | 超长前缀；不符合格式 |
| `DW-HANDOFF-STD-001` | handoff-protocol.md | GOV-AI-008 | 不符合格式；DW 域用于开发工作区，不用于治理文件 |

**保留不动的格�?*（已在项目中广泛引用）：

| 保留格式 | 文件 | 理由 |
|---------|------|------|
| `PS-STD-000` ~ `PS-STD-007` | meta/ �?8 个文�?| 符合 `<DOMAIN>-<TYPE>-<NNN>` 格式�? 个文件广泛引�?|
| `PS-REG-001` | rule-registry.md | 符合格式 |
| `ADR-0001` ~ `ADR-0041` | ADR 文件 | ADR 已冻结，独立编号空间 |

### 5.8 完整编号分配�?

> 以下为已分配�?module_id，按目录分组�?可用"槽位汇总在每段末尾�?

| 目录 | 前缀 | 已分配编�?| 可用编号 |
|------|------|----------|---------|
| `meta/` | PS-STD | 000, 001, 002, 003, 004, 006, 009, 011, 012 | 005, 007, 008, 010 |
| `meta/` | META | GLS-001, IDX-001 | �?|
| `meta/` | PS-REG | 001 | �?|
| `governance/document/` | GOV-DOC | 001, 002, 003, 004, 005, 006, 007, 008, 009 | �?|
| `governance/ai/` | GOV-AI | 001, 002, 003, 004, 005, 006, 007 | �?|
| `governance/task/` | GOV-TASK | 001, 002, 003, 004, 005 | �?|
| `governance/security/` | GOV-SEC | 001, 002, 003 | �?|
| `governance/compliance/` | GOV-CMP | 001, 002 | �?|
| `governance/architecture/` | GOV-ARCH | 001, 002, 003 | �?|
| `governance/data/` | GOV-DATA | 001, 002, 003 | �?|
| `governance/module/` | GOV-MOD | 001, 002, 003, 004, 005 | �?|
| `operational/vibe_coding/` | OPS-VC | 001, 002, 003 | �?|
| `operational/devops/` | OPS-DEV | 001 | �?|
| `operational/migration/` | OPS-MIG | 001 | �?|
| `domains/` | DOM-L## | L00-001~002, L02-001~002, L04-001~002, L07-001~002 | beta 扩展 |

> 详细文件对应用表见各目录�?`index.md`�?

### 5.9 �?module-id-registry.yaml 的矛盾处�?

`module-id-registry.yaml` 当前使用 `MOD-{LAYER_CODE}-{SEQ}` 格式，与本文�?§5.1 �?`<DOMAIN>-<TYPE>-<NNN>` 格式不一致�?

**处理方案**：施�?stable 时将 module-id-registry.yaml 的格式对齐到本文�?§5.1，当前不处理（该注册表为空壳，无实际影响）�?

---

## 6. ttl 受控词表

> **Canonical SSoT**：[`_registry/vocabularies/ttl-vocabulary.yaml`](../_registry/vocabularies/ttl-vocabulary.yaml)
>
> 以下仅列出速查。完整定义（definition、ai_behavior、retention_action 等）请查阅词汇表 YAML�?

| ttl | 含义 |
|-----|------|
| `permanent` | 永久保留 |
| `30d` | 保留 30 �?|
| `7d` | 保留 7 �?|
| `session` | 仅当次会话有�?|
| `periodic_review_90d` | 定期审查�?0 天周期） |

**AI 生成文件必须标注 ttl**。未标注 ttl �?AI 生成文件，默�?`ttl: 7d`�?

---

## 7. �?B：任务卡字段（完�?SSoT�?

> 任务卡是 AI 执行任务的最小单元。字段的**唯一真源**是本 §7，取代所有其他文件中的重复定义（包括�?`task-card-standard.md` §3 的字段定义——已�?2026-05-01 拆分，字段定义全部吸收至本节）�?
>
> 代码结构真源�?*`src/zephyr/shared/schemas.py`** �?`Task` 模型（Pydantic v2）�?*计数口径**�?*§7.1 本表列域 B 语义字段 28 �?*；同一 `Task` 另含 **`is_deleted` / `deleted_at` / `schema_version` �?3 个平�?存储追踪字段**（软删除�?schema 版本）→ **Pydantic `Task` �?31 字段**，与 SQLite `tasks` 核心列一致。业务上可称 **TaskCard**（MOD-INF-006）——`Task` 基座 + 管线/模板扩展列（§7.12）�?*禁止**以不存在�?`src/zephyr/schemas.py` 为据�?
>
> 业务规则和操作指南（如何写任务卡正文、验收标准怎么写）�?`governance/task/task-card-standard.md`�?

### 7.1 字段总表（快速索引）

> 下表�?**�?B 语义字段 28 �?*（与门禁 G0「业务完整性」对齐）�?*�?3 项平台追踪字�?*（`is_deleted` / `deleted_at` / `schema_version`）见 §7.1.1，包含在同一 `Task` 模型内但不计入「语�?28」。各字段格式�?§§7.2~7.11�?

| # | 字段 | 类型 | 必填 | 所属分�?| 说明 |
|---|------|------|:----:|---------|------|
| 1 | `task_id` | string | �?| 标识 | 唯一标识，格式见 §7.10 |
| 2 | `namespace` | enum | �?| 标识 | 7 命名空间之一，见 §9.3 |
| 3 | `seq` | int | �?| 标识 | 命名空间内自增序�?|
| 4 | `title` | string | �?| 标识 | 任务标题�?-200 字） |
| 5 | `status` | enum | �?| 状�?| 10 状态机枚举值，�?§4.2 |
| 6 | `priority` | enum | �?| 状�?| P0/P1/P2/P3/P4，与 `Priority` 枚举�?SQLite `CHECK` 一致；§9.7 与此对齐 |
| 7 | `phase` | int | �?| 状�?| **0�? 整数**，与 SQLite `tasks.phase` `CHECK` 一致；语义约定由任务系统蓝�?编排层定义—�?*禁止**与本表冲突地写作 `design`/`implement` 字符�?|
| 8 | `execution_model` | enum | �?| 模型 | 主力模型，合法值见 §7.3 |
| 9 | `model_rationale` | string | �?| 模型 | 选模型理由（1-3 句话�?|
| 10 | `fallback_model` | enum | �?| 模型 | 备选模型（主力不可用时�?|
| 11 | `files_in_scope` | string[] | �?| 路径 | 需读取的文件（绝对路径�?|
| 12 | `deliverables` | string[] | �?| 路径 | 产出的文件（绝对路径�?|
| 13 | `depends_on` | string[] | �?| 依赖 | 前置任务 task_id 列表 |
| 14 | `safety_level` | enum | �?| 安全 | H/M/L，判定准则见 §10.10 |
| 15 | `classification` | enum | �?| 安全 | `public` / `internal` / `confidential`，与 `Classification` 枚举�?**`_registry/vocabularies/classification-vocabulary.yaml`** 对齐 |
| 16 | `evolution_policy` | enum | �?| 安全 | frozen / extendable / rewritable，见 §10.11 |
| 17 | `idempotent` | bool | �?| 安全 | 任务是否可安全重�?|
| 18 | `directive` | string | �?| 执行 | 执行指令编号（如 `313+325+999`�?|
| 19 | `tags` | string[] | �?| 执行 | 标签列表（kebab-case�?|
| 20 | `acceptance` | string[] | �?| 验收 | 量化验收指标列表 |
| 21 | `estimate_hours` | float | �?| 工时 | 预估工时（小时） |
| 22 | `actual_hours` | float | �?| 工时 | 实际工时（完成后填写�?|
| 23 | `created_at` | datetime | �?| 时间 | 创建时间 ISO 8601（系统自动） |
| 24 | `updated_at` | datetime | �?| 时间 | 更新时间 ISO 8601（系统自动） |
| 25 | `completed_at` | datetime | �?| 时间 | 完成时间 ISO 8601（系统自动） |
| 26 | `session_id` | string | �?| 运行�?| 关联 session UUID（系统自动） |
| 27 | `waiting_for` | string | �?| 运行�?| WAITING 时等待的条件 |
| 28 | `ready_at` | datetime | �?| 运行�?| READY 触发时间 ISO 8601（系统自动） |

#### 7.1.1 平台/存储追踪字段（不计入语义 28�?

以下字段同属 **`src/zephyr/shared/schemas.py`** `Task` 模型，用�?*软删除与 schema 版本**（MOD-INF-012 等），统计口径常与「业�?28」区分：

| 字段 | 类型 | 说明 |
|------|------|------|
| `is_deleted` | int (0/1) | 软删除标�?|
| `deleted_at` | datetime / �?| 软删除时�?|
| `schema_version` | string | 持久化层 schema 版本追踪 |

**合计**：语�?**28** + 追踪 **3** = **`Task` 31 字段**（与 MOD-INF-006、`sqlite_schema` 核心列对齐）�?

### 7.2 核心标识字段

| 字段 | 格式规则 | 说明 |
|------|---------|------|
| `task_id` | `{NAMESPACE}-{SEQ}` | �?`ADR-001`、`SRC-042`。格式规则见 §7.10 |
| `namespace` | 7 命名空间枚举值之一（�?.3�?| task_id 前缀，控制命名空间内自增 |
| `seq` | int �?1 | 命名空间内自增序号，�?`task_repo.py` `next_seq(namespace)` 自动分配 |
| `title` | 1-200 �?| 一眼看懂干什么（对齐 Jira Summary / Linear Title�?|
| `status` | TaskStatus 10 值之一（�?.2�?| PENDING / IN_PROGRESS / COMPLETED / VERIFIED / FAILED / BLOCKED / WAITING / READY / RETRY / CANCELLED |
| `priority` | P0 / P1 / P2 / P3 / P4 | P0=关键阻塞，P1=重要近期，P2=一般计划，P3=低优先，P4=可选（�?§9.7�?|
| `phase` | 整数 **0�?** | SQLite `INTEGER NOT NULL CHECK(phase BETWEEN 0 AND 9)`；业务含义由编排�?Task 系统蓝图定义 |
| `directive` | 自由文本 | 执行指令编号，如 `313+325+999` |

### 7.3 模型执行字段

| 字段 | 格式规则 | 说明 |
|------|---------|------|
| `execution_model` | 模型枚举值之一（见下表�?| 执行本任务的主力模型 |
| `model_rationale` | 1-3 句话 | 为什么选这个模型（**强建议填写，防止 AI 乱选贵模型**�?|
| `fallback_model` | 模型枚举值之一 | 主力不可用时的备选。切换后必须�?execution_log 记录 |

**模型枚举�?*�?

| �?| 擅长场景 | 费用 |
|---|---------|------|
| `claude-opus-4.7` | 复杂多文件联动、架构级决策 | �?|
| `claude-sonnet-4.6` | 核心代码编写、代码复�?| 便宜 |
| `glm-5.1` | 讨论、基础工作、批量化工作 | 免费 |
| `kimi` | 长文分析、知识提�?| 免费 |
| `any` | 不挑模型，谁空谁�?| �?|

**model_rationale 质量判据**�?

| 质量 | 示例 |
|:----:|------|
| �?Good | `Sonnet 擅长结构化代码编写且便宜，本任务涉及 3 个文件修改，无需 Opus 架构推理` |
| �?Bad | `Sonnet 够了`（无分析）、`因为便宜`（没说便宜够用）、`Owner 选的`（推责任�?|

**默认规则**：优先使用免�?便宜模型，只有任务卡明确标注 `claude-opus-4.7` 时才使用贵模型�?

> 对标 IETF AAT：`execution_model` = `model_id`，`author_agent`（域 A�?= `agent_id`。两者不可合并——`author_agent` 回答"在哪个编辑器写的"，`execution_model` 回答"用哪个模型干�?，详�?§10.5�?

### 7.4 路径字段（防漂移核心�?

| 字段 | 格式规则 |
|------|---------|
| `files_in_scope` | **绝对路径**列表——本任务需读取的所有文�?|
| `deliverables` | **绝对路径**列表——本任务产出的所有文�?|

**路径铁律**�?

| # | 规则 |
|---|------|
| 1 | 必须使用绝对路径（如 `D:\ZephyrAlpha\src\...`），禁止相对路径 |
| 2 | 必须列出所有相关文件——AI 不会猜，漏一个就可能找不�?|
| 3 | 路径必须�?`D:\ZephyrAlpha\` 开�?|
| 4 | deliverables �?files_in_scope 不能完全重叠（除非原地修改） |

**AI 确定 files_in_scope 的规�?*�?

| 文件类型 | 是否放入 | 判据 |
|---------|:------:|------|
| 本任务需修改的文�?| �?| 直接读写 |
| 需理解接口/结构的只读文�?| �?| `shared/schemas.py` / contracts/ |
| 同目录相邻但不需要改�?| �?| 除非联动修改 |
| 下游消费者的文件 | �?| 不修改就不放 |

> **N:N 映射**：任务与文件是多对多关系。`files_in_scope` �?`deliverables` 是任务卡层面的快捷引用，完整 N:N 映射存储�?`task_files` 表中�?

### 7.5 依赖字段

| 字段 | 格式规则 | 说明 |
|------|---------|------|
| `depends_on` | task_id 列表 | 前置任务，必须全�?VERIFIED 才能开�?|

**依赖验真规则**�?

| 场景 | 行为 |
|------|------|
| depends_on 所�?task_id 均存在且终�?| �?允许开�?|
| depends_on 中有 task_id 不存�?| �?G0 阻止创建 |
| depends_on 中有 task_id 非终�?| ⚠️ 可创建，状态自�?= PENDING |
| depends_on = `[]` 或字段缺�?| �?无前置约�?|

> 对标 Jira Blocks / Azure DevOps Dependencies�?

### 7.6 安全与演进字�?

| 字段 | 类型 | 必填 | 合法�?| 说明 |
|------|------|:----:|--------|------|
| `safety_level` | enum | �?| H / M / L | H=高风险（架构/风控），M=中风险（代码修改），L=低风险（文档/测试）。判定准则见 §10.10 |
| `classification` | enum | �?| `public` / `internal` / `confidential` | 访问分类。`internal`：项目内可见、不对外分发 |
| `evolution_policy` | enum | �?| frozen / extendable / rewritable | 文件演进策略，见 §10.11 |
| `idempotent` | bool | �?| true / false | true=重试不产生副作用；false 时必须解释原�?|

**safety_level 判定准则**�?

| 条件 | �?level |
|------|:------:|
| 涉及 `src/zephyr/db/` schema 变更 | H |
| 涉及 `docs/01_policies_and_standards/` 治理标准 | H |
| 涉及数据库文件读写（�?schema�?| M |
| 涉及多个 `.py` 文件联动（非 DB 非治理） | M |
| 纯文档：README / ADR / 探索笔记 | L |
| 单文件修改、无跨文件副作用 | L |
| 不确定时 | M（默认保守） |

> **�?`ai_autonomy`（域 A）的关系**：`ai_autonomy` �?AI 能不能动文件"，`safety_level` �?动了之后有多危险"。两者独立判断，取更严�?

### 7.7 工时与时间字�?

| 字段 | 类型 | 必填 | 格式 | 说明 |
|------|------|:----:|------|------|
| `estimate_hours` | float | �?| �?0 | 预估工时（对�?Jira Story Points�?|
| `actual_hours` | float | �?| �?0 | 实际工时（完成后填写，对�?Jira Time Spent�?|
| `created_at` | datetime | �?| ISO 8601 | 创建时间（系统自动填充） |
| `updated_at` | datetime | �?| ISO 8601 | 最近更新时间（系统自动填充�?|
| `completed_at` | datetime | �?| ISO 8601 | 完成时间（系统自动填充，对齐 Jira Resolution Date�?|

### 7.8 运行时字段（系统自动管理�?

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `session_id` | string | �?| 关联 session UUID（系统自动填充） |
| `waiting_for` | string | �?| WAITING 状态时等待的资�?事件 |
| `ready_at` | datetime | �?| READY 触发时间 ISO 8601（系统自动填充） |

### 7.9 标签与验收字�?

| 字段 | 类型 | 必填 | 格式规则 | 说明 |
|------|------|:----:|---------|------|
| `tags` | string[] | �?| kebab-case 全小�?| `{前缀}:{值}` 或裸标签。如 `wave0-arbitrated`、``、`origin:b5-s2.1` |
| `acceptance` | string[] | �?| 量化验收指标 | �?`CRUD 全覆盖`、`10 状态机转换全部实现`。建议用共享度量标签（coverage/build/lint/files/diff�?|

### 7.10 task_id 格式与命名空间规�?

```
{NAMESPACE}-{SEQ}
```

| 命名空间 | 含义 | 文件路径模式 | 示例 |
|---------|------|------------|------|
| `MOD` | 模块文档 | `docs/03_modules/l<NN>_<layer>/<module>/` | MOD-001 |
| `KE` | 知识条目 | `docs/08_knowledge/` | KE-003 |
| `STD` | 标准/规范 | `docs/01_policies_and_standards/` | STD-001 |
| `DW` | ~~开发工作区~~ 已删�?| `—` | `19_development_workspace/` 已于 2026-05-02 删除 |
| `SRC` | 源代�?| `src/zephyr/` | SRC-007 |
| `OPS` | 运维/其他 | 不属于以上分类的 | OPS-001 |

**自增规则**：每个命名空间内序号独立递增，由 `task_repo.py` `next_seq(namespace)` 自动分配�?

**已废弃的�?task_id 格式**�?

| 旧前缀 | 替代 | 迁移方式 |
|--------|------|---------|
| `T-0-*` ~ `T-4-*` | �?namespace 重新分配 | 迁移时自动分�?|
| `T-V2-*` | �?namespace 重新分配 | 迁移时自动分�?|
| `T-KE-*` | `KE-{SEQ}` | �?T- 前缀 |
| `T-ADR-*` | `ADR-{SEQ}` | �?T- 前缀 |
| `T-CP-*` | `CP-{SEQ}` | �?T- 前缀 |
| `T-SCRIPT-*` | `SRC-{SEQ}` | 归入 SRC |
| `T-UNCLASSIFIED-*` | `OPS-{SEQ}` | 归入 OPS |

### 7.11 已废弃字段（�?B 层面�?

> 以下字段在任务卡层面已废弃。其替代方案和废弃原因记录于此，供迁移参考�?

| 废弃字段 | 废弃原因 | 替代方案 |
|---------|---------|---------|
| `predecessor` | �?`depends_on` 功能重复 | 使用 `depends_on` |
| `model_preference` | �?`execution_model` 功能重复 | 直接�?`execution_model` 分组 |
| `ai_autonomy`（任务卡中） | 可由 `classification` + `safety_level` 组合推导 | H+confidential �?Human-Gated，其�?�?AI-Modifiable |
| `provenance.origin` / `provenance.rationale_log` | 结构化字段过�?| 放入 `tags`（如 `origin:b5-s2.1`�?|
| `owner` | 固定�?`ZephyrAlpha-Owner`，无信息�?| 系统默认 |
| `version`（任务卡中） | 任务卡版本由 git 管理 | 不需要字�?|
| `layer`（任务卡中） | 可从 `namespace` 推导 | 不需要字�?|
| `est_hours` | 字段名不规范 | �?`estimate_hours` |
| `created` | 字段名不规范 | �?`created_at` |

### 7.12 SQLite `tasks` 表：语义 28 + 追踪�?+ Vibe 扩展�?

> **§7.1 + §7.1.1** 对应 Pydantic `Task` **31 字段**（语�?28 + 追踪 3），�?`tasks` �?*核心�?*对齐。`src/zephyr/db/sqlite_schema.py` 另含 **迁移追加�?*（如 `upstream_files`、`downstream_outputs`、`assigned_pipeline`、`source_blueprint`、`rollback_instructions`、`completed_gates` 等），用�?Vibe Coding 任务�?richer 视图�?MCP—�?*详尽列清单以 DDL + 迁移史为�?*。扩展列不在 §7.1 语义 28 内，但未禁止写入；门禁与报表应标明读取的�?*语义 28**�?*Task 31** 还是**含富扩展列的全表**�?

### 7.13 与域 A frontmatter 的关�?

任务卡字�?*不是**文档 frontmatter 字段。它们存储在 SQLite `tasks` 表中，通过 `task_id` 关联�?

�?A 中的同名字段（`execution_model`、`safety_level`、`classification`、`evolution_policy`）与�?B �?*同一概念的不同上下文**�?
- �?A 用于**文档溯源**—�?这个文档是什么安全等级、用什么模型写�?
- �?B 用于**任务执行**—�?这个任务该用什么模型做、多危险"

两者通过 `task_id` 关联，字段值应保持一致（如有差异必须解释原因）�?

---

## 8. �?C：AI 治理字段

> AI 治理字段分散在三个位置：文档 frontmatter（域 A 子集）、AI 决策日志、AI 员工档案�?
> 本节是域 C 字段的交叉引用索引，详细定义见对应章节�?

### 8.1 �?C 字段分布

| 位置 | 字段�?| 存储方式 | 真源 |
|------|:------:|---------|------|
| 文档 frontmatter（域 A 子集�?| 7 | YAML frontmatter | 本文�?§10 |
| AI 决策日志 | 28+2 | JSONL 文件 | `ai-autonomous-company-endgame-design.md` §2.6 |
| AI 员工档案 | 30+ | YAML 文件 | `ai-autonomous-company-endgame-design.md` §4 |

### 8.2 �?A 中的 AI 治理字段�? 个）

| 字段 | 说明 | 详见 |
|------|------|------|
| `ai_autonomy` | AI 自治权限等级 | §10.1 |
| `author_agent` | 创作代理（谁写的这个文档�?| §10.5 |
| `governance_family` | 治理系统家族 A/B/C/D | §10.7 |
| `ai_capability_slot` | AI 员工接入点状�?| §10.7 |
| `ai_autonomy_level_planned` | 规划�?AI 自治等级 | §10.7 |
| `ai_employee_count_planned` | 规划�?AI 员工数量 | §10.7 |
| `provenance` | 溯源信息 | §10.3 |

### 8.3 provenance 双定义澄�?

项目�?`provenance` 一词在两个上下文中使用，语义不同：

| 上下�?| 名称 | 语义 | 位置 | 格式 |
|--------|------|------|------|------|
| 文档溯源 | **`provenance`** | 文档的来源、审计链、裁决记�?| frontmatter YAML | 复杂对象（origin_drafts / audit_chain / arbitration�?|
| 运行时写入溯�?| **`WriteTrace`** | 代码运行时每次写入操作的溯源 | Python 代码 `WriteTrace(BaseModel)` | 简单对象（writer_id / timestamp / operation / target�?|

**为什么用两个�?*�?
- `provenance` 是行业术语（OpenLineage、W3C PROV 都用这个词），指文档/数据的来源和演变历史
- `WriteTrace` 是代码运行时的写入溯源，关注的是"谁在什么时候对什么做了什么操�?
- 两者粒度不同：provenance 是文档级（整个文件），WriteTrace 是操作级（单次写入）
- 代码�?`Provenance` 类已改名�?`WriteTrace`，避免与 frontmatter `provenance` 混淆

---

## 9. 受控枚举定义

> 本节定义跨域使用的枚举值。每个枚举有唯一的代码真源�?

### 9.1 category 枚举�?0 值）

> 语义：知识条目的内容类型—�?这是什么类型的知识"�?
> �?`domain`（�?.2）是两个独立维度：category �?是什么类�?，domain �?属于哪个领域"�?

| # | category | 含义 | 对标 KMS |
|---|----------|------|---------|
| 1 | `blueprint_decision` | 蓝图设计决策（模块级�?| �?|
| 2 | `strategy` | 交易策略（买卖信号、仓位管理） | domain:strategy |
| 3 | `factor` | 因子设计（alpha因子、风险因子） | domain:factor |
| 4 | `best_practice` | 最佳实践（验证过的做法�?| knowledge_type:practice |
| 5 | `lesson_learned` | 教训记录（踩过的坑、故障复盘） | knowledge_type:lesson |
| 6 | `architecture` | 架构决策（系统级，区别于蓝图决策的模块级�?| domain:infrastructure |
| 7 | `risk_control` | 风控知识（风控规则、风险度量、熔断机制） | domain:risk |
| 8 | `data_governance` | 数据治理（数据源、数据质量、数据血缘） | domain:data |
| 9 | `operations` | 运维知识（部署、监控、故障处理、CI/CD�?| �?|
| 10 | `compliance` | 合规知识（法规要求、审计标准、监管报告） | �?|

**代码真源**：`src/zephyr/mcp/knowledge_base_server.py` `_VALID_CATEGORIES`（需同步扩展�?

### 9.2 domain 枚举�?0 值）

> 语义：知识条目所属的业务领域—�?属于哪个领域"�?
> �?`category`（�?.1）是两个独立维度�?

| # | domain | 含义 | 对应 layer |
|---|--------|------|-----------|
| D0 | `data` | 数据�?| l00 / l01 |
| D1 | `feature` | 特征�?| l02 |
| D2 | `model` | 模型�?| l03 / l04 |
| D3 | `signal` | 信号�?| l05 |
| D4 | `execution` | 执行�?| l06 |
| D5 | `risk` | 风控�?| l07 |
| D6 | `portfolio` | 组合�?| l08 |
| D7 | `reporting` | 报告�?| l09 |
| D8 | `infrastructure` | 基础设施�?| cross_layer |
| D9 | `other` | 其他 | �?|

**代码真源**：`docs/08_knowledge/kms-entry-schema.md` `domain` 字段（需同步扩展�?

### 9.3 namespace 枚举�? 值）

> 语义：任务卡的命名空间——任务属于哪个工作流�?

| namespace | 含义 | 对应目录 |
|-----------|------|---------|
| `ADR` | 架构决策记录 | `02_enterprise_architecture/adr/` |
| `MOD` | 模块文档 | `03_modules/l<NN>_<layer>/<module>/` |
| `KE` | 知识条目 | `08_knowledge/` |
| `STD` | 标准 | `01_policies_and_standards/` |
| `DW` | ~~开发工作区~~ 已删�?| `—` |
| `SRC` | 源码 | `src/zephyr/` |
| `OPS` | 运维 | scripts/ |

**代码真源**：`src/zephyr/shared/schemas.py` `TaskNamespace` 枚举

### 9.4 AgentRole 枚举�? 值）

> 语义：AI 员工的角色——负责什么类型的工作�?

| role | 含义 | 典型任务 |
|------|------|---------|
| `architect` | 架构�?| 架构决策、模块边界、接口设�?|
| `implementer` | 实施�?| 代码编写、测试实�?|
| `reviewer` | 复核�?| 代码审查、文档审�?|
| `governor` | 治理�?| 标准制定、合规检�?|
| `researcher` | 研究�?| 文献调研、竞品分�?|
| `operator` | 运营�?| 部署、监控、故障处�?|

**代码真源**：`src/zephyr/orchestrator/agent_orchestrator.py` `AgentRole` 枚举

### 9.5 layer 枚举�?4 值）

> 语义：文�?模块所属的架构层—�?属于系统的哪一�?�?
> �?`domain`（�?.2）是关联维度：domain 是业务领域（D0-D9），layer 是架构分层（l00-l13）�?
> 一�?layer 可能对应多个 domain，一�?domain 也可能跨越多�?layer�?

| # | layer | 含义 | 对应 domain |
|---|-------|------|------------|
| 1 | `l00_data_source` | 数据源层 | D0 data |
| 2 | `l01_data_processing` | 数据处理�?| D0 data |
| 3 | `l02_alpha_factor` | Alpha 因子�?| D1 feature |
| 4 | `l03_signal_generation` | 信号生成�?| D3 signal |
| 5 | `l04_ml_platform` | 机器学习平台�?| D2 model |
| 6 | `l05_portfolio_construction` | 组合构建�?| D6 portfolio |
| 7 | `l06_trade_execution` | 交易执行�?| D4 execution |
| 8 | `l07_risk_management` | 风险管理�?| D5 risk |
| 9 | `l08_post_trade_analytics` | 盘后分析�?| D7 reporting |
| 10 | `l09_research_innovation` | 研究创新�?| D9 other |
| 11 | `l10_compliance` | 合规�?| D9 other |
| 12 | `l11_human_ai_interface` | 人机交互�?| D8 infrastructure |
| 13 | `shared` | 共享组件 | D8 infrastructure |
| 14 | `cross_layer` | 跨层 | D8 infrastructure |

**代码真源**：`src/zephyr/kb/triage.py` `VALID_LAYERS`（需同步对齐�?

### 9.6 source_type 枚举�? 值）

> 语义：知识条目的来源类型—�?这条知识从哪里来"�?
> �?`category`（�?.1）是关联维度：category �?是什么类�?，source_type �?从哪来的"�?

| # | source_type | 含义 | 典型场景 |
|---|------------|------|---------|
| 1 | `paper` | 学术论文 | �?arXiv/期刊提取的策�?因子 |
| 2 | `opensource` | 开源项�?| �?GitHub 项目提取的实现方�?|
| 3 | `blueprint` | 项目蓝图 | 从本项目的蓝图文档提取的设计决策 |
| 4 | `report` | 行业研究报告 | 从券�?咨询报告提取的行业洞�?|
| 5 | `practice` | 最佳实践文�?| 从博�?演讲/教程提取的实践方�?|
| 6 | `operation` | 运营经验 | 从实际运维中积累的经�?|
| 7 | `lesson` | 教训（失败案例） | 从故�?踩坑中提炼的教训 |

**代码真源**：`docs/08_knowledge/kms-entry-schema.md` `source_type` 字段

### 9.7 priority 枚举�? 值）

> 语义：优先级/严重度—�?多重�?多紧�?�?
> 统一了项目中原有的三套优先级定义：AuditSeverity（P0-P2）、模�?priority（P0-P3）�?
> activation_priority（P0-P4）。统一�?5 级，覆盖所有场景�?

| # | priority | 含义 | 适用场景 |
|---|----------|------|---------|
| 1 | `P0` | 关键/紧急——必须立即处理，阻塞其他工作 | 生产故障、安全漏洞、核心功能缺�?|
| 2 | `P1` | 重要——近期必须完成，影响核心功能 | 重要功能、关键设计决�?|
| 3 | `P2` | 一般——计划内工作，不影响核心功能 | 增强功能、优化改�?|
| 4 | `P3` | 低优先——有空再�?| 可选功能、锦上添�?|
| 5 | `P4` | 可选——不确定是否需�?| 探索性想法、远期规�?|

**代码真源**：`src/zephyr/shared/schemas.py` �?`Priority`�?*P0`–`P4**，与 SQLite `tasks.priority` `CHECK` 一致）�?

---

## 10. AI 员工与治理字�?

### 10.1 ai_autonomy 字段

标注该文档的 AI 自治权限等级，与 `ai-autonomy-authority-registry.md` 三层模型对齐�?

| �?| 含义 | AI 员工行为 |
|----|------|-----------|
| `immutable_core` | 系统宪法�?| **禁止 AI 自主修改**，需 Owner 直接审批 + ADR 记录 |
| `human_gated` | 人控闸门�?| AI 可提修改提案�?*Owner 审批后方可执�?* |
| `ai_modifiable` | AI 可改�?| AI 可自主修改，**每次修改写入 Provenance Chain** |

**默认�?*：治理标准文�?= `immutable_core`；蓝�?施工�?= `human_gated`；日�?标签 = `ai_modifiable`�?

### 10.2 created_by 字段

| �?| 含义 |
|----|------|
| `human` | 人类创建 |
| `agent` | AI 员工创建 |
| `human_plus_agent` | 人机协作创建 |

### 10.3 provenance 溯源�?

```yaml
provenance:
  origin_drafts:          # 草稿来源
    - path: "原始草稿路径"
      model: "创建该草稿的 AI 模型"
  audit_chain:            # 审计�?
    - auditor: "审计�?
      date: "YYYY-MM-DD"
      verdict: "pass|fail|conditional"
  arbitration:            # 裁决记录
    arbiter: "裁决�?
    date: "YYYY-MM-DD"
    decision: "裁决结论"
```

### 10.4 AI 员工在文档操作中的约�?

1. **创建文档**：必须填�?Draft 阶段全部 7 个必填字�?
2. **修改 `immutable_core` 文档**：必须先�?ADR，Owner 审批后方可修�?
3. **修改 `human_gated` 文档**：必须走 `request_change()` �?`approve_change()` 流程
4. **修改 `ai_modifiable` 文档**：可自主修改，但必须�?commit message 中包�?`agent_id` �?`session_id`
5. **删除文档**：无论何种权限等级，AI 员工**禁止自主删除**文档，必�?Owner 审批
6. **AI 生成文件**：frontmatter 必须包含 `created_by: agent` �?`ttl` 字段

### 10.5 模型选择字段（域 A + �?B�?

标注与该文档/任务相关�?AI 模型信息。`author_agent` �?`execution_model` 是两个独立字段，语义不同，不可合并：

| 字段 | �?| 语义 | 值的格式 | 适用场景 | 对标专业机构 |
|------|---|------|---------|---------|------------|
| `author_agent` | A | 创作代理——谁写的这个文档 | 编辑�?产品名：`Cursor-Premium` / `Trae-Free` / `Kimi-1M` / `Claude-API` | 所有文�?| **IETF: agent_id** |
| `execution_model` | B | 执行模型——计划用什么模型完成这个任�?| 底层模型名：`claude-opus-4.7` / `claude-sonnet-4.6` / `glm-5.1` / `kimi` / `any` | 任务�?| **IETF: model_id** |
| `model_rationale` | B | 选模型理�?| 自由文本�?-3 句话�?| 任务卡（建议填写�?| �?|
| `fallback_model` | B | 降级模型 | �?`execution_model` | 任务卡（可选） | �?|

**为什么不能合�?*�?
- `author_agent` 回答"谁写�?——关�?*溯源审计**（这个文档是哪个编辑�?AI 产生的）
- `execution_model` 回答"谁干�?——关�?*执行能力**（模型能不能完成这个任务�?
- 两者维度不同：一个任务可能由 `claude-sonnet-4.6` 执行（execution_model），但在 `Trae-Free` 编辑器中完成（author_agent�?
- 专业机构（IETF AAT、OpenLineage、MLflow�?00% 拆开这两个维度，没有例外

**模型选择策略**（与 `model-capability-contract.yaml` 对齐）：

| 模型 | 适合的任务类�?| 不适合的任务类�?|
|------|-------------|---------------|
| `claude-opus-4.7` | 关键架构决策、终审裁决、复杂推�?| 机械批量操作 |
| `claude-sonnet-4.6` | 中等复杂度任务、代码实现、文档编�?| 关键架构决策 |
| `glm-5.1` | 机械任务、批量文件操作、流水线执行 | 复杂推理、长上下�?|
| `kimi` | 长文档阅读、历史挖掘、中文理�?| 代码实现 |
| `any` | 无模型偏�?| �?|

### 10.6 Session Log 正文字段

Session log（`doc_type: log` 且用�?AI session 记录时）的正文包含以下字段�?*这些是正文内容，不是 frontmatter 字段**——只�?session log 才需要写这些，其他文档不需要�?

| 字段 | 类型 | 说明 |
|------|------|------|
| `context_budget_used` | string | 本次 session 消耗的上下文预算估计（�?�?50k tokens，读取了 8 个文�?�?|
| `knowledge_extracted` | int | 本次 session 提取的知识条目数量（汇总计数） |
| `construction_deviations` | list_of_objects | 施工偏差明细列表（每条含 deviation_type / blueprint_ref / description / recommended_action�?|
| `next_session_handover` | object | 交接给下一�?session 的信息，�?`next_task` / `blockers` / `context_needed` / `warnings` |

**大白话解�?*�?
- `context_budget_used`：这次干活花了多�?脑力"——AI 的上下文窗口是有限的，记录用了多少，方便下次估算
- `knowledge_extracted`：这次干活过程中，从旧文件里提炼出了几条知识（对�?`08_knowledge/` 下的 KE 条目数）。这�?*汇总计�?*，只记一个数�?
- `construction_deviations`：施工中发现了哪些偏差，每条偏差怎么处理。这�?*明细列表**，和 `knowledge_extracted` 互补而非替代。打个比方：`knowledge_extracted` �?今天赚了 500 �?，`construction_deviations` �?今天修了 3 �?bug，其�?2 个值得记录"
  - `deviation_type`（偏差类型）：`blueprint_defect`（蓝图设计有缺陷�? `tech_choice_infeasible`（技术选型不可行）/ `interface_change`（接口变更）/ `scope_change`（范围变更）
  - `blueprint_ref`（来源蓝图路径）：必须写完整物理路径，不来自蓝图时写 N/A
  - `description`（具体描述）：发现了什么问题、为什么是偏差
  - `recommended_action`（建议动作）：`extract_ke`（提�?KE�? `update_decision_record`（更新决策记录，参见 MOD-KB-001 §3.9.5�? `modify_blueprint`（修改蓝图）/ `record_only`（仅记录�?
- `next_session_handover`：交接班信息——下一�?AI 接手时需要知道：下一个任务是什么、有什么卡住的、需要先读哪些文件、有什么坑要注�?

**字段间关�?*�?
- `knowledge_extracted` �?`construction_deviations`：计�?vs 明细。`construction_deviations` �?`recommended_action` �?`extract_ke` 的条目数�?�?`knowledge_extracted` 的值（不是所�?KE 都来自施工偏差）
- `construction_deviations` 与施工图 §9.7：session �?vs 文档级。一�?session 可能涉及多份施工图，两个层面各记各的，不冲突

来源：`session-log-schema.yaml`

### 10.7 治理系统 AI 预留字段�?9 系统专用�?

来自 AC-2 决议（`ai-autonomous-company-endgame-design.md` §4.2），�?39 个治理系统预留的 AI 员工规划字段�?

| 字段 | 类型 | 合法�?| 说明 |
|------|------|--------|------|
| `governance_family` | string | `A` / `B` / `C` / `D` | 治理系统所属家族：A=机构标配，B=元治理，C=氛围独有，D=共享底座 |
| `ai_capability_slot` | enum | `planned` / `reserved` / `active` / `none` | AI 员工接入点状态：planned=已规划，reserved=已预留，active=已激活，none=�?|
| `ai_autonomy_level_planned` | enum | `l0` / `l1` / `l2` / `l3` | 规划�?AI 自治等级：L0=AI 自决，L1=自决+事后通知，L2=AI 提案+人批准，L3=人独�?|
| `ai_employee_count_planned` | int | 0-10 | 该系统计划接入的 AI 员工数量 |

**当前预填结果**（来�?ai-autonomous-company-endgame-design.md）：
- `ai_capability_slot`: 10 planned + 16 reserved + 13 none
- AI 员工规划总数�?*31 �?*

### 10.8 三层口子预留（代�?文档/前端�?3 项）

来自 OQ-063 决议（`ai-autonomous-company-endgame-design.md` §4.9），�?AI 员工在代码层/文档�?前端层预留接入点�?*这些是路�?目录预留，不�?frontmatter 字段**——定义的�?哪里�?AI 员工留了位置"，不�?文档头部填什�?�?

| �?| 编号 | 预留路径 | 用�?|
|---|------|---------|------|
| 代码 | C-1 | `src/zephyr/layers/{L}/_ai_operator/` | 每层预留 AI Operator 命名空间 |
| 代码 | C-2 | `src/zephyr/shared/contracts/ai_operator_contract.py` | AI Operator 接口协议占位 |
| 代码 | C-3 | `src/zephyr/shared/immutable_core/` | 纳入 AI 决策日志 schema |
| 文档 | D-1 | `META_GOVERNANCE/ai_authored_docs/` | AI 生成文档归档 |
| 文档 | D-2 | `META_GOVERNANCE/ai_operators_registry.md` | 全公�?AI 员工花名�?|
| 文档 | D-3 | `META_GOVERNANCE/ai_operators/b01_operators/` | B01 元治�?Operator 归属 |
| 前端 | F-1 | `frontend/src/modules/ai_ops/` | AI 操作前端命名空间 |
| 前端 | F-2 | `frontend/src/routes/` | 路由前缀 `/ai-ops/*` |
| 前端 | F-3 | `frontend/src/api/ai_operator_client.ts` | AI Operator API 客户端契�?|

**合计**：AC-2 四列字段 + 三层口子 9 �?= **13 �?AI 预留**

### 10.9 AI 决策日志（独�?schema，非 frontmatter�?

AI 决策日志（`logs/ai/{employee_id}/YYYY-MM-DD.jsonl`）有自己的独�?JSON schema，包�?28+ 字段（`decision_id` / `employee_id` / `trigger` / `context` / `reasoning` / `decision` / `outcome` / `audit` / `employee_state` 等）�?

**这些字段不属于文�?frontmatter**，不纳入本标�?§2 字段表。AI 决策日志 schema 的真源是 `ai-autonomous-company-endgame-design.md` §2.6�?

### 10.10 safety_level 字段

标注文档/任务的安全风险等级，决定 AI 操作的防护策略。与 `task-card-standard.md` §3.5 �?**`src/zephyr/shared/schemas.py`** `SafetyLevel` 枚举对齐�?

| �?| 含义 | AI 行为约束 |
|----|------|-----------|
| `H` | 高风险——架构决策、风控配�?| CoVe 幻觉检测强制触发；修改必须 Owner 审批；Gate 门禁一票否�?|
| `M` | 中风险——代码修改、业务逻辑 | CoVe 条件触发；修改需�?human_gated 流程 |
| `L` | 低风险——文档、测试、日�?| CoVe 仅黑名单触发；AI 可自主修改（ai_modifiable 范围内） |

**�?`ai_autonomy` 的关�?*：`ai_autonomy` �?AI 能不能动"，`safety_level` �?动了之后有多危险"。两者独立判断，取更严格的结果�?

### 10.11 evolution_policy 字段

标注文件本身的演进策略——允不允许被改、怎么改。与 **`src/zephyr/shared/schemas.py`** `EvolutionPolicy` 枚举�?ADR-0040 对齐�?

| �?| 含义 | AI 行为约束 |
|----|------|-----------|
| `frozen` | 冻结——任何修改都不允�?| AI 禁止修改；提议修改自动触�?CoVe 强制检�?|
| `extendable` | 可追加——可在末尾加新内容，不能改旧内容 | AI 可追加条目（如注册表新增行），但不可改写已有�?|
| `rewritable` | 可重写——可完全修改 | AI 可自主修改（�?ai_autonomy �?safety_level 约束范围内） |

**默认�?*：`extendable`。ADR 和已发布的标准默�?`frozen`�?

**�?`ai_autonomy` 的关�?*：`ai_autonomy` �?AI 有没有权�?，`evolution_policy` �?文件本身允不允许"。即�?AI �?`ai_modifiable` 权限，`frozen` 文件也不可改�?

### 10.12 blueprint_refs 字段

> **2026-05-02 更新**：`construction_plan` 作为独立 doc_type 已于 2026-05-02 合并�?`blueprint`（�?2 施工指引）。新模块不再创建独立的施工图文件。以下规则仅对历�?`doc_type: construction_plan` 文档保留适用�?

施工图（`doc_type: construction_plan`）必须标注引用的蓝图列表，确保施工图与蓝图的一致性可自动验证�?

```yaml
blueprint_refs:
  - path: "docs/03_modules/l00_data_source/<module>/blueprint.md"
    status: active
    decisions_used: ["BD-001", "BD-003"]
  - path: "03_modules/l04_risk_management/<module>/blueprint.md"
    status: draft
    decisions_used: ["BD-012"]
```

| 子字�?| 类型 | 必填 | 说明 |
|--------|------|------|------|
| `path` | string | �?| 蓝图文件路径 |
| `status` | string | �?| 蓝图当前状态（`active` / `draft` / `deprecated`�?|
| `decisions_used` | string[] | �?| 本施工图使用了该蓝图的哪些决策编�?|

**pre-commit 校验规则**�?
- `doc_type: construction_plan` 的文件必须包�?`blueprint_refs`
- `blueprint_refs` 中引用的蓝图路径必须存在
- 若引用的蓝图 `status` 不是 `active`，发�?P1 警告
- 若引用的蓝图 `status` �?`deprecated`，发�?P0 阻断

### 10.13 compliance_tags 字段

标注文档涉及的合规要求。对�?EU AI Act Article 12 合规文档要求�?

```yaml
compliance_tags:
  - SR-11-7
  - EU-AI-Act-Art12
  - GDPR-Art22
```

| 合法�?| 含义 | 适用场景 |
|--------|------|---------|
| `SR-11-7` | 美联储模型风险管�?| 涉及模型/算法的文�?|
| `EU-AI-Act-Art12` | EU AI 法案�?12 条日志要�?| 高风�?AI 系统文档 |
| `EU-AI-Act-Art14` | EU AI 法案�?14 条人工监�?| 需要人工监督的 AI 决策 |
| `GDPR-Art22` | GDPR �?22 条自动化决策 | 涉及用户数据的文�?|
| `PCI-DSS` | 支付卡行业数据安全标�?| 涉及支付数据的文�?|
| `MiFID-II` | 欧盟金融工具市场指令 | 涉及交易执行的文�?|

**pre-commit 校验规则**：`safety_level: H` 的文件建议至少包含一�?`compliance_tags` 条目（P2 警告）�?

### 10.14 human_override 字段

记录人工干预 AI 决策的情况。对�?IETF AAT `human_override` 字段�?

```yaml
human_override:
  operator_id: "ZephyrAlpha-Owner"
  date: "2026-04-28"
  reason: "AI 提议删除风控参数，Owner 否决"
  original_action: "删除 risk_threshold 参数"
```

| 子字�?| 类型 | 必填 | 说明 |
|--------|------|------|------|
| `operator_id` | string | �?| 干预人标�?|
| `date` | string | �?| 干预日期 |
| `reason` | string | �?| 干预原因 |
| `original_action` | string | �?| AI 原本打算做的动作 |

**何时填写**：当 Owner 否决�?AI 的修改提议时，必须在本字段记录�?

### 10.15 last_reviewed_by 字段

记录最后一�?review 的人和日期。对�?SR 11-7 模型验证要求�?

```yaml
last_reviewed_by:
  reviewer: "ZephyrAlpha-Owner"
  date: "2026-04-28"
  model_used: "claude-opus-4.7"
```

| 子字�?| 类型 | 必填 | 说明 |
|--------|------|------|------|
| `reviewer` | string | �?| review �?模型标识 |
| `date` | string | �?| review 日期 |
| `model_used` | string | �?| 如果�?AI review，用的什么模�?|

**�?`review_status` 的关�?*：`last_reviewed_by` 记录"�?review �?，`review_status` 记录"review 结果是什�?�?

### 10.16 review_status 字段

标注文档�?review 状态。对�?SR 11-7 持续监控要求�?

| �?| 含义 | 说明 |
|----|------|------|
| `unreviewed` | �?review | AI 创建后尚未被任何�?review |
| `reviewed` | �?review | 已被 review 但未正式批准 |
| `approved` | 已批�?| Owner 正式批准，可作为依据使用 |
| `rejected` | 已否�?| review 后被否决，需要修�?|

**默认�?*：`unreviewed`�?

**pre-commit 校验规则**�?
- `safety_level: H` �?`review_status: unreviewed` �?P1 警告
- `status: active` �?`review_status: unreviewed` �?P2 警告

### 10.17 derived_from 字段

记录本文档的**横向知识来源**——AI 在创�?修改本文档时，读了哪些文件、综合了哪些信息�?

```yaml
derived_from:
  - path: "docs/03_modules/l02_alpha_factor/<module>/blueprint.md"
    relationship: synthesized
    sections: ["BD-003", "BD-007"]
  - path: "docs/08_knowledge/KE-042-factor-decay-pattern.md"
    relationship: referenced
```

| 子字�?| 类型 | 必填 | 说明 |
|--------|------|:----:|------|
| `path` | string | �?| 来源文件路径 |
| `relationship` | enum | �?| 推导关系：`synthesized`（综合多名来源后产出新结论）/ `referenced`（直接引用来源中的事实或决策�? `transformed`（对来源内容做了实质性修改后使用�?|
| `sections` | string[] | �?| 具体引用了来源中的哪些决策编号或章节 |

**�?`supersedes` �?`provenance` 的正交关�?*�?

| 字段 | 维度 | 回答的问�?| 对标 |
|------|------|-----------|------|
| `supersedes` | 纵向替代 | "这份文档取代了什�? | �?|
| `derived_from` | 横向推导 | "这份文档的知识从哪里综合而来" | W3C PROV: wasDerivedFrom / Dublin Core: dcterms:isDerivedFrom / OpenLineage: inputs |
| `provenance` | 创作过程 | "谁在什么流程中创建了这份文�? | OpenLineage: producer / W3C PROV: wasGeneratedBy |

**典型使用场景**�?
- AI 读了 3 �?arXiv 论文 + 2 份项目蓝图，写了一�?knowledge_entry �?`derived_from` 列出 5 个来�?
- AI 综合多个模块蓝图的设计决策，写了一份跨层架构视�?�?标注 `relationship: synthesized`
- AI 翻译/重构了一份外部参考文�?�?标注 `relationship: transformed`

**默认�?*：不填。当文档�?AI 基于多个来源综合生成时，建议填写�?

---

## 11. 正文结构要求

### 11.1 �?doc_type 的正文模�?

#### standard（标准）

```
# 标题
> module_id | version | status

## 1. 目的与范�?
## 2. 定义（术语表�?
## 3. 规范正文（按条款编号�?
## 4. 违规检测规�?
## 5. 变更记录
```

#### adr（架构决策记录）

```
# ADR-{NNNN}: 标题
> status | date | deciders

## 上下文（Context�?
## 决策（Decision�?
## 理由（Rationale�?
## 后果（Consequences�?
## 否决方案（Alternatives Considered�?
```

#### blueprint（模块蓝图）

> 📄 完整模板文件：`docs/01_policies_and_standards/templates/blueprint-template.md`

```
# 标题
> module_id | version | status | layer

## 1. 设计背景与目�?
## 2. 架构决策
### 2.1 决策记录�?
| 决策编号 | 问题 | 选项 | 结论 | 理由 | 关联 ADR |
## 3. 模块边界
### 3.1 职责范围
### 3.2 不包含的职责
## 4. 接口契约
### 4.1 公共 API（Python type hints�?
### 4.2 数据模型
### 4.3 事件/消息格式
## 5. 约束条件
### 5.1 技术约�?
### 5.2 业务约束
### 5.3 性能约束
## 6. 依赖关系
## 7. 已知风险与缓�?
## 后果（Consequences�?
## 否决方案（Alternatives Considered�?
```

#### construction_plan（施工图纸）

> 📄 施工指引已合并至：`docs/01_policies_and_standards/templates/blueprint-template.md` §12

```
# 标题
> module_id | version | status | layer

## 1. 前置条件
### 1.1 依赖蓝图
| 蓝图路径 | 蓝图状�?| 本图涉及的决策编�?|
### 1.2 输入数据契约
### 1.3 运行环境
## 2. 模块分解
| 模块 ID | 名称 | 职责 | 优先�?|
## 3. 公共 API
### 3.1 函数签名（Python type hints�?
### 3.2 异常类型
## 4. 数据流（Mermaid 图）
## 5. 实施步骤
| 步骤 | 内容 | 对应蓝图决策 | 验收标准 |
## 6. 来源追溯表（§8 自包含性）
| 蓝图决策编号 | 决策结论 | 本图实施位置 | 决策来源路径 |
## 7. 测试
### 7.1 P0 用例（每模块至少 3 条，含边�?异常�?
### 7.2 测试数据准备
## 8. 技术选型�?TDR
## 9. 已知风险与缓�?
## 10. 施工状�?
| construction_status | verification_status |
```

#### design（架构视图）

```
# 标题
> module_id | version | status | layer

## 1. 视图概述
## 2. 架构元素
## 3. 关系与交�?
## 4. 视图间映�?
## 5. 约束与原�?
```

#### plan（任务书�?

```
# 标题
> module_id | version | status | layer

## 1. 任务目标
## 2. 任务分解
## 3. 依赖关系
## 4. 验收标准
## 5. 风险与缓�?
```

#### roadmap（路线图�?

```
# 标题
> module_id | version | status | layer | valid_from

## 1. 当前阶段目标
## 2. 未来 3 个月方向
## 3. 关键里程�?
## 4. 假设与约�?
## 5. 与施工计划的对接
```

#### register（登记表�?

```
# 标题
> module_id | version | status

## 1. 注册表说�?
## 2. 条目表（Markdown 表格�?
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
## 5. 未完成事�?
```

#### knowledge_entry（知识条目）

```
# 标题
> module_id | category | source_file | extracted_date

## 1. 核心结论
## 2. 详细分析
## 3. 关联条目
```

### 11.2 Taskbook 状态符�?

在任务书、施工图、检查清单中使用统一的状态符号：

| 符号 | 含义 |
|------|------|
| `[ ]` | 未开�?|
| `[/]` | 进行�?|
| `[x]` | 已完�?|
| `[~]` | 已取�?跳过 |

### 11.3 决策记忆分流规则

| 决策类型 | 记录位置 | doc_type |
|---------|---------|----------|
| 架构选型 | ADR | `adr` |
| 设计权衡 | rationale_log | `log` |
| 临时探索结论 | discussion_draft | `discussion_draft` |
| 经验证的最佳实�?| knowledge_entry | `knowledge_entry` |
| 流程/规则变更 | standard | `standard` |

---

## 12. 文件命名规范

文件命名遵循 [file-naming-standard.md](01_policies_and_standards/governance/document/file-naming-standard.md) v2.0.1（全小写 kebab-case，禁止大�?版本�?日期后缀）�?

本节仅补�?meta 域特有的 doc_type 命名约定——其余均�?file-naming-standard.md 为准�?

| doc_type | 命名格式 | 示例 |
|----------|---------|------|
| `standard` | `{topic}-standard.md` | `document-metadata-standard.md` |
| `adr` | `adr-{NNNN}-{title}.md` | `adr-0002-single-schema-with-phased-required-fields.md` |
| `blueprint` | `{module-name}-blueprint.md` | `data-source-blueprint.md` |
| `construction_plan` | `construction-plan-{layer}-{name}.md` | `construction-plan-l00-data-source.md` |
| `design` | `{topic}-design.md` | `capacity-assurance-design.md` |
| `plan` | `taskbook-{intent}.md` | `taskbook-backtest-engine-v2.md` |
| `roadmap` | `roadmap-{scope}-{YYYYMM}.md` | `roadmap-q2-202604.md` |
| `register` | `{topic}-registry.yaml` �?`{topic}-register.md` | `governance-asset-registry.yaml` |
| `index` | `index.md` | `index.md` |
| `readme` | `README.md` | `README.md` |
| `log` | `session-{YYYYMMDD}-{NNN}.md` | `session-20260428-001.md` |
| `knowledge_entry` | `KE-{NNN}-{topic}.md` | `KE-016-data-version-control.md` |
| `audit_report` | `{scan-type}-report-{YYYYMMDD}.md` | `sentinel-l1-report-20260428.md` |

---

## 13. 升格规则（Workspace �?Canonical�?

### 13.1 升格路径

```
外部独立工作区（`19_development_workspace/` 已删除，2026-05-02 迁至外部�? �?Draft / in_discussion
    �?内容稳定�?
02_enterprise_architecture/ �?governance/  �?review_ready
    �?Owner 审阅�?
01_policies_and_standards/ 相应子目�?�?02_enterprise_architecture/  �?active / accepted
```

### 13.2 升格操作

1. **只改 `status` �?*，不�?schema，不做字段迁�?
2. **只改文件位置**（`git mv`），不改文件名（除非违反命名规范�?
3. 升格时必须补齐目标阶段的必填字段
4. 升格 commit message：`promote: {old_path} -> {new_path} | status: {old} -> {new}`

### 13.3 降格规则

- `active` �?`deprecated`：需 Owner 审批 + 填写 `superseded_by`（必填，有替代品填路径，无替代品�?`"N/A"`�?
- `deprecated` �?`active`：需 Owner 审批（重新启用）
- 禁止跨级降格（`draft` 不能直接�?`deprecated`，必须先升格�?`active`�?

---

## 14. 违规检测规�?

### 14.1 自动检测项（pre-commit 执行�?

| ID | 检测内�?| 严重�?| 阻断�?|
|----|---------|--------|:------:|
| META-V01 | 缺少 frontmatter | P0 | �?|
| META-V02 | 缺少当前阶段必填字段 | P0 | �?|
| META-V03 | doc_type 使用未定义�?| P0 | �?|
| META-V04 | status 使用未定义�?| P1 | �?|
| META-V05 | ttl 使用未定义�?| P1 | �?|
| META-V06 | module_id 格式不符�?§5 规范 | P1 | �?|
| META-V07 | date 格式�?YYYY-MM-DD | P2 | �?warn |
| META-V08 | doc_type 与存放路径不匹配（�?.4�?| P2 | �?warn |
| META-V09 | AI 生成文件�?`created_by: agent` | P1 | �?|
| META-V10 | AI 生成文件�?`ttl` 字段 | P1 | �?|
| META-V11 | Deprecated 文件�?`superseded_by` | P1 | �?|
| META-V12 | `layer` 字段值不在合法列表中 | P2 | �?warn |
| META-V13 | `safety_level` 使用未定义�?| P1 | �?|
| META-V14 | `evolution_policy` 使用未定义�?| P1 | �?|
| META-V15 | `construction_plan` �?`blueprint_refs` | P1 | �?|
| META-V16 | `blueprint_refs` 引用的蓝图路径不存在 | P0 | �?|
| META-V17 | `blueprint_refs` 引用的蓝�?status �?deprecated | P0 | �?|
| META-V18 | `governance_family` 使用未定义�?| P2 | �?warn |
| META-V19 | `ai_capability_slot` 使用未定义�?| P2 | �?warn |
| META-V20 | 两个以上 `status: active` + `doc_type: standard` 文件对同一领域声明 `唯一真源`（SSoT�?| P0 | �?|
| META-V21 | `index.md` 清单条目描述的文件状态与实际文件�?frontmatter `status` 不一�?| P0 | �?|

### 14.2 人工审查�?

| ID | 审查内容 | 频率 |
|----|---------|------|
| META-R01 | doc_type 语义是否准确（不是路径匹配就一定对�?| 每月 |
| META-R02 | `summary` 是否能帮�?AI 理解文档大意 | 每月 |
| META-R03 | `tags` 是否覆盖�?AI 检索需要的关键�?| 每季�?|

---

## 15. Schema 漂移防护机制

### 15.1 核心原则

**一个项目，一�?schema，没有例外�?* 所有工具、AI 员工、脚本读�?doc_type 合法值、字段定义时，只看本文件�?

### 15.2 防护手段

| 手段 | 说明 |
|------|------|
| **单一真源** | 本文件是 doc_type 受控词表和字段定义的唯一权威来源 |
| **自动生成** | `frontmatter-schema.json` 从本文件自动生成，禁止手�?|
| **pre-commit 校验** | 提交时自动校�?frontmatter 合规�?|
| **新增值走 ADR** | 新增 doc_type 必须�?ADR，审批后更新本文�?|
| **定期扫描** | 每月运行全项�?frontmatter 合规扫描，发现漂移立即报�?|
| **版本�?* | 本文件变更时更新 `version` 字段，`frontmatter-schema.json` 同步更新版本�?|

### 15.3 漂移修复流程

1. 发现漂移（扫描报�?/ AI 自检 / 人工审查�?
2. 判断漂移类型�?
   - **字段名漂�?*（如 `doc_type: standard` vs `doc_type: governance_standard`）→ 以本文件为准，修正文�?
   - **新增值漂�?*（如使用�?`doc_type: policy`）→ 判断是否需要新增合法值；如需要，�?KB 决策记录流程；如不需要，修正为现有合法�?
   - **缺失字段漂移**（如 Active 文件�?`layer`）→ 补齐字段
3. 修正后运行全项目合规扫描确认

---

## 16. 与专业机构对照表

| 本项目字�?| IETF AAT | OpenLineage | MLflow | Databricks UC | ISO 11179 |
|-----------|----------|-------------|--------|---------------|-----------|
| `author_agent` | agent_id | producer.runId | �?| created_by | �?|
| `execution_model` | model_id | job.name | �?| �?| �?|
| `derived_from` | �?| inputs | �?| �?| �?|
| `provenance` | �?| producer | �?| �?| registration_authority |
| `compliance_tags` | �?| �?| �?| �?| �?|
| `human_override` | human_override | �?| �?| �?| �?|
| `review_status` | �?| �?| status | �?| �?|
| `safety_level` | risk_score | �?| �?| �?| �?|
| `ai_autonomy` | trust_level | �?| �?| �?| �?|
| `evolution_policy` | �?| �?| lifecycle_stage | �?| �?|
| `doc_type` | �?| �?| artifact_type | �?| data_element |
| `status` (DocStatus) | �?| �?| status | �?| registration_status |
| `status` (TaskStatus) | task_status | job.status | �?| �?| �?|
| `status` (KeStatus) | �?| lifecycleState | �?| �?| �?|
| `category` | �?| �?| �?| �?| �?|
| `domain` | �?| namespace | �?| catalog | �?|
| `namespace` | �?| namespace | �?| schema | �?|
| `module_id` | �?| �?| name | �?| identifier |
| `ttl` | �?| �?| �?| �?| �?|
| `blueprint_refs` | �?| inputs | �?| �?| �?|

**关键发现**�?
1. **identity vs execution 拆分**�? 家机�?100% 拆分身份（agent_id/producer）与执行（model_id/job），无例�?
2. **status 三域分离**：文�?任务/知识各有独立状态机，专业机构同样分离（MLflow: status, IETF: task_status, OpenLineage: lifecycleState�?
3. **audit 字段独立**：IETF AAT �?`human_override`，SR 11-7 要求 `review_status`，EU AI Act 要求 `compliance_tags`
4. **provenance 是行业术�?*：OpenLineage �?W3C PROV 都用 `provenance`，运行时溯源用不同词（本项目�?`WriteTrace`�?

---

## 17. 与其他标准的关系

| 标准 | 关系 | 交互�?|
|------|------|--------|
| `unified-numbering-standard.md` | 互补 | 本文�?§5 定义 module_id �?DOMAIN 格式，该文件定义 L{XX} 层编号格�?|
| `document-lifecycle-standard.md` | 下游 | 本文件定�?status 语义，该文件定义 TTL 管理和快照规�?|
| `file-naming-standard.md` | 下游 | 本文�?§9 定义�?doc_type 的命名约定，该文件定义通用命名规则 |
| `encoding-safety-standard.md` | 独立 | 编码安全与本标准无冲�?|
| `ai-autonomy-authority-registry.md` | 上游 | 本文�?§7 �?`ai_autonomy` 字段值与该注册表三层模型对齐 |
| `task-card-standard.md` | 下游 | 任务卡的 `ai_autonomy` 字段遵循本文�?§7 定义 |
| `ssot-authority-map.md` | 上游 | 本文�?§1.3 �?SSoT 声明与该文件对齐 |

---

## 18. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 6.0.1 | 2026-05-06 | §14.1：新�?**META-V21**——`index.md` 清单条目与实际指向文件的 frontmatter `status` 不一致（P0，对�?PS-STD-012 §2.1）�?|
| 5.9.0 | 2026-05-02 | **SSoT 根治——单层真�?*：�?.2 完整表（23 行）→速查引用�?0+13 的速查列表 + vocabulary YAML 指针）。�?.3 移除 2 个已废弃类型行（ai_governance/reference），标注"完整映射�?YAML"。�?.4 移除 4 个已废弃类型行（ai_governance/candidate_pool/discussion_draft/reference），新增 operational_rule/protocol/vocabulary/contract/terminology/template/declaration/service_spec 行，标注 YAML 优先。�?.5 流程简化："�?YAML 即可，本表不需要手动同�?。根因：双层手动同步是结构性缺陷——对�?12 家专业机构（K8s/Terraform/OpenAPI/Google SRE/Anthropic/Cursor/AGENTS.md/ComfyUI 等），无一使用"人工同步双层真源"。方案选型详细论证�?Session Log�?|
| 5.8.0 | 2026-05-02 | **vocabulary YAML 对齐**：�?.2 完整词表�?25�?3 种——移�?5 个已废弃 doc_type（checklist/ai_governance/candidate_pool/discussion_draft/reference，已�?vocabulary deprecated_values 中），新�?3 �?vocabulary 已注册但本表缺失的类型（vocabulary/contract/declaration）。�?.2.1 子集�?8�?0 值（新增 vocabulary/contract）。�? TTL 表新�?periodic_review_90d（ttl-vocabulary.yaml 已有）。新�?YAML 优先声明——本表从 vocabulary YAML 派生，冲突以 YAML 为准。根因：词汇表清�?新增�?metadata 手动同步遗漏�?5 �?deprecated 删除 + 3 个新增�?|
| 5.7.0 | 2026-05-02 | **生命周期引用约束（Lifecycle Reference Constraint�?*：�?.1.1 新增 LRC-001~005 规则——draft 文件不可�?active 文件通过 depends_on 引用（对�?Kubernetes Admission Controller + ITIL Change Enablement）。定�?lifecycle_stage 字段�? 值：draft/blueprint_reviewed/construction_reviewed/active，beta 落地）。动机：审计发现 GOV-MOD-002（draft）被 6 �?active 文件量产级引用——status �?depends_on 之间没有互锁机制�?|
| 5.6.0 | 2026-05-02 | §3.2 拆分 `design` �?`architecture_view`（正式架构视图）+ `design`（工作级设计），消除"一个词两种文档"歧义。doc_type 25 种�?1) §3.2 #6 design 含义�?架构视图/设计文档"�?设计文档（工作级设计，非正式架构视图�?，路径从 `02_enterprise_architecture/`→`02_enterprise_architecture/designs/`�?2) §3.2 新增 #25 architecture_view（正式目标架构，TOGAF/ArchiMate 级），路�?`02_enterprise_architecture/target-architecture/`�?3) §3.3 组合示例 design+layer→architecture_view+layer�?4) §3.4 路径映射拆分�?architecture_view（target-architecture/�? design（designs/），互禁对方目录�?5) §1.3 总种数、�?.5 表、�?.5、�?4 各计数引用同步更新�?6) 相关 Python 脚本同步更新：check_frontmatter_metadata.py DOC_TYPE_LEGAL + architecture_view、doc_type-vocabulary.yaml + architecture_view |
| 5.5.0 | 2026-05-01 | §3.2 拆分 `plan` �?`plan`（任务书�? `roadmap`（路线图），消除"三合一"歧义。`plan` �?执行计划"语义归入 `construction_plan`。doc_type 24 种�?1) §3.2 完整词表拆分 plan #7 �?plan #7（任务书�? roadmap #8（路线图），#8~#23 顺移�?#9~#24�?2) §3.3 组合示例拆分 plan+layer→roadmap+layer�?3) §3.4 路径映射 plan 移除 `04_construction_plans/`，新�?roadmap 行�?4) §2.5 表新�?roadmap 列�?5) §2.6 新增一致性约�?#11（roadmap �?declarative）�?6) §12 命名 plan �?`construction-plan` 改为 `taskbook`，新�?roadmap 命名�?7) §11 正文模板 plan 改为"任务�?，新�?roadmap 模板�?8) §1.3 总种数、�? B 域范围、各枚举引用同步更新�?9) 相关 Python 脚本同步更新：check_frontmatter_metadata.py DOC_TYPE_LEGAL + roadmap、triage.py VALID_DOC_TYPES + roadmap、doc_type-vocabulary.yaml + roadmap |
| 5.4.0 | 2026-05-01 | §2.5 表扩�?+3 列（adr/blueprint/construction_plan）消除模板文件的 per-doc_type 字段约束盲区；�?.6 +3 条一致性约束（#8/#9/#10）对�?rule_form-vocabulary.yaml 已有映射；条件说明表同步更新 5 行（�?layer/classification/verifiability/valid_from/evolution_policy 对新�?doc_type 的条件说明） |
| 5.3.0 | 2026-05-01 | §1.3 加入 YAML 子类型分类（document_yaml / registry_yaml），解决 _registry/ �?6 �?.yaml 文件�?depends_on �?frontmatter 字段的根本问�?|
| 5.2.0 | 2026-05-01 | 门头精简 + 上下文压缩�?1) 删除已解决问�?1（doc_type边界模糊，v5.0.0已解决）�?2) 拆分预判条件后移至文件末尾�?3) §1.0 最小必读路径从表格压缩为单行声明（~300→~40 Token）。版本号 minor +1�?|
| 5.1.9 | 2026-05-01 | 回退编辑�?1) 删除 §3.7（doc_type 迁移方案拆分后的残桩）——迁移方案独立文�?doc_type-migration-plan.md 已被 Owner 指令删除（不属于 meta/ 目录责任范围）�?2) 删除 dead link。版本号 patch +1�?|
| 5.1.8 | 2026-05-01 | 编辑性压缩�?1) §3.7 迁移方案�?5 行）拆分为独立文�?doc_type-migration-plan.md，降低注册表上下文开销�?2) §5.8 编号表从 13 个子表（131 行）压缩为单汇总表�?8 行），去 60% 占位行。版本号 patch +1�?|
| 5.1.7 | 2026-05-01 | 新增 §1.0 最小必读路径（5 步，~1000 Token），解决 2038 行注册表对新 AI session 的上下文开销问题。新 AI 读完即可开始施工。版本号 patch +1�?|
| 5.1.6 | 2026-05-01 | 新增 META-V20 违规检测规则：扫描所�?`status: active` + `doc_type: standard` 文件�?SSoT 声明章节，检测两个以上文件对同一领域声称唯一真源的冲突（P0 阻断，pre-commit 自动执行）。杜�?两个文件说自己管同一件事"�?SSoT 分裂�?|
| 5.1.5 | 2026-05-01 | 编辑性变更——frontmatter 字段排序对齐 PS-STD-001 §2.3（date 移至 created_by 之后，ai_autonomy 移至 verifiability 之后，supersedes 移至 verifiability 之后）。版本号 patch +1�?|
| 5.1.4 | 2026-05-01 | 编辑性压缩与跨文件对齐。�?2 文件命名规范：删除与 file-naming-standard.md 重复�?§12.1�? 条通用规则），§12.2 前加入引用声�?�?file-naming-standard.md 为准"。版本号 patch +1（编辑性变更）�?|
| 5.1.3 | 2026-05-01 | PS-STD-009+010 合并收尾�?1) §5.8.1：PS-STD-010 �?🆕 新建"�?📋 可用（已合并�?PS-STD-009�?（生命周期内容合并至规则治理标准）�?2) PS-STD-011 文件名更新为 `governance-methodology-standard.md`（补�?`-standard` 后缀以符合同目录命名约定）�?3) 更新 PS-STD-001 自身 `version` �?5.1.3�?|
| 5.1.2 | 2026-05-01 | meta/ 系统性自审收尾�?1) §5.8.1 注册 META-GLS-001（glossary.md——术语表）和 PS-STD-006（governance-metrics-standard.md——治理度量标准）�?2) PS-STD-006 编号�?📋 可用→�?新建�?|
| 5.1.1 | 2026-05-01 | meta/ 系统性自审�?1) frontmatter 字段修正：`version` number→string（加引号，防 YAML 解析为浮点数）、`date` 更新�?2026-05-01（同步实际修改日期）、`valid_from` 更新�?2026-04-28（首次注册生效日）�?2) §5.8.1 幽灵条目清理：删除声称存在但实际不存在的 PS-STD-006/007（错误标记为"�?已有，保�?），标注 PS-STD-005~007 �?📋 可用（待分配�?，编号可回收复用�?3) §5.8.1 新增 PS-STD-012（rule-verification-standard.md）和 META-IDX-001（index.md），均为 meta/ 系统审查补齐�?|
| 5.1.0 | 2026-05-01 | B5 审查连带修复�?1) §2.1 字段表：修正 8 处过时节号引用（module_id §6→�?、status §7→�?、layer §6.3→�?.5、safety_level/evolution_policy/ai_autonomy/provenance/author_agent/governance_family �?§8.x→�?0.x）�?2) §2.8 禁止行为表与 §3.6 #5 去重：合�?#1+#2→跨域引用，互补不重叠�?3) §2.6 新增"架构公民原则"说明块：`stable + immutable_core` 合法（约�?#1 是单向的，逆面不成立），附合法映射光谱防误判�?|
| 4.4.0 | 2026-04-29 | 新增 §9.5 layer 枚举�?4值）、�?.6 source_type 枚举�?值）、�?.7 priority 枚举�?值）；�? �?4 个跨域枚举扩展为 7 个；更新 §1.4 SSoT 声明拆分 §9.1~§9.4 �?§9.5~§9.7 两行；标注代码真源需同步对齐（triage.py VALID_LAYERS、kms-entry-schema.md source_type�?*shared/schemas** Priority 演进�?|
| 4.4.0 | 2026-04-29 | 新增文件头部"⚠️ 待解决重大问�?区域，记�?3 个已识别但未解决的问题（doc_type词表边界模糊、旧长名未迁移、internal待迁移），确保每次打开本文件都能看�?|
| 4.3.0 | 2026-04-29 | **真元规则裁定**：�?.1 DocStatus �?7 种精简�?3 种（draft/active/deprecated），删除 in_discussion/review_ready/accepted/superseded；理由：Vibe Coding语境下AI只需知道"能不能用"、废弃原因靠superseded_by字段区分、审阅由review_status单独管、不按doc_type分状态；§4.5 大小写约定从"统一小写"升级�?枚举值小�?标识符大�?二元规则（�?.5.1~§4.5.5）；§4.6 classification 二分法（public/confidential，删除internal）；§2.2 分阶段闸门删除Accepted行、Deprecated必填superseded_by；�?3.3 降格规则同步更新 |
| 4.2.0 | 2026-04-29 | 新增 §1.5 消费者注册表（对�?ISO 11179 §6.2 Stewardship），4 层分级（Tier 1 硬编码枚�?Tier 2 引用权威/Tier 3 字段对齐/Tier 4 已废弃）+ 变更同步规则矩阵 |
| 4.1.0 | 2026-04-29 | 三域 status 分离（DocStatus 7�?TaskStatus 10�?KeStatus 10值）；新�?§7 �?B 任务卡字段（18字段）；新增 §8 �?C AI 治理字段交叉索引 + provenance 双定义澄清（frontmatter `provenance` vs 代码 `WriteTrace`）；新增 §9 受控枚举定义（category 10�?domain 10�?namespace 7�?AgentRole 6值）；layer 格式确认为全小写 `l00_data_source`；新�?§16 与专业机构对照表；章节重新编号（§7-§18�?|
| 4.0.0 | 2026-04-28 | 重命名为元数据注册表（metadata-registry.md），扩展为全项目三域字段真源；`primary_model` �?`execution_model`（对�?IETF model_id）；`ai_model` �?`author_agent`（对�?IETF agent_id）；明确�?A（文�?frontmatter�? �?B（任务卡�? �?C（AI 治理）三层架构；新增 4 个审计字段：`compliance_tags`（�?.13）、`human_override`（�?.14）、`last_reviewed_by`（�?.15）、`review_status`（�?.16）；新增 §4 �?B 任务卡字段、�? �?C AI 治理字段；新�?§12 与专业机构对照表；章节编�?§7→�?、�?→�? |
| 3.6.0 | 2026-04-28 | 字段标准最终定版：新增 `safety_level`（�?.10）、`evolution_policy`（�?.11）、`blueprint_refs`（�?.12）三个字段；`governance_family` 合法值加 `D`（共享底座）；`ai_capability_slot` 合法值加 `active`（已激活）；`primary_model` �?`ai_model` 明确语义分工、不可合并；新增 META-V13~V19 七项违规检测；字段排序约定更新（�?.3�?|
| 3.5.0 | 2026-04-28 | 拆分 `design` 为三种独�?doc_type：`blueprint`（模块蓝图）、`construction_plan`（施工图纸）、`design`（架构视图）；蓝图和施工图各自拥有独立正文模板；蓝图模板侧重架构决策记录�?模块边界+接口契约+约束条件；施工图模板侧重依赖蓝图+来源追溯表（§8 自包含性）+实施步骤+施工状态双字段；doc_type �?19 种扩展为 21 �?|
| 3.4.0 | 2026-04-28 | 撤回 primary_model+ai_model 合并：保留两个字段，标注"未来统一�?ai_model"但当前不执行（涉�?18 个代码文�?数据库迁移，直接合并会运行时崩溃）；补全三层口子 9 项预留（§7.8）；AI 治理字段完整覆盖 49 �?|
| 3.3.0 | 2026-04-28 | 修正 AI 员工字段：合�?primary_model �?ai_model 为统一 ai_model 字段；Session Log 专用字段（context_budget_used/knowledge_extracted/next_session_handover）从 frontmatter 移出为正文字段；新增 §7.8 三层口子预留 9 项（C/D/F �?3 项）；AC-2 四列字段 + 三层口子 9 �?= 13 �?AI 预留 |
| 3.2.0 | 2026-04-28 | 补全 AI 员工字段：新�?§7.5 模型选择字段（primary_model/model_rationale/fallback_model）、�?.6 Session Log 专用字段（ai_model/context_budget_used/knowledge_extracted/next_session_handover）、�?.7 治理系统 AI 预留字段（governance_family/ai_capability_slot/ai_autonomy_level_planned/ai_employee_count_planned）、�?.8 AI 决策日志说明（独�?schema，非 frontmatter�?|
| 3.1.0 | 2026-04-28 | doc_type �?17 种扩展为 19 种：新增 `policy`（强制规则，�?`standard` 拆出）、`reference`（参考文档）；`standard` 含义缩窄�?推荐做法"；`design` 扩展覆盖施工图；`plan` 缩窄为路线图/任务书；本文件自�?doc_type �?`standard` 改为 `policy` |
| 3.0.0 | 2026-04-28 | 合并 frontmatter-standard.md v1.0.0 + discussion-document-standard.md v2.0.0 + frontmatter-schema.json R4；doc_type �?13/15 种统一�?17 种短名；新增 AI 员工字段（�?）；新增分阶段必填闸门（§2.2）；新增 schema 漂移防护机制（�?2）；管辖范围从工作区扩展为全局 |
| 2.0.0 | 2026-04-17 | discussion-document-standard.md：取消双 schema，改为单一 schema + 分阶段必填闸门（ADR-0002�?|
| 1.0.0 | 2026-04-17 | discussion-document-standard.md：初始版本，沙盒�?正式档双 schema |
| 1.0.0 | 2026-04-22 | frontmatter-standard.md：从 discussion-document-standard.md 提取简化版�?3 �?doc_type 长名�?|
