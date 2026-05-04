---
module_id: PS-STD-002
title: ZephyrAlpha 标准文档模板
doc_type: standard
status: active
version: "3.2.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-01"
valid_from: "2026-04-29"
summary: "ZephyrAlpha 标准文档的元标准——定义三层模板体系（L1/L2/L3）。v3.2.0 ADR 从 L2 重分类至 L3（对标 Nygard ADR 轻量格式，信息性决策记录不应承受 L2 治理章负担）。v3.1.0 L1 引入标准子类型（行为规则/数据注册/宪法原则/格式定义），通用核心 6 章 + 条件性 12 章 + 消除 frontmatter-body 重复（§16/§17）。对标 ISO/IEC Directives Part 2（IS/TS/TR 分层）+ IETF BCP 14 + Anthropic CLAUDE.md AI 可消费性。氛围编程语境下，AI 是标准的主要消费者。"
ttl: permanent
tags: [meta-standard, template, governance, ssot, iso-11179]
rule_form: declarative
scope: global
stability: frozen
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "§2.1~§2.8", why: "frontmatter字段权威定义"}
supersedes:
  - path: docs/01_policies_and_standards/meta/rule-document-format-standard.md
    version: "1.0.0"
    reason: "v2.0.0 升级为标准文档模板，新增治理层必要章节（SSoT 声明、消费者注册表、变更同步规则、受控枚举管理）"
ai_autonomy: immutable_core
---

# ZephyrAlpha 标准文档模板

> **module_id**: PS-STD-002 | **version**: 3.2.0 | **status**: active
>
> 本文档是 ZephyrAlpha 项目所有 **policy / standard** 类文档的**元标准**。
> 它规定了：一份标准文档**必须包含哪些章节**、**必须声明哪些治理信息**、
> **变更时必须同步哪些消费者**。
>
> v3.2.0 `adr` 从 L2 重分类至 L3——ADR 对标 Nygard ADR 轻量格式（信息性决策记录），
> 不应承受 L2 的 10 章治理负担。L3 只需 4 个 MUST 章。
>
> v3.1.0 L1 引入**标准子类型**——行为规则型、数据注册表型、宪法原则型、格式定义型。
> 不同子类型适用不同的章节集合，消除"所有标准必须包含所有 19 章"的一刀切。
>
> 对标：ISO/IEC Directives Part 2（IS/TS/TR 分层）、IETF BCP 14（MUST/SHOULD/MAY）、
> OpenLineage（producer/consumer 契约）。
>
> **根因**：元数据注册表（PS-STD-001）在 v4.2.0 之前缺失消费者注册表、
> 受控枚举与代码层的同步规则、SSoT 声明，导致字段改名后 18+ 个代码文件
> 需要人工逐个排查。本模板确保新标准不再重蹈覆辙。

---

## 1. 目的与范围

### 1.1 目的

确保 ZephyrAlpha 项目的每一份标准文档都具备：

- **可追溯**：谁在用这份标准、改了会影响谁
- **可同步**：变更时知道要同步更新哪些文件
- **可仲裁**：与其他标准冲突时知道以谁为准
- **可验证**：pre-commit / CI 可以自动检测违规

### 1.2 责任范围（本标准管什么）

本标准管理以下内容：
- 标准文档的**章节结构**——L1/L2/L3 三层模板体系，每层必须包含哪些章节
- 标准文档的**治理机制**——SSoT 声明、消费者注册表、变更同步规则
- 标准文档的**AI 可消费性**——自治权限标注、可验证性标注、自检清单

### 1.3 责任边界（本标准不管什么）

本标准**不**覆盖以下内容：
- frontmatter 字段的合法值和类型定义 → 以 PS-STD-001（metadata-registry.md）为准
- 文件命名规则 → 以 GOV-DOC-003（file-naming-standard.md）为准
- 文档生命周期（TTL、归档、废弃）→ 以 GOV-DOC-006（document-lifecycle-standard.md）为准
- 规则文件的变更审批流程 → 以 PS-STD-009（rule-lifecycle-and-change-standard.md）为准

### 1.4 适用范围

本模板采用**三层模板体系**（对标 ISO/IEC Directives Part 2、IETF RFC 7841、IEEE SA Operations Manual、W3C Process Document 的分层做法）：

| 模板层 | 适用 doc_type | 对标专业机构 | 规范性语言 |
|--------|-------------|------------|----------|
| **L1 治理模板** | `policy` `standard` `ai_governance` | ISO IS / IETF Standards Track / IEEE Standard / W3C REC | MUST/SHOULD/MAY |
|   | → 含 4 种**标准子类型**（§3.2）：行为规则型、数据注册表型、宪法原则型、格式定义型——不同子类型适用不同章节集合 |
| **L2 设计模板**（中等 10 章） | `blueprint` `design` `service_spec` | ISO TS / IETF BCP / IEEE RecPractice | SHOULD/MAY |

> 注：`construction_plan` 原为独立 L2 模板，已于 2026-05-02 合并入 `blueprint`（§12 施工指引）。对历史文档 `doc_type: construction_plan` 仍保留。
| **L3 基础模板**（轻量 5 章） | `adr` 及其他所有 doc_type | ISO TR / IETF Informational / IEEE Guide / W3C Note | 禁止 MUST/SHOULD |

> **核心区分机制**（四家专业机构一致）：规范性语言是分层的核心。
> L1 允许最高级规范性语言（MUST），L2 降级为 SHOULD，L3 完全禁止规范性语言。
> 这不是随意限制——信息性文档使用 MUST 会导致读者误以为有强制约束力。

各层模板的章节清单见 §3.1。L1 标准的子类型与章节适用性见 §3.2。

### 1.5 术语

| 术语 | 含义 |
|------|------|
| **SSoT** | Single Source of Truth，唯一真源 |
| **消费者** | 直接依赖本标准字段定义/枚举值/校验规则的文件 |
| **Tier 1 消费者** | 硬编码了本标准枚举值的文件（变更必须同步） |
| **受控枚举** | 值集合由本标准定义、不允许自由扩展的枚举字段 |
| **变更同步** | 标准内容变更后，必须同 commit 更新所有 Tier 1 消费者 |

---

## 2. Frontmatter 必填字段

### 2.1 所有 policy/standard 文档的必填 frontmatter

> **SSoT：frontmatter 模板的唯一真源是 `templates/` 目录下的骨架文件。**
> AI 创建新文件时，从 `templates/` 目录下对应的骨架文件复制 frontmatter。
>
> 本模板不再重复定义 frontmatter 字段值。合法值以 [metadata-registry.md](01_policies_and_standards/meta/metadata-registry.md)（PS-STD-001）为准，空骨架以 `templates/` 目录为准。

### 2.2 可选但推荐的 frontmatter

```yaml
supersedes:                          # 取代了哪些旧文档
  - path: "旧文档路径"
    version: "X.Y.Z"
    reason: "取代原因"
superseded_by: null                  # 被哪个新文档取代（Deprecated 时必填）
summary: "一段话说清本文档的目的和核心内容"  # 摘要
```

### 2.3 frontmatter 字段定义的权威来源

所有 frontmatter 字段的类型、合法值、必填阶段，以 [metadata-registry.md](01_policies_and_standards/meta/metadata-registry.md)（PS-STD-001）为准。本模板不再重复定义。

---

## 3. 章节体系

> 本章定义三层模板（L1/L2/L3）的章节清单和 L1 标准子类型的章节适用性规则。
> v3.1.0 起，L1 不再要求所有标准包含所有 19 章——不同子类型适用不同的章节集合。
> pre-commit 检测时，按子类型对应的章节要求判定合规，而非一刀切检查 19 章。

### 3.1 章节清单（三层模板体系）

> 对标 ISO/IEC Directives Part 2 的分层做法：IS/TS/TR 各有不同章节要求。
> 核心区分机制：规范性语言层级（MUST > SHOULD > 禁止）。

#### L1 治理模板（`policy` `standard` `ai_governance`）

对标：ISO International Standard / IETF Standards Track / IEEE Standard / W3C Recommendation

> v3.1.0：下表列出 L1 模板的全部 19 章基准清单。实际必含章节取决于子类型（见 §3.2），
> 不是所有标准都需要全部 19 章。§16 和 §17 已由 frontmatter 字段替代。

| # | 章节 | 必要性 | 说明 |
|---|------|:------:|------|
| 1 | **目的与范围** | MUST | 包含 §1.2 责任范围（管什么）+ §1.3 责任边界（不管什么） |
| 2 | **SSoT 声明** | MUST | 声明本文档是什么的真源，取代了什么，与什么互补 |
| 3 | **受控枚举定义** | SHOULD | 如果本文档定义了枚举值，必须列出完整清单和代码真源 |
| 4 | **消费者注册表** | MUST | 列出所有依赖本文档的文件，分 Tier |
| 5 | **主体内容** | MUST | 规则条款，使用 MUST/SHOULD/MAY |
| 6 | **禁止行为** | MUST | 明确列出违反本规则的禁止操作 |
| 7 | **变更同步规则** | MUST | 变更类型 × 消费者 Tier 的同步要求矩阵 |
| 8 | **修改条件** | MUST | 修改本文档需要满足的条件和审批流程 |
| 9 | **标准间引用规范** | MUST | normative（必须遵守）vs informative（仅供参考）引用 |
| 10 | **废弃流程** | MUST | 取代→通知消费者→过渡期→确认无引用→删除 |
| 11 | **审查周期** | SHOULD | ISO 11179 要求定期审查标准是否仍然适用 |
| 12 | **异常豁免机制** | SHOULD | 什么时候可以违反标准？谁批准？记录在哪？ |
| 13 | **与 PS-STD-001 的字段不重复声明** | MUST | 防止两个标准都定义同一个字段导致漂移 |
| 14 | **跨标准字段交叉引用** | SHOULD | 改一个字段名时，知道哪些标准也用了这个字段 |
| 15 | **AI 可消费性声明** | MUST | 氛围编程语境下，AI 能否无歧义理解并执行本标准 |
| 16 | **AI 自治权限标注** | ~~MUST~~ → 见 frontmatter | v3.1.0 起由 frontmatter `ai_autonomy` 字段替代，禁止 body 重复 |
| 17 | **可验证性标注** | ~~MUST~~ → 见 frontmatter | v3.1.0 起由 frontmatter `verifiability` 字段替代，禁止 body 重复 |
| 18 | **完整性自检清单** | MUST | AI/人类创建标准时逐项勾选的 checklist |
| 19 | **变更记录** | MUST | 版本历史表 |

### 3.2 L1 标准子类型与章节适用性

> v3.1.0 新增。对标 ISO/IEC Directives Part 2：IS/TS/TR 有不同章节要求——ISO 不搞一套模板管所有。
> 同样，L1 治理标准下存在不同性质的标准，一刀切要求所有 19 章会造成空壳章节和 Token 浪费。

#### 3.2.1 通用核心（Common Core）

以下 6 个章节是**所有 L1 标准必须包含**的，不论子类型：

| # | 章节 | 理由 |
|---|------|------|
| 1 | **目的与范围**（含责任范围+责任边界） | AI 必须知道管什么、特别是**不管什么**——责任边界模糊 = SSoT 冲突 |
| 2 | **SSoT 声明** | AI 遇到定义冲突时知道以谁为准 |
| 5 | **主体内容** | 规则条款本身 |
| 9 | **标准间引用规范**（normative/informative） | AI 必须区分强制引用和参考引用——改了 normative 引用源你也得跟着改 |
| 15 | **AI 可消费性声明** | 氛围编程核心章节——直接告诉 AI 能否无歧义执行本标准、最小必读路径、Token 预算 |
| 19 | **变更记录** | 版本追踪 |

#### 3.2.2 条件性章节（Conditional Chapters）

以下章节仅在标准满足特定条件时要求必含。不满足条件时写一行声明即可或不写：

| # | 章节 | 触发条件 | 不适用时 |
|---|------|---------|---------|
| 3 | **受控枚举定义** | 标准定义了受控枚举值 | "本文档不定义受控枚举"（1 行） |
| 4 | **消费者注册表** | 标准有明确的下游 Tier 1/2/3 消费者 | 宪法级文件"所有人都是消费者"→ 不写 |
| 6 | **禁止行为** | 标准定义了行为规则和违规后果 | 注册表的"禁止"内嵌在字段约束中 → 不写 |
| 7 | **变更同步规则** | `stability ≠ frozen`（标准会变化） | frozen → 不写 |
| 8 | **修改条件** | `stability ≠ frozen` | frozen → 不写 |
| 10 | **废弃流程** | `stability ≠ frozen` 且可能被取代 | frozen 宪法文件 → 不写 |
| 11 | **审查周期** | 所有标准都**应该**有（SHOULD 级） | 本已是 SHOULD——建议但非阻断 |
| 12 | **异常豁免机制** | 标准含 COND 级别规则（不是纯 ABS） | ABS-only（如宪法）→ 不写 |
| 13 | **字段不重复声明** | 标准定义了 PS-STD-001 之外的字段 | 不定义字段的标准 → 不写 |
| 14 | **跨标准字段交叉引用** | 标准定义的字段被其他标准引用 | 无交叉引用 → 不写 |
| 18 | **完整性自检清单** | 人类创建的标准（需人工逐项检查） | AI 生成标准 → SHOULD（可选——AI 自查是自指涉空洞） |

#### 3.2.3 已消除的重复章节

**§16（AI 自治权限标注）和 §17（可验证性标注）不再作为独立 MUST 章节**。

这两类信息已在 frontmatter 中由以下字段声明：
- `ai_autonomy`：immutable_core / human_gated / ai_editable
- `verifiability`：automated / manual / subjective

**规则**：禁止在 body 中用 prose 章节重复 frontmatter 已声明的信息。frontmatter 是机器可读的 SSoT——AI 读 YAML 零歧义，读 prose 需要推理。重复不仅浪费 Token，还会产生漂移风险（frontmatter 说 A，body 说 B）。

每条规则级别的详细自治权限和验证方式，统一在 §15（AI 可消费性声明）中说明——作为"本标准中的规则如何分配给三种 ai_autonomy 级别"的总览，而非逐条标注。

#### 3.2.4 标准子类型推导表

基于通用核心 + 条件性章节的组合，L1 标准自然分化为 4 种子类型：

| # | 章节 | 行为规则型 | 数据注册表型 | 宪法原则型 | 格式定义型 |
|---|------|:---:|:---:|:---:|:---:|
| 1 | 目的与范围 | ✅ | ✅ | ✅ | ✅ |
| 2 | SSoT 声明 | ✅ | ✅ | ✅ | ✅ |
| 3 | 受控枚举定义 | ▲ | ▲ | — | ▲ |
| 4 | 消费者注册表 | ✅ | ✅ | — | ✅ |
| 5 | 主体内容 | ✅ | ✅ | ✅ | ✅ |
| 6 | 禁止行为 | ✅ | — | — | ✅ |
| 7 | 变更同步规则 | ✅ | ✅ | — | ▲ |
| 8 | 修改条件 | ✅ | ✅ | — | ▲ |
| 9 | 标准间引用规范 | ✅ | ✅ | ✅ | ✅ |
| 10 | 废弃流程 | ✅ | ✅ | — | ▲ |
| 11 | 审查周期 | ○ | ○ | ○ | ○ |
| 12 | 异常豁免机制 | ▲ | — | ▲ | ▲ |
| 13 | 字段不重复声明 | ▲ | ○ | — | — |
| 14 | 跨标准字段交叉引用 | ▲ | ○ | — | — |
| 15 | AI 可消费性声明 | ✅ | ✅ | ✅ | ✅ |
| 18 | 完整性自检清单 | ○ | ○ | ○ | ○ |
| 19 | 变更记录 | ✅ | ✅ | ✅ | ✅ |

**图例**：✅ Common Core（必含）| ▲ 条件性（触发时必含，不触发时不写）| ○ SHOULD（建议含，缺了不阻断）| — 不适用

**子类型定义与示例**：

| 子类型 | 特征 | 示例 | 可含章节数 |
|--------|------|------|:---:|
| **行为规则型** | 定义"能做/不能做什么"、违规后果、替代方案。核心是 MUST/MUST NOT。 | PS-STD-003（禁止行为）、PS-STD-004（分类仲裁） | 10~15 |
| **数据注册表型** | 定义数据结构、字段合法值、验证规则。核心是字段表 + 枚举清单。 | PS-STD-001（元数据注册表） | 8~13 |
| **宪法原则型** | 定义不可变底层原则、宪法级约束。通常 frozen、短小精悍。 | PS-STD-000（宪法）、PS-STD-011（方法论） | 6~9 |
| **格式定义型** | 定义文档格式/验证流程/模板本身。自指涉——定义格式的标准自身也是标准。 | PS-STD-002（本文档）、PS-STD-012（验证标准） | 9~12 |

> **子类型判定方法**：读标准的 §1 目的与范围和 frontmatter 的 `stability` + `ai_autonomy` 字段。
> `frozen` + `immutable_core` → 宪法原则型；定义了 frontmatter 字段 → 数据注册表型；
> 定义了行为约束表（禁止行为/替代方案）→ 行为规则型；定义了格式/流程 → 格式定义型。
> 如果跨类型（同时有行为规则和格式定义），按"更严格的子类型"归类。

#### L2 设计模板（`blueprint` `design` `service_spec`）

> **2026-05-02 更新**：`construction_plan` 原为独立 L2 模板，现已合并入 `blueprint`。蓝图 §1-§11 承载架构决策，§12 承载施工指引。`construction_plan` doc_type 仅对历史文档保留。

对标：ISO Technical Specification / IETF BCP / IEEE Recommended Practice

| # | 章节 | 必要性 | 说明 |
|---|------|:------:|------|
| 1 | **目的与范围** | MUST | 包含 §1.2 责任范围 + §1.3 责任边界 |
| 2 | **SSoT 声明** | MUST | 声明本文档是什么的真源 |
| 3 | **受控枚举定义** | SHOULD | 如有枚举，列出清单 |
| 4 | **消费者注册表** | MUST | Tier 1/2/3 分级（设计文档的下游消费者是施工图和代码） |
| 5 | **主体内容** | MUST | 使用 SHOULD/MAY（L2 禁止使用 MUST） |
| 6 | **禁止行为** | SHOULD | 列出设计约束 |
| 7 | **变更同步规则** | MUST | 变更时同步下游施工图和代码 |
| 8 | **修改条件** | MUST | 修改审批流程 |
| 9 | **标准间引用规范** | SHOULD | normative/informative 分离 |
| 10 | **已实现代码路径索引** | MUST | 蓝图覆盖范围内所有已实现代码的完整路径表（AGENTS.md §6.14 蓝图-代码同步强制约定）。含：模块ID / 实现状态 / 源码路径 / 测试路径 / 配置路径。CI 门禁 `validate_blueprint_code_sync.py` 自动校验此表与磁盘实际一致 |
| 11 | **变更记录** | MUST | 版本历史 |

> **L2 与 L1 的关键差异**：
> - L2 禁止使用 MUST（只有 L1 治理文档才能设强制要求）
> - L2 不需要审查周期、异常豁免、AI 自治权限标注（这些是治理层专属）
> - L2 不需要完整性自检清单（设计文档有各自专用模板的 checklist）

#### L3 基础模板（`adr` 及其他所有 doc_type）

对标：ISO Technical Report / IETF Informational / IEEE Guide / W3C Note

> v3.2.0：`adr` 从 L2 重分类至 L3。ADR（Architecture Decision Record）对标 Michael Nygard 原始格式（5 段极轻结构：Context → Decision → Rationale → Consequences → Alternatives），性质是信息性决策记录，非设计规范。L2 的 10 章治理要求不适合 ADR——强制补治理章会导致 ADR 失去"快写快读"的核心价值。

| # | 章节 | 必要性 | 说明 |
|---|------|:------:|------|
| 1 | **目的与范围** | MUST | 包含 §1.2 责任范围 + §1.3 责任边界 |
| 2 | **主体内容** | MUST | 禁止使用 MUST/SHOULD（L3 是纯信息性文档） |
| 3 | **AI 自治权限标注** | MUST | 标注 AI 对本文档的操作权限 |
| 4 | **TTL 与生命周期** | MUST | 标注保留期限和过期处理方式 |
| 5 | **变更记录** | SHOULD | 版本历史（TTL <= 7d 的可省略） |

> **L3 与 L2 的关键差异**：
> - L3 完全禁止规范性语言（MUST/SHOULD），只能使用信息性措辞
> - L3 不需要消费者注册表、SSoT 声明、变更同步规则
> - L3 必须标注 TTL（信息性文档容易堆积，TTL 是清理机制）

#### 三层模板对照表

> v3.1.0 L1 列已适配标准子类型。MUST 仅表示 Common Core（6 章对所有子类型必含），
> ▲ 表示条件性（取决于子类型，见 §3.2.4 推导表）。
> v3.2.0：`adr` 从 L2 重分类至 L3，适用 L3 章节约束。

| 章节 | L1 治理 | L2 设计 | L3 基础 |
|------|:------:|:------:|:------:|
| 目的与范围（含责任范围+责任边界） | MUST | MUST | MUST |
| SSoT 声明 | MUST | MUST | — |
| 受控枚举定义 | ▲ 条件 | SHOULD | — |
| 消费者注册表 | ▲ 条件 | MUST | — |
| 主体内容 | MUST (MUST/SHOULD/MAY) | MUST (SHOULD/MAY) | MUST (信息性) |
| 禁止行为 | ▲ 条件 | SHOULD | — |
| 变更同步规则 | ▲ 条件 | MUST | — |
| 修改条件 | ▲ 条件 | MUST | — |
| 标准间引用规范 | MUST | SHOULD | — |
| 废弃流程 | ▲ 条件 | — | — |
| 审查周期 | SHOULD | — | — |
| 异常豁免机制 | ▲ 条件 | — | — |
| 字段不重复声明 | ▲ 条件 | — | — |
| 跨标准交叉引用 | ▲ 条件 | — | — |
| AI 可消费性声明 | MUST | — | — |
| AI 自治权限标注 | 见 frontmatter | — | MUST |
| 可验证性标注 | 见 frontmatter | — | — |
| 完整性自检清单 | ▲ 条件 | — | — |
| 变更记录 | MUST | MUST | SHOULD |
| TTL 与生命周期 | — | — | MUST |

### 3.3 各章节的详细要求

#### §1 目的与范围

必须包含：
- **目的**：一句话说明本文档解决什么问题
- **责任范围**（§1.2）：正向声明本文档管什么
- **责任边界**（§1.3）：负向声明本文档不管什么（对标 Kubernetes KEP Non-Goals）
- **范围**：适用于哪些文件/目录/场景

> **对标**：ISO/IEC Directives Part 2 要求每个标准必须有 Scope clause。Kubernetes KEP 强制要求 Goals + Non-Goals 双声明——明确"不管什么"和"管什么"同等重要，防责任边界模糊。

#### §2 SSoT 声明

必须包含一个表格：

| 内容 | 真源 | 非真源 |
|------|------|--------|
| {本文档定义的内容 1} | **本文档 §{N}** | {已被取代的旧文件} |
| {本文档定义的内容 2} | **本文档 §{N}** | — |

底部声明：**任何与本文档冲突的定义，以本文档为准。**

#### §3 受控枚举定义

如果本文档定义了受控枚举（字段值只能是固定集合），必须：
- 列出完整的枚举值清单（表格形式）
- 标注每个值的含义
- 标注代码真源（哪个 .py 文件硬编码了这些值）
- 标注新增枚举值的流程（是否需要 ADR）

如果本文档不定义任何受控枚举，写"本文档不定义受控枚举"即可。

#### §4 消费者注册表

必须按 Tier 分级列出所有依赖本文档的文件：

| Tier | 含义 | 变更时必须做什么 |
|------|------|----------------|
| **Tier 1** | 硬编码了本标准的枚举值/校验规则 | 同 commit 必须同步更新 |
| **Tier 2** | 引用本标准作为权威依据 | 改字段名时检查引用 |
| **Tier 3** | 字段定义对齐（以本标准为准） | 改语义时按需对齐 |

每个 Tier 列出具体文件和依赖内容。

> 对标：ISO 11179 §6.2 Stewardship 要求注册表维护消费者清单。

#### §5 主体内容

规则条款写作规范：
- 每条规则必须是**可执行的**（AI 可以判断是否违反）
- 每条规则必须是**明确的**（无歧义，不需要推断）
- P0 规则使用"**必须**"（MUST）、"**禁止**"（MUST NOT）
- P1 规则使用"**应该**"（SHOULD）、"**不应该**"（SHOULD NOT）
- P2 规则使用"**可以**"（MAY）

#### §6 禁止行为

以表格列出违反本规则的禁止操作。格式：

| 禁止行为 | 原因 | 替代方案 |
|---------|------|---------|
| {行为} | {为什么禁止} | {应该怎么做} |

#### §7 变更同步规则

必须包含变更类型 × 消费者 Tier 的同步要求矩阵：

| 变更类型 | Tier 1 同步要求 | Tier 2 同步要求 | Tier 3 同步要求 |
|---------|----------------|----------------|----------------|
| 新增枚举值 | 同 commit 更新硬编码 | 无需操作 | 无需操作 |
| 删除枚举值 | 同 commit 更新 + 迁移脚本 | 检查引用 | 检查引用 |
| 新增字段 | 同 commit 更新校验逻辑 | 无需操作 | 按需对齐 |
| 字段改名 | 同 commit 更新所有引用 | 同 commit 更新引用 | 同 commit 更新引用 |
| 修改必填阶段 | 同 commit 更新分阶段闸门 | 无需操作 | 无需操作 |

> 可根据本标准的具体情况调整行，但必须覆盖"新增枚举"和"字段改名"两种变更类型。

#### §8 修改条件

说明修改本文档需要满足的条件：
- 哪些变更需要 Owner 审批
- 哪些变更可以 AI 自主执行
- 破坏性变更（删除枚举值、字段改名）的审批流程

#### §9 标准间引用规范

> 对标 IETF BCP（Best Current Practice）：引用分 normative 和 informative 两类。

必须包含两个引用列表：

| 引用类型 | 含义 | 违反后果 |
|---------|------|---------|
| **Normative**（规范性引用） | 必须遵守的引用。被引用文档的规则与本标准同等约束力 | 违反 = 违反本标准 |
| **Informative**（资料性引用） | 仅供参考的引用。提供背景知识但不构成约束 | 违反 ≠ 违反本标准 |

格式：

```markdown
### 规范性引用（Normative）

| 文档 | 引用内容 | 冲突时以谁为准 |
|------|---------|--------------|
| metadata-registry.md (PS-STD-001) | frontmatter 字段定义 | PS-STD-001 |

### 资料性引用（Informative）

| 文档 | 引用内容 |
|------|---------|
| ISO/IEC 42001:2023 | AI 管理体系标准（设计参考） |
```

**根因**：项目曾出现三个 frontmatter 标准互相冲突，AI 不知道听谁的。区分 normative/informative 后，冲突时只需看 normative 引用链。

#### §10 废弃流程

> 对标 document-lifecycle-standard.md + file-operation-safety-policy.md。
> 取代 ≠ 删除。必须走完流程才能删除旧标准。

废弃流程五步：

```
Step 1: 创建新标准（新文件名，不带版本号后缀）
  → 新文件 frontmatter 添加 supersedes: <旧文件路径>

Step 2: 通知消费者
  → 旧文件消费者注册表中列出的所有 Tier 1 文件，必须确认已迁移

Step 3: 过渡期（至少 7 天）
  → 旧文件 status 改为 Superseded
  → 旧文件 frontmatter 添加 superseded_by: <新文件路径>
  → 过渡期内新旧标准共存，以新标准为准

Step 4: 确认无引用
  → 运行断链检测：rg "旧文件名" docs/ --include="*.md" -l
  → 所有引用已更新为新文件路径

Step 5: 删除或归档
  → 旧文件 status 改为 Deprecated
  → 按 TTL 规则处理（见 document-lifecycle-standard.md）
```

**禁止**：跳过 Step 2-4 直接删除 Active 标准。

#### §11 审查周期

> 对标 ISO 11179 §6.4 Registration Status + ISO/IEC 42001 持续监控要求。

| 审查类型 | 周期 | 触发条件 | 审查内容 |
|---------|------|---------|---------|
| **定期审查** | 每 90 天 | 到期自动触发 | 标准是否仍然适用？枚举值是否需要扩展？消费者是否有新增？ |
| **事件驱动审查** | 不定期 | 枚举值变更 / 字段改名 / 消费者报告问题 | 受影响章节是否需要更新？ |
| **Phase 转换审查** | 不定期 | 项目 Phase 变更 | 标准是否适配新 Phase 的要求？ |

每次审查结果记录在变更记录中。审查后无变更的，记录"审查通过，无变更"。

#### §12 异常豁免机制

> 对标 ISO 42001 §8.2 处理不符合项 + SR 11-7 模型验证例外。

| 豁免级别 | 定义 | 审批要求 | 记录要求 |
|---------|------|---------|---------|
| **临时豁免** | 单次 session 内违反标准 | Session Log 中记录原因 | Session Log |
| **短期豁免** | 7 天内违反标准 | Owner 口头批准 + Session Log 记录 | Session Log + 变更记录 |
| **长期豁免** | 超过 7 天的违反 | Owner 书面批准 + ADR 记录 | ADR + 变更记录 |

豁免必须包含：
- **豁免的规则**：哪条规则被豁免
- **豁免原因**：为什么必须违反
- **替代措施**：违反后用什么方式保证安全
- **到期时间**：什么时候恢复遵守

**禁止**：永久豁免（应修改标准而非永久豁免）。

#### §13 与 PS-STD-001 的字段不重复声明

> v3.1.0 改为**条件性**——仅在标准定义了 PS-STD-001 未覆盖的字段时必含。
> 根因：field-naming-standard.md 和 metadata-registry.md 都定义了 layer 格式，导致漂移。
> 绝大多数 L1 标准不定义新字段 → 不需要此章节。

**触发条件**：本标准定义了自己的字段（frontmatter 或 body 中）且该字段不在 PS-STD-001 的字段清单中。

**不适用时**：标准不定义字段或所有字段已在 PS-STD-001 中定义 → 不写本章节。

**适用时**必须声明：

```markdown
### 字段定义归属声明

本标准定义以下字段（以本标准为准）：
- {字段 1}：{定义位置}
- {字段 2}：{定义位置}

本标准引用以下字段（以 PS-STD-001 为准，本标准不重复定义）：
- frontmatter 所有字段：见 metadata-registry.md §2
- doc_type 受控词表：见 metadata-registry.md §3
- status 受控词表：见 metadata-registry.md §4
```

**禁止**：在标准文档中重复定义 PS-STD-001 已定义的字段。发现重复定义时，以 PS-STD-001 为准，本标准改为引用。

#### §14 跨标准字段交叉引用

> 根因：改了 `primary_model` 但不知道还有哪些标准也用了这个字段。

如果本标准定义的字段被其他标准引用，必须列出交叉引用表：

```markdown
### 字段交叉引用

| 本标准字段 | 引用此字段的其他标准 | 引用方式 |
|-----------|-------------------|---------|
| execution_model | task-card-standard.md | 域 B 任务卡字段 |
| safety_level | ai-autonomy-authority-registry.md | 权限层级判定 |
```

字段改名时，必须同步更新所有交叉引用方（见 §7 变更同步规则）。

#### §15 AI 可消费性声明

> 氛围编程语境下的必要章节。对标 Anthropic CLAUDE.md 最佳实践 + ISO/IEC 42001 可追溯性要求。
> 根因：AI 是本标准的主要消费者。如果 AI 无法无歧义理解并执行，标准等于不存在。

必须声明以下三项：

**15.1 AI 可理解性**

| 维度 | 要求 | 自检方法 |
|------|------|---------|
| 语义无歧义 | 每条规则只有一种解读 | 让 2 个不同 AI 模型独立解读，结果一致 |
| 上下文自足 | 不需要外部文档即可执行本标准 | AI 仅读取本标准即可正确执行 |
| 示例充分 | 每条 MUST/SHOULD 规则至少有 1 个正例和 1 个反例 | 人工检查 |

**15.2 AI 上下文预算**

| 维度 | 要求 |
|------|------|
| 标准全文 Token 估算 | 标注本标准的预估 Token 数（供 CR-001 预算分配参考） |
| 最小必读章节 | 标注 AI 执行任务时必须加载的最小章节集合 |
| 按需加载章节 | 标注可以按需加载的章节（非必须） |

**15.3 AI 工具兼容性**

| 工具 | 兼容性 | 说明 |
|------|:------:|------|
| Cursor (Premium) | ✅/❌ | 是否可直接消费本标准 |
| Trae (Free) | ✅/❌ | 是否可直接消费本标准 |
| Claude Code | ✅/❌ | 是否可直接消费本标准 |
| Kimi | ✅/❌ | 是否可直接消费本标准 |

#### §16 AI 自治权限标注

> v3.1.0 **不再作为独立 MUST 章节**。AI 自治权限已在 frontmatter 的 `ai_autonomy` 字段中声明。
> 禁止在 body 中用 prose 重复 frontmatter 已声明的信息（详见 §3.2.3）。
> 
> `ai_autonomy` 合法值（定义在 PS-STD-001 §10.3）：
> 
> | 值 | 含义 | AI 行为 |
> |---|------|--------|
> | `immutable_core` | 不可变核心，AI 禁止修改 | 违反时停止操作，上报 Owner |
> | `human_gated` | 人工门控，AI 需 Owner 批准才能执行 | 请求 Owner 审批后执行 |
> | `ai_editable` | AI 可自主执行 | 自主执行，记录在 Session Log |
> 
> 本标准中每条规则的自治权限分配，在 §15（AI 可消费性声明）中总览说明。

#### §17 可验证性标注

> v3.1.0 **不再作为独立 MUST 章节**。可验证性已在 frontmatter 的 `verifiability` 字段中声明。
> 禁止在 body 中用 prose 重复 frontmatter 已声明的信息（详见 §3.2.3）。
> 
> `verifiability` 合法值（定义在 PS-STD-001 §10.5）：
> 
> | 值 | 含义 | 验证方式 |
> |---|------|---------|
> | `automated` | 可自动验证 | pre-commit hook / pytest / mypy / ruff |
> | `manual` | 需人工验证 | Code Review / Session Log 审计 |
> | `subjective` | 需主观判断 | Owner 裁决 |
> 
> 本标准中每条规则的可验证性分配，在 §15（AI 可消费性声明）中总览说明。

#### §18 完整性自检清单

> v3.1.0 改为**条件性**——人类创建标准时必含，AI 生成标准时为 SHOULD（可选）。
> 原因：AI 自查是自指涉空洞（AI 检查 AI 是否写对，没有独立验证力）。
> 人类创建者逐项勾选仍有实际价值——防止遗漏章节。

**触发条件**：标准由人类创建或人类主导修订。

**不适用时**：全 AI 生成标准 → 可省略或简化为一行声明"本标准由 AI 生成，自检清单不适用"。

**适用时**，创建或更新标准文档，必须逐项确认（按本标准子类型过滤不适用章节）：

```markdown
### 完整性自检清单

- [ ] §1 目的与范围：包含目的、责任范围（管什么）、责任边界（不管什么）
- [ ] §2 SSoT 声明：包含真源/非真源表格 + 冲突仲裁声明
- [ ] §3 受控枚举：如有枚举，列出完整清单 + 代码真源 + 新增流程
- [ ] §4 消费者注册表：Tier 1/2/3 分级列出 + 依赖内容（宪法原则型跳过）
- [ ] §5 主体内容：MUST/SHOULD/MAY 措辞 + 可执行
- [ ] §6 禁止行为：行为 + 原因 + 替代方案（数据注册表型跳过）
- [ ] §7 变更同步规则：变更类型 × Tier 矩阵（frozen 标准跳过）
- [ ] §8 修改条件：审批流程 + AI 自治边界（frozen 标准跳过）
- [ ] §9 标准间引用：normative vs informative 分离
- [ ] §10 废弃流程：五步流程 + 过渡期（frozen 标准跳过）
- [ ] §11 审查周期：定期/事件驱动/Phase 转换
- [ ] §12 异常豁免：三级豁免 + 记录要求（纯 ABS 标准跳过）
- [ ] §13 字段不重复声明：归属声明（不定义新字段的标准跳过）
- [ ] §14 跨标准交叉引用：字段 × 引用标准表（无交叉引用跳过）
- [ ] §15 AI 可消费性：可理解性 + 上下文预算 + 工具兼容性
- [ ] §19 变更记录：版本历史表
- [ ] frontmatter 完整：所有 PS-STD-001 定义的必填字段
```

人类创建标准文档时，必须先输出此清单并逐项确认，再输出标准正文。

---

## 4. YAML 规则文档格式

### 4.1 必填顶层字段

```yaml
schema_version: "1.0.0"
doc_type: register | contract | config
title: "文档标题"
status: active | draft | deprecated
ttl: permanent | 30d | 7d | session
```

### 4.2 字段命名规范

- 使用 `snake_case`（下划线分隔）
- 布尔值使用 `true`/`false`（小写）
- 日期使用 `"YYYY-MM-DD"` 格式（带引号的字符串）
- 枚举值使用小写字母和下划线

---

## 5. 文件命名规范

遵循 [file-naming-standard.md](01_policies_and_standards/governance/document/file-naming-standard.md) v2.0.1。

> 核心约束：全小写 kebab-case，禁止大写字母、版本号后缀、日期后缀。

---

## 6. 版本控制规范

- 版本历史通过 `git log` 查询，不在文件名中体现
- 重大修订（破坏性变更）：主版本号 +1（1.0.0 → 2.0.0）
- 功能新增：次版本号 +1（1.0.0 → 1.1.0）
- 错误修复：补丁版本号 +1（1.0.0 → 1.0.1）
- 每次修改必须更新 frontmatter 中的 `version` 和 `date` 字段

---

## 7. 本文档的 SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 标准文档的三层模板体系（L1/L2/L3） | **本文档 §3.1** | rule-document-format-standard.md v1.0.0（已取代） |
| L1 标准子类型与章节适用性规则 | **本文档 §3.2** | — |
| Frontmatter 必填字段 | **metadata-registry.md §2** | 本文档 §2 仅引用，不重复定义 |
| 文件命名规范 | **file-naming-standard.md v2.0.1** | 本文档 §5 仅引用，不重复定义 |
| 消费者注册表格式 | **本文档 §3.3 §4** | — |
| 变更同步规则格式 | **本文档 §3.3 §7** | — |
| AI 自治权限层级 | **frontmatter `ai_autonomy` 字段** | 本文档 §3.3 §16 仅说明 frontmatter 字段合法值 |
| 可验证性标注体系 | **frontmatter `verifiability` 字段** | 本文档 §3.3 §17 仅说明 frontmatter 字段合法值 |

**任何与本文档冲突的定义，以本文档为准。** 但 frontmatter 字段定义以 PS-STD-001 为准。

---

## 8. 本文档的标准间引用规范

### 规范性引用（Normative）

| 文档 | 引用内容 | 冲突时以谁为准 |
|------|---------|--------------|
| metadata-registry.md (PS-STD-001) | frontmatter 字段定义、受控枚举 | PS-STD-001 |
| file-naming-standard.md | 文件命名规则 | file-naming-standard.md |
| document-lifecycle-standard.md | 文档生命周期管理 | document-lifecycle-standard.md |
| rule-lifecycle-and-change-standard.md (PS-STD-009) | 变更审批流程 | rule-lifecycle-and-change-standard.md |
| ai-autonomy-authority-registry.md | AI 自治权限三层模型 | ai-autonomy-authority-registry.md |
| vibe-coding-gate-checklist.md | 可验证性 A/M/S 标注体系 | vibe-coding-gate-checklist.md |

### 资料性引用（Informative）

| 文档 | 引用内容 |
|------|---------|
| ISO/IEC 42001:2023 | AI 管理体系标准（设计参考） |
| ISO 11179 §6.2 | 元数据注册表 Stewardship（消费者注册表设计参考） |
| IETF BCP 14 | MUST/SHOULD/MAY 语义定义 |
| Anthropic CLAUDE.md 最佳实践 | AI 可消费文档设计参考 |
| Google A2A Agent Card | AI Agent 元数据标准参考 |

---

## 9. 本文档的废弃流程

遵循 document-lifecycle-standard.md 的标准流程。本文档取代了 rule-document-format-standard.md v1.0.0，过渡期已于 v2.0.0 发布时完成。

---

## 10. 本文档的审查周期

| 审查类型 | 周期 | 上次审查 |
|---------|------|---------|
| 定期审查 | 每 90 天 | 2026-04-29（v3.0.0 创建时） |
| 事件驱动审查 | 不定期 | — |

---

## 11. 本文档的异常豁免机制

遵循 §3.3 §12 定义的三级豁免机制。本文档自身的豁免记录在变更记录中。

---

## 12. 本文档与 PS-STD-001 的字段不重复声明

### 字段定义归属声明

本标准定义以下字段（以本标准为准）：
- 标准文档必须包含的 19 个章节：见 §3.1
- 标准间引用分类（normative/informative）：见 §3.3 §9

本标准引用以下字段（以 PS-STD-001 为准，本标准不重复定义）：
- frontmatter 所有字段：见 metadata-registry.md §2
- doc_type 受控词表：见 metadata-registry.md §3
- status 受控词表：见 metadata-registry.md §4
- category 枚举：见 metadata-registry.md §9.1
- domain 枚举：见 metadata-registry.md §9.2

---

## 13. 本文档的跨标准字段交叉引用

| 本标准字段/概念 | 引用此字段的其他标准 | 引用方式 |
|---------------|-------------------|---------|
| AI 自治权限三层模型 | ai-autonomy-authority-registry.md | 权限层级定义 |
| 可验证性 A/M/S 标注 | vibe-coding-gate-checklist.md | 标注体系定义 |
| 变更审批四级流程 | rule-lifecycle-and-change-standard.md (PS-STD-009) | 审批流程定义 |
| 文档生命周期状态机 | document-lifecycle-standard.md | 状态转换规则 |
| frontmatter 字段 | metadata-registry.md (PS-STD-001) | 字段定义 |

---

## 14. 本文档的 AI 可消费性声明

| 维度 | 状态 | 说明 |
|------|:----:|------|
| 语义无歧义 | ✅ | MUST/SHOULD/MAY 精确定义 |
| 上下文自足 | ⚠️ | 需配合 PS-STD-001 理解 frontmatter 字段 |
| 示例充分 | ✅ | 每个新章节都有格式示例 |
| Token 估算 | ~4000 tokens | 最小必读：§3.1 + §3.2 + §18

---

## 15. 本文档的 AI 自治权限标注

| 规则 | 权限 | 可验证性 |
|------|------|---------|
| 标准文档必须包含 §3.1 列出的所有 MUST 章节 | immutable_core | [A] |
| 标准文档应该包含 §3.1 列出的所有 SHOULD 章节 | human_gated | [M] |
| 每条规则必须标注 AI 自治权限 | immutable_core | [A] |
| 每条规则必须标注可验证性 A/M/S | immutable_core | [A] |
| frontmatter 字段不重复定义 | immutable_core | [A] |
| 废弃流程必须走完五步 | immutable_core | [M] |
| 审查周期 90 天 | human_gated | [M] |
| 异常豁免必须记录 | immutable_core | [A] |
| AI 创建标准前必须先输出自检清单 | immutable_core | [M] |
| 标准间引用必须分 normative/informative | human_gated | [M] |

统计：immutable_core 7 条 / human_gated 3 条 / ai_modifiable 0 条。安全占比 100%（>= 30% 达标）。

---

## 16. 本文档的消费者注册表

### Tier 1：硬编码了本模板定义的章节结构

| 文件 | 依赖内容 | 同步要求 |
|------|---------|---------|
| `scripts/governance/check_frontmatter_metadata.py` | frontmatter 必填字段校验（以 metadata-registry.md 为准，间接依赖本模板的章节定义） | 间接依赖 |

### Tier 2：引用本模板作为权威依据

| 文件 | 引用方式 |
|------|---------|
| 所有 `doc_type: policy` 和 `doc_type: standard` 文档 | 按 §3 章节清单编写 |
| `docs/01_policies_and_standards/templates/blueprint-template.md` | 参考本模板的治理章节设计 |
| `docs/01_policies_and_standards/templates/blueprint-template.md` | 参考本模板的治理章节设计 |

### Tier 3：字段定义对齐

| 文件 | 对齐内容 |
|------|---------|
| `metadata-registry.md`（PS-STD-001） | frontmatter 字段定义（本模板 §2 引用 PS-STD-001，不重复定义） |

---

## 17. 本文档的变更同步规则

| 变更类型 | Tier 1 同步要求 | Tier 2 同步要求 | Tier 3 同步要求 |
|---------|----------------|----------------|----------------|
| 新增必须章节 | 更新 GATE-15 校验逻辑 | 所有 policy/standard 文档补上新章节 | 无需操作 |
| 修改章节格式 | 无需操作 | 按需更新 | 无需操作 |
| 新增 frontmatter 字段 | 同 commit 更新校验脚本 | 所有 policy/standard 文档补上新字段 | 同 commit 更新 PS-STD-001 |

---

## 18. 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| 新增必须章节 | Owner 审批（影响所有标准文档） |
| 修改章节格式 | AI 可自主执行（不影响现有文档合规性） |
| 新增 frontmatter 字段 | Owner 审批（影响所有文档的 frontmatter） |
| 修改 Tier 分级规则 | Owner 审批（影响变更同步流程） |

---

## 19. 禁止行为

| 禁止行为 | 原因 | 替代方案 |
|---------|------|---------|
| 创建不含消费者注册表的标准文档 | 改了不知道影响谁 | 按本模板 §3.2.2 §4 编写 |
| 创建不含 SSoT 声明的标准文档 | 冲突时无法仲裁 | 按本模板 §3.3 §2 编写 |
| 创建不含变更同步规则的标准文档 | 变更后消费者不同步 | 按本模板 §3.3 §7 编写 |
| 创建不含 AI 自治权限标注的标准文档 | AI 不知道哪些可以自主执行 | 在 frontmatter 中设置 `ai_autonomy` 字段 |
| 创建不含可验证性标注的标准文档 | 规则无法验证 = 形同虚设 | 在 frontmatter 中设置 `verifiability` 字段 |
| 在标准文档中重复定义 metadata-registry.md 已定义的字段 | 两个定义会漂移 | 引用 PS-STD-001 |
| 标准文档使用模糊词汇（尽量/建议/最好） | AI 无法判断是否违规 | 使用 MUST/SHOULD/MAY |
| 创建不含 normative/informative 引用分类的标准文档 | 冲突时不知道听谁的 | 按本模板 §3.3 §9 分类 |
| 跳过废弃流程直接删除 Active 标准 | 消费者不知道标准已废弃 | 按本模板 §3.3 §10 走完五步 |
| 永久豁免某条规则 | 应修改标准而非永久豁免 | 修改标准或设定期限 |
| 创建不含责任范围+责任边界声明的标准文档 | 责任边界模糊导致范围漂移 | 按本模板 §3.3 §1 编写 |

---

## 20. 违规检测

以下情况视为格式违规，pre-commit hook 应报告：

- policy/standard 文档缺少 §3 规定的必须章节
- frontmatter 缺少 §2 规定的必填字段
- 文件名包含大写字母
- 文件名包含版本号后缀
- 文件编码非 UTF-8
- 标准文档缺少 AI 自治权限标注
- 标准文档缺少可验证性标注
- 标准文档重复定义 PS-STD-001 已定义的字段
- 标准文档缺少 §1.2 责任范围 + §1.3 责任边界声明

---

## 21. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 3.1.0 | 2026-05-01 | **L1 模板架构升级**——引入标准子类型体系。Owner 直接指令覆盖 frozen + immutable_core 约束。(1) 新增 §3.2：定义 Common Core（6 章对所有 L1 标准必含）+ 条件性章节（12 章按触发条件必含）+ 4 种子类型（行为规则/数据注册/宪法原则/格式定义）。（2）§16（AI 自治权限标注）和 §17（可验证性标注）不再作为独立 MUST 章节——改由 frontmatter `ai_autonomy` / `verifiability` 字段声明，禁止 body 重复。（3）§13（字段不重复声明）改为条件性——仅定义新字段的标准需要。（4）§18（完整性自检清单）改为条件性——人类创建标准时必含，AI 生成标准为 SHOULD。对标 ISO/IEC Directives Part 2（IS/TS/TR 分层）、Kubernetes CRD required/optional 字段。版本号 minor +1。 |
| 3.0.2 | 2026-05-01 | 编辑性变更——frontmatter 字段排序对齐 PS-STD-001 §2.3（ai_autonomy 移至 verifiability 之后，supersedes 移至 verifiability 之后）。版本号 patch +1。 |
| 3.0.1 | 2026-05-01 | 编辑性压缩与跨文件对齐。(1) §5 文件命名从 6 行表压缩为引用链接（真源在 file-naming-standard.md）。(2) §14 AI 可消费性：合并 3 个子节为 1 表，删除无信息量的"工具兼容性"表。(3) 版本号 patch +1（编辑性变更）。 |
| 3.0.0 | 2026-04-29 | 引入三层模板体系（L1 治理模板 19 章 / L2 设计模板 10 章 / L3 基础模板 5 章），按 doc_type 分层适用，规范性语言分层（L1 MUST/SHOULD/MAY、L2 SHOULD/MAY、L3 禁止规范性语言）。新增 10 个必须/应该章节：§9 标准间引用规范（normative/informative）、§10 废弃流程（五步）、§11 审查周期（90天）、§12 异常豁免机制（三级）、§13 与 PS-STD-001 字段不重复声明、§14 跨标准字段交叉引用、§15 AI 可消费性声明（可理解性+上下文预算+工具兼容性）、§16 AI 自治权限标注（immutable_core/human_gated/ai_editable）、§17 可验证性标注（A/M/S）、§18 完整性自检清单。本文档自身作为示范，完整实现了所有 19 个章节。禁止行为从 5 条扩展到 10 条。违规检测新增 3 项 |
| 2.0.0 | 2026-04-29 | 升级为标准文档模板（元标准）。新增：SSoT 声明（§7）、消费者注册表（§8）、变更同步规则（§9）、修改条件（§10）、禁止行为（§11）。frontmatter 字段定义改为引用 metadata-registry.md，不再重复定义。取代 rule-document-format-standard.md v1.0.0 |
| 1.0.0 | 2026-04-22 | 初始版本：格式层面规范（frontmatter、章节、命名、版本控制） |
