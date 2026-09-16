# [BLUEPRINT] MOD-RESCHED-GATE | docs/03_modules/_cross_layer/resource_schedule_gate/blueprint.md | §
# [MODULE] zephyr.gov_enforcement.commit_gates.resource_schedule_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] croniter; yaml; scripts/backtest/compute_window_gate.py（E0 classify_window/gate_decision
#   纯函数最小 import 级复用，不改其既有函数）; scripts/governance/generators/generate_resource_profile_registry.py
#   （真源抽取函数复用，防克隆）
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway（经 in_process_gate_registry.yaml 注册）;
#   scripts/governance/generators/generate_resource_week_view.py（冲突标注复用检查函数）;
#   zephyr.infrastructure.system_telemetry.alerts.resource_schedule_alerts（findings→告警桥）;
#   tests/governance/commit_gates/test_resource_schedule_gate.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 结构校验型闸（登记时/提交时），不是运行时调度器;
#   own-scope——仅 staged 命中 config/resource_profile_registry.yaml 时触发;
#   互斥组重叠/内存天花板/申报超线=硬阻断；真源漂移=warn 不阻断（防指针失效告警）;
#   E0 复用 classify_window/gate_decision 纯函数，异常/日历未知 fail-closed;
#   cron 解析异常=该实体跳时间窗检查并记 finding（不炸整闸）;
#   理由码沿用 E0 风格：sched_overlap_group/sched_mem_ceiling/sched_e0_block
#   +sched_truth_drift（本闸）+sched_gate_absent/sched_view_stale（排产链健康码，
#   由注册表生成器 --check 臂产出——检测者须独立于被检测的闸本体）
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

资源排班全景四件套之"闸"（方案 §2.3）。三个检查+漂移检测，作用时点=登记时/提交时
结构校验（对齐 FACTORY-MAP gate 范式），不是运行时调度器：

1. ``check_overlap_group`` — 同 exclusive_group 两任务时间窗交叠（window_expr cron
   展开+est_duration_min 区间数学）→ sched_overlap_group（block）；
2. ``check_mem_ceiling`` — 同窗并发 peak_mem_gb 之和 > mem_ceiling_gb（引用
   reaper _DANGEROUS_MEM_GB=10 红线，勿收编）→ sched_mem_ceiling（block）；单实体
   申报超线同拦；
3. ``check_e0_trading`` — trading_sensitive 实体 cron 窗落交易时段保守带
   （gate_decision 不放行）→ sched_e0_block（block；E0 纯函数复用，异常/日历未知
   fail-closed）；
4. ``check_truth_drift`` — 生成器重抽 window_expr 与注册表快照比对 →
   sched_truth_drift（warn，防指针失效）。

sched_* 理由码清单齐此六码：后两码 ``sched_gate_absent``（C-5 E0/闸/闸注册缺席）
与 ``sched_view_stale``（C-10 视图指纹过期）不由本闸产出——闸本体缺席时无法自证，
检测者必须独立于被检测者，故由注册表生成器 ``--check`` 臂产出。

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
    "check_e0_trading",
    "check_truth_drift",
    "run_all_checks",
    "runtime_e0_decision",
    "load_registry_entities",
    "Finding",
    "REASON_OVERLAP",
    "REASON_MEM",
    "REASON_E0",
    "REASON_DRIFT",
    "REASON_GATE_ABSENT",
    "REASON_VIEW_STALE",
]

GATE_ID: Final = "RESOURCE-SCHEDULE"
REGISTRY_RELPATH: Final = "config/resource_profile_registry.yaml"

REASON_OVERLAP: Final = "sched_overlap_group"
REASON_MEM: Final = "sched_mem_ceiling"
REASON_E0: Final = "sched_e0_block"
REASON_DRIFT: Final = "sched_truth_drift"
# 排产链健康码（2026-09-17 P0，v2 方案 C-5/C-10）——产出方=注册表生成器 --check 臂
# （闸本体缺席时无法自证，检测者必须独立于被检测者）；清单真源仍在本模块。
REASON_GATE_ABSENT: Final = "sched_gate_absent"  # C-5：E0/闸/闸注册缺席（原先静默）
REASON_VIEW_STALE: Final = "sched_view_stale"  # C-10：rw-data.js 内嵌指纹≠注册表现盘指纹

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
    # 并发窗求和：事件点扫描（窗起点+mem/窗终点-mem，扫描线求活跃和）
    events: list[tuple[datetime, int, float]] = []
    entity_ids = sorted({str(e.get("task_id")) for e in entities if _eligible(e)})
    id_mem: dict[str, float] = {}
    id_wins: dict[str, list[tuple[datetime, datetime]]] = {}
    for e in entities:
        if not _eligible(e):
            continue
        mem = e.get("peak_mem_gb")
        if mem is None:
            continue  # 未申报（画像缺值）不参与求和——实测回写后自动纳入
        tid = str(e.get("task_id"))
        try:
            wins = expand_windows(e.get("window_expr"), e.get("est_duration_min"), now, horizon_days)
        except Exception:  # noqa: BLE001 — cron 坏实体跳过（重叠检查已 warn）
            continue
        id_mem[tid] = float(mem)
        id_wins[tid] = wins
        for (s, t) in wins:
            events.append((s, 1, tid))
            events.append((t, -1, tid))
    reported: set[frozenset[str]] = set()
    active: set[str] = set()
    for (t, delta, tid) in sorted(events, key=lambda x: (x[0], x[1])):
        if delta == 1:
            active.add(tid)
        else:
            active.discard(tid)
        total = sum(id_mem.get(a, 0.0) for a in active)
        if total > ceiling:
            key = frozenset(active)
            if key in reported:
                continue
            reported.add(key)
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
    """检查④：生成器重抽 window_expr/window_type 与注册表快照比对 → warn（防指针失效）。"""
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
    """全量检查（三检查 block + 漂移 warn）。供 commit gate/视图生成器/告警桥复用。"""
    entities, header = load_registry_entities(registry_path)
    ceiling = _mem_ceiling_gb(header)
    out: list[Finding] = []
    out.extend(check_overlap_group(entities, now, horizon_days))
    out.extend(check_mem_ceiling(entities, now, horizon_days, ceiling_gb=ceiling))
    out.extend(check_e0_trading(entities, now))
    out.extend(check_truth_drift(entities))
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
