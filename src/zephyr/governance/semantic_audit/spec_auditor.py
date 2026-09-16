# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §0.1
# [MODULE] zephyr.governance.semantic_audit.spec_auditor
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.spec_auditor
# [CONSUMERS] zephyr.governance.semantic_audit.__init__(lazy re-export)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] re-export shim; canonical implementation at zephyr.gov_audit.spec_auditor (MOD-INF-020); record_agent_spec is duck-typed (works with autonomy_core.skill_rbac_registry.AgentCapability per G-CT-007)
# [MODIFY-GUARD] semantic_auditor/blueprint.md; semantic_auditor/__init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if gov_audit.spec_auditor unavailable
# [TESTS] tests/semantic_auditor/test_semantic_auditor.py
# [A_module] module_id=MOD-INF-028 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
spec_auditor — re-export shim for zephyr.gov_audit.spec_auditor (MOD-INF-020 canonical).

治本（AI-AUDIT12 双真源收敛，2026-09-05）：本文件与 zephyr.gov_audit/spec_auditor.py
的 record_agent_spec 函数体逐字相同（仅 AgentCapability 类型注解导入源不同：
agent_spec.registry vs autonomy_core.skill_rbac_registry）。函数为 duck-typed
（仅访问 agent_id/capabilities/claimed_capabilities/model_provider/version 属性），
对两类 capability 对象运行时行为完全一致。收敛裁定：gov_audit 版为唯一实现真源；
本文件降级为 re-export shim（red_blue_validator 既有范式），G-CT-007 对
skill_rbac_registry capability 对象的兼容性不变。
蓝图 §0.1 本行标注"挂靠自 MOD-INF-020"，本收敛使物理事实与蓝图声明一致。

# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/semantic_audit/spec_auditor.yaml
"""

from zephyr.gov_audit.spec_auditor import AgentCapability, record_agent_spec  # noqa: F401

__all__ = [
    "AgentCapability",
    "record_agent_spec",
]
