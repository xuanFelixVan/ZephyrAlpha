---
module_id: KE-087
status: active
title: 1.3.1 YAML 文件子类型
category: documentation
ttl: permanent
---

# 1.3.1 YAML 文件子类型

1.3.1 YAML 文件子类型

项目中的 `.yaml` 文件按**消费者不同**分为两种子类型，遵循不同的 frontmatter 契约：

| 属性 | `document_yaml` | `registry_yaml` |
|------|----------------|-----------------|
| **消费者** | 人类 + AI（阅读+理解+执行） | CI 脚本 / pre-commit（机器解析+校验） |
| **典型文件** | `session-log-schema.yaml`、`model-capability-contract.yaml` | `_registry/` 下所有 .yaml（catalogs/ / contracts/ / vocabularies/） |
| **最小必填字段** | module_id, title, doc_type, status, version, date, owner（7 项——同 .md 文件） | schema_version, doc_type, title, status（4 项） |
| **不要求的字段** | — | module_id, rule_form, scope, stability, verifiability, layer（registry_yaml 不参与规则推导链） |
| **depends_on 要求** | 必须声明——glossary #19 规定引用链 ≤ 1 层 | 必须声明——声明依赖的元标准文件（如 PS-STD-001） |

> **裁定依据**：`_registry/` 下的文件是**机器消费的数据结构**（词表清单、索引注册表、校验契约），不是人类阅读的 prose 规则文档。强行套用 document_yaml 的 14 个必填字段（Active 阶段）会导致"词表文件被迫填 rule_form: data 假装自己是规则"的形式主义。承认其 `registry_yaml` 身份后，每个子类型只要求其消费者真正需要的字段。

> **文件扩展名区分**：`.yaml` 统一走 `registry_yaml` 契约；`.md` 统一走 `document_yaml` 契约。`_registry/schemas/` 下的 `.json` 文件（如 frontmatter-schema.json）不受本标准 frontmatter 约束——JSON 文件自带 `$schema` 自描述。
