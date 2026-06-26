---
module_id: KE-1991
status: active
title: 3. Anti-Affinity 校验
category: module_blueprint
ttl: permanent
---

# 3. Anti-Affinity 校验

3. Anti-Affinity 校验

```python
if M3_model == M7_model:
    raise AffinityViolation("M3和M7必须使用不同模型——双盲审查不可同模")
```
