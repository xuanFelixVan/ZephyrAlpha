---
module_id: META-GLS-001
title: ZephyrAlpha 规则体系术语表
doc_type: terminology
status: active
version: "1.3.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-01"
ttl: permanent
summary: "ZephyrAlpha 规则体系核心术语的统一定义——这是全项目术语的仲裁源。当同一个术语在多个文件中被定义得不一致时，以本表为准。对标 ISO 11179 §6.2（术语注册表）和 ISO/IEC Directives Part 2 §5（术语定义要求）。"
tags: [glossary, terminology, ssot, meta-reference, iso-11179]
rule_form: data
scope: global
stability: stable
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "§3.2 + §5", why: "术语定义引用了 doc_type 受控词表和 module_id 格式规范"}
---

# ZephyrAlpha 规则体系术语表

> **module_id**: META-GLS-001 | **version**: 1.3.0 | **status**: active

**唯一真源声明**：当同一个术语在多个文件中被定义得不一致时，以本表为准。

> **对标**：ISO 11179 §6.2 Metamodel Registries → Terminology Registry / ISO/IEC Directives Part 2 §5 → Terms and Definitions

---

## 核心术语（24 个）

| # | 术语 | 英文 | 定义 |
|:--:|------|------|------|
| 1 | **SSoT** | Single Source of Truth | 唯一真源——一个概念只在一个文件中定义，其他文件仅引用。违反 SSoT 的典型症状：两个文件对同一概念的定义不一致 |
| 2 | **Vibe Coding** | Vibe Coding | AI 辅助编程范式——通过自然语言与 AI 交互完成施工，AI 每次 session 从零开始读取项目文件，无跨 session 记忆 |
| 3 | **零记忆重启** | Zero-Memory Restart | Vibe Coding AI 的核心约束：每次新 session 对所有历史操作毫无记忆，项目文件必须做到"读完即理解全貌" |
| 4 | **Context Tax** | Context Tax | 上下文税——AI 每次 session 读取所有规则文件的开销，文件越多留给实际任务的容量越少。meta/ 层文件数上限 = 15 |
| 5 | **原子事务** | Atomic Transaction | 所有文件修改一步完成、直接到位。改一个文件时，相关联动修改必须在同一批操作中完成 |
| 6 | **埋雷（技术债务）** | Technical Debt / Landmine | 当前选择导致未来必须重写架构（而非简单扩展）。判定标准：不可逆的数据迁移、没有拆除路径的临时方案 |
| 7 | **受控词表** | Controlled Vocabulary | 某字段的合法值集合，不允许自由扩展。如 `doc_type` 全项目 27 个合法值，PS 子集 13 个 |
| 8 | **规则画像** | Rule Portrait | 一条规则在 PS-STD-004 五个维度上的取值组合，如 `{domain: meta, layer: cross_layer, scope: global, stability: frozen, executor: immutable_core}` |
| 9 | **推导链** | Derivation Chain | 规则冲突时按 stability → layer → scope → Owner 的链式裁决顺序（PS-STD-004 §9） |
| 10 | **三域架构** | Three-Domain Architecture | PS-STD-001 定义的字段管辖三域：域 A（文档 frontmatter）/ 域 B（任务卡）/ 域 C（AI 治理 + Session Log） |
| 11 | **分阶段闸门** | Staged Gate | PS-STD-001 §2.2：Draft 只需 7 个必填字段，Active 需 18 个（7 draft + 11 active），Deprecated 需 18+superseded_by |
| 12 | **session** | AI Session | 一次 AI 工具的完整对话周期。AI 在此周期内可保持上下文，周期结束后所有状态丢失 |
| 13 | **doc_type** | Document Type | PS-STD-001 §3.2 定义的 27 种文档类型受控词表。决定文档的章节数（19/10/5）、规范性语言强度 |
| 14 | **layer** | Layer | 规则层级：cross_layer（跨层）> L1（治理层）> L2（设计层）> L3（基础层）。决定规范性语言和推导优先级 |
| 15 | **stability** | Stability | 规则稳定性：frozen（冻结，年级别）> stable（稳定，季度级别）> evolving（演进中，月级别）。推导链第一优先维度 |
| 16 | **ai_autonomy** | AI Autonomy | AI 操作权限：immutable_core（禁止修改）> human_gated（需 Owner 批准）> ai_modifiable（可自主修改但需记录） |
| 17 | **frontmatter** | Frontmatter | 文档头部的 YAML 元数据块，以 `---` 分隔。所有规则文件的必填区域，包含 module_id/status/version 等字段 |
| 18 | **module_id** | Module Identifier | 规则文件的全局唯一标识符，格式 `DOMAIN-TYPE-NNN`（如 PS-STD-004）。定义于 PS-STD-001 §5 |
| 19 | **depends_on** | Depends On | frontmatter 字段——声明本文件引用的上游文件列表。**三级分层链深体系**：T1=SSoT定义者（≤1层，glossary/metadata），T2=框架构建者（≤2层，doc-structure/classification），T3=治理执行者（≤3层，其余meta文件）。铁律：仅指向 `meta/` 或 `AGENTS.md`；超过本层级上限的引用写在 prose 正文不在 depends_on；禁止循环引用；跨域引用（governance/operational/domains/modules）一律进正文。链深=从本文件沿 depends_on 走到叶子节点的最长步数 |
| 20 | **Tier 1/2/3 消费者** | Consumer Tier | 消费者影响等级：Tier 1（硬编码了规则编号的文件，变更必须同步）> Tier 2（消费规则但不硬编码编号，变更建议同步）> Tier 3（间接消费，变更可事后通知） |
| 21 | **ABS / COND / REC** | Absolute / Conditional / Recommended | 行为边界三级编号体系（PS-STD-003）：ABS-XX = 绝对禁止（任何情况不可违反），COND-XX = 条件禁止（特定条件下不可违反），REC-XX = 推荐做法 |
| 22 | **安全升级** | Safety Escalation | MOD-INF-022 SSoT——AI操作安全级别从低到高迁移（autonomous→auto_guard→blocked）。触发条件：规则匹配+置信度+熔断器状态。与"权限提升"是不同概念 |
| 23 | **权限提升** | Privilege Escalation | MOD-INF-018 SSoT——Agent获取超出其角色授权的权限。属于安全威胁（OWASP ASI03），RBAC L4 Sequence Guard 专门防护。与"安全升级"是不同概念 |
| 24 | **委托链** | Delegation Chain | MOD-INF-022 SSoT——任务在Agent间传递的权限递减链（四级约束+MAX_DEPTH=3）。每跳scope收窄，TLA+验证安全性 |

---

## 消费者注册表

| 消费者 | 消费方式 | Tier |
|--------|---------|:----:|
| 全部 meta/ 文件 | 术语定义以本表为准 | 1 |
| 全部 governance/ 文件 | 术语定义以本表为准 | 1 |
| 新 AI session | 首读文件之一——快速对齐术语理解 | 1 |

---

## 新增术语流程

当新概念出现需要加入术语表时：

1. **提议**：AI 或 Owner 在 Session Log 中提议新增术语，格式：`新增术语: {中文} / {英文} / {定义}`
2. **审核**：Owner 审核定义是否准确、是否与现有术语冲突
3. **添加**：按字母序插入本表
4. **级联检查**：搜索已存在的规则文件——如果该术语在现有文件中已有局部定义，需更新为引用本表（或标注"以术语表为准"）

**禁止**：绕过术语表直接在文件中定义新术语（术语先入表，再被引用）。

---

## 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.3.0 | 2026-05-02 | #19 depends_on 从"1层死规则"升级为**三级分层链深体系**（T1≤1/T2≤2/T3≤3）。新增铁律：仅指向 meta/ 或 AGENTS.md；跨域引用进正文；禁止循环引用。对标分层架构：SSoT定义者→框架构建者→治理执行者，每层链深上限严格递增以最大化上下文节省。 |
| 1.2.0 | 2026-05-01 | 修复缺陷。(1) doc_type 从 `glossary`（不在 PS-STD-001 §3.2 受控词表中）改为 `terminology`（M-3 修复）。(2) depends_on 条目引用链阈值改为 1 层死规则（对标 npm `dependencies` + Kubernetes API 直接引用模式）。 |
| 1.1.0 | 2026-05-01 | 新增 2 个术语。(1) #20 Tier 1/2/3 消费者——消费者影响等级（meta/ 中所有消费者注册表依赖此概念）。(2) #21 ABS/COND/REC——行为边界三级编号体系（PS-STD-003 核心编号系统）。术语总数 19→21。 |
| 1.0.0 | 2026-05-01 | 初始创建——meta/ 系统性复查补齐。收录 19 个核心术语，对标 ISO 11179 + ISO/IEC Directives Part 2 §5。 |
