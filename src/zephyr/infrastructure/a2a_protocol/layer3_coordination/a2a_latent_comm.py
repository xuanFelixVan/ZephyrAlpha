# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_latent_comm
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
# [A_module] module_id=MOD-INF_a2a_latent_comm | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A 隐性通信检测 — 检测 Agent 通过副作用隐式通信

检测 Agent 是否通过非消息通道隐式传递信息:
  模式1: 文件系统副作用 — Agent A 写文件, Agent B 读文件, 内容含隐式指
  模式2: 时间通道 — 通过操作时间间隔编码信息
  模式3: 存储共享 — 通过 DB 表/KV 存储共享状态

方法: 分析 Agent 间没有显式 A2A 消息但访问了相同资源的场景
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LatentCommSignal:
    agent_a: str
    agent_b: str
    shared_resource: str
    signal_type: str
    confidence: float


class A2ALatentComm:
    def __init__(self, confidence_threshold: float = 0.7):
        self._threshold = confidence_threshold
        self._resource_access: dict[str, list[str]] = {}

    def record_access(self, agent_id: str, resource: str):
        if resource not in self._resource_access:
            self._resource_access[resource] = []
        if agent_id not in self._resource_access[resource]:
            self._resource_access[resource].append(agent_id)

    def detect(self) -> list[LatentCommSignal]:
        signals: list[LatentCommSignal] = []
        for resource, agents in self._resource_access.items():
            if len(agents) >= 2:
                for i in range(len(agents)):
                    for j in range(i + 1, len(agents)):
                        confidence = min(1.0, len(agents) * 0.3)
                        if confidence >= self._threshold:
                            signals.append(
                                LatentCommSignal(
                                    agent_a=agents[i],
                                    agent_b=agents[j],
                                    shared_resource=resource,
                                    signal_type="shared_resource_access",
                                    confidence=round(confidence, 2),
                                )
                            )
        return signals
