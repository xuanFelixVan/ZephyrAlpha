# [BLUEPRINT] MOD-GOV-DS | docs/_working/total_command_closeout/10_wave_plan.md | 波 3.2/3.3/W-102
# [MODULE] scripts.governance.data_supply.supply_sources
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.data.progress_store, pyyaml
# [CONSUMERS] scripts.governance.data_supply.false_green_crosscheck; scripts.governance.data_supply.supply_conservation; scripts.governance.data_supply.check_wave3_rulers
# [STARTUP] imported
# [MATURITY] testing
# create-guard-not-dup: 死车道抢救件（字节代投非新能力），与canonical同名能力无职责重叠，逐词误报批量豁免（st-chief7-20260928 第12+轮实测均为关键词巧合命中）
# [TTL] permanent
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 真源文件缺失/为空 -> raise MissingSourceError（判据类读数禁静默降级）; ledger 空 -> 返回 () 由尺判红
# [A_module] module_id=MOD-GOV-DS-SOURCES | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [INVARIANTS] 只读取证不改生产状态；输出机生禁手改；计数以现读为准禁照抄册面旧数；探测失败必报红不得静默降级
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [TESTS] 案卷内附命令原文与实测读数，可复算
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
# noqa: m02-manual  M02豁免: 本件为一次性 CLI 判据装载器，无 while True / 无常驻线程
"""Declaration-side loaders — every reading is *derived* from an existing SSOT host.

内收纪律（Z-16「禁造第二套」/ 波 3.3「内收不造第二套」）：本件不新建任何阈值册，
只从三个既有真源派生判据输入：

  1. ``src/zephyr/data/config/tasks.yaml``            任务→目标表/业务日列/上游依赖
  2. ``src/zephyr/data/config/data_supply_sentinel.yaml``  表侧新鲜度腿（宿主 zephyr.data.supply_sentinel）
  3. ``src/zephyr/data/config/known_data_gaps.yaml``   已登记缺口台账（宿主 zephyr.data.backfill_checker）

记账侧（回执）复用既有宿主 ``zephyr.data.progress_store.ProgressStore``，禁在本件散写 SQL。
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml

_DATA_CONFIG_DIR = "src/zephyr/data/config"
_TASKS_FILE = "tasks.yaml"
_SENTINEL_FILE = "data_supply_sentinel.yaml"
_GAPS_FILE = "known_data_gaps.yaml"
_LEDGER_FILENAME = "integrator_progress.db"


class MissingSourceError(RuntimeError):
    def __init__(self, msg: str, *, details: dict | None = None):
        super().__init__(msg)
        self.details = details or {}

    """声明侧真源缺失/为空——判据类读数禁把"读不到"当成"没有声明"（W-180 红线）。"""


@dataclass(frozen=True)
class DataSupplyTaskSpec:
    """One declared supply task (SSOT = tasks.yaml)."""

    task_id: str
    table: str
    date_col: str
    upstream: tuple[str, ...] = ()
    disabled: bool = False
    schedule: str = ""


@dataclass(frozen=True)
class SentinelLeg:
    """One freshness leg declared for the existing supply sentinel host."""

    table: str
    date_col: str
    max_lag_days: int
    past_only: bool = False
    cadence: str = "incremental"
    allow_empty: bool = False
    gap_id: str = ""


@dataclass(frozen=True)
class LedgerRun:
    """One ``task_runs`` receipt row (host = zephyr.data.progress_store)."""

    run_id: int
    task_id: str
    status: str
    started_at: dt.datetime | None
    finished_at: dt.datetime | None
    rows_fetched: int | None
    rows_written: int | None


def repo_root_from(start: Path) -> Path:
    """Walk up until the data config dir is found (lane worktree or main tree)."""
    cur = start.resolve()
    for cand in (cur, *cur.parents):
        if (cand / _DATA_CONFIG_DIR / _TASKS_FILE).is_file():
            return cand
    raise MissingSourceError(f"未从 {start} 向上找到 {_DATA_CONFIG_DIR}/{_TASKS_FILE}")


def _load_yaml(path: Path, *, label: str) -> Any:
    if not path.is_file():
        raise MissingSourceError(f"{label} 真源缺失", details={"path": str(path)})
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if payload is None:
        raise MissingSourceError(f"{label} 真源为空文件（读不到 != 无声明）", details={"path": str(path)})
    return payload


def _disabled_flag(entry: dict[str, Any]) -> bool:
    extra = entry.get("extra")
    if isinstance(extra, dict):
        return bool(extra.get("disabled"))
    return False


def load_task_specs(root: Path) -> dict[str, DataSupplyTaskSpec]:
    """task_id -> DataSupplyTaskSpec, derived from tasks.yaml (no second registry)."""
    path = root / _DATA_CONFIG_DIR / _TASKS_FILE
    entries = _load_yaml(path, label="tasks.yaml")
    tasks = entries.get("tasks") if isinstance(entries, dict) else entries
    if not isinstance(tasks, list):
        raise MissingSourceError("tasks.yaml 顶层 tasks 列表缺失/形态异常")
    specs: dict[str, DataSupplyTaskSpec] = {}
    for entry in tasks:
        if not isinstance(entry, dict) or not entry.get("task_id"):
            continue
        deps = entry.get("dependencies") or ()
        specs[str(entry["task_id"])] = DataSupplyTaskSpec(
            task_id=str(entry["task_id"]),
            table=str(entry.get("table") or ""),
            date_col=str(entry.get("date_col") or ""),
            upstream=tuple(str(d) for d in deps),
            disabled=_disabled_flag(entry),
            schedule=str(entry.get("schedule") or ""),
        )
    if not specs:
        raise MissingSourceError("tasks.yaml 解析后零任务声明")
    return specs


def build_downstream_map(specs: dict[str, DataSupplyTaskSpec]) -> dict[str, tuple[str, ...]]:
    """Invert tasks.yaml ``dependencies`` -> task_id : direct downstream tasks."""
    down: dict[str, set[str]] = {}
    for spec in specs.values():
        for up in spec.upstream:
            down.setdefault(up, set()).add(spec.task_id)
    return {k: tuple(sorted(v)) for k, v in down.items()}


def downstream_closure(
    task_id: str, downstream: dict[str, tuple[str, ...]], specs: dict[str, DataSupplyTaskSpec]
) -> tuple[str, ...]:
    """All tasks transitively fed by ``task_id`` (names them for downgrade)."""
    seen: set[str] = set()
    frontier = list(downstream.get(task_id, ()))
    while frontier:
        nxt = frontier.pop()
        if nxt in seen:
            continue
        seen.add(nxt)
        frontier.extend(downstream.get(nxt, ()))
    return tuple(sorted(seen))


def downstream_tables(
    task_id: str, downstream: dict[str, tuple[str, ...]], specs: dict[str, DataSupplyTaskSpec]
) -> tuple[str, ...]:
    tables = {specs[t].table for t in downstream_closure(task_id, downstream, specs) if t in specs}
    return tuple(sorted(x for x in tables if x))


def load_sentinel_legs(root: Path) -> dict[str, list[SentinelLeg]]:
    """table -> legs, derived from the existing supply sentinel config."""
    path = root / _DATA_CONFIG_DIR / _SENTINEL_FILE
    entries = _load_yaml(path, label="data_supply_sentinel.yaml")
    raw = entries.get("tables") if isinstance(entries, dict) else None
    if not isinstance(raw, list) or not raw:
        raise MissingSourceError("data_supply_sentinel.yaml 的 tables 腿清单缺失/为空")
    legs: dict[str, list[SentinelLeg]] = {}
    for entry in raw:
        if not isinstance(entry, dict) or not entry.get("table"):
            continue
        table = str(entry["table"])
        legs.setdefault(table, []).append(
            SentinelLeg(
                table=table,
                date_col=str(entry.get("date_col") or ""),
                max_lag_days=int(entry.get("max_lag_days") or 0),
                past_only=bool(entry.get("past_only")),
                cadence=str(entry.get("cadence") or "incremental"),
                allow_empty=bool(entry.get("allow_empty")),
                gap_id=str(entry.get("gap_id") or ""),
            )
        )
    return legs


_GAP_ENTRY_LIST_KEY = "gaps"
#: 已申报且仍生效的状态才可为缺数背书；completed/resolved 表示缺口已补，不得再拿来放行。
_DECLARE_COVERING = frozenset({"accepted", "open", "in_progress", "monitoring", "deferred", "deferred_source"})
_NO_COVER = frozenset({"completed", "resolved", "fixed", "closed"})


def _iter_gap_entries(payload: Any) -> Iterable[dict[str, Any]]:
    raw = payload.get(_GAP_ENTRY_LIST_KEY) if isinstance(payload, dict) else None
    if not isinstance(raw, list):
        return ()
    return (item for item in raw if isinstance(item, dict))


def load_declared_gap_index(root: Path) -> dict[str, list[dict[str, Any]]]:
    """table -> registered gap entries (host = known_data_gaps.yaml).

    空台账是合法状态（没有已知缺口），因此这里 **不** 抛 MissingSourceError；
    但文件缺失/非映射形态/缺 ``gaps`` 键必须抛——"读不到"绝不能变成"全部判未申报"。
    """
    payload = _load_yaml(root / _DATA_CONFIG_DIR / _GAPS_FILE, label="known_data_gaps.yaml")
    if not isinstance(payload, dict) or _GAP_ENTRY_LIST_KEY not in payload:
        raise MissingSourceError("known_data_gaps.yaml 缺 gaps 键（读不到 != 无申报）")
    index: dict[str, list[dict[str, Any]]] = {}
    for entry in _iter_gap_entries(payload):
        table = str(entry.get("table") or "")
        if table:
            index.setdefault(table, []).append(entry)
    return index


def gap_covers(gaps: list[dict[str, Any]], table: str, day: dt.date) -> bool:
    """Whether a *still-effective* registered gap declares ``table``/``day`` as known-missing.

    真源字段（known_data_gaps.yaml 实测形态）：``table`` / ``gap_type`` / ``start_date`` /
    ``end_date``（null=至今开放）/ ``status``。completed/resolved 的旧缺口不再背书。
    """
    for entry in gaps or []:
        if str(entry.get("table") or "") != table:
            continue
        if str(entry.get("status") or "").lower() in _NO_COVER:
            continue
        if str(entry.get("status") or "").lower() not in _DECLARE_COVERING:
            continue
        if _day_in_entry(entry, day):
            return True
    return False


def _day_in_entry(entry: dict[str, Any], day: dt.date) -> bool:
    lo = _parse_date(str(entry.get("start_date") or ""))
    end = entry.get("end_date")
    if end in (None, "", "null"):
        return bool(lo) and day >= lo  # 开放至今
    hi = _parse_date(str(end))
    if lo and hi:
        return lo <= day <= hi
    return bool(lo) and day >= lo


def _parse_date(text: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(text[:10])
    except (ValueError, TypeError):
        return None


def default_ledger_path(root: Path) -> Path:
    """Same location the host itself uses (``ProgressStore`` 默认 = REPO_ROOT/data/...)."""
    return root / "data" / _LEDGER_FILENAME


def open_progress_store(root: Path, db_path: Path | None = None):
    """Return the existing ProgressStore host for an **already present** ledger.

    ⚠ 禁让宿主顺手建库：``ProgressStore.__init__`` 会 mkdir + connect，路径不存在时
    就地建出 0 字节库——那正是 1A.5 点名的"死库"病因。故本件先验存在性，缺失即抛。
    """
    from zephyr.data.progress_store import get_store

    target = db_path or default_ledger_path(root)
    if not Path(target).is_file():
        raise MissingSourceError(
            "记账台账不存在（禁由判据侧建库；判据读数失败必抛）",
            details={"target": str(target)},
        )
    return get_store(target)


def load_ledger_runs(store: Any, *, since: dt.datetime | None, limit: int = 5000) -> tuple[LedgerRun, ...]:
    """Read recent ``task_runs`` receipts through the host API (no raw SQL here)."""
    rows = store.list_recent_runs(limit=limit) or []
    out: list[LedgerRun] = []
    for row in rows:
        started = _as_datetime(row.get("started_at"))
        if since is not None and started is not None and started < since:
            continue
        out.append(
            LedgerRun(
                run_id=int(row.get("run_id") or 0),
                task_id=str(row.get("task_id") or ""),
                status=str(row.get("status") or ""),
                started_at=started,
                finished_at=_as_datetime(row.get("finished_at")),
                rows_fetched=_as_int(row.get("rows_fetched")),
                rows_written=_as_int(row.get("rows_written")),
            )
        )
    return tuple(out)


def _as_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_datetime(value: Any) -> dt.datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, dt.datetime):
        return value if value.tzinfo else value.replace(tzinfo=dt.timezone.utc)
    text = str(value).strip().replace("Z", "+00:00").replace(" ", "T", 1)
    try:
        parsed = dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=dt.timezone.utc)


def utc_date_of(moment: dt.datetime | None) -> dt.date | None:
    """Business-day anchor of a UTC timestamp (task_runs stores UTC ISO)."""
    return moment.date() if moment is not None else None
