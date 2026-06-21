# [A_module] module_id=MOD-ORC_model_profiler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model-profiler/blueprint.md
# [MODULE] zephyr.intelligence.model_profiling.pipeline_routing
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS] 
# [ERROR_CONTRACT] 
# [TESTS] 
"""
Model Profiler — 本地 + 远程模型性能基准测试
==============================================
自动发现 Ollama 本地模型和远程 API 模型，
运行 7 维度 26 项标准化 benchmark 测试，
生成性能排名和最佳模型推荐。

Quickstart
----------
    from zephyr.intelligence.model_profiling.pipeline_routing import ModelProfiler, ModelDiscovery

    # 仅列出可用模型
    discovery = ModelDiscovery()
    for m in discovery.discover_all():
        print(f"  {m.name} ({m.source}, {m.size_gb:.1f}GB)")

    # 快速测试单个模型
    profiler = ModelProfiler()
    profile = profiler.quick_profile("qwen3:8b")
    print(f"Score: {profile.average_score:.2f}, P50: {profile.latency_p50_ms:.0f}ms")

    # 全量 benchmark 所有 Ollama 模型
    results = profiler.profile_ollama_only()
    profiler.print_ranking(results)

    # 写入结果到 registry
    from zephyr.intelligence.model_profiling.pipeline_routing.results_writer import write_benchmark_results
    write_benchmark_results(results, "data/model_profiles/")
"""
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
