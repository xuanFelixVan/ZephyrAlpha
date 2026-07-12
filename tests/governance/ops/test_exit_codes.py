# [A_test] module_id: SRC-TST-0881 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_exit_codes
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_exit_codes.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_code_quality.code_dedup.exit_codes import (
    EXIT_CODE_DESCRIPTIONS,
    ExitCode,
    determine_exit_code,
)


class TestExitCode:
    def test_values(self):
        assert ExitCode.PASS == 0
        assert ExitCode.WARN == 1
        assert ExitCode.ERROR == 2
        assert ExitCode.TOOL_ERROR == 3
        assert ExitCode.DEGRADED == 4

    def test_is_int_enum(self):
        assert isinstance(ExitCode.PASS, int)
        assert isinstance(ExitCode.WARN, int)

    def test_all_codes_unique(self):
        values = [e.value for e in ExitCode]
        assert len(values) == len(set(values))


class TestExitCodeDescriptions:
    def test_all_codes_have_descriptions(self):
        for code in ExitCode:
            assert code in EXIT_CODE_DESCRIPTIONS

    def test_descriptions_non_empty(self):
        for code, desc in EXIT_CODE_DESCRIPTIONS.items():
            assert len(desc) > 0


class TestDetermineExitCode:
    def test_tool_error_overrides_all(self):
        assert determine_exit_code("low", tool_error=True) == ExitCode.TOOL_ERROR
        assert determine_exit_code("critical", tool_error=True) == ExitCode.TOOL_ERROR

    def test_degraded_overrides_severity(self):
        assert determine_exit_code("low", degraded=True) == ExitCode.DEGRADED
        assert determine_exit_code("high", degraded=True) == ExitCode.DEGRADED

    def test_tool_error_takes_precedence_over_degraded(self):
        assert determine_exit_code("low", tool_error=True, degraded=True) == ExitCode.TOOL_ERROR

    def test_high_severity(self):
        assert determine_exit_code("high") == ExitCode.ERROR

    def test_critical_severity(self):
        assert determine_exit_code("critical") == ExitCode.ERROR

    def test_medium_severity(self):
        assert determine_exit_code("medium") == ExitCode.WARN

    def test_low_severity(self):
        assert determine_exit_code("low") == ExitCode.WARN

    def test_no_severity(self):
        assert determine_exit_code("none") == ExitCode.PASS

    def test_empty_severity(self):
        assert determine_exit_code("") == ExitCode.PASS

    def test_unknown_severity(self):
        assert determine_exit_code("unknown") == ExitCode.PASS
