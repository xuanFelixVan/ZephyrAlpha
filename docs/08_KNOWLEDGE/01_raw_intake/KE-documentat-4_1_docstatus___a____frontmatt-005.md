---
module_id: KE-documentat-4_1_docstatus___a____frontmatt-005
title: 4.1 DocStatus（域 A：文档 frontmatter）
category: documentation
---

# 4.1 DocStatus（域 A：文档 frontmatter）

4.1 DocStatus（域 A：文档 frontmatter）

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
