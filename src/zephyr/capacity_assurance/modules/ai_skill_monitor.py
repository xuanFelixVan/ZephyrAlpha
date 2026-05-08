"""
AI Skill Monitor — AI 技能退化检测 (盲点 #23, M-28)
四维检测器：
  1. 精确度退化 (accuracy_drift)
  2. 鲁棒性退化 (robustness_drift)
  3. 效率退化 (efficiency_drift)
  4. 格式遵守度退化 (format_compliance_drift)

当任一维度低于 AISG baseline 50% 时触发 SRA-1 告警
"""
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class SkillDimension(Enum):
    ACCURACY = "accuracy"
    ROBUSTNESS = "robustness"
    EFFICIENCY = "efficiency"
    FORMAT_COMPLIANCE = "format_compliance"


@dataclass
class SkillBaseline:
    dimension: SkillDimension
    baseline_score: float
    current_score: float
    degraded: bool = False
    last_checked: float = field(default_factory=time.time)


class AISkillMonitor:
    """
    AI 技能退化监测器 (M-28, 盲点 #23)
    """

    DEGRADATION_THRESHOLD = 0.5

    def __init__(self):
        self.baselines = {
            dim: SkillBaseline(dimension=dim, baseline_score=1.0, current_score=1.0)
            for dim in SkillDimension
        }

    def record(self, dimension: SkillDimension, task_id: str,
               expected: Any, actual: Any) -> dict:
        baseline = self.baselines[dimension]
        score = self._compare(expected, actual)
        baseline.current_score = score
        baseline.last_checked = time.time()
        baseline.degraded = score < self.DEGRADATION_THRESHOLD

        return {
            "dimension": dimension.value,
            "score": score,
            "degraded": baseline.degraded,
            "task_id": task_id,
        }

    def _compare(self, expected: Any, actual: Any) -> float:
        if expected == actual:
            return 1.0
        if isinstance(expected, str) and isinstance(actual, str):
            common = sum(1 for a, b in zip(expected, actual) if a == b)
            return common / max(len(expected), len(actual), 1)
        return 0.0

    def check_all(self) -> dict[str, dict]:
        return {
            dim.value: {
                "baseline_score": b.baseline_score,
                "current_score": b.current_score,
                "degraded": b.degraded,
            }
            for dim, b in self.baselines.items()
        }
