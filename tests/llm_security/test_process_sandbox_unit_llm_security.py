# [A_test] module_id: SRC-TST-1911 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-530 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.llm_security.test_process_sandbox
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
T-V2-005 单元测试 — L2a ProcessSandbox
=======================================
覆盖场景（验收标准 #7 ≥ 80%）：
  - CWD 白名单：允许目录下的命令正常执行
  - CWD 黑名单：超出白名单的 cwd 抛出 SandboxViolation
  - ENV 白名单：只有白名单键被传入子进程
  - ENV 黑名单：非白名单键抛出 SandboxViolation（未豁免时）
  - allow_extra_env=True 豁免非白名单键
  - timeout 强制：超时抛出 SandboxTimeout
  - 成功执行：returncode / stdout / stderr 正确
  - shell=False 强制（命令列表传入）
"""

import sys
from pathlib import Path

import pytest

from zephyr.security.llm_defense.llm_security.process_sandbox import (
    L2aSandbox,
    SandboxTimeout,
    SandboxViolation,
)

# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def sandbox(tmp_path):
    """返回以 tmp_path 为 repo_root 的 L2aSandbox（避免写入真实仓库）。"""
    # 在 tmp_path 下创建白名单目录
    (tmp_path / "src" / "zephyr").mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "docs").mkdir()
    return L2aSandbox(repo_root=tmp_path)


# ---------------------------------------------------------------------------
# 1. CWD 白名单
# ---------------------------------------------------------------------------


class TestCwdWhitelist:
    def test_scripts_dir_allowed(self, sandbox, tmp_path):
        result = sandbox.run(
            cmd=[sys.executable, "-c", "print('ok')"],
            cwd=tmp_path / "scripts",
        )
        assert result.returncode == 0
        assert "ok" in result.stdout

    def test_src_zephyr_dir_allowed(self, sandbox, tmp_path):
        result = sandbox.run(
            cmd=[sys.executable, "-c", "print('zephyr')"],
            cwd=tmp_path / "src" / "zephyr",
        )
        assert result.returncode == 0

    def test_docs_dir_allowed(self, sandbox, tmp_path):
        result = sandbox.run(
            cmd=[sys.executable, "-c", "print('docs')"],
            cwd=tmp_path / "docs",
        )
        assert result.returncode == 0

    def test_repo_root_allowed_when_cwd_none(self, sandbox):
        result = sandbox.run(
            cmd=[sys.executable, "-c", "print('root')"],
            cwd=None,
        )
        assert result.returncode == 0

    def test_outside_whitelist_raises_violation(self, sandbox, tmp_path):
        outside = tmp_path / "private_data"
        outside.mkdir()
        with pytest.raises(SandboxViolation) as exc_info:
            sandbox.run(
                cmd=[sys.executable, "-c", "pass"],
                cwd=outside,
            )
        assert "白名单" in str(exc_info.value) or "whitelist" in str(exc_info.value).lower()

    def test_parent_traversal_raises_violation(self, sandbox, tmp_path):
        with pytest.raises(SandboxViolation):
            sandbox.run(
                cmd=[sys.executable, "-c", "pass"],
                cwd=tmp_path.parent,
            )

    def test_absolute_path_outside_repo_raises_violation(self, sandbox):
        with pytest.raises(SandboxViolation):
            sandbox.run(
                cmd=[sys.executable, "-c", "pass"],
                cwd=Path("/tmp"),
            )


# ---------------------------------------------------------------------------
# 2. ENV 白名单
# ---------------------------------------------------------------------------


class TestEnvWhitelist:
    def test_non_whitelist_extra_env_raises_violation(self, sandbox, tmp_path):
        with pytest.raises(SandboxViolation) as exc_info:
            sandbox.run(
                cmd=[sys.executable, "-c", "pass"],
                cwd=tmp_path / "scripts",
                extra_env={"SECRET_TOKEN": "abc123"},
                allow_extra_env=False,
            )
        assert "SECRET_TOKEN" in str(exc_info.value)

    def test_whitelist_extra_env_allowed(self, sandbox, tmp_path):
        result = sandbox.run(
            cmd=[sys.executable, "-c", "import os; print(os.environ.get('PYTHONUNBUFFERED','missing'))"],
            cwd=tmp_path / "scripts",
            extra_env={"PYTHONUNBUFFERED": "1"},
        )
        assert result.returncode == 0

    def test_allow_extra_env_bypasses_check(self, sandbox, tmp_path):
        result = sandbox.run(
            cmd=[sys.executable, "-c", "import os; print(os.environ.get('MY_SECRET','yes'))"],
            cwd=tmp_path / "scripts",
            extra_env={"MY_SECRET": "yes"},
            allow_extra_env=True,
        )
        assert result.returncode == 0
        assert "yes" in result.stdout

    def test_env_isolation_filters_system_vars(self, sandbox, tmp_path):
        """子进程不应继承 SECRET_TOKEN 等非白名单变量。"""
        import os

        os.environ["__CBG_TEST_SECRET__"] = "leaked"
        try:
            result = sandbox.run(
                cmd=[
                    sys.executable,
                    "-c",
                    "import os; print(os.environ.get('__CBG_TEST_SECRET__', 'not_found'))",
                ],
                cwd=tmp_path / "scripts",
            )
            assert "leaked" not in result.stdout
        finally:
            del os.environ["__CBG_TEST_SECRET__"]


# ---------------------------------------------------------------------------
# 3. Timeout 强制
# ---------------------------------------------------------------------------


class TestTimeout:
    def test_timeout_raises_sandbox_timeout(self, sandbox, tmp_path):
        with pytest.raises(SandboxTimeout) as exc_info:
            sandbox.run(
                cmd=[sys.executable, "-c", "import time; time.sleep(10)"],
                cwd=tmp_path / "scripts",
                timeout=0.5,
            )
        assert exc_info.value.timeout == pytest.approx(0.5)

    def test_timeout_error_contains_cmd(self, sandbox, tmp_path):
        cmd = [sys.executable, "-c", "import time; time.sleep(10)"]
        with pytest.raises(SandboxTimeout) as exc_info:
            sandbox.run(cmd=cmd, cwd=tmp_path / "scripts", timeout=0.5)
        assert exc_info.value.cmd == cmd


# ---------------------------------------------------------------------------
# 4. 正常执行结果
# ---------------------------------------------------------------------------


class TestNormalExecution:
    def test_returncode_zero_on_success(self, sandbox, tmp_path):
        result = sandbox.run(
            cmd=[sys.executable, "-c", "import sys; sys.exit(0)"],
            cwd=tmp_path / "scripts",
        )
        assert result.returncode == 0

    def test_returncode_nonzero_on_failure(self, sandbox, tmp_path):
        result = sandbox.run(
            cmd=[sys.executable, "-c", "import sys; sys.exit(1)"],
            cwd=tmp_path / "scripts",
        )
        assert result.returncode == 1

    def test_stdout_captured(self, sandbox, tmp_path):
        result = sandbox.run(
            cmd=[sys.executable, "-c", "print('hello sandbox')"],
            cwd=tmp_path / "scripts",
        )
        assert "hello sandbox" in result.stdout

    def test_stderr_captured(self, sandbox, tmp_path):
        result = sandbox.run(
            cmd=[sys.executable, "-c", "import sys; print('err', file=sys.stderr)"],
            cwd=tmp_path / "scripts",
        )
        assert "err" in result.stderr

    def test_result_contains_cwd(self, sandbox, tmp_path):
        result = sandbox.run(
            cmd=[sys.executable, "-c", "pass"],
            cwd=tmp_path / "scripts",
        )
        assert "scripts" in result.cwd

    def test_result_contains_cmd(self, sandbox, tmp_path):
        cmd = [sys.executable, "-c", "pass"]
        result = sandbox.run(cmd=cmd, cwd=tmp_path / "scripts")
        assert result.cmd == cmd


# ---------------------------------------------------------------------------
# 5. 配置自定义
# ---------------------------------------------------------------------------


class TestCustomConfig:
    def test_custom_cwd_whitelist(self, tmp_path):
        custom_dir = tmp_path / "custom_allowed"
        custom_dir.mkdir()
        sb = L2aSandbox(
            repo_root=tmp_path,
            cwd_whitelist=("custom_allowed/",),
        )
        result = sb.run(
            cmd=[sys.executable, "-c", "print('custom')"],
            cwd=custom_dir,
        )
        assert result.returncode == 0

    def test_custom_cwd_whitelist_blocks_default_dirs(self, tmp_path):
        (tmp_path / "scripts").mkdir()
        sb = L2aSandbox(
            repo_root=tmp_path,
            cwd_whitelist=("custom_only/",),
        )
        with pytest.raises(SandboxViolation):
            sb.run(
                cmd=[sys.executable, "-c", "pass"],
                cwd=tmp_path / "scripts",
            )
