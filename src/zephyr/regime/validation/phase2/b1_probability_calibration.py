# [BLUEPRINT] MOD-REGIME_VAL-002 | 12_regime_phase2_validation §2.4
# [MODULE] zephyr.regime.validation.phase2.b1_probability_calibration
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] zephyr.regime.validation.phase2.phase2_runner; scripts.tests.run_phase2_validation
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] forward_days>0; confidence∈[0,1]; 校准误差<0.10→PASS; 每态方向由数据推断(非固定映射)
# [MODIFY-GUARD] 12_regime_phase2_validation.md §2.4
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] B1ValidationError(ZA-REGIME-0023)
# [TESTS] tests/regime/phase2/test_b1_probability_calibration.py
# [A_module] module_id=MOD-REGIME_VAL-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #12_regime_phase2_validation §2.4 #12_regime_phase2_validation §4.1 B1
"""
B1 概率校准度验证器（12_regime_phase2_validation §2.4）。

方案 A：后续收益实现代理标签。
  1. 全历史 detect 收集 (timestamp, confidence, dominant_regime)
  2. 对每个 timestamp，算后续 forward_days 累计收益
  3. 按 dominant_regime 分组，算每态平均后续收益 → 推断"预期方向"（sign）
  4. "实际发生" = 该 timestamp 后续收益方向与态预期方向一致
  5. confidence 分桶（0-20/.../80-100%），每桶算"实际发生"频率
  6. 校准误差 = mean(|桶内平均 confidence - 桶内实际频率|)

判定（12_regime_phase2_validation §2.4，2026-08-08 修订）：
  ECE（样本加权校准误差）< 0.10 → PASS；0.10 ≤ ECE < 0.15 → REVIEW；≥ 0.15 → FAIL
  ECE 是行业标准（Guo et al. 2017 / sklearn calibration_curve），按样本量加权各桶误差，
  避免简单均值对 n=1 和 n=221 桶等权的统计不合理性。

设计决策：
  - 每态"预期方向"由数据推断（平均后续收益 sign），非固定映射——避免无监督 HMM
    的标签语义依赖，方案自洽（12_regime_phase2_validation §7 开放问题 2 的务实解法）。
  - 态平均收益接近 0（|mean| < min_return_threshold）时跳过该态（无明确方向）。

依据: 12_regime_phase2_validation §2.4 / 12_regime_phase2_validation §4.1 B1
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: b1_probability_calibration.py
# 层: 算法
# - id: A1
#   name_zh: ① B1Report
#   name_en: B1Report
#   intro: B1 概率校准度报告。
#   desc: B1 概率校准度报告。；公共方法（定义序）: to_dict；源码 L131-L166
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② B1ProbabilityCalibration
#   name_en: B1ProbabilityCalibration
#   intro: B1 概率校准度验证器（后续收益实现代理标签）。
#   desc: B1 概率校准度验证器（后续收益实现代理标签）。 Usage（real 模式）:: b1 = B1ProbabilityCalibration() report = b1.val…；公共方法（定义序）: validat…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A2 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: B1Report, B1ProbabilityCalibration
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
import pandas as pd

try:
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover  # noqa: BLE001
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)

# 判定门槛（12_regime_phase2_validation §2.4，2026-08-08 修订为 ECE 基准）
PASS_ERROR = 0.10  # ECE < 10% → PASS
REVIEW_ERROR = 0.15  # ECE < 15% → REVIEW
DEFAULT_FORWARD_DAYS = 20
MIN_RETURN_THRESHOLD = 0.005  # 态平均收益 |mean| < 0.5% 视为无明确方向
# confidence 分桶边界（5 桶：0-20/20-40/40-60/60-80/80-100%）
BUCKET_EDGES = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
BUCKET_LABELS = ["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"]


class B1ValidationError(ZephyrBaseError):
    """ZA-REGIME-0023: B1 验证器错误（数据不足/收益计算异常）。"""

    error_code = "ZA-REGIME-0023"


class B1Verdict(str, Enum):
    """校准度判定结果。"""

    PASS = "PASS"  # 误差 < 10%
    REVIEW = "REVIEW"  # 10% ≤ 误差 < 15%
    FAIL = "FAIL"  # ≥ 15%


@dataclass(frozen=True)
class B1CalibrationPoint:
    """单桶校准点。"""

    bucket: str  # "0-20%", ...
    predicted: float  # 桶内平均 confidence（预测概率）
    actual: float  # 桶内实际发生频率
    count: int  # 桶内样本数
    error: float  # |predicted - actual|


@dataclass(frozen=True)
class B1Report:
    """B1 概率校准度报告。"""

    reliability_curve: list[B1CalibrationPoint]  # 各桶校准点
    calibration_error: float  # mean(|predicted - actual|) 简单均值
    weighted_calibration_error: float  # ECE 样本加权均值（行业标准，诊断用）
    max_bucket_error: float  # 单桶最大误差
    forward_days: int
    total_samples: int  # 有效样本数（有后续收益 + 态有方向）
    regime_directions: dict[str, str]  # {regime: "涨"/"跌"} 数据推断的方向
    verdict: B1Verdict
    summary: str
    degraded: bool  # 样本不足 → 降级

    def to_dict(self) -> dict[str, Any]:
        return {
            "reliability_curve": [
                {
                    "bucket": p.bucket,
                    "predicted": round(p.predicted, 4),
                    "actual": round(p.actual, 4),
                    "count": p.count,
                    "error": round(p.error, 4),
                }
                for p in self.reliability_curve
            ],
            "calibration_error": round(self.calibration_error, 4),
            "weighted_calibration_error": round(self.weighted_calibration_error, 4),
            "max_bucket_error": round(self.max_bucket_error, 4),
            "forward_days": self.forward_days,
            "total_samples": self.total_samples,
            "regime_directions": self.regime_directions,
            "verdict": self.verdict.value,
            "summary": self.summary,
            "degraded": self.degraded,
        }


class B1ProbabilityCalibration:
    """B1 概率校准度验证器（后续收益实现代理标签）。

    Usage（real 模式）::

        b1 = B1ProbabilityCalibration()
        report = b1.validate(
            detect_records=[{"timestamp": ts, "confidence": 0.8,
                             "dominant_regime": "r3"}, ...],
            close=index_close_series,
            forward_days=20,
        )
    """

    def validate(
        self,
        detect_records: list[dict[str, Any]],
        close: pd.Series,
        forward_days: int = DEFAULT_FORWARD_DAYS,
    ) -> B1Report:
        """计算校准度。

        Args:
            detect_records: [{"timestamp": pd.Timestamp, "confidence": float,
                              "dominant_regime": str}, ...]。
            close: 收盘价序列（index=日期），用于算 forward return。
            forward_days: 后续收益天数（默认 20 交易日）。

        Returns:
            B1Report。
        """
        if not detect_records:
            raise B1ValidationError("detect_records 为空")
        if forward_days <= 0:
            raise B1ValidationError(f"forward_days 须 >0，实际 {forward_days}")

        # 1. 算每个 timestamp 的后续 forward_days 累计收益
        forward_returns = self._compute_forward_returns(close, forward_days)

        # 2. 关联 detect_records 与 forward_returns
        records: list[dict[str, Any]] = []
        for rec in detect_records:
            ts = rec["timestamp"]
            if ts not in forward_returns.index:
                continue
            fr = forward_returns.loc[ts]
            if np.isnan(fr):
                continue
            records.append(
                {
                    "timestamp": ts,
                    "confidence": float(rec["confidence"]),
                    "dominant_regime": str(rec["dominant_regime"]),
                    "forward_return": float(fr),
                }
            )

        if len(records) < 50:
            _logger.warning("B1: 有效样本不足 %d（需 ≥50），降级", len(records))
            return self._degraded_report(forward_days, len(records))

        # 3. 按态分组，推断每态"预期方向"（sign of mean forward return）
        regime_directions = self._infer_regime_directions(records)

        # 4. 标记"实际发生"：后续收益方向与态预期方向一致
        occurred_list: list[int] = []
        confidences: list[float] = []
        for rec in records:
            regime = rec["dominant_regime"]
            direction = regime_directions.get(regime)
            if direction is None:
                continue  # 该态无明确方向，跳过
            fr = rec["forward_return"]
            expected_pos = direction == "涨"
            actual_pos = fr > 0
            occurred = 1 if (expected_pos == actual_pos) else 0
            occurred_list.append(occurred)
            confidences.append(rec["confidence"])

        if len(occurred_list) < 50:
            _logger.warning("B1: 有方向样本不足 %d，降级", len(occurred_list))
            return self._degraded_report(forward_days, len(occurred_list))

        # 5. confidence 分桶 + 校准曲线
        confidences_arr = np.array(confidences)
        occurred_arr = np.array(occurred_list)
        curve = self._build_reliability_curve(confidences_arr, occurred_arr)

        # 6. 校准误差
        errors = [abs(p.predicted - p.actual) for p in curve if p.count > 0]
        cal_error = float(np.mean(errors)) if errors else 1.0
        max_error = max(errors) if errors else 1.0

        # ECE（Expected Calibration Error）—— 样本加权均值，行业标准校准评估指标
        # 简单均值对 n=1 和 n=221 桶等权，统计上不合理；ECE 按样本量加权，
        # 是 Guo et al. 2017 / sklearn calibration_curve 的标准评估方式。
        total_n = sum(p.count for p in curve if p.count > 0)
        weighted_error = (
            sum(p.count * abs(p.predicted - p.actual) for p in curve if p.count > 0) / total_n if total_n > 0 else 1.0
        )

        # 判定使用 ECE（行业标准），简单均值仅作诊断
        verdict = self._judge(weighted_error)
        summary = (
            f"B1 概率校准度: ECE={weighted_error:.1%}, 误差={cal_error:.1%}, "
            f"最大桶误差={max_error:.1%}, "
            f"样本={len(occurred_list)}, forward={forward_days}d → {verdict.value}"
        )
        _logger.info("B1: %s", summary)
        return B1Report(
            reliability_curve=curve,
            calibration_error=round(cal_error, 4),
            weighted_calibration_error=round(weighted_error, 4),
            max_bucket_error=round(max_error, 4),
            forward_days=forward_days,
            total_samples=len(occurred_list),
            regime_directions=regime_directions,
            verdict=verdict,
            summary=summary,
            degraded=False,
        )

    # ── 内部 ──────────────────────────────────────────────────────────

    @staticmethod
    def _compute_forward_returns(close: pd.Series, forward_days: int) -> pd.Series:
        """算每个时点的后续 forward_days 累计收益率。

        r_t = close[t + forward_days] / close[t] - 1

        Returns:
            pd.Series，index 同 close，末尾 forward_days 日为 NaN（无后续数据）。
        """
        future = close.shift(-forward_days)
        return (future / close - 1.0).dropna()

    @staticmethod
    def _infer_regime_directions(
        records: list[dict[str, Any]],
    ) -> dict[str, str]:
        """按态分组算平均后续收益，推断方向（涨/跌）。

        |mean_return| < MIN_RETURN_THRESHOLD 的态视为无明确方向（不返回）。
        """
        regime_returns: dict[str, list[float]] = {}
        for rec in records:
            regime_returns.setdefault(rec["dominant_regime"], []).append(rec["forward_return"])
        directions: dict[str, str] = {}
        for regime, rets in regime_returns.items():
            mean_r = float(np.mean(rets))
            if abs(mean_r) < MIN_RETURN_THRESHOLD:
                continue  # 无明确方向
            directions[regime] = "涨" if mean_r > 0 else "跌"
        return directions

    @staticmethod
    def _build_reliability_curve(confidences: np.ndarray, occurred: np.ndarray) -> list[B1CalibrationPoint]:
        """confidence 分桶 + 每桶算预测 vs 实际频率。"""
        curve: list[B1CalibrationPoint] = []
        for i in range(len(BUCKET_EDGES) - 1):
            lo, hi = BUCKET_EDGES[i], BUCKET_EDGES[i + 1]
            mask = (confidences >= lo) & (confidences < hi)
            if i == len(BUCKET_EDGES) - 2:
                mask = (confidences >= lo) & (confidences <= hi)
            count = int(mask.sum())
            if count == 0:
                curve.append(
                    B1CalibrationPoint(
                        bucket=BUCKET_LABELS[i],
                        predicted=0.0,
                        actual=0.0,
                        count=0,
                        error=0.0,
                    )
                )
                continue
            predicted = float(confidences[mask].mean())
            actual = float(occurred[mask].mean())
            curve.append(
                B1CalibrationPoint(
                    bucket=BUCKET_LABELS[i],
                    predicted=predicted,
                    actual=actual,
                    count=count,
                    error=abs(predicted - actual),
                )
            )
        return curve

    @staticmethod
    def _judge(error: float) -> B1Verdict:
        if error < PASS_ERROR:
            return B1Verdict.PASS
        if error < REVIEW_ERROR:
            return B1Verdict.REVIEW
        return B1Verdict.FAIL

    @staticmethod
    def _degraded_report(forward_days: int, total_samples: int) -> B1Report:
        return B1Report(
            reliability_curve=[],
            calibration_error=1.0,
            weighted_calibration_error=1.0,
            max_bucket_error=1.0,
            forward_days=forward_days,
            total_samples=total_samples,
            regime_directions={},
            verdict=B1Verdict.FAIL,
            summary=f"B1 降级：有效样本不足（{total_samples}）",
            degraded=True,
        )
