# [A_test] module_id: MOD-GOV_GIT_GUARD_BYPASS_RECONCILER | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_GIT_GUARD_BYPASS_RECONCILER | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §git-guard-bypass-reconciler
# [MODULE] tests.governance.audit.test_git_guard_bypass_reconciler
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-GOV_GIT_GUARD_BYPASS_RECONCILER | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_git_guard_bypass_reconciler.py — git_guard alias 绕过检测 reconciler 单测（L2.3 验收）

#ARCH-GIT-SELF-HARM-GUARD L2.3（2026-08-04）。

测试 make_git_guard_bypass_reconciler 的对比逻辑:
1. 窗口内无 reset → skip
2. 窗口内 reset 全被审计 → clean
3. 窗口内 reset 但审计日志不存在 → warn（强信号：疑似绕过）
4. 窗口内 reset 多于审计记录 → warn（弱信号：部分绕过）
5. 首次 commit（无 HEAD~1）→ skip
6. reconciler 异常降级为 warn（永不抛异常）

测试隔离: 用 tmp_path 临时 git 仓库，构造 reflog + 审计日志场景。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_DIR = str(_PROJECT_ROOT / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from zephyr.governance.audit.git_guard_bypass_reconciler import (  # noqa: E402
    make_git_guard_bypass_reconciler,
)


def _git_env() -> dict:
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@test.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@test.com"
    # 清理可能干扰的授权 env
    for k in ("ZEPHYR_FORCE_STASH", "ZEPHYR_COMMIT_GATEWAY", "ZEPHYR_GIT_GUARD_FAST_PATH"):
        env.pop(k, None)
    return env


def _init_repo(repo_dir: Path) -> None:
    """初始化临时 git 仓库 + 一个初始 commit。"""
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


def _make_commit(repo_dir: Path, msg: str, filename: str = "file2.py") -> None:
    """创建一个新 commit（产生 HEAD~1 窗口）。"""
    env = _git_env()
    (repo_dir / filename).write_text(f"# {msg}\n", encoding="utf-8")
    subprocess.run(["git", "add", filename], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "commit", "-m", msg, "--no-verify"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
    )


def _do_reset_hard(repo_dir: Path) -> None:
    """执行一次真实 reset --hard（产生 reflog reset 条目）。"""
    env = _git_env()
    # 绕过 alias 直接调 git（模拟绕过场景）
    subprocess.run(
        ["git", "-c", "alias.reset=", "reset", "--hard", "HEAD"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
    )


def _write_audit_log(repo_dir: Path, records: list[dict]) -> None:
    """写入审计日志。"""
    audit_dir = repo_dir / ".runtime" / "gate_audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    audit_log = audit_dir / "git_guard_self_harm.jsonl"
    with audit_log.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _make_gateway(project_root: Path) -> MagicMock:
    """构造 mock gateway（仅用 project_root）。"""
    gw = MagicMock()
    gw.project_root = project_root
    return gw


class TestGitGuardBypassReconciler:
    """L2.3: git_guard alias 绕过检测 reconciler。"""

    def test_no_reset_in_window_skip(self, tmp_path: Path) -> None:
        """窗口内无 reset 操作 → skip。"""
        _init_repo(tmp_path)
        # 直接 commit，不 reset
        _make_commit(tmp_path, "second")

        spec = make_git_guard_bypass_reconciler(_make_gateway(tmp_path))
        assert spec.gate_id == "GATE-GIT-GUARD-BYPASS"
        assert spec.priority == 810

        result = spec.reconcile(["file2.py"], "sess-test")
        assert result.action == "skip", f"无 reset 应 skip: {result.detail}"
        assert "无 reset" in result.detail

    def test_reset_all_audited_clean(self, tmp_path: Path) -> None:
        """窗口内 reset 全部被审计 → clean。"""
        _init_repo(tmp_path)
        # 获取初始 commit 时间戳作为窗口起点
        t_before_reset = time.time()
        _do_reset_hard(tmp_path)  # 产生 reflog reset
        t_after_reset = time.time()
        # 写入审计记录（模拟 git_guard 审计了这次 reset）
        _write_audit_log(
            tmp_path,
            [
                {
                    "timestamp": int((t_before_reset + t_after_reset) / 2),
                    "session_id": "sess-test",
                    "had_uncommitted": False,
                    "forced": False,
                    "file_count": 0,
                    "files_sample": [],
                }
            ],
        )
        _make_commit(tmp_path, "second")  # 产生 HEAD~1 窗口

        spec = make_git_guard_bypass_reconciler(_make_gateway(tmp_path))
        result = spec.reconcile(["file2.py"], "sess-test")
        assert result.action == "clean", f"全审计应 clean: {result.detail}"
        assert "无绕过" in result.detail or "全部被审计" in result.detail

    def test_reset_no_audit_log_warn_strong(self, tmp_path: Path) -> None:
        """窗口内 reset 但审计日志不存在 → warn（强信号：疑似绕过）。"""
        _init_repo(tmp_path)
        _do_reset_hard(tmp_path)  # 产生 reflog reset，但不写审计日志（模拟绕过）
        _make_commit(tmp_path, "second")

        spec = make_git_guard_bypass_reconciler(_make_gateway(tmp_path))
        result = spec.reconcile(["file2.py"], "sess-test")
        assert result.action == "warn", f"无审计应 warn: {result.detail}"
        assert "疑似" in result.detail or "绕过" in result.detail
        assert "审计文件不存在" in result.detail

    def test_reset_more_than_audit_warn_weak(self, tmp_path: Path) -> None:
        """窗口内 reset 多于审计记录 → warn（弱信号：部分绕过）。"""
        _init_repo(tmp_path)
        t_before = time.time()
        _do_reset_hard(tmp_path)  # 第 1 次 reset
        _do_reset_hard(tmp_path)  # 第 2 次 reset（共 2 条 reflog）
        t_after = time.time()
        # 只审计了 1 次（模拟部分绕过）
        _write_audit_log(
            tmp_path,
            [
                {
                    "timestamp": int((t_before + t_after) / 2),
                    "session_id": "sess-test",
                    "had_uncommitted": False,
                    "forced": False,
                    "file_count": 0,
                    "files_sample": [],
                }
            ],
        )
        _make_commit(tmp_path, "second")

        spec = make_git_guard_bypass_reconciler(_make_gateway(tmp_path))
        result = spec.reconcile(["file2.py"], "sess-test")
        assert result.action == "warn", f"部分绕过应 warn: {result.detail}"
        assert "差值" in result.detail or "部分" in result.detail or ">" in result.detail

    def test_first_commit_skip(self, tmp_path: Path) -> None:
        """首次 commit（无 HEAD~1）→ skip。"""
        _init_repo(tmp_path)
        # 此时只有 1 个 commit（init），无 HEAD~1
        spec = make_git_guard_bypass_reconciler(_make_gateway(tmp_path))
        result = spec.reconcile(["file1.py"], "sess-test")
        assert result.action == "skip", f"首次 commit 应 skip: {result.detail}"
        assert "首次" in result.detail or "HEAD~1" in result.detail

    def test_trigger_fires_on_any_commit(self, tmp_path: Path) -> None:
        """trigger 对任何非空 committed_files 返回 True。"""
        spec = make_git_guard_bypass_reconciler(_make_gateway(tmp_path))
        assert spec.trigger(["file.py"]) is True
        assert spec.trigger([]) is False

    def test_reconciler_never_raises(self, tmp_path: Path) -> None:
        """reconciler 永不抛异常（即使 git 命令失败也降级为 warn/skip）。"""
        # 指向一个非 git 目录
        bad_dir = tmp_path / "not_a_repo"
        bad_dir.mkdir()
        spec = make_git_guard_bypass_reconciler(_make_gateway(bad_dir))
        # 不应抛异常
        result = spec.reconcile(["file.py"], "sess-test")
        assert result.action in ("skip", "warn"), f"异常应降级: {result.action}"
        assert result.gate_id == "GATE-GIT-GUARD-BYPASS"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
