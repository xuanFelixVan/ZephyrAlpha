# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.github_api_guard
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] PR/Issue清洗不可跳过;注入标记必须移除
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
GitHub API Guard — v0.9.0 Comment and Control防御: PR评论命令注入检测+限制。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: github_api_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① GitHubAPIGuard
#   name_en: GitHubAPIGuard
#   intro: class GitHubAPIGuard 源码 L51-L75
#   desc: 公共方法（定义序）: allowed_commands, validate_command, get_audit_log；源码 L51-L75
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: GitHubAPIGuard
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class GitHubAPIGuard:
    def __init__(self):
        self._allowed_commands = {"run_tests", "format_code", "lint", "build", "deploy_staging"}
        self._audit: list[dict] = []

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def allowed_commands(self):
        """只读：allowed_commands（Stage 4 公共化）。"""
        return self._allowed_commands

    @allowed_commands.setter
    def allowed_commands(self, value):
        """写入：allowed_commands（Stage 4 公共化）。"""
        self._allowed_commands = value

    def validate_command(self, command: str, user: str) -> tuple[bool, str]:
        if command not in self._allowed_commands:
            self._audit.append({"command": command, "user": user, "result": "denied"})
            return False, f"Command '{command}' not allowed"
        self._audit.append({"command": command, "user": user, "result": "allowed"})
        return True, "OK"

    def get_audit_log(self) -> list[dict]:
        return self._audit
