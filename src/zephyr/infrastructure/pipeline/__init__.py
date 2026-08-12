# [A_module] module_id=MOD-INF-pipeline | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md
# [TTL] permanent
"""


ZephyrAlpha Pipeline 模块 — M1-M11 双管线 + K8s Scheduling Framework + 跨层数据路由
A区（M1-M5）生产管线 + B区（M6-M11）审计管线。
GOV-AI-002 v2.0.0 决策树 + 插件化路由 + Agent 桥接 + Schema 校验。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: backpressure_manager 子模块符号 6个
#   fields: BackpressureManager / BpState / BpSymbolState / emit_pause / emit_resume / emit_throttle
#   code: zephyr.infrastructure.pipeline.backpressure_manager
# - id: I2
#   name: circuit_breaker_manager 子模块符号 1个
#   fields: CircuitBreakerManager
#   code: zephyr.infrastructure.pipeline.circuit_breaker_manager
# - id: I3
#   name: cost_tracker 子模块符号 1个
#   fields: CostTracker
#   code: zephyr.infrastructure.pipeline.cost_tracker
# - id: I4
#   name: ct_pipe_routing 子模块符号 6个
#   fields: CtPipeRoutingHints / PipelineRoutingInputsError / ct_pipe_hints_from_task_card / enforce_affinity / modules_slice_from_node / resolve_ct_pipe_orc001
#   code: zephyr.infrastructure.pipeline.ct_pipe_routing
# - id: I5
#   name: dead_letter_queue 子模块符号 1个
#   fields: DeadLetterQueue
#   code: zephyr.infrastructure.pipeline.dead_letter_queue
# - id: I6
#   name: model_router 子模块符号 1个
#   fields: ModelRouter
#   code: zephyr.infrastructure.pipeline.model_router
# - id: I7
#   name: models 子模块符号 45个
#   fields: A_DAG / AFFINITY_CONSTRAINTS / B_DAG / M_MODULE_SPECS / M_MODULES / ABExperimentRoute 等45个
#   code: zephyr.infrastructure.pipeline.models
# - id: I8
#   name: pipeline_agent_bridge 子模块符号 4个
#   fields: M_TO_ROLE / PipelineAgentBridge / domain_for_pipeline / role_for_module
#   code: zephyr.infrastructure.pipeline.pipeline_agent_bridge
# - id: I9
#   name: pipeline_lock 子模块符号 6个
#   fields: FileLockBackend / LockBackend / LockResult / LockStatus / MemoryLockBackend / PipelineLock
#   code: zephyr.infrastructure.pipeline.pipeline_lock
# - id: I10
#   name: pipeline_roadmap 子模块符号 62个
#   fields: PIPELINE_DEPENDENCIES / PIPELINE_DEPENDENCIES_MAP / PIPELINE_VERSION_MAP / PROFILES / AdversarialDeceptionProtocol / AlertEscalationTracker 等62个
#   code: zephyr.infrastructure.pipeline.pipeline_roadmap
# - id: I11
#   name: preemption_manager 子模块符号 1个
#   fields: PreemptionManager
#   code: zephyr.infrastructure.pipeline.preemption_manager
# - id: I12
#   name: routing_plugins 子模块符号 5个
#   fields: DEFAULT_PLUGINS / NoEligibleNodeError / PipelineRouter / RoutingContext / RoutingPlugin
#   code: zephyr.infrastructure.pipeline.routing_plugins
# 层: 算法
# - id: A1
#   name_zh: ① 包级聚合再导出
#   name_en: zephyr.infrastructure.pipeline.__init__
#   intro: ZephyrAlpha Pipeline 模块 — M1-M11 双管线 + K8s Scheduling Framew
#   desc: MOD-INF-009 包入口，包级聚合再导出并声明 __all__（125项）
#   inputs: I1 I2 I3 I4 I5 I6 I7 I8 I9 I10 I11 I12
#   outputs: zephyr.infrastructure.pipeline 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（125项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.infrastructure.pipeline 包公共 API
#   name_en: __all__ 125项
#   intro: ZephyrAlpha Pipeline 模块 — M1-M11 双管线 + K8s Scheduling Framew——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# I5 --> A1
# I6 --> A1
# I7 --> A1
# I8 --> A1
# I9 --> A1
# I10 --> A1
# I11 --> A1
# I12 --> A1
# A1 --> O1
"""

from zephyr.infrastructure.pipeline.backpressure_manager import (
    BackpressureManager,
    BpState,
    BpSymbolState,
    emit_pause,
    emit_resume,
    emit_throttle,
)
from zephyr.infrastructure.pipeline.circuit_breaker_manager import (
    CircuitBreakerManager,
)
from zephyr.infrastructure.pipeline.cost_tracker import (
    CostTracker,
)
from zephyr.infrastructure.pipeline.ct_pipe_routing import (
    CtPipeRoutingHints,
    PipelineRoutingInputsError,
    ct_pipe_hints_from_task_card,
    enforce_affinity,
    modules_slice_from_node,
    resolve_ct_pipe_orc001,
)
from zephyr.infrastructure.pipeline.dead_letter_queue import (
    DeadLetterQueue,
)
from zephyr.infrastructure.pipeline.model_router import ModelRouter
from zephyr.infrastructure.pipeline.models import (
    A_DAG,
    AFFINITY_CONSTRAINTS,
    B_DAG,
    M_MODULE_SPECS,
    M_MODULES,
    ABExperimentRoute,
    AffinityWeight,
    AIImpactAssessment,
    ArtifactClassification,
    ArtifactType,
    CircuitBreakerState,
    ClaudeRescueTrigger,
    CostRecord,
    DeadLetterEntry,
    EmergencyFallbackPlan,
    ExperimentVariant,
    GenericModuleOutput,
    M1ParseOutput,
    M3GenerateOutput,
    M6DiffOutput,
    M7ReviewOutput,
    M8ComplianceOutput,
    M9RiskOutput,
    M10ReportOutput,
    M11GatingOutput,
    ModelCollapseAlert,
    ModelConfidence,
    ModelVersionInfo,
    ModuleInput,
    ModuleResult,
    PipelineAffinityConstraint,
    PipelineArtifact,
    PipelineArtifactManifest,
    PipelineDAG,
    PipelineLineageChain,
    PipelineLineageEntry,
    PipelineOrchestratorConfig,
    PipelineResult,
    PipelineRouteDecision,
    PipelineStage,
    PipelineStatus,
    PreemptionRecord,
    StageContext,
    StageOnFailure,
    validate_module_output,
)
from zephyr.infrastructure.pipeline.pipeline_agent_bridge import (
    M_TO_ROLE,
    PipelineAgentBridge,
    domain_for_pipeline,
    role_for_module,
)
from zephyr.infrastructure.pipeline.pipeline_lock import (
    FileLockBackend,
    LockBackend,
    LockResult,
    LockStatus,
    MemoryLockBackend,
    PipelineLock,
)
from zephyr.infrastructure.pipeline.pipeline_roadmap import (
    PIPELINE_DEPENDENCIES,
    PIPELINE_DEPENDENCIES_MAP,
    PIPELINE_VERSION_MAP,
    PROFILES,
    AdversarialDeceptionProtocol,
    AlertEscalationTracker,
    AntiPatternEntry,
    AuditIndependenceProof,
    BlueprintCodeDriftChecker,
    BlueprintCodeDriftEntry,
    ByzantineFailureCheck,
    ChaosExperimentResult,
    CheckpointResumeState,
    CodebaseHealthScore,
    ConceptDriftMonitor,
    ConstructionPhaseTracker,
    CrossMarketGuard,
    CrossModuleSyncEntry,
    DataProvenanceTracker,
    DegradationLevel,
    DegradationTimeline,
    Dependency,
    DependencyHealthChecker,
    DependencyRotDetector,
    DeschedulerTaskState,
    DriftIntoFailureAlert,
    DriftReport,
    ErrorBudget,
    FaultInjectionSpec,
    GoldenTestResult,
    HallucinationCheckResult,
    HealthReport,
    KillSwitchStatus,
    MannKendallResult,
    MarketDataPipelineStatus,
    ModelArbitrageResult,
    MutationTestResult,
    OrchestratorIntegrationBridge,
    OutcomeBiasCheck,
    PhaseStatus,
    PipelineOrchestratorRoadmapMixin,
    PipelineSignalData,
    PolicyDiffReport,
    PolicyTestCase,
    PortfolioRiskSnapshot,
    PositionEffectCheck,
    PostmortemReport,
    ReproducibilityManifest,
    ResilienceBudget,
    ReviewDebtTracker,
    ROICalculator,
    RouteDecisionLog,
    SagaLogEntry,
    SchedulingProfileDef,
    SessionBrief,
    SilentFailureAlert,
    SLOMetric,
    SLOState,
    StopTheLineTrigger,
    SupplyChainIntegrityCheck,
    TOCTOUGuardResult,
    select_profile,
)
from zephyr.infrastructure.pipeline.preemption_manager import (
    PreemptionManager,
)
from zephyr.infrastructure.pipeline.routing_plugins import (
    DEFAULT_PLUGINS,
    NoEligibleNodeError,
    PipelineRouter,
    RoutingContext,
    RoutingPlugin,
)

from . import llm_gateway

_INTELLIGENCE_LAZY_SYMBOLS = {
    "ALL_BENCHMARK_CASES": "zephyr.intelligence.model_profiling.pipeline",
    "CATEGORY_MAP": "zephyr.intelligence.model_profiling.pipeline",
    "BenchmarkCase": "zephyr.intelligence.model_profiling.pipeline",
    "CaseResult": "zephyr.intelligence.model_profiling.pipeline",
    "DiscoveredModel": "zephyr.intelligence.model_profiling.pipeline",
    "ModelDiscovery": "zephyr.intelligence.model_profiling.pipeline",
    "ModelProfile": "zephyr.intelligence.model_profiling.pipeline",
    "ModelProfiler": "zephyr.intelligence.model_profiling.pipeline",
    "ModelTaskEntry": "zephyr.intelligence.model_profiling.pipeline",
    "ModelTaskMatrix": "zephyr.intelligence.model_profiling.pipeline",
    "TaskRecommendation": "zephyr.intelligence.model_profiling.pipeline",
    "detect_drift": "zephyr.intelligence.model_profiling.results_writer",
    "load_benchmark_history": "zephyr.intelligence.model_profiling.results_writer",
    "to_model_benchmark_result": "zephyr.intelligence.model_profiling.results_writer",
    "write_benchmark_results": "zephyr.intelligence.model_profiling.results_writer",
}


def __getattr__(name: str):
    import importlib

    if name in _INTELLIGENCE_LAZY_SYMBOLS:
        mod = importlib.import_module(_INTELLIGENCE_LAZY_SYMBOLS[name])
        value = getattr(mod, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AFFINITY_CONSTRAINTS",
    "ALL_BENCHMARK_CASES",
    "A_DAG",
    "B_DAG",
    "CATEGORY_MAP",
    "DEFAULT_PLUGINS",
    "M_MODULES",
    "M_MODULE_SPECS",
    "M_TO_ROLE",
    "ABExperimentRoute",
    "AIImpactAssessment",
    "AffinityWeight",
    "ArtifactClassification",
    "ArtifactType",
    "BackpressureManager",
    "BenchmarkCase",
    "BlueprintCodeDriftChecker",
    "BlueprintCodeDriftEntry",
    "BpState",
    "BpSymbolState",
    "CaseResult",
    "ChaosExperimentResult",
    "CircuitBreakerManager",
    "CircuitBreakerState",
    "ClaudeRescueTrigger",
    "CostRecord",
    "CostTracker",
    "CtPipeRoutingHints",
    "DeadLetterEntry",
    "DeadLetterQueue",
    "DegradationLevel",
    "DiscoveredModel",
    "DriftReport",
    "EmergencyFallbackPlan",
    "ErrorBudget",
    "ExperimentVariant",
    "FaultInjectionSpec",
    "FileLockBackend",
    "GenericModuleOutput",
    "GoldenTestResult",
    "HallucinationCheckResult",
    "HealthReport",
    "LockBackend",
    "LockResult",
    "LockStatus",
    "M1ParseOutput",
    "M3GenerateOutput",
    "M6DiffOutput",
    "M7ReviewOutput",
    "M8ComplianceOutput",
    "M9RiskOutput",
    "M10ReportOutput",
    "M11GatingOutput",
    "MemoryLockBackend",
    "ModelCollapseAlert",
    "ModelConfidence",
    "ModelDiscovery",
    "ModelProfile",
    "ModelProfiler",
    "ModelRouter",
    "ModelTaskEntry",
    "ModelTaskMatrix",
    "ModelVersionInfo",
    "ModuleInput",
    "ModuleResult",
    "MutationTestResult",
    "NoEligibleNodeError",
    "OrchestratorIntegrationBridge",
    "PipelineAffinityConstraint",
    "PipelineAgentBridge",
    "PipelineArtifact",
    "PipelineArtifactManifest",
    "PipelineDAG",
    "PipelineLineageChain",
    "PipelineLineageEntry",
    "PipelineLock",
    "PipelineOrchestratorConfig",
    "PipelineOrchestratorRoadmapMixin",
    "PipelineResult",
    "PipelineRouteDecision",
    "PipelineRouter",
    "PipelineRoutingInputsError",
    "PipelineStage",
    "PipelineStatus",
    "PolicyDiffReport",
    "PreemptionManager",
    "PreemptionRecord",
    "ROICalculator",
    "RoutingContext",
    "RoutingPlugin",
    "SLOMetric",
    "SLOState",
    "SessionBrief",
    "StageContext",
    "StageOnFailure",
    "TaskRecommendation",
    "backpressure_manager",
    "backpressure_types",
    "circuit_breaker_manager",
    "cost_tracker",
    "ct_pipe_hints_from_task_card",
    "ct_pipe_routing",
    "dead_letter_queue",
    "detect_drift",
    "domain_for_pipeline",
    "emit_pause",
    "emit_resume",
    "emit_throttle",
    "enforce_affinity",
    "llm_gateway",
    "load_benchmark_history",
    "model_router",
    "models",
    "modules_slice_from_node",
    "pipeline_agent_bridge",
    "pipeline_lock",
    "pipeline_orchestrator",
    "pipeline_roadmap",
    "preemption_manager",
    "resolve_ct_pipe_orc001",
    "role_for_module",
    "routing_plugins",
    "to_model_benchmark_result",
    "validate_module_output",
    "write_benchmark_results",
]
