# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §ghost-commit-gateway
# [MODULE] zephyr.gov_enforcement.rule_bridge.git_commit_gateway
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.__init__; zephyr.security.access_control.session_concurrency; zephyr.gov_enforcement.rule_bridge.worktree_manager; zephyr.governance.audit.pg_probe (refresh_pg_probe_state，#ARCH-119 commit 前置探针，延迟 import)
# [CONSUMERS] zephyr.governance.persistence.task_repo.TaskRepository._auto_commit_on_completion; scripts/git_commit.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 全项目唯一合法 git commit 入口；全局跨进程串行锁（.ailocks/git_commit_global.lock，TTL=1800s）；commit 用 -F <msg_file> 避免 PowerShell 特殊字符问题（RULE-TWENTY 裁定2）；环境变量 ZEPHYR_COMMIT_GATEWAY=1 + commit message 追加 [GW:session_id] 标记；worktree 物理隔离（阶段3 治本 2026-06-30：commit 检测 session worktree——在 worktree 内直接 commit 无需 stash，不在 worktree 内提示建议使用 session worktree 隔离但仍向后兼容 commit）；门禁注册制 CommitGateRegistry（架构债务 #AD-001 治本：pre-commit gate 声明式注册，4 个 in-process gate DIRECTORY-CONTRACT/CLAIM-REQUIRED/HELD-OVERLAP/CAPABILITY-OVERLAP 替代 12 个硬编码 _check_*，新增门禁 register(GateSpec) 而非硬编码 _check_*）；held_files 冲突阻断（搭便车治本：HeldOverlapGate 在 commit 时检测目标文件是否被其他活跃 session 持有，命中返回 HELD_OVERLAP_VIOLATION 阻断，allow_overlap=True 放行并追加 [GW:<sid>:overlap] 标记）；commit 守卫 _in_commit_flow（红攻1治本：_run_git 检测裸 git commit 且此标志为 False 时拒绝）；rename fallback（_commit_with_file_message 内置 rename 检测，_has_staged_renames 检测到目标文件 R100 时自动切换无 pathspec + _verify_staged_is_clean 验证 staged 区只有目标文件）；adopt_prior_work 治本（2026-07-23，ARCH-054 跨 session 续作）：claim_files(adopt_prior_work=True) 认领前序未提交变更——审计记录实际基线 diff_size+sha256 到 .runtime/claim_snapshots/{sid}_adopted.jsonl 但存储空基线让 FOREIGN-CHANGE gate 放行，替代 stash 舞蹈与 --allow-overlap 逃生通道（allow_overlap commit 时绕 gate，adopt claim 时认领附审计）；claim 基线=首次 claim 时刻快照（tracker #92 治本：幂等重跑 claim_files 保留既有基线不重捕获，防止 CLI commit 主流程重跑覆盖 adopt 空基线/首次干净基线）；worktree 内 commit 跳过搭便车三 gate（tracker #92：wt_session 非 None 时 skip=_WORKTREE_SKIP_GATES 单一真源，物理隔离下无检测对象，对齐 merge 预演口径，非 worktree 路径全量保留）
# [MODIFY-GUARD] _GlobalCommitLock 的 TTL 与锁文件名；commit message 的 GW 标记格式；ZEPHYR_COMMIT_GATEWAY 环境变量名
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] GatewayError on lock timeout；CommitResult.status 暴露结果
# [TESTS] tests/test_git_commit_gateway.py
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: while True+time.sleep是_GlobalCommitLock文件锁等待循环，非周期触发
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
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from zephyr.gov_enforcement.rule_bridge.batched_auto_committer import BatchedAutoCommitter  # ARCH-GIT-CALL-BUDGET P2.3
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import CommitGateRegistry
from zephyr.gov_enforcement.rule_bridge.gate_auto_registrar import (
    auto_register_gates,  # #ARCH-GATE-REGISTRY-AUTO-001 Phase 4——YAML 驱动自动注册替代 76 个显式 import
)
from zephyr.governance.audit.blueprint_status_transition_reconciler import (
    make_blueprint_status_transition_reconciler,  # 12维度审计自动化 P1-d BLUEPRINT状态转跃reconciler
)
from zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler import (  # ARCH-TOOL-HEALTH-V1 Phase 5b
    make_commit_gateway_abuse_monitor_reconciler,
)
from zephyr.governance.audit.cross_layer_contract_signature_reconciler import (
    make_cross_layer_contract_signature_reconciler,  # 12维度审计自动化 P1-b 跨层契约签名reconciler
)
from zephyr.governance.audit.dead_public_wrapper_reconciler import (  # #ARCH-STAGE4-PUBLIC-WRAPPER-DEAD-CODE-001 防复发——死公共 wrapper 持续自动检测
    make_dead_public_wrapper_reconciler,
)
from zephyr.governance.audit.error_pattern_consumer_reconciler import (  # #ARCH-PREVENTABILITY-LAYER-001 Phase 4 P4-1b
    make_error_pattern_consumer_reconciler,
)
from zephyr.governance.audit.git_guard_bypass_reconciler import (  # #ARCH-GIT-SELF-HARM-GUARD L2.3 alias 绕过检测（priority=810，post-commit warn-only）
    make_git_guard_bypass_reconciler,
)
from zephyr.governance.audit.git_performance_monitor_reconciler import (  # ARCH-GIT-CALL-BUDGET P3.5
    make_git_performance_monitor_reconciler,
)
from zephyr.governance.audit.reconciliation_registry import (
    ReconcileResult,
    ReconciliationRegistry,
    _downgrade_auto_committed_on_flush_failure,  # #ARCH-ASSET-INDEX-FALSE-AUTO-COMMIT-001 治本
    _log_reconcile_results,  # #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 2
    _print_block_banner,  # #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 4.2
    _print_critical_warn_banner,  # #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 3
    make_arch_diagram_reconciler,
    make_architecture_health_reconciler,
    make_blueprint_frontmatter_reconciler,  # ARCH-FRONTMATTER-STATE-001 Phase 2
    make_blueprint_id_legacy_reconciler,  # ARCH-DATAQUALITY-V1.8 Task I
    make_capability_lookup_health_reconciler,  # #ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD Phase 4 G6 监控欠缺
    make_constraint_detect_reconciler,
    make_consumers_accuracy_baseline_reconciler,  # #ARCH-CONSUMERS-ACCURACY-001/003 治本 Phase 2（CONSUMERS baseline 全扫）
    make_delete_audit_reconciler,
    make_depgraph_ops_reconciler,
    make_deprecated_directory_reconciler,
    make_drift_fix_reconciler,
    make_drift_scan_reconciler,
    make_gate_inventory_sync_reconciler,
    make_gate_registry_sync_reconciler,
    make_in_process_gate_registry_drift_reconciler,  # #ARCH-GATE-REGISTRY-AUTO-001 Phase 6——YAML ↔ 内存注册表双向漂移检测
    make_index_generator_reconciler,
    make_integrity_audit_reconciler,
    make_manifest_reconciler,
    make_module_id_recommend_reconciler,
    make_path_ownership_reconciler,
    make_path_tree_reconciler,
    make_regenerate_reconciler,
    make_registry_sync_reconciler,
    make_root_temp_sweep_reconciler,  # #ARCH-ROOT-TEMP-FILE-ENFORCEMENT-001 根目录临时文件清扫（priority=803）
    make_rule_audit_reconciler,
    make_runtime_cleanup_reconciler,
    make_scripts_import_integrity_reconciler,  # ARCH-TOOL-HEALTH-V1 Phase 3
    make_session_log_index_reconciler,
    make_session_staging_lifecycle_reconciler,  # #ARCH-ROOT-TEMP-FILE-ENFORCEMENT-001 staging TTL 清理（priority=802）
    make_stash_lifecycle_reconciler,  # #ARCH-WORKTREE-002 Phase 4 stash 过期清理
    make_tmp_cleanup_reconciler,
    make_ttl_drift_incremental_reconciler,
    make_undefined_name_baseline_reconciler,  # GATE-DEPGRAPH-OPS 治本 Phase 1（F821 baseline 全扫）
    make_vocab_change_reconciler,
    make_worktree_lifecycle_reconciler,
    make_yaml_sync_reconciler,
)
from zephyr.governance.audit.remediation_progress_reconciler import (  # #ARCH-GOV-CONVERGENCE-META Phase 3.1
    make_remediation_progress_reconciler,
)
from zephyr.governance.audit.runtime_violation_snapshot_reconciler import (  # #ARCH-GOV-CONVERGENCE-META Phase 3.4b
    make_runtime_violation_snapshot_reconciler,
)
from zephyr.governance.audit.translation_coverage_reconciler import (  # TRANSLATION-COVERAGE Layer 4——翻译覆盖率存量对账（post-commit warn-only，priority=951）
    make_translation_coverage_reconciler,
)
from zephyr.governance.audit.workspace_hygiene_reconciler import (  # ARCH-TOOL-HEALTH-V1 Phase 6 + DEBT-WORKSPACE-001/002
    make_workspace_hygiene_reconciler,
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
# S3-C: claim 快照持久化目录（FOREIGN_CHANGE gate 崩溃恢复）
_CLAIM_SNAPSHOTS_DIR = ".runtime/claim_snapshots"

# Stage 4 公共化：模块级公共别名（primary 仍为私有定义，公共别名为同对象引用）。
GATEWAY_ENV = _GATEWAY_ENV
GLOBAL_LOCK_FILE = _GLOBAL_LOCK_FILE


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
    FOREIGN_CHANGE_VIOLATION = "FOREIGN_CHANGE_VIOLATION"  #ARCH-054 外来变更检测
    CLAIM_REQUIRED_VIOLATION = "CLAIM_REQUIRED_VIOLATION"
    WORKTREE_VIOLATION = "WORKTREE_VIOLATION"  # #ARCH-WORKTREE-GATE-001
    COMMIT_SCOPE_VIOLATION = "COMMIT_SCOPE_VIOLATION"  # 跨域混合提交治本（13a5e1d512）
    PURE_SHIM_VIOLATION = "PURE_SHIM_VIOLATION"
    STASH_CONFLICT = "STASH_CONFLICT"  # 阶段3 已弃用，保留向后兼容
    MERGE_IN_PROGRESS = "MERGE_IN_PROGRESS"  # B2 治本①：MERGE_HEAD 晾置截胡防护（AI-FILL-14 事故）


class GatewayError(RuntimeError):
    """Gateway 层错误（锁超时等）。"""
    error_code = "ZA-GV-0032"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


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
                    ) from None
                # PERM-TRIGGER fix: use Event().wait() instead of time.sleep()
                threading.Event().wait(self._poll_interval)

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self._acquired:
            try:
                os.remove(self._lock_file)
            except OSError:
                pass
            self._acquired = False
        return False


# Stage 4 公共化：公共别名（primary 仍为 _GlobalCommitLock，公共别名为同对象引用）。
GlobalCommitLock = _GlobalCommitLock


def _audit_commit_lock_fallback(project_root: Path, session_id: str, error_detail: str) -> None:
    """TRAE-079 铁律6：文件锁 fail-open 降级落审计。

    当 _GlobalCommitLock 因 OSError（磁盘满/权限/只读文件系统）不可用时，
    降级为无锁 commit 并记录到此审计文件。滥用监控依赖此真源。
    """
    try:
        audit_dir = project_root / ".runtime" / "gate_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": int(time.time()),
            "session_id": session_id,
            "error": error_detail,
        }
        with (audit_dir / "commit_lock_fallback.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001 — 审计写入失败不阻断 commit
        logger.debug("commit_lock_fallback audit write failed (non-blocking)", exc_info=True)


# B2 治本②（2026-08-19）：intent-to-add  index 标志位（GIT_INDEX_FLAG_INTENT_TO_ADD）
_ITA_FLAG = 0x20000000
# ita 条目的 ls-files --stage 签名=空 blob（内容未入对象库）
_EMPTY_BLOB_SHA = "e69de29b2d1d6434b8b29ae775ad8c2e48c5391"


def _audit_index_hygiene(project_root: Path, session_id: str, kind: str, payload: dict) -> None:
    """B2 治本②③：index 卫生事件审计（ita 清扫 / post-commit 一致性异常），滥用监控真源。"""
    try:
        audit_dir = project_root / ".runtime" / "gate_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": int(time.time()),
            "session_id": session_id,
            "kind": kind,
            **payload,
        }
        with (audit_dir / "gateway_index_hygiene.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001 — 审计写入失败不阻断 commit
        logger.debug("index_hygiene audit write failed (non-blocking)", exc_info=True)


# P2-2b 治本（#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）：
# git 命令 timeout 分级——原硬编码 120s 对所有 git 命令共用，导致快速读命令
# （rev-parse/show/status）与慢速写命令（commit/merge）共用上限。改为按命令类型
# 分级，单个慢命令不会耗尽整个 session 预算。
_GIT_TIMEOUT_READ = 15    # rev-parse/show/status/diff/log/ls-tree/merge-base/config
_GIT_TIMEOUT_WRITE = 60   # commit/merge/checkout/reset/update-ref/rebase
_GIT_TIMEOUT_DEFAULT = 30  # 其他默认

# Stage 4 公共化：timeout 常量公共别名。
GIT_TIMEOUT_READ = _GIT_TIMEOUT_READ
GIT_TIMEOUT_WRITE = _GIT_TIMEOUT_WRITE
GIT_TIMEOUT_DEFAULT = _GIT_TIMEOUT_DEFAULT

_GIT_READ_SUBCMDS: frozenset[str] = frozenset({
    "rev-parse", "show", "status", "diff", "log", "ls-tree", "ls-files",
    "merge-base", "config", "cat-file", "rev-list", "name-rev", "describe",
    "remote", "stash", "show-ref", "symbolic-ref", "for-each-ref",
})

_GIT_WRITE_SUBCMDS: frozenset[str] = frozenset({
    "commit", "merge", "checkout", "reset", "update-ref", "rebase",
    "cherry-pick", "revert", "apply", "am", "init", "clone", "fetch",
    "push", "pull", "tag", "add", "rm", "mv", "worktree",
})


def _classify_git_timeout(cmd: list[str]) -> int:
    """按 git 子命令类型返回 timeout 秒数（P2-2b 治本）。

    Args:
        cmd: git 命令列表（如 ``["git", "show", "HEAD"]``）。

    Returns:
        timeout 秒数：read 类 15s / write 类 60s / 其他默认 30s。
        非 git 命令或空列表返回默认 30s。
    """
    if len(cmd) < 2 or cmd[0] != "git":
        return _GIT_TIMEOUT_DEFAULT
    subcmd = cmd[1]
    if subcmd in _GIT_READ_SUBCMDS:
        return _GIT_TIMEOUT_READ
    if subcmd in _GIT_WRITE_SUBCMDS:
        return _GIT_TIMEOUT_WRITE
    return _GIT_TIMEOUT_DEFAULT


# Stage 4 公共化：公共别名。
classify_git_timeout = _classify_git_timeout


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
        # 治本(2026-07-20): .git 检查仅在 registry is None 时执行——
        # 传入 registry（测试模式）时跳过 fail-fast 检查，允许在非 git 仓库路径下实例化。
        # 理由：test_ssot_gate.py 传入 tests/governance/（非 git 仓库）+ MagicMock registry
        # 实例化 gateway 测试 _check_ssot_canonical；test_init_non_git_repo_raises 不传
        # registry 期望 raise。两条路径通过 registry 是否为 None 区分。
        # 实际 git 操作时如果 .git 不存在，git 命令会自然失败（fail-fast 仍生效）。
        if registry is None and not (self.project_root / ".git").exists():
            raise GatewayError(f"Not a git repository: {self.project_root}")
        if registry is not None:
            self._registry = registry
        else:
            from zephyr.security.access_control.session_concurrency import SessionRegistry
            self._registry = SessionRegistry(self.project_root)
        self._reconciliation_registry = ReconciliationRegistry()
        # ARCH-GIT-CALL-BUDGET P2.3 (2026-07-19): reconciler auto-commit batcher.
        self._batcher = BatchedAutoCommitter(self)
        self._register_default_reconcilers()
        # pre-commit 门禁注册表（架构债务 #AD-001 治本：5 个 in-process gate 替代 12 个硬编码 _check_*）
        self._gate_registry = CommitGateRegistry()
        # Phase 4 迁移（#ARCH-GATE-REGISTRY-AUTO-001）：82 个显式 register 替换为 auto_register_gates 调用
        auto_register_gates(self._gate_registry, self.project_root)
        self.in_commit_flow = False  # commit 守卫（红攻1治本）
        self._worktree_mgr = None  # 延迟初始化（避免未启用 worktree 时的开销）
        #ARCH-054: claim 时捕获文件基线快照（git diff HEAD -- <file>），
        # commit 时 FOREIGN-CHANGE-DETECTION gate 对比检测搭便车变更。
        # S3-C 治本（2026-07-17）：快照持久化到 .runtime/claim_snapshots/，
        # 进程崩溃后重启可恢复快照（原纯内存 dict 崩溃即丢失，gate 降级为 PASS）。
        self._claim_snapshots: dict[str, dict[str, str]] = {}
        self._claim_snapshots_dir: Path = self.project_root / _CLAIM_SNAPSHOTS_DIR
        self.load_claim_snapshots_from_disk()

    def commit_with_file_message(self, message, pathspec_file, target_files) -> tuple[str | None, str]:
        """公共接口：commit_with_file_message（Stage 4 公共化）。"""
        return self._commit_with_file_message(message, pathspec_file, target_files)


    # ── Stage 4 公共化（2026-07-29）：public wrapper ──
    def run_post_commit_reconcile_async(self, existing: list[str], session_id: str, commit_sha: str, commit_message: str='') -> None:
        '异步 spawn detached worker subprocess（P2-3 治本）。\n\n        - commit_sha 缺失 → 回退 sync（兼容 edge case）\n        - launch 失败 → 回退 sync（fail-open，reconciler 仍需执行）\n        - launch 成功 → 立即返回，worker 在后台执行\n\n        Args:\n            existing: 已 commit 的文件绝对路径列表。\n            session_id: commit session_id。\n            commit_sha: 本次 commit 的 SHA（worker 用作 status file key）。\n            commit_message: commit message（审计追溯用）。\n        '
        if not commit_sha:
            logger.warning('GitCommitGateway: async reconcile fallback to sync (no commit_sha, session=%s)', session_id)
            self._run_post_commit_reconcile_sync(existing, session_id, commit_message, result=None)
            return
        try:
            from zephyr.governance.audit.reconcile_runner import launch_reconcile_async
            launch_result = launch_reconcile_async(self.project_root, commit_sha, session_id, existing, commit_message)
            if launch_result['ok']:
                logger.info('GitCommitGateway: post-commit reconcile async launched (session=%s, sha=%s, pid=%s)', session_id, commit_sha, launch_result.get('worker_pid', 0))
            else:
                logger.warning('GitCommitGateway: async launch failed, fallback to sync: %s', launch_result.get('error', ''))
                self._run_post_commit_reconcile_sync(existing, session_id, commit_message, result=None)
        except Exception as e:
            logger.warning('GitCommitGateway: async reconcile launch failed, fallback to sync: %s', e, exc_info=True)
            self._run_post_commit_reconcile_sync(existing, session_id, commit_message, result=None)


    # ── Stage 4 公共化（2026-07-29）：public wrapper ──
    def run_post_commit_reconcile(self, existing: list[str], session_id: str, result: CommitResult, commit_message: str='') -> None:
        'Post-commit reconciler 调度器（Ruling:100PCT-AI-GOVERNANCE P2-3 异步化）。\n\n        #ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD Phase 3.4 断点4/5 治本：\n        新增 commit_message 参数——传递给 reconcile_for 和 _log_reconcile_results，\n        使 post-commit 审计链可追溯 [no-lookup:reason] / ZEPHYR_BYPASS_LOOKUP 逃生通道使用。\n        原断点4: commit() 不传 message 给 _run_post_commit_reconcile；\n        原断点5: _run_post_commit_reconcile 不传 commit_message 给 reconcile_for。\n\n        P2-3 治本（2026-07-19）：默认异步 spawn detached worker subprocess，避免 30+ 个\n        reconciler 同步执行超时被 AI 工具强制终止（误判为 commit 失败）。env\n        ``ZEPHYR_RECONCILE_SYNC=1`` 强制同步模式（测试用）。\n        '
        if result.status is not CommitStatus.OK:
            return
        # #ARCH-REGEN-CASCADE-001 治本（2026-08-05 CPU 爆炸事故）：
        # worker 内 auto-commit 不重跑 reconciler 链。病根：ZEPHYR_RECONCILE_SYNC=1
        # 让 worker 内 auto-commit 走 sync 路径，同步递归重跑 32 reconciler，每个
        # apply_depgraph-calling reconciler fire reconcile_async → N× 编排器并发
        # → blueprint_panorama 互相争用全部 300s 超时 → CPU 99% 正反馈放大。
        # worker 主循环 _run_post_commit_reconcile_sync_worker 已覆盖全部 reconciler，
        # auto-commit 仅持久化；后续 reconciler 顺序读最新 DB/文件即可，无需重跑链路。
        if os.environ.get('ZEPHYR_RECONCILE_WORKER', '') == '1':
            return
        _governance_dir = self.project_root / 'scripts' / 'governance' / 'd1_structure'
        if not _governance_dir.is_dir():
            return
        if os.environ.get('ZEPHYR_RECONCILE_SYNC', '') == '1':
            self._run_post_commit_reconcile_sync(existing, session_id, commit_message, result=result)
        elif os.environ.get('PYTEST_CURRENT_TEST'):
            # B1/R1 治本（2026-08-19）：pytest 测试体内 commit 不 spawn 真实 reconcile
            # worker——worker 以 tmp 仓为 root 跑主仓维护链路，实测挂起残留 2h+（8 僵尸
            # 进程实证），async 回写更是 xdist 尾部资源风暴放大器（61 watchdog daemon
            # 同族问题）。需覆盖 reconcile 调度的测试走 ZEPHYR_RECONCILE_SYNC=1 同步路径。
            logger.debug('GitCommitGateway: pytest env, skip async reconcile worker spawn')
            return
        else:
            self._run_post_commit_reconcile_async(existing, session_id, result.commit_hash, commit_message)


    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def reconciliation_registry(self):
        """只读：reconciliation_registry（Stage 4 公共化）。"""
        return self._reconciliation_registry

    @reconciliation_registry.setter
    def reconciliation_registry(self, value):
        """写入：reconciliation_registry（Stage 4 公共化）。"""
        self._reconciliation_registry = value


    # ------------------------------------------------------------------
    # R5 (Stage 4): public properties for private backing attributes
    # ------------------------------------------------------------------
    @property
    def claim_snapshots(self) -> dict[str, dict[str, str]]:
        """本 session 的 claim 基线快照（公开接口，backing store: _claim_snapshots）。"""
        return self._claim_snapshots

    @claim_snapshots.setter
    def claim_snapshots(self, value: dict[str, dict[str, str]]) -> None:
        self._claim_snapshots = value

    @property
    def claim_snapshots_dir(self) -> Path:
        """claim 快照磁盘持久化目录（公开接口，backing store: _claim_snapshots_dir）。"""
        return self._claim_snapshots_dir

    @claim_snapshots_dir.setter
    def claim_snapshots_dir(self, value: Path) -> None:
        self._claim_snapshots_dir = value

    @property
    def registry(self):
        """session 注册表（公开接口，backing store: _registry）。"""
        return self._registry

    @registry.setter
    def registry(self, value) -> None:
        self._registry = value

    @property
    def gate_registry(self):
        """pre-commit 门禁注册表（Stage 4 公共化，backing store: _gate_registry）。"""
        return self._gate_registry

    @gate_registry.setter
    def gate_registry(self, value) -> None:
        self._gate_registry = value

    @property
    def in_commit_flow(self) -> bool:
        """commit 守卫标志（Stage 4 公共化，backing store: _in_commit_flow）。"""
        return self._in_commit_flow

    @in_commit_flow.setter
    def in_commit_flow(self, value: bool) -> None:
        self._in_commit_flow = value

    def _get_worktree_manager(self):
        """延迟获取 WorktreeManager 单例。"""
        if self._worktree_mgr is None:
            from zephyr.gov_enforcement.rule_bridge.worktree_manager import WorktreeManager
            self._worktree_mgr = WorktreeManager(self.project_root)
        return self._worktree_mgr

    def warn_non_worktree_commit(self, session_id: str, wt_session: str | None) -> None:
        """S3-D 治本（2026-07-17）：非 worktree commit 并发风险警告。

        非 worktree commit 时检测是否有其他活跃 session：
        - 有其他活跃 session → WARN（并发风险：共享工作区 commit 可能搭便车带入
          其他 session WIP，FP-ISO.4C worktree 物理隔离能治本）
        - 无其他活跃 session → INFO（solo 工作，无并发风险，向后兼容直接 commit）
        - 在 worktree 内 → INFO（物理隔离生效，无风险）

        设计决策：不阻断非 worktree commit（向后兼容 Trae IDE 无法自动触发
        worktree 的场景），只在有并发风险时 WARN 提醒。对标 FP-ISO.4C 君子协定
        ——AI 自觉使用 worktree，gate 不强制。
        """
        if wt_session is not None:
            logger.info(
                "GitCommitGateway: 在 session worktree 内 commit，物理隔离生效（session=%s, wt=%s）",
                session_id, wt_session,
            )
            return
        # 非 worktree commit——检查是否有其他活跃 session（并发风险判定）
        try:
            # #ARCH-RECONCILER-WORKTREE-RACE 治本（2026-08-09）：
            # 与 worktree_required_gate.py 对齐——排除 reconciler worker session
            # （worker-{sha8}-{pid}）。worker 是 commit 下游产物（held_files 空、变更经
            # gateway 串行提交），无搭便车风险。不排除则每次 commit 有活跃 worker 都产
            # 噪音 WARN（非阻断，但治理噪音 + 与 gate 判定标准不一致=第二决策点）。
            other_active = [
                s for s in self.registry.list_active()
                if s.session_id != session_id
                and not s.session_id.startswith("worker-")
            ]
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            other_active = []
        if other_active:
            other_ids = [s.session_id for s in other_active]
            logger.warning(
                "GitCommitGateway: 非 worktree commit 且有其他活跃 session（session=%s, "
                "others=%s）——并发风险：共享工作区 commit 可能搭便车带入其他 session WIP。"
                "建议使用 session_worktree_start 实现物理隔离，或等待其他 session 完成后再 commit。",
                session_id, other_ids,
            )
        else:
            logger.info(
                "GitCommitGateway: 不在 session worktree 内（session=%s，无其他活跃 session）——"
                "建议使用 WorktreeManager.create_session_worktree 实现物理隔离，向后兼容直接 commit",
                session_id,
            )

    def _warn_non_worktree_commit(self, session_id: str, wt_session: str | None) -> None:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.warn_non_worktree_commit(session_id, wt_session)

    def claim_files(
        self, session_id: str, files: list[str], adopt_prior_work: bool = False
    ) -> list[str]:
        """为 session 声明持有本次 commit 的文件。claim 失败的文件从返回列表排除。

        ARCH-054: claim 成功后捕获文件基线快照（git diff HEAD -- <file>），
        供 FOREIGN-CHANGE-DETECTION gate 在 commit 时检测搭便车变更。

        adopt_prior_work: 治本(2026-07-23)——跨 session 续作场景认领前序未提交变更。
            True 时对有实际 diff 的文件记录审计日志（实际基线 diff_size+sha256 落
            .runtime/claim_snapshots/{sid}_adopted.jsonl）但存储空基线，使 FOREIGN-CHANGE
            gate 放行。与 allow_overlap 的区别：allow_overlap 在 commit 时绕过 gate，
            adopt_prior_work 在 claim 时认领（gate 仍执行、附审计）。默认 False 行为不变。
        """
        claimed: list[str] = []
        for f in files:
            if self.registry.claim_file(session_id, f):
                claimed.append(f)
                #ARCH-054: 捕获基线快照（claim 时文件的 git diff HEAD 状态）
                try:
                    abs_f = os.path.abspath(f)
                    # tracker #92 治本（2026-08-16）：本 session 已有基线记录=此前已 claim，
                    # 幂等重跑（如 CLI commit 主流程自带重跑）保留首次基线不重捕获——
                    # 基线语义=「首次 claim 时刻」（FOREIGN-CHANGE gate 判定锚点），
                    # 重捕获会把 adopt 的空基线/首次干净基线覆盖为 commit 时刻真基线，破坏语义。
                    # release_files 删快照后重新捕获，生命周期自洽。
                    if abs_f in self.claim_snapshots.get(session_id, {}):
                        continue
                    actual_baseline = self.capture_baseline_diff(abs_f)
                    if adopt_prior_work and actual_baseline:
                        # 治本(2026-07-23): 认领跨 session 前序工作——审计记录实际基线，
                        # 存储空基线让 FOREIGN-CHANGE gate 放行（替代 stash 舞蹈/逃生通道）
                        self._log_adopted_work(session_id, abs_f, actual_baseline)
                        baseline = ""
                    else:
                        baseline = actual_baseline
                    self.claim_snapshots.setdefault(session_id, {})[abs_f] = baseline
                    # S3-C: 持久化到磁盘（进程崩溃后可恢复）
                    self.save_session_snapshot(session_id)
                except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                    logger.warning(
                        "GitCommitGateway: claim_files 基线快照捕获失败 — file=%s (session=%s)",
                        f, session_id, exc_info=True,
                    )
            else:
                logger.warning(
                    "GitCommitGateway: claim_files conflict — file=%s held by other session, "
                    "skipped (session=%s)", f, session_id,
                )
        return claimed

    def release_files(self, session_id: str, files: list[str]) -> None:
        """释放 session 对文件的持有（commit 后调用，静默失败仅 warning）。

        ARCH-054: 同时清理该 session 的基线快照。
        """
        for f in files:
            if not self.registry.release_file(session_id, f):
                logger.debug(
                    "GitCommitGateway: release_files no-op — file=%s not held by session=%s",
                    f, session_id,
                )
        #ARCH-054: 清理 session 的基线快照（内存 + 磁盘，S3-C 治本）
        try:
            self.claim_snapshots.pop(session_id, None)
            self.delete_session_snapshot(session_id)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            pass

    def capture_baseline_diff(self, abs_file: str) -> str:
        """ARCH-054: 捕获文件相对 HEAD 的 diff 基线。

        claim_files 时调用，记录文件在 claim 时刻的 git diff HEAD 状态。
        commit 时 FOREIGN-CHANGE-DETECTION gate 对比：若基线非空，说明 claim 时
        文件已有外来变更（其他 session 的未提交修改），commit 会搭便车提交这些变更。

        Returns:
            git diff HEAD -- <file> 的 stdout（空串=文件干净或 git 不可用）。
        """
        try:
            rel = os.path.relpath(abs_file, str(self.project_root)).replace("\\", "/")
        except ValueError:
            rel = abs_file
        result = self.run_git(["git", "diff", "HEAD", "--", rel])
        if result.returncode != 0:
            return ""
        return result.stdout or ""

    def _capture_baseline_diff(self, abs_file: str) -> str:
        """Deprecated thin wrapper — use capture_baseline_diff."""
        return self.capture_baseline_diff(abs_file)

    def _log_adopted_work(
        self, session_id: str, abs_file: str, actual_baseline: str
    ) -> None:
        """治本(2026-07-23)：认领跨 session 前序工作的审计日志。

        adopt_prior_work=True 且文件有实际 diff 时调用。记录被认领文件的 diff
        大小+sha256(前16位)+domain 到 .runtime/claim_snapshots/{sid}_adopted.jsonl，
        供 commit_gateway_abuse_monitor_reconciler 检测滥用。审计失败不阻断主流程。

        P2（13a5e1d512 治本补强）：追加 domain 字段——从文件 [DOMAIN] 头部读取，
        便于事后审计追溯认领的文件属于哪个功能域（跨域 adopt 是混合提交的信号）。
        """
        try:
            self.claim_snapshots_dir.mkdir(parents=True, exist_ok=True)
            import hashlib
            import re
            import time as _t
            # P2：读取文件 [DOMAIN] 头部（与 commit_scope_gate / domain_fk_gate 同模式）
            domain = "UNKNOWN"
            try:
                with open(abs_file, "r", encoding="utf-8", errors="replace") as fh:
                    for _ in range(20):
                        line = fh.readline()
                        if not line:
                            break
                        m = re.match(r"^#\s*\[DOMAIN\]\s*(\S+)", line)
                        if m:
                            domain = m.group(1)
                            break
            except Exception:  # noqa: BLE001 — 文件不可读（staged delete 等）
                pass
            record = {
                "timestamp": _t.time(),
                "session_id": session_id,
                "file": abs_file,
                "domain": domain,
                "diff_size": len(actual_baseline),
                "diff_sha256": hashlib.sha256(
                    actual_baseline.encode("utf-8", errors="replace")
                ).hexdigest()[:16],
            }
            with (self.claim_snapshots_dir / f"{session_id}_adopted.jsonl").open(
                "a", encoding="utf-8"
            ) as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:  # noqa: BLE001 — 审计失败不阻断 claim
            logger.debug(
                "_log_adopted_work audit write failed (non-blocking)", exc_info=True
            )

    # ------------------------------------------------------------------
    # S3-C 治本（2026-07-17）：claim 快照磁盘持久化
    # ------------------------------------------------------------------
    # 病根：_claim_snapshots 原为纯内存 dict，进程崩溃/重启后快照丢失，
    # FOREIGN-CHANGE-DETECTION gate 降级为 PASS（无快照=不阻断），搭便车
    # 变更检测失效。持久化到 .runtime/claim_snapshots/{session_id}.json
    # 后，新 gateway 实例 __init__ 时从磁盘恢复，gate 可正常对比基线。
    # 磁盘 I/O 异常不阻断主流程（内存 dict 仍为 primary，磁盘是 backup）。

    def load_claim_snapshots_from_disk(self) -> None:
        """__init__ 时从磁盘恢复所有 session 的 claim 快照。

        遍历 ``.runtime/claim_snapshots/*.json``，加载到 ``self.claim_snapshots``。
        损坏文件跳过（log warning），不抛异常。
        """
        try:
            if not self.claim_snapshots_dir.is_dir():
                return
            for snap_file in self.claim_snapshots_dir.glob("*.json"):
                try:
                    data = json.loads(snap_file.read_text(encoding="utf-8"))
                    sid = data.get("session_id", snap_file.stem)
                    snapshots = data.get("snapshots", {})
                    if isinstance(snapshots, dict):
                        self.claim_snapshots[sid] = snapshots
                except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                    logger.warning(
                        "GitCommitGateway: claim snapshot file corrupt, skipped — %s",
                        snap_file, exc_info=True,
                    )
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning(
                "GitCommitGateway: load_claim_snapshots_from_disk failed", exc_info=True,
            )

    def _load_claim_snapshots_from_disk(self) -> None:
        """Deprecated thin wrapper — use load_claim_snapshots_from_disk."""
        self.load_claim_snapshots_from_disk()

    def save_session_snapshot(self, session_id: str) -> None:
        """将单个 session 的快照持久化到 ``{session_id}.json``（原子写入）。

        内存 dict 为 primary，磁盘为 backup——写入失败仅 log warning 不阻断。
        """
        snapshots = self.claim_snapshots.get(session_id)
        if snapshots is None:
            return
        try:
            self.claim_snapshots_dir.mkdir(parents=True, exist_ok=True)
            payload = json.dumps(
                {"session_id": session_id, "snapshots": snapshots},
                ensure_ascii=False,
            )
            # 原子写入：tmp + os.replace（对标 SessionRegistry._save）
            snap_path = self.claim_snapshots_dir / f"{session_id}.json"
            tmp_path = snap_path.with_suffix(".json.tmp")
            tmp_path.write_text(payload, encoding="utf-8")
            os.replace(tmp_path, snap_path)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning(
                "GitCommitGateway: save_session_snapshot failed — session=%s",
                session_id, exc_info=True,
            )

    def _save_session_snapshot(self, session_id: str) -> None:
        """Deprecated thin wrapper — use save_session_snapshot."""
        self.save_session_snapshot(session_id)

    def delete_session_snapshot(self, session_id: str) -> None:
        """删除 session 的磁盘快照文件（release_files 时调用）。

        文件不存在或删除失败均静默（磁盘残留无害，下次 claim 会覆盖）。
        """
        try:
            snap_path = self.claim_snapshots_dir / f"{session_id}.json"
            snap_path.unlink(missing_ok=True)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.debug(
                "GitCommitGateway: delete_session_snapshot failed — session=%s",
                session_id, exc_info=True,
            )

    def _delete_session_snapshot(self, session_id: str) -> None:
        """Deprecated thin wrapper — use delete_session_snapshot."""
        self.delete_session_snapshot(session_id)

    def _register_default_reconcilers(self) -> None:
        """注册默认 post-commit reconciler（声明式框架，P2-T1~T9 + 红蓝发现1 + P3收尾）。"""
        self._reconciliation_registry.register(make_manifest_reconciler(self))
        self._reconciliation_registry.register(make_path_tree_reconciler(self))
        self._reconciliation_registry.register(make_path_ownership_reconciler(self))  # path_ownership_map.yaml 自动同步
        self._reconciliation_registry.register(make_depgraph_ops_reconciler(self))  # 裁定#209 阶段1
        self._reconciliation_registry.register(make_blueprint_frontmatter_reconciler(self))  # ARCH-FRONTMATTER-STATE-001 Phase 2 (Link B)
        self._reconciliation_registry.register(make_drift_scan_reconciler(self))  # MOD-GOV-ALIGNMENT-LOOP §4.S1
        self._reconciliation_registry.register(make_drift_fix_reconciler(self))  # MOD-GOV-ALIGNMENT-LOOP §4.S2
        self._reconciliation_registry.register(make_module_id_recommend_reconciler(self))  # MOD-GOV-ALIGNMENT-LOOP §4.S4
        self._reconciliation_registry.register(make_yaml_sync_reconciler(self))
        # Phase 3 收敛：以下 3 个纯校验 reconciler 已升级为 pre-commit gate（见上方 _gate_registry）
        # make_precommit_id_uniqueness_reconciler / make_exempt_zone_frontmatter_reconciler /
        # make_module_id_consistency_reconciler 不再 post-commit 注册（warn->阻断前移）
        self._reconciliation_registry.register(make_vocab_change_reconciler(self))
        self._reconciliation_registry.register(make_ttl_drift_incremental_reconciler(self))  # #73 TTL 声明质保链·增量校验（priority=285，post-commit warn-only，对齐 decision_tree）
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
        self._reconciliation_registry.register(make_arch_diagram_reconciler(self))  # 议题3: 02_enterprise_architecture 下 9 个架构图生成器自动重生（decision/dataflow/integration/cross_domain/constraint/capacity/capability/navigation）
        self._reconciliation_registry.register(make_constraint_detect_reconciler(self))  # 补齐断链: 5 类违规检测器（跨域/容量/硬上限/孤儿/层级），写 PG arch_constraints 表，在 GATE-ARCH-DIAGRAM 之前跑
        self._reconciliation_registry.register(make_gate_inventory_sync_reconciler(self))  #ARCH-055 commit_gates 模块清单漂移正向检测（post-commit warn-only，priority=820）
        self._reconciliation_registry.register(make_gate_registry_sync_reconciler(self))  #ARCH-GATE-REGISTRY-SYNC-001 gate_registry.yaml 自动重生成（对标 make_manifest_reconciler，post-commit priority=830）
        self._reconciliation_registry.register(make_in_process_gate_registry_drift_reconciler(self))  # #ARCH-GATE-REGISTRY-AUTO-001 Phase 6——in_process_gate_registry.yaml ↔ 内存注册表双向漂移检测（priority=831）
        self._reconciliation_registry.register(make_tmp_cleanup_reconciler(self))  # tmp/ TTL 自动清理（priority=49，对标 make_runtime_cleanup_reconciler，治本 249+ 文件残留）
        self._reconciliation_registry.register(make_worktree_lifecycle_reconciler(self))  # worktree 残留事件驱动清理（P2，治本遗留项#2，2026-07-17，priority=800）
        self._reconciliation_registry.register(make_stash_lifecycle_reconciler(self))  # #ARCH-WORKTREE-002 Phase 4 stash 过期清理（priority=801，清理 >24h 的 session_worktree 临时 stash）
        self._reconciliation_registry.register(make_session_staging_lifecycle_reconciler(self))  # #ARCH-ROOT-TEMP-FILE-ENFORCEMENT-001 staging TTL 清理（priority=802，清理 .runtime/sessions/*/staging/ 下 >24h 文件）
        self._reconciliation_registry.register(make_root_temp_sweep_reconciler(self))  # #ARCH-ROOT-TEMP-FILE-ENFORCEMENT-001 根目录临时文件清扫（priority=803，FS-scan 补强 DCR-007 commit gate 看不到 gitignored 文件的盲区）
        self._reconciliation_registry.register(make_git_guard_bypass_reconciler(self))  # #ARCH-GIT-SELF-HARM-GUARD L2.3 alias 绕过检测（priority=810，post-commit warn-only，对比 reflog reset 与审计日志）
        self._reconciliation_registry.register(make_scripts_import_integrity_reconciler(self))  # ARCH-TOOL-HEALTH-V1 Phase 3 scripts import baseline 全扫（priority=210，post-commit 补强 pre-commit gate 只扫 staged 的盲区）
        self._reconciliation_registry.register(make_undefined_name_baseline_reconciler(self))  # GATE-DEPGRAPH-OPS 治本 Phase 1 undefined-name baseline 全扫（priority=211，post-commit 补强 UNDEFINED-NAME gate 只扫 staged + --no-verify 绕过盲区）
        self._reconciliation_registry.register(make_consumers_accuracy_baseline_reconciler(self))  # #ARCH-CONSUMERS-ACCURACY-001/003 治本 Phase 2 CONSUMERS baseline 全扫（priority=212，post-commit 补强 CONSUMERS-ACCURACY gate 只扫 staged 的盲区）
        self._reconciliation_registry.register(make_capability_lookup_health_reconciler(self))  # #ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD Phase 4 G6 监控欠缺（priority=220，post-commit 检测 [no-lookup:] bypass 频率 + audit log 健康）
        self._reconciliation_registry.register(make_blueprint_id_legacy_reconciler(self))  # ARCH-DATAQUALITY-V1.8 Task I blueprint_id legacy baseline 全扫（priority=145，post-commit warn-only，检测存量 119 条 invalid [BLUEPRINT] 头部，落盘报告供追踪，与 BLUEPRINT-FORMAT gate 互补——gate 防蔓延，reconciler 清存量）
        self._reconciliation_registry.register(make_remediation_progress_reconciler(self))  # #ARCH-GOV-CONVERGENCE-META Phase 3.1 治本进度新鲜度（priority=900，>90天未更新 block_next）
        self._reconciliation_registry.register(make_runtime_violation_snapshot_reconciler(self))  # #ARCH-GOV-CONVERGENCE-META Phase 3.4b trae_060 §5 evidence 运行时快照（priority=850，post-commit 事件触发）
        self._reconciliation_registry.register(make_git_performance_monitor_reconciler(self))  # ARCH-GIT-CALL-BUDGET P3.5 git status 计时持续监控 + stale worktree 累积预警 + 退化趋势检测（priority=870，post-commit 事件触发，warn-only）
        self._reconciliation_registry.register(make_commit_gateway_abuse_monitor_reconciler(self))  # ARCH-TOOL-HEALTH-V1 Phase 5b commit gateway 持续滥用监控（priority=875，post-commit 事件触发，五维滥用检测 warn-only，补强 POST-COMMIT-GUARD 1h 短窗口盲区）
        self._reconciliation_registry.register(make_error_pattern_consumer_reconciler(self))  # #ARCH-PREVENTABILITY-LAYER-001 Phase 4 P4-1b AI behavior telemetry JSONL 错误事件聚合 consumer（priority=880，post-commit 事件触发，聚合到 .runtime/ai_error_patterns/aggregated_patterns.json）
        self._reconciliation_registry.register(make_workspace_hygiene_reconciler(self))  # ARCH-TOOL-HEALTH-V1 Phase 6 + DEBT-WORKSPACE-001/002 工作区卫生自动清理（priority=890，post-commit auto-sync 产物 git restore 还原）
        self._reconciliation_registry.register(make_dead_public_wrapper_reconciler(self))  # #ARCH-STAGE4-PUBLIC-WRAPPER-DEAD-CODE-001 防复发——死公共 wrapper 持续自动检测（priority=950，post-commit warn-only）
        self._reconciliation_registry.register(make_translation_coverage_reconciler(self))  # TRANSLATION-COVERAGE Layer 4——翻译覆盖率存量对账（priority=951，post-commit warn-only，全扫 depgraph vs 翻译真源，落盘 drift_report.json）
        self._reconciliation_registry.register(make_cross_layer_contract_signature_reconciler(self))  # 12维度审计自动化 P1-b——跨层契约签名漂移检测（priority=215，post-commit 事件触发，对比 [C_contract] 签名 git show HEAD~1 vs HEAD）
        self._reconciliation_registry.register(make_blueprint_status_transition_reconciler(self))  # 12维度审计自动化 P1-d——BLUEPRINT 状态转跃检测（priority=825，post-commit 事件触发，STABILITY/MATURITY 逆向转跃 hard-fail）
        from zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog import (  # noqa: PLC0415
            make_worktree_drift_watchdog_reconciler,
        )
        self._reconciliation_registry.register(make_worktree_drift_watchdog_reconciler(self))  # #ARCH-WORKTREE-WRITE-INTEGRITY-001 P0-1/P0-2 工作区 tracked 漂移看门狗（priority=845，ensure-daemon+即时一扫，陈旧覆写发现靠机制）
        # 注册备份reconciler（MOD-INF-027，post-commit事件触发，8h间隔保护）
        try:
            import sys as _sys
            _backup_dir = str(self.project_root / "scripts" / "backup")
            if _backup_dir not in _sys.path:
                _sys.path.insert(0, _backup_dir)
            from backup_reconciler import make_backup_reconciler
            self._reconciliation_registry.register(make_backup_reconciler(self.project_root))
        except ImportError as e:
            logger.warning("backup_reconciler not registered: %s", e)

        # 注册 README 版本号派生校验 reconciler（MOD-GOV-readme_version_sync，2026-07-19 治本）
        # 校验 README.md "环境要求"章节版本号与真源（pyproject.toml + infrastructure_registry.yaml）一致
        # 漂移时 warn 不阻断（版本升级需人工决策），priority=210 晚于 BACKUP-RECONCILER(200)
        try:
            import sys as _sys
            _doc_sync_dir = str(self.project_root / "scripts" / "governance" / "d8_doc_sync")
            if _doc_sync_dir not in _sys.path:
                _sys.path.insert(0, _doc_sync_dir)
            from readme_version_sync_reconciler import make_readme_version_sync_reconciler
            self._reconciliation_registry.register(make_readme_version_sync_reconciler(self.project_root))
        except ImportError as e:
            logger.warning("readme_version_sync_reconciler not registered: %s", e)

        # 注册 requirements↔pyproject 依赖一致性校验 reconciler（MOD-requirements_version_sync，2026-08-01 治本 AI-01 W1）
        # 校验 requirements.txt / requirements-dev.txt / requirements-demo.txt 与 pyproject.toml 依赖集一致
        # 漂移时 warn 不阻断（版本约束变更需人工决策），priority=230 晚于 METRIC-COUNT-DRIFT(220)
        try:
            import sys as _sys
            _doc_sync_dir = str(self.project_root / "scripts" / "governance" / "d8_doc_sync")
            if _doc_sync_dir not in _sys.path:
                _sys.path.insert(0, _doc_sync_dir)
            from requirements_version_sync_reconciler import make_requirements_version_sync_reconciler
            self._reconciliation_registry.register(make_requirements_version_sync_reconciler(self.project_root))
        except ImportError as e:
            logger.warning("requirements_version_sync_reconciler not registered: %s", e)

        # 注册 dashboard 指标数描述派生校验 reconciler（MOD-metric_count_drift，#ARCH-HEALTH-DASHBOARD-001 阶段2，2026-07-20 治本）
        # 校验 architecture_health_dashboard.py METRICS 列表长度与 4 个派生文件指标数描述一致
        # 漂移时 warn 不阻断（描述同步需人工决策），priority=220 晚于 README-VERSION-SYNC(210)
        try:
            import sys as _sys
            _doc_sync_dir = str(self.project_root / "scripts" / "governance" / "d8_doc_sync")
            if _doc_sync_dir not in _sys.path:
                _sys.path.insert(0, _doc_sync_dir)
            from metric_count_drift_reconciler import make_metric_count_drift_reconciler
            self._reconciliation_registry.register(make_metric_count_drift_reconciler(self.project_root))
        except ImportError as e:
            logger.warning("metric_count_drift_reconciler not registered: %s", e)

        # 注册 ALGO_FLOW 标记 ↔ 翻译真源漂移检测 reconciler（MOD-algo_flow_translation_drift，#ARCH-69，2026-08-13 算法地图落地遗留问题1）
        # 校验 src/zephyr 模块 docstring ALGO_FLOW 标记 name_zh/intro 与 factor_registry/mtr algo_submodules 一致
        # 漂移时 warn 不阻断（翻译对齐方向需人工决策），priority=240 晚于 REQUIREMENTS-VERSION-SYNC(230)
        try:
            import sys as _sys
            _doc_sync_dir = str(self.project_root / "scripts" / "governance" / "d8_doc_sync")
            if _doc_sync_dir not in _sys.path:
                _sys.path.insert(0, _doc_sync_dir)
            from algo_flow_translation_reconciler import make_algo_flow_translation_reconciler
            self._reconciliation_registry.register(make_algo_flow_translation_reconciler(self.project_root))
        except ImportError as e:
            logger.warning("algo_flow_translation_reconciler not registered: %s", e)

    # ------------------------------------------------------------------
    # 公开 API
    # ------------------------------------------------------------------
    def _filter_existing_files(self, abs_files: list[str]) -> list[str]:
        """过滤不存在且未 git 跟踪的文件（保留 deletion commit / staged delete 场景）。"""
        existing: list[str] = []
        for f in abs_files:
            if os.path.isfile(f):
                existing.append(f)
            else:
                rel = os.path.relpath(f, str(self.project_root)).replace("\\", "/")
                if self.is_git_tracked(rel) or self._is_staged_delete(rel):
                    existing.append(f)
        return existing

    def _check_gate_results(self, gate_results: list) -> CommitResult | None:
        """检查门禁结果，返回 CommitResult 表示阻断、None 表示全部通过。"""
        for gr in gate_results:
            if not gr.passed:
                if gr.gate_id == "HELD-OVERLAP":
                    return CommitResult(status=CommitStatus.HELD_OVERLAP_VIOLATION, message=gr.detail)
                if gr.gate_id == "CLAIM-REQUIRED":
                    return CommitResult(status=CommitStatus.CLAIM_REQUIRED_VIOLATION, message=gr.detail)
                if gr.gate_id == "WORKTREE-REQUIRED":  # #ARCH-WORKTREE-GATE-001
                    return CommitResult(status=CommitStatus.WORKTREE_VIOLATION, message=gr.detail)
                if gr.gate_id == "FOREIGN-CHANGE-DETECTION":  #ARCH-054
                    return CommitResult(status=CommitStatus.FOREIGN_CHANGE_VIOLATION, message=gr.detail)
                if gr.gate_id == "COMMIT-SCOPE":  # 跨域混合提交治本（13a5e1d512）
                    return CommitResult(status=CommitStatus.COMMIT_SCOPE_VIOLATION, message=gr.detail)
                if gr.gate_id == "FILE-PLACEMENT-TTL" and gr.detail.startswith("PROMOTION_BLOCKED"):
                    return CommitResult(status=CommitStatus.PROMOTION_BLOCKED, message=gr.detail)
                return CommitResult(
                    status=CommitStatus.COMMIT_FAILED,
                    message=f"门禁 {gr.gate_id} 阻断: {gr.detail}",
                )
        return None

    def check_ssot_canonical(self, abs_files: list[str]) -> tuple[bool, str]:
        """L2 兜底门禁：检测新增 .py 文件是否声明已有 module_path（SSoT 冲突）。

        L1 scaffold 是主防线，本方法是 L2 兜底——防止 AI 绕过 scaffold 直接 Write
        新文件后 commit。检测范围仅限 ``src/zephyr/`` 下未 git-tracked 的 .py 文件。

        策略：
          - 只检查 src/zephyr/ 下的 .py 文件（其他路径/扩展名跳过）
          - 跳过已 git-tracked 文件（视为修改而非新增）
          - 解析 [MODULE] 头，反查 find_files_by_module_path
          - 命中已有文件 = SSoT 冲突 = 阻断
          - capability_lookup 不可用时 fail-open（L1 是主防线，L2 是兜底）

        （Stage 4 公共化，primary）
        """
        # 步骤1：筛选 src/zephyr/ 下未跟踪的 .py 文件
        new_py_files: list[tuple[str, str]] = []
        for abs_path in abs_files:
            norm_abs = abs_path.replace("\\", "/")
            if not norm_abs.endswith(".py"):
                continue
            try:
                rel = os.path.relpath(abs_path, str(self.project_root)).replace("\\", "/")
            except ValueError:
                continue
            if not rel.startswith("src/zephyr/"):
                continue
            if self.is_git_tracked(rel):
                continue
            new_py_files.append((abs_path, rel))

        if not new_py_files:
            return (True, "no new src/zephyr/*.py files to check (all skipped or empty)")

        try:
            from zephyr.governance.capability_lookup import CapabilityLookup
        except Exception as e:  # noqa: BLE001 — fail-open
            return (True, f"SSoT 兜底门禁 fail-open: capability_lookup 不可用 (import failed: {e})")

        try:
            lookup = CapabilityLookup()
        except Exception as e:  # noqa: BLE001 — fail-open
            return (True, f"SSoT 兜底门禁 fail-open: capability_lookup 不可用 (init failed: {e})")

        for abs_path, rel_path in new_py_files:
            try:
                header = lookup.parse_header(Path(abs_path), rel_path)
            except Exception:  # noqa: BLE001 — 单文件解析失败不阻断整体
                continue
            if not header.module_path:
                continue
            conflicts = lookup.find_files_by_module_path(header.module_path)
            conflicts = [c for c in conflicts if c != rel_path]
            if conflicts:
                conflict_basenames = [Path(c).name for c in conflicts]
                detail = (
                    f"SSoT 冲突：新文件 {rel_path} 声明的 module_path "
                    f"'{header.module_path}' 已被以下文件声明：{conflicts}"
                    f"（basename: {conflict_basenames}）——违反 SSoT 真源唯一原则。\n"
                    f"  修复指令：删除上述新增文件，扩展现有 canonical 文件后重新 commit。\n"
                    f"  查已有 canonical：python -m zephyr.governance.capability_lookup --find <关键词>"
                )
                return (False, detail)

        return (
            True,
            f"SSoT 兜底门禁 passed: {len(new_py_files)} new src/zephyr/*.py files checked, no new conflict",
        )

    def _check_ssot_canonical(self, abs_files: list[str]) -> tuple[bool, str]:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.check_ssot_canonical(abs_files)

    def _run_post_commit_reconcile(self, existing: list[str], session_id: str, result: CommitResult, commit_message: str='') -> None:
        """向后兼容 thin wrapper（Stage 4 公共化，反向层级）。"""
        return self.run_post_commit_reconcile(existing, session_id, result, commit_message)

    def _snapshot_worktree_status(self, session_id: str, result: CommitResult) -> None:
        """commit 成功后自动打 worktree git status 快照入审计（S3 观测层治本）。

        2026-08-14 worktree wipe 裁定书 S3：事故时无任何 worktree 状态留痕，
        4 个 worker 启动即死无从追查。每次网关 commit 成功后落一条 JSONL 到
        ``.runtime/gate_audit/worktree_status_snapshots.jsonl``——
        分支头（ahead/behind）+ dirty 条目清单（cap 200）+ dirty 计数。
        best-effort fail-open：快照失败永不阻断 commit。
        """
        if result.status is not CommitStatus.OK:
            return
        try:
            import json as _json
            from datetime import datetime, timezone

            r = self.run_git(["git", "status", "--porcelain=v1", "--branch"])
            lines = (r.stdout or "").splitlines() if r.returncode == 0 else []
            branch_header = lines[0] if lines and lines[0].startswith("##") else ""
            dirty = [ln for ln in lines if ln and not ln.startswith("##")]
            audit_dir = self.project_root / ".runtime" / "gate_audit"
            audit_dir.mkdir(parents=True, exist_ok=True)
            record = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "session_id": session_id,
                "commit_hash": result.commit_hash,
                "worktree_root": str(self.project_root),
                "branch_header": branch_header,
                "dirty_count": len(dirty),
                "dirty_entries": dirty[:200],
                "truncated": len(dirty) > 200,
                "git_rc": r.returncode,
            }
            with (audit_dir / "worktree_status_snapshots.jsonl").open("a", encoding="utf-8") as f:
                f.write(_json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:  # noqa: BLE001 — 快照 best-effort，失败不阻断 commit
            logger.debug("worktree status snapshot write failed (non-blocking)", exc_info=True)

    def _post_flush_rules_integrity_re_register(self, session_id: str) -> None:
        """flush 后重注册 rules_integrity 基线（治本时序竞态，2026-08-02 audit-02）。

        病根：reconcile_for 内 GATE-INTEGRITY-AUDIT 的 --register 用
        ``_hash_git_head()`` 读 pre-flush HEAD（``git show HEAD:``），而
        manifest/catalog 等 reconciler 变更在 ``flush()`` 后才入 HEAD，导致 DB
        基线滞后一周期 → ``script_manifest.yaml`` /
        ``capability_canonical_file_registry.yaml`` 永久 TAMPERED。

        修复：flush 后（batcher 已 disable）再跑一次 ``--register``，读 post-flush
        HEAD（含所有 reconciler 变更），DB 基线 = 最终状态 → ``--check`` 0 TAMPERED。

        安全性：仍用 ``_hash_git_head()``（HEAD-based），红蓝发现3 的 WIP 篡改防护
        不降级——post-flush HEAD 不含未 commit 的 WIP 篡改（攻击者篡改 protected
        文件不入 commit，flush 不会将其纳入 HEAD）。

        递归安全：``_commit_auto`` 不触发 reconciler（见 _commit_auto docstring），无递归。
        fail-open：任何异常降级为 warning log，不阻断主流程。
        """
        import os as _os
        import subprocess as _sp
        import sys as _sys
        _env = dict(_os.environ)
        _env["ZEPHYR_RECONCILER_MODE"] = "1"
        _script = "scripts/governance/meta/validate_rules_integrity.py"
        try:
            reg_result = _sp.run(
                [_sys.executable, _script, "--register"],
                cwd=str(self.project_root),
                capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                timeout=30, env=_env,
            )
        except Exception as e:  # noqa: BLE001 — fail-open 不阻断主流程
            logger.warning("post-flush rules_integrity --register error: %s", e)
            return
        if reg_result.returncode != 0:
            logger.warning(
                "post-flush rules_integrity --register failed (rc=%d): %s",
                reg_result.returncode, (reg_result.stderr or "")[:200],
            )
            return
        # 提交 DB 变更（_commit_auto 不触发 reconciler，无递归）
        _db_rel = "scripts/governance/meta/rules_integrity_db.json"
        _diff = self.run_git(["git", "diff", "--name-only", "--", _db_rel])
        if _diff.returncode == 0 and not _diff.stdout.strip():
            return  # DB 无变更（基线已匹配 post-flush HEAD）
        _abs_db = str(self.project_root / _db_rel)
        _msg = ("chore(integrity): post-flush re-register rules_integrity_db "
                "(capture final HEAD, 时序竞态治本 2026-08-02)")
        _cr = self._commit_auto(session_id, [_abs_db], _msg)
        if _cr.status == "OK":
            logger.info(
                "post-flush rules_integrity re-registered (hash=%s, session=%s)",
                _cr.commit_hash, session_id,
            )
        elif _cr.status == "NOTHING_TO_COMMIT":
            logger.debug("post-flush rules_integrity: no DB drift")
        else:
            logger.warning(
                "post-flush rules_integrity DB auto-commit %s: %s",
                _cr.status, (_cr.message or "")[:200],
            )

    def _run_post_commit_reconcile_sync(
        self, existing: list[str], session_id: str, commit_message: str = "",
        result: CommitResult | None = None,
    ) -> list[ReconcileResult]:
        """同步执行 reconciler 链路（原 _run_post_commit_reconcile 主体逻辑）。

        Args:
            existing: 已 commit 的文件绝对路径列表。
            session_id: commit session_id。
            commit_message: commit message（审计追溯用）。
            result: 可选 CommitResult——传入则填充 ``result.reconcile`` 字段（同步模式向后兼容）。

        Returns:
            reconcile_results 列表（worker 用于统计）。
        """
        try:
            # ARCH-GIT-CALL-BUDGET P2.3 (2026-07-19): batched auto-commit wrapper.
            with self._batcher as _batcher_ctx:
                _batcher_ctx.enable(session_id)
                reconcile_results = self._reconciliation_registry.reconcile_for(
                    existing, session_id, commit_message=commit_message,
                )
            # 治本（2026-08-02 audit-02 时序竞态）：flush 后重注册 rules_integrity 基线，
            # 读 post-flush HEAD（含所有 reconciler 变更）→ 消除 DB 滞后导致的永久 TAMPERED。
            # GATE-INTEGRITY-AUDIT 在 reconcile_for 内已 defer（见 _reconcile_rules_integrity）。
            self._post_flush_rules_integrity_re_register(session_id)
            if result is not None:
                result.reconcile = reconcile_results
            # 治本 #ARCH-ASSET-INDEX-FALSE-AUTO-COMMIT-001：flush() 失败时降级
            # auto_committed → warn，防止日志误报"已自动提交"但文件未真正提交。
            _downgrade_auto_committed_on_flush_failure(
                reconcile_results, getattr(self._batcher, "_last_flush_result", None),
            )
            # #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 2: 持久化 reconciler 执行结果
            # 到 governance.db reconcile_execution_log 表，消除 fail-silent（失败不可见）。
            # Phase 3.4 断点7: 同时持久化 commit_message 供审计追溯。
            _log_reconcile_results(
                self.project_root, reconcile_results, session_id,
                trigger_source="post_commit", committed_files=existing,
                commit_message=commit_message,
            )
            for rr in reconcile_results:
                if rr.action == "auto_committed":
                    logger.info("GitCommitGateway: post-commit reconcile auto-committed (session=%s): %s", session_id, rr.detail)
                elif rr.action == "warn":
                    logger.warning("GitCommitGateway: post-commit reconcile warning (session=%s): %s", session_id, rr.detail)
                elif rr.action == "clean":
                    logger.info("GitCommitGateway: post-commit reconcile clean (session=%s): %s", session_id, rr.detail)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("GitCommitGateway: post-commit reconcile failed: %s", e, exc_info=True)
            reconcile_results = []
        return reconcile_results

    def _run_post_commit_reconcile_sync_worker(
        self, existing: list[str], session_id: str, commit_message: str = "",
        heartbeat: "Callable[[str], None] | None" = None,
    ) -> list[ReconcileResult]:
        """worker-only 入口：同步执行 reconciler 链路并返回 results。

        与 ``_run_post_commit_reconcile_sync`` 区别：
        - 不传 CommitResult（worker 没有 CommitResult 对象）
        - trigger_source="post_commit_async"（标识异步 worker 调用，便于审计区分）
        - 异常向上抛（worker 兜底捕获写 status=failed）

        供 ``zephyr.governance.audit.reconcile_worker._run_worker`` 调用。
        """
        # ARCH-GIT-CALL-BUDGET P2.3 (2026-07-19): batched auto-commit wrapper.
        with self._batcher as _batcher_ctx:
            _batcher_ctx.enable(session_id)
            reconcile_results = self._reconciliation_registry.reconcile_for(
                existing, session_id, commit_message=commit_message,
                heartbeat=heartbeat,
            )
        # 治本（2026-08-02 audit-02 时序竞态）：flush 后重注册 rules_integrity 基线，
        # 读 post-flush HEAD（含所有 reconciler 变更）→ 消除 DB 滞后导致的永久 TAMPERED。
        self._post_flush_rules_integrity_re_register(session_id)
        # 治本 #ARCH-ASSET-INDEX-FALSE-AUTO-COMMIT-001：flush() 失败时降级
        # auto_committed → warn，防止日志误报"已自动提交"但文件未真正提交。
        _downgrade_auto_committed_on_flush_failure(
            reconcile_results, getattr(self._batcher, "_last_flush_result", None),
        )
        _log_reconcile_results(
            self.project_root, reconcile_results, session_id,
            trigger_source="post_commit_async", committed_files=existing,
            commit_message=commit_message,
        )
        for rr in reconcile_results:
            if rr.action == "auto_committed":
                logger.info("GitCommitGateway: worker reconcile auto-committed (session=%s): %s", session_id, rr.detail)
            elif rr.action == "warn":
                logger.warning("GitCommitGateway: worker reconcile warning (session=%s): %s", session_id, rr.detail)
        return reconcile_results

    def _run_post_commit_reconcile_async(self, existing: list[str], session_id: str, commit_sha: str, commit_message: str='') -> None:
        """向后兼容 thin wrapper（Stage 4 公共化，反向层级）。"""
        return self.run_post_commit_reconcile_async(existing, session_id, commit_sha, commit_message)

    def commit(
        self,
        session_id: str,
        files: list[str],
        message: str,
        allow_promote: bool = False,
        allow_overlap: bool = False,
        allow_derived_deletion: bool = False,
        allow_non_worktree: bool = False,
        allow_multi_domain: bool = False,
        merge_finalize: bool = False,
    ) -> CommitResult:
        """串行化 commit 入口。allow_overlap 逃生通道放行被其他 session 持有的文件，追加 [GW:<sid>:overlap] 标记。
        allow_derived_deletion 逃生通道放行受保护派生文件删除（#ARCH-BP-REGISTRY-DELETION-001 P1）。
        allow_non_worktree 逃生通道放行 WORKTREE-REQUIRED gate（#ARCH-WORKTREE-GATE-001 治本）。
        merge_finalize=True 显式完成在途 merge（B2 治本①）：MERGE_HEAD 存在时普通 commit
        一律拒绝（防截胡张冠李戴），仅本标志放行全量 commit 并追加 [GW:<sid>:merge] 留痕。"""
        if not files:
            return CommitResult(status=CommitStatus.NOTHING_TO_COMMIT, message="empty files list")
        if not session_id:
            session_id = "unknown"

        # 归一化为绝对路径（用 abspath 而非 resolve()——保留传入大小写与 git index 一致）
        abs_files = [os.path.abspath(f) for f in files]
        existing = self._filter_existing_files(abs_files)
        if not existing:
            return CommitResult(
                status=CommitStatus.NOTHING_TO_COMMIT,
                message="no existing or tracked files to commit",
            )

        # worktree 物理隔离检测（阶段3 治本 stash 循环）
        # S3-D 治本（2026-07-17）：非 worktree commit + 有其他活跃 session → WARN（并发风险）
        try:
            wt_session = self._get_worktree_manager().get_current_worktree()
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            wt_session = None
        self._warn_non_worktree_commit(session_id, wt_session)

        # B2 治本①（2026-08-19，AI-FILL-14 截胡事故）：MERGE_HEAD 盲——
        # 他人 merge --no-commit 晾置时普通 commit 会把 merge 内容连带提交并
        # 张冠李戴 commit message。显式 merge_finalize 才放行（全量 commit）。
        # 判据复用 _is_merge_in_progress（AI-R1-003 红队 worktree 感知原语）。
        if not merge_finalize and self._is_merge_in_progress():
            return self._merge_in_progress_result()

        # tracker #92 治本（2026-08-16）：worktree 物理隔离下，搭便车三 gate
        # （HELD-OVERLAP/CLAIM-REQUIRED/FOREIGN-CHANGE-DETECTION）无检测对象——
        # 同一工作区只有本 session，commit 范围由 pathspec 限定。
        # 跳过集合单一真源=session_worktree._WORKTREE_SKIP_GATES（merge 预演既有消费方，
        # 禁复制清单）；cwd 目录判定不依赖 session 活性。非 worktree 路径三 gate 全量保留。
        _gate_skip: frozenset[str] = frozenset()
        if wt_session is not None:
            from zephyr.gov_enforcement.rule_bridge.session_worktree import (  # noqa: PLC0415 延迟 import 防循环
                _WORKTREE_SKIP_GATES,
            )
            _gate_skip = _WORKTREE_SKIP_GATES

        # tracker #116 B2（#ARCH-119）：PG 可用性前置探针——commit 前置执行
        # TCP 5432 探测（≤1s，失败不阻断只落 .runtime/pg_probe_state.json），
        # 供 #1/#2/#3/#5 depgraph 类 gate 区分「DB 离线降级」vs「真实错误」，
        # 并供 DEPGRAPH-FRESHNESS 离线超 24h 豁免判定。
        try:
            from zephyr.governance.audit.pg_probe import (  # noqa: PLC0415 延迟 import 防循环
                refresh_pg_probe_state,
            )
            refresh_pg_probe_state(self.project_root)
        except Exception:  # noqa: BLE001 — 探针自身失败不阻断 commit
            logger.debug("pg_probe refresh skipped", exc_info=True)

        # #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 3: pre-commit 告警横幅
        # 翻日志本查最近 24h 的 critical_warn，有则打印醒目横幅强制 AI 看到。
        # 不阻断 commit（warn 语义），但确保上次 reconciler 失败不被忽视。
        _print_critical_warn_banner(self.project_root, context="pre_commit")

        # #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 4.2: pre-commit 硬阻断
        # block_next 是最严重的 reconciler 失败级别——下次 commit 硬阻断。
        # 与 critical_warn 的区别：critical_warn 只告警不阻断，block_next 硬阻断。
        # AI 必须先修复问题，调 resolve_blocks() 清除阻断，才能继续 commit。
        _block_err = _print_block_banner(self.project_root, context="pre_commit")
        if _block_err:
            return CommitResult(
                status=CommitStatus.COMMIT_FAILED,
                message=_block_err,
            )

        # commit message 构造（不依赖 staged 状态，锁外构造）
        gw_marker = _GW_MARKER_FMT.format(session_id=session_id)
        full_message = f"{message}\n\n{gw_marker}"
        if merge_finalize:
            full_message += f"\n[GW:{session_id}:merge]"
        if allow_overlap:
            full_message += f"\n[GW:{session_id}:overlap]"
            # TRAE-079 铁律5：allow_overlap 降级为 last-resort（仅文件锁不可用时），落审计
            logger.warning(
                "TRAE-079: allow_overlap=True last-resort escape hatch used by session %s on %d files",
                session_id, len(existing),
            )
        if allow_multi_domain:
            full_message += f"\n[GW:{session_id}:multi-domain]"

        # TRAE-079 铁律1：[gate → stage → commit] 整体在 _GlobalCommitLock 临界区内，消除 TOCTOU
        # 病根：gate 检查在锁外时，另一 session 可在 gate 通过后、commit 前修改文件（搭便车/FOREIGN_CHANGE）
        # 治本：gate 检查移入文件锁临界区，串行化整个 [gate → stage → commit] 不可分割
        try:
            with _GlobalCommitLock(self.project_root):
                # B2① TOCTOU 根治：锁内二次校验（晾置可能发生在锁外 pre-flight 通过之后）
                if not merge_finalize and self._is_merge_in_progress():
                    return self._merge_in_progress_result()
                # B2 治本②：gate 链前清扫 ita 存量残留（staged 校验盲区，merge 误报源）
                self._sweep_intent_to_add_residue(session_id, self._target_rel_set(existing))
                # pre-commit 门禁注册表（架构债务 #AD-001 治本：5 个 in-process gate 替代 12 个硬编码 _check_*）
                # 新增门禁 MUST 走 CommitGateRegistry 注册制（commit_gates/ 下 make_xxx_gate() + __init__ register）
                # commit_message 透传：CAPABILITY-LOOKUP-REQUIRED gate 据此检测 [no-lookup:reason] 逃生标记
                # （#ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD-S1 止血修复：与 session_worktree._run_pre_commit_gates L1174 对称）
                gate_results = self._check_gates_with_drift_watch(
                    existing, session_id, allow_overlap=allow_overlap,
                    allow_promote=allow_promote, commit_message=message,
                    allow_derived_deletion=allow_derived_deletion,
                    allow_non_worktree=allow_non_worktree,
                    allow_multi_domain=allow_multi_domain,
                    skip_gates=_gate_skip,
                )
                blocked = self._check_gate_results(gate_results)
                if blocked is not None:
                    return blocked

                result = self._commit_locked(session_id, existing, full_message, gw_marker)
        except GatewayError as e:
            return CommitResult(status=CommitStatus.LOCK_TIMEOUT, message="internal error")
        except OSError as e:
            # TRAE-079 铁律6：文件锁 fail-open 降级 MUST 落审计
            # 锁文件目录不可写（磁盘满/权限/只读文件系统）→ 降级为无锁 commit + 审计
            _audit_commit_lock_fallback(self.project_root, session_id, str(e))
            logger.warning(
                "TRAE-079: _GlobalCommitLock unavailable (fail-open fallback): %s — "
                "commit proceeding without serialization lock for session %s",
                e, session_id,
            )
            # 无锁降级：直接执行 gate + commit（不串行化，但 gate 仍在）
            if not merge_finalize and self._is_merge_in_progress():
                return self._merge_in_progress_result()
            self._sweep_intent_to_add_residue(session_id, self._target_rel_set(existing))
            gate_results = self._check_gates_with_drift_watch(
                existing, session_id, allow_overlap=allow_overlap,
                allow_promote=allow_promote, commit_message=message,
                allow_derived_deletion=allow_derived_deletion,
                allow_non_worktree=allow_non_worktree,
                allow_multi_domain=allow_multi_domain,
                skip_gates=_gate_skip,
            )
            blocked = self._check_gate_results(gate_results)
            if blocked is not None:
                return blocked
            result = self._commit_locked(session_id, existing, full_message, gw_marker)

        self._snapshot_worktree_status(session_id, result)
        self._run_post_commit_reconcile(existing, session_id, result, commit_message=message)
        return result

    def is_git_tracked(self, rel_path: str) -> bool:
        """检查相对路径是否被 git 跟踪（:(icase) pathspec 兼容 Windows 大小写不敏感）。

        （Stage 4 公共化，primary）
        """
        from zephyr.shared.infra.process_pool import run_subprocess_hidden

        chk = run_subprocess_hidden(
            ["git", "ls-files", "--error-unmatch", "--", f":(icase){rel_path}"],
            capture_output=True,
            cwd=str(self.project_root),
        )
        return chk.returncode == 0

    def _is_git_tracked(self, rel_path: str) -> bool:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.is_git_tracked(rel_path)

    def _is_staged_delete(self, rel_path: str) -> bool:
        """检查相对路径是否为 staged delete（不在 index 但仍在 HEAD）。必需：_is_git_tracked 对 staged delete 返回 False，凡保留/排除 staged delete 场景必须用本方法补充。"""
        if self.is_git_tracked(rel_path):
            return False
        from zephyr.shared.infra.process_pool import run_subprocess_hidden

        chk = run_subprocess_hidden(
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
            chk = self.run_git(["git", "check-ignore", "--no-index", "--"] + batch)
            if chk.returncode == 0 and chk.stdout:
                for line in chk.stdout.splitlines():
                    if line.strip():
                        ignored_rels.add(line.strip().lower())
        return [f for f, rel in zip(files, rels) if rel.lower() in ignored_rels]

    def _run_pathspec_git_cmd(
        self,
        tracked: list[str],
        git_args: list[str],
        error_prefix: str,
    ) -> str | None:
        """通过 --pathspec-from-file 执行 git 命令暂存 tracked 文件。

        P8-fix: 用 --pathspec-from-file 绕过 Windows CLI 长度限制 (WinError 206)，
        大批量 gitignored 文件（如 _backups 1036 个）直接传命令行会超长。
        返回错误字符串（含 stderr）或 None（成功/空批）。
        """
        if not tracked:
            return None
        pathspec = self._write_pathspec_file(tracked)
        try:
            r = self.run_git(git_args + [f"--pathspec-from-file={pathspec}"])
        finally:
            try:
                os.remove(pathspec)
            except OSError:
                pass
        if r.returncode != 0:
            return f"{error_prefix}: {r.stderr.strip()}"
        return None

    def _stage_gitignored_tracked(
        self, files: list[str]
    ) -> tuple[bool, str, list[str]]:
        """暂存 gitignored 且已跟踪的文件，返回 (ok, err, normal_files)。git add 对 gitignored 整批拒绝故分离处理：已删除+已跟踪->git rm --cached；已修改+已跟踪->git add -f；未跟踪的 gitignored->跳过。"""
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
            del_tracked = [f for f, rel in zip(deleted, del_rels) if self.is_git_tracked(rel)]
            err = self._run_pathspec_git_cmd(
                del_tracked,
                ["git", "rm", "--cached", "--ignore-unmatch"],
                "git rm --cached failed",
            )
            if err is not None:
                return False, err, normal_files
        if existing:
            ex_rels = [
                os.path.relpath(f, str(self.project_root)).replace("\\", "/")
                for f in existing
            ]
            ex_tracked = [
                f for f, rel in zip(existing, ex_rels)
                if self.is_git_tracked(rel) and not self._is_staged_delete(rel)
            ]
            err = self._run_pathspec_git_cmd(
                ex_tracked,
                ["git", "add", "-f"],
                "git add -f failed",
            )
            if err is not None:
                return False, err, normal_files
        return True, "", normal_files

    # ------------------------------------------------------------------
    # 内部实现
    # ------------------------------------------------------------------
    def _tracked_area_fingerprint(self) -> str:
        """tracked 区内容指纹（#ARCH-PRECOMMIT-STASH-ADAPT-001 T4-2）。

        拼接 `git diff-files`（unstaged tracked 修改，含 worktree blob hash）与
        `git diff-index --cached HEAD`（staged tracked 修改，含 index blob hash）
        的原始输出取 sha256——任何 gate 运行期对 tracked 文件的写/暂存都会改变
        指纹。git 不可达降级空串（指纹相等→不报警，松约束不阻断主流）。
        """
        from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: PLC0415

        try:
            unstaged = run_subprocess_hidden(
                ["git", "diff-files"], capture_output=True, text=True,
                cwd=str(self.project_root),
            )
            staged = run_subprocess_hidden(
                ["git", "diff-index", "--cached", "HEAD"], capture_output=True,
                text=True, cwd=str(self.project_root),
            )
            import hashlib  # noqa: PLC0415

            blob = f"{unstaged.returncode}:{unstaged.stdout}|{staged.returncode}:{staged.stdout}"
            return hashlib.sha256(blob.encode("utf-8", errors="replace")).hexdigest()
        except Exception:  # noqa: BLE001 — 降级空指纹（不报警不阻断）
            return ""

    def _audit_gate_tracked_drift(self, session_id: str) -> None:
        """gate 运行期 tracked 区漂移=违规：落审计 + stderr 醒目报警（不阻断 commit）。

        裁定原文（#ARCH-PRECOMMIT-STASH-ADAPT-001）：hook 运行期产生的任何
        tracked 区写入一律视为违规并报警，而非静默 stash 掩盖（#55 病根：
        flags.py 门禁运行期向 tracked feature_flags.jsonl 追加审计行→pre-commit
        框架 "files were modified by this hook" 结构性误报）。
        审计落 .runtime/audit/（gitignored——T4-1 铁律：审计写永不回 tracked 区）。
        """
        msg = (
            "GATE-TRACKED-DRIFT VIOLATION: pre-commit gate 运行期 tracked 区发生写入"
            "（#55 族病根回潮——hook 运行期 tracked 写=违规，须审计迁出 tracked 区）"
        )
        import sys  # noqa: PLC0415

        logger.warning("%s (session=%s)", msg, session_id)
        print(f"\n!! {msg}\n   session={session_id}——详见 .runtime/audit/hook_tracked_drift.jsonl", file=sys.stderr)
        try:
            from zephyr.shared.utils.time_utils import now_utc  # noqa: PLC0415

            audit_dir = Path(str(self.project_root)) / ".runtime" / "audit"
            audit_dir.mkdir(parents=True, exist_ok=True)
            record = {
                "timestamp": now_utc().isoformat(),
                "session_id": session_id,
                "violation": "gate_runtime_tracked_drift",
                "context": "pre_commit_gates",
            }
            with open(audit_dir / "hook_tracked_drift.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError:
            pass  # 审计落盘失败不阻断（warn 已发）

    def _check_gates_with_drift_watch(self, existing, session_id, skip_gates=frozenset(), **kwargs):
        """gate 链执行 + tracked 区漂移监视（T4-2）：运行前后指纹比对，漂移即违规报警。

        skip_gates: 透传 CommitGateRegistry.check_all（worktree 隔离跳过集合，
        单一真源=session_worktree._WORKTREE_SKIP_GATES，tracker #92）。
        """
        before = self._tracked_area_fingerprint()
        results = self._gate_registry.check_all(
            self, existing, session_id=session_id, skip_gates=skip_gates, **kwargs
        )
        after = self._tracked_area_fingerprint()
        if before and after and before != after:
            self._audit_gate_tracked_drift(session_id)
        return results

    def _commit_locked(
        self,
        session_id: str,
        files: list[str],
        full_message: str,
        gw_marker: str,
    ) -> CommitResult:
        """持锁状态下执行 add -> commit（阶段3 移除 stash 隔离，worktree 物理隔离替代）。

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
                add_ok, add_fail = self._add_and_remove_normal_files(normal_files)
                if not add_ok:
                    result = add_fail
                else:
                    # 4-6. 检查 staged 变更并 commit
                    result = self._resolve_commit_result(
                        files, normal_files, full_message, pathspec_file, gw_marker
                    )
        finally:
            self._commit_locked_finalize(
                result, files, session_id, full_message, pathspec_file
            )
        return result

    def _add_and_remove_normal_files(
        self, normal_files: list[str],
    ) -> tuple[bool, CommitResult | None]:
        """步骤3：git add existing + git rm deleted（delete 文件 git add 报错，用 git rm 替代）。

        分离 existing 和 deleted——git add 对 delete 文件失败（pathspec did not match），
        需用 git rm 替代（治本 ARCH-030）。--ignore-unmatch 跳过已 staged delete（git rm 幂等）。
        P8-fix: 用 --pathspec-from-file 绕过 Windows CLI 长度限制 (WinError 206)。
        返回 (add_ok, failure_result)：add_ok=True 时 failure_result 为 None。
        """
        add_ok = True
        failure: CommitResult | None = None
        if normal_files:
            existing_files = [f for f in normal_files if os.path.isfile(f)]
            deleted_files = [f for f in normal_files if not os.path.isfile(f)]
            # 3a. git add existing_files（modify/new/rename 目标）
            if existing_files:
                add_pathspec_file = self._write_pathspec_file(existing_files)
                try:
                    add_result = self.run_git(
                        ["git", "add", f"--pathspec-from-file={add_pathspec_file}"]
                    )
                    add_ok = add_result.returncode == 0
                    if not add_ok:
                        logger.warning("GitCommitGateway: git add 失败: %s", add_result.stderr.strip())
                        failure = CommitResult(
                            status=CommitStatus.COMMIT_FAILED,
                            message=f"git add failed: {add_result.stderr.strip()}",
                        )
                finally:
                    try:
                        os.remove(add_pathspec_file)
                    except OSError:
                        pass
            # 3b. git rm deleted_files（delete 文件用 git rm 替代 git add）
            if add_ok and deleted_files:
                del_pathspec = self._write_pathspec_file(deleted_files)
                try:
                    rm_result = self.run_git(
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
                    failure = CommitResult(
                        status=CommitStatus.COMMIT_FAILED,
                        message=f"git rm failed: {rm_result.stderr.strip()}",
                    )
        return add_ok, failure

    def _resolve_commit_result(
        self,
        files: list[str],
        normal_files: list[str],
        full_message: str,
        pathspec_file: str,
        gw_marker: str,
    ) -> CommitResult:
        """步骤4-6：判断 no-pathspec -> 检查 staged 变更 -> commit（rename 检测内置）。"""
        # 4. 判断是否需要无 pathspec commit（gitignored / staged rename）
        has_gitignored = self._should_use_no_pathspec(files, normal_files)
        # 5. 检查 staged 变更
        diff_result = self.run_git(["git", "diff", "--cached", "--quiet"])
        if diff_result.returncode == 0:
            logger.info("GitCommitGateway: files 无 staged 变更，跳过 commit")
            return CommitResult(
                status=CommitStatus.NOTHING_TO_COMMIT,
                message="no staged changes in files_in_scope",
            )
        # 6. commit（rename 检测内置到 _commit_with_file_message）
        pathspec_for_commit = None if has_gitignored else pathspec_file
        commit_hash, commit_err = self._commit_with_file_message(
            full_message, pathspec_for_commit, files
        )
        if commit_hash is None:
            return CommitResult(
                status=CommitStatus.COMMIT_FAILED,
                message=f"git commit failed: {commit_err}",
            )
        os.environ[_GATEWAY_ENV] = "1"
        logger.info(
            "GitCommitGateway: commit 成功 hash=%s marker=%s files=%d",
            commit_hash, gw_marker, len(files),
        )
        return CommitResult(
            status=CommitStatus.OK,
            message=f"committed {len(files)} files",
            commit_hash=commit_hash,
        )

    def _commit_locked_finalize(
        self,
        result: CommitResult,
        files: list[str],
        session_id: str,
        full_message: str,
        pathspec_file: str | None,
    ) -> None:
        """finally：红蓝触发 + session shutdown handoff + pathspec 清理 + 环境变量复位。"""
        # 事件驱动红蓝触发 (MOD-INF-030)：正式脚本/模块提交 -> 写异步触发记录
        if result.status == CommitStatus.OK:
            try:
                self._post_commit_red_blue_trigger(files, session_id, result.commit_hash)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("GitCommitGateway: red-blue trigger emit failed: %s", e, exc_info=True)
        # P4-T2: session shutdown handoff（crash recovery）
        if result.status == CommitStatus.OK:
            try:
                from zephyr.governance.ops_governance.phase_manager import session_shutdown
                session_shutdown(session_id, summary=full_message)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("GitCommitGateway: session_shutdown handoff failed: %s", e, exc_info=True)
        # B2 治本③：commit 后 index-HEAD 一致性校验（warn-only）+ ita 复扫
        if result.status == CommitStatus.OK:
            try:
                self._verify_post_commit_index(files, session_id)
            except Exception as e:  # noqa: BLE001 — 校验失败不掩盖 commit 成功
                logger.warning("GitCommitGateway: post-commit index 校验失败: %s", e, exc_info=True)
        if pathspec_file:
            try:
                os.remove(pathspec_file)
            except OSError:
                pass
        os.environ.pop(_GATEWAY_ENV, None)

    def _post_commit_red_blue_trigger(
        self, files: list[str], session_id: str, commit_hash: str,
    ) -> None:
        """事件驱动红蓝触发 (MOD-INF-030)：正式脚本/模块提交 -> 写异步触发记录 + 事件通知。"""
        from zephyr.security.adversarial_validation.commit_trigger import (
            detect_formal_files,
            write_trigger_record,
        )
        formal_files = detect_formal_files(files)
        if formal_files:
            write_trigger_record(commit_hash, session_id, formal_files)
            self._emit_bus_event("red_blue.trigger.queued", {
                "commit_hash": commit_hash, "session_id": session_id,
            })
            logger.info(
                "GitCommitGateway: red-blue trigger emitted (session=%s hash=%s formal=%d)",
                session_id, commit_hash[:8], len(formal_files),
            )
        # 文件变更通知（驱动 FileWatcher 增量扫描）
        for f in files:
            self._emit_bus_event("file.changed", {
                "path": f, "commit_hash": commit_hash,
            })

    @staticmethod
    def _emit_bus_event(topic: str, payload: dict) -> None:
        """向 EventBusBackpressure 发射事件（fail-open：失败仅 log 不阻断）。"""
        try:
            from zephyr.shared.event_bus import bus as _bus

            _bus.emit(topic, payload)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("GitCommitGateway: emit %s failed: %s", topic, e, exc_info=True)

    def _has_staged_renames(self, target_files: list[str]) -> bool:
        """检测目标文件中是否有 staged rename（R 状态），pathspec 会拆分 rename 需 fallback。"""
        target_rel = {
            os.path.relpath(f, str(self.project_root)).replace("\\", "/")
            for f in target_files
        }
        result = self.run_git(["git", "diff", "--cached", "--name-status", "-M"])
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
        staged_result = self.run_git(["git", "diff", "--cached", "--name-only"])
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
        result = self.run_git(["git", "reset", "HEAD", "--"] + non_target_files)
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
        # 2026-08-14 修复（#ARCH-MERGE-PATH-GAP-001②）：merge finalize 场景。
        # git 禁止 merge 期间 partial commit（fatal: cannot do a partial commit during
        # a merge），且 staged 区合法持有 merge 结果（冲突解决内容），绝不能按
        # target_files 做 staged-clean 校验/自动 unstage（会毁掉 merge 现场）。
        # 检测 MERGE_HEAD → 强制全量 commit（无 pathspec）+ 跳过 staged-clean。
        # AI-R1-003 红队治本：worktree 感知检测（原 .git/MERGE_HEAD 硬编码在
        # linked worktree 下恒 False——.git 是指针文件，见 _is_merge_in_progress）
        # B2 治本①（2026-08-19）：能走到这里且 merge_in_progress=True 的，必经
        # commit() pre-flight 的 merge_finalize 显式放行（否则已被拒）。
        merge_in_progress = self._is_merge_in_progress()
        if merge_in_progress:
            use_pathspec = False
        if use_pathspec and target_files and self._has_staged_renames(target_files):
            use_pathspec = False
        if not use_pathspec:
            if not target_files:
                return None, "无 pathspec commit 需要 target_files 参数"
            if merge_in_progress:
                logger.info("检测到 MERGE_HEAD：merge finalize 走全量 commit，跳过 staged-clean 校验")
                # #ARCH-MERGE-PATH-GAP-001④（2026-08-14 用户遗留上报立项）：
                # merge finalize 全量 commit 会把非目标 staged 文件一并收编（git 禁
                # merge 期间 partial commit，机制不可避免）——可见性兜底：收编前显式
                # 列出非目标 staged 文件，"staged 不等于你的"从静默收编转可见可追责。
                _, _, foreign_staged = self._verify_staged_is_clean(target_files)
                if foreign_staged:
                    logger.warning(
                        "merge finalize 全量 commit 将收编 %d 个非目标 staged 文件"
                        "（git 禁 merge 期间 partial commit，机制设计如此）: %s",
                        len(foreign_staged), foreign_staged,
                    )
            else:
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
        # 治本 #ARCH-ROOT-TEMP-FILE-ENFORCEMENT-001: gw_commit_msg_*.txt 是进程内 IPC
        # token（git -F 传 commit message），零持久价值。真源唯一/责任唯一：进程临时文件
        # 的规范真源是 OS temp dir（由 OS 管理生命周期/清理/隔离）。不传 dir= 即用
        # tempfile.gettempdir()，避免在项目根建立平行真源。git -F 接受任意绝对路径，
        # pathspec 内容用 os.path.relpath(abs, project_root) 计算，与 temp 文件存放位置无关。
        msg_fd, msg_path = tempfile.mkstemp(
            prefix="gw_commit_msg_", suffix=".txt"
        )
        try:
            self.in_commit_flow = True  # 放行 _run_git 的 commit 守卫（红攻1治本）
            with os.fdopen(msg_fd, "w", encoding="utf-8") as f:
                f.write(message)
            if use_pathspec:
                commit_cmd = ["git", "commit", "--no-verify", "-F", msg_path,
                              f"--pathspec-from-file={pathspec_file}"]
            else:
                commit_cmd = ["git", "commit", "--no-verify", "-F", msg_path]
            result = self.run_git(commit_cmd)
            if result.returncode != 0:
                return None, result.stderr.strip() or result.stdout.strip()
            rev_result = self.run_git(["git", "rev-parse", "HEAD"])
            if rev_result.returncode == 0:
                return rev_result.stdout.strip(), ""
            return "", ""
        finally:
            self.in_commit_flow = False
            try:
                os.remove(msg_path)
            except OSError:
                pass

    def _resolve_auto_commit_files(self, files: list[str]) -> list[str]:
        """将 files 解析为绝对路径并过滤出存在或已跟踪的文件（_commit_auto 用）。"""
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
                if self.is_git_tracked(rel):
                    existing.append(f)
        return existing

    def _run_auto_commit_gate(
        self,
        gate_name: str,
        existing: list[str],
        session_id: str,
        violation_prefix: str,
        warning_msg: str,
        check_kwargs: dict | None = None,
    ) -> CommitResult | None:
        """运行 _commit_auto 的单个门禁。

        真源复用：gate_registry.get，不复制门禁逻辑。命中违规返回 CommitResult，
        通过或未注册返回 None（未注册时记 warning，与原内联 else 分支一致）。
        """
        spec = self._gate_registry.get(gate_name)
        if spec is None:
            logger.warning(warning_msg, session_id, len(existing))
            return None
        passed, detail = spec.check(self, existing, **(check_kwargs or {}))
        if not passed:
            return CommitResult(
                status=CommitStatus.NAMING_VIOLATION,
                message=f"{violation_prefix}: {detail}",
            )
        return None

    def _git_add_with_index_lock_retry(
        self, pathspec_file: str, session_id: str,
    ) -> "CommitResult | None":
        """git add 带 index.lock 暂时性竞争重试（#ARCH-RECONCILER-INDEXLOCK-RETRY）。

        根因：外部裸 git commit（绕过 GitCommitGateway）可能持有 .git/index.lock，
        导致 reconciler auto-commit 的 git add 失败。index.lock 是暂时性竞争
        （持有进程完成后释放），且 git add 阶段 commit 未执行，重试不会产生
        重复 commit——区别于 commit 阶段失败的确定性错误盲重试
        （reconciliation_registry.py:3897 反模式，项目明确反对盲重试）。

        策略：只对 "index.lock" + "File exists" 模式重试，最多 3 次，退避 2s/4s。
        其他错误立即返回 COMMIT_FAILED（不重试）。gate-commit-gw 阻止裸 commit
        是根因治本，本方法是防御层（兜底外部绕过路径）。

        Returns:
            None=git add 成功；CommitResult(COMMIT_FAILED)=失败（重试耗尽或非 index.lock）。
        """
        max_retries = 3
        add_result = None
        for attempt in range(max_retries):
            add_result = self.run_git(
                ["git", "add", f"--pathspec-from-file={pathspec_file}"]
            )
            if add_result.returncode == 0:
                return None  # 成功
            stderr = add_result.stderr.strip()
            if "index.lock" in stderr and "File exists" in stderr and attempt < max_retries - 1:
                backoff = 2.0 * (attempt + 1)  # 2s, 4s 退避
                logger.warning(
                    "_commit_auto: git add index.lock 竞争，%.0fs 后重试 "
                    "(attempt=%d/%d, session=%s) —— #ARCH-RECONCILER-INDEXLOCK-RETRY "
                    "(暂时性竞争，commit 未执行，重试安全)",
                    backoff, attempt + 1, max_retries, session_id,
                )
                time.sleep(backoff)  # noqa: m10-time-trigger — 锁等待退避，非周期触发
                continue
            return CommitResult(
                status=CommitStatus.COMMIT_FAILED,
                message=f"git add failed (auto-commit): {stderr}",
            )
        return CommitResult(
            status=CommitStatus.COMMIT_FAILED,
            message=(
                f"git add failed (auto-commit) after {max_retries} retries"
                f" (index.lock held by external git process): "
                f"{add_result.stderr.strip() if add_result else 'unknown'}"
            ),
        )

    def _commit_auto(
        self, session_id: str, files: list[str], message: str,
    ) -> CommitResult:
        """reconciler auto-commit 唯一入口（锁 + DIRECTORY-CONTRACT gate + commit，不触发 reconciler）。阶段3 仅保留 DIRECTORY-CONTRACT gate；禁止 reconciler 裸调 git commit。"""
        # ARCH-GIT-CALL-BUDGET P2.3 (2026-07-19): batch intercept -- buffer when enabled.
        if self._batcher.is_enabled():
            return self._batcher.buffer(session_id, files, message)

        if not files:
            return CommitResult(status=CommitStatus.NOTHING_TO_COMMIT, message="empty files list")
        if not session_id:
            session_id = "unknown"

        # 治本（#ARCH-WORKTREE-002 缺陷3，2026-07-19）：检测 merge 中间态
        # 病根：auto-sync reconciler 不识别 merge 状态，手动 `git merge --no-commit` 后
        #       reconciler 检测到 staged changes 自动 _commit_auto，清理 MERGE_HEAD，
        #       导致用户手动 merge 被强制完成（HEAD 移动到 auto-sync commit）。
        # 方案：入口检测 .git/MERGE_HEAD 存在时跳过 auto-commit，保留 merge 状态
        #       供用户手动完成。实测案例（2026-07-19）：手动 git merge --no-commit --no-ff
        #       输出 "Automatic merge went well"，但随后 MERGE_HEAD 消失。
        # AI-R1-003 红队治本：worktree 感知检测（原 .git/MERGE_HEAD 硬编码在
        # linked worktree 下恒 False——.git 是指针文件，见 _is_merge_in_progress）
        if self._is_merge_in_progress():
            logger.info(
                "_commit_auto: skip auto-commit, merge in progress "
                "(session=%s, files=%d) —— #ARCH-WORKTREE-002 缺陷3 治本",
                session_id, len(files),
            )
            return CommitResult(
                status=CommitStatus.NOTHING_TO_COMMIT,
                message=(
                    "skip auto-commit: merge in progress (MERGE_HEAD exists)"
                    " —— #ARCH-WORKTREE-002 缺陷3 治本，保留 merge 状态供手动完成"
                ),
            )

        existing = self._resolve_auto_commit_files(files)
        if not existing:
            return CommitResult(
                status=CommitStatus.NOTHING_TO_COMMIT,
                message="no existing or tracked files to auto-commit",
            )

        # DIRECTORY-CONTRACT gate 校验（真源复用：gate_registry.get，不复制 DCR 逻辑）
        dcr_result = self._run_auto_commit_gate(
            "DIRECTORY-CONTRACT", existing, session_id,
            "目录契约违规（auto-commit）",
            "_commit_auto: DIRECTORY-CONTRACT gate 未注册，跳过 DCR 校验"
            "（session=%s, files=%d）——检查 __init__ 的 gate 注册",
        )
        if dcr_result is not None:
            return dcr_result

        # TTL-METADATA gate (subprocess reuse, same pattern as DCR gate)
        ttl_result = self._run_auto_commit_gate(
            "TTL-METADATA", existing, session_id,
            "ttl metadata violation (auto-commit)",
            "_commit_auto: TTL-METADATA gate 未注册，跳过 ttl 校验"
            "（session=%s, files=%d）——检查 __init__ 的 gate 注册",
        )
        if ttl_result is not None:
            return ttl_result

        # FILE-PLACEMENT-TTL gate（ARCH-049，与 TTL-METADATA 同模式覆盖 _commit_auto 路径）
        # reconciler auto-commit 传 allow_promote=True（reconciler 是受信任自动流程，exempt_subdirs 生成器输出豁免）
        fpt_result = self._run_auto_commit_gate(
            "FILE-PLACEMENT-TTL", existing, session_id,
            "file placement ttl violation (auto-commit)",
            "_commit_auto: FILE-PLACEMENT-TTL gate 未注册，跳过文件放置校验"
            "（session=%s, files=%d）——检查 __init__ 的 gate 注册",
            check_kwargs={"allow_promote": True},
        )
        if fpt_result is not None:
            return fpt_result

        gw_marker = f"[GW:{session_id}:auto]"
        full_message = f"{message}\n\n{gw_marker}"

        try:
            with _GlobalCommitLock(self.project_root):
                pathspec_file = self._write_pathspec_file(existing)
                try:
                    add_fail = self._git_add_with_index_lock_retry(
                        pathspec_file, session_id,
                    )
                    if add_fail is not None:
                        return add_fail
                    diff_result = self.run_git(["git", "diff", "--cached", "--quiet"])
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
            return CommitResult(status=CommitStatus.LOCK_TIMEOUT, message="internal error")
        except OSError as e:
            # TRAE-079 铁律6：文件锁 fail-open 降级 MUST 落审计（_commit_auto 路径同样覆盖）
            _audit_commit_lock_fallback(self.project_root, session_id, str(e))
            logger.warning(
                "TRAE-079: _GlobalCommitLock unavailable in _commit_auto (fail-open fallback): %s — "
                "auto-commit proceeding without serialization lock for session %s",
                e, session_id,
            )
            # 无锁降级：直接执行 auto-commit（不串行化，但 gate 仍在）
            pathspec_file = self._write_pathspec_file(existing)
            try:
                add_fail = self._git_add_with_index_lock_retry(
                    pathspec_file, session_id,
                )
                if add_fail is not None:
                    return add_fail
                diff_result = self.run_git(["git", "diff", "--cached", "--quiet"])
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

    def _write_pathspec_file(self, abs_files: list[str]) -> str:
        """将文件路径写入临时 pathspec 文件（:(icase) 前缀兼容 Windows 大小写不敏感）。"""
        # 治本 #ARCH-ROOT-TEMP-FILE-ENFORCEMENT-001: gw_pathspec_*.txt 同为进程 IPC token
        # （git --pathspec-from-file），归宿 OS temp dir。文件内容是 :(icase)relpath 行，
        # git 按 cwd(project_root) 解释 pathspec，与 temp 文件存放位置无关。
        fd, path = tempfile.mkstemp(
            prefix="gw_pathspec_", suffix=".txt"
        )
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            for abs_path in abs_files:
                rel = os.path.relpath(abs_path, str(self.project_root))
                rel = rel.replace("\\", "/")
                f.write(f":(icase){rel}\n")
        return path

    def _is_merge_in_progress(self) -> bool:
        """检测当前 worktree 是否处于 merge 中间态（MERGE_HEAD 存在）。

        治本（AI-R1-003 红队，2026-08-18）：原实现硬编码
        ``project_root / ".git" / "MERGE_HEAD"``——但 linked worktree 的 ``.git``
        是指针文件（内容 ``gitdir: <common>/.git/worktrees/<name>``），该路径恒不存在，
        检测在 worktree 内恒 False（worktree 盲区）。merge finalize 场景下网关误判
        非 merge → 走 pathspec partial commit → git 拒绝（"cannot do a partial
        commit during a merge"）。改用 ``git rev-parse --git-path MERGE_HEAD``
        解析真实 per-worktree git 目录（主仓与 linked worktree 均正确），
        再判文件存在性。git 命令失败（非 git 仓库）时回退旧路径判定，保持向后兼容。
        """
        result = self.run_git(["git", "rev-parse", "--git-path", "MERGE_HEAD"])
        if result.returncode == 0 and result.stdout.strip():
            git_path_merge_head = Path(result.stdout.strip())
            if not git_path_merge_head.is_absolute():
                git_path_merge_head = self.project_root / git_path_merge_head
            return git_path_merge_head.exists()
        # 回退：git 不可用时退回旧路径判定（主仓场景仍有效）
        return (self.project_root / ".git" / "MERGE_HEAD").exists()

    def _merge_in_progress_result(self) -> CommitResult:
        """B2 治本①：MERGE_HEAD 晾置拒绝响应（附处置引导与在途 merge sha 留痕）。"""
        mh = self.run_git(["git", "rev-parse", "--verify", "-q", "MERGE_HEAD"])
        mh_sha8 = mh.stdout.strip()[:8] if mh.returncode == 0 else "unknown"
        return CommitResult(
            status=CommitStatus.MERGE_IN_PROGRESS,
            message=(
                "检测到 MERGE_HEAD——存在未完成的 merge（merge --no-commit 晾置或冲突待决）。"
                "普通 commit 会把该 merge 内容连带提交并张冠李戴（AI-FILL-14 截胡事故治本）。"
                "处置：① 若是你的 merge：解决冲突后加 --merge-finalize 重新执行"
                "（全量 commit，[GW:<sid>:merge] 留痕）；"
                "② 若不是你的 merge：git merge --abort 清除后重试，或联系发起方完成。"
                f"MERGE_HEAD={mh_sha8}"
            ),
        )

    def _target_rel_set(self, files: list[str]) -> set[str]:
        """commit 目标文件 → normcase 相对路径集合（ita 清扫排除集用）。"""
        return {
            os.path.normcase(os.path.relpath(f, str(self.project_root)).replace("\\", "/"))
            for f in files
        }

    def _list_intent_to_add_paths(self) -> list[str]:
        """列出 index 中 intent-to-add 残留条目（相对路径，正斜杠）。

        B2 治本②（2026-08-19）：ita 条目对 ``git diff --cached`` 完全不可见
        （gateway staged 校验盲区），但 git merge 视其为 local changes 拒绝合并
        （09 分支两文件实证）。来源=历史 stash 周期/手动 stash pop/pre-commit
        框架 patch restore 的存量 index 残留。
        主判据：``git ls-files --debug`` flags 0x20000000 位；
        回退：``ls-files --stage`` 空 blob 签名且 HEAD 无此路径。
        """
        result = self.run_git(["git", "ls-files", "--debug"])
        if result.returncode == 0:
            ita: list[str] = []
            current: str | None = None
            for line in result.stdout.splitlines():
                if not line.startswith(" "):
                    current = line.strip()
                elif current is not None and "flags:" in line:
                    # debug 格式：flags 与 size 同行（"  size: 0\tflags: 20004000"，%x 无前缀）
                    hex_part = line.split("flags:", 1)[1].strip().split()[0]
                    try:
                        if int(hex_part, 16) & _ITA_FLAG:
                            ita.append(current)
                    except (ValueError, IndexError):
                        continue
            return ita
        # 回退：空 blob 签名（旧版 git 无 --debug 或命令失败）
        staged = self.run_git(["git", "ls-files", "--stage"])
        if staged.returncode != 0:
            return []
        ita = []
        for line in staged.stdout.splitlines():
            meta, sep, path = line.partition("\t")
            if not sep or not meta.strip():
                continue
            fields = meta.split()
            if len(fields) >= 2 and fields[1] == _EMPTY_BLOB_SHA:
                chk = self.run_git(["git", "cat-file", "-e", f"HEAD:{path.strip()}"])
                if chk.returncode != 0:
                    ita.append(path.strip())
        return ita

    def _sweep_intent_to_add_residue(self, session_id: str, exclude_rel: set[str]) -> list[str]:
        """清扫 index 中 ita 存量残留（B2 治本②）。返回被清扫的相对路径列表。

        只动 index（``git reset -q -- <paths>``），工作区内容原样保留（回 untracked）。
        MERGE_HEAD 存续期全禁——merge index 神圣，对齐 _commit_with_file_message
        "绝不能毁掉 merge 现场"。exclude_rel=本次 commit 目标（normcase 相对路径），
        防误扫目标文件。清扫事件落 .runtime/gate_audit/gateway_index_hygiene.jsonl。
        """
        if self._is_merge_in_progress():
            return []
        ita = [p for p in self._list_intent_to_add_paths() if os.path.normcase(p) not in exclude_rel]
        if not ita:
            return []
        result = self.run_git(["git", "reset", "-q", "--"] + ita)
        if result.returncode != 0:
            logger.warning(
                "GitCommitGateway: ita 残留清扫失败（不阻断）: %s", result.stderr.strip()
            )
            return []
        logger.info(
            "GitCommitGateway: 清扫 ita 残留 %d 条（merge local-changes 误报治本）: %s",
            len(ita), ita,
        )
        _audit_index_hygiene(self.project_root, session_id, "ita_sweep", {"swept": ita})
        return ita

    def _verify_post_commit_index(self, files: list[str], session_id: str) -> None:
        """B2 治本③：commit 后 index-HEAD 一致性校验（warn-only，commit 已成功不阻断）。

        a) 目标文件全部入 HEAD（staged 无残留）；
        b) ita 残留复扫（commit 过程中新产生的当场再扫一次）；
        c) merge finalize 后 MERGE_HEAD 应已消失（仍存在=异常审计）。
        异常落 .runtime/gate_audit/gateway_index_hygiene.jsonl。
        """
        anomalies: dict[str, object] = {}
        rels = [
            os.path.relpath(f, str(self.project_root)).replace("\\", "/") for f in files
        ]
        if rels:
            diff = self.run_git(["git", "diff", "--cached", "--quiet", "--"] + rels)
            if diff.returncode != 0:
                anomalies["targets_staged_residual"] = rels[:20]
        if self._list_intent_to_add_paths():
            anomalies["ita_reswept"] = self._sweep_intent_to_add_residue(session_id, set())
        if self._is_merge_in_progress():
            anomalies["merge_head_still_present"] = True
        if anomalies:
            logger.warning("GitCommitGateway: post-commit index 一致性异常: %s", anomalies)
            _audit_index_hygiene(
                self.project_root, session_id, "post_commit_consistency",
                {"anomalies": anomalies},
            )

    def run_git(self, cmd: list[str], cwd: str | None = None) -> subprocess.CompletedProcess:
        """执行 git 命令（统一 cwd + encoding）。reconciler 禁止裸调 git commit——必须走 _commit_auto()，commit 守卫 _in_commit_flow 技术强制。

        Args:
            cmd: git 命令列表（如 ``["git", "show", "HEAD:foo.py"]``）。
            cwd: 可选工作目录（默认使用 ``self.project_root``）。某些 gate 需在
                 ``git rev-parse --show-toplevel`` 返回的 worktree root 下执行。

        P2-2b 治本（#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）：
        timeout 按命令类型分级——原硬编码 120s 对所有 git 命令共用，导致
        快速读命令（rev-parse/show/status）与慢速写命令（commit/merge）共用
        上限，单个慢命令即可耗尽整个 session 预算。改为：
          - read 类（rev-parse/show/status/diff/log/ls-tree/merge-base/config）: 15s
          - write 类（commit/merge/checkout/reset/update-ref/rebase）: 60s
          - 其他默认: 30s
        """
        if (
            len(cmd) >= 2
            and cmd[0] == "git"
            and cmd[1] == "commit"
            and not getattr(self, "in_commit_flow", False)
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
        from zephyr.shared.infra.process_pool import run_subprocess_hidden

        # P2-2b 治本：timeout 按命令类型分级（原硬编码 120s）
        timeout = _classify_git_timeout(cmd)
        return run_subprocess_hidden(
            cmd,
            cwd=cwd or str(self.project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env,
        )

    def _run_git(self, cmd: list[str], cwd: str | None = None) -> subprocess.CompletedProcess:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.run_git(cmd, cwd)
