# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.contracts.batch1_infra
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

"""Batch1 基础设施层契约 — 15条 Pydantic v2 Schema（SLO/Error Budget/Token Budget/Kill Switch/Sandbox/Graceful Degradation）."""

from pydantic import BaseModel, Field


class CtSlo001(BaseModel):
    """capacity_slo.yaml Schema 定义."""

    slo_id: str
    metric: str
    target: float
    window: str
    severity: str


class CtSlo002(BaseModel):
    """SLO measurement window 定义."""

    fast_cycle: dict = Field(default_factory=lambda: {"1h": 14.4, "6h": 6.0})
    medium_cycle: dict = Field(default_factory=lambda: {"24h": 3.0, "7d": 1.0})
    slow_cycle: dict = Field(default_factory=lambda: {"28d": 1.0})


class CtEb001(BaseModel):
    """Error Budget 计算公式."""

    slo_id: str
    budget_total: float
    budget_consumed: float
    budget_remaining: float
    burn_rate: float = 0.0


class CtEb002(BaseModel):
    """Burn Rate 阈值契约."""

    threshold_1h: float = 14.4
    threshold_6h: float = 6.0
    threshold_3d: float = 3.0
    threshold_30d: float = 1.0


class CtEb003(BaseModel):
    """五级响应动作契约."""

    tier: str
    threshold: float
    actions: list[str] = Field(default_factory=list)


class CtTb001(BaseModel):
    """Token Budget 四级定义."""

    level: str
    dimension: str
    default_limit: int
    unit: str = "tokens"


class CtTb002(BaseModel):
    """Pre-flight 预估接口."""

    estimated_tokens: int
    actual_tokens: int | None = None
    accuracy_ratio: float | None = None


class CtKs001(BaseModel):
    """Kill Switch 信号格式."""

    active: bool = False
    mode: str = "normal"
    triggered_by: str | None = None
    triggered_at: str | None = None


class CtKs002(BaseModel):
    """熔断状态切换契约."""

    from_state: str
    to_state: str
    reason: str
    timestamp: str


class CtSb001(BaseModel):
    """Sandbox 子进程隔离规范."""

    max_memory_mb: int = 512
    max_cpu_seconds: int = 30
    allowed_syscalls: list[str] = Field(default_factory=list)


class CtGd001(BaseModel):
    """降级链 YAML Schema."""

    chain_id: str
    levels: list[dict] = Field(default_factory=list)


class CtGd002(BaseModel):
    """模型路由接口."""

    current_model: str
    fallback_model: str
    switch_threshold: float


class CtGd003(BaseModel):
    """输出截断策略."""

    max_output_tokens: int = 4096
    truncation_strategy: str = "semantic_boundary"


class CtSc001(BaseModel):
    """语义缓存键格式."""

    cache_key: str
    hash_algorithm: str = "sha256"
    ttl_seconds: int = 3600


class CtSc002(BaseModel):
    """ChromaDB 向量存储契约."""

    collection_name: str
    dimension: int = 1536
    distance_metric: str = "cosine"


BATCH1_CONTRACTS = {
    "CT-SLO-001": CtSlo001,
    "CT-SLO-002": CtSlo002,
    "CT-EB-001": CtEb001,
    "CT-EB-002": CtEb002,
    "CT-EB-003": CtEb003,
    "CT-TB-001": CtTb001,
    "CT-TB-002": CtTb002,
    "CT-KS-001": CtKs001,
    "CT-KS-002": CtKs002,
    "CT-SB-001": CtSb001,
    "CT-GD-001": CtGd001,
    "CT-GD-002": CtGd002,
    "CT-GD-003": CtGd003,
    "CT-SC-001": CtSc001,
    "CT-SC-002": CtSc002,
}
