---
module_id: KE-module_blu-2_220_action_dry-run_simulator-000
title: 2.220 Action Dry-Run Simulator - action_dry_run_simulator.py (🆕 v0.20.0 - 盲点270
category: module_blueprint
---

# 2.220 Action Dry-Run Simulator - action_dry_run_simulator.py (🆕 v0.20.0 - 盲点270

2.220 Action Dry-Run Simulator - action_dry_run_simulator.py (🆕 v0.20.0 - 盲点270 — 高风险动作的预飞沙箱仿真)

**致命问题**：当FLE计划执行REPAIR_CONFIG/SCHEMA_MIGRATION/SELF_UPGRADE等高风险动作时，只有二阶冲击模型告诉你"理论上会影响到谁"。但"实际上会不会破坏系统"需要在实际执行前做沙箱仿真——把动作应用到系统状态的影子副本上，观察影子副本的变化。v0.15的Replay做的是事后复盘，不是事前仿真。
**对标**：Terraform Plan + AWS CloudFormation Change Set + K8s Dry-Run + GitHub Actions Simulation

```python
class ActionDryRunSimulator:
    async def simulate_action(self,
                                action: FLEAction) -> DryRunResult:
        # 1. Snapshot 当前系统状态的影子副本（shadow state）
        shadow = await self._create_shadow_state()
        # 2. 在shadow上应用action
        try:
            await self._apply_action_to_shadow(action, shadow)
        except Exception as e:
            return DryRunResult(passed=False, failure_stage="APPLICATION",
                detail=f"Action failed during simulation: {e}",
                recommendation="DO_NOT_EXECUTE_IN_PRODUCTION")
        # 3. 在shadow上运行所有Safety Gate
        gate_results = await self._run_all_gates_on_shadow(shadow)
        gate_failures = [g for g in gate_results if not g.passed]
        if gate_failures:
            return DryRunResult(passed=False, failure_stage="SAFETY_GATES",
                detail=f"{len(gate_failures)} gates would fail: "
                       f"{[g.gate_name for g in gate_failures]}.",
                recommendation="DO_NOT_EXECUTE—Gates would reject this action in production.")
        # 4. Post-action metric impact on shadow
        metric_deltas = await self._compute_metric_deltas(shadow)
        if any(d < -0.10 for d in metric_deltas.values()):  # 任一指标恶化10%+
            top_drops = sorted(metric_deltas.items(), key=lambda x: x[1])[:3]
            return DryRunResult(passed=False, failure_stage="METRIC_IMPACT",
                detail=f"Metrics would degrade: {[(k, f'{v:.1%}') for k,v in top_drops]}.",
                recommendation=f"Review expected impact. Consider: smaller blast radius, "
                               f"phased execution, or human oversight before execution.")
        return DryRunResult(passed=True,
            detail=f"Dry-run: all {len(gate_results)} gates pass, no metric degradation.",
            recommendation="SAFE_TO_EXECUTE")
```
