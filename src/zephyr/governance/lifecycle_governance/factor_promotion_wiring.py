# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.lifecycle_governance.factor_promotion_wiring
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.lifecycle_governance.msprt_promotion_channel; zephyr.factor.governance.lifecycle_state_machine（MOD-L02-013 因子 FSM，仅消费不改）
# [CONSUMERS] 调用方（因子灰度晋升评审：champion-challenger 并行期结束后应用裁决）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 仅终局裁决（PROMOTED/ELIMINATED）产生 FSM 副作用，留观（OBSERVING/PENDING）零副作用;前置态=grayscale（champion-challenger 并行灰度期），非灰度态由 MOD-INF-038 InvalidTransitionError fail-loud 上抛不静默跳过;FSM 转换拓扑唯一真源=MOD-L02-013（本模块不新增转换边）
# [MODIFY-GUARD] 61_lifecycle_multi_ai.md §3.3 纪律 1
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidTransitionError(因子 FSM 非 grayscale 态时由 MOD-INF-038 契约上抛)
# [TESTS] tests/governance/lifecycle/test_factor_promotion_wiring.py
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_GOVERNANCE — mSPRT 晋升裁决 → 因子生命周期 FSM 消费方接线（61 号 §3.3 纪律 1）。

memo 指定的 champion-challenger 晋升场景落地：challenger 因子在 grayscale
（灰度并行期）与 champion 同台跑 mSPRT 序贯检验，通道终局裁决驱动 FSM：
  - PROMOTED → grayscale → production（challenger 晋升实盘）
  - ELIMINATED → grayscale → paper（challenger 回退纸面观察，流量切回 champion）
  - OBSERVING / PENDING → None（留观不动，FSM 零副作用）

载体裁定留痕：memo 原载体 MLflow alias 已由 51 号裁定卸载（src 零命中）——
因子侧以 MOD-L02-013 因子生命周期状态机为等价注册表状态机载体（结案报告
"注册表状态机等价物"路径），本接线即该载体的首个消费方。

依据: 61_lifecycle_multi_ai §3.3 纪律 1 + 结案报告（MLflow 退役后载体重裁定）
Version: 0.1.0
"""

from __future__ import annotations

import logging
from typing import Final

from zephyr.factor.governance.lifecycle_state_machine import GRAYSCALE, PAPER, PRODUCTION
from zephyr.governance.lifecycle_governance.msprt_promotion_channel import (
    PromotionState,
    PromotionVerdict,
)
from zephyr.shared.lifecycle.state_machine import InvalidTransitionError, StateMachine

logger = logging.getLogger(__name__)

#: 终局裁决 → 因子 FSM 目标态（转换合法性由 MOD-INF-038 校验，非法 fail-loud）
_TERMINAL_TARGET: Final[dict[PromotionState, str]] = {
    PromotionState.PROMOTED: PRODUCTION,  # challenger 晋升实盘
    PromotionState.ELIMINATED: PAPER,  # challenger 回退纸面观察
}


def apply_promotion_verdict_to_factor_fsm(verdict: PromotionVerdict, fsm: StateMachine[str]) -> str | None:
    """把 mSPRT 通道裁决应用到因子生命周期 FSM。

    Args:
        verdict: 通道裁决快照（仅终局态产生副作用）。
        fsm: challenger 因子的生命周期状态机实例（前置：须处 grayscale 并行灰度期）。

    Returns:
        新状态名（production/paper）；非终局裁决 → None（零副作用）。

    Raises:
        InvalidTransitionError: FSM 非 grayscale 态——前置守卫 fail-loud（拓扑上
            backtest→paper 等边合法但语义非晋升裁决落地，装配错误不静默跳过）。
    """
    target = _TERMINAL_TARGET.get(verdict.state)
    if target is None:
        return None  # 留观不动
    current = fsm.current_state
    if current != GRAYSCALE:
        raise InvalidTransitionError(fsm.fsm_id, current, target, allowed={GRAYSCALE})
    new_state = fsm.transition(
        target,
        context={
            "reason": "msprt_champion_challenger_verdict",
            "champion_id": verdict.champion_id,
            "challenger_id": verdict.challenger_id,
            "n": verdict.n,
            "m_value": verdict.m_value,
        },
    )
    logger.warning(
        "因子晋升裁决落地: challenger=%s state=%s → %s（n=%d, M=%.3f）",
        verdict.challenger_id,
        verdict.state.value,
        new_state,
        verdict.n,
        verdict.m_value,
    )
    return new_state


__all__: Final = [
    "apply_promotion_verdict_to_factor_fsm",
]
