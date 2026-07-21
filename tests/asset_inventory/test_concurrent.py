# [A_test] module_id: MOD-GOV_concurrent | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-226 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.asset_inventory.test_concurrent
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for MOD-INF-026 §16 Concurrent Scanner module."""

from datetime import UTC, datetime
from pathlib import Path

from zephyr.infrastructure.asset_inventory.models import RawFileEntry, ScanResult
from zephyr.infrastructure.asset_inventory.scanner import ConcurrentScanner, merge_scans
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）


class TestConcurrentScanner:
    def test_constructor(self) -> None:
        cs = ConcurrentScanner(REPO_ROOT)
        assert cs._lock_dir

    def test_not_locked_normal_file(self) -> None:
        cs = ConcurrentScanner(REPO_ROOT)
        assert not cs._is_locked(REPO_ROOT / "README.md")

    def test_scan_normal_existing_file(self) -> None:
        cs = ConcurrentScanner(REPO_ROOT)
        entry = cs._scan_normal(REPO_ROOT / "README.md")
        assert entry is not None
        assert entry.sha256
        assert len(entry.sha256) == 64
        assert entry.size_bytes > 0

    def test_shas_match_for_same_file(self) -> None:
        cs = ConcurrentScanner(REPO_ROOT)
        e1 = cs._scan_normal(REPO_ROOT / "README.md")
        e2 = cs._scan_normal(REPO_ROOT / "README.md")
        assert e1 and e2
        assert e1.sha256 == e2.sha256

    def test_verify_sha_matches(self) -> None:
        cs = ConcurrentScanner(REPO_ROOT)
        path = REPO_ROOT / "README.md"
        sha = cs._scan_normal(path).sha256  # type: ignore[union-attr]
        assert cs._verify_sha(path, sha)

    def test_verify_sha_mismatch(self) -> None:
        cs = ConcurrentScanner(REPO_ROOT)
        assert not cs._verify_sha(REPO_ROOT / "README.md", "not_a_real_sha")

    def test_scan_nonexistent_file(self) -> None:
        cs = ConcurrentScanner(REPO_ROOT)
        entry = cs._scan_normal(REPO_ROOT / "_nonexistent_xyz.txt")
        assert entry is None

    def test_scan_batch_multiple_files(self) -> None:
        cs = ConcurrentScanner(REPO_ROOT)
        paths = [
            REPO_ROOT / "README.md",
            REPO_ROOT / "pyproject.toml",
            REPO_ROOT / "_nonexistent_xyz.txt",
        ]
        results = cs.scan_batch(paths, max_workers=2)
        assert len(results) >= 2
        rel_paths = {e.relative_path for e in results}
        assert "README.md" in rel_paths or any("README" in p for p in rel_paths)

    def test_scan_batch_empty_list(self) -> None:
        cs = ConcurrentScanner(REPO_ROOT)
        results = cs.scan_batch([], max_workers=1)
        assert results == []


class TestMergeScans:
    def _entry(self, path: str, sha: str, mtime_offset: int = 0) -> RawFileEntry:
        t = datetime.now(UTC)
        p = Path(path)
        return RawFileEntry(
            relative_path=path,
            absolute_path=path,
            file_name=p.name,
            extension=p.suffix,
            size_bytes=100,
            mtime_utc=t,
            ctime_utc=t,
            sha256=sha,
        )

    def test_merge_disjoint(self) -> None:
        from datetime import datetime

        from zephyr.infrastructure.asset_inventory.models import ScanResult

        now = datetime.now(UTC)
        a = ScanResult(
            scan_id="S-A",
            scanned_at=now,
            completed_at=now,
            total_files=1,
            total_size_bytes=100,
            entries=[self._entry("a.py", "aaa")],
        )
        b = ScanResult(
            scan_id="S-B",
            scanned_at=now,
            completed_at=now,
            total_files=1,
            total_size_bytes=100,
            entries=[self._entry("b.py", "bbb")],
        )
        merged = merge_scans(a, b)
        assert merged.total_files == 2
        assert {e.relative_path for e in merged.entries} == {"a.py", "b.py"}

    def test_merge_overlap_same_sha(self) -> None:
        from datetime import datetime

        from zephyr.infrastructure.asset_inventory.models import ScanResult

        now = datetime.now(UTC)
        a = ScanResult(
            scan_id="S-A",
            scanned_at=now,
            completed_at=now,
            total_files=1,
            total_size_bytes=100,
            entries=[self._entry("x.py", "sha1")],
        )
        b = ScanResult(
            scan_id="S-B",
            scanned_at=now,
            completed_at=now,
            total_files=1,
            total_size_bytes=100,
            entries=[self._entry("x.py", "sha1")],
        )
        merged = merge_scans(a, b)
        assert merged.total_files == 1

    def test_merge_overlap_different_sha_newer_wins(self) -> None:
        from datetime import timedelta

        t = datetime.now(UTC)
        e1 = RawFileEntry(
            relative_path="x.py",
            absolute_path="x.py",
            file_name="x.py",
            extension=".py",
            size_bytes=100,
            mtime_utc=t - timedelta(days=1),
            ctime_utc=t,
            sha256="old_sha".ljust(64, "0"),
        )
        e2 = RawFileEntry(
            relative_path="x.py",
            absolute_path="x.py",
            file_name="x.py",
            extension=".py",
            size_bytes=100,
            mtime_utc=t,
            ctime_utc=t,
            sha256="new_sha".ljust(64, "0"),
        )
        a = ScanResult(
            scan_id="S-A",
            scanned_at=t,
            completed_at=t,
            total_files=1,
            total_size_bytes=100,
            entries=[e1],
        )
        b = ScanResult(
            scan_id="S-B",
            scanned_at=t,
            completed_at=t,
            total_files=1,
            total_size_bytes=100,
            entries=[e2],
        )
        merged = merge_scans(a, b)
        assert merged.total_files == 1
        assert merged.entries[0].sha256 == "new_sha".ljust(64, "0")
