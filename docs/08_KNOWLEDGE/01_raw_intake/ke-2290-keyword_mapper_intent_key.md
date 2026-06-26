---
module_id: KE-2196---intent-key-000
status: active
title: 4. Keyword Mapper — intent_keyword_mapper.py (§5.1 BUILD-C01)
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 4. Keyword Mapper — intent_keyword_mapper.py (§5.1 BUILD-C01)

4. Keyword Mapper — intent_keyword_mapper.py (§5.1 BUILD-C01)

`_MAP: dict[IntentType, list[str]]` 映射表
`map(intent: IntentType) -> list[str]`
- 若映射结果为空：on_failure=reject, fix_hint="补充 intent→keyword 映射到 intent_keyword_mapper.py"
