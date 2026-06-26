---
module_id: KE-2777
status: active
title: LoadShedder（负载脱落）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# LoadShedder（负载脱落）

LoadShedder（负载脱落）

```python
class LoadShedder:
    """负载脱落——超载时按请求优先级主动丢弃低优先级请求，不等队列满"""
    _overload_threshold: float = 0.80  # 全局负载 > 80% → 开始脱落

    async def admit(self, request: "Request") -> bool:
        """判断是否接纳请求。过载时：CRITICAL→接纳/HIGH→按概率接纳/LOW→拒绝"""
        global_load = await self._measure_global_load()
        if global_load < self._overload_threshold:
            return True
        return request.priority <= EventPriority.HIGH  # 仅CRITICAL+HIGH被接纳
```
