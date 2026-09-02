# [BLUEPRINT] MOD-GOV-056 | docs/03_modules/_domain_gov_enforcement/construction_governor_gate/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-GOV-056 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.gov_enforcement.test_construction_governor_gate
# [TESTS] src/zephyr/gov_enforcement/construction_governor_gate.py
"""MOD-GOV-056 单元测试：construction_governor_gate AI 施工门禁器。

蓝图验收（B10-02423/CAND-GOVENFOR-002，A1 D-GOVERNANCE-15）：公式 Hash 校验
（登记指纹→产出比对，漂移拒绝）+ 回归截断（影响面超阈值截断须升级审批）+
门禁判定留痕 + Fail-Closed 分支 + 确定性。审批/留痕/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime
import hashlib

import pytest

pytest.importorskip(
    "zephyr.gov_enforcement.construction_governor_gate",
    reason="construction_governor_gate not importable",
)

from zephyr.gov_enforcement.construction_governor_gate import (  # noqa: E402
    ArtifactProduct,
    ConstructionGateError,
    ConstructionGovernorGate,
    EscalationRequest,
    GateDecision,
)

_T0 = datetime.datetime(2026, 8, 26, 16, 0, 0)

_FORMULA = "price = vwap * (1 + alpha)"
_PRODUCT = "price = vwap * (1 + alpha)"


def _gate(
    records: list | None = None,
    approval=None,
    threshold: int = 3,
) -> ConstructionGovernorGate:
    return ConstructionGovernorGate(
        clock=lambda: _T0,
        impact_threshold=threshold,
        approval_sink=approval,
        record_sink=(lambda v: records.append(v)) if records is not None else None,
    )


def _registered(gate: ConstructionGovernorGate, artifact: str = "alpha_model") -> ConstructionGovernorGate:
    gate.register_formula(artifact, _FORMULA)
    return gate


def _product(
    artifact: str = "alpha_model",
    text: str = _PRODUCT,
    paths: tuple[str, ...] = ("src/a.py",),
) -> ArtifactProduct:
    return ArtifactProduct(artifact_id=artifact, produced_text=text, affected_paths=paths)


# ──────────────────────────────────────────────────────────────────────────────
# 构造参数（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestConstructor:
    def test_invalid_threshold_rejected(self) -> None:
        with pytest.raises(ConstructionGateError):
            _gate(threshold=0)
        with pytest.raises(ConstructionGateError):
            _gate(threshold=-1)
        with pytest.raises(ConstructionGateError):
            _gate(threshold=True)
        with pytest.raises(ConstructionGateError):
            _gate(threshold="3")

    def test_defaults_ok(self) -> None:
        gate = ConstructionGovernorGate(clock=lambda: _T0)
        assert gate.verdicts() == ()
        assert gate.registrations() == ()


# ──────────────────────────────────────────────────────────────────────────────
# 公式登记
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterFormula:
    def test_fingerprint_is_sha256_of_formula(self) -> None:
        gate = _registered(_gate())
        registration = gate.registrations()[0]
        assert registration.fingerprint == hashlib.sha256(_FORMULA.encode("utf-8")).hexdigest()
        assert registration.registered_at == _T0

    def test_empty_fields_rejected(self) -> None:
        gate = _gate()
        with pytest.raises(ConstructionGateError):
            gate.register_formula("", _FORMULA)
        with pytest.raises(ConstructionGateError):
            gate.register_formula("alpha_model", "")
        with pytest.raises(ConstructionGateError):
            gate.register_formula(None, _FORMULA)
        with pytest.raises(ConstructionGateError):
            gate.register_formula("alpha_model", None)

    def test_duplicate_registration_rejected(self) -> None:
        gate = _registered(_gate())
        with pytest.raises(ConstructionGateError):
            gate.register_formula("alpha_model", "other formula")

    def test_registrations_sorted_by_artifact_id(self) -> None:
        gate = _gate()
        gate.register_formula("zeta", "f1")
        gate.register_formula("beta", "f2")
        gate.register_formula("alpha", "f3")
        assert [r.artifact_id for r in gate.registrations()] == ["alpha", "beta", "zeta"]


# ──────────────────────────────────────────────────────────────────────────────
# 公式指纹核验
# ──────────────────────────────────────────────────────────────────────────────


class TestFormulaVerify:
    def test_pass_within_threshold(self) -> None:
        gate = _registered(_gate())
        verdict = gate.verify(_product())
        assert verdict.decision is GateDecision.PASS
        assert verdict.formula_match is True
        assert verdict.escalated is False
        assert verdict.truncated_paths == ()
        assert verdict.allowed_paths == ("src/a.py",)
        assert verdict.decided_at == _T0

    def test_unknown_artifact_fail_closed(self) -> None:
        gate = _gate()
        with pytest.raises(ConstructionGateError):
            gate.verify(_product(artifact="ghost"))

    def test_formula_drift_rejected(self) -> None:
        gate = _registered(_gate())
        verdict = gate.verify(_product(text="price = close * 2"))
        assert verdict.decision is GateDecision.REJECT
        assert verdict.formula_match is False
        assert "漂移" in verdict.reason

    def test_drift_precedes_escalation(self) -> None:
        gate = _registered(_gate(threshold=1))
        verdict = gate.verify(_product(text="drifted", paths=("a", "b", "c")))
        assert verdict.decision is GateDecision.REJECT  # 漂移一票否决，不走升级
        assert verdict.escalated is False

    def test_invalid_product_rejected(self) -> None:
        gate = _registered(_gate())
        with pytest.raises(ConstructionGateError):
            gate.verify("not-a-product")
        with pytest.raises(ConstructionGateError):
            gate.verify(_product(artifact=""))
        with pytest.raises(ConstructionGateError):
            gate.verify(_product(text=None))
        with pytest.raises(ConstructionGateError):
            gate.verify(_product(paths=["src/a.py"]))
        with pytest.raises(ConstructionGateError):
            gate.verify(_product(paths=("ok", 1)))


# ──────────────────────────────────────────────────────────────────────────────
# 回归截断与升级审批
# ──────────────────────────────────────────────────────────────────────────────


class TestImpactEscalation:
    def test_over_threshold_escalates_without_approval_sink(self) -> None:
        gate = _registered(_gate(threshold=2))
        verdict = gate.verify(_product(paths=("a", "b", "c")))
        assert verdict.decision is GateDecision.ESCALATE  # 未注入审批=未获批，Fail-Closed
        assert verdict.escalated is True
        assert verdict.allowed_paths == ("a", "b")
        assert verdict.truncated_paths == ("c",)
        assert verdict.impact_size == 3
        assert verdict.impact_threshold == 2

    def test_approval_granted_passes_full_paths(self) -> None:
        gate = _registered(_gate(threshold=2, approval=lambda req: True))
        verdict = gate.verify(_product(paths=("a", "b", "c")))
        assert verdict.decision is GateDecision.PASS
        assert verdict.escalated is True
        assert verdict.allowed_paths == ("a", "b", "c")
        assert verdict.truncated_paths == ()
        assert "升级审批" in verdict.reason

    def test_approval_denied_escalates(self) -> None:
        gate = _registered(_gate(threshold=2, approval=lambda req: False))
        verdict = gate.verify(_product(paths=("a", "b", "c")))
        assert verdict.decision is GateDecision.ESCALATE
        assert verdict.truncated_paths == ("c",)

    def test_approval_sink_receives_request_payload(self) -> None:
        seen: list[EscalationRequest] = []
        gate = _registered(_gate(threshold=2, approval=lambda req: seen.append(req) or True))
        gate.verify(_product(paths=("a", "b", "c")))
        assert len(seen) == 1
        assert seen[0].artifact_id == "alpha_model"
        assert seen[0].impact_size == 3
        assert seen[0].impact_threshold == 2
        assert seen[0].truncated_paths == ("c",)

    def test_approval_sink_exception_fail_closed(self) -> None:
        def boom(req: EscalationRequest) -> bool:
            raise RuntimeError("approval channel down")

        gate = _registered(_gate(threshold=1, approval=boom))
        with pytest.raises(ConstructionGateError):
            gate.verify(_product(paths=("a", "b")))

    def test_approval_non_bool_return_rejected(self) -> None:
        gate = _registered(_gate(threshold=1, approval=lambda req: "yes"))
        with pytest.raises(ConstructionGateError):
            gate.verify(_product(paths=("a", "b")))

    def test_threshold_boundary_exact_passes(self) -> None:
        gate = _registered(_gate(threshold=2))
        verdict = gate.verify(_product(paths=("a", "b")))
        assert verdict.decision is GateDecision.PASS
        assert verdict.escalated is False


# ──────────────────────────────────────────────────────────────────────────────
# 判定留痕
# ──────────────────────────────────────────────────────────────────────────────


class TestVerdictRecording:
    def test_verdicts_recorded_in_order(self) -> None:
        records: list = []
        gate = _registered(_gate(records, threshold=1))
        gate.verify(_product())
        gate.verify(_product(text="drifted", paths=("a", "b")))
        verdicts = gate.verdicts()
        assert [v.decision for v in verdicts] == [GateDecision.PASS, GateDecision.REJECT]
        assert [v.decision for v in records] == [GateDecision.PASS, GateDecision.REJECT]

    def test_verdicts_filter_by_artifact(self) -> None:
        gate = _gate()
        gate.register_formula("alpha_model", _FORMULA)
        gate.register_formula("beta_model", "beta formula")
        gate.verify(_product())
        gate.verify(_product(artifact="beta_model", text="beta formula"))
        assert len(gate.verdicts("alpha_model")) == 1
        assert len(gate.verdicts("beta_model")) == 1
        assert gate.verdicts("ghost") == ()
        with pytest.raises(ConstructionGateError):
            gate.verdicts("")

    def test_record_sink_exception_not_blocking(self) -> None:
        def boom(verdict) -> None:
            raise RuntimeError("sink down")

        gate = ConstructionGovernorGate(clock=lambda: _T0, impact_threshold=3, record_sink=boom)
        gate.register_formula("alpha_model", _FORMULA)
        verdict = gate.verify(_product())
        assert verdict.decision is GateDecision.PASS
        assert len(gate.verdicts()) == 1  # 留痕路由异常不改写判定


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_input_same_output(self) -> None:
        def run() -> list[tuple]:
            gate = _registered(_gate(threshold=2, approval=lambda req: True))
            out = []
            for text, paths in (
                (_PRODUCT, ("a",)),
                ("drifted", ("a", "b", "c")),
                (_PRODUCT, ("a", "b", "c")),
            ):
                verdict = gate.verify(_product(text=text, paths=paths))
                out.append(
                    (verdict.decision, verdict.allowed_paths, verdict.truncated_paths, verdict.actual_fingerprint)
                )
            return out

        assert run() == run()
