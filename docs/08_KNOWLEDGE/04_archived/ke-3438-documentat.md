---
module_id: KE-3438
title: 4.5.4 完整字段分类表
category: documentation
---

# 4.5.4 完整字段分类表

4.5.4 完整字段分类表

| 字段 | 类型 | 大小写 | 示例 |
|------|------|:------:|------|
| `status` | 枚举值 | 小写 | `draft` `active` `deprecated` |
| `doc_type` | 枚举值 | 小写 | `standard` `policy` `blueprint` |
| `classification` | 枚举值 | 小写 | 域 A：`public` `confidential`（推荐）；域 B 任务另见 §4.6 / §7.1 |
| `layer` | 枚举值 | 小写 | `infra_ops` `cross_layer` |
| `ai_autonomy_level` | 枚举值 | 小写 | `immutable_core` `ai_modifiable` `human_gated` |
| `ttl` | 枚举值 | 小写 | `permanent` `30d` `7d` `session` `periodic_review_90d` |
| `language` | 枚举值 | 小写 | `zh` `en` `zh_en` |
| `module_id` | **标识符** | **大写** | `L00-DS-001` `KBG-0011` `PS-STD-001` `KE-016` |
| `title` | 自由文本 | 自然语言 | `编码安全规范` |
| `version` | 语义版本 | 数字 | `1.0.0` |
