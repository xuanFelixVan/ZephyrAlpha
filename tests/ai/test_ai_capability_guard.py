# [A_test] module_id: SRC-TST-0297 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §

# [MODULE] tests.test_ai_capability_guard

# [INVARIANTS] CapabilityLevel enum has exactly 3 members; _level_meets_min is deterministic

# [MODIFY-GUARD] src/zephyr/governance/rule_enforcement/ai_capability_guard.py

# [CONSUMERS] CI pipeline

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] pytest.AssertionError on logic mismatch; PermissionError on enforcement violation

# [TESTS] tests/test_ai_capability_guard.py
# [TTL] task_bound

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from zephyr.gov_enforcement.rule_enforcement.ai_capability_guard import (
    CapabilityLevel,
    _check_file_level,
    _level_meets_min,
    require_capability,
)
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）


class TestCapabilityLevel:
    def test_enum_has_three_members(self):
        assert len(CapabilityLevel) == 3

    def test_immutable_value(self):
        assert CapabilityLevel.IMMUTABLE.value == "IMMUTABLE"

    def test_extend_value(self):
        assert CapabilityLevel.EXTEND.value == "EXTEND"

    def test_full_value(self):
        assert CapabilityLevel.FULL.value == "FULL"

    def test_is_str_enum(self):
        assert isinstance(CapabilityLevel.IMMUTABLE, str)

    def test_member_identity(self):
        assert CapabilityLevel("IMMUTABLE") is CapabilityLevel.IMMUTABLE
        assert CapabilityLevel("EXTEND") is CapabilityLevel.EXTEND
        assert CapabilityLevel("FULL") is CapabilityLevel.FULL


class TestLevelMeetsMin:
    def test_equal_levels_pass(self):
        assert _level_meets_min(CapabilityLevel.IMMUTABLE, CapabilityLevel.IMMUTABLE) is True
        assert _level_meets_min(CapabilityLevel.EXTEND, CapabilityLevel.EXTEND) is True
        assert _level_meets_min(CapabilityLevel.FULL, CapabilityLevel.FULL) is True

    def test_higher_actual_passes(self):
        assert _level_meets_min(CapabilityLevel.EXTEND, CapabilityLevel.IMMUTABLE) is True
        assert _level_meets_min(CapabilityLevel.FULL, CapabilityLevel.IMMUTABLE) is True
        assert _level_meets_min(CapabilityLevel.FULL, CapabilityLevel.EXTEND) is True

    def test_lower_actual_fails(self):
        assert _level_meets_min(CapabilityLevel.IMMUTABLE, CapabilityLevel.EXTEND) is False
        assert _level_meets_min(CapabilityLevel.IMMUTABLE, CapabilityLevel.FULL) is False
        assert _level_meets_min(CapabilityLevel.EXTEND, CapabilityLevel.FULL) is False

    def test_ordering_immutable_zero(self):
        assert _level_meets_min(CapabilityLevel.IMMUTABLE, CapabilityLevel.IMMUTABLE) is True

    def test_ordering_full_highest(self):
        assert _level_meets_min(CapabilityLevel.FULL, CapabilityLevel.IMMUTABLE) is True
        assert _level_meets_min(CapabilityLevel.FULL, CapabilityLevel.EXTEND) is True
        assert _level_meets_min(CapabilityLevel.FULL, CapabilityLevel.FULL) is True


class TestRequireCapability:
    def test_decorator_marks_operation(self):
        @require_capability("test_op")
        def sample_func():
            return 42

        assert sample_func._capability_operation == "test_op"

    def test_decorator_marks_min_level_default(self):
        @require_capability("default_level_op")
        def sample_func():
            return 1

        assert sample_func._capability_min_level is CapabilityLevel.EXTEND

    def test_decorator_marks_min_level_explicit(self):
        @require_capability("explicit_op", min_level=CapabilityLevel.FULL)
        def sample_func():
            return 2

        assert sample_func._capability_min_level is CapabilityLevel.FULL

    def test_decorator_preserves_function_result(self):
        @require_capability("add_op")
        def add(a, b):
            return a + b

        assert add(3, 7) == 10

    def test_decorator_preserves_kwargs(self):
        @require_capability("kw_op")
        def kw_func(x=0, y=0):
            return x * y

        assert kw_func(x=5, y=6) == 30

    def test_decorator_preserves_function_name(self):
        @require_capability("name_op")
        def my_named_function():
            return None

        assert my_named_function.__name__ == "my_named_function"

    def test_enforcement_blocks_insufficient_level(self):
        os.environ["ZEPHYR_ENFORCE_CAPABILITY"] = "true"
        try:

            @require_capability("restricted_op", min_level=CapabilityLevel.FULL)
            def guarded():
                return "secret"

            with (
                patch(
                    "zephyr.governance.rule_enforcement.ai_capability_guard._check_file_level",
                    return_value=CapabilityLevel.IMMUTABLE,
                ),
                pytest.raises(PermissionError),
            ):
                guarded()
        finally:
            os.environ.pop("ZEPHYR_ENFORCE_CAPABILITY", None)

    def test_enforcement_allows_sufficient_level(self):
        os.environ["ZEPHYR_ENFORCE_CAPABILITY"] = "true"
        try:

            @require_capability("open_op", min_level=CapabilityLevel.IMMUTABLE)
            def open_func():
                return "ok"

            with patch(
                "zephyr.governance.rule_enforcement.ai_capability_guard._check_file_level",
                return_value=CapabilityLevel.FULL,
            ):
                result = open_func()
                assert result == "ok"
        finally:
            os.environ.pop("ZEPHYR_ENFORCE_CAPABILITY", None)

    def test_enforcement_off_by_default(self):
        os.environ.pop("ZEPHYR_ENFORCE_CAPABILITY", None)

        @require_capability("any_op", min_level=CapabilityLevel.FULL)
        def unguarded():
            return "allowed"

        assert unguarded() == "allowed"


class TestCheckFileLevel:
    def test_shared_contracts_immutable(self):
        result = _check_file_level(str(REPO_ROOT / "src" / "zephyr" / "shared" / "contracts" / "base.py"))
        assert result is CapabilityLevel.IMMUTABLE

    def test_shared_contracts_subdir_immutable(self):
        result = _check_file_level(str(REPO_ROOT / "src" / "zephyr" / "shared" / "contracts" / "core" / "runtime_plane_tag.py"))
        assert result is CapabilityLevel.IMMUTABLE

    def test_governance_ai_immutable(self):
        result = _check_file_level(str(REPO_ROOT / "scripts" / "governance" / "ai" / "policy.py"))
        assert result is CapabilityLevel.IMMUTABLE

    def test_registry_yaml_immutable(self):
        result = _check_file_level(str(REPO_ROOT / "src" / "zephyr" / "gates" / "_registry.yaml"))
        assert result is CapabilityLevel.IMMUTABLE

    def test_scripts_governance_extend(self):
        result = _check_file_level(str(REPO_ROOT / "scripts" / "governance" / "d5_architecture" / "checker.py"))
        assert result is CapabilityLevel.EXTEND

    def test_tests_architecture_extend(self):
        result = _check_file_level(str(REPO_ROOT / "tests" / "architecture" / "test_structure.py"))
        assert result is CapabilityLevel.EXTEND

    def test_factor_registry_extend(self):
        result = _check_file_level(str(REPO_ROOT / "src" / "zephyr" / "factor_registry" / "manager.py"))
        assert result is CapabilityLevel.EXTEND

    def test_default_full(self):
        result = _check_file_level(str(REPO_ROOT / "src" / "zephyr" / "runtime" / "executor.py"))
        assert result is CapabilityLevel.FULL

    def test_empty_path_returns_full(self):
        result = _check_file_level("")
        assert result is CapabilityLevel.FULL

    def test_path_case_insensitive(self):
        result = _check_file_level("D:/ZEPHYRALPHA/SHARED/CONTRACTS/core.py")
        assert result is CapabilityLevel.IMMUTABLE


class TestBoundaryConditions:
    def test_level_meets_min_with_none_raises(self):
        with pytest.raises((TypeError, KeyError, AttributeError)):
            _level_meets_min(None, CapabilityLevel.EXTEND)

    def test_level_meets_min_both_none_raises(self):
        with pytest.raises((TypeError, KeyError, AttributeError)):
            _level_meets_min(None, None)

    def test_require_capability_empty_operation_string(self):
        @require_capability("")
        def empty_op():
            return True

        assert empty_op._capability_operation == ""
        assert empty_op() is True

    def test_check_file_level_with_none_raises(self):
        with pytest.raises((TypeError, AttributeError)):
            _check_file_level(None)

    def test_check_file_level_backslash_path(self):
        result = _check_file_level("d:\\ZephyrAlpha\\src\\zephyr\\shared\\contracts\\base.py")
        assert result is CapabilityLevel.IMMUTABLE
