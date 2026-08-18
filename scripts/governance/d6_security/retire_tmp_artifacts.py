# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/retire_tmp_artifacts.py | §
# [MODULE] scripts.governance.d6_security.retire_tmp_artifacts
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d6_security.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 默认 dry-run（--apply 才删除）；保留 .gitkeep/*.lock/活跃运行日志；清理四类目标：tmp/根层 + pg_backups/depgraph_*(排除受保护前缀) + logs/顶层(backup_report_*.json+*.log) + tmp/子目录(data_gap_check/startup_backup_* 过期)；不删 runtime_backups/pg_backups/.jsonl
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 0=无清理项或清理完成；1=发现待清理项(dry-run)；2=error
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
retire_tmp_artifacts — tmp/ + logs/ 退役区 TTL 执行器（AI-03 审计 P2/P3 治本）

治本 #ARCH-TTL-DOC-001 / AI-03 审计 P2+P3：
  tmp/ 为 task_bound 一次性脚本退役区（.gitignore + EXCLUDE_DIRS 双重豁免），
  但此前无退役执行器，文件无限堆积（审计时 298 MB）。logs/backup_report_*.json
  无保留策略（179 MB）。本脚本按 mtime 阈值执行 TTL 退役，建立有界保留。

触发模型（对齐 scan_secret_leak.py / detect_secrets.py）：
  [STARTUP] manual——人工或 CI 批量兜底调用；非时间驱动（无 cron/Timer/sleep-loop）。

保留（绝不删除）：
  - tmp/.gitkeep（维持目录结构）
  - tmp/*.lock（活跃锁：scheduler.lock / tick_subscriber.lock）
  - tmp/scheduler* / tmp/tick_subscriber*（活跃运行日志，由产生方自行轮转）
  - tmp/ 子目录内容（runtime_backups/ 由 backup_runtime_state.py max_backups 自管理不动；
    data_gap_check/ + startup_backup_*/ 由 --subdir-days 整目录过期清理，AI-03 S1 治本）

清理目标（四类）：
  1. tmp/ 根层任务产物（.py/.txt/.md/.json/.html/.js/.csv），mtime > --tmp-days（默认 7）
  2. tmp/pg_backups/depgraph_*.json，保留最新 --pg-keep 个（默认 10），删余；
     排除受保护人工备份（depgraph_pre_*/depgraph_pinned_*，AI-03 S3）
  3. logs/ 顶层过期文件（backup_report_*.json + *.log），mtime > --logs-days（默认 14）；
     不动子目录（auto_fix/mcp_audit 等审计目录）与 .jsonl（追加型审计流，由产生方管理）
  4. tmp/ 子目录（data_gap_check/ + startup_backup_*/），整目录最新 mtime > --subdir-days
     （默认 14）；runtime_backups/ 由 backup_runtime_state.py 自管理不动（AI-03 S1）

用法：
  python scripts/governance/d6_security/retire_tmp_artifacts.py            # dry-run，列出待删
  python scripts/governance/d6_security/retire_tmp_artifacts.py --apply     # 执行删除
  python scripts/governance/d6_security/retire_tmp_artifacts.py --tmp-days 3 --pg-keep 5
"""

__manifest__ = """
args: []
description: retire_tmp_artifacts — tmp/ + logs/ 退役区 TTL 执行器（AI-03 审计 P2/P3 治本）
dimensions:
- D6
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import shutil
import sys
import time
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import (  # noqa: E402
    EXIT_ERROR,
    EXIT_FINDINGS,
    EXIT_PASS,
    PROTECTED_PG_BACKUP_PREFIXES,
    REPO_ROOT,
)
from _shared.encoding import ensure_utf8_stdout  # noqa: E402

ensure_utf8_stdout()

TMP_DIR = REPO_ROOT / "tmp"
PG_BACKUPS_DIR = TMP_DIR / "pg_backups"
LOGS_DIR = REPO_ROOT / "logs"

# 保留：活跃运行日志前缀（产生方自行轮转，不由本脚本清理）
_ACTIVE_PREFIXES = ("scheduler", "tick_subscriber")
# 保留：目录占位与锁文件
_KEEP_NAMES = {".gitkeep"}
_KEEP_SUFFIXES = (".lock",)
# tmp/ 根层可清理的扩展名（任务产物；.log 受 _ACTIVE_PREFIXES 保护，仅清理非活跃 .log）
_TMP_CLEAN_EXTS = (".py", ".txt", ".md", ".json", ".html", ".js", ".csv", ".log")

# S3（AI-03 审计）：受保护的人工安全备份前缀（如 depgraph_pre_RSK_rollback_*）。
# 真源收敛至 _shared.constants.PROTECTED_PG_BACKUP_PREFIXES（原本地副本已删除，禁止重定义）。
# 此类备份由人工/repair 脚本一次性产生，排除出 keep-N 退役计数——
# 保留策略与 backup_runtime_state.py._is_protected_backup 同源（真源唯一）。

# S1（AI-03 审计）：tmp/ 子目录过期清理配置。
# runtime_backups/ 由 backup_runtime_state.py max_backups 自管理（此处不动，防双重清理）；
# pg_backups/ 由 collect_pg_backups_excess 单独处理；__pycache__ 跳过。
# data_gap_check/ + startup_backup_*/ 为一次性调查/快照目录，整目录最新 mtime 过期则清理。
_TMP_SUBDIR_DAYS_DEFAULT = 14


def _is_protected_pg_backup(name: str) -> bool:
    """判定 pg 备份是否为受保护人工安全备份（排除出 keep-N 退役计数）。

    S3（AI-03 审计）：前缀真源为 _shared.constants.PROTECTED_PG_BACKUP_PREFIXES
    （与 backup_runtime_state._is_protected_backup 同源，禁止本地重定义）。
    """
    return name.startswith(PROTECTED_PG_BACKUP_PREFIXES)


def _is_protected(name: str) -> bool:
    """活跃锁 / .gitkeep / 活跃运行日志 → 保留。"""
    if name in _KEEP_NAMES:
        return True
    if name.endswith(_KEEP_SUFFIXES):
        return True
    return name.startswith(_ACTIVE_PREFIXES)


def collect_tmp_root_stale(tmp_days: int) -> list[Path]:
    """tmp/ 根层过期任务产物（mtime > tmp_days），排除受保护文件与子目录。"""
    cutoff = time.time() - tmp_days * 86400
    stale: list[Path] = []
    if not TMP_DIR.is_dir():
        return stale
    for p in TMP_DIR.iterdir():
        if not p.is_file():
            continue  # 跳过子目录（pg_backups 等单独处理）
        if _is_protected(p.name):
            continue
        if p.suffix not in _TMP_CLEAN_EXTS:
            continue
        try:
            mtime = p.stat().st_mtime
        except OSError:
            continue
        if mtime < cutoff:
            stale.append(p)
    return stale


def collect_pg_backups_excess(pg_keep: int) -> list[Path]:
    """pg_backups/depgraph_*.json 保留最新 pg_keep 个，返回待删余量。

    S3（AI-03 审计）：受保护人工安全备份（depgraph_pre_*/depgraph_pinned_*）
    排除出 keep-N 退役计数——其保留由 backup_runtime_state.py 独立管理（真源唯一），
    本脚本不删除受保护备份，防回滚安全快照被自动退役丢失。
    """
    if not PG_BACKUPS_DIR.is_dir() or pg_keep < 0:
        return []
    files = [
        p
        for p in PG_BACKUPS_DIR.iterdir()
        if p.is_file()
        and p.name.startswith("depgraph_")
        and p.suffix == ".json"
        and not _is_protected_pg_backup(p.name)
    ]
    files.sort(key=lambda p: p.stat().st_mtime)
    if len(files) <= pg_keep:
        return []
    return files[: len(files) - pg_keep]


def collect_tmp_subdir_stale(subdir_days: int) -> list[Path]:
    """tmp/ 子目录过期清理（AI-03 S1）：data_gap_check/ + startup_backup_*/ 整目录过期。

    病根：原 retire_tmp_artifacts 显式"runtime_backups/data_gap_check 不动"，
    导致 data_gap_check/（一次性调查脚本）+ startup_backup_*/（一次性快照）永久堆积无界。

    边界（防双重清理 / 防误删）：
      - runtime_backups/ 由 backup_runtime_state.py max_backups 自管理 → 跳过
      - pg_backups/ 由 collect_pg_backups_excess 单独处理 → 跳过
      - __pycache__ → 跳过
      - 仅清理 data_gap_check/ 与 startup_backup_* 日期目录
      - 整目录最新文件 mtime > subdir_days 才清理（任一文件活跃则保留整目录）
    """
    cutoff = time.time() - subdir_days * 86400
    stale: list[Path] = []
    if not TMP_DIR.is_dir():
        return stale
    for p in TMP_DIR.iterdir():
        if not p.is_dir():
            continue
        if p.name in ("runtime_backups", "pg_backups", "__pycache__"):
            continue  # 自管理 / 单独处理
        if not (p.name == "data_gap_check" or p.name.startswith("startup_backup_")):
            continue
        try:
            mtimes = [f.stat().st_mtime for f in p.rglob("*") if f.is_file()]
        except OSError:
            continue
        if not mtimes:
            continue  # 空目录不在此处理（避免误删占位）
        if max(mtimes) < cutoff:
            stale.append(p)
    return stale


def collect_logs_stale(logs_days: int) -> list[Path]:
    """logs/ 顶层过期文件（backup_report_*.json + *.log），mtime > logs_days。

    不动子目录（auto_fix/mcp_audit 等审计目录）与 .jsonl（tamper_evident/pipeline_audit
    追加型审计流）——这些由各自产生方管理。
    """
    cutoff = time.time() - logs_days * 86400
    stale: list[Path] = []
    if not LOGS_DIR.is_dir():
        return stale
    for p in LOGS_DIR.iterdir():
        if not p.is_file():
            continue
        is_backup_report = p.name.startswith("backup_report_") and p.suffix == ".json"
        is_log = p.suffix == ".log"
        if not (is_backup_report or is_log):
            continue
        try:
            mtime = p.stat().st_mtime
        except OSError:
            continue
        if mtime < cutoff:
            stale.append(p)
    return stale


def _gather(
    tmp_days: int, pg_keep: int, logs_days: int, subdir_days: int
) -> dict[str, list[Path]]:
    """_gather implementation."""
    return {
        "tmp_root": collect_tmp_root_stale(tmp_days),
        "pg_backups": collect_pg_backups_excess(pg_keep),
        "logs_stale": collect_logs_stale(logs_days),
        "tmp_subdir": collect_tmp_subdir_stale(subdir_days),
    }


def _total_size(paths: list[Path]) -> int:
    """_total_size implementation."""
    total = 0
    for p in paths:
        try:
            total += p.stat().st_size
        except OSError:
            pass
    return total


def _fmt_size(n: int) -> str:
    """_fmt_size implementation."""
    if n >= 1_048_576:
        return f"{n / 1_048_576:.1f} MB"
    if n >= 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n} B"


def _rel(p: Path) -> str:
    """_rel implementation."""
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(
        description="tmp/ + logs/ 退役区 TTL 执行器（AI-03 P2/P3 治本，默认 dry-run）",
    )
    parser.add_argument("--apply", action="store_true", help="执行删除（默认 dry-run 仅列出）")
    parser.add_argument("--tmp-days", type=int, default=7, help="tmp/ 根层文件保留天数（默认 7）")
    parser.add_argument("--pg-keep", type=int, default=10, help="pg_backups/depgraph_*.json 保留份数（默认 10）")
    parser.add_argument("--logs-days", type=int, default=14, help="logs/顶层(backup_report_*.json+*.log) 保留天数（默认 14）")
    parser.add_argument(
        "--subdir-days",
        type=int,
        default=_TMP_SUBDIR_DAYS_DEFAULT,
        help="tmp/ 子目录(data_gap_check/startup_backup_*)整体过期天数（AI-03 S1，默认 14）",
    )
    args = parser.parse_args()

    plan = _gather(args.tmp_days, args.pg_keep, args.logs_days, args.subdir_days)
    grand_count = sum(len(v) for v in plan.values())
    grand_bytes = sum(_total_size(v) for v in plan.values())

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"=== retire_tmp_artifacts [{mode}] ===")
    print(
        f"阈值: tmp_root>{args.tmp_days}d | pg_backups keep {args.pg_keep} | "
        f"logs_stale>{args.logs_days}d | tmp_subdir>{args.subdir_days}d"
    )
    for label, paths in plan.items():
        sz = _total_size(paths)
        unit = "item(s)" if label == "tmp_subdir" else "file(s)"
        print(f"  [{label}] {len(paths)} {unit}, {_fmt_size(sz)}")
        for p in paths:
            print(f"      - {_rel(p)}")
    print(f"合计: {grand_count} item(s), {_fmt_size(grand_bytes)}")

    if not args.apply:
        if grand_count > 0:
            print("\n[dry-run] 待清理项已列出。确认后加 --apply 执行。")
            return EXIT_FINDINGS
        print("\n[dry-run] 无待清理项。")
        return EXIT_PASS

    # --apply 真删（tmp_subdir 为目录用 rmtree，其余为文件用 unlink）
    deleted = 0
    errors: list[str] = []
    for label, paths in plan.items():
        for p in paths:
            try:
                if label == "tmp_subdir":
                    shutil.rmtree(p, ignore_errors=False)
                else:
                    p.unlink()
                deleted += 1
            except OSError as e:
                errors.append(f"{_rel(p)}: {e}")
    print(f"\n[apply] 已删除 {deleted}/{grand_count} item(s)。")
    if errors:
        print(f"[apply] {len(errors)} 个错误：")
        for e in errors:
            print(f"      ! {e}")
        return EXIT_ERROR
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
