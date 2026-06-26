---
module_id: KE-2805
status: active
title: Orchestrator 侧
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# Orchestrator 侧

Orchestrator 侧
class Orchestrator:
    def create_task(self, task_card: TaskCard):
        # Step 1: 交给Pipeline做路由决策
        result = self.pipeline.dispatch(task_card)

        # Step 2: 根据PipelineResult决定后续动作
        if result.overall_status == PipelineStatus.CLAUDE_RESCUE:
            self.schedule_rescue(task_card, result.rescue_reason)
        elif result.overall_status == PipelineStatus.LOCKED:
            self.deferred_queue.enqueue(task_card)  # B72 DeferredQueue
        else:
            self.assign_session(task_card, result)
            self.notify_owner(result)  # B515 告警触达
```
