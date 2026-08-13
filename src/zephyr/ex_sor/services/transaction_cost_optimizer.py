# [BLUEPRINT] MOD-EX_SOR_EXT-003 | docs/03_modules/_domain_ex_sor/transaction_cost_optimizer/blueprint.md
# [MODULE] zephyr.ex_sor.services.transaction_cost_optimizer
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] zephyr.shared.contracts.enums.order_enums; zephyr.shared.foundation.errors
# [CONSUMERS] MOD-EX_SOR_EXT-002(ExecutionQualityScorer, 消费 TransactionCostResult); MOD-EX-CORE(成本报告)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 成本非负; 显性=佣金+印花税+过户费+监管费; 隐性=冲击+机会; 总=显性+隐性; 印花税仅卖方; 佣金有最低收费
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TransactionCostError; InvalidFeeScheduleError; InvalidCostInputError
# [TESTS] tests/ex_sor/test_transaction_cost_optimizer.py
# [A_module] module_id=MOD-EX_SOR_EXT-003 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Transaction Cost Optimizer — 交易成本优化器 (MOD-EX_SOR_EXT-003)

D-EX-SOR §2.1 XS-EXT-03: 佣金费率 + 印花税 + 冲击成本 + 机会成本 → 总成本最小化。

职责:
    - 计算 A 股交易全成本 (显性 + 隐性)
    - 分解为佣金/印花税/过户费/监管费/冲击成本/机会成本六项
    - 提供成本优化建议 (拆单/算法选择/时段选择)
    - 维护历史成本记录

A 股成本结构 (2023-08-28 印花税降后):
    显性成本 (Explicit):
        佣金       — 双边, 费率 0.025%~0.03%, 最低 5 元
        印花税     — 卖方单边, 0.05% (2023-08-28 由 0.1% 降至 0.05%)
        过户费     — 双边, 0.001% (2022-04-29 由 0.002% 降至 0.001%)
        监管费     — 双边, 0.002% (证监会规费)
    隐性成本 (Implicit):
        冲击成本   — 订单执行造成的价格变动 (vs 决策价)
        机会成本   — 未成交部分的错失收益

SSoT: depgraph MOD-EX_SOR_EXT-003
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 成交数据
#   fields: quantity成交数量 + avg_price平均成交价 + side买卖方向
#   code: calculate(...) L353
# - id: I2
#   name: A股费率表 FeeSchedule
#   fields: 佣金0.854bps(最低5元) + 印花税5bps(卖方) + 过户费0.1bps + 监管费0.2bps
#   code: FeeSchedule L126
# - id: I3
#   name: 隐性成本参数
#   fields: decision_price决策价 + unfilled_quantity未成交量 + adv日均量 + volatility日波动率
#   code: calculate(...) L361
# 层: 特征
# - id: F1
#   name_zh: 成交金额
#   name_en: notional
#   intro: 成交数量乘平均价得到的总金额, 一切费率的基数
#   formula: notional = quantity × avg_price, 保留2位
#   code: transaction_cost_optimizer.py L406
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F2
#   name_zh: 参与率
#   name_en: participation
#   intro: 成交量占日均量比例, 线性冲击估计的输入
#   formula: participation = quantity / adv
#   code: transaction_cost_optimizer.py L567
#   registry: factor_registry: 无FCT条目
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① 显性成本计算
#   name_en: TransactionCostOptimizer._calc_explicit
#   intro: 佣金+印花税+过户费+监管费四项法定费用逐项算金额
#   desc: 佣金=max(notional×0.854bps,5元); 印花税=notional×5bps仅卖方; 过户=notional×0.1bps; 监管=notional×0.2bps
#   inputs: F1 I2 I1
#   outputs: 显性成本+四项明细
#   invariant: 印花税仅卖方; 佣金有最低收费
# - id: A2
#   name_zh: ② 隐性成本计算
#   name_en: TransactionCostOptimizer._calc_implicit
#   intro: 冲击成本看成交价相对决策价的偏离, 没成交部分再算机会成本
#   desc: 冲击=±(avg_price-decision)×qty(负归0), 无决策价时用线性估计impact_bps=5×participation×vol_bps; 机会=unfilled×decision×0.001
#   inputs: I1 I3 F1 F2
#   outputs: 隐性成本+两项明细
#   invariant: 成本非负
# - id: A3
#   name_zh: ③ 总成本汇总
#   name_en: TransactionCostOptimizer.calculate
#   intro: 显性加隐性得总成本, 再折算成相对成交金额的基点
#   desc: total=explicit+implicit → total_cost_bps=total/notional×10000 → 留历史
#   inputs: A1 A2 F1
#   outputs: TransactionCostResult
#   invariant: 总=显性+隐性
# - id: A4
#   name_zh: ④ 成本优化建议
#   name_en: TransactionCostOptimizer.advise
#   intro: 找金额最大的成本项, 给出对应的降本建议和预估节省
#   desc: max(breakdown.amount)定主驱动 → 建议映射(协商费率/降换手/拆单/提成交率) → saving=total_bps×ratio
#   inputs: A3
#   outputs: OptimizationAdvice
# 层: 输出
# - id: O1
#   name_zh: 交易成本分析结果 TransactionCostResult
#   name_en: TransactionCostResult
#   intro: 六项成本分解+总成本(元/bps), 完整呈现这一单花了多少钱
#   downstream: MOD-EX_SOR_EXT-002(ExecutionQualityScorer,消费 TransactionCostResult); MOD-EX-CORE(成本报告)
# - id: O2
#   name_zh: 成本优化建议 OptimizationAdvice
#   name_en: OptimizationAdvice
#   intro: 主成本驱动项+降本建议+预估节省bps
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 -.->|断点| F1
# I1 -.->|断点| F2
# I3 -.->|断点| F2
# F1 --> A1
# I2 --> A1
# I1 --> A1
# I1 --> A2
# I3 --> A2
# F1 --> A2
# F2 --> A2
# A1 --> A3
# A2 --> A3
# F1 --> A3
# A3 --> A4
# A3 --> O1
# A4 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from enum import Enum
from typing import Final, Protocol

from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "CostComponent",
    "FeeSchedule",
    "TransactionCostBreakdown",
    "TransactionCostResult",
    "OptimizationAdvice",
    "CostPredictor",
    "ImpactCostEstimator",
    "TransactionCostOptimizer",
    "TransactionCostError",
    "InvalidFeeScheduleError",
    "InvalidCostInputError",
]

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# 常量
# ──────────────────────────────────────────────────────────────────────────────

_BPS_FACTOR: Final[Decimal] = Decimal("10000")
_ZERO: Final[Decimal] = Decimal("0")
_TWO: Final[Decimal] = Decimal("2")


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class TransactionCostError(ZephyrBaseError):
    """交易成本错误——通用基类。"""

    error_code = "ZA-XS-EXT-0003"


class InvalidFeeScheduleError(TransactionCostError):
    """费率表非法——费率为负或最低佣金为负。"""

    error_code = "ZA-XS-EXT-0003-FS"


class InvalidCostInputError(TransactionCostError):
    """成本输入非法——数量/价格为负或零。"""

    error_code = "ZA-XS-EXT-0003-CI"


# ──────────────────────────────────────────────────────────────────────────────
# 数据结构
# ──────────────────────────────────────────────────────────────────────────────


class CostComponent(Enum):
    """成本组件类型。

    约定 __str__ 返回 value, 统一日志格式。
    """

    def __str__(self) -> str:
        return self.value

    COMMISSION = "COMMISSION"  # 佣金 (券商收费)
    STAMP_DUTY = "STAMP_DUTY"  # 印花税 (卖方单边)
    TRANSFER_FEE = "TRANSFER_FEE"  # 过户费 (双边)
    REGULATORY_FEE = "REGULATORY_FEE"  # 监管费 (双边)
    IMPACT = "IMPACT"  # 冲击成本 (隐性)
    OPPORTUNITY = "OPPORTUNITY"  # 机会成本 (隐性)


@dataclass(frozen=True)
class FeeSchedule:
    """A 股交易费率表 (可配置, 默认 2023-08-28 后标准)。

    所有费率单位为 bps (万分之一)。

    Attributes:
        commission_rate_bps: 佣金费率 (双边, 默认 0.854bps = 万0.854, 国金miniQMT实盘费率)
        commission_min: 最低佣金 (元, 默认 5 元)
        stamp_duty_rate_bps: 印花税率 (卖方单边, 默认 5bps = 0.05%)
        transfer_fee_rate_bps: 过户费率 (双边, 默认 0.1bps = 0.001%)
        regulatory_fee_rate_bps: 监管费率 (双边, 默认 0.2bps = 0.002%)
    """

    commission_rate_bps: Decimal = Decimal("0.854")
    commission_min: Decimal = Decimal("5")
    stamp_duty_rate_bps: Decimal = Decimal("5")
    transfer_fee_rate_bps: Decimal = Decimal("0.1")
    regulatory_fee_rate_bps: Decimal = Decimal("0.2")

    def __post_init__(self) -> None:
        for name, val in [
            ("commission_rate_bps", self.commission_rate_bps),
            ("stamp_duty_rate_bps", self.stamp_duty_rate_bps),
            ("transfer_fee_rate_bps", self.transfer_fee_rate_bps),
            ("regulatory_fee_rate_bps", self.regulatory_fee_rate_bps),
        ]:
            if val < _ZERO:
                raise InvalidFeeScheduleError(
                    f"{name} 不能为负",
                    details={"field": name, "value": str(val)},
                )
        if self.commission_min < _ZERO:
            raise InvalidFeeScheduleError(
                "最低佣金不能为负",
                details={"commission_min": str(self.commission_min)},
            )


@dataclass(frozen=True)
class TransactionCostBreakdown:
    """单项成本明细。

    Attributes:
        component: 成本组件类型
        amount: 金额 (元)
        rate_bps: 费率 (bps, None=不适用)
        description: 描述
    """

    component: CostComponent
    amount: Decimal
    rate_bps: Decimal | None
    description: str


@dataclass(frozen=True)
class TransactionCostResult:
    """交易成本分析结果。

    Attributes:
        order_id: 订单 ID
        symbol: 标的代码
        side: 买卖方向
        quantity: 成交数量
        avg_price: 平均成交价
        notional: 成交金额 (元)
        explicit_cost: 显性成本 (佣金+税+费)
        implicit_cost: 隐性成本 (冲击+机会)
        total_cost: 总成本 (元)
        total_cost_bps: 总成本 (bps, 相对成交金额)
        breakdown: 成本明细列表
        analyzed_at: 分析时间
    """

    order_id: str
    symbol: str
    side: OrderSide
    quantity: Decimal
    avg_price: Decimal
    notional: Decimal
    explicit_cost: Decimal
    implicit_cost: Decimal
    total_cost: Decimal
    total_cost_bps: Decimal
    breakdown: list[TransactionCostBreakdown]
    analyzed_at: datetime

    @property
    def explicit_cost_bps(self) -> Decimal:
        """显性成本 (bps)。"""
        if self.notional == _ZERO:
            return _ZERO
        return self._round4(self.explicit_cost / self.notional * _BPS_FACTOR)

    @property
    def implicit_cost_bps(self) -> Decimal:
        """隐性成本 (bps)。"""
        if self.notional == _ZERO:
            return _ZERO
        return self._round4(self.implicit_cost / self.notional * _BPS_FACTOR)

    def breakdown_for(self, component: CostComponent) -> TransactionCostBreakdown | None:
        """按组件查询明细。"""
        for b in self.breakdown:
            if b.component is component:
                return b
        return None

    @staticmethod
    def _round4(value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class OptimizationAdvice:
    """成本优化建议。

    Attributes:
        primary_driver: 主要成本驱动项
        recommendation: 优化建议文本
        estimated_saving_bps: 预估节省 (bps, >=0)
        action: 建议动作
    """

    primary_driver: CostComponent
    recommendation: str
    estimated_saving_bps: Decimal
    action: str


# ──────────────────────────────────────────────────────────────────────────────
# 冲击成本估计器
# ──────────────────────────────────────────────────────────────────────────────


class ImpactCostEstimator(Protocol):
    """冲击成本估计器接口。"""

    def estimate(
        self,
        notional: Decimal,
        participation_rate: Decimal,
        volatility: Decimal,
    ) -> Decimal:
        """估计冲击成本 (元, >=0)。

        Args:
            notional: 成交金额 (元)
            participation_rate: 参与率 (order_qty / adv, 小数)
            volatility: 日波动率 (小数)
        """


class LinearImpactEstimator:
    """线性冲击模型估计器——impact = notional × rate × coeff × volatility。

    简化模型: impact_bps = coeff × participation_rate × volatility_bps
    理论对标: 线性冲击模型 (Kyle's lambda 简化版)
    """

    def __init__(self, coefficient: float = 5.0) -> None:
        """coefficient=5.0: 经验值, 1% 参与率 × 2% 波动率 → ~10bps 冲击。"""
        self._coeff = coefficient

    def estimate(
        self,
        notional: Decimal,
        participation_rate: Decimal,
        volatility: Decimal,
    ) -> Decimal:
        if notional <= _ZERO:
            return _ZERO
        pr = float(participation_rate) if participation_rate > _ZERO else 0.0
        vol_bps = float(volatility) * float(_BPS_FACTOR)
        impact_bps = self._coeff * pr * vol_bps
        impact_amount = notional * Decimal(str(impact_bps)) / _BPS_FACTOR
        return impact_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ──────────────────────────────────────────────────────────────────────────────
# 交易成本优化器
# ──────────────────────────────────────────────────────────────────────────────


class TransactionCostOptimizer:
    """交易成本优化器——全成本计算 + 分解 + 优化建议 + 历史追踪。

    用法:
        opt = TransactionCostOptimizer()
        result = opt.calculate(
            order_id="ORD-001",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=Decimal("1000"),
            avg_price=Decimal("10.50"),
            decision_price=Decimal("10.45"),  # 用于冲击成本
            unfilled_quantity=Decimal("200"),  # 用于机会成本
            adv=Decimal("1000000"),
            volatility=Decimal("0.02"),
        )
        # result.total_cost → 总成本 (元)
        # result.total_cost_bps → 总成本 (bps)
        # result.breakdown_for(CostComponent.STAMP_DUTY) → 印花税明细
    """

    def __init__(
        self,
        fee_schedule: FeeSchedule | None = None,
        impact_estimator: ImpactCostEstimator | None = None,
    ) -> None:
        self._fees = fee_schedule or FeeSchedule()
        self._impact_est = impact_estimator or LinearImpactEstimator()
        self._history: list[TransactionCostResult] = []

    # ── 属性 ──

    @property
    def history(self) -> list[TransactionCostResult]:
        """历史成本记录。"""
        return list(self._history)

    @property
    def fee_schedule(self) -> FeeSchedule:
        return self._fees

    # ── 成本计算入口 ──

    def calculate(
        self,
        order_id: str,
        symbol: str,
        side: OrderSide,
        quantity: Decimal,
        avg_price: Decimal,
        *,
        decision_price: Decimal | None = None,
        unfilled_quantity: Decimal = _ZERO,
        adv: Decimal | None = None,
        volatility: Decimal | None = None,
        now: datetime | None = None,
    ) -> TransactionCostResult:
        """计算交易全成本——显性 + 隐性 + 分解。

        Args:
            order_id: 订单 ID
            symbol: 标的代码
            side: 买卖方向
            quantity: 成交数量
            avg_price: 平均成交价
            decision_price: 决策价 (冲击成本基准, 可选)
            unfilled_quantity: 未成交数量 (机会成本用, 可选)
            adv: 日均成交量 (冲击成本用, 可选)
            volatility: 日波动率 (冲击成本用, 可选)
            now: 分析时间 (测试用)

        Returns:
            TransactionCostResult

        Raises:
            InvalidCostInputError: 数量/价格非法
        """
        now = now or datetime.now(timezone.utc)

        # 1. 校验输入
        if quantity <= _ZERO:
            raise InvalidCostInputError(
                "成交数量必须为正",
                details={"order_id": order_id, "quantity": str(quantity)},
            )
        if avg_price <= _ZERO:
            raise InvalidCostInputError(
                "成交价必须为正",
                details={"order_id": order_id, "avg_price": str(avg_price)},
            )
        if unfilled_quantity < _ZERO:
            raise InvalidCostInputError(
                "未成交数量不能为负",
                details={"unfilled_quantity": str(unfilled_quantity)},
            )

        notional = self._round2(quantity * avg_price)
        breakdown: list[TransactionCostBreakdown] = []

        # 2. 显性成本
        explicit = self._calc_explicit(side, notional, breakdown)

        # 3. 隐性成本
        implicit = self._calc_implicit(
            side,
            quantity,
            avg_price,
            notional,
            decision_price,
            unfilled_quantity,
            adv,
            volatility,
            breakdown,
        )

        total_cost = self._round2(explicit + implicit)
        total_bps = self._round4(total_cost / notional * _BPS_FACTOR) if notional > _ZERO else _ZERO

        result = TransactionCostResult(
            order_id=order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            avg_price=avg_price,
            notional=notional,
            explicit_cost=explicit,
            implicit_cost=implicit,
            total_cost=total_cost,
            total_cost_bps=total_bps,
            breakdown=breakdown,
            analyzed_at=now,
        )
        self._history.append(result)
        logger.info(
            "TransactionCost: order=%s total=%s (%s bps) explicit=%s implicit=%s",
            order_id,
            total_cost,
            total_bps,
            explicit,
            implicit,
        )
        return result

    # ── 显性成本 ──

    def _calc_explicit(
        self,
        side: OrderSide,
        notional: Decimal,
        breakdown: list[TransactionCostBreakdown],
    ) -> Decimal:
        """计算显性成本: 佣金 + 印花税 + 过户费 + 监管费。"""
        fees = self._fees
        total = _ZERO

        # 佣金 (双边, 有最低收费)
        commission_raw = notional * fees.commission_rate_bps / _BPS_FACTOR
        commission = max(commission_raw, fees.commission_min)
        commission = self._round2(commission)
        breakdown.append(
            TransactionCostBreakdown(
                component=CostComponent.COMMISSION,
                amount=commission,
                rate_bps=fees.commission_rate_bps,
                description=f"佣金 (费率 {fees.commission_rate_bps}bps, 最低 {fees.commission_min} 元)",
            )
        )
        total += commission

        # 印花税 (仅卖方)
        if side is OrderSide.SELL:
            stamp_duty = self._round2(notional * fees.stamp_duty_rate_bps / _BPS_FACTOR)
            breakdown.append(
                TransactionCostBreakdown(
                    component=CostComponent.STAMP_DUTY,
                    amount=stamp_duty,
                    rate_bps=fees.stamp_duty_rate_bps,
                    description=f"印花税 (卖方, {fees.stamp_duty_rate_bps}bps)",
                )
            )
            total += stamp_duty
        else:
            breakdown.append(
                TransactionCostBreakdown(
                    component=CostComponent.STAMP_DUTY,
                    amount=_ZERO,
                    rate_bps=fees.stamp_duty_rate_bps,
                    description="印花税 (买方免征)",
                )
            )

        # 过户费 (双边)
        transfer = self._round2(notional * fees.transfer_fee_rate_bps / _BPS_FACTOR)
        breakdown.append(
            TransactionCostBreakdown(
                component=CostComponent.TRANSFER_FEE,
                amount=transfer,
                rate_bps=fees.transfer_fee_rate_bps,
                description=f"过户费 (双边, {fees.transfer_fee_rate_bps}bps)",
            )
        )
        total += transfer

        # 监管费 (双边)
        regulatory = self._round2(notional * fees.regulatory_fee_rate_bps / _BPS_FACTOR)
        breakdown.append(
            TransactionCostBreakdown(
                component=CostComponent.REGULATORY_FEE,
                amount=regulatory,
                rate_bps=fees.regulatory_fee_rate_bps,
                description=f"监管费 (双边, {fees.regulatory_fee_rate_bps}bps)",
            )
        )
        total += regulatory

        return self._round2(total)

    # ── 隐性成本 ──

    def _calc_implicit(
        self,
        side: OrderSide,
        quantity: Decimal,
        avg_price: Decimal,
        notional: Decimal,
        decision_price: Decimal | None,
        unfilled_quantity: Decimal,
        adv: Decimal | None,
        volatility: Decimal | None,
        breakdown: list[TransactionCostBreakdown],
    ) -> Decimal:
        """计算隐性成本: 冲击成本 + 机会成本。"""
        total = _ZERO

        # 冲击成本 (需 decision_price)
        impact = _ZERO
        if decision_price is not None and decision_price > _ZERO:
            if side is OrderSide.BUY:
                # BUY: 成交价 > 决策价 → 冲击成本
                impact_per_share = avg_price - decision_price
            else:
                # SELL: 成交价 < 决策价 → 冲击成本
                impact_per_share = decision_price - avg_price
            impact = self._round2(impact_per_share * quantity)
            if impact < _ZERO:
                impact = _ZERO  # 有利执行不算成本
            breakdown.append(
                TransactionCostBreakdown(
                    component=CostComponent.IMPACT,
                    amount=impact,
                    rate_bps=None,
                    description=f"冲击成本 (成交价 {avg_price} vs 决策价 {decision_price})",
                )
            )
        else:
            # 用估计器 (需 adv + volatility)
            if adv is not None and adv > _ZERO and volatility is not None:
                participation = quantity / adv
                impact = self._impact_est.estimate(notional, participation, volatility)
                breakdown.append(
                    TransactionCostBreakdown(
                        component=CostComponent.IMPACT,
                        amount=impact,
                        rate_bps=None,
                        description=f"冲击成本 (估计, 参与率 {participation:.4f})",
                    )
                )
            else:
                breakdown.append(
                    TransactionCostBreakdown(
                        component=CostComponent.IMPACT,
                        amount=_ZERO,
                        rate_bps=None,
                        description="冲击成本 (未提供决策价/ADV, 跳过)",
                    )
                )
        total += impact

        # 机会成本 (未成交部分)
        opportunity = _ZERO
        if unfilled_quantity > _ZERO:
            if decision_price is not None and decision_price > _ZERO:
                if side is OrderSide.BUY:
                    # BUY 未成交: 后续需更高价买入 → 机会成本
                    opportunity = self._round2(unfilled_quantity * decision_price * Decimal("0.001"))
                else:
                    # SELL 未成交: 后续需更低价卖出 → 机会成本
                    opportunity = self._round2(unfilled_quantity * decision_price * Decimal("0.001"))
                breakdown.append(
                    TransactionCostBreakdown(
                        component=CostComponent.OPPORTUNITY,
                        amount=opportunity,
                        rate_bps=None,
                        description=f"机会成本 (未成交 {unfilled_quantity} 股)",
                    )
                )
            else:
                breakdown.append(
                    TransactionCostBreakdown(
                        component=CostComponent.OPPORTUNITY,
                        amount=_ZERO,
                        rate_bps=None,
                        description="机会成本 (未提供决策价, 跳过)",
                    )
                )
        else:
            breakdown.append(
                TransactionCostBreakdown(
                    component=CostComponent.OPPORTUNITY,
                    amount=_ZERO,
                    rate_bps=None,
                    description="机会成本 (全部成交, 无机会成本)",
                )
            )
        total += opportunity

        return self._round2(total)

    # ── 优化建议 ──

    def advise(self, result: TransactionCostResult) -> OptimizationAdvice:
        """生成成本优化建议——找最大成本驱动项 + 对应建议。"""
        if not result.breakdown:
            return OptimizationAdvice(
                primary_driver=CostComponent.COMMISSION,
                recommendation="无成本明细, 无法建议",
                estimated_saving_bps=_ZERO,
                action="none",
            )

        # 找最大成本驱动项
        max_item = max(result.breakdown, key=lambda b: b.amount)
        if max_item.amount <= _ZERO:
            return OptimizationAdvice(
                primary_driver=CostComponent.COMMISSION,
                recommendation="成本为零, 无需优化",
                estimated_saving_bps=_ZERO,
                action="none",
            )

        # 根据驱动项给建议
        advice_map: dict[CostComponent, tuple[str, str, float]] = {
            CostComponent.COMMISSION: (
                "佣金为主要成本, 建议与券商协商费率或增大交易量获取阶梯优惠",
                "negotiate_rate",
                0.3,  # 预估可省 30%
            ),
            CostComponent.STAMP_DUTY: (
                "印花税为法定税率不可调, 建议减少卖出频率 (降低换手率)",
                "reduce_turnover",
                0.0,
            ),
            CostComponent.IMPACT: (
                "冲击成本为主要成本, 建议使用 TWAP/VWAP 拆单或降低参与率",
                "use_algo_split",
                0.4,
            ),
            CostComponent.OPPORTUNITY: (
                "机会成本较高, 建议提高成交率 (放宽限价或使用更激进的算法)",
                "increase_fill_rate",
                0.5,
            ),
            CostComponent.TRANSFER_FEE: (
                "过户费占比低, 优化空间有限",
                "none",
                0.0,
            ),
            CostComponent.REGULATORY_FEE: (
                "监管费占比低, 优化空间有限",
                "none",
                0.0,
            ),
        }
        rec, action, saving_ratio = advice_map.get(max_item.component, ("无建议", "none", 0.0))
        saving_bps = self._round4(result.total_cost_bps * Decimal(str(saving_ratio)))
        return OptimizationAdvice(
            primary_driver=max_item.component,
            recommendation=rec,
            estimated_saving_bps=saving_bps,
            action=action,
        )

    # ── 历史查询 ──

    def get_history(self, symbol: str | None = None) -> list[TransactionCostResult]:
        """查询历史成本记录 (可按 symbol 过滤)。"""
        if symbol is None:
            return list(self._history)
        return [r for r in self._history if r.symbol == symbol]

    def clear_history(self) -> None:
        self._history.clear()

    # ── 辅助 ──

    @staticmethod
    def _round2(value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def _round4(value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
