---
module_id: KE-1990
status: active
title: 3. Affinity Enforcement（§2.5约束落地）
category: module_blueprint
ttl: permanent
---

# 3. Affinity Enforcement（§2.5约束落地）

3. Affinity Enforcement（§2.5约束落地）

```yaml
affinity_enforcement:
  - check: "M3.model == M7.model"
    on_violation: "ABORT + escalate: 双盲审查模型冲突"
  - check: "M8.model != M9.model"
    on_violation: "WARN: 建议 M8/M9 使用不同模型交叉覆盖"
```
