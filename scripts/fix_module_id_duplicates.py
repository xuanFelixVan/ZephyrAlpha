#!/usr/bin/env python3
"""
Module ID重复修复脚本

功能:
- 自动修复检测到的module_id重复问题
- 为重复的文件分配唯一的module_id
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class ModuleIdFixer:
    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.report_path = self.docs_root.parent / "docs" / "09_AUDIT" / "STATE" / "governance_check_report_after_fix.json"
        self.fixed_count = 0
        self.skipped_count = 0
        self.error_count = 0

    def load_duplicates(self) -> List[Dict]:
        """加载重复的module_id列表"""
        if not self.report_path.exists():
            print(f"[ERROR] 报告文件不存在: {self.report_path}")
            return []

        with open(self.report_path, "r", encoding="utf-8") as f:
            report = json.load(f)

        duplicates = report.get("issues", {}).get("module_id_duplicates", [])
        return duplicates

    def infer_unique_module_id(self, file_path: Path, base_id: str) -> str:
        """推断唯一的module_id"""
        path_str = str(file_path)

        # 根据文件类型添加后缀
        if "INDEX" in file_path.stem:
            suffix = "_INDEX"
        elif "README" in file_path.stem:
            suffix = "_README"
        elif "BLUEPRINT" in file_path.stem:
            suffix = "_BP"
        elif "REPORT" in file_path.stem:
            suffix = "_REPORT"
        elif "TEMPLATE" in file_path.stem:
            suffix = "_TEMPLATE"
        elif "WORKFLOW" in file_path.stem:
            suffix = "_WF"
        elif "STANDARD" in file_path.stem:
            suffix = "_STD"
        else:
            suffix = "_DOC"

        # 提取路径层级信息
        parts = Path(path_str).parts
        if len(parts) > 2:
            layer = parts[1]  # e.g., 01_FRAMEWORK, 02_FACTOR_LIBRARY
            layer_prefix = layer.split("_")[0] if "_" in layer else ""
            if layer_prefix.isdigit():
                suffix = f"_L{layer_prefix}{suffix}"

        # 清理base_id中的特殊字符
        clean_id = re.sub(r'[^A-Z0-9_]', '_', base_id)
        clean_id = re.sub(r'_+', '_', clean_id).strip('_')

        return f"{clean_id}{suffix}"

    def fix_file_module_id(self, file_path: Path, new_module_id: str, dry_run: bool = False) -> bool:
        """修复文件的module_id"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # 检查是否有YAML头部
            if not content.startswith("---"):
                print(f"[SKIP] {file_path} - 无YAML头部")
                self.skipped_count += 1
                return False

            # 替换module_id
            lines = content.split("\n")
            new_lines = []
            replaced = False

            for line in lines:
                if line.strip().startswith("module_id:"):
                    # 保留缩进
                    indent = len(line) - len(line.lstrip())
                    indent_str = line[:indent]
                    new_lines.append(f"{indent_str}module_id: {new_module_id}")
                    replaced = True
                else:
                    new_lines.append(line)

            if not replaced:
                print(f"[SKIP] {file_path} - 未找到module_id字段")
                self.skipped_count += 1
                return False

            if dry_run:
                print(f"[DRY-RUN] 将修改 {file_path} 的module_id为 {new_module_id}")
                return True

            # 写入文件
            new_content = "\n".join(new_lines)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            print(f"[OK] {file_path} -> {new_module_id}")
            self.fixed_count += 1
            return True

        except Exception as e:
            print(f"[ERROR] {file_path} - {str(e)}")
            self.error_count += 1
            return False

    def run(self, dry_run: bool = False, limit: int = None):
        """执行修复"""
        print("=" * 80)
        print("Module ID重复修复工具")
        print("=" * 80)
        print()

        duplicates = self.load_duplicates()

        if not duplicates:
            print("[INFO] 没有发现重复的module_id")
            return

        print(f"[INFO] 发现 {len(duplicates)} 组重复的module_id")
        print()

        if limit:
            duplicates = duplicates[:limit]
            print(f"[INFO] 限制处理前 {limit} 组")
            print()

        # 处理每组重复
        for dup in duplicates:
            module_id = dup["module_id"]
            files = dup["files"]

            print(f"处理: {module_id} ({len(files)}个文件)")

            for i, file_path_str in enumerate(files):
                file_path = Path(file_path_str)
                if not file_path.exists():
                    print(f"  [SKIP] {file_path} - 文件不存在")
                    continue

                # 为每个文件生成唯一的module_id
                new_module_id = self.infer_unique_module_id(file_path, module_id)

                # 如果是第一个文件，保留原始ID
                if i == 0:
                    new_module_id = module_id

                self.fix_file_module_id(file_path, new_module_id, dry_run)

        # 输出统计
        print()
        print("=" * 80)
        print("修复统计")
        print("=" * 80)
        print(f"重复组数: {len(duplicates)}")
        print(f"已修复: {self.fixed_count}")
        print(f"已跳过: {self.skipped_count}")
        print(f"错误数: {self.error_count}")
        print()

        if dry_run:
            print("[INFO] 这是模拟运行，未实际修改文件")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="修复module_id重复问题")
    parser.add_argument("--dry-run", action="store_true", help="模拟运行，不实际修改文件")
    parser.add_argument("--limit", type=int, help="限制处理的组数")
    parser.add_argument("--docs-root", default="docs", help="文档根目录")

    args = parser.parse_args()

    fixer = ModuleIdFixer(docs_root=args.docs_root)
    fixer.run(dry_run=args.dry_run, limit=args.limit)


if __name__ == "__main__":
    main()
