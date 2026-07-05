# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.work_dag
# [DOMAIN] D_TRADING
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
# [A_module] module_id=MOD-ORC_work_dag | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
WorkDAG + WorkItem — 工作编排数据模型
======================================
蓝图: ARC-0001 §4.3
借鉴: Airflow DAG + Temporal Workflow + K8s Job
"""

from pydantic import BaseModel, Field

from zephyr.integration.shared.schema.schemas import BASE_CONFIG


class WorkNode(BaseModel):
    model_config = BASE_CONFIG
    node_id: str
    capability_id: str
    work_type: str = ""
    params: dict = Field(default_factory=dict)
    layer_override: str | None = None
    priority_override: str | None = None


class WorkEdge(BaseModel):
    model_config = BASE_CONFIG
    from_node: str
    to_node: str
    condition: str = "success"


class WorkDAG(BaseModel):
    model_config = BASE_CONFIG
    dag_id: str
    name: str = ""
    description: str = ""
    nodes: list[WorkNode] = Field(default_factory=list)
    edges: list[WorkEdge] = Field(default_factory=list)
    default_layer: str = "local"
    default_priority: str = "P1"
    max_parallelism: int = 3
    retry_on_failure: int = 2
    timeout_minutes: int = 60


class WorkItem(BaseModel):
    model_config = BASE_CONFIG
    item_id: str
    dag_id: str | None = None
    node_id: str | None = None
    capability_id: str
    work_type: str = ""
    params: dict = Field(default_factory=dict)
    layer: str = "local"
    priority: str = "P1"
    status: str = "PENDING"
    depends_on: list[str] = Field(default_factory=list)
    created_at: str = ""
    scheduled_at: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    result: dict | None = None
    error: str | None = None
