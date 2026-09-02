# [TTL] permanent
# [TESTS] src/zephyr/pf_core/core/strategy_factory.py (MOD-PF-009)
"""MOD-PF-009 strategy_factory 单元测试（B1-00189 C-006 策略工厂）。"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zephyr.pf_core.core.strategy_factory import (
    DiscoveryChannel,
    StrategyFactory,
    StrategyFactoryError,
    StrategyRecord,
    StrategyRegistryEntry,
    StrategyStage,
)

NOW = datetime(2026, 8, 25, 12, 0, tzinfo=timezone.utc)


def _factory() -> StrategyFactory:
    return StrategyFactory(clock=lambda: NOW)


def _to_gate_review(f: StrategyFactory, sid: str) -> None:
    f.advance(sid, StrategyStage.HYPOTHESIS)
    f.advance(sid, StrategyStage.GENERATION)
    f.advance(sid, StrategyStage.VALIDATION)
    f.advance(sid, StrategyStage.GATE_REVIEW)


class TestHappyPath:
    def test_full_10_stage_lifecycle(self) -> None:
        f = _factory()
        rec = f.intake("alpha_x", DiscoveryChannel.GP, hypothesis="动量+价值")
        assert rec.stage is StrategyStage.DRAFT
        assert rec.channel is DiscoveryChannel.GP
        _to_gate_review(f, rec.strategy_id)
        rec = f.submit_gate_verdict(rec.strategy_id, passed=True, detail="三重门禁全过")
        assert rec.stage is StrategyStage.PHACKING_REVIEW
        rec = f.submit_phacking_metrics(rec.strategy_id, dsr=1.2, pbo=0.3)
        assert rec.stage is StrategyStage.HUMAN_ADJUDICATION
        rec = f.human_adjudicate(rec.strategy_id, approved=True, approved_by="owner")
        assert rec.stage is StrategyStage.REGISTRATION
        entry = f.register(rec.strategy_id)
        assert isinstance(entry, StrategyRegistryEntry)
        assert entry.status == "candidate"  # 恒 candidate，严禁全自动上线
        rec = f.advance(rec.strategy_id, StrategyStage.MONITORING)
        rec = f.retire(rec.strategy_id, reason="衰减退役")
        assert rec.stage is StrategyStage.RETIREMENT

    def test_all_four_channels(self) -> None:
        f = _factory()
        for ch in (DiscoveryChannel.GP, DiscoveryChannel.SR, DiscoveryChannel.LLM, DiscoveryChannel.FACTOR_MAD):
            rec = f.intake(f"s_{ch.value}", ch)
            assert rec.channel is ch

    def test_discovery_hook_only_produces_draft(self) -> None:
        f = _factory()
        hook_calls: list[str] = []

        def hook(name: str) -> StrategyRecord:
            hook_calls.append(name)
            return f.intake(name, DiscoveryChannel.LLM)

        f.register_discovery_hook(DiscoveryChannel.LLM, hook)
        rec = f.discover(DiscoveryChannel.LLM, "llm_alpha")
        assert rec.stage is StrategyStage.DRAFT
        assert hook_calls == ["llm_alpha"]

    def test_list_strategies_filter(self) -> None:
        f = _factory()
        a = f.intake("a", DiscoveryChannel.GP)
        f.intake("b", DiscoveryChannel.SR)
        f.advance(a.strategy_id, StrategyStage.HYPOTHESIS)
        assert len(f.list_strategies()) == 2
        assert [r.strategy_id for r in f.list_strategies(stage=StrategyStage.DRAFT)] != [a.strategy_id]
        assert len(f.list_strategies(stage=StrategyStage.HYPOTHESIS)) == 1


class TestGates:
    def test_gate_failure_rejects(self) -> None:
        f = _factory()
        rec = f.intake("s1", DiscoveryChannel.GP)
        _to_gate_review(f, rec.strategy_id)
        rec = f.submit_gate_verdict(rec.strategy_id, passed=False, detail="CPCV未过")
        assert rec.stage is StrategyStage.REJECTED

    def test_phacking_failure_rejects(self) -> None:
        f = _factory()
        rec = f.intake("s1", DiscoveryChannel.GP)
        _to_gate_review(f, rec.strategy_id)
        f.submit_gate_verdict(rec.strategy_id, passed=True)
        rec = f.submit_phacking_metrics(rec.strategy_id, dsr=-0.1, pbo=0.2)
        assert rec.stage is StrategyStage.REJECTED
        rec2 = f.intake("s2", DiscoveryChannel.SR)
        _to_gate_review(f, rec2.strategy_id)
        f.submit_gate_verdict(rec2.strategy_id, passed=True)
        rec2 = f.submit_phacking_metrics(rec2.strategy_id, dsr=0.5, pbo=0.9)
        assert rec2.stage is StrategyStage.REJECTED

    def test_human_rejection(self) -> None:
        f = _factory()
        rec = f.intake("s1", DiscoveryChannel.GP)
        _to_gate_review(f, rec.strategy_id)
        f.submit_gate_verdict(rec.strategy_id, passed=True)
        f.submit_phacking_metrics(rec.strategy_id, dsr=1.0, pbo=0.2)
        rec = f.human_adjudicate(rec.strategy_id, approved=False, approved_by="owner", note="逻辑不通")
        assert rec.stage is StrategyStage.REJECTED

    def test_no_auto_approve_path(self) -> None:
        f = _factory()
        rec = f.intake("s1", DiscoveryChannel.GP)
        _to_gate_review(f, rec.strategy_id)
        f.submit_gate_verdict(rec.strategy_id, passed=True)
        f.submit_phacking_metrics(rec.strategy_id, dsr=1.0, pbo=0.2)
        with pytest.raises(StrategyFactoryError):
            f.human_adjudicate(rec.strategy_id, approved=True, approved_by="")
        with pytest.raises(StrategyFactoryError):
            f.human_adjudicate(rec.strategy_id, approved=True, approved_by="  ")


class TestFailClosed:
    def test_empty_name_rejected(self) -> None:
        f = _factory()
        with pytest.raises(StrategyFactoryError):
            f.intake("", DiscoveryChannel.GP)

    def test_illegal_transition(self) -> None:
        f = _factory()
        rec = f.intake("s1", DiscoveryChannel.GP)
        with pytest.raises(StrategyFactoryError):
            f.advance(rec.strategy_id, StrategyStage.REGISTRATION)
        with pytest.raises(StrategyFactoryError):
            f.submit_gate_verdict(rec.strategy_id, passed=True)
        with pytest.raises(StrategyFactoryError):
            f.submit_phacking_metrics(rec.strategy_id, dsr=1.0, pbo=0.1)
        with pytest.raises(StrategyFactoryError):
            f.register(rec.strategy_id)

    def test_rejected_is_terminal(self) -> None:
        f = _factory()
        rec = f.intake("s1", DiscoveryChannel.GP)
        _to_gate_review(f, rec.strategy_id)
        f.submit_gate_verdict(rec.strategy_id, passed=False)
        with pytest.raises(StrategyFactoryError):
            f.advance(rec.strategy_id, StrategyStage.MONITORING)

    def test_retirement_is_terminal(self) -> None:
        f = _factory()
        rec = f.intake("s1", DiscoveryChannel.GP)
        f.retire(rec.strategy_id, reason="early kill")
        with pytest.raises(StrategyFactoryError):
            f.advance(rec.strategy_id, StrategyStage.HYPOTHESIS)

    def test_unknown_id(self) -> None:
        f = _factory()
        with pytest.raises(StrategyFactoryError):
            f.advance("ghost", StrategyStage.HYPOTHESIS)
        with pytest.raises(StrategyFactoryError):
            f.get("ghost")

    def test_non_finite_phacking_metrics(self) -> None:
        f = _factory()
        rec = f.intake("s1", DiscoveryChannel.GP)
        _to_gate_review(f, rec.strategy_id)
        f.submit_gate_verdict(rec.strategy_id, passed=True)
        with pytest.raises(StrategyFactoryError):
            f.submit_phacking_metrics(rec.strategy_id, dsr=float("nan"), pbo=0.1)

    def test_record_frozen_and_history(self) -> None:
        f = _factory()
        rec = f.intake("s1", DiscoveryChannel.GP)
        rec = f.advance(rec.strategy_id, StrategyStage.HYPOTHESIS, note="假设成立")
        assert len(rec.history) == 2
        assert rec.history[-1].to_stage is StrategyStage.HYPOTHESIS
        with pytest.raises(AttributeError):
            rec.stage = StrategyStage.REJECTED  # type: ignore[misc]
