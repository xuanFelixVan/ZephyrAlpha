# [BLUEPRINT] MOD-MLS-002 | docs/03_modules/_domain_ml_serve/model_compression_accelerator/blueprint.md | §test
# [A_module] module_id=MOD-MLS-002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [A_test] module_id: MOD-MLS-002 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.ml_serve.test_model_compression_accelerator
# [TESTS] src/zephyr/ml_serve/model_compression_accelerator.py
"""MOD-MLS-002 单元测试：model_compression_accelerator 模型压缩与推理加速器。

蓝图验收（B10-01872/CAND-MLS-002，A1 §29.28）：
三阶段压缩编排（ONNX+INT8 / llama.cpp INT4 / 知识蒸馏，执行器全注入）+
校准集防泄漏校验 + 数值误差<1e-5 验证注入 + Phase2 Double-Lock 注入 +
每阶段 C-003 验证门禁注入 + 压缩登记册。
执行器/验证器/门禁全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.ml_serve.model_compression_accelerator",
    reason="model_compression_accelerator not importable",
)

from zephyr.ml_serve.model_compression_accelerator import (  # noqa: E402
    CompressionJob,
    CompressionPhase,
    ModelCompressionAccelerator,
    ModelCompressionError,
    PhaseOutcome,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)

_PHASES = (
    CompressionPhase.ONNX_INT8,
    CompressionPhase.LLAMACPP_INT4,
    CompressionPhase.KNOWLEDGE_DISTILLATION,
)

_BASELINE = {"crps": 0.12, "sharpe": 1.8, "max_dd": 0.08}
_CANDIDATE = {"crps": 0.121, "sharpe": 1.79, "max_dd": 0.081}


def _accelerator(
    *,
    executors: dict | None = None,
    numeric_error: float = 1e-6,
    double_lock_ok: bool = True,
    gate=None,
    holdout_ids=(),
) -> ModelCompressionAccelerator:
    return ModelCompressionAccelerator(
        phase_executors=(
            executors if executors is not None
            else {phase: (lambda job: dict(_CANDIDATE)) for phase in _PHASES}
        ),
        numeric_error_validator=lambda job: numeric_error,
        double_lock_checker=lambda job: double_lock_ok,
        c003_gate=gate if gate is not None else (lambda m, b, c: True),
        holdout_ids=holdout_ids,
        clock=lambda: _T0,
    )


def _job(
    model_id: str = "m-1",
    phase: CompressionPhase = CompressionPhase.ONNX_INT8,
    job_id: str = "job-1",
    calibration_ids=("cal-1", "cal-2"),
) -> CompressionJob:
    return CompressionJob(
        job_id=job_id,
        model_id=model_id,
        phase=phase,
        calibration_ids=tuple(calibration_ids),
        submitted_at=_T0,
    )


def _registered(acc: ModelCompressionAccelerator | None = None) -> ModelCompressionAccelerator:
    acc = acc or _accelerator()
    acc.register_model("m-1", _BASELINE)
    return acc


# ──────────────────────────────────────────────────────────────────────────────
# 构造（执行器全注入硬约束）
# ──────────────────────────────────────────────────────────────────────────────


class TestConstruction:
    def test_missing_executor_raises(self) -> None:
        with pytest.raises(ModelCompressionError):
            _accelerator(executors={CompressionPhase.ONNX_INT8: lambda job: dict(_CANDIDATE)})

    def test_invalid_phase_key_raises(self) -> None:
        executors = {phase: (lambda job: dict(_CANDIDATE)) for phase in _PHASES}
        executors["ghost_phase"] = lambda job: dict(_CANDIDATE)  # 词表外键非法
        with pytest.raises(ModelCompressionError):
            _accelerator(executors=executors)


# ──────────────────────────────────────────────────────────────────────────────
# 模型登记
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterModel:
    def test_register_ok(self) -> None:
        acc = _accelerator()
        acc.register_model("m-2", _BASELINE)
        acc.register_model("m-1", _BASELINE)
        assert acc.registered_models() == ("m-1", "m-2")  # 确定性排序
        assert acc.next_phase("m-1") is CompressionPhase.ONNX_INT8

    def test_empty_model_id_raises(self) -> None:
        with pytest.raises(ModelCompressionError):
            _accelerator().register_model("", _BASELINE)

    def test_duplicate_register_raises(self) -> None:
        acc = _registered()
        with pytest.raises(ModelCompressionError):
            acc.register_model("m-1", _BASELINE)

    def test_empty_baseline_raises(self) -> None:
        with pytest.raises(ModelCompressionError):
            _accelerator().register_model("m-1", {})

    def test_non_finite_baseline_raises(self) -> None:
        with pytest.raises(ModelCompressionError):
            _accelerator().register_model("m-1", {"crps": float("nan")})


# ──────────────────────────────────────────────────────────────────────────────
# 阶段编排（严格按序推进）
# ──────────────────────────────────────────────────────────────────────────────


class TestPhaseOrder:
    def test_full_pipeline_pass(self) -> None:
        acc = _registered()
        for i, phase in enumerate(_PHASES):
            record = acc.run_phase(_job(phase=phase, job_id=f"job-{i}"))
            assert record.outcome is PhaseOutcome.PASSED
            assert record.candidate_metrics == _CANDIDATE
            assert record.reasons == ()
            assert record.finished_at == _T0
        assert acc.next_phase("m-1") is None  # 三阶段全过
        records = acc.records_of("m-1")
        assert [r.phase for r in records] == list(_PHASES)  # 登记册执行序
        assert acc.record_of("job-0").phase is CompressionPhase.ONNX_INT8

    def test_skip_phase_raises(self) -> None:
        acc = _registered()
        with pytest.raises(ModelCompressionError):
            acc.run_phase(_job(phase=CompressionPhase.LLAMACPP_INT4))  # 跳阶段

    def test_failed_not_advance_then_retry(self) -> None:
        flags = {"gate": False}
        acc = _registered(_accelerator(gate=lambda m, b, c: flags["gate"]))
        failed = acc.run_phase(_job(job_id="job-1"))
        assert failed.outcome is PhaseOutcome.FAILED
        assert acc.next_phase("m-1") is CompressionPhase.ONNX_INT8  # 门禁不过不推进
        flags["gate"] = True
        passed = acc.run_phase(_job(job_id="job-2"))  # 同阶段新 job 可重试
        assert passed.outcome is PhaseOutcome.PASSED
        assert acc.next_phase("m-1") is CompressionPhase.LLAMACPP_INT4

    def test_unknown_model_raises(self) -> None:
        with pytest.raises(ModelCompressionError):
            _accelerator().run_phase(_job(model_id="ghost"))
        with pytest.raises(ModelCompressionError):
            _accelerator().next_phase("ghost")

    def test_empty_and_duplicate_job_id_raises(self) -> None:
        acc = _registered()
        with pytest.raises(ModelCompressionError):
            acc.run_phase(_job(job_id=""))
        acc.run_phase(_job(job_id="job-1"))
        with pytest.raises(ModelCompressionError):
            acc.run_phase(_job(job_id="job-1"))

    def test_invalid_phase_type_raises(self) -> None:
        acc = _registered()
        with pytest.raises(ModelCompressionError):
            acc.run_phase(_job(phase="onnx_int8"))  # 字符串非词表成员


# ──────────────────────────────────────────────────────────────────────────────
# 校准集防泄漏校验
# ──────────────────────────────────────────────────────────────────────────────


class TestCalibrationLeak:
    def test_leak_raises(self) -> None:
        acc = _registered(_accelerator(holdout_ids=("h-1", "h-2")))
        with pytest.raises(ModelCompressionError) as exc_info:
            acc.run_phase(_job(calibration_ids=("cal-1", "h-2")))
        assert "h-2" in str(exc_info.value)

    def test_phase1_empty_calibration_raises(self) -> None:
        acc = _registered()
        with pytest.raises(ModelCompressionError):
            acc.run_phase(_job(calibration_ids=()))

    def test_empty_calibration_entry_raises(self) -> None:
        acc = _registered()
        with pytest.raises(ModelCompressionError):
            acc.run_phase(_job(calibration_ids=("cal-1", "")))


# ──────────────────────────────────────────────────────────────────────────────
# 阶段专项验证 + C-003 门禁（不过记 FAILED）
# ──────────────────────────────────────────────────────────────────────────────


class TestPhaseGates:
    def test_numeric_error_at_limit_failed(self) -> None:
        acc = _registered(_accelerator(numeric_error=1e-5))  # ≥ 上限即失败
        record = acc.run_phase(_job())
        assert record.outcome is PhaseOutcome.FAILED
        assert record.numeric_error == 1e-5
        assert any("数值误差" in r for r in record.reasons)

    def test_numeric_error_below_limit_pass(self) -> None:
        acc = _registered(_accelerator(numeric_error=9.9e-6))
        record = acc.run_phase(_job())
        assert record.outcome is PhaseOutcome.PASSED
        assert record.numeric_error == 9.9e-6

    def test_numeric_validator_exception_failed(self) -> None:
        acc = ModelCompressionAccelerator(
            phase_executors={p: (lambda job: dict(_CANDIDATE)) for p in _PHASES},
            numeric_error_validator=lambda job: 1 / 0,
            double_lock_checker=lambda job: True,
            c003_gate=lambda m, b, c: True,
            clock=lambda: _T0,
        )
        acc.register_model("m-1", _BASELINE)
        record = acc.run_phase(_job())
        assert record.outcome is PhaseOutcome.FAILED
        assert any("验证器异常" in r for r in record.reasons)

    def test_double_lock_reject_failed(self) -> None:
        acc = _registered(_accelerator(double_lock_ok=False))
        acc.run_phase(_job(job_id="job-1"))  # Phase1 先过
        record = acc.run_phase(_job(phase=CompressionPhase.LLAMACPP_INT4, job_id="job-2"))
        assert record.outcome is PhaseOutcome.FAILED
        assert any("Double-Lock" in r for r in record.reasons)
        assert record.numeric_error is None  # Phase2 不做数值误差验证

    def test_c003_gate_reject_failed(self) -> None:
        acc = _registered(_accelerator(gate=lambda m, b, c: False))
        record = acc.run_phase(_job())
        assert record.outcome is PhaseOutcome.FAILED
        assert any("C-003" in r for r in record.reasons)

    def test_executor_exception_failed(self) -> None:
        def _boom(job: CompressionJob) -> dict:
            raise RuntimeError("onnx 量化崩溃")

        executors = {p: (lambda job: dict(_CANDIDATE)) for p in _PHASES}
        executors[CompressionPhase.ONNX_INT8] = _boom
        acc = _registered(_accelerator(executors=executors))
        record = acc.run_phase(_job())
        assert record.outcome is PhaseOutcome.FAILED
        assert any("执行器异常" in r for r in record.reasons)

    def test_executor_invalid_metrics_failed(self) -> None:
        executors = {p: (lambda job: dict(_CANDIDATE)) for p in _PHASES}
        executors[CompressionPhase.ONNX_INT8] = lambda job: {"crps": float("inf")}
        acc = _registered(_accelerator(executors=executors))
        record = acc.run_phase(_job())
        assert record.outcome is PhaseOutcome.FAILED
        assert any("产出非法" in r for r in record.reasons)


# ──────────────────────────────────────────────────────────────────────────────
# 登记册查询 / 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestRegistry:
    def test_record_of_unknown_raises(self) -> None:
        acc = _registered()
        with pytest.raises(ModelCompressionError):
            acc.record_of("ghost")
        with pytest.raises(ModelCompressionError):
            acc.records_of("ghost")

    def test_determinism(self) -> None:
        def _script() -> tuple:
            acc = _registered()
            acc.run_phase(_job(job_id="job-1"))
            acc.run_phase(_job(phase=CompressionPhase.LLAMACPP_INT4, job_id="job-2"))
            return acc.records_of("m-1")

        assert _script() == _script()  # 同输入必同输出
