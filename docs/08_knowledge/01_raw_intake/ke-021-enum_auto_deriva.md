---
module_id: KE-021----------enum-auto-deriva-006
status: active
title: 6.13 枚举自动派生铁律（Enum Auto-Derivation Mandate）
category: agent_instruction
ttl: permanent
doc_type: knowledge_entry
---

# 6.13 枚举自动派生铁律（Enum Auto-Derivation Mandate）

6.13 枚举自动派生铁律（Enum Auto-Derivation Mandate）

> **v1.0.0（2026-05-03）**：触发条件——任何对 vocabulary YAML 中枚举值的增删改操作。对标 OpenAPI → `spec.yaml` 是 canonical，`swagger-ui` 是派生 / Terraform → `.tf.json` 是 canonical，`terraform-docs` 是派生 / K8s → CRD YAML 是 canonical，`kubectl explain` 是派生。三家机构一致：**canonical 改了，派生必须自动跟上，不能靠人记得更新。**

**核心原则**：**vocabulary YAML 是枚举值的唯一真源，所有其他文件中的枚举列表必须从 vocabulary YAML 派生——不是手动硬编码第二份。** 手动维护多份枚举列表 = 漂移不可避免。

- **问题根源**（2026-05-03 审计发现 44 项问题中 80% 的根因）：
  - `doc_type` 枚举在 5 个文件中独立硬编码（vocabulary 26 值、schema 12 值、field-registry 7 值、architecture-contract 7~10 值、metadata-registry 23~26 值）
  - `status` 枚举在 5 个文件中独立硬编码
  - `rule_form` 枚举在 5 个文件中独立硬编码
  - `ttl` 枚举在 5 个文件中独立硬编码，2 个文件缺少新增值
  - `layer` 枚举在 4 个文件中独立硬编码，1 个文件含历史遗留重复值
  - 每次新增/废弃枚举值需同时更新 5+ 处，Vibe Coding AI 的上下文记忆极短（§5.1），必然漏改

- **强制规则**：
  1. **vocabulary YAML = canonical SSoT**：所有枚举值的增删改必须先在 vocabulary YAML 中操作
  2. **派生文件禁止手动硬编码枚举列表**：frontmatter-field-registry.md、architecture-contract.yaml、frontmatter-schema.json 中的枚举值应标注 `derived_from: {vocabulary_yaml_path}`，且由脚本自动生成或校验
  3. **修改枚举值时的原子事务**：在 vocabulary YAML 中增删改枚举值时，MUST 在同一 session 内同步更新所有派生文件。具体清单：
     - `_registry/vocabularies/{field}-vocabulary.yaml`（canonical SSoT）
     - `_registry/catalogs/frontmatter-field-registry.md`（派生——字段数据）
     - `_registry/contracts/architecture-contract.yaml`（派生——契约约束）
     - `_registry/schemas/frontmatter-schema.json`（派生——JSON Schema）
     - `meta/metadata_registry.yaml`（派生——速查引用）
     - `_registry/catalogs/registry-master-index.yaml`（派生——entry_count）
  4. **CI 门禁强制校验**：`validate_enum_consistency.py` 自动比对 vocabulary YAML 与所有派生文件的枚举列表，不一致 → CI 失败

- **专业参考**：OpenAPI → `spec.yaml` 是 canonical，`swagger-ui` 是派生（spec 改了 UI 自动更新）/ Terraform → `.tf.json` 是 canonical，`terraform-docs` 是派生（state 改了 docs 自动更新）/ K8s → CRD YAML 是 canonical，`kubectl explain` 是派生（CRD 改了 explain 自动更新）/ ITIL SACM → CI 属性变更必须同步到所有消费该属性的 CMDB 视图
