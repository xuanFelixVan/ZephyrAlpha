"""全量比对 governance/behavioral_auditor/ 和 security/access_control/behavioral_auditor/ 下的文件。
判断 governance/ 下的副本是否可以安全删除。
"""

import hashlib
from pathlib import Path

GOV_DIR = Path(r"d:\ZephyrAlpha\src\zephyr\governance\behavioral_auditor")
SEC_DIR = Path(r"d:\ZephyrAlpha\src\zephyr\security\access_control\behavioral_auditor")


def file_hash(path: Path) -> str:
    """计算文件内容的 SHA256。"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def file_line_count(path: Path) -> int:
    """统计文件行数。"""
    with open(path, encoding="utf-8", errors="ignore") as f:
        return sum(1 for _ in f)


def main():
    print("=" * 100)
    print("全量比对 governance/behavioral_auditor/ vs security/access_control/behavioral_auditor/")
    print("=" * 100)

    # 获取两个目录下的所有文件（相对路径）
    gov_files = {f.relative_to(GOV_DIR).as_posix(): f for f in GOV_DIR.rglob("*") if f.is_file()}
    sec_files = {f.relative_to(SEC_DIR).as_posix(): f for f in SEC_DIR.rglob("*") if f.is_file()}

    print(f"\ngovernance/behavioral_auditor/ 文件数: {len(gov_files)}")
    print(f"security/access_control/behavioral_auditor/ 文件数: {len(sec_files)}")

    # 分类
    only_gov = set(gov_files) - set(sec_files)
    only_sec = set(sec_files) - set(gov_files)
    common = set(gov_files) & set(sec_files)

    print(f"\n仅在 governance/ 下的文件: {len(only_gov)}")
    for f in sorted(only_gov):
        print(f"  - {f}")

    print(f"\n仅在 security/ 下的文件: {len(only_sec)}")
    for f in sorted(only_sec):
        print(f"  - {f}")

    print(f"\n两个目录共有的文件: {len(common)}")

    # 比对共有文件
    print("\n" + "=" * 100)
    print("共有文件内容比对")
    print("=" * 100)

    identical = []
    different = []
    gov_only_content = []  # governance 下有内容，security 下没有或不同

    for rel in sorted(common):
        gov_path = gov_files[rel]
        sec_path = sec_files[rel]

        gov_h = file_hash(gov_path)
        sec_h = file_hash(sec_path)
        gov_lines = file_line_count(gov_path)
        sec_lines = file_line_count(sec_path)

        if gov_h == sec_h:
            identical.append((rel, gov_lines))
        else:
            different.append((rel, gov_lines, sec_lines))

    print(f"\n完全相同的文件: {len(identical)}")
    for rel, lines in identical:
        print(f"  [相同] {rel} ({lines} 行)")

    print(f"\n内容不同的文件: {len(different)}")
    for rel, gov_lines, sec_lines in different:
        print(f"  [不同] {rel}: governance={gov_lines}行, security={sec_lines}行")

    # 对于内容不同的文件，检查 governance 版本是否有独立价值
    # （即 governance 版本是否有 security 版本没有的函数/类）
    print("\n" + "=" * 100)
    print("内容不同文件的详细分析（governance 版本是否有独立价值）")
    print("=" * 100)

    import ast

    for rel, gov_lines, sec_lines in different:
        gov_path = gov_files[rel]
        sec_path = sec_files[rel]

        print(f"\n--- {rel} ---")
        print(f"  governance: {gov_lines} 行")
        print(f"  security:   {sec_lines} 行")

        # 用 AST 提取顶层函数和类名
        try:
            with open(gov_path, encoding="utf-8", errors="ignore") as f:
                gov_tree = ast.parse(f.read())
            gov_symbols = set()
            for node in ast.iter_child_nodes(gov_tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    gov_symbols.add(node.name)
        except Exception as e:
            gov_symbols = set()
            print(f"  governance AST 解析失败: {e}")

        try:
            with open(sec_path, encoding="utf-8", errors="ignore") as f:
                sec_tree = ast.parse(f.read())
            sec_symbols = set()
            for node in ast.iter_child_nodes(sec_tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    sec_symbols.add(node.name)
        except Exception as e:
            sec_symbols = set()
            print(f"  security AST 解析失败: {e}")

        only_in_gov = gov_symbols - sec_symbols
        only_in_sec = sec_symbols - gov_symbols
        in_both = gov_symbols & sec_symbols

        print(f"  governance 独有符号: {sorted(only_in_gov) if only_in_gov else '无'}")
        print(f"  security 独有符号: {sorted(only_in_sec) if only_in_sec else '无'}")
        print(f"  共有符号: {len(in_both)} 个")

        if only_in_gov:
            print("  ⚠️  governance 版本有独立内容，不可安全删除！")
        else:
            print("  ✅ governance 版本无独立内容，可安全删除（security 版本覆盖全部符号）")

    # 检查仅在 governance/ 下的文件
    if only_gov:
        print("\n" + "=" * 100)
        print("仅在 governance/ 下的文件分析")
        print("=" * 100)
        for rel in sorted(only_gov):
            gov_path = gov_files[rel]
            lines = file_line_count(gov_path)
            print(f"\n--- {rel} ({lines} 行) ---")
            # 读取前20行
            with open(gov_path, encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f):
                    if i >= 20:
                        break
                    print(f"  {i + 1:3d}: {line.rstrip()}")


if __name__ == "__main__":
    main()
