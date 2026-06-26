---
module_id: KE-3786
title: 验证 §10 中每个路径在磁盘上存在或标记状态一致
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 验证 §10 中每个路径在磁盘上存在或标记状态一致

验证 §10 中每个路径在磁盘上存在或标记状态一致
python scripts/governance/validate_blueprint_code_sync.py --module MOD-FEEDBACK_LOOP --audit-paths
```
