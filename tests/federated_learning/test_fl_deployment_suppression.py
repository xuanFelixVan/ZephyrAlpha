# [A_test] module_id: SRC-TST-0954 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_deployment_suppression
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.deployment_suppression
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_deployment_suppression.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.deployment_suppression import DeployGateState, DeploymentSuppression


class TestDeploymentSuppressionInstantiation:
    def test_default_construction(self):
        ds = DeploymentSuppression()
        assert ds.state == DeployGateState.OPEN
        assert ds.sustain_window == 300.0
        assert ds.blocked_count == 0


class TestUpdateFromFleState:
    def test_nominal_state_opens_gate(self):
        ds = DeploymentSuppression()
        ds.update_from_fle_state("DEGRADED")
        ds.update_from_fle_state("NOMINAL")
        assert ds.stable_since > 0.0

    def test_degraded_blocks(self):
        ds = DeploymentSuppression()
        result = ds.update_from_fle_state("DEGRADED")
        assert result == DeployGateState.BLOCKED_STABILITY
        assert ds.blocked_count == 1

    def test_crisis_blocks(self):
        ds = DeploymentSuppression()
        result = ds.update_from_fle_state("CRISIS")
        assert result == DeployGateState.BLOCKED_STABILITY

    def test_incident_active_blocks(self):
        ds = DeploymentSuppression()
        result = ds.update_from_fle_state("INCIDENT_ACTIVE")
        assert result == DeployGateState.BLOCKED_INCIDENT


class TestIsDeployAllowed:
    def test_deploy_allowed_when_open(self):
        ds = DeploymentSuppression()
        assert ds.is_deploy_allowed() is True

    def test_deploy_blocked_when_stability_blocked(self):
        ds = DeploymentSuppression()
        ds.update_from_fle_state("DEGRADED")
        assert ds.is_deploy_allowed() is False


class TestBoundaries:
    def test_sustain_window_zero(self):
        ds = DeploymentSuppression(sustain_window=0.0)
        ds.update_from_fle_state("DEGRADED")
        ds.update_from_fle_state("NOMINAL")
        assert ds.state == DeployGateState.OPEN

    def test_multiple_blocked_transitions_increment_count(self):
        ds = DeploymentSuppression(sustain_window=0.0)
        ds.update_from_fle_state("DEGRADED")
        ds.update_from_fle_state("NOMINAL")
        ds.update_from_fle_state("INEFFECTIVE")
        assert ds.blocked_count == 2
