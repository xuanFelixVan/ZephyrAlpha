---
module_id: KE-agent_inst-6_6_2_doc_type-000
title: 6.6.2 doc_type 使用规范
category: agent_instruction
---

# 6.6.2 doc_type 使用规范

6.6.2 doc_type 使用规范

登记表文件的 `doc_type` 必须根据内容类型正确选择：
- `_registry/catalogs/*.yaml` → `doc_type: register`
- `_registry/vocabularies/*.yaml` → `doc_type: vocabulary`
- `_registry/contracts/*.yaml` → `doc_type: contract`
