---
module_id: KE-2716
status: active
title: === 故障正常化漂移 Drift Into Failure ===
category: module_blueprint
---

# === 故障正常化漂移 Drift Into Failure ===

=== 故障正常化漂移 Drift Into Failure ===

class DriftIntoFailurePattern(BaseModel):
    """故障正常化漂移模式检测（B455）——对标Diane Vaughan/Vaughan/Sidney Dekker"""
    model_config = ConfigDict(frozen=True)

    pattern_id: UUID = Field(default_factory=uuid4)
    detected_at: datetime = Field(default_factory=datetime.utcnow)

    metric_name: str
    baseline_value: float
    current_value: float
    drift_rate_per_month: float = 0.0

    within_slo: bool = True
    hidden_by_error_budget: bool = False

    normal_boundary_shifted: bool = False
    normalization_start_date: Optional[datetime] = None
    normalization_duration_days: int = 0

    is_dangerous_drift: bool = False
    requires_intervention: bool = False
    intervention_type: Literal["none", "reset_baseline", "reduce_budget", "freeze_changes", "escalate"] = "none"


class AnomalyNormalizationLog(BaseModel):
    """异常正常化日志（B455）——记录被"SLO预算内"掩盖的异常"""
    model_config = ConfigDict(frozen=True)

    log_id: UUID = Field(default_factory=uuid4)

    anomaly_description: str
    first_observed: datetime
    occurrence_count: int = 1
    severity_at_first: Literal["critical", "high", "medium", "low"]
    severity_now_accepted_as: Literal["normal", "low", "medium"]

    was_ever_escalated: bool = False
    acceptance_rationale: str = ""
    ratchet_effect_detected: bool = False
