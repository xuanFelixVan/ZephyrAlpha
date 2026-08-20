# [BLUEPRINT] MOD-SIM-025 | docs/03_modules/_domain_simulation/blueprint.md
# [A_module] module_id=MOD-SIM-025 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [A_test] module_id: MOD-SIM-025 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.simulation.test_limit_board_queue
# [DOMAIN] D_SIMULATION
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/simulation/test_limit_board_queue.py
# [TTL] task_bound
"""BM-SIM-08 Paper Matching 涨跌停排队引擎单元测试(53号 §3.2 Step②).

覆盖: 板态判定(涨停/跌停/正常/0.01取整)、封板路由(同向排队/逆向即成交/
市价转限价)、成交概率公式②、FIFO队列(时间优先/部分成交/队首留存)、
参数校验与退化。
"""

from __future__ import annotations

import pytest

from zephyr.simulation.limit_board_queue import (
    BoardState,
    LimitBoardQueue,
    LimitBoardQueueError,
    OrderSide,
    OrderType,
    RouteAction,
    detect_board_state,
    estimate_fill_probability,
    limit_down_price,
    limit_up_price,
    route_order,
)


# ============== 板态判定 ==============


class TestDetectBoardState:
    def test_limit_up(self):
        assert detect_board_state(11.0, 10.0, 0.10) is BoardState.LIMIT_UP

    def test_limit_down(self):
        assert detect_board_state(9.0, 10.0, 0.10) is BoardState.LIMIT_DOWN

    def test_normal(self):
        assert detect_board_state(10.5, 10.0, 0.10) is BoardState.NORMAL

    def test_tick_rounding(self):
        # 10.05*1.1=11.055 → 0.01取整 11.06(四舍五入到分)
        assert limit_up_price(10.05, 0.10) == 11.06
        assert limit_down_price(10.05, 0.10) == pytest.approx(9.05)

    def test_chinext_20pct(self):
        assert detect_board_state(12.0, 10.0, 0.20) is BoardState.LIMIT_UP
        assert detect_board_state(11.0, 10.0, 0.20) is BoardState.NORMAL

    def test_invalid_inputs(self):
        with pytest.raises(LimitBoardQueueError):
            detect_board_state(11.0, 0.0)
        with pytest.raises(LimitBoardQueueError):
            detect_board_state(0.0, 10.0)
        with pytest.raises(LimitBoardQueueError):
            detect_board_state(11.0, 10.0, 1.5)


# ============== 封板路由 ==============


class TestRouteOrder:
    def test_normal_passthrough(self):
        r = route_order(OrderSide.BUY, 100, BoardState.NORMAL, limit_price=11.0)
        assert r.action is RouteAction.FILLED
        assert r.fill_price is None  # 正常态委托既有撮合链路

    def test_limit_up_buy_queued(self):
        r = route_order(OrderSide.BUY, 100, BoardState.LIMIT_UP, 11.0, queue_ahead=5000)
        assert r.action is RouteAction.QUEUED
        assert r.queue_ahead == 5000

    def test_limit_up_sell_filled_immediately(self):
        r = route_order(OrderSide.SELL, 100, BoardState.LIMIT_UP, 11.0)
        assert r.action is RouteAction.FILLED
        assert r.fill_price == 11.0
        assert r.fill_qty == 100

    def test_limit_down_sell_queued(self):
        r = route_order(OrderSide.SELL, 200, BoardState.LIMIT_DOWN, 9.0)
        assert r.action is RouteAction.QUEUED

    def test_limit_down_buy_filled_immediately(self):
        r = route_order(OrderSide.BUY, 200, BoardState.LIMIT_DOWN, 9.0)
        assert r.action is RouteAction.FILLED
        assert r.fill_price == 9.0

    def test_market_order_at_limit_converted(self):
        r = route_order(OrderSide.BUY, 100, BoardState.LIMIT_UP, 11.0, order_type=OrderType.MARKET)
        assert r.action is RouteAction.CONVERTED_QUEUED
        assert "转限价" in r.reason

    def test_invalid_inputs(self):
        with pytest.raises(LimitBoardQueueError):
            route_order("BUY", 100, BoardState.NORMAL, 11.0)
        with pytest.raises(LimitBoardQueueError):
            route_order(OrderSide.BUY, 0, BoardState.NORMAL, 11.0)
        with pytest.raises(LimitBoardQueueError):
            route_order(OrderSide.BUY, 100, BoardState.LIMIT_UP, 0.0)
        with pytest.raises(LimitBoardQueueError):
            route_order(OrderSide.BUY, 100, BoardState.LIMIT_UP, 11.0, queue_ahead=-1)


# ============== 成交概率公式② ==============


class TestEstimateFillProbability:
    def test_formula(self):
        # min(1, 1000/(4000+1000)) = 0.2
        assert estimate_fill_probability(4000, 1000, 1000) == pytest.approx(0.2)

    def test_full_fill_when_counter_covers(self):
        assert estimate_fill_probability(100, 100, 500) == 1.0

    def test_zero_counter_volume(self):
        assert estimate_fill_probability(1000, 500, 0) == 0.0

    def test_thin_queue_experience(self):
        # 经验阈值: queue>1000手(100,000股)且对手盘小 → P<10%
        p = estimate_fill_probability(100_001, 100, 10_000)
        assert p < 0.10

    def test_invalid(self):
        with pytest.raises(LimitBoardQueueError):
            estimate_fill_probability(-1, 100, 100)
        with pytest.raises(LimitBoardQueueError):
            estimate_fill_probability(0, 0, 100)
        with pytest.raises(LimitBoardQueueError):
            estimate_fill_probability(0, 100, -1)


# ============== FIFO 队列 ==============


class TestLimitBoardQueue:
    def _queue(self) -> LimitBoardQueue:
        return LimitBoardQueue(board_state=BoardState.LIMIT_UP, limit_price=11.0)

    def test_enqueue_time_priority(self):
        q = self._queue()
        o1 = q.enqueue("o1", OrderSide.BUY, 100)
        o2 = q.enqueue("o2", OrderSide.BUY, 200)
        assert o1.seq < o2.seq
        assert q.total_queued == 300
        assert q.n_orders == 2

    def test_wrong_side_rejected(self):
        q = self._queue()
        with pytest.raises(LimitBoardQueueError):
            q.enqueue("o1", OrderSide.SELL, 100)  # 涨停队列只接受BUY

    def test_normal_state_queue_rejected(self):
        with pytest.raises(LimitBoardQueueError):
            LimitBoardQueue(board_state=BoardState.NORMAL, limit_price=11.0)

    def test_queue_ahead_of(self):
        q = self._queue()
        q.enqueue("o1", OrderSide.BUY, 100)
        q.enqueue("o2", OrderSide.BUY, 200)
        q.enqueue("o3", OrderSide.BUY, 300)
        assert q.queue_ahead_of("o3") == 300
        assert q.queue_ahead_of("o1") == 0
        assert q.queue_ahead_of("ghost") == -1

    def test_counter_volume_fifo_fill(self):
        q = self._queue()
        q.enqueue("o1", OrderSide.BUY, 100)
        q.enqueue("o2", OrderSide.BUY, 200)
        fills = q.on_counter_volume(250)
        # o1 全成, o2 部分成交150留存50
        assert fills == [("o1", 100, 11.0), ("o2", 150, 11.0)]
        assert q.total_queued == 50
        assert q.n_orders == 1

    def test_partial_fill_head_stays(self):
        q = self._queue()
        q.enqueue("o1", OrderSide.BUY, 300)
        fills = q.on_counter_volume(100)
        assert fills == [("o1", 100, 11.0)]
        assert q.queue_ahead_of("o1") == 0
        assert q.total_queued == 200

    def test_counter_volume_exceeds_queue(self):
        q = self._queue()
        q.enqueue("o1", OrderSide.BUY, 100)
        fills = q.on_counter_volume(500)
        assert fills == [("o1", 100, 11.0)]
        assert q.n_orders == 0

    def test_zero_counter_volume_noop(self):
        q = self._queue()
        q.enqueue("o1", OrderSide.BUY, 100)
        assert q.on_counter_volume(0) == []
        assert q.total_queued == 100

    def test_negative_volume_raises(self):
        q = self._queue()
        with pytest.raises(LimitBoardQueueError):
            q.on_counter_volume(-1)

    def test_limit_down_queue_accepts_sell(self):
        q = LimitBoardQueue(board_state=BoardState.LIMIT_DOWN, limit_price=9.0)
        o = q.enqueue("s1", OrderSide.SELL, 100)
        assert o.side is OrderSide.SELL
        with pytest.raises(LimitBoardQueueError):
            q.enqueue("b1", OrderSide.BUY, 100)
