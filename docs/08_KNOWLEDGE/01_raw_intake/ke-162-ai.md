---
module_id: KE-148
status: active
title: §16 AI 自治权限标注
category: documentation
---

# §16 AI 自治权限标注

§16 AI 自治权限标注

> v3.1.0 **不再作为独立 MUST 章节**。AI 自治权限已在 frontmatter 的 `ai_autonomy` 字段中声明。
> 禁止在 body 中用 prose 重复 frontmatter 已声明的信息（详见 §3.2.3）。
>
> `ai_autonomy` 合法值（定义在 PS-STD-001 §10.3）：
>
> | 值 | 含义 | AI 行为 |
> |---|------|--------|
> | `immutable_core` | 不可变核心，AI 禁止修改 | 违反时停止操作，上报 Owner |
> | `human_gated` | 人工门控，AI 需 Owner 批准才能执行 | 请求 Owner 审批后执行 |
> | `ai_editable` | AI 可自主执行 | 自主执行，记录在 Session Log |
>
> 本标准中每条规则的自治权限分配，在 §15（AI 可消费性声明）中总览说明。
