# [BLUEPRINT] MOD-RK-10 | docs/03_modules/_domain_risk/ashare_systemic_risk_detector/blueprint.md
# [MODULE] zephyr.risk.core.ashare_systemic_risk_detector
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors; MOD-RK-17(Kill Switch,≥3因子清仓联动)
# [CONSUMERS] MOD-RK-03(Portfolio Risk Monitor,实时告警) ; MOD-RK-17(Kill Switch,LEVEL_3清仓触发)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 5大信号互斥检测;三级警报按触发信号数递进(1停开仓/2降30%/≥3清仓);LEVEL_3必须触发RK-17 Kill Switch;情绪断路器超阈值→强制升级
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidSystemicRiskInputError
# [TESTS] tests/risk/test_ashare_systemic_risk_detector.py
# [A_module] module_id=MOD-RK-10 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


A-Share Systemic Risk Detector — A股系统性风险检测器 (MOD-RK-10)

D-RISK §1.2 L2 Real-Time 盘中监控核心模块。A股系统性风险检测:
    1. 5大信号扫描:
       - 融资盘平仓潮 (MARGIN_CALL_CASCADE): 融资余额急降 + 跌停股数超阈值
       - 量化踩踏 (QUANT_STAMPEDE): 指数快速下跌 + 成交量激增
       - 流动性危机 (LIQUIDITY_CRISIS): 卖盘压力 + 买卖价差扩大
       - 政策转向 (POLICY_SHIFT): 政策信号转向标志
       - 外围冲击 (EXTERNAL_SHOCK): 外围市场大跌
    2. 三级警报 (按触发信号数):
       - 1 信号 → LEVEL_1 停开仓 (position_cap=0% 新开仓)
       - 2 信号 → LEVEL_2 降仓 30% (position_cap=70%)
       - ≥3 信号 → LEVEL_3 清仓 (position_cap=0%, 联动 Kill Switch)
    3. 情绪断路器: 情绪指数超阈值 → 强制升级警报级别
    4. 逃生执行器: LEVEL_3 时产出逃生指令 (清仓+撤单+暂停)

本模块产出 SystemicRiskAlert, LEVEL_3 时联动 RK-17 Kill Switch。
属 A 类基础设施 (信号扫描 + 阈值判定, 逻辑明确), 阈值为 C 类可调参数。
依据: D:\临时工作区\依赖图	-D-RISK-风控域.md §1.2 RK-10, §6 决策记录(A股系统性风险5信号)
SSoT: depgraph MOD-RK-10
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 两融与涨跌停数据 标量参数
#   fields: margin_balance_change 融资余额变化率(负=降) + limit_down_count 跌停股数
#   code: check() L289-290
# - id: I2
#   name: 指数与成交量数据 标量参数
#   fields: index_change_pct 指数涨跌幅 + volume_surge_ratio 成交量激增倍数
#   code: check() L291-292
# - id: I3
#   name: 盘口流动性数据 标量参数
#   fields: sell_pressure 卖盘压力(0~1) + bid_ask_spread 买卖价差
#   code: check() L293-294
# - id: I4
#   name: 政策外围情绪数据 标量参数
#   fields: policy_shift_flag 政策转向标志 + external_market_change 外围涨跌幅 + sentiment_index 情绪指数
#   code: check() L295-297
# - id: I5
#   name: 检测器配置 AshareSystemicRiskConfig
#   fields: 9项信号阈值 + 情绪断路器阈值 + LEVEL_2/3 仓位上限
#   code: AshareSystemicRiskConfig L106
# 层: 算法
# - id: A1
#   name_zh: ① 5大信号互斥扫描
#   name_en: AshareSystemicRiskDetector.check
#   intro: 融资平仓潮/量化踩踏/流动性危机/政策转向/外围冲击五路独立阈值检测
#   desc: 每对输入与配置阈值比较, 双双越限才产 SystemicRiskSignal; 缺输入的信号跳过不报错
#   inputs: I1 I2 I3 I4 I5
#   outputs: 触发信号列表 signals
#   invariant: 5大信号互斥; 未提供输入的信号跳过
# - id: A2
#   name_zh: ② 三级警报递进判定
#   name_en: _determine_level
#   intro: 按触发信号数定警报级别和仓位上限
#   desc: 0信号=NONE, 1=LEVEL_1停开仓, 2=LEVEL_2降仓至70%, ≥3=LEVEL_3清仓+Kill Switch
#   inputs: A1 I5
#   outputs: (alert_level, action, position_cap, kill_switch)
#   invariant: 三级按信号数递进; LEVEL_3必须联动RK-17
# - id: A3
#   name_zh: ③ 情绪断路器强制升级
#   name_en: check 情绪断路器段
#   intro: 情绪指数超阈值直接把警报抬到LEVEL_3
#   desc: sentiment_index >= 0.85 且当前非LEVEL_3 → 强制LEVEL_3 + position_cap=0 + kill_switch=True
#   inputs: A2 I4
#   outputs: 升级后的级别/仓位/动作描述
#   invariant: 情绪断路器超阈值→强制升级
# - id: A4
#   name_zh: ④ 逃生执行器
#   name_en: build_escape_directive
#   intro: LEVEL_3告警转清仓撤单暂停的逃生指令
#   desc: 非LEVEL_3抛InvalidSystemicRiskInputError; 否则产 liquidate_all + cancel_pending_orders + halt_new_orders 指令字典
#   inputs: A3
#   outputs: 逃生指令字典
#   invariant: 仅LEVEL_3可产逃生指令
# 层: 输出
# - id: O1
#   name_zh: 系统性风险综合告警
#   name_en: SystemicRiskAlert
#   intro: 含触发信号/警报级别/仓位上限/是否联动Kill Switch的frozen告警对象
#   invariant: LEVEL_3时 kill_switch_required=True
#   downstream: MOD-RK-03(Portfolio Risk Monitor 实时告警); MOD-RK-17(Kill Switch LEVEL_3清仓触发)
# - id: O2
#   name_zh: 逃生指令
#   name_en: escape directive dict
#   intro: 清仓+撤单+暂停新单的执行指令, 供Kill Switch执行
#   downstream: MOD-RK-17(Kill Switch 执行逃生)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# I5 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
# A3 --> A4
# A4 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "AshareSystemicRiskConfig",
    "SystemicRiskSignalType",
    "SystemicRiskAlertLevel",
    "SystemicRiskSignal",
    "SystemicRiskAlert",
    "AshareSystemicRiskDetector",
    "InvalidSystemicRiskInputError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidSystemicRiskInputError(ZephyrBaseError):
    """A股系统性风险检测器输入数据非法。"""

    error_code = "ZA-RK-0010"


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class SystemicRiskSignalType(Enum):
    """系统性风险信号类型 (5大信号)。"""

    MARGIN_CALL_CASCADE = "margin_call_cascade"  # 1. 融资盘平仓潮
    QUANT_STAMPEDE = "quant_stampede"  # 2. 量化踩踏
    LIQUIDITY_CRISIS = "liquidity_crisis"  # 3. 流动性危机
    POLICY_SHIFT = "policy_shift"  # 4. 政策转向
    EXTERNAL_SHOCK = "external_shock"  # 5. 外围冲击


class SystemicRiskAlertLevel(Enum):
    """系统性风险警报级别 (三级递进)。"""

    NONE = "none"  # 0 信号 → 正常
    LEVEL_1 = "level_1"  # 1 信号 → 停开仓
    LEVEL_2 = "level_2"  # 2 信号 → 降仓 30%
    LEVEL_3 = "level_3"  # ≥3 信号 → 清仓 (Kill Switch 联动)


# ──────────────────────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AshareSystemicRiskConfig:
    """A股系统性风险检测器配置。

    Attributes:
        margin_balance_drop_threshold: 融资余额急降阈值 (负值, 如 -0.03 = -3%)
        limit_down_count_threshold: 跌停股数阈值, 默认 50
        index_drop_threshold: 指数跌幅阈值 (负值), 默认 -0.02 (-2%)
        volume_surge_ratio_threshold: 成交量激增倍数, 默认 2.0
        bid_ask_spread_threshold: 买卖价差扩大阈值, 默认 0.005 (0.5%)
        sell_pressure_threshold: 卖盘压力阈值 (0~1), 默认 0.65
        external_market_drop_threshold: 外围市场跌幅阈值 (负值), 默认 -0.03 (-3%)
        sentiment_breaker_threshold: 情绪断路器阈值 (0~1, 极度恐慌), 默认 0.85
        level_2_position_cap: LEVEL_2 仓位上限, 默认 0.70 (降 30%)
        level_3_position_cap: LEVEL_3 仓位上限, 默认 0.0 (清仓)
    """

    margin_balance_drop_threshold: float = -0.03
    limit_down_count_threshold: int = 50
    index_drop_threshold: float = -0.02
    volume_surge_ratio_threshold: float = 2.0
    bid_ask_spread_threshold: float = 0.005
    sell_pressure_threshold: float = 0.65
    external_market_drop_threshold: float = -0.03
    sentiment_breaker_threshold: float = 0.85
    level_2_position_cap: float = 0.70
    level_3_position_cap: float = 0.0

    def __post_init__(self) -> None:
        if self.margin_balance_drop_threshold >= 0:
            raise InvalidSystemicRiskInputError(
                f"margin_balance_drop_threshold must be negative, got {self.margin_balance_drop_threshold}"
            )
        if self.limit_down_count_threshold < 1:
            raise InvalidSystemicRiskInputError(
                f"limit_down_count_threshold must be >=1, got {self.limit_down_count_threshold}"
            )
        if self.index_drop_threshold >= 0:
            raise InvalidSystemicRiskInputError(
                f"index_drop_threshold must be negative, got {self.index_drop_threshold}"
            )
        if self.volume_surge_ratio_threshold <= 1.0:
            raise InvalidSystemicRiskInputError(
                f"volume_surge_ratio_threshold must be >1.0, got {self.volume_surge_ratio_threshold}"
            )
        if self.bid_ask_spread_threshold <= 0:
            raise InvalidSystemicRiskInputError(
                f"bid_ask_spread_threshold must be >0, got {self.bid_ask_spread_threshold}"
            )
        if not 0 < self.sell_pressure_threshold <= 1:
            raise InvalidSystemicRiskInputError(
                f"sell_pressure_threshold must be in (0,1], got {self.sell_pressure_threshold}"
            )
        if self.external_market_drop_threshold >= 0:
            raise InvalidSystemicRiskInputError(
                f"external_market_drop_threshold must be negative, got {self.external_market_drop_threshold}"
            )
        if not 0 < self.sentiment_breaker_threshold <= 1:
            raise InvalidSystemicRiskInputError(
                f"sentiment_breaker_threshold must be in (0,1], got {self.sentiment_breaker_threshold}"
            )
        if not 0 <= self.level_2_position_cap <= 1:
            raise InvalidSystemicRiskInputError(
                f"level_2_position_cap must be in [0,1], got {self.level_2_position_cap}"
            )
        if not 0 <= self.level_3_position_cap < self.level_2_position_cap:
            raise InvalidSystemicRiskInputError(
                f"level_3_position_cap ({self.level_3_position_cap}) must be "
                f"< level_2_position_cap ({self.level_2_position_cap})"
            )


# ──────────────────────────────────────────────────────────────────────────────
# 信号与告警
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SystemicRiskSignal:
    """单个系统性风险信号。

    Attributes:
        signal_type: 信号类型 (5大信号之一)
        reason: 触发原因 (人类可读)
        trigger_value: 触发值
        threshold: 阈值
        timestamp: 信号时间
    """

    signal_type: SystemicRiskSignalType
    reason: str
    timestamp: datetime
    trigger_value: float | None = None
    threshold: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal_type": self.signal_type.value,
            "reason": self.reason,
            "trigger_value": self.trigger_value,
            "threshold": self.threshold,
        }


@dataclass(frozen=True)
class SystemicRiskAlert:
    """系统性风险综合告警。

    Attributes:
        triggered_signals: 触发的信号列表
        alert_level: 警报级别 (NONE/LEVEL_1/LEVEL_2/LEVEL_3)
        action: 执行动作描述
        position_cap: 仓位上限 (0~1, LEVEL_1=不变/LEVEL_2=0.70/LEVEL_3=0.0)
        kill_switch_required: 是否需要联动 Kill Switch
        sentiment_breaker_triggered: 情绪断路器是否触发 (强制升级)
        signal_count: 触发信号数
        timestamp: 告警时间
    """

    triggered_signals: list[SystemicRiskSignal]
    alert_level: SystemicRiskAlertLevel
    action: str
    position_cap: float
    kill_switch_required: bool
    sentiment_breaker_triggered: bool
    signal_count: int
    timestamp: datetime

    @property
    def is_triggered(self) -> bool:
        """是否触发系统性风险。"""
        return self.alert_level is not SystemicRiskAlertLevel.NONE

    @property
    def is_emergency(self) -> bool:
        """是否为 LEVEL_3 (清仓, 须联动 Kill Switch)。"""
        return self.alert_level is SystemicRiskAlertLevel.LEVEL_3

    def to_dict(self) -> dict[str, Any]:
        return {
            "triggered_signals": [s.to_dict() for s in self.triggered_signals],
            "alert_level": self.alert_level.value,
            "action": self.action,
            "position_cap": self.position_cap,
            "kill_switch_required": self.kill_switch_required,
            "sentiment_breaker_triggered": self.sentiment_breaker_triggered,
            "signal_count": self.signal_count,
            "is_triggered": self.is_triggered,
            "is_emergency": self.is_emergency,
        }


# ──────────────────────────────────────────────────────────────────────────────
# A股系统性风险检测器
# ──────────────────────────────────────────────────────────────────────────────


class AshareSystemicRiskDetector:
    """A股系统性风险检测器——5信号扫描 + 三级警报 + 情绪断路器 + 逃生执行器。

    用法:
        detector = AshareSystemicRiskDetector()
        alert = detector.check(
            margin_balance_change=-0.05,   # 融资余额降 5%
            limit_down_count=80,           # 80 只跌停
            index_change_pct=-0.03,        # 指数跌 3%
            volume_surge_ratio=2.5,        # 成交量激增 2.5 倍
            external_market_change=-0.04,  # 外围跌 4%
        )
        # alert.alert_level = LEVEL_3 (5 信号全触发) → 清仓 + Kill Switch
    """

    def __init__(self, config: AshareSystemicRiskConfig | None = None) -> None:
        self._config = config or AshareSystemicRiskConfig()

    @property
    def config(self) -> AshareSystemicRiskConfig:
        return self._config

    # ── 公开 API: 综合检测 ──

    def check(
        self,
        *,
        margin_balance_change: float | None = None,
        limit_down_count: int | None = None,
        index_change_pct: float | None = None,
        volume_surge_ratio: float | None = None,
        bid_ask_spread: float | None = None,
        sell_pressure: float | None = None,
        policy_shift_flag: bool | None = None,
        external_market_change: float | None = None,
        sentiment_index: float | None = None,
        now: datetime | None = None,
    ) -> SystemicRiskAlert:
        """扫描5大系统性风险信号 + 三级警报判定。

        每种信号独立检测, 未提供输入的信号跳过 (不报错)。
        警报级别按触发信号数: 0=NONE, 1=LEVEL_1, 2=LEVEL_2, ≥3=LEVEL_3。
        情绪断路器超阈值 → 强制升级至 LEVEL_3。

        Args:
            margin_balance_change: 融资余额变化率 (负=下降)
            limit_down_count: 跌停股数
            index_change_pct: 指数涨跌幅 (负=跌)
            volume_surge_ratio: 成交量激增倍数 (1.0=正常)
            bid_ask_spread: 买卖价差 (0~1)
            sell_pressure: 卖盘压力 (0~1, 0.5=均衡)
            policy_shift_flag: 政策转向标志 (True=转向)
            external_market_change: 外围市场涨跌幅 (负=跌)
            sentiment_index: 情绪指数 (0~1, >threshold=极度恐慌)
            now: 时间戳

        Returns:
            SystemicRiskAlert (含触发信号 + 警报级别 + 仓位上限)
        """
        now = now or datetime.now(timezone.utc)
        cfg = self._config
        signals: list[SystemicRiskSignal] = []

        # 1. 融资盘平仓潮: 融资余额急降 + 跌停股数超阈值 (两者均触发才算)
        if margin_balance_change is not None and limit_down_count is not None:
            sig = self._check_margin_call_cascade(margin_balance_change, limit_down_count, cfg, now)
            if sig is not None:
                signals.append(sig)

        # 2. 量化踩踏: 指数快速下跌 + 成交量激增 (两者均触发才算)
        if index_change_pct is not None and volume_surge_ratio is not None:
            sig = self._check_quant_stampede(index_change_pct, volume_surge_ratio, cfg, now)
            if sig is not None:
                signals.append(sig)

        # 3. 流动性危机: 卖盘压力 + 买卖价差扩大 (两者均触发才算)
        if sell_pressure is not None and bid_ask_spread is not None:
            sig = self._check_liquidity_crisis(sell_pressure, bid_ask_spread, cfg, now)
            if sig is not None:
                signals.append(sig)

        # 4. 政策转向: 政策信号转向标志
        if policy_shift_flag is True:
            signals.append(self._build_policy_shift(now))

        # 5. 外围冲击: 外围市场大跌
        if external_market_change is not None:
            sig = self._check_external_shock(external_market_change, cfg, now)
            if sig is not None:
                signals.append(sig)

        # 警报级别判定 (按信号数)
        signal_count = len(signals)
        alert_level, action, position_cap, kill_switch = self._determine_level(signal_count, cfg)

        # 情绪断路器: 超阈值 → 强制升级至 LEVEL_3
        sentiment_triggered = False
        if sentiment_index is not None and sentiment_index >= cfg.sentiment_breaker_threshold:
            if alert_level is not SystemicRiskAlertLevel.LEVEL_3:
                alert_level = SystemicRiskAlertLevel.LEVEL_3
                action = (
                    f"情绪断路器触发 (sentiment={sentiment_index:.2f} >= "
                    f"{cfg.sentiment_breaker_threshold:.2f}), 强制升级至 LEVEL_3: "
                    f"清仓 + 撤单 + 暂停 + Kill Switch"
                )
                position_cap = cfg.level_3_position_cap
                kill_switch = True
                sentiment_triggered = True

        if alert_level is not SystemicRiskAlertLevel.NONE:
            logger.warning(
                "Systemic risk detected: level=%s signals=%d kill_switch=%s sentiment_breaker=%s",
                alert_level.value,
                signal_count,
                kill_switch,
                sentiment_triggered,
            )

        return SystemicRiskAlert(
            triggered_signals=signals,
            alert_level=alert_level,
            action=action,
            position_cap=position_cap,
            kill_switch_required=kill_switch,
            sentiment_breaker_triggered=sentiment_triggered,
            signal_count=signal_count,
            timestamp=now,
        )

    # ── 公开 API: 逃生执行器 ──

    def build_escape_directive(self, alert: SystemicRiskAlert) -> dict[str, Any]:
        """LEVEL_3 时产出逃生指令 (清仓 + 撤单 + 暂停)。

        供 RK-17 Kill Switch 执行。

        Args:
            alert: 已触发的 SystemicRiskAlert

        Returns:
            逃生指令字典

        Raises:
            InvalidSystemicRiskInputError: 非 LEVEL_3 不产出逃生指令
        """
        if alert.alert_level is not SystemicRiskAlertLevel.LEVEL_3:
            raise InvalidSystemicRiskInputError(f"escape directive only for LEVEL_3, got {alert.alert_level.value}")
        return {
            "directive": "escape",
            "action": "liquidate_all",
            "position_cap": 0.0,
            "cancel_pending_orders": True,
            "halt_new_orders": True,
            "kill_switch_required": True,
            "reason": alert.action,
            "triggered_signals": [s.to_dict() for s in alert.triggered_signals],
            "timestamp": alert.timestamp.isoformat(),
        }

    # ── 内部: 5大信号检测 ──

    @staticmethod
    def _check_margin_call_cascade(
        margin_balance_change: float,
        limit_down_count: int,
        cfg: AshareSystemicRiskConfig,
        now: datetime,
    ) -> SystemicRiskSignal | None:
        """1. 融资盘平仓潮: 融资余额急降 + 跌停股数超阈值。"""
        if limit_down_count < 0:
            raise InvalidSystemicRiskInputError(f"limit_down_count must be >=0, got {limit_down_count}")
        if (
            margin_balance_change <= cfg.margin_balance_drop_threshold
            and limit_down_count >= cfg.limit_down_count_threshold
        ):
            return SystemicRiskSignal(
                signal_type=SystemicRiskSignalType.MARGIN_CALL_CASCADE,
                reason=(
                    f"融资余额 {margin_balance_change:.2%} <= {cfg.margin_balance_drop_threshold:.2%} "
                    f"且跌停股数 {limit_down_count} >= {cfg.limit_down_count_threshold}, "
                    f"疑似融资盘平仓潮"
                ),
                timestamp=now,
                trigger_value=margin_balance_change,
                threshold=cfg.margin_balance_drop_threshold,
            )
        return None

    @staticmethod
    def _check_quant_stampede(
        index_change_pct: float,
        volume_surge_ratio: float,
        cfg: AshareSystemicRiskConfig,
        now: datetime,
    ) -> SystemicRiskSignal | None:
        """2. 量化踩踏: 指数快速下跌 + 成交量激增。"""
        if volume_surge_ratio < 0:
            raise InvalidSystemicRiskInputError(f"volume_surge_ratio must be >=0, got {volume_surge_ratio}")
        if index_change_pct <= cfg.index_drop_threshold and volume_surge_ratio >= cfg.volume_surge_ratio_threshold:
            return SystemicRiskSignal(
                signal_type=SystemicRiskSignalType.QUANT_STAMPEDE,
                reason=(
                    f"指数 {index_change_pct:.2%} <= {cfg.index_drop_threshold:.2%} "
                    f"且成交量激增 {volume_surge_ratio:.1f}x >= {cfg.volume_surge_ratio_threshold:.1f}x, "
                    f"疑似量化踩踏"
                ),
                timestamp=now,
                trigger_value=index_change_pct,
                threshold=cfg.index_drop_threshold,
            )
        return None

    @staticmethod
    def _check_liquidity_crisis(
        sell_pressure: float,
        bid_ask_spread: float,
        cfg: AshareSystemicRiskConfig,
        now: datetime,
    ) -> SystemicRiskSignal | None:
        """3. 流动性危机: 卖盘压力 + 买卖价差扩大。"""
        if not 0 <= sell_pressure <= 1:
            raise InvalidSystemicRiskInputError(f"sell_pressure must be in [0,1], got {sell_pressure}")
        if bid_ask_spread < 0:
            raise InvalidSystemicRiskInputError(f"bid_ask_spread must be >=0, got {bid_ask_spread}")
        if sell_pressure >= cfg.sell_pressure_threshold and bid_ask_spread >= cfg.bid_ask_spread_threshold:
            return SystemicRiskSignal(
                signal_type=SystemicRiskSignalType.LIQUIDITY_CRISIS,
                reason=(
                    f"卖盘压力 {sell_pressure:.2f} >= {cfg.sell_pressure_threshold:.2f} "
                    f"且买卖价差 {bid_ask_spread:.4f} >= {cfg.bid_ask_spread_threshold:.4f}, "
                    f"流动性危机"
                ),
                timestamp=now,
                trigger_value=sell_pressure,
                threshold=cfg.sell_pressure_threshold,
            )
        return None

    @staticmethod
    def _build_policy_shift(now: datetime) -> SystemicRiskSignal:
        """4. 政策转向: 政策信号转向标志。"""
        return SystemicRiskSignal(
            signal_type=SystemicRiskSignalType.POLICY_SHIFT,
            reason="政策信号转向 (监管收紧/货币收紧/行业政策利空)",
            timestamp=now,
        )

    @staticmethod
    def _check_external_shock(
        external_market_change: float,
        cfg: AshareSystemicRiskConfig,
        now: datetime,
    ) -> SystemicRiskSignal | None:
        """5. 外围冲击: 外围市场大跌。"""
        if external_market_change <= cfg.external_market_drop_threshold:
            return SystemicRiskSignal(
                signal_type=SystemicRiskSignalType.EXTERNAL_SHOCK,
                reason=(f"外围市场 {external_market_change:.2%} <= {cfg.external_market_drop_threshold:.2%}, 外围冲击"),
                timestamp=now,
                trigger_value=external_market_change,
                threshold=cfg.external_market_drop_threshold,
            )
        return None

    # ── 内部: 警报级别判定 ──

    @staticmethod
    def _determine_level(
        signal_count: int,
        cfg: AshareSystemicRiskConfig,
    ) -> tuple[SystemicRiskAlertLevel, str, float, bool]:
        """按触发信号数判定警报级别。

        Returns:
            (alert_level, action, position_cap, kill_switch_required)
        """
        if signal_count == 0:
            return (
                SystemicRiskAlertLevel.NONE,
                "无系统性风险信号, 正常交易",
                1.0,  # 无仓位限制
                False,
            )
        if signal_count == 1:
            return (
                SystemicRiskAlertLevel.LEVEL_1,
                "1 个系统性风险信号触发: 停止新开仓, 仅允许减仓",
                1.0,  # 现有仓位不动, 仅限新开仓
                False,
            )
        if signal_count == 2:
            return (
                SystemicRiskAlertLevel.LEVEL_2,
                f"2 个系统性风险信号触发: 仓位上限降至 {cfg.level_2_position_cap:.0%}",
                cfg.level_2_position_cap,
                False,
            )
        # signal_count >= 3
        return (
            SystemicRiskAlertLevel.LEVEL_3,
            f"{signal_count} 个系统性风险信号触发: 清仓 + 撤单 + 暂停 + Kill Switch",
            cfg.level_3_position_cap,
            True,
        )
