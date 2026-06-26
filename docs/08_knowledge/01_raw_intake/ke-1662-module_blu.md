---
module_id: KE-1572
status: active
title: 17.2 门禁组合逻辑
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 17.2 门禁组合逻辑

17.2 门禁组合逻辑

当前`entry_conditions`是扁平AND——顶尖设计应支持任意布尔组合：

```yaml
check_expression: "(G0-C00 AND G0-C01) OR (admin_override == true)"
