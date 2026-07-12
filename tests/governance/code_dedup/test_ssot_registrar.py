# [A_test] module_id: SRC-TST-1675 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_ssot_registrar
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.ssot_registrar import SSOTRegistrar


class TestSSOTRegistrar:
    def test_instantiation_default(self):
        reg = SSOTRegistrar()
        assert reg is not None

    def test_instantiation_with_path(self, tmp_path):
        reg = SSOTRegistrar(manifest_path=str(tmp_path / "manifest.yaml"))
        assert reg is not None

    def test_register(self, tmp_path):
        reg = SSOTRegistrar(manifest_path=str(tmp_path / "manifest.yaml"))
        result = reg.register("func_a", "module_a", signature="(x) -> int", caller_count=3)
        assert isinstance(result, dict)

    def test_register_empty(self, tmp_path):
        reg = SSOTRegistrar(manifest_path=str(tmp_path / "manifest.yaml"))
        result = reg.register("", "", signature="", caller_count=0)
        assert isinstance(result, dict)
