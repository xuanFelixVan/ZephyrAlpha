# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.pricing_policy
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib; zephyr.ex_core.price_cage; zephyr.shared.contracts.enums.order_enums
# [CONSUMERS] ex_core.trading_session ; ex_core.adapters.miniqmt_broker ; ex_core.open_order_resolver
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 被动档买一卖一/主动档对手价/涨停卖单挂涨停/跌停买单挂跌停;挂单价仍须过价格笼子校验;零价无盘口兜底前收盘
# [MODIFY-GUARD] 40_execution_broker.md §决策⑭
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PricingPolicyError
# [TESTS] tests/ex_core/test_pricing_policy.py
# [TTL] permanent

"""

挂单价算法（40_execution_broker §决策⑭ gap 9 施工）。

v1.0.0 拆单算法（TWAP/VWAP 切片）讲了"怎么拆"，但每个子单的具体挂单价未定义——
这是 TWAP/VWAP 落地的最后一公里。本模块补全挂单价决策。

挂单价规则（§2.15 决策⑭）：
  | 订单类型                  | 默认挂单价       | 理由                          |
  |--------------------------|------------------|-------------------------------|
  | 被动买单                  | 买一价（bid1）   | 不跨价，省 spread，排队等成交 |
  | 被动卖单                  | 卖一价（ask1）   | 不跨价，省 spread，排队等成交 |
  | 主动买单（Make-or-Take）  | 卖一价（ask1）   | 跨价吃单，保证成交            |
  | 主动卖单（Make-or-Take）  | 买一价（bid1）   | 跨价吃单，保证成交            |
  | 涨停板卖单                | 涨停价           | 唯一可能成交的价位（排队）    |
  | 跌停板买单                | 跌停价           | 唯一可能成交的价位（排队）    |
  | 提1tick中间档(Phase 1.5)  | 买一+1tick/卖一-1tick | 极小成本换成交确定性     |

为何默认被动档：
  - 个人账户小资金多数订单 <1% ADV，被动挂单排队足够成交
  - 被动档省 spread（A 股 spread 约 1-2 tick，被动档比主动档省 1-2 tick 成本）
  - 主动吃单只作兜底（Make-or-Take），不作为默认

为何不挂 mid 价：A 股最小变动单位 0.01 元，mid 价常落在两个 tick 之间，无法挂单；
且挂 mid 等于既不占买一也不占卖一，成交概率更低。

为何不挂对手价作默认：主动档跨价吃单，每笔都付 spread，小单累积成本高。
仅 urgency 高（打板）或超时兜底时用。

与价格笼子协同（决策⑭ §2.15 价格笼子校验）：
  本模块只计算挂单价，不校验笼子。调用方拿到挂单价后须调用
  price_cage.check_price_cage 校验并夹边（连续竞价限价单合规硬约束）。
  正常 spread（1-2 tick）远小于 2% 笼子，被动档/Make-or-Take 正常不触发；
  低流动性票 spread 大时 Make-or-Take 对手价可能超笼子→调用方夹到笼子边界。

依据：40_execution_broker.md v2.4.0 §决策⑭
Version: 1.0.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 盘口上下文 PricingContext
#   fields: symbol/side + ask1卖一/bid1买一/last_price最新价/prev_close前收盘/limit_up涨停价/limit_down跌停价（均可空）
#   code: PricingContext (pricing_policy.py L96)
# - id: I2
#   name: 挂单档位 PricingTier 枚举
#   fields: PASSIVE被动/ACTIVE主动/LIMIT_UP_SELL涨停卖/LIMIT_DOWN_BUY跌停买/ONE_TICK_INSIDE提1tick
#   code: PricingTier (pricing_policy.py L82)
# - id: I3
#   name: 最小变动价位 PRICE_TICK 常量
#   fields: 0.01元（A股tick，量化与提1tick用）
#   code: price_cage.PRICE_TICK (pricing_policy.py L61)
# 层: 算法
# - id: A1
#   name_zh: ① 五档挂单价决策分发
#   name_en: PricingPolicy.decide
#   intro: 按档位分发到对应定价逻辑，结果统一量化到0.01 tick
#   desc: LIMIT_UP_SELL/LIMIT_DOWN_BUY走涨跌停档；ACTIVE走对手价；ONE_TICK_INSIDE走提1tick；默认PASSIVE被动档；最终_round_to_tick量化（L177-214）
#   inputs: I1 I2 I3
#   outputs: PricingDecision（price/tier/fallback_used/reason）
#   invariant: 被动档买一卖一/主动档对手价/涨停卖单挂涨停/跌停买单挂跌停
# - id: A2
#   name_zh: ② 盘口最优价解析
#   name_en: _own_price / _opponent_price
#   intro: 买单己方=买一对手=卖一，卖单反之，供各档选价
#   desc: side=BUY→own=bid1,opponent=ask1；SELL反之（L341-353）
#   inputs: I1
#   outputs: 己方价own/对手价opponent（可None）
# - id: A3
#   name_zh: ③ 被动/主动档选价与回退链
#   name_en: _pick_passive / _pick_active
#   intro: 优先盘口己方/对手价，无盘口按last_price→prev_close回退，主动档最后兜底己方±1tick估算
#   desc: 被动档取own，主动档取opponent；均无则last→prev_close；主动档仍无则own±1tick；全无→raise PricingPolicyError（L297-337）
#   inputs: A2 I1
#   outputs: (价格, 是否回退, 理由)
#   invariant: 零价无盘口兜底前收盘
# - id: A4
#   name_zh: ④ 涨跌停档定价
#   name_en: _decide_limit_up_sell / _decide_limit_down_buy
#   intro: 涨停卖单挂涨停价、跌停买单挂跌停价，是唯一可成交的排队价位
#   desc: limit_up/down_price缺失或<=0时用prev_close×(1±10%)估算；prev_close也无→raise PricingPolicyError（L218-261）
#   inputs: I1
#   outputs: 涨停/跌停挂单价
#   invariant: 涨跌停价与prev_close均无→报错不瞎挂
# - id: A5
#   name_zh: ⑤ 提1tick中间档
#   name_en: _decide_one_tick_inside
#   intro: 买单买一+1tick、卖单卖一-1tick，极小成本换成交确定性
#   desc: own缺失回退被动档逻辑；BUY→own+PRICE_TICK，SELL→own-PRICE_TICK（L263-295）
#   inputs: A2 I3
#   outputs: 提1tick挂单价
# 层: 输出
# - id: O1
#   name_zh: 挂单价决策 PricingDecision
#   name_en: PricingDecision
#   intro: 含挂单价/生效档位/是否盘口回退/人类可读理由，调用方须再过价格笼子校验后下单
#   invariant: price已量化到0.01 tick；挂单价仍须过price_cage校验
#   downstream: ex_core.trading_session / ex_core.adapters.miniqmt_broker / ex_core.open_order_resolver
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I1 --> A2
# A2 --> A3
# I1 --> A3
# A2 --> A5
# I3 --> A5
# I1 --> A4
# A1 --> A3
# A1 --> A4
# A1 --> A5
# A3 --> O1
# A4 --> O1
# A5 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Final

from zephyr.ex_core.price_cage import PRICE_TICK
from zephyr.shared.contracts.enums.order_enums import OrderSide

__all__: Final = [
    "PricingTier",
    "PricingContext",
    "PricingDecision",
    "PricingPolicyError",
    "PricingPolicy",
    "compute_quote_price",
]

_logger = logging.getLogger(__name__)


class PricingPolicyError(Exception):
    """挂单价计算错误。"""

    error_code = "ZA-XC-0011"


class PricingTier(str, Enum):
    """挂单价档位。

    决定挂单价的"主动程度"——越主动越保证成交但成本越高。
    """

    PASSIVE = "passive"  # 被动档：买一/卖一，省 spread，排队等成交
    ACTIVE = "active"  # 主动档：对手价（卖一/买一），跨价吃单保证成交
    LIMIT_UP_SELL = "limit_up_sell"  # 涨停板卖单：挂涨停价（唯一可成交价位）
    LIMIT_DOWN_BUY = "limit_down_buy"  # 跌停板买单：挂跌停价（唯一可成交价位）
    ONE_TICK_INSIDE = "one_tick_inside"  # 提1tick中间档（Phase 1.5 候选）


@dataclass(frozen=True)
class PricingContext:
    """挂单价计算上下文（盘口快照）。

    Attributes:
        symbol: 股票代码
        side: 买卖方向
        ask1: 卖一价（None=无卖盘）
        bid1: 买一价（None=无买盘）
        last_price: 最新成交价（盘口回退用）
        prev_close: 前收盘价（涨跌停计算基准 + 盘口回退兜底）
        limit_up_price: 涨停价（None=用 prev_close×1.1 估算）
        limit_down_price: 跌停价（None=用 prev_close×0.9 估算）
    """

    symbol: str
    side: OrderSide
    ask1: Decimal | None = None
    bid1: Decimal | None = None
    last_price: Decimal | None = None
    prev_close: Decimal | None = None
    limit_up_price: Decimal | None = None
    limit_down_price: Decimal | None = None


@dataclass(frozen=True)
class PricingDecision:
    """挂单价决策结果（不可变，用于审计/日志）。

    Attributes:
        price: 计算出的挂单价
        tier: 实际生效的档位
        fallback_used: 是否使用了盘口回退（True=盘口无数据用了 last_price/prev_close）
        reason: 决策理由（人类可读）
    """

    price: Decimal
    tier: PricingTier
    fallback_used: bool
    reason: str


# A 股涨跌停幅度（2026-07-06 规则修订：主板/ST ±10%，创业板/科创板 ±20%，北交所 ±30%；
# 板块分类真源=ex_core.board_lot.classify_board，板块幅度表=miniqmt_broker._BOARD_PRICE_LIMIT_PCT）
# 这里用通用 10% 作为无明确涨停价时的估算，调用方应优先传入 exchange 提供的精确涨停价
_DEFAULT_LIMIT_UP_PCT = Decimal("0.10")
_DEFAULT_LIMIT_DOWN_PCT = Decimal("0.10")


def _round_to_tick(price: Decimal) -> Decimal:
    """量化到最小价格变动单位（0.01）。"""
    return price.quantize(PRICE_TICK)


class PricingPolicy:
    """挂单价决策器。

    根据订单方向、盘口快照、涨跌停状态决定挂单价。
    支持 PASSIVE / ACTIVE / LIMIT_UP_SELL / LIMIT_DOWN_BUY / ONE_TICK_INSIDE 五档。

    用法:
        policy = PricingPolicy()

        # 1. 被动档挂单（默认，省 spread）
        ctx = PricingContext(symbol="600000.SH", side=OrderSide.BUY,
                             ask1=Decimal("10.05"), bid1=Decimal("10.04"))
        decision = policy.decide(ctx, tier=PricingTier.PASSIVE)
        # decision.price == 10.04（买一价）

        # 2. 涨停板卖单（涨停价卖单挂涨停价排队）
        ctx = PricingContext(symbol="600000.SH", side=OrderSide.SELL,
                             prev_close=Decimal("10.00"),
                             limit_up_price=Decimal("11.00"))
        decision = policy.decide(ctx, tier=PricingTier.LIMIT_UP_SELL)
        # decision.price == 11.00（涨停价）

    设计要点:
      - **无副作用**：纯函数式决策，不改盘口状态
      - **盘口回退**：无 ask1/bid1 时回退到 last_price → prev_close
      - **审计友好**：返回 PricingDecision 含理由，可记录到审计日志
      - **与价格笼子解耦**：只算挂单价，笼子校验由调用方另行调用 price_cage
    """

    def decide(
        self,
        ctx: PricingContext,
        tier: PricingTier = PricingTier.PASSIVE,
    ) -> PricingDecision:
        """计算挂单价。

        Args:
            ctx: 盘口上下文
            tier: 挂单档位（默认 PASSIVE）

        Returns:
            PricingDecision 决策结果

        Raises:
            PricingPolicyError: 无任何可用价格（盘口+last+prev_close 均无）
        """
        if tier is PricingTier.LIMIT_UP_SELL:
            return self._decide_limit_up_sell(ctx)
        if tier is PricingTier.LIMIT_DOWN_BUY:
            return self._decide_limit_down_buy(ctx)

        # PASSIVE / ACTIVE / ONE_TICK_INSIDE 都需要盘口
        opponent = self._opponent_price(ctx)  # 主动档对手价
        own = self._own_price(ctx)  # 被动档己方价

        if tier is PricingTier.ACTIVE:
            price, fallback, reason = self._pick_active(ctx, opponent, own)
            return PricingDecision(price=_round_to_tick(price), tier=tier, fallback_used=fallback, reason=reason)

        if tier is PricingTier.ONE_TICK_INSIDE:
            return self._decide_one_tick_inside(ctx, own)

        # 默认 PASSIVE
        price, fallback, reason = self._pick_passive(ctx, own, opponent)
        return PricingDecision(
            price=_round_to_tick(price), tier=PricingTier.PASSIVE, fallback_used=fallback, reason=reason
        )

    # ── 档位实现 ──

    def _decide_limit_up_sell(self, ctx: PricingContext) -> PricingDecision:
        """涨停板卖单：挂涨停价（唯一可能成交的价位，排队）。"""
        price = ctx.limit_up_price
        if price is None or price <= 0:
            # 回退：用 prev_close × (1+10%) 估算
            if ctx.prev_close and ctx.prev_close > 0:
                price = ctx.prev_close * (Decimal("1") + _DEFAULT_LIMIT_UP_PCT)
                _logger.warning(
                    "涨停价未知 symbol=%s，用 prev_close×1.1 估算=%s",
                    ctx.symbol,
                    price,
                )
            else:
                raise PricingPolicyError(
                    f"涨停板卖单无法计算涨停价：symbol={ctx.symbol} limit_up_price 和 prev_close 均无"
                )
        return PricingDecision(
            price=_round_to_tick(price),
            tier=PricingTier.LIMIT_UP_SELL,
            fallback_used=ctx.limit_up_price is None,
            reason=f"涨停板卖单挂涨停价 {price}（排队等成交）",
        )

    def _decide_limit_down_buy(self, ctx: PricingContext) -> PricingDecision:
        """跌停板买单：挂跌停价（唯一可能成交的价位，排队）。"""
        price = ctx.limit_down_price
        if price is None or price <= 0:
            if ctx.prev_close and ctx.prev_close > 0:
                price = ctx.prev_close * (Decimal("1") - _DEFAULT_LIMIT_DOWN_PCT)
                _logger.warning(
                    "跌停价未知 symbol=%s，用 prev_close×0.9 估算=%s",
                    ctx.symbol,
                    price,
                )
            else:
                raise PricingPolicyError(
                    f"跌停板买单无法计算跌停价：symbol={ctx.symbol} limit_down_price 和 prev_close 均无"
                )
        return PricingDecision(
            price=_round_to_tick(price),
            tier=PricingTier.LIMIT_DOWN_BUY,
            fallback_used=ctx.limit_down_price is None,
            reason=f"跌停板买单挂跌停价 {price}（排队等成交）",
        )

    def _decide_one_tick_inside(self, ctx: PricingContext, own: Decimal | None) -> PricingDecision:
        """提1tick中间档：买单挂买一+1tick、卖单挂卖一-1tick。

        Phase 1.5 候选策略：以极小成本（0.01元/股）换取成交确定性，避开盘口拥堵区。
        适合 urgency 中等的订单（如多因子建仓）。
        """
        if own is None or own <= 0:
            # 无盘口回退到被动档逻辑
            price, fallback, reason = self._pick_passive(ctx, own, self._opponent_price(ctx))
            return PricingDecision(
                price=_round_to_tick(price),
                tier=PricingTier.ONE_TICK_INSIDE,
                fallback_used=fallback,
                reason=f"提1tick无盘口回退：{reason}",
            )
        if ctx.side is OrderSide.BUY:
            # 买单：买一 + 1 tick（更积极，但仍是限价单排队）
            price = own + PRICE_TICK
            reason = f"提1tick买单：买一 {own} + 1tick = {price}"
        else:
            # 卖单：卖一 - 1 tick
            price = own - PRICE_TICK
            reason = f"提1tick卖单：卖一 {own} - 1tick = {price}"
        return PricingDecision(
            price=_round_to_tick(price),
            tier=PricingTier.ONE_TICK_INSIDE,
            fallback_used=False,
            reason=reason,
        )

    def _pick_passive(
        self,
        ctx: PricingContext,
        own: Decimal | None,
        opponent: Decimal | None,
    ) -> tuple[Decimal, bool, str]:
        """被动档选价：优先己方最优价，回退到 last/prev_close。"""
        if own is not None and own > 0:
            label = "买一" if ctx.side is OrderSide.BUY else "卖一"
            return own, False, f"被动档{label}价 {own}（省 spread 排队等成交）"
        # 回退链：last_price → prev_close
        if ctx.last_price is not None and ctx.last_price > 0:
            return ctx.last_price, True, f"无盘口回退最新价 {ctx.last_price}"
        if ctx.prev_close is not None and ctx.prev_close > 0:
            return ctx.prev_close, True, f"无盘口回退前收盘价 {ctx.prev_close}"
        raise PricingPolicyError(f"被动档无可用价格 symbol={ctx.symbol} side={ctx.side.value}")

    def _pick_active(
        self,
        ctx: PricingContext,
        opponent: Decimal | None,
        own: Decimal | None,
    ) -> tuple[Decimal, bool, str]:
        """主动档选价：优先对手方最优价，回退到 last/prev_close。"""
        if opponent is not None and opponent > 0:
            label = "卖一" if ctx.side is OrderSide.BUY else "买一"
            return opponent, False, f"主动档{label}价 {opponent}（跨价吃单保证成交）"
        # 回退链
        if ctx.last_price is not None and ctx.last_price > 0:
            return ctx.last_price, True, f"主动档无对手价回退最新价 {ctx.last_price}"
        if ctx.prev_close is not None and ctx.prev_close > 0:
            return ctx.prev_close, True, f"主动档无对手价回退前收盘价 {ctx.prev_close}"
        # 最后兜底：用己方价 + 1tick（模拟对手价）
        if own is not None and own > 0:
            estimated = own + PRICE_TICK if ctx.side is OrderSide.BUY else own - PRICE_TICK
            return estimated, True, f"主动档无对手价用己方价±1tick估算 {estimated}"
        raise PricingPolicyError(f"主动档无可用价格 symbol={ctx.symbol} side={ctx.side.value}")

    # ── 盘口解析 ──

    @staticmethod
    def _opponent_price(ctx: PricingContext) -> Decimal | None:
        """对手方最优价：买单→ask1，卖单→bid1。"""
        if ctx.side is OrderSide.BUY:
            return ctx.ask1
        return ctx.bid1

    @staticmethod
    def _own_price(ctx: PricingContext) -> Decimal | None:
        """己方最优价：买单→bid1，卖单→ask1。"""
        if ctx.side is OrderSide.BUY:
            return ctx.bid1
        return ctx.ask1


# ── 函数式入口 ──


def compute_quote_price(
    ctx: PricingContext,
    tier: PricingTier = PricingTier.PASSIVE,
) -> PricingDecision:
    """计算挂单价（函数式入口，便于一行调用）。

    Args:
        ctx: 盘口上下文
        tier: 挂单档位（默认 PASSIVE）

    Returns:
        PricingDecision 决策结果

    Example:
        >>> from decimal import Decimal
        >>> ctx = PricingContext(
        ...     symbol="600000.SH", side=OrderSide.BUY,
        ...     ask1=Decimal("10.05"), bid1=Decimal("10.04"),
        ... )
        >>> decision = compute_quote_price(ctx, PricingTier.PASSIVE)
        >>> decision.price
        Decimal('10.04')
    """
    return PricingPolicy().decide(ctx, tier)
