---
module_id: KE-2010
status: active
title: 3. ModuleInput
category: module_blueprint
ttl: permanent
---

# 3. ModuleInput

3. ModuleInput

```python
class ModuleInput(BaseModel):
    module_id: str          # 当前模块
    previous_artifacts: list[PipelineArtifact]  # 上级模块产出
    context: dict           # 额外上下文

    def validate(self) -> bool:
        """校验所需 Artifact 是否齐全"""
```
