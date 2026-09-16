# [A_test] module_id: MOD-RESCHED-PROFILE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-RESCHED-PROFILE | docs/03_modules/_cross_layer/resource_profile_registry/blueprint.md | §
# [MODULE] tests.scripts.test_generate_resource_profile_registry
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/scripts/test_generate_resource_profile_registry.py
# [TTL] task_bound
"""生成器测试：ps1 解析/槽位抽取/合并保全/漂移检测/孤儿标记（tmp_path，禁写生产路径）。"""
from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "gen_resched_profile_test", REPO_ROOT / "scripts" / "governance" / "generators" / "generate_resource_profile_registry.py"
)
gen = importlib.util.module_from_spec(_SPEC)
sys.modules.setdefault("gen_resched_profile_test", gen)
_SPEC.loader.exec_module(gen)

NOW = datetime(2026, 9, 16, 4, 0, tzinfo=timezone.utc)  # 周三中午北京时间


def test_parse_ps1_entities_covers_all_task_names():
    ents, warns = gen.parse_ps1_entities()
    tids = {e["task_id"] for e in ents}
    # 全部 19 个 ZephyrAlpha_ 任务任务名（来自 13 个 ps1 真源；2026-09-16 采样器
    # scan/writeback 两任务接线 +1 源 +2 实体）
    assert "sch_factory_lane_c" in tids
    assert "sch_c4_exam" in tids
    assert "sch_ollama_serve" in tids
    assert "sch_intraday_fund_flow" in tids
    assert "sch_data_scheduler" in tids
    assert "sch_trading_watchdog" in tids
    assert "sch_resource_sampler_scan" in tids
    assert "sch_resource_sampler_writeback" in tids
    assert len(ents) == 19
    # 杂音捕获杜绝：无变量名误捕实体
    assert not any("task_name" in t or t.endswith("_name") or t == "sch_svc" for t in tids)


def test_parse_ps1_triggers_extracted_from_truth():
    ents, _ = gen.parse_ps1_entities()
    by = {e["task_id"]: e for e in ents}
    # FactoryLaneC：周六 10:00（ps1 真源 Weekly DaysOfWeek Saturday At 10:00）
    assert by["sch_factory_lane_c"]["window_expr"] == "0 10 * * 6"
    assert by["sch_factory_lane_c"]["exclusive_group"] == ["mine_vs_exam"]
    # IntradayFundFlow：5 个每日触发点（'|'-连接）
    expr = by["sch_intraday_fund_flow"]["window_expr"]
    assert expr.count("|") == 4 and expr.startswith("5 10 * * *")
    # PostSettlement：工作日 15:30（多 dow 连接）
    assert by["sch_post_settlement"]["window_expr"] == "30 15 * * 1,2,3,4,5"
    # AtLogOn 常驻 → event + est=0
    assert by["sch_ollama_serve"]["window_type"] == "event"
    assert by["sch_ollama_serve"]["est_duration_min"] == 0
    # TradingWatchdog DISABLED → retired
    assert by["sch_trading_watchdog"]["status"] == "retired"


def test_parse_schedule_slots_21_slots_cron_verbatim():
    ents, warns = gen.parse_schedule_slots()
    assert len(ents) == 21
    by = {e["task_id"]: e for e in ents}
    assert by["data_slot_daily_kline"]["window_expr"] == "30 16 * * 1-5"  # APScheduler dow 归一为标准 cron
    assert by["data_slot_daily_kline"]["pool"] == "heavy"
    assert by["data_slot_auction_highfreq"]["pool"] == "realtime"
    assert by["data_slot_nightly_sentiment"]["resource_class"] == "light"  # 规则法不耗 LLM（方案 §5-2 防误报）
    assert by["data_slot_weekend_calibration"]["exclusive_group"] == ["ch_bulk_write"]


def test_manual_entities_seed_and_planned_status():
    ents = gen.manual_entities()
    tids = {e["task_id"] for e in ents}
    assert "manual_factory_grid_executor" in tids
    assert "manual_repair_kline_tz" in tids
    assert "dynamic_local_replay" in tids
    repair = next(e for e in ents if e["task_id"] == "manual_repair_kline_tz")
    assert repair["exclusive_group"] == ["repair_passport", "ch_bulk_write"]
    assert all(e["status"] == "planned" for e in ents)  # 手动实体行为零变更（方案 §8）


def test_merge_preserve_keeps_human_and_measured_fields(tmp_path):
    fresh = [
        {"task_id": "a", "resource_class": "cpu_heavy", "window_expr": "0 2 * * *", "window_type": "cron",
         "schedule_truth_source": "x.ps1", "trading_sensitive": True, "status": "active",
         "peak_mem_gb": 2.0, "est_duration_min": 30, "module_id": None, "measured": None, "samples_uri": "u"},
    ]
    existing = [
        {"task_id": "a", "module_id": "MOD-HUMAN-1", "peak_mem_gb": 4.5, "est_duration_min": 99,
         "status": "active", "notes_zh": "人复核过",
         "measured": {"peak_mem_gb": 5.1, "p90_duration_min": 42, "samples": 7, "last_at": "t"},
         "samples_uri": ".runtime/logs/resource_samples/a.jsonl",
         "window_expr": "旧值将被刷新"},
    ]
    merged, warns = gen.merge_preserve(fresh, existing)
    m = merged[0]
    assert m["module_id"] == "MOD-HUMAN-1"  # 人填保全
    assert m["peak_mem_gb"] == 4.5 and m["est_duration_min"] == 99
    assert m["measured"]["samples"] == 7  # 采样器独占保全
    assert m["window_expr"] == "0 2 * * *"  # 生成器字段刷新（时间值不搬家）


def test_merge_preserve_marks_orphaned_source(tmp_path):
    fresh = [{"task_id": "still_here", "status": "active"}]
    existing = [{"task_id": "ghost", "status": "active", "notes_zh": ""}]
    merged, warns = gen.merge_preserve(fresh, existing)
    ghost = next(e for e in merged if e["task_id"] == "ghost")
    assert ghost["status"] == "orphaned_source"
    assert any("ghost" in w for w in warns)


def test_full_registry_build_and_drift_check(tmp_path):
    out = tmp_path / "reg.yaml"
    reg = gen.build_registry(existing_path=tmp_path / "nonexistent.yaml", output_path=out)
    assert reg["total_entities"] >= 50
    assert reg["mem_ceiling_gb"] == 10.0
    assert set(gen.GROUPS) == {"ch_bulk_write", "tick_drain", "mine_vs_exam", "repair_passport", "gpu_default", "llm_local"}
    text = gen.registry_text(reg)
    out.write_text(text, encoding="utf-8")
    # 磁盘内容可解析且 --check 无漂移
    d = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert d["total_entities"] == len(d["entities"])
    # 漂移检测（同输出路径，无人工篡改 → 无漂移）
    import subprocess

    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "governance" / "generators" / "generate_resource_profile_registry.py"),
         "--check", "--output", str(out), "--existing", str(out)],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, r.stdout + r.stderr


def test_e0_mapping_layer():
    assert gen.E0_CLASS_TO_RESOURCE["local"] == "light"
    assert gen.E0_CLASS_TO_RESOURCE["local_gpu"] == "cpu_heavy"
    assert gen.E0_CLASS_TO_RESOURCE["mixed"] == "cpu_heavy"
    # trading_sensitive 推导：heavy 类受 E0 管辖
    assert "db_heavy" in gen.TRADING_SENSITIVE_CLASSES
    assert "light" not in gen.TRADING_SENSITIVE_CLASSES
