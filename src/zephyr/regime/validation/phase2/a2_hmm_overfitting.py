# [BLUEPRINT] MOD-REGIME_VAL-002 | 12_regime_phase2_validation §2.3
# [MODULE] zephyr.regime.validation.phase2.a2_hmm_overfitting
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; zephyr.regime.core.regime_detector
# [CONSUMERS] zephyr.regime.validation.phase2.phase2_runner; scripts.tests.run_phase2_validation
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] IS/OOS 分割无重叠; 标签对齐按态均值排序(permutation invariance); OOS/IS≥0.7→PASS; 降级时返回明确 degraded 标记
# [MODIFY-GUARD] 12_regime_phase2_validation.md §2.3
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] A2ValidationError(ZA-REGIME-0021)
# [TESTS] tests/regime/phase2/test_a2_hmm_overfitting.py
# [A_module] module_id=MOD-REGIME_VAL-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #12_regime_phase2_validation §2.3 #12_regime_phase2_validation §4.1 A2
"""
A2 HMM 过拟合验证器（12_regime_phase2_validation §2.3）。

方案 A：IS/OOS 交叉解码一致率。
  1. IS 数据（如 2010-2018）fit → HMM_is；OOS 数据（如 2019-2026）fit → HMM_oos
  2. HMM_is 解码 OOS → seq_is（IS 模型看 OOS 的态序列）
  3. HMM_oos 解码 OOS → seq_oos（OOS 模型看自己的态序列，作"参考真值"）
  4. 标签对齐（HMM permutation invariance）——Hungarian 全特征最优匹配建立 IS→OOS 映射
  5. 对齐后逐日一致率 = OOS 准确率；同理 IS 准确率
  6. 比值 OOS/IS ≥ 0.7 → PASS（过拟合可控）

方案 B（补充）：IS/OOS 概率分布 KL 散度——越小越不过拟合。

判定（12_regime_phase2_validation §2.3）：
  OOS/IS ≥ 0.7 → PASS；0.5 ≤ 比值 < 0.7 → REVIEW；< 0.5 → FAIL

依据: 12_regime_phase2_validation §2.3 / 12_regime_phase2_validation §4.1 A2
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: hmm_params 参数
#   fields: 参数 hmm_params（无注解）
#   code: a2_hmm_overfitting.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① A2Report
#   name_en: A2Report
#   intro: A2 过拟合验证报告。
#   desc: A2 过拟合验证报告。；公共方法（定义序）: to_dict；源码 L114-L140
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② A2HmmOverfitting
#   name_en: A2HmmOverfitting
#   intro: A2 HMM 过拟合验证器（IS/OOS 交叉解码一致率）。
#   desc: A2 HMM 过拟合验证器（IS/OOS 交叉解码一致率）。 Usage（real 模式）:: builder = RegimeFeatureBuilder(...) featu…；公共方法（定义序）: validat…
#   inputs: hmm_params
#   outputs: 返回值
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: A2Report, A2HmmOverfitting
#   downstream: zephyr.regime.validation.phase2.phase2_runner; scripts.tests.run_phase2_validat…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
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
except Exception:  # pragma: no cover  # noqa: BLE001
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)

# 判定门槛（12_regime_phase2_validation §2.3）
PASS_RATIO = 0.7  # OOS/IS ≥ 0.7 → PASS
REVIEW_RATIO = 0.5  # ≥ 0.5 → REVIEW


class A2ValidationError(ZephyrBaseError):
    """ZA-REGIME-0021: A2 验证器错误（样本不足/HMM 拟合失败/分割异常）。"""

    error_code = "ZA-REGIME-0021"


class A2Verdict(str, Enum):
    """过拟合判定结果。"""

    PASS = "PASS"  # OOS/IS ≥ 0.7，过拟合可控
    REVIEW = "REVIEW"  # 0.5 ≤ 比值 < 0.7，需结合 A1 判断
    FAIL = "FAIL"  # < 0.5，明显过拟合


@dataclass(frozen=True)
class A2Report:
    """A2 过拟合验证报告。"""

    is_accuracy: float  # IS 模型解码 IS vs OOS 模型解码 IS 的一致率
    oos_accuracy: float  # IS 模型解码 OOS vs OOS 模型解码 OOS 的一致率
    ratio: float  # oos_accuracy / is_accuracy
    kl_divergence: float  # IS/OOS 概率分布 KL 散度（越小越不过拟合）
    label_alignment: str  # 标签对齐方式描述
    is_samples: int  # IS 样本数
    oos_samples: int  # OOS 样本数
    verdict: A2Verdict
    summary: str
    degraded: bool  # hmmlearn 不可用 / 拟合失败 → 降级

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_accuracy": round(self.is_accuracy, 4),
            "oos_accuracy": round(self.oos_accuracy, 4),
            "ratio": round(self.ratio, 4),
            "kl_divergence": round(self.kl_divergence, 4),
            "label_alignment": self.label_alignment,
            "is_samples": self.is_samples,
            "oos_samples": self.oos_samples,
            "verdict": self.verdict.value,
            "summary": self.summary,
            "degraded": self.degraded,
        }


class A2HmmOverfitting:
    """A2 HMM 过拟合验证器（IS/OOS 交叉解码一致率）。

    Usage（real 模式）::

        builder = RegimeFeatureBuilder(...)
        features = builder.build_features()
        X = features[FEATURE_NAMES].to_numpy(dtype=float)
        a2 = A2HmmOverfitting()
        # IS=2010-2018, OOS=2019-2026（按索引分割）
        is_end_idx = features.index.get_loc(pd.Timestamp("2018-12-31"))
        report = a2.validate(X, is_end_idx=is_end_idx, standardize=True)
    """

    def __init__(self, hmm_params: dict[str, Any] | None = None) -> None:
        self.hmm_params = hmm_params or {
            "n_states": 4,
            "covariance_type": "full",
            "n_iter": 100,
            "n_init": 3,
            "random_state": 42,
        }

    def validate(
        self,
        X: np.ndarray,
        is_end_idx: int,
        standardize: bool = True,
    ) -> A2Report:
        """IS/OOS 分割 + 交叉 fit + 解码一致率 + KL 散度。

        Args:
            X: 全历史特征矩阵 (T, F)，可含 NaN（warmup），内部 dropna。
            is_end_idx: IS/OOS 分割索引（IS = X[:is_end_idx], OOS = X[is_end_idx:]）。
            standardize: 是否 RobustScaler 标准化（IS/OOS 各自 fit scaler，PIT）。

        Returns:
            A2Report。
        """
        from zephyr.regime.core.regime_detector import RegimeDetector

        # IS/OOS 分割（基于原始索引，各自清洗 dropna）
        X_is = self._clean_matrix(X[:is_end_idx])
        X_oos = self._clean_matrix(X[is_end_idx:])

        if len(X_is) < 100 or len(X_oos) < 100:
            raise A2ValidationError(f"IS/OOS 样本不足: IS={len(X_is)}, OOS={len(X_oos)}（需各 ≥100）")

        # 各自标准化（PIT：IS scaler 只见 IS 数据，OOS scaler 只见 OOS 数据）
        X_is_fit, scaler_is = self._standardize(X_is, standardize)
        X_oos_fit, scaler_oos = self._standardize(X_oos, standardize)

        # fit 两个 HMM
        detector_is = RegimeDetector(shrinkage_enabled=False, hmm_params=self.hmm_params)
        detector_oos = RegimeDetector(shrinkage_enabled=False, hmm_params=self.hmm_params)
        try:
            detector_is.fit({"X": X_is_fit, "lengths": None})
            detector_oos.fit({"X": X_oos_fit, "lengths": None})
        except Exception as exc:  # noqa: BLE001
            _logger.warning("A2: HMM 拟合失败，降级: %s", exc)
            return self._degraded_report(len(X_is), len(X_oos))

        hmm_is = getattr(detector_is, "_hmm_model", None)  # noqa: SLF001
        hmm_oos = getattr(detector_oos, "_hmm_model", None)  # noqa: SLF001
        if hmm_is is None or hmm_oos is None:
            _logger.warning("A2: HMM 模型为空（hmmlearn 不可用），降级")
            return self._degraded_report(len(X_is), len(X_oos))

        # 标签对齐（permutation invariance）——Hungarian 全特征最优匹配
        mapping = self._align_labels(hmm_is, hmm_oos)
        alignment_desc = "Hungarian 全特征最优匹配（欧氏距离）"

        # 交叉解码 + 一致率
        # OOS 准确率：HMM_is 解码 OOS（用 IS scaler transform）vs HMM_oos 解码 OOS
        X_oos_for_is = scaler_is.transform(X_oos) if scaler_is else X_oos
        seq_is_on_oos = hmm_is.predict(X_oos_for_is)
        seq_oos_on_oos = hmm_oos.predict(X_oos_fit)
        oos_acc = self._accuracy(seq_is_on_oos, seq_oos_on_oos, mapping)

        # IS 准确率：HMM_oos 解码 IS（用 OOS scaler transform）vs HMM_is 解码 IS
        X_is_for_oos = scaler_oos.transform(X_is) if scaler_oos else X_is
        seq_oos_on_is = hmm_oos.predict(X_is_for_oos)
        seq_is_on_is = hmm_is.predict(X_is_fit)
        # 反向映射 OOS→IS
        inv_mapping = {v: k for k, v in mapping.items()}
        is_acc = self._accuracy(seq_oos_on_is, seq_is_on_is, inv_mapping)

        ratio = oos_acc / is_acc if is_acc > 0 else 0.0

        # KL 散度（IS 模型在 OOS 上的概率 vs OOS 模型在 OOS 上的概率）
        kl = self._kl_divergence(
            hmm_is.predict_proba(X_oos_for_is),
            hmm_oos.predict_proba(X_oos_fit),
        )

        verdict = self._judge(ratio)
        summary = (
            f"A2 过拟合: IS_acc={is_acc:.1%}, OOS_acc={oos_acc:.1%}, OOS/IS={ratio:.3f}, KL={kl:.4f} → {verdict.value}"
        )
        _logger.info("A2: %s", summary)
        return A2Report(
            is_accuracy=round(is_acc, 4),
            oos_accuracy=round(oos_acc, 4),
            ratio=round(ratio, 4),
            kl_divergence=round(kl, 4),
            label_alignment=alignment_desc,
            is_samples=len(X_is),
            oos_samples=len(X_oos),
            verdict=verdict,
            summary=summary,
            degraded=False,
        )

    # ── 内部 ──────────────────────────────────────────────────────────

    @staticmethod
    def _clean_matrix(X: np.ndarray) -> np.ndarray:
        """清理特征矩阵：2D float + dropna 行 + 钳 inf。"""
        if not isinstance(X, np.ndarray):
            X = np.asarray(X, dtype=float)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        valid = np.isfinite(X).all(axis=1)
        X_clean = X[valid]
        if len(X_clean) == 0:
            raise A2ValidationError("X 全部为 NaN/Inf，无可用样本")
        return np.nan_to_num(X_clean, nan=0.0, posinf=0.0, neginf=0.0)

    @staticmethod
    def _standardize(X: np.ndarray, standardize: bool) -> tuple[np.ndarray, Any]:
        """RobustScaler 标准化（返回标准化后 X + scaler，standardize=False 时 scaler=None）。"""
        if standardize and RobustScaler is not None:
            scaler = RobustScaler().fit(X)
            return scaler.transform(X), scaler
        return X, None

    @staticmethod
    def _align_labels(hmm_a: Any, hmm_b: Any, feature_idx: int = 0) -> dict[int, int]:  # noqa: any-abuse  # 预存Any类型，待Protocol化
        """标签对齐：Hungarian 算法全特征最优匹配（scipy 不可用时回退单特征排序）。

        HMM 有 permutation invariance（A 模型的态 0 可能对应 B 模型的态 3）。
        用**全部特征列**的态均值向量算 IS/OOS 各态间欧氏距离矩阵，Hungarian
        算法（scipy.optimize.linear_sum_assignment）求一对一最优匹配（最小化
        总距离），建立 A→B 映射。

        优于原"按单特征（vol_pct）排序"：4 态 HMM 有 6 特征，单特征排序在
        两态 vol_pct 相近但其他特征差异大时会错配，导致交叉解码一致率被低估。
        Hungarian 全特征匹配是无监督 HMM 标签对齐的标准做法。

        Args:
            hmm_a: IS 模型（source）。
            hmm_b: OOS 模型（target）。
            feature_idx: scipy 不可用回退单特征排序时所用列（默认 0=realized_vol_pct）。

        Returns:
            {a_state: b_state} 映射。
        """
        means_a = hmm_a.means_  # (n_states, n_features)
        means_b = hmm_b.means_  # (n_states, n_features)
        try:
            from scipy.optimize import linear_sum_assignment

            # 全特征欧氏距离矩阵 (n_states_a, n_states_b)
            dist = np.linalg.norm(means_a[:, None, :] - means_b[None, :, :], axis=2)
            row_ind, col_ind = linear_sum_assignment(dist)
            return {int(r): int(c) for r, c in zip(row_ind, col_ind, strict=False)}
        except ImportError:  # pragma: no cover
            _logger.warning("scipy 不可用，回退单特征排序对齐（可能低估一致率）")
            means_a_1d = means_a[:, feature_idx]
            means_b_1d = means_b[:, feature_idx]
            # rank：按均值排序后的位置（0=最小均值态）
            rank_a = np.argsort(np.argsort(means_a_1d))
            rank_b = np.argsort(np.argsort(means_b_1d))
            mapping: dict[int, int] = {}
            for a_state in range(len(rank_a)):
                b_candidates = np.where(rank_b == rank_a[a_state])[0]
                mapping[a_state] = int(b_candidates[0]) if len(b_candidates) > 0 else a_state
            return mapping

    @staticmethod
    def _accuracy(seq_a: np.ndarray, seq_b: np.ndarray, mapping: dict[int, int]) -> float:
        """seq_a 通过 mapping 对齐到 seq_b 的逐日一致率。

        Args:
            seq_a: A 模型解码的状态序列（标签 A 的编号）。
            seq_b: B 模型解码的状态序列（标签 B 的编号，参考真值）。
            mapping: {a_state: b_state} 映射。

        Returns:
            一致率 ∈ [0, 1]。
        """
        if len(seq_a) == 0 or len(seq_a) != len(seq_b):
            return 0.0
        aligned = np.array([mapping.get(int(s), -1) for s in seq_a])
        return float(np.mean(aligned == seq_b))

    @staticmethod
    def _kl_divergence(p_a: np.ndarray, p_b: np.ndarray) -> float:
        """KL(p_b || p_a) 平均散度——衡量 IS/OOS 概率分布差异。

        越小越说明 IS 模型在 OOS 上的概率分布与 OOS 模型一致（不过拟合）。
        """
        eps = 1e-10
        p_a = np.clip(p_a, eps, 1.0)
        p_b = np.clip(p_b, eps, 1.0)
        # KL(p_b || p_a) = Σ p_b * log(p_b / p_a)
        kl_per_sample = np.sum(p_b * np.log(p_b / p_a), axis=1)
        return float(np.mean(kl_per_sample))

    @staticmethod
    def _judge(ratio: float) -> A2Verdict:
        if ratio >= PASS_RATIO:
            return A2Verdict.PASS
        if ratio >= REVIEW_RATIO:
            return A2Verdict.REVIEW
        return A2Verdict.FAIL

    @staticmethod
    def _degraded_report(is_samples: int, oos_samples: int) -> A2Report:
        """降级报告（hmmlearn 不可用 / 拟合失败）。"""
        return A2Report(
            is_accuracy=0.0,
            oos_accuracy=0.0,
            ratio=0.0,
            kl_divergence=float("inf"),
            label_alignment="降级（未对齐）",
            is_samples=is_samples,
            oos_samples=oos_samples,
            verdict=A2Verdict.FAIL,
            summary="A2 降级：HMM 拟合失败或 hmmlearn 不可用",
            degraded=True,
        )
