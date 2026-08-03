# [A_test] module_id: MOD-GOV_stale_shared_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_stale_shared_detector
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.stale_shared_detector import StaleSharedDetector


class TestStaleSharedDetector:
    def test_instantiation(self):
        det = StaleSharedDetector()
        assert det is not None

    def test_detect_returns_list(self):
        det = StaleSharedDetector()
        result = det.detect([])
        assert isinstance(result, list)

    def test_detect_with_stale_function(self):
        det = StaleSharedDetector()
        funcs = [{"name": "old_func", "caller_count": 0, "last_used_at": "2020-01-01T00:00:00Z"}]
        result = det.detect(funcs)
        assert "old_func" in result

    def test_detect_with_active_function(self):
        det = StaleSharedDetector()
        funcs = [{"name": "active_func", "caller_count": 5, "last_used_at": "2020-01-01T00:00:00Z"}]
        result = det.detect(funcs)
        assert "active_func" not in result

    def test_detect_empty_input(self):
        det = StaleSharedDetector()
        result = det.detect([])
        assert result == []
