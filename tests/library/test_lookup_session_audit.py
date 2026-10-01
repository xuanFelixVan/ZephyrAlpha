# [BLUEPRINT] MOD-LIB-003 | docs/03_modules/_domain_library/blueprint.md | §
# [TTL] permanent
"""lookup CLI ``--session`` 审计留痕回归（裁定#460 ②，st-circ-a4-20260930）。

零真库：lookup_assets / write_lookup_audit_log 全部替换为假件，只锁四条契约——
①无 ``--session`` 时审计零调用（行为零变化）；②携带 ``--session`` 时主查询面
写 ``.runtime/lookup_audit/<sid>.jsonl``（tool="zephyr.library.lookup"，
result_count=结果行数）；③审计故障 fail-open 不改退出码；④空白 session 视同
未提供。
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from zephyr.library import lookup as lookup_mod


def _rows(count: int) -> list[dict[str, Any]]:
    return [{"asset_id": f"AST-{i}", "kind": "file", "status": "active", "home": f"docs/x{i}.md"} for i in range(count)]


@pytest.fixture(autouse=True)
def alias_axis_on(monkeypatch: pytest.MonkeyPatch) -> None:
    """钉住别名轴开态（main() 经 globals() 读写该模块全局，fixture 出口还原防跨件污染）。"""
    monkeypatch.setattr(lookup_mod, "_alias_expansion_enabled", True)


@pytest.fixture()
def audit_dir(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> Any:
    """审计目录改道 tmp_path（测试隔离：禁写生产路径）。"""
    import zephyr.governance.capability_lookup as cap_mod

    target = tmp_path / "lookup_audit"
    monkeypatch.setattr(cap_mod, "LOOKUP_AUDIT_DIR", target)
    return target


def _read_audit(audit_dir: Any, sid: str) -> list[dict[str, Any]]:
    path = audit_dir / f"{sid}.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_no_session_keeps_behavior_identical(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], audit_dir: Any
) -> None:
    """无 --session：退出码/输出不变，审计通道零调用（行为零变化契约）。"""
    calls: list[tuple] = []
    import zephyr.governance.capability_lookup as cap_mod

    monkeypatch.setattr(lookup_mod, "lookup_assets", lambda *a, **k: _rows(2))
    monkeypatch.setattr(cap_mod, "write_lookup_audit_log", lambda *a, **k: calls.append((a, k)))
    code = lookup_mod.main(["kline"])
    assert code == 0
    assert "AST-0" in capsys.readouterr().out
    assert calls == []
    assert list(audit_dir.glob("*.jsonl")) == []


def test_session_writes_audit_with_tool_and_count(monkeypatch: pytest.MonkeyPatch, audit_dir: Any) -> None:
    """--session：主查询面留痕 tool=zephyr.library.lookup，result_count=行数。"""
    monkeypatch.setattr(lookup_mod, "lookup_assets", lambda *a, **k: _rows(3))
    code = lookup_mod.main(["kline", "--session", "st-audit-x"])
    assert code == 0
    entries = _read_audit(audit_dir, "st-audit-x")
    assert len(entries) == 1
    entry = entries[0]
    assert entry["tool"] == "zephyr.library.lookup"
    assert entry["result_count"] == 3
    assert entry["query"] == {"query": "kline", "face": "main"}
    assert entry["rule_ids"] == []


def test_session_audit_failure_is_fail_open(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], audit_dir: Any
) -> None:
    """审计写失败（抛异常）：退出码与输出不受影响（fail-open 契约）。"""
    import zephyr.governance.capability_lookup as cap_mod

    def _boom(*a: object, **k: object) -> None:
        raise RuntimeError("audit backend down")

    monkeypatch.setattr(lookup_mod, "lookup_assets", lambda *a, **k: _rows(1))
    monkeypatch.setattr(cap_mod, "write_lookup_audit_log", _boom)
    code = lookup_mod.main(["kline", "--session", "st-audit-y"])
    assert code == 0
    assert "AST-0" in capsys.readouterr().out


def test_session_empty_string_treated_as_absent(monkeypatch: pytest.MonkeyPatch, audit_dir: Any) -> None:
    """空白 --session 视同未提供：不留痕（与 write_lookup_audit_log 侧守卫对齐）。"""
    import zephyr.governance.capability_lookup as cap_mod

    calls: list[tuple] = []
    monkeypatch.setattr(lookup_mod, "lookup_assets", lambda *a, **k: _rows(1))
    monkeypatch.setattr(cap_mod, "write_lookup_audit_log", lambda *a, **k: calls.append((a, k)))
    code = lookup_mod.main(["kline", "--session", "   "])
    assert code == 0
    assert calls == []


def test_session_no_result_writes_zero_count(monkeypatch: pytest.MonkeyPatch, audit_dir: Any) -> None:
    """无结果退出码 1 仍留痕 result_count=0（gate 端可识别"查过但零命中"）。"""
    monkeypatch.setattr(lookup_mod, "lookup_assets", lambda *a, **k: [])
    code = lookup_mod.main(["ghost-asset", "--session", "st-audit-z"])
    assert code == 1
    entries = _read_audit(audit_dir, "st-audit-z")
    assert len(entries) == 1
    assert entries[0]["result_count"] == 0


def test_session_backtest_face_records_face_marker(monkeypatch: pytest.MonkeyPatch, audit_dir: Any) -> None:
    """非主查询面（backtest）留痕携 face 标记，rc 语义不变。"""
    monkeypatch.setattr(lookup_mod, "_query_backtest", lambda *a, **k: 0)
    code = lookup_mod.main(["--backtest", "--strategy", "s1", "--session", "st-audit-b"])
    assert code == 0
    entries = _read_audit(audit_dir, "st-audit-b")
    assert len(entries) == 1
    assert entries[0]["query"] == {"query": "s1", "face": "backtest"}
    assert entries[0]["result_count"] == 1
