# [A_test] module_id: SRC-TST-0908 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_system_master/blueprint.md | §
# [MODULE] tests.test_file_autoregister
# [INVARIANTS] register writes to manifest; uses atomic write pattern; returns dict with script_name and registered=True
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] register requires valid manifest_path; yaml.safe_load on corrupt file raises exception
# [TESTS] pytest tests/test_file_autoregister.py
# [TTL] task_bound

from pathlib import Path

import yaml

from zephyr.autonomy_core.file_autoregister import FileAutoRegister


class TestFileAutoRegisterInstantiation:
    def test_default_manifest_path(self):
        far = FileAutoRegister()
        assert far.manifest_path is not None
        assert isinstance(far.manifest_path, Path)

    def test_custom_manifest_path(self):
        custom = Path("/tmp/custommanifest.yaml")
        far = FileAutoRegister(manifest_path=custom)
        assert far.manifest_path == custom

    def test_none_manifest_path_uses_default(self):
        far = FileAutoRegister(manifest_path=None)
        assert far.manifest_path is not None


class TestRegister:
    def _write_manifest(self, tmp_path, data=None):
        manifest_path = tmp_path / "script-manifest.yaml"
        content = yaml.dump(data or {}, allow_unicode=True, default_flow_style=False, sort_keys=False)
        manifest_path.write_text(content, encoding="utf-8")
        return manifest_path

    def test_register_returns_success_dict(self, tmp_path):
        manifest_path = self._write_manifest(tmp_path)
        far = FileAutoRegister(manifest_path=manifest_path)
        result = far.register("scripts/test_script.py", module="test_mod")
        assert result["registered"] is True
        assert result["script_name"] == "test_script"

    def test_register_writes_to_manifest(self, tmp_path):
        manifest_path = self._write_manifest(tmp_path)
        far = FileAutoRegister(manifest_path=manifest_path)
        far.register("scripts/my_script.py", module="my_mod")
        with open(manifest_path, encoding="utf-8") as f:
            manifest = yaml.safe_load(f)
        assert "my_script" in manifest["scripts"]
        assert manifest["scripts"]["my_script"]["path"] == "scripts/my_script.py"
        assert manifest["scripts"]["my_script"]["module"] == "my_mod"
        assert manifest["scripts"]["my_script"]["registered_by"] == "file_autoregister"

    def test_register_default_module_is_unknown(self, tmp_path):
        manifest_path = self._write_manifest(tmp_path)
        far = FileAutoRegister(manifest_path=manifest_path)
        far.register("scripts/no_mod_script.py")
        with open(manifest_path, encoding="utf-8") as f:
            manifest = yaml.safe_load(f)
        assert manifest["scripts"]["no_mod_script"]["module"] == "unknown"

    def test_register_preserves_existing_entries(self, tmp_path):
        existing = {"scripts": {"old_script": {"path": "old.py", "module": "old"}}}
        manifest_path = self._write_manifest(tmp_path, existing)
        far = FileAutoRegister(manifest_path=manifest_path)
        far.register("scripts/new_script.py", module="new")
        with open(manifest_path, encoding="utf-8") as f:
            manifest = yaml.safe_load(f)
        assert "old_script" in manifest["scripts"]
        assert "new_script" in manifest["scripts"]

    def test_register_overwrites_duplicate_name(self, tmp_path):
        existing = {"scripts": {"dup_script": {"path": "old.py", "module": "old"}}}
        manifest_path = self._write_manifest(tmp_path, existing)
        far = FileAutoRegister(manifest_path=manifest_path)
        far.register("scripts/dup_script.py", module="updated")
        with open(manifest_path, encoding="utf-8") as f:
            manifest = yaml.safe_load(f)
        assert manifest["scripts"]["dup_script"]["module"] == "updated"

    def test_register_with_path_only_no_parent_dirs(self, tmp_path):
        manifest_path = self._write_manifest(tmp_path)
        far = FileAutoRegister(manifest_path=manifest_path)
        result = far.register("standalone.py", module="solo")
        assert result["script_name"] == "standalone"

    def test_register_empty_file_path(self, tmp_path):
        manifest_path = self._write_manifest(tmp_path)
        far = FileAutoRegister(manifest_path=manifest_path)
        result = far.register("", module="empty")
        assert result["script_name"] == ""
        assert result["registered"] is True

    def test_register_creates_manifest_if_missing(self, tmp_path):
        manifest_path = tmp_path / "newmanifest.yaml"
        manifest_path.write_text("", encoding="utf-8")
        far = FileAutoRegister(manifest_path=manifest_path)
        result = far.register("scripts/fresh.py", module="fresh")
        assert result["registered"] is True
        with open(manifest_path, encoding="utf-8") as f:
            manifest = yaml.safe_load(f)
        assert "fresh" in manifest["scripts"]
