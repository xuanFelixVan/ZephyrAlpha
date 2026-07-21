# [A_test] module_id: MOD-GOV_architecture_context_loader | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_architecture_context_loader
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_architecture_context_loader.py -q
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path

from zephyr.shared.blueprint_tools.architecture_context_loader import (
    DEFAULT_ARCH_CONTEXT_PATH,
    format_architecture_context_excerpt,
    load_architecture_context_dict,
)


class TestLoadArchitectureContextDict:
    def test_returns_empty_dict_when_file_not_found(self, tmp_path: Path):
        missing = tmp_path / "nonexistent.json"
        result = load_architecture_context_dict(path=missing)
        assert result == {}

    def test_returns_parsed_json_from_valid_file(self, tmp_path: Path):
        data = {"version": "1.0", "generated_at": "2026-01-01", "schema": "arch"}
        f = tmp_path / "arch.json"
        f.write_text(json.dumps(data), encoding="utf-8")
        result = load_architecture_context_dict(path=f)
        assert result == data

    def test_uses_default_path_when_none(self):
        result = load_architecture_context_dict(path=None)
        if DEFAULT_ARCH_CONTEXT_PATH.is_file():
            assert isinstance(result, dict)
            assert len(result) > 0
        else:
            assert result == {}

    def test_reads_utf8_encoded_file(self, tmp_path: Path):
        data = {"invariants": {"items": ["不变量一", "不变量二"]}}
        f = tmp_path / "utf8.json"
        f.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        result = load_architecture_context_dict(path=f)
        assert result["invariants"]["items"][0] == "不变量一"


class TestFormatArchitectureContextExcerpt:
    def test_returns_empty_string_for_empty_data(self):
        assert format_architecture_context_excerpt({}) == ""

    def test_returns_empty_string_for_none_data(self):
        assert format_architecture_context_excerpt(None) == ""

    def test_includes_header_prefix(self):
        data = {"version": "1.0", "generated_at": "2026-01-01"}
        result = format_architecture_context_excerpt(data)
        assert result.startswith("--- ZEPHYR_ARCH_CONTEXT ---\n")

    def test_truncates_when_exceeding_max_chars(self):
        items = [f"item_{i}" * 100 for i in range(200)]
        data = {"layers": items, "invariants": {"items": items}}
        result = format_architecture_context_excerpt(data, max_chars=500)
        assert "…[truncated]" in result
        full_json = json.dumps(data, ensure_ascii=False, indent=2)
        assert len(result) < len(full_json)

    def test_limits_invariants_items_to_eight(self):
        data = {"invariants": {"items": [f"inv_{i}" for i in range(20)], "total": 20}}
        result = format_architecture_context_excerpt(data)
        parsed = json.loads(
            result.split("--- ZEPHYR_ARCH_CONTEXT ---\n", 1)[1].replace("…[truncated]", "").strip()
            if "…[truncated]" in result
            else result.split("--- ZEPHYR_ARCH_CONTEXT ---\n", 1)[1]
        )
        assert len(parsed["invariants"]["items"]) <= 8

    def test_limits_layers_to_twenty_four(self):
        data = {"layers": [f"layer_{i}" for i in range(50)]}
        result = format_architecture_context_excerpt(data)
        body = result.split("--- ZEPHYR_ARCH_CONTEXT ---\n", 1)[1]
        if "…[truncated]" in body:
            body = body.replace("…[truncated]", "").rstrip()
        parsed = json.loads(body)
        assert len(parsed["layers"]) <= 24

    def test_preserves_top_level_keys(self):
        data = {
            "version": "2.0",
            "generated_at": "2026-05-23",
            "schema": "v2",
            "contracts": {"c1": "val"},
            "gate_registry": {"g1": "val"},
        }
        result = format_architecture_context_excerpt(data)
        assert '"version": "2.0"' in result
        assert '"generated_at": "2026-05-23"' in result
        assert '"schema": "v2"' in result
