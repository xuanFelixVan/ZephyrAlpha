# [A_test] module_id: MOD-GOV_session_worktree_health_check_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_SESSION_WORKTREE | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §FP-ISO.4C
# [MODULE] tests.governance.rule_bridge.test_session_worktree_health_check
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_SESSION_WORKTREE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_session_worktree_health_check.py — session_worktree_start 启动健康度自检测试

#ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD-S7 Phase 3.3 治本 G7：
验证 session_worktree_start 调用时执行健康度 smoke test，检测：
  1. capability_lookup_required_gate 模块能否 import
  2. .runtime/lookup_audit/ 目录可写
  3. capability_lookup.write_lookup_audit_log 函数可调用

对标 §11.0.3 #ARCH-TOOL-HEALTH-V1——失败时 [ESCALATION] 上报而非静默 workaround。

测试组：
- TestRunStartupHealthCheck: 直接调用 _run_startup_health_check helper
- TestStartReturnsHealthCheck: session_worktree_start 返回值含 health_check 字段
- TestHealthCheckNonBlocking: 健康检查失败不阻断 session 创建（warn-only）
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_ROOT = _PROJECT_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))


# ---------------------------------------------------------------------------
# TestRunStartupHealthCheck
# ---------------------------------------------------------------------------
pytestmark = pytest.mark.silent_failure  # Ruling:100PCT-AI-GOVERNANCE P3-2


class TestRunStartupHealthCheck:
    """直接调用 _run_startup_health_check helper 测试。"""

    def test_returns_ok_on_healthy_environment(self, tmp_path: Path):
        """健康环境 → status='ok' + 3 项检查全 pass。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import _run_startup_health_check

        result = _run_startup_health_check(tmp_path)
        assert result["status"] == "ok", f"健康环境应返回 ok: {result}"
        assert len(result["checks"]) == 3, f"应有 3 项检查，实际 {len(result['checks'])}"
        for check in result["checks"]:
            assert check["passed"] is True, f"检查项应通过: {check}"
            assert "name" in check
            assert "detail" in check

    def test_check_names_cover_three_paths(self, tmp_path: Path):
        """3 项检查覆盖 gate import / audit dir / write_lookup_audit_log。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import _run_startup_health_check

        result = _run_startup_health_check(tmp_path)
        names = {c["name"] for c in result["checks"]}
        assert "capability_lookup_required_gate import" in names
        assert "lookup_audit dir writable" in names
        assert "capability_lookup.write_lookup_audit_log callable" in names

    def test_creates_audit_dir_if_missing(self, tmp_path: Path):
        """.runtime/lookup_audit/ 目录不存在时自动创建。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import _run_startup_health_check

        audit_dir = tmp_path / ".runtime" / "lookup_audit"
        assert not audit_dir.exists(), "前置：目录应不存在"
        _run_startup_health_check(tmp_path)
        assert audit_dir.is_dir(), "健康检查后目录应已创建"

    def test_returns_failed_when_audit_dir_unwritable(self, tmp_path: Path):
        """audit dir 不可写时 → status='failed'（但仍不抛异常）。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import _run_startup_health_check

        # 模拟不可写：.runtime 路径被一个文件占位（mkdir 失败）
        runtime_blocker = tmp_path / ".runtime"
        runtime_blocker.write_text("blocker", encoding="utf-8")
        result = _run_startup_health_check(tmp_path)
        # 至少 audit_dir 检查失败
        audit_check = next(
            (c for c in result["checks"] if c["name"] == "lookup_audit dir writable"),
            None,
        )
        assert audit_check is not None
        assert audit_check["passed"] is False, f"audit dir 被文件占位时检查应失败: {audit_check}"
        assert result["status"] == "failed"


# ---------------------------------------------------------------------------
# TestStartReturnsHealthCheck
# ---------------------------------------------------------------------------


class TestStartReturnsHealthCheck:
    """session_worktree_start 返回值含 health_check 字段。"""

    def test_start_returns_health_check_field(self, tmp_path: Path):
        """session_worktree_start 成功时返回值含 health_check 字段。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import session_worktree_start

        _init_test_repo(tmp_path)
        result = session_worktree_start(
            session_id="sess-hc-001",
            project_root=tmp_path,
            allow_concurrent=True,
        )
        assert "health_check" in result, f"返回值应含 health_check 字段: {result.keys()}"
        hc = result["health_check"]
        assert hc["status"] in ("ok", "failed"), f"health_check.status 应为 ok/failed: {hc}"
        assert "checks" in hc
        assert len(hc["checks"]) == 3
        # 清理
        try:
            from zephyr.gov_enforcement.rule_bridge.session_worktree import session_worktree_abort

            session_worktree_abort("sess-hc-001", project_root=tmp_path)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# TestHealthCheckNonBlocking
# ---------------------------------------------------------------------------


class TestHealthCheckNonBlocking:
    """健康检查失败不阻断 session 创建（warn-only 设计）。"""

    def test_start_succeeds_even_if_health_check_fails(self, tmp_path: Path):
        """即使健康检查失败，session 仍应创建（非阻断）。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import session_worktree_start

        _init_test_repo(tmp_path)
        # mock _run_startup_health_check 返回失败
        failed_hc = {
            "status": "failed",
            "checks": [
                {"name": "capability_lookup_required_gate import", "passed": False, "detail": "mocked failure"},
            ],
        }
        with patch(
            "zephyr.gov_enforcement.rule_bridge.session_worktree.run_startup_health_check",
            return_value=failed_hc,
        ):
            result = session_worktree_start(
                session_id="sess-hc-fail",
                project_root=tmp_path,
                allow_concurrent=True,
            )
        # session 仍应创建成功（健康检查不阻断）
        assert result.get("registered") is True or result.get("created") is True, (
            f"健康检查失败时 session 仍应创建: {result}"
        )
        # health_check 字段应反映失败状态
        assert result["health_check"]["status"] == "failed"
        # 清理
        try:
            from zephyr.gov_enforcement.rule_bridge.session_worktree import session_worktree_abort

            session_worktree_abort("sess-hc-fail", project_root=tmp_path)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# 测试辅助
# ---------------------------------------------------------------------------


def _init_test_repo(repo_dir: Path) -> None:
    """初始化一个 git 仓库用于测试（含必要 stub）。"""
    import subprocess

    repo_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@test.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@test.com"
    subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
    )
    (repo_dir / ".gitignore").write_text("*.tmp\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init", "--no-verify"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
    )
