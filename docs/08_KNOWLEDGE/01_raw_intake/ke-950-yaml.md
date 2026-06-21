---
module_id: KE-872
status: active
title: §3 YAML 模板（直接复制填写）
category: governance
---

# §3 YAML 模板（直接复制填写）

§3 YAML 模板（直接复制填写）

```yaml
session_id: session-YYYYMMDD-NNN
completed_tasks:
  - XXX-NNN
in_progress_tasks:
  - task_id: XXX-NNN
    step: 当前执行到哪一步
    partial_deliverables: [部分产出物路径]
    next_step: 接手后第一个动作
blocked_items:
  - task_id: XXX-NNN
    reason: 一句话原因
decisions_made:
  - topic: 主题
    decision: 决策
    rationale: 理由
next_actions:
  - task_id: XXX-NNN
    priority: P0
context_summary: ≤500 字的自然语言摘要
open_questions: []
```

---
