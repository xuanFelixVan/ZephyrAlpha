---
module_id: KE-034
status: active
title: 6.6.2 doc_type 使用规范
category: agent_instruction
ttl: permanent
---

# 6.6.2 doc_type 使用规范

6.6.2 doc_type 使用规范

登记表文件的 `doc_type` 必须根据内容类型正确选择：
- `_registry/catalogs/*.yaml` → `doc_type: register`
- `_registry/vocabularies/*.yaml` → `doc_type: vocabulary`
- `_registry/contracts/*.yaml` → `doc_type: contract`
