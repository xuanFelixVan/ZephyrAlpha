# [BLUEPRINT] MOD-RESCHED-GATE | docs/03_modules/_cross_layer/resource_schedule_gate/blueprint.md | §
# [MODULE] zephyr.gov_enforcement.commit_gates.resource_schedule_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] croniter; yaml; scripts/backtest/compute_window_gate.py（E0 classify_window/gate_decision
#   纯函数最小 import 级复用，不改其既有函数）; scripts/governance/generators/generate_resource_profile_registry.py
#   （真源抽取函数复用，防克隆）; zephyr.gov_enforcement.commit_gates._diff_helpers（第四查 own-scope
#   归因：读 staged vs HEAD 注册表，算本次变更实体集）
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway（经 in_process_gate_registry.yaml 注册）;
#   scripts/governance/generators/generate_resource_week_view.py（冲突标注复用检查函数）;
#   zephyr.infrastructure.system_telemetry.alerts.resource_schedule_alerts（findings→告警桥）;
#   tests/governance/commit_gates/test_resource_schedule_gate.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 结构校验型闸（登记时/提交时），不是运行时调度器;
#   own-scope——仅 staged 命中 config/resource_profile_registry.yaml 时触发;
#   互斥组重叠/内存天花板/申报超线=硬阻断；真源漂移=warn 不阻断（防指针失效告警）;
#   planned 实体不占内存并发预算（裁定 R-D：未排产不计和）——同判据适用于第四查;
#   第四查 check_pool_concurrency（v2 C-8 同刻冲突结构盲区）：同 pool 同刻跨组堆积 +
#   同池并发内存和超 mem_ceiling 双判据，一律 sched_pool_concurrency（block），
#   与 check_mem_ceiling 共用同一窗档展开/扫描线求和数学（_budget_rows/_concurrency_sweep
#   单源，禁两套口径）；未挂 pool 的实体不臆造合成池（池缺席=sched_pool_undeclared 的账）;
#   常驻/event 型实体（window_expr 缺席或 est_duration_min≤0）永不进窗档求和（与
#   check_mem_ceiling 同口径），只在 finding.extra.resident_baseline_gb 显影该池常驻基线
#   ——基线可见而不掺和窗档账;
#   同刻堆积判据是**新冲突类**（全仓存量非零，P3 第一轮重排班清零），故仅在本次 staged
#   变更实体可归因（focus）时判，不可归因即跳过并告警留痕（宪法 §3 不连坐）；内存和
#   判据与 sched_mem_ceiling 同性质（预算类，存量已绿）→ 全量判，归因失败也不放松;
#   E0 复用 classify_window/gate_decision 纯函数，异常/日历未知 fail-closed;
#   cron 解析异常=该实体跳时间窗检查并记 finding（不炸整闸）;
#   理由码沿用 E0 风格：本闸产出五码 sched_overlap_group/sched_mem_ceiling/sched_e0_block
#   /sched_truth_drift（漂移=warn）+sched_pool_concurrency（第四查，v2 C-8）；另有排产真值
#   健康码七码 sched_gate_absent/sched_view_stale
#   /sched_pool_undeclared/sched_task_disabled/sched_task_missing/sched_task_orphan
#   /sched_task_probe_unavailable（由注册表生成器 --check 臂产出——检测者须独立于
#   被检测的闸与注册表本体，但清单真源在本模块）
# [MODIFY-GUARD] gate_id="RESOURCE-SCHEDULE"；理由码变更须同步 resource_schedule_alerts+视图
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 注册表 YAML 损坏=fail-closed 阻断；croniter 缺席=时间窗检查降级 warn；E0 异常=fail-closed
# [TESTS] tests/governance/commit_gates/test_resource_schedule_gate.py
# [A_module] module_id=MOD-RESCHED-GATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
#
# 边:
# I1 --> A1
# I1 --> A3
# I2 --> A2
# A1 --> A2
# A2 --> O1
# A3 --> O1
"""resource_schedule_gate — 排班冲突检测 commit gate（MOD-RESCHED-GATE，B2 闸）。

资源排班全景四件套之"闸"（方案 §2.3）。四个检查+漂移检测，作用时点=登记时/提交时
结构校验（对齐 FACTORY-MAP gate 范式），不是运行时调度器：

1. ``check_overlap_group`` — 同 exclusive_group 两任务时间窗交叠（window_expr cron
   展开+est_duration_min 区间数学）→ sched_overlap_group（block）；
2. ``check_mem_ceiling`` — 同窗并发 peak_mem_gb 之和 > mem_ceiling_gb（引用
   reaper _DANGEROUS_MEM_GB=10 红线，勿收编）→ sched_mem_ceiling（block）；单实体
   申报超线同拦。裁定 R-D（2026-09-17 v2 方案）：status=planned 的纸面实体**不占并发
   预算**（未排产不计和，防"纸面排班"挤掉真实重活），但单实体申报超线仍照查；
3. ``check_e0_trading`` — trading_sensitive 实体 cron 窗落交易时段保守带
   （gate_decision 不放行）→ sched_e0_block（block；E0 纯函数复用，异常/日历未知
   fail-closed）；
4. ``check_pool_concurrency``（2026-09-17 P2-a，v2 方案 C-8 结构盲区治本）→
   sched_pool_concurrency（block）。检查①只查**同组**互斥，于是"同刻不同组"永远结构性
   漏账（实证：sch_c4_exam 与 sch_f06_grid 同 cron ``0 14 * * 6`` 周六 14:00 同秒开工，
   2.0+0.5=2.5GB 并发无一处求和）。本查按 window_expr 展开窗档求交，两判据：
   ①同刻跨组堆积（同 pool、同一起爆时刻、无共享 exclusive_group）；②同池并发内存和超
   mem_ceiling（跨组一律计入）。窗档展开与扫描线求和数学与 check_mem_ceiling 同源
   （``_budget_rows``/``_concurrency_sweep``），R-D 准入同判，池缺席实体不臆造合成池；
5. ``check_truth_drift`` — 生成器重抽 window_expr 与注册表快照比对 →
   sched_truth_drift（warn，防指针失效）。

判定时点纪律（宪法 §3 own-scope）：①"同刻跨组堆积"是**新冲突类**，全仓存量非零
（P3 第一轮重排班的清零对象），故闸只在能归因到本次 staged 变更实体（``focus``，由
``_registry_focus_ids`` 读 staged vs HEAD 注册表算出）时判它，归因失败即跳过并告警
留痕；②"同池内存和超线"与 sched_mem_ceiling 同属预算类（现存全绿）→ 全量判。
``run_all_checks`` 因此**不**并①（视图/告警臂不该因存量债变全红，那会淹掉 P0 建立的
告警链），全仓清单走 ``run_pool_concurrency_audit``（P3 重排班的输入，只读）。

sched_* 理由码清单齐此十二码：``sched_gate_absent``（C-5 E0/闸/闸注册缺席）与
``sched_view_stale``（C-10 视图指纹过期）、``sched_pool_undeclared``（C-7/R-C 幽灵池与
串审计空间维池）、``sched_task_disabled``/``sched_task_missing``/``sched_task_orphan``/
``sched_task_probe_unavailable``（C-15 Windows 计划任务实测差集）七码不由本闸产出——
闸本体缺席时无法自证、注册表也无法自证"声明与操作系统实况一致"，检测者必须独立于被
检测者，故由注册表生成器 ``--check`` 臂产出（本模块仍是清单真源，三处同步由单测锁死）。

runtime 快查（非提交链路）：``runtime_e0_decision(now, is_trading_day, purpose)`` ——
api_server backtest-run 端点接 E0 用的同口径封装。
# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/resource_schedule_gate.yaml
"""

from __future__ import annotations

import importlib.util
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Final

import yaml

logger = logging.getLogger(__name__)

__all__: Final = [
    "make_resource_schedule_gate",
    "expand_windows",
    "check_overlap_group",
    "check_mem_ceiling",
    "check_pool_concurrency",
    "check_e0_trading",
    "check_truth_drift",
    "run_all_checks",
    "run_pool_concurrency_audit",
    "runtime_e0_decision",
    "load_registry_entities",
    "Finding",
    "REASON_OVERLAP",
    "REASON_MEM",
    "REASON_POOL_CONCURRENCY",
    "REASON_E0",
    "REASON_DRIFT",
    "REASON_GATE_ABSENT",
    "REASON_VIEW_STALE",
    "REASON_POOL_UNDECLARED",
    "REASON_TASK_DISABLED",
    "REASON_TASK_MISSING",
    "REASON_TASK_ORPHAN",
    "REASON_TASK_PROBE",
]

GATE_ID: Final = "RESOURCE-SCHEDULE"
REGISTRY_RELPATH: Final = "config/resource_profile_registry.yaml"

REASON_OVERLAP: Final = "sched_overlap_group"
REASON_MEM: Final = "sched_mem_ceiling"
# 第四查理由码（2026-09-17 P2-a，v2 方案 C-8 同刻冲突结构盲区）——**由本闸产出**
# （与下面七个健康码不同：健康码检测的是声明本身可不可信，本码检测的是排班账目数学）
REASON_POOL_CONCURRENCY: Final = "sched_pool_concurrency"
REASON_E0: Final = "sched_e0_block"
REASON_DRIFT: Final = "sched_truth_drift"
# 排产链健康码（2026-09-17 P0，v2 方案 C-5/C-10）——产出方=注册表生成器 --check 臂
# （闸本体缺席时无法自证，检测者必须独立于被检测者）；清单真源仍在本模块。
REASON_GATE_ABSENT: Final = "sched_gate_absent"  # C-5：E0/闸/闸注册缺席（原先静默）
REASON_VIEW_STALE: Final = "sched_view_stale"  # C-10：rw-data.js 内嵌指纹≠注册表现盘指纹
# 排产真值健康码第二批（2026-09-17 P1-a，v2 方案 C-7/C-15）——同样**不由本闸产出**：
# 它们检测的正是"注册表这份声明本身可不可信"，检测者必须在被检测物之外，故由注册表
# 生成器 --check 臂产出；本模块仍是理由码清单真源（告警桥标题/生成器字面量三处同步）。
REASON_POOL_UNDECLARED: Final = "sched_pool_undeclared"  # C-7/R-C：pool 不在执行器真实泳道词表
REASON_TASK_DISABLED: Final = "sched_task_disabled"  # C-15：声明 active 但系统实测 Disabled
REASON_TASK_MISSING: Final = "sched_task_missing"  # C-15：ps1/别名在册但系统查无此任务
REASON_TASK_ORPHAN: Final = "sched_task_orphan"  # C-15：系统里有而表里没有（画像/闸双失明）
REASON_TASK_PROBE: Final = "sched_task_probe_unavailable"  # C-15：schtasks 探针降级（不静默）

# 展开窗档地平线（28 天覆盖月度 cron，如 monthly_static）
HORIZON_DAYS: Final = 28

_DEFAULT_MEM_CEILING_GB: Final = 10.0

_E0_MODULE_CACHE: dict[str, object] = {}
_GEN_MODULE_CACHE: dict[str, object] = {}


@dataclass
class Finding:
    """一条闸 finding：severity=block 硬阻断 / warn 告警放行。"""

    reason_code: str
    severity: str  # block | warn
    task_ids: list[str]
    detail: str
    at: str | None = None  # 冲突时刻（ISO，可空）
    extra: dict = field(default_factory=dict)

    def render(self) -> str:
        return f"[{self.reason_code}/{self.severity}] {'+'.join(self.task_ids)}: {self.detail}" + (
            f"（at={self.at}）" if self.at else ""
        )


# ---------------------------------------------------------------------------
# E0 最小 import 级复用（按文件路径装载，不改 compute_window_gate 任何既有函数）
# ---------------------------------------------------------------------------
def _load_e0_module():
    """按路径装载 scripts/backtest/compute_window_gate.py（单例缓存；异常上抛=fail-closed 由调用方落码）。"""
    if "m" in _E0_MODULE_CACHE:
        return _E0_MODULE_CACHE["m"]
    from zephyr.shared.io.paths import REPO_ROOT

    path = REPO_ROOT / "scripts" / "backtest" / "compute_window_gate.py"
    spec = importlib.util.spec_from_file_location("zephyr_e0_compute_window_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"E0 闸模块装载失败: {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _E0_MODULE_CACHE["m"] = mod
    return mod


def runtime_e0_decision(now: datetime, is_trading_day: bool | None, purpose: str = "resource_schedule") -> dict:
    """运行时 E0 快查（backtest-run 端点同口径）：重活开工前一问，日历未知 fail-closed。"""
    e0 = _load_e0_module()
    return e0.gate_decision(purpose, True, now, is_trading_day)


# ---------------------------------------------------------------------------
# ① cron 展开为窗档区间
# ---------------------------------------------------------------------------
def expand_windows(
    window_expr: str | None,
    est_duration_min: int | None,
    now: datetime,
    horizon_days: int = HORIZON_DAYS,
) -> list[tuple[datetime, datetime]]:
    """cron（'|'-多段，5/6 段 croniter 口径）→ 地平线内 [(start,end)] 区间集。

    est_duration_min 缺席/0（常驻）→ 空表（不参与重叠数学）。
    cron 解析异常上抛（调用方按实体粒度记 finding）。
    """
    if not window_expr or not est_duration_min or est_duration_min <= 0:
        return []
    from zoneinfo import ZoneInfo

    from croniter import croniter

    # 注册表 window_expr 时间语义=北京 wall time（schedule.yaml/ps1 真源口径）——
    # 迭代基准强制归一 Asia/Shanghai（2026-09-16 治本：UTC 基准把周一 03:00 误判为
    # 11:00 盘中，weekend_calibration 误报 sched_e0_block 实证）
    tz = ZoneInfo("Asia/Shanghai")
    now = now.astimezone(tz)
    out: list[tuple[datetime, datetime]] = []
    horizon_end = now + timedelta(days=horizon_days)
    dur = timedelta(minutes=int(est_duration_min))
    for expr in str(window_expr).split("|"):
        expr = expr.strip()
        if not expr:
            continue
        parts = expr.split()
        if len(parts) == 6:
            # 6 段 cron（秒 分 时 日 月 周，如 auction_highfreq "*/10 15-25 9 * * 0-4"）：
            # 结构化排班粒度=分钟，秒段剥离降级为 5 段（croniter 6.2.2 秒段 bands 判定
            # 与 APScheduler 6 段语义不齐，实测 2026-09-16；分钟级窗档对重叠/天花板数学无损）
            expr = " ".join(parts[1:])
        it = croniter(expr, now)
        for _ in range(64):  # 单表达式触发数上限（防 */3 分钟级爆炸；64 步≈28 天月频/日频均够）
            t = it.get_next(datetime)
            if t >= horizon_end:
                break
            out.append((t, t + dur))
    return out


def _eligible(e: dict) -> bool:
    status = str(e.get("status") or "active")
    return status not in ("retired", "orphaned_source")


def _counts_in_budget(e: dict) -> bool:
    """是否占内存并发预算（裁定 R-D，2026-09-17 v2 方案 §3）。

    planned=画像已登记但**未排产**（方案 §8"行为零变更"），31 个纸面实体一起进求和会把
    真实重活的预算挤掉（R-D 原话：防"纸面排班"挤掉真实重活）。故只把它们从**并发和**
    里剔除；单实体申报超线仍照查（那是画像本身的问题，与排没排产无关）。
    """
    return _eligible(e) and str(e.get("status") or "active") != "planned"


# ---------------------------------------------------------------------------
# ② 三检查（纯函数，entities 注入）
# ---------------------------------------------------------------------------
def check_overlap_group(entities: list[dict], now: datetime, horizon_days: int = HORIZON_DAYS) -> list[Finding]:
    """检查①：同 exclusive_group 两任务窗档交叠 → block。"""
    findings: list[Finding] = []
    groups: dict[str, list[dict]] = {}
    for e in entities:
        if not _eligible(e):
            continue
        for g in e.get("exclusive_group") or []:
            groups.setdefault(str(g), []).append(e)
    for g, members in sorted(groups.items()):
        if len(members) < 2:
            continue
        expanded: list[tuple[dict, list[tuple[datetime, datetime]]]] = []
        for e in members:
            tid = str(e.get("task_id"))
            try:
                wins = expand_windows(e.get("window_expr"), e.get("est_duration_min"), now, horizon_days)
            except Exception as exc:  # noqa: BLE001 — cron 解析异常按实体粒度降级 warn
                findings.append(Finding(REASON_OVERLAP, "warn", [tid], f"cron 解析失败跳过时间窗检查: {exc}"))
                continue
            expanded.append((e, wins))
        hit_pairs: set[tuple[str, str]] = set()
        for i in range(len(expanded)):
            for j in range(len(expanded)):
                if i == j:
                    continue
                ea, wa = expanded[i]
                eb, wb = expanded[j]
                pair = tuple(sorted([str(ea["task_id"]), str(eb["task_id"])]))
                if pair in hit_pairs:
                    continue
                for (sa, ea_t) in wa:
                    for (sb, eb_t) in wb:
                        lo, hi = max(sa, sb), min(ea_t, eb_t)
                        if lo < hi:
                            hit_pairs.add(pair)
                            findings.append(
                                Finding(
                                    REASON_OVERLAP,
                                    "block",
                                    list(pair),
                                    f"互斥组 {g} 时间窗交叠",
                                    at=lo.isoformat(),
                                )
                            )
                            break
                    if pair in hit_pairs:
                        break
    return findings


def _mem_ceiling_gb(header: dict | None = None) -> float:
    """mem_ceiling_gb：注册表头部声明优先（引用 reaper _DANGEROUS_MEM_GB 红线），缺省 10.0。"""
    if header:
        v = header.get("mem_ceiling_gb")
        if v is not None:
            return float(v)
    return _DEFAULT_MEM_CEILING_GB


def _budget_rows(
    entities: list[dict], now: datetime, horizon_days: int = HORIZON_DAYS
) -> list[tuple[dict, float, list[tuple[datetime, datetime]]]]:
    """并发账准入行 (实体, 申报 peak_mem_gb, 展开窗档)——检查②与检查④共用同一份数学。

    三条准入/剔除口径**必须**与 check_mem_ceiling 历史行为一致（两套口径=账对不上）：

    * ``_counts_in_budget``：R-D 裁定——retired/orphaned_source 与 planned（纸面未排产）
      一律不占并发预算；
    * ``peak_mem_gb`` 未申报（None，画像缺值）→ 剔除，实测回写后自动纳入；
    * cron 解析异常 → 剔除该实体（重叠检查已按实体粒度记 warn，不在此重复炸账）。

    常驻/event/manual 实体（window_expr 缺席或 est_duration_min≤0）窗档为空表：它们
    **参与本表但无窗**，因此天然不进任何求和（现有实现即如此处置），第四查把它们的申报
    内存另行汇总为该池"常驻基线"（extra.resident_baseline_gb）显影，不掺和窗档账。
    """
    rows: list[tuple[dict, float, list[tuple[datetime, datetime]]]] = []
    for e in entities:
        if not _counts_in_budget(e):
            continue
        mem = e.get("peak_mem_gb")
        if mem is None:
            continue  # 未申报（画像缺值）不参与求和——实测回写后自动纳入
        try:
            wins = expand_windows(e.get("window_expr"), e.get("est_duration_min"), now, horizon_days)
        except Exception:  # noqa: BLE001 — cron 坏实体跳过（重叠检查已 warn）
            continue
        rows.append((e, float(mem), wins))
    return rows


def _concurrency_sweep(
    rows: list[tuple[dict, float, list[tuple[datetime, datetime]]]],
) -> tuple[list[tuple[datetime, frozenset[str]]], dict[str, float]]:
    """扫描线：窗起点 +实体 / 窗终点 −实体 → [(事件时刻, 该刻活跃实体集)] + task_id→内存。

    同一 task_id 多实体时后写覆盖前写（历史行为，注册表 task_id 唯一故不触发）。
    排序键 (time, delta) 使同时刻的"结束"先于"开始"——与 check_mem_ceiling 原实现齐。
    """
    mem_by_id: dict[str, float] = {}
    events: list[tuple[datetime, int, str]] = []
    for (e, mem, wins) in rows:
        tid = str(e.get("task_id"))
        mem_by_id[tid] = mem
        for (s, t) in wins:
            events.append((s, 1, tid))
            events.append((t, -1, tid))
    active: set[str] = set()
    snapshots: list[tuple[datetime, frozenset[str]]] = []
    for (t, delta, tid) in sorted(events, key=lambda x: (x[0], x[1])):
        if delta == 1:
            active.add(tid)
        else:
            active.discard(tid)
        snapshots.append((t, frozenset(active)))
    return snapshots, mem_by_id


def check_mem_ceiling(entities: list[dict], now: datetime, horizon_days: int = HORIZON_DAYS, ceiling_gb: float | None = None) -> list[Finding]:
    """检查②：单实体申报超线或同窗并发内存和超 mem_ceiling → block。"""
    findings: list[Finding] = []
    ceiling = float(ceiling_gb) if ceiling_gb is not None else _mem_ceiling_gb(None)
    for e in entities:
        if not _eligible(e):
            continue
        declared = e.get("peak_mem_gb")
        if declared is not None and float(declared) > ceiling:
            findings.append(
                Finding(
                    REASON_MEM,
                    "block",
                    [str(e.get("task_id"))],
                    f"申报 peak_mem_gb={declared} 超 mem_ceiling_gb={ceiling}（reaper 红线引用，须拆分或降配）",
                )
            )
    # 并发窗求和：事件点扫描（数学单源 _budget_rows+_concurrency_sweep，第四查同源复用）
    # R-D（2026-09-17）：只有排了产的实体占预算——planned 纸面实体不参与并发和（见 _counts_in_budget）
    # 口径提示：本查**不分池**（全仓一股脑求和），分池归口账见 check_pool_concurrency（C-8）
    snapshots, mem_by_id = _concurrency_sweep(_budget_rows(entities, now, horizon_days))
    reported: set[frozenset[str]] = set()
    for (t, active) in snapshots:
        total = sum(mem_by_id.get(a, 0.0) for a in active)
        if total > ceiling:
            if active in reported:
                continue
            reported.add(active)
            findings.append(
                Finding(
                    REASON_MEM,
                    "block",
                    sorted(active),
                    f"同窗并发内存和 {total:.1f}GB > mem_ceiling_gb={ceiling}",
                    at=t.isoformat(),
                )
            )
    return findings


def _shares_group(a: dict, b: dict) -> bool:
    """两实体是否共享任一 exclusive_group（共享=已有互斥账，交叠由 check_overlap_group 记）。"""
    return bool(set(a.get("exclusive_group") or []) & set(b.get("exclusive_group") or []))


def _hit_focus(ids, focus: set[str] | None) -> bool:
    """own-scope 过滤（宪法 §3）：focus=None=全量判；否则须命中本次变更实体才报。"""
    return focus is None or bool(set(ids) & set(focus))


def check_pool_concurrency(
    entities: list[dict],
    now: datetime,
    horizon_days: int = HORIZON_DAYS,
    ceiling_gb: float | None = None,
    focus: set[str] | None = None,
    pileup: bool = True,
) -> list[Finding]:
    """检查④（v2 C-8 结构盲区治本）：同 pool 并发按窗档求交，跨组同刻一律记账 → block。

    check_overlap_group 的互斥组数学只看**同组**，所以"同刻不同组"在既有三查里结构性
    不存在：实证 sch_c4_exam（heavy 池，exclusive_group=[mine_vs_exam]）与 sch_f06_grid
    （heavy 池，无组）同 cron ``0 14 * * 6`` 周六 14:00 同秒开工，2.0+0.5=2.5GB 并发
    全仓无一处求和。

    两判据（同用 REASON_POOL_CONCURRENCY，窗档展开/扫描线求和数学与 check_mem_ceiling 同源）：

    ① **同刻跨组堆积**：同 pool、窗档起点同一瞬间 ≥2 实体、且两者无共享 exclusive_group
       —— 它们必然同时抢同一条泳道，而互斥账上零记录；合法出口=错峰或声明互斥；
    ② **同池并发内存和超线**：同 pool 扫描线活跃集（≥2 实体）申报 peak_mem_gb 之和
       > mem_ceiling_gb —— 跨组同样计入（check_mem_ceiling 不分池，本判据是它的**分池
       归口**账）。

    参数口径：

    * ``pool`` 未声明的实体整条剔除——臆造"合成池"等于给执行器不存在的泳道记账，池缺席
      是 ``sched_pool_undeclared``（生成器 --check 臂，C-7/R-C）的账，不在此越权；
    * 常驻/event/manual 实体（无窗档）不进 ①② 求和（与 check_mem_ceiling 历史口径一致），
      其申报内存另汇总为该池 ``resident_baseline_gb`` 随 finding 显影——基线可见，不冒充窗档；
    * ``focus``：own-scope 归因集（本次 staged 变更实体），非 None 时只报命中集内实体的
      finding——全仓存量债不连坐本提交人（宪法 §3）；
    * ``pileup=False``：跳过判据①，只判预算类判据②。闸在**归因失败**（非 git 通道）时用
      它——①是新冲突类、存量非零（P3 清零对象），无归因即全量判=连坐；②是预算类、存量
      全绿，归因失败也不放松（保守面不窄）。

    窗口展开走 ``expand_windows``（croniter）：注册表 window_expr 已是生成器归一后的
    标准 cron（0=周日，APScheduler dow 0=周一 的映射在生成器=映射层），闸侧再归一即
    两套口径——故只复用，不另写解析（同 cron_convention 头部声明）。
    """
    ceiling = float(ceiling_gb) if ceiling_gb is not None else _mem_ceiling_gb(None)
    rows = _budget_rows(entities, now, horizon_days)

    members_by_pool: dict[str, list[tuple[dict, float, list[tuple[datetime, datetime]]]]] = {}
    resident_baseline: dict[str, float] = {}
    for (e, mem, wins) in rows:
        pool = str(e.get("pool") or "").strip()
        if not pool:
            continue  # 未挂池=不判（见 docstring 口径）
        if not wins:
            resident_baseline[pool] = resident_baseline.get(pool, 0.0) + mem
            continue  # 常驻/event/manual：无窗档可求交
        members_by_pool.setdefault(pool, []).append((e, mem, wins))

    findings: list[Finding] = []
    for pool, members in sorted(members_by_pool.items()):
        base = round(resident_baseline.get(pool, 0.0), 2)
        mem_of = {str(e.get("task_id")): mem for (e, mem, _w) in members}

        # ── 判据①：同刻跨组堆积（跨组同秒开工，互斥账上零记录）──
        if pileup:
            by_instant: dict[datetime, list[dict]] = {}
            for (e, _mem, wins) in members:
                for (s, _t) in wins:
                    by_instant.setdefault(s, []).append(e)
            seen_pairs: set[tuple[str, str]] = set()
            for t, group in sorted(by_instant.items(), key=lambda x: x[0]):
                if len(group) < 2:
                    continue
                for i in range(len(group)):
                    for j in range(i + 1, len(group)):
                        a, b = group[i], group[j]
                        ta, tb = str(a.get("task_id")), str(b.get("task_id"))
                        if ta == tb:
                            continue
                        pair = tuple(sorted([ta, tb]))
                        if pair in seen_pairs or _shares_group(a, b):
                            continue  # 同组=check_overlap_group 的账，不在此重复记
                        seen_pairs.add(pair)
                        if not _hit_focus(pair, focus):
                            continue
                        pair_mem = mem_of.get(ta, 0.0) + mem_of.get(tb, 0.0)
                        findings.append(
                            Finding(
                                REASON_POOL_CONCURRENCY,
                                "block",
                                list(pair),
                                f"池 {pool} 同刻跨组并发 {pair_mem:.1f}GB：{ta}+{tb} 同秒开工"
                                f"（该刻同池 {len(group)} 实体）且无共享 exclusive_group"
                                "——三查只记同组互斥账，跨组同刻是 C-8 结构盲区；错峰或声明互斥",
                                at=t.isoformat(),
                                extra={
                                    "pool": pool,
                                    "kind": "same_instant_cross_group",
                                    "concurrent_mem_gb": round(pair_mem, 2),
                                    "instant_entity_count": len(group),
                                    "resident_baseline_gb": base,
                                },
                            )
                        )

        # ── 判据②：同池并发内存和超 mem_ceiling（跨组一律计入的分池归口账）──
        snapshots, mem_by_id = _concurrency_sweep(members)
        reported: set[frozenset[str]] = set()
        for (t, active) in snapshots:
            if len(active) < 2:
                continue  # 单实体超线=check_mem_ceiling 的申报超线账，不双开
            total = sum(mem_by_id.get(a, 0.0) for a in active)
            if total <= ceiling or active in reported:
                continue
            reported.add(active)
            if not _hit_focus(active, focus):
                continue
            findings.append(
                Finding(
                    REASON_POOL_CONCURRENCY,
                    "block",
                    sorted(active),
                    f"池 {pool} 同窗并发内存和 {total:.1f}GB > mem_ceiling_gb={ceiling}"
                    "（跨互斥组同样计入，须错峰或降配）",
                    at=t.isoformat(),
                    extra={
                        "pool": pool,
                        "kind": "pool_mem_sum",
                        "concurrent_mem_gb": round(total, 2),
                        "resident_baseline_gb": base,
                    },
                )
            )
    return findings


def check_e0_trading(entities: list[dict], now: datetime) -> list[Finding]:
    """检查③：trading_sensitive 实体 cron 窗开工未过 E0 → block（异常 fail-closed）。

    逐窗交易日判定（结构校验口径，不查 CH 日历）：周末=非交易日（A 股周六日休市
    恒真）；工作日=保守按交易日（节假日误报方向=偏严，符合 fail-closed 保守面）。
    """
    findings: list[Finding] = []
    try:
        e0 = _load_e0_module()
        for e in entities:
            if not _eligible(e) or not bool(e.get("trading_sensitive")):
                continue
            try:
                wins = expand_windows(e.get("window_expr"), e.get("est_duration_min"), now)
            except Exception as exc:  # noqa: BLE001 — cron 坏=无法自证清白，fail-closed
                findings.append(
                    Finding(REASON_E0, "block", [str(e.get("task_id"))], f"交易敏感实体 cron 解析失败（fail-closed）: {exc}")
                )
                continue
            for (s, _t) in wins:
                is_td = s.weekday() < 5  # 结构口径：工作日保守按交易日，周末恒休市
                decision = e0.gate_decision(str(e.get("task_id")), True, s, is_td)
                if not decision.get("allowed"):
                    findings.append(
                        Finding(
                            REASON_E0,
                            "block",
                            [str(e.get("task_id"))],
                            f"交易敏感实体窗档开工未过 E0（reason={decision.get('reason_code')}）——改排休市日/盘后",
                            at=s.isoformat(),
                            extra={"e0_reason": decision.get("reason_code")},
                        )
                    )
                    break
    except Exception as exc:  # noqa: BLE001 — E0 装载/调用异常=fail-closed（宁停不裸奔）
        findings.append(Finding(REASON_E0, "block", ["<e0_module>"], f"E0 闸不可用（fail-closed）: {exc}"))
    return findings


def check_truth_drift(entities: list[dict], repo_root: Path | None = None) -> list[Finding]:
    """检查⑤：生成器重抽 window_expr/window_type 与注册表快照比对 → warn（防指针失效）。"""
    findings: list[Finding] = []
    gen = _load_generator_module(repo_root)
    if gen is None:
        return [Finding(REASON_DRIFT, "warn", ["<generator>"], "生成器模块不可装载，漂移检测跳过")]
    ps1_ents, w1 = gen.parse_ps1_entities()
    slot_ents, w2 = gen.parse_schedule_slots()
    fresh: dict[str, dict] = {}
    for e in list(ps1_ents) + list(slot_ents):
        fresh[str(e.get("task_id"))] = e
    for w in list(w1) + list(w2):
        findings.append(Finding(REASON_DRIFT, "warn", ["<truth_source>"], f"真源抽取告警: {w}"))
    for e in entities:
        if not _eligible(e):
            continue
        tid = str(e.get("task_id"))
        f = fresh.get(tid)
        if f is None:
            continue  # 手动/事件实体无机器真源（种子真源=方案文档），漂移检测不适用
        for k in ("window_expr", "window_type"):
            if str(e.get(k)) != str(f.get(k)):
                findings.append(
                    Finding(REASON_DRIFT, "warn", [tid], f"真源漂移 {k}: 注册表={e.get(k)!r} 真源重抽={f.get(k)!r}")
                )
    return findings


def _load_generator_module(repo_root: Path | None = None):
    """按路径装载注册表生成器（漂移检测复用其抽取函数——单抽取真源防克隆）。"""
    key = str(repo_root or "")
    if key in _GEN_MODULE_CACHE:
        return _GEN_MODULE_CACHE[key]
    root = repo_root
    if root is None:
        try:
            from zephyr.shared.io.paths import REPO_ROOT as R

            root = Path(R)
        except Exception:  # noqa: BLE001
            return None
    path = root / "scripts" / "governance" / "generators" / "generate_resource_profile_registry.py"
    if not path.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location("zephyr_resched_profile_generator", path)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _GEN_MODULE_CACHE[key] = mod
        return mod
    except Exception:  # noqa: BLE001 — 生成器装载失败降级（漂移检测 warn）
        logger.warning("resource_schedule_gate: 生成器装载失败", exc_info=True)
        return None


# ---------------------------------------------------------------------------
# 注册表读取 + 全量检查
# ---------------------------------------------------------------------------
def load_registry_entities(path: str | Path) -> tuple[list[dict], dict]:
    """读注册表 → (实体清单, 注册表头部)。损坏抛 yaml.YAMLError（fail-closed 由 gate 落码）。"""
    p = Path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return list(data.get("entities") or []), data


def run_all_checks(
    registry_path: str | Path,
    now: datetime,
    horizon_days: int = HORIZON_DAYS,
) -> list[Finding]:
    """全量检查（三检查 block + 漂移 warn）。供 commit gate/视图生成器/告警桥复用。

    第四查 ``check_pool_concurrency`` **有意不入本函数**：其"同刻跨组堆积"判据是 v2 C-8
    新开的冲突类，全仓存量非零（正是 P3 第一轮重排班的清零对象）。折进本函数=周历视图与
    ops 告警链一夜全红，把 P0 刚建立的"闸→告警→promotion"信号淹成噪声；闸侧按 own-scope
    只判本次变更实体，全仓清单另走 ``run_pool_concurrency_audit``（只读，P3 输入）。
    P3 清零后并入即一行（判据②本与 sched_mem_ceiling 同性质，随时可并）。
    """
    entities, header = load_registry_entities(registry_path)
    ceiling = _mem_ceiling_gb(header)
    out: list[Finding] = []
    out.extend(check_overlap_group(entities, now, horizon_days))
    out.extend(check_mem_ceiling(entities, now, horizon_days, ceiling_gb=ceiling))
    out.extend(check_e0_trading(entities, now))
    out.extend(check_truth_drift(entities))
    return out


def run_pool_concurrency_audit(
    registry_path: str | Path,
    now: datetime,
    horizon_days: int = HORIZON_DAYS,
) -> list[Finding]:
    """全仓同池并发账（只读，无归因过滤）：sched_pool_concurrency 存量清单真源。

    消费方=P3 重排班的输入（"冲突数 N→0"的 N 从这里数）与 ops/晨审的可选体检；**不经**
    run_all_checks（理由见其 docstring）。并进视图/告警桥只需把本函数输出传给
    publish_findings（桥的映射按 reason_code 通用，零改动）。
    """
    entities, header = load_registry_entities(registry_path)
    return check_pool_concurrency(entities, now, horizon_days, ceiling_gb=_mem_ceiling_gb(header))


# 参与并发账的注册表字段（own-scope 归因比对键）：改这些=改并发账；改 notes_zh/module_id/
# map_node_id 之类不改账（备注修订不该替存量债背锅）
_POOL_ACCOUNTING_FIELDS: Final = ("pool", "window_expr", "est_duration_min", "peak_mem_gb", "exclusive_group", "status")


def _registry_focus_ids(gateway, registry_path: str | Path, entities: list[dict]) -> set[str] | None:
    """本次 staged 相对 HEAD **新增/账目变更**的实体 task_id（第四查 own-scope 归因）。

    返回 None=无法归因（非 git 提交通道/无 gateway/index 里读不到该文件/YAML 解析失败）
    ——调用方据此把"同刻跨组堆积"降级跳过（不连坐，宪法 §3），预算类判据仍全量。
    注册表在 HEAD 无版本（整文件新增）→ staged 全部实体都是新增=全量归因。
    """
    if gateway is None or not hasattr(gateway, "run_git"):
        return None
    try:
        from zephyr.gov_enforcement.commit_gates._diff_helpers import _read_head_file, _read_staged_file

        rel = _registry_relpath(registry_path)
        if not rel:
            return None
        staged_text = _read_staged_file(gateway, rel)
        if staged_text is None:
            return None  # staged 副本读不到=无从归因（磁盘面可能是别人未暂存的工作区）
        staged_recs = _accounting_records(staged_text)
        head_text = _read_head_file(gateway, rel)
        if head_text is None:
            return set(staged_recs) or {str(e.get("task_id")) for e in entities}
        head_recs = _accounting_records(head_text)
        return {tid for tid, rec in staged_recs.items() if head_recs.get(tid) != rec}
    except Exception:  # noqa: BLE001 — 归因失败退化为 None（保守面：跳过新冲突类，不连坐）
        logger.debug("RESOURCE-SCHEDULE: 排班变更实体归因失败（非 git 通道？）", exc_info=True)
        return None


def _registry_relpath(path: str | Path) -> str | None:
    """任意注册表路径 → git 仓内相对正斜杠路径（``git show :<rel>`` 口径）。"""
    try:
        from zephyr.shared.io.paths import REPO_ROOT

        p = Path(path)
        try:
            rel = p.resolve().relative_to(Path(REPO_ROOT).resolve())
        except ValueError:
            rel = Path(str(path).replace("\\", "/"))
        s = str(rel).replace("\\", "/")
        if s.startswith("./"):
            s = s[2:]
        return s or None
    except Exception:  # noqa: BLE001 — REPO_ROOT 不可得=无从归因
        return None


def _accounting_records(text: str) -> dict[str, tuple]:
    """注册表 YAML 文本 → {task_id: 并发账字段元组}（比对键见 _POOL_ACCOUNTING_FIELDS）。"""
    data = yaml.safe_load(text) or {}
    out: dict[str, tuple] = {}
    for e in data.get("entities") or []:
        out[str(e.get("task_id"))] = tuple(repr(e.get(k)) for k in _POOL_ACCOUNTING_FIELDS)
    return out


# ---------------------------------------------------------------------------
# GateSpec（own-scope：仅 staged 命中注册表时触发）
# ---------------------------------------------------------------------------
def make_resource_schedule_gate():
    """构造排班冲突检测 GateSpec（own-scope：自有 staged 全量检查；外来 staged 降级 warn 不阻断）。"""
    from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        if not files:
            return True, ""
        def _is_reg(f: str) -> bool:
            norm = str(f).replace("\\", "/")
            return norm.endswith(REGISTRY_RELPATH) or norm.endswith("/resource_profile_registry.yaml")

        triggered = [f for f in files if _is_reg(f)]
        if not triggered:
            return True, ""
        # own-scope 判定（宪法 §3：own-diff 作用域；外来 staged 违规 warn+审计，不阻断无辜提交人）
        own_scope = True
        try:
            from zephyr.gov_enforcement.commit_gates._diff_helpers import _build_own_scope

            session_id = kwargs.get("session_id") or getattr(gateway, "_current_session_id", None)
            scope = _build_own_scope(gateway, files, session_id)
            own_scope = scope is None or any(_is_reg(f) for f in (scope or set()))
        except Exception:  # noqa: BLE001 — own-scope 判定失败退化为全量（保守面不变窄）
            logger.debug("RESOURCE-SCHEDULE: own-scope 判定退化", exc_info=True)
        path = triggered[0]
        try:
            entities, header = load_registry_entities(path)
        except Exception as exc:  # noqa: BLE001 — 注册表损坏=fail-closed
            return False, f"{GATE_ID}: 注册表解析异常（fail-closed，库损坏须先修）: {exc}"
        from datetime import timezone

        now = datetime.now(timezone.utc)
        findings: list[Finding] = []
        findings.extend(check_overlap_group(entities, now))
        findings.extend(check_mem_ceiling(entities, now))
        findings.extend(check_e0_trading(entities, now))
        # 第四查（C-8 同池并发账）：own-scope 归因。判据①"同刻跨组堆积"是新冲突类，
        # 全仓存量非零（P3 第一轮重排班清零对象）——只在能归因到本次变更实体时判，
        # 无归因即全量判=让本提交人替存量债背锅（宪法 §3 禁连坐）；判据②"同池内存和超线"
        # 属预算类（与 sched_mem_ceiling 同性质，现存全绿），归因失败也照判=保守面不窄。
        focus = _registry_focus_ids(gateway, path, entities)
        if focus is None:
            logger.warning(
                "%s: 排班变更实体不可归因（非 git 提交通道？）——同刻跨组堆积判据本轮跳过，同池内存和判据照跑",
                GATE_ID,
            )
        findings.extend(
            check_pool_concurrency(
                entities,
                now,
                ceiling_gb=_mem_ceiling_gb(header),
                focus=focus,
                pileup=focus is not None,
            )
        )
        blocks = [f for f in findings if f.severity == "block"]
        warns = [f for f in findings if f.severity == "warn"]
        if not own_scope:
            # 外来 staged：降级 warn+审计（owner 责任制，不阻断本提交人）
            for f in blocks:
                logger.warning("%s foreign-staged warn: %s", GATE_ID, f.render())
            return True, ""
        for w in warns:
            logger.warning("%s warn: %s", GATE_ID, w.render())
        if blocks:
            detail = "; ".join(f.render() for f in blocks[:10])
            return False, f"{GATE_ID}: {len(blocks)} 条阻断级排班冲突——{detail}"
        return True, ""

    return GateSpec(gate_id=GATE_ID, check=_check, priority=144)


def _fetch_trading_day_safe(now: datetime) -> bool | None:
    """E0 日历查询（失败返回 None → 检查③ fail-closed，不炸 gate 本体）。"""
    try:
        e0 = _load_e0_module()
        return e0.fetch_is_trading_day(now.date())
    except Exception:  # noqa: BLE001 — 日历通道不可达 → None
        return None
