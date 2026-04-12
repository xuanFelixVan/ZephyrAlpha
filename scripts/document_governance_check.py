#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
文档治理自动化检测脚本

功能:
1. 检测module_id重复
2. 检测职责重叠
3. 检测缺失INDEX.md
4. 检测YAML头部缺失
5. 生成检测报告

使用方法:
    python scripts/document_governance_check.py [--output report.json]
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple
from collections import defaultdict


class DocumentGovernanceChecker:
    """文档治理检查器"""

    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.issues = {
            "module_id_duplicates": [],
            "responsibility_overlap": [],
            "missing_index": [],
            "missing_yaml": [],
            "encoding_issues": []
        }
        self.stats = {
            "total_files": 0,
            "files_with_module_id": 0,
            "total_issues": 0
        }

    def scan_all_markdown_files(self) -> List[Path]:
        """扫描所有Markdown文件"""
        md_files = []
        for root, dirs, files in os.walk(self.docs_root):
            # 排除特定目录
            if any(exclude in root for exclude in ["audit_state", "archive", "__pycache__", ".git"]):
                continue

            for file in files:
                if file.endswith(".md"):
                    md_files.append(Path(root) / file)

        self.stats["total_files"] = len(md_files)
        return md_files

    def check_module_id_duplicates(self, md_files: List[Path]):
        """检查module_id重复"""
        module_id_map = defaultdict(list)

        for md_file in md_files:
            module_id = self.extract_module_id(md_file)
            if module_id:
                module_id_map[module_id].append(str(md_file.relative_to(self.docs_root.parent)))

        # 找出重复的module_id
        for module_id, files in module_id_map.items():
            if len(files) > 1:
                self.issues["module_id_duplicates"].append({
                    "module_id": module_id,
                    "count": len(files),
                    "files": files
                })

        self.stats["files_with_module_id"] = sum(len(files) for files in module_id_map.values())

    def check_responsibility_overlap(self, md_files: List[Path]):
        """检查职责重叠"""
        # 定义关键词
        keywords = {
            "市场状态识别": ["市场状态", "市场环境", "Market Regime", "Regime Detection"],
            "风险预算": ["风险预算", "Risk Budget", "风险贡献", "Risk Contribution"],
            "数据质量": ["数据质量", "Data Quality", "质量监控", "Quality Monitor"]
        }

        overlap_map = defaultdict(list)

        for md_file in md_files:
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()

                for responsibility, kw_list in keywords.items():
                    for keyword in kw_list:
                        if keyword.lower() in content.lower():
                            overlap_map[responsibility].append(str(md_file.relative_to(self.docs_root.parent)))
                            break
            except Exception:
                pass

        # 找出职责重叠（文件数>10）
        for responsibility, files in overlap_map.items():
            if len(files) > 10:
                self.issues["responsibility_overlap"].append({
                    "responsibility": responsibility,
                    "count": len(files),
                    "files": files[:10]  # 只显示前10个
                })

    def check_missing_index(self):
        """检查缺失INDEX.md"""
        missing_dirs = []

        for root, dirs, files in os.walk(self.docs_root):
            # 排除特定目录
            if any(exclude in root for exclude in ["audit_state", "archive", "__pycache__", ".git"]):
                continue

            # 检查是否有INDEX.md
            index_path = Path(root) / "INDEX.md"
            if index_path.exists():
                continue

            # 统计.md文件数量
            md_files = [f for f in files if f.endswith(".md")]
            if len(md_files) >= 2:  # 至少2个文件才需要INDEX.md
                missing_dirs.append({
                    "directory": str(Path(root).relative_to(self.docs_root.parent)),
                    "md_count": len(md_files)
                })

        self.issues["missing_index"] = missing_dirs

    def check_missing_yaml(self, md_files: List[Path]):
        """检查缺失YAML头部"""
        for md_file in md_files:
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    first_line = f.readline()

                if not first_line.startswith("---"):
                    self.issues["missing_yaml"].append({
                        "file": str(md_file.relative_to(self.docs_root.parent))
                    })
            except Exception:
                pass

    def check_encoding_issues(self, md_files: List[Path]):
        """检查编码问题"""
        for md_file in md_files:
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    # 检查是否有乱码字符
                    if "锟斤拷" in content or "锟斤拷" in content:
                        self.issues["encoding_issues"].append({
                            "file": str(md_file.relative_to(self.docs_root.parent))
                        })
            except UnicodeDecodeError:
                self.issues["encoding_issues"].append({
                    "file": str(md_file.relative_to(self.docs_root.parent))
                })

    def extract_module_id(self, md_file: Path) -> str:
        """从文件中提取module_id"""
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("module_id:"):
                        return line.split(":", 1)[1].strip()
        except Exception:
            pass
        return None

    def run_all_checks(self):
        """运行所有检查"""
        print("=" * 80)
        print("文档治理自动化检测")
        print("=" * 80)
        print()

        # 扫描文件
        print("第一阶段: 扫描Markdown文件")
        print("-" * 80)
        md_files = self.scan_all_markdown_files()
        print(f"扫描文件数: {len(md_files)}")
        print()

        # 检查module_id重复
        print("第二阶段: 检查module_id重复")
        print("-" * 80)
        self.check_module_id_duplicates(md_files)
        if self.issues["module_id_duplicates"]:
            print(f"[WARNING] 发现 {len(self.issues['module_id_duplicates'])} 组重复的module_id")
            for issue in self.issues["module_id_duplicates"]:
                print(f"  - {issue['module_id']}: {issue['count']}个文件")
        else:
            print("[OK] 未发现重复的module_id")
        print()

        # 检查职责重叠
        print("第三阶段: 检查职责重叠")
        print("-" * 80)
        self.check_responsibility_overlap(md_files)
        if self.issues["responsibility_overlap"]:
            print(f"[WARNING] 发现 {len(self.issues['responsibility_overlap'])} 个职责重叠问题")
            for issue in self.issues["responsibility_overlap"]:
                print(f"  - {issue['responsibility']}: {issue['count']}个文件")
        else:
            print("[OK] 未发现职责重叠问题")
        print()

        # 检查缺失INDEX.md
        print("第四阶段: 检查缺失INDEX.md")
        print("-" * 80)
        self.check_missing_index()
        if self.issues["missing_index"]:
            print(f"[WARNING] 发现 {len(self.issues['missing_index'])} 个目录缺失INDEX.md")
            for issue in self.issues["missing_index"][:10]:
                print(f"  - {issue['directory']}: {issue['md_count']}个文件")
        else:
            print("[OK] 所有目录都有INDEX.md")
        print()

        # 检查缺失YAML
        print("第五阶段: 检查缺失YAML头部")
        print("-" * 80)
        self.check_missing_yaml(md_files)
        if self.issues["missing_yaml"]:
            print(f"[WARNING] 发现 {len(self.issues['missing_yaml'])} 个文件缺失YAML头部")
        else:
            print("[OK] 所有文件都有YAML头部")
        print()

        # 检查编码问题
        print("第六阶段: 检查编码问题")
        print("-" * 80)
        self.check_encoding_issues(md_files)
        if self.issues["encoding_issues"]:
            print(f"[WARNING] 发现 {len(self.issues['encoding_issues'])} 个文件存在编码问题")
        else:
            print("[OK] 未发现编码问题")
        print()

        # 统计总问题数
        self.stats["total_issues"] = sum(len(issues) for issues in self.issues.values())

    def generate_report(self, output_path: str = None):
        """生成检测报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "stats": self.stats,
            "issues": self.issues,
            "summary": {
                "total_issues": self.stats["total_issues"],
                "critical_issues": len(self.issues["module_id_duplicates"]),
                "important_issues": len(self.issues["responsibility_overlap"]),
                "minor_issues": len(self.issues["missing_index"]) + len(self.issues["missing_yaml"])
            }
        }

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"报告已保存至: {output_path}")

        return report

    def print_summary(self):
        """打印摘要"""
        print("=" * 80)
        print("检测摘要")
        print("=" * 80)
        print(f"总文件数: {self.stats['total_files']}")
        print(f"有module_id的文件数: {self.stats['files_with_module_id']}")
        print(f"总问题数: {self.stats['total_issues']}")
        print()
        print("问题分布:")
        print(f"  - module_id重复: {len(self.issues['module_id_duplicates'])} 组")
        print(f"  - 职责重叠: {len(self.issues['responsibility_overlap'])} 个")
        print(f"  - 缺失INDEX.md: {len(self.issues['missing_index'])} 个目录")
        print(f"  - 缺失YAML头部: {len(self.issues['missing_yaml'])} 个文件")
        print(f"  - 编码问题: {len(self.issues['encoding_issues'])} 个文件")
        print()

        # 计算合规率
        if self.stats["total_files"] > 0:
            compliance_rate = (self.stats["total_files"] - self.stats["total_issues"]) / self.stats["total_files"] * 100
            print(f"文档治理合规率: {compliance_rate:.1f}%")
        print()


def main():
    parser = argparse.ArgumentParser(description="文档治理自动化检测")
    parser.add_argument("--output", type=str, help="输出报告路径 (JSON格式)")

    args = parser.parse_args()

    checker = DocumentGovernanceChecker()
    checker.run_all_checks()
    checker.print_summary()

    if args.output:
        checker.generate_report(args.output)


if __name__ == "__main__":
    main()
