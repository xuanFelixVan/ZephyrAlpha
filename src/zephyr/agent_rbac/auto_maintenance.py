"""自动维护——僵尸规则检测+权限复杂度预算(max=30)+Owner健康仪表盘(5数字)."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any

from pydantic import BaseModel, Field


class RuleHealth(BaseModel):
    rule_id: str
    last_triggered: str
    trigger_count: int = 0
    zombie: bool = False


class ComplexityBudget(BaseModel):
    current: int = 0
    max_complexity: int = 30
    exceeded: bool = False


class OwnerDashboard(BaseModel):
    active_rules: int = 0
    zombie_rules: int = 0
    complexity_pct: float = 0.0
    denied_last_24h: int = 0
    emergency_tokens_active: int = 0
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AutoMaintenance:
    _ZOMBIE_DAYS: int = 30

    def __init__(self) -> None:
        self._rules: dict[str, RuleHealth] = {}

    def register_rule(self, rule_id: str) -> RuleHealth:
        rh = RuleHealth(rule_id=rule_id, last_triggered=datetime.now(timezone.utc).isoformat())
        self._rules[rule_id] = rh
        return rh

    def record_trigger(self, rule_id: str) -> None:
        if rule_id in self._rules:
            self._rules[rule_id].last_triggered = datetime.now(timezone.utc).isoformat()
            self._rules[rule_id].trigger_count += 1

    def detect_zombies(self) -> list[RuleHealth]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=self._ZOMBIE_DAYS)
        zombies: list[RuleHealth] = []
        for rh in self._rules.values():
            if datetime.fromisoformat(rh.last_triggered) < cutoff:
                rh.zombie = True
                zombies.append(rh)
        return zombies

    def check_complexity(self) -> ComplexityBudget:
        current = len(self._rules)
        return ComplexityBudget(current=current, exceeded=current > 30)

    def get_dashboard(self, denied_last_24h: int = 0, emergency_tokens_active: int = 0) -> OwnerDashboard:
        zombies = self.detect_zombies()
        complexity = self.check_complexity()
        return OwnerDashboard(
            active_rules=len(self._rules),
            zombie_rules=len(zombies),
            complexity_pct=complexity.current / max(complexity.max_complexity, 1),
            denied_last_24h=denied_last_24h,
            emergency_tokens_active=emergency_tokens_active,
        )
