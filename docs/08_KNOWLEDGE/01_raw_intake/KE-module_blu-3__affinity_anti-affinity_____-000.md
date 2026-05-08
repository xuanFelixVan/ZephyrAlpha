---
module_id: KE-module_blu-3__affinity_anti-affinity_____-000
title: 3. Affinity/Anti-Affinity 约束矩阵（5条）
category: module_blueprint
---

# 3. Affinity/Anti-Affinity 约束矩阵（5条）

3. Affinity/Anti-Affinity 约束矩阵（5条）

```python
class AffinityWeight(str, Enum):
    HARD = "hard"    # mandatory —— 违反则 ABORT
    SOFT = "soft"    # preferred —— 违反则 WARN

class PipelineAffinityConstraint(BaseModel):
    constraint_type: str
    node_a: str
    node_b: str | None = None
    weight: AffinityWeight
    description: str

AFFINITY_CONSTRAINTS = [
    # 1. M3/M7 hard antiAffinity——双盲审查模型隔离
    PipelineAffinityConstraint("model", "M3", "M7", HARD, "双盲审查必须用不同模型"),
    # 2. M8/M9 soft antiAffinity——建议交叉
    PipelineAffinityConstraint("model", "M8", "M9", SOFT, "建议合规+风险用不同模型"),
    # 3. A区 sandbox mandatory affinity
    PipelineAffinityConstraint("sandbox", "M1", None, HARD, "M1-M4必须在full/standard"),
    # 4. A区 pipeline mandatory affinity——产出必须经M5→M6
    PipelineAffinityConstraint("pipeline", "A", None, HARD, "A区产出→M5打包→M6边界标记"),
    # 5. B区后半段 soft affinity
    PipelineAffinityConstraint("model", "M8", None, SOFT, "M8-M11优先deepseek降成本"),
]
```
