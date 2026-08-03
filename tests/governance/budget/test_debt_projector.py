# [A_test] module_id: MOD-GOV_debt_projector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_debt_projector
# [DOMAIN] D_GOV_OPS_RESILIENCE
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
from zephyr.gov_code_quality.code_dedup.debt_projector import (
    DebtProjectionResult,
    DebtProjector,
)


class TestDebtProjector:
    def test_instantiation(self):
        proj = DebtProjector()
        assert proj is not None

    def test_project_returns_result(self):
        proj = DebtProjector()
        result = proj.project(current_debt_groups=10, intake_rate_groups_per_week=2.0, fix_rate_groups_per_week=1.0)
        assert isinstance(result, DebtProjectionResult)

    def test_project_zero_rates(self):
        proj = DebtProjector()
        result = proj.project(current_debt_groups=0, intake_rate_groups_per_week=0.0, fix_rate_groups_per_week=0.0)
        assert isinstance(result, DebtProjectionResult)

    def test_project_negative_values(self):
        proj = DebtProjector()
        result = proj.project(current_debt_groups=-1, intake_rate_groups_per_week=0.0, fix_rate_groups_per_week=0.0)
        assert isinstance(result, DebtProjectionResult)
