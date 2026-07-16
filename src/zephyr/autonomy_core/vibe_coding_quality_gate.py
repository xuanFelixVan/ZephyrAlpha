# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.vibe_coding_quality_gate
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""VibeCodingQualityGate — 代码质量门禁（stub, tests 待实装后补全实现）"""
import ast
import re


class VibeCodingQualityGate:
    _SECURITY_PATTERNS = [
        re.compile(r"['\"](?:sk-|pk-|api_key|password|secret|token)[^'\"]*['\"]", re.IGNORECASE),
        re.compile(r"['\"][A-Za-z0-9]{32,}['\"]"),
    ]

    @classmethod
    def validate(cls, name: str, code: str) -> dict:
        checks: dict[str, bool] = {}
        try:
            ast.parse(code)
            checks["syntax_check"] = True
        except SyntaxError:
            checks["syntax_check"] = False
        security_ok = True
        for pattern in cls._SECURITY_PATTERNS:
            if pattern.search(code):
                security_ok = False
                break
        checks["security-scan"] = security_ok
        passed = all(checks.values())
        return {"passed": passed, "checks": checks}
