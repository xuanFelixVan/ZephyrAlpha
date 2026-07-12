# [A_test] module_id: SRC-TST-1042 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_gate_integrity_guard
# [INVARIANTS] IntegrityReport fields immutable after creation; verify always returns IntegrityReport; all_valid reflects cumulative reports
# [MODIFY-GUARD] changes must preserve test coverage for verify/verify_self/_load_manifest/_compute_sha256/reports/all_valid
# [CONSUMERS] CI pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] verify(nonexistent_path) -> IntegrityReport(valid=False); _load_manifest(missing_path) -> logs warning, no raise
# [TESTS] pytest tests/test_gate_integrity_guard.py -q
# [TTL] task_bound

from __future__ import annotations

import hashlib
from pathlib import Path

from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_integrity_guard import GateIntegrityGuard, IntegrityReport


class TestIntegrityReport:
    def test_fields_assigned(self):
        report = IntegrityReport(
            file_path="/a/b.py",
            sha256="abc123",
            expected_sha256="abc123",
            valid=True,
        )
        assert report.file_path == "/a/b.py"
        assert report.sha256 == "abc123"
        assert report.expected_sha256 == "abc123"
        assert report.valid is True
        assert report.checked_at is not None

    def test_valid_false_when_hash_mismatch(self):
        report = IntegrityReport(
            file_path="/a/b.py",
            sha256="aaa",
            expected_sha256="bbb",
            valid=False,
        )
        assert report.valid is False

    def test_expected_sha256_can_be_none(self):
        report = IntegrityReport(
            file_path="/a/c.py",
            sha256="deadbeef",
            expected_sha256=None,
            valid=False,
        )
        assert report.expected_sha256 is None


class TestGateIntegrityGuardInit:
    def test_default_init_no_manifest(self):
        guard = GateIntegrityGuard()
        assert guard.reports == []
        assert guard.all_valid is True

    def test_init_with_manifest(self, tmp_path: Path):
        manifest = tmp_path / "manifest.txt"
        manifest.write_text("file_a.py abc123\n", encoding="utf-8")
        guard = GateIntegrityGuard(manifest_path=str(manifest))
        assert guard.reports == []


class TestLoadManifest:
    def test_load_valid_manifest(self, tmp_path: Path):
        real_file = tmp_path / "alpha.py"
        real_file.write_text("print('hi')", encoding="utf-8")
        sha = GateIntegrityGuard._compute_sha256(str(real_file))
        manifest = tmp_path / "manifest.txt"
        manifest.write_text(f"{real_file} hash_a\nbeta.py hash_b\n", encoding="utf-8")
        guard = GateIntegrityGuard(manifest_path=str(manifest))
        report = guard.verify(str(real_file))
        assert report.expected_sha256 == "hash_a"
        assert report.sha256 == sha

    def test_load_manifest_skips_comments_and_blanks(self, tmp_path: Path):
        real_file = tmp_path / "alpha.py"
        real_file.write_text("x", encoding="utf-8")
        manifest = tmp_path / "manifest.txt"
        manifest.write_text(
            f"# comment\n\n  \n{real_file} hash_a\n",
            encoding="utf-8",
        )
        guard = GateIntegrityGuard(manifest_path=str(manifest))
        report = guard.verify(str(real_file))
        assert report.expected_sha256 == "hash_a"

    def test_load_manifest_missing_file_no_crash(self, tmp_path: Path):
        missing = str(tmp_path / "no_such_manifest.txt")
        guard = GateIntegrityGuard(manifest_path=missing)
        assert guard.reports == []


class TestVerify:
    def test_verify_matching_hash(self, tmp_path: Path):
        target = tmp_path / "target.py"
        target.write_text("hello world", encoding="utf-8")
        sha = GateIntegrityGuard._compute_sha256(str(target))
        guard = GateIntegrityGuard()
        report = guard.verify(str(target), expected_hash=sha)
        assert report.valid is True
        assert report.sha256 == sha
        assert report.expected_sha256 == sha

    def test_verify_mismatching_hash(self, tmp_path: Path):
        target = tmp_path / "target.py"
        target.write_text("hello world", encoding="utf-8")
        guard = GateIntegrityGuard()
        report = guard.verify(str(target), expected_hash="badhash0000000000")
        assert report.valid is False
        assert report.sha256 != "badhash0000000000"

    def test_verify_nonexistent_file(self):
        guard = GateIntegrityGuard()
        report = guard.verify("/nonexistent/path/file.py")
        assert report.valid is False
        assert report.sha256 == ""
        assert report.file_path == "/nonexistent/path/file.py"

    def test_verify_uses_manifest_when_no_expected_hash(self, tmp_path: Path):
        target = tmp_path / "mod.py"
        target.write_text("data", encoding="utf-8")
        sha = GateIntegrityGuard._compute_sha256(str(target))
        manifest = tmp_path / "manifest.txt"
        manifest.write_text(f"{target} {sha}\n", encoding="utf-8")
        guard = GateIntegrityGuard(manifest_path=str(manifest))
        report = guard.verify(str(target))
        assert report.valid is True

    def test_verify_no_expected_returns_invalid(self, tmp_path: Path):
        target = tmp_path / "mod.py"
        target.write_text("data", encoding="utf-8")
        guard = GateIntegrityGuard()
        report = guard.verify(str(target))
        assert report.valid is False
        assert report.expected_sha256 is None

    def test_verify_appends_to_reports(self, tmp_path: Path):
        target = tmp_path / "mod.py"
        target.write_text("data", encoding="utf-8")
        sha = GateIntegrityGuard._compute_sha256(str(target))
        guard = GateIntegrityGuard()
        guard.verify(str(target), expected_hash=sha)
        guard.verify(str(target), expected_hash=sha)
        assert len(guard.reports) == 2


class TestVerifySelf:
    def test_verify_self_no_trust_root(self, monkeypatch):
        monkeypatch.delenv("ZEPHYR_TRUST_ROOT", raising=False)
        guard = GateIntegrityGuard()
        assert guard.verify_self() is True


class TestComputeSha256:
    def test_compute_sha256_known_content(self, tmp_path: Path):
        target = tmp_path / "known.txt"
        content = "test content for sha256"
        target.write_text(content, encoding="utf-8")
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        result = GateIntegrityGuard._compute_sha256(str(target))
        assert result == expected

    def test_compute_sha256_empty_file(self, tmp_path: Path):
        target = tmp_path / "empty.txt"
        target.write_bytes(b"")
        expected = hashlib.sha256(b"").hexdigest()
        result = GateIntegrityGuard._compute_sha256(str(target))
        assert result == expected

    def test_compute_sha256_binary_content(self, tmp_path: Path):
        target = tmp_path / "binary.bin"
        data = bytes(range(256))
        target.write_bytes(data)
        expected = hashlib.sha256(data).hexdigest()
        result = GateIntegrityGuard._compute_sha256(str(target))
        assert result == expected


class TestReportsProperty:
    def test_reports_returns_copy(self, tmp_path: Path):
        target = tmp_path / "mod.py"
        target.write_text("x", encoding="utf-8")
        sha = GateIntegrityGuard._compute_sha256(str(target))
        guard = GateIntegrityGuard()
        guard.verify(str(target), expected_hash=sha)
        r1 = guard.reports
        r2 = guard.reports
        assert r1 is not r2
        assert len(r1) == 1


class TestAllValidProperty:
    def test_all_valid_true_when_all_pass(self, tmp_path: Path):
        target = tmp_path / "mod.py"
        target.write_text("x", encoding="utf-8")
        sha = GateIntegrityGuard._compute_sha256(str(target))
        guard = GateIntegrityGuard()
        guard.verify(str(target), expected_hash=sha)
        assert guard.all_valid is True

    def test_all_valid_false_when_any_fails(self, tmp_path: Path):
        target = tmp_path / "mod.py"
        target.write_text("x", encoding="utf-8")
        guard = GateIntegrityGuard()
        guard.verify(str(target), expected_hash="wrong_hash")
        assert guard.all_valid is False

    def test_all_valid_true_when_no_reports(self):
        guard = GateIntegrityGuard()
        assert guard.all_valid is True

    def test_all_valid_mixed_reports(self, tmp_path: Path):
        t1 = tmp_path / "good.py"
        t2 = tmp_path / "bad.py"
        t1.write_text("good", encoding="utf-8")
        t2.write_text("bad", encoding="utf-8")
        sha1 = GateIntegrityGuard._compute_sha256(str(t1))
        guard = GateIntegrityGuard()
        guard.verify(str(t1), expected_hash=sha1)
        guard.verify(str(t2), expected_hash="wrong_hash")
        assert guard.all_valid is False
