# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_behavior_fingerprint
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_a2a_behavior_fingerprint | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A 行为指纹 — Agent 行为模式学习与画像

记录每个 Agent 的操作历史, 建立行为指纹:
  - action_distribution: action 名称 -> 频率分布
  - file_touch_pattern: 哪些文件被修改过
  - avg_session_duration: 平均作业时长
  - inter_agent_interaction_rate: 与其他 Agent 的通信频率

当 Agent 行为偏离其历史指纹时 -> 触发 A2AAnomalyDetector
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BehaviorFingerprint:
    agent_id: str
    action_counts: dict[str, int] = field(default_factory=dict)
    files_touched: set[str] = field(default_factory=set)
    session_count: int = 0
    total_session_seconds: float = 0.0
    interactions: dict[str, int] = field(default_factory=dict)

    def similarity(self, other: BehaviorFingerprint) -> float:
        actions_a = set(self.action_counts.keys())
        actions_b = set(other.action_counts.keys())
        if not actions_a or not actions_b:
            return 0.0
        overlap = len(actions_a & actions_b)
        union = len(actions_a | actions_b)
        return overlap / union if union > 0 else 0.0

    @property
    def top_actions(self, n: int = 5) -> list[tuple[str, int]]:
        return sorted(self.action_counts.items(), key=lambda x: x[1], reverse=True)[:n]

    @property
    def avg_session_seconds(self) -> float:
        if self.session_count == 0:
            return 0.0
        return self.total_session_seconds / self.session_count


class A2ABehaviorFingerprint:
    def __init__(self):
        self._fingerprints: dict[str, BehaviorFingerprint] = {}

    def record_action(self, agent_id: str, action: str):
        if agent_id not in self._fingerprints:
            self._fingerprints[agent_id] = BehaviorFingerprint(agent_id=agent_id)
        fp = self._fingerprints[agent_id]
        fp.action_counts[action] = fp.action_counts.get(action, 0) + 1

    def record_file_touch(self, agent_id: str, file_path: str):
        if agent_id not in self._fingerprints:
            self._fingerprints[agent_id] = BehaviorFingerprint(agent_id=agent_id)
        self._fingerprints[agent_id].files_touched.add(file_path)

    def record_session(self, agent_id: str, duration_seconds: float):
        if agent_id not in self._fingerprints:
            self._fingerprints[agent_id] = BehaviorFingerprint(agent_id=agent_id)
        fp = self._fingerprints[agent_id]
        fp.session_count += 1
        fp.total_session_seconds += duration_seconds

    def record_interaction(self, agent_id: str, other_agent: str):
        if agent_id not in self._fingerprints:
            self._fingerprints[agent_id] = BehaviorFingerprint(agent_id=agent_id)
        fp = self._fingerprints[agent_id]
        fp.interactions[other_agent] = fp.interactions.get(other_agent, 0) + 1

    def get_fingerprint(self, agent_id: str) -> BehaviorFingerprint:
        return self._fingerprints.get(agent_id, BehaviorFingerprint(agent_id=agent_id))

    def compare(self, agent_a: str, agent_b: str) -> float:
        fp_a = self._fingerprints.get(agent_a)
        fp_b = self._fingerprints.get(agent_b)
        if fp_a is None or fp_b is None:
            return 0.0
        return fp_a.similarity(fp_b)
