# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §ghost-commit-gateway
# [MODULE] zephyr.gov_enforcement.rule_bridge.git_commit_gateway
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.__init__; zephyr.security.access_control.session_concurrency; zephyr.gov_enforcement.rule_bridge.worktree_manager
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

from zephyr.governance.audit.reconciliation_registry import (
    ReconcileResult,
    ReconciliationRegistry,
    make_manifest_reconciler,
    make_path_tree_reconciler,
    make_path_ownership_reconciler,
    make_depgraph_ops_reconciler,
    make_blueprint_frontmatter_reconciler,  # ARCH-FRONTMATTER-STATE-001 Phase 2
    make_drift_scan_reconciler,
    make_drift_fix_reconciler,
    make_module_id_recommend_reconciler,
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
    make_arch_diagram_reconciler,
    make_constraint_detect_reconciler,
    make_gate_inventory_sync_reconciler,
    make_gate_registry_sync_reconciler,
    make_tmp_cleanup_reconciler,
    make_worktree_lifecycle_reconciler,
    make_scripts_import_integrity_reconciler,  # ARCH-TOOL-HEALTH-V1 Phase 3
    make_undefined_name_baseline_reconciler,  # GATE-DEPGRAPH-OPS 治本 Phase 1（F821 baseline 全扫）
    make_capability_lookup_health_reconciler,  # #ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD Phase 4 G6 监控欠缺
    make_stash_lifecycle_reconciler,  # #ARCH-WORKTREE-002 Phase 4 stash 过期清理
    make_blueprint_id_legacy_reconciler,  # ARCH-DATAQUALITY-V1.8 Task I
    _log_reconcile_results,  # #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 2
    _print_critical_warn_banner,  # #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 3
    _print_block_banner,  # #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 4.2
)
from zephyr.governance.audit.remediation_progress_reconciler import (  # #ARCH-GOV-CONVERGENCE-META Phase 3.1
    make_remediation_progress_reconciler,
)
from zephyr.governance.audit.runtime_violation_snapshot_reconciler import (  # #ARCH-GOV-CONVERGENCE-META Phase 3.4b
    make_runtime_violation_snapshot_reconciler,
)
from zephyr.governance.audit.git_performance_monitor_reconciler import (  # ARCH-GIT-CALL-BUDGET P3.5
    make_git_performance_monitor_reconciler,
)
from zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler import (  # ARCH-TOOL-HEALTH-V1 Phase 5b
    make_commit_gateway_abuse_monitor_reconciler,
)
from zephyr.governance.audit.error_pattern_consumer_reconciler import (  # #ARCH-PREVENTABILITY-LAYER-001 Phase 4 P4-1b
    make_error_pattern_consumer_reconciler,
)
from zephyr.governance.audit.workspace_hygiene_reconciler import (  # ARCH-TOOL-HEALTH-V1 Phase 6 + DEBT-WORKSPACE-001/002
    make_workspace_hygiene_reconciler,
)
from zephyr.gov_enforcement.rule_bridge.batched_auto_committer import BatchedAutoCommitter  # ARCH-GIT-CALL-BUDGET P2.3
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import CommitGateRegistry
from zephyr.gov_enforcement.commit_gates.held_overlap_gate import make_held_overlap_gate
from zephyr.gov_enforcement.commit_gates.foreign_change_gate import make_foreign_change_gate
from zephyr.gov_enforcement.commit_gates.session_required_gate import make_session_required_gate
from zephyr.gov_enforcement.commit_gates.claim_required_gate import make_claim_required_gate
from zephyr.gov_enforcement.commit_gates.capability_overlap_gate import make_capability_overlap_gate
from zephyr.gov_enforcement.commit_gates.create_guard import make_create_guard
from zephyr.gov_enforcement.commit_gates.directory_contract_gate import make_directory_contract_gate
from zephyr.gov_enforcement.commit_gates.ttl_gate import make_ttl_gate
from zephyr.gov_enforcement.commit_gates.encoding_gate import make_encoding_gate
from zephyr.gov_enforcement.commit_gates.file_placement_ttl_gate import make_file_placement_ttl_gate
from zephyr.gov_enforcement.commit_gates.dangling_reference_gate import make_dangling_reference_gate
from zephyr.gov_enforcement.commit_gates.arch_reference_gate import make_arch_reference_gate
from zephyr.gov_enforcement.commit_gates.ruling_reference_gate import make_ruling_reference_gate
from zephyr.gov_enforcement.commit_gates.ruling_commit_verified_gate import make_ruling_commit_verified_gate
from zephyr.gov_enforcement.commit_gates.r5_digit_suffix_gate import make_r5_digit_suffix_gate
from zephyr.gov_enforcement.commit_gates.ssot_redefinition_gate import make_ssot_redefinition_gate
from zephyr.gov_enforcement.commit_gates.unsafe_dict_spread_gate import make_unsafe_dict_spread_gate
from zephyr.gov_enforcement.commit_gates.pure_shim_gate import make_pure_shim_gate
from zephyr.gov_enforcement.commit_gates.pure_assertion_gate import make_pure_assertion_gate
from zephyr.gov_enforcement.commit_gates.noqa_validation_gate import make_noqa_validation_gate
from zephyr.gov_enforcement.commit_gates.datetime_now_forbidden_gate import make_datetime_now_forbidden_gate
from zephyr.gov_enforcement.commit_gates.vocab_hardcode_gate import make_vocab_hardcode_gate
from zephyr.gov_enforcement.commit_gates.file_copy_gate import make_file_copy_gate
from zephyr.gov_enforcement.commit_gates.id_uniqueness_gate import make_id_uniqueness_gate
from zephyr.gov_enforcement.commit_gates.exempt_zone_frontmatter_gate import make_exempt_zone_frontmatter_gate
from zephyr.gov_enforcement.commit_gates.module_id_consistency_gate import make_module_id_consistency_gate
from zephyr.gov_enforcement.commit_gates.perm_trigger_gate import make_perm_trigger_gate
from zephyr.gov_enforcement.commit_gates.snapshot_drift_gate import make_snapshot_drift_gate  # Phase 3.6 rc1
from zephyr.gov_enforcement.commit_gates.vocab_chain_gate import make_vocab_chain_gate  # Phase 3.6 rc2
from zephyr.gov_enforcement.commit_gates.manual_only_permanent_gate import make_manual_only_permanent_gate  # Phase 3.6 rc4
from zephyr.gov_enforcement.commit_gates.msg_exposure_gate import make_msg_exposure_gate
from zephyr.gov_enforcement.commit_gates.empty_handler_gate import make_empty_handler_gate
from zephyr.gov_enforcement.commit_gates.orphan_module_gate import make_orphan_module_gate
from zephyr.gov_enforcement.commit_gates.rule_execution_pairing_gate import make_rule_execution_pairing_gate  # Phase 3.5
from zephyr.gov_enforcement.commit_gates.doc_ref_broken_gate import make_doc_ref_broken_gate
from zephyr.gov_enforcement.commit_gates.function_dup_gate import make_function_dup_gate
from zephyr.gov_enforcement.commit_gates.bare_getenv_gate import make_bare_getenv_gate
from zephyr.gov_enforcement.commit_gates.msg_style_gate import make_msg_style_gate
from zephyr.gov_enforcement.commit_gates.hardcoded_url_gate import make_hardcoded_url_gate
from zephyr.gov_enforcement.commit_gates.test_source_consistency_gate import make_test_source_consistency_gate
from zephyr.gov_enforcement.commit_gates.no_import_side_effect_gate import make_no_import_side_effect_gate
from zephyr.gov_enforcement.commit_gates.depgraph_freshness_gate import make_depgraph_freshness_gate  # #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 3.1
from zephyr.gov_enforcement.commit_gates.scripts_import_integrity_gate import make_scripts_import_integrity_gate  # #ARCH-DATAQUALITY-V1.4 核心治本
from zephyr.gov_enforcement.commit_gates.reconciler_health_gate import make_reconciler_health_gate  # #ARCH-DATAQUALITY-V1.7 reconciler健康度门禁
from zephyr.gov_enforcement.commit_gates.import_direction_gate import make_import_direction_gate
from zephyr.gov_enforcement.commit_gates.panorama_alignment_gate import make_panorama_alignment_gate
from zephyr.gov_enforcement.commit_gates.long_param_list_gate import make_long_param_list_gate
from zephyr.gov_enforcement.commit_gates.bare_sql_gate import make_bare_sql_gate
from zephyr.gov_enforcement.commit_gates.depgraph_write_path_gate import make_depgraph_write_path_gate
from zephyr.gov_enforcement.commit_gates.ch_batch_size_gate import make_ch_batch_size_gate
from zephyr.gov_enforcement.commit_gates.git_call_budget_gate import make_git_call_budget_gate
from zephyr.gov_enforcement.commit_gates.bare_subprocess_gate import make_bare_subprocess_gate  # trae_067 RULE-EIGHTEEN-INV-001 P8 warn-only
from zephyr.gov_enforcement.commit_gates.undefined_name_gate import make_undefined_name_gate  # GATE-DEPGRAPH-OPS 治本 Phase 1（F821 零防护缺口）
from zephyr.gov_enforcement.commit_gates.import_integrity_gate import make_import_integrity_gate  # #ARCH-CROSS-COMMIT-ATOMICITY-001 治本——悬空 import 硬阻断
from zephyr.gov_enforcement.commit_gates.domain_name_zh_direct_access_gate import make_domain_name_zh_direct_access_gate  # Step 2.5 遗留风险修复（域名字典直接访问硬阻断 priority=72）
from zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate import make_capability_lookup_required_gate  # #ARCH-GOV-CONVERGENCE-META Phase 3.4a 病根3治本
from zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate import make_forged_gw_marker_gate  # #ARCH-PREVENTABILITY-LAYER-001 Phase 2 第 6 层可预防性——forged_gw_marker 前置阻断
from zephyr.gov_enforcement.commit_gates.ch_final_gate import make_ch_final_gate
from zephyr.gov_enforcement.commit_gates.ch_version_col_gate import make_ch_version_col_gate
from zephyr.gov_enforcement.commit_gates.god_class_gate import make_god_class_gate
from zephyr.gov_enforcement.commit_gates.high_complexity_gate import make_high_complexity_gate
from zephyr.gov_enforcement.commit_gates.rule_four_way_alignment_gate import (
    make_rule_four_way_alignment_gate,
)
from zephyr.gov_enforcement.commit_gates.tests_coverage_gate import make_tests_coverage_gate
from zephyr.gov_enforcement.commit_gates.blueprint_format_gate import make_blueprint_format_gate
from zephyr.gov_enforcement.commit_gates.data_task_completeness_gate import make_data_task_completeness_gate
from zephyr.gov_enforcement.commit_gates.capability_consistency_gate import make_capability_consistency_gate
from zephyr.gov_enforcement.commit_gates.rename_depgraph_sync_gate import make_rename_depgraph_sync_gate
from zephyr.gov_enforcement.commit_gates.new_file_depgraph_gate import make_new_file_depgraph_gate  # #ARCH-DEP-001 第三期 L1 铁律技术强制
from zephyr.gov_enforcement.commit_gates.domain_fk_gate import make_domain_fk_gate
from zephyr.gov_enforcement.commit_gates.blueprint_amodule_consistency_gate import make_blueprint_amodule_consistency_gate
from zephyr.gov_enforcement.commit_gates.consumers_accuracy_gate import make_consumers_accuracy_gate  # #ARCH-CONSUMERS-ACCURACY-001 治本——CONSUMERS 字段准确性 warn-only 检测
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
    PURE_SHIM_VIOLATION = "PURE_SHIM_VIOLATION"
    STASH_CONFLICT = "STASH_CONFLICT"  # 阶段3 已弃用，保留向后兼容


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


# P2-2b 治本（#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）：
# git 命令 timeout 分级——原硬编码 120s 对所有 git 命令共用，导致快速读命令
# （rev-parse/show/status）与慢速写命令（commit/merge）共用上限。改为按命令类型
# 分级，单个慢命令不会耗尽整个 session 预算。
_GIT_TIMEOUT_READ = 15    # rev-parse/show/status/diff/log/ls-tree/merge-base/config
_GIT_TIMEOUT_WRITE = 60   # commit/merge/checkout/reset/update-ref/rebase
_GIT_TIMEOUT_DEFAULT = 30  # 其他默认

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
        self._gate_registry.register(make_held_overlap_gate())
        self._gate_registry.register(make_forged_gw_marker_gate())  # priority=30 #ARCH-PREVENTABILITY-LAYER-001 Phase 2 第 6 层可预防性——forged_gw_marker 前置阻断（早于 SESSION-REQUIRED=31）
        self._gate_registry.register(make_foreign_change_gate())  #ARCH-054 priority=45 外来变更检测（claim 时基线快照，commit 时对比）
        self._gate_registry.register(make_session_required_gate())  # priority=31 治本 session 注册强制（防 AI 绕过 session_worktree_start 传空 session_id）
        self._gate_registry.register(make_claim_required_gate())
        self._gate_registry.register(make_capability_overlap_gate())
        self._gate_registry.register(make_directory_contract_gate())
        self._gate_registry.register(make_ttl_gate())  # priority=32 ttl gate
        self._gate_registry.register(make_file_placement_ttl_gate())  # priority=33 文件放置与TTL一致性（ARCH-049，落地 ttl_vocabulary §146-152 永久区准入机制）
        self._gate_registry.register(make_create_guard())  # priority=60 治本"造第二真源"（trae_060 §2）
        self._gate_registry.register(make_rule_execution_pairing_gate())  # priority=65 Phase 3.5 规则-执行配对（trae_*.yaml MUST 有 enforcement.paired_gate_id）
        self._gate_registry.register(make_dangling_reference_gate())  # priority=70 治本悬空引用（AGENTS.md §X.Y）
        self._gate_registry.register(make_arch_reference_gate())  # priority=75 治本 #ARCH-NNN 悬空引用（编号铁律#6 代码强制）
        self._gate_registry.register(make_ruling_reference_gate())  # priority=74 治本 裁定#NNN 悬空引用（裁定#20-B，阶段2 hard block 已启用 裁定#20-G，对标 ARCH-REFERENCE，紧跟 DANGLING-REFERENCE(70) + NOQA-VALIDATION(71) 之后）
        self._gate_registry.register(make_rule_four_way_alignment_gate())  # priority=76 治本规则四方对齐（ARCH-020 补建，subprocess 调 check_rule_four_way_alignment.py --ci）
        self._gate_registry.register(make_ruling_commit_verified_gate())  # priority=109 治本 #ARCH-WORKSPACE-DRIFT-SYSTEMIC-001 盲区4 文档"已完成"声明 commit hash 真实性硬验证（原 77 与 BLUEPRINT-FORMAT 撞号，#ARCH-GATE-PRIORITY-UNIQUENESS-001 Phase 1 迁移至 109）
        self._gate_registry.register(make_r5_digit_suffix_gate())  # priority=35 治本 R5 数字后缀目录禁止（弥补 --no-verify 绕过 pre-commit 的缺口）
        self._gate_registry.register(make_rename_depgraph_sync_gate())  # priority=39 治本文件重命名后 depgraph 未同步（AI-14 审计：a2a_protocol_security→a2a_agent_blocklist 重命名导致 13 处 docs stale 引用根因；原 36 与 CH-BATCH-SIZE 冲突，迁移到 39）
        self._gate_registry.register(make_new_file_depgraph_gate())  # priority=58 #ARCH-DEP-001 第三期 L1 铁律技术强制（新建 .py 文件 depgraph 未登记硬阻断，bootstrap 豁免 3811 现有 generated 节点）
        self._gate_registry.register(make_encoding_gate())  # priority=42 治本 --no-verify 绕过 pre-commit GATE-ENCODING（F-05 防御断层，subprocess 调 check_encoding.py 复用真源，fail-open on env error 裁定ARCH-TTL-DOC-001；40被CLAIM-REQUIRED占用，41预留给DATA-TASK迁移）
        self._gate_registry.register(make_ssot_redefinition_gate())  # priority=65 治本 SSoT 符号重复定义（ARCH-033 P2，弥补 CREATE-GUARD 只管新建文件不管文件内重定义的缺口）
        self._gate_registry.register(make_unsafe_dict_spread_gate())  # priority=66 warn 级 防复发 5.147.5/5.147.12 **data 直接展开模式（schema 演进会 TypeError，SSoT filter_dataclass_fields 已治本，gate 防新 AI 制造同类债务）
        self._gate_registry.register(make_pure_shim_gate())  # priority=68 治本 --no-verify 绕过 GATE-NO-PURE-SHIM（P6 AI-15 审计，subprocess 调 check_pure_shim.py --ci）
        self._gate_registry.register(make_pure_assertion_gate())  # priority=69 治本纯陈述原则（GOV-DOC-016，subprocess 调 check_pure_assertion.py --ci）
        self._gate_registry.register(make_noqa_validation_gate())  # priority=71 治本自定义 noqa 标记无门禁（#ARCH-NOQA-GOV-001，in-process 校验 noqa_exempt_registry.yaml SSoT）
        self._gate_registry.register(make_domain_name_zh_direct_access_gate())  # priority=72 治本 DOMAIN_NAME_ZH 字典直接访问硬阻断（Step 2.5 遗留风险修复——防止 AI 绕过 DB 优先级链直接访问硬编码域名字典）
        self._gate_registry.register(make_datetime_now_forbidden_gate())  # priority=34 治本生成器代码 datetime.now() 硬阻断（AGENTS.md §11.1.1，生成器输出幂等性强制）
        self._gate_registry.register(make_vocab_hardcode_gate())  # priority=80 治本 --no-verify 绕过 GATE-VOCAB（Phase 1 AST 门禁，subprocess 调 check_vocab_hardcode.py --files --ci）
        self._gate_registry.register(make_vocab_chain_gate())  # priority=73 #ARCH-GOV-CONVERGENCE-META Phase 3.6 rc2 治本 SSoT 路径硬编码（扩展 VOCAB-HARDCODE 覆盖至消费链）
        self._gate_registry.register(make_snapshot_drift_gate())  # priority=40 #ARCH-GOV-CONVERGENCE-META Phase 3.6 rc1 治本运行时违规快照漂移（结构+新鲜度+SHA 一致性校验）
        self._gate_registry.register(make_file_copy_gate())  # priority=85 治本文件复制检测无 commit-time 强制（Phase 1 sub-task 3，subprocess 调 check_code_duplication.py --files --ast --threshold 0.7）
        # Phase 3 reconciler->gate 收敛（2026-07-03）：3 个 B 类纯校验 reconciler 升级为 pre-commit 阻断 gate
        self._gate_registry.register(make_id_uniqueness_gate())  # priority=86 治本 same-repo 重复 pre-commit hook id（原 post-commit warn reconciler）
        self._gate_registry.register(make_exempt_zone_frontmatter_gate())  # priority=87 治本豁免区 frontmatter doc_type 误放（原 post-commit warn reconciler）
        self._gate_registry.register(make_module_id_consistency_gate())  # priority=88 治本 module_id 三声明轨道一致性 + count 派生（原 post-commit warn reconciler）
        # Phase 1 AST 门禁扩展（DM-202953，2026-07-03）：5 个新 in-process gate 治本 5 病根
        self._gate_registry.register(make_perm_trigger_gate())  # priority=82 治本永久系统时间触发模式无事件订阅（病根：永久系统触发32）
        self._gate_registry.register(make_manual_only_permanent_gate())  # priority=43 #ARCH-GOV-CONVERGENCE-META Phase 3.6 rc4 治本永久系统 manual 触发无事件订阅（与 PERM-TRIGGER 互补：PERM-TRIGGER 检测时间触发，本 gate 检测 manual 触发）
        self._gate_registry.register(make_msg_exposure_gate())  # priority=83 治本错误消息暴露敏感信息（5.99.20 防复发：raise XxxError(f"...{path/tx_id/secret}...") 阻断）
        self._gate_registry.register(make_empty_handler_gate())  # priority=84 治本空 handler 函数体仅 logger/pass/return（病根：事件订阅空壳）
        self._gate_registry.register(make_orphan_module_gate())  # priority=89 治本孤儿模块死代码无 import 引用（病根：新AI可发现性55）——原86与id_uniqueness撞号，调整至89
        self._gate_registry.register(make_doc_ref_broken_gate())  # priority=91 治本文档引用断裂 .md 相对路径不存在（病根：文档引用断裂26）——原88与module_id_consistency撞号，调整至91
        self._gate_registry.register(make_function_dup_gate())  # priority=90 治本重复函数同目录同名同 body hash（病根：SSoT真源唯一性211）
        self._gate_registry.register(make_bare_getenv_gate())  # priority=81 治本裸os.getenv读密钥绕过SecretProvider（§5.17.10防复发，AST检测SECRET_INDICATOR_PATTERNS）
        self._gate_registry.register(make_msg_style_gate())  # priority=96 治本错误消息标点/箭头风格不一致（5.99.22防复发：raise消息含->或。结尾阻断）
        self._gate_registry.register(make_import_direction_gate())  # priority=97 治本shared层向上依赖（§5.152防复发）
        self._gate_registry.register(make_hardcoded_url_gate())  # priority=98 治本硬编码localhost URL（§5.160.9防复发）
        self._gate_registry.register(make_panorama_alignment_gate())  # priority=830 domain_mismatches 阻断 + orphans/drifts warn-only（ARCH-056 升级）
        self._gate_registry.register(make_long_param_list_gate())  # priority=95 治本长参数列表>7参数（§5.150防复发，AST检测新增函数参数数）
        self._gate_registry.register(make_bare_sql_gate())  # priority=94 治本裸SQL字面量（§5.160.2防复发，diff检测SELECT/INSERT/UPDATE/DELETE）
        self._gate_registry.register(make_ch_batch_size_gate())  # priority=36 防回退CH批量写入（#ARCH-CH-004，AST检测write_result在for循环内直接调用，强制BufferedWriter中间层）
        self._gate_registry.register(make_ch_final_gate())  # priority=37 裁定 #ARCH-CH-007 B5 ch_writer.query 直接调用阻断（应改用 ch_reader.query 自动注入 FINAL）
        self._gate_registry.register(make_ch_version_col_gate())  # priority=38 裁定 #ARCH-CH-009 version列语义误用阻断（diff检测非DateTime列作version参数）
        self._gate_registry.register(make_god_class_gate())  # priority=93 治本God Class方法数>20（§5.150防复发，AST检测新增类方法数）
        self._gate_registry.register(make_high_complexity_gate())  # priority=92 治本高循环复杂度>15（§5.158防复发，AST检测McCabe复杂度）
        self._gate_registry.register(make_tests_coverage_gate())  # priority=99 治本gate测试覆盖率校验（#ARCH-057，守卫者的守卫者——[TESTS]头部声明必须兑现）
        self._gate_registry.register(make_test_source_consistency_gate())  # priority=102 治本测试-源码符号漂移（§5.178防复发，AST检测测试import的符号在源码中不存在）
        self._gate_registry.register(make_blueprint_format_gate())  # priority=77 治本[BLUEPRINT]头部module_id格式（裁定#214 Phase0防蔓延，diff检测新增/修改的[BLUEPRINT]行）
        self._gate_registry.register(make_domain_fk_gate())  # priority=78 治本[DOMAIN]头部域注册表FK校验（裁定#ARCH-DRIFT-PREVENTION-001 ADP-1，diff检测[DOMAIN]值在functional_domain_registry.yaml中存在）
        self._gate_registry.register(make_blueprint_amodule_consistency_gate())  # priority=79 治本[A_module]格式一致性（裁定#ARCH-DRIFT-PREVENTION-001 ADP-3，diff检测层码后下划线+小写malformation）
        self._gate_registry.register(make_data_task_completeness_gate())  # priority=41 warn级 数据任务完整性（数据韧性三层机制§4，检测新增任务是否配置fallback_sources；原78与GATE-DOMAIN-FK冲突，迁移到41，裁定#ARCH-DRIFT-PREVENTION-001）
        self._gate_registry.register(make_depgraph_write_path_gate())  # priority=100 治本depgraph写入路径白名单（裁定#ARCH-DEPGRAPH_ACCESS_CONTROL，diff检测非白名单文件中的writable-params调用）
        self._gate_registry.register(make_capability_consistency_gate())  # priority=101 治本Provider路由-meta一致性（裁定#ARCH-CH-022 Phase 4.4，AST检测staged *_provider.py的路由能力集vs meta.capabilities声明集不一致）
        self._gate_registry.register(make_no_import_side_effect_gate())  # priority=103 治本模块导入零副作用（S4-C 2026-07-17，AST检测staged src/ .py added行的模块级I/O/网络/subprocess/DB调用+急切单例实例化，对标S4-A的telemetry.py/rollback/__init__.py修复防回归）
        self._gate_registry.register(make_depgraph_freshness_gate())  # priority=67 治本depgraph新鲜度dual-threshold（#ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 3.1，>30min WARNING/>24h 阻断，读取.runtime/depgraph_scan_cache.json _meta.saved_at）
        self._gate_registry.register(make_reconciler_health_gate())  # priority=64 治本reconciler健康度dual-level（#ARCH-DATAQUALITY-V1.7，block_next硬阻断/critical_warn警告，复用_check_recent_blocks/_check_recent_critical_warns，统一GitCommitGateway和session_worktree_commit两条路径的reconciler健康检查）
        self._gate_registry.register(make_scripts_import_integrity_gate())  # priority=104 治本_shared.constants符号导入完整性（#ARCH-DATAQUALITY-V1.4核心治本，AST检测staged _shared/constants.py added行的from-import symbols在src/zephyr/shared/io/paths.py中存在，防止符号漂移）
        self._gate_registry.register(make_git_call_budget_gate())  # priority=105 warn-only 治本 git 子进程循环调用反模式（§ARCH-GIT-CALL-BUDGET P2.2，AST检测subprocess.run(["git",...])在for/while内，warn-only P3升级block）
        self._gate_registry.register(make_bare_subprocess_gate())  # priority=108 warn-only 治本裸 subprocess.run/Popen 闪窗反模式（trae_067 RULE-EIGHTEEN-INV-001 P8，AST检测added行裸subprocess调用，warn-only P2升级block）
        self._gate_registry.register(make_undefined_name_gate())  # priority=106 治本F821未定义符号零防护（GATE-DEPGRAPH-OPS 治本 Phase 1，AI提交路径--no-verify绕过外部pre-commit，in-process stdlib AST硬阻断）
        self._gate_registry.register(make_import_integrity_gate())  # priority=107 治本悬空import硬阻断（#ARCH-CROSS-COMMIT-ATOMICITY-001，检测staged文件中import的目标模块在staged+main HEAD可解析，防ba40fa5b75同型违规）
        self._gate_registry.register(make_capability_lookup_required_gate())  # priority=110 #ARCH-GOV-CONVERGENCE-META Phase 3.4a 病根3治本（强制 AI 施工前调 rule_discovery/capability_lookup，audit log 在 .runtime/lookup_audit/<session_id>.jsonl）
        self._gate_registry.register(make_consumers_accuracy_gate())  # priority=116 warn-only 治本 [CONSUMERS] 字段准确性（#ARCH-CONSUMERS-ACCURACY-001，检测 orphan+phantom 违规，passed=True + detail 不阻断 commit；原 113 与 depgraph_pre_registration 冲突，迁移至 116）
        self._in_commit_flow = False  # commit 守卫（红攻1治本）
        self._worktree_mgr = None  # 延迟初始化（避免未启用 worktree 时的开销）
        #ARCH-054: claim 时捕获文件基线快照（git diff HEAD -- <file>），
        # commit 时 FOREIGN-CHANGE-DETECTION gate 对比检测搭便车变更。
        # S3-C 治本（2026-07-17）：快照持久化到 .runtime/claim_snapshots/，
        # 进程崩溃后重启可恢复快照（原纯内存 dict 崩溃即丢失，gate 降级为 PASS）。
        self._claim_snapshots: dict[str, dict[str, str]] = {}
        self._claim_snapshots_dir: Path = self.project_root / _CLAIM_SNAPSHOTS_DIR
        self._load_claim_snapshots_from_disk()

    def _get_worktree_manager(self):
        """延迟获取 WorktreeManager 单例。"""
        if self._worktree_mgr is None:
            from zephyr.gov_enforcement.rule_bridge.worktree_manager import WorktreeManager
            self._worktree_mgr = WorktreeManager(self.project_root)
        return self._worktree_mgr

    def _warn_non_worktree_commit(self, session_id: str, wt_session: str | None) -> None:
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
            other_active = [
                s for s in self._registry.list_active()
                if s.session_id != session_id
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

    def claim_files(self, session_id: str, files: list[str]) -> list[str]:
        """为 session 声明持有本次 commit 的文件。claim 失败的文件从返回列表排除。

        ARCH-054: claim 成功后捕获文件基线快照（git diff HEAD -- <file>），
        供 FOREIGN-CHANGE-DETECTION gate 在 commit 时检测搭便车变更。
        """
        claimed: list[str] = []
        for f in files:
            if self._registry.claim_file(session_id, f):
                claimed.append(f)
                #ARCH-054: 捕获基线快照（claim 时文件的 git diff HEAD 状态）
                try:
                    abs_f = os.path.abspath(f)
                    baseline = self._capture_baseline_diff(abs_f)
                    self._claim_snapshots.setdefault(session_id, {})[abs_f] = baseline
                    # S3-C: 持久化到磁盘（进程崩溃后可恢复）
                    self._save_session_snapshot(session_id)
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
            if not self._registry.release_file(session_id, f):
                logger.debug(
                    "GitCommitGateway: release_files no-op — file=%s not held by session=%s",
                    f, session_id,
                )
        #ARCH-054: 清理 session 的基线快照（内存 + 磁盘，S3-C 治本）
        try:
            self._claim_snapshots.pop(session_id, None)
            self._delete_session_snapshot(session_id)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            pass

    def _capture_baseline_diff(self, abs_file: str) -> str:
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
        result = self._run_git(["git", "diff", "HEAD", "--", rel])
        if result.returncode != 0:
            return ""
        return result.stdout or ""

    # ------------------------------------------------------------------
    # S3-C 治本（2026-07-17）：claim 快照磁盘持久化
    # ------------------------------------------------------------------
    # 病根：_claim_snapshots 原为纯内存 dict，进程崩溃/重启后快照丢失，
    # FOREIGN-CHANGE-DETECTION gate 降级为 PASS（无快照=不阻断），搭便车
    # 变更检测失效。持久化到 .runtime/claim_snapshots/{session_id}.json
    # 后，新 gateway 实例 __init__ 时从磁盘恢复，gate 可正常对比基线。
    # 磁盘 I/O 异常不阻断主流程（内存 dict 仍为 primary，磁盘是 backup）。

    def _load_claim_snapshots_from_disk(self) -> None:
        """__init__ 时从磁盘恢复所有 session 的 claim 快照。

        遍历 ``.runtime/claim_snapshots/*.json``，加载到 ``self._claim_snapshots``。
        损坏文件跳过（log warning），不抛异常。
        """
        try:
            if not self._claim_snapshots_dir.is_dir():
                return
            for snap_file in self._claim_snapshots_dir.glob("*.json"):
                try:
                    data = json.loads(snap_file.read_text(encoding="utf-8"))
                    sid = data.get("session_id", snap_file.stem)
                    snapshots = data.get("snapshots", {})
                    if isinstance(snapshots, dict):
                        self._claim_snapshots[sid] = snapshots
                except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                    logger.warning(
                        "GitCommitGateway: claim snapshot file corrupt, skipped — %s",
                        snap_file, exc_info=True,
                    )
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning(
                "GitCommitGateway: _load_claim_snapshots_from_disk failed", exc_info=True,
            )

    def _save_session_snapshot(self, session_id: str) -> None:
        """将单个 session 的快照持久化到 ``{session_id}.json``（原子写入）。

        内存 dict 为 primary，磁盘为 backup——写入失败仅 log warning 不阻断。
        """
        snapshots = self._claim_snapshots.get(session_id)
        if snapshots is None:
            return
        try:
            self._claim_snapshots_dir.mkdir(parents=True, exist_ok=True)
            payload = json.dumps(
                {"session_id": session_id, "snapshots": snapshots},
                ensure_ascii=False,
            )
            # 原子写入：tmp + os.replace（对标 SessionRegistry._save）
            snap_path = self._claim_snapshots_dir / f"{session_id}.json"
            tmp_path = snap_path.with_suffix(".json.tmp")
            tmp_path.write_text(payload, encoding="utf-8")
            os.replace(tmp_path, snap_path)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning(
                "GitCommitGateway: _save_session_snapshot failed — session=%s",
                session_id, exc_info=True,
            )

    def _delete_session_snapshot(self, session_id: str) -> None:
        """删除 session 的磁盘快照文件（release_files 时调用）。

        文件不存在或删除失败均静默（磁盘残留无害，下次 claim 会覆盖）。
        """
        try:
            snap_path = self._claim_snapshots_dir / f"{session_id}.json"
            snap_path.unlink(missing_ok=True)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.debug(
                "GitCommitGateway: _delete_session_snapshot failed — session=%s",
                session_id, exc_info=True,
            )

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
        self._reconciliation_registry.register(make_tmp_cleanup_reconciler(self))  # tmp/ TTL 自动清理（priority=49，对标 make_runtime_cleanup_reconciler，治本 249+ 文件残留）
        self._reconciliation_registry.register(make_worktree_lifecycle_reconciler(self))  # worktree 残留事件驱动清理（P2，治本遗留项#2，2026-07-17，priority=800）
        self._reconciliation_registry.register(make_stash_lifecycle_reconciler(self))  # #ARCH-WORKTREE-002 Phase 4 stash 过期清理（priority=801，清理 >24h 的 session_worktree 临时 stash）
        self._reconciliation_registry.register(make_scripts_import_integrity_reconciler(self))  # ARCH-TOOL-HEALTH-V1 Phase 3 scripts import baseline 全扫（priority=210，post-commit 补强 pre-commit gate 只扫 staged 的盲区）
        self._reconciliation_registry.register(make_undefined_name_baseline_reconciler(self))  # GATE-DEPGRAPH-OPS 治本 Phase 1 undefined-name baseline 全扫（priority=211，post-commit 补强 UNDEFINED-NAME gate 只扫 staged + --no-verify 绕过盲区）
        self._reconciliation_registry.register(make_capability_lookup_health_reconciler(self))  # #ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD Phase 4 G6 监控欠缺（priority=220，post-commit 检测 [no-lookup:] bypass 频率 + audit log 健康）
        self._reconciliation_registry.register(make_blueprint_id_legacy_reconciler(self))  # ARCH-DATAQUALITY-V1.8 Task I blueprint_id legacy baseline 全扫（priority=145，post-commit warn-only，检测存量 119 条 invalid [BLUEPRINT] 头部，落盘报告供追踪，与 BLUEPRINT-FORMAT gate 互补——gate 防蔓延，reconciler 清存量）
        self._reconciliation_registry.register(make_remediation_progress_reconciler(self))  # #ARCH-GOV-CONVERGENCE-META Phase 3.1 治本进度新鲜度（priority=900，>90天未更新 block_next）
        self._reconciliation_registry.register(make_runtime_violation_snapshot_reconciler(self))  # #ARCH-GOV-CONVERGENCE-META Phase 3.4b trae_060 §5 evidence 运行时快照（priority=850，post-commit 事件触发）
        self._reconciliation_registry.register(make_git_performance_monitor_reconciler(self))  # ARCH-GIT-CALL-BUDGET P3.5 git status 计时持续监控 + stale worktree 累积预警 + 退化趋势检测（priority=870，post-commit 事件触发，warn-only）
        self._reconciliation_registry.register(make_commit_gateway_abuse_monitor_reconciler(self))  # ARCH-TOOL-HEALTH-V1 Phase 5b commit gateway 持续滥用监控（priority=875，post-commit 事件触发，五维滥用检测 warn-only，补强 POST-COMMIT-GUARD 1h 短窗口盲区）
        self._reconciliation_registry.register(make_error_pattern_consumer_reconciler(self))  # #ARCH-PREVENTABILITY-LAYER-001 Phase 4 P4-1b AI behavior telemetry JSONL 错误事件聚合 consumer（priority=880，post-commit 事件触发，聚合到 .runtime/ai_error_patterns/aggregated_patterns.json）
        self._reconciliation_registry.register(make_workspace_hygiene_reconciler(self))  # ARCH-TOOL-HEALTH-V1 Phase 6 + DEBT-WORKSPACE-001/002 工作区卫生自动清理（priority=890，post-commit auto-sync 产物 git restore 还原）
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
                if self._is_git_tracked(rel) or self._is_staged_delete(rel):
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
                if gr.gate_id == "FOREIGN-CHANGE-DETECTION":  #ARCH-054
                    return CommitResult(status=CommitStatus.FOREIGN_CHANGE_VIOLATION, message=gr.detail)
                if gr.gate_id == "FILE-PLACEMENT-TTL" and gr.detail.startswith("PROMOTION_BLOCKED"):
                    return CommitResult(status=CommitStatus.PROMOTION_BLOCKED, message=gr.detail)
                return CommitResult(
                    status=CommitStatus.COMMIT_FAILED,
                    message=f"门禁 {gr.gate_id} 阻断: {gr.detail}",
                )
        return None

    def _check_ssot_canonical(self, abs_files: list[str]) -> tuple[bool, str]:
        """L2 兜底门禁：检测新增 .py 文件是否声明已有 module_path（SSoT 冲突）。

        L1 scaffold 是主防线，本方法是 L2 兜底——防止 AI 绕过 scaffold 直接 Write
        新文件后 commit。检测范围仅限 ``src/zephyr/`` 下未 git-tracked 的 .py 文件。

        策略：
          - 只检查 src/zephyr/ 下的 .py 文件（其他路径/扩展名跳过）
          - 跳过已 git-tracked 文件（视为修改而非新增）
          - 解析 [MODULE] 头，反查 find_files_by_module_path
          - 命中已有文件 = SSoT 冲突 = 阻断
          - capability_lookup 不可用时 fail-open（L1 是主防线，L2 是兜底）
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
            if self._is_git_tracked(rel):
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
                header = lookup._parse_header(Path(abs_path), rel_path)
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

    def _run_post_commit_reconcile(
        self, existing: list[str], session_id: str, result: CommitResult,
        commit_message: str = "",
    ) -> None:
        """Post-commit reconciler 调度器（Ruling:100PCT-AI-GOVERNANCE P2-3 异步化）。

        #ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD Phase 3.4 断点4/5 治本：
        新增 commit_message 参数——传递给 reconcile_for 和 _log_reconcile_results，
        使 post-commit 审计链可追溯 [no-lookup:reason] / ZEPHYR_BYPASS_LOOKUP 逃生通道使用。
        原断点4: commit() 不传 message 给 _run_post_commit_reconcile；
        原断点5: _run_post_commit_reconcile 不传 commit_message 给 reconcile_for。

        P2-3 治本（2026-07-19）：默认异步 spawn detached worker subprocess，避免 30+ 个
        reconciler 同步执行超时被 AI 工具强制终止（误判为 commit 失败）。env
        ``ZEPHYR_RECONCILE_SYNC=1`` 强制同步模式（测试用）。
        """
        if result.status is not CommitStatus.OK:
            return
        # 治本(2026-07-19): 非 Zephyr 项目（tmp_path 测试仓库等）skip post-commit reconciler
        # 原因：reconciler 依赖 Zephyr 项目结构（scripts/governance/、AGENTS.md 等），
        # 在 tmp_path 测试仓库中运行会导致 S4 frontmatter 注入污染测试文件 + 脚本缺失 warning 刷屏。
        # 对标 commit gates 的非 Zephyr skip 逻辑。
        _governance_dir = self.project_root / "scripts" / "governance" / "d1_structure"
        if not _governance_dir.is_dir():
            return

        # P2-3 分发：默认 async，ZEPHYR_RECONCILE_SYNC=1 强制 sync（测试）
        if os.environ.get("ZEPHYR_RECONCILE_SYNC", "") == "1":
            self._run_post_commit_reconcile_sync(
                existing, session_id, commit_message, result=result,
            )
        else:
            self._run_post_commit_reconcile_async(
                existing, session_id, result.commit_hash, commit_message,
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
            if result is not None:
                result.reconcile = reconcile_results
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

    def _run_post_commit_reconcile_async(
        self, existing: list[str], session_id: str, commit_sha: str,
        commit_message: str = "",
    ) -> None:
        """异步 spawn detached worker subprocess（P2-3 治本）。

        - commit_sha 缺失 → 回退 sync（兼容 edge case）
        - launch 失败 → 回退 sync（fail-open，reconciler 仍需执行）
        - launch 成功 → 立即返回，worker 在后台执行

        Args:
            existing: 已 commit 的文件绝对路径列表。
            session_id: commit session_id。
            commit_sha: 本次 commit 的 SHA（worker 用作 status file key）。
            commit_message: commit message（审计追溯用）。
        """
        if not commit_sha:
            logger.warning(
                "GitCommitGateway: async reconcile fallback to sync (no commit_sha, session=%s)",
                session_id,
            )
            self._run_post_commit_reconcile_sync(
                existing, session_id, commit_message, result=None,
            )
            return
        try:
            from zephyr.governance.audit.reconcile_runner import launch_reconcile_async
            launch_result = launch_reconcile_async(
                self.project_root, commit_sha, session_id, existing, commit_message,
            )
            if launch_result["ok"]:
                logger.info(
                    "GitCommitGateway: post-commit reconcile async launched "
                    "(session=%s, sha=%s, pid=%s)",
                    session_id, commit_sha, launch_result.get("worker_pid", 0),
                )
            else:
                # launch 失败 → 回退 sync（reconciler 仍需执行，只是退化为同步阻塞）
                logger.warning(
                    "GitCommitGateway: async launch failed, fallback to sync: %s",
                    launch_result.get("error", ""),
                )
                self._run_post_commit_reconcile_sync(
                    existing, session_id, commit_message, result=None,
                )
        except Exception as e:  # noqa: BLE001 — async 启动失败 fail-open 回退 sync
            logger.warning(
                "GitCommitGateway: async reconcile launch failed, fallback to sync: %s",
                e, exc_info=True,
            )
            self._run_post_commit_reconcile_sync(
                existing, session_id, commit_message, result=None,
            )

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

        # pre-commit 门禁注册表（架构债务 #AD-001 治本：5 个 in-process gate 替代 12 个硬编码 _check_*）
        # 新增门禁 MUST 走 CommitGateRegistry 注册制（commit_gates/ 下 make_xxx_gate() + __init__ register）
        # commit_message 透传：CAPABILITY-LOOKUP-REQUIRED gate 据此检测 [no-lookup:reason] 逃生标记
        # （#ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD-S1 止血修复：与 session_worktree._run_pre_commit_gates L1174 对称）
        gate_results = self._gate_registry.check_all(
            self, existing, session_id=session_id, allow_overlap=allow_overlap,
            allow_promote=allow_promote, commit_message=message,
        )
        blocked = self._check_gate_results(gate_results)
        if blocked is not None:
            return blocked

        gw_marker = _GW_MARKER_FMT.format(session_id=session_id)
        full_message = f"{message}\n\n{gw_marker}"
        if allow_overlap:
            full_message += f"\n[GW:{session_id}:overlap]"

        try:
            with _GlobalCommitLock(self.project_root):
                result = self._commit_locked(session_id, existing, full_message, gw_marker)
        except GatewayError as e:
            return CommitResult(status=CommitStatus.LOCK_TIMEOUT, message="internal error")

        self._run_post_commit_reconcile(existing, session_id, result, commit_message=message)
        return result

    def _is_git_tracked(self, rel_path: str) -> bool:
        """检查相对路径是否被 git 跟踪（:(icase) pathspec 兼容 Windows 大小写不敏感）。"""
        from zephyr.shared.infra.process_pool import run_subprocess_hidden

        chk = run_subprocess_hidden(
            ["git", "ls-files", "--error-unmatch", "--", f":(icase){rel_path}"],
            capture_output=True,
            cwd=str(self.project_root),
        )
        return chk.returncode == 0

    def _is_staged_delete(self, rel_path: str) -> bool:
        """检查相对路径是否为 staged delete（不在 index 但仍在 HEAD）。必需：_is_git_tracked 对 staged delete 返回 False，凡保留/排除 staged delete 场景必须用本方法补充。"""
        if self._is_git_tracked(rel_path):
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
            chk = self._run_git(["git", "check-ignore", "--no-index", "--"] + batch)
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
            r = self._run_git(git_args + [f"--pathspec-from-file={pathspec}"])
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
            del_tracked = [f for f, rel in zip(deleted, del_rels) if self._is_git_tracked(rel)]
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
                if self._is_git_tracked(rel) and not self._is_staged_delete(rel)
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
                    add_result = self._run_git(
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
        diff_result = self._run_git(["git", "diff", "--cached", "--quiet"])
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
                if self._is_git_tracked(rel):
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
        merge_head = self.project_root / ".git" / "MERGE_HEAD"
        if merge_head.exists():
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
            return CommitResult(status=CommitStatus.LOCK_TIMEOUT, message="internal error")

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

    def _run_git(self, cmd: list[str], cwd: str | None = None) -> subprocess.CompletedProcess:
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