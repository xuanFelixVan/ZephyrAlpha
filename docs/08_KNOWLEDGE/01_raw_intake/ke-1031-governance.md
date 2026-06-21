---
module_id: KE-951
status: active
title: 5.2 分类规则
category: governance_rule
---

# 5.2 分类规则

5.2 分类规则

1. 每条规则必须且只能有一个 scope
2. scope 决定了规则变更时的通知范围：
   - `global` 变更：通知所有 Tier 1 消费者
   - `domain` 变更：通知该领域内的 Tier 1 消费者
   - `module` 变更：通知引用该模块的 Tier 1 消费者
   - `session` 变更：无需通知，下次 session 自动生效
