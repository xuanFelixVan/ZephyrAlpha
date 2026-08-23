# [BLUEPRINT] MOD-CMP-007 | docs/03_modules/_domain_compliance/trading_compliance_detector/blueprint.md
# [MODULE] zephyr.compliance.trading_compliance_detector
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] stdlib + zephyr.compliance.compliance_log
# [CONSUMERS] C-004 风控引擎（Pre-Trade/盘中实时嵌入，43 号 §7.1）; 自我监控证据链 T+1 归档
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 检测目标=自我监控+自证清白（非高频对冲）; 命中一律 Hard Block+告警; 检测引擎失效=Fail-Closed 拒发任何订单; 速率/撤单率计数器消费 24/40 号不重复实现
# [MODIFY-GUARD] 43_compliance_discipline.md §7（BM-BUY-15）
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TradingComplianceError(ZA-CMP-0005)
# [TESTS] tests/compliance/test_trading_compliance_detector.py
# [TTL] permanent

"""交易合规检测（43_compliance_discipline §7，BM-BUY-15 补强）。

区别于 BM-BUY-08-B（行为纪律，管"人"），本环节管"法"——监管规则符合性。
检测目标：**自我监控 + 证据留存**（监管问询时可自证"未实施操纵"），
输出落 compliance_log 并 T+1 归档（§7.3）。

检测规则（§7.2/§7.3 阈值默认值）：
  | 类型       | 检测规则                                                     | 处置        |
  |-----------|-------------------------------------------------------------|------------|
  | 拉抬打压   | 短窗价格偏离 ±3% 且我方成交占比 > 30%（MVP 初始值，待校准）      | Hard Block |
  | 大额成交   | 单笔 > 该标的分钟均量 50%（MVP 初始值，待校准）                  | Hard Block |
  | Spoofing  | 大额挂单(>分钟均量 20%)后 10s 内撤单，同 pattern 30min ≥3 次     | Hard Block |
  | Layering  | 同侧连续 ≥3 档价格梯度单且序列内总撤单率 > 80%                   | Hard Block |
  | WashTrade | 自成交（买卖双方同账户），零容忍                               | Hard Block+人工复核 |
  | 尾盘操纵   | 14:57-15:00 申报价偏离收盘前 VWAP > 2% 且量占比 > 30%           | Hard Block |

已有基座不重复实现（§7.6）：瞬时申报速率/撤单率真源在 24 号 §3.7（令牌桶）
与 40 号（CancelRateGuard/价格笼子）；50μs 订单停留时间锁裁定不适用
（§7.5，降为记录性参数，见 compliance_report_registry）。

Version: 1.0.0
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from datetime import datetime, time

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.shared.foundation.errors import ZephyrBaseError


class TradingComplianceError(ZephyrBaseError):
    """交易合规检测错误。"""

    error_code = "ZA-CMP-0005"


class ManipulationType(enum.Enum):
    """检测类型。"""

    RAMP_DUMP = "RAMP_DUMP"  # 拉抬打压（异常交易行为）
    LARGE_TRADE = "LARGE_TRADE"  # 短时间大额成交（异常交易行为）
    SPOOFING = "SPOOFING"  # 幌骗
    LAYERING = "LAYERING"  # 分层
    WASH_TRADE = "WASH_TRADE"  # 对倒/自成交
    CLOSE_MANIPULATION = "CLOSE_MANIPULATION"  # 尾盘操纵


class ComplianceAction(enum.Enum):
    """处置。"""

    PASS = "PASS"
    HARD_BLOCK = "HARD_BLOCK"


@dataclass(frozen=True)
class ComplianceThresholds:
    """阈值（§7.2/§7.3；ramp/large 两条为 MVP 初始值，待实盘校准）。"""

    ramp_price_deviation: float = 0.03  # 拉抬打压：短窗价格偏离（MVP 待校准）
    ramp_volume_share: float = 0.30  # 拉抬打压：我方成交占比（MVP 待校准）
    large_trade_ratio: float = 0.50  # 大额成交：单笔/分钟均量（MVP 待校准）
    spoof_size_ratio: float = 0.20  # 幌骗：大额挂单/分钟均量
    spoof_cancel_window_s: float = 10.0  # 幌骗：挂单后撤单窗口（秒）
    spoof_repeat: int = 3  # 幌骗：30min 内同 pattern 次数
    spoof_repeat_window_s: float = 1800.0  # 幌骗：重复统计窗口（30min）
    layer_min_levels: int = 3  # 分层：最少梯度档数
    layer_cancel_ratio: float = 0.80  # 分层：序列内撤单率
    close_deviation: float = 0.02  # 尾盘：申报价偏离收盘前 VWAP
    close_volume_share: float = 0.30  # 尾盘：量占比
    close_window_start: time = time(14, 57)  # 尾盘：收盘集合竞价起点


@dataclass(frozen=True)
class ComplianceOrderRecord:
    """订单记录（检测输入）。"""

    order_id: str
    symbol: str
    side: str  # BUY / SELL
    price: float
    qty: float
    placed_at: datetime
    cancelled_at: datetime | None = None  # None=未撤单


@dataclass(frozen=True)
class ComplianceTradeRecord:
    """成交记录（对倒检测输入）。"""

    symbol: str
    price: float
    qty: float
    traded_at: datetime
    buyer_account: str
    seller_account: str


@dataclass(frozen=True)
class ManipulationVerdict:
    """检测结论（不可变）。"""

    mtype: ManipulationType
    action: ComplianceAction
    detail: str


class TradingComplianceDetector:
    """交易合规检测器（§7.2 异常 2 条 + §7.3 操纵 4 类，嵌入 C-004）。

    全部命中均为 Hard Block + 告警 + 落 compliance_log（证据链）。
    """

    def __init__(
        self,
        thresholds: ComplianceThresholds | None = None,
        logger: ComplianceLogger | None = None,
    ) -> None:
        self._t = thresholds or ComplianceThresholds()
        self._logger = logger or ComplianceLogger()

    @property
    def thresholds(self) -> ComplianceThresholds:
        """阈值只读访问（§7.3 SSoT；MOD-CMP-011 批处理窗口口径对齐消费）。"""
        return self._t

    @property
    def logger(self) -> ComplianceLogger:
        """落库器只读访问（MOD-CMP-011 批处理汇总事件共用同一证据链）。"""
        return self._logger

    # ── §7.2 异常交易行为（拉抬打压 / 大额成交）──

    def check_ramp_dump(self, price_change_pct: float, our_volume_share: float) -> ManipulationVerdict | None:
        """拉抬打压：短窗价格偏离超阈值且我方成交占比超阈值。

        Args:
            price_change_pct: 短窗（5min）价格变动（小数，带符号）。
            our_volume_share: 该窗口内我方成交量占市场总量比例。
        """
        t = self._t
        if abs(price_change_pct) >= t.ramp_price_deviation and our_volume_share > t.ramp_volume_share:
            return self._hit(
                ManipulationType.RAMP_DUMP,
                f"短窗价格偏离 {price_change_pct:.2%} ≥ {t.ramp_price_deviation:.2%}"
                f"且我方量占比 {our_volume_share:.2%} > {t.ramp_volume_share:.2%}",
            )
        return None

    def check_large_trade(self, order_qty: float, minute_avg_volume: float) -> ManipulationVerdict | None:
        """大额成交：单笔数量 > 该标的分钟均量阈值比例。"""
        t = self._t
        if minute_avg_volume > 0 and order_qty > t.large_trade_ratio * minute_avg_volume:
            return self._hit(
                ManipulationType.LARGE_TRADE,
                f"单笔 {order_qty:.0f} > {t.large_trade_ratio:.0%}×分钟均量 {minute_avg_volume:.0f}",
            )
        return None

    # ── §7.3 市场操纵 4 类 ──

    def check_spoofing(
        self, orders: list[ComplianceOrderRecord], minute_avg_volume: float
    ) -> ManipulationVerdict | None:
        """幌骗：大额挂单后短时撤单，且同 pattern 30min 内重复 ≥3 次。

        Args:
            orders: 同一标的近 30min 订单序列（调用方按窗口预筛）。
            minute_avg_volume: 该标的分钟均量。
        """
        t = self._t
        if minute_avg_volume <= 0:
            return None
        hits = [
            o
            for o in orders
            if o.qty > t.spoof_size_ratio * minute_avg_volume
            and o.cancelled_at is not None
            and (o.cancelled_at - o.placed_at).total_seconds() <= t.spoof_cancel_window_s
        ]
        if len(hits) >= t.spoof_repeat:
            return self._hit(
                ManipulationType.SPOOFING,
                f"30min 内大额快撤 {len(hits)} 次 ≥ {t.spoof_repeat} 次"
                f"（单量>{t.spoof_size_ratio:.0%}分钟均量且 {t.spoof_cancel_window_s:.0f}s 内撤单）",
            )
        return None

    def check_layering(self, orders: list[ComplianceOrderRecord]) -> ManipulationVerdict | None:
        """分层：同侧连续 ≥3 档价格梯度单且序列内撤单率 > 80%。

        Args:
            orders: 同一标的同侧、按挂单价排序的连续梯度单序列（调用方预筛）。
        """
        t = self._t
        if len(orders) < t.layer_min_levels:
            return None
        prices = {o.price for o in orders}
        if len(prices) < t.layer_min_levels:
            return None
        cancelled = sum(1 for o in orders if o.cancelled_at is not None)
        cancel_ratio = cancelled / len(orders)
        if cancel_ratio > t.layer_cancel_ratio:
            return self._hit(
                ManipulationType.LAYERING,
                f"同侧 {len(prices)} 档梯度单 ≥ {t.layer_min_levels} 且撤单率"
                f" {cancel_ratio:.0%} > {t.layer_cancel_ratio:.0%}",
            )
        return None

    def check_wash_trade(self, trade: ComplianceTradeRecord) -> ManipulationVerdict | None:
        """对倒：自成交零容忍（买卖双方同账户/同一实控人标记）。"""
        if trade.buyer_account == trade.seller_account:
            return self._hit(
                ManipulationType.WASH_TRADE,
                f"自成交：买卖同账户 {trade.buyer_account}，{trade.symbol}"
                f" {trade.qty:.0f}股@{trade.price:.2f}——立即人工复核",
            )
        return None

    def check_close_manipulation(
        self,
        order_price: float,
        order_qty: float,
        pre_close_vwap: float,
        window_total_volume: float,
        at_time: time,
    ) -> ManipulationVerdict | None:
        """尾盘操纵：14:57-15:00 申报价偏离收盘前 VWAP > 2% 且量占比 > 30%。

        Args:
            order_price / order_qty: 申报价/量。
            pre_close_vwap: 收盘前 VWAP。
            window_total_volume: 尾盘窗口市场总成交量。
            at_time: 申报时刻（仅 14:57 起进入检测窗口）。
        """
        t = self._t
        if at_time < t.close_window_start:
            return None
        if pre_close_vwap <= 0:
            return None
        deviation = order_price / pre_close_vwap - 1
        share = order_qty / window_total_volume if window_total_volume > 0 else 0.0
        if abs(deviation) > t.close_deviation and share > t.close_volume_share:
            return self._hit(
                ManipulationType.CLOSE_MANIPULATION,
                f"尾盘申报价偏离 VWAP {deviation:.2%} > {t.close_deviation:.2%}"
                f"且量占比 {share:.2%} > {t.close_volume_share:.2%}",
            )
        return None

    # ── 聚合 ──

    def run_all(self, *verdicts: ManipulationVerdict | None) -> list[ManipulationVerdict]:
        """聚合各检测结果（过滤 PASS/None），供 C-004 统一阻断。"""
        return [v for v in verdicts if v is not None]

    def _hit(self, mtype: ManipulationType, detail: str) -> ManipulationVerdict:
        verdict = ManipulationVerdict(mtype=mtype, action=ComplianceAction.HARD_BLOCK, detail=detail)
        self._logger.log(
            "MANIPULATION_VERDICT",
            "trading_compliance_detector",
            {"mtype": mtype.value, "action": verdict.action.value, "detail": detail},
        )
        return verdict
