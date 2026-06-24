---
module_id: KE-3966
title: 2. Anthropic Context Engineering (§13.1)
category: module_blueprint
---

# 2. Anthropic Context Engineering (§13.1)

2. Anthropic Context Engineering (§13.1)

| 实践 | 我们有？ | 差距 | 对应任务 |
|------|:---:|------|---------|
| Context Rot 模型 | ❌ | 有预算追踪，无注意力衰减模型 | TASK-014 (beta a) |
| XML Tag 强制分区 | ❌ | Flat concat 注入 | TASK-005 (四层注入) |
| Multi-Turn Curation Loop | ❌ | 单次 build→inject | TASK-014 (beta b) |
| System Prompt 版本化 | ❌ | 未追踪 prompt version | TASK-013 (本任务审计标记) |
| Hybrid Approach | 部分 | context-rules.yaml 存在但未集成 | TASK-010 |
