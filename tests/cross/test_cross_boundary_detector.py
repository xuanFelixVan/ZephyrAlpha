# [A_test] module_id: SRC-TST-0641 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_cross_boundary_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.cross_boundary_detector import (
    Boundary,
    CrossBoundaryClone,
    CrossBoundaryDetector,
)


class TestCrossBoundaryDetector:
    def test_instantiation(self):
        det = CrossBoundaryDetector()
        assert det is not None

    def test_detect_returns_clone(self):
        det = CrossBoundaryDetector()
        result = det.detect("src/a.py", "tests/test_a.py", "func_a", "func_a", 0.95, Boundary.SRC_TEST_BRIDGE)
        assert isinstance(result, CrossBoundaryClone)

    def test_detect_empty_paths(self):
        det = CrossBoundaryDetector()
        result = det.detect("", "", "", "", 0.0, Boundary.SRC_TEST_BRIDGE)
        assert isinstance(result, CrossBoundaryClone)


class TestCrossBoundaryClone:
    def test_can_auto_fix(self):
        clone = CrossBoundaryClone(
            src_path="s",
            dst_path="d",
            src_func="f",
            dst_func="f",
            similarity=0.96,
            boundary=Boundary.CROSS_LAYER_REDUNDANCY,
        )
        assert isinstance(clone.can_auto_fix, bool)
