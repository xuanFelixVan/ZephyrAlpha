# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.config_scanner
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] AI配置注入扫描不可禁用;恶意配置必须检测
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_config_scanner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Config Scanner — v0.9.0 AI配置文件注入扫描器: 检测AI修改的配置+注入攻击。
"""

from __future__ import annotations


class ConfigScanner:
    def __init__(self):
        self._baseline: dict[str, str] = {}

    def set_baseline(self, filepath: str, content_hash: str):
        self._baseline[filepath] = content_hash

    def detect_modification(self, filepath: str, current_hash: str) -> bool:
        baseline = self._baseline.get(filepath)
        return baseline is not None and baseline != current_hash

    def check_injection(self, content: str) -> list[str]:
        suspicious = []
        if "{{" in content and "}}" in content:
            suspicious.append("template_injection")
        if "eval(" in content:
            suspicious.append("code_injection")
        return suspicious
