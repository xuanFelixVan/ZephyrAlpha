# [A_test] module_id: SRC-TST-1345 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_orphan_scanner
# [INVARIANTS] 孤儿扫描不可跳过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_orphan_scanner.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_drift.orphan_scanner import (
    OrphanResource,
    find_orphan_data,
    find_orphan_docs,
    find_orphan_scripts,
    scan_orphan_resources,
)


class TestOrphanResource:
    def test_defaults(self):
        r = OrphanResource(
            resource_id="orphan-script-test",
            resource_path="/path/test.py",
            resource_type="orphan_script",
            description="not in manifest",
        )
        assert r.severity == "MINOR"
        assert r.detected_at is not None

    def test_to_dict(self):
        r = OrphanResource(
            resource_id="orphan-data-x",
            resource_path="/data/x.db",
            resource_type="orphan_data",
            description="unreferenced",
            severity="MAJOR",
        )
        d = r.to_dict()
        assert d["resource_id"] == "orphan-data-x"
        assert d["resource_type"] == "orphan_data"
        assert d["severity"] == "MAJOR"
        assert "detected_at" not in d


class TestFindOrphanScripts:
    def test_no_scripts_dir(self, tmp_path):
        result = find_orphan_scripts(str(tmp_path))
        assert result == []

    def test_scripts_without_manifest(self, tmp_path):
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "orphan_script.py").write_text("print('hello')", encoding="utf-8")
        result = find_orphan_scripts(str(tmp_path))
        assert len(result) >= 1
        assert result[0].resource_type == "orphan_script"

    def test_scripts_with_manifest(self, tmp_path):
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "registered.py").write_text("print('ok')", encoding="utf-8")
        manifest = scripts_dir / "script-manifest.yaml"
        manifest.write_text(
            "scripts:\n  - path: scripts/registered.py\n",
            encoding="utf-8",
        )
        result = find_orphan_scripts(str(tmp_path))
        registered_paths = [r.resource_path for r in result]
        assert not any("registered.py" in p for p in registered_paths)


class TestFindOrphanData:
    def test_no_data_dir(self, tmp_path):
        result = find_orphan_data(str(tmp_path))
        assert result == []

    def test_unreferenced_data_file(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "orphan_data.db").write_text("data", encoding="utf-8")
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("print('hello')", encoding="utf-8")
        result = find_orphan_data(str(tmp_path))
        assert len(result) >= 1
        assert result[0].resource_type == "orphan_data"

    def test_referenced_data_not_orphan(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "referenceditem.db").write_text("data", encoding="utf-8")
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("referenceditem", encoding="utf-8")
        result = find_orphan_data(str(tmp_path))
        referenced = [r for r in result if "referenceditem" in r.resource_path]
        assert len(referenced) == 0


class TestFindOrphanDocs:
    def test_no_docs_dir(self, tmp_path):
        result = find_orphan_docs(str(tmp_path))
        assert result == []

    def test_orphan_doc_detected(self, tmp_path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "orphan_doc.md").write_text("# Orphan", encoding="utf-8")
        result = find_orphan_docs(str(tmp_path))
        assert len(result) >= 1
        assert result[0].resource_type == "orphan_doc"

    def test_blueprint_not_flagged(self, tmp_path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "blueprint.md").write_text("# Blueprint", encoding="utf-8")
        result = find_orphan_docs(str(tmp_path))
        blueprint_orphans = [r for r in result if "blueprint.md" in r.resource_path]
        assert len(blueprint_orphans) == 0


class TestScanOrphanResources:
    def test_returns_dict_structure(self, tmp_path):
        result = scan_orphan_resources(str(tmp_path))
        assert "scripts" in result
        assert "data" in result
        assert "docs" in result
        assert "summary" in result

    def test_summary_counts(self, tmp_path):
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "orphan.py").write_text("print('x')", encoding="utf-8")
        result = scan_orphan_resources(str(tmp_path))
        summary = result["summary"]
        assert "total" in summary
        assert "scripts" in summary
        assert "data" in summary
        assert "docs" in summary
        assert summary["total"] == summary["scripts"] + summary["data"] + summary["docs"]
