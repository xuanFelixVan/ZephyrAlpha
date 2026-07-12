# [A_test] module_id: SRC-TST-1040 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §4.2

# [MODULE] tests.test_gate_context

# [INVARIANTS] GateStatus has exactly 5 members; GateResult.passed is derived from status; GateContext.deserialize must accept serialize output

# [MODIFY-GUARD] changes require source gate_context.py review

# [CONSUMERS] pytest

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] no exceptions from properties/summary; deserialize raises KeyError on missing session_id

# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import pytest

from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_context import GateContext, GateResult, GateStatus, GateViolation


class TestGateStatus:
    def test_has_five_members(self):
        assert len(GateStatus) == 5

    def test_member_values(self):
        expected = {"PASS", "FAIL", "SKIP", "WAIVED", "ERROR"}
        assert set(m.name for m in GateStatus) == expected

    def test_members_are_distinct(self):
        values = [m.value for m in GateStatus]
        assert len(values) == len(set(values))


class TestGateViolation:
    def test_instantiation_required_fields(self):
        v = GateViolation(check_id="C01", check_name="check_a", severity="P0", message="msg")
        assert v.check_id == "C01"
        assert v.check_name == "check_a"
        assert v.severity == "P0"
        assert v.message == "msg"
        assert v.detail is None

    def test_instantiation_with_detail(self):
        v = GateViolation(check_id="C02", check_name="check_b", severity="P1", message="msg", detail="extra")
        assert v.detail == "extra"

    def test_empty_strings(self):
        v = GateViolation(check_id="", check_name="", severity="", message="")
        assert v.check_id == ""
        assert v.severity == ""


class TestGateResult:
    def test_instantiation_defaults(self):
        r = GateResult(gate_id="G1", status=GateStatus.PASS)
        assert r.gate_id == "G1"
        assert r.status == GateStatus.PASS
        assert r.reasons == []
        assert r.affected_tasks == []
        assert r.task_id == ""
        assert r.violations == []
        assert r.details == {}
        assert isinstance(r.timestamp, datetime)

    def test_instantiation_full(self):
        now = datetime.now(UTC)
        v = GateViolation(check_id="C01", check_name="n", severity="P0", message="m")
        r = GateResult(
            gate_id="G2",
            status=GateStatus.FAIL,
            reasons=["r1"],
            affected_tasks=["T1"],
            timestamp=now,
            task_id="T001",
            violations=[v],
            details={"k": "v"},
        )
        assert r.gate_id == "G2"
        assert r.status == GateStatus.FAIL
        assert r.reasons == ["r1"]
        assert r.affected_tasks == ["T1"]
        assert r.timestamp == now
        assert r.task_id == "T001"
        assert r.violations == [v]
        assert r.details == {"k": "v"}

    def test_passed_property_true(self):
        r = GateResult(gate_id="G1", status=GateStatus.PASS)
        assert r.passed is True

    def test_passed_property_false(self):
        for st in (GateStatus.FAIL, GateStatus.SKIP, GateStatus.WAIVED, GateStatus.ERROR):
            r = GateResult(gate_id="G1", status=st)
            assert r.passed is False, f"expected False for {st.name}"

    def test_p0_violations_filters(self):
        v0 = GateViolation(check_id="C01", check_name="n", severity="P0", message="m1")
        v1 = GateViolation(check_id="C02", check_name="n", severity="P1", message="m2")
        v2 = GateViolation(check_id="C03", check_name="n", severity="P0", message="m3")
        r = GateResult(gate_id="G1", status=GateStatus.FAIL, violations=[v0, v1, v2])
        assert len(r.p0_violations) == 2
        assert r.p0_violations[0].check_id == "C01"
        assert r.p0_violations[1].check_id == "C03"

    def test_p0_violations_empty(self):
        r = GateResult(gate_id="G1", status=GateStatus.PASS)
        assert r.p0_violations == []

    def test_has_p0_true(self):
        v = GateViolation(check_id="C01", check_name="n", severity="P0", message="m")
        r = GateResult(gate_id="G1", status=GateStatus.FAIL, violations=[v])
        assert r.has_p0 is True

    def test_has_p0_false(self):
        v = GateViolation(check_id="C01", check_name="n", severity="P1", message="m")
        r = GateResult(gate_id="G1", status=GateStatus.FAIL, violations=[v])
        assert r.has_p0 is False

    def test_has_p0_no_violations(self):
        r = GateResult(gate_id="G1", status=GateStatus.PASS)
        assert r.has_p0 is False

    def test_summary_pass(self):
        r = GateResult(gate_id="G1", status=GateStatus.PASS, task_id="T001")
        s = r.summary()
        assert "[PASS]" in s
        assert "G1" in s
        assert "T001" in s

    def test_summary_fail(self):
        v = GateViolation(check_id="C01", check_name="n", severity="P0", message="m")
        r = GateResult(gate_id="G2", status=GateStatus.FAIL, task_id="T002", violations=[v])
        s = r.summary()
        assert "[FAIL]" in s
        assert "G2" in s
        assert "T002" in s
        assert "violations=1" in s
        assert "P0=1" in s

    def test_summary_fail_no_violations(self):
        r = GateResult(gate_id="G3", status=GateStatus.FAIL, task_id="T003")
        s = r.summary()
        assert "[FAIL]" in s
        assert "violations=0" in s
        assert "P0=0" in s

    def test_from_engine_result_identity(self):
        original = GateResult(gate_id="G1", status=GateStatus.PASS)
        result = GateResult.from_engine_result(original)
        assert result is original

    def test_from_engine_result_duck_type_passed(self):
        @dataclass
        class FakeEngine:
            passed: bool = True
            gate_id: str = "G1"
            task_id: str = "T001"
            violations: list = None
            details: dict = None
            evaluated_at: str = ""

        fake = FakeEngine()
        result = GateResult.from_engine_result(fake)
        assert result.status == GateStatus.PASS
        assert result.gate_id == "G1"
        assert result.task_id == "T001"

    def test_from_engine_result_duck_type_failed(self):
        @dataclass
        class FakeEngine:
            passed: bool = False
            gate_id: str = "G2"
            task_id: str = "T002"
            violations: list = None
            details: dict = None
            evaluated_at: str = ""

        fake = FakeEngine()
        result = GateResult.from_engine_result(fake)
        assert result.status == GateStatus.FAIL

    def test_from_engine_result_with_violations(self):
        @dataclass
        class FakeViolation:
            check_id: str = "C01"
            check_name: str = "name"
            severity: str = "P0"
            message: str = "bad"
            detail: str = None

        @dataclass
        class FakeEngine:
            passed: bool = False
            gate_id: str = "G1"
            task_id: str = "T1"
            violations: list = None
            details: dict = None
            evaluated_at: str = ""

        fake = FakeEngine(violations=[FakeViolation()])
        result = GateResult.from_engine_result(fake)
        assert len(result.violations) == 1
        assert result.violations[0].check_id == "C01"
        assert result.reasons == ["bad"]

    def test_from_engine_result_with_native_violations(self):
        v = GateViolation(check_id="C01", check_name="n", severity="P0", message="native")
        fake = type(
            "Fake",
            (),
            {"passed": False, "gate_id": "G1", "task_id": "", "violations": [v], "details": {}, "evaluated_at": ""},
        )()
        result = GateResult.from_engine_result(fake)
        assert result.violations[0] is v
        assert result.reasons == ["native"]

    def test_from_engine_result_with_evaluated_at(self):
        ts = "2026-01-15T10:30:00+00:00"
        fake = type(
            "Fake",
            (),
            {"passed": True, "gate_id": "G1", "task_id": "", "violations": [], "details": {}, "evaluated_at": ts},
        )()
        result = GateResult.from_engine_result(fake)
        assert result.timestamp.year == 2026
        assert result.timestamp.month == 1
        assert result.timestamp.day == 15

    def test_from_engine_result_invalid_evaluated_at(self):
        fake = type(
            "Fake",
            (),
            {
                "passed": True,
                "gate_id": "G1",
                "task_id": "",
                "violations": [],
                "details": {},
                "evaluated_at": "not-a-date",
            },
        )()
        result = GateResult.from_engine_result(fake)
        assert isinstance(result.timestamp, datetime)

    def test_from_engine_result_missing_attrs(self):
        fake = type("Fake", (), {})()
        result = GateResult.from_engine_result(fake)
        assert result.status == GateStatus.FAIL
        assert result.gate_id == ""
        assert result.task_id == ""

    def test_from_engine_result_violations_without_message_attr(self):
        fake_v = type("FakeV", (), {"check_id": "C1", "check_name": "n", "severity": "P2"})()
        fake = type(
            "Fake",
            (),
            {
                "passed": False,
                "gate_id": "G1",
                "task_id": "",
                "violations": [fake_v],
                "details": {},
                "evaluated_at": "",
            },
        )()
        result = GateResult.from_engine_result(fake)
        assert len(result.violations) == 0


class TestGateContext:
    def test_instantiation_defaults(self):
        ctx = GateContext(session_id="sess-001")
        assert ctx.session_id == "sess-001"
        assert ctx.task_id is None
        assert ctx.layer is None
        assert ctx.previous_results == []
        assert ctx.metadata == {}

    def test_instantiation_full(self):
        r = GateResult(gate_id="G1", status=GateStatus.PASS)
        ctx = GateContext(
            session_id="sess-002",
            task_id="T001",
            layer="L2",
            previous_results=[r],
            metadata={"key": "val"},
        )
        assert ctx.session_id == "sess-002"
        assert ctx.task_id == "T001"
        assert ctx.layer == "L2"
        assert len(ctx.previous_results) == 1
        assert ctx.metadata == {"key": "val"}

    def test_serialize_basic(self):
        ctx = GateContext(session_id="sess-003", task_id="T001", layer="L1")
        d = ctx.serialize()
        assert d["session_id"] == "sess-003"
        assert d["task_id"] == "T001"
        assert d["layer"] == "L1"
        assert d["previous_results"] == []
        assert d["metadata"] == {}

    def test_serialize_with_results(self):
        v = GateViolation(check_id="C01", check_name="n", severity="P0", message="m")
        r = GateResult(gate_id="G1", status=GateStatus.FAIL, violations=[v], task_id="T1")
        ctx = GateContext(session_id="sess-004", previous_results=[r])
        d = ctx.serialize()
        assert len(d["previous_results"]) == 1
        pr = d["previous_results"][0]
        assert pr["gate_id"] == "G1"
        assert pr["status"] == "FAIL"
        assert pr["passed"] is False
        assert len(pr["violations"]) == 1
        assert pr["violations"][0]["check_id"] == "C01"
        assert "timestamp" in pr

    def test_serialize_with_metadata(self):
        ctx = GateContext(session_id="sess-005", metadata={"env": "prod"})
        d = ctx.serialize()
        assert d["metadata"] == {"env": "prod"}

    def test_deserialize_basic(self):
        data = {"session_id": "sess-010", "task_id": "T010", "layer": "L2"}
        ctx = GateContext.deserialize(data)
        assert ctx.session_id == "sess-010"
        assert ctx.task_id == "T010"
        assert ctx.layer == "L2"

    def test_deserialize_minimal(self):
        data = {"session_id": "sess-011"}
        ctx = GateContext.deserialize(data)
        assert ctx.session_id == "sess-011"
        assert ctx.task_id is None
        assert ctx.layer is None
        assert ctx.previous_results == []
        assert ctx.metadata == {}

    def test_deserialize_with_metadata(self):
        data = {"session_id": "sess-012", "metadata": {"k": "v"}}
        ctx = GateContext.deserialize(data)
        assert ctx.metadata == {"k": "v"}

    def test_deserialize_missing_session_id_raises(self):
        with pytest.raises(KeyError):
            GateContext.deserialize({})

    def test_roundtrip_serialize_deserialize(self):
        ctx = GateContext(session_id="sess-020", task_id="T020", layer="L3", metadata={"a": "b"})
        d = ctx.serialize()
        ctx2 = GateContext.deserialize(d)
        assert ctx2.session_id == ctx.session_id
        assert ctx2.task_id == ctx.task_id
        assert ctx2.layer == ctx.layer
        assert ctx2.metadata == ctx.metadata

    def test_empty_session_id(self):
        ctx = GateContext(session_id="")
        assert ctx.session_id == ""
        d = ctx.serialize()
        ctx2 = GateContext.deserialize(d)
        assert ctx2.session_id == ""

    def test_none_task_id_and_layer(self):
        ctx = GateContext(session_id="sess-030")
        d = ctx.serialize()
        assert d["task_id"] is None
        assert d["layer"] is None

    def test_multiple_previous_results(self):
        r1 = GateResult(gate_id="G1", status=GateStatus.PASS, task_id="T1")
        r2 = GateResult(gate_id="G2", status=GateStatus.FAIL, task_id="T2")
        ctx = GateContext(session_id="sess-040", previous_results=[r1, r2])
        d = ctx.serialize()
        assert len(d["previous_results"]) == 2
        assert d["previous_results"][0]["status"] == "PASS"
        assert d["previous_results"][1]["status"] == "FAIL"
