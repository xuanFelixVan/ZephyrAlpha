---
module_id: KE-2194---5--000
status: active
title: 4. Injection Verification (§5.4 INJECT-C01)
category: module_blueprint
ttl: permanent
---

# 4. Injection Verification (§5.4 INJECT-C01)

4. Injection Verification (§5.4 INJECT-C01)

```
check: "session.system_prompt 包含所有 4 层 AND 总 tokens ≤ session_limit"
on_failure: auto_fix
fix_hint: "超出 limit → 重新 compress → 降低 knowledge 层 top_k"
```
