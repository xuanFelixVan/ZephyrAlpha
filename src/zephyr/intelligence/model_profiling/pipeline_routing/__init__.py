# [A_module] module_id=MOD-INF-034-pipeline_routing | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md
# [MODULE] zephyr.intelligence.model_profiling.pipeline_routing
# [INVARIANTS] pipeline routing variant of model profiler
# [MODIFY-GUARD] structural changes require owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""Model Profiler — Pipeline Routing variant"""

from zephyr.intelligence.model_profiling.pipeline_routing.benchmark_suite import (
    ALL_BENCHMARK_CASES,
    CATEGORY_MAP,
    BenchmarkCase,
)
from zephyr.intelligence.model_profiling.model_discovery import (
    DiscoveredModel,
    ModelDiscovery,
)
from zephyr.intelligence.model_profiling.pipeline_routing.profiler import (
    MAX_OLLAMA_MODELS,
    SKIP_MODEL_PATTERNS,
    CaseResult,
    ModelProfile,
    ModelProfiler,
)
from zephyr.intelligence.model_profiling.pipeline_routing.task_model_learner import (
    ModelTaskEntry,
    ModelTaskMatrix,
    TaskRecommendation,
)

# DEFAULT_OLLAMA_URL 已下沉到 zephyr.shared.foundation.constants (§5.160 SSoT),
# 不再从 model_discovery 重新导出, 避免引入死代码 import
try:
    from zephyr.intelligence.model_profiling.pipeline_routing import cli  # noqa: F401
except ImportError:
    pass

__all__ = [
    "ALL_BENCHMARK_CASES",
    "CATEGORY_MAP",
    "MAX_OLLAMA_MODELS",
    "SKIP_MODEL_PATTERNS",
    "BenchmarkCase",
    "CaseResult",
    "DiscoveredModel",
    "ModelDiscovery",
    "ModelProfile",
    "ModelProfiler",
    "ModelTaskEntry",
    "ModelTaskMatrix",
    "TaskRecommendation",
    "benchmark_suite",
    "capability_passport",
    "cli",
    "exam_orchestrator",
    "exam_test_cases",
    "model_discovery",
    "profiler",
    "results_writer",
    "task_model_learner",
]
