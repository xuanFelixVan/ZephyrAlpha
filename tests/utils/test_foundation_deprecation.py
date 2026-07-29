# [A_test] module_id: MOD-GOV_foundation_deprecation | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_foundation_deprecation

# [INVARIANTS] deprecated装饰器保留__name__;strict模式抛异常;silent模式零开销

# [MODIFY-GUARD] deprecation.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] DeprecatedAPIError

# [TESTS] pytest tests/test_foundation_deprecation.py -q
# [TTL] task_bound

import warnings

import pytest

from zephyr.shared.foundation.deprecation import (
    DeprecatedAPIError,
    DeprecationMode,
    deprecated,
    get_deprecation_mode,
    set_deprecation_mode,
)


@pytest.fixture(autouse=True)
def _reset_mode():
    original = get_deprecation_mode()
    yield
    set_deprecation_mode(original)


class TestDeprecationMode:
    def test_valid_modes(self):
        assert DeprecationMode.WARN == "warn"
        assert DeprecationMode.STRICT == "strict"
        assert DeprecationMode.SILENT == "silent"


class TestSetGetDeprecationMode:
    def test_set_and_get(self):
        set_deprecation_mode("strict")
        assert get_deprecation_mode() == "strict"

    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError, match="_DEPRECATION_MODE"):
            set_deprecation_mode("invalid")

    def test_set_silent(self):
        set_deprecation_mode("silent")
        assert get_deprecation_mode() == "silent"


class TestDeprecatedDecorator:
    def test_warn_mode_emits_warning(self):
        set_deprecation_mode("warn")

        @deprecated(since="0.1.0", remove_in="0.3.0", replacement="new_func")
        def old_func(x):
            return x * 2

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_func(5)
        assert result == 10
        assert len(w) >= 1
        assert "deprecated" in str(w[0].message).lower()
        assert "0.1.0" in str(w[0].message)
        assert "0.3.0" in str(w[0].message)
        assert "new_func" in str(w[0].message)

    def test_warn_mode_only_warns_once(self):
        set_deprecation_mode("warn")

        @deprecated(since="0.1.0")
        def once_func():
            return 1

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            once_func()
            once_func()
        warn_count = sum(1 for x in w if isinstance(x.message, DeprecatedAPIError))
        assert warn_count == 1

    def test_strict_mode_raises(self):
        set_deprecation_mode("strict")

        @deprecated(since="0.1.0")
        def strict_func():
            return 42

        with pytest.raises(DeprecatedAPIError):
            strict_func()

    def test_silent_mode_no_warning_no_error(self):
        set_deprecation_mode("silent")

        @deprecated(since="0.1.0")
        def silent_func(x):
            return x + 1

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = silent_func(10)
        assert result == 11
        assert len(w) == 0

    def test_preserves_function_name(self):
        @deprecated(since="0.1.0")
        def my_func():
            return "ok"

        assert my_func.__name__ == "my_func"

    def test_sets_deprecated_attributes(self):
        @deprecated(since="0.5.0", remove_in="0.7.0", replacement="better_func")
        def attr_func():
            return 1

        assert attr_func.zephyr_deprecated is True
        assert attr_func.zephyr_deprecated_since == "0.5.0"
        assert attr_func.zephyr_deprecated_remove_in == "0.7.0"
        assert attr_func.zephyr_deprecated_replacement == "better_func"

    def test_bare_decorator_no_args(self):
        set_deprecation_mode("silent")

        @deprecated
        def bare_func():
            return "bare"

        assert bare_func() == "bare"
        assert bare_func.zephyr_deprecated is True

    def test_with_reason(self):
        set_deprecation_mode("strict")

        @deprecated(since="0.1.0", reason="Use new_api instead")
        def reason_func():
            return 1

        with pytest.raises(DeprecatedAPIError) as exc_info:
            reason_func()
        assert "Use new_api instead" in str(exc_info.value)


class TestDeprecatedAPIError:
    def test_is_future_warning(self):
        assert issubclass(DeprecatedAPIError, FutureWarning)
