# [A_test] module_id: SRC-TST-POST_DOC_REVIEW | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §16
# [MODULE] tests.test_post_doc_review
# [INVARIANTS] 无
# [MODIFY-GUARD] post_doc_review_check.py
# [CONSUMERS] CI/CD
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无
# [TESTS] tests/test_post_doc_review.py
# [TTL] task_bound

import json
import subprocess
from pathlib import Path

import pytest

from zephyr.gov_enforcement.rule_enforcement.invariants.post_doc_review_check import (
    DocReviewReport,
    GitUnavailableError,
    PostDocReviewScanner,
    TamperingError,
)


def _init_git_repo(tmp_path: Path) -> str:
    """在 tmp_path 初始化 git 仓库并返回初始 commit hash。"""
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(tmp_path),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(tmp_path),
        capture_output=True,
        check=True,
    )
    (tmp_path / "README.md").write_text("init", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=str(tmp_path), capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init", "--no-verify"],
        cwd=str(tmp_path),
        capture_output=True,
        check=True,
    )
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _setup_session_with_git(
    tmp_path: Path,
    session_id: str,
    files_content: dict[str, str],
    start_commit: str,
    self_reported_files: list[str] | None = None,
) -> Path:
    """创建带 git 基线的 session 环境。

    Args:
        self_reported_files: modified_files.json 中的自报告列表。
            None=不创建 modified_files.json（模拟篡改）
    """
    session_dir = tmp_path / "session_logs" / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "session_start_commit.txt").write_text(start_commit, encoding="utf-8")

    for rel_path, content in files_content.items():
        fpath = tmp_path / rel_path
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(content, encoding="utf-8")

    if self_reported_files is not None:
        (session_dir / "modified_files.json").write_text(json.dumps(self_reported_files), encoding="utf-8")
    return session_dir


class TestPostDocReviewScanner:
    """PostDocReviewScanner 单元测试。"""

    def test_import_success(self):
        assert PostDocReviewScanner is not None
        assert DocReviewReport is not None
        assert GitUnavailableError is not None
        assert TamperingError is not None

    def test_git_unavailable_raises_red(self, tmp_path):
        """R1 防御：git 不可用（无 session_start_commit.txt）→ RED。"""
        scanner = PostDocReviewScanner(project_root=tmp_path, session_id="test-session")
        report = scanner.scan()
        assert report.git_unavailable is True
        assert report.is_clean is False
        assert report.tampering_detected is True

    def test_clean_doc_no_findings(self, tmp_path):
        """无问题的文档不产生 finding。"""
        start_commit = _init_git_repo(tmp_path)
        _setup_session_with_git(
            tmp_path,
            "test-session",
            {"docs/clean.md": "# Clean Doc\n\n结果陈述。\n"},
            start_commit,
            self_reported_files=["docs/clean.md"],
        )
        scanner = PostDocReviewScanner(project_root=tmp_path, session_id="test-session")
        report = scanner.scan()
        assert report.git_authoritative is True
        assert report.tampering_detected is False
        assert len(report.reviewed_files) == 1

    def test_cultural_benchmark_detected(self, tmp_path):
        start_commit = _init_git_repo(tmp_path)
        _setup_session_with_git(
            tmp_path,
            "test-session",
            {"docs/noise.md": "# Noise\n\n对标 K8s ResourceQuota。\n"},
            start_commit,
            self_reported_files=["docs/noise.md"],
        )
        scanner = PostDocReviewScanner(project_root=tmp_path, session_id="test-session")
        report = scanner.scan()
        assert report.is_clean is False
        assert len(report.pending_regularization) >= 1
        assert report.pending_regularization[0].issue_type == "noise"

    def test_process_statement_detected(self, tmp_path):
        start_commit = _init_git_repo(tmp_path)
        _setup_session_with_git(
            tmp_path,
            "test-session",
            {"docs/process.md": "# Process\n\n之前是X现在改为Y。\n"},
            start_commit,
            self_reported_files=["docs/process.md"],
        )
        scanner = PostDocReviewScanner(project_root=tmp_path, session_id="test-session")
        report = scanner.scan()
        assert report.is_clean is False
        assert report.pending_regularization[0].issue_type == "process_statement"

    def test_negative_statement_detected(self, tmp_path):
        start_commit = _init_git_repo(tmp_path)
        _setup_session_with_git(
            tmp_path,
            "test-session",
            {"docs/negative.md": "# Negative\n\n此规则已废止。\n"},
            start_commit,
            self_reported_files=["docs/negative.md"],
        )
        scanner = PostDocReviewScanner(project_root=tmp_path, session_id="test-session")
        report = scanner.scan()
        assert report.is_clean is False
        assert report.pending_regularization[0].issue_type == "negative_statement"

    def test_regularization_triggered_when_threshold_met(self, tmp_path):
        start_commit = _init_git_repo(tmp_path)
        _setup_session_with_git(
            tmp_path,
            "test-session",
            {"docs/multi.md": "# Multi\n\n对标 K8s。\n此规则已废止。\n之前是X现在改为Y。\n"},
            start_commit,
            self_reported_files=["docs/multi.md"],
        )
        scanner = PostDocReviewScanner(project_root=tmp_path, session_id="test-session")
        report = scanner.scan()
        assert len(report.pending_regularization) >= 3
        assert report.regularization_triggered is True

    def test_regularization_not_triggered_below_threshold(self, tmp_path):
        start_commit = _init_git_repo(tmp_path)
        _setup_session_with_git(
            tmp_path,
            "test-session",
            {"docs/single.md": "# Single\n\n对标 K8s。\n"},
            start_commit,
            self_reported_files=["docs/single.md"],
        )
        scanner = PostDocReviewScanner(project_root=tmp_path, session_id="test-session")
        report = scanner.scan()
        assert len(report.pending_regularization) == 1
        assert report.regularization_triggered is False

    def test_save_report_creates_json(self, tmp_path):
        start_commit = _init_git_repo(tmp_path)
        _setup_session_with_git(
            tmp_path,
            "test-session",
            {"docs/noise.md": "对标 K8s。\n"},
            start_commit,
            self_reported_files=["docs/noise.md"],
        )
        scanner = PostDocReviewScanner(project_root=tmp_path, session_id="test-session")
        report = scanner.scan()
        out_path = scanner.save_report(report)
        assert out_path.exists()
        saved = json.loads(out_path.read_text(encoding="utf-8"))
        assert saved["git_authoritative"] is True
        assert saved["tampering_detected"] is False

    def test_yaml_file_scanned(self, tmp_path):
        start_commit = _init_git_repo(tmp_path)
        _setup_session_with_git(
            tmp_path,
            "test-session",
            {"config/test.yaml": "description: 对标 ITIL\n"},
            start_commit,
            self_reported_files=["config/test.yaml"],
        )
        scanner = PostDocReviewScanner(project_root=tmp_path, session_id="test-session")
        report = scanner.scan()
        assert report.is_clean is False
        assert "config/test.yaml" in report.reviewed_files


class TestR1TamperingDefense:
    """R1 防御：篡改检测测试。"""

    def test_tampering_deleted_modified_files_json(self, tmp_path):
        """R1 攻击：删除 modified_files.json → 篡改告警。"""
        start_commit = _init_git_repo(tmp_path)
        _setup_session_with_git(
            tmp_path,
            "attacker",
            {"docs/attack.md": "对标 K8s。\n"},
            start_commit,
            self_reported_files=None,
        )
        scanner = PostDocReviewScanner(project_root=tmp_path, session_id="attacker")
        report = scanner.scan()
        assert report.tampering_detected is True
        assert report.is_clean is False
        assert any("篡改" in d for d in report.tampering_details)

    def test_tampering_incomplete_modified_files_json(self, tmp_path):
        """R1 攻击：删除部分文件记录 → 篡改告警。"""
        start_commit = _init_git_repo(tmp_path)
        _setup_session_with_git(
            tmp_path,
            "attacker",
            {"docs/file1.md": "对标 K8s。\n", "docs/file2.md": "此规则已废止。\n"},
            start_commit,
            self_reported_files=["docs/file1.md"],
        )
        scanner = PostDocReviewScanner(project_root=tmp_path, session_id="attacker")
        report = scanner.scan()
        assert report.tampering_detected is True
        assert any("file2.md" in d for d in report.tampering_details)

    def test_tampering_fabricated_report(self, tmp_path):
        """R1 攻击：虚报不存在的文件 → 篡改告警。"""
        start_commit = _init_git_repo(tmp_path)
        _setup_session_with_git(
            tmp_path,
            "attacker",
            {"docs/real.md": "对标 K8s。\n"},
            start_commit,
            self_reported_files=["docs/real.md", "docs/fake.md"],
        )
        scanner = PostDocReviewScanner(project_root=tmp_path, session_id="attacker")
        report = scanner.scan()
        assert report.tampering_detected is True
        assert any("fake.md" in d and "虚报告" in d for d in report.tampering_details)

    def test_no_tampering_when_lists_match(self, tmp_path):
        """R1 正常：自报告与 git 一致 → 无告警。"""
        start_commit = _init_git_repo(tmp_path)
        _setup_session_with_git(
            tmp_path,
            "normal",
            {"docs/clean.md": "# Clean\n\n结果陈述。\n"},
            start_commit,
            self_reported_files=["docs/clean.md"],
        )
        scanner = PostDocReviewScanner(project_root=tmp_path, session_id="normal")
        report = scanner.scan()
        assert report.tampering_detected is False
        assert report.git_authoritative is True

    def test_git_unavailable_no_degradation(self, tmp_path):
        """R1 防御：git 不可用不降级 → RED。"""
        session_dir = tmp_path / "session_logs" / "no-git"
        session_dir.mkdir(parents=True)
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "test.md").write_text("对标 K8s。\n", encoding="utf-8")
        (session_dir / "modified_files.json").write_text(json.dumps(["docs/test.md"]), encoding="utf-8")
        scanner = PostDocReviewScanner(project_root=tmp_path, session_id="no-git")
        report = scanner.scan()
        assert report.git_unavailable is True
        assert report.is_clean is False
        assert report.tampering_detected is True

    def test_commit_hash_injection_blocked(self, tmp_path):
        """R1 防御：commit hash 注入被校验拦截。"""
        _init_git_repo(tmp_path)
        session_dir = tmp_path / "session_logs" / "inject"
        session_dir.mkdir(parents=True)
        (session_dir / "session_start_commit.txt").write_text(
            "abc; rm -rf /; def0000000000000000000000000000000000000",
            encoding="utf-8",
        )
        scanner = PostDocReviewScanner(project_root=tmp_path, session_id="inject")
        report = scanner.scan()
        assert report.git_unavailable is True
        assert report.is_clean is False
