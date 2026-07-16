# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_tokenomics
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Tokenomics
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SkillBudgetPreset(str, Enum):
    TIGHT = "tight"
    NORMAL = "normal"
    GENEROUS = "generous"


BudgetLevel = SkillBudgetPreset


@dataclass
class TokenBudget:
    max_tokens: int
    used: int = 0
    hard_cap: bool = True
    warn_threshold: float = 0.8
    created_at: float = field(default_factory=time.time)
    last_reset: float = field(default_factory=time.time)

    @property
    def remaining(self) -> int:
        return max(0, self.max_tokens - self.used)

    @property
    def usage_ratio(self) -> float:
        if self.max_tokens == 0:
            return 1.0
        return self.used / self.max_tokens

    @property
    def is_exhausted(self) -> bool:
        return self.remaining <= 0

    @property
    def is_warning(self) -> bool:
        return self.usage_ratio >= self.warn_threshold


@dataclass
class UsageRecord:
    skill_id: str
    tokens: int
    timestamp: float = field(default_factory=time.time)
    model: str = ""
    purpose: str = ""

    @property
    def estimated_cost_usd(self) -> float:
        pricing = {
            "DeepSeek": (0.14, 0.28),
            "Claude": (3.00, 15.00),
            "GPT": (2.50, 10.00),
            "Gemini": (0.50, 1.50),
            "Qwen": (0.50, 1.50),
        }
        input_price, output_price = pricing.get(self.model, (1.0, 2.0))
        return (self.tokens / 1_000_000) * ((input_price + output_price) / 2)


class SkillTokenomics:
    _PRESET_BUDGETS: dict[SkillBudgetPreset, int] = {
        SkillBudgetPreset.TIGHT: 4096,
        SkillBudgetPreset.NORMAL: 16384,
        SkillBudgetPreset.GENEROUS: 65536,
    }

    def __init__(self, daily_budget_tokens: int = 500_000):
        self._budgets: dict[str, TokenBudget] = {}
        self._daily_budget = TokenBudget(max_tokens=daily_budget_tokens, hard_cap=False)
        self._usage_history: list[UsageRecord] = []
        self._skill_stats: dict[str, dict[str, Any]] = {}
        self._cost_tracker: float = 0.0

    # --- Budget Management ---

    def set_budget(
        self,
        skill_id: str,
        max_tokens: int,
        hard_cap: bool = True,
        warn_threshold: float = 0.8,
    ) -> dict[str, Any]:
        budget = TokenBudget(
            max_tokens=max_tokens,
            hard_cap=hard_cap,
            warn_threshold=warn_threshold,
        )
        self._budgets[skill_id] = budget
        self._skill_stats.setdefault(skill_id, {"budget_hits": 0, "budget_warnings": 0})
        return {
            "skill_id": skill_id,
            "max_tokens": max_tokens,
            "hard_cap": hard_cap,
            "warn_threshold": warn_threshold,
            "budget_set": True,
        }

    def set_preset_budget(self, skill_id: str, level: SkillBudgetPreset) -> dict[str, Any]:
        max_tokens = self._PRESET_BUDGETS.get(level, 16384)
        return self.set_budget(skill_id, max_tokens)

    def get_budget(self, skill_id: str) -> TokenBudget | None:
        return self._budgets.get(skill_id)

    def reset_budget(self, skill_id: str) -> dict[str, Any]:
        budget = self._budgets.get(skill_id)
        if budget is None:
            return {"skill_id": skill_id, "reset": False, "reason": "No budget found"}
        budget.used = 0
        budget.last_reset = time.time()
        return {"skill_id": skill_id, "reset": True, "max_tokens": budget.max_tokens}

    def reset_all(self) -> int:
        count = 0
        for sid in list(self._budgets.keys()):
            budgets = self._budgets[sid]
            budgets.used = 0
            budgets.last_reset = time.time()
            count += 1
        return count

    # --- Consumption ---

    def consume(
        self,
        skill_id: str,
        tokens: int,
        model: str = "",
        purpose: str = "",
    ) -> dict[str, Any]:
        budget = self._budgets.get(skill_id)
        if budget is None:
            budget = TokenBudget(max_tokens=16384)
            self._budgets[skill_id] = budget

        budget.used += tokens
        self._daily_budget.max_tokens += tokens
        self._daily_budget.used += tokens

        record = UsageRecord(
            skill_id=skill_id,
            tokens=tokens,
            model=model,
            purpose=purpose,
        )
        self._usage_history.append(record)

        if budget.is_exhausted and budget.hard_cap:
            self._skill_stats[skill_id]["budget_hits"] += 1
        elif budget.is_warning:
            self._skill_stats[skill_id]["budget_warnings"] += 1

        self._cost_tracker += record.estimated_cost_usd

        return {
            "skill_id": skill_id,
            "tokens_consumed": tokens,
            "tokens_used": budget.used,
            "remaining": budget.remaining,
            "usage_pct": round(budget.usage_ratio * 100, 1),
            "budget_exhausted": budget.is_exhausted,
            "budget_warning": budget.is_warning,
        }

    def evaluate_consumption(self, skill_id: str, estimated_tokens: int) -> dict[str, Any]:
        budget = self._budgets.get(skill_id)
        if budget is None:
            return {"allowed": True, "reason": "No budget — allow all"}

        can_consume = not budget.is_exhausted or not budget.hard_cap
        return {
            "allowed": can_consume,
            "skill_id": skill_id,
            "requested": estimated_tokens,
            "remaining": budget.remaining,
            "reason": "budget_exhausted" if not can_consume else "ok",
        }

    # --- Optimization Suggestions ---

    def suggest_optimizations(self) -> list[dict[str, Any]]:
        suggestions: list[dict[str, Any]] = []

        for sid, budget in self._budgets.items():
            if budget.usage_ratio > 0.9:
                suggestions.append(
                    {
                        "skill_id": sid,
                        "type": "budget_near_exhausted",
                        "current_usage_pct": round(budget.usage_ratio * 100, 1),
                        "suggestion": "Increase budget or trim skill prompt",
                    }
                )

        daily_ratio = self._daily_budget.max_tokens / (self._daily_budget.max_tokens + self._daily_budget.remaining + 1)
        if self._daily_budget.usage_ratio > 0.8:
            suggestions.append(
                {
                    "skill_id": "_global",
                    "type": "daily_budget_warning",
                    "current_usage_pct": round(self._daily_budget.usage_ratio * 100, 1),
                    "suggestion": "Consider reducing less critical skill invocations",
                }
            )

        return suggestions

    # --- Analytics ---

    def get_usage_report(self, skill_id: str | None = None) -> dict[str, Any]:
        target_history = [r for r in self._usage_history if r.skill_id == skill_id] if skill_id else self._usage_history

        total_tokens = sum(r.tokens for r in target_history)
        total_cost = sum(r.estimated_cost_usd for r in target_history)

        by_model: dict[str, int] = {}
        for r in target_history:
            by_model[r.model] = by_model.get(r.model, 0) + r.tokens

        return {
            "skill_id": skill_id or "_all",
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 4),
            "total_calls": len(target_history),
            "tokens_by_model": by_model,
            "daily_budget": {
                "used": self._daily_budget.used,
                "max": self._daily_budget.max_tokens,
                "usage_pct": round(self._daily_budget.usage_ratio * 100, 1),
            },
            "active_budgets": {
                sid: {
                    "used": b.used,
                    "max": b.max_tokens,
                    "usage_pct": round(b.usage_ratio * 100, 1),
                }
                for sid, b in self._budgets.items()
                if b.used > 0
            },
        }

    def get_top_consumers(self, n: int = 5) -> list[dict[str, Any]]:
        by_skill: dict[str, int] = {}
        by_skill_cost: dict[str, float] = {}
        for r in self._usage_history:
            by_skill[r.skill_id] = by_skill.get(r.skill_id, 0) + r.tokens
            by_skill_cost[r.skill_id] = by_skill_cost.get(r.skill_id, 0.0) + r.estimated_cost_usd

        ranked = sorted(by_skill.items(), key=lambda x: x[1], reverse=True)[:n]
        return [
            {
                "skill_id": sid,
                "tokens": tokens,
                "estimated_cost_usd": round(by_skill_cost.get(sid, 0.0), 4),
            }
            for sid, tokens in ranked
        ]

    def forecast_budget(self, skill_id: str, calls_per_hour: float, tokens_per_call: int) -> dict[str, Any]:
        budget = self._budgets.get(skill_id)
        hourly_burn = calls_per_hour * tokens_per_call

        result = {
            "skill_id": skill_id,
            "calls_per_hour": calls_per_hour,
            "tokens_per_call": tokens_per_call,
            "hourly_burn": hourly_burn,
            "budget_remaining": budget.remaining if budget else None,
            "hours_until_exhausted": (budget.remaining / hourly_burn if budget and hourly_burn > 0 else None),
        }
        return result
