# [A_test] module_id: SRC-TST-2028 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-643 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_commit_gateway_audit_reconciler
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_commit_gateway_audit_reconciler.py — GATE-INTEGRITY-AUDIT reconciler 单测（AD-GOV-001 合并后）

权威依据：make_integrity_audit_reconciler（reconciliation_registry.py）
AD-GOV-001 合并：旧 GATE-RULES-INTEGRITY + GATE-COMMIT-GW-AUDIT → GATE-INTEGRITY-AUDIT

测试组：
- TestTrigger: trigger always True（两个旧 trigger 均 always True，OR 仍 always True）
- TestSpecProperties: gate_id=GATE-INTEGRITY-AUDIT, priority=800
- TestReconcileBehavior: 合并后 reconcile 串联执行，action 取较严重

测试隔离: 所有测试用 tmp_path 临时 git 仓库，不污染生产库。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.git_commit_gateway import GitCommitGateway  # noqa: E402
from zephyr.governance.reconciliation_registry import (  # noqa: E402
    make_integrity_audit_reconciler,
    _make_old_commit_gateway_audit_reconciler,
)


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------
def _init_git_repo(repo_dir: Path) -> None:
    """在 tmp_path 初始化一个 git 仓库（含初始 commit）。"""
    repo_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@test.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@test.com"
    subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=str(repo_dir), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=str(repo_dir), capture_output=True, check=True)
    # 初始 commit
    (repo_dir / ".gitignore").write_text("*.tmp\n.runtime/\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitignore"], cwd=str(repo_dir), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "init [GW:setup]", "--no-verify"], cwd=str(repo_dir), capture_output=True, check=True)


def _make_commit(repo_dir: Path, message: str) -> None:
    """创建一个新 commit（修改 .gitignore 触发变更）。"""
    gitignore = repo_dir / ".gitignore"
    content = gitignore.read_text(encoding="utf-8")
    gitignore.write_text(content + f"# {message}\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitignore"], cwd=str(repo_dir), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", message, "--no-verify"], cwd=str(repo_dir), capture_output=True, check=True)


# ---------------------------------------------------------------------------
# TestTrigger
# ---------------------------------------------------------------------------
class TestTrigger:
    """trigger always True——绕过可能涉及任何文件，无法用文件前缀限定。"""

    def test_trigger_empty_files(self, tmp_path):
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        spec = make_integrity_audit_reconciler(gw)
        assert spec.trigger([]) is True

    def test_trigger_any_files(self, tmp_path):
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        spec = make_integrity_audit_reconciler(gw)
        assert spec.trigger(["src/foo.py", "docs/bar.md"]) is True


# ---------------------------------------------------------------------------
# TestReconcileClean
# ---------------------------------------------------------------------------
class TestReconcileClean:
    """全部 commit 含 [GW: 标记 → action=clean（测试旧 commit_gateway_audit 逻辑）。"""

    def test_all_gw_commits_clean(self, tmp_path):
        _init_git_repo(tmp_path)
        _make_commit(tmp_path, "feat: add a [GW:sess-001]")
        _make_commit(tmp_path, "feat: add b [GW:sess-002:auto]")
        gw = GitCommitGateway(project_root=tmp_path)
        spec = _make_old_commit_gateway_audit_reconciler(gw)
        result = spec.reconcile([], "sess-test")
        assert result.action == "clean"
        assert "audit clean" in result.detail


# ---------------------------------------------------------------------------
# TestReconcileViolations
# ---------------------------------------------------------------------------
class TestReconcileViolations:
    """存在无 [GW: 标记的裸 commit → action=warn。"""

    def test_bare_commit_detected(self, tmp_path):
        _init_git_repo(tmp_path)
        _make_commit(tmp_path, "feat: gateway commit [GW:sess-001]")
        _make_commit(tmp_path, "feat: bare commit no marker")  # 裸 commit
        gw = GitCommitGateway(project_root=tmp_path)
        spec = _make_old_commit_gateway_audit_reconciler(gw)
        result = spec.reconcile([], "sess-test")
        assert result.action == "warn"
        assert "1 non-GW" in result.detail

    def test_multiple_bare_commits_detected(self, tmp_path):
        _init_git_repo(tmp_path)
        _make_commit(tmp_path, "bare one")
        _make_commit(tmp_path, "feat: ok [GW:s1]")
        _make_commit(tmp_path, "bare two")
        _make_commit(tmp_path, "bare three")
        gw = GitCommitGateway(project_root=tmp_path)
        spec = _make_old_commit_gateway_audit_reconciler(gw)
        result = spec.reconcile([], "sess-test")
        assert result.action == "warn"
        assert "3 non-GW" in result.detail


# ---------------------------------------------------------------------------
# TestMergeSkip
# ---------------------------------------------------------------------------
class TestMergeSkip:
    """merge commit 跳过（合并提交无作者意图，不误报）。"""

    def test_merge_commit_not_flagged(self, tmp_path):
        _init_git_repo(tmp_path)
        # 创建分支并合并
        _make_commit(tmp_path, "feat: on main [GW:s1]")
        # 检测默认分支名（master 或 main）
        branch_r = subprocess.run(["git", "branch"], cwd=str(tmp_path), capture_output=True, text=True)
        main_branch = "master" if "master" in branch_r.stdout else "main"
        subprocess.run(["git", "checkout", "-b", "feature"], cwd=str(tmp_path), capture_output=True, check=True)
        _make_commit(tmp_path, "feat: on branch [GW:s2]")
        subprocess.run(["git", "checkout", main_branch], cwd=str(tmp_path), capture_output=True, check=True)
        subprocess.run(
            ["git", "merge", "--no-ff", "feature", "-m", "Merge branch 'feature' [GW:merge]"],
            cwd=str(tmp_path), capture_output=True, check=True,
        )
        # 现在 git log 含一个 Merge commit（含 [GW: 标记，不会误报）
        gw = GitCommitGateway(project_root=tmp_path)
        spec = _make_old_commit_gateway_audit_reconciler(gw)
        result = spec.reconcile([], "sess-test")
        # 所有 commit 都有 [GW: 标记（含 merge），应该 clean
        assert result.action == "clean"

    def test_merge_without_marker_not_flagged(self, tmp_path):
        """merge commit 即使无 [GW: 标记也不误报（跳过 merge）。"""
        _init_git_repo(tmp_path)
        _make_commit(tmp_path, "feat: ok [GW:s1]")
        # 检测默认分支名（master 或 main）
        branch_r = subprocess.run(["git", "branch"], cwd=str(tmp_path), capture_output=True, text=True)
        main_branch = "master" if "master" in branch_r.stdout else "main"
        subprocess.run(["git", "checkout", "-b", "feature"], cwd=str(tmp_path), capture_output=True, check=True)
        _make_commit(tmp_path, "feat: on branch [GW:s2]")
        subprocess.run(["git", "checkout", main_branch], cwd=str(tmp_path), capture_output=True, check=True)
        subprocess.run(
            ["git", "merge", "--no-ff", "feature", "-m", "Merge branch 'feature'"],  # 无 [GW: 标记
            cwd=str(tmp_path), capture_output=True, check=True,
        )
        gw = GitCommitGateway(project_root=tmp_path)
        spec = _make_old_commit_gateway_audit_reconciler(gw)
        result = spec.reconcile([], "sess-test")
        # merge commit 被跳过，其他 commit 都有 [GW: 标记 → clean
        assert result.action == "clean"


# ---------------------------------------------------------------------------
# TestReportWritten
# ---------------------------------------------------------------------------
class TestReportWritten:
    """报告落盘 .runtime/reconcile_reports/commit_gateway_audit_<ts>.json。"""

    def test_report_file_created(self, tmp_path):
        _init_git_repo(tmp_path)
        _make_commit(tmp_path, "bare commit")
        gw = GitCommitGateway(project_root=tmp_path)
        spec = _make_old_commit_gateway_audit_reconciler(gw)
        result = spec.reconcile([], "sess-test")
        # 报告目录存在
        reports_dir = tmp_path / ".runtime" / "reconcile_reports"
        assert reports_dir.exists()
        # 找到 commit_gateway_audit 报告
        reports = list(reports_dir.glob("commit_gateway_audit_*.json"))
        assert len(reports) >= 1
        # 报告内容正确
        report = json.loads(reports[0].read_text(encoding="utf-8"))
        assert report["gate_id"] == "GATE-COMMIT-GW-AUDIT"
        assert report["session_id"] == "sess-test"
        assert report["violations_count"] >= 1
        assert "timestamp" in report

    def test_report_contains_violation_details(self, tmp_path):
        _init_git_repo(tmp_path)
        _make_commit(tmp_path, "feat: bare commit detail test")
        gw = GitCommitGateway(project_root=tmp_path)
        spec = _make_old_commit_gateway_audit_reconciler(gw)
        result = spec.reconcile([], "sess-test")
        reports_dir = tmp_path / ".runtime" / "reconcile_reports"
        reports = list(reports_dir.glob("commit_gateway_audit_*.json"))
        report = json.loads(reports[0].read_text(encoding="utf-8"))
        assert len(report["violations"]) >= 1
        v = report["violations"][0]
        assert "hash" in v
        assert "subject" in v
        assert "[GW:" not in v["subject"]


# ---------------------------------------------------------------------------
# TestSpecProperties
# ---------------------------------------------------------------------------
class TestSpecProperties:
    """reconciler spec 属性正确。"""

    def test_gate_id(self, tmp_path):
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        spec = make_integrity_audit_reconciler(gw)
        assert spec.gate_id == "GATE-INTEGRITY-AUDIT"

    def test_priority_is_last(self, tmp_path):
        """priority=800 最后执行（审计非阻断，低优先级）。"""
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        spec = make_integrity_audit_reconciler(gw)
        assert spec.priority == 800
