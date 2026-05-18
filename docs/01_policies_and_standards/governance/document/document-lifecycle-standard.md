---
module_id: GOV-DOC-006
title: 文档生命周期管理规范
doc_type: standard
status: active
version: 1.2.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-01"
ttl: permanent
summary: "定义 ZephyrAlpha 2.0 中所有文档的生命周期管理规则，包括 TTL 分级、归档流程、废弃流程和状态快照管理。"
tags: [document-lifecycle, ttl, governance]
rule_form: declarative
scope: global
stability: stable
verifiability: manual
ai_autonomy: human_gated
---

# 文档生命周期管理规范

> **目的**：定义 ZephyrAlpha 2.0 中所有文档的生命周期管理规则，包括 TTL 分级、归档流程、废弃流程和状态快照管理，防止文档堆积和版本混乱。
>
> **铁律**：MUST 为所有文档指定 TTL 和 status——无生命周期管理 = 过期文档堆积 + AI 无法判断有效性。

## 〇、目的与范围

### 〇.1 目的

为 ZephyrAlpha 2.0 项目中所有文档定义完整的生命周期管理——从 TTL 分级到状态机到归档废弃。确保任何 AI 或人类看到一份文档时，能明确知道它处于什么状态（draft/active/deprecated）、什么时候该过期、过期后怎么处理。

### 〇.2 本标准管理以下内容

| # | 内容 | 说明 |
|---|------|------|
| 1 | TTL 分级定义 | permanent / 30d / 7d / session 四种级别 |
| 2 | 文档状态机 | draft → active → deprecated 及转换规则 |
| 3 | 状态快照管理 | LATEST 覆盖写入模式，禁止按日期新建快照 |
| 4 | 归档流程 | 审计报告 / 架构文档的归档路径与步骤 |
| 5 | 废弃流程 | 被取代时的 supersedes/superseded_by 操作步骤 |
| 6 | AI 生成产物特殊规则 | 写位置（.audit_cache/）+ frontmatter 要求 |

### 〇.3 本标准**不**覆盖以下内容

| # | 排除项 | 以哪个文件为准 |
|---|--------|-------------|
| 1 | 文件的命名规范 | file-naming-standard.md（GOV-DOC-003） |
| 2 | 文件的存放路径 | file-path-standard.md（GOV-DOC-004） |
| 3 | 文件的删除/移动安全门禁 | file-operation-safety-policy.md（GOV-DOC-007） |
| 4 | 详细的状态值枚举（全表） | meta/metadata-registry.md（PS-STD-001）§4.1 |
| 5 | 规则退役的整体审批流程（废弃级联） | meta/rule-lifecycle-and-change-standard.md（PS-STD-009）§5 |

### 〇.4 专业对标

| 来源 | 对标内容 |
|------|---------|
| ITIL Service Lifecycle | 每个服务（文档类似服务资产）有明确的创建→运营→退役阶段。本文的状态机即服务生命周期模型 |
| ISO 9001 §7.5.3.2 | 文件化信息必须有"review and approval"（审查+批准→对应状态转换）+ "retention and disposition"（保留+处置→对应 TTL 和归档） |
| K8s Deprecation Policy | "API 在移除前必须先标记为 deprecated，给予迁移窗口"——本文的 `superseded_by` 指引 + deprecated 归档流程基于此 |
| ARMA GARP（档案管理原则）| "文档归档后保留最少 12 个月才能永久删除"——GOV-DOC-002 §7.3 引用，本文 §四 归档流程对应 |

## 一、TTL 分级定义

| TTL 值 | 含义 | 适用场景 | 过期处理 |
|--------|------|---------|---------|
| `permanent` | 永久有效 | 治理规范、架构视图、ADR、知识库条目 | 不过期，需要 Owner 明确废弃 |
| `30d` | 30 天后过期 | 审计报告、状态快照、迁移报告 | 过期后移入 `09_audit/archive/` 或直接删除 |
| `7d` | 7 天后过期 | 临时工作文件、草稿、中间产物 | 过期后直接删除 |
| `session` | 本 session 结束后删除 | 临时脚本、一次性工具、session 内草稿 | session 结束时必须删除，不得提交到 git |

## 二、文档状态机

> **对齐声明**：本状态机对齐 PS-STD-001（`meta/metadata-registry.md`）§4.1——DocStatus 只有 3 种：
> `draft` / `active` / `deprecated`。"被取代"由 `superseded_by` 字段承载，不是独立的 status 值。

```
draft（草稿）
  ↓ Owner 批准
active（有效）
  ↓ 被取代 或 过时
deprecated（已废弃）
  ↓ 确认无引用 + Owner 批准
[删除 或 归档]
```

### 状态转换规则

| 转换 | 触发条件 | 操作要求 |
|------|---------|---------|
| draft → active | Owner 批准 | 更新 frontmatter `status` 为 `active`；补齐 Active 阶段 14 个必填字段（PS-STD-001 §2.2）；更新 document-metadata-index.yaml |
| active → deprecated | 被新版本取代 或 内容过时 | 填写 `superseded_by` 字段（被取代时填新路径，过时时填 `"N/A"`）；若被取代，同时在新文件中添加 `supersedes`；更新 document-metadata-index.yaml |
| deprecated → active | Owner 审批（重新启用） | 更新 frontmatter `status` 为 `active`；清除 `superseded_by` 字段 |
| deprecated → 删除 | TTL 过期 + 确认无引用 + Owner 明确指示 | 执行文件删除安全门禁（见 file-operation-safety-policy.md） |

## 三、状态快照管理（LATEST 覆盖写入模式）

> **铁律**：MUST 使用 LATEST 命名覆盖写入——按日期新建快照 = 历史堆积 + AI 无法识别最新。

### 强制规则

- **状态快照文件必须使用 LATEST 命名**：`*-LATEST.json`、`*-LATEST.yaml`、`*-LATEST.md`
- **禁止按日期新建状态快照文件**：`scan-20260413.json` ❌
- **历史版本通过 `git log` 查询**，不在目录中保留多个版本
- **覆盖写入**：每次更新状态快照时，直接覆盖 LATEST 文件

### 适用场景

| 文件类型 | 正确命名 | 错误命名 |
|---------|---------|---------|
| Sentinel 扫描结果 | `SENTINEL_L1_SCAN_LATEST.json` | `SENTINEL_L1_SCAN_20260413.json` ❌ |
| 架构快照 | `architecture-snapshot-LATEST.yaml` | `architecture-snapshot-20260413.yaml` ❌ |
| 断链报告 | `dead-link-report-LATEST.md` | `dead-link-report-20260413.md` ❌ |

**例外**：以下文件允许带日期（因为每次都是独立的记录，不是覆盖）：
- Session Log：`session-YYYYMMDD-NNN.md`（每次 session 是独立的）
- 审计报告归档：`09_audit/archive/` 下的历史报告

## 四、归档流程

当文档需要归档（保留历史但不再活跃使用）时：

```
1. 将文件移动到对应的 archive/ 子目录
   - 审计报告 → 09_audit/archive/
   - 架构文档 → 02_enterprise_architecture/archive/
2. 更新文件 frontmatter：status: deprecated，ttl: 30d
3. 更新所有引用该文件的链接（或移除引用）
4. 重新生成 document-metadata-index.yaml
5. 在同一 commit 中完成以上所有操作
```

## 五、废弃流程

> 通用退役原则参见 PS-STD-009（`meta/rule-lifecycle-and-change-standard.md`）§5（退役流程 + 废弃级联）。以下为文档特有的废弃步骤。

当文档被新版本取代时：

```
1. 创建新版本文件（新文件名，不带版本号后缀）
2. 在新文件 frontmatter 中添加：supersedes: <旧文件路径>
3. 在旧文件 frontmatter 中添加：superseded_by: <新文件路径>，status: deprecated
4. 确认无其他文件引用旧文件（运行断链检测）
5. 按 TTL 规则处理旧文件（permanent 文件需 Owner 明确指示才删除）
```

## 六、AI 生成产物的特殊规则

> **铁律**：MUST 将 AI 生成产物写入 `.audit_cache/`——直接写入 `docs/` = 污染版本历史。

| 规则 | 内容 |
|------|------|
| AI 生成产物写入位置 | **必须写入 `.audit_cache/`**（已 gitignored），禁止写入受版本控制目录 |
| AI 生成文件 frontmatter | 必须包含 `created_by: agent` 和 `ttl: 7d` 或 `ttl: 30d` |
| AI 生成产物提升为正式文档 | 需要 Owner 审查后手动移入正式目录，并更新 frontmatter |

## 七、禁止操作

| 禁止操作 | 原因 |
|---------|------|
| 按日期新建状态快照文件 | 使用 LATEST 覆盖写入模式 |
| 文件名带版本号后缀（-v2/-v3） | 版本历史通过 git log 查询 |
| AI 生成产物直接写入 `docs/` | 必须先写入 `.audit_cache/` |
| 不更新 document-metadata-index.yaml 就删除文件 | 注册表必须与实际文件同步 |
| 跳过废弃流程直接删除 Active 文档 | 必须先走废弃流程 |

## 八、与其他规则的关系

| 规则 | 与本标准的关系 |
|------|-------------|
| meta/metadata-registry.md（PS-STD-001）§4.1 | 状态值的权威定义——本标准 §二 的状态机必须对齐 PS-STD-001 的 DocStatus 枚举 |
| meta/rule-lifecycle-and-change-standard.md（PS-STD-009）§5 | 通用规则退役流程——本标准 §五 的废弃流程为文档特化版本 |
| directory-structure-standard.md（GOV-DOC-002） | 归档流程的物理路径由 GOV-DOC-002 定义（如 09_audit/archive/） |
| file-naming-standard.md（GOV-DOC-003） | 文档命名规范确保状态快照的 LATEST 后缀和 session log 的日期格式合法 |
| file-operation-safety-policy.md（GOV-DOC-007） | 废弃→删除的最后一步触发安全门禁——必须先通过三问才能删 |
| document-control-policy.md（GOV-DOC-009） | 本标准的"状态机=事实唯一"原则 → DOC-001（SSoT 唯一） |

## 九、变更记录

| 日期 | 版本 | 修改内容 |
|------|------|---------|
| 2026-04-22 | 1.0.0 | 初始创建。定义 TTL 四级分级、状态机、LATEST 模式、归档废弃流程、AI 产物规则。 |
| 2026-05-01 | 1.1.0 | 结构对齐 + 状态机修正。（1）新增 §〇 目的与范围（§〇.2 管理内容 + §〇.3 不覆盖内容 + §〇.4 专业对标）；（2）新增 §八 与其他规则的关系 + §九 变更记录；（3）状态机对齐 PS-STD-001 §4.1：移除非法状态 "Superseded"，现在只有 draft/active/deprecated 三种；（4）废弃流程从 6 步简化至 5 步；（5）字段修正：`type: generated` → `created_by: agent`。对齐 templates/policy-template.md 强制结构。 |
