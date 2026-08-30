# [BLUEPRINT] none | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/11_regime_backtest_validation_plan.md §4.1 A4 / §0.6.6 路径3
# [MODULE] zephyr.regime.validation.a4_feature_importance
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; zephyr.shared.foundation.errors
# [CONSUMERS] 人工审查; 11_regime_backtest_validation_plan A4 特征重要性(BM-BT-05-B)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] Permutation主轨(SHAP审计轨不做,memo裁定); 排列严格限制在各滚动窗口内(禁全样本洗牌,防look-ahead); importance=基线score−扰动score(越大越重要); 只读X不改调用方数据; frozen 不可变
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] A4ImportanceError(ZA-REGIME-0032)
# [TESTS] tests/regime/validation/test_a4_feature_importance.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: score_fn(X_window)→float(越大越好, 如 HMM log-likelihood) + X(T,F) 特征矩阵 + windows 窗口边界
# I2: n_repeats=5 / stability_threshold=0.70(§4.1 A4: top-2 在≥70%窗口保持) / negligible_share=0.01
# F1: 窗口内列洗牌(rng.permutation 仅作用于窗口切片) × n_repeats → 逐特征重要性
# A1: permutation_importance_windows(逐窗口逐特征扰动→均值重要性/占比/top-2 稳定性聚合)
# O1: A4PermutationReport(mean_importance/share/top2_stability/negligible_features/passed)
# [/ALGO_FLOW]
"""
D_REGIME — A4 特征重要性 Permutation 主轨（11 号 memo §4.1 A4）。

按 §4.1 A4 裁定：Permutation Importance 为主轨（SHAP 审计轨不做）——
在各 walk-forward 季度窗口内对特征列做窗口内排列（严格防 look-ahead，
禁全样本洗牌），以 score_fn（如 HMM log-likelihood，越大越好）的下降量
度量重要性。

判定（§4.1 A4）：
  - top-2 特征在 ≥70% 窗口内保持 top-2（排名稳定，真实驱动 vs 窗口噪声）；
  - 无任何特征重要性占比长期 <1%（存在则入 D 类降维候选，判不通过）。

依据: 11_regime_backtest_validation_plan §4.1 A4 / §0.6.6 升级路径 3
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: score_fn 参数
#   fields: 参数 score_fn，类型注解 Callable[[np.ndarray], float]
#   code: a4_feature_importance.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: X 参数
#   fields: 参数 X，类型注解 np.ndarray
#   code: a4_feature_importance.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: windows 参数
#   fields: 参数 windows，类型注解 Sequence[tuple[int, int]] | None
#   code: a4_feature_importance.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: n_repeats 参数
#   fields: 参数 n_repeats，类型注解 int
#   code: a4_feature_importance.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① permutation_importance_windows
#   name_en: permutation_importance_windows
#   intro: A4 主入口：窗口内 permutation 重要性 + top-2 排名稳定性。
#   desc: A4 主入口：窗口内 permutation 重要性 + top-2 排名稳定性。 Args: score_fn: 评分函数，输入 (Tw, F) 窗口矩阵，返回 float（越…；源码 L118-L209
#   inputs: score_fn X windows n_repeats seed feature_names stability_threshold n…
#   outputs: A4PermutationReport
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: A4PermutationReport
#   name_en: A4PermutationReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 人工审查; 11_regime_backtest_validation_plan A4 特征重要性(BM-BT-05-B)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np

try:  # 治理基类缺失时降级为 Exception，保证模块可独立 import
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover  # noqa: BLE001
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)


class A4ImportanceError(ZephyrBaseError):
    """ZA-REGIME-0032: A4 特征重要性分析错误（输入非法）。"""

    error_code = "ZA-REGIME-0032"


@dataclass(frozen=True)
class A4PermutationReport:
    """A4 permutation 重要性报告——不可变。"""

    feature_names: tuple[str, ...]
    n_windows: int
    mean_importance: tuple[float, ...]  # 逐特征跨窗口均值（score 下降量）
    importance_share: tuple[float, ...]  # 正部归一化占比
    top2_features: tuple[str, ...]  # 跨窗口均值 top-2
    top2_stability: float  # top-2 特征在窗口内保持 top-2 的平均比例
    negligible_features: tuple[str, ...]  # 占比 < negligible_share 的特征（降维候选）
    passed: bool  # 稳定且无可忽略特征
    summary: str


def permutation_importance_windows(
    score_fn: Callable[[np.ndarray], float],
    X: np.ndarray,
    windows: Sequence[tuple[int, int]] | None = None,
    n_repeats: int = 5,
    seed: int = 42,
    feature_names: Sequence[str] | None = None,
    stability_threshold: float = 0.70,
    negligible_share: float = 0.01,
) -> A4PermutationReport:
    """A4 主入口：窗口内 permutation 重要性 + top-2 排名稳定性。

    Args:
        score_fn: 评分函数，输入 (Tw, F) 窗口矩阵，返回 float（越大越好）。
        X: (T, F) 特征矩阵（T≥2, F≥2），只读。
        windows: [(start, end)) 窗口边界（左闭右开）；None=单窗口全样本。
        n_repeats: 每特征每窗口排列次数（≥1）。
        seed: 随机种子（复现用）。
        feature_names: 特征名（None → f0..f{F-1}）。
        stability_threshold: top-2 稳定门槛（§4.1 A4=0.70）。
        negligible_share: 可忽略特征占比门槛（§4.1 A4=0.01）。

    Raises:
        A4ImportanceError: 维度非法 / 窗口越界或过短 / 参数非正。
    """
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or X.shape[0] < 2 or X.shape[1] < 2:
        raise A4ImportanceError(f"X 须为 (T≥2, F≥2) 二维矩阵: {X.shape}")
    if not np.isfinite(X).all():
        raise A4ImportanceError("X 含 NaN/Inf")
    if n_repeats < 1:
        raise A4ImportanceError(f"n_repeats 需 ≥1: {n_repeats}")
    if not 0.0 < stability_threshold <= 1.0 or not 0.0 < negligible_share < 1.0:
        raise A4ImportanceError(f"门槛非法: stability={stability_threshold} negligible={negligible_share}")
    T, F = X.shape
    names = tuple(feature_names) if feature_names else tuple(f"f{j}" for j in range(F))
    if len(names) != F:
        raise A4ImportanceError(f"feature_names 长度 {len(names)} != F {F}")
    bounds = list(windows) if windows else [(0, T)]
    for s, e in bounds:
        if not (0 <= s < e <= T) or e - s < 2:
            raise A4ImportanceError(f"窗口非法或过短: ({s},{e})，T={T}")

    rng = np.random.default_rng(seed)
    per_window: list[np.ndarray] = []  # 每窗口 (F,) 重要性
    for s, e in bounds:
        Xw = X[s:e]
        baseline = float(score_fn(Xw))
        imp = np.empty(F, dtype=float)
        for j in range(F):
            drops = np.empty(n_repeats, dtype=float)
            for r in range(n_repeats):
                Xp = Xw.copy()
                Xp[:, j] = Xp[rng.permutation(e - s), j]  # 窗口内洗牌
                drops[r] = baseline - float(score_fn(Xp))
            imp[j] = drops.mean()
        per_window.append(imp)

    mat = np.vstack(per_window)  # (W, F)
    mean_imp = mat.mean(axis=0)
    pos = np.clip(mean_imp, 0.0, None)
    share = pos / pos.sum() if pos.sum() > 0 else np.zeros(F)

    order = np.argsort(-mean_imp)
    top2_idx = tuple(sorted(order[:2].tolist()))
    # 每个整体 top-2 特征：在多少比例窗口内也居 top-2
    hits = []
    for j in top2_idx:
        w_top2 = [set(np.argsort(-mat[w])[:2].tolist()) for w in range(mat.shape[0])]
        hits.append(float(np.mean([j in s2 for s2 in w_top2])))
    stability = float(np.mean(hits))

    negligible = tuple(names[j] for j in range(F) if share[j] < negligible_share)
    passed = stability >= stability_threshold and not negligible
    summary = (
        f"A4 特征重要性: {mat.shape[0]} 窗口 × {F} 特征, "
        f"top2=({names[top2_idx[0]]},{names[top2_idx[1]]}) 稳定性={stability:.2%} "
        f"门槛≥{stability_threshold:.0%}, 可忽略特征={list(negligible) or '无'} → "
        f"{'通过' if passed else '不通过'}"
    )
    _logger.info("A4 完成: %s", summary)
    return A4PermutationReport(
        feature_names=names,
        n_windows=mat.shape[0],
        mean_importance=tuple(float(v) for v in mean_imp),
        importance_share=tuple(float(v) for v in share),
        top2_features=(names[top2_idx[0]], names[top2_idx[1]]),
        top2_stability=stability,
        negligible_features=negligible,
        passed=passed,
        summary=summary,
    )


__all__ = [
    "A4ImportanceError",
    "A4PermutationReport",
    "permutation_importance_windows",
]
