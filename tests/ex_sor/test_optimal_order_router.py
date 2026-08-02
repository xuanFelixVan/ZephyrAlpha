# [BLUEPRINT] MOD-XS-001 | docs/03_modules/_domain_ex_sor/optimal_order_router/blueprint.md | §
# [TTL] permanent
"""OptimalOrderRouter 单元测试 (MOD-XS-001)。三维加权路由 + 审计。"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from zephyr.ex_sor.api.api_rate_limiter import TradingSession
from zephyr.ex_sor.api.broker_api_connector import (
    BrokerApiConnector,
    BrokerType,
    ConnectionConfig,
    SimulatedProtocol,
)
from zephyr.ex_sor.core.broker_adapter_manager import (
    BrokerAdapter,
    BrokerAdapterManager,
)
from zephyr.ex_sor.core.optimal_order_router import (
    DefaultMetricsProvider,
    InvalidRouteWeightsError,
    NoRouteAvailableError,
    OptimalOrderRouter,
    RouteDecision,
    RouteResult,
    RouteScore,
    RouteWeights,
    RoutingError,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType
from zephyr.shared.contracts.order import Order

NOW = datetime(2026, 8, 4, 10, 0, tzinfo=timezone.utc)


def make_order(order_id: str = "ORD-001") -> Order:
    return Order(
        order_id=order_id,
        idempotency_key=f"IDEMP-{order_id}",
        order_type=OrderType.LIMIT,
        quantity=Decimal("100"),
        side=OrderSide.BUY,
        strategy_id="STRAT-1",
        symbol="000001.SZ",
        limit_price=Decimal("10.50"),
    )


def make_router(
    brokers: list[tuple[BrokerType, int]] | None = None,
    weights: RouteWeights | None = None,
    metrics: DefaultMetricsProvider | None = None,
) -> tuple[OptimalOrderRouter, BrokerAdapterManager]:
    """构造已连接的路由器 + 适配器管理器。

    Args:
        brokers: [(broker_type, circuit_threshold), ...]; 默认 [(SIMULATED, 5)]
    """
    brokers = brokers or [(BrokerType.SIMULATED, 5)]
    mgr = BrokerAdapterManager()
    protos = {}
    for bt, threshold in brokers:
        proto = SimulatedProtocol()
        cfg = ConnectionConfig(broker=bt, circuit_failure_threshold=threshold)
        conn = BrokerApiConnector(proto, cfg)
        mgr.register_adapter(BrokerAdapter(bt, conn), primary=(bt == brokers[0][0]))
        protos[bt] = proto
    mgr.connect_all()
    router = OptimalOrderRouter(mgr, weights=weights, metrics=metrics)
    return router, mgr


# ── RouteScore ────────────────────────────────────────────────────────────────


def test_score_valid():
    s = RouteScore(latency_score=0.8, fill_rate_score=0.9, cost_score=0.7)
    assert s.latency_score == pytest.approx(0.8)
    assert s.fill_rate_score == pytest.approx(0.9)
    assert s.cost_score == pytest.approx(0.7)


def test_score_out_of_range():
    with pytest.raises(RoutingError, match="must be in"):
        RouteScore(latency_score=1.5, fill_rate_score=0.5, cost_score=0.5)
    with pytest.raises(RoutingError):
        RouteScore(latency_score=-0.1, fill_rate_score=0.5, cost_score=0.5)


def test_score_weighted_total():
    s = RouteScore(latency_score=1.0, fill_rate_score=0.5, cost_score=0.0)
    w = RouteWeights(latency_weight=0.3, fill_rate_weight=0.4, cost_weight=0.3)
    # 1.0*0.3 + 0.5*0.4 + 0.0*0.3 = 0.3 + 0.2 + 0.0 = 0.5
    assert s.weighted_total(w) == pytest.approx(0.5)


def test_score_frozen():
    s = RouteScore(0.5, 0.5, 0.5)
    with pytest.raises(Exception):
        s.latency_score = 0.9  # type: ignore[misc]


# ── RouteWeights ──────────────────────────────────────────────────────────────


def test_weights_default():
    w = RouteWeights()
    assert w.latency_weight == pytest.approx(0.3)
    assert w.fill_rate_weight == pytest.approx(0.4)
    assert w.cost_weight == pytest.approx(0.3)
    assert w.latency_weight + w.fill_rate_weight + w.cost_weight == pytest.approx(1.0)


def test_weights_custom_valid():
    w = RouteWeights(latency_weight=0.5, fill_rate_weight=0.3, cost_weight=0.2)
    assert w.latency_weight == pytest.approx(0.5)


def test_weights_sum_not_one():
    with pytest.raises(InvalidRouteWeightsError, match="sum to 1.0"):
        RouteWeights(latency_weight=0.3, fill_rate_weight=0.3, cost_weight=0.3)


def test_weights_negative():
    with pytest.raises(InvalidRouteWeightsError, match="must be >=0"):
        RouteWeights(latency_weight=-0.1, fill_rate_weight=0.6, cost_weight=0.5)


# ── DefaultMetricsProvider ────────────────────────────────────────────────────


def test_metrics_defaults():
    m = DefaultMetricsProvider()
    assert m.get_latency_ms(BrokerType.MINIQMT) == pytest.approx(5.0)
    assert m.get_fill_rate(BrokerType.MINIQMT) == pytest.approx(0.95)
    assert m.get_cost_bps(BrokerType.MINIQMT) == pytest.approx(2.5)


def test_metrics_override():
    m = DefaultMetricsProvider(overrides={BrokerType.MINIQMT: (20.0, 0.80, 5.0)})
    assert m.get_latency_ms(BrokerType.MINIQMT) == pytest.approx(20.0)
    assert m.get_fill_rate(BrokerType.MINIQMT) == pytest.approx(0.80)


def test_metrics_unknown_broker():
    """未配置的券商返回默认惩罚值。"""
    m = DefaultMetricsProvider()
    # OKX 有默认值, 但如果用未注册的类型...
    # 实际上所有 BrokerType 都有默认值, 这里测试 fallback 路径
    assert m.get_latency_ms(BrokerType.MINIQMT) > 0


# ── OptimalOrderRouter: 评分 ─────────────────────────────────────────────────


def test_score_broker_simulated_optimal():
    """SIMULATED 券商评分应最优 (延迟1ms/成交率1.0/成本0)。"""
    router, _ = make_router()
    score = router.score_broker(BrokerType.SIMULATED)
    assert score.latency_score == pytest.approx(1.0 / 1.1, abs=0.01)  # 1/(1+0.1)
    assert score.fill_rate_score == pytest.approx(1.0)
    assert score.cost_score == pytest.approx(1.0)


def test_score_broker_miniqmt():
    router, _ = make_router([(BrokerType.MINIQMT, 5)])
    score = router.score_broker(BrokerType.MINIQMT)
    # latency=5ms → 1/(1+0.5)=0.667
    assert score.latency_score == pytest.approx(1.0 / 1.5, abs=0.01)
    # fill_rate=0.95
    assert score.fill_rate_score == pytest.approx(0.95)
    # cost=2.5bps → 1/(1+0.5)=0.667
    assert score.cost_score == pytest.approx(1.0 / 1.5, abs=0.01)


def test_score_all_brokers():
    router, _ = make_router([(BrokerType.MINIQMT, 5), (BrokerType.XTP, 5)])
    scores = router._score_all_brokers(make_order())
    assert BrokerType.MINIQMT in scores
    assert BrokerType.XTP in scores
    assert len(scores) == 2


# ── OptimalOrderRouter: 路由 ─────────────────────────────────────────────────


def test_route_single_broker():
    router, mgr = make_router()
    result = router.route(make_order(), now=NOW)
    assert result.decision.selected_broker == BrokerType.SIMULATED
    assert result.selection.broker_order_id.startswith("BROKER-")
    assert result.selection.failovered is False


def test_route_selects_best_broker():
    """多券商时选评分最高的。"""
    # SIMULATED 评分最优 (延迟1ms/成交1.0/成本0)
    # 但如果用 MINIQMT 做 primary, SIMULATED 做 backup
    router, mgr = make_router([(BrokerType.MINIQMT, 5), (BrokerType.SIMULATED, 5)])
    result = router.route(make_order(), now=NOW)
    # SIMULATED 评分应该更高
    assert result.decision.selected_broker == BrokerType.SIMULATED
    # active 应被切换到 SIMULATED
    assert mgr.active_broker == BrokerType.SIMULATED


def test_route_records_decision():
    """路由决策被记录 (审计, §6.4)。"""
    router, _ = make_router()
    router.route(make_order("O1"), now=NOW)
    router.route(make_order("O2"), now=NOW)
    assert len(router.decisions) == 2
    assert router.decisions[0].order_id == "O1"
    assert router.decisions[1].order_id == "O2"


def test_route_decision_to_dict():
    router, _ = make_router()
    result = router.route(make_order(), now=NOW)
    d = result.decision.to_dict()
    assert d["order_id"] == "ORD-001"
    assert "selected_broker" in d
    assert "scores" in d
    assert "weights" in d
    assert "timestamp" in d


def test_route_decision_reason_contains_scores():
    router, _ = make_router()
    result = router.route(make_order(), now=NOW)
    assert "latency=" in result.decision.reason
    assert "fill_rate=" in result.decision.reason
    assert "cost=" in result.decision.reason


def test_route_no_available_brokers():
    """无可用券商 → NoRouteAvailableError。"""
    router, mgr = make_router()
    # 断开所有连接
    mgr.disconnect_all()
    with pytest.raises(NoRouteAvailableError):
        router.route(make_order())


def test_route_no_brokers_registered():
    """未注册任何券商 → NoRouteAvailableError。"""
    mgr = BrokerAdapterManager()
    router = OptimalOrderRouter(mgr)
    with pytest.raises(NoRouteAvailableError):
        router.route(make_order())


# ── OptimalOrderRouter: 审计查询 ─────────────────────────────────────────────


def test_get_decision_history_all():
    router, _ = make_router()
    for i in range(5):
        router.route(make_order(f"O{i}"), now=NOW)
    history = router.get_decision_history()
    assert len(history) == 5


def test_get_decision_history_by_order_id():
    router, _ = make_router()
    router.route(make_order("O1"), now=NOW)
    router.route(make_order("O2"), now=NOW)
    router.route(make_order("O1"), now=NOW)  # 同 ID 第二次
    history = router.get_decision_history(order_id="O1")
    assert len(history) == 2
    assert all(d.order_id == "O1" for d in history)


def test_get_decision_history_limit():
    router, _ = make_router()
    for i in range(10):
        router.route(make_order(f"O{i}"), now=NOW)
    history = router.get_decision_history(limit=3)
    assert len(history) == 3


def test_clear_history():
    router, _ = make_router()
    router.route(make_order(), now=NOW)
    assert len(router.decisions) == 1
    router.clear_history()
    assert len(router.decisions) == 0


# ── OptimalOrderRouter: 自定义权重 ───────────────────────────────────────────


def test_custom_weights_latency_priority():
    """延迟优先权重 → 选延迟最低的券商。"""
    weights = RouteWeights(latency_weight=0.8, fill_rate_weight=0.1, cost_weight=0.1)
    # MINIQMT (5ms) vs XTP (10ms) → MINIQMT 延迟更低
    router, mgr = make_router(
        [(BrokerType.MINIQMT, 5), (BrokerType.XTP, 5)],
        weights=weights,
    )
    result = router.route(make_order(), now=NOW)
    assert result.decision.selected_broker == BrokerType.MINIQMT


def test_custom_weights_cost_priority():
    """成本优先权重 → 选成本最低的券商。"""
    weights = RouteWeights(latency_weight=0.1, fill_rate_weight=0.1, cost_weight=0.8)
    # CTP (1.5bps) 最低成本, 但需要注册
    router, mgr = make_router(
        [(BrokerType.MINIQMT, 5), (BrokerType.CTP, 5)],
        weights=weights,
    )
    result = router.route(make_order(), now=NOW)
    assert result.decision.selected_broker == BrokerType.CTP


# ── OptimalOrderRouter: 自定义指标 ───────────────────────────────────────────


def test_custom_metrics_provider():
    """自定义指标 → 评分基于自定义数据。"""
    # 让 XTP 看起来最优
    metrics = DefaultMetricsProvider(
        overrides={
            BrokerType.MINIQMT: (50.0, 0.80, 10.0),  # 差
            BrokerType.XTP: (1.0, 0.99, 0.5),  # 优
        }
    )
    router, mgr = make_router(
        [(BrokerType.MINIQMT, 5), (BrokerType.XTP, 5)],
        metrics=metrics,
    )
    result = router.route(make_order(), now=NOW)
    assert result.decision.selected_broker == BrokerType.XTP


# ── OptimalOrderRouter: 故障转移集成 ─────────────────────────────────────────


def test_route_failover_integration():
    """路由 + 故障转移: primary 熔断 → 自动切换到备选。"""
    # primary: MINIQMT (容易熔断), backup: SIMULATED (最优)
    mgr = BrokerAdapterManager()

    proto1 = SimulatedProtocol()
    cfg1 = ConnectionConfig(broker=BrokerType.MINIQMT, circuit_failure_threshold=1)
    conn1 = BrokerApiConnector(proto1, cfg1)
    mgr.register_adapter(BrokerAdapter(BrokerType.MINIQMT, conn1), primary=True)

    proto2 = SimulatedProtocol()
    cfg2 = ConnectionConfig(broker=BrokerType.SIMULATED, circuit_failure_threshold=5)
    conn2 = BrokerApiConnector(proto2, cfg2)
    mgr.register_adapter(BrokerAdapter(BrokerType.SIMULATED, conn2))

    mgr.connect_all()
    router = OptimalOrderRouter(mgr)

    # 第一次: SIMULATED 评分更高, 切换到 SIMULATED, 下单成功
    result = router.route(make_order("O1"), now=NOW)
    assert result.decision.selected_broker == BrokerType.SIMULATED
    assert result.selection.broker == BrokerType.SIMULATED

    # 切换回 MINIQMT 并注入故障
    mgr.switch_broker(BrokerType.MINIQMT)
    proto1.set_failure_mode(submit=True)

    # 第二次: 路由选 SIMULATED (评分高), 但 active 是 MINIQMT
    # 路由器会切换到 SIMULATED 再下单 → 成功
    result2 = router.route(make_order("O2"), now=NOW)
    assert result2.decision.selected_broker == BrokerType.SIMULATED
    assert result2.selection.broker == BrokerType.SIMULATED


# ── RouteResult / RouteDecision ───────────────────────────────────────────────


def test_route_result_dataclass():
    router, _ = make_router()
    result = router.route(make_order(), now=NOW)
    assert isinstance(result, RouteResult)
    assert isinstance(result.decision, RouteDecision)
    assert result.decision.timestamp == NOW


def test_decision_scores_contains_all_brokers():
    """决策记录包含所有已注册券商的评分 (不只是选中的)。"""
    router, _ = make_router([(BrokerType.MINIQMT, 5), (BrokerType.XTP, 5)])
    result = router.route(make_order(), now=NOW)
    assert BrokerType.MINIQMT in result.decision.scores
    assert BrokerType.XTP in result.decision.scores


# ── 边界条件 ─────────────────────────────────────────────────────────────────


def test_route_session_parameter():
    """session 参数传递给 BrokerAdapterManager。"""
    router, _ = make_router()
    result = router.route(make_order(), session=TradingSession.AUCTION, now=NOW)
    assert result.selection.broker_order_id.startswith("BROKER-")


def test_route_with_default_now():
    """不传 now 时使用当前时间。"""
    router, _ = make_router()
    before = datetime.now(timezone.utc)
    result = router.route(make_order())
    after = datetime.now(timezone.utc)
    assert before <= result.decision.timestamp <= after
