# [BLUEPRINT] MOD-EX_SOR_EXT-001 | docs/03_modules/_domain_ex_sor/slippage_analyzer/blueprint.md
# [MODULE] zephyr.ex_sor.services.slippage_analyzer
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] zephyr.shared.contracts.order; zephyr.shared.contracts.enums.order_enums; zephyr.shared.foundation.errors
# [CONSUMERS] MOD-EX_SOR_EXT-002(ExecutionQualityScorer, 消费 SlippageResult); MOD-EX-CORE(执行质量报告)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 滑点符号约定: BUY 正=成本(买贵了), SELL 正=成本(卖便宜了); 归因分量和≈总滑点(残差吸收误差); 预测值为非负
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SlippageAnalyzerError; InsufficientFillsError; InvalidBenchmarkError
# [TESTS] tests/ex_sor/test_slippage_analyzer.py
# [A_module] module_id=MOD-EX_SOR_EXT-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Slippage Analyzer — 滑点分析器 (MOD-EX_SOR_EXT-001)

D-EX-SOR §2.1 XS-EXT-01: 实际vs预期滑点 + 滑点归因 + 滑点预测 + 基准比较。

职责:
    - 计算实际成交价相对多基准 (到达价/VWAP/TWAP/前收/决策价) 的滑点 (bps)
    - 将总滑点归因到市场冲击 / 时机 / 价差三因子 (+ 残差)
    - 基于平方根冲击模型预测预期滑点
    - 维护历史滑点记录供趋势分析

滑点符号约定 (统一):
    BUY  → slippage_bps = (avg_fill - benchmark) / benchmark × 10000
           正值 = 买贵了 = 成本; 负值 = 买便宜了 = 有利
    SELL → slippage_bps = (benchmark - avg_fill) / benchmark × 10000
           正值 = 卖便宜了 = 成本; 负值 = 卖贵了 = 有利

归因模型 (Phase 1, 简化版):
    market_impact_bps = impact_coeff × sqrt(participation_rate) × volatility_bps
    timing_bps        = (end_price - start_price) / start_price × 10000 × sign(side)
                        (BUY: 价格上涨→时机成本; SELL: 价格下跌→时机成本)
    spread_bps        = half_spread_bps (估计)
    residual_bps      = total_slippage - (impact + timing + spread)

SSoT: depgraph MOD-EX_SOR_EXT-001
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 成交记录列表 fills
#   fields: 每笔成交价price + 数量quantity + 时间 + 方向side, 至少1笔
#   code: SlippageFillRecord L132
# - id: I2
#   name: 基准价格映射 benchmarks
#   fields: ARRIVAL到达价/VWAP/TWAP/PREV_CLOSE前收/DECISION决策价 → 价格
#   code: SlippageBenchmark L115
# - id: I3
#   name: 归因预测参数
#   fields: adv日均量 + volatility日波动率 + start/end_price执行起止价 + spread_bps价差
#   code: analyze(...) L359
# 层: 特征
# - id: F1
#   name_zh: 加权平均成交价
#   name_en: avg_fill_price
#   intro: 所有成交按数量加权的平均价格
#   formula: avg_fill = Σ(price×qty) / Σqty, 保留4位
#   code: slippage_analyzer.py L410
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F2
#   name_zh: 参与率
#   name_en: participation
#   intro: 成交量占日均量比例, 平方根冲击模型的核心输入
#   formula: participation = total_qty / adv
#   code: slippage_analyzer.py L509
#   registry: factor_registry: 无FCT条目
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① 多基准滑点计算
#   name_en: SlippageAnalyzer._calc_slippage_bps
#   intro: 平均成交价相对每个基准算出滑点基点, 正值都是成本
#   desc: BUY: (avg_fill-bench)/bench×10000; SELL取反; 四舍五入4位; 遍历全部基准出SlippageMetric
#   inputs: F1 I2
#   outputs: 多基准SlippageMetric列表
#   invariant: 滑点符号约定 BUY正=买贵成本, SELL正=卖便宜成本
# - id: A2
#   name_zh: ② 三因子滑点归因
#   name_en: SlippageAnalyzer._attribute
#   intro: 把总滑点拆成市场冲击+时机+价差三块, 剩下的进残差
#   desc: impact=0.142×√participation×vol_bps; timing=(end-start)/start×10000按方向取号; spread=半价差; residual=总滑点-三因子
#   inputs: A1 F2 I3
#   outputs: SlippageAttribution三因子+残差
#   invariant: 归因分量和≈总滑点(残差吸收误差)
# - id: A3
#   name_zh: ③ 平方根冲击滑点预测
#   name_en: SquareRootImpactPredictor.predict
#   intro: 用平方根法则预估这单大概会滑多少个基点
#   desc: impact_bps=coeff(0.142)×√(order_size/adv)×volatility×10000 + 半价差 → 非负, 保留2位
#   inputs: F2 I3
#   outputs: predicted_slippage_bps
#   invariant: 预测值为非负
# 层: 输出
# - id: O1
#   name_zh: 滑点分析结果 SlippageResult
#   name_en: SlippageResult
#   intro: 多基准滑点+三因子归因+预测滑点的完整分析, 并留历史记录
#   downstream: MOD-EX_SOR_EXT-002(ExecutionQualityScorer,消费 SlippageResult); MOD-EX-CORE(执行质量报告)
# [/ALGO_FLOW]
#
# 边:
# I1 -.->|断点| F1
# I3 -.->|断点| F2
# F1 --> A1
# I2 --> A1
# A1 --> A2
# F2 --> A2
# I3 --> A2
# F2 --> A3
# I3 --> A3
# A1 --> O1
# A2 --> O1
# A3 --> O1
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from enum import Enum
from typing import Final, Protocol

from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "SlippageFillRecord",
    "SlippageBenchmark",
    "SlippageMetric",
    "SlippageAttribution",
    "SlippageResult",
    "SlippagePredictor",
    "SquareRootImpactPredictor",
    "SlippageAnalyzer",
    "SlippageAnalyzerError",
    "InsufficientFillsError",
    "InvalidBenchmarkError",
]

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# 常量
# ──────────────────────────────────────────────────────────────────────────────

_BPS_FACTOR: Final[Decimal] = Decimal("10000")
_ZERO: Final[Decimal] = Decimal("0")
# 平方根冲击模型默认系数 (经验值, Almgren-Chriss 简化)
_DEFAULT_IMPACT_COEFF: Final[float] = 0.142  # ≈ 1/(2×√(2π)) 量级
# 默认 half-spread 估计 (A-share, bps)
_DEFAULT_HALF_SPREAD_BPS: Final[Decimal] = Decimal("10")  # ~0.1%


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class SlippageAnalyzerError(ZephyrBaseError):
    """滑点分析错误——通用基类。"""

    error_code = "ZA-XS-EXT-0001"


class InsufficientFillsError(SlippageAnalyzerError):
    """成交记录不足——无法计算滑点 (无成交或总量为零)。"""

    error_code = "ZA-XS-EXT-0001-IF"


class InvalidBenchmarkError(SlippageAnalyzerError):
    """基准价格非法——为零/负值或缺失。"""

    error_code = "ZA-XS-EXT-0001-IB"


# ──────────────────────────────────────────────────────────────────────────────
# 数据结构
# ──────────────────────────────────────────────────────────────────────────────


class SlippageBenchmark(Enum):
    """滑点基准类型。

    约定 __str__ 返回 value, 统一日志格式。
    """

    def __str__(self) -> str:
        return self.value

    ARRIVAL = "ARRIVAL"  # 到达价 (下单时刻市场价)
    VWAP = "VWAP"  # 成交量加权均价
    TWAP = "TWAP"  # 时间加权均价
    PREV_CLOSE = "PREV_CLOSE"  # 前收盘价
    DECISION = "DECISION"  # 决策价 (信号生成时价)


@dataclass(frozen=True)
class SlippageFillRecord:
    """单笔成交记录。

    Attributes:
        fill_id: 成交编号
        price: 成交价 (Decimal, 禁止 float)
        quantity: 成交数量 (Decimal)
        timestamp: 成交时间
        side: 买卖方向
    """

    fill_id: str
    price: Decimal
    quantity: Decimal
    timestamp: datetime
    side: OrderSide

    def __post_init__(self) -> None:
        if self.price <= _ZERO:
            raise SlippageAnalyzerError(
                "成交价必须为正",
                details={"fill_id": self.fill_id, "price": str(self.price)},
            )
        if self.quantity <= _ZERO:
            raise SlippageAnalyzerError(
                "成交数量必须为正",
                details={"fill_id": self.fill_id, "quantity": str(self.quantity)},
            )


@dataclass(frozen=True)
class SlippageMetric:
    """单基准滑点指标。

    Attributes:
        benchmark: 基准类型
        benchmark_price: 基准价格
        avg_fill_price: 平均成交价
        slippage_bps: 滑点 (bps, 正=成本/负=有利)
        side: 买卖方向
    """

    benchmark: SlippageBenchmark
    benchmark_price: Decimal
    avg_fill_price: Decimal
    slippage_bps: Decimal
    side: OrderSide


@dataclass(frozen=True)
class SlippageAttribution:
    """滑点归因——三因子分解 + 残差。

    Attributes:
        market_impact_bps: 市场冲击分量 (订单自身造成的价格变动)
        timing_bps: 时机分量 (执行期间价格漂移)
        spread_bps: 价差分量 (bid-ask spread 半价差)
        residual_bps: 残差 (总滑点 - 三因子之和, 吸收模型误差)
    """

    market_impact_bps: Decimal
    timing_bps: Decimal
    spread_bps: Decimal
    residual_bps: Decimal

    @property
    def total_attributed_bps(self) -> Decimal:
        """已归因总量 (不含残差)。"""
        return self.market_impact_bps + self.timing_bps + self.spread_bps


@dataclass(frozen=True)
class SlippageResult:
    """滑点分析结果——多基准指标 + 归因 + 元信息。

    Attributes:
        order_id: 订单 ID
        symbol: 标的代码
        side: 买卖方向
        total_quantity: 总成交数量
        avg_fill_price: 加权平均成交价
        metrics: 多基准滑点指标列表
        attribution: 三因子归因
        predicted_slippage_bps: 预测滑点 (平方根模型, None=未预测)
        analyzed_at: 分析时间
    """

    order_id: str
    symbol: str
    side: OrderSide
    total_quantity: Decimal
    avg_fill_price: Decimal
    metrics: list[SlippageMetric]
    attribution: SlippageAttribution
    predicted_slippage_bps: Decimal | None
    analyzed_at: datetime

    def metric_for(self, benchmark: SlippageBenchmark) -> SlippageMetric | None:
        """按基准类型查询指标。"""
        for m in self.metrics:
            if m.benchmark is benchmark:
                return m
        return None


# ──────────────────────────────────────────────────────────────────────────────
# 滑点预测器
# ──────────────────────────────────────────────────────────────────────────────


class SlippagePredictor(Protocol):
    """滑点预测器接口——根据订单特征预测预期滑点。"""

    def predict(
        self,
        order_size: Decimal,
        adv: Decimal,
        volatility: Decimal,
        spread_bps: Decimal,
    ) -> Decimal:
        """预测滑点 (bps, 非负)。

        Args:
            order_size: 订单数量
            adv: 日均成交量
            volatility: 日波动率 (小数, 如 0.02 = 2%)
            spread_bps: bid-ask 价差 (bps)

        Returns:
            预测滑点 (bps, ≥0)
        """


class SquareRootImpactPredictor:
    """平方根冲击模型预测器——Almgren-Chriss 简化版。

    模型:
        participation = order_size / adv
        impact_bps = coeff × sqrt(participation) × volatility_bps + half_spread

    理论对标: 平方根法则 (Grinold & Kahn); Almgren-Thum et al.
    """

    def __init__(self, coefficient: float = _DEFAULT_IMPACT_COEFF) -> None:
        self._coeff = coefficient

    def predict(
        self,
        order_size: Decimal,
        adv: Decimal,
        volatility: Decimal,
        spread_bps: Decimal,
    ) -> Decimal:
        if adv <= _ZERO:
            raise InvalidBenchmarkError(
                "ADV 必须为正",
                details={"adv": str(adv)},
            )
        if order_size <= _ZERO:
            return _ZERO
        participation = float(order_size / adv)
        vol_bps = float(volatility) * float(_BPS_FACTOR)
        impact = self._coeff * math.sqrt(participation) * vol_bps
        half_spread = float(spread_bps) / 2.0
        predicted = impact + half_spread
        # 四舍五入到 0.01 bps
        return Decimal(str(round(max(predicted, 0.0), 2)))


# ──────────────────────────────────────────────────────────────────────────────
# 滑点分析器
# ──────────────────────────────────────────────────────────────────────────────


class SlippageAnalyzer:
    """滑点分析器——多基准计算 + 三因子归因 + 预测 + 历史追踪。

    用法:
        analyzer = SlippageAnalyzer()
        result = analyzer.analyze(
            order_id="ORD-001",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[SlippageFillRecord(...), ...],
            benchmarks={
                SlippageBenchmark.ARRIVAL: Decimal("10.00"),
                SlippageBenchmark.VWAP: Decimal("10.02"),
            },
            # 可选: 归因输入
            adv=Decimal("1000000"),
            volatility=Decimal("0.02"),
            start_price=Decimal("10.00"),
            end_price=Decimal("10.05"),
        )
        # result.metric_for(SlippageBenchmark.ARRIVAL).slippage_bps → 滑点
        # result.attribution.market_impact_bps → 市场冲击分量
    """

    def __init__(
        self,
        predictor: SlippagePredictor | None = None,
        half_spread_bps: Decimal = _DEFAULT_HALF_SPREAD_BPS,
    ) -> None:
        self._predictor = predictor or SquareRootImpactPredictor()
        self._half_spread_bps = half_spread_bps
        self._history: list[SlippageResult] = []

    # ── 属性 ──

    @property
    def history(self) -> list[SlippageResult]:
        """历史滑点分析记录 (按时间顺序)。"""
        return list(self._history)

    # ── 分析入口 ──

    def analyze(
        self,
        order_id: str,
        symbol: str,
        side: OrderSide,
        fills: list[SlippageFillRecord],
        benchmarks: dict[SlippageBenchmark, Decimal],
        *,
        adv: Decimal | None = None,
        volatility: Decimal | None = None,
        start_price: Decimal | None = None,
        end_price: Decimal | None = None,
        spread_bps: Decimal | None = None,
        now: datetime | None = None,
    ) -> SlippageResult:
        """分析滑点——多基准计算 + 归因 + 预测。

        Args:
            order_id: 订单 ID
            symbol: 标的代码
            side: 买卖方向
            fills: 成交记录列表 (≥1 笔)
            benchmarks: 基准价格映射 {基准类型: 价格}
            adv: 日均成交量 (归因+预测用, 可选)
            volatility: 日波动率 (归因+预测用, 可选)
            start_price: 执行开始价 (时机归因用, 可选)
            end_price: 执行结束价 (时机归因用, 可选)
            spread_bps: bid-ask 价差 bps (归因用, 可选, 默认 half_spread×2)
            now: 分析时间 (测试用)

        Returns:
            SlippageResult: 滑点分析结果

        Raises:
            InsufficientFillsError: 无成交记录
            InvalidBenchmarkError: 基准价格非法
        """
        now = now or datetime.now(timezone.utc)

        # 1. 校验成交记录
        if not fills:
            raise InsufficientFillsError(
                "无成交记录, 无法计算滑点",
                details={"order_id": order_id},
            )
        if not benchmarks:
            raise InvalidBenchmarkError(
                "未提供任何基准价格",
                details={"order_id": order_id},
            )

        # 2. 计算加权平均成交价 + 总量
        total_qty = sum((f.quantity for f in fills), _ZERO)
        if total_qty <= _ZERO:
            raise InsufficientFillsError(
                "成交总量为零",
                details={"order_id": order_id},
            )
        total_notional = sum((f.price * f.quantity for f in fills), _ZERO)
        avg_fill = self._round4(total_notional / total_qty)

        # 3. 多基准滑点计算
        metrics: list[SlippageMetric] = []
        for bench_type, bench_price in benchmarks.items():
            if bench_price <= _ZERO:
                raise InvalidBenchmarkError(
                    f"基准 {bench_type} 价格必须为正",
                    details={"benchmark": bench_type.value, "price": str(bench_price)},
                )
            slip = self._calc_slippage_bps(avg_fill, bench_price, side)
            metrics.append(
                SlippageMetric(
                    benchmark=bench_type,
                    benchmark_price=bench_price,
                    avg_fill_price=avg_fill,
                    slippage_bps=slip,
                    side=side,
                )
            )

        # 4. 归因 (以 ARRIVAL 基准为总滑点, 若无则取第一个)
        primary = self._pick_primary_metric(metrics, benchmarks)
        attribution = self._attribute(
            total_slippage=primary.slippage_bps,
            side=side,
            total_qty=total_qty,
            adv=adv,
            volatility=volatility,
            start_price=start_price,
            end_price=end_price,
            spread_bps=spread_bps,
        )

        # 5. 预测 (需 adv + volatility)
        predicted: Decimal | None = None
        if adv is not None and volatility is not None:
            sp = spread_bps if spread_bps is not None else self._half_spread_bps * 2
            predicted = self._predictor.predict(total_qty, adv, volatility, sp)

        result = SlippageResult(
            order_id=order_id,
            symbol=symbol,
            side=side,
            total_quantity=total_qty,
            avg_fill_price=avg_fill,
            metrics=metrics,
            attribution=attribution,
            predicted_slippage_bps=predicted,
            analyzed_at=now,
        )
        self._history.append(result)
        logger.info(
            "SlippageAnalyzed: order=%s symbol=%s avg_fill=%s primary_slippage=%s bps",
            order_id,
            symbol,
            avg_fill,
            primary.slippage_bps,
        )
        return result

    # ── 滑点计算 ──

    @staticmethod
    def _calc_slippage_bps(
        avg_fill: Decimal,
        benchmark: Decimal,
        side: OrderSide,
    ) -> Decimal:
        """计算滑点 (bps)。

        BUY  → (avg_fill - benchmark) / benchmark × 10000  (正=成本)
        SELL → (benchmark - avg_fill) / benchmark × 10000  (正=成本)
        """
        if side is OrderSide.BUY:
            diff = avg_fill - benchmark
        else:
            diff = benchmark - avg_fill
        bps = diff / benchmark * _BPS_FACTOR
        return SlippageAnalyzer._round4(bps)

    # ── 归因 ──

    def _attribute(
        self,
        total_slippage: Decimal,
        side: OrderSide,
        total_qty: Decimal,
        adv: Decimal | None,
        volatility: Decimal | None,
        start_price: Decimal | None,
        end_price: Decimal | None,
        spread_bps: Decimal | None,
    ) -> SlippageAttribution:
        """三因子归因 + 残差。"""
        # 市场冲击: 平方根模型 (需 adv + volatility)
        impact = _ZERO
        if adv is not None and adv > _ZERO and volatility is not None:
            participation = float(total_qty / adv)
            vol_bps = float(volatility) * float(_BPS_FACTOR)
            impact_val = _DEFAULT_IMPACT_COEFF * math.sqrt(participation) * vol_bps
            impact = Decimal(str(round(max(impact_val, 0.0), 4)))

        # 时机: 执行期间价格漂移
        timing = _ZERO
        if start_price is not None and end_price is not None and start_price > _ZERO:
            drift_bps = (end_price - start_price) / start_price * _BPS_FACTOR
            if side is OrderSide.BUY:
                # BUY: 价格上涨 → 时机成本 (正)
                timing = self._round4(drift_bps)
            else:
                # SELL: 价格下跌 → 时机成本 (正), 取反
                timing = self._round4(-drift_bps)

        # 价差: half-spread
        if spread_bps is not None and spread_bps > _ZERO:
            spread = self._round4(spread_bps / 2)
        else:
            spread = self._half_spread_bps

        # 残差: 总滑点 - 三因子
        attributed = impact + timing + spread
        residual = self._round4(total_slippage - attributed)

        return SlippageAttribution(
            market_impact_bps=impact,
            timing_bps=timing,
            spread_bps=spread,
            residual_bps=residual,
        )

    # ── 辅助 ──

    @staticmethod
    def _pick_primary_metric(
        metrics: list[SlippageMetric],
        benchmarks: dict[SlippageBenchmark, Decimal],
    ) -> SlippageMetric:
        """选主基准指标 (优先 ARRIVAL, 其次 DECISION, 再取第一个)。"""
        priority = [SlippageBenchmark.ARRIVAL, SlippageBenchmark.DECISION]
        for bench in priority:
            for m in metrics:
                if m.benchmark is bench:
                    return m
        return metrics[0]

    @staticmethod
    def _round4(value: Decimal) -> Decimal:
        """四舍五入到 4 位小数。"""
        return value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

    # ── 历史查询 ──

    def get_history(self, symbol: str | None = None) -> list[SlippageResult]:
        """查询历史滑点记录 (可按 symbol 过滤)。"""
        if symbol is None:
            return list(self._history)
        return [r for r in self._history if r.symbol == symbol]

    def clear_history(self) -> None:
        """清空历史记录。"""
        self._history.clear()
