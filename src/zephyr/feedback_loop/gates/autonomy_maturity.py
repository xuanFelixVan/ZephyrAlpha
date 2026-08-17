# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.autonomy_maturity
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

"""Autonomy Maturity Ladder — v0.7.0 R86

Blindspot: Autonomy levels hardcoded; no graduated trust model.
Risk: R86 — Premature autonomy causes irrecoverable automated damage.
"""

from dataclasses import dataclass


@dataclass
class AutonomyMaturity:
    # 主标尺（00_index 有界自治）映射：L0 OBSERVE=L0 人工；L1 NOTIFY/L2 SUGGEST=L1 建议（两亚档）；
    # L3 AUTO_MINOR=L2 低风险；L4 AUTO_FULL=保留不启用（=L3 中风险之上不开放）
    level: int = 0  # L0: OBSERVE, L1: NOTIFY, L2: SUGGEST, L3: AUTO_MINOR, L4: AUTO_FULL
