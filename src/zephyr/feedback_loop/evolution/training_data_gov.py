# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.evolution.training_data_gov
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
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
Training Data Governance — v0.14.0 R191

Blindspot: Training data unversioned; distribution drift invisible to model training.
Risk: R191 — Model trained on drifted data; silent accuracy degradation.

Mitigation: Training data version snapshots with distribution drift detection.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: training_data_gov.py
# 层: 算法
# - id: A1
#   name_zh: ① TrainingDataGov
#   name_en: TrainingDataGov
#   intro: class TrainingDataGov 源码 L71-L92
#   desc: 公共方法（定义序）: snapshot, detect_drift；源码 L71-L92
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: TrainingDataGov
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field


@dataclass
class DataSnapshot:
    snapshot_id: str
    timestamp: float
    row_count: int
    feature_count: int
    distribution_hash: str


@dataclass
class TrainingDataGov:
    snapshots: list[DataSnapshot] = field(default_factory=list)
    drift_threshold: float = 0.05

    def snapshot(self, data_checksum: str, rows: int, features: int) -> DataSnapshot:
        snap = DataSnapshot(
            snapshot_id=hashlib.md5(data_checksum.encode()).hexdigest()[:8],
            timestamp=time.time(),
            row_count=rows,
            feature_count=features,
            distribution_hash=hashlib.sha256(data_checksum.encode()).hexdigest()[:16],
        )
        self.snapshots.append(snap)
        return snap

    def detect_drift(self) -> float:
        if len(self.snapshots) < 2:
            return 0.0
        prev = self.snapshots[-2]
        curr = self.snapshots[-1]
        rows_change = abs(curr.row_count - prev.row_count) / max(prev.row_count, 1)
        return rows_change
