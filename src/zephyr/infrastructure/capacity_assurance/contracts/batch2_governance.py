# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.contracts.batch2_governance
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.infrastructure.capacity_assurance.contracts.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_batch2_governance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Batch2 治理层契约 — 15条 Pydantic v2 Schema（Provenance/AI审计守卫/TechStackValidator/Governance Loop/Sandbox资源限制）."""

from pydantic import BaseModel, Field


class CT_PR_001(BaseModel):
    """ai_provenance 表写入契约."""

    module: str
    field: str
    old_value: str | None = None
    new_value: str | None = None
    author_agent: str
    audit_result: str


class CT_PR_002(BaseModel):
    """hash 链校验算法契约."""

    prev_hash: str | None = None
    curr_hash: str
    algorithm: str = "sha256"


class CT_PR_003(BaseModel):
    """Provenance 查询接口."""

    module_pattern: str
    limit: int = 100
    include_hashes: bool = False


class CT_AG_001(BaseModel):
    """AI 审计守卫规则引擎输入/输出."""

    rule_id: str
    check_type: str
    module_target: str
    result: str


class CT_AG_002(BaseModel):
    """审计结果格式."""

    audit_id: str
    passed: bool
    findings: list[str] = Field(default_factory=list)
    timestamp: str


class CT_VL_001(BaseModel):
    """TechStackValidator 校验结果格式."""

    component_id: str
    status: str
    violations: list[str] = Field(default_factory=list)


class CT_VL_002(BaseModel):
    """mypy 配置契约."""

    strict_mode: bool = True
    ignore_missing_imports: bool = False
    warn_unused_configs: bool = True


class CT_VL_003(BaseModel):
    """ruff 规则集契约."""

    select_rules: list[str] = Field(default_factory=lambda: ["E", "F", "I", "N", "W"])
    line_length: int = 120


class CT_VL_004(BaseModel):
    """bandit 规则集契约."""

    severity_filter: list[str] = Field(default_factory=lambda: ["high", "medium"])
    exclude_dirs: list[str] = Field(default_factory=lambda: [".git", "__pycache__"])


class CT_GV_001(BaseModel):
    """治理闭环 EMA 参数."""

    alpha: float = 0.1
    window_size: int = 60
    threshold_multiplier: float = 2.0


class CT_GV_002(BaseModel):
    """阈值/持续时间契约."""

    metric_id: str
    upper_bound: float
    lower_bound: float
    sustain_duration_seconds: int = 30


class CT_SB_002(BaseModel):
    """Sandbox 资源限制规范."""

    max_memory_bytes: int = 536870912
    max_file_descriptors: int = 64
    network_access: bool = False


class CT_SB_003(BaseModel):
    """Sandbox 超时策略."""

    execution_timeout_seconds: int = 60
    kill_signal: str = "SIGKILL"
    grace_period_seconds: int = 5


class CT_MB_001(BaseModel):
    """MetricsWriteBuffer 批量写入规格."""

    batch_size: int = 100
    flush_interval_seconds: int = 5
    max_buffer_size: int = 10000


class CT_CH_001(BaseModel):
    """capacity_metrics_hourly 聚合策略."""

    aggregation_window: str = "1h"
    aggregation_funcs: list[str] = Field(default_factory=lambda: ["avg", "min", "max", "p99"])


BATCH2_CONTRACTS = {
    "CT-PR-001": CT_PR_001,
    "CT-PR-002": CT_PR_002,
    "CT-PR-003": CT_PR_003,
    "CT-AG-001": CT_AG_001,
    "CT-AG-002": CT_AG_002,
    "CT-VL-001": CT_VL_001,
    "CT-VL-002": CT_VL_002,
    "CT-VL-003": CT_VL_003,
    "CT-VL-004": CT_VL_004,
    "CT-GV-001": CT_GV_001,
    "CT-GV-002": CT_GV_002,
    "CT-SB-002": CT_SB_002,
    "CT-SB-003": CT_SB_003,
    "CT-MB-001": CT_MB_001,
    "CT-CH-001": CT_CH_001,
}
