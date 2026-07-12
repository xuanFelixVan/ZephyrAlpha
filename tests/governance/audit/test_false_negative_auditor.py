# [A_test] module_id: SRC-TST-0894 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_false_negative_auditor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.false_negative_auditor import (
    FalseNegativeAuditor,
    FNAuditResult,
)


class TestFalseNegativeAuditor:
    def test_instantiation(self):
        auditor = FalseNegativeAuditor()
        assert auditor is not None

    def test_sweep_audit(self):
        auditor = FalseNegativeAuditor()
        result = auditor.sweep_audit([], [])
        assert isinstance(result, FNAuditResult)

    def test_canary_audit(self):
        auditor = FalseNegativeAuditor()
        result = auditor.canary_audit([])
        assert isinstance(result, FNAuditResult)

    def test_sampling_audit(self):
        auditor = FalseNegativeAuditor()
        result = auditor.sampling_audit(total_functions=100, previously_flagged=10)
        assert isinstance(result, FNAuditResult)

    def test_full_audit(self):
        auditor = FalseNegativeAuditor()
        result = auditor.full_audit([], [], [], 100)
        assert isinstance(result, dict)

    def test_sweep_audit_empty(self):
        auditor = FalseNegativeAuditor()
        result = auditor.sweep_audit([], [])
        assert isinstance(result, FNAuditResult)
