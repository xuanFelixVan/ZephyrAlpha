---
module_id: KE-1610---conte-000
status: active
title: 2. Core Implementation — context_injector.py (§2.4)
category: module_blueprint
ttl: permanent
---

# 2. Core Implementation — context_injector.py (§2.4)

2. Core Implementation — context_injector.py (§2.4)

```python
def inject(session: AgentSession, context: ValidatedContext) -> InjectionResult:
    full_context = format_context(context)
    session.system_prompt += full_context
    return InjectionResult(token_count, sources)
```
