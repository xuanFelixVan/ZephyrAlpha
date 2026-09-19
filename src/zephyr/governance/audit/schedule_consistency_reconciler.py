# [BLUEPRINT] MOD-GOV_SCHED_CONSISTENCY_RECONCILER | docs/03_modules/_domain_governance/blueprint.md | §schedule-consistency-reconciler
# [MODULE] zephyr.governance.audit.schedule_consistency_reconciler
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcileResult, ReconcilerSpec, _governance_db_path);
#   zephyr.gov_enforcement.commit_gates.resource_schedule_gate (run_all_checks, load_registry_entities——时段冲突/漂移同源复用);
#   zephyr.shared.utils.time_utils (now_utc); zephyr.shared.io.file_utils (safe_write_text); PyYAML
# [CONSUMERS] scripts/ops/schedule_overview.py（统一入口，W4-4 三表一入口）;
#   zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway（post-commit 事件触发，
#   经 ReconciliationRegistry 外部规格发现钩子注册——gateway 本体 MM 在途禁碰，注册走运行时路径）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 排班三表物理不合并（Owner 裁定）：tasks.yaml+schedule.yaml=任务↔槽位主从系统，
#   resource_profile_registry=独立资源维度——本模块只做跨表读侧一致性核对，禁写三表真源;
#   reconciler 只 warn/skip/fix-in-place（fix-in-place=仅重写 .runtime 报告），禁 action=auto_committed/commit;
#   post-commit 事件触发（三表任一 commit 才触发），禁 cron/Timer/sleep-loop（宪法 §9.3）;
#   检测不自动改数——报不一致等 Owner/责任会话处置（owner 责任制）
# [MODIFY-GUARD] GATE_ID/_PRIORITY/_TRIGGER_RELPATHS/_PARKED_SLOT reason_code 语义
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] run_schedule_consistency 单表读取/解析失败 → sched_x_table_error(warn) 不抛；
#   reconcile 永不抛异常（异常降级 ReconcileResult(action="warn")，registry 框架兜底）
# [TESTS] tests/governance/audit/test_schedule_consistency_reconciler.py
# [A_module] module_id=MOD-GOV_SCHED_CONSISTENCY_RECONCILER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: reconciler 是 commit 事件触发(非 cron/manual)
"""schedule_consistency_reconciler — 排班三表一致性核对 + post-commit 事件触发 reconciler（W4-4③）。

三表一入口（Owner 裁定：物理表不合并，逻辑系统一个入口）
--------------------------------------------------------
- 表1 ``config/resource_profile_registry.yaml``（资源维度，86 实体，生成器产出）
- 表2 ``src/zephyr/data/config/tasks.yaml``（任务维度，任务引用槽位=主从系统）
- 表3 ``src/zephyr/data/config/schedule.yaml``（槽位维度，21→24 槽位）

本模块 = 三表交叉一致性的**读侧核对核心**（检测，不改数）+ ReconcilerSpec 工厂。
统一 CLI 入口 = ``scripts/ops/schedule_overview.py``（三段总览/一致性/--selftest/--reconciler-status）。

核对项（三表交叉）
------------------
- sched_x_unknown_slot: 任务引用的槽位在 schedule.yaml 不存在（X1，warn）
- sched_x_parked_task: 任务的 schedule=``disabled``（停放约定，info 只计数）
- sched_x_slot_without_profile / sched_x_profile_without_slot: 槽位↔data_slot_* 实体双向（X2，warn）
- sched_x_slot_without_tasks: 槽位零任务挂载（info）
- sched_x_ghost_pool: 实体 pool 不在 pool_vocabulary.lanes（X5，warn——daily_crypto 事故同类）
- sched_x_missing_truth_source: 实体 schedule_truth_source 指针失效（warn）
- sched_x_missing_dep: tasks.yaml dependencies 引用不存在 task_id（X6，warn）
- sched_x_table_error: 表缺失/解析失败（warn，fail-open 不阻断观测）
- 闸 findings 直通: resource_schedule_gate.run_all_checks（重叠组/内存天花板/E0/真源漂移，X4 时段冲突同源零复制）

注册路径（gateway 禁碰时的运行时注册）
--------------------------------------
git_commit_gateway.py 静态注册段在途（他会话 MM），改走
``ReconciliationRegistry.merge_external_specs`` 外部规格合并入口（reconcile_for
入口惰性调用，构造期保持"新 registry 为空"不变量）。验收 status：
``python scripts/ops/schedule_overview.py --reconciler-status``。

Usage::

    from zephyr.governance.audit.schedule_consistency_reconciler import (
        run_schedule_consistency, make_schedule_consistency_reconciler,
    )
    report = run_schedule_consistency(project_root)
    registry.register(make_schedule_consistency_reconciler(gateway))

# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/audit/schedule_consistency_reconciler.yaml
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.governance.audit.reconciliation_registry import (
    ReconcileResult,
    ReconcilerSpec,
    _governance_db_path,
)
from zephyr.shared.io.file_utils import safe_write_text
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

GATE_ID = "GATE-SCHEDULE-CONSISTENCY"
_PRIORITY = 826  # blueprint_status_transition(825) 之后、worktree watchdog(845) 之前

#: 三表真源路径（相对 project_root，正斜杠口径）
RELPATH_REGISTRY = "config/resource_profile_registry.yaml"
RELPATH_TASKS = "src/zephyr/data/config/tasks.yaml"
RELPATH_SCHEDULE = "src/zephyr/data/config/schedule.yaml"

#: 触发路径 = 三表真源 + 本模块 + 统一 CLI（改动即触发对账）
_TRIGGER_RELPATHS = (
    RELPATH_REGISTRY,
    RELPATH_TASKS,
    RELPATH_SCHEDULE,
    "src/zephyr/governance/audit/schedule_consistency_reconciler.py",
    "scripts/ops/schedule_overview.py",
)

#: 停放伪槽位（tasks.yaml schedule=disabled 为退役/暂停停放约定，非断链）
_PARKED_SLOT = "disabled"

#: data_slot_<slot> 实体命名前缀（生成器对 schedule.yaml 槽位的确定性映射）
_SLOT_ENTITY_PREFIX = "data_slot_"

#: fix-in-place 报告落点（.runtime 子目录，非根直写；仅此一处写面）
REPORT_RELPATH = ".runtime/schedule_consistency/last_result.json"

#: status 查询 SQL（NO-BARE-SQL 集中化：模块级常量）
SQL_RECENT_EXECUTIONS: Final[str] = (
    "SELECT log_id, logged_at, session_id, action, detail"
    " FROM reconcile_execution_log"
    " WHERE gate_id = ? ORDER BY logged_at DESC LIMIT ?"
)

#: 自检注入的假引用标记（--selftest 用，绝不落盘）
SELFTEST_TAG = "__selftest_fake__"


# ---------------------------------------------------------------------------
# 三表读取 + 一致性核对核心（CLI 与 reconciler 同源共用）
# ---------------------------------------------------------------------------
def _resolve(root: Path, relpath: str, override: str | None) -> Path:
    if override:
        return Path(override)
    return root / relpath


def load_three_tables(
    project_root: str | Path,
    *,
    registry_path: str | None = None,
    tasks_path: str | None = None,
    schedule_path: str | None = None,
) -> dict[str, Any]:
    """读三表 → {"registry": dict, "tasks": list, "schedule": dict, "errors": {表名: str}}。

    单表失败不抛（errors 记原因，核对阶段降级为 sched_x_table_error finding）。
    """
    root = Path(project_root)
    out: dict[str, Any] = {"registry": {}, "tasks": [], "schedule": {}, "errors": {}}
    specs = (
        ("registry", _resolve(root, RELPATH_REGISTRY, registry_path)),
        ("tasks", _resolve(root, RELPATH_TASKS, tasks_path)),
        ("schedule", _resolve(root, RELPATH_SCHEDULE, schedule_path)),
    )
    for name, path in specs:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except FileNotFoundError:
            out["errors"][name] = f"missing: {path}"
            continue
        except Exception as exc:  # noqa: BLE001 — 解析失败降级为 finding
            out["errors"][name] = f"parse: {type(exc).__name__}: {exc}"
            continue
        if name == "registry":
            out["registry"] = data
        elif name == "tasks":
            out["tasks"] = list(data.get("tasks") or [])
        else:
            out["schedule"] = data.get("schedules") or {}
    return out


def run_schedule_consistency(
    project_root: str | Path,
    *,
    now: datetime | None = None,
    registry_path: str | None = None,
    tasks_path: str | None = None,
    schedule_path: str | None = None,
    gate_checks: bool = True,
    gate_horizon_days: int = 7,
) -> dict[str, Any]:
    """三表交叉一致性核对（读三表 → check_tables；不改任何真源）。"""
    tables = load_three_tables(
        Path(project_root), registry_path=registry_path, tasks_path=tasks_path, schedule_path=schedule_path
    )
    return check_tables(
        tables,
        project_root,
        now=now,
        gate_checks=gate_checks,
        gate_horizon_days=gate_horizon_days,
        registry_path=registry_path,
    )


def _check_task_slot_refs(tasks: list[dict], slot_names: set[str]) -> tuple[list[dict], list[str]]:
    """X1 任务→槽位存在性（disabled=停放约定，info 计数）。返回 (findings, parked)。"""
    out: list[dict[str, Any]] = []
    parked: list[str] = []
    for t in tasks:
        tid = str(t.get("task_id") or "")
        if not tid:
            continue
        sched_ref = t.get("schedule")
        if sched_ref == _PARKED_SLOT:
            parked.append(tid)
        elif sched_ref not in slot_names:
            out.append(
                {
                    "reason_code": "sched_x_unknown_slot",
                    "severity": "warn",
                    "task_ids": [tid],
                    "detail": f"任务引用槽位 {sched_ref!r} 不在 schedule.yaml（{len(slot_names)} 槽位）",
                }
            )
    return out, parked


def _check_task_deps(tasks: list[dict], task_ids_known: set[str]) -> list[dict]:
    """X6 任务 DAG 依赖存在性。"""
    out: list[dict[str, Any]] = []
    for t in tasks:
        tid = str(t.get("task_id") or "")
        for dep in t.get("dependencies") or []:
            if str(dep) not in task_ids_known:
                out.append(
                    {
                        "reason_code": "sched_x_missing_dep",
                        "severity": "warn",
                        "task_ids": [tid],
                        "detail": f"依赖 {dep!r} 不在 tasks.yaml 任务清单",
                    }
                )
    return out


def _check_slot_entity_join(slot_names: set[str], entities: list[dict], tasks: list[dict]) -> list[dict]:
    """X2 槽位↔data_slot_* 实体双向 + 槽位→任务挂载计数（info）。"""
    out: list[dict[str, Any]] = []
    slot_entities = {
        str(e.get("task_id")): e for e in entities if str(e.get("task_id") or "").startswith(_SLOT_ENTITY_PREFIX)
    }
    tasks_by_slot: dict[str, list[str]] = {}
    for t in tasks:
        sref = str(t.get("schedule") or "")
        if sref:
            tasks_by_slot.setdefault(sref, []).append(str(t.get("task_id") or ""))
    for slot in sorted(slot_names):
        eid = _SLOT_ENTITY_PREFIX + slot
        if eid not in slot_entities:
            out.append(
                {
                    "reason_code": "sched_x_slot_without_profile",
                    "severity": "warn",
                    "task_ids": [slot],
                    "detail": f"槽位缺资源画像实体 {eid}",
                }
            )
        if not tasks_by_slot.get(slot):
            out.append(
                {
                    "reason_code": "sched_x_slot_without_tasks",
                    "severity": "info",
                    "task_ids": [slot],
                    "detail": "槽位零任务挂载（待排或保留槽）",
                }
            )
    for eid in sorted(slot_entities):
        slot = eid[len(_SLOT_ENTITY_PREFIX) :]
        if slot not in slot_names:
            out.append(
                {
                    "reason_code": "sched_x_profile_without_slot",
                    "severity": "warn",
                    "task_ids": [eid],
                    "detail": f"实体指向不存在的槽位 {slot!r}",
                }
            )
    return out


def _check_pools_and_truth(entities: list[dict], lanes: set[str], root: Path) -> list[dict]:
    """X5 幽灵池 + 真源指针有效性（非槽位实体一并核）。"""
    out: list[dict[str, Any]] = []
    for e in entities:
        eid = str(e.get("task_id") or "")
        pool = e.get("pool")
        if lanes and pool not in lanes:
            out.append(
                {
                    "reason_code": "sched_x_ghost_pool",
                    "severity": "warn",
                    "task_ids": [eid],
                    "detail": (
                        f"pool={pool!r} 不在 pool_vocabulary.lanes={sorted(lanes)}"
                        "（daily_crypto 事故同类：APScheduler 触发时摘 job）"
                    ),
                }
            )
        src = e.get("schedule_truth_source")
        if src and not (root / str(src)).exists():
            out.append(
                {
                    "reason_code": "sched_x_missing_truth_source",
                    "severity": "warn",
                    "task_ids": [eid],
                    "detail": f"schedule_truth_source 指针失效: {src}",
                }
            )
    return out


def _gate_passthrough_findings(reg_path: Path, ts: datetime, gate_horizon_days: int) -> list[dict[str, Any]]:
    """X4 时段冲突/漂移等——闸同源复用（真源=resource_schedule_gate）；失败 fail-open。"""
    out: list[dict[str, Any]] = []
    try:
        from zephyr.gov_enforcement.commit_gates.resource_schedule_gate import run_all_checks

        for f in run_all_checks(reg_path, ts, horizon_days=gate_horizon_days):
            out.append(
                {
                    "reason_code": f.reason_code,
                    "severity": f.severity,
                    "task_ids": list(f.task_ids),
                    "detail": f"闸直通: {f.detail}",
                }
            )
    except Exception as exc:  # noqa: BLE001 — 闸装载失败 fail-open（观测件不阻断）
        out.append(
            {
                "reason_code": "sched_x_table_error",
                "severity": "warn",
                "task_ids": ["<gate>"],
                "detail": f"resource_schedule_gate 复用失败: {type(exc).__name__}: {exc}",
            }
        )
    return out


def check_tables(
    tables: dict[str, Any],
    project_root: str | Path,
    *,
    now: datetime | None = None,
    gate_checks: bool = True,
    gate_horizon_days: int = 7,
    registry_path: str | None = None,
) -> dict[str, Any]:
    """对已装载三表做交叉一致性核对（纯函数——--selftest 内存注入假引用走此处）。

    gate_checks=True 时并入 resource_schedule_gate.run_all_checks（时段冲突/内存天花板/
    E0/真源漂移——冲突语义单真源零复制）；装载失败降级为 warn finding 不阻断。
    """
    root = Path(project_root)
    ts = now or now_utc()
    findings: list[dict[str, Any]] = []

    def _add(reason: str, severity: str, task_ids: list[str], detail: str) -> None:
        findings.append({"reason_code": reason, "severity": severity, "task_ids": task_ids, "detail": detail})

    for tname, err in sorted(tables["errors"].items()):
        _add("sched_x_table_error", "warn", [tname], f"三表读取失败（{tname}）: {err}")

    schedules: dict = tables["schedule"]
    tasks: list[dict] = tables["tasks"]
    registry: dict = tables["registry"]
    entities: list[dict] = list(registry.get("entities") or [])
    slot_names = set(schedules.keys())
    lanes = set(((registry.get("pool_vocabulary") or {}).get("lanes")) or [])

    # X1/X6 任务面
    refs, parked = _check_task_slot_refs(tasks, slot_names)
    findings.extend(refs)
    task_ids_known = {str(t.get("task_id") or "") for t in tasks if t.get("task_id")}
    if parked:
        _add(
            "sched_x_parked_task",
            "info",
            parked,
            f"{len(parked)} 任务停放于伪槽位 {_PARKED_SLOT!r}（约定内，仅计数）",
        )
    findings.extend(_check_task_deps(tasks, task_ids_known))

    # X2 槽位↔实体双向 + X5 幽灵池/真源指针
    findings.extend(_check_slot_entity_join(slot_names, entities, tasks))
    findings.extend(_check_pools_and_truth(entities, lanes, root))

    # X4 时段冲突/漂移等——闸同源复用（真源=resource_schedule_gate）
    if gate_checks and not tables["errors"].get("registry"):
        findings.extend(
            _gate_passthrough_findings(_resolve(root, RELPATH_REGISTRY, registry_path), ts, gate_horizon_days)
        )

    counts = {"block": 0, "warn": 0, "info": 0}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    return {
        "generated_at": ts.isoformat(timespec="seconds"),
        "gate_id": GATE_ID,
        "tables": {
            "slots": len(slot_names),
            "tasks": len(tasks),
            "entities": len(entities),
            "parked_tasks": len(parked),
            "errors": dict(tables["errors"]),
        },
        "findings": findings,
        "summary": {
            **counts,
            "ok": counts["block"] == 0 and counts["warn"] == 0,
        },
    }


def write_report(report: dict, project_root: str | Path) -> Path:
    """fix-in-place 唯一写面：报告落 .runtime/schedule_consistency/last_result.json。"""
    root = Path(project_root)
    out = root / REPORT_RELPATH
    out.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(report, ensure_ascii=False, indent=1) + "\n"
    expected = None
    if out.exists():
        from zephyr.shared.io.file_utils import content_sha256

        expected = content_sha256(out.read_text(encoding="utf-8"))
    safe_write_text(out, text, expected_base_sha256=expected, newline="\n")
    return out


def query_recent_executions(project_root: str | Path, limit: int = 5) -> list[dict]:
    """status 查询：governance.db reconcile_execution_log 本 gate 最近 N 条（只读）。"""
    db_path = Path(_governance_db_path(str(project_root)))
    if not db_path.exists():
        return []
    conn = sqlite3.connect(str(db_path), timeout=30.0)
    try:
        rows = conn.execute(SQL_RECENT_EXECUTIONS, (GATE_ID, int(limit))).fetchall()
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()
    return [{"log_id": r[0], "logged_at": r[1], "session_id": r[2], "action": r[3], "detail": r[4]} for r in rows]


def describe() -> dict[str, Any]:
    """status 描述（--reconciler-status 消费；不构造任何重对象）。"""
    return {
        "gate_id": GATE_ID,
        "priority": _PRIORITY,
        "module": "zephyr.governance.audit.schedule_consistency_reconciler",
        "trigger_relpaths": list(_TRIGGER_RELPATHS),
        "trigger_mode": "post-commit 事件触发（ReconciliationRegistry.merge_external_specs 运行时注册）",
        "action_vocabulary": "warn|skip|fix-in-place(仅重写 .runtime 报告)；禁 auto_committed/commit",
        "report": REPORT_RELPATH,
        "truth_tables": [RELPATH_REGISTRY, RELPATH_TASKS, RELPATH_SCHEDULE],
    }


# ---------------------------------------------------------------------------
# ReconcilerSpec 工厂（gateway 静态注册与 registry 外部发现钩子双通道同款）
# ---------------------------------------------------------------------------
def make_schedule_consistency_reconciler(gateway: object | None = None) -> ReconcilerSpec:
    """构造 post-commit 三表一致性 reconciler（只 warn/skip/fix-in-place）。

    Args:
        gateway: GitCommitGateway 实例或 None——仅取 project_root；None 时自解析 REPO_ROOT。
    """
    if gateway is not None and getattr(gateway, "project_root", None):
        project_root = Path(str(gateway.project_root))
    else:
        from zephyr.shared.io.paths import REPO_ROOT

        project_root = Path(str(REPO_ROOT))

    def _rel(f: str) -> str:
        try:
            return os.path.relpath(f, str(project_root)).replace("\\", "/")
        except ValueError:
            return f

    def _trigger(committed_files: list[str]) -> bool:
        for f in committed_files:
            rel = _rel(f)
            if rel in _TRIGGER_RELPATHS:
                return True
        return False

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        try:
            report = run_schedule_consistency(project_root)
            hit = [_rel(f) for f in committed_files if _rel(f) in _TRIGGER_RELPATHS]
            report["trigger"] = {"session_id": session_id, "files": hit[:8]}
            out = write_report(report, project_root)
            s = report["summary"]
            detail = (
                f"三表一致性: slots={report['tables']['slots']} tasks={report['tables']['tasks']} "
                f"entities={report['tables']['entities']} block={s['block']} warn={s['warn']} "
                f"info={s['info']} 报告={REPORT_RELPATH}（检测不自动改，处置=owner 责任制）"
            )
            # 只 warn/clean——禁 auto_committed/commit（Owner 裁定：报不一致不自动改）
            return ReconcileResult(
                action="warn" if (s["warn"] or s["block"]) else "clean",
                detail=detail,
                gate_id=GATE_ID,
            )
        except Exception as exc:  # noqa: BLE001 — reconciler 永不抛异常
            logger.warning("%s reconcile failed: %s", GATE_ID, exc, exc_info=True)
            return ReconcileResult(action="warn", detail=f"reconcile failed: {exc}", gate_id=GATE_ID)

    return ReconcilerSpec(
        gate_id=GATE_ID,
        trigger=_trigger,
        reconcile=_reconcile,
        priority=_PRIORITY,
        file_ops=frozenset({"read", "write"}),  # write 仅限 .runtime 报告（fix-in-place 唯一写面）
    )


def make_external_reconciler_spec(host: object | None = None) -> ReconcilerSpec:
    """ReconciliationRegistry 外部规格发现钩子入口（签名稳定：registry/gateway/None 均可）。"""
    return make_schedule_consistency_reconciler(host)
