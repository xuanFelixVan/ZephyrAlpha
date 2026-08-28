# [BLUEPRINT] MOD-CMP-018 | 待统筹登记（blueprint 未建，真源=43_compliance_discipline.md §7.2/§7.3/§10）
# [MODULE] tests.compliance.test_manipulation_realtime_monitor
# [DOMAIN] D_COMPLIANCE
# [INVARIANTS] 4 类检测各正常/边界/异常覆盖; 实时流接入隔离(监测不接执行路径, broker 零额外调用); 全量 logger 注 tmp_path 不污染生产证据链(ARCH-200③ 教训); 阻断走 C-002 既有闸抛转; 冻结人工复解释放留痕
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ComplianceGateBlockError(ZA-EX-0011) / InvalidStreamEventError(ZA-CMP-0011)
# [TESTS] self
# [TTL] permanent
"""盘中操纵 4 类检测实时流驱动测试（43 号 §7.2/§7.3，MOD-CMP-018，A8 批）。

实证目标：
    1. Spoofing/Layering/WashTrade/拉抬打压 各正常命中+边界不命中+异常降级
    2. OrderManager 实时流接入：报单/撤单/成交事件驱动检测 + C-002 冻结闸抛转
       （执行隔离：冻结后 broker 零新调用；回调异常不阻断订单主链）
    3. RedisTickMarketProvider：分钟均量/5min 短窗/归一化/降级不抛
    4. 冻结生命周期：命中冻结→人工复解释放（留痕）→闸放行
    5. 集成冒烟：模拟多标的事件流，证据链 VERDICT+ALERT 完整
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.compliance.manipulation_realtime_monitor import (
    ManipulationRealtimeMonitor,
    MarketWindow,
    RedisTickMarketProvider,
)
from zephyr.compliance.trading_compliance_detector import (
    ComplianceOrderRecord,
    ComplianceTradeRecord,
    ManipulationType,
    TradingComplianceDetector,
)
from zephyr.ex_core.order_manager import ComplianceGateBlockError, OrderManager
from zephyr.infrastructure.h1_redis_hot.h1_redis_schema import tick_latest_key
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType
from zephyr.shared.contracts.fill import Fill

_T0 = datetime(2026, 8, 28, 10, 0, tzinfo=UTC)
_SYM = "600000.SH"


def _order(order_id: str, price: float, qty: float, *, placed_at: datetime = _T0, symbol: str = _SYM) -> ComplianceOrderRecord:
    return ComplianceOrderRecord(order_id=order_id, symbol=symbol, side="BUY", price=price, qty=qty, placed_at=placed_at)


def _fast_cancel_seq(idx: int, *, minutes: int = 5, qty: float = 3000):
    """大额（>20%×10000=2000）挂单后 10s 内撤单的事件对。"""
    placed = _T0 + timedelta(minutes=idx * minutes)
    return _order(f"o{idx}", 10.0, qty, placed_at=placed), placed + timedelta(seconds=5)


def _trade(qty: float = 100, *, buyer: str = "ACC1", seller: str = "ACC2", symbol: str = _SYM, at: datetime = _T0) -> ComplianceTradeRecord:
    return ComplianceTradeRecord(symbol=symbol, price=10.0, qty=qty, traded_at=at, buyer_account=buyer, seller_account=seller)


@pytest.fixture()
def logger(tmp_path: Path) -> ComplianceLogger:
    return ComplianceLogger(path=tmp_path / "compliance_log.jsonl")


@pytest.fixture()
def detector(logger: ComplianceLogger) -> TradingComplianceDetector:
    return TradingComplianceDetector(logger=logger)


@pytest.fixture()
def monitor(detector: TradingComplianceDetector, logger: ComplianceLogger) -> ManipulationRealtimeMonitor:
    return ManipulationRealtimeMonitor(detector, minute_volume_provider=lambda s: 10000.0, logger=logger)


def _spoofing_round(m: ManipulationRealtimeMonitor, n: int = 3, **kw):
    verdicts = []
    for i in range(n):
        rec, cancelled_at = _fast_cancel_seq(i, **kw)
        m.on_order_placed(rec)
        verdicts = m.on_order_cancelled(rec.symbol, rec.order_id, cancelled_at)
    return verdicts


# ── Spoofing 实时流 ──


class TestSpoofingRealtime:
    def test_three_fast_cancels_hit_and_freeze(self, monitor: ManipulationRealtimeMonitor, logger: ComplianceLogger) -> None:
        verdicts = _spoofing_round(monitor)
        assert any(v.mtype is ManipulationType.SPOOFING for v in verdicts)
        assert monitor.is_frozen(_SYM)
        assert monitor.frozen_symbols == (_SYM,)
        # 证据链：detector 逐命中 VERDICT + 本层 REALTIME_ALERT
        events = logger.read_all()
        assert any(r.event_type == "MANIPULATION_VERDICT" and r.payload["mtype"] == "SPOOFING" for r in events)
        alerts = [r for r in events if r.event_type == "MANIPULATION_REALTIME_ALERT"]
        assert len(alerts) == 1 and alerts[0].payload["frozen"] is True and alerts[0].source == "manipulation_realtime_monitor"

    def test_pattern_spread_beyond_window_no_hit(self, monitor: ManipulationRealtimeMonitor) -> None:
        verdicts = _spoofing_round(monitor, minutes=40)  # 任意 30min 窗内至多 1 次
        assert verdicts == [] and not monitor.is_frozen(_SYM)

    def test_small_orders_no_hit(self, monitor: ManipulationRealtimeMonitor) -> None:
        assert _spoofing_round(monitor, qty=100) == []

    def test_provider_missing_degrades_skip(self, detector: TradingComplianceDetector, logger: ComplianceLogger) -> None:
        m = ManipulationRealtimeMonitor(detector, logger=logger)  # 无 provider
        assert _spoofing_round(m) == []

    def test_zero_minute_volume_skips(self, detector: TradingComplianceDetector, logger: ComplianceLogger) -> None:
        m = ManipulationRealtimeMonitor(detector, minute_volume_provider=lambda s: 0.0, logger=logger)
        assert _spoofing_round(m) == []


# ── Layering 实时流 ──


class TestLayeringRealtime:
    def _gradient(self, m: ManipulationRealtimeMonitor, levels: int = 3, cancelled: int = 3):
        verdicts = []
        for i in range(levels):
            price = round(10.0 + i * 0.1, 2)
            placed = _T0 + timedelta(seconds=i)
            m.on_order_placed(_order(f"L{i}", price, 500, placed_at=placed))
            if i < cancelled:
                verdicts = m.on_order_cancelled(_SYM, f"L{i}", placed + timedelta(seconds=30))
        return verdicts

    def test_gradient_all_cancelled_hit(self, monitor: ManipulationRealtimeMonitor) -> None:
        assert any(v.mtype is ManipulationType.LAYERING for v in self._gradient(monitor))
        assert monitor.is_frozen(_SYM)

    def test_low_cancel_ratio_no_hit(self, monitor: ManipulationRealtimeMonitor) -> None:
        assert self._gradient(monitor, cancelled=1) == []  # 33% < 80%

    def test_two_levels_no_hit(self, monitor: ManipulationRealtimeMonitor) -> None:
        assert self._gradient(monitor, levels=2, cancelled=2) == []


# ── WashTrade 实时流 ──


class TestWashTradeRealtime:
    def test_self_trade_hit(self, monitor: ManipulationRealtimeMonitor) -> None:
        verdicts = monitor.on_trade(_trade(buyer="ACC1", seller="ACC1"))
        assert len(verdicts) == 1 and verdicts[0].mtype is ManipulationType.WASH_TRADE
        assert "人工复核" in verdicts[0].detail
        assert monitor.is_frozen(_SYM)

    def test_distinct_accounts_no_hit(self, monitor: ManipulationRealtimeMonitor) -> None:
        assert monitor.on_trade(_trade()) == []
        assert not monitor.is_frozen(_SYM)


# ── 拉抬打压 实时流 ──


class TestRampDumpRealtime:
    def _ramp_monitor(self, detector, logger, window):
        return ManipulationRealtimeMonitor(detector, market_window_provider=lambda s: window, logger=logger)

    def test_price_spike_with_share_hit(self, detector, logger) -> None:
        m = self._ramp_monitor(detector, logger, MarketWindow(price_change_pct=0.04, window_volume=10000))
        verdicts = m.on_trade(_trade(qty=5000))  # 我方占比 50% > 30%，价变 4% ≥ 3%
        assert any(v.mtype is ManipulationType.RAMP_DUMP for v in verdicts)
        assert m.is_frozen(_SYM)

    def test_below_threshold_no_hit(self, detector, logger) -> None:
        m = self._ramp_monitor(detector, logger, MarketWindow(price_change_pct=0.02, window_volume=10000))
        assert m.on_trade(_trade(qty=5000)) == []

    def test_zero_market_volume_skips(self, detector, logger) -> None:
        m = self._ramp_monitor(detector, logger, MarketWindow(price_change_pct=0.05, window_volume=0.0))
        assert m.on_trade(_trade(qty=5000)) == []

    def test_provider_missing_or_none_skips(self, detector, logger) -> None:
        assert ManipulationRealtimeMonitor(detector, logger=logger).on_trade(_trade(qty=5000)) == []
        m = self._ramp_monitor(detector, logger, None)
        assert m.on_trade(_trade(qty=5000)) == []

    def test_no_our_volume_skips(self, detector, logger) -> None:
        m = self._ramp_monitor(detector, logger, MarketWindow(price_change_pct=0.04, window_volume=10000))
        assert m.on_order_placed(_order("x", 10.0, 100)) == []  # 无我方成交 → 不评估占比


# ── 冻结生命周期 ──


class TestFreezeLifecycle:
    def test_release_after_manual_review(self, monitor: ManipulationRealtimeMonitor, logger: ComplianceLogger) -> None:
        _spoofing_round(monitor)
        assert monitor.is_frozen(_SYM)
        assert monitor.release_freeze(_SYM, operator="ops_zhang") is True
        assert not monitor.is_frozen(_SYM) and monitor.frozen_symbols == ()
        releases = [r for r in logger.read_all() if r.event_type == "MANIPULATION_FREEZE_RELEASE"]
        assert len(releases) == 1 and releases[0].payload["operator"] == "ops_zhang"
        assert releases[0].payload["released_mtype"] == "SPOOFING"

    def test_release_non_frozen_returns_false(self, monitor: ManipulationRealtimeMonitor) -> None:
        assert monitor.release_freeze("000001.SZ", operator="ops") is False


# ── OrderManager 实时流接入（含 C-002 闸抛转与执行隔离） ──


def _make_om(monitor: ManipulationRealtimeMonitor):
    broker = MagicMock()
    broker.submit_order.side_effect = lambda o: f"broker_{o.order_id[:8]}"
    broker.cancel_order.return_value = True
    om = OrderManager(manipulation_monitor=monitor)
    om.register_broker("test", broker)
    monitor.attach_order_manager(om)
    return om, broker


def _submit(om: OrderManager, qty: int = 3000, symbol: str = _SYM) -> str:
    order = om.create_order(symbol=symbol, strategy_id="a8", side=OrderSide.BUY, order_type=OrderType.LIMIT,
                            quantity=Decimal(qty), limit_price=Decimal("10.0"))
    return om.submit_order(order.order_id, "test") and order.order_id


class TestOrderManagerWiring:
    def test_submit_emits_placed_event(self, monitor: ManipulationRealtimeMonitor) -> None:
        om, _ = _make_om(monitor)
        oid = _submit(om, qty=100)
        assert monitor._driver.window_size(_SYM) == 1  # 报单事件已入 30min 窗
        assert om.get_order(oid) is not None

    def test_spoofing_via_order_flow_freezes_and_gate_blocks(self, monitor: ManipulationRealtimeMonitor) -> None:
        om, broker = _make_om(monitor)
        for _ in range(3):  # 挂撤 3 轮（同秒完成，≤10s 快撤口径）
            om.cancel_order(_submit(om))
        assert monitor.is_frozen(_SYM)
        calls_before = broker.submit_order.call_count
        with pytest.raises(ComplianceGateBlockError):  # C-002 闸抛转拒发
            _submit(om)
        assert broker.submit_order.call_count == calls_before  # 执行隔离：未触达 broker
        assert monitor.release_freeze(_SYM, operator="ops") is True
        _submit(om)  # 释放后放行
        assert broker.submit_order.call_count == calls_before + 1

    def test_unfrozen_symbol_passes_gate(self, monitor: ManipulationRealtimeMonitor) -> None:
        om, broker = _make_om(monitor)
        _submit(om, symbol="000001.SZ")
        assert broker.submit_order.call_count == 1

    def test_monitor_failure_fail_closed(self, monitor: ManipulationRealtimeMonitor) -> None:
        om, _ = _make_om(monitor)
        monitor.is_frozen = MagicMock(side_effect=RuntimeError("boom"))  # type: ignore[method-assign]
        with pytest.raises(ComplianceGateBlockError):
            _submit(om)

    def test_callback_exception_isolated(self, monitor: ManipulationRealtimeMonitor) -> None:
        om, broker = _make_om(monitor)
        om.register_order_event_callback(MagicMock(side_effect=RuntimeError("bad cb")))
        _submit(om)  # 回调异常不阻断订单主链
        assert broker.submit_order.call_count == 1

    def test_fill_callback_wash_trade_path(self, detector: TradingComplianceDetector, logger: ComplianceLogger) -> None:
        m = ManipulationRealtimeMonitor(detector, logger=logger, own_account="ACC1",
                                        counterparty_resolver=lambda f: "ACC1")
        om, broker = _make_om(m)
        oid = _submit(om, qty=100)
        fill_cb = broker.register_fill_callback.call_args.args[0]  # 券商侧回报通道
        fill_cb(Fill(fill_id="f1", fill_price=Decimal("10.0"), fill_timestamp=datetime.now(UTC),
                     filled_quantity=Decimal(100), idempotency_key="k1", order_id=oid, strategy_id="a8", symbol=_SYM))
        assert m.is_frozen(_SYM)  # 对手方=本方 → 自成交命中

    def test_normal_fill_no_false_positive(self, detector: TradingComplianceDetector, logger: ComplianceLogger) -> None:
        m = ManipulationRealtimeMonitor(detector, logger=logger, own_account="ACC1")
        om, broker = _make_om(m)
        oid = _submit(om, qty=100)
        broker.register_fill_callback.call_args.args[0](
            Fill(fill_id="f2", fill_price=Decimal("10.0"), fill_timestamp=datetime.now(UTC),
                 filled_quantity=Decimal(100), idempotency_key="k2", order_id=oid, strategy_id="a8", symbol=_SYM))
        assert not m.is_frozen(_SYM)  # 对手方未知占位相异 → 不误判


# ── RedisTickMarketProvider（tick 流消费通道） ──


class _FakeRedis:
    def __init__(self, data: dict | None = None, exc: Exception | None = None) -> None:
        self._data = data or {}
        self._exc = exc

    def hgetall(self, key):
        if self._exc is not None:
            raise self._exc
        return self._data.get(key, {})


def _tick_hash(price: str, volume: str) -> dict:
    return {tick_latest_key(_SYM): {"price": price, "volume": volume}}


class TestRedisTickMarketProvider:
    def test_minute_avg_volume(self) -> None:
        provider = RedisTickMarketProvider(_FakeRedis(_tick_hash("10.5", "120000")),
                                           clock=lambda: datetime(2026, 8, 28, 10, 30))
        assert provider.minute_avg_volume(_SYM) == pytest.approx(2000.0)  # 120000/60min

    def test_symbol_normalization_bare_and_suffix(self) -> None:
        redis = _FakeRedis(_tick_hash("10.5", "60000"))
        provider = RedisTickMarketProvider(redis, clock=lambda: datetime(2026, 8, 28, 10, 30))
        assert provider.minute_avg_volume("600000") == pytest.approx(1000.0)  # 裸码归一→SH
        assert provider.minute_avg_volume(_SYM) == pytest.approx(1000.0)

    def test_missing_or_bad_tick_degrades(self) -> None:
        clock = lambda: datetime(2026, 8, 28, 10, 30)
        assert RedisTickMarketProvider(_FakeRedis(), clock=clock).minute_avg_volume(_SYM) == 0.0
        assert RedisTickMarketProvider(_FakeRedis(exc=ConnectionError()), clock=clock).minute_avg_volume(_SYM) == 0.0
        assert RedisTickMarketProvider(_FakeRedis(), clock=clock).market_window(_SYM) is None
        assert RedisTickMarketProvider(_FakeRedis(), clock=clock).minute_avg_volume("AAPL") == 0.0  # 无法归一

    def test_non_trading_hours_zero(self) -> None:
        redis = _FakeRedis(_tick_hash("10.5", "120000"))
        assert RedisTickMarketProvider(redis, clock=lambda: datetime(2026, 8, 28, 9, 0)).minute_avg_volume(_SYM) == 0.0
        assert RedisTickMarketProvider(redis, clock=lambda: datetime(2026, 8, 28, 12, 0)).minute_avg_volume(_SYM) == pytest.approx(1000.0)

    def test_market_window_accumulates(self) -> None:
        redis = _FakeRedis(_tick_hash("10.0", "100000"))
        mono = [1000.0]
        provider = RedisTickMarketProvider(redis, mono=lambda: mono[0])
        assert provider.market_window(_SYM) is None  # 冷启动单观测 → None
        mono[0] += 60
        redis._data = _tick_hash("10.5", "110000")
        window = provider.market_window(_SYM)
        assert window is not None
        assert window.price_change_pct == pytest.approx(0.05)
        assert window.window_volume == pytest.approx(10000.0)

    def test_market_window_trims_old(self) -> None:
        redis = _FakeRedis(_tick_hash("10.0", "100000"))
        mono = [1000.0]
        provider = RedisTickMarketProvider(redis, mono=lambda: mono[0])
        provider.market_window(_SYM)
        mono[0] += 400  # 超 300s 窗 → 旧观测被 trim
        window = provider.market_window(_SYM)
        assert window is None  # 仅剩新观测


# ── 集成冒烟：模拟盘中事件流 ──


class TestIntegrationSmoke:
    def test_simulated_stream_end_to_end(self, detector: TradingComplianceDetector, logger: ComplianceLogger) -> None:
        redis = _FakeRedis(_tick_hash("10.0", "120000"))
        mono = [1000.0]
        provider = RedisTickMarketProvider(redis, clock=lambda: datetime(2026, 8, 28, 10, 30), mono=lambda: mono[0])
        m = ManipulationRealtimeMonitor(detector, minute_volume_provider=provider.minute_avg_volume,
                                        market_window_provider=provider.market_window, logger=logger)
        om, broker = _make_om(m)

        # 流 1：600000.SH 挂撤 3 轮 → Spoofing 冻结 + C-002 拒发
        for _ in range(3):
            om.cancel_order(_submit(om))
        assert m.is_frozen(_SYM)
        with pytest.raises(ComplianceGateBlockError):
            _submit(om)

        # 流 2：000001.SZ 干净标的正常通行（多标的隔离）
        clean = "000001.SZ"
        redis._data[tick_latest_key(clean)] = {"price": "20.0", "volume": "50000"}
        _submit(om, qty=100, symbol=clean)
        assert not m.is_frozen(clean)

        # 证据链完整：VERDICT（detector）+ ALERT（monitor）+ 事件源可溯
        events = logger.read_all()
        assert any(r.event_type == "MANIPULATION_VERDICT" for r in events)
        assert any(r.event_type == "MANIPULATION_REALTIME_ALERT" and r.payload["symbol"] == _SYM for r in events)
        assert all(r.event_type != "MANIPULATION_REALTIME_ALERT" or r.payload["symbol"] != clean for r in events)
