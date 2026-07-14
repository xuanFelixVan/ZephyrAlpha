# [MODULE] scripts.governance.phase_a_backup
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""
phase_a_backup.py — 阶段A安全网 Tier0/Tier1 关键文件备份

将项目关键资产备份到场外目录 D:\\临时工作区\\_backups\\phase-A\\{timestamp}\\：
- Tier0: 5个核心资产文件（project-architecture-panorama / depgraph / migration-registry / zalpha_metadata.db / unified-asset-index）
- Tier1: 注册表 + 契约 + 能力卡 + 回滚策略
- Tier2: 审计日志 + 安全基线 + 红蓝对抗 + 工作DAG + 健康快照
- git bundle 全仓库备份

Usage:
    python scripts/governance/phase_a_backup.py --tier0
    python scripts/governance/phase_a_backup.py --tier1
    python scripts/governance/phase_a_backup.py --tier2
    python scripts/governance/phase_a_backup.py --all
    python scripts/governance/phase_a_backup.py --verify-only
"""

__manifest__ = """
args: [--tier0, --tier1, --tier2, --all, --verify-only, --output-dir]
description: 阶段A安全网 Tier0/1/2 关键文件备份 + git bundle——原子写入+并行复制+SHA256校验
dimensions: []
priority: P1
timeout_seconds: 600
warn_only: false
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from _shared.constants import REPO_ROOT

_MAX_WORKERS = 8

# Determine repo root
_SCRIPT_DIR = Path(__file__).resolve().parent
BACKUP_BASE = Path("D:/临时工作区/_backups/phase-A")

# ============================================================
# Tier0 file manifest (5 items: 4 YAML/data + 1 SQLite)
# ============================================================
TIER0_FILES: list[str] = [
    "data/asset_index/project-architecture-panorama.yaml",
    "data/asset_index/project-entity-depgraph.yaml",
    "docs/02_enterprise_architecture/migration-registry.yaml",
    "data/zalpha_metadata.db",
    "data/asset_index/unified-asset-index.yaml",
]

# ============================================================
# Tier1 specific files (explicit list, in addition to registries)
# ============================================================
TIER1_SPECIFIC_FILES: list[str] = [
    "data/asset_index/target_path_tree.yaml",
    "data/asset_index/depgraph-diagnosis.yaml",
    "data/asset_index/blueprint-domain-mapping.yaml",
]

# Tier1 directories to recursively copy
TIER1_DIRS: list[str] = [
    "data/contracts",
    "data/capability_cards",
    "data/rollback",
]

# ============================================================
# Tier2 directories
# ============================================================
TIER2_DIRS: list[str] = [
    "data/audit_logs",
    "data/security_baselines",
    "data/red_blue",
    "data/work_dags",
    "data/health_snapshots",
]


def _resolve(path: str) -> Path:
    """Resolve a repo-relative path to absolute."""
    return REPO_ROOT / path


def _sha256_file(filepath: Path) -> str:
    """Compute SHA256 hex digest of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _copy_atomic(src: Path, dst: Path) -> dict:
    """Copy a single file using PID-tmp + atomic rename (RULE-ONE compliant)."""
    result: dict = {
        "src": str(src.relative_to(REPO_ROOT)),
        "dst": str(dst),
        "size": 0,
        "sha256": "",
        "status": "FAILED",
    }
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        sha = _sha256_file(src)
        size = src.stat().st_size
        tmp_path = f"{dst}.{os.getpid()}.tmp"
        shutil.copy2(src, tmp_path)
        os.replace(tmp_path, str(dst))
        result["sha256"] = sha
        result["size"] = size
        result["status"] = "OK"
    except Exception as e:
        result["error"] = str(e)
    return result


def _copy_dir_atomic(src_dir: Path, dst_dir: Path) -> list[dict]:
    """Recursively copy a directory using atomic per-file copies (ThreadPoolExecutor)."""
    results: list[dict] = []
    if not src_dir.exists():
        results.append(
            {
                "src": str(src_dir.relative_to(REPO_ROOT)),
                "dst": str(dst_dir),
                "status": "MISSING",
                "error": "Directory not found",
            }
        )
        return results

    file_pairs: list[tuple[Path, Path]] = []
    for f in sorted(src_dir.rglob("*")):
        if f.is_file():
            rel = f.relative_to(src_dir)
            dst = dst_dir / rel
            file_pairs.append((f, dst))

    if not file_pairs:
        return results

    with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
        futures = {executor.submit(_copy_atomic, src, dst): (src, dst) for src, dst in file_pairs}
        for future in as_completed(futures):
            results.append(future.result())
    return results


def _backup_sqlite_vacuum(src: Path, dst: Path) -> dict:
    """Backup SQLite DB using VACUUM INTO (non-locking operation)."""
    result: dict = {
        "src": str(src.relative_to(REPO_ROOT)),
        "dst": str(dst),
        "size": 0,
        "sha256": "",
        "status": "FAILED",
    }
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(src))
        conn.execute("VACUUM INTO ?", (str(dst),))
        conn.close()
        sha = _sha256_file(dst)
        size = dst.stat().st_size
        result["sha256"] = sha
        result["size"] = size
        result["status"] = "OK"
    except Exception as e:
        result["error"] = str(e)
    return result


def _get_registry_paths() -> list[str]:
    """Parse docs/registry_of_registries.yaml to extract all physical_path entries."""
    registry_yaml = REPO_ROOT / "docs/registry_of_registries.yaml"
    paths: list[str] = ["docs/registry_of_registries.yaml"]
    if not registry_yaml.exists():
        return paths
    try:
        import yaml

        with open(registry_yaml, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        tiers = data.get("tiers", []) if data else []
        for tier in tiers:
            for reg in tier.get("registries", []):
                p = reg.get("physical_path", "")
                if p and p not in paths:
                    paths.append(p)
    except Exception:
        pass
    return paths


def _create_manifest(backup_dir: Path, entries: list[dict], tier: str) -> Path:
    """Write manifest.json with all backup entries (atomic write, RULE-ONE)."""
    ok_count = sum(1 for e in entries if e.get("status") == "OK")
    failed_count = sum(1 for e in entries if e.get("status") != "OK")
    manifest = {
        "timestamp": datetime.now(UTC).isoformat(),
        "tier": tier,
        "backup_dir": str(backup_dir),
        "total_files": len(entries),
        "ok_count": ok_count,
        "failed_count": failed_count,
        "entries": entries,
    }
    manifest_path = backup_dir / "manifest.json"
    tmp = f"{manifest_path}.{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    os.replace(tmp, str(manifest_path))
    return manifest_path


def _verify_from_manifest(backup_dir: Path) -> tuple[int, int]:
    """Verify all files in a tier backup against manifest.json SHA256.

    Returns:
        (ok_count, fail_count) tuple.
    """
    manifest_path = backup_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"  [WARN] manifest.json 不存在: {manifest_path}", file=sys.stderr)
        return (0, 0)

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    entries = manifest.get("entries", [])
    ok = 0
    fail = 0
    for entry in entries:
        dst_path = Path(entry.get("dst", ""))
        expected_sha = entry.get("sha256", "")
        status = entry.get("status", "")
        if status == "MISSING" and not dst_path.exists():
            continue  # Non-existent source is not a verification failure
        if not dst_path.exists():
            print(f"  [MISSING] {dst_path}", file=sys.stderr)
            fail += 1
            continue
        if not expected_sha:
            ok += 1  # No SHA to verify (e.g., git bundle different flow)
            continue
        actual_sha = _sha256_file(dst_path)
        if actual_sha == expected_sha:
            ok += 1
        else:
            print(
                f"  [SHA MISMATCH] {dst_path.name}: expected={expected_sha[:16]}... actual={actual_sha[:16]}...",
                file=sys.stderr,
            )
            fail += 1

    return (ok, fail)


def _verify_sqlite_integrity(db_path: Path) -> bool:
    """Run PRAGMA integrity_check on a SQLite backup."""
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute("PRAGMA integrity_check;")
        row = cursor.fetchone()
        conn.close()
        ok = row[0].lower() == "ok"
        print(f"  [SQLITE] {db_path.name}: integrity_check = {row[0]}", file=sys.stderr)
        return ok
    except Exception as e:
        print(f"  [SQLITE ERROR] {db_path.name}: {e}", file=sys.stderr)
        return False


# ============================================================
# Tier execution functions
# ============================================================


def run_tier0(backup_dir: Path) -> bool:
    """Execute Tier0 backup: 5 core assets (4 YAML/data + 1 SQLite)."""
    print("\n[Tier0] 开始备份 5 个核心资产文件...", file=sys.stderr)
    t0_dir = backup_dir / "tier0"
    entries: list[dict] = []

    for rel_path in TIER0_FILES:
        src = _resolve(rel_path)
        dst = t0_dir / rel_path
        if not src.exists():
            entries.append(
                {
                    "src": rel_path,
                    "dst": str(dst),
                    "status": "MISSING",
                    "error": "Source not found",
                }
            )
            print(f"  [Tier0] MISSING: {rel_path}", file=sys.stderr)
            continue

        print(f"  [Tier0] 备份: {rel_path} ({src.stat().st_size} bytes)", file=sys.stderr)
        if rel_path.endswith(".db"):
            r = _backup_sqlite_vacuum(src, dst)
        else:
            r = _copy_atomic(src, dst)
        entries.append(r)
        status = "OK" if r["status"] == "OK" else f"FAIL: {r.get('error', 'unknown')}"
        print(f"    -> {status} (SHA256: {r.get('sha256', 'N/A')[:16]}...)", file=sys.stderr)

    _create_manifest(t0_dir, entries, "tier0")
    ok = sum(1 for e in entries if e["status"] == "OK")
    total = len(entries)
    print(f"\n[Tier0] 完成: {ok}/{total} 文件备份成功", file=sys.stderr)

    # Also verify immediately after backup
    print("[Tier0] 自校验 SHA256...", file=sys.stderr)
    v_ok, v_fail = _verify_from_manifest(t0_dir)
    print(f"[Tier0] 自校验: {v_ok}/{v_ok + v_fail} SHA256 一致", file=sys.stderr)

    # SQLite integrity check on the backup
    db_backup = t0_dir / "data/zalpha_metadata.db"
    if db_backup.exists():
        sqlite_ok = _verify_sqlite_integrity(db_backup)
        print(f"[Tier0] SQLite integrity: {'PASS' if sqlite_ok else 'FAIL'}", file=sys.stderr)

    return all(e["status"] == "OK" for e in entries)


def run_tier1(backup_dir: Path) -> bool:
    """Execute Tier1 backup: registries + contracts + capability cards + rollback + specific files."""
    print("\n[Tier1] 开始备份注册表 + 契约 + 能力卡 + 回滚策略...", file=sys.stderr)
    t1_dir = backup_dir / "tier1"
    entries: list[dict] = []

    # 1. registry_of_registries.yaml + all referenced registries
    registry_paths = _get_registry_paths()
    print(f"  [Tier1] 注册表: {len(registry_paths)} 个路径待备份", file=sys.stderr)
    registry_pairs: list[tuple[Path, Path]] = []
    for rel_path in registry_paths:
        src = _resolve(rel_path)
        dst = t1_dir / "registries" / rel_path.replace("\\", "/")
        if src.exists():
            registry_pairs.append((src, dst))
        else:
            entries.append(
                {
                    "src": rel_path,
                    "dst": str(dst),
                    "status": "MISSING",
                    "error": "Source not found",
                }
            )
            print(f"  [Tier1] MISSING: {rel_path}", file=sys.stderr)

    # Parallel copy registries
    if registry_pairs:
        with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
            futures = {executor.submit(_copy_atomic, src, dst): (src, dst) for src, dst in registry_pairs}
            for future in as_completed(futures):
                entries.append(future.result())
        print(f"  [Tier1] 注册表: {len(registry_pairs)} 个已复制", file=sys.stderr)

    # 2. Tier1 specific files (parallel)
    specific_pairs: list[tuple[Path, Path]] = []
    for rel_path in TIER1_SPECIFIC_FILES:
        src = _resolve(rel_path)
        dst = t1_dir / "files" / rel_path
        if src.exists():
            specific_pairs.append((src, dst))
        else:
            entries.append(
                {
                    "src": rel_path,
                    "dst": str(dst),
                    "status": "MISSING",
                    "error": "Source not found",
                }
            )
    if specific_pairs:
        with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
            futures = {executor.submit(_copy_atomic, src, dst): (src, dst) for src, dst in specific_pairs}
            for future in as_completed(futures):
                entries.append(future.result())

    # 3. Tier1 directories
    for rel_dir in TIER1_DIRS:
        src_dir = _resolve(rel_dir)
        dst_dir = t1_dir / "dirs" / rel_dir
        print(f"  [Tier1] 复制目录: {rel_dir}", file=sys.stderr)
        dir_entries = _copy_dir_atomic(src_dir, dst_dir)
        entries.extend(dir_entries)
        ok_in_dir = sum(1 for e in dir_entries if e.get("status") == "OK")
        print(f"    -> {ok_in_dir}/{len(dir_entries)} 文件成功", file=sys.stderr)

    _create_manifest(t1_dir, entries, "tier1")
    ok = sum(1 for e in entries if e["status"] == "OK")
    failed = sum(1 for e in entries if e["status"] != "OK")
    print(f"\n[Tier1] 完成: {ok}/{len(entries)} 文件备份成功, {failed} 失败", file=sys.stderr)

    # Self-verify
    print("[Tier1] 自校验 SHA256...", file=sys.stderr)
    v_ok, v_fail = _verify_from_manifest(t1_dir)
    print(f"[Tier1] 自校验: {v_ok}/{v_ok + v_fail} SHA256 一致", file=sys.stderr)

    return failed == 0


def run_tier2(backup_dir: Path) -> bool:
    """Execute Tier2 backup: audit logs + security baselines + red/blue + work DAGs + health snapshots."""
    print("\n[Tier2] 开始备份审计日志 + 安全基线 + 红蓝对抗 + 工作DAG + 健康快照...", file=sys.stderr)
    t2_dir = backup_dir / "tier2"
    entries: list[dict] = []

    for rel_dir in TIER2_DIRS:
        src_dir = _resolve(rel_dir)
        dst_dir = t2_dir / rel_dir
        if not src_dir.exists():
            print(f"  [Tier2] 目录不存在，跳过: {rel_dir}", file=sys.stderr)
            entries.append(
                {
                    "src": rel_dir,
                    "dst": str(dst_dir),
                    "status": "MISSING",
                    "error": "Directory not found",
                }
            )
            continue
        print(f"  [Tier2] 复制目录: {rel_dir}", file=sys.stderr)
        dir_entries = _copy_dir_atomic(src_dir, dst_dir)
        entries.extend(dir_entries)
        ok_in_dir = sum(1 for e in dir_entries if e.get("status") == "OK")
        print(f"    -> {ok_in_dir}/{len(dir_entries)} 文件成功", file=sys.stderr)

    _create_manifest(t2_dir, entries, "tier2")
    ok = sum(1 for e in entries if e["status"] == "OK")
    print(f"\n[Tier2] 完成: {ok}/{len(entries)} 文件备份成功", file=sys.stderr)
    return True  # Tier2 is optional/best-effort


def run_git_bundle(backup_dir: Path) -> bool:
    """Create and verify git bundle of the entire repository."""
    print("\n[GitBundle] 创建全仓库 git bundle...", file=sys.stderr)
    bundle_dir = backup_dir / "git_bundle"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = bundle_dir / "zephyralpha.bundle"

    # Clean up previous attempt if any
    if bundle_path.exists():
        bundle_path.unlink()

    # Create bundle
    print(f"  [GitBundle] 执行: git bundle create {bundle_path} --all (可能需要 30-120 秒)...", file=sys.stderr)
    result_create = subprocess.run(
        ["git", "bundle", "create", str(bundle_path), "--all"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result_create.returncode != 0:
        error_msg = result_create.stderr.strip()[:500]
        print(f"  [GitBundle] 创建失败: {error_msg}", file=sys.stderr)
        entries = [
            {
                "src": "git bundle --all",
                "dst": str(bundle_path),
                "status": "FAILED",
                "error": error_msg,
            }
        ]
        _create_manifest(bundle_dir, entries, "git_bundle")
        return False

    bundle_size = bundle_path.stat().st_size
    print(f"  [GitBundle] 创建成功: {bundle_size} bytes ({bundle_size / 1024 / 1024:.1f} MB)", file=sys.stderr)

    # Verify bundle
    print("  [GitBundle] 验证: git bundle verify...", file=sys.stderr)
    result_verify = subprocess.run(
        ["git", "bundle", "verify", str(bundle_path)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result_verify.returncode != 0:
        error_msg = result_verify.stderr.strip()[:500]
        print(f"  [GitBundle] 验证失败: {error_msg}", file=sys.stderr)
        entries = [
            {
                "src": "git bundle --all",
                "dst": str(bundle_path),
                "status": "VERIFY_FAILED",
                "error": error_msg,
            }
        ]
        _create_manifest(bundle_dir, entries, "git_bundle")
        return False

    refs_output = result_verify.stdout + result_verify.stderr
    refs_line = [l for l in refs_output.split("\n") if "The bundle contains" in l]
    print(f"  [GitBundle] 验证通过: {refs_line[0] if refs_line else 'OK'}", file=sys.stderr)

    sha = _sha256_file(bundle_path)
    entries = [
        {
            "src": "git bundle --all",
            "dst": str(bundle_path),
            "size": bundle_size,
            "sha256": sha,
            "status": "OK",
        }
    ]
    _create_manifest(bundle_dir, entries, "git_bundle")
    return True


# ============================================================
# Verify-only mode
# ============================================================


def _find_latest_backup() -> Path | None:
    """Find the most recent backup directory."""
    if not BACKUP_BASE.exists():
        return None
    dirs = sorted(
        [d for d in BACKUP_BASE.iterdir() if d.is_dir() and d.name != "."],
        reverse=True,
    )
    return dirs[0] if dirs else None


def run_verify_only() -> bool:
    """Verify all files in the latest backup against manifest.json SHA256."""
    latest = _find_latest_backup()
    if not latest:
        print("[ERROR] 未找到任何备份目录", file=sys.stderr)
        return False

    print(f"\n{'=' * 60}", file=sys.stderr)
    print(f"[VERIFY-ONLY] 验证备份: {latest}", file=sys.stderr)
    print(f"{'=' * 60}", file=sys.stderr)

    all_ok = True
    summary: dict[str, dict] = {}

    for tier_name in ["tier0", "tier1", "tier2", "git_bundle"]:
        tier_dir = latest / tier_name
        if not tier_dir.exists():
            continue

        print(f"\n--- {tier_name} ---", file=sys.stderr)
        ok, fail = _verify_from_manifest(tier_dir)
        summary[tier_name] = {"ok": ok, "fail": fail}
        if fail > 0:
            all_ok = False

        # Extra: SQLite integrity check for tier0
        if tier_name == "tier0":
            db_backup = tier_dir / "data/zalpha_metadata.db"
            if db_backup.exists():
                sqlite_ok = _verify_sqlite_integrity(db_backup)
                summary[tier_name]["sqlite_integrity"] = "PASS" if sqlite_ok else "FAIL"
                if not sqlite_ok:
                    all_ok = False

        # Extra: git bundle verify
        if tier_name == "git_bundle":
            bundle = tier_dir / "zephyralpha.bundle"
            if bundle.exists():
                result = subprocess.run(
                    ["git", "bundle", "verify", str(bundle)],
                    cwd=str(REPO_ROOT),
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if result.returncode == 0:
                    refs_output = result.stdout + result.stderr
                    refs_line = [l for l in refs_output.split("\n") if "The bundle contains" in l]
                    print(f"  [GitBundle] verify 通过: {refs_line[0] if refs_line else 'OK'}", file=sys.stderr)
                    summary[tier_name]["bundle_verify"] = "PASS"
                else:
                    print(f"  [GitBundle] verify 失败: {result.stderr.strip()[:200]}", file=sys.stderr)
                    summary[tier_name]["bundle_verify"] = "FAIL"
                    all_ok = False

    # Final report
    print(f"\n{'=' * 60}", file=sys.stderr)
    print("[VERIFY-ONLY] 验证报告:", file=sys.stderr)
    for tier, stats in summary.items():
        tier_summary = f"  {tier}: {stats['ok']}/{stats['ok'] + stats['fail']} SHA256 一致"
        if "sqlite_integrity" in stats:
            tier_summary += f" | SQLite: {stats['sqlite_integrity']}"
        if "bundle_verify" in stats:
            tier_summary += f" | git bundle: {stats['bundle_verify']}"
        print(tier_summary, file=sys.stderr)
    print(f"\n[VERIFY-ONLY] 最终结果: {'PASS' if all_ok else 'FAIL'}", file=sys.stderr)
    print(f"{'=' * 60}", file=sys.stderr)

    return all_ok


# ============================================================
# Main
# ============================================================


def main() -> None:
    parser = argparse.ArgumentParser(description="阶段A安全网 Tier0/1/2 关键文件备份 + git bundle")
    parser.add_argument("--tier0", action="store_true", help="备份 Tier0 核心资产（5项）")
    parser.add_argument("--tier1", action="store_true", help="备份 Tier1 注册表+契约+能力卡+回滚策略")
    parser.add_argument("--tier2", action="store_true", help="备份 Tier2 审计日志+安全基线+红蓝+工作DAG+健康快照")
    parser.add_argument("--all", action="store_true", help="备份全部（Tier0+Tier1+Tier2+git bundle）")
    parser.add_argument("--verify-only", action="store_true", help="仅验证最新备份的 SHA256 一致性")
    parser.add_argument("--output-dir", type=str, default=None, help="自定义备份输出目录")

    args = parser.parse_args()

    if args.verify_only:
        ok = run_verify_only()
        sys.exit(0 if ok else 1)

    if not any([args.tier0, args.tier1, args.tier2, args.all]):
        parser.print_help()
        print("\n[ERROR] 请至少指定一个操作模式 (--tier0/--tier1/--tier2/--all/--verify-only)", file=sys.stderr)
        sys.exit(1)

    # Determine timestamp and backup directory
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    if args.output_dir:
        backup_dir = Path(args.output_dir)
    else:
        backup_dir = BACKUP_BASE / timestamp

    backup_dir.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] 备份目标: {backup_dir}", file=sys.stderr)
    print(f"[INFO] 时间戳: {timestamp}", file=sys.stderr)

    all_ok = True

    if args.tier0 or args.all:
        if not run_tier0(backup_dir):
            all_ok = False

    if args.tier1 or args.all:
        if not run_tier1(backup_dir):
            all_ok = False

    if args.tier2 or args.all:
        run_tier2(backup_dir)  # Tier2 is best-effort, doesn't affect exit code

    if args.all:
        if not run_git_bundle(backup_dir):
            all_ok = False

    # Final summary
    print(f"\n{'=' * 60}", file=sys.stderr)
    print(f"[SUMMARY] 备份目录: {backup_dir}", file=sys.stderr)
    print(f"[SUMMARY] 状态: {'ALL OK' if all_ok else 'SOME FAILURES'}", file=sys.stderr)
    print(f"{'=' * 60}", file=sys.stderr)

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
