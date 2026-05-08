---
module_id: KE-module_blu-1__kill_switch______b95-000
title: 1. Kill Switch 前置检查（B95）
category: module_blueprint
---

# 1. Kill Switch 前置检查（B95）

1. Kill Switch 前置检查（B95）

```python
class KillSwitchStatus(BaseModel):
    active: bool
    reason: str
    activated_by: str
    activated_at: str

def _check_kill_switch(self) -> bool:
    """dispatch() 前检查——如果 Kill Switch 开启则拒绝"""
    ks = self.capacity_assurance.get_kill_switch()
    if ks.active:
        logger.warning(f"Kill Switch ACTIVE: {ks.reason}")
        return False
    return True
```
