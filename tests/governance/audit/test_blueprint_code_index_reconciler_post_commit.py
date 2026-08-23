# [A_test] module_id: SRC-TST-CODEIDX | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_RECONCILIATION_REGISTRY | docs/03_modules/_domain_governance/audit/blueprint.md | §
# [MODULE] tests.governance.audit.test_blueprint_code_index_reconciler_post_commit
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_RECONCILIATION_REGISTRY | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_blueprint_code_index_reconciler_post_commit.py — GATE-BLUEPRINT-CODE-INDEX-SYNC 单测

autogen 段 auto-commit 通道（2026-08-23 批3b，仿 135 模板）。

测试 make_blueprint_code_index_reconciler 工厂函数：
- factory 返回正确 ReconcilerSpec（gate_id / priority=136 / callables）
- trigger 逻辑：.py 触发、docs/03_modules/*.md 触发、其他 .md/.yaml/空表不触发
- reconcile：subprocess 失败 warn、无漂移 clean、有漂移 auto_committed、
  NOTHING_TO_COMMIT clean、commit 失败 warn、非 .md diff 忽略、git diff 失败 warn
- cooldown：窗口内二次调用 skip；marker 损坏 fail-open 继续执行

与 test_blueprint_frontmatter_reconciler_post_commit.py 同型（135 模板测试 SSoT）。
测试隔离：mock subprocess/git，project_root=tmp_path（cooldown marker 落 tmp 隔离）。
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
    make_blueprint_code_index_reconciler,
)


# ---------------------------------------------------------------------------
# 辅助：FakeGateway（与 135 模板测试同款契约：project_root / run_git / _commit_auto）
# ---------------------------------------------------------------------------
class _FakeGateway:
    """模拟 GitCommitGateway，仅提供 project_root / run_git / _commit_auto。"""

    def __init__(self, project_root: Path, diff_files: list[str] | None = None, commit_status: str = "OK"):
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

    def _commit_auto(self, session_id: str, files: list[str], msg: str):
        """模拟 _commit_auto 返回。"""
        self._commit_calls.append((session_id, files, msg))
        result = MagicMock()
        result.status = self._commit_status
        result.message = "mock commit"
        return result


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
    """make_blueprint_code_index_reconciler 工厂返回值测试。"""

    def test_returns_reconciler_spec_with_correct_gate_id(self, tmp_path):
        """工厂应返回 gate_id='GATE-BLUEPRINT-CODE-INDEX-SYNC'。"""
        gw = _FakeGateway(tmp_path)
        spec = make_blueprint_code_index_reconciler(gw)
        assert spec.gate_id == "GATE-BLUEPRINT-CODE-INDEX-SYNC"

    def test_returns_reconciler_spec_with_priority_136(self, tmp_path):
        """priority 应为 136（frontmatter@135 之后、drift_scan@140 之前）。"""
        gw = _FakeGateway(tmp_path)
        spec = make_blueprint_code_index_reconciler(gw)
        assert spec.priority == 136

    def test_trigger_and_reconcile_are_callables(self, tmp_path):
        """trigger 和 reconcile 应为可调用对象。"""
        gw = _FakeGateway(tmp_path)
        spec = make_blueprint_code_index_reconciler(gw)
        assert callable(spec.trigger)
        assert callable(spec.reconcile)


# ---------------------------------------------------------------------------
# 测试：trigger 逻辑
# ---------------------------------------------------------------------------
class TestTrigger:
    """trigger 函数逻辑测试。"""

    def test_py_file_triggers(self, tmp_path):
        """.py 文件应触发（代码变更→depgraph 演进→索引需重算）。"""
        gw = _FakeGateway(tmp_path)
        spec = make_blueprint_code_index_reconciler(gw)
        files = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        assert spec.trigger(files) is True

    def test_docs_03_modules_md_triggers(self, tmp_path):
        """docs/03_modules/ 下的 .md 文件应触发（frontmatter module_id 可能变更）。"""
        gw = _FakeGateway(tmp_path)
        spec = make_blueprint_code_index_reconciler(gw)
        files = [str(tmp_path / "docs" / "03_modules" / "m1" / "blueprint.md")]
        assert spec.trigger(files) is True

    def test_other_md_does_not_trigger(self, tmp_path):
        """非 docs/03_modules/ 下的 .md 文件不应触发。"""
        gw = _FakeGateway(tmp_path)
        spec = make_blueprint_code_index_reconciler(gw)
        files = [str(tmp_path / "docs" / "01_policies" / "rule.md")]
        assert spec.trigger(files) is False

    def test_yaml_does_not_trigger(self, tmp_path):
        """.yaml 文件不应触发。"""
        gw = _FakeGateway(tmp_path)
        spec = make_blueprint_code_index_reconciler(gw)
        files = [str(tmp_path / "rules" / "trae_001.yaml")]
        assert spec.trigger(files) is False

    def test_empty_files_does_not_trigger(self, tmp_path):
        """空文件列表不应触发。"""
        gw = _FakeGateway(tmp_path)
        spec = make_blueprint_code_index_reconciler(gw)
        assert spec.trigger([]) is False


# ---------------------------------------------------------------------------
# 测试：reconcile 行为（每个用例独立 tmp_path → cooldown marker 隔离）
# ---------------------------------------------------------------------------
class TestReconcile:
    """reconcile 函数行为测试（mock subprocess/git）。"""

    @patch("zephyr.governance.audit.reconciliation_registry._run_subprocess")
    def test_subprocess_failure_returns_warn(self, mock_sub, tmp_path):
        """syncer subprocess 失败时应返回 warn（不阻断 commit）。"""
        mock_sub.return_value = _make_subprocess_result(returncode=1, stderr="db connection error")
        gw = _FakeGateway(tmp_path)
        spec = make_blueprint_code_index_reconciler(gw)
        result = spec.reconcile(["foo.py"], "sess-test")
        assert result.action == "warn"
        assert "code-index sync failed" in result.detail
        assert "rc=1" in result.detail

    @patch("zephyr.governance.audit.reconciliation_registry._run_subprocess")
    def test_no_md_changes_returns_clean(self, mock_sub, tmp_path):
        """syncer 成功但无 .md 变更时应返回 clean（幂等无漂移）。"""
        mock_sub.return_value = _make_subprocess_result(returncode=0, stdout="OK")
        gw = _FakeGateway(tmp_path, diff_files=[])
        spec = make_blueprint_code_index_reconciler(gw)
        result = spec.reconcile(["foo.py"], "sess-test")
        assert result.action == "clean"
        assert "no drift" in result.detail

    @patch("zephyr.governance.audit.reconciliation_registry._run_subprocess")
    def test_md_changes_with_commit_ok_returns_auto_committed(self, mock_sub, tmp_path):
        """有 .md 漂移且 auto-commit 成功时应返回 auto_committed。"""
        mock_sub.return_value = _make_subprocess_result(returncode=0, stdout="OK")
        gw = _FakeGateway(
            tmp_path,
            diff_files=["docs/03_modules/m1/blueprint.md", "docs/03_modules/m2/blueprint.md"],
            commit_status="OK",
        )
        spec = make_blueprint_code_index_reconciler(gw)
        result = spec.reconcile(["foo.py"], "sess-test")
        assert result.action == "auto_committed"
        assert "2 files auto-reconciled" in result.detail
        # 验证 _commit_auto 接线参数（session/files/message 契约）
        assert len(gw._commit_calls) == 1
        session_id, files, msg = gw._commit_calls[0]
        assert session_id == "sess-test"
        assert len(files) == 2
        assert all(f.endswith("blueprint.md") for f in files)
        assert "GATE-BLUEPRINT-CODE-INDEX-SYNC" in msg

    @patch("zephyr.governance.audit.reconciliation_registry._run_subprocess")
    def test_md_changes_with_nothing_to_commit_returns_clean(self, mock_sub, tmp_path):
        """有 .md 变更但 commit 返回 NOTHING_TO_COMMIT 时返回 clean（幂等空转）。"""
        mock_sub.return_value = _make_subprocess_result(returncode=0, stdout="OK")
        gw = _FakeGateway(
            tmp_path,
            diff_files=["docs/03_modules/m1/blueprint.md"],
            commit_status="NOTHING_TO_COMMIT",
        )
        spec = make_blueprint_code_index_reconciler(gw)
        result = spec.reconcile(["foo.py"], "sess-test")
        assert result.action == "clean"
        assert "no staged changes" in result.detail

    @patch("zephyr.governance.audit.reconciliation_registry._run_subprocess")
    def test_md_changes_with_commit_failure_returns_warn(self, mock_sub, tmp_path):
        """auto-commit 失败时返回 warn（留痕不阻断）。"""
        mock_sub.return_value = _make_subprocess_result(returncode=0, stdout="OK")
        gw = _FakeGateway(
            tmp_path,
            diff_files=["docs/03_modules/m1/blueprint.md"],
            commit_status="COMMIT_FAILED",
        )
        spec = make_blueprint_code_index_reconciler(gw)
        result = spec.reconcile(["foo.py"], "sess-test")
        assert result.action == "warn"
        assert "auto-commit failed" in result.detail
        assert "COMMIT_FAILED" in result.detail

    @patch("zephyr.governance.audit.reconciliation_registry._run_subprocess")
    def test_non_md_diff_files_ignored(self, mock_sub, tmp_path):
        """git diff 返回非 .md 文件时不触发 commit（只关心蓝图 .md）。"""
        mock_sub.return_value = _make_subprocess_result(returncode=0, stdout="OK")
        gw = _FakeGateway(
            tmp_path,
            diff_files=["docs/03_modules/m1/data.json", "docs/03_modules/m1/style.css"],
        )
        spec = make_blueprint_code_index_reconciler(gw)
        result = spec.reconcile(["foo.py"], "sess-test")
        assert result.action == "clean"
        assert "no drift" in result.detail
        assert len(gw._commit_calls) == 0

    @patch("zephyr.governance.audit.reconciliation_registry._run_subprocess")
    def test_git_diff_failure_returns_warn(self, mock_sub, tmp_path):
        """git diff 命令失败时应返回 warn。"""
        mock_sub.return_value = _make_subprocess_result(returncode=0, stdout="OK")
        gw = _FakeGateway(tmp_path)

        def failing_git(cmd):
            mock = MagicMock()
            mock.returncode = 1
            mock.stderr = "git error"
            mock.stdout = ""
            return mock

        gw.run_git = failing_git
        spec = make_blueprint_code_index_reconciler(gw)
        result = spec.reconcile(["foo.py"], "sess-test")
        assert result.action == "warn"
        assert "git diff failed" in result.detail


# ---------------------------------------------------------------------------
# 测试：cooldown（skip-if-recent，#ARCH-RECONCILER-TOCTOU-CLOBBER-001 同款止血）
# ---------------------------------------------------------------------------
class TestCooldown:
    """600s attempt cooldown：窗口内二次触发 skip；marker 损坏 fail-open。"""

    @patch("zephyr.governance.audit.reconciliation_registry._run_subprocess")
    def test_second_call_within_window_returns_skip(self, mock_sub, tmp_path):
        """首次调用打点（attempt 即生效），窗口内二次调用返回 skip 且不再跑 syncer。"""
        mock_sub.return_value = _make_subprocess_result(returncode=0, stdout="OK")
        gw = _FakeGateway(tmp_path, diff_files=[])
        spec = make_blueprint_code_index_reconciler(gw)

        first = spec.reconcile(["foo.py"], "sess-test")
        assert first.action == "clean"
        assert mock_sub.call_count == 1
        marker = tmp_path / ".runtime" / "code_index_sync_last_attempt"
        assert marker.exists(), "attempt marker 在 sync 开始前写入"

        second = spec.reconcile(["bar.py"], "sess-test")
        assert second.action == "skip"
        assert "cooldown" in second.detail
        assert mock_sub.call_count == 1, "cooldown 窗口内不得重跑 syncer"

    @patch("zephyr.governance.audit.reconciliation_registry._run_subprocess")
    def test_corrupt_marker_fails_open(self, mock_sub, tmp_path):
        """marker 内容损坏 → fail-open 继续执行 sync（不因坏 marker 永久跳过）。"""
        marker = tmp_path / ".runtime" / "code_index_sync_last_attempt"
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("not-a-timestamp", encoding="utf-8")

        mock_sub.return_value = _make_subprocess_result(returncode=0, stdout="OK")
        gw = _FakeGateway(tmp_path, diff_files=[])
        spec = make_blueprint_code_index_reconciler(gw)
        result = spec.reconcile(["foo.py"], "sess-test")
        assert result.action == "clean"
        assert mock_sub.call_count == 1
