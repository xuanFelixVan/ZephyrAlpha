# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md | §ghost-commit-gateway
# [MODULE] zephyr.governance.git_commit_gateway
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.task_repo.TaskRepository._auto_commit_on_completion; scripts/git_commit.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 全项目唯一合法 git commit 入口；全局跨进程串行锁（.ailocks/git_commit_global.lock，TTL=1800s）；选择性 stash 非本次 files；commit 用 -F <msg_file> 避免 PowerShell 特殊字符问题（RULE-TWENTY 裁定2）；stash pop 失败保留 stash 不丢数据；环境变量 ZEPHYR_COMMIT_GATEWAY=1 + commit message 追加 [GW:session_id] 标记
# [MODIFY-GUARD] _GlobalCommitLock 的 TTL 与锁文件名；commit message 的 GW 标记格式；ZEPHYR_COMMIT_GATEWAY 环境变量名
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] GatewayError on lock timeout；StashConflictWarning on stash pop 失败（数据保留在 stash）；CommitResult.status 暴露结果
# [TESTS] tests/test_git_commit_gateway.py
# [A_module] module_id=MOD-GOV-git_commit_gateway | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2026062512 治本）

根因（上一轮调研结论）
----------------------
多 AI session 共享 git 工作区，git index 是工作区级全局共享状态，无法 per-session 隔离。
DM-202918 只修了 TaskRepository.transition(COMPLETED) 一条路径，未覆盖 AI 手动 git commit 路径。
pre-commit stash 冲突导致本 session 修改被并发 session 的 commit 一并提交（"幽灵提交"）。

治本方案
--------
GitCommitGateway 作为全项目唯一合法 commit 入口，串行化所有 commit：
1. 全局跨进程串行锁（os.open O_CREAT|O_EXCL，参考 staging_area._CrossProcessLock）
2. 选择性 stash（git stash push -- <非本次 files>，隔离其他 session 未暂存修改）
3. git add -- <本次 files> + git commit --no-verify -F <msg_file> -- <本次 files>
4. git stash pop 恢复其他 session 修改，冲突则保留 stash 报警（不丢数据）
5. 设置环境变量 ZEPHYR_COMMIT_GATEWAY=1 + commit message 追加 [GW:session_id] 标记

社区对标
--------
- STORM（arXiv 2605.20563）：写时一致性，比 git-worktree 基线 +18.7%
- AugmentCode：worktree 隔离 + spec 分解 + 顺序合并
- 本项目不采用 git worktree（SSoT 约束 + 已投资 StagingArea 体系），采用串行化网关

Usage::

    from zephyr.governance.git_commit_gateway import GitCommitGateway, CommitStatus

    gw = GitCommitGateway(project_root="/path/to/project")
    result = gw.commit(
        session_id="sess-001",
        files=["/abs/path/file_a.py", "/abs/path/file_b.py"],
        message="feat(gov): add gateway",
    )
    if result.status == CommitStatus.OK:
        print("committed")
    elif result.status == CommitStatus.STASH_CONFLICT:
        print("stash pop failed, data kept in stash")
"""

from __future__ import annotations

__all__ = [
    "CommitResult",
    "CommitStatus",
    "GatewayError",
    "GitCommitGateway",
    "StashConflictWarning",
]

import json
import logging
import os
import subprocess
import tempfile
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
_GATEWAY_ENV = "ZEPHYR_COMMIT_GATEWAY"
_GW_MARKER_FMT = "[GW:{session_id}]"
_GLOBAL_LOCK_FILE = "git_commit_global.lock"
_LOCK_TTL_SECONDS = 1800  # 30 分钟，防进程崩溃死锁（与 staging_area.py 一致）
_LOCK_TIMEOUT_DEFAULT = 60.0  # 等待全局锁最长 60s（commit 串行化，比单文件锁久）
_POLL_INTERVAL = 0.1
_MAX_INLINE_PATHS = 50  # 超过此数量时用 --pathspec-from-file 避免 Windows CLI 长度限制 (WinError 206)


class CommitStatus(str, Enum):
    """commit 结果状态。"""

    OK = "OK"  # commit 成功
    NOTHING_TO_COMMIT = "NOTHING_TO_COMMIT"  # files_in_scope 无 staged 变更
    STASH_CONFLICT = "STASH_CONFLICT"  # commit 成功但 stash pop 失败（数据保留在 stash）
    COMMIT_FAILED = "COMMIT_FAILED"  # git commit 命令失败
    LOCK_TIMEOUT = "LOCK_TIMEOUT"  # 获取全局锁超时


class GatewayError(RuntimeError):
    """Gateway 层错误（锁超时等）。"""


class StashConflictWarning(RuntimeWarning):
    """stash pop 失败警告——数据保留在 stash 中，不丢失。"""


@dataclass
class CommitResult:
    """commit 结果。"""

    status: CommitStatus
    message: str = ""
    commit_hash: str = ""
    stash_ref: str = ""  # stash pop 失败时保留的 stash 引用
    stash_kept: bool = False  # 是否保留了 stash（pop 失败）


class _GlobalCommitLock:
    """跨进程全局串行锁（os.open O_CREAT|O_EXCL 原子创建）。

    根因: threading.Lock 只保护单进程内线程，多进程（Trae 多对话窗口）下无效。
    本锁通过 os.open(O_CREAT|O_EXCL) 原子操作实现跨进程互斥。

    锁文件: .ailocks/git_commit_global.lock（全项目唯一，串行化所有 commit）
    TTL: 30 分钟（防进程崩溃死锁，与 staging_area.py / lock_files.py 一致）

    对标 staging_area._CrossProcessLock（第 89-161 行），区别：
    - 后者按 file_path hash 分锁（per-file 锁）
    - 本锁全局唯一（commit 必须全串行，不能并发）
    """

    def __init__(
        self,
        project_root: Path,
        timeout: float = _LOCK_TIMEOUT_DEFAULT,
        poll_interval: float = _POLL_INTERVAL,
    ) -> None:
        self._lock_file = project_root / ".ailocks" / _GLOBAL_LOCK_FILE
        self._lock_file.parent.mkdir(parents=True, exist_ok=True)
        self._timeout = timeout
        self._poll_interval = poll_interval
        self._acquired = False

    def __enter__(self) -> _GlobalCommitLock:
        deadline = time.monotonic() + self._timeout
        while True:
            try:
                fd = os.open(str(self._lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                try:
                    os.write(
                        fd,
                        json.dumps(
                            {"pid": os.getpid(), "acquired_at": time.time()},
                            ensure_ascii=False,
                        ).encode("utf-8"),
                    )
                finally:
                    os.close(fd)
                self._acquired = True
                return self
            except FileExistsError:
                # 检查是否过期（防死锁）
                try:
                    data = json.loads(self._lock_file.read_text(encoding="utf-8"))
                    acquired_at = data.get("acquired_at", 0)
                    if not isinstance(acquired_at, (int, float)):
                        acquired_at = 0
                    if time.time() - acquired_at > _LOCK_TTL_SECONDS:
                        try:
                            os.remove(self._lock_file)
                        except OSError:
                            pass
                        continue
                except (OSError, ValueError, TypeError):
                    # 锁文件损坏/不可读——视为无效锁，清理后重试
                    # 修复：损坏锁不应死等，否则会导致 gateway 卡死直到超时
                    logger.warning(
                        "_GlobalCommitLock: 锁文件损坏，清理后重试: %s", self._lock_file
                    )
                    try:
                        os.remove(self._lock_file)
                    except OSError:
                        pass
                    continue
                if time.monotonic() >= deadline:
                    raise GatewayError(
                        f"Cannot acquire global commit lock (timeout {self._timeout}s)— "
                        f"another session is committing. Lock file: {self._lock_file}"
                    )
                time.sleep(self._poll_interval)

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self._acquired:
            try:
                os.remove(self._lock_file)
            except OSError:
                pass
            self._acquired = False
        return False


class GitCommitGateway:
    """全项目唯一合法 git commit 入口。

    串行化所有 commit，选择性 stash 隔离其他 session 修改，根治幽灵提交。

    环境变量: ZEPHYR_COMMIT_GATEWAY=1（commit 子进程设置，供 GATE-COMMIT-GW 门禁检测）
    commit message 标记: [GW:<session_id>]（追加到 message 末尾）
    """

    def __init__(self, project_root: str | Path | None = None) -> None:
        self.project_root = Path(project_root or Path.cwd()).resolve()
        if not (self.project_root / ".git").exists():
            raise GatewayError(f"Not a git repository: {self.project_root}")

    # ------------------------------------------------------------------
    # 公开 API
    # ------------------------------------------------------------------
    def commit(
        self,
        session_id: str,
        files: list[str],
        message: str,
    ) -> CommitResult:
        """串行化 commit 入口。

        Args:
            session_id: AI session 标识（用于 GW 标记 + stash message）。
            files: 本次 commit 的文件绝对路径列表。
            message: commit message（不含 GW 标记，自动追加）。

        Returns:
            CommitResult。
        """
        if not files:
            return CommitResult(status=CommitStatus.NOTHING_TO_COMMIT, message="empty files list")
        if not session_id:
            session_id = "unknown"

        # 归一化为绝对路径
        abs_files = [str(Path(f).resolve()) for f in files]
        # 过滤不存在且未 git 跟踪的文件：
        # - 存在的文件 → 保留
        # - 不存在但 git 跟踪 → 保留（deletion commit 场景）
        # - 不存在且未跟踪 → 丢弃（避免 git add 失败返回 COMMIT_FAILED）
        # 对标 git_commit.py CLI 的 _check_missing 逻辑（line 101-117）
        existing: list[str] = []
        for f in abs_files:
            if os.path.isfile(f):
                existing.append(f)
            else:
                rel = os.path.relpath(f, str(self.project_root)).replace("\\", "/")
                chk = subprocess.run(
                    ["git", "ls-files", "--error-unmatch", "--", rel],
                    capture_output=True,
                    cwd=str(self.project_root),
                )
                if chk.returncode == 0:
                    existing.append(f)  # git 跟踪的已删除文件
        if not existing:
            return CommitResult(
                status=CommitStatus.NOTHING_TO_COMMIT,
                message="no existing or tracked files to commit",
            )

        # 追加 GW 标记
        gw_marker = _GW_MARKER_FMT.format(session_id=session_id)
        full_message = f"{message}\n\n{gw_marker}"

        try:
            with _GlobalCommitLock(self.project_root):
                return self._commit_locked(session_id, existing, full_message, gw_marker)
        except GatewayError as e:
            return CommitResult(status=CommitStatus.LOCK_TIMEOUT, message=str(e))

    # ------------------------------------------------------------------
    # 内部实现
    # ------------------------------------------------------------------
    def _commit_locked(
        self,
        session_id: str,
        files: list[str],
        full_message: str,
        gw_marker: str,
    ) -> CommitResult:
        """持锁状态下执行 stash → add → commit → pop。

        stash pop 在 finally 中执行（无论 commit 成功失败都要恢复，不丢数据）。
        若 stash pop 失败，覆盖结果为 STASH_CONFLICT（数据保留在 stash）。

        注意：不在 try 块内 return——Python 中 return 会先捕获返回值再执行 finally，
        finally 内对同名变量重新赋值不会改变已捕获的返回值。故统一在末尾 return。
        """
        stashed = False
        stash_ref = ""
        pathspec_file: str | None = None
        result: CommitResult = CommitResult(
            status=CommitStatus.COMMIT_FAILED, message="unexpected: no result set"
        )
        # 大文件列表时用 --pathspec-from-file 避免 Windows CLI 长度限制 (WinError 206)
        # 同时检查非目标文件数：原始流程的 _stash_other_files 会显式枚举非目标文件
        # 传给 `git stash push -- <files>`，数量过多时同样触发 WinError 206
        non_target_count = self._count_non_target_changed(files)
        use_pathspec_file = (
            len(files) > _MAX_INLINE_PATHS
            or non_target_count > _MAX_INLINE_PATHS
        )
        try:
            if use_pathspec_file:
                # === 大文件列表流程（>50 文件）===
                # 1. 写 pathspec 文件
                pathspec_file = self._write_pathspec_file(files)

                # 2. git add --pathspec-from-file=<file>（staged 目标文件）
                add_result = self._run_git(
                    ["git", "add", f"--pathspec-from-file={pathspec_file}"]
                )
                if add_result.returncode != 0:
                    logger.warning(
                        "GitCommitGateway: git add (pathspec-file) 失败: %s",
                        add_result.stderr.strip(),
                    )
                    result = CommitResult(
                        status=CommitStatus.COMMIT_FAILED,
                        message=f"git add failed: {add_result.stderr.strip()}",
                    )
                else:
                    # 3. git stash push --keep-index（stash 非目标 unstaged 变更）
                    #    --keep-index 保留已 staged 的目标文件，stash 其余工作区变更
                    stash_result = self._run_git(
                        ["git", "stash", "push", "--keep-index", "-m", f"gw:{session_id}"]
                    )
                    if stash_result.returncode == 0:
                        stashed = True
                        list_result = self._run_git(
                            ["git", "stash", "list", "--format=%gd|%gs", "-1"]
                        )
                        if list_result.returncode == 0 and list_result.stdout.strip():
                            stash_ref = list_result.stdout.strip().split("|", 1)[0]
                    else:
                        stderr = stash_result.stderr.strip()
                        # "No local changes to save" = 无非目标变更，非错误
                        if "No local changes" not in stderr and "no entry" not in stderr.lower():
                            logger.warning(
                                "GitCommitGateway: stash --keep-index 失败: %s", stderr
                            )

                    # 4. 检查 staged 变更
                    diff_result = self._run_git(["git", "diff", "--cached", "--quiet"])
                    if diff_result.returncode == 0:
                        logger.info(
                            "GitCommitGateway: files 无 staged 变更，跳过 commit"
                        )
                        result = CommitResult(
                            status=CommitStatus.NOTHING_TO_COMMIT,
                            message="no staged changes in files_in_scope",
                        )
                    else:
                        # 5. git commit --no-verify -F <msg> --pathspec-from-file=<file>
                        commit_hash, commit_err = self._commit_with_file_message(
                            files, full_message, pathspec_file=pathspec_file
                        )
                        if commit_hash is None:
                            result = CommitResult(
                                status=CommitStatus.COMMIT_FAILED,
                                message=f"git commit failed: {commit_err}",
                            )
                        else:
                            os.environ[_GATEWAY_ENV] = "1"
                            logger.info(
                                "GitCommitGateway: commit 成功 hash=%s marker=%s "
                                "files=%d (pathspec-file)",
                                commit_hash, gw_marker, len(files),
                            )
                            result = CommitResult(
                                status=CommitStatus.OK,
                                message=f"committed {len(files)} files",
                                commit_hash=commit_hash,
                            )
            else:
                # === 原流程（小文件列表 ≤50 文件）===
                # 1. 选择性 stash 非本次 files 的已修改文件
                stashed, stash_ref = self._stash_other_files(session_id, files)

                # 2. git add -- <本次 files>
                add_result = self._run_git(["git", "add", "--"] + files)
                if add_result.returncode != 0:
                    logger.warning(
                        "GitCommitGateway: git add 失败: %s", add_result.stderr.strip()
                    )
                    result = CommitResult(
                        status=CommitStatus.COMMIT_FAILED,
                        message=f"git add failed: {add_result.stderr.strip()}",
                    )
                else:
                    # 3. 检查 files_in_scope 是否有 staged 变更
                    diff_result = self._run_git(
                        ["git", "diff", "--cached", "--quiet"] + files
                    )
                    if diff_result.returncode == 0:
                        # exit 0 = 无变更
                        logger.info(
                            "GitCommitGateway: files 无 staged 变更，跳过 commit"
                        )
                        result = CommitResult(
                            status=CommitStatus.NOTHING_TO_COMMIT,
                            message="no staged changes in files_in_scope",
                        )
                    else:
                        # 4. git commit --no-verify -F <msg_file> -- <本次 files>
                        commit_hash, commit_err = self._commit_with_file_message(
                            files, full_message
                        )
                        if commit_hash is None:
                            result = CommitResult(
                                status=CommitStatus.COMMIT_FAILED,
                                message=f"git commit failed: {commit_err}",
                            )
                        else:
                            # 5. 设置环境变量标记
                            os.environ[_GATEWAY_ENV] = "1"
                            logger.info(
                                "GitCommitGateway: commit 成功 hash=%s marker=%s "
                                "files=%d",
                                commit_hash, gw_marker, len(files),
                            )
                            result = CommitResult(
                                status=CommitStatus.OK,
                                message=f"committed {len(files)} files",
                                commit_hash=commit_hash,
                            )
        finally:
            # 6. 恢复 stash（无论 commit 成功失败都要恢复，不丢数据）
            if stashed:
                pop_ok = self._restore_stash()
                if not pop_ok:
                    # stash pop 失败——保留 stash，报警，覆盖结果为 STASH_CONFLICT
                    logger.warning(
                        "GitCommitGateway: stash pop 失败，数据保留在 stash: %s", stash_ref
                    )
                    if result.status == CommitStatus.OK:
                        result = CommitResult(
                            status=CommitStatus.STASH_CONFLICT,
                            message=f"commit OK but stash pop failed, data kept in stash {stash_ref}",
                            commit_hash=result.commit_hash,
                            stash_ref=stash_ref,
                            stash_kept=True,
                        )
                    else:
                        result = CommitResult(
                            status=CommitStatus.STASH_CONFLICT,
                            message=f"{result.message}; stash pop failed, data kept in stash {stash_ref}",
                            stash_ref=stash_ref,
                            stash_kept=True,
                        )
            # 清理 pathspec 临时文件
            if pathspec_file:
                try:
                    os.remove(pathspec_file)
                except OSError:
                    pass
            # 清理环境变量标记
            os.environ.pop(_GATEWAY_ENV, None)
        return result

    def _count_non_target_changed(self, target_files: list[str]) -> int:
        """统计非目标的已修改已跟踪文件数。

        用于判断是否需要切换到 pathspec-file 流程：原始流程的
        ``_stash_other_files`` 会显式枚举非目标文件并传给
        ``git stash push -- <files>``，数量过多时触发 WinError 206
        (Windows CLI 长度限制 32767 字符)。
        """
        status_result = self._run_git(["git", "status", "--porcelain"])
        if status_result.returncode != 0:
            return 0
        target_set = {str(Path(f).resolve()) for f in target_files}
        count = 0
        for line in status_result.stdout.splitlines():
            if not line.strip() or line.startswith("??"):
                continue
            path = line[3:].strip().strip('"')
            abs_path = str((self.project_root / path).resolve())
            if abs_path not in target_set:
                count += 1
        return count

    def _stash_other_files(self, session_id: str, target_files: list[str]) -> tuple[bool, str]:
        """选择性 stash 非本次 files 的已修改文件。

        策略:
        1. git status --porcelain 获取所有已修改文件
        2. 过滤出不在 target_files 中的已跟踪文件
        3. git stash push -m <session_id> -- <those files>

        Returns:
            (是否 stash 了文件, stash_ref)
        """
        # 获取工作区所有已修改文件（staged + unstaged，已跟踪）
        status_result = self._run_git(["git", "status", "--porcelain"])
        if status_result.returncode != 0:
            logger.warning("GitCommitGateway: git status 失败: %s", status_result.stderr.strip())
            return False, ""

        changed_files: list[str] = []
        target_set = {str(Path(f).resolve()) for f in target_files}
        for line in status_result.stdout.splitlines():
            if not line.strip():
                continue
            # porcelain 格式: XY <path>，X=staged状态, Y=工作区状态
            # 只处理已跟踪文件（X/Y 不是 ??）
            if line.startswith("??"):
                continue
            path = line[3:].strip().strip('"')
            abs_path = str((self.project_root / path).resolve())
            if abs_path not in target_set:
                changed_files.append(path)

        if not changed_files:
            return False, ""

        # git stash push -- <非本次 files>
        stash_msg = f"gw:{session_id}"
        stash_result = self._run_git(
            ["git", "stash", "push", "-m", stash_msg, "--"] + changed_files
        )
        if stash_result.returncode != 0:
            # stash 失败可能是"No local changes to save"——非错误
            stderr = stash_result.stderr.strip()
            if "No local changes" in stderr or "no changes" in stderr.lower():
                return False, ""
            logger.warning("GitCommitGateway: git stash push 失败: %s", stderr)
            return False, ""

        # 获取 stash ref（stash@{0}）
        list_result = self._run_git(["git", "stash", "list", "--format=%gd|%gs", "-1"])
        stash_ref = ""
        if list_result.returncode == 0 and list_result.stdout.strip():
            stash_ref = list_result.stdout.strip().split("|", 1)[0]
        logger.info("GitCommitGateway: stash 了 %d 个非本次文件 ref=%s", len(changed_files), stash_ref)
        return True, stash_ref

    def _restore_stash(self) -> bool:
        """恢复 stash（git stash pop）。

        Returns:
            True=成功恢复, False=pop 失败（数据保留在 stash）
        """
        pop_result = self._run_git(["git", "stash", "pop"])
        if pop_result.returncode != 0:
            stderr = pop_result.stderr.strip()
            # 冲突时 stash 不会被删除，数据安全
            if "conflict" in stderr.lower() or "merge" in stderr.lower():
                return False
            # 其他错误也视为失败（保留 stash）
            logger.warning("GitCommitGateway: git stash pop 异常: %s", stderr)
            return False
        return True

    def _commit_with_file_message(
        self,
        files: list[str],
        message: str,
        pathspec_file: str | None = None,
    ) -> tuple[str | None, str]:
        """用 -F <msg_file> 方式 commit（RULE-TWENTY 裁定2：避免 PowerShell 特殊字符问题）。

        Args:
            files: 目标文件列表（pathspec_file 为 None 时用 ``--`` 内联传递）。
            message: commit message。
            pathspec_file: pathspec 文件路径（大文件列表时用
                ``--pathspec-from-file`` 避免 CLI 长度限制）。

        Returns:
            (commit_hash, error_message)。commit_hash 为 None 表示失败。
        """
        # 写消息到临时文件（RULE-FIVE：temp-file + 原子写入）
        msg_fd, msg_path = tempfile.mkstemp(
            prefix="gw_commit_msg_", suffix=".txt", dir=str(self.project_root)
        )
        try:
            with os.fdopen(msg_fd, "w", encoding="utf-8") as f:
                f.write(message)

            if pathspec_file:
                commit_cmd = [
                    "git", "commit", "--no-verify", "-F", msg_path,
                    f"--pathspec-from-file={pathspec_file}",
                ]
            else:
                commit_cmd = ["git", "commit", "--no-verify", "-F", msg_path, "--"] + files
            result = self._run_git(commit_cmd)
            if result.returncode != 0:
                return None, result.stderr.strip()

            # 获取 commit hash
            rev_result = self._run_git(["git", "rev-parse", "HEAD"])
            if rev_result.returncode == 0:
                return rev_result.stdout.strip(), ""
            return "", ""
        finally:
            try:
                os.remove(msg_path)
            except OSError:
                pass

    def _write_pathspec_file(self, abs_files: list[str]) -> str:
        """将文件路径写入临时 pathspec 文件（相对路径，每行一个）。

        用于 ``git add --pathspec-from-file`` 和
        ``git commit --pathspec-from-file``，避免 Windows CLI 长度限制
        (WinError 206)。

        Returns:
            临时文件路径（调用方负责删除）。
        """
        fd, path = tempfile.mkstemp(
            prefix="gw_pathspec_", suffix=".txt", dir=str(self.project_root)
        )
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            for abs_path in abs_files:
                rel = os.path.relpath(abs_path, str(self.project_root))
                rel = rel.replace("\\", "/")  # git pathspec 用正斜杠
                f.write(f"{rel}\n")
        return path

    def _run_git(self, cmd: list[str]) -> subprocess.CompletedProcess:
        """执行 git 命令（统一 cwd + encoding）。"""
        env = os.environ.copy()
        env[_GATEWAY_ENV] = "1"  # 标记经 gateway
        return subprocess.run(
            cmd,
            cwd=str(self.project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
            env=env,
        )
