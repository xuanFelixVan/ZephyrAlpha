# [BLUEPRINT] MOD-GOV_WORKTREE_MANAGER | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §worktree-manager
# [MODULE] zephyr.gov_enforcement.rule_bridge.worktree_manager
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.commit
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] session worktree 物理隔离——每 AI session 独占一个 git worktree（.aidrafts/{session_id}/），消除多 session 共享工作目录导致的 stash 循环与互相覆盖；worktree 路径 {REPO_ROOT}/.aidrafts/{session_id}/；分支命名 session/{session_id}（基于当前 HEAD 创建）；创建/删除 worktree 用文件锁（.runtime/locks/worktree.lock）防并发冲突；merge 回主分支用 --no-ff 保留 session 提交拓扑；未 merge 的 cleanup 需显式确认（丢弃修改）
# [MODIFY-GUARD] worktree 路径前缀 .aidrafts/；分支命名前缀 session/；锁文件名 worktree.lock
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] WorktreeError on worktree 创建/删除/merge 失败；get_current_worktree 返回 None 表示不在任何 session worktree 内
# [TESTS] tests/test_worktree_manager.py
# [A_module] module_id=MOD-GOV_WORKTREE_MANAGER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: while True+time.sleep是worktree锁等待循环，非周期触发
"""

worktree_manager.py — session worktree 物理隔离管理器（阶段3 治本 stash 循环）

根因（2026-06-30 A/A/A 决策）
------------------------------
多 AI session 共享 git 工作目录，git index 是工作区级全局共享状态。
GitCommitGateway 的 stash 隔离方案在多 session 并发下产生 stash 循环
（巨型 stash pop 冲突堆积，7+ 个 stash 无法 pop），治标不治本。

治本方案
--------
每个 AI session 分配独立 git worktree（物理隔离）：
1. session 启动时 create_session_worktree -> 在 .aidrafts/{sid}/ 创建独立 worktree
2. session 在自己的 worktree 内编辑/commit，互不干扰（无需 stash）
3. session 结束时 merge_session_worktree -> 合并回主分支
4. 异常/放弃时 cleanup_session_worktree -> 丢弃修改并清理 worktree

社区对标
--------
- AugmentCode：worktree 隔离 + spec 分解 + 顺序合并
- git-worktree 基线：每 session 独立工作树，commit 互不阻塞

Usage::

    from zephyr.gov_enforcement.rule_bridge.worktree_manager import WorktreeManager

    mgr = WorktreeManager()
    wt_path = mgr.create_session_worktree("sess-001")
    # ... session 在 wt_path 内工作 ...
    mgr.merge_session_worktree("sess-001", delete_after=True)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: session_id 会话标识
#   fields: AI session 唯一 ID（字符串，非空校验）
#   code: create_session_worktree(session_id) L312
# - id: I2
#   name: repo_root 仓库根目录
#   fields: git 仓库路径（默认 REPO_ROOT，须含 .git）
#   code: WorktreeManager.__init__ L196
# - id: I3
#   name: git CLI 子进程
#   fields: git worktree add/remove/list --porcelain、git merge、git branch -D 等命令输出
#   code: run_git L205（run_subprocess_hidden，timeout=120s）
# 层: 算法
# - id: A1
#   name_zh: ① 跨进程文件锁
#   name_en: _WorktreeLock
#   intro: 用原子创建锁文件串行化 worktree 增删，防并发 session 把 git 内部状态搞乱
#   desc: os.open(O_CREAT|O_EXCL) 抢锁；过期判定 TTL=锁超时×2 防死锁；超时 30s 抛 WorktreeError；退出删除锁文件
#   inputs: I2
#   outputs: 排他锁上下文
#   invariant: 锁文件 .runtime/locks/worktree.lock 同一时刻最多一个持有者
# - id: A2
#   name_zh: ② 创建 session worktree
#   name_en: WorktreeManager.create_session_worktree
#   intro: 在 .aidrafts/{sid}/ 给每个 AI session 开独立工作树，物理隔离免 stash
#   desc: 幂等复用已存在 worktree；_force_rmtree 清残留目录；git branch -D 清旧分支；git worktree add -b session/{sid} 从当前 HEAD 建分支
#   inputs: I1 I3 A1
#   outputs: worktree 绝对路径
#   invariant: worktree 路径前缀 .aidrafts/；分支命名 session/{session_id}
# - id: A3
#   name_zh: ③ 合并回主分支
#   name_en: WorktreeManager.merge_session_worktree
#   intro: session 干完活后用 --no-ff 把 session 分支合回主分支，冲突就 abort 保现场
#   desc: 主工作目录执行 git merge --no-ff -m "...[GW:{sid}:merge]"；失败则 git merge --abort 返回 False；成功后 _remove_worktree(force=True) 清理
#   inputs: I1 I3 A1
#   outputs: True=合并成功 / False=冲突保留现场
# - id: A4
#   name_zh: ④ 清理丢弃 worktree
#   name_en: WorktreeManager.cleanup_session_worktree / _remove_worktree
#   intro: 放弃 session 时强删 worktree 和分支，Windows 文件占用走 prune+rmtree 兜底
#   desc: git worktree remove --force；失败重试一次；再失败 prune + _force_rmtree + 再 prune；git worktree list 复核真删没删；最后删 session 分支
#   inputs: I1 I3 A1
#   outputs: True=删除成功 / False=不存在或失败
# - id: A5
#   name_zh: ⑤ worktree 状态查询
#   name_en: list_session_worktrees / get_current_worktree / is_in_worktree
#   intro: 解析 git worktree list --porcelain 列出 session 工作树，判断当前目录落在哪个 worktree
#   desc: porcelain 逐行解析为 dict；normcase 标准化路径防 Windows 大小写假阴性；git-dir≠git-common-dir 判定 linked worktree
#   inputs: I3
#   outputs: session worktree 列表 / session_id 或 None / bool
# 层: 输出
# - id: O1
#   name_zh: session worktree 路径与合并结果
#   name_en: Path / bool
#   intro: create 返回隔离工作树路径，merge/cleanup 返回成功与否，供提交网关隔离 AI 提交
#   downstream: git_commit_gateway.GitCommitGateway.commit（# [CONSUMERS] 头）
# - id: O2
#   name_zh: WorktreeError 异常
#   name_en: WorktreeError
#   intro: 创建/删除/merge 失败时抛出，error_code=ZA-GV-0031
#   downstream: 调用方捕获处理（内部使用）
# [/ALGO_FLOW]
#
# 边:
# I2 --> A1
# I1 --> A2
# I3 --> A2
# A1 --> A2
# A1 --> A3
# A1 --> A4
# I1 --> A3
# I3 --> A3
# I1 --> A4
# I3 --> A4
# A2 --> A3
# I3 --> A5
# A3 --> O1
# A4 --> O1
# A5 --> O1
# A2 --> O2
"""

from __future__ import annotations

__all__: Final = ["WorktreeManager", "WorktreeError"]

import json
import logging
import os
import re
import subprocess
import threading
import time
from pathlib import Path
from typing import Final

from zephyr.shared.io.file_utils import assert_safe_rmtree_target
from zephyr.shared.io.paths import REPO_ROOT, anchor_main_root

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
_AIDRAFTS_DIR = REPO_ROOT / ".aidrafts"
_LOCK_TIMEOUT = 30.0  # worktree 操作锁最长等待 30s
_LOCK_POLL = 0.1
_BRANCH_PREFIX = "session/"

#: session_id 白名单字符集（CAND-GOVSEC-001 ①）——仅字母数字开头 + [._:@-]，
#: 禁路径分隔符与 '..'：_wt_path 直接拼接进文件系统路径，session_id='../src'
#: 即解析到 .aidrafts/ 之外（2026-08-23 src 误删同型隐患①），必须在拼接前拦住。
_SESSION_ID_RE: Final = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:@-]{0,127}$")


def _validate_session_id(session_id: str) -> None:
    """session_id 白名单消毒（CAND-GOVSEC-001 ①）。非法即 WorktreeError（fail-closed）。

    消息不含 session_id 本体（MSG-EXPOSURE 合规）。
    """
    if not isinstance(session_id, str) or not _SESSION_ID_RE.fullmatch(session_id) or ".." in session_id:
        raise WorktreeError("session_id 字符集校验失败（白名单 [A-Za-z0-9._:@-] 且禁 '..'）")


class WorktreeError(RuntimeError):
    """worktree 管理错误（创建/删除/merge 失败等）。"""

    error_code = "ZA-GV-0031"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class _WorktreeLock:
    """跨进程文件锁（os.open O_CREAT|O_EXCL 原子创建）。

    用于序列化 worktree 创建/删除操作，防止并发 session 同时操作导致
    git worktree 内部状态不一致。对标 GitCommitGateway._GlobalCommitLock。
    锁文件路径跟随 repo_root（支持测试用独立临时仓库隔离，不污染主仓库）。
    """

    def __init__(self, repo_root: Path, timeout: float = _LOCK_TIMEOUT, poll: float = _LOCK_POLL) -> None:
        self._lock_file = repo_root / ".runtime" / "locks" / "worktree.lock"
        self._lock_file.parent.mkdir(parents=True, exist_ok=True)
        self._timeout = timeout
        self._poll = poll
        self._acquired = False

    def __enter__(self) -> "_WorktreeLock":
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
                # 检查是否过期（防死锁，TTL=锁超时×2）
                try:
                    data = json.loads(self._lock_file.read_text(encoding="utf-8"))
                    acquired_at = data.get("acquired_at", 0)
                    if not isinstance(acquired_at, (int, float)):
                        acquired_at = 0
                    if time.time() - acquired_at > _LOCK_TIMEOUT * 2:
                        try:
                            os.remove(str(self._lock_file))
                        except OSError:
                            pass
                        continue
                except (OSError, ValueError, TypeError):
                    try:
                        os.remove(str(self._lock_file))
                    except OSError:
                        pass
                    continue
                if time.monotonic() >= deadline:
                    raise WorktreeError(
                        f"Cannot acquire worktree lock (timeout {self._timeout}s): {self._lock_file}"
                    ) from None
                # PERM-TRIGGER fix: use Event().wait() instead of time.sleep()
                threading.Event().wait(self._poll)

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self._acquired:
            try:
                os.remove(str(self._lock_file))
            except OSError:
                pass
            self._acquired = False
        return False


def _force_rmtree(path: Path, *, allowed_prefix: Path) -> bool:
    """Windows 文件锁兜底强删目录。返回 True=完全删除，False=有残留。

    ``shutil.rmtree`` 默认遇 [WinError 32]（文件被占用）/ 只读位 直接失败。
    Windows 上 git/subprocess 刚退出时，文件句柄延迟释放（典型 0.3-2s），
    立即删除会失败。本 helper 用 ``onerror`` 回调：清除只读位 -> 重试 ->
    sleep 500ms 等句柄释放再试 -> 记录失败（不再静默吞错，调用方据返回值决策）。
    被 ``create_session_worktree``（清残留以重建）和 ``_remove_worktree``（清残留）复用。

    CAND-GOVSEC-001 ①：删除前经 ``assert_safe_rmtree_target`` 硬断言——resolve 后
    必须严格落在 allowed_prefix 内（session_id 污染/junction 逃逸物理阻断），
    断言失败抛 UnsafeDeleteRefused，不执行任何删除。
    """
    import shutil
    import stat

    resolved = assert_safe_rmtree_target(path, allowed_prefix=allowed_prefix)
    if not resolved.exists():
        return True  # 幂等：不存在=无残留

    failed: list[str] = []

    def _on_error(func, p, exc_info):  # noqa: ANN001
        # 第一次：清除只读位重试
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
            return
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in worktree_manager", exc_info=True)
        # 第二次：sleep 等句柄释放后重试
        threading.Event().wait(0.5)
        try:
            func(p)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            failed.append(str(p))  # 记录失败，不再静默吞错

    shutil.rmtree(str(resolved), onerror=_on_error)
    return not failed and not resolved.exists()


class WorktreeManager:
    """session worktree 物理隔离管理器。

    每 AI session 独占一个 git worktree（.aidrafts/{session_id}/），
    消除多 session 共享工作目录导致的 stash 循环与互相覆盖。

    worktree 路径: {REPO_ROOT}/.aidrafts/{session_id}/
    分支命名: session/{session_id}（基于当前 HEAD 创建）
    """

    def __init__(self, repo_root: str | Path | None = None) -> None:
        self.repo_root = Path(repo_root or REPO_ROOT).resolve()
        if not (self.repo_root / ".git").exists():
            raise WorktreeError(f"Not a git repository: {self.repo_root}")
        self._drafts_dir = self.repo_root / ".aidrafts"
        # 第二代机制 session worktree 根（scripts/session_worktree.py，#ARCH-AICOLLAB-001）
        self._session_worktrees_dir = self.repo_root / ".worktrees"

    # ------------------------------------------------------------------
    # 内部辅助
    # ------------------------------------------------------------------
    def run_git(self, cmd: list[str], cwd: str | Path | None = None) -> subprocess.CompletedProcess:
        """执行 git 命令（统一 cwd + encoding + CREATE_NO_WINDOW）。"""
        from zephyr.shared.infra.process_pool import run_subprocess_hidden

        return run_subprocess_hidden(
            cmd,
            cwd=str(cwd or self.repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )

    def _run_git(self, cmd: list[str], cwd: str | Path | None = None) -> subprocess.CompletedProcess:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.run_git(cmd, cwd)

    def _wt_path(self, session_id: str) -> Path:
        """session worktree 的绝对路径（CAND-GOVSEC-001①：拼接前白名单消毒）。"""
        _validate_session_id(session_id)
        return self._drafts_dir / session_id

    def _branch_name(self, session_id: str) -> str:
        """session worktree 的分支名。"""
        return f"{_BRANCH_PREFIX}{session_id}"

    def branch_name(self, session_id: str) -> str:
        """公共接口：branch_name（Stage 4 公共化，委托到 _branch_name）。"""
        return self._branch_name(session_id)

    def _current_head_sha(self) -> str:
        """获取主工作目录当前 HEAD 的 commit SHA。"""
        r = self.run_git(["git", "rev-parse", "HEAD"])
        if r.returncode != 0:
            raise WorktreeError(f"git rev-parse HEAD failed: {r.stderr.strip()}")
        return r.stdout.strip()

    def _worktree_exists(self, session_id: str) -> bool:
        """session worktree 是否已存在（git worktree list 中）。

        路径比较用 os.path.normcase 标准化——git porcelain 输出正斜杠路径
        （D:/ZephyrAlpha/...），而 Path.__str__ 在 Windows 给反斜杠
        （D:\\ZephyrAlpha\\...），精确字符串比较会假阴性（FP-ISO.4C 修复）。
        """
        wt = os.path.normcase(str(self._wt_path(session_id)))
        for entry in self._list_porcelain():
            if os.path.normcase(entry.get("path", "")) == wt:
                return True
        return False

    def worktree_exists(self, session_id: str) -> bool:
        """公共接口：worktree_exists（Stage 4 公共化，委托到 _worktree_exists）。"""
        return self._worktree_exists(session_id)

    def _list_porcelain(self) -> list[dict]:
        """解析 git worktree list --porcelain 输出为 dict 列表。

        porcelain 格式（每块以空行分隔）::

            worktree D:/ZephyrAlpha
            HEAD a8bad6054...
            branch refs/heads/trae-redteam-deadly-5

            worktree D:/ZephyrAlpha/.aidrafts/sess-001
            HEAD 1234...
            branch refs/heads/session/sess-001
        """
        r = self.run_git(["git", "worktree", "list", "--porcelain"])
        if r.returncode != 0:
            return []
        entries: list[dict] = []
        cur: dict = {}
        for line in r.stdout.splitlines():
            if not line.strip():
                if cur:
                    entries.append(cur)
                    cur = {}
                continue
            parts = line.split(" ", 1)
            key = parts[0]
            val = parts[1] if len(parts) > 1 else ""
            if key == "worktree":
                cur = {"path": val}
            elif key == "HEAD":
                cur["head"] = val
            elif key == "branch":
                cur["branch"] = val
            elif key == "detached":
                cur["detached"] = True
            elif key == "bare":
                cur["bare"] = True
        if cur:
            entries.append(cur)
        return entries

    def _is_dirty(self, wt_path: Path) -> bool:
        """worktree 是否有未提交修改（含 untracked）。"""
        r = self.run_git(["git", "status", "--porcelain"], cwd=str(wt_path))
        if r.returncode != 0:
            return False
        return bool(r.stdout.strip())

    # ------------------------------------------------------------------
    # 公开 API
    # ------------------------------------------------------------------
    def create_session_worktree(self, session_id: str) -> Path:
        """为 session 创建独立 worktree（基于当前 HEAD 创建新分支）。

        worktree 路径: .aidrafts/{session_id}/
        分支: session/{session_id}（从主工作目录当前 HEAD 创建）

        幂等：若 worktree 已存在，直接返回其路径。

        Args:
            session_id: AI session 标识。

        Returns:
            worktree 的绝对路径。

        Raises:
            WorktreeError: 创建失败（git worktree add 失败等）。
        """
        if not session_id:
            raise WorktreeError("session_id 不能为空")
        wt_path = self._wt_path(session_id)
        branch = self.branch_name(session_id)

        with _WorktreeLock(self.repo_root):
            if self.worktree_exists(session_id):
                logger.info(
                    "WorktreeManager: session worktree 已存在，复用 (session=%s): %s",
                    session_id,
                    wt_path,
                )
                return wt_path

            # Windows 文件锁兜底：上次 cleanup 可能留下物理残留目录（git 元数据
            # 已清理但目录因文件占用未删干净）。git worktree add 因路径已存在会失败，
            # 先用 _force_rmtree 强删残留，再创建。
            if wt_path.exists():
                logger.info(
                    "WorktreeManager: 创建前清理残留物理目录 (session=%s): %s",
                    session_id,
                    wt_path,
                )
                _force_rmtree(wt_path, allowed_prefix=self._drafts_dir)

            # 清理可能残留的旧分支（上次未 merge 的 cleanup 可能留下分支）
            self.run_git(["git", "branch", "-D", branch])

            head_sha = self._current_head_sha()
            # git worktree add -b <new-branch> <path> <start-point>
            r = self.run_git(["git", "worktree", "add", "-b", branch, str(wt_path), head_sha])
            if r.returncode != 0:
                # 分支可能已存在（上次未清理），尝试复用分支
                r2 = self.run_git(["git", "worktree", "add", str(wt_path), branch])
                if r2.returncode != 0:
                    raise WorktreeError(f"git worktree add 失败: {r2.stderr.strip() or r.stderr.strip()}")
            logger.info(
                "WorktreeManager: 创建 session worktree (session=%s, branch=%s, head=%s): %s",
                session_id,
                branch,
                head_sha[:8],
                wt_path,
            )
        return wt_path

    def merge_session_worktree(self, session_id: str, delete_after: bool = True) -> bool:
        """将 session worktree 的修改 merge 回主分支。

        在主工作目录执行 git merge session/{session_id}（--no-ff 保留拓扑）。
        merge 成功后可选删除 worktree。merge 冲突时返回 False（不删除 worktree，
        保留供用户手动解决）。

        Args:
            session_id: AI session 标识。
            delete_after: merge 成功后是否删除 worktree（默认 True）。

        Returns:
            True=merge 成功，False=merge 冲突/失败（worktree 保留）。
        """
        if not session_id:
            raise WorktreeError("session_id 不能为空")
        branch = self.branch_name(session_id)
        wt_path = self._wt_path(session_id)

        with _WorktreeLock(self.repo_root):
            if not self.worktree_exists(session_id):
                raise WorktreeError(f"session worktree 不存在: {wt_path}")
            # 在主工作目录执行 merge（--no-ff 保留 session 提交拓扑）
            # merge message 末尾追加 [GW:{sid}:merge] 标记，与 session_worktree_commit 的 [GW:{sid}:worktree] 设计对齐
            r = self.run_git(
                ["git", "merge", "--no-ff", "-m", f"merge session/{session_id}\n\n[GW:{session_id}:merge]", branch]
            )
            if r.returncode != 0:
                stderr = r.stderr.strip()
                logger.warning(
                    "WorktreeManager: merge 失败/冲突 (session=%s): %s",
                    session_id,
                    stderr,
                )
                # merge 冲突时中止 merge，保持主分支干净
                self.run_git(["git", "merge", "--abort"])
                return False
            logger.info(
                "WorktreeManager: merge 成功 (session=%s, branch=%s)",
                session_id,
                branch,
            )
            if delete_after:
                # merge 成功后 worktree 内容已并入主分支；force=True 安全删除
                # （dirty 的只是冗余未提交修改，主分支已有原版）。
                # 不忽略返回值：清理失败时调用方应保留 session 供重试（防孤儿 worktree）。
                removed = self._remove_worktree(session_id, force=True)
                if not removed:
                    logger.warning(
                        "WorktreeManager: merge 成功但 worktree 清理失败 (session=%s)，"
                        "调用方应保留 session 供重试 cleanup",
                        session_id,
                    )
        return True

    def cleanup_session_worktree(self, session_id: str) -> bool:
        """删除 session worktree（未 merge 的修改丢弃）。

        **警告**：此操作丢弃 worktree 内所有未提交/未 merge 的修改。
        调用方须确认 session 放弃其工作。

        Args:
            session_id: AI session 标识。

        Returns:
            True=删除成功，False=worktree 不存在或删除失败。
        """
        if not session_id:
            raise WorktreeError("session_id 不能为空")

        with _WorktreeLock(self.repo_root):
            if not self.worktree_exists(session_id):
                logger.info(
                    "WorktreeManager: cleanup no-op——worktree 不存在 (session=%s)",
                    session_id,
                )
                return False
            return self._remove_worktree(session_id, force=True)

    def _remove_worktree(self, session_id: str, force: bool) -> bool:
        """删除 worktree 及其分支（锁内执行）。

        Args:
            session_id: session 标识。
            force: True=强制删除（丢弃修改），False=仅干净时删除。
        """
        wt_path = self._wt_path(session_id)
        branch = self.branch_name(session_id)
        cmd = ["git", "worktree", "remove"]
        if force:
            cmd.append("--force")
        cmd.append(str(wt_path))
        r = self.run_git(cmd)
        if r.returncode != 0:
            # Windows 文件句柄延迟释放可能导致 remove 失败，sleep 后重试一次
            threading.Event().wait(0.5)
            r = self.run_git(cmd)
        if r.returncode != 0:
            # git worktree remove 在 Windows 上偶发失败(Invalid argument)，
            # 根因是 Windows/git 底层问题非时序问题，兜底逻辑(prune+rmtree+prune)已处理，
            # 降级为 info 避免噪音；真正的删除失败在下方 _worktree_exists 检查处记 warning
            logger.info(
                "WorktreeManager: git worktree remove 失败，走兜底 (session=%s): %s",
                session_id,
                r.stderr.strip(),
            )
            # 尝试 prune + 物理删除兜底
            self.run_git(["git", "worktree", "prune"])
            if wt_path.exists():
                _force_rmtree(wt_path, allowed_prefix=self._drafts_dir)
            self.run_git(["git", "worktree", "prune"])
            # Windows 文件锁可能导致物理目录残留，但 git worktree 元数据已清理。
            # 物理残留无害（下次 create_session_worktree 会覆盖）。
            # 关键判定：git 是否还认这个 worktree（查 git worktree list）。
            if self.worktree_exists(session_id):
                logger.warning(
                    "WorktreeManager: git 仍认 worktree (session=%s)——真删除失败",
                    session_id,
                )
                return False
            if wt_path.exists():
                logger.info(
                    "WorktreeManager: worktree 物理目录残留 (session=%s)——git 元数据已清理，残留无害",
                    session_id,
                )
        # 删除 session 分支（force 因可能未 merge）
        br_r = self.run_git(["git", "branch", "-D" if force else "-d", branch])
        if br_r.returncode != 0:
            logger.debug(
                "WorktreeManager: 删除分支 %s 跳过 (session=%s): %s",
                branch,
                session_id,
                br_r.stderr.strip(),
            )
        logger.info(
            "WorktreeManager: 删除 session worktree (session=%s, force=%s)",
            session_id,
            force,
        )
        return True

    def list_session_worktrees(self) -> list[dict]:
        """列出所有 session worktree。

        Returns:
            dict 列表，每项含:
            - session_id: session 标识
            - path: worktree 绝对路径
            - branch: 分支名（refs/heads/session/{sid}）
            - dirty: 是否有未提交修改
        """
        result: list[dict] = []
        for entry in self._list_porcelain():
            path = entry.get("path", "")
            # 仅列出 .aidrafts/ 下的 session worktree
            try:
                rel = Path(path).relative_to(self._drafts_dir)
            except ValueError:
                continue
            session_id = rel.parts[0] if rel.parts else ""
            if not session_id:
                continue
            wt_path = Path(path)
            result.append(
                {
                    "session_id": session_id,
                    "path": path,
                    "branch": entry.get("branch", ""),
                    "dirty": self._is_dirty(wt_path) if wt_path.exists() else False,
                }
            )
        return result

    def get_current_worktree(self) -> str | None:
        """获取当前所在 worktree 的 session_id。

        通过检查当前工作目录是否落在 .aidrafts/{session_id}/ 或
        .worktrees/{session_id}/ 下判定（后者=第二代机制，
        scripts/session_worktree.py，#ARCH-AICOLLAB-001；长期盲区导致
        WORKTREE-REQUIRED gate 在 .worktrees 内误判"非 worktree"，收口
        #ARCH-RECONCILER-WORKTREE-RACE 在新机制下的复发，#ARCH-WORKTREE-ENV-001）。
        若不在任何 session worktree 内返回 None。

        Returns:
            session_id 或 None。
        """
        cwd = Path.cwd().resolve()
        # repo_root 可能是 worktree 自身（PYTHONPATH 激活后 zephyr 解析到 worktree src），
        # 此时 session worktree 基目录必须锚定主仓库才能命中 cwd
        main_root = anchor_main_root(self.repo_root)
        bases = [self._drafts_dir, self._session_worktrees_dir]
        if main_root != self.repo_root:
            bases += [main_root / ".aidrafts", main_root / ".worktrees"]
        for base in bases:
            try:
                rel = cwd.relative_to(base.resolve())
            except ValueError:
                continue
            if rel.parts:
                return rel.parts[0]
        return None

    def is_in_worktree(self) -> bool:
        """检测当前是否在 git worktree 内（非主工作目录）。

        判据：git rev-parse 的 --git-dir 与 --git-common-dir 不一致时，
        当前位于 linked worktree（非主工作目录）。

        Returns:
            True=在 linked worktree 内，False=在主工作目录。
        """
        git_dir_r = self.run_git(["git", "rev-parse", "--git-dir"])
        common_dir_r = self.run_git(["git", "rev-parse", "--git-common-dir"])
        if git_dir_r.returncode != 0 or common_dir_r.returncode != 0:
            return False
        git_dir = Path(git_dir_r.stdout.strip()).resolve()
        common_dir = Path(common_dir_r.stdout.strip()).resolve()
        # 主工作目录下两者相同；linked worktree 下 git-dir 是 common-dir 的子目录
        return git_dir != common_dir
