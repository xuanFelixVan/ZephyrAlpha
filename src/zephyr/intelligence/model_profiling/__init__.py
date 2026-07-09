# [A_module] module_id=MOD-RSC_model_profiling | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md
# [MODULE] zephyr.intelligence.model_profiling
# [INVARIANTS] 模型能力评测;能力护照;红蓝对抗评测
# [MODIFY-GUARD] docs/03_modules/_cross_layer/model_profiler/blueprint.md
# [CONSUMERS] MOD-INF-009;MOD-INF-036
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ProfilerError;EvaluationError
# [TESTS] tests/test_model_profiler/
# [TTL] permanent

"""
Model Profiling — 本地 + 远程模型性能基准测试
==============================================
自动发现 Ollama 本地模型和远程 API 模型，
运行 7 维度 26 项标准化 benchmark 测试，
生成性能排名和最佳模型推荐。

Quickstart
----------
    from zephyr.intelligence.model_profiling import ModelProfiler, ModelDiscovery

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
    from zephyr.intelligence.model_profiling.results_writer import write_benchmark_results
    write_benchmark_results(results, "data/model_profiles/")
"""

_SUBMODULES = [
    "benchmark_suite",
    "capability_passport",
    "deepseek_v4_chat",
    "exam_orchestrator",
    "exam_test_cases",
    "model_discovery",
    "profiler",
    "provider_data",
    "results_writer",
    "task_model_learner",
]


def __getattr__(name: str):
    if name in _SUBMODULES:
        import importlib

        mod = importlib.import_module(f"zephyr.intelligence.model_profiling.{name}")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


from zephyr.intelligence.model_profiling.benchmark_suite import (
    ALL_BENCHMARK_CASES,
    CATEGORY_MAP,
    BenchmarkCase,
)
from zephyr.intelligence.model_profiling.model_discovery import (
    DiscoveredModel,
    ModelDiscovery,
)
from zephyr.intelligence.model_profiling.profiler import (
    MAX_OLLAMA_MODELS,
    SKIP_MODEL_PATTERNS,
    CaseResult,
    ModelProfile,
    ModelProfiler,
)
from zephyr.intelligence.model_profiling.task_model_learner import (
    ModelTaskEntry,
    ModelTaskMatrix,
    TaskRecommendation,
)

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
    "deepseek_v4_chat",
    "exam_orchestrator",
    "exam_test_cases",
    "model_discovery",
    "profiler",
    "provider_data",
    "results_writer",
    "task_model_learner",
'case_assembler', 'exam_executor', 'exam_judge', 'exam_rubric', 'job_matcher']
