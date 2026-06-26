---
module_id: KE-2477---------nonconvergencehand-000
status: active
title: 8.3 不收敛处置协议（NonConvergenceHandler）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 8.3 不收敛处置协议（NonConvergenceHandler）

8.3 不收敛处置协议（NonConvergenceHandler）

> **这是防止 Doom Loop 的关键机制。** 不是"一直修到通过"，而是"尽力修 N 次，修不了的诚实承认"。

```python
class NonConvergenceHandler:
    def handle_stuck_dimension(self, dim_result: DimensionResult) -> EscalationReport:
        """
        维度超过 max_total_passes 仍未收敛：
          1. 不卡住——降级为 YELLOW
          2. 生成"人工裁决清单"
          3. 继续下一维度
          4. 全部维度完成后，Owner 处理 YELLOW 清单
          5. Owner 决策后重新触发审计
        """
        unresolved = [
            issue for issue in dim_result.issues
            if not issue.fixed and issue.fix_level == FixLevel.L3
        ]

        return EscalationReport(
            dimension=dim_result.dim_id,
            total_passes=dim_result.total_passes,
            unresolved_count=len(unresolved),
            human_decision_required=[self._format_for_owner(i) for i in unresolved],
            recommendation="请 Owner 逐条裁决后重新运行审计"
        )
```
