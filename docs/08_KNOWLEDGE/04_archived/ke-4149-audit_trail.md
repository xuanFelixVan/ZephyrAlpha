---
module_id: KE-3994
title: 2.1 Audit Trail 集成
category: module_blueprint
ttl: permanent
---

# 2.1 Audit Trail 集成

2.1 Audit Trail 集成

| Skill 事件 | Audit Entry Type | 内容 |
|-----------|-----------------|------|
| skill_loaded | AI_ACTION(type_id=1) | skill_id + domain + role + trigger_reason + timestamp |
| skill_applied | TASK_COMPLETE(type_id=3) | skill_id + execution_steps + artifact_hash + gate_result |
| skill_drift_detected | ANOMALY(type_id=6) | skill_id + drift_type + drift_diff + freshness_score |
| skill_unloaded | AI_ACTION(type_id=1) | skill_id + execution_summary + next_step → Session Resume |
