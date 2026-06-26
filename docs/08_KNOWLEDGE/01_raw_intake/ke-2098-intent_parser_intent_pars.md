---
module_id: KE-2007---intent-pars-000
status: active
title: 3. Intent Parser — intent_parser.py (§5.1 BUILD-C00)
category: module_blueprint
ttl: permanent
---

# 3. Intent Parser — intent_parser.py (§5.1 BUILD-C00)

3. Intent Parser — intent_parser.py (§5.1 BUILD-C00)

实现 `IntentType` 枚举 (10 类):
- CODE_GEN, CODE_REVIEW, ANALYSIS, OPS_FIX, DOC, REFACTOR, TEST, AUDIT, QUERY, DEBUG

`classify(user_prompt: str) -> IntentType`:
- on_failure: flag（仅标记，不阻断后续流程）
