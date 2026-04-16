#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
归档相关重复 module_id 消解（合并原 archive-mixed 与 archive-only 两脚本）。

  python scripts/audit/dedupe_archive_module_ids.py --mode mixed
  python scripts/audit/dedupe_archive_module_ids.py --mode archive-only

--mode mixed (Path C1): 含「活跃+归档」的重复组 → 归档副本 module_id 加 _ARCHIVED
--mode archive-only (Path C2): 全为归档路径的重复组 → 旧副本标记 DEPRECATED
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

REPO = Path(".").resolve()
L1_SCAN = REPO / "docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.json"


def _load_l1():
    with open(L1_SCAN, encoding="utf-8") as f:
        return json.load(f)


def is_archive_path(path_str: str) -> bool:
    lower = path_str.lower()
    return any(x in lower for x in ("99_archive", "06_archive", "deprecated", "archive"))


def run_mixed() -> int:
    l1 = _load_l1()
    dups = l1["module_ids"].get("duplicates", {})

    archive_groups = {}
    active_only_groups = {}
    for mid, files in dups.items():
        archive_files = [f for f in files if is_archive_path(f)]
        if archive_files:
            archive_groups[mid] = (files, archive_files)
        else:
            active_only_groups[mid] = files

    print("Path C1: 自动消解含归档的重复 module_id\n" + "=" * 70)
    print(f"📊 含归档的重复组: {len(archive_groups)} | 全活跃组: {len(active_only_groups)}\n")

    stats = {"processed": 0, "archive_files_renamed": 0, "errors": 0, "details": []}

    for mid, (all_files, archive_files) in sorted(archive_groups.items()):
        active_files = [f for f in all_files if not is_archive_path(f)]
        for arch_file in archive_files:
            path = REPO / arch_file
            if not path.exists():
                stats["details"].append(
                    {"status": "SKIP", "reason": "file_not_found", "file": arch_file, "module_id": mid}
                )
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
            except OSError as e:
                stats["errors"] += 1
                stats["details"].append(
                    {"status": "ERROR", "reason": f"read_failed: {e}", "file": arch_file, "module_id": mid}
                )
                continue

            old_pattern = rf"module_id:\s*['\"]?{re.escape(mid)}['\"]?"
            new_id = f"{mid}_ARCHIVED"
            new_content = re.sub(
                old_pattern,
                f'module_id: "{new_id}"',
                content,
                count=1,
                flags=re.IGNORECASE | re.MULTILINE,
            )

            if new_content != content:
                try:
                    path.write_text(new_content, encoding="utf-8")
                    stats["archive_files_renamed"] += 1
                    stats["details"].append(
                        {
                            "status": "RENAMED",
                            "old_id": mid,
                            "new_id": new_id,
                            "file": arch_file,
                            "active_counterpart": active_files[0] if active_files else None,
                        }
                    )
                except OSError as e:
                    stats["errors"] += 1
                    stats["details"].append(
                        {"status": "ERROR", "reason": f"write_failed: {e}", "file": arch_file, "module_id": mid}
                    )
            else:
                stats["details"].append(
                    {
                        "status": "NOTFOUND",
                        "reason": "module_id_pattern_not_found",
                        "file": arch_file,
                        "module_id": mid,
                    }
                )
        stats["processed"] += 1

    print(f"✅ 处理组数: {stats['processed']} | 重命名: {stats['archive_files_renamed']} | 错误: {stats['errors']}")
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    report_path = REPO / "docs/09_AUDIT/STATE" / f"DEDUPE_ARCHIVE_MODULEIDS_{ts}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": ts,
                "mode": "mixed",
                "archive_files_renamed": stats["archive_files_renamed"],
                "errors": stats["errors"],
                "details": stats["details"][:200],
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    print(f"📁 报告: {report_path.relative_to(REPO)}")
    return 0 if stats["errors"] == 0 else 1


def extract_date_from_path(path_str: str) -> str:
    match = re.search(r"_(\d{8})_", path_str)
    return match.group(1) if match else "0000-00-00"


def run_archive_only() -> int:
    l1 = _load_l1()
    dups = l1["module_ids"].get("duplicates", {})

    archive_only = {}
    for mid, files in dups.items():
        if all(any(x in f.lower() for x in ("99_archive", "06_archive", "deprecated")) for f in files):
            archive_only[mid] = files

    print("消解 Archive-Archive 重复 module_id\n" + "=" * 70)
    print(f"共 {len(archive_only)} 组\n")

    results = []
    for mid, files in sorted(archive_only.items()):
        files_with_dates = [(f, extract_date_from_path(f)) for f in files]
        files_with_dates.sort(key=lambda x: x[1])
        canonical = files_with_dates[-1][0]
        to_deprecate = [f for f, _ in files_with_dates[:-1]]

        for fpath in to_deprecate:
            p = REPO / fpath
            if not p.exists():
                results.append({"module_id": mid, "file": fpath, "status": "SKIP", "reason": "file_not_found"})
                continue
            try:
                content = p.read_text(encoding="utf-8", errors="replace")
                new_content = re.sub(
                    rf"(module_id:\s*['\"]?{re.escape(mid)}['\"]?)",
                    rf"\1\n# [DEPRECATED] Archive duplicate - canonical version in {canonical}",
                    content,
                    count=1,
                    flags=re.IGNORECASE | re.MULTILINE,
                )
                if "status:" in new_content:
                    new_content = re.sub(
                        r"(status:\s*)(\w+)",
                        r"\1DEPRECATED",
                        new_content,
                        count=1,
                        flags=re.MULTILINE,
                    )
                p.write_text(new_content, encoding="utf-8")
                results.append(
                    {"module_id": mid, "file": fpath, "status": "MARKED_DEPRECATED", "canonical": canonical}
                )
            except OSError as e:
                results.append({"module_id": mid, "file": fpath, "status": "ERROR", "reason": str(e)})

    marked = sum(1 for r in results if r["status"] == "MARKED_DEPRECATED")
    errors = sum(1 for r in results if r["status"] == "ERROR")
    print(f"完成: {marked} 个标记 DEPRECATED | 错误: {errors}")

    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    report_path = REPO / "docs/09_AUDIT/STATE" / f"DEDUPE_ARCHIVE_ONLY_MODULEIDS_{ts}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": ts,
                "mode": "archive-only",
                "total_duplicate_groups": len(archive_only),
                "results": results,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    print(f"报告: {report_path.relative_to(REPO)}")
    return 0 if errors == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="归档重复 module_id 消解（合并版）")
    ap.add_argument(
        "--mode",
        choices=("mixed", "archive-only"),
        default="mixed",
        help="mixed=含活跃+归档(Path C1)；archive-only=全归档重复(Path C2)",
    )
    args = ap.parse_args()
    if args.mode == "mixed":
        return run_mixed()
    return run_archive_only()


if __name__ == "__main__":
    raise SystemExit(main())
