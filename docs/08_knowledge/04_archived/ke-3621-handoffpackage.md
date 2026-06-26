---
module_id: KE-3476
title: §1 HandoffPackage 8 必填字段
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# §1 HandoffPackage 8 必填字段

§1 HandoffPackage 8 必填字段

| # | 字段 | 类型 | 说明 | 对标 | 示例 |
|---|------|------|------|------|------|
| 1 | `session_id` | string | Session 唯一标识 | ITIL：变更记录 ID | `session-20260424-001` |
| 2 | `completed_tasks` | string[] | 已完成的 task_id 列表 | Agile："我昨天完成了什么" | `["SRC-010", "KBG-007"]` |
| 3 | `in_progress_tasks` | string[] | 未闭环的任务 ID 列表 | Agile："我正在做什么" | `["SRC-013"]` |
| 4 | `blocked_items` | list[{task_id, reason}] | 阻塞项 + 原因 | Agile："有什么阻塞我" | `{task_id: SRC-018, reason: "依赖 SRC-013"}` |
| 5 | `decisions_made` | list[{topic, decision, rationale}] | 关键决策 + 理由 | Michael Nygard ADR 模式 | `{topic: "选型", decision: "SQLite", rationale: "零依赖"}` |
| 6 | `next_actions` | list[{task_id, priority}] | 下一 session 优先执行 | DevOps："下一步行动" | `{task_id: SRC-013, priority: P0}` |
| 7 | `context_summary` | string | 自然语言摘要（≤500 字） | ITIL：变更摘要 | 本 session 完成了 A、遇到 B 问题、建议下一步做 C |
| 8 | `open_questions` | string[] | 向 Owner 暴露的未解问题 | ITIL：未决风险记录 | `["是否需要 schema 校验？"]` |
