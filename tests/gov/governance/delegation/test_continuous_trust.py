# [A_test] module_id: MOD-GOV_continuous_trust | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_continuous_trust
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] ContinuousTrust ledger_dir must be temp; score clamped [-1.0, 1.0]; tier 0/1/2
# [MODIFY-GUARD] blueprint.md §4
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.AssertionError on invariant violation
# [TESTS] this file
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.governance.intelligence_governance.continuous_trust import (
    ContinuousTrust,
    TrustEntry,
    TrustScore,
    TrustTierPerms,
)


@pytest.fixture
def tmp_ledger(tmp_path: Path) -> ContinuousTrust:
    return ContinuousTrust(ledger_dir=tmp_path / "trust")


class TestTrustEntry:
    def test_creation(self):
        entry = TrustEntry(
            entry_id="TRUST-001",
            timestamp_utc="2026-01-01T00:00:00+00:00",
            trust_delta=0.1,
            reason="test",
            operation="rollback",
        )
        assert entry.entry_id == "TRUST-001"
        assert entry.trust_delta == 0.1
        assert entry.commit_sha == ""
        assert entry.execution_id == ""

    def test_creation_with_optional_fields(self):
        entry = TrustEntry(
            entry_id="TRUST-002",
            timestamp_utc="2026-01-01T00:00:00+00:00",
            trust_delta=-0.1,
            reason="fail",
            operation="rollback",
            commit_sha="abc123",
            execution_id="exec-001",
        )
        assert entry.commit_sha == "abc123"
        assert entry.execution_id == "exec-001"


class TestTrustScore:
    def test_from_ledger_empty(self):
        score = TrustScore.from_ledger([])
        assert score.score == 0.5
        assert score.tier == 1
        assert score.total_entries == 0
        assert score.positive_deltas == 0
        assert score.negative_deltas == 0

    def test_from_ledger_positive_events(self):
        entries = [
            TrustEntry("E1", "2026-01-01T00:00:00+00:00", 0.1, "ok", "rb"),
            TrustEntry("E2", "2026-01-01T00:01:00+00:00", 0.1, "ok", "rb"),
            TrustEntry("E3", "2026-01-01T00:02:00+00:00", 0.1, "ok", "rb"),
            TrustEntry("E4", "2026-01-01T00:03:00+00:00", 0.15, "recovery", "rb"),
        ]
        score = TrustScore.from_ledger(entries)
        assert score.score == 0.5 + 0.1 + 0.1 + 0.1 + 0.15
        assert score.tier == 2
        assert score.positive_deltas == 4
        assert score.negative_deltas == 0

    def test_from_ledger_negative_events_tier0(self):
        entries = [
            TrustEntry("E1", "2026-01-01T00:00:00+00:00", -0.3, "critical", "rb"),
            TrustEntry("E2", "2026-01-01T00:01:00+00:00", -0.3, "critical", "rb"),
            TrustEntry("E3", "2026-01-01T00:02:00+00:00", -0.3, "critical", "rb"),
        ]
        score = TrustScore.from_ledger(entries)
        assert score.score <= -0.3
        assert score.tier == 0
        assert score.negative_deltas == 3

    def test_from_ledger_score_clamped_upper(self):
        entries = [TrustEntry(f"E{i}", "2026-01-01T00:00:00+00:00", 0.1, "ok", "rb") for i in range(20)]
        score = TrustScore.from_ledger(entries)
        assert score.score <= 1.0

    def test_from_ledger_score_clamped_lower(self):
        entries = [TrustEntry(f"E{i}", "2026-01-01T00:00:00+00:00", -0.3, "crit", "rb") for i in range(20)]
        score = TrustScore.from_ledger(entries)
        assert score.score >= -1.0

    def test_from_ledger_last_updated(self):
        entries = [
            TrustEntry("E1", "2026-01-01T00:00:00+00:00", 0.1, "ok", "rb"),
            TrustEntry("E2", "2026-01-01T00:05:00+00:00", 0.1, "ok", "rb"),
        ]
        score = TrustScore.from_ledger(entries)
        assert score.last_updated == "2026-01-01T00:05:00+00:00"


class TestTrustTierPerms:
    def test_tier2_permissions(self):
        perms = TrustTierPerms.from_tier(2)
        assert perms.can_auto_revert is True
        assert perms.can_propose_rollback is True
        assert perms.can_discard_uncommitted is True
        assert perms.can_read_state is True
        assert perms.needs_human_approval is False

    def test_tier1_permissions(self):
        perms = TrustTierPerms.from_tier(1)
        assert perms.can_auto_revert is False
        assert perms.can_propose_rollback is True
        assert perms.needs_human_approval is True

    def test_tier0_permissions(self):
        perms = TrustTierPerms.from_tier(0)
        assert perms.can_auto_revert is False
        assert perms.can_propose_rollback is False
        assert perms.can_discard_uncommitted is False
        assert perms.can_read_state is True
        assert perms.needs_human_approval is True

    def test_default_dataclass(self):
        perms = TrustTierPerms(tier=5)
        assert perms.can_auto_revert is False
        assert perms.can_read_state is True
        assert perms.needs_human_approval is True


class TestContinuousTrust:
    def test_instantiation_default(self):
        ct = ContinuousTrust()
        assert ct.ledger_dir == Path("data/rollback/trust")

    def test_instantiation_custom_dir(self, tmp_path: Path):
        ct = ContinuousTrust(ledger_dir=tmp_path / "custom")
        assert ct.ledger_dir == tmp_path / "custom"

    def test_record_trust_event(self, tmp_ledger: ContinuousTrust):
        entry = tmp_ledger.record_trust_event(0.1, "test reason", "rollback")
        assert entry.trust_delta == 0.1
        assert entry.reason == "test reason"
        assert entry.operation == "rollback"
        assert entry.entry_id.startswith("TRUST-")

    def test_successful_rollback(self, tmp_ledger: ContinuousTrust):
        entry = tmp_ledger.successful_rollback("rollback", "sha1")
        assert entry.trust_delta == ContinuousTrust.POSITIVE_DELTA
        assert "Successful" in entry.reason
        assert entry.commit_sha == "sha1"

    def test_failed_rollback(self, tmp_ledger: ContinuousTrust):
        entry = tmp_ledger.failed_rollback("rollback", "sha2")
        assert entry.trust_delta == ContinuousTrust.NEGATIVE_DELTA
        assert "Failed" in entry.reason

    def test_critical_failure(self, tmp_ledger: ContinuousTrust):
        entry = tmp_ledger.critical_failure("rollback", "system crash")
        assert entry.trust_delta == ContinuousTrust.CRITICAL_FAILURE_DELTA
        assert "CRITICAL" in entry.reason

    def test_false_positive_trigger(self, tmp_ledger: ContinuousTrust):
        entry = tmp_ledger.false_positive_trigger()
        assert entry.trust_delta == ContinuousTrust.FALSE_POSITIVE_DELTA
        assert entry.operation == "false_positive"

    def test_successful_recovery(self, tmp_ledger: ContinuousTrust):
        entry = tmp_ledger.successful_recovery("recovery")
        assert entry.trust_delta == ContinuousTrust.SUCCESSFUL_RECOVERY_DELTA
        assert "recovery" in entry.reason

    def test_get_score_empty(self, tmp_ledger: ContinuousTrust):
        score = tmp_ledger.get_score()
        assert score.score == 0.5
        assert score.tier == 1
        assert score.total_entries == 0

    def test_get_score_after_events(self, tmp_ledger: ContinuousTrust):
        tmp_ledger.successful_rollback()
        tmp_ledger.successful_rollback()
        score = tmp_ledger.get_score()
        assert score.score == 0.7
        assert score.positive_deltas == 2

    def test_get_permissions(self, tmp_ledger: ContinuousTrust):
        perms = tmp_ledger.get_permissions()
        assert isinstance(perms, TrustTierPerms)
        assert perms.tier == 1

    def test_can_auto_revert_default(self, tmp_ledger: ContinuousTrust):
        assert tmp_ledger.can_auto_revert() is False

    def test_can_auto_revert_high_trust(self, tmp_ledger: ContinuousTrust):
        for _ in range(10):
            tmp_ledger.successful_rollback()
        assert tmp_ledger.can_auto_revert() is True

    def test_needs_human_approval_default(self, tmp_ledger: ContinuousTrust):
        assert tmp_ledger.needs_human_approval() is True

    def test_needs_human_approval_high_trust(self, tmp_ledger: ContinuousTrust):
        for _ in range(10):
            tmp_ledger.successful_rollback()
        assert tmp_ledger.needs_human_approval() is False

    def test_trust_ledger_summary(self, tmp_ledger: ContinuousTrust):
        tmp_ledger.successful_rollback()
        summary = tmp_ledger.trust_ledger_summary()
        assert "trust-score" in summary
        assert "tier" in summary
        assert "risk_coverage" in summary
        assert len(summary["risk_coverage"]) == 6

    def test_ledger_persists_to_disk(self, tmp_ledger: ContinuousTrust, tmp_path: Path):
        tmp_ledger.record_trust_event(0.1, "persist test", "rollback")
        ledger_path = tmp_path / "trust" / "continuous_trust_ledger.jsonl"
        assert ledger_path.exists()
        lines = ledger_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["trust_delta"] == 0.1

    def test_score_persists_to_disk(self, tmp_ledger: ContinuousTrust, tmp_path: Path):
        tmp_ledger.record_trust_event(0.1, "score persist", "rollback")
        score_path = tmp_path / "trust" / "trust-score.json"
        assert score_path.exists()
        data = json.loads(score_path.read_text(encoding="utf-8"))
        assert "score" in data
        assert "tier" in data

    def test_corrupted_score_file_falls_back(self, tmp_ledger: ContinuousTrust, tmp_path: Path):
        tmp_ledger.record_trust_event(0.1, "before corruption", "rollback")
        score_path = tmp_path / "trust" / "trust-score.json"
        score_path.write_text("{invalid json", encoding="utf-8")
        score = tmp_ledger.get_score()
        assert isinstance(score, TrustScore)

    def test_multiple_events_accumulate(self, tmp_ledger: ContinuousTrust):
        tmp_ledger.successful_rollback()
        tmp_ledger.failed_rollback()
        tmp_ledger.critical_failure("rb", "crash")
        score = tmp_ledger.get_score()
        expected = 0.5 + 0.1 - 0.1 - 0.3
        assert score.score == round(expected, 4)
        assert score.positive_deltas == 1
        assert score.negative_deltas == 2
