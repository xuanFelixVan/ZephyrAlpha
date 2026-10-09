# [BLUEPRINT] MOD-DATSEC-004 | docs/03_modules/_domain_data_security/data_access_auditor/blueprint.md | wiring 抢救配套测试（车道 2a st-chiefc-20261009）
# [MODULE] tests.data_security.test_wiring_audit_sink
# [DEPENDENCIES] zephyr.data_security.wiring.audit_sink；pytest
# [INVARIANTS] 输出全走 tmp_path fixture，禁写 data/ 生产路径
# [TTL] permanent
"""JsonlAuditSink（MOD-DATSEC-004）最小可红行为测试：构造契约/追加语义/fail-open/序列化。"""

from __future__ import annotations

import dataclasses
import datetime
import json
from pathlib import Path

import pytest

from zephyr.data_security.wiring import DEFAULT_SINK_RELPATH, JsonlAuditSink
from zephyr.data_security.wiring.audit_sink import _jsonify


def test_default_sink_relpath_matches_rulebook_declaration() -> None:
    """出厂落盘路径与规则册 audit.jsonl_sink 声明一致（F128 缺口②锚点）。"""
    assert DEFAULT_SINK_RELPATH == "data/audit/data_security_wiring/audit.jsonl"


def test_empty_path_fails_closed() -> None:
    """构造期空路径 ValueError（ERROR_CONTRACT：Fail-Closed）。"""
    with pytest.raises(ValueError):
        JsonlAuditSink("")


def test_append_writes_one_jsonl_event_per_call(tmp_path: Path) -> None:
    target = tmp_path / "audit.jsonl"
    fixed = datetime.datetime(2026, 10, 9, 8, 30, 0)
    sink = JsonlAuditSink(target, clock=lambda: fixed)

    sink({"event_id": "e-1", "subject": "unit"})
    sink({"event_id": "e-2"})

    lines = target.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["event_id"] == "e-1"
    assert first["_written_at"] == fixed.isoformat()


def test_fail_open_on_unwritable_target(tmp_path: Path) -> None:
    """目标为目录→OSError→fail-open 只吞不抛（审计失败不阻断主流程）。"""
    sink = JsonlAuditSink(tmp_path)
    sink({"event_id": "e-dir"})  # 不抛即通过


def test_jsonify_flattens_dataclass_datetime_path() -> None:
    @dataclasses.dataclass
    class Rec:
        at: datetime.datetime
        path: Path

    out = _jsonify(Rec(at=datetime.datetime(2026, 1, 2, 3, 4, 5), path=Path("x") / "y"))
    assert out == {"at": "2026-01-02T03:04:05", "path": str(Path("x") / "y")}


def test_package_reexports_present() -> None:
    """包级 __init__ 再出口四类关键入口存在性（接线复活面完整性）。"""
    import zephyr.data_security.wiring as pkg

    for name in ("JsonlAuditSink", "DataExitGuard", "LSGMaskingFront", "load_rulebook"):
        assert hasattr(pkg, name), name
