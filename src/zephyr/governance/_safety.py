# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [MODULE] zephyr.governance._safety
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] __all__列表不变; 公开API不变
# [MODIFY-GUARD] 新增导出须同步更新__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_escalation_engine_imports.py
# [A_module] module_id=MOD-RES__safety | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from zephyr.governance.self_test import HealthLevel, SelfTestReport, run_self_test

_SUBMODULES = [
    "api_response_sanitizer",
    "audit_write_failure_protector",
    "credential_guard",
    "formal_verifier",
    "ghost_scan",
    "git_hook_pre_scanner",
    "github_api_guard",
    "hooks_integrity_guard",
    "identity_verifier",
    "incident_response",
    "integrity_verifier",
    "memory_poison_guard",
    "process_isolator",
    "sbom_guard",
    "security_config_scanner",
    "self_validator",
    "vibe_security_verify",
    "vibe_verify_integration",
    "witness_isolation",
]

__all__ = [
    "DriftDetector",
    "HealthLevel",
    "MerkleAudit",
    "SelfTestReport",
    "run_self_test",
]
