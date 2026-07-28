# [A_test] module_id: MOD-GOV_scanner_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain_infrastructure_operations/asset_inventory/blueprint.md | §
# [MODULE] tests.test_scanner
# [INVARIANTS] Scanner.scan returns ScanResult; SecurityFilter.should_scan enforces safety rules
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] OSError/PermissionError handled gracefully
# [TESTS] tests/test_scanner_root.py
# [TTL] task_bound

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from zephyr.infrastructure.asset_inventory.models import RawFileEntry, ScanResult
from zephyr.infrastructure.asset_inventory.scanner import (
    ConcurrentScanner,
    Scanner,
    SecurityAccessLogger,
    SecurityFilter,
    _generate_scan_id,
    merge_scans,
)


def _make_entry(**overrides) -> RawFileEntry:
    defaults = dict(
        relative_path="src/zephyr/test.py",
        absolute_path="/abs/test.py",
        file_name="test.py",
        extension=".py",
        size_bytes=100,
        mtime_utc=datetime.now(UTC),
        sha256="abc123",
        is_binary=False,
    )
    defaults.update(overrides)
    return RawFileEntry(**defaults)


def _make_scan_result(entries=None, **overrides) -> ScanResult:
    defaults = dict(
        scan_id="SCAN-20260522-001",
        scanned_at=datetime.now(UTC),
        completed_at=datetime.now(UTC),
        total_files=len(entries) if entries else 0,
        total_size_bytes=sum(e.size_bytes for e in entries) if entries else 0,
        scan_mode="full",
        entries=entries or [],
        errors=[],
        duration_seconds=1.0,
    )
    defaults.update(overrides)
    return ScanResult(**defaults)


class TestScannerInstantiation:
    def test_default(self):
        s = Scanner()
        assert s.directories is not None
        assert s.max_workers > 0

    def test_custom_params(self):
        s = Scanner(directories=["src/"], excludes={"__pycache__"}, max_workers=4, root=Path("/tmp"))
        assert s.directories == ["src/"]
        assert s.max_workers == 4


class TestScannerScan:
    def test_scan_empty_directory(self, tmp_path):
        s = Scanner(directories=["subdir/"], root=tmp_path)
        (tmp_path / "subdir").mkdir()
        result = s.scan()
        assert isinstance(result, ScanResult)
        assert result.total_files == 0
        assert result.entries == []

    def test_scan_with_files(self, tmp_path):
        subdir = tmp_path / "src" / "zephyr"
        subdir.mkdir(parents=True)
        (subdir / "hello.py").write_text("print('hello')", encoding="utf-8")
        s = Scanner(directories=["src/"], root=tmp_path, max_workers=2)
        result = s.scan()
        assert result.total_files >= 1
        assert any("hello.py" in e.relative_path for e in result.entries)

    def test_scan_excludes_pycache(self, tmp_path):
        subdir = tmp_path / "src"
        subdir.mkdir()
        (subdir / "good.py").write_text("x=1", encoding="utf-8")
        cache_dir = subdir / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "good.cpython.pyc").write_bytes(b"\x00")
        s = Scanner(directories=["src/"], root=tmp_path)
        result = s.scan()
        assert not any("__pycache__" in e.relative_path for e in result.entries)

    def test_scan_nonexistent_directory(self, tmp_path):
        s = Scanner(directories=["nonexistent/"], root=tmp_path)
        result = s.scan()
        assert result.total_files == 0

    def test_scan_id_format(self):
        sid = _generate_scan_id()
        assert sid.startswith("SCAN-")


class TestScannerSave:
    def test_save_creates_file(self, tmp_path):
        s = Scanner(root=tmp_path)
        result = _make_scan_result()
        out = s.save(result, output_path=tmp_path / "scan.json")
        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["scan_id"] == "SCAN-20260522-001"


class TestConcurrentScanner:
    def test_instantiation(self, tmp_path):
        cs = ConcurrentScanner(project_root=tmp_path)
        assert cs.root == tmp_path

    def test_scan_file(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("x = 1", encoding="utf-8")
        cs = ConcurrentScanner(project_root=tmp_path)
        entry = cs.scan_file(f)
        assert entry is not None
        assert entry.file_name == "test.py"

    def test_scan_file_nonexistent(self, tmp_path):
        cs = ConcurrentScanner(project_root=tmp_path)
        try:
            entry = cs.scan_file(tmp_path / "nonexistent.py")
            assert entry is None
        except (FileNotFoundError, OSError):
            pass

    def test_scan_batch(self, tmp_path):
        f1 = tmp_path / "a.py"
        f2 = tmp_path / "b.py"
        f1.write_text("x=1", encoding="utf-8")
        f2.write_text("y=2", encoding="utf-8")
        cs = ConcurrentScanner(project_root=tmp_path)
        results = cs.scan_batch([f1, f2], max_workers=2)
        assert len(results) == 2

    def test_scan_batch_empty(self, tmp_path):
        cs = ConcurrentScanner(project_root=tmp_path)
        results = cs.scan_batch([])
        assert results == []


class TestMergeScans:
    def test_merge_disjoint(self):
        e1 = _make_entry(relative_path="a.py", sha256="sha1")
        e2 = _make_entry(relative_path="b.py", sha256="sha2")
        s1 = _make_scan_result(entries=[e1], scan_id="S1")
        s2 = _make_scan_result(entries=[e2], scan_id="S2")
        merged = merge_scans(s1, s2)
        assert merged.total_files == 2

    def test_merge_same_path_keeps_newer(self):
        now = datetime.now(UTC)
        e1 = _make_entry(relative_path="a.py", sha256="sha1", mtime_utc=now, size_bytes=10)
        e2 = _make_entry(relative_path="a.py", sha256="sha2", mtime_utc=now.replace(year=now.year + 1), size_bytes=20)
        s1 = _make_scan_result(entries=[e1], scan_id="S1")
        s2 = _make_scan_result(entries=[e2], scan_id="S2")
        merged = merge_scans(s1, s2)
        assert merged.total_files == 1
        assert merged.entries[0].sha256 == "sha2"


class TestSecurityFilter:
    def test_should_scan_normal_file(self, tmp_path):
        f = tmp_path / "code.py"
        f.write_text("x=1", encoding="utf-8")
        sf = SecurityFilter()
        ok, reason = sf.should_scan(f)
        assert ok is True
        assert reason is None

    def test_should_skip_secret_file(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text("SECRET=abc", encoding="utf-8")
        sf = SecurityFilter()
        ok, reason = sf.should_scan(f)
        assert ok is False
        assert "secret" in reason.lower() or "pattern" in reason.lower()

    def test_should_skip_pem_file(self, tmp_path):
        f = tmp_path / "cert.pem"
        f.write_text("-----BEGIN CERTIFICATE-----", encoding="utf-8")
        sf = SecurityFilter()
        ok, reason = sf.should_scan(f)
        assert ok is False

    def test_should_skip_excluded_dir(self, tmp_path):
        f = tmp_path / ".git" / "config"
        f.parent.mkdir()
        f.write_text("stuff", encoding="utf-8")
        sf = SecurityFilter()
        ok, reason = sf.should_scan(f)
        assert ok is False


class TestSecurityAccessLogger:
    def test_log_skip(self, tmp_path):
        logger = SecurityAccessLogger(log_dir=tmp_path)
        logger.log_skip("secret.env", "matches_secret_pattern")
        skips = logger.recent_skips()
        assert len(skips) >= 1
        assert skips[0].action == "SCAN_SKIP"

    def test_log_ok(self, tmp_path):
        logger = SecurityAccessLogger(log_dir=tmp_path)
        logger.log_ok("code.py", "sha256abc", 100)
        assert (tmp_path / "security_access_log.jsonl").exists()

    def test_recent_skips_empty(self, tmp_path):
        logger = SecurityAccessLogger(log_dir=tmp_path)
        assert logger.recent_skips() == []
