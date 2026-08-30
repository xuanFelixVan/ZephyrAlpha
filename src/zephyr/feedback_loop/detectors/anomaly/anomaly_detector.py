# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.anomaly.anomaly_detector
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] zephyr.feedback_loop.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: anomaly_detector.py
# 层: 算法
# - id: A1
#   name_zh: ① AnomalyDetector
#   name_en: AnomalyDetector
#   intro: class AnomalyDetector 源码 L66-L103
#   desc: 公共方法（定义序）: detect；源码 L66-L103
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: AnomalyDetector
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import uuid
from dataclasses import dataclass
from typing import Any

from zephyr.feedback_loop.collectors.feedback_collector import FeedbackCollector
from zephyr.feedback_loop.collectors.metrics_collector import MetricsCollector, MetricSnapshot
from zephyr.feedback_loop.protocols import ActionType, FeedbackProtocolAdapter


@dataclass
class AnomalyEvent:
    anomaly_id: str
    severity: int
    evidence: dict[str, Any]
    timestamp: float


@dataclass
class AnomalyDetector:
    metrics_collector: MetricsCollector
    feedback_collector: FeedbackCollector
    protocol_adapter: FeedbackProtocolAdapter | None = None
    z_threshold: float = 2.5
    max_detect_seconds: float = 300.0

    def detect(self, snapshot: MetricSnapshot) -> AnomalyEvent | None:
        result = self.metrics_collector.collect(snapshot)
        if not result["anomaly_triggered"]:
            return None
        triggered_metrics = {k: v for k, v in result["z_scores"].items() if abs(v) > self.z_threshold}
        # 5.106.2 修复: z_threshold 与类常量 Z_THRESHOLD 分叉时 triggered_metrics 可能为空,
        # max() 抛 ValueError。公开方法需空集保护。
        if not triggered_metrics:
            return None
        max_z_metric = max(triggered_metrics, key=lambda k: abs(triggered_metrics[k]))
        severity = min(int(abs(triggered_metrics[max_z_metric]) * 2), 10)
        anomaly_id = str(uuid.uuid4())[:8]
        evidence = {
            "metric_name": max_z_metric,
            "value": getattr(snapshot, max_z_metric),
            "z_score": triggered_metrics[max_z_metric],
            "baseline_ema": getattr(self.metrics_collector.baseline, f"{max_z_metric}_ema", 0.0),
            "repair_failure_rate": self.feedback_collector.repair_failure_rate(),
        }
        event = AnomalyEvent(
            anomaly_id=anomaly_id,
            severity=severity,
            evidence=evidence,
            timestamp=snapshot.timestamp,
        )
        if self.protocol_adapter is not None and severity > 0:
            self.protocol_adapter.dispatch_action(
                ActionType.NOTIFY_OWNER,
                {"anomaly_id": anomaly_id, "severity": severity, "evidence": evidence},
            )
        return event
