---
module_id: KE-204
status: active
title: 2.4 YAML 文件特殊规则
category: documentation
---

# 2.4 YAML 文件特殊规则

2.4 YAML 文件特殊规则

- `status` 使用小写：`active` / `draft` / `deprecated`（仅 3 值，`superseded` 已废弃——见 status-vocabulary.yaml deprecated_values）
- 必须包含 `schema_version` 字段
- 日期字段使用 ISO 8601 格式
