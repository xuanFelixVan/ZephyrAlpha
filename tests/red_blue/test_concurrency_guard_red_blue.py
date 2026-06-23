# [A_test] module_id: MOD-GOV_git_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback-system/blueprint.md | §concurrency_guard
# [MODULE] tests.red_blue.test_concurrency_guard_red_blue
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
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

from zephyr.infrastructure.rollback.concurrency_guard import (
    DEFAULT_TTL_S,
    scan_active_locks,
)

# 导入 git_guard（scripts 包）
from scripts.git_guard import check_and_execute, DANGEROUS_SUBCOMMANDS, _EXTRACTORS


# ============================================================================
# Fixtures
# ============================================================================


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

        with patch("scripts.git_guard._get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard._get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard._run_git_silent") as mock_git_silent:
                    # ls-files 返回包含锁定文件的列表
                    mock_git_silent.return_value = "src/important.py\nREADME.md"
                    with patch("scripts.git_guard._passthrough") as mock_pass:
                        exit_code = check_and_execute(["reset", "--hard", "HEAD~1"])
        assert exit_code == 1, "git reset --hard 应被阻断"
        mock_pass.assert_not_called()

    def test_checkout_file_blocked(self, temp_git_repo, other_session_lock):
        """场景2: 其他 session 锁定 → git checkout -- <file> → exit 1"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        with patch("scripts.git_guard._get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard._get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard._run_git_silent") as mock_git_silent:
                    # ls-files 返回包含锁定文件的列表
                    mock_git_silent.return_value = "src/important.py\nREADME.md"
                    with patch("scripts.git_guard._passthrough") as mock_pass:
                        exit_code = check_and_execute(["checkout", "--", "src/important.py"])
        assert exit_code == 1, "git checkout -- <file> 应被阻断"
        mock_pass.assert_not_called()

    def test_stash_blocked(self, temp_git_repo, other_session_lock):
        """场景3: 其他 session 锁定 → git stash → exit 1"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        with patch("scripts.git_guard._get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard._get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard._run_git_silent") as mock_git_silent:
                    # diff --name-only HEAD 返回包含锁定文件
                    mock_git_silent.return_value = "src/important.py"
                    with patch("scripts.git_guard._passthrough") as mock_pass:
                        exit_code = check_and_execute(["stash"])
        assert exit_code == 1, "git stash 应被阻断"
        mock_pass.assert_not_called()

    def test_revert_blocked(self, temp_git_repo, other_session_lock):
        """场景4: 其他 session 锁定 → git revert <commit> → exit 1"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        with patch("scripts.git_guard._get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard._get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard._run_git_silent") as mock_git_silent:
                    # diff --name-only <commit>..HEAD 返回锁定文件
                    mock_git_silent.return_value = "src/important.py"
                    with patch("scripts.git_guard._passthrough") as mock_pass:
                        exit_code = check_and_execute(["revert", "abc123"])
        assert exit_code == 1, "git revert 应被阻断"
        mock_pass.assert_not_called()

    def test_restore_blocked(self, temp_git_repo, other_session_lock):
        """场景5: 其他 session 锁定 → git restore <file> → exit 1"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        with patch("scripts.git_guard._get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard._get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard._passthrough") as mock_pass:
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

        with patch("scripts.git_guard._get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard._get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard._run_git_silent") as mock_git_silent:
                    mock_git_silent.return_value = "src/important.py"
                    with patch("scripts.git_guard._passthrough", return_value=0) as mock_pass:
                        exit_code = check_and_execute(["reset", "--hard", "HEAD~1"])
        assert exit_code == 0, "本 session 锁应允许透传"
        mock_pass.assert_called_once()

    def test_no_lock_allowed(self, temp_git_repo):
        """场景7: 无锁 → git reset --hard → 允许"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        with patch("scripts.git_guard._get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard._get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard._run_git_silent") as mock_git_silent:
                    mock_git_silent.return_value = "src/any.py"
                    with patch("scripts.git_guard._passthrough", return_value=0) as mock_pass:
                        exit_code = check_and_execute(["reset", "--hard", "HEAD~1"])
        assert exit_code == 0, "无锁应允许透传"
        mock_pass.assert_called_once()

    def test_non_dangerous_command_allowed(self, temp_git_repo, other_session_lock):
        """场景8: 非危险命令 → git status → 允许"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        with patch("scripts.git_guard._get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard._get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard._passthrough", return_value=0) as mock_pass:
                    exit_code = check_and_execute(["status"])
        assert exit_code == 0, "非危险命令应透传"
        mock_pass.assert_called_once()

    def test_reset_soft_allowed(self, temp_git_repo, other_session_lock):
        """场景9: git reset --soft → 允许（不危险）"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        with patch("scripts.git_guard._get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard._get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard._passthrough", return_value=0) as mock_pass:
                    exit_code = check_and_execute(["reset", "--soft", "HEAD~1"])
        assert exit_code == 0, "git reset --soft 应透传"
        mock_pass.assert_called_once()

    def test_empty_args_allowed(self, temp_git_repo):
        """无参数 → 允许透传"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        with patch("scripts.git_guard._passthrough", return_value=0) as mock_pass:
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

        with patch("scripts.git_guard._get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard._get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard._run_git_silent") as mock_git_silent:
                    mock_git_silent.return_value = "src/important.py"
                    with patch("scripts.git_guard._passthrough", return_value=0) as mock_pass:
                        exit_code = check_and_execute(["reset", "--hard", "HEAD~1"])
        assert exit_code == 0, "过期锁应允许透传"
        mock_pass.assert_called_once()

    def test_corrupted_registry_safe_passthrough(self, temp_git_repo, corrupted_registry):
        """场景12: registry.json 损坏 → 安全透传（不阻断正常工作）"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        # 验证损坏 registry 返回空列表（不抛异常）
        locks = scan_active_locks(temp_git_repo)
        assert len(locks) == 0, "损坏 registry 应返回空列表"

        with patch("scripts.git_guard._get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard._get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard._run_git_silent") as mock_git_silent:
                    mock_git_silent.return_value = "src/any.py"
                    with patch("scripts.git_guard._passthrough", return_value=0) as mock_pass:
                        exit_code = check_and_execute(["reset", "--hard", "HEAD~1"])
        assert exit_code == 0, "损坏 registry 应安全透传"
        mock_pass.assert_called_once()

    def test_no_ailocks_dir_allowed(self, temp_git_repo):
        """无 .ailocks 目录 → 允许透传"""
        from scripts.git_guard import check_and_execute  # noqa: F401 (top-level import)

        # 删除 .ailocks 目录
        import shutil
        shutil.rmtree(temp_git_repo / ".ailocks", ignore_errors=True)

        with patch("scripts.git_guard._get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard._get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard._run_git_silent") as mock_git_silent:
                    mock_git_silent.return_value = "src/any.py"
                    with patch("scripts.git_guard._passthrough", return_value=0) as mock_pass:
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
                with patch("scripts.git_guard._get_project_root", return_value=temp_git_repo):
                    with patch("scripts.git_guard._get_session_id", return_value="session-me-456"):
                        with patch("scripts.git_guard._run_git_silent") as mock_git_silent:
                            mock_git_silent.return_value = "src/important.py"
                            with patch("scripts.git_guard._passthrough", return_value=0):
                                return check_and_execute(["reset", "--hard", "HEAD~1"])
            except Exception as e:
                return e

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
        (temp_git_repo / ".ailocks" / "registry.json").write_text(
            json.dumps(registry), encoding="utf-8"
        )

        results = {"blocked": 0, "allowed": 0}
        lock = threading.Lock()

        def call_reset_locked():
            with patch("scripts.git_guard._get_project_root", return_value=temp_git_repo):
                with patch("scripts.git_guard._get_session_id", return_value="session-me"):
                    with patch("scripts.git_guard._run_git_silent") as mock_git_silent:
                        mock_git_silent.return_value = "src/locked.py"
                        with patch("scripts.git_guard._passthrough", return_value=0):
                            return check_and_execute(["reset", "--hard", "HEAD~1"])

        def call_reset_free():
            with patch("scripts.git_guard._get_project_root", return_value=temp_git_repo):
                with patch("scripts.git_guard._get_session_id", return_value="session-me"):
                    with patch("scripts.git_guard._run_git_silent") as mock_git_silent:
                        mock_git_silent.return_value = "src/free.py"
                        with patch("scripts.git_guard._passthrough", return_value=0):
                            return check_and_execute(["reset", "--hard", "HEAD~1"])

        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = []
            for _ in range(5):
                futures.append(pool.submit(call_reset_locked))
            for _ in range(5):
                futures.append(pool.submit(call_reset_free))
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

        with patch("scripts.git_guard._get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard._get_session_id", return_value="session-me-456"):
                with patch("scripts.git_guard._run_git_silent") as mock_git_silent:
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

        with patch("scripts.git_guard._get_project_root", return_value=temp_git_repo):
            with patch("scripts.git_guard._get_session_id", return_value="session-me"):
                with patch("scripts.git_guard._run_git_silent") as mock_git_silent:
                    mock_git_silent.return_value = "src/free.py"
                    with patch("scripts.git_guard._passthrough", side_effect=_passthrough_in_temp):
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
        """验证所有危险子命令都有对应的文件提取器"""
        # DANGEROUS_SUBCOMMANDS 和 _EXTRACTORS 已在顶部导入

        for cmd in DANGEROUS_SUBCOMMANDS:
            assert cmd in _EXTRACTORS, f"危险命令 {cmd} 缺少文件提取器"

    def test_concurrency_guard_scan_correctness(self, temp_git_repo, other_session_lock):
        """验证 concurrency_guard 扫描结果正确"""
        locks = scan_active_locks(temp_git_repo)
        assert len(locks) == 1
        assert locks[0].file_path == "src/important.py"
        assert locks[0].owner_id == "session-other-123"
        assert locks[0].task == "editing important file"

    def test_session_id_isolation(self, temp_git_repo, other_session_lock):
        """验证 session_id 隔离：其他 session 的锁对本 session 是冲突"""
        from zephyr.infrastructure.rollback.concurrency_guard import check_rollback_conflict

        # 本 session 检查 → 冲突
        result = check_rollback_conflict(
            ["src/important.py"], "session-me", temp_git_repo
        )
        assert result.has_conflict
        assert "src/important.py" in result.blocked_files

        # 其他 session 检查自己的锁 → 无冲突
        result2 = check_rollback_conflict(
            ["src/important.py"], "session-other-123", temp_git_repo
        )
        assert not result2.has_conflict
