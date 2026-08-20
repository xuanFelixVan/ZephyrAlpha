# [BLUEPRINT] MOD-INF-021 | tests/scripts/test_git_guard_self_harm.py | §git-guard-self-harm-tests
# [MODULE] tests.scripts.test_git_guard_self_harm
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.git_guard
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 测试隔离——使用 tmp_path 临时 git 仓库，禁止污染生产 .ailocks/.runtime；子进程 env 显式清理 ZEPHYR_FORCE_STASH/ZEPHYR_COMMIT_GATEWAY/ZEPHYR_GIT_GUARD_FAST_PATH
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_git_guard_self_harm.py — git_guard reset --hard 自伤检测单测（L1 止血验收）

覆盖（对标 .trae/documents/git_reset_self_harm_guard_plan.md L1 验证清单）:
1. reset --hard 有未提交修改 → 阻断 exit 1
2. reset --hard 工作区干净 → 透传 exit 0
3. reset --hard + ZEPHYR_FORCE_STASH=1 → 授权放行 + 审计写入
4. reset --soft/--mixed 不触发自伤检测（透传）
5. ZEPHYR_GIT_GUARD_FAST_PATH=1 → 跳过自伤检测（session_worktree 可信调用方）
6. 阻断时审计文件 .runtime/gate_audit/git_guard_self_harm.jsonl 写入

测试隔离: 所有测试用 tmp_path 临时 git 仓库，子进程 env 显式清理授权标记。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_GIT_GUARD = _PROJECT_ROOT / "scripts" / "git_guard.py"

# 授权相关 env（测试子进程必须显式清理，否则自伤检测被绕过）
_AUTH_ENVS = (
    "ZEPHYR_FORCE_STASH",
    "ZEPHYR_COMMIT_GATEWAY",
    "ZEPHYR_GIT_GUARD_FAST_PATH",
    "ZEPHYR_SERIALIZER_MODE",  # 66 memo 裁定 7 plumbing 白名单
)


def _clean_env() -> dict[str, str]:
    """构造不含任何授权标记的子进程 env（确保自伤检测生效）。"""
    env = os.environ.copy()
    for key in _AUTH_ENVS:
        env.pop(key, None)
    return env


def _init_repo(repo_dir: Path) -> None:
    """初始化临时 git 仓库 + 一个已 commit 的 tracked 文件。"""
    repo_dir.mkdir(parents=True, exist_ok=True)
    env = _clean_env()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@test.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@test.com"
    subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
    )
    f = repo_dir / "tracked.py"
    f.write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.py"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init", "--no-verify"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
    )


def _run_guard(repo_dir: Path, args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    """调用 git_guard.py（模拟 git alias 触发）。"""
    return subprocess.run(
        [sys.executable, str(_GIT_GUARD)] + args,
        cwd=str(repo_dir),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env or _clean_env(),
        timeout=30,
    )


# ---------------------------------------------------------------------------
# reset --hard 自伤检测
# ---------------------------------------------------------------------------
class TestResetHardSelfHarm:
    """L1 止血：reset --hard 自伤检测核心场景。"""

    def test_blocked_when_dirty(self, tmp_path: Path) -> None:
        """有未提交修改 → 阻断 exit 1 + stderr 含'自伤防护'。"""
        _init_repo(tmp_path)
        # 制造未提交修改
        (tmp_path / "tracked.py").write_text("x = 999\n", encoding="utf-8")

        r = _run_guard(tmp_path, ["reset", "--hard", "HEAD"])

        assert r.returncode == 1, f"应阻断，got rc={r.returncode}, stderr={r.stderr}"
        assert "自伤防护" in r.stderr, f"stderr 应含'自伤防护': {r.stderr}"
        assert "tracked.py" in r.stderr, f"stderr 应列出未提交文件: {r.stderr}"
        # 工作区修改应保留（未被 reset 覆盖）
        assert (tmp_path / "tracked.py").read_text(encoding="utf-8") == "x = 999\n", "未提交修改应保留"

    def test_passthrough_when_clean(self, tmp_path: Path) -> None:
        """工作区干净 → 透传 exit 0（git 真实执行 reset，无害）。"""
        _init_repo(tmp_path)

        r = _run_guard(tmp_path, ["reset", "--hard", "HEAD"])

        assert r.returncode == 0, f"干净工作区应透传，got rc={r.returncode}, stderr={r.stderr}"

    def test_forced_via_force_stash(self, tmp_path: Path) -> None:
        """ZEPHYR_FORCE_STASH=1 → 授权放行 + 审计写入 + 修改被丢弃。"""
        _init_repo(tmp_path)
        (tmp_path / "tracked.py").write_text("x = 999\n", encoding="utf-8")

        env = _clean_env()
        env["ZEPHYR_FORCE_STASH"] = "1"
        r = _run_guard(tmp_path, ["reset", "--hard", "HEAD"], env=env)

        assert r.returncode == 0, f"授权应放行，got rc={r.returncode}, stderr={r.stderr}"
        assert "授权放行" in r.stderr, f"应提示授权放行: {r.stderr}"
        # 修改应被 reset 丢弃
        assert (tmp_path / "tracked.py").read_text(encoding="utf-8") == "x = 1\n", "授权后修改应被丢弃"
        # 审计文件应写入
        audit_log = tmp_path / ".runtime" / "gate_audit" / "git_guard_self_harm.jsonl"
        assert audit_log.exists(), f"审计文件应存在: {audit_log}"
        records = [json.loads(line) for line in audit_log.read_text(encoding="utf-8").splitlines() if line]
        assert any(rec.get("forced") is True and rec.get("had_uncommitted") for rec in records), (
            f"审计记录应含 forced=True + had_uncommitted=True: {records}"
        )

    def test_reset_soft_not_blocked(self, tmp_path: Path) -> None:
        """reset --soft HEAD 不触发自伤检测（--soft 只动 HEAD，不覆盖工作区）。"""
        _init_repo(tmp_path)
        (tmp_path / "tracked.py").write_text("x = 999\n", encoding="utf-8")
        # 先 stage 修改，reset --soft 只回退 HEAD，保留工作区+index
        subprocess.run(
            ["git", "add", "tracked.py"], cwd=str(tmp_path), capture_output=True, env=_clean_env(), check=True
        )

        r = _run_guard(tmp_path, ["reset", "--soft", "HEAD"])

        # --soft 不触发自伤检测，应透传（rc=0）
        assert r.returncode == 0, f"reset --soft 应透传，got rc={r.returncode}, stderr={r.stderr}"
        # 工作区修改应保留
        assert (tmp_path / "tracked.py").read_text(encoding="utf-8") == "x = 999\n", "reset --soft 不应覆盖工作区"

    def test_fast_path_skips_self_harm(self, tmp_path: Path) -> None:
        """ZEPHYR_GIT_GUARD_FAST_PATH=1 → 跳过自伤检测（session_worktree 可信调用方）。"""
        _init_repo(tmp_path)
        (tmp_path / "tracked.py").write_text("x = 999\n", encoding="utf-8")

        env = _clean_env()
        env["ZEPHYR_GIT_GUARD_FAST_PATH"] = "1"
        r = _run_guard(tmp_path, ["reset", "--hard", "HEAD"], env=env)

        # fast-path 跳过自伤检测，直接透传 → reset 执行 → 修改被丢弃
        assert r.returncode == 0, f"fast-path 应透传，got rc={r.returncode}, stderr={r.stderr}"
        assert (tmp_path / "tracked.py").read_text(encoding="utf-8") == "x = 1\n", "fast-path 后修改被 reset 丢弃"
        # 不应出现自伤防护阻断信息
        assert "自伤防护" not in r.stderr, f"fast-path 不应触发自伤检测: {r.stderr}"

    def test_audit_log_written_on_block(self, tmp_path: Path) -> None:
        """阻断时审计文件写入 forced=False + had_uncommitted=True。"""
        _init_repo(tmp_path)
        (tmp_path / "tracked.py").write_text("x = 999\n", encoding="utf-8")

        r = _run_guard(tmp_path, ["reset", "--hard", "HEAD"])

        assert r.returncode == 1, "应阻断"
        audit_log = tmp_path / ".runtime" / "gate_audit" / "git_guard_self_harm.jsonl"
        assert audit_log.exists(), f"审计文件应存在: {audit_log}"
        records = [json.loads(line) for line in audit_log.read_text(encoding="utf-8").splitlines() if line]
        assert any(
            rec.get("forced") is False and rec.get("had_uncommitted") and rec.get("file_count", 0) >= 1
            for rec in records
        ), f"审计记录应含 forced=False + had_uncommitted=True: {records}"


# ---------------------------------------------------------------------------
# checkout -- / restore 自伤检测（L2.1）
# ---------------------------------------------------------------------------
class TestCheckoutRestoreSelfHarm:
    """L2.1：checkout -- <file> / restore <file> 自伤检测。"""

    def test_checkout_dash_dash_blocked(self, tmp_path: Path) -> None:
        """checkout -- <file> 有未提交修改 → 阻断 exit 1。"""
        _init_repo(tmp_path)
        (tmp_path / "tracked.py").write_text("x = 999\n", encoding="utf-8")

        r = _run_guard(tmp_path, ["checkout", "--", "tracked.py"])

        assert r.returncode == 1, f"应阻断，got rc={r.returncode}, stderr={r.stderr}"
        assert "自伤防护" in r.stderr, f"stderr 应含'自伤防护': {r.stderr}"
        assert "tracked.py" in r.stderr, f"stderr 应列出 at-risk 文件: {r.stderr}"
        # 修改应保留
        assert (tmp_path / "tracked.py").read_text(encoding="utf-8") == "x = 999\n", "未提交修改应保留"

    def test_restore_blocked(self, tmp_path: Path) -> None:
        """restore <file> 有未提交修改 → 阻断 exit 1。"""
        _init_repo(tmp_path)
        (tmp_path / "tracked.py").write_text("x = 999\n", encoding="utf-8")

        r = _run_guard(tmp_path, ["restore", "tracked.py"])

        assert r.returncode == 1, f"应阻断，got rc={r.returncode}, stderr={r.stderr}"
        assert "自伤防护" in r.stderr, f"stderr 应含'自伤防护': {r.stderr}"
        assert "tracked.py" in r.stderr, f"stderr 应列出 at-risk 文件: {r.stderr}"
        assert (tmp_path / "tracked.py").read_text(encoding="utf-8") == "x = 999\n", "未提交修改应保留"

    def test_restore_forced_via_force_stash(self, tmp_path: Path) -> None:
        """restore + ZEPHYR_FORCE_STASH=1 → 授权放行 + 修改被丢弃。"""
        _init_repo(tmp_path)
        (tmp_path / "tracked.py").write_text("x = 999\n", encoding="utf-8")

        env = _clean_env()
        env["ZEPHYR_FORCE_STASH"] = "1"
        r = _run_guard(tmp_path, ["restore", "tracked.py"], env=env)

        assert r.returncode == 0, f"授权应放行，got rc={r.returncode}, stderr={r.stderr}"
        assert "授权放行" in r.stderr, f"应提示授权放行: {r.stderr}"
        assert (tmp_path / "tracked.py").read_text(encoding="utf-8") == "x = 1\n", "授权后修改应被丢弃"

    def test_checkout_branch_not_blocked_by_self_harm(self, tmp_path: Path) -> None:
        """checkout <branch>（无 --）不触发自伤检测（git 本会处理未提交修改）。

        即使工作区有未提交修改，git_guard 不应阻断 checkout <branch>——
        切分支的未提交修改处理由 git 本身负责（拒绝或携带），不在自伤检测范围。
        """
        _init_repo(tmp_path)
        # 创建新分支（与 HEAD 同点，切换会成功并保留未提交修改）
        subprocess.run(
            ["git", "branch", "branch2"], cwd=str(tmp_path), capture_output=True, env=_clean_env(), check=True
        )
        (tmp_path / "tracked.py").write_text("x = 999\n", encoding="utf-8")

        r = _run_guard(tmp_path, ["checkout", "branch2"])

        # 不被自伤检测阻断（returncode 不应是 1 因自伤；stderr 不含"自伤防护"）
        assert "自伤防护" not in r.stderr, f"checkout <branch> 不应触发自伤检测: {r.stderr}"

    def test_restore_clean_file_passthrough(self, tmp_path: Path) -> None:
        """restore <file> 文件无未提交修改 → 透传 exit 0。"""
        _init_repo(tmp_path)
        # tracked.py 无修改（与 HEAD 一致）

        r = _run_guard(tmp_path, ["restore", "tracked.py"])

        assert r.returncode == 0, f"干净文件应透传，got rc={r.returncode}, stderr={r.stderr}"


# ---------------------------------------------------------------------------
# plumbing 命令拦截（66 memo 裁定 7，事故 6 根因）
# ---------------------------------------------------------------------------
class TestPlumbingBlocked:
    """read-tree/update-index/write-tree/hash-object 直操纵共享 index/对象库，默认硬阻断。"""

    @pytest.mark.parametrize(
        "args",
        [
            ["read-tree", "HEAD"],
            ["update-index", "--add", "tracked.py"],
            ["write-tree"],
            ["hash-object", "-w", "tracked.py"],
        ],
    )
    def test_plumbing_blocked_by_default(self, tmp_path: Path, args: list[str]) -> None:
        """无白名单 → 阻断 exit 1 + stderr 提示 + 审计落盘。"""
        _init_repo(tmp_path)
        r = _run_guard(tmp_path, args)
        assert r.returncode == 1, f"应阻断: {args}, rc={r.returncode}, stderr={r.stderr}"
        assert "plumbing" in r.stderr, f"stderr 应含 plumbing 提示: {r.stderr}"
        # index 未被触碰（read-tree 若真执行会清 staged 区——此处验证未执行）
        audit = tmp_path / ".runtime" / "gate_audit" / "git_guard_self_harm.jsonl"
        assert audit.is_file(), "阻断应落审计"
        assert f"plumbing:{args[0]}" in audit.read_text(encoding="utf-8"), "审计应含 plumbing 动作"

    def test_serializer_mode_whitelist_passthrough(self, tmp_path: Path) -> None:
        """ZEPHYR_SERIALIZER_MODE=1 → 透传真实 git（临时仓 read-tree HEAD 无副作用）。"""
        _init_repo(tmp_path)
        env = _clean_env()
        env["ZEPHYR_SERIALIZER_MODE"] = "1"
        r = _run_guard(tmp_path, ["read-tree", "HEAD"], env=env)
        assert r.returncode == 0, f"白名单应透传，rc={r.returncode}, stderr={r.stderr}"
        assert "plumbing" not in r.stderr, f"白名单不应触发阻断提示: {r.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
