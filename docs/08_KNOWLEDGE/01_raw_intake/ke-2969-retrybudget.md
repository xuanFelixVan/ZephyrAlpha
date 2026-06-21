---
module_id: KE-2869
status: active
title: RetryBudget（重试配额）
category: module_blueprint
---

# RetryBudget（重试配额）

RetryBudget（重试配额）

```python
class RetryBudget:
    """重试风暴防护——全局重试配额，耗尽后拒绝重试，避免级联放大"""
    _budget_per_window: int = 100    # 每分钟最多 100 次重试
    _used_this_window: int = 0
    _window_start: float = 0.0

    async def can_retry(self) -> bool:
        """检查当前窗口内是否还有重试配额"""
        if time.monotonic() - self._window_start > 60.0:
            self._used_this_window = 0
            self._window_start = time.monotonic()
        return self._used_this_window < self._budget_per_window
```
