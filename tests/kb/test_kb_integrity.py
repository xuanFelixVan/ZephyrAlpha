# [A_test] module_id: SRC-TST-1169 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_integrity
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] test_kb_integrity.py
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

from zephyr.governance.integrity import DriftReport, HashEntry, IntegrityGuard, Manifest


class TestIntegrityGuard:
    def _make_guard(self, tmp_path: Path) -> IntegrityGuard:
        return IntegrityGuard(project_root=tmp_path)

    def _make_ke_dir(self, tmp_path: Path) -> Path:
        d = tmp_path / "docs" / "08_knowledge" / "01_raw_intake"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _make_src_dir(self, tmp_path: Path) -> Path:
        d = tmp_path / "src" / "zephyr" / "kb"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def test_generate_empty_dirs(self, tmp_path: Path):
        guard = self._make_guard(tmp_path)
        self._make_ke_dir(tmp_path)
        self._make_src_dir(tmp_path)
        manifest = guard.generate()
        assert isinstance(manifest, Manifest)
        assert manifest.layer1_kes == []
        assert manifest.layer2_sources == []
        assert len(manifest.layer3_aggregate) == 64

    def test_generate_with_files(self, tmp_path: Path):
        guard = self._make_guard(tmp_path)
        ke_dir = self._make_ke_dir(tmp_path)
        src_dir = self._make_src_dir(tmp_path)
        (ke_dir / "KE-001.md").write_text("hello ke", encoding="utf-8")
        (src_dir / "mod.py").write_text("print('hi')", encoding="utf-8")
        manifest = guard.generate()
        assert len(manifest.layer1_kes) == 1
        assert len(manifest.layer2_sources) == 1
        assert manifest.layer1_kes[0].path.endswith("KE-001.md")
        assert manifest.layer2_sources[0].path.endswith("mod.py")

    def test_load_returns_none_when_no_manifest(self, tmp_path: Path):
        guard = self._make_guard(tmp_path)
        assert guard.load() is None

    def test_load_roundtrip(self, tmp_path: Path):
        guard = self._make_guard(tmp_path)
        self._make_ke_dir(tmp_path)
        self._make_src_dir(tmp_path)
        guard.generate()
        loaded = guard.load()
        assert loaded is not None
        assert loaded.version == "1.0"

    def test_verify_no_manifest_returns_not_clean(self, tmp_path: Path):
        guard = self._make_guard(tmp_path)
        report = guard.verify(layer=1)
        assert isinstance(report, DriftReport)
        assert report.is_clean is False

    def test_verify_clean_after_generate(self, tmp_path: Path):
        guard = self._make_guard(tmp_path)
        ke_dir = self._make_ke_dir(tmp_path)
        src_dir = self._make_src_dir(tmp_path)
        (ke_dir / "KE-001.md").write_text("content", encoding="utf-8")
        (src_dir / "mod.py").write_text("code", encoding="utf-8")
        guard.generate()
        report = guard.verify(layer=3)
        assert report.is_clean is True

    def test_verify_detects_added_file(self, tmp_path: Path):
        guard = self._make_guard(tmp_path)
        ke_dir = self._make_ke_dir(tmp_path)
        src_dir = self._make_src_dir(tmp_path)
        (ke_dir / "KE-001.md").write_text("content", encoding="utf-8")
        guard.generate()
        (ke_dir / "KE-002.md").write_text("new ke", encoding="utf-8")
        report = guard.verify(layer=1)
        assert report.is_clean is False
        assert len(report.added) > 0

    def test_verify_detects_removed_file(self, tmp_path: Path):
        guard = self._make_guard(tmp_path)
        ke_dir = self._make_ke_dir(tmp_path)
        src_dir = self._make_src_dir(tmp_path)
        ke_file = ke_dir / "KE-001.md"
        ke_file.write_text("content", encoding="utf-8")
        guard.generate()
        ke_file.unlink()
        report = guard.verify(layer=1)
        assert report.is_clean is False
        assert len(report.removed) > 0

    def test_verify_detects_mismatch(self, tmp_path: Path):
        guard = self._make_guard(tmp_path)
        ke_dir = self._make_ke_dir(tmp_path)
        src_dir = self._make_src_dir(tmp_path)
        ke_file = ke_dir / "KE-001.md"
        ke_file.write_text("original", encoding="utf-8")
        guard.generate()
        ke_file.write_text("tampered", encoding="utf-8")
        report = guard.verify(layer=1)
        assert report.is_clean is False
        assert len(report.mismatches) > 0

    def test_verify_layer2(self, tmp_path: Path):
        guard = self._make_guard(tmp_path)
        ke_dir = self._make_ke_dir(tmp_path)
        src_dir = self._make_src_dir(tmp_path)
        (src_dir / "core.py").write_text("src code", encoding="utf-8")
        guard.generate()
        report = guard.verify(layer=2)
        assert report.is_clean is True

    def test_manifest_path_creates_snap_dir(self, tmp_path: Path):
        guard = self._make_guard(tmp_path)
        mp = guard.manifest_path
        assert mp.parent.exists()

    def test_ke_dir_and_kb_src_dir(self, tmp_path: Path):
        guard = self._make_guard(tmp_path)
        assert str(guard.ke_dir).endswith("01_raw_intake")
        assert str(guard.kb_src_dir).endswith("kb")


class TestHashEntry:
    def test_creation(self):
        e = HashEntry(path="a.md", sha256="abc", size=10, mtime="2025-01-01")
        assert e.path == "a.md"
        assert e.size == 10


class TestDriftReport:
    def test_defaults(self):
        r = DriftReport(timestamp="t", layer=1, total=0, matched=0)
        assert r.is_clean is True
        assert r.mismatches == []
        assert r.added == []
        assert r.removed == []
