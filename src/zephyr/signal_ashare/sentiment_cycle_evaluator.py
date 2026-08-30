# [BLUEPRINT] MOD-SIG-065 | 待统筹登记（28号 memo §3.3 标准签名⑥ + 30号 §6.3）
# [MODULE] zephyr.signal_ashare.sentiment_cycle_evaluator
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.sentiment_cycle(SentimentPhase/PHASE_ORDER/evaluate_locator_accuracy)
# [CONSUMERS] G07 验证施工（隐形驱动验证时同步评估定位器准确率）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 按 28号 §3.3 标准签名⑥实现（evaluate_locator_accuracy 语义扩展）；历史回测口径（预测序列 vs 实际序列）；错判代价不对称 → 相邻阶段容错率；零样本 → 全零不抛
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/28_sentiment_cycle_trading.md §3.3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入序列长度不一致 → ValueError（fail-closed）；非法阶段名 → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_sentiment_cycle_evaluator.py
# [A_module] module_id=MOD-SIG-065 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-SIG-065 — 情绪周期定位器准确率评估器骨架（28号 §3.3 标准签名⑥）。

设计真源：28号 memo §3.3（定位器算法）+ §6 待裁定（定位器准确率历史回测
→ G07 验证施工时同步评估）+ 30号 §6.3（错判代价大，需"置信度<60%→默认保守"兜底）。

标准签名⑥（28号 §3.10）：
    evaluate_locator_accuracy(predicted_phases, actual_phases) -> dict[str, float]

本模块实现：
- 精确率（accuracy）：预测 == 实际 占比；
- 相邻阶段容错率（adjacent_tolerance_rate）：|预测索引 - 实际索引| == 1 占比
  （情绪周期相邻阶段语义接近，错判代价低于跨阶段错判）；
- 分阶段召回率（per_phase_recall）：各阶段被正确识别的比例；
- 混淆矩阵（confusion_matrix）：5×5 计数矩阵（PHASE_ORDER 轴）；
- 零样本：全零返回不抛（骨架期数据积累前常态）。

与 sentiment_cycle.evaluate_locator_accuracy 的关系：本模块是该标准签名的
生产实现载体（sentiment_cycle 内为纯函数版，本模块增加分阶段召回/混淆矩阵
与历史回测口径装配，供 G07 验证施工消费）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: predicted_phases 参数
#   fields: 参数 predicted_phases，类型注解 list[SentimentPhase]
#   code: sentiment_cycle_evaluator.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: actual_phases 参数
#   fields: 参数 actual_phases，类型注解 list[SentimentPhase]
#   code: sentiment_cycle_evaluator.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: records 参数
#   fields: 参数 records，类型注解 list[PhasePredictionRecord]
#   code: sentiment_cycle_evaluator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SentimentCycleEvalReport
#   name_en: SentimentCycleEvalReport
#   intro: 情绪周期定位器评估报告（JSON 可序列化）。
#   desc: 情绪周期定位器评估报告（JSON 可序列化）。；公共方法（定义序）: to_dict；源码 L129-L148
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② evaluate_locator_accuracy
#   name_en: evaluate_locator_accuracy
#   intro: 标准签名⑥：评估定位器准确率（28号 §3.3 + §3.10）。
#   desc: 标准签名⑥：评估定位器准确率（28号 §3.3 + §3.10）。 除精确率外计算"相邻阶段容错率"（错判代价不对称，相邻阶段语义接近）。 Args: predicted_pha…；源码 L161-L181
#   inputs: predicted_phases actual_phases
#   outputs: dict[str, float]
# - id: A3
#   name_zh: ③ evaluate_from_records
#   name_en: evaluate_from_records
#   intro: 从历史回测记录评估定位器准确率（扩展版：分阶段召回 + 混淆矩阵）。
#   desc: 从历史回测记录评估定位器准确率（扩展版：分阶段召回 + 混淆矩阵）。 Args: records: 单日预测记录列表（自动按 trade_date 升序重排）。 Returns:…；源码 L184-L247
#   inputs: records
#   outputs: SentimentCycleEvalReport
#   （注：A3 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: dict[str, float]
#   name_en: dict[str, float]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: G07 验证施工（隐形驱动验证时同步评估定位器准确率）
# - id: O2
#   name_zh: SentimentCycleEvalReport
#   name_en: SentimentCycleEvalReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: G07 验证施工（隐形驱动验证时同步评估定位器准确率）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final

from zephyr.signal_ashare.sentiment_cycle import (
    PHASE_ORDER,
    SentimentPhase,
)
from zephyr.signal_ashare.sentiment_cycle import (
    evaluate_locator_accuracy as _base_evaluate,
)

__all__: Final = [
    "SentimentCycleEvalReport",
    "evaluate_locator_accuracy",
    "evaluate_from_records",
]


@dataclass(frozen=True)
class PhasePredictionRecord:
    """单日定位器预测记录（历史回测输入）。"""

    trade_date: str  # YYYY-MM-DD
    predicted_phase: SentimentPhase  # 预测阶段
    actual_phase: SentimentPhase  # 实际阶段（事后标注）
    confidence: float | None = None  # 预测置信度（可选，用于分桶分析）


@dataclass(frozen=True)
class SentimentCycleEvalReport:
    """情绪周期定位器评估报告（JSON 可序列化）。"""

    n_samples: int
    accuracy: float  # 精确率
    adjacent_tolerance_rate: float  # 相邻阶段容错率
    per_phase_recall: dict[str, float]  # 各阶段召回率（key=阶段中文值）
    confusion_matrix: dict[str, dict[str, int]]  # 混淆矩阵（实际→预测→计数）
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典。"""
        return {
            "n_samples": self.n_samples,
            "accuracy": self.accuracy,
            "adjacent_tolerance_rate": self.adjacent_tolerance_rate,
            "per_phase_recall": self.per_phase_recall,
            "confusion_matrix": self.confusion_matrix,
            "notes": self.notes,
        }


def _normalize_phase(phase: object) -> SentimentPhase:
    """阶段归一化：SentimentPhase / name / 中文值 → SentimentPhase；非法 → ValueError。"""
    if isinstance(phase, SentimentPhase):
        return phase
    for p in PHASE_ORDER:
        if phase in (p.name, p.value):
            return p
    raise ValueError(f"非法 SentimentPhase: {phase!r}（契约：SentimentPhase/name/中文值）")


def evaluate_locator_accuracy(
    predicted_phases: list[SentimentPhase],
    actual_phases: list[SentimentPhase],
) -> dict[str, float]:
    """标准签名⑥：评估定位器准确率（28号 §3.3 + §3.10）。

    除精确率外计算"相邻阶段容错率"（错判代价不对称，相邻阶段语义接近）。

    Args:
        predicted_phases: 预测阶段序列（SentimentPhase）。
        actual_phases: 实际阶段序列（SentimentPhase，与预测等长）。

    Returns:
        {"accuracy": float, "adjacent_tolerance_rate": float, "n_samples": float}

    Raises:
        ValueError: 序列长度不一致（fail-closed）。
    """
    if len(predicted_phases) != len(actual_phases):
        raise ValueError(f"预测/实际序列长度不一致: {len(predicted_phases)} vs {len(actual_phases)}")
    return _base_evaluate(predicted_phases, actual_phases)


def evaluate_from_records(
    records: list[PhasePredictionRecord],
) -> SentimentCycleEvalReport:
    """从历史回测记录评估定位器准确率（扩展版：分阶段召回 + 混淆矩阵）。

    Args:
        records: 单日预测记录列表（自动按 trade_date 升序重排）。

    Returns:
        SentimentCycleEvalReport（零样本 → 全零 + notes 留痕）。

    Raises:
        ValueError: 记录非法（trade_date 空/阶段非法）。
    """
    if not records:
        return SentimentCycleEvalReport(
            n_samples=0,
            accuracy=0.0,
            adjacent_tolerance_rate=0.0,
            per_phase_recall={p.value: 0.0 for p in PHASE_ORDER},
            confusion_matrix={p.value: {q.value: 0 for q in PHASE_ORDER} for p in PHASE_ORDER},
            notes=["零样本（历史回测数据未积累）"],
        )

    sorted_records = sorted(records, key=lambda r: r.trade_date)
    for rec in sorted_records:
        if not isinstance(rec.trade_date, str) or not rec.trade_date.strip():
            raise ValueError(f"trade_date 非法（须非空字符串）: {rec.trade_date!r}")
        # 阶段归一化校验（fail-closed）
        _normalize_phase(rec.predicted_phase)
        _normalize_phase(rec.actual_phase)

    predicted = [rec.predicted_phase for rec in sorted_records]
    actual = [rec.actual_phase for rec in sorted_records]

    base = evaluate_locator_accuracy(predicted, actual)

    # 分阶段召回率：actual == phase 的样本中 predicted == phase 占比
    per_phase_recall: dict[str, float] = {}
    for phase in PHASE_ORDER:
        idx = [i for i, a in enumerate(actual) if a == phase]
        if not idx:
            per_phase_recall[phase.value] = 0.0
            continue
        correct = sum(1 for i in idx if predicted[i] == phase)
        per_phase_recall[phase.value] = correct / len(idx)

    # 混淆矩阵（实际→预测→计数）
    confusion: dict[str, dict[str, int]] = {p.value: {q.value: 0 for q in PHASE_ORDER} for p in PHASE_ORDER}
    for p, a in zip(predicted, actual, strict=False):
        confusion[a.value][p.value] += 1

    notes: list[str] = []
    if base["n_samples"] < 30:
        notes.append(f"样本量 n={int(base['n_samples'])} < 30，统计意义有限（30号 §6.3 口径）")

    return SentimentCycleEvalReport(
        n_samples=int(base["n_samples"]),
        accuracy=base["accuracy"],
        adjacent_tolerance_rate=base["adjacent_tolerance_rate"],
        per_phase_recall=per_phase_recall,
        confusion_matrix=confusion,
        notes=notes,
    )
