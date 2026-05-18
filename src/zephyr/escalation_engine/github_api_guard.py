# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.github_api_guard

# [INVARIANTS] PR/Issue清洗不可跳过;注入标记必须移除

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

GitHub API Guard — v0.9.0 Comment and Control防御: PR评论命令注入检测+限制。
"""
from __future__ import annotations

class GitHubAPIGuard:
    def __init__(self):
        self._allowed_commands={"run_tests","format_code","lint","build","deploy_staging"}
        self._audit:list[dict]=[]

    def validate_command(self, command:str, user:str)->tuple[bool,str]:
        if command not in self._allowed_commands:
            self._audit.append({"command":command,"user":user,"result":"denied"})
            return False,f"Command '{command}' not allowed"
        self._audit.append({"command":command,"user":user,"result":"allowed"})
        return True,"OK"

    def get_audit_log(self)->list[dict]:
        return self._audit
