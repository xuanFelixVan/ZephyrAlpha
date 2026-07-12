# [A_test] module_id: SRC-TST-0890 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-384 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_failure_matcher
# [INVARIANTS] FailureMatcher.match返回FailureMatch; probability∈[0,1]; unknown category for no match
# [MODIFY-GUARD] 仅当failure_matcher公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_failure_matcher.py -q
# [TTL] task_bound

from zephyr.orchestrator.resilience.failure_matcher import (
    FailureCategory,
    FailureMatch,
    FailureMatcher,
)


class TestFailureMatcherInstantiation:
    def test_default_instantiation(self):
        fm = FailureMatcher()
        assert fm is not None


class TestFailureMatcherMatch:
    def test_match_returns_failure_match(self):
        fm = FailureMatcher()
        result = fm.match("connection refused")
        assert isinstance(result, FailureMatch)

    def test_match_network_error(self):
        fm = FailureMatcher()
        result = fm.match("connection refused")
        assert result.category == FailureCategory.NETWORK

    def test_match_network_reset(self):
        fm = FailureMatcher()
        result = fm.match("connection reset by peer")
        assert result.category == FailureCategory.NETWORK

    def test_match_timeout_error(self):
        fm = FailureMatcher()
        result = fm.match("timed out after 30s")
        assert result.category == FailureCategory.TIMEOUT

    def test_match_deadline_exceeded(self):
        fm = FailureMatcher()
        result = fm.match("deadline exceeded")
        assert result.category == FailureCategory.TIMEOUT

    def test_match_validation_error(self):
        fm = FailureMatcher()
        result = fm.match("validation failed for input")
        assert result.category == FailureCategory.VALIDATION

    def test_match_invalid_field(self):
        fm = FailureMatcher()
        result = fm.match("invalid parameter")
        assert result.category == FailureCategory.VALIDATION

    def test_match_permission_denied(self):
        fm = FailureMatcher()
        result = fm.match("permission denied")
        assert result.category == FailureCategory.PERMISSION

    def test_match_access_denied(self):
        fm = FailureMatcher()
        result = fm.match("access denied")
        assert result.category == FailureCategory.PERMISSION

    def test_match_unauthorized(self):
        fm = FailureMatcher()
        result = fm.match("unauthorized access")
        assert result.category == FailureCategory.PERMISSION

    def test_match_disk_space(self):
        fm = FailureMatcher()
        result = fm.match("no space left on device")
        assert result.category == FailureCategory.DISK_SPACE

    def test_match_disk_full(self):
        fm = FailureMatcher()
        result = fm.match("disk full")
        assert result.category == FailureCategory.DISK_SPACE

    def test_match_dependency_error(self):
        fm = FailureMatcher()
        result = fm.match("module not found: xyz")
        assert result.category == FailureCategory.DEPENDENCY

    def test_match_import_error(self):
        fm = FailureMatcher()
        result = fm.match("import not found")
        assert result.category == FailureCategory.DEPENDENCY

    def test_match_syntax_error(self):
        fm = FailureMatcher()
        result = fm.match("SyntaxError: invalid syntax")
        assert result.category == FailureCategory.SYNTAX

    def test_match_indentation_error(self):
        fm = FailureMatcher()
        result = fm.match("IndentationError: unexpected indent")
        assert result.category == FailureCategory.SYNTAX

    def test_match_logic_error(self):
        fm = FailureMatcher()
        result = fm.match("AssertionError: assert True failed")
        assert result.category == FailureCategory.LOGIC

    def test_match_unknown_error(self):
        fm = FailureMatcher()
        result = fm.match("something completely unexpected happened")
        assert result.category == FailureCategory.UNKNOWN

    def test_match_empty_string(self):
        fm = FailureMatcher()
        result = fm.match("")
        assert result.category == FailureCategory.UNKNOWN

    def test_match_probability_range(self):
        fm = FailureMatcher()
        result = fm.match("connection refused")
        assert 0.0 <= result.probability <= 1.0

    def test_match_unknown_probability(self):
        fm = FailureMatcher()
        result = fm.match("random text with no pattern")
        assert result.probability == 0.3

    def test_match_has_suggestion(self):
        fm = FailureMatcher()
        result = fm.match("connection refused")
        assert len(result.suggestion) > 0

    def test_match_unknown_has_suggestion(self):
        fm = FailureMatcher()
        result = fm.match("random text")
        assert len(result.suggestion) > 0

    def test_match_has_pattern(self):
        fm = FailureMatcher()
        result = fm.match("connection refused")
        assert len(result.pattern) > 0

    def test_match_case_insensitive(self):
        fm = FailureMatcher()
        result = fm.match("CONNECTION REFUSED")
        assert result.category == FailureCategory.NETWORK

    def test_match_mixed_case(self):
        fm = FailureMatcher()
        result = fm.match("Permission Denied")
        assert result.category == FailureCategory.PERMISSION


class TestFailureMatcherCategorize:
    def test_categorize_returns_failure_match(self):
        fm = FailureMatcher()
        result = fm.categorize(ConnectionError("connection refused"))
        assert isinstance(result, FailureMatch)

    def test_categorize_network_exception(self):
        fm = FailureMatcher()
        result = fm.categorize(ConnectionError("connection refused"))
        assert result.category == FailureCategory.NETWORK

    def test_categorize_timeout_exception(self):
        fm = FailureMatcher()
        result = fm.categorize(TimeoutError("timed out"))
        assert result.category == FailureCategory.TIMEOUT

    def test_categorize_permission_exception(self):
        fm = FailureMatcher()
        result = fm.categorize(PermissionError("permission denied"))
        assert result.category == FailureCategory.PERMISSION

    def test_categorize_generic_exception(self):
        fm = FailureMatcher()
        result = fm.categorize(RuntimeError("something went wrong"))
        assert result.category == FailureCategory.UNKNOWN

    def test_categorize_includes_exception_type_in_message(self):
        fm = FailureMatcher()
        result = fm.categorize(ValueError("invalid value"))
        assert "ValueError" in result.pattern or result.category == FailureCategory.VALIDATION


class TestFailureMatcherAggregateFailures:
    def test_aggregate_returns_dict(self):
        fm = FailureMatcher()
        result = fm.aggregate_failures([])
        assert isinstance(result, dict)

    def test_aggregate_all_categories_present(self):
        fm = FailureMatcher()
        result = fm.aggregate_failures([])
        for cat in FailureCategory:
            assert cat in result

    def test_aggregate_counts_errors(self):
        fm = FailureMatcher()
        records = [
            {"error": "connection refused"},
            {"error": "connection reset"},
            {"error": "timed out"},
        ]
        result = fm.aggregate_failures(records)
        assert result[FailureCategory.NETWORK] == 2
        assert result[FailureCategory.TIMEOUT] == 1

    def test_aggregate_skips_empty_errors(self):
        fm = FailureMatcher()
        records = [
            {"error": "connection refused"},
            {"error": ""},
            {"error": "timed out"},
        ]
        result = fm.aggregate_failures(records)
        assert result[FailureCategory.NETWORK] == 1
        assert result[FailureCategory.TIMEOUT] == 1

    def test_aggregate_skips_missing_error_key(self):
        fm = FailureMatcher()
        records = [
            {"error": "connection refused"},
            {"message": "not an error field"},
        ]
        result = fm.aggregate_failures(records)
        assert result[FailureCategory.NETWORK] == 1

    def test_aggregate_empty_list(self):
        fm = FailureMatcher()
        result = fm.aggregate_failures([])
        total = sum(result.values())
        assert total == 0


class TestFailureCategory:
    def test_all_categories_exist(self):
        expected = [
            "network",
            "timeout",
            "validation",
            "permission",
            "disk_space",
            "dependency",
            "syntax",
            "logic",
            "unknown",
        ]
        for name in expected:
            assert hasattr(FailureCategory, name.upper()) or any(c.value == name for c in FailureCategory)

    def test_category_values(self):
        assert FailureCategory.NETWORK.value == "network"
        assert FailureCategory.UNKNOWN.value == "unknown"


class TestFailureMatch:
    def test_construction(self):
        fm = FailureMatch(
            category=FailureCategory.NETWORK,
            probability=0.85,
            pattern=r"connection\s+refused",
            suggestion="Check network",
        )
        assert fm.category == FailureCategory.NETWORK
        assert fm.probability == 0.85
        assert fm.pattern == r"connection\s+refused"
        assert fm.suggestion == "Check network"
