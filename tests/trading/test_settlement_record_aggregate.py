# [BLUEPRINT] MOD-TRADING-010 | docs/03_modules/_domain_trading/settlement_record_aggregate/blueprint.md
# [MODULE] tests.trading.test_settlement_record_aggregate
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.settlement_record_aggregate
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-TRADING-010 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-TRADING-010 SettlementRecord 结算记录核心聚合（AGG-TRD-02）单元测试.

覆盖: 注册/幂等键复用/settlement_id冲突Fail-Closed/状态机(PENDING→MATCHED/
DISCREPANT→RESOLVED→CONFIRMED)/非法转换/差异三档分类(费用类仅参考不升级工单)/
差异工单事件(OPEN/CLOSED)/sink异常不阻断/输入校验.
"""

from __future__ import annotations

import pytest

from zephyr.trading.settlement_record_aggregate import (
    DiscrepancyCategory,
    DiscrepancyTicket,
    DuplicateSettlementIdError,
    InvalidSettlementInputError,
    InvalidSettlementTransitionError,
    SettlementRecordBook,
    SettlementStatus,
)

TS = "2026-08-25T15:30:00+08:00"


def _book(sink=None) -> SettlementRecordBook:
    return SettlementRecordBook(event_sink=sink)


def _register(book: SettlementRecordBook, sid: str = "SET-1", idem: str = "IDEM-1"):
    return book.register(
        settlement_id=sid,
        idempotency_key=idem,
        trade_date="2026-08-25",
        account_id="ACC-1",
    )


class TestRegister:
    def test_register_initial_state(self):
        book = _book()
        record = _register(book)
        assert record.settlement_id == "SET-1"
        assert record.status is SettlementStatus.PENDING
        assert record.tickets == ()

    def test_register_idempotent_same_key_returns_existing(self):
        book = _book()
        _register(book)
        book.mark_matched("SET-1", TS)
        again = _register(book)
        assert again.status is SettlementStatus.MATCHED

    def test_register_duplicate_id_different_key_fail_closed(self):
        book = _book()
        _register(book)
        with pytest.raises(DuplicateSettlementIdError):
            _register(book, sid="SET-1", idem="IDEM-OTHER")

    def test_register_invalid_input(self):
        book = _book()
        with pytest.raises(InvalidSettlementInputError):
            book.register(settlement_id="", idempotency_key="K", trade_date="2026-08-25", account_id="A")


class TestStateMachine:
    def test_happy_path_matched_confirmed(self):
        book = _book()
        _register(book)
        book.mark_matched("SET-1", TS)
        record = book.confirm("SET-1", TS)
        assert record.status is SettlementStatus.CONFIRMED

    def test_discrepant_resolved_confirmed(self):
        book = _book()
        _register(book)
        book.mark_discrepant("SET-1", TS, drifts=(("D1", "PRICE_MISMATCH"),))
        book.resolve("SET-1", TS, note="人工核销")
        record = book.confirm("SET-1", TS)
        assert record.status is SettlementStatus.CONFIRMED

    def test_illegal_transition_fail_closed(self):
        book = _book()
        _register(book)
        with pytest.raises(InvalidSettlementTransitionError):
            book.confirm("SET-1", TS)
        with pytest.raises(InvalidSettlementTransitionError):
            book.resolve("SET-1", TS)

    def test_unknown_settlement_fail_closed(self):
        book = _book()
        with pytest.raises(InvalidSettlementInputError):
            book.mark_matched("SET-NONE", TS)


class TestDiscrepancyClassification:
    def test_price_qty_category(self):
        assert SettlementRecordBook.classify_drift("PRICE_MISMATCH") is DiscrepancyCategory.PRICE_QTY_MISMATCH
        assert SettlementRecordBook.classify_drift("QUANTITY_MISMATCH") is DiscrepancyCategory.PRICE_QTY_MISMATCH

    def test_missing_category(self):
        assert SettlementRecordBook.classify_drift("MISSING_IN_BROKER") is DiscrepancyCategory.MISSING_RECORD
        assert SettlementRecordBook.classify_drift("MISSING_IN_SYSTEM") is DiscrepancyCategory.MISSING_RECORD

    def test_fee_reference_category(self):
        assert SettlementRecordBook.classify_drift("COMMISSION_MISMATCH") is DiscrepancyCategory.FEE_REFERENCE


class TestDiscrepancyTickets:
    def test_ticket_raised_on_discrepant(self):
        seen: list[DiscrepancyTicket] = []
        book = _book(sink=seen.append)
        _register(book)
        record = book.mark_discrepant("SET-1", TS, drifts=(("D1", "PRICE_MISMATCH"), ("D2", "COMMISSION_MISMATCH")))
        # 费用参考类不升级工单——仅 PRICE_QTY 一档出票
        assert len(record.tickets) == 1
        ticket = record.tickets[0]
        assert ticket.category is DiscrepancyCategory.PRICE_QTY_MISMATCH
        assert ticket.drift_ids == ("D1",)
        assert ticket.status == "OPEN"
        assert seen == [ticket]

    def test_ticket_closed_on_resolve(self):
        seen: list[DiscrepancyTicket] = []
        book = _book(sink=seen.append)
        _register(book)
        book.mark_discrepant("SET-1", TS, drifts=(("D1", "MISSING_IN_BROKER"),))
        record = book.resolve("SET-1", TS)
        assert record.tickets[0].status == "CLOSED"
        assert len(seen) == 2
        assert seen[-1].status == "CLOSED"

    def test_missing_record_ticket(self):
        book = _book()
        _register(book)
        record = book.mark_discrepant("SET-1", TS, drifts=(("D9", "MISSING_IN_SYSTEM"),))
        assert record.tickets[0].category is DiscrepancyCategory.MISSING_RECORD

    def test_sink_exception_does_not_block(self):
        def _boom(_ticket):
            raise RuntimeError("sink down")

        book = _book(sink=_boom)
        _register(book)
        record = book.mark_discrepant("SET-1", TS, drifts=(("D1", "PRICE_MISMATCH"),))
        assert record.status is SettlementStatus.DISCREPANT
        assert len(record.tickets) == 1

    def test_mark_discrepant_requires_drifts(self):
        book = _book()
        _register(book)
        with pytest.raises(InvalidSettlementInputError):
            book.mark_discrepant("SET-1", TS, drifts=())
