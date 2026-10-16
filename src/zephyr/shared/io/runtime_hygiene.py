# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §runtime-hygiene
# [MODULE] zephyr.shared.io.runtime_hygiene
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.io.audit_jsonl_writer (DEFAULT_MAX_BYTES/DEFAULT_BACKUP_COUNT 判据常量同源复用，禁复制数值);
#                zephyr.shared.io.file_utils (safe_rmtree 保护区删除唯一合法通道);
#                zephyr.shared.utils.time_utils (now_utc, RULE-SCHEMA-TZ)
# [CONSUMERS] zephyr.trading.process_reaper (_run_safety_wires 第三条保命线=既有计划任务扫描循环挂点，
#             禁新常驻进程——st-diskp0-20261015 D3);
#             tests/shared/test_runtime_hygiene.py
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 本模块是 .runtime 卫生面的**函数库**（无 daemon/无 loop/无自启——挂点在消费方的既有周期面）;
#              轮转判据与命名真源=audit_jsonl_writer（50MB/3 段/`<file>.<N>` 后缀），本件只加
#              "最老段 gzip 化"一腿（替代 unlink 丢弃，B-016 更保守：移位保留+压缩保留）;
#              tmp TTL 判据=mtime（>48h 清；rescue/ 与 .gitkeep 永久豁免；新班车由 mtime 天然豁免）;
#              永不抛（卫生面失败收入返回值，反噬宿主=把保命链变事故源——对齐 process_reaper 口径）;
#              零告警零外发（本件只动手+记账，发现级问题归 vhdx_floor_watch/owner 面管）
# [MODIFY-GUARD] 无（纯新增函数面；消费方挂点=process_reaper._run_safety_wires）
# [STABILITY] new
# [SAFETY] M（删除面：.runtime/tmp 顶层 48h 陈旧条目；误删防线=ttl+mtime 双判+rescue 豁免+allowed_prefix 断言）
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 所有 sweep/rotate 函数永不抛；单项失败记入返回值 errors 继续扫其余条目
# [TESTS] tests/shared/test_runtime_hygiene.py（tmp 目录实测：轮转/gzip 最老段/TTL 两侧/rescue 豁免/dry-run 零副作用）
# [TTL] permanent
"""runtime_hygiene — .runtime 审计轮转 + tmp TTL 卫生面（st-diskp0-20261015 D3，函数库非 daemon）。

病灶：2026-10-15 D 盘满盘事故清点——.runtime/gate_audit 1.4G + .runtime/audit 501M +
.runtime/tmp 1.4G。audit_jsonl_writer 的 50MB 轮转只覆盖"走本 writer 的写侧"，裸
``open(...,"a")`` 写侧与历史存量膨胀段无人管；.runtime/tmp 只有测试残留清理腿
（reconciliation_registry._should_remove_test_dir，PID+2h TTL 双判），缺通用 48h TTL。

设计（内收，零新常驻）：
- 本模块只提供函数；唯一挂点=process_reaper._run_safety_wires 第三条 wire
  （reaper 计划任务既有扫描循环，每轮顺带，失败不反噬收割主链）。
- 轮转复用 audit_jsonl_writer 判据常量（50MB/3 段），"更旧 gzip"=最老段不再 unlink
  而是压成 ``<file>.<N>.gz``（有界：每次轮转覆盖上一份 .gz）。
- tmp TTL：.runtime/tmp 顶层条目 mtime >48h → safe_rmtree/unlink（rescue/、
  .gitkeep 豁免；今日在班车 mtime 新鲜天然豁免）。

Usage（消费方挂点示意）::

    from zephyr.shared.io.runtime_hygiene import run_runtime_hygiene
    wires["runtime_hygiene"] = run_runtime_hygiene(REPO_ROOT, dry_run=report.dry_run)

# [ALGO_FLOW] external: docs/03_modules/_domain_shared/algo_flow/io/runtime_hygiene.yaml
"""

from __future__ import annotations

import gzip
import shutil
from pathlib import Path
from typing import Final

from zephyr.shared.io.audit_jsonl_writer import DEFAULT_BACKUP_COUNT, DEFAULT_MAX_BYTES
from zephyr.shared.utils.time_utils import now_utc

#: .runtime 下参与轮转扫描的审计目录（相对 repo root；宪法 §9.4 永久区卫生面）
AUDIT_SUBDIRS: Final[tuple[str, ...]] = (".runtime/gate_audit", ".runtime/audit")

#: .runtime/tmp 顶层永久豁免（rescue=归档 ？？存证面——RB-4 §1.3，删除它=毁存证）
_TMP_PROTECTED_NAMES: Final[tuple[str, ...]] = ("rescue", ".gitkeep")

#: tmp TTL 出厂值（小时）——st-diskp0-20261015 D3 工单指定 48h
DEFAULT_TMP_TTL_HOURS: Final = 48.0

_SECONDS_PER_HOUR: Final = 3600.0


def rotate_audit_segment(
    path: Path,
    *,
    max_bytes: int = DEFAULT_MAX_BYTES,
    backup_count: int = DEFAULT_BACKUP_COUNT,
    dry_run: bool = False,
) -> str:
    """单文件入口闸：≥阈值先轮转；**最老段 gzip 化**（替代 audit_jsonl_writer._rotate 的 unlink 丢弃）。

    命名约定与 audit_jsonl_writer 同型：``<file>.<N>``（N 越大越老）；最老段
    ``<file>.<backup_count>`` 存在时压成 ``<file>.<backup_count>.gz``（覆盖旧 .gz——
    有界保留：当前段+3 明文段+1 压缩段）。返回动作：
    "rotated_gz"（轮转+最老段压缩）/"rotated"（轮转，无最老段）/"gzip_legacy"（存量超号段补压）/"ok"/"error:..."。
    """
    try:
        actions: list[str] = []
        oldest = path.with_name(f"{path.name}.{backup_count}")
        # 存量补压：超出保留份数的历史明文段（旧 unlink 语义时代的漏网）一次gzip归一
        n = backup_count + 1
        legacy = path.with_name(f"{path.name}.{n}")
        if legacy.exists() and not _is_gz(legacy):
            if not dry_run:
                _gzip_file(legacy)
            actions.append("gzip_legacy")
        if path.exists() and path.stat().st_size >= max_bytes:
            if oldest.exists():
                if not dry_run:
                    _gzip_file(oldest)
                actions.append("rotated_gz")
            else:
                actions.append("rotated")
            if not dry_run:
                for k in range(backup_count - 1, 0, -1):
                    src = path.with_name(f"{path.name}.{k}")
                    if src.exists():
                        src.rename(path.with_name(f"{path.name}.{k + 1}"))
                path.rename(path.with_name(f"{path.name}.1"))
        return actions[-1] if actions else "ok"
    except OSError as e:
        return f"error:{e}"


def _is_gz(path: Path) -> bool:
    return path.name.endswith(".gz")


def _gzip_file(path: Path) -> None:
    """原地压缩为 <name>.gz（删除原明文件；OSError 向上抛由 rotate 收敛为 error 动作）。"""
    gz_path = path.with_name(path.name + ".gz")
    with path.open("rb") as fin, gzip.open(gz_path, "wb") as fout:
        shutil.copyfileobj(fin, fout)
    path.unlink()


def sweep_audit_rotation(
    repo_root: Path | str,
    *,
    subdirs: tuple[str, ...] = AUDIT_SUBDIRS,
    max_bytes: int = DEFAULT_MAX_BYTES,
    backup_count: int = DEFAULT_BACKUP_COUNT,
    dry_run: bool = False,
) -> dict:
    """扫 .runtime 审计目录：所有当前段 *.jsonl 过同一道 50MB 轮转闸（含裸 open 写侧与历史存量）。"""
    root = Path(repo_root)
    stats: dict = {"scanned": 0, "rotated": 0, "gzipped": 0, "errors": []}
    for rel in subdirs:
        d = root / rel
        if not d.is_dir():
            continue
        for p in sorted(d.iterdir()):
            # 只认当前段（精确后缀 .jsonl）；.jsonl.N / .jsonl.N.gz 是历史段不进轮转面
            if not p.name.endswith(".jsonl") or not p.is_file():
                continue
            stats["scanned"] += 1
            action = rotate_audit_segment(p, max_bytes=max_bytes, backup_count=backup_count, dry_run=dry_run)
            if action.startswith("error"):
                stats["errors"].append(f"{p.name}: {action}")
            elif action.startswith("rotated"):
                stats["rotated"] += 1
                if action == "rotated_gz":
                    stats["gzipped"] += 1
            elif action == "gzip_legacy":
                stats["gzipped"] += 1
    return stats


def sweep_runtime_tmp(
    repo_root: Path | str,
    *,
    tmp_rel: str = ".runtime/tmp",
    ttl_hours: float = DEFAULT_TMP_TTL_HOURS,
    protected: tuple[str, ...] = _TMP_PROTECTED_NAMES,
    dry_run: bool = False,
    now_ts: float | None = None,
) -> dict:
    """.runtime/tmp 顶层条目 TTL 清扫（mtime >48h；rescue/ 与 .gitkeep 豁免；今日在班车 mtime 新鲜天然豁免）。

    判据=条目自身 mtime（目录=直接子项最后变动时刻——活跃写入的目录不满足 >48h，天然保留）。
    删除走 safe_rmtree（allowed_prefix=tmp 目录自身，防越界）；顶层散文件 unlink。
    """
    root = Path(repo_root)
    tmp_dir = root / tmp_rel
    stats: dict = {
        "scanned": 0,
        "removed_dirs": 0,
        "removed_files": 0,
        "freed_bytes": 0,
        "skipped_protected": 0,
        "errors": [],
    }
    if not tmp_dir.is_dir():
        return stats
    now = float(now_ts) if now_ts is not None else now_utc().timestamp()
    ttl_s = float(ttl_hours) * _SECONDS_PER_HOUR
    from zephyr.shared.io.file_utils import safe_rmtree

    for entry in sorted(tmp_dir.iterdir()):
        if entry.name in protected:
            stats["skipped_protected"] += 1
            continue
        try:
            age_s = now - entry.stat().st_mtime
        except OSError as e:
            stats["errors"].append(f"{entry.name}: stat_failed:{e}")
            continue
        if age_s <= ttl_s:
            continue
        stats["scanned"] += 1
        try:
            size = (
                sum(f.stat().st_size for f in entry.rglob("*") if f.is_file())
                if entry.is_dir()
                else entry.stat().st_size
            )
        except OSError:
            size = 0
        if dry_run:
            stats["freed_bytes"] += size
            if entry.is_dir():
                stats["removed_dirs"] += 1
            else:
                stats["removed_files"] += 1
            continue
        try:
            if entry.is_dir():
                safe_rmtree(entry, allowed_prefix=str(tmp_dir), ignore_errors=True)
                if entry.exists():
                    stats["errors"].append(f"{entry.name}: rmtree_incomplete")
                    continue
                stats["removed_dirs"] += 1
            else:
                entry.unlink()
                stats["removed_files"] += 1
            stats["freed_bytes"] += size
        except Exception as e:  # noqa: BLE001 — 单项失败不中断清扫（含 UnsafeDeleteRefused 断言拒绝）
            stats["errors"].append(f"{entry.name}: {type(e).__name__}:{e}")
    return stats


def run_runtime_hygiene(
    repo_root: Path | str,
    *,
    dry_run: bool = False,
    max_bytes: int = DEFAULT_MAX_BYTES,
    backup_count: int = DEFAULT_BACKUP_COUNT,
    tmp_ttl_hours: float = DEFAULT_TMP_TTL_HOURS,
) -> dict:
    """单入口（消费方挂点用）：审计轮转 + tmp TTL，两腿各自独立 try，永不抛。

    max_bytes/backup_count 透传轮转判据（真源=audit_jsonl_writer 常量；测试注小阈值实测）。
    """
    out: dict = {"dry_run": dry_run}
    try:
        out["audit_rotation"] = sweep_audit_rotation(
            repo_root, max_bytes=max_bytes, backup_count=backup_count, dry_run=dry_run
        )
    except Exception as e:  # noqa: BLE001 — 卫生面失败不反噬宿主（对齐 _run_safety_wires 口径）
        out["audit_rotation"] = {"errors": [f"unavailable: {type(e).__name__}: {e}"]}
    try:
        out["tmp_ttl"] = sweep_runtime_tmp(repo_root, ttl_hours=tmp_ttl_hours, dry_run=dry_run)
    except Exception as e:  # noqa: BLE001 — 同上
        out["tmp_ttl"] = {"errors": [f"unavailable: {type(e).__name__}: {e}"]}
    return out
