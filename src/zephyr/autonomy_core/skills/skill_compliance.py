# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_compliance
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
MOD-INF-019: Agent Spec — Skill Compliance
Author: factory-agent
Version: 0.3.0

GDPR/SOC2/ISO27001 compliance checks

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: skill_compliance.py
# 层: 算法
# - id: A1
#   name_zh: ① SkillCompliance
#   name_en: SkillCompliance
#   intro: class SkillCompliance 源码 L61-L81
#   desc: 公共方法（定义序）: check_pii, check；源码 L61-L81
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: SkillCompliance
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import re
from typing import Any

PII_PATTERNS = [
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "email"),
    (r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b", "credit_card"),
]


class SkillCompliance:
    @classmethod
    def _check_pii(cls, content: str) -> dict[str, Any]:
        findings = []
        for pat, ptype in PII_PATTERNS:
            for m in re.finditer(pat, content):
                findings.append({"type": ptype, "value": m.group()[:30] + "..."})
        return {"pii_detected": len(findings) > 0, "findings": findings}

    @classmethod
    def check_pii(cls, content) -> dict[str, Any]:
        """公共接口：check_pii（Stage 4 公共化，委托到 cls._check_pii）。"""
        return cls._check_pii(content)

    @classmethod
    def check(cls, skill_id: str, content: str | None = None) -> dict[str, Any]:
        pii = cls._check_pii(content or "")
        violations = []
        if pii["pii_detected"]:
            violations.append({"policy": "GDPR", "check": "no_pii_storage", "detail": str(pii["findings"])})
        return {"skill_id": skill_id, "compliant": len(violations) == 0, "pii_check": pii, "violations": violations}
