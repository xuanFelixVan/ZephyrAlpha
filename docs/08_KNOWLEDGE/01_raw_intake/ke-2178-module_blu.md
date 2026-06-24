---
module_id: KE-2086
status: active
title: 3.2.2 其他模型
category: module_blueprint
---

# 3.2.2 其他模型

3.2.2 其他模型

```python
class DecompositionResult(BaseModel):
    total_tasks: int = Field(ge=0)
    tasks: list[TaskCard]
    dependency_graph: dict[str, list[str]] = Field(default_factory=dict)
    unassigned_items: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

class GateCheckResult(BaseModel):
    gate_id: GateLevel
    task_id: str
    passed: bool
    violations: list[str] = Field(default_factory=list)
    checked_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class AuditFinding(BaseModel):
    finding_id: str = Field(..., pattern=r"^F-\d{4}$")
    dimension: str
    severity: str = Field(..., pattern=r"^(critical|high|medium|low|info)$")
    description: str
    source_task: str
    resolved: bool = Field(default=False)
    resolution_note: Optional[str] = None
```
