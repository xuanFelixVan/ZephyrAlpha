---
module_id: KE-1858----provenance----d-020-03-005
status: active
title: 2.3 分级 Provenance（决策 D-020-03）
category: module_blueprint
---

# 2.3 分级 Provenance（决策 D-020-03）

2.3 分级 Provenance（决策 D-020-03）

> **决策 D-020-03**：Provenance 深度由权限级别决定——always_allow 只记录轻量 provenance，auto_guard 记录标准 provenance（含决策依据+后验检查），blocked 记录全量 provenance（含阻断原因+违反规则）。版本从 v0.2.0 的 3 级扩展到 v1.0.0 的 3 级不变，但 Light 级补充 `decision_brief`。

```python
class ProvenanceDepth(str, Enum):
    LIGHT = "light"        # always_allow 操作
    STANDARD = "standard"  # auto_guard 操作
    FULL = "full"          # blocked 操作（阻断记录）

class ProvenanceLight(BaseModel):
    agent_id: str
    timestamp: datetime
    action_type: str
    ide_source: str
    decision_brief: str = Field(default="", description="一句话决策依据——如'按 MOD-INF-018 §2.2'")

class ProvenanceStandard(BaseModel):
    agent_id: str
    timestamp: datetime
    action_type: str
    ide_source: str
    decision_basis: list[str] = Field(default_factory=list, description="决策依据——读了哪些蓝图/ADR/门禁结果")
    guard_checks_executed: list[str] = Field(default_factory=list, description="执行的后验检查项")
    guard_checks_passed: list[str] = Field(default_factory=list)
    guard_checks_failed: list[str] = Field(default_factory=list)
    guard_result: Optional[str] = Field(default=None, description="后验结果——pass/fail/rolled_back")
    confidence_level: str = Field(default="high", description="AI 决策置信度——high/medium/low")

class ProvenanceFull(BaseModel):
    agent_id: str
    timestamp: datetime
    action_type: str
    ide_source: str
    blocked_reason: str = Field(..., description="阻断原因")
    attempted_action: str = Field(..., description="尝试的操作")
    rule_violated: str = Field(..., description="违反的规则ID")
    escalation_triggered: bool = Field(default=False, description="是否触发了升级/委托")
    escalation_target: Optional[str] = Field(default=None, description="升级目标——human_owner/supervisor_agent")
```
