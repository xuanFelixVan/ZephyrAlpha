# [A_test] module_id: MOD-GOV_skill_hardening | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-683 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_skill_hardening
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""生产硬化测试 —— 并发安全 + 边界条件"""

import threading
import time

from zephyr.autonomy_core.skills.skill_calibration import SkillCalibration
from zephyr.autonomy_core.skills.skill_consensus import SkillConsensus
from zephyr.autonomy_core.skills.skill_di import SkillDI
from zephyr.autonomy_core.skills.skill_feature_flags import SkillFeatureFlags
from zephyr.autonomy_core.skills.skill_idempotency import SkillIdempotency
from zephyr.autonomy_core.skills.skill_kill_switch import SkillKillSwitch
from zephyr.autonomy_core.skills.skill_lineage import SkillLineage
from zephyr.autonomy_core.skills.skill_locking import SkillLock
from zephyr.autonomy_core.skills.skill_prompt_cache import SkillPromptCache
from zephyr.autonomy_core.skills.skill_resilience import SkillResilience
from zephyr.autonomy_core.skills.skill_schema_registry import SkillSchemaRegistry
from zephyr.autonomy_core.skills.skill_temperature import SkillTemperature


class TestConcurrencySafety:
    def test_lock_acquire_release(self):
        with SkillLock.write_lock("TEST-LOCK-001"):
            assert "w:TEST-LOCK-001" in SkillLock._LOCKS
        lock = SkillLock._LOCKS.get("w:TEST-LOCK-001")
        if lock:
            assert not lock._is_owned()

    def test_read_lock_nonblocking(self):
        results = []

        def reader():
            with SkillLock.read_lock("TEST-READ-001"):
                results.append("read_done")

        t1 = threading.Thread(target=reader)
        t2 = threading.Thread(target=reader)
        t1.start()
        t2.start()
        t1.join(timeout=5)
        t2.join(timeout=5)
        assert len(results) == 2

    def test_registry_lock_exclusive(self):
        acquired = []

        def worker():
            with SkillLock.registry_lock():
                acquired.append("start")
                time.sleep(0.1)
                acquired.append("end")

        t = threading.Thread(target=worker)
        t.start()
        t.join(timeout=5)
        assert acquired == ["start", "end"]


class TestCalibrationEdgeCases:
    def test_drift_trend_insufficient_data(self):
        SkillCalibration.clear_history("TEST-CAL")
        trend = SkillCalibration.drift_trend("TEST-CAL")
        assert trend["samples"] == 0
        assert trend["avg_drift"] == 0.0

    def test_calibration_with_perfect_accuracy(self):
        result = SkillCalibration.calibrate("TEST-CAL", 0.95, 0.95)
        assert result["drift"] == 0.0
        assert result["calibrated"] is True
        assert result["overconfident"] is False

    def test_calibration_overconfidence_detected(self):
        SkillCalibration.clear_history("TEST-OC")
        for _ in range(6):
            SkillCalibration.calibrate("TEST-OC", 0.95, 0.60)
        check = SkillCalibration.should_recalibrate("TEST-OC")
        assert check["should_recalibrate"] is True


class TestConsensusEdgeCases:
    def test_unanimous_vote(self):
        winner, result = SkillConsensus.majority_vote(["opt-a", "opt-b"], {"a1": "opt-a", "a2": "opt-a", "a3": "opt-a"})
        assert winner == "opt-a"
        assert not result.tie_broken

    def test_weighted_tiebreak(self):
        winner, result = SkillConsensus.majority_vote(
            ["a", "b"], {"v1": "a", "v2": "b"}, weights={"v1": 2.0, "v2": 1.0}
        )
        assert winner == "a"

    def test_empty_vote_returns_none(self):
        winner, result = SkillConsensus.majority_vote(["a", "b"], {})
        assert winner is None


class TestIdempotencyDuplicateDetection:
    def test_hash_consistency(self):
        h1 = SkillIdempotency.hash_input("test data")
        h2 = SkillIdempotency.hash_input("test data")
        assert h1 == h2

    def test_different_inputs_different_hash(self):
        h1 = SkillIdempotency.hash_input("data A")
        h2 = SkillIdempotency.hash_input("data B")
        assert h1 != h2

    def test_clear_expired(self):
        SkillIdempotency.clear_all()
        SkillIdempotency.is_duplicate("TEST-DUP", "hash-001")
        assert SkillIdempotency.stats()["active_entries"] >= 1


class TestFeatureFlagsEnvOverride:
    def test_get_predefined_flag(self):
        val = SkillFeatureFlags.get_flag("TEST-FF", "strict_mode")
        assert val is True

    def test_set_and_get_custom_flag(self):
        SkillFeatureFlags.set_flag("TEST-FF", "custom_flag", True)
        assert SkillFeatureFlags.get_flag("TEST-FF", "custom_flag") is True
        SkillFeatureFlags.reset_skill("TEST-FF")


class TestKillSwitchAuto:
    def test_auto_kill_triggered(self):
        SkillKillSwitch.clear_all()
        result = SkillKillSwitch.auto_kill_on_errors("TEST-KILL", 5)
        assert result is not None
        assert result["action"] == "killed"
        assert SkillKillSwitch.is_killed("TEST-KILL") is True

    def test_no_kill_below_threshold(self):
        SkillKillSwitch.clear_all()
        result = SkillKillSwitch.auto_kill_on_errors("TEST-KILL-2", 1)
        assert result is None

    def test_revive_works(self):
        SkillKillSwitch.kill("TEST-REVIVE", "test")
        SkillKillSwitch.revive("TEST-REVIVE")
        assert SkillKillSwitch.is_killed("TEST-REVIVE") is False


class TestResilienceCircuitBreaker:
    def test_record_failure_increments(self):
        SkillResilience.reset("TEST-CB")
        count = SkillResilience.record_failure("TEST-CB")
        assert count == 1
        count = SkillResilience.record_failure("TEST-CB")
        assert count == 2

    def test_record_success_resets(self):
        SkillResilience.reset("TEST-CB2")
        SkillResilience.record_failure("TEST-CB2")
        SkillResilience.record_failure("TEST-CB2")
        SkillResilience.record_success("TEST-CB2")
        assert SkillResilience._failure_count.get("TEST-CB2", 0) == 0

    def test_retry_success_on_first(self):
        SkillResilience.reset("TEST-RETRY")
        result, attempts = SkillResilience.retry_with_backoff("TEST-RETRY", lambda: "ok", max_retries=3)
        assert result == "ok"
        assert attempts == 1


class TestSchemaRegistry:
    def test_validate_missing_required(self):
        SkillSchemaRegistry.register(
            "TEST-SCHEMA", input_schema={"name": {"required": True, "type": "str"}}, output_schema={}
        )
        result = SkillSchemaRegistry.validate_input("TEST-SCHEMA", {})
        assert result["valid"] is False
        assert len(result["errors"]) == 1

    def test_validate_type_mismatch(self):
        SkillSchemaRegistry.register("TEST-SCHEMA2", input_schema={"count": {"type": "int"}}, output_schema={})
        result = SkillSchemaRegistry.validate_input("TEST-SCHEMA2", {"count": "not_int"})
        assert result["valid"] is False


class TestPromptCache:
    def test_set_and_get(self):
        SkillPromptCache.set("TEST-CACHE", "hash-1", "cached response")
        val = SkillPromptCache.get("TEST-CACHE", "hash-1")
        assert val == "cached response"

    def test_invalidate_skill(self):
        SkillPromptCache.set("TEST-CACHE2", "h1", "resp1")
        SkillPromptCache.set("TEST-CACHE2", "h2", "resp2")
        SkillPromptCache.invalidate("TEST-CACHE2")
        assert SkillPromptCache.get("TEST-CACHE2", "h1") is None


class TestLineage:
    def test_latest_returns_last(self):
        ln = SkillLineage()
        ln.record_version("TEST-LIN", "v1.0", None, "init")
        ln.record_version("TEST-LIN", "v1.1", "v1.0", "patch")
        latest = ln.latest("TEST-LIN")
        assert latest["version"] == "v1.1"

    def test_diff_between_versions(self):
        ln = SkillLineage()
        ln.record_version("TEST-LIN2", "v1", None, "initial")
        ln.record_version("TEST-LIN2", "v2", "v1", "added tests")
        diff = ln.diff("TEST-LIN2", "v1", "v2")
        assert diff["found"] is True


class TestDependencyInjection:
    def test_topological_order(self):
        SkillDI.clear()
        SkillDI.register("A", {"B": "defaultB"})
        SkillDI.register("B", {})
        order = SkillDI.topological_order(["A", "B"])
        assert order.index("B") < order.index("A")

    def test_inject_fills_defaults(self):
        SkillDI.clear()
        SkillDI.register("MAIN", {"HELPER": "fallback"})
        SkillDI.register("HELPER", {"default": "helper_value"})
        result = SkillDI.inject("MAIN", {"MAIN": "main_value"})
        assert "HELPER" in result


class TestTemperature:
    def test_code_generation_low_temp(self):
        temp = SkillTemperature.get_temperature("TEST-TEMP", "code_generation")
        assert temp < 0.5

    def test_brainstorm_high_temp(self):
        temp = SkillTemperature.get_temperature("TEST-TEMP", "brainstorm")
        assert temp > 0.5

    def test_adaptive_low_confidence_boosts(self):
        SkillTemperature.set_override("TEST-ADAPT", 0.3)
        t = SkillTemperature.adaptive("TEST-ADAPT", 0.3)
        assert t > 0.3
        SkillTemperature.remove_override("TEST-ADAPT")
