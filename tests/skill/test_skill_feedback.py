# [A_test] module_id: MOD-GOV_skill_feedback | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_feedback
# [INVARIANTS] _MAX_HISTORY=100; _CONSECUTIVE_FAILURE_KILL=3
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_skill_feedback.py -q
# [TTL] task_bound

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import patch

from zephyr.autonomy_core.skills.skill_feedback import FeedbackSignal, SkillFeedback


@dataclass
class FakeModuleResult:
    status: str = "SUCCESS"
    errors: list = None
    module_id: str = "MOD-TEST-001"
    raw_output: dict = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.raw_output is None:
            self.raw_output = {}


class TestFeedbackSignalInstantiation:
    def test_create_signal(self):
        sig = FeedbackSignal(
            skill_id="SKILL-TEST",
            module_id="MOD-TEST",
            task_id="TASK-001",
            success=True,
            error_count=0,
            latency_ms=100,
            tokens_used=50,
            cost_usd=0.01,
        )
        assert sig.skill_id == "SKILL-TEST"
        assert sig.success is True

    def test_to_dict(self):
        sig = FeedbackSignal(
            skill_id="SKILL-TEST",
            module_id="MOD-TEST",
            task_id="TASK-001",
            success=True,
            error_count=0,
            latency_ms=100,
            tokens_used=50,
            cost_usd=0.01,
        )
        d = sig.to_dict()
        assert d["skill_id"] == "SKILL-TEST"
        assert d["success"] is True
        assert "timestamp" in d

    def test_default_timestamp(self):
        sig = FeedbackSignal(
            skill_id="S",
            module_id="M",
            task_id="T",
            success=True,
            error_count=0,
            latency_ms=0,
            tokens_used=0,
            cost_usd=0.0,
        )
        assert sig.timestamp > 0


class TestSkillFeedbackInstantiation:
    def test_create_instance(self):
        with patch.object(SkillFeedback, "_load_history"):
            sf = SkillFeedback()
        assert isinstance(sf, SkillFeedback)

    def test_has_history(self):
        with patch.object(SkillFeedback, "_load_history"):
            sf = SkillFeedback()
        assert isinstance(sf._history, list)

    def test_has_consecutive_failures(self):
        with patch.object(SkillFeedback, "_load_history"):
            sf = SkillFeedback()
        assert isinstance(sf._consecutive_failures, dict)


class TestRecordModuleResult:
    def test_success_result(self):
        with patch.object(SkillFeedback, "_load_history"):
            sf = SkillFeedback()
        with patch.object(sf, "_boost_freshness", return_value={"action": "freshness_boost"}):
            with patch.object(sf, "_append_signal_to_log"):
                result = sf.record_module_result(
                    skill_id="SKILL-SUCC",
                    module_result=FakeModuleResult(status="SUCCESS"),
                    task_id="TASK-001",
                )
        assert result["success"] is True
        assert result["skill_id"] == "SKILL-SUCC"
        assert result["signal"]["success"] is True

    def test_failure_result(self):
        with patch.object(SkillFeedback, "_load_history"):
            sf = SkillFeedback()
        with patch.object(sf, "_decay_freshness", return_value={"action": "freshness_decay"}):
            with patch.object(sf, "_check_auto_kill", return_value=None):
                with patch.object(sf, "_append_signal_to_log"):
                    result = sf.record_module_result(
                        skill_id="SKILL-FAIL",
                        module_result=FakeModuleResult(status="FAILURE", errors=["err1"]),
                        task_id="TASK-002",
                    )
        assert result["success"] is False
        assert result["signal"]["error_count"] == 1

    def test_raw_output_extracted(self):
        mod = FakeModuleResult(
            status="SUCCESS",
            raw_output={"tokens_used": 100, "cost_usd": 0.05, "latency_ms": 200},
        )
        with patch.object(SkillFeedback, "_load_history"):
            sf = SkillFeedback()
        with patch.object(sf, "_boost_freshness", return_value={"action": "boost"}):
            with patch.object(sf, "_append_signal_to_log"):
                result = sf.record_module_result("SKILL-RAW", mod, "TASK-003")
        assert result["signal"]["tokens_used"] == 100
        assert result["signal"]["cost_usd"] == 0.05
        assert result["signal"]["latency_ms"] == 200

    def test_none_raw_output(self):
        mod = FakeModuleResult(status="SUCCESS", raw_output=None)
        with patch.object(SkillFeedback, "_load_history"):
            sf = SkillFeedback()
        with patch.object(sf, "_boost_freshness", return_value={"action": "boost"}):
            with patch.object(sf, "_append_signal_to_log"):
                result = sf.record_module_result("SKILL-NONE-RAW", mod, "TASK-004")
        assert result["signal"]["tokens_used"] == 0
        assert result["signal"]["cost_usd"] == 0.0

    def test_history_capped_at_max(self):
        with patch.object(SkillFeedback, "_load_history"):
            sf = SkillFeedback()
        sf._MAX_HISTORY = 5
        with patch.object(sf, "_boost_freshness", return_value={"action": "boost"}):
            with patch.object(sf, "_append_signal_to_log"):
                for i in range(10):
                    sf.record_module_result(
                        "SKILL-CAP",
                        FakeModuleResult(status="SUCCESS"),
                        f"TASK-{i}",
                    )
        assert len(sf._history) <= 5


class TestGetHistory:
    def test_get_all_history(self):
        with patch.object(SkillFeedback, "_load_history"):
            sf = SkillFeedback()
        with patch.object(sf, "_boost_freshness", return_value={"action": "boost"}):
            with patch.object(sf, "_append_signal_to_log"):
                sf.record_module_result("SKILL-A", FakeModuleResult(), "T1")
                sf.record_module_result("SKILL-B", FakeModuleResult(), "T2")
        history = sf.get_history()
        assert len(history) == 2

    def test_get_history_filtered_by_skill(self):
        with patch.object(SkillFeedback, "_load_history"):
            sf = SkillFeedback()
        with patch.object(sf, "_boost_freshness", return_value={"action": "boost"}):
            with patch.object(sf, "_append_signal_to_log"):
                sf.record_module_result("SKILL-A", FakeModuleResult(), "T1")
                sf.record_module_result("SKILL-B", FakeModuleResult(), "T2")
        history = sf.get_history(skill_id="SKILL-A")
        assert all(h["skill_id"] == "SKILL-A" for h in history)

    def test_get_history_with_limit(self):
        with patch.object(SkillFeedback, "_load_history"):
            sf = SkillFeedback()
        with patch.object(sf, "_boost_freshness", return_value={"action": "boost"}):
            with patch.object(sf, "_append_signal_to_log"):
                for i in range(5):
                    sf.record_module_result("SKILL-LIM", FakeModuleResult(), f"T{i}")
        history = sf.get_history(limit=2)
        assert len(history) == 2

    def test_empty_history(self):
        with patch.object(SkillFeedback, "_load_history"):
            sf = SkillFeedback()
        history = sf.get_history()
        assert history == []


class TestStats:
    def test_stats_with_data(self):
        with patch.object(SkillFeedback, "_load_history"):
            sf = SkillFeedback()
        with patch.object(sf, "_boost_freshness", return_value={"action": "boost"}):
            with patch.object(sf, "_decay_freshness", return_value={"action": "decay"}):
                with patch.object(sf, "_check_auto_kill", return_value=None):
                    with patch.object(sf, "_append_signal_to_log"):
                        sf.record_module_result(
                            "SKILL-STAT",
                            FakeModuleResult(
                                status="SUCCESS", raw_output={"latency_ms": 100, "cost_usd": 0.01, "tokens_used": 50}
                            ),
                            "T1",
                        )
                        sf.record_module_result(
                            "SKILL-STAT",
                            FakeModuleResult(
                                status="FAILURE", raw_output={"latency_ms": 200, "cost_usd": 0.02, "tokens_used": 100}
                            ),
                            "T2",
                        )
        stats = sf.stats("SKILL-STAT")
        assert stats["total_signals"] == 2
        assert stats["success_rate"] == 0.5

    def test_stats_empty(self):
        with patch.object(SkillFeedback, "_load_history"):
            sf = SkillFeedback()
        stats = sf.stats()
        assert stats["total_signals"] == 0

    def test_stats_filtered_by_skill(self):
        with patch.object(SkillFeedback, "_load_history"):
            sf = SkillFeedback()
        with patch.object(sf, "_boost_freshness", return_value={"action": "boost"}):
            with patch.object(sf, "_append_signal_to_log"):
                sf.record_module_result("SKILL-X", FakeModuleResult(), "T1")
                sf.record_module_result("SKILL-Y", FakeModuleResult(), "T2")
        stats = sf.stats("SKILL-X")
        assert stats["total_signals"] == 1


class TestOnSuccessReset:
    def test_resets_consecutive_failures(self):
        with patch.object(SkillFeedback, "_load_history"):
            sf = SkillFeedback()
        sf._consecutive_failures["SKILL-RESET"] = 2
        sf.on_success_reset("SKILL-RESET")
        assert "SKILL-RESET" not in sf._consecutive_failures

    def test_reset_nonexistent_no_error(self):
        with patch.object(SkillFeedback, "_load_history"):
            sf = SkillFeedback()
        sf.on_success_reset("SKILL-NONEXIST")
