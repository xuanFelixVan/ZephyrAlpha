# [BLUEPRINT] MOD-XS-001 | docs/03_modules/_domain_ex_sor/optimal_order_router/blueprint.md
# [MODULE] zephyr.ex_sor.core.optimal_order_router
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] zephyr.shared.contracts.order; zephyr.shared.foundation.errors; zephyr.ex_sor.core.broker_adapter_manager; zephyr.ex_sor.api.broker_api_connector
# [CONSUMERS] MOD-EX-CORE(OMS,订单路由入口) ; MOD-XS-004(Execution Scheduler,调度后路由)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 路由决策可审计(§6.4); SOR不做风控判断(§6.1); 三维加权评分选最优券商; 评分权重和≥1.0
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RoutingError; NoRouteAvailableError; InvalidRouteWeightsError
# [TESTS] tests/ex_sor/test_optimal_order_router.py
# [A_module] module_id=MOD-XS-001 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Optimal Order Router — 智能订单路由 (MOD-XS-001)

D-EX-SOR §2.2 XS-01: 延迟/成交率/费用三维加权 → 最优券商选择。

职责:
    - 对每个可用券商计算三维评分 (延迟/成交率/费用)
    - 加权求和选出最优券商
    - 通过 BrokerAdapterManager (XS-02) 提交订单
    - 记录路由决策 (审计, §6.4)

关键约束 (D-EX-SOR §6):
    §6.1  SOR 不直接 H 依赖 D-RISK: 风控由 EX-CORE 做 Pre-Trade 检查, SOR 只负责路由
    §6.4  路由决策可审计: 每条 SOR 决策必须留痕, 支持事后复盘
    §10.1 参与率限制 ≤5%: 由 C-004 检查, SOR 不做

路由维度 (§2.2 XS-01):
    latency_score    — 延迟评分 (越低延迟→越高分, 0~1)
    fill_rate_score  — 成交率评分 (越高成交率→越高分, 0~1)
    cost_score       — 费用评分 (越低费用→越高分, 0~1)
    → 加权求和 → 选最高分券商

SSoT: depgraph MOD-XS-001
Version: 0.1.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Final, Optional, Protocol

from zephyr.ex_sor.api.api_rate_limiter import TradingSession
from zephyr.ex_sor.api.broker_api_connector import BrokerType
from zephyr.ex_sor.core.broker_adapter_manager import (
    BrokerAdapterManager,
    BrokerSelection,
)
from zephyr.shared.contracts.order import Order
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "RouteScore",
    "RouteWeights",
    "RouteDecision",
    "RouteResult",
    "BrokerMetricsProvider",
    "DefaultMetricsProvider",
    "OptimalOrderRouter",
    "RoutingError",
    "NoRouteAvailableError",
    "InvalidRouteWeightsError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class RoutingError(ZephyrBaseError):
    """路由错误——评分失败、提交失败。"""

    error_code = "ZA-XS-0001"


class NoRouteAvailableError(RoutingError):
    """无可用路由——没有可用券商或评分全为零。"""

    error_code = "ZA-XS-0001-NA"


class InvalidRouteWeightsError(RoutingError):
    """路由权重非法——权重和≠1.0 或含负值。"""

    error_code = "ZA-XS-0001-IW"


# ──────────────────────────────────────────────────────────────────────────────
# 路由评分
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class RouteScore:
    """三维路由评分——延迟/成交率/费用, 各 0~1。

    Attributes:
        latency_score: 延迟评分 (1=最快, 0=最慢)
        fill_rate_score: 成交率评分 (1=最高, 0=最低)
        cost_score: 费用评分 (1=最低, 0=最高)
    """

    latency_score: float
    fill_rate_score: float
    cost_score: float

    def __post_init__(self) -> None:
        for name, val in [
            ("latency_score", self.latency_score),
            ("fill_rate_score", self.fill_rate_score),
            ("cost_score", self.cost_score),
        ]:
            if not (0.0 <= val <= 1.0):
                raise RoutingError(
                    f"{name} must be in [0, 1], got {val}",
                    details={"field": name, "value": val},
                )

    def weighted_total(self, weights: RouteWeights) -> float:
        """加权总分 = Σ(score_i * weight_i)。"""
        return (
            self.latency_score * weights.latency_weight
            + self.fill_rate_score * weights.fill_rate_weight
            + self.cost_score * weights.cost_weight
        )


@dataclass(frozen=True)
class RouteWeights:
    """路由权重——延迟/成交率/费用, 和必须 = 1.0。

    默认: 成交率优先 (0.4) > 延迟 (0.3) = 费用 (0.3)
    """

    latency_weight: float = 0.3
    fill_rate_weight: float = 0.4
    cost_weight: float = 0.3

    def __post_init__(self) -> None:
        for name, val in [
            ("latency_weight", self.latency_weight),
            ("fill_rate_weight", self.fill_rate_weight),
            ("cost_weight", self.cost_weight),
        ]:
            if val < 0:
                raise InvalidRouteWeightsError(
                    f"{name} must be >=0, got {val}",
                    details={"field": name, "value": val},
                )
        total = self.latency_weight + self.fill_rate_weight + self.cost_weight
        if abs(total - 1.0) > 1e-6:
            raise InvalidRouteWeightsError(
                f"weights must sum to 1.0, got {total}",
                details={
                    "latency": self.latency_weight,
                    "fill_rate": self.fill_rate_weight,
                    "cost": self.cost_weight,
                    "sum": total,
                },
            )


# ──────────────────────────────────────────────────────────────────────────────
# 路由决策记录 (审计, §6.4)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class RouteDecision:
    """路由决策记录——可审计 (§6.4)。

    Attributes:
        order_id: 订单 ID
        selected_broker: 选中的券商
        scores: 各券商评分 (含未选中的)
        weights: 使用的权重
        reason: 决策理由
        timestamp: 决策时间
    """

    order_id: str
    selected_broker: BrokerType
    scores: dict[BrokerType, RouteScore]
    weights: RouteWeights
    reason: str
    timestamp: datetime

    def to_dict(self) -> dict[str, object]:
        return {
            "order_id": self.order_id,
            "selected_broker": self.selected_broker.value,
            "scores": {
                bt.value: {
                    "latency": s.latency_score,
                    "fill_rate": s.fill_rate_score,
                    "cost": s.cost_score,
                    "total": s.weighted_total(self.weights),
                }
                for bt, s in self.scores.items()
            },
            "weights": {
                "latency": self.weights.latency_weight,
                "fill_rate": self.weights.fill_rate_weight,
                "cost": self.weights.cost_weight,
            },
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True)
class RouteResult:
    """路由结果——决策 + 提交结果。

    Attributes:
        decision: 路由决策
        selection: BrokerAdapterManager 返回的提交结果
    """

    decision: RouteDecision
    selection: BrokerSelection


# ──────────────────────────────────────────────────────────────────────────────
# 券商指标提供者 (可替换, Phase 1 用默认值)
# ──────────────────────────────────────────────────────────────────────────────


class BrokerMetricsProvider(Protocol):
    """券商指标提供者接口——提供延迟/成交率/费用数据。"""

    def get_latency_ms(self, broker: BrokerType) -> float:
        """返回券商平均延迟 (毫秒)。"""

    def get_fill_rate(self, broker: BrokerType) -> float:
        """返回券商成交率 (0~1)。"""

    def get_cost_bps(self, broker: BrokerType) -> float:
        """返回券商交易成本 (basis points)。"""


class DefaultMetricsProvider:
    """默认指标提供者——静态默认值, Phase 1 使用。

    实际系统应替换为从历史数据计算的动态指标。
    """

    # 各券商默认指标 (latency_ms, fill_rate, cost_bps)
    _DEFAULTS: dict[BrokerType, tuple[float, float, float]] = {
        BrokerType.MINIQMT: (5.0, 0.95, 2.5),  # 低延迟, 高成交, 中等成本
        BrokerType.XTP: (10.0, 0.92, 2.0),  # 中延迟, 高成交, 低成本
        BrokerType.CTP: (8.0, 0.90, 1.5),  # 中延迟, 中成交, 低成本
        BrokerType.OKX: (15.0, 0.98, 5.0),  # 高延迟, 最高成交, 高成本
        BrokerType.SIMULATED: (1.0, 1.0, 0.0),  # 模拟: 最优
    }

    def __init__(self, overrides: dict[BrokerType, tuple[float, float, float]] | None = None) -> None:
        self._metrics = dict(self._DEFAULTS)
        if overrides:
            self._metrics.update(overrides)

    def get_latency_ms(self, broker: BrokerType) -> float:
        return self._metrics.get(broker, (100.0, 0.5, 10.0))[0]

    def get_fill_rate(self, broker: BrokerType) -> float:
        return self._metrics.get(broker, (100.0, 0.5, 10.0))[1]

    def get_cost_bps(self, broker: BrokerType) -> float:
        return self._metrics.get(broker, (100.0, 0.5, 10.0))[2]


# ──────────────────────────────────────────────────────────────────────────────
# 最优订单路由器
# ──────────────────────────────────────────────────────────────────────────────


class OptimalOrderRouter:
    """最优订单路由——三维加权评分选券商 + 审计记录。

    用法:
        router = OptimalOrderRouter(adapter_mgr, metrics_provider)
        result = router.route(order, session=TradingSession.INTRADAY)
        # result.decision.selected_broker → 最优券商
        # result.selection.broker_order_id → 券商订单 ID

    评分算法:
        1. 对每个可用券商计算 RouteScore (延迟/成交率/费用)
        2. 加权求和 → 总分
        3. 选最高分券商
        4. 通过 BrokerAdapterManager 提交
        5. 记录 RouteDecision (审计)
    """

    def __init__(
        self,
        adapter_manager: BrokerAdapterManager,
        weights: RouteWeights | None = None,
        metrics: BrokerMetricsProvider | None = None,
    ) -> None:
        self._mgr = adapter_manager
        self._weights = weights or RouteWeights()
        self._metrics = metrics or DefaultMetricsProvider()
        self._decisions: list[RouteDecision] = []  # 审计日志 (内存, Phase 1)

    @property
    def weights(self) -> RouteWeights:
        return self._weights

    @property
    def decisions(self) -> list[RouteDecision]:
        """历史路由决策 (审计, §6.4)。"""
        return list(self._decisions)

    # ── 路由入口 ──

    def route(
        self,
        order: Order,
        session: TradingSession = TradingSession.INTRADAY,
        now: datetime | None = None,
    ) -> RouteResult:
        """路由订单——评分→选券商→提交→记录。

        Args:
            order: 委托指令 (CTR-004)
            session: 当前交易时段
            now: 时间戳 (测试用)

        Returns:
            RouteResult: 路由决策 + 提交结果

        Raises:
            NoRouteAvailableError: 无可用券商
            RoutingError: 提交失败
        """
        now = now or datetime.now(timezone.utc)

        # 1. 评分所有可用券商
        scores = self._score_all_brokers(order)

        # 2. 选最优
        available = self._mgr.available_brokers
        if not available:
            raise NoRouteAvailableError(
                "无可用券商路由",
                details={"order_id": order.order_id},
            )

        scored = {bt: score for bt, score in scores.items() if bt in available}
        if not scored:
            raise NoRouteAvailableError(
                "可用券商均无评分",
                details={"available": [bt.value for bt in available]},
            )

        best_broker = max(scored, key=lambda bt: scored[bt].weighted_total(self._weights))
        best_score = scored[best_broker].weighted_total(self._weights)

        # 3. 构造决策记录
        decision = RouteDecision(
            order_id=order.order_id,
            selected_broker=best_broker,
            scores=scores,
            weights=self._weights,
            reason=f"最优评分 {best_score:.4f} (latency={scores[best_broker].latency_score:.2f}"
            f" fill_rate={scores[best_broker].fill_rate_score:.2f}"
            f" cost={scores[best_broker].cost_score:.2f})",
            timestamp=now,
        )
        self._decisions.append(decision)

        # 4. 如果最优不是当前 active, 切换 (Feature Toggle, §6.5)
        if self._mgr.active_broker != best_broker:
            logger.info(
                "Route: switching to best broker %s (score=%.4f)",
                best_broker.value,
                best_score,
            )
            self._mgr.switch_broker(best_broker)

        # 5. 提交 (BrokerAdapterManager 处理故障转移)
        try:
            selection = self._mgr.submit_order(order, session)
        except Exception as exc:
            raise RoutingError(
                f"路由提交失败: {exc}",
                details={
                    "order_id": order.order_id,
                    "broker": best_broker.value,
                    "score": best_score,
                },
            ) from exc

        logger.info(
            "Route: order=%s -> broker=%s (failovered=%s)",
            order.order_id,
            selection.broker.value,
            selection.failovered,
        )

        return RouteResult(decision=decision, selection=selection)

    # ── 评分 ──

    def score_broker(self, broker: BrokerType, order: Order | None = None) -> RouteScore:
        """对单个券商评分。

        评分归一化:
            latency_score  = 1 / (1 + latency_ms / 10)  — 延迟越低分越高
            fill_rate_score = fill_rate                  — 直接使用成交率
            cost_score     = 1 / (1 + cost_bps / 5)     — 成本越低分越高
        """
        latency_ms = self._metrics.get_latency_ms(broker)
        fill_rate = self._metrics.get_fill_rate(broker)
        cost_bps = self._metrics.get_cost_bps(broker)

        latency_score = 1.0 / (1.0 + latency_ms / 10.0)
        fill_rate_score = max(0.0, min(1.0, fill_rate))
        cost_score = 1.0 / (1.0 + cost_bps / 5.0)

        return RouteScore(
            latency_score=latency_score,
            fill_rate_score=fill_rate_score,
            cost_score=cost_score,
        )

    def _score_all_brokers(self, order: Order) -> dict[BrokerType, RouteScore]:
        """对所有已注册券商评分。"""
        scores: dict[BrokerType, RouteScore] = {}
        for broker in self._mgr.registered_brokers:
            scores[broker] = self.score_broker(broker, order)
        return scores

    # ── 审计查询 ──

    def get_decision_history(self, order_id: str | None = None, limit: int = 100) -> list[RouteDecision]:
        """查询路由决策历史 (审计, §6.4)。"""
        results = self._decisions
        if order_id:
            results = [d for d in results if d.order_id == order_id]
        return list(results[-limit:])

    def clear_history(self) -> None:
        """清空决策历史 (测试用)。"""
        self._decisions.clear()
