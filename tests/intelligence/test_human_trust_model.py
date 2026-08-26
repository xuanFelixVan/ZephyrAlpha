# [BLUEPRINT] MOD-INT-HUMAN-TRUST | docs/03_modules/_domain_intelligence/human_trust_model/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INT-HUMAN-TRUST | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.intelligence.test_human_trust_model
# [TESTS] src/zephyr/intelligence/human_trust_model.py
"""MOD-INT-HUMAN-TRUST 单元测试：human_trust_model 人机信任模型。

蓝图验收（B1-00221/CAND-AISA-009，C2 C-031）：
置信度三层路由（auto/confirm/forbidden，阈值表按决策域注入）+
人工否决记录学习（原因分类统计+模式提取）+
周期信任分校准（分域，分数变更写审计）。
时钟/审计全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.intelligence.human_trust_model",
    reason="human_trust_model not importable",
)

from zephyr.intelligence.human_trust_model import (  # noqa: E402
    HumanTrustError,
    HumanTrustModel,
    TrustRoute,
    TrustScoreChange,
    TrustThresholds,
    VetoRecord,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)

_THRESHOLDS = {
    "signal": TrustThresholds(auto_threshold=0.8, confirm_threshold=0.5, initial_trust=0.6),
    "risk": TrustThresholds(auto_threshold=0.9, confirm_threshold=0.7, initial_trust=0.4),
}


def _model(audits: list | None = None, thresholds=None) -> HumanTrustModel:
    return HumanTrustModel(
        thresholds=_THRESHOLDS if thresholds is None else thresholds,
        clock=lambda: _T0,
        audit_sink=(lambda c: audits.append(c)) if audits is not None else None,
    )


def _veto(domain: str = "signal", category: str = "逻辑错误") -> VetoRecord:
    return VetoRecord(domain=domain, reason_category=category, detail="d", recorded_at=_T0)


# ──────────────────────────────────────────────────────────────────────────────
# 构造（阈值表校验 Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_ok(self) -> None:
        model = _model()
        assert model.trust_score("signal") == 0.6
        assert model.trust_score("risk") == 0.4

    def test_empty_thresholds_raises(self) -> None:
        with pytest.raises(HumanTrustError):
            HumanTrustModel(thresholds={}, clock=lambda: _T0)

    def test_inverted_thresholds_raises(self) -> None:
        bad = {"d": TrustThresholds(auto_threshold=0.4, confirm_threshold=0.8)}
        with pytest.raises(HumanTrustError):
            HumanTrustModel(thresholds=bad, clock=lambda: _T0)

    def test_out_of_range_threshold_raises(self) -> None:
        bad = {"d": TrustThresholds(auto_threshold=1.2, confirm_threshold=0.5)}
        with pytest.raises(HumanTrustError):
            HumanTrustModel(thresholds=bad, clock=lambda: _T0)



# ──────────────────────────────────────────────────────────────────────────────
# 三层路由
# ──────────────────────────────────────────────────────────────────────────────


class TestRoute:
    def test_auto_route(self) -> None:
        assert _model().route("signal", 0.85) is TrustRoute.AUTO

    def test_auto_boundary(self) -> None:
        assert _model().route("signal", 0.8) is TrustRoute.AUTO

    def test_confirm_route(self) -> None:
        assert _model().route("signal", 0.6) is TrustRoute.CONFIRM

    def test_confirm_boundary(self) -> None:
        assert _model().route("signal", 0.5) is TrustRoute.CONFIRM

    def test_forbidden_route(self) -> None:
        assert _model().route("signal", 0.2) is TrustRoute.FORBIDDEN

    def test_domain_specific_thresholds(self) -> None:
        model = _model()
        assert model.route("risk", 0.85) is TrustRoute.CONFIRM  # risk auto=0.9
        assert model.route("signal", 0.85) is TrustRoute.AUTO

    def test_unknown_domain_raises(self) -> None:
        with pytest.raises(HumanTrustError):
            _model().route("ghost", 0.9)

    def test_confidence_out_of_range_raises(self) -> None:
        with pytest.raises(HumanTrustError):
            _model().route("signal", 1.5)
        with pytest.raises(HumanTrustError):
            _model().route("signal", -0.1)


# ──────────────────────────────────────────────────────────────────────────────
# 人工否决记录学习
# ──────────────────────────────────────────────────────────────────────────────


class TestVetoLearning:
    def test_record_and_stats(self) -> None:
        model = _model()
        model.record_veto(_veto(category="逻辑错误"))
        model.record_veto(_veto(category="逻辑错误"))
        model.record_veto(_veto(category="数据过期"))
        pattern = model.veto_pattern("signal")
        assert pattern.total == 3
        assert pattern.category_counts == (("逻辑错误", 2), ("数据过期", 1))
        assert pattern.dominant_category == "逻辑错误"

    def test_dominant_tie_break_deterministic(self) -> None:
        model = _model()
        model.record_veto(_veto(category="b类"))
        model.record_veto(_veto(category="a类"))
        pattern = model.veto_pattern("signal")
        assert pattern.dominant_category == "a类"  # 并列按分类名序

    def test_empty_pattern(self) -> None:
        pattern = _model().veto_pattern("signal")
        assert pattern.total == 0
        assert pattern.category_counts == ()
        assert pattern.dominant_category is None

    def test_domain_isolation(self) -> None:
        model = _model()
        model.record_veto(_veto(domain="signal", category="逻辑错误"))
        assert model.veto_pattern("risk").total == 0

    def test_unknown_domain_raises(self) -> None:
        model = _model()
        with pytest.raises(HumanTrustError):
            model.record_veto(_veto(domain="ghost"))
        with pytest.raises(HumanTrustError):
            model.veto_pattern("ghost")

    def test_empty_category_raises(self) -> None:
        with pytest.raises(HumanTrustError):
            _model().record_veto(_veto(category=""))


# ──────────────────────────────────────────────────────────────────────────────
# 周期信任分校准
# ──────────────────────────────────────────────────────────────────────────────


class TestRecalibrate:
    def test_recalibrate_updates_score_with_audit(self) -> None:
        audits: list[TrustScoreChange] = []
        model = _model(audits)
        model.record_veto(_veto())
        change = model.recalibrate("signal", period_id="2026-W35", decisions_observed=4)
        assert change.old_score == 0.6
        assert change.veto_rate == 0.25
        assert change.new_score == pytest.approx(0.6 * 0.75)
        assert change.changed_at == _T0
        assert model.trust_score("signal") == pytest.approx(0.45)
        assert audits == [change]  # 分数变更写审计

    def test_zero_veto_keeps_score(self) -> None:
        model = _model()
        change = model.recalibrate("signal", period_id="p1", decisions_observed=10)
        assert change.new_score == 0.6

    def test_per_domain_independent(self) -> None:
        model = _model()
        model.recalibrate("signal", period_id="p1", decisions_observed=10)
        assert model.trust_score("risk") == 0.4  # 未校准域不受影响

    def test_duplicate_period_rejected(self) -> None:
        model = _model()
        model.recalibrate("signal", period_id="p1", decisions_observed=10)
        with pytest.raises(HumanTrustError):
            model.recalibrate("signal", period_id="p1", decisions_observed=10)

    def test_same_period_other_domain_ok(self) -> None:
        model = _model()
        model.recalibrate("signal", period_id="p1", decisions_observed=10)
        model.recalibrate("risk", period_id="p1", decisions_observed=10)  # 不抛

    def test_invalid_inputs_raise(self) -> None:
        model = _model()
        with pytest.raises(HumanTrustError):
            model.recalibrate("signal", period_id="", decisions_observed=10)
        with pytest.raises(HumanTrustError):
            model.recalibrate("signal", period_id="p1", decisions_observed=0)
        with pytest.raises(HumanTrustError):
            model.recalibrate("ghost", period_id="p1", decisions_observed=10)

    def test_veto_exceeds_decisions_raises(self) -> None:
        model = _model()
        model.record_veto(_veto())
        model.record_veto(_veto())
        with pytest.raises(HumanTrustError):
            model.recalibrate("signal", period_id="p1", decisions_observed=1)
