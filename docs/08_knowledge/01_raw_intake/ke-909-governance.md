---
module_id: KE-831
status: active
title: 2.7 升级治理
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 2.7 升级治理

2.7 升级治理

以下场景 AI **必须**升级到 Owner，**不得跳过升级直接做决策**：

| 触发条件 | 升级动作 |
|---------|---------|
| P0 任务 BLOCKED 超过 2 个 session | Session Log 中标记 `escalation:owner` |
| 任何任务 BLOCKED 超过 5 个 session | Session Log 中标记 `escalation:owner` |
| P0 任务 FAILED 2 次 | 等待 Owner 决定：创建替代任务 / 降级 |
| 优先级冲突无法自动裁决 | 等待 Owner 裁定 |

升级通知通过 Session Log 的 `open_questions` 字段传递给 Owner。

**Owner 收到升级后的决策选项**：

| 选项 | 动作 | 后续 |
|------|------|------|
| ① 降优先级 | 将任务降为 P3/P4 | 任务按新优先级重新排队 |
| ② 给 Deadline | 在 open_questions 中回复截止时间 | AI 以 deadline 重排优先级 |
| ③ 取消任务 | 状态 → CANCELLED | 释放所有依赖它的任务 |
| ④ 不变 | 确认当前优先级合理 | AI 继续按原优先级执行 |

---
