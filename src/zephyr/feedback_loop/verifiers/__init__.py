# [DOMAIN] D_FEEDBACK_LOOP
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.verifiers
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""feedback-loop.verifiers — auto-generated package init.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包子模块导入请求
#   fields: import zephyr.feedback_loop.verifiers 触发
#   code: L16-40 from . import ...
# 层: 算法
# - id: A1
#   name_zh: 子模块 eager 导入与门面再导出
#   name_en: subpackage_eager_reexport
#   intro: from . import 全部 23 个 verifiers 子模块并以 __all__ 声明门面，无附加逻辑
#   code: __init__ 模块体
# 层: 输出
# - id: O1
#   name_zh: 包门面符号
#   name_en: package_facade_symbols
#   intro: __all__ 列出的 23 个子模块句柄
#   downstream: zephyr.feedback_loop 及外部包消费者
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> O1
"""

from . import (
    ab_test,
    action_explainability,
    ai_comment_veracity,
    attack_simulator,
    auto_rollback,
    build_reproducibility_verifier,
    canary_repair,
    cascading_rollback_analyzer,
    cross_blueprint_contract_drift,
    cross_module_integration,
    cross_session_knowledge_integrity,
    digital_twin_sandbox,
    dry_run_sandbox,
    federated_protocol,
    golden_test_external,
    no_llm_degradation,
    pre_flight_simulator,
    preventive_repair,
    rollback_integrity,
    sim2real_calibration,
    stochastic_diagnosis_verifier,
    toctou_revalidation,
    verification_engine,
)

__all__ = [
    "ab_test",
    "action_explainability",
    "ai_comment_veracity",
    "attack_simulator",
    "auto_rollback",
    "build_reproducibility_verifier",
    "canary_repair",
    "cascading_rollback_analyzer",
    "cross_blueprint_contract_drift",
    "cross_module_integration",
    "cross_session_knowledge_integrity",
    "digital_twin_sandbox",
    "dry_run_sandbox",
    "federated_protocol",
    "golden_test_external",
    "no_llm_degradation",
    "pre_flight_simulator",
    "preventive_repair",
    "rollback_integrity",
    "sim2real_calibration",
    "stochastic_diagnosis_verifier",
    "toctou_revalidation",
    "verification_engine",
]
