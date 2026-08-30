# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.capability_card
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.schema.schemas
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CapabilityCard — 能力卡片数据模型
==================================
蓝图: docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md §3.1
对标: Google A2A AgentCard + Anthropic MCP Tool + Cursor Rules

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: capability_card.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: CapabilityCategory, CapabilityCard
#   desc: 数据契约/异常/枚举声明共 2 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（2 类）
#   name_en: data classes
#   intro: CapabilityCategory, CapabilityCard
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from zephyr.shared.schema.schemas import BASE_CONFIG
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
