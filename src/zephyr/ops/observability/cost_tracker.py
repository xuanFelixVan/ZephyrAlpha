# [A_module] module_id=MOD-INF_cost_tracker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] SRC-123 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md

# [MODULE] zephyr.infrastructure.shared_services.observability.cost_tracker

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
Cost Tracker — Token 成本核算与会计。

依据：
    蓝图 MOD-INF-006 §6.3.2 + v0.6.0
    任务卡 TASK-INF-0109 (Part 2/5)
"""

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class CostRecord:
    task_id: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    timestamp_utc: str


@dataclass
class DailyBudget:
    max_tokens: int = 100000
    max_cost_usd: float = 5.0
    used_tokens: int = 0
    used_cost_usd: float = 0.0


MODEL_PRICING: dict[str, dict[str, float]] = {
    "deepseek": {"input_per_1k": 0.00014, "output_per_1k": 0.00028},
    "gpt-4": {"input_per_1k": 0.03, "output_per_1k": 0.06},
    "gpt-3.5-turbo": {"input_per_1k": 0.0005, "output_per_1k": 0.0015},
}


class CostTracker:
    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or Path("data/observability")
        self._cost_path = self._data_dir / "cost_tracker.jsonl"
        self._budget_path = self._data_dir / "daily_budget.json"

    def record(self, task_id: str, model: str, input_tokens: int, output_tokens: int) -> CostRecord:
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["deepseek"])
        cost = input_tokens / 1000 * pricing["input_per_1k"] + output_tokens / 1000 * pricing["output_per_1k"]

        record = CostRecord(
            task_id=task_id,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost_usd=round(cost, 6),
            timestamp_utc=datetime.now(UTC).isoformat(),
        )

        self._data_dir.mkdir(parents=True, exist_ok=True)

        with open(self._cost_path, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "task_id": record.task_id,
                        "model": record.model,
                        "input_tokens": record.input_tokens,
                        "output_tokens": record.output_tokens,
                        "total_tokens": record.total_tokens,
                        "cost_usd": record.cost_usd,
                        "timestamp_utc": record.timestamp_utc,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

        self._update_budget(record)

        return record

    def get_daily_budget(self) -> DailyBudget:
        if not self._budget_path.exists():
            return DailyBudget()

        try:
            data = json.loads(self._budget_path.read_text(encoding="utf-8"))
            today = datetime.now(UTC).strftime("%Y-%m-%d")
            if data.get("date") != today:
                return DailyBudget()
            return DailyBudget(
                max_tokens=data.get("max_tokens", 100000),
                max_cost_usd=data.get("max_cost_usd", 5.0),
                used_tokens=data.get("used_tokens", 0),
                used_cost_usd=data.get("used_cost_usd", 0.0),
            )
        except (json.JSONDecodeError, KeyError):
            return DailyBudget()

    def is_over_budget(self) -> tuple[bool, str]:
        budget = self.get_daily_budget()
        if budget.used_tokens >= budget.max_tokens:
            return True, f"Token budget exceeded: {budget.used_tokens}/{budget.max_tokens}"
        if budget.used_cost_usd >= budget.max_cost_usd:
            return True, f"Cost budget exceeded: ${budget.used_cost_usd:.4f}/${budget.max_cost_usd:.2f}"
        return False, ""

    def _update_budget(self, record: CostRecord) -> None:
        budget = self.get_daily_budget()
        budget.used_tokens += record.total_tokens
        budget.used_cost_usd += record.cost_usd

        self._budget_path.write_text(
            json.dumps(
                {
                    "date": datetime.now(UTC).strftime("%Y-%m-%d"),
                    "max_tokens": budget.max_tokens,
                    "max_cost_usd": budget.max_cost_usd,
                    "used_tokens": budget.used_tokens,
                    "used_cost_usd": round(budget.used_cost_usd, 6),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
