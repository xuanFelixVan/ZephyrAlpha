# [A_test] module_id: SRC-TST-1788 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_version_manifest
# [INVARIANTS] get_version returns v0.0.0 for unknown; get_path returns empty str for unknown
# [MODIFY-GUARD] src/zephyr/orchestrator/version_manifest.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] get_version/get_path/list_systems never raise
# [TESTS] tests/test_version_manifest.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.orchestrator.governance.version_manifest import VERSION_MANIFEST, VersionManifest


class TestVersionManifestInstantiation:
    def test_create_instance(self):
        vm = VersionManifest()
        assert vm is not None


class TestGetVersion:
    def test_known_system_returns_version(self):
        vm = VersionManifest()
        version = vm.get_version("orchestrator")
        assert version.startswith("v")

    def test_unknown_system_returns_default(self):
        vm = VersionManifest()
        assert vm.get_version("nonexistent") == "v0.0.0"

    def test_empty_string_returns_default(self):
        vm = VersionManifest()
        assert vm.get_version("") == "v0.0.0"


class TestGetPath:
    def test_known_system_returns_path(self):
        vm = VersionManifest()
        path = vm.get_path("orchestrator")
        assert "orchestrator" in path

    def test_unknown_system_returns_empty(self):
        vm = VersionManifest()
        assert vm.get_path("nonexistent") == ""

    def test_empty_string_returns_empty(self):
        vm = VersionManifest()
        assert vm.get_path("") == ""


class TestListSystems:
    def test_returns_list(self):
        vm = VersionManifest()
        systems = vm.list_systems()
        assert isinstance(systems, list)

    def test_contains_known_systems(self):
        vm = VersionManifest()
        systems = vm.list_systems()
        assert "orchestrator" in systems
        assert "gate_engine" in systems or "shared" in systems

    def test_all_systems_have_version_and_path(self):
        vm = VersionManifest()
        for sys_name in vm.list_systems():
            assert vm.get_version(sys_name) != "v0.0.0"
            assert vm.get_path(sys_name) != ""


class TestVersionManifestData:
    def test_manifest_is_dict(self):
        assert isinstance(VERSION_MANIFEST, dict)

    def test_manifest_has_entries(self):
        assert len(VERSION_MANIFEST) > 0

    def test_each_entry_has_version_and_path(self):
        for key, val in VERSION_MANIFEST.items():
            assert "version" in val
            assert "path" in val


class TestBoundary:
    def test_none_like_key(self):
        vm = VersionManifest()
        assert vm.get_version("None") == "v0.0.0"
        assert vm.get_path("None") == ""

    def test_list_systems_no_duplicates(self):
        vm = VersionManifest()
        systems = vm.list_systems()
        assert len(systems) == len(set(systems))
