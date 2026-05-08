---
module_id: KE-session_lo-8_2-003
title: 8.2 新增字段规则
category: session_log
---

# 8.2 新增字段规则

8.2 新增字段规则

- 新字段必须带默认值或声明为 Optional
- 新增枚举值时，老文件中未出现该值也应能加载
- 禁止删除已有字段（改为 `deprecated: true` 标记后保留 2 个次版本）
