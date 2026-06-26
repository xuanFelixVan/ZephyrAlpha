---
module_id: KE-2040-------mod-inf--000
title: 3.1 Audit Trail 集成（对接 MOD-INF-020）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.1 Audit Trail 集成（对接 MOD-INF-020）

3.1 Audit Trail 集成（对接 MOD-INF-020）

| Skill 事件 | Audit Entry Type | 记录内容 |
|------------|-----------------|---------|
| `skill_loaded` | `AI_ACTION` (type_id=1) | skill_id + domain + role + 触发原因 + timestamp |
| `skill_applied` | `TASK_COMPLETE` (type_id=3) | skill_id + 执行步骤 + 产出物 hash + 门禁结果 |
| `skill_drift_detected` | `ANOMALY` (type_id=6) | skill_id + 漂移类型 + 漂移内容 diff + freshness_score |
| `skill_unloaded` | `AI_ACTION` (type_id=1) | skill_id + 执行摘要 + 下一步建议（接入 Session Resume） |
