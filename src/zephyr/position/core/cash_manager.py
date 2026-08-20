# [BLUEPRINT] MOD-POS-006 | docs/03_modules/_domain_position/cash_manager/blueprint.md
# [MODULE] zephyr.position.core.cash_manager
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-POS-001(仓位决策,现金约束反馈) ; D-EX-CORE(资金流水)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] available_cash=total_cash-pending_settlement;pending_settlement≥0且settle后归零;max_investable≥0;total_cash=Σ流水
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidCashFlowError
# [TESTS] tests/position/test_cash_manager.py
# [A_module] module_id=MOD-POS-006 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Cash Manager — 资金管理器 (MOD-POS-006)

管理资金流水与结算状态, A股T+1约束下计算可用资金头寸, 维护最低/机会/节假日储备,
产出现金约束反馈 POS-01。

T+1 结算 (D-POSITION §1.1 POS-06):
    - 买入: 当日扣减可用 (立即生效)
    - 卖出: 当日进 pending_settlement, 次交易日 settle() 后可用

储备金体系:
    - 最低储备金 (绝对金额)
    - 机会储备 (opportunity_reserve_ratio × available)
    - 节假日储备 (holiday_reserve_ratio × available, holiday_mode 时生效)

属A类基础设施(流水记账+T+1结算+储备计算, 逻辑明确), 储备比例为C类可调参数。
依据: D:\临时工作区\依赖图-D-POSITION-仓位管理域.md §1.1 POS-06
SSoT: depgraph MOD-POS-006
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 资金流水 CashFlow
#   fields: flow_type（DEPOSIT 入金/WITHDRAWAL 出金/BUY 买入/SELL 卖出）+ amount>0（符号由类型决定）+ timestamp
#   code: cash_manager.py L115-122 CashFlow；L196 record(flow)
# - id: I2
#   name: 初始资金 initial_cash
#   fields: float≥0（账户起点）
#   code: cash_manager.py L169-176 __init__ 参数
# - id: I3
#   name: 储备金配置 CashReserveConfig
#   fields: min_reserve=100,000 绝对金额 + opportunity_reserve_ratio=0.10 + holiday_reserve_ratio=0.10
#   code: cash_manager.py L91-107 CashReserveConfig
# - id: I4
#   name: 节假日模式标志 in_holiday_mode
#   fields: bool（节前2天+节后1天持币模式，节假日储备仅此时生效）
#   code: cash_manager.py L226 compute_state 参数
# 层: 算法
# - id: A1
#   name_zh: ① 流水记账（T+1 规则）
#   name_en: record
#   intro: 买卖出入金各走各的账：买入当天就扣，卖出当天到账但冻结不可用
#   desc: L196-220 amount≤0 抛错；DEPOSIT total+；WITHDRAWAL/BUY total−（买入立即扣减）；SELL total+ 且 pending_settlement+（T+1 当日不可用）
#   inputs: I1 I2
#   outputs: total_cash / pending_settlement 内部状态
#   invariant: total_cash=Σ流水；pending_settlement≥0
# - id: A2
#   name_zh: ② T+1 结算滚动
#   name_en: settle
#   intro: 次交易日一键释放所有在途卖出资金
#   desc: L222-224 pending_settlement=0.0（昨日卖出今日可用）
#   inputs: A1
#   outputs: pending_settlement 归零
#   invariant: settle 后 pending_settlement=0
# - id: A3
#   name_zh: ③ 可用资金计算
#   name_en: compute_state 可用段
#   intro: 总资金扣掉在途冻结，才是真正能用的钱
#   desc: L238 available=total_cash−pending_settlement
#   inputs: A1 A2
#   outputs: available_cash
#   invariant: available_cash=total_cash−pending_settlement
# - id: A4
#   name_zh: ④ 三类储备计算
#   name_en: compute_state 储备段
#   intro: 最低储备雷打不动，机会储备按比例提，节假日储备只有假日模式才提
#   desc: L240-241 opportunity=available×0.10；holiday=available×0.10（仅 in_holiday_mode，否则 0）；min_reserve 为绝对金额
#   inputs: A3 I3 I4
#   outputs: min/opportunity/holiday 三储备
# - id: A5
#   name_zh: ⑤ 可投资上限合成
#   name_en: compute_state max_investable 段
#   intro: 可用资金减去全部储备就是能拿去开仓的上限，负数兜底为零
#   desc: L242-245 max_investable=max(0, available−min_reserve−opportunity_reserve−holiday_reserve)
#   inputs: A3 A4 I3
#   outputs: max_investable
#   invariant: max_investable≥0
# 层: 输出
# - id: O1
#   name_zh: 资金状态快照 CashState
#   name_en: CashState
#   intro: 总资金/在途结算/可用资金/三类储备/可投资上限/假日模式标记的完整快照
#   invariant: available=total−pending；max_investable≥0
#   downstream: MOD-POS-001 仓位决策消费 max_investable 现金约束反馈；D-EX-CORE 资金流水（[CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A1 --> A3
# A2 --> A3
# A3 --> A4
# I3 --> A4
# I4 --> A4
# A3 --> A5
# A4 --> A5
# I3 --> A5
# A5 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "CashFlowType",
    "CashReserveConfig",
    "CashFlow",
    "CashState",
    "CashManager",
    "InvalidCashFlowError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class CashFlowType(str, Enum):
    """资金流水类型。"""

    DEPOSIT = "DEPOSIT"  # 入金 (+)
    WITHDRAWAL = "WITHDRAWAL"  # 出金 (−)
    BUY = "BUY"  # 买入 (−, 立即扣减)
    SELL = "SELL"  # 卖出 (+, T+1 结算)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidCashFlowError(ZephyrBaseError):
    """资金流水非法(如金额非正、类型非法)。"""

    error_code = "ZA-POS-0006"


# ──────────────────────────────────────────────────────────────────────────────
# 配置 (C 类可调参数)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CashReserveConfig:
    """储备金配置 (设计真源 §1.1 POS-06)。"""

    min_reserve: float = 100_000.0  # 最低储备金 (绝对金额)
    opportunity_reserve_ratio: float = 0.10  # 机会储备 10%
    holiday_reserve_ratio: float = 0.10  # 节假日储备 10% (holiday_mode 时)

    def __post_init__(self) -> None:
        if self.min_reserve < 0:
            raise InvalidCashFlowError(f"min_reserve must be >= 0, got {self.min_reserve}")
        for name, val in (
            ("opportunity_reserve_ratio", self.opportunity_reserve_ratio),
            ("holiday_reserve_ratio", self.holiday_reserve_ratio),
        ):
            if not 0 <= val <= 1:
                raise InvalidCashFlowError(f"{name} must be in [0,1], got {val}")


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CashFlow:
    """单条资金流水。"""

    flow_type: CashFlowType
    amount: float  # 正数 (符号由类型决定)
    timestamp: datetime
    note: str = ""


@dataclass(frozen=True)
class CashState:
    """资金状态快照。"""

    total_cash: float  # 账户总资金 (Σ流水)
    pending_settlement: float  # T+1 未结算 (今日卖出, 次日可用)
    available_cash: float  # 可用资金 = total_cash - pending_settlement
    min_reserve: float  # 最低储备
    opportunity_reserve: float  # 机会储备
    holiday_reserve: float  # 节假日储备
    max_investable: float  # 可投资上限 = max(0, available - 各储备)
    in_holiday_mode: bool
    timestamp: datetime

    @property
    def total_reserve(self) -> float:
        return self.min_reserve + self.opportunity_reserve + self.holiday_reserve


# ──────────────────────────────────────────────────────────────────────────────
# 资金管理器
# ──────────────────────────────────────────────────────────────────────────────


class CashManager:
    """资金管理器——T+1结算约束+三类储备+可投资上限。

    用法:
        mgr = CashManager(initial_cash=1_000_000.0)
        mgr.record(CashFlow(CashFlowType.BUY, 200_000.0, t))   # 买入, 立即扣减
        mgr.record(CashFlow(CashFlowType.SELL, 100_000.0, t))  # 卖出, T+1 未可用
        state = mgr.compute_state(t)
        assert state.available_cash < 800_000  # 卖出未结算
        mgr.settle()                            # 次交易日
        state2 = mgr.compute_state(t2)
        # 卖出资金现已可用
        # POS-01 消费 state.max_investable 约束新开仓

    Args:
        initial_cash: 初始资金
        config: 储备金配置
        clock: 可选时间源 (测试注入)
    """

    def __init__(
        self,
        initial_cash: float,
        config: CashReserveConfig | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if initial_cash < 0:
            raise InvalidCashFlowError(f"initial_cash must be >= 0, got {initial_cash}")
        self._config = config or CashReserveConfig()
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._total_cash = initial_cash
        self._pending_settlement = 0.0

    @property
    def config(self) -> CashReserveConfig:
        return self._config

    @property
    def total_cash(self) -> float:
        return self._total_cash

    @property
    def pending_settlement(self) -> float:
        return self._pending_settlement

    # ── 公开 API ──

    def record(self, flow: CashFlow) -> None:
        """记录一条资金流水。

        Args:
            flow: 资金流水 (amount 必须为正, 符号由类型决定)

        Raises:
            InvalidCashFlowError: 金额非正
        """
        if flow.amount <= 0:
            raise InvalidCashFlowError(f"flow amount must be positive, got {flow.amount}")
        ft = flow.flow_type
        if ft is CashFlowType.DEPOSIT:
            self._total_cash += flow.amount
        elif ft is CashFlowType.WITHDRAWAL:
            self._total_cash -= flow.amount
        elif ft is CashFlowType.BUY:
            # 买入立即扣减可用 (从 total_cash 扣除)
            self._total_cash -= flow.amount
        elif ft is CashFlowType.SELL:
            # 卖出 T+1: total_cash 增加, 但进 pending_settlement 当日不可用
            self._total_cash += flow.amount
            self._pending_settlement += flow.amount
        else:  # pragma: no cover — enum 穷尽
            raise InvalidCashFlowError(f"unknown flow type: {ft}")

    def settle(self) -> None:
        """T+1 结算滚动: 释放所有 pending_settlement (昨日卖出今日可用)。"""
        self._pending_settlement = 0.0

    def compute_state(self, now: datetime | None = None, in_holiday_mode: bool = False) -> CashState:
        """计算当前资金状态 (可用资金+储备+可投资上限)。

        Args:
            now: 时间戳
            in_holiday_mode: 是否节假日持币模式 (节前2天+节后1天)

        Returns:
            CashState
        """
        now = now or self._clock()
        cfg = self._config
        available = self._total_cash - self._pending_settlement

        opportunity_reserve = available * cfg.opportunity_reserve_ratio
        holiday_reserve = available * cfg.holiday_reserve_ratio if in_holiday_mode else 0.0
        max_investable = max(
            0.0,
            available - cfg.min_reserve - opportunity_reserve - holiday_reserve,
        )

        return CashState(
            total_cash=self._total_cash,
            pending_settlement=self._pending_settlement,
            available_cash=available,
            min_reserve=cfg.min_reserve,
            opportunity_reserve=opportunity_reserve,
            holiday_reserve=holiday_reserve,
            max_investable=max_investable,
            in_holiday_mode=in_holiday_mode,
            timestamp=now,
        )

    # ── 便捷方法 ──

    def record_buy(self, amount: float, now: datetime | None = None) -> None:
        """记录买入流水。"""
        self.record(CashFlow(CashFlowType.BUY, amount, now or self._clock()))

    def record_sell(self, amount: float, now: datetime | None = None) -> None:
        """记录卖出流水 (T+1)。"""
        self.record(CashFlow(CashFlowType.SELL, amount, now or self._clock()))

    def record_deposit(self, amount: float, now: datetime | None = None) -> None:
        """记录入金。"""
        self.record(CashFlow(CashFlowType.DEPOSIT, amount, now or self._clock()))

    def record_withdrawal(self, amount: float, now: datetime | None = None) -> None:
        """记录出金。"""
        self.record(CashFlow(CashFlowType.WITHDRAWAL, amount, now or self._clock()))
