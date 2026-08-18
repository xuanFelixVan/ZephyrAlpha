# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.contracts.batch3_integration
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.capacity_assurance.contracts.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Batch3 集成层契约 — 14条 Pydantic v2 Schema（OTel/W3C/跨模块CT-1~4/DR/容量预测/语义缓存）."""

from pydantic import BaseModel, Field


class CtOt001(BaseModel):
    """OTel Span 格式（含 gen_ai.* 属性）."""

    span_id: str
    trace_id: str
    gen_ai_operation: str | None = None
    gen_ai_model: str | None = None
    gen_ai_token_count: int | None = None


class CtOt002(BaseModel):
    """W3C TraceContext 传播接口."""

    traceparent: str
    tracestate: str | None = None


class CtHs001(BaseModel):
    """ZephyrHealthScore 输出格式."""

    module_id: str
    health_score: float
    dimensions: dict[str, float] = Field(default_factory=dict)


class CtCt1(BaseModel):
    """capacity-assurance -> predict-router: 容量告警联动."""

    alert_level: str
    slo_id: str
    action: str = "switch_model"


class CtCt2(BaseModel):
    """capacity-assurance -> market-data-ingestor: 熔断传播."""

    kill_switch_active: bool
    dangerous_channels_paused: list[str] = Field(default_factory=list)


class CtCt3(BaseModel):
    """task-system -> capacity-assurance: Token 扣减."""

    task_id: str
    estimated_tokens: int
    allowed: bool = True
    remaining: int = 0


class CtCt4(BaseModel):
    """capacity-assurance -> iguana-rebalancer: 资本账户熔断."""

    account_id: str
    can_open_new: bool = True
    capacity_remaining: float = 1.0


class CtGd004(BaseModel):
    """双向模型切换逻辑."""

    primary_model: str
    fallback_model: str
    auto_recovery_condition: str


class CtCr001(BaseModel):
    """change_rate_limiter 渐进式切换."""

    target_rate: float
    ramp_up_minutes: int = 5
    max_concurrent_changes: int = 3


class CtAi001(BaseModel):
    """AI 行为预测维度 SLI 插桩."""

    prediction_horizon_hours: int = 24
    confidence_threshold: float = 0.8
    monitored_dimensions: list[str] = Field(default_factory=list)


class CtFb001(BaseModel):
    """预警->修复闭环 Playbook 格式."""

    alert_id: str
    playbook_steps: list[dict] = Field(default_factory=list)
    auto_fix_enabled: bool = False


class CtDr001(BaseModel):
    """DR 备份与恢复契约."""

    backup_type: str
    retention_days: int = 30
    recovery_point_objective_minutes: int = 5


class CtCp001(BaseModel):
    """容量预测模型输入/输出."""

    historical_window_days: int = 30
    predicted_growth_rate: float
    confidence_interval: float = 0.95


class CtSm001(BaseModel):
    """Sandbox 策略生命周期管理."""

    policy_id: str
    version: int = 1
    effective_from: str
    deprecated_after: str | None = None


BATCH3_CONTRACTS = {
    "CT-OT-001": CtOt001,
    "CT-OT-002": CtOt002,
    "CT-HS-001": CtHs001,
    "CT-CT1": CtCt1,
    "CT-CT2": CtCt2,
    "CT-CT3": CtCt3,
    "CT-CT4": CtCt4,
    "CT-GD-004": CtGd004,
    "CT-CR-001": CtCr001,
    "CT-AI-001": CtAi001,
    "CT-FB-001": CtFb001,
    "CT-DR-001": CtDr001,
    "CT-CP-001": CtCp001,
    "CT-SM-001": CtSm001,
}
