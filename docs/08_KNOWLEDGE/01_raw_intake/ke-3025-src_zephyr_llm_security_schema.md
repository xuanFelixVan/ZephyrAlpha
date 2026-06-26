---
module_id: KE-2925
status: active
title: src/zephyr/llm-security/schemas.py
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# src/zephyr/llm-security/schemas.py

src/zephyr/llm-security/schemas.py

class InputPayload(BaseModel):
    source: Literal["system_config", "task_card", "code_file", "vms_retrieval",
                    "external_url", "email", "mcp_tool_return", "user_chat", "unknown"]
    raw_text: str
    metadata: dict = Field(default_factory=dict)
    correlation_id: Optional[str] = None

class InputVerdict(BaseModel):
    allow: bool
    trust_level: InputTrustLevel
    isolated_prompt: Optional[str] = Field(None, description="allow=True 时提供，LLM 可直接喂")
    reason: Optional[str] = None
    matched_rules: list[str] = Field(default_factory=list)

class OutputPayload(BaseModel):
    raw_text: str
    parsed_json: Optional[dict] = None
    source_tool: Optional[str] = None
    correlation_id: Optional[str] = None

class OutputVerdict(BaseModel):
    allow: bool
    reason: Optional[str] = None
    violations: list[dict] = Field(default_factory=list, description="Pydantic errors / pattern matches")
    secret_hits: list[dict] = Field(default_factory=list)
    pattern_hits: list[dict] = Field(default_factory=list)
    quarantine: bool = Field(default=False, description="严重违规，记录并隔离 correlation_id")

class SecretScanResult(BaseModel):
    hits: list[dict]
    redacted_text: str = Field(description="命中 secret 部分被 [REDACTED] 替换后文本")

class PatternScanResult(BaseModel):
    hits: list[dict]
    severity: Literal["info", "warn", "error", "critical"]

class StrictnessSnapshot(BaseModel):
    baseline: float = Field(default=1.0, description="1.0 为默认严格度")
    current: float
    deltas: list[dict] = Field(default_factory=list, description="[{delta, ttl_minutes, reason, applied_at}]")
```
