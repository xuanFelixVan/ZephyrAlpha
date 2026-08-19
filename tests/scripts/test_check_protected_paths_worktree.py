# [A_test] module_id: MOD-INF-005 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/check_protected_paths.py | §L3.2-worktree-isolation
# [MODULE] tests.scripts.test_check_protected_paths_worktree
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-INF-005 | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_check_protected_paths_worktree.py — L3.2 worktree 隔离 warn 单测

#ARCH-GIT-SELF-HARM-GUARD L3.2（2026-08-04，方向性）。

测试 check_protected_paths.py 的 _warn_worktree_isolation 函数:
1. 主工作区 staging src/zephyr/**/*.py + 无 session → warn 输出
2. worktree 内 → 不 warn（豁免）
3. ZEPHYR_SESSION_ID 设置 → 不 warn（豁免）
4. ZEPHYR_RECONCILER_AUTO_COMMIT=1 → 不 warn（豁免）
5. 非 src/zephyr/ 文件 → 不 warn
6. warn 不影响 exit code（exit 0）
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _PROJECT_ROOT / "scripts" / "governance" / "d6_security" / "check_protected_paths.py"


def _git_env() -> dict:
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@test.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@test.com"
    for k in ("ZEPHYR_SESSION_ID", "ZEPHYR_RECONCILER_AUTO_COMMIT", "ZEPHYR_PROTECTED_PATHS_BYPASS"):
        env.pop(k, None)
    return env


def _init_repo(repo_dir: Path) -> None:
    repo_dir.mkdir(parents=True, exist_ok=True)
    env = _git_env()
    subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    # 创建 src/zephyr/ 目录结构 + 一个已 commit 的文件
    zephyr_dir = repo_dir / "src" / "zephyr"
    zephyr_dir.mkdir(parents=True, exist_ok=True)
    (zephyr_dir / "module.py").write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "src/zephyr/module.py"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "commit", "-m", "init", "--no-verify"], cwd=str(repo_dir), capture_output=True, env=env, check=True)


def _stage_file(repo_dir: Path, rel_path: str) -> None:
    """修改并 stage 一个文件。"""
    env = _git_env()
    f = repo_dir / rel_path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("# modified\n", encoding="utf-8")
    subprocess.run(["git", "add", rel_path], cwd=str(repo_dir), capture_output=True, env=env, check=True)


def _run_staged(cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(_SCRIPT), "--staged"],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env or _git_env(),
        timeout=15,
    )


class TestWorktreeIsolationWarn:
    """L3.2: worktree 隔离 warn（方向性，不影响 exit code）。

    裁定留痕（2026-08-19 统筹，AI-00 移交清单 5）：test_warn_in_main_workspace 已删——
    其期望的 _warn_worktree_isolation/WORKTREE-ISOLATION warn 在源码与 git 全史零命中
    （超前孤儿测试，4eff7f2769 前序 session 只交了测试功能从未落地）；同语义已由网关
    _warn_non_worktree_commit 覆盖（主仓 commit 活跃 session 警告实证），脚本层补函数
    与 gate 链收敛方向（CAND-GATEMECH-004）相悖。豁免用例保留（功能补全时仍有效）。
    """

    def test_no_warn_in_worktree(self, tmp_path: Path) -> None:
        """worktree 内 staging → 不 warn（豁免）。"""
        _init_repo(tmp_path)
        _stage_file(tmp_path, "src/zephyr/module.py")
        # 模拟 worktree cwd
        wt_dir = tmp_path / ".aidrafts" / "sess-test"
        wt_dir.mkdir(parents=True, exist_ok=True)

        r = _run_staged(wt_dir)
        assert r.returncode == 0
        assert "WORKTREE-ISOLATION" not in r.stderr, f"worktree 内不应 warn: {r.stderr}"

    def test_no_warn_with_session_id(self, tmp_path: Path) -> None:
        """ZEPHYR_SESSION_ID 设置 → 不 warn（豁免）。"""
        _init_repo(tmp_path)
        _stage_file(tmp_path, "src/zephyr/module.py")
        env = _git_env()
        env["ZEPHYR_SESSION_ID"] = "sess-test"

        r = _run_staged(tmp_path, env=env)
        assert r.returncode == 0
        assert "WORKTREE-ISOLATION" not in r.stderr, f"有 session 不应 warn: {r.stderr}"

    def test_no_warn_with_reconciler_env(self, tmp_path: Path) -> None:
        """ZEPHYR_RECONCILER_AUTO_COMMIT=1 → 不 warn（豁免）。"""
        _init_repo(tmp_path)
        _stage_file(tmp_path, "src/zephyr/module.py")
        env = _git_env()
        env["ZEPHYR_RECONCILER_AUTO_COMMIT"] = "1"

        r = _run_staged(tmp_path, env=env)
        assert r.returncode == 0
        assert "WORKTREE-ISOLATION" not in r.stderr, f"reconciler 不应 warn: {r.stderr}"

    def test_no_warn_for_non_zephyr_files(self, tmp_path: Path) -> None:
        """staging 非 src/zephyr/ 文件 → 不 warn。"""
        _init_repo(tmp_path)
        _stage_file(tmp_path, "scripts/helper.py")

        r = _run_staged(tmp_path)
        assert r.returncode == 0
        assert "WORKTREE-ISOLATION" not in r.stderr, f"非 src/zephyr 不应 warn: {r.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
