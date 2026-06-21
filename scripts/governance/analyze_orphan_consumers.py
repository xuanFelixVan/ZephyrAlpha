"""分析 ORPHAN MODULES 的消费者情况 — 批量 Grep 优化版。

优化策略:
1. 一次性 Grep 所有 "from zephyr" 和 "import zephyr" 语句
2. 内存中构建 {module: [consumers]} 映射
3. 对 360 个 ORPHAN MODULES 查表

用法:
    python scripts/governance/analyze_orphan_consumers.py
    python scripts/governance/analyze_orphan_consumers.py --output d:/ZephyrAlpha/orphan_analysis.json
"""

__manifest__ = {
    "args": [{"flag": "--output", "type": "str", "description": "输出 JSON 路径"}],
    "description": "分析 ORPHAN MODULES 的消费者情况（批量 Grep 优化）",
    "dimensions": ["D1", "D5"],
    "priority": "P2",
    "timeout_seconds": 60,
    "warn_only": False,
}

from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ZEPHYR = PROJECT_ROOT / "src" / "zephyr"


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
        sys.exit(2)
    data = json.loads(result.stdout)
    return data.get("orphan_modules", [])


def batch_collect_imports() -> dict[str, list[str]]:
    """一次性 Grep 所有 import 语句，构建 {module: [consumers]} 映射。

    匹配模式:
        from zephyr.X.Y.Z import ...
        from zephyr.X.Y.Z import (...)  # 多行
        import zephyr.X.Y.Z
    """
    # 使用 ripgrep 一次性搜索所有 zephyr import
    # 模式: from zephyr.<something> import  或  import zephyr.<something>
    pattern = r"(?:from\s+(zephyr[\w.]*))\s+import|(?:import\s+(zephyr[\w.]*))"

    consumers: dict[str, list[str]] = defaultdict(list)

    try:
        result = subprocess.run(
            ["rg", "--no-heading", "-n", "-e", pattern, "src/", "scripts/", "tests/"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                # 格式: file:line:content
                parts = line.split(":", 2)
                if len(parts) < 3:
                    continue
                consumer_file = parts[0]
                content = parts[2]

                # 提取模块名
                match = re.search(pattern, content)
                if match:
                    module = match.group(1) or match.group(2)
                    if module:
                        consumers[module].append(consumer_file)
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"WARNING: Grep 失败: {e}", file=sys.stderr)

    return consumers


def check_module(module_relative: str, import_map: dict[str, list[str]]) -> dict:
    """查表检查模块是否有消费者。

    Args:
        module_relative: 相对路径，如 "governance/auditor.py"
        import_map: {full_module: [consumer_files]} 映射

    Returns:
        分析结果
    """
    # 完整模块路径，如 zephyr.governance.auditor
    parts = module_relative.replace("\\", "/").split("/")
    parts[-1] = parts[-1].replace(".py", "")
    full_module = "zephyr." + ".".join(parts)

    # 查表
    consumer_files = import_map.get(full_module, [])
    # 排除自身
    consumer_files = [c for c in consumer_files if not c.endswith(module_relative)]

    # 文件大小和头部检查
    file_path = SRC_ZEPHYR / module_relative
    size = 0
    has_blueprint = False
    has_class_or_def = False
    try:
        if file_path.exists():
            stat = file_path.stat()
            size = stat.st_size
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                head = f.read(500)
            has_blueprint = "[BLUEPRINT]" in head or "[MODULE]" in head
            has_class_or_def = bool(re.search(r"^(class|def)\s+\w+", head, re.MULTILINE))
    except OSError:
        pass

    return {
        "relative": module_relative,
        "full_module": full_module,
        "has_consumer": len(consumer_files) > 0,
        "consumer_count": len(consumer_files),
        "consumers": sorted(set(consumer_files))[:5],
        "size": size,
        "has_blueprint": has_blueprint,
        "has_class_or_def": has_class_or_def,
    }


def classify(result: dict) -> str:
    """根据分析结果分类。"""
    if result["has_consumer"]:
        return "HAS_CONSUMER"
    if result["size"] < 100:
        return "NO_CONSUMER_TINY"
    if result["has_blueprint"] or result["has_class_or_def"]:
        return "NO_CONSUMER_HAS_VALUE"
    return "NO_CONSUMER_NO_VALUE"


def main() -> None:
    parser = argparse.ArgumentParser(description="分析 ORPHAN MODULES 消费者情况（批量优化版）")
    parser.add_argument("--output", type=str, help="输出 JSON 文件路径")
    args = parser.parse_args()

    orphans = get_orphan_modules()
    print(f"TOTAL ORPHAN MODULES: {len(orphans)}")

    print("批量收集所有 import 语句...")
    import_map = batch_collect_imports()
    print(f"  收集到 {len(import_map)} 个被 import 的模块")

    print("逐个分析 ORPHAN MODULES...")
    results = []
    for i, o in enumerate(orphans):
        result = check_module(o["relative"], import_map)
        result["category"] = classify(result)
        results.append(result)
        if (i + 1) % 100 == 0:
            print(f"  进度: {i+1}/{len(orphans)}")

    # 按相对路径排序
    results.sort(key=lambda x: x["relative"])

    # 统计分类
    category_counts = {}
    for r in results:
        cat = r["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

    print("\n" + "=" * 60)
    print("分类统计:")
    print("-" * 60)
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat:<30} {count:>4} 个")
    print("-" * 60)
    print(f"  {'TOTAL':<30} {len(results):>4} 个")

    # 按域+分类交叉统计
    domain_category = {}
    for r in results:
        domain = r["relative"].split("/")[0] if "/" in r["relative"] else "(root)"
        cat = r["category"]
        key = f"{domain}/{cat}"
        domain_category[key] = domain_category.get(key, 0) + 1

    print("\n按域×分类交叉统计:")
    print("-" * 60)
    for key, count in sorted(domain_category.items()):
        print(f"  {key:<50} {count:>4} 个")

    # 输出 JSON
    output_data = {
        "total": len(results),
        "categories": category_counts,
        "domain_categories": domain_category,
        "results": results,
    }

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nJSON 已写入: {out_path}")
    else:
        print("\n--- 分类统计 JSON ---")
        print(json.dumps({
            "total": len(results),
            "categories": category_counts,
            "domain_categories": domain_category,
        }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
