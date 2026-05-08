---
module_id: KE-module_blu-3__affinity_enforcement__2_5-000
title: 3. Affinity Enforcement（§2.5约束落地）
category: module_blueprint
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
