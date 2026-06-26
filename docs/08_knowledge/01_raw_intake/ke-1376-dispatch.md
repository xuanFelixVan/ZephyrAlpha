---
module_id: KE-1287
status: active
title: 1. dispatch 扩展
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 1. dispatch 扩展

1. dispatch 扩展

```python
def dispatch(self, task_card: TaskCard, dry_run: bool = False) -> PipelineResult:
    route = resolve_route(task_card)

    if dry_run:
        return PipelineResult(
            task_id=task_card.task_id,
            pipeline=route.node_id[:1],  # A/B from node prefix
            modules_executed=[],         # 无实际执行
            overall_status=PipelineStatus.SUCCESS,
            ct_pipe_route=route,
            is_dry_run=True,
            cost_total_usd=0.0,
            cost_records=[],
        )

    # ... 正常dispatch流程
```
