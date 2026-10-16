#!/usr/bin/env python
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md | §disk_floor
# [MODULE] scripts.ops.vhdx_floor_watch
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.io.audit_jsonl_writer (append_audit_jsonl 同款机制: 采样行与告警行统一写面);
#                zephyr.shared.utils.time_utils (now_utc, RULE-SCHEMA-TZ: 禁 datetime.now()/time.time() 生成时间戳)
# [CONSUMERS] 计划任务/人工手动触发（默认 one-shot）; session_worktree._disk_floor_config（阈值读取复用本件 read_disk_floor_config）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 只采样+告警，**零删停**（熔断动作=告警 escalated，执行留 Owner——NL-6 物理删除=Owner 门位）;
#              阈值单一真源=config/flags.yaml flags.disk_floor.min_free_gib（与 session_worktree create 前置闸同键，
#              禁复制字面量）; 采样行格式与 data/audit-trail/vhdx_growth_series.jsonl 既有 3 行逐字段对齐
#              （ts/vhdx_gb/d_free_gb/delta_vs_prev_gb/d_red_line_gb/d_below_red_line/d_red_line_reason）;
#              采样/告警失败不抛（监控自身异常不逃逸，与 ch_health_probe 同口径）;
#              告警双落点=.runtime/workspace_alerts/ 告警件 + .runtime/audit/disk_floor_alerts.jsonl 审计行;
#              节流=默认 60min（读序列自身末行 ts 判距，零额外状态文件）; --watch 常驻=threading.Event.wait
#              可中断等待（非 raw sleep-loop），signal 到位即自动退出（四要素之自动关闭）
# [MODIFY-GUARD] config/flags.yaml flags.disk_floor（阈值真源，本件只读禁改）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] sample_once 永不抛（OSError/解析失败收入返回值 errors 列表）; exit 0=采样成功/节流跳过;
#                  exit 1=红线告警已发（采样本身成功）; exit 2=采样设施故障（盘不可用/序列不可写）
# [TESTS] tests/scripts/test_vhdx_floor_watch.py（假 vhdx 实测采样行/阈值两侧/节流/告警双落点/格式对齐）
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 默认 one-shot 由 OS 计划任务/人工事件驱动（与 ch_health_probe 同部署形态）；
#                         --watch 常驻为显式部署选项，等待用 threading.Event.wait(timeout) 可中断事件型，
#                         非禁令针对的 cron/Timer/raw sleep-loop；常驻部署须登记 reaper 白名单（见下）
# noqa: m11-perm-manual-legitimate  M11豁免: one-shot 形态由 OS 计划任务/人工按需触发（schtasks hourly，与 ch_health_probe 同部署形态），CLI argparse 面为人工采样入口，非常驻自启服务/非 daemon
#
# 【reaper 白名单登记说明】--watch 常驻部署时，由使用者向 data/runtime/process_reaper_keep.txt
# 追加一行子串（每行一个 cmdline 子串，process_reaper 扫描命中即豁免收割）：
#     vhdx_floor_watch
# one-shot 形态（默认）进程秒级退出，无需登记。
# create-guard-not-dup: 本模块只 stat 磁盘文件大小+盘剩余并告警，不解析算法流程也不解析文件头结构——命中词 parse ts 系 now_utc ISO 时间戳解析的散文碰撞，非 algo_flow_parse/file_header_parser 的第二实现
"""vhdx_floor_watch — VHDX 增长小时级采样 + D 盘红线告警（st-diskp0-20261015 防复发 D2）。

病灶：2026-10-15 D 盘 732G 100% 满（剩余 3.2MB）。结构层=HyperV data.vhdx 569.8GiB 静态地板；
触发层=当日裂变车道≈36GiB + tmp/审计≈8GiB；午间仅 19.5GiB 余量即已告急，而监控 6 天 3 观测点零报警
——缺一个"小时级 VHDX 增长 + D 盘剩余"连续观测面。本件补该观测：只采样+告警，**零删停**
（自动删停属 Owner 门位，本件永不执行）。

采样面：
    stat D:/HyperV/VMs/zephy-ch/data.vhdx 大小 → 追加 data/audit-trail/vhdx_growth_series.jsonl
    （字段与既有 3 行逐字段对齐：ts/vhdx_gb/d_free_gb/delta_vs_prev_gb/d_red_line_gb/
    d_below_red_line/d_red_line_reason）。

红线面（D 盘剩余 < flags.disk_floor.min_free_gib，出厂 15GiB）：
    ① .runtime/workspace_alerts/vhdx_disk_floor_<date>_<time>.json 告警件；
    ② .runtime/audit/disk_floor_alerts.jsonl 告警审计行（append_audit_jsonl 同款机制，
       自带 50MB 轮转）。告警级=escalated：只升级给 Owner，不自动处置。

部署（任选其一）：
    1. OS 计划任务小时级 one-shot（推荐，零常驻）：
       schtasks /Create /SC HOURLY /TN "ZephyrVhdxFloorWatch" /TR
         "python D:\\ZephyrAlpha\\scripts\\ops\\vhdx_floor_watch.py"
    2. 常驻 --watch（须按文件头说明登记 reaper 白名单）：
       python scripts/ops/vhdx_floor_watch.py --watch
    3. 人工即时采样：python scripts/ops/vhdx_floor_watch.py --force

配置（环境变量，可选）：
    VHDX_FLOOR_VHDX_PATH    vhdx 绝对路径（默认 D:/HyperV/VMs/zephyr-ch/data.vhdx）
    VHDX_FLOOR_MIN_INTERVAL 节流分钟（默认 60；--force 跳过）
    VHDX_FLOOR_ALERT_COOLDOWN 告警冷却分钟（默认 60，防刷屏）
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import threading
from datetime import datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from zephyr.shared.io.audit_jsonl_writer import append_audit_jsonl  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

DEFAULT_VHDX_PATH = Path(os.environ.get("VHDX_FLOOR_VHDX_PATH", "D:/HyperV/VMs/zephyr-ch/data.vhdx"))
DEFAULT_SERIES_REL = Path("data") / "audit-trail" / "vhdx_growth_series.jsonl"
DEFAULT_ALERT_DIR_REL = Path(".runtime") / "workspace_alerts"
DEFAULT_AUDIT_DIR_REL = Path(".runtime") / "audit"
SERIES_FILENAME = "vhdx_growth_series.jsonl"
ALERT_AUDIT_FILENAME = "disk_floor_alerts.jsonl"
GIB = 1024**3
_DEFAULT_MIN_INTERVAL_MIN = float(os.environ.get("VHDX_FLOOR_MIN_INTERVAL", "60"))
_DEFAULT_ALERT_COOLDOWN_MIN = float(os.environ.get("VHDX_FLOOR_ALERT_COOLDOWN", "60"))
_PID_FILE = _REPO_ROOT / "logs" / "vhdx_floor_watch.pid"


def read_disk_floor_config(repo_root: Path | str | None = None) -> tuple[bool, float]:
    """flags.disk_floor 阈值读取唯一点（(enabled, min_free_gib)；读不到=出厂 (True, 15.0)）。

    单一真源=config/flags.yaml flags.disk_floor.min_free_gib——session_worktree create
    前置闸与本件共用该键（消费方禁复制字面量）；本函数即那个共享读取面。
    """
    root = Path(repo_root) if repo_root else _REPO_ROOT
    try:
        import yaml

        doc = yaml.safe_load((root / "config" / "flags.yaml").read_text(encoding="utf-8")) or {}
        cfg = (doc.get("flags") or {}).get("disk_floor") or {}
        return bool(cfg.get("enabled", True)), float(cfg.get("min_free_gib") or 15.0)
    except Exception:  # noqa: BLE001 — 配置设施异常回出厂值（fail-closed：缺配置不豁免红线）
        return True, 15.0


def _last_series_row(series_path: Path) -> dict | None:
    """读序列末行（节流与 delta 基线；空/损坏文件=None）。"""
    try:
        if not series_path.exists():
            return None
        lines = [ln for ln in series_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if not lines:
            return None
        row = json.loads(lines[-1])
        return row if isinstance(row, dict) else None
    except Exception:  # noqa: BLE001 — 序列读损坏不阻断采样（delta 记 None）
        return None


def _parse_ts(value: object) -> datetime | None:
    """ISO ts 字符串 → aware datetime（失败=None）。"""
    try:
        dt = datetime.fromisoformat(str(value))
        return dt if dt.tzinfo else None
    except (ValueError, TypeError):
        return None


def build_series_row(
    *,
    vhdx_path: Path,
    free_disk_root: Path,
    red_line_gib: float,
    red_line_enabled: bool,
    prev_row: dict | None,
    note: str | None = None,
) -> tuple[dict, dict]:
    """构造一条采样行（纯函数，与既有序列字段逐一对齐；不落盘）。

    Returns:
        (row, facts)——facts 供告警面复用（vhdx_gb/d_free_gb/below 等，零二次计算漂移）。
    """
    ts = now_utc().isoformat()
    vhdx_gb: float | None = None
    vhdx_error: str | None = None
    try:
        if vhdx_path.exists():
            vhdx_gb = vhdx_path.stat().st_size / GIB
        else:
            vhdx_error = f"vhdx_missing: {vhdx_path}"
    except OSError as e:
        vhdx_error = f"vhdx_stat_failed: {e}"
    try:
        d_free_gb = shutil_disk_free(free_disk_root) / GIB
    except OSError as e:
        d_free_gb = -1.0
        vhdx_error = vhdx_error or f"disk_usage_failed: {e}"

    delta: float | None = None
    if vhdx_gb is not None and prev_row is not None and isinstance(prev_row.get("vhdx_gb"), (int, float)):
        delta = round(vhdx_gb - float(prev_row["vhdx_gb"]), 1)

    below = bool(red_line_enabled and d_free_gb >= 0 and d_free_gb < red_line_gib)
    reason = "disabled" if not red_line_enabled else ("below_red_line" if below else "ok")
    row: dict = {
        "ts": ts,
        "vhdx_gb": round(vhdx_gb, 1) if vhdx_gb is not None else None,
        "d_free_gb": round(d_free_gb, 2) if d_free_gb >= 0 else None,
        "delta_vs_prev_gb": delta,
        "d_red_line_gb": round(red_line_gib, 1),
        "d_below_red_line": below,
        "d_red_line_reason": reason,
    }
    if note:
        row["note"] = note
    if vhdx_error:
        row["vhdx_error"] = vhdx_error
    facts = {
        "ts": ts,
        "vhdx_gb": vhdx_gb,
        "d_free_gb": d_free_gb if d_free_gb >= 0 else None,
        "red_line_gib": red_line_gib,
        "red_line_enabled": red_line_enabled,
        "below": below,
        "error": vhdx_error,
    }
    return row, facts


def shutil_disk_free(root: Path) -> float:
    """目录所在盘剩余字节数（独立小函数便于测试注入临时目录）。"""
    import shutil

    return shutil.disk_usage(str(root)).free


def _last_alert_ts(audit_dir: Path) -> datetime | None:
    """上一条告警审计行的 ts（冷却判距；读不到=None）。"""
    try:
        path = audit_dir / ALERT_AUDIT_FILENAME
        if not path.exists():
            return None
        lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if not lines:
            return None
        return _parse_ts(json.loads(lines[-1]).get("ts"))
    except Exception:  # noqa: BLE001 — 审计读失败=无冷却依据（放行，宁多告不漏告）
        return None


def write_escalation(alert_dir: Path, audit_dir: Path, facts: dict, vhdx_path: Path) -> dict:
    """红线升级告警：workspace_alerts 告警件 + audit jsonl 行（双落点，失败不抛）。"""
    record = {
        "ts": facts["ts"],
        "by": "scripts.ops.vhdx_floor_watch",
        "event": "disk_floor_breach",
        "severity": "escalated",
        "d_free_gb": facts["d_free_gb"],
        "red_line_gb": facts["red_line_gib"],
        "vhdx_gb": facts["vhdx_gb"],
        "vhdx_path": str(vhdx_path),
        "note": "只采样+告警，零自动删停；处置=Owner 门位",
        "recover": (
            "python scripts/ops/cleanup_runtime_tmp_residue.py --execute; "
            "python scripts/session_worktree.py archive --all --execute（先 dry-run）"
        ),
    }
    out: dict = {"alert_file": None, "audit_line": False}
    stamp = facts["ts"][:19].replace(":", "").replace("-", "").replace("T", "_")
    try:
        alert_dir.mkdir(parents=True, exist_ok=True)
        path = alert_dir / f"vhdx_disk_floor_{stamp}.json"
        path.write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
        out["alert_file"] = str(path)
    except OSError:
        pass
    try:
        out["audit_line"] = append_audit_jsonl(Path(audit_dir), ALERT_AUDIT_FILENAME, record)
    except Exception:  # noqa: BLE001 — 告警审计失败不抛（workspace_alerts 件已兜底）
        pass
    return out


def sample_once(
    *,
    repo_root: Path | str | None = None,
    vhdx_path: Path | None = None,
    series_path: Path | None = None,
    alert_dir: Path | None = None,
    audit_dir: Path | None = None,
    min_interval_min: float = _DEFAULT_MIN_INTERVAL_MIN,
    alert_cooldown_min: float = _DEFAULT_ALERT_COOLDOWN_MIN,
    force: bool = False,
    dry_run: bool = False,
    note: str | None = None,
) -> dict:
    """一轮采样（默认入口）：节流→构造行→落序列→红线告警。永不抛。

    Returns:
        {action: sampled|throttled|error, below, row, alert, errors[]}
        action=error 时 exit 2；below=True 且已告警时调用方 exit 1（采样成功语义）。
    """
    root = Path(repo_root) if repo_root else _REPO_ROOT
    vhdx = Path(vhdx_path) if vhdx_path else DEFAULT_VHDX_PATH
    series = Path(series_path) if series_path else root / DEFAULT_SERIES_REL
    alerts = Path(alert_dir) if alert_dir else root / DEFAULT_ALERT_DIR_REL
    audits = Path(audit_dir) if audit_dir else root / DEFAULT_AUDIT_DIR_REL
    out: dict = {"action": "sampled", "below": False, "row": None, "alert": None, "errors": []}

    prev = _last_series_row(series)
    # 节流：距末行采样 < min_interval 分钟 → 跳过（序列自身即状态，零额外状态文件）
    if not force and prev is not None:
        last_ts = _parse_ts(prev.get("ts"))
        if last_ts is not None:
            gap_min = (now_utc() - last_ts).total_seconds() / 60.0
            if gap_min < min_interval_min:
                out["action"] = "throttled"
                out["last_ts"] = prev.get("ts")
                return out

    enabled, floor_gib = read_disk_floor_config(root)
    # 红线锚盘：vhdx 所在盘（结构层地板所在），vhdx 缺席回退项目根所在盘
    anchor = vhdx if vhdx.exists() else root
    row, facts = build_series_row(
        vhdx_path=vhdx,
        free_disk_root=anchor,
        red_line_gib=floor_gib,
        red_line_enabled=enabled,
        prev_row=prev,
        note=note,
    )
    out["row"] = row
    out["below"] = facts["below"]
    if facts["error"]:
        out["errors"].append(facts["error"])

    if dry_run:
        out["dry_run"] = True
        return out
    try:
        series.parent.mkdir(parents=True, exist_ok=True)
        with series.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError as e:
        out["action"] = "error"
        out["errors"].append(f"series_append_failed: {e}")
        return out

    if facts["below"]:
        last_alert = _last_alert_ts(audits)
        cooled = last_alert is not None and (now_utc() - last_alert).total_seconds() < alert_cooldown_min * 60
        if not cooled:
            out["alert"] = write_escalation(alerts, audits, facts, vhdx)
    return out


def _run_watch(interval_min: float) -> int:
    """常驻形态：Event.wait 可中断等待（非 raw sleep-loop）；signal 到位自动退出（四要素·自动关闭）。"""
    _PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    _PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
    stop = threading.Event()

    def _handler(signum, frame):  # noqa: ARG001 — signal 签名固定
        stop.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, _handler)
        except (ValueError, OSError):
            pass
    print(f"[VHDX-FLOOR] watch 启动 PID={os.getpid()} interval={interval_min:.0f}min（Ctrl+C 退出）", flush=True)
    exit_code = 0
    try:
        while not stop.is_set():
            r = sample_once(force=True, note="watch_tick")
            print(f"[VHDX-FLOOR] {r['action']} below={r['below']}", flush=True)
            if r["action"] == "error":
                exit_code = 2
            stop.wait(timeout=interval_min * 60)
    finally:
        _PID_FILE.unlink(missing_ok=True)
    return exit_code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="VHDX 增长采样 + D 盘红线告警（只采样+告警，零删停）")
    parser.add_argument(
        "--watch",
        nargs="?",
        const=60.0,
        default=None,
        type=float,
        metavar="MIN",
        help="常驻形态（默认 60min 一轮；须按文件头登记 reaper 白名单）",
    )
    parser.add_argument("--force", action="store_true", help="跳过节流立即采样")
    parser.add_argument("--dry-run", action="store_true", help="只算不写（零副作用）")
    parser.add_argument("--vhdx", dest="vhdx", default=None, help="覆盖 vhdx 路径")
    parser.add_argument("--series", dest="series", default=None, help="覆盖序列 jsonl 路径")
    parser.add_argument("--note", dest="note", default=None, help="本行备注（写入 ts 行 note 字段）")
    args = parser.parse_args(argv)

    if args.watch is not None:
        return _run_watch(args.watch)
    r = sample_once(
        vhdx_path=Path(args.vhdx) if args.vhdx else None,
        series_path=Path(args.series) if args.series else None,
        force=args.force,
        dry_run=args.dry_run,
        note=args.note,
    )
    if r["action"] == "error":
        print(f"[VHDX-FLOOR] 采样失败: {r['errors']}", file=sys.stderr)
        return 2
    if r["action"] == "throttled":
        print(f"[VHDX-FLOOR] 节流跳过（末行 {r.get('last_ts')}；--force 强制）")
        return 0
    row = r.get("row") or {}
    print(
        f"[VHDX-FLOOR] 采样: vhdx={row.get('vhdx_gb')}GiB d_free={row.get('d_free_gb')}GiB "
        f"红线={row.get('d_red_line_gb')}GiB below={row.get('d_below_red_line')}"
    )
    if r.get("alert"):
        print(f"[VHDX-FLOOR] 红线告警已升级: {r['alert'].get('alert_file')}")
    return 1 if r["below"] else 0


if __name__ == "__main__":
    sys.exit(main())
