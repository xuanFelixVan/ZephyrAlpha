# [BLUEPRINT] MOD-INF-021 | 03_modules/l01_infrastructure/rollback-system/blueprint.md | §
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
    - MOD-INF-007 (Gate Engine) — 门禁失败信号来源
    - MOD-MASTER-001 (集成契约 CT-RBK-GATE-001)
"""
from . import agent_cooldown
from . import auditor
from . import autonomy_dashboard
from . import budget_tracker
from . import checkpoint_gc
from . import commit_quality_gate
from . import complexity_budget
from . import confidence_quantifier
from . import cross_platform_shell
from . import down_migration_generator
from . import env_watcher
from . import external_merkle_proof
from . import fault_tolerance
from . import forensic
from . import forward_fix_runner
from . import fsm_verifier
from . import git_infra_snapshot
from . import model_drift_detector
from . import owner_absent
from . import paper_live_transition
from . import post_live_verification
from . import right_to_be_forgotten
from . import rollback_bootstrap
from . import rollback_budget
from . import rollback_context_restorer
from . import rollback_dashboard
from . import rollback_drill
from . import rollback_integration
from . import rollback_loop_detector
from . import rollback_simulator
from . import rollback_state_machine
from . import rollback_target_staleness
from . import runbook_generator
from . import s3_snapshot_lifecycle
from . import secret_rotation_aware
from . import semantic_rollback_tag
from . import semantic_similar_detector
from . import startup_shutdown
from . import startup_shutdown_cli
from . import submodule_sync
from . import temporal_context_adapter
from . import topology_change_log
from . import trading_kill_switch
from . import venv_sync
from . import vulnerability_rescanner
from . import warm_standby

__version__ = "0.10.0"
__blueprint__ = "MOD-INF-021"

from zephyr.rollback.rollback_executor import RollbackExecutor
from zephyr.rollback.rollback_verifier import RollbackVerifier
from zephyr.rollback.auto_rollback_trigger import AutoRollbackTrigger
from zephyr.rollback.kill_switch import KillSwitchManager

__all__ = [
    'AutoRollbackTrigger',
    'KillSwitchManager',
    'RollbackExecutor',
    'RollbackVerifier',
    '_manifest_',
    'agent_cooldown',
    'auditor',
    'auto_rollback_trigger',
    'autonomy_dashboard',
    'backtest_engine',
    'budget_tracker',
    'checkpoint_gc',
    'commit_quality_gate',
    'complexity_budget',
    'confidence_quantifier',
    'continuous_trust',
    'contract',
    'contracts',
    'credential_rotation_trigger',
    'cross_agent_conflict_detector',
    'cross_platform_shell',
    'down_migration_generator',
    'drift_fix',
    'env_watcher',
    'external_merkle_proof',
    'fault_tolerance',
    'forensic',
    'forward_fix_runner',
    'fsm_verifier',
    'git_infra_snapshot',
    'hallucination_guard',
    'intent_archiver',
    'kill_switch',
    'knowngoodstate_ledger',
    'llm_impact_analyzer',
    'model_drift_detector',
    'owner_absent',
    'paper_live_transition',
    'phase_check_registry',
    'phase_manager',
    'post_live_verification',
    'result_types',
    'right_to_be_forgotten',
    'rollback_abuse_detector',
    'rollback_audit_nexus',
    'rollback_bootstrap',
    'rollback_budget',
    'rollback_context_restorer',
    'rollback_dashboard',
    'rollback_drill',
    'rollback_executor',
    'rollback_integration',
    'rollback_lock',
    'rollback_loop_detector',
    'rollback_simulator',
    'rollback_state_machine',
    'rollback_target_staleness',
    'rollback_verifier',
    'rollback_wal',
    'runbook_generator',
    's3_snapshot_lifecycle',
    'sandbox_enforcer',
    'secret_rotation_aware',
    'semantic_rollback_tag',
    'semantic_similar_detector',
    'sqlite_dumper',
    'startup_shutdown',
    'startup_shutdown_cli',
    'submodule_sync',
    'temporal_context_adapter',
    'topology_change_log',
    'trading_kill_switch',
    'venv_sync',
    'vulnerability_rescanner',
    'warm_standby',
]