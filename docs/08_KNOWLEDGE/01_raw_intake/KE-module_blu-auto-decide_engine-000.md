---
module_id: KE-module_blu-auto-decide_engine-000
title: Auto-Decide Engine（自动决策引擎）
category: module_blueprint
---

# Auto-Decide Engine（自动决策引擎）

Auto-Decide Engine（自动决策引擎）

```python
class AutoDecideEngine:
    """自动决策阈值——影响范围小的操作无需Owner审批。
    三维：影响模块数 × 费用（$） × 风险RPN
    """
    _thresholds: dict = {
        "impacted_modules": 3,      # 影响 ≤3 模块
        "cost_impact_usd": 0.10,    # 费用 ≤$0.10
        "risk_rpn": 50,             # RPN ≤50
    }

    async fn decide(self, operation: "Operation") -> DecideResult:
        """三阈值判断→AND 满足=自动执行|OR 不满足=送审批"""
        impact = await self._assess_impact(operation)
        if (impact.modules <= self._thresholds["impacted_modules"] and
            impact.cost <= self._thresholds["cost_impact_usd"] and
            impact.rpn <= self._thresholds["risk_rpn"]):
            log.info(f"🤖 {operation.id}: 自动执行——影响范围足够小无需Owner审批")
            return DecideResult(auto_approved=True)
        return DecideResult(needs_approval=True, reason=impact.summary())
```
