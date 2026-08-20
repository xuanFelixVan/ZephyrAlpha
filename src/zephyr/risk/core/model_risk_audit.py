# [BLUEPRINT] MOD-RK-18 | docs/03_modules/_domain_risk/model_risk_audit/blueprint.md | §
# [MODULE] zephyr.risk.core.model_risk_audit
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.risk_manager_base; zephyr.intelligence.model_drift_detector; zephyr.factor.analysis.ic_decay
# [CONSUMERS] MOD-L04-001(DefaultRiskManagerOrchestrator,模型风险评估)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] risk_level=drift+ic_decay双维度映射;drift_threshold=ModelDriftDetector.DIVERGENCE_THRESHOLD;纯机制零参数
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidModelRiskInputError
# [TESTS] tests/risk/core/test_model_risk_audit.py
# [A_module] module_id=MOD-RK-18 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

D_RISK — Model Risk Auditor (MOD-RK-18)

模型风险审计器——交易预测模型的漂移/衰退/偏差综合审计。

组装缺口（非从零实现）：漂移检测（intelligence 域 ModelDriftDetector，
面向 LLM 行为漂移）与 IC 衰减（factor 域 compute_ic_decay/compute_half_life）
散落各处，本模块将其**组装+聚焦**为 risk/core/ 内面向交易预测模型的统一
风险审计报告。

核心公式 (blueprint §3):
  drift_detected: JS 散度 > 0.15 (来自 ModelDriftDetector.DIVERGENCE_THRESHOLD)
  ic_decay_pct: IC 衰减百分比 = (initial_ic - final_ic) / initial_ic
  ic_half_life: IC 半衰期（lag 数，复用 compute_half_life 线性插值）
  risk_level: drift + ic_decay 双维度 → low/medium/high/critical
  bias_detected: 预测偏差超出阈值（默认随 drift，可选显式 bias_score）

风险等级矩阵:
                   | ic_decay<0.3 | 0.3-0.5 | 0.5-0.7 | >=0.7 |
  | no drift       | low          | low     | medium  | high  |
  | drift          | medium       | medium  | high    | critical |

日志埋点:
  - INFO: 审计完成（drift + divergence + ic_decay_pct + ic_half_life + risk_level）
  - WARNING: 输入数据不足跳过 / 检测器异常降级
  - DEBUG: 逐检测器原始输出

SSoT: depgraph MOD-RK-18 | blueprint.md §3 核心规则

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模型输出样本 列表
#   fields: list[dict]如{"pred": 0.1}; 调用前需先establish_baseline否则检测器返回drift_detected=False
#   code: audit() model_outputs L288
# - id: I2
#   name: IC衰减曲线 字典
#   fields: {lag: ic_value}预计算的各lag IC值(调用方经factor域compute_ic_decay获得)
#   code: audit() ic_data L289
# - id: I3
#   name: 预测偏差分数 浮点数可选
#   fields: bias_score显式偏差分; None则bias_detected随drift_detected
#   code: audit() bias_score L290
# - id: I4
#   name: 阈值参数 配置
#   fields: drift_threshold默认取ModelDriftDetector.DIVERGENCE_THRESHOLD(0.15) + ic_decay_threshold0.50 + bias_threshold0.15
#   code: __init__() L124-150
# 层: 特征
# - id: F1
#   name_zh: JS散度漂移分
#   name_en: divergence_score
#   intro: 模型输出分布相对基线的漂移程度(JS散度)
#   formula: JS散度(复用intelligence域ModelDriftDetector.detect_drift); 检测器异常降级为drift=False,score=0
#   code: model_risk_audit.py L172-190
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F2
#   name_zh: IC衰减百分比
#   name_en: ic_decay_pct
#   intro: 首尾IC绝对值衰减了多少比例
#   formula: ic_decay_pct=max(0, (|ic₀|−|ic_N|)/|ic₀|); |ic₀|<1e-10→0
#   code: model_risk_audit.py L218-224
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F3
#   name_zh: IC半衰期
#   name_en: ic_half_life
#   intro: IC衰减到一半需要的lag数(线性插值)
#   formula: 复用factor域compute_half_life(ic_series)线性插值; 失败降级0.0
#   code: model_risk_audit.py L226-232
#   registry: factor_registry: 无FCT条目
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① 综合审计组装
#   name_en: ModelRiskAuditor.audit
#   intro: 组装漂移检测+IC衰减+bias判定, 产出审计指标集
#   desc: _compute_drift跑漂移(异常不阻断降级no-drift); _compute_ic_decay算衰减与半衰期; bias显式score优先否则随drift; 无输入跳过对应检测
#   inputs: I1 I2 I3 I4 F1 F2 F3
#   outputs: 审计指标集(drift/decay/half_life/bias)
# - id: A2
#   name_zh: ② 双维风险等级映射
#   name_en: _compute_risk_level
#   intro: drift×ic_decay双维矩阵映射low/medium/high/critical
#   desc: drift且decay≥0.7→critical; drift且0.5≤decay<0.7→high; 其余drift→medium; 无drift时decay≥0.7→high/0.5-0.7→medium/<0.5→low
#   inputs: A1 F2
#   outputs: risk_level等级字符串
#   invariant: risk_level=drift+ic_decay双维度映射
# - id: A3
#   name_zh: ③ 风控检查结果转换
#   name_en: to_risk_check_result
#   intro: 审计报告转RiskCheckResult供编排器聚合
#   desc: critical/high→HALT; medium→warning; low→info; passed=(risk_level==low)
#   inputs: A2
#   outputs: RiskCheckResult
# 层: 输出
# - id: O1
#   name_zh: 模型风险审计报告
#   name_en: ModelRiskAuditReport
#   intro: 含漂移标志/散度/IC衰减/半衰期/偏差/综合风险等级的不可变审计报告
#   downstream: DefaultRiskManagerOrchestrator MOD-L04-001(模型风险评估)
# - id: O2
#   name_zh: 风控检查结果
#   name_en: RiskCheckResult
#   intro: 供风控编排器统一聚合的模型风险检查结果
#   downstream: DefaultRiskManagerOrchestrator MOD-L04-001
# [/ALGO_FLOW]
#
# 边:
# I1 -.->|断点| F1
# I2 -.->|断点| F2
# I2 -.->|断点| F3
# F1 --> A1
# F2 --> A1
# F3 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# F2 --> A2
# A2 --> O1
# A2 --> A3
# A3 --> O2
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from zephyr.risk.risk_manager_base import RiskCheckResult

_logger = logging.getLogger(__name__)

__all__ = [
    "ModelRiskAuditReport",
    "ModelRiskAuditor",
    "InvalidModelRiskInputError",
]

#: IC 衰减告警阈值（IC 衰减 >50% 触发告警，来自 battle_map 验收标准）
DEFAULT_IC_DECAY_THRESHOLD: float = 0.50

#: bias 判定阈值（divergence_score > 此值判定为预测偏差，默认对齐 drift 阈值）
DEFAULT_BIAS_THRESHOLD: float = 0.15


class InvalidModelRiskInputError(ValueError):
    """模型风险审计输入数据无效。"""


# ── 数据模型 ──────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ModelRiskAuditReport:
    """模型风险审计报告（不可变）。

    Attributes:
        drift_detected: 是否检测到模型漂移（JS 散度 > 阈值）
        divergence_score: JS 散度值
        ic_half_life: IC 半衰期（lag 数，线性插值），无 IC 数据时为 0.0
        ic_decay_pct: IC 衰减百分比 [0, 1+]，无 IC 数据时为 0.0
        bias_detected: 是否检测到预测偏差
        risk_level: 综合风险等级 low/medium/high/critical
        details: 原始检测器输出
        timestamp: 审计时间（UTC）
        idempotency_key: 幂等键
    """

    drift_detected: bool
    divergence_score: float
    ic_half_life: float
    ic_decay_pct: float
    bias_detected: bool
    risk_level: str
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    idempotency_key: str = ""


# ── 模型风险审计器 ──────────────────────────────────────────────────


class ModelRiskAuditor:
    """模型风险审计器——组装漂移检测 + IC 衰减的综合审计。

    纯机制零参数：阈值默认取真源（ModelDriftDetector.DIVERGENCE_THRESHOLD），
    组装现有检测器不重新实现。

    Usage:
        auditor = ModelRiskAuditor()
        report = auditor.audit(
            model_outputs=[{"pred": 0.1}, {"pred": 0.2}],
            ic_data={1: 0.05, 5: 0.04, 10: 0.02, 20: 0.01},
        )
    """

    def __init__(
        self,
        drift_threshold: float | None = None,
        ic_decay_threshold: float = DEFAULT_IC_DECAY_THRESHOLD,
        bias_threshold: float = DEFAULT_BIAS_THRESHOLD,
        drift_detector: Any | None = None,
    ):
        """初始化模型风险审计器。

        Args:
            drift_threshold: JS 散度漂移阈值，None=取 ModelDriftDetector.DIVERGENCE_THRESHOLD
            ic_decay_threshold: IC 衰减告警阈值（默认 0.50）
            bias_threshold: 预测偏差阈值（默认 0.15）
            drift_detector: 自定义 ModelDriftDetector 实例（测试用），None=创建默认
        """
        # 延迟导入避免循环依赖 + 从真源获取默认阈值
        from zephyr.intelligence.model_drift_detector import ModelDriftDetector

        self._drift_threshold = (
            drift_threshold if drift_threshold is not None else ModelDriftDetector.DIVERGENCE_THRESHOLD
        )
        self._ic_decay_threshold = ic_decay_threshold
        self._bias_threshold = bias_threshold
        # 允许注入自定义检测器（测试用），默认创建标准实例
        self._drift_detector = drift_detector or ModelDriftDetector()

    # ── 漂移检测 ──

    def _compute_drift(
        self,
        model_outputs: list[dict[str, Any]] | None,
    ) -> tuple[bool, float, dict[str, Any]]:
        """运行 ModelDriftDetector 计算漂移。

        Args:
            model_outputs: 模型输出样本列表
                （调用前需已通过 ModelDriftDetector.establish_baseline() 建立基线，
                 无基线时检测器返回 drift_detected=False）

        Returns:
            (drift_detected, divergence_score, raw_details)
        """
        if not model_outputs:
            return False, 0.0, {"skipped": "no model_outputs"}

        try:
            result = self._drift_detector.detect_drift(model_outputs)
        except Exception as exc:  # noqa: BLE001 — 检测器异常不阻断审计
            _logger.warning(
                "ModelDriftDetector failed: %s; treating as no drift",
                exc,
            )
            return False, 0.0, {"error": str(exc)}

        details = {
            "drift_detected": result.drift_detected,
            "divergence_score": result.divergence_score,
            "threshold": result.threshold,
            "exit_code": result.exit_code,
            "details": result.details,
        }
        _logger.debug(
            "Drift detection: drift=%s divergence=%.4f threshold=%.4f",
            result.drift_detected,
            result.divergence_score,
            result.threshold,
        )
        return result.drift_detected, float(result.divergence_score), details

    # ── IC 衰减分析 ──

    def _compute_ic_decay(
        self,
        ic_data: dict[int, float] | None,
    ) -> tuple[float, float, dict[str, Any]]:
        """计算 IC 衰减百分比与半衰期。

        Args:
            ic_data: {lag: ic_value} 预计算的 IC 衰减曲线（由调用方通过
                compute_ic_decay() 获得）

        Returns:
            (ic_decay_pct, ic_half_life, details)
            无 IC 数据时返回 (0.0, 0.0, {"skipped": ...})
        """
        if not ic_data:
            return 0.0, 0.0, {"skipped": "no ic_data"}

        # 延迟导入 pandas + compute_half_life（真源，避免重写插值逻辑）
        import pandas as pd

        ic_series = pd.Series(ic_data, name="ic_decay").sort_index()
        if ic_series.empty:
            return 0.0, 0.0, {"skipped": "empty ic_series"}

        initial_ic = abs(float(ic_series.iloc[0]))
        final_ic = abs(float(ic_series.iloc[-1]))

        if initial_ic < 1e-10:
            ic_decay_pct = 0.0
        else:
            ic_decay_pct = max(0.0, (initial_ic - final_ic) / initial_ic)

        try:
            from zephyr.factor.analysis.ic_decay import compute_half_life

            ic_half_life = compute_half_life(ic_series)
        except Exception as exc:  # noqa: BLE001
            _logger.warning("compute_half_life failed: %s", exc)
            ic_half_life = 0.0

        details = {
            "initial_ic": round(initial_ic, 6),
            "final_ic": round(final_ic, 6),
            "ic_decay_pct": round(ic_decay_pct, 4),
            "ic_half_life": round(float(ic_half_life), 4),
            "n_lags": len(ic_series),
        }
        _logger.debug(
            "IC decay: initial=%.6f final=%.6f decay_pct=%.4f half_life=%.4f",
            initial_ic,
            final_ic,
            ic_decay_pct,
            ic_half_life,
        )
        return float(ic_decay_pct), float(ic_half_life), details

    # ── 风险等级映射 ──

    def _compute_risk_level(
        self,
        drift_detected: bool,
        ic_decay_pct: float,
    ) -> str:
        """drift + ic_decay 双维度 → low/medium/high/critical。

        Matrix:
                       | ic_decay<0.3 | 0.3-0.5 | 0.5-0.7 | >=0.7 |
        | no drift     | low          | low     | medium  | high  |
        | drift        | medium       | medium  | high    | critical|

        Args:
            drift_detected: 是否检测到漂移
            ic_decay_pct: IC 衰减百分比

        Returns:
            risk_level 字符串 (low/medium/high/critical)
        """
        severe_decay = ic_decay_pct >= 0.7
        high_decay = 0.5 <= ic_decay_pct < 0.7

        if drift_detected:
            if severe_decay:
                return "critical"
            if high_decay:
                return "high"
            return "medium"
        else:
            if severe_decay:
                return "high"
            if high_decay:
                return "medium"
            return "low"

    # ── 综合审计 ──

    def audit(
        self,
        model_outputs: list[dict[str, Any]] | None = None,
        ic_data: dict[int, float] | None = None,
        bias_score: float | None = None,
    ) -> ModelRiskAuditReport:
        """综合审计模型风险。

        Args:
            model_outputs: 模型输出样本列表，供漂移检测
                （调用前需已通过 ModelDriftDetector.establish_baseline() 建立基线）
            ic_data: IC 衰减曲线 {lag: ic_value}（预计算，可选）
            bias_score: 预测偏差分数（可选，无则默认随 drift_detected）

        Returns:
            ModelRiskAuditReport 审计报告
        """
        drift_detected, divergence_score, drift_details = self._compute_drift(
            model_outputs,
        )
        ic_decay_pct, ic_half_life, ic_details = self._compute_ic_decay(
            ic_data,
        )

        # bias 判定：显式 bias_score 优先，否则随 drift
        if bias_score is not None:
            bias_detected = float(bias_score) > self._bias_threshold
            bias_details = {
                "bias_score": float(bias_score),
                "threshold": self._bias_threshold,
            }
        else:
            bias_detected = drift_detected
            bias_details = {"derived_from": "drift_detected", "value": drift_detected}

        risk_level = self._compute_risk_level(drift_detected, ic_decay_pct)

        report = ModelRiskAuditReport(
            drift_detected=drift_detected,
            divergence_score=round(divergence_score, 6),
            ic_half_life=round(ic_half_life, 4),
            ic_decay_pct=round(ic_decay_pct, 4),
            bias_detected=bias_detected,
            risk_level=risk_level,
            details={
                "drift": drift_details,
                "ic_decay": ic_details,
                "bias": bias_details,
                "drift_threshold": self._drift_threshold,
                "ic_decay_threshold": self._ic_decay_threshold,
            },
            timestamp=datetime.now(UTC),
            idempotency_key=f"modelrisk-{uuid.uuid4().hex[:8]}",
        )

        _logger.info(
            "Model risk audited: drift=%s divergence=%.4f ic_decay_pct=%.4f ic_half_life=%.4f bias=%s risk_level=%s",
            drift_detected,
            divergence_score,
            ic_decay_pct,
            ic_half_life,
            bias_detected,
            risk_level,
        )
        return report

    # ── 风控检查结果转换 ──

    def to_risk_check_result(
        self,
        report: ModelRiskAuditReport,
    ) -> RiskCheckResult:
        """将 ModelRiskAuditReport 转换为 RiskCheckResult（供编排器聚合）。

        severity 映射:
          - critical → HALT
          - high → HALT
          - medium → warning
          - low → info

        passed = (risk_level == "low")

        Args:
            report: 模型风险审计报告

        Returns:
            RiskCheckResult
        """
        severity_map = {
            "critical": "HALT",
            "high": "HALT",
            "medium": "warning",
            "low": "info",
        }
        severity = severity_map.get(report.risk_level, "info")
        passed = report.risk_level == "low"

        return RiskCheckResult(
            check_id=f"model-risk-{report.idempotency_key}",
            rule_name="model_risk_audit",
            passed=passed,
            limit_value=Decimal(str(self._drift_threshold)),
            actual_value=Decimal(str(report.divergence_score)),
            message=(
                f"risk_level={report.risk_level} "
                f"drift={report.drift_detected} "
                f"divergence={report.divergence_score:.4f} "
                f"ic_decay_pct={report.ic_decay_pct:.4f} "
                f"ic_half_life={report.ic_half_life:.4f} "
                f"bias={report.bias_detected}"
            ),
            severity=severity,
        )
