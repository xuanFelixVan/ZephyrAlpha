# [A_test] module_id: MOD-PLAN-013_agents | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-013 | 待统筹登记 | 缺口总账 GAP-F-44 行
# [MODULE] tests.plan_engine.test_trading_analyst_agents
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""交易域多 Analyst Agent 五角色实例化（GAP-F-44，MOD-PLAN-013 扩展）施工验证测试。

覆盖：
- 五角色齐备校验：缺角色/重角色/非法角色/非法立场/置信度越界/论点数越界全拒；
- 聚合：多方论点归牛、空方论点归熊（NEUTRAL 两侧不入），按置信度降序截取 ≤3 条；
  一侧无论点 → 占位论点+notes 留痕；
- 编排复用：辩论 AGREE→EXECUTE；分歧→DOWNSIZE 半档；风控防守员高置信看空→VETO
  （SIT_OUT+red_flag）；低置信不否决；D3 撤单比硬规则在风控防守员中性时仍生效；
- 契约：frozen、to_dict JSON 可序列化。
辩论引擎 mock，零 LLM/DB。
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.plan_engine.trading_analyst_agents import (
    ANALYST_ROLES,
    ROLE_FUNDAMENTAL,
    ROLE_MEAN_REVERTER,
    ROLE_RISK_DEFENDER,
    ROLE_SENTIMENT_HUNTER,
    ROLE_TREND_FOLLOWER,
    STANCE_BEARISH,
    STANCE_BULLISH,
    STANCE_NEUTRAL,
    AnalystCouncilConfig,
    AnalystOpinion,
    run_analyst_council,
)
from zephyr.plan_engine.trading_debate import (
    DECISION_DOWNSIZE,
    DECISION_EXECUTE,
    DECISION_SIT_OUT,
    DebateContext,
)


class _MockEngine:
    def __init__(self, verdict: str = "AGREE") -> None:
        self._verdict = verdict

    def debate(self, role_a: str, text_a: str, role_b: str, text_b: str) -> str:
        return self._verdict


def _ctx() -> DebateContext:
    return DebateContext(trade_date="2026-08-21", scenario="FLAT_OPEN_REAL_UP", is_offensive=True)


def _opinion(role: str, stance: str, conviction: float = 0.8, points: tuple[str, ...] = ("论点一",)) -> AnalystOpinion:
    return AnalystOpinion(role=role, stance=stance, conviction=conviction, points=points)


def _council_opinions(**overrides: AnalystOpinion) -> list[AnalystOpinion]:
    base = {
        ROLE_TREND_FOLLOWER: _opinion(ROLE_TREND_FOLLOWER, STANCE_BULLISH, 0.9, ("趋势多头排列", "量能配合")),
        ROLE_MEAN_REVERTER: _opinion(ROLE_MEAN_REVERTER, STANCE_NEUTRAL, 0.5, ("偏离度一般",)),
        ROLE_FUNDAMENTAL: _opinion(ROLE_FUNDAMENTAL, STANCE_BULLISH, 0.7, ("业绩超预期",)),
        ROLE_SENTIMENT_HUNTER: _opinion(ROLE_SENTIMENT_HUNTER, STANCE_BULLISH, 0.6, ("情绪升温",)),
        ROLE_RISK_DEFENDER: _opinion(ROLE_RISK_DEFENDER, STANCE_NEUTRAL, 0.4, ("未见极端风险",)),
    }
    base.update(overrides)
    return list(base.values())


class TestOpinionValidation:
    def test_unknown_role_rejected(self) -> None:
        with pytest.raises(ValueError, match="role"):
            _opinion("macro_economist", STANCE_BULLISH)

    def test_unknown_stance_rejected(self) -> None:
        with pytest.raises(ValueError, match="stance"):
            _opinion(ROLE_TREND_FOLLOWER, "STRONG_BUY")

    def test_conviction_out_of_range_rejected(self) -> None:
        with pytest.raises(ValueError, match="conviction"):
            _opinion(ROLE_TREND_FOLLOWER, STANCE_BULLISH, 1.5)

    @pytest.mark.parametrize("n", [0, 4])
    def test_points_count_rejected(self, n: int) -> None:
        with pytest.raises(ValueError, match="points"):
            _opinion(ROLE_TREND_FOLLOWER, STANCE_BULLISH, 0.8, tuple(f"p{i}" for i in range(n)))

    def test_missing_role_rejected(self) -> None:
        ops = _council_opinions()
        ops = [o for o in ops if o.role != ROLE_FUNDAMENTAL]
        with pytest.raises(ValueError, match=ROLE_FUNDAMENTAL):
            run_analyst_council(_ctx(), ops, debate_engine=_MockEngine())

    def test_duplicate_role_rejected(self) -> None:
        ops = _council_opinions()
        ops.append(_opinion(ROLE_TREND_FOLLOWER, STANCE_BEARISH))
        with pytest.raises(ValueError, match="重复"):
            run_analyst_council(_ctx(), ops, debate_engine=_MockEngine())


class TestAggregationAndOrchestration:
    def test_agree_executes(self) -> None:
        res = run_analyst_council(_ctx(), _council_opinions(), debate_engine=_MockEngine("AGREE"))
        assert res.debate_result.final_outcome == DECISION_EXECUTE
        assert res.debate_result.final_scale == 1.0
        # 三看多角色 6 条论点截 3 条，置信度降序
        assert len(res.debate_result.bull.points) == 3
        assert res.debate_result.bull.points[0] == "趋势多头排列"
        assert res.bull_side == (ROLE_TREND_FOLLOWER, ROLE_FUNDAMENTAL, ROLE_SENTIMENT_HUNTER)
        assert res.bear_side == ()

    def test_disagreement_downsizes(self) -> None:
        bearish = _council_opinions(
            **{
                ROLE_TREND_FOLLOWER: _opinion(ROLE_TREND_FOLLOWER, STANCE_BEARISH, 0.9, ("趋势破位",)),
                ROLE_FUNDAMENTAL: _opinion(ROLE_FUNDAMENTAL, STANCE_BEARISH, 0.7, ("业绩下修",)),
            }
        )
        res = run_analyst_council(_ctx(), bearish, debate_engine=_MockEngine("OVERRIDE"))
        assert res.debate_result.final_outcome == DECISION_DOWNSIZE
        assert res.debate_result.final_scale == pytest.approx(0.8)

    def test_empty_bull_side_placeholder(self) -> None:
        all_bear = _council_opinions(
            **{
                ROLE_TREND_FOLLOWER: _opinion(ROLE_TREND_FOLLOWER, STANCE_BEARISH, 0.9, ("破位",)),
                ROLE_FUNDAMENTAL: _opinion(ROLE_FUNDAMENTAL, STANCE_BEARISH, 0.7, ("下修",)),
                ROLE_SENTIMENT_HUNTER: _opinion(ROLE_SENTIMENT_HUNTER, STANCE_BEARISH, 0.6, ("退潮",)),
            }
        )
        res = run_analyst_council(_ctx(), all_bear, debate_engine=_MockEngine("OVERRIDE"))
        assert res.bull_side == ()
        assert "无看多论点" in res.debate_result.bull.points[0]
        assert any("占位" in n for n in res.notes)

    def test_risk_defender_veto(self) -> None:
        ops = _council_opinions(
            **{ROLE_RISK_DEFENDER: _opinion(ROLE_RISK_DEFENDER, STANCE_BEARISH, 0.85, ("尾部风险积聚", "流动性枯竭"))}
        )
        res = run_analyst_council(_ctx(), ops, debate_engine=_MockEngine("AGREE"))
        assert res.debate_result.final_outcome == DECISION_SIT_OUT
        assert res.debate_result.red_flag is True
        assert any("风控防守员" in r for r in res.debate_result.risk.reasons)

    def test_risk_defender_low_conviction_no_veto(self) -> None:
        ops = _council_opinions(
            **{ROLE_RISK_DEFENDER: _opinion(ROLE_RISK_DEFENDER, STANCE_BEARISH, 0.5, ("略有担忧",))}
        )
        res = run_analyst_council(_ctx(), ops, debate_engine=_MockEngine("AGREE"))
        assert res.debate_result.final_outcome == DECISION_EXECUTE

    def test_d3_hard_rule_still_active(self) -> None:
        ctx = DebateContext(trade_date="2026-08-21", scenario="HIGH_OPEN_UP", is_offensive=True, fake_ratio=0.9)
        res = run_analyst_council(ctx, _council_opinions(), debate_engine=_MockEngine("AGREE"))
        assert res.debate_result.final_outcome == DECISION_SIT_OUT
        assert res.debate_result.red_flag is True
        assert any("fake_ratio" in r for r in res.debate_result.risk.reasons)


class TestContract:
    def test_to_dict_json_serializable(self) -> None:
        res = run_analyst_council(_ctx(), _council_opinions(), debate_engine=_MockEngine())
        text = json.dumps(res.to_dict(), ensure_ascii=False)
        assert "debate_result" in text

    def test_frozen(self) -> None:
        res = run_analyst_council(_ctx(), _council_opinions(), debate_engine=_MockEngine())
        with pytest.raises(dataclasses.FrozenInstanceError):
            res.bull_side = ()  # type: ignore[misc]

    def test_five_roles_constant(self) -> None:
        assert set(ANALYST_ROLES) == {
            ROLE_TREND_FOLLOWER,
            ROLE_MEAN_REVERTER,
            ROLE_FUNDAMENTAL,
            ROLE_SENTIMENT_HUNTER,
            ROLE_RISK_DEFENDER,
        }

    def test_bad_veto_conviction_config_rejected(self) -> None:
        with pytest.raises(ValueError, match="risk_veto_conviction"):
            AnalystCouncilConfig(risk_veto_conviction=1.5)
