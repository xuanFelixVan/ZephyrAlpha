# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §ghost-commit-gateway
# [MODULE] zephyr.governance.rule_bridge.git_commit_gateway
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__; zephyr.security.access_control.session_concurrency; zephyr.governance.rule_bridge.worktree_manager
# [CONSUMERS] zephyr.governance.persistence.task_repo.TaskRepository._auto_commit_on_completion; scripts/git_commit.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 全项目唯一合法 git commit 入口；全局跨进程串行锁（.ailocks/git_commit_global.lock，TTL=1800s）；commit 用 -F <msg_file> 避免 PowerShell 特殊字符问题（RULE-TWENTY 裁定2）；环境变量 ZEPHYR_COMMIT_GATEWAY=1 + commit message 追加 [GW:session_id] 标记；worktree 物理隔离（阶段3 治本 2026-06-30：commit 检测 session worktree——在 worktree 内直接 commit 无需 stash，不在 worktree 内提示建议使用 session worktree 隔离但仍向后兼容 commit）；门禁注册制 CommitGateRegistry（架构债务 #AD-001 治本：pre-commit gate 声明式注册，4 个 in-process gate DIRECTORY-CONTRACT/CLAIM-REQUIRED/HELD-OVERLAP/CAPABILITY-OVERLAP 替代 12 个硬编码 _check_*，新增门禁 register(GateSpec) 而非硬编码 _check_*）；held_files 冲突阻断（搭便车治本：HeldOverlapGate 在 commit 时检测目标文件是否被其他活跃 session 持有，命中返回 HELD_OVERLAP_VIOLATION 阻断，allow_overlap=True 放行并追加 [GW:<sid>:overlap] 标记）；commit 守卫 _in_commit_flow（红攻1治本：_run_git 检测裸 git commit 且此标志为 False 时拒绝）；rename fallback（_commit_with_file_message 内置 rename 检测，_has_staged_renames 检测到目标文件 R100 时自动切换无 pathspec + _verify_staged_is_clean 验证 staged 区只有目标文件）
# [MODIFY-GUARD] _GlobalCommitLock 的 TTL 与锁文件名；commit message 的 GW 标记格式；ZEPHYR_COMMIT_GATEWAY 环境变量名
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] GatewayError on lock timeout；CommitResult.status 暴露结果
# [TESTS] tests/test_git_commit_gateway.py
# [A_module] module_id=MOD-GOV-git_commit_gateway | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2026062512 治本）

阶段3 根除 stash 循环：每 AI session 分配独立 git worktree（.aidrafts/{session_id}/），
session 在自己的 worktree 内编辑/commit，互不干扰（无需 stash）。GitCommitGateway
串行化所有 commit：全局跨进程串行锁 + worktree 检测 + CommitGateRegistry 门禁。
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
import tempfile
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from zephyr.governance.audit.reconciliation_registry import (
    ReconcileResult,
    ReconciliationRegistry,
    make_manifest_reconciler,
    make_path_tree_reconciler,
    make_path_ownership_reconciler,
    make_depgraph_ops_reconciler,
    make_yaml_sync_reconciler,
    make_vocab_change_reconciler,
    make_deprecated_directory_reconciler,
    make_delete_audit_reconciler,
    make_regenerate_reconciler,
    make_rule_audit_reconciler,
    make_registry_sync_reconciler,
    make_integrity_audit_reconciler,
    make_index_generator_reconciler,
    make_runtime_cleanup_reconciler,
    make_architecture_health_reconciler,
    make_session_log_index_reconciler,
)
from zephyr.governance.rule_bridge.commit_gate_registry import CommitGateRegistry
from zephyr.governance.commit_gates.held_overlap_gate import make_held_overlap_gate
from zephyr.governance.commit_gates.claim_required_gate import make_claim_required_gate
from zephyr.governance.commit_gates.capability_overlap_gate import make_capability_overlap_gate
from zephyr.governance.commit_gates.create_guard import make_create_guard
from zephyr.governance.commit_gates.directory_contract_gate import make_directory_contract_gate
from zephyr.governance.commit_gates.ttl_gate import make_ttl_gate
from zephyr.governance.commit_gates.file_placement_ttl_gate import make_file_placement_ttl_gate
from zephyr.governance.commit_gates.dangling_reference_gate import make_dangling_reference_gate
from zephyr.governance.commit_gates.arch_reference_gate import make_arch_reference_gate
from zephyr.governance.commit_gates.r5_digit_suffix_gate import make_r5_digit_suffix_gate
from zephyr.governance.commit_gates.ssot_redefinition_gate import make_ssot_redefinition_gate
from zephyr.governance.commit_gates.vocab_hardcode_gate import make_vocab_hardcode_gate
from zephyr.governance.commit_gates.file_copy_gate import make_file_copy_gate
from zephyr.governance.commit_gates.id_uniqueness_gate import make_id_uniqueness_gate
from zephyr.governance.commit_gates.exempt_zone_frontmatter_gate import make_exempt_zone_frontmatter_gate
from zephyr.governance.commit_gates.module_id_consistency_gate import make_module_id_consistency_gate
from zephyr.governance.commit_gates.perm_trigger_gate import make_perm_trigger_gate
from zephyr.governance.commit_gates.empty_handler_gate import make_empty_handler_gate
from zephyr.governance.commit_gates.orphan_module_gate import make_orphan_module_gate
from zephyr.governance.commit_gates.doc_ref_broken_gate import make_doc_ref_broken_gate
from zephyr.governance.commit_gates.function_dup_gate import make_function_dup_gate
from zephyr.governance.commit_gates.bare_getenv_gate import make_bare_getenv_gate
from zephyr.governance.commit_gates.rule_four_way_alignment_gate import (
    make_rule_four_way_alignment_gate,
)
from zephyr.shared.infra.process_pool import is_pid_alive
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

_GATEWAY_ENV = "ZEPHYR_COMMIT_GATEWAY"
_GW_MARKER_FMT = "[GW:{session_id}]"
_GLOBAL_LOCK_FILE = "git_commit_global.lock"
_LOCK_TTL_SECONDS = 1800
_LOCK_TIMEOUT_DEFAULT = 60.0
_POLL_INTERVAL = 0.1


class CommitStatus(str, Enum):
    """commit 结果状态。"""

    OK = "OK"
    NOTHING_TO_COMMIT = "NOTHING_TO_COMMIT"
    COMMIT_FAILED = "COMMIT_FAILED"
    LOCK_TIMEOUT = "LOCK_TIMEOUT"
    PROMOTION_BLOCKED = "PROMOTION_BLOCKED"
    METADATA_VIOLATION = "METADATA_VIOLATION"
    SSOT_VIOLATION = "SSOT_VIOLATION"
    NAMING_VIOLATION = "NAMING_VIOLATION"
    SCRIPT_INTEGRITY_VIOLATION = "SCRIPT_INTEGRITY_VIOLATION"
    REPO_ROOT_VIOLATION = "REPO_ROOT_VIOLATION"
    PURE_ASSERTION_VIOLATION = "PURE_ASSERTION_VIOLATION"
    HELD_OVERLAP_VIOLATION = "HELD_OVERLAP_VIOLATION"
    CLAIM_REQUIRED_VIOLATION = "CLAIM_REQUIRED_VIOLATION"
    PURE_SHIM_VIOLATION = "PURE_SHIM_VIOLATION"
    STASH_CONFLICT = "STASH_CONFLICT"  # 阶段3 已弃用，保留向后兼容


class GatewayError(RuntimeError):
    """Gateway 层错误（锁超时等）。"""


class StashConflictWarning(RuntimeWarning):
    """阶段3 移除 stash 逻辑后保留用于向后兼容。"""


@dataclass
class CommitResult:
    """commit 结果。"""

    status: CommitStatus
    message: str = ""
    commit_hash: str = ""
    stash_ref: str = ""  # 阶段3 已弃用，保留向后兼容
    stash_kept: bool = False  # 阶段3 已弃用，保留向后兼容
    reconcile: list[ReconcileResult] = field(default_factory=list)


class _GlobalCommitLock:
    """跨进程全局串行锁（os.open O_CREAT|O_EXCL 原子创建）。

    锁文件: .ailocks/git_commit_global.lock（全项目唯一，串行化所有 commit）
    TTL: 30 分钟（防进程崩溃死锁，与 staging_area.py 一致）
    僵尸锁检测：持有进程 PID 已死亡时立即清理（零窗口期）。
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

    def __enter__(self) -> "_GlobalCommitLock":
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
                try:
                    data = json.loads(self._lock_file.read_text(encoding="utf-8"))
                    acquired_at = data.get("acquired_at", 0)
                    if not isinstance(acquired_at, (int, float)):
                        acquired_at = 0
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

    串行化所有 commit。阶段3 起 worktree 物理隔离（WorktreeManager）替代 stash
    隔离——在 session worktree 内直接 commit，无需 stash 其他 session 修改。
    """

    def __init__(
        self,
        project_root: str | Path | None = None,
        registry: "SessionRegistry | None" = None,
    ) -> None:
        self.project_root = Path(project_root or Path.cwd()).resolve()
        if not (self.project_root / ".git").exists():
            raise GatewayError(f"Not a git repository: {self.project_root}")
        if registry is not None:
            self._registry = registry
        else:
            from zephyr.security.access_control.session_concurrency import SessionRegistry
            self._registry = SessionRegistry(self.project_root)
        self._reconciliation_registry = ReconciliationRegistry()
        self._register_default_reconcilers()
        # pre-commit 门禁注册表（架构债务 #AD-001 治本：5 个 in-process gate 替代 12 个硬编码 _check_*）
        self._gate_registry = CommitGateRegistry()
        self._gate_registry.register(make_held_overlap_gate())
        self._gate_registry.register(make_claim_required_gate())
        self._gate_registry.register(make_capability_overlap_gate())
        self._gate_registry.register(make_directory_contract_gate())
        self._gate_registry.register(make_ttl_gate())  # priority=32 ttl gate
        self._gate_registry.register(make_file_placement_ttl_gate())  # priority=33 文件放置与TTL一致性（ARCH-049，落地 ttl_vocabulary §146-152 永久区准入机制）
        self._gate_registry.register(make_create_guard())  # priority=60 治本"造第二真源"（trae_060 §2）
        self._gate_registry.register(make_dangling_reference_gate())  # priority=70 治本悬空引用（AGENTS.md §X.Y）
        self._gate_registry.register(make_arch_reference_gate())  # priority=75 治本 #ARCH-NNN 悬空引用（编号铁律#6 代码强制）
        self._gate_registry.register(make_rule_four_way_alignment_gate())  # priority=76 治本规则四方对齐（ARCH-020 补建，subprocess 调 check_rule_four_way_alignment.py --ci）
        self._gate_registry.register(make_r5_digit_suffix_gate())  # priority=35 治本 R5 数字后缀目录禁止（弥补 --no-verify 绕过 pre-commit 的缺口）
        self._gate_registry.register(make_ssot_redefinition_gate())  # priority=65 治本 SSoT 符号重复定义（ARCH-033 P2，弥补 CREATE-GUARD 只管新建文件不管文件内重定义的缺口）
        self._gate_registry.register(make_vocab_hardcode_gate())  # priority=80 治本 --no-verify 绕过 GATE-VOCAB（Phase 1 AST 门禁，subprocess 调 check_vocab_hardcode.py --files --ci）
        self._gate_registry.register(make_file_copy_gate())  # priority=85 治本文件复制检测无 commit-time 强制（Phase 1 sub-task 3，subprocess 调 check_code_duplication.py --files --ast --threshold 0.7）
        # Phase 3 reconciler→gate 收敛（2026-07-03）：3 个 B 类纯校验 reconciler 升级为 pre-commit 阻断 gate
        self._gate_registry.register(make_id_uniqueness_gate())  # priority=86 治本 same-repo 重复 pre-commit hook id（原 post-commit warn reconciler）
        self._gate_registry.register(make_exempt_zone_frontmatter_gate())  # priority=87 治本豁免区 frontmatter doc_type 误放（原 post-commit warn reconciler）
        self._gate_registry.register(make_module_id_consistency_gate())  # priority=88 治本 module_id 三轨一致性 + count 派生（原 post-commit warn reconciler）
        # Phase 1 AST 门禁扩展（DM-202953，2026-07-03）：5 个新 in-process gate 治本 5 病根
        self._gate_registry.register(make_perm_trigger_gate())  # priority=82 治本永久系统时间触发模式无事件订阅（病根：永久系统触发32）
        self._gate_registry.register(make_empty_handler_gate())  # priority=84 治本空 handler 函数体仅 logger/pass/return（病根：事件订阅空壳）
        self._gate_registry.register(make_orphan_module_gate())  # priority=86 治本孤儿模块死代码无 import 引用（病根：新AI可发现性55）
        self._gate_registry.register(make_doc_ref_broken_gate())  # priority=88 治本文档引用断裂 .md 相对路径不存在（病根：文档引用断裂26）
        self._gate_registry.register(make_function_dup_gate())  # priority=90 治本重复函数同目录同名同 body hash（病根：SSoT真源唯一性211）
        self._gate_registry.register(make_bare_getenv_gate())  # priority=81 治本裸os.getenv读密钥绕过SecretProvider（§5.17.10防复发，AST检测SECRET_INDICATOR_PATTERNS）
        self._in_commit_flow = False  # commit 守卫（红攻1治本）
        self._worktree_mgr = None  # 延迟初始化（避免未启用 worktree 时的开销）

    def _get_worktree_manager(self):
        """延迟获取 WorktreeManager 单例。"""
        if self._worktree_mgr is None:
            from zephyr.governance.rule_bridge.worktree_manager import WorktreeManager
            self._worktree_mgr = WorktreeManager(self.project_root)
        return self._worktree_mgr

    def claim_files(self, session_id: str, files: list[str]) -> list[str]:
        """为 session 声明持有本次 commit 的文件。claim 失败的文件从返回列表排除。"""
        claimed: list[str] = []
        for f in files:
            if self._registry.claim_file(session_id, f):
                claimed.append(f)
            else:
                logger.warning(
                    "GitCommitGateway: claim_files conflict — file=%s held by other session, "
                    "skipped (session=%s)", f, session_id,
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

    def _register_default_reconcilers(self) -> None:
        """注册默认 post-commit reconciler（声明式框架，P2-T1~T9 + 红蓝发现1 + P3收尾）。"""
        self._reconciliation_registry.register(make_manifest_reconciler(self))
        self._reconciliation_registry.register(make_path_tree_reconciler(self))
        self._reconciliation_registry.register(make_path_ownership_reconciler(self))  # path_ownership_map.yaml 自动同步
        self._reconciliation_registry.register(make_depgraph_ops_reconciler(self))  # 裁定#209 阶段1
        self._reconciliation_registry.register(make_yaml_sync_reconciler(self))
        # Phase 3 收敛：以下 3 个纯校验 reconciler 已升级为 pre-commit gate（见上方 _gate_registry）
        # make_precommit_id_uniqueness_reconciler / make_exempt_zone_frontmatter_reconciler /
        # make_module_id_consistency_reconciler 不再 post-commit 注册（warn→阻断前移）
        self._reconciliation_registry.register(make_vocab_change_reconciler(self))
        self._reconciliation_registry.register(make_deprecated_directory_reconciler(self))
        self._reconciliation_registry.register(make_delete_audit_reconciler(self))
        self._reconciliation_registry.register(make_regenerate_reconciler(self))
        self._reconciliation_registry.register(make_rule_audit_reconciler(self))
        self._reconciliation_registry.register(make_registry_sync_reconciler(self))
        self._reconciliation_registry.register(make_integrity_audit_reconciler(self))
        self._reconciliation_registry.register(make_index_generator_reconciler(self))  # P3 生成器触发接入
        self._reconciliation_registry.register(make_runtime_cleanup_reconciler(self))  # .runtime/ TTL 自动清理
        self._reconciliation_registry.register(make_architecture_health_reconciler(self))  # 架构健康度基线记录（第0期 warn-only）
        self._reconciliation_registry.register(make_session_log_index_reconciler(self))  # session_logs/index.yaml 派生（AI-03 审计 P3）

    # ------------------------------------------------------------------
    # 公开 API
    # ------------------------------------------------------------------
    def commit(
        self,
        session_id: str,
        files: list[str],
        message: str,
        allow_promote: bool = False,
        allow_overlap: bool = False,
    ) -> CommitResult:
        """串行化 commit 入口。allow_overlap 逃生通道放行被其他 session 持有的文件，追加 [GW:<sid>:overlap] 标记。"""
        if not files:
            return CommitResult(status=CommitStatus.NOTHING_TO_COMMIT, message="empty files list")
        if not session_id:
            session_id = "unknown"

        # 归一化为绝对路径（用 abspath 而非 resolve()——保留传入大小写与 git index 一致）
        abs_files = [os.path.abspath(f) for f in files]
        # 过滤不存在且未 git 跟踪的文件（保留 deletion commit / staged delete 场景）
        existing: list[str] = []
        for f in abs_files:
            if os.path.isfile(f):
                existing.append(f)
            else:
                rel = os.path.relpath(f, str(self.project_root)).replace("\\", "/")
                if self._is_git_tracked(rel) or self._is_staged_delete(rel):
                    existing.append(f)
        if not existing:
            return CommitResult(
                status=CommitStatus.NOTHING_TO_COMMIT,
                message="no existing or tracked files to commit",
            )

        # worktree 物理隔离检测（阶段3 治本 stash 循环）
        try:
            wt_session = self._get_worktree_manager().get_current_worktree()
        except Exception:
            wt_session = None
        if wt_session is not None:
            logger.info(
                "GitCommitGateway: 在 session worktree 内 commit，物理隔离生效（session=%s, wt=%s）",
                session_id, wt_session,
            )
        else:
            logger.info(
                "GitCommitGateway: 不在 session worktree 内（session=%s）——"
                "建议使用 WorktreeManager.create_session_worktree 实现物理隔离，向后兼容直接 commit",
                session_id,
            )

        # pre-commit 门禁注册表（架构债务 #AD-001 治本：5 个 in-process gate 替代 12 个硬编码 _check_*）
        # 新增门禁 MUST 走 CommitGateRegistry 注册制（commit_gates/ 下 make_xxx_gate() + __init__ register）
        gate_results = self._gate_registry.check_all(
            self, existing, session_id=session_id, allow_overlap=allow_overlap,
            allow_promote=allow_promote,
        )
        for gr in gate_results:
            if not gr.passed:
                if gr.gate_id == "HELD-OVERLAP":
                    return CommitResult(status=CommitStatus.HELD_OVERLAP_VIOLATION, message=gr.detail)
                if gr.gate_id == "CLAIM-REQUIRED":
                    return CommitResult(status=CommitStatus.CLAIM_REQUIRED_VIOLATION, message=gr.detail)
                if gr.gate_id == "FILE-PLACEMENT-TTL" and gr.detail.startswith("PROMOTION_BLOCKED"):
                    return CommitResult(status=CommitStatus.PROMOTION_BLOCKED, message=gr.detail)
                return CommitResult(
                    status=CommitStatus.COMMIT_FAILED,
                    message=f"门禁 {gr.gate_id} 阻断: {gr.detail}",
                )

        gw_marker = _GW_MARKER_FMT.format(session_id=session_id)
        full_message = f"{message}\n\n{gw_marker}"
        if allow_overlap:
            full_message += f"\n[GW:{session_id}:overlap]"

        try:
            with _GlobalCommitLock(self.project_root):
                result = self._commit_locked(session_id, existing, full_message, gw_marker)
        except GatewayError as e:
            return CommitResult(status=CommitStatus.LOCK_TIMEOUT, message=str(e))

        # Post-commit reconciler 在锁外运行（reconciler 可通过 _commit_auto 独立获取锁 auto-commit）
        if result.status == CommitStatus.OK:
            try:
                reconcile_results = self._reconciliation_registry.reconcile_for(existing, session_id)
                result.reconcile = reconcile_results
                for rr in reconcile_results:
                    if rr.action == "auto_committed":
                        logger.info("GitCommitGateway: post-commit reconcile auto-committed (session=%s): %s", session_id, rr.detail)
                    elif rr.action == "warn":
                        logger.warning("GitCommitGateway: post-commit reconcile warning (session=%s): %s", session_id, rr.detail)
                    elif rr.action == "clean":
                        print(f"GitCommitGateway: post-commit reconcile clean (session={session_id}): {rr.detail}")
            except Exception as e:
                logger.warning("GitCommitGateway: post-commit reconcile failed: %s", e)
        return result

    def _is_git_tracked(self, rel_path: str) -> bool:
        """检查相对路径是否被 git 跟踪（:(icase) pathspec 兼容 Windows 大小写不敏感）。"""
        chk = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", f":(icase){rel_path}"],
            capture_output=True,
            cwd=str(self.project_root),
        )
        return chk.returncode == 0

    def _is_staged_delete(self, rel_path: str) -> bool:
        """检查相对路径是否为 staged delete（不在 index 但仍在 HEAD）。必需：_is_git_tracked 对 staged delete 返回 False，凡保留/排除 staged delete 场景必须用本方法补充。"""
        if self._is_git_tracked(rel_path):
            return False
        chk = subprocess.run(
            ["git", "cat-file", "-e", f"HEAD:{rel_path}"],
            capture_output=True,
            cwd=str(self.project_root),
        )
        return chk.returncode == 0

    def _should_use_no_pathspec(self, files: list[str], normal_files: list[str]) -> bool:
        """判断本次 commit 是否应用无 pathspec 模式（目标含 gitignored 文件时必须）。

        AGENTS.md §8 警告勿删调用（staged delete 保护核心，commit 32ead90e 教训）。
        """
        return len(normal_files) < len(files)

    def _filter_gitignored(self, files: list[str]) -> list[str]:
        """返回 files 中被 .gitignore 忽略的绝对路径子集（--no-index 检测已跟踪+已忽略）。

        分批检测（每批 300 路径）避免 Windows CLI 长度限制 (WinError 206)。
        """
        if not files:
            return []
        rels = [
            os.path.relpath(f, str(self.project_root)).replace("\\", "/") for f in files
        ]
        ignored_rels: set[str] = set()
        _BATCH = 300
        for i in range(0, len(rels), _BATCH):
            batch = rels[i : i + _BATCH]
            chk = self._run_git(["git", "check-ignore", "--no-index", "--"] + batch)
            if chk.returncode == 0 and chk.stdout:
                for line in chk.stdout.splitlines():
                    if line.strip():
                        ignored_rels.add(line.strip().lower())
        return [f for f, rel in zip(files, rels) if rel.lower() in ignored_rels]

    def _stage_gitignored_tracked(
        self, files: list[str]
    ) -> tuple[bool, str, list[str]]:
        """暂存 gitignored 且已跟踪的文件，返回 (ok, err, normal_files)。git add 对 gitignored 整批拒绝故分离处理：已删除+已跟踪→git rm --cached；已修改+已跟踪→git add -f；未跟踪的 gitignored→跳过。"""
        ignored = self._filter_gitignored(files)
        if not ignored:
            return True, "", list(files)
        ignored_set = {os.path.abspath(f) for f in ignored}
        normal_files = [f for f in files if os.path.abspath(f) not in ignored_set]
        deleted: list[str] = []
        existing: list[str] = []
        for f in ignored:
            (existing if os.path.isfile(f) else deleted).append(f)
        if deleted:
            del_rels = [
                os.path.relpath(f, str(self.project_root)).replace("\\", "/")
                for f in deleted
            ]
            del_tracked = [f for f, rel in zip(deleted, del_rels) if self._is_git_tracked(rel)]
            if del_tracked:
                # P8-fix: 用 --pathspec-from-file 绕过 Windows CLI 长度限制 (WinError 206)
                # 大批量 gitignored+deleted 文件（如 _backups 1036 个）直接传命令行会超长
                del_pathspec = self._write_pathspec_file(del_tracked)
                try:
                    r = self._run_git(
                        ["git", "rm", "--cached", "--ignore-unmatch",
                         f"--pathspec-from-file={del_pathspec}"]
                    )
                finally:
                    try:
                        os.remove(del_pathspec)
                    except OSError:
                        pass
                if r.returncode != 0:
                    return False, f"git rm --cached failed: {r.stderr.strip()}", normal_files
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
                # P8-fix: 用 --pathspec-from-file 绕过 Windows CLI 长度限制 (WinError 206)
                ex_pathspec = self._write_pathspec_file(ex_tracked)
                try:
                    r = self._run_git(
                        ["git", "add", "-f", f"--pathspec-from-file={ex_pathspec}"]
                    )
                finally:
                    try:
                        os.remove(ex_pathspec)
                    except OSError:
                        pass
                if r.returncode != 0:
                    return False, f"git add -f failed: {r.stderr.strip()}", normal_files
        return True, "", normal_files

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
        """持锁状态下执行 add → commit（阶段3 移除 stash 隔离，worktree 物理隔离替代）。

        统一路径：始终使用 --pathspec-from-file，避免 Windows CLI 长度限制 (WinError 206)。
        """
        pathspec_file: str | None = None
        result: CommitResult = CommitResult(
            status=CommitStatus.COMMIT_FAILED, message="unexpected: no result set"
        )
        try:
            # 1. 暂存 gitignored-tracked 文件，分离出 normal_files
            gi_ok, gi_err, normal_files = self._stage_gitignored_tracked(files)
            if not gi_ok:
                result = CommitResult(status=CommitStatus.COMMIT_FAILED, message=gi_err)
            else:
                # 2. 写 commit pathspec 文件（ALL files，含 gitignored）
                pathspec_file = self._write_pathspec_file(files)
                # 3. git add normal_files（避免整批 git add 因 gitignored 路径失败）
                #    分离 existing 和 deleted——git add 对 delete 文件失败（pathspec
                #    did not match），需用 git rm 替代（治本 ARCH-030：staged/unstaged
                #    delete 文件 git add 报错导致整个 commit 流程中断）
                add_ok = True
                if normal_files:
                    existing_files = [f for f in normal_files if os.path.isfile(f)]
                    deleted_files = [f for f in normal_files if not os.path.isfile(f)]
                    # 3a. git add existing_files（modify/new/rename 目标）
                    if existing_files:
                        add_pathspec_file = self._write_pathspec_file(existing_files)
                        try:
                            add_result = self._run_git(
                                ["git", "add", f"--pathspec-from-file={add_pathspec_file}"]
                            )
                            add_ok = add_result.returncode == 0
                            if not add_ok:
                                logger.warning("GitCommitGateway: git add 失败: %s", add_result.stderr.strip())
                                result = CommitResult(
                                    status=CommitStatus.COMMIT_FAILED,
                                    message=f"git add failed: {add_result.stderr.strip()}",
                                )
                        finally:
                            try:
                                os.remove(add_pathspec_file)
                            except OSError:
                                pass
                    # 3b. git rm deleted_files（delete 文件用 git rm 替代 git add）
                    # --ignore-unmatch 跳过已 staged delete（git rm 幂等）
                    # P8-fix: 用 --pathspec-from-file 绕过 Windows CLI 长度限制 (WinError 206)
                    if add_ok and deleted_files:
                        del_pathspec = self._write_pathspec_file(deleted_files)
                        try:
                            rm_result = self._run_git(
                                ["git", "rm", "--cached", "--ignore-unmatch",
                                 f"--pathspec-from-file={del_pathspec}"]
                            )
                        finally:
                            try:
                                os.remove(del_pathspec)
                            except OSError:
                                pass
                        add_ok = rm_result.returncode == 0
                        if not add_ok:
                            logger.warning("GitCommitGateway: git rm 失败: %s", rm_result.stderr.strip())
                            result = CommitResult(
                                status=CommitStatus.COMMIT_FAILED,
                                message=f"git rm failed: {rm_result.stderr.strip()}",
                            )
                if add_ok:
                    # 4. 判断是否需要无 pathspec commit（gitignored / staged rename）
                    has_gitignored = self._should_use_no_pathspec(files, normal_files)
                    # 5. 检查 staged 变更
                    diff_result = self._run_git(["git", "diff", "--cached", "--quiet"])
                    if diff_result.returncode == 0:
                        logger.info("GitCommitGateway: files 无 staged 变更，跳过 commit")
                        result = CommitResult(
                            status=CommitStatus.NOTHING_TO_COMMIT,
                            message="no staged changes in files_in_scope",
                        )
                    else:
                        # 6. commit（rename 检测内置到 _commit_with_file_message）
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
                                "GitCommitGateway: commit 成功 hash=%s marker=%s files=%d",
                                commit_hash, gw_marker, len(files),
                            )
                            result = CommitResult(
                                status=CommitStatus.OK,
                                message=f"committed {len(files)} files",
                                commit_hash=commit_hash,
                            )
        finally:
            # 事件驱动红蓝触发 (MOD-INF-030)：正式脚本/模块提交 → 写异步触发记录
            if result.status == CommitStatus.OK:
                try:
                    self._post_commit_red_blue_trigger(files, session_id, result.commit_hash)
                except Exception as e:
                    logger.warning("GitCommitGateway: red-blue trigger emit failed: %s", e)
            # P4-T2: session shutdown handoff（crash recovery）
            if result.status == CommitStatus.OK:
                try:
                    from zephyr.governance.ops_governance.phase_manager import session_shutdown
                    session_shutdown(session_id, summary=full_message)
                except Exception as e:
                    logger.warning("GitCommitGateway: session_shutdown handoff failed: %s", e)
            if pathspec_file:
                try:
                    os.remove(pathspec_file)
                except OSError:
                    pass
            os.environ.pop(_GATEWAY_ENV, None)
        return result

    def _post_commit_red_blue_trigger(
        self, files: list[str], session_id: str, commit_hash: str,
    ) -> None:
        """事件驱动红蓝触发 (MOD-INF-030)：正式脚本/模块提交 → 写异步触发记录。"""
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
        """检测目标文件中是否有 staged rename（R 状态），pathspec 会拆分 rename 需 fallback。"""
        target_rel = {
            os.path.relpath(f, str(self.project_root)).replace("\\", "/")
            for f in target_files
        }
        result = self._run_git(["git", "diff", "--cached", "--name-status", "-M"])
        if result.returncode != 0:
            return False
        for line in result.stdout.splitlines():
            if line.startswith("R"):
                parts = line.split("\t")
                if len(parts) >= 3 and parts[2] in target_rel:
                    return True
        return False

    def _verify_staged_is_clean(
        self, target_files: list[str]
    ) -> tuple[bool, str, list[str]]:
        """验证 staged 区只有目标文件（防误提交其他 session WIP，无 pathspec commit 前置验证）。

        返回 (is_clean, error_msg, non_target_files)。
        non_target_files 为完整的非目标文件相对路径列表（供调用方自动 unstage）。
        """
        staged_result = self._run_git(["git", "diff", "--cached", "--name-only"])
        if staged_result.returncode != 0:
            return False, f"git diff --cached failed: {staged_result.stderr.strip()}", []
        staged_files = {
            os.path.normcase(f.strip())
            for f in staged_result.stdout.splitlines() if f.strip()
        }
        target_rel = {
            os.path.normcase(os.path.relpath(f, str(self.project_root)).replace("\\", "/"))
            for f in target_files
        }
        non_target = sorted(staged_files - target_rel)
        if non_target:
            sample = non_target[:5]
            return False, f"staged 区有 {len(non_target)} 个非目标文件: {sample}", non_target
        return True, "", []

    def _unstage_non_target_files(
        self, non_target_files: list[str]
    ) -> tuple[bool, str]:
        """自动 unstage 非目标文件（治本：多 session 共享 git index 时清理并发污染）。

        git index 是工作区级单例，并发 session 可能 staged 了不属于本次 commit 的文件。
        无 pathspec 模式会提交整个 staging 区，所以 commit 前必须清理非目标文件。
        此前由调用方手动 git reset HEAD 清理（反复出现 commit 卡死），现改为 GitCommitGateway 自动处理。
        """
        if not non_target_files:
            return True, ""
        result = self._run_git(["git", "reset", "HEAD", "--"] + non_target_files)
        if result.returncode != 0:
            return False, result.stderr.strip() or result.stdout.strip()
        logger.info(
            "GitCommitGateway: 自动 unstage %d 个非目标文件（多 session staging 区污染清理）",
            len(non_target_files),
        )
        return True, ""

    def _commit_with_file_message(
        self,
        message: str,
        pathspec_file: str | None = None,
        target_files: list[str] | None = None,
    ) -> tuple[str | None, str]:
        """统一 commit 入口。pathspec_file=None 时强制无 pathspec 模式；检测到 staged rename 自动切换无 pathspec。返回 (commit_hash, error)，hash 为 None 表示失败。"""
        use_pathspec = pathspec_file is not None
        if use_pathspec and target_files and self._has_staged_renames(target_files):
            use_pathspec = False
        if not use_pathspec:
            if not target_files:
                return None, "无 pathspec commit 需要 target_files 参数"
            clean, err, non_target = self._verify_staged_is_clean(target_files)
            if not clean:
                # 治本：自动 unstage 非目标文件后重新验证，避免并发 session
                # 污染 staging 区导致 commit 卡死（此前需调用方手动 git reset HEAD）
                unstage_ok, unstage_err = self._unstage_non_target_files(non_target)
                if not unstage_ok:
                    return None, (
                        f"staged 区不干净且自动清理失败: {err} | unstage error: {unstage_err}"
                    )
                clean, err, _ = self._verify_staged_is_clean(target_files)
                if not clean:
                    return None, f"staged 区不干净，自动 unstage 后仍不干净: {err}"
        msg_fd, msg_path = tempfile.mkstemp(
            prefix="gw_commit_msg_", suffix=".txt", dir=str(self.project_root)
        )
        try:
            self._in_commit_flow = True  # 放行 _run_git 的 commit 守卫（红攻1治本）
            with os.fdopen(msg_fd, "w", encoding="utf-8") as f:
                f.write(message)
            if use_pathspec:
                commit_cmd = ["git", "commit", "--no-verify", "-F", msg_path,
                              f"--pathspec-from-file={pathspec_file}"]
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
            self._in_commit_flow = False
            try:
                os.remove(msg_path)
            except OSError:
                pass

    def _commit_auto(
        self, session_id: str, files: list[str], message: str,
    ) -> CommitResult:
        """reconciler auto-commit 唯一入口（锁 + DIRECTORY-CONTRACT gate + commit，不触发 reconciler）。阶段3 仅保留 DIRECTORY-CONTRACT gate；禁止 reconciler 裸调 git commit。"""
        if not files:
            return CommitResult(status=CommitStatus.NOTHING_TO_COMMIT, message="empty files list")
        if not session_id:
            session_id = "unknown"

        abs_files = [
            os.path.abspath(f) if os.path.isabs(f) else str(self.project_root / f)
            for f in files
        ]
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

        # DIRECTORY-CONTRACT gate 校验（真源复用：gate_registry.get，不复制 DCR 逻辑）
        dcr_spec = self._gate_registry.get("DIRECTORY-CONTRACT")
        if dcr_spec is not None:
            dcr_passed, dcr_detail = dcr_spec.check(self, existing)
            if not dcr_passed:
                return CommitResult(
                    status=CommitStatus.NAMING_VIOLATION,
                    message=f"目录契约违规（auto-commit）: {dcr_detail}",
                )
        else:
            logger.warning(
                "_commit_auto: DIRECTORY-CONTRACT gate 未注册，跳过 DCR 校验"
                "（session=%s, files=%d）——检查 __init__ 的 gate 注册",
                session_id, len(existing),
            )

        # TTL-METADATA gate (subprocess reuse, same pattern as DCR gate)
        ttl_spec = self._gate_registry.get("TTL-METADATA")
        if ttl_spec is not None:
            ttl_passed, ttl_detail = ttl_spec.check(self, existing)
            if not ttl_passed:
                return CommitResult(
                    status=CommitStatus.NAMING_VIOLATION,
                    message=f"ttl metadata violation (auto-commit): {ttl_detail}",
                )
        else:
            logger.warning(
                "_commit_auto: TTL-METADATA gate 未注册，跳过 ttl 校验"
                "（session=%s, files=%d）——检查 __init__ 的 gate 注册",
                session_id, len(existing),
            )

        # FILE-PLACEMENT-TTL gate（ARCH-049，与 TTL-METADATA 同模式覆盖 _commit_auto 路径）
        # reconciler auto-commit 传 allow_promote=True（reconciler 是受信任自动流程，exempt_subdirs 生成器输出豁免）
        fpt_spec = self._gate_registry.get("FILE-PLACEMENT-TTL")
        if fpt_spec is not None:
            fpt_passed, fpt_detail = fpt_spec.check(
                self, existing, allow_promote=True,
            )
            if not fpt_passed:
                return CommitResult(
                    status=CommitStatus.NAMING_VIOLATION,
                    message=f"file placement ttl violation (auto-commit): {fpt_detail}",
                )
        else:
            logger.warning(
                "_commit_auto: FILE-PLACEMENT-TTL gate 未注册，跳过文件放置校验"
                "（session=%s, files=%d）——检查 __init__ 的 gate 注册",
                session_id, len(existing),
            )

        gw_marker = f"[GW:{session_id}:auto]"
        full_message = f"{message}\n\n{gw_marker}"

        try:
            with _GlobalCommitLock(self.project_root):
                pathspec_file = self._write_pathspec_file(existing)
                try:
                    add_result = self._run_git(
                        ["git", "add", f"--pathspec-from-file={pathspec_file}"]
                    )
                    if add_result.returncode != 0:
                        return CommitResult(
                            status=CommitStatus.COMMIT_FAILED,
                            message=f"git add failed (auto-commit): {add_result.stderr.strip()}",
                        )
                    diff_result = self._run_git(["git", "diff", "--cached", "--quiet"])
                    if diff_result.returncode == 0:
                        return CommitResult(
                            status=CommitStatus.NOTHING_TO_COMMIT,
                            message="no staged changes in auto-commit files",
                        )
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
        """将文件路径写入临时 pathspec 文件（:(icase) 前缀兼容 Windows 大小写不敏感）。"""
        fd, path = tempfile.mkstemp(
            prefix="gw_pathspec_", suffix=".txt", dir=str(self.project_root)
        )
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            for abs_path in abs_files:
                rel = os.path.relpath(abs_path, str(self.project_root))
                rel = rel.replace("\\", "/")
                f.write(f":(icase){rel}\n")
        return path

    def _run_git(self, cmd: list[str]) -> subprocess.CompletedProcess:
        """执行 git 命令（统一 cwd + encoding）。reconciler 禁止裸调 git commit——必须走 _commit_auto()，commit 守卫 _in_commit_flow 技术强制。"""
        if (
            len(cmd) >= 2
            and cmd[0] == "git"
            and cmd[1] == "commit"
            and not getattr(self, "_in_commit_flow", False)
        ):
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=1,
                stdout="",
                stderr=(
                    "_run_git: git commit 禁止裸调——必须经 commit()/_commit_auto()/"
                    "_commit_with_file_message 统一入口（DIRECTORY-CONTRACT gate 覆盖）。"
                    "见 AGENTS.md §8 L281。"
                ),
            )
        env = os.environ.copy()
        env[_GATEWAY_ENV] = "1"
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
