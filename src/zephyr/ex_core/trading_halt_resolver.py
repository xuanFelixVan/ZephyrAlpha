# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.trading_halt_resolver
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib
# [CONSUMERS] ex_core.trading_session ; ex_core.open_order_resolver
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 停牌期间不挂不撤等复牌;跨日停牌移除目标+释放预占;复牌后重新评估;目标票停牌当日跳过
# [MODIFY-GUARD] 40_execution_broker.md §决策⑮
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TradingHaltResolverError
# [TESTS] tests/ex_core/test_trading_halt_resolver.py
# [TTL] permanent

"""

临时停牌处理（40_execution_broker §决策⑮ gap 14 施工）。

实盘生存项——持仓票被停牌核查会锁住资金无法平仓，目标股停牌无法建仓，复牌后
可能跌停（如爱丽家居 9 连板后停牌核查，复牌跌停风险）。缺失会导致系统对着停牌票
反复报废单、资金预占额度被锁死。

处理规则（§2.16 决策⑮）：
  | 场景                        | 处理策略                                      |
  |-----------------------------|-----------------------------------------------|
  | 持仓票盘中临时停牌（10分钟） | 不操作等复牌，未成交卖单保留                   |
  | 目标买入票盘中临时停牌       | 从当日 firm_target_portfolio 移除，不报单      |
  | 持仓票跨日停牌核查（1-5日）  | ①从后续目标移除②释放资金预占③复牌后重新评估   |
  | 持仓票跨日停牌复牌后         | ①重新评估目标权重②跌停→挂跌停价③流动性恢复→正常|
  | 目标票停牌                  | 当日跳过，下轮调仓再评估                       |

A 股临时停牌类型（上交所 2026 修订交易规则 §4.2）：
  - 盘中临时停牌（无涨跌幅股）：新股前5日/退市整理，±30%/±60% 触发，10分钟
  - 盘中临时停牌（换手率/涉嫌违规）：风险警示股换手率>30%，至14:55或收盘
  - 跨日停牌核查（严重异动）：10日4次同向异动/累计±100%，1-5交易日
  - 重大事项停牌：重组/控制权变更，1-N交易日

与现有决策协同：
  - 决策① T+1 校验：_check_t_plus_1 已实现"停牌跳过"（submit_order 检测跳过）
  - 决策⑬ 资金预占：跨日停牌票的预占额度必须释放
  - 决策⑪ 尾盘清退：停牌票未成交订单在 14:55 一并撤单（若可撤）
  - 决策⑭ 挂单价：复牌后若跌停，卖单挂跌停价

依据：40_execution_broker.md v2.4.0 §决策⑮
Version: 1.0.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 停牌信息 HaltInfo（盘前/盘中批量拉取）
#   fields: symbol + is_halted + halt_type(4类) + is_cross_day + expected_resume + can_place/cancel_order
#   code: HaltInfo L91-113
# - id: I2
#   name: 目标权重 target_weights
#   fields: {symbol: weight} 当日调仓目标
#   code: filter_target_weights L210
# - id: I3
#   name: 当前持仓集合 held_symbols
#   fields: 持仓 symbol 集合（判断持仓票跨日停牌释放预占用）
#   code: filter_target_weights L213
# 层: 算法
# - id: A1
#   name_zh: ① 停牌状态维护
#   name_en: update_halt_status/batch_update/clear_resumed
#   intro: 维护 symbol→HaltInfo 映射表，盘前批量更新，复牌的清出缓存
#   desc: update_halt_status 单只写入 _halt_map；batch_update 批量；clear_resumed 清出 is_halted=False 的记录并返回复牌列表（L159-186）
#   inputs: I1
#   outputs: 停牌状态表 _halt_map
# - id: A2
#   name_zh: ② 下单前停牌检查
#   name_en: check_order_allowed
#   intro: 下单前查该票能否报单，跨日停牌要释放预占，盘中临停当日跳过
#   desc: 无记录或未停牌→NORMAL；is_cross_day→HALTED_RELEASE_PREPAID；否则盘中临停→HALTED_REMOVE_FROM_TARGET（L190-208）
#   inputs: A1
#   outputs: HaltStatus 决策枚举
#   invariant: 停牌期间不挂不撤等复牌
# - id: A3
#   name_zh: ③ 目标权重过滤
#   name_en: filter_target_weights
#   intro: 调仓前把停牌票从当日目标里剔除，跨日停牌的持仓票标记释放资金预占
#   desc: 遍历 target_weights：正常/已复牌→保留（曾释放预占的复牌票标 RESUMED_REEVALUATE）；跨日停牌→移除+持仓票首次标 release_prepaid（_released_prepaid 防重复）；盘中临停→移除当日跳过（L210-272）
#   inputs: A1 I2 I3
#   outputs: (过滤后目标权重, HaltAction 动作列表)
#   invariant: 跨日停牌移除目标+释放预占；无副作用返回新 dict
# - id: A4
#   name_zh: ④ 持仓票停牌检查
#   name_en: check_position_halt
#   intro: 持仓票盘中临停保留不动等复牌，跨日停牌标记释放预占
#   desc: 未停牌→NORMAL；is_cross_day→HALTED_RELEASE_PREPAID；盘中临停→HALTED_KEEP_POSITION（L274-294）
#   inputs: A1
#   outputs: HaltStatus 决策枚举
# 层: 输出
# - id: O1
#   name_zh: 停牌决策状态 HaltStatus
#   name_en: HaltStatus
#   intro: 5 态决策枚举（移除目标/保留持仓/释放预占/复牌重估/正常）供下单与持仓管理分支
#   downstream: ex_core.trading_session ; ex_core.open_order_resolver
# - id: O2
#   name_zh: 过滤后目标权重 + 停牌动作列表
#   name_en: filtered target_weights + HaltAction list
#   intro: 剔除停牌票的目标权重和带理由的审计动作记录
#   downstream: ex_core.trading_session
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A1 --> A3
# A1 --> A4
# I2 --> A3
# I3 --> A3
# A2 --> O1
# A4 --> O1
# A3 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Final

__all__: Final = [
    "HaltType",
    "HaltStatus",
    "TradingHaltResolverError",
    "TradingHaltResolver",
]

_logger = logging.getLogger(__name__)


class TradingHaltResolverError(Exception):
    """临时停牌处理错误。"""

    error_code = "ZA-XC-0014"


class HaltType(str, Enum):
    """A 股临时停牌类型（上交所 2026 修订交易规则 §4.2）。"""

    INTRADAY_PRICE_LIMIT = "intraday_price_limit"  # 盘中临停（无涨跌幅股±30%/±60%）
    INTRADAY_VIOLATION = "intraday_violation"      # 盘中临停（换手率/涉嫌违规）
    CROSS_DAY_REVIEW = "cross_day_review"          # 跨日停牌核查（严重异动）
    MAJOR_EVENT = "major_event"                    # 重大事项停牌
    UNKNOWN = "unknown"


class HaltStatus(str, Enum):
    """停牌状态决策结果。"""

    HALTED_REMOVE_FROM_TARGET = "halted_remove_from_target"  # 停牌，从目标移除
    HALTED_KEEP_POSITION = "halted_keep_position"            # 持仓停牌，保留不动
    HALTED_RELEASE_PREPAID = "halted_release_prepaid"        # 跨日停牌，释放资金预占
    RESUMED_REEVALUATE = "resumed_reevaluate"                # 复牌，重新评估
    NORMAL = "normal"                                        # 正常，无停牌


@dataclass(frozen=True)
class HaltInfo:
    """单只股票的停牌信息（不可变）。

    Attributes:
        symbol: 股票代码
        is_halted: 当前是否停牌
        halt_type: 停牌类型
        halt_start: 停牌开始时间
        expected_resume: 预计复牌时间（None=未知）
        is_cross_day: 是否跨日停牌
        can_place_order: 停牌期间能否挂单
        can_cancel_order: 停牌期间能否撤单
    """

    symbol: str
    is_halted: bool
    halt_type: HaltType = HaltType.UNKNOWN
    halt_start: datetime | None = None
    expected_resume: datetime | None = None
    is_cross_day: bool = False
    can_place_order: bool = False
    can_cancel_order: bool = False


@dataclass
class TradingHaltResolver:
    """临时停牌处理器。

    根据停牌状态决定对目标/持仓的处理策略。核心原则：
    "停牌期间不挂不撤等复牌、跨日停牌核查移除出当日目标、复牌后重新评估"。

    用法:
        resolver = TradingHaltResolver()

        # 1. 盘前拉取停牌列表
        resolver.update_halt_status("600000.SH", HaltInfo(
            symbol="600000.SH", is_halted=True,
            halt_type=HaltType.CROSS_DAY_REVIEW,
            is_cross_day=True,
        ))

        # 2. 调仓前过滤目标
        target_weights = {"600000.SH": 0.1, "000001.SZ": 0.2}
        filtered, actions = resolver.filter_target_weights(
            target_weights, held_symbols={"600000.SH"},
        )
        # 600000.SH 跨日停牌 → 从目标移除，actions 含 RELEASE_PREPAID

        # 3. 下单前检查停牌
        status = resolver.check_order_allowed("600000.SH")
        if status is HaltStatus.HALTED_REMOVE_FROM_TARGET:
            skip_order()  # 跳过下单

    设计要点:
      - **状态驱动**：维护 symbol -> HaltInfo 映射，盘前批量更新
      - **无副作用决策**：filter_target_weights 返回新 dict + 动作列表，不改输入
      - **审计友好**：HaltAction 记录每笔决策理由
      - **与资金预占解耦**：只决策"是否释放预占"，实际释放由调用方执行
    """

    # symbol -> HaltInfo
    _halt_map: dict[str, HaltInfo] = field(default_factory=dict)
    # 跨日停牌票的预占释放记录（防止重复释放）
    _released_prepaid: set[str] = field(default_factory=set)

    # ── 状态更新 ──

    def update_halt_status(self, symbol: str, info: HaltInfo) -> None:
        """更新单只股票的停牌状态（盘前/盘中批量拉取后调用）。"""
        self._halt_map[symbol] = info
        _logger.info(
            "停牌状态更新: %s halted=%s type=%s cross_day=%s",
            symbol, info.is_halted, info.halt_type.value, info.is_cross_day,
        )

    def batch_update(self, infos: list[HaltInfo]) -> None:
        """批量更新停牌状态。"""
        for info in infos:
            self._halt_map[info.symbol] = info

    def clear_resumed(self) -> list[str]:
        """清理已复牌的股票记录，返回本次清理的 symbol 列表。

        复牌后需重新评估目标权重（调用方职责），本方法只清理停牌缓存。
        """
        resumed = [
            sym for sym, info in self._halt_map.items()
            if not info.is_halted
        ]
        for sym in resumed:
            self._halt_map.pop(sym, None)
            self._released_prepaid.discard(sym)
        if resumed:
            _logger.info("清理已复牌股票: %s", resumed)
        return resumed

    # ── 决策接口 ──

    def check_order_allowed(self, symbol: str) -> HaltStatus:
        """检查是否允许对该 symbol 下单。

        Args:
            symbol: 股票代码

        Returns:
            HaltStatus 决策结果
        """
        info = self._halt_map.get(symbol)
        if info is None or not info.is_halted:
            return HaltStatus.NORMAL

        # 停牌期间：根据类型决定
        if info.is_cross_day:
            # 跨日停牌：从目标移除 + 释放预占
            return HaltStatus.HALTED_RELEASE_PREPAID
        # 盘中临停：从目标移除（无法成交）
        return HaltStatus.HALTED_REMOVE_FROM_TARGET

    def filter_target_weights(
        self,
        target_weights: dict[str, float],
        held_symbols: set[str] | None = None,
    ) -> tuple[dict[str, float], list[HaltAction]]:
        """过滤目标权重，移除停牌票。

        - 目标票停牌（盘中临停/跨日停牌）→ 从目标移除
        - 持仓票跨日停牌 → 标记释放资金预占
        - 已复牌票 → 标记重新评估（但仍保留在目标中，由策略层决定权重）

        Args:
            target_weights: 原始目标权重
            held_symbols: 当前持仓的 symbol 集合（用于判断持仓票停牌）

        Returns:
            (过滤后的目标权重, 动作列表)
        """
        held = held_symbols or set()
        filtered: dict[str, float] = {}
        actions: list[HaltAction] = []

        for symbol, weight in target_weights.items():
            info = self._halt_map.get(symbol)
            if info is None or not info.is_halted:
                # 正常或已复牌 → 保留
                filtered[symbol] = weight
                if info is not None and not info.is_halted and symbol in self._released_prepaid:
                    # 之前释放过预占，现在复牌 → 标记重新评估
                    actions.append(HaltAction(
                        symbol=symbol,
                        status=HaltStatus.RESUMED_REEVALUATE,
                        reason="复牌后重新评估（之前跨日停牌已释放预占）",
                        remove_from_target=False,
                        release_prepaid=False,
                    ))
                continue

            # 停牌处理
            if info.is_cross_day:
                # 跨日停牌：从目标移除 + 释放预占（持仓票，仅首次释放）
                should_release = symbol in held and symbol not in self._released_prepaid
                if should_release:
                    self._released_prepaid.add(symbol)
                actions.append(HaltAction(
                    symbol=symbol,
                    status=HaltStatus.HALTED_RELEASE_PREPAID,
                    reason=f"跨日停牌（{info.halt_type.value}），从目标移除"
                           + ("并释放资金预占" if should_release else ""),
                    remove_from_target=True,
                    release_prepaid=should_release,
                ))
            else:
                # 盘中临停：从目标移除（无法成交）
                actions.append(HaltAction(
                    symbol=symbol,
                    status=HaltStatus.HALTED_REMOVE_FROM_TARGET,
                    reason=f"盘中临时停牌（{info.halt_type.value}），当日跳过",
                    remove_from_target=True,
                    release_prepaid=False,
                ))

        return filtered, actions

    def check_position_halt(self, symbol: str) -> HaltStatus:
        """检查持仓票的停牌状态（用于持仓管理）。

        持仓票停牌处理：
        - 盘中临停（10分钟）：保留不动，等复牌（HALTED_KEEP_POSITION）
        - 跨日停牌：释放资金预占（HALTED_RELEASE_PREPAID）

        Args:
            symbol: 持仓股票代码

        Returns:
            HaltStatus 决策结果
        """
        info = self._halt_map.get(symbol)
        if info is None or not info.is_halted:
            return HaltStatus.NORMAL

        if info.is_cross_day:
            return HaltStatus.HALTED_RELEASE_PREPAID
        # 盘中临停：持仓保留不动
        return HaltStatus.HALTED_KEEP_POSITION

    # ── 查询 ──

    def is_halted(self, symbol: str) -> bool:
        """是否停牌。"""
        info = self._halt_map.get(symbol)
        return info is not None and info.is_halted

    def get_halt_info(self, symbol: str) -> HaltInfo | None:
        """获取停牌信息。"""
        return self._halt_map.get(symbol)

    def halted_symbols(self) -> list[str]:
        """所有停牌中的 symbol 列表。"""
        return [s for s, i in self._halt_map.items() if i.is_halted]

    def cross_day_halted_symbols(self) -> list[str]:
        """所有跨日停牌的 symbol 列表。"""
        return [s for s, i in self._halt_map.items() if i.is_halted and i.is_cross_day]


@dataclass(frozen=True)
class HaltAction:
    """停牌处理动作（不可变，用于审计/日志）。

    Attributes:
        symbol: 股票代码
        status: 决策状态
        reason: 决策理由
        remove_from_target: 是否从目标移除
        release_prepaid: 是否释放资金预占
    """

    symbol: str
    status: HaltStatus
    reason: str
    remove_from_target: bool
    release_prepaid: bool
