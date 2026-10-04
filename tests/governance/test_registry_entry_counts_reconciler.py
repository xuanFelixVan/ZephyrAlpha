# [TEST] tests/governance/test_registry_entry_counts_reconciler.py
# [TTL] task_bound
# C25 接线单测：registry_entry_counts_reconciler 触发匹配/回填解析/action 映射（tmp_path 隔离，禁写生产路径）
"""Tests for registry_entry_counts_reconciler (C25 --update-entry-counts wiring)."""

from __future__ import annotations

from types import SimpleNamespace

from zephyr.governance.audit.registry_entry_counts_reconciler import (
    _TOOL_REL,
    GATE_ID,
    ROOR_REL,
    make_external_reconciler_spec,
    make_registry_entry_counts_reconciler,
)


def _make_spec(tmp_path):
    return make_registry_entry_counts_reconciler(SimpleNamespace(project_root=str(tmp_path)))


def test_spec_shape_and_registration_hook():
    spec = _make_spec(None) if False else make_external_reconciler_spec(None)
    assert spec.gate_id == GATE_ID == "GATE-REGISTRY-ENTRY-COUNTS"
    assert spec.priority == 830
    # 删除/移动零声明——回填只行级手术写 ROOR
    assert "delete" not in spec.file_ops and "move" not in spec.file_ops
    assert "write" in spec.file_ops and "read" in spec.file_ops


def test_trigger_matches_roor_tool_and_module(tmp_path):
    spec = _make_spec(tmp_path)
    assert spec.trigger([ROOR_REL]) is True
    assert spec.trigger([_TOOL_REL]) is True
    assert spec.trigger(["src/zephyr/governance/audit/registry_entry_counts_reconciler.py"]) is True
    # Windows 反斜杠口径归一
    assert spec.trigger(["docs\\registry_of_registries.yaml"]) is True
    assert spec.trigger(["src/foo.py", "docs/other.yaml"]) is False


def test_reconcile_clean_when_no_backfill(tmp_path, monkeypatch):
    import zephyr.governance.audit.registry_entry_counts_reconciler as mod

    def fake_run(project_root):
        return {"ok": True, "fixed": [], "stale_left": 0, "stderr_tail": ""}

    monkeypatch.setattr(mod, "run_entry_counts_backfill", fake_run)
    spec = _make_spec(tmp_path)
    res = spec.reconcile([ROOR_REL], "sess-test")
    assert res.action == "clean"
    assert res.gate_id == GATE_ID


def test_reconcile_warn_on_tool_failure(tmp_path, monkeypatch):
    import zephyr.governance.audit.registry_entry_counts_reconciler as mod

    def fake_run(project_root):
        return {"ok": False, "fixed": [], "stale_left": 0, "stderr_tail": "boom"}

    monkeypatch.setattr(mod, "run_entry_counts_backfill", fake_run)
    spec = _make_spec(tmp_path)
    res = spec.reconcile([ROOR_REL], "sess-test")
    assert res.action == "warn"
    assert "boom" in res.detail or "non-zero" in res.detail


def test_reconcile_clean_when_backfill_idempotent_no_drift(tmp_path, monkeypatch):
    import zephyr.governance.audit.registry_entry_counts_reconciler as mod

    def fake_run(project_root):
        return {"ok": True, "fixed": ["REG-X entry_count: 1 -> 2"], "stale_left": 0, "stderr_tail": ""}

    monkeypatch.setattr(mod, "run_entry_counts_backfill", fake_run)
    # ROOR 无净漂移（git diff 空）→ clean
    monkeypatch.setattr(
        mod.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=0, stdout="", stderr=""),
    )
    spec = _make_spec(tmp_path)
    res = spec.reconcile([ROOR_REL], "sess-test")
    assert res.action == "clean"
    assert "无净漂移" in res.detail


def test_reconcile_warn_without_gateway_leaves_worktree(tmp_path, monkeypatch):
    import zephyr.governance.audit.registry_entry_counts_reconciler as mod

    def fake_run(project_root):
        return {"ok": True, "fixed": ["REG-X entry_count: 1 -> 2"], "stale_left": 0, "stderr_tail": ""}

    monkeypatch.setattr(mod, "run_entry_counts_backfill", fake_run)
    monkeypatch.setattr(
        mod.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=0, stdout=ROOR_REL + "\n", stderr=""),
    )
    spec = make_registry_entry_counts_reconciler(None)  # 无 gateway → 留工作区 warn
    res = spec.reconcile([ROOR_REL], "sess-test")
    assert res.action == "warn"
    assert "无 gateway" in res.detail


def test_reconcile_auto_committed_via_gateway(tmp_path, monkeypatch):
    import zephyr.governance.audit.registry_entry_counts_reconciler as mod

    def fake_run(project_root):
        return {"ok": True, "fixed": ["REG-A a: 1 -> 2", "REG-B b: 3 -> 4"], "stale_left": 0, "stderr_tail": ""}

    monkeypatch.setattr(mod, "run_entry_counts_backfill", fake_run)
    monkeypatch.setattr(
        mod.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=0, stdout=ROOR_REL + "\n", stderr=""),
    )
    committed: list[tuple[str, list[str], str]] = []

    class _Gateway:
        project_root = str(tmp_path)

        def _commit_auto(self, session_id, files, msg):
            committed.append((session_id, files, msg))
            return SimpleNamespace(status="OK")

    spec = make_registry_entry_counts_reconciler(_Gateway())
    res = spec.reconcile([ROOR_REL], "sess-c25")
    assert res.action == "auto_committed"
    assert len(committed) == 1
    sid, files, msg = committed[0]
    assert sid == "sess-c25"
    assert str(files[0]).replace("\\", "/").endswith(ROOR_REL)
    assert "CR-007" in msg


def test_reconcile_never_raises(tmp_path, monkeypatch):
    import zephyr.governance.audit.registry_entry_counts_reconciler as mod

    def boom(project_root):
        raise RuntimeError("tool exploded")

    monkeypatch.setattr(mod, "run_entry_counts_backfill", boom)
    spec = _make_spec(tmp_path)
    res = spec.reconcile([ROOR_REL], "sess-test")  # 不抛即过
    assert res.action == "warn"
