# [DOMAIN] D_FEEDBACK_LOOP
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.forensic
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""feedback-loop.forensic — auto-generated package init.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包子模块导入请求
#   fields: import zephyr.feedback_loop.forensic 触发
#   code: L16-35 from . import ...
# 层: 算法
# - id: A1
#   name_zh: 子模块 eager 导入与门面再导出
#   name_en: subpackage_eager_reexport
#   intro: from . import 全部 18 个 forensic 子模块并以 __all__ 声明门面，无附加逻辑
#   code: __init__ 模块体
# 层: 输出
# - id: O1
#   name_zh: 包门面符号
#   name_en: package_facade_symbols
#   intro: __all__ 列出的 18 个子模块句柄
#   downstream: zephyr.feedback_loop 及外部包消费者
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> O1
"""

from . import (
    architectural_sod,
    automated_rca_postmortem_generator,
    boot_integrity_attestation,
    crypto_bootstrap,
    deterministic_replay,
    external_verifier,
    fle_upgrade_safety_validator,
    guard_complexity_budget,
    guard_configuration_drift_monitor,
    interrupt_coherence_validator,
    knowledge_injection_pre_flight_verifier,
    point_in_time_reconstructor,
    self_modification_audit,
    serialization_format_tracker,
    state_migration_validator,
    sub_agent_collusion,
    toctou_guard,
    worm_write_integrity,
)

__all__ = [
    "architectural_sod",
    "automated_rca_postmortem_generator",
    "boot_integrity_attestation",
    "crypto_bootstrap",
    "deterministic_replay",
    "external_verifier",
    "fle_upgrade_safety_validator",
    "guard_complexity_budget",
    "guard_configuration_drift_monitor",
    "interrupt_coherence_validator",
    "knowledge_injection_pre_flight_verifier",
    "point_in_time_reconstructor",
    "self_modification_audit",
    "serialization_format_tracker",
    "state_migration_validator",
    "sub_agent_collusion",
    "toctou_guard",
    "worm_write_integrity",
]
