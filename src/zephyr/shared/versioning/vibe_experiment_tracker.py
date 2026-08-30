# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.versioning.vibe_experiment_tracker
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: vibe_experiment_tracker.py
# 层: 算法
# - id: A1
#   name_zh: ① VibeExperimentTracker
#   name_en: VibeExperimentTracker
#   intro: class VibeExperimentTracker 源码 L65-L83
#   desc: 公共方法（定义序）: start, record_outcome, get_by_session；源码 L65-L83
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: VibeExperimentTracker
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field


@dataclass
class ExperimentRecord:
    experiment_id: str
    session_id: str
    parameters: dict[str, str] = field(default_factory=dict)
    outcome: str = ""
    metrics: dict[str, float] = field(default_factory=dict)
    created_at: float = 0.0


class VibeExperimentTracker:
    def __init__(self):
        self._experiments: list[ExperimentRecord] = []

    def start(self, session_id: str, **parameters: str) -> ExperimentRecord:
        record = ExperimentRecord(str(uuid.uuid4())[:8], session_id, parameters, created_at=time.time())
        self._experiments.append(record)
        return record

    def record_outcome(self, experiment_id: str, outcome: str, **metrics: float) -> bool:
        for e in self._experiments:
            if e.experiment_id == experiment_id:
                e.outcome = outcome
                e.metrics.update(metrics)
                return True
        return False

    def get_by_session(self, session_id: str) -> list[ExperimentRecord]:
        return [e for e in self._experiments if e.session_id == session_id]
