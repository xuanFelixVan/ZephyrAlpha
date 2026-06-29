---
title: Ke Documentat 4 3 Vibe Coding 004
module_id: KE-352---

﻿---
module_id: ke-documentat-4-3-vibe-coding-004
title: 4.3 Vibe Coding 条件禁止
category: documentation
ttl: permanent
---

# 4.3 Vibe Coding 条件禁止

4.3 Vibe Coding 条件禁止

| #       | 条件禁止行为                               | 触发条件            | 替代方案             | 来源                                |
| ------- | ------------------------------------ | --------------- | ---------------- | --------------------------------- |
| COND-09 | COMPLETED→ACTIVE 状态转换                | 会话状态机运行时        | 状态转换表硬编码，运行时断言   | vibe-coding-gate-runbook.md |
| COND-10 | 同时加载所有层上下文                           | 任务涉及多个架构层时      | 只加载相关层的上下文       | vibe-coding-session-state-runbook.md      |
| COND-11 | 施工者自行设 `verification_status: passed` | 施工完成后自检时        | 由审计者（非施工者）填写     | blueprint-construction-template.md §12.6     |
| COND-12 | 自行创建新路径存放产出物                         | 施工阶段            | 严格按蓝图 §7 规划的路径存放 | blueprint-construction-template.md             |
| COND-13 | 隐藏未解问题                               | 交接或 session 结束时 | 必须记录，不得隐瞒        | handoff-protocol.md               |
