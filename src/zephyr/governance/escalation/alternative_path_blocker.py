# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.escalation.alternative_path_blocker
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 替代路径拦截不可绕过;bash pattern必须匹配
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Alternative Path Blocker — v0.13.0 替代工具路径拦截器。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: alternative_path_blocker.py
# 层: 算法
# - id: A1
#   name_zh: ① AlternativePathBlocker
#   name_en: AlternativePathBlocker
#   intro: class AlternativePathBlocker 源码 L55-L63
#   desc: 公共方法（定义序）: detect_alternative, block_if_detected；源码 L55-L63
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: AlternativePathBlocker
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from typing import Final

BLOCKED_ALTERNATIVES: Final[dict] = {"write_file": ["tee", "cat >", "dd of="], "execute": ["source", "."]}


class AlternativePathBlocker:
    def detect_alternative(self, primary_command: str, actual_command: str) -> bool:
        alternatives = BLOCKED_ALTERNATIVES.get(primary_command, [])
        return any(alt in actual_command.lower() for alt in alternatives)

    def block_if_detected(self, primary: str, actual: str) -> tuple[bool, str]:
        if self.detect_alternative(primary, actual):
            return False, f"Alternative path detected: {actual} instead of {primary}"
        return True, "OK"
