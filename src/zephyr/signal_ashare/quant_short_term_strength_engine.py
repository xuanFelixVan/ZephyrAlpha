# [BLUEPRINT] MOD-SIG-034 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_ashare.quant_short_term_strength_engine
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS] zephyr.signal_ashare.dual_engine_fusion_decision_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 6维度评分满分100; A~E五级评级单调; 降级路径必须有日志
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/signal_ashare/test_quant_short_term_strength_engine.py
# [A_module] module_id=MOD-SIG-034 | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: ashare_signal
# category: signal_analyzer
# status: active
# created: "2026-08-02"
# ---

r"""


D-SIGNAL-34 A股量化短线强度引擎

量化短线6维度0-100分评分(价格动量Z-score+行业强度+相对强度+资金+技术+风险)
+ A~E五级评级 + 6类输出(主升龙头/二进三/跟风/复苏/伪强/地天反包)。

与游资引擎(D-SIGNAL-33)双引擎融合：基准权重60%游资+40%量化，动态权重可调。

理论依据：多因子模型 / 评分卡 / 集成学习。

设计文档默认值可配置——所有阈值通过 QuantStrengthConfig 调整，
默认值取自 D:\临时工作区\依赖图-D-SIGNAL-信号域.md §D-SIGNAL-34。

依赖方向：D_DATA(行情数据) -> D-SIGNAL-34 -> D-SIGNAL-35(双引擎融合决策)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 量化强度输入 QuantStrengthInput数据类
#   fields: 价格动量Z-score + 行业当日涨幅% + 个股涨幅% + 大盘涨幅% + 主力净流入(元) + 流通市值(元) + 技术形态综合分0-100 + 风险评分0-100
#   code: QuantStrengthInput L157-L178
# - id: I2
#   name: 游资侧融合输入 标量参数组
#   fields: youzi_emotion_score 游资情绪评分(来自D-SIGNAL-33) + 连板数 + 是否主线龙头
#   code: QuantStrengthInput L181-L183
# 层: 特征
# - id: F1
#   name_zh: 相对强度
#   name_en: rs
#   intro: 个股涨幅比大盘涨幅强多少个百分点
#   formula: rs=个股涨幅%-大盘涨幅% ≥5%满分 ≥3%得15分 ≥1%得8分
#   code: quant_short_term_strength_engine.py L338
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F2
#   name_zh: 净流入比
#   name_en: capital_inflow_ratio
#   intro: 主力净流入占流通市值的比例
#   formula: ratio=主力净流入/流通市值 ≥5%满分 ≥2%得11分 ≥0得6分
#   code: quant_short_term_strength_engine.py L365
#   registry: factor_registry: 无FCT条目
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① 6维度分项评分与总分合成
#   name_en: analyze + score_* 系列
#   intro: 动量/行业/相对/资金/技术/风险6维各按阈值打分再加总
#   desc: 动量Z满分20(Z≥2满分 ≥1得15 ≥0得8) 行业满分15 相对满分20 资金满分15 技术满分20(≥80满分) 风险满分10反向(≤20满分) total=min(Σ6维,100)
#   inputs: I1 F1 F2
#   outputs: total_score + 6维 DimensionScore 明细
#   invariant: 6维度评分满分100
# - id: A2
#   name_zh: ② A~E五级评级
#   name_en: determine_grade
#   intro: 把总分单调映射到A极强到E极弱5档
#   desc: ≥80→A ≥65→B ≥50→C ≥35→D 否则→E
#   inputs: A1
#   outputs: grade A~E
#   invariant: A~E五级评级单调
# - id: A3
#   name_zh: ③ 6类输出分类
#   name_en: classify_category
#   intro: 结合量化总分+游资情绪+连板+主线 把股票分进6+1类
#   desc: 地天反包(1板+涨≥9.5%+风险≥60)→主升龙头(量化≥80+游资≥70+主线)→二进三(量化≥65+连板≥2)→复苏(量化≥70+游资40-65)→伪强(游资≥60+量化<50)→跟风(量化50-65+游资40-65)→中性
#   inputs: I1 I2 A1
#   outputs: category 6+1类标签
# 层: 输出
# - id: O1
#   name_zh: 量化短线强度结果
#   name_en: QuantStrengthResult
#   intro: 综合强度分+6维明细+A~E评级+6类分类 供双引擎融合消费
#   invariant: 6维度评分满分100 降级路径必须有日志
#   downstream: 双引擎融合决策引擎 MOD-SIG-035
# [/ALGO_FLOW]
#
# 边:
# I1 -.->|断点| F1
# I1 -.->|断点| F2
# I1 --> A1
# F1 --> A1
# F2 --> A1
# A1 --> A2
# A1 --> A3
# I1 --> A3
# I2 --> A3
# A1 --> O1
# A2 --> O1
# A3 --> O1
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


class StrengthGrade(str, Enum):
    """A~E五级评级。"""

    A = "A"  # 极强(80-100)
    B = "B"  # 强(65-80)
    C = "C"  # 中(50-65)
    D = "D"  # 弱(35-50)
    E = "E"  # 极弱(0-35)


class StockCategory(str, Enum):
    """6类输出——量化短线强度分类。"""

    MAIN_LEADER = "主升龙头"  # 量化强+游资强+主线
    SECOND_TO_THIRD = "二进三"  # 量化强+连板晋级
    FOLLOWER = "跟风"  # 量化中+游资中
    RECOVERY = "复苏"  # 量化高+游资中(老龙头反抽)
    FAKE_STRONG = "伪强"  # 游资高+量化低(禁追)
    INVERSE_BOARD = "地天反包"  # 极端反转形态
    NEUTRAL = "中性"  # 无法分类


# ============================================================================
# 配置（设计文档默认值，可配置）
# ============================================================================


@dataclass(frozen=True)
class QuantStrengthConfig:
    """量化短线强度引擎可配置阈值——默认值取自设计文档 §D-SIGNAL-34。"""

    # ── 维度1: 价格动量Z-score (满分20) ──
    momentum_z_excellent: float = 2.0  # Z>=2 → 满分
    momentum_z_good: float = 1.0  # Z>=1 → 15分
    momentum_z_fair: float = 0.0  # Z>=0 → 8分
    momentum_max_score: float = 20.0

    # ── 维度2: 行业强度 (满分15) ──
    # 个股所属行业当日涨幅
    sector_change_excellent: float = 3.0  # 行业涨>=3% → 满分
    sector_change_good: float = 1.5  # >=1.5% → 11分
    sector_change_fair: float = 0.0  # >=0% → 6分
    sector_max_score: float = 15.0

    # ── 维度3: 相对强度 (满分20) ──
    # 个股涨幅 vs 大盘涨幅
    relative_strength_excellent: float = 5.0  # 超大盘>=5% → 满分
    relative_strength_good: float = 3.0  # >=3% → 15分
    relative_strength_fair: float = 1.0  # >=1% → 8分
    relative_strength_max_score: float = 20.0

    # ── 维度4: 资金 (满分15) ──
    # 主力净流入/流通市值
    capital_inflow_excellent: float = 0.05  # >=5% → 满分
    capital_inflow_good: float = 0.02  # >=2% → 11分
    capital_inflow_fair: float = 0.0  # >=0% → 6分
    capital_max_score: float = 15.0

    # ── 维度5: 技术 (满分20) ──
    # 技术形态综合分(MACD+KDJ+均线+量价)
    technical_excellent: float = 80.0  # >=80 → 满分
    technical_good: float = 60.0  # >=60 → 15分
    technical_fair: float = 40.0  # >=40 → 8分
    technical_max_score: float = 20.0

    # ── 维度6: 风险 (满分10) ──
    # 风险分越低越好（反向评分）
    risk_score_excellent: float = 20.0  # 风险<=20 → 满分
    risk_score_good: float = 40.0  # <=40 → 7分
    risk_score_fair: float = 60.0  # <=60 → 4分
    risk_max_score: float = 10.0

    # ── 评级阈值 ──
    grade_a_min: float = 80.0
    grade_b_min: float = 65.0
    grade_c_min: float = 50.0
    grade_d_min: float = 35.0
    # <35 → E

    # ── 6类输出阈值 ──
    # 主升龙头: 量化>=80 + 游资>=70 + 是主线
    main_leader_quant_min: float = 80.0
    main_leader_youzi_min: float = 70.0
    # 二进三: 量化>=65 + 连板数>=2
    second_to_third_quant_min: float = 65.0
    # 跟风: 量化50-65 + 游资40-65
    follower_quant_min: float = 50.0
    follower_quant_max: float = 65.0
    # 复苏: 量化>=70 + 游资40-65
    recovery_quant_min: float = 70.0
    # 伪强: 游资>=60 + 量化<50
    fake_strong_youzi_min: float = 60.0
    fake_strong_quant_max: float = 50.0


# ============================================================================
# 输入 / 输出
# ============================================================================


@dataclass
class QuantStrengthInput:
    """量化短线强度引擎输入数据。"""

    # ── 价格动量 ──
    momentum_z_score: float = 0.0  # 价格动量Z-score

    # ── 行业强度 ──
    sector_change_pct: float = 0.0  # 所属行业当日涨幅(%)

    # ── 相对强度 ──
    stock_change_pct: float = 0.0  # 个股涨幅(%)
    market_change_pct: float = 0.0  # 大盘涨幅(%)

    # ── 资金 ──
    capital_inflow: float = 0.0  # 主力净流入(元)
    float_market_cap: float = 0.0  # 流通市值(元)

    # ── 技术 ──
    technical_score: float = 50.0  # 技术形态综合分(0-100)

    # ── 风险 ──
    risk_score: float = 50.0  # 风险评分(0-100, 越低越好)

    # ── 双引擎融合输入 ──
    youzi_emotion_score: float = 50.0  # 游资情绪评分(D-SIGNAL-33输出)
    consecutive_limit_ups: int = 0  # 连板数
    is_main_line: bool = False  # 是否主线龙头


@dataclass
class DimensionScore:
    """单维度评分结果。"""

    name: str
    score: float
    max_score: float
    detail: str


@dataclass
class QuantStrengthResult:
    """量化短线强度引擎分析结果。"""

    total_score: float  # 综合强度评分(0-100)
    dimension_scores: list[DimensionScore]  # 6维度明细
    grade: str  # A~E评级
    category: str  # 6类输出分类
    is_degraded: bool = False
    audit_trail: list[dict[str, Any]] = field(default_factory=list)


# ============================================================================
# 分析器
# ============================================================================


class QuantShortTermStrengthEngine:
    """
    A股量化短线强度引擎（D-SIGNAL-34）。

    6维度评分 + A~E评级 + 6类输出：
      1. 价格动量Z-score(20分) — 动量因子核心
      2. 行业强度(15分) — 板块共振
      3. 相对强度(20分) — 超额收益
      4. 资金(15分) — 主力资金流入
      5. 技术(20分) — 技术形态综合
      6. 风险(10分) — 风险控制(反向)
    """

    def __init__(self, config: QuantStrengthConfig | None = None) -> None:
        self._config = config or QuantStrengthConfig()

    # ------------------------------------------------------------------
    # 公开入口
    # ------------------------------------------------------------------

    def analyze(self, input_data: QuantStrengthInput) -> QuantStrengthResult:
        """执行6维度评分 + 评级 + 分类，返回综合结果。"""
        if not self._validate_input(input_data):
            logger.warning("QuantShortTermStrengthEngine: 输入数据不合法，返回降级结果")
            return self._degraded_result("输入数据校验失败")

        audit_trail: list[dict[str, Any]] = []

        # ── 6维度评分 ──
        dims: list[DimensionScore] = []

        d1 = self.score_momentum(input_data.momentum_z_score)
        dims.append(d1)
        audit_trail.append({"dimension": "价格动量", "score": d1.score, "detail": d1.detail})

        d2 = self.score_sector_strength(input_data.sector_change_pct)
        dims.append(d2)
        audit_trail.append({"dimension": "行业强度", "score": d2.score, "detail": d2.detail})

        d3 = self.score_relative_strength(input_data.stock_change_pct, input_data.market_change_pct)
        dims.append(d3)
        audit_trail.append({"dimension": "相对强度", "score": d3.score, "detail": d3.detail})

        d4 = self.score_capital(input_data.capital_inflow, input_data.float_market_cap)
        dims.append(d4)
        audit_trail.append({"dimension": "资金", "score": d4.score, "detail": d4.detail})

        d5 = self.score_technical(input_data.technical_score)
        dims.append(d5)
        audit_trail.append({"dimension": "技术", "score": d5.score, "detail": d5.detail})

        d6 = self.score_risk(input_data.risk_score)
        dims.append(d6)
        audit_trail.append({"dimension": "风险", "score": d6.score, "detail": d6.detail})

        total = min(sum(d.score for d in dims), 100.0)

        # ── A~E评级 ──
        grade = self.determine_grade(total)
        audit_trail.append({"dimension": "评级", "grade": grade})

        # ── 6类输出分类 ──
        category = self.classify_category(total, input_data)
        audit_trail.append({"dimension": "分类", "category": category})

        return QuantStrengthResult(
            total_score=total,
            dimension_scores=dims,
            grade=grade,
            category=category,
            audit_trail=audit_trail,
        )

    # ------------------------------------------------------------------
    # 维度1: 价格动量Z-score (满分20)
    # ------------------------------------------------------------------

    def score_momentum(self, z_score: float) -> DimensionScore:
        """价格动量Z-score评分。"""
        cfg = self._config
        if z_score >= cfg.momentum_z_excellent:
            score = cfg.momentum_max_score
            detail = f"Z={z_score:.2f} >= {cfg.momentum_z_excellent} → 满分"
        elif z_score >= cfg.momentum_z_good:
            score = 15.0
            detail = f"Z={z_score:.2f} >= {cfg.momentum_z_good} → 15分"
        elif z_score >= cfg.momentum_z_fair:
            score = 8.0
            detail = f"Z={z_score:.2f} >= {cfg.momentum_z_fair} → 8分"
        else:
            # 负Z-score按比例递减
            score = max(8.0 + (z_score - cfg.momentum_z_fair) * 4.0, 0.0)
            detail = f"Z={z_score:.2f} < {cfg.momentum_z_fair} → {score:.1f}分"

        return DimensionScore("价格动量", score, cfg.momentum_max_score, detail)

    # ------------------------------------------------------------------
    # 维度2: 行业强度 (满分15)
    # ------------------------------------------------------------------

    def score_sector_strength(self, sector_change_pct: float) -> DimensionScore:
        """行业强度评分。"""
        cfg = self._config
        if sector_change_pct >= cfg.sector_change_excellent:
            score = cfg.sector_max_score
            detail = f"行业涨{sector_change_pct:.1f}% → 满分"
        elif sector_change_pct >= cfg.sector_change_good:
            score = 11.0
            detail = f"行业涨{sector_change_pct:.1f}% → 11分"
        elif sector_change_pct >= cfg.sector_change_fair:
            score = 6.0
            detail = f"行业涨{sector_change_pct:.1f}% → 6分"
        else:
            score = max(6.0 + sector_change_pct * 3.0, 0.0)
            detail = f"行业涨{sector_change_pct:.1f}% → {score:.1f}分"

        return DimensionScore("行业强度", score, cfg.sector_max_score, detail)

    # ------------------------------------------------------------------
    # 维度3: 相对强度 (满分20)
    # ------------------------------------------------------------------

    def score_relative_strength(self, stock_change_pct: float, market_change_pct: float) -> DimensionScore:
        """相对强度评分——个股涨幅 vs 大盘涨幅。"""
        cfg = self._config
        rs = stock_change_pct - market_change_pct

        if rs >= cfg.relative_strength_excellent:
            score = cfg.relative_strength_max_score
            detail = f"超大盘{rs:.1f}% → 满分"
        elif rs >= cfg.relative_strength_good:
            score = 15.0
            detail = f"超大盘{rs:.1f}% → 15分"
        elif rs >= cfg.relative_strength_fair:
            score = 8.0
            detail = f"超大盘{rs:.1f}% → 8分"
        else:
            score = max(8.0 + (rs - cfg.relative_strength_fair) * 4.0, 0.0)
            detail = f"超大盘{rs:.1f}% → {score:.1f}分"

        return DimensionScore("相对强度", score, cfg.relative_strength_max_score, detail)

    # ------------------------------------------------------------------
    # 维度4: 资金 (满分15)
    # ------------------------------------------------------------------

    def score_capital(self, capital_inflow: float, float_market_cap: float) -> DimensionScore:
        """资金评分——主力净流入/流通市值。"""
        cfg = self._config
        if float_market_cap <= 0:
            return DimensionScore("资金", 0.0, cfg.capital_max_score, "流通市值为0")

        ratio = capital_inflow / float_market_cap

        if ratio >= cfg.capital_inflow_excellent:
            score = cfg.capital_max_score
            detail = f"净流入比{ratio:.1%} → 满分"
        elif ratio >= cfg.capital_inflow_good:
            score = 11.0
            detail = f"净流入比{ratio:.1%} → 11分"
        elif ratio >= cfg.capital_inflow_fair:
            score = 6.0
            detail = f"净流入比{ratio:.1%} → 6分"
        else:
            score = max(6.0 + ratio * 60.0, 0.0)
            detail = f"净流入比{ratio:.1%} → {score:.1f}分"

        return DimensionScore("资金", score, cfg.capital_max_score, detail)

    # ------------------------------------------------------------------
    # 维度5: 技术 (满分20)
    # ------------------------------------------------------------------

    def score_technical(self, technical_score: float) -> DimensionScore:
        """技术形态综合评分。"""
        cfg = self._config
        if technical_score >= cfg.technical_excellent:
            score = cfg.technical_max_score
            detail = f"技术分{technical_score:.0f} → 满分"
        elif technical_score >= cfg.technical_good:
            score = 15.0
            detail = f"技术分{technical_score:.0f} → 15分"
        elif technical_score >= cfg.technical_fair:
            score = 8.0
            detail = f"技术分{technical_score:.0f} → 8分"
        else:
            score = max(technical_score / cfg.technical_fair * 8.0, 0.0)
            detail = f"技术分{technical_score:.0f} → {score:.1f}分"

        return DimensionScore("技术", score, cfg.technical_max_score, detail)

    # ------------------------------------------------------------------
    # 维度6: 风险 (满分10, 反向评分)
    # ------------------------------------------------------------------

    def score_risk(self, risk_score: float) -> DimensionScore:
        """风险评分——风险分越低越好（反向评分）。"""
        cfg = self._config
        if risk_score <= cfg.risk_score_excellent:
            score = cfg.risk_max_score
            detail = f"风险分{risk_score:.0f} → 满分"
        elif risk_score <= cfg.risk_score_good:
            score = 7.0
            detail = f"风险分{risk_score:.0f} → 7分"
        elif risk_score <= cfg.risk_score_fair:
            score = 4.0
            detail = f"风险分{risk_score:.0f} → 4分"
        else:
            score = max(4.0 - (risk_score - cfg.risk_score_fair) * 0.1, 0.0)
            detail = f"风险分{risk_score:.0f} → {score:.1f}分"

        return DimensionScore("风险", score, cfg.risk_max_score, detail)

    # ------------------------------------------------------------------
    # A~E五级评级
    # ------------------------------------------------------------------

    def determine_grade(self, total_score: float) -> str:
        """A~E五级评级——单调映射。"""
        cfg = self._config
        if total_score >= cfg.grade_a_min:
            return StrengthGrade.A.value
        if total_score >= cfg.grade_b_min:
            return StrengthGrade.B.value
        if total_score >= cfg.grade_c_min:
            return StrengthGrade.C.value
        if total_score >= cfg.grade_d_min:
            return StrengthGrade.D.value
        return StrengthGrade.E.value

    # ------------------------------------------------------------------
    # 6类输出分类
    # ------------------------------------------------------------------

    def classify_category(self, total_score: float, input_data: QuantStrengthInput) -> str:
        """
        6类输出分类——结合量化评分 + 游资情绪 + 连板 + 主线。

        分类优先级：
        1. 主升龙头: 量化>=80 + 游资>=70 + 是主线
        2. 二进三: 量化>=65 + 连板数>=2
        3. 复苏: 量化>=70 + 游资40-65
        4. 伪强: 游资>=60 + 量化<50
        5. 跟风: 量化50-65 + 游资40-65
        6. 地天反包: 极端反转(跌幅大后涨停)
        """
        cfg = self._config
        quant = total_score
        youzi = input_data.youzi_emotion_score

        # 地天反包：极端反转（从大跌到涨停）
        # 检测：连板=1 + 当日涨停(涨幅>=9.5%) + 前日大跌(隐含在risk高)
        if input_data.consecutive_limit_ups == 1 and input_data.stock_change_pct >= 9.5 and input_data.risk_score >= 60:
            return StockCategory.INVERSE_BOARD.value

        # 1. 主升龙头
        if quant >= cfg.main_leader_quant_min and youzi >= cfg.main_leader_youzi_min and input_data.is_main_line:
            return StockCategory.MAIN_LEADER.value

        # 2. 二进三
        if quant >= cfg.second_to_third_quant_min and input_data.consecutive_limit_ups >= 2:
            return StockCategory.SECOND_TO_THIRD.value

        # 3. 复苏
        if quant >= cfg.recovery_quant_min and 40.0 <= youzi < 65.0:
            return StockCategory.RECOVERY.value

        # 4. 伪强
        if youzi >= cfg.fake_strong_youzi_min and quant < cfg.fake_strong_quant_max:
            return StockCategory.FAKE_STRONG.value

        # 5. 跟风
        if cfg.follower_quant_min <= quant <= cfg.follower_quant_max and 40.0 <= youzi <= 65.0:
            return StockCategory.FOLLOWER.value

        return StockCategory.NEUTRAL.value

    # ------------------------------------------------------------------
    # 内部辅助
    # ------------------------------------------------------------------

    def _validate_input(self, input_data: QuantStrengthInput) -> bool:
        """校验输入数据基本合法性。"""
        if input_data.float_market_cap < 0:
            return False
        if input_data.technical_score < 0 or input_data.technical_score > 100:
            return False
        if input_data.risk_score < 0 or input_data.risk_score > 100:
            return False
        if input_data.consecutive_limit_ups < 0:
            return False
        return True

    def _degraded_result(self, reason: str) -> QuantStrengthResult:
        """降级结果。"""
        logger.warning("QuantShortTermStrengthEngine 降级: %s", reason)
        return QuantStrengthResult(
            total_score=0.0,
            dimension_scores=[],
            grade=StrengthGrade.E.value,
            category=StockCategory.NEUTRAL.value,
            is_degraded=True,
            audit_trail=[{"degraded": True, "reason": reason}],
        )
