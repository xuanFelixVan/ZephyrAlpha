"""数据生命周期管理器（CT-DATA-LIFECYCLE-001）——8类数据保留策略+每日GC。"""

from __future__ import annotations

DATA_LIFECYCLE: dict[str, dict] = {
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
