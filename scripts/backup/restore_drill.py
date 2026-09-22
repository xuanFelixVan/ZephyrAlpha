# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure/blueprint.md | §restore_drill
# [MODULE] scripts.backup.restore_drill
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.shared.infra.process_pool (run_subprocess_hidden); zephyr.shared.io.paths (REPO_ROOT)
# [CONSUMERS] schtasks 月度计划任务（ZEPHYR-RESTORE-DRILL，登记 process_reaper_keep）；DR 演练台账 logs/restore_drill_*.json
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 演练库=depgraph_drill（临时库，演练完 DROP，绝不触碰生产 depgraph 库）；只读核行数（lib_assets/lib_events/nodes 三表 live vs drill 对账）；报告 JSON 落 logs/；凭据走 config/.env.postgres（RULE-SECRETS 管道，禁硬编码）；pg_restore 不可达时报告 failed 并退出 1（fail-visible）
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 恢复/核数失败写 failed 报告后退出 1；临时库确保清理（finally DROP IF EXISTS）
# [TESTS] tests/backup/test_restore_drill.py
# [A_module] module_id=MOD-INF-043 | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 月度恢复演练 CLI 由 ZEPHYR-RESTORE-DRILL schtasks 月度事件触发，人工直跑为兜底形态，非常驻
"""restore_drill.py — depgraph 账本月度恢复演练（ulib3 T2）。

取最新 depgraph.dump → pg_restore 到临时库 depgraph_drill → lib_assets/lib_events/nodes
三表行数与生产对账 → 报告落 logs/restore_drill_YYYYMMDD.json → DROP 临时库。
Owner 裁定=月度自动演练（备份不只存，要能还原）；drill 结果不入账，人工阅。

Usage::

    python scripts/backup/restore_drill.py [--dump <path>]
# [ALGO_FLOW] external: docs/03_modules/_domain_infrastructure/algo_flow/restore_drill.yaml
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from zephyr.shared.infra.process_pool import run_subprocess_hidden
from zephyr.shared.io.paths import REPO_ROOT

__all__ = ["run_drill"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定

_DRILL_DB = "depgraph_drill"
_TABLES = ("lib_assets", "lib_events", "nodes")
_DUMP_GLOB = "G:/backup/db_dumps/**/depgraph.dump"

# psql -c 语句集中化（§5.160.2）：psql 子进程调用面，SQL 文本模块级常量（表名变参走 format）
_SQL_COUNT_ROWS = "SELECT count(*) FROM {}"
_SQL_DROP_DRILL_DB = "DROP DATABASE IF EXISTS " + _DRILL_DB
_SQL_CREATE_DRILL_DB = "CREATE DATABASE " + _DRILL_DB

#: .env.postgres 缺省时的默认连接用户（PostgreSQL 出厂默认管理员名，非凭证）
_DEFAULT_PG_USER = "postgres"


def _pg_creds() -> tuple[str, str]:
    """从 config/.env.postgres 读 (user, password)（RULE-SECRETS 管道）。"""
    user, password = _DEFAULT_PG_USER, ""
    env_file = REPO_ROOT / "config/.env.postgres"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("POSTGRES_USER="):
                user = line.split("=", 1)[1].strip()
            elif line.startswith("POSTGRES_PASSWORD="):
                password = line.split("=", 1)[1].strip()
    return user, password


def _pg_bin(name: str) -> str:
    """定位 pg_dump/psql/pg_restore（PATH 优先，回退 Program Files 最新版本）。"""
    found = None
    try:
        found = name if os.path.basename(name) else None
    except Exception:  # noqa: BLE001
        found = None
    for base in (r"C:\Program Files\PostgreSQL",):
        root = Path(base)
        if root.is_dir():
            versions = sorted((int(p.name) for p in root.iterdir() if p.name.isdigit()), reverse=True)
            for v in versions:
                exe = root / str(v) / "bin" / name
                if exe.exists():
                    return str(exe)
    return name


def _find_latest_dump(explicit: str | None) -> Path | None:
    if explicit:
        p = Path(explicit)
        return p if p.exists() else None
    root = Path("G:/backup/db_dumps")
    candidates = sorted(root.glob("**/depgraph.dump"), key=lambda p: p.stat().st_mtime, reverse=True) if root.exists() else []
    return candidates[0] if candidates else None


def _count_rows(host: str, user: str, password: str, db: str, table: str, psql: str) -> int:
    env = {**os.environ, "PGPASSWORD": password}
    r = run_subprocess_hidden(
        [psql, "-h", host, "-U", user, "-d", db, "-t", "-A", "-c", _SQL_COUNT_ROWS.format(table)],
        capture_output=True, text=True, env=env, timeout=120,
    )
    if r.returncode != 0:
        raise RuntimeError(f"count {db}.{table} failed: {r.stderr[:200]}")
    return int((r.stdout or "0").strip() or 0)


def run_drill(dump_path: str | None = None, host: str = "localhost") -> dict:
    """执行一次恢复演练，返回报告 dict（含 rows 对账与 pass 判定）。"""
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    user, password = _pg_creds()
    psql, pg_restore = _pg_bin("psql.exe"), _pg_bin("pg_restore.exe")
    dump = _find_latest_dump(dump_path)
    report: dict = {"started_at": started, "drill_db": _DRILL_DB, "dump": str(dump) if dump else None, "status": "failed"}
    if dump is None:
        report["error"] = "未找到 depgraph.dump（检查 G:/backup/db_dumps 或 --dump）"
        return report
    env = {**os.environ, "PGPASSWORD": password}
    try:
        run_subprocess_hidden(
            [psql, "-h", host, "-U", user, "-d", "postgres", "-c", _SQL_DROP_DRILL_DB],
            capture_output=True, text=True, env=env, timeout=120, check=True,
        )
        run_subprocess_hidden(
            [psql, "-h", host, "-U", user, "-d", "postgres", "-c", _SQL_CREATE_DRILL_DB],
            capture_output=True, text=True, env=env, timeout=120, check=True,
        )
        r = run_subprocess_hidden(
            [pg_restore, "-h", host, "-U", user, "-d", _DRILL_DB, "--no-owner", str(dump)],
            capture_output=True, text=True, env=env, timeout=1800,
        )
        report["pg_restore_rc"] = r.returncode
        rows: dict[str, dict[str, int]] = {}
        for t in _TABLES:
            live = _count_rows(host, user, password, "depgraph", t, psql)
            try:
                drill = _count_rows(host, user, password, _DRILL_DB, t, psql)
            except Exception:  # noqa: BLE001 — 演练库缺表（旧 dump）记 -1
                drill = -1
            rows[t] = {"live": live, "drill": drill, "match": drill == live}
        report["rows"] = rows
        report["pass"] = all(v["match"] for v in rows.values())
        report["status"] = "passed" if report["pass"] else "row_mismatch"
    except Exception as exc:  # noqa: BLE001 — fail-visible 报告后退出
        report["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        try:
            run_subprocess_hidden(
                [psql, "-h", host, "-U", user, "-d", "postgres", "-c", _SQL_DROP_DRILL_DB],
                capture_output=True, text=True, env=env, timeout=120,
            )
            report["drill_db_dropped"] = True
        except Exception:  # noqa: BLE001 — 清理失败留痕
            report["drill_db_dropped"] = False
    return report


def main() -> int:
    """CLI 入口：跑演练+落报告，pass=0 否则 1。"""
    parser = argparse.ArgumentParser(description="depgraph 账本月度恢复演练（ulib3 T2）")
    parser.add_argument("--dump", default=None, help="指定 dump 路径（默认 G:/backup/db_dumps 最新）")
    args = parser.parse_args()
    report = run_drill(args.dump)
    out = REPO_ROOT / "logs" / f"restore_drill_{time.strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"restore drill status={report['status']} pass={report.get('pass')} report={out}")
    return 0 if report.get("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
