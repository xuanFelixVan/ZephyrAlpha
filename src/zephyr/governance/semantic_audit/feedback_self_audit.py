# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §0.1
# [MODULE] zephyr.governance.semantic_audit.feedback_self_audit
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.feedback_self_audit
# [CONSUMERS] zephyr.governance.semantic_audit.__init__(lazy re-export)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] re-export shim; canonical implementation at zephyr.gov_audit.feedback_self_audit (MOD-INF-020); no own logic
# [MODIFY-GUARD] semantic_auditor/blueprint.md; semantic_auditor/__init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if gov_audit.feedback_self_audit unavailable
# [TESTS] tests/feedback/feedback_loop/test_feedback_self_audit.py; tests/semantic_auditor/test_semantic_auditor.py
# [A_module] module_id=MOD-INF-028 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
feedback_self_audit — re-export shim for zephyr.gov_audit.feedback_self_audit (MOD-INF-020 canonical).

治本（AI-AUDIT12 双真源收敛，2026-09-05）：本文件与 zephyr.gov_audit/feedback_self_audit.py
自 587b569942 起为同一功能的双份承载（反馈自审计；gov_audit 版为超集，另含
_detect_self_feedback_loops），违反真源唯一。收敛裁定：gov_audit 版（超集）为唯一
实现真源；本文件降级为 re-export shim（red_blue_validator 既有范式）。
蓝图 §0.1 本行标注"挂靠自 MOD-INF-020"，本收敛使物理事实与蓝图声明一致。

# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/semantic_audit/feedback_self_audit.yaml
"""

from zephyr.gov_audit.feedback_self_audit import (  # noqa: F401
    CircularDependencyResult,
    FeedbackNode,
    FeedbackSelfAuditor,
    SelfReinforcementResult,
)

__all__ = [
    "CircularDependencyResult",
    "FeedbackNode",
    "FeedbackSelfAuditor",
    "SelfReinforcementResult",
]
