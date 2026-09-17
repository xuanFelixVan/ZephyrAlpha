# [BLUEPRINT] MOD-INF-072 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] tests.infra_ops.test_config_effect_checker
# [DOMAIN] D_INFRA_OPS
# [TTL] permanent
"""配置生效核对器测试（MOD-INF-092 / WORK-ORDER-3）。

铁律：测试隔离——全部读写走 tmp_path fixture，禁触生产 src/zephyr/data/config
与 data/failures（alert=False 或 failures_dir 注入）。
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest
import yaml

from zephyr.infra_ops.config_effect_checker import (
    SNAPSHOT_SCHEMA,
    build_loaded_state_snapshot,
    check_config_effect,
    write_loaded_state_snapshot,
)

# ── fixtures ──────────────────────────────────────────────────────────────────

SCHEDULE_YAML = """\
schedules:
  daily_kline:
    cron: "30 16 * * 0-4"
    executor: heavy
  pre_market:
    cron: "34 8 * * 0-4"
    executor: default
"""

TASKS_YAML = """\
tasks:
  - task_id: kline_daily_incremental
    source: akshare
    schedule: daily_kline
    table: c1_market.kline_daily
  - task_id: stock_list_refresh
    source: akshare
    schedule: pre_market
    table: c1_meta.stock_basic
"""


@pytest.fixture
def env(tmp_path: Path) -> dict:
    """tmp_path 隔离环境：配置目录 + 快照路径 + 失败告警目录。"""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "schedule.yaml").write_text(SCHEDULE_YAML, encoding="utf-8")
    (config_dir / "tasks.yaml").write_text(TASKS_YAML, encoding="utf-8")
    return {
        "config_dir": config_dir,
        "snapshot": tmp_path / "snapshots" / "scheduler_loaded_state.json",
        "failures_dir": tmp_path / "failures",
        "tmp_path": tmp_path,
    }


def _load_process_state(config_dir: Path) -> tuple[dict, list]:
    """模拟调度器 load_config()：解析两份 YAML 为进程内结构。"""
    sched = (yaml.safe_load((config_dir / "schedule.yaml").read_text(encoding="utf-8")) or {}).get(
        "schedules", {}
    )
    tasks = (yaml.safe_load((config_dir / "tasks.yaml").read_text(encoding="utf-8")) or {}).get(
        "tasks", []
    )
    return sched, tasks


def _export_snapshot(env: dict) -> None:
    """模拟调度器 export_loaded_state 钩子（与生产同一构建/写入函数）。"""
    schedules, tasks = _load_process_state(env["config_dir"])
    snapshot = build_loaded_state_snapshot(
        env["config_dir"], schedules, tasks, pid=12345
    )
    write_loaded_state_snapshot(snapshot, env["snapshot"])


# ── 场景 1：一致 → 绿 ─────────────────────────────────────────────────────────


def test_consistent_is_ok(env: dict) -> None:
    _export_snapshot(env)
    report = check_config_effect(
        config_dir=env["config_dir"],
        snapshot_path=env["snapshot"],
        alert=False,
    )
    assert report.status == "ok", report.summary
    assert report.mismatches == []
    assert "一致" in report.summary
    assert report.to_dict()["status"] == "ok"


def test_report_carries_gap_entries(env: dict) -> None:
    """GAP 名单（risk_params/trading_decision_map）必须出现在报告 gaps 里，不误判为红。"""
    _export_snapshot(env)
    report = check_config_effect(
        config_dir=env["config_dir"],
        snapshot_path=env["snapshot"],
        alert=False,
    )
    gap_files = {g.file for g in report.gaps}
    assert "config/risk_params.yaml" in gap_files
    assert "config/trading_decision_map.yaml" in gap_files
    assert report.status == "ok"


# ── 场景 2：改配置不重启 → 红且指到具体键 ────────────────────────────────────


def test_schedule_edit_reports_key_drift(env: dict) -> None:
    _export_snapshot(env)
    # 模拟改盘：daily_kline 16:30 -> 16:45（调度器不重启，进程仍用旧值）
    data = yaml.safe_load((env["config_dir"] / "schedule.yaml").read_text(encoding="utf-8"))
    data["schedules"]["daily_kline"]["cron"] = "45 16 * * 0-4"
    (env["config_dir"] / "schedule.yaml").write_text(
        yaml.safe_dump(data, allow_unicode=True), encoding="utf-8"
    )
    report = check_config_effect(
        config_dir=env["config_dir"], snapshot_path=env["snapshot"], alert=False
    )
    assert report.status == "mismatch"
    key_paths = {m.key_path for m in report.mismatches}
    assert "schedules.daily_kline.cron" in key_paths
    drift = next(m for m in report.mismatches if m.key_path == "schedules.daily_kline.cron")
    assert "45 16" in drift.disk_value and "30 16" in drift.process_value
    assert "重启" in drift.suggestion


def test_task_edit_reports_task_key_drift(env: dict) -> None:
    _export_snapshot(env)
    data = yaml.safe_load((env["config_dir"] / "tasks.yaml").read_text(encoding="utf-8"))
    data["tasks"][0]["schedule"] = "daily_capital"  # 任务改挂时段
    (env["config_dir"] / "tasks.yaml").write_text(
        yaml.safe_dump(data, allow_unicode=True), encoding="utf-8"
    )
    report = check_config_effect(
        config_dir=env["config_dir"], snapshot_path=env["snapshot"], alert=False
    )
    assert report.status == "mismatch"
    key_paths = {m.key_path for m in report.mismatches}
    assert "tasks.kline_daily_incremental.schedule" in key_paths


def test_task_added_and_removed(env: dict) -> None:
    _export_snapshot(env)
    data = yaml.safe_load((env["config_dir"] / "tasks.yaml").read_text(encoding="utf-8"))
    removed = data["tasks"].pop(0)
    data["tasks"].append({"task_id": "brand_new_task", "source": "akshare",
                          "schedule": "daily_kline"})
    (env["config_dir"] / "tasks.yaml").write_text(
        yaml.safe_dump(data, allow_unicode=True), encoding="utf-8"
    )
    report = check_config_effect(
        config_dir=env["config_dir"], snapshot_path=env["snapshot"], alert=False
    )
    key_kinds = {(m.key_path, m.kind) for m in report.mismatches}
    assert (f"tasks.{removed['task_id']}", "task_removed") in key_kinds
    assert ("tasks.brand_new_task", "task_added") in key_kinds
    # 噪音防护：tasks.yaml 的漂移不得把 schedule.yaml 段误判为增删（分段对比）
    assert all(m.file == "tasks.yaml" for m in report.mismatches), \
        "tasks.yaml 漂移不应在 schedule.yaml 标签下产生误报"


# ── 场景 3：快照缺失/损坏 → 不可判定（fail-closed，不误报绿） ─────────────────


def test_missing_snapshot_is_unknown_not_ok(env: dict) -> None:
    report = check_config_effect(
        config_dir=env["config_dir"],
        snapshot_path=env["snapshot"],  # 从未导出
        alert=False,
    )
    assert report.status == "unknown"
    assert report.status != "ok"
    assert "不可判定" in report.summary


def test_corrupt_snapshot_is_unknown(env: dict) -> None:
    env["snapshot"].parent.mkdir(parents=True, exist_ok=True)
    env["snapshot"].write_text("{not valid json!!", encoding="utf-8")
    report = check_config_effect(
        config_dir=env["config_dir"], snapshot_path=env["snapshot"], alert=False
    )
    assert report.status == "unknown"


def test_wrong_schema_snapshot_is_unknown(env: dict) -> None:
    env["snapshot"].parent.mkdir(parents=True, exist_ok=True)
    env["snapshot"].write_text(
        json.dumps({"schema": "something_else_v0", "files": {}}), encoding="utf-8"
    )
    report = check_config_effect(
        config_dir=env["config_dir"], snapshot_path=env["snapshot"], alert=False
    )
    assert report.status == "unknown"


# ── mtime-only：warning 不翻红（判定真源=内容 sha256） ────────────────────────


def test_mtime_only_touch_is_warning_not_red(env: dict) -> None:
    _export_snapshot(env)
    # 纯 touch（内容不变，mtime 前移 2 秒）
    future = time.time() + 2
    os.utime(env["config_dir"] / "schedule.yaml", (future, future))
    report = check_config_effect(
        config_dir=env["config_dir"], snapshot_path=env["snapshot"], alert=False
    )
    assert report.status == "ok", report.summary
    assert report.warnings, "mtime-only 漂移应产生 warning 提示"
    assert "mtime" in report.warnings[0]


# ── 告警接线：mismatch 走 Alerter 落 failures/*.json（注入目录隔离） ──────────


def test_mismatch_alerts_via_alerter_failure_file(env: dict) -> None:
    _export_snapshot(env)
    data = yaml.safe_load((env["config_dir"] / "schedule.yaml").read_text(encoding="utf-8"))
    data["schedules"]["pre_market"]["executor"] = "heavy"
    (env["config_dir"] / "schedule.yaml").write_text(
        yaml.safe_dump(data, allow_unicode=True), encoding="utf-8"
    )
    report = check_config_effect(
        config_dir=env["config_dir"],
        snapshot_path=env["snapshot"],
        alert=True,
        failures_dir=env["failures_dir"],
    )
    assert report.status == "mismatch"
    files = list(Path(env["failures_dir"]).glob("*config_effect_check*.json"))
    assert files, "ERROR 级告警应落 failures/*.json 失败文件"


def test_ok_does_not_alert(env: dict) -> None:
    _export_snapshot(env)
    check_config_effect(
        config_dir=env["config_dir"],
        snapshot_path=env["snapshot"],
        alert=True,
        failures_dir=env["failures_dir"],
    )
    assert list(Path(env["failures_dir"]).glob("*.json")) == []


# ── schema/构建函数契约 ───────────────────────────────────────────────────────


def test_snapshot_schema_and_atomic_write(env: dict) -> None:
    schedules, tasks = _load_process_state(env["config_dir"])
    snapshot = build_loaded_state_snapshot(env["config_dir"], schedules, tasks, pid=7)
    assert snapshot["schema"] == SNAPSHOT_SCHEMA
    assert snapshot["schedule_slots"] == ["daily_kline", "pre_market"]
    assert snapshot["tasks_count"] == 2
    assert set(snapshot["files"]) == {"schedule.yaml", "tasks.yaml"}
    assert all("sha256" in v and "mtime_ns" in v for v in snapshot["files"].values())
    path = write_loaded_state_snapshot(snapshot, env["snapshot"])
    assert path.exists()
    assert not path.with_name(path.name + ".tmp").exists(), "原子写后不得残留 tmp 文件"


def test_restore_matches_snapshot_again(env: dict) -> None:
    """改盘→红→还原→转绿（端到端语义的单测缩影）。"""
    _export_snapshot(env)
    original = (env["config_dir"] / "schedule.yaml").read_bytes()
    env["config_dir"].joinpath("schedule.yaml").write_bytes(original + b"# drift\n")
    report = check_config_effect(
        config_dir=env["config_dir"], snapshot_path=env["snapshot"], alert=False
    )
    assert report.status == "mismatch"
    env["config_dir"].joinpath("schedule.yaml").write_bytes(original)
    report = check_config_effect(
        config_dir=env["config_dir"], snapshot_path=env["snapshot"], alert=False
    )
    assert report.status == "ok", report.summary
