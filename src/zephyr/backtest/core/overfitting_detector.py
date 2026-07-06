# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.overfitting_detector
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES]
# [CONSUMERS] zephyr.backtest.implementations.vectorized_engine; zephyr.backtest.implementations.event_driven_engine
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 过拟合三维度三层; 样本外Sharpe<70%样本内→否决
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] OverfittingError
# [TESTS]
# [TTL] permanent
# [A_module] module_id=MOD-BT-001-overfitting_detector | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
"""过拟合检测模块(三维度 + 三层)

职责:
  - 过拟合检测三维度(D-FACTOR-03):
      1. Walk-Forward: 滚动窗口样本外验证, 参数稳定性
      2. 参数敏感性: 参数微调±10%, 收益变化幅度
      3. 泛化能力: 跨时段/跨市场/跨标的稳健性
  - 过拟合检测三层(D-SIMULATION-18/38/56):
      1. SIM-18 研究时手动检测: 因子/策略回测后人工审查
      2. SIM-38 样本内外对比: 样本内vs样本外收益差异+交叉验证+多重比较偏差校正
      3. SIM-56 上线前自动门禁: overfitting_flag=True→阻断上线
  - 过拟合否决阈值(P0-9): 样本外Sharpe < 70%样本内Sharpe → 否决上线

约束:
  - 三维度任一不稳定 → is_overfitting=True
  - 样本内外比率使用Sharpe(年化), 样本内Sharpe<=0时不适用比率判定

SSoT: docs/03_modules/_domain_backtest/blueprint.md §16.7
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Walk-Forward稳定性阈值(维度1)
WF_POSITIVE_RATIO_THRESHOLD = 0.60  # 至少60%的fold需为正Sharpe
WF_CV_THRESHOLD = 1.50  # Sharpe变异系数(std/|mean|)上限
WF_DISASTER_SHARPE = -0.50  # 单fold Sharpe低于此值视为灾难fold

# 参数敏感性阈值(维度2): 参数微调导致Sharpe相对变化上限
PARAM_MAX_CHANGE_THRESHOLD = 0.30

# 泛化能力阈值(维度3)
GEN_POSITIVE_RATIO_THRESHOLD = 0.60
GEN_CV_THRESHOLD = 1.50


class OverfittingError(Exception):
    """过拟合检测错误"""

    error_code = "ZA-BT-0005"

    def __init__(self, *args, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code


@dataclass(frozen=True)
class OverfittingConfig:
    """过拟合检测配置(不可变)

    Attributes:
        parameter_perturbation_pct: 参数微调幅度, 默认±10%
        oos_sharpe_threshold_ratio: 样本外/样本内Sharpe比率否决阈值, 默认0.70
            (样本外Sharpe < 70%样本内Sharpe → 否决上线, P0-9)
        cross_validation_folds: 交叉验证折数(用于SIM-38样本内外对比)
    """

    parameter_perturbation_pct: float = 0.10
    oos_sharpe_threshold_ratio: float = 0.70
    cross_validation_folds: int = 5

    def __post_init__(self):
        if not (0.0 < self.parameter_perturbation_pct <= 1.0):
            raise OverfittingError(
                f"parameter_perturbation_pct必须在(0, 1], got {self.parameter_perturbation_pct}"
            )
        if not (0.0 <= self.oos_sharpe_threshold_ratio <= 1.0):
            raise OverfittingError(
                f"oos_sharpe_threshold_ratio必须在[0, 1], got {self.oos_sharpe_threshold_ratio}"
            )
        if self.cross_validation_folds <= 0:
            raise OverfittingError(
                f"cross_validation_folds必须>0, got {self.cross_validation_folds}"
            )


class OverfittingDetector:
    """过拟合检测器(三维度 + 三层)

    消费Walk-Forward结果/参数扰动结果/跨时段结果与样本内外Sharpe,
    输出is_overfitting标志供SIM-56上线前自动门禁使用。
    """

    def __init__(self, config: OverfittingConfig | None = None):
        self.config = config if config is not None else OverfittingConfig()

    @staticmethod
    def _extract_sharpe(result: dict) -> float:
        """从结果字典提取Sharpe值, 处理None值/缺失键/非数值"""
        val = result.get("sharpe_ratio")
        if val is None:
            val = result.get("sharpe", 0.0)
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0

    def check_walk_forward_stability(self, walk_forward_results: list[dict]) -> dict:
        """Walk-Forward参数稳定性检测(维度1)

        检查各fold的Sharpe一致性: 正Sharpe占比/变异系数/灾难fold。

        Args:
            walk_forward_results: Walk-Forward各fold结果列表, 每项需含 sharpe_ratio 或 sharpe

        Returns:
            dict: is_stable, mean_sharpe, std_sharpe, cv, positive_ratio,
                  min_sharpe, n_folds, reasons
        """
        if not walk_forward_results:
            return {
                "is_stable": True,
                "mean_sharpe": 0.0,
                "std_sharpe": 0.0,
                "cv": 0.0,
                "positive_ratio": 0.0,
                "min_sharpe": 0.0,
                "n_folds": 0,
                "reasons": [],
            }

        sharpes = np.array(
            [self._extract_sharpe(r)
             for r in walk_forward_results],
            dtype=float,
        )
        n = len(sharpes)
        mean_sharpe = float(np.mean(sharpes))
        std_sharpe = float(np.std(sharpes, ddof=1)) if n > 1 else 0.0
        if abs(mean_sharpe) > 1e-10:
            cv = float(std_sharpe / abs(mean_sharpe))
        else:
            cv = float("inf") if std_sharpe > 0 else 0.0
        positive_ratio = float(np.mean(sharpes > 0))
        min_sharpe = float(np.min(sharpes))

        reasons: list[str] = []
        is_stable = True
        if positive_ratio < WF_POSITIVE_RATIO_THRESHOLD:
            is_stable = False
            reasons.append(
                f"Walk-Forward正Sharpe fold占比{positive_ratio:.2%}低于阈值{WF_POSITIVE_RATIO_THRESHOLD:.2%}"
            )
        if std_sharpe > 0 and cv > WF_CV_THRESHOLD:
            is_stable = False
            reasons.append(
                f"Walk-Forward Sharpe变异系数{cv:.2f}超过阈值{WF_CV_THRESHOLD:.2f}"
            )
        if min_sharpe < WF_DISASTER_SHARPE:
            is_stable = False
            reasons.append(
                f"Walk-Forward存在灾难fold(最低Sharpe={min_sharpe:.2f}<{WF_DISASTER_SHARPE:.2f})"
            )

        return {
            "is_stable": bool(is_stable),
            "mean_sharpe": mean_sharpe,
            "std_sharpe": std_sharpe,
            "cv": cv,
            "positive_ratio": positive_ratio,
            "min_sharpe": min_sharpe,
            "n_folds": n,
            "reasons": reasons,
        }

    def check_parameter_sensitivity(
        self, base_result: dict, perturbed_results: list[dict]
    ) -> dict:
        """参数敏感性检测(维度2)

        参数微调±parameter_perturbation_pct后, 检查Sharpe相对变化幅度。
        相对变化 = |perturbed_sharpe - base_sharpe| / |base_sharpe|。

        Args:
            base_result: 基准(原始参数)结果, 需含 sharpe_ratio 或 sharpe
            perturbed_results: 参数微调后结果列表, 每项需含 sharpe_ratio 或 sharpe

        Returns:
            dict: is_stable, base_sharpe, max_change, mean_change, n_perturbed, reasons
        """
        base_sharpe = self._extract_sharpe(base_result)
        if not perturbed_results:
            return {
                "is_stable": True,
                "base_sharpe": base_sharpe,
                "max_change": 0.0,
                "mean_change": 0.0,
                "n_perturbed": 0,
                "reasons": [],
            }

        perturbed_sharpes = np.array(
            [self._extract_sharpe(r)
             for r in perturbed_results],
            dtype=float,
        )
        reasons: list[str] = []

        if abs(base_sharpe) > 1e-10:
            relative_changes = np.abs(perturbed_sharpes - base_sharpe) / abs(base_sharpe)
            max_change = float(np.max(relative_changes))
            mean_change = float(np.mean(relative_changes))
            is_stable = True
            if max_change > PARAM_MAX_CHANGE_THRESHOLD:
                is_stable = False
                reasons.append(
                    f"参数微调±{self.config.parameter_perturbation_pct:.0%}导致Sharpe最大相对变化"
                    f"{max_change:.2%}超过阈值{PARAM_MAX_CHANGE_THRESHOLD:.2%}"
                )
        else:
            # 基准Sharpe接近0, 相对变化无意义, 跳过敏感性判定
            max_change = 0.0
            mean_change = 0.0
            is_stable = True
            reasons.append("基准Sharpe接近0, 参数敏感性无法评估(跳过)")

        return {
            "is_stable": bool(is_stable),
            "base_sharpe": base_sharpe,
            "max_change": max_change,
            "mean_change": mean_change,
            "n_perturbed": len(perturbed_results),
            "reasons": reasons,
        }

    def check_generalization(self, period_results: list[dict]) -> dict:
        """泛化能力检测(维度3)

        跨时段/跨市场/跨标的Sharpe稳健性: 正Sharpe占比与变异系数。

        Args:
            period_results: 各时段/市场/标的结果列表, 每项需含 sharpe_ratio 或 sharpe

        Returns:
            dict: is_stable, mean_sharpe, std_sharpe, cv, positive_ratio, n_periods, reasons
        """
        if not period_results:
            return {
                "is_stable": True,
                "mean_sharpe": 0.0,
                "std_sharpe": 0.0,
                "cv": 0.0,
                "positive_ratio": 0.0,
                "n_periods": 0,
                "reasons": [],
            }

        sharpes = np.array(
            [self._extract_sharpe(r)
             for r in period_results],
            dtype=float,
        )
        n = len(sharpes)
        mean_sharpe = float(np.mean(sharpes))
        std_sharpe = float(np.std(sharpes, ddof=1)) if n > 1 else 0.0
        if abs(mean_sharpe) > 1e-10:
            cv = float(std_sharpe / abs(mean_sharpe))
        else:
            cv = float("inf") if std_sharpe > 0 else 0.0
        positive_ratio = float(np.mean(sharpes > 0))

        reasons: list[str] = []
        is_stable = True
        if positive_ratio < GEN_POSITIVE_RATIO_THRESHOLD:
            is_stable = False
            reasons.append(
                f"跨时段正Sharpe占比{positive_ratio:.2%}低于阈值{GEN_POSITIVE_RATIO_THRESHOLD:.2%}"
            )
        if std_sharpe > 0 and cv > GEN_CV_THRESHOLD:
            is_stable = False
            reasons.append(
                f"跨时段Sharpe变异系数{cv:.2f}超过阈值{GEN_CV_THRESHOLD:.2f}"
            )

        return {
            "is_stable": bool(is_stable),
            "mean_sharpe": mean_sharpe,
            "std_sharpe": std_sharpe,
            "cv": cv,
            "positive_ratio": positive_ratio,
            "n_periods": n,
            "reasons": reasons,
        }

    def compare_in_out_sample(self, is_sharpe: float, oos_sharpe: float) -> dict:
        """样本内外对比(SIM-38 / P0-9否决阈值)

        样本外Sharpe < oos_sharpe_threshold_ratio * 样本内Sharpe → 否决上线。

        Args:
            is_sharpe: 样本内(in-sample)Sharpe
            oos_sharpe: 样本外(out-of-sample)Sharpe

        Returns:
            dict: is_overfitting, is_sharpe, oos_sharpe, ratio, reason
        """
        is_sharpe = float(is_sharpe)
        oos_sharpe = float(oos_sharpe)
        threshold = self.config.oos_sharpe_threshold_ratio

        if is_sharpe > 1e-10:
            ratio = oos_sharpe / is_sharpe
            is_overfitting = ratio < threshold
            if is_overfitting:
                reason = (
                    f"样本外Sharpe({oos_sharpe:.4f})/样本内Sharpe({is_sharpe:.4f})"
                    f"={ratio:.2%}低于阈值{threshold:.0%}→否决上线(P0-9)"
                )
            else:
                reason = ""
        else:
            # 样本内Sharpe非正, 无法计算OOS/IS比率, 不适用过拟合否决
            ratio = 0.0
            is_overfitting = False
            reason = "样本内Sharpe非正, 无法计算OOS/IS比率(跳过过拟合否决)"

        return {
            "is_overfitting": bool(is_overfitting),
            "is_sharpe": is_sharpe,
            "oos_sharpe": oos_sharpe,
            "ratio": float(ratio),
            "reason": reason,
        }

    def detect(
        self,
        walk_forward_results: list[dict] = None,
        perturbed_results: list[dict] = None,
        period_results: list[dict] = None,
        is_sharpe: float = 0,
        oos_sharpe: float = 0,
    ) -> dict:
        """综合过拟合检测(三维度 + 样本内外对比, SIM-56上线前自动门禁)

        三维度任一不稳定或样本内外比率触发否决 → is_overfitting=True。
        未提供的维度视为未检测(默认稳定, 不触发否决)。

        Args:
            walk_forward_results: Walk-Forward各fold结果(维度1), None则跳过
            perturbed_results: 参数微调结果(维度2), None则跳过; 基准Sharpe取is_sharpe
            period_results: 跨时段结果(维度3), None则跳过
            is_sharpe: 样本内Sharpe(同时作为参数敏感性基准), 默认0
            oos_sharpe: 样本外Sharpe, 默认0

        Returns:
            dict: is_overfitting, oos_is_ratio, walk_forward_stable,
                  parameter_stable, generalization_stable, reasons
        """
        reasons: list[str] = []
        walk_forward_stable = True
        parameter_stable = True
        generalization_stable = True

        # 维度1: Walk-Forward稳定性
        if walk_forward_results:
            wf = self.check_walk_forward_stability(walk_forward_results)
            walk_forward_stable = wf["is_stable"]
            if not walk_forward_stable:
                reasons.extend(wf["reasons"])

        # 维度2: 参数敏感性(基准Sharpe = 样本内Sharpe)
        if perturbed_results:
            base_result = {"sharpe_ratio": float(is_sharpe)}
            ps = self.check_parameter_sensitivity(base_result, perturbed_results)
            parameter_stable = ps["is_stable"]
            if not parameter_stable:
                reasons.extend(ps["reasons"])

        # 维度3: 泛化能力
        if period_results:
            gen = self.check_generalization(period_results)
            generalization_stable = gen["is_stable"]
            if not generalization_stable:
                reasons.extend(gen["reasons"])

        # SIM-38 / P0-9: 样本内外对比(硬否决)
        io = self.compare_in_out_sample(is_sharpe, oos_sharpe)
        oos_is_ratio = io["ratio"]
        if io["is_overfitting"]:
            reasons.append(io["reason"])

        is_overfitting = (
            (not walk_forward_stable)
            or (not parameter_stable)
            or (not generalization_stable)
            or io["is_overfitting"]
        )

        return {
            "is_overfitting": bool(is_overfitting),
            "oos_is_ratio": float(oos_is_ratio),
            "walk_forward_stable": bool(walk_forward_stable),
            "parameter_stable": bool(parameter_stable),
            "generalization_stable": bool(generalization_stable),
            "reasons": reasons,
        }


__all__ = [
    "OverfittingConfig",
    "OverfittingDetector",
    "OverfittingError",
    "WF_POSITIVE_RATIO_THRESHOLD",
    "WF_CV_THRESHOLD",
    "WF_DISASTER_SHARPE",
    "PARAM_MAX_CHANGE_THRESHOLD",
    "GEN_POSITIVE_RATIO_THRESHOLD",
    "GEN_CV_THRESHOLD",
]
