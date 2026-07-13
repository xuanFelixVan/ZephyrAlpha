# [A_test] module_id: SRC-TST-0741 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_deployment_suppression
# [INVARIANTS] DeploymentSuppression state transitions must be deterministic
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound

import time
from unittest.mock import patch

from zephyr.feedback_loop.gates.deployment_suppression import (
    DeployGateState,
    DeploymentSuppression,
)


class TestDeployGateState:
    def test_enum_values(self):
        assert DeployGateState.OPEN == "OPEN"
        assert DeployGateState.BLOCKED_STABILITY == "BLOCKED_STABILITY"
        assert DeployGateState.BLOCKED_INCIDENT == "BLOCKED_INCIDENT"


class TestDeploymentSuppressionInstantiation:
    def test_default_values(self):
        ds = DeploymentSuppression()
        assert ds.sustain_window == 300.0
        assert ds.state == DeployGateState.OPEN
        assert ds.blocked_since == 0.0
        assert ds.stable_since is None
        assert ds.blocked_count == 0

    def test_custom_sustain_window(self):
        ds = DeploymentSuppression(sustain_window=60.0)
        assert ds.sustain_window == 60.0


class TestUpdateFromFleState:
    def test_nominal_state_stays_open(self):
        ds = DeploymentSuppression()
        result = ds.update_from_fle_state("NOMINAL")
        assert result == DeployGateState.OPEN

    def test_degraded_blocks_stability(self):
        ds = DeploymentSuppression()
        result = ds.update_from_fle_state("DEGRADED")
        assert result == DeployGateState.BLOCKED_STABILITY
        assert ds.blocked_count == 1

    def test_crisis_blocks_stability(self):
        ds = DeploymentSuppression()
        result = ds.update_from_fle_state("CRISIS")
        assert result == DeployGateState.BLOCKED_STABILITY

    def test_safe_mode_blocks_stability(self):
        ds = DeploymentSuppression()
        result = ds.update_from_fle_state("SAFE_MODE")
        assert result == DeployGateState.BLOCKED_STABILITY

    def test_ineffective_blocks_stability(self):
        ds = DeploymentSuppression()
        result = ds.update_from_fle_state("INEFFECTIVE")
        assert result == DeployGateState.BLOCKED_STABILITY

    def test_incident_active_blocks_incident(self):
        ds = DeploymentSuppression()
        result = ds.update_from_fle_state("INCIDENT_ACTIVE")
        assert result == DeployGateState.BLOCKED_INCIDENT

    def test_blocked_count_increments_only_on_transition_from_open(self):
        ds = DeploymentSuppression()
        ds.update_from_fle_state("DEGRADED")
        assert ds.blocked_count == 1
        ds.update_from_fle_state("CRISIS")
        assert ds.blocked_count == 1

    def test_recovery_after_sustain_window(self):
        ds = DeploymentSuppression(sustain_window=0.0)
        ds.update_from_fle_state("DEGRADED")
        now = time.time()
        with patch("zephyr.feedback_loop.gates.deployment_suppression.time") as mock_time:
            mock_time.time.return_value = now - 1.0
            ds.update_from_fle_state("NOMINAL")
        result = ds.update_from_fle_state("NOMINAL")
        assert result == DeployGateState.OPEN

    def test_stable_since_resets_on_degraded(self):
        ds = DeploymentSuppression()
        ds.update_from_fle_state("NOMINAL")
        assert ds.stable_since > 0.0
        ds.update_from_fle_state("DEGRADED")
        assert ds.stable_since is None


class TestIsDeployAllowed:
    def test_open_allows_deploy(self):
        ds = DeploymentSuppression()
        assert ds.is_deploy_allowed() is True

    def test_blocked_stability_disallows_deploy(self):
        ds = DeploymentSuppression()
        ds.update_from_fle_state("DEGRADED")
        assert ds.is_deploy_allowed() is False

    def test_blocked_incident_disallows_deploy(self):
        ds = DeploymentSuppression()
        ds.update_from_fle_state("INCIDENT_ACTIVE")
        assert ds.is_deploy_allowed() is False


class TestRemainingBlock:
    def test_open_returns_zero(self):
        ds = DeploymentSuppression()
        assert ds.remaining_block() == 0.0

    def test_blocked_without_stable_since_returns_999(self):
        ds = DeploymentSuppression()
        ds.update_from_fle_state("DEGRADED")
        assert ds.remaining_block() == 999.0

    def test_blocked_with_stable_since_returns_positive(self):
        ds = DeploymentSuppression(sustain_window=300.0)
        ds.update_from_fle_state("DEGRADED")
        ds.update_from_fle_state("NOMINAL")
        remaining = ds.remaining_block()
        assert remaining > 0.0
