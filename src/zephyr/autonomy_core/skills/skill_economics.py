# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_economics
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
# [A_module] module_id=MOD-ORC_skill_economics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Economics
Author: factory-agent
Version: 0.3.0

Token/API cost tracking
"""

from typing import Any

PRICING = {
    "deepseek-chat": {"in": 0.001, "out": 0.002},
    "deepseek-reasoner": {"in": 0.002, "out": 0.004},
    "glm-4-flash": {"in": 0.001, "out": 0.001},
    "claude-sonnet-4": {"in": 0.020, "out": 0.080},
    "claude-opus-4": {"in": 0.100, "out": 0.400},
    "gpt-4o": {"in": 0.005, "out": 0.015},
    "gpt-4o-mini": {"in": 0.003, "out": 0.015},
}


class SkillEconomics:
    def __init__(self):
        self._costs: dict[str, dict[str, Any]] = {}
        self._spent = 0.0

    def _price(self, model: str) -> dict[str, float]:
        for k, v in PRICING.items():
            if k in model.lower():
                return v
        return {"in": 0.001, "out": 0.002}

    def track_cost(self, skill_id: str, tokens_in: int, tokens_out: int, model: str) -> dict[str, Any]:
        p = self._price(model)
        cost = round((tokens_in / 1000.0) * p["in"] + (tokens_out / 1000.0) * p["out"], 6)
        self._spent += cost
        if skill_id not in self._costs:
            self._costs[skill_id] = {"total_cost": 0.0, "calls": 0, "in": 0, "out": 0}
        self._costs[skill_id]["total_cost"] = round(self._costs[skill_id]["total_cost"] + cost, 6)
        self._costs[skill_id]["calls"] += 1
        self._costs[skill_id]["in"] += tokens_in
        self._costs[skill_id]["out"] += tokens_out
        return {"skill_id": skill_id, "cost_estimated": cost, "session_total": round(self._spent, 6)}

    def get_costs(self, skill_id: str) -> dict[str, Any]:
        return self._costs.get(skill_id, {"total_cost": 0.0, "calls": 0})

    def recommend_cheapest_model(self, strength: str = "code_generation") -> dict[str, Any]:
        candidates = [
            {"model": "deepseek-chat", "in": 0.001, "out": 0.002},
            {"model": "glm-4-flash", "in": 0.001, "out": 0.001},
        ]
        best = min(candidates, key=lambda c: c["in"] + c["out"])
        return {"recommended": best["model"], "cost_per_1k_in": best["in"], "cost_per_1k_out": best["out"]}
