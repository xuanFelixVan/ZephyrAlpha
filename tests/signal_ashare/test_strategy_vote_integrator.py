# [BLUEPRINT] MOD-SIG-134 | docs/03_modules/_domain_signal/strategy_vote_integrator/blueprint.md | §test
# [MODULE] tests.signal_ashare.test_strategy_vote_integrator
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.strategy_vote_integrator
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_strategy_vote_integrator.py
# [A_test] module_id: MOD-SIG-134 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [TTL] task_bound
"""MOD-SIG-134 多策略投票加权整合器单元测试（CAND-SIG-004）。

覆盖：一致通过 / 分歧否决 / ≥2/3 同向阈值边界 / 相关性惩罚降权（含翻转裁定）
/ 衰减自适应生效 / 弃权不计分母 / 权重过低剔除 / 非法输入 fail-closed /
participants 明细与 frozen 契约。全程内存构造，无 DB。
"""

from __future__ import annotations

import dataclasses

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.strategy_vote_integrator",
    reason="strategy_vote_integrator not importable",
)

from zephyr.signal_ashare.strategy_vote_integrator import (  # noqa: E402
    StrategyVoteSignal,
    StrategyVoteIntegratorError,
    VoteIntegratorConfig,
    integrate_strategy_votes,
)


def _s(sid: str, direction: int, weight: float, confidence: float = 1.0) -> StrategyVoteSignal:
    return StrategyVoteSignal(strategy_id=sid, direction=direction, weight=weight, confidence=confidence)


class TestConfig:
    def test_defaults_valid(self):
        cfg = VoteIntegratorConfig()
        assert cfg.correlation_threshold == 0.7
        assert cfg.min_agreement_ratio == pytest.approx(2.0 / 3.0)

    def test_invalid_threshold_raises(self):
        with pytest.raises(StrategyVoteIntegratorError):
            VoteIntegratorConfig(correlation_threshold=0.0)

    def test_invalid_agreement_ratio_raises(self):
        with pytest.raises(StrategyVoteIntegratorError):
            VoteIntegratorConfig(min_agreement_ratio=0.5)


class TestConsensus:
    def test_unanimous_long_approved(self):
        """一致通过：三席全 LONG → approved LONG，strength=1"""
        d = integrate_strategy_votes(
            "600000.SH",
            [_s("value", 1, 0.30), _s("momentum", 1, 0.25), _s("event", 1, 0.20)],
        )
        assert d.approved is True
        assert d.direction == "LONG"
        assert d.agreement_ratio == pytest.approx(1.0)
        assert d.strength == pytest.approx(1.0)
        assert d.confidence == pytest.approx(1.0)
        assert len(d.participants) == 3

    def test_unanimous_exit_is_exit_not_short(self):
        """A股无做空：一致看空 → EXIT 非 SHORT"""
        d = integrate_strategy_votes(
            "600000.SH",
            [_s("value", -1, 0.30), _s("momentum", -1, 0.25), _s("event", -1, 0.20)],
        )
        assert d.approved is True
        assert d.direction == "EXIT"
        assert d.strength == pytest.approx(1.0)

    def test_exactly_two_thirds_approved(self):
        """边界：同向占比恰 = 2/3 → 放行（≥ 阈值）"""
        d = integrate_strategy_votes("X", [_s("a", 1, 2.0), _s("b", -1, 1.0)])
        assert d.agreement_ratio == pytest.approx(2.0 / 3.0)
        assert d.approved is True
        assert d.direction == "LONG"

    def test_below_two_thirds_vetoed(self):
        """分歧否决：0.6 < 2/3 → NONE"""
        d = integrate_strategy_votes(
            "X",
            [_s("a", 1, 0.4), _s("b", -1, 0.4), _s("c", 1, 0.2)],
        )
        assert d.agreement_ratio == pytest.approx(0.6)
        assert d.approved is False
        assert d.direction == "NONE"
        assert "分歧否决" in d.reason

    def test_abstain_excluded_from_denominator(self):
        """弃权不计入分母：LONG 0.3 / EXIT 0.2 / 弃权 0.25 → 占比 0.6 → 否决"""
        d = integrate_strategy_votes(
            "X",
            [_s("a", 1, 0.3), _s("b", -1, 0.2), _s("c", 0, 0.25)],
        )
        assert d.agreement_ratio == pytest.approx(0.6)
        assert d.approved is False

    def test_empty_signals_none(self):
        d = integrate_strategy_votes("X", [])
        assert d.approved is False
        assert d.direction == "NONE"
        assert d.participants == ()


class TestCorrelationPenalty:
    def test_weaker_side_penalized(self):
        """相关性惩罚：|ρ|≥0.7 的策略对，权重较小侧 ×0.5"""
        d = integrate_strategy_votes(
            "X",
            [_s("a", 1, 0.30), _s("b", 1, 0.25), _s("c", 1, 0.20)],
            correlation_pairs={("a", "b"): 0.8},
        )
        detail = {p.strategy_id: p for p in d.participants}
        assert detail["b"].penalized is True
        assert detail["b"].adjusted_weight == pytest.approx(0.125)
        assert detail["a"].penalized is False
        assert d.approved is True

    def test_penalty_flips_decision(self):
        """惩罚降权翻转裁定：EXIT 多数派被降权 → 0.657 < 2/3 → 分歧否决"""
        signals = [_s("a", 1, 0.30), _s("b", -1, 0.40), _s("c", -1, 0.35)]
        raw = integrate_strategy_votes("X", signals)
        assert raw.approved is True
        assert raw.direction == "EXIT"
        penalized = integrate_strategy_votes("X", signals, correlation_pairs={("b", "c"): 0.9})
        assert penalized.approved is False
        assert penalized.direction == "NONE"

    def test_pair_key_order_irrelevant(self):
        """相关系数键序无关：{(b,a)} 与 {(a,b)} 等效"""
        signals = [_s("a", 1, 0.30), _s("b", 1, 0.25)]
        d1 = integrate_strategy_votes("X", signals, correlation_pairs={("a", "b"): 0.8})
        d2 = integrate_strategy_votes("X", signals, correlation_pairs={("b", "a"): 0.8})
        assert d1.participants == d2.participants

    def test_below_threshold_no_penalty(self):
        d = integrate_strategy_votes(
            "X",
            [_s("a", 1, 0.30), _s("b", 1, 0.25)],
            correlation_pairs={("a", "b"): 0.5},
        )
        assert all(p.penalized is False for p in d.participants)

    def test_penalty_applied_at_most_once_per_strategy(self):
        """a 与 b/c 均高相关：a 最弱只被罚一次（×0.5 不叠加 ×0.25）"""
        d = integrate_strategy_votes(
            "X",
            [_s("a", 1, 0.10), _s("b", 1, 0.30), _s("c", 1, 0.25)],
            correlation_pairs={("a", "b"): 0.9, ("a", "c"): 0.9},
        )
        detail = {p.strategy_id: p for p in d.participants}
        assert detail["a"].adjusted_weight == pytest.approx(0.05)

    def test_invalid_correlation_raises(self):
        with pytest.raises(StrategyVoteIntegratorError):
            integrate_strategy_votes(
                "X",
                [_s("a", 1, 0.3), _s("b", 1, 0.3)],
                correlation_pairs={("a", "b"): 1.5},
            )


class TestDecay:
    def test_half_life_halves_weight(self):
        """衰减生效：龄期 = 半衰期 → 权重 ×0.5"""
        d = integrate_strategy_votes(
            "X",
            [_s("a", 1, 0.40), _s("b", 1, 0.20)],
            signal_age_days={"a": 20.0},
        )
        detail = {p.strategy_id: p for p in d.participants}
        assert detail["a"].decay_factor == pytest.approx(0.5)
        assert detail["a"].adjusted_weight == pytest.approx(0.20)
        assert detail["b"].decay_factor == pytest.approx(1.0)

    def test_decay_flips_agreement(self):
        """衰减翻转：a 衰减后多数派易位"""
        signals = [_s("a", 1, 0.40), _s("b", -1, 0.20), _s("c", -1, 0.15)]
        fresh = integrate_strategy_votes("X", signals)
        assert fresh.direction == "NONE"  # long 0.4/0.75 = 0.533 < 2/3
        aged = integrate_strategy_votes("X", signals, signal_age_days={"b": 20.0, "c": 20.0})
        # b→0.10, c→0.075; long 0.4/0.575 = 0.696 ≥ 2/3 → LONG
        assert aged.approved is True
        assert aged.direction == "LONG"

    def test_decayed_below_min_weight_excluded(self):
        """衰减后权重 < 1e-6 → 视为退出投票"""
        d = integrate_strategy_votes(
            "X",
            [_s("a", 1, 1e-5), _s("b", 1, 0.2)],
            signal_age_days={"a": 20.0 * 30},
        )
        assert d.approved is True
        assert d.agreement_ratio == pytest.approx(1.0)

    def test_negative_age_raises(self):
        with pytest.raises(StrategyVoteIntegratorError):
            integrate_strategy_votes("X", [_s("a", 1, 0.3)], signal_age_days={"a": -1.0})


class TestValidation:
    def test_empty_symbol_raises(self):
        with pytest.raises(StrategyVoteIntegratorError):
            integrate_strategy_votes("  ", [_s("a", 1, 0.3)])

    def test_duplicate_strategy_raises(self):
        with pytest.raises(StrategyVoteIntegratorError):
            integrate_strategy_votes("X", [_s("a", 1, 0.3), _s("a", -1, 0.2)])

    def test_invalid_direction_raises(self):
        with pytest.raises(StrategyVoteIntegratorError):
            integrate_strategy_votes("X", [_s("a", 2, 0.3)])

    def test_negative_weight_raises(self):
        with pytest.raises(StrategyVoteIntegratorError):
            integrate_strategy_votes("X", [_s("a", 1, -0.1)])

    def test_confidence_out_of_range_raises(self):
        with pytest.raises(StrategyVoteIntegratorError):
            integrate_strategy_votes("X", [_s("a", 1, 0.3, confidence=1.1)])


class TestContract:
    def test_participants_sorted_and_frozen(self):
        d = integrate_strategy_votes("X", [_s("b", 1, 0.3), _s("a", 1, 0.2)])
        assert [p.strategy_id for p in d.participants] == ["a", "b"]
        with pytest.raises(dataclasses.FrozenInstanceError):
            d.participants[0].direction = -1

    def test_strength_net_of_confidence(self):
        """strength = |Σ w×dir×conf / Σw|：两 LONG，conf 1.0 与 0.5 → 0.75"""
        d = integrate_strategy_votes("X", [_s("a", 1, 0.3, 1.0), _s("b", 1, 0.3, 0.5)])
        assert d.strength == pytest.approx(0.75)
