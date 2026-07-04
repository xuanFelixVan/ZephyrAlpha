# [BLUEPRINT] SRC-198 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.trading.trading_contracts.portfolio.contracts.money
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.trading_contracts.market.instrument
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-PRT_money | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
from __future__ import annotations
from typing import Self

"""
ZephyrAlpha — shared/contracts/money.py

金额 + 货币 + 精度契约（Money + Currency + Precision Contract）。

🔒 **锁定文件（Immutable Core）**：任何修改必须先建 KB 决策记录并经人工批准。

═══════════════════════════════════════════════════════════════════════
【设计目标】
═══════════════════════════════════════════════════════════════════════
1. **禁止 float 参与金融计算**（浮点舍入误差累计 10 万笔单后 PnL 会漂）
2. **所有金额强制 Decimal + Currency**（金额自带币种，跨币种运算必报错）
3. **精度自动跟随货币**（JPY=0 位，USD=2 位，BTC=8 位），防止 1.005 → 1.01 错误舍入
4. **常用运算内置**（加减乘除、比较、正负），使用体验接近 float

**与 OQ-071 的关系**：
  本文件只包含 **Money 值对象**（够满足首批 3 铁板契约落地）。
  完整的 **Currency 类 + FXRate 汇率提供器**延后到 `currency.py`（OQ-071 P0 待锁清单）。
  本文件先内嵌 `_CURRENCY_PRECISION` 常量表满足精度查询需求。

参见：
  - OQ-071 P0 待锁 currency.py（Currency + FXRateProvider 完整版）
  - Python decimal 官方文档：https://docs.python.org/3/library/decimal.html
═══════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal, getcontext

from zephyr.trading.trading_contracts.market.instrument import CurrencyCode

# 全局 Decimal 精度（28 位有效数字，足够金融计算，含复利/开方等）
getcontext().prec = 28
getcontext().rounding = ROUND_HALF_EVEN  # 银行家舍入（金融业界标准）

# ═══════════════════════════════════════════════════════════════════
# 货币精度表
# ═══════════════════════════════════════════════════════════════════

_CURRENCY_PRECISION: dict[str, int] = {
    # 法币（ISO 4217）
    "CNY": 2,
    "HKD": 2,
    "USD": 2,
    "SGD": 2,
    "TWD": 2,
    "INR": 2,
    "GBP": 2,
    "EUR": 2,
    "CHF": 2,
    "CAD": 2,
    "AUD": 2,
    "NZD": 2,
    "JPY": 0,  # 日元无小数位
    "KRW": 0,  # 韩元无小数位
    # 加密货币
    "BTC": 8,
    "ETH": 8,
    "USDT": 6,
    "USDC": 6,
}
"""
货币精度表（小数位数）。

⚠️ 本表是**最小精度**（即展示/存储/结算用）。
   中间计算仍用 28 位 Decimal 精度，最后展示/入账时 quantize 到指定位数。

扩展方式：新增货币时在此表添加，同时更新 instrument.CurrencyCode Literal。
"""


def get_currency_precision(currency: str) -> int:
    """
    查询货币精度（小数位数）。

    未知货币默认返回 2 位（法币通用精度）并记告警。
    """
    if currency not in _CURRENCY_PRECISION:
        import warnings

        warnings.warn(
            f"货币 {currency!r} 未在精度表中注册，默认使用 2 位小数。"
            " 请在 shared/contracts/money.py 的 _CURRENCY_PRECISION 表中添加。",
            stacklevel=2,
        )
        return 2
    return _CURRENCY_PRECISION[currency]


# ═══════════════════════════════════════════════════════════════════
# 异常类
# ═══════════════════════════════════════════════════════════════════


class MoneyPrecisionError(ValueError):
    """金额精度错误（如试图用 float 构造 Money）。"""


class MoneyCurrencyMismatchError(ValueError):
    """币种不匹配错误（如 CNY Money 与 USD Money 直接相加）。"""


# ═══════════════════════════════════════════════════════════════════
# Money 值对象
# ═══════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class Money:
    """
    金额值对象（Value Object）。

    **核心约束**：
      - `amount` 必须是 Decimal（禁止 float 进入）
      - `currency` 必须是 ISO 4217 代码或主流加密货币代码
      - 所有运算**自动按货币精度舍入**（银行家舍入）
      - 跨币种运算**必须先换汇**（本阶段不内嵌换汇，留给 FXRateProvider）

    **构造方式**：
      ```python
      # ✅ 推荐：从字符串构造（零舍入误差）
      price = Money("1234.56", "CNY")

      # ✅ 允许：从 Decimal 构造
      price = Money(Decimal("1234.56"), "CNY")

      # ✅ 允许：从 int 构造
      qty_value = Money(100, "CNY")

      # ❌ 禁止：从 float 构造（抛 MoneyPrecisionError）
      price = Money(1234.56, "CNY")  # 报错！
      ```

    **运算示例**：
      ```python
      a = Money("100.50", "CNY")
      b = Money("50.25", "CNY")
      a + b                    # Money("150.75", "CNY")
      a - b                    # Money("50.25", "CNY")
      a * 2                    # Money("201.00", "CNY")
      a * Decimal("1.5")       # Money("150.75", "CNY")
      a / 2                    # Money("50.25", "CNY")
      a > b                    # True

      # ❌ 跨币种直接运算报错
      usd = Money("10", "USD")
      a + usd                  # MoneyCurrencyMismatchError!
      ```

    **为什么不内嵌换汇？**
      - 汇率是时变的、有来源的、需要回溯的（"2026-04-18 00:00:00 的 USDCNY 汇率"）
      - 汇率提供器是独立服务（FXRateProvider），由 D_DATA 数据源或 基础设施提供
      - Money 值对象只负责"带币种的金额"，不负责汇率查询
      - 换汇统一走：`converted = fx_provider.convert(money, target_ccy, as_of_date)`
    """

    amount: Decimal
    currency: CurrencyCode

    def __post_init__(self) -> None:
        # 禁止 float 进入
        if isinstance(self.amount, float):
            raise MoneyPrecisionError(
                f'Money.amount 禁止使用 float（{self.amount}）， 请用 str 或 Decimal 构造：Money("1234.56", "CNY")'
            )

        # int / str / Decimal → Decimal（frozen=True 下用 object.__setattr__ 绕过）
        if not isinstance(self.amount, Decimal):
            try:
                object.__setattr__(self, "amount", Decimal(str(self.amount)))
            except Exception as exc:
                raise MoneyPrecisionError(f"Money.amount 无法转换为 Decimal: {self.amount!r}（{exc}）") from exc

        # 按货币精度 quantize（银行家舍入）
        precision = get_currency_precision(self.currency)
        quantized = self.amount.quantize(
            Decimal(10) ** -precision,
            rounding=ROUND_HALF_EVEN,
        )
        object.__setattr__(self, "amount", quantized)

    # --- 运算符重载 ---

    def _check_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise MoneyCurrencyMismatchError(
                f"币种不匹配：{self.currency} vs {other.currency}。 请先用 FXRateProvider 换算到相同货币后再运算。"
            )

    def __add__(self, other: Money) -> Self:
        self._check_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Money) -> Self:
        self._check_same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, multiplier: int | Decimal) -> Self:
        if isinstance(multiplier, float):
            raise MoneyPrecisionError(f"Money 乘法禁止使用 float（{multiplier}），请用 int 或 Decimal。")
        if not isinstance(multiplier, Decimal):
            multiplier = Decimal(str(multiplier))
        return Money(self.amount * multiplier, self.currency)

    __rmul__ = __mul__

    def __truediv__(self, divisor: int | Decimal) -> Self:
        if isinstance(divisor, float):
            raise MoneyPrecisionError(f"Money 除法禁止使用 float（{divisor}），请用 int 或 Decimal。")
        if not isinstance(divisor, Decimal):
            divisor = Decimal(str(divisor))
        if divisor == 0:
            raise ZeroDivisionError("Money 除以零")
        return Money(self.amount / divisor, self.currency)

    def __neg__(self) -> Self:
        return Money(-self.amount, self.currency)

    def __abs__(self) -> Self:
        return Money(abs(self.amount), self.currency)

    # --- 比较 ---

    def __lt__(self, other: Money) -> bool:
        self._check_same_currency(other)
        return self.amount < other.amount

    def __le__(self, other: Money) -> bool:
        self._check_same_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: Money) -> bool:
        self._check_same_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: Money) -> bool:
        self._check_same_currency(other)
        return self.amount >= other.amount

    # --- 展示 ---

    def __repr__(self) -> str:
        return f"Money({self.amount!r}, {self.currency!r})"

    def __str__(self) -> str:
        """人类可读格式，如 "1,234.56 CNY"（千分位分隔）。"""
        precision = get_currency_precision(self.currency)
        formatted = f"{self.amount:,.{precision}f}"
        return f"{formatted} {self.currency}"

    # --- 布尔 ---

    def __bool__(self) -> bool:
        """True 当且仅当 amount != 0。"""
        return self.amount != 0

    # --- 工具方法 ---

    def is_zero(self) -> bool:
        return self.amount == 0

    def is_positive(self) -> bool:
        return self.amount > 0

    def is_negative(self) -> bool:
        return self.amount < 0
