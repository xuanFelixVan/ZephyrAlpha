# [BLUEPRINT] MOD-SIG-025 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_ashare.market_sentiment_analyzer
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.shared.contracts.synthesized_signal
# [CONSUMERS] zephyr.signal_ashare.youzi_relay_emotion_engine; zephyr.signal_ashare.dual_engine_fusion_decision_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] overall_sentiment_score in [0, 100]; all sub-scores in [0, 100]
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] MarketSentimentDataError
# [TESTS] tests/signal_ashare/test_market_sentiment_analyzer.py
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

设计真源: D:\临时工作区\依赖图-D-SIGNAL-信号域.md §1 D-SIGNAL-25
策略参数: 全部通过 MarketSentimentConfig 可配置，默认值取自设计文档

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
from typing import Optional


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


@dataclass(frozen=True)
class MarketSentimentInput:
    """市场情绪分析输入"""

    timestamp: datetime
    breadth: MarketBreadthData
    limit_data: LimitUpDownData
    index_performance: IndexPerformanceData
    yesterday_limit_up: YesterdayLimitUpPerformance | None = None
    market_turnover: float = 0.0  # 市场成交额（亿）


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

        # 综合评分（加权平均）
        # 权重: 涨跌停20% + 赚钱效应20% + 市场士气15% + 封板率15% + 涨跌家数15% + 次日风险15%
        overall_score = (
            limit_score * 0.20
            + profit_score * 0.20
            + morale_score * 0.15
            + seal_score * 0.15
            + breadth_score * 0.15
            + risk_score * 0.15
        )

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
