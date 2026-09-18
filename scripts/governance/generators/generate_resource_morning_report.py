# [BLUEPRINT] MOD-RESCHED-MORNING | docs/03_modules/_cross_layer/resource_morning_report/blueprint.md | §
# [MODULE] scripts.governance.generators.generate_resource_morning_report
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] yaml; croniter(经闸 expand_windows 间接); zephyr.shared.io.file_utils;
#   zephyr.gov_enforcement.commit_gates.resource_schedule_gate（run_pool_concurrency_audit，
#   **只 import 只读调用**，同刻冲突账判据真源在闸不在本脚本）;
#   zephyr.infrastructure.system_telemetry.resource_sampler（IncubationLedger 台账只读口）;
#   zephyr.infrastructure.system_telemetry.alerts.ops_alert_feed（通知板唯一读口）;
#   zephyr.infrastructure.system_telemetry.measure_calibration（校准报告读口）
# [CONSUMERS] 晨审 Owner/AI 会话（读 docs/_working/resource_schedule/morning_report/latest.md）;
#   tests/scripts/test_generate_resource_morning_report.py
# [STARTUP] manual（L-9 晨报=每日人工/AI 晨审入口，非再生流水线成员；无 cron 自拉起）
# [MATURITY] testing
# [INVARIANTS] 零新数据源——只吃注册表 + 孵化台账 + 样本流 + 通知板 + 闸的同池并发账，
#   不新增探针、不查 DB、不写任何生产路径;
#   全部判据复用：冲突=run_pool_concurrency_audit（本脚本零二次判定）、校准=读 calibration_report
#   （缺席即如实写"未生成"，禁臆造摘要）;
#   时钟可注入（build_report(now=…)/--now ISO）——缺省 datetime.now(UTC)；窗档时间语义=北京
#   wall time（注册表 window_expr 口径，与闸 expand_windows 同源）;
#   输出 markdown 到 docs/_working/resource_schedule/（_working 契约禁 .json）；路径可注入
#   （测试隔离禁写生产 web/.runtime 树）；CAS safe_write_text 写;
#   只读侧：注册表/台账/样本流/通知板一律零写入
# [MODIFY-GUARD] 段落增删须同步 tests/scripts/test_generate_resource_morning_report.py 的锚点断言
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 注册表缺失=FileNotFoundError 上抛；台账/样本/通知板/校准报告缺席=对应段
#   "无数据"降级不抛（晨报缺一块不等于开不出来）
# [TESTS] tests/scripts/test_generate_resource_morning_report.py
# [A_module] module_id=MOD-RESCHED-MORNING | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""generate_resource_morning_report — L-9 资源晨报生成器（MOD-RESCHED-MORNING，P5）。

v2 方案 §3 L-9：把"每天早上谁该关心什么"从五个分散真源拼成一页 markdown——
排班时间线（今天几点开什么工）、同刻冲突（第四查账上还有几笔没清零）、校准 flag
（申报值与实测偏差>30% 的实体）、告警板未决（通知线欠着的账）、再生新鲜度（画像还是
不是昨天的）。

零新数据源是硬约束：五段全部走现成读口（闸/采样器/告警板/校准报告），本脚本只做
拼装与渲染，任何判定都不在这里重写第二份（判据重写=两套口径，v2 战役 C-8 的教训）。

用法:
  python scripts/governance/generators/generate_resource_morning_report.py
  python scripts/governance/generators/generate_resource_morning_report.py --root <tmp> --now 2026-09-22T00:30:00+08:00
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Final

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from zephyr.shared.io.file_utils import content_sha256, safe_write_text  # noqa: E402

logger = logging.getLogger(__name__)

DEFAULT_REGISTRY_RELPATH: Final = Path("config/resource_profile_registry.yaml")
DEFAULT_SAMPLES_RELPATH: Final = Path(".runtime/logs/resource_samples")
DEFAULT_LEDGER_RELPATH: Final = Path(".runtime/process_incubator/ledger.jsonl")
DEFAULT_BOARD_RELPATH: Final = Path(".runtime/ops_notifications")
DEFAULT_CALIBRATION_RELPATH: Final = Path("docs/_working/resource_schedule/calibration_report.yaml")
DEFAULT_OUTPUT_RELPATH: Final = Path("docs/_working/resource_schedule/morning_report/latest.md")

# 同刻冲突/校准 flag 的展示上限（晨报是索引不是全量账，全量在真源文件里）
MAX_LIST_ROWS: Final = 12
# 今日窗档地平线=1 天（"当前同刻"的语义边界：只数今天的账，28 天存量债归闸自己）
TODAY_HORIZON_DAYS: Final = 1
# 闸 expand_windows 单表达式触发步数上限（闸内是字面量、无常量可 import，本批闸文件只读）。
# 只用于"末窗被截断"的脚注判定：两边万一不齐→脚注不显示，晨报数字本身不会错。
_EXPAND_STEP_CAP: Final = 64


def _tz():
    """北京 wall time 时区（注册表 window_expr 语义口径，与闸 expand_windows 同源）。"""
    from zoneinfo import ZoneInfo

    return ZoneInfo("Asia/Shanghai")


def _day_start(now: datetime) -> datetime:
    """今日 00:00（北京语义）。"""
    return now.astimezone(_tz()).replace(hour=0, minute=0, second=0, microsecond=0)


def _hhmm(dt: datetime) -> str:
    """_hhmm implementation."""
    return dt.astimezone(_tz()).strftime("%H:%M")


# ── 段① 今日排班时间线 ──

def build_timeline(entities: list[dict], now: datetime) -> dict[str, Any]:
    """今日窗档展开并按起始时刻排序（复用闸 expand_windows，零二次 cron 实现）。"""
    from zephyr.gov_enforcement.commit_gates.resource_schedule_gate import expand_windows

    day0 = _day_start(now)
    day_end = day0 + timedelta(days=1)
    rows: list[dict[str, Any]] = []
    quiet: list[dict[str, Any]] = []
    for e in entities:
        tid = str(e.get("task_id") or "")
        status = str(e.get("status") or "active")
        if not tid or status in ("retired", "orphaned_source"):
            continue
        measured = e.get("measured") if isinstance(e.get("measured"), dict) else {}
        base = {
            "task_id": tid,
            "pool": e.get("pool"),
            "status": status,
            "est_duration_min": e.get("est_duration_min"),
            "peak_mem_gb": e.get("peak_mem_gb"),
            "measured_p90_duration_min": measured.get("p90_duration_min"),
            "measured_peak_mem_gb": measured.get("peak_mem_gb"),
            "exclusive_group": list(e.get("exclusive_group") or []),
            "trading_sensitive": bool(e.get("trading_sensitive")),
        }
        try:
            wins = expand_windows(e.get("window_expr"), e.get("est_duration_min"), day0,
                                  horizon_days=TODAY_HORIZON_DAYS)
        except Exception as exc:  # noqa: BLE001 — 坏 cron 实体可见地降级为"未排产"，不静默吞
            logger.warning("morning_report: %s 窗档解析失败：%s", tid, exc)
            quiet.append({**base, "reason_zh": f"窗档解析失败：{str(exc)[:60]}"})
            continue
        today = [(s, t) for (s, t) in wins if day0 <= s < day_end]
        if not today:
            quiet.append({**base, "reason_zh": "今日无窗（常驻/手动/非今日班次）"})
            continue
        rows.append(_aggregate_day(base, today))
    rows.sort(key=lambda r: (r["start"], r["task_id"]))
    return {"fires": rows, "total_fires": sum(r["fires"] for r in rows),
            "quiet": quiet, "quiet_total": len(quiet), "date": day0.strftime("%Y-%m-%d")}


def _aggregate_day(base: dict[str, Any], today: list[tuple[datetime, datetime]]) -> dict[str, Any]:
    """同一实体本日多窗 → 一行（首窗起、末窗止、次数）。

    高频槽位（data_slot_event_driven */3）逐窗出行会让晨报变成 300 行噪音，
    而"谁几点到几点在跑"才是晨审要的信息；逐窗明细真源在周历视图不在这里。
    """
    return {**base, "start": min(s for (s, _t) in today), "end": max(t for (_s, t) in today),
            "fires": len(today)}


# ── 段② 同刻冲突（闸第四查，只读） ──

def build_conflicts(registry_path: Path, now: datetime) -> dict[str, Any]:
    """run_pool_concurrency_audit → 计数与明细（判据在闸，本函数零二次判定）。"""
    from zephyr.gov_enforcement.commit_gates.resource_schedule_gate import run_pool_concurrency_audit

    findings = run_pool_concurrency_audit(registry_path, now, horizon_days=TODAY_HORIZON_DAYS)
    items = [{
        "reason_code": f.reason_code,
        "severity": f.severity,
        "task_ids": list(f.task_ids),
        "detail": f.detail,
        "at": f.at,
        "kind": str((f.extra or {}).get("kind") or ""),
    } for f in findings]
    waived = sum(int((f.extra or {}).get("waived_pair_count") or 0) for f in findings)
    return {
        "total": len(items),
        "block": sum(1 for i in items if i["severity"] == "block"),
        "warn": sum(1 for i in items if i["severity"] == "warn"),
        "waived_pairs": waived,
        "items": items,
        "horizon_days": TODAY_HORIZON_DAYS,
    }


# ── 段③ 校准 flag 摘要 ──

def build_calibration_summary(calibration_path: Path) -> dict[str, Any]:
    """读校准报告摘要段；缺席=如实"未生成"（禁臆造 flag 数）。"""
    from zephyr.infrastructure.system_telemetry.measure_calibration import read_calibration_report

    report = read_calibration_report(calibration_path)
    if not report:
        return {"present": False, "path": str(calibration_path)}
    totals = report.get("totals") or {}
    return {
        "present": True,
        "path": str(calibration_path),
        "generated_at": report.get("generated_at"),
        "tolerance_pct": report.get("tolerance_pct"),
        "totals": totals,
        "低估": totals.get("低估", 0),
        "高估": totals.get("高估", 0),
        "corrections": list(report.get("proposed_corrections") or []),
    }


# ── 段④ 告警板未决 ──

def build_alert_summary(board_dir: Path, now: datetime) -> dict[str, Any]:
    """通知板活动条目（经 OpsAlertFeed 现成读口，本脚本不碰板写入）。"""
    from zephyr.infrastructure.system_telemetry.alerts.ops_alert_feed import OpsAlertFeed

    entries = OpsAlertFeed(board_dir=board_dir).list_active(now=now.timestamp())
    pending = [e for e in entries if not e.get("resolved_at")]
    items = [{
        "severity": str(e.get("severity") or ""),
        "key": str(e.get("key") or ""),
        "title": str(e.get("title") or ""),
        "message": str(e.get("message") or "")[:160],
        "module_id": str(e.get("module_id") or ""),
        "count": int(e.get("count") or 1),
        "first_seen": datetime.fromtimestamp(float(e.get("first_seen") or 0), tz=timezone.utc),
    } for e in pending]
    items.sort(key=lambda i: (i["severity"] != "critical", -i["first_seen"].timestamp()))
    return {"total": len(pending), "resolved_recent": len(entries) - len(pending),
            "critical": sum(1 for i in items if i["severity"] == "critical"),
            "warning": sum(1 for i in items if i["severity"] == "warning"),
            "items": items}


# ── 段⑤ 再生新鲜度 ──

def build_freshness(registry_path: Path, entities: list[dict], header: dict,
                    samples_dir: Path, ledger_path: Path, now: datetime) -> dict[str, Any]:
    """画像/样本/台账三根链条各自的新旧度（缺一根=排班在对旧账做工）。"""
    from zephyr.infrastructure.system_telemetry.resource_sampler import IncubationLedger

    raw_gen = str(header.get("generated_at") or "")
    age_h = None
    try:
        gen = datetime.fromisoformat(raw_gen.replace("Z", "+00:00"))
        if gen.tzinfo is None:
            gen = gen.replace(tzinfo=timezone.utc)
        age_h = round((now - gen).total_seconds() / 3600.0, 1)
    except ValueError:
        pass
    latest_sample = _latest_sample_mtime(samples_dir, now)
    ledger = IncubationLedger.load(ledger_path)
    live = sum(1 for r in ledger.records if r.exited_at is None)
    declared_total = header.get("total_entities")
    return {
        "registry_generated_at": raw_gen or "未声明",
        "registry_age_hours": age_h,
        "total_entities_declared": declared_total,
        "total_entities_actual": len(entities),
        "entity_count_consistent": (declared_total is None or int(declared_total) == len(entities)),
        "latest_sample_at": latest_sample[0] if latest_sample else "无样本流文件",
        "latest_sample_age_hours": latest_sample[1] if latest_sample else None,
        "ledger_records": len(ledger),
        "ledger_live": live,
        "ledger_bad_lines": ledger.bad_lines,
    }


def _latest_sample_mtime(samples_dir: Path, now: datetime) -> tuple[str, float] | None:
    """样本目录最新文件 mtime（采样是否还活着的最廉价证据；目录缺失=None）。"""
    d = Path(samples_dir)
    if not d.is_dir():
        return None
    newest = None
    for f in d.glob("*.jsonl"):
        try:
            m = f.stat().st_mtime
        except OSError:
            continue
        if newest is None or m > newest:
            newest = m
    if newest is None:
        return None
    dt = datetime.fromtimestamp(newest, tz=timezone.utc)
    return (dt.isoformat(timespec="seconds"), round((now - dt).total_seconds() / 3600.0, 1))


# ── 组装 + 渲染 ──

def build_report(
    registry_path: str | Path | None = None,
    samples_dir: str | Path | None = None,
    ledger_path: str | Path | None = None,
    board_dir: str | Path | None = None,
    calibration_path: str | Path | None = None,
    now: datetime | None = None,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """五段拼装（纯读，返回可渲染 dict；时钟与全部路径可注入）。"""
    n = now or datetime.now(timezone.utc)
    root_p = Path(root) if root else REPO_ROOT
    reg = Path(registry_path) if registry_path else root_p / DEFAULT_REGISTRY_RELPATH
    sdir = Path(samples_dir) if samples_dir else root_p / DEFAULT_SAMPLES_RELPATH
    led = Path(ledger_path) if ledger_path else root_p / DEFAULT_LEDGER_RELPATH
    board = Path(board_dir) if board_dir else root_p / DEFAULT_BOARD_RELPATH
    calib = Path(calibration_path) if calibration_path else root_p / DEFAULT_CALIBRATION_RELPATH

    data = yaml.safe_load(Path(reg).read_text(encoding="utf-8")) or {}
    entities = list(data.get("entities") or [])
    sections = {
        "timeline": build_timeline(entities, n),
        "conflicts": build_conflicts(Path(reg), n),
        "calibration": build_calibration_summary(calib),
        "alerts": build_alert_summary(board, n),
        "freshness": build_freshness(Path(reg), entities, data, sdir, led, n),
    }
    return {
        "generated_at": n.astimezone(timezone.utc).isoformat(timespec="seconds"),
        "local_date": sections["timeline"]["date"],
        "generator": "scripts/governance/generators/generate_resource_morning_report.py",
        "sources_zh": ["注册表", "孵化台账", "样本流", "通知板", "闸同池并发账（只读）"],
        "registry": str(reg),
        **sections,
    }


def _table_header(cols: list[str]) -> list[str]:
    """_table_header implementation."""
    return ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]


def render_markdown(rep: dict[str, Any]) -> str:
    """报告 dict → markdown（五段固定锚点，晨审按段跳读）。"""
    lines: list[str] = [
        "---",
        "ttl: task_bound",
        "status: active",
        f"generated_at: '{rep['generated_at']}'",
        "---",
        "",
        f"# 资源晨报（L-9） — {rep['local_date']}（Asia/Shanghai）",
        "",
        f"> 生成：{rep['generated_at']} · {rep['generator']}",
        f"> 数据源：{'、'.join(rep['sources_zh'])}（零新数据源，判据全在真源侧）",
        "",
    ]
    lines += _render_timeline(rep["timeline"])
    lines += _render_conflicts(rep["conflicts"])
    lines += _render_calibration(rep["calibration"])
    lines += _render_alerts(rep["alerts"])
    lines += _render_freshness(rep["freshness"])
    return "\n".join(lines) + "\n"


def _render_timeline(tl: dict[str, Any]) -> list[str]:
    """_render_timeline implementation."""
    out = [f"## 1. 今日排班时间线（按窗起点排序，{len(tl['fires'])} 个实体开工 / "
           f"{tl['total_fires']} 个开工窗）", ""]
    if not tl["fires"]:
        out += ["> 今日无可展开窗档（全为常驻/手动/非本日班次）。", ""]
    else:
        out += _table_header(["首窗", "末窗止", "次数", "task_id", "池", "申报时长(min)",
                              "实测P90(min)", "申报内存(GB)", "状态"])
        for r in tl["fires"]:
            out.append("| {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
                _hhmm(r["start"]), _hhmm(r["end"]), r["fires"], r["task_id"], r["pool"] or "-",
                r["est_duration_min"] if r["est_duration_min"] is not None else "-",
                r["measured_p90_duration_min"] if r["measured_p90_duration_min"] is not None else "-",
                r["peak_mem_gb"] if r["peak_mem_gb"] is not None else "-", r["status"]))
        out.append("")
    quiet_ids = [q["task_id"] for q in tl["quiet"]]
    if any(r["fires"] >= _EXPAND_STEP_CAP for r in tl["fires"]):
        out += [f"> 注：标 {_EXPAND_STEP_CAP} 次的行被闸 `expand_windows` 单表达式 64 步上限截断，"
                "末窗非本日真末窗（逐窗明细真源=周历视图，晨报名下不抄第二份）。", ""]
    shown = "、".join(quiet_ids[:MAX_LIST_ROWS]) or "（无）"
    out += [f"未排产/常驻实体 {tl['quiet_total']} 个（不计入今日冲突账，planned 走 R-D 裁定）：",
            "", "> " + shown + (f"…余 {len(quiet_ids) - MAX_LIST_ROWS} 个见注册表"
                                if len(quiet_ids) > MAX_LIST_ROWS else ""), ""]
    return out


def _render_conflicts(cf: dict[str, Any]) -> list[str]:
    """_render_conflicts implementation."""
    out = [f"## 2. 当前同刻冲突（第四查 sched_pool_concurrency，地平线 {cf['horizon_days']} 天）", "",
           f"- 待清零（block）：**{cf['block']}**", f"- 留痕（warn）：{cf['warn']}",
           f"- co_start_intent 豁免对（裁定 R-F，不计冲突）：{cf['waived_pairs']}", ""]
    for f in cf["items"][:MAX_LIST_ROWS]:
        tids = "+".join(f["task_ids"])
        out.append(f"- `[{f['severity']}] {f['reason_code']}` **{tids}** — {f['detail']}"
                   + (f"（{f['at']}）" if f["at"] else ""))
    if cf["total"] > MAX_LIST_ROWS:
        out.append(f"- …余 {cf['total'] - MAX_LIST_ROWS} 条见闸复跑（全量账不在晨报里抄一遍）")
    out.append("")
    return out


def _render_calibration(cal: dict[str, Any]) -> list[str]:
    """_render_calibration implementation."""
    out = ["## 3. 校准 flag 摘要（申报 vs 实测偏差 >阈值）", ""]
    if not cal.get("present"):
        out += [f"> 校准报告未生成（{cal.get('path')}）——跑 "
                "`python -m zephyr.infrastructure.system_telemetry.measure_calibration`。", ""]
        return out
    t = cal.get("totals") or {}
    out += [f"- 报告生成：{cal.get('generated_at')} · 阈值 {cal.get('tolerance_pct')}%",
            f"- flag 字段数：{t.get('flagged_fields')}（实体 {t.get('flagged_entities')}）"
            f"｜低估 {cal.get('低估')}｜高估 {cal.get('高估')}"
            f"｜样本不足 {t.get('insufficient_samples')}", ""]
    corrections = cal.get("corrections") or []
    if not corrections:
        out += ["> 本轮无超阈值偏差——申报值与实测一致（在容差内）。", ""]
        return out
    out += _table_header(["task_id", "字段", "申报", "实测", "偏差", "方向", "建议"])
    for c in corrections[:MAX_LIST_ROWS]:
        ratio = c.get("deviation_ratio")
        out.append("| {} | {} | {} | {} | {}% | {} | {} |".format(
            c.get("task_id"), c.get("field"), c.get("declared"), c.get("measured_p90"),
            round(float(ratio) * 100, 1) if ratio is not None else "-",
            c.get("direction") or "-", str(c.get("verdict") or "")[:40]))
    if len(corrections) > MAX_LIST_ROWS:
        out.append(f"\n> 余 {len(corrections) - MAX_LIST_ROWS} 条见报告文件（全量不抄）。")
    out += ["", "> 校正批须经人在环改申报值：measured.* 写权归采样器 writeback，校准器只出报告。", ""]
    return out


def _render_alerts(al: dict[str, Any]) -> list[str]:
    """_render_alerts implementation."""
    out = [f"## 4. 告警板未决条目（共 {al['total']}：critical {al['critical']} / "
           f"warning {al['warning']}；近期已解除灰显 {al['resolved_recent']}）", ""]
    if not al["items"]:
        out += ["> 板面干净（无未决通知）。", ""]
        return out
    for a in al["items"][:MAX_LIST_ROWS]:
        out.append(f"- **[{a['severity']}]** {a['title']}（`{a['key']}`，×{a['count']}，"
                   f"首发 {a['first_seen'].isoformat(timespec='seconds')}）{a['message']}")
    if al["total"] > MAX_LIST_ROWS:
        out.append(f"- …余 {al['total'] - MAX_LIST_ROWS} 条见 `GET /api/ops-notifications`")
    out.append("")
    return out


def _render_freshness(fr: dict[str, Any]) -> list[str]:
    """_render_freshness implementation."""
    ok = "一致" if fr["entity_count_consistent"] else "**不一致（计数漂移，须再生）**"
    out = ["## 5. 再生新鲜度", "",
           f"- 注册表再生时刻：{fr['registry_generated_at']}（距今 {fr['registry_age_hours']} 小时）",
           f"- total_entities 声明 {fr['total_entities_declared']} vs 实盘 "
           f"{fr['total_entities_actual']}：{ok}",
           f"- 样本流最近落盘：{fr['latest_sample_at']}"
           + (f"（距今 {fr['latest_sample_age_hours']} 小时）" if fr["latest_sample_age_hours"] is not None else ""),
           f"- 孵化台账：{fr['ledger_records']} 条（存活 {fr['ledger_live']}，坏行 {fr['ledger_bad_lines']}）",
           ""]
    if fr["registry_age_hours"] is None:
        out.append("> 注册表无 generated_at 或格式异常——再生链路身份不明，晨审先查生成器。")
    return out


def write_markdown(text: str, output: str | Path) -> Path:
    """CAS 落盘 markdown（docs/_working 契约：只出 .md，禁 .json）。"""
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    expected = content_sha256(out.read_text(encoding="utf-8")) if out.exists() else None
    safe_write_text(out, text, expected_base_sha256=expected)
    return out


def main(argv: list[str] | None = None) -> int:
    """CLI：--root/各路径/--now 全注入（测试与 E2E 主通道）。"""
    ap = argparse.ArgumentParser(description="L-9 资源晨报生成器（MOD-RESCHED-MORNING，零新数据源）")
    ap.add_argument("--root", default="", help="仓根注入（缺省真实仓根）")
    ap.add_argument("--registry", default="", help="注册表路径覆盖")
    ap.add_argument("--samples-dir", default="", help="样本流目录覆盖")
    ap.add_argument("--ledger", default="", help="孵化台账路径覆盖")
    ap.add_argument("--board-dir", default="", help="通知板目录覆盖")
    ap.add_argument("--calibration", default="", help="校准报告路径覆盖")
    ap.add_argument("--output", default="", help=f"输出 md（缺省 {DEFAULT_OUTPUT_RELPATH}）")
    ap.add_argument("--now", default="", help="ISO 时刻注入（缺省 datetime.now(UTC)）")
    ap.add_argument("--print-md", action="store_true", help="同时把 markdown 打到 stdout")
    args = ap.parse_args(argv)

    n: datetime | None = None
    if args.now:
        n = datetime.fromisoformat(args.now)
        if n.tzinfo is None:  # 裸时刻按北京 wall time 解释（window_expr 同口径，禁当 UTC 用）
            n = n.replace(tzinfo=_tz())
    root = args.root or None
    rep = build_report(
        registry_path=args.registry or None, samples_dir=args.samples_dir or None,
        ledger_path=args.ledger or None, board_dir=args.board_dir or None,
        calibration_path=args.calibration or None, now=n, root=root)
    md = render_markdown(rep)
    out = write_markdown(md, args.output or (Path(root or REPO_ROOT) / DEFAULT_OUTPUT_RELPATH))
    if args.print_md:
        print(md)
    cf, al, cal = rep["conflicts"], rep["alerts"], rep["calibration"]
    print(json.dumps({
        "ok": True, "output": str(out), "local_date": rep["local_date"],
        "today_fires": rep["timeline"]["total_fires"], "quiet_total": rep["timeline"]["quiet_total"],
        "conflicts_block": cf["block"], "conflicts_warn": cf["warn"],
        "alerts_pending": al["total"], "calibration_present": cal.get("present"),
        "registry_age_hours": rep["freshness"]["registry_age_hours"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
