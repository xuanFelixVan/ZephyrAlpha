# [DOMAIN] D_FEEDBACK_LOOP
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.evolution
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""feedback-loop.evolution — auto-generated package init.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包子模块导入请求
#   fields: import zephyr.feedback_loop.evolution 触发
#   code: L16-36 from . import ...
# 层: 算法
# - id: A1
#   name_zh: 子模块 eager 导入与门面再导出
#   name_en: subpackage_eager_reexport
#   intro: from . import 全部 19 个 evolution 子模块并以 __all__ 声明门面，无附加逻辑
#   code: __init__ 模块体
# 层: 输出
# - id: O1
#   name_zh: 包门面符号
#   name_en: package_facade_symbols
#   intro: __all__ 列出的 19 个子模块句柄
#   downstream: zephyr.feedback_loop 及外部包消费者
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> O1
"""

from . import (
    auto_reward,
    conformal_prediction,
    cross_gen_validation,
    dynamic_threshold,
    ewc_kb_review,
    failure_replay,
    graduated_activation_protocol,
    hypernetwork,
    knowledge_distillation,
    online_feature_importance,
    prompt_factory_governance,
    prompt_optimization_regression_detector,
    prompt_self_optimization_loop,
    self_modification_rate_limiter,
    self_reflection,
    self_upgrade_canary,
    semantic_intent_preservation_guard,
    teacher_transfer,
    training_data_gov,
)

__all__ = [
    "auto_reward",
    "conformal_prediction",
    "cross_gen_validation",
    "dynamic_threshold",
    "ewc_kb_review",
    "failure_replay",
    "graduated_activation_protocol",
    "hypernetwork",
    "knowledge_distillation",
    "online_feature_importance",
    "prompt_factory_governance",
    "prompt_optimization_regression_detector",
    "prompt_self_optimization_loop",
    "self_modification_rate_limiter",
    "self_reflection",
    "self_upgrade_canary",
    "semantic_intent_preservation_guard",
    "teacher_transfer",
    "training_data_gov",
]
