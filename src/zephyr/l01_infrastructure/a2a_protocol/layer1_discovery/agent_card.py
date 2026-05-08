"""Agent Card 模型 — A2A Layer 1 Discovery"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class AgentCapability(str, Enum):
    READ = "read"
    GREP = "grep"
    GLOB = "glob"
    WRITE = "write"
    BASH = "bash"
    SEARCH = "search"
    RECALL = "recall"


class AgentCard(BaseModel):
    agent_id: str = Field(..., pattern=r"^agent-[a-z0-9_-]+$")
    name: str
    description: str
    version: str = "0.1.0"
    capabilities: List[AgentCapability] = []
    skill_ids: List[str] = []
    model_preferences: List[str] = ["deepseek"]
    max_tasks: int = 5
    endpoint: Optional[str] = None
    public_key: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, str] = {}
