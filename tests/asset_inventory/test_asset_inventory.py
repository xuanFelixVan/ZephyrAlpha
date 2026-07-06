# [A_test] module_id: SRC-TST-0336 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain_infrastructure_operations/asset_inventory/blueprint.md | §test
# [MODULE] zephyr.asset_inventory
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_asset_inventory.py
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime

import pytest

models = pytest.importorskip("zephyr.infrastructure.asset_inventory.models")
dependency = pytest.importorskip("zephyr.infrastructure.asset_inventory.dependency")
metadata_mod = pytest.importorskip("zephyr.infrastructure.asset_inventory.metadata")
trust_anchor = pytest.importorskip("zephyr.infrastructure.asset_inventory.trust_anchor")


class TestAssetType:
    def test_enum_values(self):
        assert models.AssetType.MODULE.value == "module"
        assert models.AssetType.SCRIPT.value == "script"
        assert models.AssetType.GATE.value == "gate"
        assert models.AssetType.DOC.value == "doc"
        assert models.AssetType.CONFIG.value == "config"
        assert models.AssetType.TEST.value == "test"
        assert models.AssetType.DATA.value == "data"
        assert models.AssetType.REGISTRY.value == "registry"
        assert models.AssetType.UNKNOWN.value == "unknown"

    def test_from_string(self):
        assert models.AssetType("module") is models.AssetType.MODULE

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            models.AssetType("nonexistent")


class TestAssetLayer:
    def test_enum_values(self):
        assert models.AssetLayer.L00.value == "L00"
        assert models.AssetLayer.L01.value == "L01"
        assert models.AssetLayer.CROSS_LAYER.value == "cross_layer"

    def test_all_layers_present(self):
        expected = {"L00", "L01", "L02", "L03", "L04", "cross_layer"}
        actual = {e.value for e in models.AssetLayer}
        assert expected == actual


class TestAssetStatus:
    def test_enum_values(self):
        assert models.AssetStatus.ACTIVE.value == "active"
        assert models.AssetStatus.GHOST.value == "ghost"
        assert models.AssetStatus.ORPHAN.value == "orphan"

    def test_from_string(self):
        assert models.AssetStatus("stale") is models.AssetStatus.STALE


class TestPriority:
    def test_enum_values(self):
        assert models.Priority.P0.value == "P0"
        assert models.Priority.P3.value == "P3"

    def test_ordering(self):
        assert models.Priority.P0.value < models.Priority.P3.value


class TestRawFileEntry:
    def test_create_valid(self):
        entry = models.RawFileEntry(
            relative_path="src/zephyr/foo.py",
            absolute_path="/abs/src/zephyr/foo.py",
            file_name="foo.py",
            extension=".py",
            size_bytes=1024,
            mtime_utc=datetime.now(UTC),
            sha256="abc123",
        )
        assert entry.relative_path == "src/zephyr/foo.py"
        assert entry.is_binary is False

    def test_missing_required_field_raises(self):
        with pytest.raises(Exception):
            models.RawFileEntry(relative_path="x.py")


class TestScanResult:
    def test_create_with_defaults(self):
        sr = models.ScanResult(
            scan_id="SCAN-20260101-001",
            total_files=10,
            total_size_bytes=5000,
        )
        assert sr.scan_mode == "full"
        assert sr.entries == []
        assert sr.errors == []
        assert sr.completed_at is None

    def test_with_entries(self):
        entry = models.RawFileEntry(
            relative_path="a.py",
            absolute_path="/a.py",
            file_name="a.py",
            extension=".py",
            size_bytes=100,
            mtime_utc=datetime.now(UTC),
            sha256="deadbeef",
        )
        sr = models.ScanResult(
            scan_id="SCAN-001",
            total_files=1,
            total_size_bytes=100,
            entries=[entry],
        )
        assert len(sr.entries) == 1


class TestClassifiedAsset:
    def test_create_with_defaults(self):
        asset = models.ClassifiedAsset(
            relative_path="src/zephyr/bar.py",
            asset_type=models.AssetType.MODULE,
            size_bytes=2048,
            mtime_utc=datetime.now(UTC),
            sha256="cafe1234",
        )
        assert asset.layer is models.AssetLayer.CROSS_LAYER
        assert asset.status is models.AssetStatus.ACTIVE
        assert asset.priority is models.Priority.P3
        assert asset.classification_confidence == 1.0

    def test_confidence_bounds(self):
        with pytest.raises(Exception):
            models.ClassifiedAsset(
                relative_path="x.py",
                asset_type=models.AssetType.MODULE,
                size_bytes=100,
                mtime_utc=datetime.now(UTC),
                sha256="abc",
                classification_confidence=1.5,
            )


class TestDependencyNode:
    def test_create_defaults(self):
        node = dependency.DependencyNode(file_path="src/zephyr/core.py")
        assert node.layer == "cross_layer"
        assert node.imported_by_count == 0
        assert node.imports_count == 0
        assert node.is_leaf is False
        assert node.is_root is True


class TestDependencyEdge:
    def test_create(self):
        edge = dependency.DependencyEdge(
            from_file="a.py",
            to_module="zephyr.trading.orchestrator.core",
        )
        assert edge.import_type == "absolute"
        assert edge.line_number == 0


class TestDependencyGraph:
    def test_create_defaults(self):
        graph = dependency.DependencyGraph()
        assert graph.total_files == 0
        assert graph.total_edges == 0
        assert graph.nodes == {}
        assert graph.edges == []
        assert graph.circular_dependencies == []

    def test_with_nodes_and_edges(self):
        node = dependency.DependencyNode(file_path="a.py", imported_by_count=3)
        edge = dependency.DependencyEdge(from_file="b.py", to_module="a")
        graph = dependency.DependencyGraph(
            total_files=2,
            total_edges=1,
            nodes={"a.py": node},
            edges=[edge],
        )
        assert "a.py" in graph.nodes
        assert len(graph.edges) == 1


class TestDependencyExtractor:
    def test_extract_simple_import(self):
        ext = dependency.DependencyExtractor()
        code = "import os\nimport sys\n"
        edges = ext.extract("test.py", code)
        assert len(edges) >= 2
        assert any(e.to_module == "os" for e in edges)
        assert any(e.to_module == "sys" for e in edges)

    def test_extract_from_import(self):
        ext = dependency.DependencyExtractor()
        code = "from zephyr.trading.orchestrator.core import foo\n"
        edges = ext.extract("test.py", code)
        assert len(edges) == 1
        assert edges[0].to_module == "zephyr.trading.orchestrator.core.foo"
        assert edges[0].import_type == "absolute"

    def test_extract_syntax_error_returns_empty(self):
        ext = dependency.DependencyExtractor()
        edges = ext.extract("bad.py", "def (broken syntax")
        assert edges == []

    def test_extract_empty_code(self):
        ext = dependency.DependencyExtractor()
        edges = ext.extract("empty.py", "")
        assert edges == []

    def test_classify_stdlib(self):
        ext = dependency.DependencyExtractor()
        result = ext._classify_import("os")
        assert result == "stdlib"

    def test_classify_project_import(self):
        ext = dependency.DependencyExtractor()
        result = ext._classify_import("zephyr.trading.orchestrator.core")
        assert result == "absolute"

    def test_classify_third_party(self):
        ext = dependency.DependencyExtractor()
        result = ext._classify_import("numpy")
        assert result == "third_party"


class TestPriorityFromDependency:
    def test_p0(self):
        assert dependency.priority_from_dependency(5) == "P0"

    def test_p1(self):
        assert dependency.priority_from_dependency(2) == "P1"

    def test_p2(self):
        assert dependency.priority_from_dependency(1) == "P2"

    def test_p3(self):
        assert dependency.priority_from_dependency(0) == "P3"


class TestGitAssetMetadata:
    def test_create_defaults(self):
        meta = metadata_mod.GitAssetMetadata(file_path="src/zephyr/foo.py")
        assert meta.total_commits == 0
        assert meta.authors == []
        assert meta.ai_commits_ratio == 0.0

    def test_with_values(self):
        now = datetime.now(UTC)
        meta = metadata_mod.GitAssetMetadata(
            file_path="a.py",
            first_commit_sha="abc",
            first_commit_date=now,
            last_commit_sha="def",
            last_commit_date=now,
            total_commits=5,
            authors=["alice", "bob"],
        )
        assert meta.total_commits == 5
        assert len(meta.authors) == 2


class TestGitCommitInfo:
    def test_create(self):
        info = metadata_mod.GitCommitInfo(
            sha="deadbeef",
            author="alice",
            date=datetime.now(UTC),
            message="initial commit",
        )
        assert info.lines_added == 0
        assert info.lines_deleted == 0


class TestGitMetadataExtractor:
    def test_is_ai_commit(self):
        assert metadata_mod.GitMetadataExtractor._is_ai_commit("[AI] auto fix")
        assert metadata_mod.GitMetadataExtractor._is_ai_commit("generated by copilot")
        assert not metadata_mod.GitMetadataExtractor._is_ai_commit("manual fix")

    def test_parse_date_valid(self):
        result = metadata_mod.GitMetadataExtractor._parse_date("2026-01-15 10:30:00")
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 15

    def test_parse_date_invalid(self):
        result = metadata_mod.GitMetadataExtractor._parse_date("not-a-date")
        assert result.year == datetime.min.year


class TestTrustLevel:
    def test_enum_values(self):
        assert trust_anchor.TrustLevel.FULL.value == "FULL"
        assert trust_anchor.TrustLevel.PARTIAL.value == "PARTIAL"
        assert trust_anchor.TrustLevel.BROKEN.value == "BROKEN"


class TestTrustAnchorResult:
    def test_create_defaults(self):
        result = trust_anchor.TrustAnchorResult()
        assert result.git_ok is False
        assert result.test_ok is False
        assert result.audit_ok is False
        assert result.trust_level is trust_anchor.TrustLevel.BROKEN
        assert result.recommendation == ""

    def test_with_values(self):
        result = trust_anchor.TrustAnchorResult(
            git_ok=True,
            test_ok=True,
            audit_ok=True,
            trust_level=trust_anchor.TrustLevel.FULL,
            recommendation="all good",
        )
        assert result.trust_level is trust_anchor.TrustLevel.FULL


class TestTripleTrustAnchorGate:
    def test_calculate_trust_full(self):
        assert trust_anchor.TripleTrustAnchorGate._calculate_trust({"git_ok": True, "test_ok": True, "audit_ok": True}) is trust_anchor.TrustLevel.FULL

    def test_calculate_trust_partial(self):
        assert trust_anchor.TripleTrustAnchorGate._calculate_trust({"git_ok": True, "test_ok": True, "audit_ok": False}) is trust_anchor.TrustLevel.PARTIAL
        assert trust_anchor.TripleTrustAnchorGate._calculate_trust({"git_ok": True, "test_ok": False, "audit_ok": True}) is trust_anchor.TrustLevel.PARTIAL

    def test_calculate_trust_broken(self):
        assert (
            trust_anchor.TripleTrustAnchorGate._calculate_trust({"git_ok": False, "test_ok": False, "audit_ok": False}) is trust_anchor.TrustLevel.BROKEN
        )

    def test_recommend_full(self):
        rec = trust_anchor.TripleTrustAnchorGate._recommend(trust_anchor.TrustLevel.FULL)
        assert "完全可信" in rec

    def test_recommend_broken(self):
        rec = trust_anchor.TripleTrustAnchorGate._recommend(trust_anchor.TrustLevel.BROKEN)
        assert "不可信" in rec


class TestBypassState:
    def test_create_defaults(self):
        state = trust_anchor.BypassState()
        assert state.enabled is False
        assert state.reason == ""
        assert state.is_expired is False

    def test_expired(self):
        state = trust_anchor.BypassState(is_expired=True)
        assert state.is_expired is True


class TestBypassManager:
    def test_no_override_file_returns_default(self, tmp_path):
        bm = trust_anchor.BypassManager(project_root=tmp_path)
        state = bm.get_bypass_state()
        assert state.enabled is False

    def test_is_bypass_active_no_override(self, tmp_path):
        bm = trust_anchor.BypassManager(project_root=tmp_path)
        assert bm.is_bypass_active() is False

    def test_remove_override_nonexistent(self, tmp_path):
        bm = trust_anchor.BypassManager(project_root=tmp_path)
        assert bm.remove_override() is False
