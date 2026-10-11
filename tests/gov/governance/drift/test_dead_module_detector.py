# [A_test] module_id: MOD-GOV_dead_module_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.test_dead_module_detector
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=TEST-MOD-INF-017-TEST_DEAD_MODULE_DETECTOR | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.dead_module_detector import DeadModuleDetector


class TestDeadModuleDetector:
    def test_instantiation(self):
        det = DeadModuleDetector()
        assert det is not None

    def test_detect_returns_list(self, tmp_path):
        det = DeadModuleDetector()
        result = det.detect(str(tmp_path), {})
        assert isinstance(result, list)

    def test_detect_empty_dir(self, tmp_path):
        det = DeadModuleDetector()
        result = det.detect(str(tmp_path), {})
        assert isinstance(result, list)
