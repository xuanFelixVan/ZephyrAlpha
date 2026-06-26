---
module_id: KE-044------bidirectional-deep-di-001
status: active
title: 7.3 双向深挖（Bidirectional Deep Dive）
category: agent_instruction
ttl: permanent
doc_type: knowledge_entry
---

# 7.3 双向深挖（Bidirectional Deep Dive）

7.3 双向深挖（Bidirectional Deep Dive）

每个问题从两个方向同时挖掘：

- **从上而下（架构层面）**：这个问题暴露了什么架构缺陷？当前架构设计是否允许这类问题产生？如果专业机构面对同样的规模，他们会怎么设计来防止这类问题？
- **从下而上（实例层面）**：这个问题具体影响了哪些文件？修复后能覆盖哪些场景？还有哪些未被发现的同类实例？

两个方向的结论必须**汇合**——架构结论要能解释实例，实例要能验证架构结论。

- **诊断反转验证**：深挖完成后，MUST 回溯初始诊断——初始诊断与深挖结论一致吗？不一致 → 追问"为什么初始诊断是错的？" → 更新症状-根因映射表。防止基于错误初始诊断执行修复，越改越错。
