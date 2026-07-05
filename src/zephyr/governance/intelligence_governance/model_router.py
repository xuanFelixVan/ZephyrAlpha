# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.intelligence_governance.model_router
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.ops_governance.budget_models; zephyr.intelligence.model_profiling.provider_data; zephyr.intelligence.model_profiling.results_writer
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_model_router | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from zephyr.governance.ops_governance.budget_models import ModelTier

_log = logging.getLogger(__name__)


class TaskComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


TIER_COMPLEXITY_MAP: dict[ModelTier, set[TaskComplexity]] = {
    ModelTier.ECONOMY: {TaskComplexity.SIMPLE, TaskComplexity.MODERATE},
    ModelTier.STANDARD: {TaskComplexity.SIMPLE, TaskComplexity.MODERATE, TaskComplexity.COMPLEX},
    ModelTier.PREMIUM: {TaskComplexity.SIMPLE, TaskComplexity.MODERATE, TaskComplexity.COMPLEX},
}

# performance-aware routing 权重
# cost=0.5, speed=0.35, quality=0.15 → 优先便宜+快，质量作为 tie-breaker
PERF_WEIGHT_COST: float = 0.50
PERF_WEIGHT_SPEED: float = 0.35
PERF_WEIGHT_QUALITY: float = 0.15
# 归一化基准（避免绝对值的尺度差异）
NORM_COST_MAX: float = 0.03
NORM_LATENCY_MAX_MS: float = 10_000.0
NORM_THROUGHPUT_MIN: float = 1.0
NORM_THROUGHPUT_MAX: float = 200.0


@dataclass
class RoutingDecision:
    model_key: str
    provider: str
    tier: ModelTier
    reason: str
    estimated_cost_per_1k: tuple[float, float] = (0.0, 0.0)
    requires_owner: bool = False
    performance_score: float = 0.0
    benchmark_available: bool = False


@dataclass
class ModelRouter:
    _blacklist: set[str] = field(default_factory=set)
    _benchmark_profiles: dict[str, dict[str, Any]] = field(default_factory=dict)
    _perf_weight_cost: float = PERF_WEIGHT_COST
    _perf_weight_speed: float = PERF_WEIGHT_SPEED
    _perf_weight_quality: float = PERF_WEIGHT_QUALITY

    def load_benchmark_profiles(
        self,
        profiles: list[dict[str, Any]],
    ) -> int:
        """加载 ModelProfiler 产出的 benchmark 结果。

        从 ModelProfiler.profile_ollama_only() →
        to_model_benchmark_result() → 传入此方法。
        返回加载的 profile 数量。
        """
        count = 0
        for p in profiles:
            name = p.get("model_name", "")
            if not name:
                continue
            self._benchmark_profiles[name] = p
            count += 1
        _log.info("ModelRouter: loaded %d benchmark profiles", count)
        return count

    def load_benchmark_from_disk(self, results_dir: str = "data/model_profiles") -> int:
        """从磁盘加载最近的 benchmark 结果。"""
        try:
            from zephyr.intelligence.model_profiling.results_writer import load_benchmark_history
        except ImportError:
            _log.debug("ModelRouter: model-profiler not available for disk loading")
            return 0

        import json
        from pathlib import Path

        base = Path(results_dir)
        if not base.exists():
            return 0

        newest = sorted(base.glob("benchmark_*.jsonl"), reverse=True)
        if not newest:
            return 0

        profiles: list[dict[str, Any]] = []
        try:
            for line in newest[0].read_text(encoding="utf-8").strip().split("\n"):
                if line.strip():
                    profiles.append(json.loads(line))
        except Exception as exc:
            _log.warning("ModelRouter: failed to load %s: %s", newest[0], exc)
            return 0

        return self.load_benchmark_profiles(profiles)

    def route(
        self,
        complexity: TaskComplexity = TaskComplexity.MODERATE,
        tier: ModelTier | None = None,
        max_cost_per_1k: float = float("inf"),
        prefer_provider: str = "",
    ) -> RoutingDecision:
        effective_tier = tier or self._infer_tier(complexity)
        candidates = self._eligible_models(effective_tier, complexity, max_cost_per_1k)

        if not candidates:
            return RoutingDecision(
                model_key="deepseek:free",
                provider="deepseek",
                tier=ModelTier.ECONOMY,
                reason="fallback-no-eligible",
            )

        if prefer_provider:
            for c in candidates:
                if c[1] == prefer_provider:
                    key, prov = c
                    perf = self._get_perf_score(key)
                    return RoutingDecision(
                        model_key=key,
                        provider=prov,
                        tier=effective_tier,
                        reason=f"preferred-provider:{prefer_provider}",
                        performance_score=perf,
                        benchmark_available=bool(self._benchmark_profiles),
                    )

        key, prov = candidates[0]
        req_owner = effective_tier is ModelTier.PREMIUM
        perf = self._get_perf_score(key)
        has_bench = bool(self._benchmark_profiles)
        reason = f"perf-aware:{effective_tier.value}" if has_bench else f"least-cost-tier:{effective_tier.value}"
        return RoutingDecision(
            model_key=key,
            provider=prov,
            tier=effective_tier,
            reason=reason,
            requires_owner=req_owner,
            performance_score=perf,
            benchmark_available=has_bench,
        )

    def _infer_tier(self, complexity: TaskComplexity) -> ModelTier:
        if complexity is TaskComplexity.SIMPLE:
            return ModelTier.MINIMAL
        if complexity is TaskComplexity.MODERATE:
            return ModelTier.ECONOMY
        return ModelTier.STANDARD

    def _get_perf_score(self, model_key: str) -> float:
        """从 benchmark profiles 中提取某个模型的综合性能分。"""
        bp = self._benchmark_profiles.get(model_key)
        if bp is None:
            return 0.0
        return float(bp.get("task_scores", {}).get("composite_score", 0.0))

    def _compute_composite(
        self,
        full_key: str,
        cost: float,
    ) -> float:
        """计算综合评分 = cost_score * w_cost + speed_score * w_speed + quality_score * w_quality。

        分值越高越好（0.0=最差，1.0=最佳）。
        cost_score 用反向归一化（越便宜越高，所以 1 - cost/NORM_COST_MAX）。
        """
        cost_score = max(0.0, 1.0 - min(cost, NORM_COST_MAX) / NORM_COST_MAX)

        bp = self._benchmark_profiles.get(full_key)
        if bp is None:
            return cost_score * 0.7  # 无 benchmark 时仅靠价格（降权）

        ts = bp.get("task_scores", {})
        p50 = float(ts.get("latency_p50_ms", NORM_LATENCY_MAX_MS))
        throughput = float(ts.get("throughput_tok_per_sec", NORM_THROUGHPUT_MIN))
        quality = float(ts.get("composite_score", 0.0))

        speed_score = max(0.0, 1.0 - min(p50, NORM_LATENCY_MAX_MS) / NORM_LATENCY_MAX_MS)
        throughput_score = min(
            max(0.0, (throughput - NORM_THROUGHPUT_MIN) / (NORM_THROUGHPUT_MAX - NORM_THROUGHPUT_MIN)),
            1.0,
        )
        speed_score = (speed_score + throughput_score) / 2.0

        composite = (
            cost_score * self._perf_weight_cost
            + speed_score * self._perf_weight_speed
            + quality * self._perf_weight_quality
        )
        return round(composite, 4)

    def _eligible_models(
        self,
        tier: ModelTier,
        complexity: TaskComplexity,
        max_cost: float,
    ) -> list[tuple[str, str]]:
        from zephyr.intelligence.model_profiling.provider_data import DEFAULT_PROVIDERS, TIER_MODEL_MAP

        allowed = TIER_COMPLEXITY_MAP.get(tier, set())
        if complexity not in allowed:
            return []

        raw = TIER_MODEL_MAP.get(tier, [])
        candidates: list[tuple[str, str, float, float]] = []
        for full_key in raw:
            if ":" not in full_key:
                continue
            prov, model_name = full_key.split(":", 1)
            if full_key in self._blacklist:
                continue
            prov_cfg = DEFAULT_PROVIDERS.get(prov, {})
            inp = float(prov_cfg.get("price_per_1k_input", 0.0))
            outp = float(prov_cfg.get("price_per_1k_output", 0.0))
            avg = (inp + outp) / 2
            if avg > max_cost:
                continue
            if self._benchmark_profiles:
                composite = self._compute_composite(full_key, avg)
                candidates.append((full_key, prov, avg, composite))
            else:
                candidates.append((full_key, prov, avg, 0.0))

        if self._benchmark_profiles:
            candidates.sort(key=lambda x: x[3], reverse=True)
        else:
            candidates.sort(key=lambda x: x[2])
        return [(c[0], c[1]) for c in candidates]

    @property
    def has_benchmarks(self) -> bool:
        return len(self._benchmark_profiles) > 0

    @property
    def benchmark_count(self) -> int:
        return len(self._benchmark_profiles)

    @property
    def perf_weights(self) -> dict[str, float]:
        return {
            "cost": self._perf_weight_cost,
            "speed": self._perf_weight_speed,
            "quality": self._perf_weight_quality,
        }

    def set_perf_weights(self, cost: float, speed: float, quality: float) -> None:
        total = cost + speed + quality
        self._perf_weight_cost = cost / total
        self._perf_weight_speed = speed / total
        self._perf_weight_quality = quality / total

    def blacklist(self, model_key: str) -> None:
        self._blacklist.add(model_key)

    def unblacklist(self, model_key: str) -> None:
        self._blacklist.discard(model_key)

    def clear_blacklist(self) -> None:
        self._blacklist.clear()

    def all_models(self) -> list[str]:
        from zephyr.intelligence.model_profiling.provider_data import TIER_MODEL_MAP

        result: list[str] = []
        for tier in ModelTier:
            result.extend(TIER_MODEL_MAP.get(tier, []))
        return result
