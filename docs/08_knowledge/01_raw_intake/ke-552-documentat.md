---
module_id: KE-500
status: active
title: 7.3 复合命名规则（当二者联合引用时）
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 7.3 复合命名规则（当二者联合引用时）

7.3 复合命名规则（当二者联合引用时）

当需要联合描述"某代码的治理层 + 运行平面"时，使用**双标签语法**：

```
L04.limits.hard_cut.py  →  [GOV:Runtime] × [Plane:Hot]
L02.pipeline.batch.py   →  [GOV:Runtime] × [Plane:Cold]
scripts/governance/aisg/compile_desensitize_rules.py  →  [GOV:Factory] × [Plane:Cold]
docs/01_policies_and_standards/ai-security-gateway-policy.md  →  [GOV:Policy] × [Plane:—]
```

**格式**：`[GOV:<Policy|Factory|Runtime>] × [Plane:<Hot|Warm|Cold|—>]`
