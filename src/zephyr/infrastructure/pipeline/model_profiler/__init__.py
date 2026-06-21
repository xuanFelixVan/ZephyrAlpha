# [A_module] module_id=MOD-INF_model_profiler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model-profiler/blueprint.md | §
"""
Model Profiler — 本地 + 远程模型性能基准测试
==============================================
自动发现 Ollama 本地模型和远程 API 模型，
运行 7 维度 26 项标准化 benchmark 测试，
生成性能排名和最佳模型推荐。

Quickstart
----------
    from zephyr.intelligence.model_profiling.pipeline import ModelProfiler, ModelDiscovery

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
    from zephyr.intelligence.model_profiling.pipeline.results_writer import write_benchmark_results
    write_benchmark_results(results, "data/model_profiles/")
"""
from . import cli

_LAZY_SYMBOLS = {
    "DEFAULT_OLLAMA_URL": "zephyr.intelligence.model_profiling.pipeline.model_discovery",
    "DiscoveredModel": "zephyr.intelligence.model_profiling.pipeline.model_discovery",
    "ModelDiscovery": "zephyr.intelligence.model_profiling.pipeline.model_discovery",
    "ALL_BENCHMARK_CASES": "zephyr.intelligence.model_profiling.pipeline.benchmark_suite",
    "CATEGORY_MAP": "zephyr.intelligence.model_profiling.pipeline.benchmark_suite",
    "BenchmarkCase": "zephyr.intelligence.model_profiling.pipeline.benchmark_suite",
    "CaseResult": "zephyr.intelligence.model_profiling.pipeline.profiler",
    "ModelProfile": "zephyr.intelligence.model_profiling.pipeline.profiler",
    "ModelProfiler": "zephyr.intelligence.model_profiling.pipeline.profiler",
    "SKIP_MODEL_PATTERNS": "zephyr.intelligence.model_profiling.pipeline.profiler",
    "MAX_OLLAMA_MODELS": "zephyr.intelligence.model_profiling.pipeline.profiler",
    "ModelTaskEntry": "zephyr.intelligence.model_profiling.pipeline.task_model_learner",
    "ModelTaskMatrix": "zephyr.intelligence.model_profiling.pipeline.task_model_learner",
    "TaskRecommendation": "zephyr.intelligence.model_profiling.pipeline.task_model_learner",
}

_LAZY_SUBMODULES = [
    "benchmark_suite",
    "capability_passport",
    "cli",
    "deepseek_v4_chat",
    "exam_orchestrator",
    "exam_test_cases",
    "model_discovery",
    "profiler",
    "results_writer",
    "task_model_learner",
]

def __getattr__(name: str):
    import importlib
    if name in _LAZY_SUBMODULES:
        mod = importlib.import_module(f"zephyr.intelligence.model_profiling.pipeline.{name}")
        globals()[name] = mod
        return mod
    if name in _LAZY_SYMBOLS:
        mod = importlib.import_module(_LAZY_SYMBOLS[name])
        value = getattr(mod, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

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
