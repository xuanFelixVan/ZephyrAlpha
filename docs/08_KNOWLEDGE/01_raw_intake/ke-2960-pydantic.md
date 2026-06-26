---
module_id: KE-2860
status: active
title: Pydantic 严格模式示例
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# Pydantic 严格模式示例

Pydantic 严格模式示例
from pydantic import BaseModel, ConfigDict

class ToolCallArguments(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    # 任何额外字段 / 类型不符 → ValidationError
    tool_name: str
    arguments: dict
    # ...
