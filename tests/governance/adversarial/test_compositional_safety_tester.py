# [A_test] module_id: SRC-TST-0558 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_compositional_safety_tester
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] must test all public classes and methods of compositional_safety_tester
# [MODIFY-GUARD] compositional_safety_tester.py changes require sync
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/test_compositional_safety_tester.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from zephyr.governance.security_governance.compositional_safety_tester import CompositionalSafetyTester


class TestCompositionalSafetyTester:
    def test_instantiation(self):
        tester = CompositionalSafetyTester()
        assert len(tester.INDIVIDUALLY_SAFE) == 3
        assert len(tester.DANGEROUS_COMBOS) == 2

    def test_test_composition_safe_single(self):
        tester = CompositionalSafetyTester()
        result = tester.test_composition({"read_config"})
        assert result == []

    def test_test_composition_dangerous_config_modification(self):
        tester = CompositionalSafetyTester()
        result = tester.test_composition({"read_config", "write_log"})
        assert "config_modification" in result

    def test_test_composition_dangerous_config_exfiltration(self):
        tester = CompositionalSafetyTester()
        result = tester.test_composition({"read_config", "send_metric"})
        assert "config_exfiltration" in result

    def test_test_composition_both_dangerous(self):
        tester = CompositionalSafetyTester()
        result = tester.test_composition({"read_config", "write_log", "send_metric"})
        assert "config_modification" in result
        assert "config_exfiltration" in result
        assert len(result) == 2

    def test_test_composition_empty(self):
        tester = CompositionalSafetyTester()
        result = tester.test_composition(set())
        assert result == []

    def test_test_composition_unrelated(self):
        tester = CompositionalSafetyTester()
        result = tester.test_composition({"write_log", "send_metric"})
        assert result == []

    def test_is_safe_combination_true(self):
        tester = CompositionalSafetyTester()
        assert tester.is_safe_combination({"read_config"}) is True

    def test_is_safe_combination_false(self):
        tester = CompositionalSafetyTester()
        assert tester.is_safe_combination({"read_config", "write_log"}) is False

    def test_is_safe_combination_empty(self):
        tester = CompositionalSafetyTester()
        assert tester.is_safe_combination(set()) is True
