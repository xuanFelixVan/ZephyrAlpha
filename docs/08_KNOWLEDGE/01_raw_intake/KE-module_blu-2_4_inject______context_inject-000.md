---
module_id: KE-module_blu-2_4_inject______context_inject-000
title: 2.4 Inject（注入）— context_injector.py
category: module_blueprint
---

# 2.4 Inject（注入）— context_injector.py

2.4 Inject（注入）— context_injector.py

```python
def inject(session: AgentSession, context: ValidatedContext) -> InjectionResult:
    full_context = format_context(context)
    session.system_prompt += full_context
    return InjectionResult(token_count, sources)
```

---
