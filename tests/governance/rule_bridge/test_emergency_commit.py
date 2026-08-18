# [BLUEPRINT] MOD-GOV_TEST_EMERGENCY_COMMIT | tests/governance/rule_bridge/test_emergency_commit.py | §Ruling-100PCT-AI-GOVERNANCE-P2-1
# [MODULE] tests.governance.rule_bridge.test_emergency_commit
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.emergency_commit
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 临时 git 仓库隔离测试，不污染主仓库；每个测试独立 repo
# [MODIFY-GUARD] 测试函数名与 emergency_commit API 对齐
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败→pytest assert error
# [TESTS] self
# [A_module] module_id=MOD-GOV_TEST_EMERGENCY_COMMIT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
pytestmark = pytest.mark.silent_failure  # Ruling:100PCT-AI-GOVERNANCE P3-2


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


# ---------------------------------------------------------------------------
# P1-2 _agent_bucket_id 优先级链 smoke test
# （#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）
# ---------------------------------------------------------------------------


class TestAgentBucketId:
    """P1-2 治本：emergency_commit 计数按 agent_id 分桶（非 session_id）。

    治本原因：100% AI 开发下，AI 每次启动新 session_id，按 session_id 分桶
    计数永远停在 1，N>=3/N>=5 成本递增门禁永不触发。改为按 agent 持久标识分桶，
    使同一 AI 的多次 emergency_commit 累积计数。

    优先级链：
      1. ZEPHYR_AGENT_ID 环境变量（AI 显式声明）
      2. git config user.email（git 提交者标识）
      3. USER / USERNAME 环境变量（OS 用户）
      4. "default"（最终 fallback）
    """

    def test_env_zephyr_agent_id_takes_priority(self, isolated_repo, monkeypatch):
        """ZEPHYR_AGENT_ID 环境变量优先级最高。"""
        monkeypatch.setenv("ZEPHYR_AGENT_ID", "ai-glm-5.2-instance-1")
        # 即使有 git config user.email，也应优先用环境变量
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import _agent_bucket_id
        bucket = _agent_bucket_id(isolated_repo)
        assert bucket == "ai-glm-5.2-instance-1", (
            f"ZEPHYR_AGENT_ID 应优先，实际: {bucket}"
        )

    def test_git_config_email_fallback(self, isolated_repo, monkeypatch):
        """无 ZEPHYR_AGENT_ID 时，fallback 到 git config user.email。"""
        monkeypatch.delenv("ZEPHYR_AGENT_ID", raising=False)
        # isolated_repo fixture 设置了 user.email = test@zephyr.local
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import _agent_bucket_id
        bucket = _agent_bucket_id(isolated_repo)
        assert bucket == "email:test@zephyr.local", (
            f"应 fallback 到 git config user.email（前缀 email:），实际: {bucket}"
        )

    def test_user_env_fallback_when_git_fails(self, tmp_path, monkeypatch):
        """git config 失败（非 git 仓库）时，fallback 到 USER/USERNAME。"""
        monkeypatch.delenv("ZEPHYR_AGENT_ID", raising=False)
        # 用未 git init 的 tmp_path（无 user.email 配置）
        # 同时清空可能的 USER/USERNAME，先设置一个测试值
        monkeypatch.setenv("USER", "test-user-p1-2")
        # Windows 上 USERNAME 才是真正的环境变量
        monkeypatch.setenv("USERNAME", "test-user-p1-2")
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import _agent_bucket_id
        bucket = _agent_bucket_id(tmp_path)
        # 应为 user:test-user-p1-2（git config 失败 → fallback USER/USERNAME）
        assert bucket == "user:test-user-p1-2", (
            f"git 失败时应 fallback 到 USER/USERNAME，实际: {bucket}"
        )

    def test_default_fallback(self, tmp_path, monkeypatch):
        """所有标识都缺失时，fallback 到 "default"。"""
        monkeypatch.delenv("ZEPHYR_AGENT_ID", raising=False)
        monkeypatch.delenv("USER", raising=False)
        monkeypatch.delenv("USERNAME", raising=False)
        # tmp_path 不是 git 仓库，git config 会失败
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import _agent_bucket_id
        bucket = _agent_bucket_id(tmp_path)
        assert bucket == "default", (
            f"所有标识缺失时应 fallback 到 'default'，实际: {bucket}"
        )

    def test_bucket_id_stable_across_calls(self, isolated_repo, monkeypatch):
        """同一 agent 的多次调用应返回相同 bucket_id（持久性验证）。"""
        monkeypatch.setenv("ZEPHYR_AGENT_ID", "stable-agent-id-12345")
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import _agent_bucket_id
        b1 = _agent_bucket_id(isolated_repo)
        b2 = _agent_bucket_id(isolated_repo)
        b3 = _agent_bucket_id(isolated_repo)
        assert b1 == b2 == b3 == "stable-agent-id-12345", (
            "同一 agent 的 bucket_id 应跨调用稳定（持久性是 P1-2 治本核心）"
        )


# ---------------------------------------------------------------------------
# P1-2 emergency_count 分桶集成测试
# （#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）
# ---------------------------------------------------------------------------


class TestEmergencyCountBucketing:
    """P1-2 治本：emergency_count 按 agent bucket 累积（跨 session 持久）。

    验证 _read_emergency_count / _write_emergency_count / _increment_emergency_count
    均按 agent bucket_id 操作（而非 session_id）。
    """

    def test_count_file_path_uses_agent_bucket(self, isolated_repo, monkeypatch):
        """计数文件路径应为 .runtime/emergency_counts/{bucket_id}.json。"""
        monkeypatch.setenv("ZEPHYR_AGENT_ID", "test-bucket-path-agent")
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import (
            _agent_bucket_id,
            _emergency_count_path,
        )
        bucket = _agent_bucket_id(isolated_repo)
        path = _emergency_count_path(isolated_repo, bucket)
        assert path.name == "test-bucket-path-agent.json", (
            f"文件名应为 bucket_id.json，实际: {path.name}"
        )
        assert path.parent.name == "emergency_counts", (
            f"父目录应为 emergency_counts/（与 sessions/ 分离），实际: {path.parent.name}"
        )
        assert path.parent.parent.name == ".runtime"

    def test_count_persists_across_sessions(self, isolated_repo, monkeypatch):
        """同一 agent 的多次 emergency_commit 应累积计数（跨 session 持久）。

        场景：session-1 提交 1 次 → session-2 启动新 session_id → 提交第 2 次
        治本前（session_id 分桶）：session-2 看到计数 1（永远停在 1）
        治本后（agent_id 分桶）：session-2 看到计数 2（累积）
        """
        monkeypatch.setenv("ZEPHYR_AGENT_ID", "cross-session-agent-p1-2")
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import (
            _agent_bucket_id,
            _increment_emergency_count,
            _read_emergency_count,
        )
        bucket = _agent_bucket_id(isolated_repo)

        # session-1: increment 到 1
        n1 = _increment_emergency_count(isolated_repo, bucket)
        assert n1 == 1, f"第一次 increment 应返回 1，实际: {n1}"

        # 模拟 session-2 启动新 session_id（但 agent_id 不变）
        # 治本后：bucket_id 仍是同一个，计数累积
        bucket2 = _agent_bucket_id(isolated_repo)
        assert bucket == bucket2, "同一 agent 的 bucket_id 应稳定"

        # session-2: read 应看到 1（累积），increment 后变 2
        data = _read_emergency_count(isolated_repo, bucket)
        assert data["count"] == 1, (
            f"session-2 应看到 session-1 的计数（累积），实际: {data['count']}"
        )
        n2 = _increment_emergency_count(isolated_repo, bucket)
        assert n2 == 2, f"第二次 increment 应返回 2（累积），实际: {n2}"

    def test_different_agents_separate_buckets(self, isolated_repo, monkeypatch):
        """不同 agent 的计数应隔离（不同 bucket 文件）。"""
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import (
            _increment_emergency_count,
            _read_emergency_count,
        )

        # agent-A 提交 3 次
        for _ in range(3):
            _increment_emergency_count(isolated_repo, "agent-A-p1-2")
        # agent-B 提交 1 次
        _increment_emergency_count(isolated_repo, "agent-B-p1-2")

        # 验证隔离
        data_a = _read_emergency_count(isolated_repo, "agent-A-p1-2")
        data_b = _read_emergency_count(isolated_repo, "agent-B-p1-2")
        assert data_a["count"] == 3, f"agent-A 应有 3 次，实际: {data_a['count']}"
        assert data_b["count"] == 1, f"agent-B 应有 1 次，实际: {data_b['count']}"

    def test_escalation_blocks_at_threshold_five(self, isolated_repo, monkeypatch):
        """N>=5 时 _check_emergency_escalation 应阻断提交。"""
        monkeypatch.setenv("ZEPHYR_AGENT_ID", "escalation-test-agent-p1-2")
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import (
            _EMERGENCY_BLOCK_THRESHOLD,
            _agent_bucket_id,
            _check_emergency_escalation,
            _increment_emergency_count,
        )
        bucket = _agent_bucket_id(isolated_repo)
        assert _EMERGENCY_BLOCK_THRESHOLD == 5

        # increment 到 4 次（N=4，未达阈值）
        for _ in range(4):
            _increment_emergency_count(isolated_repo, bucket)
        # N=4 仍允许（reason 非空，因 N>=3 需 reason）
        allowed, _ = _check_emergency_escalation(isolated_repo, bucket, reason="test")
        assert allowed is True, "N=4 应允许（reason 非空）"

        # increment 到 5 次（N=5，达阈值）
        _increment_emergency_count(isolated_repo, bucket)
        # N=5 阻断
        allowed, err = _check_emergency_escalation(isolated_repo, bucket, reason="test")
        assert allowed is False, "N=5 应阻断"
        assert "5" in err and "阈值" in err, f"错误消息应含阈值信息: {err}"

    def test_escalation_requires_reason_at_threshold_three(self, isolated_repo, monkeypatch):
        """N>=3 且 reason 为空时 _check_emergency_escalation 应拒绝。"""
        monkeypatch.setenv("ZEPHYR_AGENT_ID", "reason-test-agent-p1-2")
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import (
            _EMERGENCY_REASON_THRESHOLD,
            _agent_bucket_id,
            _check_emergency_escalation,
            _increment_emergency_count,
        )
        bucket = _agent_bucket_id(isolated_repo)
        assert _EMERGENCY_REASON_THRESHOLD == 3

        # increment 到 3 次
        for _ in range(3):
            _increment_emergency_count(isolated_repo, bucket)
        # N=3 reason 为空 → 拒绝
        allowed, err = _check_emergency_escalation(isolated_repo, bucket, reason="")
        assert allowed is False, "N=3 且 reason 为空应拒绝"
        assert "3" in err and "reason" in err, f"错误消息应含 reason 要求: {err}"
        # N=3 reason 非空 → 允许
        allowed, _ = _check_emergency_escalation(isolated_repo, bucket, reason="P0 prod fix")
        assert allowed is True, "N=3 且 reason 非空应允许"


# ---------------------------------------------------------------------------
# P1-3 emergency_commit scenario 参数 smoke test
# （#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）
# ---------------------------------------------------------------------------


class TestEmergencyCommitScenario:
    """P1-3 治本：emergency_commit 支持 scenario 参数（dogfood/test/governance_fix 豁免）。

    commit message 应含 [SCENARIO:{scenario}] 标记，abuse_monitor 据此过滤——
    非 production 场景不计入 24h 滥用计数。
    """

    def test_default_scenario_is_production(self, isolated_repo):
        """默认 scenario=production（向后兼容）。"""
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import emergency_commit
        f = _make_tracked_file(isolated_repo, "scenario_default.py", "old\n")
        f.write_text("new\n", encoding="utf-8")
        result = emergency_commit(
            files=[str(f)],
            message="default scenario test",
            session_id="sess-scenario-default",
            project_root=str(isolated_repo),
            reason="test default scenario",
            trigger_reconcilers=False,
        )
        assert result["ok"] is True
        msg = _get_commit_message(isolated_repo)
        assert "[SCENARIO:production]" in msg, (
            f"默认应含 [SCENARIO:production] 标记，msg: {msg}"
        )

    def test_dogfood_scenario_marker(self, isolated_repo):
        """scenario=dogfood 时 commit message 含 [SCENARIO:dogfood]。"""
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import emergency_commit
        f = _make_tracked_file(isolated_repo, "scenario_dogfood.py", "old\n")
        f.write_text("new\n", encoding="utf-8")
        result = emergency_commit(
            files=[str(f)],
            message="dogfood scenario test",
            session_id="sess-scenario-dogfood",
            project_root=str(isolated_repo),
            reason="test dogfood scenario",
            trigger_reconcilers=False,
            scenario="dogfood",
        )
        assert result["ok"] is True
        msg = _get_commit_message(isolated_repo)
        assert "[SCENARIO:dogfood]" in msg, (
            f"应含 [SCENARIO:dogfood] 标记，msg: {msg}"
        )

    def test_governance_fix_scenario_marker(self, isolated_repo):
        """scenario=governance_fix 时 commit message 含 [SCENARIO:governance_fix]。"""
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import emergency_commit
        f = _make_tracked_file(isolated_repo, "scenario_govfix.py", "old\n")
        f.write_text("new\n", encoding="utf-8")
        result = emergency_commit(
            files=[str(f)],
            message="governance fix scenario test",
            session_id="sess-scenario-govfix",
            project_root=str(isolated_repo),
            reason="test governance_fix scenario",
            trigger_reconcilers=False,
            scenario="governance_fix",
        )
        assert result["ok"] is True
        msg = _get_commit_message(isolated_repo)
        assert "[SCENARIO:governance_fix]" in msg, (
            f"应含 [SCENARIO:governance_fix] 标记，msg: {msg}"
        )

    def test_scenario_marker_after_gw_marker(self, isolated_repo):
        """[SCENARIO:] 标记应在 [GW:...] 之后（abuse_monitor 解析顺序）。"""
        from zephyr.gov_enforcement.rule_bridge.emergency_commit import emergency_commit
        f = _make_tracked_file(isolated_repo, "scenario_order.py", "old\n")
        f.write_text("new\n", encoding="utf-8")
        result = emergency_commit(
            files=[str(f)],
            message="order test",
            session_id="sess-scenario-order",
            project_root=str(isolated_repo),
            reason="verify marker order",
            trigger_reconcilers=False,
            scenario="test",
        )
        assert result["ok"] is True
        msg = _get_commit_message(isolated_repo)
        # [GW:] 必须在 [SCENARIO:] 之前（abuse_monitor 先匹配 [GW:emergency]，再解析 scenario）
        gw_pos = msg.find("[GW:")
        scenario_pos = msg.find("[SCENARIO:")
        assert gw_pos >= 0 and scenario_pos >= 0, (
            f"两个标记都应存在，msg: {msg}"
        )
        assert gw_pos < scenario_pos, (
            f"[GW:] 应在 [SCENARIO:] 之前（gw_pos={gw_pos}, scenario_pos={scenario_pos}）"
        )
