# [A_test] module_id: SRC-TST-2218 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_RECONCILIATION_REGISTRY | docs/03_modules/_domain_governance/audit/blueprint.md | §
# [MODULE] tests.governance.audit.test_blueprint_frontmatter_reconciler_post_commit
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_RECONCILIATION_REGISTRY | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_blueprint_frontmatter_reconciler_post_commit.py — post-commit reconciler 单测

ARCH-FRONTMATTER-STATE-001 Phase 2 (Link B fix)。

测试 make_blueprint_frontmatter_reconciler 工厂函数：
- trigger 逻辑：.py 触发、docs/03_modules/*.md 触发、其他 .md 不触发、.yaml 不触发
- factory 返回正确 ReconcilerSpec（gate_id, priority, callables）
- reconcile 处理 subprocess 失败（返回 warn）
- reconcile 处理成功且无 .md 变更（返回 clean）
- reconcile 处理成功且有 .md 变更（返回 auto_committed）

与 tests/governance/test_blueprint_frontmatter_reconciler.py 的区别：
  那个测试 underlying syncer 函数 reconcile_blueprint_frontmatter（scripts/ 下）；
  本测试 post-commit reconciler factory make_blueprint_frontmatter_reconciler
  （reconciliation_registry.py 中的 ReconcilerSpec 工厂）。

测试隔离：用 mock 模拟 subprocess/git 操作，不触碰生产库或真实 git 仓库。
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.audit.reconciliation_registry import (  # noqa: E402
    ReconcileResult,
    make_blueprint_frontmatter_reconciler,
)


# ---------------------------------------------------------------------------
# 辅助：FakeGateway
# ---------------------------------------------------------------------------
class _FakeGateway:
    """模拟 GitCommitGateway，仅提供 project_root / _run_git / _commit_auto。"""

    def __init__(self, project_root: Path, diff_files: list[str] | None = None,
                 commit_status: str = "OK"):
        self.project_root = project_root
        self._diff_files = diff_files or []
        self._commit_status = commit_status
        self._commit_calls: list[tuple] = []

    def run_git(self, cmd: list[str]):
        """模拟 git diff --name-only -- docs/03_modules/。"""
        mock = MagicMock()
        mock.returncode = 0
        mock.stderr = ""
        if "diff" in cmd and "--name-only" in cmd:
            mock.stdout = "\n".join(self._diff_files)
        else:
            mock.stdout = ""
        return mock

    def _run_git(self, cmd: list[str]):
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.run_git(cmd)

    def _commit_auto(self, session_id: str, files: list[str], msg: str):
        """模拟 _commit_auto 返回。"""
        self._commit_calls.append((session_id, files, msg))
        result = MagicMock()
        result.status = self._commit_status
        result.message = "mock commit"
        return result


# ---------------------------------------------------------------------------
# 辅助：mock subprocess result
# ---------------------------------------------------------------------------
def _make_subprocess_result(returncode: int = 0, stdout: str = "", stderr: str = ""):
    """构造模拟的 subprocess.CompletedProcess。"""
    mock = MagicMock()
    mock.returncode = returncode
    mock.stdout = stdout
    mock.stderr = stderr
    return mock


# ---------------------------------------------------------------------------
# 测试：factory 返回 ReconcilerSpec
# ---------------------------------------------------------------------------
class TestFactorySpec:
    """make_blueprint_frontmatter_reconciler 工厂返回值测试。"""

    def test_returns_reconciler_spec_with_correct_gate_id(self, tmp_path):
        """工厂应返回 gate_id='GATE-BLUEPRINT-FRONTMATTER-SYNC'。"""
        gw = _FakeGateway(tmp_path)
        spec = make_blueprint_frontmatter_reconciler(gw)
        assert spec.gate_id == "GATE-BLUEPRINT-FRONTMATTER-SYNC"

    def test_returns_reconciler_spec_with_priority_135(self, tmp_path):
        """priority 应为 135（在 depgraph_ops@130 和 drift_scan@140 之间）。"""
        gw = _FakeGateway(tmp_path)
        spec = make_blueprint_frontmatter_reconciler(gw)
        assert spec.priority == 135

    def test_trigger_and_reconcile_are_callables(self, tmp_path):
        """trigger 和 reconcile 应为可调用对象。"""
        gw = _FakeGateway(tmp_path)
        spec = make_blueprint_frontmatter_reconciler(gw)
        assert callable(spec.trigger)
        assert callable(spec.reconcile)


# ---------------------------------------------------------------------------
# 测试：trigger 逻辑
# ---------------------------------------------------------------------------
class TestTrigger:
    """trigger 函数逻辑测试。"""

    def test_py_file_triggers(self, tmp_path):
        """.py 文件应触发。"""
        gw = _FakeGateway(tmp_path)
        spec = make_blueprint_frontmatter_reconciler(gw)
        files = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        assert spec.trigger(files) is True

    def test_docs_03_modules_md_triggers(self, tmp_path):
        """docs/03_modules/ 下的 .md 文件应触发。"""
        gw = _FakeGateway(tmp_path)
        spec = make_blueprint_frontmatter_reconciler(gw)
        files = [str(tmp_path / "docs" / "03_modules" / "m1" / "blueprint.md")]
        assert spec.trigger(files) is True

    def test_other_md_does_not_trigger(self, tmp_path):
        """非 docs/03_modules/ 下的 .md 文件不应触发。"""
        gw = _FakeGateway(tmp_path)
        spec = make_blueprint_frontmatter_reconciler(gw)
        files = [str(tmp_path / "docs" / "01_policies" / "rule.md")]
        assert spec.trigger(files) is False

    def test_yaml_does_not_trigger(self, tmp_path):
        """.yaml 文件不应触发。"""
        gw = _FakeGateway(tmp_path)
        spec = make_blueprint_frontmatter_reconciler(gw)
        files = [str(tmp_path / "rules" / "trae_001.yaml")]
        assert spec.trigger(files) is False

    def test_empty_files_does_not_trigger(self, tmp_path):
        """空文件列表不应触发。"""
        gw = _FakeGateway(tmp_path)
        spec = make_blueprint_frontmatter_reconciler(gw)
        assert spec.trigger([]) is False

    def test_mixed_files_triggers(self, tmp_path):
        """混合文件中只要有一个 .py 就应触发。"""
        gw = _FakeGateway(tmp_path)
        spec = make_blueprint_frontmatter_reconciler(gw)
        files = [
            str(tmp_path / "rules" / "trae_001.yaml"),
            str(tmp_path / "docs" / "01_policies" / "rule.md"),
            str(tmp_path / "src" / "zephyr" / "foo.py"),
        ]
        assert spec.trigger(files) is True


# ---------------------------------------------------------------------------
# 测试：reconcile 行为
# ---------------------------------------------------------------------------
class TestReconcile:
    """reconcile 函数行为测试（用 mock 模拟 subprocess/git）。"""

    @patch("zephyr.governance.audit.reconciliation_registry._run_subprocess")
    def test_subprocess_failure_returns_warn(self, mock_sub, tmp_path):
        """subprocess 失败时应返回 warn。"""
        mock_sub.return_value = _make_subprocess_result(
            returncode=1, stderr="connection error"
        )
        gw = _FakeGateway(tmp_path)
        spec = make_blueprint_frontmatter_reconciler(gw)
        result = spec.reconcile(["foo.py"], "sess-test")
        assert result.action == "warn"
        assert "frontmatter sync failed" in result.detail
        assert "rc=1" in result.detail

    @patch("zephyr.governance.audit.reconciliation_registry._run_subprocess")
    def test_no_md_changes_returns_clean(self, mock_sub, tmp_path):
        """subprocess 成功但无 .md 变更时应返回 clean。"""
        mock_sub.return_value = _make_subprocess_result(returncode=0, stdout="OK")
        gw = _FakeGateway(tmp_path, diff_files=[])  # 无 .md 变更
        spec = make_blueprint_frontmatter_reconciler(gw)
        result = spec.reconcile(["foo.py"], "sess-test")
        assert result.action == "clean"
        assert "no drift" in result.detail

    @patch("zephyr.governance.audit.reconciliation_registry._run_subprocess")
    def test_md_changes_with_commit_ok_returns_auto_committed(self, mock_sub, tmp_path):
        """subprocess 成功且有 .md 变更、commit 成功时应返回 auto_committed。"""
        mock_sub.return_value = _make_subprocess_result(returncode=0, stdout="OK")
        gw = _FakeGateway(
            tmp_path,
            diff_files=["docs/03_modules/m1/blueprint.md", "docs/03_modules/m2/blueprint.md"],
            commit_status="OK",
        )
        spec = make_blueprint_frontmatter_reconciler(gw)
        result = spec.reconcile(["foo.py"], "sess-test")
        assert result.action == "auto_committed"
        assert "2 files auto-reconciled" in result.detail
        # 验证 _commit_auto 被调用
        assert len(gw._commit_calls) == 1
        session_id, files, msg = gw._commit_calls[0]
        assert session_id == "sess-test"
        assert len(files) == 2
        assert "GATE-BLUEPRINT-FRONTMATTER-SYNC" in msg

    @patch("zephyr.governance.audit.reconciliation_registry._run_subprocess")
    def test_md_changes_with_nothing_to_commit_returns_clean(self, mock_sub, tmp_path):
        """subprocess 成功且有 .md 变更但 commit 返回 NOTHING_TO_COMMIT 时返回 clean。"""
        mock_sub.return_value = _make_subprocess_result(returncode=0, stdout="OK")
        gw = _FakeGateway(
            tmp_path,
            diff_files=["docs/03_modules/m1/blueprint.md"],
            commit_status="NOTHING_TO_COMMIT",
        )
        spec = make_blueprint_frontmatter_reconciler(gw)
        result = spec.reconcile(["foo.py"], "sess-test")
        assert result.action == "clean"
        assert "no staged changes" in result.detail

    @patch("zephyr.governance.audit.reconciliation_registry._run_subprocess")
    def test_md_changes_with_commit_failure_returns_warn(self, mock_sub, tmp_path):
        """subprocess 成功且有 .md 变更但 commit 失败时返回 warn。"""
        mock_sub.return_value = _make_subprocess_result(returncode=0, stdout="OK")
        gw = _FakeGateway(
            tmp_path,
            diff_files=["docs/03_modules/m1/blueprint.md"],
            commit_status="COMMIT_FAILED",
        )
        spec = make_blueprint_frontmatter_reconciler(gw)
        result = spec.reconcile(["foo.py"], "sess-test")
        assert result.action == "warn"
        assert "auto-commit failed" in result.detail
        assert "COMMIT_FAILED" in result.detail

    @patch("zephyr.governance.audit.reconciliation_registry._run_subprocess")
    def test_non_md_diff_files_ignored(self, mock_sub, tmp_path):
        """git diff 返回非 .md 文件时不应触发 commit（只关心 frontmatter .md）。"""
        mock_sub.return_value = _make_subprocess_result(returncode=0, stdout="OK")
        gw = _FakeGateway(
            tmp_path,
            diff_files=["docs/03_modules/m1/data.json", "docs/03_modules/m1/style.css"],
        )
        spec = make_blueprint_frontmatter_reconciler(gw)
        result = spec.reconcile(["foo.py"], "sess-test")
        assert result.action == "clean"
        assert "no drift" in result.detail
        assert len(gw._commit_calls) == 0

    @patch("zephyr.governance.audit.reconciliation_registry._run_subprocess")
    def test_git_diff_failure_returns_warn(self, mock_sub, tmp_path):
        """git diff 命令失败时应返回 warn。"""
        mock_sub.return_value = _make_subprocess_result(returncode=0, stdout="OK")
        gw = _FakeGateway(tmp_path)
        # 覆盖 _run_git 让 diff 返回失败
        def failing_git(cmd):
            mock = MagicMock()
            mock.returncode = 1
            mock.stderr = "git error"
            mock.stdout = ""
            return mock
        gw.run_git = failing_git
        spec = make_blueprint_frontmatter_reconciler(gw)
        result = spec.reconcile(["foo.py"], "sess-test")
        assert result.action == "warn"
        assert "git diff failed" in result.detail
