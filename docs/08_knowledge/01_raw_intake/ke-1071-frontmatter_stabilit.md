---
module_id: KE-986---frontmatter-----stabilit-006
status: active
title: 6.3 新 frontmatter 字段：`stability`
category: governance_rule
ttl: permanent
doc_type: knowledge_entry
---

# 6.3 新 frontmatter 字段：`stability`

6.3 新 frontmatter 字段：`stability`

```yaml
stability: frozen | stable | evolving
```

- **必填**：是（新增规则文档时）
- **默认值**：`stable`（如果未指定）
- **校验**：值必须在受控词表中
- **与 `ai_autonomy` 的一致性约束**：`frozen` 必须对应 `immutable_core`（单向强制）。其余组合无硬性约束，遵循 PS-STD-001 §2.6 架构公民原则——`stability` 描述变更频率，`ai_autonomy` 描述修改权限，两者正交。

---
