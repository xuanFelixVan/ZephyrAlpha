# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.quality.agent_quality
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.orchestrator.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_agent_quality | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""AI Agent 质量反馈闭环（CT-AGENT-QUALITY）——task完成质量评分+agent绩效追踪。"""


class AgentQualityTracker:
    def __init__(self):
        self._scores: dict[str, list[float]] = {}

    def record(self, agent_id: str, score: float) -> None:
        if agent_id not in self._scores:
            self._scores[agent_id] = []
        self._scores[agent_id].append(score)

    def average_score(self, agent_id: str) -> float:
        scores = self._scores.get(agent_id, [])
        return sum(scores) / len(scores) if scores else 0.0

    def should_escalate(self, agent_id: str) -> bool:
        return self.average_score(agent_id) < 0.6
