# [A_test] module_id: MOD-GOV_SCHED_CONSISTENCY_RECONCILER | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_SCHED_CONSISTENCY_RECONCILER | docs/03_modules/_domain_governance/blueprint.md | §schedule-consistency-reconciler
# [MODULE] tests.governance.audit.test_schedule_consistency_reconciler
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/governance/audit/test_schedule_consistency_reconciler.py
# [TTL] task_bound
"""三表一致性核对测试：X 检查红/绿 + reconciler spec 触发面 + 外部注册钩子（tmp_path 隔离，禁写生产 data/）。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))

from zephyr.governance.audit.reconciliation_registry import ReconciliationRegistry  # noqa: E402
from zephyr.governance.audit.schedule_consistency_reconciler import (  # noqa: E402
    GATE_ID,
    check_tables,
    load_three_tables,
    run_schedule_consistency,
    write_report,
)

SLOT_A = {"pre_market": {"cron": "34 8 * * 0-4", "executor": "default", "description": "盘前"}}
ENT_A = {
    "task_id": "data_slot_pre_market",
    "pool": "default",
    "peak_mem_gb": 1.0,
    "est_duration_min": 15,
    "exclusive_group": [],
    "window_type": "cron",
    "window_expr": "34 8 * * 1-5",
    "schedule_truth_source": "src/zephyr/data/config/schedule.yaml",
    "status": "active",
    "trading_sensitive": False,
}
TASK_A = {
    "task_id": "stock_basic_premarket",
    "table": "c1_market.stock_basic",
    "source": "akshare",
    "schedule": "pre_market",
    "dependencies": [],
}


def _mk_tables(tmp_path: Path, *, schedules=SLOT_A, entities=None, tasks=None) -> Path:
    """在 tmp_path 摆一套迷你三表（生产路径零接触）。"""
    (tmp_path / "src/zephyr/data/config").mkdir(parents=True, exist_ok=True)
    (tmp_path / "config").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src/zephyr/data/config/schedule.yaml").write_text(
        yaml.safe_dump({"schedules": schedules}, allow_unicode=True), encoding="utf-8"
    )
    (tmp_path / "src/zephyr/data/config/tasks.yaml").write_text(
        yaml.safe_dump({"tasks": tasks if tasks is not None else [TASK_A]}, allow_unicode=True),
        encoding="utf-8",
    )
    (tmp_path / "config/resource_profile_registry.yaml").write_text(
        yaml.safe_dump(
            {
                "total_entities": len(entities if entities is not None else [ENT_A]),
                "pool_vocabulary": {
                    "lanes": ["default", "heavy", "realtime"],
                    "workers": {"default": 8, "heavy": 2, "realtime": 4},
                },
                "entities": entities if entities is not None else [ENT_A],
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return tmp_path


def _x(rep: dict, code: str) -> int:
    return sum(1 for f in rep["findings"] if f["reason_code"] == code)


def test_clean_tables_green(tmp_path):
    root = _mk_tables(tmp_path)
    rep = run_schedule_consistency(root, gate_checks=False)
    assert rep["summary"]["ok"] is True
    assert rep["tables"] == {"slots": 1, "tasks": 1, "entities": 1, "parked_tasks": 0, "errors": {}}


def test_injected_fake_references_red(tmp_path):
    root = _mk_tables(tmp_path)
    tables = load_three_tables(root)
    tables["tasks"].append({"task_id": "fake_task", "schedule": "no_such_slot", "dependencies": []})
    tables["tasks"][0] = {**tables["tasks"][0], "dependencies": ["ghost_dep"]}
    tables["registry"]["entities"].append(
        {"task_id": "data_slot_no_such_slot", "pool": "ghost_pool", "status": "active"}
    )
    rep = check_tables(tables, str(root), gate_checks=False)
    assert _x(rep, "sched_x_unknown_slot") == 1
    assert _x(rep, "sched_x_missing_dep") == 1
    assert _x(rep, "sched_x_profile_without_slot") == 1
    assert _x(rep, "sched_x_ghost_pool") == 1
    assert rep["summary"]["ok"] is False


def test_parked_slot_is_info_not_warn(tmp_path):
    root = _mk_tables(
        tmp_path,
        tasks=[TASK_A, {"task_id": "retired_thing", "schedule": "disabled", "dependencies": []}],
    )
    rep = run_schedule_consistency(root, gate_checks=False)
    assert _x(rep, "sched_x_unknown_slot") == 0
    assert _x(rep, "sched_x_parked_task") == 1
    assert rep["findings"][-1]["severity"] == "info" or any(
        f["reason_code"] == "sched_x_parked_task" and f["severity"] == "info" for f in rep["findings"]
    )
    assert rep["summary"]["warn"] == 0  # info 不算 warn


def test_missing_truth_source_pointer(tmp_path):
    root = _mk_tables(tmp_path)
    (tmp_path / "src/zephyr/data/config/schedule.yaml").unlink()
    rep = run_schedule_consistency(root, gate_checks=False)
    assert _x(rep, "sched_x_missing_truth_source") == 1  # 指针失效
    assert _x(rep, "sched_x_table_error") == 1  # 槽位表缺失降级 finding，不抛


def test_reconciler_spec_trigger_and_reconcile(tmp_path):
    root = _mk_tables(tmp_path)
    from zephyr.governance.audit.schedule_consistency_reconciler import (
        make_schedule_consistency_reconciler,
    )

    spec = make_schedule_consistency_reconciler(type("GW", (), {"project_root": str(root)})())
    assert spec.gate_id == GATE_ID
    assert spec.trigger([str(root / "src/zephyr/data/config/tasks.yaml")]) is True
    assert spec.trigger([str(root / "README.md")]) is False
    assert "delete" not in spec.file_ops and "move" not in spec.file_ops  # 只读+报告写面

    # 注入红态 → reconcile → warn + 报告落 tmp_path/.runtime（fix-in-place 唯一写面）
    bad = _mk_tables(
        root,
        tasks=[TASK_A, {"task_id": "fake_task", "schedule": "no_such_slot", "dependencies": []}],
    )
    tables = load_three_tables(bad)
    rep = check_tables(tables, str(bad), gate_checks=False)
    assert rep["summary"]["warn"] >= 1
    result = spec.reconcile([str(bad / "src/zephyr/data/config/tasks.yaml")], "test-sid")
    assert result.action == "warn"
    assert result.gate_id == GATE_ID
    report_file = bad / ".runtime/schedule_consistency/last_result.json"
    assert report_file.exists()
    saved = json.loads(report_file.read_text(encoding="utf-8"))
    assert saved["summary"]["warn"] >= 1
    assert saved["trigger"]["session_id"] == "test-sid"


def test_registry_discovery_hook_registers_gate():
    reg = ReconciliationRegistry()
    assert GATE_ID not in reg.list_gate_ids()  # 构造期保持空（新 registry 为空不变量）
    reg.merge_external_specs()  # 外部规格发现钩子（gateway 禁碰时的运行时注册路径）
    ids = reg.list_gate_ids()
    assert GATE_ID in ids
    spec = [s for s in reg.specs if s.gate_id == GATE_ID][0]
    assert spec.priority == 826
    assert spec.file_ops >= frozenset({"read"})
