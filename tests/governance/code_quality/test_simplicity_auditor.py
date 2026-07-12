# [A_test] module_id: SRC-TST-1602 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_simplicity_auditor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.simplicity_auditor import (
    SimplicityAuditor,
    SimplicityReport,
)


class TestSimplicityAuditor:
    def test_instantiation(self):
        auditor = SimplicityAuditor()
        assert auditor is not None

    def test_audit(self):
        auditor = SimplicityAuditor()
        result = auditor.audit(engine_line_count=1000, bugs_found=2, false_positives_last_30d=5)
        assert isinstance(result, SimplicityReport)

    def test_audit_empty(self):
        auditor = SimplicityAuditor()
        result = auditor.audit()
        assert isinstance(result, SimplicityReport)
