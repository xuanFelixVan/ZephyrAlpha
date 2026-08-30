# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.work_dag
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
WorkDAG + WorkItem — 工作编排数据模型
======================================
蓝图: docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md §3.1
借鉴: Airflow DAG + Temporal Workflow + K8s Job

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: work_dag.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: WorkNode, WorkEdge, WorkDAG, WorkItem
#   desc: 数据契约/异常/枚举声明共 4 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（4 类）
#   name_en: data classes
#   intro: WorkNode, WorkEdge, WorkDAG, WorkItem
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from pydantic import BaseModel, Field

from zephyr.shared.schema.schemas import BASE_CONFIG


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
