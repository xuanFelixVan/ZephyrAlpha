# [A_module] module_id=MOD-INF_model_capability_exam | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""[BLUEPRINT] MOD-INF-036 | docs/03_modules/_cross_layer/model_capability_exam/blueprint.md

# [MODULE] zephyr.infrastructure.model_capability_exam
# [TTL] permanent

[INVARIANTS] 蓝图 §4 文件清单与代码双向对齐

[MODIFY-GUARD] model_capability_exam/blueprint.md; model-capability-exam/__init__.py __all__

[CONSUMERS] 见蓝图 §4 接口契约

[STABILITY] evolving

[SAFETY] M

[AI_AUTONOMY] ai_modifiable

[ERROR_CONTRACT] ExamError

[TESTS] tests/test_model_capability_exam.py

ModelCapabilityExam — AI模型入职考试系统 (MOD-INF-036)

五维评测: 横轴(能力覆盖) / 纵轴(精度深度) / 速轴(延迟吞吐) / 幻轴(幻觉率) / 稳轴(长时间漂移)

产出: CapabilityPassport 能力护照 -> 驱动 TaskGate 任务门控

从 MOD-INF-034 (ModelProfiler) 提取为独立模块。

"""

from __future__ import annotations

_LAZY_SYMBOLS = {
    "BreadthResult": "zephyr.intelligence.model_profiling.capability_passport",
    "CapabilityPassport": "zephyr.intelligence.model_profiling.capability_passport",
    "DepthCapabilityResult": "zephyr.intelligence.model_profiling.capability_passport",
    "DepthResult": "zephyr.intelligence.model_profiling.capability_passport",
    "DriftResult": "zephyr.intelligence.model_profiling.capability_passport",
    "HallucinationResult": "zephyr.intelligence.model_profiling.capability_passport",
    "Recommendations": "zephyr.intelligence.model_profiling.capability_passport",
    "SpeedResult": "zephyr.intelligence.model_profiling.capability_passport",
    "compute_grade": "zephyr.intelligence.model_profiling.capability_passport",
    "ExamOrchestrator": "zephyr.intelligence.model_profiling.exam_orchestrator",
    "ALL_EXAM_CASES": "zephyr.intelligence.model_profiling.exam_test_cases",
    "CASES_BY_CAPABILITY": "zephyr.intelligence.model_profiling.exam_test_cases",
    "Difficulty": "zephyr.intelligence.model_profiling.exam_test_cases",
    "ExamTestCase": "zephyr.intelligence.model_profiling.exam_test_cases",
}

_LAZY_SUBMODULES = [
    "capability_passport",
    "exam_orchestrator",
    "exam_test_cases",
]


def __getattr__(name: str):
    import importlib

    if name in _LAZY_SUBMODULES:
        if name == "capability_passport":
            mod = importlib.import_module("zephyr.intelligence.model_profiling.capability_passport")
        elif name == "exam_orchestrator":
            mod = importlib.import_module("zephyr.intelligence.model_profiling.exam_orchestrator")
        elif name == "exam_test_cases":
            mod = importlib.import_module("zephyr.intelligence.model_profiling.exam_test_cases")
        else:
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
    "ALL_EXAM_CASES",
    "CASES_BY_CAPABILITY",
    "BreadthResult",
    "CapabilityPassport",
    "DepthCapabilityResult",
    "DepthResult",
    "Difficulty",
    "DriftResult",
    "ExamOrchestrator",
    "ExamTestCase",
    "HallucinationResult",
    "Recommendations",
    "SpeedResult",
    "capability_passport",
    "compute_grade",
    "exam_orchestrator",
    "exam_test_cases",
]
