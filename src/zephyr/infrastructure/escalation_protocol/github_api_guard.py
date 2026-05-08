"""GitHub API Guard — v0.9.0 Comment and Control防御: PR评论命令注入检测+限制。"""
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
