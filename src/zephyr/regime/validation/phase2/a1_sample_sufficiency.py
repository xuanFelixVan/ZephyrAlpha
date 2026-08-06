# [BLUEPRINT] MOD-REGIME-VAL-002-A1 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/discussion_003_phase2_model_quality_validation.md §2.1
# [MODULE] zephyr.regime.validation.phase2.a1_sample_sufficiency
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; zephyr.regime.core.regime_detector
# [CONSUMERS] scripts.tests.run_phase2_validation; phase2_runner; BM-BT-05
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] A1只读 detector/builder, 不改其状态(OCP); Viterbi解码用同一拟合模型; dropna去warmup期NaN
# [MODIFY-GUARD] discussion_003_phase2_model_quality_validation.md §2.1
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] A1ValidationError(ZA-REGIME-0020)
# [TESTS] tests/regime/phase2/test_a1_sample_sufficiency.py
# [TTL] permanent
# [ARCH-REF] #discussion_003 §2.1 #discussion_002 §4.1 A1
"""A1 样本充足性验证器（discussion_003 §2.1，Phase 2 第一批 MVP）.

验证问题: HMM 9 态的稀有态够 HMM 学吗？

算法:
  1. 全量历史特征（dropna 去 warmup 期 NaN）+ RobustScaler 标准化（与 walk-forward 一致）
  2. fit 一个全新 RegimeDetector（9 态 GaussianHMM）
  3. 用 _hmm_model.predict(X)（hmmlearn 原生 Viterbi）解码全历史状态序列
  4. 统计 r1-r9 各态出现天数
  5. 对照判定门槛

判定门槛（discussion_002 §4.1 A1）:
  ≥100 天  → 充足（独立建模）
  50-100   → 中等（收缩向均值，§2.7 稀有态处理）
  <50      → 不足（合并高波动三态 → 6 态）

Overall:
  全部态 ≥100           → PASS
  存在态 50-100 但无 <50 → REVIEW
  存在态 <50            → FAIL（合并态数后重跑）

依据: discussion_003 §2.1
Version: 0.1.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np

try:
    from sklearn.preprocessing import RobustScaler
except ImportError:  # pragma: no cover
    RobustScaler = None  # type: ignore[assignment,misc]

try:
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)

# r1-r9 HMM 9 态（与 regime_detector.HMM_STATES 对齐）
HMM_STATES_9: list[str] = [f"r{i}" for i in range(1, 10)]

# 判定门槛（discussion_002 §4.1 A1）
SUFFICIENT_DAYS = 100  # ≥100 → 充足
INSUFFICIENT_DAYS = 50  # <50 → 不足（50-100 为中等区间）


class A1ValidationError(ZephyrBaseError):
    """ZA-REGIME-0020: A1 验证器错误（HMM 未拟合/特征缺失/解码异常）。"""

    error_code = "ZA-REGIME-0020"


class A1StateVerdict(str, Enum):
    """单态判定结果。"""

    SUFFICIENT = "sufficient"  # ≥100 天，独立建模
    MODERATE = "moderate"  # 50-100 天，收缩向均值
    INSUFFICIENT = "insufficient"  # <50 天，合并高波动三态 → 6 态


class A1Overall(str, Enum):
    """整体判定。"""

    PASS = "PASS"  # 全部态 ≥100
    REVIEW = "REVIEW"  # 存在 50-100 但无 <50
    FAIL = "FAIL"  # 存在 <50，需合并态数重跑


@dataclass(frozen=True)
class A1StateStat:
    """单态统计。"""

    state: str  # r1-r9
    count: int  # 出现天数
    frequency: float  # 占比
    verdict: A1StateVerdict
    action: str  # 建议动作


@dataclass(frozen=True)
class A1Report:
    """A1 验证报告。"""

    state_stats: list[A1StateStat]  # r1-r9 各态统计（按 state 排序）
    total_samples: int  # 总样本数（dropna 后）
    overall: A1Overall
    summary: str  # 人类可读总结
    fit_log_likelihood: float  # HMM 拟合 log-likelihood（诊断用）
    degraded: bool  # hmmlearn 不可用 / 拟合失败 → 降级

    @property
    def min_state_count(self) -> int:
        """最少样本态的天数。"""
        return min((s.count for s in self.state_stats), default=0)

    @property
    def insufficient_states(self) -> list[str]:
        """样本不足（<50 天）的态列表。"""
        return [s.state for s in self.state_stats if s.verdict is A1StateVerdict.INSUFFICIENT]

    def to_dict(self) -> dict[str, Any]:
        """转 dict（供 JSON 序列化）。"""
        return {
            "state_stats": [
                {
                    "state": s.state,
                    "count": s.count,
                    "frequency": round(s.frequency, 4),
                    "verdict": s.verdict.value,
                    "action": s.action,
                }
                for s in self.state_stats
            ],
            "total_samples": self.total_samples,
            "overall": self.overall.value,
            "summary": self.summary,
            "fit_log_likelihood": round(self.fit_log_likelihood, 4),
            "degraded": self.degraded,
        }


class A1SampleSufficiency:
    """A1 样本充足性验证器。

    Usage（real 模式，复用 RegimeFeatureBuilder）:
        builder = RegimeFeatureBuilder(backtest_start="2015-01-01", backtest_end="2026-06-30",
                                      data_load_start="2010-01-01")
        features = builder.build_features()
        # 取全历史特征矩阵（含 warmup 期，A1 自己 dropna）
        X_full = features[FEATURE_NAMES].to_numpy(dtype=float)
        a1 = A1SampleSufficiency()
        report = a1.validate(X_full, standardize=True)

    Usage（单测，预 fit 的 detector）:
        a1 = A1SampleSufficiency()
        report = a1.validate_with_fit_detector(detector, X_full)
    """

    def __init__(self, hmm_params: dict[str, Any] | None = None) -> None:
        """初始化。

        Args:
            hmm_params: HMM 参数（默认 9 态 full 协方差，与 regime_detector 默认一致）。
        """
        self.hmm_params = hmm_params or {
            "n_states": 9,
            "covariance_type": "full",
            "n_iter": 100,
            "n_init": 3,
            "random_state": 42,
        }

    def validate(
        self,
        X: np.ndarray,
        standardize: bool = True,
    ) -> A1Report:
        """全量历史 fit + Viterbi 解码 + 统计。

        Args:
            X: 全历史特征矩阵 (T, F)，可含 NaN（warmup 期），内部 dropna + 钳 inf。
            standardize: 是否 RobustScaler 标准化（与 walk-forward 一致，默认 True）。

        Returns:
            A1Report。
        """
        # 延迟 import 避免循环依赖
        from zephyr.regime.core.regime_detector import RegimeDetector

        X_clean = self._clean_matrix(X)
        if len(X_clean) < 100:
            raise A1ValidationError(
                f"特征矩阵样本不足: dropna 后仅 {len(X_clean)} 行（需 ≥100）"
            )

        scaler = None
        X_fit = X_clean
        if standardize and RobustScaler is not None:
            scaler = RobustScaler().fit(X_fit)
            X_fit = scaler.transform(X_fit)
            _logger.info("A1: RobustScaler 标准化（与 walk-forward 一致）")

        detector = RegimeDetector(shrinkage_enabled=False, hmm_params=self.hmm_params)
        return self._validate_with_detector(detector, X_fit, scaler, original_count=len(X))

    def validate_with_fit_detector(
        self,
        detector: Any,
        X: np.ndarray,
        standardize: bool = False,
    ) -> A1Report:
        """复用已 fit 的 detector（单测/复用 walk-forward 末态模型）。

        Args:
            detector: 已 fit 的 RegimeDetector 实例（_hmm_model 非 None）。
            X: 特征矩阵 (T, F)，可含 NaN，内部 dropna。
            standardize: 是否对 X 标准化（若 detector fit 时用了 scaler，此处也需 True 并
                传入同一 scaler——单测场景建议直接传已标准化 X 并 standardize=False）。

        Returns:
            A1Report。
        """
        X_clean = self._clean_matrix(X)
        X_fit = X_clean
        if standardize and RobustScaler is not None:
            scaler = RobustScaler().fit(X_fit)
            X_fit = scaler.transform(X_fit)
        else:
            scaler = None
        return self._validate_with_detector(detector, X_fit, scaler, original_count=len(X))

    # ── 内部 ──────────────────────────────────────────────────────────

    def _clean_matrix(self, X: np.ndarray) -> np.ndarray:
        """清理特征矩阵：转 2D float + dropna 行 + 钳 inf。"""
        if not isinstance(X, np.ndarray):
            X = np.asarray(X, dtype=float)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        if X.ndim != 2:
            raise A1ValidationError(f"X 维度应为 2D (T, F)，实际 {X.ndim}D")
        # dropna 行（warmup 期 NaN）
        valid_mask = np.isfinite(X).all(axis=1)
        X_clean = X[valid_mask]
        if len(X_clean) == 0:
            raise A1ValidationError("X 全部为 NaN/Inf，无可用样本")
        # 钳剩余 inf（防极端值）
        X_clean = np.nan_to_num(X_clean, nan=0.0, posinf=0.0, neginf=0.0)
        return X_clean

    def _validate_with_detector(
        self,
        detector: Any,
        X: np.ndarray,
        scaler: Any,
        original_count: int,
    ) -> A1Report:
        """核心：fit（如未 fit）+ Viterbi 解码 + 统计。"""
        from zephyr.regime.core.regime_detector import RegimeDetector

        # 若 detector 未 fit，则 fit（validate() 路径新建的 detector）
        needs_fit = getattr(detector, "_hmm_model", None) is None
        log_likelihood = 0.0
        degraded = False
        if needs_fit:
            try:
                detector.fit({"X": X, "lengths": None})
            except Exception as exc:
                _logger.warning("A1: HMM 拟合失败，降级为均匀分布判定: %s", exc)
                degraded = True
        else:
            # 复用已 fit 模型，需对 X 标准化（若外部传 scaler 已处理，此处跳过）
            pass

        if getattr(detector, "_hmm_model", None) is None or degraded:
            # 降级：无法 Viterbi 解码，按均匀分布估计（每态 T/9 天）
            return self._build_degraded_report(len(X))

        hmm_model = detector._hmm_model  # noqa: SLF001 — 访问私有模型做 Viterbi（OCP: 只读不改）
        try:
            state_seq = hmm_model.predict(X)  # Viterbi 解码，返回 (T,) 标签 0..n-1
            log_likelihood = float(hmm_model.score(X))
        except Exception as exc:
            _logger.warning("A1: Viterbi 解码失败: %s", exc)
            return self._build_degraded_report(len(X))

        n_states = int(self.hmm_params.get("n_states", 9))
        return self._build_report(state_seq, n_states, log_likelihood, degraded=False)

    def _build_report(
        self,
        state_seq: np.ndarray,
        n_states: int,
        log_likelihood: float,
        degraded: bool,
    ) -> A1Report:
        """构建正常报告。"""
        total = len(state_seq)
        state_stats: list[A1StateStat] = []
        for i in range(n_states):
            state_label = HMM_STATES_9[i] if i < len(HMM_STATES_9) else f"r{i + 1}"
            count = int(np.sum(state_seq == i))
            freq = count / total if total > 0 else 0.0
            verdict, action = self._judge_state(count)
            state_stats.append(
                A1StateStat(
                    state=state_label,
                    count=count,
                    frequency=freq,
                    verdict=verdict,
                    action=action,
                )
            )

        # 整体判定
        has_insufficient = any(
            s.verdict is A1StateVerdict.INSUFFICIENT for s in state_stats
        )
        has_moderate = any(s.verdict is A1StateVerdict.MODERATE for s in state_stats)
        if has_insufficient:
            overall = A1Overall.FAIL
        elif has_moderate:
            overall = A1Overall.REVIEW
        else:
            overall = A1Overall.PASS

        min_count = min((s.count for s in state_stats), default=0)
        summary = (
            f"A1 样本充足性: {total} 样本，{n_states} 态，"
            f"最少态样本={min_count} 天 → {overall.value}"
        )
        _logger.info("A1 完成: %s", summary)
        return A1Report(
            state_stats=state_stats,
            total_samples=total,
            overall=overall,
            summary=summary,
            fit_log_likelihood=log_likelihood,
            degraded=degraded,
        )

    def _build_degraded_report(self, total: int) -> A1Report:
        """降级报告（hmmlearn 不可用 / 拟合失败）。"""
        per_state = total // 9
        state_stats = [
            A1StateStat(
                state=HMM_STATES_9[i],
                count=per_state,
                frequency=per_state / total if total > 0 else 0.0,
                verdict=A1StateVerdict.SUFFICIENT if per_state >= SUFFICIENT_DAYS
                else (A1StateVerdict.MODERATE if per_state >= INSUFFICIENT_DAYS
                      else A1StateVerdict.INSUFFICIENT),
                action="[降级] hmmlearn 不可用，按均匀分布估计",
            )
            for i in range(9)
        ]
        return A1Report(
            state_stats=state_stats,
            total_samples=total,
            overall=A1Overall.REVIEW,
            summary=f"A1 降级: hmmlearn 不可用，按 1/9 均匀分布估计（每态 ~{per_state} 天）",
            fit_log_likelihood=0.0,
            degraded=True,
        )

    @staticmethod
    def _judge_state(count: int) -> tuple[A1StateVerdict, str]:
        """单态判定。"""
        if count >= SUFFICIENT_DAYS:
            return A1StateVerdict.SUFFICIENT, "独立建模"
        if count >= INSUFFICIENT_DAYS:
            return A1StateVerdict.MODERATE, "收缩向均值（§2.7 稀有态处理）"
        return A1StateVerdict.INSUFFICIENT, "合并高波动三态 → 6 态"
