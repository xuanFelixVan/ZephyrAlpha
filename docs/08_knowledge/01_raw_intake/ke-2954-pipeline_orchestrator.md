---
module_id: KE-2854
status: active
title: === Pipeline-Orchestrator 双向状态漂移 ===
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# === Pipeline-Orchestrator 双向状态漂移 ===

=== Pipeline-Orchestrator 双向状态漂移 ===

class OrchestratorPipelineStateDrift(BaseModel):
    """Pipeline与Orchestrator双向状态漂移检测（B464）"""
    model_config = ConfigDict(frozen=True)

    drift_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    pipeline_task_states: dict[str, str] = Field(default_factory=dict)
    orchestrator_task_states: dict[str, str] = Field(default_factory=dict)
    divergent_tasks: list[dict] = Field(default_factory=list)

    divergence_count: int = 0
    divergence_severity: Literal["cosmetic", "semantic", "conflicting", "dangerous"]

    automatic_reconciliation_possible: bool = True
    reconciliation_strategy: str = ""

    drift_prevention_in_place: bool = False
    sync_interval_s: float = 3600.0
