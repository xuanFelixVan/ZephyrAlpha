"""MOD-CMP-010 compliance_log JSONL 落库 单元测试（43 号 §3.2）。"""

from __future__ import annotations

from datetime import date

from zephyr.compliance.compliance_log import ComplianceLogger, ComplianceLogRecord


def test_log_and_read_roundtrip(tmp_path):
    """写入→读取闭环：字段完整、append-only 逐行累积。"""
    log = ComplianceLogger(tmp_path / "c.jsonl")
    log.log("E1", "mod_a", {"k": 1})
    log.log("E2", "mod_b", {"k": 2})
    records = log.read_all()
    assert [r.event_type for r in records] == ["E1", "E2"]
    assert records[0].source == "mod_a"
    assert records[1].payload == {"k": 2}
    assert records[0].ts  # ISO 时间戳非空


def test_log_creates_parent_dirs(tmp_path):
    """父目录不存在时自动创建。"""
    log = ComplianceLogger(tmp_path / "a" / "b" / "c.jsonl")
    assert log.log("E", "m") is not None
    assert (tmp_path / "a" / "b" / "c.jsonl").exists()


def test_non_serializable_payload_fallback(tmp_path):
    """date 等不可 JSON 序列化对象走 default=str 兜底，不抛异常。"""
    log = ComplianceLogger(tmp_path / "c.jsonl")
    rec = log.log("E", "m", {"d": date(2026, 8, 15)})
    assert rec is not None
    assert log.read_all()[0].payload["d"] == "2026-08-15"


def test_io_failure_returns_none_not_raise(tmp_path):
    """落盘失败返回 None（Fail-Silent 不阻断交易链路）。"""
    log = ComplianceLogger(tmp_path)  # 目录路径，open 必失败
    assert log.log("E", "m") is None


def test_read_all_missing_file(tmp_path):
    """文件不存在返回空列表。"""
    assert ComplianceLogger(tmp_path / "none.jsonl").read_all() == []


def test_record_immutable(tmp_path):
    """记录不可变（证据链语义）。"""
    rec = ComplianceLogRecord(ts="t", event_type="E", source="m")
    try:
        rec.event_type = "X"  # type: ignore[misc]
        raise AssertionError("frozen dataclass 不应可写")
    except AttributeError:
        pass
