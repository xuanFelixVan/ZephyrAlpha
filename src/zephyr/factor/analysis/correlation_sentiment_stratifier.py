# [BLUEPRINT] 23_strategy_correlation_validation.md §3.1②④ | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/
# [MODULE] zephyr.factor.analysis.correlation_sentiment_stratifier
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] pandas(仅消费 BM-SEL-23-B 输出, 不 import market_sentiment_analyzer 内部)
# [CONSUMERS] G07 策略相关性验证报告（分层 5×5×5 矩阵）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 纯函数无IO; 置信度<0.60->默认保守(冰点)兜底并留痕; 阶段样本<30标不足; 灰度权重行和=1
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非法阶段名->ValueError; 空标签->ValueError
# [TESTS] tests/factor/test_correlation_sentiment_stratifier.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: 逐日情绪标签 labels(5档中文) + confidences(灰度 max(P)) / 灰度结果映射(grayscale_map)
# I2: 策略收益率面板 returns_panel(T×k, 已对交易日)
# F1: 置信度兜底(confidence<0.60->冰点保守, fallback_mask留痕; 30号§6.3定位器错判污染防护)
# A1: build_phase_labels(硬标签+置信度->有效标签Series + 兜底统计)
# A2: labels_from_grayscale(消费 analyze_grayscale() 输出的 duck-type 适配器)
# A3: split_by_phase(按5阶段切面板, 每阶段标注样本量/充足标记>=30)
# A4: phase_weight_frame(灰度软分配权重帧, 30号§6.5过渡期天按P比例; 兜底行全押保守阶段)
# O1: PhaseLabelResult / dict[phase→PhaseSlice] / 权重DataFrame
# [/ALGO_FLOW]
"""
D_FACTOR — G07 情绪周期分层标签器（23 号 memo §3.1②，消费 BM-SEL-23-B）

用情绪周期 4+1 阶段（冰点/反核/主升/疯狂/退潮）给每个交易日打标签，分 5 段
分别算相关矩阵——全样本相关性可能被主升/疯狂态主导（"情绪 beta 穿多件衣服"
判据要求各阶段都看）。主升/疯狂态即高压力期，分层 = 条件相关，隐式覆盖
stress correlation（invistaja 2026-08 "相关性在压力期锁定上升"）。

置信度兜底：BM-SEL-23-B 定位器错判会污染分层标签（30 号 §6.3），
confidence<0.60 → 默认保守（冰点）并留痕 fallback_mask。
灰度软分配（30 号 §6.5）：过渡期天按 P 比例贡献给多阶段，缓解稀有态样本不足。

本模块只消费 market_sentiment_analyzer 的输出契约（duck-typed），不 import 其内部；
5 档中文阶段名与 SentimentPhase enum value 一致（BM-SEL-23-B 输出契约）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: labels 参数
#   fields: 参数 labels，类型注解 pd.Series
#   code: correlation_sentiment_stratifier.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: confidences 参数
#   fields: 参数 confidences，类型注解 pd.Series | None
#   code: correlation_sentiment_stratifier.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: confidence_threshold 参数
#   fields: 参数 confidence_threshold，类型注解 float
#   code: correlation_sentiment_stratifier.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: fallback_phase 参数
#   fields: 参数 fallback_phase，类型注解 str
#   code: correlation_sentiment_stratifier.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① build_phase_labels
#   name_en: build_phase_labels
#   intro: 由硬标签+置信度构建有效分层标签（低置信度→保守兜底）。
#   desc: 由硬标签+置信度构建有效分层标签（低置信度→保守兜底）。 Args: labels: index=交易日，values=5 档中文阶段名（BM-SEL-23-B 硬标签） con…；源码 L185-L222
#   inputs: labels confidences confidence_threshold fallback_phase
#   outputs: PhaseLabelResult
# - id: A2
#   name_zh: ② labels_from_grayscale
#   name_en: labels_from_grayscale
#   intro: 消费 analyze_grayscale() 输出映射（duck-typed）构建分层标签。
#   desc: 消费 analyze_grayscale() 输出映射（duck-typed）构建分层标签。 每个值须含 phase_prob/dominant_phase/confidence…；源码 L225-L255
#   inputs: grayscale_map confidence_threshold fallback_phase
#   outputs: PhaseLabelResult
# - id: A3
#   name_zh: ③ split_by_phase
#   name_en: split_by_phase
#   intro: 按情绪阶段切分收益率面板（5 阶段全量返回，缺样本阶段标注不足）。
#   desc: 按情绪阶段切分收益率面板（5 阶段全量返回，缺样本阶段标注不足）。 Args: returns_panel: 对齐收益率面板（T×k） labels: 有效阶段标签（build_…；源码 L258-L287
#   inputs: returns_panel labels min_samples
#   outputs: dict[str, PhaseSlice]
# - id: A4
#   name_zh: ④ phase_weight_frame
#   name_en: phase_weight_frame
#   intro: 灰度软分配权重帧（30 号 §6.5：过渡期天按 P 比例贡献给多阶段）。
#   desc: 灰度软分配权重帧（30 号 §6.5：过渡期天按 P 比例贡献给多阶段）。 每行为一日的 5 阶段权重（Σ=1）；confidence<阈值的兜底日全押保守阶段 （定位器不可信时…；源码 L290-L328
#   inputs: grayscale_map confidence_threshold fallback_phase
#   outputs: pd.DataFrame
#   （注：A4 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: PhaseLabelResult
#   name_en: PhaseLabelResult
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: G07 策略相关性验证报告（分层 5×5×5 矩阵）
# - id: O2
#   name_zh: dict[str, PhaseSlice]
#   name_en: dict[str, PhaseSlice]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: G07 策略相关性验证报告（分层 5×5×5 矩阵）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import pandas as pd

__all__ = [
    "CANONICAL_PHASES",
    "CONSERVATIVE_FALLBACK_PHASE",
    "DEFAULT_CONFIDENCE_THRESHOLD",
    "MIN_PHASE_SAMPLES",
    "PhaseLabelResult",
    "PhaseSlice",
    "build_phase_labels",
    "labels_from_grayscale",
    "phase_weight_frame",
    "split_by_phase",
]

#: BM-SEL-23-B 情绪周期 4+1 阶段（与 SentimentPhase enum value 一致的输出契约）
CANONICAL_PHASES: tuple[str, ...] = ("冰点", "反核", "主升", "疯狂", "退潮")
#: 置信度兜底阈值（23 号 memo §3.1②: 置信度<60%→默认保守）
DEFAULT_CONFIDENCE_THRESHOLD = 0.60
#: 默认保守阶段（低置信度时按冰点处理——最保守情绪假设）
CONSERVATIVE_FALLBACK_PHASE = "冰点"
#: 分层相关性可信的最小样本量（23 号 memo §3.1④: 每阶段 ≥30 交易日）
MIN_PHASE_SAMPLES = 30


@dataclass(frozen=True)
class PhaseLabelResult:
    """分层标签结果（不可变）。

    Attributes:
        labels: 有效阶段标签 Series（index=交易日，值为 5 档中文阶段）
        fallback_mask: 兜底掩码 Series（True=该日因低置信度被改判保守阶段）
        fallback_count: 兜底天数
        confidence_threshold: 使用的置信度阈值
    """

    labels: pd.Series
    fallback_mask: pd.Series
    fallback_count: int
    confidence_threshold: float


@dataclass(frozen=True)
class PhaseSlice:
    """单情绪阶段的切分结果（不可变）。

    Attributes:
        phase: 阶段名
        panel: 该阶段的收益率子面板（可能为空 DataFrame）
        n_obs: 样本量
        sufficient: n_obs >= min_samples（不足则该阶段相关性不可信，仅标注）
    """

    phase: str
    panel: pd.DataFrame
    n_obs: int
    sufficient: bool


def _validate_phase(value: Any) -> str:
    """校验阶段名属于 BM-SEL-23-B 5 档契约。"""
    phase = str(value)
    if phase not in CANONICAL_PHASES:
        raise ValueError(f"非法情绪阶段: {value!r}（BM-SEL-23-B 契约: {CANONICAL_PHASES}）")
    return phase


def build_phase_labels(
    labels: pd.Series,
    confidences: pd.Series | None = None,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    fallback_phase: str = CONSERVATIVE_FALLBACK_PHASE,
) -> PhaseLabelResult:
    """由硬标签+置信度构建有效分层标签（低置信度→保守兜底）。

    Args:
        labels: index=交易日，values=5 档中文阶段名（BM-SEL-23-B 硬标签）
        confidences: index 同 labels 的置信度（None=全 1.0，即硬标签全信）
        confidence_threshold: 兜底阈值（默认 0.60）
        fallback_phase: 保守兜底阶段（默认 冰点）

    Returns:
        PhaseLabelResult

    Raises:
        ValueError: 空标签 / 非法阶段名 / confidences 与 labels 长度不一致
    """
    if labels is None or len(labels) == 0:
        raise ValueError("labels 不能为空")
    _validate_phase(fallback_phase)
    validated = labels.map(_validate_phase)
    if confidences is None:
        conf = pd.Series(1.0, index=labels.index)
    else:
        if len(confidences) != len(labels):
            raise ValueError("confidences 与 labels 长度不一致")
        conf = confidences.reindex(labels.index).fillna(0.0)
    fallback_mask = conf < confidence_threshold
    effective = validated.where(~fallback_mask, fallback_phase)
    return PhaseLabelResult(
        labels=effective,
        fallback_mask=fallback_mask,
        fallback_count=int(fallback_mask.sum()),
        confidence_threshold=confidence_threshold,
    )


def labels_from_grayscale(
    grayscale_map: Mapping[Any, Any],
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    fallback_phase: str = CONSERVATIVE_FALLBACK_PHASE,
) -> PhaseLabelResult:
    """消费 analyze_grayscale() 输出映射（duck-typed）构建分层标签。

    每个值须含 phase_prob/dominant_phase/confidence（MarketSentimentGrayscaleResult
    或同形 dict）。等价于 dominant_phase 硬标签 + confidence 兜底。

    Args:
        grayscale_map: 交易日 → 灰度结果（属性或键访问均可）
        confidence_threshold: 兜底阈值
        fallback_phase: 保守兜底阶段

    Returns:
        PhaseLabelResult（index=排序后交易日）
    """
    if not grayscale_map:
        raise ValueError("grayscale_map 不能为空")

    def _get(obj: Any, name: str) -> Any:
        return obj.get(name) if isinstance(obj, Mapping) else getattr(obj, name)

    dates = sorted(grayscale_map.keys())
    labels = pd.Series(
        [_validate_phase(_get(grayscale_map[d], "dominant_phase")) for d in dates],
        index=pd.Index(dates),
    )
    conf = pd.Series([float(_get(grayscale_map[d], "confidence")) for d in dates], index=labels.index)
    return build_phase_labels(labels, conf, confidence_threshold, fallback_phase)


def split_by_phase(
    returns_panel: pd.DataFrame,
    labels: pd.Series,
    min_samples: int = MIN_PHASE_SAMPLES,
) -> dict[str, PhaseSlice]:
    """按情绪阶段切分收益率面板（5 阶段全量返回，缺样本阶段标注不足）。

    Args:
        returns_panel: 对齐收益率面板（T×k）
        labels: 有效阶段标签（build_phase_labels 产出；与面板按 index 交集对齐）
        min_samples: 阶段相关性可信的最小样本量（默认 30，memo §3.1④）

    Returns:
        {阶段名: PhaseSlice}（5 阶段全量；无样本阶段 panel 为空、sufficient=False）

    Raises:
        ValueError: 面板为空 / min_samples<1
    """
    if returns_panel is None or returns_panel.empty:
        raise ValueError("returns_panel 不能为空")
    if min_samples < 1:
        raise ValueError(f"min_samples 必须 >=1, got {min_samples}")
    common = returns_panel.index.intersection(labels.index)
    panel = returns_panel.loc[common]
    lab = labels.loc[common]
    out: dict[str, PhaseSlice] = {}
    for phase in CANONICAL_PHASES:
        sub = panel[lab == phase]
        out[phase] = PhaseSlice(phase, sub, len(sub), len(sub) >= min_samples)
    return out


def phase_weight_frame(
    grayscale_map: Mapping[Any, Any],
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    fallback_phase: str = CONSERVATIVE_FALLBACK_PHASE,
) -> pd.DataFrame:
    """灰度软分配权重帧（30 号 §6.5：过渡期天按 P 比例贡献给多阶段）。

    每行为一日的 5 阶段权重（Σ=1）；confidence<阈值的兜底日全押保守阶段
    （定位器不可信时不把权重分散到可能误判的阶段）。

    Args:
        grayscale_map: 交易日 → 灰度结果（phase_prob/dominant_phase/confidence）
        confidence_threshold: 兜底阈值
        fallback_phase: 保守兜底阶段

    Returns:
        DataFrame（index=交易日，columns=CANONICAL_PHASES，行和=1）
    """
    if not grayscale_map:
        raise ValueError("grayscale_map 不能为空")

    def _get(obj: Any, name: str) -> Any:
        return obj.get(name) if isinstance(obj, Mapping) else getattr(obj, name)

    dates = sorted(grayscale_map.keys())
    rows: list[list[float]] = []
    for d in dates:
        result = grayscale_map[d]
        prob = {_validate_phase(k): float(v) for k, v in dict(_get(result, "phase_prob")).items()}
        confidence = float(_get(result, "confidence"))
        if confidence < confidence_threshold:
            row = [1.0 if p == fallback_phase else 0.0 for p in CANONICAL_PHASES]
        else:
            total = sum(prob.get(p, 0.0) for p in CANONICAL_PHASES)
            row = [prob.get(p, 0.0) / total if total > 0 else 0.0 for p in CANONICAL_PHASES]
            if total <= 0:  # 概率全零退化 → 保守兜底
                row = [1.0 if p == fallback_phase else 0.0 for p in CANONICAL_PHASES]
        rows.append(row)
    return pd.DataFrame(rows, index=pd.Index(dates), columns=list(CANONICAL_PHASES))
