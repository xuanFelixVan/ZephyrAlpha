# [A_test] module_id: MOD-GOV_abac_guard_agent_rbac | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_abac_guard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
测试 L2 ABACGuard — 五维属性权限判定
"""

import time

from zephyr.security.access_control.guards.abac_guard import (
    SENSITIVITY_MIN_MATURITY,
    ABACContext,
    ABACGuard,
    SensitivityLabel,
    TemporalCategory,
)
from zephyr.security.access_control.identity import AgentIdentity, MaturityLevel


class TestTemporalClassification:
    def test_classify_normal_hours(self):
        cat = ABACGuard.classify_temporal(time.mktime((2026, 5, 7, 10, 0, 0, 3, 127, -1)))
        assert cat == TemporalCategory.NORMAL

    def test_classify_off_hours(self):
        cat = ABACGuard.classify_temporal(time.mktime((2026, 5, 7, 23, 0, 0, 3, 127, -1)))
        assert cat == TemporalCategory.OFF_HOURS

    def test_classify_lunch_peak(self):
        cat = ABACGuard.classify_temporal(time.mktime((2026, 5, 7, 12, 30, 0, 3, 127, -1)))
        assert cat == TemporalCategory.LUNCH_PEAK

    def test_classify_weekend(self):
        cat = ABACGuard.classify_temporal(time.mktime((2026, 5, 9, 10, 0, 0, 5, 129, -1)))
        assert cat == TemporalCategory.WEEKEND


class TestMaturityAccess:
    def test_l0_only_read(self):
        guard = ABACGuard()
        agent = AgentIdentity(session_id="l0-test", maturity=MaturityLevel.L0_INTERN)
        ctx = ABACContext(operation="read:docs", temporal=TemporalCategory.NORMAL, sensitivity=SensitivityLabel.PUBLIC)
        ok, msg = guard.check(agent, ctx)
        assert ok

    def test_l0_cannot_write(self):
        guard = ABACGuard()
        agent = AgentIdentity(session_id="l0-test", maturity=MaturityLevel.L0_INTERN)
        ctx = ABACContext(operation="write:src", temporal=TemporalCategory.NORMAL, sensitivity=SensitivityLabel.PUBLIC)
        ok, msg = guard.check(agent, ctx)
        assert not ok

    def test_l4_full_access(self):
        guard = ABACGuard()
        agent = AgentIdentity(session_id="l4-test", maturity=MaturityLevel.L4_PRINCIPAL)
        ctx = ABACContext(operation="delete:audit_logs", temporal=TemporalCategory.NORMAL)
        ok, msg = guard.check(agent, ctx)
        assert ok


class TestOffHoursBlocking:
    def test_l0_off_hours_blocked(self):
        guard = ABACGuard()
        agent = AgentIdentity(session_id="l0-test", maturity=MaturityLevel.L0_INTERN)
        ctx = ABACContext(operation="read:docs", temporal=TemporalCategory.OFF_HOURS)
        ok, msg = guard.check(agent, ctx)
        assert not ok

    def test_l2_off_hours_destructive_blocked(self):
        guard = ABACGuard()
        agent = AgentIdentity(session_id="l2-test", maturity=MaturityLevel.L2_REGULAR)
        ctx = ABACContext(operation="delete:file", temporal=TemporalCategory.OFF_HOURS)
        ok, msg = guard.check(agent, ctx)
        assert not ok

    def test_l2_off_hours_read_allowed(self):
        guard = ABACGuard()
        agent = AgentIdentity(session_id="l2-test", maturity=MaturityLevel.L2_REGULAR)
        ctx = ABACContext(operation="read:docs", temporal=TemporalCategory.OFF_HOURS)
        ok, msg = guard.check(agent, ctx)
        assert ok


class TestSensitivity:
    def test_l0_cannot_access_high_sensitivity(self):
        guard = ABACGuard()
        agent = AgentIdentity(session_id="l0-test", maturity=MaturityLevel.L0_INTERN)
        ctx = ABACContext(
            operation="read:docs",
            temporal=TemporalCategory.NORMAL,
            sensitivity=SensitivityLabel.HIGH,
        )
        ok, msg = guard.check(agent, ctx)
        assert not ok

    def test_l3_can_access_high_sensitivity(self):
        guard = ABACGuard()
        agent = AgentIdentity(session_id="l3-test", maturity=MaturityLevel.L3_SENIOR)
        ctx = ABACContext(
            operation="read:docs",
            temporal=TemporalCategory.NORMAL,
            sensitivity=SensitivityLabel.HIGH,
        )
        ok, msg = guard.check(agent, ctx)
        assert ok

    def test_sensitivity_labels_range(self):
        assert SensitivityLabel.PUBLIC in SENSITIVITY_MIN_MATURITY
        assert SensitivityLabel.RESTRICTED in SENSITIVITY_MIN_MATURITY


class TestTLB:
    def test_tlb_under_limit(self):
        guard = ABACGuard()
        agent = AgentIdentity(session_id="tlb-test-1", maturity=MaturityLevel.L1_JUNIOR)
        ctx = ABACContext(operation="read:docs", temporal=TemporalCategory.NORMAL, sensitivity=SensitivityLabel.PUBLIC)
        ok = True
        for _ in range(50):
            ok, _ = guard.check(agent, ctx)
        assert ok

    def test_reset_tlb(self):
        guard = ABACGuard()
        agent = AgentIdentity(session_id="tlb-reset", maturity=MaturityLevel.L1_JUNIOR)
        ctx = ABACContext(operation="read:docs", sensitivity=SensitivityLabel.PUBLIC)
        for _ in range(50):
            guard.check(agent, ctx)
        guard.reset_tlb("tlb-reset")
        ok, _ = guard.check(agent, ctx)
        assert ok


class TestSensitivityLabelBlitz:
    def test_blitz_detection(self):
        guard = ABACGuard()
        for i in range(6):
            guard.record_sensitivity_label_change(f"label_{i}")
        assert guard.is_sensitivity_label_blitz()

    def test_no_blitz_under_threshold(self):
        guard = ABACGuard()
        for i in range(3):
            guard.record_sensitivity_label_change(f"label_{i}")
        assert not guard.is_sensitivity_label_blitz()

    def test_reset_all(self):
        guard = ABACGuard()
        guard.record_sensitivity_label_change("test")
        guard.reset_all()
        assert not guard.is_sensitivity_label_blitz()


class TestSensitivityDetection:
    def test_detect_high_sensitivity(self):
        label = ABACGuard.detect_sensitivity_from_content("This file contains a secret_key")
        assert label in (SensitivityLabel.HIGH, SensitivityLabel.CONFIDENTIAL)

    def test_detect_public_content(self):
        label = ABACGuard.detect_sensitivity_from_content("Hello world, this is a test")
        assert label == SensitivityLabel.PUBLIC
