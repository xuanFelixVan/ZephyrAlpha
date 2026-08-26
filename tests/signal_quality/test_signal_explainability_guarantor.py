# [BLUEPRINT] MOD-SIGQC-006 | docs/03_modules/_domain_signal_quality/signal_explainability_guarantor/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIGQC-006 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_quality.test_signal_explainability_guarantor
# [TESTS] src/zephyr/signal_quality/signal_explainability_guarantor.py
"""MOD-SIGQC-006 单元测试：signal_explainability_guarantor 可解释性强制保障器。

蓝图验收（B2-05485/CAND-SIGQC-005，B2 D-SIGNAL-211）：
理由链三要素（触发因子+规则命中+置信度依据）强制 + 缺失即阻断 + 告警 +
解释字段入 decision_snapshot/signal_audit 链（注入 sink）+ 按 signal_id
反查回放。审计/告警 sink 全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.signal_quality.signal_explainability_guarantor",
    reason="signal_explainability_guarantor not importable",
)

from zephyr.signal_quality.signal_explainability_guarantor import (  # noqa: E402
    ExplainabilityGuarantorError,
    ExplanationRecord,
    ReasonChain,
    SignalExplainabilityGuarantor,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)

_CHAIN = ReasonChain(
    trigger_factors=("pe_percentile_low", "volume_surge"),
    rule_hits=("RULE-VAL-001",),
    confidence_basis="近 60 日命中率 0.62，IC 均值 0.05",
)


def _guarantor(
    audit: list | None = None,
    alerts: list | None = None,
) -> SignalExplainabilityGuarantor:
    return SignalExplainabilityGuarantor(
        audit_sink=(lambda r: audit.append(r)) if audit is not None else (lambda r: None),
        alert_sink=(lambda v: alerts.append(v)) if alerts is not None else None,
        clock=lambda: _T0,
    )


def _enforce(g: SignalExplainabilityGuarantor, signal_id: str = "sig-1", **kwargs) -> ExplanationRecord:
    params = {
        "signal_id": signal_id,
        "symbol": "600519.SH",
        "direction": "long",
        "confidence": 0.8,
        "reason_chain": _CHAIN,
        "emitted_at": _T0,
    }
    params.update(kwargs)
    return g.enforce(**params)


# ──────────────────────────────────────────────────────────────────────────────
# 三要素齐全（正常路径）+ 回放反查
# ──────────────────────────────────────────────────────────────────────────────


class TestEnforceOk:
    def test_enforce_returns_record_and_audits(self) -> None:
        audit: list = []
        g = _guarantor(audit)
        record = _enforce(g)
        assert record.signal_id == "sig-1"
        assert record.symbol == "600519.SH"
        assert record.direction == "long"
        assert record.confidence == 0.8
        assert record.reason_chain is _CHAIN
        assert record.emitted_at == _T0
        assert record.recorded_at == _T0  # 注入时钟
        assert audit == [record]  # 解释字段入审计链 sink

    def test_replay_roundtrip(self) -> None:
        g = _guarantor()
        record = _enforce(g)
        assert g.replay("sig-1") == record
        assert g.has("sig-1")

    def test_records_sorted_deterministic(self) -> None:
        g = _guarantor()
        _enforce(g, "sig-b")
        _enforce(g, "sig-a")
        assert [r.signal_id for r in g.records()] == ["sig-a", "sig-b"]

    def test_deterministic_replay(self) -> None:
        audit1: list = []
        audit2: list = []
        g1, g2 = _guarantor(audit1), _guarantor(audit2)
        r1 = _enforce(g1, "sig-1")
        r2 = _enforce(g2, "sig-1")
        assert r1 == r2
        assert audit1 == audit2


# ──────────────────────────────────────────────────────────────────────────────
# 三要素缺失：阻断 + 告警
# ──────────────────────────────────────────────────────────────────────────────


class TestMissingElements:
    def test_missing_trigger_factors_blocked_with_alert(self) -> None:
        alerts: list = []
        g = _guarantor(alerts=alerts)
        chain = ReasonChain(trigger_factors=(), rule_hits=("R1",), confidence_basis="依据")
        with pytest.raises(ExplainabilityGuarantorError):
            _enforce(g, reason_chain=chain)
        assert len(alerts) == 1
        assert alerts[0].signal_id == "sig-1"
        assert "触发因子" in alerts[0].missing
        assert alerts[0].raised_at == _T0

    def test_empty_trigger_factor_element_blocked(self) -> None:
        g = _guarantor()
        chain = ReasonChain(trigger_factors=("",), rule_hits=("R1",), confidence_basis="依据")
        with pytest.raises(ExplainabilityGuarantorError):
            _enforce(g, reason_chain=chain)

    def test_missing_rule_hits_blocked(self) -> None:
        alerts: list = []
        g = _guarantor(alerts=alerts)
        chain = ReasonChain(trigger_factors=("f1",), rule_hits=(), confidence_basis="依据")
        with pytest.raises(ExplainabilityGuarantorError):
            _enforce(g, reason_chain=chain)
        assert "规则命中" in alerts[0].missing

    def test_empty_rule_hit_element_blocked(self) -> None:
        g = _guarantor()
        chain = ReasonChain(trigger_factors=("f1",), rule_hits=("",), confidence_basis="依据")
        with pytest.raises(ExplainabilityGuarantorError):
            _enforce(g, reason_chain=chain)

    def test_missing_confidence_basis_blocked(self) -> None:
        alerts: list = []
        g = _guarantor(alerts=alerts)
        chain = ReasonChain(trigger_factors=("f1",), rule_hits=("R1",), confidence_basis="")
        with pytest.raises(ExplainabilityGuarantorError):
            _enforce(g, reason_chain=chain)
        assert "置信度依据" in alerts[0].missing

    def test_all_elements_missing(self) -> None:
        alerts: list = []
        g = _guarantor(alerts=alerts)
        chain = ReasonChain(trigger_factors=(), rule_hits=(), confidence_basis="")
        with pytest.raises(ExplainabilityGuarantorError):
            _enforce(g, reason_chain=chain)
        assert alerts[0].missing == ("触发因子", "规则命中", "置信度依据")

    def test_blocked_signal_not_archived(self) -> None:
        audit: list = []
        g = _guarantor(audit)
        chain = ReasonChain(trigger_factors=(), rule_hits=("R1",), confidence_basis="依据")
        with pytest.raises(ExplainabilityGuarantorError):
            _enforce(g, reason_chain=chain)
        assert not g.has("sig-1")  # 阻断信号不入档
        assert audit == []  # 阻断信号不入审计链
        with pytest.raises(ExplainabilityGuarantorError):
            g.replay("sig-1")

    def test_alert_sink_failure_keeps_blocking(self) -> None:
        def _bad_sink(_violation) -> None:
            raise RuntimeError("告警通道故障")

        g = SignalExplainabilityGuarantor(
            audit_sink=lambda r: None, alert_sink=_bad_sink, clock=lambda: _T0
        )
        chain = ReasonChain(trigger_factors=(), rule_hits=("R1",), confidence_basis="依据")
        with pytest.raises(ExplainabilityGuarantorError):  # 阻断语义不受告警异常影响
            _enforce(g, reason_chain=chain)


# ──────────────────────────────────────────────────────────────────────────────
# 审计链 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestAuditChain:
    def test_audit_sink_not_injected_raises(self) -> None:
        with pytest.raises(ExplainabilityGuarantorError):
            SignalExplainabilityGuarantor(audit_sink=None, clock=lambda: _T0)

    def test_audit_sink_failure_fail_closed(self) -> None:
        def _bad_sink(_record) -> None:
            raise RuntimeError("审计链写失败")

        g = SignalExplainabilityGuarantor(audit_sink=_bad_sink, clock=lambda: _T0)
        with pytest.raises(ExplainabilityGuarantorError):
            _enforce(g)
        assert not g.has("sig-1")  # 未入审计链即未入档，可安全重试


# ──────────────────────────────────────────────────────────────────────────────
# 其余 Fail-Closed 分支
# ──────────────────────────────────────────────────────────────────────────────


class TestFailClosed:
    def test_empty_fields_raise(self) -> None:
        g = _guarantor()
        with pytest.raises(ExplainabilityGuarantorError):
            _enforce(g, signal_id="")
        with pytest.raises(ExplainabilityGuarantorError):
            _enforce(g, symbol="")
        with pytest.raises(ExplainabilityGuarantorError):
            _enforce(g, direction="")

    def test_confidence_out_of_range_raises(self) -> None:
        g = _guarantor()
        with pytest.raises(ExplainabilityGuarantorError):
            _enforce(g, confidence=-0.1)
        with pytest.raises(ExplainabilityGuarantorError):
            _enforce(g, confidence=1.1)

    def test_duplicate_signal_id_raises(self) -> None:
        g = _guarantor()
        _enforce(g, "sig-1")
        with pytest.raises(ExplainabilityGuarantorError):
            _enforce(g, "sig-1", symbol="000001.SZ")

    def test_wrong_reason_chain_type_raises(self) -> None:
        g = _guarantor()
        with pytest.raises(ExplainabilityGuarantorError):
            _enforce(g, reason_chain={"trigger_factors": ["f1"]})  # type: ignore[arg-type]

    def test_emitted_at_non_datetime_raises(self) -> None:
        g = _guarantor()
        with pytest.raises(ExplainabilityGuarantorError):
            _enforce(g, emitted_at="2026-08-26")  # type: ignore[arg-type]

    def test_replay_unknown_raises(self) -> None:
        g = _guarantor()
        _enforce(g, "sig-1")
        with pytest.raises(ExplainabilityGuarantorError):
            g.replay("ghost")
        assert not g.has("ghost")
