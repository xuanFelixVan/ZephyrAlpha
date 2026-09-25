# [BLUEPRINT] MOD-QCURE-RECON | scripts/governance/scheduled_task_reconcile.py | §schtasks 三色对账
# [MODULE] scripts.governance.scheduled_task_reconcile
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] stdlib（subprocess/argparse/datetime/re）；zephyr.shared.io.paths.REPO_ROOT（SSOT canonical）
# [CONSUMERS] QMine 战役 M5 观测线（宿主任务挂靠待 Owner——并入既有日任务尾步，零新计划任务）；AI session 按需 CLI
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 全程只读：仅 Get-ScheduledTask/Get-ScheduledTaskInfo 查询面，绝不 Start/Enable/Disable/Register/Unregister 任何任务（查询串即真源，代码面零任务操控动词）；期望清单唯一真源=scripts/register_*.ps1 + scripts/backup/backup_daily_trigger.ps1 的任务名字面声明（grep 导出，零新登记册，净零 §4）；三色判定=绿(result=0 或 Running+267009)/黄(267008/267011 从未运行哨兵/267012/267014 超时被终止/Disabled/日触发节奏陈旧>2×周期)/红(其余非零 win32 退出码+声明有而系统无)；Daily 判定来自声明侧 New-ScheduledTaskTrigger -Daily 同文件声明；系统在册而声明侧无=漂移段单列（观测非红，含 Disabled one-shot 合法残留）；观测簿 §6 已知教训：DailyBackup 断 3 天型由「节奏陈旧」黄类捕获
# [MODIFY-GUARD] none（只读对账报表生成器；QMine M5 矿④，观测簿 §2 方案④）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PowerShell 不可用/查询失败→stderr 说明+exit 1（禁无系统面出全绿假表）；--out 写失败→exit 1；声明侧脚本缺失/解析零名→期望空清单如实呈现（不假红不假绿）
# [TESTS] tests/governance/test_scheduled_task_reconcile.py
# [A_module] module_id=QMINE-OBS-4 | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""scheduled_task_reconcile.py — Windows 计划任务三色对账生成器（QMine M5 矿④，全程只读）。

背景（观测簿 §1①/§6，2026-09-25 实测）：ZephyrAlpha* 任务 49 个在册，LastTaskResult
全仓零消费方（backfill_night.ps1:17 点名的"LastTaskResult 静默失败病"）——DailyBackup
267014 断 3 天型教训正在复发形态无人报。本件=只读生成器（红线 §9-5：生成器产出合法，
禁的是手工清单），期望清单从既有 register_*.ps1 真源 grep 导出，零新登记册。

用法（仓库根，Python 3.12）：
    python scripts/governance/scheduled_task_reconcile.py             # stdout
    python scripts/governance/scheduled_task_reconcile.py --out PATH  # 显式传参才落盘

三色：绿=result 0（或 Running+267009 运行中正常）｜黄=267011 从未运行哨兵/267014 超时
被终止/267008/267012/Disabled/日触发任务距上次运行超 2×周期｜红=其余非零退出码+声明有
而系统无。系统在册而声明侧无=漂移段单列（观测非红）。
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT  # noqa: PLC0415 — SSOT canonical（禁自建第二真源）

#: 只读查询命令——零任务操控动词（INVARIANTS 承重，修改须逐字复核）
_PS_QUERY = (
    "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8;"
    "$ErrorActionPreference='SilentlyContinue';"
    "$ts=@(Get-ScheduledTask -TaskName 'ZephyrAlpha*');"
    "foreach($t in $ts){"
    "$i=$t|Get-ScheduledTaskInfo;"
    "'{0}|{1}|{2}|{3}' -f $t.TaskName,$t.State,$i.LastTaskResult,$i.LastRunTime.ToString('yyyy-MM-dd HH:mm:ss')"
    "}"
)
_NAME_RE = re.compile(r"ZephyrAlpha[-_][A-Za-z0-9_]+")
_TASK_NAME_FIELD_RE = re.compile(r'(?:TaskName|-Name)\s*[= ]\s*"(?P<n>ZephyrAlpha[-_][A-Za-z0-9_]+)"')
#: 黄类 win32/sched 谜码（观测簿方案④；267009=Running 正常态归绿）
_YELLOW_RESULTS = {
    267008: "未计划运行（267008）",
    267011: "从未运行（267011 哨兵）",
    267012: "无更多计划运行（267012）",
    267014: "上次运行超时被终止（267014，DailyBackup 断 3 天型）",
}
_STALE_MULTIPLE_DAYS = 2  # 日触发节奏陈旧阈值=2×日周期（观测簿 §4 长尾：按 cadence 分档待 Owner）


def collect_system_tasks(runner=None) -> dict[str, dict]:
    """只读扫 ZephyrAlpha* 计划任务（Get-ScheduledTask 面）→ name → {state,result,last_run}。

    runner 注入位（测试 mock 用）；缺省=powershell 子进程。查询失败/输出零行 → RuntimeError
    （ERROR_CONTRACT：禁无系统面出全绿假表）。
    """
    if runner is None:

        def runner(cmd: list[str]) -> str:
            out = subprocess.run(cmd, capture_output=True, timeout=120, check=False)
            text = (
                out.stdout.decode("utf-8", errors="replace") if isinstance(out.stdout, bytes) else str(out.stdout or "")
            )
            err = (
                out.stderr.decode("utf-8", errors="replace") if isinstance(out.stderr, bytes) else str(out.stderr or "")
            )
            if out.returncode != 0 and not text.strip():
                raise RuntimeError(f"powershell 查询失败 rc={out.returncode}: {err[:200]}")
            return text

    text = runner(["powershell", "-NoProfile", "-NonInteractive", "-Command", _PS_QUERY])
    tasks: dict[str, dict] = {}
    for ln in text.splitlines():
        parts = ln.strip().split("|", 3)
        if len(parts) != 4 or not parts[0]:
            continue
        name, state, result_s, last_run = (p.strip() for p in parts)
        try:
            result = int(result_s)
        except ValueError:
            result = -1  # 谜码非整数（如空串）按未知非零处理 → 红，不静默吞
        tasks[name] = {"state": state, "result": result, "last_run": _parse_last_run(last_run)}
    if not tasks:
        raise RuntimeError("powershell 查询零行输出（系统面不可得，拒绝出全绿假表）")
    return tasks


def _parse_last_run(raw: str) -> datetime | None:
    """解析 LastRunTime（PS yyyy-MM-dd HH:mm:ss 本地时区）；空/坏/1999 哨兵年返回 None。"""
    try:
        ts = datetime.strptime(raw, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    if ts.year < 2000:  # 从未运行哨兵（1999-11-30 等）按"无运行史"处理
        return None
    return ts.astimezone()  # naive（PS 本地面）→ 本地 aware，与 now 同坐标系可相减


def export_expected_tasks(scripts_root: Path) -> dict[str, dict]:
    """期望清单导出（真源=register_*.ps1+backup_daily_trigger.ps1 的任务名字面声明，零新登记册）。

    只取非注释行（# 头注释里的 Verify/query 示例不算声明）；daily 标记只继承给「单任务文件
    且同文件声明 New-ScheduledTaskTrigger -Daily」——多任务文件触发器混杂（logon/daily 混编），
    按文件整体继承会造节奏陈旧假黄（保守不标，漏报可接受于假报，观测簿 §4 长尾：分档待 Owner）。
    """
    files = sorted(scripts_root.glob("register_*.ps1"))
    backup = scripts_root / "backup" / "backup_daily_trigger.ps1"
    if backup.is_file():
        files.append(backup)
    expected: dict[str, dict] = {}
    for f in files:
        if not f.is_file():
            continue
        body = [
            s
            for s in (ln.strip() for ln in f.read_text(encoding="utf-8", errors="replace").splitlines())
            if not s.startswith("#")
        ]
        text = "\n".join(body)
        names = {m.group("n") for m in _TASK_NAME_FIELD_RE.finditer(text)} | set(_NAME_RE.findall(text))
        inherit_daily = any("New-ScheduledTaskTrigger" in s and "-Daily" in s for s in body) and len(names) == 1
        for name in names:
            slot = expected.setdefault(name, {"daily": False, "sources": []})
            slot["daily"] = slot["daily"] or inherit_daily
            if f.name not in slot["sources"]:
                slot["sources"].append(f.name)
    return expected


def classify_task(entry: dict, *, state: str, result: int, last_run: datetime | None, now: datetime) -> tuple[str, str]:
    """三色判定单入口（present 任务；声明有而系统无的红在 build_report 单列）。

    优先级：Disabled → 黄类谜码 → 日触发节奏陈旧 → 绿（0 / Running+267009）→ 红其余非零。
    """
    if state == "Disabled":
        return "yellow", "Disabled（one-shot 残留/人为停用，观测项）"
    if result in _YELLOW_RESULTS:
        return "yellow", _YELLOW_RESULTS[result]
    if entry.get("daily") and last_run is not None and (now - last_run).total_seconds() > _STALE_MULTIPLE_DAYS * 86400:
        return "yellow", f"日触发节奏陈旧（距上次运行 >{_STALE_MULTIPLE_DAYS}×日周期，DailyBackup 断 3 天型捕获器）"
    if result == 0:
        return "green", "OK"
    if result == 267009 and state == "Running":
        return "green", "运行中（267009）"
    return "red", f"非零退出码 {result}"


def build_report(system: dict[str, dict], expected: dict[str, dict], *, now: datetime) -> dict:
    """对账聚合（纯函数面，I/O 收敛在 collect/export 两口）。"""
    rows: list[dict] = []
    for name, entry in sorted(expected.items()):
        if name in system:
            t = system[name]
            color, reason = classify_task(entry, state=t["state"], result=t["result"], last_run=t["last_run"], now=now)
            rows.append(
                {
                    "task": name,
                    "color": color,
                    "reason": reason,
                    "state": t["state"],
                    "result": t["result"],
                    "last_run": t["last_run"].strftime("%Y-%m-%d %H:%M") if t["last_run"] else "从未运行/哨兵",
                    "sources": entry["sources"],
                }
            )
        else:
            rows.append(
                {
                    "task": name,
                    "color": "red",
                    "reason": "声明有而系统无（register 脚本在、任务不在）",
                    "state": "-",
                    "result": "-",
                    "last_run": "-",
                    "sources": entry["sources"],
                }
            )
    order = {"red": 0, "yellow": 1, "green": 2}
    rows.sort(key=lambda r: (order[r["color"]], r["task"]))
    drift = sorted(n for n in system if n not in expected)
    counts = {c: sum(1 for r in rows if r["color"] == c) for c in ("green", "yellow", "red")}
    return {
        "generated_at": now.isoformat(timespec="seconds"),
        "declared": len(expected),
        "in_system": len(system),
        "counts": counts,
        "rows": rows,
        "drift": drift,
    }


def render_markdown(report: dict) -> str:
    """报表结构 → markdown 三色对账表。"""
    c = report["counts"]
    lines = [
        "# ZephyrAlpha 计划任务三色对账（schtasks reconcile）",
        "",
        f"- 生成时刻: {report['generated_at']}（scheduled_task_reconcile.py，全程只读，零任务操控）",
        f"- 面板: 声明侧 {report['declared']} 名（register_*.ps1+backup_daily_trigger.ps1 grep 导出，零新登记册）"
        f" × 系统侧 {report['in_system']} 个（Get-ScheduledTask ZephyrAlpha*）",
        f"- 判定: 🟢 绿 {c['green']} ｜ 🟡 黄 {c['yellow']} ｜ 🔴 红 {c['red']} ｜ 漂移（在册无声明）{len(report['drift'])}",
        "",
        "| 级别 | 任务 | State | LastTaskResult | LastRunTime | 判定依据 | 声明于 |",
        "|---|---|---|---:|---|---|---|",
    ]
    badge = {"green": "🟢", "yellow": "🟡", "red": "🔴"}
    for r in report["rows"]:
        lines.append(
            f"| {badge[r['color']]} {r['color']} | {r['task']} | {r['state']} | {r['result']} | {r['last_run']} "
            f"| {r['reason'].replace('|', chr(92) + '|')} | {', '.join(r['sources'])} |"
        )
    if report["drift"]:
        lines += ["", "## 漂移：系统在册而声明侧无（观测非红——Disabled one-shot 合法残留在此）", ""]
        sys_tasks = report.get("_system", {})
        for name in report["drift"]:
            st = sys_tasks.get(name, {}).get("state", "-")
            lines.append(f"- {name}（State={st}）")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Windows 计划任务三色对账（只读；缺省输出 stdout）")
    parser.add_argument("--out", type=Path, default=None, help="输出文件路径（缺省 stdout）")
    args = parser.parse_args(argv)
    now = datetime.now().astimezone()
    try:
        system = collect_system_tasks()
    except (RuntimeError, OSError) as exc:
        print(f"[task-reconcile] 系统面查询失败: {exc}", file=sys.stderr)
        return 1
    report = build_report(system, export_expected_tasks(REPO_ROOT / "scripts"), now=now)
    report["_system"] = system  # 漂移段 State 呈现用（渲染后即弃，非落盘字段）
    text = render_markdown(report)
    if args.out is None:
        sys.stdout.write(text)
        return 0
    try:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")  # 报表产物非热文件（非注册表/宪法/tracker 面）
        if args.out.read_text(encoding="utf-8") != text:  # 写后读回核实（宪法 §1-13 同精神）
            print("[task-reconcile] 写回核验不一致", file=sys.stderr)
            return 1
    except OSError as exc:
        print(f"[task-reconcile] 输出写失败: {exc}", file=sys.stderr)
        return 1
    print(f"[task-reconcile] 已写出: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
