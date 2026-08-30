# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.contracts.batch2_governance
# [DOMAIN] D_GOVERNANCE
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

"""
Batch2 治理层契约 — 15条 Pydantic v2 Schema（Provenance/AI审计守卫/TechStackValidator/Governance Loop/Sandbox资源限制）.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: batch2_governance.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: CtPr001, CtPr002, CtPr003, CtAg001, CtAg002, CtVl001, CtVl0…
#   desc: 数据契约/异常/枚举声明共 15 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（15 类）
#   name_en: data classes
#   intro: CtPr001, CtPr002, CtPr003, CtAg001, CtAg002, CtVl001, CtVl002, CtVl003
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from pydantic import BaseModel, Field


class CtPr001(BaseModel):
    """ai_provenance 表写入契约."""

    module: str
    field: str
    old_value: str | None = None
    new_value: str | None = None
    author_agent: str
    audit_result: str


class CtPr002(BaseModel):
    """hash 链校验算法契约."""

    prev_hash: str | None = None
    curr_hash: str
    algorithm: str = "sha256"


class CtPr003(BaseModel):
    """Provenance 查询接口."""

    module_pattern: str
    limit: int = 100
    include_hashes: bool = False


class CtAg001(BaseModel):
    """AI 审计守卫规则引擎输入/输出."""

    rule_id: str
    check_type: str
    module_target: str
    result: str


class CtAg002(BaseModel):
    """审计结果格式."""

    audit_id: str
    passed: bool
    findings: list[str] = Field(default_factory=list)
    timestamp: str


class CtVl001(BaseModel):
    """TechStackValidator 校验结果格式."""

    component_id: str
    status: str
    violations: list[str] = Field(default_factory=list)


class CtVl002(BaseModel):
    """mypy 配置契约."""

    strict_mode: bool = True
    ignore_missing_imports: bool = False
    warn_unused_configs: bool = True


class CtVl003(BaseModel):
    """ruff 规则集契约."""

    select_rules: list[str] = Field(default_factory=lambda: ["E", "F", "I", "N", "W"])
    line_length: int = 120


class CtVl004(BaseModel):
    """bandit 规则集契约."""

    severity_filter: list[str] = Field(default_factory=lambda: ["high", "medium"])
    exclude_dirs: list[str] = Field(default_factory=lambda: [".git", "__pycache__"])


class CtGv001(BaseModel):
    """治理闭环 EMA 参数."""

    alpha: float = 0.1
    window_size: int = 60
    threshold_multiplier: float = 2.0


class CtGv002(BaseModel):
    """阈值/持续时间契约."""

    metric_id: str
    upper_bound: float
    lower_bound: float
    sustain_duration_seconds: int = 30


class CtSb002(BaseModel):
    """Sandbox 资源限制规范."""

    max_memory_bytes: int = 536870912
    max_file_descriptors: int = 64
    network_access: bool = False


class CtSb003(BaseModel):
    """Sandbox 超时策略."""

    execution_timeout_seconds: int = 60
    kill_signal: str = "SIGKILL"
    grace_period_seconds: int = 5


class CtMb001(BaseModel):
    """MetricsWriteBuffer 批量写入规格."""

    batch_size: int = 100
    flush_interval_seconds: int = 5
    max_buffer_size: int = 10000


class CtCh001(BaseModel):
    """capacity_metrics_hourly 聚合策略."""

    aggregation_window: str = "1h"
    aggregation_funcs: list[str] = Field(default_factory=lambda: ["avg", "min", "max", "p99"])


BATCH2_CONTRACTS = {
    "CT-PR-001": CtPr001,
    "CT-PR-002": CtPr002,
    "CT-PR-003": CtPr003,
    "CT-AG-001": CtAg001,
    "CT-AG-002": CtAg002,
    "CT-VL-001": CtVl001,
    "CT-VL-002": CtVl002,
    "CT-VL-003": CtVl003,
    "CT-VL-004": CtVl004,
    "CT-GV-001": CtGv001,
    "CT-GV-002": CtGv002,
    "CT-SB-002": CtSb002,
    "CT-SB-003": CtSb003,
    "CT-MB-001": CtMb001,
    "CT-CH-001": CtCh001,
}
