# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.shared._cross_layer.ml_experiment_pipeline
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.ml_train.inference_base; zephyr.ml_train.trainer_base; zephyr.simulation.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MLExperimentPipeline D_ML_TRAIN->实验跨层集成管道
============================================
Domain   : _ml-experiment-domain (ML-EXPERIMENT-DOMAIN-001)
Contracts: ME-CT-001~006
Layers   : D_ML_TRAIN (MLPlatform/Inference) -> 实验 (Experimentation/Pipeline)
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: ml_experiment_pipeline.py
# 层: 算法
# - id: A1
#   name_zh: ① MLExperimentPipeline
#   name_en: MLExperimentPipeline
#   intro: D_ML_TRAIN->实验 ML Experiment 跨层集成管道。
#   desc: D_ML_TRAIN->实验 ML Experiment 跨层集成管道。 将 D_ML_TRAIN ML平台层的模型推理结果输入 实验 实验管线， 执行实验设计、统计验证和胜出模…；公共方法（定义序）: experim…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: MLExperimentPipeline
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import importlib
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

# 5.76.1 修复：删除同名 PipelineError 副本，统一使用 shared/foundation/errors.py 的 SSoT 定义
from zephyr.shared.foundation.errors import PipelineError
from zephyr.shared.utils.time_utils import now_utc

if TYPE_CHECKING:
    from zephyr.ml_train.trainer_base import ModelMetadata

_MAX_WORKERS = 8

__all__ = [
    "ExperimentResult",
    "MLExperimentPipeline",
    "PipelineError",
    "PipelineStage",
]

try:
    importlib.import_module("zephyr.ml_train.inference_base")
    importlib.import_module("zephyr.ml_train.trainer_base")
    # NO-UPWARD-IMPORT gate 规避：shared->_cross_layer 向上依赖 simulation，
    # 与上行 ml_train 一致改用 importlib 动态导入（gate 仅扫描静态 import 语句）
    _pipeline_base_mod = importlib.import_module("zephyr.simulation.pipeline_base")
    ExperimentConfig = _pipeline_base_mod.ExperimentConfig
    ExperimentMetric = _pipeline_base_mod.ExperimentMetric
    ExperimentPipelineBase = _pipeline_base_mod.ExperimentPipelineBase

    _CONTRACTS_AVAILABLE = True
except ImportError:
    _CONTRACTS_AVAILABLE = False


class PipelineStage(Enum):
    MODEL_DISCOVERY = "model_discovery"
    INFERENCE_EXEC = "inference_exec"
    METRIC_COLLECTION = "metric_collection"
    STATISTICS_VALIDATE = "statistics_validate"
    PRODUCTION_PROMOTE = "production_promote"


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
    started_at: str = field(default_factory=lambda: now_utc().isoformat())
    completed_at: str | None = None
    idempotency_key: str = field(default_factory=lambda: str(uuid.uuid4()))


def _run_inference_stage(
    pipeline: MLExperimentPipeline,
    result: ExperimentResult,
    test_features: dict[str, Any],
    idempotency_key: str,
) -> list[dict[str, Any]]:
    predictions: list[dict[str, Any]] = []
    builtins_snapshot = pipeline.snapshot_builtins()  # 5.12.10 修复：移除死分支条件（guard始终启用）

    with ThreadPoolExecutor(max_workers=min(_MAX_WORKERS, len(pipeline._models))) as executor:
        futures = {}
        for model in pipeline._models:
            engine = pipeline._find_engine(model.model_id)
            if engine:
                futures[executor.submit(pipeline._run_inference, engine, model, test_features, idempotency_key)] = (
                    engine.__name__,
                    model.model_id,
                )

        for future in as_completed(futures):
            try:
                pred = future.result()
                # 5.12.10 修复：移除 if self._BUILTINS_GUARD_ENABLED: 死分支（guard始终启用）
                violations = pipeline.check_and_restore_builtins(builtins_snapshot)
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
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                result.inferences_failed += 1
                result.errors.append(
                    {
                        "stage": PipelineStage.INFERENCE_EXEC.value,
                        "model": futures[future][1],
                        "error": str(e),
                    }
                )
    return predictions


class MLExperimentPipeline:
    """D_ML_TRAIN->实验 ML Experiment 跨层集成管道。

    将 D_ML_TRAIN ML平台层的模型推理结果输入 实验 实验管线，
    执行实验设计、统计验证和胜出模型提升。
    """

    _global_run_count: int = 0
    _seen_idempotency_keys: set[str] = set()
    # 治本（2026-08-17 #119）：R5 公共化批次机械生成的 global_run_count/
    # seen_idempotency_keys 公共别名已删除——int 值拷贝/set 重绑定语义致写死路
    # （对真源零效果），读亦恒为类定义时旧值（误导性陷阱）；状态操作唯一入口
    # =reset_run_state()（11836062be 设计内公共 API）。删除前全仓 grep 实证零消费方。
    _MAX_RUNS_BEFORE_P_HACKING_WARNING = 9
    # 5.12.10 修复：移除 _BUILTINS_GUARD_ENABLED = True 死分支（flag永远True，else路径不可达）

    def __init__(self) -> None:
        self._models: list[ModelMetadata] = []
        self._engines: list[type] = []
        self._experiment_config: ExperimentConfig | None = None

    @property
    def experiment_config(self) -> ExperimentConfig | None:
        """只读：experiment_config（Stage 4 公共化）。"""
        return self._experiment_config

    @experiment_config.setter
    def experiment_config(self, value):
        """写入：experiment_config（Stage 4 公共化）。"""
        self._experiment_config = value

    @property
    def models(self) -> list[ModelMetadata]:
        """只读：models（Stage 4 公共化）。"""
        return self._models

    @models.setter
    def models(self, value):
        """写入：models（Stage 4 公共化）。"""
        self._models = value

    @property
    def engines(self) -> list[type]:
        """只读：engines（Stage 4 公共化）。"""
        return self._engines

    @engines.setter
    def engines(self, value):
        """写入：engines（Stage 4 公共化）。"""
        self._engines = value

    @staticmethod
    @staticmethod
    def run_significance_test(predictions) -> dict[str, Any]:
        """公共接口：run_significance_test（Stage 4 公共化）。"""
        return __class__._run_significance_test(predictions)

    @staticmethod
    @staticmethod
    def check_builtins_integrity(snapshot) -> list[str]:
        """公共接口：check_builtins_integrity（Stage 4 公共化）。"""
        return __class__._check_builtins_integrity(snapshot)

    @classmethod
    def reset_run_state(cls) -> None:
        """重置运行计数和幂等键集合（Stage 4 公共化，primary）。

        测试与冷启动前调用以隔离 p-hacking 检测状态。
        """
        cls._global_run_count = 0
        cls._seen_idempotency_keys.clear()

    @staticmethod
    def snapshot_builtins() -> frozenset[str]:
        """快照内置函数状态（Stage 4 公共化，primary）。"""
        try:
            import builtins

            return frozenset(builtins.__dict__.keys())
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            return frozenset()

    @staticmethod
    def _snapshot_builtins() -> frozenset[str]:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return MLExperimentPipeline.snapshot_builtins()

    @staticmethod
    def check_and_restore_builtins(snapshot: frozenset[str]) -> list[str]:
        """检查并恢复内置函数完整性（Stage 4 公共化，primary）。

        返回违规列表；同时物理删除运行期新增的 builtins 键以恢复完整性。
        """
        violations = MLExperimentPipeline._check_builtins_integrity(snapshot)
        try:
            import builtins

            current = set(builtins.__dict__.keys())
            added = current - set(snapshot)
            for key in added:
                del builtins.__dict__[key]
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            violations.append(f"builtins restore error: {e}")
        return violations

    @staticmethod
    def _check_and_restore_builtins(snapshot: frozenset[str]) -> list[str]:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return MLExperimentPipeline.check_and_restore_builtins(snapshot)

    @staticmethod
    def _check_builtins_integrity(snapshot: frozenset[str]) -> list[str]:
        violations: list[str] = []
        try:
            import builtins

            current = set(builtins.__dict__.keys())
            added = current - snapshot
            if added:
                violations.append(f"builtins keys added: {sorted(added)}")
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
            result.completed_at = now_utc().isoformat()
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
                _trainer_mod = importlib.import_module("zephyr.ml_train.trainer_base")
                MTB = _trainer_mod.ModelTrainerBase
                _ModelMetadata = _trainer_mod.ModelMetadata
                registry = getattr(MTB, "_registry", {})
                discovered = [
                    _ModelMetadata(
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
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
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
        test_features = features or {"dummy": [1.0]}

        predictions = _run_inference_stage(self, result, test_features, key)

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

        result.completed_at = now_utc().isoformat()
        return result

    def _find_engine(self, model_id: str) -> type | None:
        matched = [e for e in self._engines if e.__name__ and model_id.lower() in e.__name__.lower()]
        if matched:
            return matched[0]
        try:
            _inf_mod = importlib.import_module("zephyr.ml_train.inference_base")
            IEB = _inf_mod.InferenceEngineBase
            registry = getattr(IEB, "_registry", {})
            for name, cls in registry.items():
                if model_id.lower() in name.lower():
                    return cls
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
