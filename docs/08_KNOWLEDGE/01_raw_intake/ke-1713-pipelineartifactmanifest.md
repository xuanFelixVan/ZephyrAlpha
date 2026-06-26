---
module_id: KE-1623
status: active
title: 2. PipelineArtifactManifest
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
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
