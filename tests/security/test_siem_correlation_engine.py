# [BLUEPRINT] MOD-SEC-025 | docs/03_modules/_domain_security/siem_correlation_engine/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SEC-025 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.security.test_siem_correlation_engine
# [TESTS] src/zephyr/security/siem_correlation_engine.py
"""MOD-SEC-025 单元测试：siem_correlation_engine SIEM 跨域关联引擎。

蓝图验收（B12-03820/CAND-SEC-006，B12）：Sigma 风格规则注册（同主体/同会
话滑动时间窗事件序列聚合）+ 命中提升严重度 + 告警分级路由（P0/P1 立即
通知，P2/P3 每日汇总）。时钟/路由/汇总全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.security.siem_correlation_engine",
    reason="siem_correlation_engine not importable",
)

from zephyr.security.siem_correlation_engine import (  # noqa: E402
    CorrelationAlert,
    GroupBy,
    SecurityEvent,
    Severity,
    SiemCorrelationEngine,
    SiemError,
    SigmaRule,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)

_CHAIN_RULE = SigmaRule(
    rule_id="attack-chain",
    title="注入→越权→数据导出 攻击链",
    sequence=("injection", "priv_escalation", "data_export"),
    window_seconds=300.0,
    group_by=GroupBy.SUBJECT,
    escalate_to=Severity.P0,
)


def _engine(
    immediate: list | None = None,
    summary: list | None = None,
    rules=(_CHAIN_RULE,),
) -> SiemCorrelationEngine:
    return SiemCorrelationEngine(
        rules=rules,
        clock=lambda: _T0,
        immediate_router=(lambda a: immediate.append(a)) if immediate is not None else None,
        summary_sink=(lambda a: summary.extend(a)) if summary is not None else None,
    )


def _event(
    event_type: str,
    seconds: float = 0.0,
    subject: str = "agent-a",
    session: str = "sess-1",
) -> SecurityEvent:
    return SecurityEvent(
        event_type=event_type,
        subject=subject,
        session_id=session,
        severity=Severity.P3,
        occurred_at=_T0 + datetime.timedelta(seconds=seconds),
        details={},
    )


# ──────────────────────────────────────────────────────────────────────────────
# 构造校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_empty_rules_raises(self) -> None:
        with pytest.raises(SiemError):
            SiemCorrelationEngine(rules=[], clock=lambda: _T0)

    def test_duplicate_rule_id_raises(self) -> None:
        with pytest.raises(SiemError):
            SiemCorrelationEngine(rules=[_CHAIN_RULE, _CHAIN_RULE], clock=lambda: _T0)

    def test_short_sequence_raises(self) -> None:
        bad = SigmaRule("r", "t", ("only",), 60.0, GroupBy.SUBJECT, Severity.P1)
        with pytest.raises(SiemError):
            SiemCorrelationEngine(rules=[bad], clock=lambda: _T0)

    def test_non_positive_window_raises(self) -> None:
        bad = SigmaRule("r", "t", ("a", "b"), 0.0, GroupBy.SUBJECT, Severity.P1)
        with pytest.raises(SiemError):
            SiemCorrelationEngine(rules=[bad], clock=lambda: _T0)

    def test_empty_event_type_in_sequence_raises(self) -> None:
        bad = SigmaRule("r", "t", ("a", ""), 60.0, GroupBy.SUBJECT, Severity.P1)
        with pytest.raises(SiemError):
            SiemCorrelationEngine(rules=[bad], clock=lambda: _T0)

    def test_illegal_group_by_raises(self) -> None:
        bad = SigmaRule("r", "t", ("a", "b"), 60.0, "subject", Severity.P1)
        with pytest.raises(SiemError):
            SiemCorrelationEngine(rules=[bad], clock=lambda: _T0)


# ──────────────────────────────────────────────────────────────────────────────
# 序列聚合命中
# ──────────────────────────────────────────────────────────────────────────────


class TestCorrelation:
    def test_full_chain_hits_with_escalation(self) -> None:
        immediate: list[CorrelationAlert] = []
        engine = _engine(immediate)
        assert engine.ingest(_event("injection", 0)) == ()
        assert engine.ingest(_event("priv_escalation", 60)) == ()
        alerts = engine.ingest(_event("data_export", 120))
        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.rule_id == "attack-chain"
        assert alert.severity is Severity.P0  # 命中提升严重度（原事件 P3）
        assert alert.matched_types == ("injection", "priv_escalation", "data_export")
        assert alert.raised_at == _T0
        assert immediate == [alert]  # P0 立即路由

    def test_out_of_order_no_hit(self) -> None:
        engine = _engine()
        engine.ingest(_event("data_export", 0))
        engine.ingest(_event("injection", 10))
        assert engine.ingest(_event("priv_escalation", 20)) == ()

    def test_window_expired_no_hit(self) -> None:
        engine = _engine()
        engine.ingest(_event("injection", 0))
        engine.ingest(_event("priv_escalation", 10))
        # 距起点 400s > 300s 滑窗 → 起点已被裁剪
        assert engine.ingest(_event("data_export", 400)) == ()

    def test_cross_subject_isolated(self) -> None:
        engine = _engine()
        engine.ingest(_event("injection", 0, subject="agent-a"))
        engine.ingest(_event("priv_escalation", 10, subject="agent-b"))
        assert engine.ingest(_event("data_export", 20, subject="agent-a")) == ()

    def test_session_grouping(self) -> None:
        rule = SigmaRule(
            "sess-rule",
            "t",
            ("login_fail", "token_reuse"),
            120.0,
            GroupBy.SESSION,
            Severity.P2,
        )
        engine = _engine(rules=(rule,))
        engine.ingest(_event("login_fail", 0, session="s1"))
        assert engine.ingest(_event("token_reuse", 30, session="s2")) == ()
        alerts = engine.ingest(_event("token_reuse", 30, session="s1"))
        assert len(alerts) == 1
        assert alerts[0].group_key == "s1"

    def test_hit_consumes_events_no_repeat(self) -> None:
        engine = _engine()
        engine.ingest(_event("injection", 0))
        engine.ingest(_event("priv_escalation", 10))
        assert len(engine.ingest(_event("data_export", 20))) == 1
        # 再补一个导出事件：链事件已被消费，不重复告警
        assert engine.ingest(_event("data_export", 30)) == ()


# ──────────────────────────────────────────────────────────────────────────────
# 分级路由
# ──────────────────────────────────────────────────────────────────────────────


class TestRouting:
    def test_p2_p3_buffered_for_daily_summary(self) -> None:
        summary: list[CorrelationAlert] = []
        rule = SigmaRule(
            "low-rule",
            "t",
            ("scan", "probe"),
            60.0,
            GroupBy.SUBJECT,
            Severity.P2,
        )
        immediate: list[CorrelationAlert] = []
        engine = _engine(immediate, summary, rules=(rule,))
        engine.ingest(_event("scan", 0))
        alerts = engine.ingest(_event("probe", 10))
        assert len(alerts) == 1
        assert immediate == []  # P2 不立即路由
        flushed = engine.flush_summary()
        assert flushed == tuple(alerts)
        assert summary == list(alerts)  # 每日汇总推送 sink

    def test_flush_summary_empty(self) -> None:
        engine = _engine()
        assert engine.flush_summary() == ()

    def test_flush_summary_clears_buffer(self) -> None:
        rule = SigmaRule(
            "low-rule",
            "t",
            ("scan", "probe"),
            60.0,
            GroupBy.SUBJECT,
            Severity.P3,
        )
        engine = _engine(rules=(rule,))
        engine.ingest(_event("scan", 0))
        engine.ingest(_event("probe", 10))
        assert len(engine.flush_summary()) == 1
        assert engine.flush_summary() == ()


# ──────────────────────────────────────────────────────────────────────────────
# 事件校验 / 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestValidationAndDeterminism:
    def test_empty_event_type_raises(self) -> None:
        engine = _engine()
        with pytest.raises(SiemError):
            engine.ingest(_event(""))

    def test_empty_subject_raises(self) -> None:
        engine = _engine()
        with pytest.raises(SiemError):
            engine.ingest(_event("injection", subject=""))

    def test_illegal_event_type_raises(self) -> None:
        engine = _engine()
        with pytest.raises(SiemError):
            engine.ingest("not-an-event")

    def test_determinism_same_input_same_alerts(self) -> None:
        def run() -> tuple:
            engine = _engine()
            engine.ingest(_event("injection", 0))
            engine.ingest(_event("priv_escalation", 60))
            return engine.ingest(_event("data_export", 120))

        assert run() == run()
