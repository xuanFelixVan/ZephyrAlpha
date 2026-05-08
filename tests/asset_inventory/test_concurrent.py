"""Tests for MOD-INF-026 §16 Concurrent Scanner module."""

from datetime import datetime, timezone
from pathlib import Path

from zephyr.asset_inventory.concurrent import ConcurrentScanner, merge_scans
from zephyr.asset_inventory.models import RawFileEntry, ScanResult


class TestConcurrentScanner:
    def test_constructor(self) -> None:
        cs = ConcurrentScanner(Path("D:/ZephyrAlpha"))
        assert cs._lock_dir

    def test_not_locked_normal_file(self) -> None:
        cs = ConcurrentScanner(Path("D:/ZephyrAlpha"))
        assert not cs._is_locked(Path("D:/ZephyrAlpha/README.md"))

    def test_scan_normal_existing_file(self) -> None:
        cs = ConcurrentScanner(Path("D:/ZephyrAlpha"))
        entry = cs._scan_normal(Path("D:/ZephyrAlpha/README.md"))
        assert entry is not None
        assert entry.sha256
        assert len(entry.sha256) == 64
        assert entry.size_bytes > 0

    def test_shas_match_for_same_file(self) -> None:
        cs = ConcurrentScanner(Path("D:/ZephyrAlpha"))
        e1 = cs._scan_normal(Path("D:/ZephyrAlpha/README.md"))
        e2 = cs._scan_normal(Path("D:/ZephyrAlpha/README.md"))
        assert e1 and e2
        assert e1.sha256 == e2.sha256

    def test_verify_sha_matches(self) -> None:
        cs = ConcurrentScanner(Path("D:/ZephyrAlpha"))
        path = Path("D:/ZephyrAlpha/README.md")
        sha = cs._scan_normal(path).sha256  # type: ignore[union-attr]
        assert cs._verify_sha(path, sha)

    def test_verify_sha_mismatch(self) -> None:
        cs = ConcurrentScanner(Path("D:/ZephyrAlpha"))
        assert not cs._verify_sha(Path("D:/ZephyrAlpha/README.md"), "not_a_real_sha")

    def test_scan_nonexistent_file(self) -> None:
        cs = ConcurrentScanner(Path("D:/ZephyrAlpha"))
        entry = cs._scan_normal(Path("D:/ZephyrAlpha/_nonexistent_xyz.txt"))
        assert entry is None

    def test_scan_batch_multiple_files(self) -> None:
        cs = ConcurrentScanner(Path("D:/ZephyrAlpha"))
        paths = [
            Path("D:/ZephyrAlpha/README.md"),
            Path("D:/ZephyrAlpha/pyproject.toml"),
            Path("D:/ZephyrAlpha/_nonexistent_xyz.txt"),
        ]
        results = cs.scan_batch(paths, max_workers=2)
        assert len(results) >= 2
        rel_paths = {e.relative_path for e in results}
        assert "README.md" in rel_paths or any("README" in p for p in rel_paths)

    def test_scan_batch_empty_list(self) -> None:
        cs = ConcurrentScanner(Path("D:/ZephyrAlpha"))
        results = cs.scan_batch([], max_workers=1)
        assert results == []


class TestMergeScans:
    def _entry(self, path: str, sha: str, mtime_offset: int = 0) -> RawFileEntry:
        t = datetime.now(timezone.utc)
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
        from datetime import datetime, timezone
        from zephyr.asset_inventory.models import ScanResult
        now = datetime.now(timezone.utc)
        a = ScanResult(
            scan_id="S-A", scanned_at=now, completed_at=now,
            total_files=1, total_size_bytes=100,
            entries=[self._entry("a.py", "aaa")],
        )
        b = ScanResult(
            scan_id="S-B", scanned_at=now, completed_at=now,
            total_files=1, total_size_bytes=100,
            entries=[self._entry("b.py", "bbb")],
        )
        merged = merge_scans(a, b)
        assert merged.total_files == 2
        assert {e.relative_path for e in merged.entries} == {"a.py", "b.py"}

    def test_merge_overlap_same_sha(self) -> None:
        from datetime import datetime, timezone
        from zephyr.asset_inventory.models import ScanResult
        now = datetime.now(timezone.utc)
        a = ScanResult(
            scan_id="S-A", scanned_at=now, completed_at=now,
            total_files=1, total_size_bytes=100,
            entries=[self._entry("x.py", "sha1")],
        )
        b = ScanResult(
            scan_id="S-B", scanned_at=now, completed_at=now,
            total_files=1, total_size_bytes=100,
            entries=[self._entry("x.py", "sha1")],
        )
        merged = merge_scans(a, b)
        assert merged.total_files == 1

    def test_merge_overlap_different_sha_newer_wins(self) -> None:
        from datetime import timedelta
        from zephyr.asset_inventory.models import ScanResult
        t = datetime.now(timezone.utc)
        e1 = RawFileEntry(
            relative_path="x.py", absolute_path="x.py",
            file_name="x.py", extension=".py",
            size_bytes=100,
            mtime_utc=t - timedelta(days=1),
            ctime_utc=t,
            sha256="old_sha".ljust(64, "0"),
        )
        e2 = RawFileEntry(
            relative_path="x.py", absolute_path="x.py",
            file_name="x.py", extension=".py",
            size_bytes=100,
            mtime_utc=t,
            ctime_utc=t,
            sha256="new_sha".ljust(64, "0"),
        )
        a = ScanResult(
            scan_id="S-A", scanned_at=t, completed_at=t,
            total_files=1, total_size_bytes=100,
            entries=[e1],
        )
        b = ScanResult(
            scan_id="S-B", scanned_at=t, completed_at=t,
            total_files=1, total_size_bytes=100,
            entries=[e2],
        )
        merged = merge_scans(a, b)
        assert merged.total_files == 1
        assert merged.entries[0].sha256 == "new_sha".ljust(64, "0")
