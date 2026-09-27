# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md | §3
# [MODULE] scripts.backup.library_ledger_backup
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); zephyr.library.snapshot_store (备份成功尾步刷快照，懒加载)
# [CONSUMERS] schtasks ZephyrAlpha_LibraryLedgerBackup/ZephyrAlpha_LibraryLedgerDrill; scripts/register_library_ledger_backup_task.ps1
# [STARTUP] scheduled_task
# [MATURITY] production
# [INVARIANTS] 全程只读 PG（get_depgraph_pg_connection 默认 read_only）；备份=双链落位（G:/backup 主 + F:/zephyr_cold 镜像）；滚动保留 30 天且每月 1 日留档不清；恢复演练=纯 Python CSV 流式核验（零 PG 写、零裸 duckdb）产出 PASS/FAIL 报告；快照刷新挂 backup 成功尾步（既有 schtasks 事件链，零新增计划任务）且 fail-open——快照故障不得改备份退出码
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达/双链任一盘不可写均非零退出；镜像盘失败不阻断主链落位（manifest 记 degraded）
# [TESTS] tests/scripts/backup/test_library_ledger_backup.py
# [A_module] module_id=MOD-INF-043 | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""library_ledger_backup.py — 图书馆 PG 账本双链备份+月度恢复演练（12 号令任务 2）。

覆盖 lib_assets / lib_events 两表（backup_pg_architecture 19 张架构真源表之外的业务
资产账本）。落位遵循 INFRA-STORE-003 存储分工：备份总仓 G:/backup（主链）+ 冷库
F:/zephyr_cold（镜像链）。调度走 schtasks（系统级调度，reaper keep 登记放行），
恢复演练=备份 CSV 读回核验（行数+抽样字段比对），不写 PG、不依赖 pg_dump。

Usage::

    python scripts/backup/library_ledger_backup.py backup          # 每日备份
    python scripts/backup/library_ledger_backup.py drill           # 月度恢复演练
    python scripts/backup/library_ledger_backup.py drill --date 20260924
    python scripts/backup/library_ledger_backup.py status          # 巡检视图
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable, Final

_SCRIPT_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
if str(_SCRIPT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_SCRIPT_ROOT / "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

LIB_TABLES: Final[tuple[str, ...]] = ("lib_assets", "lib_events")
PRIMARY_ROOT: Final[Path] = Path("G:/backup/db_dumps/library")
MIRROR_ROOT: Final[Path] = Path("F:/zephyr_cold/library")
RETENTION_DAYS: Final[int] = 30
DRILL_SAMPLE_ROWS: Final[int] = 50
SQL_COPY_TABLE: Final[dict[str, str]] = {t: f"COPY {t} TO STDOUT WITH (FORMAT csv, HEADER true)" for t in LIB_TABLES}
DRILL_REPORT_KEYS: Final[tuple[str, ...]] = ("date", "source", "verdict", "checks")


def _utc_now() -> datetime:
    return datetime.now().astimezone()


def _day_dir(root: Path, day: str) -> Path:
    return root / day


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _dump_table_csv(table: str, out_path: Path, conn) -> int:
    """COPY 单表到 gzip CSV，返回行数（不含表头）。"""
    rows = 0
    with gzip.open(out_path, "wt", encoding="utf-8", newline="") as fh:
        cur = conn.cursor()
        copy_sql = SQL_COPY_TABLE[table]
        cur.copy_expert(copy_sql, fh)
        rows = getattr(cur, "rowcount", 0) or 0
    return max(rows, 0)


def run_backup(
    conn_factory: Callable[[], object] | None = None,
    primary_root: Path = PRIMARY_ROOT,
    mirror_root: Path = MIRROR_ROOT,
    now: datetime | None = None,
) -> dict:
    """备份两表到双链，返回 manifest dict（含 degraded 镜像态）。"""
    now = now or _utc_now()
    day = now.strftime("%Y%m%d")
    conn_factory = conn_factory or get_depgraph_pg_connection
    primary_dir = _day_dir(primary_root, day)
    primary_dir.mkdir(parents=True, exist_ok=True)
    mirror_dir = _day_dir(mirror_root, day)

    conn = conn_factory()
    manifest: dict = {"date": day, "created_at": now.isoformat(), "tables": {}, "degraded": []}
    try:
        for table in LIB_TABLES:
            out_path = primary_dir / f"{table}.csv.gz"
            rows = _dump_table_csv(table, out_path, conn)
            manifest["tables"][table] = {"rows": rows, "sha256": _sha256_file(out_path)}
    finally:
        conn.close()

    manifest_path = primary_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    try:
        mirror_dir.mkdir(parents=True, exist_ok=True)
        for item in primary_dir.iterdir():
            shutil.copy2(item, mirror_dir / item.name)
    except OSError as exc:
        manifest["degraded"].append(f"mirror:{exc}")

    _prune_old_backups(primary_root)
    if mirror_root.exists() and not manifest["degraded"]:
        _prune_old_backups(mirror_root)
    print(json.dumps(manifest, ensure_ascii=False))
    return manifest


def _is_monthly_pin(day: str) -> bool:
    return day.endswith("01")


def _prune_old_backups(root: Path) -> None:
    """滚动清理：保留近 RETENTION_DAYS 天；每月 1 日目录留档不清。"""
    cutoff = _utc_now().date().toordinal() - RETENTION_DAYS
    for entry in root.iterdir():
        if not entry.is_dir() or len(entry.name) != 8 or not entry.name.isdigit():
            continue
        if _is_monthly_pin(entry.name):
            continue
        day_ord = datetime.strptime(entry.name, "%Y%m%d").date().toordinal()
        if day_ord < cutoff:
            shutil.rmtree(entry, ignore_errors=True)


def _load_manifest(day_dir: Path) -> dict:
    return json.loads((day_dir / "manifest.json").read_text(encoding="utf-8"))


def run_drill(
    day: str | None = None,
    primary_root: Path = PRIMARY_ROOT,
    report_root: Path | None = None,
    keepgoing: bool = False,
) -> dict:
    """恢复演练：读回备份 CSV 核验（行数+抽样行完整），出 PASS/FAIL 报告。

    纯 Python 流式解析（零 PG 写、零裸 duckdb.connect），报告落 report_root。
    """
    now = _utc_now()
    day = day or max((p.name for p in primary_root.iterdir() if p.is_dir()), default="")
    report_root = report_root or (_SCRIPT_ROOT / ".runtime" / "tmp" / "library_drill")
    report_root.mkdir(parents=True, exist_ok=True)
    day_dir = _day_dir(primary_root, day)
    checks: list[dict] = []
    verdict = "PASS"

    if not (day_dir / "manifest.json").exists():
        verdict = "FAIL"
        checks.append({"check": "manifest", "ok": False, "detail": f"missing {day_dir}/manifest.json"})
    else:
        manifest = _load_manifest(day_dir)
        for table in LIB_TABLES:
            spec = manifest["tables"].get(table)
            gz_path = day_dir / f"{table}.csv.gz"
            if not spec or not gz_path.exists():
                verdict = "FAIL"
                checks.append({"check": f"{table}:present", "ok": False, "detail": "missing backup file"})
                continue
            actual_sha = _sha256_file(gz_path)
            sha_ok = actual_sha == spec["sha256"]
            rows, header = _count_csv_rows(gz_path)
            rows_ok = rows == spec["rows"]
            sample_ok, sample_detail = _sample_csv_rows(gz_path, DRILL_SAMPLE_ROWS)
            checks.append({"check": f"{table}:sha256", "ok": sha_ok, "detail": actual_sha[:16]})
            checks.append({"check": f"{table}:rows", "ok": rows_ok, "detail": f"{rows} vs {spec['rows']}"})
            checks.append({"check": f"{table}:sample", "ok": sample_ok, "detail": sample_detail})
            if not (sha_ok and rows_ok and sample_ok):
                verdict = "FAIL"
                if not keepgoing:
                    break

    report = {"date": day, "source": str(day_dir), "verdict": verdict, "checks": checks}
    report_path = report_root / f"drill_report_{day}.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in DRILL_REPORT_KEYS}, ensure_ascii=False))
    if verdict != "PASS":
        raise SystemExit(4)
    return report


def _count_csv_rows(gz_path: Path) -> tuple[int, list[str]]:
    with gzip.open(gz_path, "rt", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader, [])
        return sum(1 for _ in reader), header


def _sample_csv_rows(gz_path: Path, n: int) -> tuple[bool, str]:
    """抽样核验：头部 n 行每行列数与表头一致且首列（asset_id/event_id）非空。"""
    with gzip.open(gz_path, "rt", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader, [])
        if not header:
            return False, "empty header"
        for i, row in enumerate(reader):
            if i >= n:
                break
            if len(row) != len(header):
                return False, f"row {i}: {len(row)} cols vs {len(header)}"
            if not row[0]:
                return False, f"row {i}: empty first column"
    return True, f"head {n} rows ok"


def run_status(primary_root: Path = PRIMARY_ROOT, mirror_root: Path = MIRROR_ROOT) -> dict:
    days = sorted(p.name for p in primary_root.iterdir() if p.is_dir()) if primary_root.exists() else []
    latest = {}
    if days:
        latest = _load_manifest(_day_dir(primary_root, days[-1]))
    out = {
        "primary_days": len(days),
        "latest_day": days[-1] if days else None,
        "latest_tables": {k: v.get("rows") for k, v in latest.get("tables", {}).items()},
        "mirror_present": mirror_root.exists(),
        "latest_drill": _latest_drill_verdict(),
    }
    print(json.dumps(out, ensure_ascii=False))
    return out


def _latest_drill_verdict() -> str | None:
    report_root = _SCRIPT_ROOT / ".runtime" / "tmp" / "library_drill"
    reports = sorted(report_root.glob("drill_report_*.json"))
    if not reports:
        return None
    return json.loads(reports[-1].read_text(encoding="utf-8")).get("verdict")


def _refresh_snapshot_quietly() -> dict:
    """备份成功尾步刷本地快照（S3 案 A：搭既有 schtasks 事件链，零新增计划任务）。

    fail-open：快照层任何异常（含 R1 世代指纹件未落地、磁盘不可写）只记 stderr 警告，
    不改备份退出码——快照是可派生镜像非真源，炸了不影响备份双链落位语义。
    """
    try:
        from zephyr.library.snapshot_store import refresh_snapshot  # noqa: PLC0415 — 懒加载：备份链不背 pyarrow 依赖

        result = refresh_snapshot()
    except Exception as exc:  # noqa: BLE001 — fail-open 明文豁免：快照非真源，禁连坐备份链
        print(f"[snapshot][warn] 快照刷新失败（不影响备份）：{type(exc).__name__}: {exc}", file=sys.stderr)
        return {"status": "failed", "reason": f"{type(exc).__name__}: {exc}"}
    print(f"[snapshot] {json.dumps(result, ensure_ascii=False)}", file=sys.stderr)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="图书馆 PG 账本双链备份+恢复演练")
    parser.add_argument("command", choices=["backup", "drill", "status"])
    parser.add_argument("--date", default=None, help="[drill] 指定演练日期 YYYYMMDD（默认最新）")
    args = parser.parse_args(argv)
    if args.command == "backup":
        run_backup()
        _refresh_snapshot_quietly()  # 双链落位成功=事件；fail-open 不改退出码
    elif args.command == "drill":
        run_drill(day=args.date)
    else:
        run_status()
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  schtasks ZephyrAlpha_LibraryLedgerBackup/Drill 系统级调度触发，非人工手动
    raise SystemExit(main())
