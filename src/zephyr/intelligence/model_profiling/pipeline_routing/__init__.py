# [A_module] module_id=MOD-RSC_pipeline_routing | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model-profiler/blueprint.md
# [MODULE] zephyr.intelligence.model_profiling.pipeline_routing
# [INVARIANTS] pipeline routing variant of model profiler
# [MODIFY-GUARD] structural changes require owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
"""Model Profiler — Pipeline Routing variant"""
from . import cli

from zephyr.intelligence.model_profiling.pipeline_routing.model_discovery import (
    DEFAULT_OLLAMA_URL,
    DiscoveredModel,
    ModelDiscovery,
)
from zephyr.intelligence.model_profiling.pipeline_routing.benchmark_suite import (
    ALL_BENCHMARK_CASES,
    CATEGORY_MAP,
    BenchmarkCase,
)
from zephyr.intelligence.model_profiling.pipeline_routing.profiler import (
    CaseResult,
    ModelProfile,
    ModelProfiler,
    SKIP_MODEL_PATTERNS,
    MAX_OLLAMA_MODELS,
)
from zephyr.intelligence.model_profiling.pipeline_routing.task_model_learner import (
    ModelTaskEntry,
    ModelTaskMatrix,
    TaskRecommendation,
)

__all__ = [
    'ALL_BENCHMARK_CASES',
    'BenchmarkCase',
    'CATEGORY_MAP',
    'CaseResult',
    'DEFAULT_OLLAMA_URL',
    'DiscoveredModel',
    'MAX_OLLAMA_MODELS',
    'ModelDiscovery',
    'ModelProfile',
    'ModelProfiler',
    'ModelTaskEntry',
    'ModelTaskMatrix',
    'SKIP_MODEL_PATTERNS',
    'TaskRecommendation',
    'benchmark_suite',
    'capability_passport',
    'cli',
    'deepseek_v4_chat',
    'exam_orchestrator',
    'exam_test_cases',
    'model_discovery',
    'profiler',
    'results_writer',
    'task_model_learner',
]
