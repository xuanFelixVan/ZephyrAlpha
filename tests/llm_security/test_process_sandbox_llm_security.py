# [A_test] module_id: MOD-GOV_process_sandbox_llm_security | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] tests.llm_security.test_process_sandbox
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from pathlib import Path

import pytest

from zephyr.security.llm_defense.llm_security.process_sandbox import (
    CWD_WHITELIST_SUFFIXES,
    ENV_WHITELIST,
    L2aSandbox,
    SandboxResult,
    SandboxTimeout,
    SandboxViolation,
)
from zephyr.shared.io.paths import REPO_ROOT


class TestL2aSandboxInit:
    def test_default_init(self):
        sandbox = L2aSandbox()
        assert sandbox.repo_root is not None

    def test_custom_repo_root(self):
        sandbox = L2aSandbox(repo_root=REPO_ROOT)
        assert str(sandbox.repo_root) == str(REPO_ROOT)

    def test_repo_root_is_path(self):
        sandbox = L2aSandbox(repo_root=REPO_ROOT)
        assert isinstance(sandbox.repo_root, Path)


class TestCWDValidation:
    def test_src_zephyr_cwd_allowed(self):
        sandbox = L2aSandbox(repo_root=REPO_ROOT)
        sandbox.validate_cwd(sandbox.repo_root / "src" / "zephyr")

    def test_scripts_cwd_allowed(self):
        sandbox = L2aSandbox(repo_root=REPO_ROOT)
        sandbox.validate_cwd(sandbox.repo_root / "scripts")

    def test_docs_cwd_allowed(self):
        sandbox = L2aSandbox(repo_root=REPO_ROOT)
        sandbox.validate_cwd(sandbox.repo_root / "docs")

    def test_random_cwd_blocked(self):
        sandbox = L2aSandbox(repo_root=REPO_ROOT)
        with pytest.raises(SandboxViolation):
            sandbox.validate_cwd(sandbox.repo_root / "etc" / "shadow")

    def test_repo_root_allowed(self):
        sandbox = L2aSandbox(repo_root=REPO_ROOT)
        sandbox.validate_cwd(sandbox.repo_root)


class TestEnvBuilding:
    def test_whitelist_env_included(self):
        sandbox = L2aSandbox()
        env = sandbox.build_env(None, False)
        for key in ENV_WHITELIST:
            if key in __import__("os").environ:
                assert key in env

    def test_extra_env_non_whitelist_blocked(self):
        sandbox = L2aSandbox()
        with pytest.raises(SandboxViolation):
            sandbox.build_env({"EVIL_VAR": "value"}, False)

    def test_extra_env_whitelist_allowed(self):
        sandbox = L2aSandbox()
        env = sandbox.build_env({"PATH": "/usr/bin"}, False)
        assert env["PATH"] == "/usr/bin"

    def test_extra_env_with_allow_flag(self):
        sandbox = L2aSandbox()
        env = sandbox.build_env({"CUSTOM_VAR": "value"}, True)
        assert env["CUSTOM_VAR"] == "value"


class TestSandboxRun:
    def test_run_python_version(self):
        sandbox = L2aSandbox(repo_root=REPO_ROOT)
        result = sandbox.run(
            cmd=["python", "--version"],
            cwd="src/zephyr",
            timeout=10,
        )
        assert isinstance(result, SandboxResult)
        assert result.returncode == 0

    def test_run_with_timeout_raises(self):
        sandbox = L2aSandbox(repo_root=REPO_ROOT)
        with pytest.raises(SandboxTimeout):
            sandbox.run(
                cmd=["python", "-c", "import time; time.sleep(60)"],
                cwd="src/zephyr",
                timeout=1,
            )

    def test_run_invalid_cwd_raises(self):
        sandbox = L2aSandbox(repo_root=REPO_ROOT)
        with pytest.raises(SandboxViolation):
            sandbox.run(
                cmd=["python", "--version"],
                cwd="/etc/shadow",
                timeout=5,
            )


class TestConstants:
    def test_cwd_whitelist_not_empty(self):
        assert len(CWD_WHITELIST_SUFFIXES) > 0

    def test_env_whitelist_has_path(self):
        assert "PATH" in ENV_WHITELIST

    def test_env_whitelist_has_systemroot(self):
        assert "SYSTEMROOT" in ENV_WHITELIST
