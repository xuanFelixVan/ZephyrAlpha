#!/usr/bin/env python
# [BLUEPRINT] MOD-OPS_SCHED_OVERVIEW | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §schedule-overview
# [MODULE] scripts.ops.schedule_overview
# [DOMAIN] D_DATA
# [DEPENDENCIES] yaml; zephyr.governance.audit.schedule_consistency_reconciler（三表核对核心同源）;
#   zephyr.gov_enforcement.commit_gates.resource_schedule_gate（expand_windows cron 展开——零二次 cron 实现）;
#   zephyr.governance.audit.reconciliation_registry（ReconciliationRegistry——reconciler status 查询）
# [CONSUMERS] AI 冷启动排班总览（W4-4 一条命令出三表总览）; docs/_working/resource_schedule/ 战役件
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 排班三表物理不合并（Owner 裁定）：本 CLI 是读侧总览唯一入口，禁写三表真源;
#   周历视图=槽位×任务映射（schedule.yaml 槽位语义 + tasks.yaml 任务挂载 + registry 资源档位三表投影）;
#   cron 展开复用闸 expand_windows（单实现真源，禁克隆）; 输出默认 stdout 只读，
#   唯一写面=.runtime 报告（--publish-report，fix-in-place 同源）;
#   --selftest 注入纯内存态（deepcopy），绝不落盘污染真源
# [MODIFY-GUARD] 三段总览结构（week/resource/consistency）变更须同步 rw-engine.js 渲染契约评估
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 表缺失/解析失败 → 一致性段 sched_x_table_error warn 呈现，CLI 不崩;
#   exit 语义：0=无 block；1=有 block（--fail-on warn 时 warn 也算）；2=用法/自检失败
# [TESTS] tests/scripts/test_schedule_overview.py
# [A_module] module_id=MOD-OPS_SCHED_OVERVIEW | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: AI 会话按需调用的 permanent CLI runner（排班三表总览/一致性自检/reconciler status 查询，非 cron/非 daemon/非常驻服务），由会话显式触发；自动维护面由 GATE-SCHEDULE-CONSISTENCY reconciler（post-commit 事件触发）承担
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 排班三表
#   fields: config/resource_profile_registry.yaml + src/zephyr/data/config/tasks.yaml + src/zephyr/data/config/schedule.yaml（路径可注入，物理不合并）
#   code: load_three_tables（核对核心同源）
# 层: 算法
# - id: A1
#   name_zh: ① 周历视图（槽位×任务映射）
#   name_en: build_week_section
#   intro: 槽位档案（cron/executor/worker 数）+任务挂载清单+资源档位，expand_windows 展开本周触发时刻表
#   desc: 三表 join 键=槽位名（tasks.schedule / registry.data_slot_<slot>）
# - id: A2
#   name_zh: ② 资源档位总览
#   name_en: build_resource_section
#   intro: 泳道词表/worker 配额/内存天花板/实体分布/互斥组/实测覆盖率
#   desc: 全部取自 registry 头部字段（pool_vocabulary/groups/mem_ceiling_gb），零硬编码词表
# - id: A3
#   name_zh: ③ 三表一致性检查
#   name_en: run_schedule_consistency
#   intro: 槽位存在性/资源引用有效性/时段冲突（闸同源直通）——检测不自动改
#   desc: check_tables 核心（--selftest 内存注入假引用验红/还原验绿）
# 层: 输出
# - id: O1
#   name_zh: 三段总览（text/--json）
#   name_en: overview output
#   intro: stdout 只读；--publish-report 落 .runtime/schedule_consistency/last_result.json
#   downstream: AI 冷启动 / reconciler 报告同源
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I1 --> A3
# A1 --> O1
# A2 --> O1
# A3 --> O1
"""schedule_overview — 排班三表统一总览入口（W4-4：三表一入口，物理表不合并）。

三张物理表 → 一个逻辑系统 → 一条命令：

  python scripts/ops/schedule_overview.py                    # 三段总览（周历/资源档位/一致性）
  python scripts/ops/schedule_overview.py --section week     # 只看周历视图（槽位×任务映射）
  python scripts/ops/schedule_overview.py --json             # 机生输出（供上游消费）
  python scripts/ops/schedule_overview.py --selftest         # 一致性检查红/绿自证（内存注入）
  python scripts/ops/schedule_overview.py --reconciler-status  # reconciler 注册/执行 status

设计依据：Owner 裁定——tasks.yaml+schedule.yaml 本就一体（任务引用槽位主从系统），
resource_profile_registry 独立维度；不合并物理表，读侧统一入口 + 一致性 reconciler。
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

import yaml  # noqa: E402

from zephyr.governance.audit.schedule_consistency_reconciler import (  # noqa: E402
    GATE_ID,
    RELPATH_REGISTRY,
    RELPATH_SCHEDULE,
    RELPATH_TASKS,
    REPORT_RELPATH,
    SELFTEST_TAG,
    check_tables,
    describe,
    load_three_tables,
    query_recent_executions,
    run_schedule_consistency,
    write_report,
)
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  # SSOT 路径常量（禁本地重定义）

_DOW_ZH = "一二三四五六日"


def _week_start_sh(now: datetime) -> datetime:
    """本周一 00:00（Asia/Shanghai 口径，与周历视图生成器同语义）。"""
    tz = ZoneInfo("Asia/Shanghai")
    n = now.astimezone(tz)
    return (n - timedelta(days=n.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)


def _slot_week_firings(cron: str, week_start: datetime, normalized_expr: str | None = None) -> dict[int, list[str]]:
    """槽位 cron → 本周 {dow: ["HH:MM", ...]}（复用闸 expand_windows，零二次 cron 实现）。

    normalized_expr：registry 实体的 window_expr（生成器已把 schedule.yaml 的 APScheduler
    dow 0=周一 归一为 croniter 0=周日口径——优先用它，防 dow 约定错位：APScheduler
    ``0-4``=周一~五，croniter 直解会错显成周日~四）。缺席才退回原始 cron。
    """
    from zephyr.gov_enforcement.commit_gates.resource_schedule_gate import expand_windows

    expr = str(normalized_expr or cron or "")
    out: dict[int, list[str]] = {}
    try:
        wins = expand_windows(expr, 1, week_start, horizon_days=8)
    except Exception:  # noqa: BLE001 — 坏 cron 槽位呈 "(unparsable)" 不崩总览
        return {d: ["(unparsable)"] for d in range(7)}
    week_end = week_start + timedelta(days=7)
    for s, _e in wins:
        if s < week_start or s >= week_end:
            continue
        out.setdefault(s.weekday(), []).append(s.strftime("%H:%M"))
    for d in out:
        out[d] = sorted(set(out[d]))
    return out


def _slot_entry(
    name: str,
    spec: dict,
    prof: dict,
    tasks_for_slot: list[str],
    workers: dict,
    week_start: datetime,
) -> dict:
    """单槽位周历条目（档案+任务挂载+资源档位+本周触发时刻）。"""
    pool = prof.get("pool") or spec.get("executor")
    return {
        "slot": name,
        "cron": spec.get("cron"),
        "executor": spec.get("executor"),
        "workers": workers.get(str(pool)),
        "description": str(spec.get("description") or "")[:60],
        "task_count": len(tasks_for_slot),
        "tasks": tasks_for_slot,
        "profile": {
            "task_id": prof.get("task_id"),
            "resource_class": prof.get("resource_class"),
            "pool": prof.get("pool"),
            "peak_mem_gb": prof.get("peak_mem_gb"),
            "est_duration_min": prof.get("est_duration_min"),
            "exclusive_group": list(prof.get("exclusive_group") or []),
            "trading_sensitive": prof.get("trading_sensitive"),
            "status": prof.get("status"),
        },
        "week_firings": _slot_week_firings(str(spec.get("cron") or ""), week_start, prof.get("window_expr")),
    }


def build_week_section(tables: dict, week_start: datetime) -> dict:
    """① 周历视图数据（槽位×任务映射×资源档位三表投影）。"""
    schedules: dict = tables["schedule"]
    tasks: list[dict] = tables["tasks"]
    registry: dict = tables["registry"]
    entities: list[dict] = list(registry.get("entities") or [])
    workers: dict = ((registry.get("pool_vocabulary") or {}).get("workers")) or {}

    profile_by_slot: dict[str, dict] = {}
    for e in entities:
        eid = str(e.get("task_id") or "")
        if eid.startswith("data_slot_"):
            profile_by_slot[eid[len("data_slot_") :]] = e

    tasks_by_slot: dict[str, list[str]] = {}
    for t in tasks:
        sref = str(t.get("schedule") or "")
        if sref:
            tasks_by_slot.setdefault(sref, []).append(str(t.get("task_id") or ""))

    def _sort_key(item: tuple[str, dict]) -> tuple[int, int]:
        """按本周首个触发时刻排序（无窗/解析失败沉底）。"""
        prof0 = profile_by_slot.get(item[0]) or {}
        firings = _slot_week_firings(str(item[1].get("cron") or ""), week_start, prof0.get("window_expr"))
        days = sorted(firings)
        if not days or not firings.get(days[0]):
            return (1, 0)
        hh, mm = firings[days[0]][0].split(":")
        return (0, int(hh) * 60 + int(mm))

    slots_out = [
        _slot_entry(
            name,
            spec,
            profile_by_slot.get(name) or {},
            tasks_by_slot.get(name, []),
            workers,
            week_start,
        )
        for name, spec in sorted(schedules.items(), key=_sort_key)
    ]
    return {
        "week_start": week_start.strftime("%Y-%m-%d"),
        "days": [(week_start + timedelta(days=i)).strftime("%m-%d 周" + _DOW_ZH[i]) for i in range(7)],
        "slot_count": len(slots_out),
        "task_total": sum(s["task_count"] for s in slots_out),
        "slots": slots_out,
    }


def build_resource_section(registry: dict) -> dict:
    """② 资源档位总览数据（全部取自 registry 头部，零硬编码词表）。"""
    entities: list[dict] = list(registry.get("entities") or [])
    by_pool: dict[str, int] = {}
    by_status: dict[str, int] = {}
    by_class: dict[str, int] = {}
    for e in entities:
        by_pool[str(e.get("pool"))] = by_pool.get(str(e.get("pool")), 0) + 1
        by_status[str(e.get("status"))] = by_status.get(str(e.get("status")), 0) + 1
        by_class[str(e.get("resource_class"))] = by_class.get(str(e.get("resource_class")), 0) + 1
    groups: dict[str, list[str]] = {}
    for e in entities:
        for g in e.get("exclusive_group") or []:
            groups.setdefault(str(g), []).append(str(e.get("task_id") or ""))
    measured_hit = sum(1 for e in entities if ((e.get("measured") or {}).get("peak_mem_gb")) is not None)
    return {
        "total_entities": registry.get("total_entities", len(entities)),
        "mem_ceiling_gb": registry.get("mem_ceiling_gb"),
        "lanes": list(((registry.get("pool_vocabulary") or {}).get("lanes")) or []),
        "workers": dict(((registry.get("pool_vocabulary") or {}).get("workers")) or {}),
        "by_pool": dict(sorted(by_pool.items(), key=lambda kv: -kv[1])),
        "by_status": dict(sorted(by_status.items(), key=lambda kv: -kv[1])),
        "by_class": dict(sorted(by_class.items(), key=lambda kv: -kv[1])),
        "exclusive_groups": {g: sorted(m) for g, m in sorted(groups.items())},
        "measured_coverage": f"{measured_hit}/{len(entities)}",
        "generated_at": registry.get("generated_at"),
        "generated_by": registry.get("generated_by"),
    }


# ---------------------------------------------------------------------------
# --selftest：一致性检查红/绿自证（纯内存注入，零落盘）
# ---------------------------------------------------------------------------
def run_selftest(project_root: Path) -> tuple[bool, list[str]]:
    """注入假引用→红；还原→绿。返回 (all_pass, 步骤日志)。"""
    log: list[str] = []
    tables = load_three_tables(project_root)
    root = str(project_root)

    def _xcounts(rep: dict) -> dict[str, int]:
        from collections import Counter

        return dict(Counter(f["reason_code"] for f in rep["findings"] if f["severity"] == "warn"))

    # 基线（gate_checks=False——只验证 X 检查的确定性，不掺存量闸 findings）
    base = check_tables(copy.deepcopy(tables), root, gate_checks=False)
    base_x = _xcounts(base)
    log.append(
        f"基线: unknown_slot={base_x.get('sched_x_unknown_slot', 0)} "
        f"missing_dep={base_x.get('sched_x_missing_dep', 0)} "
        f"profile_without_slot={base_x.get('sched_x_profile_without_slot', 0)} "
        f"ghost_pool={base_x.get('sched_x_ghost_pool', 0)}（期望全 0）"
    )
    ok_base = not any(
        base_x.get(k, 0)
        for k in ("sched_x_unknown_slot", "sched_x_missing_dep", "sched_x_profile_without_slot", "sched_x_ghost_pool")
    )

    # 注入四类假引用（deepcopy 内存态，绝不落盘）
    injected = copy.deepcopy(tables)
    injected["tasks"].append(
        {"task_id": f"{SELFTEST_TAG}_task", "schedule": f"{SELFTEST_TAG}_slot", "dependencies": []}
    )
    if injected["tasks"]:
        injected["tasks"][0] = {
            **injected["tasks"][0],
            "dependencies": list(injected["tasks"][0].get("dependencies") or []) + [f"{SELFTEST_TAG}_dep"],
        }
    injected["registry"].setdefault("entities", []).append(
        {"task_id": f"data_slot_{SELFTEST_TAG}_slot", "pool": f"{SELFTEST_TAG}_pool", "status": "active"}
    )
    red = check_tables(injected, root, gate_checks=False)
    red_x = _xcounts(red)
    checks = [
        ("sched_x_unknown_slot", "假任务→不存在槽位"),
        ("sched_x_missing_dep", "假依赖→不存在任务"),
        ("sched_x_profile_without_slot", "假实体→不存在槽位"),
        ("sched_x_ghost_pool", "假实体→幽灵池"),
    ]
    all_pass = ok_base
    for code, label in checks:
        hit = red_x.get(code, 0)
        ok = hit > 0
        all_pass = all_pass and ok
        log.append(f"注入→{'红(检出)' if ok else '绿(漏检!)'}: {label} [{code}] x{hit}")

    # 还原（重新读真源重跑 = 还原态）
    restored = check_tables(load_three_tables(project_root), root, gate_checks=False)
    rst_x = _xcounts(restored)
    ok_restore = not any(
        rst_x.get(k, 0)
        for k in ("sched_x_unknown_slot", "sched_x_missing_dep", "sched_x_profile_without_slot", "sched_x_ghost_pool")
    )
    all_pass = all_pass and ok_restore
    log.append(f"还原→{'绿' if ok_restore else '红(未还原!)'}: 真源重读四类检查归零")

    return all_pass, log


# ---------------------------------------------------------------------------
# 文本渲染
# ---------------------------------------------------------------------------
def _render_week_text(week: dict) -> list[str]:
    out = [
        "",
        "═" * 78,
        f"① 周历视图（槽位×任务映射）— 周窗 {week['week_start']} 起 | 槽位 {week['slot_count']} | 任务挂载 {week['task_total']}",
        "═" * 78,
    ]
    for s in week["slots"]:
        workers = s["workers"] if s["workers"] is not None else "?"
        days = " ".join(
            f"周{_DOW_ZH[d]}:{','.join(ts[:4]) + ('…' if len(ts) > 4 else '')}"
            for d, ts in sorted(s["week_firings"].items())
        )
        out.append(
            f"◆ {s['slot']}  cron={s['cron']}  executor={s['executor']}(workers={workers})  任务×{s['task_count']}"
        )
        prof = s["profile"]
        out.append(
            f"  档位: {prof.get('resource_class')}/{prof.get('pool')} {prof.get('peak_mem_gb')}GB "
            f"~{prof.get('est_duration_min')}min 互斥={prof.get('exclusive_group') or '-'} "
            f"交易敏感={prof.get('trading_sensitive')} 状态={prof.get('status')}"
        )
        if s["tasks"]:
            shown = ", ".join(s["tasks"][:5]) + (f" …共{s['task_count']}" if s["task_count"] > 5 else "")
            out.append(f"  任务: {shown}")
        if days:
            out.append(f"  本周: {days}")
        if s["description"]:
            out.append(f"  说明: {s['description']}")
    return out


def _render_resource_text(res: dict) -> list[str]:
    out = [
        "",
        "═" * 78,
        f"② 资源档位总览 — 实体 {res['total_entities']} | 实测覆盖 {res['measured_coverage']} | 内存天花板 {res['mem_ceiling_gb']}GB",
        "═" * 78,
    ]
    out.append(f"泳道: {res['lanes']}")
    out.append(f"workers: {res['workers']}")
    out.append(f"按池分布: {res['by_pool']}")
    out.append(f"按状态: {res['by_status']}")
    out.append(f"按资源类: {res['by_class']}")
    out.append(f"注册表生成: {res['generated_at']} by {res['generated_by']}")
    for g, members in res["exclusive_groups"].items():
        out.append(f"互斥组 {g}: {', '.join(members)}")
    return out


def _render_consistency_text(rep: dict) -> list[str]:
    s = rep["summary"]
    t = rep["tables"]
    out = [
        "",
        "═" * 78,
        f"③ 三表一致性检查 — 槽位 {t['slots']} × 任务 {t['tasks']} × 实体 {t['entities']} | block={s['block']} warn={s['warn']} info={s['info']}",
        "═" * 78,
    ]
    if t.get("errors"):
        out.append(f"表错误: {t['errors']}")
    if t.get("parked_tasks"):
        out.append(f"停放任务(schedule=disabled): {t['parked_tasks']}（约定内）")
    if not rep["findings"]:
        out.append("（无 findings）")
    for f in rep["findings"]:
        mark = {"block": "[BLOCK]", "warn": "[WARN] ", "info": "[info] "}.get(f["severity"], "[?]    ")
        ids = "+".join(f["task_ids"][:4]) + (f"…共{len(f['task_ids'])}" if len(f["task_ids"]) > 4 else "")
        out.append(f"{mark} {f['reason_code']}: {ids}")
        out.append(f"        {f['detail'][:110]}")
    return out


# ---------------------------------------------------------------------------
# --reconciler-status：reconciler 注册/执行 status 查询
# ---------------------------------------------------------------------------
def reconciler_status(project_root: Path) -> int:
    desc = describe()
    print(json.dumps(desc, ensure_ascii=False, indent=1))
    from zephyr.governance.audit.reconciliation_registry import ReconciliationRegistry

    reg = ReconciliationRegistry()
    reg.merge_external_specs()  # 外部规格发现钩子（gateway 禁碰时的运行时注册路径）
    ids = reg.list_gate_ids()
    registered = GATE_ID in ids
    print(f"registered_in_registry: {registered}（registry 共 {len(ids)} specs）")
    if registered:
        spec = [x for x in reg.specs if x.gate_id == GATE_ID][0]
        print(f"priority={spec.priority} file_ops={sorted(spec.file_ops)}")
        print(
            "trigger_smoke: 三表命中=",
            spec.trigger([str(project_root / RELPATH_TASKS)]),
            "无关文件=",
            spec.trigger(["README.md"]),
        )
    recent = query_recent_executions(project_root, limit=5)
    print(f"reconcile_execution_log 最近 {len(recent)} 条:")
    for r in recent:
        print(f"  {r['logged_at']} {r['action']:>6} session={r['session_id']} {str(r['detail'])[:80]}")
    report_path = project_root / REPORT_RELPATH
    if report_path.exists():
        try:
            data = json.loads(report_path.read_text(encoding="utf-8"))
            print(f"last_report: {REPORT_RELPATH} summary={data.get('summary')}")
        except Exception as exc:  # noqa: BLE001
            print(f"last_report: 读取失败 {exc}")
    else:
        print(f"last_report: 暂无（{REPORT_RELPATH} 首次 commit 触发后生成；可 --publish-report 预生成）")
    return 0 if registered else 2


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def _build_overview(args) -> tuple[dict | None, dict | None, dict | None]:
    """按 --section 装配三段数据（week/resource/consistency）。"""
    tables = load_three_tables(
        REPO_ROOT, registry_path=args.registry, tasks_path=args.tasks, schedule_path=args.schedule
    )
    now = datetime.now(timezone.utc)
    week = build_week_section(tables, _week_start_sh(now)) if args.section in ("all", "week") else None
    resource = build_resource_section(tables["registry"]) if args.section in ("all", "resource") else None
    rep = (
        check_tables(
            tables,
            str(REPO_ROOT),
            now=now,
            gate_checks=True,
            gate_horizon_days=args.horizon_days,
            registry_path=args.registry,
        )
        if args.section in ("all", "consistency")
        else None
    )
    return week, resource, rep


def _exit_code(rep: dict | None, fail_on: str) -> int:
    """exit 语义：0=无达标 finding；1=有（fail-on 判据：block > warn）。"""
    if rep is None or fail_on == "none":
        return 0
    threshold = 1 if fail_on == "warn" else 0  # severity 排序: block(0) > warn(1)
    bad = sum(1 for f in rep["findings"] if {"block": 0, "warn": 1}.get(f["severity"], 9) <= threshold)
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="排班三表统一总览入口（W4-4 三表一入口）")
    ap.add_argument("--registry", default=str(REPO_ROOT / RELPATH_REGISTRY))
    ap.add_argument("--tasks", default=str(REPO_ROOT / RELPATH_TASKS))
    ap.add_argument("--schedule", default=str(REPO_ROOT / RELPATH_SCHEDULE))
    ap.add_argument("--section", choices=["all", "week", "resource", "consistency"], default="all")
    ap.add_argument("--horizon-days", type=int, default=7, help="闸时段冲突检查地平线（默认 7）")
    ap.add_argument("--json", action="store_true", help="机生 JSON 输出")
    ap.add_argument("--publish-report", action="store_true", help="一致性报告落 .runtime（fix-in-place 同源写面）")
    ap.add_argument("--fail-on", choices=["block", "warn", "none"], default="block", help="exit 1 判据（默认 block）")
    ap.add_argument("--selftest", action="store_true", help="一致性检查红/绿自证（内存注入，零落盘）")
    ap.add_argument("--reconciler-status", action="store_true", help="reconciler 注册/执行 status 查询")
    args = ap.parse_args(argv)

    if args.reconciler_status:
        return reconciler_status(REPO_ROOT)

    if args.selftest:
        ok, log = run_selftest(REPO_ROOT)
        print("SELFTEST — 一致性检查注入假引用→红 / 还原→绿")
        for line in log:
            print(" ", line)
        print("RESULT:", "PASS" if ok else "FAIL")
        return 0 if ok else 1

    now = datetime.now(timezone.utc)
    week, resource, rep = _build_overview(args)
    if args.publish_report and rep is not None:
        out = write_report(rep, REPO_ROOT)
        print(f"[report] {out}", file=sys.stderr)

    if args.json:
        payload = {
            "generated_at": now.isoformat(timespec="seconds"),
            "entry": "scripts/ops/schedule_overview.py",
            "truth_tables": [RELPATH_REGISTRY, RELPATH_TASKS, RELPATH_SCHEDULE],
            "week": week,
            "resource": resource,
            "consistency": rep,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=1))
    else:
        print(f"排班三表总览（物理表不合并，读侧统一入口）@ {now.isoformat(timespec='seconds')}")
        if week:
            print("\n".join(_render_week_text(week)))
        if resource:
            print("\n".join(_render_resource_text(resource)))
        if rep:
            print("\n".join(_render_consistency_text(rep)))

    return _exit_code(rep, args.fail_on)


if __name__ == "__main__":
    raise SystemExit(main())
