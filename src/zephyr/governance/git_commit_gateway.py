# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §ghost-commit-gateway
# [MODULE] zephyr.governance.git_commit_gateway
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__; zephyr.security.access_control.session_concurrency
# [CONSUMERS] zephyr.governance.task_repo.TaskRepository._auto_commit_on_completion; scripts/git_commit.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 全项目唯一合法 git commit 入口；全局跨进程串行锁（.ailocks/git_commit_global.lock，TTL=1800s）；选择性 stash 非本次 files；commit 用 -F <msg_file> 避免 PowerShell 特殊字符问题（RULE-TWENTY 裁定2）；stash pop 失败保留 stash 不丢数据；环境变量 ZEPHYR_COMMIT_GATEWAY=1 + commit message 追加 [GW:session_id] 标记；session 隔离 stash（已注册 session 只 stash 其 held_files 中的非目标文件，未注册回退原逻辑）；feature flag ZEPHYR_SESSION_AWARE_STASH=0 强制禁用；rename fallback（方案 A 红蓝审核 v2：_commit_with_file_message 内置 rename 检测真源唯一，pathspec 为默认多 session 安全，_has_staged_renames 检测到目标文件 R100 时自动切换无 pathspec + _verify_staged_is_clean 验证 staged 区只有目标文件，防误提交其他 session WIP；_commit_locked 和 _commit_auto 无需重复调用，reconciler 路径自动获得 rename 保护）；_collect_non_target_rel 正确解析 rename 格式 "R old -> new" 提取新路径
# [MODIFY-GUARD] _GlobalCommitLock 的 TTL 与锁文件名；commit message 的 GW 标记格式；ZEPHYR_COMMIT_GATEWAY 环境变量名
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] GatewayError on lock timeout；StashConflictWarning on stash pop 失败（数据保留在 stash）；CommitResult.status 暴露结果
# [TESTS] tests/test_git_commit_gateway.py
# [A_module] module_id=MOD-GOV-git_commit_gateway | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
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
import re
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
    make_ghost_reconciler,
    make_path_tree_reconciler,
    make_rule_catalog_reconciler,
    make_working_docs_reconciler,
    make_domain_doc_reconciler,
    make_precommit_id_uniqueness_reconciler,
    make_rules_integrity_reconciler,
    make_vocab_change_reconciler,
    make_commit_gateway_audit_reconciler,
    make_deprecated_directory_reconciler,
)
from zephyr.governance.capability_lookup import REGISTRY_YAML  # registry 路径真源唯一（治本：消除 _check_capability_aliases / _load_protected_scripts 硬编码分裂）
from zephyr.shared.infra.process_pool import is_pid_alive  # 僵尸锁检测真源唯一（红蓝对抗归一：曾三处分裂，现统一到 process_pool.py）
from zephyr.shared.io.frontmatter_utils import parse_frontmatter_from_file

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
_MAX_INLINE_MD_FILES = 50  # 前端校验 .md 文件数阈值，超过时改用 --all-files 全量模式避免 Windows CLI 长度限制 (WinError 206)
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

# 生成器豁免子目录——落在此清单内的新文件跳过永久区晋升门禁（PROMOTION_BLOCKED）
# 真源：capability_canonical_file_registry.yaml outputs 字段 + AGENTS.md §generator-exempt-zones
# 约束：这些目录是生成器专用路径，生成器是唯一合法修改源（约定，非技术强制）
# 不含 taskcards/ 子目录（手工任务卡）和 04_architecture_principles_decisions/（手工架构决策）
_GENERATOR_EXEMPT_SUBDIRS: tuple[str, ...] = (
    "docs/02_enterprise_architecture/00_overview_entry/",
    "docs/02_enterprise_architecture/01_global_architecture_diagram/",
    "docs/02_enterprise_architecture/02_domain_architecture_docs/",
    "docs/02_enterprise_architecture/03_governance_reports/",
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
    SCRIPT_INTEGRITY_VIOLATION = "SCRIPT_INTEGRITY_VIOLATION"  # 受保护脚本完整性锚点缺失（自篡改纵深防御）
    REPO_ROOT_VIOLATION = "REPO_ROOT_VIOLATION"  # .py 文件使用 parents[N] 反模式而非 REPO_ROOT（SSoT 绕过）
    PURE_ASSERTION_VIOLATION = "PURE_ASSERTION_VIOLATION"  # 规则文档含过渡文本（GOV-DOC-016 纯陈述原则）


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
                    # 治本：先检查 PID 是否存活，僵尸锁立即清理（零窗口期）
                    # 根因：进程崩溃时 __exit__ 不执行，仅靠 TTL 30min 过期太慢
                    # （_LOCK_TIMEOUT_DEFAULT 60s << 30min，实测阻塞 3min+）
                    holder_pid = data.get("pid")
                    if holder_pid is not None and not is_pid_alive(int(holder_pid)):
                        logger.warning(
                            "_GlobalCommitLock: 持有进程 PID %s 已死亡，清理僵尸锁: %s",
                            holder_pid, self._lock_file,
                        )
                        try:
                            os.remove(self._lock_file)
                        except OSError:
                            pass
                        continue
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
        target_files 用绝对路径归一化匹配（resolve + normcase），排除本次 commit 目标。

        治本（rename 路径解析）：``R  old -> new`` 格式的 rename 行，
        ``line[3:]`` 得到 ``old -> new`` 无法被 ``Path()`` 解析。提取新路径
        （rename 目标），确保其他 session 的 staged rename 能被正确 stash。

        治本（Windows 大小写不敏感匹配）：``Path.resolve()`` 在文件不存在时
        （如 staged delete + 文件已从磁盘删除）无法归一化大小写，导致
        target_files 路径与 git status 路径大小写不一致时误判目标为非目标，
        进而被 ``_stash_other_files`` stash 走 staged delete。解法：用
        ``os.path.normcase()`` 对 resolve 结果做大小写不敏感归一化。
        """
        status_result = self._run_git(["git", "status", "--porcelain"])
        if status_result.returncode != 0:
            logger.warning(
                "GitCommitGateway: git status 失败: %s", status_result.stderr.strip()
            )
            return []
        target_set = {
            os.path.normcase(str(Path(f).resolve())) for f in target_files
        }
        result: list[str] = []
        for line in status_result.stdout.splitlines():
            if not line.strip() or line.startswith("??"):
                continue
            path = line[3:].strip().strip('"')
            # rename 格式 "R  old -> new"：提取新路径（rename 目标）
            if " -> " in path:
                path = path.split(" -> ", 1)[1].strip().strip('"')
            abs_path = os.path.normcase(str((self.project_root / path).resolve()))
            if abs_path not in target_set:
                result.append(path)
        return result

    def _register_default_reconcilers(self) -> None:
        """注册默认 post-commit reconciler（P2-T1 框架 + P2-T2 manifest + P2-T3 baseline_aware + P2-T5 ghost + P2-T6 working_docs + P2-T7 domain_doc + P2-T8 id_uniqueness + P2-T9 vocab_change + 红蓝发现1 rules_integrity + P3收尾 rule_catalog）。

        P2-T2: manifest 对账逻辑迁移为 ``make_manifest_reconciler`` 工厂。
        P2-T3: baseline_aware 对账（GATE-REG-BL 补偿，非阻断，报告落盘）。
        P2-T5: ghost 对账（depgraph 对称漂移检测，删除 commit 触发 diagnose_depgraph）。
        P2-T6: working_docs 对账（_working/ 幽灵引用检测，删除 commit 触发归档，治 AI 工作文档堆积）。
        P2-T7: domain_doc 重生（commit depgraph.db 后自动重生域 .md/.mmd 制品，治手工生成漂移）。
        P2-T8: id_uniqueness 兜底（GATE-ID-UNIQ post-compensation，commit .pre-commit-config.yaml 后重校 hook id 唯一性，非阻断报告落盘，兜底 --no-verify 绕过）。
        P2-T9: vocab_change 纠偏（GATE-VOCAB-CHANGE，commit ttl_vocabulary.yaml 后自动重判所有 docs/*.md 的 ttl，治词表变更后 ttl 漂移）。
        红蓝发现1: rules_integrity 基线同步（GATE-RULES-INTEGRITY，commit RULES_MANIFEST 文件后自动 --register 重注册本地 golden hash 基线，治合法 commit 后 C 层误报 TAMPERED）。
        P3收尾: rule_catalog 同步（GATE-RULE-CATALOG，commit rules/ 下文件后自动重新生成 rule_catalog_registry.yaml，治 catalog stale 导致 depgraph.db 数据污染）。
        """
        self._reconciliation_registry.register(make_manifest_reconciler(self))
        self._reconciliation_registry.register(make_path_tree_reconciler(self))
        self._reconciliation_registry.register(make_rule_catalog_reconciler(self))
        self._reconciliation_registry.register(make_baseline_aware_reconciler(self))
        self._reconciliation_registry.register(make_precommit_id_uniqueness_reconciler(self))
        self._reconciliation_registry.register(make_rules_integrity_reconciler(self))
        self._reconciliation_registry.register(make_vocab_change_reconciler(self))
        self._reconciliation_registry.register(make_ghost_reconciler(self))
        self._reconciliation_registry.register(make_working_docs_reconciler(self))
        self._reconciliation_registry.register(make_domain_doc_reconciler(self))
        self._reconciliation_registry.register(make_commit_gateway_audit_reconciler(self))  # GATE-COMMIT-GW-AUDIT 缺口4接线：裸commit post-compensation 审计
        self._reconciliation_registry.register(make_deprecated_directory_reconciler(self))  # GATE-DEPRECATED-DIR 09_audit 治本加固：post-commit 检测废弃目录重建

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

        # S6 预防层：_working/ 新 .md 必须声明 completes_when（完成条件）
        # 治 AI 工作文档堆积：强制 AI 创建 _working/ 文档时声明可验证的完成条件
        working_passed, working_detail = self._check_working_docs_completes_when(existing)
        if not working_passed:
            return CommitResult(
                status=CommitStatus.METADATA_VIOLATION,
                message=f"_working/ 新文档 completes_when 校验失败: {working_detail}",
            )

        # GATE-SRC-NO-DATA 等效校验：弥补 --no-verify 绕过 pre-commit 的副作用
        # 真源：trae_047 §gov_eng_002_directory_mapping 禁止规则
        src_no_data_passed, src_no_data_detail = self._check_src_no_data(existing)
        if not src_no_data_passed:
            return CommitResult(
                status=CommitStatus.METADATA_VIOLATION,
                message=f"src/ 禁 data/ 子目录校验失败: {src_no_data_detail}",
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

        # 受保护脚本完整性校验（A 层纵深防御）：AST 锚点校验
        # 治脚本自篡改缺口：检测脚本被改 → pre-commit + reconciler 两层防线同时失效
        # gateway 内嵌校验，--no-verify 绕不过（对标 _check_ssot_canonical 模式）
        integrity_passed, integrity_detail = self._check_protected_script_integrity(existing)
        if not integrity_passed:
            return CommitResult(
                status=CommitStatus.SCRIPT_INTEGRITY_VIOLATION,
                message=f"受保护脚本完整性校验失败: {integrity_detail}",
            )

        # 中文 aliases 门禁（红蓝对抗修复2）：检测 capability_canonical_file_registry.yaml
        # 的 aliases 字段是否含 CJK 字符——禁堆中文同义词 alias 裁定的代码强制。
        # gateway 内嵌校验，--no-verify 绕不过（对标 _check_ssot_canonical 模式）。
        aliases_passed, aliases_detail = self._check_capability_aliases(existing)
        if not aliases_passed:
            return CommitResult(
                status=CommitStatus.NAMING_VIOLATION,
                message=f"中文 aliases 违规: {aliases_detail}",
            )

        # 废弃目录门禁（09_audit 治本加固）：检测提交文件是否位于 docs/09_audit/ 等
        # 已废弃目录下——gateway 内嵌，--no-verify 绕不过（对标 _check_capability_aliases 模式）
        deprecated_passed, deprecated_detail = self._check_deprecated_directories(existing)
        if not deprecated_passed:
            return CommitResult(
                status=CommitStatus.NAMING_VIOLATION,
                message=f"废弃目录违规: {deprecated_detail}",
            )

        # REPO_ROOT 真源归一门禁：检测 parents[N] 反模式（SSoT 绕过）
        # 约定见 AGENTS.md §7 REPO_ROOT 真源归一——REPO_ROOT 是仓库根常量唯一真源
        # 移植自 _tmp_fix_parents.py 检测逻辑，仅检测不修复
        repo_root_passed, repo_root_detail = self._check_repo_root_usage(existing)
        if not repo_root_passed:
            return CommitResult(
                status=CommitStatus.REPO_ROOT_VIOLATION,
                message=f"REPO_ROOT 反模式: {repo_root_detail}",
            )

        # GOV-DOC-016 纯陈述原则门禁：规则文档禁止过渡文本
        # 真源：trae_030_doc_numbering_metadata.yaml §gov_doc_016_pure_assertion
        # 规则文档只含当前有效规则的肯定陈述句，历史通过 git log 追踪
        pure_passed, pure_detail = self._check_pure_assertion(existing)
        if not pure_passed:
            return CommitResult(
                status=CommitStatus.PURE_ASSERTION_VIOLATION,
                message=f"GOV-DOC-016 纯陈述违规: {pure_detail}",
            )

        # 追加 GW 标记
        gw_marker = _GW_MARKER_FMT.format(session_id=session_id)
        full_message = f"{message}\n\n{gw_marker}"

        try:
            with _GlobalCommitLock(self.project_root):
                result = self._commit_locked(session_id, existing, full_message, gw_marker)
        except GatewayError as e:
            return CommitResult(status=CommitStatus.LOCK_TIMEOUT, message=str(e))

        # Post-commit reconciler 在锁外运行（reconciler 可通过 _commit_auto 独立获取锁 auto-commit）
        # 治本：原设计在 _commit_locked.finally 内调度，reconciler 无法获取锁（死锁），
        # 且 reconciler 裸调 _run_git commit 绕过 ttl 校验。移到锁外后 reconciler 经
        # _commit_auto 统一入口，ttl 校验无法绕过。
        if result.status == CommitStatus.OK:
            try:
                reconcile_results = self._reconciliation_registry.reconcile_for(
                    existing, session_id
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
        return result

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

    def _is_staged_delete(self, rel_path: str) -> bool:
        """检查相对路径是否为 staged delete（已从 index 移除但仍在 HEAD）。

        根因：``_stage_gitignored_tracked`` 的 ``existing`` 分支对磁盘上仍存在
        的 gitignored-tracked 文件执行 ``git add -f``。若用户已 ``git rm --cached``
        暂存删除，``_is_git_tracked`` 返回 False（不在 index）使 ``ex_tracked``
        为空，理论上不会触发 ``git add -f``。但 ``_is_git_tracked`` 依赖
        ``git ls-files`` 行为，在 ``:(icase)`` magic 或 git 版本差异下可能
        不稳定。本方法作为纵深防御，显式识别 staged delete 状态，确保
        ``git add -f`` 绝不撤销用户的 staged delete。

        判据：不在 index（``git ls-files --error-unmatch`` 失败）
              AND 在 HEAD（``git cat-file -e HEAD:<path>`` 成功）。
        """
        if self._is_git_tracked(rel_path):
            return False  # 在 index 中，不是 staged delete
        chk = subprocess.run(
            ["git", "cat-file", "-e", f"HEAD:{rel_path}"],
            capture_output=True,
            cwd=str(self.project_root),
        )
        return chk.returncode == 0

    def _should_use_no_pathspec(self, files: list[str], normal_files: list[str]) -> bool:
        """判断本次 commit 是否应用无 pathspec 模式（staged delete 保护核心决策点）。

        根因：``git commit -- <pathspec>`` 提交**工作区状态**而非**暂存区状态**。
        对 gitignored 文件，工作区状态无法被 stage（gitignore 阻止），staged
        delete（``git rm --cached``）被静默跳过（历史教训：commit 32ead90e
        漏提交 5 个 egg_info 删除）。无 pathspec 模式提交所有 staged 变更，
        staged delete 正确包含，``_verify_staged_is_clean`` 确保只提交目标文件。

        判据：``normal_files`` 是 ``files`` 中非 gitignored 的子集，数量不等
        说明目标含 gitignored 文件 → 必须用无 pathspec commit。

        .. note::
            本方法是 staged delete 保护的核心决策点，受 integrity_anchors
            保护（capability_canonical_file_registry.yaml），删除/篡改会触发
            SCRIPT_INTEGRITY_VIOLATION 阻断 commit。调用点在 ``_commit_locked``，
            AGENTS.md §8 L212 警告勿删调用。
        """
        return len(normal_files) < len(files)

    def _filter_gitignored(self, files: list[str]) -> list[str]:
        """返回 ``files`` 中被 ``.gitignore`` 忽略的绝对路径子集。

        用 ``git check-ignore --no-index`` 批量检测（exit 0=有忽略项，1=无）。

        关键：必须加 ``--no-index``。默认 ``check-ignore`` 会跳过已跟踪文件——
        即使它们匹配 ``.gitignore``。而本场景的根因正是"已跟踪 + 已 gitignore"
        （如 ``.trae/documents/`` 被 gitignore 但文件仍被跟踪且已删除），
        不加 ``--no-index`` 会漏检，导致后续 ``git add`` 整批失败。

        大小写不敏感比对（Windows on-disk vs git index 大小写可能不一）。

        分批检测：避免大批量文件（如 4688 个 rename）触发 Windows CLI
        长度限制（WinError 206）。每批 300 个路径（约 24000 字符 < 32767 限制）。
        """
        if not files:
            return []
        rels = [
            os.path.relpath(f, str(self.project_root)).replace("\\", "/") for f in files
        ]
        # 分批检测，避免 Windows CLI 长度限制 (WinError 206)
        ignored_rels: set[str] = set()
        _BATCH = 300
        for i in range(0, len(rels), _BATCH):
            batch = rels[i : i + _BATCH]
            chk = self._run_git(["git", "check-ignore", "--no-index", "--"] + batch)
            # returncode 0 = 有忽略项；1 = 无忽略；其他 = 异常（视为无忽略，不阻断）
            if chk.returncode == 0 and chk.stdout:
                for line in chk.stdout.splitlines():
                    if line.strip():
                        ignored_rels.add(line.strip().lower())
        return [f for f, rel in zip(files, rels) if rel.lower() in ignored_rels]

    def _stage_gitignored_tracked(
        self, files: list[str]
    ) -> tuple[bool, str, list[str]]:
        """暂存 gitignored 且已跟踪的文件，返回剩余可正常 ``git add`` 的文件列表。

        根因：``git add`` 对 gitignored 路径（即使已跟踪且已删除）整批拒绝：
        ``The following paths are ignored by one of your .gitignore files``。
        解法：分离 gitignored 文件，按状态分别暂存——

          - 已删除（不在磁盘）+ 已跟踪 → ``git rm --cached --ignore-unmatch``
            （暂存删除；git rm 不检查 gitignore）
          - 已修改（在磁盘）+ 已跟踪 → ``git add -f``（强制暂存修改）
          - 未跟踪的 gitignored → 跳过（不应入库；从 normal_files 也排除）

        剩余非 gitignored 文件由调用方走原 ``git add`` 逻辑。commit 的 pathspec
        仍用完整 ``files``（含 gitignored），以便 ``git commit -- <path>`` 提交
        上述已暂存的删除/修改（git commit pathspec 不检查 gitignore）。

        Returns:
            (success, error_message, normal_files) —— normal_files 供正常
            ``git add`` 使用（已排除全部 gitignored 路径）。
        """
        ignored = self._filter_gitignored(files)
        if not ignored:
            return True, "", list(files)
        ignored_set = {os.path.abspath(f) for f in ignored}
        normal_files = [f for f in files if os.path.abspath(f) not in ignored_set]
        # 分离已删除 vs 已存在
        deleted: list[str] = []
        existing: list[str] = []
        for f in ignored:
            (existing if os.path.isfile(f) else deleted).append(f)
        # 已删除 + 已跟踪 → git rm --cached（暂存删除）
        if deleted:
            del_rels = [
                os.path.relpath(f, str(self.project_root)).replace("\\", "/")
                for f in deleted
            ]
            del_tracked = [
                f for f, rel in zip(deleted, del_rels) if self._is_git_tracked(rel)
            ]
            if del_tracked:
                r = self._run_git(
                    ["git", "rm", "--cached", "--ignore-unmatch", "--"] + del_tracked
                )
                if r.returncode != 0:
                    return False, f"git rm --cached failed: {r.stderr.strip()}", normal_files
        # 已存在 + 已跟踪 → git add -f（强制暂存修改）
        # 治本（staged delete 保护）：跳过 staged delete 文件——用户已 git rm --cached
        # 暂存删除，git add -f 会撤销该删除（重置 index 到工作区状态）。_is_git_tracked
        # 对 staged delete 返回 False（不在 index），理论上已排除，但 _is_staged_delete
        # 作为纵深防御确保万无一失（防 :(icase) magic 或 git 版本差异下的 _is_git_tracked
        # 不稳定）。
        if existing:
            ex_rels = [
                os.path.relpath(f, str(self.project_root)).replace("\\", "/")
                for f in existing
            ]
            ex_tracked = [
                f for f, rel in zip(existing, ex_rels)
                if self._is_git_tracked(rel) and not self._is_staged_delete(rel)
            ]
            if ex_tracked:
                r = self._run_git(["git", "add", "-f", "--"] + ex_tracked)
                if r.returncode != 0:
                    return False, f"git add -f failed: {r.stderr.strip()}", normal_files
        return True, "", normal_files

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
            # 生成器豁免子目录内的文件跳过永久区晋升门禁
            # （生成器专用路径，生成器可自由创建/删除，不受 PROMOTION_BLOCKED 阻断）
            if any(rel_lower.startswith(exempt) for exempt in _GENERATOR_EXEMPT_SUBDIRS):
                continue
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
        """GATE-15 等效校验：检查 .md + .py 文件 ttl 字段。

        弥补 GitCommitGateway --no-verify 绕过 pre-commit 的副作用。
        调用 check_frontmatter_metadata.py 做增量校验（只校验本次 commit 的 .md/.py）。
        当文件数 > _MAX_INLINE_MD_FILES 时，改用 --all-files 全量校验
        （避免 Windows WinError 206 命令行过长）。

        格式路由（真源唯一——check_frontmatter_metadata.py 内部根据扩展名分发）：
        - .md → parse_frontmatter()（YAML frontmatter）
        - .py → parse_py_header()（# [TTL] value 注释行）

        Args:
            files: 绝对路径列表。

        Returns:
            (passed, detail) — passed=True 表示通过；passed=False 时 detail 含违规详情。
        """
        # 校验 docs/ 下的 .md + src/scripts/tests/ 下的 .py
        ttl_files: list[str] = []
        for f in files:
            rel = os.path.relpath(f, str(self.project_root)).replace("\\", "/")
            if f.endswith(".md") and rel.startswith("docs/"):
                ttl_files.append(f)
            elif f.endswith(".py") and (
                rel.startswith("src/")
                or rel.startswith("scripts/")
                or rel.startswith("tests/")
            ):
                ttl_files.append(f)
        if not ttl_files:
            return True, "no .md/.py files to check"

        check_script = (
            self.project_root
            / "scripts"
            / "governance"
            / "d3_metadata"
            / "check_frontmatter_metadata.py"
        )
        if not check_script.exists():
            # fail-closed：校验脚本缺失是异常状态，必须阻断
            # 治本：原 fail-open 设计会让 ttl 校验在脚本缺失时完全失效，
            # 违规文件可静默入库。脚本缺失说明环境损坏，应阻断而非放行。
            return False, f"check script not found: {check_script}"

        cmd = [sys.executable, str(check_script)] + ttl_files
        # 文件数过多时用 --all-files 全量校验（避免 WinError 206 命令行过长）
        if len(ttl_files) > _MAX_INLINE_MD_FILES:
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

    def _check_working_docs_completes_when(self, files: list[str]) -> tuple[bool, str]:
        """S6 预防层：检查 docs/_working/ 新 .md 文件必须含 completes_when 字段。

        治 AI 工作文档堆积为漂移源：强制 AI 在创建 _working/ 文档时声明完成条件，
        使 GATE-WORKING-DOCS reconciler 能基于此条件判定失效并自动归档。

        规则真源：docs/_working/index.md §三（人类/AI 可读描述）。
        本方法是该规则的可执行实现——改规则先改 README，再同步本方法。

        仅检查新增文件（未 git 跟踪）——已跟踪文件不阻断（不破坏存量）。
        README.md 已跟踪，不受影响。

        Args:
            files: 绝对路径列表。

        Returns:
            (passed, detail) — passed=True 表示通过；passed=False 时 detail 含违规详情。
        """
        new_working_mds: list[str] = []
        for f in files:
            if not f.endswith(".md"):
                continue
            rel = os.path.relpath(f, str(self.project_root)).replace("\\", "/")
            if not rel.lower().startswith("docs/_working/"):
                continue
            # 只检查新文件（未 git 跟踪）——存量文件不阻断
            if self._is_git_tracked(rel):
                continue
            new_working_mds.append(f)

        if not new_working_mds:
            return True, "no new _working/ .md files to check"

        violations: list[str] = []
        for f in new_working_mds:
            metadata = parse_frontmatter_from_file(f)
            if metadata is None:
                violations.append(f"{os.path.basename(f)}: 缺少 frontmatter")
                continue
            completes_when = metadata.get("completes_when")
            if not completes_when or not str(completes_when).strip():
                violations.append(
                    f"{os.path.basename(f)}: 缺少 completes_when 字段"
                    "（_working/ 新文档必须声明可验证的完成条件）"
                )

        if violations:
            return False, "; ".join(violations)
        return True, f"completes_when validation passed ({len(new_working_mds)} new docs)"

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
        # 硬层 1：同 module_path 冲突（[MODULE] 头字段精确硬碰撞）——现有
        conflicts = lookup.check_ssot_conflicts(new_py_files)
        if conflicts:
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

        # 硬层 2：能力重复检测（basename 撞 capability_id/alias → duplicate）
        # 治本（2b 事件驱动）：commit 时自动触发，不依赖 AI 主动调 find() 查重——
        # 检测逻辑唯一真源收拢到 capability_lookup.check_capability_duplicates（L2/L3 共用）
        # B 方案：所有信号皆阻断（去掉软层 advisory，理由见 check_capability_duplicates docstring）
        dups = lookup.check_capability_duplicates(new_py_files)
        if dups:
            dup_lines = [f"{d.rel_path}: {d.detail}" for d in dups]
            from zephyr.governance.capability_lookup import CAPABILITY_DUPLICATE_FIX_HINT
            detail = (
                "能力重复——新增文件与已有能力构成同能力多实现"
                "（违反 SSoT / 向内收 2a 扩展优先于新建）:\n  "
                + "\n  ".join(dup_lines)
                + "\n  " + CAPABILITY_DUPLICATE_FIX_HINT
                + " 或 reg.get(\"capability_id\") 反查真源文件路径"
                + "；若为合法 canonical 迁移，在 registry YAML 声明 canonical_override"
            )
            return False, detail

        return True, "ssot check passed"

    def _check_naming_uniqueness(self, files: list[str]) -> tuple[bool, str]:
        """全量命名硬阻断检查（治本·选项B：subprocess 调用 --check-new-full）。

        治本（向内收 v2 + 选项B 扩展）：命名检查逻辑真源唯一在
        ``check_naming_convention.py::check_new_files_full``，本方法仅 subprocess
        调用。覆盖三个治本闭环：
        1. 全库覆盖：N-16 扩展到 src/+scripts/（跨包合法同名豁免）
        2. 全维度检测：新增文件 N-01~N-17 风格 + 所有文件 N-16 唯一性
        3. 绕不过：GitCommitGateway 内嵌，--no-verify 绕过 pre-commit 但绕不过此

        新增 vs 修改区分：新增文件查风格，修改文件不查（历史遗留豁免），
        但 N-16 唯一性对所有文件查（防改名撞库）。

        Args:
            files: 绝对路径列表。

        Returns:
            (passed, detail) — passed=True 表示通过；passed=False 时 detail 含违规详情。
        """
        # 治本·选项B：覆盖 tests/+docs/+src/+scripts/（全库命名硬阻断）
        _NAMING_SCOPES = ("tests/", "docs/", "src/", "scripts/")
        involves_naming_dirs = any(
            os.path.relpath(f, str(self.project_root)).replace("\\", "/").startswith(
                _NAMING_SCOPES
            )
            for f in files
        )
        if not involves_naming_dirs:
            return True, "no files in naming scopes (tests/docs/src/scripts)"

        # subprocess 调用 check_naming_convention.py --check-new-full（全量命名硬阻断真源唯一）
        script = str(
            self.project_root / "scripts" / "governance" / "d3_metadata"
            / "check_naming_convention.py"
        )
        try:
            result = subprocess.run(
                [sys.executable, script, "--check-new-full", *files],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=30,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            logger.warning(
                "GitCommitGateway: 命名检查 subprocess 失败 (fail-open): %s", e
            )
            return True, f"naming check skipped (subprocess failed: {e})"

        if result.returncode == 0:
            return True, "naming check passed"
        if result.returncode == 1:
            # exit 1 = 命名违规（EXIT_FINDINGS），stdout 含详情
            detail = result.stdout.strip() or result.stderr.strip() or "naming violations found"
            return False, detail
        # exit 2 = usage error / 脚本不存在（测试环境 tmp_path 无脚本）→ fail-open
        logger.warning(
            "GitCommitGateway: 命名检查 subprocess 异常 exit=%s: %s",
            result.returncode, result.stderr.strip(),
        )
        return True, f"naming check skipped (subprocess exit {result.returncode})"

    def _load_protected_scripts(self) -> dict[str, list[str]]:
        """从 capability_canonical_file_registry.yaml 加载受保护脚本→锚点清单映射。

        真源唯一：扫描所有 capability 条目，取有 integrity_anchors +
        canonical_override 的，构建 rel_path → [anchor_names] 映射。
        fail-open：YAML 不可达时回退硬编码并 log warning（红蓝发现6：不静默）。
        与 _load_n16_exempt_names 一致的 fail-open 策略。
        """
        yaml_path = REGISTRY_YAML  # 真源唯一：capability_lookup.REGISTRY_YAML
        try:
            import yaml
            data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
            result: dict[str, list[str]] = {}
            for cap in data.get("capabilities", []) or []:
                override = cap.get("canonical_override", "")
                anchors = cap.get("integrity_anchors", [])
                if override and isinstance(anchors, list) and anchors:
                    cleaned = [
                        str(a).strip() for a in anchors
                        if isinstance(a, str) and str(a).strip()
                    ]
                    if cleaned:
                        result[override] = cleaned
            if result:
                return result
        except Exception as e:
            # 红蓝发现6 治本：不静默吞掉异常。fail-open 策略保留（回退硬编码，
            # 避免 registry 损坏导致全项目 commit 瘫痪），但异常要可见——
            # YAML 解析失败可能是篡改信号，应 log 供追责。
            logger.warning(
                "_load_protected_scripts: YAML 加载失败，回退硬编码: %s", e
            )
        # fail-open 回退硬编码（当前唯一受保护脚本：GATE-ID-UNIQ 检测脚本）
        # 同步提醒：新增受保护脚本时更新 YAML integrity_anchors + 此处回退值
        return {
            "scripts/governance/d5_architecture/checkers/check_precommit_id_uniqueness.py": [
                "_HOOK_ID_RE",
                "_scan_hook_ids",
                "_classify_duplicates",
                "main",
            ],
        }

    def _check_protected_script_integrity(self, files: list[str]) -> tuple[bool, str]:
        """受保护脚本完整性校验（A 层纵深防御）：AST 锚点校验。

        治脚本自篡改缺口：如果 AI 直接改检测脚本
        (check_precommit_id_uniqueness.py)，把检测逻辑删掉——pre-commit hook 和
        reconciler 共用同一脚本，两层防线会同时失效。本方法在 commit 前用 AST 校验
        受保护脚本的关键结构锚点（函数/常量）是否仍在，--no-verify 绕不过
        （gateway 内嵌校验，在 git commit 之前执行，对标 _check_ssot_canonical 模式）。

        锚点清单真源：capability_canonical_file_registry.yaml 的 integrity_anchors
        字段（_load_protected_scripts 读取）。fail-open：YAML 不可达时回退硬编码并
        log warning（红蓝发现6：不静默，异常可能是篡改信号）。

        自指悖论（残留缺口，诚实记录）：gateway 本身能被改，但改 gateway 触发
        gate-triple-align/gate-reg-bl 等门禁，且 [SAFETY] M 受保护。C 层
        (validate_rules_integrity golden hash) 是第三道独立兜底，覆盖脚本全内容。

        Args:
            files: 绝对路径列表。

        Returns:
            (passed, detail) — passed=True 表示通过；passed=False 时 detail 含违规详情。
        """
        protected_map = self._load_protected_scripts()

        # 筛选本次 commit 涉及的受保护脚本
        to_check: dict[str, list[str]] = {}
        for f in files:
            rel = os.path.relpath(f, str(self.project_root)).replace("\\", "/")
            if rel in protected_map:
                to_check[rel] = protected_map[rel]

        if not to_check:
            return True, "no protected scripts in commit"

        import ast

        def _has_substantial_body(func_node: ast.AST) -> bool:
            """函数体是否含实质性语句（防空桩 def f(): pass / return []）。

            红蓝对抗发现2治本：A 层原只校验模块级 name 存在，攻击者可保留 name 但
            清空函数体（def _scan(): pass）绕过。本函数断言函数体含控制流/调用/
            赋值/非空返回，空桩必被检出。真实检测函数（_scan_hook_ids 含 For，
            _classify_duplicates 含 If，main 含 Assign+Call）均通过。
            """
            for stmt in func_node.body:
                if isinstance(stmt, (ast.For, ast.While, ast.If, ast.With,
                                     ast.Try, ast.AsyncFor, ast.AsyncWith)):
                    return True
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                    return True  # 函数调用语句
                if isinstance(stmt, ast.Assign):
                    return True  # 赋值语句
                if isinstance(stmt, ast.Return) and stmt.value is not None:
                    v = stmt.value
                    if isinstance(v, ast.Constant) and v.value is None:
                        continue  # return None 不算实质性
                    if isinstance(v, (ast.List, ast.Tuple, ast.Set)):
                        if len(getattr(v, "elts", [])) == 0:
                            continue  # return [] / () / set() 不算实质性
                        return True
                    if isinstance(v, ast.Dict) and len(getattr(v, "keys", [])) == 0:
                        continue  # return {} 不算实质性
                    return True  # return result / return func() 算实质性
            return False

        def _assign_has_substantial_value(assign_node: ast.AST) -> bool:
            """赋值是否含实质值（防空桩 _X = None / _X = ''）。

            红蓝对抗发现2治本：_HOOK_ID_RE = None 保留 name 但正则被删空。
            真实 _HOOK_ID_RE = re.compile(...) 的 value 是 Call，非 None，通过。
            """
            v = assign_node.value
            if isinstance(v, ast.Constant) and v.value is None:
                return False  # = None
            if isinstance(v, ast.Constant) and v.value == "":
                return False  # = ""
            return True

        violations: list[str] = []
        for rel, anchors in to_check.items():
            script_path = self.project_root / rel
            if not script_path.exists():
                # 受保护脚本被删除 = 检测能力失效（pre-commit + reconciler 同时失效）
                violations.append(
                    f"{rel}: 受保护脚本被删除——pre-commit + reconciler 两层防线"
                    f"将同时失效。修复：恢复脚本，或先迁移门禁到新脚本再删除。"
                )
                continue
            try:
                source = script_path.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=rel)
            except (OSError, SyntaxError) as e:
                violations.append(
                    f"{rel}: 解析失败 ({e})——无法校验完整性锚点，禁止提交"
                )
                continue

            # 收集模块级 + 类内定义的 name → AST 节点对象（FunctionDef/ClassDef/Assign/AnnAssign）
            # 红蓝对抗发现2治本：不只校验 name 存在，还校验节点实质性（防空桩绕过）。
            # 方法锚点支持：integrity_anchors 现在保护类内方法（如
            # GitCommitGateway._check_capability_aliases），原仅收集 tree.body
            # 模块级 name，类内方法检测不到。扩展递归收集 ClassDef.body。
            defined_nodes: dict[str, ast.AST] = {}

            def _collect_nodes(nodes: list) -> None:
                for node in nodes:
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        defined_nodes[node.name] = node
                    elif isinstance(node, ast.ClassDef):
                        defined_nodes[node.name] = node
                        _collect_nodes(node.body)  # 递归收集类内方法/常量
                    elif isinstance(node, ast.Assign):
                        for tgt in node.targets:
                            if isinstance(tgt, ast.Name):
                                defined_nodes[tgt.id] = node
                    elif isinstance(node, ast.AnnAssign):
                        if isinstance(node.target, ast.Name):
                            defined_nodes[node.target.id] = node

            _collect_nodes(tree.body)

            missing = [a for a in anchors if a not in defined_nodes]
            if missing:
                violations.append(
                    f"{rel}: 缺失完整性锚点 {missing}——"
                    f"检测脚本关键结构被删除/重命名，pre-commit + reconciler 两层防线"
                    f"将同时失效。修复：恢复被删锚点，或同步更新 YAML integrity_anchors"
                    f"（需人工裁定锚点变更合理性）。"
                )
                continue  # 锚点都缺了，不必再查实质性

            # 红蓝对抗发现2治本：校验锚点节点实质性（防空桩保留 name 清空实现）。
            stub_violations: list[str] = []
            for a in anchors:
                node = defined_nodes[a]
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not _has_substantial_body(node):
                        stub_violations.append(
                            f"{a}: 函数体无实质性语句（空桩 def {a}(): pass / "
                            f"return [] 绕过）——检测逻辑被清空但锚点 name 保留"
                        )
                elif isinstance(node, ast.Assign):
                    if not _assign_has_substantial_value(node):
                        stub_violations.append(
                            f"{a}: 赋值为空值（= None / = ''）——检测常量被清空"
                        )
            if stub_violations:
                violations.append(
                    f"{rel}: 锚点空桩绕过检测——{stub_violations}"
                )

        if violations:
            return False, "\n  ".join(violations)
        return True, (
            f"protected script integrity check passed ({len(to_check)} scripts)"
        )

    def _check_capability_aliases(self, files: list[str]) -> tuple[bool, str]:
        """中文 aliases 门禁（红蓝对抗修复2）：检测 capability_canonical_file_registry.yaml
        的 aliases 字段是否含 CJK 字符。

        治本：禁堆中文同义词 alias 裁定（YAML 头部 alias 策略 + AGENTS.md）原本纯靠
        文档约定，无代码强制——新 AI 可直接在 YAML 加中文 aliases，pre-commit/
        GitCommitGateway 都不检测。本方法在 gateway 层内嵌 CJK 检测，--no-verify 绕不过。

        仅当本次提交包含 registry YAML 时才检测（避免无关 commit 开销）。fail-open：
        YAML 不可达/解析失败时跳过（不阻断 commit），与 _check_protected_script_integrity
        的 fail-open 策略一致——避免 registry 文件损坏导致全项目 commit 瘫痪。
        """
        if not any(
            f.replace("\\", "/").endswith("capability_canonical_file_registry.yaml")
            for f in files
        ):
            return True, "capability aliases check skipped (registry not in commit)"
        registry_path = REGISTRY_YAML  # 真源唯一：capability_lookup.REGISTRY_YAML
        if not registry_path.exists():
            return True, "capability aliases check skipped (registry not found)"
        try:
            import yaml

            data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        except Exception as e:
            return True, f"capability aliases check skipped (YAML parse error: {e})"
        if not isinstance(data, dict):
            return True, "capability aliases check skipped (YAML not a dict)"
        # CJK 检测正则：统一汉字 + 扩展A + 兼容汉字
        cjk_re = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]")
        violations: list[str] = []
        for cap in data.get("capabilities", []) or []:
            if not isinstance(cap, dict):
                continue
            cap_id = cap.get("capability_id", "<unknown>")
            for alias in cap.get("aliases", []) or []:
                if not isinstance(alias, str):
                    continue
                if cjk_re.search(alias):
                    violations.append(
                        f"capability '{cap_id}' alias '{alias}' 含 CJK 字符——"
                        f"禁堆中文同义词 alias（见 YAML 头部 alias 策略）"
                    )
        if violations:
            return False, "\n  ".join(violations)
        return True, "capability aliases check passed (no CJK aliases)"

    # ------------------------------------------------------------------
    # 废弃目录门禁（09_audit 治本加固，红蓝对抗修复）
    # ------------------------------------------------------------------
    # 废弃目录清单：key=相对路径前缀，value=废弃原因+迁移目标
    # 与 validate_directory_structure.py 的 ALLOWED_DOCS_DIRS 白名单互补——
    # 白名单是"允许的"（warn-only 脚本），DEPRECATED_DIRS 是"显式禁止的"（gateway 硬阻断）
    _DEPRECATED_DIRS: dict[str, str] = {
        "docs/09_audit": "已合并入 docs/_working/audit/（trae_047 gov_eng_002_directory_mapping）",
    }

    def _check_deprecated_directories(self, files: list[str]) -> tuple[bool, str]:
        """废弃目录门禁：检测提交文件是否位于已废弃的目录路径下。

        治本：09_audit/ 已合并入 docs/_working/audit/，但此前无代码强制——新 AI 可
        通过 GitCommitGateway 在 docs/09_audit/ 下创建文件，--no-verify 绕过 pre-commit。
        本方法在 gateway 层内嵌废弃目录检测，--no-verify 绕不过。

        对标 _check_capability_aliases 模式（L1319）：gateway 内嵌，--no-verify 绕不过。
        """
        violations: list[str] = []
        for f in files:
            rel = os.path.relpath(f, str(self.project_root)).replace("\\", "/")
            for deprecated, reason in self._DEPRECATED_DIRS.items():
                if rel == deprecated or rel.startswith(deprecated + "/"):
                    violations.append(
                        f"{rel} → 废弃目录 {deprecated}/（{reason}）"
                    )
        if violations:
            return False, "\n  ".join(violations)
        return True, "deprecated directories check passed"

    # ------------------------------------------------------------------
    # REPO_ROOT 真源归一检测（移植自 _tmp_fix_parents.py，仅检测不修复）
    # ------------------------------------------------------------------
    _REPO_SYSPATH_LINE = re.compile(r"sys\.path\.(?:insert|append)\s*\(")
    _REPO_ASSIGN_VAR = re.compile(r"^(\s*)([A-Za-z_][A-Za-z0-9_]*)\s*[:=]")

    @staticmethod
    def _is_bootstrap_var(text: str, var_name: str) -> bool:
        """检测变量 VAR 是否被用于 sys.path.insert/append（bootstrap 合法豁免）。"""
        pat = re.compile(
            r"sys\.path\.(?:insert|append)\s*\([^)]*?\bstr\s*\(\s*"
            + re.escape(var_name)
            + r"\b"
        )
        return bool(pat.search(text))

    @classmethod
    def _match_is_bootstrap(cls, text: str, m: "re.Match[str]") -> bool:
        """判断 parents[N] 匹配是否在 sys.path bootstrap 上下文（合法豁免）。

        规则：
          (a) 匹配所在行含 sys.path.insert/append → True（bootstrap）
          (b) 匹配前缀是赋值 VAR = ...，且 VAR 用于 sys.path → True（bootstrap）
          其他 → False（路径常量，违规）
        """
        start = text.rfind("\n", 0, m.start()) + 1
        end = text.find("\n", m.start())
        if end == -1:
            end = len(text)
        line = text[start:end]
        if cls._REPO_SYSPATH_LINE.search(line):
            return True
        prefix = text[start:m.start()]
        am = cls._REPO_ASSIGN_VAR.match(prefix)
        if am:
            var_name = am.group(2)
            if var_name and cls._is_bootstrap_var(text, var_name):
                return True
        return False

    def _check_repo_root_usage(self, files: list[str]) -> tuple[bool, str]:
        """检测 .py 文件是否使用 parents[N] 反模式（应改用 REPO_ROOT）。

        移植自 ``_tmp_fix_parents.py`` 检测逻辑（仅检测不修复）。
        合法豁免：sys.path bootstrap 上下文（鸡生蛋：需先设 sys.path 才能 import REPO_ROOT）。

        检测模式：
          - ``Path(__file__).resolve().parents[N]``  → 若 resolve 后 == REPO_ROOT 则违规
          - ``Path(__file__).resolve().parent.parent...`` (2+ parent) → 同上

        真源：``zephyr.shared.io.paths.REPO_ROOT`` 是仓库根常量唯一真源。
        约定见 AGENTS.md §7 REPO_ROOT 真源归一。

        Args:
            files: 绝对路径列表。

        Returns:
            (passed, detail) — passed=True 表示通过；passed=False 时 detail 含违规详情。
        """
        violations: list[str] = []
        for f in files:
            rel = os.path.relpath(f, str(self.project_root)).replace("\\", "/")
            if not f.endswith(".py"):
                continue
            if not (
                rel.startswith("src/")
                or rel.startswith("scripts/")
                or rel.startswith("tests/")
            ):
                continue
            # Phase 1（当前）：仅检查新增（未 git 跟踪）文件，防止新违规进入
            # Phase 2：存量违规清理完成后，删除此 if 块切换为全量检查
            # 存量违规清单见 _tmp_fix_parents.py 之前的扫描结果（156 处）
            if self._is_git_tracked(rel):
                continue
            try:
                text = Path(f).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            resolved = Path(f).resolve()

            # 模式1: Path(__file__).resolve().parents[N]
            for m in re.finditer(
                r"Path\(__file__\)\.resolve\(\)\.parents\[(\d+)\]", text
            ):
                if self._match_is_bootstrap(text, m):
                    continue  # 合法豁免：sys.path bootstrap
                n = int(m.group(1))
                if n < len(resolved.parents) and resolved.parents[n] == self.project_root:
                    line_no = text.count("\n", 0, m.start()) + 1
                    violations.append(
                        f"{rel}:{line_no} — Path(__file__).resolve().parents[{n}] "
                        f"等于 REPO_ROOT，应改用 `from zephyr.shared.io.paths import REPO_ROOT`"
                    )

            # 模式2: Path(__file__).resolve().parent.parent... (2+ parent)
            for m in re.finditer(
                r"Path\(__file__\)\.resolve\(\)(?:\.parent){2,}", text
            ):
                if self._match_is_bootstrap(text, m):
                    continue  # 合法豁免：sys.path bootstrap
                chain = m.group(0)
                parent_count = chain.count(".parent")
                result = resolved
                for _ in range(parent_count):
                    result = result.parent
                if result == self.project_root:
                    line_no = text.count("\n", 0, m.start()) + 1
                    violations.append(
                        f"{rel}:{line_no} — Path(__file__).resolve(){'.parent' * parent_count} "
                        f"等于 REPO_ROOT，应改用 `from zephyr.shared.io.paths import REPO_ROOT`"
                    )

        if violations:
            return False, "\n  ".join(violations)
        return True, "REPO_ROOT usage check passed (no parents[N] violations)"

    def _check_src_no_data(self, files: list[str]) -> tuple[bool, str]:
        """GATE-SRC-NO-DATA 等效校验：弥补 --no-verify 绕过 pre-commit 的副作用。

        真源：trae_047 §gov_eng_002_directory_mapping 禁止规则
              "src/下禁止data/子目录(数据真源唯一位置为data/目录)"

        检测：files 中是否有 src/data/ 路径前缀（大小写不敏感）。
        原因：GitCommitGateway 使用 --no-verify 提交，pre-commit 钩子 gate-src-no-data
              被跳过，故在 gateway 内部做等效校验（对标 GATE-15 等效校验模式）。

        Args:
            files: 绝对路径列表。

        Returns:
            (passed, detail) — passed=True 表示通过；passed=False 时 detail 含违规详情。
        """
        violations: list[str] = []
        for f in files:
            rel = os.path.relpath(f, str(self.project_root)).replace("\\", "/")
            if rel.lower().startswith("src/data/"):
                violations.append(rel)
        if violations:
            return (
                False,
                f"src/ 下禁止 data/ 子目录（数据真源唯一位置为 data/）: {violations}",
            )
        return True, "src/ no-data check passed"

    # ------------------------------------------------------------------
    # GOV-DOC-016 纯陈述原则校验（规则文档禁止过渡文本）
    # 真源：trae_030_doc_numbering_metadata.yaml §gov_doc_016_pure_assertion
    # ------------------------------------------------------------------
    # 过渡文本模式（fail 条件实现）：
    #   "已废止"/"旧定义"/"之前是X现在改为Y"/"已被取代"等
    # 规则文档只含当前有效规则的肯定陈述句，历史通过 git log 追踪
    _PURE_ASSERTION_PATTERNS: list[tuple["re.Pattern[str]", str]] = [
        (re.compile(r"已[废止弃]\w*"), "已废止/已废弃/已弃用"),
        (re.compile(r"旧[定规]义?[则]?"), "旧定义/旧规则"),
        (re.compile(r"之前是.{1,30}现在"), "之前是X现在改为Y"),
        (re.compile(r"已被取[代替]"), "已被取代/已被替代"),
        (re.compile(r"P[0-9]迁移后"), "P2迁移后等过渡标记"),
        (re.compile(r"从.{1,30}迁移(至|到)"), "从X迁移到Y"),
    ]

    # 规则文档范围（仅这些路径的 .md/.yaml 才检测，避免误伤任务卡/方案文档）
    # 不含 docs/01_policies_and_standards/rules/——YAML 规则定义文件包含
    # fail/prohibitions/change_history 等结构性反例展示，正则无法区分反例与真违规；
    # 其纯陈述治理由 rules_integrity_reconciler 独立负责（向内收：不在此重复实现）
    _PURE_ASSERTION_PATHS: tuple[str, ...] = (
        ".trae/rules/",  # IDE 规则文件（AI 直接消费入口）
        "AGENTS.md",  # 项目宪法（AI 直接消费入口）
    )

    def _check_pure_assertion(self, files: list[str]) -> tuple[bool, str]:
        """GOV-DOC-016 纯陈述原则校验：规则文档禁止过渡文本。

        规则文档只含当前有效规则的肯定陈述句（陈述结果/约束/命令），
        禁止"已废止"/"旧定义"/"之前是X现在改为Y"/"已被取代"等过渡文本。
        历史版本差异通过 git log 追踪。

        检测范围（AI 直接消费的规则入口）：
        - .trae/rules/*.md（IDE 规则，IDE 自动注入）
        - AGENTS.md（项目宪法，AI 首读入口）

        不检测：
        - docs/01_policies_and_standards/rules/*.yaml + *.md——YAML 规则定义文件包含
          fail/prohibitions/change_history 等结构性反例展示，正则无法区分反例与真违规，
          其纯陈述治理由 rules_integrity_reconciler 独立负责
        - 任务卡/方案文档/_working/ 过程文档（允许过渡描述）

        Args:
            files: 绝对路径列表。

        Returns:
            (passed, detail) — passed=True 表示通过；passed=False 时 detail 含违规详情。
        """
        # 筛选规则文档
        rule_files: list[str] = []
        for f in files:
            rel = os.path.relpath(f, str(self.project_root)).replace("\\", "/")
            if not (f.endswith(".md") or f.endswith(".yaml")):
                continue
            for prefix in self._PURE_ASSERTION_PATHS:
                if rel.startswith(prefix) or rel == prefix:
                    rule_files.append(f)
                    break
        if not rule_files:
            return True, "pure assertion check skipped (no rule docs in commit)"

        violations: list[str] = []
        for f in rule_files:
            rel = os.path.relpath(f, str(self.project_root)).replace("\\", "/")
            try:
                content = Path(f).read_text(encoding="utf-8")
            except Exception:
                continue  # 文件不可读跳过（fail-open，与 _check_capability_aliases 一致）
            for pattern, desc in self._PURE_ASSERTION_PATTERNS:
                matches = pattern.findall(content)
                if matches:
                    violations.append(
                        f"{rel}: 发现过渡文本 [{desc}]: {matches[:3]}"
                    )
        if violations:
            return False, "\n  ".join(violations)
        return True, "pure assertion check passed (no transition text)"

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

        统一路径：始终使用 --pathspec-from-file，避免 Windows CLI 长度限制
        (WinError 206)，消除大小双路径同步成本（历史事故：gitignored bug 修复
        只修了小路径漏了大路径）。
        """
        stashed = False
        stash_ref = ""
        pathspec_file: str | None = None
        result: CommitResult = CommitResult(
            status=CommitStatus.COMMIT_FAILED, message="unexpected: no result set"
        )
        try:
            # 1. 暂存 gitignored-tracked 文件，分离出 normal_files
            #    根因：git add 对 gitignored 路径（即使已跟踪且已删除）整批拒绝：
            #    "The following paths are ignored by one of your .gitignore files"。
            #    解法：先 _stage_gitignored_tracked 用 git rm --cached / git add -f
            #    暂存 gitignored 部分，剩余 normal_files 走正常 git add。
            #    回归测试：tests/test_git_commit_gateway.py::TestGitignoredTrackedDeleted
            gi_ok, gi_err, normal_files = self._stage_gitignored_tracked(files)
            if not gi_ok:
                result = CommitResult(
                    status=CommitStatus.COMMIT_FAILED,
                    message=gi_err,
                )
            else:
                # 2. 写 commit pathspec 文件（ALL files，含 gitignored——
                #    git commit pathspec 不检查 gitignore，可安全提交已暂存的删除/修改）
                pathspec_file = self._write_pathspec_file(files)
                # 3. git add --pathspec-from-file=<file>（只暂存 normal_files，
                #    避免整批 git add 因 gitignored 路径失败）
                add_ok = True
                if normal_files:
                    add_pathspec_file = self._write_pathspec_file(normal_files)
                    try:
                        add_result = self._run_git(
                            ["git", "add", f"--pathspec-from-file={add_pathspec_file}"]
                        )
                        add_ok = add_result.returncode == 0
                        if not add_ok:
                            logger.warning(
                                "GitCommitGateway: git add (pathspec-file) 失败: %s",
                                add_result.stderr.strip(),
                            )
                            result = CommitResult(
                                status=CommitStatus.COMMIT_FAILED,
                                message=f"git add failed: {add_result.stderr.strip()}",
                            )
                    finally:
                        try:
                            os.remove(add_pathspec_file)
                        except OSError:
                            pass
                # normal_files 为空（全部 gitignored）→ 跳过 git add
                # （gitignored 已由 _stage_gitignored_tracked 暂存）
                if add_ok:
                    # 4. session 隔离 stash 非目标 unstaged 变更
                    #    _stash_other_files 内部按 session held 过滤候选：
                    #    - feature 禁用/未注册 → 回退 stash 全部非目标
                    #      （等效原 --keep-index 语义：目标已 staged，非目标被 stash）
                    #    - session 隔离生效 → 只 stash 当前 session held 的非目标
                    #    - 候选为空 → 跳过 stash（其他 session WIP 留工作区）
                    #    目标文件已通过 git add --pathspec-from-file 全量 staged，
                    #    故 stash 非目标（显式 pathspec）不影响 staged 目标。
                    stashed, stash_ref = self._stash_other_files(session_id, files)

                    # 5. 检查 staged 变更（全量检查，保守策略：不误判 NOTHING_TO_COMMIT）
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
                        # 6. commit（rename/gitignored 检测内置到 _commit_with_file_message）
                        #
                        # 治本（gitignored staged delete 修复）：当目标含 gitignored 文件
                        # 时，必须用无 pathspec commit。根因：``git commit -- <pathspec>``
                        # 提交**工作区状态**而非**暂存区状态**——对 gitignored 文件，
                        # 工作区状态无法被 stage（gitignore 阻止），staged delete 被静默
                        # 跳过。无 pathspec 模式提交所有 staged 变更，staged delete 正确
                        # 包含。_verify_staged_is_clean 确保只提交目标文件。
                        has_gitignored = self._should_use_no_pathspec(files, normal_files)
                        pathspec_for_commit = None if has_gitignored else pathspec_file
                        commit_hash, commit_err = self._commit_with_file_message(
                            full_message, pathspec_for_commit, files
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
                                "files=%d",
                                commit_hash, gw_marker, len(files),
                            )
                            result = CommitResult(
                                status=CommitStatus.OK,
                                message=f"committed {len(files)} files",
                                commit_hash=commit_hash,
                            )
        finally:
            # 7. 恢复 stash（无论 commit 成功失败都要恢复，不丢数据）
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
            # Post-commit reconciler 调度已移至 commit() 锁释放后（见 commit() 方法末尾）
            # 治本：reconciler 在锁内无法获取锁 auto-commit（死锁），移到锁外经 _commit_auto 统一入口
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

    def _stash_other_files(self, session_id: str, target_files: list[str]) -> tuple[bool, str]:
        """选择性 stash 非本次 files 的已修改文件（session 隔离版）。

        策略:
        1. _collect_non_target_rel 收集非目标已跟踪变更（相对路径，跳过 ??）
        2. _get_session_held_non_target 筛出 session 隔离候选：
           - feature 禁用/未注册/held 空 → 回退原逻辑（stash 全部非目标）
           - 否则只 stash 当前 session 持有的非目标文件（其他 session 的 WIP 留在工作区）
        3. 候选为空 → 跳过 stash
        4. 统一使用 --pathspec-from-file 避免 Windows CLI 长度限制 (WinError 206)

        Returns:
            (是否 stash 了文件, stash_ref)
        """
        all_non_target = self._collect_non_target_rel(target_files)
        if not all_non_target:
            return False, ""

        isolation_active, candidates = self._get_session_held_non_target(
            session_id, target_files, all_non_target
        )

        # 防御性检查（治本 Gap 2）：确保目标文件不在候选列表中。
        # 目标文件绝不应被 stash——stash 会回滚工作区修改，导致 git add 时
        # 丢失目标文件的修改（commit 空内容）。_collect_non_target_rel 已排除
        # 目标文件，此检查是纵深防御的第二道防线，防止路径解析差异等边界情况。
        # 治本（Windows 大小写不敏感）：用 normcase 归一化相对路径，防止
        # target_files 与 candidates 大小写不一致时防御检查失效。
        target_rel_set = {
            os.path.normcase(
                os.path.relpath(f, str(self.project_root)).replace("\\", "/")
            )
            for f in target_files
        }
        tainted = [c for c in candidates if os.path.normcase(c) in target_rel_set]
        if tainted:
            logger.warning(
                "GitCommitGateway: 防御性拦截——目标文件被错误纳入 stash 候选，"
                "已移除 (session=%s): %s",
                session_id, tainted,
            )
            candidates = [
                c for c in candidates if os.path.normcase(c) not in target_rel_set
            ]

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
        # 统一使用 --pathspec-from-file（避免 Windows CLI 长度限制 WinError 206，
        # 消除大小双路径同步成本）
        spec_file: str | None = None
        try:
            spec_file = self._write_pathspec_file(
                [str(self.project_root / c) for c in candidates]
            )
            stash_result = self._run_git(
                ["git", "stash", "push", "-m", stash_msg, f"--pathspec-from-file={spec_file}"]
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

        git stash pop 语义：冲突时 apply 但不 drop，数据保留在 stash 栈中。
        调用方（_commit_locked）在返回 False 时将 result.status 设为 STASH_CONFLICT，
        数据永不丢失——要么成功恢复到工作区，要么保留在 stash 栈可手动恢复。

        治本 Gap 2 审查结论：git stash pop 冲突时数据保留在 stash 是正确行为，
        不会丢数据。防御性检查已加到 _stash_other_files 防目标文件误入 stash。

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

    def _has_staged_renames(self, target_files: list[str]) -> bool:
        """检测目标文件中是否有 staged rename（R 状态）。

        pathspec 对 staged rename 拆分为 add+delete 破坏 rename，需 fallback
        到无 pathspec commit。本方法只检测目标文件的 rename，不因其他 session
        的 staged rename 误触发 fallback（否则会误阻断正常 pathspec commit）。
        """
        target_rel = {
            os.path.relpath(f, str(self.project_root)).replace("\\", "/")
            for f in target_files
        }
        result = self._run_git(["git", "diff", "--cached", "--name-status", "-M"])
        if result.returncode != 0:
            return False
        for line in result.stdout.splitlines():
            if line.startswith("R"):
                # rename 格式：R100\bold_path\tnew_path
                parts = line.split("\t")
                if len(parts) >= 3 and parts[2] in target_rel:
                    return True
        return False

    def _verify_staged_is_clean(self, target_files: list[str]) -> tuple[bool, str]:
        """验证 staged 区只有目标文件（防误提交其他 session WIP）。

        治本（方案 A+）：无 pathspec commit 前的防御性验证。staged 区是工作区
        级全局共享状态，多 session 并发时可能残留其他 session 的 staged 文件。
        本方法确保无 pathspec commit 只提交目标文件。

        对于 rename，``git diff --cached --name-only`` 只返回新路径（rename 目标），
        ``target_files`` 也应包含新路径。

        Args:
            target_files: 本次 commit 的目标文件绝对路径列表。

        Returns:
            (是否干净, 错误信息)。不干净时返回 False 及非目标文件列表。
        """
        staged_result = self._run_git(["git", "diff", "--cached", "--name-only"])
        if staged_result.returncode != 0:
            return False, f"git diff --cached failed: {staged_result.stderr.strip()}"
        staged_files = {
            os.path.normcase(f.strip())
            for f in staged_result.stdout.splitlines() if f.strip()
        }
        target_rel = {
            os.path.normcase(
                os.path.relpath(f, str(self.project_root)).replace("\\", "/")
            )
            for f in target_files
        }
        non_target = staged_files - target_rel
        if non_target:
            sample = sorted(non_target)[:5]
            return False, f"staged 区有 {len(non_target)} 个非目标文件: {sample}"
        return True, ""

    def _commit_with_file_message(
        self,
        message: str,
        pathspec_file: str | None = None,
        target_files: list[str] | None = None,
    ) -> tuple[str | None, str]:
        """统一 commit 入口（向内收：rename 检测内置，调用方无需关心）。

        自动 rename 检测（真源唯一）：``pathspec_file`` 非空且 ``target_files`` 非空时，
        检测到目标文件有 staged rename（R100）自动切换无 pathspec 模式。根因：
        ``git commit --pathspec-from-file`` 对 staged rename 拆分为独立 add+delete，
        只提交 pathspec 匹配部分，破坏 rename。无 pathspec 模式用
        ``_verify_staged_is_clean`` 验证 staged 区只有目标文件后 commit（防误提交
        其他 session WIP）。

        治本（红蓝审核 v2）：rename 检测逻辑从 ``_commit_locked``/``_commit_auto``
        调用方内迁到此方法，消除两处重复调用 ``_has_staged_renames`` 的真源分裂，
        且 ``_commit_auto``（reconciler 路径）自动获得 rename 保护。

        Args:
            message: commit message。
            pathspec_file: pathspec 文件路径。None 时强制无 pathspec 模式。
            target_files: 目标文件绝对路径列表（rename 检测 + staged 验证用）。

        Returns:
            (commit_hash, error_message)。commit_hash 为 None 表示失败。
        """
        use_pathspec = pathspec_file is not None
        # rename 检测：有 pathspec 且有 target_files 时，检测 rename 自动切换无 pathspec
        if use_pathspec and target_files and self._has_staged_renames(target_files):
            use_pathspec = False
        # 无 pathspec 模式：验证 staged 区干净（防误提交其他 session WIP）
        if not use_pathspec:
            if not target_files:
                return None, "无 pathspec commit 需要 target_files 参数"
            clean, err = self._verify_staged_is_clean(target_files)
            if not clean:
                return None, f"staged 区不干净，拒绝无 pathspec commit: {err}"
        # 写消息到临时文件（RULE-FIVE：temp-file + 原子写入；RULE-TWENTY 裁定2）
        msg_fd, msg_path = tempfile.mkstemp(
            prefix="gw_commit_msg_", suffix=".txt", dir=str(self.project_root)
        )
        try:
            with os.fdopen(msg_fd, "w", encoding="utf-8") as f:
                f.write(message)
            if use_pathspec:
                commit_cmd = [
                    "git", "commit", "--no-verify", "-F", msg_path,
                    f"--pathspec-from-file={pathspec_file}",
                ]
            else:
                commit_cmd = ["git", "commit", "--no-verify", "-F", msg_path]
            result = self._run_git(commit_cmd)
            if result.returncode != 0:
                return None, result.stderr.strip() or result.stdout.strip()
            rev_result = self._run_git(["git", "rev-parse", "HEAD"])
            if rev_result.returncode == 0:
                return rev_result.stdout.strip(), ""
            return "", ""
        finally:
            try:
                os.remove(msg_path)
            except OSError:
                pass

    def _commit_auto(
        self,
        session_id: str,
        files: list[str],
        message: str,
    ) -> CommitResult:
        """reconciler auto-commit 唯一入口（锁 + ttl 校验 + commit，不触发 reconciler）。

        治本：5 个 reconciler 的 auto-commit 统一经此入口，ttl 校验无法绕过。
        原设计 reconciler 裸调 ``_run_git(["git","commit",...])`` 绕过 commit() 全部
        保护（校验/锁/stash），是 TTL 防御的最大盲区。

        与 ``commit()`` 的区别：
        - 只跑 ttl 校验（机器生成文件不需 completes_when/promote/ssot/naming 校验）
        - 不触发 reconciler（避免递归：commit→reconciler→_commit_auto→reconciler）
        - 不做 stash 隔离（reconciler 在锁外运行，工作区只有机器生成文件）
        - message 自动追加 [GW:{session_id}:auto] 标记

        真源：本方法是 reconciler auto-commit 的唯一合法入口（AGENTS.md 注册）。
        禁止 reconciler 裸调 ``_run_git(["git","commit",...])``。

        Args:
            session_id: AI session 标识。
            files: 本次 auto-commit 的文件绝对路径列表。
            message: commit message（不含 GW 标记，自动追加 [GW:{sid}:auto]）。

        Returns:
            CommitResult。
        """
        if not files:
            return CommitResult(
                status=CommitStatus.NOTHING_TO_COMMIT, message="empty files list"
            )
        if not session_id:
            session_id = "unknown"

        abs_files = [
            os.path.abspath(f) if os.path.isabs(f) else str(self.project_root / f)
            for f in files
        ]
        # 过滤不存在且未 git 跟踪的文件（与 commit() 一致）
        existing: list[str] = []
        for f in abs_files:
            if os.path.isfile(f):
                existing.append(f)
            else:
                rel = os.path.relpath(f, str(self.project_root)).replace("\\", "/")
                if self._is_git_tracked(rel):
                    existing.append(f)
        if not existing:
            return CommitResult(
                status=CommitStatus.NOTHING_TO_COMMIT,
                message="no existing or tracked files to auto-commit",
            )

        # ttl 统一拦截点（机器生成的 .md 也要有合法 ttl）
        ttl_passed, ttl_detail = self._check_frontmatter_ttl(existing)
        if not ttl_passed:
            return CommitResult(
                status=CommitStatus.METADATA_VIOLATION,
                message=f"frontmatter ttl 校验失败（auto-commit）: {ttl_detail}",
            )

        # 废弃目录门禁（09_audit 治本加固，auto-commit 同样拦截）
        deprecated_passed, deprecated_detail = self._check_deprecated_directories(existing)
        if not deprecated_passed:
            return CommitResult(
                status=CommitStatus.NAMING_VIOLATION,
                message=f"废弃目录违规（auto-commit）: {deprecated_detail}",
            )

        # GOV-DOC-016 纯陈述原则门禁（auto-commit 同样拦截）
        pure_passed, pure_detail = self._check_pure_assertion(existing)
        if not pure_passed:
            return CommitResult(
                status=CommitStatus.PURE_ASSERTION_VIOLATION,
                message=f"GOV-DOC-016 纯陈述违规（auto-commit）: {pure_detail}",
            )

        # 追加 GW auto 标记
        gw_marker = f"[GW:{session_id}:auto]"
        full_message = f"{message}\n\n{gw_marker}"

        try:
            with _GlobalCommitLock(self.project_root):
                pathspec_file = self._write_pathspec_file(existing)
                try:
                    # git add（pathspec-from-file 避免 WinError 206）
                    add_result = self._run_git(
                        ["git", "add", f"--pathspec-from-file={pathspec_file}"]
                    )
                    if add_result.returncode != 0:
                        return CommitResult(
                            status=CommitStatus.COMMIT_FAILED,
                            message=f"git add failed (auto-commit): {add_result.stderr.strip()}",
                        )
                    # 检查 staged 变更
                    diff_result = self._run_git(["git", "diff", "--cached", "--quiet"])
                    if diff_result.returncode == 0:
                        return CommitResult(
                            status=CommitStatus.NOTHING_TO_COMMIT,
                            message="no staged changes in auto-commit files",
                        )
                    # commit（rename 检测内置到 _commit_with_file_message，真源唯一）
                    # reconciler 路径与 _commit_locked 一致，自动获得 rename 保护。
                    commit_hash, commit_err = self._commit_with_file_message(
                        full_message, pathspec_file, existing
                    )
                    if commit_hash is None:
                        return CommitResult(
                            status=CommitStatus.COMMIT_FAILED,
                            message=f"git commit failed (auto-commit): {commit_err}",
                        )
                    os.environ[_GATEWAY_ENV] = "1"
                    logger.info(
                        "GitCommitGateway: auto-commit 成功 hash=%s marker=%s files=%d",
                        commit_hash, gw_marker, len(existing),
                    )
                    return CommitResult(
                        status=CommitStatus.OK,
                        message=f"auto-committed {len(existing)} files",
                        commit_hash=commit_hash,
                    )
                finally:
                    try:
                        os.remove(pathspec_file)
                    except OSError:
                        pass
        except GatewayError as e:
            return CommitResult(status=CommitStatus.LOCK_TIMEOUT, message=str(e))

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
