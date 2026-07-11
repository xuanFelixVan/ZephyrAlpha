# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.vibe_security_verify
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] per-file四维测试不可跳过;安全验证必须通过
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_vibe_security_verify | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Vibe Security Verifier — v0.9.0 Vibe Coding安全验证器: AI生成代码安全基线检查。
"""

from __future__ import annotations

from typing import Final
SECURITY_CHECKS: Final[list] = ["no_eval", "no_exec", "no_os_system", "no_subprocess_shell", "no_pickle", "no_yaml_unsafe_load"]


class VibeSecurityVerify:
    def scan_code(self, code: str) -> list[str]:
        violations = []
        if "eval(" in code:
            violations.append("no_eval")
        if "exec(" in code:
            violations.append("no_exec")
        if "os.system(" in code:
            violations.append("no_os_system")
        if "shell=True" in code:
            violations.append("no_subprocess_shell")
        if "pickle." in code:
            violations.append("no_pickle")
        if "yaml.load(" in code:
            violations.append("no_yaml_unsafe_load")
        return violations

    def is_safe(self, code: str) -> bool:
        return len(self.scan_code(code)) == 0
