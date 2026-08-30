# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_knowledge_distill
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
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
A2A 知识蒸馏 — 跨 Agent 经验提炼与共享

当一个 Agent 完成任务后, 提取其经验/教训/决策模式:
  1. 从 Session Log + Task Card + Blueprint 中提取关键信息
  2. 压缩为 2-3 行的 distilled_insight
  3. 写入 Knowledge Base (KB) 供后续 Agent 消费

输出: DistilledKnowledge — KB-able key-value 结构

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: max_insights_per_agent 参数
#   fields: 参数 max_insights_per_agent（无注解）
#   code: a2a_knowledge_distill.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① A2AKnowledgeDistill
#   name_en: A2AKnowledgeDistill
#   intro: class A2AKnowledgeDistill 源码 L70-L106
#   desc: 公共方法（定义序）: distill, get_insights；源码 L70-L106
#   inputs: max_insights_per_agent
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: A2AKnowledgeDistill
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DistilledKnowledge:
    source_agent: str
    topic: str
    insight: str
    category: str = "learning"
    compressed: bool = True


class A2AKnowledgeDistill:
    def __init__(self, max_insights_per_agent: int = 20):
        self._max_insights = max_insights_per_agent
        self._insights: dict[str, list[DistilledKnowledge]] = {}

    def distill(
        self,
        agent_id: str,
        topic: str,
        raw_notes: str,
        category: str = "learning",
    ) -> DistilledKnowledge:
        insight = self._compress(raw_notes, topic)
        dk = DistilledKnowledge(
            source_agent=agent_id,
            topic=topic,
            insight=insight,
            category=category,
        )
        if agent_id not in self._insights:
            self._insights[agent_id] = []
        self._insights[agent_id].append(dk)

        if len(self._insights[agent_id]) > self._max_insights:
            self._insights[agent_id] = self._insights[agent_id][-self._max_insights :]

        return dk

    def get_insights(self, agent_id: str) -> list[DistilledKnowledge]:
        return self._insights.get(agent_id, [])

    def _compress(self, raw: str, topic: str) -> str:
        lines = raw.strip().split("\n")
        if len(lines) <= 3:
            return raw.strip()[:200]
        summary_lines = lines[:2]
        return f"[{topic}] {' '.join(l.strip() for l in summary_lines if l.strip())[:180]}..."
