# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.action_reversibility
# [DOMAIN] D_FBL_VERIFICATION
# [DEPENDENCIES] zephyr.feedback_loop.gates.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Action Reversibility — v0.15.0 R208

Blindspot: Some repairs irreversible; FLE executes without reversible-path verification.
Risk: R208 — "DELETE FROM production" executed; no undo possible because irreversibility un-checked.

Mitigation: Action reversibility gate—all destructive actions require verified rollback path.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 动作可逆性证据 参数组
#   fields: action（动作名）+ has_rollback（有无回滚路径）+ has_snapshot（有无快照）
#   code: classify(action, has_rollback, has_snapshot) L43
# - id: I2
#   name: 自治等级 整数
#   fields: autonomy_level（AI 自治级别，<3 视为低自治）
#   code: gate(autonomy_level) L50
# 层: 算法
# - id: A1
#   name_zh: ① 可逆性分类
#   name_en: ActionReversibility.classify
#   intro: 按有无快照和回滚路径把动作分成四档可逆性
#   desc: snapshot&rollback→FULLY_REVERSIBLE；仅其一→PARTIALLY_REVERSIBLE；都无→IRREVERSIBLE（UNKNOWN 枚举保留未用）
#   inputs: I1
#   outputs: Reversibility 枚举
# - id: A2
#   name_zh: ② 可逆性门禁
#   name_en: ActionReversibility.gate
#   intro: 不可逆动作在低自治级别下直接拦截并记黑名单
#   desc: IRREVERSIBLE 且 autonomy_level<3 → blocked_actions.append(action) 返回 False；其余放行 True
#   inputs: I2 A1
#   outputs: 放行 bool + blocked_actions 记录
# 层: 输出
# - id: O1
#   name_zh: 可逆性等级
#   name_en: Reversibility
#   intro: 动作的四档可逆性分类结果
#   downstream: 无下游/内部使用（feedback_loop gates 内部，[CONSUMERS] 头为空）
# - id: O2
#   name_zh: 门禁放行结果
#   name_en: gate result bool
#   intro: True 放行 / False 拦截（不可逆动作记入 blocked_actions）
#   downstream: 无下游/内部使用（FLE 修复执行前门禁，R208 缓解）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# A1 --> A2
# A1 --> O1
# A2 --> O2
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Reversibility(str, Enum):
    FULLY_REVERSIBLE = "FULLY_REVERSIBLE"
    PARTIALLY_REVERSIBLE = "PARTIALLY_REVERSIBLE"
    IRREVERSIBLE = "IRREVERSIBLE"
    UNKNOWN = "UNKNOWN"


@dataclass
class ActionReversibility:
    blocked_actions: list[str] = field(default_factory=list)

    def classify(self, action: str, has_rollback: bool, has_snapshot: bool) -> Reversibility:
        if has_snapshot and has_rollback:
            return Reversibility.FULLY_REVERSIBLE
        if has_snapshot or has_rollback:
            return Reversibility.PARTIALLY_REVERSIBLE
        return Reversibility.IRREVERSIBLE

    def gate(self, action: str, reversibility: Reversibility, autonomy_level: int) -> bool:
        if reversibility is Reversibility.IRREVERSIBLE and autonomy_level < 3:
            self.blocked_actions.append(action)
            return False
        return True
