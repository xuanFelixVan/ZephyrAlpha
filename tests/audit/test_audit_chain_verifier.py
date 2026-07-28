# [A_test] module_id: MOD-GOV_audit_chain_verifier | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §4

# [MODULE] tests.test_audit_chain_verifier

# [INVARIANTS] chain hash integrity; no placeholder code

# [MODIFY-GUARD] none

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] pytest exit 0 on pass; exit non-zero on fail

# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from zephyr.gov_enforcement.rule_enforcement.audit_chain_verifier import AuditChainVerifier, AuditEntry, AuditReport
from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_context import GateContext, GateResult, GateStatus


@pytest.fixture(autouse=True)
def _isolated_persist_path(tmp_path, monkeypatch):
    """5.37.8：隔离门禁链持久化路径到 tmp_path，防测试写入生产 data/audit_trail/。

    通过 ZEPHYR_GATE_CHAIN_PATH 环境变量覆盖默认持久化路径
    （ARCH-BENCH-LEAK-001：测试禁止写生产路径）。
    """
    monkeypatch.setenv("ZEPHYR_GATE_CHAIN_PATH", str(tmp_path / "gate_chain.jsonl"))


def _make_result(
    gate_id: str = "G1", status: GateStatus = GateStatus.PASS, reasons: list[str] | None = None
) -> GateResult:
    return GateResult(
        gate_id=gate_id,
        status=status,
        reasons=reasons or [],
        timestamp=datetime(2026, 5, 22, 12, 0, 0, tzinfo=UTC),
    )


def _make_ctx(session_id: str = "sess-001") -> GateContext:
    return GateContext(session_id=session_id, task_id="T-1", layer="core")


def _append_sync(verifier: AuditChainVerifier, gate_id: str, result: GateResult) -> AuditEntry:
    entry = verifier.append(gate_id, result)
    entry.timestamp = result.timestamp
    return entry


class TestAuditEntry:
    def test_fields_assigned(self):
        entry = AuditEntry(
            gate_id="G1",
            status=GateStatus.PASS,
            reasons=["ok"],
            previous_hash="0" * 64,
            hash="abc",
        )
        assert entry.gate_id == "G1"
        assert entry.status == GateStatus.PASS
        assert entry.reasons == ["ok"]
        assert entry.previous_hash == "0" * 64
        assert entry.hash == "abc"
        assert isinstance(entry.timestamp, datetime)

    def test_default_timestamp_is_utc_now(self):
        before = datetime.now(UTC)
        entry = AuditEntry(gate_id="G0", status=GateStatus.FAIL, reasons=[], previous_hash="", hash="")
        after = datetime.now(UTC)
        assert before <= entry.timestamp <= after

    def test_reasons_shares_reference_on_direct_construction(self):
        reasons = ["r1"]
        entry = AuditEntry(gate_id="G1", status=GateStatus.PASS, reasons=reasons, previous_hash="", hash="")
        reasons.append("r2")
        assert entry.reasons == ["r1", "r2"]


class TestAuditReport:
    def test_summary_chain_ok_reproduced_ok(self):
        report = AuditReport(entries=[], chain_valid=True, reproduced=True)
        s = report.summary()
        assert "0 entries" in s
        assert "chain=OK" in s
        assert "reproduced=OK" in s

    def test_summary_chain_broken_reproduced_mismatch(self):
        report = AuditReport(entries=[], chain_valid=False, reproduced=False)
        s = report.summary()
        assert "chain=BROKEN" in s
        assert "reproduced=MISMATCH" in s

    def test_summary_with_entries(self):
        e = AuditEntry(gate_id="G1", status=GateStatus.PASS, reasons=[], previous_hash="", hash="x")
        report = AuditReport(entries=[e], chain_valid=True, reproduced=True)
        assert "1 entries" in report.summary()

    def test_verified_at_default(self):
        before = datetime.now(UTC)
        report = AuditReport(entries=[], chain_valid=True, reproduced=True)
        after = datetime.now(UTC)
        assert before <= report.verified_at <= after


class TestAuditChainVerifierInit:
    def test_empty_on_creation(self):
        v = AuditChainVerifier()
        assert v.length == 0

    def test_chain_is_initially_empty(self):
        v = AuditChainVerifier()
        report = v.verify_chain()
        assert report.chain_valid is True
        assert report.entries == []
        assert report.reproduced is True


class TestAuditChainVerifierAppend:
    def test_append_single_entry(self):
        v = AuditChainVerifier()
        result = _make_result("G1", GateStatus.PASS)
        entry = v.append("G1", result)
        assert isinstance(entry, AuditEntry)
        assert entry.gate_id == "G1"
        assert entry.status == GateStatus.PASS
        assert entry.previous_hash == "0" * 64
        assert len(entry.hash) == 64
        assert v.length == 1

    def test_append_multiple_entries_chain_links(self):
        v = AuditChainVerifier()
        r1 = _make_result("G1", GateStatus.PASS)
        r2 = _make_result("G2", GateStatus.FAIL, reasons=["bad"])
        e1 = v.append("G1", r1)
        e2 = v.append("G2", r2)
        assert e2.previous_hash == e1.hash
        assert v.length == 2

    def test_append_copies_reasons(self):
        v = AuditChainVerifier()
        reasons = ["original"]
        result = _make_result("G1", GateStatus.FAIL, reasons=reasons)
        entry = v.append("G1", result)
        reasons.append("extra")
        assert entry.reasons == ["original"]

    def test_append_with_empty_reasons(self):
        v = AuditChainVerifier()
        result = _make_result("G1", GateStatus.PASS, reasons=[])
        entry = v.append("G1", result)
        assert entry.reasons == []

    def test_append_with_multiple_reasons(self):
        v = AuditChainVerifier()
        result = _make_result("G1", GateStatus.FAIL, reasons=["r1", "r2", "r3"])
        entry = v.append("G1", result)
        assert entry.reasons == ["r1", "r2", "r3"]

    def test_append_different_statuses(self):
        v = AuditChainVerifier()
        for status in GateStatus:
            result = _make_result(f"G-{status.name}", status)
            entry = v.append(f"G-{status.name}", result)
            assert entry.status == status


class TestAuditChainVerifierVerifyChain:
    def test_verify_empty_chain(self):
        v = AuditChainVerifier()
        report = v.verify_chain()
        assert report.chain_valid is True
        assert report.reproduced is True

    def test_verify_valid_chain(self):
        v = AuditChainVerifier()
        _append_sync(v, "G1", _make_result("G1", GateStatus.PASS))
        _append_sync(v, "G2", _make_result("G2", GateStatus.FAIL, reasons=["err"]))
        report = v.verify_chain()
        assert report.chain_valid is True
        assert report.reproduced is True

    def test_verify_tampered_hash_breaks_chain(self):
        v = AuditChainVerifier()
        _append_sync(v, "G1", _make_result("G1", GateStatus.PASS))
        v.chain[0].hash = "tampered_hash_value_that_is_wrong"
        report = v.verify_chain()
        assert report.chain_valid is False

    def test_verify_tampered_previous_hash_breaks_chain(self):
        v = AuditChainVerifier()
        _append_sync(v, "G1", _make_result("G1", GateStatus.PASS))
        _append_sync(v, "G2", _make_result("G2", GateStatus.PASS))
        v.chain[1].previous_hash = "wrong_previous_hash"
        report = v.verify_chain()
        assert report.chain_valid is False

    def test_verify_report_contains_all_entries(self):
        v = AuditChainVerifier()
        _append_sync(v, "G1", _make_result("G1", GateStatus.PASS))
        _append_sync(v, "G2", _make_result("G2", GateStatus.FAIL, reasons=["x"]))
        report = v.verify_chain()
        assert len(report.entries) == 2

    def test_verify_report_entries_are_copies(self):
        v = AuditChainVerifier()
        _append_sync(v, "G1", _make_result("G1", GateStatus.PASS))
        report = v.verify_chain()
        report.entries.clear()
        assert v.length == 1

    def test_verify_chain_timestamp_mismatch_breaks_chain(self):
        v = AuditChainVerifier()
        v.append("G1", _make_result("G1", GateStatus.PASS))
        report = v.verify_chain()
        assert report.chain_valid is False


class TestAuditChainVerifierReplay:
    def test_replay_all_match(self):
        v = AuditChainVerifier()
        _append_sync(v, "G1", _make_result("G1", GateStatus.PASS))
        _append_sync(v, "G2", _make_result("G2", GateStatus.FAIL, reasons=["err"]))
        ctx = _make_ctx()
        checkers = {
            "G1": lambda c: _make_result("G1", GateStatus.PASS),
            "G2": lambda c: _make_result("G2", GateStatus.FAIL, reasons=["err"]),
        }
        report = v.replay(ctx, checkers)
        assert report.reproduced is True
        assert report.chain_valid is True

    def test_replay_status_mismatch(self):
        v = AuditChainVerifier()
        _append_sync(v, "G1", _make_result("G1", GateStatus.PASS))
        ctx = _make_ctx()
        checkers = {
            "G1": lambda c: _make_result("G1", GateStatus.FAIL, reasons=["different"]),
        }
        report = v.replay(ctx, checkers)
        assert report.reproduced is False

    def test_replay_missing_gate_in_chain(self):
        v = AuditChainVerifier()
        _append_sync(v, "G1", _make_result("G1", GateStatus.PASS))
        ctx = _make_ctx()
        checkers = {
            "G1": lambda c: _make_result("G1", GateStatus.PASS),
            "G2": lambda c: _make_result("G2", GateStatus.PASS),
        }
        report = v.replay(ctx, checkers)
        assert report.reproduced is False

    def test_replay_empty_checkers(self):
        v = AuditChainVerifier()
        _append_sync(v, "G1", _make_result("G1", GateStatus.PASS))
        ctx = _make_ctx()
        report = v.replay(ctx, {})
        assert report.reproduced is True

    def test_replay_uses_last_matching_entry(self):
        v = AuditChainVerifier()
        _append_sync(v, "G1", _make_result("G1", GateStatus.PASS))
        _append_sync(v, "G1", _make_result("G1", GateStatus.FAIL, reasons=["retry"]))
        ctx = _make_ctx()
        checkers = {
            "G1": lambda c: _make_result("G1", GateStatus.FAIL, reasons=["retry"]),
        }
        report = v.replay(ctx, checkers)
        assert report.reproduced is True


class TestAuditChainVerifierComputeHash:
    def test_deterministic(self):
        payload = {"gate_id": "G1", "status": "PASS", "reasons": [], "previous_hash": "0" * 64}
        h1 = AuditChainVerifier.compute_hash(payload)
        h2 = AuditChainVerifier.compute_hash(payload)
        assert h1 == h2

    def test_different_payload_different_hash(self):
        p1 = {"gate_id": "G1", "status": "PASS", "reasons": [], "previous_hash": "0" * 64}
        p2 = {"gate_id": "G2", "status": "PASS", "reasons": [], "previous_hash": "0" * 64}
        assert AuditChainVerifier.compute_hash(p1) != AuditChainVerifier.compute_hash(p2)

    def test_hash_is_sha256_hex(self):
        payload = {"key": "value"}
        h = AuditChainVerifier.compute_hash(payload)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_empty_payload(self):
        h = AuditChainVerifier.compute_hash({})
        assert len(h) == 64

    def test_key_order_does_not_matter(self):
        p1 = {"a": "1", "b": "2"}
        p2 = {"b": "2", "a": "1"}
        assert AuditChainVerifier.compute_hash(p1) == AuditChainVerifier.compute_hash(p2)


class TestAuditChainVerifierClear:
    def test_clear_resets_length(self):
        v = AuditChainVerifier()
        v.append("G1", _make_result("G1", GateStatus.PASS))
        assert v.length == 1
        v.clear(confirm=True)
        assert v.length == 0

    def test_clear_resets_hash_chain(self):
        v = AuditChainVerifier()
        v.append("G1", _make_result("G1", GateStatus.PASS))
        v.clear(confirm=True)
        e2 = v.append("G2", _make_result("G2", GateStatus.PASS))
        assert e2.previous_hash == "0" * 64

    def test_clear_on_empty_verifier(self):
        v = AuditChainVerifier()
        v.clear(confirm=True)
        assert v.length == 0

    def test_clear_then_rebuild_chain(self):
        v = AuditChainVerifier()
        _append_sync(v, "G1", _make_result("G1", GateStatus.PASS))
        v.clear(confirm=True)
        _append_sync(v, "G2", _make_result("G2", GateStatus.PASS))
        _append_sync(v, "G3", _make_result("G3", GateStatus.FAIL, reasons=["x"]))
        report = v.verify_chain()
        assert report.chain_valid is True
        assert v.length == 2


class TestAuditChainVerifierClearPermission:
    """5.37.9：clear() 权限保护——必须显式 confirm=True。"""

    def test_clear_without_confirm_raises(self):
        v = AuditChainVerifier()
        v.append("G1", _make_result("G1", GateStatus.PASS))
        with pytest.raises(PermissionError):
            v.clear()
        assert v.length == 1  # 链未被抹除

    def test_clear_without_confirm_on_empty_raises(self):
        v = AuditChainVerifier()
        with pytest.raises(PermissionError):
            v.clear()

    def test_clear_with_confirm_and_reason(self):
        v = AuditChainVerifier()
        v.append("G1", _make_result("G1", GateStatus.PASS))
        v.clear(reason="test reset", confirm=True, cleared_by="pytest")
        assert v.length == 0


class TestAuditChainVerifierPersistence:
    """5.37.8：审计链 append-only JSONL 持久化 + 重启恢复。"""

    def test_append_persists_to_jsonl(self, tmp_path):
        path = tmp_path / "chain.jsonl"
        v = AuditChainVerifier(persist_path=path)
        v.append("G1", _make_result("G1", GateStatus.PASS))
        assert path.exists()
        lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == 1
        import json as _json

        raw = _json.loads(lines[0])
        assert raw["gate_id"] == "G1"
        assert raw["status"] == "PASS"
        assert len(raw["hash"]) == 64
        assert raw["previous_hash"] == "0" * 64

    def test_reload_restores_chain_across_instances(self, tmp_path):
        path = tmp_path / "chain.jsonl"
        v1 = AuditChainVerifier(persist_path=path)
        # 用 _append_sync 对齐 entry.timestamp（hash 以 result.timestamp 计算，
        # verify_chain 以 entry.timestamp 重算——与既有测试契约一致）
        _append_sync(v1, "G1", _make_result("G1", GateStatus.PASS))
        _append_sync(v1, "G2", _make_result("G2", GateStatus.FAIL, reasons=["x"]))
        tail_hash = v1.last_hash

        v2 = AuditChainVerifier(persist_path=path)
        assert v2.length == 2
        assert v2.last_hash == tail_hash
        assert v2.verify_chain().chain_valid is True

    def test_clear_confirm_removes_persisted_file(self, tmp_path):
        path = tmp_path / "chain.jsonl"
        v = AuditChainVerifier(persist_path=path)
        v.append("G1", _make_result("G1", GateStatus.PASS))
        assert path.exists()
        v.clear(confirm=True)
        assert not path.exists()
        # 新实例从空链开始
        v2 = AuditChainVerifier(persist_path=path)
        assert v2.length == 0


class TestAuditChainVerifierLength:
    def test_length_increments(self):
        v = AuditChainVerifier()
        assert v.length == 0
        v.append("G1", _make_result("G1", GateStatus.PASS))
        assert v.length == 1
        v.append("G2", _make_result("G2", GateStatus.PASS))
        assert v.length == 2

    def test_length_after_clear(self):
        v = AuditChainVerifier()
        v.append("G1", _make_result("G1", GateStatus.PASS))
        v.clear(confirm=True)
        assert v.length == 0


class TestAuditChainVerifierBoundary:
    def test_append_with_none_reasons_in_result(self):
        v = AuditChainVerifier()
        result = GateResult(
            gate_id="G1",
            status=GateStatus.PASS,
            reasons=None,
            timestamp=datetime(2026, 5, 22, 12, 0, 0, tzinfo=UTC),
        )
        with pytest.raises(TypeError):
            v.append("G1", result)

    def test_replay_with_tampered_chain(self):
        v = AuditChainVerifier()
        _append_sync(v, "G1", _make_result("G1", GateStatus.PASS))
        v.chain[0].hash = "broken"
        ctx = _make_ctx()
        checkers = {"G1": lambda c: _make_result("G1", GateStatus.PASS)}
        report = v.replay(ctx, checkers)
        assert report.chain_valid is False

    def test_verify_chain_single_entry_valid(self):
        v = AuditChainVerifier()
        _append_sync(v, "G1", _make_result("G1", GateStatus.PASS))
        report = v.verify_chain()
        assert report.chain_valid is True
        assert len(report.entries) == 1

    def test_large_chain_integrity(self):
        v = AuditChainVerifier()
        for i in range(50):
            status = GateStatus.PASS if i % 2 == 0 else GateStatus.FAIL
            reasons = [] if status == GateStatus.PASS else [f"fail-{i}"]
            _append_sync(v, f"G{i}", _make_result(f"G{i}", status, reasons=reasons))
        report = v.verify_chain()
        assert report.chain_valid is True
        assert v.length == 50

    def test_append_entry_hash_matches_compute_hash(self):
        v = AuditChainVerifier()
        result = _make_result("G1", GateStatus.PASS, reasons=["ok"])
        entry = v.append("G1", result)
        payload = {
            "gate_id": "G1",
            "status": result.status.name,
            "reasons": list(result.reasons),
            "timestamp": result.timestamp.isoformat(),
            "previous_hash": "0" * 64,
        }
        expected = AuditChainVerifier.compute_hash(payload)
        assert entry.hash == expected
