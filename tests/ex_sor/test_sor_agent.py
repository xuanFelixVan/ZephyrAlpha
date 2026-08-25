# [BLUEPRINT] MOD-XS-015 | docs/03_modules/_domain_ex_sor/sor_agent/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-XS-015 | layer=test | stability=volatile | safety=H | ai_autonomy=ai_modifiable
# [MODULE] tests.ex_sor.test_sor_agent
# [TESTS] src/zephyr/ex_sor/core/sor_agent.py
"""MOD-XS-015 单元测试：sor_agent 路由Agent（SOR）。

蓝图验收（B11-02491/CAND-SOR-001，A7 §1.4）：
Level 0 纯规则族卡 + 四维加权智能路由（流动性剔除）+ 拆单委托
（冰山/TWAP/量比映射 MOD-EX-014 降级口径）+ 滑点实际vs预估回写反馈循环 +
决策可回放 + 禁 LLM 门控。全部内存构造，不触网不触库无下单语义。
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

pytest.importorskip(
    "zephyr.ex_sor.core.sor_agent",
    reason="sor_agent not importable",
)

from zephyr.ex_sor.core.sor_agent import (  # noqa: E402
    AGENT_CARD,
    BrokerCandidate,
    SlippageFeedback,
    SorAgent,
    SorAgentError,
    SorDecision,
    SorRequest,
    SorRouteWeights,
)

_NOW = datetime(2026, 8, 25, 12, 0, 0, tzinfo=timezone.utc)


def _req(**kw) -> SorRequest:
    base = dict(
        symbol="600519.SH", side="BUY", quantity=1000, price=1700.0,
        split_algo="twap", slice_count=4, expected_slippage_bps=5.0,
    )
    base.update(kw)
    return SorRequest(**base)


def _cand(broker_id: str, latency_ms: float = 10.0, fill_rate: float = 0.95,
          cost_bps: float = 2.0, liquidity_score: float = 0.9) -> BrokerCandidate:
    return BrokerCandidate(
        broker_id=broker_id, latency_ms=latency_ms, fill_rate=fill_rate,
        cost_bps=cost_bps, liquidity_score=liquidity_score,
    )


def _fake_splitter(symbol, side, total_quantity, slice_count, algo, volume_profile):
    return {
        "symbol": symbol, "side": side, "total": total_quantity,
        "slices": slice_count, "algo": algo,
    }


class TestAgentCard:
    def test_card_level0_no_llm(self) -> None:
        assert AGENT_CARD["role"] == "sor"
        assert AGENT_CARD["autonomyLevel"] == "L0_rule_only"
        caps = {c["id"] for c in AGENT_CARD["capabilities"]}
        assert caps == {"smart_routing", "order_splitting"}
        boundaries = AGENT_CARD["autonomyBoundaries"]["immutable"]
        assert any("LLM" in b for b in boundaries)
        assert any("风控" in b for b in boundaries)  # SOR 不做风控（§6.1）


class TestRouting:
    def test_best_score_wins(self) -> None:
        agent = SorAgent(splitter_fn=_fake_splitter)
        slow = _cand("broker_slow", latency_ms=500.0)
        fast = _cand("broker_fast", latency_ms=5.0)
        dec = agent.decide(_req(), [slow, fast], now_utc=_NOW)
        assert dec.broker_id == "broker_fast"
        assert dec.score > 0.0
        assert dec.split_plan["algo"] == "twap"

    def test_low_liquidity_filtered(self) -> None:
        agent = SorAgent(splitter_fn=_fake_splitter, min_liquidity=0.5)
        illiquid = _cand("broker_illiquid", liquidity_score=0.1, latency_ms=1.0)
        liquid = _cand("broker_liquid", liquidity_score=0.9, latency_ms=50.0)
        dec = agent.decide(_req(), [illiquid, liquid], now_utc=_NOW)
        assert dec.broker_id == "broker_liquid"  # 低流动性即便低延迟也被剔除

    def test_no_candidate_fail_closed(self) -> None:
        agent = SorAgent(splitter_fn=_fake_splitter)
        with pytest.raises(SorAgentError):
            agent.decide(_req(), [], now_utc=_NOW)
        with pytest.raises(SorAgentError):
            agent.decide(_req(), [_cand("b", liquidity_score=0.0)],
                         now_utc=_NOW)  # 全部低于 min_liquidity

    def test_invalid_weights_rejected(self) -> None:
        with pytest.raises(SorAgentError):
            SorRouteWeights(w_latency=0.5, w_fill_rate=0.5, w_cost=0.5,
                            w_liquidity=0.5)  # 和=2.0
        with pytest.raises(SorAgentError):
            SorRouteWeights(w_latency=-0.5, w_fill_rate=0.5, w_cost=0.5,
                            w_liquidity=0.5)

    def test_invalid_request_fail_closed(self) -> None:
        agent = SorAgent(splitter_fn=_fake_splitter)
        with pytest.raises(SorAgentError):
            agent.decide(_req(quantity=0), [_cand("b")], now_utc=_NOW)
        with pytest.raises(SorAgentError):
            agent.decide(_req(price=-1.0), [_cand("b")], now_utc=_NOW)
        with pytest.raises(SorAgentError):
            agent.decide(_req(slice_count=0), [_cand("b")], now_utc=_NOW)


class TestSplitDelegation:
    def test_algo_mapping_iceberg_and_volume_ratio(self) -> None:
        seen: list[str] = []

        def spy_splitter(symbol, side, total_quantity, slice_count, algo, volume_profile):
            seen.append(algo)
            return {"algo": algo}

        agent = SorAgent(splitter_fn=spy_splitter)
        agent.decide(_req(split_algo="iceberg"), [_cand("b")], now_utc=_NOW)
        agent.decide(_req(split_algo="volume_ratio",
                          volume_profile=(1.0, 2.0, 3.0, 4.0)),
                     [_cand("b")], now_utc=_NOW)
        # 冰山→TWAP 等量少片（降级口径）；量比→VWAP 量能权重
        assert seen == ["twap", "vwap"]

    def test_unknown_split_algo_fail_closed(self) -> None:
        agent = SorAgent(splitter_fn=_fake_splitter)
        with pytest.raises(SorAgentError):
            agent.decide(_req(split_algo="sniper"), [_cand("b")], now_utc=_NOW)

    def test_splitter_error_wrapped(self) -> None:
        def bad_splitter(*a, **k):
            raise ValueError("板手不合法")

        agent = SorAgent(splitter_fn=bad_splitter)
        with pytest.raises(SorAgentError, match="拆单"):
            agent.decide(_req(), [_cand("b")], now_utc=_NOW)


class TestReplayAndFeedback:
    def test_replay_log_monotonic(self) -> None:
        agent = SorAgent(splitter_fn=_fake_splitter)
        d1 = agent.decide(_req(), [_cand("b1")], now_utc=_NOW)
        d2 = agent.decide(_req(), [_cand("b2")], now_utc=_NOW)
        log = agent.replay_log()
        assert len(log) == 2
        assert d1.replay_id != d2.replay_id
        assert log[0].replay_id == d1.replay_id and log[1].replay_id == d2.replay_id

    def test_feedback_pairs_expected_and_updates_bias(self) -> None:
        feedbacks: list[SlippageFeedback] = []
        agent = SorAgent(
            splitter_fn=_fake_splitter,
            feedback_sink=lambda fb: feedbacks.append(fb),
        )
        dec = agent.decide(_req(expected_slippage_bps=5.0), [_cand("b1")], now_utc=_NOW)
        fb = agent.record_fill_feedback(dec.replay_id, actual_slippage_bps=9.0)
        assert fb.expected_bps == 5.0
        assert fb.actual_bps == 9.0
        assert fb.bias_bps == pytest.approx(4.0)
        assert agent.broker_bias("b1") == pytest.approx(4.0)
        assert len(feedbacks) == 1

    def test_feedback_unknown_replay_id_fail_closed(self) -> None:
        agent = SorAgent(splitter_fn=_fake_splitter)
        with pytest.raises(SorAgentError):
            agent.record_fill_feedback("SOR-999999", actual_slippage_bps=1.0)

    def test_bias_mean_over_samples(self) -> None:
        agent = SorAgent(splitter_fn=_fake_splitter)
        d1 = agent.decide(_req(), [_cand("b1")], now_utc=_NOW)
        d2 = agent.decide(_req(), [_cand("b1")], now_utc=_NOW)
        agent.record_fill_feedback(d1.replay_id, actual_slippage_bps=7.0)  # bias +2
        agent.record_fill_feedback(d2.replay_id, actual_slippage_bps=9.0)  # bias +4
        assert agent.broker_bias("b1") == pytest.approx(3.0)
        assert agent.broker_bias("unknown") == pytest.approx(0.0)


class TestNoLlmGate:
    def test_llm_callable_rejected(self) -> None:
        import zephyr.intelligence.llm_agent_router as llm_mod

        def llm_splitter(symbol, side, total_quantity, slice_count, algo, volume_profile):
            return {}

        llm_splitter.__module__ = llm_mod.__name__  # 模拟来自 LLM 域的回调
        with pytest.raises(SorAgentError, match="LLM|llm|纯规则"):
            SorAgent(splitter_fn=llm_splitter)

    def test_llm_feedback_sink_rejected(self) -> None:
        def sink(fb):
            pass

        sink.__module__ = "zephyr.intelligence.some_llm_piece"
        with pytest.raises(SorAgentError):
            SorAgent(splitter_fn=_fake_splitter, feedback_sink=sink)
