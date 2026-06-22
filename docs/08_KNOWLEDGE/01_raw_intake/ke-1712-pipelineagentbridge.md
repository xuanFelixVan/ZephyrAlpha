---
module_id: KE-1622
status: active
title: 2. PipelineAgentBridge
category: module_blueprint
---

# 2. PipelineAgentBridge

2. PipelineAgentBridge

```python
class AgentDirective(BaseModel):
    role: str               # 对应 M 节点的 agent role
    system_prompt: str      # 该 role 的 system prompt
    sandbox_type: str       # full/standard/audit/restricted
    model: str              # deepseek/glm/claude
    task_card_ref: str      # task_id
    timeout: float          # 超时秒数

class PipelineAgentBridge(BaseModel):
    role_mapping: dict[str, str]  # "M3" → "generator_agent"
    directive_chain: list[AgentDirective]

    def bridge(self, route_decision: PipelineRouteDecision) -> AgentDirective:
        """路由决策→AgentDirective翻译"""
```
