# [A_test] module_id: SRC-TST-1793 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_vibe_security_verify
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_vibe_security_verify.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.security_governance.vibe_security_verify import (
    SECURITY_CHECKS,
    VibeSecurityVerify,
)


class TestSecurityChecksConstant:
    def test_contains_all_expected_checks(self):
        expected = [
            "no_eval",
            "no_exec",
            "no_os_system",
            "no_subprocess_shell",
            "no_pickle",
            "no_yaml_unsafe_load",
        ]
        assert expected == SECURITY_CHECKS

    def test_check_count(self):
        assert len(SECURITY_CHECKS) == 6


class TestVibeSecurityVerifyInstantiation:
    def test_instantiation(self):
        verifier = VibeSecurityVerify()
        assert verifier is not None

    def test_independent_instances(self):
        v1 = VibeSecurityVerify()
        v2 = VibeSecurityVerify()
        assert v1 is not v2


class TestScanCode:
    def test_clean_code(self):
        verifier = VibeSecurityVerify()
        code = "x = 1 + 2\nprint(x)"
        assert verifier.scan_code(code) == []

    def test_detect_eval(self):
        verifier = VibeSecurityVerify()
        code = 'result = eval("1+1")'
        violations = verifier.scan_code(code)
        assert "no_eval" in violations

    def test_detect_exec(self):
        verifier = VibeSecurityVerify()
        code = 'exec("print(1)")'
        violations = verifier.scan_code(code)
        assert "no_exec" in violations

    def test_detect_os_system(self):
        verifier = VibeSecurityVerify()
        code = 'os.system("ls")'
        violations = verifier.scan_code(code)
        assert "no_os_system" in violations

    def test_detect_subprocess_shell(self):
        verifier = VibeSecurityVerify()
        code = 'subprocess.run(["ls"], shell=True)'
        violations = verifier.scan_code(code)
        assert "no_subprocess_shell" in violations

    def test_detect_pickle(self):
        verifier = VibeSecurityVerify()
        code = "data = pickle.loads(raw)"
        violations = verifier.scan_code(code)
        assert "no_pickle" in violations

    def test_detect_yaml_unsafe_load(self):
        verifier = VibeSecurityVerify()
        code = "config = yaml.load(stream)"
        violations = verifier.scan_code(code)
        assert "no_yaml_unsafe_load" in violations

    def test_multiple_violations(self):
        verifier = VibeSecurityVerify()
        code = 'eval("1")\nos.system("ls")'
        violations = verifier.scan_code(code)
        assert "no_eval" in violations
        assert "no_os_system" in violations
        assert len(violations) == 2

    def test_all_violations_at_once(self):
        verifier = VibeSecurityVerify()
        code = 'eval("1")\nexec("2")\nos.system("3")\nsubprocess.run("4",shell=True)\npickle.load(f)\nyaml.load(s)'
        violations = verifier.scan_code(code)
        assert len(violations) == 6

    def test_empty_string(self):
        verifier = VibeSecurityVerify()
        assert verifier.scan_code("") == []

    def test_yaml_safe_load_not_flagged(self):
        verifier = VibeSecurityVerify()
        code = "config = yaml.safe_load(stream)"
        violations = verifier.scan_code(code)
        assert "no_yaml_unsafe_load" not in violations

    def test_eval_in_comment_still_detected(self):
        verifier = VibeSecurityVerify()
        code = "# uses eval( for something"
        violations = verifier.scan_code(code)
        assert "no_eval" in violations


class TestIsSafe:
    def test_safe_code(self):
        verifier = VibeSecurityVerify()
        assert verifier.is_safe("x = 1") is True

    def test_unsafe_code_eval(self):
        verifier = VibeSecurityVerify()
        assert verifier.is_safe('eval("1")') is False

    def test_unsafe_code_exec(self):
        verifier = VibeSecurityVerify()
        assert verifier.is_safe('exec("1")') is False

    def test_unsafe_code_os_system(self):
        verifier = VibeSecurityVerify()
        assert verifier.is_safe('os.system("ls")') is False

    def test_unsafe_code_subprocess_shell(self):
        verifier = VibeSecurityVerify()
        assert verifier.is_safe('subprocess.run("x",shell=True)') is False

    def test_unsafe_code_pickle(self):
        verifier = VibeSecurityVerify()
        assert verifier.is_safe("pickle.load(f)") is False

    def test_unsafe_code_yaml(self):
        verifier = VibeSecurityVerify()
        assert verifier.is_safe("yaml.load(s)") is False

    def test_empty_string_is_safe(self):
        verifier = VibeSecurityVerify()
        assert verifier.is_safe("") is True
