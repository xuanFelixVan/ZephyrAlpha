# [A_test] module_id: SRC-TST-0709 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_dead_module_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
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
