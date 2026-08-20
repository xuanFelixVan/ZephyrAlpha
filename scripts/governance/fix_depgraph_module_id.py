# [BLUEPRINT] MOD-D5_ARCH_TOOLS | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-GOV_SCRIPTS | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""fix_depgraph_module_id.py — 修正 depgraph 中不合规的 blueprint_id（module_id）并同步文件头

针对权威校验器 is_valid_module_id（裁定#208 三轨制）判定 BAD 的 28 个 production 节点：
  - 18 rename（blueprint_id 非空但不合规）：CFG-* / MOD-H1_REDIS_HOT / MOD-L02_ANA 等
  - 10 set（blueprint_id 为空/NULL）：散落的 test/script 文件

SSoT 正确顺序（关键）：
  - CFG-* YAML 注册表（规则数据真源）：先改 YAML 真源 module_id，再 --rename-blueprint-id 对齐 DB
  - Python 文件（架构数据，DB 真源）：先 --rename-blueprint-id 改 DB，再同步文件头
  - 空值节点：--set-blueprint-id 按 path 赋值（--rename-blueprint-id 的 old='' 会误伤全库 385 空值节点）

安全机制（与 fix_header_module_id.py 对齐）：
  1. Pre-flight:  git 工作区干净检查 + new_bp_id 权威格式校验 + 碰撞检查 + DB 节点存在性
  2. Per-file:    原子写入(.tmp→rename) + 立即重读验证 + 单文件回滚
  3. Post-batch:  JSON 报告 + before/after 对比

Usage::
  # Dry-run（只分析, 不修改）
  python scripts/governance/fix_depgraph_module_id.py --dry-run

  # 实际执行（需要 --confirm）
  python scripts/governance/fix_depgraph_module_id.py --confirm

  # 跳过 git 干净检查（批处理用）
  python scripts/governance/fix_depgraph_module_id.py --confirm --skip-git-check
"""

from __future__ import annotations

__manifest__ = """
args: []
description: fix_depgraph_module_id.py — 修正 depgraph 中不合规的 blueprint_id（module_id）并同步文件头
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

# 复用 fix_header_module_id 的文件头同步原语（read_file/atomic_write/fix_file 等）
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))
from d3_metadata.validate_module_id_naming import is_valid_module_id  # noqa: E402

sys.path.insert(0, str(_THIS_FILE.parent))
from fix_header_module_id import (  # noqa: E402
    BASE_DIR,
    atomic_write,
    extract_module_ids,
    fix_file,
    read_file,
    validate_module_id_format,
)

# ─── Constants ────────────────────────────────────────────────────────────────

APPLY_DEPGRAPH = BASE_DIR / "scripts" / "governance" / "apply_depgraph.py"
DEFAULT_REPORT = BASE_DIR / ".runtime" / "tmp" / "depgraph_module_id_fix_report.json"

# ─── 映射表（28 节点）─────────────────────────────────────────────────────────
# RENAME: (old_bp_id, new_bp_id, file_type)
#   file_type="yaml" → 规则数据 YAML 真源，先改文件再对齐 DB
#   file_type="py"   → 架构数据 DB 真源，先改 DB 再同步文件头
#   new_bp_id 均已通过 is_valid_module_id 校验（脚本启动时再校验一次）
RENAMES: list[tuple[str, str, str]] = [
    # 4 个 CFG-* 注册表 YAML → MOD-CFG_* 派生轨（用户确认）
    ("MOD-CFG_RULE_ENFORCEMENT", "MOD-CFG_RULE_ENFORCEMENT", "yaml"),
    ("MOD-CFG_RULE_REGISTRY", "MOD-CFG_RULE_REGISTRY", "yaml"),
    ("MOD-CFG_SCRIPTS", "MOD-CFG_SCRIPTS", "yaml"),
    ("MOD-CFG_TEST_SUITE", "MOD-CFG_TEST_SUITE", "yaml"),
    # 5 组 MOD-* 派生轨格式非法（连字符应为下划线）→ 修正为合规派生轨
    ("MOD-H1_REDIS_HOT", "MOD-H1_REDIS_HOT", "py"),  # 8 文件
    ("MOD-L02_ANA", "MOD-L02_ANA", "py"),  # 1 文件
    ("MOD-L02_GOV", "MOD-L02_GOV", "py"),  # 1 文件
    ("MOD-POS_SERVICES", "MOD-POS_SERVICES", "py"),  # 1 文件
    ("MOD-RUNTIME_INTRADAY", "MOD-RUNTIME_INTRADAY", "py"),  # 2 文件
    # 1 个 SH-* 格式非法（ABBR 段间连字符应为下划线）
    ("SH-MODULE_TRANSLATION-001", "SH-MODULE_TRANSLATION-001", "py"),  # 1 文件
]

# SET: (path, new_bp_id, note)
#   blueprint_id 为空/NULL 的节点，按 path 赋值。
#   generate_project_depgraph.py 的 docstring 声明 MOD-INF-005 → 加入既有模块（非新 ID）。
SETS: list[tuple[str, str, str]] = [
    ("scripts/diagnose_breadth_failed.py", "MOD-GOV_DIAGNOSE_BREADTH", "新 ID"),
    ("scripts/governance/generate_project_depgraph.py", "MOD-INF-005", "docstring 声明→加入既有模块"),
    ("scripts/governance/run_gate_chain.py", "MOD-GOV_GATE_CHAIN", "新 ID"),
    ("scripts/governance/d5_architecture/diagnose_depgraph.py", "MOD-GOV_DIAGNOSE_DEPGRAPH", "新 ID"),
    ("scripts/governance/_archive/one_off/phase_a_backup.py", "MOD-GOV_PHASE_A_BACKUP", "新 ID"),
    ("tests/governance/generators/test_check_gate_inventory_drift.py", "MOD-TEST_GATE_INV_DRIFT", "新 ID"),
    ("tests/governance/generators/test_generate_gate_registry.py", "MOD-TEST_GATE_REGISTRY_GEN", "新 ID"),
    ("tests/pf_core/test_intraday_surge_fall_strategy.py", "MOD-TEST_SURGE_FALL_STRATEGY", "新 ID"),
    ("tests/pf_core/test_strategy_runner_tick.py", "MOD-TEST_STRATEGY_RUNNER_TICK", "新 ID"),
    ("tests/zephyr/shared/observability/test_metrics_server.py", "MOD-TEST_METRICS_SERVER", "新 ID"),
]

# ─── 文件同步补漏（跟进批次：6 对 old→new，DB 已改仅文件未同步）──────────────
# 治本（2026-08-03）：6 节点 DB rename 已完成（report OK），但 repo_wide_replace
# 因执行时工作区 stash 隔离导致 git grep 返回 0 文件，27 个文件的旧 ID 引用未替换。
# 本节用于 --file-sync-only 模式：仅做文件精确替换，不触碰 DB（DB 已是最终状态）。
FILE_SYNC_PAIRS: list[tuple[str, str]] = [
    ("MOD-ARCH-BIZDB", "MOD-ARCH_BIZDB"),
    ("MOD-GOV-AUDIT", "MOD-GOV_AUDIT"),
    ("MOD-GOV-CG", "MOD-GOV_CG"),
    ("MOD-GOV-DOCS", "MOD-GOV_DOCS"),
    ("MOD-GOV-SCRIPTS", "MOD-GOV_SCRIPTS"),
    ("MOD-GOV-backfill_checker", "MOD-GOV_BACKFILL_CHECKER"),
]

# 文件同步时跳过的「合理保留」文件（映射表 / 测试夹具 / 审计追踪 / 脚本自身）
# 这些文件引用旧 ID 是有意为之：
#   - 映射表：记录 old→new 映射关系（fix_depgraph_module_id.py / fix_header_module_id.py）
#   - 测试夹具：测试旧 ID 兼容性（test_blueprint_id_legacy_reconciler.py）
#   - 审计追踪：记录重命名历史（audit_rename_completeness.py / test_audit_rename_completeness.py）
#   - 审计注释：reconciliation_registry.py 注释中引用旧 ID 描述 legacy 基线债务（历史记录，替换会歪曲事实）
# 治本（2026-08-03）：INTENTIONAL_SKIP 仅跳过 repo_wide_replace 的全文替换（保护映射表
# old→new 对不被破坏）。但文件自身的 [A_module] module_id 表头不属于映射表引用，
# MUST 手动维护合规格式（如 MOD-GOV_SCRIPTS 而非 MOD-GOV-SCRIPTS），不能用
# repo_wide_replace 自动替换（会连带破坏同文件内的映射表条目）。
INTENTIONAL_SKIP: set[str] = {
    "scripts/governance/fix_depgraph_module_id.py",
    "scripts/governance/fix_header_module_id.py",
    "tests/governance/audit/test_blueprint_id_legacy_reconciler.py",
    "scripts/governance/d8_doc_sync/audit_rename_completeness.py",
    "tests/infrastructure/test_audit_rename_completeness.py",
    "src/zephyr/governance/audit/reconciliation_registry.py",
}


# ─── Data Classes ─────────────────────────────────────────────────────────────


@dataclass
class RenameResult:
    old_bp_id: str
    new_bp_id: str
    file_type: str
    affected_files: list[str] = field(default_factory=list)
    db_action: str = "PENDING"
    file_sync: str = "PENDING"
    status: str = "PENDING"
    error: str | None = None


@dataclass
class SetResult:
    path: str
    new_bp_id: str
    note: str
    db_action: str = "PENDING"
    file_sync: str = "PENDING"
    status: str = "PENDING"
    error: str | None = None


# ─── DB Helpers（只读）─────────────────────────────────────────────────────────


def _get_conn():
    """_get_conn implementation."""
    from _shared.constants import get_depgraph_pg_connection  # noqa: E402

    return get_depgraph_pg_connection(autocommit=True)


def db_node_by_path(path: str) -> dict | None:
    """db_node_by_path implementation."""
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT node_id, path, blueprint_id, belongs_to, build_status, domain_id FROM nodes WHERE path=%s",  # noqa: bare-sql  存量参数化查询/动态标识符，format重排伪新增（§5.160.2集中化专项另列）
            (path,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def db_paths_by_blueprint_id(bp_id: str) -> list[str]:
    """查询某 blueprint_id 下的所有 path（用于 rename 的文件头同步清单）。"""
    conn = _get_conn()
    try:
        rows = conn.execute("SELECT path FROM nodes WHERE blueprint_id=%s ORDER BY path", (bp_id,)).fetchall()  # noqa: bare-sql  存量参数化查询/动态标识符，format重排伪新增（§5.160.2集中化专项另列）
        return [r["path"] for r in rows if r["path"]]
    finally:
        conn.close()


def db_existing_blueprint_ids() -> set[str]:
    """全库 distinct blueprint_id（用于碰撞检查）。"""
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT DISTINCT blueprint_id FROM nodes WHERE blueprint_id IS NOT NULL AND blueprint_id<>''"
        ).fetchall()
        return {r["blueprint_id"] for r in rows}
    finally:
        conn.close()


def check_git_clean() -> bool:
    """Check compliance and report findings."""
    proc = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR),
    )
    return proc.returncode == 0 and proc.stdout.strip() == ""


# ─── 文件替换（rename 的 repo-wide 精确字符串替换）────────────────────────────


def git_grep_files_containing(old: str) -> list[str]:
    """git grep 出所有含 old 字符串的已跟踪文件路径。"""
    proc = subprocess.run(
        ["git", "grep", "-l", "--fixed-strings", old],
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR),
    )
    if proc.returncode not in (0, 1):  # 1 = no matches
        return []
    return [ln for ln in proc.stdout.splitlines() if ln.strip()]


def replace_id_in_file(path: Path, old: str, new: str) -> tuple[bool, int, str | None]:
    """对单文件做精确字符串替换 old→new，原子写入 + 重读验证 + 失败回滚。

    Returns: (ok, replaced_count, error)
    """
    try:
        content, encoding, newline = read_file(path)
    except Exception as e:  # noqa: BLE001
        return False, 0, f"读取失败: {e}"
    count = content.count(old)
    if count == 0:
        return True, 0, None  # 无需替换
    new_content = content.replace(old, new)
    try:
        atomic_write(path, new_content, encoding, newline)
    except Exception as e:  # noqa: BLE001
        return False, 0, f"写入失败: {e}"
    # 验证
    try:
        vc, _, _ = read_file(path)
    except Exception as e:  # noqa: BLE001
        # 验证读取失败 → 回滚
        try:
            atomic_write(path, content, encoding, newline)
        except Exception:  # noqa: BLE001 — 回滚路径，禁止异常掩盖原始错误
            pass
        return False, 0, f"验证读取失败: {e}"
    if old in vc:
        # 仍有 old 残留 → 回滚
        try:
            atomic_write(path, content, encoding, newline)
        except Exception as e:  # noqa: BLE001
            return False, 0, f"回滚失败: {e}"
        return False, 0, "替换后仍含 old（已回滚）"
    return True, count, None


def repo_wide_replace(old: str, new: str, dry_run: bool) -> tuple[list[str], list[str], list[str]]:
    """repo-wide 精确替换 old→new。返回 (ok_files, skipped_files, failed_files)。

    跳过 INTENTIONAL_SKIP 中的文件（映射表/测试夹具/审计追踪/脚本自身）——这些文件
    引用旧 ID 是有意为之，替换会破坏映射表或审计记录。
    """
    hits = git_grep_files_containing(old)
    ok, skipped, failed = [], [], []
    for rel in hits:
        if rel.endswith((".png", ".jpg", ".jpeg", ".gif", ".pdf", ".db", ".lock")):
            skipped.append(rel)
            continue
        # 治本（2026-08-03）：跳过合理保留文件（映射表/测试夹具/审计追踪/脚本自身）
        if rel in INTENTIONAL_SKIP:
            skipped.append(rel)
            continue
        path = BASE_DIR / rel
        if not path.is_file():
            skipped.append(rel)
            continue
        if dry_run:
            ok.append(rel)
            continue
        success, _cnt, err = replace_id_in_file(path, old, new)
        if success:
            ok.append(rel)
        else:
            failed.append(f"{rel}: {err}")
    return ok, skipped, failed


# ─── apply_depgraph 子进程调用 ─────────────────────────────────────────────────


def apply_rename(old: str, new: str, dry_run: bool) -> tuple[bool, str]:
    """apply_rename implementation."""
    cmd = [sys.executable, str(APPLY_DEPGRAPH), "--rename-blueprint-id", old, new]
    if dry_run:
        cmd.append("--dry-run")
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(BASE_DIR))
    out = (proc.stdout + proc.stderr).strip()
    return proc.returncode == 0, out


def apply_set(path: str, new: str, dry_run: bool) -> tuple[bool, str]:
    """apply_set implementation."""
    cmd = [sys.executable, str(APPLY_DEPGRAPH), "--set-blueprint-id", path, new]
    if dry_run:
        cmd.append("--dry-run")
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(BASE_DIR))
    out = (proc.stdout + proc.stderr).strip()
    return proc.returncode == 0, out


# ─── Validation ───────────────────────────────────────────────────────────────


def validate_mapping(existing_ids: set[str]) -> list[str]:
    """启动时校验映射表。返回错误列表（空=全过）。"""
    errors = []
    # RENAME: new 必须合规且不碰撞（new 是全新 ID，不应已存在）
    for old, new, ftype in RENAMES:
        ok, reason = is_valid_module_id(new)
        if not ok:
            errors.append(f"RENAME {old}->{new}: new 格式不合规 ({reason})")
        if new in existing_ids and new != old:
            errors.append(f"RENAME {old}->{new}: new 已存在于 depgraph（碰撞）")
        if ftype not in ("py", "yaml"):
            errors.append(f"RENAME {old}: 未知 file_type {ftype}")
    # SET: new 必须合规（允许加入既有模块，故不查碰撞）
    for path, new, note in SETS:
        ok, reason = is_valid_module_id(new)
        if not ok:
            errors.append(f"SET {path}->{new}: new 格式不合规 ({reason})")
        node = db_node_by_path(path)
        if node is None:
            errors.append(f"SET {path}: DB 中无此节点")
        elif node["blueprint_id"] and node["blueprint_id"] == new:
            errors.append(f"SET {path}: 节点 blueprint_id 已是 {new}（无需操作）")
    return errors


# ─── Dry-run 输出 ─────────────────────────────────────────────────────────────


def print_dry_run(existing_ids: set[str]):
    """print_dry_run implementation."""
    print("=" * 100)
    print("DRY-RUN: depgraph module_id 修正计划（28 节点）")
    print("=" * 100)

    print("\n## A. RENAME（18 节点，10 组 old→new）\n")
    print(f"{'old_bp_id':34s} {'new_bp_id':34s} {'type':5s} {'files含old':>10s}")
    print("-" * 100)
    total_files = 0
    for old, new, ftype in RENAMES:
        db_paths = db_paths_by_blueprint_id(old)
        # repo-wide 文本命中（含文件头 + 文档 + 代码引用）
        grep_hits = git_grep_files_containing(old)
        total_files += len(grep_hits)
        print(f"{old:34s} {new:34s} {ftype:5s} {len(grep_hits):>10d}")
        print(f"    DB nodes ({len(db_paths)}): {', '.join(db_paths[:5])}{'...' if len(db_paths) > 5 else ''}")
        print(f"    grep命中 ({len(grep_hits)}): {', '.join(grep_hits[:4])}{'...' if len(grep_hits) > 4 else ''}")
        if ftype == "yaml":
            print(f"    策略: 先改 YAML 真源(精确替换 {old}→{new})，再 --rename-blueprint-id 对齐 DB")
        else:
            print(f"    策略: --rename-blueprint-id 改 DB，再 repo-wide 精确替换 {old}→{new}")
    print(f"\n  RENAME 合计 repo-wide 命中文件: {total_files}")

    print("\n## B. SET（10 节点，空 blueprint_id 按 path 赋值）\n")
    print(f"{'path':62s} {'new_bp_id':28s} {'note':s}")
    print("-" * 100)
    for path, new, note in SETS:
        node = db_node_by_path(path)
        cur = node["blueprint_id"] if node else "(无节点)"
        print(f"{path:62s} {new:28s} {note}")
        print(f"    当前 DB blueprint_id={cur!r}  →  策略: --set-blueprint-id + fix_file 添/改 [A_module] 头")

    print("\n" + "=" * 100)
    print(
        f"总计: {sum(1 for _ in RENAMES)} 组 rename + {len(SETS)} 组 set = {sum(1 for _ in RENAMES) + len(SETS)} 操作"
    )
    print("确认无误后用 --confirm 执行。")
    print("=" * 100)


# ─── Confirm 执行 ─────────────────────────────────────────────────────────────


def execute_confirm() -> dict:
    """execute_confirm implementation."""
    report = {
        "run_id": time.strftime("%Y%m%d_%H%M%S"),
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "mode": "confirm",
        "renames": [],
        "sets": [],
        "errors": [],
    }

    # ── A. RENAME ──
    for old, new, ftype in RENAMES:
        r = RenameResult(old_bp_id=old, new_bp_id=new, file_type=ftype)
        print(f"\n[RENAME] {old} -> {new} ({ftype})")
        try:
            if ftype == "yaml":
                # 规则数据真源：先改文件，再对齐 DB
                ok, skipped, failed = repo_wide_replace(old, new, dry_run=False)
                r.affected_files = ok
                r.file_sync = f"OK ({len(ok)} files)" if not failed else f"PARTIAL ({len(ok)} ok, {len(failed)} failed)"
                if failed:
                    r.status = "FAILED"
                    r.error = f"文件替换失败: {failed}"
                    report["errors"].append(f"{old}: {failed}")
                    report["renames"].append(asdict(r))
                    continue
                ok_db, out_db = apply_rename(old, new, dry_run=False)
                r.db_action = "OK" if ok_db else f"FAILED: {out_db}"
                r.status = "OK" if ok_db else "FAILED"
                if not ok_db:
                    r.error = out_db
                    report["errors"].append(f"{old}: DB rename failed: {out_db}")
            else:
                # 架构数据 DB 真源：先改 DB，再同步文件头
                ok_db, out_db = apply_rename(old, new, dry_run=False)
                r.db_action = "OK" if ok_db else f"FAILED: {out_db}"
                if not ok_db:
                    r.status = "FAILED"
                    r.error = out_db
                    report["errors"].append(f"{old}: DB rename failed: {out_db}")
                    report["renames"].append(asdict(r))
                    continue
                ok, skipped, failed = repo_wide_replace(old, new, dry_run=False)
                r.affected_files = ok
                r.file_sync = f"OK ({len(ok)} files)" if not failed else f"PARTIAL ({len(ok)} ok, {len(failed)} failed)"
                r.status = "OK" if not failed else "PARTIAL"
                if failed:
                    r.error = f"文件替换失败: {failed}"
                    report["errors"].append(f"{old}: {failed}")
        except Exception as e:  # noqa: BLE001
            r.status = "FAILED"
            r.error = str(e)
            report["errors"].append(f"{old}: {e}")
        report["renames"].append(asdict(r))

    # ── B. SET ──
    for path, new, note in SETS:
        r = SetResult(path=path, new_bp_id=new, note=note)
        print(f"\n[SET] {path} -> {new} ({note})")
        try:
            ok_db, out_db = apply_set(path, new, dry_run=False)
            r.db_action = "OK" if ok_db else f"FAILED: {out_db}"
            if not ok_db:
                r.status = "FAILED"
                r.error = out_db
                report["errors"].append(f"{path}: DB set failed: {out_db}")
                report["sets"].append(asdict(r))
                continue
            # 同步文件头：fix_file 会 ADD [A_module]（缺失时）或 FIX（不一致时），含原子写+验证+回滚
            node = db_node_by_path(path) or {}
            fr = fix_file(BASE_DIR / path, new, node.get("build_status", "generated"))
            if fr.status in ("VERIFIED", "SUCCESS", "SKIPPED"):
                r.file_sync = f"OK ({fr.action})"
                r.status = "OK"
            else:
                r.file_sync = f"FAILED ({fr.status})"
                r.status = "FAILED"
                r.error = fr.error
                report["errors"].append(f"{path}: file sync {fr.status}: {fr.error}")
        except Exception as e:  # noqa: BLE001
            r.status = "FAILED"
            r.error = str(e)
            report["errors"].append(f"{path}: {e}")
        report["sets"].append(asdict(r))

    report["finished_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    return report


# ─── File-Sync-Only 模式（DB 已改，仅补文件同步）────────────────────────────────


def print_file_sync_dry_run():
    """Dry-run: 展示 FILE_SYNC_PAIRS 的文件同步计划（仅文件，不触碰 DB）。"""
    print("=" * 100)
    print(f"DRY-RUN: 文件同步补漏（{len(FILE_SYNC_PAIRS)} 对 old→new，DB 已是最终状态）")
    print("=" * 100)
    print(f"\n跳过合理保留文件（INTENTIONAL_SKIP）: {len(INTENTIONAL_SKIP)} 个")
    for f in sorted(INTENTIONAL_SKIP):
        print(f"  ✓ SKIP  {f}")

    print(f"\n{'old_bp_id':34s} {'new_bp_id':34s} {'需修复文件':>10s}")
    print("-" * 100)
    total = 0
    for old, new in FILE_SYNC_PAIRS:
        hits = git_grep_files_containing(old)
        stale = [
            h
            for h in hits
            if h not in INTENTIONAL_SKIP
            and not h.endswith((".png", ".jpg", ".jpeg", ".gif", ".pdf", ".db", ".lock"))
            and (BASE_DIR / h).is_file()
        ]
        total += len(stale)
        print(f"{old:34s} {new:34s} {len(stale):>10d}")
        for f in stale[:5]:
            print(f"    ✗ {f}")
        if len(stale) > 5:
            print(f"    ... +{len(stale) - 5} more")
    print(f"\n  合计需修复文件: {total}")
    print("\n确认无误后用 --file-sync-only --confirm 执行。")
    print("=" * 100)


def execute_file_sync() -> dict:
    """执行文件同步补漏（仅文件替换，不触碰 DB）。"""
    report = {
        "run_id": time.strftime("%Y%m%d_%H%M%S"),
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "mode": "file-sync-only",
        "pairs": [],
        "errors": [],
    }
    for old, new in FILE_SYNC_PAIRS:
        print(f"\n[FILE-SYNC] {old} -> {new}")
        ok, skipped, failed = repo_wide_replace(old, new, dry_run=False)
        entry = {
            "old": old,
            "new": new,
            "replaced_files": ok,
            "skipped_files": skipped,
            "failed_files": failed,
            "status": "OK" if not failed else "PARTIAL",
        }
        print(f"  替换 {len(ok)} 文件, 跳过 {len(skipped)}, 失败 {len(failed)}")
        if failed:
            report["errors"].extend(failed)
        report["pairs"].append(entry)
    report["finished_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    return report


# ─── Main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(
        description="修正 depgraph 不合规 blueprint_id 并同步文件头（28 节点 + 6 节点文件同步补漏）",
    )
    mode = parser.add_mutually_exclusive_group(required=False)
    mode.add_argument("--dry-run", action="store_true", help="只分析, 不修改")
    mode.add_argument(
        "--confirm",
        action="store_true",
        help="实际执行（DB 修改经 apply_depgraph 自动 PG 备份，trae_054 v1.6.0；建议先 git commit 保持工作树干净）",
    )
    parser.add_argument(
        "--file-sync-only",
        action="store_true",
        help="治本（2026-08-03）：仅补文件同步（DB 已改），用于 6 节点 rename 后文件未同步的修复。配 --confirm 执行，单独使用为 dry-run。",
    )
    parser.add_argument("--skip-git-check", action="store_true", help="跳过 git 干净检查（批处理用）")
    parser.add_argument("--output", type=str, default=str(DEFAULT_REPORT), help="报告 JSON 输出路径")
    args = parser.parse_args()

    # 治本（2026-08-03）：argparse 死锁修复——required=True 互斥组强制 --dry-run/--confirm，
    # 但 --file-sync-only 与 --dry-run 互斥，导致 --file-sync-only 单独使用时无满足条件的必选参数。
    # 改为 required=False + 自定义校验：--file-sync-only 单独=dry-run，配 --confirm=执行。
    if args.file_sync_only:
        if args.dry_run:
            parser.error("--file-sync-only 与 --dry-run 互斥（--file-sync-only 单独使用即为 dry-run）")
    elif not args.dry_run and not args.confirm:
        parser.error("one of the arguments --dry-run --confirm --file-sync-only is required")

    # ── file-sync-only 模式：跳过 RENAMES/SETS 校验，仅处理 FILE_SYNC_PAIRS ──
    if args.file_sync_only:
        if not args.confirm:
            # 无 --confirm 时为 dry-run
            print_file_sync_dry_run()
            return
        # confirm: git 干净检查
        if not args.skip_git_check:
            if not check_git_clean():
                print("ERROR: git 工作区不干净，请先 commit 或 stash。", file=sys.stderr)
                print("       (安全机制: 确保 --file-sync-only --confirm 有干净回滚点)", file=sys.stderr)
                sys.exit(1)
            print("✅ Pre-flight: git 工作区干净")
        report = execute_file_sync()
        DEFAULT_REPORT.parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        n_fail = len(report["errors"])
        n_ok = sum(len(p["replaced_files"]) for p in report["pairs"])
        print(f"\n{'=' * 100}")
        print(f"DONE: {n_ok} 文件已替换, {n_fail} 失败. 报告: {args.output}")
        if report["errors"]:
            print("\n错误清单:")
            for e in report["errors"]:
                print(f"  - {e}")
        print(f"{'=' * 100}")
        sys.exit(0 if n_fail == 0 else 1)

    # Pre-flight: 校验映射表
    existing_ids = db_existing_blueprint_ids()
    errors = validate_mapping(existing_ids)
    if errors:
        print("ERROR: 映射表校验失败，中止：", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print_dry_run(existing_ids)
        return

    # confirm 模式: git 干净检查
    if not args.skip_git_check:
        if not check_git_clean():
            print("ERROR: git 工作区不干净，请先 commit 或 stash。", file=sys.stderr)
            print("       (安全机制: 确保 --confirm 有干净回滚点；批处理可用 --skip-git-check)", file=sys.stderr)
            sys.exit(1)
        print("✅ Pre-flight: git 工作区干净")

    report = execute_confirm()

    DEFAULT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    n_ok = sum(1 for r in report["renames"] if r["status"] == "OK") + sum(
        1 for r in report["sets"] if r["status"] == "OK"
    )
    n_fail = len(report["errors"])
    print(f"\n{'=' * 100}")
    print(f"DONE: {n_ok} OK, {n_fail} FAILED. 报告: {args.output}")
    if report["errors"]:
        print("\n错误清单:")
        for e in report["errors"]:
            print(f"  - {e}")
    print(f"{'=' * 100}")
    sys.exit(0 if n_fail == 0 else 1)


if __name__ == "__main__":
    main()
