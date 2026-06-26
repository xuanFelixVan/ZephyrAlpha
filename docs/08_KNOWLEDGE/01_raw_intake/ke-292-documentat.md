---
module_id: KE-270
status: active
title: 3.2.3 已消除的重复章节
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 3.2.3 已消除的重复章节

3.2.3 已消除的重复章节

**§16（AI 自治权限标注）和 §17（可验证性标注）不再作为独立 MUST 章节**。

这两类信息已在 frontmatter 中由以下字段声明：
- `ai_autonomy`：immutable_core / human_gated / ai_editable
- `verifiability`：automated / manual / subjective

**规则**：禁止在 body 中用 prose 章节重复 frontmatter 已声明的信息。frontmatter 是机器可读的 SSoT——AI 读 YAML 零歧义，读 prose 需要推理。重复不仅浪费 Token，还会产生漂移风险（frontmatter 说 A，body 说 B）。

每条规则级别的详细自治权限和验证方式，统一在 §15（AI 可消费性声明）中说明——作为"本标准中的规则如何分配给三种 ai_autonomy 级别"的总览，而非逐条标注。
