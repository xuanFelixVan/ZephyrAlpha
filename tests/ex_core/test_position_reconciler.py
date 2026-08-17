# [BLUEPRINT] MOD-EX-056 | docs/03_modules/_domain_execution_core/position_reconciler/blueprint.md
# [MODULE] tests.ex_core.test_position_reconciler
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.position_reconciler; zephyr.ex_core.position_tracker.tracker
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-EX-056 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""PositionReconciler 单元测试 — D-EX-CORE-56 盘中持仓对账器。

覆盖蓝图 §7 测试计划全部 11 项用例：
双源比对/差异检测/冻结解冻/容差/on_drift回调/多标的混合/线程安全/真实对象集成。
"""
from __future__ import annotations

import threading
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from zephyr.ex_core.position_reconciler import (
    DriftItem,
    PositionReconciler,
    ReconcileResult,
)
from zephyr.ex_core.position_tracker.tracker import PositionTracker
from zephyr.shared.contracts.position import PositionSnapshot

# ── helpers ──


def make_snapshot(holdings: dict[str, Decimal], cash: Decimal = Decimal("1000000")) -> PositionSnapshot:
    """构造一个带 holdings 的 PositionSnapshot（测试用）。"""
    return PositionSnapshot(
        as_of_timestamp=datetime.now(UTC),
        idempotency_key="test-key",
        portfolio_id="test-portfolio",
        cash=cash,
        holdings=dict(holdings),
        market_values={},
        total_market_value=Decimal("0"),
    )


class FakeSource:
    """可编程的 PositionSource —— 预设 holdings 供对账读取。"""

    def __init__(self, holdings: dict[str, Decimal] | None = None) -> None:
        self._holdings = dict(holdings) if holdings else {}

    def set_holdings(self, holdings: dict[str, Decimal]) -> None:
        self._holdings = dict(holdings)

    def get_positions(self) -> PositionSnapshot:
        return make_snapshot(self._holdings)


# ── 1. 两源完全一致 ──


def test_matched_when_identical():
    sys_src = FakeSource({"600000.SH": Decimal("100"), "000001.SZ": Decimal("200")})
    brk_src = FakeSource({"600000.SH": Decimal("100"), "000001.SZ": Decimal("200")})
    rec = PositionReconciler(sys_src, brk_src)

    result = rec.reconcile()

    assert result.matched is True
    assert result.drifts == ()
    assert result.frozen_symbols == frozenset()
    assert result.newly_frozen == frozenset()
    assert result.newly_unfrozen == frozenset()


# ── 2. 系统多记 ──


def test_drift_when_system_overcount():
    sys_src = FakeSource({"600000.SH": Decimal("110")})
    brk_src = FakeSource({"600000.SH": Decimal("100")})
    rec = PositionReconciler(sys_src, brk_src)

    result = rec.reconcile()

    assert result.matched is False
    assert len(result.drifts) == 1
    d = result.drifts[0]
    assert d.symbol == "600000.SH"
    assert d.system_qty == Decimal("110")
    assert d.broker_qty == Decimal("100")
    assert d.diff == Decimal("10")
    assert result.frozen_symbols == frozenset({"600000.SH"})
    assert result.newly_frozen == frozenset({"600000.SH"})


# ── 3. 系统少记 ──


def test_drift_when_system_undercount():
    sys_src = FakeSource({"600000.SH": Decimal("90")})
    brk_src = FakeSource({"600000.SH": Decimal("100")})
    rec = PositionReconciler(sys_src, brk_src)

    result = rec.reconcile()

    assert result.matched is False
    d = result.drifts[0]
    assert d.diff == Decimal("-10")
    assert result.frozen_symbols == frozenset({"600000.SH"})


# ── 4. 标的仅在一源（缺方按 0）──


def test_drift_when_symbol_only_in_one_source():
    # 系统有，broker 无
    sys_src = FakeSource({"600000.SH": Decimal("100")})
    brk_src = FakeSource({})
    rec = PositionReconciler(sys_src, brk_src)

    result = rec.reconcile()
    assert result.matched is False
    d = result.drifts[0]
    assert d.symbol == "600000.SH"
    assert d.system_qty == Decimal("100")
    assert d.broker_qty == Decimal("0")
    assert d.diff == Decimal("100")

    # 反向：broker 有，系统无
    rec2 = PositionReconciler(FakeSource({}), FakeSource({"000001.SZ": Decimal("50")}))
    r2 = rec2.reconcile()
    assert r2.matched is False
    assert r2.drifts[0].symbol == "000001.SZ"
    assert r2.drifts[0].system_qty == Decimal("0")
    assert r2.drifts[0].broker_qty == Decimal("50")


# ── 5. 容差非零 ──


def test_tolerance_filters_small_diff():
    sys_src = FakeSource({"600000.SH": Decimal("100.005")})
    brk_src = FakeSource({"600000.SH": Decimal("100.000")})
    rec = PositionReconciler(sys_src, brk_src, tolerance=Decimal("0.01"))

    result = rec.reconcile()
    assert result.matched is True
    assert result.drifts == ()

    # diff 超过容差则记 drift
    rec_strict = PositionReconciler(sys_src, brk_src, tolerance=Decimal("0.001"))
    r2 = rec_strict.reconcile()
    assert r2.matched is False
    assert len(r2.drifts) == 1


# ── 6. 冻结→解冻（修正后恢复一致）──


def test_freeze_then_unfreeze_on_recovery():
    sys_src = FakeSource({"600000.SH": Decimal("110")})
    brk_src = FakeSource({"600000.SH": Decimal("100")})
    rec = PositionReconciler(sys_src, brk_src)

    r1 = rec.reconcile()
    assert r1.matched is False
    assert rec.is_frozen("600000.SH")
    assert r1.newly_frozen == frozenset({"600000.SH"})
    assert r1.newly_unfrozen == frozenset()

    # 修正系统账 → 两源一致
    sys_src.set_holdings({"600000.SH": Decimal("100")})
    r2 = rec.reconcile()
    assert r2.matched is True
    assert not rec.is_frozen("600000.SH")
    assert r2.newly_frozen == frozenset()
    assert r2.newly_unfrozen == frozenset({"600000.SH"})


# ── 7. newly_frozen / newly_unfrozen 增量正确 ──


def test_incremental_freeze_unfreeze():
    sys_src = FakeSource({"A": Decimal("10"), "B": Decimal("20"), "C": Decimal("30")})
    brk_src = FakeSource({"A": Decimal("10"), "B": Decimal("20"), "C": Decimal("30")})
    rec = PositionReconciler(sys_src, brk_src)

    # 第一次：B 和 C 漂移
    sys_src.set_holdings({"A": Decimal("10"), "B": Decimal("25"), "C": Decimal("40")})
    r1 = rec.reconcile()
    assert r1.newly_frozen == frozenset({"B", "C"})
    assert r1.newly_unfrozen == frozenset()

    # 第二次：B 恢复，C 仍漂移，D 新增漂移
    sys_src.set_holdings({"A": Decimal("10"), "B": Decimal("20"), "C": Decimal("40"), "D": Decimal("99")})
    r2 = rec.reconcile()
    assert r2.newly_frozen == frozenset({"D"})
    assert r2.newly_unfrozen == frozenset({"B"})
    assert r2.frozen_symbols == frozenset({"C", "D"})


# ── 8. on_drift 回调 ──


def test_on_drift_called_when_mismatch():
    calls: list[ReconcileResult] = []
    sys_src = FakeSource({"A": Decimal("10")})
    brk_src = FakeSource({"A": Decimal("5")})
    rec = PositionReconciler(sys_src, brk_src, on_drift=lambda r: calls.append(r))

    rec.reconcile()
    assert len(calls) == 1
    assert calls[0].matched is False


def test_on_drift_not_called_when_matched():
    calls: list[ReconcileResult] = []
    src = FakeSource({"A": Decimal("10")})
    rec = PositionReconciler(src, FakeSource({"A": Decimal("10")}), on_drift=lambda r: calls.append(r))

    rec.reconcile()
    assert calls == []


def test_on_drift_exception_does_not_block_reconcile():
    def bad_callback(_r: ReconcileResult) -> None:
        raise RuntimeError("alert channel down")

    sys_src = FakeSource({"A": Decimal("10")})
    brk_src = FakeSource({"A": Decimal("5")})
    rec = PositionReconciler(sys_src, brk_src, on_drift=bad_callback)

    # 回调抛异常，但 reconcile 仍正常返回结果
    result = rec.reconcile()
    assert result.matched is False
    assert len(result.drifts) == 1


# ── 9. 多标的混合（部分一致部分漂移）──


def test_mixed_symbols_partial_match():
    sys_src = FakeSource({
        "A": Decimal("100"),   # 一致
        "B": Decimal("200"),   # 漂移（系统多）
        "C": Decimal("300"),   # 一致
        "D": Decimal("400"),   # 漂移（系统少）
    })
    brk_src = FakeSource({
        "A": Decimal("100"),
        "B": Decimal("150"),
        "C": Decimal("300"),
        "D": Decimal("450"),
    })
    rec = PositionReconciler(sys_src, brk_src)

    result = rec.reconcile()
    assert result.matched is False
    drift_symbols = {d.symbol for d in result.drifts}
    assert drift_symbols == {"B", "D"}
    assert result.frozen_symbols == frozenset({"B", "D"})
    # A 和 C 未冻结
    assert not rec.is_frozen("A")
    assert not rec.is_frozen("C")
    assert rec.is_frozen("B")
    assert rec.is_frozen("D")


# ── 10. 线程安全（并发 reconcile + is_frozen）──


def test_thread_safety_concurrent_reconcile_and_is_frozen():
    sys_src = FakeSource({"A": Decimal("10")})
    brk_src = FakeSource({"A": Decimal("10")})
    rec = PositionReconciler(sys_src, brk_src)

    errors: list[Exception] = []
    barrier = threading.Barrier(4)

    def worker() -> None:
        try:
            barrier.wait()
            for _ in range(200):
                rec.reconcile()
                rec.is_frozen("A")
                _ = rec.frozen_symbols
        except Exception as e:  # noqa: BLE001
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == []
    # 一致状态下不应有冻结
    assert not rec.is_frozen("A")


# ── 11. PositionTracker / SimulationBroker 集成（真实对象作 source）──


def test_integration_with_position_tracker_as_system_source():
    """PositionTracker 作为系统账 source，FakeSource 模拟 broker 账。

    验证 PositionReconciler 能消费 PositionTracker.get_positions() 产出的
    PositionSnapshot（CTR-006）。
    """
    from datetime import datetime

    from zephyr.shared.contracts.enums.order_enums import OrderSide
    from zephyr.shared.contracts.fill import Fill

    tracker = PositionTracker(initial_cash=Decimal("1000000"))
    fill = Fill(
        fill_id="f1",
        fill_price=Decimal("10"),
        fill_timestamp=datetime.now(UTC),
        filled_quantity=Decimal("100"),
        idempotency_key="k1",
        order_id="o1",
        strategy_id="s1",
        symbol="600000.SH",
    )
    tracker.apply_fill(fill, OrderSide.BUY)

    # broker 账与系统一致
    broker_src = FakeSource({"600000.SH": Decimal("100")})
    rec = PositionReconciler(tracker, broker_src)
    result = rec.reconcile()
    assert result.matched is True

    # broker 账不一致（少了 10 股）
    broker_src.set_holdings({"600000.SH": Decimal("90")})
    result2 = rec.reconcile()
    assert result2.matched is False
    assert rec.is_frozen("600000.SH")


def test_manual_unfreeze():
    sys_src = FakeSource({"A": Decimal("10")})
    brk_src = FakeSource({"A": Decimal("5")})
    rec = PositionReconciler(sys_src, brk_src)

    rec.reconcile()
    assert rec.is_frozen("A")

    rec.unfreeze("A")
    assert not rec.is_frozen("A")

    # 但下次 reconcile 若仍有 drift，会重新冻结
    rec.reconcile()
    assert rec.is_frozen("A")


def test_reconcile_does_not_mutate_sources():
    sys_src = FakeSource({"A": Decimal("10")})
    brk_src = FakeSource({"A": Decimal("5")})
    rec = PositionReconciler(sys_src, brk_src)

    rec.reconcile()

    # source 的 holdings 不应被修改（reconcile 是纯读比对）
    assert sys_src._holdings == {"A": Decimal("10")}
    assert brk_src._holdings == {"A": Decimal("5")}


def test_drift_item_is_frozen():
    d = DriftItem("A", Decimal("10"), Decimal("5"), Decimal("5"))
    with pytest.raises(AttributeError):
        d.symbol = "B"  # type: ignore[misc]


def test_reconcile_result_is_frozen():
    r = ReconcileResult(
        timestamp=datetime.now(UTC),
        matched=True,
        drifts=(),
        frozen_symbols=frozenset(),
        newly_frozen=frozenset(),
        newly_unfrozen=frozenset(),
    )
    with pytest.raises(AttributeError):
        r.matched = False  # type: ignore[misc]
