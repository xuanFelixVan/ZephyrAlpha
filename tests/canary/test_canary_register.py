# [A_test] module_id: SRC-TST-0483 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_canary_register
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.canary_register import CanaryRegister


class TestCanaryRegister:
    def test_instantiation_default(self):
        cr = CanaryRegister()
        assert cr is not None

    def test_instantiation_with_path(self, tmp_path):
        cr = CanaryRegister(registry_path=str(tmp_path / "canary.yaml"))
        assert cr is not None

    def test_register(self, tmp_path):
        cr = CanaryRegister(registry_path=str(tmp_path / "canary.yaml"))
        cr.register("func_name", "module_path", stage="active")
        assert len(cr._canaries) == 1

    def test_check_staleness(self, tmp_path):
        cr = CanaryRegister(registry_path=str(tmp_path / "canary.yaml"))
        result = cr.check_staleness()
        assert isinstance(result, list)

    def test_register_empty(self, tmp_path):
        cr = CanaryRegister(registry_path=str(tmp_path / "canary.yaml"))
        cr.register("", "", stage="active")
        assert len(cr._canaries) == 1
