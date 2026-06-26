# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md | §ghost-commit-gateway
# [MODULE] zephyr.governance.git_commit_gateway
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__; zephyr.security.access_control.session_concurrency
# [CONSUMERS] zephyr.governance.task_repo.TaskRepository._auto_commit_on_completion; scripts/git_commit.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 全项目唯一合法 git commit 入口；全局跨进程串行锁（.ailocks/git_commit_global.lock，TTL=1800s）；选择性 stash 非本次 files；commit 用 -F <msg_file> 避免 PowerShell 特殊字符问题（RULE-TWENTY 裁定2）；stash pop 失败保留 stash 不丢数据；环境变量 ZEPHYR_COMMIT_GATEWAY=1 + commit message 追加 [GW:session_id] 标记；session 隔离 stash（已注册 session 只 stash 其 held_files 中的非目标文件，未注册回退原逻辑）；feature flag ZEPHYR_SESSION_AWARE_STASH=0 强制禁用
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
    "ReconcileResult",
    "StashConflictWarning",
]

import json
import logging
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from zephyr.governance.reconciliation_registry import (
    ReconcileResult,
    ReconciliationRegistry,
    make_manifest_reconciler,
    make_baseline_aware_reconciler,
    make_ttl_reconciler,
    make_ghost_reconciler,
    make_path_tree_reconciler,
    make_working_docs_reconciler,
)

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
_SESSION_AWARE_STASH_ENV = "ZEPHYR_SESSION_AWARE_STASH"  # "0" 强制禁用 session 隔离 stash

# 永久区目录前缀——新文件进入这些目录需要 --allow-promote 门禁批准
# 真源：ttl_vocabulary.yaml decision_tree + project_rules.md RULE-TWO
# 非永久区路径（如 docs/_working/）的文件不触发门禁
_PERMANENT_ZONE_DIRS: tuple[str, ...] = (
    "docs/01_policies_and_standards/",
    "docs/02_enterprise_architecture/",
    "docs/03_modules/",
    "docs/08_knowledge/",
)


class CommitStatus(str, Enum):
    """commit 结果状态。"""

    OK = "OK"  # commit 成功
    NOTHING_TO_COMMIT = "NOTHING_TO_COMMIT"  # files_in_scope 无 staged 变更
    STASH_CONFLICT = "STASH_CONFLICT"  # commit 成功但 stash pop 失败（数据保留在 stash）
    COMMIT_FAILED = "COMMIT_FAILED"  # git commit 命令失败
    LOCK_TIMEOUT = "LOCK_TIMEOUT"  # 获取全局锁超时
    PROMOTION_BLOCKED = "PROMOTION_BLOCKED"  # 永久区新文件未获 --allow-promote 批准
    METADATA_VIOLATION = "METADATA_VIOLATION"  # .md 文件 frontmatter ttl 校验失败
    SSOT_VIOLATION = "SSOT_VIOLATION"  # 新增 .py 声明了已有 module_path（绕过 scaffold 创建）
    NAMING_VIOLATION = "NAMING_VIOLATION"  # N-16 文件名唯一性校验失败（--no-verify 补偿）


class GatewayError(RuntimeError):
    """Gateway 层错误（锁超时等）。"""


class StashConflictWarning(RuntimeWarning):
    """stash pop 失败警告——数据保留在 stash 中，不丢失。"""


# ReconcileResult 已迁移至 reconciliation_registry.py（P2-T1），此处通过 import re-export
# 保持 ``from zephyr.governance.git_commit_gateway import ReconcileResult`` 向后兼容。


@dataclass
class CommitResult:
    """commit 结果。"""

    status: CommitStatus
    message: str = ""
    commit_hash: str = ""
    stash_ref: str = ""  # stash pop 失败时保留的 stash 引用
    stash_kept: bool = False  # 是否保留了 stash（pop 失败）
    # P2-T1：单值 ReconcileResult → list[ReconcileResult]，支持多 reconciler 并存
    reconcile: list[ReconcileResult] = field(default_factory=list)


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

    def __init__(
        self,
        project_root: str | Path | None = None,
        registry: "SessionRegistry | None" = None,
    ) -> None:
        self.project_root = Path(project_root or Path.cwd()).resolve()
        if not (self.project_root / ".git").exists():
            raise GatewayError(f"Not a git repository: {self.project_root}")
        # session 隔离 stash 依赖 SessionRegistry（延迟 import 与 task_repo.py 一致）
        if registry is not None:
            self._registry = registry
        else:
            from zephyr.security.access_control.session_concurrency import SessionRegistry
            self._registry = SessionRegistry(self.project_root)
        # post-commit 漂移对账注册表（P2-T1：声明式 reconciler 框架，替代硬编码 _post_commit_reconcile）
        self._reconciliation_registry = ReconciliationRegistry()
        self._register_default_reconcilers()

    def claim_files(self, session_id: str, files: list[str]) -> list[str]:
        """为 session 声明持有本次 commit 的文件（激活 session 隔离 stash）。

        由调用方在 commit 前调用。claim 失败（被其他 session 持有）的文件从返回列表排除，
        不阻断 commit（文件归属协调是 lock_files.py 的职责，gateway 不强制）。

        Returns: 成功 claim 的文件列表。
        """
        claimed: list[str] = []
        for f in files:
            if self._registry.claim_file(session_id, f):
                claimed.append(f)
            else:
                logger.warning(
                    "GitCommitGateway: claim_files conflict — file=%s held by other session, "
                    "skipped (session=%s)",
                    f, session_id,
                )
        return claimed

    def release_files(self, session_id: str, files: list[str]) -> None:
        """释放 session 对文件的持有（commit 后调用，静默失败仅 warning）。"""
        for f in files:
            if not self._registry.release_file(session_id, f):
                logger.debug(
                    "GitCommitGateway: release_files no-op — file=%s not held by session=%s",
                    f, session_id,
                )

    # ------------------------------------------------------------------
    # session 隔离 stash 辅助方法（Step 4-5：选择性 stash 核心）
    # ------------------------------------------------------------------
    def _session_aware_stash_enabled(self) -> bool:
        """session 隔离 stash 是否启用（ZEPHYR_SESSION_AWARE_STASH != "0"）。

        默认启用；设为 "0" 强制禁用（kill-switch），回退原 stash-all 逻辑。
        """
        return os.environ.get(_SESSION_AWARE_STASH_ENV, "1") != "0"

    def _get_session_held_non_target(
        self,
        session_id: str,
        target_files: list[str],
        all_non_target_changed: list[str],
    ) -> tuple[bool, list[str]]:
        """从非目标变更文件中筛出可 stash 的候选（session 隔离 + 强保护）。

        强不变量（红蓝对抗修正）：feature 启用时，始终排除其他活跃 session 持有的文件，
        即使本 session 未注册（未 claim）——绝不 stash 别人的 WIP。
        三级决策：
        1. feature 禁用（kill-switch）→ 纯原 stash-all（无保护，向后兼容）
        2. feature 启用 + 本 session 未注册/held 空 → stash 全部非保护文件
           （排除他人持有，但本 session 无精确 held 范围）
        3. feature 启用 + 本 session 已注册 → 只 stash 本 session held 的非保护文件
           （精确最小集，既保护他人也只动自己的）

        Args:
            session_id: 当前 commit 的 session。
            target_files: 本次 commit 的目标文件（绝对路径）。
            all_non_target_changed: 所有非目标的已修改已跟踪文件（相对路径）。

        Returns:
            (isolation_active, candidates)
            - (False, [...])：回退模式（feature 禁用 或 未注册），
              candidates 已排除他人持有（feature 启用时）或全部（feature 禁用时）
            - (True, [...])：session 隔离生效，只 stash candidates
        """
        # kill-switch 关闭 → 纯原逻辑（stash 全部非目标，无 session 保护）
        if not self._session_aware_stash_enabled():
            return False, all_non_target_changed

        # 强不变量：feature 启用时，始终排除其他活跃 session 持有的文件
        try:
            other_held = self._registry.other_held_files(session_id)
        except Exception:
            # registry 读取异常 → 安全降级（不排除，但绝不阻断 commit）
            other_held = set()

        not_protected: list[str] = []
        for rel_path in all_non_target_changed:
            abs_p = str((self.project_root / rel_path).resolve())
            if abs_p not in other_held:
                not_protected.append(rel_path)

        info = self._registry.get_session(session_id)
        if info is None or not info.held_files:
            # 未注册 / held 空 → stash 全部非保护文件（保护他人，回退本 session 范围）
            return False, not_protected

        # 已注册 → 只 stash 本 session held 的非保护文件（精确最小集）
        held_abs = {str(Path(f).resolve()) for f in info.held_files}
        target_abs = {str(Path(f).resolve()) for f in target_files}
        candidates: list[str] = []
        for rel_path in not_protected:
            abs_p = str((self.project_root / rel_path).resolve())
            if abs_p in target_abs:
                continue
            if abs_p in held_abs:
                candidates.append(rel_path)
        return True, candidates

    def _collect_non_target_rel(self, target_files: list[str]) -> list[str]:
        """收集非目标的已修改已跟踪文件（相对路径），跳过未跟踪文件（??）。

        porcelain 格式: ``XY <path>``，X=staged, Y=工作区。``??`` 行为未跟踪，跳过。
        target_files 用绝对路径归一化匹配（resolve），排除本次 commit 目标。
        """
        status_result = self._run_git(["git", "status", "--porcelain"])
        if status_result.returncode != 0:
            logger.warning(
                "GitCommitGateway: git status 失败: %s", status_result.stderr.strip()
            )
            return []
        target_set = {str(Path(f).resolve()) for f in target_files}
        result: list[str] = []
        for line in status_result.stdout.splitlines():
            if not line.strip() or line.startswith("??"):
                continue
            path = line[3:].strip().strip('"')
            abs_path = str((self.project_root / path).resolve())
            if abs_path not in target_set:
                result.append(path)
        return result

    def _register_default_reconcilers(self) -> None:
        """注册默认 post-commit reconciler（P2-T1 框架 + P2-T2 manifest + P2-T3 baseline_aware + P2-T4 ttl + P2-T5 ghost + P2-T6 working_docs）。

        P2-T2: manifest 对账逻辑迁移为 ``make_manifest_reconciler`` 工厂。
        P2-T3: baseline_aware 对账（GATE-REG-BL 补偿，非阻断，报告落盘）。
        P2-T4: ttl 兜底（GATE-15 post-compensation，增量校验 committed .md）。
        P2-T5: ghost 对账（depgraph 对称漂移检测，删除 commit 触发 diagnose_depgraph）。
        P2-T6: working_docs 对账（_working/ 幽灵引用检测，删除 commit 触发归档，治 AI 工作文档堆积）。
        """
        self._reconciliation_registry.register(make_manifest_reconciler(self))
        self._reconciliation_registry.register(make_path_tree_reconciler(self))
        self._reconciliation_registry.register(make_baseline_aware_reconciler(self))
        self._reconciliation_registry.register(make_ttl_reconciler(self))
        self._reconciliation_registry.register(make_ghost_reconciler(self))
        self._reconciliation_registry.register(make_working_docs_reconciler(self))

    # ------------------------------------------------------------------
    # 公开 API
    # ------------------------------------------------------------------
    def commit(
        self,
        session_id: str,
        files: list[str],
        message: str,
        allow_promote: bool = False,
    ) -> CommitResult:
        """串行化 commit 入口。

        Args:
            session_id: AI session 标识（用于 GW 标记 + stash message）。
            files: 本次 commit 的文件绝对路径列表。
            message: commit message（不含 GW 标记，自动追加）。
            allow_promote: 是否允许新文件进入永久区。AI 不得设为 True——
                永久区晋升须经用户终端确认（--allow-promote CLI flag）。

        Returns:
            CommitResult。
        """
        if not files:
            return CommitResult(status=CommitStatus.NOTHING_TO_COMMIT, message="empty files list")
        if not session_id:
            session_id = "unknown"

        # 归一化为绝对路径
        # 注意：用 os.path.abspath 而非 Path(f).resolve()——resolve() 在 Windows 上会
        # 规范化为物理目录的真实大小写，当 on-disk 与 git index 大小写不一致时（如
        # 09_audit vs 09_AUDIT）会导致 git add/commit 的 pathspec 不匹配。abspath
        # 保留传入路径大小写，与 git index 一致。
        # 内部比较逻辑（_collect_non_target_rel / _get_session_held_non_target 等）
        # 仍用 resolve() 归一化双方，比较时一致匹配，不受影响。
        abs_files = [os.path.abspath(f) for f in files]
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
                if self._is_git_tracked(rel):
                    existing.append(f)  # git 跟踪的已删除文件
        if not existing:
            return CommitResult(
                status=CommitStatus.NOTHING_TO_COMMIT,
                message="no existing or tracked files to commit",
            )

        # GATE-15 等效校验：弥补 --no-verify 绕过 pre-commit 的副作用
        ttl_passed, ttl_detail = self._check_frontmatter_ttl(existing)
        if not ttl_passed:
            return CommitResult(
                status=CommitStatus.METADATA_VIOLATION,
                message=f"frontmatter ttl 校验失败: {ttl_detail}",
            )

        # 永久区晋升门禁：检测新文件进入永久区，未获批准则阻断
        if not allow_promote:
            new_permanent = self._check_permanent_zone_new_files(existing)
            if new_permanent:
                rel_list = [
                    os.path.relpath(f, str(self.project_root)).replace("\\", "/")
                    for f in new_permanent
                ]
                return CommitResult(
                    status=CommitStatus.PROMOTION_BLOCKED,
                    message=(
                        f"永久区新文件未获批准（{len(new_permanent)} 个）: {rel_list}. "
                        f"用户须在终端用 --allow-promote 确认晋升。"
                        f"AI 不得自行批准。"
                    ),
                )

        # SSoT 兜底门禁（L2）：检测新增 .py 文件是否声明了已有 module_path
        # 防止 AI 绕过 scaffold 直接 Write 新文件后 commit
        # 真源是文件头部 [MODULE] 字段，反查通过 capability_lookup 实时扫描磁盘
        ssot_passed, ssot_detail = self._check_ssot_canonical(existing)
        if not ssot_passed:
            return CommitResult(
                status=CommitStatus.SSOT_VIOLATION,
                message=ssot_detail,
            )

        # GATE-11/N-16 等效校验：弥补 --no-verify 绕过 pre-commit 的副作用
        # N-16 是文件名项目内唯一性硬阻断，必须 commit 前拦截（防止同名漂移入历史）
        naming_passed, naming_detail = self._check_naming_uniqueness(existing)
        if not naming_passed:
            return CommitResult(
                status=CommitStatus.NAMING_VIOLATION,
                message=f"N-16 文件名唯一性校验失败: {naming_detail}",
            )

        # 追加 GW 标记
        gw_marker = _GW_MARKER_FMT.format(session_id=session_id)
        full_message = f"{message}\n\n{gw_marker}"

        try:
            with _GlobalCommitLock(self.project_root):
                return self._commit_locked(session_id, existing, full_message, gw_marker)
        except GatewayError as e:
            return CommitResult(status=CommitStatus.LOCK_TIMEOUT, message=str(e))

    def _is_git_tracked(self, rel_path: str) -> bool:
        """检查相对路径是否被 git 跟踪（case-insensitive pathspec）。

        根因：Windows 文件系统大小写不敏感，但 git pathspec 默认大小写敏感。
        当 on-disk 路径大小写（如 mod_inf_008）与 git index 大小写（如 MOD-CONTEXT_ENGINE）
        不一致时，``git ls-files --error-unmatch -- <path>`` 会误报"未跟踪"，
        导致 PROMOTION_BLOCKED 误杀已跟踪的修改文件。

        解法：使用 ``:(icase)`` pathspec magic 强制大小写不敏感匹配
        （git 2.x 内置特性，全平台可用）。
        """
        chk = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", f":(icase){rel_path}"],
            capture_output=True,
            cwd=str(self.project_root),
        )
        return chk.returncode == 0

    def _check_permanent_zone_new_files(self, files: list[str]) -> list[str]:
        """检测文件列表中是否有新文件（未 git 跟踪）进入永久区。

        永久区目录见 _PERMANENT_ZONE_DIRS。AI 创建的过程文档应放 docs/_working/，
        经用户批准后才能晋升到永久区。

        性能：单次 ``git ls-files`` 批量获取永久区所有已跟踪文件（:(icase) 大小写
        不敏感），避免 N 次 per-file subprocess 调用（4800+ 文件时 ~6min → <1s）。

        Args:
            files: 绝对路径列表。

        Returns:
            新文件（未跟踪 + 在永久区路径）的绝对路径列表。空列表 = 无需门禁。
        """
        # 筛选 commit 列表中落在永久区路径下的文件（大小写不敏感前缀匹配）
        zone_files: list[tuple[str, str]] = []  # (abs_path, rel_lower)
        for f in files:
            rel = os.path.relpath(f, str(self.project_root)).replace("\\", "/")
            rel_lower = rel.lower()
            if any(rel_lower.startswith(prefix) for prefix in _PERMANENT_ZONE_DIRS):
                zone_files.append((f, rel_lower))
        if not zone_files:
            return []

        # 单次 git ls-files 批量获取永久区所有已跟踪文件（:(icase) 大小写不敏感）
        # 根因：Windows on-disk 大小写（mod_inf_008）与 git index 大小写（MOD-CONTEXT_ENGINE）
        # 不一致，:(icase) pathspec magic 强制大小写不敏感匹配
        icase_specs = [f":(icase){d}" for d in _PERMANENT_ZONE_DIRS]
        result = subprocess.run(
            ["git", "ls-files", "--", *icase_specs],
            capture_output=True, text=True, cwd=str(self.project_root),
        )
        tracked_lower: set[str] = set()
        for line in result.stdout.splitlines():
            line = line.strip()
            if line:
                tracked_lower.add(line.lower())

        # commit 列表中永久区文件若不在已跟踪集合中 → 新文件 → 需门禁
        new_in_zone = [f for f, rel_lower in zone_files if rel_lower not in tracked_lower]
        return new_in_zone

    def _check_frontmatter_ttl(self, files: list[str]) -> tuple[bool, str]:
        """GATE-15 等效校验：检查 .md 文件 frontmatter ttl 字段。

        弥补 GitCommitGateway --no-verify 绕过 pre-commit 的副作用。
        调用 check_frontmatter_metadata.py 做增量校验（只校验本次 commit 的 .md）。
        当 .md 文件数 > _MAX_INLINE_PATHS 时，改用 --all-files 全量校验
        （避免 Windows WinError 206 命令行过长）。

        Args:
            files: 绝对路径列表。

        Returns:
            (passed, detail) — passed=True 表示通过；passed=False 时 detail 含违规详情。
        """
        # 只校验 docs/ 下的 .md 文件（与 pre-commit GATE-15 的 files 正则一致）
        md_files = [
            f for f in files
            if f.endswith(".md")
            and os.path.relpath(f, str(self.project_root)).replace("\\", "/").startswith("docs/")
        ]
        if not md_files:
            return True, "no .md files to check"

        check_script = (
            self.project_root
            / "scripts"
            / "governance"
            / "d3_metadata"
            / "check_frontmatter_metadata.py"
        )
        if not check_script.exists():
            # 校验脚本不存在时不阻断（防破坏性故障）
            return True, f"check script not found: {check_script}"

        cmd = [sys.executable, str(check_script)] + md_files
        # 文件数过多时用 --all-files 全量校验（避免 WinError 206 命令行过长）
        if len(md_files) > _MAX_INLINE_PATHS:
            cmd = [sys.executable, str(check_script), "--all-files"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(self.project_root),
        )
        if result.returncode == 0:
            return True, "ttl validation passed"
        # exit 1 = 有违规，exit 2 = 脚本异常
        detail = result.stderr.strip() or result.stdout.strip() or "unknown ttl validation error"
        return False, detail

    def _check_ssot_canonical(self, files: list[str]) -> tuple[bool, str]:
        """SSoT 兜底门禁（L2）：检测新增 .py 文件是否声明了已有 module_path。

        防止 AI 绕过 scaffold 直接 Write 新文件后 commit。
        真源是文件头部 [MODULE] 字段，反查通过 capability_lookup 实时扫描磁盘。

        只检查 src/zephyr/ 下的新增（未 git 跟踪）.py 文件。
        对每个新增文件，解析其 [MODULE] 头，提取 module_path，
        反查磁盘上是否有其他文件声明了相同 module_path。

        fail-open 策略：capability_lookup 不可用时不阻断（L1 scaffold 是主防线）。

        Args:
            files: 绝对路径列表。

        Returns:
            (passed, detail) — passed=True 表示通过；passed=False 时 detail 含违规详情。
        """
        # 筛选新增的 .py 文件（在 src/zephyr/ 下且未 git 跟踪）
        new_py_files: list[tuple[str, str]] = []  # (abs_path, rel_path)
        for f in files:
            rel = os.path.relpath(f, str(self.project_root)).replace("\\", "/")
            if not rel.startswith("src/zephyr/") or not rel.endswith(".py"):
                continue
            if self._is_git_tracked(rel):
                continue  # 已跟踪文件是修改不是新增，跳过
            new_py_files.append((f, rel))

        if not new_py_files:
            return True, "no new .py files to check"

        try:
            from zephyr.governance.capability_lookup import CapabilityLookup
            lookup = CapabilityLookup()
        except Exception as e:
            # fail-open：capability_lookup 不可用时不阻断
            return True, f"capability_lookup 不可用，跳过 SSoT 兜底检查: {e}"

        # 检测逻辑调用共享函数（唯一真源：capability_lookup.check_ssot_conflicts）
        # L2 只负责筛选新增 .py（上方 _is_git_tracked）和格式化输出（下方），
        # 检测核心（解析头 + 反查 + 排除自己）收拢到 check_ssot_conflicts，L3 共用。
        conflicts = lookup.check_ssot_conflicts(new_py_files)
        if not conflicts:
            return True, "ssot check passed"

        violation_lines = [
            f"{c.rel_path} 声明 module_path={c.module_path}"
            f" 与已有文件冲突: {', '.join(c.conflicts)}"
            for c in conflicts
        ]
        detail = (
            "SSoT 冲突——新增文件声明了已有 module_path（绕过 scaffold 创建）:\n  "
            + "\n  ".join(violation_lines)
            + "\n  修复指令：删除上述新增文件，扩展对应的已有文件后重新 commit（RULE-EIGHT 扩展优先于新建）"
            + "\n  查已有 canonical：python -m zephyr.governance.capability_lookup --find <关键词>"
            + " 或 reg.get(\"capability_id\") 反查真源文件路径"
        )
        return False, detail

    def _check_naming_uniqueness(self, files: list[str]) -> tuple[bool, str]:
        """GATE-11/N-16 等效校验：检查文件名项目内唯一性。

        弥补 GitCommitGateway --no-verify 绕过 pre-commit 的副作用。
        N-16 是项目级唯一性检查——当本次 commit 涉及 tests/ 或 docs/ 下文件时，
        调用 check_naming_convention.py --scan 做 N-16 检测。

        真源：trae_028_doc_structure_naming.yaml v1.4.0 §gov_doc_003_filename_uniqueness

        Args:
            files: 绝对路径列表。

        Returns:
            (passed, detail) — passed=True 表示通过；passed=False 时 detail 含违规详情。
        """
        # 只在本次 commit 涉及 tests/ 或 docs/ 下文件时才检查（性能优化）
        involves_naming_dirs = any(
            os.path.relpath(f, str(self.project_root)).replace("\\", "/").startswith(
                ("tests/", "docs/")
            )
            for f in files
        )
        if not involves_naming_dirs:
            return True, "no files in tests/ or docs/"

        check_script = (
            self.project_root
            / "scripts"
            / "governance"
            / "d3_metadata"
            / "check_naming_convention.py"
        )
        if not check_script.exists():
            # 校验脚本不存在时不阻断（fail-open，防破坏性故障）
            return True, f"check script not found: {check_script}"

        # 调用 --scan 模式，N-16 不受 --warn-only 影响会硬阻断
        cmd = [sys.executable, str(check_script), "--scan", "--warn-only"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(self.project_root),
        )
        if result.returncode == 0:
            return True, "naming uniqueness passed"
        # exit 1 = 有 N-16 违规（硬阻断，不受 --warn-only 影响）
        output = result.stdout + result.stderr
        n16_lines = [line for line in output.splitlines() if "N-16" in line]
        detail = "\n".join(n16_lines) if n16_lines else output.strip() or "unknown naming violation"
        return False, detail

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
                    # 3. session 隔离 stash 非目标 unstaged 变更
                    #    _stash_other_files 内部按 session held 过滤候选：
                    #    - feature 禁用/未注册 → 回退 stash 全部非目标
                    #      （等效原 --keep-index 语义：目标已 staged，非目标被 stash）
                    #    - session 隔离生效 → 只 stash 当前 session held 的非目标
                    #    - 候选为空 → 跳过 stash（其他 session WIP 留工作区）
                    #    目标文件已通过 git add --pathspec-from-file 全量 staged，
                    #    故 stash 非目标（显式 pathspec）不影响 staged 目标。
                    stashed, stash_ref = self._stash_other_files(session_id, files)

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
                pop_ok = self._restore_stash(stash_ref)
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
            # Post-commit 漂移对账（P2-T1：声明式 ReconciliationRegistry，替代硬编码 _post_commit_reconcile）
            # 斩断 --no-verify 导致的 drift 循环：每个被绕过的 GATE 注册一个 reconciler，
            # commit 完成后由 registry 统一调度（trigger 命中即执行，异常降级为 warn 不阻断）
            if result.status == CommitStatus.OK:
                try:
                    reconcile_results = self._reconciliation_registry.reconcile_for(
                        files, session_id
                    )
                    result.reconcile = reconcile_results
                    for rr in reconcile_results:
                        if rr.action == "auto_committed":
                            logger.info(
                                "GitCommitGateway: post-commit reconcile auto-committed "
                                "(session=%s): %s", session_id, rr.detail
                            )
                        elif rr.action == "warn":
                            logger.warning(
                                "GitCommitGateway: post-commit reconcile warning "
                                "(session=%s): %s", session_id, rr.detail
                            )
                except Exception as e:
                    logger.warning("GitCommitGateway: post-commit reconcile failed: %s", e)
            # 事件驱动红蓝触发 (MOD-INF-030)：正式脚本/模块提交 →
            # 写异步触发记录（毫秒级，锁内）→ 消费线程在锁外跑 TIER_1 对抗。
            # 就位+门禁激活：始终 emit；门禁在消费时检查。
            if result.status == CommitStatus.OK:
                try:
                    self._post_commit_red_blue_trigger(files, session_id, result.commit_hash)
                except Exception as e:
                    logger.warning("GitCommitGateway: red-blue trigger emit failed: %s", e)
            # P4-T2: session shutdown handoff——写 .runtime/handoffs/handoff_<sid>.json
            # 供下一 session startup 读取（crash recovery：每次 commit 后更新最新状态）
            # 注意：此处在 _commit_locked() 内，变量名是 full_message（含 GW 标记）非 message
            if result.status == CommitStatus.OK:
                try:
                    from zephyr.governance.phase_manager import session_shutdown
                    session_shutdown(session_id, summary=full_message)
                except Exception as e:
                    logger.warning("GitCommitGateway: session_shutdown handoff failed: %s", e)
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
        """选择性 stash 非本次 files 的已修改文件（session 隔离版）。

        策略:
        1. _collect_non_target_rel 收集非目标已跟踪变更（相对路径，跳过 ??）
        2. _get_session_held_non_target 筛出 session 隔离候选：
           - feature 禁用/未注册/held 空 → 回退原逻辑（stash 全部非目标）
           - 否则只 stash 当前 session 持有的非目标文件（其他 session 的 WIP 留在工作区）
        3. 候选为空 → 跳过 stash
        4. 候选 > _MAX_INLINE_PATHS → --pathspec-from-file 避免 WinError 206；
           否则 git stash push -m <session_id> -- <candidates>

        Returns:
            (是否 stash 了文件, stash_ref)
        """
        all_non_target = self._collect_non_target_rel(target_files)
        if not all_non_target:
            return False, ""

        isolation_active, candidates = self._get_session_held_non_target(
            session_id, target_files, all_non_target
        )
        if not candidates:
            # 候选为空：session 隔离下无需 stash（其他 session WIP 留工作区），
            # 或回退模式下无非目标变更
            if isolation_active:
                logger.info(
                    "GitCommitGateway: session 隔离生效，无非目标候选需要 stash (session=%s)",
                    session_id,
                )
            return False, ""

        mode = "session-aware" if isolation_active else "fallback"
        logger.info(
            "GitCommitGateway: stash 模式=%s, 候选=%d 个非目标文件 (session=%s)",
            mode, len(candidates), session_id,
        )

        stash_msg = f"gw:{session_id}"
        spec_file: str | None = None
        try:
            if len(candidates) > _MAX_INLINE_PATHS:
                # 大候选列表 → --pathspec-from-file 避免 Windows CLI 长度限制
                spec_file = self._write_pathspec_file(
                    [str(self.project_root / c) for c in candidates]
                )
                stash_result = self._run_git(
                    ["git", "stash", "push", "-m", stash_msg, f"--pathspec-from-file={spec_file}"]
                )
            else:
                stash_result = self._run_git(
                    ["git", "stash", "push", "-m", stash_msg, "--"] + candidates
                )
        finally:
            if spec_file:
                try:
                    os.remove(spec_file)
                except OSError:
                    pass

        if stash_result.returncode != 0:
            # stash 失败可能是"No local changes to save"——非错误
            stderr = stash_result.stderr.strip()
            if "No local changes" in stderr or "no changes" in stderr.lower():
                return False, ""

            # 防御：Windows 上 git stash push 可能报错（如 "cannot spawn git:
            # Filename too long"）但 stash 实际已创建。用 git stash list 验证
            # 栈顶是否有本次 session 的 stash，有则视为成功。
            verify_result = self._run_git(
                ["git", "stash", "list", "--format=%gd|%gs", "-1"]
            )
            if verify_result.returncode == 0 and verify_result.stdout.strip():
                ref_msg = verify_result.stdout.strip()
                if stash_msg in ref_msg:
                    stash_ref = ref_msg.split("|", 1)[0]
                    logger.warning(
                        "GitCommitGateway: git stash push 报错但 stash 已创建 "
                        "(session=%s ref=%s, stderr=%s)",
                        session_id, stash_ref, stderr[:200],
                    )
                    return True, stash_ref

            logger.warning("GitCommitGateway: git stash push 失败: %s", stderr)
            return False, ""

        # 获取 stash ref（stash@{0}）
        list_result = self._run_git(["git", "stash", "list", "--format=%gd|%gs", "-1"])
        stash_ref = ""
        if list_result.returncode == 0 and list_result.stdout.strip():
            stash_ref = list_result.stdout.strip().split("|", 1)[0]
        logger.info("GitCommitGateway: stash 了 %d 个非本次文件 ref=%s", len(candidates), stash_ref)
        return True, stash_ref

    def _restore_stash(self, stash_ref: str = "") -> bool:
        """恢复 stash（git stash pop）。

        Args:
            stash_ref: 要恢复的 stash 引用（如 stash@{0}）。为空则 pop 栈顶。

        Returns:
            True=成功恢复, False=pop 失败（数据保留在 stash）
        """
        if stash_ref:
            pop_result = self._run_git(["git", "stash", "pop", stash_ref])
        else:
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

    def _post_commit_red_blue_trigger(
        self,
        files: list[str],
        session_id: str,
        commit_hash: str,
    ) -> None:
        """事件驱动红蓝触发 (MOD-INF-030)：正式脚本/模块提交 → 写异步触发记录。

        锁内轻量操作（毫秒级）：扫描提交文件头是否含 [BLUEPRINT]/[MODULE]
        标记，命中则写 trigger record 到 data/red_blue/trigger_queue/。
        真实对抗由 commit_trigger.RedBlueTriggerConsumer 守护线程在锁外异步执行
        （受 AUTOMATION-GATE 门禁 + CircuitBreaker 频率保护）。
        """
        from zephyr.security.adversarial_validation.commit_trigger import (
            detect_formal_files,
            write_trigger_record,
        )
        formal_files = detect_formal_files(files)
        if not formal_files:
            return
        write_trigger_record(commit_hash, session_id, formal_files)
        logger.info(
            "GitCommitGateway: red-blue trigger emitted (session=%s hash=%s formal=%d)",
            session_id, commit_hash[:8], len(formal_files),
        )

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

        每行加 ``:(icase)`` 前缀——兼容 Windows on-disk 大小写与 git index
        大小写不一致（如 on-disk ``mod_inf_008`` vs git index ``MOD-CONTEXT_ENGINE``）。
        无 ``:(icase)`` 时 ``git add`` pathspec 大小写敏感，会误报
        "pathspec did not match any file(s) known to git"。

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
                f.write(f":(icase){rel}\n")
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
