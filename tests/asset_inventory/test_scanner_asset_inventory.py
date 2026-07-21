# [A_test] module_id: MOD-GOV_scanner_asset_inventory | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-239 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.asset_inventory.test_scanner
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for MOD-INF-026 Scanner module."""

from datetime import UTC
from pathlib import Path

from zephyr.infrastructure.asset_inventory.scanner import Scanner, _generate_scan_id, _process_one, _sha256


class TestGenerateScanId:
    def test_prefix(self) -> None:
        sid = _generate_scan_id()
        assert sid.startswith("SCAN-")


class TestSHA256:
    def test_known_file(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        result = _sha256(f)
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_deterministic(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        h1 = _sha256(f)
        h2 = _sha256(f)
        assert h1 == h2

    def test_different_content(self, tmp_path: Path) -> None:
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("hello")
        f2.write_text("world")
        assert _sha256(f1) != _sha256(f2)


class TestProcessOne:
    def test_output_type(self, tmp_path: Path) -> None:
        f = tmp_path / "src" / "zephyr" / "test.py"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("# test")
        entry = _process_one(f, tmp_path)
        assert entry.relative_path == "src/zephyr/test.py"
        assert entry.extension == ".py"
        assert entry.size_bytes > 0
        assert len(entry.sha256) == 64


class TestScanner:
    def test_scan_empty_dir(self, tmp_path: Path) -> None:
        d = tmp_path / "empty"
        d.mkdir(parents=True, exist_ok=True)
        s = Scanner(directories=["empty"], excludes=set(), root=tmp_path)
        result = s.scan()
        assert result.total_files == 0
        assert result.entries == []

    def test_scan_with_files(self, tmp_path: Path) -> None:
        d = tmp_path / "src"
        d.mkdir(parents=True, exist_ok=True)
        (d / "a.py").write_text("# a")
        (d / "b.py").write_text("# b")

        s = Scanner(directories=["src"], excludes=set(), root=tmp_path)
        result = s.scan()
        assert result.total_files == 2
        paths = {e.relative_path for e in result.entries}
        assert "src/a.py" in paths
        assert "src/b.py" in paths

    def test_excludes(self, tmp_path: Path) -> None:
        d = tmp_path / "src"
        d.mkdir(parents=True, exist_ok=True)
        cache = d / "__pycache__"
        cache.mkdir()
        (cache / "cached.pyc").write_text("cached")
        (d / "real.py").write_text("real")

        s = Scanner(directories=["src"], excludes={"__pycache__"}, root=tmp_path)
        result = s.scan()
        assert result.total_files == 1
        assert result.entries[0].relative_path == "src/real.py"

    def test_incremental(self, tmp_path: Path) -> None:
        d = tmp_path / "src"
        d.mkdir(parents=True, exist_ok=True)
        (d / "old.py").write_text("old")
        from datetime import datetime, timedelta

        old_time = datetime.now(UTC) - timedelta(hours=2)

        s = Scanner(directories=["src"], excludes=set(), root=tmp_path)
        result = s.scan(incremental=True, last_scan_time=old_time)
        assert result.scan_mode == "incremental"

    def test_save(self, tmp_path: Path) -> None:
        import json

        from zephyr.infrastructure.asset_inventory.models import ScanResult

        out = tmp_path / "scan.json"
        sr = ScanResult(
            scan_id="SCAN-20260507-999",
            total_files=5,
            total_size_bytes=500,
        )
        s = Scanner(root=tmp_path)
        p = s.save(sr, output_path=out)
        assert p.exists()
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["scan_id"] == "SCAN-20260507-999"
