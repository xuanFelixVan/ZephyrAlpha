#!/usr/bin/env python3
"""
批量修复缺失YAML头部的文件

功能:
- 扫描所有缺失YAML头部的文件
- 自动添加标准化YAML头部
- 确保module_id唯一性
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set


class BatchYAMLHeaderFixer:
    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.report_path = self.docs_root.parent / "docs" / "09_AUDIT" / "STATE" / "governance_check_report_round3.json"
        self.fixed_count = 0
        self.skipped_count = 0
        self.error_count = 0
        self.existing_module_ids: Set[str] = set()

    def load_missing_yaml_files(self) -> List[str]:
        """加载缺失YAML头部的文件列表"""
        if not self.report_path.exists():
            print(f"[ERROR] 报告文件不存在: {self.report_path}")
            return []

        with open(self.report_path, "r", encoding="utf-8") as f:
            report = json.load(f)

        # 获取所有缺失YAML头部的文件
        missing_yaml = []
        issues = report.get("issues", {})

        # 从报告中提取缺失YAML头部的文件
        # 这里我们需要从完整的文件列表中筛选
        # 暂时返回空列表，后续会扫描所有文件
        return missing_yaml

    def scan_missing_yaml_files(self) -> List[Path]:
        """扫描所有缺失YAML头部的文件"""
        missing_files = []

        for md_file in self.docs_root.rglob("*.md"):
            # 跳过归档目录
            if "06_ARCHIVE" in str(md_file) and "encoding_issues_archive" in str(md_file):
                continue

            try:
                with open(md_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # 检查是否有YAML头部
                if not content.startswith("---"):
                    missing_files.append(md_file)
                else:
                    # 提取现有的module_id
                    match = re.search(r"module_id:\s*(.+)", content)
                    if match:
                        module_id = match.group(1).strip()
                        self.existing_module_ids.add(module_id)

            except Exception as e:
                print(f"[ERROR] 扫描文件失败: {md_file} - {str(e)}")

        return missing_files

    def extract_title(self, file_path: Path) -> str:
        """从文件中提取标题"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # 尝试从第一个标题提取
            match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if match:
                return match.group(1).strip()

            # 使用文件名作为标题
            return file_path.stem.replace("_", " ")

        except Exception:
            return file_path.stem.replace("_", " ")

    def infer_module_id(self, file_path: Path, title: str) -> str:
        """推断唯一的module_id"""
        # 从文件路径推断
        parts = file_path.parts

        # 提取层级信息
        layer_prefix = ""
        for part in parts:
            if part.startswith("0") and "_" in part:
                layer_prefix = part.split("_")[0]
                break

        # 从标题推断
        title_words = re.findall(r"[A-Z]+", title.upper())
        if title_words:
            title_id = "_".join(title_words[:3])
        else:
            title_id = file_path.stem.upper()[:30].replace("_", "")

        # 生成基础ID
        base_id = f"{title_id}_001"

        # 确保唯一性
        if base_id in self.existing_module_ids:
            counter = 2
            while f"{title_id}_{counter:03d}" in self.existing_module_ids:
                counter += 1
            base_id = f"{title_id}_{counter:03d}"

        self.existing_module_ids.add(base_id)
        return base_id

    def infer_document_type(self, file_path: Path) -> str:
        """推断文档类型"""
        path_str = str(file_path).lower()

        if "blueprint" in path_str:
            return "专业量化机构蓝图"
        elif "standard" in path_str:
            return "专业量化机构标准"
        elif "guide" in path_str:
            return "专业量化机构指南"
        elif "report" in path_str:
            return "专业量化机构报告"
        elif "template" in path_str:
            return "专业量化机构模板"
        elif "workflow" in path_str:
            return "专业量化机构工作流"
        else:
            return "专业量化机构文档"

    def infer_owner(self, file_path: Path) -> str:
        """推断文档所有者"""
        path_str = str(file_path)

        if "01_FRAMEWORK" in path_str:
            return "首席架构师"
        elif "02_FACTOR_LIBRARY" in path_str:
            return "因子研究团队"
        elif "03_TRADING_TACTICS" in path_str:
            return "交易策略团队"
        elif "04_EXECUTION" in path_str:
            return "执行团队"
        elif "05_IMPLEMENTATION" in path_str:
            return "实施团队"
        elif "09_AUDIT" in path_str:
            return "审计团队"
        else:
            return "文档管理员"

    def generate_yaml_header(self, file_path: Path) -> str:
        """生成YAML头部"""
        title = self.extract_title(file_path)
        module_id = self.infer_module_id(file_path, title)
        doc_type = self.infer_document_type(file_path)
        owner = self.infer_owner(file_path)
        today = datetime.now().strftime("%Y-%m-%d")

        return f"""---
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

    def add_yaml_header(self, file_path: Path, dry_run: bool = False) -> bool:
        """添加YAML头部"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # 检查是否已有YAML头部
            if content.startswith("---"):
                print(f"[SKIP] {file_path} - 已有YAML头部")
                self.skipped_count += 1
                return False

            # 生成YAML头部
            yaml_header = self.generate_yaml_header(file_path)

            if dry_run:
                print(f"[DRY-RUN] 将为 {file_path} 添加YAML头部")
                return True

            # 添加YAML头部
            new_content = yaml_header + content

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            print(f"[OK] {file_path}")
            self.fixed_count += 1
            return True

        except Exception as e:
            print(f"[ERROR] {file_path} - {str(e)}")
            self.error_count += 1
            return False

    def run(self, dry_run: bool = False, limit: int = None):
        """执行批量修复"""
        print("=" * 80)
        print("批量YAML头部修复工具")
        print("=" * 80)
        print()

        # 扫描缺失YAML头部的文件
        print("[INFO] 扫描缺失YAML头部的文件...")
        missing_files = self.scan_missing_yaml_files()

        if not missing_files:
            print("[INFO] 没有发现缺失YAML头部的文件")
            return

        print(f"[INFO] 发现 {len(missing_files)} 个文件缺失YAML头部")
        print()

        if limit:
            missing_files = missing_files[:limit]
            print(f"[INFO] 限制处理前 {limit} 个文件")
            print()

        # 批量修复
        for i, file_path in enumerate(missing_files, 1):
            print(f"[{i}/{len(missing_files)}] ", end="")
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

    parser = argparse.ArgumentParser(description="批量修复缺失YAML头部的文件")
    parser.add_argument("--dry-run", action="store_true", help="模拟运行，不实际修改文件")
    parser.add_argument("--limit", type=int, help="限制处理的文件数量")
    parser.add_argument("--docs-root", default="docs", help="文档根目录")

    args = parser.parse_args()

    fixer = BatchYAMLHeaderFixer(docs_root=args.docs_root)
    fixer.run(dry_run=args.dry_run, limit=args.limit)


if __name__ == "__main__":
    main()
