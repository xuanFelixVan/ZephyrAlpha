# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.vibe_coding_quality_gate
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
VibeCodingQualityGate — 代码质量门禁（stub, tests 待实装后补全实现）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: vibe_coding_quality_gate.py
# 层: 算法
# - id: A1
#   name_zh: ① VibeCodingQualityGate
#   name_en: VibeCodingQualityGate
#   intro: class VibeCodingQualityGate 源码 L51-L72
#   desc: 公共方法（定义序）: validate；源码 L51-L72
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: VibeCodingQualityGate
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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
