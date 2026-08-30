# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.quality.agent_quality
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
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
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
AI Agent 质量反馈闭环（CT-AGENT-QUALITY）——task完成质量评分+agent绩效追踪。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: agent_quality.py
# 层: 算法
# - id: A1
#   name_zh: ① AgentQualityTracker
#   name_en: AgentQualityTracker
#   intro: class AgentQualityTracker 源码 L49-L63
#   desc: 公共方法（定义序）: record, average_score, should_escalate；源码 L49-L63
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: AgentQualityTracker
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


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
