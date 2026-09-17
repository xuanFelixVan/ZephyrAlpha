# [BLUEPRINT] MOD-INF-092 | depgraph design node 14753482（granularity=file，2026-09-18）
# [MODULE] zephyr.infra_ops.config_effect_checker
# [DOMAIN] D_INFRA_OPS
# [DEPENDENCIES] 标准库+PyYAML（轻依赖，供计划任务/调度器钩子双方惰性导入，不引重模块）
# [CONSUMERS] zephyr.data.scheduler（export_loaded_state 钩子复用 build/write 函数）; scripts/register_config_check_task.ps1（日频计划任务）; CLI(python -m zephyr.infra_ops.config_effect_checker)
# [STARTUP] event_driven
# noqa: m11-perm-manual-legitimate  M11豁免: 本件是 WORK-ORDER-3 烟雾报警器，argparse/CLI 仅为人工与 Windows 计划任务（ZephyrAlpha_ConfigCheck 日频 08:05 外部事件）触发入口，一次性进程 read->diff->alert->exit，同 fix_pattern_miner 先例；非常驻服务无需事件订阅
# [MATURITY] production
# [INVARIANTS] 快照缺失/损坏/schema 不符=unknown（fail-closed 不误报绿）; 判定真源=内容 sha256（mtime-only 漂移仅 warning 不翻红）; 快照写入必须原子（tmp+os.replace）; 告警只走 Alerter 正门（failures/*.json），ERROR 级才落失败文件; 本件是烟雾报警器，不做热加载（热更新本体已裁定搁置，2026-09-17 Owner 裁定）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check_config_effect 永不抛（I/O/解析异常降级为 unknown/内部记录）; CLI 退出码 0=ok / 1=mismatch / 2=unknown
# [TESTS] tests/infra_ops/test_config_effect_checker.py
# [A_module] module_id=MOD-INF-092 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
ConfigEffectChecker — 配置生效核对器（MOD-INF-092，WORK-ORDER-3）。

消灭"改了配置文件以为生效、进程还在用旧值"的静默失败。**不做热加载**
（热更新本体已裁定搁置），只做烟雾报警器。

机制（自裁记录 2026-09-18，裁定顺序：第一性原理→专业机构实践→社区惯例→开源先例）：
1. 消费方自报（exported loaded-state）：调度器进程在 load_config() 末尾把
   "已加载配置指纹"（schedule 槽位清单 + tasks 指纹 + 各文件 sha256/mtime +
   loaded_at + 解析后的内存结构）原子落盘快照。核对器对比"磁盘现状 vs 快照"。
   备选方案已否决：
   - 进程内省（读 /proc、py-spy attach）：Windows 无 /proc，attach 侵入生产进程，
     风险与热加载同阶——违背"不做热更新本体"裁定边界；
   - 消息总线广播 reload 事件：调度器 schedule/tasks 无 reload 路径（只有 policies
     有 maybe_reload），为核对器新造事件通道=范围膨胀；
   - 文件 mtime 轮询直接告警：mtime 不等于"进程在用旧值"的证据（生成器重写同内容
     会误报），且指不到具体键。
2. 判定真源=内容 sha256：mtime-only 变化只产生 warning（人工确认内容等价即可），
   不翻红——进程值与磁盘内容一致时不存在"用旧值"问题。
3. 覆盖面从实出发：schedule.yaml + tasks.yaml（调度器消费，有 loaded-state 导出）。
   risk_params.yaml / trading_decision_map.yaml 的消费方（pf_alloc/risk 栈）无
   loaded-state 导出钩子——登记 GAP，不强行改消费方（避免范围膨胀）。
4. 告警通道复用 Alerter（failures/*.json 正门，ERROR 级落文件、内置冷却去重）；
   仓内未发现可编程 task_board 机制（全仓 grep 无 .py/.yaml 命中），task_board
   接线登记为 GAP 开放项。

快照落点自裁：任务书建议 `.runtime/scheduler_loaded_state.json`，但宪法 §9.4
禁止向 .runtime 根直写；调度器现有运行态文件（instance lock/run log/heartbeat）
全部在 tmp/，故默认落 `tmp/scheduler_loaded_state.json`（路径可参数化覆盖）。
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "CoverageGap",
    "Mismatch",
    "Report",
    "build_loaded_state_snapshot",
    "check_config_effect",
    "write_loaded_state_snapshot",
]

from zephyr.shared.io.paths import REPO_ROOT

# 调度器消费的两份配置（与其 _DEFAULT_CONFIG_DIR 同源）
DEFAULT_CONFIG_DIR = REPO_ROOT / "src" / "zephyr" / "data" / "config"
# 快照默认落点（自裁见模块 docstring §4）
DEFAULT_SNAPSHOT_PATH = REPO_ROOT / "tmp" / "scheduler_loaded_state.json"
# 核对报告最新一份落点（计划任务 pythonw 无控制台，报告落文件供人工/前端查看）
DEFAULT_REPORT_PATH = REPO_ROOT / "tmp" / "config_effect_check_report.json"

SNAPSHOT_SCHEMA = "scheduler_loaded_state.v1"

# 调度器消费的覆盖面（有 loaded-state 导出，可机判）
SCHEDULER_CONSUMED_FILES = ("schedule.yaml", "tasks.yaml")
# GAP 名单：消费方无 loaded-state 导出，核对器只登记不判定
GAP_FILES = (
    ("config/risk_params.yaml", "pf_alloc/risk 栈（allocation_config/adaptive_risk_coordinator）"),
    ("config/trading_decision_map.yaml", "TDM 决策映射（decision_map_gate/risk_ssot 消费）"),
)

# 告警建议动作（安全窗重启正门：杀旧子进程 -> start_scheduler.ps1 guard 自动重拉）
_SUGGEST_RESTART = (
    "在安全窗重启数据调度器（结束旧调度器子进程，guard 会自动重拉；"
    "重启加载新配置后本项转绿）。当前进程仍在用旧值——改配置不会自动生效。"
)

_GAP_NOTE = (
    "该文件消费方无 loaded-state 导出钩子，本核对器不判定其生效性（登记 GAP，"
    "建议后续给消费方加 export_loaded_state 同款钩子后再纳入覆盖面）"
)


@dataclasses.dataclass
class Mismatch:
    """一条不一致记录（磁盘现状 vs 进程快照）。"""

    file: str
    kind: str  # content_drift / key_drift / file_missing / file_added / parse_error
    key_path: str  # 具体键路径（如 schedules.daily_kline.cron）；整体漂移时为 "(file)"
    disk_value: Any
    process_value: Any
    suggestion: str = _SUGGEST_RESTART

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class CoverageGap:
    """一条覆盖面缺口（消费方无 loaded-state 导出，只登记不判定）。"""

    file: str
    consumer: str
    note: str

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class Report:
    """核对结果报告。status: ok（绿）/ mismatch（红）/ unknown（不可判定，fail-closed）。"""

    status: str
    checked_at: str
    snapshot_path: str
    config_dir: str
    mismatches: list[Mismatch] = dataclasses.field(default_factory=list)
    warnings: list[str] = dataclasses.field(default_factory=list)
    gaps: list[CoverageGap] = dataclasses.field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "checked_at": self.checked_at,
            "snapshot_path": self.snapshot_path,
            "config_dir": self.config_dir,
            "mismatches": [m.as_dict() for m in self.mismatches],
            "warnings": list(self.warnings),
            "gaps": [g.as_dict() for g in self.gaps],
            "summary": self.summary,
        }


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _now_iso() -> str:
    """TZ 显式 ISO 时间戳（SSoT=now_utc，宪法硬规则10 SCHEMA-TZ，禁裸 datetime.now）。"""
    from zephyr.shared.utils.time_utils import now_utc

    return now_utc().isoformat(timespec="seconds")


def build_loaded_state_snapshot(
    config_dir: str | Path,
    schedules: dict[str, dict],
    tasks: list[dict],
    pid: int | None = None,
) -> dict:
    """构建"已加载配置指纹"快照（调度器 export_loaded_state 钩子的数据源）。

    Args:
        config_dir: 配置目录（含 schedule.yaml/tasks.yaml）。
        schedules: 进程内已加载的调度计划（scheduler._schedules）。
        tasks: 进程内已加载的任务清单（scheduler._tasks）。
        pid: 导出进程 PID（诊断用）。

    Returns:
        快照 dict（schema=scheduler_loaded_state.v1）。含指纹（sha256/mtime/size）、
        schedule 槽位清单与解析后的内存结构（核对器做键级对比用）。
    """
    config_dir = Path(config_dir)
    files: dict[str, dict] = {}
    for name in SCHEDULER_CONSUMED_FILES:
        fp = config_dir / name
        if not fp.exists():
            continue
        raw = fp.read_bytes()
        files[name] = {
            "sha256": _sha256_bytes(raw),
            "size": len(raw),
            "mtime_ns": fp.stat().st_mtime_ns,
        }
    return {
        "schema": SNAPSHOT_SCHEMA,
        "pid": pid if pid is not None else os.getpid(),
        "loaded_at": _now_iso(),
        "config_dir": str(config_dir.resolve()),
        "schedule_slots": sorted(schedules.keys()),
        "tasks_count": len(tasks),
        "files": files,
        "parsed": {"schedules": schedules, "tasks": tasks},
    }


def write_loaded_state_snapshot(snapshot: dict, path: str | Path) -> Path:
    """原子落盘快照（tmp + os.replace，核对器不会读到半写快照）。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(snapshot, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, path)
    return path


def _compact(value: Any) -> str:
    """值压缩表示（报告/告警里人读，截断防刷屏）。"""
    try:
        text = json.dumps(value, ensure_ascii=False, default=str)
    except Exception:  # noqa: BLE001 — 表示失败降级 str()
        text = str(value)
    return text if len(text) <= 200 else text[:197] + "..."


def _diff_schedules(
    disk: dict[str, dict],
    proc: dict[str, dict],
    file_label: str,
    out: list[Mismatch],
) -> None:
    """schedule 槽位级对比：增/删槽 + 槽内字段级漂移（指到具体键）。"""
    for name in sorted((set(disk) | set(proc))):
        d, p = disk.get(name), proc.get(name)
        if d is None:
            out.append(Mismatch(file_label, "slot_removed", f"schedules.{name}",
                                None, _compact(p)))
            continue
        if p is None:
            out.append(Mismatch(file_label, "slot_added", f"schedules.{name}",
                                _compact(d), None))
            continue
        if not isinstance(d, dict) or not isinstance(p, dict):
            if d != p:
                out.append(Mismatch(file_label, "key_drift", f"schedules.{name}",
                                    _compact(d), _compact(p)))
            continue
        for field in sorted(set(d) | set(p)):
            dv, pv = d.get(field), p.get(field)
            if dv != pv:
                out.append(Mismatch(file_label, "key_drift",
                                    f"schedules.{name}.{field}", _compact(dv), _compact(pv)))


def _diff_tasks(
    disk: list[dict],
    proc: list[dict],
    file_label: str,
    out: list[Mismatch],
) -> None:
    """tasks 任务级对比（按 task_id 索引）：增/删任务 + 任务字段级漂移。"""

    def index(items: list[dict]) -> dict[str, dict]:
        result: dict[str, dict] = {}
        for i, t in enumerate(items):
            key = str(t.get("task_id", f"<index:{i}>")) if isinstance(t, dict) else f"<index:{i}>"
            result[key] = t
        return result

    d_map, p_map = index(disk), index(proc)
    for tid in sorted(set(d_map) | set(p_map)):
        d, p = d_map.get(tid), p_map.get(tid)
        if d is None:
            out.append(Mismatch(file_label, "task_removed", f"tasks.{tid}", None, _compact(p)))
            continue
        if p is None:
            out.append(Mismatch(file_label, "task_added", f"tasks.{tid}", _compact(d), None))
            continue
        if not isinstance(d, dict) or not isinstance(p, dict):
            if d != p:
                out.append(Mismatch(file_label, "key_drift", f"tasks.{tid}",
                                    _compact(d), _compact(p)))
            continue
        for field in sorted(set(d) | set(p)):
            dv, pv = d.get(field), p.get(field)
            if dv != pv:
                out.append(Mismatch(file_label, "key_drift",
                                    f"tasks.{tid}.{field}", _compact(dv), _compact(pv)))


def _diff_parsed(
    disk_parsed: dict,
    proc_parsed: dict,
    file_label: str,
    out: list[Mismatch],
) -> None:
    """解析结构级对比（按文件身份只对比所属段：schedule.yaml→schedules，tasks.yaml→tasks）。

    两份文件段结构不同（schedule.yaml 无 tasks 键、tasks.yaml 无 schedules 键），
    若不按文件身份分段，会把另一文件的段误判为整体增删。
    """
    proc_parsed = proc_parsed or {}
    if file_label == "schedule.yaml":
        _diff_schedules(disk_parsed.get("schedules") or {}, proc_parsed.get("schedules") or {},
                        file_label, out)
    elif file_label == "tasks.yaml":
        _diff_tasks(disk_parsed.get("tasks") or [], proc_parsed.get("tasks") or [], file_label, out)


def _notify(alert: bool, failures_dir: str | Path | None, level: str, error: str,
            extra: dict | None) -> None:
    """告警正门：Alerter（failures_dir 注入供测试隔离；告警自身故障只记日志）。"""
    if not alert:
        return
    try:
        from zephyr.data.alerter import Alerter

        kwargs: dict = {"failures_dir": failures_dir} if failures_dir else {}
        Alerter(**kwargs).notify(
            task_id="config_effect_check",
            error=error,
            level=level,
            source="config_effect_checker",
            extra=extra,
        )
    except Exception:  # noqa: BLE001 — 告警通道故障不改变核对结论
        logger.warning("配置核对告警写入失败", exc_info=True)


def _load_snapshot(snapshot_path: Path) -> dict | None:
    """读取并校验快照。返回 None=缺失/损坏/schema 不符（fail-closed 判据）。"""
    if not snapshot_path.exists():
        return None
    try:
        loaded = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — 损坏快照按缺失处理（fail-closed）
        logger.warning("快照读取/解析失败: %s", snapshot_path, exc_info=True)
        return None
    if isinstance(loaded, dict) and loaded.get("schema") == SNAPSHOT_SCHEMA:
        return loaded
    return None


def _compare_one_file(
    config_dir: Path,
    name: str,
    meta: dict | None,
    proc_parsed: dict,
    mismatches: list[Mismatch],
    warnings: list[str],
) -> None:
    """单文件对比：缺失/新增/内容漂移/键级定位/mtime-only warning。"""
    fp = config_dir / name
    if meta is None:
        if fp.exists():
            mismatches.append(Mismatch(name, "file_added", "(file)",
                                       "磁盘存在但进程加载时缺失", None))
        return
    if not fp.exists():
        mismatches.append(Mismatch(name, "file_missing", "(file)", None,
                                   "进程加载过该文件，现磁盘已消失"))
        return
    raw = fp.read_bytes()
    disk_sha = _sha256_bytes(raw)
    if disk_sha == meta.get("sha256"):
        if fp.stat().st_mtime_ns != meta.get("mtime_ns"):
            warnings.append(
                f"{name}: mtime 变化但内容 sha256 一致（重写同内容/被 touch），"
                "不构成'进程用旧值'证据，无需重启"
            )
        return
    mismatches.append(Mismatch(name, "content_drift", "(file)",
                               f"sha256={disk_sha[:12]}...", None))
    # 键级定位：磁盘 YAML 可解析且快照带 parsed 时逐键对比
    try:
        import yaml

        disk_parsed = yaml.safe_load(raw) or {}
    except Exception as exc:  # noqa: BLE001 — 磁盘 YAML 损坏本身就是不一致
        mismatches.append(Mismatch(name, "parse_error", "(yaml)",
                                   f"YAML 解析失败: {exc}", None))
        return
    if proc_parsed:
        _diff_parsed(disk_parsed, proc_parsed, name, mismatches)
    else:
        mismatches.append(Mismatch(name, "key_drift", "(parsed)",
                                   "磁盘结构见 content_drift", "快照无 parsed 结构，无法键级定位"))


def _build_summary(
    status: str,
    mismatches: list[Mismatch],
    warnings: list[str],
    snapshot: dict,
) -> str:
    """人读摘要（ok=绿 / mismatch=红，均带 loaded_at/pid 溯源）。"""
    loaded_at, pid = snapshot.get("loaded_at"), snapshot.get("pid")
    if status == "ok":
        return (
            f"一致（绿）：{', '.join(SCHEDULER_CONSUMED_FILES)} 磁盘现状与调度器"
            f" loaded-state 快照一致（loaded_at={loaded_at}, pid={pid}, "
            f"{len(snapshot.get('schedule_slots') or [])} 档时段/"
            f"{snapshot.get('tasks_count')} 任务）。"
            + ("；".join(warnings) if warnings else "")
        )
    keys = "; ".join(f"{m.file}:{m.key_path}[{m.kind}]" for m in mismatches[:10])
    return (
        f"不一致（{len(mismatches)} 条）：{keys}。"
        f"调度器进程（loaded_at={loaded_at}, pid={pid}）仍在用旧配置值。"
    )


def check_config_effect(
    config_dir: str | Path | None = None,
    snapshot_path: str | Path | None = None,
    alert: bool = True,
    failures_dir: str | Path | None = None,
) -> Report:
    """核对"磁盘配置现状"vs"调度器进程已加载指纹快照"。

    Args:
        config_dir: 配置目录。None 用默认 src/zephyr/data/config。
        snapshot_path: 快照路径。None 用默认 tmp/scheduler_loaded_state.json。
        alert: 不一致时是否走 Alerter 告警（测试传 False 隔离生产 failures/）。
        failures_dir: 告警失败文件目录注入（测试隔离用；None 用 Alerter 默认）。

    Returns:
        Report。status:
        - ok: 覆盖面内磁盘与进程一致（可能有 mtime-only warning）
        - mismatch: 存在内容漂移（附具体键与建议动作）
        - unknown: 快照缺失/损坏/schema 不符——**不可判定，fail-closed 不误报绿**
    """
    config_dir = Path(config_dir) if config_dir else DEFAULT_CONFIG_DIR
    snapshot_path = Path(snapshot_path) if snapshot_path else DEFAULT_SNAPSHOT_PATH
    gaps = [
        CoverageGap(rel, consumer, _GAP_NOTE)
        for rel, consumer in GAP_FILES
        if (REPO_ROOT / rel).exists()
    ]
    base = {
        "checked_at": _now_iso(),
        "snapshot_path": str(snapshot_path),
        "config_dir": str(config_dir),
        "gaps": gaps,
    }

    # ── fail-closed：快照缺失/损坏/schema 不符 = 不可判定 ──
    snapshot = _load_snapshot(snapshot_path)
    if snapshot is None:
        report = Report(
            status="unknown",
            summary=(
                "不可判定：调度器 loaded-state 快照缺失/损坏或 schema 不符"
                f"（{snapshot_path}）。fail-closed 不判绿——调度器可能未运行、"
                "未带导出钩子的旧版本、或快照被清理。请核实调度器进程后重试。"
            ),
            **base,
        )
        _notify(alert, failures_dir, "WARN", report.summary, None)
        return report

    mismatches: list[Mismatch] = []
    warnings: list[str] = []
    files_meta: dict = snapshot.get("files") or {}
    parsed = snapshot.get("parsed") or {}
    for name in SCHEDULER_CONSUMED_FILES:
        _compare_one_file(config_dir, name, files_meta.get(name), parsed,
                          mismatches, warnings)

    status = "mismatch" if mismatches else "ok"
    summary = _build_summary(status, mismatches, warnings, snapshot)
    report = Report(status=status, mismatches=mismatches, warnings=warnings,
                    summary=summary, **base)
    if status == "mismatch":
        _notify(alert, failures_dir, "ERROR", summary,
                {"mismatches": [m.as_dict() for m in mismatches]})
    return report


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：核对并输出报告（退出码 0=ok / 1=mismatch / 2=unknown）。"""
    import argparse

    parser = argparse.ArgumentParser(description="Config effect checker (WORK-ORDER-3 smoke alarm)")
    parser.add_argument("--config-dir", default=None, help="config dir (default src/zephyr/data/config)")
    parser.add_argument("--snapshot-path", default=None, help="loaded-state snapshot (default tmp/scheduler_loaded_state.json)")
    parser.add_argument("--no-alert", action="store_true", help="disable Alerter notify")
    parser.add_argument("--report-out", default=None, help="write latest report JSON here (default tmp/config_effect_check_report.json)")
    parser.add_argument("--quiet", action="store_true", help="only exit code, no stdout report")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    report = check_config_effect(
        config_dir=args.config_dir,
        snapshot_path=args.snapshot_path,
        alert=not args.no_alert,
    )
    payload = json.dumps(report.to_dict(), ensure_ascii=False, indent=1)
    report_out = Path(args.report_out) if args.report_out else DEFAULT_REPORT_PATH
    try:
        report_out.parent.mkdir(parents=True, exist_ok=True)
        report_out.write_text(payload, encoding="utf-8")
    except Exception:  # noqa: BLE001 — 报告落盘失败不影响退出码语义
        logger.warning("报告落盘失败: %s", report_out, exc_info=True)
    if not args.quiet:
        print(payload)
    else:
        print(report.summary)
    return {"ok": 0, "mismatch": 1, "unknown": 2}[report.status]


if __name__ == "__main__":
    raise SystemExit(main())
