---
module_id: KE-758
status: active
title: §1 任务系统的分层架构
category: governance
ttl: permanent
---

# §1 任务系统的分层架构

§1 任务系统的分层架构

ZephyrAlpha 的任务系统横跨 5 层：

```
┌──────────────────────────────────────────────────┐
│ 第 1 层：Schema（字段定义）                         │
│   meta/metadata_registry.yaml §7                    │
│   30 个任务卡字段的完整定义 + task_id 格式 + 枚举值     │
├──────────────────────────────────────────────────┤
│ 第 2 层：治理规则（怎么管）                           │
│   governance/task/   ← 你现在看的这个目录             │
│   ├── task-card-standard.md   操作指南：怎么写任务卡    │
│   ├── task-lifecycle-standard.md  治理规则：权限/优先级 │
│   └── task-closure-standard.md  关闭验证：残留清扫    │
├──────────────────────────────────────────────────┤
│ 第 3 层：施工计划（怎么做）                          │
│   03_modules/infra_ops/                  │
│   └── task-system/blueprint.md §5.2-§5.5       │
│       状态机实现 + G0-G6 门禁 + 超时升级 + 消费者      │
├──────────────────────────────────────────────────┤
│ 第 4 层：治理协议（跨域交叉）                          │
│   governance/ai/handoff-protocol.md               │
├──────────────────────────────────────────────────┤
│ 第 5 层：代码实现                                     │
│   src/zephyr/shared/schemas.py（Task / TaskCard 基座模型）             │
│   src/zephyr/db/task_repo.py (CRUD)                │
│   src/zephyr/gates/task_completion_gate.py (G5)    │
│   src/zephyr/mcp/task_manager_server.py             │
└──────────────────────────────────────────────────┘
```

---
