# [A_test] module_id: SRC-TST-0303 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infra_ops/capacity_assurance/blueprint.md | §test
# [MODULE] tests.test_ai_skill_monitor
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_ai_skill_monitor.py
# [TTL] task_bound

import pytest

mod = pytest.importorskip("zephyr.ops.capacity_assurance.ai_skill_monitor", reason="ai_skill_monitor not available")
AISkillMonitor = mod.AISkillMonitor
SkillDimension = mod.SkillDimension
SkillBaseline = mod.SkillBaseline


class TestAISkillMonitor:
    def test_instantiation(self):
        monitor = AISkillMonitor()
        assert len(monitor.baselines) == 4
        for dim in SkillDimension:
            assert dim in monitor.baselines

    def test_record_identical_values(self):
        monitor = AISkillMonitor()
        result = monitor.record(SkillDimension.ACCURACY, "task_1", "expected", "expected")
        assert result["score"] == 1.0
        assert result["degraded"] is False

    def test_record_different_strings(self):
        monitor = AISkillMonitor()
        result = monitor.record(SkillDimension.ROBUSTNESS, "task_2", "hello", "hallo")
        assert 0.0 < result["score"] < 1.0
        assert result["degraded"] is False

    def test_record_completely_different(self):
        monitor = AISkillMonitor()
        result = monitor.record(SkillDimension.EFFICIENCY, "task_3", 42, "different_type")
        assert result["score"] == 0.0
        assert result["degraded"] is True

    def test_record_empty_strings(self):
        monitor = AISkillMonitor()
        result = monitor.record(SkillDimension.FORMAT_COMPLIANCE, "task_4", "", "")
        assert result["score"] == 1.0

    def test_check_all(self):
        monitor = AISkillMonitor()
        monitor.record(SkillDimension.ACCURACY, "task_1", "a", "a")
        all_status = monitor.check_all()
        assert "accuracy" in all_status
        assert "robustness" in all_status
        assert all_status["accuracy"]["current_score"] == 1.0

    def test_degradation_threshold(self):
        assert AISkillMonitor.DEGRADATION_THRESHOLD == 0.5


class TestSkillDimension:
    def test_all_dimensions(self):
        dims = {d.value for d in SkillDimension}
        assert dims == {"accuracy", "robustness", "efficiency", "format_compliance"}


class TestSkillBaseline:
    def test_instantiation(self):
        bl = SkillBaseline(dimension=SkillDimension.ACCURACY, baseline_score=1.0, current_score=0.8)
        assert bl.degraded is False
        assert bl.last_checked > 0
