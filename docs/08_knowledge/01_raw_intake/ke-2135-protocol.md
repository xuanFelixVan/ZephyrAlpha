---
module_id: KE-2043
status: active
title: 3.1 Protocol 签名
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.1 Protocol 签名

3.1 Protocol 签名

```python
class PipelineServiceProtocol:
    async def route(self, task_id: str, task_type: str, priority: str,
                    model_affinity: dict | None = None) -> PipelineRouteDecision:
        """路由决策——根据task_type/priority/model_affinity选择A区/B区管线"""

    async def dispatch(self, task_id: str, route: PipelineRouteDecision) -> DispatchResult:
        """调度执行——按路由决策分配模块和模型"""

    async def execute(self, dispatch_id: str) -> PipelineResult:
        """执行管线——按M1-M11模块序列执行"""

    async def cancel(self, dispatch_id: str, reason: str) -> CancelResult:
        """取消执行——安全中断正在运行的管线"""

    async def get_status(self, dispatch_id: str) -> DispatchStatus:
        """查询状态——获取当前管线执行进度"""

    async def list_active(self, filters: dict | None = None) -> list[DispatchSummary]:
        """活跃调度列表——监控面板用"""
```
