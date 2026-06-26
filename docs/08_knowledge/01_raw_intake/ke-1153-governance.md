---
module_id: KE-1068
status: active
title: AI 幻觉自检清单
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# AI 幻觉自检清单

AI 幻觉自检清单

> **目的**：每个 AI session 开始前必须逐项自检，防止 AI 在无完整上下文的情况下幻觉补全架构信息、文件路径、接口定义等关键内容。
>
> **旧体系教训**：AI 在不知道完整架构的情况下，会幻觉补全接口（超时、重试、异常类型）、编造不存在的文件路径、推断错误的依赖关系，导致架构污染。
