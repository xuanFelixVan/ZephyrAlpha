# [A_test] module_id: MOD-GOV_atomic_fixer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_atomic_fixer
# [DOMAIN] D_GOV_CODE_QUALITY
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
from zephyr.gov_code_quality.code_dedup.atomic_fixer import (
    AtomicFixer,
    FixPlan,
    FixStep,
)


class TestAtomicFixer:
    def test_instantiation_default(self):
        fixer = AtomicFixer()
        assert fixer is not None

    def test_instantiation_with_root(self, tmp_path):
        fixer = AtomicFixer(project_root=str(tmp_path))
        assert fixer is not None

    def test_preflight_returns_fix_plan(self, tmp_path):
        fixer = AtomicFixer(project_root=str(tmp_path))
        steps = [FixStep(step=1, action="replace", file="a.py")]
        result = fixer.preflight("dup-001", steps)
        assert isinstance(result, FixPlan)
        assert result.dup_id == "dup-001"

    def test_apply_returns_tuple(self, tmp_path):
        fixer = AtomicFixer(project_root=str(tmp_path))
        steps = [FixStep(step=1, action="replace", file="a.py")]
        plan = fixer.preflight("dup-001", steps)
        result = fixer.apply(plan)
        assert isinstance(result, tuple)

    def test_recover_returns_bool(self, tmp_path):
        fixer = AtomicFixer(project_root=str(tmp_path))
        result = fixer.recover("nonexistent-hash")
        assert isinstance(result, bool)

    def test_scan_and_recover_all(self, tmp_path):
        fixer = AtomicFixer(project_root=str(tmp_path))
        result = fixer.scan_and_recover_all()
        assert isinstance(result, list)
