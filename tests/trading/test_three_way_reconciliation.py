# [BLUEPRINT] MOD-TRADING-013 | docs/03_modules/_domain_trading/three_way_reconciliation/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-TRADING-013 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.trading.test_three_way_reconciliation
# [TESTS] src/zephyr/trading/three_way_reconciliation.py
"""MOD-TRADING-013 单元测试：three_way_reconciliation 三向对账引擎。

蓝图验收（B13-04352/CAND-TRD-011，A3 D-TRADING-02）：
交易/持仓/资金三方流水（佣金/印花税/利息逐笔）+ 异常四类词表闭合
（价格/数量/费用/缺失）+ 自动匹配（标的+数量+金额容差）+ 未匹配台账
跟进状态机（OPEN→INVESTIGATING→RESOLVED，终态不可逆）+ 确定性。
时钟/告警全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime
from decimal import Decimal

import pytest

pytest.importorskip(
    "zephyr.trading.three_way_reconciliation",
    reason="three_way_reconciliation not importable",
)

from zephyr.trading.three_way_reconciliation import (  # noqa: E402
    AnomalyClass,
    CashFlow,
    FeeType,
    FollowUpStatus,
    PositionFlow,
    ThreeWayReconEngine,
    ThreeWayReconError,
    TradeFlow,
)

_T0 = datetime.datetime(2026, 8, 25, 15, 30, 0)
_DAY = datetime.date(2026, 8, 25)


def _trade(
    flow_id: str = "T-1",
    symbol: str = "600000",
    side: str = "BUY",
    qty: str = "1000",
    price: str = "10.00",
    fee: str = "15.00",
) -> TradeFlow:
    return TradeFlow(
        flow_id=flow_id,
        symbol=symbol,
        side=side,
        quantity=Decimal(qty),
        price=Decimal(price),
        expected_fee=Decimal(fee),
        traded_at=_T0,
    )


def _position(
    flow_id: str = "P-1",
    trade_ref: str = "T-1",
    symbol: str = "600000",
    qty: str = "1000",
    amount: str = "10000.00",
) -> PositionFlow:
    return PositionFlow(
        flow_id=flow_id,
        trade_ref=trade_ref,
        symbol=symbol,
        quantity=Decimal(qty),
        amount=Decimal(amount),
        confirmed_at=_T0,
    )


def _cash(flow_id: str, fee_type: FeeType, amount: str, trade_ref: str | None = "T-1") -> CashFlow:
    return CashFlow(
        flow_id=flow_id,
        fee_type=fee_type,
        amount=Decimal(amount),
        trade_ref=trade_ref,
        posted_at=_T0,
    )


def _engine(**kwargs) -> ThreeWayReconEngine:
    base = {"clock": lambda: _T0}
    base.update(kwargs)
    return ThreeWayReconEngine(**base)


def _run(engine: ThreeWayReconEngine, **over):
    return engine.reconcile(
        recon_id=over.get("recon_id", "R-1"),
        recon_date=_DAY,
        trades=over.get("trades", [_trade()]),
        positions=over.get("positions", [_position()]),
        cash_flows=over.get(
            "cash_flows",
            [
                _cash("C-1", FeeType.COMMISSION, "5.00"),
                _cash("C-2", FeeType.STAMP_TAX, "10.00"),
            ],
        ),
    )


# ──────────────────────────────────────────────────────────────────────────────
# 自动匹配（标的+数量+金额容差）
# ──────────────────────────────────────────────────────────────────────────────


class TestReconcileMatched:
    def test_all_matched(self) -> None:
        report = _run(_engine())
        assert report.matched is True
        assert report.matched_count == 1
        assert report.anomalies == ()
        assert report.totals == {
            "trades": 1,
            "positions": 1,
            "cash_flows": 2,
            "matched": 1,
            "anomalies": 0,
        }
        assert report.recon_date == _DAY
        assert report.created_at == _T0

    def test_interest_flow_not_matched_only_counted(self) -> None:
        # 利息为账户级费用（trade_ref=None）：仅计数，不参与逐笔匹配
        report = _run(
            _engine(),
            cash_flows=[
                _cash("C-1", FeeType.COMMISSION, "5.00"),
                _cash("C-2", FeeType.STAMP_TAX, "10.00"),
                _cash("C-3", FeeType.INTEREST, "2.35", trade_ref=None),
            ],
        )
        assert report.matched is True
        assert report.totals["cash_flows"] == 3

    def test_within_amount_tolerance(self) -> None:
        # 金额差 0.005 ≤ 容差 0.01 → 匹配
        report = _run(_engine(), positions=[_position(amount="10000.005")])
        assert report.matched is True


# ──────────────────────────────────────────────────────────────────────────────
# 异常分类（四类词表闭合）
# ──────────────────────────────────────────────────────────────────────────────


class TestAnomalyClasses:
    def test_quantity_mismatch(self) -> None:
        report = _run(_engine(), positions=[_position(qty="900")])
        assert report.matched is False
        assert report.matched_count == 0
        assert len(report.anomalies) == 1
        a = report.anomalies[0]
        assert a.anomaly_class is AnomalyClass.QUANTITY
        assert a.symbol == "600000"
        assert a.expected == Decimal("1000")
        assert a.actual == Decimal("900")
        assert a.status is FollowUpStatus.OPEN
        assert a.anomaly_id == "R-1-A001"

    def test_price_amount_mismatch(self) -> None:
        report = _run(_engine(), positions=[_position(amount="10050.00")])
        classes = [a.anomaly_class for a in report.anomalies]
        assert classes == [AnomalyClass.PRICE]
        assert report.anomalies[0].expected == Decimal("10000.00")
        assert report.anomalies[0].actual == Decimal("10050.00")

    def test_fee_mismatch(self) -> None:
        # 缺印花税流水：实际费用 5.00 vs 预估 15.00 → FEE
        report = _run(_engine(), cash_flows=[_cash("C-1", FeeType.COMMISSION, "5.00")])
        classes = [a.anomaly_class for a in report.anomalies]
        assert classes == [AnomalyClass.FEE]
        assert report.anomalies[0].actual == Decimal("5.00")

    def test_missing_position(self) -> None:
        report = _run(_engine(), positions=[], cash_flows=[])
        # 券商持仓确认缺失 → 单笔 MISSING（该笔不再展开数量/金额/费用比较）
        assert len(report.anomalies) == 1
        a = report.anomalies[0]
        assert a.anomaly_class is AnomalyClass.MISSING
        assert a.expected == Decimal("1000")
        assert a.actual is None
        assert report.matched_count == 0

    def test_missing_trade(self) -> None:
        report = _run(_engine(), trades=[], positions=[_position()], cash_flows=[])
        assert len(report.anomalies) == 1
        a = report.anomalies[0]
        assert a.anomaly_class is AnomalyClass.MISSING
        assert "系统交易缺失" in a.detail
        assert a.expected is None

    def test_missing_cash_ref(self) -> None:
        report = _run(
            _engine(),
            cash_flows=[
                _cash("C-1", FeeType.COMMISSION, "5.00"),
                _cash("C-2", FeeType.STAMP_TAX, "10.00"),
                _cash("C-9", FeeType.COMMISSION, "1.00", trade_ref="T-9"),
            ],
        )
        assert len(report.anomalies) == 1
        assert report.anomalies[0].anomaly_class is AnomalyClass.MISSING
        assert "未知交易" in report.anomalies[0].detail

    def test_symbol_mismatch_treated_missing(self) -> None:
        report = _run(_engine(), positions=[_position(symbol="000001")])
        classes = [a.anomaly_class for a in report.anomalies]
        assert classes == [AnomalyClass.MISSING]
        assert "标的错位" in report.anomalies[0].detail

    def test_multiple_classes_sequential_ids(self) -> None:
        report = _run(
            _engine(),
            positions=[_position(qty="900")],
            cash_flows=[_cash("C-9", FeeType.COMMISSION, "1.00", trade_ref="T-9")],
        )
        classes = [a.anomaly_class for a in report.anomalies]
        assert classes == [AnomalyClass.QUANTITY, AnomalyClass.FEE, AnomalyClass.MISSING]
        ids = [a.anomaly_id for a in report.anomalies]
        assert ids == ["R-1-A001", "R-1-A002", "R-1-A003"]


# ──────────────────────────────────────────────────────────────────────────────
# 确定性与告警
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminismAndAlert:
    def test_deterministic_repeat(self) -> None:
        kwargs = {"positions": [_position(qty="900")], "cash_flows": []}
        r1 = _run(_engine(), **kwargs)
        r2 = _run(_engine(), **kwargs)
        assert [(a.anomaly_id, a.anomaly_class, a.detail) for a in r1.anomalies] == [
            (a.anomaly_id, a.anomaly_class, a.detail) for a in r2.anomalies
        ]

    def test_alert_sink_called_on_anomaly(self) -> None:
        alerts: list = []
        report = _run(_engine(alert_sink=lambda r: alerts.append(r)), positions=[_position(qty="900")])
        assert alerts == [report]
        # 全匹配时不触发告警
        alerts2: list = []
        _run(_engine(alert_sink=lambda r: alerts2.append(r)))
        assert alerts2 == []

    def test_alert_sink_exception_swallowed(self) -> None:
        def bad_sink(report):
            raise RuntimeError("告警通道故障")

        report = _run(_engine(alert_sink=bad_sink), positions=[_position(qty="900")])
        assert report.matched is False  # 告警异常不阻断对账


# ──────────────────────────────────────────────────────────────────────────────
# 输入校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestValidation:
    def test_negative_qty_raises(self) -> None:
        with pytest.raises(ThreeWayReconError):
            _run(_engine(), trades=[_trade(qty="-1")])

    def test_empty_flow_id_raises(self) -> None:
        with pytest.raises(ThreeWayReconError):
            _run(_engine(), trades=[_trade(flow_id="")])

    def test_duplicate_trade_id_raises(self) -> None:
        with pytest.raises(ThreeWayReconError):
            _run(_engine(), trades=[_trade(), _trade()])

    def test_duplicate_position_trade_ref_raises(self) -> None:
        with pytest.raises(ThreeWayReconError):
            _run(_engine(), positions=[_position(), _position(flow_id="P-2")])

    def test_duplicate_recon_id_raises(self) -> None:
        engine = _engine()
        _run(engine)
        with pytest.raises(ThreeWayReconError):
            _run(engine)

    def test_bad_tolerance_raises(self) -> None:
        with pytest.raises(ThreeWayReconError):
            _engine(qty_tolerance=Decimal("-0.01"))
        with pytest.raises(ThreeWayReconError):
            _engine(amount_tolerance=0.01)  # 非 Decimal


# ──────────────────────────────────────────────────────────────────────────────
# 未匹配台账（跟进状态机）
# ──────────────────────────────────────────────────────────────────────────────


class TestLedgerFollowUp:
    def _engine_with_anomaly(self) -> tuple[ThreeWayReconEngine, str]:
        engine = _engine()
        report = _run(engine, positions=[_position(qty="900")])
        return engine, report.anomalies[0].anomaly_id

    def test_ledger_accumulates_sorted_and_filter(self) -> None:
        engine = _engine()
        _run(engine, recon_id="R-2", positions=[_position(qty="900")])
        _run(engine, recon_id="R-1", positions=[_position(qty="800")])
        entries = engine.ledger()
        assert [a.anomaly_id for a in entries] == ["R-1-A001", "R-2-A001"]  # 确定性排序
        assert len(engine.ledger(status=FollowUpStatus.OPEN)) == 2
        assert engine.ledger(status=FollowUpStatus.RESOLVED) == []

    def test_follow_up_full_flow(self) -> None:
        engine, aid = self._engine_with_anomaly()
        a = engine.update_follow_up(aid, FollowUpStatus.INVESTIGATING, operator="ops_zhang")
        assert a.status is FollowUpStatus.INVESTIGATING
        assert a.updated_at == _T0
        a = engine.update_follow_up(aid, FollowUpStatus.RESOLVED, operator="ops_li")
        assert a.status is FollowUpStatus.RESOLVED
        assert engine.anomaly(aid).status is FollowUpStatus.RESOLVED

    def test_follow_up_open_to_resolved_direct(self) -> None:
        engine, aid = self._engine_with_anomaly()
        a = engine.update_follow_up(aid, FollowUpStatus.RESOLVED, operator="ops_zhang")
        assert a.status is FollowUpStatus.RESOLVED

    def test_illegal_transition_raises(self) -> None:
        engine, aid = self._engine_with_anomaly()
        engine.update_follow_up(aid, FollowUpStatus.RESOLVED, operator="ops_zhang")
        with pytest.raises(ThreeWayReconError):
            engine.update_follow_up(aid, FollowUpStatus.OPEN, operator="ops_zhang")  # 终态不可逆
        engine2, aid2 = self._engine_with_anomaly()
        engine2.update_follow_up(aid2, FollowUpStatus.INVESTIGATING, operator="ops_zhang")
        with pytest.raises(ThreeWayReconError):
            engine2.update_follow_up(aid2, FollowUpStatus.OPEN, operator="ops_zhang")  # 不可回退

    def test_unknown_anomaly_and_empty_operator_raise(self) -> None:
        engine, aid = self._engine_with_anomaly()
        with pytest.raises(ThreeWayReconError):
            engine.update_follow_up("R-9-A001", FollowUpStatus.RESOLVED, operator="ops_zhang")
        with pytest.raises(ThreeWayReconError):
            engine.update_follow_up(aid, FollowUpStatus.RESOLVED, operator="")
        with pytest.raises(ThreeWayReconError):
            engine.anomaly("R-9-A001")
