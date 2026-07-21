# [A_test] module_id: MOD-GOV_escalation_fatigue_manager | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §tests
# [MODULE] zephyr.governance.escalation.escalation_fatigue_manager
# [INVARIANTS] 升级疲劳管理不可禁用;adaptive阈值不可手动覆盖
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md
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

from zephyr.governance.escalation.escalation_fatigue_manager import EscalationFatigueManager


class TestEscalationFatigueManagerInit:
    def test_instantiation_creates_empty_state(self):
        mgr = EscalationFatigueManager()
        assert isinstance(mgr._owner_escalations, dict)
        assert len(mgr._owner_escalations) == 0
        assert mgr._cooldown_h == 4
        assert mgr._max_daily == 6

    def test_instantiation_independent_instances(self):
        a = EscalationFatigueManager()
        b = EscalationFatigueManager()
        a.record_escalation("owner-1")
        assert "owner-1" not in b._owner_escalations


class TestRecordEscalation:
    def test_first_escalation_allowed(self):
        mgr = EscalationFatigueManager()
        assert mgr.record_escalation("owner-1") is True

    def test_records_timestamp(self):
        mgr = EscalationFatigueManager()
        before = time.time()
        mgr.record_escalation("owner-1")
        after = time.time()
        ts = mgr._owner_escalations["owner-1"][0]
        assert before <= ts <= after

    def test_cooldown_blocks_second_escalation(self):
        mgr = EscalationFatigueManager()
        assert mgr.record_escalation("owner-1") is True
        assert mgr.record_escalation("owner-1") is False

    def test_cooldown_allows_after_expiry(self):
        mgr = EscalationFatigueManager()
        now = time.time()
        mgr._owner_escalations["owner-1"] = [now - mgr._cooldown_h * 3600 - 1]
        assert mgr.record_escalation("owner-1") is True

    def test_daily_max_blocks_after_six(self):
        mgr = EscalationFatigueManager()
        now = time.time()
        old_ts = now - mgr._cooldown_h * 3600 - 1
        mgr._owner_escalations["owner-1"] = [old_ts] * mgr._max_daily
        assert mgr.record_escalation("owner-1") is False

    def test_daily_max_allows_sixth(self):
        mgr = EscalationFatigueManager()
        now = time.time()
        old_ts = now - mgr._cooldown_h * 3600 - 1
        mgr._owner_escalations["owner-1"] = [old_ts] * (mgr._max_daily - 1)
        assert mgr.record_escalation("owner-1") is True

    def test_independent_owners(self):
        mgr = EscalationFatigueManager()
        assert mgr.record_escalation("owner-A") is True
        assert mgr.record_escalation("owner-B") is True
        assert mgr.record_escalation("owner-A") is False
        assert mgr.record_escalation("owner-B") is False

    def test_stale_entries_not_counted(self):
        mgr = EscalationFatigueManager()
        now = time.time()
        stale = now - 86401
        mgr._owner_escalations["owner-1"] = [stale] * 10
        assert mgr.record_escalation("owner-1") is True


class TestRecordEscalationBoundary:
    def test_empty_string_owner_id(self):
        mgr = EscalationFatigueManager()
        assert mgr.record_escalation("") is True

    def test_none_owner_id_accepted(self):
        mgr = EscalationFatigueManager()
        assert mgr.record_escalation(None) is True

    def test_cooldown_boundary_exact(self):
        mgr = EscalationFatigueManager()
        now = time.time()
        mgr._owner_escalations["owner-1"] = [now - mgr._cooldown_h * 3600]
        assert mgr.record_escalation("owner-1") is True

    def test_daily_max_boundary_exact(self):
        mgr = EscalationFatigueManager()
        now = time.time()
        old_ts = now - mgr._cooldown_h * 3600 - 1
        mgr._owner_escalations["owner-1"] = [old_ts] * mgr._max_daily
        assert mgr.record_escalation("owner-1") is False

    def test_integer_owner_id_accepted(self):
        mgr = EscalationFatigueManager()
        assert mgr.record_escalation(123) is True
