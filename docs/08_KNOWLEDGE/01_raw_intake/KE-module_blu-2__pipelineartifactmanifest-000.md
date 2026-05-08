---
module_id: KE-module_blu-2__pipelineartifactmanifest-000
title: 2. PipelineArtifactManifest
category: module_blueprint
---

# 2. PipelineArtifactManifest

2. PipelineArtifactManifest

```python
class PipelineArtifactManifest(BaseModel):
    pipeline_id: str
    task_id: str
    artifacts: list[PipelineArtifact]
    meta: dict              # 扩展元数据
    created: str
```
