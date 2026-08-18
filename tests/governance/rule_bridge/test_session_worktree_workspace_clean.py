# [A_test] module_id: MOD-GOV_session_worktree_workspace_clean | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_ENFORCEMENT | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §ARCH-WORKSPACE-DRIFT-SYSTEMIC-001
# [MODULE] tests.governance.rule_bridge.test_session_worktree_workspace_clean
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-GOV_ENFORCEMENT | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_session_worktree_workspace_clean.py — session lifecycle 工作区 clean 检查单测。

#ARCH-WORKSPACE-DRIFT-SYSTEMIC-001 Phase 1 + 1.5（2026-07-20）。

测试 _check_workspace_clean / _workspace_clean_check_merge / _workspace_clean_check_abort
/ _workspace_clean_check_start / _log_workspace_drift_warn 五个 helper：

- merge context: auto-sync 产物自动 restore；真实代码修改 fail-closed 阻断
- abort context: auto-sync 产物自动 restore；真实代码修改 fail-open 告警
- start context: auto-sync 产物自动 restore；真实代码修改 fail-open 告警
- fail-open: git status 失败 / 依赖缺失不阻断业务流程
- Phase 1.5: _log_workspace_drift_warn 落盘遥测，不阻断 commit

测试隔离：用 tmp_path + 真实 git 仓库（end-to-end）。
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_DIR = str(_PROJECT_ROOT / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from zephyr.gov_enforcement.rule_bridge.session_worktree import (  # noqa: E402
    _check_workspace_clean,
    _log_workspace_drift_warn,
    _workspace_clean_check_abort,
    _workspace_clean_check_merge,
    _workspace_clean_check_start,
    _WS_CLEAN_GATE_ID,
)


# ============================================================================
# 辅助函数
# ============================================================================


def _git_env() -> dict:
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@test.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@test.com"
    return env


def _init_git_repo(repo_dir: Path) -> None:
    repo_dir.mkdir(parents=True, exist_ok=True)
    env = _git_env()
    subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(repo_dir), capture_output=True, env=env, check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(repo_dir), capture_output=True, env=env, check=True,
    )


def _commit_initial(repo_dir: Path) -> None:
    """创建初始 commit（含一个 tracked 文件 + 一个 auto-sync 产物）。"""
    env = _git_env()
    # 真实代码文件
    (repo_dir / "src").mkdir(exist_ok=True)
    (repo_dir / "src" / "real_code.py").write_text("x = 1\n", encoding="utf-8")
    # auto-sync 产物（模拟 dashboard.json）
    (repo_dir / "data").mkdir(exist_ok=True)
    (repo_dir / "data" / "reports").mkdir(exist_ok=True)
    (repo_dir / "data" / "reports" / "dashboard.json").write_text(
        '{"v": 1}\n', encoding="utf-8",
    )
    subprocess.run(
        ["git", "add", "-A"],
        cwd=str(repo_dir), capture_output=True, env=env, check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=str(repo_dir), capture_output=True, env=env, check=True,
    )


def _make_auto_sync_dirty(repo_dir: Path) -> None:
    """让 auto-sync 产物变 dirty。"""
    (repo_dir / "data" / "reports" / "dashboard.json").write_text(
        '{"v": 2}\n', encoding="utf-8",
    )


def _make_real_code_dirty(repo_dir: Path) -> None:
    """让真实代码文件变 dirty。"""
    (repo_dir / "src" / "real_code.py").write_text("x = 2\n", encoding="utf-8")


def _commit_file(repo_dir: Path, rel_path: str, content: str) -> None:
    """创建/修改文件并 commit 到 HEAD（用于测试前需 tracked 的文件）。"""
    env = _git_env()
    fpath = repo_dir / rel_path
    fpath.parent.mkdir(parents=True, exist_ok=True)
    fpath.write_bytes(content.encode("utf-8"))
    subprocess.run(
        ["git", "add", rel_path],
        cwd=str(repo_dir), capture_output=True, env=env, check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", f"add {rel_path}"],
        cwd=str(repo_dir), capture_output=True, env=env, check=True,
    )


# ============================================================================
# Phase 1: _check_workspace_clean 单测
# ============================================================================


class TestCheckWorkspaceCleanMerge:
    """merge context: fail-closed 策略。"""

    def test_clean_workspace_passes(self, tmp_path: Path):
        """工作区 clean → passed=True。"""
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        passed, detail = _check_workspace_clean(tmp_path, "sess-test", context="merge")
        assert passed is True
        assert "clean" in detail

    def test_auto_sync_only_auto_restored(self, tmp_path: Path):
        """仅 auto-sync 产物 dirty → 自动 restore → passed=True。"""
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _make_auto_sync_dirty(tmp_path)
        passed, detail = _check_workspace_clean(tmp_path, "sess-test", context="merge")
        assert passed is True
        assert "restored" in detail

    def test_real_code_blocks_merge(self, tmp_path: Path):
        """有真实代码修改 → fail-closed 阻断 merge。"""
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _make_real_code_dirty(tmp_path)
        passed, detail = _check_workspace_clean(tmp_path, "sess-test", context="merge")
        assert passed is False
        assert "阻断" in detail or "WORKSPACE-CLEAN-CHECK" in detail

    def test_real_code_and_auto_sync_blocks_merge(self, tmp_path: Path):
        """auto-sync + 真实代码 → restore auto-sync 后仍阻断（真实代码未处理）。"""
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _make_auto_sync_dirty(tmp_path)
        _make_real_code_dirty(tmp_path)
        passed, detail = _check_workspace_clean(tmp_path, "sess-test", context="merge")
        assert passed is False
        assert "阻断" in detail or "WORKSPACE-CLEAN-CHECK" in detail

    def test_session_files_excluded_from_merge_check(self, tmp_path: Path):
        """merge context: session_files 列出的文件不视为搭便车（worktree 模式语义）。"""
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _make_real_code_dirty(tmp_path)  # 创建 src/real_code.py modified
        # 把 src/real_code.py 列入 session_files → 应被排除，merge 通过
        passed, detail = _check_workspace_clean(
            tmp_path, "sess-test", context="merge",
            session_files=["src/real_code.py"],
        )
        assert passed is True, f"session_files 排除失败: {detail}"

    def test_session_files_partial_exclusion_still_blocks(self, tmp_path: Path):
        """merge context: session_files 只排除列出的文件，其他真实代码修改仍阻断。"""
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _make_real_code_dirty(tmp_path)  # src/real_code.py modified
        # 再加一个未列入 session_files 的真实代码修改（先 commit 再 modified，才是 modified 状态）
        _commit_file(tmp_path, "src/other.py", "initial\n")
        (tmp_path / "src" / "other.py").write_bytes(b"modified\n")
        passed, detail = _check_workspace_clean(
            tmp_path, "sess-test", context="merge",
            session_files=["src/real_code.py"],  # 只排除 real_code.py
        )
        assert passed is False, f"未排除的真实代码修改应阻断: {detail}"


class TestCheckWorkspaceCleanAbort:
    """abort context: fail-open 策略。"""

    def test_clean_workspace_passes(self, tmp_path: Path):
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        passed, detail = _check_workspace_clean(tmp_path, "sess-test", context="abort")
        assert passed is True

    def test_real_code_fail_open(self, tmp_path: Path):
        """有真实代码修改 → fail-open 不阻断 abort。"""
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _make_real_code_dirty(tmp_path)
        passed, detail = _check_workspace_clean(tmp_path, "sess-test", context="abort")
        assert passed is True  # abort 不阻断
        assert "warn" in detail or "real code" in detail

    def test_auto_sync_restored(self, tmp_path: Path):
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _make_auto_sync_dirty(tmp_path)
        passed, detail = _check_workspace_clean(tmp_path, "sess-test", context="abort")
        assert passed is True
        assert "restored" in detail


class TestCheckWorkspaceCleanStart:
    """start context: fail-closed 策略（#ARCH-WORKTREE-COMMIT-PERSISTENCE-001 Phase 4）。"""

    def test_clean_workspace_passes(self, tmp_path: Path):
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        passed, detail = _check_workspace_clean(tmp_path, "sess-test", context="start")
        assert passed is True

    def test_real_code_fail_closed(self, tmp_path: Path):
        """start 时有真实代码修改 → fail-closed 阻断（Phase 4 治本，原 fail-open 无效）。"""
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _make_real_code_dirty(tmp_path)
        passed, detail = _check_workspace_clean(tmp_path, "sess-test", context="start")
        assert passed is False  # start 阻断（Phase 4: fail-closed）
        assert "WORKSPACE_DRIFT_BLOCKED" in detail

    def test_auto_sync_restored(self, tmp_path: Path):
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _make_auto_sync_dirty(tmp_path)
        passed, detail = _check_workspace_clean(tmp_path, "sess-test", context="start")
        assert passed is True


class TestCheckWorkspaceCleanFailOpen:
    """fail-open: git status 失败 / 依赖缺失不阻断。"""

    def test_invalid_context_raises(self, tmp_path: Path):
        """无效 context 应被当作 abort/start 处理（fail-open）。"""
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _make_real_code_dirty(tmp_path)
        # 无效 context 不走 fail-closed 分支（仅 merge 才阻断）
        passed, detail = _check_workspace_clean(
            tmp_path, "sess-test", context="invalid",
        )
        assert passed is True  # 非 merge context 不阻断

    def test_nonexistent_repo_fail_open(self, tmp_path: Path):
        """不存在的仓库 → fail-open 返回 True。"""
        nonexistent = tmp_path / "nonexistent"
        passed, detail = _check_workspace_clean(
            nonexistent, "sess-test", context="merge",
        )
        assert passed is True
        assert "skip" in detail or "failed" in detail


# ============================================================================
# Phase 1: 包装函数测试
# ============================================================================


class TestWrapperFunctions:
    """三个包装函数返回值正确。"""

    def test_merge_wrapper_blocks_on_real_code(self, tmp_path: Path):
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _make_real_code_dirty(tmp_path)
        passed, detail = _workspace_clean_check_merge(tmp_path, "sess-test")
        assert passed is False

    def test_abort_wrapper_never_blocks(self, tmp_path: Path):
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _make_real_code_dirty(tmp_path)
        passed, detail = _workspace_clean_check_abort(tmp_path, "sess-test")
        assert passed is True

    def test_start_wrapper_fail_closed(self, tmp_path: Path):
        """start wrapper: 有真实代码修改时 fail-closed（Phase 4 治本）。"""
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _make_real_code_dirty(tmp_path)
        passed, detail = _workspace_clean_check_start(tmp_path, "sess-test")
        assert passed is False  # Phase 4: start fail-closed

    def test_gate_id_constant(self):
        assert _WS_CLEAN_GATE_ID == "WORKSPACE-CLEAN-CHECK"


# ============================================================================
# Phase 1.5: _log_workspace_drift_warn 单测
# ============================================================================


class TestLogWorkspaceDriftWarn:
    """Phase 1.5: commit 前落盘遥测。"""

    def test_clean_workspace_no_warn(self, tmp_path: Path):
        """工作区 clean → 不落盘。"""
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _log_workspace_drift_warn(tmp_path, "sess-test", ["src/real_code.py"])
        warn_file = tmp_path / ".runtime" / "workspace_drift_warn.jsonl"
        assert not warn_file.exists()

    def test_missed_real_changes_logged(self, tmp_path: Path):
        """漏列真实代码 → 落盘遥测。"""
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _make_real_code_dirty(tmp_path)
        # commit 列出空 files（漏列 real_code.py）
        _log_workspace_drift_warn(tmp_path, "sess-test", [])
        warn_file = tmp_path / ".runtime" / "workspace_drift_warn.jsonl"
        assert warn_file.exists()
        content = warn_file.read_text(encoding="utf-8").strip()
        assert "src/real_code.py" in content
        assert "missed_count" in content

    def test_auto_sync_not_counted_as_missed(self, tmp_path: Path):
        """auto-sync 产物不算漏列。"""
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _make_auto_sync_dirty(tmp_path)
        # commit 列出空 files，auto-sync 产物 dirty 但不算漏列
        _log_workspace_drift_warn(tmp_path, "sess-test", [])
        warn_file = tmp_path / ".runtime" / "workspace_drift_warn.jsonl"
        assert not warn_file.exists()  # auto-sync 不落盘

    def test_files_listed_not_counted_as_missed(self, tmp_path: Path):
        """已列入 files 的修改不算漏列。"""
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _make_real_code_dirty(tmp_path)
        # commit 正确列出 real_code.py
        _log_workspace_drift_warn(tmp_path, "sess-test", ["src/real_code.py"])
        warn_file = tmp_path / ".runtime" / "workspace_drift_warn.jsonl"
        assert not warn_file.exists()

    def test_fail_open_on_error(self, tmp_path: Path):
        """异常不阻断（best-effort）。"""
        nonexistent = tmp_path / "nonexistent"
        # 不应抛异常
        _log_workspace_drift_warn(nonexistent, "sess-test", [])


# ============================================================================
# Phase 1.5: 集成验证（真实 git 仓库 end-to-end）
# ============================================================================


class TestEndToEndScenario:
    """end-to-end: 模拟 193 文件残留场景。"""

    def test_merge_blocks_on_multiple_real_changes(self, tmp_path: Path):
        """模拟多个真实代码修改 → merge 阻断。"""
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        # 模拟多个真实代码修改
        for i in range(5):
            (repo_dir := tmp_path / "src" / f"file_{i}.py").write_text(
                f"x = {i}\n", encoding="utf-8",
            )
            subprocess.run(
                ["git", "add", "-A"],
                cwd=str(tmp_path), capture_output=True, check=True,
                env=_git_env(),
            )
            subprocess.run(
                ["git", "commit", "-m", f"add file_{i}"],
                cwd=str(tmp_path), capture_output=True, check=True,
                env=_git_env(),
            )
            (tmp_path / "src" / f"file_{i}.py").write_text(
                f"x = {i * 10}\n", encoding="utf-8",
            )
        passed, detail = _workspace_clean_check_merge(tmp_path, "sess-test")
        assert passed is False
        assert "real code" in detail.lower() or "阻断" in detail

    def test_start_blocks_on_residue(self, tmp_path: Path):
        """start 时检测到真实代码残留 → fail-closed 阻断（Phase 4 治本，原 fail-open 无效）。

        auto-sync 产物先自动 restore，真实代码残留仍然存在 → 阻断。
        """
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _make_real_code_dirty(tmp_path)
        _make_auto_sync_dirty(tmp_path)
        passed, detail = _workspace_clean_check_start(tmp_path, "sess-test")
        # Phase 4: start fail-closed——真实代码残留阻断 start
        assert passed is False
        assert "WORKSPACE_DRIFT_BLOCKED" in detail


# ============================================================================
# Phase 2: auto-recover 内容完整性测试（staged / MM 状态处理）
# ============================================================================


def _make_auto_sync_staged(repo_dir: Path) -> None:
    """让 auto-sync 产物变 staged（M 状态）。"""
    (repo_dir / "data" / "reports" / "dashboard.json").write_text(
        '{"v": 99}\n', encoding="utf-8",
    )
    subprocess.run(
        ["git", "add", "data/reports/dashboard.json"],
        cwd=str(repo_dir), capture_output=True, check=True,
        env=_git_env(),
    )


def _make_auto_sync_mm_state(repo_dir: Path) -> None:
    """让 auto-sync 产物变 MM 状态（staged + worktree 同时 modified）。"""
    # 先 staged
    (repo_dir / "data" / "reports" / "dashboard.json").write_text(
        '{"v": 100}\n', encoding="utf-8",
    )
    subprocess.run(
        ["git", "add", "data/reports/dashboard.json"],
        cwd=str(repo_dir), capture_output=True, check=True,
        env=_git_env(),
    )
    # 再 worktree modified
    (repo_dir / "data" / "reports" / "dashboard.json").write_text(
        '{"v": 101}\n', encoding="utf-8",
    )


def _git_porcelain_status(repo_dir: Path) -> str:
    """获取 git status --porcelain 原始输出（过滤 .runtime/ 运行时审计目录）。

    2026-08-19 B2 治本适配：GitCommitGateway 的 index 卫生审计（gateway_index_
    hygiene.jsonl）落 project_root/.runtime/gate_audit/——生产主仓 .gitignore 已豁免
    .runtime/（L106），测试 tmp 仓无 .gitignore 致 `?? .runtime/` 假脏。过滤对齐
    生产"版本控制视角干净"语义（与既有 workspace_drift_warn.jsonl 同族运行时产物）。
    """
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(repo_dir), capture_output=True, text=True, check=True,
        env=_git_env(),
    )
    return "".join(
        ln for ln in r.stdout.splitlines(keepends=True)
        if not ln.rstrip("\n").endswith(" .runtime/") and ln.strip() != "?? .runtime/"
    )


class TestRestoreAutoSyncBatchStagedHandling:
    """Phase 2: _restore_auto_sync_batch 处理 staged / MM 状态。"""

    def test_staged_only_auto_sync_restored(self, tmp_path: Path):
        """M 状态（staged only）的 auto-sync 文件 → unstage + restore。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import (
            _restore_auto_sync_batch,
        )
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _make_auto_sync_staged(tmp_path)
        # 确认初始状态是 M （staged only）
        assert _git_porcelain_status(tmp_path).startswith("M  ")

        restored_count, failed = _restore_auto_sync_batch(
            tmp_path, ["data/reports/dashboard.json"], "test",
        )
        assert restored_count == 1
        assert failed == []
        # 还原后应该是 clean
        assert _git_porcelain_status(tmp_path).strip() == ""

    def test_mm_state_auto_sync_restored(self, tmp_path: Path):
        """MM 状态（staged + worktree）的 auto-sync 文件 → unstage + restore。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import (
            _restore_auto_sync_batch,
        )
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _make_auto_sync_mm_state(tmp_path)
        # 确认初始状态是 MM（staged + worktree）
        assert _git_porcelain_status(tmp_path).startswith("MM ")

        restored_count, failed = _restore_auto_sync_batch(
            tmp_path, ["data/reports/dashboard.json"], "test",
        )
        assert restored_count == 1
        assert failed == []
        # 还原后应该是 clean
        assert _git_porcelain_status(tmp_path).strip() == ""

    def test_mixed_staged_and_worktree_auto_sync(self, tmp_path: Path):
        """混合 M  +  M 状态的 auto-sync 文件 → 都被还原。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import (
            _restore_auto_sync_batch,
        )
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        # 创建第二个 auto-sync 产物（mock 路径模式）
        (tmp_path / "data" / "reports" / "summary.json").write_text(
            '{"s": 1}\n', encoding="utf-8",
        )
        subprocess.run(
            ["git", "add", "-A"],
            cwd=str(tmp_path), capture_output=True, check=True,
            env=_git_env(),
        )
        subprocess.run(
            ["git", "commit", "-m", "add summary"],
            cwd=str(tmp_path), capture_output=True, check=True,
            env=_git_env(),
        )
        # dashboard.json 设为 staged（M ）
        _make_auto_sync_staged(tmp_path)
        # summary.json 设为 worktree modified（ M）
        (tmp_path / "data" / "reports" / "summary.json").write_text(
            '{"s": 2}\n', encoding="utf-8",
        )
        # 验证状态
        status = _git_porcelain_status(tmp_path)
        assert "M  data/reports/dashboard.json" in status
        assert " M data/reports/summary.json" in status

        restored_count, failed = _restore_auto_sync_batch(
            tmp_path,
            ["data/reports/dashboard.json", "data/reports/summary.json"],
            "test",
        )
        assert restored_count == 2
        assert failed == []
        # 还原后应该是 clean
        assert _git_porcelain_status(tmp_path).strip() == ""

    def test_empty_files_returns_zero(self, tmp_path: Path):
        """空文件列表 → 返回 (0, [])。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import (
            _restore_auto_sync_batch,
        )
        restored_count, failed = _restore_auto_sync_batch(tmp_path, [], "test")
        assert restored_count == 0
        assert failed == []


class TestCheckWorkspaceCleanStagedIntegration:
    """Phase 2: _check_workspace_clean 集成测试——staged auto-sync 完整流程。"""

    def test_staged_auto_sync_passes_merge(self, tmp_path: Path):
        """merge context: staged auto-sync 文件 → 自动 unstage + restore → pass。"""
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _make_auto_sync_staged(tmp_path)
        passed, detail = _check_workspace_clean(tmp_path, "sess-test", context="merge")
        assert passed is True, f"staged auto-sync 应被自动还原: {detail}"
        assert "restored" in detail
        # 验证 git status 已 clean
        assert _git_porcelain_status(tmp_path).strip() == ""

    def test_mm_state_auto_sync_passes_merge(self, tmp_path: Path):
        """merge context: MM 状态 auto-sync 文件 → 自动 unstage + restore → pass。"""
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        _make_auto_sync_mm_state(tmp_path)
        passed, detail = _check_workspace_clean(tmp_path, "sess-test", context="merge")
        assert passed is True, f"MM 状态 auto-sync 应被自动还原: {detail}"
        assert "restored" in detail
        # 验证 git status 已 clean
        assert _git_porcelain_status(tmp_path).strip() == ""

    def test_staged_real_code_blocks_merge(self, tmp_path: Path):
        """merge context: staged 真实代码修改 → 仍 fail-closed 阻断。"""
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        # 真实代码 staged
        (tmp_path / "src" / "real_code.py").write_text("x = 99\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "src/real_code.py"],
            cwd=str(tmp_path), capture_output=True, check=True,
            env=_git_env(),
        )
        passed, detail = _check_workspace_clean(tmp_path, "sess-test", context="merge")
        assert passed is False
        assert "阻断" in detail or "WORKSPACE-CLEAN-CHECK" in detail

    def test_staged_real_code_fail_open_abort(self, tmp_path: Path):
        """abort context: staged 真实代码 → fail-open 不阻断。"""
        _init_git_repo(tmp_path)
        _commit_initial(tmp_path)
        (tmp_path / "src" / "real_code.py").write_text("x = 99\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "src/real_code.py"],
            cwd=str(tmp_path), capture_output=True, check=True,
            env=_git_env(),
        )
        passed, _ = _check_workspace_clean(tmp_path, "sess-test", context="abort")
        assert passed is True  # abort 不阻断
