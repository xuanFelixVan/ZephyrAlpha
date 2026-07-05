# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.budget_tracker
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.governance.ops_governance.budget_models
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
# [A_module] module_id=MOD-RES_budget_tracker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import time
from dataclasses import dataclass, field
from enum import Enum

from .budget_models import BudgetDimension


def __getattr__(name):
    if name == "RollbackBudgetTracker":
        from zephyr.infrastructure.rollback.budget_tracker import RollbackBudgetTracker

        return RollbackBudgetTracker
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


class TrackerScope(Enum):
    GLOBAL = "global"
    SESSION = "session"
    TASK = "task"
    TURN = "turn"
    REQUEST = "request"


@dataclass
class BudgetSnapshot:
    scope: TrackerScope
    scope_id: str
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    wall_time_seconds: float = 0.0
    created_at: float = field(default_factory=time.time)
    ttl: float | None = None

    @property
    def total_tokens(self) -> int:
        return self.tokens_in + self.tokens_out

    def is_expired(self) -> bool:
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    def to_dict(self) -> dict:
        return {
            "scope": self.scope.value,
            "scope_id": self.scope_id,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "total_tokens": self.total_tokens,
            "cost_usd": round(self.cost_usd, 6),
            "wall_time_seconds": round(self.wall_time_seconds, 2),
            "created_at": self.created_at,
        }


@dataclass
class TrackerSummary:
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    total_wall_time: float = 0.0
    request_count: int = 0
    turn_count: int = 0
    active_sessions: int = 0
    by_scope: dict[str, BudgetSnapshot] = field(default_factory=dict)
    dimension_usage: dict[str, float] = field(default_factory=dict)

    def usage_ratio(self, dimension: BudgetDimension, limit: int) -> float:
        usage = self.dimension_usage.get(dimension.value, 0.0)
        if limit == 0:
            return 1.0
        return min(usage / limit, 1.0)


class BudgetTracker:
    def __init__(self):
        self._snapshots: dict[tuple[TrackerScope, str], BudgetSnapshot] = {}
        self._requests: list[BudgetSnapshot] = []
        self._turns: list[BudgetSnapshot] = []
        self._start_time: float = time.time()
        self._ttl_map: dict[TrackerScope, float] = {
            TrackerScope.REQUEST: 300,
            TrackerScope.TURN: 900,
            TrackerScope.TASK: 7200,
            TrackerScope.SESSION: 86400,
        }

    def open_scope(self, scope: TrackerScope, scope_id: str) -> BudgetSnapshot:
        key = (scope, scope_id)
        if key in self._snapshots:
            return self._snapshots[key]
        ttl = self._ttl_map.get(scope)
        snap = BudgetSnapshot(scope=scope, scope_id=scope_id, ttl=ttl)
        self._snapshots[key] = snap
        return snap

    def record_request(
        self,
        scope: TrackerScope,
        scope_id: str,
        tokens_in: int,
        tokens_out: int,
        cost_usd: float = 0.0,
        wall_time: float = 0.0,
    ) -> BudgetSnapshot:
        snap = self.open_scope(scope, scope_id)
        snap.tokens_in += tokens_in
        snap.tokens_out += tokens_out
        snap.cost_usd += cost_usd
        snap.wall_time_seconds += wall_time
        self._requests.append(
            BudgetSnapshot(
                scope=TrackerScope.REQUEST,
                scope_id=f"{scope_id}-req-{len(self._requests)}",
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost_usd=cost_usd,
                wall_time_seconds=wall_time,
                ttl=self._ttl_map.get(TrackerScope.REQUEST),
            )
        )
        return snap

    def record_turn(self, turn_id: str, snapshots: list[BudgetSnapshot]) -> BudgetSnapshot:
        total_in = sum(s.tokens_in for s in snapshots)
        total_out = sum(s.tokens_out for s in snapshots)
        total_cost = sum(s.cost_usd for s in snapshots)
        total_time = sum(s.wall_time_seconds for s in snapshots)
        turn = BudgetSnapshot(
            scope=TrackerScope.TURN,
            scope_id=turn_id,
            tokens_in=total_in,
            tokens_out=total_out,
            cost_usd=total_cost,
            wall_time_seconds=total_time,
            ttl=self._ttl_map.get(TrackerScope.TURN),
        )
        self._turns.append(turn)
        return turn

    def get_snapshot(self, scope: TrackerScope, scope_id: str) -> BudgetSnapshot | None:
        return self._snapshots.get((scope, scope_id))

    def summarize(self) -> TrackerSummary:
        self._cleanup_expired()
        summary = TrackerSummary()
        for (scope, sid), snap in self._snapshots.items():
            summary.total_tokens += snap.total_tokens
            summary.total_cost_usd += snap.cost_usd
            summary.total_wall_time += snap.wall_time_seconds
            summary.by_scope[f"{scope.value}:{sid}"] = snap
            if scope is TrackerScope.REQUEST:
                summary.request_count += 1
            elif scope is TrackerScope.SESSION:
                summary.active_sessions += 1
        summary.turn_count = len(self._turns)
        summary.dimension_usage = {
            BudgetDimension.TOKEN.value: summary.total_tokens,
            BudgetDimension.COST.value: summary.total_cost_usd,
            BudgetDimension.TIME.value: summary.total_wall_time,
        }
        return summary

    def dimension_usage(self, dimension: BudgetDimension) -> float:
        s = self.summarize()
        return s.dimension_usage.get(dimension.value, 0.0)

    def elapsed(self) -> float:
        return time.time() - self._start_time

    def _cleanup_expired(self) -> None:
        expired = [k for k, s in self._snapshots.items() if s.is_expired()]
        for k in expired:
            del self._snapshots[k]

    def dump(self) -> str:
        return json.dumps(
            {
                "summary": self.summarize().__dict__,
                "snapshots": {f"{k[0].value}:{k[1]}": v.to_dict() for k, v in self._snapshots.items()},
                "elapsed": round(self.elapsed(), 2),
            },
            indent=2,
            default=str,
        )

    def clear(self) -> None:
        self._snapshots.clear()
        self._requests.clear()
        self._turns.clear()
        self._start_time = time.time()


# 代理导出：RollbackBudgetTracker 实际定义在 infrastructure.rollback.budget_tracker
