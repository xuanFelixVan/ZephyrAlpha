"""[BLUEPRINT] MOD-INF-036 | docs/03_modules/_cross_layer/model-capability-exam/blueprint.md


[MODULE] zephyr.model_capability_exam


[INVARIANTS] 蓝图 §4 文件清单与代码双向对齐


[MODIFY-GUARD] model-capability-exam/blueprint.md; model_capability_exam/__init__.py __all__


[CONSUMERS] 见蓝图 §4 接口契约


[STABILITY] evolving


[SAFETY] M


[AI_AUTONOMY] ai_modifiable


[ERROR_CONTRACT] ExamError


[TESTS] tests/model_capability_exam/





ModelCapabilityExam — AI模型入职考试系统 (MOD-INF-036)





五维评测: 横轴(能力覆盖) / 纵轴(精度深度) / 速轴(延迟吞吐) / 幻轴(幻觉率) / 稳轴(长时间漂移)


产出: CapabilityPassport 能力护照 → 驱动 TaskGate 任务门控





从 MOD-INF-034 (ModelProfiler) 提取为独立模块。


"""






from __future__ import annotations





from zephyr.model_capability_exam.capability_passport import (


    BreadthResult,


    CapabilityPassport,


    DepthCapabilityResult,


    DepthResult,


    DriftResult,


    HallucinationResult,


    Recommendations,


    SpeedResult,


    compute_grade,


)


from zephyr.model_capability_exam.exam_orchestrator import ExamOrchestrator


from zephyr.model_capability_exam.exam_test_cases import (


    ALL_EXAM_CASES,


    CASES_BY_CAPABILITY,


    Difficulty,


    ExamTestCase,


)





from zephyr.model_capability_exam.exam_test_cases import Difficulty, ExamTestCase





__all__ = [


    'compute_grade',


    'exam_test_cases',


    'ALL_EXAM_CASES',


    'BreadthResult',


    'CapabilityPassport',


    'CASES_BY_CAPABILITY',


    'DepthCapabilityResult',


    'DepthResult',


    'Difficulty',


    'DriftResult',


    'ExamOrchestrator',


    'ExamTestCase',


    'HallucinationResult',


    'Recommendations',


    'SpeedResult',
    'capability_passport',
    'exam_orchestrator',
]


