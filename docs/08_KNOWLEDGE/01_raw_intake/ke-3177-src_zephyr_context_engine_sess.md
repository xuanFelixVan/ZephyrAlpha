---
module_id: KE-3071
status: active
title: src/zephyr/context-engine/session_carryover.py
category: session_log
ttl: permanent
doc_type: knowledge_entry
---

# src/zephyr/context-engine/session_carryover.py

src/zephyr/context-engine/session_carryover.py
from datetime import datetime
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

class EndedReason(str, Enum):
    NORMAL_SHUTDOWN = "normal_shutdown"
    USER_COMMAND = "user_command"
    CRASH = "crash"
    IDLE_TIMEOUT = "idle_timeout"
    IDE_CLOSE = "ide_close"

class HallucinationRule(str, Enum):
    LOOP_SAME_OBSERVATION = "loop_same_observation"
    NO_PROGRESS_TIMEOUT = "no_progress_timeout"
    REPEATED_SAME_FILE_EDIT = "repeated_same_file_edit"
    TOOL_REPEAT_WITHOUT_RESULT = "tool_repeat_without_result"
    FABRICATED_PATH = "fabricated_path"
    FABRICATED_API = "fabricated_api"
    OTHER = "other"

class OpenTask(BaseModel):
    model_config = ConfigDict(extra='forbid')
    task_id: str
    status: Literal["draft", "queued", "assigned", "running", "blocked", "reviewing"]
    summary: str = Field(max_length=300)
    files_in_scope: list[str] = Field(default_factory=list)
    last_observation: str | None = Field(default=None, max_length=500)
    next_action_hint: str | None = Field(default=None, max_length=300)

class Blocker(BaseModel):
    model_config = ConfigDict(extra='forbid')
    task_id: str
    reason: str = Field(max_length=500)
    requires_user: bool
    suggested_prompt: str | None = None

class HallucinationEvent(BaseModel):
    model_config = ConfigDict(extra='forbid')
    event_id: str
    task_id: str
    rule_triggered: HallucinationRule
    evidence: str = Field(max_length=1000)
    mitigation_applied: str | None = None
    timestamp: datetime

class ContextState(BaseModel):
    model_config = ConfigDict(extra='forbid')
    active_collections: list[Literal["decisions", "code_context", "lessons",
                                      "knowledge", "runtime_logs"]] = Field(default_factory=list)
    recent_retrievals: list[dict] = Field(default_factory=list, max_length=20)
    compression_strategy_used: Literal["llm", "rule_based", "truncate", "none"] | None = None
    mcp_channels_active: list[Literal["tools", "resources", "prompts", "sampling"]] = \
        Field(default_factory=list)

class TokenBudget(BaseModel):
    model_config = ConfigDict(extra='forbid')
    session_total_used: int = Field(default=0, ge=0)
    session_remaining: int | None = None
    daily_quota_consumed: int | None = None
    opus_calls_today: int = Field(default=0, ge=0, le=10)   # Opus M-03 日配额

class EnvironmentSnapshot(BaseModel):
    model_config = ConfigDict(extra='forbid')
    git_branch: str | None = None
    git_head_sha: str | None = None
    uncommitted_files: list[str] = Field(default_factory=list)
    ruff_status: Literal["clean", "warnings", "errors"] | None = None
    pytest_last_result: Literal["pass", "fail", "not_run"] | None = None

class IDEInfo(BaseModel):
    model_config = ConfigDict(extra='forbid')
    ide_id: Literal["cursor", "trae", "claude_desktop", "generic_mcp"]
    ide_version: str | None = None
    os: str | None = No
