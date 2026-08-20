# [BLUEPRINT] MOD-CMP-007 | docs/03_modules/_domain_compliance/trading_compliance_detector/blueprint.md
# [MODULE] zephyr.compliance.manipulation_stream_driver
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] zephyr.compliance.trading_compliance_detector(同一 detector 实例驱动, 不重复实现检测规则); zephyr.shared.foundation.errors
# [CONSUMERS] 盘中实时流接线层(43号§10边界: 由盘中实时流以同一 detector 实例驱动, 不在 Pre-Trade 链范围)
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 检测规则唯一真源=TradingComplianceDetector(本模块只做窗口缓存+预筛, 不重复实现); 事件驱动零定时器(on_order/on_cancel/on_trade 喂入); 30min 滚动窗口(trim 防内存膨胀); WashTrade 零容忍即时检测; minute_volume_provider 缺失→Spoofing 跳过不误判(降级不阻断); 不接真实流(调用方喂事件)
# [MODIFY-GUARD] 43_compliance_discipline.md §7.3/§10
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidStreamEventError(ZA-CMP-0006)
# [TESTS] tests/compliance/test_manipulation_stream_driver.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: ComplianceOrderRecord(挂单/撤单事件) + ComplianceTradeRecord(成交事件) + minute_volume_provider(分钟均量注入)
# F1: on_order_placed(record)——入窗口缓存→评估该 symbol(Spoofing 需分钟均量/Layering 同侧梯度序列预筛)
# F2: on_order_cancelled(symbol, order_id, cancelled_at)——冻结记录 replace 标记撤单→重评估
# F3: on_trade(trade)——WashTrade 零容忍即时检测(买卖双方同账户)
# F4: trim_before(cutoff)——30min 滚动窗口修剪(detector.spoof_repeat_window_s 口径)
# A1: _evaluate_symbol(symbol)——check_spoofing(窗口内全部订单) + check_layering(同侧按时间序单调梯度最长run≥3档)
# O1: list[ManipulationVerdict](命中一律 HARD_BLOCK, 证据由 detector 落 compliance_log)
# [/ALGO_FLOW]
"""D_COMPLIANCE — 市场操纵盘中实时检测流驱动适配（43 号 §10 边界项施工）。

43 号 §10 施工记录边界："Spoofing/Layering/WashTrade 需订单/成交历史，由盘中
实时流以同一 detector 实例驱动，不在 Pre-Trade 链范围"。本模块即该实时流
驱动适配层——不接真实流（调用方按事件喂入），只做三件事：
  1. 30min 滚动窗口订单缓存（撤单标记 replace 更新）；
  2. 检测预筛（同侧梯度序列 run 构造 / 分钟均量供给桥）；
  3. 以**同一 TradingComplianceDetector 实例**驱动检测（规则唯一真源，
     本模块零重复实现）。

降级：minute_volume_provider 缺失 → Spoofing 检测跳过（不缺数据硬判，
防误伤——43 号 §7.3"防误伤"口径）；Layering/WashTrade 不依赖均量正常评估。
"""

from __future__ import annotations

import logging
from dataclasses import replace
from datetime import datetime
from itertools import pairwise
from typing import Callable

from zephyr.compliance.trading_compliance_detector import (
    ComplianceOrderRecord,
    ComplianceTradeRecord,
    ManipulationVerdict,
    TradingComplianceDetector,
)
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)


class InvalidStreamEventError(ZephyrBaseError):
    """实时流事件非法——空 symbol/order_id、时间倒挂等。"""

    error_code = "ZA-CMP-0006"


class ManipulationStreamDriver:
    """Spoofing/Layering/WashTrade 盘中实时检测驱动适配器。

    Args:
        detector: TradingComplianceDetector 实例（None=自建默认阈值实例）。
            同一实例驱动——检测规则/阈值/落日志全归 detector。
        minute_volume_provider: callable(symbol) -> float 分钟均量供给
            （Spoofing 检测前提；None=Spoofing 跳过降级）。
    """

    def __init__(
        self,
        detector: TradingComplianceDetector | None = None,
        *,
        minute_volume_provider: Callable[[str], float] | None = None,
    ) -> None:
        self._detector = detector or TradingComplianceDetector()
        self._minute_volume_provider = minute_volume_provider
        # symbol -> order_id -> 订单记录（撤单标记原地 replace）
        self._orders: dict[str, dict[str, ComplianceOrderRecord]] = {}

    # ── 事件喂入 ──

    def on_order_placed(self, record: ComplianceOrderRecord) -> list[ManipulationVerdict]:
        """挂单事件：入窗 + 评估该标的。返回命中结论（空=未命中）。"""
        self._require_symbol(record.symbol)
        if not record.order_id:
            raise InvalidStreamEventError("order_id 不能为空", details={"symbol": record.symbol})
        self._orders.setdefault(record.symbol, {})[record.order_id] = record
        return self._evaluate_symbol(record.symbol)

    def on_order_cancelled(
        self,
        symbol: str,
        order_id: str,
        cancelled_at: datetime,
    ) -> list[ManipulationVerdict]:
        """撤单事件：标记撤单时间 + 重评估该标的。"""
        self._require_symbol(symbol)
        if not order_id:
            raise InvalidStreamEventError("order_id 不能为空", details={"symbol": symbol})
        book = self._orders.get(symbol, {})
        record = book.get(order_id)
        if record is None:
            _logger.debug("撤单事件无对应挂单（窗口外/未知单）: %s %s", symbol, order_id)
            return []
        if cancelled_at < record.placed_at:
            raise InvalidStreamEventError(
                "撤单时间早于挂单时间（时钟倒挂）",
                details={"symbol": symbol, "order_id": order_id},
            )
        book[order_id] = replace(record, cancelled_at=cancelled_at)
        return self._evaluate_symbol(symbol)

    def on_trade(self, trade: ComplianceTradeRecord) -> list[ManipulationVerdict]:
        """成交事件：WashTrade 零容忍即时检测。"""
        self._require_symbol(trade.symbol)
        verdict = self._detector.check_wash_trade(trade)
        return [verdict] if verdict is not None else []

    # ── 窗口维护 ──

    def trim_before(self, cutoff: datetime) -> int:
        """修剪 30min 滚动窗口（placed_at 早于 cutoff 且未撤单的订单剔除）。
        已撤单订单在 spoof_repeat_window 内仍计 pattern——修剪口径与
        detector.spoof_repeat_window_s 对齐由调用方传 cutoff 保证。
        返回剔除条数。
        """
        removed = 0
        for symbol in list(self._orders):
            book = self._orders[symbol]
            for order_id in list(book):
                if book[order_id].placed_at < cutoff:
                    del book[order_id]
                    removed += 1
            if not book:
                del self._orders[symbol]
        return removed

    def window_size(self, symbol: str) -> int:
        """该标的当前窗口缓存条数（观测用）。"""
        return len(self._orders.get(symbol, {}))

    # ── 检测驱动 ──

    def _evaluate_symbol(self, symbol: str) -> list[ManipulationVerdict]:
        orders = list(self._orders.get(symbol, {}).values())
        if not orders:
            return []
        verdicts: list[ManipulationVerdict] = []

        # Spoofing：需分钟均量（provider 缺失降级跳过，防误伤）
        if self._minute_volume_provider is not None:
            minute_avg = float(self._minute_volume_provider(symbol))
            verdict = self._detector.check_spoofing(orders, minute_avg)
            if verdict is not None:
                verdicts.append(verdict)

        # Layering：同侧按挂单时间序的单调梯度 run（min_levels 阈值由 detector 判定，
        # 本层不预筛档数——阈值唯一真源归 detector，防双真源漂移）
        for run in self._layering_runs(orders):
            verdict = self._detector.check_layering(run)
            if verdict is not None:
                verdicts.append(verdict)
                break  # 同标的一次评估报一条（防告警风暴）

        return verdicts

    def _layering_runs(self, orders: list[ComplianceOrderRecord]) -> list[list[ComplianceOrderRecord]]:
        """构造同侧单调价格梯度 run 候选序列（按挂单时间序，严格单调升或降）。"""
        runs: list[list[ComplianceOrderRecord]] = []
        by_side: dict[str, list[ComplianceOrderRecord]] = {}
        for o in orders:
            by_side.setdefault(o.side, []).append(o)
        for side_orders in by_side.values():
            side_orders.sort(key=lambda o: o.placed_at)
            for direction in ("asc", "desc"):
                run = self._longest_monotonic_run(side_orders, direction)
                if len(run) >= 2:  # 最小单调对；档数阈值归 detector.check_layering
                    runs.append(run)
        return runs

    @staticmethod
    def _longest_monotonic_run(
        orders: list[ComplianceOrderRecord], direction: str
    ) -> list[ComplianceOrderRecord]:
        """时间序上最长严格单调（升/降）价格连续子序列。"""
        if not orders:
            return []
        best: list[ComplianceOrderRecord] = []
        current = [orders[0]]
        for prev, cur in pairwise(orders):
            step_ok = cur.price > prev.price if direction == "asc" else cur.price < prev.price
            if step_ok:
                current.append(cur)
            else:
                if len(current) > len(best):
                    best = current
                current = [cur]
        return best if len(best) >= len(current) else current

    @staticmethod
    def _require_symbol(symbol: str) -> None:
        if not symbol or not symbol.strip():
            raise InvalidStreamEventError("symbol 不能为空", details={"symbol": repr(symbol)})


__all__ = [
    "InvalidStreamEventError",
    "ManipulationStreamDriver",
]
