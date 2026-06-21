# [BLUEPRINT] MOD-INF-037 | docs/02_enterprise_architecture/domain-model-migration-plan.md | §6.8
# [MODULE] scripts.migration.unnest_from_mcp_server
# [INVARIANTS] 将integration/mcp_server/下的文件移回src/zephyr/; 仅复制不删除源; 排除scripts/migration/和data/asset_index/
# [MODIFY-GUARD] 需同步generate_path_migration_mapping.py
# [CONSUMERS] TC-6-3前置步骤
# [STABILITY] volatile
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] mcp_server目录不存在->exit 0; 权限错误->记录继续
# [TESTS] tests/test_unnest_from_mcp_server.py
"""Phase 1: 将 src/zephyr/integration/mcp_server/ 下的文件解嵌套回 src/zephyr/。

上次搬家事故将 src/zephyr/ 整体嵌套搬到了 integration/mcp_server/ 下。
本脚本将文件从 integration/mcp_server/{subpath} 复制到 src/zephyr/{subpath}。
源文件暂不删除（由后续 cleanup 统一处理）。

用法:
    python scripts/migration/unnest_from_mcp_server.py --dry-run
    python scripts/migration/unnest_from_mcp_server.py
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MCP_SERVER_DIR = PROJECT_ROOT / "src" / "zephyr" / "integration" / "mcp_server"
TARGET_BASE = PROJECT_ROOT / "src" / "zephyr"
LOG_FILE = PROJECT_ROOT / "data" / "asset_index" / "unnest-log.yaml"

EXCLUDED_PREFIXES = [
    "integration/mcp_server/",
    "__pycache__/",
]


def _is_excluded(rel_path: str) -> bool:
    for prefix in EXCLUDED_PREFIXES:
        if prefix in rel_path:
            return True
    return False


def _collect_files() -> list[tuple[Path, Path]]:
    if not MCP_SERVER_DIR.exists():
        print(f"[INFO] {MCP_SERVER_DIR} does not exist. Nothing to unnest.")
        return []

    pairs: list[tuple[Path, Path]] = []
    for f in MCP_SERVER_DIR.rglob("*.py"):
        if not f.is_file():
            continue
        if "__pycache__" in str(f):
            continue

        rel = f.relative_to(MCP_SERVER_DIR)
        rel_str = str(rel).replace("\\", "/")

        if _is_excluded(rel_str):
            continue

        target = TARGET_BASE / rel
        pairs.append((f, target))

    return pairs


def _copy_single(src: Path, dst: Path) -> dict:
    if not src.exists():
        return {"src": str(src), "dst": str(dst), "status": "failed", "reason": "source_missing"}

    dst.parent.mkdir(parents=True, exist_ok=True)

    if dst.exists():
        if src.resolve() == dst.resolve():
            return {"src": str(src), "dst": str(dst), "status": "skipped", "reason": "same_path"}
        try:
            if dst.stat().st_size == src.stat().st_size:
                if dst.read_bytes() == src.read_bytes():
                    return {"src": str(src), "dst": str(dst), "status": "skipped", "reason": "already_exists_same_content"}
        except OSError:
            pass

    try:
        shutil.copy2(str(src), str(dst))
        return {"src": str(src), "dst": str(dst), "status": "copied", "reason": ""}
    except OSError as e:
        return {"src": str(src), "dst": str(dst), "status": "failed", "reason": str(e)}


def _atomic_write_yaml(path: Path, data: dict) -> None:
    try:
        import yaml
    except ImportError:
        print("[ERROR] PyYAML not installed.", file=sys.stderr)
        sys.exit(2)
    content = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
    tmp_path = f"{path}.{os.getpid()}.tmp"
    try:
        Path(tmp_path).write_text(content, encoding="utf-8")
        os.replace(tmp_path, path)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Unnest files from integration/mcp_server/ back to src/zephyr/")
    parser.add_argument("--dry-run", action="store_true", help="Dry run — no actual copies")
    args = parser.parse_args()

    print("=== Phase 1: Unnest from integration/mcp_server/ ===")
    if args.dry_run:
        print("(dry-run mode)")

    pairs = _collect_files()
    print(f"Files to unnest: {len(pairs)}")

    if not pairs:
        print("Nothing to do.")
        sys.exit(0)

    if args.dry_run:
        for src, dst in pairs[:20]:
            rel_src = src.relative_to(PROJECT_ROOT)
            rel_dst = dst.relative_to(PROJECT_ROOT)
            print(f"  {rel_src} -> {rel_dst}")
        if len(pairs) > 20:
            print(f"  ... and {len(pairs) - 20} more")
        sys.exit(0)

    success = 0
    failed = 0
    skipped = 0
    results: list[dict] = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(_copy_single, s, d): (s, d) for s, d in pairs}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            if result["status"] == "copied":
                success += 1
            elif result["status"] == "skipped":
                skipped += 1
            else:
                failed += 1
                print(f"  FAILED: {result['src']} ({result.get('reason', '')})")

    log = {
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_dir": str(MCP_SERVER_DIR),
        "target_dir": str(TARGET_BASE),
        "stats": {"success": success, "failed": failed, "skipped": skipped},
        "results": results,
    }
    _atomic_write_yaml(LOG_FILE, log)

    print(f"\n=== Results ===")
    print(f"  Copied:  {success}")
    print(f"  Failed:  {failed}")
    print(f"  Skipped: {skipped}")
    print(f"  Log: {LOG_FILE}")

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
