# [A_test] module_id: SRC-TST-2002 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-619 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_contract_template_manager
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
Unit tests for contract_template_manager.py (T-2-31, C55)
==========================================================
Minimum: 10 tests
"""


from datetime import datetime
from pathlib import Path

import pytest

from zephyr.gov_enforcement.rule_enforcement.contract_template_manager import (
    ContractParameter,
    ContractTemplate,
    ContractTemplateManager,
)

_TS = datetime(2026, 4, 24, 12, 0, 0)


def _make_template(
    tool_name: str = "test_tool",
    version: str = "1.0.0",
    params: list[ContractParameter] | None = None,
    safety: str = "L",
) -> ContractTemplate:
    return ContractTemplate(
        tool_name=tool_name,
        version=version,
        parameters=params or [],
        safety_level=safety,
        created_at=_TS,
        updated_at=_TS,
    )


class TestContractParameter:
    def test_valid_parameter(self) -> None:
        p = ContractParameter(name="query", param_type="str", required=True, description="Search query")
        assert p.name == "query"
        assert p.param_type == "str"
        assert p.required is True

    def test_invalid_param_type(self) -> None:
        with pytest.raises(Exception, match="param_type"):
            ContractParameter(name="x", param_type="bytes")

    def test_default_values(self) -> None:
        p = ContractParameter(name="x", param_type="int")
        assert p.required is True
        assert p.description == ""
        assert p.default is None


class TestContractTemplate:
    def test_valid_template(self) -> None:
        t = _make_template()
        assert t.tool_name == "test_tool"
        assert t.version == "1.0.0"

    def test_duplicate_param_names_rejected(self) -> None:
        with pytest.raises(Exception, match="Duplicate"):
            ContractTemplate(
                tool_name="dup",
                parameters=[
                    ContractParameter(name="x", param_type="str"),
                    ContractParameter(name="x", param_type="int"),
                ],
                created_at=_TS,
                updated_at=_TS,
            )

    def test_invalid_version_format(self) -> None:
        with pytest.raises(Exception):
            ContractTemplate(
                tool_name="bad_ver",
                version="v1",
                created_at=_TS,
                updated_at=_TS,
            )

    def test_invalid_safety_level(self) -> None:
        with pytest.raises(Exception):
            ContractTemplate(
                tool_name="bad_safety",
                safety_level="X",
                created_at=_TS,
                updated_at=_TS,
            )


class TestContractTemplateManager:
    def test_register_and_get(self) -> None:
        mgr = ContractTemplateManager()
        t = _make_template(tool_name="search")
        mgr.register(t)
        result = mgr.get("search")
        assert result is not None
        assert result.tool_name == "search"

    def test_get_nonexistent(self) -> None:
        mgr = ContractTemplateManager()
        assert mgr.get("nope") is None

    def test_register_duplicate_same_version_raises(self) -> None:
        mgr = ContractTemplateManager()
        t1 = _make_template(tool_name="search", version="1.0.0")
        mgr.register(t1)
        with pytest.raises(ValueError, match="already registered"):
            mgr.register(t1)

    def test_register_upgrade_version(self) -> None:
        mgr = ContractTemplateManager()
        t1 = _make_template(tool_name="search", version="1.0.0")
        mgr.register(t1)
        t2 = _make_template(tool_name="search", version="2.0.0")
        mgr.register(t2)
        assert mgr.get("search").version == "2.0.0"

    def test_list_templates_sorted(self) -> None:
        mgr = ContractTemplateManager()
        mgr.register(_make_template(tool_name="zeta_tool"))
        mgr.register(_make_template(tool_name="alpha_tool"))
        names = [t.tool_name for t in mgr.list_templates()]
        assert names == ["alpha_tool", "zeta_tool"]

    def test_remove_existing(self) -> None:
        mgr = ContractTemplateManager()
        mgr.register(_make_template(tool_name="search"))
        assert mgr.remove("search") is True
        assert mgr.get("search") is None

    def test_remove_nonexistent(self) -> None:
        mgr = ContractTemplateManager()
        assert mgr.remove("nope") is False

    def test_validate_invocation_ok(self) -> None:
        mgr = ContractTemplateManager()
        t = _make_template(
            tool_name="search",
            params=[
                ContractParameter(name="query", param_type="str", required=True),
                ContractParameter(name="limit", param_type="int", required=False),
            ],
        )
        mgr.register(t)
        errors = mgr.validate_invocation("search", {"query": "test"})
        assert errors == []

    def test_validate_invocation_missing_required(self) -> None:
        mgr = ContractTemplateManager()
        t = _make_template(
            tool_name="search",
            params=[
                ContractParameter(name="query", param_type="str", required=True),
            ],
        )
        mgr.register(t)
        errors = mgr.validate_invocation("search", {})
        assert len(errors) == 1
        assert "Missing required" in errors[0]

    def test_validate_invocation_unknown_param(self) -> None:
        mgr = ContractTemplateManager()
        mgr.register(_make_template(tool_name="search"))
        errors = mgr.validate_invocation("search", {"bogus": 1})
        assert len(errors) == 1
        assert "Unknown parameter" in errors[0]

    def test_validate_invocation_unknown_tool(self) -> None:
        mgr = ContractTemplateManager()
        errors = mgr.validate_invocation("nope", {})
        assert len(errors) == 1
        assert "Unknown tool" in errors[0]

    def test_flush_and_load(self, tmp_path: Path) -> None:
        store = tmp_path / "contracts.json"
        mgr1 = ContractTemplateManager(store_path=store)
        mgr1.register(_make_template(tool_name="search"))
        mgr1.flush()

        mgr2 = ContractTemplateManager(store_path=store)
        loaded = mgr2.load()
        assert loaded == 1
        assert mgr2.get("search") is not None

    def test_flush_no_store_path(self) -> None:
        mgr = ContractTemplateManager()
        assert mgr.flush() == 0

    def test_load_no_file(self, tmp_path: Path) -> None:
        mgr = ContractTemplateManager(store_path=tmp_path / "nope.json")
        assert mgr.load() == 0

    def test_load_no_store_path(self) -> None:
        mgr = ContractTemplateManager()
        assert mgr.load() == 0

    def test_clear(self) -> None:
        mgr = ContractTemplateManager()
        mgr.register(_make_template(tool_name="a"))
        mgr.register(_make_template(tool_name="b"))
        removed = mgr.clear()
        assert removed == 2
        assert mgr.template_count == 0

    def test_template_count(self) -> None:
        mgr = ContractTemplateManager()
        assert mgr.template_count == 0
        mgr.register(_make_template(tool_name="a"))
        assert mgr.template_count == 1

    def test_store_path_property(self, tmp_path: Path) -> None:
        store = tmp_path / "contracts.json"
        mgr = ContractTemplateManager(store_path=store)
        assert mgr.store_path == store

    def test_store_path_property_none(self) -> None:
        mgr = ContractTemplateManager()
        assert mgr.store_path is None
