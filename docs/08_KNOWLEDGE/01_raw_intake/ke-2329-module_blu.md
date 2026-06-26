---
module_id: KE-2234--------17-000
status: active
title: §4.3 管线执行结果（17字段）
category: module_blueprint
ttl: permanent
---

# §4.3 管线执行结果（17字段）

§4.3 管线执行结果（17字段）

```python
class PipelineResult(BaseModel):
    task_id: str
    pipeline: str
    pipeline_version: str
    modules_executed: list[ModuleResult]
    overall_status: PipelineStatus    # SUCCESS/FAILURE/PARTIAL_FAILURE/CLAUDE_RESCUE/LOCKED
    needs_claude_rescue: bool
    rescue_reason: str
    ct_pipe_route: PipelineRouteDecision|None
    ct_pipe_warnings: list[str]
    artifact_manifest: PipelineArtifactManifest|None
    is_dry_run: bool
    cost_total_usd: float
    cost_records: list[CostRecord]
    impact_assessment: AIImpactAssessment|None
    fallback_plan: EmergencyFallbackPlan|None
    dead_letter: DeadLetterEntry|None
    circuit_breaker_state: dict[str, str]|None
```
