# [A_test] module_id: SRC-TST-0211 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain-autonomy_core/rollback-system/blueprint.md | §
# [MODULE] tests.test__manifest_
# [INVARIANTS] MANIFEST dict structure must have required top-level keys
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError on missing keys; TypeError on wrong types
# [TESTS] tests/test__manifest_.py

from __future__ import annotations

from zephyr.governance._manifest import MANIFEST


class TestManifestStructure:
    def test_manifest_is_dict(self):
        assert isinstance(MANIFEST, dict)

    def test_manifest_has_required_top_level_keys(self):
        required_keys = {
            "module_id",
            "version",
            "code_directory",
            "files",
            "directories",
            "total_py_files",
            "total_dirs",
        }
        assert required_keys.issubset(set(MANIFEST.keys()))

    def test_manifest_module_id(self):
        assert MANIFEST["module_id"] == "MOD-INF-021"

    def test_manifest_version_is_string(self):
        assert isinstance(MANIFEST["version"], str)
        assert len(MANIFEST["version"]) > 0

    def test_manifest_code_directory_is_string(self):
        assert isinstance(MANIFEST["code_directory"], str)
        assert "rollback" in MANIFEST["code_directory"]


class TestManifestFiles:
    def test_files_is_list(self):
        assert isinstance(MANIFEST["files"], list)

    def test_files_non_empty(self):
        assert len(MANIFEST["files"]) > 0

    def test_each_file_entry_has_required_keys(self):
        required_file_keys = {"file", "responsibility"}
        for entry in MANIFEST["files"]:
            assert required_file_keys.issubset(set(entry.keys())), f"Missing keys in {entry.get('file', 'UNKNOWN')}"

    def test_each_file_entry_file_is_string(self):
        for entry in MANIFEST["files"]:
            assert isinstance(entry["file"], str), f"file field not string in {entry}"
            assert entry["file"].endswith(".py"), f"file field does not end with .py: {entry['file']}"

    def test_each_file_entry_responsibility_is_string(self):
        for entry in MANIFEST["files"]:
            assert isinstance(entry["responsibility"], str), f"responsibility not string in {entry['file']}"

    def test_total_py_files_matches_file_count(self):
        assert MANIFEST["total_py_files"] == len(MANIFEST["files"])


class TestManifestDirectories:
    def test_directories_is_list(self):
        assert isinstance(MANIFEST["directories"], list)

    def test_directories_non_empty(self):
        assert len(MANIFEST["directories"]) > 0

    def test_each_directory_entry_has_required_keys(self):
        required_dir_keys = {"path", "description"}
        for entry in MANIFEST["directories"]:
            assert required_dir_keys.issubset(set(entry.keys())), f"Missing keys in dir {entry.get('path', 'UNKNOWN')}"

    def test_each_directory_path_is_string(self):
        for entry in MANIFEST["directories"]:
            assert isinstance(entry["path"], str), f"path not string in {entry}"

    def test_total_dirs_matches_directory_count(self):
        assert MANIFEST["total_dirs"] == len(MANIFEST["directories"])


class TestManifestBoundaryCases:
    def test_manifest_no_empty_file_names(self):
        for entry in MANIFEST["files"]:
            assert len(entry["file"].strip()) > 0, "Empty file name found"

    def test_manifest_no_empty_responsibility(self):
        for entry in MANIFEST["files"]:
            assert len(entry["responsibility"].strip()) > 0, f"Empty responsibility for {entry['file']}"

    def test_manifest_no_duplicate_file_entries(self):
        file_names = [entry["file"] for entry in MANIFEST["files"]]
        assert len(file_names) == len(set(file_names)), "Duplicate file entries found"

    def test_manifest_no_duplicate_directory_entries(self):
        dir_paths = [entry["path"] for entry in MANIFEST["directories"]]
        assert len(dir_paths) == len(set(dir_paths)), "Duplicate directory entries found"
