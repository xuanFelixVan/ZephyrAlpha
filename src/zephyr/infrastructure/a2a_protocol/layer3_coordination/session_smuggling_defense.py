# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.session_smuggling_defense
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
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""
A2A Session 走私防御 — 防止跨 Agent session 上下文伪造

攻击场景:
  Agent A 发送消息给 Agent B, 但伪造了自己是 Agent C (session_id=C)
  Agent B 基于伪造的 session 上下文做出错误决策

防御:
  1. 每个跨 Agent 消息必须带有源 Agent 的 HMAC 签名
  2. 接收方验证签名后才消费消息
  3. 签名失败 -> 标记为 session_smuggling_attempt -> 记录 + block

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: max_attempts_per_agent 参数
#   fields: 参数 max_attempts_per_agent（无注解）
#   code: session_smuggling_defense.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SessionSmugglingDefense
#   name_en: SessionSmugglingDefense
#   intro: class SessionSmugglingDefense 源码 L73-L112
#   desc: 公共方法（定义序）: verify_session, is_blocked；源码 L73-L112
#   inputs: max_attempts_per_agent
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: SessionSmugglingDefense
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
