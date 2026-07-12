# [A_test] module_id: SRC-TST-0423 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_behavioral_trust_checker
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.behavioral_trust_checker import (
    BehavioralTrustChecker,
    TrustCheck,
)


class TestBehavioralTrustChecker:
    def test_instantiation(self):
        checker = BehavioralTrustChecker()
        assert checker is not None

    def test_register(self):
        checker = BehavioralTrustChecker()
        checker.register("func_a", "return_type=int;params=1")
        assert "func_a" in checker._signatures

    def test_verify(self):
        checker = BehavioralTrustChecker()
        checker.register("func_a", "return_type=int;params=1")
        result = checker.verify("func_a", "return_type=int;params=1")
        assert isinstance(result, TrustCheck)

    def test_verify_unknown_function(self):
        checker = BehavioralTrustChecker()
        result = checker.verify("nonexistent", "sig")
        assert isinstance(result, TrustCheck)

    def test_register_empty_name(self):
        checker = BehavioralTrustChecker()
        checker.register("", "")
        assert "" in checker._signatures
