# [BLUEPRINT] MOD-CMP-013 | docs/03_modules/_domain_compliance/evidence_chain_generator/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-CMP-013 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.compliance.test_evidence_chain_generator
# [TESTS] src/zephyr/compliance/evidence_chain_generator.py
"""MOD-CMP-013 单元测试：evidence_chain_generator 合规证据链生成器。

蓝图验收（B1-00312/CAND-CMP-003，§0定位/§1规则）：
采集器注册表注入自动采集 → append-only prev_hash 哈希链（注入 root 落盘 JSONL）→
按时间/类型/标的检索导出。时钟/落盘全注入内存替身与 tmp_path，不触网。
"""

from __future__ import annotations

import datetime
import json

import pytest

pytest.importorskip(
    "zephyr.compliance.evidence_chain_generator",
    reason="evidence_chain_generator not importable",
)

from zephyr.compliance.evidence_chain_generator import (  # noqa: E402
    GENESIS_HASH,
    EvidenceChainError,
    EvidenceChainGenerator,
    EvidenceSnapshot,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)
_T1 = datetime.datetime(2026, 8, 25, 10, 0, 0)
_T2 = datetime.datetime(2026, 8, 25, 14, 0, 0)


def _snap(
    snapshot_id: str = "ev-1",
    evidence_type: str = "order",
    symbol: str = "600519",
    taken_at: datetime.datetime = _T0,
    payload: dict | None = None,
) -> EvidenceSnapshot:
    return EvidenceSnapshot(
        snapshot_id=snapshot_id,
        evidence_type=evidence_type,
        symbol=symbol,
        payload={"qty": 100, "price": 1700.0} if payload is None else payload,
        taken_at=taken_at,
    )


def _gen(root=None) -> EvidenceChainGenerator:
    return EvidenceChainGenerator(clock=lambda: _T0, root=root)


# ──────────────────────────────────────────────────────────────────────────────
# 采集器注册表
# ──────────────────────────────────────────────────────────────────────────────


class TestCollectorRegistry:
    def test_register_ok(self) -> None:
        gen = _gen()
        gen.register_collector("orders", lambda: [_snap()])
        records = gen.collect()
        assert len(records) == 1

    def test_duplicate_collector_raises(self) -> None:
        gen = _gen()
        gen.register_collector("orders", lambda: [])
        with pytest.raises(EvidenceChainError):
            gen.register_collector("orders", lambda: [])

    def test_empty_name_raises(self) -> None:
        gen = _gen()
        with pytest.raises(EvidenceChainError):
            gen.register_collector("", lambda: [])

    def test_non_callable_raises(self) -> None:
        gen = _gen()
        with pytest.raises(EvidenceChainError):
            gen.register_collector("bad", "not-a-callable")

    def test_collect_deterministic_order_by_name(self) -> None:
        gen = _gen()
        gen.register_collector("b_later", lambda: [_snap("ev-b")])
        gen.register_collector("a_first", lambda: [_snap("ev-a")])
        records = gen.collect()
        assert [r.snapshot.snapshot_id for r in records] == ["ev-a", "ev-b"]


# ──────────────────────────────────────────────────────────────────────────────
# 哈希链（append-only + prev_hash）
# ──────────────────────────────────────────────────────────────────────────────


class TestHashChain:
    def test_genesis_prev_hash(self) -> None:
        gen = _gen()
        gen.register_collector("orders", lambda: [_snap()])
        (record,) = gen.collect()
        assert record.seq == 1
        assert record.prev_hash == GENESIS_HASH
        assert len(record.record_hash) == 64

    def test_chain_links(self) -> None:
        gen = _gen()
        gen.register_collector("orders", lambda: [_snap("ev-1"), _snap("ev-2")])
        r1, r2 = gen.collect()
        assert r2.prev_hash == r1.record_hash
        assert r2.seq == 2

    def test_verify_ok(self) -> None:
        gen = _gen()
        gen.register_collector("orders", lambda: [_snap("ev-1"), _snap("ev-2")])
        gen.collect()
        assert gen.verify_chain() is True

    def test_tamper_detected(self) -> None:
        gen = _gen()
        gen.register_collector("orders", lambda: [_snap("ev-1"), _snap("ev-2")])
        gen.collect()
        original = gen._chain[1]
        tampered = type(original)(
            seq=original.seq,
            snapshot=_snap("ev-2", payload={"qty": 999}),
            prev_hash=original.prev_hash,
            record_hash=original.record_hash,
            recorded_at=original.recorded_at,
        )
        gen._chain[1] = tampered  # 模拟篡改
        with pytest.raises(EvidenceChainError):
            gen.verify_chain()

    def test_same_input_same_hash(self) -> None:
        g1 = _gen()
        g1.register_collector("orders", lambda: [_snap()])
        g2 = _gen()
        g2.register_collector("orders", lambda: [_snap()])
        assert g1.collect()[0].record_hash == g2.collect()[0].record_hash


# ──────────────────────────────────────────────────────────────────────────────
# 落盘（注入 root）
# ──────────────────────────────────────────────────────────────────────────────


class TestPersist:
    def test_persist_jsonl(self, tmp_path) -> None:
        gen = _gen(root=tmp_path)
        gen.register_collector("orders", lambda: [_snap("ev-1"), _snap("ev-2")])
        gen.collect()
        lines = (tmp_path / "evidence_chain.jsonl").read_text(encoding="utf-8").splitlines()
        assert len(lines) == 2
        first = json.loads(lines[0])
        assert first["seq"] == 1
        assert first["snapshot"]["snapshot_id"] == "ev-1"
        assert first["prev_hash"] == GENESIS_HASH

    def test_no_root_no_persist(self, tmp_path) -> None:
        gen = _gen()
        gen.register_collector("orders", lambda: [_snap()])
        gen.collect()
        assert not (tmp_path / "evidence_chain.jsonl").exists()


# ──────────────────────────────────────────────────────────────────────────────
# 非法输入 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestFailClosed:
    def test_empty_snapshot_id_raises(self) -> None:
        gen = _gen()
        gen.register_collector("orders", lambda: [_snap(snapshot_id="")])
        with pytest.raises(EvidenceChainError):
            gen.collect()

    def test_empty_evidence_type_raises(self) -> None:
        gen = _gen()
        gen.register_collector("orders", lambda: [_snap(evidence_type="")])
        with pytest.raises(EvidenceChainError):
            gen.collect()

    def test_empty_symbol_raises(self) -> None:
        gen = _gen()
        gen.register_collector("orders", lambda: [_snap(symbol="")])
        with pytest.raises(EvidenceChainError):
            gen.collect()

    def test_unserializable_payload_raises(self) -> None:
        gen = _gen()
        gen.register_collector("orders", lambda: [_snap(payload={"bad": object()})])
        with pytest.raises(EvidenceChainError):
            gen.collect()

    def test_invalid_query_range_raises(self) -> None:
        gen = _gen()
        with pytest.raises(EvidenceChainError):
            gen.query(start=_T2, end=_T0)


# ──────────────────────────────────────────────────────────────────────────────
# 检索导出
# ──────────────────────────────────────────────────────────────────────────────


class TestQueryExport:
    def _seeded(self) -> EvidenceChainGenerator:
        gen = _gen()
        gen.register_collector(
            "orders",
            lambda: [
                _snap("ev-1", evidence_type="order", symbol="600519", taken_at=_T0),
                _snap("ev-2", evidence_type="trade", symbol="600519", taken_at=_T1),
                _snap("ev-3", evidence_type="decision", symbol="000001", taken_at=_T2),
            ],
        )
        gen.collect()
        return gen

    def test_query_by_time_range(self) -> None:
        gen = self._seeded()
        out = gen.query(start=_T1, end=_T2)
        assert [r.snapshot.snapshot_id for r in out] == ["ev-2", "ev-3"]

    def test_query_by_type(self) -> None:
        gen = self._seeded()
        out = gen.query(evidence_type="trade")
        assert [r.snapshot.snapshot_id for r in out] == ["ev-2"]

    def test_query_by_symbol(self) -> None:
        gen = self._seeded()
        out = gen.query(symbol="000001")
        assert [r.snapshot.snapshot_id for r in out] == ["ev-3"]

    def test_query_combined(self) -> None:
        gen = self._seeded()
        out = gen.query(start=_T0, end=_T1, evidence_type="order", symbol="600519")
        assert [r.snapshot.snapshot_id for r in out] == ["ev-1"]

    def test_export_jsonl_full(self) -> None:
        gen = self._seeded()
        lines = gen.export_jsonl().splitlines()
        assert len(lines) == 3
        parsed = [json.loads(line) for line in lines]
        assert [p["seq"] for p in parsed] == [1, 2, 3]
        assert parsed[2]["prev_hash"] == parsed[1]["record_hash"]

    def test_export_jsonl_subset(self) -> None:
        gen = self._seeded()
        subset = gen.query(symbol="000001")
        text = gen.export_jsonl(subset)
        assert len(text.splitlines()) == 1
        assert json.loads(text)["snapshot"]["symbol"] == "000001"

    def test_export_empty_chain(self) -> None:
        gen = _gen()
        assert gen.export_jsonl() == ""

    def test_records_readonly_copy(self) -> None:
        gen = self._seeded()
        view = gen.records()
        view.clear()  # 改副本不影响链
        assert len(gen.records()) == 3
