# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.matching_engine
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.portfolio
# [CONSUMERS] zephyr.backtest.implementations.vectorized_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] A股约束: T+1/涨跌停/停牌/100股整数倍; 手续费/滑点实际扣除
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] MatchingError
# [TESTS]
# [A_module] module_id=MOD-BT-001-matching_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""回测撮合引擎模块

职责:
  - 根据目标权重生成买卖订单
  - 应用滑点模型(流动性+市场冲击)
  - 计算手续费(券商佣金+印花税+过户费)
  - A股约束:100股整数倍/涨跌停/停牌/T+1

约束:
  - 撮合为市价单(按当日收盘价成交,MVP简化)
  - 滑点:固定bps模型(MVP),后续可扩展为流动性+市场冲击模型
  - 手续费:券商佣金(万三,最低5元)+印花税(卖出0.1%)
  - 涨跌停:价格触及涨跌停板时不成交
  - 停牌:无数据时不成交

SSoT: docs/03_modules/_domain_backtest/blueprint.md §3.2 §5.1
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional

from zephyr.backtest.core.portfolio import BacktestFill, Portfolio


class MatchingError(Exception):
    """撮合引擎错误"""


@dataclass
class MatchingConfig:
    """撮合配置

    Attributes:
        commission_rate: 券商佣金费率(万三=0.0003)
        slippage_bps: 滑点(bps,1bp=0.01%)
        stamp_tax_rate: 印花税率(卖出0.1%=0.001)
        min_commission: 最低佣金(5元)
        lot_size: 最小交易单位(A股100股)
        price_limit_pct: 涨跌停板限制(10%=0.10, ST股5%=0.05)
    """

    commission_rate: Decimal = Decimal("0.0003")
    slippage_bps: Decimal = Decimal("1")
    stamp_tax_rate: Decimal = Decimal("0.001")
    min_commission: Decimal = Decimal("5")
    lot_size: int = 100
    price_limit_pct: Decimal = Decimal("0.10")


class MatchingEngine:
    """回测撮合引擎

    根据目标权重生成买卖订单,应用滑点和手续费,产出BacktestFill列表。

    撮合逻辑:
    1. 计算当前总NAV(现金+市值)
    2. 对每个symbol计算目标持仓金额 = NAV * target_weight
    3. 计算目标数量 = floor(目标金额 / price / lot_size) * lot_size
    4. 差额 = 目标数量 - 当前持仓
    5. 先卖后买(避免现金不足)

    A股约束:
    - 100股整数倍(买入)
    - 涨跌停不成交(需前一日收盘价作为基准,MVP简化:跳过涨跌停检查)
    - 停牌不成交(无价格数据时跳过)
    - T+1由Portfolio负责(matching_engine只生成fills)

    Usage:
        engine = MatchingEngine(config=MatchingConfig(...))
        fills = engine.generate_fills(
            target_weights={"000001.SZ": 0.5, "600000.SH": 0.5},
            prices={"000001.SZ": Decimal("10.5"), "600000.SH": Decimal("8.3")},
            portfolio=portfolio,
            date="2024-01-15",
        )
        for fill in fills:
            portfolio.apply_fill(fill)
    """

    def __init__(self, config: Optional[MatchingConfig] = None):
        """初始化撮合引擎

        Args:
            config: 撮合配置(可选,默认使用MatchingConfig默认值)
        """
        self._config = config or MatchingConfig()

    def generate_fills(
        self,
        target_weights: dict[str, float],
        prices: dict[str, Decimal],
        portfolio: Portfolio,
        date: Any,
        prev_close: Optional[dict[str, Decimal]] = None,
    ) -> list[BacktestFill]:
        """根据目标权重生成成交记录

        Args:
            target_weights: {symbol: weight} 目标权重(0.0-1.0, sum<=1.0)
            prices: {symbol: price} 当日价格
            portfolio: 当前持仓
            date: 当前日期
            prev_close: 前一日收盘价(可选,用于涨跌停检查)

        Returns:
            BacktestFill列表(先卖后买排序)

        Raises:
            MatchingError: 参数无效
        """
        if not target_weights:
            return []

        if not prices:
            raise MatchingError("prices不能为空")

        # 计算当前总NAV
        total_nav = portfolio.total_nav(prices)
        if total_nav <= 0:
            raise MatchingError(f"总NAV必须>0, got {total_nav}")

        # 计算目标持仓和差额
        orders: list[dict] = []  # 待执行订单

        for symbol, weight in target_weights.items():
            if weight <= 0:
                continue

            price = prices.get(symbol)
            if price is None or price <= 0:
                # 停牌或无数据,跳过
                continue

            # 涨跌停检查(MVP简化:有prev_close时才检查)
            if prev_close and self._is_price_limit(symbol, price, prev_close.get(symbol)):
                continue

            # 计算目标数量(100股整数倍)
            target_value = total_nav * Decimal(str(weight))
            target_qty = int(target_value / price / self._config.lot_size) * self._config.lot_size

            # 当前持仓
            current_pos = portfolio.get_position(symbol)
            current_qty = current_pos.quantity if current_pos else Decimal("0")

            # 差额
            diff = Decimal(target_qty) - current_qty

            if diff > 0:
                # 买入
                orders.append({"side": "BUY", "symbol": symbol, "quantity": diff, "price": price})
            elif diff < 0:
                # 卖出
                orders.append({"side": "SELL", "symbol": symbol, "quantity": abs(diff), "price": price})

        # 先卖后买(避免现金不足)
        orders.sort(key=lambda o: 0 if o["side"] == "SELL" else 1)

        # 生成fills
        fills: list[BacktestFill] = []
        for order in orders:
            fill = self._create_fill(date, order)
            if fill is not None:
                fills.append(fill)

        return fills

    def _create_fill(self, date: Any, order: dict) -> Optional[BacktestFill]:
        """创建成交记录(含滑点和手续费)

        Args:
            date: 成交日期
            order: 订单字典(side/symbol/quantity/price)

        Returns:
            BacktestFill对象(无成交返回None)
        """
        symbol = order["symbol"]
        side = order["side"]
        quantity = order["quantity"]
        base_price = order["price"]

        if quantity <= 0:
            return None

        # 应用滑点
        fill_price = self._apply_slippage(base_price, side)

        # 计算手续费
        commission = self._calc_commission(quantity, fill_price, side)

        return BacktestFill(
            date=date,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=fill_price,
            commission=commission,
            slippage_cost=abs(fill_price - base_price) * quantity,
        )

    def _apply_slippage(self, price: Decimal, side: str) -> Decimal:
        """应用滑点

        买入价 = price + slippage
        卖出价 = price - slippage

        Args:
            price: 基础价格
            side: 买卖方向

        Returns:
            含滑点的价格
        """
        slippage = price * self._config.slippage_bps / Decimal("10000")
        if side == "BUY":
            return price + slippage
        elif side == "SELL":
            return price - slippage
        else:
            raise MatchingError(f"无效side: {side}")

    def _calc_commission(self, quantity: Decimal, price: Decimal, side: str) -> Decimal:
        """计算手续费(券商佣金+印花税)

        券商佣金: max(quantity * price * commission_rate, min_commission)
        印花税: 卖出时 quantity * price * stamp_tax_rate

        Args:
            quantity: 成交数量
            price: 成交价格
            side: 买卖方向

        Returns:
            总手续费
        """
        gross = quantity * price

        # 券商佣金(最低5元)
        commission = gross * self._config.commission_rate
        if commission < self._config.min_commission:
            commission = self._config.min_commission

        # 印花税(卖出)
        if side == "SELL":
            commission += gross * self._config.stamp_tax_rate

        return commission

    def _is_price_limit(
        self, symbol: str, price: Decimal, prev_close: Optional[Decimal]
    ) -> bool:
        """检查是否涨跌停

        A股涨跌停板: ±10%(ST股±5%)
        MVP简化:统一用10%,不区分ST股

        Args:
            symbol: 标的代码
            price: 当前价格
            prev_close: 前一日收盘价

        Returns:
            True=涨跌停(不成交), False=正常
        """
        if prev_close is None or prev_close <= 0:
            return False

        change_pct = abs(price - prev_close) / prev_close
        # 涨跌停板价格四舍五入到分
        upper_limit = (prev_close * (1 + self._config.price_limit_pct)).quantize(Decimal("0.01"))
        lower_limit = (prev_close * (1 - self._config.price_limit_pct)).quantize(Decimal("0.01"))

        return price >= upper_limit or price <= lower_limit

    @property
    def config(self) -> MatchingConfig:
        """撮合配置"""
        return self._config


__all__ = ["MatchingEngine", "MatchingConfig", "MatchingError"]
