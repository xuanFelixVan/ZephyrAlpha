---
module_id: KE-2426
title: 7.1 指令格式要求
category: module_blueprint
ttl: permanent
---

# 7.1 指令格式要求

7.1 指令格式要求

| 要求 | 原因 |
|------|------|
| 所有 Skill 指令使用 **Checklist 格式**（checkbox 列表） | Vibe Coding 中大段描述容易被 AI 忽略——checklist 是零歧义的 |
| 使用 `CRITICAL:` 前缀标记绝不可违反的铁律 | 对标 Codified Context 的 coordinate-wizard 实践——4 条 CRITICAL 规则比 40 条建议更有效 |
| 每个指令后附 **断言格式的验证步骤**（"门禁 PASS ✓"、"pytest 0 failures ✓"） | 确保每个操作有明确的"完成"定义 |
| 避免"建议/最好/推荐"等弱化词 | 弱指令 = 执行不可靠 |
