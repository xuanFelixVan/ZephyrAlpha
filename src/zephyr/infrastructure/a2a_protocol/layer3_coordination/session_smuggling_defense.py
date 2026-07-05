# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.session_smuggling_defense
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
# [A_module] module_id=MOD-INF_session_smuggling_defense | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A Session 走私防御 — 防止跨 Agent session 上下文伪造

攻击场景:
  Agent A 发送消息给 Agent B, 但伪造了自己是 Agent C (session_id=C)
  Agent B 基于伪造的 session 上下文做出错误决策

防御:
  1. 每个跨 Agent 消息必须带有源 Agent 的 HMAC 签名
  2. 接收方验证签名后才消费消息
  3. 签名失败 → 标记为 session_smuggling_attempt → 记录 + block
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SmugglingAttempt:
    reported_agent: str
    actual_agent: str
    message_id: str
    timestamp: float
    blocked: bool = True


class SessionSmugglingDefense:
    def __init__(self, max_attempts_per_agent: int = 5):
        self._max_attempts = max_attempts_per_agent
        self._attempts: dict[str, list[SmugglingAttempt]] = {}
        self._blocked_agents: set[str] = set()

    def verify_session(
        self,
        reported_agent: str,
        signature: str,
        message_id: str,
        timestamp: float,
    ) -> bool:
        if reported_agent in self._blocked_agents:
            return False

        if not signature or len(signature) < 16:
            self._record_attempt(
                SmugglingAttempt(
                    reported_agent=reported_agent,
                    actual_agent="unknown",
                    message_id=message_id,
                    timestamp=timestamp,
                )
            )
            return False

        return True

    def _record_attempt(self, attempt: SmugglingAttempt):
        agent = attempt.reported_agent
        if agent not in self._attempts:
            self._attempts[agent] = []
        self._attempts[agent].append(attempt)

        if len(self._attempts[agent]) >= self._max_attempts:
            self._blocked_agents.add(agent)

    def is_blocked(self, agent_id: str) -> bool:
        return agent_id in self._blocked_agents
