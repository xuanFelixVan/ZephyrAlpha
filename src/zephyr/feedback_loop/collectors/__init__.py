# [DOMAIN] D_FEEDBACK_LOOP
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.collectors
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""feedback-loop.collectors — auto-generated package init.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包子模块导入请求
#   fields: import zephyr.feedback_loop.collectors 触发
#   code: L16-37 from . import ...
# 层: 算法
# - id: A1
#   name_zh: 子模块 eager 导入与门面再导出
#   name_en: subpackage_eager_reexport
#   intro: from . import 全部 20 个 collectors 子模块并以 __all__ 声明门面，无附加逻辑
#   code: __init__ 模块体
# 层: 输出
# - id: O1
#   name_zh: 包门面符号
#   name_en: package_facade_symbols
#   intro: __all__ 列出的 20 个子模块句柄
#   downstream: zephyr.feedback_loop 及外部包消费者
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> O1
"""

from . import (
    calendar_adapter,
    config_timeline,
    data_quality_validator,
    feedback_collector,
    financial_stratification,
    kb_provenance,
    knowledge_capture,
    knowledge_freshness,
    knowledge_injection,
    knowledge_packaging,
    known_unknown_registry,
    llm_cost_accounting,
    market_calendar,
    market_event_integrator,
    metrics_collector,
    notification_feedback,
    schema_evolution,
    schema_migration,
    temporal_event_store,
    token_finops,
)

__all__ = [
    "calendar_adapter",
    "config_timeline",
    "data_quality_validator",
    "feedback_collector",
    "financial_stratification",
    "kb_provenance",
    "knowledge_capture",
    "knowledge_freshness",
    "knowledge_injection",
    "knowledge_packaging",
    "known_unknown_registry",
    "llm_cost_accounting",
    "market_calendar",
    "market_event_integrator",
    "metrics_collector",
    "notification_feedback",
    "schema_evolution",
    "schema_migration",
    "temporal_event_store",
    "token_finops",
]
