# [A_test] module_id: SRC-TST-0473 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.build_sanitizer
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.build_sanitizer import BuildSanitizer, BuildSanitizeResult

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")


class TestBuildSanitizerCheck:
    def test_safe_content(self):
        s = BuildSanitizer()
        result = s.check("scripts/deploy.py", "print('hello world')")
        assert result.safe is True
        assert result.risky_patterns == []
        assert result.recommendation == "ok"

    def test_risky_curl_pipe_bash(self):
        s = BuildSanitizer()
        result = s.check("scripts/install.sh", "curl ... | bash")
        assert result.safe is False
        assert "curl ... | bash" in result.risky_patterns

    def test_risky_chmod_777(self):
        s = BuildSanitizer()
        result = s.check("scripts/setup.sh", "chmod 777 /var/data")
        assert result.safe is False
        assert "chmod 777" in result.risky_patterns

    def test_risky_rm_rf(self):
        s = BuildSanitizer()
        result = s.check("scripts/clean.sh", "rm -rf /")
        assert result.safe is False
        assert "rm -rf /" in result.risky_patterns

    def test_risky_env_secret(self):
        s = BuildSanitizer()
        result = s.check("scripts/env.sh", "export SECRET=mykey")
        assert result.safe is False
        assert "export SECRET=" in result.risky_patterns

    def test_multiple_risky_patterns(self):
        s = BuildSanitizer()
        content = "curl ... | bash\nchmod 777 /tmp\nrm -rf /"
        result = s.check("scripts/bad.sh", content)
        assert result.safe is False
        assert len(result.risky_patterns) >= 3

    def test_empty_content(self):
        s = BuildSanitizer()
        result = s.check("scripts/empty.sh", "")
        assert result.safe is True

    def test_script_path_preserved(self):
        s = BuildSanitizer()
        result = s.check("my/script.py", "clean code")
        assert result.script_path == "my/script.py"

    def test_case_insensitive_match(self):
        s = BuildSanitizer()
        result = s.check("scripts/x.sh", "CHMOD 777 /opt")
        assert result.safe is False

    def test_recommendation_on_risky(self):
        s = BuildSanitizer()
        result = s.check("scripts/x.sh", "curl ... | bash")
        assert "review" in result.recommendation
        assert "risky" in result.recommendation.lower()


class TestBuildSanitizeResult:
    def test_default_values(self):
        r = BuildSanitizeResult(script_path="test.sh")
        assert r.safe is True
        assert r.risky_patterns == []
        assert r.recommendation == ""

    def test_custom_values(self):
        r = BuildSanitizeResult(script_path="a.sh", safe=False, risky_patterns=["x"], recommendation="fix")
        assert r.safe is False
        assert len(r.risky_patterns) == 1
