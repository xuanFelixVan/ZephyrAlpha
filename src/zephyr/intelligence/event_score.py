# [BLUEPRINT] MOD-INT-EVENT-SCORE | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md | §2.5
# [MODULE] zephyr.intelligence.event_score
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] pandas; zephyr.data.trading_calendar; zephyr.data.ch_reader（默认量能 provider，lazy）; zephyr.data.table_registry（lazy）
# [CONSUMERS] 事件驱动 sleeve（首批策略C，选股漏斗 BM-SEL-19 第四层输入，待开通降级不阻塞）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] event_score 单因子∈[-1.5,+1.5]；|score|<0.2 噪声不动作；EMERGENCY 熔断停止开仓（调用方注入）；T+1：holding_days=0 买入当日不可卖，EXTREME_REACTION 线须 holding_days>=1；利空事件只能剔除/回避（A股不能做空）；volume_series 默认 provider symbol 参数白名单校验防注入
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md §2.4/§2.5
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EventScoreError(ZA-IT-0005)——symbol 非法/输入契约违反时抛；数据缺失走降级路径不抛
# [TESTS] tests/intelligence/test_event_score.py
# [A_module] module_id=MOD-INT-EVENT-SCORE | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] 26_event_driven_strategy_detail §2.5 事件影响评分/进出场触发算法
# [ALGO_FLOW]
# I1: EventRecord（symbol/class_/surprise_direction/sentiment_score/decay_stage_factor/extreme_reaction_modifier/day0_reaction/actual_eps/report_type）
# I2: EarningsFactorData（业绩类一致预期/盈余波动/EAR/ORJ 价格，外部数据层供给）
# I3: MarketEventStore（事件存储协议，MVP=ListEventStore 内存实现）+ VolumeProvider（量能协议，默认 ClickHouse kline_daily）
# F1: event_score_single_factor（六类权重×方向×情绪×衰减×极端修正 ∈[-1.5,1.5]）
# F2: event_score_dual_factor（SUE+EAR，业绩类）/ event_score_triple_factor（+预期差+ORJ，主选）
# F3: compute_event_score 调度（业绩+三因子数据→triple；业绩+双因子数据→dual；其余→single 降级）
# F4: should_enter / should_enter_with_confirmation（EMERGENCY→不动作→|score|<0.2 噪声→方向分支→确认型第三分支）
# F5: should_exit（DECAY_TIMEOUT / EXTREME_REACTION / CONTRADICTION 三道线）
# A1: has_contradictory_event（event_store 近 5 交易日反向事件）+ has_volume_confirmation（量比≥1.5×20日均量）
# A2: check_selling_pressure_absorbed（CVD 转正+放量+价格企稳，PEAD Inversion 极端负反应 day2-3 确认）
# A3: 薄封装 trading_days_ago（交易日历）/ volume_series / volume_ma（kline_daily 薄查询）
# O1: 评分 float / 入场 True|"EXIT"|("WAIT_CONFIRM",2)|False / 出场 "DECAY_TIMEOUT"|"EXTREME_REACTION"|"CONTRADICTION"|False
# [/ALGO_FLOW]
"""MOD-INT-EVENT-SCORE — 事件驱动 sleeve 事件影响评分与进出场触发（26 号 §2.5 施工化）。

公式族（26 号 §2.5 首版/v1.2.0/v1.3.0 逐式落码）：
- ``event_score_single_factor``：六类通用首版
  ``weight × surprise_direction × sentiment_score × decay_stage_factor × extreme_reaction_modifier``
  ∈ [-1.5, +1.5]；正→入池做多候选，负→剔除/回避；``|score| < 0.2`` → 噪声不动作。
- ``event_score_dual_factor``：业绩类 SUE+EAR 双因子（Rockstead 2026-05，r=0.004 近正交）。
- ``event_score_triple_factor``：SUE(预期差增强)+EAR+ORJ 三因子（v1.3.0 主选，
  一致预期时序可得时；双因子为降级默认；无业绩数据时单因子兜底）。
- ``compute_event_score``：调度器——扩展单点修改。

进出场（§2.5 首版 + v1.2.0 确认型 + §1.3 T+1 时序）：
- ``should_enter`` 四分支；``should_enter_with_confirmation`` 补确认型第三分支
  （模糊事件等 day1-2 量价确认）。
- ``should_exit`` 三道线：decay 兜底 / 极端反应提前退出（``holding_days>=1``，T+1 约束）
  / 反向事件覆盖。

辅助函数（v1.7.0 补全闭环）+ 四薄封装（v1.9.1 接口契约）：
- ``has_contradictory_event`` / ``has_volume_confirmation`` / ``decay_exit_window``。
- ``event_store``：协议 + ``ListEventStore`` 内存 MVP——生产 ClickHouse 落库
  （fund_news_data + 事件分类落库）依赖事件分类管道，未闭合，登记降级。
- ``volume_series`` / ``volume_ma``：c1_market.kline_daily 薄封装（默认 CH provider，
  可注入 fake 测试）。
- ``trading_days_ago``：复用 zephyr.data.trading_calendar。

外部数据（一致预期/EAR/ORJ 价格）由调用方从数据层获取后经
``EarningsFactorData`` 注入——本模块不直接依赖万得/同花顺接口（保持纯函数可测）。

依据: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md §2.4/§2.5
Version: 0.1.0
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Final, Protocol, Sequence, runtime_checkable

import numpy as np
import pandas as pd

from zephyr.data.calendar import MarketCalendar, get_market_calendar

# 默认 A 股日历（保持向后兼容，零行为变化）
_DEFAULT_CALENDAR: Final = get_market_calendar("ashare")

try:
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # noqa: BLE001  # pragma: no cover
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_log = logging.getLogger(__name__)


class EventScoreError(ZephyrBaseError):
    """ZA-IT-0005: 事件评分输入契约违反（symbol 非法/字段缺失）。"""

    # 2026-08-21 定稿（Owner 批准两步收口）：原 ZA-INT-0001 与 sentinel_server.MCPError
    # 重码→改号 ZA-INT-0005（git 首引入裁定 canonical=先引入者）；同日 INT→IT 前缀
    # 语义迁移定稿 ZA-IT-0005（注册表 IT=D_INTELLIGENCE 为本模块域；零消费方实证）
    error_code = "ZA-IT-0005"


# ── 26 号 §2.5 常量（首版裁定值）──
EVENT_CLASS_WEIGHT: Final[dict[str, float]] = {
    "earnings": 1.0,  # 业绩
    "ma": 1.2,  # 并购
    "policy": 0.8,  # 政策
    "surprise": 1.5,  # 突发
    "ipo": 1.3,  # IPO/再融资（v1.6.0）
    "geopolitical": 1.4,  # 地缘/宏观（v1.6.0）
}

# decay_exit_window（§2.4 衰减表 rising+decay 总长 = 持仓天数上限，v1.7.0 程序化）
DECAY_EXIT_WINDOW: Final[dict[str, int]] = {
    "earnings": 10,  # 业绩：rising 5 + decay 5
    "ma": 15,  # 并购：rising 7 + decay 8
    "policy": 20,  # 政策：rising 10 + decay 10
    "surprise": 5,  # 突发：rising 2 + decay 3
    "ipo": 15,  # IPO：上市后 day1-5 虹吸期 + day6-15 衰减
    "geopolitical": 25,  # 地缘：rising 5-15 远长于业绩/并购
}
DEFAULT_DECAY_EXIT_WINDOW: Final[int] = 10  # 未知事件类保守默认

SIGNAL_NOISE_THRESHOLD: Final[float] = 0.2  # |score| < 0.2 → 噪声不动作
EXTREME_REACTION_THRESHOLD: Final[float] = 0.03  # §2.4 PEAD Inversion 3% 阈值
WINSORIZE_Z_LIMIT: Final[float] = 3.0  # SUE winsorize ±3
DEFAULT_MIN_VOLUME_RATIO: Final[float] = 1.5  # 量比阈值（1.5×20 日均量）
VOLUME_BASELINE_WINDOW: Final[int] = 20  # 均量基线窗口
CONTRADICT_LOOKBACK_DAYS: Final[int] = 5  # 反向事件回溯交易日数

# 报告期权重（中邮证券 2026-06：一季报最优，年报 A 股不定价利好降权）
REPORT_PERIOD_WEIGHT: Final[dict[str, float]] = {
    "Q1": 1.0,
    "semi": 0.8,
    "Q3": 0.7,
    "annual": 0.4,
}
DEFAULT_REPORT_WEIGHT: Final[float] = 0.7

# 确认型入场等待交易日数（v1.2.0：极端反应等 day 2 确认）
WAIT_CONFIRM_DAYS: Final[int] = 2


# ── 数据契约 ──────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class EventRecord:
    """事件记录（event_score 输入契约）。

    class_ : earnings / ma / policy / surprise / ipo / geopolitical（六类，§2.3）。
    surprise_direction : +1 利好 / -1 利空 / 0 中性。
    sentiment_score : NLP 情绪分 [-1, +1]（#ARCH-NLP-PIPELINE-001，
        作事件方向触发维度，非截面排序——§2.7 QLoRA 警示）。
    decay_stage_factor : rising=1.0 / decay=0.5 / post-decay=0.2。
    extreme_reaction_modifier : |reaction|>3% → 0.3（§2.4 极端反转修正）；否则 1.0。
    day0_reaction : 事件日收益率（PEAD Inversion 判定）。
    actual_eps / report_type : 业绩类专用（Q1/semi/Q3/annual）。
    """

    symbol: str
    class_: str
    surprise_direction: float = 0.0
    sentiment_score: float = 0.0
    decay_stage_factor: float = 1.0
    extreme_reaction_modifier: float = 1.0
    day0_reaction: float = 0.0
    actual_eps: float = 0.0
    report_type: str = "Q3"


@dataclass(frozen=True, slots=True)
class EarningsFactorData:
    """业绩类事件外部因子数据（调用方从数据层获取注入）。

    dual 必需：consensus_eps / surprise_std / ear。
    triple 追加：consensus_before / consensus_after（公告前后一致预期，
    修正动量）+ open_next / close_event（ORJ 价格对）。
    """

    consensus_eps: float
    surprise_std: float
    ear: float
    consensus_before: float | None = None
    consensus_after: float | None = None
    open_next: float | None = None
    close_event: float | None = None

    @property
    def has_triple(self) -> bool:
        """三因子数据齐备（一致预期时序 + OHLC 可得，v1.3.0 主选条件）。"""
        return (
            self.consensus_before is not None
            and self.consensus_after is not None
            and self.open_next is not None
            and self.close_event is not None
        )


@dataclass(frozen=True, slots=True)
class StoredEvent:
    """事件存储记录（event_store 协议元素，MVP 内存实现）。"""

    symbol: str
    event_date: date
    surprise_direction: float = 0.0
    class_: str = ""


@runtime_checkable
class MarketEventStore(Protocol):
    """市场事件存储协议（26 号 v1.9.1 接口契约薄封装）。

    生产实现（fund_news_data + 事件分类落库）依赖事件分类管道，未闭合；
    MVP 用 ``ListEventStore`` 内存实现承载 ``has_contradictory_event`` 查询。
    """

    def query(self, *, symbol: str, since: date) -> list[StoredEvent]: ...


class ListEventStore:
    """MarketEventStore 内存 MVP 实现（上游管道 add 事件，sleeve query 消费）。"""

    def __init__(self) -> None:
        self._events: list[StoredEvent] = []

    def add(self, event: StoredEvent) -> None:
        self._events.append(event)

    def query(self, *, symbol: str, since: date) -> list[StoredEvent]:
        return [e for e in self._events if e.symbol == symbol and e.event_date >= since]


@runtime_checkable
class VolumeProvider(Protocol):
    """量能数据协议（26 号 v1.9.1 薄封装：个股日K 表 PIT 查询基座）。"""

    def volume_series(self, symbol: str, days: int) -> list[float]: ...
    def volume_ma(self, symbol: str, window: int) -> float: ...


# ── 评分公式族 ────────────────────────────────────────────────────────


def event_score_single_factor(event: EventRecord) -> float:
    """首版单因子评分（六类通用）。∈ [-1.5, +1.5]。

    ``weight[class_] × surprise_direction × sentiment_score ×
    decay_stage_factor × extreme_reaction_modifier``（§2.5 首版显式公式）。
    """
    return (
        EVENT_CLASS_WEIGHT.get(event.class_, 1.0)
        * event.surprise_direction
        * event.sentiment_score
        * event.decay_stage_factor
        * event.extreme_reaction_modifier
    )


def _winsorize_z(x: float) -> float:
    return max(-WINSORIZE_Z_LIMIT, min(WINSORIZE_Z_LIMIT, x))


def event_score_dual_factor(event: EventRecord, data: EarningsFactorData) -> float:
    """业绩类双因子：SUE(基本面惊喜) + EAR(市场反应)。

    Rockstead 2026-05：SUE 与 EAR 近零相关（r=0.004），组合年化 18.50%；
    EAR 含反转成分，用于"识别过度反应"而非"追涨"（§2.5 v1.2.0）。
    combined > 0 → 漂移延续占优 → 入池做多；< 0 → 过度反应反转占优 → 不追涨/回避。
    """
    sue = 0.0 if data.surprise_std <= 0 else (event.actual_eps - data.consensus_eps) / data.surprise_std
    sue_z = _winsorize_z(sue)
    reaction_extremity = abs(data.ear) / EXTREME_REACTION_THRESHOLD
    ear_reversal_weight = min(reaction_extremity, 1.0)  # 0~1，越极端越反转
    return sue_z * (1 - ear_reversal_weight * 0.5) - data.ear * ear_reversal_weight * 10


def expectation_gap_with_revision_momentum(
    actual_eps: float,
    report_type: str,
    *,
    consensus: float,
    consensus_before: float,
    consensus_after: float,
) -> float:
    """A 股预期差 + 分析师修正动量（Whisper Number 本土化，§2.5 v1.3.0）。

    季报/半年报用财报后一致预期**变动**（上调=超预期）；年报用静态预期差且降权
    （A 股不定价业绩利好）。gap > 0 = 超预期，< 0 = 不及预期。
    """
    static_gap = (actual_eps - consensus) / abs(consensus) if consensus != 0 else 0.0
    revision_momentum = (consensus_after - consensus_before) / abs(consensus_before) if consensus_before != 0 else 0.0
    if report_type != "annual":
        return revision_momentum
    return static_gap * REPORT_PERIOD_WEIGHT.get(report_type, DEFAULT_REPORT_WEIGHT)


def overnight_return_jump(open_next: float, close_event: float) -> float:
    """ORJ 隔夜跳空 = 次日开盘价 / 事件日收盘价 - 1（Bahcivan 2023，§2.5 v1.3.0）。

    A 股 T+1 下财报多盘后披露 → 次日开盘 = 市场隔夜消化后第一反应。
    close_event ≤ 0（数据缺失）→ 0.0 降级。
    """
    if close_event <= 0:
        return 0.0
    return open_next / close_event - 1.0


def event_score_triple_factor(event: EventRecord, data: EarningsFactorData) -> float:
    """SUE(预期差增强) + EAR(日内反应) + ORJ(隔夜跳空) 三因子融合（v1.3.0 主选）。

    三因子两两近正交 → 真分散化。ORJ 极端（>3%）触发反转修正（与 §2.4
    PEAD Inversion 协同，比 3 日 EAR 更早的前置预警）。
    combined > 0 → 入池做多；< 0 → 不追涨/回避。

    Raises
    ------
    EventScoreError
        data 缺三因子字段（契约违反；调度器经 has_triple 预检不会触发）。
    """
    if not data.has_triple:
        raise EventScoreError("event_score_triple_factor: EarningsFactorData 缺三因子字段")
    sue = expectation_gap_with_revision_momentum(
        event.actual_eps,
        event.report_type,
        consensus=data.consensus_eps,
        consensus_before=float(data.consensus_before),
        consensus_after=float(data.consensus_after),
    )
    sue_z = _winsorize_z(sue)
    orj = overnight_return_jump(float(data.open_next), float(data.close_event))
    orj_signal = orj if abs(orj) <= EXTREME_REACTION_THRESHOLD else -orj * 0.5  # 极端跳空反转修正
    reaction_extremity = max(abs(data.ear), abs(orj)) / EXTREME_REACTION_THRESHOLD
    reversal_weight = min(reaction_extremity, 1.0)
    return (
        sue_z * (1 - reversal_weight * 0.3)  # SUE 漂移（极端反应时降权）
        + orj_signal * 2.0  # ORJ 隔夜第一反应（温和时加权）
        - data.ear * reversal_weight * 10  # EAR 过度反应反转修正
    )


def compute_event_score(event: EventRecord, data: EarningsFactorData | None = None) -> float:
    """评分调度器（26 号 v1.7.0）：业绩类→双/三因子，其他五类→首版单因子。

    降级链：业绩+三因子数据→triple（主选）→ 业绩+双因子数据→dual（降级默认）
    → 业绩无外部数据→single（兜底，§2.7 单条推理降级裁定同源）。
    """
    if event.class_ == "earnings" and data is not None:
        if data.has_triple:
            return event_score_triple_factor(event, data)
        return event_score_dual_factor(event, data)
    if event.class_ == "earnings" and data is None:
        _log.debug("compute_event_score: 业绩类无 EarningsFactorData，降级单因子 symbol=%s", event.symbol)
    return event_score_single_factor(event)


# ── 进出场触发 ────────────────────────────────────────────────────────


def should_enter(
    event: EventRecord,
    current_position: float,
    *,
    emergency: bool = False,
    data: EarningsFactorData | None = None,
) -> object:
    """入场触发（§2.5 首版四分支）。

    EMERGENCY 熔断停开仓（调用方读 MarketEventIntegrator.current_mode 注入）
    → 评分 → |score|<0.2 噪声不动作 → score>0 且空仓开多 / score<0 且有持仓 "EXIT"。
    """
    if emergency:
        return False
    score = compute_event_score(event, data)
    if abs(score) < SIGNAL_NOISE_THRESHOLD:
        return False
    if score > 0 and current_position == 0:
        return True
    if score < 0 and current_position > 0:
        return "EXIT"
    return False


def should_enter_with_confirmation(
    event: EventRecord,
    current_position: float,
    day0_reaction: float | None = None,
    *,
    emergency: bool = False,
    data: EarningsFactorData | None = None,
    volume_confirmed: bool = False,
) -> object:
    """事件触发后入场决策（v1.2.0 确认型完整版，NexusFi 三模式补全）。

    1. 极端反应（|reaction|>3%）→ ``("WAIT_CONFIRM", 2)`` 等 day 2 确认反转
    2. 温和反应且有明确信号（|score|≥0.2）→ 立即入场/EXIT（momentum continuation）
    3. 模糊事件（|score|<0.2 且温和正反应 + 次日量价确认）→ 确认型入场

    ``volume_confirmed`` 由调用方以 ``has_volume_confirmation`` 预先计算注入。
    """
    if emergency:
        return False
    score = compute_event_score(event, data)
    reaction = event.day0_reaction if day0_reaction is None else day0_reaction

    # 1. 极端反应：不入场（§2.4 PEAD Inversion，反转风险）
    if abs(reaction) > EXTREME_REACTION_THRESHOLD:
        return ("WAIT_CONFIRM", WAIT_CONFIRM_DAYS)
    # 2. 温和反应且有明确信号
    if abs(score) >= SIGNAL_NOISE_THRESHOLD:
        if score > 0 and current_position == 0:
            return True
        if score < 0 and current_position > 0:
            return "EXIT"
    # 3. 模糊事件：等 day 1-2 量价确认再入场，避免噪声
    if 0 < reaction <= EXTREME_REACTION_THRESHOLD and volume_confirmed:
        return True
    return False


def should_exit(
    event: EventRecord,
    position: float,
    holding_days: int,
    *,
    contradictory: bool = False,
    decay_exit_window: dict[str, int] | None = None,
) -> object:
    """出场触发（§2.5 三道线）。

    1. decay phase 兜底退出（按事件类衰减表）
    2. 极端反应提前退出（§2.4 PEAD Inversion，``holding_days>=1`` 隐含 T+1 约束：
       买入当日=0 不可卖，次日=1 可卖起点）
    3. 反向事件触发（新利空覆盖旧利好，``contradictory`` 由
       ``has_contradictory_event`` 预先计算注入）

    ``position`` 保留于签名（首版契约），当前三道线不消费。
    """
    del position  # 首版三道线不消费持仓量，仅签名契约
    windows = decay_exit_window or DECAY_EXIT_WINDOW
    if holding_days > windows.get(event.class_, DEFAULT_DECAY_EXIT_WINDOW):
        return "DECAY_TIMEOUT"
    if abs(event.day0_reaction) > EXTREME_REACTION_THRESHOLD and holding_days >= 1:
        return "EXTREME_REACTION"
    if contradictory:
        return "CONTRADICTION"
    return False


# ── 辅助函数（v1.7.0 补全）────────────────────────────────────────────


def trading_days_ago(
    n: int,
    *,
    from_date: date | None = None,
    calendar: MarketCalendar | None = None,
) -> date:
    """n 个交易日前的日期（默认 A 股日历，可注入其他市场日历）。

    n=0 → from_date 当日；n<0 → EventScoreError。

    Args:
        n: 回溯交易日数（≥0）
        from_date: 基准日期（None=今日）
        calendar: 市场日历注入（None=ASHareCalendar 默认，零行为变化）
    """
    if n < 0:
        raise EventScoreError(f"trading_days_ago: n 须 ≥0，实际 {n}")
    cal = calendar or _DEFAULT_CALENDAR
    d = from_date or date.today()
    count = 0
    while count < n:
        d -= timedelta(days=1)
        if cal.is_trading_day(d):
            count += 1
    return d


def has_contradictory_event(
    symbol: str,
    current_direction: float = 1.0,
    lookback_days: int = CONTRADICT_LOOKBACK_DAYS,
    *,
    event_store: MarketEventStore,
    today: date | None = None,
) -> bool:
    """检测近 lookback_days 交易日是否有与持仓方向相反的事件（should_exit 第三道线）。

    current_direction 恒 +1（A 股不能做空，持仓即多头）。
    """
    since = trading_days_ago(lookback_days, from_date=today)
    for ev in event_store.query(symbol=symbol, since=since):
        if ev.surprise_direction != 0 and ev.surprise_direction != current_direction:
            return True
    return False


def has_volume_confirmation(
    recent_volumes: Sequence[float],
    baseline_volume: float,
    min_ratio: float = DEFAULT_MIN_VOLUME_RATIO,
) -> bool:
    """事件后成交量是否放大（确认型入场第三分支，NexusFi confirmation 施工化）。

    recent_volumes : 事件后成交量序列（``volume_series(symbol, days)`` 产物）。
    baseline_volume  : 20 日均量基线（``volume_ma(symbol, 20)`` 产物）；
        ≤0（新股/长期停牌基线缺失）→ 保守不入场。
    """
    if baseline_volume <= 0:
        return False
    if not recent_volumes:
        return False
    return float(np.mean(list(recent_volumes))) >= min_ratio * baseline_volume


def check_selling_pressure_absorbed(
    day2_3_data: pd.DataFrame,
    baseline_volume_ratio: float = 1.5,
    cvd_threshold: float = 0.0,
) -> dict[str, Any]:
    """吸收卖压判定（§2.4 PEAD Inversion 极端负反应 day 2-3 确认）。

    day2_3_data : day 2-3 分钟级 OHLCV（列 high/low/close/volume）。
    CVD 转正（买方主动量超卖方=聪明资金低位接货）+ 量能放大（放量消化）
    + 价格企稳（跌幅<2%）三者共振才确认"吸收卖压"。
    空数据/列缺失/量能基线 NaN → absorbed=False（保守观望）。
    """
    required = {"high", "low", "close", "volume"}
    if day2_3_data is None or day2_3_data.empty:
        return {"absorbed": False, "cvd_final": 0.0, "volume_ratio": 0.0, "price_stabilized": False}
    missing = required - set(day2_3_data.columns)
    if missing:
        raise EventScoreError(f"check_selling_pressure_absorbed: 缺列 {sorted(missing)}")

    mid_price = (day2_3_data["high"] + day2_3_data["low"]) / 2
    delta = np.where(
        day2_3_data["close"] > mid_price,
        day2_3_data["volume"],
        -day2_3_data["volume"],
    )
    cvd = np.cumsum(delta)
    baseline = day2_3_data["volume"].rolling(5).mean().mean()
    volume_ratio = (
        float(day2_3_data["volume"].mean() / baseline) if baseline and not np.isnan(baseline) else float("nan")
    )
    price_stabilized = bool(
        day2_3_data["close"].iloc[-1] >= day2_3_data["close"].iloc[0] * 0.98  # 跌幅<2%
    )
    absorbed = bool(
        not np.isnan(volume_ratio)
        and cvd[-1] > cvd_threshold
        and volume_ratio > baseline_volume_ratio
        and price_stabilized
    )
    return {
        "absorbed": absorbed,  # True=卖压已吸收可布局, False=卖压未止继续观望
        "cvd_final": float(cvd[-1]),
        "volume_ratio": volume_ratio,
        "price_stabilized": price_stabilized,
    }


# ── 量能薄封装（默认 ClickHouse kline_daily provider）──────────────────

_SYMBOL_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9.]{1,20}$")

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀，同 pit_query 约定）
_SQL_VOLUME = "SELECT trade_date, volume FROM {table} WHERE symbol = '{symbol}' ORDER BY trade_date DESC LIMIT {limit}"


class ClickHouseKlineVolumeProvider:
    """VolumeProvider 默认实现——c1_market.kline_daily 薄查询（production 数据基座）。

    lazy import ch_reader/table_registry：纯函数测试路径零 CH 依赖。
    """

    def __init__(self) -> None:
        from zephyr.data.table_registry import get_registry

        self._table = get_registry().table("market_kline_daily")

    def _fetch(self, symbol: str, limit: int) -> list[tuple[str, float]]:
        if not _SYMBOL_RE.match(symbol):
            raise EventScoreError(f"volume 查询 symbol 非法: {symbol!r}")
        from zephyr.data import ch_reader

        tsv = ch_reader.query(_SQL_VOLUME.format(table=self._table, symbol=symbol, limit=limit))
        if not tsv or not tsv.strip():
            return []
        rows: list[tuple[str, float]] = []
        for line in tsv.strip().splitlines():
            parts = line.split("\t")
            if len(parts) != 2:
                continue
            try:
                rows.append((parts[0], float(parts[1])))
            except ValueError:
                continue
        rows.reverse()  # DESC → 时间升序
        return rows

    def volume_series(self, symbol: str, days: int) -> list[float]:
        """最近 days 个交易日成交量（时间升序）；无数据 → 空列表。"""
        if days <= 0:
            return []
        return [v for _, v in self._fetch(symbol, days)]

    def volume_ma(self, symbol: str, window: int) -> float:
        """最近 window 个交易日均量；样本不足/无数据 → 0.0（调用方按基线缺失降级）。"""
        if window <= 0:
            return 0.0
        vals = [v for _, v in self._fetch(symbol, window)]
        if len(vals) < window:
            return 0.0
        return float(np.mean(vals))


_DEFAULT_VOLUME_PROVIDER: VolumeProvider | None = None


def _default_volume_provider() -> VolumeProvider:
    global _DEFAULT_VOLUME_PROVIDER
    if _DEFAULT_VOLUME_PROVIDER is None:
        _DEFAULT_VOLUME_PROVIDER = ClickHouseKlineVolumeProvider()
    return _DEFAULT_VOLUME_PROVIDER


def volume_series(symbol: str, days: int, *, provider: VolumeProvider | None = None) -> list[float]:
    """事件后 days 日成交量序列（26 号 v1.9.1 薄封装，默认 kline_daily provider）。"""
    return (provider or _default_volume_provider()).volume_series(symbol, days)


def volume_ma(symbol: str, window: int = VOLUME_BASELINE_WINDOW, *, provider: VolumeProvider | None = None) -> float:
    """window 日均量基线（默认 20 日）。"""
    return (provider or _default_volume_provider()).volume_ma(symbol, window)


__all__: Final = [
    "EVENT_CLASS_WEIGHT",
    "DECAY_EXIT_WINDOW",
    "DEFAULT_DECAY_EXIT_WINDOW",
    "SIGNAL_NOISE_THRESHOLD",
    "EXTREME_REACTION_THRESHOLD",
    "DEFAULT_MIN_VOLUME_RATIO",
    "VOLUME_BASELINE_WINDOW",
    "CONTRADICT_LOOKBACK_DAYS",
    "REPORT_PERIOD_WEIGHT",
    "WAIT_CONFIRM_DAYS",
    "EventScoreError",
    "EventRecord",
    "EarningsFactorData",
    "StoredEvent",
    "MarketEventStore",
    "ListEventStore",
    "VolumeProvider",
    "ClickHouseKlineVolumeProvider",
    "event_score_single_factor",
    "event_score_dual_factor",
    "event_score_triple_factor",
    "compute_event_score",
    "expectation_gap_with_revision_momentum",
    "overnight_return_jump",
    "should_enter",
    "should_enter_with_confirmation",
    "should_exit",
    "trading_days_ago",
    "has_contradictory_event",
    "has_volume_confirmation",
    "check_selling_pressure_absorbed",
    "volume_series",
    "volume_ma",
]
