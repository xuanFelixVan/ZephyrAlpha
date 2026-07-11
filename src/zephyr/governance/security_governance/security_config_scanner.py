# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.security_config_scanner
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 安全配置扫描不可跳过;数据库/云/API配置必须检查
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_security_config_scanner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Security Config Scanner — v0.13.0 缺失安全配置扫描器。
"""

from __future__ import annotations

from typing import Final
REQUIRED_CONFIGS: Final[dict] = {"limits.yaml": "resource_limits", "cors.yaml": "cors_whitelist", "secrets.yaml": "api_keys"}


class SecurityConfigScanner:
    def scan(self, existing_files: list[str]) -> dict:
        missing = {}
        for req_file, desc in REQUIRED_CONFIGS.items():
            if not any(req_file in f for f in existing_files):
                missing[req_file] = desc
        return {"missing_count": len(missing), "missing": missing, "complete": len(missing) == 0}
