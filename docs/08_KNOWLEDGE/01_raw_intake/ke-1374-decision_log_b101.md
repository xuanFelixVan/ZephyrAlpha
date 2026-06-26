---
module_id: KE-1285
status: active
title: 1. Decision Log（B101）
category: module_blueprint
ttl: permanent
---

# 1. Decision Log（B101）

1. Decision Log（B101）

```python
class RouteDecisionLog(BaseModel):
    log_id: str
    task_id: str
    timestamp: str
    policy_version: str           # pipeline配置版本
    input_params: dict            # {task_type, priority, target_layer, complexity}
    matched_rule: str             # 命中的路由规则
    output_route: PipelineRouteDecision
    affinity_violations: list[str] # 校验发现的冲突
    owner: str                    # 触发dispatch的session
    b134_lineage_hash: str        # HMAC-SHA256 用于数据血缘链
