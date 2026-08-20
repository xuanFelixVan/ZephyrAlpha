# [BLUEPRINT] MOD-RPT-027 | docs/03_modules/_domain_reporting/ashare_trade_record_template/blueprint.md
# [MODULE] zephyr.reporting.ashare_trade_record_template
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.reporting
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 11必填字段强制校验; amount=quantity×price一致性; stamp_duty仅SELL>0; quantity为100整数倍; TradeRecordEntry frozen不可变
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidTradeRecordError(ZA-RPT-0005)
# [TESTS] tests/reporting/test_ashare_trade_record_template.py
# [A_module] module_id=MOD-RPT-027 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
r"""

D_REPORTING — A股交易记录模板引擎 (ASHare Trade Record Template)

为 A 股交易记录提供标准化模板: 11 必填字段 + 强制校验 + 模板版本管理。
满足证监会交易记录留存要求, 属 A 类基础设施。

设计真源: D:/临时工作区/依赖图/10-D-REPORTING-报告域.md §1.3 D-REPORTING-27
蓝图: docs/03_modules/_domain_reporting/ashare_trade_record_template/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 交易记录字典 entry
#   fields: 11必填字段 trade_date/symbol/side/quantity/price/amount/commission/stamp_duty/transfer_fee/strategy_id/account_id
#   code: validate() 参数 entry（dict）
# 层: 算法
# - id: A1
#   name_zh: ① 格式校验（日期/代码/方向）
#   name_en: AShareTradeRecordTemplate.validate 格式段
#   intro: 校验交易日期是 YYYY-MM-DD、证券代码是 6 位数字、买卖方向是 BUY/SELL
#   desc: _DATE_RE=^\d{4}-\d{2}-\d{2}$；_SYMBOL_RE=^\d{6}$；side.upper()∈(BUY,SELL)；缺字段或格式错抛 ZA-RPT-0005
#   inputs: I1
#   outputs: 格式合法的 trade_date/symbol/side
# - id: A2
#   name_zh: ② 数值与业务规则校验
#   name_en: AShareTradeRecordTemplate.validate 数值段
#   intro: 校验数量为 100 整数倍、金额等于数量乘价格、印花税仅卖出可非零等 A 股规则
#   desc: quantity>0 且 quantity%100==0；price>0；amount==quantity×price；commission/transfer_fee≥0；stamp_duty≥0 且 BUY 时必须=0；strategy_id/account_id 非空
#   inputs: A1
#   outputs: 校验通过的 11 字段数值
#   invariant: amount=quantity×price一致性；stamp_duty仅SELL>0；quantity为100整数倍
# - id: A3
#   name_zh: ③ 不可变记录生成
#   name_en: TradeRecordEntry 构建
#   intro: 把校验通过的字段装进 frozen 不可变记录并带模板版本号
#   desc: TradeRecordEntry(schema_version="1.0")，strategy_id/account_id 去首尾空格
#   inputs: A2
#   outputs: TradeRecordEntry
#   invariant: TradeRecordEntry frozen不可变
# 层: 输出
# - id: O1
#   name_zh: A股交易记录（模板校验通过）
#   name_en: TradeRecordEntry
#   intro: 满足证监会交易记录留存要求的 11 必填字段标准化不可变记录
#   invariant: 11必填字段强制校验
#   downstream: zephyr.reporting（报告域内部消费）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

_TEMPLATE_VERSION = "1.0"

# 11 必填字段定义: (字段名, 类型描述, 校验函数)
_REQUIRED_FIELDS: tuple[str, ...] = (
    "trade_date",
    "symbol",
    "side",
    "quantity",
    "price",
    "amount",
    "commission",
    "stamp_duty",
    "transfer_fee",
    "strategy_id",
    "account_id",
)

# 正则: YYYY-MM-DD
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# 正则: 6位数字证券代码
_SYMBOL_RE = re.compile(r"^\d{6}$")

_VALID_SIDES = ("BUY", "SELL")

# A股最小交易单位
_LOT_SIZE = Decimal("100")
# 价格精度: 0.01
_PRICE_PRECISION = Decimal("0.01")


class InvalidTradeRecordError(ZephyrBaseError):
    """交易记录输入非法——缺字段/类型错/值非法/一致性失败。"""

    error_code = "ZA-RPT-0005"


# ── 数据模型（frozen 不可变）──


@dataclass(frozen=True)
class TradeRecordEntry:
    """A股交易记录——11 必填字段的不可变校验通过记录。"""

    trade_date: str
    symbol: str
    side: str
    quantity: Decimal
    price: Decimal
    amount: Decimal
    commission: Decimal
    stamp_duty: Decimal
    transfer_fee: Decimal
    strategy_id: str
    account_id: str
    schema_version: str = _TEMPLATE_VERSION


# ── 校验工具 ──


def _to_decimal(value: object, field_name: str) -> Decimal:
    """将值转为 Decimal, 失败抛异常。"""
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    if isinstance(value, str):
        try:
            return Decimal(value)
        except InvalidOperation as exc:
            raise InvalidTradeRecordError(
                f"字段 {field_name} 无法转为 Decimal: {value!r}",
                details={"field": field_name, "value": str(value)},
            ) from exc
    raise InvalidTradeRecordError(
        f"字段 {field_name} 类型非法: 期望数值, 实际={type(value).__name__}",
        details={"field": field_name, "actual_type": type(value).__name__},
    )


def _require_field(entry: dict, field: str) -> object:
    """提取必填字段, 缺失抛异常。"""
    if field not in entry:
        raise InvalidTradeRecordError(
            f"缺少必填字段: {field}",
            details={"missing_field": field},
        )
    return entry[field]


# ── 模板引擎主类 ──


class AShareTradeRecordTemplate:
    """A股交易记录模板引擎——11必填字段模板+强制校验+版本管理。

    纯基础设施, 无外部状态。线程安全（无共享可变状态）。

    Usage:
        tpl = AShareTradeRecordTemplate()
        entry = tpl.validate({
            "trade_date": "2026-08-02",
            "symbol": "600000",
            "side": "BUY",
            "quantity": "100",
            "price": "10.00",
            "amount": "1000.00",
            "commission": "5.00",
            "stamp_duty": "0",
            "transfer_fee": "0.10",
            "strategy_id": "S001",
            "account_id": "A001",
        })
    """

    def get_required_fields(self) -> list[str]:
        """返回 11 必填字段名列表。"""
        return list(_REQUIRED_FIELDS)

    def get_template_version(self) -> str:
        """返回模板版本号。"""
        return _TEMPLATE_VERSION

    def validate(self, entry: dict) -> TradeRecordEntry:
        """校验交易记录字典, 返回不可变 TradeRecordEntry。

        Args:
            entry: 含 11 必填字段的字典。

        Returns:
            TradeRecordEntry: 校验通过的不可变记录。

        Raises:
            InvalidTradeRecordError: 缺字段/类型错/值非法/一致性失败。
        """
        if not isinstance(entry, dict):
            raise InvalidTradeRecordError(
                f"entry 必须为 dict, 实际类型={type(entry).__name__}",
                details={"actual_type": type(entry).__name__},
            )

        # ── 提取并校验各字段 ──

        # 1. trade_date: YYYY-MM-DD
        trade_date = _require_field(entry, "trade_date")
        if not isinstance(trade_date, str) or not _DATE_RE.match(trade_date):
            raise InvalidTradeRecordError(
                f"trade_date 格式非法(期望 YYYY-MM-DD): {trade_date!r}",
                details={"field": "trade_date", "value": str(trade_date)},
            )

        # 2. symbol: 6位数字
        symbol = _require_field(entry, "symbol")
        if not isinstance(symbol, str) or not _SYMBOL_RE.match(symbol):
            raise InvalidTradeRecordError(
                f"symbol 格式非法(期望6位数字): {symbol!r}",
                details={"field": "symbol", "value": str(symbol)},
            )

        # 3. side: BUY / SELL
        side = _require_field(entry, "side")
        if not isinstance(side, str) or side.upper() not in _VALID_SIDES:
            raise InvalidTradeRecordError(
                f"side 非法(期望 BUY/SELL): {side!r}",
                details={"field": "side", "value": str(side)},
            )
        side = side.upper()

        # 4. quantity: >0, 100整数倍
        quantity = _to_decimal(_require_field(entry, "quantity"), "quantity")
        if quantity <= 0:
            raise InvalidTradeRecordError(
                f"quantity 必须为正: {quantity}",
                details={"field": "quantity", "value": str(quantity)},
            )
        if quantity % _LOT_SIZE != 0:
            raise InvalidTradeRecordError(
                f"quantity 必须为 {_LOT_SIZE} 的整数倍: {quantity}",
                details={"field": "quantity", "value": str(quantity)},
            )

        # 5. price: >0
        price = _to_decimal(_require_field(entry, "price"), "price")
        if price <= 0:
            raise InvalidTradeRecordError(
                f"price 必须为正: {price}",
                details={"field": "price", "value": str(price)},
            )

        # 6. amount: = quantity × price (一致性校验)
        amount = _to_decimal(_require_field(entry, "amount"), "amount")
        expected_amount = quantity * price
        if amount != expected_amount:
            raise InvalidTradeRecordError(
                f"amount 不一致: 期望={expected_amount} 实际={amount} (quantity={quantity} × price={price})",
                details={
                    "field": "amount",
                    "expected": str(expected_amount),
                    "actual": str(amount),
                },
            )

        # 7. commission: ≥0
        commission = _to_decimal(_require_field(entry, "commission"), "commission")
        if commission < 0:
            raise InvalidTradeRecordError(
                f"commission 不能为负: {commission}",
                details={"field": "commission", "value": str(commission)},
            )

        # 8. stamp_duty: ≥0, SELL时允许>0, BUY时必须=0
        stamp_duty = _to_decimal(_require_field(entry, "stamp_duty"), "stamp_duty")
        if stamp_duty < 0:
            raise InvalidTradeRecordError(
                f"stamp_duty 不能为负: {stamp_duty}",
                details={"field": "stamp_duty", "value": str(stamp_duty)},
            )
        if side == "BUY" and stamp_duty > 0:
            raise InvalidTradeRecordError(
                f"stamp_duty 买入时必须为0: {stamp_duty}",
                details={"field": "stamp_duty", "value": str(stamp_duty), "side": side},
            )

        # 9. transfer_fee: ≥0
        transfer_fee = _to_decimal(_require_field(entry, "transfer_fee"), "transfer_fee")
        if transfer_fee < 0:
            raise InvalidTradeRecordError(
                f"transfer_fee 不能为负: {transfer_fee}",
                details={"field": "transfer_fee", "value": str(transfer_fee)},
            )

        # 10. strategy_id: 非空
        strategy_id = _require_field(entry, "strategy_id")
        if not isinstance(strategy_id, str) or not strategy_id.strip():
            raise InvalidTradeRecordError(
                "strategy_id 不能为空",
                details={"field": "strategy_id"},
            )

        # 11. account_id: 非空
        account_id = _require_field(entry, "account_id")
        if not isinstance(account_id, str) or not account_id.strip():
            raise InvalidTradeRecordError(
                "account_id 不能为空",
                details={"field": "account_id"},
            )

        record = TradeRecordEntry(
            trade_date=trade_date,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            amount=amount,
            commission=commission,
            stamp_duty=stamp_duty,
            transfer_fee=transfer_fee,
            strategy_id=strategy_id.strip(),
            account_id=account_id.strip(),
            schema_version=_TEMPLATE_VERSION,
        )

        _logger.debug(
            "validate: date=%s symbol=%s side=%s qty=%s price=%s amount=%s",
            record.trade_date,
            record.symbol,
            record.side,
            record.quantity,
            record.price,
            record.amount,
        )
        return record


__all__ = [
    "AShareTradeRecordTemplate",
    "InvalidTradeRecordError",
    "TradeRecordEntry",
]
