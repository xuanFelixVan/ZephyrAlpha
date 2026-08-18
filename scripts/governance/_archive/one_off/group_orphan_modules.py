# [BLUEPRINT] MOD-GOV_GROUP_ORPHAN_MODULES
# [MODULE]# [MODULE] scripts.governance.group_orphan_modules
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""按域分组统计 ORPHAN MODULES — 用于建任务卡批量处理。

用法:
    python scripts/governance/group_orphan_modules.py
    python scripts/governance/group_orphan_modules.py --output d:/ZephyrAlpha/orphan_groups.json
"""

from __future__ import annotations

__manifest__ = {
    "args": [{"flag": "--output", "type": "str", "description": "输出 JSON 路径"}],
    "description": "按域分组统计 ORPHAN MODULES（用于建任务卡批量处理）",
    "dimensions": ["D1", "D5"],
    "priority": "P2",
    "timeout_seconds": 60,
    "warn_only": False,
}

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from _shared.constants import EXIT_ERROR, REPO_ROOT

PROJECT_ROOT = REPO_ROOT


def get_orphan_modules() -> list[dict]:
    """调用 audit_registration.py --json 获取孤儿模块清单。"""
    result = subprocess.run(
        ["python", "scripts/governance/audit_registration.py", "--json"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )
    if result.returncode not in (0, 1):
        print(f"ERROR: audit_registration.py 失败: {result.stderr}", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    data = json.loads(result.stdout)
    return data.get("orphan_modules", [])


def group_by_domain(orphans: list[dict]) -> dict[str, list[dict]]:
    """按第一级目录（域）分组。

    Returns:
        {domain: [{"relative": ..., "suggestion": ...}, ...]}
    """
    groups: dict[str, list[dict]] = defaultdict(list)
    for item in orphans:
        rel = item["relative"]
        # 第一级目录 = 域（如 governance/, shared/, ops/）
        parts = rel.split("/")
        domain = parts[0] if len(parts) > 1 else "(root)"
        groups[domain].append(item)
    return groups


def group_by_subpackage(orphans: list[dict]) -> dict[str, list[dict]]:
    """按完整包路径分组（更细粒度，用于单卡内部分批）。"""
    groups: dict[str, list[dict]] = defaultdict(list)
    for item in orphans:
        rel = item["relative"]
        parts = rel.split("/")
        # 完整包路径 = 除最后文件名外的所有目录
        pkg = "/".join(parts[:-1]) if len(parts) > 1 else "(root)"
        groups[pkg].append(item)
    return groups


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="按域分组统计 ORPHAN MODULES")
    parser.add_argument("--output", type=str, help="输出 JSON 文件路径")
    parser.add_argument("--by-subpackage", action="store_true", help="按子包分组（更细粒度）")
    args = parser.parse_args()

    orphans = get_orphan_modules()
    print(f"TOTAL ORPHAN MODULES: {len(orphans)}")
    print("=" * 60)

    if args.by_subpackage:
        groups = group_by_subpackage(orphans)
        label = "子包"
    else:
        groups = group_by_domain(orphans)
        label = "域"

    # 按数量降序
    sorted_groups = sorted(groups.items(), key=lambda x: -len(x[1]))

    print(f"\n按{label}分组统计:")
    print("-" * 60)
    for pkg, items in sorted_groups:
        print(f"  {pkg:<40} {len(items):>4} 个")

    print("-" * 60)
    print(f"  {'TOTAL':<40} {len(orphans):>4} 个")
    print(f"\n域/子包数量: {len(sorted_groups)}")

    # 输出 JSON
    output_data = {
        "total_orphans": len(orphans),
        "group_count": len(sorted_groups),
        "group_by": "subpackage" if args.by_subpackage else "domain",
        "groups": [
            {
                "package": pkg,
                "count": len(items),
                "modules": [it["relative"] for it in items],
            }
            for pkg, items in sorted_groups
        ],
    }

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nJSON 已写入: {out_path}")
    else:
        print("\n--- JSON 输出 ---")
        print(json.dumps(output_data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
