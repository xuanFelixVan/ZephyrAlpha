# [A_module] module_id=MOD-INF-rollback | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [TTL] permanent
"""


MOD-INF-021 Rollback System — ZephyrAlpha 回滚/撤销基础设施。

模块定位 (blueprint §1):
    本模块提供 Git-native + SQLite Dump 双轨 Checkpoint 机制，实现四级回滚操作
    (full_revert / partial_revert / discard / hard_reset) 以及 Forward-Fix 替代决策路径。

    核心能力:
        - 双轨 Checkpoint (git commit + SQLite JSONL dump)
        - 自动回滚触发器 (基于 auto_guard 后验信号三分类)
        - 回滚验证器 (G0 门禁 + DB 一致性自愈)
        - 回滚状态机 (步骤级追踪 + 部分失败恢复)
        - Forward-Fix 决策器 (优先 fix 而非 revert)
        - 三级 Kill Switch (L1 Session / L2 Skill / L3 Global)
        - 回滚演练调度器 (每周 DiRT drill + 混沌注入)

代码落位:
    src/zephyr/rollback/

版本: 0.10.0 (blueprint MOD-INF-021)

关联蓝图:
    - MOD-INF-020 (Drift Detector) — 失败信号来源
    - MOD-GATE_ENGINE (Gate Engine) — 门禁失败信号来源
    - MOD-MASTER_BLUEPRINT (集成契约 CT-RBK-GATE-001)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包导入请求（import zephyr.infrastructure.rollback）
#   fields: 无参数，触发包级急切导入与再导出
#   code: rollback/__init__.py L35
# 层: 算法
# - id: A1
#   name_zh: ① 子模块急切导入聚合
#   name_en: eager submodule imports
#   intro: 急切导入 35 个回滚子模块，deprecated 三模块已移出急切导入保证零副作用
#   desc: L35-69：agent_cooldown/auditor/.../vulnerability_rescanner；S4-A 移除 cross_platform_shell/venv_sync/warm_standby
#   inputs: I1
#   outputs: 子模块命名空间
# - id: A2
#   name_zh: ② 核心 API 再导出
#   name_en: __all__ 公共入口
#   intro: 再导出 6 个核心类 + concurrency_guard 3 个冲突检测函数，version 0.10.0
#   desc: L74-84：AutoRollbackTrigger/KillSwitchManager/RollbackBootIntegration/RollbackExecutor/RollbackVerifier/BootResult + check_rollback_conflict 等
#   inputs: A1
#   outputs: 回滚基础设施公共 API
# 层: 输出
# - id: O1
#   name_zh: 回滚基础设施公共入口
#   name_en: rollback package public API
#   intro: 双轨 Checkpoint/四级回滚/Forward-Fix/Kill Switch 等能力的统一入口（blueprint MOD-INF-021）
#   downstream: trading.boot_hooks（RollbackBootIntegration）；feedback_loop.scheduler_act 与 integration.mcp.governance_server（RollbackExecutor）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

# S4-A（2026-07-17）：模块导入零副作用——急切导入不再包含标为 deprecated 的子模块。
# 已从急切导入移除：cross_platform_shell / venv_sync / warm_standby（三者均标注
# deprecated，消费者仅各自的测试，且测试直接从子模块路径导入，不依赖
# 包级再导出）。需要时仍可 `from zephyr.infrastructure.rollback.<name> import ...`。
from . import (
    agent_cooldown,
    auditor,
    budget_tracker,
    checkpoint_gc,
    commit_quality_gate,
    complexity_budget,
    drift_fix,
    env_watcher,
    external_merkle_proof,
    forensic,
    forward_fix_runner,
    git_infra_snapshot,
    right_to_be_forgotten,
    rollback_boot_integration,
    rollback_bootstrap,
    rollback_budget,
    rollback_context_restorer,
    rollback_dashboard,
    rollback_drill,
    rollback_integration,
    rollback_loop_detector,
    rollback_simulator,
    rollback_state_machine,
    rollback_target_staleness,
    runbook_generator,
    s3_snapshot_lifecycle,
    secret_rotation_aware,
    semantic_rollback_tag,
    semantic_similar_detector,
    submodule_sync,
    temporal_context_adapter,
    topology_change_log,
    vulnerability_rescanner,
)

__version__ = "0.10.0"
__blueprint__ = "MOD-INF-021"

from zephyr.infrastructure.rollback.auto_rollback_trigger import AutoRollbackTrigger
from zephyr.infrastructure.rollback.kill_switch import KillSwitchManager
from zephyr.infrastructure.rollback.rollback_boot_integration import BootResult, RollbackBootIntegration
from zephyr.infrastructure.rollback.rollback_executor import RollbackExecutor
from zephyr.infrastructure.rollback.rollback_verifier import RollbackVerifier
from zephyr.infrastructure.runtime.concurrency_guard import (
    ConcurrencyConflictError,
    check_rollback_conflict,
    classify_uncommitted_files,
    scan_active_locks,
)

__all__ = [
    "AutoRollbackTrigger",
    "BootResult",
    "KillSwitchManager",
    "RollbackBootIntegration",
    "RollbackExecutor",
    "RollbackVerifier",
    "_manifest_",
    "agent_cooldown",
    "auditor",
    "auto_rollback_trigger",
    "budget_tracker",
    "checkpoint_gc",
    "commit_quality_gate",
    "complexity_budget",
    "contract",
    "contracts",
    "credential_rotation_trigger",
    "drift_fix",
    "env_watcher",
    "external_merkle_proof",
    "forensic",
    "forward_fix_runner",
    "git_infra_snapshot",
    "hallucination_guard",
    "intent_archiver",
    "kill_switch",
    "knowngoodstate_ledger",
    "right_to_be_forgotten",
    "rollback_abuse_detector",
    "rollback_audit_nexus",
    "rollback_bootstrap",
    "rollback_budget",
    "rollback_context_restorer",
    "rollback_dashboard",
    "rollback_drill",
    "rollback_executor",
    "rollback_integration",
    "rollback_lock",
    "rollback_loop_detector",
    "rollback_simulator",
    "rollback_state_machine",
    "rollback_target_staleness",
    "rollback_verifier",
    "rollback_wal",
    "runbook_generator",
    "s3_snapshot_lifecycle",
    "secret_rotation_aware",
    "semantic_rollback_tag",
    "semantic_similar_detector",
    "sqlite_dumper",
    "submodule_sync",
    "temporal_context_adapter",
    "topology_change_log",
    "vulnerability_rescanner",
]
