# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/backup_runtime_state.py | §
# [MODULE] scripts.governance.meta.backup_runtime_state
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.meta.__init__; zephyr.governance.depgraph_schema (_build_pg_dsn, backup_pg_depgraph 函数)
# [CONSUMERS] scripts.governance.apply_depgraph (backup_pg_depgraph 事件触发入口); tests/dr/test_restore_from_backup.py
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/dr/test_restore_from_backup.py
# [TTL] permanent
"""
backup_runtime_state.py — 运行时状态备份（蓝图 §33 灾备）

DEPRECATED（ARCH-041）：git history 已是 yaml/jsonl 文件真源（directory_contract L740），
物理快照违反真源唯一原则。本脚本默认输出路径已从 meta/_backups/（deprecated）改为
tmp/runtime_backups/（临时目录，不进 git）。

PG depgraph 备份已实现（ARCH-041 §5.33.1 治本）：backup_pg_depgraph() 函数。
触发方式：apply_depgraph.py 成功修改 depgraph 后自动调用（事件触发）。

.runtime/ handoffs+reconcile_reports 备份已实现（5.33.7 治本）：backup_runtime_handoffs()
函数。.runtime/ 被 .gitignore 整目录忽略（git 非真源），需独立物理备份；
保留最近 10 份（对齐 backup_pg_depgraph 标杆），RPO/RTO 真源见 config/dr_policy.yaml。

YAML/JSONL 快照功能仍保留（向后兼容），但已标记 DEPRECATED。

Usage:
    python scripts/governance/meta/backup_runtime_state.py
    python scripts/governance/meta/backup_runtime_state.py --output-dir tmp/runtime_backups/
    python scripts/governance/meta/backup_runtime_state.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 运行时状态备份 — SQLite导出JSON+YAML快照→commit（灾备 §33）
dimensions:
- D1
priority: P1
timeout_seconds: 60
warn_only: true
"""

import argparse
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

from _shared.constants import EXIT_PASS, REPO_ROOT, SCRIPTS_DIR

META_DIR = SCRIPTS_DIR / "meta"
# ARCH-041: 默认输出路径从 meta/_backups/（deprecated）改为 tmp/runtime_backups/（不进 git）
DEFAULT_BACKUP_DIR = REPO_ROOT / "tmp" / "runtime_backups"


def backup_yaml_files(backup_dir: Path) -> list[str]:
    """备份所有 meta/ 下的 YAML 状态文件。

    Args:
        backup_dir: 备份输出目录

    Returns:
        list[str]: 备份的文件列表
    """
    backed_up: list[str] = []
    yaml_files = list(META_DIR.glob("*.yaml"))
    for yf in yaml_files:
        if yf.name.startswith("_"):
            continue
        dst = backup_dir / yf.name
        try:
            content = yf.read_bytes()
            tmp = f"{dst}.tmp"
            with open(tmp, "wb") as f:
                f.write(content)
            os.replace(tmp, str(dst))
            backed_up.append(str(yf.relative_to(SCRIPTS_DIR)))
        except OSError:
            continue
    return backed_up


def backup_jsonl_files(backup_dir: Path) -> list[str]:
    """备份所有 meta/ 下的 JSONL 文件。

    Args:
        backup_dir: 备份输出目录

    Returns:
        list[str]: 备份的文件列表
    """
    backed_up: list[str] = []
    jsonl_files = list(META_DIR.glob("*.jsonl"))
    for jf in jsonl_files:
        dst = backup_dir / jf.name
        try:
            content = jf.read_bytes()
            tmp = f"{dst}.tmp"
            with open(tmp, "wb") as f:
                f.write(content)
            os.replace(tmp, str(dst))
            backed_up.append(str(jf.relative_to(SCRIPTS_DIR)))
        except OSError:
            continue
    return backed_up


def create_manifest(backup_dir: Path, backed_up: list[str]) -> None:
    """创建备份 manifest。

    Args:
        backup_dir: 备份目录
        backed_up: 备份文件列表
    """
    manifest = {
        "timestamp": datetime.now(UTC).isoformat(),
        "backup_type": "runtime_state_snapshot",
        "files": backed_up,
        "source": str(META_DIR.relative_to(REPO_ROOT)),
    }
    manifest_path = backup_dir / "backup_manifest.json"
    tmp = f"{manifest_path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    os.replace(tmp, str(manifest_path))


# ── PG depgraph 备份（ARCH-041 §5.33.1 治本）──────────────────────────────
# pg_dump 不可用时的 fallback：用 psycopg2 查询导出为 JSON。
# 触发方式：apply_depgraph.py 成功修改 depgraph 后自动调用（事件触发，非时间触发）。
# 自动清理：保留最近 max_backups 个备份。

def backup_pg_depgraph(
    max_backups: int = 10, throttle_seconds: int = 0
) -> str | None:
    """备份 PG depgraph 数据（nodes + edges 表）到 tmp/pg_backups/。

    ARCH-041 §5.33.1 治本：PG depgraph 无备份脚本，此处补强。
    使用 psycopg2 查询导出为 JSON（pg_dump 不可用时的 fallback）。
    自动清理旧备份（保留最近 max_backups 个）。

    Obs2 治本（节流）：连续 apply_depgraph 调用会在数秒内产生大量冗余快照
    （实测 14 秒 8 份）。DR 备份无需如此细粒度——depgraph 变更已由 git commit
    追溯（trae_054 STEP0 铁律：改 depgraph 前必须 git commit 备份），throttle_seconds
    窗口内的多次变更合并为下一次备份即可，RPO 损失可接受（中间态可由 git 历史重放）。
    默认 0 = 不节流（向后兼容测试）；apply_depgraph 事件触发入口传 60。

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

    # Obs2 治本节流：距上次备份不足 throttle_seconds 则跳过冗余快照。
    # DR 备份目的=灾难恢复（非版本控制），git commit 已提供变更追溯。
    if throttle_seconds > 0:
        existing = sorted(backup_dir.glob("depgraph_*.json"))
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
    backup_path = backup_dir / f"depgraph_{timestamp}.json"

    try:
        conn = psycopg2.connect(**_build_pg_dsn())
        cur = conn.cursor()

        # 导出 nodes 表
        cur.execute("SELECT * FROM nodes ORDER BY node_id")
        columns = [desc[0] for desc in cur.description]
        nodes = [dict(zip(columns, row, strict=False)) for row in cur.fetchall()]

        # 导出 edges 表
        cur.execute("SELECT * FROM edges ORDER BY edge_id")
        columns = [desc[0] for desc in cur.description]
        edges = [dict(zip(columns, row, strict=False)) for row in cur.fetchall()]

        conn.close()

        backup_data = {
            "timestamp": timestamp,
            "source": "depgraph (PostgreSQL)",
            "tables": {
                "nodes": {"count": len(nodes), "rows": nodes},
                "edges": {"count": len(edges), "rows": edges},
            },
        }

        backup_path.write_text(
            json.dumps(backup_data, default=str, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        # 自动清理旧备份
        backups = sorted(backup_dir.glob("depgraph_*.json"))
        if len(backups) > max_backups:
            for old in backups[:-max_backups]:
                try:
                    old.unlink()
                except OSError:
                    pass

        print(
            f"[BACKUP-PG] depgraph 备份完成: {backup_path.relative_to(REPO_ROOT)} "
            f"(nodes={len(nodes)}, edges={len(edges)})",
            file=sys.stderr,
        )
        return str(backup_path)
    except Exception as e:
        print(f"[BACKUP-PG] ERROR: {e}", file=sys.stderr)
        return None


# ── .runtime/ 状态备份（5.33.7 治本）──────────────────────────────────────
# .runtime/ 被 .gitignore 整目录忽略（git 非真源），handoffs/reconcile_reports
# 丢失无法从 git 恢复。此处补强物理备份：tmp/runtime_backups/runtime_handoffs_<ts>/，
# 保留最近 max_backups 份（对齐 backup_pg_depgraph 标杆）。
# RPO/RTO 量化目标唯一真源：config/dr_policy.yaml（runtime_state 条目）。

RUNTIME_STATE_DIRS = (".runtime/handoffs", ".runtime/reconcile_reports")
RUNTIME_BACKUP_PREFIX = "runtime_handoffs_"


def backup_runtime_handoffs(max_backups: int = 10, backup_dir: Path | None = None) -> str | None:
    """备份 .runtime/handoffs/ + .runtime/reconcile_reports/ 到 tmp/runtime_backups/。

    5.33.7 治本：.runtime/ 无备份路径（git 忽略 + 无物理快照）。
    自动清理旧备份（保留最近 max_backups 份，对齐 backup_pg_depgraph 标杆）。

    Args:
        max_backups: 保留的备份份数
        backup_dir: 备份输出根目录（默认 DEFAULT_BACKUP_DIR=tmp/runtime_backups/）

    Returns:
        备份目录路径；源目录全部缺失或全部复制失败返回 None
    """
    backup_root = backup_dir or DEFAULT_BACKUP_DIR
    sources = [REPO_ROOT / d for d in RUNTIME_STATE_DIRS]
    existing = [s for s in sources if s.is_dir()]
    if not existing:
        print("[BACKUP-RUNTIME] .runtime/ 源目录均不存在，跳过", file=sys.stderr)
        return None

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
        f"[BACKUP-RUNTIME] .runtime/ 备份完成: {dest.relative_to(REPO_ROOT)} "
        f"({'; '.join(copied)})",
        file=sys.stderr,
    )
    return str(dest)


def main() -> None:
    """Entry point: parse args, run logic, return exit code.

    ARCH-041 治本（P5 根因修复）：YAML/JSONL snapshot 创建已移除——git history 是
    yaml/jsonl 文件真源（directory_contract L740），物理快照违反真源唯一原则且
    snapshot_* 目录无清理机制导致无限累积（实测 4 次调用产生 3292+ 碎文件）。
    main() 现仅执行有效的 .runtime/ handoffs 物理备份（5.33.7 治本，git 非真源）。
    backup_yaml_files/backup_jsonl_files 函数保留（向后兼容）但不再被 main() 调用。
    """
    parser = argparse.ArgumentParser(description="运行时状态备份")
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(DEFAULT_BACKUP_DIR),
        help=f"备份输出目录（默认: {DEFAULT_BACKUP_DIR}）",
    )
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
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
    backup_runtime_handoffs(backup_dir=backup_dir)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
