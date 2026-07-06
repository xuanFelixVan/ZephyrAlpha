# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_dashboard
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
# [A_module] module_id=MOD-INF_a2a_dashboard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A 监控仪表盘 — Agent 集群运行状态可视化面板

实时展示:
  - Agent 负载: 每个 Agent 当前 task 数量 + 队列深度
  - 冲突数: 过去 N 分钟的冲突检测数量
  - 异常数: 过去 N 分钟的统计异常数量
  - 安全事件: 被安全扫描器拦截的消息数量
  - 桥接状态: RBAC/Audit/Escalation 三向桥接健康

输出: DashboardPanel — 可渲染为文本/JSON/MCP 的监控视图
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DashboardPanel:
    timestamp: float
    agents: dict[str, dict]
    conflicts: dict
    anomalies: dict
    security: dict
    bridge_status: dict

    def render(self) -> str:
        lines = [
            "=" * 60,
            "  A2A Protocol Dashboard",
            "=" * 60,
            "",
            "--- Agents ---",
        ]
        for aid, info in self.agents.items():
            lines.append(f"  {aid}: load={info.get('load', 0)}, role={info.get('role', 'unknown')}")

        lines.extend(["", "--- Conflicts ---"])
        lines.append(f"  total={self.conflicts.get('total', 0)}, blocking={self.conflicts.get('blocking', 0)}")

        lines.extend(["", "--- Anomalies ---"])
        lines.append(f"  total={self.anomalies.get('total', 0)}, by_level={self.anomalies.get('by_level', {})}")

        lines.extend(["", "--- Security ---"])
        lines.append(f"  blocked={self.security.get('blocked', 0)}, suspicious={self.security.get('suspicious', 0)}")

        lines.extend(["", "--- Bridges ---"])
        for bridge, status in self.bridge_status.items():
            lines.append(f"  {bridge}: {status}")

        lines.extend(["", "=" * 60])
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "agents": self.agents,
            "conflicts": self.conflicts,
            "anomalies": self.anomalies,
            "security": self.security,
            "bridge_status": self.bridge_status,
        }


class A2ADashboard:
    def __init__(self):
        self._agent_info: dict[str, dict] = {}
        self._conflict_stats: dict = {}
        self._anomaly_stats: dict = {}
        self._security_stats: dict = {}
        self._bridge_status: dict = {}

    def update_agent(self, agent_id: str, load: int, role: str = "builder"):
        self._agent_info[agent_id] = {"load": load, "role": role}

    def update_conflicts(self, stats: dict):
        self._conflict_stats = stats

    def update_anomalies(self, stats: dict):
        self._anomaly_stats = stats

    def update_security(self, stats: dict):
        self._security_stats = stats

    def update_bridge(self, bridge_name: str, status: str):
        self._bridge_status[bridge_name] = status

    def snapshot(self) -> DashboardPanel:
        import time as _time

        return DashboardPanel(
            timestamp=_time.time(),
            agents=dict(self._agent_info),
            conflicts=dict(self._conflict_stats),
            anomalies=dict(self._anomaly_stats),
            security=dict(self._security_stats),
            bridge_status=dict(self._bridge_status),
        )
