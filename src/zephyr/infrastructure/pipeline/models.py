# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] zephyr.infrastructure.pipeline.models
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.schema.schemas
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_models | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Pipeline 数据模型
=================
依据：MOD-TASK_SYSTEM §3.2.2 + GOV-AI-002 v2.0.0 模型路由策略
"""

from __future__ import annotations

import ast
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from zephyr.shared.schema.schemas import BASE_CONFIG
from zephyr.shared.utils.time_utils import now_utc

__all__ = [
    "AFFINITY_CONSTRAINTS",
    "A_DAG",
    "B_DAG",
    "M_MODULES",
    "M_MODULE_SPECS",
    "ABExperimentRoute",
    "AIImpactAssessment",
    "AffinityWeight",
    "ArtifactClassification",
    "ArtifactType",
    "CircuitBreakerState",
    "ClaudeRescueTrigger",
    "CostRecord",
    "DeadLetterEntry",
    "EmergencyFallbackPlan",
    "ExecutionMode",
    "ExperimentVariant",
    "GenericModuleOutput",
    "M1ParseOutput",
    "M3GenerateOutput",
    "M6DiffOutput",
    "M7ReviewOutput",
    "M8ComplianceOutput",
    "M9RiskOutput",
    "M10ReportOutput",
    "M11GatingOutput",
    "ModelCollapseAlert",
    "ModelConfidence",
    "ModelVersionInfo",
    "ModuleInput",
    "ModuleResult",
    "NightShiftAmbiguityLogEntry",
    "PipelineAffinityConstraint",
    "PipelineArtifact",
    "PipelineArtifactManifest",
    "PipelineDAG",
    "PipelineLineageChain",
    "PipelineLineageEntry",
    "PipelineOrchestratorConfig",
    "PipelineResult",
    "PipelineRouteDecision",
    "PipelineStage",
    "PipelineStatus",
    "PreemptionRecord",
    "StageContext",
    "StageOnFailure",
    "validate_module_output",
]


class PipelineStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    PARTIAL_FAILURE = "partial_failure"
    FAILURE = "failure"
    CLAUDE_RESCUE = "claude_rescue"
    LOCKED = "locked"
    G6_BLOCKED = "g6_blocked"


class ModuleStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"


class ExecutionMode(str, Enum):
    """三层执行模式——L1(Trae)/L2(Local)/L3(API)"""

    TRAE = "trae"
    LOCAL = "local"
    API = "api"


class ModuleResult(BaseModel):
    """单模块执行结果"""

    model_config = BASE_CONFIG

    module_id: str = Field(..., pattern=r"^M(1[0-1]|[1-9])$")
    pipeline: str = Field(..., pattern=r"^[ABC]$")
    model: str = Field(...)
    status: ModuleStatus = ModuleStatus.PENDING
    output: dict[str, Any] = {}
    errors: list[str] = []
    tokens_used: int = 0
    duration_ms: int = 0
    started_at: str | None = None
    finished_at: str | None = None
    fallback_from: str | None = Field(
        default=None,
        description="如果此模块经过模型降级，记录原始请求的模型名",
    )
    blind_review_role: str | None = Field(
        default=None,
        description="双盲审查角色：'generator' | 'reviewer'",
    )
    confidence: ModelConfidence | None = Field(
        default=None,
        description="模型输出置信度——B158",
    )


class PipelineRouteDecision(BaseModel):
    """CT-PIPE-ORC-001 路由输出（PipelineNode 子集）。"""

    model_config = BASE_CONFIG

    node_id: str = Field(..., pattern=r"^M(1[0-1]|[1-9])$")
    execution_model: str = Field(min_length=1)
    sandbox_profile: str = Field(min_length=1)
    gate_profile: str = Field(min_length=1)
    rationale: str = Field(default="", description="路由依据摘要")


class PipelineResult(BaseModel):
    """管线执行结果"""

    model_config = BASE_CONFIG

    task_id: str
    pipeline: str
    execution_mode: ExecutionMode = Field(default=ExecutionMode.TRAE, description="三层执行模式")
    modules_executed: list[ModuleResult] = Field(default_factory=list)
    overall_status: PipelineStatus = PipelineStatus.PENDING
    needs_claude_rescue: bool = False
    rescue_reason: str = ""
    started_at: str = Field(default_factory=lambda: now_utc().isoformat())
    finished_at: str | None = None
    ct_pipe_route: PipelineRouteDecision | None = None
    ct_pipe_warnings: list[str] = Field(default_factory=list)
    artifact_manifest: PipelineArtifactManifest | None = None
    is_dry_run: bool = Field(default=False, description="dry_run 模式下产出")
    lineage: PipelineLineageChain | None = Field(
        default=None,
        description="数据血缘链——SOC2 CC7.2 审计证据",
    )
    model_collapse: ModelCollapseAlert | None = Field(
        default=None,
        description="模型崩塌检测结果——B132",
    )
    pipeline_version: str = Field(
        default="0.9.0",
        description="执行此结果的 Pipeline 版本——B166；见模块文档「模拟边界」",
    )
    cost_total_usd: float = Field(default=0.0, description="总成本（USD）——B161")
    cost_records: list[CostRecord] = Field(default_factory=list, description="逐模块成本明细——B161")
    impact_assessment: AIImpactAssessment | None = Field(
        default=None,
        description="AI 影响评估结果——B157",
    )
    fallback_plan: EmergencyFallbackPlan | None = Field(
        default=None,
        description="降级计划（三模全失败时）——B147",
    )
    dead_letter: DeadLetterEntry | None = Field(
        default=None,
        description="死信队列条目（永久失败时）——B169",
    )
    circuit_breaker_state: CircuitBreakerState | None = Field(
        default=None,
        description="断路器状态——B151",
    )
    bridge_result: dict | None = Field(
        default=None,
        description="Pipeline->AgentOrchestrator 桥接结果——B34+B36",
    )
    skill_injection: dict | None = Field(
        default=None, description="Agent Spec Skill 注入结果——domain/role skill 上下文"
    )
    night_shift_log: list[NightShiftAmbiguityLogEntry] = Field(
        default_factory=list, description="夜班登记表——API 夜间不确定条目"
    )


class ClaudeRescueTrigger(BaseModel):
    """Claude 特种救援触发记录——GOV-AI-002 §三"""

    model_config = BASE_CONFIG

    triggered: bool = False
    reason: str = ""
    deepseek_failure_count: int = 0
    glm_rejection_count: int = 0
    is_owner_critical: bool = False
    has_security_tag: bool = False
    is_experimental: bool = False


class ModelCollapseAlert(BaseModel):
    """模型崩塌检测——三模同质化预警 + 少数派报告。

    当 M3(DeepSeek)+M7(GLM)+Claude 三个模型对同一任务产出相同结论时，
    触发模型崩塌预警——可能是三个模型在同一训练集上趋同，
    或 prompt 设计导致缺乏对抗性。
    """

    model_config = BASE_CONFIG

    detected: bool = False
    severity: str = Field(default="info", description="info | warn | critical")
    affected_modules: list[str] = Field(default_factory=list)
    homogeneous_verdict: str | None = Field(default=None)
    detail: str = Field(default="", description="崩塌详情描述")
    minority_report: str | None = Field(
        default=None,
        description="当两模一致(如M3+M7)但第三模不同时，此字段记录少数派模型的结论摘要",
    )


class NightShiftAmbiguityLogEntry(BaseModel):
    """夜班登记表条目——API 夜间执行遇到第三种选择时登记

    API 遇到非黑非白的第三种选择时，不做强行判定，
    登记上下文和可选方案，留待人类白天裁定。
    """

    model_config = BASE_CONFIG

    id: str = Field(..., description="NSL-{sequence} 编号")
    timestamp: str = Field(default_factory=lambda: now_utc().isoformat(), description="检测时间")
    task_id: str = Field(..., description="关联任务ID")
    module: str = Field(..., description="触发模块节点 Mx")
    context: str = Field(..., description="不确定的上下文描述")
    options: list[dict[str, str]] = Field(default_factory=list, description="可选方案列表 [{label, description}]")
    auto_decision: str = Field(default="C", description="API 自动选择的最保守方案")
    requires_human: bool = Field(default=True, description="需要人类裁定")
    human_decision: str | None = Field(default=None, description="人类裁定结果")
    human_timestamp: str | None = Field(default=None, description="人类裁定时间")
    human_notes: str | None = Field(default=None, description="人类备注")


# ============================================================================
# v0.9.0 第九轮审计——运维韧性 & 可观测性 数据模型
# ============================================================================


class CircuitBreakerState(str, Enum):
    """断路器三态——对标 Netflix Hystrix。"""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class ModelVersionInfo(BaseModel):
    """模型版本锁定信息——对标 Langfuse model registry。"""

    model_config = BASE_CONFIG
    model_name: str
    version: str
    api_endpoint: str = ""
    context_limit_tokens: int = 128_000
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0


class ModelConfidence(BaseModel):
    """模型输出置信度——B158。"""

    model_config = BASE_CONFIG
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    source: str = Field(default="", description="logprob | self_eval | ensemble")
    calibration_note: str = Field(default="")


class AIImpactAssessment(BaseModel):
    """AI 影响评估——NIST AI RMF MAP 函数。"""

    model_config = BASE_CONFIG
    risk_tier: str = Field(default="low", description="low | medium | high | critical")
    affected_stakeholders: list[str] = Field(default_factory=list)
    data_sensitivity_level: str = Field(default="internal")
    autonomy_level: str = Field(default="advisory", description="advisory | assistive | autonomous")
    human_review_required: bool = False


class CostRecord(BaseModel):
    """LLM 调用成本记录——B161。"""

    model_config = BASE_CONFIG
    model: str
    tokens_input: int = 0
    tokens_output: int = 0
    cost_usd: float = 0.0
    estimated: bool = Field(default=True, description="模拟估算或实际API返回")


class DeadLetterEntry(BaseModel):
    """死信队列条目——B169。"""

    model_config = BASE_CONFIG
    task_id: str
    failed_at: str = Field(default_factory=lambda: now_utc().isoformat())
    failure_reason: str = ""
    retry_count: int = 0
    last_error: str = ""


class EmergencyFallbackPlan(BaseModel):
    """三模全失败降级计划——B147。"""

    model_config = BASE_CONFIG
    activated: bool = False
    all_models_failed: list[str] = Field(default_factory=list)
    recommended_action: str = Field(
        default="WAIT_AND_RETRY", description="WAIT_AND_RETRY | ESCALATE_TO_HUMAN | USE_CACHED | ABORT"
    )
    wait_before_retry_s: int = 300
    fallback_routes: list[str] = Field(default_factory=list)


class ExperimentVariant(str, Enum):
    """A/B 实验变体——B159。"""

    CONTROL = "control"
    TREATMENT = "treatment"


class ABExperimentRoute(BaseModel):
    """A/B 实验路由决策——B159。"""

    model_config = BASE_CONFIG
    experiment_id: str
    variant: ExperimentVariant
    routing_hash: str = Field(default="", description="hash(task_id) %% 100")
    control_route: str = Field(default="")
    treatment_route: str = Field(default="")


class PreemptionRecord(BaseModel):
    """优先级抢占记录——对标 K8s Priority Preemption。

    P0/P1 任务可抢占 P3 任务。被抢占的任务记录在此，
    P0 完成后可 resume。
    """

    model_config = BASE_CONFIG

    preempted_task_id: str
    preempted_by_task_id: str
    preempted_priority: str
    preempted_at: str = Field(default_factory=lambda: now_utc().isoformat())
    resumed_at: str | None = None
    state_snapshot: dict[str, object] = Field(default_factory=dict)


class PipelineOrchestratorConfig(BaseModel):
    """管线编排器配置"""

    model_config = BASE_CONFIG

    max_retries: int = 3
    claude_rescue_threshold: int = 3
    glm_rejection_threshold: int = 2
    default_timeout_s: int = 300
    enable_parallel_modules: bool = False
    health_degraded_threshold: int = 20
    health_critical_failure_ratio: float = 0.05
    periodic_profile_interval_s: float = 3600.0
    auto_profile_on_startup: bool = False

    circuit_breaker_enabled: bool = Field(default=True, description="B151 断路器")
    g6_enabled: bool = Field(default=True, description="G6 蓝图合规门禁（测试模式可关闭）")
    cache_enabled: bool = Field(default=False, description="B154 响应缓存")
    cache_ttl_s: int = Field(default=3600, description="缓存 TTL（秒）")
    rate_limit_per_model: dict[str, float] = Field(
        default_factory=lambda: {"deepseek": 10.0, "glm": 20.0, "claude": 5.0},
        description="B162 每模型每秒最大调用数",
    )
    model_versions: list[ModelVersionInfo] = Field(
        default_factory=lambda: [
            ModelVersionInfo(
                model_name="deepseek",
                version="v4-pro",
                context_limit_tokens=128000,
                cost_per_1k_input=0.00174,
                cost_per_1k_output=0.00348,
            ),
            ModelVersionInfo(
                model_name="glm",
                version="5.1",
                context_limit_tokens=128000,
                cost_per_1k_input=0.0,
                cost_per_1k_output=0.0,
            ),
            ModelVersionInfo(
                model_name="claude",
                version="opus-4.7",
                context_limit_tokens=200000,
                cost_per_1k_input=0.005,
                cost_per_1k_output=0.025,
            ),
        ],
        description="B150 模型版本锁定 + B170 上下文窗口限制",
    )
    log_buffer_max: int = Field(default=2000, description="B148 日志缓冲区上限")
    latency_samples_max: int = Field(default=100, description="B148 延迟样本上限")
    human_detection_method: str = Field(
        default="heartbeat", description="人类在场检测方式: heartbeat | manual_switch | time_window"
    )
    working_hours_start: int = Field(default=9, ge=0, le=23, description="工作时间开始（时）")
    working_hours_end: int = Field(default=21, ge=0, le=23, description="工作时间结束（时）")
    local_model_always_on: bool = Field(default=True, description="本地模型 24/7 常驻运行")
    accuracy_tracking_enabled: bool = Field(default=False, description="B155 准确率追踪")


# ============================================================================
# M1-M11 模块静态规格——GOV-AI-002 决策树的具体化
# ============================================================================

M_MODULE_SPECS: dict[str, dict[str, str]] = {
    "M1": {"pipeline": "A", "model": "deepseek", "role": "任务卡解析->结构化执行计划"},
    "M2": {"pipeline": "A", "model": "deepseek", "role": "上下文装配->调用 context-engine"},
    "M3": {"pipeline": "A", "model": "deepseek", "role": "代码/文档生成——核心生产"},
    "M4": {"pipeline": "A", "model": "deepseek", "role": "格式校验"},
    "M5": {"pipeline": "A", "model": "glm", "role": "产物打包"},
    "M6": {"pipeline": "B", "model": "deepseek", "role": "差异检测——产出 vs 期望"},
    "M7": {"pipeline": "B", "model": "glm", "role": "深度审查——逐个文件逻辑/合规"},
    "M8": {"pipeline": "B", "model": "deepseek", "role": "标准合规——PS/GOV/KB决策记录"},
    "M9": {"pipeline": "B", "model": "deepseek", "role": "风险评估——OWASP LLM Top 10"},
    "M10": {"pipeline": "B", "model": "deepseek", "role": "审计报告->Finding 格式"},
    "M11": {"pipeline": "B", "model": "deepseek", "role": "门禁裁决——G5/G6"},
}

M_MODULES: list[str] = sorted(M_MODULE_SPECS.keys(), key=lambda x: int(x[1:]))

# ============================================================================
# Pipeline DAG 拓扑——对标 GitHub Actions jobs.<id>.needs + K8s DAG 工作流
# ============================================================================


class StageOnFailure(str, Enum):
    """Stage 失败的处置策略。"""

    ABORT = "abort"
    SKIP = "skip"
    RETRY = "retry"
    CLAUDE_RESCUE = "claude_rescue"


class PipelineStage(BaseModel):
    """Pipeline 中的一个可执行阶段——DAG 节点。

    对标 GitHub Actions `jobs.<id>`:
      - stage_id: 唯一标识（如 "parse", "generate", "audit"）
      - module_id: 绑定的 M 节点
      - depends_on: 前置依赖（声明式 DAG）
      - skip_condition: 条件跳过
      - on_failure: 失败策略
    """

    stage_id: str
    module_id: str = Field(min_length=2, max_length=3, pattern=r"^M\d{1,2}$")
    depends_on: list[str] = Field(default_factory=list)
    skip_condition: str | None = Field(
        default=None,
        description="Python 表达式字符串——为 True 时跳过此阶段。可引用 ctx.metadata。",
    )
    on_failure: StageOnFailure = StageOnFailure.ABORT
    retry_max: int = Field(default=0, ge=0, le=3)
    timeout_seconds: int | None = Field(default=None, ge=10)
    parallel_group: str | None = Field(
        default=None,
        description="同一 parallel_group 的 stage 可以并行执行。",
    )

    model_config = ConfigDict(use_enum_values=True)


class PipelineDAG(BaseModel):
    """声明式 Pipeline DAG 拓扑——替代硬编码线性序列。

    使用示例（A区生产管线）:
        PipelineDAG(
            dag_id="production-A",
            stages=[
                PipelineStage(stage_id="parse",    module_id="M1", depends_on=[]),
                PipelineStage(stage_id="assemble", module_id="M2", depends_on=["parse"]),
                PipelineStage(stage_id="generate", module_id="M3", depends_on=["assemble"],
                              on_failure=StageOnFailure.RETRY, retry_max=1),
                PipelineStage(stage_id="validate", module_id="M4", depends_on=["generate"]),
                PipelineStage(stage_id="package",  module_id="M5", depends_on=["validate"],
                              skip_condition="all(m.status == 'ok' for m in ctx.results[-1:])"),
            ],
        )
    """

    dag_id: str
    stages: list[PipelineStage] = Field(min_length=1)
    entry_stages: list[str] | None = Field(
        default=None,
        description="入口 stage 列表——None 时自动计算（depends_on 为空的 stage）",
    )
    max_parallel: int = Field(default=2, ge=1, le=8)

    @model_validator(mode="after")
    def _validate_dag(self) -> PipelineDAG:
        stage_ids = {s.stage_id for s in self.stages}
        for s in self.stages:
            for dep in s.depends_on:
                if dep not in stage_ids:
                    raise ValueError(f"Stage {s.stage_id} depends on unknown stage {dep!r}")
        return self

    def resolve_entry_stages(self) -> list[str]:
        if self.entry_stages:
            return self.entry_stages
        return [s.stage_id for s in self.stages if not s.depends_on]

    def resolve_execution_order(self) -> list[list[str]]:
        """拓扑排序->分层并行执行计划。

        Returns
        -------
        list[list[str]]
            每层是一组可并行执行的 stage_id。
        """
        in_degree: dict[str, int] = {s.stage_id: len(s.depends_on) for s in self.stages}
        reverse_deps: dict[str, list[str]] = {s.stage_id: [] for s in self.stages}
        for s in self.stages:
            for dep in s.depends_on:
                reverse_deps[dep].append(s.stage_id)

        order: list[list[str]] = []
        ready = [sid for sid, deg in in_degree.items() if deg == 0]
        while ready:
            order.append(sorted(ready))
            next_ready: list[str] = []
            for sid in ready:
                for child in reverse_deps[sid]:
                    in_degree[child] -= 1
                    if in_degree[child] == 0:
                        next_ready.append(child)
            ready = next_ready

        remaining = [sid for sid, deg in in_degree.items() if deg > 0]
        if remaining:
            raise ValueError(f"Pipeline DAG {self.dag_id!r}: cycle detected involving {remaining}")
        return order

    def get_stage(self, stage_id: str) -> PipelineStage | None:
        for s in self.stages:
            if s.stage_id == stage_id:
                return s
        return None


class StageContext(BaseModel):
    """Stage 执行上下文——在 Stage 间传递。

    每个 Stage 完成后，其 result 追加到 results 列表。
    skip_condition 表达式可引用 ctx.results, ctx.metadata。
    """

    dag: PipelineDAG
    results: list[ModuleResult] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)
    aborted: bool = False

    def evaluate_skip(self, condition: str) -> bool:
        # 5.17.6 修复：eval() 可经 ctx.__class__.__mro__ 逃逸 __builtins__ 限制->RCE
        # 改为 AST 预校验拒绝 dunder 访问，再安全 eval
        if not condition or not condition.strip():
            return False
        try:
            tree = ast.parse(condition, mode="eval")
        except SyntaxError:
            return False
        # 拒绝任何 dunder 属性/名称访问（阻断 __class__/__mro__/__subclasses__/__globals__ 逃逸链）
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
                return False
            if isinstance(node, ast.Name) and node.id.startswith("__"):
                return False
        namespace = {"ctx": self, "all": all, "any": any}
        try:
            return bool(eval(compile(tree, "<skip_condition>", "eval"), {"__builtins__": {}}, namespace))
        except Exception:
            return False


A_DAG = PipelineDAG(
    dag_id="production-A",
    stages=[
        PipelineStage(stage_id="parse", module_id="M1", depends_on=[]),
        PipelineStage(
            stage_id="assemble",
            module_id="M2",
            depends_on=["parse"],
        ),
        PipelineStage(
            stage_id="generate",
            module_id="M3",
            depends_on=["assemble"],
            on_failure=StageOnFailure.RETRY,
            retry_max=1,
        ),
        PipelineStage(
            stage_id="validate",
            module_id="M4",
            depends_on=["generate"],
        ),
        PipelineStage(
            stage_id="package",
            module_id="M5",
            depends_on=["validate"],
        ),
    ],
)

B_DAG = PipelineDAG(
    dag_id="audit-B",
    stages=[
        PipelineStage(stage_id="diff", module_id="M6", depends_on=[]),
        PipelineStage(
            stage_id="deep_review",
            module_id="M7",
            depends_on=["diff"],
            on_failure=StageOnFailure.RETRY,
            retry_max=1,
        ),
        PipelineStage(
            stage_id="compliance",
            module_id="M8",
            depends_on=["deep_review"],
            parallel_group="audit_mid",
        ),
        PipelineStage(
            stage_id="risk",
            module_id="M9",
            depends_on=["deep_review"],
            parallel_group="audit_mid",
        ),
        PipelineStage(
            stage_id="report",
            module_id="M10",
            depends_on=["compliance", "risk"],
        ),
        PipelineStage(
            stage_id="gating",
            module_id="M11",
            depends_on=["report"],
            on_failure=StageOnFailure.CLAUDE_RESCUE,
        ),
    ],
    max_parallel=2,
)

# ============================================================================
# Affinity / Anti-Affinity 约束矩阵——对标 K8s podAffinity/podAntiAffinity
# ============================================================================


class AffinityWeight(str, Enum):
    HARD = "hard"
    SOFT = "soft"


class PipelineAffinityConstraint(BaseModel):
    """管线亲和性/反亲和性约束。

    对标 K8s podAffinity/podAntiAffinity:
      - HARD (requiredDuringSchedulingIgnoredDuringExecution): 违反->ABORT
      - SOFT (preferredDuringSchedulingIgnoredDuringExecution): 违反->WARN

    constraint_type:
      - "model":      约束模型分配（防止同模审查）
      - "sandbox":    约束沙箱分配
      - "pipeline":   约束管线流向（A区->B区穿越）
    """

    constraint_type: str = Field(..., description="model | sandbox | pipeline")
    node_a: str = Field(..., description="主约束节点")
    node_b: str | None = Field(default=None, description="对标节点——None表示单节点约束")
    weight: AffinityWeight
    description: str = Field(default="")


AFFINITY_CONSTRAINTS: list[PipelineAffinityConstraint] = [
    PipelineAffinityConstraint(
        constraint_type="model",
        node_a="M3",
        node_b="M7",
        weight=AffinityWeight.HARD,
        description="双盲审查必须用不同模型——M3/M7 hard antiAffinity",
    ),
    PipelineAffinityConstraint(
        constraint_type="model",
        node_a="M8",
        node_b="M9",
        weight=AffinityWeight.SOFT,
        description="建议合规+风险用不同模型交叉审查",
    ),
    PipelineAffinityConstraint(
        constraint_type="sandbox",
        node_a="M1",
        weight=AffinityWeight.HARD,
        description="M1-M4必须在full/standard沙箱执行",
    ),
    PipelineAffinityConstraint(
        constraint_type="pipeline",
        node_a="A",
        weight=AffinityWeight.HARD,
        description="A区产出必须经M5打包->M6边界标记",
    ),
    PipelineAffinityConstraint(
        constraint_type="model",
        node_a="M8",
        weight=AffinityWeight.SOFT,
        description="M8-M11优先DeepSeek降低成本",
    ),
]

# M3↔M7 antiAffinity 硬约束影响链路文档
# deepseek不可用 -> M3降级到glm -> M7被迫改用claude (不能同模)
# -> claude成本上升但保证双盲独立性——这是双盲审计体系的安全底线


# ============================================================================
# Artifact Passing——模块间结构化产出物传递（对标 CI/CD Artifacts）
# ============================================================================


class ArtifactType(str, Enum):
    CODE = "code"
    DOC = "doc"
    DIFF = "diff"
    AUDIT_REPORT = "audit_report"
    PLAN = "plan"
    CONTEXT_BUNDLE = "context_bundle"
    METADATA = "metadata"


class ArtifactClassification(str, Enum):
    """artifact 数据分级——对标 SOC2 CC7.2 + DLP 策略。"""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class PipelineArtifact(BaseModel):
    """模块执行后的产出物——对标 GitHub Actions upload-artifact。

    每个 ModuleResult 可以产出 0..N 个 Artifact。
    下游模块通过 artifact_key 引用。
    """

    artifact_key: str = Field(description="唯一引用键——如 'M3_generated_code'")
    artifact_id: str = Field(default="", description="UUID格式唯一标识")
    artifact_type: ArtifactType
    produced_by: str = Field(description="产出模块的 module_id——如 'M3'")
    content: str = Field(default="", description="产出物内容或摘要")
    path: str | None = Field(default=None, description="产出物文件路径")
    size: int = Field(default=0, ge=0, description="产出物大小(字节)")
    hash_value: str = Field(default="", description="SHA256 完整性哈希——B138")
    timestamp: str = Field(default_factory=lambda: now_utc().isoformat(), description="产出时间戳")
    classification: ArtifactClassification = Field(
        default=ArtifactClassification.INTERNAL,
        description="数据分级标签——SOC2 CC7.2 数据生命周期管理",
    )
    file_paths: list[str] = Field(default_factory=list)
    summary: str = Field(default="", description="人类可读摘要—— ≤200 chars")
    metadata: dict[str, object] = Field(default_factory=dict)

    def artifact_ref(self) -> str:
        return self.artifact_key


class ModuleInput(BaseModel):
    """模块的输入——从上一个模块的产出物中选取。"""

    module_id: str
    consumes: list[str] = Field(
        default_factory=list,
        description="依赖的 artifact_key 列表",
    )
    previous_artifacts: list[PipelineArtifact] = Field(
        default_factory=list,
        description="上级模块的产出物",
    )
    context: dict[str, object] = Field(
        default_factory=dict,
        description="额外上下文——opaque dict 可校验",
    )
    task_override: dict[str, object] | None = Field(
        default=None,
        description="传递给模型的补充指令——如 '基于 M3 生成的代码做审查'",
    )

    def validate(self) -> bool:
        """校验所需 Artifact 是否齐全。"""
        available_keys = {a.artifact_key for a in self.previous_artifacts}
        for required in self.consumes:
            if required not in available_keys:
                return False
        return True


class PipelineArtifactManifest(BaseModel):
    """一次 Pipeline 执行的完整产出物清单——对标 CI/CD Artifacts Summary。

    使用场景：
      - M6 审查 M3 产出 -> manifest.get("M3_generated_code")
      - Claude 救援 -> manifest 作为完整上下文注入
      - FLE 反馈 -> 对比 manifest.diff_to_expected
    """

    run_id: str
    pipeline_id: str = Field(default="", description="管线标识 A_DAG/B_DAG")
    task_id: str = Field(default="", description="关联的任务ID")
    artifacts: list[PipelineArtifact] = Field(default_factory=list)
    meta: dict[str, object] = Field(default_factory=dict, description="扩展元数据")
    created: str = Field(default_factory=lambda: now_utc().isoformat(), description="创建时间")

    def get(self, artifact_key: str) -> PipelineArtifact | None:
        for a in self.artifacts:
            if a.artifact_key == artifact_key:
                return a
        return None

    def by_module(self, module_id: str) -> list[PipelineArtifact]:
        return [a for a in self.artifacts if a.produced_by == module_id]

    def by_type(self, artifact_type: ArtifactType) -> list[PipelineArtifact]:
        return [a for a in self.artifacts if a.artifact_type == artifact_type]


# ============================================================================
# Data Lineage —— 数据血缘追踪（SOC2 CC7.2 审计证据链）
# ============================================================================


class PipelineLineageEntry(BaseModel):
    """单个模块的上下游血缘记录——对标 dbt model lineage + OpenLineage。

    HMAC 链：每个 entry 的 lineage_hash = HMAC(parent_hash, current_module_id + artifact_keys)
    串联后形成不可篡改的审计证据链。
    """

    module_id: str
    pipeline: str
    upstream_module_ids: list[str] = Field(default_factory=list)
    consumed_artifact_keys: list[str] = Field(default_factory=list)
    produced_artifact_keys: list[str] = Field(default_factory=list)
    started_at: str = ""
    finished_at: str = ""
    lineage_hash: str = Field(
        default="",
        description="HMAC-SHA256(parent_hash || module_id || artifact_keys)——不可篡改链",
    )
    classification_summary: dict[str, int] = Field(
        default_factory=dict,
        description="本次产出的分级统计——如 {'internal': 3, 'confidential': 1}",
    )


class PipelineLineageChain(BaseModel):
    """一次 Pipeline 执行的完整血缘链路。

    entries 按执行顺序排列，每个 entry 的 lineage_hash 由前一个 entry 的
    lineage_hash 派生，形成不可篡改的审计证据链。
    """

    run_id: str
    entries: list[PipelineLineageEntry] = Field(default_factory=list)

    def verify_integrity(self) -> bool:
        """验证 HMAC 链完整性。"""
        import hashlib

        prev_hash = ""
        for entry in self.entries:
            expected = hashlib.sha256(
                f"{prev_hash}|{entry.module_id}|{','.join(sorted(entry.produced_artifact_keys))}".encode()
            ).hexdigest()
            if entry.lineage_hash and entry.lineage_hash != expected:
                return False
            prev_hash = entry.lineage_hash
        return True

    def add_entry(self, entry: PipelineLineageEntry) -> str:
        """将 entry 追加到链中，基于前一个 entry 的 hash 计算当前 hash。
        返回计算后的 lineage_hash。
        """
        import hashlib

        parent_hash = self.entries[-1].lineage_hash if self.entries else ""
        raw = f"{parent_hash}|{entry.module_id}|{','.join(sorted(entry.produced_artifact_keys))}"
        entry.lineage_hash = hashlib.sha256(raw.encode()).hexdigest()
        self.entries.append(entry)
        return entry.lineage_hash


# ============================================================================
# ModuleOutput Schema——每个 M 节点的输出形状契约（B37 第四轮审计）
# ============================================================================


class M1ParseOutput(BaseModel):
    """M1 输出：任务卡解析->结构化执行计划"""

    model_config = BASE_CONFIG
    task_id: str
    plan: dict[str, object] = Field(default_factory=dict)
    estimated_steps: int = Field(ge=1, le=50)
    summary: str = ""


class M3GenerateOutput(BaseModel):
    """M3 输出：代码/文档生成——核心生产"""

    model_config = BASE_CONFIG
    module_id: str = "M3"
    generated_files: list[str] = Field(default_factory=list)
    diffs: list[str] = Field(default_factory=list)
    verdict: str = Field(default="ok")
    summary: str = ""
    tokens_used: int = 0


class M7ReviewOutput(BaseModel):
    """M7 输出：深度审查——逐个文件逻辑/合规"""

    model_config = BASE_CONFIG
    module_id: str = "M7"
    reviewed_files: list[str] = Field(default_factory=list)
    issues_found: int = Field(default=0, ge=0)
    verdict: str = Field(default="ok")
    summary: str = ""


class M8ComplianceOutput(BaseModel):
    """M8 输出：标准合规——PS/GOV/KB决策记录"""

    model_config = BASE_CONFIG
    module_id: str = "M8"
    standards_checked: list[str] = Field(default_factory=list)
    violations: list[str] = Field(default_factory=list)
    verdict: str = Field(default="ok")
    summary: str = ""


class M9RiskOutput(BaseModel):
    """M9 输出：风险评估——OWASP LLM Top 10"""

    model_config = BASE_CONFIG
    module_id: str = "M9"
    risk_level: str = "low"
    owasp_items: list[str] = Field(default_factory=list)
    verdict: str = Field(default="ok")
    summary: str = ""


class M10ReportOutput(BaseModel):
    """M10 输出：审计报告->Finding 格式"""

    model_config = BASE_CONFIG
    module_id: str = "M10"
    finding_count: int = Field(default=0, ge=0)
    findings: list[dict[str, object]] = Field(default_factory=list)
    verdict: str = Field(default="ok")
    summary: str = ""


class M6DiffOutput(BaseModel):
    """M6 差异检测输出——B区审计入口信号。"""

    has_changes: bool = False
    changed_files: list[str] = []
    diff_summary: str = ""
    added_lines: int = 0
    removed_lines: int = 0
    total_diff_files: int = 0


class M11GatingOutput(BaseModel):
    """M11 输出：门禁裁决——G5/G6"""

    model_config = BASE_CONFIG
    module_id: str = "M11"
    g5_passed: bool = False
    g6_passed: bool = False
    verdict: str = Field(default="blocked")
    summary: str = ""


class GenericModuleOutput(BaseModel):
    """通用模块输出——未定义专用 schema 时的兜底"""

    model_config = BASE_CONFIG
    module_id: str
    summary: str = ""
    tokens_used: int = 0
    simulated: bool = False
    dry_run: bool = False


_MODULE_OUTPUT_SCHEMAS: dict[str, type[BaseModel]] = {
    "M1": M1ParseOutput,
    "M3": M3GenerateOutput,
    "M6": M6DiffOutput,
    "M7": M7ReviewOutput,
    "M8": M8ComplianceOutput,
    "M9": M9RiskOutput,
    "M10": M10ReportOutput,
    "M11": M11GatingOutput,
}


def validate_module_output(module_id: str, output: dict[str, Any]) -> dict[str, Any]:
    """对模块输出做 Schema 校验。失败时附加 _validation_errors 不抛异常。"""
    schema_cls = _MODULE_OUTPUT_SCHEMAS.get(module_id, GenericModuleOutput)
    try:
        validated = schema_cls(**output)
        result = validated.model_dump()
        result["_schema_validated"] = True
        return result
    except Exception as exc:
        output["_schema_validated"] = False
        output["_validation_errors"] = str(exc)
        return output
