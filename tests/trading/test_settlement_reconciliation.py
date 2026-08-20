# [BLUEPRINT] MOD-TRADING-003 | docs/03_modules/_domain_trading/settlement_reconciliation/blueprint.md
# [MODULE] tests.trading.test_settlement_reconciliation
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.settlement_reconciliation; zephyr.shared.contracts.fill
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-TRADING-003 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-TRADING-003 Settlement & Reconciliation Engine 单元测试.

覆盖: 完全匹配/价格差异/数量差异/佣金差异/系统缺失/券商缺失/
混合差异/容差边界/回调触发/回调异常不阻断/报告哈希一致性/Decimal精度.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from zephyr.shared.contracts.fill import Fill
from zephyr.trading.settlement_reconciliation import (
    BrokerSettlementRecord,
    DriftType,
    InvalidSettlementInputError,
    ReconciliationConfig,
    ReconciliationResult,
    SettlementDrift,
    SettlementReconciler,
    SettlementReport,
)

SETTLEMENT_DATE = "2026-08-01"


# ── 辅助工厂 ──


def make_fill(
    fill_id: str = "F001",
    order_id: str = "O001",
    broker_fill_id: str | None = "B001",
    symbol: str = "600000.SH",
    price: str = "10.00",
    qty: str = "100",
    commission: str = "5.00",
) -> Fill:
    return Fill(
        fill_id=fill_id,
        fill_price=Decimal(price),
        fill_timestamp=datetime(2026, 8, 1, 10, 0, tzinfo=UTC),
        filled_quantity=Decimal(qty),
        idempotency_key=f"ik-{fill_id}",
        order_id=order_id,
        strategy_id="S001",
        symbol=symbol,
        broker_fill_id=broker_fill_id,
        commission=Decimal(commission),
    )


def make_broker_record(
    trade_id: str = "B001",
    order_id: str = "O001",
    symbol: str = "600000.SH",
    price: str = "10.00",
    qty: str = "100",
    commission: str = "5.00",
    settlement_date: str = SETTLEMENT_DATE,
) -> BrokerSettlementRecord:
    return BrokerSettlementRecord(
        trade_id=trade_id,
        order_id=order_id,
        symbol=symbol,
        settlement_price=Decimal(price),
        settlement_quantity=Decimal(qty),
        commission=Decimal(commission),
        settlement_date=settlement_date,
    )


# ── 完全匹配 ──


class TestFullMatch:
    def test_single_trade_match(self):
        """单笔交易完全匹配——无差异。"""
        fills = [make_fill()]
        records = [make_broker_record()]
        r = SettlementReconciler().reconcile(fills, records, SETTLEMENT_DATE)

        assert r.matched is True
        assert len(r.drifts) == 0
        assert r.total_system_trades == 1
        assert r.total_broker_trades == 1
        assert r.matched_trades == 1
        assert r.settlement_date == SETTLEMENT_DATE

    def test_multiple_trades_all_match(self):
        """多笔交易全部匹配。"""
        fills = [
            make_fill(fill_id="F1", broker_fill_id="B1", order_id="O1"),
            make_fill(
                fill_id="F2",
                broker_fill_id="B2",
                order_id="O2",
                symbol="000001.SZ",
                price="20.50",
                qty="200",
                commission="10.25",
            ),
        ]
        records = [
            make_broker_record(trade_id="B1", order_id="O1"),
            make_broker_record(
                trade_id="B2", order_id="O2", symbol="000001.SZ", price="20.50", qty="200", commission="10.25"
            ),
        ]
        r = SettlementReconciler().reconcile(fills, records, SETTLEMENT_DATE)

        assert r.matched is True
        assert r.matched_trades == 2

    def test_empty_both_sides(self):
        """双侧均为空——匹配, 0笔。"""
        r = SettlementReconciler().reconcile([], [], SETTLEMENT_DATE)
        assert r.matched is True
        assert r.matched_trades == 0
        assert r.total_system_trades == 0
        assert r.total_broker_trades == 0

    def test_within_tolerance_match(self):
        """差异在容差范围内——视为匹配。"""
        fills = [make_fill(price="10.005", commission="5.004")]
        records = [make_broker_record(price="10.000", commission="5.000")]
        # price_tolerance=0.01, commission_tolerance=0.01 → 差异0.005/0.004 < 0.01
        r = SettlementReconciler().reconcile(fills, records, SETTLEMENT_DATE)
        assert r.matched is True
        assert r.matched_trades == 1


# ── 价格差异 ──


class TestPriceMismatch:
    def test_price_mismatch_detected(self):
        """价格差异超容差——检测到 PRICE_MISMATCH。"""
        fills = [make_fill(price="10.05")]
        records = [make_broker_record(price="10.00")]
        r = SettlementReconciler().reconcile(fills, records, SETTLEMENT_DATE)

        assert r.matched is False
        assert len(r.drifts) == 1
        d = r.drifts[0]
        assert d.drift_type == DriftType.PRICE_MISMATCH
        assert d.system_value == Decimal("10.05")
        assert d.broker_value == Decimal("10.00")
        assert d.diff == Decimal("0.05")

    def test_price_at_tolerance_boundary(self):
        """价格差异恰好等于容差——不报差异(>而非>=)。"""
        fills = [make_fill(price="10.01")]
        records = [make_broker_record(price="10.00")]
        # diff=0.01, tolerance=0.01 → abs(0.01) > 0.01 is False → 无差异
        r = SettlementReconciler().reconcile(fills, records, SETTLEMENT_DATE)
        assert r.matched is True


# ── 数量差异 ──


class TestQuantityMismatch:
    def test_quantity_mismatch_detected(self):
        """数量差异——检测到 QUANTITY_MISMATCH(A股必须精确, tolerance=0)。"""
        fills = [make_fill(qty="100")]
        records = [make_broker_record(qty="99")]
        r = SettlementReconciler().reconcile(fills, records, SETTLEMENT_DATE)

        assert r.matched is False
        assert len(r.drifts) == 1
        d = r.drifts[0]
        assert d.drift_type == DriftType.QUANTITY_MISMATCH
        assert d.diff == Decimal("1")


# ── 佣金差异 ──


class TestCommissionMismatch:
    def test_commission_mismatch_detected(self):
        """佣金差异超容差——检测到 COMMISSION_MISMATCH。"""
        fills = [make_fill(commission="5.00")]
        records = [make_broker_record(commission="5.50")]
        r = SettlementReconciler().reconcile(fills, records, SETTLEMENT_DATE)

        assert r.matched is False
        assert len(r.drifts) == 1
        d = r.drifts[0]
        assert d.drift_type == DriftType.COMMISSION_MISMATCH
        assert d.diff == Decimal("-0.50")


# ── 缺失记录 ──


class TestMissingRecords:
    def test_missing_in_broker(self):
        """系统有交易但券商结算单无——MISSING_IN_BROKER。"""
        fills = [make_fill(broker_fill_id="B1")]
        records = []  # 券商无记录
        r = SettlementReconciler().reconcile(fills, records, SETTLEMENT_DATE)

        assert r.matched is False
        assert len(r.drifts) == 1
        d = r.drifts[0]
        assert d.drift_type == DriftType.MISSING_IN_BROKER
        assert d.system_value is not None
        assert d.broker_value is None
        assert d.diff is None

    def test_missing_in_system(self):
        """券商有记录但系统无对应Fill——MISSING_IN_SYSTEM。"""
        fills = []
        records = [make_broker_record(trade_id="B1")]
        r = SettlementReconciler().reconcile(fills, records, SETTLEMENT_DATE)

        assert r.matched is False
        assert len(r.drifts) == 1
        d = r.drifts[0]
        assert d.drift_type == DriftType.MISSING_IN_SYSTEM
        assert d.system_value is None
        assert d.broker_value is not None
        assert d.diff is None

    def test_order_id_fallback_pairing(self):
        """broker_fill_id 缺失时用 order_id 回退配对。"""
        fills = [make_fill(broker_fill_id=None, order_id="O999")]
        records = [make_broker_record(trade_id="", order_id="O999")]
        r = SettlementReconciler().reconcile(fills, records, SETTLEMENT_DATE)
        assert r.matched is True
        assert r.matched_trades == 1


# ── 混合差异 ──


class TestMixedDrifts:
    def test_multiple_drift_types(self):
        """同一笔交易同时有价格+数量差异——2条drift。"""
        fills = [make_fill(price="10.10", qty="100")]
        records = [make_broker_record(price="10.00", qty="98")]
        r = SettlementReconciler().reconcile(fills, records, SETTLEMENT_DATE)

        assert r.matched is False
        assert len(r.drifts) == 2
        types = {d.drift_type for d in r.drifts}
        assert types == {DriftType.PRICE_MISMATCH, DriftType.QUANTITY_MISMATCH}

    def test_mixed_scenario(self):
        """混合场景: 1笔匹配 + 1笔价格差异 + 1笔系统缺失 + 1笔券商缺失。"""
        fills = [
            make_fill(fill_id="F1", broker_fill_id="B1", order_id="O1"),  # 匹配
            make_fill(fill_id="F2", broker_fill_id="B2", order_id="O2", price="10.50"),  # 价格差异
            make_fill(fill_id="F3", broker_fill_id="B3", order_id="O3"),  # 券商缺失
        ]
        records = [
            make_broker_record(trade_id="B1", order_id="O1"),  # 匹配
            make_broker_record(trade_id="B2", order_id="O2", price="10.00"),  # 价格差异
            make_broker_record(trade_id="BX", order_id="OX", symbol="999999.SZ"),  # 系统缺失
        ]
        r = SettlementReconciler().reconcile(fills, records, SETTLEMENT_DATE)

        assert r.matched is False
        assert r.matched_trades == 1
        assert r.total_system_trades == 3
        assert r.total_broker_trades == 3
        # 1 price mismatch + 1 missing_in_broker + 1 missing_in_system = 3 drifts
        assert len(r.drifts) == 3


# ── 容差配置 ──


class TestCustomConfig:
    def test_custom_tolerance(self):
        """自定义容差——更宽松的容差使差异不报。"""
        fills = [make_fill(price="10.20", qty="105")]
        records = [make_broker_record(price="10.00", qty="100")]
        # 默认容差: price=0.01, qty=0 → 会报差异
        r_default = SettlementReconciler().reconcile(fills, records, SETTLEMENT_DATE)
        assert not r_default.matched

        # 宽松容差: price=0.50, qty=10 → 不报差异
        config = ReconciliationConfig(
            price_tolerance=Decimal("0.50"),
            quantity_tolerance=Decimal("10"),
        )
        r_custom = SettlementReconciler(config=config).reconcile(fills, records, SETTLEMENT_DATE)
        assert r_custom.matched is True
        assert r_custom.matched_trades == 1


# ── 回调 ──


class TestDiscrepancyCallback:
    def test_callback_triggered_on_drift(self):
        """有差异时触发 on_discrepancy 回调。"""
        triggered: list[ReconciliationResult] = []

        def on_disc(result: ReconciliationResult) -> None:
            triggered.append(result)

        fills = [make_fill(price="10.50")]
        records = [make_broker_record(price="10.00")]
        SettlementReconciler(on_discrepancy=on_disc).reconcile(fills, records, SETTLEMENT_DATE)

        assert len(triggered) == 1
        assert triggered[0].matched is False

    def test_callback_not_triggered_on_match(self):
        """无差异时不触发回调。"""
        triggered: list[ReconciliationResult] = []

        def on_disc(result: ReconciliationResult) -> None:
            triggered.append(result)

        fills = [make_fill()]
        records = [make_broker_record()]
        SettlementReconciler(on_discrepancy=on_disc).reconcile(fills, records, SETTLEMENT_DATE)

        assert len(triggered) == 0

    def test_callback_exception_does_not_block(self):
        """回调抛异常不阻断对账主流程。"""

        def bad_callback(result: ReconciliationResult) -> None:
            raise RuntimeError("告警通道故障")

        fills = [make_fill(price="10.50")]
        records = [make_broker_record(price="10.00")]
        # 不应抛异常
        r = SettlementReconciler(on_discrepancy=bad_callback).reconcile(fills, records, SETTLEMENT_DATE)
        assert r.matched is False
        assert len(r.drifts) == 1


# ── 报告生成 ──


class TestSettlementReport:
    def test_report_generation(self):
        """生成结算报告——含 report_id/hash/settlement_date。"""
        fills = [make_fill()]
        records = [make_broker_record()]
        reconciler = SettlementReconciler()
        result = reconciler.reconcile(fills, records, SETTLEMENT_DATE)
        report = reconciler.generate_report(result, portfolio_id="PF-001")

        assert isinstance(report, SettlementReport)
        assert report.report_id.startswith("SR-")
        assert report.settlement_date == SETTLEMENT_DATE
        assert report.portfolio_id == "PF-001"
        assert len(report.report_hash) == 64  # SHA-256 hex
        assert report.schema_version == "1.0"
        assert report.result is result

    def test_report_hash_deterministic(self):
        """相同输入生成的报告哈希一致(确定性)。"""
        fills = [make_fill(price="10.50")]
        records = [make_broker_record(price="10.00")]
        reconciler = SettlementReconciler()

        result1 = reconciler.reconcile(fills, records, SETTLEMENT_DATE)
        result2 = reconciler.reconcile(fills, records, SETTLEMENT_DATE)

        report1 = reconciler.generate_report(result1, "PF-001")
        report2 = reconciler.generate_report(result2, "PF-001")

        # 哈希内容相同(忽略 timestamp/report_id/generated_at 不参与哈希)
        assert report1.report_hash == report2.report_hash

    def test_report_hash_changes_with_different_drifts(self):
        """不同差异内容生成不同哈希。"""
        reconciler = SettlementReconciler()

        # 场景1: 价格差异
        r1 = reconciler.reconcile(
            [make_fill(price="10.50")],
            [make_broker_record(price="10.00")],
            SETTLEMENT_DATE,
        )
        # 场景2: 数量差异
        r2 = reconciler.reconcile(
            [make_fill(qty="100")],
            [make_broker_record(qty="99")],
            SETTLEMENT_DATE,
        )

        h1 = reconciler.generate_report(r1, "PF-001").report_hash
        h2 = reconciler.generate_report(r2, "PF-001").report_hash
        assert h1 != h2

    def test_report_hash_changes_with_different_portfolio(self):
        """不同 portfolio_id 生成不同哈希。"""
        fills = [make_fill(price="10.50")]
        records = [make_broker_record(price="10.00")]
        reconciler = SettlementReconciler()
        result = reconciler.reconcile(fills, records, SETTLEMENT_DATE)

        h1 = reconciler.generate_report(result, "PF-001").report_hash
        h2 = reconciler.generate_report(result, "PF-002").report_hash
        assert h1 != h2


# ── 输入校验 ──


class TestInputValidation:
    def test_empty_settlement_date_raises(self):
        """空结算日期——抛 InvalidSettlementInputError。"""
        with pytest.raises(InvalidSettlementInputError):
            SettlementReconciler().reconcile([make_fill()], [make_broker_record()], "")

    def test_error_code(self):
        """错误码 ZA-TR-0003。"""
        assert InvalidSettlementInputError.error_code == "ZA-TR-0003"


# ── Decimal 精度 ──


class TestDecimalPrecision:
    def test_decimal_precision_preserved(self):
        """Decimal 精度在差异计算中保持。"""
        fills = [make_fill(price="10.123456789")]
        records = [make_broker_record(price="10.000000000")]
        config = ReconciliationConfig(price_tolerance=Decimal("0"))
        r = SettlementReconciler(config=config).reconcile(fills, records, SETTLEMENT_DATE)
        d = r.drifts[0]
        assert d.system_value == Decimal("10.123456789")
        assert d.broker_value == Decimal("10.000000000")
        assert d.diff == Decimal("0.123456789")

    def test_no_float_contamination(self):
        """确保无 float 污染——所有值为 Decimal 类型。"""
        fills = [make_fill(price="10.05", qty="100", commission="5.25")]
        records = [make_broker_record(price="10.00", qty="99", commission="5.00")]
        r = SettlementReconciler().reconcile(fills, records, SETTLEMENT_DATE)

        for d in r.drifts:
            if d.system_value is not None:
                assert isinstance(d.system_value, Decimal)
            if d.broker_value is not None:
                assert isinstance(d.broker_value, Decimal)
            if d.diff is not None:
                assert isinstance(d.diff, Decimal)


# ── 不可变性 ──


class TestImmutability:
    def test_frozen_dataclasses(self):
        """frozen dataclass 不可修改。"""
        record = make_broker_record()
        with pytest.raises(Exception):
            record.trade_id = "X"  # type: ignore[misc]

        drift = SettlementDrift(
            trade_id="T1",
            symbol="600000.SH",
            drift_type=DriftType.PRICE_MISMATCH,
            system_value=Decimal("10"),
            broker_value=Decimal("9"),
            diff=Decimal("1"),
        )
        with pytest.raises(Exception):
            drift.symbol = "X"  # type: ignore[misc]


# ── 结算日期不一致警告 ──


class TestSettlementDateMismatch:
    def test_date_mismatch_does_not_block(self):
        """券商记录结算日期不一致——警告但不阻断对账。"""
        fills = [make_fill()]
        records = [make_broker_record(settlement_date="2026-07-31")]
        # 日期不一致但 trade_id 仍能配对, 对账正常执行
        r = SettlementReconciler().reconcile(fills, records, SETTLEMENT_DATE)
        assert r.matched is True
        assert r.matched_trades == 1
