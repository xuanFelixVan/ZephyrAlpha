# [A_module] module_id=MOD-INF-034 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模型发现 请求
#   fields: 本地 Ollama 模型清单 + 远程 API 模型清单
#   code: ModelDiscovery().discover_all() L27
# - id: I2
#   name: 单模型评测 请求
#   fields: 模型名（如 qwen3:8b）
#   code: profiler.quick_profile("qwen3:8b") L32
# 层: 算法
# - id: A1
#   name_zh: ① 模型自动发现
#   name_en: ModelDiscovery.discover_all
#   intro: 扫描本地Ollama和远程API，列出全部可用模型
#   desc: 返回 DiscoveredModel(name, source, size_gb) 列表（docstring L26-28）
#   inputs: I1
#   outputs: 可用模型清单
# - id: A2
#   name_zh: ② 7维26项基准评测
#   name_en: ModelProfiler.quick_profile / profile_ollama_only
#   intro: 对模型跑标准化benchmark，算综合评分与延迟
#   desc: 跑 ALL_BENCHMARK_CASES（7维度26项）→ ModelProfile(average_score, latency_p50_ms)（L17-19, L31-37）
#   inputs: I2 A1
#   outputs: ModelProfile 评测结果
# - id: A3
#   name_zh: ③ 结果排名与写库
#   name_en: print_ranking / results_writer.write_benchmark_results
#   intro: 生成性能排名和最佳模型推荐，结果落盘
#   desc: print_ranking 打印排名；write_benchmark_results 写入 data/model_profiles/（L37-41）
#   inputs: A2
#   outputs: 排名结果 + registry 文件
# - id: A4
#   name_zh: ④ 子模块懒加载导出
#   name_en: __getattr__ importlib 懒加载
#   intro: 10个子模块按需import，避免包导入时全量加载
#   desc: __getattr__ 命中 _SUBMODULES 即 importlib.import_module 并缓存到 globals（L58-65）
#   inputs: I1
#   outputs: 子模块符号（benchmark_suite/profiler/model_discovery 等）
# 层: 输出
# - id: O1
#   name_zh: 模型评测公共API与评测结果
#   name_en: ModelProfiler/ModelDiscovery + ModelProfile
#   intro: 对外暴露模型发现、基准评测、能力护照等能力
#   downstream: MOD-INF-009 / MOD-INF-036（# [CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A4
# I2 --> A2
# A1 --> A2
# A2 --> A3
# A3 --> O1
# A4 --> O1
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
    "case_assembler",
    "exam_executor",
    "exam_judge",
    "exam_rubric",
    "job_matcher",
]
