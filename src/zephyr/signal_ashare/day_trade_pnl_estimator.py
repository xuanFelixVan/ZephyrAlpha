# [BLUEPRINT] MOD-SIG-132 | docs/03_modules/_domain_signal/day_trade_pnl_estimator/blueprint.md
# [MODULE] zephyr.signal_ashare.day_trade_pnl_estimator
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（协议核心纯内存；费率/时钟全注入）
# [CONSUMERS] 运行时装配批（统一注入点装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 做T净盈亏=价差-双边佣金-印花税-冲击成本（四要素费率注入，印花税仅卖出侧，佣金含单笔最低）；置信度=历史相似价差实现率滚动统计（相似度容差注入）；成交回写按预估vs实现偏差滚动校正冲击系数（倍率钳制）；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal/day_trade_pnl_estimator/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DayTradePnlError(占位 ZA-SIG-UNREGISTERED-DAY-TRADE-PNL)——费率模型缺失/费率越界/价格非正/股数非正整数/实现盈亏非有限值/非法配置时抛
# [TESTS] tests/signal_ashare/test_day_trade_pnl_estimator.py
# [A_module] module_id=MOD-SIG-132 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
DayTradePnlEstimator — 做T盈亏预估器（MOD-SIG-132）。

B11-02600（AUD-DRAFT-001-DIGEST P2 波 P2-W06，CAND-TESTB-055，A7 技能
day-trade-pnl-estimate）：做T成本模型净盈亏预估（价差-双边佣金-印花税
-冲击成本四要素费率注入）+ 置信度（历史相似价差实现率滚动统计）
+ 成交回写校准（预估vs实现偏差滚动校正冲击系数，倍率钳制）。

查重分工：t0_point_analyzer=做T买卖点识别（本件=成本模型盈亏预估，
不识别买卖点）；t0_trading_pipeline=做T流水线编排（零交集）。

纯内存/DI设计；外部副作用（OS调用/网络/进程控制）全部经注入回调。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: fee_model 参数
#   fields: 参数 fee_model（无注解）
#   code: day_trade_pnl_estimator.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: day_trade_pnl_estimator.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: day_trade_pnl_estimator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① DayTradePnlEstimator
#   name_en: DayTradePnlEstimator
#   intro: 做T盈亏预估器（四要素成本模型+置信度+成交回写校准）。
#   desc: 做T盈亏预估器（四要素成本模型+置信度+成交回写校准）。；公共方法（定义序）: estimate, record_fill, impact_multiplier, fill_count, fills；源码 L189-L…
#   inputs: fee_model config clock
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: DayTradePnlEstimator
#   downstream: 运行时装配批（统一注入点装配）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "DayTradeFeeModel",
    "DayTradeFillRecord",
    "DayTradePnlConfig",
    "DayTradePnlError",
    "DayTradePnlEstimate",
    "DayTradePnlEstimator",
]


class DayTradePnlError(Exception):
    """做T盈亏预估协议输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-DAY-TRADE-PNL。
    """


def _validate_finite(name: str, value: float, lo: float) -> float:
    """校验为有限实数且 >= lo，否则 Fail-Closed。"""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DayTradePnlError(f"{name} 非数值: {value!r}")
    v = float(value)
    if math.isnan(v) or math.isinf(v):
        raise DayTradePnlError(f"{name} 非有限值: {value!r}")
    if v < lo:
        raise DayTradePnlError(f"{name} 越界: {value!r}（须>={lo}）")
    return v


def _validate_shares(shares: int) -> int:
    """校验股数为正整数。"""
    if isinstance(shares, bool) or not isinstance(shares, int) or shares <= 0:
        raise DayTradePnlError(f"shares 非法: {shares!r}（须为正整数）")
    return shares


@dataclass(frozen=True)
class DayTradeFeeModel:
    """做T四要素费率模型（注入）：单边佣金率/印花税率/冲击基准费率/单笔最低佣金。"""

    commission_rate: float
    stamp_tax_rate: float
    impact_rate: float
    min_commission: float = 0.0

    def __post_init__(self) -> None:
        _validate_finite("commission_rate", self.commission_rate, 0.0)
        _validate_finite("stamp_tax_rate", self.stamp_tax_rate, 0.0)
        _validate_finite("impact_rate", self.impact_rate, 0.0)
        _validate_finite("min_commission", self.min_commission, 0.0)


@dataclass(frozen=True)
class DayTradePnlConfig:
    """预估器配置（相似度容差/实现率阈值/校准窗口/倍率钳制）。"""

    similarity_tol: float = 0.002
    realize_threshold: float = 0.8
    calibration_window: int = 20
    mult_min: float = 0.5
    mult_max: float = 3.0

    def __post_init__(self) -> None:
        _validate_finite("similarity_tol", self.similarity_tol, 0.0)
        _validate_finite("realize_threshold", self.realize_threshold, 0.0)
        if (
            isinstance(self.calibration_window, bool)
            or not isinstance(self.calibration_window, int)
            or self.calibration_window < 1
        ):
            raise DayTradePnlError(f"calibration_window 非法: {self.calibration_window!r}（须为正整数）")
        _validate_finite("mult_min", self.mult_min, 1.0e-12)
        _validate_finite("mult_max", self.mult_max, 1.0e-12)
        if not self.mult_min <= self.mult_max:
            raise DayTradePnlError("mult_min 须小于等于 mult_max")


@dataclass(frozen=True)
class DayTradePnlEstimate:
    """做T净盈亏预估结果（四要素成本拆分+置信度）。"""

    buy_price: float
    sell_price: float
    shares: int
    gross_spread: float
    commission: float
    stamp_tax: float
    impact_cost: float
    net_pnl: float
    spread_ratio: float
    confidence: float
    confidence_samples: int
    impact_multiplier: float
    estimated_at: datetime.datetime


@dataclass(frozen=True)
class DayTradeFillRecord:
    """成交回写记录（预估vs实现偏差+冲击校正量）。"""

    buy_price: float
    sell_price: float
    shares: int
    spread_ratio: float
    estimated_net: float
    realized_net: float
    shortfall_rate: float
    realized_flag: bool
    filled_at: datetime.datetime


class DayTradePnlEstimator:
    """做T盈亏预估器（四要素成本模型+置信度+成交回写校准）。"""

    def __init__(
        self,
        *,
        fee_model: DayTradeFeeModel | None = None,
        config: DayTradePnlConfig | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if fee_model is None:
            raise DayTradePnlError("费率模型未注入（Fail-Closed）")
        if not isinstance(fee_model, DayTradeFeeModel):
            raise DayTradePnlError(f"费率模型类型非法: {type(fee_model)!r}")
        self._fees = fee_model
        self._cfg = config or DayTradePnlConfig()
        self._clock = clock or datetime.datetime.now
        self._fills: list[DayTradeFillRecord] = []
        self._multiplier = 1.0

    # ------------------------------------------------------------------
    # 预估
    # ------------------------------------------------------------------
    def estimate(self, buy_price: float, sell_price: float, shares: int) -> DayTradePnlEstimate:
        """净盈亏预估 = 价差 - 双边佣金 - 印花税 - 冲击成本（含置信度）。"""
        buy = _validate_finite("buy_price", buy_price, 1.0e-12)
        sell = _validate_finite("sell_price", sell_price, 1.0e-12)
        n = _validate_shares(shares)
        gross, commission, stamp, impact, net = self._cost_breakdown(buy, sell, n)
        spread_ratio = (sell - buy) / buy
        similar = [f for f in self._fills if abs(f.spread_ratio - spread_ratio) <= self._cfg.similarity_tol]
        confidence = sum(1.0 if f.realized_flag else 0.0 for f in similar) / len(similar) if similar else 0.0
        return DayTradePnlEstimate(
            buy_price=buy,
            sell_price=sell,
            shares=n,
            gross_spread=gross,
            commission=commission,
            stamp_tax=stamp,
            impact_cost=impact,
            net_pnl=net,
            spread_ratio=spread_ratio,
            confidence=confidence,
            confidence_samples=len(similar),
            impact_multiplier=self._multiplier,
            estimated_at=self._clock(),
        )

    # ------------------------------------------------------------------
    # 成交回写校准
    # ------------------------------------------------------------------
    def record_fill(
        self,
        buy_price: float,
        sell_price: float,
        shares: int,
        realized_net: float,
    ) -> DayTradeFillRecord:
        """成交回写：预估vs实现偏差滚动校正冲击系数（倍率钳制）。"""
        realized = _validate_finite("realized_net", realized_net, -1.0e18)
        est = self.estimate(buy_price, sell_price, shares)
        turnover = est.buy_price * est.shares + est.sell_price * est.shares
        shortfall_rate = (est.net_pnl - realized) / turnover
        if est.net_pnl > 0.0:
            realized_flag = realized >= self._cfg.realize_threshold * est.net_pnl
        else:
            realized_flag = realized >= est.net_pnl
        record = DayTradeFillRecord(
            buy_price=est.buy_price,
            sell_price=est.sell_price,
            shares=est.shares,
            spread_ratio=est.spread_ratio,
            estimated_net=est.net_pnl,
            realized_net=realized,
            shortfall_rate=shortfall_rate,
            realized_flag=realized_flag,
            filled_at=self._clock(),
        )
        self._fills.append(record)
        del self._fills[: max(0, len(self._fills) - self._cfg.calibration_window)]
        self._recalibrate()
        _log.info(
            "成交回写: 价差=%.4f%% 预估=%.2f 实现=%.2f 冲击倍率→%.4f",
            est.spread_ratio * 100.0,
            est.net_pnl,
            realized,
            self._multiplier,
        )
        return record

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------
    @property
    def impact_multiplier(self) -> float:
        """现行冲击系数倍率（回写校准后）。"""
        return self._multiplier

    @property
    def fill_count(self) -> int:
        """回写记录数（校准窗口内）。"""
        return len(self._fills)

    def fills(self) -> tuple[DayTradeFillRecord, ...]:
        """回写记录（按回写先后升序）。"""
        return tuple(self._fills)

    # ------------------------------------------------------------------
    # 内部
    # ------------------------------------------------------------------
    def _cost_breakdown(self, buy: float, sell: float, shares: int) -> tuple[float, float, float, float, float]:
        """四要素成本拆分（价差/双边佣金/印花税/冲击成本）。"""
        buy_amount = buy * shares
        sell_amount = sell * shares
        gross = sell_amount - buy_amount
        commission = max(buy_amount * self._fees.commission_rate, self._fees.min_commission) + max(
            sell_amount * self._fees.commission_rate, self._fees.min_commission
        )
        stamp = sell_amount * self._fees.stamp_tax_rate
        impact = (buy_amount + sell_amount) * self._fees.impact_rate * self._multiplier
        net = gross - commission - stamp - impact
        return gross, commission, stamp, impact, net

    def _recalibrate(self) -> None:
        """按窗口内平均偏差率滚动校正冲击倍率（钳制 [mult_min, mult_max]）。"""
        if self._fees.impact_rate <= 0.0 or not self._fills:
            self._multiplier = 1.0
            return
        mean_shortfall = sum(f.shortfall_rate for f in self._fills) / len(self._fills)
        raw = 1.0 + mean_shortfall / self._fees.impact_rate
        self._multiplier = min(self._cfg.mult_max, max(self._cfg.mult_min, raw))
