# [BLUEPRINT] MOD-EX_SOR_EXT-002 | docs/03_modules/_domain_ex_sor/execution_quality_scorer/blueprint.md
# [MODULE] zephyr.ex_sor.services.execution_quality_scorer
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] zephyr.shared.contracts.enums.order_enums; zephyr.shared.foundation.errors; zephyr.ex_sor.services.slippage_analyzer; zephyr.ex_sor.services.transaction_cost_optimizer
# [CONSUMERS] MOD-EX-CORE(执行质量报告); MOD-XS-011(算法选择器反馈环)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 各维度评分∈[0,1]; 权重和=1.0; overall=Σ(score_i×weight_i); verdict: good≥0.8/acceptable≥0.5/poor<0.5
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] QualityScorerError; InvalidWeightsError; InsufficientMetricsError
# [TESTS] tests/ex_sor/test_execution_quality_scorer.py
# [A_module] module_id=MOD-EX_SOR_EXT-002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Execution Quality Scorer — 执行质量评分器 (MOD-EX_SOR_EXT-002)

D-EX-SOR §2.1 XS-EXT-02: 价格/时间/成本/市场影响多维评估 + 历史追踪。

职责:
    - 从执行结果提取四维度指标 (价格/时间/成本/市场影响)
    - 各维度归一化到 [0, 1] 评分 (1=最优)
    - 加权求和得总体评分 + 评定 (good/acceptable/poor)
    - 维护历史评分供趋势分析

四维度评分模型:
    Price  — 滑点越小越好: score = max(0, 1 - slippage_bps / threshold)
             threshold 默认 50 bps (50bps 视为最差)
    Time   — 执行越快越好: score = max(0, 1 - duration / expected_duration)
             expected_duration 默认 300 秒 (5 分钟)
    Cost   — 总成本越低越好: score = max(0, 1 - cost_bps / threshold)
             threshold 默认 30 bps (30bps 视为最差)
    Impact — 冲击越小越好: score = max(0, 1 - impact_bps / threshold)
             threshold 默认 20 bps (20bps 视为最差)

可消费上游:
    - SlippageAnalyzer (EXT-001) 的 SlippageResult → price + impact 维度
    - TransactionCostOptimizer (EXT-003) 的 TransactionCostResult → cost 维度
    - 也可直接传入原始指标 (slippage_bps, duration_s, cost_bps, impact_bps)

SSoT: depgraph MOD-EX_SOR_EXT-002
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 原始执行指标
#   fields: slippage_bps滑点 + duration_seconds耗时 + total_cost_bps成本 + impact_bps冲击, 至少给一项
#   code: score(...) L322; 可来自EXT-001 SlippageResult/EXT-003 TransactionCostResult
# - id: I2
#   name: 质量评分权重 QualityWeights
#   fields: 价格0.35 + 时间0.25 + 成本0.25 + 影响0.15, 和必须=1.0
#   code: QualityWeights L134
# - id: I3
#   name: 最差阈值基准
#   fields: 滑点50bps + 耗时300s + 成本30bps + 冲击20bps (达到即0分)
#   code: DefaultBenchmarkProvider L252
# 层: 算法
# - id: A1
#   name_zh: ① 单维度归一评分
#   name_en: ExecutionQualityScorer._score_dimension
#   intro: 每个维度按离最差阈值的比例折算成0~1分, 越小越好
#   desc: score=max(0, 1-raw/threshold), 对PRICE/TIME/COST/IMPACT四维分别计算, 保留4位
#   inputs: I1 I3
#   outputs: ExecutionDimensionScore单维评分
#   invariant: 各维度评分∈[0,1]
# - id: A2
#   name_zh: ② 四维加权汇总评定
#   name_en: ExecutionQualityScorer._calc_overall+_verdict
#   intro: 四维分按权重加权平均得总分, 再定good/acceptable/poor三档
#   desc: overall=Σ(score×w)/Σw → good≥0.8 / acceptable≥0.5 / poor<0.5 → 留历史
#   inputs: A1 I2
#   outputs: overall_score + verdict
#   invariant: 权重和=1.0; overall=Σ(score_i×weight_i)
# 层: 输出
# - id: O1
#   name_zh: 执行质量评分结果 ExecutionQualityResult
#   name_en: ExecutionQualityResult
#   intro: 总分+评定+各维度明细, 衡量这一单执行得好不好
#   downstream: MOD-EX-CORE(执行质量报告); MOD-XS-011(算法选择器反馈环)
# - id: O2
#   name_zh: 历史评分趋势
#   name_en: average_score/get_history
#   intro: 历史评分可按标的/最低分过滤并算平均分, 供趋势分析
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I3 --> A1
# A1 --> A2
# I2 --> A2
# A2 --> O1
# A2 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Final, Protocol

from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "QualityDimension",
    "QualityWeights",
    "ExecutionDimensionScore",
    "ExecutionQualityResult",
    "QualityBenchmarkProvider",
    "DefaultBenchmarkProvider",
    "ExecutionQualityScorer",
    "QualityScorerError",
    "InvalidWeightsError",
    "InsufficientMetricsError",
]

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# 常量 & 阈值
# ──────────────────────────────────────────────────────────────────────────────

# 各维度 "最差" 阈值 (达到此值 → score=0)
_DEFAULT_PRICE_THRESHOLD_BPS: Final[float] = 50.0  # 50bps 滑点 = 最差
_DEFAULT_TIME_THRESHOLD_S: Final[float] = 300.0  # 300 秒 = 最差
_DEFAULT_COST_THRESHOLD_BPS: Final[float] = 30.0  # 30bps 总成本 = 最差
_DEFAULT_IMPACT_THRESHOLD_BPS: Final[float] = 20.0  # 20bps 冲击 = 最差

# 评定阈值
_VERDICT_GOOD: Final[float] = 0.8
_VERDICT_ACCEPTABLE: Final[float] = 0.5


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class QualityScorerError(ZephyrBaseError):
    """质量评分错误——通用基类。"""

    error_code = "ZA-XS-EXT-0002"


class InvalidWeightsError(QualityScorerError):
    """权重非法——和≠1.0 或含负值。"""

    error_code = "ZA-XS-EXT-0002-IW"


class InsufficientMetricsError(QualityScorerError):
    """指标不足——至少需要一个维度指标。"""

    error_code = "ZA-XS-EXT-0002-IM"


# ──────────────────────────────────────────────────────────────────────────────
# 数据结构
# ──────────────────────────────────────────────────────────────────────────────


class QualityDimension(Enum):
    """质量评分维度。

    约定 __str__ 返回 value。
    """

    def __str__(self) -> str:
        return self.value

    PRICE = "PRICE"  # 价格维度 (滑点)
    TIME = "TIME"  # 时间维度 (执行速度)
    COST = "COST"  # 成本维度 (总交易成本)
    IMPACT = "IMPACT"  # 市场影响维度


@dataclass(frozen=True)
class QualityWeights:
    """质量评分权重——四维度, 和必须 = 1.0。

    默认: 价格优先 (0.35) > 时间 (0.25) = 成本 (0.25) > 影响 (0.15)
    """

    price_weight: float = 0.35
    time_weight: float = 0.25
    cost_weight: float = 0.25
    impact_weight: float = 0.15

    def __post_init__(self) -> None:
        for name, val in [
            ("price_weight", self.price_weight),
            ("time_weight", self.time_weight),
            ("cost_weight", self.cost_weight),
            ("impact_weight", self.impact_weight),
        ]:
            if val < 0:
                raise InvalidWeightsError(
                    f"{name} 不能为负",
                    details={"field": name, "value": val},
                )
        total = self.price_weight + self.time_weight + self.cost_weight + self.impact_weight
        if abs(total - 1.0) > 1e-6:
            raise InvalidWeightsError(
                f"权重和必须为 1.0, 实际 {total}",
                details={"sum": total},
            )

    def weight_for(self, dim: QualityDimension) -> float:
        return {
            QualityDimension.PRICE: self.price_weight,
            QualityDimension.TIME: self.time_weight,
            QualityDimension.COST: self.cost_weight,
            QualityDimension.IMPACT: self.impact_weight,
        }[dim]


@dataclass(frozen=True)
class ExecutionDimensionScore:
    """单维度评分。

    Attributes:
        dimension: 维度类型
        score: 评分 [0, 1], 1=最优
        raw_value: 原始指标值 (bps 或 秒)
        threshold: 最差阈值 (达到此值 score=0)
        verdict: 单维度评定 (good/acceptable/poor)
    """

    dimension: QualityDimension
    score: float
    raw_value: float
    threshold: float
    verdict: str

    def __post_init__(self) -> None:
        if not (0.0 <= self.score <= 1.0):
            raise QualityScorerError(
                f"评分必须在 [0, 1], 实际 {self.score}",
                details={"dimension": self.dimension.value, "score": self.score},
            )


@dataclass(frozen=True)
class ExecutionQualityResult:
    """执行质量评分结果。

    Attributes:
        order_id: 订单 ID
        symbol: 标的代码
        side: 买卖方向
        overall_score: 总体评分 [0, 1]
        verdict: 总体评定 (good/acceptable/poor)
        dimension_scores: 各维度评分
        weights: 使用的权重
        evaluated_at: 评估时间
    """

    order_id: str
    symbol: str
    side: OrderSide
    overall_score: float
    verdict: str
    dimension_scores: list[ExecutionDimensionScore]
    weights: QualityWeights
    evaluated_at: datetime

    def score_for(self, dim: QualityDimension) -> ExecutionDimensionScore | None:
        """按维度查询评分。"""
        for ds in self.dimension_scores:
            if ds.dimension is dim:
                return ds
        return None


# ──────────────────────────────────────────────────────────────────────────────
# 基准提供者 (可替换阈值)
# ──────────────────────────────────────────────────────────────────────────────


class QualityBenchmarkProvider(Protocol):
    """质量基准提供者——提供各维度最差阈值。"""

    def price_threshold_bps(self) -> float:
        """价格维度最差阈值 (bps)。"""

    def time_threshold_s(self) -> float:
        """时间维度最差阈值 (秒)。"""

    def cost_threshold_bps(self) -> float:
        """成本维度最差阈值 (bps)。"""

    def impact_threshold_bps(self) -> float:
        """市场影响维度最差阈值 (bps)。"""


class DefaultBenchmarkProvider:
    """默认基准提供者——静态阈值。"""

    def price_threshold_bps(self) -> float:
        return _DEFAULT_PRICE_THRESHOLD_BPS

    def time_threshold_s(self) -> float:
        return _DEFAULT_TIME_THRESHOLD_S

    def cost_threshold_bps(self) -> float:
        return _DEFAULT_COST_THRESHOLD_BPS

    def impact_threshold_bps(self) -> float:
        return _DEFAULT_IMPACT_THRESHOLD_BPS


# ──────────────────────────────────────────────────────────────────────────────
# 执行质量评分器
# ──────────────────────────────────────────────────────────────────────────────


class ExecutionQualityScorer:
    """执行质量评分器——四维度评估 + 加权汇总 + 历史追踪。

    用法 1 (原始指标):
        scorer = ExecutionQualityScorer()
        result = scorer.score(
            order_id="ORD-001",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            slippage_bps=Decimal("15"),    # 滑点 15bps
            duration_seconds=120.0,         # 执行 120 秒
            total_cost_bps=Decimal("8"),    # 总成本 8bps
            impact_bps=Decimal("5"),        # 冲击 5bps
        )

    用法 2 (消费上游结果):
        # slippage_result 来自 SlippageAnalyzer (EXT-001)
        # cost_result 来自 TransactionCostOptimizer (EXT-003)
        result = scorer.score_from_results(
            order_id="ORD-001",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            slippage_result=slippage_result,
            cost_result=cost_result,
            duration_seconds=120.0,
        )
    """

    def __init__(
        self,
        weights: QualityWeights | None = None,
        benchmark: QualityBenchmarkProvider | None = None,
    ) -> None:
        self._weights = weights or QualityWeights()
        self._benchmark = benchmark or DefaultBenchmarkProvider()
        self._history: list[ExecutionQualityResult] = []

    # ── 属性 ──

    @property
    def weights(self) -> QualityWeights:
        return self._weights

    @property
    def history(self) -> list[ExecutionQualityResult]:
        return list(self._history)

    # ── 评分入口 (原始指标) ──

    def score(
        self,
        order_id: str,
        symbol: str,
        side: OrderSide,
        *,
        slippage_bps: Decimal | None = None,
        duration_seconds: float | None = None,
        total_cost_bps: Decimal | None = None,
        impact_bps: Decimal | None = None,
        now: datetime | None = None,
    ) -> ExecutionQualityResult:
        """从原始指标评分——至少提供一个维度指标。

        Args:
            order_id: 订单 ID
            symbol: 标的代码
            side: 买卖方向
            slippage_bps: 滑点 (bps, PRICE 维度)
            duration_seconds: 执行耗时 (秒, TIME 维度)
            total_cost_bps: 总成本 (bps, COST 维度)
            impact_bps: 冲击成本 (bps, IMPACT 维度)
            now: 评估时间

        Returns:
            ExecutionQualityResult

        Raises:
            InsufficientMetricsError: 无任何指标
        """
        now = now or datetime.now(timezone.utc)
        dim_scores: list[ExecutionDimensionScore] = []

        if slippage_bps is not None:
            dim_scores.append(
                self._score_dimension(
                    QualityDimension.PRICE,
                    abs(float(slippage_bps)),
                    self._benchmark.price_threshold_bps(),
                )
            )
        if duration_seconds is not None:
            dim_scores.append(
                self._score_dimension(
                    QualityDimension.TIME,
                    float(duration_seconds),
                    self._benchmark.time_threshold_s(),
                )
            )
        if total_cost_bps is not None:
            dim_scores.append(
                self._score_dimension(
                    QualityDimension.COST,
                    abs(float(total_cost_bps)),
                    self._benchmark.cost_threshold_bps(),
                )
            )
        if impact_bps is not None:
            dim_scores.append(
                self._score_dimension(
                    QualityDimension.IMPACT,
                    abs(float(impact_bps)),
                    self._benchmark.impact_threshold_bps(),
                )
            )

        if not dim_scores:
            raise InsufficientMetricsError(
                "至少需要一个维度指标",
                details={"order_id": order_id},
            )

        overall = self._calc_overall(dim_scores)
        verdict = self._verdict(overall)

        result = ExecutionQualityResult(
            order_id=order_id,
            symbol=symbol,
            side=side,
            overall_score=overall,
            verdict=verdict,
            dimension_scores=dim_scores,
            weights=self._weights,
            evaluated_at=now,
        )
        self._history.append(result)
        logger.info(
            "QualityScored: order=%s overall=%.4f (%s) dims=%d",
            order_id,
            overall,
            verdict,
            len(dim_scores),
        )
        return result

    # ── 评分入口 (消费上游结果) ──

    def score_from_results(
        self,
        order_id: str,
        symbol: str,
        side: OrderSide,
        *,
        slippage_bps: Decimal | None = None,
        duration_seconds: float | None = None,
        total_cost_bps: Decimal | None = None,
        impact_bps: Decimal | None = None,
        now: datetime | None = None,
    ) -> ExecutionQualityResult:
        """从上游分析结果提取指标后评分。

        本方法接受已计算好的指标值 (与 score() 相同),
        便于从 SlippageResult / TransactionCostResult 提取后直接传入。

        使用示例:
            # 从 SlippageResult 提取
            slip_bps = slip_result.metric_for(SlippageBenchmark.ARRIVAL).slippage_bps
            impact_bps = slip_result.attribution.market_impact_bps
            # 从 TransactionCostResult 提取
            cost_bps = cost_result.total_cost_bps
            # 评分
            result = scorer.score_from_results(
                order_id, symbol, side,
                slippage_bps=slip_bps,
                impact_bps=impact_bps,
                total_cost_bps=cost_bps,
                duration_seconds=120.0,
            )
        """
        return self.score(
            order_id,
            symbol,
            side,
            slippage_bps=slippage_bps,
            duration_seconds=duration_seconds,
            total_cost_bps=total_cost_bps,
            impact_bps=impact_bps,
            now=now,
        )

    # ── 评分逻辑 ──

    def _score_dimension(
        self,
        dim: QualityDimension,
        raw_value: float,
        threshold: float,
    ) -> ExecutionDimensionScore:
        """单维度评分: score = max(0, 1 - raw / threshold)。"""
        if threshold <= 0:
            score = 0.0 if raw_value > 0 else 1.0
        else:
            score = max(0.0, 1.0 - raw_value / threshold)
        verdict = self._verdict(score)
        return ExecutionDimensionScore(
            dimension=dim,
            score=round(score, 4),
            raw_value=round(raw_value, 4),
            threshold=threshold,
            verdict=verdict,
        )

    def _calc_overall(self, dim_scores: list[ExecutionDimensionScore]) -> float:
        """加权总分 = Σ(score_i × weight_i) / Σ(weight_i)。"""
        total_weight = 0.0
        weighted_sum = 0.0
        for ds in dim_scores:
            w = self._weights.weight_for(ds.dimension)
            weighted_sum += ds.score * w
            total_weight += w
        if total_weight <= 0:
            return 0.0
        return round(weighted_sum / total_weight, 4)

    @staticmethod
    def _verdict(score: float) -> str:
        """评定: good ≥0.8 / acceptable ≥0.5 / poor <0.5。"""
        if score >= _VERDICT_GOOD:
            return "good"
        if score >= _VERDICT_ACCEPTABLE:
            return "acceptable"
        return "poor"

    # ── 历史查询 ──

    def get_history(
        self,
        symbol: str | None = None,
        min_score: float | None = None,
    ) -> list[ExecutionQualityResult]:
        """查询历史评分 (可按 symbol / 最低分过滤)。"""
        results = list(self._history)
        if symbol is not None:
            results = [r for r in results if r.symbol == symbol]
        if min_score is not None:
            results = [r for r in results if r.overall_score >= min_score]
        return results

    def average_score(self, symbol: str | None = None) -> float:
        """计算历史平均分 (可按 symbol 过滤)。"""
        results = self.get_history(symbol=symbol)
        if not results:
            return 0.0
        return sum(r.overall_score for r in results) / len(results)

    def clear_history(self) -> None:
        self._history.clear()
