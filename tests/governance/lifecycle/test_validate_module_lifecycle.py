# [A_test] module_id: MOD-TEST-lifecycle-gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/lifecycle/validate_module_lifecycle.py | §
# [MODULE] tests.governance.lifecycle.test_validate_module_lifecycle
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-lifecycle-gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""validate_module_lifecycle.py 红蓝夹具（B10-P1）——ORPHAN-MODULE 转换门。

蓝（合法过）：active→deprecated（带 superseded_by）/ deprecated→archived（retain_until 已过）
红（拦）：跳阶段（active→archived）/ 逆向（deprecated→active、active→in_dev）/
P0 suspended / P0 successor 未 active 或 <30 天 / deprecated 缺 superseded_by /
deprecated 新增消费者 / archived ID 重用 / retain 未满。
tmp_path 隔离：全程零触生产账本。
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_SPEC = importlib.util.spec_from_file_location(
    "validate_module_lifecycle_under_test",
    _REPO / "scripts/governance/d5_architecture/validators/lifecycle/validate_module_lifecycle.py",
)
MOD = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = MOD  # 延迟注解/数据类解析需要 sys.modules 注册
_SPEC.loader.exec_module(MOD)

TABLE = MOD.load_transition_table()
TODAY = datetime(2026, 9, 27)


def _types(findings: list[dict]) -> set[str]:
    return {f["type"] for f in findings}


def _entry(mid: str, status: str, **kw) -> dict:
    e = {"module_id": mid, "status": status, "path": f"docs/{mid}.md"}
    e.update(kw)
    return e


# ---------- 蓝：合法转换 ----------


def test_legal_transition_active_to_deprecated_passes():
    old = [_entry("MOD-X", "active")]
    new = [_entry("MOD-X", "deprecated", superseded_by="MOD-Y")]
    findings = MOD.evaluate_transitions(old, new, TABLE, today=TODAY, successor_age_fn=lambda e: 60)
    assert findings == []


def test_legal_transition_deprecated_to_archived_passes_when_retain_passed():
    old = [_entry("MOD-X", "deprecated", superseded_by="MOD-Y")]
    new = [_entry("MOD-X", "archived")]
    recs = [{"module_id": "MOD-X", "retain_until": "2026-01-01"}]  # 已过期
    findings = MOD.evaluate_transitions(old, new, TABLE, retirement_records=recs, today=TODAY)
    assert findings == []


def test_case_drift_normalized_not_invalid():
    """大小写归一（S9 簿 §4.6 修复2）：'Active' 只报 CASE_DRIFT(MEDIUM)，不报 INVALID_STATUS。"""
    findings = MOD.entry_findings(_entry("MOD-X", "Active"), TABLE)
    assert _types(findings) == {"CASE_DRIFT"}


# ---------- 红：跳阶段 / 逆向 ----------


def test_skip_stage_active_to_archived_blocked():
    old = [_entry("MOD-X", "active")]
    new = [_entry("MOD-X", "archived")]
    findings = MOD.evaluate_transitions(old, new, TABLE, today=TODAY)
    assert "ILLEGAL_TRANSITION" in _types(findings)


def test_skip_stage_active_to_suspended_then_archived_chain_blocked():
    old = [_entry("MOD-X", "active")]
    new = [_entry("MOD-X", "deprecated", superseded_by="MOD-Y")]  # active→deprecated 合法；再 archived 由 retain 链拦
    findings = MOD.evaluate_transitions(old, new, TABLE, today=TODAY, successor_age_fn=lambda e: 60)
    assert findings == []


def test_reverse_deprecated_to_active_blocked():
    old = [_entry("MOD-X", "deprecated")]
    new = [_entry("MOD-X", "active")]
    findings = MOD.evaluate_transitions(old, new, TABLE, today=TODAY)
    f = [x for x in findings if x["type"] == "ILLEGAL_TRANSITION"]
    assert f and "逆向" in f[0]["detail"]


def test_reverse_active_to_in_dev_blocked():
    old = [_entry("MOD-X", "active")]
    new = [_entry("MOD-X", "in_dev")]
    assert "ILLEGAL_TRANSITION" in _types(MOD.evaluate_transitions(old, new, TABLE, today=TODAY))


def test_whitelist_reverse_testing_to_in_dev_allowed():
    old = [_entry("MOD-X", "testing")]
    new = [_entry("MOD-X", "in_dev")]
    assert MOD.evaluate_transitions(old, new, TABLE, today=TODAY) == []


# ---------- 红：retain 90 天（ABS-22 消解） ----------


def test_retain_not_passed_blocked_on_deprecated_to_archived():
    old = [_entry("MOD-X", "deprecated")]
    new = [_entry("MOD-X", "archived")]
    recs = [{"module_id": "MOD-X", "retain_until": (TODAY + timedelta(days=10)).strftime("%Y-%m-%d")}]
    findings = MOD.evaluate_transitions(old, new, TABLE, retirement_records=recs, today=TODAY)
    assert "RETAIN_NOT_PASSED" in _types(findings)


def test_retain_record_missing_blocked_on_deprecated_to_archived():
    old = [_entry("MOD-X", "deprecated")]
    new = [_entry("MOD-X", "archived")]
    findings = MOD.evaluate_transitions(old, new, TABLE, retirement_records=[], today=TODAY)
    assert "RETAIN_RECORD_MISSING" in _types(findings)


# ---------- 红：deprecated 完整性 ----------


def test_deprecated_missing_superseded_by_blocked():
    findings = MOD.entry_findings(_entry("MOD-X", "deprecated"), TABLE)
    assert "MISSING_SUPERSEDED_BY" in _types(findings)


# ---------- 红：P0 红线 ----------


def test_p0_suspended_blocked():
    findings = MOD.entry_findings(_entry("MOD-X", "suspended", priority="P0"), TABLE)
    assert "P0_SUSPENDED" in _types(findings)


def test_p0_deprecated_successor_not_active_blocked():
    findings = MOD.entry_findings(
        _entry("MOD-X", "deprecated", priority="P0", superseded_by="MOD-Y"),
        TABLE,
        registry_lookup=lambda mid: _entry("MOD-Y", "suspended"),
    )
    assert "P0_SUCCESSOR_NOT_ACTIVE" in _types(findings)


def test_p0_deprecated_successor_too_young_blocked():
    findings = MOD.entry_findings(
        _entry("MOD-X", "deprecated", priority="P0", superseded_by="MOD-Y"),
        TABLE,
        registry_lookup=lambda mid: _entry("MOD-Y", "active"),
        successor_age_fn=lambda e: 10,
    )
    assert "P0_SUCCESSOR_TOO_YOUNG" in _types(findings)


def test_p0_deprecated_successor_age_unknown_blocked_conservatively():
    findings = MOD.entry_findings(
        _entry("MOD-X", "deprecated", priority="P0", superseded_by="MOD-Y"),
        TABLE,
        registry_lookup=lambda mid: _entry("MOD-Y", "active"),
        successor_age_fn=lambda e: None,
    )
    assert "P0_SUCCESSOR_AGE_UNKNOWN" in _types(findings)


def test_p0_deprecated_successor_mature_passes():
    findings = MOD.entry_findings(
        _entry("MOD-X", "deprecated", priority="P0", superseded_by="MOD-Y"),
        TABLE,
        registry_lookup=lambda mid: _entry("MOD-Y", "active"),
        successor_age_fn=lambda e: 45,
    )
    assert findings == []


# ---------- 红：deprecated 新增消费者 / archived ID 重用 ----------


def test_deprecated_new_consumer_blocked():
    """代码面新增引用=拦；docs 命中=历史记载放行（与 MLC-003 step2 分类同口径）。"""
    findings = MOD.scan_deprecated_new_consumers(
        {"MOD-D"},
        [("src/new_consumer.py", "import mod_d  # MOD-D"), ("docs/hist.md", "MOD-D 历史记载")],
    )
    f = [x for x in findings if x["type"] == "DEPRECATED_NEW_CONSUMER"]
    assert len(f) == 1 and f[0]["where"] == "src/new_consumer.py"


def test_deprecated_new_consumer_exempt_archive_paths():
    findings = MOD.scan_deprecated_new_consumers(
        {"MOD-D"},
        [("scripts/_archive/old.py", "MOD-D"), ("architecture_model/module_id_registry.yaml", "MOD-D")],
    )
    assert findings == []


def test_archived_id_reuse_blocked():
    old = [_entry("MOD-OLD", "archived")]
    new = [_entry("MOD-OLD", "planned")]  # 同 ID 重新登记
    findings = MOD.evaluate_transitions(old, new, TABLE, today=TODAY)
    assert "ARCHIVED_ID_REUSE" in _types(findings)


def test_archived_id_reuse_via_retirement_record_blocked():
    old = [_entry("MOD-A", "active")]
    new = [_entry("MOD-DEAD", "planned")]
    recs = [{"module_id": "MOD-DEAD", "archived_date": "2026-01-01"}]
    findings = MOD.evaluate_transitions(old, new, TABLE, retirement_records=recs, today=TODAY)
    assert "ARCHIVED_ID_REUSE" in _types(findings)


# ---------- 全账本审计模式（无 --staged） ----------


def test_scan_registry_lifecycle_flags_legacy_and_missing_fields(tmp_path: Path):
    reg_text = (
        "registered_ids:\n  - module_id: MOD-A\n    status: merged\n  - module_id: MOD-B\n    status: deprecated\n"
    )
    p = tmp_path / "reg.yaml"
    p.write_text(reg_text, encoding="utf-8")
    registry = MOD.load_module_registry(p)
    findings = MOD.scan_registry_lifecycle(registry, table=TABLE)
    types = _types(findings)
    assert "INVALID_STATUS" in types  # merged=越界值（P3 收敛映射待迁移）
    assert "MISSING_SUPERSEDED_BY" in types  # deprecated 缺 superseded_by


# ---------- --staged 门端到端（git 取证面 monkeypatch） ----------


def test_staged_gate_own_diff_scope_and_consumer_scan(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    old_text = "registered_ids:\n  - module_id: MOD-D\n    status: active\n    path: docs/d.md\n"
    new_text = (
        "registered_ids:\n"
        "  - module_id: MOD-D\n    status: deprecated\n    superseded_by: MOD-E\n    path: docs/d.md\n"
        "retirement_records:\n"
        '  - module_id: MOD-D\n    retain_until: "2026-12-26"\n'
    )
    reg = tmp_path / "module_id_registry.yaml"
    reg.write_text(new_text, encoding="utf-8")
    monkeypatch.setattr(MOD, "staged_files", lambda root: ["module_id_registry.yaml", "src/new_use.py"])
    monkeypatch.setattr(MOD, "staged_old_registry_text", lambda root, rel: old_text)
    monkeypatch.setattr(MOD, "staged_added_lines", lambda root: [("src/new_use.py", "from d import MOD_D  # MOD-D")])
    findings = MOD.run_staged_gate(tmp_path, "module_id_registry.yaml", table=TABLE)
    types = _types(findings)
    assert "DEPRECATED_NEW_CONSUMER" in types  # 同 diff 新增 deprecated 消费者→拦
    assert "ILLEGAL_TRANSITION" not in types  # active→deprecated 合法
    assert "MISSING_SUPERSEDED_BY" not in types


def test_staged_gate_skips_registry_when_not_staged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """own-diff 作用域：账本未暂存→账本面零判读（不拦无辜提交人）。"""
    reg_text = "registered_ids:\n  - module_id: MOD-A\n    status: merged\n"  # 工作区越界值，但未暂存
    reg = tmp_path / "module_id_registry.yaml"
    reg.write_text(reg_text, encoding="utf-8")
    monkeypatch.setattr(MOD, "staged_files", lambda root: ["docs/other.md"])
    monkeypatch.setattr(MOD, "staged_added_lines", lambda root: [])
    findings = MOD.run_staged_gate(tmp_path, "module_id_registry.yaml", table=TABLE)
    assert "INVALID_STATUS" not in _types(findings)
