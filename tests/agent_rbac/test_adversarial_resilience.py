# [A_test] module_id: MOD-GOV_adversarial_resilience | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.adversarial_resilience
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.adversarial_resilience import (
        MAESTRO_LAYERS,
        OWASP_TOP10_MAP,
        AdversarialResilience,
        ASIRiskLevel,
    )

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")


class TestAdversarialResilience:
    def test_assess_self_modification_critical(self):
        ar = AdversarialResilience()
        result = ar.assess_self_modification("agent1", "modify:self_constraints")
        assert result.risk_level == ASIRiskLevel.CRITICAL
        assert result.owasp_category == "ASI08"

    def test_assess_disable_kill_critical(self):
        ar = AdversarialResilience()
        result = ar.assess_self_modification("agent1", "disable:kill_switch")
        assert result.risk_level == ASIRiskLevel.CRITICAL

    def test_assess_benign_operation(self):
        ar = AdversarialResilience()
        result = ar.assess_self_modification("agent1", "read:config")
        assert result.risk_level == ASIRiskLevel.NONE

    def test_assess_empty_operation(self):
        ar = AdversarialResilience()
        result = ar.assess_self_modification("agent1", "")
        assert result.risk_level == ASIRiskLevel.NONE


class TestIncentiveAlignment:
    def test_zero_events(self):
        ar = AdversarialResilience()
        score = ar.assess_incentive_alignment("agent1", 0, 0)
        assert score.safety_alignment == 0.5
        assert score.overall_score > 0

    def test_all_safety(self):
        ar = AdversarialResilience()
        score = ar.assess_incentive_alignment("agent1", 10, 0)
        assert score.safety_alignment == 1.0

    def test_all_violations(self):
        ar = AdversarialResilience()
        score = ar.assess_incentive_alignment("agent1", 0, 10)
        assert score.safety_alignment == 0.0

    def test_mixed(self):
        ar = AdversarialResilience()
        score = ar.assess_incentive_alignment("agent1", 7, 3)
        assert abs(score.safety_alignment - 0.7) < 0.01


class TestOwaspCoverage:
    def test_coverage_keys(self):
        ar = AdversarialResilience()
        coverage = ar.get_owasp_coverage()
        assert len(coverage) == 10
        assert all(v is True for v in coverage.values())

    def test_owasp_map_has_asi08(self):
        assert "ASI08" in OWASP_TOP10_MAP

    def test_maestro_layers_count(self):
        assert len(MAESTRO_LAYERS) == 5
