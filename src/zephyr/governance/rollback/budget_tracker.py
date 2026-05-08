"""G-CT-009 契约：Rollback → Budget 回滚成本计入预算."""

from __future__ import annotations


class RollbackBudgetTracker:
    """回滚成本追踪→Budget."""

    def track_cost(self, agent_id: str, rollback_id: str, estimated_cost: float) -> dict:
        return {
            "agent_id": agent_id,
            "rollback_id": rollback_id,
            "cost": estimated_cost,
            "budget_consumed": True,
        }
