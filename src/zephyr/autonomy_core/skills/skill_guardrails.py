# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_guardrails
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Guardrails
Author: factory-agent
Version: 0.3.0

Runtime guardrails: budget/mutation/output checks

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: skill_guardrails.py
# 层: 算法
# - id: A1
#   name_zh: ① SkillGuardrails
#   name_en: SkillGuardrails
#   intro: class SkillGuardrails 源码 L64-L112
#   desc: 公共方法（定义序）: active, violations, allowed, check_pre_execution, check_output；源码 L64-L112
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: SkillGuardrails
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Any, Final

DESTRUCTIVE: Final[set] = {
    "rm -rf": "critical",
    "DROP TABLE": "critical",
    "TRUNCATE": "high",
    "DELETE FROM": "high",
    "format c:": "critical",
    "rmdir /s": "high",
}


class SkillGuardrails:
    MIN_OUTPUT = 5

    def __init__(self):
        self._violations: list[dict[str, Any]] = []
        self._active = True

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def active(self):
        """只读：active（Stage 4 公共化）。"""
        return self._active

    @active.setter
    def active(self, value):
        """写入：active（Stage 4 公共化）。"""
        self._active = value

    @property
    def violations(self) -> list[dict[str, Any]]:
        """只读：violations（Stage 4 公共化）。"""
        return self._violations

    @violations.setter
    def violations(self, value):
        """写入：violations（Stage 4 公共化）。"""
        self._violations = value

    @property
    def allowed(self) -> bool:
        return self._active and len(self._violations) == 0

    def check_pre_execution(self, skill_id: str, operation: str, budget_remaining: int | None = None) -> dict[str, Any]:
        v = []
        if budget_remaining is not None and budget_remaining <= 0:
            v.append({"type": "budget_exhausted", "severity": "blocking"})
        op_upper = operation.upper()
        for pat, sev in DESTRUCTIVE.items():
            if pat.upper() in op_upper:
                v.append({"type": "destructive", "severity": sev, "detail": operation[:100]})
        self._violations.extend(v)
        return {"allowed": len(v) == 0, "skill_id": skill_id, "operation": operation[:200], "violations": v}

    def check_output(self, skill_id: str, output: str) -> dict[str, Any]:
        v = []
        if len(output.strip()) < self.MIN_OUTPUT:
            v.append({"type": "too_short", "severity": "warning"})
        self._violations.extend(v)
        return {"allowed": len(v) == 0, "skill_id": skill_id, "violations": v}
