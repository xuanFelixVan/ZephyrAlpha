# [BLUEPRINT] MOD-SIG-135 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/69_trading_decision_map.md §2.11 D20
# [MODULE] zephyr.signal_ashare.core.daily_condition_sensor
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（纯函数核，零 IO；原始指标由调用方从 DS-082/DS-059/DS-150 算好注入）
# [CONSUMERS] TDM-E-L1-S5（日级市场条件传感器）；TDM-E-L1-AGG（四层温度计日级输入）；TDM-E-L2-05-1（水温→响应）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 11 信号各自三值判定(+1/0/-1)后计票合成; 缺数据信号计 0 票并记 missing; 可用信号<6 → tier=None(INSUFFICIENT_DATA fail-closed); 昨日基数=0 的环比信号按缺数据处理(防除零); net→五档映射单调且闭区间边界确定; 同输入必同输出(frozen); D20 裁噪预留=相关性去重不在本件(灰度合成阶段做)
# [MODIFY-GUARD] design_memos/69_trading_decision_map.md §2.11 D20 + 地图节点 TDM-E-L1-S5
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非法枚举/负家数 → DailyConditionSensorError（fail-closed）；缺数据不是错误（记 missing 走降级）
# [TESTS] tests/signal_ashare/test_daily_condition_sensor.py
# [TTL] permanent
"""DailyConditionSensor — 日级市场条件传感器（11 信号→S0-S4 五档水温，D20）。

69 号备忘录 §2.11 D20 定稿：日级水温是四层温度计里唯一盘中可变的 L1 输入，
管"今天多激进"——水烫(S4)=当日可激进，水冰(S0)=当日只看不动。

**A 组实战 8 信号**：①涨停家数环比 ②连板梯队环比 ③炸板率(>50% 警报)
④跌停+核按钮家数 ⑤昨日涨停溢价(≤-5% 警报) ⑥红盘家数(<1500 警报)
⑦量能匹配诱多识别(价升量缩) ⑧板块联动混沌。
**B 组机构 3 信号**：⑨宽度领先 ⑩对坏消息的反应 ⑪市值分层宽度。

Owner 裁定"先大而全跑数据、后数据裁噪"（D21 三防弹衣适用）：11 信号全上计票，
相关性去重留灰度合成阶段。5 档判定阈值=经验拍定（proposed），回测校准后升级
（holdout 纪律：12 个月保密考卷只考一次）。

查重分工（蓝图 §1）：market_state_sensor=日 BAR trend×vol 九网格（月/周级状态的
日度快照）；本件=**盘中环比骤变读数**（当日 11 信号计票→五档），是 S5 的合成核。
sector_gate.WaterTemp=水温档的**响应侧**（本模块输出可映射为其入参），本件不判响应。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DailyConditionSensorError(ValueError):
    """非法输入（fail-closed）：负家数/比率越界。"""


class WaterTempTier(str, Enum):
    """日级水温五档（S0 冰 → S4 烫；管今天多激进）。"""

    S0_ICE = "S0"  # 水冰：当日只看不动
    S1_COOL = "S1"
    S2_NEUTRAL = "S2"  # 中性
    S3_WARM = "S3"
    S4_HOT = "S4"  # 水烫：当日可激进


class SignalVote(str, Enum):
    """单信号三值计票（+1 偏多 / 0 中性或缺数据 / -1 偏空）。"""

    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    BULLISH = "BULLISH"


@dataclass(frozen=True)
class DailySensorThresholds:
    """11 信号判定阈值（经验拍定=proposed，回测校准后升级；config 可注入）。"""

    limit_up_ratio_up: float = 1.10  # ①涨停家数环比 >1.10 → +1
    limit_up_ratio_down: float = 0.90  # ① <0.90 → -1
    ladder_ratio_up: float = 1.10  # ②连板梯队环比
    ladder_ratio_down: float = 0.90
    failed_board_bearish: float = 0.50  # ③炸板率 >50% → -1（D20 警报线）
    failed_board_bullish: float = 0.20  # ③ <20% → +1
    limit_down_bearish: int = 30  # ④跌停+核按钮 >30 家 → -1
    limit_down_bullish: int = 0  # ④ =0 → +1
    premium_bearish: float = -0.05  # ⑤昨日涨停溢价 ≤-5% → -1（D20 警报线）
    premium_bullish: float = 0.02  # ⑤ ≥+2% → +1
    advancers_bearish: int = 1500  # ⑥红盘 <1500 → -1（D20 警报线）
    advancers_bullish: int = 2800  # ⑥ >2800 → +1
    sector_chaos_bearish: float = 0.60  # ⑧板块联动混沌 >0.6 → -1
    sector_chaos_bullish: float = 0.30  # ⑧ <0.3 → +1
    breadth_leading_band: float = 0.10  # ⑨宽度领先 |x|>0.1 计票
    bad_news_react_bullish: float = 0.05  # ⑩抗跌 >+5% → +1
    bad_news_react_bearish: float = -0.10  # ⑩利空大跌 <-10% → -1
    cap_tier_breadth_bullish: float = 0.60  # ⑪市值分层宽度 >0.6 → +1
    cap_tier_breadth_bearish: float = 0.30  # ⑪ <0.3 → -1
    min_available_signals: int = 6  # 可用信号低于此数 → 拒绝给档（fail-closed）


@dataclass(frozen=True)
class DailyRawSignals:
    """当日盘中 11 信号原始读数（None=该信号暂缺数据；环比类自带昨日基数）。

    语义说明：⑦量能诱多 volume_match_trap=True 表示"指数涨但量能萎缩"（诱多，
    偏空）；None=量价关系正常或暂缺。⑩对坏消息的反应 bad_news_reaction>0=抗跌
    （强），<0=利空放大（脆弱）。⑪市值分层宽度 cap_tier_breadth≈各市值层宽度
    的健康离散度（普涨活跃=高，单层独撑=低）。
    """

    limit_up_count: int | None = None  # ①当日
    limit_up_count_prev: int | None = None  # ①昨日基数
    ladder_count: int | None = None  # ②连板（≥2 板）家数
    ladder_count_prev: int | None = None
    failed_board_ratio: float | None = None  # ③∈[0,1]
    limit_down_count: int | None = None  # ④跌停+核按钮
    yesterday_limit_up_premium: float | None = None  # ⑤∈[-1,1] 平均价差
    advancers: int | None = None  # ⑥红盘家数
    volume_match_trap: bool | None = None  # ⑦True=价升量缩诱多
    sector_chaos_index: float | None = None  # ⑧∈[0,1]
    breadth_leading: float | None = None  # ⑨环比变化 ∈[-1,1]
    bad_news_reaction: float | None = None  # ⑩∈[-1,1]
    cap_tier_breadth: float | None = None  # ⑪∈[0,1]

    def __post_init__(self) -> None:
        for name in ("limit_up_count", "limit_up_count_prev", "ladder_count",
                     "ladder_count_prev", "limit_down_count", "advancers"):
            v = getattr(self, name)
            if v is not None and v < 0:
                raise DailyConditionSensorError(f"{name} 家数不可为负: {v}")
        for name, lo, hi in (
            ("failed_board_ratio", 0.0, 1.0),
            ("yesterday_limit_up_premium", -1.0, 1.0),
            ("sector_chaos_index", 0.0, 1.0),
            ("breadth_leading", -1.0, 1.0),
            ("bad_news_reaction", -1.0, 1.0),
            ("cap_tier_breadth", 0.0, 1.0),
        ):
            v = getattr(self, name)
            if v is not None and not (lo <= v <= hi):
                raise DailyConditionSensorError(f"{name} 越界 [{lo},{hi}]: {v}")


@dataclass(frozen=True)
class SignalDetail:
    """单信号计票明细（可审计）。"""

    name: str
    vote: SignalVote
    missing: bool


@dataclass(frozen=True)
class DailyConditionVerdict:
    """五档水温读数（frozen）。"""

    tier: WaterTempTier | None  # None=数据不足拒绝给档
    net_score: int  # 计票净分（+多-空）
    bullish_count: int
    bearish_count: int
    missing_count: int
    insufficient_data: bool
    details: tuple[SignalDetail, ...] = field(default_factory=tuple)


def _ratio_vote(
    today: int | None, prev: int | None, th: DailySensorThresholds,
    up: float, down: float, name: str,
) -> tuple[SignalVote, bool]:
    """环比三值判定；昨日基数缺失或为 0（无法算环比）按缺数据。"""
    if today is None or prev is None or prev == 0:
        return SignalVote.NEUTRAL, True
    ratio = today / prev
    if ratio > up:
        return SignalVote.BULLISH, False
    if ratio < down:
        return SignalVote.BEARISH, False
    return SignalVote.NEUTRAL, False


def _band_vote(value: float | None, th: DailySensorThresholds,
               bull_over: float, bear_under: float) -> tuple[SignalVote, bool]:
    """带通三值判定（越高越好型）：>bull_over → +1，<bear_under → -1。"""
    if value is None:
        return SignalVote.NEUTRAL, True
    if value > bull_over:
        return SignalVote.BULLISH, False
    if value < bear_under:
        return SignalVote.BEARISH, False
    return SignalVote.NEUTRAL, False


def _low_good_vote(value: float | None, good_under: float,
                   bad_over: float) -> tuple[SignalVote, bool]:
    """低优三值判定（越低越好型：炸板率/板块混沌）：<good_under → +1，>bad_over → -1。

    边界口径：警报线为严格大于（D20"炸板率>50%"），恰好等于警报线计中性。
    """
    if value is None:
        return SignalVote.NEUTRAL, True
    if value < good_under:
        return SignalVote.BULLISH, False
    if value > bad_over:
        return SignalVote.BEARISH, False
    return SignalVote.NEUTRAL, False




def _tier_of(net: int) -> WaterTempTier:
    """净分→五档映射（单调：≥+4 S4 / +2~+3 S3 / -1~+1 S2 / -2~-3 S1 / ≤-4 S0）。"""
    if net >= 4:
        return WaterTempTier.S4_HOT
    if net >= 2:
        return WaterTempTier.S3_WARM
    if net >= -1:
        return WaterTempTier.S2_NEUTRAL
    if net >= -3:
        return WaterTempTier.S1_COOL
    return WaterTempTier.S0_ICE

def _limit_down_vote(value: int | None, th: DailySensorThresholds) -> tuple[SignalVote, bool]:
    """④跌停+核按钮（>上限偏空；=0 偏多）。"""
    if value is None:
        return SignalVote.NEUTRAL, True
    if value > th.limit_down_bearish:
        return SignalVote.BEARISH, False
    if value == th.limit_down_bullish:
        return SignalVote.BULLISH, False
    return SignalVote.NEUTRAL, False


def _advancers_vote(value: int | None, th: DailySensorThresholds) -> tuple[SignalVote, bool]:
    """⑥红盘家数（<下限偏空；>上限偏多）。"""
    if value is None:
        return SignalVote.NEUTRAL, True
    if value < th.advancers_bearish:
        return SignalVote.BEARISH, False
    if value > th.advancers_bullish:
        return SignalVote.BULLISH, False
    return SignalVote.NEUTRAL, False


def _trap_vote(is_trap: bool | None) -> tuple[SignalVote, bool]:
    """⑦量能诱多（True=价升量缩偏空；False=正常偏多）。"""
    if is_trap is None:
        return SignalVote.NEUTRAL, True
    return (SignalVote.BEARISH, False) if is_trap else (SignalVote.BULLISH, False)


def evaluate_daily_condition(
    raw: DailyRawSignals,
    thresholds: DailySensorThresholds | None = None,
) -> DailyConditionVerdict:
    """11 信号计票 → S0-S4 五档水温（纯函数，同输入必同输出）。

    映射（单调，闭区间边界确定）：net ≥ +4 → S4；+2~+3 → S3；-1~+1 → S2；
    -2~-3 → S1；≤ -4 → S0。可用信号（非 missing）< min_available_signals
    → tier=None + insufficient_data=True（fail-closed：数据不足不下激进结论）。
    """
    th = thresholds or DailySensorThresholds()

    details: list[SignalDetail] = []

    # ①涨停家数环比
    v, miss = _ratio_vote(raw.limit_up_count, raw.limit_up_count_prev, th,
                          th.limit_up_ratio_up, th.limit_up_ratio_down, "limit_up_ratio")
    details.append(SignalDetail("limit_up_ratio", v, miss))
    # ②连板梯队环比
    v2, miss2 = _ratio_vote(raw.ladder_count, raw.ladder_count_prev, th,
                            th.ladder_ratio_up, th.ladder_ratio_down, "ladder_ratio")
    details.append(SignalDetail("ladder_ratio", v2, miss2))
    # ③炸板率（越低越好：<20% 偏多；>50% 警报偏空）
    v3, miss3 = _low_good_vote(raw.failed_board_ratio,
                               th.failed_board_bullish, th.failed_board_bearish)
    details.append(SignalDetail("failed_board_ratio", v3, miss3))
    # ④跌停+核按钮（>30 偏空；=0 偏多）
    v4, miss4 = _limit_down_vote(raw.limit_down_count, th)
    details.append(SignalDetail("limit_down_count", v4, miss4))
    # ⑤昨日涨停溢价（≤-5% 警报偏空；≥+2% 偏多）
    v5, miss5 = _band_vote(raw.yesterday_limit_up_premium, th,
                           th.premium_bullish, th.premium_bearish)
    details.append(SignalDetail("yesterday_premium", v5, miss5))
    # ⑥红盘家数（<1500 警报偏空；>2800 偏多）
    v6, miss6 = _advancers_vote(raw.advancers, th)
    details.append(SignalDetail("advancers", v6, miss6))
    # ⑦量能匹配诱多识别（True=价升量缩 → -1；False=正常 → +1；None=缺）
    v7, miss7 = _trap_vote(raw.volume_match_trap)
    details.append(SignalDetail("volume_match_trap", v7, miss7))
    # ⑧板块联动混沌（越低越好：<0.3 → +1；>0.6 混沌 → -1）
    v8, miss8 = _low_good_vote(raw.sector_chaos_index,
                               th.sector_chaos_bullish, th.sector_chaos_bearish)
    details.append(SignalDetail("sector_chaos", v8, miss8))
    # ⑨宽度领先（对称带通）
    v9, miss9 = _band_vote(raw.breadth_leading, th,
                           th.breadth_leading_band, -th.breadth_leading_band)
    details.append(SignalDetail("breadth_leading", v9, miss9))
    # ⑩对坏消息的反应（抗跌 +1；利空放大 -1）
    v10, miss10 = _band_vote(raw.bad_news_reaction, th,
                             th.bad_news_react_bullish, th.bad_news_react_bearish)
    details.append(SignalDetail("bad_news_reaction", v10, miss10))
    # ⑪市值分层宽度（>0.6 → +1；<0.3 → -1）
    v11, miss11 = _band_vote(raw.cap_tier_breadth, th,
                             th.cap_tier_breadth_bullish, th.cap_tier_breadth_bearish)
    details.append(SignalDetail("cap_tier_breadth", v11, miss11))

    bullish = sum(1 for d in details if d.vote is SignalVote.BULLISH)
    bearish = sum(1 for d in details if d.vote is SignalVote.BEARISH)
    missing = sum(1 for d in details if d.missing)
    net = bullish - bearish
    available = len(details) - missing

    if available < th.min_available_signals:
        return DailyConditionVerdict(
            tier=None,
            net_score=net,
            bullish_count=bullish,
            bearish_count=bearish,
            missing_count=missing,
            insufficient_data=True,
            details=tuple(details),
        )

    return DailyConditionVerdict(
        tier=_tier_of(net),
        net_score=net,
        bullish_count=bullish,
        bearish_count=bearish,
        missing_count=missing,
        insufficient_data=False,
        details=tuple(details),
    )
