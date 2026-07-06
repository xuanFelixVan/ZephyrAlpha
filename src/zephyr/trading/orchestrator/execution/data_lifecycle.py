from typing import Final

# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.execution.data_lifecycle
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.orchestrator.__init__
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
# [A_module] module_id=MOD-ORC_data_lifecycle | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""数据生命周期管理器（CT-DATA-LIFECYCLE-001）——8类数据保留策略+每日GC。"""

DATA_LIFECYCLE: Final[dict[str, dict]] = {
    "task_cards": {"hot_days": 7, "cold_days": 90, "archive_policy": "compress"},
    "findings": {"hot_days": 30, "cold_days": 180, "archive_policy": "compress"},
    "knowledge_entries": {"hot_days": 7, "cold_days": 365, "archive_policy": "keep"},
    "audit_logs": {"hot_days": 30, "cold_days": 365, "archive_policy": "compress"},
    "metrics": {"hot_days": 14, "cold_days": 90, "archive_policy": "rollup"},
    "vector_embeddings": {"hot_days": 7, "cold_days": 0, "archive_policy": "regenerate"},
    "dlq_messages": {"hot_days": 7, "cold_days": 30, "archive_policy": "purge"},
    "session_logs": {"hot_days": 30, "cold_days": 365, "archive_policy": "keep"},
}


class DataLifecycleManager:
    def get_policy(self, data_type: str) -> dict | None:
        return DATA_LIFECYCLE.get(data_type)

    def list_types(self) -> list[str]:
        return list(DATA_LIFECYCLE.keys())

    def should_purge(self, data_type: str, age_days: int) -> bool:
        policy = DATA_LIFECYCLE.get(data_type)
        if policy is None:
            return False
        if policy["archive_policy"] == "purge" and age_days > policy["cold_days"]:
            return True
        return False
