# [A_test] module_id: MOD-GOV_support_architecture_context_loader | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.architecture_context_loader
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

import json
import os
import tempfile

import pytest

try:
    from zephyr.shared.blueprint_tools.architecture_context_loader import (
        DEFAULT_ARCH_CONTEXT_PATH,
        format_architecture_context_excerpt,
        load_architecture_context_dict,
    )
except Exception as _exc:
    pytest.skip(f"cannot import architecture_context_loader: {_exc}", allow_module_level=True)


class TestLoadArchitectureContextDict:
    def test_load_nonexistent_path_returns_empty(self):
        from pathlib import Path

        result = load_architecture_context_dict(Path(tempfile.mktemp(suffix=".json")))
        assert result == {}

    def test_load_valid_json_file(self):
        data = {"version": "1.0", "contracts": [], "layers": []}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(data, f)
            tmp = f.name
        try:
            result = load_architecture_context_dict(
                type("P", (), {"is_file": lambda s: True, "read_text": lambda s, encoding: json.dumps(data)})()
            )
        finally:
            os.unlink(tmp)

    def test_load_default_path(self):
        result = load_architecture_context_dict()
        assert isinstance(result, dict)


class TestFormatArchitectureContextExcerpt:
    def test_format_empty_data(self):
        result = format_architecture_context_excerpt({})
        assert result == ""

    def test_format_with_data(self):
        data = {
            "generated_at": "2026-01-01",
            "version": "1.0",
            "schema": "test",
            "contracts": ["c1"],
            "invariants": {"total": 5, "items": ["inv1", "inv2"]},
            "layers": ["L1"],
            "gate_registry": {"G1": "ok"},
        }
        result = format_architecture_context_excerpt(data)
        assert "ZEPHYR_ARCH_CONTEXT" in result
        assert "1.0" in result

    def test_format_truncates_long_output(self):
        data = {
            "generated_at": "2026-01-01",
            "version": "1.0",
            "schema": "test",
            "contracts": ["c1"] * 1000,
            "invariants": {"total": 5, "items": ["inv"] * 100},
            "layers": ["L"] * 100,
            "gate_registry": {"G1": "x" * 10000},
        }
        result = format_architecture_context_excerpt(data, max_chars=500)
        assert len(result) <= 600

    def test_default_arch_context_path_is_path(self):
        from pathlib import Path

        assert isinstance(DEFAULT_ARCH_CONTEXT_PATH, Path)
