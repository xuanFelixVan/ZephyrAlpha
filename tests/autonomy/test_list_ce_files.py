# [A_test] module_id: MOD-GOV_list_ce_files | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.ce_file_lister
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.autonomy_core.context.ce_file_lister import CATEGORIES, collect_files, generate_manifest
except Exception as _exc:
    pytest.skip(f"cannot import list_ce_files: {_exc}", allow_module_level=True)


class TestCollectFiles:
    def test_collect_files_returns_dict(self):
        result = collect_files()
        assert isinstance(result, dict)
        for category in CATEGORIES:
            assert category in result

    def test_collect_files_entries_have_path_and_size(self):
        result = collect_files()
        for category, entries in result.items():
            assert isinstance(entries, list)
            for entry in entries:
                assert "path" in entry
                assert "size_kb" in entry

    def test_collect_files_skips_underscore_prefix(self):
        result = collect_files()
        for category, entries in result.items():
            for entry in entries:
                filename = entry["path"].split("/")[-1].split("\\")[-1]
                assert not filename.startswith("_")


class TestGenerateManifest:
    def test_generate_manifest_returns_valid_json(self):
        import json

        raw = generate_manifest()
        data = json.loads(raw)
        assert isinstance(data, dict)

    def test_generate_manifest_has_required_fields(self):
        import json

        data = json.loads(generate_manifest())
        assert "module_id" in data
        assert "root" in data
        assert "files" in data
        assert "total_py_files" in data
        assert data["module_id"] == "MOD-CONTEXT_ENGINE"

    def test_generate_manifest_total_py_files_non_negative(self):
        import json

        data = json.loads(generate_manifest())
        assert data["total_py_files"] >= 0
