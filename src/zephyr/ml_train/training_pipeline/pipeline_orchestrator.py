# [BLUEPRINT] MOD-ML-001 | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] zephyr.ml_train.training_pipeline.pipeline_orchestrator
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] zephyr.ml_train.trainer_base
# [CONSUMERS] GAP-F-34/35 训练任务编排；MOD-ML-002 ai_operator（巡检消费运行记录）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 四段顺序 load→train→evaluate→register 不可乱序；register 段只产 candidate 草稿禁直改注册表；失败即短路后续段
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PipelineStageError(ZA-MLT-0004)——请求非法/编排失败时抛；训练器内部错误原样吸收进 result.status=failed
# [TESTS] tests/ml_train/test_training_pipeline.py
# [A_module] module_id=MOD-ML-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
D_ML_TRAIN — MOD-ML-001 训练管线编排器。

四段顺序编排：load（数据就位校验）→ train（训练器训练）→ evaluate（评估，
无评估集回退训练指标）→ register（产出 model_registry 晋升片段草稿，恒
candidate，由治理流程串行合并，本编排器禁直改注册表）。

红线：全部产物 testing 封顶，禁止生效实盘（B-009）；训练器由调用方注入
（策略×训练解耦，宪章 §3 约束四同构）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: pipeline_orchestrator.py
# 层: 算法
# - id: A1
#   name_zh: ① TrainingPipelineOrchestrator
#   name_en: TrainingPipelineOrchestrator
#   intro: 训练管线编排器（MOD-ML-001）。
#   desc: 训练管线编排器（MOD-ML-001）。 用法:: result = TrainingPipelineOrchestrator().run(request) assert res…；公共方法（定义序）: run；源码…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: TrainingPipelineOrchestrator
#   downstream: GAP-F-34/35 训练任务编排；MOD-ML-002 ai_operator（巡检消费运行记录）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Final

from zephyr.ml_train.trainer_base import ModelTrainerBase

_log = logging.getLogger(__name__)

_STAGES: Final[tuple[str, ...]] = ("load", "train", "evaluate", "register")


class PipelineStageError(Exception):
    """ZA-MLT-0004: 训练管线请求非法/编排失败。"""

    error_code = "ZA-MLT-0004"


@dataclass(frozen=True)
class TrainingPipelineRequest:
    """训练管线请求（参数 >7 收 dataclass，§5.150）。

    Attributes
    ----------
    pipeline_id : 管线运行标识（幂等追溯用）。
    trainer : 注入的训练器（ModelTrainerBase 实现，如 DensityQuantileTrainer）。
    train_features / train_target : 训练集。
    eval_features / eval_target : 评估集（可空——空则评估段回退训练指标）。
    idempotency_key : 幂等键（INV-007）。
    """

    pipeline_id: str
    trainer: ModelTrainerBase
    train_features: dict[str, Any]
    train_target: object
    eval_features: dict[str, Any] | None
    eval_target: object
    idempotency_key: str


@dataclass(frozen=True)
class TrainingPipelineResult:
    """训练管线运行结果。"""

    pipeline_id: str
    status: str  # completed / failed
    stages: tuple[str, ...]  # 实际完成的段（顺序）
    train_metrics: dict[str, float]
    eval_metrics: dict[str, float]
    registry_draft: dict[str, Any]
    failed_stage: str = ""
    error: str = ""
    finished_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class TrainingPipelineOrchestrator:
    """训练管线编排器（MOD-ML-001）。

    用法::

        result = TrainingPipelineOrchestrator().run(request)
        assert result.status == "completed"
        draft = result.registry_draft  # model_registry 晋升片段草稿
    """

    def run(self, request: TrainingPipelineRequest) -> TrainingPipelineResult:
        """执行四段编排。训练器内部异常吸收为 status=failed（不抛出）。"""
        self._validate_request(request)
        done: list[str] = []

        # ── 段 1: load（数据就位校验）──
        load_err = self._check_load(request)
        if load_err:
            return self._failed(request, done, "load", load_err)
        done.append("load")

        # ── 段 2: train ──
        try:
            train_metrics = request.trainer.train(request.train_features, request.train_target, request.idempotency_key)
        except Exception as exc:  # noqa: BLE001 — 训练器错误吸收进结果（留痕不炸编排）
            return self._failed(request, done, "train", str(exc))
        done.append("train")

        # ── 段 3: evaluate（无评估集回退训练指标）──
        try:
            if request.eval_features is None or request.eval_target is None:
                eval_metrics = dict(train_metrics)
            else:
                eval_metrics = request.trainer.validate(request.eval_features, request.eval_target)
        except Exception as exc:  # noqa: BLE001
            return self._failed(request, done, "evaluate", str(exc), train_metrics)
        done.append("evaluate")

        # ── 段 4: register（只产 candidate 草稿，禁直改注册表）──
        try:
            draft = self._build_registry_draft(request, eval_metrics)
        except Exception as exc:  # noqa: BLE001
            return self._failed(request, done, "register", str(exc), train_metrics, eval_metrics)
        done.append("register")

        _log.info("管线完成: %s stages=%s", request.pipeline_id, done)
        return TrainingPipelineResult(
            pipeline_id=request.pipeline_id,
            status="completed",
            stages=tuple(done),
            train_metrics=train_metrics,
            eval_metrics=eval_metrics,
            registry_draft=draft,
        )

    # ── 内部 ─────────────────────────────────────────────────────────

    def _validate_request(self, request: TrainingPipelineRequest) -> None:
        if request.trainer is None:
            raise PipelineStageError("trainer 缺失（需注入 ModelTrainerBase 实现）")
        if not request.pipeline_id:
            raise PipelineStageError("pipeline_id 为空")
        if not request.idempotency_key:
            raise PipelineStageError("idempotency_key 为空（INV-007）")

    def _check_load(self, request: TrainingPipelineRequest) -> str:
        if not request.train_features:
            return "train_features 为空"
        if request.train_target is None:
            return "train_target 缺失"
        return ""

    def _build_registry_draft(self, request: TrainingPipelineRequest, eval_metrics: dict[str, float]) -> dict[str, Any]:
        trainer = request.trainer
        if hasattr(trainer, "build_registry_entry"):
            return trainer.build_registry_entry(metrics=eval_metrics)  # type: ignore[no-any-return]
        # 通用回退：无定制草稿接口的训练器产最小 candidate 草稿
        return {
            "model_id": getattr(trainer, "__model_id__", "UNKNOWN"),
            "eval_metrics": dict(eval_metrics),
            "promotion_stage": "candidate",
            "status": "candidate",
        }

    def _failed(
        self,
        request: TrainingPipelineRequest,
        done: list[str],
        stage: str,
        error: str,
        train_metrics: dict[str, float] | None = None,
        eval_metrics: dict[str, float] | None = None,
    ) -> TrainingPipelineResult:
        _log.error("管线失败: %s stage=%s err=%s", request.pipeline_id, stage, error)
        return TrainingPipelineResult(
            pipeline_id=request.pipeline_id,
            status="failed",
            stages=tuple(done),
            train_metrics=train_metrics or {},
            eval_metrics=eval_metrics or {},
            registry_draft={},
            failed_stage=stage,
            error=error,
        )


__all__ = [
    "PipelineStageError",
    "TrainingPipelineOrchestrator",
    "TrainingPipelineRequest",
    "TrainingPipelineResult",
]
