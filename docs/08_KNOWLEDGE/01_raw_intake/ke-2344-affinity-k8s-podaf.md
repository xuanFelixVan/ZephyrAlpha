---
module_id: KE-2249---------k8s-podaf-000
status: active
title: 4.5 Affinity 约束模型（对标 K8s PodAffinityTerm + WeightedPodAffinityTerm）
category: module_blueprint
---

# 4.5 Affinity 约束模型（对标 K8s PodAffinityTerm + WeightedPodAffinityTerm）

4.5 Affinity 约束模型（对标 K8s PodAffinityTerm + WeightedPodAffinityTerm）

```python
class AffinityWeight(str, Enum):
    HARD = "hard"    # mandatory —— 违反则 ABORT
    SOFT = "soft"    # preferred —— 违反则 WARN

class PipelineAffinityConstraint(BaseModel):
    constraint_type: str                  # "model" | "sandbox" | "pipeline"
    node_a: str                           # 主语节点 "M3"
    node_b: str | None = None             # 宾语节点 "M7"，单节点约束为 None
    weight: AffinityWeight = AffinityWeight.SOFT
    description: str = ""

    def check(self, modules: dict[str, ModuleResult]) -> bool:
        """校验约束是否满足。返回 True=通过。"""
        ...

AFFINITY_CONSTRAINTS: list[PipelineAffinityConstraint] = [
    PipelineAffinityConstraint(
        constraint_type="model", node_a="M3", node_b="M7",
        weight=AffinityWeight.HARD,
        description="双盲审查必须用不同模型",
    ),
    PipelineAffinityConstraint(
        constraint_type="model", node_a="M8", node_b="M9",
        weight=AffinityWeight.SOFT,
        description="建议合规检查+风险评估用不同模型",
    ),
]
```
