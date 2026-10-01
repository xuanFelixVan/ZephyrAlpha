# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain_risk/risk-management-core/blueprint.md | §清算 T+1 分桶
# [MODULE] tests.risk.test_kill_switch_t1_bucket
# [DOMAIN] D_RISK
# [DEPENDENCIES] pytest; zephyr.risk.stop_loss
# [CONSUMERS] ARCH-127 清算链 T+1 分桶质量守卫（execute_kill_switch_liquidation）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 测试禁写生产路径——假 broker 注入可用量，state_store 走 tmp_path
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest 断言失败即红
# [TESTS] self
# [TTL] task_bound
# [TEST] tests/risk/test_kill_switch_t1_bucket.py
# 覆盖（ARCH-127 验收）：部分锁定分桶/全锁定零发单/全可卖满额清/空头回补不分桶/
#   broker 无可卖量能力=既有全量行为/可卖量探测异常降级/柜台镜像 holdings 形态。
# 铁律：不连真实券商、不写 data/，JsonStateStore 全部 tmp_path。
from __future__ import annotations

from zephyr.risk.stop_loss import execute_kill_switch_liquidation
from zephyr.shared.state_store import JsonStateStore

# ── 测试替身 ──


class _FakeBroker:
    """无实时查询能力的 broker（兜底快照路径）。"""

    def __init__(self, available: dict[str, float] | None = None):
        self.placed_orders: list[dict] = []
        self._available = available or {}

    def cancel_order(self, order_id: str) -> None:
        pass

    def place_order(self, symbol: str, direction: str, qty: float, order_type: str) -> None:
        self.placed_orders.append({"symbol": symbol, "direction": direction, "qty": qty, "order_type": order_type})

    def available_qty(self, symbol: str) -> float:
        return self._available.get(symbol, 0.0)


def _run(broker, positions: dict, tmp_path) -> dict:
    return execute_kill_switch_liquidation(
        broker,
        positions,
        open_orders={},
        scope="position",
        max_orders_per_second=15,
        state_store=JsonStateStore(tmp_path),
    )


# ── T+1 分桶核心语义 ──


class TestT1Bucketing:
    def test_partial_locked_sold_and_rejected_buckets(self, tmp_path):
        """部分锁定：可卖 400/持仓 1000 → 发 SELL 400，锁定 600 进 t_plus_1_rejected，不计失败。"""
        broker = _FakeBroker(available={"510300.SH": 400.0})
        report = _run(broker, {"510300.SH": 1000}, tmp_path)
        assert report["status"] == "executed"
        assert len(broker.placed_orders) == 1
        assert broker.placed_orders[0]["qty"] == 400
        assert broker.placed_orders[0]["direction"] == "SELL"
        assert report["liquidation_orders"] == ["510300.SH"]
        assert report["t_plus_1_rejected"] == [("510300.SH", 600.0)]
        assert report["all_success"] is True

    def test_fully_locked_no_order_placed(self, tmp_path):
        """全锁定（当日买入）：available=0 → 零发单，全量进 t_plus_1_rejected，all_success=True。"""
        broker = _FakeBroker(available={})  # available_qty 缺省返回 0
        report = _run(broker, {"510300.SH": 1000}, tmp_path)
        assert broker.placed_orders == []
        assert report["liquidation_orders"] == []
        assert report["t_plus_1_rejected"] == [("510300.SH", 1000.0)]
        assert report["all_success"] is True

    def test_fully_available_full_qty_sold(self, tmp_path):
        """可卖量 >= 持仓：满额发单，零锁定残留。"""
        broker = _FakeBroker(available={"510300.SH": 1000.0})
        report = _run(broker, {"510300.SH": 1000}, tmp_path)
        assert broker.placed_orders[0]["qty"] == 1000
        assert report["t_plus_1_rejected"] == []
        assert report["all_success"] is True

    def test_short_cover_not_t1_bucketed(self, tmp_path):
        """空头回补（qty<0 → BUY）：无 T+1 约束，全量发单不进锁定桶。"""
        broker = _FakeBroker(available={"IF2512.CFE": 0.0})
        report = _run(broker, {"IF2512.CFE": -5}, tmp_path)
        assert len(broker.placed_orders) == 1
        assert broker.placed_orders[0]["direction"] == "BUY"
        assert broker.placed_orders[0]["qty"] == 5
        assert report["t_plus_1_rejected"] == []
        assert report["all_success"] is True


# ── 能力降级边界 ──


class TestAvailabilityFallback:
    def test_broker_without_capability_full_qty_legacy(self, tmp_path):
        """broker 无 available_qty 能力（无 get_holdings）→ 按可卖量未知全量发单（既有行为）。"""
        broker = _FakeBroker()
        broker.available_qty = None  # 摘掉能力探针（非 callable=无能力）
        report = _run(broker, {"510300.SH": 800}, tmp_path)
        assert broker.placed_orders[0]["qty"] == 800
        assert report["t_plus_1_rejected"] == []

    def test_available_qty_probe_raises_fallback_full_qty(self, tmp_path):
        """可卖量探测抛异常 → 降级全量发单（探测失败不阻断清算）。"""

        class _RaisingBroker(_FakeBroker):
            def available_qty(self, symbol: str) -> float:
                raise RuntimeError("counter mirror unavailable")

        broker = _RaisingBroker()
        report = _run(broker, {"510300.SH": 800}, tmp_path)
        assert broker.placed_orders[0]["qty"] == 800
        assert report["t_plus_1_rejected"] == []

    def test_holdings_mirror_available_qty_field(self, tmp_path):
        """柜台镜像形态：get_holdings() 行内 available_qty 字段为可卖量真源（无 available_qty 方法）。"""
        broker = _FakeBroker()
        broker.available_qty = None  # 摘掉能力探针（非 callable=无能力）
        broker.get_holdings = lambda: {"510300.SH": {"qty": 1000, "available_qty": 250}}  # type: ignore[attr-defined]
        report = _run(broker, {"510300.SH": 1000}, tmp_path)
        assert broker.placed_orders[0]["qty"] == 250
        assert report["t_plus_1_rejected"] == [("510300.SH", 750.0)]
        assert report["all_success"] is True
