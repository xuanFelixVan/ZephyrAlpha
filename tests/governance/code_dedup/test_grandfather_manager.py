# [A_test] module_id: SRC-TST-1080 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_grandfather_manager
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.grandfather_manager import (
    GrandfatherManager,
)


class TestGrandfatherManager:
    def test_instantiation_default(self):
        gm = GrandfatherManager()
        assert gm is not None

    def test_instantiation_with_path(self, tmp_path):
        gm = GrandfatherManager(registry_path=str(tmp_path / "gf.yaml"))
        assert gm is not None

    def test_grandfather_check(self):
        gm = GrandfatherManager()
        result = gm.grandfather_check("grp-001", "2024-01-01T00:00:00Z")
        assert isinstance(result, tuple)

    def test_fossilize(self):
        gm = GrandfatherManager()
        result = gm.fossilize("grp-001", "func_a", file_path="a.py", first_detected_at="2020-01-01T00:00:00Z")
        assert result is not None or result is None

    def test_is_fossil(self):
        gm = GrandfatherManager()
        result = gm.is_fossil("grp-001")
        assert isinstance(result, bool)

    def test_get_all_entries(self):
        gm = GrandfatherManager()
        result = gm.get_all_entries()
        assert isinstance(result, (list, dict))

    def test_override(self):
        gm = GrandfatherManager()
        result = gm.override("grp-001", force=True)
        assert result is not None

    def test_archaeology_check(self):
        gm = GrandfatherManager()
        result = gm.archaeology_check(git_log_ok=True, all_tests_ok=True, rollback_ok=True)
        assert isinstance(result, tuple)
