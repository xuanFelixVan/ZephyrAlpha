# [A_test] module_id: SRC-TST-1593 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_shadow_verifier
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.shadow_verifier import (
    ShadowVerifier,
    ShadowVerifyResult,
)


class TestShadowVerifier:
    def test_instantiation(self):
        verifier = ShadowVerifier()
        assert verifier is not None

    def test_verify_size(self, tmp_path):
        verifier = ShadowVerifier()
        result = verifier.verify_size(str(tmp_path), str(tmp_path))
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_verify_semantic(self):
        verifier = ShadowVerifier()
        result = verifier.verify_semantic({"func_a"}, {"func_a", "func_b"})
        assert isinstance(result, tuple)
        assert len(result) == 2
        coverage = len({"func_a"} & {"func_a", "func_b"}) / len({"func_a", "func_b"})
        assert result[0] == (coverage >= 0.80)

    def test_generate_dashboard_card(self, tmp_path):
        verifier = ShadowVerifier()
        result = verifier.generate_dashboard_card(str(tmp_path), str(tmp_path), {"func_a"}, {"func_a"})
        assert isinstance(result, ShadowVerifyResult)

    def test_verify_size_nonexistent(self):
        verifier = ShadowVerifier()
        result = verifier.verify_size("nonexistent", "nonexistent")
        assert isinstance(result, tuple)
        assert result[0] is True

    def test_verify_semantic_empty(self):
        verifier = ShadowVerifier()
        result = verifier.verify_semantic(set(), set())
        assert result == (True, 1.0)
