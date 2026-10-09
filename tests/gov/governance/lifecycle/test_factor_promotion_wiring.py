# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.lifecycle.test_factor_promotion_wiring
# [DOMAIN] D_GOVERNANCE
# [A_module] module_id=MOD-TEST-GOV-FACTORWIRE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""因子晋升场景消费方接线单元测试（mSPRT 通道裁决 → 因子生命周期 FSM）。

覆盖:
  - PROMOTED → grayscale → production（challenger 因子晋升实盘，61 号 §3.3 纪律 1）
  - ELIMINATED → grayscale → paper（challenger 回退纸面观察，FSM 合法回退边）
  - OBSERVING / PENDING → None（留观不动，FSM 零副作用）
  - 前置态错位 fail-loud：非 grayscale 态晋升裁决 → InvalidTransitionError 上抛（不静默跳过）
"""

from __future__ import annotations

import pytest

from zephyr.factor.governance.lifecycle_state_machine import (
    BACKTEST,
    DEVELOPMENT,
    GRAYSCALE,
    PAPER,
    PRODUCTION,
    RESEARCH,
    create_factor_fsm,
)
from zephyr.governance.lifecycle_governance.factor_promotion_wiring import (
    apply_promotion_verdict_to_factor_fsm,
)
from zephyr.governance.lifecycle_governance.msprt_promotion_channel import (
    PromotionState,
    PromotionVerdict,
)
from zephyr.pf_core.core.msprt_champion_challenger import ChampionChallengerDecision
from zephyr.shared.lifecycle.state_machine import InvalidTransitionError


def _verdict(state: PromotionState, decision: ChampionChallengerDecision | None = None) -> PromotionVerdict:
    return PromotionVerdict(
        champion_id="factor_champion",
        challenger_id="factor_challenger",
        state=state,
        decision=decision,
        n=30,
        m_value=25.0,
        log_m=3.2,
    )


def _fsm_at_grayscale():
    """把因子 FSM 沿合法路径推进到 grayscale（champion-challenger 并行灰度期）。"""
    fsm = create_factor_fsm()
    for target in (DEVELOPMENT, BACKTEST, PAPER, GRAYSCALE):
        fsm.transition(target)
    return fsm


class TestPromotionWiring:
    def test_promoted_advances_to_production(self):
        fsm = _fsm_at_grayscale()
        new_state = apply_promotion_verdict_to_factor_fsm(
            _verdict(PromotionState.PROMOTED, ChampionChallengerDecision.PROMOTE_CHALLENGER), fsm
        )
        assert new_state == PRODUCTION
        assert fsm.current_state == PRODUCTION

    def test_eliminated_rolls_back_to_paper(self):
        """challenger 淘汰回退：灰度 → 纸面（流量切回 champion，因子退观察）。"""
        fsm = _fsm_at_grayscale()
        new_state = apply_promotion_verdict_to_factor_fsm(
            _verdict(PromotionState.ELIMINATED, ChampionChallengerDecision.ELIMINATE_CHALLENGER), fsm
        )
        assert new_state == PAPER
        assert fsm.current_state == PAPER

    @pytest.mark.parametrize(
        "state,decision",
        [
            (PromotionState.OBSERVING, ChampionChallengerDecision.RETAIN_CHAMPION),
            (PromotionState.PENDING, None),
        ],
    )
    def test_non_terminal_verdict_no_side_effect(self, state, decision):
        fsm = _fsm_at_grayscale()
        assert apply_promotion_verdict_to_factor_fsm(_verdict(state, decision), fsm) is None
        assert fsm.current_state == GRAYSCALE  # 留观不动

    def test_non_grayscale_fsm_fails_loud(self):
        """装配错误（因子未处灰度并行期）→ 非法转换异常上抛，不静默吞。"""
        fsm = create_factor_fsm()  # research 态
        with pytest.raises(InvalidTransitionError):
            apply_promotion_verdict_to_factor_fsm(
                _verdict(PromotionState.PROMOTED, ChampionChallengerDecision.PROMOTE_CHALLENGER), fsm
            )
        assert fsm.current_state == RESEARCH

    def test_backtest_state_eliminate_also_fails_loud(self):
        """拓扑陷阱：backtest→paper 是 FSM 合法边，但非灰度期的淘汰裁决不得借道落地。"""
        fsm = create_factor_fsm()
        for target in (DEVELOPMENT, BACKTEST):
            fsm.transition(target)
        with pytest.raises(InvalidTransitionError):
            apply_promotion_verdict_to_factor_fsm(
                _verdict(PromotionState.ELIMINATED, ChampionChallengerDecision.ELIMINATE_CHALLENGER), fsm
            )
        assert fsm.current_state == BACKTEST
