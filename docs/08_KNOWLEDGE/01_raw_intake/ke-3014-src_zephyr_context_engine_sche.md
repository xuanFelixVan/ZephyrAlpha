---
module_id: KE-2914
status: active
title: src/zephyr/context-engine/schemas.py (experimental 产出)
category: module_blueprint
---

# src/zephyr/context-engine/schemas.py (experimental 产出)

src/zephyr/context-engine/schemas.py (experimental 产出)

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class ContextRequest(BaseModel):
    task_id: str
    task_kind: Literal["feature", "refactor", "bugfix", "review", "architecture", "research"]
    target_files: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    token_budget: int = Field(default=16000, ge=2000, le=200000)
    ide_id: IDEID = IDEID.GENERIC_MCP
    slot_overrides: dict[str, float] | None = Field(
        default=None,
        description="动态覆盖默认 slot 预算占比，如 {'code_refs': 0.45, 'lessons': 0.05}")

class SlotContent(BaseModel):
    slot: str
    items: list[dict]
    token_count: int
    source_traces: list[str] = Field(description="可追溯源，如 ['vms://decisions/KBG-0016', 'file://src/...']")
    degraded_sources: list[str] = Field(default_factory=list, description="本 slot 遇到的降级源")

class ContextBundle(BaseModel):
    request_id: str
    task_id: str
    slots: dict[str, SlotContent]
    total_token_count: int
    token_budget: int
    compression_ratio: Optional[float] = None
    built_at: datetime
    bundle_hash: str = Field(description="sha256(序列化 slots)，用于 inject 幂等")
    degraded: bool = Field(default=False, description="任一 slot 触发降级则为 True")
    degrade_reasons: list[str] = Field(default_factory=list)

class ValidationReport(BaseModel):
    passed: bool
    token_within_budget: bool
    all_citations_resolvable: bool
    no_stale_references: bool
    violations: list[str] = Field(default_factory=list)

class InjectResult(BaseModel):
    channels_used: list[IDEChannel]
    channels_skipped: list[tuple[IDEChannel, str]] = Field(description="[(channel, skip_reason)]")
    injected_at: datetime
    ack_received: bool
