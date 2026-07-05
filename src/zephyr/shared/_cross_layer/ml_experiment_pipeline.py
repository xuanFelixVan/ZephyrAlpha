# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.shared._cross_layer.ml_experiment_pipeline
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.ml_train.inference_base; zephyr.ml_train.trainer_base; zephyr.simulation.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_ml_experiment_pipeline | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""MLExperimentPipeline D_ML_TRAIN→实验跨层集成管道
============================================
Domain   : _ml-experiment-domain (ML-EXPERIMENT-DOMAIN-001)
Contracts: ME-CT-001~006
Layers   : D_ML_TRAIN (MLPlatform/Inference) → 实验 (Experimentation/Pipeline)
Status   : Phase B — 骨架管道已就绪，底层C轨模块 blocked_by_infrastructure

管线阶段
--------
Stage 1: ModelDiscovery     — 发现已注册模型+版本
Stage 2: InferenceExec      — 并行执行模型推理
Stage 3: MetricCollection   — 收集实验指标
Stage 4: StatisticsValidate — 显著性检验+效应量计算
Stage 5: ProductionPromote  — 胜出模型提升至生产

ME-CT 契约覆盖
---------------
ME-CT-001: ModelServing 生命周期管理
ME-CT-002: 推理幂等性保证
ME-CT-003: 实验指标标准化契约
ME-CT-004: 统计验证门禁
ME-CT-005: 模型提升审批链
ME-CT-006: 跨层审计追踪
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

_MAX_WORKERS = 8

__all__ = [
    "ExperimentResult",
    "MLExperimentPipeline",
    "PipelineError",
    "PipelineStage",
]

try:
    from zephyr.ml_train.inference_base import InferenceEngineBase
    from zephyr.ml_train.trainer_base import ModelMetadata, ModelTrainerBase
    from zephyr.simulation.pipeline_base import (
        ExperimentConfig,
        ExperimentMetric,
        ExperimentPipelineBase,
    )

    _CONTRACTS_AVAILABLE = True
except ImportError:
    _CONTRACTS_AVAILABLE = False


class PipelineStage(Enum):
    MODEL_DISCOVERY = "model_discovery"
    INFERENCE_EXEC = "inference_exec"
    METRIC_COLLECTION = "metric_collection"
    STATISTICS_VALIDATE = "statistics_validate"
    PRODUCTION_PROMOTE = "production_promote"


class PipelineError(Exception):
    def __init__(self, stage: PipelineStage, message: str, detail: dict[str, Any] | None = None) -> None:
        self.stage = stage
        self.message = message
        self.detail = detail or {}
        super().__init__(f"[{stage.value}] {message}")


@dataclass
class ExperimentResult:
    pipeline_id: str
    status: str
    stage: PipelineStage
    models_discovered: int = 0
    inferences_run: int = 0
    inferences_failed: int = 0
    metrics_collected: int = 0
    significant_results: int = 0
    best_model: str | None = None
    best_effect_size: float = 0.0
    promoted: bool = False
    errors: list[dict[str, Any]] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: str | None = None
    idempotency_key: str = field(default_factory=lambda: str(uuid.uuid4()))


class MLExperimentPipeline:
    """D_ML_TRAIN→实验 ML Experiment 跨层集成管道。

    将 D_ML_TRAIN ML平台层的模型推理结果输入 实验 实验管线，
    执行实验设计、统计验证和胜出模型提升。
    """

    _global_run_count: int = 0
    _seen_idempotency_keys: set[str] = set()
    _MAX_RUNS_BEFORE_P_HACKING_WARNING = 9
    # 5.12.10 修复：移除 _BUILTINS_GUARD_ENABLED = True 死分支（flag永远True，else路径不可达）

    def __init__(self) -> None:
        self._models: list[ModelMetadata] = []
        self._engines: list[type] = []
        self._experiment_config: ExperimentConfig | None = None

    @staticmethod
    def _snapshot_builtins() -> frozenset[str]:
        try:
            import builtins

            return frozenset(builtins.__dict__.keys())
        except Exception:
            return frozenset()

    @staticmethod
    def _check_builtins_integrity(snapshot: frozenset[str]) -> list[str]:
        violations: list[str] = []
        try:
            import builtins

            current = set(builtins.__dict__.keys())
            added = current - snapshot
            if added:
                violations.append(f"builtins keys added: {sorted(added)}")
        except Exception as e:
            violations.append(f"builtins guard error: {e}")
        return violations

    def register_model(self, model_meta: ModelMetadata) -> None:
        self._models.append(model_meta)

    def register_engine(self, engine_cls: type) -> None:
        self._engines.append(engine_cls)

    def set_experiment_config(self, config: ExperimentConfig) -> None:
        self._experiment_config = config

    def run(
        self,
        features: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> ExperimentResult:
        key = idempotency_key or str(uuid.uuid4())
        MLExperimentPipeline._seen_idempotency_keys.add(key)
        MLExperimentPipeline._global_run_count += 1

        if MLExperimentPipeline._global_run_count > MLExperimentPipeline._MAX_RUNS_BEFORE_P_HACKING_WARNING:
            result = ExperimentResult(
                pipeline_id=str(uuid.uuid4())[:8],
                status="p_hacking_warning",
                stage=PipelineStage.STATISTICS_VALIDATE,
                idempotency_key=key,
                significant_results=MLExperimentPipeline._global_run_count,
                promoted=True,
                errors=[
                    {
                        "stage": "p_hacking_detection",
                        "message": (
                            f"Potential p-hacking: {MLExperimentPipeline._global_run_count} experiment runs "
                            f"detected across {len(MLExperimentPipeline._seen_idempotency_keys)} unique keys "
                            f"(threshold: {MLExperimentPipeline._MAX_RUNS_BEFORE_P_HACKING_WARNING})"
                        ),
                    }
                ],
            )
            result.completed_at = datetime.utcnow().isoformat()
            return result

        result = ExperimentResult(
            pipeline_id=str(uuid.uuid4())[:8],
            status="running",
            stage=PipelineStage.MODEL_DISCOVERY,
            idempotency_key=key,
        )

        if not _CONTRACTS_AVAILABLE:
            result.errors.append(
                {
                    "stage": "preflight",
                    "message": "D_ML_TRAIN/实验 contracts unavailable — running in degraded mode",
                }
            )

        result.stage = PipelineStage.MODEL_DISCOVERY
        if not self._models:
            try:
                from zephyr.ml_train.trainer_base import ModelTrainerBase as MTB

                registry = getattr(MTB, "_registry", {})
                discovered = [
                    ModelMetadata(
                        model_id=name,
                        model_version="latest",
                        model_type="unknown",
                        framework="unknown",
                        features=[],
                        target="unknown",
                    )
                    for name in registry
                ]
                self._models = discovered
            except Exception:
                self._models = []

        result.models_discovered = len(self._models)
        if not self._models:
            result.status = "no_models"
            result.errors.append(
                {
                    "stage": PipelineStage.MODEL_DISCOVERY.value,
                    "message": "No models discovered or registered",
                }
            )
            return result

        result.stage = PipelineStage.INFERENCE_EXEC
        predictions: list[dict[str, Any]] = []
        test_features = features or {"dummy": [1.0]}

        builtins_snapshot = self._snapshot_builtins()  # 5.12.10 修复：移除死分支条件（guard始终启用）

        with ThreadPoolExecutor(max_workers=min(_MAX_WORKERS, len(self._models))) as executor:
            futures = {}
            for model in self._models:
                engine = self._find_engine(model.model_id)
                if engine:
                    futures[executor.submit(self._run_inference, engine, model, test_features, key)] = (
                        engine.__name__,
                        model.model_id,
                    )

            for future in as_completed(futures):
                try:
                    pred = future.result()
                    # 5.12.10 修复：移除 if self._BUILTINS_GUARD_ENABLED: 死分支（guard始终启用）
                    violations = self._check_and_restore_builtins(builtins_snapshot)
                    if violations:
                        result.inferences_failed += 1
                        result.errors.append(
                            {
                                "stage": PipelineStage.INFERENCE_EXEC.value,
                                "model": futures[future][1],
                                "error": f"BUILTINS TAMPERED AND RESTORED: {violations}",
                            }
                        )
                        continue
                    if pred:
                        predictions.append(pred)
                        result.inferences_run += 1
                except Exception as e:
                    result.inferences_failed += 1
                    result.errors.append(
                        {
                            "stage": PipelineStage.INFERENCE_EXEC.value,
                            "model": futures[future][1],
                            "error": str(e),
                        }
                    )

        if not predictions:
            result.status = "no_predictions"
            return result

        result.stage = PipelineStage.METRIC_COLLECTION
        result.metrics_collected = self._collect_metrics(predictions, result)

        result.stage = PipelineStage.STATISTICS_VALIDATE
        significance = self._run_significance_test(predictions)
        result.significant_results = significance.get("significant_count", 0)
        result.best_model = significance.get("best_model")
        result.best_effect_size = significance.get("best_effect_size", 0.0)

        result.stage = PipelineStage.PRODUCTION_PROMOTE
        result.promoted = result.significant_results > 0 and result.best_effect_size > 0.1
        if not result.promoted:
            result.errors.append(
                {
                    "stage": PipelineStage.PRODUCTION_PROMOTE.value,
                    "message": "No model met promotion threshold",
                    "significant": result.significant_results,
                    "threshold": 0.1,
                }
            )

        result.status = "completed_with_errors" if result.errors else "completed"

        result.completed_at = datetime.utcnow().isoformat()
        return result

    def _find_engine(self, model_id: str) -> type | None:
        matched = [e for e in self._engines if e.__name__ and model_id.lower() in e.__name__.lower()]
        if matched:
            return matched[0]
        try:
            from zephyr.ml_train.inference_base import InferenceEngineBase as IEB

            registry = getattr(IEB, "_registry", {})
            for name, cls in registry.items():
                if model_id.lower() in name.lower():
                    return cls
        except Exception as e:
            logger.warning("suppressed error in ml_experiment_pipeline", exc_info=True)
        return self._engines[0] if self._engines else None

    @staticmethod
    def _run_inference(
        engine_cls: type,
        model: ModelMetadata,
        features: dict[str, Any],
        idempotency_key: str,
    ) -> dict[str, Any] | None:
        engine = engine_cls()
        if hasattr(engine, "predict"):
            prediction = engine.predict(features)
            return {
                "model_id": model.model_id,
                "model_version": model.model_version,
                "prediction": getattr(prediction, "prediction", prediction),
                "confidence": getattr(prediction, "confidence", 0.5),
                "key": idempotency_key,
            }
        return None

    def _collect_metrics(self, predictions: list[dict[str, Any]], result: ExperimentResult) -> int:
        count = 0
        for pred in predictions:
            if not pred:
                continue
            try:
                metric = ExperimentMetric(
                    experiment_id=result.pipeline_id,
                    metric_name=f"inference_{pred.get('model_id', 'unknown')}",
                    control_value=0.0,
                    treatment_value=float(pred.get("prediction", 0.0)),
                    effect_size=abs(float(pred.get("prediction", 0.0))),
                    p_value=1.0 - float(pred.get("confidence", 0.5)),
                    is_significant=float(pred.get("confidence", 0.5)) > 0.95,
                )
                if metric.is_significant:
                    result.significant_results += 1
                    if abs(metric.effect_size) > result.best_effect_size:
                        result.best_effect_size = abs(metric.effect_size)
                        result.best_model = pred.get("model_id")
                count += 1
            except Exception as e:
                result.errors.append(
                    {
                        "stage": PipelineStage.METRIC_COLLECTION.value,
                        "model": pred.get("model_id", "unknown"),
                        "error": str(e),
                    }
                )
        return count

    @staticmethod
    def _run_significance_test(predictions: list[dict[str, Any]]) -> dict[str, Any]:
        significant = [p for p in predictions if p.get("confidence", 0) > 0.95]
        best = max(predictions, key=lambda p: abs(float(p.get("prediction", 0.0)))) if predictions else None
        return {
            "significant_count": len(significant),
            "total": len(predictions),
            "best_model": best.get("model_id") if best else None,
            "best_effect_size": abs(float(best.get("prediction", 0.0))) if best else 0.0,
        }


if __name__ == "__main__":
    import json as _json

    pipe = MLExperimentPipeline()
    result = pipe.run()
    print(
        _json.dumps(
            {
                "status": result.status,
                "models_discovered": result.models_discovered,
                "inferences_run": result.inferences_run,
                "significant_results": result.significant_results,
                "promoted": result.promoted,
                "errors": result.errors,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
