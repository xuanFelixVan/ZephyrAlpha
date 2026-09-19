# [A_test] module_id: MOD-OPS_SCHED_OVERVIEW | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-OPS_SCHED_OVERVIEW | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §schedule-overview
# [MODULE] tests.scripts.test_schedule_overview
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/scripts/test_schedule_overview.py
# [TTL] task_bound
"""统一 CLI 测试：周历三表投影/dow 归一/资源档位/selftest 红绿/exit 语义（tmp_path 隔离）。"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "sched_overview_test", REPO_ROOT / "scripts" / "ops" / "schedule_overview.py"
)
so = importlib.util.module_from_spec(_SPEC)
sys.modules.setdefault("sched_overview_test", so)
_SPEC.loader.exec_module(so)

TZ = timezone.utc
MON = datetime(2026, 9, 14, 12, 0, tzinfo=TZ)  # 周一（周窗 09-14 起）


def _mk_tables(tmp_path: Path):
    """迷你三表：2 槽位/2 任务/2 实体（窗口_expr 用 croniter 口径 1-5=周一~五）。"""
    (tmp_path / "src/zephyr/data/config").mkdir(parents=True, exist_ok=True)
    (tmp_path / "config").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src/zephyr/data/config/schedule.yaml").write_text(
        yaml.safe_dump(
            {
                "schedules": {
                    "pre_market": {"cron": "34 8 * * 0-4", "executor": "default", "description": "盘前"},
                    "lonely_slot": {"cron": "00 5 * * 1", "executor": "heavy", "description": "空槽"},
                }
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    (tmp_path / "src/zephyr/data/config/tasks.yaml").write_text(
        yaml.safe_dump(
            {
                "tasks": [
                    {"task_id": "t_premarket", "schedule": "pre_market", "dependencies": []},
                    {"task_id": "t_retired", "schedule": "disabled", "dependencies": []},
                ]
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    (tmp_path / "config/resource_profile_registry.yaml").write_text(
        yaml.safe_dump(
            {
                "total_entities": 2,
                "mem_ceiling_gb": 10.0,
                "pool_vocabulary": {"lanes": ["default", "heavy"], "workers": {"default": 8, "heavy": 2}},
                "entities": [
                    {
                        "task_id": "data_slot_pre_market",
                        "pool": "default",
                        "resource_class": "light",
                        "peak_mem_gb": 1.0,
                        "est_duration_min": 15,
                        "exclusive_group": [],
                        "window_type": "cron",
                        "window_expr": "34 8 * * 1-5",
                        "schedule_truth_source": "src/zephyr/data/config/schedule.yaml",
                        "status": "active",
                        "trading_sensitive": False,
                    },
                    {
                        "task_id": "data_slot_lonely_slot",
                        "pool": "heavy",
                        "resource_class": "cpu_heavy",
                        "peak_mem_gb": 2.0,
                        "est_duration_min": 30,
                        "exclusive_group": ["g1"],
                        "window_type": "cron",
                        "window_expr": "00 5 * * 1",
                        "schedule_truth_source": "src/zephyr/data/config/schedule.yaml",
                        "status": "planned",
                        "trading_sensitive": False,
                    },
                ],
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return tmp_path


def _load(root: Path) -> dict:
    return so.load_three_tables(str(root))


def test_week_section_slot_task_profile_join(tmp_path):
    tables = _load(_mk_tables(tmp_path))
    week = so.build_week_section(tables, so._week_start_sh(MON))
    by_slot = {s["slot"]: s for s in week["slots"]}
    assert week["slot_count"] == 2
    assert by_slot["pre_market"]["task_count"] == 1
    assert by_slot["pre_market"]["tasks"] == ["t_premarket"]
    assert by_slot["pre_market"]["profile"]["resource_class"] == "light"
    assert by_slot["pre_market"]["workers"] == 8
    # APScheduler dow 0-4（周一~五）经注册表 window_expr 归一后=周一~五（防 0=周日 错显）
    dows = set(by_slot["pre_market"]["week_firings"].keys())
    assert dows == {0, 1, 2, 3, 4}
    assert by_slot["pre_market"]["week_firings"][0] == ["08:34"]
    assert by_slot["lonely_slot"]["task_count"] == 0  # 零任务槽位照常入视图


def test_resource_section_counts(tmp_path):
    tables = _load(_mk_tables(tmp_path))
    res = so.build_resource_section(tables["registry"])
    assert res["total_entities"] == 2
    assert res["by_pool"] == {"default": 1, "heavy": 1}
    assert res["workers"]["heavy"] == 2
    assert res["exclusive_groups"] == {"g1": ["data_slot_lonely_slot"]}
    assert res["measured_coverage"] == "0/2"


def test_consistency_and_exit_semantics(tmp_path):
    root = _mk_tables(tmp_path)
    tables = _load(root)
    rep = so.check_tables(tables, str(root), gate_checks=False)
    assert rep["summary"]["ok"] is True  # 迷你三表干净（disabled=停放 info）
    assert rep["tables"]["parked_tasks"] == 1
    # fail-on 语义：无 warn/block → exit 0
    payload = {"summary": rep["summary"], "findings": rep["findings"], "tables": rep["tables"]}
    bad = sum(1 for f in payload["findings"] if {"block": 0, "warn": 1}.get(f["severity"], 9) <= 0)
    assert bad == 0


def test_selftest_red_green_in_memory(tmp_path):
    ok, log = so.run_selftest(REPO_ROOT)  # 真仓三表（只读+内存注入，零落盘）
    assert ok is True
    assert any("注入→红" in x for x in log)
    assert any("还原→绿" in x for x in log)
    assert not (tmp_path / ".runtime").exists()  # 自检不落盘


def test_json_payload_sections(tmp_path):
    tables = _load(_mk_tables(tmp_path))
    week = so.build_week_section(tables, so._week_start_sh(MON))
    resource = so.build_resource_section(tables["registry"])
    payload = json.loads(json.dumps({"week": week, "resource": resource}, ensure_ascii=False))
    assert set(payload["week"]) >= {"week_start", "days", "slots", "slot_count", "task_total"}
    assert payload["resource"]["lanes"] == ["default", "heavy"]
