# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/backup_runtime_state.py | §
# [MODULE] scripts.governance.meta.backup_runtime_state
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.meta.__init__; zephyr.governance.depgraph_schema (_build_pg_dsn, backup_pg_architecture 函数)
# [CONSUMERS] scripts.governance.apply_depgraph/apply_battle_map/apply_decisiongraph/apply_dataflowgraph (backup_pg_architecture 事件触发入口); tests/dr/test_restore_from_backup.py
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/dr/test_restore_from_backup.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
backup_runtime_state.py — 运行时状态备份（蓝图 §33 灾备）

DEPRECATED（ARCH-041）：git history 已是 yaml/jsonl 文件真源（directory_contract L740），
物理快照违反真源唯一原则。本脚本默认输出路径已从 meta/_backups/（deprecated）改为
tmp/runtime_backups/（临时目录，不进 git）。

PG 架构库备份已实现（ARCH-041 §5.33.1 治本 v2 扩展）：backup_pg_architecture() 函数，
覆盖四图 19 张 DB 真源表（depgraph 11 + battle_map 3 + decisiongraph 2 + dataflowgraph 3）。
触发方式：apply_depgraph/apply_battle_map/apply_decisiongraph/apply_dataflowgraph
成功修改架构数据后自动调用（事件触发）。

.runtime/ handoffs+reconcile_reports 备份已实现（5.33.7 治本）：backup_runtime_handoffs()
函数。.runtime/ 被 .gitignore 整目录忽略（git 非真源），需独立物理备份；
保留最近 10 份（对齐 backup_pg_architecture 标杆），RPO/RTO 真源见 config/dr_policy.yaml。

YAML/JSONL 物理快照已删除（ARCH-041 + AI-03 P5 治本）：git history 是 yaml/jsonl
文件真源（directory_contract L740），物理快照违反真源唯一原则且无清理机制导致无限累积。

Usage:
    python scripts/governance/meta/backup_runtime_state.py
    python scripts/governance/meta/backup_runtime_state.py --output-dir tmp/runtime_backups/
    python scripts/governance/meta/backup_runtime_state.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 运行时状态备份 — PG 架构库（四图19表）+ .runtime/handoffs 物理备份（灾备 §33）
dimensions:
- D1
priority: P1
timeout_seconds: 60
warn_only: true
"""

import argparse
import contextlib
import json
import os
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parents[1]
_GOV_DIR = str(_SCRIPT_DIR)
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from _shared.constants import EXIT_PASS, PROTECTED_PG_BACKUP_PREFIXES, REPO_ROOT, SCRIPTS_DIR

# ARCH-041: 默认输出路径从 meta/_backups/（deprecated）改为 tmp/runtime_backups/（不进 git）
DEFAULT_BACKUP_DIR = REPO_ROOT / "tmp" / "runtime_backups"

# S3（AI-03 审计）：人工安全备份（回滚前快照，如 depgraph_pre_RSK_rollback_*）保护前缀。
# 真源收敛至 _shared.constants.PROTECTED_PG_BACKUP_PREFIXES（原本地副本已删除，禁止重定义）。
# 此类备份由人工/repair 脚本一次性产生（非 apply_depgraph 事件路径），排除出 keep-10
# 保留计数，独立保留最新 _PROTECTED_KEEP 份，避免被自动保留策略挤出丢失安全快照。
_PROTECTED_KEEP = 5

# §5.160.2 SQL 集中化：架构库备份导出 SQL（提取到模块级常量，禁裸 SQL 字面量）
# ARCH-041 §5.33.1 治本 v2 扩展（2026-08-03）：从 depgraph 2 表扩展到四图 19 张 DB 真源表。
#   - depgraph (11 表)：nodes/edges/nodes_metadata/edges_metadata/domains/domain_dependencies/
#       domain_mapping/rule_bindings/blueprint_links/nodes_archive_module_lifecycle/domain_events
#   - battle_map (3 表)：battle_map_steps/battle_map_anchors/battle_map_edges
#   - decisiongraph (2 表，DB 真源；decision_layers/tracks 是 YAML 派生不备份)
#   - dataflowgraph (3 表，DB 真源；dataflow_runs 空表/metadata 派生不备份)
# 排除原则：仅备份 DB 真源表，YAML 缓存表/视图/空表不备份（真源收敛原则）。
_ARCHITECTURE_TABLES: list[str] = [
    # depgraph (11 表)
    "nodes", "edges", "nodes_metadata", "edges_metadata",
    "domains", "domain_dependencies", "domain_mapping",
    "rule_bindings", "blueprint_links", "nodes_archive_module_lifecycle",
    "domain_events",
    # battle_map (3 表)
    "battle_map_steps", "battle_map_anchors", "battle_map_edges",
    # decisiongraph (2 表，DB 真源；decision_layers/tracks 是 YAML 派生不备份)
    "decision_nodes", "decision_edges",
    # dataflowgraph (3 表，DB 真源；dataflow_runs 空表/metadata 派生不备份)
    "dataflow_datasets", "dataflow_edges", "dataflow_jobs",
]

# §5.160.2 SQL 集中化：预生成各表的 SELECT SQL（table 是 _ARCHITECTURE_TABLES 硬编码常量，无注入风险）
_SQL_DUMP_TABLES: dict[str, str] = {t: f"SELECT * FROM {t}" for t in _ARCHITECTURE_TABLES}


def _is_protected_backup(name: str) -> bool:
    """判定备份文件名是否为受保护的人工安全备份（排除出常规 keep-N 计数）。"""
    return name.startswith(PROTECTED_PG_BACKUP_PREFIXES)


@contextlib.contextmanager
def _backup_lock(lock_path: Path, *, label: str):
    """非阻塞跨进程 try-lock——序列化备份临界区，防并发冗余快照（AI-03 W1 治本）。

    病根：backup_pg_architecture 的 throttle 仅检查 existing[-1] mtime，无文件锁，
    并发 apply 调用竞态绕过节流（实测 71s 内产生 5 份冗余 architecture 快照）。

    与 _concurrency.FileLock 的区别（非重复造轮子）：
      FileLock = 阻塞轮询锁（等待获取，适合同文件读写互斥）；
      本锁 = try-skip 语义——获取失败立即让步（并发备份应跳过而非排队，
      避免在节流窗口内堆积冗余快照）。原子性由 os.O_CREAT|os.O_EXCL 保证
      （与 _concurrency.ProcessLock._try_write_lock 同一原语）。

    P4 治本（2026-08-03，僵尸锁根因修复）：原实现用 O_CREAT|O_EXCL 创建 lock，
    若持有进程异常退出（崩溃/kill）未走 finally unlink，lock 永久残留，
    后续所有备份全 SKIP（实测 .backup_pg.lock 自 8/2 残留至 8/3，12 次备份全失效）。
    修复：FileExistsError 时读 lock 内容的 pid，若该 pid 已不存在则视为僵尸锁，
    删除后重新创建（接管）。仍存活则正常让步跳过。
    """
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd: int | None = None
    acquired = False
    try:
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        payload = json.dumps({"pid": os.getpid(), "label": label, "acquired_at": datetime.now(UTC).isoformat()})
        os.write(fd, payload.encode("utf-8"))
        acquired = True
        yield True
    except FileExistsError:
        # P4 治本：检测僵尸锁——读持有者 pid，若已死则接管
        holder_pid = _read_lock_holder_pid(lock_path)
        if holder_pid is not None and not _is_pid_alive(holder_pid):
            # 僵尸锁：持有进程已死，安全接管
            print(
                f"[BACKUP-LOCK] 检测到僵尸锁 (pid={holder_pid} 已死)，删除残留 lock 后接管: {lock_path.name}",
                file=sys.stderr,
            )
            try:
                lock_path.unlink()
            except OSError:
                pass  # 竞态：可能已被其他进程清理，继续尝试创建
            # 重试创建 lock（O_EXCL 保证原子性，若被其他接管进程抢先则让步）
            try:
                fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
                payload = json.dumps({"pid": os.getpid(), "label": label, "acquired_at": datetime.now(UTC).isoformat()})
                os.write(fd, payload.encode("utf-8"))
                acquired = True
                yield True
                return
            except FileExistsError:
                # 被其他进程抢先接管，让步
                yield False
                return
        # 持有进程仍存活，正常让步
        yield False  # 另一进程持有锁 → 调用方跳过
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        if acquired:
            try:
                lock_path.unlink()
            except OSError:
                pass


def _read_lock_holder_pid(lock_path: Path) -> int | None:
    """读取 lock 文件内容，解析 holder pid。失败返回 None（保守：不接管）。

    P4 治本辅助函数：lock 文件由 _backup_lock 写入 JSON payload（pid/label/
    acquired_at）。损坏文件（非 JSON / 缺 pid 字段 / pid 类型异常）一律返回 None，
    调用方据此跳过接管，避免误删未知状态 lock。
    """
    try:
        data = json.loads(lock_path.read_text(encoding="utf-8"))
        pid = data.get("pid")
        return int(pid) if isinstance(pid, int) else None
    except (OSError, ValueError, TypeError):
        return None


def _is_pid_alive(pid: int) -> bool:
    """跨平台检测 pid 是否存活。Windows 用 OpenProcess，POSIX 用 os.kill(pid, 0)。

    P4 治本辅助函数：保守语义——检测失败时返回 True（认为存活，不接管，不误删
    活锁）。仅在明确确认进程已死时返回 False。Windows OpenProcess 返回 0 表示
    进程不存在（实测 999999 等不存在的 PID 返回 0）。
    """
    if os.name == "nt":
        # Windows: OpenProcess 检测进程是否存在
        try:
            import ctypes
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000  # noqa: gate-vocab
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if handle:
                kernel32.CloseHandle(handle)
                return True
            return False  # OpenProcess 返回 0 = 进程不存在
        except Exception:
            return True  # 检测失败保守认为存活（不误删活锁，宁可让步不接管）
    else:
        # POSIX: signal 0 不实际发信号，仅检测进程是否存在
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


# ── PG 架构库备份（ARCH-041 §5.33.1 治本 v2 扩展）─────────────────────────
# pg_dump 不可用时的 fallback：用 psycopg2 查询导出为 JSON。
# 触发方式：apply_depgraph/apply_battle_map/apply_decisiongraph/apply_dataflowgraph
#   成功修改架构数据后自动调用（事件触发，非时间触发）。
# 自动清理：保留最近 max_backups 个备份。
# v2 扩展（2026-08-03）：从 depgraph 2 表（nodes/edges）扩展到四图 19 张 DB 真源表。


def _export_architecture_tables(cur) -> dict[str, dict]:
    """导出四图架构真源表（_ARCHITECTURE_TABLES，19 表）为 dict。

    从 backup_pg_architecture 提取（§5.158 NO-HIGH-COMPLEXITY 治本：降低主函数复杂度）。
    缺失表优雅跳过（psycopg2.UndefinedTable），不阻断整体备份。

    Args:
        cur: psycopg2 cursor（已连接）

    Returns:
        {table_name: {"count": N, "rows": [...]}} 字典
    """
    from psycopg2.errors import UndefinedTable

    tables_data: dict[str, dict] = {}
    for table in _ARCHITECTURE_TABLES:
        try:
            cur.execute(_SQL_DUMP_TABLES[table])
            columns = [desc[0] for desc in cur.description]
            rows = [dict(zip(columns, row, strict=False)) for row in cur.fetchall()]
            tables_data[table] = {"count": len(rows), "rows": rows}
        except UndefinedTable:
            # 表不存在（如新装环境未初始化某图 schema）——跳过，不阻断整体备份
            print(f"[BACKUP-PG] WARN: 表 {table} 不存在，跳过", file=sys.stderr)
    return tables_data


def _prune_old_backups(backup_dir: Path, max_backups: int) -> None:
    """清理旧备份：常规备份保留最近 max_backups 份，受保护备份独立保留 _PROTECTED_KEEP 份。

    从 backup_pg_architecture 提取（§5.158 NO-HIGH-COMPLEXITY 治本：降低主函数复杂度）。
    S3：受保护备份（architecture_pre_*/architecture_pinned_*）不占常规 keep-N 配额。
    """
    all_backups = sorted(backup_dir.glob("architecture_*.json"))
    regular = [p for p in all_backups if not _is_protected_backup(p.name)]
    protected = [p for p in all_backups if _is_protected_backup(p.name)]
    for old in regular[:-max_backups]:
        try:
            old.unlink()
        except OSError:
            pass
    for old in protected[:-_PROTECTED_KEEP]:
        try:
            old.unlink()
        except OSError:
            pass


def backup_pg_architecture(max_backups: int = 10, throttle_seconds: int = 0) -> str | None:
    """备份 PG 架构库数据（四图 19 张 DB 真源表）到 tmp/pg_backups/。

    ARCH-041 §5.33.1 治本 v2 扩展：原 backup_pg_depgraph 仅备份 nodes/edges，
    扩展为 backup_pg_architecture 覆盖四图架构真源表（depgraph+battle_map+decisiongraph+dataflowgraph）。
    使用 psycopg2 查询导出为 JSON（pg_dump 不可用时的 fallback）。
    自动清理旧备份（保留最近 max_backups 个）。

    Obs2 治本（节流）：连续 apply 调用会在数秒内产生大量冗余快照
    （实测 14 秒 8 份）。DR 备份无需如此细粒度——架构变更已由 git commit
    追溯（depgraph_dirty.flag 标记；DB 数据备份由 backup_pg_architecture 自动，trae_054 v1.6.0 STEP0），throttle_seconds
    窗口内的多次变更合并为下一次备份即可，RPO 损失可接受（中间态可由 git 历史重放）。
    默认 0 = 不节流（向后兼容测试）；apply 事件触发入口传 60。

    Args:
        max_backups: 保留的备份数量
        throttle_seconds: 节流窗口（秒）。>0 时若距上次备份不足该秒数则跳过
            并返回上次备份路径；0 = 不节流

    Returns:
        备份文件路径（节流时返回上次备份路径），失败返回 None
    """
    import psycopg2

    # _build_pg_dsn 在 src/ 下，需要 sys.path
    src_path = str(REPO_ROOT / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    from zephyr.governance.depgraph_schema import _build_pg_dsn

    backup_dir = REPO_ROOT / "tmp" / "pg_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    # AI-03 W1 治本：throttle+备份临界区加非阻塞跨进程锁，防并发 apply
    # 调用竞态绕过节流（原仅 mtime 检查无锁，实测 71s 产生 5 份冗余快照）。
    # 锁内完成 throttle 检查+备份写入+保留清理，确保节流判断基于已提交的最新快照。
    lock_path = backup_dir / ".backup_pg.lock"
    with _backup_lock(lock_path, label="pg_architecture") as got_lock:
        if not got_lock:
            print(
                "[BACKUP-PG] SKIP: 另一进程正在备份架构库，跳过并发冗余快照",
                file=sys.stderr,
            )
            existing = sorted(
                p for p in backup_dir.glob("architecture_*.json") if not _is_protected_backup(p.name)
            )
            return str(existing[-1]) if existing else None

        # Obs2 治本节流：距上次备份不足 throttle_seconds 则跳过冗余快照。
        # DR 备份目的=灾难恢复（非版本控制），git commit 已提供变更追溯。
        # S3：排除受保护人工备份（architecture_pre_*/architecture_pinned_*），其不应抑制常规备份节流。
        if throttle_seconds > 0:
            existing = sorted(
                p for p in backup_dir.glob("architecture_*.json") if not _is_protected_backup(p.name)
            )
            if existing:
                try:
                    import time as _time

                    age = _time.time() - existing[-1].stat().st_mtime
                    if age < throttle_seconds:
                        print(
                            f"[BACKUP-PG] SKIP: 距上次备份 {int(age)}s < {throttle_seconds}s "
                            f"节流窗口（DR 备份，git commit 已追溯变更），跳过冗余快照: "
                            f"{existing[-1].name}",
                            file=sys.stderr,
                        )
                        return str(existing[-1])
                except OSError:
                    pass  # stat 失败则不节流，继续备份（保守：宁可多备不漏）

        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"architecture_{timestamp}.json"

        try:
            conn = psycopg2.connect(**_build_pg_dsn())
            cur = conn.cursor()

            tables_data = _export_architecture_tables(cur)

            conn.close()

            backup_data = {
                "timestamp": timestamp,
                "source": "architecture (PostgreSQL) — depgraph+battle_map+decisiongraph+dataflowgraph",
                "tables": tables_data,
            }

            backup_path.write_text(
                json.dumps(backup_data, default=str, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            _prune_old_backups(backup_dir, max_backups)

            table_counts = ", ".join(f"{t}={d['count']}" for t, d in tables_data.items())
            print(
                f"[BACKUP-PG] 架构库备份完成: {backup_path.relative_to(REPO_ROOT)} "
                f"({len(tables_data)}/{len(_ARCHITECTURE_TABLES)} 表: {table_counts})",
                file=sys.stderr,
            )
            return str(backup_path)
        except Exception as e:  # noqa: BLE001  # DR 安全网：备份失败须降级为日志+返回 None，绝不中断 apply 主流程
            print(f"[BACKUP-PG] ERROR: {e}", file=sys.stderr)
            return None


# 向后兼容别名（deprecated）：旧代码可能 import backup_pg_depgraph
backup_pg_depgraph = backup_pg_architecture


# ── .runtime/ 状态备份（5.33.7 治本）──────────────────────────────────────
# .runtime/ 被 .gitignore 整目录忽略（git 非真源），handoffs/reconcile_reports
# 丢失无法从 git 恢复。此处补强物理备份：tmp/runtime_backups/runtime_handoffs_<ts>/，
# 保留最近 max_backups 份（对齐 backup_pg_architecture 标杆）。
# RPO/RTO 量化目标唯一真源：config/dr_policy.yaml（runtime_state 条目）。

RUNTIME_STATE_DIRS = (".runtime/handoffs", ".runtime/reconcile_reports")
RUNTIME_BACKUP_PREFIX = "runtime_handoffs_"


def backup_runtime_handoffs(
    max_backups: int = 10,
    backup_dir: Path | None = None,
    throttle_seconds: int = 0,
) -> str | None:
    """备份 .runtime/handoffs/ + .runtime/reconcile_reports/ 到 tmp/runtime_backups/。

    5.33.7 治本：.runtime/ 无备份路径（git 忽略 + 无物理快照）。
    自动清理旧备份（保留最近 max_backups 份，对齐 backup_pg_architecture 标杆）。

    AI-03 W2 治本：增加 throttle_seconds 节流 + 非阻塞跨进程锁，对齐
    backup_pg_architecture 的 Obs2 节流设计（原 runtime_handoffs 完全无节流，
    实测 4 分钟内连续手动调用产生 3 份×2204 文件的冗余快照）。

    Args:
        max_backups: 保留的备份份数
        backup_dir: 备份输出根目录（默认 DEFAULT_BACKUP_DIR=tmp/runtime_backups/）
        throttle_seconds: 节流窗口（秒）。>0 时若距上次备份不足该秒数则跳过
            并返回上次备份路径；0 = 不节流（向后兼容测试，默认）

    Returns:
        备份目录路径；源目录全部缺失或全部复制失败返回 None
    """
    backup_root = backup_dir or DEFAULT_BACKUP_DIR
    sources = [REPO_ROOT / d for d in RUNTIME_STATE_DIRS]
    existing = [s for s in sources if s.is_dir()]
    if not existing:
        print("[BACKUP-RUNTIME] .runtime/ 源目录均不存在，跳过", file=sys.stderr)
        return None

    # AI-03 W2 治本：throttle+备份临界区加非阻塞跨进程锁（对齐 backup_pg_architecture）
    lock_path = Path(backup_root) / ".backup_runtime.lock"
    with _backup_lock(lock_path, label="runtime_handoffs") as got_lock:
        if not got_lock:
            print(
                "[BACKUP-RUNTIME] SKIP: 另一进程正在备份 .runtime/，跳过并发冗余快照",
                file=sys.stderr,
            )
            prior = sorted(p for p in backup_root.glob(f"{RUNTIME_BACKUP_PREFIX}*") if p.is_dir())
            return str(prior[-1]) if prior else None

        # 节流：距上次备份不足 throttle_seconds 则跳过冗余快照（对齐 pg_depgraph Obs2）
        if throttle_seconds > 0:
            prior = sorted(p for p in backup_root.glob(f"{RUNTIME_BACKUP_PREFIX}*") if p.is_dir())
            if prior:
                try:
                    import time as _time

                    age = _time.time() - prior[-1].stat().st_mtime
                    if age < throttle_seconds:
                        print(
                            f"[BACKUP-RUNTIME] SKIP: 距上次备份 {int(age)}s < {throttle_seconds}s "
                            f"节流窗口，跳过冗余快照: {prior[-1].name}",
                            file=sys.stderr,
                        )
                        return str(prior[-1])
                except OSError:
                    pass  # stat 失败则不节流，继续备份（保守：宁可多备不漏）

        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        dest = backup_root / f"{RUNTIME_BACKUP_PREFIX}{timestamp}"
        dest.mkdir(parents=True, exist_ok=True)

        copied: list[str] = []
        for src in existing:
            target = dest / src.name
            try:
                shutil.copytree(src, target)
            except OSError as e:
                print(f"[BACKUP-RUNTIME] 复制失败 {src}: {e}", file=sys.stderr)
                continue
            file_count = sum(1 for p in target.rglob("*") if p.is_file())
            copied.append(f"{src.relative_to(REPO_ROOT)} ({file_count} files)")

        if not copied:
            return None

        manifest = {
            "timestamp": datetime.now(UTC).isoformat(),
            "backup_type": "runtime_handoffs",
            "sources": copied,
            "dr_policy": "config/dr_policy.yaml#runtime_state",
        }
        manifest_path = dest / "manifest.json"
        tmp = f"{manifest_path}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        os.replace(tmp, str(manifest_path))

        # 自动清理旧备份（保留最近 max_backups 份）
        backups = sorted(p for p in backup_root.glob(f"{RUNTIME_BACKUP_PREFIX}*") if p.is_dir())
        if len(backups) > max_backups:
            for old in backups[:-max_backups]:
                shutil.rmtree(old, ignore_errors=True)

        print(
            f"[BACKUP-RUNTIME] .runtime/ 备份完成: {dest.relative_to(REPO_ROOT)} ({'; '.join(copied)})",
            file=sys.stderr,
        )
        return str(dest)


def main() -> None:
    """Entry point: parse args, run logic, return exit code.

    ARCH-041 治本（P5 根因修复）：YAML/JSONL snapshot 创建已移除——git history 是
    yaml/jsonl 文件真源（directory_contract L740），物理快照违反真源唯一原则且
    snapshot_* 目录无清理机制导致无限累积（实测 4 次调用产生 3292+ 碎文件）。
    main() 现仅执行有效的 .runtime/ handoffs 物理备份（5.33.7 治本，git 非真源）。
    """
    parser = argparse.ArgumentParser(description="运行时状态备份")
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(DEFAULT_BACKUP_DIR),
        help=f"备份输出目录（默认: {DEFAULT_BACKUP_DIR}）",
    )
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    parser.add_argument(
        "--throttle-seconds",
        type=int,
        default=60,
        help="节流窗口秒数（AI-03 W2 治本，默认 60）：距上次备份不足该秒数则跳过冗余快照；0=不节流",
    )
    args = parser.parse_args()

    # ARCH-041: YAML/JSONL snapshot 已移除（P5 治本），仅保留 .runtime/ handoffs 备份
    print(
        "[BACKUP-RUNTIME] ARCH-041: YAML/JSONL snapshot 已移除（git 是真源），"
        "仅执行 .runtime/ handoffs 物理备份（5.33.7 治本）\n",
        file=sys.stderr,
    )

    backup_dir = Path(args.output_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)

    # 5.33.7 治本：.runtime/ handoffs + reconcile_reports 物理备份（保留最近 10 份）
    # .runtime/ 被 .gitignore 整目录忽略（git 非真源），需独立物理备份
    # AI-03 W2：main() 默认传 throttle_seconds=60，防连续手动调用产生冗余快照
    backup_runtime_handoffs(backup_dir=backup_dir, throttle_seconds=args.throttle_seconds)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
