"""批量注册 50 个无消费者 ORPHAN MODULES 到对应 __init__.py 的 __all__。

策略:
1. 从 audit_registration.py --json 获取 50 个 ORPHAN MODULES
2. 用 AST 提取每个模块的顶层 class/function 名
3. 按域分组，修改对应 __init__.py
4. 添加 import 语句 + __all__ 条目
5. 原子写入（RULE-ONE）

前置条件: 4 个 __init__.py 已加锁（session-20260621-fixall）

用法:
    python scripts/governance/register_orphan_modules.py
    python scripts/governance/register_orphan_modules.py --dry-run
"""

from __future__ import annotations
import argparse
import ast
import json
import os
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


def extract_top_level_names(file_path: Path) -> tuple[str | None, list[str]]:
    """用 AST 提取模块的顶层 class 名和 function 名。

    Returns:
        (first_class_name, [all_top_level_names])
    """
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError):
        return None, []

    class_names: list[str] = []
    func_names: list[str] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            class_names.append(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                func_names.append(node.name)

    # 优先用 class 名，其次用 function 名
    all_names = class_names + func_names
    first = class_names[0] if class_names else (func_names[0] if func_names else None)
    return first, all_names


def get_import_name(module_relative: str) -> str:
    """根据文件名生成驼峰命名（audit_registration.py 的 suggestion 逻辑）。"""
    module_name = Path(module_relative).stem
    return "".join(p.capitalize() for p in module_name.split("_"))


def group_orphans_by_package(orphans: list[dict]) -> dict[str, list[dict]]:
    """按包路径分组。"""
    groups: dict[str, list[dict]] = defaultdict(list)
    for o in orphans:
        rel = o["relative"]
        parts = rel.split("/")
        pkg = "/".join(parts[:-1]) if len(parts) > 1 else ""
        # 添加提取的导出名
        file_path = SRC_ZEPHYR / rel
        first_name, all_names = extract_top_level_names(file_path)
        # 优先用 AST 提取的 class 名，其次用驼峰命名
        export_name = first_name or get_import_name(rel)
        o["export_name"] = export_name
        o["all_names"] = all_names
        o["module_name"] = Path(rel).stem
        groups[pkg].append(o)
    return groups


def update_init_py(pkg: str, modules: list[dict], dry_run: bool = False) -> dict:
    """更新对应包的 __init__.py，添加 import 语句和 __all__ 条目。

    Returns:
        {"init_py": ..., "added_imports": [...], "added_all": [...], "skipped": [...]}
    """
    # __init__.py 路径
    if pkg:
        init_py = SRC_ZEPHYR / pkg / "__init__.py"
        pkg_dotted = "zephyr." + pkg.replace("/", ".")
    else:
        init_py = SRC_ZEPHYR / "__init__.py"
        pkg_dotted = "zephyr"

    if not init_py.exists():
        return {"init_py": str(init_py), "error": "__init__.py 不存在"}

    content = init_py.read_text(encoding="utf-8")
    added_imports: list[str] = []
    added_all: list[str] = []
    skipped: list[str] = []

    # 收集需要添加的 import 语句和 __all__ 条目
    for m in modules:
        module_name = m["module_name"]
        export_name = m["export_name"]
        rel = m["relative"]

        import_line = f"from {pkg_dotted}.{module_name} import {export_name}"

        # 检查是否已存在
        if import_line in content:
            skipped.append(rel)
            continue
        if f'"{export_name}"' in content or f"'{export_name}'" in content:
            skipped.append(rel)
            continue

        added_imports.append(import_line)
        added_all.append(export_name)

    if not added_imports:
        return {
            "init_py": str(init_py),
            "added_imports": [],
            "added_all": [],
            "skipped": skipped,
            "message": "无需修改（全部已存在）",
        }

    # 构建新内容
    new_content = content

    # 1. 添加 import 语句（在文件开头，第一个 __all__ 之前）
    # 找到 __all__ 的位置
    all_match = None
    try:
        tree = ast.parse(new_content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        all_match = node
                        break
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id == "__all__":
                    all_match = node
            if all_match:
                break
    except SyntaxError:
        pass

    # 添加 import 语句到文件开头（docstring 之后）
    import_block = "\n".join(added_imports)
    if all_match:
        # 在 __all__ 之前插入 import
        lines = new_content.split("\n")
        # 找到 __all__ 行
        all_line_idx = None
        for i, line in enumerate(lines):
            if "__all__" in line and ("=" in line or ":" in line):
                all_line_idx = i
                break
        if all_line_idx is not None:
            lines.insert(all_line_idx, import_block)
            new_content = "\n".join(lines)
        else:
            new_content = import_block + "\n\n" + new_content
    else:
        new_content = import_block + "\n\n" + new_content

    # 2. 添加 __all__ 条目
    if "__all__" in new_content:
        # 在 __all__ 列表末尾添加
        for name in added_all:
            # 匹配 __all__ = [...] 的最后一个 ]
            # 简单方法：在 ] 前添加
            pattern_end = r"(\]\s*)$"
            import re
            # 找到 __all__ = [...] 的结束 ]
            lines = new_content.split("\n")
            in_all = False
            all_end_idx = None
            for i, line in enumerate(lines):
                if "__all__" in line and ("[" in line):
                    in_all = True
                if in_all and "]" in line:
                    all_end_idx = i
                    break

            if all_end_idx is not None:
                # 在 ] 之前添加新条目
                all_line = lines[all_end_idx]
                indent = "    "
                # 检查上一行是否有逗号
                if all_end_idx > 0 and not lines[all_end_idx - 1].rstrip().endswith(","):
                    if lines[all_end_idx - 1].strip() not in ("[", ""):
                        lines[all_end_idx - 1] = lines[all_end_idx - 1].rstrip() + ","

                for name in added_all:
                    lines.insert(all_end_idx, f'{indent}"{name}",')
                    all_end_idx += 1
                new_content = "\n".join(lines)
                break
        else:
            # 没找到 __all__ = [...]，追加
            new_content += f'\n\n__all__.extend({added_all!r})\n'
    else:
        # 没有 __all__，创建
        all_entries = ",\n    ".join(f'"{n}"' for n in added_all)
        new_content += f'\n\n__all__ = [\n    {all_entries},\n]\n'

    if dry_run:
        print(f"\n[DRY-RUN] {init_py}:")
        print(f"  新增 import: {len(added_imports)} 条")
        for line in added_imports:
            print(f"    {line}")
        print(f"  新增 __all__: {len(added_all)} 条")
        for name in added_all:
            print(f"    {name}")
        if skipped:
            print(f"  跳过（已存在）: {len(skipped)} 条")
    else:
        # 原子写入（RULE-ONE）
        tmp_path = Path(str(init_py) + f".{os.getpid()}.tmp")
        try:
            tmp_path.write_text(new_content, encoding="utf-8")
            os.replace(str(tmp_path), str(init_py))
            print(f"[OK] {init_py}: 新增 {len(added_imports)} import + {len(added_all)} __all__")
            if skipped:
                print(f"     跳过 {len(skipped)} 条（已存在）")
        except PermissionError:
            try:
                os.remove(str(tmp_path))
            except OSError:
                pass
            print(f"[ERROR] {init_py}: 写入权限被拒", file=sys.stderr)
            return {"init_py": str(init_py), "error": "PermissionError"}

    return {
        "init_py": str(init_py),
        "added_imports": added_imports,
        "added_all": added_all,
        "skipped": skipped,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="批量注册无消费者 ORPHAN MODULES 到 __all__")
    parser.add_argument("--dry-run", action="store_true", help="只显示将要做的修改，不实际写入")
    args = parser.parse_args()

    orphans = get_orphan_modules()
    print(f"TOTAL ORPHAN MODULES: {len(orphans)}")

    # 提取导出名
    print("提取模块导出名（AST）...")
    groups = group_orphans_by_package(orphans)
    print(f"按包分组: {len(groups)} 个包")
    for pkg, mods in sorted(groups.items()):
        print(f"  {pkg or '(root)':<30} {len(mods):>3} 个")

    print("\n开始注册...")
    results = []
    for pkg, mods in sorted(groups.items()):
        result = update_init_py(pkg, mods, dry_run=args.dry_run)
        results.append(result)

    # 汇总
    total_added_imports = sum(len(r.get("added_imports", [])) for r in results)
    total_added_all = sum(len(r.get("added_all", [])) for r in results)
    total_skipped = sum(len(r.get("skipped", [])) for r in results)

    print(f"\n{'='*60}")
    print(f"汇总:")
    print(f"  新增 import: {total_added_imports}")
    print(f"  新增 __all__: {total_added_all}")
    print(f"  跳过（已存在）: {total_skipped}")

    if not args.dry_run:
        print(f"\n下一步: 运行 audit_registration.py 验证")


if __name__ == "__main__":
    main()
