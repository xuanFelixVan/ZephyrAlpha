---
module_id: KE-2573
status: active
title: Bulkhead（舱壁隔离）
category: module_blueprint
---

# Bulkhead（舱壁隔离）

Bulkhead（舱壁隔离）

```python
class Bulkhead:
    """舱壁隔离——per-module 线程/连接池上限，防止一个模块耗尽全局资源"""
    _pools: dict[str, "ResourcePool"] = {}

    class ResourcePool:
        max_concurrent: int       # 最多并发操作数
        semaphore: asyncio.Semaphore

    def configure(self, module_id: str,
                  max_concurrent: int = 10,
                  max_db_connections: int = 5) -> None: ...

    async def acquire(self, module_id: str) -> AsyncContextManager:
        """获取该模块的资源——若已满则等待；超时则抛 ResourceExhaustedError"""
```
