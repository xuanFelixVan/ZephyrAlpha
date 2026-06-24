# [A_test] module_id: SRC-TST-0514 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3-§7
# [MODULE] tests.test_check_type_registry
# [INVARIANTS] Handler import+instantiation+run return type; name attribute match
# [MODIFY-GUARD] source handler changes require test updates
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError on invariant violation
# [TESTS] pytest tests/test_check_type_registry.py
from __future__ import annotations

import pytest

from zephyr.governance.rule_enforcement.check_types.check_type_registry import (
    CheckTypeHandler,
    get_check_type,
    list_check_types,
    register_check_type,
)


class TestCheckTypeHandlerABC:
    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            CheckTypeHandler()

    def test_abstract_run_method(self):
        assert hasattr(CheckTypeHandler, "run")

    def test_name_attribute_exists(self):
        assert hasattr(CheckTypeHandler, "name")


class TestRegisterCheckType:
    def test_decorator_registers_handler(self):
        @register_check_type
        class _TestRegHandler(CheckTypeHandler):
            name = "test_reg_handler_gen"

            def run(self, task, params, check, project_root):
                return []

        retrieved = get_check_type("test_reg_handler_gen")
        assert retrieved is _TestRegHandler

    def test_decorator_returns_class(self):
        @register_check_type
        class _TestRetHandler(CheckTypeHandler):
            name = "test_ret_handler_gen"

            def run(self, task, params, check, project_root):
                return []

        assert isinstance(_TestRetHandler, type)


class TestGetCheckType:
    def test_known_type_returns_handler(self):
        handler = get_check_type("field_presence")
        assert handler is not None
        assert issubclass(handler, CheckTypeHandler)

    def test_unknown_type_returns_none(self):
        assert get_check_type("nonexistent_xyz_abc") is None


class TestListCheckTypes:
    def test_returns_sorted_list(self):
        types = list_check_types()
        assert isinstance(types, list)
        assert types == sorted(types)

    def test_contains_known_types(self):
        types = list_check_types()
        assert "field_presence" in types
        assert "classification" in types
        assert "encoding" in types

    def test_non_empty(self):
        types = list_check_types()
        assert len(types) >= 20


class TestAutoImport:
    def test_auto_import_populates_registry(self):
        from zephyr.governance.rule_enforcement.check_types.check_type_registry import _auto_import

        _auto_import()
        types = list_check_types()
        assert len(types) >= 20

    def test_all_handlers_are_subclasses(self):
        types = list_check_types()
        for name in types:
            cls = get_check_type(name)
            assert issubclass(cls, CheckTypeHandler), f"{name} is not a CheckTypeHandler subclass"
