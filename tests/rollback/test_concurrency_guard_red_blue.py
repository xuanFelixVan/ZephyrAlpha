# [A_test] module_id: MOD-GOV_git_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §concurrency_guard
# [MODULE] tests.red_blue.test_concurrency_guard_red_blue
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [DOMAIN] D_GOVERNANCE
# [A_module] module_id=MOD-INF-021 | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""
红蓝对抗极端测试 — git_guard + concurrency_guard 端到端防护能力验证。

测试目标：验证多 AI 并发场景下，裸 git 命令（reset --hard / checkout -- / stash / revert）
是否被正确拦截，防止覆盖其他 session 的工作。

测试矩阵：
  红队（攻击）：模拟其他 session 持有文件锁，尝试用裸 git 命令覆盖
  蓝队（防御）：git_guard.check_and_execute() 应阻断并返回 exit 1

场景覆盖：
  1. 其他 session 锁定文件 → git reset --hard → 被阻断
  2. 其他 session 锁定文件 → git checkout -- <file> → 被阻断
  3. 其他 session 锁定文件 → git stash → 被阻断
  4. 其他 session 锁定文件 → git revert <commit> → 被阻断
  5. 其他 session 锁定文件 → git restore <file> → 被阻断
  6. 本 session 锁定文件 → git reset --hard → 允许（透传）
  7. 无锁 → git reset --hard → 允许（透传）
  8. 非危险命令 → git status → 允许（透传）
  9. git reset --soft → 允许（不危险）
  10. 过期锁（TTL）→ git reset --hard → 允许（锁已失效）
  11. 并发：多线程同时触发 git_guard 检查
  12. 内部错误（registry.json 损坏）→ 安全透传
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from unittest.mock import patch

import pytest

# 确保 src 和项目根目录在 path 中
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_SRC = _PROJECT_ROOT / "src"
for _p in [str(_SRC), str(_PROJECT_ROOT)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# 导入 git_guard（scripts 包）
# mv 防护相关导入
from scripts.git_guard import (
    _EXTRACTORS,
    DANGEROUS_SUBCOMMANDS,
    MV_STRATEGY_ENV,
    check_and_execute,
    scan_untracked_in_dir,
)
from zephyr.infrastructure.runtime.concurrency_guard import (
    DEFAULT_TTL_S,
    scan_active_locks,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def _isolate_mv_strategy_env(monkeypatch):
    """每个测试前确保 MV_STRATEGY_ENV 不泄漏（与 test_concurrent_mv_guard.py 同源治本）。"""
    monkeypatch.delenv(MV_STRATEGY_ENV, raising=False)


@pytest.fixture(autouse=True)
def _isolate_l1_self_harm_layer(monkeypatch):
    """隔离 L1 自伤层环境依赖：git_guard._get_dirty_tracked_files 裸 subprocess 不带 cwd，
    会读 pytest 进程 cwd 的真仓状态（本 worktree 脏）致 fail-closed 误拦一切 reset --hard。
    patch 为空集让用例走到锁冲突真路径；红队用例同受益（此前脏工作区下被 L1 错因拦截，
    未真正验证锁冲突分支）。L1 层自身语义由其专项测试覆盖。"""
    monkeypatch.setattr("scripts.git_guard._get_dirty_tracked_files", lambda: set())


@pytest.fixture
def temp_git_repo():
    """创建临时 git 仓库，用于隔离测试。"""
    root = Path(tempfile.mkdtemp(prefix="git_guard_test_"))
    # 初始化 git 仓库
    subprocess.run(["git", "init"], cwd=root, capture_output=True, check=True)
    # 配置 user（避免 commit 失败）
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=root, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, capture_output=True)
    # 创建初始文件并提交
    (root / "README.md").write_text("# test\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=root, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=root, capture_output=True, check=True)
    # 创建 .ailocks 目录
    (root / ".ailocks").mkdir(exist_ok=True)
    return root


@pytest.fixture
def other_session_lock(temp_git_repo):
    """模拟其他 session 持有文件锁。"""
    registry = {
        "locks": {
            "src/important.py": {
                "owner_id": "session-other-123",
                "task": "editing important file",
                "timestamp": time.time(),
                "pid": 99999,
            }
        }
    }
    registry_path = temp_git_repo / ".ailocks" / "registry.json"
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    return temp_git_repo


@pytest.fixture
def own_session_lock(temp_git_repo):
    """模拟本 session 持有文件锁。"""
    registry = {
        "locks": {
            "src/important.py": {
                "owner_id": "session-me-456",
                "task": "my own edit",
                "timestamp": time.time(),
                "pid": os.getpid(),
            }
        }
    }
    registry_path = temp_git_repo / ".ailocks" / "registry.json"
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    return temp_git_repo


@pytest.fixture
def expired_lock(temp_git_repo):
    """模拟过期的文件锁（TTL 已过）。"""
    registry = {
        "locks": {
            "src/important.py": {
                "owner_id": "session-dead-789",
                "task": "crashed session",
                "timestamp": time.time() - (DEFAULT_TTL_S + 100),  # 过期
                "pid": 88888,
            }
        }
    }
    registry_path = temp_git_repo / ".ailocks" / "registry.json"
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    return temp_git_repo


@pytest.fixture
def corrupted_registry(temp_git_repo):
    """模拟损坏的 registry.json。"""
    registry_path = temp_git_repo / ".ailocks" / "registry.json"
    registry_path.write_text("{invalid json content!!!", encoding="utf-8")
    return temp_git_repo


def _make_git_args(repo_root: Path, session_id: str = "session-me-456"):
    """构造 git_guard 调用环境。"""
    env = os.environ.copy()
    env["ZEPHYR_SESSION_ID"] = session_id
    return env


# ============================================================================
# 红队场景：其他 session 锁定 → 危险命令应被阻断
# ============================================================================


class TestRedTeamBlockedByOtherSession:
    """红队：其他 session 持有锁时，所有危险命令必须被阻断。"""

    def test_reset_hard_blocked(self, temp_git_repo, other_session_lock):
        """场景1: 其他 session 锁定 → git reset --hard → exit 1"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard.run_git_silent") as mock_git_silent:
                    # ls-files 返回包含锁定文件的列表
                    mock_git_silent.return_value = "src/important.py\nREADME.md"
                    with patch("scripts.git_guard.passthrough") as mock_pass:
                        exit_code = check_and_execute(["reset", "--hard", "HEAD~1"])
        assert exit_code == 1, "git reset --hard 应被阻断"
        mock_pass.assert_not_called()

    def test_checkout_file_blocked(self, temp_git_repo, other_session_lock):
        """场景2: 其他 session 锁定 → git checkout -- <file> → exit 1"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard.run_git_silent") as mock_git_silent:
                    # ls-files 返回包含锁定文件的列表
                    mock_git_silent.return_value = "src/important.py\nREADME.md"
                    with patch("scripts.git_guard.passthrough") as mock_pass:
                        exit_code = check_and_execute(["checkout", "--", "src/important.py"])
        assert exit_code == 1, "git checkout -- <file> 应被阻断"
        mock_pass.assert_not_called()

    def test_stash_blocked(self, temp_git_repo, other_session_lock):
        """场景3: 其他 session 锁定 → git stash → exit 1"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard.run_git_silent") as mock_git_silent:
                    # diff --name-only HEAD 返回包含锁定文件
                    mock_git_silent.return_value = "src/important.py"
                    with patch("scripts.git_guard.passthrough") as mock_pass:
                        exit_code = check_and_execute(["stash"])
        assert exit_code == 1, "git stash 应被阻断"
        mock_pass.assert_not_called()

    def test_revert_blocked(self, temp_git_repo, other_session_lock):
        """场景4: 其他 session 锁定 → git revert <commit> → exit 1"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard.run_git_silent") as mock_git_silent:
                    # diff --name-only <commit>..HEAD 返回锁定文件
                    mock_git_silent.return_value = "src/important.py"
                    with patch("scripts.git_guard.passthrough") as mock_pass:
                        exit_code = check_and_execute(["revert", "abc123"])
        assert exit_code == 1, "git revert 应被阻断"
        mock_pass.assert_not_called()

    def test_restore_blocked(self, temp_git_repo, other_session_lock):
        """场景5: 其他 session 锁定 → git restore <file> → exit 1"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard.passthrough") as mock_pass:
                    exit_code = check_and_execute(["restore", "src/important.py"])
        assert exit_code == 1, "git restore 应被阻断"
        mock_pass.assert_not_called()


# ============================================================================
# 蓝队场景：本 session 锁 / 无锁 / 非危险命令 → 允许透传
# ============================================================================


class TestBlueTeamAllowedPassthrough:
    """蓝队：无冲突场景应允许透传。"""

    def test_own_session_lock_allowed(self, temp_git_repo, own_session_lock):
        """场景6: 本 session 锁定 → git reset --hard → 允许"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard.run_git_silent") as mock_git_silent:
                    mock_git_silent.return_value = "src/important.py"
                    with patch("scripts.git_guard.passthrough", return_value=0) as mock_pass:
                        exit_code = check_and_execute(["reset", "--hard", "HEAD~1"])
        assert exit_code == 0, "本 session 锁应允许透传"
        mock_pass.assert_called_once()

    def test_no_lock_allowed(self, temp_git_repo):
        """场景7: 无锁 → git reset --hard → 允许"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard.run_git_silent") as mock_git_silent:
                    mock_git_silent.return_value = "src/any.py"
                    with patch("scripts.git_guard.passthrough", return_value=0) as mock_pass:
                        exit_code = check_and_execute(["reset", "--hard", "HEAD~1"])
        assert exit_code == 0, "无锁应允许透传"
        mock_pass.assert_called_once()

    def test_non_dangerous_command_allowed(self, temp_git_repo, other_session_lock):
        """场景8: 非危险命令 → git status → 允许"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard.passthrough", return_value=0) as mock_pass:
                    exit_code = check_and_execute(["status"])
        assert exit_code == 0, "非危险命令应透传"
        mock_pass.assert_called_once()

    def test_reset_soft_allowed(self, temp_git_repo, other_session_lock):
        """场景9: git reset --soft → 允许（不危险）"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard.passthrough", return_value=0) as mock_pass:
                    exit_code = check_and_execute(["reset", "--soft", "HEAD~1"])
        assert exit_code == 0, "git reset --soft 应透传"
        mock_pass.assert_called_once()

    def test_empty_args_allowed(self, temp_git_repo):
        """无参数 → 允许透传"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        with patch("scripts.git_guard.passthrough", return_value=0) as mock_pass:
            exit_code = check_and_execute([])
        assert exit_code == 0
        mock_pass.assert_called_once()


# ============================================================================
# 边界场景：过期锁 / 损坏 registry / 内部错误
# ============================================================================


class TestEdgeCases:
    """边界场景：过期锁、损坏 registry、内部错误。"""

    def test_expired_lock_allowed(self, temp_git_repo, expired_lock):
        """场景10: 过期锁 → git reset --hard → 允许（锁已失效）"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        # 验证过期锁确实被忽略
        locks = scan_active_locks(temp_git_repo)
        assert len(locks) == 0, "过期锁应被忽略"

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard.run_git_silent") as mock_git_silent:
                    mock_git_silent.return_value = "src/important.py"
                    with patch("scripts.git_guard.passthrough", return_value=0) as mock_pass:
                        exit_code = check_and_execute(["reset", "--hard", "HEAD~1"])
        assert exit_code == 0, "过期锁应允许透传"
        mock_pass.assert_called_once()

    def test_corrupted_registry_safe_passthrough(self, temp_git_repo, corrupted_registry):
        """场景12: registry.json 损坏 → 安全透传（不阻断正常工作）"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        # 验证损坏 registry 返回空列表（不抛异常）
        locks = scan_active_locks(temp_git_repo)
        assert len(locks) == 0, "损坏 registry 应返回空列表"

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard.run_git_silent") as mock_git_silent:
                    mock_git_silent.return_value = "src/any.py"
                    with patch("scripts.git_guard.passthrough", return_value=0) as mock_pass:
                        exit_code = check_and_execute(["reset", "--hard", "HEAD~1"])
        assert exit_code == 0, "损坏 registry 应安全透传"
        mock_pass.assert_called_once()

    def test_no_ailocks_dir_allowed(self, temp_git_repo):
        """无 .ailocks 目录 → 允许透传"""
        # 删除 .ailocks 目录
        import shutil

        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        shutil.rmtree(temp_git_repo / ".ailocks", ignore_errors=True)

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard.run_git_silent") as mock_git_silent:
                    mock_git_silent.return_value = "src/any.py"
                    with patch("scripts.git_guard.passthrough", return_value=0) as mock_pass:
                        exit_code = check_and_execute(["reset", "--hard", "HEAD~1"])
        assert exit_code == 0
        mock_pass.assert_called_once()


# ============================================================================
# 并发场景：多线程同时触发 git_guard
# ============================================================================


class TestConcurrentGuard:
    """并发场景：多线程同时调用 git_guard。"""

    def test_concurrent_checks_no_deadlock(self, temp_git_repo, other_session_lock):
        """场景11: 10 线程并发调用 git_guard → 无死锁，全部被阻断"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        results = []
        errors = []

        def call_guard():
            try:
                return check_and_execute(["reset", "--hard", "HEAD~1"])
            except Exception as e:
                return e

        # mock.patch 非线程安全：每线程各自 patch 会互相拆解（先退出线程还原真函数，
        # 其余线程可能落到真仓/真 git）。所有线程补丁值相同，池外单次进程级 patch 等价且安全。
        with (
            patch("scripts.git_guard.get_project_root", return_value=temp_git_repo),
            patch("scripts.git_guard.get_session_id", return_value="session-me-456"),
            patch("scripts.git_guard.run_git_silent") as mock_git_silent,
            patch("scripts.git_guard.passthrough", return_value=0),
        ):
            mock_git_silent.return_value = "src/important.py"
            with ThreadPoolExecutor(max_workers=10) as pool:
                futures = [pool.submit(call_guard) for _ in range(10)]
                for future in as_completed(futures, timeout=30):
                    try:
                        result = future.result()
                        if isinstance(result, Exception):
                            errors.append(str(result))
                        else:
                            results.append(result)
                    except Exception as e:
                        errors.append(str(e))

        assert len(errors) == 0, f"并发执行错误: {errors}"
        assert len(results) == 10
        assert all(r == 1 for r in results), "所有并发调用都应被阻断"

    def test_mixed_concurrent_some_blocked_some_allowed(self, temp_git_repo):
        """混合并发：部分文件被其他 session 锁，部分无锁 → 只有冲突的被阻断"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        # 文件 A 被其他 session 锁定
        registry = {
            "locks": {
                "src/locked.py": {
                    "owner_id": "session-other",
                    "task": "editing",
                    "timestamp": time.time(),
                    "pid": 99999,
                }
            }
        }
        (temp_git_repo / ".ailocks" / "registry.json").write_text(json.dumps(registry), encoding="utf-8")

        results = {"blocked": 0, "allowed": 0}
        lock = threading.Lock()
        # 并发 patch 竞争治本：patch 全局只进出一回，run_git_silent 按 thread-local
        # 分流目标文件（原实现每线程各自 with patch——模块属性全局共享，线程交错时
        # locked 线程读到 free 线程的 mock 返回值 → 误透传，flaky）
        _tlocal = threading.local()

        def call_reset(target: str):
            _tlocal.target = target
            return check_and_execute(["reset", "--hard", "HEAD~1"])

        with (
            patch("scripts.git_guard.get_project_root", return_value=temp_git_repo),
            patch("scripts.git_guard.get_session_id", return_value="session-me"),
            patch("scripts.git_guard.run_git_silent") as mock_git_silent,
            patch("scripts.git_guard.passthrough", return_value=0),
        ):
            mock_git_silent.side_effect = lambda *a, **k: _tlocal.target
            with ThreadPoolExecutor(max_workers=4) as pool:
                futures = []
                for _ in range(5):
                    futures.append(pool.submit(call_reset, "src/locked.py"))
                for _ in range(5):
                    futures.append(pool.submit(call_reset, "src/free.py"))
                for future in as_completed(futures, timeout=30):
                    result = future.result()
                    with lock:
                        if result == 1:
                            results["blocked"] += 1
                        else:
                            results["allowed"] += 1

        assert results["blocked"] == 5, f"应阻断5个，实际{results['blocked']}"
        assert results["allowed"] == 5, f"应允许5个，实际{results['allowed']}"


# ============================================================================
# 真实 git 命令执行验证（端到端）
# ============================================================================


class TestEndToEndRealGit:
    """端到端：真实 git 命令执行验证（不 mock _passthrough）。"""

    def test_real_reset_hard_blocked(self, temp_git_repo, other_session_lock):
        """端到端：其他 session 锁定 → git reset --hard 真实被阻断，文件不丢失"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        # 创建一个会被 reset 的文件
        target_file = temp_git_repo / "src" / "important.py"
        target_file.parent.mkdir(exist_ok=True)
        target_file.write_text("# important content\n", encoding="utf-8")
        subprocess.run(["git", "add", "src/important.py"], cwd=temp_git_repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "add important"], cwd=temp_git_repo, capture_output=True)

        # 记录原始 commit
        original_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=temp_git_repo, capture_output=True, text=True
        ).stdout.strip()

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard.run_git_silent") as mock_git_silent:
                    mock_git_silent.return_value = "src/important.py"
                    exit_code = check_and_execute(["reset", "--hard", "HEAD~1"])

        # 验证被阻断
        assert exit_code == 1, "应被阻断"

        # 验证文件未被破坏
        current_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=temp_git_repo, capture_output=True, text=True
        ).stdout.strip()
        assert current_commit == original_commit, "commit 不应变（reset 未执行）"
        assert target_file.exists(), "文件应存在"
        assert target_file.read_text(encoding="utf-8") == "# important content\n"

    def test_real_reset_hard_allowed_no_lock(self, temp_git_repo):
        """端到端：无锁 → git reset --hard 真实执行"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        # 创建文件并提交
        target_file = temp_git_repo / "src" / "free.py"
        target_file.parent.mkdir(exist_ok=True)
        target_file.write_text("# v1\n", encoding="utf-8")
        subprocess.run(["git", "add", "src/free.py"], cwd=temp_git_repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "v1"], cwd=temp_git_repo, capture_output=True)
        first_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=temp_git_repo, capture_output=True, text=True
        ).stdout.strip()

        # 修改文件并提交
        target_file.write_text("# v2\n", encoding="utf-8")
        subprocess.run(["git", "add", "src/free.py"], cwd=temp_git_repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "v2"], cwd=temp_git_repo, capture_output=True)

        # mock _passthrough 在 temp_git_repo 中执行 git 命令
        def _passthrough_in_temp(git_args):
            return subprocess.call(["git"] + git_args, cwd=temp_git_repo)

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-me"):
                with patch("scripts.git_guard.run_git_silent") as mock_git_silent:
                    mock_git_silent.return_value = "src/free.py"
                    with patch("scripts.git_guard.passthrough", side_effect=_passthrough_in_temp):
                        exit_code = check_and_execute(["reset", "--hard", "HEAD~1"])

        # 验证透传执行
        assert exit_code == 0, "无锁应允许执行"
        current_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=temp_git_repo, capture_output=True, text=True
        ).stdout.strip()
        assert current_commit == first_commit, "reset 应执行，回到第一个 commit"


# ============================================================================
# 防御能力总结验证
# ============================================================================


class TestDefenseSummary:
    """防御能力总结：验证所有防护层协同工作。"""

    def test_all_dangerous_commands_covered(self):
        """验证所有危险子命令都有防护路径（extractor 锁冲突 或 专用前置自伤分支）"""
        # DANGEROUS_SUBCOMMANDS 和 _EXTRACTORS 已在顶部导入。
        # clean 由专用前置分支 _check_self_harm_clean 防护（#ARCH-GIT-CLEAN-GUARD-FIX：
        # untracked 不在锁管辖，无 extractor 是刻意设计，与 mv stub 模式同类）
        _DEDICATED_PRECHECK = {"clean"}
        for cmd in DANGEROUS_SUBCOMMANDS:
            assert cmd in _EXTRACTORS or cmd in _DEDICATED_PRECHECK, f"危险命令 {cmd} 缺少防护路径"

    def test_concurrency_guard_scan_correctness(self, temp_git_repo, other_session_lock):
        """验证 concurrency_guard 扫描结果正确"""
        locks = scan_active_locks(temp_git_repo)
        assert len(locks) == 1
        assert locks[0].file_path == "src/important.py"
        assert locks[0].owner_id == "session-other-123"
        assert locks[0].task == "editing important file"

    def test_session_id_isolation(self, temp_git_repo, other_session_lock):
        """验证 session_id 隔离：其他 session 的锁对本 session 是冲突"""
        from zephyr.infrastructure.runtime.concurrency_guard import check_rollback_conflict

        # 本 session 检查 → 冲突
        result = check_rollback_conflict(["src/important.py"], "session-me", temp_git_repo)
        assert result.has_conflict
        assert "src/important.py" in result.blocked_files

        # 其他 session 检查自己的锁 → 无冲突
        result2 = check_rollback_conflict(["src/important.py"], "session-other-123", temp_git_repo)
        assert not result2.has_conflict


# ============================================================================
# Stash 专项防护验证（根因修复：stash push 会移走未提交修改）
# ============================================================================


class TestStashGuard:
    """stash 专项测试：验证 stash push 默认阻断，pop/apply 检查锁冲突。

    根因：原 git_guard 对 stash 只检查锁冲突，不阻止 push 移走自己的未提交修改。
    修复后：push 有未提交修改 → 阻断；pop/apply → 检查锁冲突；list/show/drop → 透传。
    """

    def test_stash_push_blocked_with_uncommitted(self, temp_git_repo):
        """stash push 有未提交修改 → 阻断（防止移走修改）"""
        from scripts.git_guard import check_and_execute

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.run_git_silent") as mock_git:
                mock_git.return_value = "src/uncommitted.py"
                with patch("scripts.git_guard.passthrough", return_value=0):
                    exit_code = check_and_execute(["stash"])
        assert exit_code == 1, "有未提交修改时 stash 应被阻断"

    def test_stash_push_allowed_no_uncommitted(self, temp_git_repo):
        """stash push 无未提交修改 → 透传（stash 无操作）"""
        from scripts.git_guard import check_and_execute

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.run_git_silent", return_value=""):
                with patch("scripts.git_guard.passthrough", return_value=0):
                    exit_code = check_and_execute(["stash"])
        assert exit_code == 0, "无未提交修改时 stash 应透传"

    def test_stash_push_force_env(self, temp_git_repo, monkeypatch):
        """ZEPHYR_FORCE_STASH=1 → 强制 stash 透传（self_healer 等合法场景）"""
        from scripts.git_guard import check_and_execute

        monkeypatch.setenv("ZEPHYR_FORCE_STASH", "1")
        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.run_git_silent") as mock_git:
                mock_git.return_value = "src/uncommitted.py"
                with patch("scripts.git_guard.passthrough", return_value=0):
                    exit_code = check_and_execute(["stash"])
        assert exit_code == 0, "ZEPHYR_FORCE_STASH=1 应强制透传"

    def test_stash_list_readonly_passthrough(self, temp_git_repo):
        """stash list → 透传（只读操作）"""
        from scripts.git_guard import check_and_execute

        with patch("scripts.git_guard.passthrough", return_value=0) as mock_pass:
            exit_code = check_and_execute(["stash", "list"])
        assert exit_code == 0, "stash list 应透传"
        assert mock_pass.called, "stash list 应调用 _passthrough"

    def test_stash_show_readonly_passthrough(self, temp_git_repo):
        """stash show → 透传（只读操作）"""
        from scripts.git_guard import check_and_execute

        with patch("scripts.git_guard.passthrough", return_value=0) as mock_pass:
            exit_code = check_and_execute(["stash", "show"])
        assert exit_code == 0
        assert mock_pass.called

    def test_stash_pop_blocked_with_lock_conflict(self, temp_git_repo, other_session_lock):
        """stash pop 有锁冲突 → 阻断（会覆盖工作区文件）"""
        from scripts.git_guard import check_and_execute

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-me"):
                with patch("scripts.git_guard.run_git_silent") as mock_git:
                    mock_git.return_value = "src/important.py"
                    with patch("scripts.git_guard.passthrough", return_value=0):
                        exit_code = check_and_execute(["stash", "pop"])
        assert exit_code == 1, "stash pop 有锁冲突应阻断"

    def test_stash_pop_allowed_no_lock_conflict(self, temp_git_repo):
        """stash pop 无锁冲突 → 透传"""
        from scripts.git_guard import check_and_execute

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-me"):
                with patch("scripts.git_guard.run_git_silent") as mock_git:
                    mock_git.return_value = "src/free.py"
                    with patch("scripts.git_guard.passthrough", return_value=0):
                        exit_code = check_and_execute(["stash", "pop"])
        assert exit_code == 0, "stash pop 无锁冲突应透传"

    def test_stash_apply_blocked_with_lock_conflict(self, temp_git_repo, other_session_lock):
        """stash apply 有锁冲突 → 阻断"""
        from scripts.git_guard import check_and_execute

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-me"):
                with patch("scripts.git_guard.run_git_silent") as mock_git:
                    mock_git.return_value = "src/important.py"
                    with patch("scripts.git_guard.passthrough", return_value=0):
                        exit_code = check_and_execute(["stash", "apply"])
        assert exit_code == 1, "stash apply 有锁冲突应阻断"


# ============================================================================
# git mv 目录重命名防护验证（根因修复：git mv 只移动已跟踪文件，未跟踪文件丢失）
# ============================================================================


class TestMvGuardMock:
    """git mv 防护 mock 测试：验证拦截逻辑（不执行真实 git 命令）。"""

    def test_mv_dir_with_untracked_blocked(self, temp_git_repo):
        """场景: 源目录存在未跟踪文件 → 默认策略 block → exit 1"""
        from scripts.git_guard import check_and_execute

        # 创建源目录（模拟目录存在）
        (temp_git_repo / "old_dir").mkdir(exist_ok=True)

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.scan_untracked_in_dir", return_value=["old_dir/untracked.md"]):
                with patch("scripts.git_guard.passthrough", return_value=0) as mock_pass:
                    exit_code = check_and_execute(["mv", "old_dir", "new_dir"])
        assert exit_code == 1, "源目录有未跟踪文件时 git mv 应被阻断"
        mock_pass.assert_not_called()

    def test_mv_dir_no_untracked_passthrough(self, temp_git_repo):
        """场景: 源目录无未跟踪文件 → 透传"""
        from scripts.git_guard import check_and_execute

        (temp_git_repo / "old_dir").mkdir(exist_ok=True)

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.scan_untracked_in_dir", return_value=[]):
                with patch("scripts.git_guard.passthrough", return_value=0) as mock_pass:
                    exit_code = check_and_execute(["mv", "old_dir", "new_dir"])
        assert exit_code == 0, "无未跟踪文件应透传"
        mock_pass.assert_called_once()

    def test_mv_file_not_dir_passthrough(self, temp_git_repo):
        """场景: 源是文件（非目录）→ 透传（不检查未跟踪文件）"""
        from scripts.git_guard import check_and_execute

        # 创建文件（非目录）
        (temp_git_repo / "tracked_file.py").write_text("# test\n", encoding="utf-8")

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.scan_untracked_in_dir") as mock_scan:
                with patch("scripts.git_guard.passthrough", return_value=0) as mock_pass:
                    exit_code = check_and_execute(["mv", "tracked_file.py", "renamed.py"])
        assert exit_code == 0, "源是文件应透传"
        mock_pass.assert_called_once()
        mock_scan.assert_not_called()

    def test_mv_not_enough_args_passthrough(self, temp_git_repo):
        """场景: git mv 参数不足（<2）→ 透传"""
        from scripts.git_guard import check_and_execute

        with patch("scripts.git_guard.passthrough", return_value=0) as mock_pass:
            exit_code = check_and_execute(["mv", "only_one_arg"])
        assert exit_code == 0, "参数不足应透传"
        mock_pass.assert_called_once()

    def test_mv_dir_strategy_force(self, temp_git_repo, monkeypatch):
        """场景: ZEPHYR_MV_STRATEGY=force → 强制透传"""
        from scripts.git_guard import check_and_execute

        monkeypatch.setenv(MV_STRATEGY_ENV, "force")
        (temp_git_repo / "old_dir").mkdir(exist_ok=True)

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.scan_untracked_in_dir", return_value=["old_dir/untracked.md"]):
                with patch("scripts.git_guard.passthrough", return_value=0) as mock_pass:
                    exit_code = check_and_execute(["mv", "old_dir", "new_dir"])
        assert exit_code == 0, "force 策略应透传"
        mock_pass.assert_called_once()

    def test_mv_dir_blocked_reports_files(self, temp_git_repo, capsys):
        """场景: block 策略报告未跟踪文件列表"""
        from scripts.git_guard import check_and_execute

        (temp_git_repo / "old_dir").mkdir(exist_ok=True)

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.scan_untracked_in_dir", return_value=["old_dir/a.md", "old_dir/b.md"]):
                with patch("scripts.git_guard.passthrough", return_value=0):
                    exit_code = check_and_execute(["mv", "old_dir", "new_dir"])

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "old_dir/a.md" in captured.err
        assert "old_dir/b.md" in captured.err
        assert "ZEPHYR_MV_STRATEGY" in captured.err


class TestMvGuardEndToEnd:
    """git mv 防护端到端测试：真实文件系统操作。"""

    def _setup_dir_with_tracked_and_untracked(self, repo_root: Path, dir_name: str):
        """创建含已跟踪+未跟踪文件的目录。"""
        dir_path = repo_root / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        # 已跟踪文件
        (dir_path / "tracked.py").write_text("# tracked\n", encoding="utf-8")
        subprocess.run(["git", "add", f"{dir_name}/tracked.py"], cwd=repo_root, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "add tracked"], cwd=repo_root, capture_output=True, check=True)
        # 未跟踪文件
        (dir_path / "untracked.md").write_text("# untracked content\n", encoding="utf-8")
        (dir_path / "subdir").mkdir(exist_ok=True)
        (dir_path / "subdir" / "nested.md").write_text("# nested\n", encoding="utf-8")
        return dir_path

    def test_mv_dir_strategy_move_e2e(self, temp_git_repo, monkeypatch):
        """端到端: strategy=move → 未跟踪文件移动到目标目录"""
        from scripts.git_guard import check_and_execute

        monkeypatch.setenv(MV_STRATEGY_ENV, "move")
        self._setup_dir_with_tracked_and_untracked(temp_git_repo, "old_dir")

        def _passthrough_in_temp(git_args):
            return subprocess.call(["git"] + git_args, cwd=temp_git_repo)

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.passthrough", side_effect=_passthrough_in_temp):
                exit_code = check_and_execute(["mv", "old_dir", "new_dir"])

        assert exit_code == 0, "move 策略应成功执行"
        # 未跟踪文件应在新目录中
        assert (temp_git_repo / "new_dir" / "untracked.md").exists(), "未跟踪文件应移动到新目录"
        assert (temp_git_repo / "new_dir" / "subdir" / "nested.md").exists(), "嵌套未跟踪文件应移动到新目录"
        # 内容应保留
        assert (temp_git_repo / "new_dir" / "untracked.md").read_text(encoding="utf-8") == "# untracked content\n"

    def test_mv_dir_strategy_stage_e2e(self, temp_git_repo, monkeypatch):
        """端到端: strategy=stage → 未跟踪文件暂存到 .aidrafts/"""
        from scripts.git_guard import check_and_execute

        monkeypatch.setenv(MV_STRATEGY_ENV, "stage")
        monkeypatch.setenv("ZEPHYR_SESSION_ID", "session-test-mv")
        self._setup_dir_with_tracked_and_untracked(temp_git_repo, "old_dir")

        def _passthrough_in_temp(git_args):
            return subprocess.call(["git"] + git_args, cwd=temp_git_repo)

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-test-mv"):
                with patch("scripts.git_guard.passthrough", side_effect=_passthrough_in_temp):
                    exit_code = check_and_execute(["mv", "old_dir", "new_dir"])

        assert exit_code == 0, "stage 策略应成功执行"
        # 未跟踪文件应在 .aidrafts/ 中
        stage_base = temp_git_repo / ".aidrafts" / "session-test-mv" / "mv_rescue"
        assert (stage_base / "old_dir" / "untracked.md").exists(), "未跟踪文件应暂存到 .aidrafts/"
        assert (stage_base / "old_dir" / "subdir" / "nested.md").exists(), "嵌套未跟踪文件应暂存"
        # 映射文件应存在
        mapping_file = stage_base / "mapping.json"
        assert mapping_file.exists(), "映射文件应存在"
        import json as _json

        mapping = _json.loads(mapping_file.read_text(encoding="utf-8"))
        assert mapping["source_dir"] == "old_dir"
        assert "old_dir/untracked.md" in mapping["files"]

    def test_mv_dir_blocked_preserves_files(self, temp_git_repo):
        """端到端: block 策略 → 文件不被移动，git mv 不执行"""
        from scripts.git_guard import check_and_execute

        self._setup_dir_with_tracked_and_untracked(temp_git_repo, "old_dir")

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.passthrough", return_value=0) as mock_pass:
                exit_code = check_and_execute(["mv", "old_dir", "new_dir"])

        assert exit_code == 1, "block 策略应阻断"
        mock_pass.assert_not_called()
        # 未跟踪文件应仍在原位
        assert (temp_git_repo / "old_dir" / "untracked.md").exists(), "阻断时文件不应被移动"
        assert (temp_git_repo / "old_dir" / "subdir" / "nested.md").exists(), "嵌套文件不应被移动"

    def test_mv_dir_no_untracked_e2e(self, temp_git_repo):
        """端到端: 目录无未跟踪文件 → 正常 git mv 执行"""
        from scripts.git_guard import check_and_execute

        # 创建仅含已跟踪文件的目录
        dir_path = temp_git_repo / "clean_dir"
        dir_path.mkdir(exist_ok=True)
        (dir_path / "tracked.py").write_text("# tracked\n", encoding="utf-8")
        subprocess.run(["git", "add", "clean_dir/tracked.py"], cwd=temp_git_repo, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "add clean"], cwd=temp_git_repo, capture_output=True, check=True)

        def _passthrough_in_temp(git_args):
            return subprocess.call(["git"] + git_args, cwd=temp_git_repo)

        with patch("scripts.git_guard.get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard.passthrough", side_effect=_passthrough_in_temp):
                exit_code = check_and_execute(["mv", "clean_dir", "renamed_dir"])

        assert exit_code == 0, "无未跟踪文件应正常执行"
        assert (temp_git_repo / "renamed_dir" / "tracked.py").exists(), "已跟踪文件应在新目录"


class TestMvScanUntracked:
    """scan_untracked_in_dir 单元测试。"""

    def test_scan_finds_untracked_files(self, temp_git_repo):
        """扫描应发现目录中的未跟踪文件"""
        dir_path = temp_git_repo / "test_dir"
        dir_path.mkdir(exist_ok=True)
        (dir_path / "untracked.md").write_text("# untracked\n", encoding="utf-8")
        (dir_path / "sub").mkdir(exist_ok=True)
        (dir_path / "sub" / "nested.md").write_text("# nested\n", encoding="utf-8")

        result = scan_untracked_in_dir("test_dir", temp_git_repo)
        assert "test_dir/untracked.md" in result
        assert "test_dir/sub/nested.md" in result

    def test_scan_ignores_tracked_files(self, temp_git_repo):
        """扫描应忽略已跟踪文件"""
        dir_path = temp_git_repo / "test_dir"
        dir_path.mkdir(exist_ok=True)
        (dir_path / "tracked.py").write_text("# tracked\n", encoding="utf-8")
        subprocess.run(["git", "add", "test_dir/tracked.py"], cwd=temp_git_repo, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "add"], cwd=temp_git_repo, capture_output=True, check=True)

        result = scan_untracked_in_dir("test_dir", temp_git_repo)
        assert len(result) == 0, "已跟踪文件不应出现在未跟踪列表"

    def test_scan_empty_dir(self, temp_git_repo):
        """空目录 → 空列表"""
        (temp_git_repo / "empty_dir").mkdir(exist_ok=True)
        result = scan_untracked_in_dir("empty_dir", temp_git_repo)
        assert result == []
