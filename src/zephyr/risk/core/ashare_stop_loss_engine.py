# [BLUEPRINT] MOD-RK-09 | docs/03_modules/_domain_risk/ashare_stop_loss_engine/blueprint.md
# [MODULE] zephyr.risk.core.ashare_stop_loss_engine
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors; MOD-RK-04(Stop Loss Engine,执行止损)
# [CONSUMERS] MOD-RK-03(Portfolio Risk Monitor,实时告警) ; MOD-RK-04(Stop Loss Engine,执行)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 6种止损模式互斥检测;亏损限额三级递进(日<周<月);强制停盘天数随级别递增;EMERGENCY级必须触发RK-04执行
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidStopLossInputError
# [TESTS] tests/risk/test_ashare_stop_loss_engine.py
# [A_module] module_id=MOD-RK-09 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


A-Share Stop-Loss Rule Engine — A股止损规则引擎 (MOD-RK-09)

D-RISK §1.2 L2 Real-Time 盘中监控核心模块。A股特色止损规则检测:
    1. 6种A股止损模式:
       - 固定比例-7% (FIXED_PCT): 持仓亏损 >= 7%
       - 关键支撑破位 (SUPPORT_BREAK): 价格跌破关键支撑位
       - 逻辑失效 (LOGIC_INVALIDATION): 买入逻辑不再成立
       - 竞价不及预期 (AUCTION_DISAPPOINT): 集合竞价不及预期
       - 分时破位 (INTRADAY_BREAK): 分时图破位(跌破分时均线/前低)
       - 板块退潮 (SECTOR_EBB): 所属板块退潮
    2. 亏损限额三级 (INV-003):
       - 日亏 -2% → 强制停盘 1 天
       - 周亏 -5% → 强制停盘 2 天
       - 月亏 -10% → 强制停盘 3 天
    3. 强制停盘 + 强制复盘

本模块产出 StopLossSignal / LossLimitAlert, 由 RK-04 Stop Loss Engine 执行实际止损动作。
属 A 类基础设施 (规则检测 + 阈值判定, 逻辑明确), 阈值为 C 类可调参数。
依据: D:\临时工作区\依赖图	-D-RISK-风控域.md §1.2 RK-09, §6 决策记录(亏损限额三级)
SSoT: depgraph MOD-RK-09
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 持仓价格 浮点数对
#   fields: entry_price买入价 + current_price当前价(均须>0否则抛InvalidStopLossInputError)
#   code: check_position() L326-328
# - id: I2
#   name: 技术位参考 浮点数可选
#   fields: support_level关键支撑位/vwap分时均价/prev_low前低(None跳过对应检测, vwap优先于prev_low)
#   code: check_position() L330-332
# - id: I3
#   name: 市场环境信号 可选参数
#   fields: sector_momentum板块动量/logic_valid买入逻辑标志/auction_expected_price+auction_actual_price竞价价格对
#   code: check_position() L333-336
# - id: I4
#   name: 账户三周期盈亏率 浮点数
#   fields: daily_pnl_pct/weekly_pnl_pct/monthly_pnl_pct(负数=亏损)
#   code: check_loss_limit() L424-426
# - id: I5
#   name: 止损阈值配置 AshareStopLossConfig
#   fields: fixed_pct7%/日限2%/周限5%/月限10%/停盘1-2-3天/竞价折扣2%/分时破位1%/板块退潮-2%
#   code: AshareStopLossConfig L117-145
# 层: 特征
# - id: F1
#   name_zh: 持仓亏损率
#   name_en: loss_pct
#   intro: 从买入价到现价亏了多少比例
#   formula: loss_pct=(entry_price−current_price)/entry_price
#   code: ashare_stop_loss_engine.py L511
#   registry: factor_registry: 无FCT条目
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① 六种止损模式检测
#   name_en: check_position
#   intro: 固定比例-7%/支撑破位/逻辑失效/竞价不及预期/分时破位/板块退潮六种模式逐一检测
#   desc: 每种模式独立判定(未提供输入的模式跳过不报错); 触发即产StopLossSignal(WARNING软止损/CRITICAL硬止损); 结果按严重级别降序返回
#   inputs: I1 I2 I3 I5 F1
#   outputs: list[StopLossSignal](按严重级降序)
#   invariant: 6种止损模式互斥检测(各模式独立判定)
# - id: A2
#   name_zh: ② 亏损限额三级检测
#   name_en: check_loss_limit
#   intro: 日亏2%/周亏5%/月亏10%三级递进, 取最高触发级定强制停盘天数
#   desc: loss=|min(pnl,0)|取亏损绝对值; 月≥10%→MONTHLY停3天(EMERGENCY), 周≥5%→WEEKLY停2天, 日≥2%→DAILY停1天; 取最高级别
#   inputs: I4 I5
#   outputs: LossLimitAlert(触发级别+停盘天数)
#   invariant: 亏损限额日<周<月递进; 停盘天数随级别递增
# 层: 输出
# - id: O1
#   name_zh: 止损信号列表
#   name_en: list[StopLossSignal]
#   intro: 单标的触发的止损信号(CRITICAL及以上须RK-04执行止损, EMERGENCY联动Kill Switch)
#   invariant: EMERGENCY级必须触发RK-04执行
#   downstream: Portfolio Risk Monitor MOD-RK-03(实时告警); Stop Loss Engine MOD-RK-04(执行止损)
# - id: O2
#   name_zh: 亏损限额告警
#   name_en: LossLimitAlert
#   intro: 含日/周/月亏损率/触发级别/强制停盘天数的账户级告警(INV-003)
#   downstream: Stop Loss Engine MOD-RK-04(执行); Portfolio Risk Monitor MOD-RK-03
# [/ALGO_FLOW]
#
# 边:
# I1 -.->|断点| F1
# F1 --> A1
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I5 --> A1
# I4 --> A2
# I5 --> A2
# A1 --> O1
# A2 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "AshareStopLossConfig",
    "StopLossTriggerType",
    "StopLossSeverity",
    "StopLossSignal",
    "LossLimitLevel",
    "LossLimitAlert",
    "AshareStopLossRuleEngine",
    "InvalidStopLossInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidStopLossInputError(ZephyrBaseError):
    """A股止损规则引擎输入数据非法 (如价格非正、亏损率符号错误)。"""

    error_code = "ZA-RK-0025"


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class StopLossTriggerType(Enum):
    """A股止损触发类型 (6种模式 + 亏损限额)。"""

    FIXED_PCT = "fixed_pct"                       # 1. 固定比例-7%
    SUPPORT_BREAK = "support_break"               # 2. 关键支撑破位
    LOGIC_INVALIDATION = "logic_invalidation"     # 3. 逻辑失效
    AUCTION_DISAPPOINT = "auction_disappoint"     # 4. 竞价不及预期
    INTRADAY_BREAK = "intraday_break"             # 5. 分时破位
    SECTOR_EBB = "sector_ebb"                     # 6. 板块退潮
    LOSS_LIMIT = "loss_limit"                     # 亏损限额触发 (INV-003)


class StopLossSeverity(Enum):
    """止损严重级别。"""

    NONE = "none"           # 未触发
    WARNING = "warning"     # 建议止损 (软止损)
    CRITICAL = "critical"   # 强制止损 (硬止损)
    EMERGENCY = "emergency"  # 强制停盘 (Kill Switch 联动)


class LossLimitLevel(Enum):
    """亏损限额级别 (三级递进)。"""

    NONE = "none"       # 未触发
    DAILY = "daily"     # 日亏 -2% → 停盘 1 天
    WEEKLY = "weekly"   # 周亏 -5% → 停盘 2 天
    MONTHLY = "monthly"  # 月亏 -10% → 停盘 3 天


# ──────────────────────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AshareStopLossConfig:
    """A股止损规则引擎配置。

    Attributes:
        fixed_pct_threshold: 固定比例止损阈值, 默认 0.07 (-7%)
        daily_loss_limit: 日亏损限额, 默认 0.02 (-2%)
        weekly_loss_limit: 周亏损限额, 默认 0.05 (-5%)
        monthly_loss_limit: 月亏损限额, 默认 0.10 (-10%)
        daily_halt_days: 日亏损触发停盘天数, 默认 1
        weekly_halt_days: 周亏损触发停盘天数, 默认 2
        monthly_halt_days: 月亏损触发停盘天数, 默认 3
        auction_discount_threshold: 竞价不及预期阈值(开盘价低于预期%),
            默认 0.02 (-2%)
        intraday_vwap_break_threshold: 分时破位阈值(跌破分时均线%),
            默认 0.01 (-1%)
        sector_momentum_threshold: 板块退潮动量阈值, 默认 -0.02 (-2%)
    """

    fixed_pct_threshold: float = 0.07
    daily_loss_limit: float = 0.02
    weekly_loss_limit: float = 0.05
    monthly_loss_limit: float = 0.10
    daily_halt_days: int = 1
    weekly_halt_days: int = 2
    monthly_halt_days: int = 3
    auction_discount_threshold: float = 0.02
    intraday_vwap_break_threshold: float = 0.01
    sector_momentum_threshold: float = -0.02

    def __post_init__(self) -> None:
        if not 0 < self.fixed_pct_threshold <= 1:
            raise InvalidStopLossInputError(
                f"fixed_pct_threshold must be in (0,1], got {self.fixed_pct_threshold}"
            )
        if not 0 < self.daily_loss_limit <= 1:
            raise InvalidStopLossInputError(
                f"daily_loss_limit must be in (0,1], got {self.daily_loss_limit}"
            )
        if not 0 < self.weekly_loss_limit <= 1:
            raise InvalidStopLossInputError(
                f"weekly_loss_limit must be in (0,1], got {self.weekly_loss_limit}"
            )
        if not 0 < self.monthly_loss_limit <= 1:
            raise InvalidStopLossInputError(
                f"monthly_loss_limit must be in (0,1], got {self.monthly_loss_limit}"
            )
        # 亏损限额递进约束: 日 < 周 < 月
        if not (self.daily_loss_limit < self.weekly_loss_limit < self.monthly_loss_limit):
            raise InvalidStopLossInputError(
                f"loss limits must be increasing: daily({self.daily_loss_limit}) "
                f"< weekly({self.weekly_loss_limit}) < monthly({self.monthly_loss_limit})"
            )
        if self.daily_halt_days < 1 or self.weekly_halt_days < 1 or self.monthly_halt_days < 1:
            raise InvalidStopLossInputError(
                f"halt_days must be >=1, got daily={self.daily_halt_days} "
                f"weekly={self.weekly_halt_days} monthly={self.monthly_halt_days}"
            )
        # 停盘天数递进约束: 日 <= 周 <= 月
        if not (self.daily_halt_days <= self.weekly_halt_days <= self.monthly_halt_days):
            raise InvalidStopLossInputError(
                f"halt_days must be non-decreasing: daily({self.daily_halt_days}) "
                f"<= weekly({self.weekly_halt_days}) <= monthly({self.monthly_halt_days})"
            )


# ──────────────────────────────────────────────────────────────────────────────
# 结果
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class StopLossSignal:
    """单标的止损信号。

    Attributes:
        symbol: 标的代码
        trigger_type: 触发类型 (6种模式之一)
        severity: 严重级别
        reason: 触发原因 (人类可读)
        suggested_action: 建议动作
        trigger_value: 触发值 (如实际亏损率)
        threshold: 阈值 (如 -7%)
        timestamp: 信号时间
    """

    symbol: str
    trigger_type: StopLossTriggerType
    severity: StopLossSeverity
    reason: str
    suggested_action: str
    timestamp: datetime
    trigger_value: float | None = None
    threshold: float | None = None

    @property
    def is_emergency(self) -> bool:
        """是否为 EMERGENCY 级 (须联动 Kill Switch / 强制停盘)。"""
        return self.severity is StopLossSeverity.EMERGENCY

    @property
    def is_critical(self) -> bool:
        """是否为 CRITICAL 级 (须触发 RK-04 执行止损)。"""
        return self.severity in (StopLossSeverity.CRITICAL, StopLossSeverity.EMERGENCY)

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "trigger_type": self.trigger_type.value,
            "severity": self.severity.value,
            "reason": self.reason,
            "suggested_action": self.suggested_action,
            "trigger_value": self.trigger_value,
            "threshold": self.threshold,
            "is_critical": self.is_critical,
            "is_emergency": self.is_emergency,
        }


@dataclass(frozen=True)
class LossLimitAlert:
    """亏损限额告警 (INV-003)。

    Attributes:
        daily_loss_pct: 日亏损率 (负数, 如 -0.025 = -2.5%)
        weekly_loss_pct: 周亏损率
        monthly_loss_pct: 月亏损率
        triggered_level: 触发的级别 (NONE/DAILY/WEEKLY/MONTHLY, 取最高)
        forced_halt_days: 强制停盘天数
        reason: 触发原因
        timestamp: 告警时间
    """

    daily_loss_pct: float
    weekly_loss_pct: float
    monthly_loss_pct: float
    triggered_level: LossLimitLevel
    forced_halt_days: int
    reason: str
    timestamp: datetime

    @property
    def is_triggered(self) -> bool:
        """是否触发亏损限额。"""
        return self.triggered_level is not LossLimitLevel.NONE

    @property
    def severity(self) -> StopLossSeverity:
        """亏损限额对应的严重级别。"""
        if self.triggered_level is LossLimitLevel.MONTHLY:
            return StopLossSeverity.EMERGENCY
        if self.triggered_level in (LossLimitLevel.DAILY, LossLimitLevel.WEEKLY):
            return StopLossSeverity.CRITICAL
        return StopLossSeverity.NONE

    def to_dict(self) -> dict[str, Any]:
        return {
            "daily_loss_pct": self.daily_loss_pct,
            "weekly_loss_pct": self.weekly_loss_pct,
            "monthly_loss_pct": self.monthly_loss_pct,
            "triggered_level": self.triggered_level.value,
            "forced_halt_days": self.forced_halt_days,
            "reason": self.reason,
            "severity": self.severity.value,
            "is_triggered": self.is_triggered,
        }


# ──────────────────────────────────────────────────────────────────────────────
# A股止损规则引擎
# ──────────────────────────────────────────────────────────────────────────────


class AshareStopLossRuleEngine:
    """A股止损规则引擎——6种止损模式 + 亏损限额三级 + 强制停盘。

    用法 (单标的止损检测):
        engine = AshareStopLossRuleEngine()
        signals = engine.check_position(
            symbol="600519",
            entry_price=1800.0,
            current_price=1650.0,
            support_level=1680.0,
            vwap=1670.0,
            sector_momentum=-0.03,
            logic_valid=False,
        )
        # signals → list[StopLossSignal]

    用法 (亏损限额检测):
        alert = engine.check_loss_limit(
            daily_pnl_pct=-0.025,   # 日亏 2.5%
            weekly_pnl_pct=-0.06,   # 周亏 6%
            monthly_pnl_pct=-0.08,  # 月亏 8%
        )
        # alert.triggered_level = WEEKLY (取最高, 停盘 2 天)
    """

    def __init__(self, config: AshareStopLossConfig | None = None) -> None:
        self._config = config or AshareStopLossConfig()

    @property
    def config(self) -> AshareStopLossConfig:
        return self._config

    # ── 公开 API: 单标的止损检测 ──

    def check_position(
        self,
        symbol: str,
        entry_price: float,
        current_price: float,
        *,
        support_level: float | None = None,
        vwap: float | None = None,
        prev_low: float | None = None,
        sector_momentum: float | None = None,
        logic_valid: bool | None = None,
        auction_expected_price: float | None = None,
        auction_actual_price: float | None = None,
        now: datetime | None = None,
    ) -> list[StopLossSignal]:
        """检测单标的的6种A股止损模式。

        每种模式独立检测, 返回所有触发的信号列表 (可能多个同时触发)。
        未提供输入的模式跳过检测 (不报错)。

        Args:
            symbol: 标的代码
            entry_price: 买入价
            current_price: 当前价
            support_level: 关键支撑位 (None=跳过支撑破位检测)
            vwap: 分时成交量加权均价 (None=跳过分时破位检测)
            prev_low: 前低 (分时破位备选, vwap 优先)
            sector_momentum: 板块动量 (None=跳过板块退潮检测)
            logic_valid: 买入逻辑是否仍成立 (None=跳过逻辑失效检测)
            auction_expected_price: 竞价预期价 (None=跳过竞价检测)
            auction_actual_price: 竞价实际开盘价
            now: 时间戳

        Returns:
            触发的 StopLossSignal 列表 (按严重级别降序)
        """
        if not symbol:
            raise InvalidStopLossInputError("symbol must be non-empty")
        if entry_price <= 0:
            raise InvalidStopLossInputError(
                f"entry_price must be positive, got {entry_price}"
            )
        if current_price <= 0:
            raise InvalidStopLossInputError(
                f"current_price must be positive, got {current_price}"
            )

        now = now or datetime.now(timezone.utc)
        signals: list[StopLossSignal] = []
        cfg = self._config

        # 1. 固定比例-7%
        sig = self._check_fixed_pct(symbol, entry_price, current_price, cfg, now)
        if sig is not None:
            signals.append(sig)

        # 2. 关键支撑破位
        if support_level is not None:
            sig = self._check_support_break(symbol, current_price, support_level, now)
            if sig is not None:
                signals.append(sig)

        # 3. 逻辑失效
        if logic_valid is False:
            signals.append(self._build_logic_invalidation(symbol, now))

        # 4. 竞价不及预期
        if auction_expected_price is not None and auction_actual_price is not None:
            sig = self._check_auction_disappoint(
                symbol, auction_expected_price, auction_actual_price, cfg, now
            )
            if sig is not None:
                signals.append(sig)

        # 5. 分时破位
        ref_price = vwap if vwap is not None else prev_low
        if ref_price is not None:
            sig = self._check_intraday_break(symbol, current_price, ref_price, cfg, now)
            if sig is not None:
                signals.append(sig)

        # 6. 板块退潮
        if sector_momentum is not None:
            sig = self._check_sector_ebb(symbol, sector_momentum, cfg, now)
            if sig is not None:
                signals.append(sig)

        # 按严重级别降序 (EMERGENCY > CRITICAL > WARNING > NONE)
        severity_order = {
            StopLossSeverity.EMERGENCY: 0,
            StopLossSeverity.CRITICAL: 1,
            StopLossSeverity.WARNING: 2,
            StopLossSeverity.NONE: 3,
        }
        signals.sort(key=lambda s: severity_order.get(s.severity, 99))
        return signals

    # ── 公开 API: 亏损限额检测 ──

    def check_loss_limit(
        self,
        daily_pnl_pct: float,
        weekly_pnl_pct: float,
        monthly_pnl_pct: float,
        now: datetime | None = None,
    ) -> LossLimitAlert:
        """检测亏损限额三级 (INV-003)。

        亏损率以负数表示 (如 -0.025 = -2.5%), 正数表示盈利。
        取最高触发级别 (MONTHLY > WEEKLY > DAILY)。

        Args:
            daily_pnl_pct: 日盈亏率 (负=亏损)
            weekly_pnl_pct: 周盈亏率
            monthly_pnl_pct: 月盈亏率

        Returns:
            LossLimitAlert (含触发级别 + 强制停盘天数)
        """
        now = now or datetime.now(timezone.utc)
        cfg = self._config

        # 亏损率取绝对值与限额比较 (输入负数, 限额正数)
        daily_loss = abs(min(daily_pnl_pct, 0.0))
        weekly_loss = abs(min(weekly_pnl_pct, 0.0))
        monthly_loss = abs(min(monthly_pnl_pct, 0.0))

        # 三级递进检测, 取最高级别
        if monthly_loss >= cfg.monthly_loss_limit:
            level = LossLimitLevel.MONTHLY
            halt_days = cfg.monthly_halt_days
            reason = (
                f"月亏损 {monthly_loss:.2%} >= 限额 {cfg.monthly_loss_limit:.2%}, "
                f"强制停盘 {halt_days} 天"
            )
        elif weekly_loss >= cfg.weekly_loss_limit:
            level = LossLimitLevel.WEEKLY
            halt_days = cfg.weekly_halt_days
            reason = (
                f"周亏损 {weekly_loss:.2%} >= 限额 {cfg.weekly_loss_limit:.2%}, "
                f"强制停盘 {halt_days} 天"
            )
        elif daily_loss >= cfg.daily_loss_limit:
            level = LossLimitLevel.DAILY
            halt_days = cfg.daily_halt_days
            reason = (
                f"日亏损 {daily_loss:.2%} >= 限额 {cfg.daily_loss_limit:.2%}, "
                f"强制停盘 {halt_days} 天"
            )
        else:
            level = LossLimitLevel.NONE
            halt_days = 0
            reason = "亏损未达限额"

        alert = LossLimitAlert(
            daily_loss_pct=daily_pnl_pct,
            weekly_loss_pct=weekly_pnl_pct,
            monthly_loss_pct=monthly_pnl_pct,
            triggered_level=level,
            forced_halt_days=halt_days,
            reason=reason,
            timestamp=now,
        )

        if alert.is_triggered:
            logger.warning(
                "Loss limit triggered: level=%s halt_days=%d daily=%.2f%% weekly=%.2f%% monthly=%.2f%%",
                level.value,
                halt_days,
                daily_pnl_pct * 100,
                weekly_pnl_pct * 100,
                monthly_pnl_pct * 100,
            )

        return alert

    # ── 内部: 6种止损模式检测 ──

    @staticmethod
    def _check_fixed_pct(
        symbol: str,
        entry_price: float,
        current_price: float,
        cfg: AshareStopLossConfig,
        now: datetime,
    ) -> StopLossSignal | None:
        """1. 固定比例-7%: 持仓亏损 >= threshold。"""
        loss_pct = (entry_price - current_price) / entry_price
        if loss_pct >= cfg.fixed_pct_threshold:
            return StopLossSignal(
                symbol=symbol,
                trigger_type=StopLossTriggerType.FIXED_PCT,
                severity=StopLossSeverity.CRITICAL,
                reason=f"持仓亏损 {loss_pct:.2%} >= 固定止损阈值 {cfg.fixed_pct_threshold:.2%}",
                suggested_action="立即止损卖出",
                trigger_value=loss_pct,
                threshold=cfg.fixed_pct_threshold,
                timestamp=now,
            )
        return None

    @staticmethod
    def _check_support_break(
        symbol: str,
        current_price: float,
        support_level: float,
        now: datetime,
    ) -> StopLossSignal | None:
        """2. 关键支撑破位: 价格跌破支撑位。"""
        if support_level <= 0:
            raise InvalidStopLossInputError(
                f"support_level must be positive, got {support_level}"
            )
        if current_price < support_level:
            break_pct = (support_level - current_price) / support_level
            return StopLossSignal(
                symbol=symbol,
                trigger_type=StopLossTriggerType.SUPPORT_BREAK,
                severity=StopLossSeverity.CRITICAL,
                reason=f"价格 {current_price} 跌破关键支撑 {support_level} ({break_pct:.2%})",
                suggested_action="止损卖出, 跌破支撑后下行空间打开",
                trigger_value=current_price,
                threshold=support_level,
                timestamp=now,
            )
        return None

    @staticmethod
    def _build_logic_invalidation(symbol: str, now: datetime) -> StopLossSignal:
        """3. 逻辑失效: 买入逻辑不再成立。"""
        return StopLossSignal(
            symbol=symbol,
            trigger_type=StopLossTriggerType.LOGIC_INVALIDATION,
            severity=StopLossSeverity.WARNING,
            reason="买入逻辑不再成立 (催化剂消退/基本面恶化/主题证伪)",
            suggested_action="退出持仓, 逻辑不在则持有无意义",
            timestamp=now,
        )

    @staticmethod
    def _check_auction_disappoint(
        symbol: str,
        expected_price: float,
        actual_price: float,
        cfg: AshareStopLossConfig,
        now: datetime,
    ) -> StopLossSignal | None:
        """4. 竞价不及预期: 开盘价低于预期 >= threshold。"""
        if expected_price <= 0:
            raise InvalidStopLossInputError(
                f"expected_price must be positive, got {expected_price}"
            )
        discount = (expected_price - actual_price) / expected_price
        if discount >= cfg.auction_discount_threshold:
            return StopLossSignal(
                symbol=symbol,
                trigger_type=StopLossTriggerType.AUCTION_DISAPPOINT,
                severity=StopLossSeverity.WARNING,
                reason=(
                    f"竞价开盘 {actual_price} 低于预期 {expected_price} "
                    f"({discount:.2%} >= {cfg.auction_discount_threshold:.2%})"
                ),
                suggested_action="开盘止损, 竞价弱势预示当日承压",
                trigger_value=discount,
                threshold=cfg.auction_discount_threshold,
                timestamp=now,
            )
        return None

    @staticmethod
    def _check_intraday_break(
        symbol: str,
        current_price: float,
        ref_price: float,
        cfg: AshareStopLossConfig,
        now: datetime,
    ) -> StopLossSignal | None:
        """5. 分时破位: 价格跌破分时均线/前低 >= threshold。"""
        if ref_price <= 0:
            raise InvalidStopLossInputError(
                f"ref_price (vwap/prev_low) must be positive, got {ref_price}"
            )
        break_pct = (ref_price - current_price) / ref_price
        if break_pct >= cfg.intraday_vwap_break_threshold:
            return StopLossSignal(
                symbol=symbol,
                trigger_type=StopLossTriggerType.INTRADAY_BREAK,
                severity=StopLossSeverity.WARNING,
                reason=(
                    f"价格 {current_price} 跌破分时参考 {ref_price} ({break_pct:.2%} "
                    f">= {cfg.intraday_vwap_break_threshold:.2%})"
                ),
                suggested_action="减仓, 分时破位预示日内转弱",
                trigger_value=break_pct,
                threshold=cfg.intraday_vwap_break_threshold,
                timestamp=now,
            )
        return None

    @staticmethod
    def _check_sector_ebb(
        symbol: str,
        sector_momentum: float,
        cfg: AshareStopLossConfig,
        now: datetime,
    ) -> StopLossSignal | None:
        """6. 板块退潮: 板块动量 <= threshold (负值)。"""
        if sector_momentum <= cfg.sector_momentum_threshold:
            return StopLossSignal(
                symbol=symbol,
                trigger_type=StopLossTriggerType.SECTOR_EBB,
                severity=StopLossSeverity.WARNING,
                reason=(
                    f"板块动量 {sector_momentum:.2%} <= 退潮阈值 "
                    f"{cfg.sector_momentum_threshold:.2%}"
                ),
                suggested_action="减仓, 板块退潮时个股难独立走强",
                trigger_value=sector_momentum,
                threshold=cfg.sector_momentum_threshold,
                timestamp=now,
            )
        return None
