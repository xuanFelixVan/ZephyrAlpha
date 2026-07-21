# [A_test] module_id: MOD-GOV_enhanced_security | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_enhanced_security
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""七项增强安全机制整合测试."""

from __future__ import annotations

from zephyr.security.access_control.agent_creation_policy import AgentCreationPolicy, CreationPolicy
from zephyr.security.access_control.auto_maintenance import AutoMaintenance
from zephyr.security.access_control.cache_invalidation import CacheInvalidation
from zephyr.security.access_control.detectors.cross_session_detector import CrossSessionDetector
from zephyr.security.access_control.emergency_override import EmergencyOverride
from zephyr.security.access_control.permission_hooks import PermissionHooks


class TestEnhancedSecurity:
    def test_cross_session_token_sign_and_verify(self):
        detector = CrossSessionDetector()
        token = detector.sign_token("agent_1", "session_abc")
        assert token.signature != ""

        result = detector.verify_token(token.agent_id, token.session_id, token.nonce, token.timestamp, token.signature)
        assert result["valid"] is True

    def test_cross_session_forgery_detected(self):
        detector = CrossSessionDetector()
        token = detector.sign_token("agent_1", "session_abc")
        result = detector.verify_token("agent_2", token.session_id, token.nonce, token.timestamp, token.signature)
        assert result["valid"] is False

    def test_permission_hooks_defaults_registered(self):
        hooks = PermissionHooks()
        hooks.register_defaults()
        pre_results = hooks.run(PermissionHooks.PRE_CHECK, agent_id="test")
        assert len(pre_results) == 3
        assert all("error" not in r for r in pre_results)

    def test_agent_creation_policy_decay(self):
        policy = AgentCreationPolicy()
        child_maturity = policy.get_child_maturity("PROVEN")
        assert child_maturity == "MATURE"

        child_caps = policy.get_child_capabilities(["read", "write", "execute", "delete"])
        assert len(child_caps) <= 3

    def test_spawn_storm_detection(self):
        policy = AgentCreationPolicy()
        cp = CreationPolicy(parent_agent_id="stormer", parent_maturity="MATURE", parent_capability_count=5)
        result = policy.can_create(cp)
        assert result["allowed"] is True

    def test_cache_invalidation_push(self):
        cache = CacheInvalidation()
        event = cache.push_invalidation("rule_001")
        assert event.processed is False

        result = cache.process(event.event_id)
        assert result["processed"] is True

    def test_emergency_override_issue_and_verify(self):
        override = EmergencyOverride()
        token = override.issue("bytebuddy", ["read", "write"])
        assert token.token_id.startswith("EMG-")

        result = override.verify(token.token_id)
        assert result["valid"] is True

    def test_emergency_override_one_time(self):
        override = EmergencyOverride()
        token = override.issue("bytebuddy", ["read"])
        override.verify(token.token_id)
        result = override.verify(token.token_id)
        assert result["valid"] is False

    def test_emergency_override_revoke(self):
        override = EmergencyOverride()
        token = override.issue("bytebuddy", ["read"])
        override.revoke(token.token_id)
        result = override.verify(token.token_id)
        assert result["valid"] is False

    def test_auto_maintenance_dashboard(self):
        maint = AutoMaintenance()
        maint.register_rule("rule_old")
        dashboard = maint.get_dashboard(denied_last_24h=5)
        assert dashboard.active_rules == 1
        assert isinstance(dashboard.complexity_pct, float)
