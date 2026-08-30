# [BLUEPRINT] MOD-PF-015 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/23_strategy_correlation_validation.md | §
# [MODULE] zephyr.pf_core.strategy_correlation_pipeline
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] numpy; pandas; zephyr.factor.analysis.correlation_preprocessing; zephyr.factor.analysis.correlation_sentiment_stratifier; zephyr.factor.analysis.correlation_block_bootstrap; zephyr.factor.analysis.correlation_neff; zephyr.factor.analysis.correlation_drift_monitor; zephyr.factor.analysis.correlation_overfitting_audit(类型)
# [CONSUMERS] G07 施工前一次性验证批次; MOD-PA-004 门禁(strategy_correlation_gate)上游生产者
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 纯函数无IO; 输入为算术日收益率→伪净值(1+r).cumprod()复用预处理管线(ln(1+r)对数口径); 交易日交集对齐禁前向填充; 战略级阈值0.6与门禁运营级0.85/0.90互补非冲突; 报告七部分与23号文§3.1⑤模板一一对应; 分层样本<30只标注不抛错
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空面板/列数<2/收益率<=-1->ValueError; phase_labels与grayscale_map同时给->ValueError; 样本不足环节降级为None不抛错
# [TESTS] tests/pf_core/test_strategy_correlation_pipeline.py
# [TTL] permanent
# [ALGO_FLOW]
# 层: 输入
# - id: I1 策略日收益率面板 returns(T×k, index=date, columns=strategy_names)
# - id: I2 可选 BM-SEL-23-B 情绪分层标签(phase_labels+confidences 或 grayscale_map)
# - id: I3 可选过拟合审计结果/正交维度映射(第6/7部分留口)
# 层: 算法
# - id: A1 预处理: 伪净值→preprocess_strategy_returns(ln(1+r)+ADF+Modified Z-score标注+交集对齐)
# - id: A2 双相关矩阵: compute_strategy_correlation(Pearson+Spearman)
# - id: A3 分层: build_phase_labels/labels_from_grayscale→split_by_phase→逐阶段双矩阵(消费 BM-SEL-23-B)
# - id: A4 block-bootstrap CI: bootstrap_correlation_ci(2000×同步行重采样+Fisher z互验)
# - id: A5 Neff: effective_bets(Ledoit-Wolf收缩前置)
# - id: A6 结论: 三条件交叉(各阶段>0.6对数>=3 / Neff<3 / 两两最大>0.6, 任一触发即REVIEW_REQUIRED)
# - id: A7 漂移监控: compute_rolling_spearman(63日)+assess_pair_drift(CUSUM k=0.5σ/h=4σ + PSI>0.2/0.4)
# 层: 输出
# - id: O1 StrategyCorrelationReport(七部分+漂移附录) + render_markdown(23号文报告模板)
# [/ALGO_FLOW]
"""
G07 策略间相关性验证管线骨架（23 号 memo §3.1⑤ 七部分报告模板）。

编排层——不重复造轮子，全部计算委托 factor/analysis 已测试的五个引擎：
  1. correlation_preprocessing（对数收益率统一 + ADF + 异常值标注 + 交易日对齐）
  2. correlation_sentiment_stratifier（BM-SEL-23-B 情绪周期 4+1 分层标签消费）
  3. correlation_block_bootstrap（multivariate stationary bootstrap CI + Fisher z 互验）
  4. correlation_neff（Ledoit-Wolf 收缩前置的组合层有效下注数）
  5. correlation_drift_monitor（§5.4 CUSUM-PSI 上线后漂移监控）

输入为策略日收益率面板（算术口径），内部构造伪净值 (1+r).cumprod() 复用
preprocess_strategy_returns——ln(nav_t/nav_{t-1}) ≡ ln(1+r_t)，对数口径统一。
相关性必须用 PnL stream，禁用 binary 信号序列（tetrachoric 效应，Soloviov 2026）。

阈值分层（23 号 memo §3.1③）：0.6 战略级"重新审视"（本管线产出），
0.85/0.90 运营级 REJECT/HARD_REJECT（MOD-PA-004 门禁消费），两者互补。

第 6 部分（过拟合检测矩阵）需全量参数搜索 history（T×N returns matrix，memo §7
待定问题"参数搜索 history 的留存"），本管线只接受调用方预算好的
OverfitAuditResult 映射作留口；第 7 部分（正交性验证）接受策略→正交维度映射
做覆盖度检查，量化互验以第 4 部分 Neff 为准。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: returns 参数
#   fields: 参数 returns，类型注解 pd.DataFrame
#   code: strategy_correlation_pipeline.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: params 参数
#   fields: 参数 params（无注解）
#   code: strategy_correlation_pipeline.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: report 参数
#   fields: 参数 report，类型注解 StrategyCorrelationReport
#   code: strategy_correlation_pipeline.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① run_strategy_correlation_pipeline
#   name_en: run_strategy_correlation_pipeline
#   intro: G07 策略间相关性验证管线（施工前一次性，非 runtime 周期任务）。
#   desc: G07 策略间相关性验证管线（施工前一次性，非 runtime 周期任务）。 Args: returns: 策略日收益率面板（算术口径，index=date，columns=策略…；源码 L458-L490
#   inputs: returns params
#   outputs: StrategyCorrelationReport
# - id: A2
#   name_zh: ② render_markdown
#   name_en: render_markdown
#   intro: 按 23 号 memo §3.1⑤ 七部分模板渲染报告（markdown）。
#   desc: 按 23 号 memo §3.1⑤ 七部分模板渲染报告（markdown）。；源码 L700-L711
#   inputs: report
#   outputs: str
#   （注：A2 之后另有 7 个公共定义未列入（含 7 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: StrategyCorrelationReport
#   name_en: StrategyCorrelationReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: G07 施工前一次性验证批次; MOD-PA-004 门禁(strategy_correlation_gate)上游生产者
# - id: O2
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: G07 施工前一次性验证批次; MOD-PA-004 门禁(strategy_correlation_gate)上游生产者
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Any, Final, Mapping

import numpy as np
import pandas as pd

from zephyr.factor.analysis.correlation_block_bootstrap import (
    MIN_OBS as BOOTSTRAP_MIN_OBS,
)
from zephyr.factor.analysis.correlation_block_bootstrap import (
    BootstrapCIResult,
    bootstrap_correlation_ci,
)
from zephyr.factor.analysis.correlation_drift_monitor import (
    DEFAULT_ROLLING_WINDOW,
    PairDriftReport,
    assess_pair_drift,
    compute_rolling_spearman,
)
from zephyr.factor.analysis.correlation_neff import NeffResult, effective_bets
from zephyr.factor.analysis.correlation_overfitting_audit import OverfitAuditResult
from zephyr.factor.analysis.correlation_preprocessing import (
    PreprocessResult,
    compute_strategy_correlation,
    preprocess_strategy_returns,
)
from zephyr.factor.analysis.correlation_sentiment_stratifier import (
    CANONICAL_PHASES,
    DEFAULT_CONFIDENCE_THRESHOLD,
    MIN_PHASE_SAMPLES,
    PhaseLabelResult,
    build_phase_labels,
    labels_from_grayscale,
    split_by_phase,
)

__all__: Final = [
    "DEFAULT_NEFF_MIN",
    "DEFAULT_STRATEGIC_THRESHOLD",
    "ORTHOGONAL_DIMENSIONS",
    "ConclusionSection",
    "FullSampleSection",
    "OrthogonalitySection",
    "PhaseMatrixSection",
    "StratifiedSection",
    "StrategyCorrelationParams",
    "StrategyCorrelationReport",
    "render_markdown",
    "run_strategy_correlation_pipeline",
]

#: 战略级重新审视阈值（23 号 memo §3.1③；与门禁运营级 0.85/0.90 互补非冲突）
DEFAULT_STRATEGIC_THRESHOLD = 0.6
#: Neff 战略级下限（memo §3.1⑤: 两两都<0.6 但 Neff<3 仍危险）
DEFAULT_NEFF_MIN = 3.0
#: 触发"各阶段高相关"审视的分层对数门槛（memo §3.1⑤ 第5部分条件①）
PHASE_HIGH_CORR_PAIRS_MIN = 3
#: LW 收缩强度警惕线（启发式：α 大=原始矩阵噪声大/相关结构弱，Neff 偏乐观需共读）
LW_ALPHA_CAVEAT = 0.5
#: 第 7 部分三正交维度（memo §3.1⑤，mental-momentum.ai 2026-06）
ORTHOGONAL_DIMENSIONS: tuple[str, ...] = ("趋势方向", "执行时机", "风险大小")


@dataclass(frozen=True)
class FullSampleSection:
    """报告第 1 部分：全样本双版本相关矩阵。

    Attributes:
        pearson/spearman: k×k 相关矩阵（对角=1）
        n_obs: 对齐后样本量 T
        strategies: 策略名（列序）
    """

    pearson: pd.DataFrame
    spearman: pd.DataFrame
    n_obs: int
    strategies: tuple[str, ...]


@dataclass(frozen=True)
class PhaseMatrixSection:
    """报告第 2 部分的单阶段切片。

    Attributes:
        phase: BM-SEL-23-B 5 档阶段名
        n_obs: 该阶段样本量
        sufficient: n_obs >= min_samples（不足则矩阵为 None，仅标注"样本不足"）
        pearson/spearman: 该阶段相关矩阵（不足为 None）
    """

    phase: str
    n_obs: int
    sufficient: bool
    pearson: pd.DataFrame | None
    spearman: pd.DataFrame | None


@dataclass(frozen=True)
class StratifiedSection:
    """报告第 2 部分：5 情绪阶段分层矩阵（BM-SEL-23-B 消费结果）。

    Attributes:
        phases: 5 阶段切片（CANONICAL_PHASES 固定顺序）
        fallback_count: 低置信度兜底天数（定位器错判污染防护留痕）
        confidence_threshold: 使用的置信度阈值
        min_samples: 阶段可信最小样本量
    """

    phases: tuple[PhaseMatrixSection, ...]
    fallback_count: int
    confidence_threshold: float
    min_samples: int


@dataclass(frozen=True)
class ConclusionSection:
    """报告第 5 部分："情绪 beta 穿多件衣服"判定（多指标交叉验证）。

    三条件任一触发即 REVIEW_REQUIRED（memo §3.1⑤）：
      ① 任一（样本充足的）情绪阶段内 Spearman ρ>threshold 的对数 >= 3
      ② Neff < neff_min
      ③ 全样本两两最大 Spearman ρ > threshold

    Attributes:
        verdict: "PASS" / "REVIEW_REQUIRED"
        triggers: 触发的条件清单（空=PASS）
        max_pairs_per_phase: ① 单阶段高相关对数最大值（无分层输入为 None=未评估）
        max_pairwise_corr: ③ 全样本两两最大 Spearman ρ
        neff: ② 组合层有效下注数
        lw_alpha: Ledoit-Wolf 收缩强度（α 大即使 Neff>=3 也应警惕，memo v1.4.1 自洽性）
        alpha_caveat: α>LW_ALPHA_CAVEAT 且 Neff 未触发 → Neff 结论偏乐观警告
        threshold/neff_min: 使用的判定阈值
    """

    verdict: str
    triggers: tuple[str, ...]
    max_pairs_per_phase: int | None
    max_pairwise_corr: float
    neff: float
    lw_alpha: float
    alpha_caveat: bool
    threshold: float
    neff_min: float


@dataclass(frozen=True)
class OrthogonalitySection:
    """报告第 7 部分：策略组合正交性验证（三维度覆盖度）。

    Attributes:
        dimension_map: 策略 → 正交维度（趋势方向/执行时机/风险大小）
        covered/uncovered: 已覆盖/未覆盖维度
        degenerate: 覆盖维度 <2 → 组合退化，需引入正交新策略（memo §3.1⑤ 第7部分）
        note: 与 Neff 互验的说明（量化判定以第 4 部分为准）
    """

    dimension_map: dict[str, str]
    covered: tuple[str, ...]
    uncovered: tuple[str, ...]
    degenerate: bool
    note: str


@dataclass(frozen=True)
class StrategyCorrelationParams:
    """G07 策略间相关性验证管线参数对象（封装 17 个可选参数）。

    按功能分组：
      - 情绪分层：phase_labels / phase_confidences / grayscale_map / confidence_threshold / min_phase_samples
      - bootstrap：run_bootstrap / n_bootstrap / block_size
      - 判定阈值：threshold / neff_min
      - 漂移监控：run_drift / drift_window / drift_recent_window
      - 留口：overfit_audits / dimension_map / seed
    """

    phase_labels: pd.Series | None = None
    phase_confidences: pd.Series | None = None
    grayscale_map: Mapping[Any, Any] | None = None
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
    min_phase_samples: int = MIN_PHASE_SAMPLES
    run_bootstrap: bool = True
    n_bootstrap: int = 2000
    block_size: int = 0
    threshold: float = DEFAULT_STRATEGIC_THRESHOLD
    neff_min: float = DEFAULT_NEFF_MIN
    run_drift: bool = True
    drift_window: int = DEFAULT_ROLLING_WINDOW
    drift_recent_window: int = DEFAULT_ROLLING_WINDOW
    overfit_audits: Mapping[str, OverfitAuditResult] | None = None
    dimension_map: Mapping[str, str] | None = None
    seed: int | None = None


@dataclass(frozen=True)
class StrategyCorrelationReport:
    """G07 验证报告（23 号 memo §3.1⑤ 七部分 + §5.4 漂移监控附录）。

    Attributes:
        part1_full_sample: 全样本 Pearson+Spearman 双矩阵
        part2_stratified: 情绪周期 5 阶段分层矩阵（无分层输入为 None）
        part3_bootstrap_ci: block-bootstrap 90% CI + Fisher z 互验（关闭或样本不足为 None）
        part4_neff: 组合层有效下注数（LW 收缩前置）
        part5_conclusion: 战略级判定
        part6_overfitting: 过拟合检测矩阵（调用方预算的 OverfitAuditResult 映射；None=留口）
        part7_orthogonality: 正交性验证（无维度映射为 None=留口）
        drift_monitoring: §5.4 CUSUM-PSI 逐对漂移报告（关闭或样本不足为 None）
        preprocessing: 预处理产出（对齐面板/ADF/异常值标注/非平稳警告）
    """

    part1_full_sample: FullSampleSection
    part2_stratified: StratifiedSection | None
    part3_bootstrap_ci: BootstrapCIResult | None
    part4_neff: NeffResult
    part5_conclusion: ConclusionSection
    part6_overfitting: Mapping[str, OverfitAuditResult] | None
    part7_orthogonality: OrthogonalitySection | None
    drift_monitoring: dict[tuple[str, str], PairDriftReport] | None
    preprocessing: PreprocessResult
    meta: dict[str, Any] = field(default_factory=dict)


def _returns_to_pseudo_nav(returns: pd.DataFrame) -> dict[str, pd.Series]:
    """算术日收益率 → 伪净值映射（每列先 dropna 再 (1+r).cumprod()）。

    ln(nav_t/nav_{t-1}) ≡ ln(1+r_t)，与 preprocess_strategy_returns 的对数口径
    精确一致；r <= -1 时 nav 非正，由 to_log_returns 抛 ValueError（单日跌超
    -100% 对做多策略不可能，属输入错误）。
    """
    nav_map: dict[str, pd.Series] = {}
    for col in returns.columns:
        r = pd.to_numeric(returns[col], errors="coerce").dropna()
        nav_map[str(col)] = (1.0 + r.astype(float)).cumprod()
    return nav_map


def _build_stratified(
    panel: pd.DataFrame,
    label_result: PhaseLabelResult,
    min_samples: int,
) -> StratifiedSection:
    """按情绪阶段切分并逐阶段算双矩阵（样本不足只标注，矩阵 None）。"""
    slices = split_by_phase(panel, label_result.labels, min_samples=min_samples)
    sections: list[PhaseMatrixSection] = []
    for phase in CANONICAL_PHASES:
        sl = slices[phase]
        if sl.sufficient:
            mats = compute_strategy_correlation(sl.panel)
            sections.append(PhaseMatrixSection(phase, sl.n_obs, True, mats["pearson"], mats["spearman"]))
        else:
            sections.append(PhaseMatrixSection(phase, sl.n_obs, False, None, None))
    return StratifiedSection(
        phases=tuple(sections),
        fallback_count=label_result.fallback_count,
        confidence_threshold=label_result.confidence_threshold,
        min_samples=min_samples,
    )


def _offdiag_max(corr: pd.DataFrame) -> float:
    """相关矩阵上三角（不含对角）最大值。"""
    values = corr.to_numpy(dtype=float)
    n = values.shape[0]
    if n < 2:
        return float("nan")
    return float(np.max(values[np.triu_indices(n, k=1)]))


def _build_conclusion(
    spearman_full: pd.DataFrame,
    stratified: StratifiedSection | None,
    neff: NeffResult,
    threshold: float,
    neff_min: float,
) -> ConclusionSection:
    """第 5 部分判定：三条件任一触发即 REVIEW_REQUIRED（以 Spearman 为准，抗打板极值）。"""
    triggers: list[str] = []
    max_pairs: int | None = None
    if stratified is not None:
        counts = [
            int(np.sum(s.spearman.to_numpy(dtype=float)[np.triu_indices(len(s.spearman), k=1)] > threshold))
            for s in stratified.phases
            if s.sufficient and s.spearman is not None and len(s.spearman) >= 2
        ]
        max_pairs = max(counts) if counts else 0
        if max_pairs >= PHASE_HIGH_CORR_PAIRS_MIN:
            triggers.append(f"phase_pairs>={PHASE_HIGH_CORR_PAIRS_MIN}")
    max_pairwise = _offdiag_max(spearman_full)
    if max_pairwise > threshold:
        triggers.append(f"max_pairwise>{threshold}")
    if neff.neff < neff_min:
        triggers.append(f"neff<{neff_min}")
    alpha_caveat = bool(neff.alpha > LW_ALPHA_CAVEAT and neff.neff >= neff_min)
    return ConclusionSection(
        verdict="REVIEW_REQUIRED" if triggers else "PASS",
        triggers=tuple(triggers),
        max_pairs_per_phase=max_pairs,
        max_pairwise_corr=max_pairwise,
        neff=neff.neff,
        lw_alpha=neff.alpha,
        alpha_caveat=alpha_caveat,
        threshold=threshold,
        neff_min=neff_min,
    )


def _build_orthogonality(dimension_map: Mapping[str, str]) -> OrthogonalitySection:
    """第 7 部分：三正交维度覆盖度检查（定性映射；量化互验以 Neff 为准）。"""
    invalid = set(dimension_map.values()) - set(ORTHOGONAL_DIMENSIONS)
    if invalid:
        raise ValueError(f"非法正交维度: {sorted(invalid)}（契约: {ORTHOGONAL_DIMENSIONS}）")
    covered = tuple(d for d in ORTHOGONAL_DIMENSIONS if d in set(dimension_map.values()))
    uncovered = tuple(d for d in ORTHOGONAL_DIMENSIONS if d not in covered)
    degenerate = len(covered) < 2
    note = (
        "覆盖维度<2→组合退化，需引入正交新策略；与第 4 部分 Neff 互验"
        "（两结论不一致时以正交性维度为准——维度退化是更深层的过拟合，memo §3.1⑤⑦）"
    )
    return OrthogonalitySection(dict(dimension_map), covered, uncovered, degenerate, note)


def _build_drift(
    panel: pd.DataFrame,
    spearman_full: pd.DataFrame,
    window: int,
    recent_window: int,
) -> dict[tuple[str, str], PairDriftReport]:
    """§5.4 逐对 CUSUM-PSI 漂移监控（基线 ρ₀=全样本 Spearman 点估计）。

    PSI 基线分布=滚动 ρ 序列除近 recent_window 日外的部分，近期分布=近
    recent_window 日；基线段不足 2 点时只跑 CUSUM（PSI 留 None）。
    """
    reports: dict[tuple[str, str], PairDriftReport] = {}
    names = list(panel.columns)
    for a, b in itertools.combinations(names, 2):
        rho = compute_rolling_spearman(panel[a], panel[b], window=window)
        valid = rho.dropna()
        baseline_dist: pd.Series | None = None
        recent_dist: pd.Series | None = None
        if len(valid) > recent_window + 1:
            baseline_dist = valid.iloc[:-recent_window]
            recent_dist = valid.iloc[-recent_window:]
        reports[(a, b)] = assess_pair_drift(
            rho,
            baseline_rho=float(spearman_full.loc[a, b]),
            baseline_dist=baseline_dist,
            recent_dist=recent_dist,
        )
    return reports


def run_strategy_correlation_pipeline(
    returns: pd.DataFrame,
    *,
    params: StrategyCorrelationParams | None = None,
) -> StrategyCorrelationReport:
    """G07 策略间相关性验证管线（施工前一次性，非 runtime 周期任务）。

    Args:
        returns: 策略日收益率面板（算术口径，index=date，columns=策略名，k>=2）
        params: 管线参数对象（None=全部默认）；封装 17 个可选参数：
            - 情绪分层：phase_labels / phase_confidences / grayscale_map /
              confidence_threshold / min_phase_samples
            - bootstrap：run_bootstrap / n_bootstrap / block_size
            - 判定阈值：threshold（战略级 0.6）/ neff_min（默认 3.0）
            - 漂移监控：run_drift / drift_window / drift_recent_window
            - 留口：overfit_audits / dimension_map / seed

    Returns:
        StrategyCorrelationReport（七部分 + 漂移附录 + 预处理留痕）

    Raises:
        ValueError: 空面板/列数<2/收益率<=-1/phase_labels 与 grayscale_map 同给
    """
    p = params or StrategyCorrelationParams()

    if returns is None or returns.empty:
        raise ValueError("returns 不能为空")
    if returns.ndim != 2 or returns.shape[1] < 2:
        raise ValueError(f"returns 必须为 T×k 面板且 k>=2, got shape={returns.shape}")
    if p.phase_labels is not None and p.grayscale_map is not None:
        raise ValueError("phase_labels 与 grayscale_map 互斥（二选一）")

    return _execute_pipeline(returns, p)


def _execute_pipeline(returns: pd.DataFrame, p: StrategyCorrelationParams) -> StrategyCorrelationReport:
    """管线执行主体（拆自 run_strategy_correlation_pipeline，降循环复杂度）。"""
    # ① 数据预处理 pipeline（对数收益率统一 + ADF + 异常值标注 + 交易日交集对齐）
    prep = preprocess_strategy_returns(_returns_to_pseudo_nav(returns))
    panel = prep.aligned_log_returns

    # ② 第 1 部分：全样本双版本相关矩阵
    mats = compute_strategy_correlation(panel)
    part1 = FullSampleSection(mats["pearson"], mats["spearman"], len(panel), tuple(panel.columns))

    # ③ 第 2 部分：BM-SEL-23-B 情绪周期分层（可选）
    label_result: PhaseLabelResult | None = None
    if p.grayscale_map is not None:
        label_result = labels_from_grayscale(p.grayscale_map, confidence_threshold=p.confidence_threshold)
    elif p.phase_labels is not None:
        label_result = build_phase_labels(
            p.phase_labels, p.phase_confidences, confidence_threshold=p.confidence_threshold
        )
    part2 = _build_stratified(panel, label_result, p.min_phase_samples) if label_result is not None else None

    # ④ 第 3 部分：block-bootstrap CI + Fisher z 互验（样本不足降级 None）
    part3: BootstrapCIResult | None = None
    if p.run_bootstrap and len(panel) >= BOOTSTRAP_MIN_OBS:
        part3 = bootstrap_correlation_ci(
            panel, n_bootstrap=p.n_bootstrap, block_size=p.block_size, threshold=p.threshold, seed=p.seed
        )

    # ⑤ 第 4 部分：组合层 Neff（Ledoit-Wolf 收缩前置）
    part4 = effective_bets(panel)

    # ⑥ 第 5 部分：战略级结论
    part5 = _build_conclusion(mats["spearman"], part2, part4, p.threshold, p.neff_min)

    # ⑦ 第 7 部分：正交性覆盖度（可选留口）
    part7 = _build_orthogonality(p.dimension_map) if p.dimension_map is not None else None

    # ⑧ §5.4 漂移监控附录（样本不足降级 None）
    drift: dict[tuple[str, str], PairDriftReport] | None = None
    if p.run_drift and len(panel) >= p.drift_window + 2:
        drift = _build_drift(panel, mats["spearman"], p.drift_window, p.drift_recent_window)

    meta = {
        "n_strategies": len(panel.columns),
        "n_obs": len(panel),
        "date_start": str(panel.index[0]),
        "date_end": str(panel.index[-1]),
        "stationarity_warnings": list(prep.stationarity_warnings),
        "outlier_counts": {name: int(mask.sum()) for name, mask in prep.outliers.items()},
    }
    return StrategyCorrelationReport(part1, part2, part3, part4, part5, p.overfit_audits, part7, drift, prep, meta)


def _matrix_md(df: pd.DataFrame) -> str:
    """相关矩阵 → markdown 表。"""
    cols = [str(c) for c in df.columns]
    lines = ["| | " + " | ".join(cols) + " |", "|" + "---|" * (len(cols) + 1)]
    for idx, row in df.iterrows():
        lines.append("| " + str(idx) + " | " + " | ".join(f"{float(v):.3f}" for v in row) + " |")
    return "\n".join(lines)


def _render_header(report: StrategyCorrelationReport) -> list[str]:
    """渲染报告头部（标题 + 元信息）。"""
    p1 = report.part1_full_sample
    return [
        "# G07 策略间相关性验证报告（23 号文 §3.1⑤ 七部分模板）",
        "",
        f"- 策略数: {report.meta.get('n_strategies', len(p1.strategies))} | "
        f"样本: {report.meta.get('date_start', '?')} ~ {report.meta.get('date_end', '?')} "
        f"(T={p1.n_obs})",
        f"- 预处理: ADF 非平稳警告={report.meta.get('stationarity_warnings', [])}；"
        f"异常值标注(不剔除)={report.meta.get('outlier_counts', {})}",
        "",
        "## 1. 全样本相关矩阵（Pearson + Spearman 双版本）",
        "",
        "**Pearson**（门禁 MOD-PA-004 消费口径）：",
        _matrix_md(p1.pearson),
        "",
        "**Spearman**（抗打板极端收益率；与 Pearson 差异大时以本版为准）：",
        _matrix_md(p1.spearman),
        "",
        "## 2. 情绪周期分层矩阵（BM-SEL-23-B 4+1）",
    ]


def _render_part2_stratified(report: StrategyCorrelationReport) -> list[str]:
    """渲染第 2 部分：情绪周期分层矩阵。"""
    out: list[str] = []
    if report.part2_stratified is None:
        out.append("未提供情绪分层标签——本部分未评估（条件①不参与判定）。")
    else:
        p2 = report.part2_stratified
        out.append(
            f"置信度阈值={p2.confidence_threshold}，兜底天数={p2.fallback_count}，阶段可信最小样本={p2.min_samples}。"
        )
        for sec in p2.phases:
            out.append(f"### 阶段：{sec.phase}（n={sec.n_obs}）")
            if not sec.sufficient or sec.spearman is None:
                out.append("样本不足（<最小样本量）——本阶段相关性不可信，仅标注。")
            else:
                out.append("Spearman：")
                out.append(_matrix_md(sec.spearman))
    return out


def _render_part3_bootstrap(report: StrategyCorrelationReport) -> list[str]:
    """渲染第 3 部分：block-bootstrap 置信区间。"""
    out: list[str] = ["", "## 3. block-bootstrap 置信区间 + Fisher z 互验"]
    p3 = report.part3_bootstrap_ci
    if p3 is None:
        out.append("未运行（关闭或样本不足 MIN_OBS）。")
    else:
        out.append(
            f"multivariate stationary bootstrap {p3.n_bootstrap}×，PPW 自动块长={p3.block_size}，"
            f"CI={p3.confidence:.0%}，战略级阈值={p3.threshold}；参数法(Fisher z)与非参数 CI 互验，"
            "不一致时以 bootstrap 为准（不假设正态）。"
        )
        out.append("| 策略对 | Pearson 点估计 | Spearman 点估计 | Spearman CI | P(ρ>阈值) | Fisher CI |")
        out.append("|---|---|---|---|---|---|")
        for pair, ci in p3.spearman.items():
            pp = p3.pearson[pair]
            out.append(
                f"| {pair[0]}×{pair[1]} | {pp.point:.3f} | {ci.point:.3f} | "
                f"[{ci.ci_lower:.3f}, {ci.ci_upper:.3f}] | {ci.prob_above_threshold:.3f} | "
                f"[{ci.fisher_ci_lower:.3f}, {ci.fisher_ci_upper:.3f}] |"
            )
    return out


def _render_part4_neff(report: StrategyCorrelationReport) -> list[str]:
    """渲染第 4 部分：组合层有效下注数 Neff。"""
    p4 = report.part4_neff
    return [
        "",
        "## 4. 组合层有效下注数 Neff（Ledoit-Wolf 收缩前置）",
        f"- Neff=(Σλ)²/Σλ² = **{p4.neff:.3f}** / {p4.n_assets} 策略（等相关近似 {p4.neff_equicorr:.3f} 仅辅助）",
        f"- LW 收缩强度 α={p4.alpha:.4f}（α 大=噪声大/相关结构弱，Neff 偏乐观需共读）；"
        f"特征值={[round(float(v), 4) for v in p4.eigenvalues]}",
    ]


def _render_part5_conclusion(report: StrategyCorrelationReport) -> list[str]:
    """渲染第 5 部分：战略级结论。"""
    p5 = report.part5_conclusion
    out = [
        "",
        "## 5. 结论（是否“情绪 beta 穿多件衣服”）",
        f"- 判定: **{p5.verdict}**（三条件任一触发即 REVIEW_REQUIRED）",
        f"  - ① 单阶段 ρ>{p5.threshold} 对数最大值: "
        f"{p5.max_pairs_per_phase if p5.max_pairs_per_phase is not None else '未评估(无分层)'}",
        f"  - ② Neff={p5.neff:.3f}（下限 {p5.neff_min}）",
        f"  - ③ 两两最大 Spearman ρ={p5.max_pairwise_corr:.3f}",
        f"- 触发条件: {list(p5.triggers) if p5.triggers else '无'}",
    ]
    if p5.alpha_caveat:
        out.append(f"- ⚠️ LW α={p5.lw_alpha:.3f} 偏大：收缩后 Neff 偏乐观，分散结论需警惕（memo v1.4.1）")
    if p5.verdict == "REVIEW_REQUIRED":
        out.append("- 触发后审视清单（memo §3.1③）：信号源是否同源/持仓周期重叠/选股池交集率/是否合并为单 sleeve")
    return out


def _render_part6_overfitting(report: StrategyCorrelationReport) -> list[str]:
    """渲染第 6 部分：过拟合检测矩阵。"""
    out = ["", "## 6. 过拟合检测矩阵（DSR/PBO/PDR/PSI/DFR + verdict）"]
    if report.part6_overfitting is None:
        out.append("留口——需全量参数搜索 history（T×N returns matrix），见 memo §7 待定问题。")
    else:
        out.append("| 策略 | verdict | 指标 |")
        out.append("|---|---|---|")
        for name, res in report.part6_overfitting.items():
            metrics = ", ".join(f"{k}={v:.3f}" for k, v in sorted(res.metrics.items()))
            out.append(f"| {name} | {res.verdict.value} | {metrics} |")
    return out


def _render_part7_orthogonality(report: StrategyCorrelationReport) -> list[str]:
    """渲染第 7 部分：策略组合正交性验证。"""
    out = ["", "## 7. 策略组合正交性验证（趋势方向/执行时机/风险大小）"]
    p7 = report.part7_orthogonality
    if p7 is None:
        out.append("留口——需策略→正交维度映射输入；量化互验以第 4 部分 Neff 为准。")
    else:
        out.append(f"- 维度映射: {p7.dimension_map}")
        out.append(f"- 已覆盖: {list(p7.covered)}；未覆盖: {list(p7.uncovered)}")
        out.append(f"- 组合退化: {'是' if p7.degenerate else '否'}（覆盖维度<2 即退化）")
        out.append(f"- 说明: {p7.note}")
    return out


def _render_drift_appendix(report: StrategyCorrelationReport) -> list[str]:
    """渲染附录：相关性漂移监控。"""
    out = ["", "## 附：相关性漂移监控（§5.4 CUSUM-PSI，上线后持续）"]
    if report.drift_monitoring is None:
        out.append("未运行（关闭或样本不足窗口）。")
    else:
        out.append("| 策略对 | CUSUM 告警 | 首个告警位 | PSI | PSI 分级 | 综合 |")
        out.append("|---|---|---|---|---|---|")
        for pair, rep in report.drift_monitoring.items():
            out.append(
                f"| {pair[0]}×{pair[1]} | {'是' if rep.cusum.alarm else '否'} | "
                f"{rep.cusum.first_alarm_pos if rep.cusum.first_alarm_pos is not None else '-'} | "
                f"{f'{rep.psi:.3f}' if rep.psi is not None else '-'} | {rep.psi_level.value} | "
                f"{'DRIFT' if rep.drift_detected else 'stable'} |"
            )
    return out


def render_markdown(report: StrategyCorrelationReport) -> str:
    """按 23 号 memo §3.1⑤ 七部分模板渲染报告（markdown）。"""
    out: list[str] = []
    out.extend(_render_header(report))
    out.extend(_render_part2_stratified(report))
    out.extend(_render_part3_bootstrap(report))
    out.extend(_render_part4_neff(report))
    out.extend(_render_part5_conclusion(report))
    out.extend(_render_part6_overfitting(report))
    out.extend(_render_part7_orthogonality(report))
    out.extend(_render_drift_appendix(report))
    return "\n".join(out) + "\n"
