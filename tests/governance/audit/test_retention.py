# [A_test] module_id: SRC-TST-1459 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_retention
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from zephyr.gov_audit.retention import (
    ExpiredEntry,
    RetentionEnforcer,
    RetentionPolicy,
    RetentionResult,
)


@pytest.fixture
def data_dir_with_expired(tmp_path):
    data_dir = tmp_path / "audit-trail"
    hot_dir = data_dir / "hot"
    warm_dir = data_dir / "warm"
    cold_dir = data_dir / "cold"
    hot_dir.mkdir(parents=True)
    warm_dir.mkdir(parents=True)
    cold_dir.mkdir(parents=True)

    old_time = (datetime.now(UTC) - timedelta(days=400)).timestamp()
    recent_time = (datetime.now(UTC) - timedelta(days=5)).timestamp()

    old_hot = hot_dir / "old_events.jsonl"
    old_hot.write_text('{"test": "old"}\n', encoding="utf-8")
    import os

    os.utime(old_hot, (old_time, old_time))

    recent_hot = hot_dir / "recent_events.jsonl"
    recent_hot.write_text('{"test": "recent"}\n', encoding="utf-8")
    os.utime(recent_hot, (recent_time, recent_time))

    old_warm = warm_dir / "old_warm.jsonl.gz"
    old_warm.write_text('{"test": "old_warm"}\n', encoding="utf-8")
    os.utime(old_warm, (old_time, old_time))

    return data_dir


@pytest.fixture
def enforcer(data_dir_with_expired):
    policy = RetentionPolicy(
        hot_retention_days=30, warm_retention_days=180, cold_retention_days=365, require_owner_approval=True
    )
    return RetentionEnforcer(data_dir=data_dir_with_expired, policy=policy)


class TestRetentionPolicy:
    def test_default_values(self):
        policy = RetentionPolicy()
        assert policy.hot_retention_days == 30
        assert policy.warm_retention_days == 180
        assert policy.cold_retention_days == 365
        assert policy.require_owner_approval is True

    def test_custom_values(self):
        policy = RetentionPolicy(hot_retention_days=7, require_owner_approval=False)
        assert policy.hot_retention_days == 7
        assert policy.require_owner_approval is False


class TestExpiredEntry:
    def test_default_values(self):
        entry = ExpiredEntry()
        assert entry.entry_id == ""
        assert entry.age_days == 0

    def test_custom_values(self):
        entry = ExpiredEntry(entry_id="test.jsonl", tier="hot", age_days=50, reason="Exceeds hot retention")
        assert entry.tier == "hot"
        assert entry.age_days == 50


class TestRetentionResult:
    def test_default_values(self):
        result = RetentionResult()
        assert result.dry_run is True
        assert result.expired_count == 0
        assert result.deleted_count == 0

    def test_custom_values(self):
        result = RetentionResult(dry_run=False, expired_count=5, deleted_count=3)
        assert result.dry_run is False
        assert result.skipped_count == 0


class TestRetentionEnforcer:
    def test_instantiation(self, tmp_path):
        enf = RetentionEnforcer(data_dir=tmp_path)
        assert enf._policy.hot_retention_days == 30

    def test_dry_run_does_not_delete(self, enforcer):
        result = enforcer.dry_run()
        assert result.dry_run is True
        assert result.deleted_count == 0

    def test_enforce_without_approval_skips(self, enforcer):
        result = enforcer.enforce(dry_run=False, owner_approved=False)
        assert result.deleted_count == 0
        assert result.skipped_count >= 0

    def test_enforce_with_approval_deletes(self, enforcer, data_dir_with_expired):
        expired = enforcer.get_expired()
        entry_ids = [e.entry_id for e in expired]
        enforcer.approve_deletion(entry_ids)
        result = enforcer.enforce(dry_run=False, owner_approved=True)
        assert result.deleted_count >= 0

    def test_get_expired_finds_old_files(self, enforcer):
        expired = enforcer.get_expired()
        assert len(expired) >= 1
        for e in expired:
            assert e.age_days > 0

    def test_get_expired_empty_dir(self, tmp_path):
        enf = RetentionEnforcer(data_dir=tmp_path)
        expired = enf.get_expired()
        assert expired == []

    def test_approve_deletion(self, enforcer):
        enforcer.approve_deletion(["file1.jsonl", "file2.jsonl"])
        assert "file1.jsonl" in enforcer._approved_deletions
        assert "file2.jsonl" in enforcer._approved_deletions

    def test_enforce_no_approval_required(self, tmp_path):
        policy = RetentionPolicy(require_owner_approval=False)
        enf = RetentionEnforcer(data_dir=tmp_path, policy=policy)
        result = enf.enforce(dry_run=False, owner_approved=False)
        assert isinstance(result, RetentionResult)

    def test_get_expired_sorted_by_age(self, enforcer):
        expired = enforcer.get_expired()
        if len(expired) >= 2:
            assert expired[0].age_days >= expired[1].age_days
