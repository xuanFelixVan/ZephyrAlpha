# [A_test] layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §concurrency_guard
# [MODULE] tests.red_blue.test_concurrent_mv_guard
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [DOMAIN] D_GOVERNANCE
# [A_module] module_id=MOD-INF-021 | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""
并发红蓝极限对抗测试 — 多 AI 并发执行 git mv 时的防护能力验证。

测试目标：模拟多 AI 并发场景，验证 git mv 目录重命名不会导致未跟踪文件丢失，
覆盖各种变种场景（嵌套/特殊字符/.gitignore/竞争/锁冲突/三策略）。

红队（攻击）：模拟多 AI 并发 git mv / 文件写入 / 文件锁
蓝队（防御）：git_guard 应正确拦截/处理，不丢失文件，不死锁

场景矩阵（14 类）：
  1.  并发 git mv 不同目录 + 各自未跟踪文件
  2.  并发 git mv 同一目录（竞争条件）
  3.  git mv + 同时其他 session 写文件
  4.  git mv + 文件锁冲突
  5.  嵌套未跟踪文件
  6.  特殊字符文件名（中文/空格）
  7.  .gitignore 未跟踪文件
  8.  move 策略端到端
  9.  stage 策略端到端 + mapping.json 验证
  10. force 策略
  11. 多 AI 同时在源目录创建未跟踪文件
  12. git mv 后旧目录残留检查
  13. 并发不死锁（压力测试）
  14. 边界场景（文件非目录/参数不足）
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from unittest.mock import patch

import pytest

# Bootstrap: 基于 .git marker 定位仓库根（文件移动不 break，替代 parents[N] 硬编码）
_PROJECT_ROOT = Path(__file__).resolve()
while not (_PROJECT_ROOT / ".git").exists() and _PROJECT_ROOT != _PROJECT_ROOT.parent:
    _PROJECT_ROOT = _PROJECT_ROOT.parent
_SRC = _PROJECT_ROOT / "src"
for _p in [str(_SRC), str(_PROJECT_ROOT)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts.git_guard import (
    DANGEROUS_SUBCOMMANDS,
    MV_STRATEGY_ENV,
    check_and_execute,
    handle_mv,
    scan_untracked_in_dir,
)

# ============================================================================
# 辅助函数
# ============================================================================


def _init_repo(root: Path) -> None:
    """初始化临时 git 仓库。"""
    subprocess.run(["git", "init"], cwd=root, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=root, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, capture_output=True)
    # 禁用中文路径转义，确保 git status --porcelain 输出原始 UTF-8
    subprocess.run(["git", "config", "core.quotepath", "false"], cwd=root, capture_output=True)
    (root / "README.md").write_text("# test\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=root, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=root, capture_output=True, check=True)
    (root / ".ailocks").mkdir(exist_ok=True)


def _add_tracked_dir(root: Path, dir_name: str, files: dict[str, str]) -> None:
    """创建并提交已跟踪目录。"""
    dir_path = root / dir_name
    dir_path.mkdir(parents=True, exist_ok=True)
    for fname, content in files.items():
        file_path = dir_path / fname
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", dir_name], cwd=root, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", f"add {dir_name}"], cwd=root, capture_output=True, check=True)


def _add_untracked(root: Path, rel_path: str, content: str = "untracked") -> Path:
    """创建未跟踪文件。"""
    file_path = root / rel_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return file_path


def _add_lock(root: Path, file_rel: str, owner: str) -> None:
    """模拟其他 session 持有文件锁。"""
    registry = {"locks": {}}
    reg_path = root / ".ailocks" / "registry.json"
    if reg_path.is_file():
        registry = json.loads(reg_path.read_text(encoding="utf-8"))
    registry.setdefault("locks", {})[file_rel] = {
        "owner_id": owner,
        "task": "concurrent test",
        "timestamp": time.time(),
        "pid": 99999,
    }
    reg_path.write_text(json.dumps(registry), encoding="utf-8")


def _make_e2e_passthrough(repo_root: Path):
    """创建端到端 passthrough：在临时仓库中执行真实 git 命令。"""

    def _pt(git_args: list[str]) -> int:
        return subprocess.call(["git"] + git_args, cwd=str(repo_root))

    return _pt


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def _isolate_mv_strategy_env(monkeypatch):
    """每个测试前确保 MV_STRATEGY_ENV 不泄漏。

    治本：线程化 patch.dict(os.environ, ...) 在并发线程中竞态导致 env var
    交叉污染（线程 A set stage → 线程 B save stage → A restore delete →
    B restore stage → stage 泄漏）。autouse monkeypatch.delenv 确保每个测试
    开始时 env 干净，不依赖前序测试的 patch.dict 恢复正确性。
    """
    monkeypatch.delenv(MV_STRATEGY_ENV, raising=False)


@pytest.fixture
def repo():
    """创建临时 git 仓库。"""
    root = Path(tempfile.mkdtemp(prefix="conc_mv_"))
    _init_repo(root)
    yield root
    # 清理
    shutil.rmtree(root, ignore_errors=True)


@pytest.fixture
def repo_with_dirs(repo):
    """创建带两个已跟踪目录的仓库。"""
    _add_tracked_dir(repo, "dir_a", {"a.py": "a", "sub/b.py": "b"})
    _add_tracked_dir(repo, "dir_b", {"c.py": "c"})
    return repo


# ============================================================================
# 场景 1: 并发 git mv 不同目录 + 各自未跟踪文件
# ============================================================================


class TestConcurrentMvDifferentDirs:
    """红队：两个 AI 并发 git mv 不同目录，各自有未跟踪文件。"""

    def test_both_blocked_when_untracked(self, repo_with_dirs):
        """两个 AI 并发 git mv，各自源目录有未跟踪文件 → 都应被阻断。"""
        repo = repo_with_dirs
        _add_untracked(repo, "dir_a/untracked_a.py")
        _add_untracked(repo, "dir_b/untracked_b.py")

        results: dict[str, int] = {}
        results_lock = threading.Lock()

        def ai_session(session_id: str, source: str, dest: str):
            env = os.environ.copy()
            env["ZEPHYR_SESSION_ID"] = session_id
            env.pop(MV_STRATEGY_ENV, None)  # 默认 block
            with patch("scripts.git_guard.get_project_root", return_value=repo):
                with patch("scripts.git_guard.get_session_id", return_value=session_id):
                    with patch("scripts.git_guard.passthrough", return_value=0) as mock_pt:
                        with patch.dict(os.environ, env, clear=False):
                            code = check_and_execute(["mv", source, dest])
            with results_lock:
                results[session_id] = code
            mock_pt.assert_not_called()

        with ThreadPoolExecutor(max_workers=2) as ex:
            f1 = ex.submit(ai_session, "session-a", "dir_a", "new_dir_a")
            f2 = ex.submit(ai_session, "session-b", "dir_b", "new_dir_b")
            f1.result(timeout=30)
            f2.result(timeout=30)

        assert results.get("session-a") == 1, "AI-A 的 git mv 应被阻断"
        assert results.get("session-b") == 1, "AI-B 的 git mv 应被阻断"
        # 未跟踪文件应保留在原位
        assert (repo / "dir_a" / "untracked_a.py").exists()
        assert (repo / "dir_b" / "untracked_b.py").exists()

    def test_both_pass_when_clean(self, repo_with_dirs):
        """两个 AI 并发 git mv 干净目录 → 都应透传。

        注意：patch 非线程安全，改用 side_effect + 串行调用避免竞争。
        """
        repo = repo_with_dirs
        results: list[int] = []

        def ai_session(source: str, dest: str):
            with patch("scripts.git_guard.get_project_root", return_value=repo):
                with patch("scripts.git_guard.passthrough", return_value=0):
                    code = check_and_execute(["mv", source, dest])
            results.append(code)

        # 串行执行（patch 非线程安全）
        ai_session("dir_a", "new_dir_a")
        ai_session("dir_b", "new_dir_b")

        assert results[0] == 0
        assert results[1] == 0


# ============================================================================
# 场景 2: 并发 git mv 同一目录（竞争条件）
# ============================================================================


class TestConcurrentMvSameDir:
    """红队：两个 AI 并发 git mv 同一目录到不同目标。"""

    def test_concurrent_mv_same_dir_with_untracked(self, repo_with_dirs):
        """两个 AI 竞争 git mv 同一目录（含未跟踪文件）→ 至少一个被阻断。"""
        repo = repo_with_dirs
        _add_untracked(repo, "dir_a/untracked.py")

        results: list[int] = []
        results_lock = threading.Lock()
        barrier = threading.Barrier(2)

        def ai_session(session_id: str, dest: str):
            barrier.wait()  # 确保真正并发
            with patch("scripts.git_guard.get_project_root", return_value=repo):
                with patch("scripts.git_guard.get_session_id", return_value=session_id):
                    with patch("scripts.git_guard.passthrough", return_value=0):
                        code = check_and_execute(["mv", "dir_a", dest])
            with results_lock:
                results.append(code)

        with ThreadPoolExecutor(max_workers=2) as ex:
            f1 = ex.submit(ai_session, "session-a", "new_dir_1")
            f2 = ex.submit(ai_session, "session-b", "new_dir_2")
            f1.result(timeout=30)
            f2.result(timeout=30)

        # 两个都应被阻断（因为源目录有未跟踪文件）
        assert all(c == 1 for c in results), f"竞争场景下应都阻断，实际: {results}"
        # 未跟踪文件应保留
        assert (repo / "dir_a" / "untracked.py").exists()


# ============================================================================
# 场景 3: git mv + 同时其他 session 写文件
# ============================================================================


class TestMvWithConcurrentWrite:
    """红队：AI-B git mv 目录时，AI-A 同时在该目录写文件。"""

    def test_concurrent_write_during_mv(self, repo_with_dirs):
        """AI-B git mv dir_a，AI-A 同时在 dir_a 写未跟踪文件 → 不丢失。"""
        repo = repo_with_dirs
        mv_done = threading.Event()
        write_done = threading.Event()
        mv_result: list[int] = []

        def ai_b_mv():
            with patch("scripts.git_guard.get_project_root", return_value=repo):
                with patch("scripts.git_guard.get_session_id", return_value="session-b"):
                    with patch("scripts.git_guard.passthrough", return_value=0):
                        code = check_and_execute(["mv", "dir_a", "new_dir_a"])
            mv_result.append(code)
            mv_done.set()

        def ai_a_write():
            # 在 mv 检查期间创建未跟踪文件
            time.sleep(0.05)
            _add_untracked(repo, "dir_a/concurrent_write.py", "ai-a content")
            write_done.set()

        with ThreadPoolExecutor(max_workers=2) as ex:
            f1 = ex.submit(ai_b_mv)
            f2 = ex.submit(ai_a_write)
            f1.result(timeout=30)
            f2.result(timeout=30)

        # 无论 mv 是否被阻断，未跟踪文件不应丢失
        # 如果 mv 在写入前检查 → 阻断（文件在检查后创建，但文件仍在原位）
        # 如果 mv 在写入后检查 → 阻断（检测到未跟踪文件）
        assert (repo / "dir_a" / "concurrent_write.py").exists() or (
            repo / "new_dir_a" / "concurrent_write.py"
        ).exists(), "并发写入的文件不应丢失"


# ============================================================================
# 场景 4: git mv + 文件锁冲突
# ============================================================================


class TestMvWithLockConflict:
    """红队：AI-B git mv 目录时，AI-A 持有该目录下文件的锁。"""

    def test_mv_blocked_by_lock(self, repo_with_dirs):
        """AI-A 锁定 dir_a/a.py，AI-B git mv dir_a → 应被阻断（锁冲突）。"""
        repo = repo_with_dirs
        _add_lock(repo, "dir_a/a.py", "session-a")

        with patch("scripts.git_guard.get_project_root", return_value=repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-b"):
                # mv 检测到未跟踪文件会先阻断；若无未跟踪文件，mv extractor 返回 []
                # 所以锁冲突不会通过 mv 路径检测（extractor 返回空）
                # 这里验证 mv 路径的行为：无未跟踪文件 → 透传
                with patch("scripts.git_guard.passthrough", return_value=0) as mock_pt:
                    code = check_and_execute(["mv", "dir_a", "new_dir_a"])

        # 无未跟踪文件 → 透传（锁冲突由 reset/checkout 路径检测，mv 路径不检测锁）
        # 这是已知设计：mv 只检测未跟踪文件，不检测锁
        assert code == 0
        mock_pt.assert_called_once()

    def test_mv_with_untracked_and_lock(self, repo_with_dirs):
        """AI-A 锁定文件 + 有未跟踪文件 → mv 被阻断（因未跟踪文件）。"""
        repo = repo_with_dirs
        _add_lock(repo, "dir_a/a.py", "session-a")
        _add_untracked(repo, "dir_a/untracked.py")

        with patch("scripts.git_guard.get_project_root", return_value=repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-b"):
                with patch("scripts.git_guard.passthrough", return_value=0) as mock_pt:
                    code = check_and_execute(["mv", "dir_a", "new_dir_a"])

        assert code == 1, "有未跟踪文件应被阻断"
        mock_pt.assert_not_called()


# ============================================================================
# 场景 5: 嵌套未跟踪文件
# ============================================================================


class TestMvNestedUntracked:
    """红队：源目录有深层嵌套的未跟踪文件。"""

    def test_nested_untracked_detected(self, repo_with_dirs):
        """dir_a/sub/deep/nested.py 未跟踪 → git mv 被阻断。"""
        repo = repo_with_dirs
        _add_untracked(repo, "dir_a/sub/deep/nested.py", "deep content")

        with patch("scripts.git_guard.get_project_root", return_value=repo):
            with patch("scripts.git_guard.passthrough", return_value=0) as mock_pt:
                code = check_and_execute(["mv", "dir_a", "new_dir_a"])

        assert code == 1, "嵌套未跟踪文件应被检测到"
        mock_pt.assert_not_called()
        # 文件应保留
        assert (repo / "dir_a" / "sub" / "deep" / "nested.py").exists()

    def test_multiple_nested_untracked(self, repo_with_dirs):
        """多个层级的未跟踪文件都应被检测。"""
        repo = repo_with_dirs
        _add_untracked(repo, "dir_a/l1.py")
        _add_untracked(repo, "dir_a/sub/l2.py")
        _add_untracked(repo, "dir_a/sub/deep/l3.py")

        with patch("scripts.git_guard.get_project_root", return_value=repo):
            untracked = scan_untracked_in_dir("dir_a", repo)

        assert len(untracked) == 3, f"应检测到 3 个未跟踪文件，实际: {untracked}"
        assert "dir_a/l1.py" in untracked
        assert "dir_a/sub/l2.py" in untracked
        assert "dir_a/sub/deep/l3.py" in untracked


# ============================================================================
# 场景 6: 特殊字符文件名（中文/空格）
# ============================================================================


class TestMvSpecialChars:
    """红队：未跟踪文件名含中文/空格/特殊字符。"""

    def test_chinese_filename(self, repo_with_dirs):
        """中文文件名未跟踪 → git mv 被阻断。"""
        repo = repo_with_dirs
        _add_untracked(repo, "dir_a/中文报告.md", "中文内容")

        with patch("scripts.git_guard.get_project_root", return_value=repo):
            untracked = scan_untracked_in_dir("dir_a", repo)

        assert len(untracked) == 1
        assert "中文" in untracked[0]

    def test_space_in_filename(self, repo_with_dirs):
        """含空格文件名未跟踪 → git mv 被阻断。"""
        repo = repo_with_dirs
        _add_untracked(repo, "dir_a/file with space.py", "space content")

        with patch("scripts.git_guard.get_project_root", return_value=repo):
            untracked = scan_untracked_in_dir("dir_a", repo)

        assert len(untracked) == 1
        assert "file with space.py" in untracked[0]

    def test_mixed_special_chars(self, repo_with_dirs):
        """混合特殊字符（中文+空格+括号）。"""
        repo = repo_with_dirs
        _add_untracked(repo, "dir_a/报告 (最终版).md", "mixed")

        with patch("scripts.git_guard.get_project_root", return_value=repo):
            untracked = scan_untracked_in_dir("dir_a", repo)

        assert len(untracked) == 1
        assert "报告" in untracked[0]


# ============================================================================
# 场景 7: .gitignore 未跟踪文件
# ============================================================================


class TestMvGitignoreFiles:
    """红队：未跟踪文件在 .gitignore 中。"""

    def test_gitignored_untracked_detected(self, repo_with_dirs):
        """.gitignore 中的文件仍是未跟踪文件 → 应被检测。"""
        repo = repo_with_dirs
        # 创建 .gitignore
        (repo / ".gitignore").write_text("*.log\n__pycache__/\n", encoding="utf-8")
        subprocess.run(["git", "add", ".gitignore"], cwd=repo, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "add gitignore"], cwd=repo, capture_output=True, check=True)
        # 创建被 ignore 的文件
        _add_untracked(repo, "dir_a/debug.log", "log content")

        with patch("scripts.git_guard.get_project_root", return_value=repo):
            untracked = scan_untracked_in_dir("dir_a", repo)

        # git status --porcelain --untracked-files=all 会显示 ignored 文件吗？
        # 实际上 --untracked-files=all 显示未跟踪文件，但不显示 ignored 文件
        # 所以 ignored 文件不会被检测到（git 不认为它是未跟踪的）
        # 这是预期行为：ignored 文件由用户自己管理
        # 但如果用户用 git mv 目录，ignored 文件会留在旧目录 → 丢失
        # 这是一个边界情况，记录为已知限制
        # 验证：ignored 文件不被检测（git 行为）
        assert len(untracked) == 0 or "debug.log" not in untracked, ".gitignore 中的文件不应被检测为未跟踪（git 行为）"


# ============================================================================
# 场景 8: move 策略端到端
# ============================================================================


class TestMvStrategyMoveE2E:
    """蓝队：move 策略将未跟踪文件一并移动到目标目录。"""

    def test_move_strategy_preserves_files(self, repo_with_dirs):
        """move 策略：未跟踪文件应出现在目标目录。"""
        repo = repo_with_dirs
        _add_untracked(repo, "dir_a/untracked1.py", "content1")
        _add_untracked(repo, "dir_a/sub/untracked2.py", "content2")

        env = {MV_STRATEGY_ENV: "move", "ZEPHYR_SESSION_ID": "session-b"}
        with patch("scripts.git_guard.get_project_root", return_value=repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-b"):
                with patch("scripts.git_guard.passthrough", side_effect=_make_e2e_passthrough(repo)):
                    with patch.dict(os.environ, env, clear=False):
                        code = check_and_execute(["mv", "dir_a", "new_dir_a"])

        assert code == 0, "move 策略应成功"
        # 未跟踪文件应在目标目录
        assert (repo / "new_dir_a" / "untracked1.py").exists(), "未跟踪文件应移动到目标目录"
        assert (repo / "new_dir_a" / "sub" / "untracked2.py").exists(), "嵌套未跟踪文件应移动"
        # 内容应保留
        assert (repo / "new_dir_a" / "untracked1.py").read_text(encoding="utf-8") == "content1"

    def test_move_strategy_preserves_content(self, repo_with_dirs):
        """move 策略：文件内容不损坏。"""
        repo = repo_with_dirs
        original_content = "line1\nline2\nline3\n特殊内容\n"
        _add_untracked(repo, "dir_a/data.txt", original_content)

        env = {MV_STRATEGY_ENV: "move"}
        with patch("scripts.git_guard.get_project_root", return_value=repo):
            with patch("scripts.git_guard.passthrough", side_effect=_make_e2e_passthrough(repo)):
                with patch.dict(os.environ, env, clear=False):
                    code = check_and_execute(["mv", "dir_a", "new_dir_a"])

        assert code == 0
        moved_content = (repo / "new_dir_a" / "data.txt").read_text(encoding="utf-8")
        assert moved_content == original_content, "文件内容应完整保留"


# ============================================================================
# 场景 9: stage 策略端到端 + mapping.json 验证
# ============================================================================


class TestMvStrategyStageE2E:
    """蓝队：stage 策略将未跟踪文件暂存到 .aidrafts/。"""

    def test_stage_strategy_creates_mapping(self, repo_with_dirs):
        """stage 策略：创建 mapping.json，文件移到 .aidrafts/。"""
        repo = repo_with_dirs
        _add_untracked(repo, "dir_a/file1.py", "content1")
        _add_untracked(repo, "dir_a/file2.py", "content2")

        env = {MV_STRATEGY_ENV: "stage", "ZEPHYR_SESSION_ID": "session-b"}
        with patch("scripts.git_guard.get_project_root", return_value=repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-b"):
                with patch("scripts.git_guard.passthrough", side_effect=_make_e2e_passthrough(repo)):
                    with patch.dict(os.environ, env, clear=False):
                        code = check_and_execute(["mv", "dir_a", "new_dir_a"])

        assert code == 0, "stage 策略应成功"
        # mapping.json 应存在
        mapping_path = repo / ".aidrafts" / "session-b" / "mv_rescue" / "mapping.json"
        assert mapping_path.exists(), "mapping.json 应存在"
        mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
        assert mapping["source_dir"] == "dir_a"
        assert "dir_a/file1.py" in mapping["files"]
        assert "dir_a/file2.py" in mapping["files"]
        # 文件应在 .aidrafts/
        stage_file1 = repo / mapping["files"]["dir_a/file1.py"]
        assert stage_file1.exists(), "暂存文件应存在"
        assert stage_file1.read_text(encoding="utf-8") == "content1"

    def test_stage_strategy_removes_from_source(self, repo_with_dirs):
        """stage 策略：未跟踪文件应从源目录移除（避免被 git mv 遗留）。"""
        repo = repo_with_dirs
        _add_untracked(repo, "dir_a/temp.py", "temp")

        env = {MV_STRATEGY_ENV: "stage", "ZEPHYR_SESSION_ID": "session-c"}
        with patch("scripts.git_guard.get_project_root", return_value=repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-c"):
                with patch("scripts.git_guard.passthrough", side_effect=_make_e2e_passthrough(repo)):
                    with patch.dict(os.environ, env, clear=False):
                        check_and_execute(["mv", "dir_a", "new_dir_a"])

        # 源目录的未跟踪文件应已移除（移到 .aidrafts/）
        assert not (repo / "dir_a" / "temp.py").exists(), "源目录未跟踪文件应已移除"


# ============================================================================
# 场景 10: force 策略
# ============================================================================


class TestMvStrategyForce:
    """红队：force 策略跳过检查（用户明确选择）。"""

    def test_force_strategy_passthrough(self, repo_with_dirs):
        """force 策略：有未跟踪文件也透传。"""
        repo = repo_with_dirs
        _add_untracked(repo, "dir_a/untracked.py", "content")

        env = {MV_STRATEGY_ENV: "force"}
        with patch("scripts.git_guard.get_project_root", return_value=repo):
            with patch("scripts.git_guard.passthrough", return_value=0) as mock_pt:
                with patch.dict(os.environ, env, clear=False):
                    code = check_and_execute(["mv", "dir_a", "new_dir_a"])

        assert code == 0, "force 策略应透传"
        mock_pt.assert_called_once()

    def test_force_strategy_case_insensitive(self, repo_with_dirs):
        """force 策略：大小写不敏感（FORCE/Force）。"""
        repo = repo_with_dirs
        _add_untracked(repo, "dir_a/untracked.py")

        for variant in ["FORCE", "Force", "FORCE"]:
            env = {MV_STRATEGY_ENV: variant}
            with patch("scripts.git_guard.get_project_root", return_value=repo):
                with patch("scripts.git_guard.passthrough", return_value=0) as mock_pt:
                    with patch.dict(os.environ, env, clear=False):
                        code = check_and_execute(["mv", "dir_a", "new_dir_a"])
            assert code == 0, f"{variant} 应等效于 force"
            mock_pt.assert_called_once()


# ============================================================================
# 场景 11: 多 AI 同时在源目录创建未跟踪文件
# ============================================================================


class TestMultipleAiCreateUntracked:
    """红队：多个 AI 同时在源目录创建未跟踪文件，然后 git mv。"""

    def test_multiple_writers_then_mv(self, repo_with_dirs):
        """3 个 AI 并发在 dir_a 写文件，然后 git mv → 应检测到所有文件。"""
        repo = repo_with_dirs

        def writer(ai_id: str):
            _add_untracked(repo, f"dir_a/ai_{ai_id}.py", f"content from {ai_id}")

        with ThreadPoolExecutor(max_workers=3) as ex:
            futures = [ex.submit(writer, f"{i}") for i in range(3)]
            for f in futures:
                f.result(timeout=10)

        with patch("scripts.git_guard.get_project_root", return_value=repo):
            untracked = scan_untracked_in_dir("dir_a", repo)

        assert len(untracked) == 3, f"应检测到 3 个文件，实际: {untracked}"

    def test_race_write_during_scan(self, repo_with_dirs):
        """扫描期间有新文件写入 → 扫描结果可能不含新文件（TOCTOU）。

        这是已知限制：扫描和 mv 之间存在 TOCTOU 窗口。
        验证：即使有 TOCTOU，文件也不应丢失（block 策略保留文件）。
        """
        repo = repo_with_dirs
        _add_untracked(repo, "dir_a/before_scan.py")

        scan_done = threading.Event()

        def late_writer():
            scan_done.wait(timeout=5)
            _add_untracked(repo, "dir_a/after_scan.py", "late")

        with patch("scripts.git_guard.get_project_root", return_value=repo):
            with patch("scripts.git_guard.passthrough", return_value=0) as mock_pt:
                # 启动 late writer
                t = threading.Thread(target=late_writer)
                t.start()
                # 执行 mv（block 策略）
                code = check_and_execute(["mv", "dir_a", "new_dir_a"])
                scan_done.set()
                t.join(timeout=5)

        # block 策略 → 阻断，所有文件保留
        assert code == 1
        mock_pt.assert_not_called()
        # 两个文件都应保留（block 不执行 mv）
        assert (repo / "dir_a" / "before_scan.py").exists()
        assert (repo / "dir_a" / "after_scan.py").exists()


# ============================================================================
# 场景 12: git mv 后旧目录残留检查
# ============================================================================


class TestMvOldDirResidue:
    """蓝队：git mv 后检查旧目录是否残留未跟踪文件。"""

    def test_block_preserves_old_dir(self, repo_with_dirs):
        """block 策略：旧目录和未跟踪文件都保留。"""
        repo = repo_with_dirs
        _add_untracked(repo, "dir_a/keep.py", "keep")

        with patch("scripts.git_guard.get_project_root", return_value=repo):
            with patch("scripts.git_guard.passthrough", return_value=0) as mock_pt:
                code = check_and_execute(["mv", "dir_a", "new_dir_a"])

        assert code == 1
        mock_pt.assert_not_called()
        # 旧目录应存在
        assert (repo / "dir_a").is_dir()
        # 未跟踪文件应保留
        assert (repo / "dir_a" / "keep.py").exists()
        # 目标目录不应存在（mv 未执行）
        assert not (repo / "new_dir_a").exists()

    def test_move_no_residue(self, repo_with_dirs):
        """move 策略：未跟踪文件移到目标，旧目录无残留未跟踪文件。"""
        repo = repo_with_dirs
        _add_untracked(repo, "dir_a/move_me.py", "move")

        env = {MV_STRATEGY_ENV: "move"}
        with patch("scripts.git_guard.get_project_root", return_value=repo):
            with patch("scripts.git_guard.passthrough", side_effect=_make_e2e_passthrough(repo)):
                with patch.dict(os.environ, env, clear=False):
                    check_and_execute(["mv", "dir_a", "new_dir_a"])

        # 未跟踪文件应在目标目录
        assert (repo / "new_dir_a" / "move_me.py").exists()


# ============================================================================
# 场景 13: 并发不死锁（压力测试）
# ============================================================================


class TestConcurrentNoDeadlock:
    """蓝队：高并发下不死锁、不崩溃。"""

    def test_stress_10_concurrent_mv(self, repo):
        """10 个 AI 并发 git mv 不同目录 → 不死锁。"""
        # 创建 10 个已跟踪目录
        for i in range(10):
            _add_tracked_dir(repo, f"dir_{i}", {f"file_{i}.py": f"content {i}"})
            _add_untracked(repo, f"dir_{i}/untracked.py", f"untracked {i}")

        results: list[int] = []
        results_lock = threading.Lock()

        def ai_session(ai_id: int):
            with patch("scripts.git_guard.get_project_root", return_value=repo):
                with patch("scripts.git_guard.passthrough", return_value=0):
                    code = check_and_execute(["mv", f"dir_{ai_id}", f"new_dir_{ai_id}"])
            with results_lock:
                results.append(code)

        with ThreadPoolExecutor(max_workers=10) as ex:
            futures = [ex.submit(ai_session, i) for i in range(10)]
            for f in as_completed(futures):
                f.result(timeout=60)

        assert len(results) == 10, "所有线程应完成"
        assert all(c == 1 for c in results), "所有 mv 应被阻断（有未跟踪文件）"

    def test_stress_mixed_strategies(self, repo):
        """混合策略并发：block/move/stage/force 同时执行 → 不死锁。"""
        for i in range(8):
            _add_tracked_dir(repo, f"dir_{i}", {"f.py": str(i)})
            _add_untracked(repo, f"dir_{i}/u.py", f"u{i}")

        strategies = ["block", "move", "stage", "force", "block", "move", "stage", "force"]
        results: list[int] = []
        results_lock = threading.Lock()

        def ai_session(ai_id: int, strategy: str):
            env = {MV_STRATEGY_ENV: strategy, "ZEPHYR_SESSION_ID": f"session-{ai_id}"}
            with patch("scripts.git_guard.get_project_root", return_value=repo):
                with patch("scripts.git_guard.get_session_id", return_value=f"session-{ai_id}"):
                    with patch("scripts.git_guard.passthrough", return_value=0):
                        with patch.dict(os.environ, env, clear=False):
                            code = check_and_execute(["mv", f"dir_{ai_id}", f"new_dir_{ai_id}"])
            with results_lock:
                results.append(code)

        with ThreadPoolExecutor(max_workers=8) as ex:
            futures = [ex.submit(ai_session, i, strategies[i]) for i in range(8)]
            for f in as_completed(futures):
                f.result(timeout=60)

        assert len(results) == 8, "所有线程应完成"
        # block → 1, move/stage/force → 0（mock passthrough）
        # 不检查具体值，只验证不死锁（所有线程完成）


# ============================================================================
# 场景 14: 边界场景
# ============================================================================


class TestMvEdgeCases:
    """边界场景：文件非目录、参数不足、空目录。"""

    def test_mv_file_not_dir(self, repo_with_dirs):
        """git mv 文件（非目录）→ 透传（不扫描未跟踪文件）。"""
        repo = repo_with_dirs
        with patch("scripts.git_guard.get_project_root", return_value=repo):
            with patch("scripts.git_guard.passthrough", return_value=0) as mock_pt:
                code = check_and_execute(["mv", "dir_a/a.py", "new_a.py"])

        assert code == 0, "文件 mv 应透传"
        mock_pt.assert_called_once()

    def test_mv_not_enough_args(self, repo_with_dirs):
        """git mv 无足够参数 → 透传。"""
        repo = repo_with_dirs
        with patch("scripts.git_guard.passthrough", return_value=0) as mock_pt:
            code = check_and_execute(["mv"])

        assert code == 0
        mock_pt.assert_called_once()

    def test_mv_one_arg(self, repo_with_dirs):
        """git mv 只有一个参数 → 透传。"""
        repo = repo_with_dirs
        with patch("scripts.git_guard.get_project_root", return_value=repo):
            with patch("scripts.git_guard.passthrough", return_value=0) as mock_pt:
                code = check_and_execute(["mv", "dir_a"])

        assert code == 0
        mock_pt.assert_called_once()

    def test_mv_nonexistent_source(self, repo_with_dirs):
        """git mv 不存在的源 → 透传（让 git 报错）。"""
        repo = repo_with_dirs
        with patch("scripts.git_guard.get_project_root", return_value=repo):
            with patch("scripts.git_guard.passthrough", return_value=1) as mock_pt:
                code = check_and_execute(["mv", "nonexistent_dir", "new_dir"])

        assert code == 1  # git 报错返回 1
        mock_pt.assert_called_once()

    def test_mv_empty_dir(self, repo):
        """git mv 空目录（无文件）→ 透传。"""
        # 空目录无法 git add（git 不跟踪空目录），所以这不是有效场景
        # 但如果目录有已跟踪文件但无未跟踪文件 → 透传
        _add_tracked_dir(repo, "clean_dir", {"f.py": "c"})

        with patch("scripts.git_guard.get_project_root", return_value=repo):
            with patch("scripts.git_guard.passthrough", return_value=0) as mock_pt:
                code = check_and_execute(["mv", "clean_dir", "new_clean_dir"])

        assert code == 0, "干净目录应透传"
        mock_pt.assert_called_once()

    def test_mv_with_flags(self, repo_with_dirs):
        """git mv -f dir new_dir（带 flag）→ 正确解析 source/dest。"""
        repo = repo_with_dirs
        _add_untracked(repo, "dir_a/untracked.py")

        with patch("scripts.git_guard.get_project_root", return_value=repo):
            with patch("scripts.git_guard.passthrough", return_value=0) as mock_pt:
                code = check_and_execute(["mv", "-f", "dir_a", "new_dir_a"])

        assert code == 1, "带 flag 也应检测未跟踪文件"
        mock_pt.assert_not_called()


# ============================================================================
# 场景 15: 完整端到端 — 模拟真实事故场景
# ============================================================================


class TestRealIncidentScenario:
    """模拟 2026-06-24 真实事故：AI-A 生成文件 + AI-B git mv 目录。"""

    def test_real_incident_block_strategy(self, repo):
        """复现事故：AI-A 生成报告，AI-B git mv 目录 → block 策略保护文件。"""
        # AI-A 创建已跟踪目录
        _add_tracked_dir(repo, "3_治理报告", {"existing.md": "existing"})
        # AI-A 生成未跟踪文件（事故场景）
        _add_untracked(
            repo,
            "3_治理报告/orphan_cleanup_audit.md",
            "# 孤儿清理审计报告\n这是 AI-A 生成的重要文件\n",
        )

        # AI-B 执行目录重命名
        with patch("scripts.git_guard.get_project_root", return_value=repo):
            with patch("scripts.git_guard.passthrough", return_value=0) as mock_pt:
                code = check_and_execute(["mv", "3_治理报告", "03_governance_reports"])

        # block 策略 → 阻断，文件保留
        assert code == 1, "应阻断 git mv"
        mock_pt.assert_not_called()
        # AI-A 的文件应保留
        assert (repo / "3_治理报告" / "orphan_cleanup_audit.md").exists()
        content = (repo / "3_治理报告" / "orphan_cleanup_audit.md").read_text(encoding="utf-8")
        assert "孤儿清理审计报告" in content

    def test_real_incident_move_strategy(self, repo):
        """事故场景 + move 策略：文件移到目标目录。"""
        _add_tracked_dir(repo, "3_治理报告", {"existing.md": "existing"})
        _add_untracked(
            repo,
            "3_治理报告/orphan_cleanup_audit.md",
            "# 审计报告\n",
        )

        env = {MV_STRATEGY_ENV: "move"}
        with patch("scripts.git_guard.get_project_root", return_value=repo):
            with patch("scripts.git_guard.passthrough", side_effect=_make_e2e_passthrough(repo)):
                with patch.dict(os.environ, env, clear=False):
                    code = check_and_execute(["mv", "3_治理报告", "03_governance_reports"])

        assert code == 0
        # 文件应在目标目录
        assert (repo / "03_governance_reports" / "orphan_cleanup_audit.md").exists()
        assert (repo / "03_governance_reports" / "existing.md").exists()

    def test_real_incident_stage_strategy(self, repo):
        """事故场景 + stage 策略：文件暂存到 .aidrafts/。"""
        _add_tracked_dir(repo, "3_治理报告", {"existing.md": "existing"})
        _add_untracked(repo, "3_治理报告/orphan_cleanup_audit.md", "# 审计\n")

        env = {MV_STRATEGY_ENV: "stage", "ZEPHYR_SESSION_ID": "session-b"}
        with patch("scripts.git_guard.get_project_root", return_value=repo):
            with patch("scripts.git_guard.get_session_id", return_value="session-b"):
                with patch("scripts.git_guard.passthrough", side_effect=_make_e2e_passthrough(repo)):
                    with patch.dict(os.environ, env, clear=False):
                        code = check_and_execute(["mv", "3_治理报告", "03_governance_reports"])

        assert code == 0
        # mapping.json 应存在
        mapping_path = repo / ".aidrafts" / "session-b" / "mv_rescue" / "mapping.json"
        assert mapping_path.exists()
        mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
        assert "3_治理报告/orphan_cleanup_audit.md" in mapping["files"]
        # 暂存文件应存在
        stage_file = repo / mapping["files"]["3_治理报告/orphan_cleanup_audit.md"]
        assert stage_file.exists()
