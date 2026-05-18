# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.test_code_dedup_engine.test_degradation_edge
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""降级边缘场景测试 — Stage 失败后系统行为."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def test_degradation_stage_failure():
    from zephyr.l01_infrastructure.code_dedup_engine.degradation import DegradationManager, DegradationLevel
    dm = DegradationManager()

    def always_fail():
        raise RuntimeError("Simulated failure")

    result = dm.run_stage("test_stage", always_fail, on_degrade=DegradationLevel.STAGE1_ONLY)
    assert not result.success
    assert "Simulated failure" in result.error

    report = dm.get_report()
    assert report.level == DegradationLevel.STAGE1_ONLY


def test_degradation_pipeline():
    from zephyr.l01_infrastructure.code_dedup_engine.degradation import DegradationManager
    from zephyr.l01_infrastructure.code_dedup_engine.exit_codes import ExitCode
    dm = DegradationManager()

    stages = [
        ("stage_ok", lambda: 42, None),
    ]
    report = dm.run_pipeline(stages)
    assert report.exit_code == ExitCode.PASS
    assert len(report.stages) == 1
    assert report.stages[0].success
