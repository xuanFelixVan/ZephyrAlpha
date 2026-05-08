---
module_id: KE-session_lo-1_3-002
title: 1.3 核心设计原则
category: session_log
---

# 1.3 核心设计原则

1.3 核心设计原则

| 原则 | 说明 |
|------|------|
| **可机器读写 + 可人工审阅** | JSON 格式，frontmatter 友好；字段命名自解释 |
| **版本化**：`schema_version` 字段强制 | 未来 schema 演化时，老文件可被自动迁移 |
| **幂等写入** | 多次调用 `save()` 以最后一次为准 |
| **单文件 SSoT** | 每个项目根只有一份 `session_carryover.json` |
| **机密隔离** | 不写入敏感信息（API Key / Secret）|

---
