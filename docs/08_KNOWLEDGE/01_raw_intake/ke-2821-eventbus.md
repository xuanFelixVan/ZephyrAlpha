---
module_id: KE-2724
status: active
title: EventBus 监听
category: module_blueprint
---

# EventBus 监听

EventBus 监听
self.event_bus.subscribe("PIPELINE_SIGNAL", self._on_pipeline_signal)

async def _on_pipeline_signal(self, signal: PipelineSignal):
    if signal.action == "cancel" and signal.task_id in self._active:
        await self.cancel_dispatch(signal.task_id)
    elif signal.action == "modify_priority":
        # 更新优先级→可能触发preemption
    elif signal.action == "switch_model":
        # 当前模块失败后切换到指定模型
```
