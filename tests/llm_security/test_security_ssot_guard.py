# [A_test] module_id: MOD-GOV_security_ssot_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_security_ssot_guard

# [INVARIANTS] _extract_declared_paths去重保序;_validate_path_format拒绝绝对路径和反斜杠;CheckResult不可变语义

# [MODIFY-GUARD] ssot_guard.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] SsotViolation;RegistryParseError

# [TESTS] pytest tests/test_security_ssot_guard.py -q
# [TTL] task_bound

from zephyr.shared.security.ssot_guard import (
    REGISTRY_REL_PATH,
    WATCHED_EXTENSIONS,
    WATCHED_PREFIXES,
    CheckResult,
    GuardReport,
    RegistryParseError,
    SsotError,
    SsotViolation,
    _extract_declared_paths,
    _validate_path_format,
)


class TestExtractDeclaredPaths:
    def test_extracts_path_fields(self):
        content = "entries:\n  path: src/zephyr/main.py\n  core_file: scripts/run.py\n"
        paths = _extract_declared_paths(content)
        assert "src/zephyr/main.py" in paths
        assert "scripts/run.py" in paths

    def test_deduplicates(self):
        content = "  path: a.py\n  path: a.py\n"
        paths = _extract_declared_paths(content)
        assert paths.count("a.py") == 1

    def test_preserves_order(self):
        content = "  path: first.py\n  path: second.py\n  path: third.py\n"
        paths = _extract_declared_paths(content)
        assert paths == ["first.py", "second.py", "third.py"]

    def test_ignores_comments(self):
        content = "  path: #comment\n  path: real.py\n"
        paths = _extract_declared_paths(content)
        assert "real.py" in paths

    def test_strips_trailing_slash(self):
        content = "  path: src/zephyr/\n"
        paths = _extract_declared_paths(content)
        assert paths == ["src/zephyr"]

    def test_empty_content(self):
        assert _extract_declared_paths("") == []

    def test_canonical_path_field(self):
        content = "  canonical_path: docs/index.md\n"
        paths = _extract_declared_paths(content)
        assert "docs/index.md" in paths

    def test_entry_field(self):
        content = "  entry: scripts/run.py\n"
        paths = _extract_declared_paths(content)
        assert "scripts/run.py" in paths


class TestValidatePathFormat:
    def test_valid_relative_path(self):
        assert _validate_path_format("src/zephyr/main.py") is None

    def test_absolute_unix_path(self):
        result = _validate_path_format("/usr/local/bin/app")
        assert result is not None
        assert "绝对路径" in result

    def test_absolute_windows_path(self):
        result = _validate_path_format("C:\\Users\\test")
        assert result is not None
        assert "绝对路径" in result

    def test_backslash_separator(self):
        result = _validate_path_format("src\\zephyr\\main.py")
        assert result is not None
        assert "反斜杠" in result

    def test_simple_filename(self):
        assert _validate_path_format("file.py") is None


class TestCheckResult:
    def test_passed_str(self):
        r = CheckResult(check_id="C-1", passed=True, message="ok")
        assert "✅" in str(r)
        assert "C-1" in str(r)

    def test_failed_str(self):
        r = CheckResult(check_id="C-2", passed=False, message="fail", details=["detail1"])
        assert "❌" in str(r)
        assert "detail1" in str(r)


class TestGuardReport:
    def test_all_passed(self):
        report = GuardReport()
        report.add(CheckResult(check_id="C-1", passed=True, message="ok"))
        report.add(CheckResult(check_id="C-2", passed=True, message="ok"))
        assert report.passed is True

    def test_any_failed(self):
        report = GuardReport()
        report.add(CheckResult(check_id="C-1", passed=True, message="ok"))
        report.add(CheckResult(check_id="C-2", passed=False, message="fail"))
        assert report.passed is False

    def test_empty_report_passes(self):
        report = GuardReport()
        assert report.passed is True

    def test_str_output(self):
        report = GuardReport()
        report.add(CheckResult(check_id="C-1", passed=True, message="ok"))
        text = str(report)
        assert "SSoT" in text
        assert "通过" in text


class TestSsotViolation:
    def test_attributes(self):
        err = SsotViolation(check_id="C-1", message="test violation")
        assert err.check_id == "C-1"
        assert "test violation" in err.message
        assert "[C-1]" in str(err)

    def test_inherits_ssot_error(self):
        assert issubclass(SsotViolation, SsotError)

    def test_inherits_zephyr_base_error(self):
        from zephyr.shared.foundation.errors import ZephyrBaseError

        assert issubclass(SsotViolation, ZephyrBaseError)


class TestRegistryParseError:
    def test_inherits_ssot_error(self):
        assert issubclass(RegistryParseError, SsotError)


class TestConstants:
    def test_watched_prefixes_not_empty(self):
        assert len(WATCHED_PREFIXES) > 0

    def test_watched_extensions(self):
        assert ".py" in WATCHED_EXTENSIONS
        assert ".yaml" in WATCHED_EXTENSIONS
        assert ".md" in WATCHED_EXTENSIONS

    def test_registry_rel_path(self):
        assert "rule_catalog_registry.yaml" in REGISTRY_REL_PATH
