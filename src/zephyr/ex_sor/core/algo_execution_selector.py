# [BLUEPRINT] MOD-XS-011 | docs/03_modules/_domain-ex_sor/algo_execution_selector/blueprint.md
# [MODULE] zephyr.ex_sor.core.algo_execution_selector
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] zephyr.shared.contracts.order; zephyr.shared.contracts.enums.order_enums; zephyr.shared.foundation.errors; zephyr.ex_sor.core.algo_trading_engine
# [CONSUMERS] MOD-XS-005(Algo Engine,消费 AlgoSelection 执行); D-EX-CORE(OMS,算法推荐入口)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 选择可审计(每条决策留痕); 评分归一[0,1]; 选最高分算法; 不可绕过流动性评估; 大单(>5%ADV)倾向 ICEBERG 隐藏
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SelectorError; NoAlgoAvailableError; InvalidFeaturesError
# [TESTS] tests/ex_sor/test_algo_execution_selector.py
# [A_module] module_id=MOD-XS-011 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Algo Execution Selector — 算法执行选择器 (MOD-XS-011)

D-EX-SOR §2.2 XS-11: 订单特征(大小/紧急度/流动性) → 自动选择最优算法 + 算法推荐 + 效果评估。

职责:
    - 提取订单特征 (adv_fraction / urgency / spread_bps / side)
    - 对每种已注册算法计算适配度评分 [0,1]
    - 选最高分算法 + 记录决策 (审计)
    - 执行后效果评估 (Phase 1: 简单实现差额打分)

依赖 (depgraph edge 9745163: XS-011 → XS-005):
    本模块消费 XS-05 AlgoTradingEngine 的算法注册表 (get_algo_types),
    不重复实现算法逻辑; 选择结果 AlgoSelection 供 XS-05 generate_plan 使用。

选择规则 (Phase 1 评分驱动, 非硬编码 if-else):
    TWAP     — 小单 + 低紧急度 + 低价差 → 被动均匀
    VWAP     — 中单 + 中紧急度 → 跟随成交量分布
    ICEBERG  — 大单(>5%ADV) + 需隐藏意图 → 冰山
    POV      — 中大单 + 想跟随实时量 → 参与率
    IS       — 中等 + 风险均衡 → AC 轨迹
    ALT      — 高紧急度 + 小中单 → 激进吃单 (附录B Sniper→ALT)

理论对标 (§2.2 XS-11): 强化学习算法选择/自适应算法参数/多算法协同 (Phase 2+)

SSoT: depgraph MOD-XS-011
Version: 0.1.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Final, Protocol

from zephyr.ex_sor.core.algo_trading_engine import (
    MAX_ADV_FRACTION,
    MAX_PARTICIPATION_RATE,
    AlgoTradingEngine,
    AlgoType,
    MarketContext,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.contracts.order import Order
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "OrderFeatures",
    "AlgoSelection",
    "AlgoScoreBreakdown",
    "AlgoExecutionSelector",
    "AlgoEvaluator",
    "DefaultAlgoEvaluator",
    "ExecutionOutcome",
    "SelectorError",
    "NoAlgoAvailableError",
    "InvalidFeaturesError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class SelectorError(ZephyrBaseError):
    """算法选择器错误。"""

    error_code = "ZA-XS-0011"


class NoAlgoAvailableError(SelectorError):
    """无可用算法——注册表为空或全部评分无效。"""

    error_code = "ZA-XS-0011-NA"


class InvalidFeaturesError(SelectorError):
    """订单特征非法——urgency 越界、ADV 为零等。"""

    error_code = "ZA-XS-0011-IF"


# ──────────────────────────────────────────────────────────────────────────────
# 订单特征
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class OrderFeatures:
    """订单特征——算法选择的输入。

    Attributes:
        order_id: 订单 ID
        symbol: 标的
        side: 买卖方向
        quantity: 订单数量
        adv_fraction: 订单占 ADV 比例 (quantity/ADV)
        urgency: 紧急度 [0,1] (0=不急, 1=最急)
        spread_bps: 买卖价差 (basis points); 缺失用 -1 表示未知
        last_price: 最新价
    """

    order_id: str
    symbol: str
    side: OrderSide
    quantity: Decimal
    adv_fraction: Decimal
    urgency: Decimal
    spread_bps: Decimal = Decimal("-1")
    last_price: Decimal | None = None

    def __post_init__(self) -> None:
        if not self.order_id:
            raise InvalidFeaturesError("order_id 不能为空", details={"field": "order_id"})
        if self.adv_fraction < 0:
            raise InvalidFeaturesError(
                "adv_fraction 不能为负",
                details={"field": "adv_fraction", "value": str(self.adv_fraction)},
            )
        if self.urgency < 0 or self.urgency > 1:
            raise InvalidFeaturesError(
                "urgency 必须在 [0, 1]",
                details={"field": "urgency", "value": str(self.urgency)},
            )
        if self.quantity <= 0:
            raise InvalidFeaturesError(
                "quantity 必须为正",
                details={"field": "quantity", "value": str(self.quantity)},
            )

    @classmethod
    def from_order(
        cls,
        order: Order,
        ctx: MarketContext,
        urgency: Decimal = Decimal("0.5"),
    ) -> OrderFeatures:
        """从 Order + MarketContext 提取特征。"""
        if ctx.adv <= 0:
            raise InvalidFeaturesError(
                "adv 必须为正",
                details={"field": "adv", "value": str(ctx.adv)},
            )
        adv_frac = order.quantity / ctx.adv
        spread_bps = Decimal("-1")
        if ctx.bid_price is not None and ctx.ask_price is not None and ctx.last_price > 0:
            spread = ctx.ask_price - ctx.bid_price
            spread_bps = (spread / ctx.last_price) * Decimal("10000")
        return cls(
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            adv_fraction=adv_frac,
            urgency=urgency,
            spread_bps=spread_bps,
            last_price=ctx.last_price,
        )


# ──────────────────────────────────────────────────────────────────────────────
# 评分明细
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AlgoScoreBreakdown:
    """单算法评分明细——可审计。

    Attributes:
        algo: 算法类型
        size_score: 订单大小适配度 [0,1]
        urgency_score: 紧急度适配度 [0,1]
        liquidity_score: 流动性适配度 [0,1]
        total: 加权总分 [0,1]
    """

    algo: AlgoType
    size_score: float
    urgency_score: float
    liquidity_score: float
    total: float

    def to_dict(self) -> dict[str, object]:
        return {
            "algo": self.algo.value,
            "size": round(self.size_score, 4),
            "urgency": round(self.urgency_score, 4),
            "liquidity": round(self.liquidity_score, 4),
            "total": round(self.total, 4),
        }


# ──────────────────────────────────────────────────────────────────────────────
# 选择结果
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AlgoSelection:
    """算法选择结果——可审计。

    Attributes:
        order_id: 订单 ID
        selected_algo: 选中的算法
        breakdowns: 所有候选算法评分明细
        features: 订单特征
        reason: 选择理由
        timestamp: 决策时间
    """

    order_id: str
    selected_algo: AlgoType
    breakdowns: list[AlgoScoreBreakdown]
    features: OrderFeatures
    reason: str
    timestamp: datetime

    @property
    def scores(self) -> dict[AlgoType, float]:
        """算法→总分 映射。"""
        return {b.algo: b.total for b in self.breakdowns}

    def to_dict(self) -> dict[str, object]:
        return {
            "order_id": self.order_id,
            "selected_algo": self.selected_algo.value,
            "features": {
                "symbol": self.features.symbol,
                "side": self.features.side.value,
                "quantity": str(self.features.quantity),
                "adv_fraction": str(self.features.adv_fraction),
                "urgency": str(self.features.urgency),
                "spread_bps": str(self.features.spread_bps),
            },
            "breakdowns": [b.to_dict() for b in self.breakdowns],
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
        }


# ──────────────────────────────────────────────────────────────────────────────
# 执行效果评估
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ExecutionOutcome:
    """执行结果——效果评估输入。

    Attributes:
        order_id: 订单 ID
        algo_type: 使用的算法
        decision_price: 决策价 (下单前价)
        avg_fill_price: 平均成交价
        quantity_filled: 成交数量
        duration_seconds: 执行耗时 (秒)
    """

    order_id: str
    algo_type: AlgoType
    decision_price: Decimal
    avg_fill_price: Decimal
    quantity_filled: Decimal
    duration_seconds: float = 0.0


@dataclass(frozen=True)
class AlgoEvaluationResult:
    """算法效果评估结果。

    Attributes:
        order_id: 订单 ID
        algo_type: 评估的算法
        implementation_shortfall_bps: 实施差额 (bps, 正=成本)
        fill_rate: 成交率 [0,1]
        efficiency_score: 效率评分 [0,1] (越高越好)
        verdict: 评定 (good/acceptable/poor)
    """

    order_id: str
    algo_type: AlgoType
    implementation_shortfall_bps: Decimal
    fill_rate: Decimal
    efficiency_score: float
    verdict: str


class AlgoEvaluator(Protocol):
    """算法效果评估器接口。"""

    def evaluate(self, outcome: ExecutionOutcome) -> AlgoEvaluationResult:
        """评估单次执行效果。"""


class DefaultAlgoEvaluator:
    """默认效果评估器——Implementation Shortfall + 成交率打分 (Phase 1)。

    评分模型:
        IS_bps = (avg_fill - decision) / decision × 10000  (BUY)
        IS_bps = (decision - avg_fill) / decision × 10000  (SELL)
        fill_rate = quantity_filled / order_quantity (需外部传入, 此处用 outcome)
        efficiency = 1 - min(IS_bps/50, 1)  (50bps 视为最差)
    """

    def evaluate(self, outcome: ExecutionOutcome) -> AlgoEvaluationResult:
        if outcome.decision_price <= 0:
            raise SelectorError(
                "decision_price 必须为正",
                details={"field": "decision_price", "value": str(outcome.decision_price)},
            )
        # IS 计算 (此处用绝对值, 不区分方向; 方向由调用方在 outcome 构造时体现)
        diff = outcome.avg_fill_price - outcome.decision_price
        is_bps = (diff / outcome.decision_price) * Decimal("10000")
        is_bps = abs(is_bps)

        # 成交率: outcome 内只有 filled, 用 filled>0 判断; 完整成交率需订单总量
        # Phase 1: 若 filled==0 视为 0, 否则 1.0 (简化, 完整版需 total)
        fill_rate = Decimal("1.0") if outcome.quantity_filled > 0 else Decimal("0")

        # 效率评分: IS 越低越好
        is_f = float(is_bps)
        efficiency = max(0.0, 1.0 - min(is_f / 50.0, 1.0))

        if is_bps <= Decimal("5"):
            verdict = "good"
        elif is_bps <= Decimal("20"):
            verdict = "acceptable"
        else:
            verdict = "poor"

        return AlgoEvaluationResult(
            order_id=outcome.order_id,
            algo_type=outcome.algo_type,
            implementation_shortfall_bps=is_bps,
            fill_rate=fill_rate,
            efficiency_score=efficiency,
            verdict=verdict,
        )


# ──────────────────────────────────────────────────────────────────────────────
# 算法选择器
# ──────────────────────────────────────────────────────────────────────────────


class AlgoExecutionSelector:
    """算法执行选择器——订单特征 → 评分 → 选最优算法。

    用法:
        selector = AlgoExecutionSelector(engine)
        sel = selector.select(order, ctx, urgency=Decimal("0.3"))
        # sel.selected_algo → AlgoType (交由 XS-05 generate_plan)

    评分模型 (三维加权):
        size_score      — 订单大小 (adv_fraction) 适配度
        urgency_score   — 紧急度适配度
        liquidity_score — 流动性 (spread) 适配度
        total = 0.4×size + 0.35×urgency + 0.25×liquidity
    """

    # 评分权重 (§2.2 XS-11 多维加权)
    SIZE_WEIGHT: Final[float] = 0.40
    URGENCY_WEIGHT: Final[float] = 0.35
    LIQUIDITY_WEIGHT: Final[float] = 0.25

    def __init__(
        self,
        engine: AlgoTradingEngine,
        weights: tuple[float, float, float] | None = None,
    ) -> None:
        self._engine = engine
        if weights is not None:
            self._size_w, self._urg_w, self._liq_w = self._validate_weights(weights)
        else:
            self._size_w, self._urg_w, self._liq_w = (
                self.SIZE_WEIGHT,
                self.URGENCY_WEIGHT,
                self.LIQUIDITY_WEIGHT,
            )
        self._selections: list[AlgoSelection] = []  # 审计日志 (内存)

    @staticmethod
    def _validate_weights(w: tuple[float, float, float]) -> tuple[float, float, float]:
        s, u, l = w
        if s < 0 or u < 0 or l < 0:
            raise SelectorError(
                "权重不能为负",
                details={"size": s, "urgency": u, "liquidity": l},
            )
        total = s + u + l
        if abs(total - 1.0) > 1e-6:
            raise SelectorError(
                "权重和必须≈1.0",
                details={"size": s, "urgency": u, "liquidity": l, "sum": total},
            )
        return s, u, l

    # ── 选择入口 ──

    def select(
        self,
        order: Order,
        ctx: MarketContext,
        urgency: Decimal = Decimal("0.5"),
        now: datetime | None = None,
    ) -> AlgoSelection:
        """选择最优算法——提取特征→评分→选最高分→记录。

        Args:
            order: 委托指令
            ctx: 市场上下文
            urgency: 紧急度 [0,1]
            now: 时间戳 (测试用)

        Returns:
            AlgoSelection: 选择结果 (含评分明细 + 理由)

        Raises:
            NoAlgoAvailableError: 注册表为空
            InvalidFeaturesError: 特征非法
        """
        now = now or datetime.now(timezone.utc)

        available = self._engine.get_algo_types()
        if not available:
            raise NoAlgoAvailableError(
                "算法注册表为空",
                details={"order_id": order.order_id},
            )

        features = OrderFeatures.from_order(order, ctx, urgency)
        breakdowns = [self._score_algo(algo, features) for algo in available]

        # 选最高分 (并列时取列表中靠前的, 稳定)
        best = max(breakdowns, key=lambda b: b.total)
        selected = best.algo

        reason = self._build_reason(selected, best, features)
        selection = AlgoSelection(
            order_id=order.order_id,
            selected_algo=selected,
            breakdowns=breakdowns,
            features=features,
            reason=reason,
            timestamp=now,
        )
        self._selections.append(selection)
        logger.info(
            "Select: order=%s algo=%s score=%.4f (adv_frac=%.4f urgency=%.2f)",
            order.order_id,
            selected.value,
            best.total,
            float(features.adv_fraction),
            float(features.urgency),
        )
        return selection

    # ── 评分 ──

    def _score_algo(self, algo: AlgoType, f: OrderFeatures) -> AlgoScoreBreakdown:
        """对单算法评分 (三维 + 加权)。"""
        size_s = self._size_score(algo, f)
        urg_s = self._urgency_score(algo, f)
        liq_s = self._liquidity_score(algo, f)
        total = self._size_w * size_s + self._urg_w * urg_s + self._liq_w * liq_s
        return AlgoScoreBreakdown(
            algo=algo,
            size_score=size_s,
            urgency_score=urg_s,
            liquidity_score=liq_s,
            total=total,
        )

    def _size_score(self, algo: AlgoType, f: OrderFeatures) -> float:
        """订单大小适配度。

        adv_fraction 阈值:
            tiny  <0.1%    → TWAP/ALT 优
            small <1%      → TWAP/VWAP
            medium 1-5%    → VWAP/IS/POV
            large >5%      → ICEBERG/POV (需隐藏/参与率控制)
        """
        frac = float(f.adv_fraction)
        if algo == AlgoType.TWAP:
            # 小单最佳, 大单骤降
            if frac < 0.001:
                return 0.95
            if frac < 0.01:
                return 0.80
            if frac < 0.05:
                return 0.40
            return 0.10
        if algo == AlgoType.VWAP:
            # 中单最佳
            if frac < 0.001:
                return 0.60
            if frac < 0.01:
                return 0.85
            if frac < 0.05:
                return 0.90
            return 0.45
        if algo == AlgoType.ICEBERG:
            # 大单最佳 (隐藏意图)
            if frac < 0.01:
                return 0.15
            if frac < 0.05:
                return 0.55
            return 0.95  # >5% ADV
        if algo == AlgoType.POV:
            # 中大单 (跟随实时量)
            if frac < 0.001:
                return 0.30
            if frac < 0.01:
                return 0.60
            if frac < 0.05:
                return 0.85
            return 0.80
        if algo == AlgoType.IS:
            # 中等风险均衡
            if frac < 0.001:
                return 0.50
            if frac < 0.01:
                return 0.75
            if frac < 0.05:
                return 0.85
            return 0.55
        if algo == AlgoType.ALT:
            # 小中单 (大单不适用, 冲击过大)
            if frac < 0.001:
                return 0.85
            if frac < 0.01:
                return 0.70
            if frac < 0.05:
                return 0.25
            return 0.05
        return 0.0

    def _urgency_score(self, algo: AlgoType, f: OrderFeatures) -> float:
        """紧急度适配度。

        ALT: 高紧急度优 (快速吃单)
        TWAP: 低紧急度优 (被动等待)
        IS: 中等最优 (风险均衡)
        VWAP/POV/ICEBERG: 中等偏好
        """
        u = float(f.urgency)
        if algo == AlgoType.ALT:
            # 高紧急度: 线性增长
            return u
        if algo == AlgoType.TWAP:
            # 低紧急度: 线性递减
            return 1.0 - u
        if algo == AlgoType.IS:
            # 中等最优: 钟形 (0.5 峰值)
            return 1.0 - abs(u - 0.5) * 2.0
        if algo == AlgoType.VWAP:
            # 中低偏好
            return 1.0 - abs(u - 0.4) * 1.5
        if algo == AlgoType.POV:
            # 中等
            return 1.0 - abs(u - 0.5) * 1.5
        if algo == AlgoType.ICEBERG:
            # 中低 (大单不急)
            return 1.0 - abs(u - 0.35) * 1.5
        return 0.0

    def _liquidity_score(self, algo: AlgoType, f: OrderFeatures) -> float:
        """流动性适配度 (基于价差 bps)。

        spread 未知(-1) → 中性 0.5
        窄价差(<5bps): ALT/AGGRESSIVE 可行
        宽价差(>20bps): 被动算法(TWAP/ICEBERG)避免吃价差
        """
        if f.spread_bps < 0:
            return 0.5  # 未知, 中性
        sp = float(f.spread_bps)
        if algo == AlgoType.ALT:
            # 窄价差优 (吃单成本低)
            if sp < 5:
                return 0.90
            if sp < 15:
                return 0.50
            return 0.15
        if algo == AlgoType.TWAP:
            # 宽价差优 (避免吃单)
            if sp < 5:
                return 0.60
            if sp < 15:
                return 0.75
            return 0.90
        if algo == AlgoType.ICEBERG:
            # 宽价差优 (挂单被动)
            if sp < 5:
                return 0.55
            if sp < 15:
                return 0.75
            return 0.85
        if algo == AlgoType.VWAP:
            return 0.70 if sp < 15 else 0.55
        if algo == AlgoType.POV:
            return 0.70 if sp < 15 else 0.50
        if algo == AlgoType.IS:
            return 0.75 if sp < 15 else 0.60
        return 0.5

    def _build_reason(self, selected: AlgoType, best: AlgoScoreBreakdown, f: OrderFeatures) -> str:
        """构造可审计的选择理由。"""
        size_tag = (
            "tiny"
            if f.adv_fraction < Decimal("0.001")
            else "small"
            if f.adv_fraction < Decimal("0.01")
            else "medium"
            if f.adv_fraction < Decimal("0.05")
            else "large"
        )
        urg_tag = "low" if f.urgency < Decimal("0.33") else "mid" if f.urgency < Decimal("0.66") else "high"
        return (
            f"选 {selected.value}: 总分 {best.total:.4f} "
            f"(size={best.size_score:.2f} urgency={best.urgency_score:.2f} "
            f"liquidity={best.liquidity_score:.2f}) | "
            f"订单={size_tag}({float(f.adv_fraction):.4f} ADV) 紧急度={urg_tag}"
        )

    # ── 审计查询 ──

    @property
    def selections(self) -> list[AlgoSelection]:
        """历史选择决策 (审计)。"""
        return list(self._selections)

    def get_history(self, order_id: str | None = None, limit: int = 100) -> list[AlgoSelection]:
        results = self._selections
        if order_id:
            results = [s for s in results if s.order_id == order_id]
        return list(results[-limit:])

    def clear_history(self) -> None:
        self._selections.clear()

    # ── 推荐 (不绑定具体订单, 供展示) ──

    def recommend(self, features: OrderFeatures) -> AlgoType:
        """根据特征推荐算法 (无副作用, 不记审计)。"""
        available = self._engine.get_algo_types()
        if not available:
            raise NoAlgoAvailableError("算法注册表为空", details={})
        breakdowns = [self._score_algo(algo, features) for algo in available]
        best = max(breakdowns, key=lambda b: b.total)
        return best.algo
