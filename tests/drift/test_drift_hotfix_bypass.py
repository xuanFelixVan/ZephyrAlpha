# [A_test] module_id: SRC-TST-0777 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_drift_hotfix_bypass
# [INVARIANTS] 旁路必须72h自动过期
# [MODIFY-GUARD] src/zephyr/behavioral-auditor/drift_hotfix_bypass.py
# [CONSUMERS] CI pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip
# [TESTS] python -m pytest tests/test_drift_hotfix_bypass.py -q
# [TTL] task_bound

from __future__ import annotations

import json
import os
import uuid
from datetime import UTC, datetime, timedelta

from zephyr.gov_drift.drift_hotfix_bypass import (
    HOTFIX_PREFIXES,
    SUPPRESSION_TTL_HOURS,
    HotfixAuditEntry,
    HotfixBypass,
)


class TestConstants:
    def test_hotfix_prefixes(self):
        assert isinstance(HOTFIX_PREFIXES, tuple)
        assert len(HOTFIX_PREFIXES) > 0
        for prefix in HOTFIX_PREFIXES:
            assert prefix.startswith("[")

    def test_suppression_ttl(self):
        assert SUPPRESSION_TTL_HOURS == 72


class TestHotfixAuditEntry:
    def test_creation(self):
        entry_id = uuid.uuid4()
        entry = HotfixAuditEntry(
            entry_id=entry_id,
            commit_hash="abc123",
            module_ids=["mod_a"],
            dimensions=["dim_x"],
        )
        assert entry.entry_id == entry_id
        assert entry.commit_hash == "abc123"
        assert entry.module_ids == ["mod_a"]
        assert entry.dimensions == ["dim_x"]
        assert entry.owner_ack == ""
        assert entry.timestamp is None
        assert entry.suppressed_until is None

    def test_custom_values(self):
        now = datetime.now(UTC)
        until = now + timedelta(hours=72)
        entry = HotfixAuditEntry(
            entry_id=uuid.uuid4(),
            commit_hash="def456",
            module_ids=["mod_b"],
            dimensions=["dim_y"],
            owner_ack="owner1",
            timestamp=now,
            suppressed_until=until,
        )
        assert entry.owner_ack == "owner1"
        assert entry.timestamp == now
        assert entry.suppressed_until == until


class TestHotfixBypass:
    def test_init_with_custom_root(self, tmp_path):
        bypass = HotfixBypass(project_root=str(tmp_path))
        assert bypass._project_root == str(tmp_path)
        assert os.path.isdir(bypass._audit_dir)

    def test_is_hotfix_commit_hotfix(self, tmp_path):
        bypass = HotfixBypass(project_root=str(tmp_path))
        assert bypass.is_hotfix_commit("[HOTFIX] fix critical bug")

    def test_is_hotfix_commit_emergency(self, tmp_path):
        bypass = HotfixBypass(project_root=str(tmp_path))
        assert bypass.is_hotfix_commit("[EMERGENCY] urgent fix")

    def test_is_hotfix_commit_normal(self, tmp_path):
        bypass = HotfixBypass(project_root=str(tmp_path))
        assert not bypass.is_hotfix_commit("fix: normal bug")

    def test_is_hotfix_commit_case_insensitive(self, tmp_path):
        bypass = HotfixBypass(project_root=str(tmp_path))
        assert bypass.is_hotfix_commit("[hotfix] lowercase prefix")

    def test_is_hotfix_commit_empty_string(self, tmp_path):
        bypass = HotfixBypass(project_root=str(tmp_path))
        assert not bypass.is_hotfix_commit("")

    def test_is_hotfix_commit_whitespace_only(self, tmp_path):
        bypass = HotfixBypass(project_root=str(tmp_path))
        assert not bypass.is_hotfix_commit("   ")

    def test_process_hotfix_creates_entry(self, tmp_path):
        bypass = HotfixBypass(project_root=str(tmp_path))
        entry = bypass.process_hotfix(
            commit_hash="abc123",
            commit_message="[HOTFIX] fix",
            module_ids=["mod_a"],
            affected_dimensions=["dim_x"],
            owner_ack="owner1",
        )
        assert isinstance(entry, HotfixAuditEntry)
        assert entry.commit_hash == "abc123"
        assert entry.module_ids == ["mod_a"]
        assert entry.owner_ack == "owner1"
        assert entry.timestamp is not None
        assert entry.suppressed_until is not None

    def test_process_hotfix_suppression_ttl(self, tmp_path):
        bypass = HotfixBypass(project_root=str(tmp_path))
        entry = bypass.process_hotfix(
            commit_hash="abc123",
            commit_message="[HOTFIX] fix",
            module_ids=["mod_a"],
            affected_dimensions=["dim_x"],
        )
        delta = entry.suppressed_until - entry.timestamp
        assert abs(delta.total_seconds() - SUPPRESSION_TTL_HOURS * 3600) < 5

    def test_process_hotfix_writes_audit_log(self, tmp_path):
        bypass = HotfixBypass(project_root=str(tmp_path))
        bypass._core_writer = None
        bypass.process_hotfix(
            commit_hash="abc123",
            commit_message="[HOTFIX] fix",
            module_ids=["mod_a"],
            affected_dimensions=["dim_x"],
        )
        log_path = bypass._audit_log_path
        assert os.path.exists(log_path)
        with open(log_path, encoding="utf-8") as f:
            line = f.readline().strip()
            record = json.loads(line)
            assert record["commit_hash"] == "abc123"

    def test_is_suppressed_active(self, tmp_path):
        bypass = HotfixBypass(project_root=str(tmp_path))
        bypass.process_hotfix(
            commit_hash="abc123",
            commit_message="[HOTFIX] fix",
            module_ids=["mod_a"],
            affected_dimensions=["dim_x"],
        )
        assert bypass.is_suppressed("abc123")

    def test_is_suppressed_not_found(self, tmp_path):
        bypass = HotfixBypass(project_root=str(tmp_path))
        assert not bypass.is_suppressed("nonexistent")

    def test_check_expired_hotfixes_none_expired(self, tmp_path):
        bypass = HotfixBypass(project_root=str(tmp_path))
        bypass.process_hotfix(
            commit_hash="abc123",
            commit_message="[HOTFIX] fix",
            module_ids=["mod_a"],
            affected_dimensions=["dim_x"],
        )
        expired = bypass.check_expired_hotfixes()
        assert "abc123" not in expired

    def test_check_expired_hotfixes_manually_expired(self, tmp_path):
        bypass = HotfixBypass(project_root=str(tmp_path))
        entry = bypass.process_hotfix(
            commit_hash="abc123",
            commit_message="[HOTFIX] fix",
            module_ids=["mod_a"],
            affected_dimensions=["dim_x"],
        )
        entry.suppressed_until = datetime.now(UTC) - timedelta(hours=1)
        expired = bypass.check_expired_hotfixes()
        assert "abc123" in expired
        assert not bypass.is_suppressed("abc123")
