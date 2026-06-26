---
module_id: KE-291
status: active
title: 3.4 doc_type 与存放路径的映射
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 3.4 doc_type 与存放路径的映射

3.4 doc_type 与存放路径的映射

> Canonical SSoT 见 vocabulary YAML 各条目的 `allowed_directories` 和 `forbidden_directories` 字段。
> 以下为关键规则速查——不含已废弃类型。

| doc_type | 应存放的目录 | 禁止存放的目录 |
|----------|------------|--------------|
| `policy` | `01_policies_and_standards/governance/` | `03_modules/` `08_knowledge/` |
| `standard` | `01_policies_and_standards/governance/` `08_knowledge/` | `03_modules/` |
| `adr` | `02_enterprise_architecture/adr/` | 其他所有目录 |
| `blueprint` | `03_modules/l<NN>_<layer>/<module>/` | `01_policies_and_standards/` |
| `construction_plan` | `03_modules/l<NN>_<layer>/<module>/` | `01_policies_and_standards/` |
| `architecture_view` | `02_enterprise_architecture/target_architecture/` | `01_policies_and_standards/` `03_modules/` |
| `design` | `02_enterprise_architecture/` | | `01_policies_and_standards/` `03_modules/` |
| `operational_rule` | `01_policies_and_standards/operational/` | `governance/` `03_modules/` |
| `protocol` | `01_policies_and_standards/governance/` | `03_modules/` |
| `register` | `01_policies_and_standards/_registry/` | `03_modules/` |
| `vocabulary` | `01_policies_and_standards/_registry/vocabularies/` | `governance/` `operational/` |
| `contract` | `01_policies_and_standards/_registry/contracts/` | `governance/` `operational/` |
| `template` | `01_policies_and_standards/templates/` | — |
| `terminology` | `01_policies_and_standards/meta/` | — |
| `index` | 各目录根 | — |
| `readme` | 各目录根 | — |
| `log` | `09_audit/` | | `03_modules/` |
| `knowledge_entry` | `08_knowledge/` | `01_policies_and_standards/` |
| `audit_report` | `09_audit/` | — |
| `service_spec` | `03_modules/_b_track_interfaces/` | — |
| `plan` | `01_policies_and_standards/` | | — |
| `roadmap` | `01_policies_and_standards/` | | — |
| `declaration` | `docs/`（项目根） | `01_policies_and_standards/` |
