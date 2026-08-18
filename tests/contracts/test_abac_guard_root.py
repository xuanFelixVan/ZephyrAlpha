# [A_test] module_id: MOD-GOV_abac_guard_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.guards.abac_guard
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

import time

from zephyr.security.access_control.guards.abac_guard import (
    SENSITIVITY_MIN_MATURITY,
    ABACContext,
    ABACGuard,
    SensitivityLabel,
    TemporalCategory,
    TLBRecord,
)
from zephyr.shared.contracts.identity.agent_identity import (
    AgentIdentity,
    AgentRole,
    IDESource,
    MaturityLevel,
)


def _make_agent(
    role=AgentRole.WRITER,
    maturity=MaturityLevel.L2_REGULAR,
    session_id="test-session-abac-001",
    **kwargs,
):
    return AgentIdentity(
        session_id=session_id,
        role=role,
        maturity=maturity,
        ide_source=IDESource.TRAE,
        **kwargs,
    )


def _make_context(
    intent="unknown",
    temporal=TemporalCategory.NORMAL,
    sensitivity=SensitivityLabel.INTERNAL,
    operation="read:docs",
):
    return ABACContext(
        intent=intent,
        temporal=temporal,
        sensitivity=sensitivity,
        operation=operation,
    )


class TestTemporalCategory:
    def test_enum_values(self):
        assert TemporalCategory.NORMAL.value == "normal"
        assert TemporalCategory.OFF_HOURS.value == "off_hours"
        assert TemporalCategory.LUNCH_PEAK.value == "lunch_peak"
        assert TemporalCategory.WEEKEND.value == "weekend"

    def test_enum_members_count(self):
        assert len(TemporalCategory) == 4


class TestSensitivityLabel:
    def test_enum_values(self):
        assert SensitivityLabel.PUBLIC.value == "public"
        assert SensitivityLabel.RESTRICTED.value == "restricted"

    def test_sensitivity_min_maturity_mapping(self):
        assert SENSITIVITY_MIN_MATURITY[SensitivityLabel.PUBLIC] == MaturityLevel.L0_INTERN
        assert SENSITIVITY_MIN_MATURITY[SensitivityLabel.RESTRICTED] == MaturityLevel.L4_PRINCIPAL


class TestABACContext:
    def test_default_values(self):
        ctx = ABACContext()
        assert ctx.intent == "unknown"
        assert ctx.temporal == TemporalCategory.NORMAL
        assert ctx.sensitivity == SensitivityLabel.INTERNAL
        assert ctx.operation == ""

    def test_custom_values(self):
        ctx = ABACContext(
            intent="deploy",
            temporal=TemporalCategory.OFF_HOURS,
            sensitivity=SensitivityLabel.HIGH,
            operation="deploy:production",
        )
        assert ctx.intent == "deploy"
        assert ctx.temporal == TemporalCategory.OFF_HOURS
        assert ctx.sensitivity == SensitivityLabel.HIGH
        assert ctx.operation == "deploy:production"


class TestTLBRecord:
    def test_default_values(self):
        rec = TLBRecord(agent_id="test")
        assert rec.counter == 0
        rec.limit == 100

    def test_custom_limit(self):
        rec = TLBRecord(agent_id="test", limit=500)
        assert rec.limit == 500


class TestABACGuardCheck:
    def test_normal_context_passes(self):
        guard = ABACGuard()
        agent = _make_agent(maturity=MaturityLevel.L2_REGULAR)
        ctx = _make_context(
            temporal=TemporalCategory.NORMAL,
            sensitivity=SensitivityLabel.INTERNAL,
            operation="read:docs",
        )
        ok, msg = guard.check(agent, ctx)
        assert ok is True

    def test_weekend_blocks_l0_intern(self):
        guard = ABACGuard()
        agent = _make_agent(maturity=MaturityLevel.L0_INTERN, session_id="intern-001")
        ctx = _make_context(
            temporal=TemporalCategory.WEEKEND,
            sensitivity=SensitivityLabel.PUBLIC,
            operation="read:docs",
        )
        ok, msg = guard.check(agent, ctx)
        assert ok is False
        assert "Weekend" in msg

    def test_weekend_allows_senior(self):
        guard = ABACGuard()
        agent = _make_agent(maturity=MaturityLevel.L3_SENIOR)
        ctx = _make_context(
            temporal=TemporalCategory.WEEKEND,
            sensitivity=SensitivityLabel.PUBLIC,
            operation="read:docs",
        )
        ok, msg = guard.check(agent, ctx)
        assert ok is True

    def test_off_hours_blocks_l0_intern(self):
        guard = ABACGuard()
        agent = _make_agent(maturity=MaturityLevel.L0_INTERN, session_id="intern-002")
        ctx = _make_context(
            temporal=TemporalCategory.OFF_HOURS,
            sensitivity=SensitivityLabel.PUBLIC,
            operation="read:docs",
        )
        ok, msg = guard.check(agent, ctx)
        assert ok is False
        assert "Off-hours" in msg

    def test_off_hours_blocks_destructive_for_junior(self):
        guard = ABACGuard()
        agent = _make_agent(maturity=MaturityLevel.L1_JUNIOR)
        ctx = _make_context(
            temporal=TemporalCategory.OFF_HOURS,
            sensitivity=SensitivityLabel.PUBLIC,
            operation="delete:temp_files",
        )
        ok, msg = guard.check(agent, ctx)
        assert ok is False
        assert "Destructive" in msg

    def test_lunch_peak_throttles_heavy_for_junior(self):
        guard = ABACGuard()
        agent = _make_agent(maturity=MaturityLevel.L1_JUNIOR)
        ctx = _make_context(
            temporal=TemporalCategory.LUNCH_PEAK,
            sensitivity=SensitivityLabel.PUBLIC,
            operation="batch:process",
        )
        ok, msg = guard.check(agent, ctx)
        assert ok is False
        assert "throttled" in msg.lower() or "Heavy" in msg


class TestABACGuardMaturity:
    def test_l0_intern_only_read(self):
        guard = ABACGuard()
        agent = _make_agent(maturity=MaturityLevel.L0_INTERN)
        ctx = _make_context(
            temporal=TemporalCategory.NORMAL,
            sensitivity=SensitivityLabel.PUBLIC,
            operation="write:src",
        )
        ok, msg = guard.check(agent, ctx)
        assert ok is False
        assert "Maturity" in msg

    def test_l4_principal_wildcard(self):
        guard = ABACGuard()
        agent = _make_agent(maturity=MaturityLevel.L4_PRINCIPAL)
        ctx = _make_context(
            temporal=TemporalCategory.NORMAL,
            sensitivity=SensitivityLabel.RESTRICTED,
            operation="anything:goes",
        )
        ok, msg = guard.check(agent, ctx)
        assert ok is True


class TestABACGuardSensitivity:
    def test_low_maturity_blocked_for_confidential(self):
        guard = ABACGuard()
        agent = _make_agent(maturity=MaturityLevel.L0_INTERN)
        ctx = _make_context(
            temporal=TemporalCategory.NORMAL,
            sensitivity=SensitivityLabel.CONFIDENTIAL,
            operation="read:docs",
        )
        ok, msg = guard.check(agent, ctx)
        assert ok is False
        assert "Sensitivity" in msg

    def test_high_maturity_allowed_for_confidential(self):
        guard = ABACGuard()
        agent = _make_agent(maturity=MaturityLevel.L2_REGULAR)
        ctx = _make_context(
            temporal=TemporalCategory.NORMAL,
            sensitivity=SensitivityLabel.CONFIDENTIAL,
            operation="read:docs",
        )
        ok, msg = guard.check(agent, ctx)
        assert ok is True


class TestABACGuardTLB:
    def test_tlb_within_limit(self):
        guard = ABACGuard()
        agent = _make_agent(maturity=MaturityLevel.L0_INTERN)
        ctx = _make_context(
            temporal=TemporalCategory.NORMAL,
            sensitivity=SensitivityLabel.PUBLIC,
            operation="read:docs",
        )
        ok, msg = guard.check(agent, ctx)
        assert ok is True

    def test_tlb_exceed_limit(self):
        guard = ABACGuard()
        agent = _make_agent(maturity=MaturityLevel.L0_INTERN, session_id="tlb-test")
        ctx = _make_context(
            temporal=TemporalCategory.NORMAL,
            sensitivity=SensitivityLabel.PUBLIC,
            operation="read:docs",
        )
        for _ in range(100):
            guard.check(agent, ctx)
        ok, msg = guard.check(agent, ctx)
        assert ok is False
        assert "TLB" in msg

    def test_reset_tlb(self):
        guard = ABACGuard()
        agent = _make_agent(maturity=MaturityLevel.L0_INTERN, session_id="tlb-reset")
        ctx = _make_context(
            temporal=TemporalCategory.NORMAL,
            sensitivity=SensitivityLabel.PUBLIC,
            operation="read:docs",
        )
        for _ in range(100):
            guard.check(agent, ctx)
        guard.reset_tlb("tlb-reset")
        ok, msg = guard.check(agent, ctx)
        assert ok is True

    def test_reset_all(self):
        guard = ABACGuard()
        agent = _make_agent(maturity=MaturityLevel.L0_INTERN, session_id="tlb-reset-all")
        ctx = _make_context(
            temporal=TemporalCategory.NORMAL,
            sensitivity=SensitivityLabel.PUBLIC,
            operation="read:docs",
        )
        for _ in range(100):
            guard.check(agent, ctx)
        guard.reset_all()
        ok, msg = guard.check(agent, ctx)
        assert ok is True


class TestABACGuardSensitivityBlitz:
    def test_not_blitz_initially(self):
        guard = ABACGuard()
        assert guard.is_sensitivity_label_blitz() is False

    def test_blitz_triggered(self):
        guard = ABACGuard()
        now = time.time()
        for i in range(5):
            guard.record_sensitivity_label_change(f"label_{i}", now)
        assert guard.is_sensitivity_label_blitz() is True

    def test_blitz_reset_after_window(self):
        guard = ABACGuard()
        old_ts = time.time() - 120
        for i in range(5):
            guard.record_sensitivity_label_change(f"label_{i}", old_ts)
        guard.record_sensitivity_label_change("new_label", time.time())
        assert guard.is_sensitivity_label_blitz() is False


class TestABACGuardClassifyTemporal:
    def test_weekend_saturday(self):
        saturday_morning = _make_local_timestamp(2026, 5, 23, 10, 0)
        result = ABACGuard.classify_temporal(saturday_morning)
        assert result == TemporalCategory.WEEKEND

    def test_weekend_sunday(self):
        sunday_afternoon = _make_local_timestamp(2026, 5, 24, 14, 0)
        result = ABACGuard.classify_temporal(sunday_afternoon)
        assert result == TemporalCategory.WEEKEND

    def test_off_hours_early_morning(self):
        early = _make_local_timestamp(2026, 5, 22, 5, 0)
        result = ABACGuard.classify_temporal(early)
        assert result == TemporalCategory.OFF_HOURS

    def test_off_hours_late_night(self):
        late = _make_local_timestamp(2026, 5, 22, 23, 0)
        result = ABACGuard.classify_temporal(late)
        assert result == TemporalCategory.OFF_HOURS

    def test_lunch_peak(self):
        lunch = _make_local_timestamp(2026, 5, 22, 12, 30)
        result = ABACGuard.classify_temporal(lunch)
        assert result == TemporalCategory.LUNCH_PEAK

    def test_normal_hours(self):
        normal = _make_local_timestamp(2026, 5, 22, 10, 0)
        result = ABACGuard.classify_temporal(normal)
        assert result == TemporalCategory.NORMAL


class TestABACGuardDetectSensitivity:
    def test_public_content(self):
        result = ABACGuard.detect_sensitivity_from_content("Hello world")
        assert result == SensitivityLabel.PUBLIC

    def test_password_content(self):
        result = ABACGuard.detect_sensitivity_from_content("The password is secret")
        assert result == SensitivityLabel.HIGH

    def test_api_key_content(self):
        result = ABACGuard.detect_sensitivity_from_content("api.key=abc123")
        assert result == SensitivityLabel.CONFIDENTIAL

    def test_top_secret_content(self):
        result = ABACGuard.detect_sensitivity_from_content("This is top secret information")
        assert result == SensitivityLabel.RESTRICTED

    def test_internal_content(self):
        result = ABACGuard.detect_sensitivity_from_content("This is an internal document")
        assert result == SensitivityLabel.INTERNAL

    def test_empty_content(self):
        result = ABACGuard.detect_sensitivity_from_content("")
        assert result == SensitivityLabel.PUBLIC


def _make_local_timestamp(year, month, day, hour, minute):
    return time.mktime(time.struct_time((year, month, day, hour, minute, 0, 0, 0, -1)))
