---
module_id: KE-governance-2_1_v1-003
title: 2.1 V1 自动化阻断
category: governance_rule
---

# 2.1 V1 自动化阻断

2.1 V1 自动化阻断

当以下条件触发时，操作被**自动阻止**：

| 触发条件 | 阻断规则 | 来源 |
|---------|---------|------|
| frontmatter 缺失或格式错误 | META-V01~V02 | PS-STD-001 §14 |
| doc_type 使用未定义值 | META-V03 | PS-STD-001 §14 |
| 修改 `stability: frozen` 文件 | P0 变更 | PS-STD-009 §2 |
| 删除 `ttl: permanent` 文件 | 禁止删除 | — |
| `blueprint_refs` 引用的蓝图不存在 | META-V16 | PS-STD-001 §14 |
| `index.md` 文件状态与实际 frontmatter `status` 不一致 | META-V21 | PS-STD-012 §2.1 |

**V1 阻断不可绕过**。任何 V1 阻断必须先修复问题，才能继续操作。
