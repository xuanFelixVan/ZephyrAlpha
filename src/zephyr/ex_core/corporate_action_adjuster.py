# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.corporate_action_adjuster
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib
# [CONSUMERS] ex_core.trading_session ; ex_core.adapters.miniqmt_broker ; ex_core.price_cage
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 除权除息日调整前收盘价→重算涨跌停→价格笼子基准价;送股转增同步持仓股数;现金红利T+1到账
# [MODIFY-GUARD] 40_execution_broker.md §决策⑯
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CorporateActionAdjusterError
# [TESTS] tests/ex_core/test_corporate_action_adjuster.py
# [TTL] permanent

"""

除权除息日处理（40_execution_broker §决策⑯ gap 15 施工）。

A 股常规公司行动（每年年报季密集发生）。缺失后果：除权除息日系统仍用昨日收盘价
算涨跌停价和价格笼子基准价，会与交易所调整后的新基准价不符→挂单价超笼子直接废单；
持仓股数未同步送股→持仓对账失败、T+1 可卖数量错位。

除权除息参考价公式（沪深北交易所《交易规则》§4.3）：
  | 情形                    | 公式                                                    |
  |-------------------------|---------------------------------------------------------|
  | 仅现金分红（除息）       | 除息参考价 = 登记日收盘价 − 每股现金红利                |
  | 仅送股/转增（除权）      | 除权参考价 = 登记日收盘价 ÷ (1 + 每股送转比例)         |
  | 现金分红 + 送转（除权除息）| 除权除息参考价 = (登记日收盘价 − 现金红利) ÷ (1+送转比例)|

影响传导：
  - 前收盘价 → 调整为除权除息参考价（价格笼子基准价回退值）
  - 涨跌停价 → 新前收盘价 ×（1±涨跌幅）
  - 持仓股数 → 送股/转增增加股数
  - 持仓成本 → 除权除息后摊薄
  - 资金 → 现金红利 T+1 到账

与现有决策协同：
  - 决策①涨跌停校验：_check_price_limit 必须用除权除息后的新前收盘价
  - 决策⑭价格笼子：笼子基准价回退链用调整后的前收盘价
  - 决策⑨ T+1：送股增加股数何时可卖（通常 T+1），需查 can_sell_volume
  - 决策⑮临时停牌：除权除息日可能伴随停牌（如除权除息同时停牌一小时）

数据源：xtdata.get_instrument_detail(symbol) 的 ex_dividend_date 字段，
或 Tushare/AkShare 除权除息接口。MVP 建议盘前批量拉取当日除权除息列表。

依据：40_execution_broker.md v2.4.0 §决策⑯
Version: 1.0.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 公司行动信息 CorporateAction（盘前批量拉取除权除息列表）
#   fields: symbol + ex_date + record_date + 每股现金红利 + 送转比例 + 登记日收盘价
#   code: CorporateAction L85-103
# - id: I2
#   name: 原始前收盘价 original_prev_close
#   fields: 昨日收盘价（Decimal）+ 涨跌幅限制 price_limit_pct（默认10%）
#   code: get_adjusted_prev_close L253-257
# - id: I3
#   name: 当前持仓 current_qty + current_avg_cost
#   fields: 持仓股数 + 持仓均价（Decimal）
#   code: adjust_position L300-304
# 层: 算法
# - id: A1
#   name_zh: ① 除权除息参考价计算
#   name_en: compute_ex_dividend_price / ex_dividend_price
#   intro: 按交易所公式算除权除息后的新基准价，量化到 0.01 元
#   desc: 仅分红: record_close−红利；仅送转: record_close÷(1+送转比)；分红+送转: (record_close−红利)÷(1+送转比)（L126-140）；quantize(0.01, ROUND_HALF_UP)（L176-178）；record_close≤0 抛 CorporateActionAdjusterError
#   inputs: I1
#   outputs: 除权除息参考价（新前收盘价）
#   invariant: 除权除息日调整前收盘价
# - id: A2
#   name_zh: ② 调整后涨跌停价重算
#   name_en: get_adjusted_limit_prices
#   intro: 用新前收盘价 ×（1±涨跌幅）重算涨跌停价，避免挂单价超笼子废单
#   desc: limit_up=new_prev×(1+pct)、limit_down=new_prev×(1−pct)，均 quantize(0.01)（L291-298）
#   inputs: A1 I2
#   outputs: (涨停价, 跌停价)
# - id: A3
#   name_zh: ③ 持仓调整（送股+摊薄+红利）
#   name_en: adjust_position
#   intro: 送转增加股数、总成本减红利后按新股数摊薄均价、现金红利 T+1 到账
#   desc: new_qty=qty×(1+送转比) 量化整数股（L323-325）；new_avg_cost=(qty×cost−qty×红利)/new_qty 量化 0.0001（L331-338）；cash_dividend_received=qty×每股红利（L332）
#   inputs: A1 I3
#   outputs: AdjustmentResult（新股数/新成本/红利/新前收盘价）
#   invariant: 送股转增同步持仓股数；现金红利T+1到账
# 层: 输出
# - id: O1
#   name_zh: 调整后前收盘价与涨跌停价
#   name_en: adjusted prev_close + limit prices
#   intro: 除权除息日替代昨收价的新基准，供涨跌停校验与价格笼子回退链使用
#   downstream: ex_core.trading_session ; ex_core.price_cage ; ex_core.adapters.miniqmt_broker
# - id: O2
#   name_zh: 持仓调整结果 AdjustmentResult
#   name_en: AdjustmentResult
#   intro: 送股后新股数/摊薄成本/现金红利的不可变审计记录
#   downstream: ex_core.trading_session
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# I2 --> A2
# A1 --> A3
# I3 --> A3
# A2 --> O1
# A1 --> O1
# A3 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from enum import Enum
from typing import Final

__all__: Final = [
    "CorporateActionType",
    "CorporateAction",
    "AdjustmentResult",
    "CorporateActionAdjusterError",
    "CorporateActionAdjuster",
    "compute_ex_dividend_price",
]

_logger = logging.getLogger(__name__)


class CorporateActionAdjusterError(Exception):
    """除权除息处理错误。"""

    error_code = "ZA-XC-0015"


class CorporateActionType(str, Enum):
    """公司行动类型。"""

    CASH_DIVIDEND = "cash_dividend"        # 仅现金分红（除息）
    STOCK_DIVIDEND = "stock_dividend"      # 仅送股/转增（除权）
    CASH_AND_STOCK = "cash_and_stock"      # 现金分红 + 送转（除权除息）
    NONE = "none"                          # 无公司行动


@dataclass(frozen=True)
class CorporateAction:
    """单只股票的公司行动信息（不可变）。

    Attributes:
        symbol: 股票代码
        ex_date: 除权除息日
        record_date: 股权登记日
        cash_dividend_per_share: 每股现金红利（元，0=无现金分红）
        stock_dividend_ratio: 每股送转比例（如 0.1 = 10送1，0=无送转）
        record_close: 登记日收盘价（用于计算除权除息参考价）
    """

    symbol: str
    ex_date: date
    record_date: date
    cash_dividend_per_share: Decimal = Decimal("0")
    stock_dividend_ratio: Decimal = Decimal("0")
    record_close: Decimal = Decimal("0")

    @property
    def action_type(self) -> CorporateActionType:
        """判断公司行动类型。"""
        has_cash = self.cash_dividend_per_share > 0
        has_stock = self.stock_dividend_ratio > 0
        if has_cash and has_stock:
            return CorporateActionType.CASH_AND_STOCK
        if has_cash:
            return CorporateActionType.CASH_DIVIDEND
        if has_stock:
            return CorporateActionType.STOCK_DIVIDEND
        return CorporateActionType.NONE

    @property
    def ex_dividend_price(self) -> Decimal:
        """除权除息参考价（按公式计算）。

        - 仅现金分红：登记日收盘价 − 每股现金红利
        - 仅送股/转增：登记日收盘价 ÷ (1 + 每股送转比例)
        - 现金分红 + 送转：(登记日收盘价 − 现金红利) ÷ (1 + 送转比例)
        """
        if self.record_close <= 0:
            raise CorporateActionAdjusterError(
                f"登记日收盘价无效 symbol={self.symbol} record_close={self.record_close}"
            )
        atype = self.action_type
        if atype is CorporateActionType.CASH_DIVIDEND:
            return self.record_close - self.cash_dividend_per_share
        if atype is CorporateActionType.STOCK_DIVIDEND:
            return self.record_close / (Decimal("1") + self.stock_dividend_ratio)
        if atype is CorporateActionType.CASH_AND_STOCK:
            return (
                (self.record_close - self.cash_dividend_per_share)
                / (Decimal("1") + self.stock_dividend_ratio)
            )
        return self.record_close  # NONE


@dataclass(frozen=True)
class AdjustmentResult:
    """持仓/基准价调整结果（不可变，用于审计）。

    Attributes:
        symbol: 股票代码
        action: 公司行动信息
        new_prev_close: 调整后的前收盘价（= 除权除息参考价）
        new_position_qty: 调整后的持仓股数（送股增加）
        new_avg_cost: 调整后的持仓成本（摊薄）
        cash_dividend_received: 现金红利总额（T+1 到账）
    """

    symbol: str
    action: CorporateAction
    new_prev_close: Decimal
    new_position_qty: Decimal
    new_avg_cost: Decimal
    cash_dividend_received: Decimal


def compute_ex_dividend_price(action: CorporateAction) -> Decimal:
    """计算除权除息参考价（函数式入口）。

    Args:
        action: 公司行动信息

    Returns:
        除权除息参考价（量化到 0.01）

    Raises:
        CorporateActionAdjusterError: 登记日收盘价无效
    """
    raw = action.ex_dividend_price
    # 量化到 0.01（A 股最小价格变动单位）
    return raw.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass
class CorporateActionAdjuster:
    """除权除息日处理器。

    盘前批量拉取当日除权除息列表，调整前收盘价/涨跌停价/持仓股数/持仓成本，
    确保系统基准与交易所一致。

    用法:
        adjuster = CorporateActionAdjuster()

        # 1. 盘前拉取除权除息列表
        adjuster.register_action(CorporateAction(
            symbol="600000.SH",
            ex_date=date(2026, 8, 10),
            record_date=date(2026, 8, 7),
            cash_dividend_per_share=Decimal("0.50"),
            stock_dividend_ratio=Decimal("0.1"),  # 10送1
            record_close=Decimal("10.00"),
        ))

        # 2. 获取调整后的前收盘价（替代昨日收盘价）
        new_prev = adjuster.get_adjusted_prev_close("600000.SH", Decimal("10.00"))

        # 3. 调整持仓（送股增加股数 + 成本摊薄 + 现金红利）
        result = adjuster.adjust_position(
            symbol="600000.SH",
            current_qty=Decimal("1000"),
            current_avg_cost=Decimal("10.00"),
        )
        # result.new_position_qty = 1100（1000 + 100送股）
        # result.new_avg_cost = 9.09（摊薄）
        # result.cash_dividend_received = 500（1000股 × 0.5元）

    设计要点:
      - **状态驱动**：维护 symbol -> CorporateAction 映射，盘前批量注册
      - **幂等**：同一 symbol 重复注册覆盖（最新为准）
      - **审计友好**：AdjustmentResult 记录每项调整前后值
      - **与价格笼子解耦**：只算新前收盘价，笼子校验由调用方另行调用
    """

    # symbol -> CorporateAction
    _action_map: dict[str, CorporateAction] = field(default_factory=dict)

    # ── 注册 ──

    def register_action(self, action: CorporateAction) -> None:
        """注册单只股票的除权除息信息（盘前批量拉取后调用）。"""
        if action.action_type is CorporateActionType.NONE:
            _logger.debug("无公司行动，跳过注册: %s", action.symbol)
            return
        self._action_map[action.symbol] = action
        _logger.info(
            "注册除权除息: %s type=%s ex_date=%s cash=%s stock_ratio=%s",
            action.symbol, action.action_type.value, action.ex_date,
            action.cash_dividend_per_share, action.stock_dividend_ratio,
        )

    def batch_register(self, actions: list[CorporateAction]) -> None:
        """批量注册除权除息信息。"""
        for action in actions:
            self.register_action(action)

    def has_action(self, symbol: str) -> bool:
        """是否登记了除权除息。"""
        return symbol in self._action_map

    def get_action(self, symbol: str) -> CorporateAction | None:
        """获取除权除息信息。"""
        return self._action_map.get(symbol)

    # ── 调整接口 ──

    def get_adjusted_prev_close(
        self,
        symbol: str,
        original_prev_close: Decimal,
    ) -> Decimal:
        """获取调整后的前收盘价。

        若该 symbol 当日有除权除息，返回除权除息参考价；
        否则返回原始前收盘价。

        Args:
            symbol: 股票代码
            original_prev_close: 原始前收盘价（昨日收盘价）

        Returns:
            调整后的前收盘价
        """
        action = self._action_map.get(symbol)
        if action is None:
            return original_prev_close
        return compute_ex_dividend_price(action)

    def get_adjusted_limit_prices(
        self,
        symbol: str,
        original_prev_close: Decimal,
        price_limit_pct: Decimal = Decimal("0.10"),
    ) -> tuple[Decimal, Decimal]:
        """获取调整后的涨跌停价。

        Args:
            symbol: 股票代码
            original_prev_close: 原始前收盘价
            price_limit_pct: 涨跌幅限制（默认 10%；2026-07-06 规则：主板/ST ±10%，
                创业板/科创板 ±20%，北交所 ±30%，板块分类真源=board_lot.classify_board）

        Returns:
            (涨停价, 跌停价) — 基于调整后的前收盘价计算
        """
        new_prev = self.get_adjusted_prev_close(symbol, original_prev_close)
        limit_up = (new_prev * (Decimal("1") + price_limit_pct)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP,
        )
        limit_down = (new_prev * (Decimal("1") - price_limit_pct)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP,
        )
        return limit_up, limit_down

    def adjust_position(
        self,
        symbol: str,
        current_qty: Decimal,
        current_avg_cost: Decimal,
    ) -> AdjustmentResult | None:
        """调整持仓（送股增加股数 + 成本摊薄 + 现金红利）。

        Args:
            symbol: 股票代码
            current_qty: 当前持仓股数
            current_avg_cost: 当前持仓均价

        Returns:
            AdjustmentResult 调整结果；无除权除息返回 None
        """
        action = self._action_map.get(symbol)
        if action is None:
            return None

        new_prev_close = compute_ex_dividend_price(action)

        # 送股增加股数：new_qty = old_qty × (1 + 送转比例)
        new_qty = current_qty * (Decimal("1") + action.stock_dividend_ratio)
        # 量化到整数股
        new_qty = new_qty.quantize(Decimal("1"), rounding=ROUND_HALF_UP)

        # 成本摊薄：持仓总成本不变，股数增加 → 均价下降
        # 总成本 = old_qty × old_avg_cost
        # 现金红利减少总成本（分红部分视为成本回收）
        # new_avg_cost = (old_qty × old_avg_cost − 现金红利总额) / new_qty
        total_cost = current_qty * current_avg_cost
        cash_dividend_total = current_qty * action.cash_dividend_per_share
        if new_qty > 0:
            new_avg_cost = (
                (total_cost - cash_dividend_total) / new_qty
            ).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        else:
            new_avg_cost = Decimal("0")

        _logger.info(
            "持仓调整: %s qty %s→%s cost %s→%s cash_dividend=%s new_prev=%s",
            symbol, current_qty, new_qty, current_avg_cost, new_avg_cost,
            cash_dividend_total, new_prev_close,
        )

        return AdjustmentResult(
            symbol=symbol,
            action=action,
            new_prev_close=new_prev_close,
            new_position_qty=new_qty,
            new_avg_cost=new_avg_cost,
            cash_dividend_received=cash_dividend_total,
        )

    def symbols_with_actions(self) -> list[str]:
        """所有登记了除权除息的 symbol 列表。"""
        return list(self._action_map.keys())
