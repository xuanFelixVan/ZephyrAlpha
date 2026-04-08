#!/usr/bin/env python3
"""
检查编码问题文件的可读性

功能:
- 读取governance_check_report.json中编码问题的文件列表
- 检查每个文件是否可正常阅读
- 生成可读性报告
"""

import json
from pathlib import Path
from typing import List, Dict
import chardet


class EncodingChecker:
    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.report_path = self.docs_root.parent / "docs" / "09_AUDIT" / "STATE" / "governance_check_report.json"
        self.readable_count = 0
        self.unreadable_count = 0
        self.error_count = 0
        self.results = []

    def load_encoding_issue_files(self) -> List[str]:
        """加载编码问题的文件列表"""
        if not self.report_path.exists():
            print(f"[ERROR] 报告文件不存在: {self.report_path}")
            return []

        with open(self.report_path, "r", encoding="utf-8") as f:
            report = json.load(f)

        encoding_issues = report.get("issues", {}).get("encoding_issues", [])
        return [item["file"] for item in encoding_issues]

    def check_file_readability(self, file_path: Path) -> Dict:
        """检查文件可读性"""
        result = {
            "file": str(file_path),
            "exists": file_path.exists(),
            "readable": False,
            "encoding": None,
            "error": None,
            "sample": None
        }

        if not file_path.exists():
            result["error"] = "文件不存在"
            return result

        try:
            # 检测编码
            with open(file_path, "rb") as f:
                raw_data = f.read()

            detected = chardet.detect(raw_data)
            result["encoding"] = detected.get("encoding", "unknown")

            # 尝试读取文件
            try:
                content = raw_data.decode(result["encoding"])
                result["readable"] = True
                result["sample"] = content[:200]  # 前200个字符
                self.readable_count += 1
            except Exception as e:
                result["readable"] = False
                result["error"] = f"解码失败: {str(e)}"
                self.unreadable_count += 1

        except Exception as e:
            result["error"] = f"读取失败: {str(e)}"
            self.error_count += 1

        return result

    def run(self, limit: int = None):
        """执行可读性检查"""
        print("=" * 80)
        print("编码问题文件可读性检查")
        print("=" * 80)
        print()

        # 加载编码问题的文件列表
        encoding_files = self.load_encoding_issue_files()

        if not encoding_files:
            print("[INFO] 没有发现编码问题的文件")
            return

        print(f"[INFO] 发现 {len(encoding_files)} 个编码问题的文件")
        print()

        if limit:
            encoding_files = encoding_files[:limit]
            print(f"[INFO] 限制检查前 {limit} 个文件")
            print()

        # 检查每个文件
        for file_path_str in encoding_files:
            file_path = Path(file_path_str)
            result = self.check_file_readability(file_path)
            self.results.append(result)

            status = "[OK]" if result["readable"] else "[ERROR]"
            print(f"{status} {file_path}")
            if result["encoding"]:
                print(f"     编码: {result['encoding']}")
            if result["error"]:
                print(f"     错误: {result['error']}")

        # 输出统计
        print()
        print("=" * 80)
        print("检查统计")
        print("=" * 80)
        print(f"总文件数: {len(encoding_files)}")
        print(f"可读文件: {self.readable_count}")
        print(f"不可读文件: {self.unreadable_count}")
        print(f"错误文件: {self.error_count}")
        print()

        # 输出不可读文件列表
        if self.unreadable_count > 0:
            print("=" * 80)
            print("不可读文件列表")
            print("=" * 80)
            for result in self.results:
                if not result["readable"]:
                    print(f"- {result['file']}")
                    if result["error"]:
                        print(f"  错误: {result['error']}")
            print()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="检查编码问题文件的可读性")
    parser.add_argument("--limit", type=int, help="限制检查的文件数量")
    parser.add_argument("--docs-root", default="docs", help="文档根目录")

    args = parser.parse_args()

    checker = EncodingChecker(docs_root=args.docs_root)
    checker.run(limit=args.limit)


if __name__ == "__main__":
    main()
