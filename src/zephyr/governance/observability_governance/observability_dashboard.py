# [BLUEPRINT] SRC-052 | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.governance.observability_governance.observability_dashboard
# [DOMAIN] D_OPS
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-GOV_observability_dashboard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class DashboardPanel(str, Enum):
    SYSTEM_HEALTH = "system_health"
    COST = "cost"
    ORDER_FLOW = "order_flow"
    MODEL_DRIFT = "model_drift"


class SLI(str, Enum):
    CPU = "cpu"
    MEMORY = "memory"
    DISK_IO = "disk_io"
    NETWORK_THROUGHPUT = "network_throughput"
    CONTEXT_LENGTH = "context_length"
    TOKEN_CONSUMPTION = "token_consumption"
    DECISION_ACCURACY = "decision_accuracy"
    STATE_AWARENESS = "state_awareness"
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"
    FEEDBACK_ADOPTION = "feedback_adoption"
    DATA_FRESHNESS = "data_freshness"


@dataclass
class DashboardConfig:
    panels: dict[str, dict[str, object]] = field(default_factory=dict)
    refresh_interval_seconds: int = 10

    @staticmethod
    def default() -> DashboardConfig:
        return DashboardConfig(
            panels={
                "system_health": {
                    "title": "系统健康",
                    "slis": [sli.value for sli in SLI],
                    "sli_count": 11,
                },
                "cost": {
                    "title": "成本仪表板",
                    "metrics": ["daily_api_cost", "cumulative_cost", "budget_remaining"],
                },
                "order_flow": {
                    "title": "订单流",
                    "metrics": ["order_latency_p95", "order_count", "fill_rate"],
                },
                "model_drift": {
                    "title": "模型漂移",
                    "metrics": ["drift_score", "feature_psi", "prediction_stability"],
                },
            },
            refresh_interval_seconds=10,
        )
