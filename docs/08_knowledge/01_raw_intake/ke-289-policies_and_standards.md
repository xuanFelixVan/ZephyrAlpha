---
module_id: ke-documentat-3-2-1--01-policies-and-standar-005
title: 3.2.1 `01_policies_and_standards/` 子集（13 值）
category: documentation
ttl: permanent
---

# 3.2.1 `01_policies_and_standards/` 子集（13 值）

3.2.1 `01_policies_and_standards/` 子集（13 值）

> 全项目有 27 种 doc_type，但 `01_policies_and_standards/` 目录下**只使用以下 13 种**。
> 其他 doc_type（如 `blueprint`、`construction_plan`、`roadmap`、`knowledge_entry`）属于其他目录，不在此处使用。
> **例外**：`templates/` 下的模板文件不受此 13 值子集约束——模板 doc_type 取目标文档类型。
> 例如 `blueprint-construction-template.md` 的 `doc_type: blueprint` 合法（它为蓝图提供模板，其 doc_type 表达的是目标，不是文件本身的分类）。
status: active

| # | doc_type | 含义 | 对应目录 | rule_form |
|---|----------|------|---------|-----------|
| 1 | `policy` | 强制约束 | `governance/` | 声明式 |
| 2 | `standard` | 推荐做法 | `governance/` | 声明式 |
| 3 | `operational_rule` | 操作规程 | `operational/` | 过程式 |
| 4 | `register` | 登记表 | `_registry/` | 数据 |
| 5 | `index` | 目录索引 | 所有目录 | 声明式 |
| 6 | `protocol` | 协议 | `governance/` | 声明式 |
| 7 | `terminology` | 术语表 | `meta/` | 数据 |
| 8 | `template` | 模板 | `templates/` | 结构 |
| 9 | `vocabulary` | 受控词表 | `_registry/vocabularies/` | 数据 |
| 10 | `contract` | 验证契约 | `_registry/contracts/` | 数据 |
| 11 | `reference` | 参考文档 | `_registry/catalogs/` | 数据 |
| 12 | `gate` | 质量门禁 | `_registry/` | 声明式 |
| 13 | `schema` | Schema 定义 | `_registry/schemas/` | 数据 |
