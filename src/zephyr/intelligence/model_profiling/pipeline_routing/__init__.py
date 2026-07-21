# [A_module] module_id=MOD-GOV-init | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
    _HAS_CLI = True
except ImportError:
    _HAS_CLI = False

# __all__ 治本原则: 只声明实际通过 from...import 导入的符号
# 历史问题: 旧 __all__ 声明了 capability_passport/exam_orchestrator/exam_test_cases/
# model_discovery 等模块名,但这些模块位于父目录 model_profiling/ 下,不在本包内,
# 且本 __init__.py 未 import 它们 -> import * 时 AttributeError
# 同理 benchmark_suite/results_writer/profiler/task_model_learner 是本包内模块,
# 但只导入了它们的符号(如 BenchmarkCase),未导入模块本身,不应出现在 __all__
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
]
if _HAS_CLI:
    __all__.append("cli")
