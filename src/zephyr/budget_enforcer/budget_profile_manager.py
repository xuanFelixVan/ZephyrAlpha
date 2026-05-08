from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class BudgetProfile:
    name: str
    token_limit: int
    cost_limit: float
    time_limit: float
    model_tier: str
    description: str = ""


class BudgetProfileManager:

    DEFAULT_PROFILES: dict[str, BudgetProfile] = {
        "minimal": BudgetProfile(
            name="minimal", token_limit=2000, cost_limit=0.05, time_limit=60.0,
            model_tier="minimal", description="极简模式：最小消耗"
        ),
        "standard": BudgetProfile(
            name="standard", token_limit=8000, cost_limit=0.30, time_limit=300.0,
            model_tier="economy", description="标准模式：常规任务"
        ),
        "premium": BudgetProfile(
            name="premium", token_limit=16000, cost_limit=0.80, time_limit=600.0,
            model_tier="standard", description="高级模式：复杂任务（需审批）"
        ),
    }

    def __init__(self, profile_path: str = "config/budget_profiles.yaml"):
        self._profile_path = Path(profile_path)
        self._profiles: dict[str, BudgetProfile] = dict(self.DEFAULT_PROFILES)
        self._load()

    def _load(self) -> None:
        if self._profile_path.exists():
            with open(self._profile_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data:
                    for name, cfg in data.items():
                        self._profiles[name] = BudgetProfile(
                            name=name,
                            token_limit=cfg.get("token_limit", 8000),
                            cost_limit=cfg.get("cost_limit", 0.30),
                            time_limit=cfg.get("time_limit", 300.0),
                            model_tier=cfg.get("model_tier", "economy"),
                            description=cfg.get("description", ""),
                        )

    def _save(self) -> None:
        data = {
            name: {
                "token_limit": p.token_limit,
                "cost_limit": p.cost_limit,
                "time_limit": p.time_limit,
                "model_tier": p.model_tier,
                "description": p.description,
            }
            for name, p in self._profiles.items()
        }
        with open(self._profile_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    def get(self, name: str) -> BudgetProfile | None:
        return self._profiles.get(name)

    def list_profiles(self) -> list[str]:
        return list(self._profiles.keys())

    def add(self, profile: BudgetProfile) -> None:
        self._profiles[profile.name] = profile
        self._save()

    def remove(self, name: str) -> None:
        if name in self.DEFAULT_PROFILES:
            return
        self._profiles.pop(name, None)
        self._save()

    def set_active(self, name: str) -> BudgetProfile | None:
        return self._profiles.get(name)

    def match_for_task(self, estimated_tokens: int, estimated_cost: float) -> BudgetProfile:
        best = self._profiles["minimal"]
        for p in self._profiles.values():
            if (
                p.token_limit >= estimated_tokens
                and p.cost_limit >= estimated_cost
            ):
                if p.token_limit < best.token_limit:
                    best = p
        return best
