---
module_id: KE-3238
title: 核心术语（21 个）
category: documentation
---

# 核心术语（21 个）

核心术语（21 个）

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

---
