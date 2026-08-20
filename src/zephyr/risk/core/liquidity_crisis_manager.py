# [BLUEPRINT] MOD-RK-21 | docs/03_modules/_domain_risk/liquidity_crisis_manager/blueprint.md
# [MODULE] zephyr.risk.core.liquidity_crisis_manager
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors; MOD-RK-10(AshareSystemicRiskDetector,危机检测复用)
# [CONSUMERS] 盘中风控循环调用方(35号§3.13盘中实时风控循环同tick); MOD-RK-17(Kill Switch,LEVEL_3逃生指令)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 检测真源唯一(委托MOD-RK-10不重复判定);恢复阈值<触发阈值(hysteresis);LEVEL_1→0恢复须经最短持续时间门控;跌停spread置1.0/涨停置None;纯函数零副作用
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidLiquidityCrisisInputError
# [TESTS] tests/risk/core/test_liquidity_crisis_manager.py
# [A_module] module_id=MOD-RK-21 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Liquidity Crisis Manager — 流动性危机管理器 (MOD-RK-21)

37号设计备忘（37_liquidity_crisis_protocol v1.0.18）的施工落地模块。承载 memo 已定义
但未落码的 6 项算法，与 MOD-RK-10/MOD-RK-08 互补不重复：

    1. §3.1.1 sell_pressure：OBI 反转卖盘压力（盘口卖方主导程度，范围 [0,1]）
    2. §3.1.2 bid_ask_spread：Quoted Spread 买卖价差（(ask-bid)/mid）
    3. §3.5.1 detect_limit_status：A股涨跌停五状态检测（涨跌停时 spread 监控失效）
    4. §3.6 check_recovery：危机恢复判定（hysteresis 半阈值 + 最短持续时间门控）
    5. §3.8 run_intraday_liquidity_check：盘中流动性监控单遍编排
       （涨跌停检测→危机检测(委托MOD-RK-10)→响应→恢复判定）
    6. §3.2a compute_ipo_liquidity_drain：IPO 流动性抽离前瞻预警

设计边界（memo §4.1）：不新建独立检测器——危机检测委托 MOD-RK-10
AshareSystemicRiskDetector.check()，本模块不提供第二套检测阈值，触发阈值一律从
detector.config 读取（消除两处真相源）。本模块无内部轮询/定时器——由调用方
（盘中风控循环，30s tick）逐 tick 驱动，符合事件驱动铁律（trae_060）。

A股 T+1 约束：LEVEL_1/2 响应中"仅平仓"受 T+1 限制——当日买入不可卖，
平仓只能减已持仓（T-1 及更早），新建仓被 halt_new_orders 阻断。

依据: 37_liquidity_crisis_protocol v1.0.18 §3.1-§3.8
SSoT: depgraph MOD-RK-21
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 盘口快照 MarketLiquiditySnapshot
#   fields: last_price最新价 + bid_price/ask_price买一卖一(可None) + bid_volumes/ask_volumes五档量 + limit_up_price/limit_down_price涨跌停价
#   code: MarketLiquiditySnapshot L295
# - id: I2
#   name: 恢复状态 LiquidityRecoveryState
#   fields: in_crisis是否危机中 + level当前级别 + entered_at触发时刻
#   code: LiquidityRecoveryState L325
# - id: I3
#   name: 检测器配置 AshareSystemicRiskConfig
#   fields: sell_pressure_threshold=0.65 + bid_ask_spread_threshold=0.005（触发阈值唯一真源）
#   code: run_intraday_liquidity_check() 从 detector.config 读取 L857
# - id: I4
#   name: 恢复配置 LiquidityCrisisConfig
#   fields: spread_recovery=0.0025半阈值 + sell_pressure_recovery=0.50 + min_hold_minutes={1:10,2:15,3:30}
#   code: LiquidityCrisisConfig L230
# - id: I5
#   name: IPO事件列表 list[IPOEvent] + 市场日均成交额
#   fields: symbol + listing_date上市日 + raise_amount募资额(亿元); market_avg_volume_20d(亿元)
#   code: IPOEvent L374 / compute_ipo_liquidity_drain() L701
# 层: 特征
# - id: F1
#   name_zh: 卖盘压力（OBI反转）
#   name_en: sell_pressure
#   intro: 盘口卖方挂单占比，1=纯卖压，0.5=均衡
#   formula: sell_pressure = ΣVolAsk / (ΣVolBid + ΣVolAsk)（等价 (1-OBI)/2）；无盘口返回0.5中性
#   code: compute_sell_pressure() L441
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F2
#   name_zh: 买卖价差（Quoted Spread）
#   name_en: bid_ask_spread
#   intro: 盘口即时交易成本，零延迟领先于成交价恶化
#   formula: spread = (ask - bid) / mid, mid=(ask+bid)/2；盘口缺失返回None
#   code: compute_bid_ask_spread() L481
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F3
#   name_zh: 涨跌停状态
#   name_en: limit_status
#   intro: 涨跌停时盘口退化为单价位，spread监控失效须特殊处理
#   formula: 涨停=价达limit_up且无卖一; 跌停=价达limit_down且无买一; 距板<0.5%=near
#   code: detect_limit_status() L512
#   registry: factor_registry: 无FCT条目
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① 有效价差解析
#   name_en: resolve_effective_spread
#   intro: 跌停置1.0使AND可满足/涨停置None跳过（37号§3.5算法断裂修复）
#   desc: LIMIT_DOWN→1.0; LIMIT_UP→None(买压主导不触发危机); 其余→原始spread
#   inputs: F2 F3
#   outputs: effective_spread
#   invariant: 跌停时危机检测不被None短路; 涨停永不触发流动性危机
# - id: A2
#   name_zh: ② 危机检测（委托MOD-RK-10）
#   name_en: detector.check
#   intro: 双条件AND（卖压≥0.65且价差≥0.5%）由MOD-RK-10执行，本模块不重复判定
#   desc: alert=detector.check(sell_pressure, bid_ask_spread=effective_spread); 触发阈值从detector.config读
#   inputs: F1 A1 I3
#   outputs: SystemicRiskAlert
#   invariant: 检测真源唯一=MOD-RK-10
# - id: A3
#   name_zh: ③ 危机恢复判定
#   name_en: check_recovery
#   intro: hysteresis半阈值+最短持续时间门控防thrashing
#   desc: elapsed<min_hold→None; L1→0需双半阈值+0信号; L2→1需信号≤1+spread<半阈值×1.2; L3→2需信号≤2+冷却期满
#   inputs: F1 A1 I2 I4
#   outputs: target_level(0/1/2)或None
#   invariant: 恢复阈值<触发阈值（制造稳定缓冲带）; 返回0是有效结果须is not None判定
# - id: A4
#   name_zh: ④ 盘中单遍编排
#   name_en: run_intraday_liquidity_check
#   intro: 涨跌停→检测→响应→恢复四阶段单遍执行（37号§3.8）
#   desc: 由调用方30s tick驱动; 危机时enter_crisis+halt_new_orders; 非危机且危机中→试恢复exit_crisis
#   inputs: I1 I2 I3 I4 A1 A2 A3
#   outputs: LiquidityLoopResult
#   invariant: 危机中不检查恢复（防刚触发就恢复的thrashing）
# - id: A5
#   name_zh: ⑤ IPO流动性抽离预警
#   name_en: compute_ipo_liquidity_drain
#   intro: 前瞻性预警——IPO日历+募资规模上市日前已知（37号§3.2a）
#   desc: drain_ratio=未来5日募资总额/市场日均成交额; 四级→position_cap_adjustment(1.0/0.90/0.75/0.60)
#   inputs: I5
#   outputs: IPOLiquidityDrain
#   invariant: drain_ratio<0.01不调整; 与§3.2 Amihud事后检测正交（事前vs事后）
# 层: 输出
# - id: O1
#   name_zh: 盘中流动性循环结果
#   name_en: LiquidityLoopResult
#   intro: 涨跌停状态+卖压+有效价差+alert+halt_new_orders+position_cap+恢复迁移
#   downstream: 盘中风控循环调用方(消费alert/执行响应); MOD-RK-17(LEVEL_3逃生指令)
# - id: O2
#   name_zh: IPO流动性抽离预警
#   name_en: IPOLiquidityDrain
#   intro: drain_ratio+drain_level+position_cap_adjustment仓位上限调整系数
#   downstream: FirmRiskAggregator(仓位上限节流); 26号事件驱动sleeve(alpha方向联动)
# [/ALGO_FLOW]
#
# 边:
# I1 --> F3
# I1 --> F1
# I1 --> F2
# F2 --> A1
# F3 --> A1
# F1 --> A2
# A1 --> A2
# I3 --> A2
# F1 --> A3
# A1 --> A3
# I2 --> A3
# I4 --> A3
# A1 --> A4
# A2 --> A4
# A3 --> A4
# I5 --> A5
# A4 --> O1
# A5 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import Enum
from typing import Any, Final

from zephyr.risk.core.ashare_systemic_risk_detector import (
    AshareSystemicRiskDetector,
    SystemicRiskAlert,
    SystemicRiskAlertLevel,
)
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "InvalidLiquidityCrisisInputError",
    "IPODrainLevel",
    "LimitStatus",
    "LiquidityCrisisConfig",
    "LiquidityRecoveryState",
    "MarketLiquiditySnapshot",
    "LiquidityLoopResult",
    "IPOEvent",
    "IPOLiquidityDrain",
    "RecoveryCheckInput",
    "compute_sell_pressure",
    "compute_bid_ask_spread",
    "detect_limit_status",
    "resolve_effective_spread",
    "check_recovery",
    "compute_ipo_liquidity_drain",
    "run_intraday_liquidity_check",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidLiquidityCrisisInputError(ZephyrBaseError):
    """流动性危机管理器输入数据非法。"""

    error_code = "ZA-RK-0021"


# ──────────────────────────────────────────────────────────────────────────────
# 枚举与配置
# ──────────────────────────────────────────────────────────────────────────────


class LimitStatus(str, Enum):
    """涨跌停状态（37号 §3.5.1 五状态）。"""

    LIMIT_UP = "limit_up"  # 涨停：价达涨停价且无卖一（买不进）
    LIMIT_DOWN = "limit_down"  # 跌停：价达跌停价且无买一（卖不出）
    NEAR_UP = "near_up"  # 接近涨停：距涨停 <0.5%（即将封板预警）
    NEAR_DOWN = "near_down"  # 接近跌停：距跌停 <0.5%
    NORMAL = "normal"  # 正常


class IPODrainLevel(str, Enum):
    """IPO 流动性抽离分级（37号 §3.2a 四级）。"""

    NEGLIGIBLE = "NEGLIGIBLE"  # 可忽略：drain_ratio < 1%，仓位不变
    MODERATE = "MODERATE"  # 温和：1%~2%，仓位上限 ×0.90
    SEVERE = "SEVERE"  # 严重：2%~3%，仓位上限 ×0.75
    EXTREME = "EXTREME"  # 极端：≥3%，仓位上限 ×0.60


@dataclass(frozen=True)
class LiquidityCrisisConfig:
    """流动性危机恢复配置（37号 §3.6，C 类参数可调）。

    触发阈值不在此定义——唯一真源是 MOD-RK-10 的 AshareSystemicRiskConfig
    （sell_pressure_threshold=0.65 / bid_ask_spread_threshold=0.005），
    本配置只承载恢复侧参数，消除两处真相源。

    Attributes:
        spread_recovery_ratio: spread 恢复阈值相对触发阈值的比例（0.5=半阈值）
        sell_pressure_recovery: 卖压恢复阈值（0.50，触发阈值的 ~77%）
        recovery_band_multiplier: LEVEL_2/3 降级恢复的 spread 放宽倍数（1.2）
        min_hold_minutes: 各级别最短持续时间门控（分钟），防 thrashing
        near_limit_band: 接近涨跌停判定带宽（0.005 = 0.5%）
        ipo_drain_thresholds: IPO 抽离分级阈值（NEGLIGIBLE/MODERATE/SEVERE 上界）
        ipo_cap_adjustments: 各 drain_level 对应仓位上限调整系数
        ipo_horizon_days: IPO 预警前瞻窗口（自然日，memo §3.2a 为 5）
    """

    spread_recovery_ratio: float = 0.5
    sell_pressure_recovery: float = 0.50
    recovery_band_multiplier: float = 1.2
    min_hold_minutes: dict[int, int] = field(default_factory=lambda: {1: 10, 2: 15, 3: 30})
    near_limit_band: float = 0.005
    ipo_drain_thresholds: tuple[float, float, float] = (0.01, 0.02, 0.03)
    ipo_cap_adjustments: tuple[float, float, float, float] = (1.0, 0.90, 0.75, 0.60)
    ipo_horizon_days: int = 5

    def __post_init__(self) -> None:
        if not 0 < self.spread_recovery_ratio < 1:
            raise InvalidLiquidityCrisisInputError(
                f"spread_recovery_ratio must be in (0,1), got {self.spread_recovery_ratio}"
            )
        if not 0 < self.sell_pressure_recovery <= 1:
            raise InvalidLiquidityCrisisInputError(
                f"sell_pressure_recovery must be in (0,1], got {self.sell_pressure_recovery}"
            )
        if self.recovery_band_multiplier < 1.0:
            raise InvalidLiquidityCrisisInputError(
                f"recovery_band_multiplier must be >=1.0, got {self.recovery_band_multiplier}"
            )
        if set(self.min_hold_minutes) != {1, 2, 3} or any(v <= 0 for v in self.min_hold_minutes.values()):
            raise InvalidLiquidityCrisisInputError(
                f"min_hold_minutes must cover levels 1/2/3 with positive minutes, got {self.min_hold_minutes}"
            )
        if not 0 < self.near_limit_band < 0.05:
            raise InvalidLiquidityCrisisInputError(f"near_limit_band must be in (0,0.05), got {self.near_limit_band}")
        if self.ipo_horizon_days < 1:
            raise InvalidLiquidityCrisisInputError(f"ipo_horizon_days must be >=1, got {self.ipo_horizon_days}")


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class MarketLiquiditySnapshot:
    """盘口流动性快照（单标的单 tick，37号 §3.8 编排输入）。

    字段与 miniQMT xtdata.get_full_tick 五档快照对齐
    （src/zephyr/data/implementations/miniqmt_provider.py §_parse_auction_book_tick）。

    Attributes:
        symbol: 标的代码
        last_price: 最新成交价
        bid_price: 买一价（None=无买单，跌停典型场景）
        ask_price: 卖一价（None=无卖单，涨停典型场景）
        bid_volumes: 多档买盘挂单量（如 5 档买一至买五）
        ask_volumes: 多档卖盘挂单量（如 5 档卖一至卖五）
        limit_up_price: 涨停价（当日涨停基准，前收 × (1+涨幅限制)）
        limit_down_price: 跌停价（当日跌停基准）
        timestamp: 快照时间（UTC）
    """

    symbol: str
    last_price: float
    bid_price: float | None
    ask_price: float | None
    bid_volumes: tuple[float, ...]
    ask_volumes: tuple[float, ...]
    limit_up_price: float
    limit_down_price: float
    timestamp: datetime


@dataclass
class LiquidityRecoveryState:
    """危机恢复状态（调用方持有，跨 tick 持久，37号 §3.6/§3.8）。

    非冻结 dataclass——状态对象须可迁移。模块内不持有全局实例，
    由调用方（盘中风控循环）创建并逐 tick 传入，保证纯函数编排。

    Attributes:
        in_crisis: 是否处于危机中
        level: 当前警报级别（0=正常 / 1=LEVEL_1 / 2=LEVEL_2 / 3=LEVEL_3）
        entered_at: 进入当前级别时刻（UTC，None=未在危机中）
    """

    in_crisis: bool = False
    level: int = 0
    entered_at: datetime | None = None

    def enter_crisis(self, level: int, timestamp: datetime) -> None:
        """进入/迁移危机级别（记录迁移时刻，重置持续时间计数）。"""
        if level < 1 or level > 3:
            raise InvalidLiquidityCrisisInputError(f"crisis level must be in {1, 2, 3}, got {level}")
        self.in_crisis = True
        self.level = level
        self.entered_at = timestamp

    def exit_crisis(self, target_level: int, timestamp: datetime) -> None:
        """退出到目标级别（0=正常态清空状态；1/2=降级保留计时锚点）。"""
        if target_level < 0 or target_level >= self.level:
            raise InvalidLiquidityCrisisInputError(f"target_level must be in [0,{self.level}), got {target_level}")
        if target_level == 0:
            self.in_crisis = False
            self.level = 0
            self.entered_at = None
        else:
            # 降级（如 L3→L2）：更新级别并以迁移时刻为新持续时间锚点
            self.level = target_level
            self.entered_at = timestamp

    def elapsed_minutes(self, now: datetime) -> float:
        """距进入当前级别的已过分钟数（未在危机中返回 0）。"""
        if not self.in_crisis or self.entered_at is None:
            return 0.0
        return max(0.0, (now - self.entered_at).total_seconds() / 60.0)


@dataclass(frozen=True)
class IPOEvent:
    """IPO 事件（37号 §3.2a，上市日前已知的前瞻信息）。

    Attributes:
        symbol: 标的代码
        listing_date: 上市日期
        raise_amount: 募资额（亿元）
    """

    symbol: str
    listing_date: date
    raise_amount: float


@dataclass(frozen=True)
class IPOLiquidityDrain:
    """IPO 流动性抽离预警结果（37号 §3.2a）。

    Attributes:
        drain_ratio: 未来 N 日 IPO 募资总额 / 全市场日均成交额
        drain_level: NEGLIGIBLE / MODERATE / SEVERE / EXTREME
        position_cap_adjustment: 仓位上限调整系数（1.0=不变）
        counted_ipos: 计入抽离的 IPO 数
    """

    drain_ratio: float
    drain_level: IPODrainLevel
    position_cap_adjustment: float
    counted_ipos: int


@dataclass(frozen=True)
class LiquidityLoopResult:
    """盘中流动性监控单遍结果（37号 §3.8）。

    Attributes:
        symbol: 标的代码
        limit_status: 涨跌停状态
        sell_pressure: 卖盘压力（OBI 反转）
        raw_spread: 原始买卖价差（None=盘口缺失）
        effective_spread: 有效价差（跌停置 1.0 / 涨停置 None 后）
        alert: MOD-RK-10 系统性风险告警（检测唯一真源产出）
        halt_new_orders: 是否停止新开仓（LEVEL_1+ 响应）
        position_cap: 仓位上限（LEVEL_1=1.0 / LEVEL_2=0.70 / LEVEL_3=0.0）
        recovery_target: 本遍恢复迁移目标级别（None=未发生迁移）
        escape_directive: LEVEL_3 逃生指令字典（非 LEVEL_3 为 None）
        timestamp: 判定时间（UTC）
    """

    symbol: str
    limit_status: LimitStatus
    sell_pressure: float
    raw_spread: float | None
    effective_spread: float | None
    alert: SystemicRiskAlert
    halt_new_orders: bool
    position_cap: float
    recovery_target: int | None
    escape_directive: dict[str, Any] | None
    timestamp: datetime


# ──────────────────────────────────────────────────────────────────────────────
# 纯函数：盘口特征（37号 §3.1.1 / §3.1.2 / §3.5.1）
# ──────────────────────────────────────────────────────────────────────────────


def compute_sell_pressure(
    bid_volumes: list[float] | tuple[float, ...],
    ask_volumes: list[float] | tuple[float, ...],
) -> float:
    """卖盘压力 = 卖方挂单占比（OBI 反转，37号 §3.1.1）。

    sell_pressure = ΣVolAsk / (ΣVolBid + ΣVolAsk)，范围 [0,1]。
    1=纯卖压，0.5=均衡，0=纯买压。与 MOD-RK-10 阈值 0.65 量纲一致
    （卖压≥0.65 = 买盘仅占 35%，Polymarket 2026-06 卖压主导阈值量级）。

    注：memo §3.1.1 行文写作 "1 - OBI"，其数学等价口径为
    (1 - OBI) / 2 = ΣVolAsk / (ΣVolBid + ΣVolAsk)——本实现取后者，
    与 memo 声明的值域 [0,1]、均衡点 0.5 及 0.65 阈值语义自洽。

    Args:
        bid_volumes: 多档买盘挂单量（如 5 档买一至买五）
        ask_volumes: 多档卖盘挂单量（如 5 档卖一至卖五）

    Returns:
        sell_pressure ∈ [0, 1]；无盘口数据返回 0.5（中性值不触发）

    Raises:
        InvalidLiquidityCrisisInputError: 挂单量为负
    """
    total_bid = 0.0
    total_ask = 0.0
    for v in bid_volumes:
        if v < 0:
            raise InvalidLiquidityCrisisInputError(f"bid volume must be >=0, got {v}")
        total_bid += v
    for v in ask_volumes:
        if v < 0:
            raise InvalidLiquidityCrisisInputError(f"ask volume must be >=0, got {v}")
        total_ask += v
    total = total_bid + total_ask
    if total == 0:
        return 0.5  # 无盘口数据，返回中性值不触发
    return total_ask / total


def compute_bid_ask_spread(
    bid_price: float | None,
    ask_price: float | None,
) -> float | None:
    """买卖价差 = (ask - bid) / mid（Quoted Spread，37号 §3.1.2）。

    直接从盘口读取零延迟，适合盘内实时检测；spread 扩大先于成交价恶化
    （领先信号）。与 MOD-RK-10 阈值 0.005（0.5%）量纲一致。

    Args:
        bid_price: 买一价（None=无买单）
        ask_price: 卖一价（None=无卖单）

    Returns:
        spread ∈ [0, +∞)；盘口缺失/非法返回 None（由调用方按 §3.5 规则处理）

    Raises:
        InvalidLiquidityCrisisInputError: ask < bid（交叉盘口，数据异常）
    """
    if bid_price is None or ask_price is None:
        return None
    if bid_price <= 0 or ask_price <= 0:
        return None
    if ask_price < bid_price:
        raise InvalidLiquidityCrisisInputError(f"crossed book: ask {ask_price} < bid {bid_price}")
    mid = (bid_price + ask_price) / 2
    return (ask_price - bid_price) / mid


def detect_limit_status(
    last_price: float,
    limit_up_price: float,
    limit_down_price: float,
    bid_price: float | None,
    ask_price: float | None,
    tolerance: float = 1e-6,
    near_limit_band: float = 0.005,
) -> LimitStatus:
    """涨跌停状态检测（37号 §3.5.1 五状态）。

    判定顺序关键：精确封板（封单消失）先于接近判定——价达涨停但卖一仍在
    （未封死）落入 NEAR_UP 而非 LIMIT_UP。

    Args:
        last_price: 最新成交价
        limit_up_price: 涨停价（当日涨停基准）
        limit_down_price: 跌停价（当日跌停基准）
        bid_price: 买一价（None=无买单）
        ask_price: 卖一价（None=无卖单）
        tolerance: 价格比较容差（浮点精度）
        near_limit_band: 接近判定带宽（0.005=0.5%，LiquidityCrisisConfig 注入）

    Returns:
        LimitStatus 五态之一

    Raises:
        InvalidLiquidityCrisisInputError: 价格非法或涨跌停价倒挂
    """
    if last_price <= 0 or limit_up_price <= 0 or limit_down_price <= 0:
        raise InvalidLiquidityCrisisInputError(
            f"prices must be positive: last={last_price} up={limit_up_price} down={limit_down_price}"
        )
    if limit_up_price <= limit_down_price:
        raise InvalidLiquidityCrisisInputError(f"limit_up {limit_up_price} must be > limit_down {limit_down_price}")

    # 1. 涨停判定：最新价达涨停价 + 卖一缺失（无卖单=买不进）
    if abs(last_price - limit_up_price) < tolerance and ask_price is None:
        return LimitStatus.LIMIT_UP

    # 2. 跌停判定：最新价达跌停价 + 买一缺失（无买单=卖不出）
    if abs(last_price - limit_down_price) < tolerance and bid_price is None:
        return LimitStatus.LIMIT_DOWN

    # 3. 接近涨停：距涨停 <0.5%（即将封板，提前预警）
    if last_price >= limit_up_price * (1 - near_limit_band):
        return LimitStatus.NEAR_UP

    # 4. 接近跌停：距跌停 <0.5%
    if last_price <= limit_down_price * (1 + near_limit_band):
        return LimitStatus.NEAR_DOWN

    return LimitStatus.NORMAL


def resolve_effective_spread(
    limit_status: LimitStatus,
    raw_spread: float | None,
) -> float | None:
    """有效价差解析——涨跌停特殊处理（37号 §3.5 算法断裂修复 + §3.5.1 联动表）。

    - LIMIT_DOWN（跌停）→ 1.0：跌停=平仓通道冻结=流动性危机子类，
      置大值使 MOD-RK-10 双条件 AND（卖压≥0.65 且 spread≥0.5%）可满足；
      若置 None 则检测器跳过检查，信号无法触发（v1.0.2 修复的算法断裂）
    - LIMIT_UP（涨停）→ None：涨停为买压主导非流动性危机，跳过检查
      （§3.5.1 联动表：涨停 spread 置 None；即使置 1.0 也因卖压≈0 不触发，
      置 None 语义更干净且阻断异常数据下的误触发）
    - 其余 → 原始 spread（None 透传=盘口缺失由检测器跳过）

    Args:
        limit_status: 涨跌停状态（detect_limit_status 产出）
        raw_spread: 原始价差（compute_bid_ask_spread 产出，可 None）

    Returns:
        有效价差（None=跳过危机检查）
    """
    if limit_status is LimitStatus.LIMIT_DOWN:
        return 1.0
    if limit_status is LimitStatus.LIMIT_UP:
        return None
    return raw_spread


# ──────────────────────────────────────────────────────────────────────────────
# 危机恢复判定（37号 §3.6）
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class RecoveryCheckInput:
    """危机恢复判定入参（37号 §3.6，参数对象封装）。

    Attributes:
        current_spread: 当前有效买卖价差（已过 §3.5.1 涨跌停检测处理）
        current_sell_pressure: 当前卖压（§3.1.1 OBI 反转）
        trigger_threshold_spread: spread 触发阈值（0.005=0.5%，来自 detector.config）
        recovery_threshold_spread: spread 恢复半阈值（0.0025=0.25%）
        trigger_threshold_pressure: 卖压触发阈值（0.65，来自 detector.config）
        recovery_threshold_pressure: 卖压恢复半阈值（0.50）
        min_hold_minutes: 当前级别最短持续时间（分钟，{1:10,2:15,3:30}[level] 注入）
        elapsed: 距触发已过时间（分钟，recovery_state.elapsed_minutes(now)）
        current_level: 当前警报级别（1/2/3）
        active_signals: 当前活动触发信号数（§3.1 双条件计数：卖压超阈值 +
            spread 超阈值，范围 0-2）
    """

    current_spread: float
    current_sell_pressure: float
    trigger_threshold_spread: float
    recovery_threshold_spread: float
    trigger_threshold_pressure: float
    recovery_threshold_pressure: float
    min_hold_minutes: int
    elapsed: float
    current_level: int
    active_signals: int = 0


def _validate_recovery_input(inp: RecoveryCheckInput) -> None:
    """校验恢复入参（强制 hysteresis 不对称：恢复阈值 < 触发阈值）。"""
    if inp.current_level not in (1, 2, 3):
        raise InvalidLiquidityCrisisInputError(f"current_level must be in (1,2,3), got {inp.current_level}")
    if inp.min_hold_minutes <= 0 or inp.elapsed < 0:
        raise InvalidLiquidityCrisisInputError(
            f"min_hold must be >0 and elapsed >=0, got {inp.min_hold_minutes}/{inp.elapsed}"
        )
    if not 0 < inp.recovery_threshold_spread < inp.trigger_threshold_spread:
        raise InvalidLiquidityCrisisInputError(
            f"recovery spread {inp.recovery_threshold_spread} must be in (0, trigger {inp.trigger_threshold_spread})"
        )
    if not 0 < inp.recovery_threshold_pressure < inp.trigger_threshold_pressure:
        raise InvalidLiquidityCrisisInputError(
            f"recovery pressure {inp.recovery_threshold_pressure} must be in "
            f"(0, trigger {inp.trigger_threshold_pressure})"
        )


def check_recovery(inp: RecoveryCheckInput) -> int | None:
    """危机恢复判定——滞后双阈值（hysteresis）+ 最短持续时间门控（37号 §3.6）。

    触发阈值与恢复阈值不对称（恢复阈值更宽松），避免临界状态反复震荡
    （触发→恢复→再触发的 thrashing）。恢复条件持续满足而非瞬时满足由
    最短持续时间门控保证（LEVEL_1 10min / LEVEL_2 15min / LEVEL_3 30min，
    LEVEL_3 的 30 分钟已覆盖 Kill Switch 冷却期）。

    Args:
        inp: 恢复判定入参（RecoveryCheckInput，阈值真源一律从 detector.config 读取）

    Returns:
        target_level: 恢复后的目标级别（0=正常 / 1=LEVEL_1 / 2=LEVEL_2），
            或 None（不恢复）。
        ⚠️ 返回 0（正常态）是有效恢复结果，调用方须用 `is not None` 判定，
            不可用真值检查（`if recovered:` 在 target_level=0 时为 False，
            会跳过 LEVEL_1→正常的恢复，37号 v1.0.16 已修此 bug）

    Raises:
        InvalidLiquidityCrisisInputError: 参数非法（级别/阈值/时间）
    """
    _validate_recovery_input(inp)

    # 1. 最短持续时间门控（防 thrashing）
    if inp.elapsed < inp.min_hold_minutes:
        return None

    # 2. 半阈值 hysteresis 检查（恢复阈值 < 触发阈值，制造稳定缓冲带）
    spread_ok = inp.current_spread < inp.recovery_threshold_spread
    pressure_ok = inp.current_sell_pressure < inp.recovery_threshold_pressure

    # 3. 分级恢复条件（各级别恢复目标递进，信号数要求递减宽松）
    if inp.current_level == 1 and spread_ok and pressure_ok and inp.active_signals == 0:
        # LEVEL_1 → 正常：所有信号归零 + spread/pressure 降至半阈值
        return 0

    if inp.current_level == 2 and inp.active_signals <= 1 and inp.current_spread < inp.recovery_threshold_spread * 1.2:
        # LEVEL_2 → LEVEL_1：信号降至≤1 + spread < 半阈值×1.2（略宽于正常恢复）
        return 1

    if inp.current_level == 3 and inp.active_signals <= 2 and inp.current_spread < inp.recovery_threshold_spread * 1.2:
        # LEVEL_3 → LEVEL_2：Kill Switch 冷却期满（min_hold=30 覆盖）+ 信号降至≤2
        return 2

    return None


# ──────────────────────────────────────────────────────────────────────────────
# IPO 流动性抽离预警（37号 §3.2a）
# ──────────────────────────────────────────────────────────────────────────────


def compute_ipo_liquidity_drain(
    upcoming_ipos: list[IPOEvent],
    market_avg_volume_20d: float,
    today: date | None = None,
    config: LiquidityCrisisConfig | None = None,
) -> IPOLiquidityDrain:
    """IPO 流动性抽离前瞻预警（37号 §3.2a）。

    与 §3.2 Amihud/成交量萎缩的事后检测正交——本节是事前预警（IPO 上市日前
    已知募资规模），提前调整仓位上限保留现金（如 2026-07-27 长鑫科技 688825
    科创板上市募资 666 亿，drain_ratio≈2.5% → SEVERE → 仓位上限降至 75%）。

    Args:
        upcoming_ipos: 候选 IPO 事件列表（含未来与过去，本函数按前瞻窗口过滤）
        market_avg_volume_20d: 全市场 20 日均成交额（亿元）
        today: 基准日（默认今日；测试可注入）
        config: 恢复/预警配置（默认 LiquidityCrisisConfig()）

    Returns:
        IPOLiquidityDrain（drain_ratio / drain_level / position_cap_adjustment）

    Raises:
        InvalidLiquidityCrisisInputError: 市场日均成交额非正 / 募资额为负
    """
    cfg = config or LiquidityCrisisConfig()
    if market_avg_volume_20d <= 0:
        raise InvalidLiquidityCrisisInputError(f"market_avg_volume_20d must be positive, got {market_avg_volume_20d}")
    ref_today = today or datetime.now(UTC).date()

    # 前瞻窗口过滤：今日 ≤ 上市日 ≤ 今日 + horizon（memo 伪代码口径为自然日）
    horizon_end = date.fromordinal(ref_today.toordinal() + cfg.ipo_horizon_days)
    total_raise = 0.0
    counted = 0
    for ipo in upcoming_ipos:
        if ipo.raise_amount < 0:
            raise InvalidLiquidityCrisisInputError(f"raise_amount must be >=0, got {ipo.raise_amount} ({ipo.symbol})")
        if ref_today <= ipo.listing_date <= horizon_end:
            total_raise += ipo.raise_amount
            counted += 1

    drain_ratio = total_raise / market_avg_volume_20d

    t_neg, t_mod, t_sev = cfg.ipo_drain_thresholds
    cap_neg, cap_mod, cap_sev, cap_ext = cfg.ipo_cap_adjustments
    if drain_ratio < t_neg:
        drain_level, cap_adj = IPODrainLevel.NEGLIGIBLE, cap_neg
    elif drain_ratio < t_mod:
        drain_level, cap_adj = IPODrainLevel.MODERATE, cap_mod
    elif drain_ratio < t_sev:
        drain_level, cap_adj = IPODrainLevel.SEVERE, cap_sev
    else:
        drain_level, cap_adj = IPODrainLevel.EXTREME, cap_ext

    if drain_level in (IPODrainLevel.SEVERE, IPODrainLevel.EXTREME):
        logger.warning(
            "IPO liquidity drain alert: ratio=%.4f level=%s cap_adj=%.2f ipos=%d",
            drain_ratio,
            drain_level.value,
            cap_adj,
            counted,
        )

    return IPOLiquidityDrain(
        drain_ratio=drain_ratio,
        drain_level=drain_level,
        position_cap_adjustment=cap_adj,
        counted_ipos=counted,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 盘中流动性监控单遍编排（37号 §3.8）
# ──────────────────────────────────────────────────────────────────────────────


def run_intraday_liquidity_check(
    snapshot: MarketLiquiditySnapshot,
    recovery_state: LiquidityRecoveryState,
    detector: AshareSystemicRiskDetector | None = None,
    config: LiquidityCrisisConfig | None = None,
    now: datetime | None = None,
) -> LiquidityLoopResult:
    """盘中流动性监控单遍检查——四阶段编排（37号 §3.8）。

    由调用方（盘中风控循环，30s tick，对齐 35号 §3.13）逐 tick 驱动——
    本函数无内部轮询/定时器（事件驱动铁律 trae_060）。

    编排顺序（关键，乱序即算法断裂）：
      1. 涨跌停检测（§3.5.1）先行——涨跌停时 spread 失效须解析有效价差
      2. 流动性危机检测（§3.1）——委托 MOD-RK-10，触发阈值从其 config 读取
      3. 响应执行（§3.3）——按 LEVEL_1/2/3 分级（停开仓仅平仓/降仓/逃生指令）
      4. 恢复判定（§3.6）——仅非危机时检查（防"刚触发就恢复"thrashing）

    A股 T+1 约束：LEVEL_1/2 的"仅平仓"受 T+1 限制——当日买入不可卖，
    平仓只对 T-1 及更早持仓生效，新建仓被 halt_new_orders 阻断。

    Args:
        snapshot: 盘口流动性快照（miniQMT 五档 tick 对齐）
        recovery_state: 危机恢复状态（调用方持有跨 tick 持久）
        detector: MOD-RK-10 检测器（默认构造，生产须注入共享实例）
        config: 恢复/预警配置
        now: 判定时间（默认 UTC now；测试可注入）

    Returns:
        LiquidityLoopResult（含 alert + halt_new_orders + position_cap +
        recovery_target + escape_directive）
    """
    detector = detector or AshareSystemicRiskDetector()
    cfg = config or LiquidityCrisisConfig()
    now = now or datetime.now(UTC)

    # ── 阶段 1：涨跌停检测（§3.5.1）──须先于危机检测，spread 涨跌停时失效 ──
    limit_status = detect_limit_status(
        last_price=snapshot.last_price,
        limit_up_price=snapshot.limit_up_price,
        limit_down_price=snapshot.limit_down_price,
        bid_price=snapshot.bid_price,
        ask_price=snapshot.ask_price,
        near_limit_band=cfg.near_limit_band,
    )

    # ── 阶段 2：危机检测（§3.1，委托 MOD-RK-10，检测真源唯一）──
    sell_pressure = compute_sell_pressure(snapshot.bid_volumes, snapshot.ask_volumes)
    raw_spread = compute_bid_ask_spread(snapshot.bid_price, snapshot.ask_price)
    effective_spread = resolve_effective_spread(limit_status, raw_spread)

    alert = detector.check(
        sell_pressure=sell_pressure,
        bid_ask_spread=effective_spread,
        now=now,
    )

    # ── 阶段 3：响应执行（§3.3）——分级，停开仓仅平仓 ──
    level_num = _alert_level_to_int(alert.alert_level)
    halt_new_orders = level_num >= 1
    position_cap = alert.position_cap
    escape_directive: dict[str, Any] | None = None
    if alert.is_emergency:
        escape_directive = detector.build_escape_directive(alert)
        logger.warning(
            "Liquidity crisis LEVEL_3: symbol=%s escape directive issued",
            snapshot.symbol,
        )

    recovery_target: int | None = None
    if alert.is_triggered:
        # 进入/迁移危机级别（以本次触发时刻重置持续时间计数）
        if not recovery_state.in_crisis or recovery_state.level != level_num:
            recovery_state.enter_crisis(level_num, timestamp=now)
    else:
        # ── 阶段 4：恢复判定（§3.6）——仅非危机时检查 ──
        if recovery_state.in_crisis:
            trigger_spread = detector.config.bid_ask_spread_threshold
            trigger_pressure = detector.config.sell_pressure_threshold
            # §3.1 双条件活动信号计数（卖压超阈值 + spread 超阈值，范围 0-2）
            active_signals = int(sell_pressure >= trigger_pressure) + int(
                effective_spread is not None and effective_spread >= trigger_spread
            )
            # 有效价差缺失（如涨停）按 0.0 处理——买压主导侧无危机语义
            spread_for_recovery = effective_spread if effective_spread is not None else 0.0
            recovery_target = check_recovery(
                RecoveryCheckInput(
                    current_spread=spread_for_recovery,
                    current_sell_pressure=sell_pressure,
                    trigger_threshold_spread=trigger_spread,
                    recovery_threshold_spread=trigger_spread * cfg.spread_recovery_ratio,
                    trigger_threshold_pressure=trigger_pressure,
                    recovery_threshold_pressure=cfg.sell_pressure_recovery,
                    min_hold_minutes=cfg.min_hold_minutes[recovery_state.level],
                    elapsed=recovery_state.elapsed_minutes(now),
                    current_level=recovery_state.level,
                    active_signals=active_signals,
                )
            )
            # ⚠️ 用 is not None 判定——target_level=0（LEVEL_1→正常）是有效恢复
            if recovery_target is not None:
                prev_level = recovery_state.level
                recovery_state.exit_crisis(target_level=recovery_target, timestamp=now)
                halt_new_orders = recovery_target >= 1
                position_cap = {0: 1.0, 1: 1.0, 2: 0.70}[recovery_target]
                logger.info(
                    "Liquidity crisis recovery: symbol=%s L%d→L%d",
                    snapshot.symbol,
                    prev_level,
                    recovery_target,
                )

    return LiquidityLoopResult(
        symbol=snapshot.symbol,
        limit_status=limit_status,
        sell_pressure=sell_pressure,
        raw_spread=raw_spread,
        effective_spread=effective_spread,
        alert=alert,
        halt_new_orders=halt_new_orders,
        position_cap=position_cap,
        recovery_target=recovery_target,
        escape_directive=escape_directive,
        timestamp=now,
    )


def _alert_level_to_int(level: SystemicRiskAlertLevel) -> int:
    """SystemicRiskAlertLevel 枚举 → 整数级别（0=NONE）。"""
    return {
        SystemicRiskAlertLevel.NONE: 0,
        SystemicRiskAlertLevel.LEVEL_1: 1,
        SystemicRiskAlertLevel.LEVEL_2: 2,
        SystemicRiskAlertLevel.LEVEL_3: 3,
    }[level]
