# [A_test] module_id: MOD-GOV_git_batcher | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-003 | docs/03_modules/_domain_infrastructure/runtime_integration/blueprint.md | §ARCH-GIT-CALL-BUDGET
# [MODULE] tests.infrastructure.test_git_batcher
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] task_bound
"""test_git_batcher.py — GitCommandBatcher 批量化工具单测。

ARCH-GIT-CALL-BUDGET（trae_064 GIT-BUDGET-INV-002 批量化强制）。

覆盖:
1. git_show_batch: 批量获取文件内容（成功 / 空文件列表 / 不存在 ref / tar 解析失败）
2. git_diff_cached_names: 批量获取 staged 文件名
3. git_diff_names: 批量获取 diff 文件名
4. git_ls_files_tracked: 批量获取 tracked 文件
5. git_restore_batch: 批量还原文件（成功 / 空列表 / staged=True / 失败 fail-open / 超时 / 异常）
6. _parse_tar_archive: tar 解析（合法 tar / 损坏数据）

测试隔离: 真实 git subprocess + tmp_path 临时 git 仓库（end-to-end）。
"""
from __future__ import annotations

import io
import os
import subprocess
import sys
import tarfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_DIR = str(_PROJECT_ROOT / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from zephyr.infrastructure.git_batcher import GitCommandBatcher  # noqa: E402

# ============================================================================
# 辅助函数
# ============================================================================


def _git_env() -> dict:
    """构造 git 测试环境变量。"""
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@test.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@test.com"
    return env


def _init_git_repo(repo_dir: Path) -> None:
    """初始化最小 git 仓库（含初始 commit）。"""
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
    # 禁用 autocrlf——避免 Windows 上 git 自动将 \n 转 \r\n 导致内容比对失败
    subprocess.run(
        ["git", "config", "core.autocrlf", "false"],
        cwd=str(repo_dir), capture_output=True, env=env, check=True,
    )
    # 使用 write_bytes 避免 Windows write_text 的 \n→\r\n 自动转换
    (repo_dir / "README.md").write_bytes(b"init\n")
    subprocess.run(["git", "add", "README.md"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(repo_dir), capture_output=True, env=env, check=True)


def _commit_file(repo_dir: Path, path: str, content: str) -> None:
    """创建/修改文件并 commit 到 HEAD。"""
    env = _git_env()
    fpath = repo_dir / path
    fpath.parent.mkdir(parents=True, exist_ok=True)
    # 使用 write_bytes 避免 Windows write_text 的 \n→\r\n 自动转换
    # （否则 git archive 返回 \r\n 内容，断言 b"...\\n" 失败）
    fpath.write_bytes(content.encode("utf-8"))
    subprocess.run(["git", "add", path], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"add {path}"],
        cwd=str(repo_dir), capture_output=True, env=env, check=True,
    )


# ============================================================================
# git_show_batch 测试
# ============================================================================


class TestGitShowBatch:
    """git_show_batch 批量获取文件内容测试。"""

    def test_empty_files_returns_empty_dict(self, tmp_path):
        _init_git_repo(tmp_path)
        batcher = GitCommandBatcher(tmp_path)
        assert batcher.git_show_batch("HEAD", []) == {}

    def test_single_file_success(self, tmp_path):
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "src/foo.py", "content foo\n")
        batcher = GitCommandBatcher(tmp_path)
        result = batcher.git_show_batch("HEAD", ["src/foo.py"])
        assert "src/foo.py" in result
        assert result["src/foo.py"] == b"content foo\n"

    def test_multiple_files_success(self, tmp_path):
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "src/foo.py", "foo\n")
        _commit_file(tmp_path, "src/bar.py", "bar\n")
        batcher = GitCommandBatcher(tmp_path)
        result = batcher.git_show_batch("HEAD", ["src/foo.py", "src/bar.py"])
        assert result["src/foo.py"] == b"foo\n"
        assert result["src/bar.py"] == b"bar\n"

    def test_nonexistent_file_skipped(self, tmp_path):
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "src/foo.py", "foo\n")
        batcher = GitCommandBatcher(tmp_path)
        # git archive 对不存在的 pathspec 会返回非零退出码（fatal: pathspec did not match）
        # → git_show_batch fail-open 返回空字典（不是部分成功）
        # 这是预期行为——调用方应在调用前过滤已 tracked 的文件
        result = batcher.git_show_batch("HEAD", ["src/foo.py", "nonexistent.py"])
        # 混合 pathspec 中任一不存在 → 整体失败 → 空字典
        assert result == {}

    def test_nonexistent_ref_returns_empty(self, tmp_path):
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "src/foo.py", "foo\n")
        batcher = GitCommandBatcher(tmp_path)
        # 不存在的 ref → git archive 失败 → 空字典
        result = batcher.git_show_batch("NONEXISTENT_REF", ["src/foo.py"])
        assert result == {}

    def test_timeout_returns_empty_dict(self, tmp_path):
        _init_git_repo(tmp_path)
        batcher = GitCommandBatcher(tmp_path)
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="git", timeout=1)):
            result = batcher.git_show_batch("HEAD", ["src/foo.py"])
        assert result == {}

    def test_generic_exception_returns_empty_dict(self, tmp_path):
        _init_git_repo(tmp_path)
        batcher = GitCommandBatcher(tmp_path)
        with patch("subprocess.run", side_effect=OSError("disk full")):
            result = batcher.git_show_batch("HEAD", ["src/foo.py"])
        assert result == {}


# ============================================================================
# git_diff_cached_names 测试
# ============================================================================


class TestGitDiffCachedNames:
    """git_diff_cached_names 批量获取 staged 文件名测试。"""

    def test_no_staged_returns_empty(self, tmp_path):
        _init_git_repo(tmp_path)
        batcher = GitCommandBatcher(tmp_path)
        assert batcher.git_diff_cached_names() == []

    def test_returns_staged_files(self, tmp_path):
        _init_git_repo(tmp_path)
        (tmp_path / "src").mkdir(parents=True, exist_ok=True)
        (tmp_path / "src" / "foo.py").write_text("v1\n", encoding="utf-8")
        (tmp_path / "src" / "bar.py").write_text("v2\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "src/foo.py", "src/bar.py"],
            cwd=str(tmp_path), capture_output=True, env=_git_env(), check=True,
        )
        batcher = GitCommandBatcher(tmp_path)
        result = set(batcher.git_diff_cached_names())
        assert result == {"src/foo.py", "src/bar.py"}

    def test_timeout_returns_empty(self, tmp_path):
        _init_git_repo(tmp_path)
        batcher = GitCommandBatcher(tmp_path)
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="git", timeout=1)):
            assert batcher.git_diff_cached_names() == []


# ============================================================================
# git_diff_names 测试
# ============================================================================


class TestGitDiffNames:
    """git_diff_names 批量获取 diff 文件名测试。"""

    def test_no_diff_returns_empty(self, tmp_path):
        _init_git_repo(tmp_path)
        batcher = GitCommandBatcher(tmp_path)
        assert batcher.git_diff_names("HEAD") == []

    def test_returns_diff_files(self, tmp_path):
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "src/foo.py", "v1\n")
        # 修改但未 stage（worktree 与 HEAD 有 diff）
        (tmp_path / "src" / "foo.py").write_text("v2\n", encoding="utf-8")
        batcher = GitCommandBatcher(tmp_path)
        # ref_spec="HEAD" 比较 worktree 与 HEAD（无 ref_spec.. 形式时表示 HEAD 与 worktree）
        result = batcher.git_diff_names("HEAD")
        assert "src/foo.py" in result


# ============================================================================
# git_ls_files_tracked 测试
# ============================================================================


class TestGitLsFilesTracked:
    """git_ls_files_tracked 批量获取 tracked 文件测试。"""

    def test_returns_all_tracked_files(self, tmp_path):
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "src/foo.py", "foo\n")
        _commit_file(tmp_path, "src/bar.py", "bar\n")
        batcher = GitCommandBatcher(tmp_path)
        result = set(batcher.git_ls_files_tracked())
        assert "README.md" in result
        assert "src/foo.py" in result
        assert "src/bar.py" in result

    def test_filter_by_files(self, tmp_path):
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "src/foo.py", "foo\n")
        _commit_file(tmp_path, "src/bar.py", "bar\n")
        batcher = GitCommandBatcher(tmp_path)
        result = set(batcher.git_ls_files_tracked(["src/foo.py", "nonexistent.py"]))
        assert "src/foo.py" in result
        assert "nonexistent.py" not in result


# ============================================================================
# git_restore_batch 测试（核心：GIT-BUDGET-INV-002 合规验证）
# ============================================================================


class TestGitRestoreBatch:
    """git_restore_batch 批量还原文件测试。

    这是 trae_064 ARCH-GIT-CALL-BUDGET GIT-BUDGET-INV-002 批量化强制治本的核心方法。
    workspace_hygiene_reconciler 使用此方法替代 N 次逐文件 git restore。
    """

    def test_empty_files_returns_empty_list(self, tmp_path):
        _init_git_repo(tmp_path)
        batcher = GitCommandBatcher(tmp_path)
        assert batcher.git_restore_batch([]) == []

    def test_batch_success_returns_all_files(self, tmp_path):
        # 批量 restore 2 个文件成功 → 返回全部文件列表
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "src/foo.py", "v1\n")
        _commit_file(tmp_path, "src/bar.py", "v1\n")
        # 修改两个文件
        (tmp_path / "src" / "foo.py").write_text("v2\n", encoding="utf-8")
        (tmp_path / "src" / "bar.py").write_text("v2\n", encoding="utf-8")
        batcher = GitCommandBatcher(tmp_path)
        files = ["src/foo.py", "src/bar.py"]
        restored = batcher.git_restore_batch(files)
        # 应返回全部文件（returncode=0 时返回 list(files)）
        assert set(restored) == set(files)
        # 文件应被还原到 HEAD 版本
        assert (tmp_path / "src" / "foo.py").read_text(encoding="utf-8") == "v1\n"
        assert (tmp_path / "src" / "bar.py").read_text(encoding="utf-8") == "v1\n"

    def test_single_file_success(self, tmp_path):
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "src/foo.py", "v1\n")
        (tmp_path / "src" / "foo.py").write_text("v2\n", encoding="utf-8")
        batcher = GitCommandBatcher(tmp_path)
        restored = batcher.git_restore_batch(["src/foo.py"])
        assert restored == ["src/foo.py"]
        assert (tmp_path / "src" / "foo.py").read_text(encoding="utf-8") == "v1\n"

    def test_staged_true_unstages_files(self, tmp_path):
        # staged=True → `git restore --staged` 还原 staged 状态（unstage）
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "src/foo.py", "v1\n")
        # 修改并 stage
        (tmp_path / "src" / "foo.py").write_text("v2\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "src/foo.py"],
            cwd=str(tmp_path), capture_output=True, env=_git_env(), check=True,
        )
        batcher = GitCommandBatcher(tmp_path)
        restored = batcher.git_restore_batch(["src/foo.py"], staged=True)
        assert restored == ["src/foo.py"]
        # staged 状态被还原（worktree 仍 v2，但 staged 应为 v1）
        # git diff --cached 应为空
        r = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=str(tmp_path), capture_output=True, text=True, env=_git_env(),
        )
        assert r.stdout.strip() == ""

    def test_batch_failure_returns_empty_list(self, tmp_path):
        # git restore 失败（如文件不存在） → 返回空列表（fail-open，不逐个重试）
        _init_git_repo(tmp_path)
        batcher = GitCommandBatcher(tmp_path)
        # 不存在的文件 → git restore 返回非零 → 返回空列表
        restored = batcher.git_restore_batch(["nonexistent.py"])
        assert restored == []

    def test_batch_failure_does_not_retry_per_file(self, tmp_path):
        # 关键性质：批量失败不逐个重试（GIT-BUDGET-INV-002 反模式）
        # 即使部分文件存在，批量失败也返回空列表（依赖下次 post-commit 兜底）
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "src/foo.py", "v1\n")
        (tmp_path / "src" / "foo.py").write_text("v2\n", encoding="utf-8")
        batcher = GitCommandBatcher(tmp_path)
        # 混合存在与不存在的文件 → git restore 失败 → 返回空列表
        restored = batcher.git_restore_batch(["src/foo.py", "nonexistent.py"])
        assert restored == []
        # 注意：foo.py 未被还原（因为批量失败，不逐个重试）

    def test_timeout_returns_empty_list(self, tmp_path):
        _init_git_repo(tmp_path)
        batcher = GitCommandBatcher(tmp_path)
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="git", timeout=1)):
            restored = batcher.git_restore_batch(["src/foo.py"])
        assert restored == []

    def test_generic_exception_returns_empty_list(self, tmp_path):
        _init_git_repo(tmp_path)
        batcher = GitCommandBatcher(tmp_path)
        with patch("subprocess.run", side_effect=OSError("disk full")):
            restored = batcher.git_restore_batch(["src/foo.py"])
        assert restored == []

    def test_returns_list_of_input_files_on_success(self, tmp_path):
        # 验证 returncode=0 时返回的是 list(files) 副本
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "a.py", "v1\n")
        _commit_file(tmp_path, "b.py", "v1\n")
        _commit_file(tmp_path, "c.py", "v1\n")
        for f in ("a.py", "b.py", "c.py"):
            (tmp_path / f).write_text("v2\n", encoding="utf-8")
        batcher = GitCommandBatcher(tmp_path)
        files = ["a.py", "b.py", "c.py"]
        restored = batcher.git_restore_batch(files)
        # 验证返回是 list 且元素相同（顺序无关）
        assert isinstance(restored, list)
        assert set(restored) == set(files)
        # 验证返回的是副本，修改不影响原 list
        restored.append("d.py")
        assert "d.py" not in files


# ============================================================================
# _parse_tar_archive 测试
# ============================================================================


class TestParseTarArchive:
    """_parse_tar_archive tar 解析测试。"""

    def test_empty_tar_returns_empty_dict(self, tmp_path):
        _init_git_repo(tmp_path)
        batcher = GitCommandBatcher(tmp_path)
        # 空 tar → 空字典
        bio = io.BytesIO()
        with tarfile.open(fileobj=bio, mode="w|") as tar:
            pass  # 不添加任何成员
        empty_tar = bio.getvalue()
        result = batcher.parse_tar_archive(empty_tar)
        assert result == {}

    def test_corrupted_data_returns_empty_dict(self, tmp_path):
        _init_git_repo(tmp_path)
        batcher = GitCommandBatcher(tmp_path)
        # 非 tar 数据 → TarError → 空字典
        result = batcher.parse_tar_archive(b"not a tar file")
        assert result == {}

    def test_valid_tar_with_files(self, tmp_path):
        _init_git_repo(tmp_path)
        batcher = GitCommandBatcher(tmp_path)
        # 构造合法 tar
        bio = io.BytesIO()
        with tarfile.open(fileobj=bio, mode="w|") as tar:
            for name, content in [("foo.py", b"foo\n"), ("bar.py", b"bar\n")]:
                info = tarfile.TarInfo(name=name)
                info.size = len(content)
                tar.addfile(info, io.BytesIO(content))
        tar_bytes = bio.getvalue()
        result = batcher.parse_tar_archive(tar_bytes)
        assert result["foo.py"] == b"foo\n"
        assert result["bar.py"] == b"bar\n"

    def test_skips_directories(self, tmp_path):
        _init_git_repo(tmp_path)
        batcher = GitCommandBatcher(tmp_path)
        # tar 中的目录条目应被跳过（只取 isfile()）
        bio = io.BytesIO()
        with tarfile.open(fileobj=bio, mode="w|") as tar:
            # 添加目录条目
            dir_info = tarfile.TarInfo(name="src/")
            dir_info.type = tarfile.DIRTYPE
            tar.addfile(dir_info)
            # 添加文件
            file_info = tarfile.TarInfo(name="src/foo.py")
            file_info.size = 4
            tar.addfile(file_info, io.BytesIO(b"foo\n"))
        tar_bytes = bio.getvalue()
        result = batcher.parse_tar_archive(tar_bytes)
        assert "src/foo.py" in result
        assert "src/" not in result  # 目录被跳过
