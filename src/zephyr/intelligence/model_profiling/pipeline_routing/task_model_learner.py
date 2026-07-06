# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md
# [MODULE] zephyr.intelligence.model_profiling.pipeline_routing.task_model_learner
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.integration.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RSC_task_model_learner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ModelTaskMatrix — 任务×模型性能学习引擎
==========================================
增量学习每个任务类型在每个模型上的表现，逐步收敛到最优任务→模型映射。

数据结构
--------
{
  "M3_code_generation": {
    "qwen3:8b": {
      "sample_count": 42,
      "avg_duration_ms": 850.3,
      "avg_tokens_per_sec": 72.1,
      "avg_confidence": 0.87,
      "composite_score": 0.76,
      "last_updated": "2026-05-08T12:00:00"
    },
    ...
  },
  ...
}

推荐算法
--------
composite_score = speed_norm * 0.40 + quality_norm * 0.35 + consistency_norm * 0.25
  speed_norm     = min(throughput / THROUGHPUT_MAX, 1.0)
  quality_norm   = avg_confidence
  consistency_norm = 1.0 - stddev / max(mean, 1.0)

推荐策略
--------
- 样本数 >= 3: 用实际运行数据推荐
- 样本数 <  3: 用 benchmark 基准数据兜底
- 样本数 =  0: 返回 static mapping (M_MODULE_SPECS)
"""

from __future__ import annotations

from typing import Final
import json
import logging
import statistics
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)

THROUGHPUT_MAX: Final[float] = 200.0
MIN_SAMPLES_FOR_LEARNED: Final[int] = 3
DEFAULT_STORAGE_DIR: Final[str] = "data/model_learning"


@dataclass
class ModelTaskEntry:
    model_name: str
    sample_count: int = 0
    total_duration_ms: float = 0.0
    total_tokens: int = 0
    total_confidence: float = 0.0
    duration_samples: list[float] = field(default_factory=list)
    confidence_samples: list[float] = field(default_factory=list)
    last_updated: str = ""

    avg_duration_ms: float = 0.0
    avg_tokens_per_sec: float = 0.0
    avg_confidence: float = 0.0
    composite_score: float = 0.0

    def update(self, duration_ms: float, tokens: int, confidence: float) -> None:
        self.sample_count += 1
        self.total_duration_ms += duration_ms
        self.total_tokens += tokens
        self.total_confidence += confidence
        self.duration_samples.append(duration_ms)
        if len(self.duration_samples) > 200:
            self.duration_samples = self.duration_samples[-200:]
        self.confidence_samples.append(confidence)
        if len(self.confidence_samples) > 200:
            self.confidence_samples = self.confidence_samples[-200:]
        self.last_updated = datetime.now(UTC).isoformat()

        self.avg_duration_ms = self.total_duration_ms / self.sample_count
        tps = (self.total_tokens / (self.total_duration_ms / 1000)) if self.total_duration_ms > 0 else 0.0
        self.avg_tokens_per_sec = round(tps, 1)
        self.avg_confidence = round(self.total_confidence / self.sample_count, 4)

        speed_score = min(self.avg_tokens_per_sec / THROUGHPUT_MAX, 1.0)
        quality_score = self.avg_confidence
        dur_std = statistics.stdev(self.duration_samples) if len(self.duration_samples) >= 2 else 0.0
        consistency_score = max(0.0, 1.0 - dur_std / max(self.avg_duration_ms, 1.0))

        self.composite_score = round(speed_score * 0.40 + quality_score * 0.35 + consistency_score * 0.25, 4)


@dataclass
class TaskRecommendation:
    task_type: str
    best_model: str
    score: float
    sample_count: int
    source: str
    alternatives: list[dict[str, Any]] = field(default_factory=list)


class ModelTaskMatrix:
    """任务×模型性能矩阵——增量学习 + 推荐引擎。"""

    def __init__(self, storage_dir: str = DEFAULT_STORAGE_DIR) -> None:
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._matrix: dict[str, dict[str, ModelTaskEntry]] = {}
        self._benchmark_baseline: dict[str, dict[str, float]] = {}
        self._load()

    def record(
        self,
        task_type: str,
        model: str,
        duration_ms: float,
        tokens: int,
        confidence: float = 0.0,
    ) -> None:
        """记录一次任务执行结果——增量学习。"""
        matrix = self._matrix.setdefault(task_type, {})
        entry = matrix.get(model)
        if entry is None:
            entry = ModelTaskEntry(model_name=model)
            matrix[model] = entry
        entry.update(duration_ms, tokens, confidence)
        _log.debug("Learner: %s × %s = %.3f (n=%d)", task_type, model, entry.composite_score, entry.sample_count)

    def recommend(self, task_type: str) -> TaskRecommendation:
        """为指定任务类型推荐最佳模型。"""
        entries = self._matrix.get(task_type, {})

        if entries:
            learned = [(model, e) for model, e in entries.items() if e.sample_count >= MIN_SAMPLES_FOR_LEARNED]
            if learned:
                learned.sort(key=lambda x: x[1].composite_score, reverse=True)
                best_model, best_entry = learned[0]
                alts = [{"model": m, "score": e.composite_score, "samples": e.sample_count} for m, e in learned[1:4]]
                return TaskRecommendation(
                    task_type=task_type,
                    best_model=best_model,
                    score=best_entry.composite_score,
                    sample_count=best_entry.sample_count,
                    source="learned",
                    alternatives=alts,
                )

        baseline = self._benchmark_baseline.get(task_type, {})
        if baseline:
            best = max(baseline.items(), key=lambda x: x[1])
            return TaskRecommendation(
                task_type=task_type,
                best_model=best[0],
                score=best[1],
                sample_count=0,
                source="benchmark_baseline",
            )

        from zephyr.infrastructure.pipeline.models import M_MODULE_SPECS

        spec = M_MODULE_SPECS.get(task_type, {})
        static_model = spec.get("model", "deepseek")
        return TaskRecommendation(
            task_type=task_type,
            best_model=static_model,
            score=0.0,
            sample_count=0,
            source="static_spec",
        )

    def recommend_all(self) -> list[TaskRecommendation]:
        """为所有已知任务类型推荐最佳模型。"""
        from zephyr.infrastructure.pipeline.models import M_MODULES

        results: list[TaskRecommendation] = []
        for module_id in M_MODULES:
            results.append(self.recommend(module_id))
        return results

    def load_benchmark_baseline(self, profiles: list[dict[str, Any]]) -> int:
        """从 ModelProfiler benchmark 结果中播种基准数据。"""
        count = 0
        from zephyr.infrastructure.pipeline.models import M_MODULE_SPECS

        module_to_role = {
            mid: M_MODULE_SPECS.get(mid, {}).get("role", "").split("——")[0].strip()
            if "——" in M_MODULE_SPECS.get(mid, {}).get("role", "")
            else ""
            for mid in M_MODULE_SPECS
        }
        category_to_modules: dict[str, list[str]] = {
            "code_generation": ["M3"],
            "code_fix": ["M4"],
            "semantic": ["M1", "M2"],
            "quality": ["M6", "M7"],
            "reasoning": ["M8", "M9", "M10", "M11"],
            "hallucination": ["M7", "M11"],
        }

        for p in profiles:
            model_name = p.get("model_name", "")
            ts = p.get("task_scores", {})
            if not model_name or not ts:
                continue
            composite = float(ts.get("composite_score", 0.0))
            if composite <= 0:
                continue
            cat_scores = ts
            for cat in category_to_modules:
                cat_score = cat_scores.get(cat, composite)
                if isinstance(cat_score, (int, float)) and cat_score > 0:
                    for module_id in category_to_modules.get(cat, []):
                        self._benchmark_baseline.setdefault(module_id, {})[model_name] = float(cat_score)
                        count += 1
        self._save()
        _log.info("ModelTaskMatrix: loaded %d baseline entries from benchmark", count)
        return count

    def snapshot(self) -> dict[str, Any]:
        """返回完整矩阵快照。"""
        result: dict[str, Any] = {}
        for task_type, models in self._matrix.items():
            result[task_type] = {}
            for model, entry in models.items():
                result[task_type][model] = {
                    "sample_count": entry.sample_count,
                    "avg_duration_ms": round(entry.avg_duration_ms, 1),
                    "avg_tokens_per_sec": entry.avg_tokens_per_sec,
                    "avg_confidence": entry.avg_confidence,
                    "composite_score": entry.composite_score,
                    "last_updated": entry.last_updated,
                }
        return result

    def summary(self) -> str:
        """生成人类可读的摘要。"""
        recs = self.recommend_all()
        learned_count = sum(1 for r in recs if r.source == "learned")
        lines: list[str] = [
            f"ModelTaskMatrix: {len(recs)} task types, {learned_count} learned, {len(recs) - learned_count} from baseline/spec",
        ]
        lines.append(f"  {'Task':<8} {'Best Model':<25} {'Score':>7} {'Samples':>8} {'Source':>12}")
        lines.append(f"  {'-' * 8} {'-' * 25} {'-' * 7} {'-' * 8} {'-' * 12}")
        for r in recs:
            lines.append(f"  {r.task_type:<8} {r.best_model:<25} {r.score:>6.3f} {r.sample_count:>8} {r.source:>12}")
        return "\n".join(lines)

    def persistence_path(self) -> str:
        return str(self._dir / "task-model-matrix.json")

    def _save(self) -> None:
        try:
            data: dict[str, Any] = {
                "matrix": self.snapshot(),
                "benchmark_baseline": self._benchmark_baseline,
                "saved_at": datetime.now(UTC).isoformat(),
            }
            (self._dir / "task-model-matrix.json").write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except Exception as exc:
            _log.debug("ModelTaskMatrix: save failed: %s", exc, exc_info=True)

    def _load(self) -> None:
        path = self._dir / "task-model-matrix.json"
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            self._benchmark_baseline = data.get("benchmark_baseline", {})
            matrix_data = data.get("matrix", {})
            for task_type, models in matrix_data.items():
                for model, vals in models.items():
                    entry = ModelTaskEntry(model_name=model)
                    entry.sample_count = vals.get("sample_count", 0)
                    entry.avg_duration_ms = vals.get("avg_duration_ms", 0.0)
                    entry.avg_tokens_per_sec = vals.get("avg_tokens_per_sec", 0.0)
                    entry.avg_confidence = vals.get("avg_confidence", 0.0)
                    entry.composite_score = vals.get("composite_score", 0.0)
                    entry.last_updated = vals.get("last_updated", "")
                    self._matrix.setdefault(task_type, {})[model] = entry
            _log.info("ModelTaskMatrix: loaded %d task types from disk", len(matrix_data))
        except Exception as exc:
            _log.debug("ModelTaskMatrix: load failed: %s", exc, exc_info=True)
