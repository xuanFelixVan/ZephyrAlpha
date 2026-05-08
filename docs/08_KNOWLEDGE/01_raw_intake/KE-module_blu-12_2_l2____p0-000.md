---
module_id: KE-module_blu-12_2_l2____p0-000
title: 12.2 L2 隔离 P0
category: module_blueprint
---

# 12.2 L2 隔离 P0

12.2 L2 隔离 P0

| # | 用例 | 预期 |
|:-:|------|------|
| P0-L2-1 | UNTRUSTED 内容出现在 `<untrusted_input>` 标签内 | - |
| P0-L2-2 | XML 特殊字符转义（`<` → `&lt;`） | 无 XML 注入风险 |
| P0-L2-3 | guardrails 正确注入 | - |
