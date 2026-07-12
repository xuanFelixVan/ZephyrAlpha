# [A_test] module_id: SRC-TST-1238 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_load_bearing
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] test_load_bearing.py
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.gov_kb.load_bearing import LBEntry, LBStatus, LoadBearingWall, WallReport


def _write_ke(directory: Path, name: str, frontmatter: dict, body: str = "content") -> Path:
    import yaml

    directory.mkdir(parents=True, exist_ok=True)
    fm_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False).rstrip()
    text = f"---\n{fm_str}\n---\n{body}"
    p = directory / f"{name}.md"
    p.write_text(text, encoding="utf-8")
    return p


class TestLoadBearingWall:
    def _make_wall(self, tmp_path: Path) -> LoadBearingWall:
        return LoadBearingWall(project_root=tmp_path)

    def _ke_dir(self, tmp_path: Path) -> Path:
        return tmp_path / "docs" / "08_knowledge" / "01_raw_intake"

    def test_scan_empty_dir(self, tmp_path: Path):
        wall = self._make_wall(tmp_path)
        self._ke_dir(tmp_path).mkdir(parents=True, exist_ok=True)
        entries = wall.scan()
        assert entries == []

    def test_scan_no_dir(self, tmp_path: Path):
        wall = self._make_wall(tmp_path)
        entries = wall.scan()
        assert entries == []

    def test_scan_finds_load_bearing(self, tmp_path: Path):
        wall = self._make_wall(tmp_path)
        ke_dir = self._ke_dir(tmp_path)
        _write_ke(
            ke_dir,
            "KE-001",
            {
                "module_id": "KE-001",
                "is_load_bearing": True,
                "category": "governance",
                "version": 1,
            },
        )
        entries = wall.scan()
        assert len(entries) == 1
        assert entries[0].ke_id == "KE-001"
        assert entries[0].category == "governance"

    def test_scan_ignores_non_load_bearing(self, tmp_path: Path):
        wall = self._make_wall(tmp_path)
        ke_dir = self._ke_dir(tmp_path)
        _write_ke(ke_dir, "KE-002", {"module_id": "KE-002", "category": "general"})
        entries = wall.scan()
        assert len(entries) == 0

    def test_register(self, tmp_path: Path):
        wall = self._make_wall(tmp_path)
        ke_dir = self._ke_dir(tmp_path)
        _write_ke(ke_dir, "KE-010", {"module_id": "KE-010", "category": "test"})
        entry = wall.register("KE-010")
        assert isinstance(entry, LBEntry)
        assert entry.ke_id == "KE-010"
        entries = wall.scan()
        assert len(entries) == 1

    def test_register_already_load_bearing_raises(self, tmp_path: Path):
        wall = self._make_wall(tmp_path)
        ke_dir = self._ke_dir(tmp_path)
        _write_ke(ke_dir, "KE-011", {"module_id": "KE-011", "is_load_bearing": True, "category": "test"})
        with pytest.raises(ValueError, match="already load-bearing"):
            wall.register("KE-011")

    def test_register_force(self, tmp_path: Path):
        wall = self._make_wall(tmp_path)
        ke_dir = self._ke_dir(tmp_path)
        _write_ke(ke_dir, "KE-012", {"module_id": "KE-012", "is_load_bearing": True, "category": "test"})
        entry = wall.register("KE-012", force=True)
        assert entry.ke_id == "KE-012"

    def test_register_not_found_raises(self, tmp_path: Path):
        wall = self._make_wall(tmp_path)
        self._ke_dir(tmp_path).mkdir(parents=True, exist_ok=True)
        with pytest.raises(FileNotFoundError):
            wall.register("KE-999")

    def test_deregister(self, tmp_path: Path):
        wall = self._make_wall(tmp_path)
        ke_dir = self._ke_dir(tmp_path)
        _write_ke(ke_dir, "KE-020", {"module_id": "KE-020", "is_load_bearing": True, "category": "test"})
        wall.deregister("KE-020")
        entries = wall.scan()
        assert len(entries) == 0

    def test_deregister_not_found_raises(self, tmp_path: Path):
        wall = self._make_wall(tmp_path)
        self._ke_dir(tmp_path).mkdir(parents=True, exist_ok=True)
        with pytest.raises(FileNotFoundError):
            wall.deregister("KE-999")

    def test_check_healthy(self, tmp_path: Path):
        wall = self._make_wall(tmp_path)
        ke_dir = self._ke_dir(tmp_path)
        _write_ke(
            ke_dir,
            "KE-030",
            {
                "module_id": "KE-030",
                "is_load_bearing": True,
                "category": "governance",
                "version": 1,
            },
        )
        report = wall.check()
        assert isinstance(report, WallReport)
        assert report.overall in (LBStatus.HEALTHY, LBStatus.EXPIRING)

    def test_check_missing_file(self, tmp_path: Path):
        wall = self._make_wall(tmp_path)
        from datetime import UTC, datetime

        entry = LBEntry(
            ke_id="KE-040",
            file_path="docs/08_knowledge/01_raw_intake/KE-040.md",
            source_hash="abc",
            ttl="",
            category="test",
        )
        issues = wall._check_one(entry, datetime.now(UTC))
        assert any("MISSING" in i for i in issues)

    def test_know_dir_property(self, tmp_path: Path):
        wall = self._make_wall(tmp_path)
        assert str(wall.know_dir).endswith("01_raw_intake")

    def test_manifest_path_property(self, tmp_path: Path):
        wall = self._make_wall(tmp_path)
        assert "snapshots" in str(wall.manifest_path)


class TestLBEntry:
    def test_defaults(self):
        e = LBEntry(ke_id="KE-1", file_path="a.md", source_hash="h", ttl="", category="c")
        assert e.depends_on == []
        assert e.version == 1
        assert e.status == LBStatus.HEALTHY


class TestLBStatus:
    def test_values(self):
        assert LBStatus.HEALTHY.value == "healthy"
        assert LBStatus.CORRUPT.value == "corrupt"
        assert LBStatus.MISSING.value == "missing"
