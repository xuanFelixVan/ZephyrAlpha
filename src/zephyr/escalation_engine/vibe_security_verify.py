# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.vibe_security_verify

# [INVARIANTS] per-file四维测试不可跳过;安全验证必须通过

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Vibe Security Verifier — v0.9.0 Vibe Coding安全验证器: AI生成代码安全基线检查。
"""
from __future__ import annotations

SECURITY_CHECKS=["no_eval","no_exec","no_os_system","no_subprocess_shell","no_pickle","no_yaml_unsafe_load"]

class VibeSecurityVerify:
    def scan_code(self,code:str)->list[str]:
        violations=[]
        if "eval(" in code:violations.append("no_eval")
        if "exec(" in code:violations.append("no_exec")
        if "os.system(" in code:violations.append("no_os_system")
        if "shell=True" in code:violations.append("no_subprocess_shell")
        if "pickle." in code:violations.append("no_pickle")
        if "yaml.load(" in code:violations.append("no_yaml_unsafe_load")
        return violations

    def is_safe(self,code:str)->bool:
        return len(self.scan_code(code))==0
