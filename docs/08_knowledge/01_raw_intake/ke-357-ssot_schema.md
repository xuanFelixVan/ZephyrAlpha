---
module_id: KE-322---schema-002
title: 4.11 SSoT 与 Schema 一致性条件禁止
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 4.11 SSoT 与 Schema 一致性条件禁止

4.11 SSoT 与 Schema 一致性条件禁止

| #       | 条件禁止行为                                     | 触发条件                 | 替代方案                                           | 来源                                                      |
| ------- | ------------------------------------------ | -------------------- | ---------------------------------------------- | ------------------------------------------------------- |
| COND-38 | 引用 Deprecated ADR 作为当前决策依据                 | 引用 ADR 时             | 必须确认 ADR status 为 Active，Deprecated ADR 仅作历史参考 | ssot-authority-map.md                                   |
| COND-39 | 同一 module\_id 在两个 Active 文件中出现             | 注册/更新 module\_id 时   | module\_id 必须全局唯一，禁止权限漂移                       | ssot-authority-map.md, validate\_authority\_registry.py |
| COND-40 | Schema 三处（ADR / DDL / Pydantic Model）不同步更新 | 修改 schema 字段时        | 新增字段必须同时更新 ADR + SQLite DDL + Pydantic Model   | adr-0040, schemas.py                                    |
| COND-41 | SSoT 注册表与实际文件不同步                           | git commit 涉及治理敏感文件时 | 新增/删除治理文件时注册表必须同步暂存                            | ssot\_guard.py                                          |
