# [BLUEPRINT] MOD-ML-013 | docs/03_modules/_domain_machine_learning_train/ml_model_factory/blueprint.md
# [MODULE] zephyr.ml_train.ml_model_factory
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] 无（协议核心纯内存；clock/robustness_validator/gray_orchestrator/gpu_scheduler 全注入）
# [CONSUMERS] 运行时装配批（模型注册/晋级编排/训练提交统一注入点装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 生命周期状态机 dev→candidate→staging→production→retired 词表闭合; 回退仅 production→staging / staging→candidate; 晋级 production 强制对抗鲁棒门禁(未注入/不过 Fail-Closed 禁上线)+灰度编排注入(未注入 Fail-Closed); GPU 训练提交强制注入 scheduler(未注入 Fail-Closed); 重复注册拒绝; 迁移历史留痕; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_machine_learning_train/ml_model_factory/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] MlModelFactoryError(占位 ZA-MLT-UNREGISTERED-MODEL-FACTORY)——空名称/重复注册/未知模型/非法状态迁移/门禁未注入或不过/scheduler缺失时抛
# [TESTS] tests/ml_train/test_ml_model_factory.py
# [A_module] module_id=MOD-ML-013 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""MlModelFactory — ML 模型工厂（MOD-ML-013）。

B1-00253（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLT-017，C2 C-029）：
**模型注册表**（名称/版本/元数据）+ **全生命周期状态机**
（dev→candidate→staging→production→retired，含回退）+ **灰度发布编排**
（挂 gray_release_shadow_deployer 语义注入回调）+ **对抗鲁棒门禁**
（注入 validator，不过禁上线）+ **GPU 任务队列整合**（注入 scheduler）。

查重分工（蓝图 §0）：model_version_registry=版本登记表（本件=生命周期
编排与门禁，不重建版本存储）；gray_release_shadow_deployer=影子部署实现
（本件仅注入其编排语义回调，不实现影子逻辑）；adversarial_robustness_
validator=鲁棒性评估实现（本件仅注入其判定回调）。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "MlModelFactoryError",
    "ModelRecord",
    "ModelStage",
    "MlModelFactory",
    "StageTransition",
]

#: 前进迁移（含退役）；回退迁移单独定义
_FORWARD: Final[dict["ModelStage", frozenset]] = {}
_ROLLBACK: Final[dict["ModelStage", "ModelStage"]] = {}


class MlModelFactoryError(Exception):
    """模型工厂输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-MLT-UNREGISTERED-MODEL-FACTORY。
    """


class ModelStage(str, Enum):
    """模型生命周期阶段（词表闭合）。"""

    DEV = "dev"
    CANDIDATE = "candidate"
    STAGING = "staging"
    PRODUCTION = "production"
    RETIRED = "retired"


_FORWARD.update({
    ModelStage.DEV: frozenset({ModelStage.CANDIDATE, ModelStage.RETIRED}),
    ModelStage.CANDIDATE: frozenset({ModelStage.STAGING, ModelStage.RETIRED}),
    ModelStage.STAGING: frozenset({ModelStage.PRODUCTION, ModelStage.RETIRED}),
    ModelStage.PRODUCTION: frozenset({ModelStage.RETIRED}),
    ModelStage.RETIRED: frozenset(),
})
_ROLLBACK.update({
    ModelStage.PRODUCTION: ModelStage.STAGING,
    ModelStage.STAGING: ModelStage.CANDIDATE,
})


@dataclass(frozen=True)
class ModelRecord:
    """模型注册记录（frozen，迁移产生新记录）。"""

    name: str
    version: str
    metadata: dict
    stage: ModelStage
    registered_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass(frozen=True)
class StageTransition:
    """生命周期迁移留痕（frozen）。"""

    name: str
    version: str
    from_stage: ModelStage
    to_stage: ModelStage
    reason: str
    transitioned_at: datetime.datetime


class MlModelFactory:
    """ML 模型工厂（注册表 + 生命周期状态机 + 门禁/编排/队列注入）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        robustness_validator: Callable[[str, str, Mapping[str, Any]], bool] | None = None,
        gray_orchestrator: Callable[[ModelRecord], bool] | None = None,
        gpu_scheduler: Callable[[str, Mapping[str, Any]], Any] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._robustness_validator = robustness_validator
        self._gray_orchestrator = gray_orchestrator
        self._gpu_scheduler = gpu_scheduler
        self._records: dict[tuple[str, str], ModelRecord] = {}
        self._history: dict[tuple[str, str], list[StageTransition]] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _key(self, name: str, version: str) -> tuple[str, str]:
        if not name:
            raise MlModelFactoryError("模型名称为空")
        if not version:
            raise MlModelFactoryError("模型版本为空")
        return (name, version)

    def _record_of(self, name: str, version: str) -> ModelRecord:
        record = self._records.get(self._key(name, version))
        if record is None:
            raise MlModelFactoryError(f"未知模型: {name!r}@{version!r}（未注册）")
        return record

    def _transit(self, record: ModelRecord, to_stage: ModelStage, reason: str) -> ModelRecord:
        """内部迁移执行（合法性校验在调用方完成）。"""
        now = self._clock()
        new_record = ModelRecord(
            name=record.name,
            version=record.version,
            metadata=dict(record.metadata),
            stage=to_stage,
            registered_at=record.registered_at,
            updated_at=now,
        )
        self._records[(record.name, record.version)] = new_record
        self._history[(record.name, record.version)].append(StageTransition(
            name=record.name,
            version=record.version,
            from_stage=record.stage,
            to_stage=to_stage,
            reason=reason,
            transitioned_at=now,
        ))
        _log.info(
            "模型迁移: %s@%s %s -> %s (%s)",
            record.name, record.version, record.stage.value, to_stage.value, reason,
        )
        return new_record

    def _forward(self, name: str, version: str, to_stage: ModelStage, reason: str) -> ModelRecord:
        record = self._record_of(name, version)
        if to_stage not in _FORWARD[record.stage]:
            raise MlModelFactoryError(
                f"非法状态迁移: {name!r}@{version!r} 当前 {record.stage.value}，"
                f"不可前进至 {to_stage.value}"
            )
        return self._transit(record, to_stage, reason)

    # ── 注册表 ────────────────────────────────────────────────────────────

    def register_model(
        self,
        name: str,
        version: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> ModelRecord:
        """注册模型（初始 dev；重复注册拒绝）。"""
        key = self._key(name, version)
        if key in self._records:
            raise MlModelFactoryError(f"模型重复注册: {name!r}@{version!r}")
        now = self._clock()
        record = ModelRecord(
            name=name,
            version=version,
            metadata=dict(metadata or {}),
            stage=ModelStage.DEV,
            registered_at=now,
            updated_at=now,
        )
        self._records[key] = record
        self._history[key] = []
        _log.info("模型注册: %s@%s", name, version)
        return record

    # ── 生命周期状态机 ────────────────────────────────────────────────────

    def submit_candidate(self, name: str, version: str) -> ModelRecord:
        """dev → candidate。"""
        return self._forward(name, version, ModelStage.CANDIDATE, "提交候选")

    def promote_to_staging(self, name: str, version: str) -> ModelRecord:
        """candidate → staging。"""
        return self._forward(name, version, ModelStage.STAGING, "晋级预发布")

    def promote_to_production(self, name: str, version: str) -> ModelRecord:
        """staging → production：对抗鲁棒门禁 + 灰度编排双注入强制。

        鲁棒 validator 未注入或判定不过 → Fail-Closed 禁上线；
        灰度编排未注入 → Fail-Closed（禁止绕过灰度直上线）。
        """
        record = self._record_of(name, version)
        if self._robustness_validator is None:
            raise MlModelFactoryError(
                "robustness_validator 未注入（对抗鲁棒门禁强制，禁止旁路上线）"
            )
        try:
            robust_ok = bool(self._robustness_validator(name, version, record.metadata))
        except Exception:  # noqa: BLE001 — 门禁异常按不过处理不抛
            _log.exception("robustness_validator 判定异常: %s@%s", name, version)
            robust_ok = False
        if not robust_ok:
            raise MlModelFactoryError(
                f"对抗鲁棒门禁未通过: {name!r}@{version!r}（禁上线）"
            )
        if self._gray_orchestrator is None:
            raise MlModelFactoryError(
                "gray_orchestrator 未注入（灰度发布编排强制，禁止直上线）"
            )
        promoted = self._forward(name, version, ModelStage.PRODUCTION, "鲁棒门禁通过+灰度编排晋级")
        try:
            ok = bool(self._gray_orchestrator(promoted))
        except Exception:  # noqa: BLE001 — 编排异常留痕不阻断（编排语义仅挂载）
            _log.exception("gray_orchestrator 编排异常: %s@%s", name, version)
            ok = False
        if not ok:
            _log.warning("灰度编排返回未受理: %s@%s（已上线，编排留痕）", name, version)
        return promoted

    def rollback(self, name: str, version: str, reason: str = "") -> ModelRecord:
        """回退：production→staging 或 staging→candidate（其余拒绝）。"""
        record = self._record_of(name, version)
        target = _ROLLBACK.get(record.stage)
        if target is None:
            raise MlModelFactoryError(
                f"非法回退: {name!r}@{version!r} 当前 {record.stage.value} 无回退路径"
            )
        return self._transit(record, target, reason or "回退")

    def retire(self, name: str, version: str, reason: str = "") -> ModelRecord:
        """退役：任意非 retired 阶段 → retired（终态）。"""
        return self._forward(name, version, ModelStage.RETIRED, reason or "退役")

    # ── GPU 任务队列 ──────────────────────────────────────────────────────

    def submit_training(self, name: str, version: str, payload: Mapping[str, Any]) -> Any:
        """提交 GPU 训练任务（scheduler 未注入 Fail-Closed）。"""
        self._record_of(name, version)
        if self._gpu_scheduler is None:
            raise MlModelFactoryError(
                "gpu_scheduler 未注入（GPU 任务队列强制，禁止旁路）"
            )
        return self._gpu_scheduler(f"{name}@{version}", dict(payload))

    # ── 查询 ─────────────────────────────────────────────────────────────

    def get_record(self, name: str, version: str) -> ModelRecord:
        """单模型记录查询（未知 → Fail-Closed）。"""
        return self._record_of(name, version)

    def history(self, name: str, version: str) -> list[StageTransition]:
        """迁移历史（按发生序）。"""
        self._record_of(name, version)
        return list(self._history[self._key(name, version)])

    def list_models(self, stage: ModelStage | None = None) -> tuple[ModelRecord, ...]:
        """模型清单（按 (name, version) 确定性排序；可按阶段过滤）。"""
        records = [
            r for r in self._records.values()
            if stage is None or r.stage is stage
        ]
        records.sort(key=lambda r: (r.name, r.version))
        return tuple(records)
