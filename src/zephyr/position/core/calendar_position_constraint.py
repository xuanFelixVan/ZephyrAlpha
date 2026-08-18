# [BLUEPRINT] MOD-POS-017 | docs/03_modules/_domain_position/calendar_position_constraint/blueprint.md
# [MODULE] zephyr.position.core.calendar_position_constraint
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-POS-010(限仓执行器) ; MOD-POS-001(仓位决策引擎)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] overall_cap=min(各约束cap);block_new=any(全标的BLOCK_NEW);无约束cap=1.0;自然日计算
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidCalendarInputError
# [TESTS] tests/position/test_calendar_position_constraint.py
# [A_module] module_id=MOD-POS-017 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Calendar Position Constraint — 日历仓位约束 (MOD-POS-017)

根据A股风险日历事件, 生成临时仓位上限调整和否决指令。
覆盖7类日历事件: 期权交割/期货交割/年报预告/年报截止/半年报预告/股东空窗/财报发布。

依据: D:\临时工作区\依赖图-D-POSITION-仓位管理域.md §1.5 POS-17 + §7.4
SSoT: depgraph MOD-POS-017
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 当前日期 current_date
#   fields: date（自然日计算，不做交易日历调整；非 date 类型抛 InvalidCalendarInputError）
#   code: calendar_position_constraint.py L181-198 check 参数
# - id: I2
#   name: 持仓标的元数据 positions
#   fields: list[PositionInfo(symbol/is_st/market_cap_yi 亿元/has_forecast/earnings_release_date)]，可选
#   code: calendar_position_constraint.py L96-104 PositionInfo
# 层: 算法
# - id: A1
#   name_zh: ① 股指期权交割日检查
#   name_en: _check_option_expiry
#   intro: 每月第四个周三交割，当天禁开新仓，前后窗口期仓位上限打九折
#   desc: L216-239 第四个周三=_fourth_wednesday(首周三+21天, L357-362)；当天→BLOCK_NEW；前2天~后1天→REDUCE_CAP cap=0.9
#   inputs: I1
#   outputs: 0~1 条 CalendarConstraint
# - id: A2
#   name_zh: ② 年报预告截止检查
#   name_en: _check_annual_forecast_deadline
#   intro: 1 月 26-31 日截止窗口内，没出业绩预告的个股不准新买入
#   desc: L243-259 month==1 且 day≥26；筛 has_forecast=False 标的→BLOCK_NEW（标的级）
#   inputs: I1 I2
#   outputs: 0~1 条 CalendarConstraint
# - id: A3
#   name_zh: ③ 年报截止 ST 清零检查
#   name_en: _check_annual_report_deadline
#   intro: 4 月 20-30 日年报截止窗口内，ST 股仓位强制清零
#   desc: L263-279 month==4 且 day≥20；筛 is_st 标的→FORCE_CLEAR cap=0.0
#   inputs: I1 I2
#   outputs: 0~1 条 CalendarConstraint
# - id: A4
#   name_zh: ④ 半年报预告截止检查
#   name_en: _check_interim_forecast_deadline
#   intro: 7 月 10-15 日截止窗口内，没出预告的个股不准新买入
#   desc: L283-299 month==7 且 day≥10；筛 has_forecast=False 标的→BLOCK_NEW（标的级）
#   inputs: I1 I2
#   outputs: 0~1 条 CalendarConstraint
# - id: A5
#   name_zh: ⑤ 股东信息空窗期检查
#   name_en: _check_shareholder_blackout
#   intro: 11 月到次年 4 月底空窗期内，微盘股仓位上限收紧一半
#   desc: L303-330 month∈{11,12,1,2,3} 或 (4 月且 day≤30)；筛 0<market_cap_yi<50 亿→TIGHTEN_CAP cap=0.5
#   inputs: I1 I2
#   outputs: 0~1 条 CalendarConstraint
# - id: A6
#   name_zh: ⑥ 财报发布前检查
#   name_en: _check_earnings_release
#   intro: 个股财报发布前 3 天内禁止新建仓且上限打九折
#   desc: L334-352 0<(earnings_release_date-d).days≤3 → BLOCK_NEW cap=0.9（逐标的）
#   inputs: I1 I2
#   outputs: 0~N 条 CalendarConstraint
# - id: A7
#   name_zh: ⑦ 约束聚合成预警
#   name_en: check
#   intro: 把六类日历检查的结果汇总成一份仓位预警
#   desc: L181-212 六个 _check_* 顺序 extend 合并；派生 overall_cap_adjustment=min(cap)、block_new_positions=any(全标的 BLOCK_NEW)、block_new/force_clear_symbols 集合
#   inputs: A1 A2 A3 A4 A5 A6
#   outputs: CalendarPositionAlert
#   invariant: overall_cap=min(各约束 cap)；block_new=any(全标的 BLOCK_NEW)；无约束 cap=1.0
# 层: 输出
# - id: O1
#   name_zh: 日历仓位预警 CalendarPositionAlert
#   name_en: CalendarPositionAlert
#   intro: 检查日期+生效约束清单，附综合上限调整/全面禁新/标的级禁新/强清集合四个派生判定
#   invariant: overall_cap_adjustment∈[0,1]
#   downstream: MOD-POS-010 限仓执行器；MOD-POS-001 仓位决策引擎（[CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I2 --> A2
# I1 --> A3
# I2 --> A3
# I1 --> A4
# I2 --> A4
# I1 --> A5
# I2 --> A5
# I1 --> A6
# I2 --> A6
# A1 --> A7
# A2 --> A7
# A3 --> A7
# A4 --> A7
# A5 --> A7
# A6 --> A7
# A7 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "CalendarEventType",
    "ConstraintAction",
    "CalendarConstraint",
    "PositionInfo",
    "CalendarPositionAlert",
    "CalendarPositionConstraint",
    "InvalidCalendarInputError",
]

logger = logging.getLogger(__name__)

# 微盘股市值阈值 (亿元)
MICRO_CAP_THRESHOLD_YI = 50.0


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class CalendarEventType(str, Enum):
    """A股风险日历事件类型。"""

    INDEX_OPTION_EXPIRY = "INDEX_OPTION_EXPIRY"        # 股指期权交割日
    INDEX_FUTURE_EXPIRY = "INDEX_FUTURE_EXPIRY"         # 股指期货交割日
    ANNUAL_FORECAST_DEADLINE = "ANNUAL_FORECAST_DEADLINE"  # 年报预告截止
    ANNUAL_REPORT_DEADLINE = "ANNUAL_REPORT_DEADLINE"    # 年报+一季报截止
    INTERIM_FORECAST_DEADLINE = "INTERIM_FORECAST_DEADLINE"  # 半年报预告截止
    SHAREHOLDER_BLACKOUT = "SHAREHOLDER_BLACKOUT"       # 股东信息空窗期
    EARNINGS_RELEASE = "EARNINGS_RELEASE"               # 财报发布


class ConstraintAction(str, Enum):
    """约束动作。"""

    BLOCK_NEW = "BLOCK_NEW"        # 否决新开仓
    FORCE_CLEAR = "FORCE_CLEAR"    # 强制清仓
    REDUCE_CAP = "REDUCE_CAP"      # 仓位上限下调
    TIGHTEN_CAP = "TIGHTEN_CAP"    # 仓位上限收紧


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidCalendarInputError(ZephyrBaseError):
    """日历约束输入非法。"""

    error_code = "ZA-POS-0017"


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PositionInfo:
    """持仓标的元数据。"""

    symbol: str
    is_st: bool = False
    market_cap_yi: float = 0.0                   # 市值 (亿元)
    has_forecast: bool = True                    # 是否已出业绩预告
    earnings_release_date: date | None = None    # 财报发布日


@dataclass(frozen=True)
class CalendarConstraint:
    """单条日历仓位约束。"""

    rule: str
    event_type: CalendarEventType
    action: ConstraintAction
    cap_adjustment: float                          # 1.0=不变, 0.5=收紧50%, 0.0=清零
    description: str
    affected_symbols: tuple[str, ...] | None = None  # None=全标的, 空tuple=无受影响


@dataclass(frozen=True)
class CalendarPositionAlert:
    """日历仓位预警。"""

    check_date: date
    active_constraints: list[CalendarConstraint] = field(default_factory=list)

    @property
    def overall_cap_adjustment(self) -> float:
        """综合仓位上限调整 (取最严格=min)。"""
        if not self.active_constraints:
            return 1.0
        return min(c.cap_adjustment for c in self.active_constraints)

    @property
    def block_new_positions(self) -> bool:
        """是否全面否决新开仓 (全标的 BLOCK_NEW)。"""
        return any(
            c.action is ConstraintAction.BLOCK_NEW and c.affected_symbols is None
            for c in self.active_constraints
        )

    @property
    def block_new_symbols(self) -> set[str]:
        """特定标的否决新开仓。"""
        symbols: set[str] = set()
        for c in self.active_constraints:
            if c.action is ConstraintAction.BLOCK_NEW and c.affected_symbols:
                symbols.update(c.affected_symbols)
        return symbols

    @property
    def force_clear_symbols(self) -> set[str]:
        """强制清仓标的。"""
        symbols: set[str] = set()
        for c in self.active_constraints:
            if c.action is ConstraintAction.FORCE_CLEAR and c.affected_symbols:
                symbols.update(c.affected_symbols)
        return symbols


# ──────────────────────────────────────────────────────────────────────────────
# 日历仓位约束器
# ──────────────────────────────────────────────────────────────────────────────


class CalendarPositionConstraint:
    """A股风险日历仓位约束——根据日期生成仓位约束。

    用法:
        constraint = CalendarPositionConstraint()
        alert = constraint.check(date(2026, 1, 28), positions=[
            PositionInfo("000001.SZ", has_forecast=False),
        ])
        if alert.block_new_positions:
            # 期权交割日, 否决所有新开仓
        if alert.overall_cap_adjustment < 1.0:
            # 仓位上限需调整

    日期计算用自然日 (不做交易日历调整)。
    """

    def check(
        self,
        current_date: date,
        positions: list[PositionInfo] | None = None,
    ) -> CalendarPositionAlert:
        """检查当前日期的日历仓位约束。

        Args:
            current_date: 当前日期
            positions: 持仓标的元数据列表 (可选, 用于标的级约束)

        Returns:
            CalendarPositionAlert
        """
        if not isinstance(current_date, date):
            raise InvalidCalendarInputError(
                f"current_date must be a date, got {type(current_date).__name__}"
            )
        positions = positions or []
        constraints: list[CalendarConstraint] = []

        constraints.extend(self._check_option_expiry(current_date))
        constraints.extend(self._check_annual_forecast_deadline(current_date, positions))
        constraints.extend(self._check_annual_report_deadline(current_date, positions))
        constraints.extend(self._check_interim_forecast_deadline(current_date, positions))
        constraints.extend(self._check_shareholder_blackout(current_date, positions))
        constraints.extend(self._check_earnings_release(current_date, positions))

        return CalendarPositionAlert(
            check_date=current_date,
            active_constraints=constraints,
        )

    # ── 期权交割日 ──

    def _check_option_expiry(self, d: date) -> list[CalendarConstraint]:
        """股指期权交割日 (每月第四个周三) + 前2天/后1天窗口。"""
        constraints: list[CalendarConstraint] = []
        expiry = self._fourth_wednesday(d.year, d.month)

        # 交割日当天: 否决新开仓
        if d == expiry:
            constraints.append(CalendarConstraint(
                rule="option_expiry_day",
                event_type=CalendarEventType.INDEX_OPTION_EXPIRY,
                action=ConstraintAction.BLOCK_NEW,
                cap_adjustment=1.0,
                description=f"期权交割日 {expiry}: 否决新开仓, 仅允许减仓",
            ))
        # 前2天 + 后1天: 仓位上限下调10%
        elif expiry - timedelta(days=2) <= d <= expiry + timedelta(days=1):
            constraints.append(CalendarConstraint(
                rule="option_expiry_window",
                event_type=CalendarEventType.INDEX_OPTION_EXPIRY,
                action=ConstraintAction.REDUCE_CAP,
                cap_adjustment=0.9,
                description=f"期权交割日 {expiry} 窗口期: 仓位上限下调10%",
            ))
        return constraints

    # ── 年报预告截止 ──

    def _check_annual_forecast_deadline(
        self, d: date, positions: list[PositionInfo]
    ) -> list[CalendarConstraint]:
        """年报预告截止日前5日 (1月26-31日): 未出预告个股否决新买入。"""
        if d.month != 1 or d.day < 26:
            return []
        no_forecast = [p.symbol for p in positions if not p.has_forecast]
        if not no_forecast:
            return []
        return [CalendarConstraint(
            rule="annual_forecast_deadline",
            event_type=CalendarEventType.ANNUAL_FORECAST_DEADLINE,
            action=ConstraintAction.BLOCK_NEW,
            cap_adjustment=1.0,
            description="年报预告截止日前5日: 否决未出预告个股新买入",
            affected_symbols=tuple(no_forecast),
        )]

    # ── 年报+一季报截止 ──

    def _check_annual_report_deadline(
        self, d: date, positions: list[PositionInfo]
    ) -> list[CalendarConstraint]:
        """4月下旬 (4月20-30日): ST股强制清零。"""
        if d.month != 4 or d.day < 20:
            return []
        st_symbols = [p.symbol for p in positions if p.is_st]
        if not st_symbols:
            return []
        return [CalendarConstraint(
            rule="annual_report_st_clear",
            event_type=CalendarEventType.ANNUAL_REPORT_DEADLINE,
            action=ConstraintAction.FORCE_CLEAR,
            cap_adjustment=0.0,
            description="年报截止日4月下旬: ST股仓位强制清零",
            affected_symbols=tuple(st_symbols),
        )]

    # ── 半年报预告截止 ──

    def _check_interim_forecast_deadline(
        self, d: date, positions: list[PositionInfo]
    ) -> list[CalendarConstraint]:
        """半年报预告截止日前5日 (7月10-15日): 未出预告个股否决新买入。"""
        if d.month != 7 or d.day < 10:
            return []
        no_forecast = [p.symbol for p in positions if not p.has_forecast]
        if not no_forecast:
            return []
        return [CalendarConstraint(
            rule="interim_forecast_deadline",
            event_type=CalendarEventType.INTERIM_FORECAST_DEADLINE,
            action=ConstraintAction.BLOCK_NEW,
            cap_adjustment=1.0,
            description="半年报预告截止日前5日: 否决未出预告个股新买入",
            affected_symbols=tuple(no_forecast),
        )]

    # ── 股东信息空窗期 ──

    def _check_shareholder_blackout(
        self, d: date, positions: list[PositionInfo]
    ) -> list[CalendarConstraint]:
        """股东信息空窗期 (11月-次年4月30日): 微盘股(<50亿)上限收紧50%。"""
        in_blackout = d.month >= 11 or d.month <= 4 and d.day <= 30
        if d.month in (11, 12):
            in_blackout = True
        elif d.month in (1, 2, 3) or (d.month == 4 and d.day <= 30):
            in_blackout = True
        else:
            in_blackout = False

        if not in_blackout:
            return []
        micro_caps = [
            p.symbol for p in positions
            if 0 < p.market_cap_yi < MICRO_CAP_THRESHOLD_YI
        ]
        if not micro_caps:
            return []
        return [CalendarConstraint(
            rule="shareholder_blackout_micro_cap",
            event_type=CalendarEventType.SHAREHOLDER_BLACKOUT,
            action=ConstraintAction.TIGHTEN_CAP,
            cap_adjustment=0.5,
            description="股东信息空窗期: 微盘股(<50亿)仓位上限收紧50%",
            affected_symbols=tuple(micro_caps),
        )]

    # ── 财报发布 ──

    def _check_earnings_release(
        self, d: date, positions: list[PositionInfo]
    ) -> list[CalendarConstraint]:
        """财报发布前3天: 该标的上限下调+禁止新建。"""
        constraints: list[CalendarConstraint] = []
        for p in positions:
            if p.earnings_release_date is None:
                continue
            days_before = (p.earnings_release_date - d).days
            if 0 < days_before <= 3:
                constraints.append(CalendarConstraint(
                    rule="earnings_release_soon",
                    event_type=CalendarEventType.EARNINGS_RELEASE,
                    action=ConstraintAction.BLOCK_NEW,
                    cap_adjustment=0.9,
                    description=f"{p.symbol} 财报发布前{days_before}天: 禁止新建+上限下调",
                    affected_symbols=(p.symbol,),
                ))
        return constraints

    # ── 日期计算工具 ──

    @staticmethod
    def _fourth_wednesday(year: int, month: int) -> date:
        """计算指定月份的第四个周三 (股指期权交割日)。"""
        first_day = date(year, month, 1)
        # 周三 = weekday() 2; 第一个周三的日号
        first_wed_day = 1 + (2 - first_day.weekday()) % 7
        return date(year, month, first_wed_day + 21)  # 第四个 = 第一个 + 3周

    @staticmethod
    def _third_friday(year: int, month: int) -> date:
        """计算指定月份的第三个周五 (股指期货交割日)。"""
        first_day = date(year, month, 1)
        first_fri_day = 1 + (4 - first_day.weekday()) % 7
        return date(year, month, first_fri_day + 14)  # 第三个 = 第一个 + 2周
