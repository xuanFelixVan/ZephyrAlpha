# [A_test] module_id: MOD-GOV_knowngoodstate_ledger | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_knowngoodstate_ledger
# [INVARIANTS] signature is SHA256 of "commit_sha|verified_at|method|file_count|db_integrity"
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from zephyr.infrastructure.rollback.knowngoodstate_ledger import (
    KnownGoodRecord,
    KnowngoodstateLedger,
)


class TestKnownGoodRecord:
    def test_fields(self):
        rec = KnownGoodRecord(
            commit_sha="abc123",
            verified_at="2026-01-01T00:00:00Z",
            verification_method="post_rollback",
            file_count=10,
            db_integrity_pass=True,
            signature="sig123",
        )
        assert rec.commit_sha == "abc123"
        assert rec.file_count == 10
        assert rec.db_integrity_pass is True


class TestKnowngoodstateLedgerInstantiation:
    def test_default_project_root(self):
        ledger = KnowngoodstateLedger()
        assert ledger._project_root == Path.cwd()

    def test_custom_project_root(self, tmp_path):
        ledger = KnowngoodstateLedger(project_root=tmp_path)
        assert ledger._project_root == tmp_path


class TestDeclareKnownGood:
    def test_declare_creates_record(self, tmp_path):
        ledger = KnowngoodstateLedger(project_root=tmp_path)
        record = ledger.declare_known_good(
            commit_sha="sha001",
            verification_method="manual",
            file_count=5,
            db_integrity_pass=True,
        )
        assert record.commit_sha == "sha001"
        assert record.verification_method == "manual"
        assert record.file_count == 5
        assert record.db_integrity_pass is True
        assert record.verified_at != ""
        assert record.signature != ""

    def test_signature_is_sha256(self, tmp_path):
        ledger = KnowngoodstateLedger(project_root=tmp_path)
        record = ledger.declare_known_good("sha002", "auto", 3, True)
        raw = f"{record.commit_sha}|{record.verified_at}|{record.verification_method}|{record.file_count}|{record.db_integrity_pass}"
        expected = hashlib.sha256(raw.encode()).hexdigest()
        assert record.signature == expected

    def test_declare_persists_to_file(self, tmp_path):
        ledger = KnowngoodstateLedger(project_root=tmp_path)
        ledger.declare_known_good("sha003", "post_rollback_verification", 0, True)
        ledger_file = tmp_path / ".zephyr/knowngoodstate_ledger.jsonl"
        assert ledger_file.exists()
        lines = ledger_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["commit_sha"] == "sha003"

    def test_declare_default_values(self, tmp_path):
        ledger = KnowngoodstateLedger(project_root=tmp_path)
        record = ledger.declare_known_good("sha004")
        assert record.verification_method == "post_rollback_verification"
        assert record.file_count == 0
        assert record.db_integrity_pass is True

    def test_declare_db_integrity_fail(self, tmp_path):
        ledger = KnowngoodstateLedger(project_root=tmp_path)
        record = ledger.declare_known_good("sha005", db_integrity_pass=False)
        assert record.db_integrity_pass is False

    def test_multiple_declarations(self, tmp_path):
        ledger = KnowngoodstateLedger(project_root=tmp_path)
        ledger.declare_known_good("sha010")
        ledger.declare_known_good("sha011")
        ledger.declare_known_good("sha012")
        records = ledger.get_latest_known_good(limit=10)
        assert len(records) == 3


class TestGetLatestKnownGood:
    def test_empty_ledger(self, tmp_path):
        ledger = KnowngoodstateLedger(project_root=tmp_path)
        records = ledger.get_latest_known_good()
        assert records == []

    def test_limit_respected(self, tmp_path):
        ledger = KnowngoodstateLedger(project_root=tmp_path)
        for i in range(10):
            ledger.declare_known_good(f"sha{i:03d}")
        records = ledger.get_latest_known_good(limit=3)
        assert len(records) == 3
        assert records[0].commit_sha == "sha007"
        assert records[2].commit_sha == "sha009"

    def test_no_ledger_file(self, tmp_path):
        ledger = KnowngoodstateLedger(project_root=tmp_path)
        ledger._ledger_path.unlink(missing_ok=True)
        records = ledger.get_latest_known_good()
        assert records == []


class TestFindKnownGood:
    def test_find_existing(self, tmp_path):
        ledger = KnowngoodstateLedger(project_root=tmp_path)
        ledger.declare_known_good("sha100")
        record = ledger.find_known_good("sha100")
        assert record is not None
        assert record.commit_sha == "sha100"

    def test_find_nonexistent(self, tmp_path):
        ledger = KnowngoodstateLedger(project_root=tmp_path)
        ledger.declare_known_good("sha100")
        record = ledger.find_known_good("sha999")
        assert record is None

    def test_find_returns_latest(self, tmp_path):
        ledger = KnowngoodstateLedger(project_root=tmp_path)
        ledger.declare_known_good("sha200")
        ledger.declare_known_good("sha200")
        record = ledger.find_known_good("sha200")
        assert record is not None


class TestIsKnownGood:
    def test_known_good(self, tmp_path):
        ledger = KnowngoodstateLedger(project_root=tmp_path)
        ledger.declare_known_good("sha300")
        assert ledger.is_known_good("sha300") is True

    def test_not_known_good(self, tmp_path):
        ledger = KnowngoodstateLedger(project_root=tmp_path)
        assert ledger.is_known_good("sha999") is False

    def test_empty_ledger(self, tmp_path):
        ledger = KnowngoodstateLedger(project_root=tmp_path)
        assert ledger.is_known_good("sha000") is False
