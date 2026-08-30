# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.guard.temporal_coherence_of_self_model
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
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
R525: TemporalCoherenceOfSelfModel
FLE自模型跨时间一致性校验 — 昨天的自模型和今天矛盾？

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: temporal_coherence_of_self_model.py
# 层: 算法
# - id: A1
#   name_zh: ① TemporalCoherenceOfSelfModel
#   name_en: TemporalCoherenceOfSelfModel
#   intro: class TemporalCoherenceOfSelfModel 源码 L66-L134
#   desc: 公共方法（定义序）: compute_dict_similarity, record_snapshot, check_coherence；源码 L66-L134
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: TemporalCoherenceOfSelfModel
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import hashlib
import json
import time
from dataclasses import dataclass, field


@dataclass
class SelfModelSnapshot:
    timestamp: float
    capabilities: dict[str, float]
    limits: dict[str, float]
    health_score: float
    hash: str = ""


@dataclass
class TemporalCoherenceOfSelfModel:
    snapshots: list[SelfModelSnapshot] = field(default_factory=list)

    @staticmethod
    def compute_dict_similarity(a: dict[str, float], b: dict[str, float]) -> float:
        keys = set(a.keys()) | set(b.keys())
        if not keys:
            return 1.0
        diffs = [abs(a.get(k, 0.0) - b.get(k, 0.0)) / max(abs(a.get(k, 0.0)), abs(b.get(k, 0.0)), 1e-06) for k in keys]
        return 1.0 - sum(diffs) / len(keys)

    max_snapshots: int = 30
    coherence_threshold: float = 0.7

    def record_snapshot(self, capabilities: dict[str, float], limits: dict[str, float], health_score: float) -> str:
        content = json.dumps({"capabilities": capabilities, "limits": limits}, sort_keys=True)
        h = hashlib.sha256(content.encode()).hexdigest()[:16]

        snapshot = SelfModelSnapshot(
            timestamp=time.time(),
            capabilities=capabilities,
            limits=limits,
            health_score=health_score,
            hash=h,
        )
        self.snapshots.append(snapshot)
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots = self.snapshots[-self.max_snapshots :]
        return h

    def check_coherence(self) -> dict:
        if len(self.snapshots) < 2:
            return {"status": "insufficient_data", "coherence_score": 1.0}

        latest = self.snapshots[-1]
        previous = self.snapshots[-2]

        cap_diff = self._compute_dict_similarity(latest.capabilities, previous.capabilities)
        limit_diff = self._compute_dict_similarity(latest.limits, previous.limits)
        health_diff = 1.0 - abs(latest.health_score - previous.health_score)

        coherence = (cap_diff + limit_diff + health_diff) / 3.0

        inconsistencies = []
        if cap_diff < self.coherence_threshold:
            inconsistencies.append("capability_drift")
        if limit_diff < self.coherence_threshold:
            inconsistencies.append("limit_drift")
        if health_diff < self.coherence_threshold:
            inconsistencies.append("health_score_jump")

        severity = "normal"
        if len(inconsistencies) >= 2:
            severity = "critical"
        elif len(inconsistencies) == 1:
            severity = "warning"

        return {
            "status": severity,
            "coherence_score": round(coherence, 3),
            "inconsistencies": inconsistencies,
            "previous_hash": previous.hash,
            "current_hash": latest.hash,
        }

    @staticmethod
    def _compute_dict_similarity(a: dict[str, float], b: dict[str, float]) -> float:
        """向后兼容 thin wrapper（Stage 4 公共化，反向层级）。"""
        return TemporalCoherenceOfSelfModel.compute_dict_similarity(a, b)
