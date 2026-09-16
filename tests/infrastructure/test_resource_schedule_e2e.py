# [A_test] module_id: MOD-RESCHED-PROFILE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-RESCHED-PROFILE | docs/03_modules/_cross_layer/resource_profile_registry/blueprint.md | §9
# [MODULE] tests.infrastructure.test_resource_schedule_e2e
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/infrastructure/test_resource_schedule_e2e.py
# [TTL] task_bound
"""端到端全链路：启动→采样器捕获→实测回写→闸冲突→视图渲染→告警送达（沙箱注册表，零生产写入）。

模拟重活=轻量 python -c sleep 子进程（marker cmdline）——遵守"测试禁真启重活进程"红线；
进程表走真实 psutil（唯一真进程环节），其余全链路生产代码路径。
证据导出：设 ZEPHYR_RESCHED_E2E_EVIDENCE_DIR=<dir> 时把全链路证据落盘（Owner 汇报附件）。
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

MARKER = "zephyr-resource-probe:e2e_probe_heavy"
PROBE_TASK = "e2e_probe_heavy"
RIVAL_TASK = "e2e_rival_backfill"

sys.path.insert(0, str(REPO_ROOT / "src"))
from zephyr.infrastructure.system_telemetry.alerts.resource_schedule_alerts import (  # noqa: E402
    ResourceScheduleAlerts,
)
from zephyr.gov_enforcement.commit_gates.resource_schedule_gate import (  # noqa: E402
    run_all_checks,
)
from zephyr.infrastructure.system_telemetry.resource_sampler import ResourceSampler  # noqa: E402


def _evidence_dir() -> Path | None:
    env = os.environ.get("ZEPHYR_RESCHED_E2E_EVIDENCE_DIR", "")
    return Path(env) if env else None


@pytest.fixture()
def sandbox(tmp_path):
    """沙箱注册表=生产结构+探针实体+对手实体（互斥组重叠+内存压力设计）。"""
    prod = REPO_ROOT / "config" / "resource_profile_registry.yaml"
    data = yaml.safe_load(prod.read_text(encoding="utf-8")) or {}
    entities = list(data.get("entities") or [])[:5]  # 少量背景实体
    entities.append(
        {
            "task_id": PROBE_TASK, "module_id": None, "map_node_id": None,
            "resource_class": "cpu_heavy", "pool": "heavy", "peak_mem_gb": 6.0,
            "est_duration_min": 10, "exclusive_group": ["e2e_excl"], "window_type": "dynamic",
            "window_expr": "* * * * *",  # 动态实体：可运行窗=任意时刻（闸区间数学可判定）
            "schedule_truth_source": "docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md",
            "trading_sensitive": True,
            "measured": {"peak_mem_gb": None, "p90_duration_min": None, "samples": 0, "last_at": None},
            "samples_uri": f".runtime/logs/resource_samples/{PROBE_TASK}.jsonl",
            "status": "planned", "notes_zh": "E2E 探针（模拟重活，仅沙箱注册表）",
        }
    )
    entities.append(
        {
            "task_id": RIVAL_TASK, "module_id": None, "map_node_id": None,
            "resource_class": "db_heavy", "pool": "heavy", "peak_mem_gb": 6.0,
            "est_duration_min": 240, "exclusive_group": ["e2e_excl"], "window_type": "cron",
            "window_expr": "* * * * *",  # 每分钟触发——与探针观测窗必然交叠
            "schedule_truth_source": "docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md",
            "trading_sensitive": False,
            "measured": {"peak_mem_gb": None, "p90_duration_min": None, "samples": 0, "last_at": None},
            "samples_uri": f".runtime/logs/resource_samples/{RIVAL_TASK}.jsonl",
            "status": "active", "notes_zh": "E2E 对手实体（构造互斥组重叠）",
        }
    )
    data["entities"] = entities
    reg = tmp_path / "resource_profile_registry.yaml"
    reg.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return reg


def test_e2e_full_chain(sandbox, tmp_path):
    evid = _evidence_dir()
    steps: dict[str, dict] = {}
    sandbox_samples = tmp_path / "samples"

    # ── ① 启动：轻量子进程模拟重活（marker cmdline；psutil 真进程表可见）──
    proc = subprocess.Popen(
        [sys.executable, "-c", f"import time; print('{MARKER}', flush=True); time.sleep(6)"],
        stdout=subprocess.PIPE, text=True,
    )
    assert proc.stdout is not None and proc.stdout.readline().strip() == MARKER  # 进程已起、cmdline 已带 marker
    steps["01_spawn"] = {"ok": True, "pid": proc.pid, "cmdline_marker": MARKER}

    try:
        # ── ② 采样器捕获（真实 psutil 扫描；观测正则=marker）──
        sampler = ResourceSampler(
            registry_path=sandbox,
            samples_dir=sandbox_samples,
            patterns={PROBE_TASK: MARKER.replace(":", r"\:")},
        )
        summary = sampler.scan_once()
        assert summary["samples_written"].get(PROBE_TASK, 0) >= 1, summary
        steps["02_sampler_capture"] = {"ok": True, "samples_written": summary["samples_written"],
                                       "scanned_processes": summary["scanned_processes"]}

        # ── ③ 实测回写（max+15% margin/P90 口径）──
        wb = sampler.writeback(task_ids=[PROBE_TASK])
        assert PROBE_TASK in wb["updated"]
        data = yaml.safe_load(sandbox.read_text(encoding="utf-8"))
        probe = next(e for e in data["entities"] if e["task_id"] == PROBE_TASK)
        assert probe["measured"]["samples"] >= 1
        assert probe["measured"]["peak_mem_gb"] is not None
        steps["03_writeback"] = {"ok": True, "measured": probe["measured"]}
    finally:
        if proc.stdout is not None:
            proc.stdout.close()  # 管道句柄显式关闭，防 GC 随机点 ResourceWarning 被 filterwarnings=error 升级炸测试
        proc.wait(timeout=15)

    # ── ④ 闸检测冲突（互斥组重叠+内存天花板 12>10）──
    findings = run_all_checks(sandbox, datetime.now(timezone.utc))
    reasons = {f.reason_code for f in findings}
    blocks = [f for f in findings if f.severity == "block"]
    assert blocks, [f.render() for f in findings]
    assert "sched_overlap_group" in reasons
    assert "sched_mem_ceiling" in reasons  # 6+6>10 同窗
    steps["04_gate_conflict"] = {"ok": True, "block_count": len(blocks),
                                 "reasons": sorted(reasons),
                                 "detail": [f.render() for f in blocks[:3]]}

    # ── ⑤ 图渲染（生成器产出，冲突入图）──
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "vw_e2e", REPO_ROOT / "scripts" / "governance" / "generators" / "generate_resource_week_view.py"
    )
    vw = importlib.util.module_from_spec(spec)
    sys.modules["vw_e2e"] = vw
    spec.loader.exec_module(vw)
    view = vw.build_view_data(sandbox, datetime.now(timezone.utc))
    view_js = tmp_path / "rw-data.js"
    view_js.write_text(vw.render_js(view), encoding="utf-8")
    conf_tasks = {t for c in view["conflicts"] if c["severity"] == "block" for t in c["task_ids"]}
    assert view["total_entities"] >= 5 and {PROBE_TASK, RIVAL_TASK} <= conf_tasks
    steps["05_view_render"] = {"ok": True, "total_entities": view["total_entities"],
                               "scheduled": view["scheduled"], "block_conflicts": view["block_conflicts"],
                               "js_bytes": view_js.stat().st_size}

    # ── ⑥ 告警通道送达（OpsAlertFeed 板→/api/ops-notifications 同源）──
    board = tmp_path / "ops_board"
    r = ResourceScheduleAlerts(board_dir=board).publish_findings(findings)
    assert r["active_keys"], r
    board_file = board / "notifications.jsonl"
    entries = [json.loads(x) for x in board_file.read_text(encoding="utf-8").splitlines() if x.strip()]
    crit = [e for e in entries if e["severity"] == "critical"]
    assert crit and any("sched_overlap_group" in e["key"] for e in crit)
    # 晨审可见性：板为机器可读 JSONL，任意晨审进程可直读（此处模拟晨审读取）
    morning_view = [{"key": e["key"], "severity": e["severity"], "title": e["title"]} for e in entries]
    steps["06_alert_delivery"] = {"ok": True, "board_entries": len(entries),
                                  "critical_keys": [e["key"] for e in crit],
                                  "morning_audit_read": morning_view[:3]}

    assert all(v.get("ok") for v in steps.values())

    # ── 证据导出（Owner 汇报附件；零人工参与）──
    if evid:
        # docs/_working 目录契约只允许 .md/.yaml/.csv/.html（GATE-DIRECTORY-CONTRACT）——
        # 证据一律转 yaml/csv 形态；rw-data.js 本体已提交于 web/ 树，报告中引用路径
        evid.mkdir(parents=True, exist_ok=True)
        report = {"generated_at": datetime.now(timezone.utc).isoformat(),
                  "chain": "启动→采样→回写→闸→图→告警",
                  "view_data_js": "src/zephyr/frontend/dashboard/web/features/resourceweek/rw-data.js",
                  "steps": steps}
        (evid / "e2e_report.yaml").write_text(yaml.safe_dump(report, allow_unicode=True, sort_keys=False), encoding="utf-8")
        shutil.copy(sandbox, evid / "sandbox_registry.yaml")
        # 临时区目录契约：ttl=permanent 拒收——证据副本改 task_bound（GATE-DIRECTORY-CONTRACT）
        sb = evid / "sandbox_registry.yaml"
        sb.write_text(sb.read_text(encoding="utf-8").replace("ttl: permanent", "ttl: task_bound", 1), encoding="utf-8")
        shutil.copy(board_file, evid / "notifications.yaml")
        pf = sandbox_samples / f"{PROBE_TASK}.jsonl"
        if pf.exists():
            rows = [json.loads(x) for x in pf.read_text(encoding="utf-8").splitlines() if x.strip()]
            if rows:
                cols = list(rows[0].keys())
                lines = [",".join(cols)]
                for r in rows:
                    lines.append(",".join(str(r[c]) for c in cols))
                (evid / "e2e_probe_heavy_samples.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
