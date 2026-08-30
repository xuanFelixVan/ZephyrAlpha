# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain-governance/audit-trail/blueprint.md
# [MODULE] zephyr.gov_audit.observability_dashboard
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不可变审计记录;密码学完整性;只追加
# [MODIFY-GUARD] docs/03_modules/_domain-governance/audit-trail/blueprint.md;src/zephyr/audit-trail/__init__.py
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] IntegrityError;WriteError
# [TESTS] tests/test_audit_trail/
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: observability_dashboard.py
# 层: 算法
# - id: A1
#   name_zh: ① DashboardConfig
#   name_en: DashboardConfig
#   intro: class DashboardConfig 源码 L77-L104
#   desc: 公共方法（定义序）: default；源码 L77-L104
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: DashboardConfig
#   downstream: MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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
