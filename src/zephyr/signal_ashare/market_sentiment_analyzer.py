# [BLUEPRINT] MOD-SIG-025 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_ashare.market_sentiment_analyzer
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.shared.contracts.synthesized_signal
# [CONSUMERS] zephyr.signal_ashare.youzi_relay_emotion_engine; zephyr.signal_ashare.dual_engine_fusion_decision_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] overall_sentiment_score in [0, 100]; all sub-scores in [0, 100];
#   M1 增量维度（①②a/b⑤⑥⑦）输入缺数据 → 对应结果字段 None 且不参与加权
#   （维度⑧缺失时权重自动归一回既有 6 分数，行为与现状一致）；
#   distortion_flag=True 时综合分 ×0.7 降权后仍 clamp 至 [0, 100]
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] MarketSentimentDataError
# [TESTS] tests/signal_ashare/test_market_sentiment_analyzer.py; tests/signal_ashare/test_market_sentiment_m1_increments.py
# [A_module] module_id=MOD-SIG-025 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""


D-SIGNAL-25 — A股市场情绪分析引擎

7维度市场情绪分析：
  1. 涨跌家数分析（二八分化检测）
  2. 涨停跌停数量分析（做多热情/恐慌蔓延）
  3. 赚钱效应评估器（涨停板/板块涨幅/市场温度）
  4. 次日回调风险预警器（指数涨个股跌→次日风险）
  5. 市场士气评估器（散户游资跟随度）
  6. 封板率分析
  7. 昨日涨停表现追踪

设计真源: D:\临时工作区\依赖图-D-SIGNAL-信号域.md §1 D-SIGNAL-25
策略参数: 全部通过 MarketSentimentConfig 可配置，默认值取自设计文档

M1 情绪增量包（44 号升级备忘 §9.1/§9.2/§9.4 + 92 号清单 §6.1，2026-08-22 施工；
全部优雅降级——Optional 输入缺数据时该维度跳过/置 None 不炸）：
  M1-① 涨跌加速度三件套（§9.1）：breadth_vel_5m / breadth_acc_15m（二阶）/
    lu_net_rate_5m / break_rate_5m；拐点信号（修复中=lu_net_rate 由负转正且持续
    ≥10min；恶化中=breadth_vel<0 且指数涨幅>0）；20 日滚动 z-score 归一
    （统计由消费方预计算供给）；快照缺失>2min 当分钟置 NaN 不外推。
  M1-②a/b 护盘/风格失真检测=维度⑧（§9.2 过渡近似版）：
    a) 指数贡献度拆解 guard_ratio=Σcontrib(固定权重股名单 TOP≈10，config 常量)
       /max(指数涨幅,ε)；护盘假象=guard_ratio>0.6 且 adv/total<0.4；
    b) 黄白线剪刀差 spread=ret_加权-ret_不加权；权重掩护=spread>+1σ_20d 且 30min 走扩；
    a/b 任一触发 → distortion_flag=True → 综合情绪分降权 ×0.7；
    维度⑧权重 ≤0.10 可配置，缺数据时跳过且权重自动归一回既有 6 分数。
  M1-⑤ 量能盘中预测（§9.4 上半）：p̄(t)=20 日同时刻累计成交占全天比中位数曲线
    （240 点，消费方预计算）；ŷ_full=cum_vol(t)/p̄(t)；缩量警示=ŷ<20日均量×0.85；
    放量确认=ŷ>1.2× 且 breadth_vel>0。
  M1-⑥ 大幅回撤个股数（§9.4 下半）：日内曾冲高≥5% 且现价回吐≥50% 计数；
    ≥7 只且最大回撤>10% → 追涨被埋警示（M2 降档触发条件之一的信号输出）。
  M1-⑦ 昨日破板今表现（§2 M1-⑦ + 92 号 §1 D11 实证口径）：炸板判定=K线×涨跌停
    联算（昨日 high≥limit_up 且 close<limit_up）；今日平均收益=承接力指标。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 市场涨跌家数 MarketBreadthData数据类
#   fields: 上涨家数 + 下跌家数 + 平盘家数 + 总家数
#   code: MarketBreadthData L53
# - id: I2
#   name: 涨跌停数据 LimitUpDownData数据类
#   fields: 涨停数 + 跌停数 + 接近涨停数(涨幅>9%) + 封住涨停数 + 曾涨停数(含炸板)
#   code: LimitUpDownData L63
# - id: I3
#   name: 指数表现 IndexPerformanceData数据类
#   fields: 指数名称 + 指数涨跌幅%
#   code: IndexPerformanceData L74
# - id: I4
#   name: 昨日涨停今日表现 YesterdayLimitUpPerformance数据类
#   fields: 昨日涨停数量 + 今日平均收益 + 今日正收益比例（可空）
#   code: YesterdayLimitUpPerformance L82
# 层: 特征
# - id: F1
#   name_zh: 上涨家数占比
#   name_en: advance_ratio
#   intro: 上涨股票占全市场的比例 ≥80%即二八分化
#   formula: 上涨家数/总家数 ∈0,1
#   code: market_sentiment_analyzer.py L203
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F2
#   name_zh: 下跌家数占比
#   name_en: decline_ratio
#   intro: 下跌股票占比 指数涨它却高=虚假繁荣
#   formula: 下跌家数/总家数 ∈0,1
#   code: market_sentiment_analyzer.py L281
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F3
#   name_zh: 封板率
#   name_en: seal_rate
#   intro: 曾涨停的股票里有多少最终封住 衡量打板资金诚意
#   formula: 封住涨停数/曾涨停数 ∈0,1 ≥0.7好 ≤0.4差
#   code: market_sentiment_analyzer.py L329
#   registry: factor_registry: 无FCT条目
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① 涨跌家数分析
#   name_en: analyze_breadth
#   intro: 检测二八分化/普涨/普跌/均衡并打分
#   desc: 涨或跌占比≥0.8→二八分化 >0.6→普涨/普跌 否则均衡 分段线性映射0-100
#   inputs: I1 F1 F2
#   outputs: breadth_status + breadth_score
# - id: A2
#   name_zh: ② 涨跌停热情分析
#   name_en: analyze_limit_activity
#   intro: 看涨停跌停数量判断做多热情还是恐慌蔓延
#   desc: 涨停≥50→做多热情 跌停≥20→恐慌蔓延 否则 score=50+(涨停-跌停)×2
#   inputs: I2
#   outputs: limit_zeal_status + limit_score
# - id: A3
#   name_zh: ③ 赚钱效应与市场士气评估
#   name_en: evaluate_profit_effect + evaluate_morale
#   intro: 用上涨占比分别评估赚钱强不强和散户跟随士气
#   desc: 占比≥0.6→强/高涨 ≤0.3→弱/低迷 中间给50分 分段线性映射
#   inputs: I1 F1
#   outputs: profit_effect + morale 双评分
# - id: A4
#   name_zh: ④ 次日回调风险预警
#   name_en: warn_next_day_risk
#   intro: 指数涨但个股跌占比高→预警次日回调
#   desc: 指数涨 且 跌占比≥0.3→高风险 ≥0.4→中风险 否则低风险
#   inputs: I1 I3 F2
#   outputs: next_day_risk_status + score
# - id: A5
#   name_zh: ⑤ 封板率分档与昨日涨停追踪
#   name_en: analyze_seal_rate + track_yesterday_limit_up
#   intro: 封板率分好中差 昨日涨停股今日均收益>3%好 <-2%差
#   desc: seal_rate×100为分 昨涨停均收益阈值分档 无数据→"无数据"
#   inputs: I2 I4 F3
#   outputs: seal_rate_status + yesterday_lu_status
# - id: A6
#   name_zh: ⑥ 综合评分与情绪阶段定位
#   name_en: analyze + _determine_phase
#   intro: 6维分数加权成综合情绪分 再定位5档情绪阶段
#   desc: overall=涨跌停0.20+赚钱效应0.20+士气0.15+封板率0.15+涨跌家数0.15+次日风险0.15 → <20冰点 <40反核 <60主升 <80疯狂 ≥80退潮
#   inputs: A1 A2 A3 A4 A5
#   outputs: overall_score + sentiment_phase
# 层: 输出
# - id: O1
#   name_zh: 市场情绪分析结果
#   name_en: MarketSentimentResult
#   intro: 7维状态与评分+综合情绪分+情绪阶段 一次输出
#   invariant: overall_sentiment_score in [0,100]; all sub-scores in [0,100]
#   downstream: 游资接力情绪引擎 MOD-SIG-033; 双引擎融合决策引擎 MOD-SIG-035
# [/ALGO_FLOW]
#
# 边:
# I1 -.->|断点| F1
# I1 -.->|断点| F2
# I2 -.->|断点| F3
# F1 --> A1
# F2 --> A1
# F1 --> A3
# F2 --> A4
# F3 --> A5
# I2 --> A2
# I3 --> A4
# I4 --> A5
# A1 --> A6
# A2 --> A6
# A3 --> A6
# A4 --> A6
# A5 --> A6
# A6 --> O1
"""

# =============================================================================
# BM-SEL-25 影响评估（BM-SEL-23-B 输出契约升级：4+1 硬标签 → 5 维灰度概率，
# 2026-08-19 AI-NIGHT-001 包G；对齐 10_regime_detector_spec §2.5.4 用户裁定
# "输出应为灰度概率，不是硬标签" 与 28_sentiment_cycle_trading §3.3）
#
# 升级内容：新增 analyze_grayscale() → MarketSentimentGrayscaleResult
# （5 维灰度概率 P(冰点..退潮) Σ=1 + dominant_phase + confidence + fallback_triggered）。
#
# 评估结论：既有硬标签消费方**零影响**，灰度为**纯增量**——
#   1. analyze() 签名/返回类型/硬标签语义（sentiment_phase 5 档）完全不变；
#   2. BM-SEL-25 双引擎融合（MOD-SIG-035）当前经游资引擎（MOD-SIG-033）自有
#      4+1 阶段判定消费情绪周期（grep 实证：不直接 import 本模块类），
#      本模块新增方法不改变其任何既有输入；
#   3. 灰度输出为新方法 + 新 dataclass，无字段删改、无行为变更、无下游迁移成本。
# 后续：28 号 memo §3.3 locate_sentiment_phase 为灰度定位器完整版（设计态，
# 贝叶斯+转移平滑+兜底），本方法为 production 硬标签链路的轻量灰度桥
# （同一 overall_score 按阶段中心高斯软分配）。
# =============================================================================

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Final, Mapping, Optional


class SentimentPhase(str, Enum):
    """市场情绪阶段"""

    FREEZING = "冰点"
    REVERSAL = "反核"
    MAIN_RALLY = "主升"
    EUPHORIA = "疯狂"
    RETREATING = "退潮"


@dataclass(frozen=True)
class MarketBreadthData:
    """市场涨跌家数数据"""

    advancing_count: int
    declining_count: int
    flat_count: int
    total_count: int


@dataclass(frozen=True)
class LimitUpDownData:
    """涨跌停数据"""

    limit_up_count: int
    limit_down_count: int
    near_limit_up_count: int  # 接近涨停（涨幅>9%）
    sealed_limit_up_count: int  # 封住涨停的数量
    attempted_limit_up_count: int  # 曾涨停（含炸板）


@dataclass(frozen=True)
class IndexPerformanceData:
    """指数表现数据"""

    index_name: str
    index_change_pct: float  # 指数涨跌幅


@dataclass(frozen=True)
class YesterdayLimitUpPerformance:
    """昨日涨停股今日表现"""

    count: int  # 昨日涨停数量
    avg_return_today: float  # 今日平均收益
    positive_ratio: float  # 今日正收益比例


# ------------------------------------------------------------------
# M1 增量输入结构（44 号 §9.1/§9.2/§9.4；快照式纯函数，消费方喂数据）
# ------------------------------------------------------------------


@dataclass(frozen=True)
class BreadthSnapshot:
    """M1-① 分钟级全市场快照（44 号 §9.1）"""

    timestamp: datetime
    advancing_count: int  # 上涨家数
    declining_count: int  # 下跌家数
    limit_up_count: int  # 涨停数
    sealed_limit_up_count: int  # 封住涨停数
    attempted_limit_up_count: int  # 曾涨停数（含炸板）


@dataclass(frozen=True)
class FeatureZScoreStats:
    """20 日滚动 z-score 归一统计（消费方预计算供给；std≤0 时 z 不计算）"""

    mean: float
    std: float


@dataclass(frozen=True)
class BreadthTimeSeries:
    """M1-① 分钟级快照序列（时间升序，分钟粒度；缺失分钟按 NaN 处理不外推）"""

    snapshots: tuple[BreadthSnapshot, ...]
    total_count: int  # 全市场家数
    zscore_stats: Mapping[str, FeatureZScoreStats] | None = None  # 特征名 → 20 日滚动统计


@dataclass(frozen=True)
class IndexContributionInput:
    """M1-②a 指数贡献度拆解输入（过渡近似版；权重取 config 固定名单）"""

    constituent_returns: Mapping[str, float]  # 成分代码 → 当日涨幅（与指数涨幅同单位）


@dataclass(frozen=True)
class SpreadSeriesInput:
    """M1-②b 黄白线剪刀差输入（spread = ret_加权指数 - ret_不加权等权指数）"""

    spreads: tuple[float, ...]  # 分钟级 spread 序列，时间升序
    hist_mean: float  # 20 日同时刻 spread 均值（消费方预计算）
    hist_std: float  # 20 日同时刻 spread 标准差（≤0 时 z 不计算）


@dataclass(frozen=True)
class VolumeForecastInput:
    """M1-⑤ 量能盘中预测输入（44 号 §9.4 上半）"""

    cum_volume: float  # 当日截至当前累计成交额（亿）
    minute_index: int  # 当前分钟序号（对应 pct_curve 下标，9:30=0）
    pct_curve: tuple[float, ...]  # p̄(t)：20 日同时刻累计成交占全天比中位数曲线（分钟级 240 点）
    avg_full_volume_20d: float  # 20 日全天均量（亿）


@dataclass(frozen=True)
class StockIntradayGain:
    """M1-⑥ 个股日内涨幅快照（用于大幅回撤判定）"""

    high_gain_pct: float  # 日内最高涨幅（%）
    current_gain_pct: float  # 现价涨幅（%）


@dataclass(frozen=True)
class BrokenBoardStock:
    """M1-⑦ 昨日炸板候选股（K线×涨跌停联算判定）及其今日表现"""

    code: str
    yesterday_high: float  # 昨日最高价
    yesterday_close: float  # 昨日收盘价
    yesterday_limit_up: float  # 昨日涨停价
    today_return_pct: float  # 今日收益（小数）


@dataclass(frozen=True)
class MarketSentimentInput:
    """市场情绪分析输入"""

    timestamp: datetime
    breadth: MarketBreadthData
    limit_data: LimitUpDownData
    index_performance: IndexPerformanceData
    yesterday_limit_up: YesterdayLimitUpPerformance | None = None
    market_turnover: float = 0.0  # 市场成交额（亿）
    # ---- M1 增量 Optional 输入（44 号；缺数据=对应维度跳过，由消费方/调度回路供给）----
    time_series: BreadthTimeSeries | None = None  # M1-① 分钟级快照序列
    index_contrib: IndexContributionInput | None = None  # M1-②a 指数贡献度
    spread_series: SpreadSeriesInput | None = None  # M1-②b 黄白线剪刀差
    volume_series: VolumeForecastInput | None = None  # M1-⑤ 量能盘中预测
    drawdown_stocks: tuple[StockIntradayGain, ...] | None = None  # M1-⑥ 回撤候选股
    broken_board_stocks: tuple[BrokenBoardStock, ...] | None = None  # M1-⑦ 昨日炸板候选


# M1-②a 护盘固定权重股名单（过渡近似版，44 号 §9.2：四大行+两桶油+保险龙头 TOP≈10；
# 权重为静态近似值，精确版待 #225 index_weight 闭环后替换）
DEFAULT_GUARD_WEIGHTS: Final[dict[str, float]] = {
    "601398.SH": 0.035,  # 工商银行
    "601939.SH": 0.025,  # 建设银行
    "601288.SH": 0.030,  # 农业银行
    "601988.SH": 0.020,  # 中国银行
    "600036.SH": 0.030,  # 招商银行
    "601857.SH": 0.025,  # 中国石油
    "600028.SH": 0.015,  # 中国石化
    "601318.SH": 0.040,  # 中国平安
    "601628.SH": 0.015,  # 中国人寿
    "601601.SH": 0.010,  # 中国太保
}


@dataclass
class MarketSentimentConfig:
    """市场情绪分析配置（全部可配置，默认值取自设计文档）"""

    # 二八分化检测
    divergence_ratio_threshold: float = 0.8  # 上涨占比>80%或<20%=二八分化

    # 涨停热情阈值
    limit_up_zeal_threshold: int = 50  # 涨停>50=做多热情
    limit_down_panic_threshold: int = 20  # 跌停>20=恐慌蔓延

    # 封板率阈值
    seal_rate_good: float = 0.7  # >70%=好
    seal_rate_bad: float = 0.4  # <40%=差

    # 赚钱效应阈值
    profit_effect_strong: float = 0.6  # 上涨家数占比>60%=强
    profit_effect_weak: float = 0.3  # <30%=弱

    # 次日回调风险
    next_day_risk_divergence_threshold: float = 0.3  # 指数涨但个股跌占比>30%=高风险

    # 市场士气阈值
    morale_high_threshold: float = 0.6  # 上涨占比>60%=高涨
    morale_low_threshold: float = 0.3  # <30%=低迷

    # 昨日涨停表现
    yesterday_lu_good_return: float = 0.03  # 均收益>3%=好
    yesterday_lu_bad_return: float = -0.02  # <-2%=差

    # 情绪阶段评分阈值
    phase_freezing_score: float = 20.0  # <20=冰点
    phase_reversal_score: float = 40.0  # 20-40=反核
    phase_main_rally_score: float = 60.0  # 40-60=主升
    phase_euphoria_score: float = 80.0  # 60-80=疯狂
    # >80=退潮（高位开始退潮）

    # ---- M1-① 涨跌加速度（44 号 §9.1）----
    accel_vel_window_min: int = 5  # 速度窗口（分钟）
    accel_acc_window_min: int = 15  # 二阶加速度窗口（分钟）
    accel_repair_persist_min: int = 10  # 修复中判定：lu_net_rate 由负转正后持续 ≥10min

    # ---- M1-②a/b 护盘/风格失真（44 号 §9.2，过渡近似版）----
    guard_weights: dict[str, float] = field(
        default_factory=lambda: dict(DEFAULT_GUARD_WEIGHTS)
    )  # 护盘固定权重股名单（代码→近似权重）
    guard_ratio_threshold: float = 0.6  # 护盘比阈值：>0.6 且 adv/total<0.4 → 护盘假象
    guard_breadth_low: float = 0.4  # 上涨占比阈值：<0.4=指数红但 6 成个股跌
    guard_epsilon: float = 1e-4  # 指数涨幅分母保护
    spread_zscore_threshold: float = 1.0  # 黄白线 spread > +1σ_20d
    spread_widening_window_min: int = 30  # spread 走扩回看窗口（分钟）
    distortion_weight: float = 0.08  # 维度⑧权重（≤distortion_weight_cap）
    distortion_weight_cap: float = 0.10  # 维度⑧权重上限
    distortion_damp_factor: float = 0.7  # distortion_flag 触发时综合分降权系数

    # ---- M1-⑤ 量能盘中预测（44 号 §9.4 上半）----
    volume_shrink_threshold: float = 0.85  # 缩量警示：ŷ_full < 20 日均量×0.85
    volume_confirm_threshold: float = 1.2  # 放量确认：ŷ_full > 20 日均量×1.2 且 breadth_vel>0

    # ---- M1-⑥ 大幅回撤个股数（44 号 §9.4 下半）----
    drawdown_high_gain_min: float = 5.0  # 日内最高涨幅 ≥5%
    drawdown_pullback_ratio: float = 0.5  # 现价较最高回吐 ≥50%
    drawdown_count_warn: int = 7  # 回撤股数 ≥7
    drawdown_max_pct_warn: float = 10.0  # 且最大回撤 >10% → 追涨被埋警示

    # ---- M1-⑦ 昨日破板今表现（44 号 §2 M1-⑦）----
    broken_board_good_return: float = 0.03  # 破板今均收益 ≥3% = 承接力强
    broken_board_bad_return: float = -0.02  # ≤-2% = 承接力弱


@dataclass(frozen=True)
class BreadthAccelerationResult:
    """M1-① 涨跌加速度三件套结果（44 号 §9.1；缺失分钟置 None 不外推）"""

    breadth_vel_5m: float | None  # (adv_t - adv_{t-5}) / total
    breadth_acc_15m: float | None  # breadth_vel_5m(t) - breadth_vel_5m(t-15)，二阶
    lu_net_rate_5m: float | None  # lu_t - lu_{t-5}，负值=涨停在减少
    break_rate_5m: float | None  # Δattempted / max(Δattempted, Δsealed+Δattempted)
    breadth_vel_5m_z: float | None = None  # 20 日滚动 z-score（统计缺失时 None）
    breadth_acc_15m_z: float | None = None
    lu_net_rate_5m_z: float | None = None
    break_rate_5m_z: float | None = None
    repairing: bool = False  # 修复中：lu_net_rate_5m 由负转正且持续 ≥10min
    deteriorating: bool = False  # 恶化中：breadth_vel_5m<0 且指数涨幅>0


@dataclass(frozen=True)
class DistortionDetectionResult:
    """M1-②a/b 护盘/风格失真检测结果（44 号 §9.2，维度⑧）"""

    guard_ratio: float | None  # a 通道护盘比 Σcontrib(固定权重股)/max(指数涨幅,ε)
    guard_illusion: bool  # a 通道：guard_ratio>0.6 且 adv/total<0.4 → 护盘假象
    spread_current: float | None  # b 通道当前 spread
    spread_zscore: float | None  # b 通道 spread 对 20 日同时刻的 z-score
    spread_widening_30m: bool | None  # b 通道 spread 30min 内走扩
    weight_cover: bool  # b 通道：spread>+1σ_20d 且走扩 → 权重掩护
    distortion_flag: bool  # a/b 任一触发 → 综合情绪分降权 ×0.7
    distortion_score: float  # 维度⑧评分 0-100（触发=0，无信号=100）


@dataclass(frozen=True)
class VolumeForecastResult:
    """M1-⑤ 量能盘中预测结果（44 号 §9.4 上半）"""

    predicted_full_volume: float  # ŷ_full = cum_vol(t) / p̄(t)（亿）
    volume_ratio: float  # ŷ_full / 20 日均量
    shrink_warning: bool  # 缩量警示：<0.85×（情绪分升档受限标记）
    volume_confirm: bool  # 放量确认：>1.2× 且 breadth_vel>0


@dataclass(frozen=True)
class DrawdownRiskResult:
    """M1-⑥ 大幅回撤个股数结果（44 号 §9.4 下半）"""

    drawdown_count: int  # 回撤股数（日内曾冲高≥5% 且现价回吐≥50%）
    max_drawdown_pct: float  # 其中最大回撤（百分点）
    chase_buried_warning: bool  # ≥7 只且最大回撤>10% → 追涨被埋警示


@dataclass(frozen=True)
class BrokenBoardResult:
    """M1-⑦ 昨日破板今表现结果（44 号 §2 M1-⑦）"""

    broken_count: int  # 昨日炸板股数（high≥limit_up 且 close<limit_up）
    avg_return_today: float | None  # 今日平均收益=承接力指标
    positive_ratio: float | None  # 今日正收益比例
    support_strength: str  # "强"/"中"/"弱"/"无数据"


@dataclass(frozen=True)
class MarketSentimentResult:
    """市场情绪分析结果"""

    timestamp: datetime

    # 1. 涨跌家数分析
    breadth_status: str  # "二八分化"/"普涨"/"普跌"/"均衡"
    breadth_score: float  # 0-100

    # 2. 涨跌停分析
    limit_zeal_status: str  # "做多热情"/"正常"/"恐慌蔓延"
    limit_score: float  # 0-100

    # 3. 赚钱效应
    profit_effect_status: str  # "强"/"中"/"弱"
    profit_effect_score: float  # 0-100

    # 4. 次日回调风险
    next_day_risk_status: str  # "高风险"/"中风险"/"低风险"
    next_day_risk_score: float  # 0-100

    # 5. 市场士气
    morale_status: str  # "高涨"/"正常"/"低迷"
    morale_score: float  # 0-100

    # 6. 封板率
    seal_rate_status: str  # "好"/"中"/"差"
    seal_rate: float  # 0-1

    # 7. 昨日涨停表现
    yesterday_lu_status: str  # "好"/"中"/"差"/"无数据"

    # 综合
    overall_score: float  # 0-100
    sentiment_phase: str  # SentimentPhase enum value

    # ---- M1 增量结果（44 号；对应 Optional 输入缺数据时 None，不破坏既有字段）----
    breadth_acceleration: BreadthAccelerationResult | None = None  # M1-①
    distortion: DistortionDetectionResult | None = None  # M1-②a/b（维度⑧）
    volume_forecast: VolumeForecastResult | None = None  # M1-⑤
    drawdown_risk: DrawdownRiskResult | None = None  # M1-⑥
    broken_board: BrokenBoardResult | None = None  # M1-⑦


# ------------------------------------------------------------------
# 23-B 灰度概率输出（增量契约，对齐 10_regime §2.5.4 灰度裁定）
# ------------------------------------------------------------------

# 阶段中心=硬标签分段中点（<20 冰点/20-40 反核/40-60 主升/60-80 疯狂/≥80 退潮）
GRAYSCALE_PHASE_CENTERS: dict[SentimentPhase, float] = {
    SentimentPhase.FREEZING: 10.0,
    SentimentPhase.REVERSAL: 30.0,
    SentimentPhase.MAIN_RALLY: 50.0,
    SentimentPhase.EUPHORIA: 70.0,
    SentimentPhase.RETREATING: 90.0,
}
GRAYSCALE_SIGMA = 12.0  # 高斯软分配带宽：相邻阶段在分段边界处等概率
GRAYSCALE_CONFIDENCE_FALLBACK = 0.60  # 置信度<60%→默认保守（30 号 §6.3）


@dataclass(frozen=True)
class MarketSentimentGrayscaleResult:
    """5 维灰度概率输出（23-B 升级增量契约，既有硬标签结果不受影响）"""

    timestamp: datetime
    phase_prob: dict[str, float]  # {阶段中文名: P}，Σ=1
    dominant_phase: str  # 主导阶段（argmax）
    confidence: float  # 置信度 = max(P)
    overall_score: float  # 综合情绪分（与 analyze() 一致）
    fallback_triggered: bool  # confidence < 0.60 → 建议默认保守


class MarketSentimentDataError(Exception):
    """市场情绪数据不完整错误"""


class MarketSentimentAnalyzer:
    """
    A股市场情绪分析引擎（D-SIGNAL-25）

    7维度分析 → 综合情绪评分 → 情绪阶段定位

    所有策略参数通过 config 可配置，默认值取自设计文档。
    """

    def __init__(self, config: MarketSentimentConfig | None = None) -> None:
        self._config = config or MarketSentimentConfig()

    # ------------------------------------------------------------------
    # 1. 涨跌家数分析（二八分化检测）
    # ------------------------------------------------------------------
    def analyze_breadth(self, breadth: MarketBreadthData) -> tuple[str, float]:
        """分析涨跌家数，检测二八分化"""
        total = breadth.total_count or (breadth.advancing_count + breadth.declining_count + breadth.flat_count)
        if total == 0:
            return "无数据", 50.0

        advance_ratio = breadth.advancing_count / total
        decline_ratio = breadth.declining_count / total

        # 二八分化检测
        if advance_ratio >= self._config.divergence_ratio_threshold:
            status = "二八分化"
            score = 80.0 + (advance_ratio - self._config.divergence_ratio_threshold) * 100
        elif decline_ratio >= self._config.divergence_ratio_threshold:
            status = "二八分化"
            score = 20.0 - (decline_ratio - self._config.divergence_ratio_threshold) * 100
        elif advance_ratio > 0.6:
            status = "普涨"
            score = 60.0 + (advance_ratio - 0.6) * 50
        elif decline_ratio > 0.6:
            status = "普跌"
            score = 40.0 - (decline_ratio - 0.6) * 50
        else:
            status = "均衡"
            score = 50.0 + (advance_ratio - decline_ratio) * 25

        return status, max(0.0, min(100.0, score))

    # ------------------------------------------------------------------
    # 2. 涨停跌停数量分析（做多热情/恐慌蔓延）
    # ------------------------------------------------------------------
    def analyze_limit_activity(self, limit_data: LimitUpDownData) -> tuple[str, float]:
        """分析涨停跌停数量，判断做多热情或恐慌蔓延"""
        lu = limit_data.limit_up_count
        ld = limit_data.limit_down_count

        if lu >= self._config.limit_up_zeal_threshold:
            status = "做多热情"
            score = 70.0 + min(30.0, (lu - self._config.limit_up_zeal_threshold) * 0.5)
        elif ld >= self._config.limit_down_panic_threshold:
            status = "恐慌蔓延"
            score = 30.0 - min(30.0, (ld - self._config.limit_down_panic_threshold) * 0.5)
        else:
            status = "正常"
            # 涨停多于跌停=偏多，反之偏空
            diff = lu - ld
            score = 50.0 + diff * 2.0

        return status, max(0.0, min(100.0, score))

    # ------------------------------------------------------------------
    # 3. 赚钱效应评估器
    # ------------------------------------------------------------------
    def evaluate_profit_effect(self, breadth: MarketBreadthData) -> tuple[str, float]:
        """评估赚钱效应"""
        total = breadth.total_count or (breadth.advancing_count + breadth.declining_count + breadth.flat_count)
        if total == 0:
            return "无数据", 50.0

        advance_ratio = breadth.advancing_count / total

        if advance_ratio >= self._config.profit_effect_strong:
            status = "强"
            score = 60.0 + (advance_ratio - self._config.profit_effect_strong) * 100
        elif advance_ratio <= self._config.profit_effect_weak:
            status = "弱"
            score = 40.0 - (self._config.profit_effect_weak - advance_ratio) * 100
        else:
            status = "中"
            score = 50.0

        return status, max(0.0, min(100.0, score))

    # ------------------------------------------------------------------
    # 4. 次日回调风险预警器
    # ------------------------------------------------------------------
    def warn_next_day_risk(self, breadth: MarketBreadthData, index_perf: IndexPerformanceData) -> tuple[str, float]:
        """预警次日回调风险（指数涨个股跌→次日风险）"""
        total = breadth.total_count or (breadth.advancing_count + breadth.declining_count + breadth.flat_count)
        if total == 0:
            return "无数据", 50.0

        decline_ratio = breadth.declining_count / total
        index_up = index_perf.index_change_pct > 0

        # 指数涨但个股跌=虚假繁荣，次日回调风险高
        if index_up and decline_ratio >= self._config.next_day_risk_divergence_threshold:
            status = "高风险"
            score = 80.0 + (decline_ratio - self._config.next_day_risk_divergence_threshold) * 100
        elif index_up and decline_ratio >= 0.4:
            status = "中风险"
            score = 60.0
        else:
            status = "低风险"
            score = 30.0

        return status, max(0.0, min(100.0, score))

    # ------------------------------------------------------------------
    # 5. 市场士气评估器
    # ------------------------------------------------------------------
    def evaluate_morale(self, breadth: MarketBreadthData) -> tuple[str, float]:
        """评估市场士气（散户游资跟随度）"""
        total = breadth.total_count or (breadth.advancing_count + breadth.declining_count + breadth.flat_count)
        if total == 0:
            return "无数据", 50.0

        advance_ratio = breadth.advancing_count / total

        if advance_ratio >= self._config.morale_high_threshold:
            status = "高涨"
            score = 60.0 + (advance_ratio - self._config.morale_high_threshold) * 100
        elif advance_ratio <= self._config.morale_low_threshold:
            status = "低迷"
            score = 40.0 - (self._config.morale_low_threshold - advance_ratio) * 100
        else:
            status = "正常"
            score = 50.0

        return status, max(0.0, min(100.0, score))

    # ------------------------------------------------------------------
    # 6. 封板率分析
    # ------------------------------------------------------------------
    def analyze_seal_rate(self, limit_data: LimitUpDownData) -> tuple[str, float]:
        """分析封板率"""
        attempted = limit_data.attempted_limit_up_count
        if attempted == 0:
            return "无数据", 50.0, 0.0

        seal_rate = limit_data.sealed_limit_up_count / attempted

        if seal_rate >= self._config.seal_rate_good:
            status = "好"
        elif seal_rate <= self._config.seal_rate_bad:
            status = "差"
        else:
            status = "中"

        score = seal_rate * 100
        return status, max(0.0, min(100.0, score)), seal_rate

    # ------------------------------------------------------------------
    # 7. 昨日涨停表现追踪
    # ------------------------------------------------------------------
    def track_yesterday_limit_up(self, yesterday_lu: YesterdayLimitUpPerformance | None) -> str:
        """追踪昨日涨停股今日表现"""
        if yesterday_lu is None or yesterday_lu.count == 0:
            return "无数据"

        avg_ret = yesterday_lu.avg_return_today
        if avg_ret >= self._config.yesterday_lu_good_return:
            return "好"
        elif avg_ret <= self._config.yesterday_lu_bad_return:
            return "差"
        else:
            return "中"

    # ------------------------------------------------------------------
    # M1-① 涨跌加速度三件套（44 号 §9.1）
    # ------------------------------------------------------------------
    def analyze_breadth_acceleration(
        self,
        time_series: BreadthTimeSeries | None,
        index_change_pct: float,
    ) -> BreadthAccelerationResult | None:
        """涨跌加速度三件套 + 拐点信号。

        time_series=None 或快照数不足 → 整组跳过返回 None；
        分钟网格上缺失快照的窗口特征置 NaN（输出 None）不外推。
        """
        if time_series is None or len(time_series.snapshots) < 2:
            return None
        cfg = self._config
        snaps = sorted(time_series.snapshots, key=lambda s: s.timestamp)
        t0 = snaps[0].timestamp
        n = int(round((snaps[-1].timestamp - t0).total_seconds() / 60.0)) + 1
        w = cfg.accel_vel_window_min
        if n <= w:
            return None

        nan = float("nan")
        adv = [nan] * n
        lu = [nan] * n
        att = [nan] * n
        sealed = [nan] * n
        for s in snaps:
            i = int(round((s.timestamp - t0).total_seconds() / 60.0))
            adv[i] = float(s.advancing_count)
            lu[i] = float(s.limit_up_count)
            att[i] = float(s.attempted_limit_up_count)
            sealed[i] = float(s.sealed_limit_up_count)
        total = float(time_series.total_count)

        # 5min 窗口特征序列（任一操作数缺失 → 当分钟 NaN 不外推）
        vel = [nan] * n
        lu_net = [nan] * n
        brk = [nan] * n
        for i in range(w, n):
            if not (math.isnan(adv[i]) or math.isnan(adv[i - w])) and total > 0:
                vel[i] = (adv[i] - adv[i - w]) / total
            if not (math.isnan(lu[i]) or math.isnan(lu[i - w])):
                lu_net[i] = lu[i] - lu[i - w]
            if not (math.isnan(att[i]) or math.isnan(att[i - w]) or math.isnan(sealed[i]) or math.isnan(sealed[i - w])):
                d_att = att[i] - att[i - w]
                d_sealed = sealed[i] - sealed[i - w]
                den = max(d_att, d_sealed + d_att)
                brk[i] = d_att / den if den > 0 else 0.0
        # 15min 二阶加速度 acc(i) = vel(i) - vel(i-15)
        aw = cfg.accel_acc_window_min
        acc = [nan] * n
        for i in range(w + aw, n):
            if not (math.isnan(vel[i]) or math.isnan(vel[i - aw])):
                acc[i] = vel[i] - vel[i - aw]

        def _val(x: float) -> float | None:
            return None if math.isnan(x) else x

        last = n - 1
        vel_now = _val(vel[last])

        # 拐点·修复中：lu_net_rate_5m 由负转正且持续 ≥10min
        run = 0
        i = last
        while i >= w and not math.isnan(lu_net[i]) and lu_net[i] > 0:
            run += 1
            i -= 1
        repairing = run >= cfg.accel_repair_persist_min and i >= w and not math.isnan(lu_net[i]) and lu_net[i] < 0
        # 拐点·恶化中：breadth_vel_5m<0 且指数涨幅>0
        deteriorating = vel_now is not None and vel_now < 0 and index_change_pct > 0

        # 20 日滚动 z-score 归一（统计由消费方预计算供给）
        stats = time_series.zscore_stats or {}

        def _z(name: str, x: float | None) -> float | None:
            st = stats.get(name)
            if st is None or x is None or st.std <= 0:
                return None
            return (x - st.mean) / st.std

        return BreadthAccelerationResult(
            breadth_vel_5m=vel_now,
            breadth_acc_15m=_val(acc[last]),
            lu_net_rate_5m=_val(lu_net[last]),
            break_rate_5m=_val(brk[last]),
            breadth_vel_5m_z=_z("breadth_vel_5m", vel_now),
            breadth_acc_15m_z=_z("breadth_acc_15m", _val(acc[last])),
            lu_net_rate_5m_z=_z("lu_net_rate_5m", _val(lu_net[last])),
            break_rate_5m_z=_z("break_rate_5m", _val(brk[last])),
            repairing=repairing,
            deteriorating=deteriorating,
        )

    # ------------------------------------------------------------------
    # M1-②a/b 护盘/风格失真检测（44 号 §9.2 过渡近似版，维度⑧）
    # ------------------------------------------------------------------
    def detect_distortion(
        self,
        index_contrib: IndexContributionInput | None,
        spread_series: SpreadSeriesInput | None,
        advance_ratio: float | None,
        index_change_pct: float,
    ) -> DistortionDetectionResult | None:
        """护盘/风格失真检测（a 指数贡献度拆解 + b 黄白线剪刀差）。

        两通道输入均缺或均不可计算 → 维度⑧跳过返回 None；
        a/b 任一触发 → distortion_flag=True（综合分降权 ×0.7）。
        """
        if index_contrib is None and spread_series is None:
            return None
        cfg = self._config

        # 通道 a：指数贡献度拆解（固定权重股名单近似）
        guard_ratio: float | None = None
        guard_illusion = False
        if index_contrib is not None and index_change_pct > cfg.guard_epsilon:
            contrib_sum = 0.0
            for code, weight in cfg.guard_weights.items():
                ret = index_contrib.constituent_returns.get(code)
                if ret is not None:
                    contrib_sum += weight * ret
            guard_ratio = contrib_sum / max(index_change_pct, cfg.guard_epsilon)
            if (
                guard_ratio > cfg.guard_ratio_threshold
                and advance_ratio is not None
                and advance_ratio < cfg.guard_breadth_low
            ):
                guard_illusion = True

        # 通道 b：黄白线剪刀差（spread>+1σ_20d 且 30min 内走扩）
        spread_now: float | None = None
        spread_z: float | None = None
        widening: bool | None = None
        weight_cover = False
        if spread_series is not None and spread_series.spreads:
            spread_now = spread_series.spreads[-1]
            if spread_series.hist_std > 0:
                spread_z = (spread_now - spread_series.hist_mean) / spread_series.hist_std
            w30 = cfg.spread_widening_window_min
            if len(spread_series.spreads) > w30:
                widening = spread_now > spread_series.spreads[-1 - w30]
            if spread_z is not None and spread_z > cfg.spread_zscore_threshold and widening is True:
                weight_cover = True

        if guard_ratio is None and spread_z is None:
            return None

        # 维度⑧评分：0-100，按逼近/突破阈值程度单调递减（触发=0，无信号=100）
        sev_a = 0.0
        if guard_ratio is not None and advance_ratio is not None and advance_ratio < cfg.guard_breadth_low:
            sev_a = min(1.0, max(0.0, guard_ratio) / cfg.guard_ratio_threshold)
        sev_b = 0.0
        if spread_z is not None and widening is True:
            sev_b = min(1.0, max(0.0, spread_z) / cfg.spread_zscore_threshold)
        score = 100.0 * (1.0 - max(sev_a, sev_b))

        return DistortionDetectionResult(
            guard_ratio=guard_ratio,
            guard_illusion=guard_illusion,
            spread_current=spread_now,
            spread_zscore=spread_z,
            spread_widening_30m=widening,
            weight_cover=weight_cover,
            distortion_flag=guard_illusion or weight_cover,
            distortion_score=max(0.0, min(100.0, score)),
        )

    # ------------------------------------------------------------------
    # M1-⑤ 量能盘中预测（44 号 §9.4 上半）
    # ------------------------------------------------------------------
    def forecast_volume(
        self,
        volume_input: VolumeForecastInput | None,
        breadth_vel_5m: float | None,
    ) -> VolumeForecastResult | None:
        """ŷ_full=cum_vol(t)/p̄(t)；缩量警示 / 放量确认（breadth_vel>0 联动 M1-①）。"""
        if volume_input is None:
            return None
        cfg = self._config
        curve = volume_input.pct_curve
        idx = volume_input.minute_index
        if not curve or idx < 0 or idx >= len(curve):
            return None
        p_bar = curve[idx]
        if p_bar <= 0 or volume_input.avg_full_volume_20d <= 0:
            return None
        y_hat = volume_input.cum_volume / p_bar
        ratio = y_hat / volume_input.avg_full_volume_20d
        return VolumeForecastResult(
            predicted_full_volume=y_hat,
            volume_ratio=ratio,
            shrink_warning=ratio < cfg.volume_shrink_threshold,
            volume_confirm=(ratio > cfg.volume_confirm_threshold and breadth_vel_5m is not None and breadth_vel_5m > 0),
        )

    # ------------------------------------------------------------------
    # M1-⑥ 大幅回撤个股数（44 号 §9.4 下半）
    # ------------------------------------------------------------------
    def count_large_drawdowns(
        self,
        stocks: tuple[StockIntradayGain, ...] | None,
    ) -> DrawdownRiskResult | None:
        """回撤股={日内最高涨幅≥5% 且现价较最高回吐≥50%}；≥7 且最大回撤>10% → 追涨被埋警示。"""
        if stocks is None:
            return None
        cfg = self._config
        count = 0
        max_dd = 0.0
        for s in stocks:
            if s.high_gain_pct < cfg.drawdown_high_gain_min:
                continue
            pullback = (s.high_gain_pct - s.current_gain_pct) / s.high_gain_pct
            if pullback < cfg.drawdown_pullback_ratio:
                continue
            count += 1
            max_dd = max(max_dd, s.high_gain_pct - s.current_gain_pct)
        return DrawdownRiskResult(
            drawdown_count=count,
            max_drawdown_pct=max_dd,
            chase_buried_warning=(count >= cfg.drawdown_count_warn and max_dd > cfg.drawdown_max_pct_warn),
        )

    # ------------------------------------------------------------------
    # M1-⑦ 昨日破板今表现（44 号 §2 M1-⑦ + 92 号 §1 D11 实证口径）
    # ------------------------------------------------------------------
    def track_broken_boards(
        self,
        stocks: tuple[BrokenBoardStock, ...] | None,
    ) -> BrokenBoardResult | None:
        """炸板判定=昨日 high≥limit_up 且 close<limit_up；今日平均收益=承接力指标。"""
        if stocks is None:
            return None
        cfg = self._config
        broken = [
            s for s in stocks if s.yesterday_high >= s.yesterday_limit_up and s.yesterday_close < s.yesterday_limit_up
        ]
        if not broken:
            return BrokenBoardResult(
                broken_count=0,
                avg_return_today=None,
                positive_ratio=None,
                support_strength="无数据",
            )
        avg_ret = sum(s.today_return_pct for s in broken) / len(broken)
        pos_ratio = sum(1 for s in broken if s.today_return_pct > 0) / len(broken)
        if avg_ret >= cfg.broken_board_good_return:
            strength = "强"
        elif avg_ret <= cfg.broken_board_bad_return:
            strength = "弱"
        else:
            strength = "中"
        return BrokenBoardResult(
            broken_count=len(broken),
            avg_return_today=avg_ret,
            positive_ratio=pos_ratio,
            support_strength=strength,
        )

    # ------------------------------------------------------------------
    # 综合7维度分析
    # ------------------------------------------------------------------
    def analyze(self, input_data: MarketSentimentInput) -> MarketSentimentResult:
        """
        综合7维度市场情绪分析

        输入: MarketSentimentInput
        输出: MarketSentimentResult
        """
        # 1. 涨跌家数
        breadth_status, breadth_score = self.analyze_breadth(input_data.breadth)

        # 2. 涨跌停
        limit_status, limit_score = self.analyze_limit_activity(input_data.limit_data)

        # 3. 赚钱效应
        profit_status, profit_score = self.evaluate_profit_effect(input_data.breadth)

        # 4. 次日回调风险
        risk_status, risk_score = self.warn_next_day_risk(input_data.breadth, input_data.index_performance)

        # 5. 市场士气
        morale_status, morale_score = self.evaluate_morale(input_data.breadth)

        # 6. 封板率
        seal_status, seal_score, seal_rate = self.analyze_seal_rate(input_data.limit_data)

        # 7. 昨日涨停表现
        yesterday_lu_status = self.track_yesterday_limit_up(input_data.yesterday_limit_up)

        # ---- M1 增量（44 号；缺数据自动跳过不炸）----
        breadth_total = input_data.breadth.total_count or (
            input_data.breadth.advancing_count + input_data.breadth.declining_count + input_data.breadth.flat_count
        )
        advance_ratio = input_data.breadth.advancing_count / breadth_total if breadth_total else None
        accel_result = self.analyze_breadth_acceleration(
            input_data.time_series, input_data.index_performance.index_change_pct
        )
        distortion_result = self.detect_distortion(
            input_data.index_contrib,
            input_data.spread_series,
            advance_ratio,
            input_data.index_performance.index_change_pct,
        )
        volume_result = self.forecast_volume(
            input_data.volume_series,
            accel_result.breadth_vel_5m if accel_result is not None else None,
        )
        drawdown_result = self.count_large_drawdowns(input_data.drawdown_stocks)
        broken_board_result = self.track_broken_boards(input_data.broken_board_stocks)

        # 综合评分（加权平均）
        # 权重: 涨跌停20% + 赚钱效应20% + 市场士气15% + 封板率15% + 涨跌家数15% + 次日风险15%
        base_score = (
            limit_score * 0.20
            + profit_score * 0.20
            + morale_score * 0.15
            + seal_score * 0.15
            + breadth_score * 0.15
            + risk_score * 0.15
        )
        if distortion_result is not None:
            # 维度⑧接入：既有 6 分数权重按 (1-w8) 比例重归一；触发失真再 ×0.7 降权
            w8 = max(0.0, min(self._config.distortion_weight, self._config.distortion_weight_cap))
            overall_score = base_score * (1.0 - w8) + distortion_result.distortion_score * w8
            if distortion_result.distortion_flag:
                overall_score *= self._config.distortion_damp_factor
        else:
            # 维度⑧缺数据跳过 → 权重自动归一回既有 6 分数（行为与现状一致）
            overall_score = base_score

        # 情绪阶段定位
        phase = self._determine_phase(overall_score)

        return MarketSentimentResult(
            timestamp=input_data.timestamp,
            breadth_status=breadth_status,
            breadth_score=breadth_score,
            limit_zeal_status=limit_status,
            limit_score=limit_score,
            profit_effect_status=profit_status,
            profit_effect_score=profit_score,
            next_day_risk_status=risk_status,
            next_day_risk_score=risk_score,
            morale_status=morale_status,
            morale_score=morale_score,
            seal_rate_status=seal_status,
            seal_rate=seal_rate,
            yesterday_lu_status=yesterday_lu_status,
            overall_score=max(0.0, min(100.0, overall_score)),
            sentiment_phase=phase,
            breadth_acceleration=accel_result,
            distortion=distortion_result,
            volume_forecast=volume_result,
            drawdown_risk=drawdown_result,
            broken_board=broken_board_result,
        )

    def _determine_phase(self, score: float) -> str:
        """根据综合评分定位情绪阶段"""
        if score < self._config.phase_freezing_score:
            return SentimentPhase.FREEZING.value
        elif score < self._config.phase_reversal_score:
            return SentimentPhase.REVERSAL.value
        elif score < self._config.phase_main_rally_score:
            return SentimentPhase.MAIN_RALLY.value
        elif score < self._config.phase_euphoria_score:
            return SentimentPhase.EUPHORIA.value
        else:
            return SentimentPhase.RETREATING.value

    # ------------------------------------------------------------------
    # 8. 5 维灰度概率输出（23-B 升级增量方法）
    # ------------------------------------------------------------------
    def analyze_grayscale(self, input_data: MarketSentimentInput) -> MarketSentimentGrayscaleResult:
        """灰度概率分析（纯增量，不改 analyze() 硬标签链路）。

        复用 analyze() 的 overall_score，按阶段中心高斯软分配为 5 维概率
        P(冰点..退潮) Σ=1；confidence=max(P)，<60% 时 fallback_triggered=True
        （建议默认保守，对齐 30 号 §6.3 兜底纪律）。
        """
        result = self.analyze(input_data)
        score = result.overall_score
        raw = {
            phase: math.exp(-((score - center) ** 2) / (2.0 * GRAYSCALE_SIGMA**2))
            for phase, center in GRAYSCALE_PHASE_CENTERS.items()
        }
        total = sum(raw.values())
        phase_prob = {phase.value: v / total for phase, v in raw.items()}
        dominant = max(phase_prob, key=phase_prob.get)
        confidence = phase_prob[dominant]
        return MarketSentimentGrayscaleResult(
            timestamp=result.timestamp,
            phase_prob=phase_prob,
            dominant_phase=dominant,
            confidence=confidence,
            overall_score=score,
            fallback_triggered=confidence < GRAYSCALE_CONFIDENCE_FALLBACK,
        )
