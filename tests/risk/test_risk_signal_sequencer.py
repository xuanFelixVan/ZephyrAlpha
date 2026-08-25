# [BLUEPRINT] MOD-RK-41 | docs/03_modules/_domain_risk/risk_signal_sequencer/blueprint.md | §test
# [MODULE] tests.risk.test_risk_signal_sequencer
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.risk_signal_sequencer
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_risk_signal_sequencer.py
# [A_test] module_id: MOD-RK-41 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-RK-41 单元测试: RiskSignalSequencer — 风险-信号交互排序器。

覆盖: 全序规则（阻断期内 SUPPRESSED/CLEAR 后 ADMITTED/GLOBAL 全覆盖/SYMBOL
仅同标的/边界同时刻阻断先生效）、乱序检测（后到更早风控事件→REVOKED+
violation）、风控恒胜、幂等去重（信号/风控双侧）、输入 Fail-Closed、
audit_sink 触发范围与异常不阻断、确定性。
"""

from __future__ import annotations

import datetime

import pytest

from zephyr.risk.risk_signal_sequencer import (
    ArbitrationAction,
    ArbitrationRecord,
    InvalidSequencerConfigError,
    InvalidSequencerEventError,
    RiskEvent,
    RiskEventKind,
    RiskScope,
    RiskSignalSequencer,
    SignalEvent,
)

T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)


def _dt(seconds: int) -> datetime.datetime:
    return T0 + datetime.timedelta(seconds=seconds)


def _risk(
    event_id: str,
    kind: RiskEventKind = RiskEventKind.VETO,
    scope: RiskScope = RiskScope.GLOBAL,
    symbol: str = "",
    seconds: int = 0,
    seq: int = 1,
) -> RiskEvent:
    return RiskEvent(
        event_id=event_id,
        kind=kind,
        scope=scope,
        symbol=symbol,
        occurred_at=_dt(seconds),
        seq=seq,
    )


def _signal(signal_id: str, symbol: str = "600000", seconds: int = 10, seq: int = 1) -> SignalEvent:
    return SignalEvent(signal_id=signal_id, symbol=symbol, occurred_at=_dt(seconds), seq=seq)


@pytest.fixture
def seq() -> RiskSignalSequencer:
    return RiskSignalSequencer()


class TestTotalOrder:
    def test_signal_admitted_without_block(self, seq):
        r = seq.ingest_signal(_signal("S1"))
        assert r.action is ArbitrationAction.ADMITTED
        assert r.violation is False
        assert r.deduped is False

    def test_signal_suppressed_during_active_veto(self, seq):
        seq.ingest_risk(_risk("R1", seconds=0))
        r = seq.ingest_signal(_signal("S1", seconds=10))
        assert r.action is ArbitrationAction.SUPPRESSED
        assert r.risk_event_id == "R1"

    def test_signal_suppressed_during_downgrade(self, seq):
        seq.ingest_risk(_risk("R1", kind=RiskEventKind.DOWNGRADE, seconds=0))
        r = seq.ingest_signal(_signal("S1", seconds=10))
        assert r.action is ArbitrationAction.SUPPRESSED

    def test_signal_admitted_after_clear(self, seq):
        seq.ingest_risk(_risk("R1", seconds=0))
        seq.ingest_risk(_risk("R2", kind=RiskEventKind.CLEAR, seconds=5))
        r = seq.ingest_signal(_signal("S1", seconds=10))
        assert r.action is ArbitrationAction.ADMITTED

    def test_block_at_same_instant_suppresses(self, seq):
        # 风控 occurred_at == 信号 occurred_at → 阻断先生效（<=）
        seq.ingest_risk(_risk("R1", seconds=10, seq=1))
        r = seq.ingest_signal(_signal("S1", seconds=10, seq=2))
        assert r.action is ArbitrationAction.SUPPRESSED

    def test_block_after_signal_does_not_suppress(self, seq):
        seq.ingest_risk(_risk("R1", seconds=20))
        r = seq.ingest_signal(_signal("S1", seconds=10))
        assert r.action is ArbitrationAction.ADMITTED


class TestScope:
    def test_global_block_covers_all_symbols(self, seq):
        seq.ingest_risk(_risk("R1", scope=RiskScope.GLOBAL, seconds=0))
        assert seq.ingest_signal(_signal("S1", symbol="600000")).action is ArbitrationAction.SUPPRESSED
        assert seq.ingest_signal(_signal("S2", symbol="000001")).action is ArbitrationAction.SUPPRESSED

    def test_symbol_block_only_covers_same_symbol(self, seq):
        seq.ingest_risk(_risk("R1", scope=RiskScope.SYMBOL, symbol="600000", seconds=0))
        assert seq.ingest_signal(_signal("S1", symbol="600000")).action is ArbitrationAction.SUPPRESSED
        assert seq.ingest_signal(_signal("S2", symbol="000001")).action is ArbitrationAction.ADMITTED

    def test_symbol_clear_only_clears_same_symbol(self, seq):
        seq.ingest_risk(_risk("R1", scope=RiskScope.SYMBOL, symbol="600000", seconds=0))
        seq.ingest_risk(_risk("R2", scope=RiskScope.SYMBOL, symbol="000001", seconds=0))
        seq.ingest_risk(_risk("R3", kind=RiskEventKind.CLEAR, scope=RiskScope.SYMBOL, symbol="600000", seconds=5))
        assert seq.ingest_signal(_signal("S1", symbol="600000")).action is ArbitrationAction.ADMITTED
        assert seq.ingest_signal(_signal("S2", symbol="000001")).action is ArbitrationAction.SUPPRESSED

    def test_global_clear_clears_all(self, seq):
        seq.ingest_risk(_risk("R1", scope=RiskScope.SYMBOL, symbol="600000", seconds=0))
        seq.ingest_risk(_risk("R2", scope=RiskScope.GLOBAL, seconds=0))
        seq.ingest_risk(_risk("R3", kind=RiskEventKind.CLEAR, scope=RiskScope.GLOBAL, seconds=5))
        assert seq.active_blocks() == ()

    def test_active_blocks_snapshot_by_symbol(self, seq):
        seq.ingest_risk(_risk("R1", scope=RiskScope.SYMBOL, symbol="600000", seconds=0))
        seq.ingest_risk(_risk("R2", scope=RiskScope.GLOBAL, seconds=0))
        assert len(seq.active_blocks("600000")) == 2
        assert len(seq.active_blocks("000001")) == 1
        assert len(seq.active_blocks()) == 2


class TestOutOfOrderArbitration:
    def test_late_earlier_risk_revokes_admitted_signal(self, seq):
        seq.ingest_signal(_signal("S1", seconds=10, seq=1))
        records = seq.ingest_risk(_risk("R1", seconds=5, seq=1))
        revoked = [r for r in records if r.action is ArbitrationAction.REVOKED]
        assert len(revoked) == 1
        assert revoked[0].subject_id == "S1"
        assert revoked[0].violation is True
        assert revoked[0].risk_event_id == "R1"
        assert "ORDER_VIOLATION" in revoked[0].reason

    def test_revoked_signal_stays_revoked_on_redo(self, seq):
        seq.ingest_signal(_signal("S1", seconds=10))
        seq.ingest_risk(_risk("R1", seconds=5))
        r = seq.ingest_signal(_signal("S1", seconds=10))
        assert r.action is ArbitrationAction.REVOKED
        assert r.deduped is True

    def test_later_risk_does_not_revoke_earlier_signal(self, seq):
        seq.ingest_signal(_signal("S1", seconds=10))
        records = seq.ingest_risk(_risk("R1", seconds=20))
        assert all(r.action is not ArbitrationAction.REVOKED for r in records)

    def test_symbol_scoped_revocation_only_same_symbol(self, seq):
        seq.ingest_signal(_signal("S1", symbol="600000", seconds=10))
        seq.ingest_signal(_signal("S2", symbol="000001", seconds=10))
        records = seq.ingest_risk(_risk("R1", scope=RiskScope.SYMBOL, symbol="600000", seconds=5))
        revoked_ids = {r.subject_id for r in records if r.action is ArbitrationAction.REVOKED}
        assert revoked_ids == {"S1"}

    def test_seq_tiebreak_in_order_key(self, seq):
        # 同时刻：seq 更大的信号晚于 seq 更小的风控 → 乱序撤销
        seq.ingest_signal(_signal("S1", seconds=10, seq=5))
        records = seq.ingest_risk(_risk("R1", seconds=10, seq=3))
        assert any(r.action is ArbitrationAction.REVOKED for r in records)


class TestIdempotency:
    def test_duplicate_signal_deduped(self, seq):
        first = seq.ingest_signal(_signal("S1"))
        again = seq.ingest_signal(_signal("S1"))
        assert again.deduped is True
        assert again.action is first.action

    def test_duplicate_risk_deduped(self, seq):
        seq.ingest_risk(_risk("R1"))
        records = seq.ingest_risk(_risk("R1"))
        assert len(records) == 1
        assert records[0].deduped is True
        # 阻断不重复登记
        assert len(seq.active_blocks()) == 1


class TestFailClosed:
    def test_risk_event_blank_id(self):
        with pytest.raises(InvalidSequencerEventError):
            _risk(" ")

    def test_risk_event_symbol_scope_requires_symbol(self):
        with pytest.raises(InvalidSequencerEventError):
            _risk("R1", scope=RiskScope.SYMBOL, symbol="")

    def test_risk_event_bad_kind(self):
        with pytest.raises(InvalidSequencerEventError):
            RiskEvent(
                event_id="R1",
                kind="VETO",  # type: ignore[arg-type]  # 字符串非枚举→拒绝
                scope=RiskScope.GLOBAL,
                symbol="",
                occurred_at=_dt(0),
                seq=1,
            )

    def test_risk_event_bad_time(self):
        with pytest.raises(InvalidSequencerEventError):
            RiskEvent(
                event_id="R1",
                kind=RiskEventKind.VETO,
                scope=RiskScope.GLOBAL,
                symbol="",
                occurred_at="2026-08-25",  # type: ignore[arg-type]
                seq=1,
            )

    def test_risk_event_bad_seq(self):
        with pytest.raises(InvalidSequencerEventError):
            RiskEvent(
                event_id="R1",
                kind=RiskEventKind.VETO,
                scope=RiskScope.GLOBAL,
                symbol="",
                occurred_at=_dt(0),
                seq=True,  # type: ignore[arg-type]  # bool 非 int→拒绝
            )

    def test_signal_blank_symbol(self):
        with pytest.raises(InvalidSequencerEventError):
            _signal("S1", symbol="")

    def test_ingest_wrong_type(self, seq):
        with pytest.raises(InvalidSequencerEventError):
            seq.ingest_signal("not-an-event")  # type: ignore[arg-type]
        with pytest.raises(InvalidSequencerEventError):
            seq.ingest_risk(_signal("S1"))  # type: ignore[arg-type]

    def test_config_bad_audit_sink(self):
        with pytest.raises(InvalidSequencerConfigError):
            RiskSignalSequencer(audit_sink="not-callable")  # type: ignore[arg-type]


class TestAuditSink:
    def test_suppressed_and_revoked_emitted(self):
        seen: list[ArbitrationRecord] = []
        seq = RiskSignalSequencer(audit_sink=seen.append)
        seq.ingest_risk(_risk("R1", seconds=0))
        seq.ingest_signal(_signal("S1", seconds=10))  # SUPPRESSED
        # 无阻断前先放行 S3，再后到更早风控→REVOKE
        seq2_seen: list[ArbitrationRecord] = []
        seq2 = RiskSignalSequencer(audit_sink=seq2_seen.append)
        seq2.ingest_signal(_signal("S3", seconds=10))
        seq2.ingest_risk(_risk("R9", seconds=5))
        assert [r.action for r in seen] == [ArbitrationAction.SUPPRESSED]
        assert [r.action for r in seq2_seen] == [ArbitrationAction.REVOKED]

    def test_admitted_not_emitted(self):
        seen: list[ArbitrationRecord] = []
        seq = RiskSignalSequencer(audit_sink=seen.append)
        seq.ingest_signal(_signal("S1"))
        assert seen == []

    def test_sink_exception_does_not_block(self):
        def _boom(_record: ArbitrationRecord) -> None:
            raise RuntimeError("sink down")

        seq = RiskSignalSequencer(audit_sink=_boom)
        seq.ingest_risk(_risk("R1", seconds=0))
        r = seq.ingest_signal(_signal("S1", seconds=10))
        assert r.action is ArbitrationAction.SUPPRESSED
        assert seq.sink_errors == 1


class TestDeterminism:
    def test_same_sequence_same_output(self):
        def _run() -> list[str]:
            s = RiskSignalSequencer()
            out: list[str] = []
            out.append(s.ingest_signal(_signal("S1", seconds=10)).action.value)
            for rec in s.ingest_risk(_risk("R1", seconds=5)):
                out.append(rec.action.value)
            out.append(s.ingest_signal(_signal("S2", seconds=20)).action.value)
            s.ingest_risk(_risk("R2", kind=RiskEventKind.CLEAR, seconds=25))
            out.append(s.ingest_signal(_signal("S3", seconds=30)).action.value)
            return out

        assert _run() == _run() == ["ADMITTED", "ADMITTED", "REVOKED", "SUPPRESSED", "ADMITTED"]
