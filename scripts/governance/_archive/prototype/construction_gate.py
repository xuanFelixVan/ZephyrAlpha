# [BLUEPRINT] MOD-INF-005 | scripts/governance/construction_gate.py | §
# [MODULE] scripts.governance.construction_gate
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.architecture_governance.path_resolver
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
Construction Gate — 施工前路径校验门禁
调用 PathResolver 校验任务卡的 downstream_outputs 路径是否匹配当前项目结构。

用法:
  # 校验单个任务卡文件
  python scripts/governance/construction_gate.py check <task_card_md_path>

  # 校验任务卡内容（stdin）
  python scripts/governance/construction_gate.py check-stdin

  # 导出当前模块树（供蓝图设计参考）
  python scripts/governance/construction_gate.py tree

  # 查询模块归属
  python scripts/governance/construction_gate.py module <module_name>

设计原则：
  - 防止 AI 将文件放入错误位置（路径应精确）
  - 检测任务卡路径与项目结构的偏差（路径漂移）
  - 校验在文件创建前执行，不阻塞施工，但报告偏差
"""

import json
import os
import re
import sys

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from zephyr.governance.architecture_governance.path_resolver import PathResolver

RESOLVER = None


def get_resolver():
    """get_resolver implementation."""
    global RESOLVER
    if RESOLVER is None:
        RESOLVER = PathResolver(PROJECT_ROOT)
    return RESOLVER


def validate_task_card(file_path: str) -> dict:
    """校验单个任务卡 .md 文件的所有 downstream_outputs 路径"""
    if not os.path.isfile(file_path):
        return {"error": f"File not found: {file_path}", "file": file_path}

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    task_id = re.search(r'task_id:\s*"([^"]+)"', content)
    task_id = task_id.group(1) if task_id else os.path.basename(file_path).replace(".md", "")

    title = re.search(r'title:\s*"([^"]+)"', content)
    title = title.group(1) if title else ""

    # Parse downstream_outputs
    downstream = []
    in_downstream = False
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("downstream_outputs:"):
            in_downstream = True
            continue
        if in_downstream:
            if stripped.startswith("- path:"):
                pm = re.search(r'path:\s*"([^"]+)"', stripped)
                if pm:
                    downstream.append(pm.group(1))
            elif (stripped.startswith("- ") or not stripped.startswith(" ")) and not stripped.startswith("- path:"):
                in_downstream = False

    resolver = get_resolver()
    results = []
    all_ok = True

    for expected_path in downstream:
        resolution = resolver.validate_path(expected_path)
        results.append(
            {
                "expected": expected_path,
                "exists_at_expected": resolution.exists_at_expected,
                "status": resolution.status,
                "suggested": resolution.suggested_path,
                "fuzzy_matches": [
                    {"path": fp, "ratio": f"{r:.0%}"}
                    for fp, r in (resolution.found_fuzzy[:3] if resolution.found_fuzzy else [])
                ],
            }
        )
        if resolution.status != "OK":
            all_ok = False

    return {
        "task_id": task_id,
        "title": title,
        "file": file_path,
        "all_ok": all_ok,
        "total": len(results),
        "drifted": sum(1 for r in results if r["status"] == "PATH_DRIFT"),
        "variants": sum(1 for r in results if r["status"] == "NAME_VARIANT"),
        "missing": sum(1 for r in results if r["status"] == "MISSING"),
        "results": results,
    }


def check_stdin():
    """从 stdin 读取任务卡内容并校验"""
    content = sys.stdin.read()
    # Write to temp file
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(content)
        tmp_path = f.name
    try:
        result = validate_task_card(tmp_path)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    finally:
        os.unlink(tmp_path)


def export_tree():
    """导出模块树"""
    resolver = get_resolver()
    tree = resolver.dump_module_tree()
    print(json.dumps(tree, indent=2, ensure_ascii=False))


def query_module(module_name: str):
    """查询模块的归属目录"""
    resolver = get_resolver()
    dirs = resolver.resolve_module(module_name)
    output = {
        "module": module_name,
        "found": len(dirs) > 0,
        "directories": [os.path.relpath(d, PROJECT_ROOT) for d in dirs],
    }

    # Also show existing files in those dirs
    if dirs:
        primary = dirs[0]
        py_files = [f for f in os.listdir(primary) if f.endswith(".py") and f != "__init__.py"]
        output["existing_files"] = sorted(py_files)

    print(json.dumps(output, indent=2, ensure_ascii=False))


def main():
    """Entry point: parse args, run logic, return exit code."""
    if len(sys.argv) < 2:
        print("Usage: construction_gate.py <check|check-stdin|tree|module> [args]")
        print("  check <file>        Validate a task card .md file")
        print("  check-stdin         Validate task card content from stdin")
        print("  tree                Export module tree")
        print("  module <name>       Query module directory")
        sys.exit(EXIT_FINDINGS)

    cmd = sys.argv[1]

    if cmd == "check":
        if len(sys.argv) < 3:
            print("Usage: construction_gate.py check <task_card.md>", file=sys.stderr)
            sys.exit(EXIT_FINDINGS)
        result = validate_task_card(sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if "error" in result:
            sys.exit(EXIT_FINDINGS)
        if not result["all_ok"]:
            sys.exit(EXIT_ERROR)

    elif cmd == "check-stdin":
        check_stdin()

    elif cmd == "tree":
        export_tree()

    elif cmd == "module":
        if len(sys.argv) < 3:
            print("Usage: construction_gate.py module <module_name>", file=sys.stderr)
            sys.exit(EXIT_FINDINGS)
        query_module(sys.argv[2])

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(EXIT_FINDINGS)


if __name__ == "__main__":
    main()
