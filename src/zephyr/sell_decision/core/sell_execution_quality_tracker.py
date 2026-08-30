# [BLUEPRINT] MOD-SELL-012 | docs/03_modules/MOD-SELL-012/
# [MODULE] zephyr.sell_decision.core.sell_execution_quality_tracker
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] D-EX-CORE(执行质量回执) ; MOD-SELL-011(AB测试执行维度输入) ; D_RISK
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 卖出滑点=(决策价−成交价)/决策价(正=卖亏); 加权平均按成交权重; 分级GOOD≤0.1%/ACCEPTABLE≤0.3%/否则DEGRADED; 单笔超ACCEPTABLE线留痕; 追踪只评估不改执行(三维解耦); 纯函数可单测
# [MODIFY-GUARD] docs/03_modules/MOD-SELL-012/
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidFillRecordError(ZA-SELL-0027)
# [TESTS] tests/sell_decision/test_sell_execution_quality_tracker.py
# [A_module] module_id=MOD-SELL-012 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Sell Execution Quality Tracker — 卖出执行质量追踪 (MOD-SELL-012)

卖出执行的复盘度量：对每笔卖出成交计算滑点（决策价→成交价的损耗），
按成交权重加权聚合，分级产出质量报告：

  - 滑点口径：slippage = (decision_price − executed_price) / decision_price
    （卖出：正值=卖亏，负值=卖得更好）；
  - 分级：加权平均滑点 ≤0.1% → GOOD；≤0.3% → ACCEPTABLE；否则
    DEGRADED（执行通道可能劣化，供执行域排查与 AB 测试执行维度输入）；
  - 单笔滑点超 ACCEPTABLE 线的标的留痕（outlier_symbols）。

追踪只评估、不改执行（与选股策略/执行算法零耦合）。

纪律：纯函数、无 IO；成交记录由调用方注入（禁自造数据管道）。
Version: 1.0.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: fills 参数
#   fields: 参数 fills，类型注解 Sequence[SellFillRecord]
#   code: sell_execution_quality_tracker.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: good_threshold_pct 参数
#   fields: 参数 good_threshold_pct（无注解）
#   code: sell_execution_quality_tracker.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: acceptable_threshold_pct 参数
#   fields: 参数 acceptable_threshold_pct（无注解）
#   code: sell_execution_quality_tracker.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① evaluate_execution_quality
#   name_en: evaluate_execution_quality
#   intro: 评估卖出执行质量（纯函数）。
#   desc: 评估卖出执行质量（纯函数）。 Args: fills: 卖出成交记录 good_threshold_pct: GOOD 线上限 ≥0（默认 0.1%） acceptable_th…；源码 L164-L245
#   inputs: fills good_threshold_pct acceptable_threshold_pct
#   outputs: ExecutionQualityReport
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: ExecutionQualityReport
#   name_en: ExecutionQualityReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: D-EX-CORE(执行质量回执) ; MOD-SELL-011(AB测试执行维度输入) ; D_RISK
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "ExecutionQualityGrade",
    "ExecutionQualityReport",
    "FillSlippage",
    "InvalidFillRecordError",
    "SellFillRecord",
    "evaluate_execution_quality",
]

_DEFAULT_GOOD_THRESHOLD: Final = 0.001  # ≤0.1% GOOD
_DEFAULT_ACCEPTABLE_THRESHOLD: Final = 0.003  # ≤0.3% ACCEPTABLE


class ExecutionQualityGrade(str, Enum):
    """执行质量分级。"""

    GOOD = "GOOD"
    ACCEPTABLE = "ACCEPTABLE"
    DEGRADED = "DEGRADED"


class InvalidFillRecordError(ZephyrBaseError):
    """卖出成交记录非法（价格非正/权重越界/标的为空）。"""

    error_code = "ZA-SELL-0027"


@dataclass(frozen=True)
class SellFillRecord:
    """单笔卖出成交记录。

    Attributes:
        symbol: 标的代码
        decision_price: 决策时基准价（>0）
        executed_price: 实际成交均价（>0）
        weight: 成交权重 ≥0（组合权重口径，用于加权）
    """

    symbol: str
    decision_price: float
    executed_price: float
    weight: float


@dataclass(frozen=True)
class FillSlippage:
    """单笔滑点明细。

    Attributes:
        symbol: 标的
        slippage_pct: 滑点（正=卖亏）
        weight: 成交权重
    """

    symbol: str
    slippage_pct: float
    weight: float


@dataclass(frozen=True)
class ExecutionQualityReport:
    """执行质量报告（frozen 不可变）。

    Attributes:
        fills: 单笔滑点明细（按输入顺序）
        avg_slippage_pct: 权重加权平均滑点
        max_slippage_pct: 最大单笔滑点
        worst_symbol: 最差标的
        grade: 质量分级
        outlier_symbols: 单笔超 ACCEPTABLE 线的标的（留痕）
        warnings: 预警
    """

    fills: tuple[FillSlippage, ...]
    avg_slippage_pct: float
    max_slippage_pct: float
    worst_symbol: str
    grade: ExecutionQualityGrade
    outlier_symbols: tuple[str, ...]
    warnings: tuple[str, ...] = field(default_factory=tuple)


def evaluate_execution_quality(
    fills: Sequence[SellFillRecord],
    *,
    good_threshold_pct: float = _DEFAULT_GOOD_THRESHOLD,
    acceptable_threshold_pct: float = _DEFAULT_ACCEPTABLE_THRESHOLD,
) -> ExecutionQualityReport:
    """评估卖出执行质量（纯函数）。

    Args:
        fills: 卖出成交记录
        good_threshold_pct: GOOD 线上限 ≥0（默认 0.1%）
        acceptable_threshold_pct: ACCEPTABLE 线上限 ≥0（默认 0.3%，须 ≥good）

    Returns:
        ExecutionQualityReport

    Raises:
        InvalidFillRecordError: 输入非法
    """
    for name, v in (("good_threshold_pct", good_threshold_pct), ("acceptable_threshold_pct", acceptable_threshold_pct)):
        if not math.isfinite(v) or v < 0.0:
            raise InvalidFillRecordError(f"{name} 非法（须为有限非负值），got {v}")
    if good_threshold_pct > acceptable_threshold_pct:
        raise InvalidFillRecordError(
            f"good_threshold({good_threshold_pct}) 不可超过 acceptable_threshold({acceptable_threshold_pct})"
        )

    details: list[FillSlippage] = []
    for f in fills:
        if not f.symbol:
            raise InvalidFillRecordError("成交记录 symbol 为空")
        if not math.isfinite(f.decision_price) or f.decision_price <= 0.0:
            raise InvalidFillRecordError(f"标的 {f.symbol} 决策价非法（须为正有限值），got {f.decision_price}")
        if not math.isfinite(f.executed_price) or f.executed_price <= 0.0:
            raise InvalidFillRecordError(f"标的 {f.symbol} 成交价非法（须为正有限值），got {f.executed_price}")
        if not math.isfinite(f.weight) or f.weight < 0.0:
            raise InvalidFillRecordError(f"标的 {f.symbol} 成交权重非法（须为有限非负值），got {f.weight}")
        slip = (f.decision_price - f.executed_price) / f.decision_price
        details.append(FillSlippage(symbol=f.symbol, slippage_pct=slip, weight=f.weight))

    if not details:
        return ExecutionQualityReport(
            fills=(),
            avg_slippage_pct=0.0,
            max_slippage_pct=0.0,
            worst_symbol="",
            grade=ExecutionQualityGrade.GOOD,
            outlier_symbols=(),
            warnings=(),
        )

    total_weight = sum(d.weight for d in details)
    avg = (
        sum(d.slippage_pct * d.weight for d in details) / total_weight
        if total_weight > 0.0
        else sum(d.slippage_pct for d in details) / len(details)
    )
    worst = max(details, key=lambda d: d.slippage_pct)

    if avg <= good_threshold_pct:
        grade = ExecutionQualityGrade.GOOD
    elif avg <= acceptable_threshold_pct:
        grade = ExecutionQualityGrade.ACCEPTABLE
    else:
        grade = ExecutionQualityGrade.DEGRADED

    outliers = tuple(d.symbol for d in details if d.slippage_pct > acceptable_threshold_pct)
    warnings: list[str] = []
    if grade is ExecutionQualityGrade.DEGRADED:
        warnings.append(f"卖出执行平均滑点 {avg:.3%} 超 ACCEPTABLE 线 {acceptable_threshold_pct:.3%}，执行通道疑似劣化")
    for sym in outliers:
        warnings.append(f"标的 {sym} 单笔滑点超 ACCEPTABLE 线（留痕复盘）")

    return ExecutionQualityReport(
        fills=tuple(details),
        avg_slippage_pct=avg,
        max_slippage_pct=worst.slippage_pct,
        worst_symbol=worst.symbol,
        grade=grade,
        outlier_symbols=outliers,
        warnings=tuple(warnings),
    )
