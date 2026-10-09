# [BLUEPRINT] MOD-DT-001 | docs/03_modules/_domain_digital_twin/market_twin_simulator/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-DT-001 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.digital_twin.test_market_twin_simulator
# [TESTS] src/zephyr/digital_twin/market_twin_simulator.py
"""MOD-DT-001 单元测试：market_twin_simulator 数字孪生市场仿真（Phase1 规则 ABM）。

蓝图验收（B10-01864/CAND-DIGITALT-001，A1 §29.23）：
BDI 规则库注入（信念→愿望→意图）+ 限价/市价/集合竞价三模式撮合 +
情绪传染（邻接注入同步更新）+ 统计特征校验（波动率聚集/肥尾/量自相关，
注入统计器）+ simulated=True 硬标注 + 审计回调。全内存替身，不触网。
"""

from __future__ import annotations

import datetime
import math

import pytest

pytest.importorskip(
    "zephyr.digital_twin.market_twin_simulator",
    reason="market_twin_simulator not importable",
)

from zephyr.digital_twin.market_twin_simulator import (  # noqa: E402
    AuditEvent,
    BDIRuleBook,
    MarketTwinError,
    MarketTwinSimulator,
    MatchMode,
    Order,
    OrderSide,
    OrderType,
    StylizedFactReport,
    Trade,
    TwinAgent,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _sim(**kw) -> MarketTwinSimulator:
    kw.setdefault("initial_price", 100.0)
    kw.setdefault("clock", lambda: _T0)
    return MarketTwinSimulator(**kw)


def _agent(agent_id: str, cash: float = 0.0, position: int = 0, sentiment: float = 0.0) -> TwinAgent:
    return TwinAgent(agent_id=agent_id, cash=cash, position=position, sentiment=sentiment)


def _limit(oid: str, agent: str, side: OrderSide, price: float, qty: int) -> Order:
    return Order(order_id=oid, agent_id=agent, side=side, order_type=OrderType.LIMIT, price=price, quantity=qty)


def _market(oid: str, agent: str, side: OrderSide, qty: int) -> Order:
    return Order(order_id=oid, agent_id=agent, side=side, order_type=OrderType.MARKET, price=None, quantity=qty)


def _prices_from_returns(rets: list[float], p0: float = 100.0) -> list[float]:
    px = [p0]
    for r in rets:
        px.append(px[-1] * math.exp(r))
    return px


# ──────────────────────────────────────────────────────────────────────────────
# 智能体注册 / 构造守卫
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterAgent:
    def test_register_ok(self) -> None:
        sim = _sim()
        sim.register_agent(_agent("a", cash=1000.0, position=5))
        snap = sim.snapshot()
        assert snap.agents == (("a", 1000.0, 5, 0.0),)

    def test_register_empty_id_raises(self) -> None:
        with pytest.raises(MarketTwinError):
            _sim().register_agent(_agent(""))

    def test_register_duplicate_raises(self) -> None:
        sim = _sim()
        sim.register_agent(_agent("a"))
        with pytest.raises(MarketTwinError):
            sim.register_agent(_agent("a"))

    def test_register_negative_raises(self) -> None:
        sim = _sim()
        with pytest.raises(MarketTwinError):
            sim.register_agent(_agent("a", cash=-1.0))
        with pytest.raises(MarketTwinError):
            sim.register_agent(_agent("b", position=-1))


class TestConstructorGuard:
    def test_invalid_initial_price_and_weight_raise(self) -> None:
        with pytest.raises(MarketTwinError):
            _sim(initial_price=0.0)
        with pytest.raises(MarketTwinError):
            _sim(contagion_weight=1.5)


# ──────────────────────────────────────────────────────────────────────────────
# simulated=True 硬标注
# ──────────────────────────────────────────────────────────────────────────────


class TestHardLabel:
    def test_payloads_simulated_false_raise(self) -> None:
        with pytest.raises(MarketTwinError):
            Order(
                order_id="o",
                agent_id="a",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                price=None,
                quantity=1,
                simulated=False,
            )
        with pytest.raises(MarketTwinError):
            Trade(
                trade_id="t",
                buy_order_id="b",
                sell_order_id="s",
                buy_agent="x",
                sell_agent="y",
                price=1.0,
                quantity=1,
                mode=MatchMode.LIMIT,
                matched_at=_T0,
                simulated=False,
            )
        with pytest.raises(MarketTwinError):
            AuditEvent(kind="k", detail={}, raised_at=_T0, simulated=False)


# ──────────────────────────────────────────────────────────────────────────────
# 订单入簿
# ──────────────────────────────────────────────────────────────────────────────


class TestSubmitOrder:
    def test_submit_unknown_agent_raises(self) -> None:
        with pytest.raises(MarketTwinError):
            _sim().submit_order(_market("m1", "ghost", OrderSide.BUY, 1))

    def test_submit_duplicate_id_raises(self) -> None:
        sim = _sim()
        sim.register_agent(_agent("a", cash=1e6))
        sim.submit_order(_limit("o1", "a", OrderSide.BUY, 100.0, 1))
        with pytest.raises(MarketTwinError):
            sim.submit_order(_limit("o1", "a", OrderSide.BUY, 100.0, 1))

    def test_price_validation(self) -> None:
        sim = _sim()
        sim.register_agent(_agent("a", cash=1e6))
        with pytest.raises(MarketTwinError):
            sim.submit_order(_limit("o1", "a", OrderSide.BUY, 0.0, 1))  # 限价非正价
        with pytest.raises(MarketTwinError):
            sim.submit_order(
                Order(
                    order_id="o2",
                    agent_id="a",
                    side=OrderSide.BUY,
                    order_type=OrderType.MARKET,
                    price=100.0,
                    quantity=1,
                )
            )  # 市价带价

    def test_bad_quantity_raises(self) -> None:
        sim = _sim()
        sim.register_agent(_agent("a", cash=1e6))
        with pytest.raises(MarketTwinError):
            sim.submit_order(_limit("o1", "a", OrderSide.BUY, 100.0, 0))


# ──────────────────────────────────────────────────────────────────────────────
# 限价连续竞价
# ──────────────────────────────────────────────────────────────────────────────


class TestLimitMatch:
    def _book(self) -> MarketTwinSimulator:
        sim = _sim()
        sim.register_agent(_agent("buyer", cash=1e6))
        sim.register_agent(_agent("seller", position=1000))
        return sim

    def test_cross_trade_passive_price_and_settlement(self) -> None:
        sim = self._book()
        sim.submit_order(_limit("s1", "seller", OrderSide.SELL, 99.5, 10))  # 先挂
        sim.submit_order(_limit("b1", "buyer", OrderSide.BUY, 100.0, 10))
        trades = sim.match(MatchMode.LIMIT)
        assert len(trades) == 1
        assert trades[0].price == 99.5  # 被动（先挂）方价格
        assert trades[0].quantity == 10
        assert trades[0].simulated is True
        snap = dict((a[0], a) for a in sim.snapshot().agents)
        assert snap["buyer"][1] == pytest.approx(1e6 - 995.0)
        assert snap["buyer"][2] == 10
        assert snap["seller"][1] == pytest.approx(995.0)
        assert snap["seller"][2] == 990
        assert sim.snapshot().last_price == 99.5

    def test_no_cross_no_trade(self) -> None:
        sim = self._book()
        sim.submit_order(_limit("s1", "seller", OrderSide.SELL, 99.5, 10))
        sim.submit_order(_limit("b1", "buyer", OrderSide.BUY, 99.0, 10))
        assert sim.match(MatchMode.LIMIT) == ()

    def test_price_time_priority(self) -> None:
        sim = self._book()
        sim.submit_order(_limit("s1", "seller", OrderSide.SELL, 100.0, 10))
        sim.submit_order(_limit("b1", "buyer", OrderSide.BUY, 101.0, 4))  # 低价先挂
        sim.submit_order(_limit("b2", "buyer", OrderSide.BUY, 102.0, 4))  # 高价后挂
        trades = sim.match(MatchMode.LIMIT)
        assert [t.buy_order_id for t in trades] == ["b2", "b1"]  # 价格优先
        assert all(t.price == 100.0 for t in trades)  # 被动方=先挂卖单

    def test_invalid_mode_raises(self) -> None:
        with pytest.raises(MarketTwinError):
            self._book().match("limit")


# ──────────────────────────────────────────────────────────────────────────────
# 市价吃簿
# ──────────────────────────────────────────────────────────────────────────────


class TestMarketMatch:
    def test_market_buy_eats_book_then_cancel_residual(self) -> None:
        sim = _sim()
        sim.register_agent(_agent("buyer", cash=1e6))
        sim.register_agent(_agent("seller", position=1000))
        sim.submit_order(_limit("s1", "seller", OrderSide.SELL, 100.0, 5))
        sim.submit_order(_limit("s2", "seller", OrderSide.SELL, 101.0, 5))
        sim.submit_order(_market("m1", "buyer", OrderSide.BUY, 8))
        trades = sim.match(MatchMode.MARKET)
        assert [(t.price, t.quantity) for t in trades] == [(100.0, 5), (101.0, 3)]
        # 限价剩余 2 留簿：下一轮市价单先吃残留，再吃空簿无成交
        sim.submit_order(_market("m2", "buyer", OrderSide.BUY, 8))
        sim.submit_order(_market("m3", "buyer", OrderSide.BUY, 2))
        trades2 = sim.match(MatchMode.MARKET)
        assert [(t.buy_order_id, t.price, t.quantity) for t in trades2] == [("m2", 101.0, 2)]

    def test_market_without_counterpart_no_trade(self) -> None:
        sim = _sim()
        sim.register_agent(_agent("buyer", cash=1e6))
        sim.submit_order(_market("m1", "buyer", OrderSide.BUY, 5))
        assert sim.match(MatchMode.MARKET) == ()
        assert sim.snapshot().agents[0][1] == pytest.approx(1e6)  # 现金未动


# ──────────────────────────────────────────────────────────────────────────────
# 集合竞价
# ──────────────────────────────────────────────────────────────────────────────


class TestCallAuction:
    def test_uniform_price_max_volume_tie_take_low(self) -> None:
        sim = _sim()
        sim.register_agent(_agent("b1", cash=1e6))
        sim.register_agent(_agent("b2", cash=1e6))
        sim.register_agent(_agent("s1", position=1000))
        sim.register_agent(_agent("s2", position=1000))
        sim.submit_order(_limit("ob1", "b1", OrderSide.BUY, 102.0, 10))
        sim.submit_order(_limit("ob2", "b2", OrderSide.BUY, 101.0, 10))
        sim.submit_order(_limit("os1", "s1", OrderSide.SELL, 99.0, 10))
        sim.submit_order(_limit("os2", "s2", OrderSide.SELL, 100.0, 10))
        trades = sim.match(MatchMode.CALL_AUCTION)
        # 出清量 20；价格 100/101 平局取低价 100
        assert sum(t.quantity for t in trades) == 20
        assert all(t.price == 100.0 for t in trades)
        assert all(t.mode is MatchMode.CALL_AUCTION for t in trades)


# ──────────────────────────────────────────────────────────────────────────────
# 情绪传染（邻接注入）
# ──────────────────────────────────────────────────────────────────────────────


class TestSentiment:
    def test_contagion_step_values(self) -> None:
        sim = _sim(adjacency={"x": ("y",), "y": ("x", "z")}, contagion_weight=0.5)
        sim.register_agent(_agent("x", sentiment=1.0))
        sim.register_agent(_agent("y", sentiment=0.0))
        sim.register_agent(_agent("z", sentiment=-1.0))
        out = sim.step_sentiment()
        assert out["x"] == pytest.approx(0.5)  # 0.5·1.0 + 0.5·0.0
        assert out["y"] == pytest.approx(0.0)  # 0.5·0.0 + 0.5·mean(1.0,-1.0)
        assert out["z"] == pytest.approx(-1.0)  # 无邻接不变

    def test_contagion_unknown_neighbor_raises(self) -> None:
        sim = _sim(adjacency={"x": ("ghost",)})
        sim.register_agent(_agent("x"))
        with pytest.raises(MarketTwinError):
            sim.step_sentiment()


# ──────────────────────────────────────────────────────────────────────────────
# BDI 运行（规则库注入）
# ──────────────────────────────────────────────────────────────────────────────


class TestRunRound:
    @staticmethod
    def _rules() -> BDIRuleBook:
        def intention(agent, desire, view, oid):
            diff = desire - agent.position
            if diff > 0:
                return Order(
                    order_id=oid,
                    agent_id=agent.agent_id,
                    side=OrderSide.BUY,
                    order_type=OrderType.LIMIT,
                    price=view.last_price * 1.05,
                    quantity=diff,
                )
            if diff < 0:
                return Order(
                    order_id=oid,
                    agent_id=agent.agent_id,
                    side=OrderSide.SELL,
                    order_type=OrderType.LIMIT,
                    price=view.last_price,
                    quantity=-diff,
                )
            return None

        return BDIRuleBook(
            belief_fn=lambda agent, view: view.last_price,  # 信念：公允价=最新价
            desire_fn=lambda agent, belief, view: 10 if agent.cash > 50000 else 0,  # 愿望：资金充裕→持仓10
            intention_fn=intention,  # 意图：差额→限价单
        )

    def test_run_round_bdi_pipeline(self) -> None:
        events: list[AuditEvent] = []
        sim = _sim(rules=self._rules(), audit_sink=events.append)
        sim.register_agent(_agent("buyer", cash=1e6))
        sim.register_agent(_agent("seller", cash=0.0, position=100))
        result = sim.run_round(MatchMode.LIMIT)
        assert result.round_no == 1
        assert result.orders_submitted == 2
        assert len(result.trades) == 1
        trade = result.trades[0]
        assert trade.quantity == 10
        assert trade.price == pytest.approx(105.0)  # 买方先挂（agent_id 排序）→ 被动价
        assert trade.simulated is True
        kinds = [e.kind for e in events]
        assert kinds.count("order_submitted") == 2
        assert "trade_matched" in kinds and "sentiment_step" in kinds and "round_done" in kinds
        assert all(e.simulated is True for e in events)

    def test_run_round_without_rules_fail_closed(self) -> None:
        sim = _sim()
        sim.register_agent(_agent("a", cash=1e6))
        with pytest.raises(MarketTwinError):
            sim.run_round()


# ──────────────────────────────────────────────────────────────────────────────
# 统计特征校验
# ──────────────────────────────────────────────────────────────────────────────


class TestStylizedFacts:
    _RETS = [0.0] * 20 + [0.2, -0.2, 0.15, -0.15]  # 聚集 + 肥尾
    _VOLS = [10.0] * 6 + [50.0] * 6 + [10.0] * 6 + [50.0] * 6  # 块状 → 量自相关

    def test_builtin_pass(self) -> None:
        sim = _sim()
        report = sim.verify_stylized_facts(
            prices=_prices_from_returns(self._RETS),
            volumes=self._VOLS,
        )
        assert report.volatility_clustering > 0.0
        assert report.excess_kurtosis > 0.0
        assert report.volume_autocorr > 0.0
        assert report.passed is True
        assert report.simulated is True

    def test_insufficient_data_fail_closed(self) -> None:
        sim = _sim()
        with pytest.raises(MarketTwinError):
            sim.verify_stylized_facts()  # 仿真记录仅 1 价格点
        with pytest.raises(MarketTwinError):
            sim.verify_stylized_facts(prices=(100.0, 101.0))

    def test_injected_verifier(self) -> None:
        seen = []

        def verifier(series):
            seen.append(series)
            return StylizedFactReport(
                volatility_clustering=0.5,
                excess_kurtosis=2.0,
                volume_autocorr=0.6,
                passed=True,
                detail="injected",
            )

        sim = _sim(stats_verifier=verifier)
        report = sim.verify_stylized_facts(prices=_prices_from_returns(self._RETS))
        assert report.detail == "injected" and report.passed is True
        assert len(seen) == 1
        assert len(seen[0].returns) == len(self._RETS)  # log 收益 = 价格点 - 1
        # 注入器返回非法类型 → Fail-Closed
        sim2 = _sim(stats_verifier=lambda series: {"passed": True})
        with pytest.raises(MarketTwinError):
            sim2.verify_stylized_facts(prices=_prices_from_returns(self._RETS))


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_input_same_snapshot(self) -> None:
        def _run() -> tuple:
            sim = _sim()
            sim.register_agent(_agent("buyer", cash=1e6))
            sim.register_agent(_agent("seller", position=1000))
            sim.submit_order(_limit("s1", "seller", OrderSide.SELL, 99.5, 10))
            sim.submit_order(_limit("b1", "buyer", OrderSide.BUY, 100.0, 10))
            trades = sim.match(MatchMode.LIMIT)
            return sim.snapshot(), trades

        assert _run() == _run()
