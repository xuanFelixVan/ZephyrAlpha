# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] zephyr.security.access_control.detectors.anomaly_detector
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests.agent_rbac.test_crosscut_d
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
AnomalyDetector - rolling z-score anomaly detection per field.

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
#   intro: Rolling z-score based anomaly detector.
#   desc: Rolling z-score based anomaly detector. 治本(2026-07-19): 实现 feed() 以匹配 tests/agent_rbac/te…；公共方法（定义序）: feed；源码…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: AnomalyDetector
#   downstream: tests.agent_rbac.test_crosscut_d
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean, pstdev


@dataclass
class AnomalyScore:
    anomalous: bool = False
    z_score: float = 0.0


class AnomalyDetector:
    """Rolling z-score based anomaly detector.

    治本(2026-07-19): 实现 feed() 以匹配 tests/agent_rbac/test_crosscut_d.py 契约.
    每个字段维护独立的历史窗口, z-score 超过阈值(3.0)判定为异常.
    """

    THRESHOLD: float = 3.0
    MIN_SAMPLES: int = 2

    def __init__(self) -> None:
        self._history: dict[str, list[float]] = {}

    def feed(self, field_name: str, value: float) -> AnomalyScore:
        history = self._history.setdefault(field_name, [])
        z_score = 0.0
        anomalous = False
        if len(history) >= self.MIN_SAMPLES:
            mu = mean(history)
            sigma = pstdev(history) if len(history) > 1 else 0.0
            if sigma > 0:
                z_score = abs(value - mu) / sigma
                anomalous = z_score > self.THRESHOLD
            elif value != mu:
                z_score = float("inf")
                anomalous = z_score > self.THRESHOLD
        history.append(value)
        return AnomalyScore(anomalous=anomalous, z_score=z_score)


__all__ = ["AnomalyDetector", "AnomalyScore"]
