# [BLUEPRINT] MOD-SIG-023 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_ashare.short_term_stock_selector
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.institutional_behavior_analyzer; zephyr.signal_ashare.capital_flow_pattern_analyzer
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 评分卡7维权重和=100; 降级路径必须有日志
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/signal_ashare/test_short_term_stock_selector.py
# [A_module] module_id=MOD-SIG-023 | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: ashare_signal
# category: signal_analyzer
# status: active
# created: "2026-08-02"
# ---

r"""


D-SIGNAL-23 A股短线选股引擎

机构选股评分器(目标价空间40%+基本面30%+技术趋势20%+流动性10%)
+ 强庄股识别器(走势独立/换手率异常/盘口神秘大单)
+ 连板潜力评分卡(7维100分: 连板高度/封单强度/板块效应/分歧程度/市值流动性/封板时间/催化强度)
+ 连板分歧程度评估器。

理论依据：多因子选股 / 评分卡模型 / 行为金融学。

设计文档默认值可配置——所有权重和阈值通过 ShortTermStockSelectorConfig 调整，
默认值取自 D:\临时工作区\依赖图-D-SIGNAL-信号域.md §D-SIGNAL-23。

依赖方向：D-SIGNAL-21(主力行为) + D-SIGNAL-22(资金线) -> D-SIGNAL-23 -> D-SIGNAL-24(日内买卖点)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 单只股票选股输入 StockSelectionInput
#   fields: 目标价/现价/基本面分/技术趋势分/流动性分 + 大盘相关系数/换手率/大单占比 + 连板高度/封单金额/流通市值/板块热度/开板次数/封板时间/催化强度 + 上游主力阶段与资金形态上下文
#   code: StockSelectionInput L121
# - id: I2
#   name: 选股器权重阈值配置 ShortTermStockSelectorConfig
#   fields: 机构评分4维权重(40/30/20/10) + 强庄股3阈值 + 连板评分卡7维权重(和=100) + 潜力等级阈值
#   code: ShortTermStockSelectorConfig L79
# 层: 特征
# - id: F1
#   name_zh: 目标价空间评分
#   name_en: target_space_score
#   intro: 目标价相对现价的上涨空间越大分越高
#   formula: upside=(target-current)/current×100 → clamp(upside/50×100, 0, 100)（50%空间=满分）
#   code: short_term_stock_selector.py L302
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F2
#   name_zh: 封流比（封单强度）
#   name_en: seal_ratio
#   intro: 封单金额占流通市值的比例，越高说明封板越硬
#   formula: seal_ratio=seal_amount/(float_cap×10000) → 分档: ≥1%→100 / ≥0.5%→90 / ≥0.1%→60 / >0→30
#   code: short_term_stock_selector.py L415
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F3
#   name_zh: 连板高度评分
#   name_en: height_score
#   intro: 连板越多分越高，但5板以上因高位风险反降分
#   formula: 映射表{0:0, 1:40, 2:70, 3:90, 4:100, ≥5:80}
#   code: short_term_stock_selector.py L401
#   registry: factor_registry: 有FCT条目 FCT-SENT-002（分量：连板高度——情绪三件套之一，节点为分量计算步骤，§4.16.4 分量引用）
#   is_break: false
# 层: 算法
# - id: A1
#   name_zh: ① 机构选股评分器
#   name_en: score_institutional
#   intro: 目标价空间40%+基本面30%+技术趋势20%+流动性10%加权出机构评分
#   desc: 4因子各自clamp到0~100后按配置权重加权，总分clamp到0~100
#   inputs: F1 I1 I2
#   outputs: 机构评分0~100 + 4维明细
#   invariant: 4维权重和=100
# - id: A2
#   name_zh: ② 强庄股识别器
#   name_en: identify_strong_stock
#   intro: 走势独立+换手率异常+盘口神秘大单三条件累积分判强庄股
#   desc: 相关系数<0.3加35分/换手≥10%加35分/大单占比≥15%加30分，≥70强庄 ≥40普通 否则弱势
#   inputs: I1 I2
#   outputs: 强庄类型 + 置信度0~100
# - id: A3
#   name_zh: ③ 连板潜力评分卡
#   name_en: score_limitup_potential
#   intro: 7维100分评分卡衡量连板接力潜力
#   desc: 连板高度/封单强度/板块效应/分歧程度/市值流动性/封板时间/催化强度按7维权重加权
#   inputs: F2 F3 I1 I2
#   outputs: 连板评分0~100 + 7维明细 + 潜力等级
#   invariant: 7维权重和=100
# - id: A4
#   name_zh: ④ 连板分歧程度评估器
#   name_en: evaluate_divergence
#   intro: 按开板次数判断分歧度，分歧越高走势越不确定
#   desc: 无连板→无分歧；开板≥2→高分歧；开板≥1→中分歧；否则低分歧
#   inputs: I1 I2
#   outputs: 分歧度 高/中/低/无
# - id: A5
#   name_zh: ⑤ 综合评分与推荐
#   name_en: _compute_overall_score + _make_recommendation
#   intro: 机构40%+强庄30%+连板30%合成总分并给出操作建议
#   desc: overall=inst×0.4+strong×0.3+limitup×0.3；≥80且强庄→强烈推荐，≥65且非高分歧→推荐，≥45→观望，否则回避
#   inputs: A1 A2 A3 A4
#   outputs: 综合评分0~100 + 推荐意见
# 层: 输出
# - id: O1
#   name_zh: 短线选股结果 StockSelectionResult
#   name_en: StockSelectionResult
#   intro: 含机构评分/强庄类型/连板评分/分歧度/综合评分/推荐意见/审计轨迹的结果对象
#   invariant: 评分均clamp在0~100；输入非法走降级结果is_degraded=true
#   downstream: 无下游/内部使用（[CONSUMERS]为空；设计依赖方向指向D-SIGNAL-24日内买卖点）
# [/ALGO_FLOW]
#
# 边:
# I1 -.->|断点| F1
# I1 -.->|断点| F2
# I1 --> F3
# I1 --> A1
# I1 --> A2
# I1 --> A3
# I1 --> A4
# I2 --> A1
# I2 --> A2
# I2 --> A3
# I2 --> A4
# F1 --> A1
# F2 --> A3
# F3 --> A3
# A1 --> A5
# A2 --> A5
# A3 --> A5
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ============================================================================
# 枚举
# ============================================================================


class StrongStockType(str, Enum):
    """强庄股类型。"""

    STRONG_MAIN_FORCE = "强庄股"
    NORMAL = "普通"
    WEAK = "弱势"


class LimitUpPotential(str, Enum):
    """连板潜力等级。"""

    HIGH = "高潜力"
    MEDIUM = "中潜力"
    LOW = "低潜力"
    NONE = "无潜力"


# ============================================================================
# 配置
# ============================================================================


@dataclass(frozen=True)
class ShortTermStockSelectorConfig:
    """短线选股可配置阈值——默认值取自设计文档 §D-SIGNAL-23。"""

    # ── 机构选股评分器权重（和=100）──
    institutional_weight_target_space: float = 40.0  # 目标价空间
    institutional_weight_fundamental: float = 30.0  # 基本面
    institutional_weight_technical: float = 20.0  # 技术趋势
    institutional_weight_liquidity: float = 10.0  # 流动性

    # ── 强庄股识别阈值 ──
    # 走势独立：与大盘相关系数低
    independence_corr_threshold: float = 0.3  # 相关系数<0.3 = 独立
    # 换手率异常
    turnover_anomaly_min: float = 10.0  # 换手率>10% = 异常
    turnover_anomaly_max: float = 3.0  # 换手率<3% = 低活跃
    # 盘口神秘大单
    mystery_order_ratio: float = 0.15  # 大单占比>15% = 神秘大单

    # ── 连板潜力评分卡7维权重（和=100）──
    limitup_weight_height: float = 15.0  # 连板高度
    limitup_weight_seal: float = 20.0  # 封单强度
    limitup_weight_sector: float = 15.0  # 板块效应
    limitup_weight_divergence: float = 15.0  # 分歧程度
    limitup_weight_liquidity: float = 15.0  # 市值流动性
    limitup_weight_seal_time: float = 10.0  # 封板时间
    limitup_weight_catalyst: float = 10.0  # 催化强度

    # ── 连板分歧程度 ──
    # 分歧度越高 = 后续走势越不确定
    divergence_open_count_threshold: int = 2  # 开板次数>=2 = 高分歧

    # ── 潜力等级阈值 ──
    potential_high_threshold: float = 75.0
    potential_medium_threshold: float = 50.0


# ============================================================================
# 输入 / 输出
# ============================================================================


@dataclass
class StockSelectionInput:
    """短线选股输入数据（单只股票）。"""

    symbol: str

    # ── 机构选股评分器输入 ──
    target_price: float = 0.0  # 目标价
    current_price: float = 0.0  # 当前价
    fundamental_score: float = 50.0  # 基本面评分 0~100
    technical_trend_score: float = 50.0  # 技术趋势评分 0~100
    liquidity_score: float = 50.0  # 流动性评分 0~100

    # ── 强庄股识别输入 ──
    corr_with_market: float = 1.0  # 与大盘相关系数
    turnover_rate: float = 0.0  # 换手率%
    large_order_ratio: float = 0.0  # 大单占比

    # ── 连板评分卡输入 ──
    consecutive_limit_ups: int = 0  # 连板高度
    seal_order_amount: float = 0.0  # 封单金额(万元)
    float_market_cap: float = 0.0  # 流通市值(亿元)
    sector_hot_score: float = 50.0  # 板块热度 0~100
    open_board_count: int = 0  # 开板次数
    seal_time_minutes: int = 0  # 封板时间(分钟，从开盘算)
    catalyst_strength: float = 50.0  # 催化强度 0~100

    # ── 上下文（来自上游模块）──
    main_force_phase: str = "未知"  # 来自 D-SIGNAL-21
    capital_flow_pattern: str = "未知"  # 来自 D-SIGNAL-22


@dataclass
class StockSelectionResult:
    """短线选股结果。"""

    symbol: str
    # 机构选股评分
    institutional_score: float  # 0~100
    institutional_breakdown: dict[str, float]
    # 强庄股识别
    strong_stock_type: str
    strong_stock_confidence: float
    # 连板潜力评分卡
    limitup_score: float  # 0~100
    limitup_breakdown: dict[str, float]
    limitup_potential: str  # LimitUpPotential
    # 连板分歧程度
    divergence_degree: str  # "高分歧"/"中分歧"/"低分歧"/"无分歧"
    # 综合
    overall_score: float
    recommendation: str  # "强烈推荐"/"推荐"/"观望"/"回避"
    audit_trail: list[dict[str, Any]] = field(default_factory=list)
    is_degraded: bool = False


# ============================================================================
# 分析器
# ============================================================================


class ShortTermStockSelector:
    """
    A股短线选股引擎（D-SIGNAL-23）。

    3维度分析：
      1. 机构选股评分器（4因子加权）
      2. 强庄股识别器（走势独立/换手率异常/盘口神秘大单）
      3. 连板潜力评分卡（7维100分）+ 连板分歧程度评估
    """

    def __init__(self, config: ShortTermStockSelectorConfig | None = None) -> None:
        self._config = config or ShortTermStockSelectorConfig()

    # ------------------------------------------------------------------
    # 公开入口
    # ------------------------------------------------------------------

    def analyze(self, input_data: StockSelectionInput) -> StockSelectionResult:
        """执行3维度短线选股分析。"""
        if not self._validate_input(input_data):
            logger.warning("ShortTermStockSelector: 输入数据不合法，返回降级结果")
            return self._degraded_result(input_data.symbol, "输入数据校验失败")

        audit_trail: list[dict[str, Any]] = []

        # ── 维度1: 机构选股评分器 ──
        inst_score, inst_breakdown = self.score_institutional(input_data)
        audit_trail.append(
            {
                "dimension": "institutional_scoring",
                "result": inst_score,
                "breakdown": inst_breakdown,
            }
        )

        # ── 维度2: 强庄股识别 ──
        strong_type, strong_conf = self.identify_strong_stock(input_data)
        audit_trail.append(
            {
                "dimension": "strong_stock",
                "result": strong_type,
                "confidence": strong_conf,
            }
        )

        # ── 维度3: 连板潜力评分卡 ──
        lu_score, lu_breakdown = self.score_limitup_potential(input_data)
        lu_potential = self._classify_potential(lu_score)
        audit_trail.append(
            {
                "dimension": "limitup_potential",
                "result": lu_score,
                "potential": lu_potential,
                "breakdown": lu_breakdown,
            }
        )

        # ── 连板分歧程度 ──
        divergence = self.evaluate_divergence(input_data)
        audit_trail.append(
            {
                "dimension": "divergence",
                "result": divergence,
            }
        )

        # ── 综合评分 + 推荐 ──
        overall = self._compute_overall_score(inst_score, strong_type, strong_conf, lu_score, lu_potential)
        recommendation = self._make_recommendation(overall, strong_type, lu_potential, divergence)

        return StockSelectionResult(
            symbol=input_data.symbol,
            institutional_score=inst_score,
            institutional_breakdown=inst_breakdown,
            strong_stock_type=strong_type,
            strong_stock_confidence=strong_conf,
            limitup_score=lu_score,
            limitup_breakdown=lu_breakdown,
            limitup_potential=lu_potential,
            divergence_degree=divergence,
            overall_score=overall,
            recommendation=recommendation,
            audit_trail=audit_trail,
        )

    # ------------------------------------------------------------------
    # 维度1: 机构选股评分器
    # ------------------------------------------------------------------

    def score_institutional(self, input_data: StockSelectionInput) -> tuple[float, dict[str, float]]:
        """
        机构选股评分器：目标价空间40% + 基本面30% + 技术趋势20% + 流动性10%。

        返回(综合评分0~100, 各因子明细)。
        """
        cfg = self._config

        # 目标价空间评分
        target_space_score = self._score_target_space(input_data.target_price, input_data.current_price)
        # 基本面评分
        fundamental_score = max(0.0, min(100.0, input_data.fundamental_score))
        # 技术趋势评分
        technical_score = max(0.0, min(100.0, input_data.technical_trend_score))
        # 流动性评分
        liquidity_score = max(0.0, min(100.0, input_data.liquidity_score))

        breakdown = {
            "目标价空间": round(target_space_score, 2),
            "基本面": round(fundamental_score, 2),
            "技术趋势": round(technical_score, 2),
            "流动性": round(liquidity_score, 2),
        }

        overall = (
            target_space_score * cfg.institutional_weight_target_space / 100.0
            + fundamental_score * cfg.institutional_weight_fundamental / 100.0
            + technical_score * cfg.institutional_weight_technical / 100.0
            + liquidity_score * cfg.institutional_weight_liquidity / 100.0
        )
        return round(min(max(overall, 0.0), 100.0), 2), breakdown

    def _score_target_space(self, target: float, current: float) -> float:
        """目标价空间评分：上涨空间越大分越高。"""
        if current <= 0 or target <= 0:
            return 0.0
        upside = (target - current) / current * 100.0
        # 0%→0分, 50%→100分（线性映射，封顶100）
        return min(max(upside / 50.0 * 100.0, 0.0), 100.0)

    # ------------------------------------------------------------------
    # 维度2: 强庄股识别器
    # ------------------------------------------------------------------

    def identify_strong_stock(self, input_data: StockSelectionInput) -> tuple[str, float]:
        """
        强庄股识别器：走势独立 + 换手率异常 + 盘口神秘大单。

        返回(类型, 置信度0~100)。
        """
        cfg = self._config
        score = 0.0

        # 走势独立：与大盘相关系数低
        if input_data.corr_with_market < cfg.independence_corr_threshold:
            score += 35.0
        elif input_data.corr_with_market < 0.5:
            score += 15.0

        # 换手率异常：高位换手=主力活动
        if input_data.turnover_rate >= cfg.turnover_anomaly_min:
            score += 35.0
        elif input_data.turnover_rate >= 5.0:
            score += 20.0

        # 盘口神秘大单
        if input_data.large_order_ratio >= cfg.mystery_order_ratio:
            score += 30.0
        elif input_data.large_order_ratio >= 0.08:
            score += 15.0

        score = min(score, 100.0)

        if score >= 70.0:
            return StrongStockType.STRONG_MAIN_FORCE.value, score
        if score >= 40.0:
            return StrongStockType.NORMAL.value, score
        return StrongStockType.WEAK.value, score

    # ------------------------------------------------------------------
    # 维度3: 连板潜力评分卡
    # ------------------------------------------------------------------

    def score_limitup_potential(self, input_data: StockSelectionInput) -> tuple[float, dict[str, float]]:
        """
        连板潜力评分卡：7维100分。

        7维：连板高度/封单强度/板块效应/分歧程度/市值流动性/封板时间/催化强度。
        返回(总分0~100, 各维明细)。
        """
        cfg = self._config

        # 1. 连板高度（连板越多分越高，但高位板风险也高）
        height_score = self._score_consecutive_height(input_data.consecutive_limit_ups)
        # 2. 封单强度（封流比）
        seal_score = self._score_seal_strength(input_data.seal_order_amount, input_data.float_market_cap)
        # 3. 板块效应
        sector_score = max(0.0, min(100.0, input_data.sector_hot_score))
        # 4. 分歧程度（开板次数越少越好；无连板时该维度不适用 → 0 分）
        if input_data.consecutive_limit_ups == 0:
            divergence_score = 0.0
        else:
            divergence_score = self._score_divergence(input_data.open_board_count)
        # 5. 市值流动性（中小市值=高分）
        liquidity_score = self._score_market_liquidity(input_data.float_market_cap)
        # 6. 封板时间（越早封板=越强）
        seal_time_score = self._score_seal_time(input_data.seal_time_minutes)
        # 7. 催化强度
        catalyst_score = max(0.0, min(100.0, input_data.catalyst_strength))

        breakdown = {
            "连板高度": round(height_score, 2),
            "封单强度": round(seal_score, 2),
            "板块效应": round(sector_score, 2),
            "分歧程度": round(divergence_score, 2),
            "市值流动性": round(liquidity_score, 2),
            "封板时间": round(seal_time_score, 2),
            "催化强度": round(catalyst_score, 2),
        }

        total = (
            height_score * cfg.limitup_weight_height / 100.0
            + seal_score * cfg.limitup_weight_seal / 100.0
            + sector_score * cfg.limitup_weight_sector / 100.0
            + divergence_score * cfg.limitup_weight_divergence / 100.0
            + liquidity_score * cfg.limitup_weight_liquidity / 100.0
            + seal_time_score * cfg.limitup_weight_seal_time / 100.0
            + catalyst_score * cfg.limitup_weight_catalyst / 100.0
        )
        return round(min(max(total, 0.0), 100.0), 2), breakdown

    def _score_consecutive_height(self, count: int) -> float:
        """连板高度评分：1板=40, 2板=70, 3板=90, 4板=100, 5板+=80(高位风险)。"""
        mapping = {0: 0, 1: 40, 2: 70, 3: 90, 4: 100}
        if count in mapping:
            return float(mapping[count])
        if count >= 5:
            return 80.0  # 高位板风险
        return 0.0

    def _score_seal_strength(self, seal_amount: float, float_cap: float) -> float:
        """封单强度评分：封流比(封单/流通市值)越高分越高。"""
        if float_cap <= 0:
            return 0.0
        # 封流比 = 封单金额(万元) / 流通市值(亿元) / 10000 (单位转换)
        seal_ratio = seal_amount / (float_cap * 10000.0) if float_cap > 0 else 0.0
        # 封流比 0.1%=60分, 0.5%=90分, 1%+=100分
        if seal_ratio >= 0.01:
            return 100.0
        if seal_ratio >= 0.005:
            return 90.0
        if seal_ratio >= 0.001:
            return 60.0
        if seal_ratio > 0:
            return 30.0
        return 0.0

    def _score_divergence(self, open_count: int) -> float:
        """分歧程度评分：开板次数越少分越高。"""
        mapping = {0: 100, 1: 70, 2: 40, 3: 20}
        return float(mapping.get(open_count, 10.0))

    def _score_market_liquidity(self, float_cap: float) -> float:
        """市值流动性评分：中小市值(20~100亿)分最高。"""
        if float_cap <= 0:
            return 0.0
        if 20 <= float_cap <= 100:
            return 100.0
        if 10 <= float_cap < 20:
            return 80.0
        if 100 < float_cap <= 300:
            return 70.0
        if float_cap < 10:
            return 60.0
        return 40.0  # 大市值

    def _score_seal_time(self, minutes: int) -> float:
        """封板时间评分：越早封板分越高。"""
        if minutes <= 0:
            return 0.0
        if minutes <= 5:  # 开盘即封
            return 100.0
        if minutes <= 30:  # 9:30-10:00
            return 85.0
        if minutes <= 90:  # 10:00-11:00
            return 70.0
        if minutes <= 240:  # 11:00-13:30
            return 50.0
        if minutes <= 300:  # 13:30-14:30
            return 30.0
        return 15.0  # 14:30后封板

    # ------------------------------------------------------------------
    # 连板分歧程度评估器
    # ------------------------------------------------------------------

    def evaluate_divergence(self, input_data: StockSelectionInput) -> str:
        """
        连板分歧程度评估：基于开板次数判断分歧度。

        高分歧=后续走势不确定，中分歧=有争议，低分歧=一致看好，无分歧=无连板。
        """
        cfg = self._config
        if input_data.consecutive_limit_ups == 0:
            return "无分歧"
        if input_data.open_board_count >= cfg.divergence_open_count_threshold:
            return "高分歧"
        if input_data.open_board_count >= 1:
            return "中分歧"
        return "低分歧"

    # ------------------------------------------------------------------
    # 综合评分 + 推荐
    # ------------------------------------------------------------------

    def _classify_potential(self, score: float) -> str:
        cfg = self._config
        if score >= cfg.potential_high_threshold:
            return LimitUpPotential.HIGH.value
        if score >= cfg.potential_medium_threshold:
            return LimitUpPotential.MEDIUM.value
        if score > 0:
            return LimitUpPotential.LOW.value
        return LimitUpPotential.NONE.value

    def _compute_overall_score(
        self,
        inst_score: float,
        strong_type: str,
        strong_conf: float,
        lu_score: float,
        lu_potential: str,
    ) -> float:
        """综合评分(0~100)——机构评分40% + 强庄度30% + 连板潜力30%。"""
        strong_norm = strong_conf  # 0~100
        score = inst_score * 0.40 + strong_norm * 0.30 + lu_score * 0.30
        return round(min(max(score, 0.0), 100.0), 2)

    def _make_recommendation(
        self,
        overall: float,
        strong_type: str,
        lu_potential: str,
        divergence: str,
    ) -> str:
        """生成推荐意见。"""
        if overall >= 80 and strong_type == StrongStockType.STRONG_MAIN_FORCE.value:
            return "强烈推荐"
        if overall >= 65 and divergence != "高分歧":
            return "推荐"
        if overall >= 45:
            return "观望"
        return "回避"

    # ------------------------------------------------------------------
    # 辅助
    # ------------------------------------------------------------------

    def _validate_input(self, data: StockSelectionInput) -> bool:
        if not data.symbol:
            return False
        if data.current_price < 0:
            return False
        return True

    def _degraded_result(self, symbol: str, reason: str) -> StockSelectionResult:
        return StockSelectionResult(
            symbol=symbol,
            institutional_score=0.0,
            institutional_breakdown={},
            strong_stock_type=StrongStockType.WEAK.value,
            strong_stock_confidence=0.0,
            limitup_score=0.0,
            limitup_breakdown={},
            limitup_potential=LimitUpPotential.NONE.value,
            divergence_degree="无分歧",
            overall_score=0.0,
            recommendation="回避",
            is_degraded=True,
            audit_trail=[{"dimension": "degraded", "reason": reason}],
        )


__all__ = [
    "LimitUpPotential",
    "ShortTermStockSelector",
    "ShortTermStockSelectorConfig",
    "StockSelectionInput",
    "StockSelectionResult",
    "StrongStockType",
]
