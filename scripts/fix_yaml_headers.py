#!/usr/bin/env python3
"""
批量添加YAML头部到缺失的Markdown文件

功能:
- 读取governance_check_report.json中缺失YAML头部的文件列表
- 为每个文件生成合适的YAML头部
- 在文件开头插入YAML头部
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import re


class YAMLHeaderFixer:
    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.report_path = self.docs_root.parent / "docs" / "09_AUDIT" / "STATE" / "governance_check_report.json"
        self.fixed_count = 0
        self.skipped_count = 0
        self.error_count = 0

    def load_missing_yaml_files(self) -> List[str]:
        """加载缺失YAML头部的文件列表"""
        if not self.report_path.exists():
            print(f"[ERROR] 报告文件不存在: {self.report_path}")
            return []

        with open(self.report_path, "r", encoding="utf-8") as f:
            report = json.load(f)

        missing_yaml = report.get("issues", {}).get("missing_yaml", [])
        return [item["file"] for item in missing_yaml]

    def extract_title_from_file(self, file_path: Path) -> str:
        """从文件中提取标题"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # 尝试提取第一个标题
            lines = content.split("\n")
            for line in lines[:20]:  # 只检查前20行
                if line.startswith("# "):
                    return line[2:].strip()
                elif line.startswith("## "):
                    return line[3:].strip()

            # 如果没有标题，使用文件名
            return file_path.stem.replace("_", " ").replace("-", " ").title()

        except Exception:
            return file_path.stem.replace("_", " ").replace("-", " ").title()

    def infer_module_id(self, file_path: Path, title: str) -> str:
        """推断module_id"""
        # 从文件路径推断层级
        path_str = str(file_path)

        # 提取层级信息
        if "01_FRAMEWORK" in path_str:
            prefix = "FRAMEWORK_"
        elif "02_FACTOR_LIBRARY" in path_str:
            prefix = "FACTOR_"
        elif "03_TRADING_TACTICS" in path_str:
            prefix = "TRADING_"
        elif "04_EXECUTION" in path_str:
            prefix = "EXEC_"
        elif "05_IMPLEMENTATION" in path_str:
            prefix = "IMPL_"
        elif "06_ARCHIVE" in path_str:
            prefix = "ARCHIVED_"
        elif "07_RESEARCH" in path_str:
            prefix = "RESEARCH_"
        elif "08_KNOWLEDGE" in path_str:
            prefix = "KNOWLEDGE_"
        elif "09_AUDIT" in path_str:
            prefix = "AUDIT_"
        elif "09_ARCHIVE" in path_str:
            prefix = "ARCHIVED_"
        else:
            prefix = "DOC_"

        # 从标题生成ID部分
        title_part = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '_', title)
        title_part = re.sub(r'_+', '_', title_part).strip('_')
        title_part = title_part[:30].upper()  # 限制长度

        # 组合成module_id
        module_id = f"{prefix}{title_part}_001"

        return module_id

    def infer_document_type(self, file_path: Path) -> str:
        """推断文档类型"""
        path_str = str(file_path).lower()
        filename = file_path.stem.lower()

        if "blueprint" in filename or "blueprint" in path_str:
            return "专业量化机构蓝图"
        elif "spec" in filename or "specification" in filename:
            return "技术规格书"
        elif "guide" in filename or "manual" in filename:
            return "操作手册"
        elif "standard" in filename:
            return "标准文档"
        elif "report" in filename:
            return "审计报告"
        elif "index" in filename:
            return "索引文档"
        elif "readme" in filename:
            return "说明文档"
        elif "checklist" in filename:
            return "检查清单"
        elif "template" in filename:
            return "模板文档"
        else:
            return "通用文档"

    def infer_owner(self, file_path: Path) -> str:
        """推断文档所有者"""
        path_str = str(file_path)

        if "01_FRAMEWORK" in path_str:
            return "首席架构师"
        elif "02_FACTOR_LIBRARY" in path_str:
            return "因子工程团队"
        elif "03_TRADING_TACTICS" in path_str:
            return "交易策略团队"
        elif "04_EXECUTION" in path_str:
            return "执行团队"
        elif "05_IMPLEMENTATION" in path_str:
            return "实施团队"
        elif "09_AUDIT" in path_str:
            return "审计系统"
        else:
            return "文档管理员"

    def generate_yaml_header(self, file_path: Path) -> str:
        """生成YAML头部"""
        title = self.extract_title_from_file(file_path)
        module_id = self.infer_module_id(file_path, title)
        doc_type = self.infer_document_type(file_path)
        owner = self.infer_owner(file_path)
        today = datetime.now().strftime("%Y-%m-%d")

        yaml_header = f"""---
module_id: {module_id}
version: 1.0.0
status: Active
created_date: {today}
last_updated: {today}
owner: {owner}
standard_type: {doc_type}
applicable_scope: 全系统
compliance_level: 专业标准
---

"""

        return yaml_header

    def has_yaml_header(self, file_path: Path) -> bool:
        """检查文件是否已有YAML头部"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                first_line = f.readline()
                return first_line.strip().startswith("---")
        except Exception:
            return False

    def add_yaml_header(self, file_path: Path, dry_run: bool = False) -> bool:
        """为文件添加YAML头部"""
        try:
            # 检查是否已有YAML头部
            if self.has_yaml_header(file_path):
                print(f"[SKIP] {file_path} - 已有YAML头部")
                self.skipped_count += 1
                return False

            # 读取原文件内容
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                original_content = f.read()

            # 生成YAML头部
            yaml_header = self.generate_yaml_header(file_path)

            # 合并内容
            new_content = yaml_header + original_content

            if dry_run:
                print(f"[DRY-RUN] 将为 {file_path} 添加YAML头部")
                return True

            # 写入文件
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            print(f"[OK] {file_path}")
            self.fixed_count += 1
            return True

        except Exception as e:
            print(f"[ERROR] {file_path} - {str(e)}")
            self.error_count += 1
            return False

    def run(self, dry_run: bool = False, limit: Optional[int] = None):
        """执行批量修复"""
        print("=" * 80)
        print("YAML头部批量修复工具")
        print("=" * 80)
        print()

        # 加载缺失YAML头部的文件列表
        missing_files = self.load_missing_yaml_files()

        if not missing_files:
            print("[INFO] 没有发现缺失YAML头部的文件")
            return

        print(f"[INFO] 发现 {len(missing_files)} 个缺失YAML头部的文件")
        print()

        if limit:
            missing_files = missing_files[:limit]
            print(f"[INFO] 限制处理前 {limit} 个文件")
            print()

        # 处理每个文件
        for file_path_str in missing_files:
            file_path = Path(file_path_str)
            if not file_path.exists():
                print(f"[SKIP] {file_path} - 文件不存在")
                self.skipped_count += 1
                continue

            self.add_yaml_header(file_path, dry_run)

        # 输出统计
        print()
        print("=" * 80)
        print("修复统计")
        print("=" * 80)
        print(f"总文件数: {len(missing_files)}")
        print(f"已修复: {self.fixed_count}")
        print(f"已跳过: {self.skipped_count}")
        print(f"错误数: {self.error_count}")
        print()

        if dry_run:
            print("[INFO] 这是模拟运行，未实际修改文件")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="批量添加YAML头部")
    parser.add_argument("--dry-run", action="store_true", help="模拟运行，不实际修改文件")
    parser.add_argument("--limit", type=int, help="限制处理的文件数量")
    parser.add_argument("--docs-root", default="docs", help="文档根目录")

    args = parser.parse_args()

    fixer = YAMLHeaderFixer(docs_root=args.docs_root)
    fixer.run(dry_run=args.dry_run, limit=args.limit)


if __name__ == "__main__":
    main()
