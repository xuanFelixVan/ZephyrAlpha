---
module_id: KE-149
status: active
title: §17 可验证性标注
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# §17 可验证性标注

§17 可验证性标注

> v3.1.0 **不再作为独立 MUST 章节**。可验证性已在 frontmatter 的 `verifiability` 字段中声明。
> 禁止在 body 中用 prose 重复 frontmatter 已声明的信息（详见 §3.2.3）。
>
> `verifiability` 合法值（定义在 PS-STD-001 §10.5）：
>
> | 值 | 含义 | 验证方式 |
> |---|------|---------|
> | `automated` | 可自动验证 | pre-commit hook / pytest / mypy / ruff |
> | `manual` | 需人工验证 | Code Review / Session Log 审计 |
> | `subjective` | 需主观判断 | Owner 裁决 |
>
> 本标准中每条规则的可验证性分配，在 §15（AI 可消费性声明）中总览说明。
