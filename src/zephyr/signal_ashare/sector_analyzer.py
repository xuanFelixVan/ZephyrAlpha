# [BLUEPRINT] MOD-SIG-026 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_ashare.sector_analyzer
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS] zephyr.signal_ashare.quant_short_term_strength_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] strength_score in [0, 100]; all sub-scores in [0, 100]
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SectorDataError
# [TESTS] tests/signal_ashare/test_sector_analyzer.py
# [A_module] module_id=MOD-SIG-026 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""


D-SIGNAL-26 — A股板块分析引擎

6维度板块分析：
  1. 板块强度评估（涨停数量/梯队完整性/板块指数趋势）
  2. 板块延续性判断（短期题材vs趋势题材/政策持续时间/资金介入深度）
  3. 板块轮动预警（连续大涨+放量+龙头滞涨→切换）
  4. 板块启动条件评估（技术突破+政策支持+订单落地）
  5. 大盘成交额风格适配（大成交→趋势票/小成交→妖股）
  6. 抱团瓦解切换信号检测

设计真源: D:\临时工作区\依赖图-D-SIGNAL-信号域.md §1 D-SIGNAL-26
策略参数: 全部通过 SectorAnalysisConfig 可配置，默认值取自设计文档

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 板块数据 SectorData数据类
#   fields: 涨停数 + 总股数 + 二板/三板数 + 板块指数涨跌幅 + 成交量变化 + 连续上涨天数 + 连续放量天数 + 龙头涨跌幅 + 龙头是否滞涨 + 净流入(亿) + 政策支持 + 订单落地 + 技术突破
#   code: SectorData L67-L93
# - id: I2
#   name: 大盘成交额 标量
#   fields: market_turnover 全市场成交额(万亿) 默认1.0
#   code: analyze() L337 参数
# 层: 算法
# - id: A1
#   name_zh: ① 板块强度评估
#   name_en: evaluate_strength
#   intro: 涨停数量+梯队完整性+板块指数趋势三项加评估板块强不强
#   desc: 涨停≥5→40分 ≥1→20分; 有三板→30 有二板→20; 指数涨≥3%→30 ≥0→15; 满分100 ≥70强 ≥40中 否则弱
#   inputs: I1
#   outputs: strength_status + strength_score
# - id: A2
#   name_zh: ② 板块延续性判断
#   name_en: judge_continuity
#   intro: 按连涨天数和资金深度区分短期题材还是趋势题材
#   desc: 连涨≥5天→趋势题材 60+(天数-5)×5; ≤3天→短期题材 30+天数×5; 净流入≥10亿+10分
#   inputs: I1
#   outputs: theme_type + continuity_score
# - id: A3
#   name_zh: ③ 板块轮动预警
#   name_en: warn_rotation
#   intro: 连续大涨+放量+龙头滞涨三信号叠加 预警资金要切换板块
#   desc: 连涨≥3天+30 连续放量≥2天+30 龙头滞涨+40 总分≥60触发预警
#   inputs: I1
#   outputs: rotation_warning + rotation_score
# - id: A4
#   name_zh: ④ 板块启动条件评估
#   name_en: evaluate_launch_conditions
#   intro: 技术突破+政策支持为必须条件 全满足才算启动就绪
#   desc: 技术突破+40 政策支持+35 订单落地+25(配置非必须) 净流入>0+10 ready=必须条件全满足
#   inputs: I1
#   outputs: launch_ready + launch_score
# - id: A5
#   name_zh: ⑤ 大盘成交额风格适配
#   name_en: adapt_market_style
#   intro: 成交额大做趋势票 成交额小出妖股
#   desc: ≥1.5万亿→趋势票 ≤0.8万亿→妖股 中间→混合
#   inputs: I2
#   outputs: market_style
# - id: A6
#   name_zh: ⑥ 抱团瓦解信号检测
#   name_en: detect_breakdown
#   intro: 龙头大跌伴随放量 或板块指数大跌 判定抱团瓦解
#   desc: 龙头跌≥5% 且 放量≥2倍 → True; 板块指数跌≥5% → True
#   inputs: I1
#   outputs: breakdown_signal 布尔
# - id: A7
#   name_zh: ⑦ 综合评分与板块状态判定
#   name_en: analyze + _determine_status
#   intro: 6维分数加权成综合分 再按优先级定位6种板块状态
#   desc: overall=强度×0.30+延续×0.20+启动×0.20+(100-轮动)×0.15+(瓦解?0:100)×0.15; 状态 瓦解→轮动(预警+强度≥70)→启动(就绪+强度<40)→高潮(≥90)/加速(≥70)/休眠(<20)
#   inputs: A1 A2 A3 A4 A5 A6
#   outputs: sector_status + overall_score
# 层: 输出
# - id: O1
#   name_zh: 板块分析结果
#   name_en: SectorAnalysisResult
#   intro: 6维状态与评分+板块状态+综合分 一次输出
#   invariant: strength_score in [0,100]; all sub-scores in [0,100]
#   downstream: 量化短线强度引擎 MOD-SIG-034
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I1 --> A3
# I1 --> A4
# I1 --> A6
# I2 --> A5
# A1 --> A7
# A2 --> A7
# A3 --> A7
# A4 --> A7
# A5 --> A7
# A6 --> A7
# A7 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Optional


class SectorTheme(str, Enum):
    """板块题材类型"""

    SHORT_TERM = "短期题材"
    TREND = "趋势题材"


class MarketStyle(str, Enum):
    """大盘成交额风格"""

    TREND = "趋势票"
    MIXED = "混合"
    MONSTER = "妖股"


class SectorStatus(str, Enum):
    """板块状态"""

    LAUNCHING = "启动"
    ACCELERATING = "加速"
    PEAK = "高潮"
    ROTATING = "轮动"
    COLLAPSING = "瓦解"
    DORMANT = "休眠"


@dataclass(frozen=True)
class SectorData:
    """板块数据"""

    sector_name: str
    # 涨停数据
    limit_up_count: int  # 板块内涨停数量
    total_stocks: int  # 板块总股票数
    # 梯队数据
    tier2_count: int  # 二板数量
    tier3_count: int  # 三板数量
    # 板块指数
    sector_index_change_pct: float  # 板块指数涨跌幅
    sector_index_volume_change_pct: float  # 成交量变化
    # 连续表现
    consecutive_up_days: int  # 连续上涨天数
    consecutive_volume_up_days: int  # 连续放量天数
    # 龙头表现
    leader_change_pct: float  # 龙头股涨跌幅
    leader_lagging: bool  # 龙头是否滞涨
    # 资金
    net_inflow: float  # 净流入金额（亿）
    # 政策/事件
    has_policy_support: bool  # 是否有政策支持
    has_order_landing: bool  # 是否有订单落地
    # 技术面
    technical_breakout: bool  # 是否技术突破


@dataclass
class SectorAnalysisConfig:
    """板块分析配置（全部可配置，默认值取自设计文档）"""

    # 板块强度阈值
    strong_limit_up_count: int = 5  # 涨停>5=强
    weak_limit_up_count: int = 1  # 涨停<1=弱
    strong_tier_completeness: int = 3  # 有3级以上梯队=完整

    # 板块指数趋势阈值
    strong_index_change: float = 0.03  # 涨幅>3%=强
    weak_index_change: float = -0.02  # 跌幅>2%=弱

    # 延续性判断
    short_term_max_days: int = 3  # 连续上涨<3天=短期题材
    trend_min_days: int = 5  # 连续上涨>5天=趋势题材
    deep_inflow_threshold: float = 10.0  # 净流入>10亿=深度介入

    # 轮动预警阈值
    rotation_consecutive_up: int = 3  # 连续大涨3天
    rotation_volume_up: int = 2  # 连续放量2天
    # 龙头滞涨即触发轮动预警

    # 启动条件
    launch_needs_breakthrough: bool = True
    launch_needs_policy: bool = True
    launch_needs_order: bool = False  # 订单落地非必须

    # 大盘成交额风格适配
    trend_turnover_threshold: float = 1.5  # >1.5万亿=趋势票
    monster_turnover_threshold: float = 0.8  # <8000亿=妖股

    # 抱团瓦解信号
    breakdown_leader_drop: float = -0.05  # 龙头跌>5%=瓦解信号
    breakdown_volume_surge: float = 2.0  # 放量>2倍=瓦解信号


@dataclass(frozen=True)
class SectorAnalysisResult:
    """板块分析结果"""

    sector_name: str
    timestamp: datetime

    # 1. 板块强度
    strength_status: str  # "强"/"中"/"弱"
    strength_score: float  # 0-100

    # 2. 延续性
    theme_type: str  # SectorTheme enum value
    continuity_score: float  # 0-100

    # 3. 轮动预警
    rotation_warning: bool  # 是否有轮动预警
    rotation_score: float  # 0-100 (越高越可能轮动)

    # 4. 启动条件
    launch_ready: bool  # 是否满足启动条件
    launch_score: float  # 0-100

    # 5. 风格适配
    market_style: str  # MarketStyle enum value

    # 6. 抱团瓦解
    breakdown_signal: bool  # 是否有瓦解信号

    # 综合
    sector_status: str  # SectorStatus enum value
    overall_score: float  # 0-100


class SectorDataError(Exception):
    """板块数据不完整错误"""


class SectorAnalyzer:
    """
    A股板块分析引擎（D-SIGNAL-26）

    6维度分析 → 综合板块状态评估

    所有策略参数通过 config 可配置，默认值取自设计文档。
    """

    def __init__(self, config: SectorAnalysisConfig | None = None) -> None:
        self._config = config or SectorAnalysisConfig()

    # ------------------------------------------------------------------
    # 1. 板块强度评估
    # ------------------------------------------------------------------
    def evaluate_strength(self, data: SectorData) -> tuple[str, float]:
        """评估板块强度（涨停数量+梯队完整性+板块指数趋势）"""
        score = 0.0

        # 涨停数量
        if data.limit_up_count >= self._config.strong_limit_up_count:
            score += 40.0
        elif data.limit_up_count >= self._config.weak_limit_up_count:
            score += 20.0
        else:
            score += 5.0

        # 梯队完整性（有三板=完整梯队）
        max_tier = max(data.tier2_count > 0, data.tier3_count > 0)
        if data.tier3_count > 0:
            score += 30.0  # 有三板=梯队完整
        elif data.tier2_count > 0:
            score += 20.0  # 有二板=梯队较完整
        else:
            score += 10.0

        # 板块指数趋势
        if data.sector_index_change_pct >= self._config.strong_index_change:
            score += 30.0
        elif data.sector_index_change_pct >= 0:
            score += 15.0
        elif data.sector_index_change_pct >= self._config.weak_index_change:
            score += 5.0
        else:
            score += 0.0

        score = max(0.0, min(100.0, score))

        if score >= 70:
            status = "强"
        elif score >= 40:
            status = "中"
        else:
            status = "弱"

        return status, score

    # ------------------------------------------------------------------
    # 2. 板块延续性判断
    # ------------------------------------------------------------------
    def judge_continuity(self, data: SectorData) -> tuple[str, float]:
        """判断板块延续性（短期题材vs趋势题材）"""
        days = data.consecutive_up_days
        inflow = data.net_inflow

        if days >= self._config.trend_min_days:
            theme = SectorTheme.TREND.value
            score = 60.0 + min(40.0, (days - self._config.trend_min_days) * 5)
        elif days <= self._config.short_term_max_days:
            theme = SectorTheme.SHORT_TERM.value
            score = 30.0 + days * 5
        else:
            theme = SectorTheme.SHORT_TERM.value
            score = 40.0 + (days - self._config.short_term_max_days) * 5

        # 资金介入深度加分
        if inflow >= self._config.deep_inflow_threshold:
            score += 10.0

        return theme, max(0.0, min(100.0, score))

    # ------------------------------------------------------------------
    # 3. 板块轮动预警
    # ------------------------------------------------------------------
    def warn_rotation(self, data: SectorData) -> tuple[bool, float]:
        """轮动预警（连续大涨+放量+龙头滞涨→切换）"""
        score = 0.0

        # 连续大涨
        if data.consecutive_up_days >= self._config.rotation_consecutive_up:
            score += 30.0

        # 连续放量
        if data.consecutive_volume_up_days >= self._config.rotation_volume_up:
            score += 30.0

        # 龙头滞涨
        if data.leader_lagging:
            score += 40.0

        warning = score >= 60.0
        return warning, max(0.0, min(100.0, score))

    # ------------------------------------------------------------------
    # 4. 板块启动条件评估
    # ------------------------------------------------------------------
    def evaluate_launch_conditions(self, data: SectorData) -> tuple[bool, float]:
        """评估板块启动条件（技术突破+政策支持+订单落地）"""
        score = 0.0
        conditions_met = 0
        conditions_needed = 0

        if self._config.launch_needs_breakthrough:
            conditions_needed += 1
            if data.technical_breakout:
                conditions_met += 1
                score += 40.0

        if self._config.launch_needs_policy:
            conditions_needed += 1
            if data.has_policy_support:
                conditions_met += 1
                score += 35.0

        if self._config.launch_needs_order:
            conditions_needed += 1
            if data.has_order_landing:
                conditions_met += 1
                score += 25.0

        # 资金流入加分
        if data.net_inflow > 0:
            score += 10.0

        ready = conditions_met == conditions_needed and conditions_needed > 0
        return ready, max(0.0, min(100.0, score))

    # ------------------------------------------------------------------
    # 5. 大盘成交额风格适配
    # ------------------------------------------------------------------
    def adapt_market_style(self, market_turnover: float) -> str:
        """大盘成交额风格适配（大成交→趋势票/小成交→妖股）"""
        if market_turnover >= self._config.trend_turnover_threshold:
            return MarketStyle.TREND.value
        elif market_turnover <= self._config.monster_turnover_threshold:
            return MarketStyle.MONSTER.value
        else:
            return MarketStyle.MIXED.value

    # ------------------------------------------------------------------
    # 6. 抱团瓦解切换信号检测
    # ------------------------------------------------------------------
    def detect_breakdown(self, data: SectorData) -> bool:
        """检测抱团瓦解信号"""
        # 龙头大跌 + 放量
        if data.leader_change_pct <= self._config.breakdown_leader_drop:
            if data.sector_index_volume_change_pct >= self._config.breakdown_volume_surge:
                return True
        # 板块指数大跌
        if data.sector_index_change_pct <= self._config.breakdown_leader_drop:
            return True
        return False

    # ------------------------------------------------------------------
    # 综合6维度分析
    # ------------------------------------------------------------------
    def analyze(self, data: SectorData, market_turnover: float = 1.0) -> SectorAnalysisResult:
        """
        综合6维度板块分析

        输入: SectorData + market_turnover
        输出: SectorAnalysisResult
        """
        # 1. 板块强度
        strength_status, strength_score = self.evaluate_strength(data)

        # 2. 延续性
        theme_type, continuity_score = self.judge_continuity(data)

        # 3. 轮动预警
        rotation_warning, rotation_score = self.warn_rotation(data)

        # 4. 启动条件
        launch_ready, launch_score = self.evaluate_launch_conditions(data)

        # 5. 风格适配
        market_style = self.adapt_market_style(market_turnover)

        # 6. 抱团瓦解
        breakdown = self.detect_breakdown(data)

        # 综合状态判定
        overall_score = (
            strength_score * 0.30
            + continuity_score * 0.20
            + launch_score * 0.20
            + (100 - rotation_score) * 0.15
            + (0 if breakdown else 100) * 0.15
        )

        status = self._determine_status(
            strength_score,
            rotation_warning=rotation_warning,
            breakdown=breakdown,
            launch_ready=launch_ready,
        )

        return SectorAnalysisResult(
            sector_name=data.sector_name,
            timestamp=datetime.now(UTC),
            strength_status=strength_status,
            strength_score=strength_score,
            theme_type=theme_type,
            continuity_score=continuity_score,
            rotation_warning=rotation_warning,
            rotation_score=rotation_score,
            launch_ready=launch_ready,
            launch_score=launch_score,
            market_style=market_style,
            breakdown_signal=breakdown,
            sector_status=status,
            overall_score=max(0.0, min(100.0, overall_score)),
        )

    def _determine_status(
        self,
        strength_score: float,
        *,
        rotation_warning: bool,
        breakdown: bool,
        launch_ready: bool,
    ) -> str:
        """根据各维度评分判定板块状态"""
        if breakdown:
            return SectorStatus.COLLAPSING.value
        if rotation_warning and strength_score >= 70:
            return SectorStatus.ROTATING.value
        if launch_ready and strength_score < 40:
            return SectorStatus.LAUNCHING.value
        if strength_score >= 70:
            if strength_score >= 90:
                return SectorStatus.PEAK.value
            return SectorStatus.ACCELERATING.value
        if strength_score < 20:
            return SectorStatus.DORMANT.value
        return SectorStatus.ACCELERATING.value
