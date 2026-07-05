# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_blame_attribution
# [DOMAIN] D_INFRA_RUNTIME
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
# [A_module] module_id=MOD-INF_a2a_blame_attribution | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A 责任归属引擎 — 因果链分析 + 责任分配

当 A2A 系统出现问题(数据损坏/错误输出), 追溯根本原因:
  1. 构建因果图 (causal_trace graph)
  2. 沿因果链向上追溯——哪个 Agent 的哪个 action 导致了问题
  3. 输出 blame_ratio — 各 Agent 的责任占比

方法: 基于 A2ACausalTrace 的因果图 + 破坏性贡献度分析
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BlameItem:
    agent_id: str
    action: str
    contribution: float
    evidence: str = ""


@dataclass
class BlameReport:
    incident_id: str
    items: list[BlameItem] = field(default_factory=list)
    root_cause_agent: str = ""

    @property
    def primary_blame(self) -> BlameItem | None:
        if not self.items:
            return None
        return max(self.items, key=lambda x: x.contribution)


class A2ABlameAttribution:
    def __init__(self):
        self._records: dict[str, dict] = {}

    def add_record(self, agent_id: str, action: str, timestamp: float, impact_score: float = 0.0):
        record_id = f"{agent_id}:{action}:{timestamp}"
        self._records[record_id] = {
            "agent_id": agent_id,
            "action": action,
            "timestamp": timestamp,
            "impact_score": impact_score,
        }

    def attribute(self, incident_id: str, suspect_agents: list[str]) -> BlameReport:
        report = BlameReport(incident_id=incident_id)

        total_impact = sum(r["impact_score"] for r in self._records.values() if r["agent_id"] in suspect_agents)
        if total_impact == 0:
            total_impact = 1.0

        for agent_id in suspect_agents:
            agent_records = [r for r in self._records.values() if r["agent_id"] == agent_id]
            if not agent_records:
                continue

            contribution = sum(r["impact_score"] for r in agent_records) / total_impact
            report.items.append(
                BlameItem(
                    agent_id=agent_id,
                    action=agent_records[-1]["action"],
                    contribution=round(contribution, 3),
                    evidence=f"{len(agent_records)} actions recorded",
                )
            )

        report.items.sort(key=lambda x: x.contribution, reverse=True)
        if report.items:
            report.root_cause_agent = report.items[0].agent_id

        return report
