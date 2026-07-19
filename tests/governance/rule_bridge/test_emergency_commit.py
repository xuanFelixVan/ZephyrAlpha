# [BLUEPRINT] MOD-GOV-test_emergency_commit | tests/governance/rule_bridge/test_emergency_commit.py | §Ruling-100PCT-AI-GOVERNANCE-P2-1
# [MODULE] tests.governance.rule_bridge.test_emergency_commit
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.emergency_commit
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 临时 git 仓库隔离测试，不污染主仓库；每个测试独立 repo
# [MODIFY-GUARD] 测试函数名与 emergency_commit API 对齐
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败→pytest assert error
# [TESTS] self
# [TTL] permanent
"""test_emergency_commit.py — emergency_commit API 测试（Ruling:100PCT-AI-GOVERNANCE P2-1）

测试覆盖：
  1. 输入校验（空文件列表、空 session_id、文件不存在）
  2. 基本提交（单文件修改、新文件创建）
  3. 多文件提交
  4. commit message [GW:...:emergency] 标记
  5. 持久化到 reconcile_execution_log
  6. 审计报告文件生成

测试策略：
  - 每个测试用独立临时 git 仓库（_isolated_repo fixture），不污染主仓库
  - monkeypatch REPO_ROOT 指向临时仓库
  - 验证 commit 真实写入 git history（git log + git show）
  - 验证 DB 记录（sqlite3 直查 governance.db）
"""

from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def isolated_repo(tmp_path_factory, monkeypatch):
    """临时 git 仓库，每个测试独立，不污染主仓库。

    对标 test_session_worktree.py 的 _isolated_repo fixture，但简化：
    emergency_commit 不需要 worktree/gate stub，只需基础 git repo。
    """
    repo = tmp_path_factory.mktemp("ec_test_repo")
    subprocess.run(["git", "init"], cwd=repo, capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@zephyr.local"],
        cwd=repo, capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Zephyr Test"],
        cwd=repo, capture_output=True, check=True,
    )
    # 初始 commit（emergency_commit 需要 HEAD 作为 parent）
    (repo / ".gitkeep").write_text("", encoding="utf-8")
    subprocess.run(["git", "add", ".gitkeep"], cwd=repo, capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init"], cwd=repo, capture_output=True, check=True,
    )

    # monkeypatch emergency_commit 模块的 REPO_ROOT
    import zephyr.gov_enforcement.rule_bridge.emergency_commit as ec_mod
    monkeypatch.setattr(ec_mod, "REPO_ROOT", repo)

    return repo


def _make_tracked_file(repo: Path, name: str, content: str) -> Path:
    """创建并 commit 一个已跟踪文件（作为修改基础）。"""
    f = repo / name
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", name], cwd=repo, capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"add {name}"], cwd=repo, capture_output=True, check=True,
    )
    return f


def _get_commit_message(repo: Path, ref: str = "HEAD") -> str:
    """获取指定 ref 的完整 commit message。"""
    r = subprocess.run(
        ["git", "log", "-1", "--format=%B", ref],
        cwd=repo, capture_output=True, text=True, check=True,
    )
    return r.stdout


def _get_head_sha(repo: Path) -> str:
    """获取 HEAD SHA。"""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo, capture_output=True, text=True, check=True,
    )
    return r.stdout.strip()


def _query_reconcile_log(repo: Path) -> list[dict]:
    """读取 governance.db 的 reconcile_execution_log 表。"""
    db_path = repo / "data" / "databases" / "governance.db"
    if not db_path.exists():
        return []
    conn = sqlite3.connect(str(db_path))
    try:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT log_id, gate_id, session_id, trigger_source, action, detail, "
            "committed_files_summary, commit_message "
            "FROM reconcile_execution_log"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 输入校验测试
# ---------------------------------------------------------------------------


class TestInputValidation:
    """emergency_commit 输入校验。"""

    def test_empty_files_returns_failed(self, isolated_repo):
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import emergency_commit
        result = emergency_commit(
            files=[],
            message="test",
            session_id="sess-test-001",
            project_root=str(isolated_repo),
        )
        assert result["ok"] is False
        assert result["status"] == "FAILED"
        assert "empty files list" in result["error"]

    def test_empty_session_id_returns_failed(self, isolated_repo):
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import emergency_commit
        result = emergency_commit(
            files=[".gitkeep"],
            message="test",
            session_id="",
            project_root=str(isolated_repo),
        )
        assert result["ok"] is False
        assert "session_id required" in result["error"]

    def test_nonexistent_file_returns_failed(self, isolated_repo):
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import emergency_commit
        result = emergency_commit(
            files=["nonexistent_file.py"],
            message="test",
            session_id="sess-test-001",
            project_root=str(isolated_repo),
        )
        assert result["ok"] is False
        assert "不存在" in result["error"] or "not exist" in result["error"].lower()


# ---------------------------------------------------------------------------
# 基本提交测试
# ---------------------------------------------------------------------------


class TestBasicCommit:
    """emergency_commit 基本提交功能。"""

    def test_single_file_modification(self, isolated_repo):
        """修改已跟踪文件并提交。"""
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import emergency_commit
        # 创建已跟踪文件
        f = _make_tracked_file(isolated_repo, "src/module.py", "old content\n")
        # 修改文件
        f.write_text("new content\n", encoding="utf-8")

        orig_sha = _get_head_sha(isolated_repo)
        result = emergency_commit(
            files=[str(f)],
            message="fix: update module content",
            session_id="sess-ec-001",
            project_root=str(isolated_repo),
            reason="test basic commit",
            trigger_reconcilers=False,  # 测试环境无 reconciler
        )
        assert result["ok"] is True, f"expected ok=True, got: {result}"
        assert result["status"] == "OK"
        assert result["commit_hash"], "commit_hash should be non-empty"
        assert result["files_count"] == 1

        # 验证 HEAD 前进
        new_sha = _get_head_sha(isolated_repo)
        assert new_sha != orig_sha, "HEAD should advance after commit"

        # 验证 commit 内容
        msg = _get_commit_message(isolated_repo)
        assert "fix: update module content" in msg
        assert "[GW:sess-ec-001:emergency]" in msg

    def test_new_file_creation(self, isolated_repo):
        """创建新文件（不在 HEAD tree 中，测试 --add flag）。"""
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import emergency_commit
        new_file = isolated_repo / "src" / "new_module.py"
        new_file.parent.mkdir(parents=True, exist_ok=True)
        new_file.write_text("# new module\n", encoding="utf-8")

        result = emergency_commit(
            files=[str(new_file)],
            message="feat: add new module",
            session_id="sess-ec-002",
            project_root=str(isolated_repo),
            reason="test new file",
            trigger_reconcilers=False,
        )
        assert result["ok"] is True, f"expected ok=True, got: {result}"
        assert result["commit_hash"]

        # 验证新文件在 HEAD commit tree 中
        # 注意：不能用 git ls-files（读主 index），因为 emergency_commit 用临时 index
        # 不污染主 index。用 git ls-tree HEAD 验证文件在 commit tree 中。
        r = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", "HEAD"],
            cwd=isolated_repo, capture_output=True, text=True,
        )
        tracked_files = r.stdout.strip().split("\n")
        assert "src/new_module.py" in tracked_files, \
            f"new file should be in HEAD tree, got: {tracked_files}"

    def test_multiple_files(self, isolated_repo):
        """多文件提交。"""
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import emergency_commit
        f1 = _make_tracked_file(isolated_repo, "file1.py", "content1\n")
        f2 = _make_tracked_file(isolated_repo, "file2.py", "content2\n")
        f1.write_text("updated1\n", encoding="utf-8")
        f2.write_text("updated2\n", encoding="utf-8")

        result = emergency_commit(
            files=[str(f1), str(f2)],
            message="update both files",
            session_id="sess-ec-003",
            project_root=str(isolated_repo),
            reason="test multi-file",
            trigger_reconcilers=False,
        )
        assert result["ok"] is True, f"expected ok=True, got: {result}"
        assert result["files_count"] == 2

        # 验证两个文件都在最新 commit 中
        r = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
            cwd=isolated_repo, capture_output=True, text=True,
        )
        changed = r.stdout.strip().split("\n")
        assert "file1.py" in changed
        assert "file2.py" in changed


# ---------------------------------------------------------------------------
# 审计与持久化测试
# ---------------------------------------------------------------------------


class TestAuditPersistence:
    """emergency_commit 治理可见性测试。"""

    def test_gw_emergency_marker_in_message(self, isolated_repo):
        """commit message 必须含 [GW:{session_id}:emergency] 标记。"""
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import emergency_commit
        f = _make_tracked_file(isolated_repo, "audit_test.py", "old\n")
        f.write_text("new\n", encoding="utf-8")

        result = emergency_commit(
            files=[str(f)],
            message="audit marker test",
            session_id="sess-audit-001",
            project_root=str(isolated_repo),
            reason="verify GW marker",
            trigger_reconcilers=False,
        )
        assert result["ok"] is True

        msg = _get_commit_message(isolated_repo)
        assert "[GW:sess-audit-001:emergency]" in msg, \
            f"GW emergency marker missing in: {msg}"

    def test_reason_in_message(self, isolated_repo):
        """commit message 应包含 reason（便于事后审计）。"""
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import emergency_commit
        f = _make_tracked_file(isolated_repo, "reason_test.py", "old\n")
        f.write_text("new\n", encoding="utf-8")

        test_reason = "GitCommitGateway lock stuck 60s timeout"
        result = emergency_commit(
            files=[str(f)],
            message="reason test",
            session_id="sess-reason-001",
            project_root=str(isolated_repo),
            reason=test_reason,
            trigger_reconcilers=False,
        )
        assert result["ok"] is True

        msg = _get_commit_message(isolated_repo)
        assert test_reason in msg, f"reason missing in commit message: {msg}"

    def test_persisted_to_reconcile_log(self, isolated_repo):
        """emergency_commit 必须持久化到 reconcile_execution_log 表。"""
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import emergency_commit
        f = _make_tracked_file(isolated_repo, "db_test.py", "old\n")
        f.write_text("new\n", encoding="utf-8")

        result = emergency_commit(
            files=[str(f)],
            message="db persistence test",
            session_id="sess-db-001",
            project_root=str(isolated_repo),
            reason="verify DB log",
            trigger_reconcilers=False,
        )
        assert result["ok"] is True

        rows = _query_reconcile_log(isolated_repo)
        ec_rows = [r for r in rows if r.get("action") == "emergency_commit"]
        assert len(ec_rows) >= 1, \
            f"expected >=1 emergency_commit row, got: {rows}"

        row = ec_rows[-1]
        assert row["gate_id"] == "EMERGENCY-COMMIT"
        assert row["session_id"] == "sess-db-001"
        assert row["trigger_source"] == "emergency_commit"
        assert "db_test.py" in row["committed_files_summary"]
        assert "[GW:sess-db-001:emergency]" in row["commit_message"]

    def test_report_file_generated(self, isolated_repo):
        """审计报告文件应生成在 .runtime/reconcile_reports/。"""
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import emergency_commit
        f = _make_tracked_file(isolated_repo, "report_test.py", "old\n")
        f.write_text("new\n", encoding="utf-8")

        result = emergency_commit(
            files=[str(f)],
            message="report file test",
            session_id="sess-report-001",
            project_root=str(isolated_repo),
            reason="verify report file",
            trigger_reconcilers=False,
        )
        assert result["ok"] is True

        reports_dir = isolated_repo / ".runtime" / "reconcile_reports"
        report_files = list(reports_dir.glob("emergency_commit_*.json"))
        assert len(report_files) >= 1, \
            f"expected >=1 report file, got: {report_files}"

        import json
        report = json.loads(report_files[-1].read_text(encoding="utf-8"))
        assert report["gate_id"] == "EMERGENCY-COMMIT"
        assert report["session_id"] == "sess-report-001"
        assert report["action"] == "emergency_commit"
        assert report["files_count"] == 1
        assert "report_test.py" in report["files"]


# ---------------------------------------------------------------------------
# 边界条件测试
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """emergency_commit 边界条件。"""

    def test_relative_path_input(self, isolated_repo):
        """支持相对路径输入（相对 project_root）。"""
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import emergency_commit
        f = _make_tracked_file(isolated_repo, "rel_path_test.py", "old\n")
        f.write_text("new\n", encoding="utf-8")

        # 用相对路径
        result = emergency_commit(
            files=["rel_path_test.py"],
            message="relative path test",
            session_id="sess-rel-001",
            project_root=str(isolated_repo),
            trigger_reconcilers=False,
        )
        assert result["ok"] is True, f"expected ok=True, got: {result}"

    def test_commit_hash_is_short_sha(self, isolated_repo):
        """commit_hash 应为短 SHA（10 位）。"""
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import emergency_commit
        f = _make_tracked_file(isolated_repo, "sha_test.py", "old\n")
        f.write_text("new\n", encoding="utf-8")

        result = emergency_commit(
            files=[str(f)],
            message="sha test",
            session_id="sess-sha-001",
            project_root=str(isolated_repo),
            trigger_reconcilers=False,
        )
        assert result["ok"] is True
        short_sha = result["commit_hash"]
        assert len(short_sha) == 10, \
            f"short SHA should be 10 chars, got {len(short_sha)}: {short_sha}"

        # 验证短 SHA 是真实 commit SHA 的前缀
        full_sha = _get_head_sha(isolated_repo)
        assert full_sha.startswith(short_sha), \
            f"full SHA {full_sha} should start with {short_sha}"

    def test_branch_field_in_result(self, isolated_repo):
        """结果应包含 branch 字段。"""
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import emergency_commit
        f = _make_tracked_file(isolated_repo, "branch_test.py", "old\n")
        f.write_text("new\n", encoding="utf-8")

        result = emergency_commit(
            files=[str(f)],
            message="branch test",
            session_id="sess-branch-001",
            project_root=str(isolated_repo),
            trigger_reconcilers=False,
        )
        assert result["ok"] is True
        assert result["branch"], "branch field should be non-empty"
        # 临时仓库默认在 master 或 main 分支
        assert result["branch"] in ("master", "main"), \
            f"unexpected branch: {result['branch']}"
