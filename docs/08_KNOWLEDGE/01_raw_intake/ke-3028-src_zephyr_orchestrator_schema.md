---
module_id: KE-2928
status: active
title: src/zephyr/orchestrator/schemas.py
category: module_blueprint
---

# src/zephyr/orchestrator/schemas.py

src/zephyr/orchestrator/schemas.py

from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class TaskSubmit(BaseModel):
    task_card_path: str = Field(description="任务卡 YAML 文件路径")
    priority: int = Field(default=5, ge=1, le=10)
    depends_on: list[str] = Field(default_factory=list, description="前置任务 task_id")
    required_capabilities: list[str] = Field(default_factory=list,
        description="Agent 必备能力，如 ['python', 'pandas', 'backtest']")
    timeout_seconds: int = Field(default=3600, ge=60, le=86400)
    sandbox_policy: Optional["SandboxPolicy"] = None

class Task(BaseModel):
    task_id: str
    state: TaskState
    submitted_at: datetime
    task_card_path: str
    task_card_hash: str
    priority: int
    depends_on: list[str]
    required_capabilities: list[str]
    claimed_by: Optional[str] = None
    sandbox_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout_seconds: int
    retry_count: int = 0
    last_progress_at: Optional[datetime] = None
    metrics: dict = Field(default_factory=dict)

class AgentSpec(BaseModel):
    agent_id: str
    agent_kind: Literal["implementer", "reviewer", "tester", "planner", "generic"]
    capabilities: list[str]
    max_concurrent_tasks: int = Field(default=1, ge=1, le=10)
    heartbeat_interval_seconds: int = Field(default=30)

class AgentProgress(BaseModel):
    task_id: str
    agent_id: str
    stage: Literal["planning", "coding", "testing", "reviewing"]
    files_touched: list[str]
    tokens_consumed: int
    tools_invoked: list[str]
    observation_hash: str = Field(description="本次进度观测指纹，用于幻觉循环检测")
    timestamp: datetime

class TaskResult(BaseModel):
    task_id: str
    output_files: list[str]
    test_passed: bool
    test_report_path: Optional[str] = None
    metrics: dict
    summary: str = Field(description="自然语言摘要，入 VMS task_history")

class TaskFailure(BaseModel):
    task_id: str
    failure_kind: Literal[
        "timeout",
        "exception",
        "test_failed",
        "review_rejected",
        "hallucination_detected",
        "sandbox_violation",
        "dependency_failed",
    ]
    message: str
    retryable: bool
    stack_trace: Optional[str] = None

class SandboxPolicy(BaseModel):
    writable_paths: list[str] = Field(description="白名单可写路径（相对 repo root）")
    readable_paths: list[str] = Field(default_factory=list,
        description="白名单可读路径，默认整个 repo 只读")
    network_access: Literal["none", "local_only", "full"] = "none"
    max_memory_mb: int = Field(default=2048)
    max_cpu_seconds: int = Field(default=3600)
    allowed_commands: list[str] = Field(default_factory=list,
        description="白名单可执行命令，为空=拒绝所有命令执行")

class Sandbox(BaseModel):
    sandbox_id: str
    task_id: str
    kind: Literal["windows_acl", "docker", "none"]
    mount_root: str = Field(description="Agent 感知的根目录，Agent 所有路径必经此前缀")
    policy: SandboxPolicy
    created_at: dateti
