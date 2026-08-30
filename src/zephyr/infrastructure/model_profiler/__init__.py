# [A_module] module_id=MOD-INF-model_profiler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md
# [MODULE] zephyr.infrastructure.model_profiler
# [INVARIANTS] 模型能力评测;能力护照;红蓝对抗评测
# [MODIFY-GUARD] docs/03_modules/_cross_layer/model_profiler/blueprint.md;src/zephyr/intelligence/model_profiling/__init__.py
# [CONSUMERS] MOD-INF-009;MOD-INF-036
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ProfilerError;EvaluationError
# [TESTS] tests/test_model_profiler/
# [TTL] permanent

"""
Model Profiler — 本地 + 远程模型性能基准测试
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: __init__.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 ALL_BENCHMARK_CASES, CATEGORY_MAP, DEFAULT_OLLAMA_URL, MAX_OLLAMA_MODELS, S…
#   desc: __init__ import L0；__all__ 25 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（25 符号）
#   name_en: __all__
#   intro: ALL_BENCHMARK_CASES, CATEGORY_MAP, DEFAULT_OLLAMA_URL, MAX_OLLAMA_MODELS, SKIP_…
#   downstream: MOD-INF-009;MOD-INF-036
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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

_LAZY_SYMBOLS = {
    "DEFAULT_OLLAMA_URL": "zephyr.intelligence.model_profiling.model_discovery",
    "DiscoveredModel": "zephyr.intelligence.model_profiling.model_discovery",
    "ModelDiscovery": "zephyr.intelligence.model_profiling.model_discovery",
    "ALL_BENCHMARK_CASES": "zephyr.intelligence.model_profiling.benchmark_suite",
    "CATEGORY_MAP": "zephyr.intelligence.model_profiling.benchmark_suite",
    "BenchmarkCase": "zephyr.intelligence.model_profiling.benchmark_suite",
    "CaseResult": "zephyr.intelligence.model_profiling.profiler",
    "ModelProfile": "zephyr.intelligence.model_profiling.profiler",
    "ModelProfiler": "zephyr.intelligence.model_profiling.profiler",
    "SKIP_MODEL_PATTERNS": "zephyr.intelligence.model_profiling.profiler",
    "MAX_OLLAMA_MODELS": "zephyr.intelligence.model_profiling.profiler",
    "ModelTaskEntry": "zephyr.intelligence.model_profiling.task_model_learner",
    "ModelTaskMatrix": "zephyr.intelligence.model_profiling.task_model_learner",
    "TaskRecommendation": "zephyr.intelligence.model_profiling.task_model_learner",
}


def __getattr__(name: str):
    import importlib

    if name in _SUBMODULES:
        mod = importlib.import_module(f"zephyr.intelligence.model_profiling.{name}")
        globals()[name] = mod
        return mod
    if name in _LAZY_SYMBOLS:
        mod = importlib.import_module(_LAZY_SYMBOLS[name])
        value = getattr(mod, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "ALL_BENCHMARK_CASES",
    "CATEGORY_MAP",
    "DEFAULT_OLLAMA_URL",
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
]
