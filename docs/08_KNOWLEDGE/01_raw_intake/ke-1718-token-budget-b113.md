---
module_id: KE-1628----b113-000
status: active
title: 2. Token Budget 协调（B113）
category: module_blueprint
---

# 2. Token Budget 协调（B113）

2. Token Budget 协调（B113）

```python
class TokenBudget(BaseModel):
    limit: int = 200000              # 200K tokens 每日限额
    consumed: int = 0
    warn_threshold: float = 0.80    # 80% 告警
    block_threshold: float = 1.00   # 100% 阻止

def _check_token_budget(self, estimated_tokens: int) -> tuple[bool, str]:
    """跨dispatch Token预算协调"""
    budget = self._token_budget
    
    if budget.consumed + estimated_tokens > budget.limit * budget.block_threshold:
        return False, f"Token预算耗尽：{budget.consumed}/{budget.limit}"
    
    if budget.consumed + estimated_tokens > budget.limit * budget.warn_threshold:
        # 发出WARNING→仍允许执行但通知Owner
        self._notify_budget_warning(budget.consumed + estimated_tokens, budget.limit)
    
    budget.consumed += estimated_tokens
    return True, ""
```
