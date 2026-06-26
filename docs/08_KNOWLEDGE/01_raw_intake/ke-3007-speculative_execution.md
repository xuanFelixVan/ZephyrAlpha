---
module_id: KE-2907
status: active
title: Speculative Execution
category: module_blueprint
ttl: permanent
---

# Speculative Execution

Speculative Execution

```python
class SpeculativeExecutor:
    """RI-01 EventBus 投机执行——关键路径同时发 2 路，取最快返回"""
    async def emit_with_hedge(self, event: Event,
                              replicas: int = 2) -> EventResult:
        """发送到 N 个消费者，第一个完成的结果直接返回"""
        tasks = [consumer.handle(event) for consumer in self._replicas[:replicas]]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        return done.pop().result()
```
