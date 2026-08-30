# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.persuasion_detector
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 心理说服检测不可禁用;Cialdini六原则必须覆盖
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Persuasion Detector — D-022-09 心理说服检测: 对抗语气+恳求+绕过指令。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: persuasion_detector.py
# 层: 算法
# - id: A1
#   name_zh: ① PersuasionDetector
#   name_en: PersuasionDetector
#   intro: class PersuasionDetector 源码 L65-L72
#   desc: 公共方法（定义序）: detect, score；源码 L65-L72
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: PersuasionDetector
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from typing import Final

SUSPICIOUS_PATTERNS: Final[list] = [
    "please",
    "urgent",
    "trust me",
    "you must",
    "override",
    "bypass",
    "ignore rules",
    "just this once",
    "don't escalate",
]


class PersuasionDetector:
    def detect(self, text: str) -> tuple[bool, list[str]]:
        found = [p for p in SUSPICIOUS_PATTERNS if p.lower() in text.lower()]
        return len(found) > 0, found

    def score(self, text: str) -> float:
        _, found = self.detect(text)
        return min(1.0, len(found) / len(SUSPICIOUS_PATTERNS))
