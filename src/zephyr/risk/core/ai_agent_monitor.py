# [BLUEPRINT] MOD-RK-14 | docs/03_modules/_domain_risk/ai_agent_monitor/blueprint.md | §
# [MODULE] zephyr.risk.core.ai_agent_monitor
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.risk_manager_base; zephyr.feedback_loop.detectors.anomaly.emergent_behavior_detector; zephyr.feedback_loop.detectors.correlation.agent_trajectory_anomaly_detector; zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_behavior_fingerprint
# [CONSUMERS] MOD-L04-001(DefaultRiskManagerOrchestrator,AI/Agent风险评估)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] risk_score=0.4*emergence+0.3*trajectory+0.3*fingerprint;is_breached=risk_score>threshold OR emergence_state==CRITICAL;纯机制零参数
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidAiAgentInputError
# [TESTS] tests/risk/core/test_ai_agent_monitor.py
# [A_module] module_id=MOD-RK-14 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

D_RISK — AI/Agent Risk Monitor (MOD-RK-14)

AI/Agent 行为越界监控器——检测交易 Agent 的 ASI/AST/MCP 隐性串谋
和自治边界违反。

组装缺口（非从零实现）：检测能力散落于 D_FBL_DETECTORS / D_SECURITY /
D_AUTONOMY_CORE，本模块将其**组装+聚焦**为 risk/core/ 内面向交易 Agent
的越界监控。

核心公式 (blueprint §3):
  emergence_score: 来自 EmergentBehaviorDetector 状态映射
    STABLE=0.0, CORRELATING=0.5, HYSTERETIC=0.7, CRITICAL=1.0
  trajectory_score: 轨迹异常数量归一化 min(anomalies/5, 1.0)
  fingerprint_score: 行为指纹偏差 [0, 1]
  risk_score = 0.4 × emergence_score + 0.3 × trajectory_score + 0.3 × fingerprint_score
  is_breached = risk_score > threshold(默认0.6) 或 emergence_state == CRITICAL

日志埋点:
  - INFO: 评估完成（emergence + trajectory + fingerprint + risk_score + is_breached）
  - WARNING: 输入数据不足跳过
  - DEBUG: 逐检测器原始输出

SSoT: depgraph MOD-RK-14 | blueprint.md §3 核心规则

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Agent行为指标 字典数据
#   fields: {metric_name: value}如agent_a_latency, 供涌现检测器累积metric_history(≥5点才出相关性)
#   code: assess() agent_metrics L210
# - id: I2
#   name: 轨迹异常数量 整数
#   fields: 预计算轨迹异常数(调用方经AgentTrajectoryAnomalyDetector.detect_trajectory_anomalies获得)
#   code: assess() trajectory_anomaly_count L211
# - id: I3
#   name: 行为指纹偏差 浮点数
#   fields: 预计算偏差[0,1](A2ABehaviorFingerprint.compare相似度取1-similarity)
#   code: assess() fingerprint_deviation L212
# - id: I4
#   name: 阈值参数 配置
#   fields: risk_threshold默认0.6(>则越界) + correlation_threshold默认0.70(高相关对判定)
#   code: __init__() L124-127
# 层: 特征
# - id: F1
#   name_zh: 涌现行为评分
#   name_en: emergence_score
#   intro: 把涌现检测器的状态映射成0~1分
#   formula: STABLE=0.0/CORRELATING=0.5/HYSTERETIC=0.7/CRITICAL=1.0 状态映射查表
#   code: ai_agent_monitor.py L65-70 + L234
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F2
#   name_zh: 轨迹异常评分
#   name_en: trajectory_score
#   intro: 轨迹异常个数按5个封顶归一化到0~1
#   formula: min(anomaly_count/5.0, 1.0)
#   code: ai_agent_monitor.py L235
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F3
#   name_zh: 指纹偏差评分
#   name_en: fingerprint_score
#   intro: 行为指纹偏差截断到[0,1]直接用
#   formula: clamp(float(fingerprint_deviation), 0.0, 1.0); None→0.0
#   code: ai_agent_monitor.py L203 + L236
#   registry: factor_registry: 无FCT条目
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① 多检测器组装综合评分
#   name_en: AiAgentMonitor.assess
#   intro: 组装涌现检测器加轨迹指纹三路评分, 0.4/0.3/0.3加权算综合风险分并判越界
#   desc: __init__创建有状态EmergentBehaviorDetector跨调用复用; record_metrics→detect_emergence得state; risk_score=0.4×emergence+0.3×trajectory+0.3×fingerprint; is_breached=risk>threshold OR state==CRITICAL
#   inputs: I1 I2 I3 I4 F1 F2 F3
#   outputs: AiAgentRiskMetrics快照
#   invariant: risk_score=0.4×emergence+0.3×trajectory+0.3×fingerprint
# - id: A2
#   name_zh: ② 风控检查结果转换
#   name_en: to_risk_check_result
#   intro: 把风险快照转成编排器可聚合的RiskCheckResult
#   desc: passed=!is_breached; limit=0.6; actual=risk_score; severity越界=HALT否则info
#   inputs: A1
#   outputs: RiskCheckResult
# 层: 输出
# - id: O1
#   name_zh: AI/Agent风险快照
#   name_en: AiAgentRiskMetrics
#   intro: 含涌现状态/高相关对数/异常数/指纹偏差/综合风险分/越界标志的不可变快照
#   invariant: risk_score∈[0,1]保留4位小数
#   downstream: DefaultRiskManagerOrchestrator MOD-L04-001(AI/Agent风险评估)
# - id: O2
#   name_zh: 风控检查结果
#   name_en: RiskCheckResult
#   intro: 供风控编排器统一聚合的AI/Agent风险检查结果
#   downstream: DefaultRiskManagerOrchestrator MOD-L04-001
# [/ALGO_FLOW]
#
# 边:
# I1 -.->|断点| F1
# I2 -.->|断点| F2
# I3 -.->|断点| F3
# F1 --> A1
# F2 --> A1
# F3 --> A1
# I4 --> A1
# A1 --> O1
# A1 --> A2
# A2 --> O2
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from zephyr.risk.risk_manager_base import RiskCheckResult

_logger = logging.getLogger(__name__)

__all__ = [
    "AiAgentRiskMetrics",
    "AiAgentMonitor",
    "InvalidAiAgentInputError",
]

#: 综合 risk_score 阈值（默认 0.6，>此值判定为越界）
DEFAULT_RISK_THRESHOLD: float = 0.6

#: EmergenceState → emergence_score 映射
_EMERGENCE_SCORE_MAP: dict[str, float] = {
    "STABLE": 0.0,
    "CORRELATING": 0.5,
    "HYSTERETIC": 0.7,
    "CRITICAL": 1.0,
}


class InvalidAiAgentInputError(ValueError):
    """AI/Agent 风险监控输入数据无效。"""


# ── 数据模型 ──────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AiAgentRiskMetrics:
    """AI/Agent 行为风险快照（不可变）。

    Attributes:
        emergence_state: 涌现行为状态 STABLE/CORRELATING/CRITICAL/HYSTERETIC
        high_correlation_pairs: 高相关 Agent 对数
        trajectory_anomalies: 轨迹异常数量
        fingerprint_deviation: 行为指纹偏差 [0, 1]
        risk_score: 综合风险评分 [0, 1]
        is_breached: 是否越界
        details: 原始检测器输出
        timestamp: 评估时间（UTC）
        idempotency_key: 幂等键
    """

    emergence_state: str
    high_correlation_pairs: int
    trajectory_anomalies: int
    fingerprint_deviation: float
    risk_score: float
    is_breached: bool
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    idempotency_key: str = ""


# ── AI/Agent 风险监控器 ──────────────────────────────────────────────


class AiAgentMonitor:
    """AI/Agent 行为越界监控器——组装多检测器的综合风险评估。

    纯机制零参数：阈值使用行业标准默认值，组装现有检测器不重新实现。

    Usage:
        mon = AiAgentMonitor()
        metrics = mon.assess(
            agent_metrics={"agent_a_latency": 0.8, "agent_b_latency": 0.9},
            trajectory_anomaly_count=2,
            fingerprint_deviation=0.7,
        )
    """

    def __init__(
        self,
        risk_threshold: float = DEFAULT_RISK_THRESHOLD,
        correlation_threshold: float = 0.70,
    ):
        self._risk_threshold = risk_threshold
        self._correlation_threshold = correlation_threshold
        # EmergentBehaviorDetector 是有状态的（累积 metric_history），
        # 必须在 __init__ 创建并跨 assess() 调用复用，否则单次调用
        # 仅记录 1 个数据点，永远无法达到计算相关性所需的 ≥5 点。
        from zephyr.feedback_loop.detectors.anomaly.emergent_behavior_detector import (
            EmergentBehaviorDetector,
        )

        self._emergence_detector = EmergentBehaviorDetector(
            correlation_threshold=self._correlation_threshold,
        )

    # ── 涌现行为评分 ──

    def _compute_emergence(
        self,
        agent_metrics: dict[str, float] | None,
    ) -> tuple[str, int, dict[str, Any]]:
        """运行 EmergentBehaviorDetector 计算涌现行为评分。

        Returns:
            (emergence_state, high_correlation_pairs, raw_details)
        """
        if not agent_metrics:
            return "STABLE", 0, {"skipped": "no agent_metrics"}

        self._emergence_detector.record_metrics(agent_metrics)
        result = self._emergence_detector.detect_emergence()

        state = result.get("state", "STABLE")
        high_corr = result.get("high_correlation_pairs", 0)

        _logger.debug(
            "Emergence detection: state=%s high_corr=%d details=%s",
            state,
            high_corr,
            result,
        )
        return state, high_corr, result

    # ── 轨迹异常评分 ──

    def _compute_trajectory(
        self,
        trajectory_anomaly_count: int,
    ) -> tuple[int, dict[str, Any]]:
        """计算轨迹异常评分。

        Args:
            trajectory_anomaly_count: 预计算的轨迹异常数量（由调用方通过
                AgentTrajectoryAnomalyDetector.detect_trajectory_anomalies() 获得）

        Returns:
            (anomaly_count, details)
        """
        return trajectory_anomaly_count, {"anomaly_count": trajectory_anomaly_count}

    # ── 行为指纹偏差评分 ──

    def _compute_fingerprint(
        self,
        fingerprint_deviation: float | None,
    ) -> tuple[float, dict[str, Any]]:
        """计算行为指纹偏差评分。

        Args:
            fingerprint_deviation: 预计算的偏差值 [0, 1]（由调用方通过
                A2ABehaviorFingerprint.compare() 获得相似度后取 1-similarity）

        Returns:
            (deviation_score, details)
        """
        if fingerprint_deviation is None:
            return 0.0, {"skipped": "no fingerprint data"}

        deviation = max(0.0, min(1.0, float(fingerprint_deviation)))
        return deviation, {"deviation": deviation}

    # ── 综合评估 ──

    def assess(
        self,
        agent_metrics: dict[str, float] | None = None,
        trajectory_anomaly_count: int = 0,
        fingerprint_deviation: float | None = None,
    ) -> AiAgentRiskMetrics:
        """综合评估 AI/Agent 行为风险。

        Args:
            agent_metrics: Agent 行为指标 {metric_name: value}，供涌现检测
            trajectory_anomaly_count: 轨迹异常数量（预计算）
            fingerprint_deviation: 行为指纹偏差 [0, 1]（预计算）

        Returns:
            AiAgentRiskMetrics 风险快照
        """
        emergence_state, high_corr, emergence_details = self._compute_emergence(
            agent_metrics,
        )
        anomaly_count, trajectory_details = self._compute_trajectory(
            trajectory_anomaly_count,
        )
        fp_deviation, fingerprint_details = self._compute_fingerprint(
            fingerprint_deviation,
        )

        emergence_score = _EMERGENCE_SCORE_MAP.get(emergence_state, 0.0)
        trajectory_score = min(anomaly_count / 5.0, 1.0)
        fingerprint_score = fp_deviation

        risk_score = 0.4 * emergence_score + 0.3 * trajectory_score + 0.3 * fingerprint_score
        is_breached = risk_score > self._risk_threshold or emergence_state == "CRITICAL"

        metrics = AiAgentRiskMetrics(
            emergence_state=emergence_state,
            high_correlation_pairs=high_corr,
            trajectory_anomalies=anomaly_count,
            fingerprint_deviation=round(fp_deviation, 4),
            risk_score=round(risk_score, 4),
            is_breached=is_breached,
            details={
                "emergence": emergence_details,
                "trajectory": trajectory_details,
                "fingerprint": fingerprint_details,
                "emergence_score": emergence_score,
                "trajectory_score": round(trajectory_score, 4),
                "fingerprint_score": round(fingerprint_score, 4),
            },
            timestamp=datetime.now(UTC),
            idempotency_key=f"aiagent-{uuid.uuid4().hex[:8]}",
        )

        _logger.info(
            "AiAgent risk assessed: emergence=%s high_corr=%d anomalies=%d fp_dev=%.4f risk=%.4f breached=%s",
            emergence_state,
            high_corr,
            anomaly_count,
            fp_deviation,
            risk_score,
            is_breached,
        )
        return metrics

    # ── 风控检查结果转换 ──

    def to_risk_check_result(
        self,
        metrics: AiAgentRiskMetrics,
    ) -> RiskCheckResult:
        """将 AiAgentRiskMetrics 转换为 RiskCheckResult（供编排器聚合）。

        Args:
            metrics: AI/Agent 风险指标

        Returns:
            RiskCheckResult（passed=!is_breached, severity=HALT/warning/info）
        """
        return RiskCheckResult(
            check_id=f"ai-agent-{metrics.idempotency_key}",
            rule_name="ai_agent_monitor",
            passed=not metrics.is_breached,
            limit_value=Decimal(str(DEFAULT_RISK_THRESHOLD)),
            actual_value=Decimal(str(metrics.risk_score)),
            message=(
                f"risk_score={metrics.risk_score:.4f} "
                f"emergence={metrics.emergence_state} "
                f"anomalies={metrics.trajectory_anomalies} "
                f"fp_dev={metrics.fingerprint_deviation:.4f}"
            ),
            severity="HALT" if metrics.is_breached else "info",
        )


# 延迟导入 Decimal（避免在模块级别引入 decimal 的开销，仅在 to_risk_check_result 中使用）
from decimal import Decimal  # noqa: E402
