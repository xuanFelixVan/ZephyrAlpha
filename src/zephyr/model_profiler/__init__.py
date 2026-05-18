# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model-profiler/blueprint.md
# [MODULE] zephyr.model_profiler
# [INVARIANTS] 模型能力评测;能力护照;红蓝对抗评测
# [MODIFY-GUARD] docs/03_modules/_cross_layer/model-profiler/blueprint.md;src/zephyr/model_profiler/__init__.py
# [CONSUMERS] MOD-INF-009;MOD-INF-036
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ProfilerError;EvaluationError
# [TESTS] tests/test_model_profiler/

"""
Model Profiler — 本地 + 远程模型性能基准测试
==============================================
自动发现 Ollama 本地模型和远程 API 模型，
运行 7 维度 26 项标准化 benchmark 测试，
生成性能排名和最佳模型推荐。

Quickstart
----------
    from zephyr.model_profiler import ModelProfiler, ModelDiscovery

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
    from zephyr.model_profiler.results_writer import write_benchmark_results
    write_benchmark_results(results, "data/model_profiles/")
"""

from zephyr.model_profiler.model_discovery import (
    DEFAULT_OLLAMA_URL,
    DiscoveredModel,
    ModelDiscovery,
)
from zephyr.model_profiler.benchmark_suite import (
    ALL_BENCHMARK_CASES,
    CATEGORY_MAP,
    BenchmarkCase,
)
from zephyr.model_profiler.profiler import (
    CaseResult,
    ModelProfile,
    ModelProfiler,
    SKIP_MODEL_PATTERNS,
    MAX_OLLAMA_MODELS,
)
from zephyr.model_profiler.task_model_learner import (
    ModelTaskEntry,
    ModelTaskMatrix,
    TaskRecommendation,
)

__all__ = [
    "ALL_BENCHMARK_CASES",
    "BenchmarkCase",
    "CaseResult",
    "CATEGORY_MAP",
    "DEFAULT_OLLAMA_URL",
    "DiscoveredModel",
    "MAX_OLLAMA_MODELS",
    "ModelDiscovery",
    "ModelProfile",
    "ModelProfiler",
    "ModelTaskEntry",
    "ModelTaskMatrix",
    "SKIP_MODEL_PATTERNS",
    "TaskRecommendation",
    "benchmark_suite",
    "capability_passport",
    "cli",
    "deepseek_v4_chat",
    "exam_orchestrator",
    "exam_test_cases",
    "profiler",
    "results_writer",
    "task_model_learner",
]
