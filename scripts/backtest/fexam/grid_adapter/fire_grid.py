# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/90_execution_log.md | 网格考点火器（五门前置fail-closed）
# [MODULE] scripts.backtest.fexam.grid_adapter.fire_grid.py
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] 见文件内 import
# [CONSUMERS] run_fexam.py 或手工 CLI
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] staging 转正件；判定面不入核
# [MODIFY-GUARD] docs/_working/matrix_campaign/90_execution_log.md
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 见 docstring
# [TESTS] tests/backtest/fexam/
# [TTL] task_bound
# create-guard-not-dup: tmp 24h TTL 抢救转正件（Owner 批 P0-1），对拍结论已锁定随文件
# -*- coding: utf-8 -*-
"""F道·网格点火启动器（st-matrix-20261006 / F lane）。

消费 emit_configs.py 产出的 fire_plan.yaml + *.subspace.json，逐行发射
factory_grid_executor.py（冻结件零改动，纯外挂）。

门位（全部 fail-closed，任一不过=禁点火）：
  G1 GPU 空闲门   nvidia-smi 显存占用 < 阈值 且 无 st-t3series 进程（探测失败=忙）
  G2 预算钳制门   行格点数经 factory_grid_executor._apply_prereg_budget 钳制（冻结册真源）；
                  战役累计已点格点 + 本行格点 ≤ grid_points_cap；墙钟估算
                  cells×per_point_seconds_measured ≤ single_job_wall_clock_cap_hours
  G3 收割守卫门   process_reaper_keep.txt 须已登记 "factory_grid_executor"（只检查不代写——
                  本车道纪律禁写车道外文件；缺登记=打印指令后拒发，防长批被 reaper 误杀）
  G4 人位确认门   点火须 --fire --i-understand-ignition 双旗标；缺省 dry-run（只验证不发车，
                  零 GPU 占用）。E0 日历问闸不旁路：发射命令不带 --skip-compute-gate。

断点续跑：fire_state.json 逐行记 pending/fired/done/failed + run_dir；重启跳过 done
（判据=该行 out_dir 存在 summary.json，机生判非肉眼）；fitted 无状态重入。

用法：
  python fire_grid.py                    # dry-run：全门预检+打印发射计划（不占 GPU）
  python fire_grid.py --row std_device   # 只处理指定行（可逗号分隔）
  python fire_grid.py --fire --i-understand-ignition   # 真点火（四门全过才发）
  python fire_grid.py --status           # 查看断点清单
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[3]
_EXECUTOR = _REPO / "scripts" / "backtest" / "factory_grid_executor.py"
_REAPER_KEEP = _REPO / "data" / "runtime" / "process_reaper_keep.txt"
INTAKE_DIR = _REPO / "data" / "strategy_intake"
STATE_PATH = _HERE / "fire_state.json"
LOG_PATH = _HERE / "fire_log.jsonl"

sys.path.insert(0, str(_REPO / "src"))
sys.path.insert(0, str(_REPO / "scripts" / "backtest"))
sys.path.insert(0, str(_REPO / "scripts" / "backtest" / "translated"))

from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: E402

#: G1 判定（2026-10-06 修正：桌面合成常驻 ~4.3GB 是基线非任务占用，阈值法在本机恒忙=bug；
#: 改为"非系统计算进程名单"法——query-compute-apps 命中的进程名剔除 Windows 桌面族后为空=空闲）
VRAM_DESKTOP_BASELINE_MB = 5000  #: 桌面基线缓冲（仅作日志参考，不参与判定）
SYSTEM_GPU_PROC_NAMES = (
    "dwm.exe",
    "explorer.exe",
    "searchhost.exe",
    "shellhost.exe",
    "startmenuexperiencehost.exe",
    "msedgewebview2.exe",
    "lockapp.exe",
    "nvidia overlay.exe",
    "nvcontainer.exe",
    "nvidia web helper.exe",
    "chrome.exe",
    "msedge.exe",
    "firefox.exe",
    "widgetservice.exe",
)
#: st-t3series 进程识别：只查 python 家族（防 WMI 查询进程自匹配——其自身 cmdline 含匹配串）
BUSY_PROCESS_PATTERN = "t3series"


def log(event: str, **kw) -> None:
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "event": event, **kw}
    line = json.dumps(rec, ensure_ascii=False)
    print(line)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


# ── G1 GPU 空闲门 ────────────────────────────────────────────────────────────


def gpu_probe() -> dict:
    """nvidia-smi 双探针（显存水位 + 计算进程 cmdline）。任何探测失败=忙（fail-closed）。"""

    def _smi(args: list[str]) -> str:
        try:
            p = run_subprocess_hidden(["nvidia-smi"] + args, timeout=20, encoding="utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001
            return f"__error__:{type(exc).__name__}: {exc}"
        if p.returncode != 0:
            return f"__error__:{(p.stderr or '').strip()[:120]}"
        return (p.stdout or "").strip()

    mem = _smi(["--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"])
    if mem.startswith("__error__"):
        return {"idle": False, "reason": f"nvidia-smi 不可达（fail-closed）: {mem}"}
    try:
        used_mb, total_mb = (int(x.strip()) for x in mem.splitlines()[0].split(","))
    except Exception as exc:  # noqa: BLE001
        return {"idle": False, "reason": f"显存水位解析失败（fail-closed）: {exc}: {mem!r}"}
    # 计算进程名单（记录留档；判定改用确定性双判据——进程名穷举对桌面生态不可维护）
    procs = _smi(["--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader"])
    t3_hit = _t3series_running()
    free_mb = total_mb - used_mb
    # 确定性空闲双判据：
    # ①对方战役日志目录 30 分钟无更新（t1r_*.log 停更=收卷）
    # ②空余显存 >= 8000MB（桌面基线 4.3GB 恒占，但 24GB 卡余量足够本任务 ~6GB）
    t3_log_stale = _t3series_logs_stale()
    idle = t3_log_stale and free_mb >= 8000
    if not t3_log_stale:
        reason = "st-t3series 日志 30 分钟内有更新（未收卷）"
    elif free_mb < 8000:
        reason = f"空余显存 {free_mb}MB < 8000MB"
    else:
        reason = "ok（对方日志已停更+显存余量充足）"
    return {
        "idle": idle,
        "reason": reason,
        "vram_used_mb": used_mb,
        "vram_total_mb": total_mb,
        "vram_free_mb": free_mb,
        "compute_apps": procs.splitlines()[:8],
        "t3series_running": t3_hit,
        "t3series_logs_stale": t3_log_stale,
    }


def _t3series_logs_stale() -> bool:
    """对方战役日志（.runtime/tmp/st-t3series-20261006/*.log）30 分钟无更新=收卷。失败=未收卷（fail-closed）。"""
    try:
        log_dir = _HERE.parent / "st-t3series-20261006"
        if not log_dir.is_dir():
            return True  # 目录不存在=对方从未开工/已清场
        import time as _t

        newest = max(f.stat().st_mtime for f in log_dir.glob("*.log") if f.is_file())
        return (_t.time() - newest) > 1800
    except Exception:  # noqa: BLE001
        return False  # fail-closed


def _t3series_running() -> bool:
    """python 家族进程 cmdline 匹配（只查 python.exe/pythonw.exe——排除 WMI 查询进程自匹配）。"""
    try:
        p = run_subprocess_hidden(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | "
                "Where-Object {$_.CommandLine -match 't3series'} | Select-Object -First 1 ProcessId",
            ],
            timeout=30,
            encoding="utf-8",
            errors="replace",
        )
        return bool(p.returncode == 0 and (p.stdout or "").strip())
    except Exception:  # noqa: BLE001
        return True  # 探测失败按忙处理（fail-closed）


# ── G2 预算钳制门 ────────────────────────────────────────────────────────────


def budget_check(row: dict, fired_cells_total: int) -> dict:
    """冻结册预算钳制（真源=config/search_space_prereg.yaml，经执行器原函数零复制）。"""
    import factory_grid_executor as fge

    n = fge._apply_prereg_budget(str(row.get("stage") or ""), int(row["n_samples"]))
    caps = fge._load_prereg_caps(str(row.get("stage") or ""))
    cap_total = int(caps.get("grid_points_cap") or 0)
    over_campaign = cap_total and (fired_cells_total + n) > cap_total
    per_point = float(caps.get("per_point_seconds_measured") or 0)
    wall_h = (n * per_point / 3600.0) if per_point else None
    cap_h = float(caps.get("single_job_wall_clock_cap_hours") or 0)
    return {
        "clamped_n": n,
        "grid_points_cap": cap_total,
        "campaign_over_cap": bool(over_campaign),
        "wall_clock_hours_estimate": round(wall_h, 4) if wall_h is not None else None,
        "wall_clock_cap_hours": cap_h,
        "wall_clock_ok": (wall_h is None) or (cap_h <= 0) or (wall_h <= cap_h),
    }


# ── G3 收割守卫门 ────────────────────────────────────────────────────────────


def reaper_keep_ok() -> tuple[bool, str]:
    if not _REAPER_KEEP.exists():
        return False, f"{_REAPER_KEEP} 不存在——长批任务未登记，reaper 可能误杀（禁发）"
    txt = _REAPER_KEEP.read_text(encoding="utf-8", errors="replace")
    if "factory_grid_executor" not in txt:
        return False, "process_reaper_keep.txt 未登记 factory_grid_executor——先登记再点火（本车道禁代写）"
    return True, "ok"


# ── 状态与断点续跑 ───────────────────────────────────────────────────────────


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"rows": {}, "fired_cells_total": 0}


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def find_done_run_dir(cfg_name: str) -> str | None:
    """机生判 done：grid_* 目录 summary.json 含本行 subspace 且 mode=batch_b_subspace。"""
    if not INTAKE_DIR.exists():
        return None
    cfg_path = _HERE / "grid_configs" / f"{cfg_name}.subspace.json"
    if not cfg_path.exists():
        return None  # row_id 带 @v1 等后缀时无同名文件——按未完成处理（非崩溃）
    want = json.loads(cfg_path.read_text(encoding="utf-8"))
    for d in sorted(INTAKE_DIR.glob("grid_*"), reverse=True):
        sj = d / "summary.json"
        if not sj.exists():
            continue
        try:
            s = json.loads(sj.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if s.get("mode") == "batch_b_subspace" and (s.get("subspace") or {}) == want:
            return d.name
    return None


def fire_row(row: dict, dry_run: bool) -> int:
    name = str(row.get("row_id") or f"{row['config']}@{row.get('factor_surface') or 'v1'}")
    state = load_state()
    st = state["rows"].get(name, {"status": "pending"})
    done_dir = find_done_run_dir(row["config"])
    if st.get("status") == "done" or done_dir:
        st.update(status="done", run_dir=done_dir or st.get("run_dir"))
        state["rows"][name] = st
        save_state(state)
        log("skip_done", row=name, run_dir=done_dir)
        return 0

    # v1_value 因子面仅 t3a 冻结卡通道可注入（T6：factor_surface 随 stage t3 家族注入，
    # 普通批次 CLI 无此参数）——本行显式 blocked，禁静默降级为 v1 重复跑（fake coverage）。
    if str(row.get("factor_surface") or "v1") not in ("v1", ""):
        st.update(
            status="blocked_channel",
            reason=(
                f"factor_surface={row['factor_surface']} 仅 --stage t3 家族通道可注入（t3a 冻结卡钳制）；"
                "普通批次不可达——需 Owner 裁定开 t3 通道或弃行"
            ),
        )
        state["rows"][name] = st
        save_state(state)
        log("skip_channel", row=name, reason=st["reason"])
        return 3

    gpu = gpu_probe()
    budget = budget_check(row, int(state.get("fired_cells_total", 0)))
    keep = reaper_keep_ok()
    gates = {
        "G1_gpu_idle": gpu["idle"],
        "G2_budget": (not budget["campaign_over_cap"]) and budget["wall_clock_ok"],
        "G3_reaper_keep": keep[0],
    }
    if not dry_run:
        gates["G4_ignition_flags"] = True  # 已过 --fire + --i-understand-ignition 双旗标
    log("gate_check", row=name, dry_run=dry_run, gates=gates, gpu=gpu, budget=budget, reaper_keep=keep[1])
    if not dry_run and not all(gates.values()):
        st.update(status="blocked", gates=gates)
        state["rows"][name] = st
        save_state(state)
        return 3

    subspace_json = (_HERE / "grid_configs" / row["subspace_file"]).read_text(encoding="utf-8")
    cmd = [
        sys.executable,
        str(_EXECUTOR),
        "--subspace-json",
        subspace_json,
        "--n-samples",
        str(budget["clamped_n"]),
        "--start",
        str(row.get("start")),
        "--end",
        str(row.get("end")),
        "--engine",
        "auto",
    ]
    log("fire", row=name, cmd=[c if len(c) < 80 else c[:77] + "..." for c in cmd], dry_run=dry_run)
    if dry_run:
        # dry-run 恒打印发射计划（含被门挡下的行，供留守窗复核）；G1 不过=预期（今晚占卡）
        st.update(status="dry_run_ok" if all(gates.values()) else "dry_run_blocked", gates=gates, cmd_preview=cmd[:4])
        state["rows"][name] = st
        save_state(state)
        return 0

    st.update(status="fired", started_at=time.strftime("%Y-%m-%dT%H:%M:%S"))
    state["rows"][name] = st
    state["fired_cells_total"] = int(state.get("fired_cells_total", 0)) + int(row["n_samples"])
    save_state(state)
    # 长跑发射：子进程输出追加落盘（无闪窗/无内存缓冲），供发射后审计
    with open(_HERE / "fire_last_run.log", "ab") as _lf:
        p = run_subprocess_hidden(
            cmd, cwd=str(_REPO), capture_output=False, text=False, stdout=_lf, stderr=subprocess.STDOUT
        )
    if p.returncode == 0:
        done_dir = find_done_run_dir(row["config"])
        st.update(status="done", run_dir=done_dir, finished_at=time.strftime("%Y-%m-%dT%H:%M:%S"))
        state["rows"][name] = st
        save_state(state)
        log("done", row=name, run_dir=done_dir, rc=0)
        return 0
    st.update(status="failed", rc=p.returncode)
    state["rows"][name] = st
    save_state(state)
    log("failed", row=name, rc=p.returncode)
    return p.returncode or 1


def main() -> int:
    ap = argparse.ArgumentParser(description="F道 网格点火启动器（默认 dry-run）")
    ap.add_argument("--fire", action="store_true", help="真点火（还须 --i-understand-ignition）")
    ap.add_argument("--i-understand-ignition", action="store_true", help="人位确认：知道这是真 GPU 跑批")
    ap.add_argument("--row", default="", help="只处理指定行（逗号分隔 config 名）")
    ap.add_argument("--status", action="store_true", help="只看断点清单")
    args = ap.parse_args()
    if args.fire and not args.i_understand_ignition:
        print("[G4] --fire 须搭配 --i-understand-ignition（人位确认门）")
        return 2

    plan = yaml.safe_load((_HERE / "grid_configs" / "fire_plan.yaml").read_text(encoding="utf-8"))
    rows = plan.get("rows") or []
    if args.row:
        want = {x.strip() for x in args.row.split(",") if x.strip()}
        rows = [r for r in rows if r["config"] in want]
        if not rows:
            print(f"[fire] plan 中无行: {sorted(want)}")
            return 2

    if args.status:
        state = load_state()
        for r in rows:
            st = state["rows"].get(r["config"], {})
            print(
                f"{r['config']:<20} cells={r['n_samples']:>4} surface={r['factor_surface']:<9} "
                f"status={st.get('status', 'pending'):<10} run_dir={st.get('run_dir', '-')}"
            )
        return 0

    dry = not (args.fire and args.i_understand_ignition)
    rc = 0
    for r in rows:
        rc = fire_row(r, dry_run=dry) or rc
    log("campaign_end", dry_run=dry, rows=len(rows), rc=rc)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
