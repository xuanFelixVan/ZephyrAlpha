---
module_id: KE-139---ps-std-001-000
status: active
title: §13 与 PS-STD-001 的字段不重复声明
category: documentation
---

# §13 与 PS-STD-001 的字段不重复声明

§13 与 PS-STD-001 的字段不重复声明

> v3.1.0 改为**条件性**——仅在标准定义了 PS-STD-001 未覆盖的字段时必含。
> 根因：field-naming-standard.md 和 metadata_registry.yaml 都定义了 layer 格式，导致漂移。
> 绝大多数 L1 标准不定义新字段 → 不需要此章节。

**触发条件**：本标准定义了自己的字段（frontmatter 或 body 中）且该字段不在 PS-STD-001 的字段清单中。

**不适用时**：标准不定义字段或所有字段已在 PS-STD-001 中定义 → 不写本章节。

**适用时**必须声明：

```markdown
