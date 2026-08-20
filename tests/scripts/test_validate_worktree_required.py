# [A_test] module_id: MOD-INF-005 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | scripts/governance/d11_compliance/validate_worktree_required.py | §gate-worktree-required
# [MODULE] tests.scripts.test_validate_worktree_required
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-INF-005 | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_validate_worktree_required.py — GATE-WORKTREE-REQUIRED 软门禁单测（L3.1 验收）

#ARCH-GIT-SELF-HARM-GUARD L3.1（2026-08-04）。

测试 validate_worktree_required.py 的渐进式软门禁逻辑:
1. worktree 内 commit → 放行 exit 0
2. 主工作区 commit → warn exit 0 + 计数
3. 累计 >= 阈值 → 阻断 exit 1
4. 合并提交 → 放行
5. reconciler auto-commit → 放行
6. 计数日志正确写入

测试隔离: 用 tmp_path 临时 git 仓库 + 子进程调用脚本。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_HOOK_SCRIPT = _PROJECT_ROOT / "scripts" / "governance" / "d11_compliance" / "validate_worktree_required.py"


def _git_env() -> dict:
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@test.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@test.com"
    # 清理可能干扰的 env
    for k in ("ZEPHYR_SESSION_ID", "ZEPHYR_RECONCILER_AUTO_COMMIT"):
        env.pop(k, None)
    return env


def _init_repo(repo_dir: Path) -> None:
    """初始化临时 git 仓库。"""
    repo_dir.mkdir(parents=True, exist_ok=True)
    env = _git_env()
    subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
    )
    (repo_dir / "file1.py").write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "file1.py"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init", "--no-verify"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
    )


def _run_hook(cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    """调用 validate_worktree_required.py。"""
    return subprocess.run(
        [sys.executable, str(_HOOK_SCRIPT)],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env or _git_env(),
        timeout=15,
    )


def _make_worktree_dir(repo_dir: Path) -> Path:
    """构造 .aidrafts/sess-xxx 路径（模拟 worktree cwd）。"""
    wt_dir = repo_dir / ".aidrafts" / "sess-test123"
    wt_dir.mkdir(parents=True, exist_ok=True)
    return wt_dir


class TestWorktreeRequiredGate:
    """L3.1: GATE-WORKTREE-REQUIRED 软门禁。"""

    def test_worktree_commit_passes(self, tmp_path: Path) -> None:
        """worktree 内 commit（cwd 含 .aidrafts/sess-）→ 放行 exit 0。"""
        _init_repo(tmp_path)
        wt_dir = _make_worktree_dir(tmp_path)

        r = _run_hook(wt_dir)
        assert r.returncode == 0, f"worktree 内应放行: {r.stderr}"

    def test_main_workspace_warns_exit0(self, tmp_path: Path) -> None:
        """主工作区 commit → warn exit 0（不阻断）+ 计数。"""
        _init_repo(tmp_path)
        env = _git_env()
        env["ZEPHYR_SESSION_ID"] = "sess-test"

        r = _run_hook(tmp_path, env=env)
        assert r.returncode == 0, f"未超阈值应 warn exit 0: {r.stderr}"
        assert "WARN" in r.stderr, f"应含 WARN: {r.stderr}"
        assert "1/5" in r.stderr or "1/" in r.stderr, f"应显示计数: {r.stderr}"

        # 计数日志应写入
        skip_log = tmp_path / ".runtime" / "gate_audit" / "worktree_skip.jsonl"
        assert skip_log.exists(), f"计数日志应存在: {skip_log}"
        records = [json.loads(line) for line in skip_log.read_text(encoding="utf-8").splitlines() if line]
        assert len(records) == 1
        assert records[0]["session_id"] == "sess-test"

    def test_threshold_escalation_blocks(self, tmp_path: Path) -> None:
        """累计 >= 5 次 → 升级为阻断 exit 1。"""
        _init_repo(tmp_path)
        env = _git_env()
        env["ZEPHYR_SESSION_ID"] = "sess-repeat"

        # 预写 5 条计数记录（模拟已累计 5 次）
        skip_log = tmp_path / ".runtime" / "gate_audit" / "worktree_skip.jsonl"
        skip_log.parent.mkdir(parents=True, exist_ok=True)
        with skip_log.open("a", encoding="utf-8") as f:
            for i in range(5):
                f.write(json.dumps({"timestamp": 0, "session_id": "sess-repeat", "cwd": str(tmp_path)}) + "\n")

        r = _run_hook(tmp_path, env=env)
        assert r.returncode == 1, f"超阈值应阻断 exit 1: {r.stderr}"
        assert "BLOCKED" in r.stderr, f"应含 BLOCKED: {r.stderr}"
        assert "5" in r.stderr, f"应显示累计次数: {r.stderr}"

    def test_merge_commit_passes(self, tmp_path: Path) -> None:
        """合并提交（.git/MERGE_HEAD 存在）→ 放行。"""
        _init_repo(tmp_path)
        # 模拟 merge 状态
        git_dir = tmp_path / ".git"
        (git_dir / "MERGE_HEAD").write_text("abc123\n", encoding="utf-8")

        r = _run_hook(tmp_path)
        assert r.returncode == 0, f"合并提交应放行: {r.stderr}"

    def test_reconciler_auto_commit_passes(self, tmp_path: Path) -> None:
        """reconciler auto-commit（ZEPHYR_RECONCILER_AUTO_COMMIT=1）→ 放行。"""
        _init_repo(tmp_path)
        env = _git_env()
        env["ZEPHYR_RECONCILER_AUTO_COMMIT"] = "1"

        r = _run_hook(tmp_path, env=env)
        assert r.returncode == 0, f"reconciler auto-commit 应放行: {r.stderr}"

    def test_per_session_counting_isolated(self, tmp_path: Path) -> None:
        """不同 session 的计数相互隔离。"""
        _init_repo(tmp_path)
        # session-A 已有 5 条记录
        skip_log = tmp_path / ".runtime" / "gate_audit" / "worktree_skip.jsonl"
        skip_log.parent.mkdir(parents=True, exist_ok=True)
        with skip_log.open("a", encoding="utf-8") as f:
            for i in range(5):
                f.write(json.dumps({"timestamp": 0, "session_id": "sess-A", "cwd": str(tmp_path)}) + "\n")

        # session-B 应从 0 开始（warn 而非 block）
        env = _git_env()
        env["ZEPHYR_SESSION_ID"] = "sess-B"
        r = _run_hook(tmp_path, env=env)
        assert r.returncode == 0, f"session-B 未超阈值应 warn: {r.stderr}"
        assert "1/5" in r.stderr or "1/" in r.stderr, f"session-B 应从 1 开始: {r.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
