---
module_id: KE-module_blu-6_3-000
title: 6.3 漂移严重度评估
category: module_blueprint
---

# 6.3 漂移严重度评估

6.3 漂移严重度评估

```python
def _assess_drift(zombie_count: int, orphan_count: int) -> Severity:
    total_drift = zombie_count + orphan_count
    if total_drift == 0:
        return Severity.GREEN
    if total_drift <= 3:
        return Severity.YELLOW
    return Severity.RED  # >3 个漂移 = 注册表严重滞后
```

---
