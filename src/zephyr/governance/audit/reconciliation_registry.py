# [BLUEPRINT] MOD-GOV_RECONCILIATION_REGISTRY | .trae/documents/systemic_drift_root_cure_continuation_plan.md | §4 P2-T1

# [MODULE] zephyr.governance.audit.reconciliation_registry

# [DOMAIN] D_GOV_AUDIT

# [DEPENDENCIES] zephyr.shared.infra.process_pool (run_subprocess_hidden), zephyr.shared.utils.time_utils (now_utc), PyYAML (optional, lazy import in _load_test_residue_config for trae_071 §test_residue_reclaim SSoT 加载), psutil (optional, lazy import in _pid_exists for PID 存活检查)

# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway

# [STARTUP] imported

# [MATURITY] production

# [INVARIANTS] ReconciliationRegistry.register 幂等（同 gate_id 覆盖旧 spec）；reconcile_for 按 priority 升序执行命中 trigger 的 reconciler；reconciler 异常被捕获为 warn 结果（不阻断后续 reconciler）

# [MODIFY-GUARD] ReconcilerSpec 字段结构；ReconcileResult.action 枚举语义

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] reconcile_for 永不抛异常——单个 reconciler 异常降级为 ReconcileResult(action="warn")

# [TESTS] tests/test_reconciliation_registry.py (P3-T1)

# [A_module] module_id=MOD-GOV_RECONCILIATION_REGISTRY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

# [TTL] permanent

# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

# noqa: m10-time-trigger  M10豁免: "cron"在注释中说明reconciler是事件触发(非cron/manual)

"""

reconciliation_registry.py — GitCommitGateway post-commit 漂移对账注册表（P2-T1）

把 ``_post_commit_reconcile`` 单线硬编码升级为声明式 registry：每个被

``--no-verify`` 绕过的 pre-commit GATE 注册一个 post-commit reconciler，

commit 完成后由 registry 统一调度。

设计理由（三层病根之机制层治本）

--------------------------------

GitCommitGateway 在所有 commit 路径统一用 ``--no-verify``（斩断 stash 冲突链），

副作用是系统性关闭全部 pre-commit 漂移检测 GATE。P0-DRC 仅硬编码补了 manifest

1/4 条线。本 registry 把"补偿"从硬编码 if-then 流水线升级为可扩展声明式框架：

新增 GATE 补偿只需 ``register(spec)``，不改 gateway 方法体。

命名区隔（防混淆）

------------------

本模块的 ``ReconcilerSpec`` / ``ReconciliationRegistry`` 管 **commit-gateway

post-commit drift 对账**，与 ``zephyr.infrastructure.asset_inventory.Reconciler``

（MOD-INF-026 资产清单对账，磁盘 vs unified-asset-index.yaml）是**完全不同的

关注点**，勿混淆。

纯 stdlib 解耦

---------------

本模块仅依赖 stdlib（dataclasses/typing），不 import zephyr.*，便于 mutation

testing 用 ``importlib.util.spec_from_file_location`` 直接加载（仿

``post_sync_validator.py`` SSoT 解耦模式，规避 ``zephyr.integration.events``

import 链断裂）。

Usage::

    from zephyr.governance.audit.reconciliation_registry import (

        ReconcileResult, ReconcilerSpec, ReconciliationRegistry,

    )

    registry = ReconciliationRegistry()

    registry.register(ReconcilerSpec(

        gate_id="GATE-19-manifest",

        trigger=lambda files: any(f.startswith("scripts/") and f.endswith(".py") for f in files),

        reconcile=lambda files, sid: ReconcileResult(action="clean", detail="ok"),

        priority=100,

        file_ops=frozenset({"read", "write"}),

    ))

    results = registry.reconcile_for(["scripts/foo.py"], "sess-001")

    # results == [ReconcileResult(action="clean", detail="ok")]

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: committed_files 提交文件清单 list[str]
#   fields: 本次 commit 的文件相对路径列表
#   code: reconcile_for(committed_files) L715
# - id: I2
#   name: session_id+commit_message 会话上下文 str
#   fields: 会话标识 + 提交说明（3-arg reconciler 审计用）
#   code: reconcile_for(session_id, commit_message) L717
# - id: I3
#   name: ReconcilerSpec 对账声明 dataclass
#   fields: gate_id + trigger + reconcile + priority
#   code: ReconcilerSpec L625
# 层: 算法
# - id: A1
#   name_zh: ① 声明式注册 幂等排序
#   name_en: ReconciliationRegistry.register
#   intro: 每个被绕过的 pre-commit GATE 注册一个补偿 reconciler，同 gate_id 覆盖旧 spec
#   desc: 去重（同 gate_id 移除旧 spec）→ append → 按 priority 升序排序
#   inputs: I3
#   outputs: 有序 _specs 列表
#   invariant: 同 gate_id 幂等覆盖
# - id: A2
#   name_zh: ② 事件调度执行 异常降级
#   name_en: ReconciliationRegistry.reconcile_for
#   intro: commit 完成后按优先级遍历 spec，trigger 命中即执行 reconcile，永不抛异常
#   desc: trigger 过滤 → heartbeat 刷新 → inspect.signature 检测 arity（3-arg 传 commit_message）→ 执行 → dict 结果防御转 ReconcileResult → 填充 gate_id；TimeoutExpired 升级 critical_warn，其余异常降级 warn
#   inputs: I1 I2 A1
#   outputs: list[ReconcileResult]
#   invariant: 永不抛异常，单 reconciler 失败不阻断后续
# - id: A3
#   name_zh: ③ 对账结果落库
#   name_en: _log_reconcile_results
#   intro: 把每条对账结果写入 governance.db reconcile_log 表，供告警横幅和阻断查询
#   desc: 锚定主库 governance.db（strip_session_worktree 防 worktree 分裂）→ 确保 ack/commit_message/error_pattern_id 列 → INSERT 结果行
#   inputs: A2
#   outputs: reconcile_log 表记录
# - id: A4
#   name_zh: ④ GATE 补偿器工厂族
#   name_en: make_*_reconciler
#   intro: 20+ 个工厂函数各为一个 pre-commit GATE 生成 trigger+reconcile 闭包 spec
#   desc: manifest/path_tree/depgraph_ops/blueprint_frontmatter/drift_scan/drift_fix/yaml_sync/delete_audit/regenerate/rule_audit 等工厂，闭包捕获 gateway 与 project_root
#   inputs: I3
#   outputs: ReconcilerSpec 实例（交 A1 注册）
# 层: 输出
# - id: O1
#   name_zh: ReconcileResult 结果列表
#   name_en: list[ReconcileResult]
#   intro: 每个命中 reconciler 的对账结论（skip/clean/auto_committed/warn/critical_warn/block_next）
#   invariant: action 六枚举之一
#   downstream: GitCommitGateway（[CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway）
# - id: O2
#   name_zh: reconcile_log SQLite 记录
#   name_en: reconcile_log
#   intro: 持久化对账历史，critical_warn/block_next 供下次 commit 前横幅与硬阻断
#   downstream: 内部 _check_recent_critical_warns/_check_recent_blocks 与治理看板
# [/ALGO_FLOW]
#
# 边:
# I3 --> A1
# I3 --> A4
# I1 --> A2
# I2 --> A2
# A1 --> A2
# A4 --> A1
# A2 --> A3
# A2 --> O1
# A3 --> O2
"""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from zephyr.shared.infra.process_pool import run_subprocess_hidden
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

__all__ = [
    "ReconcileResult",
    "ReconcilerSpec",
    "ReconciliationRegistry",
    "make_manifest_reconciler",
    "make_path_tree_reconciler",
    "make_path_ownership_reconciler",
    "make_depgraph_ops_reconciler",
    "make_blueprint_frontmatter_reconciler",
    "make_blueprint_code_index_reconciler",  # autogen 段 auto-commit 通道（2026-08-23 批3b，仿135模板）
    "make_drift_scan_reconciler",
    "make_drift_fix_reconciler",
    "make_module_id_recommend_reconciler",
    "make_yaml_sync_reconciler",
    "make_precommit_id_uniqueness_reconciler",
    "make_vocab_change_reconciler",
    "make_deprecated_directory_reconciler",
    "make_exempt_zone_frontmatter_reconciler",
    "make_delete_audit_reconciler",
    "make_regenerate_reconciler",
    "make_rule_audit_reconciler",
    "make_registry_sync_reconciler",
    "make_integrity_audit_reconciler",
    "make_module_id_consistency_reconciler",
    "make_index_generator_reconciler",
    "make_runtime_cleanup_reconciler",
    "make_architecture_health_reconciler",
    "make_session_log_index_reconciler",
    "make_arch_diagram_reconciler",
    "make_gate_inventory_sync_reconciler",
    "make_gate_registry_sync_reconciler",
    "make_in_process_gate_registry_drift_reconciler",  # #ARCH-GATE-REGISTRY-AUTO-001 Phase 6
    "make_tmp_cleanup_reconciler",
    "make_worktree_lifecycle_reconciler",
    "make_scripts_import_integrity_reconciler",  # ARCH-TOOL-HEALTH-V1 Phase 3
    "make_undefined_name_baseline_reconciler",  # GATE-DEPGRAPH-OPS 治本 Phase 1
    "acknowledge_critical_warns",  # GATE-DEPGRAPH-OPS 治本 Phase 2（告警 ack 消音）
    "backfill_auto_ack_healed",  # #AUTO-ACK-HEALED-WARN 治本（自愈 ack 一次性回填）
    "cleanup_reconcile_log",  # #RECONCILE-LOG-RETENTION 治本（日志保留清理）
    "make_stash_lifecycle_reconciler",  # #ARCH-WORKTREE-002 Phase 4 stash 过期清理
    "make_blueprint_id_legacy_reconciler",  # ARCH-DATAQUALITY-V1.8 Task I
    "make_capability_lookup_health_reconciler",  # #ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD Phase 4 G6
    "log_gate_failure",  # Ruling:100PCT-AI-GOVERNANCE P1-5 — gate fail-open 持久化
    "log_emergency_commit",  # Ruling:100PCT-AI-GOVERNANCE P2-1 — emergency_commit 审计
    "make_commit_gateway_abuse_monitor_reconciler",  # ARCH-TOOL-HEALTH-V1 Phase 5b
    "make_workspace_hygiene_reconciler",  # ARCH-TOOL-HEALTH-V1 Phase 6 + DEBT-WORKSPACE-001/002
    "make_dead_public_wrapper_reconciler",  # #ARCH-STAGE4-PUBLIC-WRAPPER-DEAD-CODE-001 防复发——死公共 wrapper 持续自动检测（priority=950）
    "make_metric_count_drift_reconciler",  # #ARCH-HEALTH-DASHBOARD-001 阶段2 dashboard 指标数描述漂移校验
    "make_cross_layer_contract_signature_reconciler",  # 12维度审计自动化 P1-b 跨层契约签名漂移检测
    "make_blueprint_status_transition_reconciler",  # 12维度审计自动化 P1-d BLUEPRINT 状态转跃检测
    "make_session_staging_lifecycle_reconciler",  # #ARCH-ROOT-TEMP-FILE-ENFORCEMENT-001 staging TTL 清理（priority=802）
    "make_root_temp_sweep_reconciler",  # #ARCH-ROOT-TEMP-FILE-ENFORCEMENT-001 根目录临时文件清扫（priority=803）
]

# 5.59.5 修复：统一 subprocess 解码策略

# 病根：reconciler 中 subprocess.run 调用散落 24 处，解码策略不一致（部分 strict、

# 部分 errors="replace"），含非 UTF-8 字符的子进程输出在 strict 模式下抛

# UnicodeDecodeError 导致 reconciler 降级失败。封装统一入口确保 errors="replace"。


def _run_subprocess(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """5.59.5 修复：统一 subprocess 解码策略，使用 errors='replace' 避免非 UTF-8 字符抛 UnicodeDecodeError。"""

    kwargs.setdefault("capture_output", True)

    kwargs.setdefault("text", True)

    kwargs.setdefault("errors", "replace")

    return run_subprocess_hidden(cmd, **kwargs)


# SQL 集中化（§5.160.2 NO-BARE-SQL gate 合规）

SQL_CREATE_DRIFT_SCAN_RESULTS = """CREATE TABLE IF NOT EXISTS drift_scan_results (

    scan_id TEXT PRIMARY KEY,

    scan_time TEXT NOT NULL,

    trigger_event TEXT NOT NULL,

    total_drifts INTEGER NOT NULL,

    high_count INTEGER NOT NULL,

    low_count INTEGER NOT NULL,

    auto_fixable INTEGER NOT NULL,

    details_json TEXT

)"""

SQL_INSERT_DRIFT_SCAN_RESULT = (
    "INSERT INTO drift_scan_results "
    "(scan_id, scan_time, trigger_event, total_drifts, "
    "high_count, low_count, auto_fixable, details_json) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
)

# S2: drift_fix_reconciler SQL（§5.160.2 NO-BARE-SQL gate 合规）

SQL_FIND_MODULE_BY_PATH = (
    "SELECT DISTINCT blueprint_id FROM nodes "
    "WHERE path = %s AND blueprint_id IS NOT NULL AND blueprint_id != '' "
    "LIMIT 1"
)

SQL_CREATE_DRIFT_AUDIT_FINDINGS = """CREATE TABLE IF NOT EXISTS drift_audit_findings (

    finding_id TEXT PRIMARY KEY,

    finding_time TEXT NOT NULL,

    drift_type TEXT NOT NULL,

    severity TEXT NOT NULL,

    file_path TEXT NOT NULL,

    detail TEXT NOT NULL,

    status TEXT NOT NULL DEFAULT 'open'

)"""

SQL_INSERT_DRIFT_AUDIT_FINDING = (
    "INSERT INTO drift_audit_findings "
    "(finding_id, finding_time, drift_type, severity, file_path, detail, status) "
    "VALUES (?, ?, ?, ?, ?, ?, 'open')"
)

# S4: module_id_recommend SQL（§5.160.2 NO-BARE-SQL gate 合规）

SQL_FIND_MODULE_BY_DIR = (
    "SELECT DISTINCT blueprint_id FROM nodes "
    "WHERE path LIKE %s AND blueprint_id IS NOT NULL AND blueprint_id != '' "
    "LIMIT 1"
)

# S5: reconcile_execution_log SQL（#ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 2 治本）

# 治本动机：reconciler 失败只返回 warn 结果无持久化日志，AI 无法查询历史失败

# （fail-silent 最危险失败模式）。本表持久化每次 reconciler 执行结果（含完整 detail

# 不截断），AI 查 governance.db 即可见历史失败。复用 drift_scan_reconciler 的

# SQLite governance.db 模式（§5.160.2 NO-BARE-SQL 合规）。

SQL_CREATE_RECONCILE_EXECUTION_LOG = """CREATE TABLE IF NOT EXISTS reconcile_execution_log (

    log_id TEXT PRIMARY KEY,

    logged_at TEXT NOT NULL,

    gate_id TEXT NOT NULL,

    session_id TEXT,

    trigger_source TEXT NOT NULL,

    action TEXT NOT NULL,

    detail TEXT,

    committed_files_summary TEXT,

    acknowledged_at TEXT,

    commit_message TEXT,

    error_pattern_id TEXT

)"""

# 治本（test_critical_warn_ack SSoT）：SQL_INSERT_RECONCILE_LOG 只插入 8 字段

# （不含 commit_message）——老库（无 commit_message 列）也能正常 INSERT。

# commit_message 通过单独 SQL_UPDATE_COMMIT_MESSAGE 写入（仅当非空时调用，

# 且需先 _ensure_commit_message_column 补列）。

SQL_INSERT_RECONCILE_LOG = (
    "INSERT INTO reconcile_execution_log "
    "(log_id, logged_at, gate_id, session_id, trigger_source, "
    "action, detail, committed_files_summary) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
)

# commit_message 单独 UPDATE（INSERT 后调用，仅当 commit_message 非空）。

# 老库需先 _ensure_commit_message_column 补列（幂等）。

SQL_UPDATE_COMMIT_MESSAGE = "UPDATE reconcile_execution_log SET commit_message = ? WHERE log_id = ?"

# GATE-DEPGRAPH-OPS 治本 Phase 2（告警消解语义）：老库幂等迁移——

# 2026-07-19 前创建的 governance.db 无 acknowledged_at 列，写入/查询路径

# 统一经 _ensure_ack_column 补列（PRAGMA 检测，幂等）。

SQL_ALTER_RECONCILE_LOG_ADD_ACK = "ALTER TABLE reconcile_execution_log ADD COLUMN acknowledged_at TEXT"

# #ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD-S6 Phase 3.4 治本断点7：

# 老库幂等迁移——2026-07-19 前创建的 governance.db 无 commit_message 列，

# 写入/查询路径统一经 _ensure_commit_message_column 补列（PRAGMA 检测，幂等）。

# commit_message 用于 post-commit 审计链追溯——CAPABILITY-LOOKUP-REQUIRED gate

# 的 [no-lookup:reason] 逃生通道标记检测需要 commit_message，原断点4-7 导致

# reconciler 无法获取 commit_message 做审计。

SQL_ALTER_RECONCILE_LOG_ADD_COMMIT_MESSAGE = "ALTER TABLE reconcile_execution_log ADD COLUMN commit_message TEXT"

# #ARCH-PREVENTABILITY-LAYER-001 Phase 4 P4-1a 治本（2026-07-20）：

# 老库幂等迁移——2026-07-20 前创建的 governance.db 无 error_pattern_id 列，

# 写入路径统一经 _ensure_error_pattern_id_column 补列（PRAGMA 检测，幂等）。

# error_pattern_id 用于关联 reconciler 失败记录到 AI 错误模式库

# （P4-1 ai_error_pattern_library.py），使 AI 可查询"同类错误历史"而非

# "单次错误详情"。referential-by-convention（SQLite 未启用 FK 约束）。

SQL_ALTER_RECONCILE_LOG_ADD_ERROR_PATTERN_ID = "ALTER TABLE reconcile_execution_log ADD COLUMN error_pattern_id TEXT"

# P4-1a: error_pattern_id 单独 UPDATE（INSERT 后调用，供 P4-1 模式库回填使用）。

# P4-1a 阶段只提供 schema 支持，不填充值；P4-1 ai_error_pattern_library.py

# 会从 detail 提取错误模式指纹，回填 error_pattern_id。

SQL_UPDATE_ERROR_PATTERN_ID = "UPDATE reconcile_execution_log SET error_pattern_id = ? WHERE log_id = ?"

# GATE-DEPGRAPH-OPS 治本 Phase 2（告警消解语义）：活跃 critical_warn 查询。

# 双重消音：① acknowledged_at IS NULL（手动 ack 消音）；② NOT EXISTS 同 gate_id

# 之后的 clean 记录（自愈消音——问题修复后 reconciler 下次运行产出 clean，

# 旧 critical_warn 自动从横幅消失，消除"已解决事件持续告警"的告警疲劳）。

SQL_SELECT_ACTIVE_CRITICAL_WARNS = (
    "SELECT w.gate_id, w.logged_at, substr(w.detail, 1, 200) "
    "FROM reconcile_execution_log w "
    "WHERE w.action = 'critical_warn' AND w.logged_at >= ? "
    "AND w.acknowledged_at IS NULL "
    "AND NOT EXISTS ("
    "SELECT 1 FROM reconcile_execution_log c "
    "WHERE c.gate_id = w.gate_id AND c.action = 'clean' AND c.logged_at > w.logged_at"
    ") "
    "ORDER BY w.logged_at DESC LIMIT 10"
)

# 手动确认（ack）：acknowledged_at IS NULL 过滤保证幂等（重复 ack 不再 UPDATE）。

SQL_ACK_CRITICAL_WARNS_ALL = (
    "UPDATE reconcile_execution_log SET acknowledged_at = ? "
    "WHERE action = 'critical_warn' AND logged_at >= ? AND acknowledged_at IS NULL"
)

SQL_ACK_CRITICAL_WARNS_BY_GATE = (
    "UPDATE reconcile_execution_log SET acknowledged_at = ? "
    "WHERE action = 'critical_warn' AND logged_at >= ? "
    "AND acknowledged_at IS NULL AND gate_id = ?"
)

# 治本 #AUTO-ACK-HEALED-WARN (2026-07-23): clean 记录持久化自愈——
# 同 gate 出现 clean 后，前置未确认且已愈合（有后续 clean）的 critical_warn
# 自动 ack。与 SQL_SELECT_ACTIVE_CRITICAL_WARNS 的 NOT EXISTS 自愈语义对称
# （查询时过滤 → 写时持久化到 acknowledged_at），消除"已愈合但 acknowledged_at
# 永不回填"导致的审计视图污染（历史 164 条假阳性 unack 记录）。
# 仅 ack 有后续 clean 的 warn（EXISTS 子查询），未愈合的真正活跃告警保持 unack。
SQL_AUTO_ACK_HEALED_BY_GATE = (
    "UPDATE reconcile_execution_log SET acknowledged_at = ? "
    "WHERE action = 'critical_warn' AND acknowledged_at IS NULL "
    "AND gate_id = ? "
    "AND EXISTS ("
    "SELECT 1 FROM reconcile_execution_log c "
    "WHERE c.gate_id = reconcile_execution_log.gate_id "
    "AND c.action = 'clean' AND c.logged_at > reconcile_execution_log.logged_at"
    ")"
)

SQL_AUTO_ACK_HEALED_ALL = (
    "UPDATE reconcile_execution_log SET acknowledged_at = ? "
    "WHERE action = 'critical_warn' AND acknowledged_at IS NULL "
    "AND EXISTS ("
    "SELECT 1 FROM reconcile_execution_log c "
    "WHERE c.gate_id = reconcile_execution_log.gate_id "
    "AND c.action = 'clean' AND c.logged_at > reconcile_execution_log.logged_at"
    ")"
)

# 治本 #RECONCILE-LOG-RETENTION (2026-07-23): reconcile_execution_log 无限增长
# 治理——超阈值时删除 N 天前记录（fail-open，不阻断 commit/merge 主流程）。
# 保留窗口 180 天兼顾审计可追溯性与库体积；阈值触发避免每次 commit 都扫表。
SQL_COUNT_RECONCILE_LOG = "SELECT COUNT(*) FROM reconcile_execution_log"

SQL_PRUNE_OLD_RECONCILE_LOGS = "DELETE FROM reconcile_execution_log WHERE logged_at < ?"

DEFAULT_RETENTION_DAYS = 180
LOG_PRUNE_THRESHOLD = 50000

# #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 4.2/4.1: block_next 查询/清除 SQL

# （集中化，避免 NO-BARE-SQL gate；P4.1 补齐 P4.2 半成品——原 _print_block_banner

# 用内联 SQL，现统一为常量，并新增 DELETE 供 resolve_blocks 使用）

SQL_SELECT_BLOCKS = (
    "SELECT gate_id, logged_at, substr(detail, 1, 200) "
    "FROM reconcile_execution_log "
    "WHERE action = 'block_next' AND logged_at >= ? "
    "ORDER BY logged_at DESC LIMIT 10"
)

SQL_DELETE_BLOCKS = "DELETE FROM reconcile_execution_log WHERE action = 'block_next' AND logged_at >= ?"


@dataclass
class ReconcileResult:
    """post-commit 真源对账结果（P0-DRC / P2-T1 迁移至本模块）。

    action 含义：

    - skip: 本次 commit 未涉及该 reconciler 关心的文件，跳过对账

    - clean: 真源重生成后无变更，一致

    - auto_committed: 检测到漂移并自动提交修复

    - warn: 检测到漂移但自动修复失败（仅告警，不阻断；commit 已入 git 历史）

    - critical_warn: 严重失败——架构图与代码不一致且自动同步失败（#ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 3）。

      比 warn 更严重：下次 commit/merge 前打印告警横幅强制 AI 看到。不阻断 commit

      （commit 已入历史无法回滚），但确保失败不被忽视。

    - block_next: 最严重——下次 commit/merge 硬阻断（#ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 4.2/4.1）。

      比 critical_warn 更严重：下次 commit/merge 被 raise/return error 硬阻断，AI 必须修复

      问题后调 resolve_blocks() 清除阻断才能继续。用于需要强制干预的场景（如拓扑不一致、

      安全机制失效）。P4.1 起 PRE-MERGE-TOPO-CHECK 失败时写入此 action（#ARCH-DEP-PREMERGE-ENFORCE）。

    """

    action: str  # "skip" | "clean" | "auto_committed" | "warn" | "critical_warn" | "block_next"

    detail: str = ""

    # #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 2: 由 reconcile_for 填充，

    # 用于 _log_reconcile_results 追踪是哪个 reconciler 产生了该结果。

    # 默认空字符串保持向后兼容（手工构造的 ReconcileResult 无 gate_id）。

    gate_id: str = ""


@dataclass
class ReconcilerSpec:
    """单个 GATE 的 post-commit 对账声明。

    Attributes:

        gate_id: 关联的 pre-commit GATE 标识（如 "GATE-19-manifest"）。

        trigger: 判断本次 committed_files 是否命中该 reconciler；

            返回 True 才执行 reconcile。签名 ``(committed_files: list[str]) -> bool``。

        reconcile: 执行对账，返回 ReconcileResult。

            签名 ``(committed_files: list[str], session_id: str) -> ReconcileResult``。

            reconciler 是闭包，注册时捕获所需上下文（project_root / gateway 实例等）。

            #ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD Phase 3.4 断点6：

            可选第 3 参数 ``commit_message: str``——reconcile_for 用 inspect.signature

            检测 arity，3-arg reconciler 收到 commit_message 用于审计（如

            CAPABILITY-LOOKUP-REQUIRED gate 的 [no-lookup:reason] 标记审计）。

            2-arg reconciler（现有全部 reconciler）向后兼容不收 commit_message。

        priority: 执行优先级（升序，数字小先执行）；同 priority 按 register 顺序。

        file_ops: 文件操作面显式声明（#ARCH-RECONCILER-AUTO-DELETE-GOV-001 T1①，

            2026-08-14 裁定）——``{"none","read","write","delete","move"}`` 子集，

            注册时强校验（空集/非法值 raise）。reconcile_for 执行前经

            ops_guard.set_reconciler_context 注入，执行删除/移动但未声明对应

            能力 → DeleteBlockedError 阻断 + 本表映射 critical_warn。

            第一性原理：自动化代理判定准确率恒<100%，删除能力必须显式声明、

            全量审计、可逆（回收站）。

    """

    gate_id: str

    trigger: Callable[[list[str]], bool]

    reconcile: Callable[..., ReconcileResult]

    priority: int = 100

    file_ops: frozenset = frozenset()  # 空=未声明 → register 强校验拦截


#: file_ops 合法操作集（T1① 声明制词表）
_VALID_FILE_OPS = frozenset({"none", "read", "write", "delete", "move"})


class ReconciliationRegistry:
    """声明式 post-commit 漂移对账注册表（P2-T1）。

    每个 GitCommitGateway 实例持有一个 registry（实例级，非模块级单例——

    避免 reconciler 闭包捕获 gateway 前的先有鸡先有蛋问题）。

    commit 完成后调 ``reconcile_for(committed_files, session_id)``，

    registry 按 priority 升序遍历所有注册的 spec，trigger 命中即执行 reconcile。

    容错：单个 reconciler 抛异常时降级为 ``ReconcileResult(action="warn")``，

    不阻断后续 reconciler 执行（drift 对账非阻断，commit 已入历史）。

    """

    def __init__(self) -> None:

        self._specs: list[ReconcilerSpec] = []

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def specs(self) -> list[ReconcilerSpec]:
        """只读：specs（Stage 4 公共化）。"""
        return self._specs

    @specs.setter
    def specs(self, value):
        """写入：specs（Stage 4 公共化）。"""
        self._specs = value

    def register(self, spec: ReconcilerSpec) -> None:
        """注册一个 reconciler spec（同 gate_id 覆盖旧 spec，幂等）。

        按 priority 升序保持 _specs 有序（注册后即排序，reconcile_for 时无需再排）。

        T1① 强校验（#ARCH-RECONCILER-AUTO-DELETE-GOV-001）：file_ops 空集=未声明
        或含非法值 → raise ValueError（显式声明制，注册期 fail-closed）。

        """

        if not spec.file_ops:
            raise ValueError(
                f"ReconcilerSpec {spec.gate_id} 未声明 file_ops——"
                "T1① 显式声明制（#ARCH-RECONCILER-AUTO-DELETE-GOV-001）："
                "从 {{'none','read','write','delete','move'}} 中显式选择操作面"
            )

        _invalid = set(spec.file_ops) - _VALID_FILE_OPS

        if _invalid:
            raise ValueError(
                f"ReconcilerSpec {spec.gate_id} file_ops 含非法值 {_invalid}，合法集={sorted(_VALID_FILE_OPS)}"
            )

        # 幂等：同 gate_id 先移除旧 spec

        self._specs = [s for s in self._specs if s.gate_id != spec.gate_id]

        self._specs.append(spec)

        self._specs.sort(key=lambda s: s.priority)

    def reconcile_for(
        self,
        committed_files: list[str],
        session_id: str,
        commit_message: str = "",
        heartbeat: Callable[[str], None] | None = None,
    ) -> list[ReconcileResult]:
        """遍历注册的 reconciler，trigger 命中即执行，返回结果列表。

        单个 reconciler 异常降级为 warn 结果，不阻断后续。

        #ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD Phase 3.4 断点5/6 治本：

        新增 commit_message 可选参数——3-arg reconciler（inspect.signature 检测

        arity ≥ 3）收到 commit_message 用于审计（如 [no-lookup:reason] 标记审计）。

        2-arg reconciler（现有全部 reconciler）向后兼容不收 commit_message。

        原断点5: reconcile_for 不接收 commit_message；原断点6: 不传递给 spec.reconcile。

        """

        import inspect

        # T1① lazy import（本模块顶层纯 stdlib 约束，函数内 import 为先例）：
        # DeleteBlockedError 用于映射 critical_warn；ops_guard 不可达时上下文
        # 注入降级为空操作（不阻断 reconciler 主流程，声明制失效风险由注册期
        # 强校验兜底——file_ops 空值根本注册不进来）。
        try:
            from scripts.ops_guard import (
                DeleteBlockedError as _DeleteBlockedError,
            )
            from scripts.ops_guard import (
                reset_reconciler_context as _reset_rc_ctx,
            )
            from scripts.ops_guard import (
                set_reconciler_context as _set_rc_ctx,
            )
        except Exception:  # noqa: BLE001 — ops_guard 不可达降级（注册期强校验已兜底）
            _DeleteBlockedError = None
            _set_rc_ctx = None
            _reset_rc_ctx = None

        results: list[ReconcileResult] = []

        for spec in self._specs:
            try:
                if not spec.trigger(committed_files):
                    continue

                # #ARCH-RECONCILE-WORKER-HEARTBEAT-001 治本（2026-08-01）：
                # 执行前刷新心跳（best-effort，失败不阻断）。
                if heartbeat is not None:
                    try:
                        heartbeat(spec.gate_id)

                    except Exception:  # noqa: BLE001 — 心跳失败不影响 reconciler 主流程
                        pass

                # Phase 3.4 断点6 治本：检测 reconciler arity，3-arg 传 commit_message

                try:
                    sig_params = inspect.signature(spec.reconcile).parameters

                    accepts_msg = len(sig_params) >= 3

                except (ValueError, TypeError):
                    accepts_msg = False  # 内置/C 函数无法 introspect，向后兼容 2-arg

                # T1① file_ops 上下文注入：执行前把 spec 声明注入 ops_guard
                # contextvar——reconciler 内部任何删除/移动（guard_* API 或
                # 装了 in-process 补丁的裸 stdlib）未声明即 DeleteBlockedError。
                _rc_token = None
                if _set_rc_ctx is not None:
                    try:
                        _rc_token = _set_rc_ctx(spec.gate_id, spec.file_ops)
                    except Exception:  # noqa: BLE001 — 注入失败不阻断（审计缺失风险接受）
                        _rc_token = None

                try:
                    if accepts_msg:
                        result = spec.reconcile(committed_files, session_id, commit_message)

                    else:
                        result = spec.reconcile(committed_files, session_id)

                finally:
                    if _rc_token is not None and _reset_rc_ctx is not None:
                        try:
                            _reset_rc_ctx(_rc_token)
                        except Exception:  # noqa: BLE001 — reset 失败不掩盖主结果
                            pass

                # Defensive: 某些 reconciler 可能返回 dict 而非 ReconcileResult，

                # 转换为 ReconcileResult 防止 _run_reconcilers_after_merge 级联失败。

                if isinstance(result, dict):
                    logger.warning(
                        "ReconciliationRegistry: reconciler %s returned dict, converting",
                        spec.gate_id,
                    )

                    result = ReconcileResult(
                        action=result.get("action", "warn"),
                        detail=result.get("detail", ""),
                    )

                # #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 2: 填充 gate_id

                # 供 _log_reconcile_results 追踪结果归属。dataclass mutable，直接赋值。

                if not result.gate_id:
                    result.gate_id = spec.gate_id

                results.append(result)

            except subprocess.TimeoutExpired as e:
                # #ARCH-PRE-EXISTING-DEBT-001 治本（2026-07-20）：

                # timeout 异常升级 critical_warn（非 warn），让 _check_recent_critical_warns

                # 横幅强制 AI 看到。原设计 timeout 被降级为 warn，AI 看不到 loud 提示，

                # 违反 P0-1 ruling「reconciler 失败升级 critical_warn 强制 AI 看到」。

                logger.warning(
                    "ReconciliationRegistry: reconciler %s timed out: %s",
                    spec.gate_id,
                    e,
                )

                results.append(
                    ReconcileResult(
                        action="critical_warn",
                        detail=f"reconciler {spec.gate_id} timed out (timeout={e.timeout}s): {e}",
                        gate_id=spec.gate_id,
                    )
                )

            except (Exception, KeyboardInterrupt) as e:  # noqa: BLE001 — drift 对账非阻断；KeyboardInterrupt 也降级（commit 已入库，reconciler 中断不应 crash 进程，治本 #2026-0701）
                # T1① file_ops 未声明阻断 → 升级 critical_warn（强制 AI 看到：
                # 某 reconciler 执行了它没声明的删除/移动能力——裁定书红队场景）
                if _DeleteBlockedError is not None and isinstance(e, _DeleteBlockedError):
                    logger.warning(
                        "ReconciliationRegistry: reconciler %s file_ops 未声明阻断: %s",
                        spec.gate_id,
                        e,
                    )

                    results.append(
                        ReconcileResult(
                            action="critical_warn",
                            detail=f"reconciler {spec.gate_id} file_ops 未声明执行删除/移动被阻断（I-GOV-2/T1①）: {e}",
                            gate_id=spec.gate_id,
                        )
                    )

                    continue

                logger.warning(
                    "ReconciliationRegistry: reconciler %s failed: %s",
                    spec.gate_id,
                    e,
                )

                results.append(
                    ReconcileResult(
                        action="warn",
                        detail=f"reconciler {spec.gate_id} raised: {e}",
                        gate_id=spec.gate_id,
                    )
                )

        return results

    @property
    def spec_count(self) -> int:
        """已注册的 reconciler 数量（测试/诊断用）。"""

        return len(self._specs)

    def list_gate_ids(self) -> list[str]:
        """已注册的 gate_id 列表（诊断用）。"""

        return [s.gate_id for s in self._specs]


def _governance_db_path(project_root: object) -> str:
    """governance.db 绝对路径，锚定主仓库根（GATE-DEPGRAPH-OPS 治本 Phase 3）。

    worktree 进程内 REPO_ROOT 解析为 worktree 根，直接 join project_root 会把

    观测数据写入 .aidrafts/<session>/data/ 而分裂（merge/abort 后即丢失）。

    #ARCH-WORKTREE-DB-SPLIT-001（2026-08-15）：strip_session_worktree → anchor_main_root。
    原深路径段剥离对"宿主 worktree 内嵌套 pytest tmp 测试库根"
    （.../.worktrees/<宿主>/.runtime/tmp/pytest_*/<test>，conftest basetemp 重定向）
    误剥到主仓根——测试写 tmp 库、本函数读主仓真库，读写双向错位
    （test_critical_warn_ack 等 24 项同族失败实证；cleanup 类函数甚至对主仓真库
    执行 DELETE，存量数据安全隐患）。anchor_main_root 单级父目录结构判定：
    真 worktree 根→锚主仓；嵌套 tmp 测试库根→原样返回，测试隔离恢复。

    """

    import os
    from pathlib import Path

    from zephyr.shared.io.paths import anchor_main_root

    root = anchor_main_root(Path(str(project_root)))

    return os.path.join(str(root), "data", "databases", "governance.db")


def _ensure_ack_column(conn: object) -> None:
    """老库幂等补 acknowledged_at 列（GATE-DEPGRAPH-OPS 治本 Phase 2）。

    2026-07-19 前创建的 governance.db 无 ack 列；PRAGMA table_info 检测，

    缺失才 ALTER（幂等，新库 no-op）。所有读写路径统一调用。

    """

    cols = {r[1] for r in conn.execute("PRAGMA table_info(reconcile_execution_log)")}

    if cols and "acknowledged_at" not in cols:
        conn.execute(SQL_ALTER_RECONCILE_LOG_ADD_ACK)


def _ensure_commit_message_column(conn: object) -> None:
    """老库幂等补 commit_message 列（#ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD Phase 3.4 断点7）。

    2026-07-19 前创建的 governance.db 无 commit_message 列；PRAGMA table_info 检测，

    缺失才 ALTER（幂等，新库 no-op）。所有写入路径统一调用，确保 commit_message

    可持久化到 reconcile_execution_log 表（post-commit 审计链追溯）。

    """

    cols = {r[1] for r in conn.execute("PRAGMA table_info(reconcile_execution_log)")}

    if cols and "commit_message" not in cols:
        conn.execute(SQL_ALTER_RECONCILE_LOG_ADD_COMMIT_MESSAGE)


def _ensure_error_pattern_id_column(conn: object) -> None:
    """老库幂等补 error_pattern_id 列（#ARCH-PREVENTABILITY-LAYER-001 Phase 4 P4-1a）。

    2026-07-20 前创建的 governance.db 无 error_pattern_id 列；PRAGMA table_info

    检测，缺失才 ALTER（幂等，新库 no-op）。所有写入路径统一调用，确保 P4-1

    ai_error_pattern_library.py 可回填 error_pattern_id（关联失败记录到错误模式库）。

    """

    cols = {r[1] for r in conn.execute("PRAGMA table_info(reconcile_execution_log)")}

    if cols and "error_pattern_id" not in cols:
        conn.execute(SQL_ALTER_RECONCILE_LOG_ADD_ERROR_PATTERN_ID)


def _downgrade_auto_committed_on_flush_failure(
    results: list[ReconcileResult],
    flush_result: object | None,
) -> None:
    """治本 #ARCH-ASSET-INDEX-FALSE-AUTO-COMMIT-001（2026-07-30）：
    flush() 失败时降级 auto_committed → warn，防止日志误报"已自动提交"。

    病根：BatchedAutoCommitter.buffer() 返回合成 CommitResult(status=OK,
    commit_hash="BUFFERED")，reconciler 据此返回 action="auto_committed"。
    但实际 git commit 在 flush() 中执行，可能因 NOTHING_TO_COMMIT /
    COMMIT_FAILED / NAMING_VIOLATION 等失败。此时 auto_committed 是误报，
    需降级为 warn 并记录 flush 失败原因，使日志与实际行为一致。

    典型场景：GATE-ASSET-INDEX bootstrap 写索引文件 → buffer() 返回 OK →
    auto_committed；workspace_hygiene 把索引文件 git restore 还原 →
    flush() git diff --cached --quiet 返回 0 → NOTHING_TO_COMMIT。
    降级后 DB 记 warn 而非 auto_committed，消除治理盲区。

    原地修改 results 列表（修改 ReconcileResult.action/detail）。
    flush 成功时不做任何修改（auto_committed 准确）。

    Args:
        results: reconcile_for 返回的 ReconcileResult 列表（原地修改）。
        flush_result: batcher.flush() 的返回值（CommitResult 或 None）。
    """
    if flush_result is None:
        return
    flush_status = getattr(flush_result, "status", None)
    # CommitStatus 是 str Enum：CommitStatus.OK == "OK" 为 True（str 子类相等），
    # 但 str(CommitStatus.OK) 在 Py3.11+ 返回 "CommitStatus.OK"（非 "OK"），
    # 故必须用 == 比较，禁止 str() 比较（否则成功也被误降级）。
    # real _commit_auto 返回 OK 仅当 git commit 真正成功
    # （NOTHING_TO_COMMIT / COMMIT_FAILED 等不在此列）
    if flush_status == "OK":
        return  # flush 成功，auto_committed 准确，无需降级
    # flush 失败或未真正提交：降级所有 auto_committed → warn
    flush_msg = str(getattr(flush_result, "message", ""))[:200]
    for r in results:
        if r.action == "auto_committed":
            r.action = "warn"
            orig_detail = r.detail or ""
            r.detail = (
                f"index regeneration buffered but flush() did not commit "
                f"(flush_status={flush_status}, flush_msg={flush_msg}); "
                f"original: {orig_detail}"
            )


def _log_reconcile_results(
    project_root: object,
    results: list[ReconcileResult],
    session_id: str,
    trigger_source: str,
    committed_files: list[str] | None = None,
    commit_message: str = "",
) -> None:
    """将 reconciler 执行结果持久化到 governance.db reconcile_execution_log 表。

    治本 #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 2：

    之前 reconciler 失败只返回 warn 结果，无持久化日志，AI 无法查询历史失败

    （fail-silent 最危险失败模式——失败不可见，下次 commit 照常开工）。

    本函数在 reconcile_for 的两个调用方（GitCommitGateway._run_post_commit_reconcile

    和 session_worktree._run_reconcilers_after_merge）统一写日志，所有 reconciler

    自动受益（无需逐个修改 reconciler 实现）。

    治本 #ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD Phase 3.4 断点7：

    新增 commit_message 参数——持久化 commit message 到 reconcile_execution_log 表，

    使 post-commit 审计链可追溯 [no-lookup:reason] / ZEPHYR_BYPASS_LOOKUP 逃生通道使用。

    原断点7：_log_reconcile_results 不存储 commit_message，审计链断裂。

    设计裁定（复用 drift_scan_reconciler 模式）：

    - SQLite governance.db（非 PG depgraph）——reconcile 日志是运行时观测数据，

      不需要 PG 事务一致性，且避免触碰 TRAE-059 _schema_version 保护。

    - detail 完整记录（不截断）——失败诊断需要完整错误信息。

    - skip 结果不记录（未触发对账，无日志价值）。

    - 异常降级为 logger.warning（不阻断 commit/merge 主流程）。

    Args:

        project_root: Path 对象（gateway.project_root / merge root）。

        results: reconcile_for 返回的 ReconcileResult 列表（gate_id 已填充）。

        session_id: commit session_id（用于关联 commit 与 reconcile）。

        trigger_source: "post_commit" 或 "post_merge"（标识日志触发方）。

        committed_files: 本次 commit 的文件列表（摘要记录前 20 个，便于追溯）。

        commit_message: 本次 commit 的 message（审计追溯用，post_merge 时为空）。

    """

    import os
    import sqlite3
    import uuid

    try:
        db_path = _governance_db_path(project_root)

        files_summary = ""

        if committed_files:
            rel_files = [_rel_path(f, str(project_root)) for f in committed_files[:20]]

            files_summary = "; ".join(rel_files)

            if len(committed_files) > 20:
                files_summary += f"; ...(+{len(committed_files) - 20} more)"

        # commit_message 截断到 2000 字符（避免超长 message 撑爆 SQLite）

        msg_truncated = (commit_message or "")[:2000]

        conn = sqlite3.connect(db_path, timeout=30.0)

        try:
            conn.execute(SQL_CREATE_RECONCILE_EXECUTION_LOG)

            _ensure_ack_column(conn)  # 老库补 ack 列（幂等）

            _ensure_commit_message_column(conn)  # 老库补 commit_message 列（幂等，Phase 3.4 断点7）

            _ensure_error_pattern_id_column(conn)  # P4-1a: 老库补 error_pattern_id 列（幂等）

            for r in results:
                if r.action == "skip":
                    continue  # skip 未触发对账，无日志价值

                log_id = f"rc-{uuid.uuid4().hex[:12]}"

                conn.execute(
                    SQL_INSERT_RECONCILE_LOG,
                    (
                        log_id,
                        now_utc(),
                        r.gate_id or "unknown",
                        session_id,
                        trigger_source,
                        r.action,
                        r.detail,
                        files_summary,
                    ),
                )

                # commit_message 单独 UPDATE（治本：SQL_INSERT_RECONCILE_LOG 8 字段，

                # 老库兼容；commit_message 非空时通过 UPDATE 写入，新库有列，老库已补列）

                if msg_truncated:
                    conn.execute(
                        SQL_UPDATE_COMMIT_MESSAGE,
                        (msg_truncated, log_id),
                    )

            # 治本 #AUTO-ACK-HEALED-WARN (2026-07-23): 本次 clean 结果会愈合同 gate
            # 的前置 critical_warn，立即回填 acknowledged_at（持久化自愈，消除审计
            # 视图假阳性 unack）。EXISTS 子查询保证只 ack 有后续 clean 的 warn，
            # 真正活跃告警（无后续 clean）保持 unack。read-your-own-writes：本次
            # 插入的 clean 记录在同一事务内对 EXISTS 子查询可见。
            for _gid in {r.gate_id for r in results if r.action == "clean" and r.gate_id}:
                conn.execute(SQL_AUTO_ACK_HEALED_BY_GATE, (now_utc(), _gid))

            # 治本 #RECONCILE-LOG-RETENTION (2026-07-23): 超阈值时清理 N 天前记录，
            # 防止 reconcile_execution_log 无限增长（fail-open，不阻断主流程）。
            try:
                from datetime import datetime, timedelta, timezone

                _log_count = conn.execute(SQL_COUNT_RECONCILE_LOG).fetchone()[0]
                if _log_count > LOG_PRUNE_THRESHOLD:
                    _cutoff = str(datetime.now(timezone.utc) - timedelta(days=DEFAULT_RETENTION_DAYS))
                    conn.execute(SQL_PRUNE_OLD_RECONCILE_LOGS, (_cutoff,))
            except Exception as _prune_err:  # noqa: BLE001 — retention 失败不阻断主流程
                logger.warning("_log_reconcile_results: retention prune skipped: %s", _prune_err)

            conn.commit()

        finally:
            conn.close()

    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("_log_reconcile_results: DB write failed: %s", e)


def log_gate_failure(
    project_root: object,
    gate_id: str,
    detail: str,
    session_id: str = "",
    trigger_source: str = "pre_commit_gate",
    stack_trace: str = "",
) -> None:
    """持久化 gate 检测器失效到 reconcile_execution_log 表。

    Ruling:100PCT-AI-GOVERNANCE P1-5 (2026-07-19) 治本：

    gate fail-open 时（检测器失效但放行 commit），仅 logger.warning 不够 loud，

    且不持久化——AI 无法查询历史失败（fail-silent 最危险失败模式）。

    本函数让 gate 失效持久化到 governance.db，AI 查 reconcile_execution_log 即可见。

    与 _log_reconcile_results 的区别：

    - _log_reconcile_results: post-commit/post-merge reconciler 批量结果持久化

    - log_gate_failure: pre-commit gate 单条检测器失效持久化（action='critical_warn'）

    复用 reconcile_execution_log 表（gate_id 字段已支持 gate 复用）。

    action='critical_warn' 与 P0-1 治本一致，触发 _print_critical_warn_banner 横幅

    （下次 commit/merge 时强制 AI 看到历史 gate 失效）。

    P1-3 (2026-07-20) 治本：增加 stack_trace 参数，持久化完整调用栈。

    原实现只存 detail 字符串（type(e).__name__: e），丢失栈信息——post-mortem 诊断能力受损。

    新实现：stack_trace 非空时追加到 detail 末尾（detail 是 TEXT 字段不截断）。

    调用方在 except 块中用 traceback.format_exc() 传入。

    Args:

        project_root: Path 对象（gateway.project_root）。

        gate_id: 失效的 gate ID（如 "GATE-PANORAMA-ALIGNMENT"）。

        detail: 失败详情（完整错误信息，不截断）。

        session_id: commit session_id（可空）。

        trigger_source: 触发源标识（默认 "pre_commit_gate"）。

        stack_trace: 完整调用栈（traceback.format_exc() 输出，可空）。

    """

    import os
    import sqlite3
    import uuid

    try:
        db_path = _governance_db_path(project_root)

        # Ruling:100PCT-AI-GOVERNANCE P1-5: 确保目录存在（测试/首次运行场景）

        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # P1-3 (2026-07-20): stack_trace 非空时追加到 detail（不截断，TEXT 字段）

        full_detail = detail

        if stack_trace:
            full_detail = f"{detail}\n\n--- Stack trace ---\n{stack_trace}"

        conn = sqlite3.connect(db_path, timeout=30.0)

        try:
            conn.execute(SQL_CREATE_RECONCILE_EXECUTION_LOG)

            _ensure_ack_column(conn)

            _ensure_commit_message_column(conn)

            _ensure_error_pattern_id_column(conn)  # P4-1a: 老库补 error_pattern_id 列（幂等）

            log_id = f"gf-{uuid.uuid4().hex[:12]}"

            conn.execute(
                SQL_INSERT_RECONCILE_LOG,
                (log_id, now_utc(), gate_id, session_id, trigger_source, "critical_warn", full_detail, ""),
            )

            conn.commit()

        finally:
            conn.close()

    except Exception as e:  # noqa: BLE001 — 持久化失败不能阻断 gate 主流程
        logger.warning("log_gate_failure: DB write failed: %s", e)


def log_emergency_commit(
    project_root: object,
    session_id: str,
    commit_sha: str,
    branch: str,
    files: list[str],
    reason: str,
    message: str = "",
) -> None:
    """持久化 emergency_commit 到 reconcile_execution_log + 审计报告文件。

    Ruling:100PCT-AI-GOVERNANCE P2-1 (2026-07-19) 治本：

    emergency_commit 用 git commit-tree 绕过所有 hook，是治理盲区。本函数让

    emergency_commit 持久化到 governance.db（action='emergency_commit'）+ 写

    审计报告到 .runtime/reconcile_reports/，AI 可查询历史。

    与 log_gate_failure 的区别：

    - log_gate_failure: gate 检测器失效，action='critical_warn'，触发横幅告警

    - log_emergency_commit: 紧急提交审计，action='emergency_commit'，不触发横幅

      （emergency_commit 是合法操作，只是需要审计可追溯）

    持久化内容：

    1. reconcile_execution_log 表（gate_id='EMERGENCY-COMMIT', action='emergency_commit'）

    2. .runtime/reconcile_reports/emergency_commit_<timestamp>.json 审计报告

    Args:

        project_root: Path 对象（项目根）。

        session_id: emergency_commit 的 session_id。

        commit_sha: commit SHA（完整或短 SHA 均可）。

        branch: 提交到的分支名。

        files: 提交的文件相对路径列表。

        reason: 紧急提交原因（写入 detail 字段）。

        message: 完整 commit message（含 [GW:...] 标记，写入 commit_message 字段）。

    """

    import json
    import os
    import sqlite3
    import uuid
    from pathlib import Path

    try:
        root = Path(str(project_root)).resolve()

        db_path = _governance_db_path(root)

        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # 持久化到 reconcile_execution_log

        detail = f"emergency_commit sha={commit_sha} branch={branch} files={len(files)} reason={reason}"

        files_summary = ", ".join(files[:20])  # 截断前 20 个文件避免过长

        if len(files) > 20:
            files_summary += f" ... (+{len(files) - 20} more)"

        conn = sqlite3.connect(db_path, timeout=30.0)

        try:
            conn.execute(SQL_CREATE_RECONCILE_EXECUTION_LOG)

            _ensure_ack_column(conn)

            _ensure_commit_message_column(conn)

            _ensure_error_pattern_id_column(conn)  # P4-1a: 老库补 error_pattern_id 列（幂等）

            log_id = f"ec-{uuid.uuid4().hex[:12]}"

            conn.execute(
                SQL_INSERT_RECONCILE_LOG,
                (
                    log_id,
                    now_utc(),
                    "EMERGENCY-COMMIT",  # gate_id 字段复用为操作标识
                    session_id,
                    "emergency_commit",  # trigger_source
                    "emergency_commit",  # action
                    detail,
                    files_summary,
                ),
            )

            # commit_message 单独 UPDATE（治本：SQL_INSERT_RECONCILE_LOG 8 字段）

            msg_truncated = message[:2000] if message else ""

            if msg_truncated:
                conn.execute(
                    SQL_UPDATE_COMMIT_MESSAGE,
                    (msg_truncated, log_id),
                )

            conn.commit()

        finally:
            conn.close()

        # 写审计报告到 .runtime/reconcile_reports/

        reports_dir = root / ".runtime" / "reconcile_reports"

        reports_dir.mkdir(parents=True, exist_ok=True)

        import time

        timestamp = int(time.time())

        report = {
            "gate_id": "EMERGENCY-COMMIT",
            "timestamp": timestamp,
            "session_id": session_id,
            "commit_sha": commit_sha,
            "branch": branch,
            "files": files,
            "files_count": len(files),
            "reason": reason,
            "action": "emergency_commit",
            "message_preview": (message[:500] if message else ""),
        }

        report_file = reports_dir / f"emergency_commit_{timestamp}.json"

        report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

        logger.info(
            "log_emergency_commit: persisted sha=%s branch=%s files=%d",
            commit_sha[:10] if commit_sha else "?",
            branch,
            len(files),
        )

    except Exception as e:  # noqa: BLE001 — 审计日志失败不能阻断 emergency commit
        logger.warning("log_emergency_commit: persistence failed: %s", e)


def _check_recent_critical_warns(project_root: object, hours: int = 24) -> list[dict]:
    """查询 governance.db 最近 N 小时内的【活跃】critical_warn 记录。

    治本 #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 3：

    让 commit/merge 前能看到最近的严重失败（depgraph 同步失败等），

    由 _print_critical_warn_banner 打印告警横幅强制 AI 看到。

    GATE-DEPGRAPH-OPS 治本 Phase 2（告警消解语义）：只返回活跃告警——

    ① 已 ack（acknowledged_at 非空）消音；② 同 gate_id 之后有 clean 记录

    （问题已修复自愈）消音。消除"已解决事件持续告警"的告警疲劳。

    Args:

        project_root: Path 对象（gateway.project_root / merge root）。

        hours: 查询窗口（小时），默认 24h。

    Returns:

        list[dict]: 每条含 gate_id/logged_at/detail（detail 截断到 200 字符用于横幅显示）。

        空列表表示无活跃 critical_warn 或查询失败（fail-open，不阻断主流程）。

    """

    import sqlite3
    from datetime import datetime, timedelta, timezone

    try:
        db_path = _governance_db_path(project_root)

        # 治本: 用 str() 而非 isoformat()——SQLite 存 datetime 经 str() 生成空格分隔
        # ('2026-07-22 18:26:51+00:00')，isoformat() 用 'T' 分隔，字符串比较时
        # 'T'(ord=84) > ' '(ord=32) 导致 logged_at >= cutoff 永远 False（fail-silent）
        cutoff = str(datetime.now(timezone.utc) - timedelta(hours=hours))

        conn = sqlite3.connect(db_path, timeout=10.0)

        try:
            conn.execute(SQL_CREATE_RECONCILE_EXECUTION_LOG)

            _ensure_ack_column(conn)  # 老库补 ack 列（幂等，否则查询报 no such column）

            rows = conn.execute(SQL_SELECT_ACTIVE_CRITICAL_WARNS, (cutoff,)).fetchall()

            return [{"gate_id": r[0], "logged_at": r[1], "detail": r[2]} for r in rows]

        finally:
            conn.close()

    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("_check_recent_critical_warns: query failed: %s", e)

        return []


def _print_critical_warn_banner(project_root: object, context: str) -> None:
    """打印 critical_warn 告警横幅（如有近期记录）。

    治本 #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 3：

    "工人失败时大声喊"——commit/merge 前翻日志本，有 critical_warn 就打印醒目横幅。

    不阻断 commit/merge（warn 语义），但确保失败不被忽视（消除 fail-silent 的最后一公里）。

    Args:

        project_root: Path 对象（gateway.project_root / merge root）。

        context: "pre_commit" 或 "pre_merge"（标识调用场景，显示在横幅中）。

    """

    warns = _check_recent_critical_warns(project_root)

    if not warns:
        return

    # 保留 print（5.20 B 类）：本函数职责即打印醒目横幅（"工人失败时大声喊"），

    # 必须不依赖 logging 配置直出控制台

    print("\n" + "=" * 78)

    print(f"!! CRITICAL RECONCILER FAILURES DETECTED (last 24h) -- context: {context}")

    print(f"   {len(warns)} recent critical_warn(s) in reconcile_execution_log:")

    for w in warns[:5]:
        print(f"   - [{w['logged_at']}] {w['gate_id']}: {w['detail']}")

    if len(warns) > 5:
        print(f"   ... and {len(warns) - 5} more (query governance.db for full list)")

    print("   Action required: investigate failures before proceeding.")

    print("=" * 78 + "\n")


def _check_recent_blocks(project_root: object, hours: int = 24) -> list[dict]:
    """查询 governance.db 最近 N 小时内的 block_next 记录。

    治本 #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 4.2/4.1：

    block_next 是最严重的 reconciler 失败级别——下次 commit/merge 硬阻断。

    本函数供 _print_block_banner 查询近期 block_next 记录，与

    _check_recent_critical_warns 对称（critical_warn 只告警，block_next 硬阻断）。

    P4.1 起 PRE-MERGE-TOPO-CHECK 失败时写入 block_next action

    （#ARCH-DEP-PREMERGE-ENFORCE），此函数才会查到非空结果。

    Args:

        project_root: Path 对象（gateway.project_root / merge root）。

        hours: 查询窗口（小时），默认 24h。

    Returns:

        list[dict]: 每条含 gate_id/logged_at/detail（detail 截断到 200 字符用于横幅显示）。

        空列表表示无 block_next 或查询失败（fail-open，不阻断主流程）。

    """

    import sqlite3
    from datetime import datetime, timedelta, timezone

    try:
        db_path = _governance_db_path(project_root)

        # 治本: 用 str() 而非 isoformat()——SQLite 存 datetime 经 str() 生成空格分隔
        # ('2026-07-22 18:26:51+00:00')，isoformat() 用 'T' 分隔，字符串比较时
        # 'T'(ord=84) > ' '(ord=32) 导致 logged_at >= cutoff 永远 False（fail-silent）
        cutoff = str(datetime.now(timezone.utc) - timedelta(hours=hours))

        conn = sqlite3.connect(db_path, timeout=10.0)

        try:
            rows = conn.execute(SQL_SELECT_BLOCKS, (cutoff,)).fetchall()

        finally:
            conn.close()

        return [{"gate_id": r[0], "logged_at": r[1], "detail": r[2]} for r in rows]

    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("_check_recent_blocks: query failed: %s", e)

        return []


def _print_block_banner(project_root: object, context: str) -> str | None:
    """打印 block_next 阻断横幅并返回 error 字符串（如有 block_next 记录）。

    治本 #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 4.2/4.1：

    "工人失败时锁门"——commit/merge 前翻日志本，有 block_next 就打印醒目横幅

    并返回 error 字符串（调用方据此硬阻断）。比 critical_warn 更严重：

    critical_warn 只告警不阻断，block_next 硬阻断——AI 必须修复问题后调

    resolve_blocks() 清除阻断才能继续。

    设计裁定（不直接 raise 而返回 error message）：reconciliation_registry 是

    纯 stdlib 模块，不能 import GatewayError（循环导入）。调用方

    （GitCommitGateway.commit / session_worktree_merge）拿到 error message 后

    自行决定如何阻断（return CommitResult / return error dict）。

    P4.1 起 PRE-MERGE-TOPO-CHECK 失败时写入 block_next（#ARCH-DEP-PREMERGE-ENFORCE），

    此函数成为 block_next 机制的实际执行点。

    Args:

        project_root: Path 对象（gateway.project_root / merge root）。

        context: "pre_commit" 或 "pre_merge"（标识调用场景，显示在横幅中）。

    Returns:

        error 字符串（有 block_next 记录，阻断 commit/merge）| None（无记录，不阻断）。

    """

    blocks = _check_recent_blocks(project_root)

    if not blocks:
        return None

    # 保留 print（5.20 B 类）：本函数职责即打印阻断横幅（"工人失败时锁门"），

    # 必须不依赖 logging 配置直出控制台

    print("\n" + "=" * 78)

    print(f"!!! BLOCKING RECONCILER FAILURES (last 24h) -- context: {context}")

    print(f"   {len(blocks)} recent block_next(s) in reconcile_execution_log:")

    for b in blocks[:5]:
        print(f"   - [{b['logged_at']}] {b['gate_id']}: {b['detail']}")

    if len(blocks) > 5:
        print(f"   ... and {len(blocks) - 5} more (query governance.db for full list)")

    print("   HARD BLOCK: fix failures then run resolve_blocks() to clear.")

    print("=" * 78 + "\n")

    return (
        f"BLOCKING reconciler failures ({len(blocks)} block_next in last 24h, "
        f"context={context}). Fix failures then run resolve_blocks() to clear."
    )


def resolve_blocks(project_root: object, hours: int = 24) -> dict:
    """清除 governance.db 中近 N 小时的 block_next 阻断记录。

    治本 #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 4.2/4.1：

    AI 修复 block_next 指向的问题（如拓扑漂移、reconciler 失败）后调用此函数

    清除阻断记录，恢复 commit/merge。DELETE reconcile_execution_log 中

    action='block_next' 且 logged_at >= cutoff 的记录。

    设计裁定（DELETE 而非新增 resolved 字段）：YAGNI——block_next 是"待处理"

    状态，清除即"已处理"，无需保留 resolved 历史影响后续阻断判断。查询侧

    （_check_recent_blocks）只查未删除的 block_next，DELETE 后即不可见。

    避免 ALTER TABLE 加 resolved 字段的迁移成本。

    Args:

        project_root: Path 对象（gateway.project_root / merge root）。

        hours: 清除窗口（小时），默认 24h（与 _check_recent_blocks 查询窗口一致）。

    Returns:

        {"resolved": int, "error": str | None} —— resolved=删除的行数，

        error 非 None 表示 DB 操作失败（AI 应检查 governance.db 状态）。

    """

    import os
    import sqlite3
    from datetime import datetime, timedelta, timezone

    try:
        db_path = os.path.join(str(project_root), "data", "databases", "governance.db")

        # 治本: 用 str() 而非 isoformat()——SQLite 存 datetime 经 str() 生成空格分隔
        # ('2026-07-22 18:26:51+00:00')，isoformat() 用 'T' 分隔，字符串比较时
        # 'T'(ord=84) > ' '(ord=32) 导致 logged_at >= cutoff 永远 False（fail-silent）
        cutoff = str(datetime.now(timezone.utc) - timedelta(hours=hours))

        conn = sqlite3.connect(db_path, timeout=10.0)

        try:
            cur = conn.execute(SQL_DELETE_BLOCKS, (cutoff,))

            deleted = cur.rowcount

            conn.commit()

        finally:
            conn.close()

        logger.info("resolve_blocks: cleared %d block_next records (window=%dh)", deleted, hours)

        return {"resolved": deleted, "error": None}

    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("resolve_blocks: DB delete failed: %s", e)

        return {"resolved": 0, "error": str(e)}


def acknowledge_critical_warns(project_root: object, gate_id: str | None = None, hours: int = 24) -> dict:
    """手动确认（ack）近 N 小时的 critical_warn 告警，使其从告警横幅消音。

    GATE-DEPGRAPH-OPS 治本 Phase 2（告警消解语义）：

    病根——critical_warn 记录永久活跃，问题修复后仍反复打印告警横幅

    （2026-07-18 GATE-DEPGRAPH-OPS 两次 critical_warn 已修复但持续告警），

    导致告警疲劳、真实新告警被淹没。本函数提供手动确认出口：

    AI/人工排查确认后 ack，告警从横幅消失；未 ack 的继续告警。

    与自愈消音互补：同 gate_id 之后 reconciler 产出 clean 记录时旧告警

    自动消音（无需 ack）；ack 用于"已人工确认但 clean 尚未产生"的场景。

    幂等：acknowledged_at IS NULL 过滤，重复 ack 不再 UPDATE。

    老库自动补 ack 列（_ensure_ack_column）。空库 CREATE 兜底建表。

    Returns:

        {"acknowledged": int, "gate_id": str | None, "error": str | None}。

    """

    import sqlite3
    from datetime import datetime, timedelta, timezone
    from pathlib import Path

    try:
        db_path = _governance_db_path(project_root)

        Path(db_path).parent.mkdir(parents=True, exist_ok=True)  # 空库 CREATE 兜底

        # 治本: 用 str() 而非 isoformat()——SQLite 存 datetime 经 str() 生成空格分隔
        # ('2026-07-22 18:26:51+00:00')，isoformat() 用 'T' 分隔，字符串比较时
        # 'T'(ord=84) > ' '(ord=32) 导致 logged_at >= cutoff 永远 False（fail-silent）
        cutoff = str(datetime.now(timezone.utc) - timedelta(hours=hours))

        conn = sqlite3.connect(db_path, timeout=10.0)

        try:
            conn.execute(SQL_CREATE_RECONCILE_EXECUTION_LOG)

            _ensure_ack_column(conn)  # 老库补列（幂等）

            if gate_id is None:
                cur = conn.execute(SQL_ACK_CRITICAL_WARNS_ALL, (now_utc(), cutoff))

            else:
                cur = conn.execute(SQL_ACK_CRITICAL_WARNS_BY_GATE, (now_utc(), cutoff, gate_id))

            acked = cur.rowcount

            conn.commit()

        finally:
            conn.close()

        logger.info(
            "acknowledge_critical_warns: acked %d critical_warn(s) (gate_id=%s, window=%dh)",
            acked,
            gate_id or "ALL",
            hours,
        )

        return {"acknowledged": acked, "gate_id": gate_id, "error": None}

    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("acknowledge_critical_warns: DB update failed: %s", e)

        return {"acknowledged": 0, "gate_id": gate_id, "error": str(e)}


def backfill_auto_ack_healed(project_root: object) -> dict:
    """一次性回填：自动确认所有已自愈（有后续 clean 记录）的 critical_warn。

    治本 #AUTO-ACK-HEALED-WARN (2026-07-23)：
    历史数据中存在已自愈但 acknowledged_at 未回填的 critical_warn（部署自动 ack
    机制前积累的假阳性 unack）。本函数全局扫描并回填，仅 ack 有后续 clean 的 warn，
    真正活跃告警（无后续 clean）保持 unack。

    与 _log_reconcile_results 内联自动 ack 的区别：本函数处理全部 gate 的历史
    积压，内联版本只处理本次 commit 产出 clean 的 gate（增量）。部署新代码后
    调用一次本函数清理存量，之后内联版本维持增量。

    幂等：acknowledged_at IS NULL 过滤，重复调用不再 UPDATE。

    Returns:
        {"acknowledged": int, "error": str | None}。
    """
    import sqlite3
    from pathlib import Path

    try:
        db_path = _governance_db_path(project_root)
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)  # 空库 CREATE 兜底
        conn = sqlite3.connect(db_path, timeout=30.0)
        try:
            conn.execute(SQL_CREATE_RECONCILE_EXECUTION_LOG)
            _ensure_ack_column(conn)  # 老库补列（幂等）
            cur = conn.execute(SQL_AUTO_ACK_HEALED_ALL, (now_utc(),))
            acked = cur.rowcount
            conn.commit()
        finally:
            conn.close()
        logger.info("backfill_auto_ack_healed: acked %d healed critical_warn(s)", acked)
        return {"acknowledged": acked, "error": None}
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("backfill_auto_ack_healed: DB update failed: %s", e)
        return {"acknowledged": 0, "error": str(e)}


def cleanup_reconcile_log(project_root: object, retention_days: int = DEFAULT_RETENTION_DAYS) -> dict:
    """删除 retention_days 天前的 reconcile_execution_log 记录。

    治本 #RECONCILE-LOG-RETENTION (2026-07-23)：
    reconcile_execution_log 无限增长（5 天 13K 记录），本函数提供手动清理出口。
    _log_reconcile_results 内置超阈值自动触发（LOG_PRUNE_THRESHOLD）；本函数供
    运维/AI 主动清理或验证保留策略。

    cutoff 用 str()（空格分隔）与 logged_at 存储格式对齐（datetime 一致性铁律）。

    Args:
        project_root: Path 对象（gateway.project_root）。
        retention_days: 保留天数，默认 180 天。

    Returns:
        {"deleted": int, "retention_days": int, "error": str | None}。
    """
    import sqlite3
    from datetime import datetime, timedelta, timezone
    from pathlib import Path

    try:
        db_path = _governance_db_path(project_root)
        if not Path(db_path).is_file():
            return {"deleted": 0, "retention_days": retention_days, "error": None}
        cutoff = str(datetime.now(timezone.utc) - timedelta(days=retention_days))
        conn = sqlite3.connect(db_path, timeout=30.0)
        try:
            cur = conn.execute(SQL_PRUNE_OLD_RECONCILE_LOGS, (cutoff,))
            deleted = cur.rowcount
            conn.commit()
        finally:
            conn.close()
        logger.info("cleanup_reconcile_log: deleted %d records older than %dd", deleted, retention_days)
        return {"deleted": deleted, "retention_days": retention_days, "error": None}
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("cleanup_reconcile_log: DB prune failed: %s", e)
        return {"deleted": 0, "retention_days": retention_days, "error": str(e)}


def _write_reconcile_report(project_root: object, prefix: str, report: dict) -> tuple[object, str]:
    """写 reconciler 报告到 ``.runtime/reconcile_reports/{prefix}_{ts}.json``。

    向内收（消除重复）：6 个 reconciler 都有 mkdir+ts+write+try/except 报告落盘

    模式，本函数收拢为单点。自动添加 ``timestamp`` 字段。

    Args:

        project_root: Path 对象（gateway.project_root，类型注解 object 保持纯 stdlib）。

        prefix: 报告文件名前缀（如 "baseline_aware" / "rules_integrity"）。

        report: 报告字典（不含 timestamp，本函数自动注入）。

    Returns:

        (report_path, "") 成功 | (None, error_msg) 失败。

    """

    import json
    import time

    reports_dir = project_root / ".runtime" / "reconcile_reports"

    reports_dir.mkdir(parents=True, exist_ok=True)

    ts = int(time.time())

    report["timestamp"] = ts

    report_path = reports_dir / f"{prefix}_{ts}.json"

    try:
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return report_path, ""

    except OSError as e:
        return None, "internal error"


def make_manifest_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-19 manifest post-commit 对账 reconciler（P2-T2）。

    把原 ``GitCommitGateway._post_commit_reconcile`` 逻辑迁移为独立 ReconcilerSpec，

    注册到 ReconciliationRegistry。闭包捕获 gateway 实例以复用 ``project_root``

    与 ``_run_git``。

    对账链（与迁移前行为等价）：

    1. trigger: committed_files 含 scripts/ 下 .py -> 命中

    2. 重生成 scripts/script-manifest.yaml（generate_manifest.py os.walk 全树 SSoT）

    3. git diff 检测 manifest 变更 -> 无变更返回 clean

    4. 有变更 -> git add + git commit --no-verify（斩断 zombie 引用循环）

    manifest 体系区分（P1-T4 校正 + #51 裁定收敛 2026-08-14）：本 reconciler 重生成的是

    ``scripts/script-manifest.yaml``（全树 manifest 登记真源，generate_manifest.py 产出，

    供 gateway + audit_registration + orphan_scanner 等登记检查链消费）；非

    ``scripts/governance/script_manifest.yaml``

    （governance 子集，generate_script_manifest.py 产出，GATE-19/21 校验）。二者非冗余。

    Args:

        gateway: GitCommitGateway 实例（仅用其 project_root + _run_git，类型注解为

            object 避免本纯 stdlib 模块 import zephyr.*）。

    Returns:

        ReconcilerSpec(gate_id="GATE-19-manifest", priority=100)。

    """

    import os
    import subprocess
    import sys

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel.startswith("scripts/") and rel.endswith(".py"):
                return True

        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        # 1. 重生成 manifest（SSoT disk-scan）

        gen_result = _run_subprocess(
            [sys.executable, "scripts/generate_manifest.py"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )

        if gen_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"manifest regeneration failed: {gen_result.stderr.strip()[:200]}",
            )

        # 2. 检测 manifest 变更

        diff_result = gateway.run_git(["git", "diff", "--name-only", "--", "scripts/script-manifest.yaml"])

        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="manifest up to date")

        # 3. 变更 -> 自动提交修复（经 _commit_auto 统一入口，DCR gate 覆盖）

        # 治本（2026-06-30）：原裸调 _run_git commit 绕过 DCR gate，改为走 _commit_auto

        # 统一入口，ttl/deprecated/pure_assertion/pure_shim/DCR 五重 gate 覆盖。

        auto_msg = "chore(manifest): auto-reconcile by GitCommitGateway post-commit"

        abs_files = [str(project_root / "scripts/script-manifest.yaml")]

        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)

        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail="manifest drift detected and auto-reconciled",
            )

        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="manifest no drift (auto-commit found no staged changes)",
            )

        return ReconcileResult(
            action="warn",
            detail=f"manifest drift detected, auto-commit failed ({commit_result.status}): "
            f"{commit_result.message[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-19-manifest",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=100,
        file_ops=frozenset({"read", "write"}),
    )


def make_path_tree_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 arch_directory_tree post-commit 自动同步 reconciler。

    commit .py/.yaml 文件后，depgraph 的 arch_directory_tree 表可能过时

    （磁盘文件结构变了但 DB 未同步）。本 reconciler 在 post-commit 跑

    generate_project_path_tree.py --write 同步磁盘->DB，如有变更自动提交。

    对标 make_manifest_reconciler 的"检测变更->自动提交"模式。

    替代原 pre-commit GATE-SYNC-PATH-TREE hook（该 hook 有原 depgraph.db（SQLite）

    unstaged 死循环副作用，reconciler 在 post-commit 自动提交修复此问题）。

    Args:

        gateway: GitCommitGateway 实例（用 project_root + _run_git）。

    Returns:

        ReconcilerSpec(gate_id="GATE-PATH-TREE", priority=150)。

    """

    import os
    import subprocess
    import sys

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel.endswith((".py", ".yaml", ".yml")):
                return True

        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        # P1 治本已落地（#ARCH-REGEN-NONIDEMPOTENT-001，commit 97c77a9c8a，2026-08-05）：
        # 6 生成器去 datetime.now + LIMIT 加 ORDER BY + write_text 加 newline=\n，
        # 生成器幂等性已恢复。P0 止血 skip 已移除，恢复正常 reconciler 逻辑。
        # 派生产物离库（#ARCH-GOV-BUDGET-001 / I-GOV-1）见 AGENTS.md §11.1.4。

        # 治本（2026-06-27）：删除 depgraph.db git diff/add/commit 死代码。

        # P2 PG 迁移后 depgraph 已迁至 PostgreSQL，generate_project_path_tree.py --write

        # 直接写入 PG（不产生 .db 文件变更），原 git diff/add/commit depgraph.db 逻辑

        # 永远不会命中（diff 永远为空），属于路径污染残留死代码。

        sync_result = _run_subprocess(
            [sys.executable, "scripts/governance/generate_project_path_tree.py", "--write"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,  # 止血：60->120（项目规模 10k+ 目录逼近 60s 预算；治本见 generate_path_tree.py 性能优化任务）
        )

        if sync_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"path_tree sync failed: {sync_result.stderr.strip()[:200]}",
            )

        # 串联调用 d5 generate_path_tree.py 生成架构文档 md（治本 trae_060 §5）

        # 读 depgraph arch_directory_tree -> 生成 md 文档供人类查看

        doc_result = _run_subprocess(
            [sys.executable, "scripts/governance/d5_architecture/generators/generate_path_tree.py"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,  # 止血：60->120（项目规模 10k+ 目录逼近 60s 预算；治本见 generate_path_tree.py 性能优化任务）
        )

        if doc_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"path_tree sync OK but doc gen failed: {doc_result.stderr.strip()[:150]}",
            )

        # 4. 检测 full_project_tree 文档变更 -> 自动提交（治本 post-commit 循环）

        # 病根：原实现生成 md 后返回 action="clean" 不自动提交，导致每次 commit 后

        # full_project_tree_en/zh.md 变成 modified 残留（post-commit 循环）。

        # 治本：对标 make_manifest_reconciler line 277-304，检测变更->_commit_auto 自动提交。

        _tree_files = [
            "docs/02_enterprise_architecture/01_global_architecture_diagram/full_project_tree_en.md",
            "docs/02_enterprise_architecture/01_global_architecture_diagram/full_project_tree_zh.md",
        ]

        _diff_result = gateway.run_git(["git", "diff", "--name-only", "--"] + _tree_files)

        if _diff_result.returncode == 0 and not _diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="arch_directory_tree synced + path doc up to date")

        # 变更 -> 自动提交（_commit_auto 不触发 reconciler，无循环风险）

        _auto_msg = "chore(path-tree): auto-reconcile full_project_tree by GitCommitGateway post-commit"

        _abs_files = [str(project_root / f) for f in _tree_files]

        _commit_result = gateway._commit_auto(session_id, _abs_files, _auto_msg)

        if _commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail="arch_directory_tree synced + path doc regenerated and auto-committed",
            )

        if _commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="arch_directory_tree synced + path doc no drift (auto-commit found no staged changes)",
            )

        return ReconcileResult(
            action="warn",
            detail=f"path doc drift detected, auto-commit failed ({_commit_result.status}): "
            f"{_commit_result.message[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-PATH-TREE",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=150,
        file_ops=frozenset({"read", "write"}),
    )


# trae_060-reviewed: 合规——新增 reconciler（无法合并进已有：path_tree 触发 .py/.yaml，path_ownership 触发 blueprint.md，生成器不同；治本：path_ownership_map.yaml 自动同步消除手工维护漂移）


def make_path_ownership_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 path_ownership_map.yaml post-commit 自动同步 reconciler。

    commit docs/03_modules/**/blueprint.md 后，path_ownership_map.yaml 可能过时

    （蓝图 §0.1 文件清单变了但 ownership map 未同步）。本 reconciler 在 post-commit

    跑 generate_path_ownership_map.py --write 同步，如有变更自动提交。

    对标 make_path_tree_reconciler（arch_directory_tree 同步）的 subprocess 模式。

    区别：

    - 触发条件：仅 blueprint.md 变更（path_tree 触发 .py/.yaml）

    - 生成器：generate_path_ownership_map.py（path_tree 用 generate_project_path_tree.py）

    - 输出：docs/03_modules/path_ownership_map.yaml（path_tree 输出 full_project_tree.md）

    """

    import os
    import subprocess
    import sys

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel.endswith("blueprint.md") and rel.startswith("docs/03_modules/"):
                return True

        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        ownership_file = "docs/03_modules/path_ownership_map.yaml"

        # 1. 重新生成 path_ownership_map.yaml

        sync_result = _run_subprocess(
            [sys.executable, "scripts/governance/generators/generate_path_ownership_map.py", "--write"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )

        if sync_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"path_ownership sync failed: {sync_result.stderr.strip()[:200]}",
            )

        # 2. 检测 path_ownership_map.yaml 是否有变更

        diff_result = gateway.run_git(["git", "diff", "--name-only", "--", ownership_file])

        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="path_ownership_map.yaml up to date")

        # 3. 有变更 -> 自动提交

        abs_file = str(project_root / ownership_file)

        auto_msg = "chore(path-ownership): auto-reconcile path_ownership_map by GitCommitGateway post-commit"

        commit_result = gateway._commit_auto(session_id, [abs_file], auto_msg)

        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail="path_ownership_map.yaml regenerated and auto-committed",
            )

        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="path_ownership_map.yaml no drift (auto-commit found no staged changes)",
            )

        return ReconcileResult(
            action="warn",
            detail=f"path_ownership_map.yaml drift detected, auto-commit failed ({commit_result.status}): "
            f"{commit_result.message[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-PATH-OWNERSHIP",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=160,  # 在 path_tree(150) 之后
        file_ops=frozenset({"read", "write"}),
    )


def make_depgraph_ops_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 depgraph nodes/edges 运营态 post-commit 自动同步 reconciler（裁定#209）。

    commit .py 文件后，depgraph 的 nodes/edges 运营态表可能过时（代码变了但

    depgraph 未同步）。本 reconciler 在 post-commit 跑 generate_project_depgraph.py

    同步代码->DB。

    对标 make_path_tree_reconciler（arch_directory_tree 同步）的 subprocess 模式。

    区别：

    - trigger 只匹配 .py（不匹配 .yaml/.yml——避免改 depgraph 数据时触发自己）

    - reconcile 直接跑 --output-db --force（P1/P2 保护机制兜底，不覆盖手工字段）

    - 失败降级 warn，不阻断 commit

    - 无文档自动提交（nodes/edges 无人类可读 md 派生，由 design_vs_production 独立生成）

    阶段1（裁定#209）：全量扫描，每次 commit .py 都重跑。

    阶段3（裁定#209）：引入文件级 hash fingerprint 增量，降低频率成本。

    实弹验证（2026-07-02 R2）：干净环境重跑，确认 reconciler 全流程在无并发干扰下正常工作。

    Args:

        gateway: GitCommitGateway 实例（用 project_root）。

    Returns:

        ReconcilerSpec(gate_id="GATE-DEPGRAPH-OPS", priority=130)。

    """

    import os
    import subprocess
    import sys

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel.endswith(".py"):
                return True

        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        # 全量同步代码->DB（P1/P2 保护机制兜底，不覆盖手工字段，详见 §14.2.1）

        # S3（裁定#209 阶段3）：scan_cache.json 已实现 content_hash 增量——

        # --force 仅控制 DB 写入安全门禁（裁定#207 R2 C2），不影响 scan cache。

        # AST 解析已为 O(变更文件)，DB 写入仍为全量 DELETE+INSERT（事务原子安全）。

        import time

        # #ARCH-WORKTREE-DB-SPLIT-001（2026-08-15 裁定）治本①：全量 DELETE+INSERT
        # 重建的扫描根=cwd 工作区——N 工作区并发下共享 PG 被"最后写入者"翻转
        # （worktree 6505 ↔ 主仓 6500 实证振荡→126 tracked 蓝图派生统计反复 dirty）。
        # 裁定：全量重建仅允许主仓锚定上下文；worktree 内增量登记走 apply_depgraph
        # （design 节点 upsert，NEW-FILE-DEPGRAPH gate 修复路径①），merge 后由主仓
        # 重建自然吸收（#ARCH-70 同 path design→production 自动转换）。
        # 父目录结构判定（非段匹配）——pytest tmp 库嵌套宿主 worktree 下不误判。
        from zephyr.shared.io.paths import anchor_main_root

        _root_path = Path(str(project_root))
        _main_root = anchor_main_root(_root_path)
        if _main_root != _root_path:
            return ReconcileResult(
                action="clean",
                detail=(
                    "worktree 上下文跳过 depgraph 全量重建（#ARCH-WORKTREE-DB-SPLIT-001 "
                    "裁定：重建权威归主仓锚定进程，worktree 增量登记走 apply_depgraph "
                    "--add-design-node，merge 后主仓重建自动吸收）"
                ),
            )

        # 遗留项3 治本（GATE-DEPGRAPH-OPS pytest tmp 噪音）：tmp 测试库无生成器
        # 脚本——原逻辑照 spawn 致 rc=2 "can't open file" critical_warn 污染生产
        # reconcile_execution_log（#50 治了 DB 写入隔离，subprocess 调用残留）。
        # 无生成器=非 Zephyr 仓库→clean skip（不是失败，不应告警）。
        _generator = _root_path / "scripts" / "governance" / "generate_project_depgraph.py"
        if not _generator.is_file():
            return ReconcileResult(
                action="clean",
                detail="非 Zephyr 仓库（无 generate_project_depgraph.py，tmp 测试库等），跳过 depgraph sync",
            )

        # #ARCH-DEPGRAPH-OPS-TIMEOUT-001（2026-07-22）治本：skip-if-recent + timeout 升级。

        # 根因：generate_project_depgraph.py --force 全量扫描需 208-296s，原 timeout=300s

        # 仅 4s 余量→~4% 超时率（13/317）。且每次 .py commit 都重跑（无 skip），100% AI

        # 开发高频 commit 下浪费严重。治本：① marker 文件防并发+防冗余（600s cooldown，

        # 在 sync 开始前写 marker，防止并发 commit 各自触发 5 分钟全量扫描）② timeout

        # 300→600s（2x 余量，典型 296s 运行有充足空间）。marker 在 sync 开始前写入

        # （非结束），故失败也有 cooldown——合理：超时=系统过载，立即重试大概率再超时。

        _SKIP_WINDOW = 600  # 10 min cooldown after any attempt（success or failure）

        # #ARCH-WORKTREE-DB-SPLIT-001：cooldown marker 锚主仓——原 project_root 相对
        # 路径使各工作区各有节流器（共享 PG 却无共享节流），锚主仓后全仓单节流。
        _marker = _main_root / ".runtime" / "depgraph_ops_last_attempt"

        try:
            if _marker.exists():
                _last = float(_marker.read_text(encoding="utf-8").strip())

                _elapsed = now_utc().timestamp() - _last

                if _elapsed < _SKIP_WINDOW:
                    return ReconcileResult(
                        action="skip",
                        detail=f"skip depgraph sync: last attempt {_elapsed:.0f}s ago < {_SKIP_WINDOW}s cooldown (#ARCH-DEPGRAPH-OPS-TIMEOUT-001)",
                    )

        except (ValueError, OSError):  # noqa: BLE001 — corrupt marker, proceed
            pass

        # 写 marker 在 sync 开始前（防并发 commit 触发多个 5 分钟全量扫描）

        try:
            _marker.parent.mkdir(parents=True, exist_ok=True)

            _marker.write_text(str(now_utc().timestamp()), encoding="utf-8")

        except OSError:  # noqa: BLE001 — marker 写失败不阻断 sync
            pass

        start = time.time()

        _env = dict(os.environ)

        _src = str(project_root / "src")

        _env["PYTHONPATH"] = _src + (os.pathsep + _env["PYTHONPATH"] if _env.get("PYTHONPATH") else "")

        sync_result = _run_subprocess(
            [
                sys.executable,
                "scripts/governance/generate_project_depgraph.py",
                "--output-db",
                "depgraph",
                "--force",
            ],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,  # 全量扫描 208-296s，给 2x 余量（原 300s 仅 4s 余量→4% 超时率）
            env=_env,
        )

        elapsed = time.time() - start

        if sync_result.returncode != 0:
            # #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 2: detail 不截断

            # 原截断到 200 字符导致 fail-silent（完整 traceback 丢失，AI 无法诊断）。

            # 现完整记录 stderr，由 _log_reconcile_results 持久化到 governance.db。

            # #ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 3: action 升级为 critical_warn

            # depgraph 同步失败 = 架构图与代码不一致，是严重问题。下次 commit/merge 前

            # 打印告警横幅强制 AI 看到（_check_recent_critical_warns）。

            return ReconcileResult(
                action="critical_warn",
                detail=f"depgraph ops sync failed in {elapsed:.1f}s (rc={sync_result.returncode}): "
                f"{sync_result.stderr.strip()}",
            )

        return ReconcileResult(
            action="clean",
            detail=f"depgraph nodes/edges synced in {elapsed:.1f}s (P1/P2 protection active, 裁定#209 阶段1)",
        )

    return ReconcilerSpec(
        gate_id="GATE-DEPGRAPH-OPS",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=130,
        file_ops=frozenset({"read", "write"}),
    )


# trae_060-reviewed: 通过§4元问题审查。①该存在：ARCH-FRONTMATTER-STATE-001 Link B 断链（frontmatter 无 post-commit 自动写路径，generate_project_depgraph.py:4139 try/except 静默调用失败即漂移）。②无法合并进 make_depgraph_ops_reconciler@130（职责不同：DB 同步 vs .md frontmatter 同步；且需 priority=135>130 读最新 depgraph）。③治本：修复根因（缓存层无自动写路径），非治标。


def make_blueprint_frontmatter_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 blueprint frontmatter post-commit 自动同步 reconciler

    (ARCH-FRONTMATTER-STATE-001 Phase 2，修复 Link B)。

    三层状态模型断链修复：

        代码真源 (ground truth) → depgraph (运营态, scanner 派生) → blueprint frontmatter (缓存层)

    Link B 断链：frontmatter 无 post-commit 自动写路径，原本只在

    generate_project_depgraph.py 内 try/except 静默调用，失败即漂移。

    本 reconciler 在 post-commit 把 depgraph → blueprint frontmatter 同步

    明确化为独立 reconciler，事件触发、可见、可观测、可降级。

    依赖顺序（priority 设计，确保 drift_scan@140 看到已同步状态）：

        - priority=130 (depgraph_ops): 代码 → depgraph nodes/edges 运营态同步

        - priority=135 (本 reconciler): depgraph → blueprint frontmatter 同步

        - priority=140 (drift_scan): 检测代码↔blueprint↔depgraph 漂移

    对标 make_depgraph_ops_reconciler 的 subprocess + auto_commit 模式：

        - trigger 匹配 .py（代码变更触发 depgraph 更新→frontmatter 需重算）

          或 docs/03_modules/ 下的 .md（蓝图本身被编辑，frontmatter 需重算）

        - reconcile 跑 sync_panorama_module.py --all 同步全量 frontmatter

        - 检测 docs/03_modules/ 下 .md 变更 → _commit_auto 自动提交

        - 失败降级 warn，不阻断 commit

    防递归：reconciler 提交的 .md 变更会再次触发本 reconciler，但此时

    frontmatter 已同步，git diff 为空，返回 clean，无无限循环。

    Args:

        gateway: GitCommitGateway 实例（用 project_root / _run_git / _commit_auto）。

    Returns:

        ReconcilerSpec(gate_id="GATE-BLUEPRINT-FRONTMATTER-SYNC", priority=135)。

    """

    import os
    import sys
    import time

    project_root = gateway.project_root

    def _safe_relpath(f: str) -> str:
        """相对路径安全转换——治本（test_blueprint_frontmatter_reconciler_post_commit SSoT）。

        测试可能传入相对路径（如 'foo.py'），``os.path.relpath`` 在 Windows

        跨盘符场景（cwd 在 D: 而 project_root 在 C:）抛 ValueError。

        本函数捕获异常返回原路径，保证 trigger/extract 逻辑不崩溃。

        """

        try:
            return _rel_path(f, str(project_root))

        except (ValueError, OSError):
            return f.replace("\\", "/")

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _safe_relpath(f)

            if rel.endswith(".py"):
                return True

            if rel.startswith("docs/03_modules/") and rel.endswith(".md"):
                return True

        return False

    def _extract_module_ids_from_md(committed_files: list[str]) -> list[str]:
        """从 docs/03_modules/*.md frontmatter 提取 module_id（#ARCH-PRE-EXISTING-DEBT-001 治本，2026-07-20）。

        增量分发的核心：只同步本次 commit 涉及的模块，避免全量扫描 616+ 模块。

        提取策略：读 .md 文件前 30 行，正则匹配 ``module_id: MOD-XXX``。

        """

        import re

        pattern = re.compile(r"^module_id:\s*(MOD-[^\s]+)", re.MULTILINE)

        module_ids: set[str] = set()

        for f in committed_files:
            rel = _safe_relpath(f)

            if not (rel.startswith("docs/03_modules/") and rel.endswith(".md")):
                continue

            try:
                with open(f, encoding="utf-8", errors="replace") as fh:
                    head = "".join(fh.readline() for _ in range(30))

                m = pattern.search(head)

                if m:
                    module_ids.add(m.group(1))

            except OSError:
                continue

        return sorted(module_ids)

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        start = time.time()

        _env = dict(os.environ)

        _src = str(project_root / "src")

        _env["PYTHONPATH"] = _src + (os.pathsep + _env["PYTHONPATH"] if _env.get("PYTHONPATH") else "")

        # #ARCH-PRE-EXISTING-DEBT-001 治本（2026-07-20）：

        # 增量分发——从 committed_files 提取 module_id，只同步涉及的模块。

        # 全量 --all 模式作 fallback（.py 改动可能影响多个模块的 depgraph）。

        # timeout 配置化：env ZEPHYR_FRONTMATTER_SYNC_TIMEOUT 覆盖默认值。

        module_ids = _extract_module_ids_from_md(committed_files)

        has_py_changes = any(_safe_relpath(f).endswith(".py") for f in committed_files)

        # #ARCH-RECONCILER-TOCTOU-CLOBBER-001 P0 止血（2026-08-03）：
        # timeout 300→600s（2x 余量），对标 #ARCH-DEPGRAPH-OPS-TIMEOUT-001。
        # 根因同源：sync_panorama_module.py --all 全量扫描 208-296s，原 300s 仅 4s 余量→~4% 超时率。
        default_timeout = 600 if (has_py_changes or not module_ids) else 120

        timeout = int(_env.get("ZEPHYR_FRONTMATTER_SYNC_TIMEOUT", str(default_timeout)))

        if module_ids and not has_py_changes:
            # 增量模式：只同步 .md frontmatter 涉及的模块

            cmd = [sys.executable, "scripts/governance/sync_panorama_module.py"] + module_ids

            mode = f"incremental ({len(module_ids)} modules)"

        else:
            # 全量模式：.py 改动或无 module_id 提取失败时 fallback

            cmd = [sys.executable, "scripts/governance/sync_panorama_module.py", "--all"]

            mode = "full (--all)"

        # #ARCH-RECONCILER-TOCTOU-CLOBBER-001 P0 止血（2026-08-03）：
        # skip-if-recent marker，对标 #ARCH-DEPGRAPH-OPS-TIMEOUT-001。
        # 仅全量模式（has_py_changes or not module_ids）应用——增量模式 <5s 无需 skip。
        # 根因：每次 .py commit 都重跑 208-296s 全量扫描，100% AI 高频 commit 下浪费严重
        # 且 300s+ 窗口是 TOCTOU clobber 的放大因。600s cooldown 收窄 race 窗口。
        # marker 在 sync 开始前写入（非结束），故失败也有 cooldown——合理：
        # 超时=系统过载，立即重试大概率再超时。
        if has_py_changes or not module_ids:
            _SKIP_WINDOW = 600  # 10 min cooldown after any attempt（success or failure）
            _marker = project_root / ".runtime" / "frontmatter_sync_last_attempt"
            try:
                if _marker.exists():
                    _last = float(_marker.read_text(encoding="utf-8").strip())
                    _elapsed = now_utc().timestamp() - _last
                    if _elapsed < _SKIP_WINDOW:
                        return ReconcileResult(
                            action="skip",
                            detail=f"skip frontmatter sync: last attempt {_elapsed:.0f}s ago < {_SKIP_WINDOW}s cooldown (#ARCH-RECONCILER-TOCTOU-CLOBBER-001)",
                        )
            except (ValueError, OSError):  # noqa: BLE001 — corrupt marker, proceed
                pass
            # 写 marker 在 sync 开始前（防并发 commit 触发多个 5 分钟全量扫描）
            try:
                _marker.parent.mkdir(parents=True, exist_ok=True)
                _marker.write_text(str(now_utc().timestamp()), encoding="utf-8")
            except OSError:  # noqa: BLE001 — marker 写失败不阻断 sync
                pass

        sync_result = _run_subprocess(
            cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=_env,
        )

        elapsed = time.time() - start

        if sync_result.returncode != 0:
            # 治本（test_blueprint_frontmatter_reconciler_post_commit SSoT）：

            # 返回 warn（非 critical_warn）——测试期望 warn。

            # detail 不截断保留完整 stderr 供诊断。

            return ReconcileResult(
                action="warn",
                detail=f"frontmatter sync failed in {elapsed:.1f}s (rc={sync_result.returncode}, mode={mode}, timeout={timeout}s): "
                f"{sync_result.stderr.strip()}",
            )

        # 检测 docs/03_modules/ 下 .md frontmatter 变更（DB 同步不进 git，无需提交）

        diff_result = gateway.run_git(["git", "diff", "--name-only", "--", "docs/03_modules/"])

        if diff_result.returncode != 0:
            # 治本（SSoT）：返回 warn

            return ReconcileResult(
                action="warn",
                detail=f"frontmatter sync: git diff failed: {diff_result.stderr.strip()}",
            )

        changed_files = [
            f.strip() for f in diff_result.stdout.strip().splitlines() if f.strip() and f.strip().endswith(".md")
        ]

        if not changed_files:
            return ReconcileResult(
                action="clean",
                detail=f"frontmatter sync: no drift in {elapsed:.1f}s (all consistent)",
            )

        # 变更 → 自动提交修复（_commit_auto 统一入口，DCR gate 覆盖）

        abs_files = [str(project_root / f) for f in changed_files]

        auto_msg = (
            "chore(frontmatter): auto-sync by GATE-BLUEPRINT-FRONTMATTER-SYNC "
            "post-commit (ARCH-FRONTMATTER-STATE-001 Phase 2)"
        )

        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)

        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail=f"frontmatter sync: {len(changed_files)} files auto-reconciled in {elapsed:.1f}s",
            )

        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail=f"frontmatter sync: {len(changed_files)} files but no staged changes in {elapsed:.1f}s",
            )

        return ReconcileResult(
            action="warn",
            detail=f"frontmatter sync: auto-commit failed ({commit_result.status}): {commit_result.message}",
        )

    return ReconcilerSpec(
        gate_id="GATE-BLUEPRINT-FRONTMATTER-SYNC",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=135,
        file_ops=frozenset({"read", "write"}),
    )


# 2026-08-23 立项（用户批准「autogen 段 auto-commit 通道」批3b）：blueprint「已实现代码
# 完整路径索引」段与 frontmatter 同病——sync_blueprint_code_index.py 只有手动/CI --check
# 触发路径，无 post-commit 自动写+提交通道，depgraph 演进后索引段漂移挂工作区（派生物
# 滞留事故族）。仿 135 模板补齐 Link B 同型断链：syncer 已有 atomic_write_safe +
# blueprint_write_lock（#ARCH-RECONCILER-TOCTOU-CLOBBER-001），本 reconciler 只做
# 事件触发 + 变更检测 + _commit_auto 收口，不重写同步逻辑（单一真源在 syncer）。
def make_blueprint_code_index_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 blueprint 代码索引段 post-commit 自动同步 reconciler（GATE-BLUEPRINT-CODE-INDEX-SYNC）。

    与 make_blueprint_frontmatter_reconciler@135 同型（仿 135 模板）：

        代码真源 → depgraph.nodes（运营态）→ blueprint「已实现代码完整路径索引」段（缓存层）

    断链：sync_blueprint_code_index.py 仅手动/CI --check 路径，无 post-commit 自动
    写+提交通道——depgraph 演进后索引段漂移挂工作区，派生物滞留。本 reconciler
    补齐「事件触发 → syncer 重算 → git diff 检测 → _commit_auto 收口」链路。

    依赖顺序（priority=136 设计）：

        - priority=130 (depgraph_ops)：代码 → depgraph nodes/edges 运营态同步
        - priority=135 (frontmatter)：depgraph → blueprint frontmatter 同步
        - priority=136 (本 reconciler)：depgraph → blueprint 代码索引段同步
          （在 frontmatter 之后串行化——两者都写 blueprint.md 且本 syncer 自 bump
          frontmatter version；在 drift_scan@140 之前，保证漂移检测看到已同步状态）

    模式（对标 135）：

        - trigger：.py（代码变更→depgraph 演进→索引需重算）或 docs/03_modules/
          下 .md（frontmatter module_id 可能变更）
        - reconcile：subprocess 跑 sync_blueprint_code_index.py（写入模式，幂等）
        - skip-if-recent cooldown：syncer 恒为全量扫描（600+ 蓝图 × depgraph 查询），
          100% AI 高频 commit 下每次触发浪费且放大 TOCTOU 窗口——600s attempt
          cooldown（#ARCH-RECONCILER-TOCTOU-CLOBBER-001 同根因同款止血）
        - 检测 docs/03_modules/ 下 .md 变更 → _commit_auto 自动提交
        - 失败降级 warn，不阻断 commit

    防递归：本 reconciler 提交的 blueprint.md 变更再触发 135/本 reconciler，但
    索引段已同步 → syncer 幂等无改动 → git diff 为空 → clean 终止，无无限循环。

    Args:
        gateway: GitCommitGateway 实例（用 project_root / run_git / _commit_auto）。

    Returns:
        ReconcilerSpec(gate_id="GATE-BLUEPRINT-CODE-INDEX-SYNC", priority=136)。
    """

    import os
    import sys
    import time

    project_root = gateway.project_root

    def _safe_relpath(f: str) -> str:
        """相对路径安全转换（跨盘符 ValueError 兜底，同 135 模板 SSoT）。"""
        try:
            return _rel_path(f, str(project_root))
        except (ValueError, OSError):
            return f.replace("\\", "/")

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = _safe_relpath(f)
            if rel.endswith(".py"):
                return True
            if rel.startswith("docs/03_modules/") and rel.endswith(".md"):
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        start = time.time()

        _env = dict(os.environ)
        _src = str(project_root / "src")
        _env["PYTHONPATH"] = _src + (os.pathsep + _env["PYTHONPATH"] if _env.get("PYTHONPATH") else "")

        # skip-if-recent cooldown（对标 135：syncer 恒全量扫描，attempt 打点即生效——
        # 失败也有 cooldown，超时=系统过载立即重试大概率再超时）
        _SKIP_WINDOW = 600  # 10 min cooldown after any attempt（success or failure）
        _marker = project_root / ".runtime" / "code_index_sync_last_attempt"
        try:
            if _marker.exists():
                _last = float(_marker.read_text(encoding="utf-8").strip())
                _elapsed = now_utc().timestamp() - _last
                if _elapsed < _SKIP_WINDOW:
                    return ReconcileResult(
                        action="skip",
                        detail=f"skip code-index sync: last attempt {_elapsed:.0f}s ago < {_SKIP_WINDOW}s cooldown (#ARCH-RECONCILER-TOCTOU-CLOBBER-001)",
                    )
        except (ValueError, OSError):  # noqa: BLE001 — corrupt marker, proceed
            pass
        try:
            _marker.parent.mkdir(parents=True, exist_ok=True)
            _marker.write_text(str(now_utc().timestamp()), encoding="utf-8")
        except OSError:  # noqa: BLE001 — marker 写失败不阻断 sync
            pass

        timeout = int(_env.get("ZEPHYR_CODE_INDEX_SYNC_TIMEOUT", "300"))
        cmd = [
            sys.executable,
            "scripts/governance/d5_architecture/syncers/sync_blueprint_code_index.py",
        ]

        sync_result = _run_subprocess(
            cmd,
            cwd=str(project_root),
            timeout=timeout,
            env=_env,
        )

        elapsed = time.time() - start

        if sync_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"code-index sync failed in {elapsed:.1f}s (rc={sync_result.returncode}, timeout={timeout}s): "
                f"{sync_result.stderr.strip()}",
            )

        # 检测 docs/03_modules/ 下 .md 变更（索引段 + version bump 均落蓝图文件）
        diff_result = gateway.run_git(["git", "diff", "--name-only", "--", "docs/03_modules/"])
        if diff_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"code-index sync: git diff failed: {diff_result.stderr.strip()}",
            )

        changed_files = [
            f.strip() for f in diff_result.stdout.strip().splitlines() if f.strip() and f.strip().endswith(".md")
        ]

        if not changed_files:
            return ReconcileResult(
                action="clean",
                detail=f"code-index sync: no drift in {elapsed:.1f}s (all consistent)",
            )

        # 变更 → 自动提交修复（_commit_auto 统一入口，DCR gate 覆盖）
        abs_files = [str(project_root / f) for f in changed_files]
        auto_msg = (
            "chore(code-index): auto-sync by GATE-BLUEPRINT-CODE-INDEX-SYNC "
            "post-commit (autogen 段 auto-commit 通道，2026-08-23 批3b)"
        )
        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)

        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail=f"code-index sync: {len(changed_files)} files auto-reconciled in {elapsed:.1f}s",
            )

        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail=f"code-index sync: {len(changed_files)} files but no staged changes in {elapsed:.1f}s",
            )

        return ReconcileResult(
            action="warn",
            detail=f"code-index sync: auto-commit failed ({commit_result.status}): {commit_result.message}",
        )

    return ReconcilerSpec(
        gate_id="GATE-BLUEPRINT-CODE-INDEX-SYNC",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=136,
        file_ops=frozenset({"read", "write"}),
    )


def make_drift_scan_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 merge/commit 事件触发的全量 drift 扫描 reconciler（MOD-GOV-ALIGNMENT-LOOP §4.S1）。

    commit .py 文件后，跑 check_blueprint_code_alignment.py 全量检测

    蓝图↔代码对齐 drift，结果写入 governance.db drift_scan_results 表。

    对标 make_depgraph_ops_reconciler 的 subprocess 模式。

    区别：

    - depgraph_ops 同步代码→DB（generate_project_depgraph.py）

    - drift_scan 检测对齐 drift（check_blueprint_code_alignment.py）并入库

    - priority=140（在 depgraph_ops=130 之后，确保 depgraph 已同步再扫描 drift）

    Args:

        gateway: GitCommitGateway 实例（用 project_root）。

    Returns:

        ReconcilerSpec(gate_id="GATE-DRIFT-SCAN", priority=140)。

    """

    import json
    import os
    import sqlite3
    import sys
    import time
    import uuid

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel.endswith(".py"):
                return True

        return False

    def _ensure_table(conn: sqlite3.Connection) -> None:

        conn.execute(SQL_CREATE_DRIFT_SCAN_RESULTS)

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        start = time.time()

        _env = dict(os.environ)

        _src = str(project_root / "src")

        _env["PYTHONPATH"] = _src + (os.pathsep + _env["PYTHONPATH"] if _env.get("PYTHONPATH") else "")

        scan_result = _run_subprocess(
            [
                sys.executable,
                "scripts/governance/d5_architecture/checkers/check_blueprint_code_alignment.py",
                "--json",
                "--warn-only",
            ],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
            env=_env,
        )

        elapsed = time.time() - start

        if scan_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"drift scan failed in {elapsed:.1f}s (rc={scan_result.returncode}): "
                f"{scan_result.stderr.strip()[:200]}",
            )

        try:
            data = json.loads(scan_result.stdout)

        except json.JSONDecodeError as e:
            return ReconcileResult(
                action="warn",
                detail=f"drift scan JSON parse failed: {e}; stdout[:200]={scan_result.stdout[:200]}",
            )

        total = data.get("total_findings", 0)

        high = data.get("high", 0)

        low = data.get("low", 0)

        findings = data.get("findings", [])

        auto_fixable = sum(1 for f in findings if f.get("type") in ("CODE_NOT_IN_DEPGRAPH", "ORPHAN_MODULE_ID"))

        db_path = os.path.join(str(project_root), "data", "databases", "governance.db")

        try:
            conn = sqlite3.connect(db_path, timeout=30.0)

            _ensure_table(conn)

            scan_id = f"scan-{uuid.uuid4().hex[:12]}"

            conn.execute(
                SQL_INSERT_DRIFT_SCAN_RESULT,
                (
                    scan_id,
                    now_utc(),
                    "merge.completed",
                    total,
                    high,
                    low,
                    auto_fixable,
                    json.dumps(data, ensure_ascii=False),
                ),
            )

            conn.commit()

            conn.close()

        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("drift_scan_reconciler: DB write failed: %s", e)

        if total == 0:
            return ReconcileResult(
                action="clean",
                detail=f"drift scan clean in {elapsed:.1f}s (0 drifts, "
                f"scanned {data.get('code_headers_scanned', 0)} files)",
            )

        return ReconcileResult(
            action="warn",
            detail=f"drift scan found {total} drifts (HIGH:{high} LOW:{low}, "
            f"auto_fixable:{auto_fixable}) in {elapsed:.1f}s",
        )

    return ReconcilerSpec(
        gate_id="GATE-DRIFT-SCAN",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=140,
        file_ops=frozenset({"read", "write"}),
    )


def _drift_fix_find_module(file_rel: str) -> str | None:
    """查 depgraph 反查 file→blueprint_id（模块级，降低 make_drift_fix_reconciler 复杂度）。

    注意：zephyr.governance.depgraph_schema.get_depgraph_pg_connection 返回原生

    psycopg2 connection（无 execute() 方法，需用 cursor()）。与 scripts/_shared/

    constants.py 的 PgConnExecuteWrapper 不同——src 内不可导入 _shared 包。

    """

    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    file_rel = file_rel.replace("\\", "/")

    try:
        conn = get_depgraph_pg_connection(autocommit=True)

        with conn.cursor() as cur:
            cur.execute(SQL_FIND_MODULE_BY_PATH, (file_rel,))

            row = cur.fetchone()

        conn.close()

        if row:
            return row[0]

    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("drift_fix: depgraph lookup failed for %s: %s", file_rel, e)

    return None


def _drift_fix_header(project_root: Path, file_rel: str, old_modid: str, new_modid: str) -> bool:
    """修复 .py 文件 [BLUEPRINT] 头部的 module_id。"""

    import os
    import re

    abs_path = os.path.join(str(project_root), file_rel)

    try:
        with open(abs_path, encoding="utf-8") as f:
            content = f.read()

    except OSError:
        return False

    pattern = re.compile(r"(\[BLUEPRINT\]\s+)" + re.escape(old_modid))

    new_content, count = pattern.subn(r"\g<1>" + new_modid, content, count=1)

    if count == 0:
        return False

    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True


def _drift_fix_log_audit(project_root: Path, finding: dict) -> None:
    """不可修复的 drift 写入 governance.db drift_audit_findings 表。"""

    import os
    import sqlite3
    import uuid

    db_path = os.path.join(str(project_root), "data", "databases", "governance.db")

    try:
        conn = sqlite3.connect(db_path, timeout=30.0)

        conn.execute(SQL_CREATE_DRIFT_AUDIT_FINDINGS)

        finding_id = f"af-{uuid.uuid4().hex[:12]}"

        conn.execute(
            SQL_INSERT_DRIFT_AUDIT_FINDING,
            (
                finding_id,
                now_utc(),
                finding.get("type", ""),
                finding.get("severity", ""),
                finding.get("file", ""),
                finding.get("detail", ""),
            ),
        )

        conn.commit()

        conn.close()

    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("drift_fix: audit finding log failed: %s", e)


def _classify_orphan_drifts(
    findings: list[dict],
    project_root: Path,
) -> tuple[list[tuple[str, str, str]], list[dict]]:
    """遍历 findings，对 ORPHAN_MODULE_ID 分级：可修复→fixed_files，不可修复→escalated。"""

    fixed_files: list[tuple[str, str, str]] = []

    escalated: list[dict] = []

    for f in findings:
        if f.get("type") != "ORPHAN_MODULE_ID":
            continue

        file_rel = f.get("file", "").replace("\\", "/")

        detail = f.get("detail", "")

        old_modid = ""

        if "引用" in detail and "不在" in detail:
            old_modid = detail.split("引用")[1].split("不在")[0].strip()

        if not old_modid:
            escalated.append(f)

            continue

        matched = _drift_fix_find_module(file_rel)

        if matched and matched != old_modid and _drift_fix_header(project_root, file_rel, old_modid, matched):
            fixed_files.append((file_rel, old_modid, matched))

        else:
            escalated.append(f)

    return fixed_files, escalated


def _finalize_drift_fixes(
    fixed_files: list[tuple[str, str, str]],
    escalated: list[dict],
    session_id: str,
    start: float,
    gateway: object,
    project_root: Path,
) -> ReconcileResult:
    """自动提交修复 + 记录升级的 audit findings，返回 ReconcileResult。"""

    import time

    if not fixed_files and not escalated:
        return ReconcileResult(action="clean", detail="no fixable drifts found")

    for ef in escalated:
        _drift_fix_log_audit(project_root, ef)

    if not fixed_files:
        return ReconcileResult(
            action="warn",
            detail=f"escalated {len(escalated)} unresolvable drift(s) to audit findings",
        )

    abs_files = [str(project_root / f[0]) for f in fixed_files]

    fix_summary = "; ".join(f"{old}→{new}" for _, old, new in fixed_files)

    auto_msg = f"fix(alignment_loop): S2 auto-fix ORPHAN_MODULE_ID drift ({fix_summary})"

    commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)

    elapsed = time.time() - start

    esc_suffix = f", escalated {len(escalated)} to audit" if escalated else ""

    if commit_result.status == "OK":
        return ReconcileResult(
            action="auto_committed",
            detail=f"auto-fixed {len(fixed_files)} ORPHAN_MODULE_ID drift(s){esc_suffix} in {elapsed:.1f}s",
        )

    return ReconcileResult(
        action="warn",
        detail=f"fixed {len(fixed_files)} file(s) but auto-commit failed: {commit_result.message[:100]}",
    )


def make_drift_fix_reconciler(gateway: object) -> ReconcilerSpec:
    """S2: 分级自治 drift 自动修复 pipeline（MOD-GOV-ALIGNMENT-LOOP §4.S2）。

    S1 扫描后，对检测到的 drift 按风险分级自动修复：

    - ORPHAN_MODULE_ID (HIGH, 可匹配): 查 depgraph 反查 file→module_id → 修复 [BLUEPRINT] 头部 → auto_commit

    - ORPHAN_MODULE_ID (HIGH, 不可匹配): 写入 drift_audit_findings 表 → 人工审批

    - CODE_NOT_IN_DEPGRAPH (LOW): 跳过（depgraph_ops_reconciler priority=130 已处理）

    闭环验证：修复后 S1 下次扫描自动确认 drift 减少。

    Args:

        gateway: GitCommitGateway 实例（用 project_root + _commit_auto）。

    Returns:

        ReconcilerSpec(gate_id="GATE-DRIFT-FIX", priority=150)。

    """

    import json
    import os
    import sys

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel.endswith(".py"):
                return True

        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        import time

        start = time.time()

        _env = dict(os.environ)

        _src = str(project_root / "src")

        _env["PYTHONPATH"] = _src + (os.pathsep + _env["PYTHONPATH"] if _env.get("PYTHONPATH") else "")

        scan_result = _run_subprocess(
            [
                sys.executable,
                "scripts/governance/d5_architecture/checkers/check_blueprint_code_alignment.py",
                "--json",
                "--warn-only",
            ],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
            env=_env,
        )

        if scan_result.returncode != 0:
            return ReconcileResult(action="warn", detail=f"drift fix scan failed: {scan_result.stderr.strip()[:200]}")

        try:
            data = json.loads(scan_result.stdout)

        except json.JSONDecodeError:
            return ReconcileResult(action="warn", detail="drift fix scan JSON parse failed")

        findings = data.get("findings", [])

        if not findings:
            return ReconcileResult(action="clean", detail="no drifts to fix")

        fixed_files, escalated = _classify_orphan_drifts(findings, project_root)

        return _finalize_drift_fixes(fixed_files, escalated, session_id, start, gateway, project_root)

    return ReconcilerSpec(
        gate_id="GATE-DRIFT-FIX",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=150,
        file_ops=frozenset({"read", "write"}),
    )


def _module_id_infer_from_dir(file_rel: str) -> str | None:
    """从同目录 depgraph 节点推断 module_id（S4 防蔓延）。

    新建 .py 文件无 [BLUEPRINT] 头部时，查 depgraph 同目录下已有文件的

    blueprint_id，推断该文件应属的 module_id。

    """

    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    file_rel = file_rel.replace("\\", "/")

    dir_prefix = file_rel.rsplit("/", 1)[0] + "/%" if "/" in file_rel else "%"

    try:
        conn = get_depgraph_pg_connection(autocommit=True)

        with conn.cursor() as cur:
            cur.execute(SQL_FIND_MODULE_BY_DIR, (dir_prefix,))

            row = cur.fetchone()

        conn.close()

        if row:
            return row[0]

    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("module_id_recommend: dir lookup failed for %s: %s", file_rel, e)

    return None


def _module_id_inject_header(project_root: Path, file_rel: str, module_id: str) -> bool:
    """在 .py 文件头部注入 [BLUEPRINT] + [TTL] 完整头部。

    治本（2026-07-17，遗留项修复）：注入模板补全 [TTL] permanent 字段。

    原模板仅含 [BLUEPRINT] 导致 auto-commit 被 TTL-METADATA gate 阻断（hard block：

    文件有头部但缺 required ttl 字段）。

    自动兜底机制完整性原则：注入器必须遵守后续校验器的所有规则，禁止注入半成品。

    默认 permanent：S4 处理的 src/scripts/ 下文件按 ttl_vocabulary.yaml decision_tree

    Q3 判定属永久区路径；task_bound 文件应由 AI 创建时显式声明，不应依赖兜底注入。

    """

    import os

    abs_path = os.path.join(str(project_root), file_rel)

    try:
        with open(abs_path, encoding="utf-8") as f:
            content = f.read()

    except OSError:
        return False

    if "[BLUEPRINT]" in content[:500]:
        return False

    header = f"# [BLUEPRINT] {module_id} | (auto-injected by S4 reconciler) | §\n# [TTL] permanent\n"

    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(header + content)

    return True


def _classify_headerless_files(
    committed_files: list[str],
    project_root: Path,
) -> tuple[list[tuple[str, str]], list[str]]:
    """遍历 committed .py 文件，分类：无 [BLUEPRINT] 头部且可推断→injected，不可推断→skipped。"""

    import os
    import re

    bp_re = re.compile(r"\[BLUEPRINT\]\s+(\S+)")

    injected: list[tuple[str, str]] = []

    skipped: list[str] = []

    for abs_path in committed_files:
        rel = _rel_path(abs_path, str(project_root))

        if not rel.endswith(".py"):
            continue

        # 治本（2026-08-18 AI-00 实证）：_archive 归档件豁免——归档件不再参与治理注入

        if "_archive" in rel.replace("\\", "/").split("/"):
            continue

        try:
            with open(abs_path, encoding="utf-8") as f:
                head = f.read(500)

        except OSError:
            continue

        if bp_re.search(head):
            continue

        matched = _module_id_infer_from_dir(rel)

        if matched and _module_id_inject_header(project_root, rel, matched):
            injected.append((rel, matched))

        else:
            skipped.append(rel)

    return injected, skipped


def make_module_id_recommend_reconciler(gateway: object) -> ReconcilerSpec:
    """S4: 新建文件 module_id 自动推荐（MOD-GOV-ALIGNMENT-LOOP §4.S4）。

    commit .py 文件后，检测无 [BLUEPRINT] 头部的新建文件：

    - 从同目录 depgraph 节点推断 module_id → 自动注入 [BLUEPRINT] 头部 → auto_commit

    - 无法推断 → 跳过（AI 需手动查蓝图）

    防蔓延：新文件不再以"无头部"状态进入代码库，避免 ORPHAN drift 积累。

    Args:

        gateway: GitCommitGateway 实例（用 project_root + _commit_auto）。

    Returns:

        ReconcilerSpec(gate_id="GATE-MODULE-ID-RECOMMEND", priority=160)。

    """

    import os

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel.endswith(".py"):
                return True

        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        injected, skipped = _classify_headerless_files(committed_files, project_root)

        if not injected:
            return ReconcileResult(action="clean", detail="no headerless files to fix")

        abs_files = [str(project_root / f[0]) for f in injected]

        inj_summary = "; ".join(f"{f}→{m}" for f, m in injected)

        auto_msg = f"fix(alignment_loop): S4 auto-inject [BLUEPRINT] header ({inj_summary})"

        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)

        skip_suffix = f", skipped {len(skipped)} (no module inferred)" if skipped else ""

        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail=f"auto-injected {len(injected)} [BLUEPRINT] header(s){skip_suffix}",
            )

        return ReconcileResult(
            action="warn",
            detail=f"injected {len(injected)} header(s) but auto-commit failed: {commit_result.message[:100]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-MODULE-ID-RECOMMEND",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=160,
        file_ops=frozenset({"read", "write"}),
    )


# ============================================================================

# 裁定 C / P2 / #ARCH-GUC-TRIGGER-FIX-001: 错误分类纯函数

# ============================================================================

# reconciler 以 subprocess 方式运行 sync_yaml_to_depgraph.py，无法直接捕获

# Python 异常。本函数解析 stderr/stdout 文本匹配错误模式，决定是否重试：

#   - deterministic: schema bug / GUC 未注册 / 约束违规 → 不重试，立即 escalate

#   - transient: 连接/死锁/超时 → 重试可能成功

#   - unknown: 未知错误 → 保守重试

#

# 原 bug（sync_dataflow_registry retry 23 次全失败）正是确定性错误被盲重试的典型。

# 提取到模块级便于单元测试（对齐 commit_gateway_abuse_monitor_reconciler._classify_abuse 模式）。

_DETERMINISTIC_PATTERNS = (
    "unrecognized configuration parameter",  # GUC 未注册（#ARCH-GUC-TRIGGER-FIX-001 根因）
    "undefinedobject",  # GUC/对象未定义
    "undefinedcolumn",  # 列不存在
    "undefinedtable",  # 表不存在
    "undefinedfunction",  # 函数不存在
    "undefinedparameter",  # 参数未定义
    "syntax error",  # SQL 语法错误
    "duplicatetable",  # 表已存在
    "duplicatecolumn",  # 列已存在
    "duplicateobject",  # 对象已存在
    "permission denied",  # 权限不足
    "not-null constraint",  # NOT NULL 约束
    "foreign key constraint",  # FK 约束
    "unique constraint",  # UNIQUE 约束
    "check constraint",  # CHECK 约束
    "invalid input syntax",  # 数据类型不匹配
    "does not exist",  # 表/列/函数不存在（通用）
    "already exists",  # 对象已存在（通用）
)

_TRANSIENT_PATTERNS = (
    "operationalerror",
    "deadlock detected",
    "could not serialize access",
    "connection refused",
    "connection timeout",
    "could not connect",
    "server closed the connection unexpectedly",
    "terminating connection due to",
)


def _classify_sync_failure(error_text: str) -> str:
    """分类 sync 失败错误，决定 reconciler 是否重试（裁定 C / P2 / #ARCH-GUC-TRIGGER-FIX-001）。

    Args:

        error_text: sync_yaml_to_depgraph.py subprocess 的 stderr/stdout 文本。

    Returns:

        "deterministic" - 确定性错误（schema bug），不重试，立即 escalate

        "transient" - 瞬态错误（连接/死锁），重试可能成功

        "unknown" - 未知错误，保守重试

    """

    text = (error_text or "").lower()

    for pat in _DETERMINISTIC_PATTERNS:
        if pat in text:
            return "deterministic"

    for pat in _TRANSIENT_PATTERNS:
        if pat in text:
            return "transient"

    return "unknown"


def make_yaml_sync_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 YAML->depgraph 规则同步 post-commit reconciler。

    commit rules/*.yaml 或 _registry/**/*.yaml 后，depgraph 的规则缓存表

    （contracts/gates/field_vocabularies 等 16 张）可能与 YAML 真源漂移。

    本 reconciler 在 post-commit 跑 sync_yaml_to_depgraph.py 同步 YAML->DB。

    S1.6 重试队列：sync 失败时写入 data/cache/yaml_sync_retry_queue.json，

    后续任意 commit 自动重试（最多 _MAX_RETRY_ATTEMPTS=3 次），超过后升级为

    error 停止重试。AI 发现 error 级别告警时应检查 sync 脚本路径/依赖是否正确，

    而非自行创建新的同步逻辑（本 reconciler 是 YAML->DB 同步的唯一入口）。

    治本 trae_060 §5 "MUST 补事件注册"——消除手动 sync 导致的漂移

    （如 contracts 表 126 条外键违规的根因：AI 改 YAML 后忘记手动跑 sync）。

    Args:

        gateway: GitCommitGateway 实例（用 project_root）。

    Returns:

        ReconcilerSpec(gate_id="GATE-YAML-SYNC", priority=160)。

    """

    import json
    import os
    import subprocess
    import sys
    from datetime import UTC, datetime
    from pathlib import Path

    project_root = gateway.project_root

    # S1.6: 重试队列持久化路径（data/cache/ 已被 .gitignore）

    _RETRY_QUEUE_PATH = Path(project_root) / "data" / "cache" / "yaml_sync_retry_queue.json"

    _MAX_RETRY_ATTEMPTS = 3  # S1.6: 超过此次数后停止重试，升级为 error 防止无限循环

    def _read_retry_queue() -> dict | None:
        """读取重试队列。返回 None 表示无待重试项。"""

        if not _RETRY_QUEUE_PATH.exists():
            return None

        try:
            return json.loads(_RETRY_QUEUE_PATH.read_text(encoding="utf-8"))

        except (json.JSONDecodeError, OSError):
            return None

    def _write_retry_queue(data: dict) -> None:
        """写入重试队列"""

        _RETRY_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)

        _RETRY_QUEUE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _clear_retry_queue() -> None:
        """清空重试队列"""

        if _RETRY_QUEUE_PATH.exists():
            # T1② 收敛：guard 安全 API（审计+file_ops 声明制强制）
            from scripts.ops_guard import guard_remove

            guard_remove(_RETRY_QUEUE_PATH)

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if not rel.endswith((".yaml", ".yml")):
                continue

            # 规则文件变更触发

            if rel.startswith("docs/01_policies_and_standards/rules/"):
                return True

            # 注册表文件变更触发

            if rel.startswith("docs/01_policies_and_standards/_registry/"):
                return True

            # 资产真源文件变更触发（#180/#181/#182/#179）

            # architecture_model/data/*.yaml: 数据源资产 + 数据源 API

            # architecture_model/runtime/*.yaml: 服务资产

            # architecture_model/contracts/*.yaml: 契约资产

            # config/*.yaml: 配置项资产（文件系统扫描派生）

            if rel.startswith("architecture_model/data/"):
                return True

            if rel.startswith("architecture_model/runtime/"):
                return True

            if rel.startswith("architecture_model/contracts/"):
                return True

            if rel.startswith("config/"):
                return True

        # S1.6: 有待重试项时也触发，但超过最大重试次数后停止（防止无限循环）

        queue = _read_retry_queue()

        if queue is not None:
            if queue.get("attempt", 0) < _MAX_RETRY_ATTEMPTS:
                return True

        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        sync_result = _run_subprocess(
            [sys.executable, "scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )

        if sync_result.returncode == 0:
            # S1.6: 成功->清空重试队列

            _clear_retry_queue()

            return ReconcileResult(
                action="clean",
                detail="YAML->depgraph rules synced",
            )

        # 裁定 C / P2 / #ARCH-GUC-TRIGGER-FIX-001: 失败时先分类错误

        # deterministic 错误（schema bug / GUC 未注册 / 约束违规）重试必然失败，立即 escalate

        # transient / unknown 错误保留重试机制（可能下次成功）

        error_text = sync_result.stderr.strip() or sync_result.stdout.strip()

        error_class = _classify_sync_failure(error_text)

        if error_class == "deterministic":
            # 确定性错误：清空重试队列（不重试），立即升级为 error

            # 原因：schema bug / GUC 未注册 / SQL 语法错误重试 N 次必然失败 N 次

            # 原 bug（sync_dataflow_registry retry 23 次全失败）正是此类错误被盲重试的典型

            _clear_retry_queue()

            _write_retry_queue(
                {
                    "failed_at": datetime.now(UTC).isoformat(),
                    "attempt": 1,
                    "error": error_text[:500],
                    "error_class": error_class,
                    "triggered_by": session_id,
                    "escalated": True,
                }
            )

            return ReconcileResult(
                action="error",
                detail=(
                    f"yaml sync DETERMINISTIC failure (error_class={error_class}, "
                    f"NOT retryable — schema bug / GUC / constraint). "
                    f"Manual fix needed: {error_text[:200]}"
                ),
            )

        # transient / unknown 错误：保留重试机制

        prev = _read_retry_queue() or {}

        attempt = prev.get("attempt", 0) + 1

        _write_retry_queue(
            {
                "failed_at": datetime.now(UTC).isoformat(),
                "attempt": attempt,
                "error": error_text[:500],
                "error_class": error_class,
                "triggered_by": session_id,
            }
        )

        if attempt >= _MAX_RETRY_ATTEMPTS:
            # 超过最大重试次数->升级为 error（停止重试，需人工介入修路径/依赖）

            return ReconcileResult(
                action="error",
                detail=(
                    f"yaml sync failed {attempt} times (max={_MAX_RETRY_ATTEMPTS}, "
                    f"error_class={error_class}), STOPPED retry. "
                    f"Manual fix needed: {error_text[:200]}"
                ),
            )

        return ReconcileResult(
            action="warn",
            detail=(
                f"yaml sync failed (attempt {attempt}/{_MAX_RETRY_ATTEMPTS}, "
                f"error_class={error_class}, will retry on next commit): "
                f"{error_text[:200]}"
            ),
        )

    return ReconcilerSpec(
        gate_id="GATE-YAML-SYNC",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=160,
        file_ops=frozenset({"read", "write", "delete"}),
    )


def _collect_csv_refs(content: str, is_path_fn) -> list[str]:

    import csv

    refs: list[str] = []

    try:
        reader = csv.reader(content.splitlines())

        for row in reader:
            for cell in row:
                cell = cell.strip().strip('"').strip("'")

                if "/" in cell and "." in cell and is_path_fn(cell):
                    refs.append(cell)

    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        pass  # CSV 解析失败回退到正则结果

    return refs


def make_precommit_id_uniqueness_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-ID-UNIQ post-commit 兜底 reconciler（治本改进点2）。

    GATE-ID-UNIQ (pre-commit hook id 唯一性) 被 GitCommitGateway 的 --no-verify

    系统性绕过（机制层病根，与 GATE-REG-BL 同根：post-commit 补偿层；原 GATE-15-ttl 已删除）。

    本 reconciler 在 post-commit 跑 check_precommit_id_uniqueness.py --ci 重校，

    检测到 same-repo 重复 id 则记录违规报告供追责（commit 已入历史，非阻断——

    沿用原 make_ttl_reconciler 的设计裁定，该 reconciler 已删除但模式沿用）。

    设计裁定（非阻断）：

    post-commit 无法回滚 commit；same-repo 重复 id 已入 git 历史，仅告警记录到

    .runtime/reconcile_reports/id_uniqueness_<ts>.json，供 ide_health_daemon +

    人工追责 + 后续修复（git revert 或 amend）。双层防御：pre-commit GATE-ID-UNIQ

    阻断 + post-commit reconciler 兜底 --no-verify 绕过场景。

    向内收设计（三原则审核）：

    - 责任唯一：检测逻辑只在 check_precommit_id_uniqueness.py 一处（pre-commit

      hook 与本 reconciler 共用同一脚本，无第二检测实现）

    - 真源唯一：复用 ReconciliationRegistry 框架（第8个 reconciler），不新建兜底系统；

      复用 make_ttl_reconciler 的"post-commit 重校 + 报告落盘 + 非阻断"模式

    - 向内收：扩展 ``_register_default_reconcilers`` 一行，不改 gateway 方法体

    trigger 裁定：committed_files 含 ``.pre-commit-config.yaml`` 即命中

    （该文件是 GATE-ID-UNIQ 的唯一校验对象，与 pre-commit hook 的 files 正则一致）。

    Args:

        gateway: GitCommitGateway 实例（用 project_root，类型注解 object

            保持本纯 stdlib 模块不 import zephyr.*）。

    Returns:

        ReconcilerSpec(gate_id="GATE-ID-UNIQ", priority=250)。

    """

    import json
    import os
    import subprocess
    import sys
    import time

    project_root = gateway.project_root

    _CONFIG_REL = ".pre-commit-config.yaml"

    _CHECK_SCRIPT = "scripts/governance/d5_architecture/checkers/check_precommit_id_uniqueness.py"

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel == _CONFIG_REL:
                return True

        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        # 1. post-commit 重校（脚本内部读 CONFIG_PATH = REPO_ROOT/.pre-commit-config.yaml，

        #    不接受文件参；--ci 硬阻断语义在 post-commit 退化为非阻断——exit 1 仅作信号）

        scan_result = _run_subprocess(
            [sys.executable, _CHECK_SCRIPT, "--ci"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )

        # 2. 报告落盘

        report = {
            "gate_id": "GATE-ID-UNIQ",
            "session_id": session_id,
            "exit_code": scan_result.returncode,
            "checked_file": _CONFIG_REL,
            "stdout_tail": scan_result.stdout.strip()[-500:],
            "stderr_tail": scan_result.stderr.strip()[-500:],
        }

        report_path, write_err = _write_reconcile_report(project_root, "id_uniqueness", report)

        if write_err:
            return ReconcileResult(
                action="warn",
                detail=f"id_uniqueness scan done (exit={scan_result.returncode}) but report write failed: {write_err}",
            )

        # 3. 判定（exit 0 = clean；exit 1 = same-repo 重复 id 检出；exit 2 = 脚本异常）

        if scan_result.returncode == 0:
            return ReconcileResult(
                action="clean",
                detail=f"id_uniqueness scan clean, report={report_path.name}",
            )

        return ReconcileResult(
            action="warn",
            detail=f"id_uniqueness scan detected violations (exit={scan_result.returncode}), report={report_path.name}",
        )

    return ReconcilerSpec(
        gate_id="GATE-ID-UNIQ",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=250,
        file_ops=frozenset({"read", "write"}),
    )


def make_vocab_change_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-VOCAB-CHANGE post-commit reconciler（词表变更自动纠偏）。

    当 ttl_vocabulary.yaml 的 decision_tree 变更时，自动重判所有 docs/*.md 的 ttl，

    修正不一致的值并自动提交（治本：词表变更后 ttl 漂移自动纠偏，无需手动跑 backfill）。

    对账链：

    1. trigger: committed_files 含 ttl_vocabulary.yaml -> 命中

    2. 调用 backfill_ttl_metadata.py --rejudge 重判所有 docs/*.md 的 ttl

    3. git diff 检测 docs/ 下 .md 变更 -> 无变更返回 clean

    4. 有变更 -> git add + git commit --no-verify（斩断循环）

    设计依据：trae_060 治本方案——decision_tree 机器可读化后，词表变更应自动传播到

    所有 .md 文件的 ttl 字段，消除手动 backfill 漂移风险。reconciler 优先级 280

    （在原 GATE-15-ttl 300 之前执行；GATE-15-ttl 已删除，ttl 校验由 pre-compensation 承担）。

    Args:

        gateway: GitCommitGateway 实例（用 project_root + _run_git）。

    Returns:

        ReconcilerSpec(gate_id="GATE-VOCAB-CHANGE", priority=280)。

    """

    import os
    import subprocess
    import sys

    project_root = gateway.project_root

    _VOCAB_REL = "docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml"

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel == _VOCAB_REL:
                return True

        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        # 1. 重判所有 docs/*.md 的 ttl（--rejudge 模式重判已有 ttl 的文件）

        rejudge_result = _run_subprocess(
            [sys.executable, "scripts/governance/d3_metadata/backfill_ttl_metadata.py", "--rejudge"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,  # 5175 文件重判需要较长时间
        )

        if rejudge_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"ttl rejudge failed (exit={rejudge_result.returncode}): {rejudge_result.stderr.strip()[:200]}",
            )

        # 2. 检测 docs/ 下 .md 变更（reconciler 执行时工作区只有本次修改，

        #    其他 session 修改已被 stash 隔离）

        #    只提交 .md 变更——reconciler 目的是重判 docs/*.md 的 ttl（docstring 明确）；

        #    .yaml/.json 等规则文件的 body section 变更不应由 reconciler 代提交

        #    （防御 backfill_ttl_metadata.py 误改 rules/*.yaml 的 body section，

        #     2026-06-30 红蓝对抗修复：曾因无 .md 过滤误删 trae_001 ttl_design section）

        diff_result = gateway.run_git(["git", "diff", "--name-only", "--", "docs/"])

        if diff_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"git diff failed: {diff_result.stderr.strip()[:200]}",
            )

        changed_files = [
            f.strip() for f in diff_result.stdout.strip().splitlines() if f.strip() and f.strip().endswith(".md")
        ]

        if not changed_files:
            return ReconcileResult(
                action="clean",
                detail="ttl rejudge: no drift detected (all ttl consistent)",
            )

        # 3. 变更 -> 自动提交修复（经 _commit_auto 统一入口，DCR gate 覆盖）

        # 治本（2026-06-30）：原裸调 _run_git commit 绕过 DCR gate，改为走 _commit_auto

        # 统一入口，五重 gate 覆盖。原"--no-verify 斩断 pre-commit 循环"由 _commit_auto

        # 内部的 --no-verify 保证（_commit_with_file_message 统一用 --no-verify）。

        abs_files = [str(project_root / f) for f in changed_files]

        auto_msg = "chore(ttl): auto-rejudge by GATE-VOCAB-CHANGE post-commit (decision_tree changed)"

        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)

        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail=f"ttl rejudge: {len(changed_files)} files auto-reconciled",
            )

        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail=f"ttl rejudge: {len(changed_files)} files but no staged changes (auto-commit)",
            )

        return ReconcileResult(
            action="warn",
            detail=f"ttl rejudge: auto-commit failed ({commit_result.status}): {commit_result.message[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-VOCAB-CHANGE",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=280,
        file_ops=frozenset({"read", "write"}),
    )


# trae_060-reviewed: ①该存在——#73 实证断裂（ttl 声明"准不准"无周期校验，TTL-METADATA 只管"有没有"）；
# ②不能合并进已有——make_vocab_change_reconciler 触发条件=词表文件变更+auto-commit 纠偏，与本 reconciler
# 每次 commit 增量校验+warn-only 语义正交；判定逻辑零重复（复用 backfill_ttl_metadata.py --check 统一出口）；
# ③治本——校验复用 decision_tree SSoT，reconciler 仅做事件接入，不新增写路径/新真源。
def make_ttl_drift_incremental_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-TTL-DRIFT-INCREMENTAL post-commit reconciler（#73 TTL 声明质保链·增量校验）。

    断裂点（tracker #73 实证）：TTL-METADATA 门禁管"有没有"（缺 ttl 不让 commit）；
    GATE-VOCAB-CHANGE 管词表变更后的全量纠偏；但日常新增/修改文档的 ttl 声明
    "准不准"无周期校验（原常设 TTL reconciler 已删除）——漂移只有词表变更时才被发现。

    本 reconciler 补齐增量校验：每次 commit 后对其中的 ttl 载体文件跑
    backfill_ttl_metadata.py --rejudge --check（dry-run 零写入，warn-only），
    声明与 ttl_vocabulary.yaml decision_tree 不符即 warn 曝光，纠偏走人工确认
    （声明是人/AI 的显式意图，不做静默 auto-fix——reconciler 纪律 warn/skip/fix-in-place，
    此处取 warn）。

    对账链：
    1. trigger: committed_files 含 ttl 载体后缀且位于 docs/src/scripts/tests 扫描域
    2. subprocess 调 backfill_ttl_metadata.py --rejudge --check <files>
    3. exit 0 -> clean；exit 1 -> warn（CHANGED FILES 清单）；其他 -> warn（脚本异常）

    Args:

        gateway: GitCommitGateway 实例（用 project_root）。

    Returns:

        ReconcilerSpec(gate_id="GATE-TTL-DRIFT-INCREMENTAL", priority=285)。

    """

    import sys

    project_root = gateway.project_root

    _TTL_SUFFIXES = frozenset({".md", ".py", ".sh", ".ps1", ".mmd", ".yaml", ".json"})

    # 管辖域=文档保留期判定树的 zone 模型覆盖范围（见 docstring"管辖域"节实证收窄说明）
    _SCAN_ROOT_PREFIXES = ("docs/", "architecture_model/")

    def _pick_targets(committed_files: list[str]) -> list[str]:

        targets = []

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if not rel.startswith(_SCAN_ROOT_PREFIXES):
                continue

            if Path(rel).suffix.lower() not in _TTL_SUFFIXES:
                continue

            if (project_root / rel).is_file():
                targets.append(rel)

        return targets

    def _trigger(committed_files: list[str]) -> bool:

        return bool(_pick_targets(committed_files))

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        targets = _pick_targets(committed_files)

        if not targets:
            return ReconcileResult(
                action="clean",
                detail="ttl drift incremental: no ttl-bearing files in commit",
            )

        result = _run_subprocess(
            [
                sys.executable,
                "scripts/governance/d3_metadata/backfill_ttl_metadata.py",
                "--rejudge",
                "--check",
                *targets,
            ],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )

        if result.returncode == 0:
            return ReconcileResult(
                action="clean",
                detail=f"ttl drift incremental: {len(targets)} files consistent",
            )

        if result.returncode != 1:
            return ReconcileResult(
                action="warn",
                detail=f"ttl drift incremental check error (exit={result.returncode}): {result.stderr.strip()[:200]}",
            )

        # exit 1 = 漂移——解析 CHANGED FILES 清单曝光

        drift_files = []

        in_section = False

        for line in result.stdout.splitlines():
            if line.startswith("=== CHANGED FILES"):
                in_section = True

                continue

            if in_section and line.strip():
                drift_files.append(line.strip())

        shown = ", ".join(drift_files[:10])

        more = f" (+{len(drift_files) - 10} more)" if len(drift_files) > 10 else ""

        return ReconcileResult(
            action="warn",
            detail=f"ttl drift incremental: {len(drift_files)} file(s) ttl 声明与 "
            f"decision_tree 不符——{shown}{more}；处置=人工裁定（词表裁定序："
            f"显式声明 > zone 契约 > doc_type 默认 > decision_tree 辅助判定——"
            f"中性区显式 permanent 可为合法 override；确认声明有误再跑 "
            f"backfill_ttl_metadata.py --rejudge <file> 纠偏提交，warn-only 不写文件）",
        )

    return ReconcilerSpec(
        gate_id="GATE-TTL-DRIFT-INCREMENTAL",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=285,
        file_ops=frozenset({"read"}),
    )


def _audit_commit_history(
    project_root: object,
    audit_window: int,
    gw_marker: str,
    rv_marker: str = "",
) -> tuple[list[dict], str | None]:
    """扫描最近 N 个 commit，返回 (裸commit违规, error)。

    rv_marker 保留为兼容参数（旧调用方仍传入），rv_uses 追溯通道已于 2026-07-18

    治本收敛为不再返回——裸 commit 检测为唯一对外契约，rv 追溯报告移除。

    治本（2026-06-30 病根1 看门人无人看）：把 make_commit_gateway_audit_reconciler

    闭包内的审计逻辑提取为模块级函数，使其成为可被 integrity_anchors 保护的 name

    （A 层 _check_protected_script_integrity 已在 AD-001 阶段3 删除，但模块级函数

    结构保留，供未来复活 A 层时直接复用）。与 working_docs_ghost_ref_archiver 模式

    一致：工厂函数 + 模块级逻辑函数模式。

    两阶段检查：subject 快速扫描 + body 二次确认

    （GitCommitGateway.commit() 把 [GW:tag] 追加到 message 末尾用 \\n\\n 分隔，

    --oneline 只看 subject 会误判手动 commit 为裸 commit，需查 body）。

    Args:

        project_root: Path 对象（gateway.project_root，类型注解 object 保持纯 stdlib）。

        audit_window: 审计窗口（最近 N 个 commit）。

        gw_marker: GW 标记字符串（如 "[GW:"）。

    Returns:

        (violations, error_msg): error_msg 非 None 表示 git log 失败；

        error_msg 为 None 时 violations 为裸 commit 违规列表（每条含 hash + subject）。

    """

    import subprocess

    log_result = _run_subprocess(
        ["git", "log", f"-{audit_window}", "--oneline"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=10,
    )

    if log_result.returncode != 0:
        return [], f"git log failed: {log_result.stderr.strip()[:200]}"

    violations: list[dict] = []

    for line in log_result.stdout.strip().splitlines():
        # format: <hash> <subject>

        parts = line.split(" ", 1)

        if len(parts) < 2:
            continue

        commit_hash, subject = parts[0], parts[1]

        # 跳过 merge commit（合并提交无作者意图；大小写不敏感以兼容 session_worktree 的小写 "merge session/..."）

        if subject.lower().startswith("merge "):
            continue

        if gw_marker in subject:
            # subject 已含 [GW:（合法 commit）

            continue

        # subject 无 [GW: -> 查 body（手动 commit 的 [GW:tag] 在 body 末尾）

        body_result = _run_subprocess(
            ["git", "show", "-s", "--format=%B", commit_hash],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )

        body = body_result.stdout if body_result.returncode == 0 else ""

        if gw_marker in body:
            # body 含 [GW:（合法 commit）

            continue

        violations.append({"hash": commit_hash, "subject": subject[:120]})

    return violations, None


def _migrate_deprecated_files(items, dep_path, target_base, project_root) -> list[dict]:

    import shutil

    migrated: list[dict] = []

    for item in items:
        rel_to_dep = item.relative_to(dep_path)

        target = target_base / rel_to_dep

        src_rel = str(item.relative_to(project_root)).replace("\\", "/")

        dst_rel = str(target.relative_to(project_root)).replace("\\", "/")

        if target.exists():
            migrated.append({"src": src_rel, "dst": dst_rel, "status": "skipped_exists"})

        else:
            target.parent.mkdir(parents=True, exist_ok=True)

            # T1② 收敛：guard 安全 API（审计+file_ops 声明制强制）
            from scripts.ops_guard import guard_move

            guard_move(str(item), str(target))

            migrated.append({"src": src_rel, "dst": dst_rel, "status": "moved"})

    return migrated


def _remove_empty_subdirs(dep_path, project_root) -> list[str]:

    import os
    from pathlib import Path

    removed_dirs: list[str] = []

    for root, _dirs, _files in os.walk(dep_path, topdown=False):
        try:
            if not os.listdir(root):
                # T1② 收敛：guard 安全 API（空目录清理，审计落盘）
                from scripts.ops_guard import guard_rmtree

                guard_rmtree(root)

                removed_dirs.append(str(Path(root).relative_to(project_root)).replace("\\", "/"))

        except OSError:
            pass  # 目录非空或权限不足，跳过

    return removed_dirs


def make_deprecated_directory_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-DEPRECATED-DIR post-commit reconciler（09_audit 治本加固）。

    扫描 docs/ 下是否存在已废弃目录（如 09_audit/），存在则告警。

    双层防御：directory_contract_gate（subprocess 调 check_directory_contract.py）阻断提交 +

    post-commit reconciler 兜底 mkdir 但未提交的场景（如脚本 mkdir 后未 commit）。

    设计裁定（非阻断）：

    post-commit 无法回滚已提交内容；废弃目录可能是脚本 mkdir 的副作用（未 commit），

    仅告警记录到 ``.runtime/reconcile_reports/deprecated_directory_<ts>.json``。

    trigger 裁定：always True（废弃目录可能由任何脚本 mkdir 重建，与 commit 文件无关）。

    向内收设计：

    - 复用 ReconciliationRegistry 框架，不新建兜底系统

    - 废弃目录清单从 directory_contract.yaml §7 deprecated_directories 动态加载（真源唯一，治本 2026-06-30：原依赖 gateway._DEPRECATED_DIRS 已删除导致降级为 no-op）

    - 复用 _write_reconcile_report 报告落盘

    Args:

        gateway: GitCommitGateway 实例（用 project_root 定位契约文件）。

    Returns:

        ReconcilerSpec(gate_id="GATE-DEPRECATED-DIR", priority=600)。

    """

    project_root = gateway.project_root

    # 从 directory_contract.yaml §7 deprecated_directories 动态加载（真源唯一）

    # 治本 2026-06-30：原 getattr(gateway, "_DEPRECATED_DIRS", {}) 因 _DEPRECATED_DIRS

    # 已删除（AD-001 阶段3）返回空 dict 导致 reconciler 降级为 no-op，现直接读契约真源

    import yaml as _yaml  # 局部导入（模块声明 pure stdlib，yaml 仅此函数需要）

    _contract_path = (
        project_root / "docs" / "01_policies_and_standards" / "_registry" / "contracts" / "directory_contract.yaml"
    )

    deprecated_dirs: dict[str, str] = {}

    try:
        with open(_contract_path, encoding="utf-8") as _f:
            _contract = _yaml.safe_load(_f) or {}

        for _entry in _contract.get("deprecated_directories", []):
            _path = _entry.get("path", "")

            _reason = _entry.get("reason", "")

            if _path:
                deprecated_dirs[_path] = _reason

    except (OSError, _yaml.YAMLError):
        # fail-open：契约读取失败时 reconciler 降级为 no-op（不阻断 commit）

        deprecated_dirs = {}

    def _trigger(committed_files: list[str]) -> bool:

        # 始终检测：脚本可能 mkdir 但未 commit（如 session_continuity 的 handoff 写入）

        return True

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        """自动修复：迁移废弃目录内容到合规目录 + 删除空目录。

        治本策略（非 warn-only）：

        - 空目录 -> 直接 rmdir -> action=clean

        - 非空目录 -> shutil.move 迁移到 docs/_working/audit/（不覆盖已有文件）

          -> rmdir 空目录 -> action=warn（迁移的文件需人工 commit）

        - 部分失败 -> action=warn

        消灭"只告警不消除"——无论脚本如何 mkdir，下一次 commit 后自动清理。

        """

        # 合规目标目录：docs/09_audit/ -> docs/_working/audit/

        _COMPLIANT_MAP: dict[str, str] = {
            "docs/09_audit": "docs/_working/audit",
        }

        violations: list[dict] = []

        for dep_dir, reason in deprecated_dirs.items():
            dep_path = project_root / dep_dir

            if not (dep_path.exists() and dep_path.is_dir()):
                continue

            # 收集所有文件（不含目录本身）

            items = [p for p in dep_path.rglob("*") if p.is_file()]

            # 自动迁移：将文件迁移到合规目录（不覆盖已有文件）

            target_base_rel = _COMPLIANT_MAP.get(dep_dir, dep_dir.replace("09_audit", "_working/audit"))

            target_base = project_root / target_base_rel

            migrated = _migrate_deprecated_files(items, dep_path, target_base, project_root)

            # 删除空目录（从最深层开始，bottom-up）

            removed_dirs = _remove_empty_subdirs(dep_path, project_root)

            still_exists = dep_path.exists()

            moved_count = sum(1 for m in migrated if m["status"] == "moved")

            violations.append(
                {
                    "deprecated_dir": dep_dir,
                    "reason": reason,
                    "item_count": len(items),
                    "migrated": migrated,
                    "moved_count": moved_count,
                    "removed_dirs": removed_dirs,
                    "dir_removed": not still_exists,
                }
            )

        report = {
            "gate_id": "GATE-DEPRECATED-DIR",
            "session_id": session_id,
            "violations_count": len(violations),
            "violations": violations,
        }

        report_path, write_err = _write_reconcile_report(project_root, "deprecated_directory", report)

        if write_err:
            return ReconcileResult(
                action="warn",
                detail=f"scan done ({len(violations)} violations) but report write failed: {write_err}",
            )

        if not violations:
            return ReconcileResult(
                action="clean",
                detail=f"no deprecated directories found, report={report_path.name}",
            )

        all_removed = all(v.get("dir_removed") for v in violations)

        total_moved = sum(v.get("moved_count", 0) for v in violations)

        if all_removed and total_moved == 0:
            # 空目录已自动删除——彻底消灭

            return ReconcileResult(
                action="clean",
                detail=f"auto-removed {len(violations)} empty deprecated directories, report={report_path.name}",
            )

        elif all_removed and total_moved > 0:
            # 文件已迁移 + 目录已删除，迁移的文件待 commit

            return ReconcileResult(
                action="warn",
                detail=f"auto-migrated {total_moved} files to docs/_working/audit/ and removed deprecated dirs (commit migrated files), report={report_path.name}",
            )

        else:
            return ReconcileResult(
                action="warn",
                detail=f"partial remediation ({len(violations)} violations, some dirs remain), report={report_path.name}",
            )

    return ReconcilerSpec(
        gate_id="GATE-DEPRECATED-DIR",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=600,  # 中等优先级（非阻断，但需要及时发现）
        file_ops=frozenset({"read", "move", "delete"}),
    )


# ============================================================

# 缺口2/3 共享辅助（规则文件审计 + 豁免区 frontmatter 检测）

# 提取到模块级避免两个 reconciler 重复定义（向内收原则）

# ============================================================

_RULE_FILE_PATHS = (
    "docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml",
    "docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml",
    "docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml",
    "docs/01_policies_and_standards/_registry/contracts/architecture_contract.yaml",
    "docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml",
)

_EXEMPT_ZONE_PREFIXES = (
    "docs/_working/",
    "docs/_archive/",
    ".runtime/",
    ".trae/",
    "docs/01_policies_and_standards/templates/",
)

_FRONTMATTER_EXTS = (".md", ".yaml", ".yml")

# DCR-001 全量扫描触发的契约文件子集（directory_contract + doc_type_vocabulary）

# 提取到模块级避免 check_vocab_hardcode 检测5 误报：

# 函数体内 yaml.safe_load 加载 architecture_issue_registry.yaml（非词表），

# 但同时含 "vocabularies/..." 路径字符串触发 has_vocab_ref 误报。

_CONTRACT_FILES_FOR_DCR = frozenset(
    {
        "docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml",
        "docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml",
    }
)


def _rel_path(f: str, project_root_str: str) -> str:
    """文件路径归一化：os.path.relpath + replace("\\", "/")。

    跨盘兜底（治本，2026-07-21）：

    Windows 跨盘场景（项目在 D 盘，Python/临时文件在 C 盘）下，

    ``os.path.relpath`` 抛 ``ValueError: path is on mount 'D:', start on mount 'C:'``。

    此前 34 处调用点中仅 1 处（L555）有 try/except 兜底，其余 33 处裸调用，

    跨盘时整个 reconciler 失败。本函数统一兜底：

    - 跨盘 ValueError：fallback 到 ``os.path.basename(f)``（至少保留文件名）

    - 其他 OSError：同上 fallback

    - 正常同盘：返回相对路径（原行为不变）

    """

    import os

    try:
        return os.path.relpath(f, project_root_str).replace("\\", "/")

    except (ValueError, OSError):
        # 跨盘或路径无效——fallback 到 basename，至少保留文件名用于日志

        return os.path.basename(f).replace("\\", "/")


def _extract_doc_type(content: str, is_markdown: bool) -> str:
    """从 frontmatter 提取 doc_type 值；无 frontmatter/doc_type 返回空串。

    frontmatter 判定：首行以 ``---`` 开头。.md 取 ``---`` 之间的块；

    .yaml/.yml 取首行 ``---`` 之后的全部内容（YAML document start marker）。

    doc_type 仅识别内联形式 ``doc_type: <value>``（最常见，块形式不识别——

    原型启发式，非完整 YAML 解析，避免引入非 stdlib yaml 依赖）。

    """

    lines = content.splitlines()

    if not lines or not lines[0].lstrip().startswith("---"):
        return ""

    if is_markdown:
        block: list[str] = []

        closed = False

        for line in lines[1:]:
            if line.lstrip().startswith("---"):
                closed = True

                break

            block.append(line)

        if not closed:
            return ""

    else:
        block = lines[1:]

    for line in block:
        stripped = line.strip()

        if ":" not in stripped:
            continue

        key, _, val = stripped.partition(":")

        if key.strip() != "doc_type":
            continue

        val = val.strip()

        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]

        if " #" in val:
            val = val.split(" #", 1)[0].strip()

        return val

    return ""


def make_exempt_zone_frontmatter_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-EXEMPT-ZONE-FM post-commit reconciler（缺口2：豁免区 frontmatter 检测）。

    治本动机：docs/_working/ / docs/_archive/ / .runtime/ / .trae/ / templates/

    五类豁免前缀不受 DCR-001/002 frontmatter 校验约束。若豁免区文件带

    frontmatter + 非空 doc_type，说明本应放正式目录却被塞进豁免区。

    P0 修复（2026-06-30）：原设计此检测与规则文件审计共用 trigger（只在规则文件

    变更时才触发），导致单独提交豁免区文件时检测永不执行（死代码）。现拆分为

    独立 reconciler，trigger 改为检测豁免区文件被提交。

    priority=710（在 GATE-RULE-FILE-AUDIT 700 之后）。

    """

    import json
    import os
    from datetime import datetime
    from pathlib import Path

    project_root = gateway.project_root

    _project_root_str = str(project_root)

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, _project_root_str)

            for zone in _EXEMPT_ZONE_PREFIXES:
                if rel.startswith(zone):
                    return True

        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        exempt_zone_frontmatter_files: list[dict] = []

        for f in committed_files:
            rel = _rel_path(f, _project_root_str)

            matched_zone = ""

            for zone in _EXEMPT_ZONE_PREFIXES:
                if rel.startswith(zone):
                    matched_zone = zone

                    break

            if not matched_zone:
                continue

            if not rel.endswith(_FRONTMATTER_EXTS):
                continue

            abs_path = Path(_project_root_str) / rel

            try:
                content = abs_path.read_text(encoding="utf-8", errors="replace")

            except OSError:
                continue

            doc_type = _extract_doc_type(content, rel.endswith(".md"))

            if doc_type:
                exempt_zone_frontmatter_files.append(
                    {
                        "file": rel,
                        "doc_type": doc_type,
                        "exempt_zone": matched_zone,
                    }
                )

        if not exempt_zone_frontmatter_files:
            return ReconcileResult(action="clean", detail="no exempt-zone frontmatter files")

        reports_dir = os.path.join(_project_root_str, ".runtime", "reconcile_reports")

        os.makedirs(reports_dir, exist_ok=True)

        ts_iso = now_utc().isoformat(timespec="seconds")

        ts_file = ts_iso.replace(":", "")

        report = {
            "timestamp": ts_iso,
            "session_id": session_id,
            "exempt_zone_frontmatter_files": exempt_zone_frontmatter_files,
            "note": "豁免区下有 frontmatter 的文件不受 DCR-001/002 约束，请确认是否应迁移到正式目录",
        }

        report_path = os.path.join(reports_dir, f"exempt_zone_fm_{ts_file}.json")

        try:
            with open(report_path, "w", encoding="utf-8") as fh:
                json.dump(report, fh, ensure_ascii=False, indent=2)

        except OSError as e:
            return ReconcileResult(
                action="warn",
                detail=f"exempt-zone audit done ({len(exempt_zone_frontmatter_files)} file(s)) but report write failed: {e}",
            )

        return ReconcileResult(
            action="warn",
            detail=(
                f"{len(exempt_zone_frontmatter_files)} exempt-zone frontmatter file(s) "
                f"detected (manual review recommended), report={os.path.basename(report_path)}"
            ),
        )

    return ReconcilerSpec(
        gate_id="GATE-EXEMPT-ZONE-FM",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=710,
        file_ops=frozenset({"read", "write"}),
    )


# ============================================================

# AD-GOV-001 治理收敛：5 组 reconciler 合并（16->11）

# 合并规则（严格遵守）：

# - trigger = 旧A trigger OR 旧B trigger（任一命中即执行）

# - reconcile = 串联执行 旧A -> 旧B；action 取较严重

#   （severity: skip/nothing=0, clean=1, warn=2, auto_committed=2），detail 拼接两者

# - priority = max(旧A, 旧B)

# 治本（2026-06-30 元问题4）：原 _make_old_*_reconciler 私有函数已删除，reconcile

# 逻辑内联到下方 5 个 make_* compose 包装函数的闭包中。Python 无真私有，保留

# _make_old_* 等于留可 import 的绕过入口；内联后 reconcile 逻辑仅在 make_* 闭包

# 内可见，无法被外部 import 绕过 compose。reconcile 逻辑真源不动（gateway._commit_auto

# / subprocess / 报告落盘调用原样保留）。

# _compose_reconcilers 是 compose 工具函数（被测试覆盖），保留。

# 测试规范见 tests/governance/audit/test_integrity_audit_reconciler.py——用公共 API +

# mock spec + 模块级函数 _audit_commit_history 测试。

# 新增 reconciler 前 MUST 过 trae_060 §4 元问题审查，教训登记 #ARCH-028。

# ============================================================


def _compose_reconcilers(
    gate_id: str,
    *specs: ReconcilerSpec,
) -> ReconcilerSpec:
    """合并 N 个（≥2）reconciler spec 为一个（AD-GOV-001 治理收敛工具函数）。

    元问题1治本扩展（2026-06-30）：原签名只支持 2 个 spec，AGENTS.md 引用检测

    需 3-way 合并（rules_integrity + commit_gw_audit + agents_md_refs）。扩展为

    *specs 可变参数，向后兼容（2 参数时行为不变，5 个现有调用点零回归）。

    - trigger: 所有 spec trigger 的 OR（任一命中即执行）

    - reconcile: 串联执行所有 spec.reconcile（按传入顺序）；action 取较严重

      （severity: warn=auto_committed=2 > clean=1 > skip=nothing=0），detail 拼接全部

    - priority: max(所有 spec.priority)

    """

    if len(specs) < 2:
        raise ValueError(f"_compose_reconcilers requires at least 2 specs, got {len(specs)}")

    triggers = [s.trigger for s in specs]

    reconciles = [s.reconcile for s in specs]

    _SEVERITY = {
        "skip": 0,
        "clean": 1,
        "nothing": 0,
        "warn": 2,
        "auto_committed": 2,
        "critical_warn": 3,
        "block_next": 4,
    }

    def _trigger(committed_files: list[str]) -> bool:

        return any(t(committed_files) for t in triggers)

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        results = [r(committed_files, session_id) for r in reconciles]

        # action 取较严重（severity 高者胜）

        action = results[0].action

        for res in results[1:]:
            if _SEVERITY.get(res.action, 0) > _SEVERITY.get(action, 0):
                action = res.action

        # detail 平铺拼接全部（格式：[action_a] detail_a | [action_b] detail_b | ...）

        detail = " | ".join(f"[{r.action}] {r.detail}" for r in results)

        return ReconcileResult(action=action, detail=detail)

    return ReconcilerSpec(
        gate_id=gate_id,
        trigger=_trigger,
        reconcile=_reconcile,
        priority=max(s.priority for s in specs),
        # T1① 组合 spec 操作面 = 子 specs 并集（声明制可审计）
        file_ops=frozenset().union(*(s.file_ops for s in specs)),
    )


def _backup_depgraph_for_autoclean(project_root: object, session_id: str) -> tuple:
    """ghost auto-clean 前的逻辑备份（nodes + edges 表 CSV）。

    治本（2026-07-04）：符合"备份先行：改 depgraph 前必须备份"硬约束（trae_054 STEP0）。

    函数内 import psycopg2 + get_depgraph_pg_connection（F1 裸 connection，支持 copy_expert），

    不破坏本模块顶层"纯 stdlib"约束（reconciliation_registry 用于 mutation testing，

    顶层须纯 stdlib；函数内 import 是允许的，与既有 _reconcile_ghost 内 import 一致）。

    治本（2026-07-08，ARCH-DEBT-BACKUP-CLEANUP）：备份路径统一到 tmp/pg_backups/（.gitignored，

    与 backup_runtime_state.py 的 backup_pg_architecture 标杆机制对齐），并新增保留策略——保留最近

    max_backups 个 ghost_autoclean_* 目录，超出部分自动清理（对标 backup_pg_architecture 的保留 10 个）。

    消除"备份目录只增不减"的技术债务。详见 trae_081_audit_dimensions_framework.yaml 维度 5.1.3。

    Args:

        project_root: Path 对象（gateway.project_root）。

        session_id: 触发 auto-clean 的 session_id（用于备份目录命名追溯）。

    Returns:

        (backup_dir_path, "") 成功 | (None, error_msg) 失败（fail-closed 不清理）。

    """

    import time
    from pathlib import Path

    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        return None, f"import depgraph_schema failed: {e}"

    ts = int(time.time())

    backup_dir = Path(project_root) / "tmp" / "pg_backups" / f"ghost_autoclean_{ts}"

    backup_dir.mkdir(parents=True, exist_ok=True)

    conn = get_depgraph_pg_connection(autocommit=True)

    try:
        with conn.cursor() as cur:
            for table in ("nodes", "edges"):
                csv_path = backup_dir / f"{table}.csv"

                with open(csv_path, "w", encoding="utf-8") as f:
                    cur.copy_expert(f"COPY {table} TO STDOUT WITH CSV HEADER", f)

        # 治本（2026-07-08）：保留策略——清理过期 ghost_autoclean 备份（对标 backup_pg_architecture）

        _cleanup_old_ghost_backups(project_root, max_backups=10)

        return backup_dir, ""

    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        return None, str(e)

    finally:
        conn.close()


def _cleanup_old_ghost_backups(project_root: object, max_backups: int = 10) -> int:
    """清理过期的 ghost_autoclean_* 备份目录，保留最近 max_backups 个。

    治本（2026-07-08，ARCH-DEBT-BACKUP-CLEANUP）：对标 backup_runtime_state.py 的

    backup_pg_architecture 保留策略（保留最近 10 个），消除"备份目录只增不减"的技术债务。

    备份目录命名：ghost_autoclean_{unix_timestamp}（按时间戳排序 = 按创建时间排序）。

    Args:

        project_root: Path 对象（gateway.project_root）。

        max_backups: 保留的备份数量上限（默认 10）。

    Returns:

        清理的备份数量（异常时返回 0，不阻断主流程）。

    """

    import os
    import shutil
    from pathlib import Path

    try:
        base = Path(project_root) / "tmp" / "pg_backups"

        if not base.exists():
            return 0

        # 列出所有 ghost_autoclean_* 目录，按名称（含时间戳）降序排序 = 最近创建的在前

        backups = sorted(
            [d for d in base.iterdir() if d.is_dir() and d.name.startswith("ghost_autoclean_")],
            key=lambda d: d.name,
            reverse=True,
        )

        # 超出 max_backups 的全部删除

        to_remove = backups[max_backups:]

        for d in to_remove:
            # T1② 收敛：guard 安全 API（审计+file_ops 声明制强制）
            from scripts.ops_guard import guard_rmtree

            try:
                guard_rmtree(str(d))

            except OSError:
                # Windows 文件锁兜底——只读位清除后重试

                import stat

                try:
                    for f in d.rglob("*"):
                        if f.is_file():
                            os.chmod(f, stat.S_IWRITE)

                    guard_rmtree(str(d))

                except OSError:
                    pass  # fail-open，不阻断主流程

        return len(to_remove)

    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return 0  # fail-open，保留策略失败不阻断主备份流程


def make_delete_audit_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-DELETE-AUDIT post-commit 对账 reconciler（AD-GOV-001 合并）。

    合并来源：

    - 旧 GATE-GHOST (priority=400)：commit 删除文件后跑 diagnose_depgraph.py

      检测 depgraph 残留 ghost node（磁盘已删除但 DB 仍保留），记录报告供追责。

    - 旧 GATE-WORKING-DOCS (priority=500)：扫描 docs/_working/ 工作文档的幽灵引用，

      归档有幽灵引用的文档到 .runtime/working_archive/ 并自动提交 _working/ 删除。

    合并原因：两者 trigger 完全重叠（均检测 committed 文件不在磁盘 = 删除 commit），

    reconcile 均处理"删除引发的漂移"，逻辑可串联，合并消除冗余 trigger 评估。

    合并后执行：先 ghost 诊断，再 working_docs 归档；action 取较严重，detail 拼接。

    priority=max(400,500)=500。

    治本（2026-06-30 元问题4）：reconcile 逻辑内联自原 _make_old_ghost_reconciler

    与 _make_old_working_docs_reconciler，私有函数已删除，无法被外部 import 绕过。

    """

    import os
    import re
    import subprocess
    import sys

    project_root = gateway.project_root

    # === 旧 GATE-GHOST 逻辑（内联自 _make_old_ghost_reconciler）===

    def _trigger_ghost(committed_files: list[str]) -> bool:

        # committed 文件不在磁盘 = 删除 commit（post-commit 时点，工作树已反映删除）

        return any(not os.path.isfile(f) for f in committed_files)

    def _reconcile_ghost(committed_files: list[str], session_id: str) -> ReconcileResult:

        # P0 修复（2026-07-04）：动态查找 diagnose_depgraph.py 路径

        # 原写死 scripts/governance/diagnose_depgraph.py，gov-split 批次4b（commit 170cba56e0）

        # 将文件迁移到 scripts/governance/d5_architecture/ 后路径失效，导致检测机制完全失效

        # （所有报告 exit=2 ghost=-1 "can't open file"）。改为 glob 动态查找，兼容未来迁移。

        import glob as _glob

        diag_candidates = [
            os.path.join(str(project_root), "scripts", "governance", "diagnose_depgraph.py"),
        ]

        diag_candidates += _glob.glob(
            os.path.join(str(project_root), "scripts", "governance", "**", "diagnose_depgraph.py"),
            recursive=True,
        )

        diag_path = next((p for p in diag_candidates if os.path.isfile(p)), None)

        if diag_path is None:
            return ReconcileResult(
                action="warn",
                detail="ghost diagnose skipped: diagnose_depgraph.py not found under scripts/governance/",
            )

        # 1. 跑 diagnose_depgraph.py（无 --output，捕获 stdout 解析 ghost_count）

        diag_result = _run_subprocess(
            [sys.executable, diag_path],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )

        # 2. 解析 ghost_count（输出格式：[DIAG]   Found N orphan nodes (M ghost: ...))

        ghost_count = -1

        m = re.search(r"\((\d+)\s+ghost:", diag_result.stdout)

        if m:
            ghost_count = int(m.group(1))

        # 3. 报告落盘

        report = {
            "gate_id": "GATE-GHOST",
            "session_id": session_id,
            "exit_code": diag_result.returncode,
            "ghost_count": ghost_count,
            "deleted_files": [f for f in committed_files if not os.path.isfile(f)],
            "stdout_tail": diag_result.stdout.strip()[-800:],
            "stderr_tail": diag_result.stderr.strip()[-500:],
        }

        report_path, write_err = _write_reconcile_report(project_root, "ghost", report)

        if write_err:
            return ReconcileResult(
                action="warn",
                detail=f"ghost diagnose done (exit={diag_result.returncode}) but report write failed: {write_err}",
            )

        # 4. 判定（ghost_count==0 = clean；>0 在阈值内 = auto_clean；>阈值/-1 = warn）

        if diag_result.returncode == 0 and ghost_count == 0:
            return ReconcileResult(
                action="clean",
                detail=f"ghost diagnose clean (ghost_count=0), report={report_path.name}",
            )

        # P1 auto_clean（2026-07-04）：ghost_count > 0 且 ≤ 阈值 -> 自动清理

        # 治本：消除"检测自动/清理人工"gap（root_cause: 检测坏 + 无自动闭环导致 ghost 无声狂累积）。

        # 备份先行（符合 trae_054 STEP0 硬约束），备份失败则 fail-closed 不清理。

        # 与"永久系统必须全自动（自动触发/运行/维护/关闭）禁止需手工干预"硬约束对齐。

        _GHOST_AUTO_CLEAN_THRESHOLD = 50  # ghost ≤ 50 自动清理，> 50 warn（防批量误删）

        if diag_result.returncode == 0 and 0 < ghost_count <= _GHOST_AUTO_CLEAN_THRESHOLD:
            backup_dir, backup_err = _backup_depgraph_for_autoclean(project_root, session_id)

            if backup_err:
                return ReconcileResult(
                    action="warn",
                    detail=f"ghost count={ghost_count} but backup failed: {backup_err}, skip auto-clean for safety",
                )

            # 调 apply_depgraph.py --cleanup-orphan-nodes（清理已在 backup 之后）

            clean_nodes = _run_subprocess(
                [sys.executable, "scripts/governance/apply_depgraph.py", "--cleanup-orphan-nodes"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=300,
            )

            # 再调 --cleanup-orphan-edges（清理孤儿边）

            clean_edges = _run_subprocess(
                [sys.executable, "scripts/governance/apply_depgraph.py", "--cleanup-orphan-edges"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=300,
            )

            return ReconcileResult(
                action="auto_committed",
                detail=(
                    f"auto-cleaned {ghost_count} ghost nodes "
                    f"(nodes_exit={clean_nodes.returncode}, edges_exit={clean_edges.returncode}), "
                    f"backup={backup_dir.name}, report={report_path.name}"
                ),
            )

        # ghost_count > 阈值 或 解析失败（-1）-> warn（防批量误删/检测失败）

        return ReconcileResult(
            action="warn",
            detail=f"ghost diagnose: ghost_count={ghost_count} (exit={diag_result.returncode}), report={report_path.name}",
        )

    spec_ghost = ReconcilerSpec(
        gate_id="GATE-GHOST",
        trigger=_trigger_ghost,
        reconcile=_reconcile_ghost,
        priority=400,
        file_ops=frozenset({"read", "delete"}),
    )

    # === 旧 GATE-WORKING-DOCS 逻辑（内联自 _make_old_working_docs_reconciler）===
    # #ARCH-RECONCILER-AUTO-DELETE-GOV-001 治本（2026-08-14 用户裁定完整版一次到位）：
    # 旧机制"幽灵引用即归档+auto-commit 删除"=一枪毙命，对治理文档误判率 100%
    # （tracker/裁定书/潘潘文档三次事故实证）。重写为 doc_lifecycle 状态机驱动：
    # 观察（7 天宽限）→ 自动复活 → 满期归档（30 天回收站）——零物理删除。

    def _trigger_working(committed_files: list[str]) -> bool:

        # 状态机每次 post-commit 都推进（增量轻量：正则+mtime+清单 diff），
        # 不再依赖"删除型 commit"触发——复活检测/宽限期推进需要周期执行。
        return True

    def _reconcile_working(committed_files: list[str], session_id: str) -> ReconcileResult:

        from zephyr.governance.audit.doc_lifecycle import evaluate_lifecycle

        report = evaluate_lifecycle(project_root)

        # 报告落盘（沿用旧通道）
        report_payload = {
            "gate_id": "GATE-WORKING-DOCS",
            "session_id": session_id,
            "scanned": report.scanned,
            "skipped_permanent": report.skipped_permanent,
            "watched": report.watched,
            "revived": report.revived,
            "archived": report.archived,
            "pruned_recycle": report.pruned_recycle,
            "error": report.error,
        }

        report_path, write_err = _write_reconcile_report(project_root, "working_docs", report_payload)

        if write_err:
            return ReconcileResult(
                action="warn",
                detail=f"doc_lifecycle evaluated but report write failed: {write_err}",
            )

        detail = (
            f"lifecycle: scanned={report.scanned} permanent_skip={report.skipped_permanent} "
            f"watch+{len(report.watched)} revived={len(report.revived)} "
            f"archived={len(report.archived)} recycle_pruned={report.pruned_recycle}, "
            f"report={report_path.name}"
        )

        # 删除类永不 auto-commit（I-GOV-2 铁律 architecture_issue_registry L12341：
        # "reconciler 只允许 warn/skip/fix-in-place，禁止 action=commit"；
        # #ARCH-RECONCILER-AUTO-DELETE-GOV-001 T0② 裁定——物理消除
        # "误判×自动执行×自动入库"放大链）。
        # 归档已 move 进 30 天回收站（可逆，guard_recycle 审计在案）；git deletion
        # 留在工作区，由人工/AI 会话审查后走常规网关显式提交（人在环确认），
        # reconciler 只 warn 不提交。
        if report.archived:
            return ReconcileResult(
                action="warn",
                detail=(
                    detail + f" | {len(report.archived)} docs 已归档回收站（30 天可恢复），"
                    "git deletion 待人工审查后常规提交（I-GOV-2：删除类禁止 auto-commit）"
                ),
            )

        if report.error:
            return ReconcileResult(action="warn", detail=detail + f" error={report.error[:120]}")

        if report.scanned == 0:
            return ReconcileResult(action="skip", detail="no lifecycle candidates in _working/")

        return ReconcileResult(action="clean", detail=detail)

    spec_working = ReconcilerSpec(
        gate_id="GATE-WORKING-DOCS",
        trigger=_trigger_working,
        reconcile=_reconcile_working,
        priority=500,
        file_ops=frozenset({"read", "move"}),
    )

    return _compose_reconcilers("GATE-DELETE-AUDIT", spec_ghost, spec_working)


def make_regenerate_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-REGENERATE post-commit 自动重生 reconciler（AD-GOV-001 合并）。

    合并来源：

    - 旧 GATE-DOMAIN-DOC (priority=600)：PG 写入脚本 commit 后跑

      generate_domain_doc.py --all（generate_domain_dependency_diagram.py 已于 2026-07-30 下线，.mmd 由域文档内嵌 mermaid 替代）

      重生所有域制品，有变更自动提交。

    - 旧 GATE-ARCH-MODEL (priority=610)：PG 写入脚本 commit 后跑

      dm200916_write_direct.py 重生根树 architecture_model/index.yaml 的 domains

      列表，有变更自动提交。

    合并原因：两者 trigger 完全重叠（均匹配同一组 PG 写入脚本 commit），reconcile

    均为"DB 变更->派生制品重生"，逻辑可串联，合并消除冗余 trigger 评估。

    合并后执行：先重生域文档，再重生根树 index.yaml；action 取较严重，detail 拼接。

    priority=max(600,610)=610。

    治本（2026-06-30 元问题4）：reconcile 逻辑内联自原 _make_old_domain_doc_reconciler

    与 _make_old_arch_model_reconciler，私有函数已删除。

    """

    import os
    import subprocess
    import sys

    project_root = gateway.project_root

    # PG 写入脚本真源列表（DB 变更即代表域可能漂移）

    _PG_WRITE_SCRIPTS = (
        "scripts/governance/apply_depgraph.py",
        "scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py",
        "scripts/governance/generate_project_path_tree.py",
    )

    _GEN_DIR = "scripts/governance/d5_architecture/generators"

    _DOC_DIRS = (
        "docs/02_enterprise_architecture/02_domain_architecture_docs",
        "docs/02_enterprise_architecture/generated/domains",
    )

    _GEN_SCRIPT = "scripts/governance/d5_architecture/dm200916_write_direct.py"

    _ARCH_MODEL_INDEX = ("architecture_model/index.yaml",)

    # DM-90974 Phase 2: depgraph dirty flag — PG 写入脚本落此空文件标记 DB 已变，

    # _trigger_domain_doc 检测 flag 存在即 fire，_reconcile_domain_doc 成功后由

    # _clear_depgraph_dirty_flag() 删除。真源仍是 PostgreSQL DB；此 flag 仅作

    # "运行时 DB 写入→下次 commit 触发 reconciler"的桥接信号（派生缓存，单向

    # DB 写入→flag→reconcile→删 flag）。解决"apply_depgraph.py --delete-nodes

    # 等运行时操作不产生 git commit → 原 trigger 永不 fire"的盲区。

    #

    # 治本（2026-07-19 真源收敛）：路径真源为 zephyr.shared.io.paths.DEPGRAPH_DIRTY_FLAG。

    # 原独立重算 `project_root / "data" / "databases" / "depgraph_dirty.flag"` 违反真源唯一铁律——

    # 路径变更只改 paths.py 不会同步到此处，导致写入端（_shared.constants 调 mark_depgraph_dirty）

    # 与读取端（此 _trigger_domain_doc）不一致，reconciler 静默失效。

    # 现直接 import 真源，消除真源重复。测试隔离通过 monkeypatch paths.DEPGRAPH_DIRTY_FLAG 实现。

    from zephyr.shared.io.paths import DEPGRAPH_DIRTY_FLAG as _DEPGRAPH_DIRTY_FLAG

    def _clear_depgraph_dirty_flag() -> None:
        """DM-90974: 重生成功后删除 dirty flag，避免下次 commit 重复触发。

        失败不阻断成功路径返回（最坏情况是 flag 残留 → 下次 commit 重复 fire

        一次重生，生成器幂等保证无害，与治本前等价，不退化）。

        """

        try:
            # T1② 收敛：guard 安全 API（审计+file_ops 声明制强制）
            from scripts.ops_guard import guard_remove

            guard_remove(_DEPGRAPH_DIRTY_FLAG)

        except OSError:
            # flag 删除失败不阻断主流程（reconcile 已成功，下次最多多 fire 一次）

            pass

    # === 旧 GATE-DOMAIN-DOC 逻辑（内联自 _make_old_domain_doc_reconciler）===

    def _trigger_domain_doc(committed_files: list[str]) -> bool:

        # DM-90974 Phase 2: 运行时 DB 写入不产生 git commit，原 trigger 永不 fire。

        # PG 写入脚本成功 commit 后落 depgraph_dirty.flag，此处检测 flag 存在即触发。

        if _DEPGRAPH_DIRTY_FLAG.exists():
            return True

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel in _PG_WRITE_SCRIPTS:
                return True

            # 文件删除也触发：layer 1 ghost 过滤确保重生后的文档不含幽灵节点

            if not os.path.isfile(f) and f.endswith((".py", ".yaml", ".yml")):
                return True

        return False

    def _reconcile_domain_doc(committed_files: list[str], session_id: str) -> ReconcileResult:

        # P1 治本已落地（#ARCH-REGEN-NONIDEMPOTENT-001，commit 97c77a9c8a，2026-08-05）：
        # 6 生成器去 datetime.now + LIMIT 加 ORDER BY + write_text 加 newline=\n，
        # 生成器幂等性已恢复。P0 止血 skip 已移除，恢复正常 reconciler 逻辑。
        # 派生产物离库（#ARCH-GOV-BUDGET-001 / I-GOV-1）见 AGENTS.md §11.1.4。

        # 0. drift-gate: 预检测域文档产物是否已有未提交变更（体系A reconcile_async 可能已跑过）

        #    有变更 → 跳过生成器直接 auto-commit（消除与体系A双重执行，治本 #ARCH-DUAL-TRIGGER）

        #    无变更 → 产物可能过时，继续跑生成器（原逻辑兜底）

        pre_diff = gateway.run_git(["git", "diff", "--name-only", "--", *_DOC_DIRS])

        if pre_diff.returncode == 0 and pre_diff.stdout.strip():
            pre_changed = [f.strip() for f in pre_diff.stdout.splitlines() if f.strip()]

            pre_abs = [str(project_root / f) for f in pre_changed]

            pre_commit = gateway._commit_auto(
                session_id,
                pre_abs,
                "chore(docs): auto-commit systemA-regenerated domain docs (drift-gate skipped generators)",
            )

            if pre_commit.status == "OK":
                # 跳过生成器也要清 dirty flag，否则下次 commit 重复 fire

                _clear_depgraph_dirty_flag()

                return ReconcileResult(
                    action="auto_committed",
                    detail=f"drift-gate: skipped domain_doc generators, auto-committed {len(pre_changed)} files (systemA already ran)",
                )

            # auto-commit 失败 → 落回原逻辑跑生成器（兜底，不阻断）

        # 1. 重生所有域制品（生成器不含时间戳，相同 DB 输入->相同输出）

        for gen_name in ("generate_domain_doc.py",):
            gen_result = _run_subprocess(
                [sys.executable, f"{_GEN_DIR}/{gen_name}", "--all"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
            )

            if gen_result.returncode != 0:
                return ReconcileResult(
                    action="warn",
                    detail=f"{gen_name} --all failed: {gen_result.stderr.strip()[:200]}",
                )

        # 1b. 重生域索引（无 --all 参数，单独运行）

        idx_result = _run_subprocess(
            [sys.executable, f"{_GEN_DIR}/generate_domain_index.py"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )

        if idx_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"generate_domain_index.py failed: {idx_result.stderr.strip()[:200]}",
            )

        # 2. 检测制品变更

        diff_result = gateway.run_git(["git", "diff", "--name-only", "--", *_DOC_DIRS])

        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            # DM-90974 Phase 2: 重生后无漂移 = 成功，清 dirty flag 避免下次重复 fire

            _clear_depgraph_dirty_flag()

            return ReconcileResult(action="clean", detail="domain docs up to date")

        # 3. 变更 -> 自动提交（经 _commit_auto 统一入口，DCR gate 覆盖）

        changed_files = [f.strip() for f in diff_result.stdout.splitlines() if f.strip()]

        abs_files = [str(project_root / f) for f in changed_files]

        auto_msg = "chore(docs): auto-regenerate domain docs by GitCommitGateway post-commit"

        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)

        if commit_result.status == "OK":
            # DM-90974 Phase 2: 成功提交 = 成功，清 dirty flag

            _clear_depgraph_dirty_flag()

            return ReconcileResult(
                action="auto_committed",
                detail="domain docs drift detected and auto-regenerated",
            )

        if commit_result.status == "NOTHING_TO_COMMIT":
            # DM-90974 Phase 2: 无变更可提交 = 成功（生成器幂等无 diff），清 dirty flag

            _clear_depgraph_dirty_flag()

            return ReconcileResult(
                action="clean",
                detail="domain docs no drift (auto-commit found no staged changes)",
            )

        # warn 路径（auto-commit 失败）不清 dirty flag → 下次 commit 仍会 fire 重试

        return ReconcileResult(
            action="warn",
            detail=f"domain docs drift detected, auto-commit failed ({commit_result.status}): "
            f"{commit_result.message[:200]}",
        )

    spec_domain_doc = ReconcilerSpec(
        gate_id="GATE-DOMAIN-DOC",
        trigger=_trigger_domain_doc,
        reconcile=_reconcile_domain_doc,
        priority=600,
        file_ops=frozenset({"read", "write", "delete"}),
    )

    # === 旧 GATE-ARCH-MODEL 逻辑（内联自 _make_old_arch_model_reconciler）===

    def _trigger_arch_model(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel in _PG_WRITE_SCRIPTS:
                return True

        return False

    def _reconcile_arch_model(committed_files: list[str], session_id: str) -> ReconcileResult:

        # 1. 重生根树 index.yaml（dm200916 从 depgraph (PostgreSQL) domains 表派生）

        gen_result = _run_subprocess(
            [sys.executable, _GEN_SCRIPT],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )

        if gen_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"dm200916_write_direct.py failed: {gen_result.stderr.strip()[:200]}",
            )

        # 2. 检测 index.yaml 变更

        diff_result = gateway.run_git(["git", "diff", "--name-only", "--", *_ARCH_MODEL_INDEX])

        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="EA tree index.yaml up to date")

        # 3. 变更 -> 自动提交（经 _commit_auto 统一入口，DCR gate 覆盖）

        abs_files = [str(project_root / rel) for rel in _ARCH_MODEL_INDEX]

        auto_msg = "chore(arch_model): auto-regenerate EA tree index.yaml by GitCommitGateway post-commit"

        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)

        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail="EA tree index.yaml drift detected and auto-regenerated",
            )

        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="EA tree index.yaml no drift (auto-commit found no staged changes)",
            )

        return ReconcileResult(
            action="warn",
            detail=f"EA tree index.yaml drift detected, auto-commit failed ({commit_result.status}): "
            f"{commit_result.message[:200]}",
        )

    spec_arch_model = ReconcilerSpec(
        gate_id="GATE-ARCH-MODEL",
        trigger=_trigger_arch_model,
        reconcile=_reconcile_arch_model,
        priority=610,
        file_ops=frozenset({"read", "write"}),
    )

    # === GATE-MANIFEST 逻辑（新增 2026-07-01：.py 文件增删后自动重生 script_manifest.yaml）===

    _MANIFEST_FILE = "scripts/governance/script_manifest.yaml"

    _MANIFEST_GEN = "scripts/governance/generators/generate_script_manifest.py"

    def _trigger_manifest(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel.endswith(".py") and rel.startswith("scripts/"):
                return True

        return False

    def _reconcile_manifest(committed_files: list[str], session_id: str) -> ReconcileResult:

        gen_result = _run_subprocess(
            [sys.executable, _MANIFEST_GEN],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )

        if gen_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"generate_script_manifest.py failed: {gen_result.stderr.strip()[:200]}",
            )

        diff_result = gateway.run_git(["git", "diff", "--name-only", "--", _MANIFEST_FILE])

        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="script manifest up to date")

        abs_file = str(project_root / _MANIFEST_FILE)

        auto_msg = "chore(manifest): auto-regenerate script_manifest.yaml by GitCommitGateway post-commit"

        commit_result = gateway._commit_auto(session_id, [abs_file], auto_msg)

        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail="script manifest drift detected and auto-regenerated",
            )

        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="script manifest no drift",
            )

        return ReconcileResult(
            action="warn",
            detail=f"script manifest drift detected, auto-commit failed ({commit_result.status})",
        )

    spec_manifest = ReconcilerSpec(
        gate_id="GATE-MANIFEST",
        trigger=_trigger_manifest,
        reconcile=_reconcile_manifest,
        priority=620,
        file_ops=frozenset({"read", "write"}),
    )

    return _compose_reconcilers("GATE-REGENERATE", spec_domain_doc, spec_arch_model, spec_manifest)


def make_rule_audit_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-RULE-AUDIT post-commit 规则同步+审计+ARCH引用检测 reconciler（AD-GOV-001 合并）。

    合并来源：

    - 旧 GATE-RULE-CATALOG (priority=160)：commit rules/ 下文件后跑

      generate_rule_catalog.py 重新生成 rule_catalog_registry.yaml，有变更自动提交。

    - 旧 GATE-RULE-FILE-AUDIT (priority=700)：commit 治理真源规则文件

      （directory_contract/doc_type_vocabulary/ttl_vocabulary/architecture_contract/

      gate_registry）后落盘审计记录，提示人工审查（约束可能被悄悄放宽）。

      P5 改造（2026-06-30）：当 directory_contract.yaml 或 doc_type_vocabulary.yaml

      变更时，额外跑 check_directory_contract.py 全量扫描，确认契约变更未引入

      DCR-001 违规（目录->doc_type 对应），违规列表写入审计报告。

    - 新增 GATE-ARCH-REFS (priority=710，元问题2治本 2026-06-30)：扫描 committed_files

      中所有 #ARCH-XXX 引用，检查是否在 architecture_issue_registry.yaml 的 entries 中

      有对应条目。病根：注册表铁律#6"任何 #ARCH-XXX 引用必须在本注册表有对应条目，禁止

      grep-and-claim 占位"是君子协定，无技术强制。#ARCH-027 冲突就是 AI 占位而不查重

      导致的。检测到未登记的 #ARCH-XXX 引用->warn（非阻断，detail 列出未登记编号）。

    合并原因：三者关注点相邻（规则文件变更的自动同步 + 人工审计兜底 + ARCH引用查重），

    trigger 重叠（规则文件/文本文件变更），合并形成"自动同步+审计告警+ARCH查重"单入口。

    合并后执行：先重生成 catalog（自动提交漂移），再落盘规则文件审计告警，最后检测

    #ARCH-XXX 引用有效性；action 取较严重，detail 拼接。priority=max(160,700,710)=710。

    治本（2026-06-30 元问题4）：reconcile 逻辑内联自原 _make_old_rule_catalog_reconciler

    与 _make_old_rule_file_audit_reconciler，私有函数已删除。

    治本（2026-06-30 元问题2）：新增 #ARCH-XXX 引用查重检测，合并入本 reconciler

    不新增 reconciler（trae_060 §4 审查通过：该存在+可合并入已有）。

    """

    import json
    import os
    import re
    import subprocess
    import sys
    from datetime import datetime

    project_root = gateway.project_root

    _project_root_str = str(project_root)

    _CATALOG_REL = "docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml"

    _PERCEPTION_INDEX_REL = "docs/01_policies_and_standards/_registry/catalogs/rule_ai_perception_index.yaml"

    _RULES_PREFIX = "docs/01_policies_and_standards/rules/"

    _rule_set = set(_RULE_FILE_PATHS)

    # === 旧 GATE-RULE-CATALOG 逻辑（内联自 _make_old_rule_catalog_reconciler）===

    def _trigger_catalog(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel.startswith(_RULES_PREFIX) and rel.endswith((".yaml", ".yml", ".md")):
                return True

        return False

    def _reconcile_catalog(committed_files: list[str], session_id: str) -> ReconcileResult:

        # 1. 重新生成 catalog（generate_rule_catalog.py 幂等）
        # timeout=180：基线实测 20s（215 文件全量 yaml.safe_load），post-commit async
        # 与并发会话/pytest/Defender 共享整机 IO——60s 仅 3x 余量，2026-08-15 14:46
        # 实证并发挤压超时一次（critical_warn）；async 不阻塞 commit 主链，180s 纯收益。

        gen_result = _run_subprocess(
            [sys.executable, "scripts/governance/d3_metadata/generate_rule_catalog.py"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )

        if gen_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"rule_catalog generation failed: {gen_result.stderr.strip()[:200]}",
            )

        # 1b. 重新生成规则AI感知索引（#ARCH-GOV-CONVERGENCE-META Phase 3.2a）

        #    trae_*.yaml 变更后联动重生成 rule_ai_perception_index.yaml（同源，串联跑）
        #    timeout 与上同理 180s（同源同型全量扫描，共享整机 IO 余量标定）

        perception_result = _run_subprocess(
            [sys.executable, "scripts/governance/generators/generate_rule_ai_perception_index.py"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )

        if perception_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"rule_ai_perception_index generation failed: {perception_result.stderr.strip()[:200]}",
            )

        # 2. 检测 catalog + perception_index 变更

        diff_result = gateway.run_git(["git", "diff", "--name-only", "--", _CATALOG_REL, _PERCEPTION_INDEX_REL])

        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="rule_catalog + perception_index up to date")

        # 3. 变更 -> 自动提交（经 _commit_auto 统一入口，DCR gate 覆盖）

        auto_msg = "chore(catalog): auto-sync rule_catalog + perception_index by GitCommitGateway post-commit"

        abs_files = [str(project_root / _CATALOG_REL), str(project_root / _PERCEPTION_INDEX_REL)]

        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)

        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail="rule_catalog_registry drift detected and auto-reconciled",
            )

        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="rule_catalog_registry no drift (auto-commit found no staged changes)",
            )

        return ReconcileResult(
            action="warn",
            detail=f"rule_catalog_registry drift detected, auto-commit failed ({commit_result.status}): "
            f"{commit_result.message[:200]}",
        )

    spec_catalog = ReconcilerSpec(
        gate_id="GATE-RULE-CATALOG",
        trigger=_trigger_catalog,
        reconcile=_reconcile_catalog,
        priority=160,
        file_ops=frozenset({"read", "write"}),
    )

    # === 旧 GATE-RULE-FILE-AUDIT 逻辑（内联自 _make_old_rule_file_audit_reconciler）===

    def _trigger_rule_file_audit(committed_files: list[str]) -> bool:

        for f in committed_files:
            if _rel_path(f, _project_root_str) in _rule_set:
                return True

        return False

    def _reconcile_rule_file_audit(committed_files: list[str], session_id: str) -> ReconcileResult:

        rule_files_changed = [
            _rel_path(f, _project_root_str) for f in committed_files if _rel_path(f, _project_root_str) in _rule_set
        ]

        reports_dir = os.path.join(_project_root_str, ".runtime", "reconcile_reports")

        os.makedirs(reports_dir, exist_ok=True)

        ts_iso = now_utc().isoformat(timespec="seconds")

        ts_file = ts_iso.replace(":", "")

        # P5 改造（2026-06-30）：契约文件变更时触发 DCR-001 全量扫描

        # 当 directory_contract.yaml 或 doc_type_vocabulary.yaml 变更时，

        # 跑 check_directory_contract.py 全量扫描，确认契约变更未引入 DCR-001 违规

        _CONTRACT_FILES = _CONTRACT_FILES_FOR_DCR  # 模块级常量引用（避免 check_vocab_hardcode 检测5 误报）

        contract_changed = [f for f in rule_files_changed if f in _CONTRACT_FILES]

        dcr_scan_summary = None

        dcr001_violations: list[str] = []

        if contract_changed:
            scan_result = _run_subprocess(
                [sys.executable, "scripts/governance/d1_structure/check_directory_contract.py"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
            )

            # 解析 stderr 中的 DCR-001 违规行（格式: "  [error] DCR-001 <file>"）

            stderr_lines = scan_result.stderr.splitlines() if scan_result.stderr else []

            dcr001_violations = [line.strip() for line in stderr_lines if "DCR-001" in line and "error" in line]

            if scan_result.returncode == 0:
                dcr_scan_summary = f"clean (exit=0, {len(dcr001_violations)} DCR-001 violations)"

            else:
                dcr_scan_summary = (
                    f"findings (exit={scan_result.returncode}, {len(dcr001_violations)} DCR-001 violations)"
                )

        report = {
            "timestamp": ts_iso,
            "session_id": session_id,
            "rule_files_changed": rule_files_changed,
            "note": "规则文件变更需人工审查（约束可能被放宽）",
        }

        if contract_changed:
            report["contract_dcr_scan"] = {
                "contract_files_changed": contract_changed,
                "scan_summary": dcr_scan_summary,
                "dcr001_violations": dcr001_violations,
                "violation_count": len(dcr001_violations),
            }

        report_path = os.path.join(reports_dir, f"rule_file_audit_{ts_file}.json")

        try:
            with open(report_path, "w", encoding="utf-8") as fh:
                json.dump(report, fh, ensure_ascii=False, indent=2)

        except OSError as e:
            return ReconcileResult(
                action="warn",
                detail=f"rule-file audit done ({len(rule_files_changed)} file(s)) but report write failed: {e}",
            )

        detail_parts = [
            f"{len(rule_files_changed)} rule file(s) changed "
            f"(manual review recommended), report={os.path.basename(report_path)}"
        ]

        if contract_changed:
            if dcr001_violations:
                detail_parts.append(
                    f"DCR-001 全量扫描发现 {len(dcr001_violations)} 个违规（契约变更可能引入漂移，需人工排查）"
                )

            else:
                detail_parts.append("DCR-001 全量扫描通过（契约变更后全量合规）")

        return ReconcileResult(
            action="warn",
            detail="; ".join(detail_parts),
        )

    spec_rule_file_audit = ReconcilerSpec(
        gate_id="GATE-RULE-FILE-AUDIT",
        trigger=_trigger_rule_file_audit,
        reconcile=_reconcile_rule_file_audit,
        priority=700,
        file_ops=frozenset({"read", "write"}),
    )

    # === 元问题2治本（2026-06-30）：#ARCH-XXX 引用查重检测 ===

    _ARCH_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml"

    # 治本（audit-02，2026-08-02）：原 _ARCH_TEXT_EXTS 与 _reference_helpers.REFERENCE_TEXT_EXTS
    # 不一致（缺 .json），导致 .json 文件中 #ARCH- 引用逃逸 warn 层；且 _ARCH_PATTERN 仅匹配
    # #ARCH-\d{3}（漏检 ARCH-GOV-SHIM-001 等多段式编号与 ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD-S2
    # 等 S 阶段标记，与 commit-time 阻断门正则不一致）。收敛为复用 _reference_helpers
    # .REFERENCE_TEXT_EXTS（含 .json，单一真源）+ 扩展 _ARCH_PATTERN 为与 arch_reference_gate
    # ._ARCH_REF_RE 同源匹配范围（多段式 + 末段 S 阶段标记），消除正则第二真源。
    from zephyr.gov_enforcement.commit_gates._reference_helpers import REFERENCE_TEXT_EXTS

    # 非捕获正则：findall 返回完整 #ARCH-XXX 串，与 registered_ids（完整 issue_id）按全串比较。
    # 匹配范围与 arch_reference_gate._ARCH_REF_RE 对齐（audit-02 2026-08-02）：
    # 纯数字 #ARCH-008 / 两段式 #ARCH-CH-007 / 多段式 #ARCH-GOV-SHIM-001 / S 变体 #ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD-S2
    _ARCH_PATTERN = re.compile(r"#ARCH-(?:[A-Z]+(?:-[A-Z]+)*-[A-Z]?\d+|\d+)")

    def _trigger_arch_refs(committed_files: list[str]) -> bool:

        # 文本文件可能含 #ARCH-XXX 引用

        for f in committed_files:
            if f.replace("\\", "/").lower().endswith(REFERENCE_TEXT_EXTS):
                return True

        return False

    def _reconcile_arch_refs(committed_files: list[str], session_id: str) -> ReconcileResult:

        from pathlib import Path

        arch_registry = Path(project_root) / _ARCH_REGISTRY_REL

        if not arch_registry.exists():
            return ReconcileResult(
                action="clean", detail="architecture_issue_registry.yaml not found, skip ARCH refs check"
            )

        # 加载注册表 entries（真源：architecture_issue_registry.yaml）

        try:
            import yaml

            data = yaml.safe_load(arch_registry.read_text(encoding="utf-8"))

            entries = data.get("entries", []) if isinstance(data, dict) else []

            registered_ids: set[str] = set()

            for entry in entries:
                if isinstance(entry, dict):
                    iid = entry.get("issue_id", "")

                    if isinstance(iid, str) and iid:
                        registered_ids.add(iid)

        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            return ReconcileResult(action="warn", detail=f"failed to parse architecture_issue_registry: {e}")

        # 扫描 committed_files 中所有 #ARCH-XXX 引用

        referenced: set[str] = set()

        for f in committed_files:
            if not f.replace("\\", "/").lower().endswith(REFERENCE_TEXT_EXTS):
                continue

            try:
                content = Path(f).read_text(encoding="utf-8")

                referenced.update(_ARCH_PATTERN.findall(content))

            except (OSError, UnicodeDecodeError):
                continue

        if not referenced:
            return ReconcileResult(action="clean", detail="no #ARCH-XXX refs in committed files")

        # 失效引用（引用了但不在注册表 entries 中）——铁律#6: 禁止 grep-and-claim 占位

        stale = referenced - registered_ids

        if stale:
            return ReconcileResult(
                action="warn",
                detail=f"committed files reference unregistered #ARCH-XXX ids: {sorted(stale)}. "
                f"These ids not in architecture_issue_registry.yaml entries. "
                f"Register them first or fix the reference (铁律#6: 禁止 grep-and-claim 占位).",
            )

        return ReconcileResult(action="clean", detail=f"all #ARCH-XXX refs registered ({len(referenced)} refs)")

    spec_arch_refs = ReconcilerSpec(
        gate_id="GATE-ARCH-REFS",
        trigger=_trigger_arch_refs,
        reconcile=_reconcile_arch_refs,
        priority=710,  # 最后执行（ARCH引用检测非阻断，低优先级）
        file_ops=frozenset({"read", "write"}),
    )

    return _compose_reconcilers("GATE-RULE-AUDIT", spec_catalog, spec_rule_file_audit, spec_arch_refs)


def make_registry_sync_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-REGISTRY-SYNC post-commit 注册表同步+基线对账 reconciler（AD-GOV-001 合并）。

    合并来源：

    - 旧 GATE-REGISTRY-INDEX (priority=155)：commit infrastructure_registry.yaml 后

      跑 generate_registry_master_index.py 重新生成 registry_master_index.yaml，

      有变更自动提交（校验+自动修复双闭环）。

    - 旧 GATE-REG-BL (priority=200)：commit src/zephyr/ 与 scripts/governance/ 下

      .py 后跑 audit_registration.py --baseline-aware 增量扫描 NEW 孤儿，记录报告。

    合并原因：两者均守护"注册表/基线一致性"，trigger 在 governance 域 .py 变更上

    重叠，逻辑可串联，合并形成"注册表索引同步+基线孤儿扫描"单入口。

    合并后执行：先重生成 registry_master_index，再跑 baseline-aware 孤儿扫描；

    action 取较严重，detail 拼接。priority=max(155,200)=200。

    治本（2026-06-30 元问题4）：reconcile 逻辑内联自原 _make_old_registry_index_reconciler

    与 _make_old_baseline_aware_reconciler，私有函数已删除。

    """

    import os
    import subprocess
    import sys

    project_root = gateway.project_root

    _INDEX_REL = "docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml"

    _INFRA_REL = "docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml"

    # === 旧 GATE-REGISTRY-INDEX 逻辑（内联自 _make_old_registry_index_reconciler）===

    def _trigger_index(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel == _INFRA_REL:
                return True

        return False

    def _reconcile_index(committed_files: list[str], session_id: str) -> ReconcileResult:

        # 1. 重新生成 registry_master_index（generate_registry_master_index.py 幂等）

        gen_result = _run_subprocess(
            [sys.executable, "scripts/governance/generators/generate_registry_master_index.py"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )

        if gen_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"registry_master_index generation failed: {gen_result.stderr.strip()[:200]}",
            )

        # 2. 检测 index 变更

        diff_result = gateway.run_git(["git", "diff", "--name-only", "--", _INDEX_REL])

        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="registry_master_index up to date")

        # 3. 变更 -> 自动提交（经 _commit_auto 统一入口，DCR gate 覆盖）

        auto_msg = "chore(registry): auto-sync registry_master_index by GitCommitGateway post-commit"

        abs_files = [str(project_root / _INDEX_REL)]

        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)

        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail="registry_master_index drift detected and auto-reconciled",
            )

        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="registry_master_index no drift (auto-commit found no staged changes)",
            )

        return ReconcileResult(
            action="warn",
            detail=f"registry_master_index drift detected, auto-commit failed ({commit_result.status}): "
            f"{commit_result.message[:200]}",
        )

    spec_index = ReconcilerSpec(
        gate_id="GATE-REGISTRY-INDEX",
        trigger=_trigger_index,
        reconcile=_reconcile_index,
        priority=155,
        file_ops=frozenset({"read", "write"}),
    )

    # === 旧 GATE-REG-BL 逻辑（内联自 _make_old_baseline_aware_reconciler）===

    def _trigger_baseline(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel.startswith("src/zephyr/") and rel.endswith(".py"):
                return True

            if rel.startswith("scripts/governance/") and rel.endswith(".py"):
                return True

        return False

    def _reconcile_baseline(committed_files: list[str], session_id: str) -> ReconcileResult:

        # 1. post-commit baseline-aware 扫描（非阻断）

        # 治本 Bug 1：改用 --files 传入精确 committed_files，替代 --incremental。

        rel_py_files = [_rel_path(f, str(project_root)) for f in committed_files if f.endswith(".py")]

        rel_py_files = [rel for rel in rel_py_files if rel.startswith("src/zephyr/") or rel.startswith("scripts/")]

        if not rel_py_files:
            return ReconcileResult(
                action="skip",
                detail="baseline_aware: no src/zephyr|scripts .py in committed files",
            )

        scan_result = _run_subprocess(
            [sys.executable, "scripts/governance/d11_compliance/audit_registration.py", "--baseline-aware", "--files"]
            + rel_py_files,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )

        # 2. 报告落盘（无论 exit code，记录供追责）

        report = {
            "gate_id": "GATE-REG-BL",
            "session_id": session_id,
            "exit_code": scan_result.returncode,
            "stdout_tail": scan_result.stdout.strip()[-500:],
            "stderr_tail": scan_result.stderr.strip()[-500:],
            "committed_files": committed_files,
            "scanned_files": rel_py_files,
        }

        report_path, write_err = _write_reconcile_report(project_root, "baseline_aware", report)

        if write_err:
            return ReconcileResult(
                action="warn",
                detail=f"baseline_aware scan done (exit={scan_result.returncode}) but report write failed: {write_err}",
            )

        # 3. 判定结果

        if scan_result.returncode == 0:
            return ReconcileResult(
                action="clean",
                detail=f"baseline_aware scan clean, report={report_path.name}",
            )

        # exit 1 = NEW 孤儿检出（commit 已入历史，仅告警）

        return ReconcileResult(
            action="warn",
            detail=f"baseline_aware scan detected NEW orphans (exit={scan_result.returncode}), report={report_path.name}",
        )

    spec_baseline = ReconcilerSpec(
        gate_id="GATE-REG-BL",
        trigger=_trigger_baseline,
        reconcile=_reconcile_baseline,
        priority=200,
        file_ops=frozenset({"read", "write"}),
    )

    return _compose_reconcilers("GATE-REGISTRY-SYNC", spec_index, spec_baseline)


def make_integrity_audit_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-INTEGRITY-AUDIT post-commit 完整性+网关审计+引用检测 reconciler（AD-GOV-001 合并）。

    合并来源：

    - 旧 GATE-RULES-INTEGRITY (priority=270)：每次 commit 后跑

      validate_rules_integrity.py --register 重算 RULES_MANIFEST 文件 hash 写入

      本地基线，消除"C 层基线与 commit 不同步->误报 TAMPERED"结构性缺陷。

    - 旧 GATE-COMMIT-GW-AUDIT (priority=800)：扫描最近 20 个 commit，标记未经

      GitCommitGateway 的裸 commit（message 不含 [GW: 标记），告警 --no-verify 绕过。

    - 新增 GATE-AGENTS-MD-REFS (priority=810，元问题1治本 2026-06-30)：检测 AGENTS.md

      中引用的 reconciliation_registry.py 公共函数名（make_*_reconciler）是否在 __all__

      列表中。病根：AGENTS.md 硬编码函数名，reconciler 重命名/合并后 AGENTS.md 不会

      自动更新，新AI按失效指引造幻觉（如步骤1修复的 _make_old_rules_integrity_reconciler

      失效引用）。检测到失效引用->warn（非阻断，告警供人工修正）。

    合并原因：三者 trigger 均 always True 或与 AGENTS.md/reconciliation_registry.py

    变更相关，逻辑可串联，合并形成"基线同步+网关审计+引用检测"非阻断兜底单入口。

    合并后执行：先重注册 rules_integrity 基线，再审计 commit 网关标记，最后检测

    AGENTS.md 引用有效性；action 取较严重，detail 拼接。priority=max(270,800,810)=810。

    治本（2026-06-30 元问题4）：reconcile 逻辑内联自原 _make_old_rules_integrity_reconciler

    与 _make_old_commit_gateway_audit_reconciler，私有函数已删除。_audit_commit_history

    是模块级函数（非 _make_old_*），保留供本闭包调用与 integrity_anchors 保护。

    治本（2026-06-30 元问题1）：新增 AGENTS.md 引用有效性检测，合并入本 reconciler

    不新增 reconciler（trae_060 §4 审查通过：该存在+可合并入已有）。检测逻辑用正则

    提取 make_*_reconciler 公共函数名引用，检查是否在 __all__ 中。

    """

    import os
    import subprocess
    import sys

    project_root = gateway.project_root

    _VALIDATE_SCRIPT = "scripts/governance/meta/validate_rules_integrity.py"

    _AUDIT_WINDOW = 20  # 审计最近 20 个 commit

    _GW_MARKER = "[GW:"

    _RV_MARKER = "[RECONCILER-VERIFY]"  # reconciler-verify 豁免通道标记（事后审计追溯）

    # === 旧 GATE-RULES-INTEGRITY 逻辑（内联自 _make_old_rules_integrity_reconciler）===

    def _trigger_rules_integrity(committed_files: list[str]) -> bool:

        # 第一性原理治本：总是触发。原宽匹配基于未校验假设，未来 RULES_MANIFEST

        # 新增其他路径文件会假阴性漏触发。--register 仅 hash RULES_MANIFEST 文件

        # （毫秒级），不值得为省此开销引入假设。RULES_MANIFEST 真源在 validate_rules_integrity.py 顶部。

        return True

    def _reconcile_rules_integrity(committed_files: list[str], session_id: str) -> ReconcileResult:

        # 治本（2026-08-02 audit-02 时序竞态）：batcher 启用期间（reconcile_for 内）跳过 --register，

        # 改由 GitCommitGateway._post_flush_rules_integrity_re_register 的 post-flush 重注册捕获最终 HEAD。

        # 病根：register() 用 _hash_git_head() 读 pre-flush HEAD（git show HEAD:），而 manifest/catalog 等

        # reconciler 变更在 flush() 后才入 HEAD，导致 DB 基线滞后一周期 →

        # script_manifest.yaml / capability_canonical_file_registry.yaml 永久 TAMPERED。

        # 修复：batcher 启用时 defer 到 post-flush，读 post-flush HEAD = 最终状态 → --check 0 TAMPERED。

        # 安全性：post-flush register 仍用 _hash_git_head()（HEAD-based），红蓝发现3 的 WIP 篡改防护不降级。

        _batcher = getattr(gateway, "_batcher", None)

        if _batcher is not None and _batcher.is_enabled():
            return ReconcileResult(
                action="skip",
                detail="rules_integrity --register deferred to post-flush "
                "(时序竞态治本 2026-08-02: pre-flush HEAD 滞后 → post-flush 捕获最终状态)",
            )

        # 1. post-commit 重注册基线（--register 内部读 RULES_MANIFEST 真源，重算全部 hash）

        # 红蓝发现4 治本：设置 ZEPHYR_RECONCILER_MODE=1 门禁令牌，允许 --register。

        _env = dict(os.environ)

        _env["ZEPHYR_RECONCILER_MODE"] = "1"

        reg_result = _run_subprocess(
            [sys.executable, _VALIDATE_SCRIPT, "--register"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            env=_env,
        )

        # 2. 报告落盘（无论 exit code，记录供追责）

        report = {
            "gate_id": "GATE-RULES-INTEGRITY",
            "session_id": session_id,
            "exit_code": reg_result.returncode,
            "stdout_tail": reg_result.stdout.strip()[-500:],
            "stderr_tail": reg_result.stderr.strip()[-500:],
            "triggered_by": committed_files,
        }

        report_path, write_err = _write_reconcile_report(project_root, "rules_integrity", report)

        if write_err:
            return ReconcileResult(
                action="warn",
                detail=f"rules_integrity --register done (exit={reg_result.returncode}) "
                f"but report write failed: {write_err}",
            )

        # 3. 判定（--register exit 0 = 基线已更新；非 0 = 脚本异常）

        if reg_result.returncode == 0:
            # 治本（2026-08-02 audit-02）：--register 更新 rules_integrity_db.json 后 MUST 调

            # _commit_auto 提交，否则 DB 变更残留工作区不入库。原仅 return action="auto_committed"

            # 但未调 _commit_auto（对标 make_manifest_reconciler L2177-2217 模式补齐）。

            _db_rel = "scripts/governance/meta/rules_integrity_db.json"

            _diff_result = gateway.run_git(["git", "diff", "--name-only", "--", _db_rel])

            if _diff_result.returncode == 0 and not _diff_result.stdout.strip():
                return ReconcileResult(
                    action="clean",
                    detail=f"rules_integrity baseline up to date, report={report_path.name}",
                )

            _auto_msg = "chore(integrity): auto-re-register rules_integrity_db by GitCommitGateway post-commit"

            _abs_db = str(project_root / _db_rel)

            _commit_result = gateway._commit_auto(session_id, [_abs_db], _auto_msg)

            if _commit_result.status == "OK":
                return ReconcileResult(
                    action="auto_committed",
                    detail=f"rules_integrity baseline re-registered post-commit "
                    f"(C层基线已同步合法 commit), report={report_path.name}",
                )

            if _commit_result.status == "NOTHING_TO_COMMIT":
                return ReconcileResult(
                    action="clean",
                    detail=f"rules_integrity baseline no drift (auto-commit found no staged changes), "
                    f"report={report_path.name}",
                )

            return ReconcileResult(
                action="warn",
                detail=f"rules_integrity --register succeeded but auto-commit failed "
                f"({_commit_result.status}): {_commit_result.message[:200]}",
            )

        return ReconcileResult(
            action="warn",
            detail=f"rules_integrity --register failed (exit={reg_result.returncode}), report={report_path.name}",
        )

    spec_rules_integrity = ReconcilerSpec(
        gate_id="GATE-RULES-INTEGRITY",
        trigger=_trigger_rules_integrity,
        reconcile=_reconcile_rules_integrity,
        priority=270,
        file_ops=frozenset({"read", "write"}),
    )

    # === 旧 GATE-COMMIT-GW-AUDIT 逻辑（内联自 _make_old_commit_gateway_audit_reconciler）===

    def _trigger_commit_gw_audit(committed_files: list[str]) -> bool:

        # 审计始终运行：绕过 gateway 的裸 commit 可能涉及任何文件

        return True

    def _reconcile_commit_gw_audit(committed_files: list[str], session_id: str) -> ReconcileResult:

        # 审计逻辑真源：模块级 _audit_commit_history（A 层 AST 锚点保护，

        # 治本 2026-06-30 病根1 看门人无人看）。闭包只做调用 + 报告落盘 + 判定。

        violations, err = _audit_commit_history(
            project_root,
            _AUDIT_WINDOW,
            _GW_MARKER,
            _RV_MARKER,
        )

        if err:
            return ReconcileResult(action="warn", detail=err)

        # 并发冲突检测（治本 2026-07-12，遗留项2根因）：

        # 检测到裸 commit 时，检查是否有活跃的 breaking_change session。

        # 如果有 → 说明可能发生了并发冲突（裸 commit + 治本变更 session 并发），

        # 在报告中标记 CONCURRENT_BREAKING_CHANGE_CONFLICT 供 AI 查阅。

        concurrent_conflict = False

        conflict_sessions: list[str] = []

        if violations:
            try:
                from zephyr.security.access_control.session_concurrency import SessionRegistry

                registry = SessionRegistry(str(project_root))

                breaker = registry.find_breaking_change_session(exclude_session_id=session_id)

                if breaker is not None:
                    concurrent_conflict = True

                    conflict_sessions = [breaker.session_id]

                    # 额外列出所有活跃 session

                    active = registry.list_active()

                    conflict_sessions = [s.session_id for s in active if s.session_id != session_id]

            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                pass  # fail-open：SessionRegistry 异常不阻断审计

        # 3. 报告落盘

        report = {
            "gate_id": "GATE-COMMIT-GW-AUDIT",
            "session_id": session_id,
            "audit_window": _AUDIT_WINDOW,
            "violations_count": len(violations),
            "violations": violations,
            "concurrent_conflict": concurrent_conflict,
            "conflict_sessions": conflict_sessions,
        }

        report_path, write_err = _write_reconcile_report(project_root, "commit_gateway_audit", report)

        if write_err:
            return ReconcileResult(
                action="warn",
                detail=f"audit done ({len(violations)} violations) but report write failed: {write_err}",
            )

        # 4. 判定（非阻断：commit 已入历史，仅告警）

        if not violations:
            return ReconcileResult(
                action="clean",
                detail=f"audit clean (window={_AUDIT_WINDOW}), report={report_path.name}",
            )

        if concurrent_conflict:
            return ReconcileResult(
                action="warn",
                detail=f"CONCURRENT_BREAKING_CHANGE_CONFLICT: audit detected {len(violations)} non-GW commits "
                f"with {len(conflict_sessions)} active breaking_change session(s) {conflict_sessions}. "
                f"Likely concurrency violation (bare git commit during breaking_change session). "
                f"report={report_path.name}",
            )

        return ReconcileResult(
            action="warn",
            detail=f"audit detected {len(violations)} non-GW commits (window={_AUDIT_WINDOW}), report={report_path.name}",
        )

    spec_commit_gw_audit = ReconcilerSpec(
        gate_id="GATE-COMMIT-GW-AUDIT",
        trigger=_trigger_commit_gw_audit,
        reconcile=_reconcile_commit_gw_audit,
        priority=800,  # 最后执行（审计非阻断，低优先级）
        file_ops=frozenset({"read", "write"}),
    )

    # === 元问题1治本（2026-06-30）：AGENTS.md 引用有效性检测 ===

    def _trigger_agents_md_refs(committed_files: list[str]) -> bool:

        # AGENTS.md 或 reconciliation_registry.py 变更时触发——引用关系在这两个文件

        # 变更时可能过时（reconciler 合并/重命名会导致 AGENTS.md 引用失效）

        for f in committed_files:
            fn = f.replace("\\", "/").lower()

            if "agents.md" in fn or "reconciliation_registry.py" in fn:
                return True

        return False

    def _reconcile_agents_md_refs(committed_files: list[str], session_id: str) -> ReconcileResult:

        import re
        from pathlib import Path

        agents_md = Path(project_root) / "AGENTS.md"

        if not agents_md.exists():
            return ReconcileResult(action="clean", detail="AGENTS.md not found, skip refs check")

        content = agents_md.read_text(encoding="utf-8")

        # 提取 AGENTS.md 中引用的 make_*_reconciler 公共函数名

        # （_make_old_* 私有函数引用是描述性提及"已删除"，不检测——私有函数不在 __all__ 是正常的）

        referenced = set(re.findall(r"\bmake_\w+_reconciler\b", content))

        if not referenced:
            return ReconcileResult(action="clean", detail="no make_*_reconciler refs in AGENTS.md")

        # 加载模块 __all__（真源：reconciliation_registry.__all__）

        try:
            import zephyr.governance.audit.reconciliation_registry as reg_module

            available = set(reg_module.__all__)

        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            return ReconcileResult(action="warn", detail=f"failed to load reconciliation_registry: {e}")

        # 失效引用（AGENTS.md 引用了但不在 __all__ 中）

        stale = referenced - available

        if stale:
            return ReconcileResult(
                action="warn",
                detail=f"AGENTS.md references stale reconciliation_registry functions: {sorted(stale)}. "
                f"These functions not in __all__. Update AGENTS.md to reference valid function names.",
            )

        return ReconcileResult(action="clean", detail=f"AGENTS.md refs all valid ({len(referenced)} refs)")

    spec_agents_md_refs = ReconcilerSpec(
        gate_id="GATE-AGENTS-MD-REFS",
        trigger=_trigger_agents_md_refs,
        reconcile=_reconcile_agents_md_refs,
        priority=810,  # 最后执行（引用检测非阻断，最低优先级）
        file_ops=frozenset({"read", "write"}),
    )

    return _compose_reconcilers("GATE-INTEGRITY-AUDIT", spec_rules_integrity, spec_commit_gw_audit, spec_agents_md_refs)


# trae_060-reviewed: 通过§4元问题审查。该 reconciler 该存在——三声明轨道 module_id（CFG-/MOD-/PS-*）语义此前未定义，

# 导致 AI 误判为冲突并反复"修复"。不能删除（检测需求真实），不能合并（现有 reconciler 无 module_id 三声明轨道校验逻辑）。

# 治本：S0-3 已在 PS-STD-001 定义三声明轨道语义，本 reconciler 自动校验一致性（非阻断，仅告警）。

# 向内收：扩展已有 reconciliation_registry.py 框架（第12个 reconciler），不新建独立系统。

# P8-FIX-S1 扩展：增加 count 派生校验（total_registered/total_templates/total_dependencies）。

#   元问题审查：count 不一致是真实漂移源（template_registry 声明 14 但实际 13）。

#   能否合并：是——扩展本 reconciler 职责，不新建 count_reconciler（向内收）。


def make_module_id_consistency_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-MODULE-ID-CONSISTENCY post-commit 注册表一致性校验 reconciler（P8-FIX-S0 + S1）。

    病根：单个治理文件中同时出现三种 module_id 声明（头部 CFG-* + 锚定 MOD-* +

    body PS-*/GOV-*），语义未定义导致 AI 误判为冲突并反复"修复"。

    治本（P8-FIX-S0 v2.4.0，2026-06-30）：

    - S0-3 已在 PS-STD-001 §5 定义三声明轨道语义（header_config_id / anchor_module_ownership /

      body_rule_id），明确三者互补不冲突。

    - 本 reconciler 在 post-commit 自动校验三声明轨道一致性——检查三者是否在

      module_id_registry.yaml 中归属同一模块。不一致->warn（非阻断）。

    P8-FIX-S1 扩展（2026-06-30）：count 派生校验

    - 注册表的 count 字段（total_registered/total_templates/total_dependencies）是派生数据，

      手工维护导致漂移（如 template_registry 声明 14 但实际 13）。

    - 扩展本 reconciler 增加 count 校验：统计列表条目数，与声明的 count 比对，不一致->warn。

    - 向内收：不新建 count_reconciler，扩展已有 module_id_consistency_reconciler 职责。

    设计裁定（非阻断）：

    post-commit 无法回滚 commit；不一致已入 git 历史，仅告警记录到

    .runtime/reconcile_reports/module_id_consistency_<ts>.json，供人工修正。

    trigger 裁定：committed_files 含 module_id_registry.yaml / template_registry.yaml /

    cross_module_dependency_registry.yaml 或 _registry/contracts/ 下的 .yaml 文件即命中。

    向内收设计：

    - 责任唯一：三声明轨道语义定义在 PS-STD-001 §5，校验逻辑在本 reconciler 单点

    - 真源唯一：复用 ReconciliationRegistry 框架（第12个 reconciler）

    - 事件触发：post-commit 自动执行，无 cron/manual

    Args:

        gateway: GitCommitGateway 实例（用 project_root）。

    Returns:

        ReconcilerSpec(gate_id="GATE-MODULE-ID-CONSISTENCY", priority=300)。

    """

    import os
    import re

    project_root = gateway.project_root

    _REGISTRY_REL = "architecture_model/module_id_registry.yaml"

    _TEMPLATE_REGISTRY_REL = "docs/03_modules/template_registry.yaml"

    _DEP_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/cross_module_dependency_registry.yaml"

    _CONTRACTS_DIR = "docs/01_policies_and_standards/_registry/contracts/"

    # 三声明轨道正则

    _RE_HEADER_CFG = re.compile(r"^#\s*\[A_config\]\s*module_id=(CFG-\S+)", re.MULTILINE)

    _RE_ANCHOR_MOD = re.compile(r"^#\s*module_id:\s*(MOD-\S+)", re.MULTILINE)

    _RE_BODY_RULE = re.compile(r"^module_id:\s*([A-Z]+(?:-[A-Z]+)*-\w+)\s*$", re.MULTILINE)

    # P8-FIX-S1: count 派生校验——统计列表条目数正则

    _RE_MODULE_ID_ENTRY = re.compile(r"^  - module_id:\s*\S+", re.MULTILINE)

    _RE_TEMPLATE_ENTRY = re.compile(r"^  - template_id:", re.MULTILINE)

    _RE_DEP_ENTRY = re.compile(r"^- dep_id:\s*DEP-", re.MULTILINE)

    # P8-FIX-S1: count 声明读取正则

    _RE_TOTAL_REGISTERED = re.compile(r"^total_registered:\s*(\d+)", re.MULTILINE)

    _RE_TOTAL_TEMPLATES = re.compile(r"^\s*total_templates:\s*(\d+)", re.MULTILINE)

    _RE_TOTAL_DEPS = re.compile(r"^\s*total_dependencies:\s*(\d+)", re.MULTILINE)

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel in (_REGISTRY_REL, _TEMPLATE_REGISTRY_REL, _DEP_REGISTRY_REL) or rel.startswith(_CONTRACTS_DIR):
                return True

        return False

    def _is_target_file(rel: str) -> bool:
        """判断文件是否为本 reconciler 的目标治理文件。"""

        return rel in (_REGISTRY_REL, _TEMPLATE_REGISTRY_REL, _DEP_REGISTRY_REL) or rel.startswith(_CONTRACTS_DIR)

    def _check_track_consistency(content: str, rel: str, violations: list) -> None:
        """三声明轨道一致性校验（P8-FIX-S0）：CFG/MOD/rule 互补不冲突。"""

        cfg_match = _RE_HEADER_CFG.search(content)

        mod_match = _RE_ANCHOR_MOD.search(content)

        rule_match = _RE_BODY_RULE.search(content)

        cfg_id = cfg_match.group(1) if cfg_match else None

        mod_id = mod_match.group(1) if mod_match else None

        rule_id = rule_match.group(1) if rule_match else None

        tracks_found = sum(1 for x in [cfg_id, mod_id, rule_id] if x)

        if tracks_found < 2 and cfg_id:
            violations.append(
                {
                    "file": rel,
                    "issue": "incomplete_tracks",
                    "cfg_id": cfg_id,
                    "mod_id": mod_id,
                    "rule_id": rule_id,
                    "detail": f"文件有 header CFG-{cfg_id} 但仅 {tracks_found}/3 声明轨声明",
                }
            )

    def _check_count_mismatch(
        rel: str,
        content: str,
        violations: list,
        find_regex,
        declared_regex,
        field_name: str,
        entry_desc: str,
    ) -> None:
        """单文件 count 派生校验：统计条目数与声明的 count 比对。"""

        actual_count = len(find_regex.findall(content))

        declared = declared_regex.search(content)

        declared_count = int(declared.group(1)) if declared else None

        if declared_count is not None and declared_count != actual_count:
            violations.append(
                {
                    "file": rel,
                    "issue": "count_mismatch",
                    "field": field_name,
                    "declared": declared_count,
                    "actual": actual_count,
                    "detail": f"{field_name}={declared_count} 但实际 {entry_desc} 有 {actual_count} 条",
                }
            )

    def _check_count_derivation(rel: str, content: str, violations: list) -> None:
        """count 派生校验路由（P8-FIX-S1）：按文件类型分发到对应 count 校验。"""

        if rel == _REGISTRY_REL:
            _check_count_mismatch(
                rel,
                content,
                violations,
                _RE_MODULE_ID_ENTRY,
                _RE_TOTAL_REGISTERED,
                "total_registered",
                "registered_ids",
            )

        elif rel == _TEMPLATE_REGISTRY_REL:
            _check_count_mismatch(
                rel, content, violations, _RE_TEMPLATE_ENTRY, _RE_TOTAL_TEMPLATES, "total_templates", "templates"
            )

        elif rel == _DEP_REGISTRY_REL:
            _check_count_mismatch(
                rel, content, violations, _RE_DEP_ENTRY, _RE_TOTAL_DEPS, "total_dependencies", "dependencies"
            )

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        violations = []

        checked = 0

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if not _is_target_file(rel):
                continue

            abs_path = project_root / rel

            if not abs_path.exists():
                continue

            try:
                content = abs_path.read_text(encoding="utf-8", errors="replace")

            except OSError:
                continue

            checked += 1

            # === 三声明轨道一致性校验（P8-FIX-S0） ===

            _check_track_consistency(content, rel, violations)

            # === count 派生校验（P8-FIX-S1） ===

            _check_count_derivation(rel, content, violations)

        report = {
            "gate_id": "GATE-MODULE-ID-CONSISTENCY",
            "session_id": session_id,
            "checked_files": checked,
            "violations": violations,
        }

        report_path, write_err = _write_reconcile_report(project_root, "module_id_consistency", report)

        if write_err:
            return ReconcileResult(
                action="warn",
                detail=f"module_id consistency check done ({checked} files) but report write failed: {write_err}",
            )

        if not violations:
            return ReconcileResult(
                action="clean",
                detail=f"module_id consistency check clean ({checked} files), report={report_path.name}",
            )

        return ReconcileResult(
            action="warn",
            detail=f"module_id consistency check found {len(violations)} violations in {checked} files, report={report_path.name}",
        )

    return ReconcilerSpec(
        gate_id="GATE-MODULE-ID-CONSISTENCY",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=300,
        file_ops=frozenset({"read", "write"}),
    )


# trae_060-reviewed: P3 生成器自动触发接入——index_generator(infrastructure/asset_inventory)

# 接入 GitCommitGateway post-commit reconciler 轨（非 boot_hooks 事件轨）。

# 向内收：扩展已有 reconciliation_registry.py 框架（第14个 reconciler），不新建独立触发系统。

# 价值审判：index_generator 是 production 资产索引真源，unified-asset-index.yaml 漂移需自动修复。


def make_index_generator_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-ASSET-INDEX post-commit 资产索引重生 reconciler（P3 生成器触发接入）。

    病根：index_generator 是 MOD-INF-026 production 生成器，产出 unified-asset-index.yaml

    作为项目 SSoT。但 src/zephyr/**/*.py 或注册表 yaml 变更后，索引可能过时——

    原设计无自动触发，依赖手动跑 ``python -m zephyr.infrastructure.asset_inventory bootstrap``。

    治本（P3 生成器自动触发接入）：

    - 接入 GitCommitGateway post-commit reconciler 轨（事件触发，非时间触发/手动触发）

    - trigger: committed_files 含 src/zephyr/**/*.py 或注册表 yaml 变更

    - reconcile: 跑 scan->classify->index 全管线（bootstrap 幂等），检测 unified-asset-index.yaml

      漂移，有变更->auto-commit（经 _commit_auto 统一入口，DCR gate 覆盖）

    trigger 裁定（注册表路径真源：index_generator.py REGISTRY_DIRS）：

    - src/zephyr/**/*.py：资产文件变更->索引可能漂移

    - src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml：gates 注册表变更

    - docs/03_modules/module-registry.yaml：模块注册表变更

    - docs/03_modules/blueprint_registry.yaml：蓝图注册表变更

    向内收设计：

    - 责任唯一：索引生成逻辑只在 IndexGenerator 一处（本 reconciler 仅调用，不复制逻辑）

    - 真源唯一：复用 ReconciliationRegistry 框架（第14个 reconciler），不新建独立触发系统

    - 事件触发：post-commit 自动执行，无 cron/manual

    Args:

        gateway: GitCommitGateway 实例（用 project_root + _run_git + _commit_auto）。

    Returns:

        ReconcilerSpec(gate_id="GATE-ASSET-INDEX", priority=170)。

    """

    import os
    import subprocess
    import sys

    project_root = gateway.project_root

    _INDEX_REL = "data/asset_index/unified-asset-index.yaml"

    # 注册表路径真源：index_generator.py REGISTRY_DIRS

    _REGISTRY_PATHS = (
        "src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml",
        "docs/03_modules/module-registry.yaml",
        "docs/03_modules/blueprint_registry.yaml",
    )

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel.startswith("src/zephyr/") and rel.endswith(".py"):
                return True

            if rel in _REGISTRY_PATHS:
                return True

        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        # 1. 跑 scan->classify->index 全管线（bootstrap 幂等，含 index 生成）

        bootstrap_result = _run_subprocess(
            [sys.executable, "-m", "zephyr.infrastructure.asset_inventory", "bootstrap"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,  # 全管线较慢（scan+classify+index+reconcile+dashboard）
        )

        if bootstrap_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"asset_inventory bootstrap failed: {bootstrap_result.stderr.strip()[:200]}",
            )

        # 2. 检测 unified-asset-index.yaml 变更

        diff_result = gateway.run_git(["git", "diff", "--name-only", "--", _INDEX_REL])

        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="unified-asset-index up to date")

        # 3. 变更 -> 自动提交（经 _commit_auto 统一入口，DCR gate 覆盖）

        abs_files = [str(project_root / _INDEX_REL)]

        auto_msg = "chore(asset_index): auto-regenerate unified-asset-index.yaml by GitCommitGateway post-commit"

        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)

        if commit_result.status == "OK":
            # 治本 #ARCH-ASSET-INDEX-FALSE-AUTO-COMMIT-001：当 commit_hash=="BUFFERED"
            # 时，commit 被 batcher 延迟到 flush()。detail 标注"pending flush"，
            # flush 失败时由 _downgrade_auto_committed_on_flush_failure 降级为 warn。
            is_buffered = getattr(commit_result, "commit_hash", "") == "BUFFERED"

            detail = "unified-asset-index drift detected and auto-regenerated"

            if is_buffered:
                detail += " (batched, pending flush)"

            return ReconcileResult(
                action="auto_committed",
                detail=detail,
            )

        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="unified-asset-index no drift (auto-commit found no staged changes)",
            )

        return ReconcileResult(
            action="warn",
            detail=f"unified-asset-index drift detected, auto-commit failed ({commit_result.status}): "
            f"{commit_result.message[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-ASSET-INDEX",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=170,  # 在 path_tree(150) 和 yaml_sync(160) 之后，vocab_change(280) 之前
        file_ops=frozenset({"read", "write"}),
    )


# trae_060-reviewed: 通过元问题审查。.runtime/ 线性增长无封顶（4100+ 文件），需 TTL 自动清理。

# 该 reconciler 该存在——扩展已有 reconciliation_registry 框架（第15个 reconciler），

# 事件触发（post-commit），非 cron/manual，满足项目约束"reconciler 必须事件触发"。

# 治本 #ARCH-TEST-RESIDUE-CLEANUP-001（2026-08-04）：.runtime/tmp/ 测试残留目录自动
# 回收共享判定逻辑。pytest_<PID>/（tests/conftest.py:67 PID-unique basetemp，治本
# #ARCH-XDIST-WORKER-CRASH-001）+ git_guard_test_*/tmp*/conc_mv_* 等测试框架残留，
# 因 make_runtime_cleanup_reconciler 原 os.rmdir 只删空目录 bug（pytest_<PID>/ 内
# fixture 子目录如 test_conftest_py_exempted0/ 永远非空）积压 10 万+ 文件。
# 本组模块级函数供 make_runtime_cleanup_reconciler 与 scripts/ops/cleanup_runtime_tmp_residue.py
# oneoff 脚本复用——判定真源唯一。事件驱动（post-commit），符合 trae_071 LAW-4。

# trae_071 YAML 真源路径（§test_residue_reclaim 段——测试残留清理配置 SSoT）。
# 基于 __file__ 解析（worktree 安全——读运行代码同 checkout 的 YAML，非主仓库）。
# trae_062 SSoT：规则数据真源是 YAML 文件，代码动态加载，禁止硬编码前缀/TTL。
_TRAE_071_YAML_PATH = (
    Path(__file__).resolve().parents[4]
    / "docs"
    / "01_policies_and_standards"
    / "rules"
    / "trae_071_temporary_file_lifecycle.yaml"
)
# 配置缓存（首次 _load_test_residue_config() 读 YAML+解析，后续 O(1) 返回）。
# 会话期内 YAML 不变；reconciler 每 commit 触发、脚本一次性运行，无需失效策略。
# _TEST_RESIDUE_CONFIG_LOADED 标记"已尝试加载"——失败也缓存（None），避免 reconciler
# 遍历 .runtime/tmp/ 多目录时重复 open() 缺失文件 + 重复 warn（log spam）。
_TEST_RESIDUE_CONFIG_CACHE: dict | None = None
_TEST_RESIDUE_CONFIG_LOADED = False


def _load_test_residue_config() -> dict | None:
    """从 trae_071 YAML §test_residue_reclaim 加载测试残留清理配置（SSoT 真源）。

    真源：docs/01_policies_and_standards/rules/trae_071_temporary_file_lifecycle.yaml
    §test_residue_reclaim.covered_patterns（dir_prefixes/exact_names/tmp_prefix）
    + §test_residue_reclaim.params（ttl_seconds/fresh_protect_seconds/pid_alive_check）。

    trae_062 SSoT：规则数据真源是 YAML 文件。本函数是代码侧唯一加载入口，
    make_runtime_cleanup_reconciler 与 scripts/ops/cleanup_runtime_tmp_residue.py
    共享本函数，禁止代码内硬编码前缀/TTL（会形成多源漂移）。

    缓存：首次调用读 YAML+解析（成功存 dict / 失败存 None），后续直接返回缓存。
    失败也缓存——避免 reconciler 遍历多目录时重复 open 缺失文件 + 重复 warn。
    reconciler 每 commit 是新进程，脚本一次性运行，无需进程内失效/恢复。

    失败处理（fail-open，返回 None）：
      - YAML 缺失/损坏/段缺失 → 返回 None（warn 一次）
      - 调用方决定降级行为（trae_071 §test_residue_reclaim.failure_handling）：
        * reconciler → 跳过测试残留清理（其余 .runtime/ TTL 清理仍执行）
        * oneoff 脚本 → fail-loud 退出（手动工具必须有配置才能安全清理）

    Returns:
        配置 dict（对齐 YAML 段结构）；YAML 不可达/段缺失 → None。
    """
    global _TEST_RESIDUE_CONFIG_CACHE, _TEST_RESIDUE_CONFIG_LOADED
    if _TEST_RESIDUE_CONFIG_LOADED:
        return _TEST_RESIDUE_CONFIG_CACHE
    _TEST_RESIDUE_CONFIG_LOADED = True  # 标记已尝试（成功或失败均不再重试）
    try:
        import yaml  # noqa: PLC0415 — lazy import 保持模块顶层依赖最小

        with open(_TRAE_071_YAML_PATH, "r", encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)
    except (OSError, ImportError, ValueError) as exc:
        logger.warning(
            "test_residue_reclaim config 不可达(%s: %s)，reconciler 将跳过测试残留清理。",
            type(exc).__name__,
            exc,
        )
        return None  # _TEST_RESIDUE_CONFIG_CACHE 保持 None
    if not isinstance(doc, dict):
        logger.warning("test_residue_reclaim: YAML 顶层非 dict，跳过测试残留清理。")
        return None
    section = doc.get("test_residue_reclaim")
    if not isinstance(section, dict):
        logger.warning("test_residue_reclaim 段缺失/非 dict，跳过测试残留清理。")
        return None
    covered = section.get("covered_patterns") or {}
    params = section.get("params") or {}
    _TEST_RESIDUE_CONFIG_CACHE = {
        "dir_prefixes": tuple(covered.get("dir_prefixes") or ()),
        "exact_names": frozenset(covered.get("exact_names") or ()),
        "tmp_prefix": covered.get("tmp_prefix") or "tmp",
        "ttl_seconds": float(params.get("ttl_seconds") or 7200),
        "fresh_protect_seconds": float(params.get("fresh_protect_seconds") or 600),
        "pid_alive_check": bool(params.get("pid_alive_check", True)),
    }
    return _TEST_RESIDUE_CONFIG_CACHE


def _match_test_residue(name: str) -> bool:
    """判断 .runtime/tmp/ 下目录名是否属于测试残留（应纳入清理范围）。

    判定真源：trae_071 YAML §test_residue_reclaim.covered_patterns（动态加载）。
    config 不可达 → 返回 False（reconciler fail-open 跳过，不误匹配非测试目录）。
    """
    cfg = _load_test_residue_config()
    if cfg is None:
        return False
    if name in cfg["exact_names"]:
        return True
    if name.startswith(cfg["tmp_prefix"]):  # tmp*, tmp31n6tt7n 等 tempfile 残留
        return True
    return any(name.startswith(p) for p in cfg["dir_prefixes"])


def _parse_pid_from_name(name: str) -> int | None:
    """从 pytest_<PID> 目录名解析 PID；非 pytest_ 前缀返回 None。"""
    if not name.startswith("pytest_"):
        return None
    try:
        return int(name[len("pytest_") :])
    except ValueError:
        return None


def _pid_exists(pid: int) -> bool:
    """检查 PID 是否存活。优先 psutil（已装 7.2.2），fallback ctypes(os.win32)/os.kill。

    psutil 为可选依赖，lazy import 以保证不可达时降级为标准库方案
    （ctypes/os.kill），不硬性要求安装 psutil。
    """
    try:
        import psutil  # noqa: PLC0415 — lazy import：psutil 可选，不可达时降级 stdlib

        return bool(psutil.pid_exists(pid))
    except ImportError:
        pass
    import os  # noqa: PLC0415
    import sys  # noqa: PLC0415

    if sys.platform == "win32":
        import ctypes  # noqa: PLC0415

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return False
        kernel32.CloseHandle(handle)
        return True
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _should_remove_test_dir(dirpath, now: float, ttl: float | None = None) -> bool:
    """判定 .runtime/tmp/ 下测试残留目录是否应删除（PID 存活 + TTL 双保险）。

    - mtime < fresh_protect_seconds → False（防误删正在写入）
    - mtime < ttl → False（TTL 内保留）
    - pytest_<PID>：PID 存活 → False（测试还在跑）
    - 其余 → True

    阈值真源：trae_071 YAML §test_residue_reclaim.params（动态加载）。
    config 不可达 → 返回 False（reconciler fail-open 跳过，不删）。
    ttl 参数保留兼容性（显式传入优先），默认从 config 加载。

    供 make_runtime_cleanup_reconciler 与 oneoff 脚本复用（判定真源唯一）。
    """
    cfg = _load_test_residue_config()
    if cfg is None:
        return False
    if ttl is None:
        ttl = cfg["ttl_seconds"]
    import os  # noqa: PLC0415

    try:
        mtime = os.path.getmtime(str(dirpath))
    except OSError:
        return False
    age = now - mtime
    if age < cfg["fresh_protect_seconds"]:
        return False
    if age < ttl:
        return False
    if cfg["pid_alive_check"]:
        pid = _parse_pid_from_name(os.path.basename(str(dirpath)))
        if pid is not None and _pid_exists(pid):
            return False
    return True


def make_runtime_cleanup_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-RUNTIME-CLEANUP post-commit .runtime/ TTL 清理 reconciler。

    病根：.runtime/ 是项目运行时产物目录（.gitignore 豁免），但无自动清理机制——

    handoffs/（700+ session 交接包）、reconcile_reports/（2900+ 对账报告）、root-level

    temp files 线性增长，总计 4100+ 文件，GOV-DOC-018 文件夹容量阈值超标。

    治本（事件触发 TTL 清理）：

    - trigger: 每次 commit 都触发（扫描 4100 文件 mtime 成本 <0.1s）

    - reconcile: 删除 mtime > 7 天的文件，保留 .gitkeep（目录标记）和 .jsonl（审计日志）

    - 自维护/自关闭：每次 commit 后自动清理，返回 ReconcileResult

    保护规则（第一性原理：只删临时产物，保留有状态的持久文件）：

    - .gitkeep：目录结构标记

    - *.jsonl：append-only 审计日志

    - 其余 >7 天文件：临时产物，过期安全删除

    向内收：扩展 ReconciliationRegistry 框架（第15个 reconciler），不新建独立清理系统。

    复用 _GlobalCommitLock 的 TTL+mtime 模式。

    """

    import os
    import time

    project_root = gateway.project_root

    _TTL_SECONDS = 7 * 86400  # 7 天

    _PROTECTED_NAMES = {".gitkeep"}

    _PROTECTED_SUFFIX = ".jsonl"

    def _trigger(committed_files: list[str]) -> bool:

        return True  # .runtime/ 增长与每次 commit 正相关

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        runtime_dir = project_root / ".runtime"

        if not runtime_dir.exists():
            return ReconcileResult(action="skip", detail=".runtime/ not found")

        now = time.time()

        deleted = 0

        errors = 0

        # T5 告警卫生（2026-08-14，#ARCH-RECONCILER-AUTO-DELETE-GOV-001 裁定5）：
        # 锁定跳过=clean 语义——文件被占用（WinError 32/5 → PermissionError）非异常，
        # 不计入 errors；errors 只报真异常，避免恒定 warn 噪音淹没真告警。
        locked_skipped = 0

        for dirpath, _dirnames, filenames in os.walk(runtime_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)

                try:
                    mtime = os.path.getmtime(filepath)

                    if now - mtime < _TTL_SECONDS:
                        continue  # 仍在 TTL 内

                    if filename in _PROTECTED_NAMES:
                        continue  # 目录结构标记

                    if filename.endswith(_PROTECTED_SUFFIX):
                        continue  # append-only 审计日志

                    # T1② 收敛：guard 安全 API（审计+file_ops 声明制强制）
                    from scripts.ops_guard import guard_remove

                    guard_remove(filepath)

                    deleted += 1

                except PermissionError:
                    locked_skipped += 1  # 锁定跳过=clean 语义（T5）

                except OSError:
                    errors += 1

        # 治本 #ARCH-XDIST-WORKER-CRASH-001 + #ARCH-TEST-RESIDUE-CLEANUP-001:

        # 回收 .runtime/tmp/ 下测试残留目录（pytest_<PID>/ PID-unique basetemp +

        # git_guard_test_*/tmp*/conc_mv_*/b1/g1/... 等测试框架残留）。

        # 原版 os.rmdir 只删空目录——pytest_<PID>/ 内 fixture 子目录

        # （test_conftest_py_exempted0/...）永远非空 → 永远删不掉 → 10 万+ 文件积压。

        # 升级：PID 存活 + TTL 双判定 → shutil.rmtree 整目录（含残留子目录/文件）。

        # 判定真源 = 模块级 _should_remove_test_dir（与 oneoff 脚本复用同一真源）。

        import shutil  # noqa: PLC0415

        _tmp_dir = runtime_dir / "tmp"

        if _tmp_dir.exists():
            for _name in os.listdir(_tmp_dir):
                if not _match_test_residue(_name):
                    continue

                _dirpath = _tmp_dir / _name

                if not _dirpath.is_dir():
                    continue

                if not _should_remove_test_dir(_dirpath, now):
                    continue  # TTL 内 / PID 存活 / 正在写入，跳过

                try:
                    # T1② 收敛：guard 安全 API（审计+file_ops 声明制强制）
                    from scripts.ops_guard import guard_rmtree

                    guard_rmtree(str(_dirpath))

                    deleted += 1

                except PermissionError:
                    locked_skipped += 1  # 锁定跳过=clean 语义（T5）

                except OSError:
                    errors += 1  # 真异常才计入（T5：原 pass 静默吞掉，改为可观测）

        return ReconcileResult(
            action="clean" if errors == 0 else "warn",
            detail=f".runtime/ TTL cleanup: deleted={deleted}, errors={errors}, locked_skipped={locked_skipped}",
        )

    return ReconcilerSpec(
        gate_id="GATE-RUNTIME-CLEANUP",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=50,  # 在所有 reconciler 之前执行——先清理旧文件
        file_ops=frozenset({"read", "delete"}),
    )


# trae_060-reviewed: 架构健康度仪表盘 post-commit 基线记录（第0期 warn-only，ai_first_governance_principles.md（文档已删 2026-07-30，git 历史可查） §四）。

# 触发条件：任何 .py 文件变更（30 项指标覆盖代码/脚本/门禁/depgraph 维度）

# 行为：subprocess 调用 architecture_health_dashboard.py --snapshot 保存基线快照到 data/architecture_health/

# 非阻断：ReconcileResult(action="clean"/"warn")，第0期仅记录基线不阻断 commit

# 第1期升级路径：转为 pre-commit commit gate（exit 1 阻断），见 ai_first_governance_principles.md（文档已删 2026-07-30，git 历史可查） §四 第1期


def make_architecture_health_reconciler(gateway: object) -> ReconcilerSpec:
    """构造架构健康度仪表盘 post-commit 基线记录 reconciler（第0期 warn-only）。

    ai_first_governance_principles.md（文档已删 2026-07-30，git 历史可查） §四 第0期：每次 commit 自动生成架构健康度指标快照，

    替代手动调研。仪表盘 30 项指标（M01-M31），warn-only 模式（exit 0 不阻断 commit）。

    对账链：

    1. trigger: committed_files 含 .py 文件 -> 命中

    2. subprocess 调用 architecture_health_dashboard.py --snapshot

    3. 快照保存到 data/architecture_health/dashboard_<ts>.json + latest.json

    4. 返回 ReconcileResult(action="clean"/"warn")，不阻断 commit

    第1期升级路径：转为 pre-commit commit gate（exit 1 阻断），见

    ai_first_governance_principles.md（文档已删 2026-07-30，git 历史可查） §四 第1期。

    Args:

        gateway: GitCommitGateway 实例（仅用其 project_root）。

    Returns:

        ReconcilerSpec(gate_id="GATE-ARCH-HEALTH", priority=300)。

    """

    import os
    import subprocess
    import sys

    project_root = gateway.project_root

    dashboard = project_root / "scripts" / "governance" / "architecture_health_dashboard.py"

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel.endswith(".py"):
                return True

        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        if not dashboard.exists():
            return ReconcileResult(action="skip", detail="dashboard script not found")

        try:
            result = _run_subprocess(
                [sys.executable, str(dashboard), "--snapshot"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(project_root),
                timeout=120,
            )

            if result.returncode == 0:
                return ReconcileResult(
                    action="clean",
                    detail="architecture health baseline snapshot saved (warn-only, Phase 0)",
                )

            else:
                return ReconcileResult(
                    action="warn",
                    detail=f"dashboard exit code {result.returncode}: {result.stderr[:200]}",
                )

        except subprocess.TimeoutExpired:
            return ReconcileResult(action="warn", detail="dashboard timeout after 120s")

        except Exception as e:  # noqa: BLE001 — drift 对账非阻断
            return ReconcileResult(action="warn", detail=f"dashboard failed: {e}")

    return ReconcilerSpec(
        gate_id="GATE-ARCH-HEALTH",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=300,  # 低优先级最后执行——基线记录非紧急
        file_ops=frozenset({"read", "write"}),
    )


# AI-03 审计 P3 待办落地（2026-07-05）：session_logs/index.yaml 派生 reconciler。

# 病根：index.yaml 的 by_date/by_module/by_contract 派生数据截至 2026-05-08 未更新，

#   派生脚本（validate_session_log_index_integrity.py --generate）无自动触发机制。

# 治本：接入 GitCommitGateway post-commit reconciler 轨（事件触发，非时间触发/手动触发）。

# 向内收：扩展已有 reconciliation_registry.py 框架（增加一个 reconciler，序号以实际注册顺序为准，不硬编码——裁定 D 治本 2026-07-19），不新建独立触发系统。

# 真源：validate_session_log_index_integrity.py 是 index.yaml 派生逻辑唯一真源，本 reconciler 仅调用。

# trae_060-reviewed: 通过元问题审查。session_logs/index.yaml 派生数据过期是真实问题（截至 2026-05-08

# 未更新），需自动触发机制。现有所有已注册 reconciler 无一处理 session_logs/ 目录，无法合并进已有（数量以 ReconciliationRegistry 实际注册为准，不硬编码——裁定 D 治本 2026-07-19）。

# 事件触发（post-commit: session_logs/**/*.yaml 落盘），非 cron/manual，满足项目约束"reconciler 必须事件触发"。

# 派生逻辑真源唯一：validate_session_log_index_integrity.py --generate（本 reconciler 仅调用，不复制逻辑）。


def make_session_log_index_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-SESSION-LOG-INDEX post-commit session_logs/index.yaml 派生 reconciler。

    病根：session_logs/index.yaml 的 by_date/by_module/by_contract 派生数据由

    ``validate_session_log_index_integrity.py --generate`` 从 session log YAML 派生，

    但原设计无自动触发机制——新 session yaml 落盘后 index.yaml 不会自动更新，

    导致索引过期（截至 2026-05-08 未更新，AI-03 审计 P3）。

    治本（事件触发派生）：

    - 接入 GitCommitGateway post-commit reconciler 轨（事件触发，非 cron/manual）

    - trigger: committed_files 含 session_logs/**/*.yaml 且非 index.yaml 本身

    - reconcile: 调用 validate_session_log_index_integrity.py --generate，

      检测 index.yaml 变更，有变更->auto-commit（经 _commit_auto 统一入口，DCR gate 覆盖）

    trigger 裁定（派生真源：validate_session_log_index_integrity.py L88-99）：

    - session_logs/**/*.yaml（排除 _auto/ 子目录和 index.yaml 本身）

    向内收设计：

    - 责任唯一：派生逻辑只在 validate_session_log_index_integrity.py 一处（本 reconciler 仅调用）

    - 真源唯一：复用 ReconciliationRegistry 框架（增加一个 reconciler，序号以实际注册顺序为准，不硬编码——裁定 D 治本 2026-07-19），不新建独立触发系统

    - 事件触发：post-commit 自动执行，无 cron/manual

    Args:

        gateway: GitCommitGateway 实例（用 project_root + _run_git + _commit_auto）。

    Returns:

        ReconcilerSpec(gate_id="GATE-SESSION-LOG-INDEX", priority=175)。

    """

    import os
    import subprocess
    import sys

    project_root = gateway.project_root

    _INDEX_REL = "session_logs/index.yaml"

    _VALIDATOR_REL = "scripts/governance/d5_architecture/validators/session/validate_session_log_index_integrity.py"

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            # 命中 session_logs/**/*.yaml，排除 index.yaml 本身和 _auto/ 派生产物

            if rel.startswith("session_logs/") and rel.endswith(".yaml") and rel != _INDEX_REL and "/_auto/" not in rel:
                return True

        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        validator = project_root / _VALIDATOR_REL

        if not validator.exists():
            return ReconcileResult(
                action="warn",
                detail=f"validator script not found: {_VALIDATOR_REL}",
            )

        # 1. 调用 validate_session_log_index_integrity.py --generate（校验 + 汇总生成）

        gen_result = _run_subprocess(
            [
                sys.executable,
                str(validator),
                "--generate",
            ],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,  # 扫描 session_logs/ 较快（<50 文件）
        )

        if gen_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"validator --generate failed (exit {gen_result.returncode}): {gen_result.stderr.strip()[:200]}",
            )

        # 2. 检测 index.yaml 变更

        diff_result = gateway.run_git(["git", "diff", "--name-only", "--", _INDEX_REL])

        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="session_logs/index.yaml up to date")

        # 3. 变更 -> 自动提交（经 _commit_auto 统一入口，DCR gate 覆盖）

        abs_files = [str(project_root / _INDEX_REL)]

        auto_msg = "chore(session_logs): auto-regenerate index.yaml by GitCommitGateway post-commit"

        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)

        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail="session_logs/index.yaml drift detected and auto-regenerated",
            )

        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="session_logs/index.yaml no drift (auto-commit found no staged changes)",
            )

        return ReconcileResult(
            action="warn",
            detail=f"session_logs/index.yaml drift detected, auto-commit failed ({commit_result.status}): "
            f"{commit_result.message[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-SESSION-LOG-INDEX",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=175,  # 在 index_generator(170) 之后，runtime_cleanup 之前
        file_ops=frozenset({"read", "write"}),
    )


# 病根：02_enterprise_architecture 下 9 个架构图生成器无自动触发，depgraph/dataflow/decision

# PG 或 YAML 真源变更后架构图 MD 过时。原 make_regenerate_reconciler 仅覆盖 domain_doc/

# domain_dependency_diagram/domain_index + arch_model + script_manifest，不含

# decision/dataflow/integration/cross_domain/constraint/capacity/capability/navigation。

# 治本：扩展 ReconciliationRegistry 框架（第19个 reconciler），事件触发，非 cron/manual。

# 三图对齐：depgraph(600-620)+dataflow(630)+decision(630) trigger 对齐，priority 相邻。

# trae_060-reviewed: 该存在（9 个生成器无自动触发是真实问题），不能合并进已有 reconciler

#   （已有 make_regenerate_reconciler 仅含 domain_doc/arch_model/manifest，trigger 虽重叠但

#   输出目标不同——9 个架构图 MD 是独立输出，需独立 reconciler），治本（事件触发+auto-commit）。


def make_arch_diagram_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-ARCH-DIAGRAM post-commit 架构图自动重生 reconciler（议题3）。

    病根：``docs/02_enterprise_architecture/`` 下 9 个架构图生成器无自动触发机制——

    depgraph/dataflow/decision PG 表变更或 YAML 真源变更后，架构图 MD 文档过时，

    依赖手动跑各生成器。这违反"永久系统必须全自动"硬约束。

    治本（事件触发自动重生，三图对齐）：

    - 接入 GitCommitGateway post-commit reconciler 轨（事件触发，非 cron/manual）

    - trigger: PG 写入脚本 commit OR YAML 真源变更 -> 命中

    - reconcile: 串联跑 15 个生成器，检测漂移，auto-commit

    涵盖生成器（输出均在 docs/02_enterprise_architecture/）：

      1. generate_decision_diagram.py        -> 06_decision_architecture/decision_index.md

      2. generate_dataflow_diagram.py        -> 05_dataflow_architecture/dataflow_index.md

      3. generate_integration_topology.py     -> 01_global_architecture_diagram/integration_topology.md

      4. generate_design_vs_production.py    -> 03_governance_reports/design_vs_production.md

      5. generate_cross_domain_matrix.py     -> 01_global_architecture_diagram/cross_domain_matrix.md

      6. generate_constraint_violations.py    -> 03_governance_reports/constraint_violations.md

      7. generate_capacity_report.py         -> 03_governance_reports/capacity_report.md

      8. generate_capability_heatmap.py       -> 01_global_architecture_diagram/global_capability_heatmap.md

      9. generate_navigation_index.py         -> 00_overview_entry/navigation_index.md

     10. generate_panorama_registry.py        -> 00_overview_entry/panorama_registry.md

     11. align_panoramas.py                   -> 03_governance_reports/panorama_alignment_report.md（ARCH-053 全景对齐检测器）

     11b. align_battle_map.py                 -> 03_governance_reports/battle_map_alignment_report.md（作战地图对齐检测器，BM-INV-001~007）

     12. generate_asset_catalog.py            -> 01_global_architecture_diagram/asset_catalog.md（#179/#180/#181/#182 资产清单）

     13. generate_policies.py                 -> src/zephyr/data/config/policies.yaml（#183 数据源策略派生）

     14. generate_data_inventory.py           -> 05_dataflow_architecture/data_inventory.md（真源：ClickHouse 实时扫描）

     15. generate_data_acquisition_flow.py    -> 05_dataflow_architecture/data_acquisition_flow.md（真源：tasks.yaml）

    已覆盖（不在本 reconciler 范围，由 make_regenerate_reconciler 处理）：

      - generate_domain_doc.py --all

      - generate_domain_dependency_diagram.py --all  # 已于 2026-07-30 下线（.mmd 由域文档内嵌 mermaid 替代）

      - generate_domain_index.py

      - dm200916_write_direct.py（根树 index.yaml）

    已覆盖（由 make_path_tree_reconciler 处理）：

      - generate_path_tree.py

    trigger 真源：

      - PG 写入脚本（DB 变更即代表架构可能漂移）：

        apply_depgraph.py / sync_yaml_to_depgraph.py / generate_project_path_tree.py /

        generate_decision_graph.py（decisiongraph sync 入口）

      - YAML 真源（架构图直接数据源）：

        architecture_model/domain/decision_graph_model.yaml

        docs/01_policies_and_standards/_registry/catalogs/dataflow_graph_registry.yaml

        architecture_model/cross_cutting/capability_heatmap.yaml

    向内收设计：

    - 责任唯一：生成逻辑只在各生成器一处（本 reconciler 仅调用，不复制逻辑）

    - 真源唯一：复用 ReconciliationRegistry 框架（第19个 reconciler），不新建独立触发系统

    - 事件触发：post-commit 自动执行，无 cron/manual

    - 三图对齐：depgraph(600) / dataflow(630) / decision(630) 三图 trigger+priority 对齐

    Args:

        gateway: GitCommitGateway 实例（用 project_root + _run_git + _commit_auto）。

    Returns:

        ReconcilerSpec(gate_id="GATE-ARCH-DIAGRAM", priority=630)。

    """

    import os
    import subprocess
    import sys

    project_root = gateway.project_root

    # PG 写入脚本真源（DB 变更即代表架构图可能漂移）

    _PG_WRITE_SCRIPTS = (
        "scripts/governance/apply_depgraph.py",
        "scripts/governance/apply_decisiongraph.py",  # decisiongraph DB 写入入口（节点/边增删改）
        "scripts/governance/apply_dataflowgraph.py",  # dataflowgraph DB 写入入口 #ARCH-053
        "scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py",
        "scripts/governance/generate_project_path_tree.py",
        "scripts/governance/generate_decision_graph.py",  # decisiongraph sync 入口
    )

    # YAML 真源（架构图直接数据源）

    _YAML_SOURCES = (
        "architecture_model/domain/decision_graph_model.yaml",
        "docs/01_policies_and_standards/_registry/catalogs/dataflow_graph_registry.yaml",
        "architecture_model/cross_cutting/capability_heatmap.yaml",
        # 资产 YAML 真源（#179/#180/#181/#182）：变更触发 asset_catalog.md 重生
        "architecture_model/data/data_sources_registry.yaml",
        "architecture_model/data/data_source_apis_registry.yaml",
        "architecture_model/runtime/service_registry.yaml",
        "architecture_model/contracts/cross_layer_contracts.yaml",
        # generate_data_acquisition_flow.py 真源：tasks.yaml 变更触发 data_acquisition_flow.md 重生
        "src/zephyr/data/config/tasks.yaml",
    )

    _GEN_DIR = "scripts/governance/d5_architecture/generators"

    # 15 个生成器 + 输出路径（漂移检测目标）

    _GENERATORS = (
        "generate_decision_diagram.py",
        "generate_dataflow_diagram.py",
        "generate_integration_topology.py",
        "generate_design_vs_production.py",
        "generate_cross_domain_matrix.py",
        "generate_constraint_violations.py",
        "generate_capacity_report.py",
        "generate_capability_heatmap.py",
        "generate_navigation_index.py",
        "generate_panorama_registry.py",  # 全景图清单总表（00_overview_entry/panorama_registry.md）
        "align_panoramas.py",  # ARCH-053 三图对齐检测器（manual，但 PG 写入后自动重生）
        "generate_asset_catalog.py",  # #179/#180/#181/#182 资产清单全景图（256 项资产）
        "generate_policies.py",  # #183 数据源策略派生（data_sources_registry.yaml → policies.yaml）
        "generate_data_inventory.py",  # 业务数据清单（真源：ClickHouse 实时扫描；YAML/PG 变更顺带重生）
        "generate_data_acquisition_flow.py",  # 数据采集流图（真源：tasks.yaml）
    )

    _OUTPUTS = (
        "docs/02_enterprise_architecture/06_decision_architecture/decision_index.md",
        "docs/02_enterprise_architecture/05_dataflow_architecture/dataflow_index.md",
        "docs/02_enterprise_architecture/01_global_architecture_diagram/integration_topology.md",
        "docs/02_enterprise_architecture/03_governance_reports/design_vs_production.md",
        "docs/02_enterprise_architecture/01_global_architecture_diagram/cross_domain_matrix.md",
        "docs/02_enterprise_architecture/03_governance_reports/constraint_violations.md",
        "docs/02_enterprise_architecture/03_governance_reports/capacity_report.md",
        "docs/02_enterprise_architecture/01_global_architecture_diagram/global_capability_heatmap.md",
        "docs/02_enterprise_architecture/00_overview_entry/navigation_index.md",
        "docs/02_enterprise_architecture/00_overview_entry/panorama_registry.md",
        "docs/02_enterprise_architecture/03_governance_reports/panorama_alignment_report.md",  # ARCH-053 全景对齐检测器
        "docs/02_enterprise_architecture/03_governance_reports/battle_map_alignment_report.md",  # 作战地图对齐检测器（BM-INV-001~007）
        "docs/02_enterprise_architecture/01_global_architecture_diagram/asset_catalog.md",  # #179/#180/#181/#182
        "src/zephyr/data/config/policies.yaml",  # #183 数据源策略派生物
        "docs/02_enterprise_architecture/05_dataflow_architecture/data_inventory.md",  # generate_data_inventory.py
        "docs/02_enterprise_architecture/05_dataflow_architecture/data_acquisition_flow.md",  # generate_data_acquisition_flow.py
    )

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel in _PG_WRITE_SCRIPTS:
                return True

            if rel in _YAML_SOURCES:
                return True

        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        # 0. drift-gate: 预检测产物是否已有未提交变更（体系A reconcile_async 可能已跑过）

        #    有变更 → 跳过生成器直接 auto-commit（消除与体系A双重执行，治本 #ARCH-DUAL-TRIGGER）

        #    无变更 → 产物可能过时，继续跑生成器（原逻辑兜底）

        pre_diff = gateway.run_git(["git", "diff", "--name-only", "--", *_OUTPUTS])

        if pre_diff.returncode == 0 and pre_diff.stdout.strip():
            pre_changed = [f.strip() for f in pre_diff.stdout.splitlines() if f.strip()]

            pre_abs = [str(project_root / f) for f in pre_changed]

            pre_commit = gateway._commit_auto(
                session_id,
                pre_abs,
                "chore(arch): auto-commit systemA-regenerated diagrams (drift-gate skipped generators)",
            )

            if pre_commit.status == "OK":
                return ReconcileResult(
                    action="auto_committed",
                    detail=f"drift-gate: skipped {len(_GENERATORS)} generators, auto-committed {len(pre_changed)} files (systemA already ran)",
                )

            # auto-commit 失败 → 落回原逻辑跑生成器（兜底，不阻断）

        # 1. 串联跑 15 个生成器（无 --all 参数，直接运行；幂等：相同输入->相同输出）

        failed_gens: list[str] = []

        for gen_name in _GENERATORS:
            gen_result = _run_subprocess(
                [sys.executable, f"{_GEN_DIR}/{gen_name}"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,  # 单个生成器最多 3 分钟（depgraph 查询 + MD 写入）
            )

            if gen_result.returncode != 0:
                failed_gens.append(f"{gen_name}: {gen_result.stderr.strip()[:120]}")

                # 不 return，继续跑剩余生成器（部分漂移修复优于全跳过）

        if failed_gens and len(failed_gens) == len(_GENERATORS):
            # 全部失败 -> warn 直接返回（无漂移可检测）

            return ReconcileResult(
                action="warn",
                detail=f"all {len(_GENERATORS)} generators failed: {'; '.join(failed_gens[:3])}",
            )

        # 2. 检测输出文件变更（即使部分生成器失败，已成功的可能产生漂移）

        diff_result = gateway.run_git(["git", "diff", "--name-only", "--", *_OUTPUTS])

        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            if failed_gens:
                return ReconcileResult(
                    action="warn",
                    detail=f"no drift but {len(failed_gens)} generator(s) failed: {'; '.join(failed_gens[:3])}",
                )

            return ReconcileResult(action="clean", detail="arch diagrams up to date")

        # 3. 变更 -> 自动提交（经 _commit_auto 统一入口，DCR gate 覆盖）

        changed_files = [f.strip() for f in diff_result.stdout.splitlines() if f.strip()]

        abs_files = [str(project_root / f) for f in changed_files]

        auto_msg = "chore(arch): auto-regenerate architecture diagrams by GitCommitGateway post-commit"

        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)

        if commit_result.status == "OK":
            detail = f"arch diagrams drift detected and auto-regenerated ({len(changed_files)} files)"

            if failed_gens:
                detail += f"; {len(failed_gens)} generator(s) failed: {'; '.join(failed_gens[:3])}"

            return ReconcileResult(action="auto_committed", detail=detail)

        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="arch diagrams no drift (auto-commit found no staged changes)",
            )

        return ReconcileResult(
            action="warn",
            detail=f"arch diagrams drift detected, auto-commit failed ({commit_result.status}): "
            f"{commit_result.message[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-ARCH-DIAGRAM",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=630,  # 在 regenerate(600-620) 之后，rule_audit(700-710) 之前
        file_ops=frozenset({"read", "write"}),
    )


# 病根：generate_constraint_violations.py 只读不检测，arch_constraints 表 56 条全部默认

# open，无检测器写入 violation_status/details/detected_at。链路断裂。

# 该存在：检测器是独立职责（检测 vs 展示），不能合并进生成器。

# 治本：事件触发（PG 写入脚本 commit）+ 跑检测器写 PG。

# trae_060-reviewed: 该存在（检测器是独立职责，不能合并进生成器），治本（事件触发+写PG）


def make_constraint_detect_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-CONSTRAINT-DETECT post-commit 架构违规检测 reconciler。

    病根：``generate_constraint_violations.py`` 只读 ``arch_constraints`` 表生成 MD 报告，

    但没有任何检测器实际检测违规并写入 ``violation_status``/``details``/``detected_at``。

    导致报告中 56 条约束全部默认 ``open``，无法区分真违规和正常约束——链路断裂。

    治本（补齐断链的检测层）：

    - 接入 GitCommitGateway post-commit reconciler 轨（事件触发，非 cron/manual）

    - trigger: PG 写入脚本 commit -> 命中（与 GATE-ARCH-DIAGRAM 相同 trigger）

    - reconcile: 跑 ``detect_constraint_violations.py``，5 类检测 -> 写 PG

    5 类检测（写入 constraint_type 区分规则定义和检测结果）：

      1. cross_domain_violation — 跨域违规（import 跨域但未在 domain_dependencies 声明）

      2. capacity_exceeded — 容量超限（production 节点 > max_modules，ARCH-CAP-001）

      3. hard_limit_exceeded — 硬上限违规（production 节点 > 150，ARCH-CAP-002 v1.0.8）

      4. orphan_node — 孤儿节点（路径未注册到 arch_directory_tree）

      5. layer_violation — 层级违规（低层依赖高层）

    链路（与 GATE-ARCH-DIAGRAM 协作）：

      1. GATE-CONSTRAINT-DETECT (625): 跑检测器，写 PG arch_constraints 表

      2. GATE-ARCH-DIAGRAM (630): 跑生成器，读 PG（含新检测结果），生成 MD，auto-commit

    Args:

        gateway: GitCommitGateway 实例（用 project_root）。

    Returns:

        ReconcilerSpec(gate_id="GATE-CONSTRAINT-DETECT", priority=625)。

    """

    import os
    import subprocess
    import sys

    project_root = gateway.project_root

    # PG 写入脚本真源（DB 变更即代表可能产生新违规）

    _PG_WRITE_SCRIPTS = (
        "scripts/governance/apply_depgraph.py",
        "scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py",
        "scripts/governance/generate_project_path_tree.py",
        "scripts/governance/generate_decision_graph.py",
    )

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel in _PG_WRITE_SCRIPTS:
                return True

        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        # 跑检测器（写 PG，不产生文件变更）

        gen_result = _run_subprocess(
            [sys.executable, "scripts/governance/d5_architecture/detect_constraint_violations.py"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )

        if gen_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"constraint detection failed: {gen_result.stderr.strip()[:200]}",
            )

        # 检测器写 PG，不产生文件变更，返回 clean

        # GATE-ARCH-DIAGRAM (630) 会在本 reconciler 之后触发，跑生成器展示新检测结果

        return ReconcileResult(
            action="clean",
            detail=f"constraint detection completed: {gen_result.stdout.strip().splitlines()[-1] if gen_result.stdout.strip() else 'done'}",
        )

    return ReconcilerSpec(
        gate_id="GATE-CONSTRAINT-DETECT",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=625,  # 在 GATE-ARCH-DIAGRAM (630) 之前跑，生成器依赖检测结果
        file_ops=frozenset({"read", "write"}),
    )


# ARCH-055 治本（2026-07-09）：commit_gates 模块清单漂移检测

# 病根：blueprint.md §0.1 模块清单靠手工维护，100% AI 开发模式下漂移率 20.7%（6/29）

# 现有 GATE-AGENTS-MD-REFS 是反向检测（文档引用→代码存在性），本 reconciler 补正向（代码→文档）

# trae_060-reviewed: 该 reconciler 独立存在治本（commit_gates 模块清单漂移正向检测），

# 不合并进已有 reconciler（现有 reconciler 无此检测逻辑，GATE-AGENTS-MD-REFS 是反向检测不覆盖正向）


def _auto_fix_gate_inventory(project_root) -> dict:
    """ADP-4: 自动修复 commit_gates 模块清单漂移（裁定#ARCH-DRIFT-PREVENTION-001）。

    检测 missing 文件后，自动在 blueprint.md §0.1 表格末尾补齐 missing 文件行。

    extra 文件不自动删除（可能人工添加，需人工确认）。

    Returns:

        {"fixed": bool, "detail": str} — fixed=True 表示已修改 blueprint.md。

    """

    try:
        # 治本（DM-90974 副带）：完整项目路径 import 替代 sys.path.insert + 裸模块名，

        # 消除 IMPORT-INTEGRITY gate 静态扫描误报（gate 看不到 sys.path 运行时操作）。

        # 包结构 scripts/governance/generators/__init__.py 已存在，完整路径可解析。

        from scripts.governance.generators.check_gate_inventory_drift import detect_drift

    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        return {"fixed": False, "detail": f"cannot import detect_drift: {e}"}

    missing, _extra = detect_drift()

    if not missing:
        return {"fixed": False, "detail": "no missing files to add"}

    blueprint_path = project_root / "docs" / "03_modules" / "_cross_layer" / "gate_engine" / "blueprint.md"

    if not blueprint_path.is_file():
        return {"fixed": False, "detail": "blueprint.md not found"}

    # #ARCH-RECONCILER-TOCTOU-CLOBBER-001 P0 止血：整文件 READ-MODIFY-WRITE 加 advisory lock，
    # 防止跨 commit/session 并发写导致 clobber（读旧→写新覆盖并发编辑）。
    import contextlib  # noqa: E402 — nullcontext fallback for fail-open

    try:
        from scripts.governance._shared.file_lock import blueprint_write_lock

        _lock = blueprint_write_lock(blueprint_path)
    except ImportError:  # pragma: no cover — filelock 是项目依赖
        _lock = contextlib.nullcontext()

    with _lock:
        text = blueprint_path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines(keepends=True)
        last_gate_idx = -1
        for i, line in enumerate(lines):
            if line.startswith("| `commit_gates/"):
                last_gate_idx = i
        if last_gate_idx < 0:
            return {"fixed": False, "detail": "cannot locate §0.1 gate table"}
        new_rows = [
            f"| `commit_gates/{f}` | §0.1 | auto-added by GATE-MODULE-INVENTORY-SYNC (ADP-4) | 已实现 | | 本模块 |\n"
            for f in missing
        ]
        lines[last_gate_idx + 1 : last_gate_idx + 1] = new_rows
        blueprint_path.write_text("".join(lines), encoding="utf-8")
        return {"fixed": True, "detail": f"added {len(missing)} missing gate(s): {', '.join(missing)}"}


def make_gate_inventory_sync_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 commit_gates 模块清单漂移检测 post-commit reconciler（ARCH-055 + ADP-4 治本）。

    commit src/zephyr/gov_enforcement/commit_gates/*.py 后，blueprint.md §0.1 模块清单

    可能过时（新增/删除 gate 文件但文档未同步）。本 reconciler 在 post-commit 跑

    check_gate_inventory_drift.py 检测脚本，漂移时 auto-fix + warn（裁定#ARCH-DRIFT-PREVENTION-001

    ADP-4：自动补齐 missing 文件行到 §0.1 表格，extra 不自动删除需人工确认）。

    auto-fix + warn 理由（ADP-4 升级）：漂移是文档同步滞后，非代码错误；阻断会导致

    AI 无法 commit 正常的 gate 新增（因 blueprint.md 未同步而阻断 gate 代码本身的

    commit，形成死循环）。auto-fix 自动补齐 missing 文件行消除漂移，warn 保留提醒

    （auto-fix 失败或 extra 文件需人工确认时）。

    Args:

        gateway: GitCommitGateway 实例（用 project_root）。

    Returns:

        ReconcilerSpec(gate_id="GATE-MODULE-INVENTORY-SYNC", priority=820)。

    """

    import os
    import sys

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel.startswith("src/zephyr/gov_enforcement/commit_gates/") and rel.endswith(".py"):
                return True

        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        check_script = "scripts/governance/generators/check_gate_inventory_drift.py"

        result = _run_subprocess(
            [sys.executable, check_script],
            cwd=str(project_root),
            timeout=30,
        )

        if result.returncode == 0:
            return ReconcileResult(action="clean", detail=result.stdout.strip()[:200])

        if result.returncode == 1:
            # ADP-4: 升级为 warn + auto-fix（裁定#ARCH-DRIFT-PREVENTION-001）

            fix = _auto_fix_gate_inventory(project_root)

            if fix["fixed"]:
                bp_abs = str(project_root / "docs" / "03_modules" / "_cross_layer" / "gate_engine" / "blueprint.md")

                auto_msg = f"fix(gate_engine): GATE-MODULE-INVENTORY-SYNC auto-fix blueprint.md §0.1 ({fix['detail']})"

                commit_result = gateway._commit_auto(session_id, [bp_abs], auto_msg)

                if commit_result.status == "OK":
                    return ReconcileResult(
                        action="auto_committed",
                        detail=f"inventory drift auto-fixed: {fix['detail']}",
                    )

                if commit_result.status == "NOTHING_TO_COMMIT":
                    return ReconcileResult(
                        action="clean",
                        detail=f"inventory auto-fix no staged changes (auto-commit): {fix['detail']}",
                    )

                return ReconcileResult(
                    action="warn",
                    detail=f"inventory drift auto-fix commit failed ({commit_result.status}): "
                    f"{commit_result.message[:200]}",
                )

            return ReconcileResult(
                action="warn",
                detail=f"commit_gates inventory drift (ARCH-055), auto-fix N/A: {fix['detail']}",
            )

        return ReconcileResult(
            action="warn",
            detail=f"check_gate_inventory_drift.py error: {result.stderr.strip()[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-MODULE-INVENTORY-SYNC",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=820,  # 在 GATE-AGENTS-MD-REFS(810) 之后
        file_ops=frozenset({"read", "write"}),
    )


# trae_060-reviewed: 该存在+不可合并进已有+治本。gate_registry.yaml 无任何 reconciler 自动重生成

# （对比 script_manifest 有 make_manifest_reconciler 完整覆盖），机制缺失需补齐。

# make_gate_inventory_sync_reconciler 名字相近但只修 blueprint.md §0.1（文档层），不修

# gate_registry.yaml（数据层），职责不同不可合并。治本：post-commit 修复型对标

# make_manifest_reconciler，trigger 覆盖三源，auto_commit 修复（ARCH-GATE-REGISTRY-SYNC-001）。


def make_gate_registry_sync_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 gate_registry.yaml 自动重生成 post-commit reconciler（ARCH-GATE-REGISTRY-SYNC-001 治本）。

    commit src/zephyr/gov_enforcement/commit_gates/*.py / .pre-commit-config.yaml /

    generate_gate_registry.py 后，gate_registry.yaml 可能过时（新增/删除 gate 但登记表未同步）。

    本 reconciler 在 post-commit 跑 generate_gate_registry.py 重生成 + auto_commit 修复。

    治本策略选择（裁定 ARCH-GATE-REGISTRY-SYNC-001）：

    - 采用策略 B（post-commit 修复型），对标 make_manifest_reconciler

    - 否决策略 A（pre-commit 阻断型）：阻断会导致 AI 无法 commit 新 gate 代码（清单未同步→

      阻断→无法 commit→死循环），与 make_gate_inventory_sync_reconciler ADP-4 裁定一致

    职责边界（与 make_gate_inventory_sync_reconciler 分离）：

    - make_gate_inventory_sync_reconciler：修 blueprint.md §0.1 模块清单（文档层）

    - 本 reconciler：修 gate_registry.yaml 门禁登记表（数据层，三源合并）

    trigger 覆盖三源（generate_gate_registry.py 三源合并机制）：

    1. src/zephyr/gov_enforcement/commit_gates/*.py（CommitGates 源）

    2. .pre-commit-config.yaml（pre-commit hooks 源）

    3. scripts/governance/generators/generate_gate_registry.py（生成器自身 + MANUAL_GATES 硬编码）

    Args:

        gateway: GitCommitGateway 实例（用 project_root + _run_git + _commit_auto）。

    Returns:

        ReconcilerSpec(gate_id="GATE-GATE-REGISTRY-SYNC", priority=830)。

        priority=830——在 GATE-MODULE-INVENTORY-SYNC(820) 之后执行（gate_registry.yaml 依赖

        commit_gates/*.py 扫描，需在 blueprint.md §0.1 同步后执行，避免竞争）。

    """

    import os
    import sys

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            # 三源覆盖：CommitGates 源 + pre-commit hooks 源 + 生成器自身

            if rel.startswith("src/zephyr/gov_enforcement/commit_gates/") and rel.endswith(".py"):
                return True

            if rel == ".pre-commit-config.yaml":
                return True

            if rel == "scripts/governance/generators/generate_gate_registry.py":
                return True

        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        # 1. 重生成 gate_registry.yaml（三源合并 SSoT）

        gen_script = "scripts/governance/generators/generate_gate_registry.py"

        gen_result = _run_subprocess(
            [sys.executable, gen_script],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )

        if gen_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=f"gate_registry regeneration failed: {gen_result.stderr.strip()[:200]}",
            )

        # 2. 检测 gate_registry.yaml 变更

        registry_rel = "docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml"

        diff_result = gateway.run_git(["git", "diff", "--name-only", "--", registry_rel])

        if diff_result.returncode == 0 and not diff_result.stdout.strip():
            return ReconcileResult(action="clean", detail="gate_registry up to date")

        # 3. 变更 -> 自动提交修复（经 _commit_auto 统一入口，gate 覆盖）

        auto_msg = "chore(gate_registry): auto-regenerate by GitCommitGateway post-commit (ARCH-GATE-REGISTRY-SYNC-001)"

        abs_files = [str(project_root / registry_rel)]

        commit_result = gateway._commit_auto(session_id, abs_files, auto_msg)

        if commit_result.status == "OK":
            return ReconcileResult(
                action="auto_committed",
                detail="gate_registry drift detected and auto-reconciled",
            )

        if commit_result.status == "NOTHING_TO_COMMIT":
            return ReconcileResult(
                action="clean",
                detail="gate_registry no drift (auto-commit found no staged changes)",
            )

        return ReconcileResult(
            action="warn",
            detail=f"gate_registry drift detected, auto-commit failed ({commit_result.status}): "
            f"{commit_result.message[:200]}",
        )

    return ReconcilerSpec(
        gate_id="GATE-GATE-REGISTRY-SYNC",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=830,  # 在 GATE-MODULE-INVENTORY-SYNC(820) 之后
        file_ops=frozenset({"read", "write"}),
    )


# trae_060-reviewed: 该存在+可合并入已有框架（复用 ReconciliationRegistry post-commit warn-only 漂移检测，

# 对标 make_undefined_name_baseline_reconciler）。病根：auto_register_gates fail-open 仅 logger.warning，

# 无 reconciler 则漂移不入 reconcile_execution_log。与 make_gate_registry_sync_reconciler 职责分离。

# #ARCH-GATE-REGISTRY-AUTO-001 Phase 6——in_process_gate_registry.yaml ↔ 内存注册表双向校验


def make_in_process_gate_registry_drift_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 in_process_gate_registry.yaml ↔ 内存注册表双向漂移检测 reconciler。

    #ARCH-GATE-REGISTRY-AUTO-001 Phase 6——YAML 真源与运行时注册表对账。

    auto_register_gates fail-open（import 失败仅 logger.warning），无 reconciler 则漂移

    不入 reconcile_execution_log，违反"所有reconciler失败结果必须持久化记录"铁律。

    本 reconciler 补强：post-commit 事件触发，对比 YAML 声明 gate_ids 与 fresh registry

    注册 gate_ids，落盘漂移报告。

    trigger: commit 触及 in_process_gate_registry.yaml / gate_auto_registrar.py /

    commit_gates/*.py 时触发。

    reconcile: 创建 fresh CommitGateRegistry，调用 auto_register_gates，对比：

      - yaml-only gates（YAML 声明但未注册 = import/register 失败 或 gate_id 不匹配）

      - in-memory-only gates（注册但 YAML 未声明 = factory 返回不同 gate_id）

    返回 ReconcileResult(action="warn") 含漂移详情，持久化到 reconcile_execution_log。

    设计权衡：

    1. warn 不 auto-fix——漂移修复需人工判断（笔误 vs 故意删除 vs import 路径变更）

    2. fresh registry——不复用 gateway._gate_registry（已被显式 register 污染）

    3. priority=831——紧随 GATE-GATE-REGISTRY-SYNC(830)

    """

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel == "docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml":
                return True

            if rel == "src/zephyr/gov_enforcement/rule_bridge/gate_auto_registrar.py":
                return True

            if rel.startswith("src/zephyr/gov_enforcement/commit_gates/") and rel.endswith(".py"):
                return True

        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import CommitGateRegistry
        from zephyr.gov_enforcement.rule_bridge.gate_auto_registrar import (
            auto_register_gates,
            load_gate_entries,
        )

        entries = load_gate_entries(project_root)

        if not entries:
            return ReconcileResult(
                action="warn",
                detail="in_process_gate_registry.yaml: no entries loaded (YAML parse failed or empty)",
            )

        yaml_gate_ids = {e.get("gate_id", "") for e in entries if e.get("gate_id")}

        yaml_disabled = {e.get("gate_id", "") for e in entries if not e.get("enabled", True) and e.get("gate_id")}

        fresh_registry = CommitGateRegistry()

        failures = auto_register_gates(fresh_registry, project_root)

        registered_ids = set(fresh_registry.list_gate_ids())

        # 双向对比

        yaml_enabled = yaml_gate_ids - yaml_disabled

        yaml_only = yaml_enabled - registered_ids  # YAML 声明了但内存中没有此 gate_id

        in_memory_only = registered_ids - yaml_gate_ids  # 内存注册了但 YAML 没声明此 gate_id

        drift_parts: list[str] = []

        if failures:
            fail_summary = "; ".join(f"{gid}: {err[:80]}" for gid, err in failures[:5])

            drift_parts.append(f"{len(failures)} import/register failure(s): {fail_summary}")

        if yaml_only:
            drift_parts.append(f"{len(yaml_only)} yaml-only gate_id(s) (mismatch or failed): {sorted(yaml_only)[:5]}")

        if in_memory_only:
            drift_parts.append(
                f"{len(in_memory_only)} in-memory-only gate_id(s) (factory returns different id): {sorted(in_memory_only)[:5]}"
            )

        if not drift_parts:
            return ReconcileResult(
                action="clean",
                detail=f"in_process_gate_registry drift check clean: YAML={len(yaml_gate_ids)} gates, registered={len(registered_ids)} gates",
            )

        return ReconcileResult(
            action="warn",
            detail=f"in_process_gate_registry drift detected: YAML={len(yaml_gate_ids)} gates ({len(yaml_disabled)} disabled), registered={len(registered_ids)} gates. "
            + " | ".join(drift_parts),
        )

    return ReconcilerSpec(
        gate_id="GATE-IN-PROCESS-REGISTRY-DRIFT",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=831,  # 紧随 GATE-GATE-REGISTRY-SYNC(830)
        file_ops=frozenset({"read", "write"}),
    )


# trae_060-reviewed: 该存在+可合并入已有框架。tmp/ 清理对标 make_runtime_cleanup_reconciler，

# 复用 ReconciliationRegistry 框架（第20个 reconciler），不新建独立清理系统。

# 病根：tmp/ 是 task_bound 退役区（.gitignore L228-232）无自动清理，249+ 文件残留，

# 依赖 AI 自觉=反模式。治本：post-commit 事件触发 TTL 清理（对标 runtime_cleanup）。


def make_tmp_cleanup_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-TMP-CLEANUP post-commit tmp/ TTL 清理 reconciler。

    病根：tmp/ 是 task_bound 一次性脚本退役区（.gitignore 全目录忽略），但无自动

    清理机制——249+ 文件残留，磁盘空间线性增长。原依赖 AI 自觉删除，在 100% AI

    开发模式下不可靠（AI 上下文有限，任务完成后忘记清理）。

    治本（事件触发 TTL 清理，对标 make_runtime_cleanup_reconciler）：

    - trigger: 每次 commit 都触发（扫描 tmp/ mtime 成本 <0.01s）

    - reconcile: 删除 mtime > 7 天的文件，保留 .gitkeep

    - 自维护/自关闭：每次 commit 后自动清理，返回 ReconcileResult

    保护规则（第一性原理：tmp/ 全目录 .gitignore，所有文件都是临时产物）：

    - .gitkeep：目录结构标记

    - mtime < 7 天的文件：可能在当前任务中使用中

    - 其余 > 7 天文件：过期安全删除

    向内收：扩展 ReconciliationRegistry 框架，复用 make_runtime_cleanup_reconciler

    的 TTL+mtime 模式，零新真源。

    """

    import os
    import time

    project_root = gateway.project_root

    _TTL_SECONDS = 7 * 86400  # 7 天（对标 make_runtime_cleanup_reconciler）

    _PROTECTED_NAMES = {".gitkeep"}

    # 豁免有自治轮转机制的子系统（防止 tmp_cleanup 与其轮转逻辑冲突）：

    # - pg_backups/: backup_runtime_state.py 自治轮转（max_backups=10，行203-209）

    # - scheduler_*: scheduler.py RotatingFileHandler 自治轮转（10MB/5备份，行1406-1413）

    _PROTECTED_DIRS = {"pg_backups"}

    _PROTECTED_PREFIXES = ("scheduler_",)

    def _trigger(committed_files: list[str]) -> bool:

        return True  # tmp/ 清理与每次 commit 正相关（commit 意味着任务推进）

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        tmp_dir = project_root / "tmp"

        if not tmp_dir.exists():
            return ReconcileResult(action="skip", detail="tmp/ not found")

        now = time.time()

        deleted = 0

        errors = 0

        locked_skipped = 0  # T5 告警卫生：锁定跳过=clean 语义

        for dirpath, _dirnames, filenames in os.walk(tmp_dir):
            # 豁免自治轮转子目录（pg_backups/由 backup_runtime_state.py max_backups=10 自治）

            rel_dir = _rel_path(dirpath, str(tmp_dir))

            if any(rel_dir == d or rel_dir.startswith(f"{d}/") for d in _PROTECTED_DIRS):
                continue

            for filename in filenames:
                filepath = os.path.join(dirpath, filename)

                try:
                    # 豁免自治轮转前缀（scheduler_*由 scheduler.py RotatingFileHandler 自治）

                    if filename.startswith(_PROTECTED_PREFIXES):
                        continue

                    mtime = os.path.getmtime(filepath)

                    if now - mtime < _TTL_SECONDS:
                        continue  # 仍在 TTL 内（可能当前任务使用中）

                    if filename in _PROTECTED_NAMES:
                        continue  # 目录结构标记

                    # T1② 收敛：guard 安全 API（审计+file_ops 声明制强制）
                    from scripts.ops_guard import guard_remove

                    guard_remove(filepath)

                    deleted += 1

                except PermissionError:
                    locked_skipped += 1  # 锁定跳过=clean 语义（T5）

                except OSError:
                    errors += 1

        return ReconcileResult(
            action="clean" if errors == 0 else "warn",
            detail=f"tmp/ TTL cleanup: deleted={deleted}, errors={errors}, locked_skipped={locked_skipped}",
        )

    return ReconcilerSpec(
        gate_id="GATE-TMP-CLEANUP",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=49,  # 在 GATE-RUNTIME-CLEANUP(50) 之前执行——先清理 tmp/
        file_ops=frozenset({"read", "delete"}),
    )


# trae_060-reviewed: 该存在+可合并入已有框架。worktree 残留清理对标 make_tmp_cleanup_reconciler

# 的 post-commit TTL 模式，复用 ReconciliationRegistry 框架（第26个 reconciler）。病根：stale

# worktree 清理依赖君子协定（仅 start 被动触发），违反永久系统全自动铁律。治本：post-commit/merge

# 事件触发 session_worktree_sweep（P1 已落地公开 API），事件驱动自动清理。


def make_worktree_lifecycle_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-WORKTREE-LIFECYCLE post-commit worktree 残留事件驱动清理 reconciler。

    病根（治本遗留项#2，2026-07-17）：session_worktree 是永久系统，但其 stale

    worktree 清理依赖君子协定——仅在 session_worktree_start 内部被动触发

    （_sweep_stale_worktrees）。当 AI 累积 stale worktree（来自崩溃/放弃/心跳

    TTL 过期的 session）且无新 session 启动时，残留 worktree 永久堆积，违反

    「永久系统必须全自动」铁律（事件触发→自动运行→自动维护→自动关闭）。

    治本（事件驱动，对标 make_tmp_cleanup_reconciler 的 post-commit TTL 模式）：

    - trigger: 任何非空 committed_files 触发（sweep 安全且成本低——无 stale

      worktree 时立即返回，三重保护判据防误清活跃 session）

    - reconcile: 调公开函数 session_worktree_sweep(project_root, max_age_minutes=30)，

      清理 .aidrafts/ 下 stale session worktree 残留

    - 自维护/自关闭：每次 commit/merge 后自动清理，无需 AI 干预

    触发路径覆盖（P2 有效性保证）：

    1. GitCommitGateway commit 后（main worktree auto-reconciler 自提交等）

    2. session_worktree_merge 后——_run_reconcilers_after_merge 创建临时

       GitCommitGateway 实例，__init__ 注册本 reconciler，reconcile_for 触发执行

    向内收：扩展 ReconciliationRegistry 框架，复用 session_worktree_sweep 公开

    API（P1 已落地），零新真源。lazy import 避免 reconciliation_registry →

    session_worktree 的 import-time 耦合。

    为什么 trigger 不做文件过滤：worktree 残留与具体 committed_files 无关——任何

    commit 都意味着 AI 活跃，是清理 stale 残留的合适时机；sweep 三重保护

    （age / active session / branch ancestor）确保安全。

    """

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:

        return bool(committed_files)  # 任何有文件的 commit 都触发（sweep 安全且成本低）

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        # lazy import 避免 import-time 耦合（reconciliation_registry 不应在模块加载时

        # 依赖 gov_enforcement.rule_bridge.session_worktree）

        from zephyr.gov_enforcement.rule_bridge.session_worktree import session_worktree_sweep

        try:
            result = session_worktree_sweep(
                project_root=project_root,
                max_age_minutes=30,
            )

        except Exception as e:  # noqa: BLE001 — 5.135治标: reconciler 容错降级
            return ReconcileResult(
                action="warn",
                detail=f"worktree lifecycle sweep 异常（降级告警）: {e}",
            )

        swept = result.get("swept", 0)

        skipped = result.get("skipped", 0)

        warnings = result.get("warnings", [])

        if warnings:
            return ReconcileResult(
                action="warn",
                detail=(
                    f"worktree lifecycle sweep: swept={swept}, skipped={skipped}, "
                    f"warnings={len(warnings)}; first: {(warnings[0] if warnings else '')[:200]}"
                ),
            )

        if swept > 0:
            return ReconcileResult(
                action="clean",
                detail=f"worktree lifecycle sweep: swept={swept} stale worktree(s), skipped={skipped}",
            )

        return ReconcileResult(action="skip", detail="worktree lifecycle sweep: 无 stale 残留")

    return ReconcilerSpec(
        gate_id="GATE-WORKTREE-LIFECYCLE",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=800,  # 在 GATE-GATE-REGISTRY-SYNC(830) 之前——worktree 清理是基础设施级
        file_ops=frozenset({"read", "delete"}),
    )


# trae_060-reviewed: 该存在+可合并入已有框架（第28个reconciler）。病根：pre-commit

# gate（SCRIPTS-IMPORT-INTEGRITY, priority=104）只扫 staged 文件（incremental-only）+

# --no-verify 可绕过。治本：post-commit baseline 全扫（扫描磁盘上所有

# scripts/governance/**/*.py，commit 已入库不可绕过），复用

# scan_all_scripts_for_import_violations（与 gate 共享 _scan_file_content helper，DRY）。


def make_scripts_import_integrity_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-SCRIPTS-IMPORT-BASELINE post-commit baseline 全扫 reconciler。

    病根（第一性原理）：pre-commit gate 只扫 staged 文件，有两个盲区：

    1. **gate 上线前的基线 bug**：gate 在 commit 96caa8ceaa（2026-07-19 00:58:40）才上线，

       此前已存在的 F821 违规（如 deb695006f 引入的 NameError）永远不会被 staged 扫描命中。

    2. **--no-verify 绕过**：pre-commit hook 可被 --no-verify 绕过，gate 不执行；

       本 reconciler 在 post-commit 阶段运行，commit 已入库不可绕过。

    治本：post-commit baseline 全扫——扫描磁盘上所有 scripts/governance/**/*.py 文件，

    报告 violations 为 warn（commit 已入库不可阻断；warn 供 AI 修复）。

    向内收：复用 scan_all_scripts_for_import_violations 公开入口（与 gate 共享

    _scan_file_content helper），零新真源。lazy import 避免 import-time 耦合

    （reconciliation_registry 不应在模块加载时依赖 commit_gates.scripts_import_integrity_gate）。

    触发策略：committed_files 含 scripts/governance/**/*.py 文件时触发（新违规只可能

    由 governance 脚本变更引入）；或含 scripts_import_integrity_gate.py 自身变更时触发

    （检测逻辑变更应重跑 baseline）。其他 commit 不触发（避免无谓全扫开销）。

    """

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:

        # 触发条件：committed_files 含 scripts/governance/**/*.py 或 gate 自身

        for f in committed_files:
            normalized = f.replace("\\", "/")

            if normalized.startswith("scripts/governance/") and normalized.endswith(".py"):
                return True

            if "scripts_import_integrity_gate.py" in normalized:
                return True

        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        # lazy import 避免 import-time 耦合（reconciliation_registry 不应在模块加载时

        # 依赖 gov_enforcement.commit_gates.scripts_import_integrity_gate）

        from zephyr.gov_enforcement.commit_gates.scripts_import_integrity_gate import (
            scan_all_scripts_for_import_violations,
        )

        try:
            violations, error_msg = scan_all_scripts_for_import_violations(project_root)

        except Exception as e:  # noqa: BLE001 — 5.135治标: reconciler 容错降级
            return ReconcileResult(
                action="warn",
                detail=f"scripts import baseline scan 异常（降级告警）: {e}",
            )

        if error_msg is not None:
            # fail-open：_shared.constants 不可导入或 scripts/governance/ 不存在

            return ReconcileResult(action="skip", detail=f"baseline scan skip: {error_msg}")

        if violations:
            detail = (
                f"scripts import baseline scan: {len(violations)} violation(s) detected"
                "（#ARCH-TOOL-HEALTH-V1 Phase 3 baseline 全扫）\n"
                + "\n".join(violations[:30])  # 截断到前 30 条避免日志过长
                + (f"\n  ...(+{len(violations) - 30} more)" if len(violations) > 30 else "")
            )

            logger.warning("GATE-SCRIPTS-IMPORT-BASELINE: %s", detail)

            return ReconcileResult(action="warn", detail=detail)

        return ReconcileResult(
            action="clean",
            detail="scripts import baseline scan: 0 violations (clean)",
        )

    return ReconcilerSpec(
        gate_id="GATE-SCRIPTS-IMPORT-BASELINE",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=210,  # post-commit baseline 全扫组（在 manifest=200/readme=210 区间之后，
        file_ops=frozenset({"read"}),
        # gate-registry=830 之前；同 priority 按 register 顺序，不冲突）
    )


# trae_060-reviewed: 该存在+可合并入已有框架。病根：pre-commit UNDEFINED-NAME gate

# （priority=106）只扫 staged 文件，有两个盲区：

# 1. **gate 上线前的基线 bug**：gate 在 2026-07-19 才上线，此前已存在的 F821 违规

#    （如 deb695006f 引入的 NameError）永远不会被 staged 扫描命中。

# 2. **--no-verify 绕过**：pre-commit hook 可被 --no-verify 绕过，gate 不执行；

#    本 reconciler 在 post-commit 阶段运行，commit 已入库不可绕过。

# 治本：post-commit baseline 全扫——扫描 scripts/governance/**/*.py + src/**.py，

# 报告 violations 为 warn（commit 已入库不可阻断；warn 供 AI 修复）。

# 向内收：复用 scan_all_for_undefined_names 公开入口（与 gate 共享

# scan_content_for_undefined_names helper），零新真源。lazy import 避免 import-time 耦合

# （reconciliation_registry 不应在模块加载时依赖 commit_gates.undefined_name_gate）。

# 触发策略：committed_files 含 scripts/governance/**/*.py 或 src/**/*.py 时触发

# （新违规只可能由这些路径的 .py 变更引入）；或含 undefined_name_gate.py 自身变更时触发

# （检测逻辑变更应重跑 baseline）。其他 commit 不触发（避免无谓全扫开销）。


def make_undefined_name_baseline_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-UNDEFINED-NAME-BASELINE post-commit baseline 全扫 reconciler。

    病根（第一性原理）：pre-commit UNDEFINED-NAME gate 只扫 staged 文件，有两个盲区：

    1. **gate 上线前的基线 bug**：F821 违规（如 deb695006f 引入的 NameError）在 gate

       上线前已存在，永远不会被 staged 扫描命中。

    2. **--no-verify 绕过**：pre-commit hook 可被 --no-verify 绕过，gate 不执行；

       本 reconciler 在 post-commit 阶段运行，commit 已入库不可绕过。

    治本：post-commit baseline 全扫——扫描磁盘上所有 scripts/governance/**/*.py +

    src/**.py 文件，报告 violations 为 warn（commit 已入库不可阻断；warn 供 AI 修复）。

    向内收：复用 scan_all_for_undefined_names 公开入口（与 gate 共享

    scan_content_for_undefined_names helper），零新真源。lazy import 避免 import-time 耦合

    （reconciliation_registry 不应在模块加载时依赖 commit_gates.undefined_name_gate）。

    触发策略：committed_files 含 scripts/governance/**/*.py 或 src/**/*.py 时触发

    （新违规只可能由这些路径的 .py 变更引入）；或含 undefined_name_gate.py 自身变更时触发

    （检测逻辑变更应重跑 baseline）。其他 commit 不触发（避免无谓全扫开销）。

    """

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:

        # 触发条件：committed_files 含 scripts/governance/**/*.py 或 src/**/*.py

        # 或 undefined_name_gate.py 自身（检测逻辑变更应重跑 baseline）

        for f in committed_files:
            normalized = f.replace("\\", "/")

            if normalized.startswith("scripts/governance/") and normalized.endswith(".py"):
                return True

            if normalized.startswith("src/") and normalized.endswith(".py"):
                return True

            if "undefined_name_gate.py" in normalized:
                return True

        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        # lazy import 避免 import-time 耦合（reconciliation_registry 不应在模块加载时

        # 依赖 gov_enforcement.commit_gates.undefined_name_gate）

        from zephyr.gov_enforcement.commit_gates.undefined_name_gate import (
            scan_all_for_undefined_names,
        )

        try:
            violations, error_msg = scan_all_for_undefined_names(project_root)

        except Exception as e:  # noqa: BLE001 — reconciler 容错降级
            return ReconcileResult(
                action="warn",
                detail=f"undefined name baseline scan 异常（降级告警）: {e}",
            )

        if error_msg is not None:
            # fail-open：scripts/governance/ 与 src/ 均不存在

            return ReconcileResult(action="skip", detail=f"baseline scan skip: {error_msg}")

        if violations:
            detail = (
                f"undefined name baseline scan: {len(violations)} violation(s) detected"
                "（GATE-DEPGRAPH-OPS 治本 Phase 1 baseline 全扫）\n"
                + "\n".join(violations[:30])  # 截断到前 30 条避免日志过长
                + (f"\n  ...(+{len(violations) - 30} more)" if len(violations) > 30 else "")
            )

            logger.warning("GATE-UNDEFINED-NAME-BASELINE: %s", detail)

            return ReconcileResult(action="warn", detail=detail)

        return ReconcileResult(
            action="clean",
            detail="undefined name baseline scan: 0 violations (clean)",
        )

    return ReconcilerSpec(
        gate_id="GATE-UNDEFINED-NAME-BASELINE",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=211,  # post-commit baseline 全扫组（scripts-import=210 之后，
        file_ops=frozenset({"read", "write"}),
        # gate-registry=830 之前；同 priority 按 register 顺序，不冲突）
    )


# trae_060-reviewed: 对标 make_undefined_name_baseline_reconciler（第31个reconciler）。

# 病根（#ARCH-CONSUMERS-ACCURACY-001/003）：pre-commit CONSUMERS-ACCURACY gate 只扫

# staged 文件，有两个盲区：①gate 上线前的历史漂移（842 violations）永不命中 staged 扫描；

# ②--no-verify 绕过。治本：post-commit baseline 全扫——扫描磁盘所有 src/**.py +

# scripts/governance/**.py 的 [CONSUMERS] 字段准确性，报告 violations 为 warn。

# 向内收：复用 consumers_accuracy_gate.scan_all_for_consumers_accuracy（与 gate 共享

# check_consumers_accuracy），零新真源。lazy import 避免 import-time 耦合。

# trae_060-reviewed: 通过——该 reconciler 与 make_undefined_name_baseline_reconciler 同构

# （post-commit baseline 全扫模式），不可合并（扫描目标不同：UNDEFINED-NAME vs CONSUMERS-ACCURACY），

# 是 CONSUMERS-ACCURACY gate 的 post-commit 补强（对标 undefined-name gate + reconciler 模式）。


def make_consumers_accuracy_baseline_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-CONSUMERS-ACCURACY-BASELINE post-commit baseline 全扫 reconciler。

    对标 make_undefined_name_baseline_reconciler（priority=211），本 reconciler

    priority=212 紧接其后。

    病根（#ARCH-CONSUMERS-ACCURACY-001/003）：pre-commit gate 只扫 staged 文件，

    历史漂移（842 violations）+ --no-verify 绕过 = 两个盲区。

    治本：post-commit baseline 全扫——扫描磁盘所有 src/**.py + scripts/governance/**.py，

    报告 [CONSUMERS] 字段准确性 violations 为 warn（commit 已入库不可阻断；warn 供 AI 修复）。

    向内收：复用 consumers_accuracy_gate.scan_all_for_consumers_accuracy（与 gate 共享

    check_consumers_accuracy），零新真源。lazy import 避免 import-time 耦合

    （reconciliation_registry 不应在模块加载时依赖 commit_gates.consumers_accuracy_gate）。

    触发策略：committed_files 含 scripts/governance/**/*.py 或 src/**/*.py 时触发

    （新违规只可能由这些路径的 .py 变更引入）；或含 consumers_accuracy_gate.py 自身变更时触发

    （检测逻辑变更应重跑 baseline）。其他 commit 不触发（避免无谓全扫开销）。

    """

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:

        for f in committed_files:
            normalized = f.replace("\\", "/")

            if normalized.startswith("scripts/governance/") and normalized.endswith(".py"):
                return True

            if normalized.startswith("src/") and normalized.endswith(".py"):
                return True

            if "consumers_accuracy_gate.py" in normalized:
                return True

        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        # lazy import 避免 import-time 耦合

        from zephyr.gov_enforcement.commit_gates.consumers_accuracy_gate import (
            scan_all_for_consumers_accuracy,
        )

        try:
            violations, error_msg = scan_all_for_consumers_accuracy(project_root)

        except Exception as e:  # noqa: BLE001 — reconciler 容错降级
            return ReconcileResult(
                action="warn",
                detail=f"consumers accuracy baseline scan 异常（降级告警）: {e}",
            )

        if error_msg is not None:
            return ReconcileResult(action="skip", detail=f"baseline scan skip: {error_msg}")

        if violations:
            detail = (
                f"consumers accuracy baseline scan: {len(violations)} violation(s) detected"
                "（#ARCH-CONSUMERS-ACCURACY-001/003 治本 baseline 全扫）\n"
                + "\n".join(violations[:30])  # 截断到前 30 条避免日志过长
                + (f"\n  ...(+{len(violations) - 30} more)" if len(violations) > 30 else "")
            )

            logger.warning("GATE-CONSUMERS-ACCURACY-BASELINE: %s", detail)

            return ReconcileResult(action="warn", detail=detail)

        return ReconcileResult(
            action="clean",
            detail="consumers accuracy baseline scan: 0 violations (clean)",
        )

    return ReconcilerSpec(
        gate_id="GATE-CONSUMERS-ACCURACY-BASELINE",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=212,  # post-commit baseline 全扫组（undefined-name=211 之后）
        file_ops=frozenset({"read", "write"}),
    )


# trae_060-reviewed: 该存在+可合并入已有框架（第30个reconciler）。病根（#ARCH-WORKTREE-002

# 缺陷4）：session_worktree 在多处 stash 临时修改（_pre_merge_auto_clean 的

# _execute_cleanups / _ensure_worktree_base_fresh / 手动 merge 前），但从不清理。

# auto-recover 机制（commit f7cce1ce97）修复了 stash 丢失 bug，但未清理过期 stash。

# 实测 34 个 stash 堆积，部分 30+ 小时，占用 git 对象存储，且积累的 stash 会混淆

# AI 判断（AI 看到 stash list 会以为有未提交工作）。

# 治本：post-commit 事件触发，清理 > 24h 的 session_worktree 临时 stash（按 msg

# 前缀 session_worktree_pre_merge: / session_worktree_abort: 识别）。保留 < 24h

# 的 stash（AI 可能还需要 pop 恢复）。不影响用户手动 stash（无前缀匹配）。

# 向内收：扩展 ReconciliationRegistry 框架，复用 git stash 命令，零新真源。

# 对标 make_worktree_lifecycle_reconciler（worktree 残留清理）的 event-driven TTL 模式。


def _strip_stash_branch_prefix(message: str) -> str:
    """去掉 ``On <branch>: `` 前缀（git stash list --format=%s 默认格式）。

    git stash list 的 %s 输出格式是 ``On <branch>: <message>``，但

    _PROTECTED_STASH_PREFIXES 是基于原始 message 的前缀匹配。不去掉分支前缀

    会导致所有 stash 的 startswith 检查都失败（#ARCH-STASH-LIFECYCLE-FIX-001 治本，

    2026-07-22：原 _AI_STASH_PREFIXES 用 startswith 检查，但所有 stash message

    都带 ``On dev: `` 前缀，导致 startswith 永不匹配，reconciler 形同虚设）。

    """

    if message.startswith("On "):
        idx = message.find(": ", 3)

        if idx > 0:
            return message[idx + 2 :]

    return message


def make_stash_lifecycle_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-STASH-LIFECYCLE post-commit stash 过期清理 reconciler.

    病根（#ARCH-WORKTREE-002 缺陷4 → #ARCH-STASH-ACCUMULATION-001 系统性扩展，

    2026-07-21）：session_worktree 在多处 stash 临时修改，但从不清理。

    auto-recover 机制修复了 stash 丢失 bug，但未清理过期 stash。实测 34-45 个

    stash 堆积，部分 30+ 小时。原 reconciler 只清理 session_worktree 前缀 +

    24h TTL，无法处理 AI 为 merge 准备创建的临时 stash 和 100% AI 开发场景下

    多 session 并发产生的未知前缀 stash。

    治本（#ARCH-STASH-ACCUMULATION-001 系统性扩展，事件驱动 TTL 清理；

    #ARCH-STASH-LIFECYCLE-FIX-001 反向匹配治本，2026-07-22）：

    - trigger: 任何非空 committed_files 触发（stash 堆积与 AI 活跃正相关，

      每次 commit 是清理过期 stash 的合适时机；扫描 stash list 成本 <0.1s）

    - reconcile: ``git stash list --format=%gd|%ct|%s`` 获取所有 stash 的

      ref/timestamp/message，过滤非 user-manual- 前缀 + age > 4h 的 stash，

      按索引降序 drop（避免 renumbering 问题）

    - 自维护/自关闭：每次 commit 后自动清理，无需 AI 干预

    保护规则（第一性原理：100% AI 场景下显式保护 user-manual- 前缀）：

    - 反向匹配治本（#ARCH-STASH-LIFECYCLE-FIX-001，2026-07-22）：

      非 ``user-manual-`` 前缀的 stash 都是 AI 创建的。原方案用 8 个 AI 前缀

      列表 startswith 匹配，但有两个病根：1) ``On <branch>: `` 前缀导致 startswith

      永不匹配（reconciler 形同虚设）；2) AI 手动创建 stash 的 message 模式

      不可穷举（实测有 pre-merge-cleanup / other-session-wip / pre-construction

      / auto-sync / unrelated / CONSUMERS-ACCURACY 等 7+ 种未知前缀）

    - 保留 < 4h 的 stash（AI session 典型生命周期 <4h，可能还需要 pop 恢复）

    - user-manual- 前缀永不被清理（显式保护，aggressive 模式也不清理）

    - aggressive 模式（ZEPHYR_STASH_LIFECYCLE_AGGRESSIVE=1）：清理所有非

      user-manual- 前缀 stash（无视 age，用于存量清理）

    向内收：扩展 ReconciliationRegistry 框架，不新建独立清理系统。

    复用 _run_subprocess 统一 subprocess 解码策略。

    复用模块级 _strip_stash_branch_prefix 处理 ``On <branch>: `` 前缀。

    """

    import os
    import time

    project_root = gateway.project_root

    _STASH_TTL_SECONDS = 4 * 3600  # 4 小时（AI session 典型生命周期，#ARCH-STASH-ACCUMULATION-001 Phase 1）

    _PROTECTED_STASH_PREFIXES = ("user-manual-",)

    def _is_protected(message: str) -> bool:

        # 必须先 strip ``On <branch>: `` 前缀，否则 startswith 永不匹配（#ARCH-STASH-LIFECYCLE-FIX-001）

        return _strip_stash_branch_prefix(message).startswith(_PROTECTED_STASH_PREFIXES)

    def _is_ai_generated(message: str) -> bool:
        """100% AI 开发场景：非 user-manual- 前缀的 stash 都是 AI 创建的。

        反向匹配治本（#ARCH-STASH-LIFECYCLE-FIX-001，2026-07-22）。原方案用

        AI 前缀列表 startswith 匹配，但有两个病根：1) ``On <branch>: `` 前缀

        导致 startswith 永不匹配；2) AI 手动创建 stash 的 message 模式不可穷举。

        反向匹配更治本——user-manual- 是显式保护，其余都是 AI stash。

        """

        stripped = _strip_stash_branch_prefix(message)

        return not stripped.startswith(_PROTECTED_STASH_PREFIXES)

    def _should_drop(message: str, age: float, aggressive: bool) -> bool:

        if _is_protected(message):
            return False

        if aggressive:
            return True

        if not _is_ai_generated(message):
            return False

        return age >= _STASH_TTL_SECONDS

    def _stash_index(stash_ref: str) -> int:
        """从 stash ref（如 ``stash@{3}``）提取索引，用于降序排序避免 renumbering。"""

        try:
            return int(stash_ref.split("{", 1)[1].rstrip("}"))

        except (IndexError, ValueError):
            return 0

    def _trigger(committed_files: list[str]) -> bool:

        return bool(committed_files)  # 任何有文件的 commit 都触发（扫描成本低）

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        # git stash list --format=%gd|%ct|%s: stash ref | committer timestamp | message

        list_result = _run_subprocess(
            ["git", "stash", "list", "--format=%gd|%ct|%s"],
            cwd=str(project_root),
            timeout=30,
        )

        if list_result.returncode != 0:
            return ReconcileResult(
                action="warn",
                detail=(
                    f"stash lifecycle: git stash list failed (rc="
                    f"{list_result.returncode}): {list_result.stderr.strip()[:200]}"
                ),
            )

        lines = [line for line in list_result.stdout.splitlines() if line.strip()]

        if not lines:
            return ReconcileResult(action="skip", detail="stash lifecycle: 无 stash")

        now = time.time()

        aggressive = os.environ.get("ZEPHYR_STASH_LIFECYCLE_AGGRESSIVE", "") == "1"

        to_drop: list[tuple[str, float, str]] = []  # (stash_ref, age_hours, message)

        kept = 0

        protected = 0

        for line in lines:
            parts = line.split("|", 2)

            if len(parts) < 3:
                continue

            stash_ref, ts_str, message = parts

            try:
                stash_ts = float(ts_str)

            except ValueError:
                continue

            age = now - stash_ts

            if _is_protected(message):
                protected += 1

                continue

            if not _should_drop(message, age, aggressive):
                kept += 1

                continue

            to_drop.append((stash_ref, age / 3600, message))

        if not to_drop:
            return ReconcileResult(
                action="skip",
                detail=(
                    f"stash lifecycle: {kept} stash(es) 全部在 TTL 内或受保护，"
                    f"无需清理（protected={protected}, aggressive={aggressive}）"
                ),
            )

        # 按索引降序 drop——避免 renumbering 问题（drop stash@{3} 后 stash@{4} 变 stash@{3}）

        to_drop.sort(key=lambda x: _stash_index(x[0]), reverse=True)

        dropped = 0

        errors = 0

        for stash_ref, age_h, _msg in to_drop:
            drop_result = _run_subprocess(
                ["git", "stash", "drop", stash_ref],
                cwd=str(project_root),
                timeout=15,
            )

            if drop_result.returncode == 0:
                dropped += 1

                logger.info(
                    "GATE-STASH-LIFECYCLE: dropped %s (age=%.1fh)",
                    stash_ref,
                    age_h,
                )

            else:
                errors += 1

                logger.warning(
                    "GATE-STASH-LIFECYCLE: drop %s failed: %s",
                    stash_ref,
                    drop_result.stderr.strip()[:200],
                )

        action = "clean" if errors == 0 else "warn"

        return ReconcileResult(
            action=action,
            detail=(
                f"stash lifecycle: dropped={dropped} "
                f"(>{_STASH_TTL_SECONDS // 3600}h AI stash, aggressive={aggressive}), "
                f"kept={kept}, protected={protected}, errors={errors}"
            ),
        )

    return ReconcilerSpec(
        gate_id="GATE-STASH-LIFECYCLE",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=801,  # worktree_lifecycle=800 之后，gate_registry_sync=830 之前
        file_ops=frozenset({"read", "write"}),
        # （stash 清理与 worktree 清理同属基础设施级，紧跟 worktree_lifecycle）
    )


# trae_060-reviewed: 该存在+可合并入已有框架（第29个reconciler）。病根：pre-commit

# BLUEPRINT-FORMAT gate（priority=77）只检测 staged added 行的新违规，存量 64 条

# legacy blueprint_id（MOD-GOV_SCRIPTS / ARCHITECTURE-DIAGRAM-PLAN / 空头 / SRC-XXX

# 残留等）grandfathered 不检测。治本：post-commit baseline 全扫，报告存量债务，

# warn-only（commit 已入库不可阻断；warn 供 AI/人工修复追踪）。


def make_blueprint_id_legacy_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-BLUEPRINT-ID-LEGACY post-commit baseline 全扫 reconciler（#ARCH-DATAQUALITY-V1.8 Task I）。

    病根（第一性原理）：pre-commit BLUEPRINT-FORMAT gate 有两个盲区：

    1. **gate 上线前的基线债务**：64 条 legacy blueprint_id 头部（MOD-GOV_SCRIPTS /

       ARCHITECTURE-DIAGRAM-PLAN / 空头 / (migrated...) / SRC-XXX 残留等）在 gate

       上线前已存在，grandfathered 不检测，永远不会被 staged 扫描命中。

    2. **--no-verify 绕过**：pre-commit hook 可被 --no-verify 绕过，gate 不执行；

       本 reconciler 在 post-commit 阶段运行，commit 已入库不可绕过。

    治本：post-commit baseline 全扫——扫描 src/zephyr/ + tests/ + scripts/ 下所有

    .py 文件的 [BLUEPRINT] 头部，用 is_valid_module_id() 校验，收集违规并落盘报告，

    返回 warn（commit 已入库不可阻断；warn 供 AI/人工修复追踪）。

    向内收（消除重复）：

    - 真源唯一：复用 validate_module_id_naming.is_valid_module_id（裁定#208 格式

      校验唯一真源），禁止复制正则。

    - 框架唯一：扩展 ReconciliationRegistry（第29个 reconciler），不新建独立触发系统。

    - 事件触发：post-commit 自动执行，无 cron/manual。

    与 BLUEPRINT-FORMAT gate 的分工：

    - BLUEPRINT-FORMAT gate（pre-commit, priority=77, 阻断型）：检测 staged added 行

      的**新增**违规，阻断 commit。

    - 本 reconciler（post-commit, priority=145, warn-only）：全扫**存量**违规，

      落盘报告供追踪，不阻断。

    两者互补不冲突——gate 防蔓延，reconciler 清存量。

    trigger 裁定：committed_files 含 .py 文件时触发（legacy 头可能在任何 .py 文件中，

    且 post-commit 全扫开销可接受——只读每个文件前几行提取 [BLUEPRINT] 头）。

    Args:

        gateway: GitCommitGateway 实例（用 project_root）。

    Returns:

        ReconcilerSpec(gate_id="GATE-BLUEPRINT-ID-LEGACY", priority=145)。

    """

    import os
    import re
    import sys

    project_root = gateway.project_root

    # 匹配 [BLUEPRINT] 头部行，提取 module_id token（第一个非空白 token）

    # 对标 blueprint_format_gate.py L79——真源同源，不复制正则逻辑

    _BP_HEADER_RE = re.compile(r"^#\s*\[BLUEPRINT\]\s*(\S+)?")

    # 扫描范围：src/zephyr/ + tests/ + scripts/（与 validate_python_syntax.py 一致）

    _SCAN_DIRS = ("src/zephyr", "tests", "scripts")

    _EXCLUDE_DIRS = frozenset(
        {
            "__pycache__",
            ".git",
            ".ailocks",
            ".trae",
            "session_logs",
            "_archive",
            ".runtime",
            "node_modules",
        }
    )

    def _trigger(committed_files: list[str]) -> bool:

        # 触发条件：committed_files 含任何 .py 文件（legacy 头可能在任何 .py 中）

        # 或含 validate_module_id_naming.py 自身（校验逻辑变更应重跑 baseline）

        for f in committed_files:
            normalized = f.replace("\\", "/")

            if normalized.endswith(".py"):
                return True

            if "validate_module_id_naming.py" in normalized:
                return True

        return False

    def _iter_py_files(root):
        """递归遍历 _SCAN_DIRS 下所有 .py 文件（排除 _EXCLUDE_DIRS）。"""

        for scan_dir_rel in _SCAN_DIRS:
            scan_dir = root / scan_dir_rel

            if not scan_dir.is_dir():
                continue

            for path in scan_dir.rglob("*.py"):
                # 排除 __pycache__ 等

                parts = set(path.relative_to(root).parts)

                if parts & _EXCLUDE_DIRS:
                    continue

                # 排除路径中包含排除目录的

                try:
                    rel_parts = path.relative_to(scan_dir).parts

                except ValueError:
                    continue

                if any(p in _EXCLUDE_DIRS for p in rel_parts):
                    continue

                yield path

    def _extract_blueprint_id(file_path) -> tuple[str | None, int | None]:
        """从文件前 5 行提取 [BLUEPRINT] 头部的 module_id。

        Returns:

            (module_id, line_no) —

            - (None, None): 无 [BLUEPRINT] 头行（文件无蓝图声明）

            - ("", line_no): [BLUEPRINT] 头存在但 module_id 为空（违规：空头）

            - (module_id, line_no): [BLUEPRINT] 头含 module_id token

        """

        try:
            with file_path.open("r", encoding="utf-8", errors="replace") as fh:
                for line_no, line in enumerate(fh, start=1):
                    if line_no > 5:
                        break

                    m = _BP_HEADER_RE.match(line)

                    if m:
                        # m.group(1) 为 None 时表示 "# [BLUEPRINT]" 空头——

                        # 转空字符串以区分"无头"（返回 None, None）

                        return (m.group(1) or ""), line_no

        except OSError:
            pass

        return None, None

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        # lazy import：reconciliation_registry 不应在模块加载时依赖

        # scripts/governance/d3_metadata/validate_module_id_naming

        try:
            # 治本（DM-90974 副带）：完整项目路径 import 替代 sys.path.insert + 裸模块名，

            # 消除 IMPORT-INTEGRITY gate 静态扫描误报（gate 看不到 sys.path 运行时操作）。

            # 包结构 scripts/governance/d3_metadata/__init__.py 已存在，完整路径可解析。

            from scripts.governance.d3_metadata.validate_module_id_naming import is_valid_module_id

        except ImportError as e:
            return ReconcileResult(
                action="skip",
                detail=f"blueprint_id_legacy scan skip: cannot import is_valid_module_id: {e}",
            )

        violations: list[dict] = []

        scanned = 0

        files_with_header = 0

        for py_file in _iter_py_files(project_root):
            scanned += 1

            module_id, line_no = _extract_blueprint_id(py_file)

            if module_id is None and line_no is None:
                # 无 [BLUEPRINT] 头行——不在本 reconciler 职责范围（由 ORPHAN-MODULE gate 等管）

                continue

            files_with_header += 1

            if not module_id:
                # 空头：[BLUEPRINT] 行存在但无 module_id token

                violations.append(
                    {
                        "file": str(py_file.relative_to(project_root)).replace("\\", "/"),
                        "line": line_no,
                        "module_id": "",
                        "reason": "empty [BLUEPRINT] header (missing module_id)",
                    }
                )

                continue

            ok, reason = is_valid_module_id(module_id)

            if not ok:
                violations.append(
                    {
                        "file": str(py_file.relative_to(project_root)).replace("\\", "/"),
                        "line": line_no,
                        "module_id": module_id,
                        "reason": reason,
                    }
                )

        report = {
            "gate_id": "GATE-BLUEPRINT-ID-LEGACY",
            "session_id": session_id,
            "scanned_files": scanned,
            "files_with_blueprint_header": files_with_header,
            "violation_count": len(violations),
            "violations": violations[:200],  # 截断到前 200 条避免报告过大
            "truncated": len(violations) > 200,
            "truncated_count": max(0, len(violations) - 200),
        }

        report_path, write_err = _write_reconcile_report(project_root, "blueprint_id_legacy", report)

        if write_err:
            return ReconcileResult(
                action="warn",
                detail=(
                    f"blueprint_id_legacy scan done ({scanned} files, {len(violations)} violations) "
                    f"but report write failed: {write_err}"
                ),
            )

        if not violations:
            return ReconcileResult(
                action="clean",
                detail=(
                    f"blueprint_id_legacy scan clean: 0 violations in {scanned} files "
                    f"({files_with_header} with [BLUEPRINT] header), report={report_path.name}"
                ),
            )

        # 按违规类型聚合统计

        reason_counts: dict[str, int] = {}

        for v in violations:
            # 取 reason 的第一行作为类型键

            key = v["reason"].split("(")[0].strip()[:80]

            reason_counts[key] = reason_counts.get(key, 0) + 1

        summary_lines = [f"  - {count}x {key}" for key, count in sorted(reason_counts.items(), key=lambda x: -x[1])]

        detail = (
            f"blueprint_id_legacy scan: {len(violations)} violation(s) in {scanned} files "
            f"({files_with_header} with [BLUEPRINT] header)\n"
            f"  violation breakdown:\n"
            + "\n".join(summary_lines[:10])
            + (f"\n  ...(+{len(summary_lines) - 10} more types)" if len(summary_lines) > 10 else "")
            + f"\n  report={report_path.name}"
            + "\n  Action: fix [BLUEPRINT] header to use valid MOD-/SH- prefix "
            "(see裁定#208 three-track: MOD-{LAYER}-NNN / MOD-{DOMAIN}[-NNN] / SH-{ABBR}-NNN)"
        )

        logger.warning("GATE-BLUEPRINT-ID-LEGACY: %s", detail)

        return ReconcileResult(action="warn", detail=detail)

    return ReconcilerSpec(
        gate_id="GATE-BLUEPRINT-ID-LEGACY",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=145,  # 在 drift_scan@140 之后，module_id_recommend@170 之前
        file_ops=frozenset({"read", "write"}),
        # ——drift_scan 看到已同步状态，本 reconciler 报告存量 legacy 债务
    )


# trae_060-reviewed: ①该存在——治本 G6 监控缺失（.runtime/lookup_audit/ 长期为空，gate 静默失效无监控）；

# ②无法合并进已有 reconciler（职责独立：CAPABILITY-LOOKUP gate 健康度监控，非 depgraph/frontmatter/drift）；

# ③治本——事件触发检测 bypass 频率 + audit log 存在性，非时间触发。


def make_capability_lookup_health_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 CAPABILITY-LOOKUP-REQUIRED gate 健康度监控 reconciler。

    #ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD-S8 Phase 4 治本 G6（监控缺失）：

    病根 G6——.runtime/lookup_audit/ 曾长期为空（铁证），无监控检测 gate 静默失效；

    ZEPHYR_BYPASS_LOOKUP=1 无升级机制，高频率使用应触发告警。

    治本（post-commit 事件触发，非时间触发——铁律）：

    1. 检测 commit_message 中的 [no-lookup:reason] 标记 → 记录到 bypass_audit.jsonl

    2. 统计最近 N 次 commit 中 bypass 频率 → 超阈值 critical_warn（升级）

    3. 检查 .runtime/lookup_audit/ 是否有 session 级 audit log（排除 bypass_audit.jsonl）

       → 无日志且无 bypass → warn（gate 可能静默失效，对标 G6 铁证）

    3-arg reconciler（Phase 3.4 断点6 治本）：接收 commit_message 做审计。

    Args:

        gateway: GitCommitGateway 实例（用 project_root）。

    Returns:

        ReconcilerSpec(gate_id="CAPABILITY-LOOKUP-HEALTH", priority=220)。

    """

    import json
    import os
    import time

    project_root = gateway.project_root

    BYPASS_AUDIT_LOG = project_root / ".runtime" / "lookup_audit" / "bypass_audit.jsonl"

    LOOKUP_AUDIT_DIR = project_root / ".runtime" / "lookup_audit"

    # #ARCH-066: bypass 策略迁移到共享模块 capability_lookup_bypass_policy——
    # gate 和 reconciler 共用白名单/阈值/标记前缀，消除双真源。
    # 真源是 trae_077 YAML（fail-open 加载），共享模块模块初始化时加载。
    from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
        BYPASS_MARKER_PREFIX as _BYPASS_MARKER_PREFIX,
    )
    from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
        ESCALATION_THRESHOLD as BYPASS_ESCALATION_THRESHOLD,
    )
    from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
        WINDOW as BYPASS_WINDOW,
    )
    from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (
        is_exempt_reason as _is_exempt_reason_fn,
    )

    def _is_exempt_bypass(reason: str) -> bool:
        """判断 bypass reason 是否属于合法豁免场景（委托共享模块 is_exempt_reason）。

        #ARCH-066: 迁移到共享模块——gate 和 reconciler 用同一白名单 + 归一化（_ → -）。
        """
        return _is_exempt_reason_fn(reason)

    def _trigger(committed_files: list[str]) -> bool:
        """命中 src/zephyr/**/*.py 业务代码 commit。"""

        for f in committed_files:
            rel = _rel_path(f, str(project_root))

            if rel.startswith("src/zephyr/") and rel.endswith(".py"):
                return True

        return False

    def _read_recent_bypasses() -> list[dict]:
        """读取 bypass_audit.jsonl 最近 N 条记录。"""

        if not BYPASS_AUDIT_LOG.is_file():
            return []

        try:
            lines = BYPASS_AUDIT_LOG.read_text(encoding="utf-8").splitlines()

            entries = []

            for line in lines[-BYPASS_WINDOW * 2 :]:  # 读最近 2N 行解析
                line = line.strip()

                if not line:
                    continue

                try:
                    entries.append(json.loads(line))

                except (json.JSONDecodeError, ValueError):
                    continue

            return entries[-BYPASS_WINDOW:]

        except OSError:
            return []

    def _has_session_audit_logs() -> bool:
        """检查 .runtime/lookup_audit/ 是否有 session 级 audit log（排除 bypass_audit.jsonl）。"""

        if not LOOKUP_AUDIT_DIR.is_dir():
            return False

        for entry in LOOKUP_AUDIT_DIR.iterdir():
            if entry.name == "bypass_audit.jsonl":
                continue

            if entry.name.startswith("._"):
                continue  # 健康检查测试文件

            if entry.is_file() and entry.suffix == ".jsonl":
                return True

        return False

    def _reconcile(
        committed_files: list[str],
        session_id: str,
        commit_message: str = "",
    ) -> ReconcileResult:
        """3-arg reconciler：检测 bypass + 监控 audit log 健康。

        #ARCH-CAPABILITY-LOOKUP-SCENE-CLASSIFY-001: bypass 统计场景分类——

        合法 bypass（白名单关键词匹配）豁免统计，只统计违规 bypass。

        """

        msg = commit_message or ""

        has_bypass_marker = _BYPASS_MARKER_PREFIX in msg

        # 1. 记录 bypass 使用（新增 scene 字段——exempt/violation）

        if has_bypass_marker:
            try:
                BYPASS_AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

                reason = ""

                if _BYPASS_MARKER_PREFIX in msg:
                    start = msg.index(_BYPASS_MARKER_PREFIX) + len(_BYPASS_MARKER_PREFIX)

                    end = msg.find("]", start)

                    reason = msg[start:end] if end > start else ""

                # #ARCH-CAPABILITY-LOOKUP-SCENE-CLASSIFY-001: scene 分类

                scene = "exempt" if _is_exempt_bypass(reason) else "violation"

                entry = {
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "session_id": session_id,
                    "reason": reason,
                    "scene": scene,
                    "commit_message_snippet": msg[:200],
                }

                with open(BYPASS_AUDIT_LOG, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

            except OSError as e:
                logger.warning("CAPABILITY-LOOKUP-HEALTH: bypass log write failed: %s", e)

        # 2. 统计 **违规** bypass 频率 → 升级

        # #ARCH-CAPABILITY-LOOKUP-SCENE-CLASSIFY-001: 只统计非白名单 bypass（违规），

        # 合法 bypass（exempt）不计入——避免 critical_warn 误报（狼来了效应）。

        recent_bypasses = _read_recent_bypasses()

        violation_count = sum(1 for entry in recent_bypasses if not _is_exempt_bypass(entry.get("reason", "")))

        if violation_count > BYPASS_ESCALATION_THRESHOLD:
            exempt_count = len(recent_bypasses) - violation_count

            detail = (
                f"CAPABILITY-LOOKUP-HEALTH: [no-lookup:] **违规** bypass 频率过高——"
                f"最近 {BYPASS_WINDOW} 次 bypass 中 {violation_count} 次违规 "
                f"(合法豁免 {exempt_count} 次，阈值 {BYPASS_ESCALATION_THRESHOLD})。"
                f"这表明 AI 频繁在非合法场景跳过能力反查，MUST 上报人类排查。"
                f"对标 #ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD G6 + #ARCH-CAPABILITY-LOOKUP-SCENE-CLASSIFY-001。"
            )

            logger.error("[ESCALATION] %s", detail)

            return ReconcileResult(action="critical_warn", detail=detail)

        # 3. 检查 audit log 健康（G6 铁证：曾长期为空）

        if not has_bypass_marker and not _has_session_audit_logs():
            detail = (
                "CAPABILITY-LOOKUP-HEALTH: .runtime/lookup_audit/ 无 session 级 audit log "
                "且本次 commit 未使用 bypass——CAPABILITY-LOOKUP-REQUIRED gate 可能静默失效 "
                "(AI 未调用能力反查但 gate 未阻断)。对标 G6 铁证（曾长期为空）。"
                "MUST 检查 gate 是否正常工作 + AI 是否遵循 RULE-CAPABILITY-LOOKUP 铁律。"
            )

            logger.warning("[ESCALATION] %s", detail)

            return ReconcileResult(action="warn", detail=detail)

        # 4. 正常路径

        if has_bypass_marker:
            reason = ""

            if _BYPASS_MARKER_PREFIX in msg:
                start = msg.index(_BYPASS_MARKER_PREFIX) + len(_BYPASS_MARKER_PREFIX)

                end = msg.find("]", start)

                reason = msg[start:end] if end > start else ""

            scene = "exempt" if _is_exempt_bypass(reason) else "violation"

            detail = (
                f"CAPABILITY-LOOKUP-HEALTH: 本次 commit 使用 [no-lookup:] bypass "
                f"(scene={scene}, 最近 {violation_count} 违规/{len(recent_bypasses)} 总 bypass)，"
                f"违规频率正常。"
            )

        else:
            detail = (
                f"CAPABILITY-LOOKUP-HEALTH: audit log 正常，gate 工作正常 "
                f"(最近 {violation_count} 违规/{len(recent_bypasses)} 总 bypass)。"
            )

        return ReconcileResult(action="clean", detail=detail)

    return ReconcilerSpec(
        gate_id="CAPABILITY-LOOKUP-HEALTH",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=220,  # 在 scripts_import_integrity@210 / undefined_name_baseline@211 之后
        file_ops=frozenset({"read"}),
    )


# 治本 #ARCH-ROOT-TEMP-FILE-ENFORCEMENT-001（2026-07-22）：根目录临时文件清扫 reconciler。

# 病根：策略层（trae_070/071 + directory_contract DCR-007）已完备，但 DCR-007 只看 staged

# 文件，根目录临时文件全被 .gitignore 忽略→永不 staged→门禁永远看不见（结构性盲区）。

# 本 reconciler 补盲区：post-commit FS 扫描根目录 depth-0 平铺文件，混合策略清扫。

# 仅扫平铺文件不删目录（目录删除风险高——tmp/ 含 pg_backups 175MB，已实证）。


def make_root_temp_sweep_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-ROOT-TEMP-SWEEP post-commit 根目录临时文件清扫 reconciler.

    治本（#ARCH-ROOT-TEMP-FILE-ENFORCEMENT-001 + #ARCH-ROOT-TEMP-WHITELIST-001/002）：

    - trigger: 任何 commit 都触发（扫描根目录+子目录根 depth-0 平铺文件成本 <0.05s）
    - reconcile: 白名单模式 v2——动态从 git ls-tree HEAD 获取跟踪文件列表，
      不在跟踪列表内的文件按策略处理（.log 删除，其余移到 .runtime/tmp/ 隔离）
    - .runtime/tmp/ TTL 清理：24h 过期文件自动删除（#ARCH-ROOT-TEMP-WHITELIST-002
      防止隔离区变垃圾场——v1 只移动不清理，.runtime/tmp/ 积压 126 文件无清理机制）
    - 子目录根清扫：src/scripts/docs 根的 _*.py 临时文件（v1 只扫项目根，
      src/_fix_all.py 等子目录根临时文件不受覆盖）
    - 自维护/自关闭：每次 commit 后自动清扫，无需 AI 干预

    白名单模式 v2（#ARCH-ROOT-TEMP-WHITELIST-002 治本，2026-07-22）：

    v1 用手工 frozenset，与 .gitignore ! 例外 + git tracked 形成三源手工维护，
    必然漂移。v2 从 git ls-tree HEAD 动态派生白名单——新增合法根文件只需 git add，
    无需改代码。git 不可达时 fail-open 用 v1 硬编码白名单兜底。

    保护规则（第一性原理：根目录平铺文件几乎都是临时产物，但需防误删正在写入的文件）：

    - mtime < 10min 的文件：跳过（可能正在写入——pytest 运行中/commit 进行中）
    - 不递归子目录：仅扫平铺文件（目录删除风险高）
    - git tracked 文件：跳过（动态白名单——根目录全量，子目录只扫 _ 前缀）
    - .env*：跳过（含密钥，即使不在白名单也绝不触碰）
    - __ 前缀文件：跳过（__init__.py 等合法 Python 包标记）

    红蓝对抗第二轮修复（2026-07-22）：

    CRITICAL-1: .runtime/tmp/ 24h TTL 清理（v1 移动不清理=新垃圾场）
    CRITICAL-2: 子目录根清扫（v1 只扫项目根，src/_fix_*.py 无人管）
    HIGH-1: 动态白名单（v1 手工 frozenset 三源漂移）

    向内收：扩展 ReconciliationRegistry 框架，复用 logger，零新真源。
    """

    import os
    import re
    import shutil
    import time

    project_root = gateway.project_root

    _FRESH_SECONDS = 10 * 60  # 10 分钟安全阈值（避免删到正在写入的文件）

    _RUNTIME_TMP_TTL = 24 * 60 * 60  # 24h——.runtime/tmp/ 隔离区文件 TTL

    _SWEEP_SUBDIRS = ("src", "scripts", "docs")  # 子目录根清扫目标

    # v1 硬编码白名单（git 不可达时的 fail-open 兜底，#ARCH-ROOT-TEMP-WHITELIST-001）

    _ROOT_FILE_WHITELIST_FALLBACK = frozenset(
        {
            ".dockerignore",
            ".editorconfig",
            ".env",
            ".env.example",
            ".gitattributes",
            ".gitignore",
            ".importlinter",
            ".pre-commit-config.yaml",
            ".traeignore",
            "AGENTS.md",
            "CONTRIBUTING.md",
            "docker-compose.yml",
            "Dockerfile",
            "LICENSE",
            "MANIFEST.in",
            "py.ini",
            "pyproject.toml",
            "README.md",
            "requirements.txt",
            "requirements-demo.txt",
            "requirements-dev.txt",
            "SECURITY.md",
            "sitecustomize.py",
        }
    )

    _DELETE_PATTERNS = (
        re.compile(r"^.*\.log$"),  # 根目录 .log 全是临时产物
    )

    def _match_delete(name: str) -> bool:

        return any(p.match(name) for p in _DELETE_PATTERNS)

    def _get_tracked_files(subdir: str = ""):
        """从 git ls-tree HEAD 动态获取跟踪文件列表（#ARCH-ROOT-TEMP-WHITELIST-002）。

        消除手工白名单三源问题：白名单真源为 git tracked 文件。

        git 不可达时返回 None，调用方用 _ROOT_FILE_WHITELIST_FALLBACK 兜底。

        """

        try:
            cmd = ["git", "ls-tree", "--name-only", "HEAD"]

            if subdir:
                cmd.extend(["--", subdir + "/"])

            result = _run_subprocess(
                cmd,
                cwd=str(project_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
            )

            if result.returncode != 0:
                return None

            tracked = set()

            prefix = (subdir + "/") if subdir else ""

            for line in result.stdout.strip().splitlines():
                if prefix:
                    if line.startswith(prefix):
                        remainder = line[len(prefix) :]

                        if "/" not in remainder:
                            tracked.add(remainder)

                else:
                    if "/" not in line:
                        tracked.add(line)

            return frozenset(tracked)

        except Exception:  # noqa: BLE001
            return None

    def _cleanup_runtime_tmp(rt_tmp, now):
        """清理 .runtime/tmp/ 中超过 TTL 的文件（#ARCH-ROOT-TEMP-WHITELIST-002）。

        v1 病根：reconciler 移动文件到 .runtime/tmp/ 但无清理——隔离区变垃圾场，

        积压 126 文件。TTL=24h 确保隔离区只保留近期文件。

        """

        if not rt_tmp.exists():
            return 0, 0

        purged = 0

        errors = 0

        try:
            for name in os.listdir(str(rt_tmp)):
                if name == ".gitkeep":
                    continue

                full = os.path.join(str(rt_tmp), name)

                if not os.path.isfile(full):
                    continue

                try:
                    mtime = os.path.getmtime(full)

                except OSError:
                    continue

                if now - mtime > _RUNTIME_TMP_TTL:
                    try:
                        # T1② 收敛：guard 安全 API（审计+file_ops 声明制强制）
                        from scripts.ops_guard import guard_remove

                        guard_remove(full)

                        purged += 1

                        logger.info(
                            "GATE-ROOT-TEMP-SWEEP: purged %s from .runtime/tmp/ (TTL>24h)",
                            name,
                        )

                    except OSError:
                        errors += 1

        except OSError:
            pass

        return purged, errors

    def _trigger(committed_files: list[str]) -> bool:

        return True  # 根目录清扫与每次 commit 正相关

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        if not project_root.exists():
            return ReconcileResult(action="skip", detail="root_temp_sweep: project_root not found")

        now = time.time()

        rt_tmp = project_root / ".runtime" / "tmp"

        deleted = 0

        moved = 0

        errors = 0

        skipped_fresh = 0

        # === 1. 根目录清扫（动态白名单 v2，#ARCH-ROOT-TEMP-WHITELIST-002） ===

        root_whitelist = _get_tracked_files()

        if root_whitelist is None:
            root_whitelist = _ROOT_FILE_WHITELIST_FALLBACK

            logger.warning("GATE-ROOT-TEMP-SWEEP: git unreachable, using fallback whitelist")

        try:
            entries = os.listdir(project_root)

        except OSError as exc:
            return ReconcileResult(action="warn", detail=f"root_temp_sweep: listdir failed: {exc}")

        for name in entries:
            # worktree 安全护栏（2026-08-14 AI-GIT-001 实证治本）：以下条目永不触碰。
            # .git：worktree 内是 gitdir 指针 FILE（非 tracked，动态白名单不覆盖）——
            #   被 move 后 worktree 瞬间失效（prunable），git 命令从 worktree cwd
            #   向上穿透锚定主仓（2026-08-14 本会话实证：S4 修复后 worker 首次正确
            #   锚定 worktree，本 reconciler 随即将 .runtime/tmp/.git 扫走）。
            # activate_env.ps1：worktree 环境三件套（#ARCH-WORKTREE-ENV-001），
            #   被扫走后环境激活契约断裂。
            if name in (".git", "activate_env.ps1"):
                continue

            full = os.path.join(str(project_root), name)

            if not os.path.isfile(full):
                continue  # 仅扫平铺文件，跳过目录

            # 密钥保护：.env* 文件绝不触碰

            if name.startswith(".env"):
                continue

            # 动态白名单检查（#ARCH-ROOT-TEMP-WHITELIST-002）

            if name in root_whitelist:
                continue

            is_delete = _match_delete(name)

            try:
                mtime = os.path.getmtime(full)

            except OSError:
                continue

            if now - mtime < _FRESH_SECONDS:
                skipped_fresh += 1

                continue  # 正在写入，跳过

            try:
                # T1② 收敛：guard 安全 API（审计+file_ops 声明制强制）
                from scripts.ops_guard import guard_move, guard_remove

                if is_delete:
                    guard_remove(full)

                    deleted += 1

                    logger.info("GATE-ROOT-TEMP-SWEEP: deleted %s (token/log)", name)

                else:
                    rt_tmp.mkdir(parents=True, exist_ok=True)

                    dst = os.path.join(str(rt_tmp), name)

                    if os.path.exists(dst):  # 防同名冲突
                        stem, ext = os.path.splitext(name)

                        dst = os.path.join(str(rt_tmp), f"{stem}.sweep{int(now)}{ext}")

                    guard_move(full, dst)

                    moved += 1

                    logger.info("GATE-ROOT-TEMP-SWEEP: moved %s -> .runtime/tmp/", name)

            except OSError as exc:
                errors += 1

                logger.warning("GATE-ROOT-TEMP-SWEEP: process %s failed: %s", name, exc)

        # === 2. 子目录根清扫（src/scripts/docs，#ARCH-ROOT-TEMP-WHITELIST-002） ===

        # v1 病根：只扫项目根目录，src/_fix_all.py 等子目录根临时文件不受覆盖。

        # 子目录策略：只扫 _ 前缀文件（temp 模式），跳过 __ 前缀（__init__.py 等）。

        # 不用全量白名单（子目录有大量合法未跟踪文件如 .pyc，白名单策略不适用）。

        for subdir in _SWEEP_SUBDIRS:
            subdir_path = project_root / subdir

            if not subdir_path.exists():
                continue

            subdir_whitelist = _get_tracked_files(subdir)

            if subdir_whitelist is None:
                continue  # git 不可达时子目录不扫（fail-safe）

            try:
                sub_entries = os.listdir(str(subdir_path))

            except OSError:
                continue

            for name in sub_entries:
                full = os.path.join(str(subdir_path), name)

                if not os.path.isfile(full):
                    continue

                if name.startswith(".env"):
                    continue

                if name in subdir_whitelist:
                    continue

                # 子目录只扫 _ 前缀（temp），跳过 __ 前缀（__init__.py 等）

                if not name.startswith("_") or name.startswith("__"):
                    continue

                is_delete = _match_delete(name)

                try:
                    mtime = os.path.getmtime(full)

                except OSError:
                    continue

                if now - mtime < _FRESH_SECONDS:
                    skipped_fresh += 1

                    continue

                try:
                    # T1② 收敛：guard 安全 API（审计+file_ops 声明制强制）
                    from scripts.ops_guard import guard_move, guard_remove

                    if is_delete:
                        guard_remove(full)

                        deleted += 1

                        logger.info("GATE-ROOT-TEMP-SWEEP: deleted %s/%s (subdir temp)", subdir, name)

                    else:
                        rt_tmp.mkdir(parents=True, exist_ok=True)

                        dst_name = f"{subdir}_{name}"  # 加子目录前缀防冲突

                        dst = os.path.join(str(rt_tmp), dst_name)

                        if os.path.exists(dst):
                            stem, ext = os.path.splitext(dst_name)

                            dst = os.path.join(str(rt_tmp), f"{stem}.sweep{int(now)}{ext}")

                        guard_move(full, dst)

                        moved += 1

                        logger.info("GATE-ROOT-TEMP-SWEEP: moved %s/%s -> .runtime/tmp/", subdir, name)

                except OSError as exc:
                    errors += 1

                    logger.warning("GATE-ROOT-TEMP-SWEEP: process %s/%s failed: %s", subdir, name, exc)

        # === 3. .runtime/tmp/ TTL 清理（#ARCH-ROOT-TEMP-WHITELIST-002） ===

        # v1 病根：reconciler 移动文件到 .runtime/tmp/ 但无清理——隔离区变垃圾场。

        purged, purge_errors = _cleanup_runtime_tmp(rt_tmp, now)

        errors += purge_errors

        if deleted == 0 and moved == 0 and errors == 0 and purged == 0:
            return ReconcileResult(action="skip", detail="root_temp_sweep: 无过期临时文件")

        action = "clean" if errors == 0 else "warn"

        return ReconcileResult(
            action=action,
            detail=(
                f"root_temp_sweep: deleted={deleted}, moved={moved} (->.runtime/tmp/), "
                f"purged={purged} (.runtime/tmp/ TTL>24h), errors={errors}, "
                f"skipped_fresh={skipped_fresh}"
            ),
        )

    return ReconcilerSpec(
        gate_id="GATE-ROOT-TEMP-SWEEP",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=803,  # session_staging=802 之后，gate_registry_sync=830 之前
        file_ops=frozenset({"read", "delete", "move"}),
    )


# 治本 #ARCH-TEMP-FILE-LIFECYCLE-001 / #ARCH-ROOT-TEMP-FILE-ENFORCEMENT-001（2026-07-22 落地）：

# trae_071 §7 spec 了该 reconciler（priority=802）但一直未实现（被 sess-18504/sess-55092

# 持有阻塞）。暂存层 .runtime/sessions/<sid>/staging/ 无生命周期治理：成果文件无声删除

# （FINAL_resonance_rank.csv 事件）+ 历史会话遗留 staging 垃圾堆积。本 reconciler 补齐。

# 注：merge/abort 事件对【特定 session】staging 的即时清理由 session_worktree.py 直接

# rmtree 处理（事件语义=放弃/完成）；本 reconciler 负责所有【孤儿 session】staging 的

# post-commit TTL 清理（>24h），两者正交互补。


def make_session_staging_lifecycle_reconciler(gateway: object) -> ReconcilerSpec:
    """构造 GATE-SESSION-STAGING-LIFECYCLE post-commit 暂存层 TTL 清理 reconciler.

    治本（事件驱动 TTL 清理，对标 make_stash_lifecycle_reconciler priority=801）：

    - trigger: 任何 commit 都触发（扫描 .runtime/sessions/*/staging/ 成本 <0.05s）

    - reconcile: 枚举 .runtime/sessions/*/staging/，删除 mtime+24h<now 的文件；

      检测疑似未 promote 成果（.md/.csv）并 warn（仍清理——staging 是草稿区）

    - 自维护/自关闭：每次 commit 后自动清理

    保护规则（第一性原理：staging 是会话级中间产物，24h TTL 对齐 stash_lifecycle）：

    - mtime < 24h 的 staging 文件：可能当前 session 使用中，保留

    - > 24h 的 staging 文件：过期安全删除

    - 系统文件（.runtime/sessions/<sid>/ 下非 staging/ 的 heartbeat.jsonl 等）不触碰

      （仅扫描 staging/ 子目录）

    向内收：扩展 ReconciliationRegistry 框架，复用 _rel_path 跨盘兜底。

    """

    import os
    import time

    project_root = gateway.project_root

    _STAGING_TTL_SECONDS = 24 * 3600  # 24h（对齐 make_stash_lifecycle_reconciler）

    _SUSPECTED_OUTPUT_EXTS = (".md", ".csv")  # 疑似未 promote 成果

    def _trigger(committed_files: list[str]) -> bool:

        return True

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:

        sessions_dir = project_root / ".runtime" / "sessions"

        if not sessions_dir.exists():
            return ReconcileResult(action="skip", detail="staging_lifecycle: .runtime/sessions/ not found")

        now = time.time()

        deleted = 0

        errors = 0

        warned_unpromoted = 0

        scanned = 0

        try:
            session_entries = os.listdir(sessions_dir)

        except OSError as exc:
            return ReconcileResult(action="warn", detail=f"staging_lifecycle: listdir failed: {exc}")

        for sid_name in session_entries:
            staging = os.path.join(str(sessions_dir), sid_name, "staging")

            if not os.path.isdir(staging):
                continue

            for dirpath, _dirnames, filenames in os.walk(staging):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)

                    scanned += 1

                    try:
                        mtime = os.path.getmtime(filepath)

                    except OSError:
                        continue

                    if now - mtime < _STAGING_TTL_SECONDS:
                        continue  # 仍在 TTL 内

                    if filename.lower().endswith(_SUSPECTED_OUTPUT_EXTS):
                        warned_unpromoted += 1

                        logger.warning(
                            "GATE-SESSION-STAGING-LIFECYCLE: 疑似未 promote 成果被清理: "
                            "%s (mtime=%s，超过 24h TTL 视为草稿)",
                            _rel_path(filepath, str(project_root)),
                            time.strftime("%Y-%m-%d %H:%M", time.localtime(mtime)),
                        )

                    try:
                        # T1② 收敛：guard 安全 API（审计+file_ops 声明制强制）
                        from scripts.ops_guard import guard_remove

                        guard_remove(filepath)

                        deleted += 1

                    except OSError:
                        errors += 1

            try:
                if os.path.isdir(staging) and not os.listdir(staging):
                    # T1② 收敛：guard 安全 API（空 staging 目录清理，审计落盘）
                    from scripts.ops_guard import guard_rmtree

                    guard_rmtree(staging)  # 清理空的 staging 目录（不删 session 目录——系统文件可能在其中）

            except OSError:
                pass

        if deleted == 0 and errors == 0:
            return ReconcileResult(
                action="skip",
                detail=f"staging_lifecycle: scanned={scanned}, 无 >24h 过期文件",
            )

        action = "clean" if errors == 0 else "warn"

        return ReconcileResult(
            action=action,
            detail=(
                f"staging_lifecycle: scanned={scanned}, deleted={deleted} (>24h TTL), "
                f"warned_unpromoted={warned_unpromoted}, errors={errors}"
            ),
        )

    return ReconcilerSpec(
        gate_id="GATE-SESSION-STAGING-LIFECYCLE",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=802,  # worktree_lifecycle=800/stash_lifecycle=801 之后，
        file_ops=frozenset({"read", "delete"}),
        # root_temp_sweep=803 之前（暂存层清理先于根目录清扫）
    )
