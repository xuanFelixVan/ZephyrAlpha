# [BLUEPRINT] MOD-ML-013 | docs/03_modules/_domain_machine_learning_train/ml_model_factory/blueprint.md | §test
# [A_module] module_id=MOD-ML-013 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [A_test] module_id: MOD-ML-013 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.ml_train.test_ml_model_factory
# [TESTS] src/zephyr/ml_train/ml_model_factory.py
"""MOD-ML-013 单元测试：ml_model_factory ML 模型工厂。

蓝图验收（B1-00253/CAND-MLT-017，C2 C-029）：
模型注册表（名称/版本/元数据）+ 生命周期状态机（dev→candidate→staging→
production→retired 含回退）+ 晋级 production 强制对抗鲁棒门禁（未注入/不过
Fail-Closed）+ 灰度编排注入（未注入 Fail-Closed）+ GPU 队列注入（未注入
Fail-Closed）+ 查询确定性排序。门禁/编排/队列全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.ml_train.ml_model_factory",
    reason="ml_model_factory not importable",
)

from zephyr.ml_train.ml_model_factory import (  # noqa: E402
    MlModelFactory,
    MlModelFactoryError,
    ModelRecord,
    ModelStage,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _factory(
    *,
    robust_ok: bool = True,
    with_validator: bool = True,
    with_gray: bool = True,
    gray_calls: list | None = None,
    scheduler=None,
) -> MlModelFactory:
    return MlModelFactory(
        clock=lambda: _T0,
        robustness_validator=(lambda n, v, m: robust_ok) if with_validator else None,
        gray_orchestrator=((lambda r: gray_calls.append(r) or True) if gray_calls is not None else (lambda r: True))
        if with_gray
        else None,
        gpu_scheduler=scheduler,
    )


def _registered(factory: MlModelFactory, name: str = "gbm_alpha", version: str = "1.0.0") -> ModelRecord:
    return factory.register_model(name, version, metadata={"framework": "lightgbm"})


def _to_staging(factory: MlModelFactory, name: str = "gbm_alpha", version: str = "1.0.0") -> None:
    _registered(factory, name, version)
    factory.submit_candidate(name, version)
    factory.promote_to_staging(name, version)


# ──────────────────────────────────────────────────────────────────────────────
# 注册表
# ──────────────────────────────────────────────────────────────────────────────


class TestRegister:
    def test_register_ok_initial_dev(self) -> None:
        factory = _factory()
        record = _registered(factory)
        assert record.stage is ModelStage.DEV
        assert record.metadata == {"framework": "lightgbm"}
        assert record.registered_at == _T0

    def test_register_duplicate_rejected(self) -> None:
        factory = _factory()
        _registered(factory)
        with pytest.raises(MlModelFactoryError):
            _registered(factory)

    def test_register_empty_name_rejected(self) -> None:
        factory = _factory()
        with pytest.raises(MlModelFactoryError):
            factory.register_model("", "1.0.0")

    def test_register_empty_version_rejected(self) -> None:
        factory = _factory()
        with pytest.raises(MlModelFactoryError):
            factory.register_model("gbm_alpha", "")

    def test_register_default_metadata_empty(self) -> None:
        factory = _factory()
        record = factory.register_model("m", "0.1.0")
        assert record.metadata == {}


# ──────────────────────────────────────────────────────────────────────────────
# 生命周期状态机
# ──────────────────────────────────────────────────────────────────────────────


class TestLifecycle:
    def test_full_path_to_production(self) -> None:
        factory = _factory()
        _to_staging(factory)
        record = factory.promote_to_production("gbm_alpha", "1.0.0")
        assert record.stage is ModelStage.PRODUCTION

    def test_skip_stage_rejected(self) -> None:
        factory = _factory()
        _registered(factory)
        with pytest.raises(MlModelFactoryError):
            factory.promote_to_staging("gbm_alpha", "1.0.0")  # dev→staging 越级

    def test_backward_transition_rejected(self) -> None:
        factory = _factory()
        _registered(factory)
        factory.submit_candidate("gbm_alpha", "1.0.0")
        with pytest.raises(MlModelFactoryError):
            factory.submit_candidate("gbm_alpha", "1.0.0")  # candidate→candidate 非法

    def test_unknown_model_raises(self) -> None:
        factory = _factory()
        with pytest.raises(MlModelFactoryError):
            factory.submit_candidate("ghost", "1.0.0")
        with pytest.raises(MlModelFactoryError):
            factory.get_record("ghost", "1.0.0")

    def test_rollback_production_to_staging(self) -> None:
        factory = _factory()
        _to_staging(factory)
        factory.promote_to_production("gbm_alpha", "1.0.0")
        record = factory.rollback("gbm_alpha", "1.0.0", reason="线上回撤超限")
        assert record.stage is ModelStage.STAGING

    def test_rollback_staging_to_candidate(self) -> None:
        factory = _factory()
        _to_staging(factory)
        record = factory.rollback("gbm_alpha", "1.0.0")
        assert record.stage is ModelStage.CANDIDATE

    def test_rollback_dev_rejected(self) -> None:
        factory = _factory()
        _registered(factory)
        with pytest.raises(MlModelFactoryError):
            factory.rollback("gbm_alpha", "1.0.0")

    def test_retire_terminal(self) -> None:
        factory = _factory()
        _to_staging(factory)
        factory.promote_to_production("gbm_alpha", "1.0.0")
        record = factory.retire("gbm_alpha", "1.0.0")
        assert record.stage is ModelStage.RETIRED
        with pytest.raises(MlModelFactoryError):
            factory.retire("gbm_alpha", "1.0.0")  # 终态不可再迁

    def test_history_trail(self) -> None:
        factory = _factory()
        _to_staging(factory)
        factory.promote_to_production("gbm_alpha", "1.0.0")
        factory.rollback("gbm_alpha", "1.0.0", reason="回退验证")
        history = factory.history("gbm_alpha", "1.0.0")
        stages = [(t.from_stage, t.to_stage) for t in history]
        assert stages == [
            (ModelStage.DEV, ModelStage.CANDIDATE),
            (ModelStage.CANDIDATE, ModelStage.STAGING),
            (ModelStage.STAGING, ModelStage.PRODUCTION),
            (ModelStage.PRODUCTION, ModelStage.STAGING),
        ]
        assert history[-1].reason == "回退验证"


# ──────────────────────────────────────────────────────────────────────────────
# 对抗鲁棒门禁 + 灰度编排（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestProductionGates:
    def test_validator_not_injected_fail_closed(self) -> None:
        factory = _factory(with_validator=False)
        _to_staging(factory)
        with pytest.raises(MlModelFactoryError):
            factory.promote_to_production("gbm_alpha", "1.0.0")

    def test_validator_reject_forbids_production(self) -> None:
        factory = _factory(robust_ok=False)
        _to_staging(factory)
        with pytest.raises(MlModelFactoryError):
            factory.promote_to_production("gbm_alpha", "1.0.0")
        assert factory.get_record("gbm_alpha", "1.0.0").stage is ModelStage.STAGING

    def test_validator_exception_treated_as_reject(self) -> None:
        def _boom(n, v, m):
            raise RuntimeError("validator 崩溃")

        factory = MlModelFactory(clock=lambda: _T0, robustness_validator=_boom, gray_orchestrator=lambda r: True)
        _to_staging(factory)
        with pytest.raises(MlModelFactoryError):
            factory.promote_to_production("gbm_alpha", "1.0.0")

    def test_gray_orchestrator_not_injected_fail_closed(self) -> None:
        factory = _factory(with_gray=False)
        _to_staging(factory)
        with pytest.raises(MlModelFactoryError):
            factory.promote_to_production("gbm_alpha", "1.0.0")

    def test_gray_orchestrator_invoked_with_record(self) -> None:
        calls: list[ModelRecord] = []
        factory = _factory(gray_calls=calls)
        _to_staging(factory)
        factory.promote_to_production("gbm_alpha", "1.0.0")
        assert len(calls) == 1
        assert calls[0].stage is ModelStage.PRODUCTION

    def test_promotion_requires_staging(self) -> None:
        factory = _factory()
        _registered(factory)
        factory.submit_candidate("gbm_alpha", "1.0.0")
        with pytest.raises(MlModelFactoryError):
            factory.promote_to_production("gbm_alpha", "1.0.0")  # candidate→production 越级


# ──────────────────────────────────────────────────────────────────────────────
# GPU 任务队列
# ──────────────────────────────────────────────────────────────────────────────


class TestGpuQueue:
    def test_submit_training_ok(self) -> None:
        submitted: list[tuple[str, dict]] = []
        factory = _factory(scheduler=lambda key, payload: submitted.append((key, payload)) or "job-1")
        _registered(factory)
        job = factory.submit_training("gbm_alpha", "1.0.0", {"gpu": "A800", "epochs": 10})
        assert job == "job-1"
        assert submitted == [("gbm_alpha@1.0.0", {"gpu": "A800", "epochs": 10})]

    def test_submit_training_scheduler_missing_fail_closed(self) -> None:
        factory = _factory()
        _registered(factory)
        with pytest.raises(MlModelFactoryError):
            factory.submit_training("gbm_alpha", "1.0.0", {})

    def test_submit_training_unknown_model_raises(self) -> None:
        factory = _factory(scheduler=lambda k, p: "job-1")
        with pytest.raises(MlModelFactoryError):
            factory.submit_training("ghost", "1.0.0", {})


# ──────────────────────────────────────────────────────────────────────────────
# 查询
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_list_models_deterministic_order(self) -> None:
        factory = _factory()
        factory.register_model("zeta", "1.0.0")
        factory.register_model("alpha", "2.0.0")
        factory.register_model("alpha", "1.0.0")
        names = [(r.name, r.version) for r in factory.list_models()]
        assert names == [("alpha", "1.0.0"), ("alpha", "2.0.0"), ("zeta", "1.0.0")]

    def test_list_models_filter_by_stage(self) -> None:
        factory = _factory()
        _registered(factory, "m1", "1.0.0")
        factory.register_model("m2", "1.0.0")
        factory.submit_candidate("m2", "1.0.0")
        dev = factory.list_models(stage=ModelStage.DEV)
        assert [r.name for r in dev] == ["m1"]
        candidates = factory.list_models(stage=ModelStage.CANDIDATE)
        assert [r.name for r in candidates] == ["m2"]
