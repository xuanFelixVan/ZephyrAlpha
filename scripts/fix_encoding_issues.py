#!/usr/bin/env python3
"""
批量修复编码问题文件

功能:
- 读取governance_check_report.json中编码问题的文件列表
- 检测每个文件的当前编码
- 将文件转换为UTF-8编码
- 保存文件
"""

import json
from pathlib import Path
from typing import List, Optional
import chardet


class EncodingFixer:
    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.report_path = self.docs_root.parent / "docs" / "09_AUDIT" / "STATE" / "governance_check_report.json"
        self.fixed_count = 0
        self.skipped_count = 0
        self.error_count = 0

    def load_encoding_issue_files(self) -> List[str]:
        """加载编码问题的文件列表"""
        if not self.report_path.exists():
            print(f"[ERROR] 报告文件不存在: {self.report_path}")
            return []

        with open(self.report_path, "r", encoding="utf-8") as f:
            report = json.load(f)

        encoding_issues = report.get("issues", {}).get("encoding_issues", [])
        return [item["file"] for item in encoding_issues]

    def detect_encoding(self, file_path: Path) -> Optional[str]:
        """检测文件编码"""
        try:
            with open(file_path, "rb") as f:
                raw_data = f.read()

            detected = chardet.detect(raw_data)
            return detected.get("encoding", None)
        except Exception:
            return None

    def is_utf8(self, file_path: Path) -> bool:
        """检查文件是否已经是UTF-8编码"""
        encoding = self.detect_encoding(file_path)
        if not encoding:
            return False

        encoding_lower = encoding.lower()
        return encoding_lower in ["utf-8", "utf-8-sig", "utf8", "utf_8"]

    def fix_encoding(self, file_path: Path, dry_run: bool = False) -> bool:
        """修复文件编码"""
        try:
            # 检查是否已经是UTF-8
            if self.is_utf8(file_path):
                print(f"[SKIP] {file_path} - 已经是UTF-8编码")
                self.skipped_count += 1
                return False

            # 检测当前编码
            current_encoding = self.detect_encoding(file_path)
            if not current_encoding:
                print(f"[ERROR] {file_path} - 无法检测编码")
                self.error_count += 1
                return False

            # 读取文件内容
            with open(file_path, "rb") as f:
                raw_data = f.read()

            # 解码内容
            try:
                content = raw_data.decode(current_encoding)
            except Exception as e:
                print(f"[ERROR] {file_path} - 解码失败: {str(e)}")
                self.error_count += 1
                return False

            if dry_run:
                print(f"[DRY-RUN] 将转换 {file_path} 从 {current_encoding} 到 UTF-8")
                return True

            # 编码为UTF-8
            utf8_data = content.encode("utf-8")

            # 写入文件
            with open(file_path, "wb") as f:
                f.write(utf8_data)

            print(f"[OK] {file_path} - {current_encoding} -> UTF-8")
            self.fixed_count += 1
            return True

        except Exception as e:
            print(f"[ERROR] {file_path} - {str(e)}")
            self.error_count += 1
            return False

    def run(self, dry_run: bool = False, limit: Optional[int] = None):
        """执行批量修复"""
        print("=" * 80)
        print("编码问题批量修复工具")
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
            print(f"[INFO] 限制处理前 {limit} 个文件")
            print()

        # 处理每个文件
        for file_path_str in encoding_files:
            file_path = Path(file_path_str)
            if not file_path.exists():
                print(f"[SKIP] {file_path} - 文件不存在")
                self.skipped_count += 1
                continue

            self.fix_encoding(file_path, dry_run)

        # 输出统计
        print()
        print("=" * 80)
        print("修复统计")
        print("=" * 80)
        print(f"总文件数: {len(encoding_files)}")
        print(f"已修复: {self.fixed_count}")
        print(f"已跳过: {self.skipped_count}")
        print(f"错误数: {self.error_count}")
        print()

        if dry_run:
            print("[INFO] 这是模拟运行，未实际修改文件")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="批量修复编码问题文件")
    parser.add_argument("--dry-run", action="store_true", help="模拟运行，不实际修改文件")
    parser.add_argument("--limit", type=int, help="限制处理的文件数量")
    parser.add_argument("--docs-root", default="docs", help="文档根目录")

    args = parser.parse_args()

    fixer = EncodingFixer(docs_root=args.docs_root)
    fixer.run(dry_run=args.dry_run, limit=args.limit)


if __name__ == "__main__":
    main()
