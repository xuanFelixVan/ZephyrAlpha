# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.capability_card
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_capability_card | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CapabilityCard — 能力卡片数据模型
==================================
蓝图: ARC-0001 §6.1
对标: Google A2A AgentCard + Anthropic MCP Tool + Cursor Rules
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from zephyr.integration.shared.schema.schemas import BASE_CONFIG
from zephyr.shared.utils.time_utils import now_utc


class CapabilityCategory(str, Enum):
    EMBEDDING = "embedding"
    INFERENCE = "inference"
    SEARCH = "search"
    RERANK = "rerank"
    GOVERNANCE = "governance"
    INFRA = "infra"
    ORCHESTRATION = "orchestration"
    DATA = "data"
    SECURITY = "security"
    OBSERVABILITY = "observability"
    COORDINATION = "coordination"


class CapabilityCard(BaseModel):
    """能力卡片——自描述的能力契约。

    对标:
      - Google A2A AgentCard: name, description, capabilities, skills, examples
      - MCP Tool: name, description, inputSchema
      - Cursor Rules: alwaysApply, globs, description
    """

    model_config = BASE_CONFIG

    capability_id: str = Field(..., description="全局唯一，如 embedding-router")
    name: str = Field(..., description="人类可读名")
    category: CapabilityCategory = Field(..., description="能力类别")
    description: str = Field(..., description="一句话描述 + 使用场景")
    input_schema: dict[str, Any] = Field(default_factory=dict, description="JSON Schema 输入契约")
    output_schema: dict[str, Any] = Field(default_factory=dict, description="JSON Schema 输出契约")
    tags: list[str] = Field(default_factory=list, description="可搜索标签")
    priority: str = Field(default="P1", description="P0/P1/P2")
    runtime_plane: str = Field(default="warm", description="hot/warm/cold")
    requires_human: bool = Field(default=False, description="是否需要人在环")
    status: str = Field(default="ACTIVE", description="ACTIVE/DEGRADED/INACTIVE")
    registered_at: str = Field(default_factory=lambda: now_utc().isoformat())
    examples: list[dict[str, Any]] = Field(default_factory=list, description="使用示例")
