---
module_id: KE-1291
status: active
title: 1. PipelineArtifact
category: module_blueprint
---

# 1. PipelineArtifact

1. PipelineArtifact

```python
class ArtifactClassification(str, Enum):  # B138
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class PipelineArtifact(BaseModel):
    artifact_id: str
    type: str               # "code" | "document" | "report" | "finding" | ...
    source_module: str      # "M3"
    content: str
    path: str | None
    size: int
    hash: str               # SHA256
    timestamp: str
    classification: ArtifactClassification
```
