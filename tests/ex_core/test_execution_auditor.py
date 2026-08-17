# [BLUEPRINT] MOD-EX-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""ExecutionAuditLogger 单元测试 — MOD-EX-003 / D-EX-CORE-15

覆盖: 哈希链完整性 / 篡改检测 / 八类事件 / 查询 / 报告 / frozen / 持久化 / 异常隔离
对齐 POS-009 PositionAuditLogger 同构测试模式。
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from zephyr.ex_core.audit_journal.auditor import (
    ZERO_HASH,
    AuditChainError,
    AuditSource,
    ExecutionAuditEventType,
    ExecutionAuditLogger,
    ExecutionAuditRecord,
    ExecutionAuditReport,
    _compute_record_hash,
)

# ──────────────────────────────────────────────────────────────────────────────
# fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def audit() -> ExecutionAuditLogger:
    """空审计记录器 (仅内存)。"""
    return ExecutionAuditLogger()


@pytest.fixture
def audit_with_order(audit: ExecutionAuditLogger) -> tuple[ExecutionAuditLogger, str]:
    """含一条 ORDER_CREATED 记录的审计器。"""
    order_id = "ord-001"
    audit.log_order_created(order_id, "600000.SH", {"qty": 100, "price": "10.50"})
    return audit, order_id


# ──────────────────────────────────────────────────────────────────────────────
# 基本记录
# ──────────────────────────────────────────────────────────────────────────────


class TestSingleRecord:
    """单条记录: hash 正确, prev_hash=ZERO_HASH。"""

    def test_first_record_prev_hash_is_zero(self, audit: ExecutionAuditLogger):
        rec = audit.log_order_created("ord-001", "600000.SH", {"qty": 100})
        assert rec is not None
        assert rec.prev_hash == ZERO_HASH

    def test_first_record_hash_is_sha256(self, audit: ExecutionAuditLogger):
        rec = audit.log_order_created("ord-001", "600000.SH", {"qty": 100})
        assert rec is not None
        # SHA-256 产物 = 64 hex 字符
        assert len(rec.record_hash) == 64
        assert all(c in "0123456789abcdef" for c in rec.record_hash)

    def test_record_hash_matches_recompute(self, audit: ExecutionAuditLogger):
        rec = audit.log_order_created("ord-001", "600000.SH", {"qty": 100})
        recomputed = _compute_record_hash(
            rec.record_id,
            rec.timestamp,
            rec.event_type,
            rec.order_id,
            rec.symbol,
            rec.source,
            rec.detail,
            rec.prev_hash,
        )
        assert recomputed == rec.record_hash

    def test_record_count_increments(self, audit: ExecutionAuditLogger):
        assert audit.record_count == 0
        audit.log_order_created("ord-001", "600000.SH", {})
        assert audit.record_count == 1
        audit.log_order_submitted("ord-001", "600000.SH", {})
        assert audit.record_count == 2

    def test_last_hash_empty_chain(self, audit: ExecutionAuditLogger):
        assert audit.last_hash == ZERO_HASH

    def test_last_hash_after_record(self, audit: ExecutionAuditLogger):
        rec = audit.log_order_created("ord-001", "600000.SH", {})
        assert audit.last_hash == rec.record_hash


# ──────────────────────────────────────────────────────────────────────────────
# 哈希链
# ──────────────────────────────────────────────────────────────────────────────


class TestHashChain:
    """多条链式: 每条 prev_hash = 上一条 record_hash。"""

    def test_chain_links(self, audit: ExecutionAuditLogger):
        r1 = audit.log_order_created("ord-001", "600000.SH", {})
        r2 = audit.log_order_submitted("ord-001", "600000.SH", {})
        r3 = audit.log_order_filled("ord-001", "600000.SH", {"fill_price": "10.52"})

        assert r2.prev_hash == r1.record_hash
        assert r3.prev_hash == r2.record_hash

    def test_verify_chain_empty(self, audit: ExecutionAuditLogger):
        ok, break_at = audit.verify_chain()
        assert ok is True
        assert break_at is None

    def test_verify_chain_valid(self, audit: ExecutionAuditLogger):
        audit.log_order_created("ord-001", "600000.SH", {})
        audit.log_order_submitted("ord-001", "600000.SH", {})
        audit.log_order_filled("ord-001", "600000.SH", {})

        ok, break_at = audit.verify_chain()
        assert ok is True
        assert break_at is None

    def test_verify_chain_detects_tampered_detail(self, audit: ExecutionAuditLogger):
        """篡改 detail 后 verify_chain() 返回 False + 断点。"""
        rec = audit.log_order_created("ord-001", "600000.SH", {"qty": 100})
        assert rec is not None

        # 篡改: 替换为一条 detail 被改的记录 (保持 record_hash 不变)
        tampered = ExecutionAuditRecord(
            record_id=rec.record_id,
            timestamp=rec.timestamp,
            event_type=rec.event_type,
            order_id=rec.order_id,
            symbol=rec.symbol,
            source=rec.source,
            detail={"qty": 999},  # 篡改!
            prev_hash=rec.prev_hash,
            record_hash=rec.record_hash,  # hash 没重算
        )
        audit._records[0] = tampered

        ok, break_at = audit.verify_chain()
        assert ok is False
        assert break_at == rec.record_id

    def test_verify_chain_detects_broken_link(self, audit: ExecutionAuditLogger):
        """prev_hash 链接断裂检测。"""
        r1 = audit.log_order_created("ord-001", "600000.SH", {})
        r2 = audit.log_order_submitted("ord-001", "600000.SH", {})
        assert r1 is not None and r2 is not None

        # 篡改 r2 的 prev_hash
        broken = ExecutionAuditRecord(
            record_id=r2.record_id,
            timestamp=r2.timestamp,
            event_type=r2.event_type,
            order_id=r2.order_id,
            symbol=r2.symbol,
            source=r2.source,
            detail=r2.detail,
            prev_hash="0" * 63 + "1",  # 错误的 prev_hash
            record_hash=r2.record_hash,
        )
        audit._records[1] = broken

        ok, break_at = audit.verify_chain()
        assert ok is False
        assert break_at == r2.record_id


# ──────────────────────────────────────────────────────────────────────────────
# 八类事件便捷方法
# ──────────────────────────────────────────────────────────────────────────────


class TestEightEventTypes:
    """每类事件便捷方法各记一条。"""

    @pytest.mark.parametrize(
        "method_name,event_type",
        [
            ("log_order_created", ExecutionAuditEventType.ORDER_CREATED),
            ("log_order_submitted", ExecutionAuditEventType.ORDER_SUBMITTED),
            ("log_order_filled", ExecutionAuditEventType.ORDER_FILLED),
            ("log_fill_received", ExecutionAuditEventType.FILL_RECEIVED),
            ("log_order_cancelled", ExecutionAuditEventType.ORDER_CANCELLED),
            ("log_order_rejected", ExecutionAuditEventType.ORDER_REJECTED),
            ("log_order_expired", ExecutionAuditEventType.ORDER_EXPIRED),
            ("log_idempotency_blocked", ExecutionAuditEventType.IDEMPOTENCY_BLOCKED),
        ],
    )
    def test_each_convenience_method(
        self,
        audit: ExecutionAuditLogger,
        method_name: str,
        event_type: ExecutionAuditEventType,
    ):
        method = getattr(audit, method_name)
        rec = method("ord-001", "600000.SH", {"test": True})
        assert rec is not None
        assert rec.event_type == event_type

    def test_all_eight_types_in_one_chain(self, audit: ExecutionAuditLogger):
        """一个订单完整生命周期: 8 类事件全入链。"""
        oid = "ord-lifecycle"
        sym = "000001.SZ"
        detail = {"qty": 100, "price": "10.00"}

        audit.log_order_created(oid, sym, detail)
        audit.log_order_submitted(oid, sym, detail)
        audit.log_fill_received(oid, sym, {"fill_qty": 100, "fill_price": "10.02"})
        audit.log_order_filled(oid, sym, {"avg_price": "10.02"})
        # 另一个订单的被拒/撤/过期/幂等
        audit.log_order_cancelled("ord-002", sym, {"reason": "user_cancel"})
        audit.log_order_rejected("ord-003", sym, {"reason": "insufficient_funds"})
        audit.log_order_expired("ord-004", sym, {"reason": "timeout"})
        audit.log_idempotency_blocked("ord-005", sym, {"dup_key": "key-abc"})

        assert audit.record_count == 8
        ok, _ = audit.verify_chain()
        assert ok is True


# ──────────────────────────────────────────────────────────────────────────────
# 查询
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    """按 order_id / symbol / event_type / 时间范围查询。"""

    def test_query_by_order_id(self, audit: ExecutionAuditLogger):
        audit.log_order_created("ord-001", "600000.SH", {})
        audit.log_order_created("ord-002", "000001.SZ", {})

        results = audit.query(order_id="ord-001")
        assert len(results) == 1
        assert results[0].order_id == "ord-001"

    def test_query_by_symbol(self, audit: ExecutionAuditLogger):
        audit.log_order_created("ord-001", "600000.SH", {})
        audit.log_order_created("ord-002", "600000.SH", {})
        audit.log_order_created("ord-003", "000001.SZ", {})

        results = audit.query(symbol="600000.SH")
        assert len(results) == 2
        assert all(r.symbol == "600000.SH" for r in results)

    def test_query_by_event_type(self, audit: ExecutionAuditLogger):
        audit.log_order_created("ord-001", "600000.SH", {})
        audit.log_order_submitted("ord-001", "600000.SH", {})
        audit.log_order_filled("ord-001", "600000.SH", {})

        results = audit.query(event_type=ExecutionAuditEventType.ORDER_FILLED)
        assert len(results) == 1
        assert results[0].event_type == ExecutionAuditEventType.ORDER_FILLED

    def test_query_by_time_range(self, audit: ExecutionAuditLogger):
        t0 = datetime(2026, 1, 1, 9, 30, tzinfo=UTC)
        t1 = t0 + timedelta(minutes=1)
        t2 = t0 + timedelta(minutes=5)
        t3 = t0 + timedelta(minutes=10)

        audit.log(ExecutionAuditEventType.ORDER_CREATED, "o1", "S", AuditSource.AUTO, {}, t0)
        audit.log(ExecutionAuditEventType.ORDER_SUBMITTED, "o1", "S", AuditSource.AUTO, {}, t1)
        audit.log(ExecutionAuditEventType.ORDER_FILLED, "o1", "S", AuditSource.AUTO, {}, t2)
        audit.log(ExecutionAuditEventType.ORDER_CANCELLED, "o2", "S", AuditSource.AUTO, {}, t3)

        # [t1, t3] 闭区间 → 3 条 (t1, t2, t3)
        results = audit.query(start=t1, end=t3)
        assert len(results) == 3

        # [t1, t2] 闭区间 → 2 条 (t1, t2)
        results = audit.query(start=t1, end=t2)
        assert len(results) == 2

    def test_query_combined_filters(self, audit: ExecutionAuditLogger):
        audit.log_order_created("ord-001", "600000.SH", {})
        audit.log_order_created("ord-002", "600000.SH", {})
        audit.log_order_submitted("ord-001", "600000.SH", {})

        results = audit.query(order_id="ord-001", event_type=ExecutionAuditEventType.ORDER_CREATED)
        assert len(results) == 1
        assert results[0].order_id == "ord-001"
        assert results[0].event_type == ExecutionAuditEventType.ORDER_CREATED

    def test_query_no_match(self, audit: ExecutionAuditLogger):
        audit.log_order_created("ord-001", "600000.SH", {})
        results = audit.query(order_id="nonexistent")
        assert results == []

    def test_query_all_when_no_filters(self, audit: ExecutionAuditLogger):
        audit.log_order_created("ord-001", "600000.SH", {})
        audit.log_order_submitted("ord-001", "600000.SH", {})
        results = audit.query()
        assert len(results) == 2


# ──────────────────────────────────────────────────────────────────────────────
# 报告
# ──────────────────────────────────────────────────────────────────────────────


class TestReport:
    """报告统计: by_event_type / by_symbol / by_source。"""

    def test_report_counts(self, audit: ExecutionAuditLogger):
        audit.log_order_created("ord-001", "600000.SH", {}, AuditSource.AUTO)
        audit.log_order_submitted("ord-001", "600000.SH", {}, AuditSource.AUTO)
        audit.log_order_filled("ord-001", "600000.SH", {}, AuditSource.SIMULATION)
        audit.log_order_created("ord-002", "000001.SZ", {}, AuditSource.LIVE)

        t0 = datetime(2026, 1, 1, tzinfo=UTC)
        t1 = datetime(2026, 12, 31, tzinfo=UTC)
        report = audit.generate_report(t0, t1)

        assert report.total_records == 4
        assert report.by_event_type == {
            "ORDER_CREATED": 2,
            "ORDER_SUBMITTED": 1,
            "ORDER_FILLED": 1,
        }
        assert report.by_symbol == {"600000.SH": 3, "000001.SZ": 1}
        assert report.by_source == {"AUTO": 2, "SIMULATION": 1, "LIVE": 1}
        assert report.chain_valid is True
        assert report.chain_break_at is None

    def test_report_chain_invalid(self, audit: ExecutionAuditLogger):
        rec = audit.log_order_created("ord-001", "600000.SH", {})
        assert rec is not None
        # 篡改
        audit._records[0] = ExecutionAuditRecord(
            record_id=rec.record_id,
            timestamp=rec.timestamp,
            event_type=rec.event_type,
            order_id=rec.order_id,
            symbol=rec.symbol,
            source=rec.source,
            detail={"tampered": True},
            prev_hash=rec.prev_hash,
            record_hash=rec.record_hash,
        )

        t0 = datetime(2026, 1, 1, tzinfo=UTC)
        t1 = datetime(2026, 12, 31, tzinfo=UTC)
        report = audit.generate_report(t0, t1)

        assert report.chain_valid is False
        assert report.chain_break_at == rec.record_id

    def test_report_empty_period(self, audit: ExecutionAuditLogger):
        audit.log_order_created("ord-001", "600000.SH", {})

        # 查询一个不包含任何记录的时间段
        t0 = datetime(2025, 1, 1, tzinfo=UTC)
        t1 = datetime(2025, 12, 31, tzinfo=UTC)
        report = audit.generate_report(t0, t1)

        assert report.total_records == 0
        assert report.by_event_type == {}


# ──────────────────────────────────────────────────────────────────────────────
# frozen 不可变
# ──────────────────────────────────────────────────────────────────────────────


class TestFrozenImmutable:
    """frozen dataclass 不可变: setattr 抛 FrozenInstanceError。"""

    def test_record_is_frozen(self, audit: ExecutionAuditLogger):
        rec = audit.log_order_created("ord-001", "600000.SH", {})
        assert rec is not None
        with pytest.raises(AttributeError):
            rec.order_id = "tampered"  # type: ignore[misc]

    def test_record_detail_dict_is_mutable_but_not_recommended(self, audit: ExecutionAuditLogger):
        """frozen dataclass 的 dict 字段本身可变 (浅冻结), 但不应修改。

        这是 Python frozen dataclass 的已知行为: frozen 阻止属性重新赋值,
        但不深冻结容器。hash 计算时用 detail 的快照, 修改 detail 会导致
        verify_chain 检测到篡改 (重算 hash 不匹配)。
        """
        rec = audit.log_order_created("ord-001", "600000.SH", {"qty": 100})
        assert rec is not None
        # 修改 detail 内部 (不推荐, 但 Python 允许)
        rec.detail["qty"] = 999
        # verify_chain 会检测到篡改 (重算 hash 不匹配)
        ok, break_at = audit.verify_chain()
        assert ok is False

    def test_report_is_frozen(self, audit: ExecutionAuditLogger):
        t0 = datetime(2026, 1, 1, tzinfo=UTC)
        t1 = datetime(2026, 12, 31, tzinfo=UTC)
        report = audit.generate_report(t0, t1)
        with pytest.raises(AttributeError):
            report.total_records = 999  # type: ignore[misc]


# ──────────────────────────────────────────────────────────────────────────────
# 持久化
# ──────────────────────────────────────────────────────────────────────────────


class TestPersistence:
    """flush → load round-trip: 链完整, hash 一致。"""

    def test_flush_load_roundtrip(self, tmp_path: Path):
        persist_path = tmp_path / "audit"
        audit = ExecutionAuditLogger(persist_path=persist_path)

        audit.log_order_created("ord-001", "600000.SH", {"qty": Decimal("100"), "price": "10.50"})
        audit.log_order_submitted("ord-001", "600000.SH", {})
        audit.log_order_filled("ord-001", "600000.SH", {"fill_price": "10.52"})

        original_count = audit.record_count
        original_hashes = [r.record_hash for r in audit._records]

        audit.flush()

        # 新实例加载
        audit2 = ExecutionAuditLogger(persist_path=persist_path)
        audit2.load()

        assert audit2.record_count == original_count
        loaded_hashes = [r.record_hash for r in audit2._records]
        assert loaded_hashes == original_hashes

        # 链完整性
        ok, break_at = audit2.verify_chain()
        assert ok is True
        assert break_at is None

    def test_flush_creates_jsonl_file(self, tmp_path: Path):
        persist_path = tmp_path / "audit"
        audit = ExecutionAuditLogger(persist_path=persist_path)
        audit.log_order_created("ord-001", "600000.SH", {})

        audit.flush()

        jsonl_path = persist_path.with_suffix(".jsonl")
        assert jsonl_path.exists()
        content = jsonl_path.read_text(encoding="utf-8").strip()
        data = json.loads(content)
        assert data["order_id"] == "ord-001"
        assert data["event_type"] == "ORDER_CREATED"

    def test_load_nonexistent_file(self, tmp_path: Path):
        """load 不存在的文件: 不抛异常, 记录数为 0。"""
        persist_path = tmp_path / "nonexistent"
        audit = ExecutionAuditLogger(persist_path=persist_path)
        audit.load()  # 不应抛异常
        assert audit.record_count == 0

    def test_flush_without_persist_path(self, audit: ExecutionAuditLogger):
        """无 persist_path 时 flush: 无操作, 不抛异常。"""
        audit.log_order_created("ord-001", "600000.SH", {})
        audit.flush()  # 不应抛异常

    def test_load_without_persist_path(self, audit: ExecutionAuditLogger):
        """无 persist_path 时 load: 无操作, 不抛异常。"""
        audit.load()  # 不应抛异常


# ──────────────────────────────────────────────────────────────────────────────
# 异常隔离
# ──────────────────────────────────────────────────────────────────────────────


class TestExceptionIsolation:
    """log() 内部异常不阻断执行主流程 (catch + log)。"""

    def test_log_with_unserializable_detail_returns_none(self, audit: ExecutionAuditLogger):
        """detail 含循环引用时, log() 返回 None, 不抛异常。

        _compute_record_hash 用 json.dumps(default=str) 序列化 detail,
        但循环引用在编码器层面抛 ValueError, default=str 无法兜底。
        """
        circular: list[Any] = []
        circular.append(circular)  # 循环引用: json.dumps 抛 ValueError

        rec = audit.log(
            ExecutionAuditEventType.ORDER_CREATED,
            "ord-001",
            "600000.SH",
            AuditSource.AUTO,
            {"bad": circular},
        )
        # log() 内部 catch 异常, 返回 None, 不抛出
        assert rec is None
        # 记录未入链
        assert audit.record_count == 0

    def test_convenience_method_exception_isolation(self, audit: ExecutionAuditLogger):
        """便捷方法内部异常不抛出。"""
        circular: list[Any] = []
        circular.append(circular)

        rec = audit.log_order_created("ord-001", "600000.SH", {"bad": circular})
        assert rec is None
        assert audit.record_count == 0

    def test_log_after_failure_still_works(self, audit: ExecutionAuditLogger):
        """异常后, 后续正常 log 仍能工作。"""
        circular: list[Any] = []
        circular.append(circular)

        # 第一次失败
        audit.log_order_created("ord-001", "600000.SH", {"bad": circular})
        assert audit.record_count == 0

        # 第二次正常
        rec = audit.log_order_created("ord-002", "600000.SH", {"qty": 100})
        assert rec is not None
        assert audit.record_count == 1
        assert rec.prev_hash == ZERO_HASH  # 链从 ZERO_HASH 开始


# ──────────────────────────────────────────────────────────────────────────────
# 枚举与错误类型
# ──────────────────────────────────────────────────────────────────────────────


class TestEnumsAndErrors:
    """枚举值和错误类型验证。"""

    def test_event_type_values(self):
        assert ExecutionAuditEventType.ORDER_CREATED.value == "ORDER_CREATED"
        assert ExecutionAuditEventType.IDEMPOTENCY_BLOCKED.value == "IDEMPOTENCY_BLOCKED"

    def test_source_values(self):
        assert AuditSource.AUTO.value == "AUTO"
        assert AuditSource.SIMULATION.value == "SIMULATION"
        assert AuditSource.LIVE.value == "LIVE"
        assert AuditSource.MANUAL.value == "MANUAL"

    def test_audit_chain_error_code(self):
        assert AuditChainError.error_code == "ZA-EX-0015"

    def test_audit_chain_error_is_zephyr_base_error(self):
        from zephyr.shared.foundation.errors import ZephyrBaseError

        assert issubclass(AuditChainError, ZephyrBaseError)

    def test_event_type_count(self):
        """确认 8 类事件。"""
        assert len(list(ExecutionAuditEventType)) == 8
