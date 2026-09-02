# [BLUEPRINT] MOD-ML-012 | docs/03_modules/_domain_machine_learning_train/model_version_registry/blueprint.md
# [MODULE] zephyr.ml_train.core.model_version_registry
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 运行时装配批（训练完成/验证完成事件外发；激活门禁消费）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 阶段机 TRAINED→VALIDATED→SHADOW_VERIFIED→ACTIVATED→DEPRECATED(终态)；VALIDATED须非空有限metrics；INV-011: 仅SHADOW_VERIFIED可ACTIVATED且须approved_by非空(人工闸门)；每模型同时刻至多一个ACTIVATED；记录frozen；事件经event_sink外发；非法输入Fail-Closed
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ModelVersionRegistryError
# [TESTS] tests/ml_train/test_model_version_registry.py
# [A_module] module_id=MOD-ML-012 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""Model Version Registry — 训练域 Model 聚合 + 版本生命周期 + INV-011 影子验证门 (MOD-ML-012, CAND-MLT-016, B4-06880)

AGG-008 Model 聚合 + ENT-006 ModelVersion 实体：模型版本五阶段状态机
（TRAINED→VALIDATED→SHADOW_VERIFIED→ACTIVATED→DEPRECATED），E-ML-01
ModelTrained / E-RS-03 ModelValidated 事件经 event_sink 外发；INV-011 门禁——
TRAIN 产出模型必须经影子验证（SHADOW_VERIFIED）且获人工批准后方可 ACTIVATED
进 Warm。

与既有件分工（蓝图 §0 查重裁定）：trainer_base.ModelRegistry=训练器**类**注册
（OCP 扩展点）；experiment_tracking=实验运行记录；gray_release_shadow_deployer
=影子部署执行面（本件消费其结论作 shadow_proof 注入，不 import）；factor_factory
=因子发现流水线。本件为模型版本实例聚合与生命周期判定核心，口径互不重复。

纪律：纯内存实现无 IO；影子证明/批准人由调用方注入（不越域取数）；事件外发经
event_sink 回调（落账委托装配批）。

依据: blueprint.md（MOD-ML-012）§1 规则
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模型标识 + 版本
#   fields: model_id/version 非空字符串
#   code: register_trained() 等公开方法参数
# - id: I2
#   name: 验证/影子/批准证据
#   fields: validation_metrics 非空有限; shadow_proof 非空; approved_by 非空
#   code: record_validated/record_shadow_verified/activate 参数
# 层: 算法
# - id: A1
#   name_zh: ① 阶段机推进（Fail-Closed）
#   name_en: _transition
#   intro: 合法迁移表校验；DEPRECATED 终态拒绝一切再迁移
# - id: A2
#   name_zh: ② INV-011 门禁
#   name_en: activate
#   intro: 仅 SHADOW_VERIFIED→ACTIVATED；同模型已有 ACTIVATED 版本拒绝并存
# - id: A3
#   name_zh: ③ 事件外发
#   name_en: _emit
#   intro: ModelTrained/ModelValidated 事件经 event_sink 回调
# 层: 输出
# - id: O1
#   name: ModelVersionRecord
#   fields: 版本 frozen 快照（stage/metrics/时间戳/lineage）
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A1 --> A3
# A2 --> O1
# A3 --> O1
# [/ALGO_FLOW]
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "ModelTrainedEvent",
    "ModelValidatedEvent",
    "ModelVersionRecord",
    "ModelVersionRegistry",
    "ModelVersionRegistryError",
    "ModelVersionStage",
]


class ModelVersionRegistryError(ZephyrBaseError):
    """模型版本注册表操作非法（Fail-Closed）。

    错误码占位：ZA-MLT-0014（待主代理统一登记转正，
    建议号段 ZA-MLT-0012；P1W20 建议的 ZA-MLT-0003/0004 与在案码冲突，
    以主代理对账为准）。
    """

    error_code = "ZA-MLT-0014"


class ModelVersionStage(str, Enum):
    """ENT-006 ModelVersion 生命周期阶段。"""

    TRAINED = "TRAINED"
    VALIDATED = "VALIDATED"
    SHADOW_VERIFIED = "SHADOW_VERIFIED"
    ACTIVATED = "ACTIVATED"
    DEPRECATED = "DEPRECATED"


_ALLOWED: Final[dict[ModelVersionStage, frozenset[ModelVersionStage]]] = {
    ModelVersionStage.TRAINED: frozenset({ModelVersionStage.VALIDATED, ModelVersionStage.DEPRECATED}),
    ModelVersionStage.VALIDATED: frozenset({ModelVersionStage.SHADOW_VERIFIED, ModelVersionStage.DEPRECATED}),
    ModelVersionStage.SHADOW_VERIFIED: frozenset({ModelVersionStage.ACTIVATED, ModelVersionStage.DEPRECATED}),
    ModelVersionStage.ACTIVATED: frozenset({ModelVersionStage.DEPRECATED}),
    ModelVersionStage.DEPRECATED: frozenset(),
}


@dataclass(frozen=True)
class ModelTrainedEvent:
    """E-ML-01 ModelTrained 事件（frozen）。"""

    model_id: str
    version: str
    occurred_at: datetime


@dataclass(frozen=True)
class ModelValidatedEvent:
    """E-RS-03 ModelValidated 事件（frozen）。"""

    model_id: str
    version: str
    metrics: Mapping[str, float]
    occurred_at: datetime


@dataclass(frozen=True)
class ModelVersionRecord:
    """ENT-006 ModelVersion 快照（frozen）。"""

    model_id: str
    version: str
    stage: ModelVersionStage
    training_metrics: Mapping[str, float] = field(default_factory=dict)
    validation_metrics: Mapping[str, float] = field(default_factory=dict)
    lineage: Mapping[str, str] = field(default_factory=dict)
    shadow_proof: str = ""
    approved_by: str = ""
    trained_at: datetime | None = None
    validated_at: datetime | None = None
    shadow_verified_at: datetime | None = None
    activated_at: datetime | None = None
    deprecated_at: datetime | None = None


def _require_text(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ModelVersionRegistryError(f"{name} 不能为空字符串")
    return value


def _require_metrics(name: str, metrics: Mapping[str, float]) -> dict[str, float]:
    if not metrics:
        raise ModelVersionRegistryError(f"{name} 不能为空")
    out: dict[str, float] = {}
    for k, v in metrics.items():
        if not k:
            raise ModelVersionRegistryError(f"{name} 指标名不能为空")
        fv = float(v)
        if not math.isfinite(fv):
            raise ModelVersionRegistryError(f"{name}[{k}] 必须为有限值: {v}")
        out[k] = fv
    return out


class ModelVersionRegistry:
    """AGG-008 Model 聚合 + ENT-006 版本生命周期注册表。

    Args:
        event_sink: 事件回调（ModelTrained/ModelValidated；None=仅返回记录）
        clock: 时间源（测试注入）
    """

    def __init__(
        self,
        event_sink: Callable[[object], None] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._event_sink = event_sink
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._models: dict[str, dict[str, ModelVersionRecord]] = {}

    # ── 公开 API ──

    def register_trained(
        self,
        model_id: str,
        version: str,
        training_metrics: Mapping[str, float] | None = None,
        lineage: Mapping[str, str] | None = None,
    ) -> ModelVersionRecord:
        """登记新训练版本（TRAINED），发 E-ML-01。"""
        model_id = _require_text("model_id", model_id)
        version = _require_text("version", version)
        tm = dict(training_metrics or {})
        for k, v in tm.items():
            if not math.isfinite(float(v)):
                raise ModelVersionRegistryError(f"training_metrics[{k}] 必须为有限值: {v}")
        bucket = self._models.setdefault(model_id, {})
        if version in bucket:
            raise ModelVersionRegistryError(f"版本已存在: {model_id}@{version}")
        rec = ModelVersionRecord(
            model_id=model_id,
            version=version,
            stage=ModelVersionStage.TRAINED,
            training_metrics=tm,
            lineage=dict(lineage or {}),
            trained_at=self._clock(),
        )
        bucket[version] = rec
        self._emit(ModelTrainedEvent(model_id=model_id, version=version, occurred_at=rec.trained_at))
        return rec

    def record_validated(
        self,
        model_id: str,
        version: str,
        validation_metrics: Mapping[str, float],
    ) -> ModelVersionRecord:
        """TRAINED→VALIDATED（须非空有限验证指标），发 E-RS-03。"""
        vm = _require_metrics("validation_metrics", validation_metrics)
        rec = self._transition(model_id, version, ModelVersionStage.VALIDATED)
        rec = replace(rec, validation_metrics=vm, validated_at=self._clock())
        self._models[model_id][version] = rec
        self._emit(ModelValidatedEvent(model_id=model_id, version=version, metrics=vm, occurred_at=rec.validated_at))
        return rec

    def record_shadow_verified(self, model_id: str, version: str, shadow_proof: str) -> ModelVersionRecord:
        """VALIDATED→SHADOW_VERIFIED（INV-011：影子验证结论注入）。"""
        shadow_proof = _require_text("shadow_proof（INV-011 影子验证证明）", shadow_proof)
        rec = self._transition(model_id, version, ModelVersionStage.SHADOW_VERIFIED)
        rec = replace(rec, shadow_proof=shadow_proof, shadow_verified_at=self._clock())
        self._models[model_id][version] = rec
        return rec

    def activate(self, model_id: str, version: str, approved_by: str) -> ModelVersionRecord:
        """SHADOW_VERIFIED→ACTIVATED（INV-011 门 + 人工闸门 + 单激活约束）。"""
        approved_by = _require_text("approved_by（严禁全自动上线）", approved_by)
        active = self.active_version(model_id)
        if active is not None and active.version != version:
            raise ModelVersionRegistryError(f"模型 {model_id!r} 已有激活版本 {active.version!r}（须先 deprecate）")
        rec = self._transition(model_id, version, ModelVersionStage.ACTIVATED)
        rec = replace(rec, approved_by=approved_by, activated_at=self._clock())
        self._models[model_id][version] = rec
        return rec

    def deprecate(self, model_id: str, version: str, reason: str) -> ModelVersionRecord:
        """任意非终态→DEPRECATED（终态不可逆）。"""
        reason = _require_text("reason", reason)
        rec = self._transition(model_id, version, ModelVersionStage.DEPRECATED)
        rec = replace(rec, deprecated_at=self._clock())
        self._models[model_id][version] = rec
        return rec

    def get(self, model_id: str, version: str) -> ModelVersionRecord:
        try:
            return self._models[model_id][version]
        except KeyError:
            raise ModelVersionRegistryError(f"未知版本: {model_id}@{version}") from None

    def active_version(self, model_id: str) -> ModelVersionRecord | None:
        for rec in self._models.get(model_id, {}).values():
            if rec.stage is ModelVersionStage.ACTIVATED:
                return rec
        return None

    def list_versions(self, model_id: str) -> list[ModelVersionRecord]:
        return [self._models[model_id][v] for v in sorted(self._models.get(model_id, {}))]

    # ── 内部 ──

    def _transition(self, model_id: str, version: str, to: ModelVersionStage) -> ModelVersionRecord:
        rec = self.get(model_id, version)
        if to not in _ALLOWED[rec.stage]:
            raise ModelVersionRegistryError(f"非法阶段迁移: {model_id}@{version} {rec.stage.value}→{to.value}")
        return replace(rec, stage=to)

    def _emit(self, event: object) -> None:
        if self._event_sink is not None:
            self._event_sink(event)
