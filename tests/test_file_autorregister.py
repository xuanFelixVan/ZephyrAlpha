# [A_test] module_id: SRC-TST-0909 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_file_autorregister
# [INVARIANTS] register must produce valid YAML; manifest_path must be Path or None
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FileNotFoundError on missing manifest dir; yaml.YAMLError on corrupt input
# [TESTS] tests/test_file_autorregister.py
# [TTL] task_bound

from pathlib import Path

import pytest
import yaml

from zephyr.autonomy_core.file_autorregister import FileAutoRegister


def _make_manifest(tmp_path, content=None):
    p = tmp_path / "manifest.yaml"
    if content is not None:
        p.write_text(yaml.dump(content, allow_unicode=True), encoding="utf-8")
    else:
        p.write_text("", encoding="utf-8")
    return p


class TestFileAutoRegisterInit:
    def test_default_manifest_path(self):
        reg = FileAutoRegister()
        assert reg.manifest_path.name == "script-manifest.yaml"
        assert "scripts" in str(reg.manifest_path)

    def test_custom_manifest_path(self, tmp_path):
        custom = tmp_path / "custommanifest.yaml"
        reg = FileAutoRegister(manifest_path=custom)
        assert reg.manifest_path == custom

    def test_none_manifest_path_resolves_default(self):
        reg = FileAutoRegister(manifest_path=None)
        assert reg.manifest_path is not None
        assert isinstance(reg.manifest_path, Path)


class TestFileAutoRegisterRegister:
    def test_register_new_script(self, tmp_path):
        manifest = _make_manifest(tmp_path, {"scripts": {}})
        reg = FileAutoRegister(manifest_path=manifest)
        result = reg.register("scripts/governance/my_script.py")
        assert result["registered"] is True
        assert result["script_name"] == "my_script"
        data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
        assert "my_script" in data["scripts"]
        assert data["scripts"]["my_script"]["path"] == "scripts/governance/my_script.py"

    def test_register_overwrites_existing(self, tmp_path):
        manifest = _make_manifest(tmp_path, {"scripts": {"old_script": {"path": "x.py"}}})
        reg = FileAutoRegister(manifest_path=manifest)
        result = reg.register("scripts/governance/old_script.py")
        assert result["registered"] is True
        data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
        assert data["scripts"]["old_script"]["path"] == "scripts/governance/old_script.py"
        assert data["scripts"]["old_script"]["module"] == "agent-spec"

    def test_register_empty_manifest(self, tmp_path):
        manifest = _make_manifest(tmp_path)
        reg = FileAutoRegister(manifest_path=manifest)
        result = reg.register("scripts/new_tool.py")
        assert result["registered"] is True
        data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
        assert "new_tool" in data["scripts"]

    def test_register_preserves_other_entries(self, tmp_path):
        manifest = _make_manifest(tmp_path, {"scripts": {"existing": {"path": "a.py", "module": "other"}}})
        reg = FileAutoRegister(manifest_path=manifest)
        reg.register("scripts/another.py")
        data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
        assert "existing" in data["scripts"]
        assert "another" in data["scripts"]

    def test_register_stem_extraction(self, tmp_path):
        manifest = _make_manifest(tmp_path, {"scripts": {}})
        reg = FileAutoRegister(manifest_path=manifest)
        result = reg.register("scripts/deep/nested/my_file.py")
        assert result["script_name"] == "my_file"


class TestFileAutoRegisterBoundary:
    def test_register_nonexistent_manifest_dir(self, tmp_path):
        missing = tmp_path / "no_such_dir" / "manifest.yaml"
        reg = FileAutoRegister(manifest_path=missing)
        with pytest.raises(FileNotFoundError):
            reg.register("scripts/x.py")

    def test_register_path_with_spaces(self, tmp_path):
        manifest = _make_manifest(tmp_path, {"scripts": {}})
        reg = FileAutoRegister(manifest_path=manifest)
        result = reg.register("scripts/my script.py")
        assert result["registered"] is True
        assert result["script_name"] == "my script"

    def test_register_corrupt_manifest(self, tmp_path):
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text("{{invalid yaml::", encoding="utf-8")
        reg = FileAutoRegister(manifest_path=manifest)
        with pytest.raises(yaml.YAMLError):
            reg.register("scripts/x.py")
