# [A_test] module_id: MOD-GOV_version | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_version

# [INVARIANTS] __version__格式PEP440;version_compatible同MAJOR兼容;VersionMismatchError继承Exception

# [MODIFY-GUARD] __version__.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] VersionMismatchError

# [TESTS] pytest tests/test_version.py -q
# [TTL] task_bound

import pytest

from zephyr.shared.__version__ import (
    MIN_COMPATIBLE_SHARED_VERSION,
    VersionMismatchError,
    __version__,
    __version_info__,
    _parse_semver,
    check_shared_version,
    version_compatible,
    version_eq,
    version_gt,
    version_gte,
    version_lt,
    version_lte,
)


class TestVersion:
    def test_is_string(self):
        assert isinstance(__version__, str)

    def test_format(self):
        parts = __version__.split(".")
        assert len(parts) >= 3

    def test_version_info(self):
        assert isinstance(__version_info__, tuple)
        assert len(__version_info__) >= 3


class TestMinCompatibleVersion:
    def test_is_string(self):
        assert isinstance(MIN_COMPATIBLE_SHARED_VERSION, str)


class TestParseSemver:
    def test_valid_semver(self):
        result = _parse_semver("1.2.3")
        assert result == (1, 2, 3)

    def test_zero_version(self):
        result = _parse_semver("0.0.0")
        assert result == (0, 0, 0)

    def test_comparison(self):
        assert _parse_semver("1.2.3") < _parse_semver("1.2.4")
        assert _parse_semver("1.2.0") < _parse_semver("1.3.0")
        assert _parse_semver("0.9.9") < _parse_semver("1.0.0")

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="invalid semver"):
            _parse_semver("abc")


class TestVersionComparison:
    def test_eq(self):
        assert version_eq("1.2.3", "1.2.3") is True
        assert version_eq("1.2.3", "1.2.4") is False

    def test_lt(self):
        assert version_lt("1.2.3", "1.2.4") is True
        assert version_lt("1.2.4", "1.2.3") is False

    def test_lte(self):
        assert version_lte("1.2.3", "1.2.3") is True
        assert version_lte("1.2.3", "1.2.4") is True

    def test_gt(self):
        assert version_gt("1.2.4", "1.2.3") is True
        assert version_gt("1.2.3", "1.2.4") is False

    def test_gte(self):
        assert version_gte("1.2.3", "1.2.3") is True
        assert version_gte("1.2.4", "1.2.3") is True


class TestVersionCompatible:
    def test_same_major_compatible(self):
        assert version_compatible("0.7.0", "0.6.0") is True

    def test_different_major_incompatible(self):
        assert version_compatible("1.0.0", "0.7.0") is False

    def test_same_version(self):
        assert version_compatible("0.7.0", "0.7.0") is True

    def test_newer_minor_compatible(self):
        assert version_compatible("0.8.0", "0.7.0") is True


class TestCheckSharedVersion:
    def test_current_version_passes(self):
        assert check_shared_version(__version__) is True

    def test_incompatible_returns_false(self):
        result = check_shared_version("99.0.0")
        assert result is False

    def test_incompatible_strict_raises(self):
        with pytest.raises(VersionMismatchError):
            check_shared_version("99.0.0", strict=True)


class TestVersionMismatchError:
    def test_inherits_exception(self):
        err = VersionMismatchError("mismatch")
        assert isinstance(err, Exception)
