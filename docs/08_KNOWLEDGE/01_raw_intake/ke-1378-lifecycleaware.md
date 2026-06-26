---
module_id: KE-1289
status: active
title: 1. LifecycleAware 实现
category: module_blueprint
ttl: permanent
---

# 1. LifecycleAware 实现

1. LifecycleAware 实现

```python
class PipelineOrchestrator(LifecycleAware):
    async def on_init(self):
        """加载config、注册metrics、预热API连接"""

    async def on_startup(self):
        """恢复上次未完成的dispatch、启动Descheduler定时器"""

    async def on_shutdown(self):
        """等待活跃dispatch ≤30s超时、保存state、释放锁"""
        # B152: graceful_shutdown——活跃dispatch超时后SIGKILL

    async def health_check(self) -> dict:
        """返回当前健康状态"""
        return {
            "status": "healthy"|"degraded"|"critical",
            "active_dispatches": len(self._active),
            "circuit_breaker": self.cb_state,
            "cost_today": self._cost_total,
            "dead_letter_count": len(self._dead_letters),
        }
```
