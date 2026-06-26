---
module_id: KE-2515
status: active
title: 9.2 Pre-flight Estimation
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 9.2 Pre-flight Estimation

9.2 Pre-flight Estimation

执行前预估成本，超出预算则拒绝或降级：

```python
class CostEstimator:
    async def estimate(self, prompt_tokens: int, model: str) -> CostEstimate:
        estimated_cost = prompt_tokens * MODEL_COST[model].input_per_1k / 1000
        if estimated_cost > self.session_budget_remaining:
            return CostEstimate(affordable=False, suggestion="downgrade_model")
        return CostEstimate(affordable=True, estimated_cost=estimated_cost)
```
